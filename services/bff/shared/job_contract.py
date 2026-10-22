"""Algorithm output publication checks; upload/auth remain owned by the remote BFF."""

def validate_real_result(result):
    if not isinstance(result, dict) or result.get('schema_version') not in (
        'DIARY_ONE_X02_STAGED_PREVIEW_V04_1', 'DIARY_ONE_X02_PRODUCT_PREVIEW_V01'):
        raise ValueError('Unexpected X02 result schema')
    if result.get('dev_lite_fallback') or result.get('delivery_state') == 'PIPELINE_BLOCKED':
        raise ValueError('X02 did not produce a publishable real result')
    if result.get('delivery_state') not in ('NO_GROUNDED_MEMORY', 'READY_PRIMARY_COPY',
        'READY_WITH_GROUNDED_COPY_FALLBACK', 'READY_WITH_ITEM_BLOCKS'):
        raise ValueError('Unknown or missing delivery state')
    for name in ('chapters', 'ahas', 'selected_memory_outcomes'):
        if not isinstance(result.get(name), list):
            raise ValueError(f'Missing X02 {name}')
    outcomes = result['selected_memory_outcomes']
    if any(not isinstance(o, dict) or not isinstance(o.get('memory_id'), str)
           or o.get('memory_type') not in ('CHAPTER', 'AHA')
           or o.get('visibility_state') not in ('VISIBLE_PREVIEW', 'DIAGNOSTIC_ONLY') for o in outcomes):
        raise ValueError('Invalid memory outcomes')
    if result['delivery_state'] == 'NO_GROUNDED_MEMORY' and (outcomes or result['chapters'] or result['ahas']):
        raise ValueError('Empty-day state contains memories')
    for kind, name in [('CHAPTER', 'chapters'), ('AHA', 'ahas')]:
        for item in result[name]:
            if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'] or not isinstance(item.get('story'), str):
                raise ValueError('Invalid memory shape')
            if kind == 'CHAPTER' and (not isinstance(item.get('title'), str) or not item['title']
                or not isinstance(item.get('tags'), list) or any(not isinstance(tag, str) for tag in item['tags'])):
                raise ValueError('Invalid chapter shape')
            if kind == 'CHAPTER' and 'highlights' in item:
                highlights = item['highlights']
                if (not isinstance(highlights, list) or len(highlights) > 2 or any(
                    not isinstance(h, dict) or not isinstance(h.get('id'), str) or not h['id']
                    or not isinstance(h.get('story'), str) or not h['story'].strip()
                    or h.get('parent_chapter_id') != item['id'] for h in highlights)
                    or len({h['id'] for h in highlights}) != len(highlights)):
                    raise ValueError('Invalid chapter highlights')
            if kind == 'CHAPTER' and 'preview_story' in item and (
                not isinstance(item['preview_story'], str) or not item['preview_story'].strip()):
                raise ValueError('Invalid chapter preview')
            if item.get('publication_status') == 'STAGED_PREVIEW_VALIDATED' and not any(
                o.get('memory_type') == kind and o.get('memory_id') == item['id']
                and o.get('visibility_state') == 'VISIBLE_PREVIEW' for o in outcomes
            ):
                raise ValueError('Published memory is missing its outcome')
    visible = [o for o in outcomes if o['visibility_state'] == 'VISIBLE_PREVIEW']
    if result['delivery_state'] != 'NO_GROUNDED_MEMORY' and not visible:
        raise ValueError('Ready result has no visible memories')
    for outcome in visible:
        items = result['chapters'] if outcome['memory_type'] == 'CHAPTER' else result['ahas']
        if not any(item['id'] == outcome['memory_id'] and item.get('publication_status') == 'STAGED_PREVIEW_VALIDATED' for item in items):
            raise ValueError('Visible outcome refers to an unpublished memory')
    trace = result.get('trace')
    if ((isinstance(trace, dict) and trace.get('pipeline_version') in ('X02_PRODUCT_EDITOR_V06', 'X02_PRODUCT_EDITOR_V07'))
            or result.get('editor_policy') in ('EXPERIENCE_HIGHLIGHTS_NATURAL_COPY_V06', 'EXPERIENCE_HIGHLIGHTS_NATURAL_COPY_V07')):
        _validate_v06_chapter_images(result)


