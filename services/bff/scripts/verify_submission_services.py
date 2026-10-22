"""Isolated local PostgreSQL/MinIO submission checks; never calls a model.

Run with the BFF Python environment. Requires a local Docker daemon and cached
postgres:16-alpine + cgr.dev/chainguard/minio:latest images. Removes only the two
temporary containers it creates; never mounts project or production data.
"""
import argparse
import asyncio
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True).strip()


async def check_services():
    import httpx
    from fastapi import FastAPI
    from PIL import Image
    from sqlalchemy import select, text
    from sqlalchemy.ext.asyncio import AsyncSession
    from minio.versioningconfig import VersioningConfig, ENABLED
    from bff.auth import require_bearer
    from bff.routes import day_revisions, jobs
    from shared.config import settings
    from shared.db import async_engine, init_db_async, AsyncSessionLocal
    from shared.models import Base, CloudJob
    from shared.quota import CallerIdentity, quota_store
    from shared.storage import minio_client, ensure_bucket, download_bytes

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text('ALTER TABLE cloud_jobs DROP COLUMN input_fingerprint'))
    await init_db_async()
    await init_db_async()
    async with async_engine.connect() as conn:
        assert await conn.scalar(text("SELECT count(*) FROM information_schema.columns WHERE table_name='cloud_jobs' AND column_name='input_fingerprint'")) == 1

    client = minio_client()
    ensure_bucket(client)
    client.set_bucket_versioning(settings.minio_bucket, VersioningConfig(ENABLED))
    application = FastAPI()
    application.include_router(day_revisions.router)
    application.include_router(jobs.router)
    identity = CallerIdentity('lab:api_token', None, 'api_token')
    application.dependency_overrides[require_bearer] = lambda: identity
    image = io.BytesIO(); Image.new('RGB', (768, 1024), 'white').save(image, format='JPEG')
    jpeg = image.getvalue()
    raw = json.dumps({'bundle_version': 'DIARY_ONE_APP_LIBRARY_BUNDLE_V04',
        'session': {'session_id': 'isolated-regression'}, 'assets': [{'asset_id': 'photo',
        'media_kind': 'PHOTO', 'frames': [{'frame_id': 'f0', 'relative_path': 'frames/f0.jpg',
        'width': 768, 'height': 1024, 'sha256': hashlib.sha256(jpeg).hexdigest()}]}]}).encode()
    def files(revision, language='zh'):
        return [('manifest', (None, raw, 'application/json')), ('day_revision_id', (None, revision)),
                ('app_client_profile', (None, json.dumps({'language': language}), 'application/json')),
                ('f0', ('frame.jpg', jpeg, 'image/jpeg'))]
    def stored():
        return {(obj.object_name, obj.version_id) for obj in client.list_objects(
            settings.minio_bucket, recursive=True, include_version=True)}
    async def rows(revision):
        async with AsyncSessionLocal() as session:
            return list((await session.scalars(select(CloudJob).where(CloudJob.day_revision_id == revision))).all())

    checks = ['existing_schema_migration_is_idempotent']
    # Queue notification is the only external work disabled. DB, storage, HTTP
    # multipart handling and quota persistence all use their real implementations.
    with patch.object(day_revisions, 'notify_worker', lambda job_id: None):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=application), base_url='http://local-test') as http:
            async def post(revision, language='zh'):
                return await http.post('/v1/day-revisions', files=files(revision, language))
            replies = await asyncio.gather(*(post('same-input') for _ in range(8)))
            assert all(r.status_code == 200 for r in replies), [r.text for r in replies]
            ids = {r.json()['job_id'] for r in replies}; assert len(ids) == 1
            assert len(await rows('same-input')) == 1
            assert quota_store().count_today(identity.key) == 1
            first = ids.pop()
            assert download_bytes(client, f'jobs/{first}/bundle.json') == raw
            assert download_bytes(client, f'jobs/{first}/frames/f0.jpg') == jpeg
            assert (await http.get(f'/v1/jobs/{first}')).json()['status'] == 'pending'
            checks.append('8_concurrent_identical_requests_create_one_durable_job_and_charge')
            replies = await asyncio.gather(post('different-input', 'zh'), post('different-input', 'en'))
            assert sorted(r.status_code for r in replies) == [200, 409]
            assert len(await rows('different-input')) == 1
            checks.append('concurrent_different_inputs_conflict_without_second_charge')
            assert quota_store().count_today(identity.key) == 2
            before = stored()
            upload = day_revisions.upload_bytes
            def write_then_fail(storage, name, data, content_type):
                upload(storage, name, data, content_type)
                if name.endswith('.jpg'): raise OSError('injected after actual object write')
            with patch.object(day_revisions, 'upload_bytes', write_then_fail):
                assert (await post('storage-failure')).status_code == 503
            assert stored() == before and not await rows('storage-failure')
            assert quota_store().count_today(identity.key) == 2
            checks.append('real_versioned_object_partial_write_removed_and_quota_refunded')

            async def fail_commit(session): raise OSError('injected before database commit')
            with patch.object(AsyncSession, 'commit', fail_commit):
                assert (await post('db-failure')).status_code == 503
            assert stored() == before and not await rows('db-failure')
            assert quota_store().count_today(identity.key) == 2
            checks.append('actual_database_rollback_removes_objects_and_refunds_quota')

            commit = AsyncSession.commit
            async def lost_ack(session):
                await commit(session)
                raise ConnectionError('injected after successful commit')
            with patch.object(AsyncSession, 'commit', lost_ack):
                reply = await post('ack-lost')
            assert reply.status_code == 200, reply.text
            assert len(await rows('ack-lost')) == 1
            assert quota_store().count_today(identity.key) == 3
            retry = await post('ack-lost')
            assert retry.json()['job_id'] == reply.json()['job_id'] and retry.json()['idempotent']
            assert len(stored()) == 9  # 3 complete bundles, manifest/profile/frame each.
            checks.append('actual_commit_with_lost_ack_preserves_job_and_retry_reuses_it')
    await async_engine.dispose()
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    endpoint = docker('context', 'inspect', '--format', '{{.Endpoints.docker.Host}}')
    if not endpoint.startswith('unix://') or os.environ.get('DOCKER_HOST') or os.environ.get('DOCKER_CONTEXT'):
        raise SystemExit('Use the local Docker Unix socket with no endpoint overrides.')
    images = ['postgres:16-alpine', 'cgr.dev/chainguard/minio:latest']
    image_ids = {name: docker('image', 'inspect', name, '--format', '{{.Id}}') for name in images}
    created = []
    try:
        suffix = f'{os.getpid()}-{int(time.time())}'
        pg, store = f'diary-regression-pg-{suffix}', f'diary-regression-minio-{suffix}'
        docker('run', '-d', '--rm', '--name', pg, '--cpus', '1', '--memory', '256m',
               '-p', '127.0.0.1::5432', '-e', 'POSTGRES_USER=diary_test', '-e', 'POSTGRES_DB=diary_test',
               '-e', 'POSTGRES_PASSWORD=local-regression-only', images[0]); created.append(pg)
        docker('run', '-d', '--rm', '--name', store, '--cpus', '1', '--memory', '512m',
               '-p', '127.0.0.1::9000', '-e', 'MINIO_ROOT_USER=regression',
               '-e', 'MINIO_ROOT_PASSWORD=local-regression-only', images[1], 'server', '/tmp/regression',
               '--address', ':9000'); created.append(store)
        pg_port = docker('port', pg, '5432/tcp').split(':')[-1]
        store_port = docker('port', store, '9000/tcp').split(':')[-1]
        import urllib.request
        for _ in range(30):
            ready = subprocess.run(['docker', 'exec', pg, 'pg_isready', '-U', 'diary_test'], capture_output=True).returncode == 0
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{store_port}/minio/health/ready', timeout=1): pass
            except Exception: ready = False
            if ready: break
            time.sleep(0.5)
        else: raise RuntimeError('Temporary services did not become ready')
        with tempfile.TemporaryDirectory(prefix='diary-submission-regression-') as directory:
            os.environ.update(DATABASE_URL=f'postgresql+asyncpg://diary_test:local-regression-only@127.0.0.1:{pg_port}/diary_test',
                DATABASE_URL_SYNC=f'postgresql+psycopg://diary_test:local-regression-only@127.0.0.1:{pg_port}/diary_test',
                MINIO_ENDPOINT=f'127.0.0.1:{store_port}', MINIO_ACCESS_KEY='regression',
                MINIO_SECRET_KEY='local-regression-only', MINIO_BUCKET='isolated-regression',
                DAY_REVISION_QUOTA_PATH=str(Path(directory)/'quota.json'), DAY_REVISION_DAILY_LIMIT='100')
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            checks = asyncio.run(check_services())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({'checks_passed': checks, 'image_ids': image_ids,
            'model_calls': 0, 'public_server_calls': 0}, indent=2) + '\n')
        print(json.dumps({'passed': len(checks), 'checks': checks}))
    finally:
        for name in reversed(created):
            subprocess.run(['docker', 'rm', '-f', '-v', name], check=True, stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
