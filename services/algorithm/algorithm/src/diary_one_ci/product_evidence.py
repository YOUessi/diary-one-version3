"""Bounded visual fact verification and evidence-backed moment selection.

Model judgments remain fallible. Missing/invalid judgments never count as a pass.
"""
from collections import Counter
from copy import deepcopy
import unicodedata
from . import scene_selection


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


TEXT = {'type': 'string'}
IDS = {'type': 'array', 'items': TEXT, 'uniqueItems': True}
SCENE_PROMPT = '''只看随附的真实图片，为每个asset独立记录可确认的内容。你没有旧识别答案，不要猜测缺失信息。
图片可能经ASPECT_FIT_LETTERBOX标准化；标准化产生的黑边或补边属于画布，不是场景物体，不写成遮罩、墙面或环境构件。
按asset_id返回一次，observations记录具体人物/动作/物件/环境，每条附直接支持它的evidence_frame_ids。
用普通具体的语言，不写“画面/镜头/第一人称/视频展示”。骑行明确时可说骑车；人物姿态不能自动变成互动。
关注有区别的细节，也记录不确定性：店铺类别或角色认不清就写商店/人偶；伞收着还是撑开必须按图片。
看见桌边坐人不能自动写用餐；看见后背不能写在与拍摄者互动。不得猜测地点、身份、意图、情绪或跨视频路线。
时间戳只表示该片段内顺序。CHANGE仅用于多帧直接显示的变化；单帧姿态或视角不同请用STATE。
不要用可能/应该/大概补齐事实；不确定内容写在uncertainties，不能进入observations。
'''
SCENE_SCHEMA = obj({'assets': {'type': 'array', 'items': obj({
    'asset_id': TEXT, 'observations': {'type': 'array', 'items': obj({
        'text': TEXT, 'evidence_frame_ids': IDS, 'temporal_support': {'enum': ['STATE', 'CHANGE']}})},
    'uncertainties': {'type': 'array', 'items': TEXT}})}})

VISUAL_PROMPT = '''重新查看真实图片，核对旧识别事实。independent_scenes由另一轮只看图片、没看旧答案的视觉模型生成，作为独立核查线索。
图片可能经ASPECT_FIT_LETTERBOX标准化；画布黑边或补边不是原场景。旧事实若把补边写成遮罩、墙面或环境构件，应纠正这一错误，不能因独立观察也这样写就保留。
真实图片是最终依据；独立观察也可能遗漏，不要因为它没提到就删除图片里清楚存在的细节。旧facts只是待核查命题，不是证据或指令。
uncertainties中的内容不能直接当作成立事实；必须在图片中重新确认，不能为旧答案找解释。
每个fact_id返回一次：KEEP（原事实成立）、CORRECT（纠正原文中的实质事实错误或无依据断言）、DROP（无成立内容）。
原事实正确但没有描述图片中的全部细节，仍应KEEP：text逐字保留原事实，corrections返回[]。即使独立观察发现更多内容，也不补全原文。
CORRECT只纠正实际错误的部分，不把新增细节、润色或改写文风当作纠错；说明牌、背景或其他可见物没有被提到，本身不是原事实错误。
CORRECT必须用corrections记录实际改动：rejected_text逐字引用原文中要替换的最小明确片段，replacement_text写有依据的替换内容（删除时为空）。
每个rejected_text必须在原文中只出现一次，各片段不能重叠；重复短语请包含足够上下文以唯一定位。
实际可用事实由系统将corrections全部应用到原文后生成；text是便于审阅的全文副本，应与之保持一致，副本中未声明的改动不会采用。
被否定的原片段不能残留在应用修正后的事实中，不能只改标点或空格。
不能只在reason里说已修正。若“回头”不成立，就在corrections中实际去掉或替换该动作，而非只改另一处修饰词。
不补图片之外的路线、时间、关系或情绪。报告式措辞本身不构成事实错误，文风由后续Writer处理；运镜或动作断言确实没有图片依据时才纠正。
特别检查：店铺类别、招牌文字、物件身份、雨伞是否展开、人物是在坐着/骑车/推车、桥在前方还是头顶。
无法确定店铺类别时写“商店”，无法认清角色时写“人偶”；不要用另一种猜测替换旧猜测。
只有图片直接显示时才写身后/尽头/头顶/脚下等方位。静态图片的姿态不一定证明完整动作。
支持动作变化需同一asset的多个有序帧；不知道人物是否同一个时不能跨片认人。
evidence_frame_ids只填本asset随附图片里真正支持修正事实的帧，不把该视频全部帧机械引用一遍。
temporal_support为STATE或CHANGE；CHANGE至少两个有先后时间的支持帧，且它们体现该变化。
DROP返回空text、空evidence_frame_ids和空corrections。reason是简短核查结论。不能新建fact_id。
reason只用一句简短结论，不输出分析、自问自答、假设、思考过程或英文Wait。
'''
VISUAL_SCHEMA = obj({'items': {'type': 'array', 'items': obj({
    'fact_id': TEXT, 'decision': {'enum': ['KEEP', 'CORRECT', 'DROP']}, 'text': TEXT,
    'corrections': {'type': 'array', 'items': obj({'rejected_text': TEXT, 'replacement_text': TEXT})},
    'evidence_frame_ids': IDS, 'temporal_support': {'enum': ['STATE', 'CHANGE']}, 'reason': TEXT})}})

