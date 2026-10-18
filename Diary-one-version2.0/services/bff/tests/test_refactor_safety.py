"""Regression tests for refactor boundaries; no live service or user data touched."""
import asyncio
import time
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.dialects import postgresql

from shared.oauth import validate_google_claims
from shared.quota import CallerIdentity, DailyQuotaStore
from shared.sessions import SessionStore
from shared.models import JobStatus
from bff.routes import account, day_revisions
from bff.routes.jobs import get_job
from worker import processor


def test_google_rejects_other_app_issuer_expired_and_missing_subject():
    claims = dict(aud='our-client', iss='https://accounts.google.com', exp=time.time() + 3600, sub='subject')
    validate_google_claims(claims, {'our-client'})
    for invalid in [dict(aud='other-client'), dict(iss='attacker'), dict(exp=0), dict(exp='bad'), dict(sub='')]:
        with pytest.raises(HTTPException) as caught:
            validate_google_claims({**claims, **invalid}, {'our-client'})
        assert caught.value.status_code == 401


def test_session_revocation_persists_and_preserves_other_accounts(tmp_path):
    path = tmp_path / 'sessions.json'
    sessions = SessionStore(path)
    for token, email in [('one', 'A@example.com'), ('two', 'a@example.com'), ('other', 'b@example.com')]:
        sessions.register(token, email)
    sessions.revoke_email(' A@EXAMPLE.COM ')
    restored = SessionStore(path)
    assert restored.resolve_email('one') is None
    assert restored.resolve_email('two') is None
    assert restored.resolve_email('other') == 'b@example.com'


def test_quota_deletion_preserves_other_accounts(tmp_path):
    store = DailyQuotaStore(tmp_path / 'quota.json')
    store.consume('email:a@example.com')
    store.consume('email:b@example.com')
    store.delete_caller('email:a@example.com')
    assert store.count_today('email:a@example.com') == 0
    assert store.count_today('email:b@example.com') == 1


def test_redis_notification_failure_keeps_durable_submission(monkeypatch):
    monkeypatch.setattr(day_revisions, 'enqueue_job', Mock(side_effect=ConnectionError('Redis offline')))
    day_revisions.notify_worker(str(uuid.uuid4()))  # must not turn a committed submission into HTTP failure


def account_fixture(monkeypatch, jobs):
    session = SimpleNamespace(scalars=AsyncMock(return_value=SimpleNamespace(all=lambda: jobs)),
                              delete=AsyncMock(), commit=AsyncMock())
    hooks = SimpleNamespace(lock=AsyncMock(), evidence=Mock(), revoke=Mock(), quota=Mock(), forget=AsyncMock())
    monkeypatch.setattr(account, 'lock_account', hooks.lock)
    monkeypatch.setattr(account, 'delete_job_evidence', hooks.evidence)
    monkeypatch.setattr(account, 'session_store', lambda: SimpleNamespace(revoke_email=hooks.revoke))
    monkeypatch.setattr(account, 'quota_store', lambda: SimpleNamespace(delete_caller=hooks.quota))
    monkeypatch.setattr(account, '_otp', SimpleNamespace(store=SimpleNamespace(forget=hooks.forget)))
    caller = CallerIdentity('email:a@example.com', 'a@example.com', 'session')
    return session, hooks, caller


def test_account_deletion_requires_own_session(monkeypatch):
    session, hooks, _ = account_fixture(monkeypatch, [])
    with pytest.raises(HTTPException) as caught:
        asyncio.run(account.delete_account(Mock(), CallerIdentity('lab:api_token', None, 'api_token'), session))
    assert caught.value.status_code == 403
    hooks.lock.assert_not_called()


@pytest.mark.parametrize('status', [JobStatus.pending, JobStatus.processing])
def test_account_deletion_refuses_inflight_without_touching_data(monkeypatch, status):
    session, hooks, caller = account_fixture(monkeypatch, [SimpleNamespace(id=uuid.uuid4(), status=status)])
    with pytest.raises(HTTPException) as caught:
        asyncio.run(account.delete_account(Mock(), caller, session))
    assert caught.value.status_code == 409
    hooks.evidence.assert_not_called()
    session.delete.assert_not_called()
    hooks.revoke.assert_not_called()


