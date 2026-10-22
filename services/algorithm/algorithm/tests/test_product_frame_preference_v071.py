"""Optional image optimization cannot erase already validated memories.

Scripted whole-pipeline checks exercise failure handling, not visual quality.
"""
from copy import deepcopy
import dataclasses

import pytest

from diary_one_ci import product_editor as p
from diary_one_ci.x02 import X02ExecutionError, X02StageCallError, run_x02_product
from test_product_editor import Gateway, make_x02_bundle
from test_product_media_explanations_v071 import recorded


class PreferenceGateway(Gateway):
    def __init__(self, mode='unchanged', *, hard_initial=False, prefer=True):
        super().__init__()
        self.mode, self.hard_initial, self.prefer = mode, hard_initial, prefer
        self.initial = None
        self.attempted = None
        self.feedback = []

    def call(self, stage, prompt, schema, evidence=(), context=None):
        if stage == 'S09C_PRODUCT_VERIFIED_REPAIR':
            self.feedback.append(deepcopy(context))
            if self.mode == 'transport':
                raise OSError('Injected optional image optimization outage')
        result = super().call(stage, prompt, schema, evidence, context)
        raw = result.output
        if stage == 'S09A_FRAME_OBSERVATION' and self.prefer:
            # Same verified subject in another shown frame remains readable.
            # This creates a real soft preference through the frame compiler.
            raw['images'][0].update(visibility='PARTIAL', prominence='TINY_OR_UNCLEAR', occlusion='PARTIAL')
        if stage == 'S09B_PRODUCT_VERIFIED_STRUCTURE':
            if self.hard_initial:
                raw['chapters'][0]['hero_candidate_id'] = 'P999'
            self.initial = deepcopy(raw)
        if stage == 'S09C_PRODUCT_VERIFIED_REPAIR':
            if self.mode == 'stage_error':
                failed = dataclasses.replace(result, output={}, call_status='FAILED', request_id='failed-preference-stage')
                raise X02StageCallError('Invalid provider output', stage_run=failed, code='MODEL_RESPONSE_INVALID')
            if self.mode == 'malformed':
                raw = {}
            elif self.mode == 'delete':
                raw.update(chapters=[], moments=[], media_choices=[], chapter_boundaries=[],
                    unselected_facts=[dict(fact_id=f['id'], reason='Fixture optimization attempted removal')
                                      for f in context['facts']])
            elif self.mode == 'theme':
                raw['chapters'][0]['theme'] = '街边另一种主题'
            elif self.mode == 'focus':
                raw['chapters'][0]['focus'] = '街边细节'
            elif self.mode == 'kind':
                raw['chapters'][0]['experience_kind'] = 'OTHER'
            elif self.mode == 'grouping':
                raw['chapters'][0]['grouping_reason'] = 'Changed grouping without permission'
            elif self.mode == 'moment':
                raw['moments'][0]['focus'] = '另一处可见细节'
            elif self.mode == 'delete_moment':
                raw['moments'] = []
            elif self.mode == 'media_only':
                candidate = context['media_selection_candidates'][1]['candidate_id']
                raw['chapters'][0]['hero_candidate_id'] = candidate
                raw['media_choices'][0]['candidate_id'] = candidate
            self.attempted = deepcopy(raw)
            return dataclasses.replace(result, output=raw)
        return result


def run(tmp_path, mode, **kwargs):
    gateway = PreferenceGateway(mode, **kwargs)
    return run_x02_product(make_x02_bundle(tmp_path, 1), gateway), gateway


@pytest.mark.parametrize('identity', [['C01'], {'id': 'C01'}])
def test_malformed_chapter_identity_is_rejected_without_unhashable_crash(identity):
    data = recorded()
    data['output']['chapters'][0]['id'] = identity
    before = deepcopy(data)
    chapters, _, issues, _, _ = p.compile_assessed_structure(
        data['output'], data['facts'], data['assets'], 4, candidates=data['candidates'],
        shown_frames=data['shown'], scene_clues=data['scene_clues'])
    assert not chapters and issues and data == before
    assert any('chapter identity' in r['reason'] for r in issues)