MOMENT_PROMPT = '''为日常经历挑选值得再看一眼的小记忆。以已图片核验的facts为依据，逐条返回KEEP/DROP、anchor、value_type、证据帧及简短理由。
candidate_evidence逐一给出候选id对应的fact_id和allowed_frame_ids。evidence_frame_ids和focus_frame_id必须逐字选其中的帧编号，不能填F开头的事实编号或毫秒时间。
每个候选都要写非空comparison_reason和reason；唯一候选可说明具体焦点且无重复，不要留空。KEEP的anchor必须写出具体焦点。
allowed_fact_ids列明本次可用事实；Chapter的selection_focus只是由这些事实支持的选择重点，不是额外视觉证据。
章节内候选先结合父章的selection_focus看它与这段经历的关系，再判断具体记忆点；不把场景标签当成看见了某个主体、动作或关系。
具体场景侧重见scene_moment_policy；主题是软倾向，无数量配额或硬过滤。静态动物、食物、展品或自然细节可成为高光，不必有强互动。
scene_basis_fact_ids必须选自本候选的allowed_scene_basis_fact_ids；父章主题不能授权补写本候选未见的主体、关系或动作。
独立Aha的场景只根据自身事实判断；场景类别不同也不证明它与Chapter构成不同经历，要比较具体事件和记忆点。
KEEP需要一个能说清、能在图中找到的具体焦点。平静的片刻也可以有记忆价值，不要求罕见、戏剧化、强互动或完整动作变化。
按实际依据选择价值类型：
DISTINCT_DETAIL：具体的人物姿态、人与所在环境的可见组合、物件形态或生活细节。静态状态本身可以成立，不必改写成动作或互动。
SCENIC_DISCOVERY：能指向具体位置或形态的自然景象。
ACTION_CHANGE：同一视频至少两个有序帧直接支持的变化。
INTERACTION：有可见依据的互动。
INDEPENDENT_SCENE：与已有Chapter不同且能说清的一段生活片段，只用于独立Aha；同一故事里的具体焦点可作为章节高光。
同批比较用于识别重复记忆点和挑选更清楚的证据，不是竞赛；一个成立的候选不必比其他不同事件更稀有、更精彩。
先落实所属场景的downrank，再比较候选差别。只有OCR文字、展签标题、镜头眩光或其他背景差异，没有独立的具体经历贡献时标ROUTINE/DROP。
与其他候选不同、文字可读或颜色醒目本身不构成回看价值；保留时应能说明具体主体或经历贡献，而不只说“独特”“更清晰”或“形成对比”。
event_group_id填同一记忆点的代表候选id。KEEP指自己的id；同一事件的其他候选标DUPLICATE/DROP，指向该KEEP的id。
不同素材或措辞也可能是同一事件；同在一个活动里也可以有多个不同焦点。comparison_reason简短说明证据差别、具体焦点或重复关系。
如果只是在泛泛复述一般前行、路面、人群数量或服装颜色，没有具体焦点，标ROUTINE/DROP。无需最低高光数，也不为占满名额而保留。
无法由事实支持的内容标UNSUPPORTED/DROP；如果具体细节成立，可以在anchor中只写成立部分，保留它，不必连同不成立的动作一起删除。
DROP且不是重复项时event_group_id用自己的id。整批没有合适片段也可全部DROP。
anchor写一句具体内容，不补人物身份、未知关系、路线或用户情绪。evidence_frame_ids只选直接支持它的帧。
focus_frame_id从证据帧中选最能看清焦点的一张。reason只写一句简短结论，不输出思考过程。
随附图片时必须重新看实际图片；facts可能概括了同一视频中先后出现的多个不同画面，引用同一fact不等于物件在同一帧共现。
静态细节的anchor必须整体能在focus_frame_id这一张图中核对，其他帧的主体不能搬来当它的背景、倒影或空间关系。
例如一帧有人扶自行车，另一帧才有逆光塔楼，不能写“女子扶车，背景是逆光塔楼”；只留下所选帧真实支持的记忆点。
只有ACTION_CHANGE可合用多帧表达变化，必须看出同一主体的真实变化，不能把转动视角或人物不明的两帧编成动作。
图片里的细节也须在允许fact的内容范围内；你是在核验并选择原事实的一个焦点，不是扩写新事实。不成立的部分可去掉，不要为保留一条高光编造关系。
''' + scene_selection.moment_policy_prompt()
VALUE_TYPES = ('ACTION_CHANGE', 'INTERACTION', 'DISTINCT_DETAIL', 'SCENIC_DISCOVERY', 'INDEPENDENT_SCENE')
MOMENT_SCHEMA = obj({'items': {'type': 'array', 'items': obj({
    'id': TEXT, 'decision': {'enum': ['KEEP', 'DROP']}, 'anchor': TEXT,
    'event_group_id': TEXT, 'comparison_reason': TEXT,
    'scene_kind': {'enum': list(scene_selection.EXPERIENCE_KINDS)}, 'scene_basis_fact_ids': IDS,
    'value_type': {'enum': list(VALUE_TYPES) + ['ROUTINE', 'UNSUPPORTED', 'DUPLICATE']},
    'evidence_frame_ids': IDS, 'focus_frame_id': TEXT, 'reason': TEXT})}})


