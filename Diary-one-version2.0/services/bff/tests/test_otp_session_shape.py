"""ACC03 — OTP verify must return session_token for App fail-closed path."""
from __future__ import annotations

from shared.otp import issue_session_token


def test_issue_session_token_shape():
    body = issue_session_token("tester@example.com")
    assert body.get("ok") is True
    assert body.get("email") == "tester@example.com"
    assert isinstance(body.get("session_token"), str)
    assert len(str(body["session_token"])) >= 16
    assert (body.get("profile") or {}).get("email") == "tester@example.com"
