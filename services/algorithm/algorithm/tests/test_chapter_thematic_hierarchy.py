"""Content-first, repeat-location merge is allowed across source time ranges."""
from copy import deepcopy

import pytest

from diary_one_ci import chapter_theme_hierarchy as p
from diary_one_ci.product_editor import compile_structure_wire


def day(n=20):
    assets={};facts={};obs=[]
    for i in range(n):
        aid=f'V{i+1:03d}';fid=f'F{i+1:03d}';src=f'clip-{i:03d}'
        text=('海港标志性建筑与蓝色水面' if i<4 or i>=n-4 else
              '露天市场售卖手工首饰' if i<8 else
              '商业街内的店铺和咖啡座' if i<12 else
              '自然公园池塘里的植物')
        assets[aid]={'asset_id':src,'sequence_index':i,'original_duration_ms':10000,
             'frames':[{'frame_id':src+'-f0','source_timestamp_ms':2000}]}
        facts[fid]={'id':fid,'asset_id':aid,'source_asset_id':src,'visual_reviewed':True,
             'evidence_frame_ids':[src+'-f0'],'text':text}
        obs.append({'source_asset_id':src,'activity_code':'WALKING',
            'setting_code':'STREET','facts':[{'text':text}]})
    return assets,facts,obs


def spans(n=20):
    ends=[3,7,11,15,n-1]
    return [{'start_index':i*4,'end_index':end,
             'theme':x,'experience_kind':k,
             'reason':'独立视觉画面包含具有意义的连续场景与真实活动事实'}
            for i,(end,x,k) in enumerate(zip(ends,[
               '海港建筑','市集商品','商业街区','公园植物','海港建筑回顾'
            ],['CITYWALK','MARKET_SHOPPING','CITYWALK','GARDEN','CITYWALK']))]


def theme_output():
    return {'chapters':[
       {'title':'海港地标与建筑漫步','experience_kind':'CITYWALK',
        'episode_ids':['E01','E05'],'anchor_fact_ids':['F002','F019'],
        'reason':'同一海港地标在不同片段出现，合并不需要再开新章'},
       {'title':'露天市场摊位体验','experience_kind':'MARKET_SHOPPING',
        'episode_ids':['E02'],'anchor_fact_ids':['F005'],
        'reason':'市集摊位和手工首饰是一段独立购物经历'},
       {'title':'城市购物与咖啡馆','experience_kind':'CITYWALK',
        'episode_ids':['E03'],'anchor_fact_ids':['F010'],
        'reason':'市中心商铺和咖啡馆属于相对一致的商业环境'},
       {'title':'自然公园和池塘','experience_kind':'GARDEN',
        'episode_ids':['E04'],'anchor_fact_ids':['F013'],
        'reason':'树木与池塘形成不同于市区的自然体验'}
    ]}


def test_revisited_subject_merges_across_gap_but_all_facts_have_single_owner():
    a,f,o=day()
    stage=[]
    def ask(name,prompt,schema,context):
        stage.append(name)
        return ({'episodes':spans()} if name.startswith('S07T')
                else theme_output())
    wire,audit=p.plan(a,o,f,ask)
    assert stage==['S07T_THEMATIC_EPISODE_DISCOVERY','S07U_THEMATIC_CHAPTER_FUSION',
                   'S07V_THEMATIC_CHAPTER_COHERENCE_REVIEW']
    assert len(audit['independent_episodes'])==5
    assert len(wire['chapters'])==4
    assert set(wire['chapters'][0]['fact_ids'])==set(
        [f'F{x:03d}' for x in list(range(1,5))+list(range(17,21))])
    assert len({fid for c in wire['chapters'] for fid in c['fact_ids']})==20
    assert audit['chapter_grouping'][0]['episode_ids']==['E01','E05']
    assert audit['unassigned_verified_facts']==0
    compiled,moments,issues,coverage=compile_structure_wire(wire,f,a,5)
    assert len(compiled)==4 and moments==[] and issues==[]
    assert [len(c['fact_ids']) for c in compiled]==[8,4,4,4]


