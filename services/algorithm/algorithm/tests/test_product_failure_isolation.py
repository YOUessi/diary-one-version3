"""Deterministic editorial failures; these assertions are not visual-quality scores."""
from copy import deepcopy

import pytest
from diary_one_ci import product_editor as p
from test_product_editor import chapter
from test_product_editor import wire_output


def fixture():
    facts = {f'F00{i}': {'id': f'F00{i}', 'asset_id': f'V00{i}',
             'text': '街边散步。', 'visual_reviewed': True,
             'evidence_frame_ids': [f'frame-{i}']} for i in range(1, 4)}
    chapters = [chapter(f'C0{i}', f'F00{i}', f'V00{i}') for i in range(1, 4)]
    boundaries = [dict(chapter_ids=[f'C0{i}', f'C0{j}'],
        evidence_fact_ids=[f'F00{i}', f'F00{j}'], basis='SEPARATE_EXPERIENCE',
        reason='Synthetic separate activity evidence') for i, j in [(1, 2), (1, 3), (2, 3)]]
    return facts, dict(chapters=chapters, moments=[], unselected_facts=[], chapter_boundaries=boundaries)


@pytest.mark.parametrize('damage', ['semantic', 'foreign_fact', 'bad_type'])
def test_rejected_chapter_cannot_erase_other_valid_chapters(damage):
    facts, raw = fixture()
    if damage == 'semantic': raw['chapters'][0]['grouping_reason'] = '不同片段的连续骑行'
    if damage == 'foreign_fact': raw['chapters'][0]['fact_ids'] = ['F999']
    if damage == 'bad_type': raw['chapters'][0]['theme'] = None
    original = deepcopy(raw)
    chapters, _, rejected, _ = p.compile_selection(raw, facts, {}, enforce_boundaries=True)
    assert [c['id'] for c in chapters] == ['C02', 'C03']
    assert any(r['item'] == 'C01' for r in rejected)
    assert raw == original


@pytest.mark.parametrize('damage', ['missing_pair', 'foreign_chapter', 'wrong_evidence', 'duplicate_pair'])
def test_surviving_chapter_boundaries_still_require_valid_evidence(damage):
    facts, raw = fixture()
    raw['chapters'][0]['theme'] = None
    if damage == 'missing_pair': raw['chapter_boundaries'].pop()
    if damage == 'foreign_chapter': raw['chapter_boundaries'][0]['chapter_ids'] = ['C01', 'C99']
    if damage == 'wrong_evidence': raw['chapter_boundaries'][-1]['evidence_fact_ids'] = ['F001', 'F002']
    if damage == 'duplicate_pair': raw['chapter_boundaries'].append(deepcopy(raw['chapter_boundaries'][-1]))
    assert not p.compile_selection(raw, facts, {}, enforce_boundaries=True)[0]


@pytest.mark.parametrize('disposition', ['REDUNDANT', 'CAPACITY_LIMIT'])
def test_unpublished_chapters_and_empty_capacity_cannot_justify_omission(disposition):
    facts, _ = fixture()
    raw = {'decisions': [dict(asset_id='V001', disposition=disposition,
        reason='C01 already covers this; slots full', moment=None, covered_by_ids=['C01'])]}
    additions, ledger = p.compile_recovery(raw, {'V001'}, [], [], facts, {}, {'C01'})
    assert not additions and ledger[0]['status'] == 'BLOCKED'


def test_redundancy_must_point_to_a_published_memory():
    facts, raw = fixture()
    decision = dict(asset_id='V003', disposition='REDUNDANT', reason='Same experience',
                    moment=None, covered_by_ids=['C01'])
    assert p.compile_recovery({'decisions': [decision]}, {'V003'}, raw['chapters'][:1], [], facts, {}, set())[1][0]['status'] == 'VALIDATED'
    decision['covered_by_ids'] = ['C99']
    assert p.compile_recovery({'decisions': [decision]}, {'V003'}, raw['chapters'][:1], [], facts, {}, set())[1][0]['status'] == 'BLOCKED'


@pytest.mark.parametrize('title_ids,expected', [(['F002'], 'frame-2'), (['F003'], 'frame-3'), (['F001'], 'frame-1')])
def test_final_title_focus_reselects_only_already_verified_frames(title_ids, expected):
    facts, raw = fixture()
    c = raw['chapters'][0]
    c.update(fact_ids=list(facts), selected_asset_ids=['V001', 'V002', 'V003'], hero_frame_id='frame-1',
        media_choices=[dict(asset_id=f'V00{i}', frame_id=f'frame-{i}', fact_ids=[f'F00{i}'],
            role='PRIMARY' if i == 1 else 'SUPPORT', reason='Original verified selection') for i in range(1, 4)])
    original = deepcopy(c)
    reviewed = {'C01': dict(title='已核验的主题', title_fact_ids=title_ids,
                sentences=[dict(text='已核验正文。', fact_ids=title_ids)])}
    chapters, audit = p.reconcile_final_chapter_media([c], reviewed, facts)
    assert chapters[0]['hero_frame_id'] == expected
    assert chapters[0]['selection_focus']['fact_ids'] == title_ids
    assert chapters[0]['selected_asset_ids'] == original['selected_asset_ids']
    assert c == original and audit[0]['status'] != 'BLOCKED'
    facts[title_ids[0]]['evidence_frame_ids'] = ['some-other-frame']
    assert p.reconcile_final_chapter_media([c], reviewed, facts)[1][0]['status'] == 'BLOCKED'


