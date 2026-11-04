"""Evidence-first Chapter planning with noncontiguous thematic episode fusion.

A recurring location or activity may be combined across distant source spans.
Time/order helps explain experience context; it is never a mandatory split.
All fact/frame bindings are grounded and validated, with explicit stage audit.
"""
from collections import Counter
from copy import deepcopy

from jsonschema import Draft202012Validator

from . import chapter_episode_router as legacy
from .scene_selection import EXPERIENCE_KINDS
from .scenelet_builder import tokens

VERSION = "GLOBAL_THEMATIC_EPISODES_AND_CHAPTERS_V02"
MAX_MICRO_EPISODES = 18

EPISODE_PROMPT = """你是一名第一人称生活日记的全局素材编辑。请先观察全部逐段视觉事实，
找出具有意义、持续一段内容的独立经历（Episode），暂时不要决定最终Chapter数量。
source_index只是素材导入序号，不能推断每个片段间隔多久、用户是否返回或当时的情绪。

区分经历的依据：可辨认的活动、具体建筑/作品/人物/物体、空间与场景、以及真实内容变化。
不能因为过了若干分钟、进入一个路口、或者同一建筑再次出现就开新重要经历。
连续、短暂且同类的画面可以归为一个经历；不同体验即使都是WALKING也要留清楚边界。
同一地点后来再次出现，如果与当前局部园林/商业内容确实形成不同的视觉场景，
在Episode识别阶段可先暂存成独立的观察段，之后由全局主编决定是否融合进
前面相同的主题Chapter；并不是要求再新开一个Chapter，避免重复地点造成机械拆章。
特别注意在一天的最开头和最末尾也要检查实际画面，不能把清楚的新场景并入上一段
泛泛的步行主题。但仅有几秒的无关变化或片尾广告绝不值得新Episode。
多角度观看同一物体、连续骑行经过不同道路，也不能只凭视角改变拆成多个经历。

只输出1..max_episodes个真实素材闭区间，严格完整、按序覆盖0..source_count-1，无重叠无空缺。
theme/reason来自真实观察，不创造F ID、媒体ID、人物关系或时间信息，不为了凑数量拆章。
这只是细粒度Episode层级，不要直接压到最终3–5个Chapter。只返回JSON。"""

EPISODE_REPAIR_PROMPT = """检查上次Episode区间JSON的合同错误：区间必须从0开始连续
覆盖到source_count-1。只修复错误区间，原来合法的主题与边界不应随意改变。
不能人为填充未知经历，不能凭时间凑分段，返回完整合法JSON。"""

CHAPTER_PROMPT = """你是全局生活日记主编。现在阅读全部有视觉证据的Episode，
在理解主题后组织为1..chapter_limit个真正值得用户回顾的Chapter。
核心规则：相同地点、同一活动、同一体验若在不连续的时间段重现，可以融合成同一Chapter；
时间顺序是上下文，不是必须切分的规则。一个地方回来两次，不等于必须有两个Chapter！
不同Episode只要同一实质主题，可以一同归属一章，episode_ids不要求连续。
反过来，不同主题即使相邻也可以独立，真正独立的作品、博物馆、商业活动、城市公园、
园林植物、运动或其它有辨识度的经历不应被泛泛的城市漫步描述吞并。
若连续同一骑行活动很久，允许只有一章；不是为了凑满五章而拆碎视频。

每个Episode必须恰好分配到一章，不能遗漏、不能重复。
每个Chapter选择1..4条高价值anchor_fact_ids，为后续图片候选保留有辨识度的
真实建筑、作品、活动、事件或具体自然主体，优先于普通道路、墙面、背景人群。
只从输入已经有可靠视觉事实的fact_id中选择，并且必须属于该章分配的Episode。
注意：选出锚点不表示图片画质已通过；真正的图片审核还要在后续逐帧执行。
不能编造事实、图片、时间或人物关系，也不能把同一地点重现当成固定章节理由。
返回严格JSON。"""

