from diary_one_ci import chapter_story_outline as story


def fixture():
    assets={
      'V001':{'asset_id':'clip-A','sequence_index':0},
      'V002':{'asset_id':'clip-B','sequence_index':1},
      'V003':{'asset_id':'clip-C','sequence_index':2}}
    facts={
      'F001':{'asset_id':'V001','evidence_frame_ids':['clip-A-f0'],
              'text':'港口码头有木帆船','visual_reviewed':True},
      'F002':{'asset_id':'V002','evidence_frame_ids':['clip-B-f0'],
              'text':'城市市场卖水果','visual_reviewed':True},
      'F003':{'asset_id':'V003','evidence_frame_ids':['clip-C-f0'],
              'text':'港口边有建筑雕塑','visual_reviewed':True}}
    plan={'chapter_grouping':[
       {'episode_ids':['E01','E03']},
       {'episode_ids':['E02']}],
      'independent_episodes':[
       {'episode_id':'E01','theme':'港口码头','experience_kind':'CITYWALK','start_index':0,'end_index':0},
       {'episode_id':'E02','theme':'城市市场','experience_kind':'MARKET_SHOPPING','start_index':1,'end_index':1},
       {'episode_id':'E03','theme':'港口建筑','experience_kind':'CITYWALK','start_index':2,'end_index':2}]}
    chapters=[{'id':'C01','theme':'港口漫步',
       'media_choices':[{'asset_id':'V001','frame_id':'clip-A-f0','fact_ids':['F001']},
                        {'asset_id':'V003','frame_id':'clip-C-f0','fact_ids':['F003']}]},
       {'id':'C02','theme':'城市市集',
        'media_choices':[{'asset_id':'V002','frame_id':'clip-B-f0','fact_ids':['F002']}]}]
    return assets,facts,plan,chapters


def test_noncontiguous_episode_outlines_stay_in_same_chapter():
    assets,facts,plan,chapters=fixture()
    output=story.build(chapters,plan,assets,facts)
    assert len(output['C01']['experiences'])==2
    assert output['C01']['covered_episode_ids']==['E01','E03']
    assert [v['frame_id'] for e in output['C01']['experiences']
            for v in e['selected_visual_evidence']]==['clip-A-f0','clip-C-f0']
    assert len(story.writer_context(output)['C01']['verified_experiences'])==2


def test_unrepresented_episode_never_fabricates_a_claim():
    assets,facts,plan,chapters=fixture()
    chapters[0]['media_choices']=chapters[0]['media_choices'][:1]
    outline=story.build(chapters,plan,assets,facts)
    assert outline['C01']['unrepresented_episode_ids']==['E03']
    assert story.writer_context(outline)['C01']['verified_experiences'][0]['episode_id']=='E01'


def test_foreign_media_fact_fails_closed():
    assets,facts,plan,chapters=fixture()
    chapters[0]['media_choices'][0]['asset_id']='V999'
    try:story.build(chapters,plan,assets,facts)
    except ValueError as e:assert str(e)=='STORY_OUTLINE_UNKNOWN_SELECTED_ASSET'
    else:assert False
