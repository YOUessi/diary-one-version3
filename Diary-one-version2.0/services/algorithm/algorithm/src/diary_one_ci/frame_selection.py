"""Within-image judgments for the existing image-bearing editorial call.

Facts supported by several frames are clues, not proof that each frame shows
every subject in the fact. The model must assess the actual displayed image.
This module validates references and relative decisions, not visual truth. It
never calls a model, changes facts, silently replaces a picture or creates Aha.
"""
from copy import deepcopy


REVISION = 'FRAME_SUBJECT_COMPARISON_V04_DEDICATED_OBSERVATION'
THEME_FIT = ('MAIN_SUBJECT', 'SUPPORTING_CONTEXT', 'BACKGROUND_ONLY', 'UNSUPPORTED')
VISIBILITY = ('CLEAR', 'PARTIAL', 'NOT_VISIBLE')
PROMINENCE = ('DOMINANT', 'READABLE', 'TINY_OR_UNCLEAR')
OCCLUSION = ('NONE', 'PARTIAL', 'DOMINANT')
FIELDS = ('candidate_id', 'fact_ids', 'scene_observation_id', 'visible_detail', 'theme_fit',
          'visibility', 'prominence', 'occlusion')

FRAME_SELECTION_PROMPT = '''
本轮frame_assessments是逐张看图的选择依据，不是重新识别整段视频。对每个已随附P候选恰好返回一次。
多帧共同支持一条fact，不表示那条fact的全部主体/动作在每张图里都看得见。必须看当前P图片，不把同素材其他帧的内容搬过来。
每项只返回candidate_id/fact_ids/scene_observation_id/visible_detail/theme_fit/visibility/prominence/occlusion。
candidate_scene_clues是先前独立看图观察已通过本帧引用校验的可用线索，不是整段事实，也不是客观视觉真值。它可能遗漏细节；本轮不能用整段fact填补未观察到的主体。
若线索provenance为DEDICATED_PER_FRAME_OBSERVATION，它来自专门逐P图审：fact_ids只能选supported_fact_ids，且subject_role/visibility/prominence/occlusion是该图审的具体判断。不能把ACTIVITY_CONTEXT器材语境重新涂成MAIN_SUBJECT，也不能把模糊/遮挡主体重新写成清晰无遮挡。
对可辨认的主体，从当前P的candidate_scene_clues中选一条与真实图片及本章重点相符的观察，返回其scene_observation_id；visible_detail逐字复制该条完整text，不增删、不拼接其他观察，不从其他P借用文本。
fact_ids只列与所选观察及当前图片具体细节相符的允许事实；只有多帧fact引用而没有本帧scene线索，不能声称该主体在此帧出现。
theme_fit相对你最终确定的所属章节selection_focus：MAIN_SUBJECT是直接呈现本章重点；SUPPORTING_CONTEXT帮助理解活动；BACKGROUND_ONLY只是背景；无可辨认事实用UNSUPPORTED。
MAIN_SUBJECT须直接关联本章focus_fact_ids，不能凭场景名、文件名或器材类型补出主体。
visibility是重点主体能否辨认（CLEAR/PARTIAL/NOT_VISIBLE）；prominence是它在本图中的显著程度（DOMINANT/READABLE/TINY_OR_UNCLEAR）；occlusion是它被前景遮挡的程度（NONE/PARTIAL/DOMINANT）。只评价这一主体，不用整张图的清晰度冒充主体清晰度。
没有有效scene线索、或线索不支持允许事实的可辨认主体时，scene_observation_id=null、visible_detail=''、fact_ids=[]、theme_fit=UNSUPPORTED、visibility=NOT_VISIBLE、prominence=TINY_OR_UNCLEAR；不要为了覆盖素材假称可见或编造观察。该帧不能入选本章组图或封面，可改选证据齐全的候选。
按same_asset_candidate_groups比较同素材候选。同一fact可能包含不同细节；只有fact_supports中visible_quote指向相同可见内容时才作为同主体替代帧比较，不能只凭fact编号相同把互补细节排掉。选择能直接呈现章重点且主体可辨的帧；同一主体在另一帧更清楚、更显著或遮挡更少时，不因编号靠前而选较弱帧。
封面比较与focus有直接事实关联的候选；具体场景主体优先于泛泛环境或构图美观。动物观察看动物、展览看展品、制作或用餐看食物/实际操作；不要求主体必须动态、罕见或有互动。
活动器材、手臂、车把只能帮助说明活动，不能因为占画面大就自动成为主题主体。按当前场景实际重点比较沿途主体与环境，不把所有骑行图都优先选成车把特写。
主体在所有候选中都不可辨时可选有事实依据的环境语境，并如实写SUPPORTING_CONTEXT，不把背景改称主体；主线确实是环境/建筑观察时，以对应focus事实为依据。
组图服务于互补细节，不强制每张都达到封面主题主体等级；同素材不同细节无需被一套审美排序抹掉。高光价值仍独立判断，不从本轮分级自动产生高光。
visible_detail、focus及media_choices.reason只谈该图可核对的主体/状态、主题贡献和遮挡差异；不得补出未知同伴/亲子/身份关系、连续路线、起终点、情绪、目的或时间先后。主题与理由不是新的事实。
这些分类是基于图片的模型判断，不是客观检测分数或人工验收。不要输出数值美学分、分析过程或新增字段。
'''


