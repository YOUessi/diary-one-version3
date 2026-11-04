"""Build chapter-wide, multi-Episode writing outlines from real selected frames.

The previous writer tended to compress an entire market/district/garden into
a single cover object's description. This module supplies all distinct
selected experiences and their own frame-supported facts, without ever
inventing travel routes or filling gaps from unseen source videos.
"""
from collections import defaultdict
from copy import deepcopy

VERSION='EPISODE_COVERAGE_STORY_OUTLINE_V01'

def build(chapters, episode_audit, assets, facts, *, route_to_original=None):
    groups=episode_audit.get('chapter_grouping',[])
    episodes={e['episode_id']:e
              for e in episode_audit.get('independent_episodes',[])}
    if not groups:
        return {}
    if len(chapters)!=len(groups):
        raise ValueError('STORY_OUTLINE_CHAPTER_COUNT_DRIFT')
    index_map=(route_to_original if route_to_original is not None
        else {a['sequence_index']:a['sequence_index'] for a in assets.values()})
    out={}
    for i,(chapter,group) in enumerate(zip(chapters,groups),1):
        cid=f'C{i:02d}'
        if chapter['id']!=cid:
            raise ValueError('STORY_OUTLINE_CHAPTER_ORDER_DRIFT')
        choices=chapter.get('media_choices',[])
        chosen={}
        for c in choices:
            aid=c.get('asset_id')
            if aid not in assets:
                raise ValueError('STORY_OUTLINE_UNKNOWN_SELECTED_ASSET')
            chosen[aid]=c
        epirows=[]
        for eid in group['episode_ids']:
            e=episodes[eid]
            indices={index_map[k] for k in range(e['start_index'],e['end_index']+1)}
            evidence=[]
            for aid,choice in chosen.items():
                if assets[aid]['sequence_index'] not in indices:
                    continue
                fidset=[fid for fid in choice.get('fact_ids',[])
                        if fid in facts and facts[fid]['asset_id']==aid
                        and choice['frame_id'] in facts[fid].get('evidence_frame_ids',[])
                        and facts[fid].get('visual_reviewed') is True]
                for fid in fidset[:2]:
                    evidence.append({'fact_id':fid,'frame_id':choice['frame_id'],
                        'source_asset_id':assets[aid]['asset_id'],
                        'exact_verified_description':facts[fid]['text'][:190]})
            # A lack of chosen media is evidence that this Episode has no
            # representative picture in the current published gallery.
            # The model must not fabricate narrative support for the gap.
            epirows.append({'episode_id':eid,'theme':e['theme'],
               'experience_kind':e['experience_kind'],
               'source_span':[e['start_index'],e['end_index']],
               'gallery_supported':bool(evidence),
               'selected_visual_evidence':evidence[:4],
               'copy_policy':('DESCRIBE_IF_RELEVANT_FROM_THESE_EXACT_FRAME_FACTS'
                              if evidence else
                              'NO_SELECTED_IMAGE_EVIDENCE_DO_NOT_INVENT')})
        out[cid]={'policy':VERSION,'chapter_id':cid,'chapter_theme':chapter['theme'],
            'experiences':epirows,
            'covered_episode_ids':[e['episode_id'] for e in epirows if e['gallery_supported']],
            'unrepresented_episode_ids':[e['episode_id'] for e in epirows if not e['gallery_supported']],
            'editorial_rule':'Represent meaningful distinct experiences; do not reduce a district or garden to just its cover object. Never invent interclip route or elapsed time.'}
    return out


def writer_context(outlines):
    """An exact-grounding subset suitable for the S11 prompt."""
    return {cid:{'chapter_theme':row['chapter_theme'],
       'verified_experiences':[{
         'episode_id':e['episode_id'],'theme':e['theme'],
         'selected_visual_evidence':e['selected_visual_evidence']}
         for e in row['experiences'] if e['gallery_supported']],
       'unrepresented_episode_ids':row['unrepresented_episode_ids'],
       'policy':row['editorial_rule']}
       for cid,row in outlines.items()}
