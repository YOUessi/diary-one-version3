"""ACC03 OTP — shared by Dev Lite and production BFF."""
from __future__ import annotations

import asyncio
import json
import random
import secrets
import smtplib
import ssl
import time
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field


class OtpRequestBody(BaseModel):
    email: str = Field(min_length=3)


class OtpVerifyBody(BaseModel):
    email: str = Field(min_length=3)
    code: str = Field(min_length=4, max_length=12)


@dataclass(frozen=True)
class OtpMailConfig:
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_security: str = "ssl"
    otp_ttl_seconds: int = 600
    expose_otp_in_response: bool = True
    strict_smtp_required: bool = False  # Dev Lite: 503 when no SMTP and expose=false

    def smtp_configured(self) -> bool:
        return bool(self.smtp_host.strip() and self.smtp_from.strip())


def normalize_email(email: str) -> str:
    return email.strip().lower()


def normalize_code_digits(code: str) -> str:
    return "".join(c for c in code if c.isdigit())


def generate_otp_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def issue_session_token(email: str) -> dict[str, Any]:
    nickname = email.split("@")[0] or "Guest"
    return {
        "ok": True,
        "email": email,
        "session_token": secrets.token_urlsafe(24),
        "profile": {"email": email, "nickname": nickname},
    }


def send_otp_email_blocking(cfg: OtpMailConfig, to_email: str, code: str) -> None:
    if not cfg.smtp_configured():
        raise RuntimeError("smtp_not_configured")
    msg = EmailMessage()
    msg["Subject"] = "Diary One verification code"
    msg["From"] = cfg.smtp_from.strip()
    msg["To"] = to_email
    msg.set_content(
        f"Your Diary One code is: {code}\n\n"
        f"It expires in {cfg.otp_ttl_seconds // 60} minutes.\n"
        "If you did not request this, ignore this email.\n"
    )
    host = cfg.smtp_host.strip()
    port = int(cfg.smtp_port)
    user = cfg.smtp_user.strip()
    password = cfg.smtp_password
    security = (cfg.smtp_security or "ssl").lower()
    if security == "ssl":
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as smtp:
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    elif security == "starttls":
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)


class SessionRegistrar(Protocol):
    def register(self, session_token: str, email: str) -> None: ...


class OtpStore:
    def __init__(self, persist_path: Path | None = None) -> None:
        self._data: dict[str, dict[str, Any]] = {}
        self._path = persist_path
        self._lock = asyncio.Lock()
        if self._path and self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._data = {}

    def _save(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def put(self, email: str, code: str, expires_at: float) -> None:
        async with self._lock:
            self._data[email] = {"code": code, "expires_at": expires_at, "attempts": 0}
            self._save()

    async def forget(self, email: str) -> None:
        async with self._lock:
            self._data.pop(normalize_email(email), None)
            self._save()

    async def verify(
        self,
        email: str,
        digits: str,
    ) -> tuple[str, ...]:
        """Return () on success, or error detail string."""
        async with self._lock:
            entry = self._data.get(email)
            if not entry:
                return ("no_otp_requested",)
            if time.time() > float(entry["expires_at"]):
                return ("otp_expired",)
            entry["attempts"] = int(entry.get("attempts", 0)) + 1
            if entry["attempts"] > 8:
                self._save()
                return ("too_many_attempts",)
            if digits != entry["code"]:
                self._save()
                return ("invalid_code",)
            del self._data[email]
            self._save()
            return ()


class OtpService:
    def __init__(self, mail: OtpMailConfig, store: OtpStore) -> None:
        self.mail = mail
        self.store = store

    async def request(self, email: str) -> dict[str, Any]:
        email = normalize_email(email)
        code = generate_otp_code()
        expires = time.time() + self.mail.otp_ttl_seconds
        await self.store.put(email, code, expires)

        out: dict[str, Any] = {
            "ok": True,
            "email": email,
            "ttl_seconds": self.mail.otp_ttl_seconds,
        }

        if self.mail.smtp_configured():
            await asyncio.to_thread(send_otp_email_blocking, self.mail, email, code)
            out["message"] = "OTP sent by email."
            out["delivery"] = "smtp"
            if self.mail.expose_otp_in_response:
                out["dev_code"] = code
            return out

        out["message"] = "OTP issued. Configure SMTP_* for real email delivery."
        if self.mail.expose_otp_in_response:
            out["dev_code"] = code
            out["delivery"] = "response_only"
            return out

        out["delivery"] = "email_not_configured"
        if self.mail.strict_smtp_required:
            return {"_error": "smtp_required", **out}
        return out

    async def verify(
        self,
        email: str,
        code: str,
        sessions: SessionRegistrar | None = None,
    ) -> tuple[dict[str, Any] | None, str | None]:
        email = normalize_email(email)
        digits = normalize_code_digits(code)
        err = await self.store.verify(email, digits)
        if err:
            return None, err[0]
        body = issue_session_token(email)
        if sessions and body.get("session_token"):
            sessions.register(str(body["session_token"]), email)
        return body, None
