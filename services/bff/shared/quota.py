"""Per-caller daily day-revision quota for multi-user beta."""
from __future__ import annotations

import json
import os
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from shared.api_auth import parse_bearer
from shared.sessions import SessionStore
from shared.atomic_file import write_json_atomic

try:
    import fcntl
except ImportError:  # Windows development fallback; production BFF runs on Linux.
    fcntl = None


@dataclass(frozen=True)
class QuotaCharge:
    day: str
    key: str
    charge_id: str
    used: int


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

    @contextmanager
    def _locked(self):
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.with_suffix('.lock').open('a+b') as lock_file:
                if fcntl is not None: fcntl.flock(lock_file, fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    if fcntl is not None: fcntl.flock(lock_file, fcntl.LOCK_UN)

    def _load(self) -> dict:
        if not self._path.exists():
            return {}
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or any(not isinstance(bucket, dict) for bucket in raw.values()):
                raise ValueError("invalid quota snapshot")
            return raw
        except (OSError, ValueError) as exc:
            raise OSError("Quota snapshot is unreadable; refusing to reset usage") from exc

    def _save(self, data: dict) -> None:
        write_json_atomic(self._path, data)

    def count_today(self, key: str) -> int:
        with self._locked():
            data = self._load()
            day = self._day()
            bucket = data.get(day) or {}
            return int(bucket.get(key, 0))

    def delete_caller(self, key: str) -> None:
        with self._locked():
            data = self._load()
            for bucket in data.values():
                if isinstance(bucket, dict):
                    bucket.pop(key, None)
                    charges = bucket.get("_charges", {})
                    for charge_id in list(charges):
                        if charges[charge_id] == key: charges.pop(charge_id)
            self._save(data)

    def consume(self, key: str, *, limit: int | None = None) -> int:
        """Increment and return new count. Raises HTTP 429 if over limit."""
        return self.charge(key, str(uuid.uuid4()), limit=limit).used

    def charge(self, key: str, charge_id: str, *, limit: int | None = None) -> QuotaCharge:
        """Persist a charge receipt so compensation cannot refund a different request."""
        lim = daily_limit() if limit is None else limit
        if lim <= 0:
            return QuotaCharge(self._day(), key, charge_id, 0)
        with self._locked():
            data = self._load()
            day = self._day()
            # Drop old days
            data = {day: data.get(day) or {}}
            bucket = data[day]
            cur = int(bucket.get(key, 0))
            charges = bucket.setdefault("_charges", {})
            if charge_id in charges:
                if charges[charge_id] != key: raise ValueError("quota receipt owner mismatch")
                return QuotaCharge(day, key, charge_id, cur)
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
            charges[charge_id] = key
            data[day] = bucket
            self._save(data)
            return QuotaCharge(day, key, charge_id, cur)

    def refund(self, charge: QuotaCharge) -> None:
        if charge.used == 0:
            return
        with self._locked():
            data = self._load()
            bucket = data.get(charge.day, {})
            charges = bucket.get("_charges", {})
            if charges.get(charge.charge_id) != charge.key:
                return
            charges.pop(charge.charge_id)
            bucket[charge.key] = max(0, int(bucket.get(charge.key, 0)) - 1)
            self._save(data)

    def refund_job(self, key: str, charge_id: str) -> None:
        """Reconcile an interrupted unpublished job, even across UTC midnight."""
        with self._locked():
            data = self._load()
            changed = False
            for bucket in data.values():
                charges = bucket.get('_charges', {})
                if charges.get(charge_id) == key:
                    charges.pop(charge_id)
                    bucket[key] = max(0, int(bucket.get(key, 0)) - 1)
                    changed = True
            if changed: self._save(data)


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
