"""Regressions derived from the Sydney run; not visual accuracy measurements."""
from copy import deepcopy

import pytest

from diary_one_ci import final_copy_evidence as e
from diary_one_ci import narrative_focus as n
from diary_one_ci import product_editor as p
from test_final_copy_evidence import inputs, memory
from test_product_failure_isolation import fixture


def claim_context(item, frame_ids):
    fact = {**item['facts'][0], 'evidence_frame_ids': frame_ids}
    return {'id': item['id'], 'kind': 'CHAPTER', 'title': 'A supported landmark',
            'title_fact_ids': [fact['id']], 'title_evidence': [fact], 'sentence_checks': []}


def test_late_referenced_image_survives_large_directory_and_only_that_image_is_sent(tmp_path):
    assets, bundle = inputs(tmp_path, 1)
    assets['V0']['media_kind'] = 'VIDEO'
    item = memory(frames=[f'f{i}' for i in range(30)])
    evidence, scope = e.build_final_copy_scope([item], assets, bundle, max_frames=None)
    plan = e.build_final_claim_batches([claim_context(item, ['f29'])], evidence, scope)
    assert len(evidence) == 30
    assert not scope['memories'][0]['unshown_refs']
    assert len(plan['batches']) == 1
    assert [frame['frame_id'] for _, frame, _ in plan['batches'][0]['evidence']] == ['f29']


def test_large_directory_does_not_allow_one_claim_to_send_over_24_images(tmp_path):
    assets, bundle = inputs(tmp_path, 1)
    assets['V0']['media_kind'] = 'VIDEO'
    item = memory(frames=[f'f{i}' for i in range(30)])
    evidence, scope = e.build_final_copy_scope([item], assets, bundle, max_frames=None)
    plan = e.build_final_claim_batches([claim_context(item, [f'f{i}' for i in range(25)])], evidence, scope)
    assert not plan['batches']
    assert plan['claims'][0]['status'] == 'NOT_EVALUATED'
    assert plan['claims'][0]['reason'] == 'CLAIM_IMAGE_BUDGET_EXCEEDED'


def anchored_inputs():
    facts = {
        'F1': {'id': 'F1', 'asset_id': 'V1', 'text': '海边可见歌剧院，字幕为Opera House。',
               'support_grade': 'STRONG', 'frame_pts_ms': [1000], 'visual_reviewed': True,
               'evidence_frame_ids': ['opera']},
        'F2': {'id': 'F2', 'asset_id': 'V2', 'text': '渡轮正在行驶。',
               'support_grade': 'STRONG', 'frame_pts_ms': [1000], 'visual_reviewed': True,
               'evidence_frame_ids': ['ferry']}}
    chapter = {'id': 'C1', 'theme': '海港地标漫步', 'fact_ids': ['F1', 'F2'],
               'selection_focus': {'experience_kind': 'CITYWALK', 'focus': '歌剧院和海港', 'fact_ids': ['F1', 'F2']},
               'hero_asset_id': 'V1', 'hero_frame_id': 'opera', 'media_choices': [
                   {'asset_id': 'V1', 'frame_id': 'opera', 'fact_ids': ['F1']},
                   {'asset_id': 'V2', 'frame_id': 'ferry', 'fact_ids': ['F2']}]}
    return chapter, facts


def anchored_memory():
    chapter, facts = anchored_inputs()
    return p.memory_specs([chapter], [], facts)[0]


def test_writer_receives_original_theme_and_whole_hero_fact_despite_caption_only_excerpt():
    item = anchored_memory()
    original = deepcopy(item)
    brief = {'narrative_details': [
        {'fact_id': 'F1', 'evidence_quote': '字幕为Opera House', 'role': 'SUPPORT'},
        {'fact_id': 'F2', 'evidence_quote': '渡轮正在行驶', 'role': 'MAIN'}]}
    context = n.writing_context(item, brief)
    anchor = context.get('chapter_anchor', {})
    assert anchor.get('theme') == '海港地标漫步'
    assert anchor.get('hero_frame_id') == 'opera'
    assert anchor.get('hero_fact_ids') == ['F1']
    assert next(f['text'] for f in anchor['facts'] if f['id'] == 'F1') == '海边可见歌剧院，字幕为Opera House。'
    assert item == original


