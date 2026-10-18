"""Validate the frozen output schema and bind every public reference to this input."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from PIL import Image

# Byte-for-byte snapshot of algorithm/contracts/codex_x02_staged_preview_v04_1_media_v01_input_v04.schema.json.
SCHEMA_PATH = Path(__file__).parent / 'contracts' / 'x02_staged_preview_v04_1.schema.json'
SCHEMA_SHA256 = hashlib.sha256(SCHEMA_PATH.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
VALIDATOR = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding='utf-8')))


def validate_result_contract(result: dict[str, Any], manifest_bytes: bytes, bundle_dir: Path | None = None) -> None:
    # Never trust an upstream admission marker; only this worker may attach it.
    payload = {key: value for key, value in result.items() if key != '_publish'}
    error = next(VALIDATOR.iter_errors(payload), None)
    if error:
        raise ValueError('result_schema_invalid:' + '/'.join(map(str, error.absolute_path)))
    manifest = json.loads(manifest_bytes)
    if result['bundle_manifest_sha256'] != hashlib.sha256(manifest_bytes).hexdigest():
        raise ValueError('result_manifest_mismatch')
    if result['session_id'] != manifest['session']['session_id']:
        raise ValueError('result_session_mismatch')
    assets = {asset['asset_id']: asset for asset in manifest['assets']}
    if len(assets) != len(manifest['assets']):
        raise ValueError('duplicate_input_asset')
    frames = {}
    for asset_id, asset in assets.items():
        for frame in asset['frames']:
            if frame['frame_id'] in frames:
                raise ValueError('duplicate_input_frame')
            frames[frame['frame_id']] = (asset_id, frame)

    def refs(row: dict[str, Any], asset_id: str | None = None) -> None:
        for key in ('asset_id', 'source_asset_id', 'hero_asset_id'):
            if key in row and row[key] is not None and row[key] not in assets:
                raise ValueError('unknown_asset_reference')
        for key in ('source_asset_ids', 'unresolved_asset_ids'):
            if any(item not in assets for item in row.get(key, [])):
                raise ValueError('unknown_asset_reference')
        for frame_id in row.get('evidence_frame_ids', []):
            if frame_id not in frames or (asset_id and frames[frame_id][0] != asset_id):
                raise ValueError('unknown_or_cross_asset_frame')

    observations = {row['id']: row for row in result['observations']}
    moments = {row['id']: row for row in result['moments']}
    if len(observations) != len(result['observations']) or len(moments) != len(result['moments']):
        raise ValueError('duplicate_evidence_identity')
    refs(result)
    facts = {}
    for row in observations.values():
        refs(row, row['asset_id'])
        if row['media_kind'] != assets[row['asset_id']]['media_kind']:
            raise ValueError('evidence_media_kind_mismatch')
        for fact in row.get('facts', []):
            refs(fact, row['asset_id'])
            if fact['fact_id'] in facts:
                raise ValueError('duplicate_fact_identity')
            facts[fact['fact_id']] = fact
    for row in moments.values():
        refs(row)
        if any(item not in observations for item in row.get('observation_ids', [])):
            raise ValueError('unknown_observation_reference')

    public = {}
    selected_frames = set()
    for kind, rows in [('CHAPTER', result['chapters']), ('AHA', result['ahas'])]:
        for row in rows:
            key = (kind, row['id'])
            if key in public:
                raise ValueError('duplicate_memory_identity')
            public[key] = row
            refs(row)
            if any(item not in moments for item in row.get('moment_ids', [])):
                raise ValueError('unknown_moment_reference')
            if row['publication_status'] != 'STAGED_PREVIEW_VALIDATED':
                raise ValueError('unvalidated_public_memory')
            for claim in row.get('claims', []):
                refs(claim)
                fact = facts.get(claim['fact_id'])
                if not fact or not set(claim['evidence_frame_ids']).issubset(set(fact['evidence_frame_ids'])):
                    raise ValueError('claim_fact_lineage_mismatch')
            media = row.get('selected_media', [])
            if not media:
                raise ValueError('public_memory_missing_media')
            hero = [item for item in media if item.get('role') == 'HERO']
            if hero and (len(hero) != 1 or hero[0]['asset_id'] != row['hero_asset_id']):
                raise ValueError('hero_reference_mismatch')
            if row['hero_asset_id'] not in {item['asset_id'] for item in media}:
                raise ValueError('hero_not_selected')
            for item in media:
                refs(item, item['asset_id'])
                observation = observations.get(item.get('observation_id'))
                if not observation or observation['asset_id'] != item['asset_id']:
                    raise ValueError('selected_observation_mismatch')
                if item.get('source_asset_id') != item['asset_id'] or item['media_kind'] != assets[item['asset_id']]['media_kind']:
                    raise ValueError('selected_media_lineage_mismatch')
                if not item.get('evidence_frame_ids'):
                    raise ValueError('selected_media_missing_frames')
                selected_frames.update(item['evidence_frame_ids'])

    visible = set()
    outcomes = set()
    for row in result['selected_memory_outcomes']:
        key = (row['memory_type'], row['memory_id'])
        if key in outcomes:
            raise ValueError('duplicate_memory_outcome')
        outcomes.add(key)
        if row['visibility_state'] == 'VISIBLE_PREVIEW':
            visible.add(key)
    if visible != set(public):
        raise ValueError('visible_memory_set_mismatch')
    if result['delivery_state'] == 'NO_GROUNDED_MEMORY' and public:
        raise ValueError('nonempty_honest_empty')
    if result['delivery_state'].startswith('READY_') and not public:
        raise ValueError('ready_without_public_memory')

    if bundle_dir is not None:
        root = bundle_dir.resolve()
        for frame_id in selected_frames:
            _, frame = frames[frame_id]
            path = (root / frame['relative_path']).resolve()
            if not path.is_relative_to(root):
                raise ValueError('selected_media_missing_or_unsafe')
            # BFF stores multipart uploads by their exact frame ID; retain the same
            # canonical mapping as x02_proxy, without substituting a different frame.
            if not path.is_file():
                path = (root / 'frames' / (frame_id + '.jpg')).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError('selected_media_missing_or_unsafe')
            if hashlib.sha256(path.read_bytes()).hexdigest() != frame['sha256']:
                raise ValueError('selected_media_hash_mismatch')
            with Image.open(path) as image:
                if image.size != (frame['width'], frame['height']):
                    raise ValueError('selected_media_dimensions_mismatch')
                image.verify()
