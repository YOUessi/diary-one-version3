import asyncio
import json
import shutil
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select

from shared.config import settings
from shared.db import SyncSessionLocal
from shared.mock_preview import mock_preview_result, preview_has_no_memories
from shared.models import CloudJob, JobStatus
from shared.result_admit import apply_admission
from shared.storage import download_to_dir, minio_client
from worker.x02_proxy import run_x02_preview


def process_job_sync(job_id: str) -> None:
    session = SyncSessionLocal()
    try:
        jid = uuid.UUID(job_id)
        job = session.scalar(select(CloudJob).where(CloudJob.id == jid).with_for_update(skip_locked=True))
        if not job:
            return
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.worker_recovery_grace_seconds)
        updated = job.updated_at
        if updated is not None and updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if job.status not in (JobStatus.pending, JobStatus.processing):
            return
        if job.status == JobStatus.processing and (updated is None or updated > cutoff):
            return
        job.status = JobStatus.processing
        job.message = "Running X02 preview…"
        session.commit()

        # Hold a database row lock during execution. Recovery scans skip this row,
        # regardless of model latency. A dead worker releases the lock automatically.
        job = session.scalar(select(CloudJob).where(CloudJob.id == jid).with_for_update(skip_locked=True))
        if not job or job.status != JobStatus.processing:
            return

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

            result, envelope = apply_admission(
                result,
                bundle_version=job.bundle_version,
                allow_mock=settings.allow_mock_preview,
                manifest_bytes=manifest_path.read_bytes(),
                bundle_dir=tmp,
            )
            if envelope.get("fail_job"):
                job.status = JobStatus.failed
                job.result = result
                job.error = str(envelope.get("admit_reason") or "not_admitted")
                job.message = f"Result not admitted ({envelope.get('admit_reason')})"
            else:
                job.status = JobStatus.succeeded
                job.result = result
                job.error = None
                if envelope.get("admit_reason") == "no_grounded_memory":
                    job.message = "Completed with no grounded memories (honest empty)"
        except Exception as exc:  # noqa: BLE001
            if settings.allow_mock_preview:
                try:
                    manifest = json.loads((tmp / "bundle.json").read_text(encoding="utf-8"))
                    result = mock_preview_result(manifest)
                    result["dev_lite_fallback"] = True
                    result["dev_lite_x02_error"] = str(exc)
                    result, envelope = apply_admission(
                        result,
                        bundle_version=job.bundle_version,
                        allow_mock=True,
                    )
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


def recoverable_job_ids(limit: int) -> list[str]:
    """Durable pending outbox plus crash recovery; never resets another live worker."""
    session = SyncSessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.worker_recovery_grace_seconds)
        rows = session.scalars(
            select(CloudJob).where(
                (CloudJob.status == JobStatus.pending) |
                ((CloudJob.status == JobStatus.processing) & (CloudJob.updated_at <= cutoff))
            ).order_by(CloudJob.created_at).limit(limit).with_for_update(skip_locked=True)
        ).all()
        return [str(job.id) for job in rows]
    finally:
        session.close()
