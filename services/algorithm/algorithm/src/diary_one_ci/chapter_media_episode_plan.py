"""Link S07 thematic Episodes to exact S09 image-verified candidate P IDs.

Pure generation constraint and audit, *not* an additional LLM Judge.
The producer chooses one cover plus up to five complementary images from the
same Chapter's verified photos. The chosen collection's experience coverage
is measured after S09B so S11 cannot treat absent photos as visual evidence.
"""
from collections import defaultdict
from copy import deepcopy

VERSION='SOURCE_VERIFIED_EPISODE_GALLERY_COVERAGE_V01'

def candidate_map(groups, episodes, candidates, assets, route_to_original):
    source={e['episode_id']:e for e in episodes}
    actual_sequence={aid:row['sequence_index'] for aid,row in assets.items()}
    episode_by_original={}
    for e in episodes:
        for idx in range(e['start_index'],e['end_index']+1):
            original=route_to_original[idx]
            if original in episode_by_original:
                raise ValueError('SOURCE_ASSIGNED_TO_TWO_PROVISIONAL_EPISODES')
            episode_by_original[original]=e['episode_id']
    cards=[]
    assigned={}
    for i,c in enumerate(groups):
        cid=f'C{i+1:02d}'
        episode_ids=list(c['episode_ids'])
        for eid in episode_ids:
            if eid not in source or eid in assigned:
                raise ValueError('DUPLICATE_OR_UNKNOWN_EPISODE_IN_MEDIA_PLAN')
            assigned[eid]=cid
        entries=[]
        for eid in episode_ids:
            e=source[eid]
            cands=[p for p in candidates if
              episode_by_original.get(actual_sequence.get(p['asset_id']))==eid]
            entries.append({'episode_id':eid,'theme':e['theme'],
                'experience_kind':e['experience_kind'],
                'candidate_ids':[p['candidate_id'] for p in cands],
                'supporting_image_verified_fact_ids':list(dict.fromkeys(
                    fid for p in cands for fid in p.get('fact_ids',[])))[:12],
                'visual_candidate_available':bool(cands)})
        cards.append({'chapter_id':cid,'episode_count':len(entries),
            'episode_candidates':entries,
            'gallery_budget_max':5,
            'selection_instruction':'封面要最能体现整章核心；组图优先表现不同有意义的Episode。'
                '如果一章不同重要经历有图可选，不要重复选择5张几乎相同的普通环境。'
                '但不存在好图的Episode不得强行编造画面；五张图库无法穷尽全部Episode时，'
                '保留明确的缺口供S11/S14审查，不因满额强行错误归属。'})
    if set(assigned)!=set(source):
        raise ValueError('EPISODE_WITHOUT_CHAPTER_OWNERSHIP')
    return {'version':VERSION,'chapters':cards,
            'no_forced_one_photo_per_episode_when_more_than_five':True,
            'source_basis':'EXACT_CANDIDATE_FRAME_AND_VERIFIED_FACTS'}


def restrict_to_independently_verified_frames(plan, assessments):
    """No P ID is advertised as available before S09A supports actual frame."""
    bypid={a['candidate_id']:a for a in assessments}
    amended=deepcopy(plan)
    dropped=[]
    for chapter in amended['chapters']:
        for episode in chapter['episode_candidates']:
            original=episode['candidate_ids']
            accepted=[pid for pid in original
                if pid in bypid and bypid[pid].get('fact_ids')]
            dropped.extend(pid for pid in original if pid not in accepted)
            episode['candidate_ids']=accepted
            episode['supporting_image_verified_fact_ids']=list(dict.fromkeys(
                fact for pid in accepted for fact in bypid[pid]['fact_ids']))
            episode['visual_candidate_available']=bool(accepted)
    amended['policy']='ONLY_S09A_INDEPENDENTLY_IMAGE_REVIEWED_CANDIDATES'
    amended['rejected_candidate_ids']=sorted(set(dropped))
    return amended


def selected_coverage(plan, raw_selection):
    byid={c['chapter_id']:c for c in plan['chapters']}
    submitted={c['chapter_id']:c for c in raw_selection['chapter_media']}
    if set(byid)!=set(submitted):
        raise ValueError('S09B_SOURCE_COVERAGE_REQUIRES_ALL_CHAPTERS')
    output=[]
    for cid,card in byid.items():
        seen={r['candidate_id'] for r in submitted[cid]['media_choices']}
        represented=[]
        missing=[]
        no_evidence=[]
        for row in card['episode_candidates']:
            if set(row['candidate_ids'])&seen:
                represented.append(row['episode_id'])
            elif row['candidate_ids']:
                missing.append({'episode_id':row['episode_id'],
                  'theme':row['theme'],
                  'available_approved_candidate_ids':row['candidate_ids']})
            else:
                no_evidence.append(row['episode_id'])
        output.append({'chapter_id':cid,
          'represented_episode_ids':represented,
          'source_verified_candidates_unselected':missing,
          'episodes_without_any_approved_candidate':no_evidence,
          'gallery_media_count':len(seen),
          'policy':'SOURCE_GROUNDED_GALLERY_COVERAGE_NOT_AN_LLM_SCORE'})
    return {'version':VERSION,'chapters':output,
       'status':'AUDIT_ONLY_NO_UNVERIFIED_MEDIA_PROMOTION'}
