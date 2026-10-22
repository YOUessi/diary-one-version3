"""Local selection-reason regressions; recorded output is not visual ground truth."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from diary_one_ci import product_editor as p
from diary_one_ci import frame_observation


def recorded():
    return json.loads((Path(__file__).parent / 'fixtures/product_media_explanation_nagoya_v071.json').read_text())


def repair(data):
    return p.repair_media_explanations(data['output'], data['facts'], data['assets'],
        data['candidates'], data['shown'], scene_clues=data['scene_clues'])


def test_real_nagoya_reason_repairs_only_to_exact_single_frame_observation():
    data = recorded(); original = deepcopy(data)
    chapters, _, issues, _, audit = p.compile_assessed_structure(
        data['output'], data['facts'], data['assets'], 4, candidates=data['candidates'],
        shown_frames=data['shown'], scene_clues=data['scene_clues'])
    assert not issues and len(chapters) == 1 and data == original
    records = audit['selection_explanation_repairs']
    assert len(records) == 1 and records[0]['candidate_id'] == 'P002'
    assert records[0]['raw_reason'] == '呈现路边草地上的同伴身影，作为有证据的沿途人物细节，丰富骑行叙事。'
    assert records[0]['unsupported_terms'] == ['同伴']
    assert records[0]['action'] == 'REPLACED_WITH_VERIFIED_SINGLE_FRAME_SCENE'
    assert records[0]['scene_observation_id'] == 'SC003'
    assert records[0]['evidence_frame_ids'] == ['asset-1-f0']
    chosen = next(c for c in chapters[0]['media_choices'] if c['asset_id'] == 'V002')
    assert chosen['reason'] == records[0]['replacement_reason']
    assert chosen['frame_id'] == 'asset-1-f0'
    assert chapters[0]['hero_frame_id'] == next(c['frame_id'] for c in data['candidates']
        if c['candidate_id'] == data['output']['chapters'][0]['hero_candidate_id'])


@pytest.mark.parametrize('change', ['missing', 'wrong_frame', 'multiple_frames', 'wrong_asset', 'changed_quote', 'unsupported_scene'])
def test_untrusted_gallery_explanation_is_removed_without_guessing_a_picture(change):
    data = recorded(); clues = data['scene_clues']['candidate_scene_clues']['P002']
    if change == 'missing': clues.clear()
    elif change == 'wrong_frame': clues[0]['evidence_frame_ids'] = ['asset-4-f0']
    elif change == 'multiple_frames': clues[0]['evidence_frame_ids'].append('asset-1-f1')
    elif change == 'wrong_asset': clues[0]['asset_id'] = 'V005'
    elif change == 'changed_quote': clues[0]['text'] = '自行车在草地上。'
    elif change == 'unsupported_scene':
        clues[0]['text'] = '同伴跨坐在自行车上。'
        next(a for a in data['output']['frame_assessments'] if a['candidate_id'] == 'P002')['visible_detail'] = clues[0]['text']
    hero = data['output']['chapters'][0]['hero_candidate_id']
    clean, audit, issues = repair(data)
    assert not issues and len(clean['chapters']) == 1
    assert clean['chapters'][0]['hero_candidate_id'] == hero
    assert 'P002' not in [r['candidate_id'] for r in clean['media_choices']]
    assert audit[0]['action'] == 'REMOVED_GALLERY_WITHOUT_SINGLE_FRAME_SCENE'
    assert audit[0]['replacement_reason'] is None


@pytest.mark.parametrize('change', ['foreign_frame', 'wrong_fact', 'duplicate_candidate', 'unknown_candidate'])
def test_bad_bindings_cannot_escape_as_explanation_cleanup(change):
    data = recorded()
    if change == 'foreign_frame':
        next(c for c in data['candidates'] if c['candidate_id'] == 'P002')['frame_id'] = 'asset-4-f0'
    elif change == 'wrong_fact':
        next(c for c in data['candidates'] if c['candidate_id'] == 'P002')['fact_ids'] = ['F001']
    elif change == 'duplicate_candidate':
        data['output']['media_choices'].append(deepcopy(next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')))
    else:
        next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')['candidate_id'] = 'P999'
    clean, audit, _ = repair(data)
    assert clean == data['output'] and not audit


def test_unrepairable_hero_blocks_its_own_chapter_without_new_cover_or_losing_other_chapter():
    data = recorded(); raw = data['output']; chapter = raw['chapters'][0]
    chapter['hero_candidate_id'] = 'P002'
    data['scene_clues']['candidate_scene_clues']['P002'].clear()
    # A genuinely independent chapter and explicit valid boundary survive.
    second = deepcopy(chapter)
    second.update(id='C02', fact_ids=['F004'], focus_fact_ids=['F004'], hero_candidate_id='P003')
    chapter['fact_ids'].remove('F004')
    chapter['focus_fact_ids'] = [f for f in chapter['focus_fact_ids'] if f != 'F004']
    raw['chapters'].append(second)
    raw['chapter_boundaries'] = [dict(chapter_ids=['C01', 'C02'], basis='DIFFERENT_ACTIVITY',
        evidence_fact_ids=['F003', 'F004'], reason='Independent fixture activities')]
    raw['media_choices'] = [r for r in raw['media_choices'] if r['candidate_id'] != 'P003']
    raw['media_choices'].append(dict(chapter_id='C02', candidate_id='P003', reason='呈现有依据的树木与小路。'))
    clean, audit, issues = repair(data)
    assert [c['id'] for c in clean['chapters']] == ['C02']
    assert clean['chapters'][0]['hero_candidate_id'] == 'P003'
    assert clean['chapter_boundaries'] == []
    assert all(row['chapter_id'] == 'C02' for row in clean['media_choices'])
    assert audit[0]['action'] == 'BLOCKED_HERO_WITHOUT_SINGLE_FRAME_SCENE'
    assert any(issue['item'] == 'C01' for issue in issues)
    assert not any(issue['item'] == 'C02' for issue in issues)
    compiled, _, rejected, _, _ = p.compile_assessed_structure(raw, data['facts'], data['assets'], 4,
        candidates=data['candidates'], shown_frames=data['shown'], scene_clues=data['scene_clues'])
    assert [c['id'] for c in compiled] == ['C02']
    assert not any(issue['item'] == 'C02' for issue in rejected)


def test_gallery_removal_preserves_chapter_with_valid_but_not_single_frame_scene():
    data = recorded()
    data['scene_clues']['candidate_scene_clues']['P002'][0]['evidence_frame_ids'].append('asset-1-f1')
    compiled, _, issues, _, audit = p.compile_assessed_structure(
        data['output'], data['facts'], data['assets'], 4, candidates=data['candidates'],
        shown_frames=data['shown'], scene_clues=data['scene_clues'])
    assert not issues and len(compiled) == 1
    assert 'V002' not in compiled[0]['selected_asset_ids']
    assert 'F003' in compiled[0]['fact_ids']  # Only the gallery proposal was removed.
    assert audit['selection_explanation_repairs'][0]['action'] == 'REMOVED_GALLERY_WITHOUT_SINGLE_FRAME_SCENE'


def test_empty_or_unknown_reason_is_not_filled_from_a_scene():
    data = recorded()
    next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')['reason'] = ''
    clean, audit, _ = repair(data)
    assert clean == data['output'] and not audit


def dedicated_fixture():
    """Explicit synthetic FO attached to the recorded valid P002 binding."""
    data = recorded()
    candidate = next(c for c in data['candidates'] if c['candidate_id'] == 'P002')
    fids = candidate['fact_ids']
    assert len(fids) == 1
    text = data['facts'][fids[0]]['text']
    output = {'images': [dict(candidate_id='P002', observation=text, subject_role='SPECIFIC_SUBJECT',
        visibility='CLEAR', prominence='READABLE', occlusion='NONE',
        fact_checks=[dict(fact_id=fids[0], support='VISIBLE', visible_quote=text, not_visible_quote='')])]}
    clues, audit = frame_observation.compile_observations(output, [candidate], data['facts'])
    assert audit['frame_ledger'][0]['status'] == 'VERIFIED_REFERENCE_SCOPE'
    data['scene_clues']['candidate_scene_clues']['P002'] = clues['candidate_scene_clues']['P002']
    assessment = next(a for a in data['output']['frame_assessments'] if a['candidate_id'] == 'P002')
    assessment.update(scene_observation_id='FO:P002', visible_detail=text,
        fact_ids=fids, theme_fit='MAIN_SUBJECT', visibility='CLEAR', prominence='READABLE', occlusion='NONE')
    row = next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')
    row['reason'] = '骑行队伍的默契配合让此图更有故事性。'
    return data


@pytest.mark.parametrize('reason', ['骑行队伍的默契配合让此图更有故事性。',
                                   '这张图记录了今日挑战的终点。', '主体清晰，适合作为补图。'])
def test_every_dedicated_reason_is_exact_observation_without_a_keyword_trigger(reason):
    data = dedicated_fixture()
    raw = next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')
    raw['reason'] = reason
    original = deepcopy(data)
    assert not p.unsupported_editorial_context(reason, ['F003'], data['facts'])
    clean, audit, issues = repair(data)
    chosen = next(r for r in clean['media_choices'] if r['candidate_id'] == 'P002')
    observation = data['scene_clues']['candidate_scene_clues']['P002'][0]
    assert not issues and data == original
    assert chosen['reason'] == observation['text'] and chosen['reason'] != reason
    assert audit == [dict(chapter_id='C01', candidate_id='P002', asset_id='V002', frame_id='asset-1-f0',
        fact_ids=['F003'], raw_reason=reason, unsupported_terms=[], reason_policy='EXACT_DEDICATED_FRAME_OBSERVATION',
        action='CANONICALIZED_TO_DEDICATED_FRAME_OBSERVATION', replacement_reason=observation['text'],
        scene_observation_id='FO:P002', evidence_frame_ids=['asset-1-f0'])]


def test_unchanged_dedicated_reason_is_still_audited_and_legacy_safe_reason_untouched():
    data = dedicated_fixture()
    raw = next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')
    raw['reason'] = data['scene_clues']['candidate_scene_clues']['P002'][0]['text']
    clean, audit, issues = repair(data)
    assert clean == data['output'] and not issues and len(audit) == 1
    assert audit[0]['raw_reason'] == audit[0]['replacement_reason']
    data = recorded()
    next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')['reason'] = '主体清晰，适合作为补图。'
    clean, audit, issues = repair(data)
    assert clean == data['output'] and not audit and not issues


@pytest.mark.parametrize('fault', ['foreign_quote', 'wrong_supported_fact', 'unresolved', 'missing_fact_checks',
                                  'wrong_frame', 'wrong_asset', 'cross_frame', 'wrong_observation_id',
                                  'altered_observation', 'borrow_nonvisible_fact'])
def test_dedicated_provenance_alone_cannot_authorize_a_public_reason(fault):
    data = dedicated_fixture()
    clue = data['scene_clues']['candidate_scene_clues']['P002'][0]
    if fault == 'foreign_quote': clue['fact_supports'][0]['visible_quote'] = '一个不在原事实中的动作'
    elif fault == 'wrong_supported_fact': clue['supported_fact_ids'] = ['F001']
    elif fault == 'unresolved': clue['subject_role'] = 'UNRESOLVED'
    elif fault == 'missing_fact_checks': clue.pop('fact_supports')
    elif fault == 'wrong_frame': clue['evidence_frame_ids'] = ['asset-4-f0']
    elif fault == 'wrong_asset': clue['asset_id'] = 'V005'
    elif fault == 'cross_frame': clue['evidence_frame_ids'].append('asset-1-f1')
    elif fault == 'wrong_observation_id': clue['scene_observation_id'] = 'FO:P009'
    elif fault == 'altered_observation': clue['text'] += '同伴'
    else:
        clue['fact_supports'][0].update(support='NOT_VISIBLE', visible_quote='', not_visible_quote='')
    clean, audit, issues = repair(data)
    assert not issues and 'P002' not in [r['candidate_id'] for r in clean['media_choices']]
    assert audit[0]['action'] == 'REMOVED_GALLERY_WITHOUT_SINGLE_FRAME_SCENE'
    assert not audit[0]['replacement_reason']


def test_dedicated_canonicalization_cannot_hide_bad_candidate_binding_or_empty_reason():
    for fault in ('wrong_frame', 'wrong_fact', 'empty_reason'):
        data = dedicated_fixture()
        candidate = next(c for c in data['candidates'] if c['candidate_id'] == 'P002')
        if fault == 'wrong_frame': candidate['frame_id'] = 'asset-4-f0'
        elif fault == 'wrong_fact': candidate['fact_ids'] = ['F001']
        else: next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P002')['reason'] = ''
        clean, audit, _ = repair(data)
        assert clean == data['output'] and not audit
