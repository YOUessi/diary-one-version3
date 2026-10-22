"""Recorded title failure + synthetic visual verdicts; no model-quality gold."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from diary_one_ci import product_editor as p
from diary_one_ci.x02 import X02CallAttemptLimitReached
from final_copy_test_support import bound_test_images, write_and_review_with_test_images
from test_product_editor import scripted_final_verdict


def fixture():
    return json.loads((Path(__file__).parent/'fixtures/product_r55_title_rejected_valid_body.json').read_text())


def test_title_scope_requires_the_selected_exact_frame_not_just_the_same_video():
    memory = fixture()['memory']
    facts = {f['id']: f for f in memory['facts']}
    chapter = {**memory, 'media_choices': [
        {'asset_id': 'V002', 'frame_id': 'asset-1-f0', 'fact_ids': ['F002', 'F003', 'F001']}]}
    # F003 is only visible at f2; F001 belongs to another source.
    spec = p.memory_specs([chapter], [], facts)[0]
    assert spec['selected_title_fact_ids'] == ['F002']
    assert spec['fact_ids'] == memory['fact_ids']
    assert len(spec['facts']) == len(facts)


def exercise(mode='accept'):
    f=fixture();m=f['memory'];raw=f['row'];calls=[]
    if mode in ('selected', 'unselected'):
        m['selected_title_fact_ids'] = raw['sentences'][0]['fact_ids']
    elif mode == 'no_selected':
        m['selected_title_fact_ids'] = []
    prior,_=p.compile_copy({'items':[raw]},[m],review=True)
    packet={'reviewed':prior,'copy_response_normalizations':[]}
    def ask(stage,prompt,schema,context,**kwargs):
        calls.append((stage,deepcopy(context),bool(kwargs.get('evidence'))))
        if stage=='PATCH_C01':
            if mode=='budget':raise X02CallAttemptLimitReached('Synthetic budget exhausted')
            assert context['rejection_reason']==f['verdict']['title_reason']
            result=dict(id='C01',source_index=0,title='林间骑行与道路',title_fact_ids=[raw['sentences'][0]['fact_ids'][0]])
            if mode in ('selected', 'unselected'):
                assert all(set(s['fact_ids']) <= set(m['selected_title_fact_ids']) for s in context['supported_sentences'])
            if mode == 'unselected':
                result.update(source_index=1, title_fact_ids=raw['sentences'][1]['fact_ids'])
            if mode=='foreign':result['title_fact_ids']=['F999']
            elif mode=='foreign_sentence':result['title_fact_ids']=raw['sentences'][1]['fact_ids']
            elif mode=='invalid_source':result['source_index']=999
            elif mode=='recorded_r56':
                recorded=json.loads((Path(__file__).parent/'fixtures/product_r56_title_repair_cross_clip.json').read_text())
                result={**recorded['raw_title_patch'],'source_index':0}
            elif mode=='duplicate':result['title_fact_ids']*=2
            elif mode=='extra_body':result['sentences']=raw['sentences']
            elif mode=='self_approval':result['supported']=True
            return result
        verdict=scripted_final_verdict(context)
        for c,r in zip(context['claims'],verdict['claims']):
            if stage.startswith('INITIAL') and c['field']=='TITLE':r.update(supported=False,reason=f['verdict']['title_reason'])
            if mode=='no_body' and c['field']=='SENTENCE':r.update(supported=False,reason='Injected no approved body')
            if mode=='deny' and stage.startswith('PATCH_VERIFY'):r.update(supported=False,reason='Independent title denial')
        return verdict
    with bound_test_images([m]) as (items,evidence,scope):
        p.verify_final_chapter_copy(packet,items,'INITIAL',ask=ask,time_basis='IMPORT_ORDER_ONLY',
            stage_runs=[],evidence=evidence,evidence_scope=scope)
        assert not packet['reviewed']
        if mode=='terminal':packet['final_verification_terminal_failure']=True
        if mode=='changed_pixels':
            fact=next(f for f in items[0]['facts'] if f['id']==raw['sentences'][0]['fact_ids'][0])
            path=next(path for a,frame,path in evidence if a['asset_id']==fact['asset_id'] and frame['frame_id'] in fact['evidence_frame_ids'])
            Path(path).write_bytes(b'changed-image')
        before=len(calls)
        p.repair_final_titles(packet,items,'PATCH',ask=ask,time_basis='IMPORT_ORDER_ONLY',
            stage_runs=[],evidence=evidence,evidence_scope=scope)
        after=len(calls)
        p.repair_final_titles(packet,items,'PATCH',ask=ask,time_basis='IMPORT_ORDER_ONLY',
            stage_runs=[],evidence=evidence,evidence_scope=scope)
        assert len(calls)==after
    return packet,calls[before:],raw


def test_recorded_failure_recovers_with_title_only_patch_and_exact_image_verification():
    packet,calls,raw=exercise()
    assert len(calls)==2 and calls[0][0]=='PATCH_C01' and calls[1][0].startswith('PATCH_VERIFY_C01_')
    assert not calls[0][2] and calls[1][2]
    assert all(c['field']=='TITLE' for c in calls[1][1]['claims'])
    result=packet['reviewed']['C01']
    assert result['sentences']==[{k:s[k] for k in ('text','fact_ids')} for s in raw['sentences']]
    assert result['story']==''.join(s['text'] for s in raw['sentences'])
    assert packet['final_title_repair_ledger'][0]['status']=='ACCEPTED_AFTER_INDEPENDENT_TITLE_IMAGE_VERIFICATION'
    assert packet['final_verification_output']['items'][0]['title_supported'] is False  # original verdict remains


@pytest.mark.parametrize('mode',['foreign','foreign_sentence','invalid_source','recorded_r56','duplicate','extra_body','self_approval','deny','budget','changed_pixels','unselected'])
def test_malformed_unverified_budget_or_changed_image_cannot_publish_old_or_new_title(mode):
    packet,calls,_=exercise(mode)
    assert not packet['reviewed'] and len(calls)<=2
    assert packet['final_title_repair_ledger'][0]['status']=='BLOCKED'


@pytest.mark.parametrize('mode',['terminal','no_body'])
def test_terminal_failure_or_no_approved_sentence_does_not_attempt_repair(mode):
    packet,calls,_=exercise(mode)
    assert not calls and not packet['reviewed']


def test_title_repair_uses_selected_fact_but_keeps_other_approved_body_sentences():
    packet, calls, raw = exercise('selected')
    assert len(calls) == 2
    assert packet['reviewed']['C01']['sentences'] == [
        {k: s[k] for k in ('text', 'fact_ids')} for s in raw['sentences']]


def test_no_selected_supported_source_blocks_without_wasting_another_model_call():
    packet, calls, _ = exercise('no_selected')
    assert not calls and not packet['reviewed']
    assert packet['final_title_repair_ledger'][0]['reason'] == 'NO_APPROVED_SENTENCE_WITH_SELECTED_FRAME'


def test_dangling_opening_after_final_removal_uses_one_polish_then_only_changed_claim_is_rechecked():
    f=fixture();m=f['memory'];raw=deepcopy(f['row'])
    raw['title']='沿路骑行';raw['title_fact_ids']=[raw['sentences'][0]['fact_ids'][0]]
    raw['sentences'][1]['text']='另一处场景中，路旁有茂密的植物。'
    # Keep fixture references; assertions concern transport/scopes, not pixel truth.
    calls=[]
    def ask(stage,prompt,schema,context,**kwargs):
        calls.append((stage,deepcopy(context)))
        if stage=='WRITE_NARRATIVE_BRIEF':return {'items':[]}
        if stage=='WRITE':return {'items':[dict(id='C01',title=raw['title'],story=''.join(s['text'] for s in raw['sentences']))]}
        if stage=='REVIEW':return {'items':[deepcopy(raw)]}
        if stage=='REPAIR_FINAL_STYLE':
            item=context['items'][0];out=deepcopy(item)
            draft={'id':'C01','title':item['title'],'title_fact_ids':item['title_fact_ids'],'decision':'PUBLISH','reason':'Synthetic polish','voice_issues':[],
                'sentences':[dict(source_index=s['source_index'],text=s['draft_text'],fact_ids=s['fact_ids']) for s in item['sentence_checks']]}
            draft['sentences'][0]['text']='路旁有茂密的植物。'
            return {'items':[draft]}
        result=scripted_final_verdict(context)
        if 'POLISHED' not in stage:
            for c,r in zip(context['claims'],result['claims']):
                if c['field']=='SENTENCE' and c['source_index']==0:r.update(supported=False,reason='Injected unsupported first sentence')
        return result
    packet=write_and_review_with_test_images([m],('WRITE','REVIEW','REPAIR'),ask=ask,time_basis='UNKNOWN',stage_runs=[])
    assert packet['reviewed']['C01']['story'].startswith('路旁有茂密的植物。')
    assert len([c for c in calls if c[0]=='REPAIR_FINAL_STYLE'])==1
    rechecked=[c for s,c in calls if 'FINAL_VERIFY_POLISHED' in s]
    assert len(rechecked)==1 and [c['text'] for c in rechecked[0]['claims']]==['路旁有茂密的植物。']
    assert all(c['field']=='SENTENCE' for c in rechecked[0]['claims'])
