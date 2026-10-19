"""Reference/ranking regressions, not a claim of model visual accuracy."""
from copy import deepcopy

import jsonschema
import pytest

from diary_one_ci.frame_selection import (
    FRAME_SELECTION_PROMPT, augment_frame_selection_schema,
    frame_selection_context, resolve_frame_selection as resolve_actual,
    scene_clues_from_visual_outputs,
)


# Independently specified scripted SCENE observations, not generated from the
# judgment under test. An altered image description must therefore fail binding.
SCENE_TEXTS = {
    'P1': ['前景手臂遮挡远处桥梁。', '桥梁主体清晰可辨。', '整洁的周边环境。'],
    'P2': ['桥梁主体清晰可辨。', '一只动物静静伏在枝条上。', '展柜内器物的纹路清晰可见。'],
    'P3': ['路边花墙清晰。'],
    'P4': ['路边雕塑完整可见。', '花墙主体更完整。'],
}


def fixture_clues(candidates):
    return {'candidate_scene_clues': {c['candidate_id']: [
        dict(scene_observation_id=c['candidate_id'] + ':' + str(index), text=text,
             asset_id=c['asset_id'], evidence_frame_ids=[c['frame_id']])
        for index, text in enumerate(SCENE_TEXTS.get(c['candidate_id'], []))] for c in candidates}}


def resolve_frame_selection(output, candidates, facts):
    return resolve_actual(output, candidates, facts, scene_clues=fixture_clues(candidates))


def inputs():
    facts = {
        'F1': dict(asset_id='V1', text='移动视角前方有桥梁。', evidence_frame_ids=['f0', 'f1']),
        'F2': dict(asset_id='V2', text='路边有一面花墙。', evidence_frame_ids=['f2']),
    }
    candidates = [dict(candidate_id=pid, asset_id=aid, frame_id=frame, fact_ids=[fid])
                  for pid, aid, frame, fid in [('P1', 'V1', 'f0', 'F1'),
                      ('P2', 'V1', 'f1', 'F1'), ('P3', 'V2', 'f2', 'F2')]]
    return candidates, facts


def assessment(pid, refs, *, fit='MAIN_SUBJECT', visibility='CLEAR', prominence='READABLE',
               occlusion='NONE', detail='桥梁主体清晰可辨。'):
    quote_id = (pid + ':' + str(SCENE_TEXTS.get(pid, []).index(detail))) if detail in SCENE_TEXTS.get(pid, []) else None
    return dict(candidate_id=pid, fact_ids=refs, scene_observation_id=quote_id, visible_detail=detail,
                theme_fit=fit, visibility=visibility, prominence=prominence, occlusion=occlusion)


def output(hero='P2'):
    return dict(chapters=[dict(id='C1', fact_ids=['F1', 'F2'], focus_fact_ids=['F1'],
                              hero_candidate_id=hero)],
        media_choices=[dict(chapter_id='C1', candidate_id=hero, reason='呈现本章主体。'),
                       dict(chapter_id='C1', candidate_id='P3', reason='补充路边细节。')],
        frame_assessments=[
            assessment('P1', ['F1'], fit='SUPPORTING_CONTEXT', visibility='PARTIAL',
                       prominence='TINY_OR_UNCLEAR', occlusion='DOMINANT', detail='前景手臂遮挡远处桥梁。'),
            assessment('P2', ['F1']),
            assessment('P3', ['F2'], fit='SUPPORTING_CONTEXT', detail='路边花墙清晰。')],
        moments=[], unselected_facts=[])


def test_multiframe_fact_does_not_make_every_frame_an_equal_cover():
    candidates, facts = inputs()
    raw = output('P1')
    before = deepcopy(raw)
    clean, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert raw == before and 'frame_assessments' not in clean
    assert audit['automatic_replacements'] == []
    assert not issues and audit['preference_warnings']
    assert any(c['stronger_candidate_ids'] == ['P2'] for c in audit['comparisons'])
    # P2 was displayed but not nominated in media_choices: comparison still uses it.
    assert 'P2' not in [c['candidate_id'] for c in raw['media_choices']]
    clean, audit, issues = resolve_frame_selection(output(), candidates, facts)
    assert not issues and audit['status'] == 'REFERENCE_AND_RELATIVE_DECISION_VALIDATED'
    assert clean['chapters'][0]['hero_candidate_id'] == 'P2'


