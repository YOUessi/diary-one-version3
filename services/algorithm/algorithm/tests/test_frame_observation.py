"""Scripted reference and retry regressions, not visual-quality acceptance."""
from copy import deepcopy
from types import SimpleNamespace

import jsonschema
import pytest

from diary_one_ci import frame_observation as fo, frame_selection as fs, x02


def fixture():
    facts = {'F1': dict(asset_id='V1', source_asset_id='source1',
        text='前景可见手臂与车把，桥面上有橙色车厢。', evidence_frame_ids=['f0', 'f1'])}
    candidates = [dict(candidate_id=pid, asset_id='V1', frame_id=f, fact_ids=['F1'])
                  for pid, f in [('P1', 'f0'), ('P2', 'f1')]]
    evidence = [(dict(asset_id='source1'), dict(frame_id=c['frame_id']), '/fixture/' + c['frame_id'] + '.jpg')
                for c in candidates]
    rows = [dict(candidate_id='P1', observation='前景是手臂与车把。', subject_role='ACTIVITY_CONTEXT',
        visibility='CLEAR', prominence='DOMINANT', occlusion='NONE', fact_checks=[dict(fact_id='F1',
        support='PARTIAL', visible_quote='手臂与车把', not_visible_quote='桥面上有橙色车厢')]),
        dict(candidate_id='P2', observation='桥面上可见橙色车厢。', subject_role='SPECIFIC_SUBJECT',
        visibility='CLEAR', prominence='READABLE', occlusion='NONE', fact_checks=[dict(fact_id='F1',
        support='PARTIAL', visible_quote='桥面上有橙色车厢', not_visible_quote='手臂与车把')])]
    return candidates, facts, evidence, {'images': rows}


def structure(clues, hero='P1'):
    rows = []
    for pid, options in clues['candidate_scene_clues'].items():
        if options:
            clue = options[0]
            rows.append(dict(candidate_id=pid, fact_ids=['F1'], scene_observation_id=clue['scene_observation_id'],
                visible_detail=clue['text'], theme_fit='MAIN_SUBJECT', visibility='CLEAR',
                prominence='DOMINANT', occlusion='NONE'))
        else:
            rows.append(dict(candidate_id=pid, fact_ids=[], scene_observation_id=None, visible_detail='',
                theme_fit='UNSUPPORTED', visibility='NOT_VISIBLE', prominence='TINY_OR_UNCLEAR', occlusion='NONE'))
    return dict(chapters=[dict(id='C1', fact_ids=['F1'], focus_fact_ids=['F1'], hero_candidate_id=hero)],
        media_choices=[dict(chapter_id='C1', candidate_id=hero, reason='可见主体。')], frame_assessments=rows)


def test_exact_single_frame_support_reaches_selection_without_rewriting_facts():
    candidates, facts, _, output = fixture()
    original = deepcopy((output, candidates, facts))
    clues, audit = fo.compile_observations(output, candidates, facts)
    assert [r['status'] for r in audit['frame_ledger']] == ['VERIFIED_REFERENCE_SCOPE'] * 2
    assert audit['frame_claim_supports'][0]['fact_supports'][0]['visible_quote'] == '手臂与车把'
    raw = structure(clues)
    clean, decision, issues = fs.resolve_frame_selection(raw, candidates, facts, scene_clues=clues)
    assert not issues and clean['chapters'][0]['hero_candidate_id'] == 'P1'
    assert decision['preference_warnings'][0]['code'] == 'FOCUS_SUBJECT_PREFERRED_FOR_COVER'
    assert decision['preference_warnings'][0]['stronger_candidate_ids'] == ['P2']
    normalization = next(r for r in decision['classification_normalizations'] if r['candidate_id'] == 'P1')
    assert normalization['changes']['theme_fit']['effective'] == 'SUPPORTING_CONTEXT'
    assert raw['frame_assessments'][0]['theme_fit'] == 'MAIN_SUBJECT'
    assert (output, candidates, facts) == original


