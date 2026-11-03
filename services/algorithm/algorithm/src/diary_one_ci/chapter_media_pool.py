"""Balanced, traceable media candidate pool for global Chapter drafts.

Per-Chapter budget, temporal diversity and verified fact support. The final
model makes the visual choice; this ranker never fabricates an image or force-
publishes an unavailable scene. Videos remain on the owner's device.
"""
from collections import defaultdict, Counter
import math
import re

from .scenelet_builder import tokens


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
                               max_per_chapter=8,max_total=44,
                               priority_fact_ids_by_chapter=None,
                               episode_source_ranges_by_chapter=None,
                               observations=()):
    """Value-preserving evidence candidates, with legacy spread compatibility."""
    if not(1<=max_per_chapter<=12 and 1<=max_total<=64):
        raise ValueError('Invalid media image request limit')
    if priority_fact_ids_by_chapter is not None or episode_source_ranges_by_chapter is not None:
        return _select_evidence_priority_candidates(
            facts,assets,bundle,chapter_fact_groups,
            max_per_chapter=max_per_chapter,max_total=max_total,
            priority_fact_ids_by_chapter=priority_fact_ids_by_chapter or {},
            episode_source_ranges_by_chapter=episode_source_ranges_by_chapter or {},
            observations=observations)
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


