"""Final immutable verdicts; fixtures exercise evidence binding, not model accuracy."""
from copy import deepcopy

import jsonschema
import pytest

from diary_one_ci import product_editor as p
from test_product_editor import scripted_final_verdict


FACTS = {
    'F005': dict(id='F005', asset_id='V005', text='镜头跟随两名男子穿过铺设红色地砖的宽阔步道，两侧种植棕榈树。远处可见白色石柱门廊结构及一艘停泊的白色船只。',
        evidence_frame_ids=['asset-4-f0', 'asset-4-f1'], visual_reviewed=True, temporal_support='CHANGE', support_grade='STRONG', frame_pts_ms=[0, 4004],
        frame_observations=[dict(text='远处可见白色石柱门廊结构及一艘停泊的白色船只。', evidence_frame_ids=['asset-4-f1'])]),
    'F006': dict(id='F006', asset_id='V006', text='视频展示了海滨区域的连续移动画面。起初在沙滩上经过蓝色健身器材和高楼，随后视角转向开阔的海滩，可见海水、远处的山脉以及零散游客。',
        evidence_frame_ids=['asset-5-f2'], visual_reviewed=True, temporal_support='CHANGE', support_grade='STRONG', frame_pts_ms=[9977]),
}
# Exact C02 from candidate-v7-1-hardened-r3/H0zAYx5UCIM__group_04.
TEXTS = ['宽阔的步道铺着红色地砖，两侧种满棕榈树。', '白色石柱门廊下停泊着一艘白船。',
         '望向开阔的海滩，海水连着远处的山脉，零星游客散在岸边。']


from final_copy_test_support import bound_test_images, write_and_review_with_test_images
from diary_one_ci import final_copy_evidence
from diary_one_ci.x02 import X02ModelNotReady, X02StageCallError
from types import SimpleNamespace


def memories():
    return p.memory_specs([dict(id='C02', theme='海滨', fact_ids=['F005', 'F006'])], [], deepcopy(FACTS))


def reviewed():
    return dict(id='C02', title='红砖步道与远山海景', title_fact_ids=['F005', 'F006'], decision='PUBLISH',
        reason='Synthetic original review', voice_issues=[], sentences=[dict(text=t, fact_ids=[fid], source_index=i)
            for i, (t, fid) in enumerate(zip(TEXTS, ['F005', 'F005', 'F006']))])


def run(*, rejected=(1,), title=True, malformed=None, failure=False):
    calls = []; original = reviewed()
    def ask(stage, prompt, schema, context, *, evidence=()):
        calls.append((stage, deepcopy(context), evidence))
        if stage.endswith('_NARRATIVE_BRIEF'): return {'items': []}
        if stage == 'WRITE': return {'items': [dict(id='C02', title=original['title'], story=''.join(TEXTS))]}
        if stage == 'REVIEW': return {'items': [deepcopy(original)]}
        if '_FINAL_TITLE_REPAIR_' in stage: return {}  # Failed repair cannot revive the rejected original title.
        assert stage.startswith('REVIEW_FINAL_VERIFY_B') and evidence
        if failure: raise TimeoutError('injected batch timeout')
        result = scripted_final_verdict(context)
        for claim, row in zip(context['claims'], result['claims']):
            if claim['field'] == 'TITLE': row['supported'] = title
            elif claim['source_index'] in rejected: row.update(supported=False, reason='Spatial relation unsupported by image')
        if malformed and any(c['source_index'] == 0 for c in context['claims']): malformed(result)
        return result
    packet = write_and_review_with_test_images(memories(), ('WRITE', 'REVIEW', 'REPAIR'), ask=ask,
        time_basis='IMPORT_SEQUENCE_ONLY', stage_runs=[])
    return packet, calls


def test_actual_r3_c02_bad_relation_is_locally_removed_using_image_only_claim_context():
    packet, calls = run()
    assert packet['review_output']['items'][0] == reviewed()
    assert packet['reviewed']['C02']['story'] == TEXTS[0] + TEXTS[2]
    assert packet['reviewed']['C02']['title'] == reviewed()['title']
    batches = packet['final_verification_batches']; assert len(batches) == 3
    assert packet['final_verification_output']['provenance'] == 'PROGRAM_AGGREGATED_IMAGE_CLAIM_VERDICTS'
    for stage, context, evidence in calls[3:]:
        encoded = __import__('json').dumps(context, ensure_ascii=False)
        assert evidence and 'image_transform_audit' in context
        assert FACTS['F005']['text'] not in encoded and 'frame_observations' not in encoded
        for claim in context['claims']:
            assert set(claim) == {'claim_id','memory_id','kind','field','source_index','text','fact_ids','frame_refs'}
    assert batches[1]['raw_output']['claims'][1]['supported'] is False