CHAPTER_REPAIR_PROMPT = """此前Chapter方案遗漏/重复分配了Episode，或者选了
不属于本章Episode的视觉事实锚点。只修改错误项，每个Episode必须且只能有一个父章；
允许同一地点非连续地融合到同一个Chapter。不得创造事实ID、地点或素材，返回合法JSON。"""

CHAPTER_COHERENCE_REPAIR_PROMPT = """上一版经独立编辑核查有严重的内容混合：
一个Chapter同时承担购物/商业市场等活动和独立的自然公园/园林经历，已经形成主题松散的大杂烩。
这里列出的mixed_theme_chapters是需重点修正的编辑问题，不是要强制不同地标都开新章。
请重新进行全局Episode归属：可以合并两个相似的海滨或市场Chapter，释放一个Chapter席位给园林；
也可以直接把有不同主题的Episode归入已有最相关Chapter。允许少于五章，不能凑数字。
请认真分析每个Episode的内容，再把不连贯的主题重新组织；不是仅修改标题、reason。
不同时间的相同地点/同一主题允许直接融合；不需要再次单开新章。
所有真实Episode必须恰好归属一次、所有1..4条高价值视觉事实锚点必须归属于其Chapter。
禁止捏造事实、素材、拍摄时钟或额外Episode，返回完整合法JSON。"""


def thematic_coherence_conflicts(grouping, episodes):
    """Conservative generic activity conflict detector, not a place list.

    Two unrelated experiences can share a Chapter if one is only a short
    incidental frame, but distinct reviewed Episodes for a persistent
    shopping experience and a persistent garden/park are a strong review
    obligation. This detector only requests an editor correction; it cannot
    silently publish, split or change fact ownership.
    """
    byid={e['episode_id']:e for e in episodes}
    incompatible=[
       (frozenset({'MARKET_SHOPPING'}),frozenset({'GARDEN','PARK_LEISURE'})),
       (frozenset({'DINING'}),frozenset({'GARDEN','PARK_LEISURE'})),
    ]
    # A Chapter with several subexperiences can hide a completely unrelated
    # episode. This is a review signal only: spelling/lexical overlap is
    # NEVER used as a hard factual judgement or a new-Chapter rule.
    common={'the','and','with','into','through','from','near','area',
            'walk','walking','views','view','exploration','visit',
            'day','journey','chapter','local','around'}
    def meaningful(text):
        return {x for x in tokens(text) if x not in common}
    conflicts=[]
    for idx,c in enumerate(grouping,1):
        rows=[byid[e] for e in c['episode_ids']]
        kinds={e['experience_kind'] for e in rows}
        triggers=[{'left':sorted(a),'right':sorted(b)}
          for a,b in incompatible if kinds & a and kinds & b]
        lexical_outliers=[]
        if len(rows)>=3:
            theme_tokens=meaningful(c['title'])
            for e in rows:
                evidence=meaningful(e['theme'])
                other=set().union(*(meaningful(other['theme'])
                                    for other in rows if other is not e))
                if (len(evidence)>=2 and not evidence.intersection(theme_tokens)
                        and not evidence.intersection(other)):
                    lexical_outliers.append({'episode_id':e['episode_id'],
                        'episode_theme':e['theme'],
                        'reason':'EPISODE_SUBJECT_NOT_PRESENT_IN_CHAPTER_OR_PEER_THEMES'})
        if triggers or lexical_outliers:
            conflicts.append({'chapter_index':idx,'chapter_theme':c['title'],
              'episode_ids':c['episode_ids'],
              'episode_themes':[e['theme'] for e in rows],
              'kinds':sorted(kinds),'incompatible_activity_groups':triggers,
              'lexical_subject_outliers':lexical_outliers})
    return conflicts


