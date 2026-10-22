"""PRD DAT01 / AI03 — result admission before Diary publish.

Rules (PRD V0.1 §19–21):
- Only contract-valid grounded results may enter the consumer surface.
- Failures must not be packaged as finished Empty-Day filler (AI03).
- Honest NO_GROUNDED_MEMORY is allowed (DIA02: 允许少生成、允许没有).
- Mock / PIPELINE_BLOCKED must not admit when ALLOW_MOCK_PREVIEW=false.
"""
from __future__ import annotations

from typing import Any
from pathlib import Path

from shared.result_contract import validate_result_contract, CONTRACT_VERSION


# Delivery states that may surface to Diary (honest empty included separately).
_READY_STATES = frozenset(
    {
        "READY_PRIMARY_COPY",
        "READY_WITH_GROUNDED_COPY_FALLBACK",
        "READY_WITH_ITEM_BLOCKS",
        "STAGED_PREVIEW_DELIVERED",  # research / mock contract shape
    }
)


def _pipeline_version(result: dict[str, Any]) -> str | None:
    for key in ("pipeline_version", "schema_version"):
        v = result.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    trace = result.get("decision_trace")
    if isinstance(trace, dict):
        v = trace.get("pipeline_version")
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def build_publish_envelope(
    result: dict[str, Any],
    *,
    bundle_version: str | None,
    allow_mock: bool,
) -> dict[str, Any]:
    delivery = str(result.get("delivery_state") or "").strip()
    is_mock = bool(result.get("dev_lite_fallback"))
    reason = "ok"
    admit = True
    fail_job = False

    if is_mock and not allow_mock:
        admit = False
        fail_job = True
        reason = "mock_disallowed"
    elif delivery == "PIPELINE_BLOCKED":
        admit = False
        fail_job = True
        reason = "pipeline_blocked"
    elif delivery == "NO_GROUNDED_MEMORY":
        # Honest empty day — admit as empty, do not invent filler (DIA02 + AI03).
        admit = True
        fail_job = False
        reason = "no_grounded_memory"
    elif delivery and delivery not in _READY_STATES:
        admit = False
        fail_job = True
        reason = f"unsupported_delivery:{delivery}"
    elif not delivery and not is_mock:
        # Missing delivery_state on a real path — refuse guess (SYS01).
        admit = False
        fail_job = True
        reason = "missing_delivery_state"

    envelope = {
        "publish_admit": admit,
        "admit_reason": reason,
        "fail_job": fail_job,
        "delivery_state": delivery or None,
        "pipeline_version": _pipeline_version(result),
        "schema_version": result.get("schema_version"),
        "experiment": result.get("experiment"),
        "bundle_version": bundle_version,
        "bundle_manifest_sha256": result.get("bundle_manifest_sha256"),
        "session_id": result.get("session_id"),
        "result_contract_version": CONTRACT_VERSION,
        "production_ready": bool(result.get("production_ready")),
        "is_mock_fallback": is_mock,
        "prd_refs": ["SYS01", "DAT01", "AI03", "DIA02"],
    }
    return envelope


def apply_admission(
    result: dict[str, Any],
    *,
    bundle_version: str | None,
    allow_mock: bool,
    manifest_bytes: bytes | None = None,
    bundle_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Attach `_publish` envelope; return (result, envelope)."""
    envelope = build_publish_envelope(
        result, bundle_version=bundle_version, allow_mock=allow_mock
    )
    if envelope['publish_admit'] and not envelope['is_mock_fallback']:
        try:
            if manifest_bytes is None:
                raise ValueError('missing_input_manifest')
            envelope['result_contract_sha256'] = validate_result_contract(result, manifest_bytes, bundle_dir)
            envelope['input_bound'] = True
        except (ValueError, KeyError, TypeError, OSError) as error:
            envelope.update(publish_admit=False, fail_job=True, input_bound=False,
                            admit_reason='result_contract_rejected:' + str(error)[:180])
    out = dict(result)
    out["_publish"] = envelope
    return out, envelope
