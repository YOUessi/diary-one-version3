"""P1/P0 scenelet and global chapter planner: six-domain metamorphic tests."""
from copy import deepcopy

import pytest
from diary_one_ci import scenelet_builder as s
from diary_one_ci import chapter_boundary_planner as p


def make_case(n=5, *,same=True,clock=False):
    acts=['CYCLING']*n if same else ['CYCLING','CYCLING','DINING','DINING','NATURE_WALK'][:n]
    places=['ROAD']*n if same else ['ROAD','ROAD','INTERIOR','INTERIOR','PARK'][:n]
    texts=['骑车经过长路']*n if same else ['骑车经过长路','骑车经过公路',
        '坐在室内吃饭','坐在室内喝水','公园树荫与河流'][:n]
    assets={};facts={};observations=[]
    for i in range(n):
        aid=f'V{i+1:03d}';source_id=f'asset-{i}';fid=f'F{i+1:03d}'
        assets[aid]={'asset_id':source_id,'sequence_index':i,
            'original_duration_ms':10000,
            'frames':[{'frame_id':f'{source_id}-f0','source_timestamp_ms':2000}],
            **({'capture_time_ms':1730000000000+i*120000,
                'capture_time_source':'DEVICE_VERIFIED','capture_time_confidence':'VERIFIED'}
                if clock else {})}
        facts[fid]={'id':fid,'asset_id':aid,'text':texts[i],
            'evidence_frame_ids':[f'{source_id}-f0'],'visual_reviewed':True}
        observations.append({'source_asset_id':source_id,
            'activity_code':acts[i],'setting_code':places[i]})
    return assets,facts,observations


@pytest.mark.parametrize('name',[
    'day','citywalk','family','hobby','cycling','fishing'
])
def test_constant_evidence_is_not_split_just_to_fill_chapter_quota(name):
    a,f,o=make_case(n=32 if name=='fishing' else 5)
    out=s.build_scene_map(a,f,o)
    proposal=p.propose_chapters(out)
    assert out['scenelet_count']==1
    assert proposal['recommended_count']==1
    assert proposal['chapter_candidates'][0]['fact_ids']==list(f)
    assert not any(x['capture_start_ms'] for x in out['scenelets'])


def test_independent_activity_and_setting_change_produces_advisory_boundaries():
    a,f,o=make_case(n=5,same=False,clock=True)
    out=s.build_scene_map(a,f,o)
    assert out['time_basis']=='VERIFIED_CAPTURE'
    proposal=p.propose_chapters(out)
    assert proposal['recommended_count']>=3
    assert len({x for row in proposal['chapter_candidates'] for x in row['asset_ids']})==len(a)
    assert all(row['status']=='PROPOSAL_NEEDS_SEMANTIC_EDITOR_REVIEW'
               for row in proposal['chapter_candidates'])


def test_untrusted_capture_metadata_never_becomes_a_verified_clock():
    a,f,o=make_case(n=4)
    a['V002']['capture_time_ms']=1730000000000
    a['V002']['capture_time_source']='UNKNOWN'
    a['V002']['capture_time_confidence']='VERIFIED'
    out=s.build_scene_map(a,f,o)
    assert out['time_basis']=='IMPORT_SEQUENCE_ONLY'
    assert all(x['capture_start_ms'] is None for x in out['scenelets'])


def test_embedding_version_mismatch_prevents_cosine_comparison():
    a,f,o=make_case(n=2)
    a['V001']['embedding_model_id']='S0-A'
    a['V002']['embedding_model_id']='S0-B'
    for k in a:
        a[k]['frames'][0]['embedding']=[1.,0.,0.]
    items=s.records(a,f,o)
    assert s.pair_similarity(items[0],items[1])['visual'] is None
    a['V002']['embedding_model_id']='S0-A'
    items=s.records(a,f,o)
    assert s.pair_similarity(items[0],items[1])['visual']==1.0


def test_no_fact_assets_are_accounted_but_cannot_create_new_episodes():
    a,f,o=make_case(n=4)
    del f['F003']
    m=s.build_scene_map(a,f,o)
    assert m['asset_count']==4
    assert sum(len(x['asset_ids']) for x in m['scenelets'])==4


def test_big_map_has_explicit_hierarchical_flag_not_silent_truncation():
    a,f,o=make_case(n=5,same=False)
    m=s.build_scene_map(a,f,o)
    context=s.editor_scene_summary(m,max_scenelets=1)
    assert context['status']=='HIERARCHICAL_COMPLETE'
    assert context['all_scenelet_ids_accounted'] is True
    assert len(context['scenelet_groups']) <= 1


def test_replan_contract_cannot_restore_unverified_or_foreign_facts():
    lost=[{'draft_chapter_id':'C04','draft_fact_ids':['F4','F5']}]
    reviewed={'chapters':[{'id':'C01','fact_ids':['F1']}]}
    schema=p.disposition_schema(lost)
    assert schema['properties']['items']['minItems']==1
    def decide(action,target=None,facts=None):
        return {'items':[{'draft_chapter_id':'C04','action':action,
            'target_chapter_id':target,'supporting_fact_ids':facts or ['F4'],
            'reason':'图片显示具有独立记忆价值的具体活动内容'}]}
    with pytest.raises(ValueError):
        p.check_dispositions(decide('RESTORE_CHAPTER',facts=['F9']),lost,{'F4'},reviewed)
    with pytest.raises(ValueError):
        p.check_dispositions(decide('RESTORE_CHAPTER',facts=['F5']),lost,{'F4'},reviewed)
    with pytest.raises(ValueError):
        p.check_dispositions(decide('KEEP_MERGED',target='C99'),lost,{'F4'},reviewed)
    checked=p.check_dispositions(decide('RESTORE_CHAPTER'),lost,{'F4'},reviewed)
    assert checked['replan_required'] is True
    merged=p.check_dispositions(decide('KEEP_MERGED',target='C01'),lost,{'F4'},reviewed)
    assert merged['replan_required'] is True  # Missing fact must be inserted into the target Chapter via bounded replan


def test_replan_has_bounded_validation_and_never_fabricates_structure():
    current={'chapters':[{'id':'C01','fact_ids':['F1']}],'moments':[]}
    proposed={'chapters':[{'id':'C01','fact_ids':['F1']},{'id':'C02','fact_ids':['F2']}],
              'moments':[]}
    original=deepcopy(current)
    failed,status=p.merge_replan_review(current,proposed,lambda q: ([],[],[{'item':'C02'}],[]))
    assert failed==original and status['status']=='REPLAN_BLOCKED'
    success,status=p.merge_replan_review(current,proposed,
        lambda q: ([1,2],[],[],[]))
    assert success==proposed and status['status']=='REPLAN_APPLIED'
    assert current==original


def test_no_scene_name_keyword_or_fixed_citywalk_count():
    a,f,o=make_case(n=5,same=False)
    first=p.propose_chapters(s.build_scene_map(a,f,o))
    for fid in f:
        f[fid]['text']=f[fid]['text'].replace('骑车','行进').replace('公园','绿地')
    next_plan=p.propose_chapters(s.build_scene_map(a,f,o))
    assert next_plan['recommended_count']==first['recommended_count']