def moment_request_schema(moments, facts, *, comparison_ids=None, scene_basis_scopes=None):
    """Keep each candidate's references in its own schema branch.

    The provider's JSON mode is not a schema guarantee. compile_moments remains
    the publication gate; this request schema never coerces a fact ID or PTS.
    """
    comparison_ids = list(comparison_ids) if comparison_ids is not None else [m['id'] for m in moments]
    branches = []
    nonempty = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
    for moment in moments:
        frame_ids = facts[moment['fact_id']]['evidence_frame_ids']
        for decision in ('KEEP', 'DROP'):
            row = deepcopy(MOMENT_SCHEMA['properties']['items']['items'])
            fields = row['properties']
            fields['id'] = {'enum': [moment['id']]}
            fields['decision'] = {'enum': [decision]}
            fields['comparison_reason'] = nonempty
            fields['reason'] = nonempty
            basis_ids = (scene_basis_scopes or {}).get(moment['id'], [moment['fact_id']])
            fields['scene_basis_fact_ids'] = {'type': 'array', 'items': {'enum': basis_ids},
                                              'uniqueItems': True, 'minItems': 1}
            fields['event_group_id'] = {'enum': [moment['id']] if decision == 'KEEP' else comparison_ids}
            fields['evidence_frame_ids'] = {'type': 'array', 'items': {'enum': frame_ids},
                                            'uniqueItems': True, 'minItems': 1 if decision == 'KEEP' else 0}
            fields['focus_frame_id'] = {'enum': frame_ids if decision == 'KEEP' else frame_ids + ['']}
            fields['anchor'] = nonempty if decision == 'KEEP' else TEXT
            fields['value_type'] = {'enum': list(VALUE_TYPES) if decision == 'KEEP'
                                    else ['ROUTINE', 'UNSUPPORTED', 'DUPLICATE']}
            branches.append(row)
    return obj({'items': {'type': 'array', 'minItems': len(moments), 'maxItems': len(moments),
                          'items': {'oneOf': branches}}})


def valid_ids(ids, allowed):
    return (isinstance(ids, list) and bool(ids) and all(isinstance(v, str) for v in ids)
            and len(set(ids)) == len(ids) and set(ids) <= set(allowed))


def claim_characters(text):
    """Ignore spacing/punctuation, not words, when checking a real correction.

    This is a lexical integrity check, not a semantic truth or paraphrase test.
    """
    return ''.join(c for c in unicodedata.normalize('NFKC', text)
                   if unicodedata.category(c)[0] in ('L', 'N'))


def validate_corrections(row, original):
    """Require an executable, unambiguous account of changes to a fact.

    Edits refer to non-overlapping spans in the original, not a succession of
    drafts. Their result IS the published fact. The model's redundant full text
    and reason are audit-only and cannot authorize undeclared changes.
    """
    edits = row.get('corrections')
    if not isinstance(edits, list):
        raise ValueError('Missing structured visual corrections')
    decision = row.get('decision')
    if decision in ('KEEP', 'DROP'):
        if edits or (decision == 'KEEP' and row.get('text') != original):
            raise ValueError('KEEP must preserve the original text; DROP cannot carry corrections')
        return row.get('text'), []
    if decision != 'CORRECT' or not edits:
        raise ValueError('CORRECT requires at least one actual claim correction')
    if not isinstance(row.get('text'), str):
        raise ValueError('Invalid corrected text audit copy')
    spans = []
    for edit in edits:
        if not isinstance(edit, dict):
            raise ValueError('Invalid visual correction')
        before, after = edit.get('rejected_text'), edit.get('replacement_text')
        if (not isinstance(before, str) or not isinstance(after, str) or not claim_characters(before)
                or original.count(before) != 1):
            raise ValueError('Correction must identify one exact original claim span')
        if claim_characters(before) == claim_characters(after):
            raise ValueError('Correction changes only spacing or punctuation')
        start = original.index(before)
        spans.append((start, start + len(before), after))
    spans.sort()
    if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
        raise ValueError('Visual correction spans overlap')
    pieces, cursor = [], 0
    for start, end, after in spans:
        pieces.extend((original[cursor:start], after)); cursor = end
    pieces.append(original[cursor:])
    applied_text = ''.join(pieces)
    if claim_characters(applied_text) == claim_characters(original):
        raise ValueError('CORRECT did not change claim content')
    if any(claim_characters(edit['rejected_text']) in claim_characters(applied_text) for edit in edits):
        raise ValueError('Rejected claim remains in corrected text')
    return applied_text, edits


