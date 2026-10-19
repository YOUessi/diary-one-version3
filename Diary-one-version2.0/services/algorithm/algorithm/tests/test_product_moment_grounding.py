"""Image scope regressions, not a claim of perfect semantic model accuracy."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from diary_one_ci import product_editor as p, product_evidence as e


def example():
    facts = {'F001': {'id': 'F001', 'asset_id': 'V001', 'source_asset_id': 'asset-4',
        'text': '女子扶着自行车站在河边，另一帧显示逆光下的塔楼。', 'support_grade': 'STRONG',
        'evidence_frame_ids': ['woman', 'tower'], 'frame_pts_ms': [1000, 5000],
        'temporal_support': 'STATE', 'visual_reviewed': True}}
    assets = {'V001': {'asset_id': 'asset-4', 'frames': [
        {'frame_id': name, 'source_timestamp_ms': pts, 'relative_path': name + '.jpg'}
        for name, pts in [('woman', 1000), ('tower', 5000)]]}}
    moment = {'id': 'M01', 'parent_chapter_id': None, 'fact_id': 'F001',
              'focus': '女子扶车，背景是逆光塔楼', 'revisit_reason': '待核查的原候选', 'chapter_relations': []}
    return facts, assets, [moment]


def test_moment_review_sees_images_and_static_copy_cannot_reuse_another_frame():
    facts, assets, moments = example()
    original = deepcopy(facts)
    calls = []
    def ask(stage, prompt, schema, context, *, evidence):
        calls.append((stage, context, evidence))
        assert [f['frame_id'] for _, f, _ in evidence] == ['woman', 'tower']
        assert '不能写“女子扶车，背景是逆光塔楼”' in prompt
        return {'items': [{'id': 'M01', 'decision': 'KEEP', 'anchor': '女子扶着自行车站在河边。',
            'event_group_id': 'M01', 'comparison_reason': '一个成立的人物姿态',
            'scene_kind': 'CYCLING', 'scene_basis_fact_ids': ['F001'], 'value_type': 'DISTINCT_DETAIL',
            'evidence_frame_ids': ['woman', 'tower'], 'focus_frame_id': 'woman', 'reason': '只保留本帧所见'}]}
    kept, ledger, audit = e.review_moments(moments, [], facts, ask,
        assets=assets, bundle=SimpleNamespace(manifest_path=Path('/tmp/bundle/manifest.json')))
    assert len(calls) == 1 and len(kept) == 1
    assert kept[0]['focus_frame_ids'] == ['woman']
    assert audit['review_basis'] == 'FACTS_AND_SHOWN_IMAGES'
    memory = p.memory_specs([], kept, facts)[0]
    assert memory['facts'][0]['text'] == '女子扶着自行车站在河边。'
    assert memory['facts'][0]['evidence_frame_ids'] == ['woman']
    assert memory['facts'][0]['frame_pts_ms'] == [1000]
    assert memory['evidence_groups'][0]['facts'] == memory['facts']
    assert facts == original  # Original full multi-frame fact remains audit data.


def test_round_robin_cap_does_not_advertise_unshown_frames():
    facts, assets, moments = example()
    facts['F002'] = {**deepcopy(facts['F001']), 'id': 'F002', 'asset_id': 'V002'}
    assets['V002'] = {**deepcopy(assets['V001']), 'asset_id': 'asset-5'}
    moments.append({**moments[0], 'id': 'M02', 'fact_id': 'F002'})
    scoped, evidence, audit = e.moment_visual_scope(moments, facts, assets,
        SimpleNamespace(manifest_path=Path('/tmp/bundle/manifest.json')), max_frames=2)
    assert [(a['asset_id'], f['frame_id']) for a, f, _ in evidence] == [('asset-4', 'woman'), ('asset-5', 'woman')]
    assert scoped['F001']['evidence_frame_ids'] == scoped['F002']['evidence_frame_ids'] == ['woman']
    assert facts['F001']['evidence_frame_ids'] == ['woman', 'tower']
    assert len(audit['shown_frames']) == 2


def test_text_only_historical_review_is_not_mislabelled_image_reviewed():
    facts, _, moments = example()
    def ask(*args):
        return {'items': [{'id': 'M01', 'decision': 'KEEP', 'anchor': '女子扶车',
            'event_group_id': 'M01', 'comparison_reason': 'fixture', 'scene_kind': 'CYCLING',
            'scene_basis_fact_ids': ['F001'], 'value_type': 'DISTINCT_DETAIL',
            'evidence_frame_ids': ['woman'], 'focus_frame_id': 'woman', 'reason': 'fixture'}]}
    kept, _, audit = e.review_moments(moments, [], facts, ask)
    assert 'anchor_reviewed_with_images' not in kept[0]
    assert audit['review_basis'] == 'FACT_TEXT_ONLY'


def test_chapter_copy_receives_only_bound_fact_fragments_per_frame():
    facts, _, _ = example(); original = deepcopy(facts)
    supports = [{'asset_id': 'V001', 'evidence_frame_ids': ['woman'],
                 'text': '这个额外观察不是允许写作的新事实',
                 'fact_supports': [{'fact_id': 'F001', 'support': 'PARTIAL', 'visible_quote': '女子扶着自行车'}]},
                {'asset_id': 'V001', 'evidence_frame_ids': ['tower'],
                 'fact_supports': [{'fact_id': 'F001', 'support': 'PARTIAL', 'visible_quote': '逆光下的塔楼'}]},
                {'asset_id': 'V002', 'evidence_frame_ids': ['woman'],
                 'fact_supports': [{'fact_id': 'F001', 'support': 'VISIBLE', 'visible_quote': '女子'}]},
                {'asset_id': 'V001', 'evidence_frame_ids': ['unshown'],
                 'fact_supports': [{'fact_id': 'F001', 'support': 'VISIBLE', 'visible_quote': '女子'}]}]
    memory = p.memory_specs([{'id': 'C01', 'theme': '骑行', 'fact_ids': ['F001']}], [], facts,
                            frame_claim_supports=supports)[0]
    assert memory['facts'][0]['frame_observations'] == [
        {'frame_id': 'woman', 'supported_text': '女子扶着自行车'},
        {'frame_id': 'tower', 'supported_text': '逆光下的塔楼'}]
    assert memory['facts'][0]['text'] == original['F001']['text']
    assert facts == original
