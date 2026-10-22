"""Per-caller daily day-revision quota for multi-user beta."""
from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from shared.api_auth import parse_bearer
from shared.sessions import SessionStore


def daily_limit() -> int:
    raw = os.environ.get("DAY_REVISION_DAILY_LIMIT", "8").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 8
    return max(0, n)


def max_inflight_per_user() -> int:
    raw = os.environ.get("DAY_REVISION_MAX_INFLIGHT", "2").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 2
    return max(1, n)


def worker_max_concurrent() -> int:
    raw = os.environ.get("WORKER_MAX_CONCURRENT", "1").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 1
    return max(1, min(n, 8))


@dataclass(frozen=True)
class CallerIdentity:
    """Stable quota key + optional email for job ownership."""

    key: str
    email: Optional[str]
    kind: str  # session | api_token | open


def resolve_caller(
    authorization: str | None,
    api_token: str,
    sessions: SessionStore | None,
) -> CallerIdentity:
    token = parse_bearer(authorization)
    if token and sessions:
        email = sessions.resolve_email(token)
        if email:
            return CallerIdentity(key=f"email:{email}", email=email, kind="session")
    if token and api_token and token == api_token:
        return CallerIdentity(key="lab:api_token", email=None, kind="api_token")
    if not token and not api_token:
        return CallerIdentity(key="lab:open", email=None, kind="open")
    # Authorized path shouldn't hit here after require_bearer
    return CallerIdentity(key="lab:unknown", email=None, kind="open")


class DailyQuotaStore:
    """JSON file counter: { day: { key: count } }."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()

    def _day(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _load(self) -> dict:
        if not self._path.exists():
            return {}
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, data: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self._path)

    def count_today(self, key: str) -> int:
        with self._lock:
            data = self._load()
            day = self._day()
            bucket = data.get(day) or {}
            return int(bucket.get(key, 0))

    def delete_caller(self, key: str) -> None:
        with self._lock:
            data = self._load()
            for bucket in data.values():
                if isinstance(bucket, dict):
                    bucket.pop(key, None)
            self._save(data)

    def consume(self, key: str, *, limit: int | None = None) -> int:
        """Increment and return new count. Raises HTTP 429 if over limit."""
        lim = daily_limit() if limit is None else limit
        if lim <= 0:
            return 0
        with self._lock:
            data = self._load()
            day = self._day()
            # Drop old days
            data = {day: data.get(day) or {}}
            bucket = data[day]
            cur = int(bucket.get(key, 0))
            if cur >= lim:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "day_revision_quota_exceeded",
                        "message": f"Daily upload limit reached ({lim}). Try again tomorrow.",
                        "limit": lim,
                        "used": cur,
                        "reset": "UTC midnight",
                    },
                )
            cur += 1
            bucket[key] = cur
            data[day] = bucket
            self._save(data)
            return cur


# Process-local default for Dev Lite / single-node BFF
_DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "day_revision_quota.json"
_store: DailyQuotaStore | None = None


def quota_store(path: Path | None = None) -> DailyQuotaStore:
    global _store
    if path is not None:
        return DailyQuotaStore(path)
    if _store is None:
        env_path = os.environ.get("DAY_REVISION_QUOTA_PATH", "").strip()
        _store = DailyQuotaStore(Path(env_path) if env_path else _DEFAULT_PATH)
    return _store


def assert_quota(
    caller: CallerIdentity,
    store: DailyQuotaStore | None = None,
    *,
    limit: int | None = None,
) -> int:
    return (store or quota_store()).consume(caller.key, limit=limit)


def assert_inflight(current: int, *, limit: int | None = None) -> None:
    lim = max_inflight_per_user() if limit is None else limit
    if current < lim:
        return
    raise HTTPException(
        status_code=429,
        detail={
            "error": "day_revision_inflight_limit",
            "message": f"Too many jobs still processing ({lim}). Wait for one to finish.",
            "limit": lim,
            "inflight": current,
        },
    )
