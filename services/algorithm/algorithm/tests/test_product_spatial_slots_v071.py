"""Recorded contradictory phrases + synthetic geometry, not learned visual truth."""
from copy import deepcopy
import json

import jsonschema
import pytest
from diary_one_ci import product_editor as p

REF={'source_asset_id':'asset-a','frame_id':'frame-a'}


def target(text='向日葵下的金鱼'):
    return p.spatial_relation_targets({'claim_id':'Q1','text':text,'frame_refs':[REF]})[0]


def observation(t=None):
    t=t or target()
    return dict(target_id=t['target_id'],frame_ref=deepcopy(REF),subject_visible=True,reference_visible=True,
        identity_confirmed=True,same_frame=True,subject_box=[.4,.6,.6,.8],reference_box=[.2,.2,.7,.5],
        observed_relation='BELOW',support_surface='NOT_APPLICABLE',description='Synthetic fish below flower fixture')


def test_recorded_fish_direction_contradiction_is_rejected_despite_any_prior_approval():
    t=target();r=observation(t)
    r.update(observed_relation='ABOVE',subject_box=[.6,.1,.9,.5],reference_box=[.4,.7,.6,.9],
        description='金鱼处于向日葵上方，符合向日葵下的金鱼。')
    assert p.compile_spatial_observation(t,r)==(False,'SPATIAL_OBSERVED_RELATION_CONTRADICTS_TEXT')
    r['observed_relation']='BELOW'
    assert p.compile_spatial_observation(t,r)==(False,'SPATIAL_LOCALIZATION_CONTRADICTS_OBSERVED_RELATION')


def test_recorded_panda_below_beam_cannot_become_on_beam_by_yes_verdict():
    t=target('横梁上的小熊猫');r=observation(t)
    r.update(observed_relation='SUPPORTED_BY',support_surface='REFERENCE',
        subject_box=[.42,.63,.56,.72],reference_box=[0,.37,.9,.44],description='Subject supposedly supported by beam')
    assert p.compile_spatial_observation(t,r)[0] is False
    r.update(subject_box=[.42,.2,.56,.35],support_surface='OTHER_VISIBLE_SURFACE')
    assert p.compile_spatial_observation(t,r)==(False,'SPATIAL_SUPPORTING_SURFACE_NOT_CONFIRMED')


@pytest.mark.parametrize('field,value', [('same_frame',False),('identity_confirmed',False),('subject_visible',False),
    ('reference_visible',False),('frame_ref',None),('frame_ref',{'source_asset_id':'asset-b','frame_id':'frame-b'}),
    ('subject_box',None),('subject_box',[.5,.5,.5,.7]),('reference_box',[.7,.5,.2,.8])])
def test_unseen_ambiguous_foreign_frame_or_invalid_localization_fails_closed(field,value):
    r=observation();r[field]=value
    assert p.compile_spatial_observation(target(),r)[0] is False


@pytest.mark.parametrize('field,value',[('subject_box',[-.1,.1,.5,.5]),('reference_box',[.2,.3,1.1,.8]),
    ('frame_ref',{'source_asset_id':'asset-a','frame_id':'OTHER'}),('same_frame','true'),('target_id','Q_OTHER')])
def test_wire_schema_rejects_out_of_range_foreign_and_mistyped_observations(field,value):
    t=target();r=observation();r[field]=value
    assert list(jsonschema.Draft202012Validator(p.spatial_observation_schema([t],[])).iter_errors({'observations':[r],'claims':[]}))


def test_consistent_observation_can_support_only_the_same_explicit_relation():
    t=target();r=observation()
    assert p.compile_spatial_observation(t,r)[0] is True
    inverse=target('向日葵上的金鱼')
    assert p.compile_spatial_observation(inverse,r)[0] is False
    assert t['subject']=='金鱼' and t['reference']=='向日葵'
    public={k:t[k] for k in ('target_id','subject','reference','allowed_frame_refs')}
    assert '下' not in json.dumps(public,ensure_ascii=False)
    assert 'expected_relations' not in public and 'source_quote' not in public


def test_partial_or_abstract_relation_stays_in_generic_review_without_fake_parse():
    assert p.spatial_relation_targets({'claim_id':'Q','text':'动物站在横梁上，身后是山。','frame_refs':[REF]})==[]
    assert p.spatial_relation_targets({'claim_id':'Q','text':'动物园里的闲适时刻','frame_refs':[REF]})==[]


def test_english_only_public_selection_reason_falls_back_to_true_role_without_translation():
    chapters=[dict(id='C01',hero_asset_id='asset-a',hero_frame_id='frame-a',hero_reason='An animal on a branch.',
        selected_media=[dict(asset_id='asset-a',source_asset_id='asset-a',representative_frame_id='frame-a',selection_reason='An animal on a branch.'),
                        dict(asset_id='asset-b',source_asset_id='asset-b',representative_frame_id='frame-b',selection_reason='湖面映着树木。')])]
    audit=p.normalize_public_media_reasons(chapters,[])
    assert chapters[0]['hero_reason']==chapters[0]['selected_media'][0]['selection_reason']=='用作本章节封面。'
    assert chapters[0]['selected_media'][1]['selection_reason']=='湖面映着树木。'
    assert audit[0]['reason']=='PUBLIC_EXPLANATION_NOT_CHINESE'
    assert audit[0]['original_selection_reason']=='An animal on a branch.'


@pytest.mark.parametrize('variant,expected', [('same', False), ('other_frame', True), ('other_subject', True), ('plain_subject', True), ('separately_verified_relation', True)])
def test_conflict_veto_is_bound_to_same_image_entities_and_unparsed_relation(variant, expected):
    t=target('枯木上的小熊猫')
    claim=dict(claim_id='Q2', text='红褐色小熊猫趴在横跨画面的枯木上休息。', frame_refs=[deepcopy(REF)])
    if variant=='other_frame': claim['frame_refs'][0]['frame_id']='frame-b'
    if variant=='other_subject': claim['text']='水鸟趴在横跨画面的枯木上休息。'
    if variant=='plain_subject': claim['text']='红褐色小熊猫。'
    if variant=='separately_verified_relation': claim['text']='小熊猫站在枯木下。'
    judgments={'Q2': {'supported':True, 'reason':'Synthetic generic approval'}}
    batches=[{'spatial_verification': {'relation_targets':[t], 'compiled_observations':[{'target_id':t['target_id'],'supported':False}]}}]
    conflicts=p.veto_conflicting_unparsed_relations([claim],judgments,batches)
    assert judgments['Q2']['supported'] is expected
    assert bool(conflicts) is (not expected)


def test_same_parsed_relation_cannot_be_both_approved_and_rejected():
    t = target('枯木上的小熊猫')
    claim = dict(claim_id='Q2', text='枯木上的小熊猫', frame_refs=[deepcopy(REF)])
    judgments = {'Q2': {'supported': True, 'reason': 'Contradictory approval'}}
    batches = [{'spatial_verification': {'relation_targets': [t],
        'compiled_observations': [{'target_id': t['target_id'], 'supported': False}]}}]
    conflicts = p.veto_conflicting_unparsed_relations([claim], judgments, batches)
    assert not judgments['Q2']['supported']
    assert conflicts[0]['reason'] == 'SAME_RELATION_HAS_CONFLICTING_VERDICTS'
