"""Recorded schema omission + injected failures, never a semantic quality gold."""
from copy import deepcopy
import dataclasses
import json
from pathlib import Path

import pytest
from diary_one_ci import frame_selection, product_editor as p
from diary_one_ci.x02 import run_x02_product
from test_product_editor import Gateway, make_x02_bundle


def recorded():
    return json.loads((Path(__file__).parent / 'fixtures/product_structure_missing_focus_rural_v071.json').read_text())


def schema(data):
    return frame_selection.augment_frame_selection_schema(p.structure_wire_schema(
        data['facts'], 4, candidates=data['candidates']), data['candidates'],
        data['facts'], scene_clues=data['scene_clues'])


def compile_data(data, output):
    return p.compile_assessed_structure(output, data['facts'], data['assets'], 4,
        candidates=data['candidates'], shown_frames=data['shown'], scene_clues=data['scene_clues'])


def repair(data, response):
    audit, calls = [], []
    def ask(stage, prompt, requested_schema, context, **kwargs):
        calls.append((stage, requested_schema, context, kwargs))
        return deepcopy(response)
    output = p.request_structure_repair('REPAIR', 'full original prompt', schema(data),
        {'draft': data['output'], 'facts': list(data['facts'].values())}, ask=ask, audit=audit,
        evidence=('actual-picture-sentinel',), semantic_precheck=lambda probe: compile_data(data, probe)[2])
    return output, audit, calls


def test_recorded_failure_is_missing_focus_not_foreign_p_candidate():
    data = recorded(); original = deepcopy(data)
    chapters, moments, issues, _, audit = compile_data(data, data['output'])
    assert not chapters and not moments
    assert any('missing=[\'focus_fact_ids\']' in r['reason'] for r in issues)
    assert any('chapters.C01.focus_fact_ids:' in r['reason'] for r in issues)
    assert len(audit['assessments']) == len(data['candidates']) == 12
    assert not any('unknown or duplicate shown candidate' in r['reason'] for r in issues)
    assert data == original


def test_recorded_structure_survives_only_explicit_model_focus_decision():
    data = recorded(); original = deepcopy(data)
    # A scripted patch tests reference handling, not a human rating of focus.
    patch = {'chapters': [dict(id='C01', focus_fact_ids=['F002', 'F004', 'F009'])]}
    output, audit, calls = repair(data, patch)
    expected = deepcopy(data['output']); expected['chapters'][0]['focus_fact_ids'] = patch['chapters'][0]['focus_fact_ids']
    assert output == expected and data == original
    assert len(calls) == 1 and calls[0][2]['repair_mode'] == 'MISSING_FOCUS_FACT_IDS_ONLY'
    assert calls[0][3] == {}  # No reclassifying the images in this text-only patch.
    assert audit[0]['raw_structure'] == original['output'] and audit[0]['raw_patch'] == patch
    assert audit[0]['status'] == 'PATCHED_PENDING_FULL_VALIDATION'
    chapters, moments, issues, _, _ = compile_data(data, output)
    assert len(chapters) == 1 and len(moments) == 2 and not issues
    assert chapters[0]['hero_asset_id'] == 'V001'
    assert output['media_choices'] == original['output']['media_choices']


@pytest.mark.parametrize('patch', [None, {}, {'chapters': []},
    {'chapters': [dict(id='C99', focus_fact_ids=['F001'])]},
    {'chapters': [dict(id='C01', focus_fact_ids=['F999'])]},
    {'chapters': [dict(id='C01', focus_fact_ids=[])]},
    {'chapters': [dict(id='C01', focus_fact_ids=['F001','F001'])]},
    {'chapters': [dict(id='C01', focus_fact_ids=['F001'], theme='unauthorized')]},
    {'chapters': [dict(id='C01', focus_fact_ids=['F001'])] * 2},
    {'chapters': [dict(id='C01', focus_fact_ids=['F001'])], 'moments': []},
])
def test_missing_malformed_unknown_duplicate_or_extra_patch_cannot_publish(patch):
    data = recorded(); output, audit, calls = repair(data, patch)
    assert output == data['output'] and len(calls) == 1
    assert audit[0]['status'] == 'REJECTED'
    assert not compile_data(data, output)[0]


@pytest.mark.parametrize('damage', ['unknown_candidate','foreign_fact','duplicate_chapter','extra_key','other_missing','wrong_scene'])
def test_other_reference_or_shape_errors_use_full_repair_without_silent_mapping(damage):
    data = recorded(); row = data['output']['chapters'][0]
    if damage == 'unknown_candidate': row['hero_candidate_id'] = 'P999'
    elif damage == 'foreign_fact': row['fact_ids'].append('F999')
    elif damage == 'duplicate_chapter': data['output']['chapters'].append(deepcopy(row))
    elif damage == 'extra_key': row['made_up'] = 'value'
    elif damage == 'other_missing': del row['grouping_reason']
    elif damage == 'wrong_scene': data['output']['frame_assessments'][0]['scene_observation_id'] = 'FO:P002'
    output, audit, calls = repair(data, {})
    assert output == {} and audit == [] and len(calls) == 1
    assert 'repair_mode' not in calls[0][2] and calls[0][3]['evidence']


