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

VERSION = "GLOBAL_THEMATIC_EPISODES_AND_CHAPTERS_V03"
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

按如下“可复核编辑决策顺序”直接形成可发布结构，不要输出私有思维过程：
①对每个Episode先写下具体可见的独特活动、人物或主体，不把所有WALKING概括成相同主题。
②比较同主题Episode，即使时间不连续也可归一章；不同活动即使相邻也不必一章。
③检查整个Day是否漏掉值得记住的地点/作品/事件；如果Chapter数量有限，将次要但真实的
  小经历收进相关Chapter的Episode，不得直接删掉来源事实。
④比较相似的两章是否重复；比较每章内部是否存在错放的Episode。
⑤以本章多个事实共同定义主题，1..4条anchor_fact_ids必须都来自本章真实已核验图片。
⑥最终章数是内容选择后的结果，不是先凑满5章。仅输出严格JSON，不报告未经证实的推理步骤。
返回严格JSON。"""

CHAPTER_REPAIR_PROMPT = """此前Chapter方案遗漏/重复分配了Episode，或者选了
不属于本章Episode的视觉事实锚点。只修改错误项，每个Episode必须且只能有一个父章；
允许同一地点非连续地融合到同一个Chapter。不得创造事实ID、地点或素材，返回合法JSON。"""

CHAPTER_COHERENCE_REPAIR_PROMPT = """你正在对已提出的日记Chapter作一次有证据的全局编辑修改，
不是第二个独立的LLM-as-a-Judge；你必须完成可以用于正式生成的合法Chapter结构。

输入的editorial_edit_actions只代表由已验证Episode/F ID计算得到的候选编辑动作，
不代表这些文字相似的主体已经被证明相同。请逐项根据实际视觉事实考虑：
- MIXED_THEME_REVIEW：如果两种独立活动确实难以在同一记忆主题下自然表达，把错误归属的
  Episode移动到已有更相关章节；若真正发生一次自然混合活动，可以保留而不强制拆分。
- SAME_THEME_CROSS_CHAPTER_MERGE_REVIEW：如果两章其实在表达同一经历，融合成一个Chapter；
  但同一个普通建筑类别、同样都是WALKING并不证明是同一地点，更不能仅凭时间强制合并。