def test_repeat_location_only_may_remain_one_chapter():
    a,f,o=day()
    episodes=[{'start_index':0,'end_index':19,'theme':'同一体验',
              'experience_kind':'CITYWALK','reason':'所有画面始终指向同一个可回顾的经历'}]
    def ask(name,prompt,schema,context):
        if name.startswith('S07T'):return {'episodes':episodes}
        return {'chapters':[{'title':'同一天的一次完整体验',
            'experience_kind':'CITYWALK','episode_ids':['E01'],
            'anchor_fact_ids':['F001'],'reason':'真实视觉记录始终可以合理归入共同主题'}]}
    wire,audit=p.plan(a,o,f,ask)
    assert len(wire['chapters'])==1


def test_missing_last_source_repair_only_after_explicit_validation():
    a,f,o=day()
    bad=spans()
    bad[-1]['end_index']=18
    stages=[]
    def ask(name,prompt,schema,context):
        stages.append(name)
        if name=='S07T_THEMATIC_EPISODE_DISCOVERY':
            return {'episodes':bad}
        if name=='S07T_THEMATIC_EPISODE_INTERVAL_REPAIR':
            assert context['validation_error']=='EPISODE_PROPOSAL_INCOMPLETE_COVERAGE'
            return {'episodes':spans()}
        return theme_output()
    wire,audit=p.plan(a,o,f,ask)
    assert len(wire['chapters'])==4
    assert len(audit['repairs'])==1
    assert stages[1]=='S07T_THEMATIC_EPISODE_INTERVAL_REPAIR'


def test_disallow_duplicate_episodes_foreign_anchors_and_source_gaps():
    a,f,o=day()
    episodes=p.validate_episodes({'episodes':spans()},20)
    good=theme_output()
    for invalid in [
       {**good,'chapters':[{**good['chapters'][0],
                           'episode_ids':['E01','E05','E03']},
                          *good['chapters'][1:]]},
       {**good,'chapters':[{**good['chapters'][0],
                           'anchor_fact_ids':['F002','F009']},
                          *good['chapters'][1:]]},
       {**good,'chapters':good['chapters'][:-1]},
    ]:
        with pytest.raises(ValueError):
            p.validate_chapters(invalid,episodes,a,f,5)
    originals=deepcopy(episodes)
    with pytest.raises(ValueError):
        p.validate_episodes({'episodes':[{**spans()[0],'end_index':2},
                                         *spans()[1:]]},20)
    assert episodes==originals


def test_no_named_geography_or_timestamps_needed_for_source_fusion():
    a,f,o=day()
    for fact in f.values():
        fact['text']=fact['text'].replace('海港','湖畔').replace('商业街','展厅')
    def ask(name,prompt,schema,ctx):
        return {'episodes':spans()} if name.startswith('S07T') else theme_output()
    wire,audit=p.plan(a,o,f,ask)
    assert wire['chapters'][0]['fact_ids'][0]=='F001'
    assert 'F020' in wire['chapters'][0]['fact_ids']
    assert audit['time_basis']=='IMPORT_SEQUENCE_ONLY'



def test_coherence_reviewer_can_fix_mixed_content_without_forcing_chapter_count():
    a,f,o=day()
    mixed=theme_output()
    mixed['chapters'][1]['episode_ids']=['E02','E03']
    mixed['chapters'][1]['anchor_fact_ids']=['F005','F010']
    mixed['chapters']=mixed['chapters'][:2]+mixed['chapters'][3:]
    # Three valid but awkward chapters -> four semantically coherent.
    stages=[]
    def ask(stage,prompt,schema,ctx):
        stages.append(stage)
        if stage.startswith('S07T'):return {'episodes':spans()}
        return deepcopy(mixed) if stage=='S07U_THEMATIC_CHAPTER_FUSION' else theme_output()
    wire,audit=p.plan(a,o,f,ask)
    assert audit['semantic_coherence_review']['accepted'] is True
    assert audit['semantic_coherence_review']['changed'] is True
    assert len(wire['chapters'])==4
    assert set(fid for c in wire['chapters'] for fid in c['fact_ids'])==set(f)
    assert len(stages)==3


