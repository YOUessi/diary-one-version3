"""Second-review disagreement/faults are simulated; no model-quality truth claims."""
from copy import deepcopy

import jsonschema
import pytest

from diary_one_ci import product_editor as p
from diary_one_ci.x02 import X02ModelNotReady
from final_copy_test_support import bound_test_images
from test_product_editor import scripted_final_verdict


FACT = dict(id='F001', asset_id='V001', text='动物停留在岩石旁，画面上部有木梁。',
    evidence_frame_ids=['frame-a','frame-b'], visual_reviewed=True,
    temporal_support='STATE', support_grade='STRONG', frame_pts_ms=[0, 5000])


def item():
    return p.memory_specs([dict(id='C01', theme='动物', fact_ids=['F001'])], [],
        {'F001': deepcopy(FACT)})[0]


def copy_row(title='岩石旁的动物', texts=('动物停在横梁上。','旁边有绿色植物。')):
    return dict(id='C01', decision='PUBLISH', reason='Scripted pre-review', title=title,
        title_fact_ids=['F001'], voice_issues=[], sentences=[
            dict(text=text, fact_ids=['F001'], source_index=i) for i,text in enumerate(texts)])


@pytest.mark.parametrize('text', ['横梁上的红褐色身影', '白船停泊在门廊下。', '展柜里的花瓶',
    '水面倒映着建筑。', '头顶是高架桥。', '小鸟站在树枝上。', '船在桥的正下方。'])
def test_relationship_triggers_across_scenes_without_declaring_truth(text):
    assert p.requires_spatial_relation_review(text)


@pytest.mark.parametrize('text', ['海边散步', '红砖步道与远山海景', '金色树叶', '一艘白船停泊着。'])
def test_no_explicit_spatial_relation_adds_no_special_review(text):
    assert not p.requires_spatial_relation_review(text)


def verify(mode='deny', *, title=False, primary=False):
    memory=item(); row=copy_row(title='横梁上的动物' if title else '岩石旁的动物',
                              texts=('绿色植物围着岩石。',) if title else ('动物停在横梁上。','旁边有绿色植物。'))
    compiled,_=p.compile_copy({'items':[row]},[memory],review=True)
    packet={'reviewed':compiled,'copy_response_normalizations':[]}; calls=[]
    def ask(stage,prompt,schema,context,*,evidence):
        calls.append((stage,deepcopy(context),deepcopy(schema)))
        result=scripted_final_verdict(context)
        if stage.endswith('_SPATIAL'):
            assert evidence and context['verification_mode']=='IMAGE_FIRST_SPATIAL_OBSERVATIONS_HIDDEN_EXPECTED_RELATION'
            assert 'facts' not in context and 'previous_verdict' not in context
            assert all(p.requires_spatial_relation_review(c['text']) for c in context['claims'])
            assert all('expected_relations' not in t and 'source_quote' not in t for t in context['relation_targets'])
            if mode=='timeout': raise TimeoutError('Injected relation outage')
            if mode=='terminal': raise X02ModelNotReady('Injected auth/provider unavailable')
            if mode=='foreign': result['observations'][0]['target_id']='OTHER_MEMORY'
            elif mode=='missing': result['observations']=[]
            elif mode=='duplicate': result['observations']*=2
            elif mode=='rewrite': result['observations'][0]['text']='unauthorized'
            elif mode=='wrong_type': result['observations'][0]['same_frame']='true'
            elif mode=='empty_reason': result['observations'][0]['description']=''
            elif mode=='deny':
                for r in result['observations']: r.update(observed_relation='UNKNOWN')
        elif primary:
            for c,r in zip(context['claims'],result['claims']):
                if p.requires_spatial_relation_review(c['text']): r.update(supported=False,reason='Primary denied')
        return result
    with bound_test_images([memory]) as (items,evidence,scope):
        p.verify_final_chapter_copy(packet,items,'FINAL_VERIFY',ask=ask,time_basis='UNKNOWN',
            stage_runs=[],evidence=evidence,evidence_scope=scope)
    return packet,calls,row


