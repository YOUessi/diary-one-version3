from final_copy_test_support import write_and_review_with_test_images
"""Contract/regression checks; scripted model outputs are not quality scores."""
import dataclasses
import json
from pathlib import Path

import jsonschema
import pytest
from diary_one_ci import product_editor as p
from diary_one_ci.x02 import run_x02_product
from diary_one_ci.x01_server import _write_x02_run_audit
from test_x02 import ScriptedGateway, make_x02_bundle, make_x02_bundle_v03


def chapter(cid='C01', fid='F001', aid='V001'):
    return dict(selection_focus=dict(experience_kind='CITYWALK', focus='街边散步', fact_ids=[fid]), id=cid, theme='街边散步', fact_ids=[fid], selected_asset_ids=[aid],
                hero_asset_id=aid, grouping_reason='A complete activity, fixture only')



def choose_media(c, context):
    """Explicit scripted image decision, never a production default."""
    candidates = context.get('media_selection_candidates')
    if candidates is None:
        return c
    choices = []
    for aid in c['selected_asset_ids']:
        candidate = next(f for f in candidates if f['asset_id'] == aid and set(f['fact_ids']) & set(c['fact_ids']))
        choices.append(dict(asset_id=aid, frame_id=candidate['frame_id'],
            fact_ids=[f for f in candidate['fact_ids'] if f in c['fact_ids']], role='PRIMARY',
            reason='Fixture explicit choice supporting the experience'))
    c['media_choices'] = choices
    c['hero_frame_id'] = next(row['frame_id'] for row in choices if row['asset_id'] == c['hero_asset_id'])
    return c


def wire_output(output, context):
    """A scripted provider response in V07's smaller internal contract."""
    from copy import deepcopy
    result = deepcopy(output)
    final = 'media_selection_candidates' in context
    result['chapters'] = []
    if final:
        result['media_choices'] = []
    for c in output['chapters']:
        focus = c['selection_focus']
        row = {k: deepcopy(c[k]) for k in ('id', 'theme', 'fact_ids', 'grouping_reason')}
        row.update(experience_kind=focus['experience_kind'], focus=focus['focus'], focus_fact_ids=focus['fact_ids'])
        if final:
            for choice in c['media_choices']:
                candidate = next(f for f in context['media_selection_candidates']
                    if f['asset_id'] == choice['asset_id'] and f['frame_id'] == choice['frame_id'])
                result['media_choices'].append(dict(chapter_id=c['id'], candidate_id=candidate['candidate_id'],
                    reason=choice['reason']))
                if choice['asset_id'] == c['hero_asset_id']:
                    row['hero_candidate_id'] = candidate['candidate_id']
        result['chapters'].append(row)
    if final and 'frame_selection_policy' in context:
        # Explicit canned judgments for synthetic pipeline fixtures. These
        # tests exercise data flow and are not image-quality evaluations.
        focus_refs = {fid for c in output['chapters'] for fid in c['selection_focus']['fact_ids']}
        result['frame_assessments'] = []
        for c in context['media_selection_candidates']:
            clue = context['frame_selection_policy']['candidate_scene_clues'][c['candidate_id']][0]
            result['frame_assessments'].append(dict(candidate_id=c['candidate_id'], fact_ids=c['fact_ids'],
                scene_observation_id=clue['scene_observation_id'], visible_detail=clue['text'],
                theme_fit='MAIN_SUBJECT' if set(c['fact_ids']) & focus_refs else 'SUPPORTING_CONTEXT',
                visibility='CLEAR', prominence='READABLE', occlusion='NONE'))
    return result


def moment(parent='C01', fid='F001'):
    return dict(id='M01', parent_chapter_id=parent, fact_id=fid, focus='骑行者回头',
                revisit_reason='A specific visible action', chapter_relations=[
                    dict(chapter_id='C01', relation='WITHIN_CHAPTER' if parent else 'DISTINCT')])


def scripted_final_verdict(context):
    """Explicit canned approval for synthetic fixtures, not visual validation."""
    if 'relation_targets' in context:
        observations = []
        for target in context['relation_targets']:
            # Synthetic image fixtures contain no real objects. These fixed
            # relations exercise the wire/geometry contract, not model vision.
            inside = any(s in target['reference'] for s in ('海湾','展柜'))
            below = '门廊' in target['reference']
            observations.append(dict(target_id=target['target_id'],frame_ref=target['allowed_frame_refs'][0],
                subject_visible=True,reference_visible=True,identity_confirmed=True,same_frame=True,
                subject_box=[.4,.6,.6,.8] if below else [.4,.3,.6,.6],
                reference_box=[0,0,1,1] if inside else [.1,.2,.9,.5] if below else [0,.6,1,.8],
                observed_relation='INSIDE' if inside else 'BELOW' if below else 'SUPPORTED_BY',
                support_surface='NOT_APPLICABLE' if inside or below else 'REFERENCE',
                description='Synthetic localized relation fixture, not visual truth'))
        return {'claims':[dict(claim_id=c['claim_id'],supported=True,reason='Synthetic fallback fixture')
                          for c in context['claims']], 'observations':observations}
    if 'claims' in context:
        return {'claims': [dict(claim_id=c['claim_id'], supported=True, reason='Synthetic final verdict fixture')
                           for c in context['claims']]}
    return {'items': [dict(id=m['id'], title_supported=True, title_reason='Synthetic final verdict fixture',
        sentences=[dict(source_index=s['source_index'], supported=True, reason='Synthetic final verdict fixture')
                   for s in m['sentence_checks']]) for m in context['items']]}


def test_parent_relation_suffices_but_standalone_requires_all_chapters():
    facts = {'F001': {'asset_id': 'V001'}, 'F002': {'asset_id': 'V002'}, 'F003': {'asset_id': 'V003'}}
    out = dict(chapters=[chapter(), chapter('C02', 'F002', 'V002')], moments=[moment()], unselected_facts=[])
    assert len(p.compile_selection(out, facts, {})[1]) == 1
    out['moments'][0]['chapter_relations'] = [{}]
    assert p.compile_selection(out, facts, {})[1][0]['chapter_relations'] == [dict(chapter_id='C01', relation='WITHIN_CHAPTER')]
    out['moments'] = [moment(None, 'F003')]
    assert not p.compile_selection(out, facts, {})[1]
    out['moments'][0]['chapter_relations'].append(dict(chapter_id='C02', relation='DISTINCT'))
    assert len(p.compile_selection(out, facts, {})[1]) == 1
    out['moments'][0]['chapter_relations'][1]['relation'] = 'UNCERTAIN'
    assert not p.compile_selection(out, facts, {})[1]


def test_standalone_cannot_republish_chapter_fact_or_asset():
    facts = {'F001': {'asset_id': 'V001'}}
    out = dict(chapters=[chapter(), chapter('C02')], moments=[moment(None)], unselected_facts=[])
    chapters, moments, rejected, _ = p.compile_selection(out, facts, {})
    assert len(chapters) == 1 and not moments and len(rejected) == 2


@pytest.mark.parametrize('mutation', ['foreign_fact', 'duplicate', 'long', 'block'])
def test_copy_cannot_escape_its_evidence_or_review(mutation):
    memories = [dict(id='M01', kind='HIGHLIGHT', fact_ids=['F001'],
                    facts=[dict(id='F001', asset_id='V001', text='骑行者在桥上回头。')])]
    row = dict(id='M01', decision='PUBLISH', title='骑行者回头', title_fact_ids=['F001'],
               sentences=[dict(text='骑行者在桥上回头。', fact_ids=['F001'])])
    if mutation == 'foreign_fact': row['sentences'][0]['fact_ids'] = ['F002']
    if mutation == 'long': row['sentences'][0]['text'] = '长' * 29
    if mutation == 'block': row['decision'] = 'BLOCK'
    out = {'items': [row, row] if mutation == 'duplicate' else [row]}
    assert not p.compile_copy(out, memories, review=True)[0]


