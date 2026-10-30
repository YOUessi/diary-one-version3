"""Trace and preserve visual evidence for provisional Chapter structures.

The initial LLM draft is NOT ground truth. Its proposed scene anchors must
nevertheless be image-reviewed before the next editor may safely discard an
experience. This module:
* compares draft/final by fact identity, never by reused Chapter IDs alone;
* admits only source facts explicitly referenced in a provisional chapter;
* keeps a bounded number of anchor assets available to visual review;
* reserves media-choice candidates for visually verified draft anchors.

An anchor is a review obligation, not a fact verdict or forced published Chapter.
"""
from collections import defaultdict


LOST_ANCHOR_REVIEW_PROMPT = (
    '\nS07中有核心事实在S08复核后未进入任何Chapter或Moment，'
    '这些真实图片已重新核验。请按已核验事实判断它们是否构成独立经历、'
    '应合入现有章节、只作为Moment保留，或因证据不足舍弃。'
    '\n相同活动类别既不意味着必然属于同一段经历，也不意味着应拆成多个章节。'
    '需要比较实际可见的事件、主体、场景关联与可信时间依据；'
    '单纯地点、路面或视角变化不能自动升格成章。'
    '\nS07主题只是待验证的候选，不是事实真值；'
    '取消独立章节时要在已有结构和未选择事实中留下明确证据去向，'
    '并避免把旧章节ID无记录地赋予不同经历。'
)


def _chapters(packet):
    rows = packet.get('chapters', []) if isinstance(packet, dict) else []
    return rows if isinstance(rows, list) else []


def draft_anchor_proposals(packet, facts, *, max_anchor_assets_per_chapter=3):
    """Return bounded, fact-referenced candidates from each S07 Chapter.

    The model's theme and focus are contextual hints only; no model-provided
    name, emotion or continuity is promoted into visual evidence here.
    """
    if type(max_anchor_assets_per_chapter) is not int or max_anchor_assets_per_chapter < 1:
        raise ValueError('Expected a positive integer anchor-asset budget')
    proposals = []
    for row in _chapters(packet):
        if not isinstance(row, dict) or not isinstance(row.get('id'), str):
            continue
        stated = row.get('fact_ids', [])
        if not isinstance(stated, list):
            stated = []
        allowed = {fid for fid in stated if isinstance(fid, str) and fid in facts}
        focus = row.get('focus_fact_ids', [])
        if not isinstance(focus, list):
            focus = []
        # S07 focus may be invalid; keep only facts really attached to its
        # own Chapter. If none survive, record an explicit unknown anchor.
        focus = list(dict.fromkeys(fid for fid in focus if fid in allowed))
        seen_assets, anchor_facts = set(), []
        for fid in focus:
            aid = facts[fid]['asset_id']
            if aid in seen_assets:
                continue
            seen_assets.add(aid)
            anchor_facts.append(fid)
            if len(seen_assets) >= max_anchor_assets_per_chapter:
                break
        proposals.append({
            'draft_chapter_id': row['id'], 'draft_theme': row.get('theme', ''),
            'experience_kind': row.get('experience_kind'),
            'draft_fact_ids': list(dict.fromkeys(fid for fid in stated if fid in allowed)),
            'focus_fact_ids': focus,
            'anchor_fact_ids': anchor_facts,
            'anchor_asset_ids': [facts[fid]['asset_id'] for fid in anchor_facts],
            'status': 'ANCHORS_AVAILABLE' if anchor_facts else 'NO_VALID_DRAFT_ANCHOR'
        })
    return proposals