def _ids(values, allowed, *, empty=False):
    if (not isinstance(values, list) or (not empty and not values)
            or any(not isinstance(v, str) for v in values)
            or len(set(values)) != len(values) or not set(values) <= set(allowed)):
        raise ValueError('expected unique allowed fact/candidate IDs')
    return values


def _candidates(candidates, facts):
    by_id, frames = {}, set()
    for candidate in candidates:
        pid, aid, frame = (candidate.get(k) for k in ('candidate_id', 'asset_id', 'frame_id'))
        if not all(isinstance(v, str) and v.strip() for v in (pid, aid, frame)):
            raise ValueError('Invalid trusted candidate identity')
        if pid in by_id or (aid, frame) in frames:
            raise ValueError('Duplicate trusted candidate image')
        refs = _ids(candidate.get('fact_ids'), facts)
        if any(facts[f]['asset_id'] != aid or frame not in facts[f].get('evidence_frame_ids', []) for f in refs):
            raise ValueError('Trusted candidate is not bound to its fact source and frame')
        by_id[pid] = candidate
        frames.add((aid, frame))
    return by_id


def scene_clues_from_visual_outputs(visual_outputs, candidates, facts):
    """Index only observations already checked against S09A's shown images.

    The visual reviewer records ``accepted_scenes`` from collect_scenes. Never
    reconstruct acceptance from a raw model output: its frame references may
    have failed validation. Observations remain model evidence, not truth.
    """
    by_id = _candidates(candidates, facts)
    scenes, issues = [], []
    for packet in visual_outputs if isinstance(visual_outputs, list) else []:
        if not isinstance(packet, dict) or packet.get('stage') != 'INDEPENDENT_SCENE':
            continue
        accepted = packet.get('accepted_scenes')
        if not isinstance(accepted, list):
            issues.append('Independent scene output lacks validated accepted_scenes')
            continue
        scenes.extend(accepted)
    groups = {}
    for scene in scenes:
        if isinstance(scene, dict) and isinstance(scene.get('asset_id'), str):
            groups.setdefault(scene['asset_id'], []).append(scene)
    result = {pid: [] for pid in by_id}
    serial = 0
    for aid, matches in groups.items():
        if len(matches) != 1:
            issues.append('Duplicate accepted independent scene for ' + aid)
            continue
        observations = matches[0].get('observations')
        for obs in observations if isinstance(observations, list) else []:
            refs = obs.get('evidence_frame_ids') if isinstance(obs, dict) else None
            if (not isinstance(obs, dict) or not isinstance(obs.get('text'), str) or not obs['text'].strip()
                    or not isinstance(refs, list) or not refs or any(not isinstance(f, str) for f in refs)
                    or len(set(refs)) != len(refs) or obs.get('temporal_support') not in ('STATE', 'CHANGE')):
                issues.append('Malformed accepted observation for ' + aid)
                continue
            serial += 1
            row = {'scene_observation_id': 'SC%03d' % serial, 'text': obs['text'],
                   'asset_id': aid, 'evidence_frame_ids': list(refs)}
            for pid, candidate in by_id.items():
                if candidate['asset_id'] == aid and candidate['frame_id'] in refs:
                    result[pid].append(deepcopy(row))
    return {'candidate_scene_clues': result, 'issues': issues,
            'evidence_scope': 'VALIDATED_INDEPENDENT_SCENE_REFERENCES_NOT_VISUAL_GROUND_TRUTH'}