def test_invalid_semantic_review_is_ignored_without_losing_original_evidence():
    a,f,o=day()
    invalid=deepcopy(theme_output())
    invalid['chapters'][2]['episode_ids']=['E01']
    def ask(stage,prompt,schema,ctx):
        if stage.startswith('S07T'):return {'episodes':spans()}
        return invalid if stage=='S07V_THEMATIC_CHAPTER_COHERENCE_REVIEW' else theme_output()
    wire,audit=p.plan(a,o,f,ask)
    assert audit['semantic_coherence_review']['status']=='REJECTED_INVALID_REVIEW'
    assert len(wire['chapters'])==4
    assert set(fid for c in wire['chapters'] for fid in c['fact_ids'])==set(f)


def test_persistent_shopping_and_park_in_one_chapter_triggers_scoped_replan():
    a,f,o=day()
    episodes=p.validate_episodes({'episodes':spans()},20)
    mixed={'chapters':[
       {**theme_output()['chapters'][0]},
       {'title':'商场购物与公园自然植物合成一章','experience_kind':'CITYWALK',
        'episode_ids':['E02','E04'],'anchor_fact_ids':['F005','F013'],
        'reason':'两个内容确实不同但错误地只凭同一天步行硬合并'},
       {**theme_output()['chapters'][2]}
    ]}
    assert len(p.thematic_coherence_conflicts(
        p.validate_chapters(mixed,episodes,a,f,5),episodes))==1
    stages=[]
    def ask(stage,prompt,schema,ctx):
        stages.append(stage)
        if stage.startswith('S07T'):return {'episodes':spans()}
        if stage=='S07W_THEMATIC_COHERENCE_CORRECTION':
            assert len(ctx['mixed_theme_chapters'])==1
            return theme_output()
        return mixed
    wire,audit=p.plan(a,o,f,ask)
    assert len(wire['chapters'])==4
    assert audit['semantic_coherence_review']['status']=='APPLIED_COHERENT_REPLAN'
    assert 'S07W_THEMATIC_COHERENCE_CORRECTION' in stages
    assert not audit['semantic_coherence_review']['conflicts_remaining']


def test_sixteen_or_more_provisional_episodes_are_not_forced_to_five():
    n=18
    episodes=[{'start_index':i,'end_index':i,'theme':'一个可验证的微经历',
        'experience_kind':'CITYWALK','reason':'具体场景与真实视觉观察都有来源'}
        for i in range(n)]
    valid=p.validate_episodes({'episodes':episodes},n)
    assert len(valid)==18
    assert valid[-1]['end_index']==17


def test_valid_five_fact_focus_is_bounded_without_deleting_any_episode():
    a,f,o=day()
    eps=p.validate_episodes({'episodes':spans()},20)
    proposal=theme_output()
    proposal['chapters'][0]['anchor_fact_ids']=[
        'F001','F002','F003','F017','F020']
    fixed,trace=p.normalize_only_excess_visual_anchors(
        proposal,eps,a,f,5)
    assert len(trace)==1
    assert len(fixed['chapters'][0]['anchor_fact_ids'])==4
    assert 'F001' in fixed['chapters'][0]['anchor_fact_ids']
    assert 'F020' in fixed['chapters'][0]['anchor_fact_ids']
    assert p.validate_chapters(fixed,eps,a,f,5)
    assert proposal['chapters'][0]['anchor_fact_ids']==[
        'F001','F002','F003','F017','F020']


def test_nonverified_and_foreign_fact_cannot_be_recovered_by_trim():
    a,f,o=day()
    eps=p.validate_episodes({'episodes':spans()},20)
    proposal=theme_output()
    proposal['chapters'][0]['anchor_fact_ids']=[
        'F001','F002','F003','F017','F006']
    with pytest.raises(ValueError,match='INVALID_EXCESS_ANCHOR_OWNERSHIP'):
        p.normalize_only_excess_visual_anchors(proposal,eps,a,f,5)