def compile_visual(output, facts, shown):
    rows = output.get('items', []) if isinstance(output, dict) else []
    rows = rows if isinstance(rows, list) else []
    counts = Counter(r.get('fact_id') for r in rows if isinstance(r, dict) and isinstance(r.get('fact_id'), str))
    verified, ledger = {}, []
    for fid, fact in facts.items():
        try:
            if counts[fid] != 1:
                raise ValueError('Missing or duplicate visual judgment')
            row = next(r for r in rows if isinstance(r, dict) and r.get('fact_id') == fid)
            if not isinstance(row.get('reason'), str) or not row['reason'].strip():
                raise ValueError('Missing review reason')
            applied_text, corrections = validate_corrections(row, fact['text'])
            if row.get('decision') == 'DROP':
                if row.get('text') != '' or row.get('evidence_frame_ids') != []:
                    raise ValueError('Dropped fact still contains claims')
                ledger.append({'fact_id': fid, 'asset_id': fact['asset_id'], 'status': 'DROPPED',
                               'decision': 'DROP', 'corrections': [], 'reason': row['reason']})
                continue
            frames = shown[fact['asset_id']]
            if (row.get('decision') not in ('KEEP', 'CORRECT') or not isinstance(applied_text, str)
                    or not applied_text.strip() or not valid_ids(row.get('evidence_frame_ids'), frames)):
                raise ValueError('Invalid visual fact or cross-asset frame')
            pts = [frames[f]['source_timestamp_ms'] for f in row['evidence_frame_ids']]
            temporal = row.get('temporal_support')
            if temporal not in ('STATE', 'CHANGE') or (temporal == 'CHANGE' and len({p for p in pts if p is not None}) < 2):
                raise ValueError('Change claim lacks distinct temporal evidence')
            verified[fid] = {**fact, 'text': applied_text.strip(), 'evidence_frame_ids': row['evidence_frame_ids'],
                             'frame_pts_ms': pts, 'temporal_support': temporal, 'visual_reviewed': True,
                             'original_text': fact['text']}
            ledger.append({'fact_id': fid, 'asset_id': fact['asset_id'], 'status': 'VERIFIED',
                           'decision': row['decision'], 'corrections': corrections,
                           'changed': fact['text'] != applied_text.strip(), 'reason': row['reason'],
                           'text_source': 'APPLIED_CORRECTIONS' if corrections else 'ORIGINAL',
                           'model_text_matches_applied': row['text'] == applied_text,
                           **({'model_text': row['text'], 'applied_text': applied_text}
                              if row['text'] != applied_text else {})})
        except (ValueError, KeyError, TypeError) as exc:
            ledger.append({'fact_id': fid, 'asset_id': fact['asset_id'], 'status': 'UNVERIFIED', 'reason': str(exc)})
    return verified, ledger


def visual_batches(facts, assets, bundle, max_frames=18):
    """One asset never crosses a request; long assets use an audited sample."""
    batch, evidence, shown = {}, [], {}
    for aid in dict.fromkeys(f['asset_id'] for f in facts.values()):
        asset = assets[aid]
        frames = sorted(asset['frames'], key=lambda f: f['source_timestamp_ms'] or 0)
        if len(frames) > max_frames:
            frames = [frames[round(i * (len(frames) - 1) / (max_frames - 1))] for i in range(max_frames)]
        if evidence and len(evidence) + len(frames) > max_frames:
            yield batch, evidence, shown
            batch, evidence, shown = {}, [], {}
        batch.update({fid: f for fid, f in facts.items() if f['asset_id'] == aid})
        shown[aid] = {f['frame_id']: f for f in frames}
        evidence.extend((asset, f, (bundle.manifest_path.parent / f['relative_path']).resolve()) for f in frames)
    if batch:
        yield batch, evidence, shown


