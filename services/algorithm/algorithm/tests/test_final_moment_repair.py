"""Transport/contract regressions for recorded zoo failure shapes, not visual gold."""
from copy import deepcopy

import pytest

from diary_one_ci import product_editor as p
from diary_one_ci.final_moment_repair import repair_final_moments, validate_reduction, candidate_copies
from diary_one_ci.x02 import X02CallAttemptLimitReached
from final_copy_test_support import bound_test_images
from test_product_editor import scripted_final_verdict


def exercise(mode='accept', kind='HIGHLIGHT'):
    fact = dict(id='F006', text='红褐色长尾的小熊猫趴在横跨的树干上。', asset_id='V006',
                support_grade='DIRECT', frame_pts_ms=[0], evidence_frame_ids=['asset-5-f0'])
    if mode == 'cross_field':
        fact['text'] = '红褐色长尾的小熊猫趴在横跨的树干上休息。'
    memory = dict(id='M01', kind=kind, theme=fact['text'], fact_ids=['F006'], facts=[fact],
                  evidence_groups=[dict(asset_id='V006', facts=[fact])],
                  copy_evidence_scope='IMAGE_REVIEWED_MOMENT_ANCHOR_ONLY; NOT_THE_FULL_MULTI_FRAME_FACT')
    if mode == 'no_anchor':
        memory.pop('copy_evidence_scope')
    raw = dict(id='M01', title='红褐色的小熊猫', title_fact_ids=['F006'],
               sentences=[dict(text=fact['text'], fact_ids=['F006'])], decision='PUBLISH', reason='Fixture')
    if mode in ('both', 'spatial', 'spatial_repeated', 'cross_field'):
        raw['title'] = '树干上的小熊猫'
    reviewed, _ = p.compile_copy({'items': [raw]}, [memory], review=True)
    assert reviewed
    packet = dict(reviewed=reviewed)
    calls = []

    def ask(stage, prompt, schema, context, **kwargs):
        calls.append(dict(stage=stage, context=deepcopy(context), images=bool(kwargs.get('evidence'))))
        if stage == 'REPAIR_M01':
            if mode == 'budget':
                raise X02CallAttemptLimitReached('Synthetic limit')
            if mode == 'null':
                return {'choice_id': None}
            if mode == 'bare_null':
                return None
            assert schema['type'] == 'object'  # compatible with the JSON-object gateway
            result = dict(id='M01', title='小熊猫' if mode in ('both', 'spatial') else '红褐色的小熊猫', title_fact_ids=['F006'],
                sentences=[dict(source_index=0, text='红褐色长尾的小熊猫。', fact_ids=['F006'])])
            if mode == 'foreign':
                result['sentences'][0]['fact_ids'] = ['F007']
            elif mode == 'protected':
                result['title'] = '另一只小熊猫'
            elif mode == 'self_approval':
                result['supported'] = True
            elif mode == 'unchanged':
                result['sentences'][0]['text'] = fact['text']
            elif mode == 'extra_sentence':
                result['sentences'] *= 2
            elif mode == 'spatial_repeated':
                result['title'] = '树干旁的小熊猫'
            elif mode == 'new_action':
                result['sentences'][0]['text'] = '红褐色的小熊猫，拖着一条蓬松的长尾。'
            elif mode == 'new_location':
                result['sentences'][0]['text'] = '红褐色小熊猫趴在岩石上。'
            elif mode == 'new_mood':
                result['sentences'][0]['text'] = '红褐色长尾的小熊猫悠闲地休息。'
            if mode in ('spatial', 'spatial_repeated'):
                assert context['withdrawn_relations'] == [
                    {'subject': '小熊猫', 'reference': '树干', 'source_quote': '树干上的小熊猫'}]
            if mode in ('foreign', 'protected', 'self_approval', 'unchanged', 'extra_sentence', 'spatial_repeated', 'new_action', 'new_location', 'new_mood'):
                return {'choice_id': 'R01', 'copy': result}
            if mode == 'unknown_choice':
                return {'choice_id': 'R99'}
            if mode == 'free_text_choice':
                return {'choice_id': '小熊猫在玩耍'}
            assert all(c['copy']['title_fact_ids'] == ['F006'] for c in context['candidate_copies'])
            assert all(c['copy']['sentences'][0]['fact_ids'] == ['F006'] for c in context['candidate_copies'])
            return {'choice_id': 'R01'}
        if mode == 'cross_field' and stage.endswith('_SPATIAL'):
            return {'claims': [dict(claim_id=c['claim_id'], supported=True, reason='Fault injection: says body is supported') for c in context['claims']],
                    'observations': [dict(target_id=t['target_id'], frame_ref=t['allowed_frame_refs'][0],
                        subject_visible=True, reference_visible=True, identity_confirmed=True, same_frame=True,
                        subject_box=[.43,.48,.57,.55], reference_box=[0,.26,.73,.41],
                        observed_relation='SUPPORTED_BY', support_surface='REFERENCE', description='Fault injection: boxes contradict claimed support')
                        for t in context['relation_targets']]}
        verdict = scripted_final_verdict(context)
        for claim, row in zip(context['claims'], verdict['claims']):
            if mode != 'cross_field' and stage.startswith('INITIAL') and (claim['field'] == 'SENTENCE' or mode in ('both', 'spatial', 'spatial_repeated', 'cross_field')):
                row.update(supported=False, reason='Animal is on a rock, not supported by the overhead trunk')
            if mode == 'deny' and stage.startswith('REPAIR_VERIFY'):
                row.update(supported=False, reason='Independent image rejection')
        return verdict

    with bound_test_images([memory]) as (items, evidence, scope):
        p.verify_final_chapter_copy(packet, items, 'INITIAL', ask=ask, time_basis='IMPORT_ORDER_ONLY',
                                   stage_runs=[], evidence=evidence, evidence_scope=scope)
        assert not packet['reviewed']
        if mode not in ('no_candidate', 'cross_field'):
            packet['final_verification_batches'].append({
                'input': {'claims': [{'claim_id': 'spatial-title', 'memory_id': 'M01'}]},
                'spatial_verification': {
                    'relation_targets': [{'target_id': 't1', 'claim_id': 'spatial-title', 'subject': '小熊猫',
                                          'reference': '树干', 'source_quote': '树干上的小熊猫'},
                                         {'target_id': 'other', 'claim_id': 'another-memory',
                                          'subject': '水鸟', 'reference': '水池', 'source_quote': '水池里的水鸟'}],
                    'compiled_observations': [{'target_id': 't1', 'supported': False},
                                              {'target_id': 'other', 'supported': False}],
                }})
        if mode == 'terminal':
            packet['final_verification_terminal_failure'] = True
        if mode == 'changed_pixels':
            evidence[0][2].write_bytes(b'changed')
        before = len(calls)
        repair_final_moments(packet, items, 'REPAIR', ask=ask, time_basis='IMPORT_ORDER_ONLY',
                             stage_runs=[], evidence=evidence, evidence_scope=scope)
        after = len(calls)
        repair_final_moments(packet, items, 'REPAIR', ask=ask, time_basis='IMPORT_ORDER_ONLY',
                             stage_runs=[], evidence=evidence, evidence_scope=scope)
        assert len(calls) == after
    return packet, calls[before:]