class Gateway(ScriptedGateway):
    def __init__(self, review_fails=False):
        super().__init__()
        self.review_fails = review_fails

    def call(self, stage, prompt, schema, evidence=(), context=None):
        result = super().call(stage, prompt, schema, evidence, context)
        if '_FINAL_VERIFY' in stage:
            return dataclasses.replace(result, output=scripted_final_verdict(context))
        if stage in ('S07_PRODUCT_EDITOR', 'S08_PRODUCT_STRUCTURE_REVIEW', 'S09_PRODUCT_CONTRACT_REPAIR', 'S09B_PRODUCT_VERIFIED_STRUCTURE', 'S09C_PRODUCT_VERIFIED_REPAIR'):
            output = wire_output(dict(chapters=[choose_media(chapter(), context)], moments=[moment()], unselected_facts=[], chapter_boundaries=[]), context)
        elif stage.startswith('S09A_FRAME_OBSERVATION'):
            # Explicit observation of the synthetic fixture images. Validate
            # the P/image mapping; no production or missing-response fallback.
            assert len(evidence) == len(context['candidate_frames'])
            output = {'images': []}
            for c, (asset, frame, _) in zip(context['candidate_frames'], evidence):
                assert c['frame_id'] == frame['frame_id']
                index = asset.get('sequence_index', int(asset.get('timeline_offset_ms', 0)) // 120_000)
                expected = '第%d项可见historic_town_walk。' % (index + 1)
                assert all(f['text'] == expected for f in c['facts'])
                output['images'].append(dict(candidate_id=c['candidate_id'], observation=expected,
                    subject_role='SPECIFIC_SUBJECT', visibility='CLEAR', prominence='READABLE', occlusion='NONE',
                    fact_checks=[dict(fact_id=f['fact_id'], support='VISIBLE', visible_quote=expected,
                        not_visible_quote='') for f in c['facts']]))
        elif stage.startswith(('S09A_PRODUCT_VISUAL', 'S14A_PRODUCT_VISUAL')):
            if stage.endswith('_SCENE'):
                output = {'assets': [dict(asset_id=aid, observations=[dict(text='街边有人散步。',
                    evidence_frame_ids=[x['id'] for x in frames], temporal_support='STATE')], uncertainties=[])
                    for aid, frames in context['shown_frames'].items()]}
                return dataclasses.replace(result, output=output)
            output = {'items': [dict(fact_id=f['fact_id'], decision='KEEP', text=f['text'],
                evidence_frame_ids=[x['id'] for x in context['shown_frames'][f['asset_id']]],
                temporal_support='STATE', reason='Fixture visual check', corrections=[]) for f in context['facts']]}
        elif stage in ('S10_PRODUCT_MOMENT_VALUE', 'S14C_PRODUCT_MOMENT_VALUE'):
            by_fact = {f['id']: f for f in context['facts']}
            output = {'items': [dict(id=m['id'], decision='KEEP', anchor=m['focus'], value_type='DISTINCT_DETAIL',
                scene_kind='OTHER', scene_basis_fact_ids=[m['fact_id']],
                event_group_id=m['id'], comparison_reason='Fixture unique event among candidates',
                focus_frame_id=by_fact[m['fact_id']]['evidence_frame_ids'][0],
                evidence_frame_ids=by_fact[m['fact_id']]['evidence_frame_ids'], reason='Fixture value check') for m in context['moments']]}
        elif stage in ('S11_PRODUCT_WRITER', 'S12_PRODUCT_FACT_REVIEW', 'S13_PRODUCT_COPY_REPAIR_VERIFY', 'S17_PRODUCT_RECOVERY_REPAIR_VERIFY'):
            if stage == 'S12_PRODUCT_FACT_REVIEW' and self.review_fails:
                raise ValueError('Simulated invalid review response')
            if stage.endswith('_VERIFY'):
                output = {'items': [dict(id=m['id'], title='街边散步', decision='PUBLISH', reason='Fixture',
                    title_fact_ids=m.get('title_fact_ids', m.get('fact_ids')),
                    sentences=[dict(text='街边有人散步。', fact_ids=[g['facts'][0]['id']], source_index=g['source_index'])
                        for g in m['sentence_checks']] if 'sentence_checks' in m else
                        [dict(text='街边有人散步。', fact_ids=m['fact_ids'])], voice_issues=[])
                    for m in context['items']]}
                return dataclasses.replace(result, output=output)
            output = {'items': [dict(id=m['id'], title='街边散步', story='街边有人散步。')
                if stage == 'S11_PRODUCT_WRITER' and m['kind'] == 'CHAPTER' else
                dict(id=m['id'], title='街边散步', decision='PUBLISH', reason='Fixture',
                title_fact_ids=m['fact_ids'],
                sentences=[dict(text='街边有人散步。', fact_ids=m['fact_ids'], **({'source_index': 0} if 'source_sentences' in m else {}))]) for m in context['items']]}
        else:
            return result
        return dataclasses.replace(result, output=output)


def test_full_pipeline_retains_low_salience_and_nested_highlight(tmp_path):
    path = make_x02_bundle(tmp_path, 1)
    result = run_x02_product(path, Gateway())
    assert result['delivery_state'] == 'READY_PRIMARY_COPY'
    assert len(result['decision_trace']['editor_input']['facts']) == 1
    c = result['chapters'][0]
    assert len(c['selected_media']) == 1  # No fake padding to three clips.
    assert c['highlights'][0]['parent_chapter_id'] == c['id']
    assert not result['ahas']
    assert c['highlights'][0]['selected_media'][0]['range_basis'] == 'WHOLE_SOURCE_CLIP'
    assert c['highlights'][0]['selected_media'][0]['focus_pts_ms'] is not None
    schema = json.loads((Path(__file__).parents[1] / 'contracts/product_preview_v01.schema.json').read_text())
    jsonschema.validate(result, schema)
    _write_x02_run_audit(tmp_path / 'audit', json.loads(path.read_text()), result, 0, 0, 0)
    assert list((tmp_path / 'audit').rglob('run_audit.json'))


def test_failed_review_never_publishes_raw_fact_fallback(tmp_path):
    result = run_x02_product(make_x02_bundle(tmp_path, 1), Gateway(review_fails=True))
    assert result['delivery_state'] == 'PIPELINE_BLOCKED'
    assert not result['chapters'] and not result['ahas']
    assert result['decision_trace']['selected_structure']['chapters']
    assert result['decision_trace']['drafts']


def test_style_repair_transport_failure_preserves_fact_reviewed_copy(tmp_path):
    class StyleFailure(Gateway):
        def call(self, stage, *args, **kwargs):
            if stage == 'S13_PRODUCT_COPY_REPAIR':
                raise TimeoutError('Simulated style repair outage')
            result = super().call(stage, *args, **kwargs)
            if stage == 'S12_PRODUCT_FACT_REVIEW':
                for item in result.output['items']:
                    item['sentences'][0]['text'] = '画面中有人散步。'
            return result
    result = run_x02_product(make_x02_bundle(tmp_path, 1), StyleFailure())
    assert result['chapters'] and result['chapters'][0]['copy_review_flags'] == ['画面中']
    assert len(result['decision_trace']['transport_failures']) == 2


def test_one_lost_structure_response_is_retried_without_publishing_empty_day(tmp_path):
    class Interrupted(Gateway):
        attempts = 0
        def call(self, stage, *args, **kwargs):
            if stage == 'S08_PRODUCT_STRUCTURE_REVIEW':
                self.attempts += 1
                if self.attempts == 1:
                    raise TimeoutError('Lost transport')
            return super().call(stage, *args, **kwargs)
    gateway = Interrupted()
    result = run_x02_product(make_x02_bundle(tmp_path, 1), gateway)
    assert gateway.attempts == 2 and result['chapters']
    assert result['decision_trace']['transport_failures'][0]['usage_known'] is False


def scoped_memory():
    return dict(id='C01', kind='CHAPTER', fact_ids=['F001', 'F002', 'F003'], facts=[
        dict(id='F001', asset_id='V001', text='骑行经过竹林小路。'),
        dict(id='F002', asset_id='V002', text='路边停着卡车，远处有输电塔。'),
        dict(id='F003', asset_id='V001', text='小路旁有护栏。')])


def copy_row(sentences, title='竹林小路骑行', title_ids=None):
    return dict(id='C01', title=title, title_fact_ids=title_ids or ['F001'],
                decision='PUBLISH', reason='Fixture only', sentences=[
                    dict(text=t, fact_ids=ids) for t, ids in sentences])


@pytest.mark.parametrize(('sentences', 'title', 'expected'), [
    ([('竹林小路旁停着卡车。', ['F001', 'F002'])], '竹林小路骑行', 'MULTI_ASSET_SENTENCE'),
    ([('骑行经过竹林。', ['F001']), ('随后来到停着卡车的路边。', ['F002'])], '竹林小路骑行', 'CROSS_CLIP_TRANSITION'),
    ([('骑行经过竹林。', ['F001'])], '竹林通勤独行', 'UNSUPPORTED_CONTEXT'),
    ([('和同伴骑行经过竹林。', ['F001'])], '竹林小路骑行', 'UNSUPPORTED_CONTEXT'),
])
def test_publication_blocks_cross_clip_splicing_and_unsupported_context(sentences, title, expected):
    accepted, ledger = p.compile_copy({'items': [copy_row(sentences, title)]}, [scoped_memory()], review=True)
    assert not accepted and expected in ledger[0]['reason']


def test_single_clip_multi_fact_and_independent_sentences_are_allowed():
    row = copy_row([('骑行经过竹林，小路旁有护栏。', ['F001', 'F003']),
                    ('路边停着卡车，远处有输电塔。', ['F002'])])
    assert p.compile_copy({'items': [row]}, [scoped_memory()], review=True)[0]
    row['title_fact_ids'] = ['F999']
    assert not p.compile_copy({'items': [row]}, [scoped_memory()], review=True)[0]


def test_grounding_edits_existing_sentences_without_expanding_into_a_scene_inventory():
    memory = scoped_memory()
    memory['source_sentences'] = [{'source_index': 0, 'text': '骑车经过竹林。'}]
    row = copy_row([('骑车经过竹林。', ['F001'])])
    row['sentences'][0]['source_index'] = 0
    accepted, _ = p.compile_copy({'items': [row]}, [memory], review=True)
    assert 'source_index' not in accepted['C01']['sentences'][0]  # Audit field stays out of app contract.
    row['sentences'].append(dict(text='路边停着卡车。', fact_ids=['F002'], source_index=1))
    assert not p.compile_copy({'items': [row]}, [memory], review=True)[0]
    row['sentences'][1]['source_index'] = 0
    assert not p.compile_copy({'items': [row]}, [memory], review=True)[0]


def test_visible_coverage_excludes_failed_parent_and_unselected_media():
    c = chapter(); c['fact_ids'] = ['F001', 'F002']
    facts = {'F001': {'asset_id': 'V001'}, 'F002': {'asset_id': 'V002'}}
    m = moment(fid='F002')
    assert p.visible_assets([c], [m], {'M01': {}}, facts) == set()
    assert p.visible_assets([c], [m], {'C01': {}}, facts) == {'V001'}
    assert p.visible_assets([c], [m], {'C01': {}, 'M01': {}}, facts) == {'V001', 'V002'}


def recovery_decision(aid='V002', fid='F002', mid='M90'):
    m = moment(None, fid); m['id'] = mid
    return dict(asset_id=aid, disposition='ADD_MEMORY', reason='Distinct supported experience', moment=m)


def test_recovery_must_cover_missing_assets_and_obey_identity_evidence_and_capacity():
    facts = {f'F00{i}': {'asset_id': f'V00{i}'} for i in range(1, 7)}
    def compile(rows, current=None, reserved=None):
        return p.compile_recovery({'decisions': rows}, {'V002'}, [chapter()], current or [], facts, {}, reserved or set())
    row = recovery_decision()
    assert len(compile([row])[0]) == 1
    assert not compile([row, row])[0]
    assert not compile([recovery_decision(fid='F003')])[0]
    assert not compile([row], reserved={'M90'})[0]
    existing = [recovery_decision(aid=f'V00{i}', fid=f'F00{i}', mid=f'M0{i}')['moment'] for i in range(3, 6)]
    assert not compile([row], current=existing)[0]
    assert compile([])[1][0]['status'] == 'BLOCKED'


def test_invalid_writer_draft_is_repaired_in_fact_review_not_silently_lost(tmp_path):
    class InvalidDraft(Gateway):
        def call(self, stage, *args, **kwargs):
            run = super().call(stage, *args, **kwargs)
            if stage == 'S11_PRODUCT_WRITER':
                for item in run.output['items']:
                    item['title'] = '下班通勤'
            return run
    result = run_x02_product(make_x02_bundle(tmp_path, 1), InvalidDraft())
    assert result['chapters']
    assert result['decision_trace']['writer_output']['items'][0]['title'] == '下班通勤'
    chapter_draft = next(r for r in result['decision_trace']['writer_items'] if r['id'] == 'C01')
    assert chapter_draft['status'] == 'DRAFT_REQUIRES_GROUNDING'
    assert '通勤' not in result['chapters'][0]['title']


def test_recovery_is_run_after_failed_copy_and_still_requires_its_own_review(tmp_path):
    class Recovery(Gateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            run = super().call(stage, prompt, schema, evidence, context)
            if stage in ('S12_PRODUCT_FACT_REVIEW', 'S13_PRODUCT_COPY_REPAIR'):
                return dataclasses.replace(run, output={'items': []})
            if stage == 'S14_PRODUCT_COVERAGE_REVIEW':
                assert context['unrepresented_assets'] == ['V001']
                assert not context['published_chapters']
                row = recovery_decision('V001', 'F001')
                row['moment']['chapter_relations'] = []
                return dataclasses.replace(run, output={'decisions': [row]})
            if stage in ('S15_PRODUCT_RECOVERY_WRITER', 'S16_PRODUCT_RECOVERY_REVIEW'):
                row = copy_row([('街边有人散步。', ['F001'])], title='街边散步')
                row['id'] = 'M90'
                return dataclasses.replace(run, output={'items': [row]})
            return run
    result = run_x02_product(make_x02_bundle(tmp_path, 1), Recovery())
    assert not result['chapters'] and len(result['ahas']) == 1
    assert result['decision_trace']['publication_asset_coverage'][0]['status'] == 'VISIBLE'
    assert result['decision_trace']['recovery_copy']['review_ledger'][0]['reviewed'] is True


def test_chapter_keeps_all_facts_and_has_no_length_or_sentence_target():
    facts = {f'F00{i}': dict(id=f'F00{i}', text=f'Fixture {i}', support_grade='STRONG', asset_id=f'V00{i}', frame_pts_ms=[0])
             for i in range(1, 5)}
    c = chapter(); c['fact_ids'] = list(facts); c['selected_asset_ids'] = [f'V00{i}' for i in range(1, 5)]
    memories = p.memory_specs([c], [], facts)
    assert memories[0]['fact_ids'] == list(facts)
    # A richer paragraph must survive writer, reviewer, and public wire contracts.
    row = copy_row([('小路旁的竹林向两侧铺开，骑车经过时，绿色的竹叶铺满小路两旁。' * 2, [fid]) for fid in facts])
    row['voice_issues'] = []
    result, ledger = p.compile_copy({'items': [row]}, memories, review=True)
    assert len(result['C01']['story']) > 120 and not ledger[0]['style_flags']
    jsonschema.validate({'items': [row]}, p.copy_schema(memories, review=True))
    wire = json.loads((Path(__file__).parents[1] / 'contracts/product_preview_v01.schema.json').read_text())
    jsonschema.validate(result['C01']['story'], wire['$defs']['chapter']['properties']['story'])
    jsonschema.validate(row['sentences'], wire['$defs']['chapter']['properties']['sentence_claims'])
    jsonschema.validate({'items': [{'id': 'C01', 'title': row['title'], 'story': result['C01']['story']}]},
                        p.writer_schema(memories))
    # A single supported sentence remains valid too; no padding requirement.
    row['sentences'] = [dict(text='骑车经过竹林。', fact_ids=['F001'])]
    assert p.compile_copy({'items': [row]}, memories, review=True)[0]


def test_narrative_material_has_no_count_quota_and_review_keeps_full_facts():
    facts = {f'F00{i}': dict(id=f'F00{i}', text='骑车经过竹林。', support_grade='STRONG',
                            asset_id=f'V00{i}', frame_pts_ms=[0]) for i in range(1, 5)}
    c = chapter(); c['fact_ids'] = list(facts)
    def ask(stage, prompt, schema, context, *, evidence=()):
        if '_FINAL_VERIFY' in stage:
            return scripted_final_verdict(context)
        if stage.endswith('_NARRATIVE_BRIEF'):
            return {'items': [{'id': 'C01', 'details': [
                {'fact_id': fid, 'evidence_quote': '骑车经过竹林。', 'role': 'MAIN'} for fid in facts]}]}
        if stage == 'WRITE':
            m = context['items'][0]
            assert [d['fact_id'] for d in m['writing_material']] == list(facts)
            assert len(m['writing_material']) == 4
            assert 'angle' not in m and 'narrative_brief' not in m
            assert 'facts' not in m
            return {'items': [{'id': 'C01', 'title': '竹林骑行', 'story': '骑车经过竹林。'}]}
        assert len(context['items'][0]['facts']) == 4
        row = copy_row([('骑车经过竹林。', ['F001'])])
        row['sentences'][0]['source_index'] = 0
        return {'items': [row]}
    packet = write_and_review_with_test_images(p.memory_specs([c], [], facts), ('WRITE', 'REVIEW', 'REPAIR'),
                                ask=ask, time_basis='IMPORT_ORDER_ONLY', stage_runs=[])
    assert packet['reviewed'] and len(c['fact_ids']) == 4



def test_bridge_surface_equivalent_is_allowed_but_overhead_inference_is_not():
    memory = scoped_memory()
    memory['facts'][0]['text'] = '前方有高架桥，一辆列车驶过桥面。'
    row = copy_row([('前方高架桥上有列车驶过。', ['F001'])], title='列车驶过桥面')
    assert p.compile_copy({'items': [row]}, [memory], review=True)[0]
    row['sentences'][0]['text'] = '列车从头顶的高架桥驶过。'
    assert not p.compile_copy({'items': [row]}, [memory], review=True)[0]


@pytest.mark.parametrize('judgment', ['DISTINCT', 'WITHIN_CHAPTER', 'UNCERTAIN', None])
def test_missing_relations_need_explicit_complete_judgment_not_default_distinct(judgment):
    row = recovery_decision(); row['moment']['chapter_relations'] = []
    output = {'decisions': [row]}; chapters = [chapter()]
    candidates = p.recovery_relation_candidates(output, chapters)
    assert len(candidates) == 1
    response = {'items': [{'moment_id': 'M90', 'relations': {'C01': judgment} if judgment else {}}]}
    corrected = p.apply_relation_review(output, response, candidates, chapters)
    assert output['decisions'][0]['moment']['chapter_relations'] == []
    facts = {'F001': {'asset_id': 'V001'}, 'F002': {'asset_id': 'V002'}}
    additions, _ = p.compile_recovery(corrected, {'V002'}, chapters, [], facts, {}, set())
    assert bool(additions) is (judgment == 'DISTINCT')


def test_relation_review_leaves_complete_records_alone_and_does_not_accept_duplicate_rows():
    output = {'decisions': [recovery_decision()]}; chapters = [chapter()]
    assert not p.recovery_relation_candidates(output, chapters)
    output['decisions'][0]['moment']['chapter_relations'] = [{}]
    candidates = p.recovery_relation_candidates(output, chapters)
    row = {'moment_id': 'M90', 'relations': {'C01': 'DISTINCT'}}
    corrected = p.apply_relation_review(output, {'items': [row, row]}, candidates, chapters)
    assert corrected == output


def split_structure():
    facts = {'F001': {'asset_id': 'V001'}, 'F002': {'asset_id': 'V002'},
             'F003': {'asset_id': 'V001'}}
    output = dict(chapters=[chapter(), chapter('C02', 'F002', 'V002')], moments=[], unselected_facts=[],
        chapter_boundaries=[dict(chapter_ids=['C01', 'C02'], basis='DIFFERENT_ACTIVITY',
            evidence_fact_ids=['F001', 'F002'], reason='骑行与室内市场购物是不同活动')])
    return facts, output


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'scenery', 'capacity', 'one_sided', 'foreign', 'blank'])
def test_chapter_split_requires_complete_owned_experience_evidence(fault):
    facts, output = split_structure()
    row = output['chapter_boundaries'][0]
    if fault == 'missing': output['chapter_boundaries'] = []
    elif fault == 'duplicate': output['chapter_boundaries'].append(dict(row))
    elif fault == 'scenery': row['basis'] = 'SCENERY_CHANGE'
    elif fault == 'capacity': row['basis'] = 'MEDIA_CAPACITY'
    elif fault == 'one_sided': row['evidence_fact_ids'] = ['F001', 'F003']
    elif fault == 'foreign': row['evidence_fact_ids'] = ['F001', 'F999']
    elif fault == 'blank': row['reason'] = ' '
    chapters, _, rejected, _ = p.compile_selection(output, facts, {}, enforce_boundaries=True)
    assert not chapters and any(r['item'] == 'chapter_boundaries' for r in rejected)