@pytest.mark.parametrize('detail', ['一只动物静静伏在枝条上。', '展柜内器物的纹路清晰可见。'])
def test_static_subject_outranks_pretty_context_without_a_motion_requirement(detail):
    candidates, facts = inputs()
    raw = output('P1')
    raw['frame_assessments'][0] = assessment('P1', ['F1'], fit='SUPPORTING_CONTEXT',
        prominence='DOMINANT', detail='整洁的周边环境。')
    raw['frame_assessments'][1] = assessment('P2', ['F1'], visibility='PARTIAL', detail=detail)
    assert resolve_frame_selection(raw, candidates, facts)[1]['preference_warnings']
    assert not resolve_frame_selection(raw, candidates, facts)[2]
    raw['chapters'][0]['hero_candidate_id'] = 'P2'
    raw['media_choices'][0]['candidate_id'] = 'P2'
    assert not resolve_frame_selection(raw, candidates, facts)[2]


def test_unrelated_chapter_fact_is_not_a_cross_asset_cover_competitor():
    candidates, facts = inputs()
    raw = output()
    raw['frame_assessments'][2].update(prominence='DOMINANT')
    _, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert not issues
    focused = next(c for c in audit['comparisons'] if c['scope'] == 'DIRECT_FOCUS_FACT_SUPPORT')
    assert 'P3' not in focused['compared_candidate_ids']
    raw['frame_assessments'][2]['theme_fit'] = 'MAIN_SUBJECT'
    original = deepcopy(raw)
    _, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert not issues and raw == original
    assert audit['classification_normalizations'] == [dict(chapter_id='C1', candidate_id='P3',
        rule='CHAPTER_FACT_WITHOUT_FOCUS_REFERENCE_IS_CONTEXT', raw_theme_fit='MAIN_SUBJECT',
        effective_theme_fit='SUPPORTING_CONTEXT', fact_ids=['F2'], focus_fact_ids=['F1'])]
    assert next(a for a in audit['assessments'] if a['candidate_id'] == 'P3')['theme_fit'] == 'MAIN_SUBJECT'


def test_unselected_main_tag_outside_focus_does_not_discard_supported_cover():
    candidates, facts = inputs()
    raw = output()
    raw['media_choices'].pop()  # P3 belongs to chapter, but is not selected.
    raw['frame_assessments'][2]['theme_fit'] = 'MAIN_SUBJECT'
    clean, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert not issues and clean['chapters'][0]['hero_candidate_id'] == 'P2'
    assert audit['classification_normalizations'][0]['candidate_id'] == 'P3'
    assert audit['automatic_replacements'] == []


def test_normalized_nonfocus_cover_still_loses_to_directly_supported_subject():
    candidates, facts = inputs()
    raw = output()
    raw['chapters'][0]['hero_candidate_id'] = 'P3'
    raw['frame_assessments'][2].update(theme_fit='MAIN_SUBJECT', prominence='DOMINANT')
    _, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert not issues and audit['classification_normalizations'] and audit['preference_warnings']
    focused = next(c for c in audit['comparisons'] if c['scope'] == 'DIRECT_FOCUS_FACT_SUPPORT')
    assert focused['stronger_candidate_ids'] == ['P2']


def test_different_same_asset_details_can_be_complementary_gallery_choices():
    candidates, facts = inputs()
    facts['F3'] = dict(asset_id='V2', text='路边有小型雕塑。', evidence_frame_ids=['f3'])
    candidates.append(dict(candidate_id='P4', asset_id='V2', frame_id='f3', fact_ids=['F3']))
    raw = output()
    raw['chapters'][0]['fact_ids'].append('F3')
    raw['frame_assessments'].append(assessment('P4', ['F3'], fit='SUPPORTING_CONTEXT',
        prominence='DOMINANT', detail='路边雕塑完整可见。'))
    _, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert not issues
    gallery = next(c for c in audit['comparisons'] if c['role'] == 'GALLERY')
    assert gallery['compared_candidate_ids'] == ['P3']


