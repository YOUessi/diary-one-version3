"""Resume actual perception/editor pipeline with scripted external responses."""
import dataclasses
import http.client
import json
import threading

import pytest

from diary_one_ci import x02
from test_product_editor import Gateway
from test_x02 import make_x02_bundle


class CheckpointGateway(Gateway):
    def __init__(self, fail_assets=(), stop_after_perception=False):
        super().__init__()
        self.fail_assets = set(fail_assets)
        self.stop_after_perception = stop_after_perception
        self.perception_assets = []

    def call(self, stage, prompt, schema, evidence=(), context=None):
        result = super().call(stage, prompt, schema, evidence, context)
        if stage.startswith('S04_PERCEPTION'):
            indexes = tuple(a['timeline_offset_ms'] // 120_000 for a in context['assets'])
            self.perception_assets.append(indexes)
            if self.fail_assets.intersection(indexes):
                raise x02.X02StageCallError('Connection reset by peer',
                    stage_run=dataclasses.replace(result, call_status='FAILED_BEFORE_RESPONSE'),
                    code='MODEL_TRANSPORT_FAILED')
        if self.stop_after_perception and stage == 'S07_PRODUCT_EDITOR':
            raise x02.X02StageCallError('Connection reset by peer',
                stage_run=dataclasses.replace(result, call_status='FAILED_BEFORE_RESPONSE'),
                code='MODEL_TRANSPORT_FAILED')
        return result


def test_resume_after_editor_failure_revalidates_perception_without_another_api_call(tmp_path):
    path = make_x02_bundle(tmp_path / 'input', 3)
    cache = tmp_path / 'checkpoints'
    with pytest.raises(x02.X02ExecutionError):
        x02.run_x02_product(path, CheckpointGateway(stop_after_perception=True), checkpoint_dir=cache)
    second = CheckpointGateway()
    result = x02.run_x02_product(path, second, checkpoint_dir=cache)
    assert second.perception_assets == []
    assert result['chapters'] and not result['unresolved_asset_ids']
    assert result['trace']['evaluation_run_mode'] == 'RESUMED_PERCEPTION_CHECKPOINT'
    assert result['trace']['cross_run_semantic_cache_used'] is True
    assert result['decision_trace']['perception_checkpoint']['reused_assets'] == 3
    cached = [m for m in result['trace']['stage_metrics'] if m['stage'].startswith('S04_PERCEPTION')]
    assert cached and all(m['model_calls'] == 0 and m['input_tokens'] == 0 for m in cached)


def test_resume_retries_only_failed_visual_batches(tmp_path):
    path = make_x02_bundle(tmp_path / 'input', 6)
    cache = tmp_path / 'checkpoints'
    first = x02.run_x02_product(path, CheckpointGateway(fail_assets=(3, 4, 5)), checkpoint_dir=cache)
    assert first['delivery_state'] == 'PIPELINE_BLOCKED'
    second = CheckpointGateway()
    result = x02.run_x02_product(path, second, checkpoint_dir=cache)
    assert second.perception_assets == [(3, 4, 5)]
    assert result['coverage_status'] == 'COMPLETE'
    assert len(result['observations']) == 6
    assert all(o['status'] != 'FAILED' for o in result['observations'])


@pytest.mark.parametrize('changed', ['model', 'prompt', 'manifest'])
def test_changed_model_prompt_or_input_does_not_reuse_prior_observations(tmp_path, monkeypatch, changed):
    path = make_x02_bundle(tmp_path / 'input', 1)
    cache = tmp_path / 'checkpoints'
    x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=cache)
    second = CheckpointGateway()
    if changed == 'model':
        second.model = 'different-model'
    elif changed == 'prompt':
        original = x02._perception_prompt
        monkeypatch.setattr(x02, '_perception_prompt', lambda *a, **kw: original(*a, **kw) + '\nchanged policy')
    else:
        manifest = json.loads(path.read_text())
        manifest['session']['exported_at'] = '2026-10-23T00:00:00Z'
        path.write_text(json.dumps(manifest))
    result = x02.run_x02_product(path, second, checkpoint_dir=cache)
    assert second.perception_assets == [(0,)]
    assert result['chapters']
    assert result['trace']['cross_run_semantic_cache_used'] is False


def test_corrupt_checkpoint_is_a_miss_not_a_failed_generation(tmp_path):
    path = make_x02_bundle(tmp_path / 'input', 1)
    cache = tmp_path / 'checkpoints'
    x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=cache)
    files = list(cache.rglob('*.json'))
    assert files
    for file in files:
        file.write_text('{truncated')
    gateway = CheckpointGateway()
    result = x02.run_x02_product(path, gateway, checkpoint_dir=cache)
    assert gateway.perception_assets == [(0,)]
    assert result['chapters']