def test_two_small_independent_experiences_can_be_chapters_without_three_clip_minimum():
    facts, output = split_structure()
    chapters, _, rejected, _ = p.compile_selection(output, facts, {}, enforce_boundaries=True)
    assert len(chapters) == 2 and not rejected
    jsonschema.validate(output, p.EDITOR_SCHEMA)


def test_boundary_cannot_omit_nonadjacent_chapter_comparison():
    facts, output = split_structure()
    facts['F004'] = {'asset_id': 'V004'}
    output['chapters'].append(chapter('C03', 'F004', 'V004'))
    output['chapter_boundaries'].append(dict(chapter_ids=['C02', 'C03'], basis='SEPARATE_EXPERIENCE',
        evidence_fact_ids=['F002', 'F004'], reason='另一个独立经历'))
    assert p.chapter_boundary_issues(output, output['chapters'])
    output['chapter_boundaries'].append(dict(chapter_ids=['C01', 'C03'], basis='SEPARATE_EXPERIENCE',
        evidence_fact_ids=['F001', 'F004'], reason='不同活动的事实支持'))
    assert not p.chapter_boundary_issues(output, output['chapters'])


def test_one_experience_retains_facts_and_highlight_outside_five_display_clips():
    facts = {f'F{i:03}': {'asset_id': f'V{i:03}'} for i in range(1, 9)}
    c = chapter(); c['fact_ids'] = list(facts)
    c['selected_asset_ids'] = [f'V{i:03}' for i in range(1, 6)]
    output = dict(chapters=[c], moments=[moment(fid='F008')], chapter_boundaries=[], unselected_facts=[])
    chapters, moments, rejected, _ = p.compile_selection(output, facts, {}, enforce_boundaries=True)
    assert not rejected and len(chapters) == 1 and len(chapters[0]['fact_ids']) == 8
    assert p.visible_assets(chapters, moments, {'C01': {}, 'M01': {}}, facts) == {
        'V001', 'V002', 'V003', 'V004', 'V005', 'V008'}


