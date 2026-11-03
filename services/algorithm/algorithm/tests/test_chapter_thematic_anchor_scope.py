"""Only fact anchors may be repaired, not Chapter ownership or invented claims."""
from diary_one_ci import chapter_theme_hierarchy as h
import pytest


def source():
    a={f'V{i:03d}':{'asset_id':f'clip_{i:03d}','sequence_index':i-1}
       for i in range(1,7)}
    f={f'F{i:03d}':{'id':f'F{i:03d}','asset_id':f'V{i:03d}',
       'visual_reviewed':True,'evidence_frame_ids':[f'clip_{i:03d}-f0'],
       'text':'可见具体物体'} for i in range(1,7)}
    e=[{'episode_id':'E01','start_index':0,'end_index':2},
       {'episode_id':'E02','start_index':3,'end_index':5}]
    c={'chapters':[{'title':'港湾建筑','experience_kind':'CITYWALK',
         'episode_ids':['E01'],'anchor_fact_ids':['F005'],
         'reason':'港湾建筑主体与水面符合记录中的景物'},
        {'title':'公园植物','experience_kind':'GARDEN',
         'episode_ids':['E02'],'anchor_fact_ids':['F004','F002'],
         'reason':'植物在同一片区域组成具体自然景观'}]}
    return a,f,e,c


def test_invalid_cross_episode_anchors_are_replaced_only_with_real_visual_facts():
    assets,facts,episodes,raw=source()
    with pytest.raises(ValueError,match='CHAPTER_ANCHOR_OUTSIDE_EPISODE'):
        h.validate_chapters(raw,episodes,assets,facts,5)
    repaired,records=h.normalize_invalid_visual_anchors(raw,episodes,assets,facts,5)
    assert len(records)==2
    assert repaired['chapters'][0]['anchor_fact_ids']==['F001']
    assert repaired['chapters'][1]['anchor_fact_ids']==['F004']
    assert repaired['chapters'][0]['episode_ids']==raw['chapters'][0]['episode_ids']
    assert repaired['chapters'][1]['reason']==raw['chapters'][1]['reason']
    assert h.validate_chapters(repaired,episodes,assets,facts,5)
    assert raw['chapters'][0]['anchor_fact_ids']==['F005']


def test_no_unverified_evidence_can_be_promoted():
    assets,facts,episodes,raw=source()
    for i in (1,2,3):
        facts[f'F{i:03d}']['visual_reviewed']=False
    with pytest.raises(ValueError,match='Cannot recover malformed Chapter structure'):
        h.normalize_invalid_visual_anchors(raw,episodes,assets,facts,5)


def test_duplicate_episode_ownership_not_repaired_as_an_image_error():
    assets,facts,episodes,raw=source()
    raw['chapters'][1]['episode_ids']=['E01']
    amended,rec=h.normalize_invalid_visual_anchors(raw,episodes,assets,facts,5)
    with pytest.raises(ValueError,match='EPISODE_ASSIGNMENT_NOT_EXACTLY_ONCE'):
        h.validate_chapters(amended,episodes,assets,facts,5)
