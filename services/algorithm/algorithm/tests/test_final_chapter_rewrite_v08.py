"""No rejected claim can become public without a second image-bound verdict."""
from pathlib import Path
from copy import deepcopy

from diary_one_ci import product_editor as p


def _memory():
    fact={'id':'F001','asset_id':'V001','text':'渡轮在水面上，岸边有行人。',
          'visual_reviewed':True,'support_grade':'SUPPORTED',
          'evidence_frame_ids':['frame-1']}
    return {'id':'C01','kind':'CHAPTER','theme':'海港与渡轮',
            'fact_ids':['F001'],'facts':[fact],
            'selected_title_fact_ids':['F001'],'evidence_groups':[
                {'asset_id':'V001','facts':[fact]}],
            'copy_contract':{'type_label':'章节','length_policy':'按内容自然成文'}}


def _packet():
    return {'reviewed':{}, 'final_verification_output':{'items':[{
        'id':'C01','title_supported':True,'title_evaluated':True,
        'title_reason':'可见主体清楚',
        'sentences':[{'source_index':0,'supported':False,
                      'reason':'方向被实际图片证据否定'}]}]},
        'final_verification_ledger':[{'id':'C01','status':'BLOCKED'}],
        'final_verification_terminal_failure':False}


def _response():
    return {'items':[{'id':'C01','title':'海港渡轮',
                      'title_fact_ids':['F001'],'decision':'PUBLISH',
                      'reason':'删掉错误方向','sentences':[
                          {'text':'渡轮在水面上，岸边有行人。','fact_ids':['F001']}],
                      'voice_issues':[]}]}


def test_rejected_sentence_requires_a_new_independent_verifier(monkeypatch):
    packet=_packet()
    verified=[]
    def verify(child,items,stage,*,ask,time_basis,stage_runs,evidence=(),evidence_scope=None):
        verified.append({'stage':stage,'n_images':len(evidence),
                         'copy':child['reviewed']['C01']['story']})
        child['reviewed'].clear()
        child['final_verification_ledger']=[{'id':'C01','status':'BLOCKED'}]
    monkeypatch.setattr(p,'verify_final_chapter_copy',verify)
    calls=[]
    def ask(stage,prompt,schema,context,*,evidence=()):
        calls.append((stage,len(evidence)))
        return _response()
    p.recover_rejected_final_chapters(packet,[_memory()],'S13_FINAL_CHAPTER_REWRITE',
        ask=ask,time_basis='IMPORT_SEQUENCE_ONLY',stage_runs=[],
        evidence=[({'asset_id':'V001'},{'frame_id':'frame-1'},Path('/does/not/exist'))])
    assert calls==[('S13_FINAL_CHAPTER_REWRITE_C01',1)]
    assert verified and verified[0]['n_images']==1
    assert packet['reviewed']=={}
    assert packet['final_chapter_repair_ledger'][0]['status']=='BLOCKED'
    assert packet['final_chapter_repair_ledger'][0]['reason']=='REWRITE_FAILED_INDEPENDENT_IMAGE_VERIFICATION'


def test_no_approved_image_means_no_rewrite_call():
    packet=_packet()
    calls=[]
    p.recover_rejected_final_chapters(packet,[_memory()],'S13_FINAL_CHAPTER_REWRITE',
        ask=lambda *args,**kwargs:calls.append(args),time_basis='IMPORT_SEQUENCE_ONLY',
        stage_runs=[],evidence=[])
    assert not calls and packet['reviewed']=={}
    assert packet['final_chapter_repair_ledger'][0]['reason']=='NO_ACTUAL_SOURCE_IMAGES'


def test_do_not_repair_when_no_negative_verdict():
    packet=_packet()
    packet['final_verification_output']['items'][0]['sentences'][0]['supported']=True
    packet['reviewed']['C01']={'title':'海港渡轮'}
    calls=[]
    p.recover_rejected_final_chapters(packet,[_memory()],'S13_FINAL_CHAPTER_REWRITE',
        ask=lambda *args,**kwargs:calls.append(args),time_basis='IMPORT_SEQUENCE_ONLY',
        stage_runs=[],evidence=[])
    assert calls==[]
    assert packet['final_chapter_repair_ledger']==[]