def test_account_deletion_storage_failure_remains_retryable(monkeypatch):
    session, hooks, caller = account_fixture(monkeypatch, [SimpleNamespace(id=uuid.uuid4(), status=JobStatus.succeeded)])
    hooks.evidence.side_effect = OSError('Storage unavailable')
    with pytest.raises(HTTPException) as caught:
        asyncio.run(account.delete_account(Mock(), caller, session))
    assert caught.value.status_code == 503
    session.delete.assert_not_called()
    hooks.revoke.assert_not_called()
    session.commit.assert_not_called()


def test_account_deletion_filters_owner_and_clears_sessions_quota_otp(monkeypatch):
    job = SimpleNamespace(id=uuid.uuid4(), status=JobStatus.failed)
    session, hooks, caller = account_fixture(monkeypatch, [job])
    assert asyncio.run(account.delete_account(Mock(), caller, session)) == {'deleted': True}
    statement = session.scalars.call_args.args[0].compile(dialect=postgresql.dialect())
    assert 'cloud_jobs.owner_email =' in str(statement)
    assert caller.email in statement.params.values()
    hooks.evidence.assert_called_once_with([str(job.id)])
    session.delete.assert_awaited_once_with(job)
    session.commit.assert_awaited_once()
    hooks.revoke.assert_called_once_with(caller.email)
    hooks.quota.assert_called_once_with(caller.key)
    hooks.forget.assert_awaited_once_with(caller.email)


def test_versioned_evidence_deletion_limits_prefix_and_version_ids(monkeypatch):
    client = Mock()
    client.list_objects.return_value = [SimpleNamespace(object_name='jobs/id/bundle.json', version_id='version1')]
    removed = []
    client.remove_objects.side_effect = lambda bucket, objects: removed.extend(objects) or iter([])
    monkeypatch.setattr(account, 'minio_client', lambda: client)
    account.delete_job_evidence(['id'])
    assert client.list_objects.call_args.kwargs == dict(prefix='jobs/id/', recursive=True, include_version=True)
    assert removed[0].name == 'jobs/id/bundle.json'
    assert removed[0].version_id == 'version1'


@pytest.mark.parametrize('status', [JobStatus.succeeded, JobStatus.failed, JobStatus.processing])
def test_duplicate_or_live_job_is_not_executed(monkeypatch, status):
    session = Mock()
    session.scalar.return_value = SimpleNamespace(status=status, updated_at=datetime.now(timezone.utc))
    monkeypatch.setattr(processor, 'SyncSessionLocal', lambda: session)
    cloud = Mock()
    monkeypatch.setattr(processor, 'run_x02_preview', cloud)
    processor.process_job_sync(str(uuid.uuid4()))
    session.commit.assert_not_called()
    session.close.assert_called_once()
    cloud.assert_not_called()


def test_recovery_scan_uses_skip_locked_and_stale_cutoff(monkeypatch):
    session = Mock()
    job_id = uuid.uuid4()
    session.scalars.return_value.all.return_value = [SimpleNamespace(id=job_id)]
    monkeypatch.setattr(processor, 'SyncSessionLocal', lambda: session)
    assert processor.recoverable_job_ids(3) == [str(job_id)]
    statement = session.scalars.call_args.args[0].compile(dialect=postgresql.dialect())
    assert 'FOR UPDATE SKIP LOCKED' in str(statement)
    assert 'cloud_jobs.updated_at <=' in str(statement)
    assert any(isinstance(value, datetime) and value < datetime.now(timezone.utc) - timedelta(seconds=30)
               for value in statement.params.values())
    session.close.assert_called_once()


@pytest.mark.parametrize('owner', [None, 'b@example.com'])
def test_session_cannot_read_ownerless_or_another_accounts_job(owner):
    session = SimpleNamespace(get=AsyncMock(return_value=SimpleNamespace(owner_email=owner)))
    with pytest.raises(HTTPException) as caught:
        asyncio.run(get_job(str(uuid.uuid4()), session, CallerIdentity('email:a@example.com', 'a@example.com', 'session')))
    assert caught.value.status_code == 404