def test_two_different_visible_fragments_of_one_fact_are_complementary_not_ranked():
    candidates, facts, _, output = fixture()
    facts['F1']['text'] = '街边有雕塑，后面可见花墙。'
    output['images'][0].update(observation='街边有雕塑。', subject_role='SPECIFIC_SUBJECT', prominence='READABLE')
    output['images'][0]['fact_checks'][0].update(visible_quote='街边有雕塑', not_visible_quote='可见花墙')
    output['images'][1].update(observation='花墙完整可见。', prominence='DOMINANT')
    output['images'][1]['fact_checks'][0].update(visible_quote='可见花墙', not_visible_quote='街边有雕塑')
    clues, _ = fo.compile_observations(output, candidates, facts)
    _, audit, issues = fs.resolve_frame_selection(structure(clues), candidates, facts, scene_clues=clues)
    assert not issues and not audit['preference_warnings']
    same_asset = next(r for r in audit['comparisons'] if r['scope'] == 'SAME_ASSET_SAME_VISIBLE_FACT_FRAGMENT')
    assert same_asset['compared_candidate_ids'] == ['P1']


def test_same_visible_fragment_can_produce_nonblocking_quality_feedback():
    candidates, facts, _, output = fixture()
    output['images'][0] = {**deepcopy(output['images'][1]), 'candidate_id': 'P1', 'visibility': 'PARTIAL',
                           'prominence': 'TINY_OR_UNCLEAR', 'occlusion': 'PARTIAL'}
    clues, _ = fo.compile_observations(output, candidates, facts)
    _, audit, issues = fs.resolve_frame_selection(structure(clues), candidates, facts, scene_clues=clues)
    assert not issues and audit['preference_warnings'][0]['code'] == 'SAME_SUBJECT_MORE_READABLE_FRAME'
    assert audit['preference_warnings'][0]['stronger_candidate_ids'] == ['P2']


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'foreign_fact', 'fabricated_quote', 'overlap',
                                  'contradictory_support', 'missing_check', 'duplicate_check', 'unhashable_id'])
def test_invalid_observation_isolated_to_its_image_without_scene_fallback(fault):
    candidates, facts, _, output = fixture()
    row = output['images'][0]
    if fault == 'missing': output['images'].pop(0)
    elif fault == 'duplicate': output['images'].append(deepcopy(row))
    elif fault == 'foreign_fact': row['fact_checks'][0]['fact_id'] = 'F99'
    elif fault == 'fabricated_quote': row['fact_checks'][0]['visible_quote'] = '车厢停在手臂旁边'
    elif fault == 'overlap': row['fact_checks'][0]['not_visible_quote'] = '车把'
    elif fault == 'contradictory_support': row['fact_checks'][0]['support'] = 'NOT_VISIBLE'
    elif fault == 'missing_check': row['fact_checks'] = []
    elif fault == 'duplicate_check': row['fact_checks'] *= 2
    elif fault == 'unhashable_id': row['candidate_id'] = ['P1']
    clues, audit = fo.compile_observations(output, candidates, facts)
    assert not clues['candidate_scene_clues']['P1'] and clues['candidate_scene_clues']['P2']
    assert audit['frame_ledger'][0]['status'] == 'UNVERIFIED' and not audit['whole_response_invalid']
    _, decision, issues = fs.resolve_frame_selection(structure(clues, 'P2'), candidates, facts, scene_clues=clues)
    assert not issues and not decision['preference_warnings']
    assert fs.resolve_frame_selection(structure(clues, 'P1'), candidates, facts, scene_clues=clues)[2]


def test_dedicated_quote_does_not_allow_editor_to_borrow_a_nonvisible_fact():
    candidates, facts, _, output = fixture()
    facts['F2'] = {**facts['F1'], 'text': '有人扶着自行车。'}
    candidates[0]['fact_ids'].append('F2')
    output['images'][0]['fact_checks'].append(dict(fact_id='F2', support='NOT_VISIBLE',
        visible_quote='', not_visible_quote='有人扶着自行车'))
    clues, _ = fo.compile_observations(output, candidates, facts)
    raw = structure(clues)
    raw['chapters'][0]['fact_ids'].append('F2')
    raw['frame_assessments'][0]['fact_ids'] = ['F2']
    assert fs.resolve_frame_selection(raw, candidates, facts, scene_clues=clues)[2]
    schema = fs.augment_frame_selection_schema(dict(type='object', properties={}, required=[]),
        candidates, facts, scene_clues=clues)
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate(raw, schema)


