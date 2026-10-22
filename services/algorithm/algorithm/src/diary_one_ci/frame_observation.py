"""One bounded image-bearing observation of every displayed P candidate.

This is model evidence with checked source references, not objective detection.
It does not create facts, publish copy, choose a cover or invoke a fallback from
another image when a particular frame lacks a valid observation.
"""
from collections import Counter
from copy import deepcopy

from .frame_selection import _candidates, VISIBILITY, PROMINENCE, OCCLUSION


REVISION = 'PER_FRAME_FACT_SUPPORT_V02_ISOLATED_FACT_CHECKS'
SUBJECT_ROLES = ('SPECIFIC_SUBJECT', 'ACTIVITY_CONTEXT', 'BACKGROUND', 'UNRESOLVED')
SUPPORT = ('VISIBLE', 'PARTIAL', 'NOT_VISIBLE', 'UNCERTAIN')
FRAME_FIELDS = {'candidate_id', 'observation', 'subject_role', 'visibility',
                'prominence', 'occlusion', 'fact_checks'}
CHECK_FIELDS = {'fact_id', 'support', 'visible_quote', 'not_visible_quote'}

PROMPT = '''你是逐帧观察员。本次每张真实图片都对应一个P编号，必须逐张查看，对每个P恰好返回一项；不是按素材概述视频，也不选择Chapter封面。
candidate_frames明确给出P→素材→frame以及仅该P允许核对的facts。图片标签与这个表对应。不要把同一视频其他图片中的主体或动作搬到当前图片。
observation只用一小句写当前这一张最具体、最可辨认的主体及状态。优先检查画面中的具体事件主体、动物、展品、食物、独特景物或实际操作；不要因为车把/手臂/器材占据大面积，就遗漏其后可见的具体主体。静态主体不需动作或稀有性才值得被观察。
对candidate_frames中每条允许fact恰好做一次fact_checks：support为VISIBLE（对应事实主张在本帧可辨）、PARTIAL（仅部分可见）、NOT_VISIBLE或UNCERTAIN。
visible_quote必须逐字摘取fact.text里在本帧可核对的一个连续片段；不得用“...”或“……”省略或拼接多个片段，不能改写原句。PARTIAL时只摘成立部分，不复制整条多事件事实。not_visible_quote可逐字摘取同一fact里不在本帧中的一个连续片段；没有合适的连续片段可留空，绝不拼接。两个片段不能重叠；没有可见支持就visible_quote=''。同时填写可见与不可见片段时support必须PARTIAL。不要为满足引用捏造画面内容。
同一fact若写先看到人物、随后转向塔楼，人物图只支持人物片段，塔楼图只支持塔楼片段；不能写成同一帧中人物以塔楼为背景。单帧不证明时间先后、行进方向或持续动作，无法判断就标PARTIAL/UNCERTAIN；实际可见的姿态、物体和状态仍可保留。
subject_role只判断本帧观察的角色：SPECIFIC_SUBJECT=具体可辨主体/细节；ACTIVITY_CONTEXT=器材、手臂、普通路面等只说明正在做何种活动；BACKGROUND=无重点的背景；UNRESOLVED=没有可核对支持。不要把骑行器材自动升级为具体发现，也不要把动物园/博物馆的环境美观优先于可见动物/展品。
visibility CLEAR/PARTIAL/NOT_VISIBLE，prominence DOMINANT/READABLE/TINY_OR_UNCLEAR，occlusion NONE/PARTIAL/DOMINANT：均针对observation描述的主体，不拿全图清楚冒充主体清楚。若没有任何可见fact片段，subject_role=UNRESOLVED、visibility=NOT_VISIBLE、prominence=TINY_OR_UNCLEAR。
只陈述图片能支持的内容；不得补出同伴、亲属、身份、感受、目的、连续路线或目的地。标准化黑色补边不是场景物体。observation不是新增事实，更不是用户文案。
返回images数组，每项仅candidate_id/observation/subject_role/visibility/prominence/occlusion/fact_checks；每个fact_check仅fact_id/support/visible_quote/not_visible_quote。'''


