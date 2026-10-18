"""OTP session tokens — validated as Bearer on protected routes."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class SessionStore:
    def __init__(self, persist_path: Path | None = None, ttl_seconds: int = 60 * 60 * 24 * 30) -> None:
        self._ttl = ttl_seconds
        self._path = persist_path
        self._by_token: dict[str, dict[str, Any]] = {}
        if self._path and self._path.exists():
            try:
                raw = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._by_token = {str(k): v for k, v in raw.items()}
            except json.JSONDecodeError:
                self._by_token = {}
        self._prune()

    def _save(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix('.tmp')
        tmp.write_text(
            json.dumps(self._by_token, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(self._path)

    def _prune(self) -> None:
        now = time.time()
        dead = [t for t, v in self._by_token.items() if float(v.get("expires_at", 0)) < now]
        for t in dead:
            del self._by_token[t]

    def register(self, session_token: str, email: str) -> None:
        token = session_token.strip()
        if not token:
            return
        self._prune()
        self._by_token[token] = {
            "email": email.strip().lower(),
            "expires_at": time.time() + self._ttl,
        }
        self._save()

    def resolve_email(self, session_token: str) -> str | None:
        token = session_token.strip()
        if not token:
            return None
        self._prune()
        entry = self._by_token.get(token)
        if not entry:
            return None
        if float(entry.get("expires_at", 0)) < time.time():
            del self._by_token[token]
            self._save()
            return None
        return str(entry.get("email") or "")

    def revoke_email(self, email: str) -> None:
        owner = email.strip().lower()
        previous = self._by_token
        self._by_token = {token: value for token, value in self._by_token.items()
                          if str(value.get("email") or "").strip().lower() != owner}
        try:
            self._save()
        except OSError:
            self._by_token = previous
            raise
