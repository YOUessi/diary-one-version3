"""Input identity and stable errors shared by both BFF runtimes."""
import hashlib
import json

from fastapi import HTTPException
from shared.form_fields import read_form_bytes


async def read_profile_and_fingerprint(form, manifest_bytes: bytes) -> tuple[bytes | None, str]:
    raw = await read_form_bytes(form.get("app_client_profile")) if "app_client_profile" in form else None
    try:
        profile = json.loads(raw) if raw else None
        if raw and not isinstance(profile, dict):
            raise ValueError("profile must be an object")
        canonical = json.dumps({"manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "profile": profile},
                               sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (ValueError, UnicodeError) as exc:
        raise HTTPException(422, detail={"code": "EVIDENCE_INPUT_INVALID",
            "reason": "invalid_input_profile", "retryable": False, "action": "reimport"}) from exc
    # Bind exact manifest bytes because the downstream result contract does too.
    # The validated manifest includes each frame's SHA256 and asset metadata.
    return raw or None, hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def check_revision_input(owner, caller, stored_fingerprint, fingerprint) -> None:
    owner = (owner or "").strip().lower()
    caller = (caller or "").strip().lower()
    reason = "owner_mismatch" if owner != caller else (
        "legacy_input_unverifiable" if not stored_fingerprint else "input_mismatch")
    if owner != caller or not stored_fingerprint or stored_fingerprint != fingerprint:
        raise HTTPException(409, detail={"code": "DAY_REVISION_CONFLICT", "reason": reason,
            "retryable": False, "action": "new_revision"})


def storage_unavailable() -> HTTPException:
    return HTTPException(503, detail={"code": "SUBMISSION_STORAGE_UNAVAILABLE",
        "retryable": True, "action": "retry_same_revision"})