def test_second_review_veto_removes_only_bad_relation_sentence():
    packet,calls,_=verify()
    assert packet['reviewed']['C01']['story']=='旁边有绿色植物。'
    assert len([c for c in calls if c[0].endswith('_SPATIAL')])==1
    challenged=next(b for b in packet['final_verification_batches'] if 'spatial_verification' in b)
    assert all(r['supported'] for r in challenged['raw_output']['claims'])
    assert challenged['spatial_verification']['compiled_observations'][0]['supported'] is False
    assert challenged['spatial_verification']['judgment_source'].endswith('NOT_GROUND_TRUTH')


def test_title_relation_is_not_protected_by_earlier_approval():
    packet,_,_=verify(title=True)
    assert not packet['reviewed']


@pytest.mark.parametrize('mode',['timeout','foreign','missing','duplicate','rewrite','wrong_type','empty_reason'])
def test_failed_or_malformed_challenge_cannot_pass_and_keeps_unrelated_sentence(mode):
    packet,_,_=verify(mode)
    assert packet['reviewed']['C01']['story']=='旁边有绿色植物。'
    audit=next(b['spatial_verification'] for b in packet['final_verification_batches'] if 'spatial_verification' in b)
    assert audit['status']=='NOT_EVALUATED'


def test_secondary_approval_never_resurrects_primary_rejection():
    packet,calls,_=verify('approve',primary=True)
    assert packet['reviewed']['C01']['story']=='旁边有绿色植物。'
    assert not any(c[0].endswith('_SPATIAL') for c in calls)


def test_successful_independent_checks_keep_exact_frozen_words_and_references():
    packet,_,row=verify('approve')
    expected,_=p.compile_copy({'items':[row]},[item()],review=True)
    assert packet['reviewed']==expected


def test_terminal_challenge_failure_stops_further_provider_requests():
    packet,calls,_=verify('terminal')
    assert packet['final_verification_terminal_failure']
    assert calls[-1][0].endswith('_SPATIAL')


@pytest.mark.parametrize('mode',['valid','foreign_refs','new_relation','timeout'])
def test_camera_report_title_can_be_reworded_only_with_locked_citations_and_final_images(mode):
    memory=item(); memory['facts'][0]['text']='海湾中停着白色船只，远处有房屋。'
    row=copy_row(title='海湾全景镜头平移',texts=('海湾中停着白色船只。',))
    prior,_=p.compile_copy({'items':[row]},[memory],review=True)
    assert prior['C01']['style_flags']==['TITLE_REPORT_STYLE']
    before=deepcopy(prior); packet={'reviewed':prior,'copy_response_normalizations':[]}
    def ask(stage,prompt,schema,context,**kwargs):
        if stage=='STYLE':
            if mode=='timeout': raise TimeoutError('Injected optional style outage')
            result=deepcopy(row);result['title']='门廊下的白船' if mode=='new_relation' else '海湾里的白船'
            if mode=='foreign_refs':result['title_fact_ids']=['F999']
            return {'items':[result]}
        result=scripted_final_verdict(context)
        if mode=='new_relation' and stage.endswith('_SPATIAL'):
            for r in result['observations']:r.update(observed_relation='UNKNOWN')
        return result
    p.polish_final_chapter_style(packet,[memory],'STYLE',ask=ask,time_basis='UNKNOWN',stage_runs=[])
    if mode in ('timeout','foreign_refs'):assert packet['reviewed']==before
    else:
        assert not packet['reviewed']['C01']['style_flags']
        assert packet['reviewed']['C01']['sentences']==before['C01']['sentences']
        assert packet['reviewed']['C01']['title_fact_ids']==before['C01']['title_fact_ids']
    with bound_test_images([memory]) as (items,evidence,scope):
        p.verify_final_chapter_copy(packet,items,'FINAL_VERIFY',ask=ask,time_basis='UNKNOWN',stage_runs=[],evidence=evidence,evidence_scope=scope)
    assert bool(packet['reviewed']) == (mode!='new_relation')
