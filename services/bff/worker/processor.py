import asyncio
import shutil
import tempfile
import uuid
from pathlib import Path

from sqlalchemy import select

from shared.db import SyncSessionLocal
from shared.models import CloudJob, JobStatus
from shared.storage import download_to_dir, minio_client
from worker.x02_proxy import run_x02_preview


def process_job_sync(job_id: str) -> None:
    session = SyncSessionLocal()
    try:
        jid = uuid.UUID(job_id)
        job = session.get(CloudJob, jid)
        if not job:
            return
        job.status = JobStatus.processing
        job.message = "Running X02 preview…"
        session.commit()

        tmp = Path(tempfile.mkdtemp(prefix="diary-job-"))
        try:
            download_to_dir(minio_client(), job.object_prefix, tmp)
            manifest_path = tmp / "bundle.json"
            if not manifest_path.exists():
                raise FileNotFoundError("bundle.json missing in object storage")

            result = asyncio.run(run_x02_preview(tmp, manifest_path))

            job.status = JobStatus.succeeded
            job.result = result
            job.message = "Cloud processing complete"
            job.error = None
        except Exception as exc:  # noqa: BLE001
            job.status = JobStatus.failed
            job.error = str(exc)
            job.message = "Cloud processing failed"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        session.commit()
    finally:
        session.close()


def requeue_stale_processing() -> None:
    session = SyncSessionLocal()
    try:
        rows = session.scalars(select(CloudJob).where(CloudJob.status == JobStatus.processing)).all()
        for job in rows:
            job.status = JobStatus.pending
        session.commit()
    finally:
        session.close()