def _specific_subject_terms(text):
    """Scene-agnostic clues: quoted labels and title-cased entity phrases.

    This is never a place-name lookup. Named artwork, a branded sculpture,
    a shopfront, a museum, an animal species, etc. can contribute evidence.
    """
    text=str(text or '')
    names=set()
    names.update(m.strip().casefold() for m in
                 re.findall(r'[“「『]([^”」』]{2,45})[”」』]',text))
    names.update(m.casefold() for m in
                 re.findall(r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){1,5}\b',text))
    return {n for n in names if len(n)>=3}


def _source_fact_stats(facts, assets):
    """Term evidence per source clip; no assumed real capture timestamp."""
    docs={}
    for fid,f in facts.items():
        aid=f.get('asset_id')
        if aid in assets and f.get('visual_reviewed') is True:
            docs.setdefault(aid,[]).append(str(f.get('text') or ''))
    term_freq=Counter()
    named_freq=Counter()
    for texts in docs.values():
        term_freq.update(set().union(*(tokens(x) for x in texts)))
        named_freq.update(set().union(*(_specific_subject_terms(x) for x in texts)))
    return len(docs),term_freq,named_freq


def _select_evidence_priority_candidates(
        facts,assets,bundle,chapter_fact_groups, *,
        max_per_chapter,max_total,priority_fact_ids_by_chapter,
        episode_source_ranges_by_chapter,observations):
    """Chapter-safe source coverage: protected actual facts, then experiences.

    Source-asset identity, verified fact ID and actual frame ID are required.
    Exact original prompt/profile/recognition is reused; nothing is inferred
    from dataset name or image filename. A fact can anchor a Chapter only
    when an actual supplied JPG frame supports that fact.
    """
    if max_total < len(chapter_fact_groups):
        raise ValueError('Image candidate cap cannot cover all Chapters')
    n_documents,df,ndf=_source_fact_stats(facts,assets)
    order={aid:asset.get('sequence_index') for aid,asset in assets.items()}
    obs={o.get('source_asset_id'):o for o in observations if isinstance(o,dict)}
    chapter_rows={}
    audit_chapters=[]
    all_reserved=set()
    for cid,ids in chapter_fact_groups.items():
        if not isinstance(cid,str):
            continue
        allowed={fid for fid in ids if fid in facts and
                 facts[fid].get('asset_id') in assets and
                 facts[fid].get('visual_reviewed') is True}
        protected=[fid for fid in priority_fact_ids_by_chapter.get(cid,[]) if fid in allowed]
        # Never silently upgrade an unverified or foreign fact to a protected
        # image: this is a local contract mismatch, not a soft preference.
        if len(protected)!=len(priority_fact_ids_by_chapter.get(cid,[])):
            raise ValueError('UNVERIFIED_OR_FOREIGN_PRIORITY_FACT')
        by_asset=defaultdict(list)
        for fid in sorted(allowed):
            fact=facts[fid]
            for frameid in fact.get('evidence_frame_ids',[]):
                by_asset[fact['asset_id']].append((fid,frameid))
        rows=[]
        for aid,refs in by_asset.items():
            valid=[]
            for fr in assets[aid].get('frames',[]):
                refs_for_frame=[fid for fid,fid_frame in refs if fid_frame==fr['frame_id']]
                if refs_for_frame:
                    valid.append((fr,sorted(set(refs_for_frame))))
            if not valid:continue
            relevant=set(protected)
            valid.sort(key=lambda z:(
                -len(set(z[1]) & relevant),
                -len(z[1]),
                abs(float(z[0].get('source_timestamp_ms') or 0)-
                    float(assets[aid].get('original_duration_ms') or 10000)/2),
                z[0]['frame_id']))
            fr,supported=valid[0]
            text=' '.join(facts[fid].get('text','') for fid in supported)
            toks=tokens(text)
            names=_specific_subject_terms(text)
            # Treat uncommon and explicitly named subjects as important:
            # this is a generic content signal, not a hardcoded landmark.
            rarity=sum(max(0.,math.log((n_documents+1)/(1+df[t])))*1.
                       for t in toks)/(max(1,len(toks))**0.5)
            namescore=sum(1./math.sqrt(1+ndf[name]) for name in names)
            meta=obs.get(assets[aid].get('asset_id'),{})
            salience={'HIGH':2.0,'MEDIUM':0.9,'LOW':0.0}.get(meta.get('event_salience'),0.0)
            quality=float(meta.get('quality_score',0.0) or 0.0)
            score=rarity+2.2*namescore+0.4*min(len(supported),3)+salience+0.8*quality
            rows.append({'asset_id':aid,'frame':fr,'fact_ids':supported,
                         'index':order[aid],'score':round(score,4),
                         'explicit_subjects':sorted(names),
                         'support_strength':len(supported)})
        rows.sort(key=lambda z:(z['index'],z['asset_id']))
        chosen=[]
        def add(row,why):
            if row and row['asset_id'] not in {x['asset_id'] for x in chosen}:
                if len(chosen)<max_per_chapter:
                    chosen.append({**row,'reason_to_show':why})
                    return True
            return False
        # Primary: each model-identified focus fact must reach S09A/B before
        # generic timeline frames, as long as the real JPG exists.
        for fid in protected:
            options=[r for r in rows if fid in r['fact_ids']]
            if options:
                add(sorted(options,key=lambda x:(-x['score'],x['index']))[0],
                    'PROTECTED_VERIFIED_STORY_ANCHOR')
        # Secondary: protect independent experiences, including a repeated
        # place that was fused across nonadjacent ranges. We do not force a
        # second Chapter or require any particular scene name to recur.
        groups=episode_source_ranges_by_chapter.get(cid,[])
        reservation_failed=[]
        for group in groups:
            start,end=group['start_index'],group['end_index']
            if any(start<=x['index']<=end for x in chosen):
                continue
            pool=[r for r in rows if start<=r['index']<=end]
            if pool:
                best=sorted(pool,key=lambda x:(-x['score'],x['index']))[0]
                if not add(best,'EPISODE_VISUAL_COVERAGE'):
                    reservation_failed.append(group['episode_id'])
            else:
                reservation_failed.append(group['episode_id'])
        # Tertiary: complement with high-value real subjects, not uniform
        # five positions. Guard redundancy via token similarity and distance.
        while len(chosen)<max_per_chapter:
            remaining=[r for r in rows if r['asset_id'] not in
                       {x['asset_id'] for x in chosen}]
            if not remaining:break
            def utility(row):
                dist=min((abs(row['index']-other['index']) for other in chosen),
                         default=max(1,len(assets)))
                distinct_names=set(row['explicit_subjects'])-set().union(
                    *(set(other['explicit_subjects']) for other in chosen))
                return (row['score']+1.2*len(distinct_names)
                        +0.25*math.log1p(dist))
            best=max(remaining,key=lambda z:(utility(z),-z['index']))
            add(best,'VALUE_NOVELTY_AND_COMPLEMENT')
        audit_chapters.append({
            'chapter_id':cid,'protected_fact_ids':protected,
            'selected_source_asset_ids':[r['asset_id'] for r in chosen],
            'reasons':[r['reason_to_show'] for r in chosen],
            'eligible_source_count':len(rows),
            'episode_ids':[g['episode_id'] for g in groups],
            'uncovered_episode_ids':reservation_failed,
            'protected_fact_ids_without_selected_frame':[
                 fid for fid in protected if not any(fid in z['fact_ids'] for z in chosen)]})
        chapter_rows[cid]=chosen

    # Source-based Chapter groups must have no collisions. Final judgement
    # may choose different images; one uploaded source never belongs to two
    # distinct Chapters unless the thematic fact contract itself is broken.
    selected=[];seen=set()
    rounds=max((len(rows) for rows in chapter_rows.values()),default=0)
    for depth in range(rounds):
        for cid,rows in chapter_rows.items():
            if depth>=len(rows):continue
            row=rows[depth]
            key=(row['asset_id'],row['frame']['frame_id'])
            if key in seen:
                raise ValueError('CROSS_CHAPTER_REUSED_MEDIA_CANDIDATE')
            selected.append((cid,row))
            seen.add(key)
            if len(selected)>=max_total:break
        if len(selected)>=max_total:break
    shown={};evidence=[];records=[]
    for cid,r in selected:
        aid,frame=r['asset_id'],r['frame']
        shown.setdefault(aid,{})[frame['frame_id']]=frame
        evidence.append((assets[aid],frame,
             (bundle.manifest_path.parent/frame['relative_path']).resolve()))
        records.append({'candidate_id':f'P{len(records)+1:03d}',
             'asset_id':aid,'frame_id':frame['frame_id'],
             'pts_ms':frame.get('source_timestamp_ms'),
             'fact_ids':r['fact_ids']})
    audit={'policy':'CONTENT_FIRST_EPISODE_AND_ANCHOR_POOL_V02',
           'max_frames':max_total,'max_per_chapter':max_per_chapter,
           'eligible_frame_count':sum(row['eligible_source_count'] for row in audit_chapters),
           'shown_frame_count':len(records),'shown_frames':records,
           'priority_coverage_audit':audit_chapters,
           'chapter_coverage':[{'chapter_id':cid,
               'status':'COVERED' if any(z['asset_id'] in {x['asset_id'] for x in rows}
                          for z in records) else
                        'NO_VERIFIED_CANDIDATE' if not rows else 'BUDGET_EXHAUSTED',
               'candidate_ids':[z['candidate_id'] for z in records
                 if z['asset_id'] in {x['asset_id'] for x in rows}]}
                 for cid,rows in chapter_rows.items()],
           'unrepresented_candidate_groups':[
               cid for cid,rows in chapter_rows.items() if rows and not any(
                   z['asset_id'] in {x['asset_id'] for x in rows} for z in records)]}
    return shown,evidence,audit