def _scene_choices(scene_clues, by_id):
    """Bind trusted scene clues to this exact displayed candidate table again."""
    source = scene_clues.get('candidate_scene_clues', {}) if isinstance(scene_clues, dict) else {}
    source = source if isinstance(source, dict) else {}
    result = {}
    for pid, candidate in by_id.items():
        rows = source.get(pid, [])
        choices = {}
        for row in rows if isinstance(rows, list) else []:
            if (not isinstance(row, dict) or not isinstance(row.get('scene_observation_id'), str)
                    or not row['scene_observation_id'] or not isinstance(row.get('text'), str) or not row['text'].strip()
                    or row.get('asset_id') != candidate['asset_id']
                    or not isinstance(row.get('evidence_frame_ids'), list)
                    or candidate['frame_id'] not in row['evidence_frame_ids']):
                continue
            sid = row['scene_observation_id']
            if row.get('provenance') == 'DEDICATED_PER_FRAME_OBSERVATION':
                try:
                    _ids(row.get('supported_fact_ids'), candidate['fact_ids'])
                    if (row.get('subject_role') not in ('SPECIFIC_SUBJECT', 'ACTIVITY_CONTEXT', 'BACKGROUND')
                            or row.get('visibility') not in VISIBILITY or row.get('prominence') not in PROMINENCE
                            or row.get('occlusion') not in OCCLUSION):
                        continue
                except ValueError:
                    continue
            if sid in choices:
                choices[sid] = None  # Duplicate identity cannot become a selectable quote.
            else:
                choices[sid] = row
        result[pid] = {sid: row for sid, row in choices.items() if row is not None}
    return result


def frame_selection_context(candidates, facts, *, scene_clues=None):
    """Add to the SAME request that sends these actual candidate images."""
    by_id = _candidates(candidates, facts)
    groups = {}
    for pid, candidate in by_id.items():
        groups.setdefault(candidate['asset_id'], []).append(pid)
    return {'revision': REVISION,
            'fact_scope': 'MULTI_FRAME_FACT_IS_A_CLUE_NOT_PER_IMAGE_VISIBILITY_PROOF',
            'comparison_scope': 'SAME_ASSET_SAME_VISIBLE_FACT_FRAGMENT_FOR_GALLERY; FOCUS_SUPPORTED_SUBJECT_OVER_CONTEXT_FOR_HERO',
            'same_asset_candidate_groups': [{'asset_id': aid, 'candidate_ids': pids} for aid, pids in groups.items()],
            'candidate_fact_allowlist': {pid: list(c['fact_ids']) for pid, c in by_id.items()},
            'candidate_scene_clues': {pid: list(rows.values()) for pid, rows in _scene_choices(scene_clues, by_id).items()},
            'scene_scope': 'MISSING_SCENE_IS_UNAVAILABLE_EVIDENCE_NOT_PERMISSION_TO_REUSE_A_CLIP_FACT',
            'assessment_scope': 'EXACTLY_THE_IMAGES_ATTACHED_TO_THIS_CALL; MODEL_JUDGMENT_NOT_GROUND_TRUTH'}


