import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bff.auth import require_bearer
from shared.db import get_async_session
from shared.models import CloudJob, JobStatus
from shared.quota import CallerIdentity

router = APIRouter(prefix="/v1", dependencies=[Depends(require_bearer)])


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_async_session),
    caller: CallerIdentity = Depends(require_bearer),
):
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    job = await session.get(CloudJob, jid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Session users only see their own jobs (lab API token / open mode skip).
    if caller.email and job.owner_email and job.owner_email != caller.email:
        raise HTTPException(status_code=404, detail="Job not found")

    body: dict = {
        "job_id": str(job.id),
        "status": job.status.value,
        "message": job.message,
        "day_revision_id": job.day_revision_id,
        "bundle_version": job.bundle_version,
    }
    if job.result and isinstance(job.result, dict):
        pub = job.result.get("_publish")
        if isinstance(pub, dict):
            body["publish"] = pub
    if job.status == JobStatus.succeeded and job.result:
        body["result"] = job.result
    if job.status == JobStatus.failed:
        body["message"] = job.error or job.message or "failed"
        if job.result:
            body["result"] = job.result
    return body