def observation_schema(candidates, facts):
    by_id = _candidates(candidates, facts)
    variants = []
    for pid, candidate in by_id.items():
        checks = [{'type': 'object', 'additionalProperties': False, 'required': sorted(CHECK_FIELDS),
            'properties': {'fact_id': {'const': fid}, 'support': {'enum': list(SUPPORT)},
                'visible_quote': {'type': 'string'}, 'not_visible_quote': {'type': 'string'}}}
            for fid in candidate['fact_ids']]
        variants.append({'type': 'object', 'additionalProperties': False, 'required': sorted(FRAME_FIELDS),
            'properties': {'candidate_id': {'const': pid}, 'observation': {'type': 'string', 'minLength': 1},
                'subject_role': {'enum': list(SUBJECT_ROLES)}, 'visibility': {'enum': list(VISIBILITY)},
                'prominence': {'enum': list(PROMINENCE)}, 'occlusion': {'enum': list(OCCLUSION)},
                'fact_checks': {'type': 'array', 'minItems': len(checks), 'maxItems': len(checks),
                    'items': {'oneOf': checks}}}})
    return {'type': 'object', 'additionalProperties': False, 'required': ['images'], 'properties': {
        'images': {'type': 'array', 'minItems': len(by_id), 'maxItems': len(by_id),
                   'items': {'oneOf': variants} if variants else False}}}


def _quote(value, text):
    if not isinstance(value, str) or (value and (value not in text or not any(c.isalnum() for c in value))):
        raise ValueError('Fact support quote is not a substantive exact original fragment')
    return value


def _compile_fact_check(check, facts):
    """Validate exact spans before any conservative classification change."""
    text = facts[check['fact_id']]['text']
    visible = _quote(check['visible_quote'], text)
    absent = _quote(check['not_visible_quote'], text)
    if check['support'] not in SUPPORT:
        raise ValueError('Invalid fact support category')
    if check['support'] in ('VISIBLE', 'PARTIAL'):
        if not visible:
            raise ValueError('Visible fact requires an exact original fragment')
    elif visible:
        raise ValueError('Unavailable fact cannot publish a visible fragment')
    if visible and absent:
        visible_starts = [i for i in range(len(text)) if text.startswith(visible, i)]
        absent_starts = [i for i in range(len(text)) if text.startswith(absent, i)]
        if any(v < a + len(absent) and a < v + len(visible)
               for v in visible_starts for a in absent_starts):
            raise ValueError('Visible and not-visible fact fragments overlap')
    effective = deepcopy(check)
    normalization = None
    if check['support'] == 'VISIBLE' and absent:
        # Both exact, disjoint spans already exist in the original fact. Only
        # weaken the classification; never fill, repair or extend either quote.
        effective['support'] = 'PARTIAL'
        normalization = {'rule': 'EXACT_VISIBLE_AND_ABSENT_SPANS_ARE_PARTIAL',
                         'raw_support': 'VISIBLE', 'effective_support': 'PARTIAL'}
    return effective, normalization