def augment_frame_selection_schema(schema, candidates, facts, *, scene_clues=None):
    """Extend only the internal provider response; public schema is unchanged."""
    by_id = _candidates(candidates, facts)
    scene_choices = _scene_choices(scene_clues, by_id)
    variants = []
    for pid, candidate in by_id.items():
        variants.append({'type': 'object', 'additionalProperties': False, 'required': list(FIELDS),
            'properties': {'candidate_id': {'const': pid},
                'fact_ids': {'type': 'array', 'items': {'enum': candidate['fact_ids']}, 'uniqueItems': True},
                'scene_observation_id': {'enum': [None, *scene_choices[pid]]},
                'visible_detail': {'type': 'string'},
                'theme_fit': {'enum': list(THEME_FIT)}, 'visibility': {'enum': list(VISIBILITY)},
                'prominence': {'enum': list(PROMINENCE)}, 'occlusion': {'enum': list(OCCLUSION)}},
            'allOf': [{'oneOf': [
                {'properties': {'scene_observation_id': {'const': sid}, 'visible_detail': {'const': row['text']},
                    'fact_ids': {'minItems': 1, 'items': {'enum': row.get('supported_fact_ids', candidate['fact_ids'])}}}}
                for sid, row in scene_choices[pid].items()] + [
                {'properties': {'scene_observation_id': {'const': None}, 'visible_detail': {'const': ''},
                    'fact_ids': {'maxItems': 0}, 'theme_fit': {'const': 'UNSUPPORTED'},
                    'visibility': {'const': 'NOT_VISIBLE'}, 'prominence': {'const': 'TINY_OR_UNCLEAR'}}}]}]})
    result = deepcopy(schema)
    result['properties']['frame_assessments'] = {'type': 'array', 'minItems': len(by_id),
        'maxItems': len(by_id), 'items': {'oneOf': variants} if variants else False}
    if 'frame_assessments' not in result['required']:
        result['required'].append('frame_assessments')
    return result


def _quality(judgment):
    """Qualitative model labels; no image-derived or calibrated score implied."""
    fit = {'UNSUPPORTED': 0, 'BACKGROUND_ONLY': 1, 'SUPPORTING_CONTEXT': 2, 'MAIN_SUBJECT': 3}[judgment['theme_fit']]
    visibility = {'NOT_VISIBLE': 0, 'PARTIAL': 1, 'CLEAR': 2}[judgment['visibility']]
    prominence = {'TINY_OR_UNCLEAR': 0, 'READABLE': 1, 'DOMINANT': 2}[judgment['prominence']]
    obstruction = {'DOMINANT': 0, 'PARTIAL': 1, 'NONE': 2}[judgment['occlusion']]
    # A plainly visible thematic subject beats a prettier contextual image.
    # Conversely, a nominal subject that cannot be made out gets no such boost.
    readable = visibility >= 1 and prominence >= 1 and obstruction >= 1
    tier = 2 if fit == 3 and readable else (1 if readable else 0)
    return tier, fit, visibility, prominence, obstruction


def _same_visible_claim(left, right, scene_choices):
    """Compare a shared visible fragment, never merely a whole clip fact ID.

    Containment is deliberately conservative: different fragments may describe
    complementary subjects. This is a textual comparison scope, not an image
    similarity test or a proof that the model's observation is correct.
    """
    common = set(left['fact_ids']) & set(right['fact_ids'])
    if not common:
        return False
    a = scene_choices[left['candidate_id']].get(left['scene_observation_id'], {})
    b = scene_choices[right['candidate_id']].get(right['scene_observation_id'], {})
    if all(c.get('provenance') == 'DEDICATED_PER_FRAME_OBSERVATION' for c in (a, b)):
        def fragments(clue):
            return {r['fact_id']: r['visible_quote'] for r in clue.get('fact_supports', [])
                    if isinstance(r, dict) and r.get('fact_id') in common
                    and r.get('support') in ('VISIBLE', 'PARTIAL')
                    and isinstance(r.get('visible_quote'), str)
                    and sum(ch.isalnum() for ch in r['visible_quote']) >= 2}
        aa, bb = fragments(a), fragments(b)
        return any(aa[f] in bb[f] or bb[f] in aa[f] for f in aa.keys() & bb.keys())
    # Legacy accepted SCENE has no per-fact fragment ledger. Only the exact
    # same observation is an adequate textual basis for comparing its frames.
    return bool(a.get('text')) and a.get('text') == b.get('text')