def test_pipeline_reviews_evidence_beyond_representative_media_and_does_not_infer_chapter_count(tmp_path):
    class AllExperience(Gateway):
        seen_visual_assets = set()
        def call(self, stage, prompt, schema, evidence=(), context=None):
            result = super().call(stage, prompt, schema, evidence, context)
            if stage in ('S07_PRODUCT_EDITOR', 'S08_PRODUCT_STRUCTURE_REVIEW', 'S09B_PRODUCT_VERIFIED_STRUCTURE'):
                assert context['chapter_limit'] == 5  # V2 capacity, not a mandatory five-Chapter target.
                c = chapter(); c['fact_ids'] = [f['id'] for f in context['facts']]
                c['selected_asset_ids'] = list(dict.fromkeys(f['asset_id'] for f in context['facts']))[:5]
                output = dict(chapters=[choose_media(c, context)], moments=[moment(fid=c['fact_ids'][-1])],
                              chapter_boundaries=[], unselected_facts=[])
                return dataclasses.replace(result, output=wire_output(output, context))
            if stage.startswith('S09A_PRODUCT_VISUAL'):
                self.seen_visual_assets.update(a for a in context['shown_frames'] if a.startswith('V'))
            return result
    gateway = AllExperience()
    result = run_x02_product(make_x02_bundle(tmp_path, 6), gateway)
    assert gateway.seen_visual_assets == {f'V{i:03}' for i in range(1, 7)}
    assert len(result['decision_trace']['verified_facts']) == 6
    assert len(result['decision_trace']['selected_structure']['chapters']) == 1


def test_missing_split_basis_is_repaired_before_visual_or_writer_stages(tmp_path):
    class MissingBoundary(Gateway):
        repaired = False
        def call(self, stage, prompt, schema, evidence=(), context=None):
            result = super().call(stage, prompt, schema, evidence, context)
            if stage in ('S07_PRODUCT_EDITOR', 'S08_PRODUCT_STRUCTURE_REVIEW'):
                return dataclasses.replace(result, output=wire_output(dict(chapters=[chapter(), chapter('C02', 'F002', 'V002')],
                    moments=[], unselected_facts=[], chapter_boundaries=[]), context))
            if stage in ('S09_PRODUCT_CONTRACT_REPAIR', 'S09B_PRODUCT_VERIFIED_STRUCTURE'):
                if stage == 'S09_PRODUCT_CONTRACT_REPAIR':
                    assert any(r['item'] == 'chapter_boundaries' for r in context['issues'])
                    self.repaired = True
                c = chapter(); c['fact_ids'] = ['F001', 'F002']; c['selected_asset_ids'] = ['V001', 'V002']
                return dataclasses.replace(result, output=wire_output(dict(chapters=[choose_media(c, context)], moments=[], unselected_facts=[], chapter_boundaries=[]), context))
            if stage.startswith('S09A_PRODUCT_VISUAL') or stage == 'S11_PRODUCT_WRITER':
                assert self.repaired
            return result
    gateway = MissingBoundary()
    result = run_x02_product(make_x02_bundle(tmp_path, 2), gateway)
    assert gateway.repaired
    assert len(result['decision_trace']['selected_structure']['chapters']) == 1
    assert result['decision_trace']['contract_repair_issues']
    assert not result['decision_trace']['rejected_items']


@pytest.mark.parametrize('field', ['selected_asset_ids', 'hero_asset_id', 'fact_ids', 'boundary_fact', 'moment_fact', 'unselected_fact'])
def test_structure_schema_rejects_wrong_reference_namespace(field):
    facts, output = split_structure()
    facts = {k: v for k, v in facts.items() if k != 'F003'}
    schema = p.selection_schema(facts, {'V001': {}, 'V002': {}}, 2)
    jsonschema.validate(output, schema)
    if field == 'selected_asset_ids': output['chapters'][0][field] = ['f001']
    elif field == 'hero_asset_id': output['chapters'][0][field] = 'F001'
    elif field == 'fact_ids': output['chapters'][0][field] = ['V001']
    elif field == 'boundary_fact': output['chapter_boundaries'][0]['evidence_fact_ids'] = ['F001', 'F999']
    elif field == 'moment_fact': output['moments'] = [moment(fid='f001')]
    elif field == 'unselected_fact': output['unselected_facts'] = [dict(fact_id='F999', reason='未知')]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(output, schema)


@pytest.mark.parametrize(('field', 'bad_value', 'expected_allowed'), [
    ('selected_asset_ids', ['f001'], 'V001'), ('hero_asset_id', 'f001', 'V001'), ('fact_ids', ['f001'], 'F001')])
def test_structure_repair_errors_name_actual_field_bad_value_and_allowed_ids(field, bad_value, expected_allowed):
    facts, output = split_structure()
    output['chapters'][0][field] = bad_value
    _, _, rejected, _ = p.compile_selection(output, facts, {})
    issue = next(r['reason'] for r in rejected if r['item'] == 'C01')
    assert 'chapters.C01.' + field in issue
    assert 'f001' in issue and 'allowed=' in issue and expected_allowed in issue


def test_structure_schema_rebuilt_after_visual_drops_a_fact():
    facts, _ = split_structure()
    assets = {'V001': {}, 'V002': {}}
    before = p.selection_schema(facts, assets)
    after = p.selection_schema({'F001': facts['F001']}, assets)
    def refs(schema):
        chapter = schema['properties']['chapters']['items']['properties']
        return chapter['fact_ids']['items']['enum'], chapter['selected_asset_ids']['items']['enum']
    assert refs(before) == (['F001', 'F002', 'F003'], ['V001', 'V002'])
    assert refs(after) == (['F001'], ['V001'])
    assert p.EDITOR_SCHEMA['properties']['chapters']['items']['properties']['fact_ids']['items'] == p.STRING


def test_unselected_unknown_fact_is_a_repairable_error_not_silently_discarded():
    facts, output = split_structure()
    output['unselected_facts'] = [dict(fact_id='f009', reason='重复路面')]
    _, _, rejected, _ = p.compile_selection(output, facts, {})
    issue = next(r['reason'] for r in rejected if r['item'] == 'unselected_facts')
    assert 'unselected_facts[0].fact_id' in issue and 'f009' in issue and 'F001' in issue


def test_boundary_repair_lists_exact_missing_pairs_and_schema_permits_merging():
    facts, output = split_structure()
    output['chapter_boundaries'] = []
    issues = p.chapter_boundary_issues(output, output['chapters'])
    assert issues[-1]['missing_pairs'] == [['C01', 'C02']]
    assert 'C01' in issues[-1]['reason'] and 'C02' in issues[-1]['reason']
    schema = p.selection_schema(facts, {'V001': {}, 'V002': {}})
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate(output, schema)
    c = chapter(); c['fact_ids'] = list(facts); c['selected_asset_ids'] = ['V001', 'V002']
    merged = dict(chapters=[c], chapter_boundaries=[], moments=[], unselected_facts=[])
    jsonschema.validate(merged, schema)  # The same schema must not freeze the original count.


def test_four_chapters_require_all_six_boundaries_without_fixed_chapter_count():
    facts = {f'F{i:03}': {'asset_id': f'V{i:03}'} for i in range(1, 5)}
    chapters = [chapter(f'C{i:02}', f'F{i:03}', f'V{i:03}') for i in range(1, 5)]
    output = dict(chapters=chapters, chapter_boundaries=[], moments=[], unselected_facts=[])
    issue = p.chapter_boundary_issues(output, chapters)[-1]
    assert issue['missing_pairs'] == [['C01','C02'], ['C01','C03'], ['C01','C04'], ['C02','C03'], ['C02','C04'], ['C03','C04']]
    schema = p.selection_schema(facts, {f'V{i:03}': {} for i in range(1, 5)})
    for a, b in issue['missing_pairs']:
        output['chapter_boundaries'].append(dict(chapter_ids=[a, b], basis='DIFFERENT_ACTIVITY',
            evidence_fact_ids=['F0'+a[1:], 'F0'+b[1:]], reason='活动不同'))
    jsonschema.validate(output, schema)
    output['chapter_boundaries'].pop()
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate(output, schema)