CHAPTER_COHERENCE_PROMPT = """请作为独立复核编辑审查上一版全局Chapter，而不是机械地保持其5章数量。
逐项对照所有Episode的主题与实际画面描述，判断每个Chapter是否有共同的内容主线。
如果一章不自然地拼接了两个独立的活动/场景（例如一个展览场景与无关的商店活动），
应把它们分别归入有主题关联的其它章，或在章数允许时分开。允许最终从5章降为4章。
不要因为一个建筑/地方在时间线末尾再次出现就产生“返回同一地点”的第二章；
同一实质体验应跨时间合并，但也不得把不同活动因共享WALKING标签强行合并。
每个Episode仍恰好归属一个Chapter，且每章必须保留能直接支持主题的1..4条高价值
真实fact ID作为候选图锚点，优先给有辨识度的建筑/作品/重要活动而非普通道路。
不为满足五章限额乱加标题，不补写或捏造没有提供的事实。
若前版符合上述规则，可原样完整返回。只输出JSON。"""


def coherence_penalty(grouping, episodes):
    """Only rank proposals for *additional review*, not force a boundary.

    A semantically unrelated Episode that is also isolated far outside its
    parent Chapter's other source ranges is more suspicious than a short
    adjacent transition scene. Matching nonadjacent themes incur no penalty:
    this permits genuine repeated-location fusion.
    """
    problems=thematic_coherence_conflicts(grouping,episodes)
    score=0.
    for problem in problems:
        score+=5.*len(problem['incompatible_activity_groups'])
        group=problem['episode_ids']
        for outlier in problem['lexical_subject_outliers']:
            eid=outlier['episode_id']
            n=int(eid[1:])
            near=min((abs(n-int(other[1:])) for other in group if other!=eid),
                     default=1)
            score+=1.+min(4.,max(0,near-1)*0.6)
    return round(score,4)


def _valid(schema, value):
    return next(Draft202012Validator(schema).iter_errors(value), None) is None


def episode_schema(count, limit):
    if not 1 <= limit <= MAX_MICRO_EPISODES:
        raise ValueError("Invalid microepisode limit")
    row = {'type':'object','additionalProperties':False,
           'required':['start_index','end_index','theme','experience_kind','reason'],
           'properties':{
             'start_index':{'type':'integer','minimum':0,'maximum':count-1},
             'end_index':{'type':'integer','minimum':0,'maximum':count-1},
             'theme':{'type':'string','minLength':2},
             'experience_kind':{'enum':sorted(EXPERIENCE_KINDS)},
             'reason':{'type':'string','minLength':8}}}
    return {'type':'object','additionalProperties':False,'required':['episodes'],
       'properties':{'episodes':{'type':'array','minItems':1,
           'maxItems':min(limit,count),'items':row}}}


def validate_episodes(output, count, limit=MAX_MICRO_EPISODES):
    if not _valid(episode_schema(count,limit),output):
        raise ValueError("EPISODE_PROPOSAL_SCHEMA_INVALID")
    cursor=0
    for episode in output['episodes']:
        if episode['start_index']!=cursor or episode['end_index']<cursor:
            raise ValueError("EPISODE_PROPOSAL_GAP_OVERLAP_OR_REORDER")
        cursor=episode['end_index']+1
    if cursor!=count:
        raise ValueError("EPISODE_PROPOSAL_INCOMPLETE_COVERAGE")
    return [{**deepcopy(e),'episode_id':f'E{i+1:02d}'}
            for i,e in enumerate(output['episodes'])]