- OUTLIER_EPISODE_REVIEW：检查被放入错误主题的具体视觉经历，移到真实主题相关的Chapter。
优先对现有Chapter合并、调整Episode归属，必要时减少章数。不为填满5章硬拆，
也不能因两个场景时间相邻就强合。保持重要具体作品、建筑、动物、购物、自然、
运动等视觉内容被合理表达，短暂的独特记忆可以作为本章Episode而非单独开章。
只改有证据的地方；允许原方案已经合理时保持不变。
只能使用真实Episode ID和属于其所有权的已核验F ID。严禁猜测拍摄地点路线、人物
关系、真实经过时间、购买成功、返回情绪。返回完整合法JSON。"""


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
    from . import chapter_editorial_decision_flow
    advice=chapter_editorial_decision_flow.action_hints(grouping,episodes,max_actions=20)
    actual_moves={}
    for row in advice['actions']:
        if row['action']=='OUTLIER_EPISODE_REVIEW':
            actual_moves.setdefault(row['chapter_index'],[]).append({
                'episode_id':row['episode_ids'][0],
                'existing_target_chapter_index':row['suggested_existing_chapter_index'],
                'strong_shared_named_subjects':row['strong_shared_named_subjects'],
                'reason':'BETTER_EXISTING_CHAPTER_WITH_SOURCE_NAMED_SUBJECT'})
    conflicts=[]
    for index,c in enumerate(grouping):
        rows=[byid[e] for e in c['episode_ids']]
        kinds={e['experience_kind'] for e in rows}
        triggers=[{'left':sorted(a),'right':sorted(b)}
             for a,b in incompatible if kinds&a and kinds&b]
        lexical_outliers=actual_moves.get(index,[])
        if triggers or lexical_outliers:
            conflicts.append({'chapter_index':index+1,'chapter_theme':c['title'],
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


def _episode_facts(episodes, assets, facts, observations, visual_memory=None):
    """Full episode coverage plus diverse, globally distinctive verified facts.

    R5_27 originally sampled up to 16 evenly spaced observations and 4 high
    *frequency* lexical rows. That could miss a brief but valuable object
    (artwork, building, activity) even when S04 had already verified it.
    The global-memory anchor list adds high-value proof without creating a
    geographic or domain-specific rule. Every F is still in candidate_fact_ids.
    """
    order={aid:a['sequence_index'] for aid,a in assets.items()}
    globally_protected={r['fact_id'] for r in
        (visual_memory or {}).get('priority_anchors',[]) if r.get('fact_id') in facts}
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
        count=min(12,len(candidates))
        positions={round(i*(len(candidates)-1)/(count-1)) for i in range(count)} if count>1 else {0}
        chosen=[candidates[i] for i in sorted(positions)]
        excerpt=[{'fact_id':fid,'text':f['text'][:170],
                  'source_index':order[f['asset_id']]}
                 for fid,f in chosen]
        protected=[(fid,f) for fid,f in candidates if fid in globally_protected]
        protected.sort(key=lambda pair:(order[pair[1]['asset_id']],pair[0]))
        chosen_fact_ids={z['fact_id'] for z in excerpt}
        for fid,f in protected[:8]:
            if fid not in chosen_fact_ids:
                excerpt.append({'fact_id':fid,'text':f['text'][:170],
                    'source_index':order[f['asset_id']]})
                chosen_fact_ids.add(fid)
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
          'globally_protected_fact_ids':[fid for fid,_ in protected[:8]],
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


def normalize_only_excess_visual_anchors(proposal, episodes, assets, facts,
                                         chapter_limit):
    """Bounded formatting recovery: cannot change any Episode or visual fact.

    A valid proposal can emit five verified focus facts when the public schema
    permits four. Preserve Episode ownership and remove only surplus refs;
    malformed identity, provenance or other schema violations fail closed.
    """
    if not isinstance(proposal,dict) or set(proposal)!={'chapters'} or not isinstance(proposal['chapters'],list):
        raise ValueError('NOT_AN_EXCESS_ANCHOR_ONLY_RESPONSE')
    updated=deepcopy(proposal)
    schema=chapter_schema([e['episode_id'] for e in episodes],
                          list(facts),chapter_limit)
    order={aid:a['sequence_index'] for aid,a in assets.items()}
    corrections=[]
    for row in updated['chapters']:
        if not isinstance(row,dict) or not isinstance(row.get('anchor_fact_ids'),list):
            raise ValueError('NOT_AN_EXCESS_ANCHOR_ONLY_RESPONSE')
        anchors=row['anchor_fact_ids']
        if len(anchors)<=4:continue
        if len(anchors)>12 or len(set(anchors))!=len(anchors):
            raise ValueError('INVALID_EXCESS_ANCHOR_IDENTITIES')
        owned={index for e in episodes if e['episode_id'] in row.get('episode_ids',[])
               for index in range(e['start_index'],e['end_index']+1)}
        if not owned or any(fid not in facts or
                 facts[fid].get('visual_reviewed') is not True or
                 facts[fid].get('asset_id') not in order or
                 order[facts[fid]['asset_id']] not in owned for fid in anchors):
            raise ValueError('INVALID_EXCESS_ANCHOR_OWNERSHIP')
        ranked=sorted(anchors,key=lambda fid:(order[facts[fid]['asset_id']],fid))
        slots=sorted({round(i*(len(ranked)-1)/3) for i in range(4)})
        if len(slots)!=4:raise ValueError('ANCHOR_SPREAD_UNAVAILABLE')
        selected=[ranked[i] for i in slots]
        row['anchor_fact_ids']=selected
        corrections.append({'chapter_title':row['title'],
            'original_verified_anchor_ids':anchors,
            'kept_verified_anchor_ids':selected,
            'reason':'SCHEMA_MAX4_ONLY_NO_EPISODES_OR_FACTS_REMOVED'})
    if not corrections or not _valid(schema,updated):
        raise ValueError('NOT_AN_EXCESS_ANCHOR_ONLY_RESPONSE')
    return updated,corrections


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
    grounded=_episode_facts(episodes,assets,facts,observations,
                            visual_memory=visual_memory)
    from . import chapter_editorial_decision_flow
    evidence_cards=chapter_editorial_decision_flow.episode_cards(grounded,limit=9)
    ids=sorted(facts)
    schema=chapter_schema([e['episode_id'] for e in episodes],ids,chapter_limit)
    subcontext={'policy':VERSION,'chapter_limit':chapter_limit,
         'episodes':grounded,'allowed_fact_ids':ids,
         'episode_editorial_evidence_cards':evidence_cards,
         'global_memory':compact,
         'do_not_split_repeated_location':True,
         'editorial_process':['RECOVER_WORTH_REMEMBERING_EXPERIENCES',
                              'FUSE_SAME_REAL_EXPERIENCE_ACROSS_SOURCE_SPANS',
                              'REMOVE_UNRELATED_EPISODE_MISASSIGNMENTS',
                              'KEEP_CHAPTER_SUBJECT_AND_FACT_ANCHORS_ALIGNED',
                              'PRESERVE_IMPORTANT_EXPERIENCES_WITHIN_CHAPTER_BUDGET'],
         'time_basis':'IMPORT_SEQUENCE_ONLY'}
    raw_chapters=ask('S07U_THEMATIC_CHAPTER_FUSION',CHAPTER_PROMPT,schema,subcontext)
    try:
        if not _valid(schema,raw_chapters):
            amended,fixes=normalize_only_excess_visual_anchors(
                raw_chapters,episodes,assets,facts,chapter_limit)
            raw_chapters=amended
            repairs.append({'stage':'S07U_ANCHOR_CARDINALITY_ONLY',
                'reason':'PROVIDER_EMITTED_MORE_THAN_FOUR_VALID_FOCUS_FACTS',
                'items':fixes})
        normalized=validate_chapters(raw_chapters,episodes,assets,facts,chapter_limit)
    except (ValueError,TypeError,KeyError) as e:
        repairs.append({'stage':'S07U','reason':str(e)})
        raw_chapters=ask('S07U_THEMATIC_CHAPTER_REPAIR',CHAPTER_REPAIR_PROMPT,
             schema,{**subcontext,'invalid_proposal':raw_chapters,
                     'validation_error':str(e)})
        try:
            if not _valid(schema,raw_chapters):
                amended,fixes=normalize_only_excess_visual_anchors(
                    raw_chapters,episodes,assets,facts,chapter_limit)
                raw_chapters=amended
                repairs.append({'stage':'S07U_ANCHOR_CARDINALITY_ONLY_AFTER_MODEL_REPAIR',
                    'items':fixes})
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
        from . import chapter_editorial_decision_flow
        previous_actions=chapter_editorial_decision_flow.action_hints(
            normalized,grounded,max_actions=20)['actions']
        suggested_actions=chapter_editorial_decision_flow.action_hints(
            validated_review,grounded,max_actions=20)['actions']
        previous_penalty=coherence_penalty(normalized,episodes)
        proposed_penalty=coherence_penalty(validated_review,episodes)
        reviewer.update(previous_concrete_concerns=len(previous_actions),
                        candidate_concrete_concerns=len(suggested_actions),
                        previous_known_penalty=previous_penalty,
                        candidate_known_penalty=proposed_penalty)
        if (proposed_penalty<=previous_penalty
                and len(suggested_actions)<=len(previous_actions)):
            reviewer.update(accepted=True,status='APPLIED_VALID_GENERATION_REVISION',
                            changed=validated_review!=normalized)
            normalized=validated_review
        else:
            reviewer.update(accepted=False,status='RETAINED_SOURCE_GROUNDED_INITIAL',
                            changed=False)
    except (ValueError,TypeError,KeyError) as exc:
        reviewer.update(status='REJECTED_INVALID_REVIEW',
                        error_type=type(exc).__name__)
    original_conflicts=thematic_coherence_conflicts(normalized,episodes)
    edit_plan=chapter_editorial_decision_flow.action_hints(normalized,grounded,max_actions=8)
    reviewer['mixed_theme_conflicts_before_correction']=original_conflicts
    reviewer['evidence_grounded_editorial_actions_before']=edit_plan
    if original_conflicts or edit_plan['actions']:
        alternate=ask('S07W_THEMATIC_COHERENCE_CORRECTION',
            CHAPTER_COHERENCE_REPAIR_PROMPT,schema,
            {**subcontext,
             'previous_proposal':{'chapters':[
                  {k:v for k,v in row.items() if k not in ('first_index','source_indices')}
                  for row in normalized]},
             'mixed_theme_chapters':original_conflicts,
             'editorial_edit_actions':edit_plan['actions'],
             'budgeted_content_first_layout_candidate':
                chapter_editorial_decision_flow.budgeted_edit_recipe(
                    normalized,grounded,chapter_limit=chapter_limit),
             'instruction':'请按证据决定是否合并、移动或保留现有内容，而不是为增加章数而改。候选layout只是编辑建议，不能省略真实证据的核对。'})
        try:
            revised=validate_chapters(alternate,episodes,assets,facts,chapter_limit)
            remaining=thematic_coherence_conflicts(revised,episodes)
            revised_plan=chapter_editorial_decision_flow.action_hints(
                revised,grounded,max_actions=8)
            before_memberships=[c['episode_ids'] for c in normalized]
            after_memberships=[c['episode_ids'] for c in revised]
            before_penalty=coherence_penalty(normalized,episodes)
            after_penalty=coherence_penalty(revised,episodes)
            before_action_count=len(edit_plan['actions'])
            after_action_count=len(revised_plan['actions'])
            reviewer['coherence_penalty_before']=before_penalty
            reviewer['coherence_penalty_after']=after_penalty
            reviewer['candidate_edit_actions_before']=before_action_count
            reviewer['candidate_edit_actions_after']=after_action_count
            improved=(after_penalty < before_penalty or
                      (after_penalty <= before_penalty and
                       after_action_count < before_action_count))
            if (improved and
                    (before_memberships!=after_memberships
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
       'episode_evidence_cards':evidence_cards,
       'editorial_edit_policy':chapter_editorial_decision_flow.VERSION,
       'noncontiguous_theme_fusion_enabled':True,
       'unassigned_verified_facts':len(set(facts)-
         {fid for c in wire['chapters'] for fid in c['fact_ids']})}
