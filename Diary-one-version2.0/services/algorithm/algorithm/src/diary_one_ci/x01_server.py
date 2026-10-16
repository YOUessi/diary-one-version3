from __future__ import annotations

import argparse
import datetime

try:
    import cgi
except ModuleNotFoundError:  # Python 3.13+ — pip install legacy-cgi (provides cgi module)
    raise SystemExit(
        "Python 3.13+ removed stdlib cgi. Run: python -m pip install legacy-cgi"
    ) from None
import getpass
import hmac
import json
import math
import os
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Optional, Tuple

from .bundle import APP_LIBRARY_BUNDLE_VERSION_V03, APP_LIBRARY_BUNDLE_VERSION_V04
from .core import canonical_bytes
from .x01 import (
    FixtureEditorialAdapter,
    OpenAIResponsesAdapter,
    QwenChatCompletionsAdapter,
    X01ContractError,
    X01Error,
    X01ModelNotReady,
    X01PostModelContractError,
    X01_PIPELINE_VERSION,
    X01_SCHEMA_VERSION,
    model_run_audit_snapshot,
    run_x01,
)
from .x02 import (
    PERCEPTION_BATCH_MAX_ASSETS,
    PERCEPTION_BATCH_MAX_EVIDENCE_BYTES,
    PERCEPTION_BATCH_MAX_FRAMES,
    PERCEPTION_SINGLE_ASSET_RETRY_LIMIT,
    X02ContractError,
    X02Error,
    X02_EVALUATION_RUN_MODE,
    X02ExecutionError,
    X02_FIELD_DEGRADATION_SHA256,
    X02_FIELD_DEGRADATION_VERSION,
    X02ModelNotReady,
    X02_EXPERIMENT,
    X02_OBSERVATION_COMPATIBILITY_SHA256,
    X02_OBSERVATION_COMPATIBILITY_VERSION,
    X02_PIPELINE_VERSION,
    X02_PREVIEW_PATH,
    X02_RUN_SIDECAR_PATH,
    X02_SCHEMA_VERSION,
    X02_STORYLINE_CONTRACT_SHA256,
    X02_STORYLINE_CONTRACT_VERSION,
    X02_WRITER_SURFACE_POLICY_VERSION,
    X02_V03_PIPELINE_VERSION,
    X02_V03_PREVIEW_PATH,
    X02_V03_RUN_SIDECAR_PATH,
    X02_V03_SCHEMA_VERSION,
    run_x02,
    run_x02_v03,
    x02_runtime_policies,
    stage_run_audit_snapshot,
    stage_gateway_for_adapter,
)
from .codex_chapter_media import POLICY_VERSION as CHAPTER_MEDIA_POLICY_VERSION


