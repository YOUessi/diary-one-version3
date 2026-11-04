"""Real lived experience never equals an explicitly identified source-video endcard."""
from copy import deepcopy

import pytest
from diary_one_ci import source_content_gate as gate


def case(n=10):
    assets={}
    obs=[]
    facts={}
    for i in range(n):
        aid=f'V{i+1:03d}';sid=f'clip-{i:03d}'
        text=('画面为视频结尾的推广界面（End Card），包含Instagram、Facebook图标及'
              '账号名，以及KEEP WATCHING、Subscribe等文字提示。'
              if i==n-1 else '街道旁的实体橱窗里有手工商品和人群')
        assets[aid]={'asset_id':sid,'sequence_index':i,
                     'frames':[{'frame_id':sid+'-f0'}]}
        obs.append({'asset_id':aid,'source_asset_id':sid,'activity_code':'OBSERVING',
            'facts':[{'text':text,'evidence_frame_ids':[sid+'-f0']}],
            'setting_code':'STREET'})
        facts[f'F{i+1:03d}']={'asset_id':aid,'source_asset_id':sid,
             'text':text,'evidence_frame_ids':[sid+'-f0'],'visual_reviewed':True}
    return assets,obs,facts


def test_reject_verified_terminal_endcard_but_preserve_raw_observation():
    assets,obs,facts=case()
    before=deepcopy((assets,obs,facts))
    decision=gate.evaluate(assets,obs,facts)
    assert decision['excluded_asset_ids']==['V010']
    assert decision['exclusion_count']==1
    assert decision['decisions'][0]['evidence_frame_ids']==['clip-009-f0']
    scoped,newobs,eligible,idxmap=gate.editorial_scope(assets,obs,facts,decision)
    assert len(scoped)==9 and 'F010' not in scoped
    assert len(eligible)==9 and list(idxmap)==list(range(9))
    assert newobs[-1]['facts']==[]
    assert obs[-1]['facts']==before[1][-1]['facts']
    assert facts==before[2] and assets==before[0]


def test_real_street_advertisements_are_not_erased_even_with_subscribe_text():
    assets,obs,facts=case()
    obs[-1]['facts'][0]['text']='人行道旁有广告牌写着Subscribe，旁边是售卖旅游纪念品的真实店铺。'
    facts['F010']['text']=obs[-1]['facts'][0]['text']
    result=gate.evaluate(assets,obs,facts)
    assert result['excluded_asset_ids']==[] and result['decisions']==[]


def test_endcard_early_is_review_not_auto_deleted():
    assets,obs,facts=case(40)
    copied=obs[-1]['facts'][0]['text']
    obs[-1]['facts'][0]['text']='街边真实餐馆外墙'
    facts['F040']['text']=obs[-1]['facts'][0]['text']
    obs[5]['facts'][0]['text']=copied
    facts['F006']['text']=copied
    decision=gate.evaluate(assets,obs,facts)
    assert decision['excluded_asset_ids']==[]
    assert decision['review_required_asset_ids']==['V006']


def test_weak_outro_word_without_multiple_cta_is_review_not_exclusion():
    assets,obs,facts=case()
    obs[-1]['facts'][0]['text']='这是视频结尾的画面，但是只是普通海滨步道。'
    facts['F010']['text']=obs[-1]['facts'][0]['text']
    decision=gate.evaluate(assets,obs,facts)
    assert not decision['excluded_asset_ids']
    assert decision['review_required_asset_ids']==['V010']


def test_frameless_fact_never_promoted_by_gate():
    assets,obs,facts=case()
    obs[-1]['facts']=[]
    facts['F010']['visual_reviewed']=False
    d=gate.evaluate(assets,obs,facts)
    assert d['excluded_asset_ids']==[]


def test_middle_exclusion_reindexes_only_editorial_scope():
    assets,obs,facts=case(10)
    msg=obs[-1]['facts'][0]['text']
    obs[5]['facts'][0]['text']=msg
    facts['F006']['text']=msg
    # Gate does not exclude middle assets automatically; the helper supports
    # an externally verified exclusion when VLM later confirms it.
    forced={'excluded_asset_ids':['V006']}
    filtered,_,eligible,idxmap=gate.editorial_scope(assets,obs,facts,forced)
    assert eligible['V007']['sequence_index']==5
    assert idxmap[5]==6
    assert 'F006' not in filtered
    assert 'F010' in filtered