def test_dynamic_schema_binds_real_candidate_and_fact_ids_and_empty_batch():
    candidates, facts, _, output = fixture()
    schema = fo.observation_schema(candidates, facts)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(output, schema)
    output['images'][0]['fact_checks'][0]['fact_id'] = 'F99'
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate(output, schema)
    jsonschema.validate({'images': []}, fo.observation_schema([], {}))


def call_with(responses, *, stage_runs=None):
    candidates, facts, evidence, _ = fixture()
    calls = []
    def ask(stage, prompt, schema, context, **kwargs):
        calls.append((stage, deepcopy(context), kwargs['evidence']))
        response = responses[len(calls) - 1]
        if isinstance(response, Exception): raise response
        return response
    clues, audit = fo.review_frame_observations(candidates, facts, ask, evidence=evidence, stage_runs=stage_runs)
    return clues, audit, calls


def test_partial_invalid_does_not_trigger_another_normal_image_call():
    _, _, _, output = fixture(); output['images'].pop(0)
    clues, audit, calls = call_with([output])
    assert len(calls) == 1 and len(audit['attempts']) == 1
    assert not clues['candidate_scene_clues']['P1'] and clues['candidate_scene_clues']['P2']


@pytest.mark.parametrize('failure', [ValueError('bad json'), {'wrong': []}, {'images': []}])
def test_whole_format_failure_has_one_bounded_image_bearing_retry(failure):
    candidates, _, evidence, output = fixture()
    clues, audit, calls = call_with([failure, output])
    assert len(calls) == len(audit['attempts']) == 2
    assert calls[1][0].endswith('_FORMAT_RETRY') and calls[1][2] == evidence
    assert calls[0][1]['image_order'] == [c['candidate_id'] for c in candidates]
    assert all(clues['candidate_scene_clues'].values())


def test_repeated_invalid_format_stops_and_keeps_failure_evidence():
    clues, audit, calls = call_with([{}, {}])
    assert len(calls) == 2 and audit['whole_response_invalid']
    assert not any(clues['candidate_scene_clues'].values())


@pytest.mark.parametrize('error', [TimeoutError('transport'), x02.X02Error('failed')])
def test_transport_failure_has_no_module_retry_or_old_scene_fallback(error):
    clues, audit, calls = call_with([error])
    assert len(calls) == 1 and audit['failure']['type'] == type(error).__name__
    assert not any(clues['candidate_scene_clues'].values())


@pytest.mark.parametrize('code', ['HTTP_403', 'MODEL_RESPONSE_NOT_JSON'])
def test_gateway_failure_code_controls_format_retry_and_preserves_failed_stage(code):
    failed = SimpleNamespace(stage='S09A_FRAME_OBSERVATION', call_status='FAILED')
    exc = x02.X02StageCallError('fixture', stage_run=failed, code=code)
    _, _, _, output = fixture()
    stages = []
    _, audit, calls = call_with([exc, output], stage_runs=stages)
    assert len(calls) == (2 if code == 'MODEL_RESPONSE_NOT_JSON' else 1)
    assert stages == [failed] and audit['attempts'][0]['failure']['code'] == code


def test_honest_no_visible_fact_support_is_unavailable_without_retry():
    _, _, _, output = fixture()
    for row in output['images']:
        row.update(subject_role='UNRESOLVED', visibility='NOT_VISIBLE', prominence='TINY_OR_UNCLEAR')
        row['fact_checks'][0].update(support='UNCERTAIN', visible_quote='', not_visible_quote='')
    clues, audit, calls = call_with([output])
    assert len(calls) == 1 and not audit['whole_response_invalid']
    assert not any(clues['candidate_scene_clues'].values()) and not audit['frame_claim_supports']
    assert {r['status'] for r in audit['frame_ledger']} == {'UNAVAILABLE'}