def test_readable_but_invalid_observation_is_revalidated_before_reuse(tmp_path):
    from diary_one_ci.bundle import load_app_library_bundle
    path = make_x02_bundle(tmp_path / 'input', 1)
    cache = tmp_path / 'checkpoints'
    x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=cache)
    record = json.loads(next(cache.rglob('*.json')).read_text())
    store = x02._perception_checkpoint_store(cache, load_app_library_bundle(path), CheckpointGateway())
    receipt = dict(store.load(record['key']))
    receipt['output'] = {'observations': []}
    store.save(record['key'], receipt)
    gateway = CheckpointGateway()
    result = x02.run_x02_product(path, gateway, checkpoint_dir=cache)
    assert gateway.perception_assets == [(0,)]
    assert result['chapters']
    assert result['decision_trace']['perception_checkpoint']['reused_assets'] == 0


def test_optional_checkpoint_write_failure_does_not_fail_generation(tmp_path):
    path = make_x02_bundle(tmp_path / 'input', 1)
    unavailable = tmp_path / 'not-a-directory'
    unavailable.write_text('occupied')
    result = x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=unavailable)
    assert result['chapters']
    assert result['decision_trace']['perception_checkpoint']['saved_batches'] == 0
    assert any(e['status'] == 'SAVE_FAILED' for e in result['decision_trace']['perception_checkpoint']['events'])


@pytest.mark.parametrize('poison_existing', [False, True])
def test_provider_declared_failure_is_not_an_empty_success_checkpoint(tmp_path, poison_existing):
    from diary_one_ci.bundle import load_app_library_bundle
    class DeclaredFailure(CheckpointGateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            result = super().call(stage, prompt, schema, evidence, context)
            if stage.startswith('S04_PERCEPTION'):
                for row in result.output['observations']:
                    row.update(status='FAILED', facts=[])
            return result
    path = make_x02_bundle(tmp_path / 'input', 1)
    cache = tmp_path / 'checkpoints'
    if poison_existing:
        x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=cache)
        record = json.loads(next(cache.rglob('*.json')).read_text())
        store = x02._perception_checkpoint_store(cache, load_app_library_bundle(path), CheckpointGateway())
        receipt = dict(store.load(record['key']))
        for row in receipt['output']['observations']:
            row.update(status='FAILED', facts=[])
        store.save(record['key'], receipt)
    else:
        failed = x02.run_x02_product(path, DeclaredFailure(), checkpoint_dir=cache)
        assert failed['delivery_state'] == 'PIPELINE_BLOCKED'
        assert failed['unresolved_asset_ids']
        assert not list(cache.rglob('*.json'))
    second = CheckpointGateway()
    result = x02.run_x02_product(path, second, checkpoint_dir=cache)
    assert second.perception_assets == [(0,)]
    assert result['chapters'] and not result['unresolved_asset_ids']


def test_http_product_retry_survives_temporary_input_cleanup_and_audits_reuse(tmp_path, monkeypatch):
    from diary_one_ci.x01_server import make_server
    monkeypatch.setenv('DIARY_ONE_X02_EDITOR', 'product_v1')
    path = make_x02_bundle(tmp_path / 'input', 1)
    manifest = json.loads(path.read_text())
    boundary = 'OfflineCheckpointBoundary'
    body = bytearray()
    def part(name, filename, content_type, data):
        body.extend(('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
                     'Content-Type: %s\r\n\r\n' % (boundary, name, filename, content_type)).encode())
        body.extend(data)
        body.extend(b'\r\n')
    part('manifest', 'bundle.json', 'application/json', path.read_bytes())
    for asset in manifest['assets']:
        for frame in asset['frames']:
            part(frame['frame_id'], frame['relative_path'], 'image/jpeg',
                 (path.parent / frame['relative_path']).read_bytes())
    body.extend(('--%s--\r\n' % boundary).encode())
    audits = tmp_path / 'server-audits'
    server = make_server('127.0.0.1', 0, adapter_name='fixture',
                         run_audit_dir=tmp_path / 'legacy-audits', x02_run_audit_dir=audits)
    gateway = CheckpointGateway(stop_after_perception=True)
    server.RequestHandlerClass.stage_gateway = gateway
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def post():
        connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=20)
        try:
            connection.request('POST', x02.X02_PREVIEW_PATH, bytes(body),
                {'Content-Type': 'multipart/form-data; boundary=' + boundary})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()
    try:
        status, failure = post()
        assert status >= 500 and failure['code'] == 'MODEL_TRANSPORT_FAILED'
        status, failure = post()
        assert status >= 500 and failure['model_call_attempted'] is True
        assert failure['model_call_completed'] is False
        failed_audit = json.loads((audits / manifest['session']['session_id'] / 'failed_run_audit.json').read_text())
        assert failed_audit['evaluation_run_mode'] == 'RESUMED_PERCEPTION_CHECKPOINT'
        assert failed_audit['cross_run_semantic_cache_used'] is True
        assert failed_audit['completed_stage_calls'] == []
        assert failed_audit['perception_checkpoint']['reused_assets'] == 1
        gateway.stop_after_perception = False
        status, result = post()
        assert status == 200 and result['chapters']
        assert gateway.perception_assets == [(0,)]
        assert result['trace']['cross_run_semantic_cache_used'] is True
        audit = json.loads((audits / manifest['session']['session_id'] / 'run_audit.json').read_text())
        assert audit['cross_run_semantic_cache_used'] is True
        assert audit['evaluation_run_mode'] == 'RESUMED_PERCEPTION_CHECKPOINT'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
