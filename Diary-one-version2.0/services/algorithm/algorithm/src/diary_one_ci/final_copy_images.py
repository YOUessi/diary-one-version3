"""Declared letterbox removal for final copy verification only.

No subject detection, resize, enhancement or generated pixels. Only the declared
aspect-fit content rectangle is retained. JPEG encoding can change pixel values.
"""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageStat


VERSION = 'FINAL_COPY_DECLARED_VIDEO_LETTERBOX_V01'
PAD_MAX_CHANNEL = 16
PAD_MAX_MEAN_CHANNEL = 1.0


def _inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def prepare_final_copy_images(evidence, artifact_dir, *, bundle_root):
    """Keep identity metadata; return temporary paths and a reproducible audit.

    Callers must still apply the existing per-memory reference whitelist. This
    function changes neither facts nor image order/count, and makes no visual
    judgement. Uncertain padding is retained unchanged with a skip reason.
    The caller owns a TemporaryDirectory covering the request lifetime; audit
    hashes describe ephemeral derived bytes, not durable output files.
    """
    root = Path(bundle_root).resolve()
    output = Path(artifact_dir)
    if not output.is_absolute():
        raise ValueError('artifact_dir must be absolute')
    output = output.resolve()
    if _inside(output, root):
        raise ValueError('artifact_dir must be outside the input bundle')
    transformed, ledger = [], []
    for asset, frame, raw_path in evidence:
        source = Path(raw_path).resolve()
        if not _inside(source, root) or not source.is_file():
            raise ValueError('Source image must exist inside its input bundle')
        data = source.read_bytes()
        digest = sha256(data).hexdigest()
        row = {'source_asset_id': asset.get('asset_id'), 'frame_id': frame.get('frame_id'),
               'source_path': str(source), 'source_sha256': digest,
               'status': 'ORIGINAL_RETAINED', 'crop_rect': None,
               'output_sha256': digest, 'output_kind': 'ORIGINAL',
               'artifact_retention': 'EPHEMERAL'}
        ledger.append(row)
        transformed.append((asset, frame, source))
        if not frame.get('sha256') or frame['sha256'] != digest:
            raise ValueError('Source SHA missing or mismatched; refusing final evidence')
        if asset.get('media_kind') != 'VIDEO':
            row['reason'] = 'NON_VIDEO_NEVER_CROPPED'
            continue
        if frame.get('spatial_transform') != 'ASPECT_FIT_LETTERBOX':
            row['reason'] = 'TRANSFORM_NOT_DECLARED_LETTERBOX'
            continue
        dims = [asset.get('original_width'), asset.get('original_height'),
                frame.get('width'), frame.get('height')]
        if any(type(d) is not int or d <= 0 for d in dims):
            row['reason'] = 'MISSING_OR_INVALID_DECLARED_DIMENSIONS'
            continue
        ow, oh, fw, fh = dims
        scale = min(fw / ow, fh / oh)
        cw, ch = max(1, round(ow * scale)), max(1, round(oh * scale))
        left, top = (fw - cw) // 2, (fh - ch) // 2
        bbox = (left, top, left + cw, top + ch)
        if bbox == (0, 0, fw, fh):
            row['reason'] = 'NO_DECLARED_PADDING'
            continue
        with Image.open(BytesIO(data)) as original:
            if original.size != (fw, fh) or original.getexif().get(274, 1) != 1:
                row['reason'] = 'DECODED_DIMENSIONS_OR_ORIENTATION_MISMATCH'
                continue
            rgb = original.convert('RGB')
            pads = [(0, 0, fw, top), (0, top + ch, fw, fh),
                    (0, top, left, top + ch), (left + cw, top, fw, top + ch)]
            stats = []
            for box in pads:
                if box[2] <= box[0] or box[3] <= box[1]:
                    continue
                region = rgb.crop(box)
                stats.append({'rect': list(box), 'max_channel': max(v[1] for v in region.getextrema()),
                              'mean_channels': ImageStat.Stat(region).mean})
            row['padding_check'] = {'max_channel_threshold': PAD_MAX_CHANNEL,
                                    'max_mean_channel_threshold': PAD_MAX_MEAN_CHANNEL, 'regions': stats}
            if not stats or any(s['max_channel'] > PAD_MAX_CHANNEL or
                                max(s['mean_channels']) > PAD_MAX_MEAN_CHANNEL for s in stats):
                row['reason'] = 'DECLARED_PADDING_NOT_VERIFIED_BLACK'
                continue
            cropped = rgb.crop(bbox)
            buf = BytesIO()
            cropped.save(buf, format='JPEG', quality=100, subsampling=0, optimize=False)
            jpeg = buf.getvalue()
            output_sha = sha256(jpeg).hexdigest()
            key = sha256(json.dumps({'version': VERSION, 'source_sha256': digest, 'bbox': bbox},
                                    sort_keys=True).encode()).hexdigest()
            output.mkdir(parents=True, exist_ok=True)
            target = output / (key + '.jpg')
            if target.is_symlink():
                raise ValueError('Derived target is a symlink')
            try:
                with target.open('xb') as handle:
                    handle.write(jpeg)
            except FileExistsError:
                if sha256(target.read_bytes()).hexdigest() != output_sha:
                    raise ValueError('Existing derived artifact differs; refusing overwrite')
            transformed[-1] = (asset, frame, target)
            row.update(status='DECLARED_BLACK_PADDING_REMOVED', reason='DECLARED_RECT_AND_BLACK_PADDING_VERIFIED',
                       crop_rect=list(bbox), output_sha256=output_sha, output_kind='DERIVED_JPEG',
                       input_dimensions=[fw, fh], output_dimensions=[cw, ch],
                       source_crop_rgb_sha256=sha256(cropped.tobytes()).hexdigest(),
                       encoding={'format': 'JPEG', 'quality': 100, 'subsampling': 0,
                                 'resize': False, 'enhancement': False})
    return tuple(transformed), {'version': VERSION, 'bundle_root': str(root),
                               'artifact_retention': 'EPHEMERAL', 'frames': ledger,
                               'source_metadata_preserved': True,
                               'note': 'Original bytes unchanged. Derived JPEG is a declared crop, not new visual evidence. Derived paths exist only during the caller-owned request scope; hashes and crop parameters permit reconstruction.'}
