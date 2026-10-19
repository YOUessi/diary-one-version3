"""Frozen output schemas plus input/evidence binding, independent of generation.

Product's public V01 envelope contains several editor revisions. Version-specific
checks below preserve its fact/asset namespaces instead of imposing V04.1's model.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator
from PIL import Image

from shared.job_contract import validate_real_result

CONTRACT_VERSION = 'DIARY_ONE_INPUT_BOUND_RESULT_V01'
STAGED = 'DIARY_ONE_X02_STAGED_PREVIEW_V04_1'
PRODUCT = 'DIARY_ONE_X02_PRODUCT_PREVIEW_V01'
SCHEMA_PATHS = {
    STAGED: Path(__file__).parent / 'contracts/x02_staged_preview_v04_1.schema.json',
    PRODUCT: Path(__file__).parent / 'contracts/x02_product_preview_v01.schema.json',
}
SCHEMA_SHA256 = {key: hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                 for key, path in SCHEMA_PATHS.items()}
VALIDATORS = {key: Draft202012Validator(json.loads(path.read_text()),
              format_checker=Draft202012Validator.FORMAT_CHECKER) for key, path in SCHEMA_PATHS.items()}


def app_asset_id(source: str) -> str:
    value = source[6:] if source.startswith('asset_') else source
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return value


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _ids(value, allowed, *, required=False):
    _require(isinstance(value, list) and (not required or bool(value)) and
             all(isinstance(x, str) for x in value) and len(value) == len(set(value)) and
             set(value) <= set(allowed), 'invalid_or_unknown_references')
    return value


def _index(rows, key='id'):
    _require(isinstance(rows, list) and all(isinstance(x, dict) and isinstance(x.get(key), str)
                                         and x[key] for x in rows), 'invalid_reference_rows')
    result = {row[key]: row for row in rows}
    _require(len(result) == len(rows), 'duplicate_reference_identity')
    return result


def _reviewed_text(original, record):
    """Replay the declared original-text spans; never trust a revised full copy."""
    edits = record.get('corrections')
    _require(isinstance(edits, list), 'missing_visual_corrections')
    if record.get('decision') == 'KEEP':
        _require(not edits, 'keep_has_corrections')
        return original.strip()
    _require(record.get('decision') == 'CORRECT' and bool(edits), 'invalid_visual_decision')
    characters = lambda text: ''.join(c.lower() for c in text if c.isalnum())
    spans = []
    for edit in edits:
        before, after = edit.get('rejected_text'), edit.get('replacement_text')
        _require(isinstance(before, str) and isinstance(after, str) and bool(characters(before))
                 and original.count(before) == 1 and characters(before) != characters(after),
                 'invalid_visual_correction_span')
        start = original.index(before)
        spans.append((start, start + len(before), after))
    spans.sort()
    _require(all(left[1] <= right[0] for left, right in zip(spans, spans[1:])), 'overlapping_visual_corrections')
    pieces, cursor = [], 0
    for start, end, after in spans:
        pieces.extend((original[cursor:start], after))
        cursor = end
    value = ''.join(pieces) + original[cursor:]
    _require(bool(value.strip()) and characters(value) != characters(original) and
             all(characters(e['rejected_text']) not in characters(value) for e in edits), 'unapplied_visual_corrections')
    return value.strip()


def validate_result_contract(result, manifest_bytes, bundle_dir=None):
    """Return the exact contract hash after complete binding; never trusts _publish."""
    _require(isinstance(result, dict), 'invalid_result_object')
    schema = result.get('schema_version')
    _require(schema in VALIDATORS, 'unsupported_result_schema')
    payload = {key: value for key, value in result.items() if key != '_publish'}
    error = next(VALIDATORS[schema].iter_errors(payload), None)
    if error:
        raise ValueError('result_schema_invalid:' + '/'.join(map(str, error.absolute_path)))
    validate_real_result(payload)
    _require(isinstance(manifest_bytes, bytes) and bool(manifest_bytes), 'missing_input_manifest')
    manifest = json.loads(manifest_bytes)
    _require(result.get('bundle_manifest_sha256') == hashlib.sha256(manifest_bytes).hexdigest(),
             'result_manifest_mismatch')
    _require(result.get('session_id') == manifest['session']['session_id'], 'result_session_mismatch')
    if schema == PRODUCT or bundle_dir is not None:
        _require(bundle_dir is not None and Path(bundle_dir).is_dir(), 'missing_input_evidence')
    assets = _index(manifest['assets'], 'asset_id')
    aliases = {app_asset_id(aid): aid for aid in assets}
    internal_aliases = {aid: 'V%03d' % (i + 1) for i, aid in enumerate(assets)}
    _require(len(aliases) == len(assets), 'ambiguous_app_asset_identity')
    frames = {}
    for aid, asset in assets.items():
        _require(asset.get('media_kind') in ('PHOTO', 'VIDEO'), 'invalid_input_media_kind')
        for fid, frame in _index(asset['frames'], 'frame_id').items():
            _require(fid not in frames, 'duplicate_input_frame')
            frames[fid] = (aid, frame)
    checked_frames = set()

    def frame_refs(ids, source=None, required=False):
        for fid in _ids(ids, frames, required=required):
            _require(source is None or frames[fid][0] == source, 'cross_asset_frame')
            checked_frames.add(fid)

    def source_of(row):
        source = row.get('source_asset_id')
        if source is None:
            source = aliases.get(row.get('asset_id'))
        _require(source in assets, 'unknown_source_asset')
        if 'asset_id' in row:
            _require(row['asset_id'] == app_asset_id(source), 'app_source_asset_mismatch')
        return source

    observations = _index(result.get('observations'))
    observation_facts, fact_sources = {}, {}
    observed_sources = set()
    for oid, row in observations.items():
        source = source_of(row)
        observed_sources.add(source)
        _require(row.get('media_kind') == assets[source]['media_kind'], 'observation_media_kind_mismatch')
        frame_refs(row.get('evidence_frame_ids', []), source)
        for fid, fact in _index(row.get('facts', []), 'fact_id').items():
            _require(fid not in observation_facts, 'duplicate_fact_identity')
            frame_refs(fact.get('evidence_frame_ids', []), source, True)
            observation_facts[fid] = fact
            fact_sources[fid] = (source, oid)
    frame_refs(result.get('evidence_frame_ids', []))
    unresolved = _ids(result.get('unresolved_asset_ids', []), assets)
    _require(observed_sources | set(unresolved) == set(assets), 'missing_input_asset_accounting')
    if result.get('coverage_status') == 'COMPLETE':
        _require(not unresolved, 'complete_with_unresolved_input')
    if result['delivery_state'] == 'NO_GROUNDED_MEMORY':
        _require(not unresolved and all(o.get('status') != 'FAILED' for o in observations.values()),
                 'failed_input_is_not_honest_empty')
    moments = _index(result.get('moments'))
    moment_sources = {}
    if schema == STAGED:
        for mid, moment in moments.items():
            oids = _ids(moment.get('observation_ids', []), observations, required=True)
            sources = {source_of(observations[oid]) for oid in oids}
            source_ids = _ids(moment.get('source_asset_ids', []), assets, required=True)
            asset_ids = _ids(moment.get('asset_ids', []), aliases, required=True)
            _require(set(source_ids) == sources and set(asset_ids) == {app_asset_id(s) for s in sources},
                     'moment_observation_lineage_mismatch')
            frame_refs(moment.get('evidence_frame_ids', []))
            _require(all(frames[f][0] in sources for f in moment.get('evidence_frame_ids', [])),
                     'moment_frame_lineage_mismatch')
            moment_sources[mid] = sources

    verified = result.get('decision_trace', {}).get('verified_facts', {})
    chapter_structure, moment_structure = {}, {}
    product_version = None
    if schema == PRODUCT:
        _require(not moments, 'product_moments_must_use_selected_structure')
        product_version = result['editor_policy'].rsplit('_V', 1)[-1]
        _require(result['trace']['pipeline_version'] == 'X02_PRODUCT_EDITOR_V' + product_version,
                 'product_policy_pipeline_mismatch')
        _require(isinstance(verified, dict), 'invalid_verified_facts')
        trace = result['decision_trace']
        if int(product_version) <= 3:
            # Pre-visual-review revisions referenced the deterministic S04
            # catalog directly. Reconstruct it, never promote self-declared
            # public claims into a new "verified" source of truth.
            verified = {}
            for oid, observation in observations.items():
                if observation.get('status') not in ('OBSERVED', 'PARTIAL'):
                    continue
                source = source_of(observation)
                for fact in observation.get('facts', []):
                    if fact.get('support_grade') not in ('STRONG', 'MODERATE') or not fact.get('evidence_frame_ids'):
                        continue
                    fid = 'F%03d' % (len(verified) + 1)
                    verified[fid] = {**fact, 'id': fid, 'asset_id': internal_aliases[source],
                        'source_asset_id': source, 'observation_id': oid,
                        'frame_pts_ms': [frames[f][1].get('source_timestamp_ms') for f in fact['evidence_frame_ids']]}
            _require(all('selection_focus' not in c and 'hero_frame_id' not in c for c in result['chapters']),
                     'legacy_policy_with_new_image_contract')
        if int(product_version) >= 6:
            records = trace.get('visual_fact_ledger', []) + trace.get('recovery_visual_ledger', [])
            visual_records = {}
            for record in records:
                if record.get('status') == 'VERIFIED':
                    _require(record.get('fact_id') not in visual_records, 'duplicate_verified_fact_judgment')
                    visual_records[record['fact_id']] = record
        # Earlier product revisions may lack visual review. Their original fact
        # lineage remains required; V04+ cannot downgrade the visual evidence gate.
        for fid, fact in verified.items():
            _require(isinstance(fact, dict) and fact.get('id') == fid, 'invalid_verified_fact_identity')
            original = observation_facts.get(fact.get('fact_id'))
            _require(original is not None, 'verified_fact_missing_observation')
            source, oid = fact_sources[fact['fact_id']]
            _require(fact.get('source_asset_id') == source and fact.get('observation_id') == oid,
                     'verified_fact_source_mismatch')
            _require(fact.get('asset_id') == internal_aliases[source], 'verified_fact_internal_asset_mismatch')
            frame_refs(fact.get('evidence_frame_ids'), source, True)
            if int(product_version) >= 4:
                _require(fact.get('visual_reviewed') is True, 'unverified_public_fact')
            if int(product_version) >= 6:
                record = visual_records.get(fid)
                _require(record is not None and fact.get('original_text') == original['text'],
                         'visual_original_fact_mismatch')
                _require(fact['text'] == _reviewed_text(original['text'], record), 'visual_correction_text_mismatch')
                pts = [frames[f][1].get('source_timestamp_ms') for f in fact['evidence_frame_ids']]
                _require(fact.get('frame_pts_ms') == pts, 'fact_pts_mismatch')
                _require(fact.get('temporal_support') in ('STATE', 'CHANGE') and
                         (fact['temporal_support'] != 'CHANGE' or len({p for p in pts if p is not None}) >= 2),
                         'unsupported_temporal_change')
        if schema == PRODUCT:
            namespace = uuid.UUID(result['session_id'])
            structure = trace.get('selected_structure', {})
            for cid, chapter in _index(structure.get('chapters')).items():
                _ids(chapter.get('fact_ids'), verified, required=True)
                public_id = str(uuid.uuid5(namespace, result['editor_policy'] + ':chapter:' + cid))
                chapter_structure[public_id] = chapter
            for mid, moment in _index(structure.get('moments')).items():
                _require(moment.get('fact_id') in verified, 'unknown_structural_moment_fact')
                kind = 'highlight' if moment.get('parent_chapter_id') is not None else 'aha'
                public_id = str(uuid.uuid5(namespace, result['editor_policy'] + ':' + kind + ':' + mid))
                moment_structure[public_id] = moment

    def claims_for(row):
        claims = row.get('claims')
        _require(isinstance(claims, list) and claims, 'missing_public_claims')
        if schema == PRODUCT:
            mapped = _index(claims)
            for fid, fact in mapped.items():
                _require(fact == verified.get(fid), 'public_claim_verified_fact_mismatch')
                frame_refs(fact['evidence_frame_ids'], fact['source_asset_id'], True)
            return mapped
        mapped = _index(claims, 'fact_id')
        for fid, fact in mapped.items():
            _require(fact == observation_facts.get(fid), 'claim_fact_lineage_mismatch')
            frame_refs(fact['evidence_frame_ids'], fact_sources[fid][0], True)
        return mapped

    def media_for(row, claims, *, chapter=False, chapter_facts=None):
        media = row.get('selected_media')
        _require(isinstance(media, list) and 1 <= len(media) <= (5 if chapter else 1), 'invalid_selected_media_count')
        seen, heroes = set(), []
        for item in media:
            _require(isinstance(item, dict), 'invalid_selected_media')
            source = source_of(item)
            _require(source not in seen, 'duplicate_selected_asset')
            seen.add(source)
            asset = assets[source]
            _require(item.get('media_kind') == asset['media_kind'], 'selected_media_kind_mismatch')
            frame_refs(item.get('evidence_frame_ids'), source, True)
            if item.get('role') == 'HERO':
                heroes.append(item)
            if schema == STAGED:
                observation = observations.get(item.get('observation_id'))
                _require(observation is not None and source_of(observation) == source,
                         'selected_observation_mismatch')
            else:
                # A chapter gallery may show additional reviewed chapter facts
                # beyond its narrative claims. A moment has only its own claims.
                support = chapter_facts.values() if chapter_facts is not None else claims.values()
                supported = {f for fact in support if fact.get('source_asset_id') == source
                             for f in fact['evidence_frame_ids']}
                _require(set(item['evidence_frame_ids']) <= supported, 'selected_media_without_fact_support')
                if asset['media_kind'] == 'PHOTO':
                    _require(item.get('start_ms') is None and item.get('end_ms') is None and
                             item.get('focus_pts_ms') is None, 'photo_has_video_range')
                    if int(product_version) >= 7:
                        _require(item.get('range_basis') == 'STILL_IMAGE', 'photo_range_basis_mismatch')
                else:
                    _require(item.get('range_basis') in ('WHOLE_SOURCE_CLIP', 'EVIDENCE_CONTEXT_WINDOW_NOT_EVENT_BOUNDARIES'),
                             'video_range_basis_mismatch')
                    duration = asset.get('original_duration_ms')
                    start, end, focus = (item.get(k) for k in ('start_ms', 'end_ms', 'focus_pts_ms'))
                    _require(isinstance(duration, int) and duration > 0 and isinstance(start, int) and
                             isinstance(end, int) and 0 <= start < end <= duration, 'invalid_video_range')
                    _require(focus is None or (isinstance(focus, int) and start <= focus <= end), 'invalid_focus_pts')
                    if item.get('range_basis') == 'WHOLE_SOURCE_CLIP':
                        _require(start == 0 and end == duration, 'whole_source_range_mismatch')
                    if focus is not None:
                        _require(focus in [frames[f][1].get('source_timestamp_ms') for f in item['evidence_frame_ids']],
                                 'focus_pts_not_evidenced')
        if chapter:
            _require(len(heroes) == 1 and row.get('hero_asset_id') == heroes[0]['asset_id'], 'hero_reference_mismatch')
        elif schema == STAGED:
            _require(row.get('hero_asset_id') == media[0]['asset_id'], 'aha_hero_reference_mismatch')
        return seen

    public, all_public_ids = set(), set()
    for kind, rows in [('CHAPTER', result['chapters']), ('AHA', result['ahas'])]:
        for row in rows:
            key = (kind, row['id'])
            _require(row['id'] not in all_public_ids, 'duplicate_memory_identity')
            all_public_ids.add(row['id'])
            public.add(key)
            _require(row.get('publication_status') == 'STAGED_PREVIEW_VALIDATED', 'unvalidated_public_memory')
            _require(isinstance(row.get('story'), str) and bool(row['story'].strip()), 'empty_public_story')
            claims = claims_for(row)
            chapter_facts = None
            if schema == PRODUCT:
                if kind == 'CHAPTER':
                    structure = chapter_structure.get(row['id'])
                    _require(structure is not None and set(claims) <= set(structure['fact_ids']),
                             'chapter_structure_claim_mismatch')
                    chapter_facts = {fid: verified[fid] for fid in structure['fact_ids']}
                else:
                    structure = moment_structure.get(row['id'])
                    _require(structure is not None and structure.get('parent_chapter_id') is None and
                             set(claims) == {structure['fact_id']}, 'aha_structure_claim_mismatch')
            selected = media_for(row, claims, chapter=kind == 'CHAPTER', chapter_facts=chapter_facts)
            frame_refs(row.get('evidence_frame_ids', []))
            if schema == STAGED:
                mids = _ids(row.get('moment_ids'), moments, required=True)
                sources = set().union(*(moment_sources[mid] for mid in mids))
                _require(selected <= sources and {fact_sources[fid][0] for fid in claims} <= sources
                         and all(frames[f][0] in sources for f in row.get('evidence_frame_ids', [])),
                         'memory_moment_lineage_mismatch')
            elif kind == 'CHAPTER':
                _ids(row.get('title_claim_ids', []), claims)
                for sentence in row['sentence_claims']:
                    _require(isinstance(sentence, dict) and isinstance(sentence.get('text'), str)
                             and bool(sentence['text'].strip()), 'invalid_sentence_claim')
                    _ids(sentence.get('fact_ids'), claims, required=True)
                for highlight in row['highlights']:
                    _require(highlight['id'] not in all_public_ids and highlight['parent_chapter_id'] == row['id'],
                             'invalid_nested_highlight_identity')
                    all_public_ids.add(highlight['id'])
                    highlighted_claims = claims_for(highlight)
                    # A highlight can come from a chapter fact not selected for
                    # its five gallery slots. Its source must belong to this chapter.
                    chapter_sources = {f['source_asset_id'] for f in (chapter_facts or claims).values()} | selected
                    _require({f['source_asset_id'] for f in highlighted_claims.values()} <= chapter_sources,
                             'highlight_outside_parent_chapter')
                    if schema == PRODUCT:
                        moment = moment_structure.get(highlight['id'])
                        _require(moment is not None and moment.get('parent_chapter_id') == structure['id']
                                 and set(highlighted_claims) == {moment['fact_id']}
                                 and set(highlighted_claims) <= set(chapter_facts), 'highlight_structure_claim_mismatch')
                    media_for(highlight, highlighted_claims)
    outcomes = set()
    visible = set()
    for row in result['selected_memory_outcomes']:
        key = (row['memory_type'], row['memory_id'])
        _require(key not in outcomes, 'duplicate_memory_outcome')
        outcomes.add(key)
        if row['visibility_state'] == 'VISIBLE_PREVIEW':
            visible.add(key)
    _require(visible == public, 'visible_memory_set_mismatch')
    if schema == PRODUCT:
        structural_outcomes = {('CHAPTER', cid) for cid in chapter_structure}
        structural_outcomes.update(('AHA', mid) for mid, m in moment_structure.items() if m.get('parent_chapter_id') is None)
        _require(outcomes == structural_outcomes, 'outcome_selected_structure_mismatch')

    # Preserve the remote V04.1 validator's metadata-only testing interface.
    # The new Product contract always requires the uploaded evidence above.
    if bundle_dir is None:
        return SCHEMA_SHA256[schema]
    root = Path(bundle_dir).resolve()
    # Empty output must not turn a missing/corrupt upload into a bound success.
    # Validate all submitted evidence, including unselected/insufficient frames.
    for fid in sorted(frames):
        frame = frames[fid][1]
        relative = frame.get('relative_path')
        _require(isinstance(relative, str) and relative and not Path(relative).is_absolute(), 'unsafe_evidence_path')
        path = (root / relative).resolve()
        _require(path.is_relative_to(root), 'unsafe_evidence_path')
        if not path.is_file():
            _require(re.fullmatch(r'[A-Za-z0-9_-]{1,200}', fid) is not None, 'unsafe_frame_id')
            path = (root / 'frames' / (fid + '.jpg')).resolve()
        _require(path.is_relative_to(root) and path.is_file(), 'missing_input_frame')
        _require(hashlib.sha256(path.read_bytes()).hexdigest() == frame.get('sha256'), 'evidence_hash_mismatch')
        with Image.open(path) as image:
            _require(image.format == 'JPEG' and image.size == (frame.get('width'), frame.get('height')),
                     'evidence_format_or_dimensions_mismatch')
            image.verify()
        with Image.open(path) as image:
            image.load()  # verify alone does not decode truncated image data.
    return SCHEMA_SHA256[schema]
