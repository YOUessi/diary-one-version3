import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from bff.auth import require_bearer
from bff.account_guard import lock_account
from shared.config import settings
from shared.db import get_async_session
from shared.form_fields import read_form_field
from shared.models import CloudJob, JobStatus
from shared.queue import enqueue_job
from shared.quota import (
    CallerIdentity,
    assert_inflight,
    quota_store,
)
from shared.storage import minio_client, upload_bytes, delete_prefix
from shared.evidence_input import read_validated_upload
from shared.submission import read_profile_and_fingerprint, check_revision_input, storage_unavailable

router = APIRouter(prefix="/v1", dependencies=[Depends(require_bearer)])
logger = logging.getLogger(__name__)


def notify_worker(job_id: str) -> None:
    # Postgres pending rows are the durable delivery record; Redis is a wake-up hint.
    try:
        enqueue_job(job_id)
    except Exception:
        logger.exception("Worker notification failed for job %s; database recovery will retry", job_id)


def idempotent_owner_decision(
    *,
    owner_email: str | None,
    caller_email: str | None,
) -> str:
    """Return reuse | conflict | legacy_ok for day_revision idempotency."""
    owner = (owner_email or "").strip().lower()
    caller = (caller_email or "").strip().lower()
    if owner and caller and owner != caller:
        return "conflict"
    if owner and caller and owner == caller:
        return "reuse"
    if not owner and not caller:
        return "legacy_ok"
    return "conflict"


@router.post("/day-revisions")
async def create_day_revision(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    caller: CallerIdentity = Depends(require_bearer),
):
    """
    Multipart compatible with App Library Bundle upload (manifest + frame_id files).
    Same shape as X02 research preview.
    """
    form = await request.form()
    manifest_bytes, manifest_json, frame_contents = await read_validated_upload(form)
    profile_bytes, fingerprint = await read_profile_and_fingerprint(form, manifest_bytes)
    rev_id = await read_form_field(form.get("day_revision_id"))
    rev_id = rev_id or f"dayrev_{uuid.uuid4()}"
    if len(rev_id) > 128:
        raise HTTPException(422, detail="day_revision_id too long")
    if caller.email:
        await lock_account(session, caller.email, request)
    # Serialize the revision even for API-token callers and across BFF processes.
    await session.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:revision, 1))"),
                          {"revision": rev_id})

    existing = await session.scalar(
        select(CloudJob)
        .where(CloudJob.day_revision_id == rev_id)
        .order_by(CloudJob.created_at.desc())
        .limit(1)
    )
    if existing:
        check_revision_input(existing.owner_email, caller.email, existing.input_fingerprint, fingerprint)
    if existing and existing.status in (
        JobStatus.pending,
        JobStatus.processing,
        JobStatus.succeeded,
    ):
        decision = idempotent_owner_decision(
            owner_email=existing.owner_email,
            caller_email=caller.email,
        )
        if decision == "conflict":
            raise HTTPException(
                status_code=409,
                detail="day_revision_id already used by another account",
            )
        if existing.status == JobStatus.pending:
            notify_worker(str(existing.id))
        return {
            "job_id": str(existing.id),
            "day_revision_id": rev_id,
            "status": existing.status.value,
            "idempotent": True,
        }

    if caller.email:
        inflight = await session.scalar(
            select(func.count())
            .select_from(CloudJob)
            .where(
                CloudJob.owner_email == caller.email,
                CloudJob.status.in_([JobStatus.pending, JobStatus.processing]),
            )
        )
        assert_inflight(int(inflight or 0), limit=settings.day_revision_max_inflight)

    job_id = uuid.uuid4()
    prefix = f"jobs/{job_id}/"
    bundle_version = manifest_json.get("bundle_version")
    job = CloudJob(
        id=job_id,
        day_revision_id=rev_id,
        owner_email=caller.email,
        input_fingerprint=fingerprint,
        bundle_version=bundle_version,
        object_prefix=prefix,
        status=JobStatus.pending,
        message="Queued for cloud processing",
    )
    quota = quota_store()
    charge = None
    client = None
    committing = False
    try:
        client = minio_client()
        charge = quota.charge(caller.key, str(job_id), limit=settings.day_revision_daily_limit)
        upload_bytes(client, f"{prefix}bundle.json", manifest_bytes, "application/json")
        if profile_bytes:
            upload_bytes(client, f"{prefix}app_client_profile.json", profile_bytes, "application/json")
        for frame_id, frame_bytes in frame_contents.items():
            upload_bytes(client, f"{prefix}frames/{frame_id}.jpg", frame_bytes, "image/jpeg")
        session.add(job)
        committing = True
        await session.commit()
    except BaseException as exc:
        logger.warning("Submission interrupted for job %s", job_id, exc_info=True)
        # A lost commit acknowledgement is not proof of rollback. Confirm before
        # deleting evidence a worker might already be processing.
        try:
            try:
                await session.rollback()
            except Exception:
                if committing: raise
                logger.exception("Rollback connection unavailable before commit for job %s", job_id)
            accepted = await session.get(CloudJob, job_id) if committing else None
        except Exception:
            logger.exception("Submission outcome unknown; retaining job %s evidence and charge", job_id)
            raise storage_unavailable() from exc
        if accepted is None:
            try:
                if charge is not None: quota.refund(charge)
            except OSError:
                logger.exception("Quota compensation needs reconciliation; retaining job %s evidence", job_id)
                raise storage_unavailable() from exc
            if client is not None and charge is not None:
                try: delete_prefix(client, prefix)
                except Exception: logger.exception("Submission cleanup needs retry: %s", job_id)
            if isinstance(exc, HTTPException): raise
            if not isinstance(exc, Exception): raise
            raise storage_unavailable() from exc
        job = accepted

    notify_worker(str(job_id))

    return {
        "job_id": str(job_id),
        "day_revision_id": rev_id,
        "status": job.status.value,
        "quota_used": charge.used if charge is not None else 0,
        "quota_limit": settings.day_revision_daily_limit,
    }
