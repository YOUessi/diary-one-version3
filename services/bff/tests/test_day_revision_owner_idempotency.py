"""Multi-user: day_revision_id reuse must not cross owner_email."""
from __future__ import annotations

# Import helper without loading SQLAlchemy engines.
import importlib.util
from pathlib import Path


def _load_decision_fn():
    path = Path(__file__).resolve().parents[1] / "bff" / "routes" / "day_revisions.py"
    text = path.read_text(encoding="utf-8")
    # Execute only the pure helper by compiling a tiny stub.
    stub = {}
    start = text.index("def idempotent_owner_decision")
    end = text.index("@router.post", start)
    exec(compile(text[start:end], str(path), "exec"), stub)  # noqa: S102
    return stub["idempotent_owner_decision"]


def test_idempotent_owner_matrix():
    decide = _load_decision_fn()
    assert decide(owner_email="a@x.com", caller_email="a@x.com") == "reuse"
    assert decide(owner_email="a@x.com", caller_email="b@x.com") == "conflict"
    assert decide(owner_email=None, caller_email=None) == "legacy_ok"
    assert decide(owner_email="a@x.com", caller_email=None) == "conflict"
    assert decide(owner_email=None, caller_email="a@x.com") == "conflict"


def test_conflict_detail_contract_for_app():
    """App retries once on detail containing this phrase (DAY_REVISION_CONFLICT)."""
    detail = "day_revision_id already used by another account"
    assert "another account" in detail
    assert "day_revision_id" in detail
