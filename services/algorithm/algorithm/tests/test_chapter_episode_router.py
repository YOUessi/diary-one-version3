"""Global route identity and media facts contract; never a fixed city split."""
from copy import deepcopy

import pytest
from diary_one_ci import chapter_episode_router as r, product_editor as p, frame_selection

def fixtures(n=60):
    assets={}
    facts={}
    observations=[]
    for i in range(n):
        aid=f'V{i+1:03d}'
        src=f'segment-{i:03d}'
        assets[aid]={'asset_id':src,'sequence_index':i,'original_duration_ms':10000,
                     'frames':[{'frame_id':f'{src}-f0','source_timestamp_ms':2000}]}
        facts[f'F{i+1:03d}']={'id':f'F{i+1:03d}','asset_id':aid,
            'source_asset_id':src,'evidence_frame_ids':[f'{src}-f0'],
            'visual_reviewed':True,'text': ('街区市集摊位与行人' if i<n//2 else '植物园池塘和树林')}
        observations.append({'source_asset_id':src,
           'activity_code':'WALKING' if i<n//2 else 'OBSERVING',
           'setting_code':'URBAN_STREET' if i<n//2 else 'PARK',
           'facts':[{'text':facts[f'F{i+1:03d}']['text']}]})
    return assets,facts,observations

def episodes(n=60):
    return [{'start_index':0,'end_index':n//2-1,'theme':'城市集市与街区',
             'experience_kind':'CITYWALK','reason':'有多段市集和街道相关的具体事实'},
            {'start_index':n//2,'end_index':n-1,'theme':'树林公园里的池塘',
             'experience_kind':'GARDEN','reason':'有多段绿色树木池塘和小径的具体事实'}]

def test_episode_wire_binds_all_fact_ids_once_across_60_clips():
    assets,facts,_=fixtures()
    wire=r.compile_wire(episodes(),assets,facts)
    assert [len(c['fact_ids']) for c in wire['chapters']]==[30,30]
    assert len({fid for c in wire['chapters'] for fid in c['fact_ids']})==len(facts)
    assert len(wire['chapter_boundaries'])==1
    chapters,moments,issues,_=p.compile_structure_wire(wire,facts,assets,5)
    assert len(chapters)==2 and moments==[] and issues==[]

def test_route_gaps_duplicates_and_fabricated_kinds_are_rejected():
    good=episodes()
    for bad in [
        [{**good[0],'end_index':28},good[1]],
        [good[0],{**good[1],'start_index':29}],
        [good[0],{**good[1],'end_index':70}],
        [good[0],{**good[1],'experience_kind':'MAGICAL_SEA'}],
        [good[0],{**good[1],'start_index':59,'end_index':59}],
    ]:
        with pytest.raises(ValueError):
            r.validate({'chapters':bad},60)

def test_route_has_one_episode_when_visuals_are_homogeneous():
    assets,facts,observations=fixtures()
    seen=[]
    def ask(stage, prompt,schema,context):
        seen.append(stage)
        return {'chapters':[{'start_index':0,'end_index':59,'theme':'一次完整骑行经历',
                             'experience_kind':'CYCLING','reason':'画面中连续展示了一段骑行活动'}]}
    route,audit=r.route(assets,observations,ask)
    assert len(route)==1
    assert audit['review_attempted'] is False
    assert seen==['S07X_PRODUCT_EPISODE_ROUTE']

def test_long_or_tiny_fragment_requests_semantic_review_not_forced_splitting():
    assert r.needs_review([{'start_index':0,'end_index':50},
                           {'start_index':51,'end_index':59}],60)
    assert r.needs_review([{'start_index':0,'end_index':16},
                           {'start_index':17,'end_index':31},
                           {'start_index':32,'end_index':42},
                           {'start_index':43,'end_index':55},
                           {'start_index':56,'end_index':59}],60)
    assert not r.needs_review([{'start_index':0,'end_index':59}],60)

def test_media_selector_locks_chapters_and_uses_exact_frame_observation_quotes():
    assets,facts,_=fixtures(n=4)
    wire=r.compile_wire(episodes(4),assets,facts)
    candidates=[]
    scene={'candidate_scene_clues':{}}
    for i,(aid,a) in enumerate(assets.items()):
        pid=f'P{i+1:03d}'
        fid=f'F{i+1:03d}'
        candidates.append({'candidate_id':pid,'asset_id':aid,'frame_id':a['frames'][0]['frame_id'],
                           'fact_ids':[fid]})
        text=f'这一张真实图片独立观察到的内容{i+1}'
        scene['candidate_scene_clues'][pid]=[{'scene_observation_id':f'FO:{pid}',
             'text':text,'asset_id':aid,'evidence_frame_ids':[a['frames'][0]['frame_id']],
             'supported_fact_ids':[fid],'provenance':'DEDICATED_PER_FRAME_OBSERVATION',
             'subject_role':'SPECIFIC_SUBJECT','visibility':'CLEAR',
             'prominence':'READABLE','occlusion':'NONE'}]
    def ask(stage,prompt,schema,context,evidence=()):
        assert stage=='S09B_PRODUCT_EPISODE_MEDIA_ONLY'
        return {'chapter_media':[{'chapter_id':'C01','hero_candidate_id':'P001',
                 'focus':'街区市集与摊位','focus_fact_ids':['F001'],
                 'media_choices':[{'candidate_id':'P001','reason':'raw model choice'}]},
                {'chapter_id':'C02','hero_candidate_id':'P003',
                 'focus':'花园里的树林与池塘','focus_fact_ids':['F003'],
                 'media_choices':[{'candidate_id':'P003','reason':'raw model choice'}]}]}
    completed,audit=r.select_media(wire,candidates,scene,ask,evidence=[])
    assert len(completed['chapters'])==2
    assert all(audit['frame_assessment_provenance'])
    assert len(completed['frame_assessments'])==4
    assert completed['chapters'][0]['focus']==wire['chapters'][0]['theme']
    assert completed['chapters'][0]['focus_fact_ids']==['F001']
    assert completed['chapters'][1]['focus_fact_ids']==['F003']
    assert audit['focus_updates'][0]['verified_cover_focus']=='街区市集与摊位'
    assert audit['focus_updates'][0]['episode_focus']=='城市集市与街区'
    assert completed['media_choices'][0]['reason']=='这一张真实图片独立观察到的内容1'
    a,_,hard=frame_selection.resolve_frame_selection(completed,candidates,facts,scene_clues=scene)
    assert not hard

def test_media_cannot_cross_episode_source_or_fabricate_new_image():
    assets,facts,_=fixtures(n=4)
    wire=r.compile_wire(episodes(4),assets,facts)
    c=[{'candidate_id':'P001','asset_id':'V001','frame_id':'segment-000-f0','fact_ids':['F001']},
       {'candidate_id':'P002','asset_id':'V003','frame_id':'segment-002-f0','fact_ids':['F003']}]
    scene={'candidate_scene_clues':{k['candidate_id']:[
        {'scene_observation_id':'FO:'+k['candidate_id'],'text':'可见实际主体',
         'asset_id':k['asset_id'],'evidence_frame_ids':[k['frame_id']],
         'supported_fact_ids':k['fact_ids'],'provenance':'DEDICATED_PER_FRAME_OBSERVATION',
         'subject_role':'SPECIFIC_SUBJECT','visibility':'CLEAR',
         'prominence':'READABLE','occlusion':'NONE'}] for k in c}}
    def wrong(stage,prompt,schema,context,evidence=()):
        return {'chapter_media':[{'chapter_id':'C01','hero_candidate_id':'P002',
                     'media_choices':[{'candidate_id':'P002','reason':'wrong chapter'}]},
                {'chapter_id':'C02','hero_candidate_id':'P001',
                     'media_choices':[{'candidate_id':'P001','reason':'wrong chapter'}]}]}
    with pytest.raises(ValueError):
        r.select_media(wire,c,scene,wrong,evidence=[])


def test_media_scoped_repair_preserves_good_chapter_and_only_resends_bad_images():
    assets,facts,_=fixtures(n=4)
    wire=r.compile_wire(episodes(4),assets,facts)
    candidates=[]
    scene={'candidate_scene_clues':{}}
    evidence=[]
    for i,(aid,asset) in enumerate(assets.items(),1):
        pid=f'P{i:03d}'
        fid=f'F{i:03d}'
        frame=asset['frames'][0]['frame_id']
        candidates.append({'candidate_id':pid,'asset_id':aid,
                           'frame_id':frame,'fact_ids':[fid]})
        scene['candidate_scene_clues'][pid]=[{
            'scene_observation_id':'FO:'+pid,'text':facts[fid]['text'],
            'asset_id':aid,'evidence_frame_ids':[frame],
            'supported_fact_ids':[fid],'provenance':'DEDICATED_PER_FRAME_OBSERVATION',
            'subject_role':'SPECIFIC_SUBJECT','visibility':'CLEAR',
            'prominence':'READABLE','occlusion':'NONE'}]
        evidence.append(object())
    bad={'chapter_media':[
        {'chapter_id':'C01','hero_candidate_id':'P003','focus':'不属于本章的花园主体',
         'focus_fact_ids':['F003'],
         'media_choices':[{'candidate_id':'P003','reason':'跨章借用'}]},
        {'chapter_id':'C02','hero_candidate_id':'P003','focus':'花园树林与池塘',
         'focus_fact_ids':['F003'],
         'media_choices':[{'candidate_id':'P003','reason':'合法封面'}]}]}
    repair={'chapter_media':[
        {'chapter_id':'C01','hero_candidate_id':'P001','focus':'市集摊位与行人',
         'focus_fact_ids':['F001'],
         'media_choices':[{'candidate_id':'P001','reason':'本章合法主题'}]}]}
    calls=[]
    def ask(stage,prompt,schema,context,evidence=()):
        calls.append((stage,len(evidence),context))
        return bad if len(calls)==1 else repair
    final,audit=r.select_media(wire,candidates,scene,ask,evidence=evidence,facts=facts)
    assert [row['hero_candidate_id'] for row in final['chapters']]==['P001','P003']
    assert [row['focus_fact_ids'] for row in final['chapters']]==[['F001'],['F003']]
    assert len(calls)==2
    assert calls[1][0]=='S09C_PRODUCT_EPISODE_MEDIA_SCOPED_REPAIR'
    assert calls[1][1]==2
    assert calls[1][2]['invalid_chapter_ids']==['C01']
    assert calls[1][2]['locked_valid_chapter_ids']==['C02']
    assert audit['media_contract_repairs'][0]['status']=='SCOPED_REPAIR_APPLIED'


def test_focus_must_derive_from_hero_not_other_unselected_scene():
    assets,facts,_=fixtures(n=2)
    wire=r.compile_wire([{'start_index':0,'end_index':1,'theme':'街区购物',
                          'experience_kind':'CITYWALK','reason':'街道和商铺事实构成主题'}],
                        assets,facts)
    candidates=[]
    clues={'candidate_scene_clues':{}}
    for i,(aid,a) in enumerate(assets.items(),1):
        pid=f'P{i:03d}'
        fid=f'F{i:03d}'
        fr=a['frames'][0]['frame_id']
        candidates.append({'candidate_id':pid,'asset_id':aid,'frame_id':fr,'fact_ids':[fid]})
        clues['candidate_scene_clues'][pid]=[{'scene_observation_id':'FO:'+pid,
            'text':'可见街区商铺','asset_id':aid,'evidence_frame_ids':[fr],
            'supported_fact_ids':[fid],'provenance':'DEDICATED_PER_FRAME_OBSERVATION',
            'subject_role':'SPECIFIC_SUBJECT','visibility':'CLEAR',
            'prominence':'READABLE','occlusion':'NONE'}]
    out={'chapter_media':[{'chapter_id':'C01','hero_candidate_id':'P001',
         'focus':'另一画面中的商铺','focus_fact_ids':['F002'],
         'media_choices':[{'candidate_id':'P001','reason':'封面事实一'},
                          {'candidate_id':'P002','reason':'补充事实二'}]}]}
    with pytest.raises(ValueError,match='FOCUS_NOT_DIRECTLY_SUPPORTED_BY_CHOSEN_IMAGES'):
        r.select_media(wire,candidates,clues,lambda *a,**kw: out,evidence=[],facts=facts)


def test_multiple_selected_images_preserve_episode_focus_not_just_cover_detail():
    assets,facts,_=fixtures(n=4)
    wire=r.compile_wire(episodes(4),assets,facts)
    candidates=[]
    clues={'candidate_scene_clues':{}}
    for i,(aid,a) in enumerate(assets.items(),1):
        pid=f'P{i:03d}'
        fid=f'F{i:03d}'
        fr=a['frames'][0]['frame_id']
        candidates.append({'candidate_id':pid,'asset_id':aid,'frame_id':fr,
                           'fact_ids':[fid]})
        clues['candidate_scene_clues'][pid]=[{
            'scene_observation_id':'FO:'+pid,'text':facts[fid]['text'],
            'asset_id':aid,'evidence_frame_ids':[fr],
            'supported_fact_ids':[fid],
            'provenance':'DEDICATED_PER_FRAME_OBSERVATION',
            'subject_role':'SPECIFIC_SUBJECT','visibility':'CLEAR',
            'prominence':'READABLE','occlusion':'NONE'}]
    raw={'chapter_media':[
        {'chapter_id':'C01','hero_candidate_id':'P001',
         'focus':'一处街边市场的摊位','focus_fact_ids':['F001'],
         'media_choices':[{'candidate_id':'P001','reason':'市场主体'},
                          {'candidate_id':'P002','reason':'街区补充'}]},
        {'chapter_id':'C02','hero_candidate_id':'P003',
         'focus':'公园池塘边的树林','focus_fact_ids':['F003'],
         'media_choices':[{'candidate_id':'P003','reason':'园林主体'},
                          {'candidate_id':'P004','reason':'小径补充'}]}
    ]}
    compiled,audit=r.select_media(
        wire,candidates,clues,lambda *args,**kwargs:raw,
        evidence=[object() for _ in candidates],facts=facts)
    assert [row['focus'] for row in compiled['chapters']] == [
        '城市集市与街区','树林公园里的池塘']
    assert compiled['chapters'][0]['focus_fact_ids']==['F001','F002']
    assert compiled['chapters'][1]['focus_fact_ids']==['F003','F004']
    assert audit['focus_updates'][0]['raw_model_cover_focus']=='一处街边市场的摊位'
    assert audit['focus_updates'][0]['verified_cover_focus']==facts['F001']['text']
    assert audit['focus_updates'][0]['focus_fallback']=='MODEL_FOCUS_NOT_ANCHORED_TO_HERO_FACT'
    assert audit['focus_updates'][0]['episode_focus']=='城市集市与街区'