@pytest.mark.parametrize('kind', ['AHA', 'HIGHLIGHT'])
def test_anchor_bound_local_repair_preserves_title_and_independently_checks_new_sentence(kind):
    packet, calls = exercise(kind=kind)
    assert packet['reviewed']['M01']['title'] == '红褐色的小熊猫'
    assert len(calls) == 2 and all(c['images'] for c in calls)
    assert calls[0]['context']['frame_refs'] == [{'source_asset_id': 'V006', 'frame_id': 'asset-5-f0'}]
    assert calls[0]['context']['protected_fields'] == ['title']
    assert [c['field'] for c in calls[1]['context']['claims']] == ['SENTENCE']
    assert packet['final_moment_repair_ledger'][0]['status'].startswith('ACCEPTED_AFTER_INDEPENDENT')
    assert packet['final_verification_output']['items'][0]['sentences'][0]['supported'] is False


@pytest.mark.parametrize('mode', ['both', 'spatial'])
def test_both_failed_title_and_sentence_require_new_independent_approval(mode):
    packet, calls = exercise(mode)
    assert packet['reviewed']['M01']
    assert {c['field'] for c in calls[1]['context']['claims']} == {'TITLE', 'SENTENCE'}


@pytest.mark.parametrize('mode', ['foreign', 'protected', 'self_approval', 'unchanged', 'extra_sentence',
                                  'deny', 'budget', 'changed_pixels', 'null', 'bare_null', 'spatial_repeated', 'unknown_choice', 'free_text_choice', 'no_candidate'])