def _episode_facts(episodes, assets, facts, observations):
    """Distributed, directly verified fact evidence for each provisional episode."""
    order={aid:a['sequence_index'] for aid,a in assets.items()}
    by_source={o.get('source_asset_id'):o for o in observations if isinstance(o,dict)}
    out=[]
    for episode in episodes:
        left,right=episode['start_index'],episode['end_index']
        candidates=[(fid,f) for fid,f in facts.items()
           if f.get('visual_reviewed') and f.get('asset_id') in order
              and left<=order[f['asset_id']]<=right]
        candidates.sort(key=lambda t:(order[t[1]['asset_id']],t[0]))
        if not candidates:
            raise ValueError("EPISODE_WITHOUT_VISUALLY_REVIEWED_EVIDENCE")
        count=min(16,len(candidates))
        positions={round(i*(len(candidates)-1)/(count-1)) for i in range(count)} if count>1 else {0}
        chosen=[candidates[i] for i in sorted(positions)]
        excerpt=[{'fact_id':fid,'text':f['text'][:170],
                  'source_index':order[f['asset_id']]}
                 for fid,f in chosen]
        # Secondary lexical richness merely broadens context; it is not used
        # to replace image verification or hardcode any geographic landmark.
        local=Counter()
        for _,f in candidates:
            local.update(tokens(f['text']))
        def richness(row):
            return sum(min(3,local[x]) for x in tokens(row[1]['text']))
        seen={row['fact_id'] for row in excerpt}
        for fid,f in sorted(candidates,
                key=lambda row:(-richness(row),order[row[1]['asset_id']]))[:4]:
            if fid not in seen:
                excerpt.append({'fact_id':fid,'text':f['text'][:170],
                                'source_index':order[f['asset_id']]})
                seen.add(fid)
        out.append({**episode,'fact_count':len(candidates),
          'candidate_fact_ids':[fid for fid,_ in candidates],
          'representative_verified_facts':excerpt,
          'activities':sorted({by_source.get(assets[f['asset_id']]['asset_id'],{}).get('activity_code','UNKNOWN')
                               for _,f in candidates}),
          'time_basis':'IMPORT_SEQUENCE_ONLY'})
    return out


def chapter_schema(episode_ids, fact_ids, chapter_limit):
    if not episode_ids or not fact_ids:
        raise ValueError("Cannot plan without grounded visual evidence")
    row={'type':'object','additionalProperties':False,
      'required':['title','experience_kind','episode_ids','anchor_fact_ids','reason'],
      'properties':{
        'title':{'type':'string','minLength':3,'maxLength':80},
        'experience_kind':{'enum':sorted(EXPERIENCE_KINDS)},
        'episode_ids':{'type':'array','minItems':1,'uniqueItems':True,
            'items':{'enum':episode_ids}},
        'anchor_fact_ids':{'type':'array','minItems':1,'maxItems':4,
            'uniqueItems':True,'items':{'enum':fact_ids}},
        'reason':{'type':'string','minLength':8}}}
    return {'type':'object','additionalProperties':False,'required':['chapters'],
      'properties':{'chapters':{'type':'array','minItems':1,
            'maxItems':min(chapter_limit,len(episode_ids)),'items':row}}}


def validate_chapters(proposal, episodes, assets, facts, chapter_limit):
    spans={e['episode_id']:set(range(e['start_index'],e['end_index']+1)) for e in episodes}
    order={aid:a['sequence_index'] for aid,a in assets.items()}
    valid_fids=[fid for fid,f in facts.items() if f.get('visual_reviewed')
                and f.get('asset_id') in order]
    if not _valid(chapter_schema(list(spans),valid_fids,chapter_limit),proposal):
        raise ValueError("THEMATIC_CHAPTER_SCHEMA_INVALID")
    assigned=[]
    normalized=[]
    for row in proposal['chapters']:
        selected=row['episode_ids']
        assigned.extend(selected)
        indices=set().union(*(spans[e] for e in selected))
        chapter_fids={fid for fid in valid_fids if order[facts[fid]['asset_id']] in indices}
        if not chapter_fids or not set(row['anchor_fact_ids'])<=chapter_fids:
            raise ValueError("CHAPTER_ANCHOR_OUTSIDE_EPISODE")
        normalized.append({**deepcopy(row),
                           'first_index':min(indices),'source_indices':sorted(indices)})
    if len(set(assigned))!=len(assigned) or set(assigned)!=set(spans):
        raise ValueError("EPISODE_ASSIGNMENT_NOT_EXACTLY_ONCE")
    normalized.sort(key=lambda row:row['first_index'])
    return normalized



