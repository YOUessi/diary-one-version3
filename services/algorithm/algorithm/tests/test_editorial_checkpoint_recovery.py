import dataclasses
import json
import hashlib
import shutil
import pytest
from diary_one_ci import x02
from test_product_checkpoint_recovery import CheckpointGateway
from test_x02 import make_x02_bundle


class StopAtStructure(CheckpointGateway):
    def call(self, stage, prompt, schema, evidence=(), context=None):
        result = super().call(stage, prompt, schema, evidence, context)
        if stage == 'S09B_PRODUCT_VERIFIED_STRUCTURE':
            raise x02.X02StageCallError('Connection reset by peer',
                stage_run=dataclasses.replace(result, call_status='FAILED_BEFORE_RESPONSE'),
                code='MODEL_TRANSPORT_FAILED')
        return result


def test_resume_editorial_skips_completed_calls_and_keeps_checks(tmp_path, monkeypatch):
    monkeypatch.setattr('diary_one_ci.model_recovery.time.sleep', lambda _: None)
    path = make_x02_bundle(tmp_path / 'input', 3)
    cache = tmp_path / 'checkpoints'
    with pytest.raises(x02.X02ExecutionError) as failed:
        x02.run_x02_product(path, StopAtStructure(), checkpoint_dir=cache)
    assert failed.value.editorial_checkpoint['saved_stages'] > 0
    second = CheckpointGateway()
    result = x02.run_x02_product(path, second, checkpoint_dir=cache)
    stages = [c['stage'] for c in second.calls]
    assert stages[0] == 'S09B_PRODUCT_VERIFIED_STRUCTURE'
    assert result['chapters'] and not result['unresolved_asset_ids']
    assert result['trace']['evaluation_run_mode'] == 'RESUMED_EDITORIAL_CHECKPOINT'
    audit = result['decision_trace']['editorial_checkpoint']
    assert audit['reused_stages'] > 0
    cached = [m for m in result['trace']['stage_metrics'] if m['stage'] == 'S07_PRODUCT_EDITOR']
    assert cached and cached[0]['model_calls'] == cached[0]['input_tokens'] == 0


def test_repeated_failure_reports_reuse_and_only_current_failed_calls(tmp_path, monkeypatch):
    monkeypatch.setattr('diary_one_ci.model_recovery.time.sleep', lambda _: None)
    path = make_x02_bundle(tmp_path / 'input', 3)
    cache = tmp_path / 'checkpoints'
    for attempt in range(2):
        with pytest.raises(x02.X02ExecutionError) as failed:
            x02.run_x02_product(path, StopAtStructure(), checkpoint_dir=cache)
        if attempt:
            assert failed.value.editorial_checkpoint['reused_stages'] > 0
            assert sum(r.model_calls for r in failed.value.stage_runs) == 2
            assert all(r.stage == 'S09B_PRODUCT_VERIFIED_STRUCTURE' for r in failed.value.stage_runs if r.model_calls)


def test_invalid_cached_schema_is_miss_and_semantic_gates_still_run(tmp_path):
    from diary_one_ci.core import canonical_bytes
    path = make_x02_bundle(tmp_path / 'input', 3)
    cache = tmp_path / 'checkpoints'
    x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=cache)
    target = next(f for f in (cache / 'editorial').rglob('*.json')
                  if json.loads(f.read_text())['receipt']['stage'] == 'S09B_PRODUCT_VERIFIED_STRUCTURE')
    record = json.loads(target.read_text())
    record['receipt']['output'] = {'chapters': 'not-an-array'}
    record.pop('checksum')
    record['checksum'] = hashlib.sha256(canonical_bytes(record)).hexdigest()
    target.write_text(json.dumps(record))
    gateway = CheckpointGateway()
    result = x02.run_x02_product(path, gateway, checkpoint_dir=cache)
    assert result['chapters']
    assert 'S09B_PRODUCT_VERIFIED_STRUCTURE' in [c['stage'] for c in gateway.calls]


def test_cache_reuse_cannot_skip_deterministic_compile_gate(tmp_path, monkeypatch):
    from diary_one_ci import product_editor
    path = make_x02_bundle(tmp_path / 'input', 3)
    cache = tmp_path / 'checkpoints'
    x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=cache)
    original = product_editor.compile_selection
    calls = []
    def gate(*args, **kwargs):
        calls.append(True)
        return original(*args, **kwargs)
    monkeypatch.setattr(product_editor, 'compile_selection', gate)
    gateway = CheckpointGateway()
    result = x02.run_x02_product(path, gateway, checkpoint_dir=cache)
    # Some legacy scripted writer outputs fail their full wire schema and must
    # not be cached even when downstream field-level repair can accept them.
    assert result['decision_trace']['editorial_checkpoint']['reused_stages'] > 0
    assert 'S09B_PRODUCT_VERIFIED_STRUCTURE' not in [c['stage'] for c in gateway.calls]
    assert calls


def test_relocated_upload_reuses_final_image_reviews(tmp_path):
    path = make_x02_bundle(tmp_path / 'input', 3)
    cache = tmp_path / 'checkpoints'
    x02.run_x02_product(path, CheckpointGateway(), checkpoint_dir=cache)
    moved = tmp_path / 'new-http-extraction'
    shutil.copytree(path.parent, moved)
    shutil.rmtree(path.parent)
    gateway = CheckpointGateway()
    result = x02.run_x02_product(moved / path.name, gateway, checkpoint_dir=cache)
    assert result['chapters']
    assert not [c for c in gateway.calls if 'FINAL_VERIFY' in c['stage']]


def test_perception_receipt_has_no_current_transport_on_reuse(tmp_path):
    class Diagnosed(CheckpointGateway):
        def call(self, *args, **kwargs):
            result = super().call(*args, **kwargs)
            return dataclasses.replace(result, transport_diagnostics={'total_ms': 1234, 'phase': 'COMPLETE'})
    path = make_x02_bundle(tmp_path / 'input', 3)
    cache = tmp_path / 'checkpoints'
    x02.run_x02_product(path, Diagnosed(), checkpoint_dir=cache)
    result = x02.run_x02_product(path, Diagnosed(), checkpoint_dir=cache)
    stage = next(m for m in result['trace']['stage_metrics'] if m['stage'].startswith('S04_'))
    assert stage['model_calls'] == 0
    assert not stage.get('transport_diagnostics')
    assert stage['checkpoint_provenance']['prior_request_id']