def test_valid_final_copy_retains_exact_text_title_and_refs():
    packet, _ = run(rejected=())
    original, _ = p.compile_copy({'items': [reviewed()]}, memories(), review=True)
    assert packet['reviewed'] == original


@pytest.mark.parametrize('kwargs', [{'rejected': (0,1,2)}, {'title': False}, {'failure': True}])
def test_all_invalid_title_invalid_or_all_transport_failed_cannot_use_old_publish(kwargs):
    packet, _ = run(**kwargs)
    assert not packet['reviewed']


@pytest.mark.parametrize('mutation', [
    lambda r: r['claims'][0].update(text='unauthorized rewrite'),
    lambda r: r['claims'][0].update(claim_id='FOREIGN'),
    lambda r: r['claims'].pop(),
    lambda r: r['claims'][1].update(claim_id=r['claims'][0]['claim_id']),
    lambda r: r['claims'][0].update(supported='true'),
    lambda r: r['claims'][0].update(reason=1),
    lambda r: r['claims'][0].update(reason='   '),
])
def test_malformed_batch_is_local_and_raw_is_retained(mutation):
    packet, _ = run(rejected=(), malformed=mutation)
    assert packet['reviewed']['C02']['story'] == TEXTS[2]
    assert packet['final_verification_batches'][1]['status'] == 'NOT_EVALUATED'
    assert packet['final_verification_batches'][1]['raw_output'] is not None
    assert packet['final_verification_batches'][0]['status'] == 'EVALUATED'


@pytest.mark.parametrize('kind', ['CHAPTER','HIGHLIGHT','AHA'])
@pytest.mark.parametrize('supported', [True,False])
def test_normal_memory_kind_retains_its_own_copy_contract(kind, supported):
    item = dict(id='M01', kind=kind, fact_ids=['F005'], facts=[deepcopy(FACTS['F005'])])
    row = dict(id='M01', decision='PUBLISH', reason='Synthetic original', title='棕榈步道', title_fact_ids=['F005'],
        sentences=[dict(text='红砖步道两侧长着棕榈树。', fact_ids=['F005'])])
    prior, _ = p.compile_copy({'items':[row]}, [item], review=True)
    packet = {'reviewed':deepcopy(prior), 'copy_response_normalizations':[]}
    def ask(stage,prompt,schema,context,*,evidence):
        output=scripted_final_verdict(context)
        if not supported: output['claims'][1]['supported']=False
        jsonschema.validate(output,schema)
        return output
    with bound_test_images([item]) as (items,evidence,scope):
        p.verify_final_chapter_copy(packet,items,'FINAL',ask=ask,time_basis='UNKNOWN',stage_runs=[],evidence=evidence,evidence_scope=scope)
    assert packet['reviewed'] == (prior if supported else {})


def test_same_image_claims_across_memories_share_one_request_without_sharing_fact_scope():
    first=memories()[0]; second=deepcopy(first); second['id']='C03'
    with bound_test_images([first,second]) as (items,evidence,scope):
        raw=reviewed(); other=deepcopy(raw); other['id']='C03'
        prior,_=p.compile_copy({'items':[raw,other]},items,review=True)
        _,context=p.final_copy_verification_items(items,prior)
        plan=final_copy_evidence.build_final_claim_batches(context,evidence,scope)
        assert len(plan['claims']) == 8 and len(plan['batches']) == 3
        assert {c['memory_id'] for c in plan['batches'][1]['claims']} == {'C02','C03'}
        assert len({c['claim_id'] for c in plan['claims']}) == 8
        scope['memories'][1]['shown_refs']=[]
        plan=final_copy_evidence.build_final_claim_batches(context,evidence,scope)
        assert all(c.get('status')=='NOT_EVALUATED' for c in plan['claims'] if c['memory_id']=='C03')
        assert all(c.get('batch_id') for c in plan['claims'] if c['memory_id']=='C02')


@pytest.mark.parametrize('code', ['MODEL_HTTP_401','MODEL_HTTP_403','MODEL_HTTP_429','NOT_READY','BUDGET'])
def test_terminal_provider_failure_stops_later_batches_with_explicit_unexecuted_audit(code):
    item=memories()[0]; prior,_=p.compile_copy({'items':[reviewed()]},[item],review=True)
    packet={'reviewed':prior,'copy_response_normalizations':[]}; calls=[]; stages=[]
    failed=SimpleNamespace(call_status='FAILED')
    def ask(*args,**kwargs):
        calls.append(args[0])
        if code=='NOT_READY': raise X02ModelNotReady('unavailable')
        if code=='BUDGET':
            from diary_one_ci.x02 import X02CallAttemptLimitReached
            raise X02CallAttemptLimitReached('budget')
        raise X02StageCallError('blocked',stage_run=failed,code=code)
    with bound_test_images([item]) as (items,evidence,scope):
        p.verify_final_chapter_copy(packet,items,'FINAL',ask=ask,time_basis='UNKNOWN',stage_runs=stages,evidence=evidence,evidence_scope=scope)
    assert len(calls)==1 and not packet['reviewed'] and packet['final_verification_terminal_failure']
    assert all(b['reason']=='NOT_EXECUTED_AFTER_TERMINAL_PROVIDER_FAILURE' for b in packet['final_verification_batches'][1:])
    if code.startswith('MODEL_'): assert stages == [failed]


