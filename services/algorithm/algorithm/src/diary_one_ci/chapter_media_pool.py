"""Balanced, traceable media candidate pool for global Chapter drafts.

Per-Chapter budget, temporal diversity and verified fact support. The final
model makes the visual choice; this ranker never fabricates an image or force-
publishes an unavailable scene. Videos remain on the owner's device.
"""
from collections import defaultdict
import math


def _spread(rows, limit):
    """Reserve early, middle and late *distinct assets* without time invention."""
    if limit <= 0:
        return []
    if len(rows)<=limit:
        return rows
    chosen=[]
    for i in range(limit):
        pos=round(i*(len(rows)-1)/(limit-1)) if limit>1 else len(rows)//2
        row=rows[pos]
        if row not in chosen:
            chosen.append(row)
    return chosen


def select_balanced_candidates(facts,assets,bundle,chapter_fact_groups, *,
                               max_per_chapter=8,max_total=44):
    """Fair round-robin across proposed Chapters, not first 18 frames of a day."""
    if not(1<=max_per_chapter<=12 and 1<=max_total<=64):
        raise ValueError('Invalid media image request limit')
    chapter_rows={}
    for cid,ids in chapter_fact_groups.items():
        if not isinstance(cid,str):
            continue
        by_asset=defaultdict(list)
        for fid in ids:
            if fid not in facts or not facts[fid].get('visual_reviewed'):
                continue
            fact=facts[fid]
            for frame_id in fact.get('evidence_frame_ids',[]):
                by_asset[fact['asset_id']].append(frame_id)
        candidates=[]
        for aid,frames in by_asset.items():
            if aid not in assets:
                continue
            valid=[f for f in assets[aid]['frames']
                   if f['frame_id'] in frames]
            if not valid:
                continue
            # One representative per source clip for chapter gallery pool.
            # Preference for a genuine selected frame near middle avoids
            # blindly always choosing f0; final review compares alternatives.
            valid.sort(key=lambda f:(
                abs(float(f.get('source_timestamp_ms') or 0)
                    - (float(assets[aid].get('original_duration_ms') or 10000)/2)),
                f['frame_id']))
            frame=valid[0]
            support=[fid for fid in ids if fid in facts
                     and facts[fid]['asset_id']==aid
                     and frame['frame_id'] in facts[fid]['evidence_frame_ids']]
            if support:
                candidates.append((aid,frame,support))
        candidates.sort(key=lambda item:(assets[item[0]].get('sequence_index',0),item[0]))
        chapter_rows[cid]=_spread(candidates,max_per_chapter)

    selected=[]
    seen=set()
    max_depth=max((len(x) for x in chapter_rows.values()), default=0)
    for depth in range(max_depth):
        for cid,options in chapter_rows.items():
            if depth>=len(options):
                continue
            aid,frame,support=options[depth]
            key=(aid,frame['frame_id'])
            if key in seen:
                continue
            selected.append((aid,frame,support))
            seen.add(key)
            if len(selected)>=max_total:
                break
        if len(selected)>=max_total:
            break
    shown={}
    evidence=[]
    records=[]
    for aid,frame,support in selected:
        fid=frame['frame_id']
        shown.setdefault(aid,{})[fid]=frame
        evidence.append((assets[aid],frame,(bundle.manifest_path.parent / frame['relative_path']).resolve()))
        records.append({'candidate_id':f'P{len(records)+1:03d}',
            'asset_id':aid,'frame_id':fid,
            'pts_ms':frame.get('source_timestamp_ms'),
            'fact_ids':support})
    audit={'policy':'GLOBAL_CHAPTER_BALANCED_CANDIDATES_V01',
           'max_frames':max_total,'max_per_chapter':max_per_chapter,
           'eligible_frame_count':len({(a,f) for options in chapter_rows.values()
                                         for a,fr,_ in options for f in [fr['frame_id']]}),
           'shown_frame_count':len(records),'shown_frames':records,
           'chapter_coverage':[{
               'chapter_id':cid,
               'status':'COVERED' if any(r['asset_id'] in {a for a,_,_ in options} for r in records)
                   else 'NO_VERIFIED_CANDIDATE' if not options else 'BUDGET_EXHAUSTED',
               'candidate_ids':[r['candidate_id'] for r in records
                   if any(r['asset_id']==aid and r['frame_id']==fr['frame_id'] for aid,fr,_ in options)]
           } for cid,options in chapter_rows.items()],
           'unrepresented_candidate_groups':[cid for cid,options in chapter_rows.items()
                                              if options and not any(
                                                  any(r['asset_id']==aid and r['frame_id']==fr['frame_id']
                                                      for aid,fr,_ in options) for r in records)]
         }
    return shown,evidence,audit