@pytest.mark.parametrize('patch_kind', ['correct', 'foreign_id', 'duplicate', 'one_sided', 'empty'])
def test_boundary_only_repair_is_bounded_and_cannot_rewrite_content(patch_kind):
    facts, canonical = fixture()
    raw = wire_output(canonical, {})
    expected = deepcopy(raw)
    del raw['chapter_boundaries'][0]['chapter_ids']
    original = deepcopy(raw)
    patch = {'chapter_boundaries': deepcopy(expected['chapter_boundaries'])}
    if patch_kind == 'foreign_id': patch['chapter_boundaries'][0]['chapter_ids'][0] = 'C99'
    if patch_kind == 'duplicate': patch['chapter_boundaries'][1] = deepcopy(patch['chapter_boundaries'][0])
    if patch_kind == 'one_sided': patch['chapter_boundaries'][0]['evidence_fact_ids'] = ['F001']
    if patch_kind == 'empty': patch['chapter_boundaries'] = []
    calls, audit = [], []
    def ask(*args):
        calls.append(args)
        return patch
    result = p.repair_boundary_contract(raw, p.structure_wire_schema(facts), facts, ask=ask, audit=audit)
    assert len(calls) == 1
    assert raw == original
    assert result == (expected if patch_kind == 'correct' else original)
    assert audit[0]['status'] == ('PATCHED_PENDING_FULL_VALIDATION' if patch_kind == 'correct' else 'REJECTED')


def test_boundary_repair_does_not_hide_an_unrelated_schema_error():
    facts, canonical = fixture()
    raw = wire_output(canonical, {})
    raw['chapters'][0]['id'] = None
    del raw['chapter_boundaries'][0]['chapter_ids']
    assert p.repair_boundary_contract(raw, p.structure_wire_schema(facts), facts,
        ask=lambda *a: pytest.fail('Should not request a boundary-only repair'), audit=[]) is raw


@pytest.mark.parametrize('patch_kind', ['valid', 'foreign_asset', 'invented_cover'])
def test_failed_coverage_gets_one_scoped_repair_and_cannot_edit_valid_decisions(patch_kind):
    facts, raw = fixture()
    chapters = raw['chapters'][:1]
    duplicate = dict(id='M90', fact_id='F001', parent_chapter_id=None,
        chapter_relations=[dict(chapter_id='C01', relation='DISTINCT')], focus='街边散步', revisit_reason='same fact')
    coverage = {'decisions': [dict(asset_id='V001', disposition='ADD_MEMORY', reason='No selected image', moment=duplicate),
        dict(asset_id='V003', disposition='INSUFFICIENT', reason='No distinctive detail', moment=None)]}
    original = deepcopy(coverage)
    patch = dict(asset_id='V001', disposition='REDUNDANT', reason='Already expressed by published chapter',
                 moment=None, covered_by_ids=['C01'])
    if patch_kind == 'foreign_asset': patch['asset_id'] = 'V999'
    if patch_kind == 'invented_cover': patch['covered_by_ids'] = ['C99']
    calls, audit = [], []
    context = dict(unrepresented_assets=['V001', 'V003'], reserved_ids=[])
    def ask(*args): calls.append(args); return {'decisions': [patch]}
    result = p.repair_coverage_contract(coverage, context, chapters, [], facts, {}, ask=ask, audit=audit)
    assert len(calls) == 1 and coverage == original
    assert next(r for r in result['decisions'] if r['asset_id'] == 'V003') == original['decisions'][1]
    final = p.compile_recovery(result, {'V001','V003'}, chapters, [], facts, {}, set())[1]
    assert (next(r for r in final if r['asset_id']=='V001')['status']=='VALIDATED') == (patch_kind=='valid')


@pytest.mark.parametrize('failure', [OSError, ValueError])
def test_coverage_repair_failure_retains_original_valid_rows(failure):
    facts, canonical = fixture()
    raw = {'decisions': [dict(asset_id='V001',disposition='CAPACITY_LIMIT',reason='incorrectly full',moment=None),
                        dict(asset_id='V003',disposition='INSUFFICIENT',reason='no detail',moment=None)]}
    audit = []
    def ask(*args): raise failure('injected')
    assert p.repair_coverage_contract(raw, dict(unrepresented_assets=['V001','V003'],reserved_ids=[]),
        canonical['chapters'][:1], [], facts, {}, ask=ask, audit=audit) is raw
    assert audit[0]['status']=='REQUEST_FAILED'


@pytest.mark.parametrize('published', [0, 1, 2, 3])
def test_rejected_recovery_copy_cannot_occupy_a_final_capacity_slot(published):
    moments = [dict(id='M'+str(i), parent_chapter_id=None) for i in range(3)]
    moments.append(dict(id='H01', parent_chapter_id='C01'))
    reviewed = {**{m['id']: {} for m in moments[:published]}, 'H01': {}}
    ledger = [dict(asset_id='V007', status='VALIDATED', disposition='CAPACITY_LIMIT', reason='Three proposed additions'),
              dict(asset_id='V008', status='VALIDATED', disposition='INSUFFICIENT', reason='No detail')]
    original = deepcopy(ledger)
    result = p.reconcile_published_capacity(ledger, moments, reviewed)
    assert ledger == original and result[1] == ledger[1]
    if published == 3:
        assert result == ledger
    else:
        assert result[0]['status'] == 'BLOCKED'
        assert result[0]['reason'] == 'CAPACITY_OPEN_AFTER_FINAL_REVIEW'
        assert result[0]['published_slots'] == published
