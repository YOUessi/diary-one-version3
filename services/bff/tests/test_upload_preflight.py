"""Real multipart routes with real image bytes; no live DB, storage or model."""
import asyncio
import hashlib
import io
import json
import shutil
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from bff.routes import day_revisions
from bff.auth import require_bearer
from shared.db import get_async_session
from shared.models import JobStatus
from shared.quota import CallerIdentity, DailyQuotaStore
from dev_lite import app as lite
from worker import processor


def upload_case(kind="valid"):
    image = io.BytesIO()
    Image.new("RGB", (768, 1024), "white").save(image, format="PNG" if kind == "png" else "JPEG")
    content = image.getvalue()
    if kind == "truncated": content = content[:len(content) // 2]
    frame = {"frame_id": "photo-f0", "relative_path": "frames/photo-f0.jpg", "width": 768,
             "height": 432 if kind == "dimensions" else 1024,
             "sha256": hashlib.sha256(content).hexdigest()}
    manifest = {"bundle_version": "DIARY_ONE_APP_LIBRARY_BUNDLE_V04",
                "session": {"session_id": "preflight"},
                "assets": [{"asset_id": "photo", "media_kind": "PHOTO", "frames": [frame]}]}
    if kind == "hash": frame["sha256"] = "0" * 64
    if kind == "path": frame["relative_path"] = "../../outside.jpg"
    if kind == "null_path": frame["relative_path"] = "frames/bad\x00.jpg"
    if kind == "identity": frame["frame_id"] = "../outside"
    if kind == "duplicate_frame": manifest["assets"][0]["frames"].append(dict(frame))
    if kind == "no_frames": manifest["assets"][0]["frames"] = []
    raw = json.dumps([] if kind == "shape" else manifest).encode()
    if kind == "invalid_json": raw = b"not json"
    files = [("manifest", (None, raw, "application/json")), ("day_revision_id", (None, "revision")),
             (frame["frame_id"], ("photo.jpg", content, "image/jpeg"))]
    if kind == "missing": files.pop()
    if kind == "extra": files.append(("extra", ("extra.jpg", content, "image/jpeg")))
    if kind == "duplicate_part": files.append(files[-1])
    if kind == "duplicate_manifest": files.append(files[0])
    return raw, content, files


@pytest.fixture(params=["lite", "docker"])
def api(request, monkeypatch, tmp_path):
    caller = CallerIdentity("lab:api_token", None, "api_token")
    quota = DailyQuotaStore(tmp_path / "quota.json")
    storage = Mock()
    session = SimpleNamespace(scalar=AsyncMock(return_value=None), add=Mock(), commit=AsyncMock())
    if request.param == "lite":
        monkeypatch.setattr(lite, "DATA", tmp_path)
        monkeypatch.setattr(lite, "JOBS_DIR", tmp_path / "jobs")
        monkeypatch.setattr(lite, "_jobs", {})
        monkeypatch.setattr(lite, "_revision_index", {})
        monkeypatch.setattr(lite, "_quota", quota)
        monkeypatch.setattr(lite, "_process_job", AsyncMock())
        app = lite.app
        app.dependency_overrides[lite.require_token] = lambda: caller
    else:
        app = FastAPI()
        app.include_router(day_revisions.router)
        app.dependency_overrides[require_bearer] = lambda: caller
        app.dependency_overrides[get_async_session] = lambda: session
        monkeypatch.setattr(day_revisions, "quota_store", lambda: quota)
        monkeypatch.setattr(day_revisions, "minio_client", lambda: object())
        monkeypatch.setattr(day_revisions, "upload_bytes", storage)
        monkeypatch.setattr(day_revisions, "notify_worker", Mock())
    yield SimpleNamespace(client=TestClient(app, raise_server_exceptions=False), quota=quota,
                          storage=storage, session=session, root=tmp_path, kind=request.param)
    app.dependency_overrides.clear()


@pytest.mark.parametrize("kind", ["dimensions", "png", "hash", "truncated", "missing", "extra",
    "path", "null_path", "identity", "duplicate_frame", "duplicate_part", "duplicate_manifest", "shape", "no_frames", "invalid_json"])
def test_invalid_upload_is_rejected_before_quota_storage_or_job(api, kind):
    response = api.client.post("/v1/day-revisions", files=upload_case(kind)[2])
    assert response.status_code == 422, (kind, response.status_code, response.text)
    detail = response.json()["detail"]
    assert detail["code"] == "EVIDENCE_INPUT_INVALID"
    assert detail["retryable"] is False and detail["action"] == "reimport"
    assert api.quota.count_today("lab:api_token") == 0
    assert not (api.root / "jobs").exists()
    api.storage.assert_not_called()
    api.session.add.assert_not_called()
    if api.kind == "lite":
        assert lite._jobs == {}
        lite._process_job.assert_not_called()


def test_valid_upload_queues_the_validated_original_bytes(api):
    raw, content, files = upload_case()
    response = api.client.post("/v1/day-revisions", files=files)
    assert response.status_code == 200, response.text
    assert response.json()["job_id"] and response.json()["status"] == "pending"
    assert api.quota.count_today("lab:api_token") == 1
    if api.kind == "lite":
        directory = api.root / "jobs" / response.json()["job_id"]
        assert (directory / "bundle.json").read_bytes() == raw
        assert (directory / "frames/photo-f0.jpg").read_bytes() == content
    else:
        written = {call.args[1].split("/", 2)[2]: call.args[2] for call in api.storage.call_args_list}
        assert written == {"bundle.json": raw, "frames/photo-f0.jpg": content}
        api.session.commit.assert_awaited_once()


@pytest.mark.parametrize("runtime", ["lite", "docker"])
@pytest.mark.parametrize("allow_mock", [False, True])
@pytest.mark.parametrize("missing", [None, "manifest", "frame"])
def test_recovered_bad_evidence_never_calls_model_or_becomes_mock_success(monkeypatch, tmp_path, runtime, allow_mock, missing):
    raw, content, _ = upload_case("dimensions")
    (tmp_path / "bundle.json").write_bytes(raw)
    (tmp_path / "frames").mkdir()
    (tmp_path / "frames/photo-f0.jpg").write_bytes(content)
    if missing == "manifest": (tmp_path / "bundle.json").unlink()
    if missing == "frame": (tmp_path / "frames/photo-f0.jpg").unlink()
    cloud = AsyncMock(return_value={})
    if runtime == "lite":
        job = {"job_id": "job", "status": "pending", "bundle_version": "DIARY_ONE_APP_LIBRARY_BUNDLE_V04"}
        monkeypatch.setattr(lite, "_jobs", {"job": job})
        monkeypatch.setattr(lite, "_call_x02", cloud)
        monkeypatch.setattr(lite.settings, "allow_mock_preview", allow_mock)
        asyncio.run(lite._process_job_inner("job", tmp_path))
        assert job["status"] == "failed"
        assert job["error"].startswith("EVIDENCE_INPUT_INVALID:")
    else:
        job = SimpleNamespace(id=uuid.uuid4(), status=JobStatus.pending, updated_at=None,
                              object_prefix="jobs/job/", bundle_version="DIARY_ONE_APP_LIBRARY_BUNDLE_V04")
        session = Mock(); session.scalar.return_value = job
        monkeypatch.setattr(processor, "SyncSessionLocal", lambda: session)
        monkeypatch.setattr(processor, "minio_client", lambda: object())
        def download(client, prefix, dest): shutil.copytree(tmp_path, dest, dirs_exist_ok=True)
        monkeypatch.setattr(processor, "download_to_dir", download)
        monkeypatch.setattr(processor, "run_x02_preview", cloud)
        monkeypatch.setattr(processor.settings, "allow_mock_preview", allow_mock)
        processor.process_job_sync(str(job.id))
        assert job.status == JobStatus.failed
        assert job.error.startswith("EVIDENCE_INPUT_INVALID:")
    cloud.assert_not_called()
