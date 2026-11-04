"""Global Chapter proposals and auditable, bounded structure replan contracts.

This is evidence-oriented planning, not a classifier of scene names. One
Scenelet may be a Moment; many scenelets may belong to one Chapter. Neither
full-day duration nor the input's activity label imposes a desired count.
"""
from collections import defaultdict
from copy import deepcopy
from hashlib import sha256

VERSION='CHAPTER_GLOBAL_PLAN_V01'
MAX_CHAPTERS=8
REPLAN_SCHEMA_VERSION='DRAFT_MERGE_DISPOSITION_V01'
DISPOSITION_PROMPT = '''S07只是候选，不是最终真值。请检查S08后丢失的章节焦点事实，并基于本轮真实图片核验后仍成立的内容，为每个候选返回唯一去向。KEEP_MERGED必须指向已有章节且其事实确实属于同一经历；KEEP_AS_MOMENT表示独立细节不足以单独成章但值得保留；RESTORE_CHAPTER需有足够事实支持完整独立经历；DROP_UNSUPPORTED需明确说明视觉事实虽成立但没有独立记忆价值；REVIEW_REQUIRED表示证据不足或编辑冲突。只使用提供的已核验fact_ids，不要把同类活动自动合并，也不要把每处景物变化拆成新章。你是在提供待核验的编辑决定，而非真值。'''
ACTIONS=('KEEP_MERGED','KEEP_AS_MOMENT','RESTORE_CHAPTER','DROP_UNSUPPORTED','REVIEW_REQUIRED')


def boundary_strength(edge):
    reason=edge.get('reason')
    sim=edge.get('similarities',{})
    if reason=='ACTIVITY_AND_VISUAL_NOVELTY':
        return 2.4
    if reason=='SETTING_AND_VISUAL_NOVELTY':
        # The changed place alone is not enough; facts must support a
        # distinct experience as checked by the later model.
        return 1.5
    if reason=='DISTINCT_VISUAL_SUBJECTS':
        return 1.25
    if reason=='VERIFIED_TIME_GAP':
        return .65
    return 0.


