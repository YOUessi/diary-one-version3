import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bff.auth import require_bearer
from shared.db import get_async_session
from shared.models import CloudJob, JobStatus

router = APIRouter(prefix="/v1", dependencies=[Depends(require_bearer)])


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id")

    job = await session.get(CloudJob, jid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    body: dict = {
        "job_id": str(job.id),
        "status": job.status.value,
        "message": job.message,
        "day_revision_id": job.day_revision_id,
    }
    if job.status == JobStatus.succeeded and job.result:
        body["result"] = job.result
    if job.status == JobStatus.failed:
        body["message"] = job.error or job.message or "failed"
    return body