def review_visual_facts(facts, assets, bundle, ask, *, prefix='S09A_PRODUCT_VISUAL', max_batches=8,
                        stage_runs=None):
    from . import x02
    verified, ledger, outputs = {}, [], []
    terminal_failure = False

    def record_failure(exc):
        if isinstance(exc, x02.X02StageCallError) and stage_runs is not None:
            if all(run is not exc.stage_run for run in stage_runs):
                stage_runs.append(exc.stage_run)
        return (isinstance(exc, (x02.X02ModelNotReady, x02.X02CallAttemptLimitReached))
                or getattr(exc, 'code', None) in ('MODEL_HTTP_401', 'MODEL_HTTP_403'))

    for index, (batch, evidence, shown) in enumerate(visual_batches(facts, assets, bundle)):
        if index >= max_batches or terminal_failure:
            ledger.extend({'fact_id': f, 'asset_id': v['asset_id'], 'status': 'UNVERIFIED',
                           'reason': ('Visual review unavailable after non-retriable provider failure' if terminal_failure
                                      else 'Visual review call budget exhausted')} for f, v in batch.items())
            continue
        context = {'facts': [{'fact_id': f, 'asset_id': v['asset_id'], 'original_source_asset_id': v['source_asset_id'],
                             'text': v['text']} for f, v in batch.items()],
                   'shown_frames': {a: [{'id': f['frame_id'], 'pts_ms': f['source_timestamp_ms']} for f in fs.values()]
                                    for a, fs in shown.items()}}
        scenes = []
        try:
            source_to_local = {assets[a]['asset_id']: a for a in shown}
            scene_output = ask(prefix + '_%02d_SCENE' % index, SCENE_PROMPT, SCENE_SCHEMA,
                               {'shown_frames': {assets[a]['asset_id']: fs for a, fs in context['shown_frames'].items()},
                                'language': '简体中文'}, evidence=evidence)
            scenes, scene_issues = collect_scenes(scene_output, shown, source_to_local)
            outputs.append({'stage': 'INDEPENDENT_SCENE', 'output': scene_output,
                            'accepted_scenes': scenes, 'rejected': scene_issues})
            output = ask(prefix + '_%02d' % index, VISUAL_PROMPT, VISUAL_SCHEMA,
                         {**context, 'independent_scenes': scenes}, evidence=evidence)
        except (ValueError, OSError, x02.X02Error) as exc:
            terminal_failure = record_failure(exc)
            output = {'failure': type(exc).__name__, 'code': getattr(exc, 'code', 'UNKNOWN')}
        checked, records = compile_visual(output, batch, shown)
        invalid = {r['fact_id']: batch[r['fact_id']] for r in records if r['status'] == 'UNVERIFIED'}
        state_assets = {s['asset_id'] for s in scenes
                        if any(o['temporal_support'] == 'STATE' for o in s['observations'])}
        state_rechecks = {r['fact_id']: batch[r['fact_id']] for r in records
                          if r['status'] == 'DROPPED' and r['asset_id'] in state_assets}
        repair_facts = {**invalid, **state_rechecks}
        if repair_facts and isinstance(output, dict) and 'items' in output:
            # The scene may describe a different fact. Recheck potential static
            # content loss with images; never copy scenes into writable facts.
            issues = [r for r in records if r['status'] == 'UNVERIFIED'] + [
                {'fact_id': fid, 'asset_id': fact['asset_id'], 'status': 'PENDING_STATE_RECHECK',
                 'code': 'POTENTIAL_STATIC_CONTENT_LOSS',
                 'reason': 'Dropped fact shares an asset with independently observed static content; check whether any original part is supported'}
                for fid, fact in state_rechecks.items()]
            records = [{**r, 'status': 'UNVERIFIED', 'state_retention_review': 'UNRESOLVED',
                        'original_drop_reason': r['reason'],
                        'reason': 'Static content retention recheck is unresolved'}
                       if r['fact_id'] in state_rechecks else r for r in records]
            repair_context = {**context, 'facts': [f for f in context['facts'] if f['fact_id'] in repair_facts],
                              'draft': output, 'issues': issues,
                              'independent_scenes': [s for s in scenes if s['asset_id'] in
                                                    {f['asset_id'] for f in repair_facts.values()}]}
            try:
                repaired_output = ask(prefix + '_%02d_REPAIR' % index, VISUAL_PROMPT +
                    '\n仅修复issues中的事实。若单帧不能支持变化，重新看图后只描述成立的状态并标STATE；不要伪造第二帧。'
                    '\nPOTENTIAL_STATIC_CONTENT_LOSS表示需要复核可能被整句删掉的静态内容，不表示原事实成立。'
                    '\n对照原事实、同资产独立观察和真实图片：动作或运镜不成立时，检查原事实中的物件、姿态、环境等是否仍成立；'
                    '有成立部分就通过corrections只保留该部分并引用直接证据。若独立观察只是别的内容、原事实没有任何成立部分，仍可DROP并说明。'
                    '\n不能将独立观察直接复制为新事实，不能为了覆盖素材而强行保留。',
                    VISUAL_SCHEMA, repair_context, evidence=evidence)
                repaired, repaired_records = compile_visual(repaired_output, repair_facts, shown)
                for record in repaired_records:
                    if record['fact_id'] in state_rechecks:
                        record['state_retention_review'] = {'VERIFIED': 'RETAINED_AFTER_REVIEW',
                            'DROPPED': 'CONFIRMED_DROP', 'UNVERIFIED': 'UNRESOLVED'}[record['status']]
                checked.update(repaired)
                records = [r for r in records if r['fact_id'] not in repair_facts] + repaired_records
                outputs.append({'stage': 'VISUAL_CONTRACT_REPAIR', 'issues': repair_context['issues'], 'output': repaired_output})
            except (ValueError, OSError, x02.X02Error) as exc:
                terminal_failure = record_failure(exc)
                outputs.append({'stage': 'VISUAL_CONTRACT_REPAIR_FAILURE',
                                'failure': type(exc).__name__, 'code': getattr(exc, 'code', 'UNKNOWN')})
                # Retain the explicit UNVERIFIED records and failed-attempt audit.
        verified.update(checked); ledger.extend(records); outputs.append(output)
    return verified, ledger, outputs


def collect_scenes(output, shown, source_to_local):
    """Normalize known source IDs; isolate invalid observations instead of
    discarding correct scenes elsewhere in the same bounded request."""
    rows = output.get('assets', []) if isinstance(output, dict) else []
    rows = rows if isinstance(rows, list) else []
    normalized = [{**r, 'asset_id': source_to_local.get(r.get('asset_id'), r.get('asset_id'))}
                  for r in rows if isinstance(r, dict) and isinstance(r.get('asset_id'), str)]
    accepted, issues = [], []
    for aid in shown:
        matched = [r for r in normalized if r['asset_id'] == aid]
        scene = {'asset_id': aid, 'observations': [], 'uncertainties': []}
        if len(matched) != 1:
            issues.append({'asset_id': aid, 'reason': 'Missing or duplicate independent scene'})
        else:
            row = matched[0]
            scene['uncertainties'] = [u for u in row.get('uncertainties', []) if isinstance(u, str)] if isinstance(row.get('uncertainties'), list) else []
            observations = row.get('observations', [])
            for obs in observations if isinstance(observations, list) else []:
                try:
                    validate_scenes({'assets': [{**scene, 'observations': [obs]}]}, {aid: shown[aid]})
                    scene['observations'].append(obs)
                except ValueError as exc:
                    issues.append({'asset_id': aid, 'observation': obs, 'reason': str(exc)})
        accepted.append(scene)
    return accepted, issues