def test_repair_verification_has_local_evidence_and_cannot_borrow_another_sentences_video():
    memory = scoped_memory()
    memory['evidence_groups'] = [{'asset_id': a, 'facts': [f for f in memory['facts'] if f['asset_id'] == a]}
                                 for a in ['V001', 'V002']]
    memory['source_sentences'] = [{'source_index': 0, 'text': '骑车经过竹林。'},
                                {'source_index': 1, 'text': '竹林后，来到路边卡车旁。'}]
    row = copy_row([('骑车经过竹林。', ['F001']), ('竹林后，来到路边卡车旁。', ['F002'])])
    row['voice_issues'] = []
    for i, sentence in enumerate(row['sentences']): sentence['source_index'] = i
    compiled, context = p.sentence_verification_items([memory], {'items': [row]})
    assert 'facts' not in context[0] and 'draft' not in context[0] and 'evidence_groups' not in context[0]
    assert [f['id'] for f in context[0]['sentence_checks'][1]['facts']] == ['F002']
    assert '竹林' not in str(context[0]['sentence_checks'][1]['facts'])
    row['sentences'][1] = dict(text='骑车经过竹林。', fact_ids=['F001'], source_index=1)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({'items': [row]}, p.copy_schema(compiled, review=True))
    accepted, ledger = p.compile_copy({'items': [row]}, compiled, review=True)
    assert not accepted and 'sentences[1].fact_ids' in ledger[0]['reason']
    row['sentences'][1] = dict(text='路边停着卡车。', fact_ids=['F002'], source_index=1)
    jsonschema.validate({'items': [row]}, p.copy_schema(compiled, review=True))
    assert p.compile_copy({'items': [row]}, compiled, review=True)[0]['C01']['story'] == '骑车经过竹林。路边停着卡车。'


def test_local_sentence_verification_may_remove_unsupported_sentence_without_padding():
    memory = scoped_memory()
    memory['evidence_groups'] = [{'asset_id': a, 'facts': [f for f in memory['facts'] if f['asset_id'] == a]}
                                 for a in ['V001', 'V002']]
    memory['source_sentences'] = [{'source_index': 0, 'text': '骑车经过竹林。'}, {'source_index': 1, 'text': '无依据的感受。'}]
    row = copy_row([('骑车经过竹林。', ['F001']), ('无依据的感受。', ['F002'])])
    for i, sentence in enumerate(row['sentences']): sentence['source_index'] = i
    compiled, _ = p.sentence_verification_items([memory], {'items': [row]})
    row['sentences'] = row['sentences'][:1]
    assert p.compile_copy({'items': [row]}, compiled, review=True)[0]['C01']['story'] == '骑车经过竹林。'


def image_choice_fixture():
    facts = {
        'F001': dict(id='F001', asset_id='V001', text='长颈鹿站在树旁。', visual_reviewed=True, evidence_frame_ids=['a0', 'a1']),
        'F002': dict(id='F002', asset_id='V002', text='参观者站在围栏旁。', visual_reviewed=True, evidence_frame_ids=['b0']),
        'F003': dict(id='F003', asset_id='V003', text='园区道路旁立着指示牌。', visual_reviewed=True, evidence_frame_ids=['c0']),
        'F004': dict(id='F004', asset_id='V004', text='另一个片段的河流。', visual_reviewed=True, evidence_frame_ids=['d0'])}
    assets = {aid: dict(asset_id=aid, frames=[dict(frame_id=frame, source_timestamp_ms=i * 1000,
                relative_path=frame + '.jpg') for i, frame in enumerate(f['evidence_frame_ids'])])
              for aid, f in [(f['asset_id'], f) for f in facts.values()]}
    shown = {aid: {f['frame_id']: f for f in a['frames']} for aid, a in assets.items()}
    c = chapter(); c.update(fact_ids=['F001', 'F002', 'F003'], selected_asset_ids=['V001','V002','V003'],
        selection_focus=dict(experience_kind='ZOO_ANIMALS', focus='动物和参观环境', fact_ids=['F001']),
        hero_frame_id='a1', media_choices=[
            dict(asset_id='V001', frame_id='a1', fact_ids=['F001'], role='PRIMARY', reason='动物主体可辨，帮助回想本章主题'),
            dict(asset_id='V002', frame_id='b0', fact_ids=['F002'], role='CONTEXT', reason='参观者与围栏补充参观环境'),
            dict(asset_id='V003', frame_id='c0', fact_ids=['F003'], role='CONTEXT', reason='园区路径补充场景')])
    output = dict(chapters=[c], moments=[], chapter_boundaries=[], unselected_facts=[dict(fact_id='F004',reason='独立未选片段')])
    return facts, assets, shown, output


def test_zoo_focus_is_grounded_without_fixed_animal_context_ratio_or_action_requirement():
    facts, assets, shown, output = image_choice_fixture()
    # One static animal view plus two contextual views is valid: no quota and
    # no forced action/interaction. This contract test is not a quality score.
    compiled, _, rejected, _ = p.compile_selection(output, facts, assets, enforce_focus=True, shown_frames=shown)
    assert not rejected and compiled[0]['selection_focus']['experience_kind'] == 'ZOO_ANIMALS'
    assert compiled[0]['hero_frame_id'] == 'a1'
    jsonschema.validate(output, p.selection_schema(facts, assets, shown_frames=shown))


@pytest.mark.parametrize('fault', ['foreign_frame', 'unshown_frame', 'outside_chapter_focus', 'duplicate_choice',
    'missing_choice', 'unverified_fact', 'wrong_fact_asset', 'unsupported_frame', 'wrong_hero', 'missing_reason'])
def test_image_choices_cannot_escape_shown_verified_chapter_evidence(fault):
    facts, assets, shown, output = image_choice_fixture()
    c = output['chapters'][0]; choice = c['media_choices'][0]
    if fault == 'foreign_frame': choice['frame_id'] = 'b0'
    elif fault == 'unshown_frame': del shown['V001']['a1']
    elif fault == 'outside_chapter_focus': c['selection_focus']['fact_ids'] = ['F004']
    elif fault == 'duplicate_choice': c['media_choices'][1] = dict(choice)
    elif fault == 'missing_choice': c['media_choices'].pop()
    elif fault == 'unverified_fact': facts['F001']['visual_reviewed'] = False
    elif fault == 'wrong_fact_asset': choice['fact_ids'] = ['F002']
    elif fault == 'unsupported_frame': facts['F001']['evidence_frame_ids'] = ['a0']
    elif fault == 'wrong_hero': c['hero_frame_id'] = 'b0'
    elif fault == 'missing_reason': choice['reason'] = ' '
    chapters, _, rejected, _ = p.compile_selection(output, facts, assets, enforce_focus=True, shown_frames=shown)
    assert not chapters and rejected


def test_image_candidate_budget_preserves_facts_and_exposes_omitted_assets(tmp_path):
    from copy import deepcopy
    from types import SimpleNamespace
    assets, facts = {}, {}
    for i in range(20):
        aid, fid = 'V%03d' % i, 'F%03d' % i
        frames = [dict(frame_id='%s-%d' % (aid, j), source_timestamp_ms=j * 1000,
                       relative_path='%s-%d.jpg' % (aid, j)) for j in range(3)]
        assets[aid] = dict(asset_id=aid, frames=frames)
        facts[fid] = dict(id=fid, asset_id=aid, visual_reviewed=True, evidence_frame_ids=[f['frame_id'] for f in frames])
    snapshot = deepcopy(facts)
    shown, evidence, audit = p.media_selection_candidates(facts, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), max_frames=18)
    assert len(evidence) == audit['shown_frame_count'] == 18
    assert audit['eligible_frame_count'] == 60 and len(audit['omitted_asset_ids']) == 2
    assert len(shown) == 18 and facts == snapshot
    assert all(frame['frame_id'] in shown[aid] for aid, asset in assets.items()
               for frame in asset['frames'] if any(e[1]['frame_id'] == frame['frame_id'] for e in evidence))
    assert 'hero_frame_id' not in audit  # Sampling never chooses a published cover.


def test_final_editor_receives_actual_frames_and_publishes_its_explicit_nonfirst_choice(tmp_path):
    class LastFrame(Gateway):
        observed_choice = None
        def call(self, stage, prompt, schema, evidence=(), context=None):
            result = super().call(stage, prompt, schema, evidence, context)
            if stage in ('S07_PRODUCT_EDITOR', 'S08_PRODUCT_STRUCTURE_REVIEW'):
                assert 'hero_frame_id' not in schema['properties']['chapters']['items']['properties']
            if stage == 'S09B_PRODUCT_VERIFIED_STRUCTURE':
                assert evidence and len(evidence) <= 18
                candidates = context['media_selection_candidates']
                assert {f['frame_id'] for f in candidates} == {f['frame_id'] for _, f, _ in evidence}
                selected = max(candidates, key=lambda f: f['pts_ms'])
                self.observed_choice = selected['frame_id']
                c = result.output['chapters'][0]
                c['hero_candidate_id'] = selected['candidate_id']
                result.output['media_choices'][0]['candidate_id'] = selected['candidate_id']
            return result
    gateway = LastFrame()
    result = run_x02_product(make_x02_bundle(tmp_path, 1), gateway)
    chapter = result['chapters'][0]; media = chapter['selected_media'][0]
    assert chapter['hero_frame_id'] == media['representative_frame_id'] == gateway.observed_choice
    assert media['evidence_frame_ids'][0] == gateway.observed_choice
    assert media['range_basis'] == 'WHOLE_SOURCE_CLIP' and media['start_ms'] == 0 and media['end_ms'] == 2300
    assert media['selection_fact_ids'] == chapter['selection_focus']['fact_ids']
    assert chapter['hero_reason'] == media['selection_reason']
    assert 'representative_frame_id' not in chapter['highlights'][0]['selected_media'][0]
    wire = json.loads((Path(__file__).parents[1]/'contracts/product_preview_v01.schema.json').read_text())
    jsonschema.validate(result, wire)
    del media['representative_frame_id']
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate(result, wire)
    result['editor_policy'] = 'EXPERIENCE_HIGHLIGHTS_NATURAL_COPY_V05'
    result['trace']['pipeline_version'] = 'X02_PRODUCT_EDITOR_V05'
    jsonschema.validate(result, wire)  # Historical outputs keep their old contract.


