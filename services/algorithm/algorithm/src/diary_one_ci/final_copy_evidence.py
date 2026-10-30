"""Bound the final copy verdict to images actually supplied for each memory.

This assembles input, not a visual verdict. A valid reference or a supplied
image does not establish that its source fact is true.
"""
from collections import Counter
from pathlib import Path


VERSION = 'FINAL_COPY_SHOWN_FRAME_SCOPE_V01'


def build_final_copy_scope(items, assets, bundle, max_frames=24):
    """Return gateway evidence tuples and an explicit per-memory image scope.

    Round-robin allocation prevents the first long chapter consuming the image
    budget. Moment facts must already be narrowed by ``memory_specs``; optional
    focus_frame_ids only prioritize references and can never authorize new ones.
    """
    # None builds a validated reference directory, not a model request. Actual
    # requests below still contain only one claim's exact images, bounded at 24.
    if max_frames is not None and (type(max_frames) is not int or not 0 <= max_frames <= 24):
        raise ValueError('max_frames must be None or an integer from 0 to 24')
    root = Path(bundle.manifest_path).resolve().parent
    issues, rows, queues, available = [], [], [], {}
    id_counts = Counter(item.get('id') for item in items)
    for item in items:
        mid = item.get('id')
        row = {'id': mid, 'kind': item.get('kind'), 'shown_frame_ids': [],
               'shown_refs': [], 'unshown_refs': [], 'visual_check_available': False}
        rows.append(row)
        queue, refs = [], []
        queues.append(queue)
        if not isinstance(mid, str) or not mid or id_counts[mid] != 1:
            issues.append({'memory_id': mid, 'code': 'AMBIGUOUS_MEMORY_ID'})
            continue
        fact_ids = item.get('fact_ids', [])
        for fact in item.get('facts', []):
            aid, fid = fact.get('asset_id'), fact.get('id')
            asset = assets.get(aid)
            error = None
            if fid not in fact_ids:
                error = 'FACT_NOT_OWNED_BY_MEMORY'
            elif not isinstance(asset, dict):
                error = 'UNKNOWN_ASSET'
            elif fact.get('source_asset_id', asset.get('asset_id')) != asset.get('asset_id'):
                error = 'SOURCE_ASSET_MISMATCH'
            if error:
                issues.append({'memory_id': mid, 'fact_id': fid, 'asset_id': aid, 'code': error})
                continue
            frames = asset.get('frames', [])
            counts = Counter(f.get('frame_id') for f in frames)
            index = {f.get('frame_id'): f for f in frames}
            for frame_id in fact.get('evidence_frame_ids', []):
                ref = {'fact_id': fid, 'asset_id': aid, 'source_asset_id': asset.get('asset_id'),
                       'frame_id': frame_id}
                frame = index.get(frame_id)
                error = None
                if frame is None or counts[frame_id] != 1:
                    error = 'FRAME_NOT_UNIQUELY_OWNED_BY_ASSET'
                else:
                    relative = frame.get('relative_path')
                    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
                        error = 'INVALID_IMAGE_PATH'
                    else:
                        path = (root / relative).resolve()
                        try:
                            path.relative_to(root)
                            readable = path.is_file() and path.stat().st_size > 0
                        except (OSError, ValueError):
                            readable = False
                        if not readable:
                            error = 'IMAGE_UNAVAILABLE_OR_OUTSIDE_BUNDLE'
                if error:
                    row['unshown_refs'].append({**ref, 'reason': error})
                    issues.append({'memory_id': mid, **ref, 'code': error})
                    continue
                key = (aid, frame_id)
                available[key] = (asset, frame, path)
                if key not in queue:
                    queue.append(key)
                if ref not in refs:
                    refs.append(ref)
        focus = item.get('focus_frame_ids', [])
        queue.sort(key=lambda key: key[1] not in focus)
        row['_refs'] = refs

    # Each turn grants one new input image to each memory. Shared input images
    # consume only one slot while retaining each memory's independent fact map.
    selected = []
    positions = [0] * len(queues)
    limit = len(available) if max_frames is None else max_frames
    while len(selected) < limit:
        progress = False
        for i, queue in enumerate(queues):
            while positions[i] < len(queue) and queue[positions[i]] in selected:
                positions[i] += 1
            if positions[i] < len(queue):
                selected.append(queue[positions[i]])
                positions[i] += 1
                progress = True
                if len(selected) == limit:
                    break
        if not progress:
            break
    selected_set = set(selected)
    for row in rows:
        for ref in row.pop('_refs', []):
            if (ref['asset_id'], ref['frame_id']) in selected_set:
                row['shown_refs'].append(ref)
                if ref['frame_id'] not in row['shown_frame_ids']:
                    row['shown_frame_ids'].append(ref['frame_id'])
            else:
                row['unshown_refs'].append({**ref, 'reason': 'IMAGE_BUDGET'})
        row['visual_check_available'] = bool(row['shown_refs'])
    scope = {'version': VERSION, 'max_frames': max_frames, 'bundle_root': str(root),
             'allocation_mode': 'REFERENCE_DIRECTORY' if max_frames is None else 'BOUNDED_PRESELECTION',
             'max_claim_frames': 24,
             'scope_notice': 'Images are available evidence, not verified visual truth. Judge each memory only from its own shown_refs. Unshown facts cannot establish visual relations.',
             'shown_frames': [{'asset_id': aid, 'source_asset_id': assets[aid]['asset_id'], 'frame_id': frame_id}
                              for aid, frame_id in selected],
             'memories': rows, 'issues': issues}
    return tuple(available[key] for key in selected), scope