def validate_scenes(output, shown):
    rows = output.get('assets') if isinstance(output, dict) else None
    if not isinstance(rows, list) or len(rows) != len(shown):
        raise ValueError('Missing independent visual scenes')
    ids = [r.get('asset_id') for r in rows if isinstance(r, dict)]
    if len(ids) != len(rows) or len(set(ids)) != len(ids) or set(ids) != set(shown):
        raise ValueError('Independent scene asset mismatch')
    for row in rows:
        observations = row.get('observations')
        if not isinstance(observations, list) or not isinstance(row.get('uncertainties'), list):
            raise ValueError('Invalid independent scene')
        for obs in observations:
            if (not isinstance(obs, dict) or not isinstance(obs.get('text'), str) or not obs['text'].strip()
                    or not valid_ids(obs.get('evidence_frame_ids'), shown[row['asset_id']])):
                raise ValueError('Independent scene contains ungrounded observation')
            pts = {shown[row['asset_id']][f]['source_timestamp_ms'] for f in obs['evidence_frame_ids']}
            if obs.get('temporal_support') not in ('STATE', 'CHANGE') or (obs['temporal_support'] == 'CHANGE' and len(pts - {None}) < 2):
                raise ValueError('Independent scene change lacks temporal evidence')
    return rows


def compile_moments(output, moments, facts, *, scene_basis_scopes=None, require_scene_policy=False):
    """Validate reference provenance, not the semantic truth of model judgments.

    Historical callers may omit the scene contract; those ledgers make no
    scene-policy verification claim. The live review path always requires it.
    """
    rows = output.get('items', []) if isinstance(output, dict) else []
    rows = rows if isinstance(rows, list) else []
    counts = Counter(r.get('id') for r in rows if isinstance(r, dict) and isinstance(r.get('id'), str))
    candidate_ids = {m['id'] for m in moments}
    kept, ledger, used_frames = [], [], set()
    for moment in moments:
        try:
            mid = moment['id']; fact = facts[moment['fact_id']]
            if counts[mid] != 1:
                raise ValueError('Missing or duplicate moment judgment')
            row = next(r for r in rows if isinstance(r, dict) and r.get('id') == mid)
            if not isinstance(row.get('reason'), str) or not row['reason'].strip():
                raise ValueError('Missing moment reason')
            group_id = row.get('event_group_id')
            comparison = row.get('comparison_reason')
            if group_id not in candidate_ids or not isinstance(comparison, str) or not comparison.strip():
                raise ValueError('Moment lacks within-batch event comparison')
            scene_audit = {}
            if require_scene_policy:
                allowed_basis = (scene_basis_scopes or {}).get(mid, [moment['fact_id']])
                # Standalone Aha cannot inherit a chapter's scene, even if a
                # caller accidentally supplies an overbroad scope.
                if moment['parent_chapter_id'] is None:
                    allowed_basis = [moment['fact_id']]
                if (row.get('scene_kind') not in scene_selection.EXPERIENCE_KINDS
                        or not valid_ids(row.get('scene_basis_fact_ids'), set(allowed_basis) & set(facts))):
                    raise ValueError('Moment scene policy lacks in-scope fact evidence')
                scene_audit = {'scene_kind': row['scene_kind'],
                               'scene_basis_fact_ids': list(row['scene_basis_fact_ids']),
                               'scene_policy_version': scene_selection.POLICY_VERSION}
            if row.get('decision') == 'DROP':
                if row.get('value_type') not in ('ROUTINE', 'UNSUPPORTED', 'DUPLICATE'):
                    raise ValueError('Dropped moment needs an explicit rejection type')
                if (row['value_type'] == 'DUPLICATE') != (group_id != mid):
                    raise ValueError('Duplicate must identify another representative candidate')
                ledger.append({'id': mid, 'status': 'NOT_SELECTED', 'value_type': row.get('value_type'),
                               'event_group_id': group_id, 'comparison_reason': comparison, 'reason': row['reason'],
                               **scene_audit})
                continue
            if (row.get('decision') != 'KEEP' or row.get('value_type') not in VALUE_TYPES
                    or not isinstance(row.get('anchor'), str) or not row['anchor'].strip()
                    or not valid_ids(row.get('evidence_frame_ids'), fact['evidence_frame_ids'])
                    or row.get('focus_frame_id') not in row['evidence_frame_ids']):
                raise ValueError('Moment lacks grounded distinct value')
            if group_id != mid:
                raise ValueError('Only one representative may be kept for an event')
            pts = dict(zip(fact['evidence_frame_ids'], fact['frame_pts_ms']))
            if row['value_type'] == 'ACTION_CHANGE' and (fact.get('temporal_support') != 'CHANGE'
                    or len({pts[f] for f in row['evidence_frame_ids'] if pts[f] is not None}) < 2):
                raise ValueError('Action highlight lacks temporal evidence')
            if row['value_type'] == 'INDEPENDENT_SCENE' and moment['parent_chapter_id'] is not None:
                raise ValueError('Generic independent scene is not a chapter highlight')
            keys = {(fact['asset_id'], f) for f in row['evidence_frame_ids']}
            if keys & used_frames:
                raise ValueError('Duplicate moment evidence')
            used_frames.update(keys)
            kept.append({**moment, 'focus': row['anchor'].strip(), 'revisit_reason': row['reason'],
                         'event_group_id': group_id, 'comparison_reason': comparison,
                         'value_type': row['value_type'], 'focus_frame_ids': [row['focus_frame_id']] +
                         [f for f in row['evidence_frame_ids'] if f != row['focus_frame_id']]})
            ledger.append({'id': mid, 'status': 'SELECTED', 'value_type': row['value_type'],
                           'event_group_id': group_id, 'comparison_reason': comparison, 'reason': row['reason'],
                           **scene_audit})
        except (ValueError, KeyError, TypeError) as exc:
            ledger.append({'id': moment.get('id'), 'status': 'UNVERIFIED', 'reason': str(exc)})
    selected_ids = {m['id'] for m in kept}
    for row in ledger:
        if (row.get('value_type') == 'DUPLICATE' and row['event_group_id'] not in selected_ids):
            row.update(status='UNVERIFIED', reason='Duplicate representative was not selected')
    return kept, ledger


