"""Offline historical Product wire regressions, not fresh model/quality evaluations.

Public references originate from the checked-in index. JPEGs below are deliberate
synthetic disk fixtures; exact historical JPEG replay is recorded separately.
"""
import hashlib
import io
import json
from pathlib import Path

import pytest
from PIL import Image

from shared.result_admit import apply_admission
from shared.result_contract import CONTRACT_VERSION, SCHEMA_SHA256, validate_result_contract

FIXTURES = Path(__file__).parent / 'fixtures/product_contract'


def fixture(tmp_path, name='nagoya_r52'):
    manifest = json.loads((FIXTURES / f'{name}-manifest.json').read_bytes())
    result = json.loads((FIXTURES / f'{name}-result.json').read_bytes())
    for asset in manifest['assets']:
        for frame in asset['frames']:
            image = io.BytesIO()
            Image.new('RGB', (frame['width'], frame['height']), 'white').save(image, format='JPEG')
            content = image.getvalue()
            frame['sha256'] = hashlib.sha256(content).hexdigest()
            path = tmp_path / frame['relative_path']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    raw = json.dumps(manifest, separators=(',', ':')).encode()
    result['bundle_manifest_sha256'] = hashlib.sha256(raw).hexdigest()
    return result, manifest, raw


def admit(result, manifest, raw, root):
    return apply_admission(result, manifest_bytes=raw, bundle_dir=root,
                           bundle_version=manifest['bundle_version'], allow_mock=False)


@pytest.mark.parametrize('name,counts', [
    ('nagoya_r52', (1, 0)), ('zoo_r52', (3, 0)), ('rural_r55', (0, 2)), ('photo_v07', (1, 0)),
])
def test_historical_product_references_survive_admission_without_copy_or_image_rewrite(tmp_path, name, counts):
    result, manifest, raw = fixture(tmp_path, name)
    frozen = json.dumps(result, sort_keys=True)
    saved, envelope = admit(result, manifest, raw, tmp_path)
    assert envelope['publish_admit'], envelope
    assert (len(saved['chapters']), len(saved['ahas'])) == counts
    assert envelope['result_contract_version'] == CONTRACT_VERSION
    assert envelope['result_contract_sha256'] == SCHEMA_SHA256[result['schema_version']]
    assert envelope['session_id'] == result['session_id']
    assert json.dumps(result, sort_keys=True) == frozen
    assert saved['chapters'] == result['chapters'] and saved['ahas'] == result['ahas']


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(bundle_manifest_sha256='f' * 64),
    lambda r: r.update(session_id='11111111-1111-4111-8111-111111111111'),
    lambda r: r['chapters'][0].update(id='11111111-1111-4111-8111-111111111111'),
    lambda r: r['chapters'][0].update(hero_frame_id='missing'),
    lambda r: r['chapters'][0]['selected_media'][0].update(representative_frame_id='missing'),
    lambda r: r['chapters'][0]['selected_media'][0].update(source_asset_id='foreign'),
    lambda r: r['chapters'][0]['selected_media'][0].update(selection_fact_ids=['F999']),
    lambda r: r['chapters'][0]['claims'][0].update(text='unsupported invented copy'),
    lambda r: r['chapters'][0]['sentence_claims'][0].update(fact_ids=['F999']),
    lambda r: r['chapters'][0]['highlights'][0].update(parent_chapter_id='foreign'),
    lambda r: r['decision_trace']['selected_structure']['chapters'][0].update(fact_ids=['F999']),
    lambda r: r.update(selected_memory_outcomes=[]),
])
def test_invalid_product_fact_or_frame_bindings_cannot_publish(tmp_path, mutation):
    result, manifest, raw = fixture(tmp_path, 'photo_v07')
    mutation(result)
    _, envelope = admit(result, manifest, raw, tmp_path)
    assert not envelope['publish_admit'] and envelope['fail_job']


def test_product_requires_evidence_and_rejects_changed_or_missing_frame_bytes(tmp_path):
    result, manifest, raw = fixture(tmp_path)
    assert not admit(result, manifest, raw, None)[1]['publish_admit']
    path = tmp_path / manifest['assets'][0]['frames'][0]['relative_path']
    path.write_bytes(b'changed')
    assert not admit(result, manifest, raw, tmp_path)[1]['publish_admit']
    path.unlink()
    assert not admit(result, manifest, raw, tmp_path)[1]['publish_admit']


def empty_result(result):
    result.update(delivery_state='NO_GROUNDED_MEMORY', semantic_day_state='EMPTY_DAY',
                  output_mode='EMPTY_DAY', chapters=[], ahas=[], selected_memory_outcomes=[])
    result['observations'][0].update(status='INSUFFICIENT_EVIDENCE', facts=[])
    result['decision_trace'].update(verified_facts={}, visual_fact_ledger=[], recovery_visual_ledger=[],
                                    selected_structure={'chapters': [], 'moments': []})


@pytest.mark.parametrize('delivery', ['READY_WITH_ITEM_BLOCKS', 'NO_GROUNDED_MEMORY'])
@pytest.mark.parametrize('signal', ['INCOMPLETE', 'PARTIAL_UNRESOLVED', 'unresolved', 'FAILED'])
def test_product_contract_and_admission_reject_each_incomplete_input_signal(tmp_path, delivery, signal):
    result, manifest, raw = fixture(tmp_path, 'photo_v07')
    if delivery == 'NO_GROUNDED_MEMORY':
        empty_result(result)
    else:
        result['delivery_state'] = delivery
    if signal == 'unresolved':
        # Product historically permits omitted coverage; unresolved IDs alone must block.
        result.pop('coverage_status')
        result['unresolved_asset_ids'] = [manifest['assets'][0]['asset_id']]
    elif signal == 'FAILED':
        # Neither a forged COMPLETE label nor empty unresolved IDs can conceal failure.
        result['observations'][0]['status'] = 'FAILED'
    else:
        result['coverage_status'] = signal

    with pytest.raises(ValueError):
        validate_result_contract(result, raw, tmp_path)
    _, envelope = admit(result, manifest, raw, tmp_path)
    assert not envelope['publish_admit'] and envelope['fail_job']


def test_complete_partial_observation_with_grounded_facts_still_publishes(tmp_path):
    result, manifest, raw = fixture(tmp_path, 'photo_v07')
    result['observations'][0]['status'] = 'PARTIAL'

    _, envelope = admit(result, manifest, raw, tmp_path)

    assert envelope['publish_admit'] and envelope['input_bound'], envelope


def test_complete_insufficient_evidence_is_an_honest_empty_result(tmp_path):
    result, manifest, raw = fixture(tmp_path, 'photo_v07')
    empty_result(result)

    saved, envelope = admit(result, manifest, raw, tmp_path)

    assert envelope['publish_admit'] and envelope['input_bound'], envelope
    assert not envelope['fail_job']
    assert saved['chapters'] == [] and saved['ahas'] == []


def test_historical_product_without_optional_coverage_fields_still_publishes(tmp_path):
    result, manifest, raw = fixture(tmp_path, 'nagoya_r52')
    result.pop('coverage_status')
    result.pop('unresolved_asset_ids')

    _, envelope = admit(result, manifest, raw, tmp_path)

    assert envelope['publish_admit'] and envelope['input_bound'], envelope
