"""S09 album must know which selected facts represent which lived Episode."""
import pytest
from diary_one_ci import chapter_media_episode_plan as p


def fixtures():
    grouped=[{'title':'港湾经历','episode_ids':['E01','E03']},
             {'title':'市集购物','episode_ids':['E02']}]
    episodes=[{'episode_id':'E01','theme':'港湾建筑','experience_kind':'CITYWALK',
               'start_index':0,'end_index':1},
              {'episode_id':'E02','theme':'市集手工艺品','experience_kind':'MARKET_SHOPPING',
               'start_index':2,'end_index':2},
              {'episode_id':'E03','theme':'港湾大桥与海景','experience_kind':'CITYWALK',
               'start_index':3,'end_index':3}]
    assets={f'V{i+1:03d}':{'sequence_index':i} for i in range(4)}
    picks=[{'candidate_id':f'P{i+1:03d}','asset_id':f'V{i+1:03d}',
            'frame_id':f'frame_{i}','fact_ids':[f'F{i+1:03d}']}
           for i in range(4)]
    return grouped,episodes,assets,picks


def test_cross_time_experiences_stay_one_album_with_real_candidates():
    grouped,episodes,assets,picks=fixtures()
    m=p.candidate_map(grouped,episodes,picks,assets,{i:i for i in range(4)})
    assert len(m['chapters'])==2
    first=m['chapters'][0]
    assert [z['episode_id'] for z in first['episode_candidates']]==['E01','E03']
    assert first['episode_candidates'][0]['candidate_ids']==['P001','P002']
    assert first['episode_candidates'][1]['candidate_ids']==['P004']
    assert m['chapters'][1]['episode_candidates'][0]['candidate_ids']==['P003']


def test_actual_selections_audit_unrepresented_scene_not_fake_it():
    grouped,episodes,assets,picks=fixtures()
    m=p.candidate_map(grouped,episodes,picks,assets,{i:i for i in range(4)})
    selection={'chapter_media':[
      {'chapter_id':'C01','media_choices':[{'candidate_id':'P001'}]},
      {'chapter_id':'C02','media_choices':[{'candidate_id':'P003'}]}]}
    a=p.selected_coverage(m,selection)
    first=a['chapters'][0]
    assert first['represented_episode_ids']==['E01']
    assert first['source_verified_candidates_unselected']==[{
       'episode_id':'E03','theme':'港湾大桥与海景',
       'available_approved_candidate_ids':['P004']}]
    assert a['status']=='AUDIT_ONLY_NO_UNVERIFIED_MEDIA_PROMOTION'
    assert not first['episodes_without_any_approved_candidate']


def test_excluding_last_outro_changes_source_index_without_foreign_ownership():
    grouped,episodes,assets,picks=fixtures()
    # Source input index 2 was excluded; filtered Episode indices 0,1,2
    # now point to original source 0,1,3.
    groups=[{'episode_ids':['E01','E02']}]
    eps=[{'episode_id':'E01','theme':'海岸1','experience_kind':'CITYWALK',
          'start_index':0,'end_index':1},
         {'episode_id':'E02','theme':'海岸2','experience_kind':'CITYWALK',
          'start_index':2,'end_index':2}]
    a=p.candidate_map(groups,eps,[picks[0],picks[1],picks[3]],
                      assets,{0:0,1:1,2:3})
    assert a['chapters'][0]['episode_candidates'][1]['candidate_ids']==['P004']


def test_episode_is_not_assigned_to_two_chapters():
    grouped,episodes,assets,picks=fixtures()
    grouped[1]['episode_ids']=['E01','E02']
    with pytest.raises(ValueError,match='DUPLICATE_OR_UNKNOWN_EPISODE'):
        p.candidate_map(grouped,episodes,picks,assets,{i:i for i in range(4)})


def test_stage_s09a_restriction_does_not_advertise_unverified_frame_candidates():
    grouped,episodes,assets,picks=fixtures()
    plan=p.candidate_map(grouped,episodes,picks,assets,{i:i for i in range(4)})
    scoped=p.restrict_to_independently_verified_frames(plan,[
      {'candidate_id':'P001','fact_ids':['F001']},
      {'candidate_id':'P002','fact_ids':[]},
      {'candidate_id':'P003','fact_ids':['F003']},
      {'candidate_id':'P004','fact_ids':['F004']}])
    assert scoped['rejected_candidate_ids']==['P002']
    assert scoped['chapters'][0]['episode_candidates'][0]['candidate_ids']==['P001']
    assert scoped['chapters'][0]['episode_candidates'][0]['supporting_image_verified_fact_ids']==['F001']
    assert plan['chapters'][0]['episode_candidates'][0]['candidate_ids']==['P001','P002']
