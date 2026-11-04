"""Fact-grounded Chapter editorial actions, not an in-cloud LLM-as-Judge.

A source-grounded *candidate action* teaches the Chapter generator to consider:
- MERGE_REVIEW: separate chapters describe the same specific experience;
- MOVE_REVIEW: an episode's concrete subject belongs more naturally in
  another chapter than its current one;
- MIXED_THEME_REVIEW: multiple separately evidenced subexperiences do not
  share a clear Chapter subject;
- RETAIN: strong visual subjects survive the limited chapter/gallery budget.

These are hypotheses and edit suggestions, never automated ownership changes
or new visual facts. They are evaluated by existing generation S07U/V/W,
not by a new final-quality LLM Judge. True final quality is evaluated by the
external user-requested ChatGPT after full published frames are available.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import log
from typing import Mapping

from .scenelet_builder import tokens

VERSION='FACT_GROUNDED_EDITORIAL_DECISION_ACTIONS_V01'
# Generic camera language, scene descriptions and observation boilerplate.
# Deliberately contains NO geographic names or domain-specific landmarks.
_BOILERPLATE={
    '画面','视频','镜头','可见','显示','出现','附近','正在','可以','有人',
    '其中','前方','后方','背景','前景','周围','一些','多个','一名',
    '这是','一个','地面','道路','路边','天空','人群','情况',
    'view','scene','camera','image','photo','people','walking',
    'shows','showing','visible','there','some','with','near','and',
    'around','area','from','the','this','these','them','several'
}
# Incompatible activities only ask for a reconsideration. E.g. a market
# *inside* a garden may genuinely be one Chapter; photos must decide.
_CROSS_ACTIVITY=(
    (frozenset({'MARKET_SHOPPING'}),frozenset({'GARDEN','PARK_LEISURE'})),
    (frozenset({'MARKET_SHOPPING'}),frozenset({'FISHING','FLY_FISHING','KAYAK_FISHING'})),
    (frozenset({'COOKING'}),frozenset({'GARDEN','PARK_LEISURE'})),
)


def _distinctive(text:str)->set[str]:
    raw=str(text or '').casefold()
    terms=tokens(raw)
    return {s for s in terms if len(s)>=2 and s not in _BOILERPLATE
            and not any(k in s for k in ('画面','镜头','视频'))}


def episode_cards(episodes, *, limit=8):
    """Keep concrete episode IDs and verified F references, not hidden CoT."""
    if not 1<=limit<=24:
        raise ValueError('Invalid evidence-card limit')
    cards=[]
    for e in episodes:
        candidates=list(e.get('representative_verified_facts',()))
        ranked=sorted(candidates,key=lambda r:(
            -len(_distinctive(r.get('text',''))),
            r.get('source_index',0),r.get('fact_id','')))
        seen=set()
        real=[]
        for f in ranked:
            fid=f.get('fact_id')
            if not fid or fid in seen:
                continue
            seen.add(fid)
            real.append({'fact_id':fid,'source_index':f.get('source_index'),
                         'quote':str(f.get('text',''))[:175]})
            if len(real)>=limit:break
        cards.append({'episode_id':e['episode_id'],
            'theme':e['theme'],'experience_kind':e['experience_kind'],
            'source_interval':[e['start_index'],e['end_index']],
            'source_asset_count':e['end_index']-e['start_index']+1,
            'verified_fact_count':e.get('fact_count'),
            'real_visual_evidence':real,
            'facts_are_grounded':True})
    return cards


def _concrete_named_pairs(text):
    """Literal named subject phrases: advisory only, never identity proof."""
    import re
    groups=re.findall(r'(?<![a-z])(?:[A-Z][a-z]{2,}[ -]+){1,4}[A-Z][a-z]{2,}',str(text))
    names=set()
    ignored={'Return','View','Waterfront','Area','Walking','Scene',
             'Local','Chapter','Visit','Historic','Exploration'}
    for group in groups:
        terms=group.replace('-',' ').split()
        for i in range(len(terms)-1):
            pair=terms[i:i+2]
            if not any(t in ignored for t in pair):
                names.add(' '.join(pair).casefold())
    return names


def action_hints(grouping, episodes, *, max_actions=10):
    """Suggest bounded editing actions, with real Episode/F evidence.

    The editor may leave the proposal unchanged. We never move a source,
    assert a cross-time identity, or infer that different locations must be
    different Chapters. Textual similarity is *weak* evidence, not ground truth.
    """
    if max_actions<0 or max_actions>30:
        raise ValueError('Invalid action limit')
    if not grouping or not episodes:
        return {'version':VERSION,'actions':[],
                'status':'NO_GROUNDED_EPISODES'}
    cards={e['episode_id']:e for e in episode_cards(episodes)}
    assigned={}
    for pos,g in enumerate(grouping):
        for eid in g['episode_ids']:
            if eid in assigned or eid not in cards:
                raise ValueError('EPISODE_OWNERSHIP_IS_NOT_VALID_FOR_EDIT_HINTS')
            assigned[eid]=pos
    if set(assigned)!=set(cards):
        raise ValueError('MISSING_EPISODE_IN_EDIT_HINTS')
    topics={eid:_distinctive(e['theme']+' '+' '.join(
        x['quote'] for x in e['real_visual_evidence'])) for eid,e in cards.items()}
    named={eid:_concrete_named_pairs(e['theme']+' '+' '.join(
        x['quote'] for x in e['real_visual_evidence'])) for eid,e in cards.items()}
    # Term IDF over *episodes*, not entire day's 1fps observations, so a
    # crowded general street word does not dominate rarer concrete subjects.
    df=Counter(term for subject in topics.values() for term in subject)
    n=len(topics)
    weights={term:log((n+1)/(1+count))+1 for term,count in df.items()}
    def overlap(a,b):
        intersection=a&b
        if len(intersection)<2:
            return 0.,[]
        common=sorted(intersection,key=lambda word:(-weights.get(word,0.),word))
        shared_weight=sum(weights.get(w,0.) for w in intersection)
        total=sum(weights.get(w,0.) for w in (a|b))
        return round(shared_weight/max(total,1.),4),common[:8]
    rows=[]
    for index,ch in enumerate(grouping):
        refs=[cards[eid] for eid in ch['episode_ids']]
        kinds={r['experience_kind'] for r in refs}
        allfacts=sorted({v['fact_id'] for r in refs
                         for v in r['real_visual_evidence']})
        for left,right in _CROSS_ACTIVITY:
            if kinds&left and kinds&right:
                rows.append({'action':'MIXED_THEME_REVIEW',
                  'chapter_index':index,'chapter_title':ch['title'],
                  'episode_ids':[r['episode_id'] for r in refs],
                  'supporting_fact_ids':allfacts[:12],
                  'evidence_scope':'EXPLICIT_DIFFERENT_EXPERIENCE_KINDS',
                  'editorial_instruction':'比较这些已验证活动是否有共同的实际经历主题；不能只因为同一天或同街区就硬合并。',
                  'automatically_reassign':False})
        # Do not label an Episode an "outlier" simply because it adds a
        # different valuable subject to a coherent multi-scene citywalk.
        # Suggest a MOVE only when another *existing* Chapter has stronger
        # concrete visual evidence and shares a specific named subject.
        if len(refs)>=2:
            for e in refs:
                eid=e['episode_id']
                parent_peers=[x['episode_id'] for x in refs if x['episode_id']!=eid]
                parent_subjects=set().union(*(named[x] for x in parent_peers))
                # For repeated named places keep the initial membership:
                # a return/another viewpoint does NOT force a second chapter.
                if named[eid]&parent_subjects:
                    continue
                parent_topics=set().union(*(topics[x] for x in parent_peers))
                parent_sim,_=overlap(topics[eid],parent_topics)
                ranked_targets=[]
                for j,other in enumerate(grouping):
                    if j==index:continue
                    other_eids=other['episode_ids']
                    concrete=named[eid]&set().union(*(named[x] for x in other_eids))
                    if not concrete:continue
                    other_topics=set().union(*(topics[x] for x in other_eids))
                    score,shared=overlap(topics[eid],other_topics)
                    if score>max(.08,parent_sim+.03) or len(concrete)>=2:
                        ranked_targets.append((score,j,sorted(concrete),shared))
                if not ranked_targets:
                    continue
                score,to_index,names_shared,shared=max(ranked_targets)
                rows.append({'action':'OUTLIER_EPISODE_REVIEW',
                    'chapter_index':index,'suggested_existing_chapter_index':to_index,
                    'chapter_title':ch['title'],
                    'episode_ids':[eid],
                    'supporting_fact_ids':[v['fact_id']
                        for v in e['real_visual_evidence']],
                    'strong_shared_named_subjects':names_shared,
                    'shared_distinctive_terms':shared,
                    'topic_affinity_current':parent_sim,
                    'topic_affinity_other':score,
                    'evidence_scope':'BETTER_EXISTING_CHAPTER_WITH_NAMED_SUBJECT_SUPPORT',
                    'editorial_instruction':'新候选只说明可以核查移动到已有章节；必须看具体来源证据。'
                       '同地点重现可以融合，不能根据相隔时间或泛泛活动标签移动。',
                    'automatically_reassign':False})
    # Strongest same-topic proposals across separate Chapters. Do not
    # infer that a recurring landmark warrants an independent Chapter.
    for i,a in enumerate(grouping):
        for j in range(i+1,len(grouping)):
            b=grouping[j]
            kinds_a={cards[e]['experience_kind'] for e in a['episode_ids']}
            kinds_b={cards[e]['experience_kind'] for e in b['episode_ids']}
            # Only invoke advisory if source observations provide *some*
            # shared activity and several non-generic visual tokens.
            if not kinds_a&kinds_b:
                continue
            ta=set().union(*(topics[e] for e in a['episode_ids']))
            tb=set().union(*(topics[e] for e in b['episode_ids']))
            similarity,shared=overlap(ta,tb)
            if similarity<.15 or len(shared)<3:
                continue
            fids=[q['fact_id'] for eid in (a['episode_ids']+b['episode_ids'])
                  for q in cards[eid]['real_visual_evidence']]
            rows.append({'action':'SAME_THEME_CROSS_CHAPTER_MERGE_REVIEW',
               'chapter_indices':[i,j],
               'chapter_titles':[a['title'],b['title']],
               'episode_ids':a['episode_ids']+b['episode_ids'],
               'supporting_fact_ids':list(dict.fromkeys(fids))[:14],
               'shared_visual_terms':shared,
               'topic_overlap_proxy_not_identity':similarity,
               'editorial_instruction':'从视觉主体与实际活动判断是否属于同一经历主题；同地点重现可以合并，不因为时钟或来源距离强制拆章。',
               'automatically_merge':False})
    # Action order is deterministic and scoped. Only source/F IDs are allowed;
    # there is no model-generated fact, user location or timestamp here.
    priority={'MIXED_THEME_REVIEW':0,
              'SAME_THEME_CROSS_CHAPTER_MERGE_REVIEW':1,
              'OUTLIER_EPISODE_REVIEW':2}
    rows.sort(key=lambda r:(priority.get(r['action'],9),
                            r.get('chapter_index',r.get('chapter_indices',[0])[0]),
                            r['episode_ids']))
    return {'version':VERSION,'actions':rows[:max_actions],
        'action_count_total':len(rows),
        'status':'ADVISORY_EVIDENCE_BOUND_NO_AUTOMATIC_EDIT',
        'time_policy':'TEMPORAL_DISTANCE_ALONE_NEVER_SPLITS_OR_MERGES',
        'fact_policy':'SOURCE_VERIFIED_ONLY'}


def budgeted_edit_recipe(grouping, episodes, *, chapter_limit=5):
    """Suggest a source-grounded free-one-slot merge plus split, never enact it.

    Typical error: one group contains both a substantial shopping experience
    and a garden/park experience while the UI chapter budget is full. An
    editor first asks whether two other naturally related groups could share a
    Chapter, then represents the dissimilar long experiences distinctly.

    This is a structural *candidate*, not a new LLM judge. Existing S07W
    still owns title writing, anchors, and final validity; the compiler only
    accepts actual already-reviewed F/E identities.
    """
    if chapter_limit<1 or not episodes or not grouping:
        return {'status':'NO_ACTION','candidate_episode_layouts':[]}
    byid={e['episode_id']:e for e in episodes}
    kinds_nature={'GARDEN','PARK_LEISURE','NATURE_WALK'}
    kinds_other={'MARKET_SHOPPING','CITYWALK','MUSEUM','DINING','SIGHTSEEING'}
    mixed=[]
    for pos,ch in enumerate(grouping):
        rows=[byid[e] for e in ch['episode_ids']]
        nature=[e['episode_id'] for e in rows if e['experience_kind'] in kinds_nature]
        other=[e['episode_id'] for e in rows if e['experience_kind'] in kinds_other]
        if nature and other and ({byid[e]['experience_kind'] for e in other}&
                                  {'MARKET_SHOPPING','DINING'}):
            mixed.append((pos,nature,other))
    if len(mixed)!=1 or len(grouping)<3 or len(grouping)>chapter_limit:
        return {'status':'NO_CLEAR_SINGLE_MIXED_GROUP','candidate_episode_layouts':[]}
    mixed_id,nature,other=mixed[0]
    # Only suggest a sibling merge if the pair shares concrete topical words.
    # "CITYWALK" alone, index adjacency and exact chapter count are not
    # sufficient reasons to join unrelated experiences.
    excluded={'walk','walking','citywalk','chapter','scene','area','view',
              'exploration','visit','historic','city','precinct','district',
              'experience','street','garden','market','the','with','and'}
    pair_options=[]
    for i,a in enumerate(grouping):
        if i==mixed_id:continue
        for j in range(i+1,len(grouping)):
            if j==mixed_id:continue
            ta=_distinctive(a['title'])-excluded
            tb=_distinctive(grouping[j]['title'])-excluded
            common={t for t in ta&tb if len(t)>=4}
            if not common:
                continue
            ai={byid[e]['experience_kind'] for e in a['episode_ids']}
            bi={byid[e]['experience_kind'] for e in grouping[j]['episode_ids']}
            # A related waterfront nature walk and maritime district is
            # possible; garden versus shopping still needs reinspection.
            broad={'CITYWALK','NATURE_WALK','OUTDOOR_SCENERY','MUSEUM'}
            if not ((ai&bi) or (ai<=broad and bi<=broad)):
                continue
            strength=len(common)+.15/(1+abs(i-j))
            pair_options.append((strength,i,j,sorted(common)))
    if not pair_options:
        return {'status':'NO_SAFE_THEMATIC_SIBLING_MERGE',
                'mixed_episode_ids':grouping[mixed_id]['episode_ids'],
                'candidate_episode_layouts':[]}
    _,i,j,shared=max(pair_options,key=lambda x:(x[0],-x[1],-x[2]))
    proposal=[]
    for k,ch in enumerate(grouping):
        if k==i:
            proposal.append({'episode_ids':list(ch['episode_ids'])+
                list(grouping[j]['episode_ids']),
                'origin_chapter_indices':[i,j],
                'action':'MERGE_RELATED_EXISTING_THEMES',
                'shared_visual_terms_not_identity_proof':shared})
        elif k==j:
            continue
        elif k==mixed_id:
            proposal.append({'episode_ids':other,'origin_chapter_indices':[mixed_id],
                'action':'RETAIN_NON_NATURE_EXPERIENCES_WITH_THEIR_OWN_TOPIC'})
            proposal.append({'episode_ids':nature,'origin_chapter_indices':[mixed_id],
                'action':'PROTECT_DISTINCT_NATURE_EXPERIENCES'})
        else:
            proposal.append({'episode_ids':list(ch['episode_ids']),
                'origin_chapter_indices':[k],'action':'PRESERVE_OTHER_GROUP'})
    expected=[e['episode_id'] for e in episodes]
    flat=[eid for p in proposal for eid in p['episode_ids']]
    if len(proposal)>chapter_limit or len(flat)!=len(expected) or set(flat)!=set(expected):
        raise ValueError('EDIT_RECIPE_MUST_PRESERVE_EVERY_REAL_EPISODE')
    return {'status':'ADVISORY_LAYOUT_WITH_BUDGETED_MERGE_AND_SPLIT',
        'candidate_episode_layouts':proposal,'source_chapter_index_to_split':mixed_id,
        'thematic_merge_pair_indices':[i,j],
        'shared_topic_terms':shared,
        'important':'This is not an automatic edit or verified same-place identity; S07W must corroborate all grouping and valid fact anchors.'}