def compile_observations(output, candidates, facts):
    """Accept or reject each P independently; no textual/first-frame fallback."""
    by_id = _candidates(candidates, facts)
    audit = {'revision': REVISION, 'source': 'DEDICATED_PER_FRAME_OBSERVATION',
             'raw_output': deepcopy(output), 'frame_ledger': [], 'frame_claim_supports': [],
             'extra_rows': [], 'whole_response_invalid': False, 'fact_check_ledger': [],
             'validation_scope': 'MODEL_IMAGE_JUDGMENT_WITH_SOURCE_AND_QUOTE_BINDING_NOT_VISUAL_GROUND_TRUTH'}
    rows = output.get('images') if isinstance(output, dict) and set(output) == {'images'} else None
    if not isinstance(rows, list):
        rows = []
        audit['whole_response_invalid'] = True
    counts = Counter(row.get('candidate_id') for row in rows
                     if isinstance(row, dict) and isinstance(row.get('candidate_id'), str))
    clues = {pid: [] for pid in by_id}
    for i, row in enumerate(rows):
        if (not isinstance(row, dict) or not isinstance(row.get('candidate_id'), str)
                or row['candidate_id'] not in by_id):
            audit['extra_rows'].append({'index': i, 'reason': 'Unknown or malformed candidate identity'})
    for pid, candidate in by_id.items():
        try:
            if counts[pid] != 1:
                raise ValueError('Missing or duplicate dedicated observation for this P')
            row = next(r for r in rows if isinstance(r, dict) and r.get('candidate_id') == pid)
            if set(row) != FRAME_FIELDS:
                raise ValueError('Unexpected per-frame observation fields')
            if not isinstance(row['observation'], str) or not row['observation'].strip():
                raise ValueError('Missing concrete observation')
            if (row['subject_role'] not in SUBJECT_ROLES or row['visibility'] not in VISIBILITY
                    or row['prominence'] not in PROMINENCE or row['occlusion'] not in OCCLUSION):
                raise ValueError('Invalid subject/visibility classification')
            checks = row['fact_checks']
            if (not isinstance(checks, list) or len(checks) != len(candidate['fact_ids'])
                    or any(not isinstance(c, dict) or set(c) != CHECK_FIELDS for c in checks)):
                raise ValueError('Each allowed fact needs exactly one visibility check')
            ids = [c['fact_id'] for c in checks]
            if (any(not isinstance(fid, str) for fid in ids) or len(set(ids)) != len(ids)
                    or set(ids) != set(candidate['fact_ids'])):
                raise ValueError('Foreign, duplicate or missing frame fact check')
            supported, accepted_checks = [], []
            for check in checks:
                ledger = {'candidate_id': pid, 'fact_id': check['fact_id'], 'raw_check': deepcopy(check)}
                try:
                    effective, normalization = _compile_fact_check(check, facts)
                    accepted_checks.append(effective)
                    if effective['support'] in ('VISIBLE', 'PARTIAL'):
                        supported.append(check['fact_id'])
                    ledger.update(status='VERIFIED_REFERENCE_SCOPE', effective_check=deepcopy(effective))
                    if normalization:
                        ledger['classification_normalization'] = normalization
                except (KeyError, TypeError, ValueError) as exc:
                    ledger.update(status='UNVERIFIED', reason=str(exc))
                audit['fact_check_ledger'].append(ledger)
            unavailable = row['subject_role'] == 'UNRESOLVED' or row['visibility'] == 'NOT_VISIBLE'
            if unavailable and (supported or row['subject_role'] != 'UNRESOLVED'
                                or row['visibility'] != 'NOT_VISIBLE' or row['prominence'] != 'TINY_OR_UNCLEAR'):
                raise ValueError('Unresolved image must not claim visible fact support')
            if not unavailable and not supported:
                raise ValueError('Image subject lacks a directly supported fact fragment')
            record = {'candidate_id': pid, 'asset_id': candidate['asset_id'], 'frame_id': candidate['frame_id'],
                      'status': 'UNAVAILABLE' if unavailable else 'VERIFIED_REFERENCE_SCOPE',
                      'fact_checks': deepcopy(accepted_checks), 'raw_fact_checks': deepcopy(checks),
                      'unverified_fact_ids': [c['fact_id'] for c in checks
                          if c['fact_id'] not in {v['fact_id'] for v in accepted_checks}]}
            audit['frame_ledger'].append(record)
            if unavailable:
                continue
            clue = {'scene_observation_id': 'FO:' + pid, 'text': row['observation'],
                'asset_id': candidate['asset_id'], 'evidence_frame_ids': [candidate['frame_id']],
                'supported_fact_ids': supported, 'fact_supports': deepcopy(accepted_checks),
                'raw_fact_supports': deepcopy(checks),
                'provenance': 'DEDICATED_PER_FRAME_OBSERVATION',
                **{k: row[k] for k in ('subject_role', 'visibility', 'prominence', 'occlusion')}}
            clues[pid] = [clue]
            audit['frame_claim_supports'].append({'candidate_id': pid, **deepcopy(clue)})
        except (KeyError, TypeError, ValueError) as exc:
            audit['frame_ledger'].append({'candidate_id': pid, 'asset_id': candidate['asset_id'],
                'frame_id': candidate['frame_id'], 'status': 'UNVERIFIED', 'reason': str(exc)})
    if by_id and not any(r['status'] != 'UNVERIFIED' for r in audit['frame_ledger']):
        audit['whole_response_invalid'] = True
    return {'candidate_scene_clues': clues, 'issues': [r for r in audit['frame_ledger'] if r['status'] == 'UNVERIFIED'],
            'evidence_scope': 'DEDICATED_PER_IMAGE_MODEL_OBSERVATION_WITH_FACT_QUOTES_NOT_VISUAL_GROUND_TRUTH'}, audit


