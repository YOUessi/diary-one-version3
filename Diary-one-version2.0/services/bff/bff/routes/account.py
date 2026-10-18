from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from minio.deleteobjects import DeleteObject

from bff.account_guard import lock_account
from bff.auth import require_bearer
from bff.routes.auth_otp import session_store, _otp
from shared.config import settings
from shared.db import get_async_session
from shared.models import CloudJob, JobStatus
from shared.quota import CallerIdentity, quota_store
from shared.storage import minio_client

router = APIRouter(prefix="/v1/account")


def delete_job_evidence(job_ids: list[str]) -> None:
    client = minio_client()
    for job_id in job_ids:
        # Prefix comes from the owned job's UUID, never an arbitrary request path.
        objects = client.list_objects(settings.minio_bucket, prefix=f"jobs/{job_id}/",
                                      recursive=True, include_version=True)
        errors = client.remove_objects(settings.minio_bucket, (
            DeleteObject(obj.object_name, obj.version_id) for obj in objects if obj.object_name
        ))
        if next(iter(errors), None) is not None:
            raise RuntimeError("Evidence deletion incomplete")


@router.delete("")
async def delete_account(request: Request, caller: CallerIdentity = Depends(require_bearer),
                         session: AsyncSession = Depends(get_async_session)):
    if caller.kind != "session" or not caller.email:
        raise HTTPException(status_code=403, detail="account_session_required")
    await lock_account(session, caller.email, request)
    # Refuse while work is active; no deletion races with a worker reading evidence.
    jobs = list((await session.scalars(select(CloudJob).where(CloudJob.owner_email == caller.email))).all())
    if any(job.status in (JobStatus.pending, JobStatus.processing) for job in jobs):
        raise HTTPException(status_code=409, detail="processing_in_progress_try_again_when_finished")
    try:
        await run_in_threadpool(delete_job_evidence, [str(job.id) for job in jobs])
    except Exception as exc:
        raise HTTPException(status_code=503, detail="data_deletion_incomplete_retry") from exc
    for job in jobs:
        await session.delete(job)
    quota_store().delete_caller(caller.key)
    await _otp.store.forget(caller.email)
    session_store().revoke_email(caller.email)
    await session.commit()
    return {"deleted": True}