def test_missing_final_image_choice_is_blocked_instead_of_defaulting_to_first_frame(tmp_path):
    class MissingChoice(Gateway):
        def call(self, stage, *args, **kwargs):
            result = super().call(stage, *args, **kwargs)
            if stage in ('S09B_PRODUCT_VERIFIED_STRUCTURE', 'S09C_PRODUCT_VERIFIED_REPAIR'):
                for c in result.output['chapters']:
                    c.pop('hero_candidate_id')
                result.output.pop('media_choices')
            return result
    result = run_x02_product(make_x02_bundle(tmp_path, 1), MissingChoice())
    assert not result['chapters'] and result['delivery_state'] == 'PIPELINE_BLOCKED'
    assert result['decision_trace']['media_selection_rejections']


def test_recorded_zoo_selection_focus_aliases_normalize_without_rewriting_values_or_raw_output():
    from copy import deepcopy
    facts, assets, shown, output = image_choice_fixture()
    # Exact field pattern and text observed in the first V06 zoo run; trim only
    # the fixture fact list to the three chapter-owned IDs available here.
    aliased = {'s_experience_kind': 'ZOO_ANIMALS',
        's_focus': '记录多种展区动物的形态、神态及环境细节，展现参观过程中的生物多样性。',
        's_fact_ids': ['F001', 'F002', 'F003']}
    output['chapters'][0]['selection_focus'] = aliased
    original = deepcopy(output)
    chapters, _, rejected, _ = p.compile_selection(output, facts, assets, enforce_focus=True, shown_frames=shown)
    assert not rejected and output == original
    assert chapters[0]['selection_focus'] == {'experience_kind': aliased['s_experience_kind'],
        'focus': aliased['s_focus'], 'fact_ids': aliased['s_fact_ids']}
    assert chapters[0]['selection_focus_normalization']['rule'] == 'SELECTION_FOCUS_EXACT_S_PREFIX_ALIASES'
    chapters[0]['selection_focus']['fact_ids'].append('F999')
    assert output == original  # Compiled metadata cannot mutate the provider audit.


@pytest.mark.parametrize('mutation', ['mixed_equal', 'mixed_conflict', 'partial', 'unknown_alias', 'unknown_canonical',
                                      'invalid_kind', 'foreign_fact', 'empty_focus'])
def test_selection_focus_alias_compatibility_never_fills_or_overrides_values(mutation):
    facts, assets, shown, output = image_choice_fixture()
    focus = {'s_experience_kind': 'ZOO_ANIMALS', 's_focus': '动物细节', 's_fact_ids': ['F001']}
    if mutation == 'mixed_equal': focus['experience_kind'] = 'ZOO_ANIMALS'
    elif mutation == 'mixed_conflict': focus['experience_kind'] = 'CYCLING'
    elif mutation == 'partial': focus.pop('s_focus')
    elif mutation == 'unknown_alias': focus['s_theme'] = '动物'
    elif mutation == 'unknown_canonical': focus = {'experience_kind':'ZOO_ANIMALS', 'focus':'动物', 'fact_ids':['F001'], 'extra':'value'}
    elif mutation == 'invalid_kind': focus['s_experience_kind'] = 'ZOO'
    elif mutation == 'foreign_fact': focus['s_fact_ids'] = ['F004']
    elif mutation == 'empty_focus': focus['s_focus'] = ' '
    output['chapters'][0]['selection_focus'] = focus
    chapters, _, rejected, _ = p.compile_selection(output, facts, assets, enforce_focus=True, shown_frames=shown)
    assert not chapters and 'selection_focus' in rejected[0]['reason']


def test_v07_repairs_recorded_key_drift_without_accepting_more_aliases(tmp_path):
    class AliasedFocus(Gateway):
        def call(self, stage, *args, **kwargs):
            result = super().call(stage, *args, **kwargs)
            if stage in ('S07_PRODUCT_EDITOR', 'S08_PRODUCT_STRUCTURE_REVIEW'):
                for c in result.output['chapters']:
                    c['focuse_experience_kind'] = c.pop('experience_kind')
                    c['focuse_fact_ids'] = c.pop('focus_fact_ids')
                    c['foucs'] = c.pop('focus')
            return result
    result = run_x02_product(make_x02_bundle(tmp_path, 1), AliasedFocus())
    assert result['chapters'] and set(result['chapters'][0]['selection_focus']) == {'experience_kind','focus','fact_ids'}
    trace = result['decision_trace']
    assert 'focuse_experience_kind' in trace['editor_draft']['chapters'][0]
    assert 'focuse_experience_kind' in trace['contract_repair_issues'][0]['reason']
    assert trace['editor_output']['chapters'][0]['experience_kind'] == 'CITYWALK'
    assert not trace['selection_focus_normalizations']
    assert 'selection_focus_normalization' not in trace['selected_structure']['chapters'][0]
    wire = json.loads((Path(__file__).parents[1]/'contracts/product_preview_v01.schema.json').read_text())
    jsonschema.validate(result, wire)


def flat_image_fixture():
    facts, assets, shown, canonical = image_choice_fixture()
    candidates = []
    for aid, frames in shown.items():
        for frame_id, frame in frames.items():
            candidates.append(dict(candidate_id='P%03d' % (len(candidates) + 1), asset_id=aid,
                frame_id=frame_id, pts_ms=frame['source_timestamp_ms'],
                fact_ids=[fid for fid, fact in facts.items() if fact['asset_id'] == aid and
                          frame_id in fact['evidence_frame_ids']]))
    return facts, assets, shown, candidates, wire_output(canonical, {'media_selection_candidates': candidates})


def test_flat_wire_program_maps_chosen_picture_without_rewriting_provider_audit():
    from copy import deepcopy
    facts, assets, shown, candidates, output = flat_image_fixture()
    original = deepcopy(output)
    jsonschema.validate(output, p.structure_wire_schema(facts, candidates=candidates))
    chapters, _, rejected, _ = p.compile_structure_wire(output, facts, assets,
        candidates=candidates, shown_frames=shown)
    assert not rejected and output == original
    c = chapters[0]
    assert c['hero_asset_id'] == 'V001' and c['hero_frame_id'] == 'a1'  # Explicitly the second frame.
    assert c['selected_asset_ids'] == ['V001', 'V002', 'V003']
    assert c['media_choices'][0]['fact_ids'] == ['F001']
    assert c['selection_focus']['experience_kind'] == 'ZOO_ANIMALS'
    # The model supplies one P identity, with no opportunity to make up a
    # different asset/frame/fact mapping alongside it.
    assert set(output['media_choices'][0]) == {'chapter_id', 'candidate_id', 'reason'}
    c['selection_focus']['fact_ids'].append('F999')
    assert output == original


@pytest.mark.parametrize('fault', ['missing_frame', 'missing_all_assessments'])
def test_frame_review_failure_preserves_unrelated_chapter_and_independent_aha(fault):
    facts, assets, shown, candidates, _ = flat_image_fixture()
    scenes = [dict(asset_id=aid, observations=[dict(text=f['text'],
        evidence_frame_ids=f['evidence_frame_ids'], temporal_support='STATE')
        for f in facts.values() if f['asset_id'] == aid]) for aid in assets]
    clues = p.frame_selection.scene_clues_from_visual_outputs(
        [dict(stage='INDEPENDENT_SCENE', accepted_scenes=scenes)], candidates, facts)
    context = dict(media_selection_candidates=candidates,
        frame_selection_policy=p.frame_selection.frame_selection_context(candidates, facts, scene_clues=clues))
    c1 = choose_media(chapter(), context)
    c2 = choose_media(chapter('C02', 'F002', 'V002'), context)
    independent = moment(None, 'F004')
    independent.update(id='M02', chapter_relations=[dict(chapter_id=cid, relation='DISTINCT') for cid in ['C01', 'C02']])
    output = wire_output(dict(chapters=[c1, c2], moments=[moment(), independent],
        chapter_boundaries=[dict(chapter_ids=['C01', 'C02'], basis='SEPARATE_EXPERIENCE',
            evidence_fact_ids=['F001', 'F002'], reason='Fixture independent experiences.')],
        unselected_facts=[]), context)
    if fault == 'missing_frame':
        output['frame_assessments'] = [row for row in output['frame_assessments'] if row['candidate_id'] != 'P001']
    else:
        output.pop('frame_assessments')
    chapters, moments, rejected, coverage, audit = p.compile_assessed_structure(
        output, facts, assets, 4, candidates=candidates, shown_frames=shown, scene_clues=clues)
    assert [c['id'] for c in chapters] == ([] if fault == 'missing_all_assessments' else ['C02'])
    assert [m['id'] for m in moments] == ['M02']
    assert any(row['item'] == 'M01' for row in rejected)
    assert next(row for row in coverage if row['fact_id'] == 'F001')['status'] == 'NOT_SELECTED'
    assert next(row for row in coverage if row['fact_id'] == 'F004')['status'] == 'SELECTED'
    assert audit['automatic_replacements'] == []


