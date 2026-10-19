"""Recorded R2 selection regression; downstream canned copy is not quality evidence."""
from copy import deepcopy
import json
from pathlib import Path
import time
from types import SimpleNamespace
import uuid

import pytest

from diary_one_ci import product_editor as p
from diary_one_ci.x02 import StageRun
from test_product_editor import scripted_final_verdict


def recorded():
    return json.loads((Path(__file__).parent / 'fixtures/product_unavailable_proposal_nagoya_r2.json').read_text())


def compile(data):
    return p.compile_assessed_structure(data['output'], data['facts'], data['assets'], 4,
        candidates=data['candidates'], shown_frames=data['shown'], scene_clues=data['scene_clues'])


def test_exact_r2_unavailable_alternative_preserves_explicit_cover_and_chapter():
    data = recorded(); before = deepcopy(data)
    chapters, moments, issues, _, audit = compile(data)
    assert not issues and [c['id'] for c in chapters] == ['C01']
    assert len(moments) == 2 and data == before
    assert chapters[0]['hero_frame_id'] == 'asset-0-f0'
    assert 'P009' not in chapters[0]['candidate_selection_audit']['ranked_candidate_ids']
    assert chapters[0]['fact_ids'] == data['output']['chapters'][0]['fact_ids']
    removed = audit['unavailable_media_proposals']
    assert len(removed) == 1 and removed[0]['candidate_id'] == 'P009'
    assert removed[0]['action'] == 'REMOVED_EXPLICITLY_UNSUPPORTED_NON_HERO_PROPOSAL'
    assert removed[0]['raw_assessment']['visibility'] == 'NOT_VISIBLE'
    assert removed[0]['hero_candidate_id_unchanged'] == 'P001'


def test_unavailable_nonhero_from_another_asset_is_omitted_without_fact_loss():
    data = recorded()
    next(r for r in data['output']['media_choices'] if r['candidate_id'] == 'P009')['candidate_id'] = 'P010'
    chapters, _, issues, _, audit = compile(data)
    assert not issues and chapters[0]['hero_frame_id'] == 'asset-0-f0'
    assert audit['unavailable_media_proposals'][0]['candidate_id'] == 'P010'
    assert 'F006' in chapters[0]['fact_ids']


@pytest.mark.parametrize('fault', ['hero', 'duplicate_choice', 'duplicate_assessment', 'unknown_candidate',
    'wrong_frame', 'wrong_asset', 'foreign_fact', 'missing_assessment', 'empty_reason', 'malformed_unavailable'])
def test_isolation_does_not_hide_hard_binding_or_hero_failure(fault):
    data = recorded(); raw = data['output']
    choice = next(r for r in raw['media_choices'] if r['candidate_id'] == 'P009')
    candidate = next(r for r in data['candidates'] if r['candidate_id'] == 'P009')
    assessment = next(r for r in raw['frame_assessments'] if r['candidate_id'] == 'P009')
    if fault == 'hero': raw['chapters'][0]['hero_candidate_id'] = 'P009'
    elif fault == 'duplicate_choice': raw['media_choices'].append(deepcopy(choice))
    elif fault == 'duplicate_assessment': raw['frame_assessments'].append(deepcopy(assessment))
    elif fault == 'unknown_candidate': choice['candidate_id'] = 'P999'
    elif fault == 'wrong_frame': candidate['frame_id'] = 'asset-4-f2'
    elif fault == 'wrong_asset': candidate['asset_id'] = 'V005'
    elif fault == 'foreign_fact': candidate['fact_ids'] = ['F006']
    elif fault == 'missing_assessment': raw['frame_assessments'].remove(assessment)
    elif fault == 'empty_reason': choice['reason'] = ''
    else: assessment['fact_ids'] = ['F001']
    clean, removed = p.isolate_unavailable_media_proposals(raw, data['facts'], data['assets'], data['candidates'], data['shown'])
    assert clean == raw and not removed
    try:
        chapters, _, issues, _, _ = compile(data)
    except ValueError:
        assert fault in ('wrong_frame', 'wrong_asset', 'foreign_fact')
    else:
        assert not chapters and issues


