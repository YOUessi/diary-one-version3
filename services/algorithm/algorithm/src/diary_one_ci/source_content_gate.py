"""Source-content gate: a real lived scene is not a video-player outro.

Only an explicitly grounded, terminal promotional end card is excluded
automatically. Brand names, billboards, shop signs, public advertisements,
subtitle overlays and normal social-media screens *by themselves* NEVER
authorize deletion. Ambiguous examples stay in review, not silently erased.

Gate result contains original observed quote, frame references and asset IDs.
No media is modified or uploaded; original observations remain available in
the caller's audit. The gate never makes a new visual inference from filenames.
"""
from __future__ import annotations

from copy import deepcopy
import re

VERSION = 'SOURCE_CONTENT_CONTEXT_GATE_V01'

# Strong *structural* evidence that frames depict a video/post-production
# outro. Neither a geographic place nor an account/brand is special-cased.
_END_CARD = re.compile(
    r'\b(?:end\s*card|end\s*screen|outro\s*(?:screen|card)|'
    r'video\s*(?:ending|end)\s*(?:screen|card)|'
    r'end\s*of\s*video)\b|'
    r'片尾(?:推广|宣传|广告|页|画面|界面|卡片)|'
    r'视频结尾(?:的)?(?:推广|宣传|广告|页面|画面|界面|卡片)|'
    r'结尾(?:的)?推广界面',
    re.I,
)
_CALL_TO_ACTION = [
    re.compile(s, re.I) for s in (
        r'(?<![a-z])subscribe(?![a-z])|订阅(?:频道|账号|我|我们)?',
        r'(?<![a-z])keep\s*watching(?![a-z])|继续观看|继续看',
        r'(?<![a-z])follow\s*(?:us|me|our)(?![a-z])|关注(?:我们|账号|频道)',
        r'(?<![a-z])(?:instagram|facebook|youtube)(?![a-z])|社交(?:媒体|账号|平台)',
        r'(?<![a-z])watch\s*next(?![a-z])|观看下一(?:个|条|集)',
    )
]

def evaluate(assets, observations, facts=None, *, terminal_fraction=0.07):
    """Read visual observations + verified facts, never synthetic location IDs.

    An exclusion requires (1) an explicit post-production end-card assertion,
    (2) at least two *different* CTA families in the supporting text,
    (3) position in the last ~7% of the imported source sequence.
    If these conflict, mark REVIEW_REQUIRED but preserve original content.
    """
    if not 0 < terminal_fraction <= .20:
        raise ValueError('Invalid terminal screening fraction')
    by_source={a['asset_id']:a for a in assets.values()}
    observation_map={o['source_asset_id']:o for o in observations
                     if isinstance(o,dict) and isinstance(o.get('source_asset_id'),str)}
    n=len(assets)
    rows=[]
    excluded=set()
    review=set()
    for aid,a in sorted(assets.items(),key=lambda pair:pair[1]['sequence_index']):
        source=a['asset_id']
        obs=observation_map.get(source,{})
        source_rows=[{'text':str(f.get('text','')),
                      'evidence_frame_ids':f.get('evidence_frame_ids',[]),
                      'source':'S04_ORIGINAL_OBSERVATION'}
                     for f in obs.get('facts',[]) if isinstance(f,dict)]
        if facts is not None:
            source_rows += [{'text':str(f.get('text','')),
                         'evidence_frame_ids':f.get('evidence_frame_ids',[]),
                         'source':'IMAGE_VERIFIED_FACT',
                         'fact_id':fid}
                         for fid,f in facts.items()
                         if f.get('asset_id')==aid and f.get('visual_reviewed') is True]
        supporting=[r for r in source_rows if _END_CARD.search(r['text'])]
        if not supporting:
            continue
        evidence_text=' '.join(r['text'] for r in source_rows)
        ctas=[i for i,pat in enumerate(_CALL_TO_ACTION) if pat.search(evidence_text)]
        idx=a['sequence_index']
        at_end=idx>=max(0,n-max(2,round(n*terminal_fraction)))
        if len(ctas)>=2 and at_end:
            status='EXCLUDE_SOURCE_OUTRO'
            excluded.add(aid)
        else:
            status='REVIEW_REQUIRED_NOT_AUTO_EXCLUDED'
            review.add(aid)
        rows.append({'asset_id':aid,'source_asset_id':source,
            'source_sequence_index':idx,'status':status,
            'evidence_frame_ids':list(dict.fromkeys(
                f for r in supporting for f in r['evidence_frame_ids'])),
            'observed_quotes':[r['text'][:280] for r in supporting[:3]],
            'cta_signal_families':ctas,'terminal_context':at_end,
            'decision_basis':'EXPLICIT_POST_PRODUCTION_END_CARD_PLUS_MULTIPLE_CTA_IN_TERMINAL_CONTEXT'
                if aid in excluded else 'AMBIGUOUS_POST_PRODUCTION_CONTEXT_REQUIRE_INDEPENDENT_REVIEW'})
    return {'version':VERSION,'source_asset_count':n,
        'exclusion_count':len(excluded),
        'excluded_asset_ids':sorted(excluded),
        'review_required_asset_ids':sorted(review),
        'decisions':rows,
        'policy':'ONLY_EXPLICIT_PROMOTIONAL_VIDEO_OUTRO; NO_GENERIC_AD_SIGN_FILTER',
        'raw_source_media_modified':False}


def editorial_scope(assets, observations, facts, decision):
    """Return factual editorial scope, preserving original documents untouched.

    Canonical V IDs and original frames stay unchanged. Only a temporary
    contiguous planning index is created for valid original source assets.
    No terminal promotional fact may be a Chapter title/copy/media anchor.
    """
    blocked=set(decision['excluded_asset_ids'])
    new_facts={fid:f for fid,f in facts.items() if f.get('asset_id') not in blocked}
    new_obs=[]
    for o in observations:
        if not isinstance(o,dict):
            continue
        copy=deepcopy(o)
        if copy.get('asset_id') in blocked or next(
                (aid for aid,a in assets.items() if a['asset_id']==copy.get('source_asset_id')),
                None) in blocked:
            copy['facts']=[]
            copy['activity_code']='UNKNOWN'
            copy['event_salience']='NONE'
            copy['motifs']=[]
            copy['excluded_from_editorial_memory']='SOURCE_PROMOTIONAL_OUTRO'
        new_obs.append(copy)
    eligible={}
    original_indices={}
    for aid,a in sorted(assets.items(),key=lambda pair:pair[1]['sequence_index']):
        if aid in blocked:
            continue
        record=deepcopy(a)
        original_indices[len(eligible)]=a['sequence_index']
        record['sequence_index']=len(eligible)
        eligible[aid]=record
    if not eligible or not new_facts:
        raise ValueError('NO_ELIGIBLE_LIVED_EXPERIENCE_AFTER_CONTENT_GATE')
    return new_facts,new_obs,eligible,original_indices
