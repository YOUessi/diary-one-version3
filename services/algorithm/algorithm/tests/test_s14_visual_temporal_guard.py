"""S14 rescue cannot turn a one-frame pan claim into a 'verified static fact'."""
from diary_one_ci import product_evidence as e


def input_example():
    text='镜头从对岸的高楼天际线平移至一处白色建筑。'
    fact={'F001':{'id':'F001','asset_id':'V001','text':text,
                  'evidence_frame_ids':['frame-0','frame-1']}}
    shown={'V001':{'frame-0':{'source_timestamp_ms':1000},
                   'frame-1':{'source_timestamp_ms':5000}}}
    item={'fact_id':'F001','decision':'KEEP','text':text,'corrections':[],
          'evidence_frame_ids':['frame-1'],'temporal_support':'STATE',
          'reason':'单张图片上可见这座建筑'}
    return fact,shown,{'items':[item]}


def test_recovery_rejects_single_frame_explicit_camera_pan():
    facts,shown,output=input_example()
    accepted,ledger=e.compile_visual(output,facts,shown,strict_static_transition=True)
    assert not accepted
    assert ledger[0]['status']=='UNVERIFIED'
    assert ledger[0]['reason']=='STATE_CANNOT_PROVE_EXPLICIT_CAMERA_TRANSITION'


def test_recovery_does_not_reject_true_static_location_or_multi_frame_change():
    facts,shown,output=input_example()
    output['items'][0]['text']='镜头从对岸的高楼天际线平移至一处白色建筑。'
    output['items'][0]['temporal_support']='CHANGE'
    output['items'][0]['evidence_frame_ids']=['frame-0','frame-1']
    accepted,ledger=e.compile_visual(output,facts,shown,strict_static_transition=True)
    assert list(accepted)==['F001']
    assert ledger[0]['status']=='VERIFIED'
    assert not e.explicit_temporal_camera_transition('镜头里有一座白色建筑。')
    assert not e.explicit_temporal_camera_transition('从画面左侧到右侧排列着几座建筑。')
    assert e.explicit_temporal_camera_transition('视角转向宽阔的十字路口。')


def test_legacy_S09A_contract_reproducible_without_new_strict_gate():
    facts,shown,output=input_example()
    accepted,_=e.compile_visual(output,facts,shown)
    assert list(accepted)==['F001']