def test_whole_editor_replays_real_r2_structure_then_reaches_and_publishes_canned_copy(tmp_path):
    data = recorded(); initial = deepcopy(data['initial']); before = deepcopy(data)
    manifest_path = tmp_path / 'bundle.json'
    manifest = deepcopy(data['manifest'])
    # Explicit synthetic JPEG bytes exercise binding only, never real semantic quality.
    from PIL import Image
    from hashlib import sha256
    for asset in manifest['assets']:
        for frame in asset.get('frames', []):
            target = tmp_path / frame['relative_path']
            target.parent.mkdir(parents=True, exist_ok=True)
            Image.new('RGB', (frame['width'], frame['height']), (40, 100, 80)).save(target)
            frame['sha256'] = sha256(target.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    bundle = SimpleNamespace(manifest=manifest, manifest_path=manifest_path)
    calls = []
    def call(stage, prompt, schema, evidence=(), context=None):
        calls.append(stage)
        if '_FINAL_VERIFY' in stage:
            output = scripted_final_verdict(context)
        elif stage in data['recorded_stages']:
            output = deepcopy(data['recorded_stages'][stage])
        elif stage == 'S10_PRODUCT_MOMENT_VALUE':
            output = {'items': [dict(id=m['id'], decision='DROP', anchor='', event_group_id=m['id'],
                comparison_reason='Offline fixture leaves copy verification scoped to the chapter', scene_kind='CYCLING',
                scene_basis_fact_ids=[m['fact_id']], value_type='ROUTINE', evidence_frame_ids=[], focus_frame_id='',
                reason='Synthetic downstream judgment, not a real quality decision') for m in context['moments']]}
        elif stage.endswith('_NARRATIVE_BRIEF'):
            output = {'items': [dict(id='C01', details=[dict(fact_id='F001', evidence_quote='前方可见铁轨桥', role='MAIN')])]}
        elif stage == 'S11_PRODUCT_WRITER':
            output = {'items': [dict(id='C01', title='铁轨桥旁', story='前方是一座铁轨桥。')]}
        elif stage == 'S12_PRODUCT_FACT_REVIEW':
            output = {'items': [dict(id='C01', decision='PUBLISH', reason='Canned regression review', title='铁轨桥旁',
                title_fact_ids=['F001'], sentences=[dict(text='前方是一座铁轨桥。', fact_ids=['F001'], source_index=0)])]}
        elif stage == 'S14_PRODUCT_COVERAGE_REVIEW':
            output = {'decisions': [dict(asset_id=aid, disposition='REDUNDANT', reason='Canned coverage only', moment=None)
                for aid in context['unrepresented_assets']]}
        else:
            raise AssertionError('Unexpected offline stage ' + stage)
        return StageRun(stage=stage, output=output, provider='offline', model='recorded-and-scripted', request_id=stage,
            input_tokens=0, output_tokens=0, latency_seconds=0, model_frame_count=len(evidence), model_calls=0,
            pricing_currency='USD', input_rate_per_million=0, output_rate_per_million=0,
            native_currency_per_usd=1, pricing_basis='OFFLINE_NO_CALL')
    result = p.run(bundle=bundle, **initial, call_model=call, stage_runs=[],
        gateway=SimpleNamespace(provider='offline', model='recorded-and-scripted'), run_started=time.monotonic(),
        namespace=uuid.UUID(data['manifest']['session']['session_id']))
    assert data == before and 'S11_PRODUCT_WRITER' in calls and len(result['chapters']) == 1
    assert result['trace']['model_calls'] == 0
    trace = result['decision_trace']
    assert trace['editor_output']['media_choices'][1]['candidate_id'] == 'P009'  # Raw record preserved.
    assert not trace['media_selection_rejections']
    assert trace['media_selection_audit']['frame_assessment']['unavailable_media_proposals'][0]['candidate_id'] == 'P009'
    assert result['chapters'][0]['hero_frame_id'] == 'asset-0-f0'