def review_frame_observations(candidates, facts, ask, *, evidence, stage='S09A_FRAME_OBSERVATION', stage_runs=None):
    """One normal call; at most one retry for a wholly invalid JSON contract.

    Partial invalid images stay unavailable. Transport/auth errors never trigger
    this format retry; there is no fallback to an old broad scene description.
    """
    from . import x02
    _candidates(candidates, facts)
    if len(evidence) != len(candidates):
        raise ValueError('Per-frame observation requires one actual image per P')
    for candidate, item in zip(candidates, evidence):
        asset, frame, _ = item
        if frame['frame_id'] != candidate['frame_id']:
            raise ValueError('Per-frame evidence order does not match candidate identity')
        source_ids = {facts[f].get('source_asset_id') for f in candidate['fact_ids']}
        if source_ids - {None} and asset['asset_id'] not in source_ids:
            raise ValueError('Per-frame image source does not match its verified facts')
    context = {'revision': REVISION, 'candidate_frames': [
        {'candidate_id': c['candidate_id'], 'asset_id': c['asset_id'], 'frame_id': c['frame_id'],
         'facts': [{'fact_id': fid, 'text': facts[fid]['text']} for fid in c['fact_ids']]}
        for c in candidates], 'image_order': [c['candidate_id'] for c in candidates]}
    attempts = []
    if not candidates:
        clues, audit = compile_observations({'images': []}, candidates, facts)
        return clues, {**audit, 'attempts': attempts}
    schema = observation_schema(candidates, facts)
    for attempt in range(2):
        current_stage = stage if attempt == 0 else stage + '_FORMAT_RETRY'
        retryable = False
        try:
            output = ask(current_stage, PROMPT, schema, context, evidence=evidence)
            clues, audit = compile_observations(output, candidates, facts)
            retryable = audit['whole_response_invalid']
        except (ValueError, OSError, x02.X02Error) as exc:
            if isinstance(exc, x02.X02StageCallError) and stage_runs is not None:
                if all(run is not exc.stage_run for run in stage_runs):
                    stage_runs.append(exc.stage_run)
            clues, audit = compile_observations(None, candidates, facts)
            audit['failure'] = {'type': type(exc).__name__, 'code': getattr(exc, 'code', 'UNKNOWN')}
            retryable = ((isinstance(exc, ValueError) and not isinstance(exc, x02.X02Error))
                         or getattr(exc, 'code', None) == 'MODEL_RESPONSE_NOT_JSON')
        attempts.append({'stage': current_stage, **deepcopy(audit)})
        if not retryable or attempt:
            return clues, {**audit, 'attempts': attempts}
        context = {**context, 'repair_instruction': 'Previous whole response was invalid. Return exactly every P and its allowed fact checks.',
                   'issues': audit['frame_ledger']}