def normalize_invalid_visual_anchors(proposal, episodes, assets, facts, chapter_limit):
    """Post-LLM scope-only repair; never change a theme or Episode owner.

    Repair is allowed only after the single explicit S07U provider repair
    still repeats a cross-Episode image reference. A replacement must be a
    truly image-reviewed F ID from one of the assigned Episodes. No facts
    or source memberships are invented, and validation is rerun afterwards.
    """
    spans={e['episode_id']:set(range(e['start_index'],e['end_index']+1))
           for e in episodes}
    order={aid:a['sequence_index'] for aid,a in assets.items()}
    valid=[fid for fid,f in facts.items() if f.get('visual_reviewed') is True
           and f.get('asset_id') in order]
    schema=chapter_schema(list(spans),valid,chapter_limit)
    if not _valid(schema,proposal):
        raise ValueError('Cannot recover malformed Chapter structure by editing visual anchor IDs')
    amended=deepcopy(proposal)
    corrections=[]
    for row in amended['chapters']:
        ids=row['episode_ids']
        if not ids or len(set(ids))!=len(ids) or any(e not in spans for e in ids):
            raise ValueError('Cannot repair unknown or repeated Episode identities')
        members=set().union(*(spans[e] for e in ids))
        allowed={fid for fid in valid if order[facts[fid]['asset_id']] in members}
        if not allowed:
            raise ValueError('Cannot repair Chapter without any verified image')
        before=row['anchor_fact_ids']
        after=[fid for fid in before if fid in allowed]
        if len(after)==len(before):
            continue
        if not after:
            # Prefer the first representative visual evidence listed from
            # this Chapter's actual Episode; never fall back to a model-
            # invented or foreign F ID. Frame/identity checks already ran.
            actual=[fid for fid in valid if fid in allowed]
            actual.sort(key=lambda fid:(order[facts[fid]['asset_id']],fid))
            after=actual[:1]
        row['anchor_fact_ids']=after
        corrections.append({'title':row['title'],
             'removed_foreign_or_unverified_anchor_facts':
                [fid for fid in before if fid not in allowed],
             'retained_actual_verified_anchor_facts':after,
             'rule':'ONLY_VERIFIED_FACTS_FROM_ASSIGNED_EPISODES'})
    if not corrections:
        raise ValueError('No valid deterministic anchor correction possible')
    return amended,corrections


def build_wire(chapters, assets, facts):
    """Ground noncontiguous thematic group membership to the original asset F IDs."""
    order={aid:a['sequence_index'] for aid,a in assets.items()}
    wire={'chapters':[],'moments':[],'chapter_boundaries':[],'unselected_facts':[]}
    used=set()
    for i,row in enumerate(chapters,1):
        indices=set(row['source_indices'])
        fids=[fid for fid,f in facts.items() if f.get('asset_id') in order
              and order[f['asset_id']] in indices]
        if not fids or used.intersection(fids):
            raise ValueError("REPEATED_OR_EMPTY_VERIFIED_EPISODE_FACTS")
        used.update(fids)
        anchors=[fid for fid in row['anchor_fact_ids'] if fid in fids]
        if not anchors:
            raise ValueError("UNSUPPORTED_CHAPTER_ANCHOR")
        wire['chapters'].append({'id':f'C{i:02d}','theme':row['title'],
            'fact_ids':fids,'experience_kind':row['experience_kind'],
            'focus':row['title'],'focus_fact_ids':anchors,
            # This field enters the PUBLIC image-backed chapter contract.
            # The model's grouping reason can mention an unproved trip
            # relation such as 'again/return', even though its Episode/F IDs
            # are valid. Keep raw model prose in the Episode audit, and bind
            # the public grouping reason to a neutral deterministic
            # fact-ownership statement without implying travel chronology.
            'grouping_reason':'本章依照实际已核验图像事实中的共同视觉主体与活动组织。'})
    if used!=set(facts):
        raise ValueError("VERIFIED_FACT_LOST_DURING_CROSS_TIME_FUSION")
    for i,left in enumerate(wire['chapters']):
        for right in wire['chapters'][i+1:]:
            wire['chapter_boundaries'].append({
              'chapter_ids':[left['id'],right['id']],
              'basis':'DIFFERENT_ACTIVITY' if left['experience_kind']!=right['experience_kind']
                     else 'SEPARATE_EXPERIENCE',
              'evidence_fact_ids':[left['focus_fact_ids'][0],right['focus_fact_ids'][0]],
              'reason':'独立视觉事实支持不同主题；相同经历允许跨时间融合，不因地点重复拆章。'})
    return wire


