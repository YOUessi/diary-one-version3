import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bff.auth import require_bearer
from shared.db import get_async_session
from shared.models import CloudJob, JobStatus
from shared.queue import enqueue_job
from shared.form_fields import read_form_bytes, read_form_field
from shared.storage import minio_client, upload_bytes

router = APIRouter(prefix="/v1", dependencies=[Depends(require_bearer)])


@router.post("/day-revisions")
async def create_day_revision(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Multipart compatible with App Library Bundle upload (manifest + frame_id files).
    Same shape as X02 research preview.
    """
    form = await request.form()
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
        return {
            "job_id": str(existing.id),
            "day_revision_id": rev_id,
            "status": existing.status.value,
            "idempotent": True,
        }

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
        bundle_version=bundle_version,
        object_prefix=prefix,
        status=JobStatus.pending,
        message="Queued for cloud processing",
    )
    session.add(job)
    await session.commit()

    enqueue_job(str(job_id))

    return {"job_id": str(job_id), "day_revision_id": rev_id, "status": "pending"}