def test_invalid_unverified_or_unavailable_repair_never_publishes(mode):
    packet, calls = exercise(mode)
    assert not packet['reviewed']
    assert len(calls) <= 2
    assert packet['final_moment_repair_ledger'][0]['status'] == 'BLOCKED'
    if mode == 'budget':
        assert packet['final_verification_terminal_failure']


@pytest.mark.parametrize('mode', ['terminal', 'no_anchor'])
def test_no_repair_after_terminal_provider_failure_or_without_reviewed_anchor(mode):
    packet, calls = exercise(mode)
    assert not calls and not packet['reviewed']


@pytest.mark.parametrize('mode', ['new_action', 'new_location', 'new_mood'])
def test_repair_cannot_add_facts_even_if_independent_stub_would_approve(mode):
    packet, calls = exercise(mode)
    assert not packet['reviewed']
    assert len(calls) == 1  # rejected mechanically before asking a permissive verifier
    assert 'without any free text' in packet['final_moment_repair_ledger'][0]['reason']


@pytest.mark.parametrize('original, candidate', [
    ('疑似小熊猫趴在枯木上。', '小熊猫。'),
    ('没有看见猫在树上。', '猫在树上。'),
    ('可能是水鸟站在石头上。', '水鸟。'),
    ('车在桥下，人在桥上。', '车在桥上。'),
    ('小熊猫在树上。', '小熊猫在树上'),
    ('小熊猫在树上。', '小熊猫！'),
])
def test_reduction_does_not_flip_qualifiers_stitch_relations_or_only_change_punctuation(original, candidate):
    with pytest.raises(ValueError):
        validate_reduction(original, candidate)


def test_recorded_full_run_copy_can_only_keep_the_original_subject_without_the_trunk():
    relations = [dict(subject='小熊猫', reference='枯木', source_quote='枯木上的小熊猫')]
    validate_reduction('枯木上的小熊猫', '小熊猫', relations)
    validate_reduction('红褐色小熊猫趴在横跨画面的枯木上休息。', '红褐色小熊猫。', relations)
    with pytest.raises(ValueError, match='complete original relation subject'):
        validate_reduction('枯木上的小熊猫', '熊猫', relations)
    with pytest.raises(ValueError, match='withdrawn relation'):
        validate_reduction('红褐色小熊猫趴在横跨画面的枯木上休息。', '小熊猫趴在横跨画面的枯木上。', relations)


def test_catalog_for_recorded_failure_contains_only_literal_subject_copies():
    relations = [dict(subject='小熊猫', reference='枯木', source_quote='枯木上的小熊猫')]
    draft = dict(id='M01', title='枯木上的小熊猫', title_fact_ids=['F006'],
                 sentences=[dict(source_index=0, text='红褐色小熊猫趴在横跨画面的枯木上休息。', fact_ids=['F006'])])
    choices = candidate_copies(draft, False, False, relations)
    assert len(choices) == 2
    assert {c['copy']['title'] for c in choices} == {'小熊猫'}
    assert {c['copy']['sentences'][0]['text'] for c in choices} == {'红褐色小熊猫。', '小熊猫。'}
    assert all(c['copy']['sentences'][0]['source_index'] == 0 for c in choices)


def test_no_candidate_does_not_request_free_writing_or_publish():
    packet, calls = exercise('no_candidate')
    assert not calls and not packet['reviewed']
    assert packet['final_moment_repair_ledger'][0]['reason'] == 'NO_EXTRACTIVE_CANDIDATE'


def test_same_image_title_veto_invalidates_false_body_approval_before_repair():
    packet, calls = exercise('cross_field')
    conflicts = packet['final_verification_relation_conflicts']
    assert len(conflicts) == 1 and conflicts[0]['previous_verdict']['supported'] is True
    original = packet['final_verification_output']['items'][0]
    assert original['title_supported'] is False and original['sentences'][0]['supported'] is False
    assert packet['reviewed']['M01']['title'] == '小熊猫'
    assert packet['reviewed']['M01']['story'] == '红褐色长尾的小熊猫。'
    assert calls[0]['context']['protected_fields'] == []
    assert {c['field'] for c in calls[1]['context']['claims']} == {'TITLE', 'SENTENCE'}