def test_valid_but_weaker_cover_is_a_preference_warning_not_a_chapter_failure():
    facts, assets, shown, candidates, _ = flat_image_fixture()
    scenes = [dict(asset_id=aid, observations=[dict(text=f['text'],
        evidence_frame_ids=f['evidence_frame_ids'], temporal_support='STATE')
        for f in facts.values() if f['asset_id'] == aid]) for aid in assets]
    clues = p.frame_selection.scene_clues_from_visual_outputs(
        [dict(stage='INDEPENDENT_SCENE', accepted_scenes=scenes)], candidates, facts)
    context = dict(media_selection_candidates=candidates,
        frame_selection_policy=p.frame_selection.frame_selection_context(candidates, facts, scene_clues=clues))
    output = wire_output(dict(chapters=[choose_media(chapter(), context)], moments=[moment()],
        chapter_boundaries=[], unselected_facts=[]), context)
    output['frame_assessments'][0].update(theme_fit='SUPPORTING_CONTEXT', visibility='PARTIAL',
        prominence='TINY_OR_UNCLEAR', occlusion='DOMINANT')
    chapters, moments, rejected, _, audit = p.compile_assessed_structure(
        output, facts, assets, 4, candidates=candidates, shown_frames=shown, scene_clues=clues)
    assert [c['id'] for c in chapters] == ['C01']
    assert [m['id'] for m in moments] == ['M01']
    assert audit['preference_warnings'] and not rejected


@pytest.mark.parametrize('fault', ['fact_as_picture', 'asset_as_picture', 'unknown_picture', 'unknown_chapter',
    'duplicate_picture', 'foreign_chapter_picture', 'hero_not_selected', 'missing_hero',
    'missing_choices', 'extra_mapping', 'outside_chapter_focus', 'unshown', 'unverified'])
def test_flat_wire_cannot_bypass_image_or_evidence_boundaries(fault):
    facts, assets, shown, candidates, output = flat_image_fixture()
    c, rows = output['chapters'][0], output['media_choices']
    if fault == 'fact_as_picture': rows[0]['candidate_id'] = 'F001'
    elif fault == 'asset_as_picture': rows[0]['candidate_id'] = 'V001'
    elif fault == 'unknown_picture': rows[0]['candidate_id'] = 'P999'
    elif fault == 'unknown_chapter': rows[0]['chapter_id'] = 'C99'
    elif fault == 'duplicate_picture': rows.append(dict(rows[0]))
    elif fault == 'foreign_chapter_picture': rows[1]['candidate_id'] = 'P005'  # F004 outside this chapter.
    elif fault == 'hero_not_selected': c['hero_candidate_id'] = 'P001'
    elif fault == 'missing_hero': c.pop('hero_candidate_id')
    elif fault == 'missing_choices': output['media_choices'] = []
    elif fault == 'extra_mapping': rows[0]['asset_id'] = 'V004'
    elif fault == 'outside_chapter_focus': c['focus_fact_ids'] = ['F004']
    elif fault == 'unshown': del shown['V001']['a1']
    elif fault == 'unverified': facts['F001']['visual_reviewed'] = False
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets,
        candidates=candidates, shown_frames=shown)
    assert not chapters and issues
    if fault in ('fact_as_picture', 'asset_as_picture', 'unknown_picture'):
        assert rows[0]['candidate_id'] in issues[0]['reason'] and 'P002' in issues[0]['reason']


@pytest.mark.parametrize('malformed', ['focuse', 'nested', 'legacy_s_aliases', 'fact_as_asset'])
def test_flat_wire_rejects_recorded_v6_shapes_instead_of_growing_aliases(malformed):
    facts = {'F001': {'asset_id': 'V001'}}
    output = wire_output(dict(chapters=[chapter()], moments=[], chapter_boundaries=[], unselected_facts=[]), {})
    c = output['chapters'][0]
    if malformed == 'focuse':
        c['focuse_experience_kind'] = c.pop('experience_kind')
        c['foucs'] = c.pop('focus')
        c['focuse_fact_ids'] = c.pop('focus_fact_ids')
    elif malformed in ('nested', 'legacy_s_aliases'):
        focus = dict(experience_kind=c.pop('experience_kind'), focus=c.pop('focus'), fact_ids=c.pop('focus_fact_ids'))
        c['selection_focus'] = {'s_' + k: v for k, v in focus.items()} if malformed == 'legacy_s_aliases' else focus
    else:
        c['selected_asset_ids'] = ['F001']
        c['hero_asset_id'] = 'F001'
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(output, p.structure_wire_schema(facts))
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, {})
    assert not chapters and 'unknown=' in issues[0]['reason']


def test_initial_wire_preserves_experience_without_inventing_media_and_final_requires_picture():
    facts, assets, _, canonical = image_choice_fixture()
    output = wire_output(canonical, {})
    chapters, _, rejected, _ = p.compile_structure_wire(output, facts, assets)
    assert not rejected and chapters[0]['fact_ids'] == ['F001', 'F002', 'F003']
    assert 'selected_asset_ids' not in chapters[0] and 'hero_asset_id' not in chapters[0]
    assert 'hero_candidate_id' not in p.structure_wire_schema(facts)['properties']['chapters']['items']['properties']
    output['chapters'][0]['hero_candidate_id'] = 'P001'
    output['media_choices'] = []
    chapters, _, issues, coverage = p.compile_structure_wire(output, facts, assets, candidates=[], shown_frames={})
    assert not chapters and issues and len(coverage) == len(facts)


@pytest.mark.parametrize('kind', p.EXPERIENCE_KINDS)
def test_registered_scene_policy_can_pass_through_flat_wire_without_changing_public_focus(kind):
    from diary_one_ci.scene_selection import policy_for
    facts = {'F001': {'asset_id': 'V001'}}
    output = wire_output(dict(chapters=[chapter()], moments=[], chapter_boundaries=[], unselected_facts=[]), {})
    output['chapters'][0]['experience_kind'] = kind
    jsonschema.validate(output, p.structure_wire_schema(facts))
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, {})
    assert not issues and chapters[0]['selection_focus']['experience_kind'] == kind
    assert policy_for(kind)['experience_kind'] == kind  # Reachability, not semantic scene accuracy.


def test_scene_policies_reach_initial_final_stages_and_trace_is_bound_to_chapter(tmp_path):
    from diary_one_ci.scene_selection import selection_policy_context
    class Policies(Gateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            if stage in ('S07_PRODUCT_EDITOR', 'S09B_PRODUCT_VERIFIED_STRUCTURE'):
                assert context['scene_selection_policy'] == selection_policy_context()
                assert set(schema['properties']['chapters']['items']['properties']['experience_kind']['enum']) == set(p.EXPERIENCE_KINDS)
                if stage == 'S09B_PRODUCT_VERIFIED_STRUCTURE':
                    bound = context['chapter_selection_policies'][0]
                    assert bound['chapter_id'] == 'C01' and bound['basis_fact_ids'] == ['F001']
                    assert bound['policy']['experience_kind'] == 'CITYWALK'
            return super().call(stage, prompt, schema, evidence, context)
    result = run_x02_product(make_x02_bundle(tmp_path, 1), Policies())
    trace = result['decision_trace']
    assert trace['chapter_selection_policies'][0]['policy']['experience_kind'] == 'CITYWALK'
    assert trace['chapter_selection_policies'][0]['basis_fact_ids'] == ['F001']
    assert trace['media_selection_audit']['shown_frames'][0]['candidate_id'] == 'P001'


@pytest.mark.parametrize('invent_action_change', [False, True])
def test_photo_single_frame_has_no_video_range_or_temporal_action_highlight(tmp_path, invent_action_change):
    path = make_x02_bundle_v03(tmp_path)
    manifest = json.loads(path.read_text())
    manifest['assets'] = manifest['assets'][:1]  # Existing PHOTO_SINGLE_FRAME / PHOTO_REPRESENTATIVE fixture.
    path.write_text(json.dumps(manifest))
    assert manifest['assets'][0]['original_duration_ms'] is None
    assert manifest['assets'][0]['frames'][0]['source_timestamp_ms'] is None
    class PhotoGateway(Gateway):
        def call(self, stage, *args, **kwargs):
            result = super().call(stage, *args, **kwargs)
            if stage == 'S10_PRODUCT_MOMENT_VALUE' and invent_action_change:
                result.output['items'][0]['value_type'] = 'ACTION_CHANGE'
            return result
    result = run_x02_product(path, PhotoGateway())
    chapter = result['chapters'][0]
    media = chapter['selected_media'][0]
    assert media['media_kind'] == 'PHOTO' and media['range_basis'] == 'STILL_IMAGE'
    assert media['start_ms'] is None and media['end_ms'] is None and media['focus_pts_ms'] is None
    assert len(media['evidence_frame_ids']) == 1
    if invent_action_change:
        assert not chapter['highlights']
        assert result['decision_trace']['moment_value_ledger'][0]['status'] == 'UNVERIFIED'
    else:
        highlight_media = chapter['highlights'][0]['selected_media'][0]
        assert highlight_media['range_basis'] == 'STILL_IMAGE' and highlight_media['focus_pts_ms'] is None
    schema = json.loads((Path(__file__).parents[1]/'contracts/product_preview_v01.schema.json').read_text())
    jsonschema.validate(result, schema)


def ranked_image_fixture():
    facts, assets, shown, candidates, output = flat_image_fixture()
    frame = dict(frame_id='b1', source_timestamp_ms=3000, relative_path='b1.jpg')
    assets['V002']['frames'].append(frame); shown['V002']['b1'] = frame
    facts['F002']['evidence_frame_ids'].append('b1')
    candidates.append(dict(candidate_id='P006', asset_id='V002', frame_id='b1', pts_ms=3000, fact_ids=['F002']))
    # First proposal is not the explicit cover; first preferred V002 picture
    # is not that source's first frame. Both choices must be respected.
    output['media_choices'] = [dict(chapter_id='C01', candidate_id=pid, reason='该候选对主题有具体贡献')
                                for pid in ['P001', 'P006', 'P002', 'P003', 'P004']]
    return facts, assets, shown, candidates, output


def test_ranked_alternatives_use_explicit_hero_and_other_assets_model_preference():
    from copy import deepcopy
    facts, assets, shown, candidates, output = ranked_image_fixture()
    original = deepcopy(output)
    jsonschema.validate(output, p.structure_wire_schema(facts, candidates=candidates))
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets,
        candidates=candidates, shown_frames=shown)
    assert not issues and output == original
    c = chapters[0]
    assert [(r['asset_id'], r['frame_id'], r['role']) for r in c['media_choices']] == [
        ('V001', 'a1', 'PRIMARY'), ('V002', 'b1', 'SUPPORT'), ('V003', 'c0', 'SUPPORT')]
    audit = c['candidate_selection_audit']
    assert audit['ranked_candidate_ids'] == ['P001','P006','P002','P003','P004']
    assert audit['selected_candidate_ids'] == ['P002','P006','P004']
    assert audit['deduplicated_candidates'] == [
        dict(candidate_id='P001', asset_id='V001', representative_candidate_id='P002', reason='EXPLICIT_HERO_FOR_ASSET'),
        dict(candidate_id='P003', asset_id='V002', representative_candidate_id='P006', reason='EARLIER_MODEL_PREFERENCE_FOR_ASSET')]


