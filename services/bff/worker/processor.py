import asyncio
import json
import shutil
import tempfile
import uuid
from pathlib import Path

from sqlalchemy import select

from shared.db import SyncSessionLocal
from shared.models import CloudJob, JobStatus
from shared.storage import download_to_dir, minio_client
from worker.x02_proxy import run_x02_preview
from shared.config import settings
from shared.mock_preview import mock_preview_result, preview_has_no_memories


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
            if settings.allow_mock_preview and preview_has_no_memories(result):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                mock = mock_preview_result(manifest)
                mock["dev_lite_fallback"] = True
                mock["dev_lite_x02_empty"] = True
                mock["dev_lite_x02_delivery_state"] = result.get("delivery_state")
                result = mock
                job.message = "Mock preview (X02 returned no grounded memories)"
            else:
                job.message = "Cloud processing complete"

            job.status = JobStatus.succeeded
            job.result = result
            job.error = None
        except Exception as exc:  # noqa: BLE001
            if settings.allow_mock_preview:
                try:
                    manifest = json.loads((tmp / "bundle.json").read_text(encoding="utf-8"))
                    result = mock_preview_result(manifest)
                    result["dev_lite_fallback"] = True
                    result["dev_lite_x02_error"] = str(exc)
                    job.status = JobStatus.succeeded
                    job.result = result
                    job.error = None
                    job.message = f"Mock preview (X02 unavailable: {exc})"
                except Exception:  # noqa: BLE001
                    job.status = JobStatus.failed
                    job.error = str(exc)
                    job.message = "Cloud processing failed"
            else:
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