def test_chapter_anchor_cannot_authorize_an_unselected_or_foreign_fact():
    chapter, facts = anchored_inputs()
    facts['F3'] = {**facts['F1'], 'id': 'F3', 'asset_id': 'V3',
                   'evidence_frame_ids': ['unselected'], 'text': '未选中的素材。'}
    facts['F4'] = {**facts['F1'], 'id': 'F4', 'text': '不属于本章的事实。'}
    facts['F5'] = {**facts['F1'], 'id': 'F5', 'visual_reviewed': False,
                   'text': '未完成图像审核的事实。'}
    chapter['fact_ids'] += ['F3', 'F5']
    chapter['selection_focus']['fact_ids'] += ['F3', 'F4', 'F5']
    chapter['media_choices'][0]['fact_ids'] += ['F4', 'F5']
    item = p.memory_specs([chapter], [], facts)[0]
    anchor = item.get('chapter_anchor', {})
    assert {f['id'] for f in anchor.get('facts', [])} == {'F1', 'F2'}
    assert anchor.get('hero_fact_ids') == ['F1']


def test_original_supported_cover_wins_over_more_body_mentions_of_another_picture():
    facts, raw = fixture()
    chapter = raw['chapters'][0]
    chapter.update(fact_ids=list(facts), selected_asset_ids=['V001', 'V002'], hero_frame_id='frame-1',
        media_choices=[dict(asset_id=f'V00{i}', frame_id=f'frame-{i}', fact_ids=[f'F00{i}'],
                            role='PRIMARY' if i == 1 else 'SUPPORT', reason='Verified selection') for i in (1, 2)])
    reviewed = {'C01': {'title': '两处海港地标', 'title_fact_ids': ['F001', 'F002'],
                       'sentences': [{'text': '第二处细节。', 'fact_ids': ['F002']}]}}
    result, audit = p.reconcile_final_chapter_media([chapter], reviewed, facts)
    assert result[0]['hero_frame_id'] == 'frame-1'
    assert audit[0]['status'] == 'RETAINED'


def test_unevaluated_title_never_triggers_semantic_replacement():
    item = anchored_memory()
    draft = {'id': 'C1', 'title': '海港地标漫步', 'title_fact_ids': ['F1'],
             'sentences': [{'text': '渡轮正在行驶。', 'fact_ids': ['F2'], 'source_index': 0}]}
    packet = {'reviewed': {}, '_final_verification_memories': [{**item, 'draft': draft}],
              'final_verification_output': {'items': [{'id': 'C1', 'title_supported': False,
                  'title_evaluated': False, 'title_reason': 'NO_UNIQUE_BOUND_IMAGE:F1:opera',
                  'sentences': [{'source_index': 0, 'supported': True}]}]}}
    def no_request(*args, **kwargs):
        pytest.fail('Missing evidence must not ask the writer to invent a narrower title')
    p.repair_final_titles(packet, [item], 'REPAIR', ask=no_request,
                         time_basis='IMPORT_ORDER_ONLY', stage_runs=[])
    assert not packet.get('final_title_repair_attempted_ids')


def test_missing_image_is_reported_as_unevaluated_not_a_visual_rejection():
    item = anchored_memory()
    copy = {'id': 'C1', 'title': '海港地标漫步', 'title_fact_ids': ['F1'], 'style_flags': [],
            'sentences': [{'text': '渡轮正在行驶。', 'fact_ids': ['F2']}]}
    packet = {'reviewed': {'C1': copy}}
    p.verify_final_chapter_copy(packet, [item], 'VERIFY', ask=lambda *a, **k: pytest.fail('No images'),
                               time_basis='IMPORT_ORDER_ONLY', stage_runs=[])
    verdict = packet['final_verification_output']['items'][0]
    assert verdict.get('title_evaluated') is False
    assert not packet['reviewed']