@pytest.mark.parametrize('fault', ['bad_reason', 'not_shown', 'unsupported_frame', 'unknown_field', 'duplicate_p'])
def test_bad_lower_ranked_alternative_cannot_escape_validation_via_deduplication(fault):
    facts, assets, shown, candidates, output = ranked_image_fixture()
    alternative = next(r for r in output['media_choices'] if r['candidate_id'] == 'P003')
    if fault == 'bad_reason': alternative['reason'] = ' '
    elif fault == 'not_shown': del shown['V002']['b0']
    elif fault == 'unsupported_frame': facts['F002']['evidence_frame_ids'].remove('b0')
    elif fault == 'unknown_field': alternative['role'] = 'HIGHLIGHT'
    else: output['media_choices'].append(dict(alternative))
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets,
        candidates=candidates, shown_frames=shown)
    assert not chapters and issues


def test_ranked_choices_allow_more_than_five_images_and_cap_actual_assets_without_erasing_facts():
    facts, assets, shown, candidates, output = ranked_image_fixture()
    frame = dict(frame_id='c1', source_timestamp_ms=1000, relative_path='c1.jpg')
    assets['V003']['frames'].append(frame); shown['V003']['c1'] = frame
    facts['F003']['evidence_frame_ids'].append('c1')
    candidates.append(dict(candidate_id='P007', asset_id='V003', frame_id='c1', fact_ids=['F003']))
    output['media_choices'].append(dict(chapter_id='C01', candidate_id='P007', reason='同资产备选图'))
    assert len(output['media_choices']) == 6
    jsonschema.validate(output, p.structure_wire_schema(facts, candidates=candidates))
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets, candidates=candidates, shown_frames=shown)
    assert not issues and len(chapters[0]['selected_asset_ids']) == 3
    for i in range(4, 7):
        aid, fid, pid, frame_id = 'V%03d' % i, 'F%03d' % i, 'P%03d' % (i + 10), 'extra%d' % i
        frame = dict(frame_id=frame_id, source_timestamp_ms=0, relative_path=frame_id+'.jpg')
        assets[aid] = dict(asset_id=aid, frames=[frame]); shown[aid] = {frame_id: frame}
        facts[fid] = dict(id=fid, asset_id=aid, visual_reviewed=True, evidence_frame_ids=[frame_id])
        candidates.append(dict(candidate_id=pid, asset_id=aid, frame_id=frame_id, fact_ids=[fid]))
        output['chapters'][0]['fact_ids'].append(fid)
        output['media_choices'].append(dict(chapter_id='C01', candidate_id=pid, reason='另一资产代表图'))
    output['unselected_facts'] = []
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets, candidates=candidates, shown_frames=shown)
    assert not issues and chapters[0]['selected_asset_ids'] == ['V001', 'V002', 'V003', 'V004', 'V005']
    assert chapters[0]['fact_ids'] == ['F001', 'F002', 'F003', 'F004', 'F005', 'F006']
    assert chapters[0]['candidate_selection_audit']['capacity_omitted_asset_ids'] == ['V006']


def test_recorded_highlight_role_error_is_removed_from_new_wire_not_coerced_into_a_moment():
    facts, assets, shown, candidates, output = flat_image_fixture()
    next(r for r in candidates if r['candidate_id'] == 'P003')['candidate_id'] = 'P014'
    choice = output['media_choices'][1]; choice['candidate_id'] = 'P014'
    choice['role'] = 'HIGHLIGHT'  # Actual zoo failure shape: optional display semantics derailed selection.
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets, candidates=candidates, shown_frames=shown)
    assert not chapters and any("'role'" in r['reason'] for r in issues)
    choice.pop('role')
    jsonschema.validate(output, p.structure_wire_schema(facts, candidates=candidates))
    chapters, moments, issues, _ = p.compile_structure_wire(output, facts, assets, candidates=candidates, shown_frames=shown)
    assert not issues and not moments
    assert chapters[0]['media_choices'][1]['role'] == 'SUPPORT'


def capacity_image_fixture(hero='P007'):
    facts, assets, shown, candidates = {}, {}, {}, []
    for i in range(1, 8):
        aid, fid, pid, frame_id = 'V%03d' % i, 'F%03d' % i, 'P%03d' % i, 'frame-%d' % i
        frame = dict(frame_id=frame_id, source_timestamp_ms=1000, relative_path=frame_id+'.jpg')
        facts[fid] = dict(id=fid, asset_id=aid, evidence_frame_ids=[frame_id], visual_reviewed=True)
        assets[aid] = dict(asset_id=aid, frames=[frame]); shown[aid] = {frame_id: frame}
        candidates.append(dict(candidate_id=pid, asset_id=aid, frame_id=frame_id, fact_ids=[fid]))
    c = chapter(); c['fact_ids'] = list(facts)
    output = wire_output(dict(chapters=[c], moments=[moment(fid='F006')], chapter_boundaries=[], unselected_facts=[]), {})
    output['chapters'][0]['hero_candidate_id'] = hero
    output['media_choices'] = [dict(chapter_id='C01', candidate_id=r['candidate_id'], reason='有依据的候选画面') for r in candidates]
    return facts, assets, shown, candidates, output


@pytest.mark.parametrize(('hero', 'expected', 'omitted'), [
    ('P007', ['P001','P002','P003','P004','P007'], ['V005','V006']),
    ('P001', ['P001','P002','P003','P004','P005'], ['V006','V007'])])
def test_capacity_reserves_explicit_hero_and_preserves_excluded_asset_facts_and_highlights(hero, expected, omitted):
    from copy import deepcopy
    facts, assets, shown, candidates, output = capacity_image_fixture(hero)
    before = deepcopy(output)
    jsonschema.validate(output, p.structure_wire_schema(facts, candidates=candidates))
    chapters, moments, issues, _ = p.compile_structure_wire(output, facts, assets, candidates=candidates, shown_frames=shown)
    assert not issues and output == before and len(chapters) == 1
    c = chapters[0]; audit = c['candidate_selection_audit']
    assert len(c['selected_asset_ids']) == 5 and c['hero_frame_id'] == 'frame-' + str(int(hero[1:]))
    assert c['fact_ids'] == list(facts) and moments[0]['fact_id'] == 'F006'
    assert audit['selected_candidate_ids'] == expected and audit['capacity_omitted_asset_ids'] == omitted
    assert all(r['reason'] == 'DISPLAY_CAPACITY_NOT_VALUE_JUDGMENT' for r in audit['capacity_omitted_candidates'])
    assert audit['capacity_rule'] == 'EXPLICIT_HERO_PLUS_FIRST_RANKED_OTHER_ASSETS'
    assert audit['max_selected_assets'] == 5 and not audit['deduplicated_candidates']
    assert set(audit['ranked_candidate_ids']) == set(expected) | {r['candidate_id'] for r in audit['capacity_omitted_candidates']}


@pytest.mark.parametrize('fault', ['bad_reason', 'unshown_frame', 'unverified_fact'])
def test_capacity_omission_never_hides_an_invalid_lower_ranked_proposal(fault):
    facts, assets, shown, candidates, output = capacity_image_fixture()
    if fault == 'bad_reason': output['media_choices'][5]['reason'] = ' '
    elif fault == 'unshown_frame': del shown['V006']['frame-6']
    else: facts['F006']['visual_reviewed'] = False
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets, candidates=candidates, shown_frames=shown)
    assert not chapters and issues


def test_capacity_audit_partitions_all_proposals_including_unshown_asset_alternatives():
    facts, assets, shown, candidates, output = capacity_image_fixture()
    frame = dict(frame_id='frame-6-detail', source_timestamp_ms=2000, relative_path='detail.jpg')
    assets['V006']['frames'].append(frame); shown['V006'][frame['frame_id']] = frame
    facts['F006']['evidence_frame_ids'].append(frame['frame_id'])
    candidates.append(dict(candidate_id='P008', asset_id='V006', frame_id=frame['frame_id'], fact_ids=['F006']))
    output['media_choices'].append(dict(chapter_id='C01', candidate_id='P008', reason='第六资产的另一张有效备选'))
    chapters, _, issues, _ = p.compile_structure_wire(output, facts, assets, candidates=candidates, shown_frames=shown)
    assert not issues
    audit = chapters[0]['candidate_selection_audit']
    assert [r['candidate_id'] for r in audit['capacity_omitted_candidates']] == ['P005','P006','P008']
    assert audit['capacity_omitted_candidates'][-1]['representative_candidate_id'] == 'P006'
    assert not audit['deduplicated_candidates']  # All proposals of an omitted asset have one honest capacity reason.
