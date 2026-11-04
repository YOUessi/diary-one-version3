"""Tests of content-based Chapter count, independent from external route evidence."""
from pathlib import Path
import json
from diary_one_ci import chapter_theme_hierarchy as planner
from diary_one_ci import chapter_boundary_planner, chapter_episode_router
from diary_one_ci.product_editor import compile_structure_wire, EDITOR_SCHEMA

def test_six_real_distinct_experiences_compile_as_six_chapters():
    assert chapter_boundary_planner.MAX_CHAPTERS==8
    assert chapter_episode_router.MAX_CHAPTERS==8
    assert EDITOR_SCHEMA['properties']['chapters']['maxItems']==8
    assert EDITOR_SCHEMA['properties']['chapter_boundaries']['maxItems']==28
    assert json.loads((Path(__file__).resolve().parents[1]/
      'contracts/product_preview_v01.schema.json').read_text())['properties']['chapters']['maxItems']==8
    assets={}
    facts={}
    episodes=[]
    for i in range(6):
        aid=f'V{i+1:03d}'
        sid=f'clip-{i:03d}'
        assets[aid]={'asset_id':sid,'sequence_index':i,'frames':[
            {'frame_id':sid+'-f0','source_timestamp_ms':2000}],
            'original_duration_ms':10000}
        facts[f'F{i+1:03d}']={'id':f'F{i+1:03d}','asset_id':aid,
            'visual_reviewed':True,'text':f'可见独立的活动主体与场景{i}',
            'evidence_frame_ids':[sid+'-f0']}
        episodes.append({'episode_id':f'E{i+1:02d}',
           'start_index':i,'end_index':i,'theme':f'值得保留的不同经历{i}',
           'experience_kind':'CITYWALK',
           'reason':'可见独立的主体和实际场景支持该片段'})
    raw={'chapters':[{'title':f'真实不同体验和地点{i}',
        'experience_kind':'CITYWALK',
        'episode_ids':[f'E{i+1:02d}'],
        'anchor_fact_ids':[f'F{i+1:03d}'],
        'reason':'各个Chapter具有不同的实质内容与视觉事实'}
        for i in range(6)]}
    normalized=planner.validate_chapters(raw,episodes,assets,facts,8)
    assert len(normalized)==6
    wire=planner.build_wire(normalized,assets,facts)
    assert len(wire['chapter_boundaries'])==15
    chapters,moments,issues,coverage=compile_structure_wire(
        wire,facts,assets,8)
    assert not issues and len(chapters)==6
    assert len({fid for c in chapters for fid in c['fact_ids']})==6


def test_one_continuous_experience_stays_one_chapter_despite_eight_slot_cap():
    assets={'V001':{'asset_id':'a','sequence_index':0,'frames':[{'frame_id':'a-f0'}]}}
    facts={'F001':{'asset_id':'V001','visual_reviewed':True,
            'evidence_frame_ids':['a-f0'],'text':'同一连续骑行的地面和路况'}}
    episodes=[{'episode_id':'E01','start_index':0,'end_index':0,
        'theme':'单次连续骑行','experience_kind':'CYCLING','reason':'同一连续活动'}]
    output={'chapters':[{'title':'一次完整骑行活动','experience_kind':'CYCLING',
        'episode_ids':['E01'],'anchor_fact_ids':['F001'],
        'reason':'仅一次有证据支持的独立活动'}]}
    assert len(planner.validate_chapters(output,episodes,assets,facts,8))==1
