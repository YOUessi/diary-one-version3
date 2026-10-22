"""Dev Lite job persistence and day_revision idempotency."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from shared.atomic_file import write_json_atomic

logger = logging.getLogger(__name__)

INDEX_NAME = "revision_job_index.json"
META_NAME = "job_meta.json"


def index_path(data_dir: Path) -> Path:
    return data_dir / INDEX_NAME


def save_revision_index(data_dir: Path, index: dict[str, str]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(index_path(data_dir), index)


def write_job_meta(job_dir: Path, meta: dict[str, Any]) -> None:
    job_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(job_dir / META_NAME, meta)


def read_job_meta(job_dir: Path) -> dict[str, Any] | None:
    path = job_dir / META_NAME
    if not path.exists():
        return None
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(meta, dict) or meta.get("job_id") != job_dir.name:
            raise ValueError("invalid job identity")
        if not isinstance(meta.get("status"), str) or meta["status"] not in {"pending", "processing", "succeeded", "failed"}:
            raise ValueError("invalid job status")
        if not isinstance(meta.get("day_revision_id"), str):
            raise ValueError("invalid revision")
        if meta.get("owner_email") is not None and not isinstance(meta["owner_email"], str):
            raise ValueError("invalid owner")
        if not isinstance(meta.get("message"), str):
            raise ValueError("invalid message")
        if "submitted_at_ns" in meta and (type(meta["submitted_at_ns"]) is not int or meta["submitted_at_ns"] < 0):
            raise ValueError("invalid submission timestamp")
        return meta
    except (OSError, ValueError, UnicodeError):
        logger.warning("Ignoring unreadable or invalid job metadata: %s", job_dir.name)
        return None


def reload_jobs_from_disk(
    jobs_dir: Path,
    data_dir: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Rebuild in-memory jobs + revision index after BFF restart."""
    jobs: dict[str, dict[str, Any]] = {}
    # The index is a cache, never an authority for ownership or successful state.
    index: dict[str, str] = {}

    if not jobs_dir.exists():
        return jobs, index

    revisions = {}
    for child in jobs_dir.iterdir():
        if not child.is_dir():
            continue
        job_id = child.name
        meta = read_job_meta(child)
        if meta is None:
            # Missing/corrupt metadata must not become an unowned success.
            continue
        jobs[job_id] = meta
        rev = str(meta.get("day_revision_id") or "").strip()
        if rev:
            rank = (int(meta.get("submitted_at_ns") or 0), job_id)
            if rev not in revisions or rank > revisions[rev]:
                revisions[rev] = rank
                index[rev] = job_id

    return jobs, index


def idempotent_reuse_status(status: str) -> bool:
    """Same day_revision_id: reuse job while in-flight or already succeeded."""
    return status in ("pending", "processing", "running", "succeeded")