def resolve_frame_selection(output, candidates, facts, *, scene_clues=None):
    """Return (selection_output, audit, issues) without mutating the model output.

    selection_output removes only frame_assessments for the existing strict
    structure compiler. Callers MUST feed hard issues to the bounded repair and
    reject unresolved affected chapters. Preference warnings can invite the
    same repair, but must not invalidate otherwise supported content.
    The candidate table must contain only images actually sent to this call.
    """
    by_id = _candidates(candidates, facts)
    scene_choices = _scene_choices(scene_clues, by_id)
    clean = deepcopy(output)
    raw = clean.pop('frame_assessments', None) if isinstance(clean, dict) else None
    audit = {'revision': REVISION, 'status': 'UNVERIFIED',
             'judgment_source': 'MODEL_LOOKING_AT_ATTACHED_IMAGES_NOT_OBJECTIVE_TRUTH',
             'raw_assessments': deepcopy(raw), 'assessments': [], 'comparisons': [],
             'classification_normalizations': [], 'preference_warnings': [],
             'automatic_replacements': [], 'ranking_basis': ['readable_thematic_subject', 'theme_fit',
                 'subject_visibility', 'subject_prominence', 'subject_occlusion']}
    audit['scene_clues'] = deepcopy(scene_clues)
    audit['candidates_without_scene_clues'] = [pid for pid, rows in scene_choices.items() if not rows]
    issues, assessed, invalid = [], {}, set()
    def issue(item, reason):
        identity = item if isinstance(item, str) and item else 'frame_assessments:malformed_item'
        issues.append({'item': identity, 'reason': 'frame_assessments: ' + reason})
    chapters = clean.get('chapters') if isinstance(clean, dict) else None
    def candidate_issue(pid, reason):
        """A broken frame judgment must not erase another chapter or Aha."""
        affected = []
        choices = clean.get('media_choices', []) if isinstance(clean, dict) else []
        choices = choices if isinstance(choices, list) else []
        if pid in by_id and isinstance(chapters, list):
            for chapter in chapters:
                selected_here = (chapter.get('hero_candidate_id') == pid or any(
                    isinstance(choice, dict) and choice.get('chapter_id') == chapter.get('id')
                    and choice.get('candidate_id') == pid for choice in choices)) if isinstance(chapter, dict) else False
                if (isinstance(chapter, dict) and isinstance(chapter.get('id'), str) and selected_here):
                    affected.append(chapter['id'])
        for item in affected or ['frame_assessments:' + pid]:
            issue(item, reason)
    if not isinstance(raw, list):
        issue('frame_assessments', 'return exactly one image assessment for every shown P candidate')
        return clean, audit, issues
    for index, value in enumerate(raw):
        pid = value.get('candidate_id') if isinstance(value, dict) else None
        try:
            if not isinstance(value, dict) or set(value) != set(FIELDS):
                raise ValueError('expected exactly ' + '/'.join(FIELDS))
            if not isinstance(pid, str) or pid not in by_id or pid in assessed:
                raise ValueError('unknown or duplicate shown candidate')
            refs = _ids(value['fact_ids'], by_id[pid]['fact_ids'], empty=True)
            if (value['theme_fit'] not in THEME_FIT or value['visibility'] not in VISIBILITY
                    or value['prominence'] not in PROMINENCE or value['occlusion'] not in OCCLUSION):
                raise ValueError('invalid visibility/theme/prominence/occlusion category')
            unavailable = value['visibility'] == 'NOT_VISIBLE' or value['theme_fit'] == 'UNSUPPORTED'
            if unavailable and (refs or value['visibility'] != 'NOT_VISIBLE'
                    or value['theme_fit'] != 'UNSUPPORTED' or value['prominence'] != 'TINY_OR_UNCLEAR'):
                raise ValueError('not-visible subject must be UNSUPPORTED with no visible fact references')
            if not unavailable and not refs:
                raise ValueError('visible subject needs an allowed fact reference')
            if unavailable:
                if value['scene_observation_id'] is not None or value['visible_detail'] != '':
                    raise ValueError('unavailable subject must not publish a scene quote')
            else:
                sid = value['scene_observation_id']
                if not isinstance(sid, str) or sid not in scene_choices[pid]:
                    raise ValueError('missing validated scene observation bound to this exact image')
                if value['visible_detail'] != scene_choices[pid][sid]['text']:
                    raise ValueError('visible_detail must exactly quote the referenced per-frame scene observation')
                clue = scene_choices[pid][sid]
                if clue.get('provenance') == 'DEDICATED_PER_FRAME_OBSERVATION':
                    _ids(refs, clue['supported_fact_ids'])
            assessed[pid] = deepcopy(value)
        except (KeyError, TypeError, ValueError) as exc:
            reason = 'row %d: %s' % (index, exc)
            if isinstance(pid, str) and pid in by_id:
                invalid.add(pid)
                candidate_issue(pid, reason)
            else:
                issue('frame_assessments:unknown_row_%d' % index, reason)
    missing = [pid for pid in by_id if pid not in assessed]
    for pid in missing:
        invalid.add(pid)
        candidate_issue(pid, 'missing valid assessment for ' + pid)
    audit['assessments'] = list(assessed.values())
    if not isinstance(clean, dict):
        return clean, audit, issues
    choices = clean.get('media_choices')
    if not isinstance(chapters, list) or not isinstance(choices, list):
        issue('frame_assessments', 'selection requires chapters and media_choices arrays')
        return clean, audit, issues
    for chapter in chapters:
        cid = chapter.get('id') if isinstance(chapter, dict) else None
        try:
            if not isinstance(cid, str) or not cid:
                raise ValueError('missing chapter identity')
            chapter_facts = set(_ids(chapter.get('fact_ids'), facts))
            selected_ids = {r.get('candidate_id') for r in choices if isinstance(r, dict)
                            and r.get('chapter_id') == cid and isinstance(r.get('candidate_id'), str)}
            if any(pid in selected_ids or pid == chapter.get('hero_candidate_id') for pid in invalid):
                continue  # Already recorded a scoped issue; assess other chapters.
            focus = chapter.get('selection_focus')
            focus_refs = focus.get('fact_ids') if isinstance(focus, dict) else chapter.get('focus_fact_ids')
            try:
                focus_facts = set(_ids(focus_refs, chapter_facts))
            except ValueError as exc:
                raise ValueError('chapters.%s.focus_fact_ids: must be a nonempty unique subset of this chapter fact_ids' % cid) from exc
            relevant = {pid: deepcopy(a) for pid, a in assessed.items()
                        if pid not in invalid and set(a['fact_ids']) & chapter_facts}
            for pid, a in relevant.items():
                clue = scene_choices[pid].get(a['scene_observation_id'], {})
                if clue.get('provenance') == 'DEDICATED_PER_FRAME_OBSERVATION':
                    effective = {k: clue[k] for k in ('visibility', 'prominence', 'occlusion')}
                    cap = {'ACTIVITY_CONTEXT': 'SUPPORTING_CONTEXT', 'BACKGROUND': 'BACKGROUND_ONLY'}.get(clue['subject_role'])
                    if cap and THEME_FIT.index(a['theme_fit']) < THEME_FIT.index(cap):
                        effective['theme_fit'] = cap
                    changes = {k: {'raw': a[k], 'effective': value} for k, value in effective.items() if a[k] != value}
                    if changes:
                        audit['classification_normalizations'].append({'chapter_id': cid, 'candidate_id': pid,
                            'rule': 'DEDICATED_FRAME_OBSERVATION_CONTROLS_VISIBLE_SUBJECT_CLASSIFICATION',
                            'scene_observation_id': clue['scene_observation_id'], 'changes': changes})
                    a.update(effective)
                if a['theme_fit'] == 'MAIN_SUBJECT' and not set(a['fact_ids']) & focus_facts:
                    # Theme membership follows the verified reference scope,
                    # not a model tag. A mislabeled, possibly unselected image
                    # must not discard an otherwise valid chapter. No picture,
                    # quote, fact reference or visibility judgment is changed.
                    a['theme_fit'] = 'SUPPORTING_CONTEXT'
                    audit['classification_normalizations'].append({
                        'chapter_id': cid, 'candidate_id': pid,
                        'rule': 'CHAPTER_FACT_WITHOUT_FOCUS_REFERENCE_IS_CONTEXT',
                        'raw_theme_fit': 'MAIN_SUBJECT', 'effective_theme_fit': 'SUPPORTING_CONTEXT',
                        'fact_ids': list(a['fact_ids']), 'focus_fact_ids': list(focus_refs)})
            selected = [r for r in choices if isinstance(r, dict) and r.get('chapter_id') == cid]
            pids = _ids([r.get('candidate_id') for r in selected], by_id)
            hero = chapter.get('hero_candidate_id')
            if hero not in pids:
                raise ValueError('explicit hero candidate must also be a media choice')
            for pid in pids:
                if pid not in relevant:
                    raise ValueError('%s has no visible fact belonging to this chapter' % pid)
            representatives = {}
            for pid in pids:
                aid = by_id[pid]['asset_id']
                representatives.setdefault(aid, hero if aid == by_id[hero]['asset_id'] else pid)
            for aid, pid in representatives.items():
                selected_assessment = relevant[pid]
                # Different fragments of one fact can describe distinct scenes.
                peers = {other: a for other, a in relevant.items()
                         if by_id[other]['asset_id'] == aid
                         and _same_visible_claim(selected_assessment, a, scene_choices)}
                better = [other for other, a in peers.items() if _quality(a) > _quality(selected_assessment)]
                audit['comparisons'].append({'chapter_id': cid, 'role': 'HERO' if pid == hero else 'GALLERY',
                    'selected_candidate_id': pid, 'scope': 'SAME_ASSET_SAME_VISIBLE_FACT_FRAGMENT',
                    'compared_candidate_ids': list(peers), 'stronger_candidate_ids': better})
                if better:
                    audit['preference_warnings'].append({'item': cid, 'candidate_id': pid,
                        'stronger_candidate_ids': better, 'code': 'SAME_SUBJECT_MORE_READABLE_FRAME',
                        'reason': '%s has more readable same-subject alternatives %s; this preference does not invalidate its evidence' % (pid, ','.join(better))})
            # Do not score irrelevant assets or unrelated chapter facts against
            # a cover. Both the competitor's visible detail and the final focus
            # must share an actual verified fact reference.
            focused = {pid: a for pid, a in relevant.items() if set(a['fact_ids']) & focus_facts}
            better = [pid for pid, a in focused.items() if a['theme_fit'] == 'MAIN_SUBJECT'
                      and _quality(a)[0] == 2 and _quality(a) > _quality(relevant[hero])
                      and (relevant[hero]['theme_fit'] != 'MAIN_SUBJECT'
                           or _same_visible_claim(relevant[hero], a, scene_choices))]
            audit['comparisons'].append({'chapter_id': cid, 'role': 'HERO',
                'selected_candidate_id': hero, 'scope': 'DIRECT_FOCUS_FACT_SUPPORT',
                'compared_candidate_ids': list(focused), 'stronger_candidate_ids': better})
            if better:
                audit['preference_warnings'].append({'item': cid, 'candidate_id': hero,
                    'stronger_candidate_ids': better, 'code': 'FOCUS_SUBJECT_PREFERRED_FOR_COVER',
                    'reason': 'hero %s has stronger directly focus-supported alternatives %s; preserve an evidence-valid chapter if the preference remains unresolved' % (hero, ','.join(better))})
        except (KeyError, TypeError, ValueError) as exc:
            issue(cid or 'frame_assessments', str(exc))
    audit['status'] = ('REQUIRES_BOUNDED_REPAIR' if issues else
        'REFERENCE_VALIDATED_WITH_PREFERENCE_WARNINGS' if audit['preference_warnings'] else
        'REFERENCE_AND_RELATIVE_DECISION_VALIDATED')
    return clean, audit, issues
