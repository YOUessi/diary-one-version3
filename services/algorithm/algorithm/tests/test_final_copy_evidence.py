from copy import deepcopy
from types import SimpleNamespace

import pytest

from diary_one_ci.final_copy_evidence import build_final_copy_scope


def inputs(tmp_path, n=3):
    assets = {}
    for i in range(n):
        aid = 'V' + str(i)
        frames = []
        for j in range(30):
            relative = aid + '-' + str(j) + '.jpg'
            (tmp_path / relative).write_bytes(b'image input fixture')
            frames.append({'frame_id': 'f' + str(j), 'relative_path': relative})
        assets[aid] = {'asset_id': 'source-' + aid, 'frames': frames}
    bundle = SimpleNamespace(manifest_path=tmp_path / 'bundle.json')
    return assets, bundle


def memory(mid='C1', aid='V0', kind='CHAPTER', frames=('f0', 'f1')):
    return {'id': mid, 'kind': kind, 'fact_ids': ['F-' + mid], 'facts': [
        {'id': 'F-' + mid, 'asset_id': aid, 'text': 'Original fixed fact.', 'evidence_frame_ids': list(frames)}]}


def test_round_robin_budget_preserves_all_kinds_without_changing_input(tmp_path):
    assets, bundle = inputs(tmp_path)
    items = [memory('C', 'V0', frames=['f' + str(j) for j in range(30)]),
             memory('H', 'V1', 'HIGHLIGHT', ['f4']), memory('A', 'V2', 'AHA', ['f5'])]
    original = deepcopy((items, assets))
    evidence, scope = build_final_copy_scope(items, assets, bundle)
    assert len(evidence) == 24
    assert [(a['asset_id'], f['frame_id']) for a, f, _ in evidence[:3]] == [
        ('source-V0', 'f0'), ('source-V1', 'f4'), ('source-V2', 'f5')]
    assert all(m['visual_check_available'] for m in scope['memories'])
    assert scope['memories'][0]['unshown_refs'][0]['reason'] == 'IMAGE_BUDGET'
    assert (items, assets) == original


def test_focus_priority_cannot_authorize_foreign_frame(tmp_path):
    assets, bundle = inputs(tmp_path)
    item = memory(frames=['f0', 'f1'])
    item['focus_frame_ids'] = ['f20', 'f1']
    evidence, scope = build_final_copy_scope([item], assets, bundle, max_frames=1)
    assert evidence[0][1]['frame_id'] == 'f1'
    assert scope['memories'][0]['shown_refs'][0]['fact_id'] == 'F-C1'
    assert all(r['frame_id'] != 'f20' for r in scope['shown_frames'])


def test_same_frame_id_on_different_assets_never_borrows_image(tmp_path):
    assets, bundle = inputs(tmp_path)
    items = [memory('C', 'V0', frames=['f0']), memory('H', 'V1', 'HIGHLIGHT', ['f0'])]
    evidence, scope = build_final_copy_scope(items, assets, bundle, max_frames=1)
    assert len(evidence) == 1
    assert scope['memories'][0]['visual_check_available']
    assert not scope['memories'][1]['visual_check_available']
    assert scope['memories'][1]['unshown_refs'][0]['asset_id'] == 'V1'


def test_shared_image_deduplicates_but_fact_scope_remains_per_memory(tmp_path):
    assets, bundle = inputs(tmp_path)
    items = [memory('C', frames=['f0']), memory('H', kind='HIGHLIGHT', frames=['f0'])]
    evidence, scope = build_final_copy_scope(items, assets, bundle, max_frames=1)
    assert len(evidence) == 1
    assert [m['shown_refs'][0]['fact_id'] for m in scope['memories']] == ['F-C', 'F-H']


@pytest.mark.parametrize('fault,code', [
    ('source', 'SOURCE_ASSET_MISMATCH'), ('foreign_frame', 'FRAME_NOT_UNIQUELY_OWNED_BY_ASSET'),
    ('missing_image', 'IMAGE_UNAVAILABLE_OR_OUTSIDE_BUNDLE'), ('escape', 'IMAGE_UNAVAILABLE_OR_OUTSIDE_BUNDLE'),
    ('foreign_fact', 'FACT_NOT_OWNED_BY_MEMORY')])
def test_missing_or_foreign_input_never_claimed_visually_available(tmp_path, fault, code):
    assets, bundle = inputs(tmp_path)
    item = memory(frames=['f0'])
    if fault == 'source': item['facts'][0]['source_asset_id'] = 'source-V1'
    elif fault == 'foreign_frame': item['facts'][0]['evidence_frame_ids'] = ['f-unknown']
    elif fault == 'missing_image': (tmp_path / 'V0-0.jpg').unlink()
    elif fault == 'escape': assets['V0']['frames'][0]['relative_path'] = '../outside.jpg'
    elif fault == 'foreign_fact': item['fact_ids'] = ['other']
    evidence, scope = build_final_copy_scope([item], assets, bundle)
    assert not evidence and not scope['memories'][0]['visual_check_available']
    assert scope['issues'][0]['code'] == code


def test_zero_budget_marks_all_refs_unshown_and_negative_budget_rejected(tmp_path):
    assets, bundle = inputs(tmp_path)
    evidence, scope = build_final_copy_scope([memory()], assets, bundle, max_frames=0)
    assert not evidence and len(scope['memories'][0]['unshown_refs']) == 2
    with pytest.raises(ValueError):
        build_final_copy_scope([memory()], assets, bundle, max_frames=-1)
    with pytest.raises(ValueError):
        build_final_copy_scope([memory()], assets, bundle, max_frames=25)
