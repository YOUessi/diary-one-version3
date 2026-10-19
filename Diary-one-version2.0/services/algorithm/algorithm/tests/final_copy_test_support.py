"""Real temporary JPEG inputs plus explicitly scripted verdicts for unit tests.

These pixels test binding and transport, not the truth of the synthetic text.
"""
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from PIL import Image
from diary_one_ci import final_copy_evidence, product_editor as p


@contextmanager
def bound_test_images(items):
    with TemporaryDirectory(prefix='diary-copy-fixture-') as directory:
        root = Path(directory); memories = deepcopy(items); assets = {}
        for memory in memories:
            for fact in memory['facts']:
                aid = fact['asset_id']; source = fact.get('source_asset_id', aid)
                asset = assets.setdefault(aid, {'asset_id': source, 'media_kind': 'VIDEO', 'frames': []})
                fact.setdefault('evidence_frame_ids', ['fixture-' + fact['id']])
                fact.setdefault('frame_pts_ms', [0] * len(fact['evidence_frame_ids']))
                for index, fid in enumerate(fact['evidence_frame_ids']):
                    if any(f['frame_id'] == fid for f in asset['frames']):
                        continue
                    path = root / (aid + '_' + fid + '.jpg')
                    Image.new('RGB', (48, 32), (40, 100, 80)).save(path)
                    asset['frames'].append({'frame_id': fid, 'relative_path': path.name,
                        'sha256': sha256(path.read_bytes()).hexdigest(), 'width': 48, 'height': 32,
                        'source_timestamp_ms': index * 1000})
        bundle = SimpleNamespace(manifest_path=root / 'bundle.json')
        evidence, scope = final_copy_evidence.build_final_copy_scope(memories, assets, bundle)
        yield memories, evidence, scope


def write_and_review_with_test_images(items, stages, **kwargs):
    with bound_test_images(items) as (memories, evidence, scope):
        return p.write_and_review(memories, stages, **kwargs,
            final_evidence=evidence, final_evidence_scope=scope)