@pytest.mark.parametrize('mode', ['malformed', 'transport', 'stage_error'])
def test_failed_optional_image_optimization_retains_validated_content(tmp_path, mode):
    result, gateway = run(tmp_path, mode)
    trace = result['decision_trace']
    audit = trace['media_selection_audit']
    assert len(result['chapters']) == 1 and result['delivery_state'] == 'READY_PRIMARY_COPY'
    assert trace['editor_output'] == gateway.initial
    assert not gateway.feedback[0]['issues'] and gateway.feedback[0]['image_preference_feedback']
    assert not trace['media_selection_rejections']
    assert audit['preference_optimization']['status'] == 'RETAINED_VALIDATED_S09B'
    assert audit['frame_assessment'] == {k: v for k, v in audit['frame_assessment_attempts'][0].items() if k != 'stage'}
    if mode == 'malformed':
        assert audit['preference_optimization']['reason'] == 'OPTIMIZATION_FAILED_HARD_CHECKS'
        assert audit['preference_optimization']['attempted_output'] == {}
    else:
        assert audit['preference_optimization']['reason'] == 'OPTIMIZATION_REQUEST_FAILED'
        assert audit['frame_assessment_attempts'][-1]['status'] == 'REQUEST_FAILED'
    if mode == 'transport':
        assert len(gateway.feedback) == 2
        assert [r['attempt'] for r in trace['transport_failures']] == [1, 2]
    if mode == 'stage_error':
        assert result['trace']['model_call_failed_count'] == 1
        assert result['trace']['request_ids'].count('failed-preference-stage') == 1
        assert audit['preference_optimization']['failure']['code'] == 'MODEL_RESPONSE_INVALID'


@pytest.mark.parametrize('mode', ['delete', 'theme', 'focus', 'kind', 'grouping', 'moment', 'delete_moment'])
def test_optional_image_stage_cannot_change_nonmedia_structure(tmp_path, mode):
    result, gateway = run(tmp_path, mode)
    trace = result['decision_trace']
    audit = trace['media_selection_audit']['preference_optimization']
    assert len(result['chapters']) == 1
    assert trace['editor_output'] == gateway.initial
    assert audit['status'] == 'RETAINED_VALIDATED_S09B'
    assert audit['reason'] == 'OPTIMIZATION_CHANGED_NON_MEDIA_STRUCTURE'
    assert audit['attempted_output'] == gateway.attempted
    assert not audit['attempted_rejections']  # Structurally legal, outside this stage's authority.


def test_valid_explicit_picture_change_is_accepted(tmp_path):
    result, gateway = run(tmp_path, 'media_only')
    trace = result['decision_trace']
    audit = trace['media_selection_audit']['preference_optimization']
    assert audit['status'] == 'ACCEPTED_MEDIA_ONLY_UPDATE'
    assert trace['editor_output'] == gateway.attempted
    assert trace['editor_output']['chapters'][0]['hero_candidate_id'] != gateway.initial['chapters'][0]['hero_candidate_id']
    assert result['chapters'][0]['hero_frame_id'] == trace['selected_structure']['chapters'][0]['hero_frame_id']
    assert not trace['media_selection_rejections']


@pytest.mark.parametrize('mode', ['malformed', 'transport', 'stage_error'])
def test_initial_hard_failure_is_never_retained_as_fallback(tmp_path, mode):
    if mode == 'malformed':
        result, gateway = run(tmp_path, mode, hard_initial=True)
        assert gateway.feedback[0]['issues']
        assert not result['chapters'] and result['delivery_state'] == 'PIPELINE_BLOCKED'
        assert 'preference_optimization' not in result['decision_trace']['media_selection_audit']
    else:
        with pytest.raises((OSError, X02ExecutionError)):
            run(tmp_path, mode, hard_initial=True)


def test_initial_hard_failure_allows_an_actual_complete_repair(tmp_path):
    result, gateway = run(tmp_path, 'media_only', hard_initial=True)
    assert gateway.feedback[0]['issues'] and len(result['chapters']) == 1
    assert result['decision_trace']['editor_output'] == gateway.attempted
    assert not result['decision_trace']['media_selection_rejections']
    assert 'preference_optimization' not in result['decision_trace']['media_selection_audit']


def test_no_image_preference_adds_no_optimization_call(tmp_path):
    result, gateway = run(tmp_path, 'unchanged', prefer=False)
    assert result['chapters'] and gateway.feedback == []
    assert 'preference_optimization' not in result['decision_trace']['media_selection_audit']
