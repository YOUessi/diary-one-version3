import copy
import hashlib
import io
import json
from pathlib import Path

import pytest
from PIL import Image

from shared.result_admit import apply_admission
from shared.result_contract import validate_result_contract


def fixture():
    result = json.loads((Path(__file__).parent / 'fixtures/synthetic_qwen38_result.json').read_text(encoding='utf-8'))
    result.pop('_publish', None)
    manifest = {'session': {'session_id': result['session_id']}, 'assets': [
        {'asset_id': 'asset-0', 'media_kind': 'PHOTO', 'frames': [
            {'frame_id': 'asset-0-f0', 'relative_path': 'frames/test.jpg',
             'sha256': '0' * 64, 'width': 768, 'height': 1024}]}]}
    raw = json.dumps(manifest).encode()
    result['bundle_manifest_sha256'] = hashlib.sha256(raw).hexdigest()
    return result, raw


def test_real_synthetic_result_passes_full_schema_and_input_binding():
    result, raw = fixture()
    _, env = apply_admission(result, manifest_bytes=raw, bundle_version='DIARY_ONE_APP_LIBRARY_BUNDLE_V04', allow_mock=False)
    assert env['publish_admit'], env
    assert env['input_bound'] and len(env['result_contract_sha256']) == 64


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(bundle_manifest_sha256='f' * 64),
    lambda r: r.update(session_id='another-session'),
    lambda r: r['ahas'][0].update(story=4),
    lambda r: r['ahas'][0]['selected_media'][0].update(asset_id='unknown'),
    lambda r: r['ahas'][0]['selected_media'][0].update(evidence_frame_ids=['missing']),
    lambda r: r['ahas'][0]['claims'][0].update(fact_id='unknown'),
    lambda r: r['ahas'][0]['selected_media'][0].update(observation_id='unknown'),
    lambda r: r.update(selected_memory_outcomes=[]),
    lambda r: r['selected_memory_outcomes'].append(copy.deepcopy(r['selected_memory_outcomes'][0])),
    lambda r: r['ahas'][0].update(moment_ids=['unknown']),
    lambda r: r.update(delivery_state='NO_GROUNDED_MEMORY'),
])
def test_mutated_results_fail_closed(mutation):
    result, raw = fixture()
    mutation(result)
    _, env = apply_admission(result, manifest_bytes=raw, bundle_version='DIARY_ONE_APP_LIBRARY_BUNDLE_V04', allow_mock=False)
    assert not env['publish_admit'] and env['fail_job']


def test_corrupt_or_wrong_media_cannot_publish(tmp_path):
    result, raw = fixture()
    image = io.BytesIO()
    Image.new('RGB', (768, 1024), 'white').save(image, format='JPEG')
    content = image.getvalue()
    manifest = json.loads(raw)
    frame = manifest['assets'][0]['frames'][0]
    frame['sha256'] = hashlib.sha256(content).hexdigest()
    raw = json.dumps(manifest).encode()
    result['bundle_manifest_sha256'] = hashlib.sha256(raw).hexdigest()
    path = tmp_path / 'frames/test.jpg'
    path.parent.mkdir()
    path.write_bytes(content)
    def admit():
        return apply_admission(result, manifest_bytes=raw, bundle_dir=tmp_path,
                               bundle_version='DIARY_ONE_APP_LIBRARY_BUNDLE_V04', allow_mock=False)[1]
    assert admit()['publish_admit']
    path.write_bytes(b'broken-media')
    assert not admit()['publish_admit']
    path.unlink()
    assert not admit()['publish_admit']


def test_staged_complete_label_cannot_hide_failed_observation():
    result, raw = fixture()
    result['observations'][0]['status'] = 'FAILED'

    with pytest.raises(ValueError):
        validate_result_contract(result, raw)
    _, env = apply_admission(result, manifest_bytes=raw,
                            bundle_version='DIARY_ONE_APP_LIBRARY_BUNDLE_V04', allow_mock=False)
    assert not env['publish_admit'] and env['fail_job']


def test_staged_partial_observation_with_complete_coverage_still_publishes():
    result, raw = fixture()
    result['observations'][0]['status'] = 'PARTIAL'

    _, env = apply_admission(result, manifest_bytes=raw,
                            bundle_version='DIARY_ONE_APP_LIBRARY_BUNDLE_V04', allow_mock=False)

    assert env['publish_admit'] and env['input_bound'], env