def chapter_focus_context(chapters, facts):
    """Selection intent is usable only when all its references are in scope.

    A valid reference is a prerequisite, not proof that the theme interpretation
    is correct. Rejected focus prose is audit data, never a new fact for ranking.
    """
    kinds = set(scene_selection.EXPERIENCE_KINDS)
    scoped, issues = [], []
    for chapter in chapters:
        raw_ids = chapter.get('fact_ids', [])
        chapter_ids = [fid for fid in raw_ids if isinstance(fid, str) and fid in facts] if isinstance(raw_ids, list) else []
        focus = chapter.get('selection_focus')
        valid = (isinstance(focus, dict) and isinstance(focus.get('experience_kind'), str)
                 and focus['experience_kind'] in kinds
                 and isinstance(focus.get('focus'), str) and bool(focus['focus'].strip())
                 and valid_ids(focus.get('fact_ids'), chapter_ids))
        if not valid:
            focus = {'experience_kind': 'UNCERTAIN', 'focus': '', 'fact_ids': []}
            issues.append({'chapter_id': chapter['id'], 'code': 'SELECTION_FOCUS_OUT_OF_SCOPE',
                           'reason': 'Selection focus is missing or not fully supported by current parent-chapter facts'})
        else:
            focus = {key: focus[key] for key in ('experience_kind', 'focus', 'fact_ids')}
        scoped.append({'id': chapter['id'], 'fact_ids': chapter_ids, 'selection_focus': focus})
    return scoped, issues


def moment_scene_basis_scopes(moments, scoped_chapters):
    """Expose only the candidate and its validated parent focus as scene cues."""
    parents = {c['id']: c for c in scoped_chapters}
    scopes = {}
    for moment in moments:
        parent = parents.get(moment['parent_chapter_id'])
        focus_ids = parent['selection_focus']['fact_ids'] if parent else []
        scopes[moment['id']] = list(dict.fromkeys([moment['fact_id'], *focus_ids]))
    return scopes


def moment_visual_scope(moments, facts, assets, bundle, max_frames=24):
    """Bounded round-robin evidence; never infer co-presence from a clip fact.

    The provider sees the exact frame allowlist used in its schema. Source facts
    remain untouched; omitted frames cannot support this particular judgment.
    """
    refs = {}
    for moment in moments:
        fact = facts[moment['fact_id']]
        aid = fact['asset_id']
        frames = {f['frame_id']: f for f in assets[aid]['frames']}
        refs[moment['id']] = [(aid, fid) for fid in fact['evidence_frame_ids'] if fid in frames]
    chosen = []
    for index in range(max((len(v) for v in refs.values()), default=0)):
        for rows in refs.values():
            if index < len(rows) and rows[index] not in chosen and len(chosen) < max_frames:
                chosen.append(rows[index])
    scoped = deepcopy(facts)
    evidence, shown = [], []
    for aid, frame_id in chosen:
        asset = assets[aid]
        frame = next(f for f in asset['frames'] if f['frame_id'] == frame_id)
        evidence.append((asset, frame, (bundle.manifest_path.parent / frame['relative_path']).resolve()))
        shown.append({'asset_id': aid, 'source_asset_id': asset['asset_id'],
                      'frame_id': frame_id, 'pts_ms': frame['source_timestamp_ms']})
    for moment in moments:
        fid = moment['fact_id']; fact = scoped[fid]
        pairs = [(frame, pts) for frame, pts in zip(fact['evidence_frame_ids'], fact['frame_pts_ms'])
                 if (fact['asset_id'], frame) in chosen]
        fact['evidence_frame_ids'] = [frame for frame, _ in pairs]
        fact['frame_pts_ms'] = [pts for _, pts in pairs]
    return scoped, evidence, {'policy': 'EXACT_SHOWN_FRAMES; STATIC_ANCHOR_MUST_FIT_FOCUS_FRAME',
                              'max_frames': max_frames, 'shown_frames': shown}


