"""Independent audit of *semantic* and *visual* day coverage.

No "every scene must be Chapter" rule: all novel scenelets are reviewed
as candidate evidence, but routine footage may be legitimately left out.
A semantic mention never substitutes for an image, and a selected image does
not prove claims about an invisible action or the photographer.
"""
from collections import Counter

VERSION='GLOBAL_CHAPTER_DUAL_COVERAGE_V01'


def audit_coverage(scene_map, chapters, moments, *, verified_fact_ids=(),
                   visible_media=(), available_asset_ids=()):
    scenes=scene_map.get('scenelets',[])
    seen_fact=set()
    for row in chapters:
        seen_fact.update(fid for fid in row.get('fact_ids',[]) if isinstance(fid,str))
    for row in moments:
        if isinstance(row,dict) and isinstance(row.get('fact_id'),str):
            seen_fact.add(row['fact_id'])
    verified=set(verified_fact_ids)
    displayed_sources=set(visible_media)
    available=set(available_asset_ids)
    rows=[]
    for s in scenes:
        ids=set(s.get('fact_ids',[]))
        aids=set(s.get('asset_ids',[]))
        supported=ids&verified
        in_story=ids&seen_fact
        in_gallery=aids&displayed_sources
        eligible=bool(supported)
        significant=eligible and s.get('evidence_asset_count',0)>=2
        # Significant is a *review* priority, not evidence that it merits a
        # separate Chapter. A long routine scene can be skipped legitimately.
        status=('NO_VERIFIED_FACTS' if not eligible else
                'MEDIA_AND_SEMANTIC' if in_story and in_gallery else
                'SEMANTIC_ONLY' if in_story else
                'MEDIA_ONLY' if in_gallery else
                'REVIEW_REQUIRED' if significant else 'NOT_SELECTED_SINGLE_SCENE')
        rows.append({'scenelet_id':s['scenelet_id'],
            'asset_ids':s['asset_ids'],
            'supported_fact_ids':sorted(supported),
            'semantically_covered_fact_ids':sorted(in_story),
            'selected_media_asset_ids':sorted(in_gallery),
            'evidence_asset_count':s.get('evidence_asset_count',0),
            'status':status,'candidate_significance':significant})
    eligible=[r for r in rows if r['supported_fact_ids']]
    if eligible:
        semantic=sum(bool(r['semantically_covered_fact_ids']) for r in eligible)/len(eligible)
        visual=sum(bool(r['selected_media_asset_ids']) for r in eligible)/len(eligible)
    else:
        semantic=visual=0.
    unresolved=[r['scenelet_id'] for r in rows if r['status']=='REVIEW_REQUIRED']
    no_media=[r['scenelet_id'] for r in rows if r['status']=='SEMANTIC_ONLY']
    missing_files=sorted(displayed_sources-available) if available else []
    return {'version':VERSION,'status':'REVIEW_REQUIRED' if unresolved or missing_files else 'AUDITED',
        'scenelet_count':len(scenes),'verified_scenelet_count':len(eligible),
        'semantic_scenelet_coverage':round(semantic,4),
        'visual_scenelet_coverage':round(visual,4),
        'semantic_only_scenelet_ids':no_media,
        'unrepresented_significant_scenelet_ids':unresolved,
        'selected_asset_missing_original':missing_files,
        'scenelets':rows,
        'warning':'Unrepresented does not prove that a Chapter should exist. Review significance independently.'}


def status_for_delivery(coverage,existing_delivery):
    """Do not silently label a day clean when high-evidence scenes need review."""
    if coverage.get('status')=='REVIEW_REQUIRED' and existing_delivery=='READY_PRIMARY_COPY':
        return 'READY_WITH_ITEM_BLOCKS'
    return existing_delivery