def test_gallery_same_visible_fact_compares_all_shown_alternatives():
    candidates, facts = inputs()
    facts['F2']['evidence_frame_ids'].append('f3')
    candidates.append(dict(candidate_id='P4', asset_id='V2', frame_id='f3', fact_ids=['F2']))
    raw = output()
    raw['frame_assessments'].append(assessment('P4', ['F2'], fit='SUPPORTING_CONTEXT',
        prominence='DOMINANT', detail='花墙主体更完整。'))
    # Same observation, independently attached to both frames, supports a
    # comparison. A shared clip fact alone would not.
    clues = fixture_clues(candidates)
    clues['candidate_scene_clues']['P4'][1]['text'] = '路边花墙清晰。'
    raw['frame_assessments'][-1]['visible_detail'] = '路边花墙清晰。'
    _, audit, issues = resolve_actual(raw, candidates, facts, scene_clues=clues)
    assert not issues and audit['preference_warnings']
    gallery = next(c for c in audit['comparisons'] if c['role'] == 'GALLERY')
    assert gallery['stronger_candidate_ids'] == ['P4']


def test_ties_do_not_force_first_candidate_or_automatic_replacement():
    candidates, facts = inputs()
    raw = output()
    raw['frame_assessments'][0] = assessment('P1', ['F1'])
    for hero in ('P1', 'P2'):
        raw['chapters'][0]['hero_candidate_id'] = hero
        raw['media_choices'][0]['candidate_id'] = hero
        _, audit, issues = resolve_frame_selection(raw, candidates, facts)
        assert not issues and audit['automatic_replacements'] == []


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'foreign_fact', 'invalid_category',
                                     'contradiction', 'empty_detail', 'extra_field'])
def test_bad_known_frame_judgments_only_mark_affected_chapter(mutation):
    candidates, facts = inputs()
    raw = output('P1')
    raw['chapters'][0]['fact_ids'] = ['F1']
    raw['chapters'].append(dict(id='C2', fact_ids=['F2'], focus_fact_ids=['F2'], hero_candidate_id='P3'))
    raw['media_choices'][1]['chapter_id'] = 'C2'
    raw['frame_assessments'][2]['theme_fit'] = 'MAIN_SUBJECT'
    if mutation == 'missing': raw['frame_assessments'].pop(0)
    if mutation == 'duplicate': raw['frame_assessments'].append(deepcopy(raw['frame_assessments'][0]))
    if mutation == 'foreign_fact': raw['frame_assessments'][0]['fact_ids'] = ['F2']
    if mutation == 'invalid_category': raw['frame_assessments'][0]['prominence'] = 'BEAUTIFUL'
    if mutation == 'contradiction': raw['frame_assessments'][0]['visibility'] = 'NOT_VISIBLE'
    if mutation == 'empty_detail': raw['frame_assessments'][0]['visible_detail'] = '  '
    if mutation == 'extra_field': raw['frame_assessments'][0]['score'] = 99
    _, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert issues and {i['item'] for i in issues} == {'C1'}
    assert any(c['chapter_id'] == 'C2' for c in audit['comparisons'])


def test_unknown_candidate_and_missing_overall_assessments_are_not_invented():
    candidates, facts = inputs()
    raw = output()
    del raw['frame_assessments']
    assert resolve_frame_selection(raw, candidates, facts)[2][0]['item'] == 'frame_assessments'
    raw = output()
    raw['frame_assessments'].append(assessment('P999', ['F1']))
    assert {i['item'] for i in resolve_frame_selection(raw, candidates, facts)[2]} == {'frame_assessments:unknown_row_3'}


def test_unassigned_candidate_issue_does_not_claim_an_unrelated_chapter_failed():
    candidates, facts = inputs()
    raw = output()
    raw['chapters'][0]['fact_ids'] = ['F1']
    raw['media_choices'].pop()
    raw['frame_assessments'].pop()
    assert {i['item'] for i in resolve_frame_selection(raw, candidates, facts)[2]} == {'frame_assessments:P3'}


@pytest.mark.parametrize('fault', ['missing', 'forged_quote', 'duplicate'])
def test_bad_unselected_alternative_neither_blocks_supported_chapter_nor_competes(fault):
    candidates, facts = inputs()
    raw = output()  # P2 is the selected hero; P1 is only an alternative.
    if fault == 'missing': raw['frame_assessments'].pop(0)
    elif fault == 'forged_quote': raw['frame_assessments'][0]['visible_detail'] = '不存在的主体。'
    else: raw['frame_assessments'].append(deepcopy(raw['frame_assessments'][0]))
    _, audit, issues = resolve_frame_selection(raw, candidates, facts)
    assert {i['item'] for i in issues} == {'frame_assessments:P1'}
    assert audit['comparisons'] and all('P1' not in c['compared_candidate_ids'] for c in audit['comparisons'])