DEFAULT_MAX_BODY_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_SIDECAR_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_ASSETS = 240
DEFAULT_QWEN_KEYCHAIN_SERVICE = "DiaryOne DashScope API Key"
DEFAULT_WEB_TEST_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
RUN_SIDECAR_SCHEMA_VERSION = "DIARY_ONE_X01_RUN_SIDECAR_V01"
HUMAN_EVALUATION_SCHEMA_VERSION = "DIARY_ONE_HUMAN_EVALUATION_V02"
RUN_AUDIT_SCHEMA_VERSION = "DIARY_ONE_X01_RUN_AUDIT_V01"
FAILED_RUN_AUDIT_SCHEMA_VERSION = "DIARY_ONE_X01_FAILED_RUN_AUDIT_V01"
X02_V03_RUN_AUDIT_SCHEMA_VERSION = "DIARY_ONE_X02_RUN_AUDIT_V03"
X02_V03_FAILED_RUN_AUDIT_SCHEMA_VERSION = "DIARY_ONE_X02_FAILED_RUN_AUDIT_V03"
X02_RUN_AUDIT_SCHEMA_VERSION = "DIARY_ONE_X02_RUN_AUDIT_V04_1"
X02_FAILED_RUN_AUDIT_SCHEMA_VERSION = "DIARY_ONE_X02_FAILED_RUN_AUDIT_V04_1"
_SIDECAR_WRITE_LOCK = threading.Lock()


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _default_run_audit_dir() -> Path:
    configured = os.environ.get("DIARY_ONE_X01_RUN_AUDIT_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "var" / "x01_runs"


def _default_x02_run_audit_dir() -> Path:
    configured = os.environ.get("DIARY_ONE_X02_RUN_AUDIT_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "var" / "x02_runs"


def _normalized_session_id(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("session_id must be a UUID string")
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise ValueError("session_id must be a valid UUID") from exc


def _atomic_write_json(path: Path, value: Dict[str, object]) -> None:
    _assert_json_storage_safe(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(value)
    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".%s." % path.name, suffix=".tmp", dir=str(path.parent), delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(str(temporary_path), str(path))
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def _assert_json_storage_safe(value: object, depth: int = 0) -> None:
    if depth > 64:
        raise ValueError("JSON nesting exceeds the storage safety limit")
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        for child in value.values():
            _assert_json_storage_safe(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            _assert_json_storage_safe(child, depth + 1)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("JSON numbers must be finite")
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise ValueError("sidecar contains a value that cannot be stored as JSON")


def _assert_no_embedded_images(value: object) -> None:
    if isinstance(value, dict):
        for child in value.values():
            _assert_no_embedded_images(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_embedded_images(child)
    elif isinstance(value, str) and value.lstrip().lower().startswith("data:image/"):
        raise ValueError("run audit must not contain embedded image payloads")


def _write_run_audit(
    audit_root: Path,
    manifest: Dict[str, object],
    result: Dict[str, object],
    materialization_duration_ms: float,
    x01_run_duration_ms: float,
    request_body_bytes: int,
) -> Path:
    session_id = _normalized_session_id(result.get("session_id"))
    if _normalized_session_id(manifest.get("session", {}).get("session_id")) != session_id:
        raise ValueError("manifest and result session IDs do not match")
    trace = result.get("trace")
    if not isinstance(trace, dict):
        raise ValueError("result.trace must be an object")
    run_id = _normalized_session_id(trace.get("run_id") or str(uuid.uuid4()))
    trace["run_id"] = run_id
    audit = {
        "schema_version": RUN_AUDIT_SCHEMA_VERSION,
        "run_id": run_id,
        "recorded_at": _utc_now(),
        "session_id": session_id,
        "image_payloads_included": False,
        "manifest": manifest,
        "result": result,
        "server_metrics": [
            {
                "stage": "REQUEST_MULTIPART_MATERIALIZATION",
                "duration_ms": round(max(0.0, materialization_duration_ms), 3),
                "request_body_bytes": request_body_bytes,
            },
            {
                "stage": "X01_RUN",
                "duration_ms": round(max(0.0, x01_run_duration_ms), 3),
            },
        ],
    }
    _assert_no_embedded_images(audit)
    session_root = audit_root / session_id
    archive = session_root / "runs" / (run_id + ".run_audit.json")
    latest = session_root / "run_audit.json"
    _atomic_write_json(archive, audit)
    _atomic_write_json(latest, audit)
    return latest


def _write_x02_run_audit(
    audit_root: Path,
    manifest: Dict[str, object],
    result: Dict[str, object],
    materialization_duration_ms: float,
    x02_run_duration_ms: float,
    request_body_bytes: int,
) -> Path:
    session_id = _normalized_session_id(result.get("session_id"))
    if _normalized_session_id(manifest.get("session", {}).get("session_id")) != session_id:
        raise ValueError("manifest and result session IDs do not match")
    trace = result.get("trace")
    if not isinstance(trace, dict):
        raise ValueError("result.trace must be an object")
    run_id = _normalized_session_id(trace.get("run_id") or str(uuid.uuid4()))
    trace["run_id"] = run_id
    result_schema_version = result.get("schema_version")
    if result_schema_version == X02_SCHEMA_VERSION:
        audit_schema_version = X02_RUN_AUDIT_SCHEMA_VERSION
    elif result_schema_version == X02_V03_SCHEMA_VERSION:
        audit_schema_version = X02_V03_RUN_AUDIT_SCHEMA_VERSION
    else:
        raise ValueError("unknown X02 result schema version")
    audit = {
        "schema_version": audit_schema_version,
        "run_id": run_id,
        "recorded_at": _utc_now(),
        "session_id": session_id,
        "evaluation_run_mode": X02_EVALUATION_RUN_MODE,
        "cross_run_semantic_cache_used": False,
        "image_payloads_included": False,
        "manifest": manifest,
        "result": result,
        "server_metrics": [
            {
                "stage": "REQUEST_MULTIPART_MATERIALIZATION",
                "duration_ms": round(max(0.0, materialization_duration_ms), 3),
                "request_body_bytes": request_body_bytes,
            },
            {
                "stage": "X02_STAGED_RUN",
                "duration_ms": round(max(0.0, x02_run_duration_ms), 3),
            },
        ],
    }
    _assert_no_embedded_images(audit)
    session_root = audit_root / session_id
    archive = session_root / "runs" / (run_id + ".run_audit.json")
    latest = session_root / "run_audit.json"
    _atomic_write_json(archive, audit)
    _atomic_write_json(latest, audit)
    return latest


def _write_x02_failed_run_audit(
    audit_root: Path,
    manifest: Dict[str, object],
    error: X02ExecutionError,
    materialization_duration_ms: float,
    request_body_bytes: int,
    audit_schema_version: str = X02_FAILED_RUN_AUDIT_SCHEMA_VERSION,
) -> Tuple[str, Path]:
    session = manifest.get("session")
    if not isinstance(session, dict):
        raise ValueError("failed X02 run manifest.session must be an object")
    session_id = _normalized_session_id(session.get("session_id"))
    failure_id = str(uuid.uuid4())
    stage_runs = [stage_run_audit_snapshot(run) for run in error.stage_runs]
    historical_v03 = audit_schema_version == X02_V03_FAILED_RUN_AUDIT_SCHEMA_VERSION
    if historical_v03:
        for item in stage_runs:
            item.pop("call_status", None)
    completed_stage_calls = (
        stage_runs
        if historical_v03 else [
            item for item in stage_runs if item.get("call_status") == "COMPLETED"
        ]
    )
    audit = {
        "schema_version": audit_schema_version,
        "failure_id": failure_id,
        "recorded_at": _utc_now(),
        "session_id": session_id,
        "status": "FAILED",
        "evaluation_run_mode": X02_EVALUATION_RUN_MODE,
        "cross_run_semantic_cache_used": False,
        "image_payloads_included": False,
        "failure": {
            "stage": error.stage,
            "code": error.code,
            "message": str(error)[:2_000],
        },
        "manifest": manifest,
        "completed_stage_calls": completed_stage_calls,
        "stage_metrics": [{
            "stage": "REQUEST_MULTIPART_MATERIALIZATION",
            "duration_ms": round(max(0.0, materialization_duration_ms), 3),
            "request_body_bytes": request_body_bytes,
            "model_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
        }] + [{
            "stage": item["stage"],
            "duration_ms": round(float(item["latency_seconds"]) * 1_000.0, 3),
            "model_calls": item["model_calls"],
            "input_tokens": item["input_tokens"],
            "output_tokens": item["output_tokens"],
            "estimated_cost_usd": item["estimated_cost_usd"],
            "request_id": item["request_id"],
            "pricing_basis": item["pricing"]["basis"],
        } for item in stage_runs],
    }
    if not historical_v03:
        audit["stage_call_attempts"] = stage_runs
    _assert_no_embedded_images(audit)
    session_root = audit_root / session_id
    archive = session_root / "failures" / (failure_id + ".failed_run_audit.json")
    latest = session_root / "failed_run_audit.json"
    _atomic_write_json(archive, audit)
    _atomic_write_json(latest, audit)
    return failure_id, latest


def _write_failed_run_audit(
    audit_root: Path,
    manifest: Dict[str, object],
    error: X01PostModelContractError,
    materialization_duration_ms: float,
    request_body_bytes: int,
) -> Tuple[str, Path]:
    session = manifest.get("session")
    if not isinstance(session, dict):
        raise ValueError("failed run manifest.session must be an object")
    session_id = _normalized_session_id(session.get("session_id"))
    failure_id = str(uuid.uuid4())
    model = model_run_audit_snapshot(error.model_run)
    model_calls = model.get("model_calls")
    input_tokens = model.get("input_tokens")
    output_tokens = model.get("output_tokens")
    pricing = model.get("pricing")
    estimated_cost_usd = (
        pricing.get("estimated_cost_usd") if isinstance(pricing, dict) else None
    )
    error_code = _contract_error_code(str(error))
    audit = {
        "schema_version": FAILED_RUN_AUDIT_SCHEMA_VERSION,
        "failure_id": failure_id,
        "recorded_at": _utc_now(),
        "session_id": session_id,
        "status": "FAILED",
        "image_payloads_included": False,
        "failure": {
            "stage": "DETERMINISTIC_VALIDATION_SELECTION",
            "code": error_code,
            "message": str(error)[:2_000],
        },
        "manifest": manifest,
        "model_run": model,
        "stage_metrics": [
            {
                "stage": "REQUEST_MULTIPART_MATERIALIZATION",
                "duration_ms": round(max(0.0, materialization_duration_ms), 3),
                "request_body_bytes": request_body_bytes,
                "model_calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
            },
            {
                "stage": "BUNDLE_LOAD",
                "duration_ms": round(error.bundle_load_seconds * 1_000.0, 3),
                "model_calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
            },
            {
                "stage": "EDITORIAL_MODEL_BRIDGE",
                "duration_ms": round(error.model_seconds * 1_000.0, 3),
                "model_calls": model_calls,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost_usd": estimated_cost_usd,
            },
            {
                "stage": "DETERMINISTIC_VALIDATION_SELECTION_FAILED",
                "duration_ms": round(error.validation_seconds * 1_000.0, 3),
                "model_calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
            },
        ],
    }
    _assert_no_embedded_images(audit)
    session_root = audit_root / session_id
    archive = session_root / "failures" / (failure_id + ".failed_run_audit.json")
    latest = session_root / "failure_audit.json"
    _atomic_write_json(archive, audit)
    _atomic_write_json(latest, audit)
    return failure_id, latest


def _contract_error_code(message: str) -> str:
    lowered = message.lower()
    if "evidence" in lowered and "not presented to the model" in lowered:
        return "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL"
    if "selected_evidence" in lowered or "model evidence" in lowered:
        return "MODEL_EVIDENCE_REPORT_INVALID"
    if "pricing" in lowered or "token" in lowered or "model_calls" in lowered:
        return "MODEL_USAGE_METADATA_INVALID"
    return "POST_MODEL_CONTRACT_VIOLATION"


def _validate_run_sidecar(value: object) -> Tuple[str, Optional[Dict[str, object]], Optional[Dict[str, object]]]:
    if not isinstance(value, dict):
        raise ValueError("sidecar body must be a JSON object")
    if value.get("schema_version") != RUN_SIDECAR_SCHEMA_VERSION:
        raise ValueError("sidecar schema_version is unsupported")
    session_id = _normalized_session_id(value.get("session_id"))
    client_trace = value.get("client_trace")
    human_review = value.get("human_review")
    if client_trace is not None and not isinstance(client_trace, dict):
        raise ValueError("client_trace must be an object")
    if human_review is not None:
        if not isinstance(human_review, dict):
            raise ValueError("human_review must be an object")
        if human_review.get("schema_version") != HUMAN_EVALUATION_SCHEMA_VERSION:
            raise ValueError("human_review schema_version is unsupported")
        if _normalized_session_id(human_review.get("session_id")) != session_id:
            raise ValueError("human_review session_id must match sidecar session_id")
        _normalized_session_id(human_review.get("evaluation_id"))
        try:
            _normalized_session_id(human_review.get("run_id"))
        except ValueError as exc:
            raise ValueError("human_review run_id must be a valid UUID") from exc
        for field in ("bundle_manifest_sha256", "pipeline_version", "request_id"):
            supplied = human_review.get(field)
            if not isinstance(supplied, str) or not supplied.strip():
                raise ValueError("human_review %s must be a non-empty string" % field)
        revision = human_review.get("revision")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
            raise ValueError("human_review revision must be an integer greater than or equal to zero")
    if client_trace is None and human_review is None:
        raise ValueError("sidecar requires client_trace or human_review")
    _assert_no_embedded_images(value)
    _assert_json_storage_safe(value)
    return session_id, client_trace, human_review


def _write_run_sidecar(
    audit_root: Path,
    value: object,
    expected_pipeline_version: Optional[str] = None,
) -> Tuple[str, list]:
    with _SIDECAR_WRITE_LOCK:
        return _write_run_sidecar_locked(
            audit_root,
            value,
            expected_pipeline_version,
        )


def _write_run_sidecar_locked(
    audit_root: Path,
    value: object,
    expected_pipeline_version: Optional[str] = None,
) -> Tuple[str, list]:
    session_id, client_trace, human_review = _validate_run_sidecar(value)
    session_root = audit_root / session_id
    if not (session_root / "run_audit.json").is_file():
        raise ValueError("sidecar session_id does not match a recorded research run")
    received_at = _utc_now()
    saved = []
    prepared_review = (
        _prepare_human_review_write(
            audit_root,
            session_id,
            human_review,
            expected_pipeline_version,
        )
        if human_review is not None else None
    )
    if client_trace is not None:
        bound_audit = _resolve_recorded_run(audit_root, session_id, client_trace)
        _assert_recorded_pipeline_version(bound_audit, expected_pipeline_version)
        record = {
            "schema_version": "DIARY_ONE_X01_CLIENT_TRACE_SIDECAR_V01",
            "session_id": session_id,
            "received_at": received_at,
            "bound_run_id": bound_audit["run_id"],
            "client_trace": client_trace,
        }
        if client_trace.get("run_id") is not None:
            _atomic_write_json(
                session_root / "client_traces" / (str(bound_audit["run_id"]) + ".client_trace.json"),
                record,
            )
        _atomic_write_json(session_root / "client_trace.json", record)
        saved.append("client_trace")
    if human_review is not None:
        if prepared_review is None:  # pragma: no cover - internal invariant
            raise ValueError("human review preparation is missing")
        bound_audit = prepared_review["bound_audit"]
        evaluation_id = str(prepared_review["evaluation_id"])
        revision = int(prepared_review["revision"])
        archive = prepared_review["archive"]
        if not isinstance(bound_audit, dict) or not isinstance(archive, Path):
            raise ValueError("human review preparation is invalid")
        record = {
            "schema_version": "DIARY_ONE_X01_HUMAN_REVIEW_SIDECAR_V01",
            "session_id": session_id,
            "received_at": received_at,
            "evaluation_id": evaluation_id,
            "revision": revision,
            "bound_run": _audit_binding(bound_audit),
            "human_review": human_review,
        }
        existing = prepared_review.get("existing")
        if existing is not None:
            if not isinstance(existing, dict):  # pragma: no cover - internal invariant
                raise ValueError("recorded human review is invalid")
            record = existing
        else:
            _atomic_write_json(archive, record)
        _atomic_write_json(session_root / "human_review.json", record)
        saved.append("human_review")
    return session_id, saved


def _prepare_human_review_write(
    audit_root: Path,
    session_id: str,
    human_review: Dict[str, object],
    expected_pipeline_version: Optional[str] = None,
) -> Dict[str, object]:
    bound_audit = _resolve_recorded_run(audit_root, session_id, human_review)
    _assert_recorded_pipeline_version(bound_audit, expected_pipeline_version)
    evaluation_id = _normalized_session_id(human_review["evaluation_id"])
    revision = int(human_review["revision"])
    review_root = audit_root / session_id / "reviews" / evaluation_id
    archive = review_root / ("%d.human_review.json" % revision)
    higher_revisions = [
        candidate_revision
        for candidate_revision in (
            _review_revision(path) for path in review_root.glob("*.human_review.json")
        )
        if candidate_revision is not None and candidate_revision > revision
    ] if review_root.is_dir() else []
    if higher_revisions:
        raise ValueError(
            "human_review revision is stale; recorded revision %d is newer"
            % max(higher_revisions)
        )
    existing = None
    if archive.is_file():
        existing = _read_json_object(archive, "recorded human review")
        if canonical_bytes(existing.get("human_review")) != canonical_bytes(human_review):
            raise ValueError("human_review revision conflicts with different recorded content")
    return {
        "bound_audit": bound_audit,
        "evaluation_id": evaluation_id,
        "revision": revision,
        "archive": archive,
        "existing": existing,
    }


def _read_json_object(path: Path, label: str) -> Dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("%s is unreadable" % label) from exc
    if not isinstance(value, dict):
        raise ValueError("%s must be a JSON object" % label)
    return value


def _resolve_recorded_run(
    audit_root: Path,
    session_id: str,
    binding: Dict[str, object],
) -> Dict[str, object]:
    run_id_value = binding.get("run_id")
    if run_id_value is not None:
        run_id = _normalized_session_id(run_id_value)
        path = audit_root / session_id / "runs" / (run_id + ".run_audit.json")
    else:
        path = audit_root / session_id / "run_audit.json"
    if not path.is_file():
        raise ValueError("sidecar run_id does not match a recorded research run")
    audit = _read_json_object(path, "recorded research run audit")
    if _normalized_session_id(audit.get("session_id")) != session_id:
        raise ValueError("recorded run audit has the wrong session_id")
    audit_run_id = _normalized_session_id(audit.get("run_id"))
    if run_id_value is not None and _normalized_session_id(run_id_value) != audit_run_id:
        raise ValueError("sidecar run_id does not match recorded run audit")
    result = audit.get("result")
    if not isinstance(result, dict):
        raise ValueError("recorded run audit result is invalid")
    trace = result.get("trace")
    if not isinstance(trace, dict):
        raise ValueError("recorded run audit trace is invalid")
    expected = {
        "bundle_manifest_sha256": result.get("bundle_manifest_sha256"),
        "pipeline_version": trace.get("pipeline_version"),
        "request_id": trace.get("request_id"),
    }
    for field, expected_value in expected.items():
        supplied = binding.get(field)
        if supplied is not None and supplied != expected_value:
            raise ValueError("sidecar %s does not match recorded run audit" % field)
    supplied_session = binding.get("session_id")
    if supplied_session is not None and _normalized_session_id(supplied_session) != session_id:
        raise ValueError("sidecar nested session_id does not match envelope")
    return audit


def _audit_binding(audit: Dict[str, object]) -> Dict[str, object]:
    result = audit["result"]
    if not isinstance(result, dict):  # pragma: no cover - verified by resolver
        raise ValueError("recorded run audit result is invalid")
    trace = result["trace"]
    if not isinstance(trace, dict):  # pragma: no cover - verified by resolver
        raise ValueError("recorded run audit trace is invalid")
    return {
        "run_id": audit["run_id"],
        "bundle_manifest_sha256": result["bundle_manifest_sha256"],
        "pipeline_version": trace["pipeline_version"],
        "request_id": trace["request_id"],
    }


def _assert_recorded_pipeline_version(
    audit: Dict[str, object],
    expected_pipeline_version: Optional[str],
) -> None:
    if expected_pipeline_version is None:
        return
    result = audit.get("result")
    if not isinstance(result, dict):
        raise ValueError("recorded run audit result is invalid")
    trace = result.get("trace")
    if not isinstance(trace, dict):
        raise ValueError("recorded run audit trace is invalid")
    actual_pipeline_version = trace.get("pipeline_version")
    if actual_pipeline_version != expected_pipeline_version:
        raise ValueError(
            "sidecar route expects pipeline_version %s; recorded run uses %s"
            % (expected_pipeline_version, actual_pipeline_version)
        )


def _review_revision(path: Path) -> Optional[int]:
    prefix = path.name.split(".", 1)[0]
    try:
        revision = int(prefix)
    except ValueError:
        return None
    return revision if revision >= 0 else None


def _macos_keychain_qwen_api_key(
    service: str = DEFAULT_QWEN_KEYCHAIN_SERVICE,
) -> str:
    """Read the local research credential without printing or exporting it."""
    if sys.platform != "darwin":
        return ""
    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                getpass.getuser(),
                "-s",
                service,
                "-w",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _resolve_qwen_api_key() -> Tuple[Optional[str], str]:
    environment_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    if environment_key:
        return environment_key, "environment"
    keychain_key = _macos_keychain_qwen_api_key()
    if keychain_key:
        return keychain_key, "macos_keychain"
    return None, "missing"


def _model_not_ready_payload(adapter: object) -> Dict[str, object]:
    credential_environment = str(getattr(adapter, "credential_environment", "MODEL_API_KEY"))
    return {
        "error": "model_not_ready",
        "message": (
            "Configure %s on the Mac X01 research server. No fixture fallback was used."
            % credential_environment
        ),
    }


class X01RequestHandler(BaseHTTPRequestHandler):
    server_version = "DiaryOneResearch/0.2"
    adapter = QwenChatCompletionsAdapter()
    stage_gateway = stage_gateway_for_adapter(adapter)
    max_body_bytes = DEFAULT_MAX_BODY_BYTES
    max_sidecar_bytes = DEFAULT_MAX_SIDECAR_BYTES
    max_assets = DEFAULT_MAX_ASSETS
    bearer_token = ""
    allowed_origins = DEFAULT_WEB_TEST_ORIGINS
    run_audit_dir = _default_run_audit_dir()
    x02_run_audit_dir = _default_x02_run_audit_dir()

    def do_OPTIONS(self) -> None:
        if self.path.rstrip("/") not in (
            "/health",
            "/x01/v0.1/preview",
            "/x01/v0.1/run-sidecar",
            X02_PREVIEW_PATH,
            X02_RUN_SIDECAR_PATH,
            X02_V03_PREVIEW_PATH,
            X02_V03_RUN_SIDECAR_PATH,
        ):
            self._json(404, {"error": "not_found"})
            return
        if not self._origin_allowed():
            self._json(403, {"error": "origin_not_allowed"})
            return
        self.send_response(204)
        self._cors_headers()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.rstrip("/") != "/health":
            self._json(404, {"error": "not_found"})
            return
        if not self._origin_allowed():
            self._json(403, {"error": "origin_not_allowed"})
            return
        if not self._authorized():
            self._json(401, {"error": "unauthorized"})
            return
        self._json(200, {
            "status": "ok",
            "schemaVersion": X02_SCHEMA_VERSION,
            "experiment": X02_EXPERIMENT,
            "experimental": True,
            "leaderboardEligible": False,
            "productionReady": bool(
                self.stage_gateway.ready
                and (
                    "alibaba" in str(self.stage_gateway.provider or "").lower()
                    or "qwen" in str(self.stage_gateway.model or "").lower()
                    or "dashscope" in str(self.stage_gateway.provider or "").lower()
                )
            ),
            "modelReady": self.stage_gateway.ready,
            "provider": self.stage_gateway.provider,
            "model": self.stage_gateway.model,
            "maxAssets": self.max_assets,
            "previewPath": X02_PREVIEW_PATH,
            "runSidecarPath": X02_RUN_SIDECAR_PATH,
            "storylineContractVersion": X02_STORYLINE_CONTRACT_VERSION,
            "storylineContractSHA256": X02_STORYLINE_CONTRACT_SHA256,
            "observationSemanticContractVersion": X02_OBSERVATION_COMPATIBILITY_VERSION,
            "observationSemanticContractSHA256": X02_OBSERVATION_COMPATIBILITY_SHA256,
            "fieldDegradationContractVersion": X02_FIELD_DEGRADATION_VERSION,
            "fieldDegradationContractSHA256": X02_FIELD_DEGRADATION_SHA256,
            "writerSurfacePolicyVersion": X02_WRITER_SURFACE_POLICY_VERSION,
            "chapterMediaPolicyVersion": CHAPTER_MEDIA_POLICY_VERSION,
            "runtimePolicies": x02_runtime_policies(),
            "perceptionBatchMaxAssets": PERCEPTION_BATCH_MAX_ASSETS,
            "perceptionBatchMaxFrames": PERCEPTION_BATCH_MAX_FRAMES,
            "perceptionBatchMaxEvidenceBytes": PERCEPTION_BATCH_MAX_EVIDENCE_BYTES,
            "perceptionSingleAssetRetryLimit": PERCEPTION_SINGLE_ASSET_RETRY_LIMIT,
            "evaluationRunMode": X02_EVALUATION_RUN_MODE,
            "crossRunSemanticCacheUsed": False,
            "appLibraryBundleVersion": APP_LIBRARY_BUNDLE_VERSION_V03,
            "supportedAppLibraryBundleVersions": [
                "DIARY_ONE_APP_LIBRARY_BUNDLE_V01", "DIARY_ONE_APP_LIBRARY_BUNDLE_V02",
                APP_LIBRARY_BUNDLE_VERSION_V03, APP_LIBRARY_BUNDLE_VERSION_V04,
            ],
            "phoneTestSpatialTransforms": ["CENTER_CROP_ASPECT_FILL", "ASPECT_FIT_LETTERBOX"],
            "phoneTestEvidenceProfileVersion": "PHONE_TEST_DURATION_WINDOWS_V01",
            "historicalX01": {
                "schemaVersion": X01_SCHEMA_VERSION,
                "previewPath": "/x01/v0.1/preview",
                "runSidecarPath": "/x01/v0.1/run-sidecar",
                "executionMode": "HISTORICAL_COMPATIBILITY_BRIDGE",
            },
            "historicalX02V03": {
                "schemaVersion": X02_V03_SCHEMA_VERSION,
                "pipelineVersion": X02_V03_PIPELINE_VERSION,
                "previewPath": X02_V03_PREVIEW_PATH,
                "runSidecarPath": X02_V03_RUN_SIDECAR_PATH,
                "executionMode": "HISTORICAL_COMPATIBILITY_ROUTE",
            },
            "maxSidecarBytes": self.max_sidecar_bytes,
            "runAuditEnabled": True,
            "failedRunAuditEnabled": True,
            "granularObservationValidation": True,
            "fieldLevelObservationDegradation": True,
            "durationAwarePhoneTestEvidence": True,
            "contractBasis": "CANONICAL_V1_25_S00_S13",
            "executionMode": "X02_STAGED_REAL_MEDIA_PREVIEW_NOT_PRODUCTION",
            "pipelineVersion": X02_PIPELINE_VERSION,
            "stagedRealMediaPreviewImplemented": True,
            "storylineSegmentationImplemented": True,
            "fullStagedPipelineImplemented": False,
            "s13Executed": False,
        })

    def do_POST(self) -> None:
        request_path = self.path.rstrip("/")
        if request_path not in (
            "/x01/v0.1/preview",
            "/x01/v0.1/run-sidecar",
            X02_PREVIEW_PATH,
            X02_RUN_SIDECAR_PATH,
            X02_V03_PREVIEW_PATH,
            X02_V03_RUN_SIDECAR_PATH,
        ):
            self._json(404, {"error": "not_found"})
            return
        if not self._origin_allowed():
            self._json(403, {"error": "origin_not_allowed"})
            return
        if not self._authorized():
            self._json(401, {"error": "unauthorized"})
            return
        if request_path in (
            "/x01/v0.1/run-sidecar",
            X02_RUN_SIDECAR_PATH,
            X02_V03_RUN_SIDECAR_PATH,
        ):
            if request_path == X02_RUN_SIDECAR_PATH:
                expected_pipeline_version = X02_PIPELINE_VERSION
            elif request_path == X02_V03_RUN_SIDECAR_PATH:
                expected_pipeline_version = X02_V03_PIPELINE_VERSION
            else:
                expected_pipeline_version = X01_PIPELINE_VERSION
            self._handle_run_sidecar(
                self.x02_run_audit_dir
                if request_path.startswith("/x02/")
                else self.run_audit_dir,
                expected_pipeline_version,
            )
            return
        is_x02 = request_path.startswith("/x02/")
        runtime = self.stage_gateway if is_x02 else self.adapter
        if not runtime.ready:
            self._json(503, _model_not_ready_payload(runtime))
            return
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/form-data"):
            self._json(415, {"error": "multipart_required"})
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > self.max_body_bytes:
            self._json(413, {
                "error": "upload_size_invalid",
                "maxBytes": self.max_body_bytes,
            })
            return

        request_started = time.monotonic()
        manifest: Optional[Dict[str, object]] = None
        materialization_duration_ms = 0.0
        try:
            with tempfile.TemporaryDirectory(prefix="diary-one-x02-" if is_x02 else "diary-one-x01-") as temporary:
                materialization_started = time.monotonic()
                manifest_path = self._materialize_bundle(Path(temporary), content_type, content_length)
                materialization_complete = time.monotonic()
                loaded_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if not isinstance(loaded_manifest, dict):
                    raise ValueError("manifest must be a JSON object")
                manifest = loaded_manifest
                pipeline_started = time.monotonic()
                if request_path == X02_PREVIEW_PATH:
                    result = run_x02(manifest_path, self.stage_gateway)
                elif request_path == X02_V03_PREVIEW_PATH:
                    result = run_x02_v03(manifest_path, self.stage_gateway)
                else:
                    if manifest.get("bundle_version") == APP_LIBRARY_BUNDLE_VERSION_V04:
                        raise ValueError("App Library Bundle V04 requires the current X02 preview")
                    result = run_x01(manifest_path, self.adapter)
                pipeline_complete = time.monotonic()
                materialization_duration_ms = (materialization_complete - materialization_started) * 1_000.0
                pipeline_run_duration_ms = (pipeline_complete - pipeline_started) * 1_000.0
                trace = result.get("trace")
                if isinstance(trace, dict):
                    trace["completed_at"] = _utc_now()
                    trace["server_metrics"] = [{
                        "stage": "REQUEST_MULTIPART_MATERIALIZATION",
                        "duration_ms": round(materialization_duration_ms, 3),
                        "request_body_bytes": content_length,
                    }]
                    trace["server_total_before_audit_ms"] = round(
                        (pipeline_complete - request_started) * 1_000.0, 3
                    )
                if is_x02:
                    _write_x02_run_audit(
                        self.x02_run_audit_dir,
                        manifest,
                        result,
                        materialization_duration_ms,
                        pipeline_run_duration_ms,
                        content_length,
                    )
                else:
                    _write_run_audit(
                        self.run_audit_dir,
                        manifest,
                        result,
                        materialization_duration_ms,
                        pipeline_run_duration_ms,
                        content_length,
                    )
            self._json(200, result)
        except (X01ModelNotReady, X02ModelNotReady) as exc:
            self._json(503, {"error": "model_not_ready", "message": str(exc)})
        except X02ExecutionError as exc:
            failure_id: Optional[str] = None
            if manifest is not None:
                try:
                    failure_id, _ = _write_x02_failed_run_audit(
                        self.x02_run_audit_dir,
                        manifest,
                        exc,
                        materialization_duration_ms,
                        content_length,
                        (
                            X02_V03_FAILED_RUN_AUDIT_SCHEMA_VERSION
                            if request_path == X02_V03_PREVIEW_PATH
                            else X02_FAILED_RUN_AUDIT_SCHEMA_VERSION
                        ),
                    )
                except (OSError, ValueError):
                    failure_id = None
            response = {
                "error": "staged_execution_failed",
                "code": exc.code,
                "stage": exc.stage,
                "message": str(exc),
                "model_call_completed": (
                    bool(exc.stage_runs)
                    if request_path == X02_V03_PREVIEW_PATH else any(
                        run.call_status == "COMPLETED" for run in exc.stage_runs
                    )
                ),
                "failure_audit_saved": bool(failure_id),
            }
            if request_path != X02_V03_PREVIEW_PATH:
                response["model_call_attempted"] = bool(exc.stage_runs)
            if failure_id:
                response["failure_id"] = failure_id
            status = 422 if exc.code in (
                "MODEL_STRUCTURED_OUTPUT_INVALID",
                "MODEL_RESPONSE_NOT_JSON",
                "POST_MODEL_CONTRACT_VIOLATION",
            ) else 502
            self._json(status, response)
        except X01PostModelContractError as exc:
            failure_id: Optional[str] = None
            if manifest is not None:
                try:
                    failure_id, _ = _write_failed_run_audit(
                        self.run_audit_dir,
                        manifest,
                        exc,
                        materialization_duration_ms,
                        content_length,
                    )
                except (OSError, ValueError):
                    failure_id = None
            response: Dict[str, object] = {
                "error": "contract_violation",
                "code": _contract_error_code(str(exc)),
                "message": str(exc),
                "model_call_completed": True,
                "failure_audit_saved": bool(failure_id),
            }
            if failure_id:
                response["failure_id"] = failure_id
            self._json(422, response)
        except (ValueError, X01ContractError, X02ContractError) as exc:
            self._json(422, {"error": "contract_violation", "message": str(exc)})
        except (X01Error, X02Error) as exc:
            self._json(502, {"error": "model_request_failed", "message": str(exc)})
        except Exception as exc:  # pragma: no cover - last-resort server boundary
            self._json(500, {"error": "internal_error", "message": str(exc)})

    def _handle_run_sidecar(
        self,
        audit_root: Path,
        expected_pipeline_version: str,
    ) -> None:
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().split(";", 1)[0].strip() == "application/json":
            self._json(415, {"error": "json_required"})
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > self.max_sidecar_bytes:
            self._json(413, {
                "error": "sidecar_size_invalid",
                "maxBytes": self.max_sidecar_bytes,
            })
            return
        try:
            raw = self.rfile.read(content_length)
            value = json.loads(raw.decode("utf-8"))
            session_id, saved = _write_run_sidecar(
                audit_root,
                value,
                expected_pipeline_version,
            )
            self._json(200, {
                "status": "saved",
                "session_id": session_id,
                "saved": saved,
            })
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._json(422, {"error": "sidecar_invalid", "message": str(exc)})
        except OSError as exc:
            self._json(500, {"error": "sidecar_write_failed", "message": str(exc)})

    def _materialize_bundle(self, root: Path, content_type: str, content_length: int) -> Path:
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": str(content_length),
            },
            keep_blank_values=True,
        )
        manifest_part = _single_form_part(form, "manifest")
        manifest_bytes = _part_bytes(manifest_part)
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("manifest is not valid UTF-8 JSON") from exc
        assets = manifest.get("assets")
        if not isinstance(assets, list) or not assets:
            raise ValueError("manifest.assets must be a non-empty array")
        if len(assets) > self.max_assets:
            raise ValueError(
                "The local staged preview accepts at most %d assets per synthetic day; this bundle has %d"
                % (self.max_assets, len(assets))
            )

        manifest_path = root / "bundle.json"
        manifest_path.write_bytes(manifest_bytes)
        for asset in assets:
            if not isinstance(asset, dict) or not isinstance(asset.get("frames"), list):
                raise ValueError("manifest asset/frame structure is invalid")
            for frame in asset["frames"]:
                if not isinstance(frame, dict):
                    raise ValueError("manifest frame must be an object")
                frame_id = str(frame.get("frame_id", ""))
                relative = Path(str(frame.get("relative_path", "")))
                if not frame_id or relative.is_absolute():
                    raise ValueError("frame_id and a relative_path are required")
                destination = (root / relative).resolve()
                try:
                    destination.relative_to(root.resolve())
                except ValueError as exc:
                    raise ValueError("frame relative_path escapes the bundle") from exc
                part = _single_form_part(form, frame_id)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(_part_bytes(part))
        # Optional App → cloud preference contract (soft editorial; never invents facts).
        profile_part = _optional_form_part(form, "app_client_profile")
        if profile_part is not None:
            from . import app_client_profile as client_profile

            client_profile.write_profile(root, _part_bytes(profile_part))
        return manifest_path

    def _json(self, status: int, value: Dict[str, object]) -> None:
        data = canonical_bytes(value)
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _origin_allowed(self) -> bool:
        origin = self.headers.get("Origin")
        return origin is None or origin in self.allowed_origins

    def _cors_headers(self) -> None:
        origin = self.headers.get("Origin")
        if origin and origin in self.allowed_origins:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def _authorized(self) -> bool:
        if not self.bearer_token:
            return True
        supplied = self.headers.get("Authorization", "")
        expected = "Bearer " + self.bearer_token
        return hmac.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8"))


def _single_form_part(form: cgi.FieldStorage, name: str) -> cgi.FieldStorage:
    if name not in form:
        raise ValueError("multipart field is missing: %s" % name)
    value = form[name]
    if isinstance(value, list):
        raise ValueError("multipart field must appear exactly once: %s" % name)
    return value


def _optional_form_part(form: cgi.FieldStorage, name: str):
    if name not in form:
        return None
    value = form[name]
    if isinstance(value, list):
        if not value:
            return None
        if len(value) > 1:
            raise ValueError("multipart field must appear at most once: %s" % name)
        return value[0]
    return value


def _part_bytes(part: cgi.FieldStorage) -> bytes:
    if part.file is not None:
        value = part.file.read()
        return value if isinstance(value, bytes) else str(value).encode("utf-8")
    value = part.value
    return value if isinstance(value, bytes) else str(value).encode("utf-8")


def make_server(
    host: str,
    port: int,
    adapter_name: str = "qwen",
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    max_sidecar_bytes: int = DEFAULT_MAX_SIDECAR_BYTES,
    max_assets: int = DEFAULT_MAX_ASSETS,
    bearer_token: str = "",
    tls_cert: Optional[str] = None,
    tls_key: Optional[str] = None,
    qwen_api_key: Optional[str] = None,
    allowed_origins: Tuple[str, ...] = DEFAULT_WEB_TEST_ORIGINS,
    run_audit_dir: Optional[Path] = None,
    x02_run_audit_dir: Optional[Path] = None,
) -> ThreadingHTTPServer:
    if adapter_name == "fixture":
        adapter = FixtureEditorialAdapter()
    elif adapter_name == "qwen":
        adapter = QwenChatCompletionsAdapter(api_key=qwen_api_key)
    elif adapter_name == "openai":
        adapter = OpenAIResponsesAdapter()
    else:
        raise ValueError("unknown adapter: %s" % adapter_name)

    class ConfiguredHandler(X01RequestHandler):
        pass

    ConfiguredHandler.adapter = adapter
    ConfiguredHandler.stage_gateway = stage_gateway_for_adapter(adapter)
    ConfiguredHandler.max_body_bytes = max_body_bytes
    ConfiguredHandler.max_sidecar_bytes = max_sidecar_bytes
    ConfiguredHandler.max_assets = max_assets
    ConfiguredHandler.bearer_token = bearer_token
    ConfiguredHandler.allowed_origins = allowed_origins
    ConfiguredHandler.run_audit_dir = (run_audit_dir or _default_run_audit_dir()).resolve()
    ConfiguredHandler.x02_run_audit_dir = (
        x02_run_audit_dir or _default_x02_run_audit_dir()
    ).resolve()
    server = ThreadingHTTPServer((host, port), ConfiguredHandler)
    if bool(tls_cert) != bool(tls_key):
        server.server_close()
        raise ValueError("both tls_cert and tls_key are required")
    if tls_cert and tls_key:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(tls_cert, tls_key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
    server.diary_one_tls_enabled = bool(tls_cert)  # type: ignore[attr-defined]
    return server


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Diary One staged research preview server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--adapter", choices=("qwen", "openai", "fixture"), default="qwen")
    parser.add_argument("--max-assets", type=int, default=int(os.environ.get("DIARY_ONE_X01_MAX_ASSETS", DEFAULT_MAX_ASSETS)))
    parser.add_argument(
        "--run-audit-dir",
        default=os.environ.get("DIARY_ONE_X01_RUN_AUDIT_DIR"),
        help="Directory for image-free historical X01 run audits and review sidecars.",
    )
    parser.add_argument(
        "--x02-run-audit-dir",
        default=os.environ.get("DIARY_ONE_X02_RUN_AUDIT_DIR"),
        help="Directory for image-free X02 staged run audits and review sidecars.",
    )
    parser.add_argument("--bearer-token", default=os.environ.get("DIARY_ONE_X01_BEARER_TOKEN", ""))
    parser.add_argument("--tls-cert", default=os.environ.get("DIARY_ONE_X01_TLS_CERT"))
    parser.add_argument("--tls-key", default=os.environ.get("DIARY_ONE_X01_TLS_KEY"))
    parser.add_argument(
        "--allowed-origin",
        action="append",
        dest="allowed_origins",
        help="Exact Web test origin allowed by CORS; repeat for more than one origin.",
    )
    args = parser.parse_args(argv)
    qwen_api_key: Optional[str] = None
    credential_source = "not_applicable"
    if args.adapter == "qwen":
        qwen_api_key, credential_source = _resolve_qwen_api_key()
    is_loopback = args.host in ("127.0.0.1", "::1", "localhost")
    if not is_loopback and (not args.tls_cert or not args.tls_key or not args.bearer_token):
        parser.error("non-loopback X01 requires --tls-cert, --tls-key, and --bearer-token")
    server = make_server(
        args.host,
        args.port,
        args.adapter,
        max_assets=args.max_assets,
        bearer_token=args.bearer_token,
        tls_cert=args.tls_cert,
        tls_key=args.tls_key,
        qwen_api_key=qwen_api_key,
        allowed_origins=tuple(args.allowed_origins or DEFAULT_WEB_TEST_ORIGINS),
        run_audit_dir=Path(args.run_audit_dir).expanduser() if args.run_audit_dir else None,
        x02_run_audit_dir=(
            Path(args.x02_run_audit_dir).expanduser() if args.x02_run_audit_dir else None
        ),
    )
    adapter = server.RequestHandlerClass.adapter
    scheme = "https" if server.diary_one_tls_enabled else "http"  # type: ignore[attr-defined]
    print(
        "Diary One staged research server listening on %s://%s:%d · adapter=%s · model=%s · ready=%s · auth=%s · credential=%s"
        % (
            scheme,
            args.host,
            args.port,
            adapter.provider,
            adapter.model,
            adapter.ready,
            bool(args.bearer_token),
            credential_source,
        ),
        flush=True,
    )
    if args.adapter == "fixture":
        print("WARNING: fixture adapter is contract-test-only and must not be treated as algorithm output.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
