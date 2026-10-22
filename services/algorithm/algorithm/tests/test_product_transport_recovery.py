"""Fault-injected real pipeline regressions, without remote model calls."""
import dataclasses
import http.client

import pytest

from diary_one_ci import x02
from test_product_editor import Gateway
from test_x02 import make_x02_bundle


class InterruptedGateway(Gateway):
    def __init__(self, target, message='[Errno 54] Connection reset by peer', failures=1, code='MODEL_TRANSPORT_FAILED'):
        super().__init__()
        self.target, self.message, self.failures, self.code = target, message, failures, code
        self.attempts = 0

    def call(self, stage, prompt, schema, evidence=(), context=None):
        run = super().call(stage, prompt, schema, evidence, context)
        if self.target == 'S09_PRODUCT_CONTRACT_REPAIR' and stage == 'S08_PRODUCT_STRUCTURE_REVIEW':
            return dataclasses.replace(run, output={})
        if stage.startswith(self.target):
            self.attempts += 1
            if self.attempts <= self.failures:
                failed = dataclasses.replace(run, output={}, input_tokens=0, output_tokens=0,
                    call_status='FAILED_BEFORE_RESPONSE')
                raise x02.X02StageCallError(self.message, stage_run=failed, code=self.code)
        return run


@pytest.mark.parametrize('target', ['S04_PERCEPTION', 'S09_PRODUCT_CONTRACT_REPAIR'])
@pytest.mark.parametrize('message', ['[Errno 54] Connection reset by peer',
                                   '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol'])
def test_transient_wrapped_failure_recovers_without_losing_observations(tmp_path, target, message):
    gateway = InterruptedGateway(target, message)
    result = x02.run_x02_product(make_x02_bundle(tmp_path, 1), gateway)
    assert gateway.attempts == 2
    assert result['unresolved_asset_ids'] == []
    assert result['chapters']
    assert result['coverage_status'] == 'COMPLETE'
    assert result['trace']['model_call_failed_count'] == 1


@pytest.mark.parametrize('message,code', [
    ('[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed', 'MODEL_TRANSPORT_FAILED'),
    ('Unsupported protocol configuration', 'MODEL_TRANSPORT_FAILED'),
    ('Unauthorized', 'MODEL_HTTP_401'),
    ('Forbidden', 'MODEL_HTTP_403'),
    ('Quota exhausted', 'MODEL_HTTP_429'),
])
def test_permanent_or_unclassified_failure_does_not_retry(tmp_path, message, code):
    gateway = InterruptedGateway('S09_PRODUCT_CONTRACT_REPAIR', message, failures=99, code=code)
    with pytest.raises(x02.X02ExecutionError):
        x02.run_x02_product(make_x02_bundle(tmp_path, 1), gateway)
    assert gateway.attempts == 1


def test_persistent_reset_stops_after_bounded_retry_and_keeps_failed_attempts(tmp_path):
    gateway = InterruptedGateway('S09_PRODUCT_CONTRACT_REPAIR', failures=99)
    with pytest.raises(x02.X02ExecutionError) as failure:
        x02.run_x02_product(make_x02_bundle(tmp_path, 1), gateway)
    assert gateway.attempts == 2
    runs = [r for r in failure.value.stage_runs if r.stage == 'S09_PRODUCT_CONTRACT_REPAIR']
    assert len(runs) == 2
    assert all(r.call_status == 'FAILED_BEFORE_RESPONSE' for r in runs)


def test_unresolved_input_cannot_be_overridden_by_partial_visual_review(tmp_path):
    class MixedFailure(Gateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            run = super().call(stage, prompt, schema, evidence, context)
            if stage.startswith('S04_PERCEPTION') and context['assets'][0]['timeline_offset_ms'] >= 360_000:
                raise x02.X02StageCallError('Connection reset by peer',
                    stage_run=dataclasses.replace(run, call_status='FAILED_BEFORE_RESPONSE'),
                    code='MODEL_TRANSPORT_FAILED')
            if stage == 'S10_PRODUCT_MOMENT_VALUE':
                raise ValueError('Injected invalid value review')
            return run
    result = x02.run_x02_product(make_x02_bundle(tmp_path, 6), MixedFailure())
    assert result['chapters'], 'A reviewed draft remains diagnostic evidence.'
    assert len(result['unresolved_asset_ids']) == 3
    assert result['coverage_status'] == 'INCOMPLETE'
    assert result['delivery_state'] == 'PIPELINE_BLOCKED'
    assert result['output_mode'] == 'PIPELINE_BLOCKED'


def test_incomplete_http_body_is_audited_as_transport_failure():
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    def interrupted(*args):
        raise http.client.IncompleteRead(b'partial', 200)
    gateway = x02.QwenStageGateway(QwenChatCompletionsAdapter(api_key='offline-placeholder', transport=interrupted))
    with pytest.raises(x02.X02StageCallError) as caught:
        gateway.call('S09_PRODUCT_CONTRACT_REPAIR', 'offline', {}, context={'_audit_stage_failures': True})
    assert caught.value.code == 'MODEL_TRANSPORT_FAILED'
    assert caught.value.stage_run.call_status == 'FAILED_BEFORE_RESPONSE'
    assert caught.value.stage_run.model_calls == 1


def test_recovery_waits_before_repeating_a_transient_request(tmp_path, monkeypatch):
    from diary_one_ci import model_recovery
    delays = []
    monkeypatch.setattr(model_recovery.time, 'sleep', delays.append)
    result = x02.run_x02_product(make_x02_bundle(tmp_path, 1), InterruptedGateway('S09_PRODUCT_CONTRACT_REPAIR'))
    assert result['chapters']
    assert len(delays) == 1 and 0.5 <= delays[0] <= 0.75