def propose_chapters(scene_map, *, chapter_limit=MAX_CHAPTERS):
    """Coarse time-ordered scenelet coverage with unconstrained Chapter count.

    A different-looking view is only a *potential* Chapter boundary. Scores
    remain advisory. The editorial VLM must judge independent experiences
    with fact support; the plan never invents activities, destinations or copy.
    """
    if type(chapter_limit) is not int or not 1<=chapter_limit<=MAX_CHAPTERS:
        raise ValueError('Chapter limit out of range')
    scenes=scene_map.get('scenelets',[])
    if not scenes:
        return {'version':VERSION,'chapter_candidates':[],
            'scenelet_count':0,'recommended_count':0,'time_basis':scene_map.get('time_basis')}
    index={aid:i for i,scene in enumerate(scenes) for aid in scene['asset_ids']}
    choices=[]
    for edge in scene_map.get('boundaries',[]):
        left,right=edge.get('left_asset_id'),edge.get('right_asset_id')
        if left not in index or right not in index or index[left]==index[right]:
            continue
        i=index[right]
        if i<1:continue
        # One boundary of a scenelet pair; no benefit from several source
        # asset edges inside the same Scenelet.
        score=boundary_strength(edge)
        if score>=1.2 and scenes[i-1]['fact_ids'] and scenes[i]['fact_ids']:
            choices.append((score,i,edge['reason']))
    # Pairwise scores are often tied across many small scenelets. Picking
    # the earliest ties created four tiny intro Chapters and one enormous
    # remainder. Select salient boundaries with GLOBAL spread, not raw
    # source index, while retaining evidence-based candidate eligibility.
    # A fully tied set has no local evidence favoring early cut points.
    # Use balanced quantile targets *only among already eligible boundaries*.
    # This is an advisory coverage safeguard, not an imposed Chapter count:
    # homogeneous scenes produce no eligible boundaries and remain one chapter.
    unique = {i: (score,i,reason) for score,i,reason in choices}
    pending = list(unique.values())
    if pending and len({score for score,_,_ in pending}) == 1:
        k = min(chapter_limit-1,len(pending))
        strongest=[]
        for slot in range(1,k+1):
            target=len(scenes)*slot/(k+1)
            winner=min(pending,key=lambda x:(abs(x[1]-target),-x[0],x[1]))
            strongest.append(winner)
            pending.remove(winner)
    else:
        strongest=[]
        while pending and len(strongest)<chapter_limit-1:
            boundaries=[0,*sorted(i for _,i,_ in strongest),len(scenes)]
            def candidate_priority(option):
                score,i,_=option
                left=max(x for x in boundaries if x<i)
                right=min(x for x in boundaries if x>i)
                ratio=min(i-left,right-i)/max(1,right-left)
                return (score*(.9+ratio),min(i-left,right-i),-i)
            winner=max(pending,key=candidate_priority)
            strongest.append(winner)
            pending.remove(winner)
    splits={i:reason for _,i,reason in strongest}
    groups=[]
    start=0
    for i in sorted(splits):
        groups.append((start,i,splits[i]))
        start=i
    groups.append((start,len(scenes),None))
    proposals=[]
    for order,(left,right,reason) in enumerate(groups,1):
        members=scenes[left:right]
        aids=list(dict.fromkeys(aid for x in members for aid in x['asset_ids']))
        fids=list(dict.fromkeys(fid for x in members for fid in x['fact_ids']))
        sid='CP'+sha256('|'.join(x['scenelet_id'] for x in members).encode()).hexdigest()[:12]
        # Coverage exemplars must include the middle and tail of a long
        # proposal. The old fids[:3] silently erased distant experiences
        # from the model's high-salience summary.
        anchor_indices=[0,len(fids)//2,len(fids)-1] if fids else []
        anchors=list(dict.fromkeys(fids[i] for i in anchor_indices))
        proposals.append({'proposal_id':sid,
            'order':order,'scenelet_ids':[x['scenelet_id'] for x in members],
            'asset_ids':aids,'fact_ids':fids,
            'boundary_from_previous':reason,
            'anchor_fact_ids':anchors,
            'evidence_scenelet_count':sum(bool(x['fact_ids']) for x in members),
            'status':'PROPOSAL_NEEDS_SEMANTIC_EDITOR_REVIEW'})
    assert {aid for c in proposals for aid in c['asset_ids']} == {
        aid for s in scenes for aid in s['asset_ids']}
    return {'version':VERSION,
        'time_basis':scene_map.get('time_basis','IMPORT_SEQUENCE_ONLY'),
        'scenelet_count':len(scenes),'recommended_count':len(proposals),
        'chapter_candidates':proposals,'candidate_boundaries':[
            {'before_scenelet':scenes[i]['scenelet_id'],'reason':reason,'score':score}
            for score,i,reason in strongest],
        'notice':'Advisory global coverage plan, not a mandatory Chapter count or proof of independent experience.'}


def disposition_schema(missing):
    """Strict model response; no free-form IDs or invented source references."""
    ids=[r['draft_chapter_id'] for r in missing]
    return {'type':'object','additionalProperties':False,'required':['items'],
        'properties':{'items':{'type':'array',
            'minItems':len(ids),'maxItems':len(ids),
            'items':{'type':'object','additionalProperties':False,
                'required':['draft_chapter_id','action','target_chapter_id',
                            'supporting_fact_ids','reason'],
                'properties':{
                    'draft_chapter_id':{'enum':ids},
                    'action':{'enum':list(ACTIONS)},
                    'target_chapter_id':{'type':['string','null']},
                    'supporting_fact_ids':{'type':'array','items':{'type':'string'},
                                           'uniqueItems':True},
                    'reason':{'type':'string','minLength':8}}}}}}


def check_dispositions(output,missing,verified_facts,reviewed):
    """Reject invented facts/targets or unreviewed 'RESTORE' claims.

    A model judgement is evidence-weighted but not objective truth.
    A verified topic can still reasonably be folded into another Chapter.
    """
    if not isinstance(output,dict) or set(output)!={'items'} or not isinstance(output['items'],list):
        raise ValueError('Invalid disposition format')
    rows=output['items']
    expected={r['draft_chapter_id']:r for r in missing}
    if len(rows)!=len(expected):
        raise ValueError('Missing or duplicated draft dispositions')
    valid_targets={r['id'] for r in reviewed.get('chapters',[]) if isinstance(r,dict)}
    verified=set(verified_facts)
    decisions={}
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'draft_chapter_id','action','target_chapter_id','supporting_fact_ids','reason'}:
            raise ValueError('Invalid disposition item')
        key=row['draft_chapter_id']
        if key not in expected or key in decisions:
            raise ValueError('Unknown or duplicate draft chapter')
        action=row['action']
        if action not in ACTIONS:
            raise ValueError('Invalid disposition action')
        facts=row['supporting_fact_ids']
        source=set(expected[key]['draft_fact_ids'])
        if (not isinstance(facts,list) or not facts or len(set(facts))!=len(facts)
                or not set(facts)<=source or not set(facts)<=verified):
            raise ValueError('Disposition not based on visual-reviewed facts')
        if (not isinstance(row['reason'],str) or len(row['reason'].strip())<8):
            raise ValueError('Disposition requires a concrete reason')
        target=row['target_chapter_id']
        if action=='KEEP_MERGED':
            if target not in valid_targets:
                raise ValueError('Merged target must be real Chapter')
        elif target is not None:
            raise ValueError('Non-merged disposition cannot cite a target Chapter')
        decisions[key]=deepcopy(row)
    return {'version':REPLAN_SCHEMA_VERSION,'decisions':list(decisions.values()),
        'replan_required':any(r['action'] in ('KEEP_MERGED','KEEP_AS_MOMENT','RESTORE_CHAPTER','REVIEW_REQUIRED')
                              for r in decisions.values()),
        'moment_downgrades':[r['draft_chapter_id'] for r in decisions.values()
                             if r['action']=='KEEP_AS_MOMENT'],
        'evidence_gate_passed':True}


def merge_replan_review(original,proposed,validator,*,allow_no_change=False):
    """Install a replanned structure only if it passes the existing compiler.

    No synthetic/fabricated Chapter creation. When the model fails to return
    a valid plan, retain the original structure and mark the attempt blocked.
    """
    if not isinstance(proposed,dict):
        return original,{'status':'REPLAN_BLOCKED','reason':'MODEL_OUTPUT_INVALID'}
    try:
        compiled=validator(proposed)
        if any(compiled[2]):
            return original,{'status':'REPLAN_BLOCKED','reason':'STRUCTURE_CONTRACT_REJECTED',
                'rejections':compiled[2]}
        if (not allow_no_change and proposed.get('chapters',[])==original.get('chapters',[])
                and proposed.get('moments',[])==original.get('moments',[])):
            return original,{'status':'REPLAN_BLOCKED','reason':'NO_CHANGES_TO_CONSIDER'}
        return proposed,{'status':'REPLAN_APPLIED','chapters':len(compiled[0]),
            'moments':len(compiled[1])}
    except (KeyError,ValueError,TypeError) as exc:
        return original,{'status':'REPLAN_BLOCKED','reason':type(exc).__name__}