def test_missing_actual_images_cannot_be_marked_verified_and_make_no_request():
    item=memories()[0]; prior,_=p.compile_copy({'items':[reviewed()]},[item],review=True)
    packet={'reviewed':prior,'copy_response_normalizations':[]}
    def ask(*args,**kwargs): raise AssertionError('No bound images should be sent')
    p.verify_final_chapter_copy(packet,[item],'FINAL',ask=ask,time_basis='UNKNOWN',stage_runs=[],evidence_scope={'memories':[]})
    assert not packet['reviewed'] and packet['final_verification_batches']==[]


@pytest.mark.parametrize('mode',['valid','timeout','wrong_title','wrong_refs','new_relation'])
def test_style_polish_remains_optional_and_cannot_bypass_image_claim_verdict(mode):
    item=memories()[0]; row=reviewed(); row['sentences']=[dict(text='镜头显示一艘停泊的白船。',fact_ids=['F005'],source_index=0)]
    prior,_=p.compile_copy({'items':[row]},[item],review=True)
    packet={'reviewed':prior,'copy_response_normalizations':[]}; before=deepcopy(prior)
    def ask(stage,prompt,schema,context,**kwargs):
        if stage=='POLISH':
            if mode=='timeout': raise TimeoutError('optional unavailable')
            output=deepcopy(row);output['sentences'][0]['text']='一艘白船停泊在远处。' if mode!='new_relation' else '一艘白船停在门廊下。'
            if mode=='wrong_title':output['title']='擅改标题'
            if mode=='wrong_refs':output['sentences'][0]['fact_ids']=['F006']
            return {'items':[output]}
        result=scripted_final_verdict(context)
        if mode=='new_relation':
            for c,r in zip(context['claims'],result['claims']):
                if c['field']=='SENTENCE':r.update(supported=False,reason='unsupported relation')
        return result
    p.polish_final_chapter_style(packet,[item],'POLISH',ask=ask,time_basis='UNKNOWN',stage_runs=[])
    if mode in ('timeout','wrong_title','wrong_refs'):assert packet['reviewed']==before
    with bound_test_images([item]) as (items,evidence,scope):
        p.verify_final_chapter_copy(packet,items,'FINAL',ask=ask,time_basis='UNKNOWN',stage_runs=[],evidence=evidence,evidence_scope=scope)
    assert bool(packet['reviewed']) == (mode!='new_relation')


def test_unflagged_copy_adds_no_style_call():
    item=memories()[0];prior,_=p.compile_copy({'items':[reviewed()]},[item],review=True)
    packet={'reviewed':prior,'copy_response_normalizations':[]}
    def ask(*args,**kwargs):raise AssertionError('unneeded optional request')
    p.polish_final_chapter_style(packet,[item],'STYLE',ask=ask,time_basis='UNKNOWN',stage_runs=[])
    assert packet['reviewed']==prior


@pytest.mark.parametrize('code', ['MODEL_HTTP_401', 'MODEL_HTTP_403', 'MODEL_HTTP_429', 'NOT_READY', 'BUDGET'])
def test_real_run_terminal_final_failure_never_calls_coverage_or_recovery(tmp_path, code):
    import dataclasses
    from diary_one_ci.x02 import run_x02_product, X02CallAttemptLimitReached
    from test_product_editor import Gateway
    from test_x02 import make_x02_bundle
    calls = []
    class FailingFinal(Gateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            calls.append(stage)
            result = super().call(stage, prompt, schema, evidence, context)
            if '_FINAL_VERIFY_B' in stage:
                assert 'image_transform_audit' not in prompt
                assert 'image_transform_audit' in context
                assert all(str(path.parent) not in prompt for _, _, path in evidence)
                if code == 'NOT_READY': raise X02ModelNotReady('injected not-ready')
                if code == 'BUDGET': raise X02CallAttemptLimitReached('injected shared run budget')
                raise X02StageCallError('injected terminal error',
                    stage_run=dataclasses.replace(result, output={}, call_status='FAILED'), code=code)
            return result
    result = run_x02_product(make_x02_bundle(tmp_path, 1), FailingFinal())
    assert '_FINAL_VERIFY_B' in calls[-1]
    assert sum('_FINAL_VERIFY_B' in stage for stage in calls) == 1
    assert not any(stage.startswith(('S14', 'S15', 'S16', 'S17')) for stage in calls)
    assert not result['chapters'] and not result['ahas']
    assert result['decision_trace']['final_verification_terminal_failure']
