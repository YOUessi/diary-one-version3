"""Recorded media/boundary failure; scripted repair is not a semantic gold."""
from copy import deepcopy
import dataclasses
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from diary_one_ci import frame_selection, product_editor as p


def recorded():
    return json.loads((Path(__file__).parent / 'fixtures/product_phase10_media_boundary_r518.json').read_text())


def schema(data):
    return frame_selection.augment_frame_selection_schema(
        p.structure_wire_schema(data['facts'], candidates=data['candidates']),
        data['candidates'], data['facts'], scene_clues=data['scene_clues'])


def compile_output(data, output):
    return p.compile_assessed_structure(output, data['facts'], data['assets'], 4,
        candidates=data['candidates'], shown_frames=data['shown'], scene_clues=data['scene_clues'])


def test_budget_reserves_evidence_for_late_independent_chapter(tmp_path):
    data = recorded()
    groups = {c['id']: c['fact_ids'] for c in data['draft']['chapters']}
    shown, evidence, audit = p.media_selection_candidates(data['facts'], data['assets'],
        SimpleNamespace(manifest_path=tmp_path / 'bundle.json'),
        preferred_assets=list(data['assets']), chapter_fact_groups=groups)
    assert len(evidence) == 18
    assert 'V024' in shown, 'Map chapter must have an actual candidate within the same total budget.'
    assert 'V001' in shown and any(data['facts'][fid]['asset_id'] in shown for fid in groups['C02'])
    assert len({(c['asset_id'], c['frame_id']) for c in audit['shown_frames']}) == 18
    assert all(row['status'] == 'COVERED' for row in audit['chapter_coverage'])


def test_budget_does_not_invent_a_candidate_for_unverified_chapter(tmp_path):
    data = recorded()
    data['facts']['F025']['visual_reviewed'] = False
    shown, _, audit = p.media_selection_candidates(data['facts'], data['assets'],
        SimpleNamespace(manifest_path=tmp_path / 'bundle.json'),
        chapter_fact_groups={'C02': ['F025']})
    assert 'V024' not in shown
    assert audit['chapter_coverage'] == [{'chapter_id': 'C02', 'status': 'NO_VERIFIED_CANDIDATE',
                                        'candidate_ids': []}]


def test_chapter_reservations_respect_small_total_budget_and_deduplicate(tmp_path):
    data = recorded()
    shown, evidence, audit = p.media_selection_candidates(data['facts'], data['assets'],
        SimpleNamespace(manifest_path=tmp_path / 'bundle.json'), max_frames=1,
        chapter_fact_groups={'C01': ['F025'], 'C02': ['F025'], 'C03': ['F001']})
    assert len(evidence) == 1 and list(shown) == ['V024']
    assert [r['status'] for r in audit['chapter_coverage']] == ['COVERED', 'COVERED', 'BUDGET_EXHAUSTED']


def boundary_patch():
    return {'chapter_boundaries': [{'chapter_ids': ['C01', 'C02'], 'basis': 'DIFFERENT_ACTIVITY',
        'evidence_fact_ids': ['F024', 'F025'], 'reason': 'Scripted boundary fixture: outdoor path versus map image.'}]}


def test_recorded_null_hero_does_not_prevent_explicit_boundary_repair():
    data = recorded(); original = deepcopy(data['output']); audit = []
    assert not compile_output(data, original)[0]
    def ask(stage, prompt, requested_schema, context):
        assert stage == 'S09D_PRODUCT_BOUNDARY_REPAIR'
        assert set(requested_schema['properties']) == {'chapter_boundaries'}
        return boundary_patch()
    repaired = p.repair_boundary_contract(original, schema(data), data['facts'], ask=ask, audit=audit)
    chapters, _, issues, _, _ = compile_output(data, repaired)
    assert [c['id'] for c in chapters] == ['C01']
    assert any(r['item'] == 'C02' for r in issues)
    assert repaired['chapters'][1]['hero_candidate_id'] is None
    assert {k:v for k,v in repaired.items() if k != 'chapter_boundaries'} == {
        k:v for k,v in original.items() if k != 'chapter_boundaries'}
    assert original == data['output']
    assert audit[0]['status'] == 'PATCHED_PENDING_FULL_VALIDATION'
    assert audit[0]['deferred_hero_issues']