def test_unseen_subject_cannot_be_selected_but_does_not_require_a_chapter():
    candidates, facts = inputs()
    raw = output()
    raw['frame_assessments'] = [assessment(c['candidate_id'], [], fit='UNSUPPORTED',
        visibility='NOT_VISIBLE', prominence='TINY_OR_UNCLEAR', detail='') for c in candidates]
    assert resolve_frame_selection(raw, candidates, facts)[2]
    raw.update(chapters=[], media_choices=[])
    assert not resolve_frame_selection(raw, candidates, facts)[2]  # May have independent Aha.


@pytest.mark.parametrize('mutation', ['cross_asset', 'foreign_frame', 'duplicate_image'])
def test_trusted_table_must_bind_fact_to_actual_asset_and_frame(mutation):
    candidates, facts = inputs()
    if mutation == 'cross_asset': candidates[0]['asset_id'] = 'V2'
    if mutation == 'foreign_frame': candidates[0]['frame_id'] = 'f999'
    if mutation == 'duplicate_image': candidates[1]['frame_id'] = 'f0'
    with pytest.raises(ValueError):
        frame_selection_context(candidates, facts)


def test_dynamic_schema_and_context_are_exact_and_leave_original_inputs_unchanged():
    candidates, facts = inputs()
    base = dict(type='object', properties={'chapters': {'type': 'array'}}, required=['chapters'])
    original = deepcopy((base, candidates, facts))
    schema = augment_frame_selection_schema(base, candidates, facts, scene_clues=fixture_clues(candidates))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(output(), schema)
    raw = output()
    raw['frame_assessments'][0]['fact_ids'] = ['F2']
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(raw, schema)
    context = frame_selection_context(candidates, facts)
    assert context['same_asset_candidate_groups'][0] == dict(asset_id='V1', candidate_ids=['P1', 'P2'])
    assert context['candidate_fact_allowlist']['P1'] == ['F1']
    assert (base, candidates, facts) == original
    assert '未知同伴' in FRAME_SELECTION_PROMPT and '连续路线' in FRAME_SELECTION_PROMPT


def test_empty_candidate_batch_is_supported_without_fake_frames():
    base = dict(type='object', properties={}, required=[])
    schema = augment_frame_selection_schema(base, [], {})
    jsonschema.validate(dict(frame_assessments=[]), schema)
    assert not resolve_frame_selection(dict(chapters=[], media_choices=[], frame_assessments=[]), [], {})[2]


def independent_scene_fixture(candidates):
    return [{'stage': 'INDEPENDENT_SCENE', 'accepted_scenes': [
        dict(asset_id='V1', observations=[
            dict(text='前景手臂遮挡远处桥梁。', evidence_frame_ids=['f0'], temporal_support='STATE'),
            dict(text='桥梁主体清晰可辨。', evidence_frame_ids=['f1'], temporal_support='STATE')]),
        dict(asset_id='V2', observations=[
            dict(text='路边花墙清晰。', evidence_frame_ids=['f2'], temporal_support='STATE')])]}]


def scene_bound_output(candidates, facts):
    clues = scene_clues_from_visual_outputs(independent_scene_fixture(candidates), candidates, facts)
    raw = output()
    for row in raw['frame_assessments']:
        clue = clues['candidate_scene_clues'][row['candidate_id']][0]
        row.update(scene_observation_id=clue['scene_observation_id'], visible_detail=clue['text'])
    return raw, clues


@pytest.mark.parametrize('fault', ['quote_another_frame', 'append_clip_claim', 'same_frame_wrong_quote_id',
                                  'borrow_foreign_asset', 'omit_quote_identity'])