def test_legal_id_from_different_chapter_is_not_a_valid_focus():
    data = recorded(); row = data['output']['chapters'][0]
    row['fact_ids'].remove('F010')
    output, audit, _ = repair(data, {'chapters': [dict(id='C01', focus_fact_ids=['F010'])]})
    assert output == data['output'] and audit[0]['status'] == 'REJECTED'


@pytest.mark.parametrize('raw', [None, [], {}, {'chapters': None}, {'chapters': 'wrong type'},
    {'chapters': [None]}, {'chapters': [{'id': ['not-hashable']}]}])
def test_malformed_structure_does_not_crash_short_repair_router(raw):
    data = recorded(); data['output'] = raw
    output, audit, calls = repair(data, {})
    assert output == {} and audit == [] and len(calls) == 1
    assert calls[0][2]['draft'] == raw


def test_recorded_missing_focus_plus_continuity_uses_existing_full_repair_once():
    data = json.loads((Path(__file__).parent / 'fixtures/product_missing_focus_with_continuity_r53.json').read_text())
    raw = data['raw_structure']; original = deepcopy(raw)
    facts = {f['id']: f for f in data['facts']}
    assets = {f['asset_id']: {} for f in facts.values()}
    calls, audit = [], []
    def ask(stage, prompt, schema, context, **kwargs):
        calls.append((stage, schema, context, kwargs))
        return {'model_repair_sentinel': True}
    result = p.request_structure_repair('S09', 'full repair prompt', p.structure_wire_schema(facts),
        {'draft': raw, 'facts': data['facts'], 'issues': []}, ask=ask, audit=audit,
        semantic_precheck=lambda probe: p.compile_structure_wire(probe, facts, assets)[2])
    assert result == {'model_repair_sentinel': True} and len(calls) == 1
    assert 'repair_mode' not in calls[0][2]
    assert 'focus_fact_ids' not in calls[0][2]['draft']['chapters'][0]
    assert any('连续骑行' in r['reason'] for r in calls[0][2]['issues'])
    assert audit[0]['status'] == 'ROUTED_TO_FULL_REPAIR'
    assert raw == original  # No validation-only IDs are silently persisted.


@pytest.mark.parametrize('damage', ['unsupported_theme', 'unsupported_grouping', 'foreign_parent'])
def test_other_semantic_defects_cannot_spend_budget_on_focus_only(damage):
    data = recorded()
    if damage == 'unsupported_theme': data['output']['chapters'][0]['theme'] = '好友连续骑行'
    elif damage == 'unsupported_grouping': data['output']['chapters'][0]['grouping_reason'] = '归途中的连续骑行'
    else: data['output']['moments'][0]['parent_chapter_id'] = 'C99'
    result, audit, calls = repair(data, {'full_repair_sentinel': True})
    assert result == {'full_repair_sentinel': True} and len(calls) == 1
    assert 'repair_mode' not in calls[0][2] and calls[0][3]['evidence']
    assert audit[0]['status'] == 'ROUTED_TO_FULL_REPAIR'


class MissingFocusGateway(Gateway):
    def call(self, stage, prompt, schema, evidence=(), context=None):
        if context.get('repair_mode') == 'MISSING_FOCUS_FACT_IDS_ONLY':
            base = super().call('S07_PRODUCT_EDITOR', prompt, p.structure_wire_schema(
                {f['id']:f for f in context['facts']}), evidence, context)
            return dataclasses.replace(base, stage=stage, output={'chapters': [dict(
                id=c['id'], focus_fact_ids=[c['fact_ids'][0]]) for c in context['chapters']]})
        result = super().call(stage, prompt, schema, evidence, context)
        if stage in ('S08_PRODUCT_STRUCTURE_REVIEW','S09B_PRODUCT_VERIFIED_STRUCTURE'):
            for c in result.output['chapters']: c.pop('focus_fact_ids')
        return result


def test_full_pipeline_uses_two_existing_bounded_repairs_and_retains_public_contract(tmp_path):
    result = run_x02_product(make_x02_bundle(tmp_path, 1), MissingFocusGateway())
    assert result['chapters'] and result['delivery_state'] == 'READY_PRIMARY_COPY'
    trace = result['decision_trace']; records = trace['focused_contract_repairs']
    assert [r['stage'] for r in records] == ['S09_PRODUCT_CONTRACT_REPAIR','S09C_PRODUCT_VERIFIED_REPAIR']
    assert all(r['status'] == 'PATCHED_PENDING_FULL_VALIDATION' for r in records)
    assert not trace['media_selection_rejections']
