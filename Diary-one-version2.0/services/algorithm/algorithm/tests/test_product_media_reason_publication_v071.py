"""Deterministic publication cleanup; raw model records and pixels stay unchanged."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest

from diary_one_ci import product_editor as p
from diary_one_ci.x02 import run_x02_product
from test_product_editor import Gateway
from test_x02 import make_x02_bundle


def fixture():
    return json.loads((Path(__file__).parent / 'fixtures/product_reason_fallback_zoo_r5.json').read_text())


def test_actual_r5_zoo_reason_is_withdrawn_after_failed_claim_but_image_and_copy_stay():
    source = fixture(); packet = deepcopy(source['packet']); original_packet = deepcopy(packet)
    chapters = deepcopy(source['chapters']); prior = deepcopy(chapters)
    audit = p.normalize_public_media_reasons(chapters, [('PRIMARY', packet)])
    panda = next(m for m in chapters[0]['selected_media'] if m['source_asset_id'] == 'asset-5')
    assert panda['selection_reason'] == chapters[0]['hero_reason'] == '用作本章节封面。'
    event = next(a for a in audit if a['source_asset_id'] == 'asset-5')
    assert event['original_selection_reason'] == 'A red panda walking along a thick wooden log in an enclosure with a pavilion structure.'
    assert {a['claim_id'] for a in event['triggering_claims']} == {'Q003', 'Q009', 'Q010'}
    for original, changed in zip(prior, chapters):
        assert original['story'] == changed['story'] and original['title'] == changed['title']
        assert original['hero_frame_id'] == changed['hero_frame_id']
        for before, after in zip(original['selected_media'], changed['selected_media']):
            assert {k:v for k,v in before.items() if k!='selection_reason'} == {k:v for k,v in after.items() if k!='selection_reason'}
    assert packet == original_packet
    assert any('walking along' in c['reason'] for c in packet['selected_structure']['chapters'][0]['media_choices'])


def simple():
    chapter = {'id':'C-public', 'hero_asset_id':'app-a', 'hero_frame_id':'same', 'hero_reason':'原封面理由',
        'selected_media':[
            {'asset_id':'app-a','source_asset_id':'a','representative_frame_id':'same','selection_reason':'原封面理由'},
            {'asset_id':'app-b','source_asset_id':'b','representative_frame_id':'same','selection_reason':'原细节理由'},
            {'asset_id':'app-c','source_asset_id':'c','representative_frame_id':'other','selection_reason':'原其他理由'}]}
    claim = {'claim_id':'Q1','memory_id':'M1','field':'SENTENCE','source_index':0,
        'frame_refs':[{'source_asset_id':'b','frame_id':'same'}]}
    packet={'final_verification_input':{'claims':[claim]},'final_verification_output':{'items':[
        {'id':'M1','title_supported':True,'sentences':[{'source_index':0,'supported':False,'reason':'unconfirmed relation'}]}]}}
    return [chapter],packet


def test_exact_source_and_representative_frame_only_and_support_role_text():
    chapters,packet=simple();before=deepcopy(chapters)
    audit=p.normalize_public_media_reasons(chapters,[('RECOVERY',packet)])
    assert chapters[0]['hero_reason']==before[0]['hero_reason']
    assert chapters[0]['selected_media'][0]==before[0]['selected_media'][0]
    assert chapters[0]['selected_media'][1]['selection_reason']=='作为本章节的补充画面。'
    assert chapters[0]['selected_media'][2]==before[0]['selected_media'][2]
    assert audit[0]['triggering_claims'][0]['packet']=='RECOVERY'
    assert audit[0]['original_hero_reason'] is None
    assert not p.normalize_public_media_reasons(chapters,[('RECOVERY',packet)])


@pytest.mark.parametrize('case',['accepted','not_displayed_frame','absent_claims'])
def test_unaffected_public_reasons_remain_byte_for_byte(case):
    chapters,packet=simple();before=deepcopy(chapters)
    if case=='accepted':packet['final_verification_output']['items'][0]['sentences'][0]['supported']=True
    elif case=='not_displayed_frame':packet['final_verification_input']['claims'][0]['frame_refs'][0]['frame_id']='not-selected'
    else:packet['final_verification_input']['claims']=[]
    assert p.normalize_public_media_reasons(chapters,[('PRIMARY',packet)])==[]
    assert chapters==before


def test_unexecuted_claim_has_no_visual_approval_and_neutralizes_only_its_selected_frame():
    chapters,packet=simple();packet['final_verification_output']={}
    audit=p.normalize_public_media_reasons(chapters,[('PRIMARY',packet)])
    assert audit[0]['triggering_claims'][0]['verdict_reason']=='FINAL_CLAIM_NOT_EVALUATED'
    assert chapters[0]['selected_media'][1]['selection_reason']=='作为本章节的补充画面。'


def test_whole_pipeline_model_requests_and_raw_outputs_are_unchanged(tmp_path, monkeypatch):
    manifest=make_x02_bundle(tmp_path,1)
    class Recorded(Gateway):
        def __init__(self):super().__init__();self.record=[]
        def call(self,stage,prompt,schema,evidence=(),context=None):
            result=super().call(stage,prompt,schema,evidence,context)
            if '_FINAL_VERIFY_B' in stage:
                for claim,row in zip(context['claims'],result.output['claims']):
                    if claim['memory_id']=='M01':row.update(supported=False,reason='Synthetic failed moment claim')
            self.record.append(deepcopy({'stage':stage,'prompt':prompt,'schema':schema,'context':context,
                'images':[(a['asset_id'],f['frame_id'],sha256(Path(path).read_bytes()).hexdigest()) for a,f,path in evidence],
                'output':result.output}))
            return result
    baseline=Recorded()
    with monkeypatch.context() as patch:
        patch.setattr(p,'normalize_public_media_reasons',lambda chapters,packets:[])
        original=run_x02_product(manifest,baseline)
    current=Recorded();updated=run_x02_product(manifest,current)
    assert baseline.record==current.record
    assert original['chapters'] and updated['chapters']
    assert updated['chapters'][0]['hero_reason']=='用作本章节封面。'
    assert updated['decision_trace']['public_media_reason_fallbacks']
    left=deepcopy(original['chapters']);right=deepcopy(updated['chapters'])
    for rows in (left,right):
        for chapter in rows:
            chapter.pop('hero_reason')
            for media in chapter['selected_media']:media.pop('selection_reason')
    assert left==right
    for key in ('editor_input','editor_output','writer_output','review_output','final_verification_input',
                'final_verification_output','final_verification_batches','verified_facts','selected_structure'):
        assert original['decision_trace'][key]==updated['decision_trace'][key]
