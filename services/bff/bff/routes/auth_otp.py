"""ACC03 OTP — production BFF (shared logic with Dev Lite)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from shared.config import settings
from shared.otp import OtpMailConfig, OtpRequestBody, OtpService, OtpStore, OtpVerifyBody
from shared.oauth import OAuthBody, exchange_oauth
from shared.sessions import SessionStore

router = APIRouter(prefix="/v1/auth")

_SESSIONS_PATH = Path(__file__).resolve().parents[2] / "data" / "sessions.json"
_sessions = SessionStore(_SESSIONS_PATH)
_smtp_ready = bool(settings.smtp_host.strip() and settings.smtp_from.strip())
_otp = OtpService(
    OtpMailConfig(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password=settings.smtp_password,
        smtp_from=settings.smtp_from,
        smtp_security=settings.smtp_security,
        otp_ttl_seconds=settings.otp_ttl_seconds,
        expose_otp_in_response=settings.expose_otp_in_response,
        # When SMTP is configured, require send success (no silent local-only).
        strict_smtp_required=_smtp_ready,
    ),
    OtpStore(),
)


def session_store() -> SessionStore:
    return _sessions


@router.post("/otp/request")
async def otp_request(body: OtpRequestBody) -> dict[str, Any]:
    try:
        out = await _otp.request(body.email)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"smtp_send_failed:{e}") from e
    if out.get("_error") == "smtp_required":
        raise HTTPException(
            status_code=503,
            detail="smtp_required: set SMTP_HOST/SMTP_FROM or EXPOSE_OTP_IN_RESPONSE=true",
        )
    return out


@router.post("/otp/verify")
async def otp_verify(body: OtpVerifyBody) -> dict[str, Any]:
    result, err = await _otp.verify(body.email, body.code, sessions=_sessions)
    if err:
        status = 429 if err == "too_many_attempts" else 400
        raise HTTPException(status_code=status, detail=err)
    return result or {}


@router.post("/oauth")
async def oauth_login(body: OAuthBody) -> dict[str, Any]:
    return await exchange_oauth(body, _sessions)
