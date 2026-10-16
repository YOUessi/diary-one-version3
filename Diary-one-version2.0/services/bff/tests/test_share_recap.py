"""Unit tests for Daily Recap render (no real ffmpeg required)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bff.routes import share_recap as share_recap_mod
from bff.routes.share_recap import router as bff_router


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(share_recap_mod, "DATA", tmp_path / "recap_videos")
    app = FastAPI()
    app.include_router(bff_router)
    # Bypass auth dependency for route body tests
    app.dependency_overrides[share_recap_mod.require_bearer] = lambda: None
    return TestClient(app)


def test_missing_slide_count_returns_400(client: TestClient) -> None:
    with patch.object(share_recap_mod, "ffmpeg_available", return_value=True):
        res = client.post("/v1/share/daily-recap/render", data={})
    assert res.status_code == 400
    assert "slide_count" in res.json()["detail"]


def test_no_ffmpeg_returns_503(client: TestClient) -> None:
    with patch.object(share_recap_mod, "ffmpeg_available", return_value=False):
        res = client.post(
            "/v1/share/daily-recap/render",
            data={"slide_count": "1"},
            files={"slide_0": ("a.jpg", b"\xff\xd8\xff", "image/jpeg")},
        )
    assert res.status_code == 503


def test_success_returns_mp4(client: TestClient, tmp_path: Path) -> None:
    def fake_render(paths, out, **_kwargs):  # type: ignore[no-untyped-def]
        Path(out).write_bytes(b"fake-mp4-bytes")

    with (
        patch.object(share_recap_mod, "ffmpeg_available", return_value=True),
        patch.object(share_recap_mod, "render_slideshow_mp4", side_effect=fake_render),
    ):
        res = client.post(
            "/v1/share/daily-recap/render",
            data={"slide_count": "1", "fps": "24", "slide_duration_sec": "2.5"},
            files={"slide_0": ("a.jpg", b"\xff\xd8\xff\xd9", "image/jpeg")},
        )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("video/mp4")
    assert res.content == b"fake-mp4-bytes"


def test_unauthorized_without_override() -> None:
    app = FastAPI()
    app.include_router(bff_router)
    client = TestClient(app)
    with patch.object(share_recap_mod, "ffmpeg_available", return_value=True):
        res = client.post(
            "/v1/share/daily-recap/render",
            data={"slide_count": "1"},
            files={"slide_0": ("a.jpg", b"abc", "image/jpeg")},
        )
    assert res.status_code == 401