def test_multiframe_fact_cannot_transfer_subject_from_another_frames_scene(fault):
    candidates, facts = inputs()
    raw, clues = scene_bound_output(candidates, facts)
    assert not resolve_actual(raw, candidates, facts, scene_clues=clues)[2]
    raw['chapters'][0]['hero_candidate_id'] = 'P1'
    raw['media_choices'][0]['candidate_id'] = 'P1'
    row = raw['frame_assessments'][0]
    if fault == 'quote_another_frame':
        row.update(scene_observation_id=raw['frame_assessments'][1]['scene_observation_id'],
                   visible_detail=raw['frame_assessments'][1]['visible_detail'])
    elif fault == 'append_clip_claim':
        row['visible_detail'] += '桥梁主体清晰可辨。'
    elif fault == 'same_frame_wrong_quote_id':
        row['visible_detail'] = raw['frame_assessments'][1]['visible_detail']
    elif fault == 'borrow_foreign_asset':
        row.update(scene_observation_id=raw['frame_assessments'][2]['scene_observation_id'],
                   visible_detail=raw['frame_assessments'][2]['visible_detail'])
    else:
        row['scene_observation_id'] = None
    # Both P1/P2 cite F1. The allowed multi-frame fact is insufficient: quote
    # identity must independently bind to exactly the displayed candidate.
    assert raw['frame_assessments'][0]['fact_ids'] == raw['frame_assessments'][1]['fact_ids'] == ['F1']
    _, _, issues = resolve_actual(raw, candidates, facts, scene_clues=clues)
    assert issues and {i['item'] for i in issues} == {'C1'}


def test_scene_index_uses_only_prevalidated_observations_not_raw_model_answer():
    candidates, facts = inputs()
    raw, _ = scene_bound_output(candidates, facts)
    packets = independent_scene_fixture(candidates)
    packets[0]['output'] = {'assets': packets[0].pop('accepted_scenes')}
    clues = scene_clues_from_visual_outputs(packets, candidates, facts)
    assert all(not rows for rows in clues['candidate_scene_clues'].values())
    assert clues['issues']
    assert resolve_actual(raw, candidates, facts, scene_clues=clues)[2]
    assert resolve_actual(raw, candidates, facts)[2]  # No optional permissive path.


def test_missing_scene_for_selected_frame_fails_closed_without_erasing_other_chapter():
    candidates, facts = inputs()
    raw, clues = scene_bound_output(candidates, facts)
    raw['chapters'][0]['fact_ids'] = ['F1']
    raw['chapters'].append(dict(id='C2', fact_ids=['F2'], focus_fact_ids=['F2'], hero_candidate_id='P3'))
    raw['media_choices'][1]['chapter_id'] = 'C2'
    raw['frame_assessments'][2]['theme_fit'] = 'MAIN_SUBJECT'
    clues['candidate_scene_clues']['P2'] = []
    _, audit, issues = resolve_actual(raw, candidates, facts, scene_clues=clues)
    assert {i['item'] for i in issues} == {'C1'}
    assert audit['candidates_without_scene_clues'] == ['P2']
    assert any(c['chapter_id'] == 'C2' for c in audit['comparisons'])


def test_unavailable_scene_may_be_declined_but_cannot_be_a_selected_picture():
    candidates, facts = inputs()
    raw, clues = scene_bound_output(candidates, facts)
    clues['candidate_scene_clues']['P1'] = []
    raw['frame_assessments'][0] = assessment('P1', [], fit='UNSUPPORTED',
        visibility='NOT_VISIBLE', prominence='TINY_OR_UNCLEAR', detail='')
    assert not resolve_actual(raw, candidates, facts, scene_clues=clues)[2]
    raw['chapters'][0]['hero_candidate_id'] = 'P1'
    raw['media_choices'][0]['candidate_id'] = 'P1'
    assert resolve_actual(raw, candidates, facts, scene_clues=clues)[2]


def test_scene_quote_schema_rejects_matching_text_from_wrong_candidate():
    candidates, facts = inputs()
    raw, clues = scene_bound_output(candidates, facts)
    schema = augment_frame_selection_schema(dict(type='object', properties={}, required=[]),
        candidates, facts, scene_clues=clues)
    jsonschema.validate(raw, schema)
    raw['frame_assessments'][0].update(scene_observation_id=raw['frame_assessments'][1]['scene_observation_id'],
        visible_detail=raw['frame_assessments'][1]['visible_detail'])
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(raw, schema)


def test_shared_scene_observation_retains_its_explicit_frame_scope_without_fabricated_precision():
    candidates, facts = inputs()
    packets = independent_scene_fixture(candidates)
    packets[0]['accepted_scenes'][0]['observations'][0]['evidence_frame_ids'] = ['f0', 'f1']
    clues = scene_clues_from_visual_outputs(packets, candidates, facts)
    shared = clues['candidate_scene_clues']['P1'][0]
    assert shared in clues['candidate_scene_clues']['P2']
    assert shared['evidence_frame_ids'] == ['f0', 'f1']
    assert 'NOT_VISUAL_GROUND_TRUTH' in clues['evidence_scope']
