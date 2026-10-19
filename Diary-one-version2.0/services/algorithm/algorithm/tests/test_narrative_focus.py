from final_copy_test_support import write_and_review_with_test_images
from test_product_editor import scripted_final_verdict
from copy import deepcopy

import jsonschema
import pytest

from diary_one_ci import narrative_focus as n
from diary_one_ci import product_editor as p


def memories():
    return [{'id': 'C01', 'facts': [
        {'id': 'F1', 'asset_id': 'V1', 'text': '骑车经过桥边，橙色列车驶过桥面。路人穿粉色上衣。'},
        {'id': 'F2', 'asset_id': 'V2', 'text': '桥边有逆光下的塔楼。'}]}]


def brief():
    return {'items': [{'id': 'C01', 'details': [
        {'fact_id': 'F1', 'evidence_quote': '橙色列车驶过桥面', 'role': 'MAIN'},
        {'fact_id': 'F1', 'evidence_quote': '路人穿粉色上衣', 'role': 'BACKGROUND'},
        {'fact_id': 'F2', 'evidence_quote': '逆光下的塔楼', 'role': 'SUPPORT'}]}]}


def test_one_fact_can_have_both_main_and_background_without_losing_facts():
    items = memories()
    original = deepcopy(items)
    jsonschema.validate(brief(), n.brief_schema(items))
    hints, audit = n.validate_briefs(brief(), items)
    assert hints['C01']['priority_fact_ids'] == ['F1', 'F2']
    assert [d['role'] for d in hints['C01']['narrative_details']] == ['MAIN', 'BACKGROUND', 'SUPPORT']
    assert items == original
    assert audit[0]['status'] == 'ACCEPTED'


@pytest.mark.parametrize('change,reason', [
    ({'fact_id': 'F99'}, 'FOREIGN_FACT'),
    ({'evidence_quote': '橙色列车呼啸而过'}, 'UNSUPPORTED_QUOTE'),
    ({'evidence_quote': '橙色列车路人穿粉色上衣'}, 'UNSUPPORTED_QUOTE'),
    ({'evidence_quote': '   '}, 'UNSUPPORTED_QUOTE'),
    ({'role': 'SUPPORT'}, 'MISSING_MAIN'),
])
def test_rejects_untraceable_editorial_hint(change, reason):
    output = brief()
    output['items'][0]['details'][0].update(change)
    hints, audit = n.validate_briefs(output, memories())
    assert not hints and audit[0]['reason'] == reason


def test_conflicting_roles_and_duplicate_chapter_fail_without_hiding_other_chapter():
    output = brief()
    output['items'][0]['details'].append({**output['items'][0]['details'][0], 'role': 'BACKGROUND'})
    assert n.validate_briefs(output, memories())[1][0]['reason'] == 'DUPLICATE_DETAIL'
    output = brief()
    output['items'].append(deepcopy(output['items'][0]))
    output['items'].append({'id': 'C02', 'details': [
        {'fact_id': 'F3', 'evidence_quote': '鱼跃出水面', 'role': 'MAIN'}]})
    items = memories() + [{'id': 'C02', 'facts': [{'id': 'F3', 'text': '鱼跃出水面。'}]}]
    hints, audit = n.validate_briefs(output, items)
    assert set(hints) == {'C02'}
    assert audit[0]['reason'] == 'MISSING_OR_DUPLICATE_CHAPTER'


def test_bad_focus_falls_back_to_all_original_facts_in_actual_writer():
    memory = {**memories()[0], 'kind': 'CHAPTER', 'fact_ids': ['F1', 'F2']}
    memory['evidence_groups'] = [{'asset_id': f['asset_id'], 'facts': [f]} for f in memory['facts']]
    observed = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        if stage.endswith('_NARRATIVE_BRIEF'):
            bad = brief()
            bad['items'][0]['details'][0]['evidence_quote'] = '与好友愉快骑行'
            return bad
        if stage == 'WRITE':
            observed.append(context['items'][0])
            return {'items': [{'id': 'C01', 'title': '桥上的列车', 'story': '橙色列车驶过桥面。'}]}
        return {'items': [{'id': 'C01', 'title': '桥上的列车', 'title_fact_ids': ['F1'],
            'decision': 'PUBLISH', 'reason': '事实与表达一致', 'voice_issues': [],
            'sentences': [{'text': '橙色列车驶过桥面。', 'fact_ids': ['F1'], 'source_index': 0}]}]}
    packet = write_and_review_with_test_images([memory], ('WRITE', 'REVIEW', 'REPAIR'), ask=ask,
                                time_basis='IMPORT_ORDER_ONLY', stage_runs=[])
    assert packet['reviewed']
    assert observed[0]['facts'] == memory['facts']
    assert not observed[0].get('narrative_details')
    assert packet['narrative_brief_ledger'][0]['reason'] == 'UNSUPPORTED_QUOTE'