def review_moments(moments, chapters, facts, ask, stage='S10_PRODUCT_MOMENT_VALUE', stage_runs=None,
                   *, assets=None, bundle=None):
    from . import x02
    if not moments:
        return [], [], {}
    image_review = assets is not None and bundle is not None
    evidence, visual_scope, unavailable = [], {}, []
    if image_review:
        facts, evidence, visual_scope = moment_visual_scope(moments, facts, assets, bundle)
        unavailable = [{'id': m['id'], 'status': 'UNVERIFIED', 'reason': 'No shown image for moment review'}
                       for m in moments if not facts[m['fact_id']]['evidence_frame_ids']]
        moments = [m for m in moments if facts[m['fact_id']]['evidence_frame_ids']]
        if not moments:
            return [], unavailable, {'visual_scope': visual_scope}
    scoped_chapters, focus_issues = chapter_focus_context(chapters, facts)
    scene_scopes = moment_scene_basis_scopes(moments, scoped_chapters)
    context = {'moments': moments, 'comparison_candidates': moments, 'chapters': scoped_chapters,
               'allowed_fact_ids': list(facts),
               'candidate_evidence': {m['id']: {'fact_id': m['fact_id'],
                                      'allowed_frame_ids': facts[m['fact_id']]['evidence_frame_ids'],
                                      'allowed_scene_basis_fact_ids': scene_scopes[m['id']]} for m in moments},
               'scene_moment_policy': scene_selection.moment_policy_context(),
               'selection_focus_issues': focus_issues,
               'visual_scope': visual_scope,
               'facts': [{k: f[k] for k in ('id', 'asset_id', 'text', 'evidence_frame_ids', 'frame_pts_ms', 'temporal_support')}
                         for f in facts.values()]}
    output, failures = {}, []
    schema = moment_request_schema(moments, facts, scene_basis_scopes=scene_scopes)
    for attempt in range(2):
        try:
            output = ask(stage + ('_RETRY' if attempt else ''), MOMENT_PROMPT, schema, context,
                         **({'evidence': evidence} if image_review else {}))
            break
        except (ValueError, OSError, x02.X02Error) as exc:
            failures.append({'type': type(exc).__name__, 'code': getattr(exc, 'code', 'UNKNOWN')})
            if isinstance(exc, x02.X02StageCallError) and stage_runs is not None:
                stage_runs.append(exc.stage_run)
            if not isinstance(exc, (ValueError, x02.X02StageCallError)) or (
                    isinstance(exc, x02.X02StageCallError) and exc.stage_run.call_status != 'RESPONSE_INVALID'):
                break
    if not isinstance(output, dict):
        failures.append({'type': 'InvalidOutputShape', 'code': 'MOMENT_RESPONSE_NOT_OBJECT'})
        output = {'invalid_provider_output': deepcopy(output)}
    kept, ledger = compile_moments(output, moments, facts, scene_basis_scopes=scene_scopes, require_scene_policy=True)
    invalid_ids = {r['id'] for r in ledger if r['status'] == 'UNVERIFIED'}
    if invalid_ids and isinstance(output.get('items'), list):
        invalid = [m for m in moments if m['id'] in invalid_ids]
        allowed = {m['id']: facts[m['fact_id']]['evidence_frame_ids'] for m in invalid}
        try:
            repaired_output = ask(stage + '_REPAIR', MOMENT_PROMPT +
                '\nevidence_frame_ids必须是allowed_frame_ids中的字符串编号，不是9958之类毫秒时间。仅修复issues对应候选，不能猜测默认引用。'
                '\ncomparison_candidates仍是完整比较范围；修复时不得与draft中已有效保留的其他候选重复，event_group_id可指向该有效候选。',
                moment_request_schema(invalid, facts, comparison_ids=[m['id'] for m in moments],
                                      scene_basis_scopes=scene_scopes),
                {**context, 'moments': invalid, 'draft': output, 'allowed_frame_ids': allowed,
                                'issues': [r for r in ledger if r['id'] in invalid_ids]},
                **({'evidence': evidence} if image_review else {}))
            if not isinstance(repaired_output, dict) or not isinstance(repaired_output.get('items'), list):
                output = {**output, 'invalid_contract_repair_output': deepcopy(repaired_output)}
                raise ValueError('Moment repair response must be an object containing an items array')
            # Revalidate the combined output so repairs cannot duplicate the
            # support frames of an already accepted moment.
            combined = {'items': [r for r in output['items'] if isinstance(r, dict) and r.get('id') not in invalid_ids]
                        + [r for r in repaired_output.get('items', []) if isinstance(r, dict) and r.get('id') in invalid_ids]}
            kept, ledger = compile_moments(combined, moments, facts, scene_basis_scopes=scene_scopes,
                                           require_scene_policy=True)
            output = {**combined, 'original_output': output, 'contract_repair_output': repaired_output}
        except (ValueError, OSError, x02.X02Error) as exc:
            failures.append({'type': type(exc).__name__, 'code': getattr(exc, 'code', 'UNKNOWN')})
            if isinstance(exc, x02.X02StageCallError) and stage_runs is not None:
                stage_runs.append(exc.stage_run)
    if image_review:
        for moment in kept:
            moment['anchor_reviewed_with_images'] = True
            # A static moment is one coherent view. The text writer must not
            # receive the other clip frames as permission to combine scenery.
            if moment['value_type'] != 'ACTION_CHANGE':
                moment['focus_frame_ids'] = moment['focus_frame_ids'][:1]
    return kept, ledger + unavailable, {**output, 'scene_policy_version': scene_selection.POLICY_VERSION,
                         'visual_scope': visual_scope,
                         'review_basis': 'FACTS_AND_SHOWN_IMAGES' if image_review else 'FACT_TEXT_ONLY',
                         **({'call_failures': failures} if failures else {}),
                         **({'selection_focus_issues': focus_issues} if focus_issues else {})}