def build_final_claim_batches(context_items, evidence, evidence_scope):
    """Group immutable claims only when their complete ordered input images agree.

    Old fact/observation prose is deliberately absent from the model context.
    The full facts remain with the caller for deterministic reference checks.
    Missing evidence is local to a claim; it never authorizes a substitute image.
    """
    scopes = {row['id']: row for row in (evidence_scope or {}).get('memories', [])}
    images, counts = {}, Counter()
    for asset, frame, path in evidence:
        key = (asset['asset_id'], frame['frame_id'])
        counts[key] += 1
        images[key] = (asset, frame, path)
    claims, batches, grouped = [], [], {}
    for memory in context_items:
        specifications = [('TITLE', None, memory['title'], memory['title_fact_ids'], memory['title_evidence'])]
        specifications.extend(('SENTENCE', s['source_index'], s['draft_text'], s['fact_ids'], s['facts'])
                              for s in memory['sentence_checks'])
        shown = scopes.get(memory['id'], {}).get('shown_refs', [])
        for field, source_index, text, fact_ids, facts in specifications:
            claim = {'claim_id': 'Q%03d' % (len(claims) + 1), 'memory_id': memory['id'], 'kind': memory['kind'],
                     'field': field, 'source_index': source_index, 'text': text,
                     'fact_ids': list(fact_ids), 'frame_refs': []}
            claims.append(claim)
            keys, issues = [], []
            for fact in facts:
                fid, aid = fact['id'], fact['asset_id']
                wanted = fact.get('evidence_frame_ids', [])
                if not wanted:
                    issues.append('NO_FRAME_REFERENCES:' + fid)
                for frame_id in wanted:
                    matches = [ref for ref in shown if ref.get('fact_id') == fid and ref.get('asset_id') == aid
                               and ref.get('frame_id') == frame_id]
                    sources = {ref.get('source_asset_id') for ref in matches}
                    if len(sources) != 1:
                        issues.append('NO_UNIQUE_BOUND_IMAGE:' + fid + ':' + frame_id)
                        continue
                    source = next(iter(sources)); key = (source, frame_id)
                    if counts[key] != 1:
                        issues.append('IMAGE_NOT_ATTACHED:' + fid + ':' + frame_id)
                        continue
                    asset, frame, _ = images[key]
                    claim['frame_refs'].append({'fact_id': fid, 'asset_id': aid, 'source_asset_id': source,
                        'frame_id': frame_id, 'media_kind': asset['media_kind'],
                        'source_timestamp_ms': frame.get('source_timestamp_ms')})
                    if key not in keys:
                        keys.append(key)
            # Canonical temporal order within each source; source IDs do not
            # imply capture order or a continuous route between source clips.
            keys.sort(key=lambda key: (key[0], images[key][1].get('source_timestamp_ms') is None,
                                      images[key][1].get('source_timestamp_ms') or 0, key[1]))
            if issues or not keys:
                claim.update(status='NOT_EVALUATED', reason='; '.join(issues) or 'NO_BOUND_IMAGES')
                continue
            if len(keys) > 24:
                claim.update(status='NOT_EVALUATED', reason='CLAIM_IMAGE_BUDGET_EXCEEDED')
                continue
            key = tuple(keys)
            if key not in grouped:
                batch = {'batch_id': 'B%03d' % (len(batches) + 1), 'claims': [],
                         'evidence': tuple(images[k] for k in keys)}
                batches.append(batch); grouped[key] = batch
            grouped[key]['claims'].append(claim)
            claim['batch_id'] = grouped[key]['batch_id']
    return {'claims': claims, 'batches': batches}