def _validate_v06_chapter_images(result):
    """Preserve and validate explicit V06/V07 image references before persistence.

    This is a result contract check. Actual JPEG existence/checksums require the
    uploaded bundle and remain verified by the algorithm and offline evaluator.
    Earlier preview versions do not have this image-selection contract.
    """
    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def refs(value, allowed):
        return (isinstance(value, list) and bool(value)
                and all(isinstance(item, str) for item in value)
                and len(value) == len(set(value)) and set(value) <= set(allowed))

    trace = result.get('trace')
    v7 = (result.get('editor_policy') == 'EXPERIENCE_HIGHLIGHTS_NATURAL_COPY_V07' or
          (isinstance(trace, dict) and trace.get('pipeline_version') == 'X02_PRODUCT_EDITOR_V07'))
    scene_kinds = ('ZOO_ANIMALS', 'CYCLING', 'CITYWALK', 'FISHING', 'FLY_FISHING', 'KAYAK_FISHING', 'FAMILY_OUTING', 'CHILDREN_PLAY', 'COOKING', 'DINING', 'MARKET_SHOPPING', 'NATURE_WALK', 'GARDEN', 'PARK_LEISURE', 'OUTDOOR_SCENERY', 'MUSEUM', 'OTHER', 'UNCERTAIN') if v7 else ('ZOO_ANIMALS', 'CYCLING', 'CITYWALK', 'OTHER', 'UNCERTAIN')
    decision = result.get('decision_trace')
    verified = decision.get('verified_facts') if isinstance(decision, dict) else None
    if result['chapters'] and not isinstance(verified, dict):
        raise ValueError('V06 chapter images require verified facts')
    for chapter in result['chapters']:
        raw_claims = chapter.get('claims')
        if (not isinstance(raw_claims, list) or not raw_claims
                or any(not isinstance(fact, dict) or not nonempty(fact.get('id')) for fact in raw_claims)):
            raise ValueError('V06 chapter images require identified claims')
        claims = {fact['id']: fact for fact in raw_claims}
        if (len(claims) != len(raw_claims) or any(fact != verified.get(fid)
                or fact.get('visual_reviewed') is not True or not nonempty(fact.get('source_asset_id'))
                or not refs(fact.get('evidence_frame_ids'), fact.get('evidence_frame_ids') or [])
                for fid, fact in claims.items())):
            raise ValueError('V06 chapter claims must match image-verified facts')
        focus = chapter.get('selection_focus')
        if (not isinstance(focus, dict) or focus.get('experience_kind') not in scene_kinds
                or not nonempty(focus.get('focus')) or not refs(focus.get('fact_ids'), claims)):
            raise ValueError('Invalid V06 chapter selection_focus')
        selected = chapter.get('selected_media')
        if not isinstance(selected, list) or not 1 <= len(selected) <= 5:
            raise ValueError('Invalid V06 chapter selected_media')
        seen_assets, seen_frames = set(), set()
        heroes = []
        for media in selected:
            if not isinstance(media, dict):
                raise ValueError('Invalid V06 selected image')
            aid, source = media.get('asset_id'), media.get('source_asset_id')
            frame, fact_ids = media.get('representative_frame_id'), media.get('selection_fact_ids')
            evidence = media.get('evidence_frame_ids')
            if (not nonempty(aid) or not nonempty(source) or not nonempty(frame)
                    or not refs(fact_ids, claims) or not isinstance(evidence, list) or not evidence
                    or not all(nonempty(fid) for fid in evidence) or len(evidence) != len(set(evidence))
                    or evidence[0] != frame):
                raise ValueError('Invalid V06 representative frame references')
            if any(claims[fid].get('source_asset_id') != source
                   or frame not in (claims[fid].get('evidence_frame_ids') or []) for fid in fact_ids):
                raise ValueError('V06 representative frame is not supported by its asset facts')
            if media.get('selection_role') not in (('PRIMARY', 'DETAIL', 'CONTEXT', 'SUPPORT') if v7 else ('PRIMARY', 'DETAIL', 'CONTEXT')) or not nonempty(media.get('selection_reason')):
                raise ValueError('Invalid V06 image selection rationale')
            if source in seen_assets or (source, frame) in seen_frames:
                raise ValueError('Duplicate V06 chapter representative image')
            seen_assets.add(source)
            seen_frames.add((source, frame))
            if media.get('role') == 'HERO':
                heroes.append(media)
        if (len(heroes) != 1 or chapter.get('hero_asset_id') != heroes[0]['asset_id']
                or chapter.get('hero_frame_id') != heroes[0]['representative_frame_id']
                or not nonempty(chapter.get('hero_reason'))):
            raise ValueError('V06 cover must match its selected representative image')
