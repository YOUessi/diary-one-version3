"""Same-input retries and persistence failures at real multipart route boundaries."""
import json
from pathlib import Path

import pytest

from dev_lite import app as lite
from shared.models import JobStatus
from test_upload_preflight import api, upload_case


def files(profile=None, change=None):
    raw, content, parts = upload_case()
    manifest = json.loads(raw)
    if change: manifest["session"]["session_id"] = change
    parts[0] = ("manifest", (None, json.dumps(manifest), "application/json"))
    if profile is not None:
        parts.append(("app_client_profile", (None, profile, "application/json")))
    return parts


def submit(api, **kw):
    return api.client.post("/v1/day-revisions", files=files(**kw))


def existing(api, **kw):
    response = submit(api, **kw)
    assert response.status_code == 200, response.text
    jid = response.json()["job_id"]
    if api.kind == "docker":
        api.session.scalar.return_value = api.committed[-1]
    return jid


def test_same_input_reuses_job_without_new_charge(api):
    jid = existing(api, profile='{"language":"zh","style":"short"}')
    response = submit(api, profile='{ "style": "short", "language": "zh" }')
    assert response.status_code == 200, response.text
    assert response.json()["job_id"] == jid and response.json()["idempotent"]
    assert api.quota.count_today("lab:api_token") == 1


def test_manifest_byte_change_conflicts_because_result_contract_binds_raw_hash(api):
    existing(api)
    parts = files()
    parts[0] = ('manifest', (None, parts[0][1][1] + '\n', 'application/json'))
    response = api.client.post('/v1/day-revisions', files=parts)
    assert response.status_code == 409
    assert api.quota.count_today('lab:api_token') == 1


@pytest.mark.parametrize("change", ["manifest", "profile", "legacy"])
@pytest.mark.parametrize("failed", [False, True])
def test_same_revision_rejects_changed_or_unverifiable_input(api, change, failed):
    jid = existing(api, profile='{"language":"zh"}')
    job = lite._jobs[jid] if api.kind == "lite" else api.committed[-1]
    if api.kind == "lite":
        if failed: job["status"] = "failed"
        if change == "legacy": job.pop("input_fingerprint", None)
    else:
        if failed: job.status = JobStatus.failed
        if change == "legacy": job.input_fingerprint = None
    response = submit(api, profile='{"language":"en"}' if change == "profile" else '{"language":"zh"}',
                      change="other" if change == "manifest" else None)
    assert response.status_code == 409, response.text
    assert api.quota.count_today("lab:api_token") == 1


@pytest.mark.parametrize("profile", ['[]', '{', '{"score":NaN}'])
def test_invalid_profile_rejected_before_storage_and_charge(api, profile):
    response = submit(api, profile=profile)
    assert response.status_code == 422
    assert api.quota.count_today("lab:api_token") == 0
    assert not api.objects and not (api.root / "jobs").exists()


def test_frame_storage_failure_refunds_charge_and_removes_partial_bundle(api, monkeypatch):
    if api.kind == "lite":
        original = Path.write_bytes
        def failing_write(path, data):
            if path.suffix == ".jpg": raise OSError("injected storage full")
            return original(path, data)
        monkeypatch.setattr(Path, "write_bytes", failing_write)
    else:
        write = api.storage.side_effect
        def failing_write(client, name, data, content_type):
            if name.endswith(".jpg"): raise OSError("injected storage full")
            return write(client, name, data, content_type)
        api.storage.side_effect = failing_write
    response = submit(api)
    assert response.status_code == 503, response.text
    assert api.quota.count_today("lab:api_token") == 0
    assert not api.objects
    assert not list((api.root / "jobs").glob("*/bundle.json"))
    if api.kind == "lite": assert not lite._jobs and not lite._revision_index
    else: assert not api.committed


def test_metadata_or_db_failure_refunds_and_cleans_files(api, monkeypatch):
    if api.kind == "lite":
        def fail(*args): raise OSError("injected metadata failure")
        monkeypatch.setattr(lite, "write_job_meta", fail)
    else:
        api.session.commit.side_effect = OSError("injected DB failure")
    response = submit(api)
    assert response.status_code == 503
    assert api.quota.count_today("lab:api_token") == 0
    assert not api.objects and not list((api.root / "jobs").glob("*/bundle.json"))
    if api.kind == "lite": assert not lite._jobs and not lite._revision_index


