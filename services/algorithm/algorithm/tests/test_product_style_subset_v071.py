"""Bounded style editing can omit redundancy without changing sentence ownership."""
from copy import deepcopy

import pytest
from diary_one_ci import product_editor as p
from final_copy_test_support import write_and_review_with_test_images
from test_product_editor import scripted_final_verdict


TEXTS=['双手握住车把，沿道路前行。','水渠里落下一道细细的水流。','戴着露指手套的手稳在车把上，前方是树林。']


def memory():
    facts={f'F00{i+1}':dict(id=f'F00{i+1}',asset_id=f'V00{i+1}',text=text,
        evidence_frame_ids=[f'frame-{i}'],visual_reviewed=True,temporal_support='STATE',
        support_grade='STRONG',frame_pts_ms=[0]) for i,text in enumerate(TEXTS)}
    return p.memory_specs([dict(id='C01',theme='骑行',fact_ids=list(facts))],[],facts)[0]


def row():
    return dict(id='C01',title='路旁的水渠',title_fact_ids=['F002'],decision='PUBLISH',reason='Synthetic checked copy',
        voice_issues=[],sentences=[dict(text=t,fact_ids=[f'F00{i+1}'],source_index=i) for i,t in enumerate(TEXTS)])


def polish(mode='subset'):
    m=memory();raw=row();prior,_=p.compile_copy({'items':[raw]},[m],review=True)
    packet={'reviewed':prior,'copy_response_normalizations':[],'validated_narrative_briefs':{
        'C01':{'narrative_details':[dict(fact_id='F002',evidence_quote=TEXTS[1],role='MAIN')]}}}
    before=deepcopy(prior);calls=[]
    def ask(stage,prompt,schema,context,**kwargs):
        calls.append(context)
        result=deepcopy(raw)
        result['sentences']=[result['sentences'][1],result['sentences'][2]]
        result['sentences'][1]['text']='前方是树林。'
        if mode=='empty':result['sentences']=[]
        elif mode=='reverse':result['sentences'].reverse()
        elif mode=='duplicate':result['sentences'][1]=deepcopy(result['sentences'][0])
        elif mode=='foreign_index':result['sentences'][0]['source_index']=99
        elif mode=='cross_asset_refs':result['sentences'][0]['fact_ids']=['F001']
        elif mode=='merged_refs':result['sentences'][0]['fact_ids']=['F001','F002']
        elif mode=='extra_sentence':result['sentences'].append(dict(source_index=3,text='新的场景',fact_ids=['F003']))
        elif mode=='unchanged':result=deepcopy(raw)
        return {'items':[result]}
    p.polish_final_chapter_style(packet,[m],'STYLE',ask=ask,time_basis='UNKNOWN',stage_runs=[])
    return packet,before,calls


def test_subset_removes_whole_redundant_sentence_preserves_order_refs_and_audits_omission():
    packet,before,calls=polish()
    assert before['C01']['style_flags']==['POV_BODY_REPETITION']
    assert packet['reviewed']['C01']['story']==TEXTS[1]+'前方是树林。'
    assert [s['fact_ids'] for s in packet['reviewed']['C01']['sentences']]==[['F002'],['F003']]
    assert packet['reviewed']['C01']['title']==before['C01']['title']
    ledger=packet['final_style_ledger'][0]
    assert ledger['retained_source_indices']==[1,2] and ledger['omitted_source_indices']==[0]
    assert calls[0]['items'][0]['repeated_viewpoint_source_indices']==[0,2]
    assert calls[0]['items'][0]['narrative_details'][0]['role']=='MAIN'


@pytest.mark.parametrize('mode',['empty','reverse','duplicate','foreign_index','cross_asset_refs','merged_refs','extra_sentence'])
def test_bad_subset_or_cross_source_edit_keeps_previously_reviewed_copy(mode):
    packet,before,_=polish(mode)
    assert packet['reviewed']==before
    assert packet['final_style_ledger'][0]['status']=='RETAINED_PRIOR_REVIEWED_COPY'


def test_useful_repeated_actions_are_not_automatically_deleted():
    packet,before,_=polish('unchanged')
    assert packet['reviewed']==before
    assert packet['final_style_ledger'][0]['status']=='RETAINED_PRIOR_REVIEWED_COPY'


@pytest.mark.parametrize('texts', [['双手握住车把。'],['车把上系着一只铃铛。','手臂上有彩色袖套。'],
    ['抬起手臂调整相机。','手臂缓缓落下。'],['村口有一辆自行车。','骑车经过水渠。']])
def test_one_grip_or_unrelated_gear_and_body_details_are_not_repetition(texts):
    assert len(p.repeated_viewpoint_context([dict(text=t) for t in texts]))<2


def test_repetition_uses_one_existing_style_call_and_final_image_checks():
    m=memory();raw=row();calls=[]
    def ask(stage,prompt,schema,context,**kwargs):
        calls.append(stage)
        if stage=='WRITE_NARRATIVE_BRIEF':return {'items':[]}
        if stage=='WRITE':return {'items':[dict(id='C01',title=raw['title'],story=''.join(TEXTS))]}
        if stage=='REVIEW':return {'items':[deepcopy(raw)]}
        if stage=='REPAIR_FINAL_STYLE':
            result=deepcopy(raw);result['sentences']=[result['sentences'][1]]
            return {'items':[result]}
        if stage.startswith('REVIEW_FINAL_VERIFY'):return scripted_final_verdict(context)
        raise AssertionError('Unnecessary factual repair stage: '+stage)
    packet=write_and_review_with_test_images([m],('WRITE','REVIEW','REPAIR'),ask=ask,
        time_basis='UNKNOWN',stage_runs=[])
    assert calls.count('REPAIR_FINAL_STYLE')==1 and 'REPAIR' not in calls and 'REPAIR_VERIFY' not in calls
    assert packet['reviewed']['C01']['story']==TEXTS[1]
    assert packet['final_verification_input']['reused_exact_approved_claim_ids']
    assert any(h['final_verification_input']['actual_images_attached'] for h in packet['final_verification_history'])
