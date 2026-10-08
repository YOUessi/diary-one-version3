"""Apple / Google identity token → Diary One session (same shape as OTP verify)."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, Field

from shared.otp import issue_session_token
from shared.sessions import SessionStore

APPLE_AUDIENCES = (
    "host.exp.Exponent",
    "com.nexleap.diaryone.dev",
    "com.nexleap.diaryone",
)


class OAuthBody(BaseModel):
    provider: str = Field(min_length=3)
    identity_token: str = Field(min_length=20)


async def exchange_oauth(body: OAuthBody, sessions: SessionStore) -> dict[str, Any]:
    provider = body.provider.strip().lower()
    token = body.identity_token.strip()
    try:
        if provider == "google":
            email = await _google_email(token)
        elif provider == "apple":
            email = await _apple_email(token)
        else:
            raise HTTPException(status_code=400, detail="unsupported_provider")
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail=f"oauth_verify_failed:{exc}") from exc
    issued = issue_session_token(email)
    sessions.register(str(issued["session_token"]), email)
    issued["provider"] = provider
    return issued


async def _google_email(id_token: str) -> str:
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="google_token_rejected")
    data = r.json()
    email = str(data.get("email") or "").strip().lower()
    verified = str(data.get("email_verified")).lower() in ("true", "1")
    if not email or not verified:
        raise HTTPException(status_code=401, detail="google_email_unverified")
    return email


async def _apple_email(identity_token: str) -> str:
    import jwt
    from jwt import PyJWKClient

    jwks = PyJWKClient("https://appleid.apple.com/auth/keys")
    signing_key = jwks.get_signing_key_from_jwt(identity_token)
    claims = jwt.decode(
        identity_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=APPLE_AUDIENCES,
        options={"verify_aud": True},
    )
    email = str(claims.get("email") or "").strip().lower()
    sub = str(claims.get("sub") or "").strip()
    if not email and sub:
        email = f"apple.{sub[:16]}@privaterelay.appleid.com"
    if not email:
        raise HTTPException(status_code=401, detail="apple_email_missing")
    return email
