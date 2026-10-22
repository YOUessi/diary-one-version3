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


def test_refund_is_idempotent_and_never_refunds_another_submission(tmp_path):
    store = DailyQuotaStore(tmp_path / 'q.json')
    first = store.charge('email:a@b.com', 'job-one', limit=8)
    store.charge('email:a@b.com', 'job-two', limit=8)
    restored = DailyQuotaStore(tmp_path / 'q.json')
    restored.refund(first)
    restored.refund(first)
    assert restored.count_today('email:a@b.com') == 1


def test_delayed_refund_does_not_debit_next_day(tmp_path, monkeypatch):
    store = DailyQuotaStore(tmp_path / 'q.json')
    monkeypatch.setattr(store, '_day', lambda: '2026-10-21')
    first = store.charge('email:a@b.com', 'job-one', limit=8)
    monkeypatch.setattr(store, '_day', lambda: '2026-10-22')
    store.charge('email:a@b.com', 'job-two', limit=8)
    store.refund(first)
    assert store.count_today('email:a@b.com') == 1


def test_charge_receipt_survives_reopening_without_double_charge(tmp_path):
    path = tmp_path / 'q.json'
    DailyQuotaStore(path).charge('email:a@b.com', 'job-one', limit=1)
    DailyQuotaStore(path).charge('email:a@b.com', 'job-one', limit=1)
    assert DailyQuotaStore(path).count_today('email:a@b.com') == 1


def test_separate_store_instances_do_not_lose_concurrent_charges(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    start = threading.Barrier(16)
    path = tmp_path / 'q.json'
    def charge(i):
        store = DailyQuotaStore(path)
        start.wait()
        return store.charge('email:a@b.com', f'job-{i}', limit=100)
    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(charge, range(16)))
    assert DailyQuotaStore(path).count_today('email:a@b.com') == 16


def test_corrupt_quota_file_is_not_silently_reset(tmp_path):
    path = tmp_path / 'q.json'; path.write_text('{"2026-10-22":')
    with pytest.raises(OSError): DailyQuotaStore(path).consume('email:a@b.com')
    assert path.read_text() == '{"2026-10-22":'
