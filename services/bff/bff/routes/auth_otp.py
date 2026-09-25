"""ACC03 OTP — mirrors Dev Lite for Docker production BFF API parity.

Expo Go / internal beta: expose_otp_in_response returns dev_code.
Real SMTP is intentionally not wired until product confirms mail credentials.
"""
from __future__ import annotations

import random
import secrets
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from shared.config import settings

router = APIRouter(prefix="/v1/auth")

_otp: dict[str, dict[str, Any]] = {}
_OTP_TTL = 600
_EXPOSE = True  # flip false when SMTP is configured


class OtpRequest(BaseModel):
    email: str = Field(min_length=3)


class OtpVerify(BaseModel):
    email: str = Field(min_length=3)
    code: str = Field(min_length=4)


@router.post("/otp/request")
async def otp_request(body: OtpRequest) -> dict[str, Any]:
    email = body.email.strip().lower()
    code = f"{random.randint(0, 999999):06d}"
    _otp[email] = {
        "code": code,
        "expires_at": time.time() + _OTP_TTL,
        "attempts": 0,
    }
    out: dict[str, Any] = {
        "ok": True,
        "email": email,
        "message": "OTP issued (production BFF stub; SMTP not configured).",
        "ttl_seconds": _OTP_TTL,
    }
    if _EXPOSE or getattr(settings, "expose_otp_in_response", True):
        out["dev_code"] = code
        out["delivery"] = "response_only"
    else:
        out["delivery"] = "email_not_configured"
    return out


@router.post("/otp/verify")
async def otp_verify(body: OtpVerify) -> dict[str, Any]:
    email = body.email.strip().lower()
    digits = "".join(c for c in body.code if c.isdigit())
    entry = _otp.get(email)
    if not entry:
        raise HTTPException(status_code=400, detail="no_otp_requested")
    if time.time() > float(entry["expires_at"]):
        raise HTTPException(status_code=400, detail="otp_expired")
    entry["attempts"] = int(entry.get("attempts", 0)) + 1
    if entry["attempts"] > 8:
        raise HTTPException(status_code=429, detail="too_many_attempts")
    if digits != entry["code"]:
        raise HTTPException(status_code=400, detail="invalid_code")
    del _otp[email]
    return {
        "ok": True,
        "email": email,
        "session_token": secrets.token_urlsafe(24),
        "profile": {"email": email, "nickname": email.split("@")[0] or "Guest"},
    }
