import json
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bff.auth import require_bearer
from bff.account_guard import lock_account
from shared.config import settings
from shared.db import get_async_session
from shared.form_fields import read_form_bytes, read_form_field
from shared.models import CloudJob, JobStatus
from shared.queue import enqueue_job
from shared.quota import (
    CallerIdentity,
    assert_inflight,
    assert_quota,
    quota_store,
)
from shared.storage import minio_client, upload_bytes

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
    if caller.email:
        await lock_account(session, caller.email, request)
    manifest_part = form.get("manifest")
    if manifest_part is None:
        raise HTTPException(status_code=400, detail="manifest required")

    manifest_bytes = await read_form_bytes(manifest_part)
    if not manifest_bytes:
        raise HTTPException(status_code=400, detail="manifest required")
    try:
        manifest_json = json.loads(manifest_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="manifest must be JSON")

    rev_id = await read_form_field(form.get("day_revision_id"))
    rev_id = rev_id or f"dayrev_{uuid.uuid4()}"

    existing = await session.scalar(
        select(CloudJob)
        .where(CloudJob.day_revision_id == rev_id)
        .order_by(CloudJob.created_at.desc())
        .limit(1)
    )
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

    used = assert_quota(
        caller,
        quota_store(),
        limit=settings.day_revision_daily_limit,
    )

    job_id = uuid.uuid4()
    prefix = f"jobs/{job_id}/"
    client = minio_client()

    upload_bytes(client, f"{prefix}bundle.json", manifest_bytes, "application/json")

    profile_part = form.get("app_client_profile")
    if profile_part is not None:
        profile_bytes = await read_form_bytes(profile_part)
        if profile_bytes:
            upload_bytes(client, f"{prefix}app_client_profile.json", profile_bytes, "application/json")

    for key, part in form.items():
        if key in ("manifest", "app_client_profile", "day_revision_id"):
            continue
        if not hasattr(part, "read"):
            continue
        frame_bytes = await part.read()
        upload_bytes(client, f"{prefix}frames/{key}.jpg", frame_bytes, "image/jpeg")

    bundle_version = manifest_json.get("bundle_version")

    job = CloudJob(
        id=job_id,
        day_revision_id=rev_id,
        owner_email=caller.email,
        bundle_version=bundle_version,
        object_prefix=prefix,
        status=JobStatus.pending,
        message="Queued for cloud processing",
    )
    session.add(job)
    await session.commit()

    notify_worker(str(job_id))

    return {
        "job_id": str(job_id),
        "day_revision_id": rev_id,
        "status": "pending",
        "quota_used": used,
        "quota_limit": settings.day_revision_daily_limit,
    }
