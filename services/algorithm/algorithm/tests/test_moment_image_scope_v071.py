"""Independent bounded-image/anchor regressions; no model-quality score implied."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import pytest

from diary_one_ci import product_editor as p, product_evidence as e
from test_product_moment_grounding import example


def judged(**updates):
    row = {'id': 'M01', 'decision': 'KEEP', 'anchor': '女子扶着自行车站在河边。',
        'event_group_id': 'M01', 'comparison_reason': '这一帧人物姿态成立',
        'scene_kind': 'CYCLING', 'scene_basis_fact_ids': ['F001'], 'value_type': 'DISTINCT_DETAIL',
        'evidence_frame_ids': ['woman'], 'focus_frame_id': 'woman', 'reason': '本帧所见'}
    row.update(updates)
    return {'items': [row]}


def test_unshown_frame_is_rejected_by_request_schema_and_compiler():
    facts, assets, moments = example()
    scoped, evidence, _ = e.moment_visual_scope(moments, facts, assets,
        SimpleNamespace(manifest_path=Path('/tmp/bundle/manifest.json')), max_frames=1)
    assert [frame['frame_id'] for _, frame, _ in evidence] == ['woman']
    output = judged(evidence_frame_ids=['tower'], focus_frame_id='tower')
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(output, e.moment_request_schema(moments, scoped))
    kept, ledger = e.compile_moments(output, moments, scoped)
    assert not kept and ledger[0]['status'] == 'UNVERIFIED'


def test_action_change_keeps_two_distinct_shown_times_and_original_facts(tmp_path):
    facts, assets, moments = example()
    facts['F001'].update(text='同一女子从站立到坐上自行车。', temporal_support='CHANGE')
    original = deepcopy(facts)
    for _, frame, path in e.moment_visual_scope(moments, facts, assets,
            SimpleNamespace(manifest_path=tmp_path / 'bundle.json'))[1]:
        path.write_bytes(('fixture:' + frame['frame_id']).encode())
    observed = []
    def ask(stage, prompt, schema, context, *, evidence):
        observed.extend((f['frame_id'], path.read_bytes()) for _, f, path in evidence)
        output = judged(anchor='女子从站立到坐上自行车。', value_type='ACTION_CHANGE',
                        evidence_frame_ids=['woman', 'tower'])
        jsonschema.validate(output, schema)
        return output
    kept, _, audit = e.review_moments(moments, [], facts, ask,
        assets=assets, bundle=SimpleNamespace(manifest_path=tmp_path / 'bundle.json'))
    assert observed == [('woman', b'fixture:woman'), ('tower', b'fixture:tower')]
    assert len(kept) == 1 and kept[0]['focus_frame_ids'] == ['woman', 'tower']
    assert audit['review_basis'] == 'FACTS_AND_SHOWN_IMAGES'
    memory = p.memory_specs([], kept, facts)[0]
    assert memory['facts'][0]['frame_pts_ms'] == [1000, 5000]
    assert memory['facts'][0]['text'] == '女子从站立到坐上自行车。'
    assert facts == original


@pytest.mark.parametrize('points', [[1000, 1000], [None, None], [1000, None]])
def test_action_change_cannot_be_manufactured_from_non_distinct_time_evidence(points):
    facts, _, moments = example()
    facts['F001'].update(temporal_support='CHANGE', frame_pts_ms=points)
    kept, ledger = e.compile_moments(judged(value_type='ACTION_CHANGE', evidence_frame_ids=['woman', 'tower']),
                                     moments, facts)
    assert not kept and 'temporal evidence' in ledger[0]['reason']


def test_static_anchor_has_no_other_frame_observation_channel():
    facts, _, moments = example()
    facts['F001']['frame_observations'] = [
        {'frame_id': 'woman', 'text': '女子扶车。'},
        {'frame_id': 'tower', 'text': '逆光塔楼。'},
        {'frame_id': 'unknown', 'text': '其它画面中的未知地点。'},
    ]
    original = deepcopy(facts)
    moment = {**moments[0], 'anchor_reviewed_with_images': True,
        'value_type': 'DISTINCT_DETAIL', 'focus': '女子扶车。', 'focus_frame_ids': ['woman']}
    memory = p.memory_specs([], [moment], facts)[0]
    assert 'frame_observations' not in memory['facts'][0]
    assert memory['facts'][0]['text'] == '女子扶车。'
    assert '塔楼' not in str(memory['facts']) and '未知地点' not in str(memory['evidence_groups'])
    assert facts == original


@pytest.mark.parametrize('response', [[], None, 'not an object'])
def test_malformed_moment_provider_envelope_is_audited_without_pipeline_exception(response):
    facts, _, moments = example()
    calls = []
    def ask(*args, **kwargs):
        calls.append(args[0]); return deepcopy(response)
    kept, ledger, output = e.review_moments(moments, [], facts, ask)
    assert not kept and ledger[0]['status'] == 'UNVERIFIED'
    assert len(calls) == 1
    assert output['invalid_provider_output'] == response
    assert output['call_failures'][0]['code'] == 'MOMENT_RESPONSE_NOT_OBJECT'


@pytest.mark.parametrize('response', [[], None, {'items': None}])
def test_malformed_moment_repair_preserves_other_valid_candidates(response):
    facts, _, moments = example()
    facts['F002'] = {**deepcopy(facts['F001']), 'id': 'F002', 'asset_id': 'V002',
                     'evidence_frame_ids': ['other'], 'frame_pts_ms': [1000]}
    moments.append({**moments[0], 'id': 'M02', 'fact_id': 'F002'})
    valid = judged()['items'][0]
    invalid = {**deepcopy(valid), 'id': 'M02', 'event_group_id': 'M02', 'scene_basis_fact_ids': ['F002']}
    calls = []
    def ask(stage, *args, **kwargs):
        calls.append(stage)
        return deepcopy(response) if stage.endswith('_REPAIR') else {'items': [valid, invalid]}
    kept, ledger, output = e.review_moments(moments, [], facts, ask)
    assert len(calls) == 2 and [row['id'] for row in kept] == ['M01']
    assert next(row for row in ledger if row['id'] == 'M02')['status'] == 'UNVERIFIED'
    assert output['invalid_contract_repair_output'] == response
    assert output['call_failures'][0]['type'] == 'ValueError'
