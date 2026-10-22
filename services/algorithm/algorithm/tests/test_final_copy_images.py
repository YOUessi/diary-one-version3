from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
from tempfile import TemporaryDirectory

from PIL import Image
import pytest

from diary_one_ci.final_copy_images import prepare_final_copy_images


def fixture(tmp_path, *, padding=(0, 0, 0), size=(768, 1024), original=(2560, 1440)):
    root = tmp_path / 'input'
    root.mkdir()
    image = Image.new('RGB', size, padding)
    scale = min(size[0] / original[0], size[1] / original[1])
    w, h = round(original[0] * scale), round(original[1] * scale)
    left, top = (size[0] - w) // 2, (size[1] - h) // 2
    image.paste((32, 128, 200), (left, top, left + w, top + h))
    path = root / 'frame.jpg'
    image.save(path, quality=100, subsampling=0)
    frame = dict(frame_id='f1', relative_path='frame.jpg', width=size[0], height=size[1],
                 spatial_transform='ASPECT_FIT_LETTERBOX', sha256=sha256(path.read_bytes()).hexdigest())
    asset = dict(asset_id='source', media_kind='VIDEO', original_width=original[0], original_height=original[1])
    return [(asset, frame, path)], root, tmp_path / 'derived'


@pytest.mark.parametrize('size,original,rect', [
    ((768, 1024), (2560, 1440), [0, 296, 768, 728]),
    ((1024, 768), (1440, 2560), [296, 0, 728, 768])])
def test_only_declared_black_padding_removed_identity_and_original_unchanged(tmp_path, size, original, rect):
    evidence, root, output = fixture(tmp_path, size=size, original=original)
    before = deepcopy(evidence)
    source_bytes = evidence[0][2].read_bytes()
    result, audit = prepare_final_copy_images(evidence, output, bundle_root=root)
    row = audit['frames'][0]
    assert row['crop_rect'] == rect and row['status'] == 'DECLARED_BLACK_PADDING_REMOVED'
    assert result[0][0] is evidence[0][0] and result[0][1] is evidence[0][1]
    assert evidence == before
    assert evidence[0][2].read_bytes() == source_bytes
    assert sha256(result[0][2].read_bytes()).hexdigest() == row['output_sha256']
    assert Image.open(result[0][2]).size == tuple(row['output_dimensions'])
    again, again_audit = prepare_final_copy_images(evidence, output, bundle_root=root)
    assert again == result and again_audit == audit


@pytest.mark.parametrize('change,reason', [
    ('photo', 'NON_VIDEO_NEVER_CROPPED'), ('crop', 'TRANSFORM_NOT_DECLARED_LETTERBOX'),
    ('unknown', 'TRANSFORM_NOT_DECLARED_LETTERBOX'), ('size', 'DECODED_DIMENSIONS_OR_ORIENTATION_MISMATCH'),
    ('original', 'MISSING_OR_INVALID_DECLARED_DIMENSIONS')])
def test_unknown_nonvideo_or_mismatched_metadata_retains_original(tmp_path, change, reason):
    evidence, root, output = fixture(tmp_path)
    a, f, _ = evidence[0]
    if change == 'photo': a['media_kind'] = 'PHOTO'
    elif change == 'crop': f['spatial_transform'] = 'CENTER_CROP_ASPECT_FILL'
    elif change == 'unknown': f.pop('spatial_transform')
    elif change == 'size': f['width'] = 999
    elif change == 'original': a.pop('original_width')
    result, audit = prepare_final_copy_images(evidence, output, bundle_root=root)
    assert result == tuple(evidence)
    assert audit['frames'][0]['reason'] == reason
    assert not output.exists()


def test_nonblack_padding_and_full_frame_never_cropped(tmp_path):
    evidence, root, output = fixture(tmp_path, padding=(32, 32, 32))
    result, audit = prepare_final_copy_images(evidence, output, bundle_root=root)
    assert result == tuple(evidence)
    assert audit['frames'][0]['reason'] == 'DECLARED_PADDING_NOT_VERIFIED_BLACK'
    evidence[0][0].update(original_width=768, original_height=1024)
    _, audit = prepare_final_copy_images(evidence, output, bundle_root=root)
    assert audit['frames'][0]['reason'] == 'NO_DECLARED_PADDING'


def test_wrong_sha_unsafe_output_and_existing_corruption_are_not_overwritten(tmp_path):
    evidence, root, output = fixture(tmp_path)
    with pytest.raises(ValueError, match='outside'):
        prepare_final_copy_images(evidence, root / 'derived', bundle_root=root)
    expected = evidence[0][1]['sha256']
    evidence[0][1]['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='SHA missing or mismatched'):
        prepare_final_copy_images(evidence, output, bundle_root=root)
    evidence[0][1]['sha256'] = expected
    result, _ = prepare_final_copy_images(evidence, output, bundle_root=root)
    result[0][2].write_bytes(b'preexisting conflict')
    with pytest.raises(ValueError, match='refusing overwrite'):
        prepare_final_copy_images(evidence, output, bundle_root=root)
    assert result[0][2].read_bytes() == b'preexisting conflict'


@pytest.mark.parametrize('kind,transform', [('PHOTO', 'ASPECT_FIT_LETTERBOX'),
    ('VIDEO', 'CENTER_CROP_ASPECT_FILL'), ('VIDEO', 'UNKNOWN'), ('VIDEO', 'ASPECT_FIT_LETTERBOX')])
@pytest.mark.parametrize('sha_error', ['missing', 'different'])
def test_every_image_including_uncropped_inputs_requires_exact_source_sha(tmp_path, kind, transform, sha_error):
    evidence, root, output = fixture(tmp_path)
    evidence[0][0]['media_kind'] = kind
    evidence[0][1]['spatial_transform'] = transform
    if sha_error == 'missing':
        evidence[0][1].pop('sha256')
    else:
        evidence[0][1]['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='SHA missing or mismatched'):
        prepare_final_copy_images(evidence, output, bundle_root=root)
    assert not output.exists()


def test_temporary_image_lifetime_is_not_claimed_as_persistent_audit(tmp_path):
    evidence, root, _ = fixture(tmp_path)
    with TemporaryDirectory(dir=tmp_path) as folder:
        transformed, audit = prepare_final_copy_images(evidence, folder, bundle_root=root)
        derived = transformed[0][2]
        assert derived.is_file()
        assert audit['artifact_retention'] == 'EPHEMERAL'
        row = audit['frames'][0]
        assert row['source_path'] == str(evidence[0][2])
        assert row['output_kind'] == 'DERIVED_JPEG'
        assert 'output_path' not in row and 'artifact_dir' not in audit
        assert folder not in json.dumps(audit)
        assert row['encoding'] == {'format': 'JPEG', 'quality': 100, 'subsampling': 0,
                                   'resize': False, 'enhancement': False}
    assert not derived.exists() and evidence[0][2].exists()


def test_source_outside_bundle_or_derived_symlink_cannot_be_used(tmp_path):
    evidence, root, output = fixture(tmp_path)
    wrong_root = tmp_path / 'different_bundle'; wrong_root.mkdir()
    with pytest.raises(ValueError, match='inside its input bundle'):
        prepare_final_copy_images(evidence, output, bundle_root=wrong_root)
    transformed, _ = prepare_final_copy_images(evidence, output, bundle_root=root)
    target = transformed[0][2]
    target.unlink()
    target.symlink_to(evidence[0][2])
    with pytest.raises(ValueError, match='symlink'):
        prepare_final_copy_images(evidence, output, bundle_root=root)
