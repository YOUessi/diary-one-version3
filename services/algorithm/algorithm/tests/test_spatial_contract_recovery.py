"""Wire-fault regressions; scripted verdicts do not establish visual truth."""
from copy import deepcopy
from pathlib import Path
import hashlib

import pytest

from diary_one_ci import product_editor as p
from final_copy_test_support import bound_test_images
from test_product_spatial_style_v071 import item


@pytest.mark.parametrize('text', ['动物园里的动物们', '棕榈树下的砖路行走', '展厅里的参观片段'])
def test_scene_or_activity_uses_independent_claim_review_without_fake_boxes(text):
    assert p.requires_spatial_relation_review(text)
    assert p.spatial_relation_targets({'claim_id': 'Q1', 'text': text, 'frame_refs': []}) == []


def run_case(first, second=None):
    calls = []
    with bound_test_images([item()]) as (_, evidence, scope):
        ref = {'source_asset_id': 'V001', 'frame_id': 'frame-a'}
        claim = {'claim_id': 'Q1', 'text': '横梁上的动物', 'field': 'TITLE', 'frame_refs': [ref]}
        def ask(stage, prompt, schema, context, *, evidence):
            hashes = [hashlib.sha256(Path(path).read_bytes()).hexdigest() for asset, frame, path in evidence]
            calls.append({'stage': stage, 'context': deepcopy(context), 'hashes': hashes})
            response = first if len(calls) == 1 else second
            if isinstance(response, Exception): raise response
            return deepcopy(response)
        result = p.verify_spatial_claims({'evidence': evidence}, 'FINAL_VERIFY_SPATIAL',
            {'claims': [claim]}, ask=ask, evidence_scope=scope, stage_runs=[])
    return result, calls


def output():
    return {'claims': [], 'observations': [{
        'target_id': 'Q1:R1', 'frame_ref': {'source_asset_id': 'V001', 'frame_id': 'frame-a'},
        'subject_visible': True, 'reference_visible': True, 'identity_confirmed': True, 'same_frame': True,
        'subject_box': [.4, .1, .6, .3], 'reference_box': [.2, .3, .8, .5],
        'observed_relation': 'SUPPORTED_BY', 'support_surface': 'REFERENCE', 'description': 'Scripted contact observation',
    }]}


def test_out_of_range_coordinates_get_one_image_bound_reask_never_auto_rescaled():
    original = output()
    original['observations'][0]['subject_box'] = [400, 100, 600, 300]
    (verdicts, audit, terminal), calls = run_case(original, output())
    assert len(calls) == 2
    assert calls[0]['hashes'] == calls[1]['hashes'] and calls[0]['hashes']
    assert verdicts['Q1']['supported'] and not terminal
    assert audit['raw_output'] == original
    assert audit['format_repair']['status'] == 'VALIDATED'
    assert audit['format_repair']['raw_output'] == output()
    assert 'expected_relations' not in str(calls[1]['context'])
    assert 'source_quote' not in str(calls[1]['context'])


@pytest.mark.parametrize('second', [None, {'claims': [], 'observations': []}, TimeoutError('repair timeout')])
def test_bad_or_unavailable_repair_stays_blocked_without_third_attempt(second):
    original = output(); original['observations'][0]['subject_box'] = [100, 200, 300, 400]
    (verdicts, audit, _), calls = run_case(original, second)
    assert len(calls) == 2 and not verdicts['Q1']['supported']
    assert audit['raw_output'] == original


def test_valid_but_contradictory_observation_is_not_reasked_until_it_passes():
    denied = output(); denied['observations'][0]['observed_relation'] = 'BELOW'
    (verdicts, _, _), calls = run_case(denied, output())
    assert len(calls) == 1 and not verdicts['Q1']['supported']


def test_network_fault_is_not_relabelled_as_format_fault():
    (verdicts, audit, _), calls = run_case(TimeoutError('provider outage'), output())
    assert len(calls) == 1 and not verdicts['Q1']['supported']
    assert 'format_repair' not in audit