def plan(assets, observations, facts, ask, *, chapter_limit=legacy.MAX_CHAPTERS,
         visual_memory=None):
    if not facts:
        raise ValueError("NO_VISUALLY_VERIFIED_FACTS_TO_PLAN")
    ctx=legacy.context(assets,observations,chapter_limit=chapter_limit)
    n=ctx['source_count']
    limit=min(MAX_MICRO_EPISODES,n)
    from . import global_visual_memory
    if visual_memory is None:
        visual_memory=global_visual_memory.build(assets,facts,observations)
    compact=global_visual_memory.editor_context(visual_memory,max_anchors=48)
    context={**ctx,'max_episodes':limit,
        'episode_count_not_limited_to_chapter_limit':True,
        'policy':VERSION,'cross_time_theme_fusion_allowed':True,
        'global_memory':compact,
        'global_entity_candidates_are_hypotheses_not_proven_identifications':True}
    raw=ask('S07T_THEMATIC_EPISODE_DISCOVERY',EPISODE_PROMPT,
            episode_schema(n,limit),context)
    repairs=[]
    try:
        episodes=validate_episodes(raw,n,limit)
    except (ValueError,TypeError,KeyError) as e:
        repairs.append({'stage':'S07T','reason':str(e)})
        raw=ask('S07T_THEMATIC_EPISODE_INTERVAL_REPAIR',EPISODE_REPAIR_PROMPT,
                episode_schema(n,limit),
                {**context,'invalid_proposal':raw,'validation_error':str(e)})
        episodes=validate_episodes(raw,n,limit)
    grounded=_episode_facts(episodes,assets,facts,observations)
    ids=sorted(facts)
    schema=chapter_schema([e['episode_id'] for e in episodes],ids,chapter_limit)
    subcontext={'policy':VERSION,'chapter_limit':chapter_limit,
         'episodes':grounded,'allowed_fact_ids':ids,
         'global_memory':compact,
         'do_not_split_repeated_location':True,
         'time_basis':'IMPORT_SEQUENCE_ONLY'}
    raw_chapters=ask('S07U_THEMATIC_CHAPTER_FUSION',CHAPTER_PROMPT,schema,subcontext)
    try:
        normalized=validate_chapters(raw_chapters,episodes,assets,facts,chapter_limit)
    except (ValueError,TypeError,KeyError) as e:
        repairs.append({'stage':'S07U','reason':str(e)})
        raw_chapters=ask('S07U_THEMATIC_CHAPTER_REPAIR',CHAPTER_REPAIR_PROMPT,
             schema,{**subcontext,'invalid_proposal':raw_chapters,
                     'validation_error':str(e)})
        try:
            normalized=validate_chapters(raw_chapters,episodes,assets,facts,chapter_limit)
        except ValueError as second_error:
            if str(second_error)!='CHAPTER_ANCHOR_OUTSIDE_EPISODE':
                raise
            amended,anchor_corrections=normalize_invalid_visual_anchors(
                raw_chapters,episodes,assets,facts,chapter_limit)
            # The Episode membership and original provider rationale are
            # unchanged. Only image fact anchors are replaced with real
            # verified F IDs from those already assigned source indices.
            normalized=validate_chapters(amended,episodes,assets,facts,chapter_limit)
            repairs.append({'stage':'S07U_ANCHOR_SCOPE_ONLY',
                'reason':'MODEL_REPAIR_STILL_REFERENCED_FOREIGN_FACT',
                'items':anchor_corrections})
    # The proposal compiler only guarantees ownership. A separate semantic
    # critique improves editorial coherence; invalid revisions are rejected
    # and the already-valid plan stays intact, never deleting evidence.
    reviewer={'attempted':True,'accepted':False,'status':'RETAINED_VALID_PROPOSAL'}
    reviewed=ask('S07V_THEMATIC_CHAPTER_COHERENCE_REVIEW',
       CHAPTER_COHERENCE_PROMPT,schema,
       {**subcontext,'previous_proposal':raw_chapters,
        'review_mode':'CONTENT_COHERENCE_AND_REPEATED_SUBJECT_FUSION'})
    try:
        validated_review=validate_chapters(reviewed,episodes,assets,facts,chapter_limit)
        reviewer.update(accepted=True,status='APPLIED_VALID_INDEPENDENT_REVIEW',
                        changed=validated_review!=normalized)
        normalized=validated_review
    except (ValueError,TypeError,KeyError) as exc:
        reviewer.update(status='REJECTED_INVALID_REVIEW',
                        error_type=type(exc).__name__)
    original_conflicts=thematic_coherence_conflicts(normalized,episodes)
    reviewer['mixed_theme_conflicts_before_correction']=original_conflicts
    if original_conflicts:
        alternate=ask('S07W_THEMATIC_COHERENCE_CORRECTION',
            CHAPTER_COHERENCE_REPAIR_PROMPT,schema,
            {**subcontext,
             'previous_proposal':{'chapters':[
                  {k:v for k,v in row.items() if k not in ('first_index','source_indices')}
                  for row in normalized]},
             'mixed_theme_chapters':original_conflicts})
        try:
            revised=validate_chapters(alternate,episodes,assets,facts,chapter_limit)
            remaining=thematic_coherence_conflicts(revised,episodes)
            before_memberships=[c['episode_ids'] for c in normalized]
            after_memberships=[c['episode_ids'] for c in revised]
            before_penalty=coherence_penalty(normalized,episodes)
            after_penalty=coherence_penalty(revised,episodes)
            reviewer['coherence_penalty_before']=before_penalty
            reviewer['coherence_penalty_after']=after_penalty
            if (after_penalty<before_penalty
                    and (before_memberships!=after_memberships
                         or any(c['incompatible_activity_groups'] for c in original_conflicts))):
                normalized=revised
                reviewer.update(status='APPLIED_COHERENT_REPLAN',
                                scoped_correction=True,
                                conflicts_remaining=remaining)
            else:
                reviewer.update(status='COHERENCE_REPLAN_DID_NOT_IMPROVE',
                                scoped_correction=False,
                                conflicts_remaining=original_conflicts)
        except (ValueError,TypeError,KeyError) as exc:
            reviewer.update(status='COHERENCE_REPLAN_INVALID',
                            error_type=type(exc).__name__,
                            conflicts_remaining=original_conflicts)
    wire=build_wire(normalized,assets,facts)
    return wire,{'version':VERSION,'independent_episodes':grounded,
       'chapter_grouping':normalized,'source_count':n,
       'time_basis':'IMPORT_SEQUENCE_ONLY','repairs':repairs,
       'semantic_coherence_review':reviewer,
       'noncontiguous_theme_fusion_enabled':True,
       'unassigned_verified_facts':len(set(facts)-
         {fid for c in wire['chapters'] for fid in c['fact_ids']})}
