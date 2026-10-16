"""Unit tests for require_api_bearer."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from shared.api_auth import require_api_bearer
from shared.sessions import SessionStore


def test_open_mode_no_header_when_empty_api_token() -> None:
    require_api_bearer(None, "", None)


def test_rejects_garbage_bearer_when_empty_api_token() -> None:
    with pytest.raises(HTTPException) as ei:
        require_api_bearer("Bearer not-a-real-session", "", None)
    assert ei.value.status_code == 401


def test_accepts_static_api_token() -> None:
    require_api_bearer("Bearer lab-token", "lab-token", None)


def test_accepts_session_token(tmp_path) -> None:  # type: ignore[no-untyped-def]
    store = SessionStore(tmp_path / "sessions.json")
    store.register("sess-1", "a@b.com")
    require_api_bearer("Bearer sess-1", "lab-token", store)


def test_rejects_wrong_token() -> None:
    with pytest.raises(HTTPException) as ei:
        require_api_bearer("Bearer wrong", "lab-token", None)
    assert ei.value.status_code == 401