def test_index_cache_failure_does_not_lose_a_committed_job(api, monkeypatch):
    if api.kind != "lite": pytest.skip("Lite has a derived disk index")
    def fail(*args): raise OSError("injected index cache failure")
    monkeypatch.setattr(lite, "save_revision_index", fail)
    response = submit(api)
    assert response.status_code == 200, response.text
    jobs, index = lite.reload_jobs_from_disk(api.root / "jobs", api.root)
    jid = response.json()["job_id"]
    assert jobs[jid]["status"] == "pending" and index["revision"] == jid


def test_db_commit_ack_lost_preserves_accepted_job_and_evidence(api):
    if api.kind != "docker": pytest.skip("Postgres commit acknowledgement")
    commit = api.session.commit.side_effect
    def lost_ack():
        commit()
        raise ConnectionError("commit reply lost")
    api.session.commit.side_effect = lost_ack
    response = submit(api)
    assert response.status_code == 200, response.text
    assert str(api.committed[0].id) == response.json()["job_id"]
    assert len(api.objects) == 2 and api.quota.count_today("lab:api_token") == 1


def test_unknown_commit_outcome_keeps_evidence_and_charge_for_reconciliation(api):
    if api.kind != "docker": pytest.skip("Postgres commit acknowledgement")
    api.session.commit.side_effect = ConnectionError("connection lost")
    api.session.get.side_effect = ConnectionError("database still unavailable")
    response = submit(api)
    assert response.status_code == 503
    assert len(api.objects) == 2 and api.quota.count_today("lab:api_token") == 1


def test_atomic_job_publication_failure_refunds_once(api, monkeypatch):
    if api.kind != "lite": pytest.skip("Lite directory publication")
    original = Path.rename
    def fail(path, dest):
        if path.parent.name == 'submission_staging': raise OSError('publish failed')
        return original(path, dest)
    monkeypatch.setattr(Path, 'rename', fail)
    assert submit(api).status_code == 503
    assert api.quota.count_today('lab:api_token') == 0
    assert not lite._jobs and not lite._revision_index


@pytest.mark.parametrize('charged', [False, True])
def test_restart_recovers_charge_for_unpublished_staging_job(api, charged):
    if api.kind != 'lite': pytest.skip('Lite directory publication')
    staged = api.root / 'submission_staging' / 'interrupted-job'
    lite.write_job_meta(staged, dict(job_id='interrupted-job', day_revision_id='old', status='pending',
        message='queued', owner_email=None, quota_key='lab:api_token'))
    if charged: api.quota.charge('lab:api_token', 'interrupted-job', limit=8)
    lite._recover_staging_submissions()
    lite._recover_staging_submissions()
    assert api.quota.count_today('lab:api_token') == 0
    assert not staged.exists() and not lite._jobs


def test_refund_write_failure_preserves_recovery_evidence(api, monkeypatch):
    def failed_refund(charge): raise OSError('quota disk unavailable')
    monkeypatch.setattr(api.quota, 'refund', failed_refund)
    if api.kind == 'lite':
        original = Path.rename
        def failed_publish(path, dest):
            if path.parent.name == 'submission_staging': raise OSError('publish failed')
            return original(path, dest)
        monkeypatch.setattr(Path, 'rename', failed_publish)
    else:
        api.session.commit.side_effect = OSError('database unavailable')
    assert submit(api).status_code == 503
    assert api.quota.count_today('lab:api_token') == 1
    if api.kind == 'lite':
        assert len(list((api.root / 'submission_staging').glob('*/job_meta.json'))) == 1
        lite._recover_staging_submissions()
        assert api.quota.count_today('lab:api_token') == 0
        assert not list((api.root / 'submission_staging').glob('*'))
    else:
        assert len(api.objects) == 2


def test_rollback_connection_error_before_commit_still_compensates_known_rejection(api):
    if api.kind != 'docker': pytest.skip('Postgres rollback connection')
    api.storage.side_effect = OSError('object storage unavailable')
    api.session.rollback.side_effect = ConnectionError('DB connection gone before any commit')
    assert submit(api).status_code == 503
    assert api.quota.count_today('lab:api_token') == 0