def test_same_fact_relations_are_checked_in_public_selection_explanations():
    facts = {'F1': {'text': '一名骑行者身穿粉色上衣，停在河边。'},
             'F2': {'text': '两位朋友交谈。'}}
    assert p.unsupported_editorial_context('同伴在河边互动，体现连续骑行', ['F1'], facts) == [
        '同伴', '互动', '连续骑行']
    assert p.unsupported_editorial_context('朋友交谈', ['F1'], facts) == ['朋友']
    assert not p.unsupported_editorial_context('朋友交谈', ['F2'], facts)
    assert not p.unsupported_editorial_context('河边骑行者的姿态补充活动细节', ['F1'], facts)


def test_camera_reporting_is_a_style_issue_without_blocking_grounded_copy():
    memory = {**memories()[0], 'kind': 'CHAPTER', 'fact_ids': ['F1', 'F2']}
    for text in ('画面最后转向逆光下的塔楼。', '画面转向逆光下的塔楼。', '画面定格在逆光下的塔楼。'):
        output = {'items': [{'id': 'C01', 'title': '逆光下的塔楼', 'title_fact_ids': ['F2'],
            'decision': 'PUBLISH', 'reason': '模型复核', 'voice_issues': [],
            'sentences': [{'text': text, 'fact_ids': ['F2']}]}]}
        accepted, ledger = p.compile_copy(output, [memory], review=True)
        assert accepted and ledger[0]['style_flags']


def test_detail_priorities_reach_independent_reviewer_as_hints_not_replacement_facts():
    memory = {**memories()[0], 'kind': 'CHAPTER', 'fact_ids': ['F1', 'F2']}
    memory['evidence_groups'] = [{'asset_id': f['asset_id'], 'facts': [f]} for f in memory['facts']]
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        if stage.endswith('_NARRATIVE_BRIEF'):
            return brief()
        if stage == 'WRITE':
            assert p.CHAPTER_VOICE in prompt
            draft_input = context['items'][0]
            assert 'facts' not in draft_input
            assert [d['evidence_quote'] for d in draft_input['writing_material']] == [
                '橙色列车驶过桥面', '逆光下的塔楼']
            assert [d['asset_id'] for d in draft_input['writing_material']] == ['V1', 'V2']
            assert all(d['role'] != 'BACKGROUND' for d in draft_input['writing_material'])
            return {'items': [{'id': 'C01', 'title': '列车驶过桥面', 'story': '橙色列车驶过桥面。'}]}
        assert [{k: f[k] for k in ('id', 'asset_id', 'text')} for f in context['items'][0]['facts']] == memory['facts']
        assert context['items'][0]['narrative_details'] == n.validate_briefs(brief(), [memory])[0]['C01']['narrative_details']
        return {'items': [{'id': 'C01', 'title': '列车驶过桥面', 'title_fact_ids': ['F1'],
            'decision': 'PUBLISH', 'reason': '事实与表达一致', 'voice_issues': [],
            'sentences': [{'text': '橙色列车驶过桥面。', 'fact_ids': ['F1'], 'source_index': 0}]}]}
    packet = write_and_review_with_test_images([memory], ('WRITE', 'REVIEW', 'REPAIR'), ask=ask,
                                time_basis='IMPORT_ORDER_ONLY', stage_runs=[])
    assert packet['reviewed']
    assert packet['writer_material_scope']['C01'] == 'SELECTED_EXCERPTS_FULL_FACTS_RESERVED_FOR_INDEPENDENT_REVIEW'


def test_fluency_problem_is_a_repairable_style_issue_without_erasing_valid_facts():
    memory = {**memories()[0], 'kind': 'CHAPTER', 'fact_ids': ['F1', 'F2']}
    memory['evidence_groups'] = [{'asset_id': f['asset_id'], 'facts': [f]} for f in memory['facts']]
    output = {'items': [{'id': 'C01', 'title': '列车驶过桥面', 'title_fact_ids': ['F1'],
        'decision': 'PUBLISH', 'reason': '句子有证据，但中文搭配需要修订', 'voice_issues': ['FLUENCY'],
        'sentences': [{'text': '骑行进在桥边，橙色列车驶过桥面。', 'fact_ids': ['F1']}]}]}
    accepted, ledger = p.compile_copy(output, [memory], review=True)
    assert accepted['C01']['style_flags'] == ['FLUENCY']
    assert ledger[0]['status'] == 'ACCEPTED'
    jsonschema.validate(output, p.copy_schema([memory], review=True))