def test_complete_overflow_can_merge_source_groups_without_losing_any_experience():
    a,f,o=day()
    episodes=p.validate_episodes({'episodes':spans()},20)
    # A structured but over-cap original with all five Episodes preserved.
    draft={'chapters':[]}
    for k in range(5):
        draft['chapters'].append({'title':f'完整可见体验组{k+1}',
             'experience_kind':'CITYWALK',
             'episode_ids':[f'E{k+1:02d}'],
             'anchor_fact_ids':[f'F{k*4+1:03d}'],
             'reason':'真实视觉事实支持原来单独分开的观察阶段'})
    seen=[]
    def ask(stage,prompt,schema,context):
        seen.append(stage)
        assert context['source_chapter_count']==5
        assert len(context['required_episode_ids'])==5
        return {'can_safely_merge':True,
            'merge_groups':[{'chapter_indices':[0,4],
                'title':'两端属于同一海港城市漫步体验',
                'experience_kind':'CITYWALK',
                'reason':'两组实际看到的海港地标相同且均有视觉证据可以合理合并',
                'evidence_episode_ids':['E01','E05']}]}
    compact,audit=p.compact_overflow_with_source_safe_merge(
        draft,episodes,a,f,4,ask,{'chapter_limit':4})
    assert len(compact['chapters'])==4
    assert set(e for c in compact['chapters'] for e in c['episode_ids'])=={
        'E01','E02','E03','E04','E05'}
    assert compact['chapters'][0]['episode_ids']==['E01','E05']
    assert audit['all_original_episode_ids_preserved']
    assert audit['merged_existing_chapter_groups'][0]['source_indices']==[0,4]
    assert p.validate_chapters(compact,episodes,a,f,4)
    assert draft['chapters'][0]['episode_ids']==['E01']
    assert seen==['S07U_SAFE_OVERFLOW_MERGE_ONLY']


def test_overflow_merge_fails_closed_when_model_has_no_supported_merge():
    a,f,o=day()
    episodes=p.validate_episodes({'episodes':spans()},20)
    draft={'chapters':[{'title':f'独立场景和人物体验{k}',
        'experience_kind':'CITYWALK','episode_ids':[f'E{k+1:02d}'],
        'anchor_fact_ids':[f'F{k*4+1:03d}'],
        'reason':'不同的真实活动具有独立视觉图像事实'}
        for k in range(5)]}
    def refuse(stage,prompt,schema,ctx):
        return {'can_safely_merge':False,'merge_groups':[]}
    with pytest.raises(ValueError,match='NO_EVIDENCE_BACKED_OVERFLOW_MERGE'):
        p.compact_overflow_with_source_safe_merge(
            draft,episodes,a,f,4,refuse,{'chapter_limit':4})
    def foreign(stage,prompt,schema,ctx):
        return {'can_safely_merge':True,'merge_groups':[{
            'chapter_indices':[0,4],'title':'街头漫步统一体验',
            'experience_kind':'CITYWALK',
            'reason':'虽然有各自视觉描述但没有证明它们相关',
            'evidence_episode_ids':['E01','E02']}]}
    with pytest.raises(ValueError,match='MERGE_CITED_FOREIGN_EPISODE'):
        p.compact_overflow_with_source_safe_merge(
            draft,episodes,a,f,4,foreign,{'chapter_limit':4})


def test_complete_source_episodes_must_exist_before_overflow_compaction():
    a,f,o=day()
    episodes=p.validate_episodes({'episodes':spans()},20)
    draft={'chapters':[{'title':f'体验{k}',
        'experience_kind':'CITYWALK','episode_ids':[f'E{k+1:02d}'],
        'anchor_fact_ids':[f'F{k*4+1:03d}'],
        'reason':'图像包含具体活动的真实来源证据'}
        for k in range(4)]}
    with pytest.raises(ValueError,match='INVALID_INITIAL_OVERFLOW_BOUNDS'):
        p.compact_overflow_with_source_safe_merge(
            draft,episodes,a,f,4,lambda *x: None,{'chapter_limit':4})
