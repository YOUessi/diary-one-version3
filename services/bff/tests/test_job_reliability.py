"""Persistence and access-control regressions using isolated synthetic jobs."""
import asyncio
import json
import os
from unittest.mock import AsyncMock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from dev_lite import app as lite
from dev_lite import job_store
from shared.quota import CallerIdentity


def meta(job_id="job", **changes):
    return dict(job_id=job_id, day_revision_id="revision", status="succeeded",
                message="Complete", owner_email="owner@example.invalid",
                result={"marker": "synthetic-only"}, **changes)


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(lite, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(lite, "_jobs", {})
    lite.app.dependency_overrides[lite.require_token] = lambda: CallerIdentity(
        "email:owner@example.invalid", "owner@example.invalid", "session")
    yield TestClient(lite.app, raise_server_exceptions=False), tmp_path
    lite.app.dependency_overrides.clear()


@pytest.mark.parametrize("owner", [None, "", "other@example.invalid"])
def test_session_cannot_read_unowned_or_foreign_job(client, owner):
    http, root = client
    item = meta(); item["owner_email"] = owner
    job_store.write_job_meta(root / "job", item)
    assert http.get("/v1/jobs/job").status_code == 404


def test_owner_can_read_result_after_memory_restart(client):
    http, root = client
    job_store.write_job_meta(root / "job", meta())
    result = http.get("/v1/jobs/job")
    assert result.status_code == 200
    assert result.json()["result"] == {"marker": "synthetic-only"}


@pytest.mark.parametrize("raw", [None, '{"owner_email":', '[]', '{"job_id":"wrong"}',
    json.dumps(dict(meta(), submitted_at_ns='corrupt')), json.dumps(dict(meta(), status=[]))])
def test_bad_meta_never_turns_result_file_into_success(client, raw):
    http, root = client
    directory = root / "job"; directory.mkdir()
    if raw is not None: (directory / "job_meta.json").write_text(raw)
    (directory / "result.json").write_text('{"marker":"synthetic-only"}')
    jobs, index = job_store.reload_jobs_from_disk(root, root.parent)
    assert "job" not in jobs and "revision" not in index
    assert http.get("/v1/jobs/job").status_code == 404


@pytest.mark.parametrize("target", ["meta", "index"])
def test_interrupted_atomic_write_preserves_previous_json(monkeypatch, tmp_path, target):
    if target == "meta":
        path = tmp_path / "job_meta.json"
        before = meta(); after = dict(before, status="failed")
        write = lambda value: job_store.write_job_meta(tmp_path, value)
    else:
        path = tmp_path / job_store.INDEX_NAME
        before = {"revision": "job"}; after = {"revision": "new"}
        write = lambda value: job_store.save_revision_index(tmp_path, value)
    write(before)
    replace = os.replace
    def fail_replace(source, dest):
        if Path(dest) == path: raise OSError("injected disk failure")
        return replace(source, dest)
    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError): write(after)
    assert json.loads(path.read_text()) == before
    assert list(tmp_path.iterdir()) == [path]


def test_restart_rebuilds_index_from_verified_meta_not_stale_index(tmp_path):
    jobs_dir = tmp_path / "jobs"
    job_store.write_job_meta(jobs_dir / "job", meta())
    job_store.save_revision_index(tmp_path, {"revision": "missing", "deleted": "missing"})
    jobs, index = job_store.reload_jobs_from_disk(jobs_dir, tmp_path)
    assert list(jobs) == ["job"]
    assert index == {"revision": "job"}


def test_late_old_job_update_does_not_override_newer_submission_on_restart(tmp_path):
    jobs = tmp_path / 'jobs'
    job_store.write_job_meta(jobs / 'new', meta('new', submitted_at_ns=20))
    job_store.write_job_meta(jobs / 'old', meta('old', submitted_at_ns=10))
    _, index = job_store.reload_jobs_from_disk(jobs, tmp_path)
    assert index == {'revision': 'new'}


def test_saved_result_survives_terminal_meta_failure_without_another_model_call(monkeypatch, tmp_path):
    from test_product_result_contract import fixture
    directory = tmp_path / 'jobs' / 'job'; directory.mkdir(parents=True)
    result, manifest, raw = fixture(directory, 'photo_v07')
    (directory / 'bundle.json').write_bytes(raw)
    job = dict(meta(), status='pending', result=None, bundle_version=manifest['bundle_version'])
    job_store.write_job_meta(directory, job)
    monkeypatch.setattr(lite, 'DATA', tmp_path)
    monkeypatch.setattr(lite, '_jobs', {'job': job})
    monkeypatch.setattr(lite, '_revision_index', {})
    monkeypatch.setattr(lite.settings, 'allow_mock_preview', False)
    cloud = AsyncMock(return_value=result)
    monkeypatch.setattr(lite, '_call_x02', cloud)
    write = lite.write_job_meta
    def fail_terminal(path, item):
        if item['status'] in {'succeeded', 'failed'}: raise OSError('terminal metadata unavailable')
        write(path, item)
    monkeypatch.setattr(lite, 'write_job_meta', fail_terminal)
    with pytest.raises(OSError): asyncio.run(lite._process_job_inner('job', directory))
    assert job['status'] == 'processing'  # No in-memory success before durable commit.
    assert json.loads((directory / 'result.json').read_text())['chapters'] == result['chapters']
    monkeypatch.setattr(lite, 'write_job_meta', write)
    restored, index = job_store.reload_jobs_from_disk(tmp_path / 'jobs', tmp_path)
    monkeypatch.setattr(lite, '_jobs', restored)
    monkeypatch.setattr(lite, '_revision_index', index)
    asyncio.run(lite._process_job_inner('job', directory))
    assert lite._jobs['job']['status'] == 'succeeded'
    assert lite._jobs['job']['result']['chapters'] == result['chapters']
    assert cloud.await_count == 1