def transition_audit(draft, reviewed, facts, *, verified_facts=None):
    """Explain where S07 draft Chapters went after S08/S09B.

    A reused Chapter ID without fact overlap is explicitly a collision.
    The comparison is an audit, not evidence that the provisional draft must
    be preserved as an independent Chapter.
    """
    proposals = draft_anchor_proposals(draft, facts)
    finals = {
        row['id']: row for row in _chapters(reviewed)
        if isinstance(row, dict) and isinstance(row.get('id'), str)
    }
    # An experience may legitimately be down-scoped to a Moment, rather
    # than a full Chapter. A fact referenced by a provisional Moment is
    # accounted for but still awaits the normal downstream evidence gates.
    moments = reviewed.get('moments', []) if isinstance(reviewed, dict) else []
    moment_facts = {
        m['fact_id'] for m in moments if isinstance(m, dict)
        and isinstance(m.get('fact_id'), str)
    } if isinstance(moments, list) else set()
    verified = set(verified_facts) if verified_facts is not None else None
    retained_chapter_facts = {
        fid for row in finals.values() for fid in row.get('fact_ids', [])
        if isinstance(fid, str)
    }
    mapped = defaultdict(list)
    records = []
    for source in proposals:
        draft_ids = set(source['draft_fact_ids'])
        overlaps = {
            cid: len(draft_ids.intersection(
                fid for fid in row.get('fact_ids', []) if isinstance(fid, str)))
            for cid, row in finals.items()
        }
        best = max(overlaps, key=overlaps.get) if overlaps and max(overlaps.values()) else None
        draft_id = source['draft_chapter_id']
        reused = draft_id in finals and overlaps[draft_id] == 0
        if best:
            mapped[best].append(draft_id)
        anchors = source['anchor_fact_ids']
        surviving_anchors = ([] if verified is None
                             else [fid for fid in anchors if fid in verified])
        if verified is None:
            visual_status = 'NOT_YET_REVIEWED'
        elif surviving_anchors:
            visual_status = 'VERIFIED'
        else:
            visual_status = 'NO_VERIFIED_ANCHOR'
        records.append({
            **source,
            'best_reviewed_chapter_id': best,
            'retained_fact_overlap': overlaps.get(best, 0),
            'same_id_reused_for_different_facts': reused,
            'fact_overlap_by_final_chapter': overlaps,
            'represented_as_moment_fact_ids': [
                fid for fid in source['draft_fact_ids'] if fid in moment_facts
            ],
            'unaccounted_fact_ids': [
                fid for fid in source['draft_fact_ids']
                if fid not in retained_chapter_facts and fid not in moment_facts
            ],
            'visual_review_status': visual_status,
            'verified_anchor_fact_ids': surviving_anchors,
        })
    for record in records:
        target = record['best_reviewed_chapter_id']
        record['transition'] = (
            'REPRESENTED_AS_MOMENT' if target is None
                and not record['unaccounted_fact_ids']
                and record['represented_as_moment_fact_ids'] else
            'PARTIALLY_REPRESENTED_AS_MOMENT' if target is None
                and record['represented_as_moment_fact_ids'] else
            'OMITTED' if target is None else
            'MERGED_WITH_ANOTHER_DRAFT' if len(mapped[target]) > 1 else
            'RETAINED' if target == record['draft_chapter_id'] else
            'RENUMBERED_OR_REGROUPED'
        )
        record['needs_explicit_editorial_disposition'] = (
            record['transition'] != 'RETAINED'
            or record['same_id_reused_for_different_facts']
        )
    return {
        'policy': 'S07_DRAFT_ANCHOR_REVIEW_BEFORE_DISCARD',
        'draft_chapter_count': len(proposals),
        'final_chapter_count': len(finals),
        'records': records,
        'has_reused_id_collision': any(x['same_id_reused_for_different_facts'] for x in records),
        'omitted_draft_chapters': [x['draft_chapter_id'] for x in records if x['transition'] == 'OMITTED'],
        'editorial_dispositions_required': [x['draft_chapter_id'] for x in records
            if x['needs_explicit_editorial_disposition']],
        'notice': 'S07 is provisional; a recorded omission is not automatic proof of a missing Chapter.'
    }


def unrepresented_anchor_proposals(proposals, reviewed, facts):
    """Return ONLY draft anchors omitted from the reviewed Chapter fact sets.

    A legitimate merge keeping all source facts must not perturb the original
    media candidate order or introduce extra visual-model requests.
    """
    accounted = {
        fid for chapter in _chapters(reviewed) if isinstance(chapter, dict)
        for fid in chapter.get('fact_ids', []) if isinstance(fid, str)
    }
    # A draft scenelet can be intentionally represented by a smaller Moment.
    # It does not require an entire Chapter to survive. The downstream moment
    # evidence and publication gates still decide if this representation holds.
    moments = reviewed.get('moments', []) if isinstance(reviewed, dict) else []
    if isinstance(moments, list):
        accounted.update(
            m['fact_id'] for m in moments if isinstance(m, dict)
            and isinstance(m.get('fact_id'), str)
        )
    lost = []
    for item in proposals:
        omitted = [fid for fid in item['anchor_fact_ids'] if fid not in accounted]
        if omitted:
            lost.append({
                **item,
                'anchor_fact_ids': omitted,
                'anchor_asset_ids': [facts[fid]['asset_id'] for fid in omitted],
                'lost_anchor_fact_ids': omitted,
            })
    return lost


def anchor_asset_ids(proposals):
    """Assets requiring early visual review, de-duplicated in draft order."""
    return list(dict.fromkeys(
        aid for record in proposals for aid in record['anchor_asset_ids']
    ))


def media_reservations(proposals, verified_facts, *, prefix='DRAFT_ANCHOR_'):
    """Reserve at least one verified-image candidate for each S07 scene anchor.

    Never pass failed/absent facts into the media schema; groups are candidate
    retrieval obligations, not published Chapter IDs.
    """
    verified = set(verified_facts)
    groups = {}
    for item in proposals:
        anchor_facts = [fid for fid in item['anchor_fact_ids'] if fid in verified]
        if anchor_facts:
            groups[prefix + item['draft_chapter_id']] = anchor_facts
    return groups