@pytest.mark.parametrize('fault', ['order', 'source', 'missing'])
def test_actual_image_mapping_checked_before_any_provider_call(fault):
    candidates, facts, evidence, _ = fixture()
    if fault == 'order': evidence.reverse()
    if fault == 'source': evidence[0][0]['asset_id'] = 'foreign'
    if fault == 'missing': evidence.pop()
    def ask(*args, **kwargs): pytest.fail('must reject before a model call')
    with pytest.raises(ValueError): fo.review_frame_observations(candidates, facts, ask, evidence=evidence)


def test_empty_batch_does_not_call_provider():
    def ask(*args, **kwargs): pytest.fail('empty batch must not call model')
    _, audit = fo.review_frame_observations([], {}, ask, evidence=[])
    assert audit['attempts'] == []


def test_visible_with_exact_disjoint_absent_span_is_only_weakened_to_partial():
    candidates, facts, _, output = fixture()
    output['images'][1]['fact_checks'][0]['support'] = 'VISIBLE'
    original = deepcopy(output)
    clues, audit = fo.compile_observations(output, candidates, facts)
    clue = clues['candidate_scene_clues']['P2'][0]
    assert output == original and clue['supported_fact_ids'] == ['F1']
    assert clue['fact_supports'][0] == {**original['images'][1]['fact_checks'][0], 'support': 'PARTIAL'}
    assert clue['raw_fact_supports'] == original['images'][1]['fact_checks']
    row = next(r for r in audit['fact_check_ledger'] if r['candidate_id'] == 'P2')
    assert row['classification_normalization']['rule'] == 'EXACT_VISIBLE_AND_ABSENT_SPANS_ARE_PARTIAL'


@pytest.mark.parametrize('bad_quote', ['在铺设好的小路上...路两旁是草堤', '在铺设好的小路上，路旁有草堤'])
def test_one_invalid_fact_quote_does_not_discard_a_separate_valid_fact(bad_quote):
    candidates, facts, _, output = fixture()
    facts['F2'] = {**facts['F1'], 'text': '在铺设好的小路上骑自行车，路两旁是草堤和电线杆。'}
    candidates[1]['fact_ids'].append('F2')
    output['images'][1]['fact_checks'][0]['support'] = 'VISIBLE'  # Exact contradictory label -> PARTIAL.
    output['images'][1]['fact_checks'].append(dict(fact_id='F2', support='VISIBLE',
        visible_quote=bad_quote, not_visible_quote='骑自行车'))
    clues, audit = fo.compile_observations(output, candidates, facts)
    clue = clues['candidate_scene_clues']['P2'][0]
    assert clue['supported_fact_ids'] == ['F1']
    assert [c['fact_id'] for c in clue['fact_supports']] == ['F1']
    assert len(clue['raw_fact_supports']) == 2
    assert audit['frame_ledger'][1]['unverified_fact_ids'] == ['F2']
    assert next(c for c in audit['fact_check_ledger'] if c['fact_id'] == 'F2')['status'] == 'UNVERIFIED'
    # No malformed F2 quotation can leak into the internal writing-material ledger.
    assert audit['frame_claim_supports'][1]['fact_supports'] == clue['fact_supports']
    raw = structure(clues, 'P2')
    assert not fs.resolve_frame_selection(raw, candidates, facts, scene_clues=clues)[2]
    raw['frame_assessments'][1]['fact_ids'].append('F2')
    assert fs.resolve_frame_selection(raw, candidates, facts, scene_clues=clues)[2]


@pytest.mark.parametrize('bad_absent', ['手臂...车把', '桥面上有橙色', '未见人物'])
def test_partial_normalization_never_repairs_nonexact_or_overlapping_quotes(bad_absent):
    candidates, facts, _, output = fixture()
    output['images'][1]['fact_checks'][0].update(support='VISIBLE', not_visible_quote=bad_absent)
    clues, audit = fo.compile_observations(output, candidates, facts)
    assert not clues['candidate_scene_clues']['P2']
    assert audit['frame_ledger'][1]['status'] == 'UNVERIFIED'
    row = next(r for r in audit['fact_check_ledger'] if r['candidate_id'] == 'P2')
    assert row['status'] == 'UNVERIFIED' and 'classification_normalization' not in row