@pytest.mark.parametrize('damage', ['missing_pair', 'unknown_id', 'one_sided_facts', 'rewrite_content'])
def test_bad_boundary_patch_never_bypasses_full_validation(damage):
    data = recorded(); audit = []; patch = boundary_patch()
    row = patch['chapter_boundaries'][0]
    if damage == 'missing_pair': del row['chapter_ids']
    elif damage == 'unknown_id': row['chapter_ids'][1] = 'C99'
    elif damage == 'one_sided_facts': row['evidence_fact_ids'] = ['F001', 'F002']
    else: patch['chapters'] = []
    repaired = p.repair_boundary_contract(data['output'], schema(data), data['facts'],
        ask=lambda *args: patch, audit=audit)
    assert repaired is data['output']
    assert audit and audit[-1]['status'] == 'REJECTED'
    assert not compile_output(data, repaired)[0]


def test_other_invalid_structure_still_cannot_use_boundary_only_repair():
    data = recorded(); data['output']['chapters'][1]['fact_ids'] = ['F999']
    repaired = p.repair_boundary_contract(data['output'], schema(data), data['facts'],
        ask=lambda *args: pytest.fail('foreign facts require a structure repair'), audit=[])
    assert repaired is data['output']


def test_product_request_shows_evidence_for_the_last_provisional_chapter(tmp_path):
    from diary_one_ci.x02 import run_x02_product
    from test_product_editor import Gateway, chapter, wire_output, make_x02_bundle
    class ProbeComplete(RuntimeError):
        pass
    class TwoChapters(Gateway):
        candidates = []
        def call(self, stage, prompt, requested_schema, evidence=(), context=None):
            if stage == 'S09B_PRODUCT_VERIFIED_STRUCTURE':
                self.candidates = context['media_selection_candidates']
                raise ProbeComplete()
            run = super().call(stage, prompt, requested_schema, evidence, context)
            if stage in ('S07_PRODUCT_EDITOR', 'S08_PRODUCT_STRUCTURE_REVIEW'):
                first = chapter(); first['fact_ids'] = [f'F{i:03}' for i in range(1, 24)]
                last = chapter('C02', 'F024', 'V024')
                output = {'chapters': [first, last], 'moments': [], 'unselected_facts': [],
                    'chapter_boundaries': [{'chapter_ids': ['C01', 'C02'],
                        'basis': 'SEPARATE_EXPERIENCE', 'evidence_fact_ids': ['F001', 'F024'],
                        'reason': 'Independent activities in synthetic fixture'}]}
                return dataclasses.replace(run, output=wire_output(output, context))
            return run
    gateway = TwoChapters()
    with pytest.raises(ProbeComplete):
        run_x02_product(make_x02_bundle(tmp_path, 24), gateway)
    assert len(gateway.candidates) == 18
    assert any(c['asset_id'] == 'V024' for c in gateway.candidates)


def test_chapter_reservation_requires_its_fact_not_merely_the_same_asset(tmp_path):
    data = recorded()
    other = deepcopy(data['assets']['V024']['frames'][0])
    other.update(frame_id='other_frame', source_timestamp_ms=9999)
    data['assets']['V024']['frames'].append(other)
    data['facts']['F026'] = {**data['facts']['F025'], 'id': 'F026',
                            'evidence_frame_ids': ['other_frame']}
    _, evidence, audit = p.media_selection_candidates(data['facts'], data['assets'],
        SimpleNamespace(manifest_path=tmp_path / 'bundle.json'),
        chapter_fact_groups={'C03': ['F025'], 'C04': ['F026']})
    assert len(evidence) == 18
    for row, fid in zip(audit['chapter_coverage'], ['F025', 'F026']):
        assert row['status'] == 'COVERED'
        matching = [c for c in audit['shown_frames'] if c['candidate_id'] in row['candidate_ids']]
        assert matching and all(fid in c['fact_ids'] for c in matching)
    assert audit['chapter_coverage'][0]['candidate_ids'] != audit['chapter_coverage'][1]['candidate_ids']
