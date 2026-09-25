"""Dev Lite job persistence and day_revision idempotency."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

INDEX_NAME = "revision_job_index.json"
META_NAME = "job_meta.json"


def index_path(data_dir: Path) -> Path:
    return data_dir / INDEX_NAME


def load_revision_index(data_dir: Path) -> dict[str, str]:
    path = index_path(data_dir)
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return {str(k): str(v) for k, v in raw.items()}
    except json.JSONDecodeError:
        return {}
    return {}


def save_revision_index(data_dir: Path, index: dict[str, str]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    index_path(data_dir).write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_job_meta(job_dir: Path, meta: dict[str, Any]) -> None:
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / META_NAME).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_job_meta(job_dir: Path) -> dict[str, Any] | None:
    path = job_dir / META_NAME
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def reload_jobs_from_disk(
    jobs_dir: Path,
    data_dir: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Rebuild in-memory jobs + revision index after BFF restart."""
    jobs: dict[str, dict[str, Any]] = {}
    index = load_revision_index(data_dir)

    if not jobs_dir.exists():
        return jobs, index

    for child in jobs_dir.iterdir():
        if not child.is_dir():
            continue
        job_id = child.name
        meta = read_job_meta(child)
        if meta is None:
            result_path = child / "result.json"
            if result_path.exists():
                meta = {
                    "job_id": job_id,
                    "day_revision_id": "",
                    "status": "succeeded",
                    "message": "Loaded from disk (legacy)",
                    "bundle_version": None,
                    "result": None,
                    "error": None,
                }
            else:
                continue
        jobs[job_id] = meta
        rev = str(meta.get("day_revision_id") or "").strip()
        if rev:
            index[rev] = job_id

    return jobs, index


def idempotent_reuse_status(status: str) -> bool:
    """Same day_revision_id: reuse job while in-flight or already succeeded."""
    return status in ("pending", "processing", "running", "succeeded")
