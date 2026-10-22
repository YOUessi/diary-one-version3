"""Unit tests for daily day-revision quota."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from shared.quota import DailyQuotaStore, assert_inflight, resolve_caller
from shared.sessions import SessionStore


def test_daily_quota_blocks_over_limit(tmp_path) -> None:  # type: ignore[no-untyped-def]
    store = DailyQuotaStore(tmp_path / "q.json")
    key = "email:a@b.com"
    assert store.consume(key, limit=2) == 1
    assert store.consume(key, limit=2) == 2
    with pytest.raises(HTTPException) as ei:
        store.consume(key, limit=2)
    assert ei.value.status_code == 429
    detail = ei.value.detail
    assert isinstance(detail, dict)
    assert detail["error"] == "day_revision_quota_exceeded"


def test_quota_unlimited_when_limit_zero(tmp_path) -> None:  # type: ignore[no-untyped-def]
    store = DailyQuotaStore(tmp_path / "q.json")
    assert store.consume("lab:api_token", limit=0) == 0


def test_assert_inflight() -> None:
    assert_inflight(1, limit=2)
    with pytest.raises(HTTPException) as ei:
        assert_inflight(2, limit=2)
    assert ei.value.status_code == 429


def test_resolve_caller_session(tmp_path) -> None:  # type: ignore[no-untyped-def]
    sessions = SessionStore(tmp_path / "s.json")
    sessions.register("tok", "User@Example.com")
    ident = resolve_caller("Bearer tok", "lab", sessions)
    assert ident.email == "user@example.com"
    assert ident.key == "email:user@example.com"
    assert ident.kind == "session"


def test_resolve_caller_api_token() -> None:
    ident = resolve_caller("Bearer lab", "lab", None)
    assert ident.key == "lab:api_token"
    assert ident.email is None
