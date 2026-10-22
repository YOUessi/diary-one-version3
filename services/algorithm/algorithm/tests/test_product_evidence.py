from final_copy_test_support import write_and_review_with_test_images
from test_product_editor import scripted_final_verdict
"""Safety/selection regressions; fixtures do not measure visual model quality."""
from copy import deepcopy

import pytest
import jsonschema

from diary_one_ci import product_evidence as e, product_editor as p, x02
from test_product_editor import scoped_memory, copy_row


def fact(fid='F001', aid='V001'):
    return {'id': fid, 'asset_id': aid, 'source_asset_id': 'asset-0', 'text': '一家书店门前摆着人偶。',
            'evidence_frame_ids': ['f0', 'f1'], 'frame_pts_ms': [1000, 5000], 'temporal_support': 'CHANGE'}


def visual_row():
    return {'fact_id': 'F001', 'decision': 'CORRECT', 'text': '一家商店门前摆着人偶。',
            'corrections': [{'rejected_text': '书店', 'replacement_text': '商店'}],
            'evidence_frame_ids': ['f1'], 'temporal_support': 'STATE', 'reason': '图像不支持书店类别'}


SHOWN = {'V001': {'f0': {'source_timestamp_ms': 1000}, 'f1': {'source_timestamp_ms': 5000}}}


def failed_stage(stage, status='RESPONSE_INVALID'):
    return x02.StageRun(stage=stage, output={}, provider='fixture', model='fixture', request_id='fixture-failed',
        input_tokens=10, output_tokens=2, latency_seconds=0.1, model_frame_count=1, model_calls=1,
        pricing_currency='USD', input_rate_per_million=0, output_rate_per_million=0,
        native_currency_per_usd=1, pricing_basis='FIXTURE', call_status=status)


def test_visual_correction_is_the_writable_fact_original_is_kept_for_audit():
    original = fact(); snapshot = deepcopy(original)
    facts, ledger = e.compile_visual({'items': [visual_row()]}, {'F001': original}, SHOWN)
    assert '书店' not in facts['F001']['text']
    assert facts['F001']['original_text'] == original['text']
    assert facts['F001']['frame_pts_ms'] == [5000] and ledger[0]['changed']
    assert original == snapshot
    assert ledger[0]['corrections'] == visual_row()['corrections']
    assert 'corrections' not in facts['F001']  # Rejected claims are audit-only.


def test_nagoya_v4_f005_needs_real_corrections_and_publishes_the_applied_patch():
    # Recorded failed V4 judgment; inline so private run artifacts are not needed.
    text = ('视频展示了在桥上或高处俯瞰河流与城市远景的画面（f0）。随后镜头中出现一名戴绿色头盔、'
            '穿粉色上衣的女性骑行者站在桥面上回头（f1），最后画面再次转向夕阳下的河景与高塔建筑（f2）。')
    original = {**fact(), 'text': text}
    row = {**visual_row(), 'text': text,
           'reason': '原描述中“回头”不准确，人物实为侧身望向侧面；修正为直接的事实陈述。',
           'corrections': []}
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': original}, SHOWN)
    assert not facts and ledger[0]['status'] == 'UNVERIFIED'
    assert 'requires at least one actual claim correction' in ledger[0]['reason']
    row['corrections'] = [{'rejected_text': '回头', 'replacement_text': '侧身望向侧面'}]
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': original}, SHOWN)
    assert ledger[0]['status'] == 'VERIFIED' and '回头' not in facts['F001']['text']
    assert ledger[0]['model_text'] == text and not ledger[0]['model_text_matches_applied']
    assert ledger[0]['applied_text'] == facts['F001']['text']
    row['text'] = text.replace('回头', '侧身望向侧面')
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': original}, SHOWN)
    assert ledger[0]['status'] == 'VERIFIED' and '回头' not in facts['F001']['text']
    assert ledger[0]['model_text_matches_applied']


def test_rural_water_fact_uses_declared_patch_despite_extra_character_in_model_copy():
    # The real V5 failure: the redundant full text added 中, although the patch
    # merely removed camera narration. Preserve the grounded patched fact.
    text = '镜头视角向下移动并聚焦于路边水渠，可见水流从水泥台阶上落下。'
    row = {**visual_row(), 'text': '路边水渠中，可见水流从水泥台阶上落下。',
           'corrections': [dict(rejected_text='镜头视角向下移动并聚焦于', replacement_text='')]}
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': {**fact(), 'text': text}}, SHOWN)
    assert ledger[0]['status'] == 'VERIFIED' and ledger[0]['text_source'] == 'APPLIED_CORRECTIONS'
    assert facts['F001']['text'] == '路边水渠，可见水流从水泥台阶上落下。'
    assert not ledger[0]['model_text_matches_applied']


def test_undeclared_new_claim_in_redundant_model_text_never_reaches_writable_facts():
    row = {**visual_row(), 'text': '一家商店门前摆着红色人偶，旁边有人跳舞。'}
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': fact()}, SHOWN)
    assert facts['F001']['text'] == '一家商店门前摆着人偶。'
    assert '跳舞' not in facts['F001']['text'] and not ledger[0]['model_text_matches_applied']
    assert ledger[0]['model_text'] == row['text']


@pytest.mark.parametrize('case', [
    'missing_edits', 'empty_edits', 'unchanged_patch', 'punctuation',
    'absent_span', 'repeated_span', 'overlap', 'rejected_still_present', 'keep_changed', 'keep_with_edits'])
def test_visual_claim_change_must_be_real_complete_and_reconstructable(case):
    original = fact(); row = visual_row()
    if case == 'missing_edits': row.pop('corrections')
    if case == 'empty_edits': row['corrections'] = []
    if case == 'unchanged_patch': row['corrections'][0]['replacement_text'] = '书店'
    if case == 'punctuation':
        row.update(text=original['text'].replace('。', '！'),
                   corrections=[dict(rejected_text=original['text'], replacement_text=original['text'].replace('。', '！'))])
    if case == 'absent_span': row['corrections'][0]['rejected_text'] = '玩具店'
    if case == 'repeated_span': original['text'] = '书店招牌下，书店门前摆着人偶。'
    if case == 'overlap':
        row['corrections'].append(dict(rejected_text='一家书店', replacement_text='商店'))
    if case == 'rejected_still_present':
        row['corrections'][0]['replacement_text'] = '商店或书店'
        row['text'] = '一家商店或书店门前摆着人偶。'
    if case == 'keep_changed': row.update(decision='KEEP', corrections=[])
    if case == 'keep_with_edits': row.update(decision='KEEP', text=original['text'])
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': original}, SHOWN)
    assert not facts and ledger[0]['status'] == 'UNVERIFIED'


def test_keep_and_drop_need_no_cosmetic_rewriting():
    row = {**visual_row(), 'decision': 'KEEP', 'text': fact()['text'], 'corrections': []}
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': fact()}, SHOWN)
    assert len(facts) == 1 and not ledger[0]['changed']
    row.update(decision='DROP', text='', evidence_frame_ids=[])
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': fact()}, SHOWN)
    assert not facts and ledger[0]['status'] == 'DROPPED'


def museum_fact_and_expansion():
    # Recorded V07 museum failure: a correct horse-armour fact was expanded
    # with unrelated background details, leaving the supposedly rejected claim.
    original = {**fact('F003', 'V003'), 'source_asset_id': 'asset-2',
        'text': '展厅中央陈列着一套完整的马匹与骑士金属盔甲展品，头盔上装饰有醒目的红色羽毛。背景墙上挂有织物挂毯，左侧有一名黑衣参观者背对镜头站立。',
        'evidence_frame_ids': ['asset-2-f0'], 'frame_pts_ms': [None], 'temporal_support': 'STATE'}
    row = {'fact_id': 'F003', 'decision': 'CORRECT', 'text': original['text'],
        'corrections': [{'rejected_text': '背景墙上挂有织物挂毯',
                         'replacement_text': '上方天花板为玻璃采光顶，透出蓝色的天光；背景墙上挂有织物挂毯及一面红底白十字旗帜'}],
        'evidence_frame_ids': ['asset-2-f0'], 'temporal_support': 'STATE',
        'reason': '原描述未提及显著的玻璃采光顶和红底白十字旗帜，补充这些视觉事实以匹配图片内容。'}
    return original, row


def test_museum_expansion_stays_invalid_but_exact_original_keep_is_valid():
    original, row = museum_fact_and_expansion()
    shown = {'V003': {'asset-2-f0': {'source_timestamp_ms': None}}}
    facts, ledger = e.compile_visual({'items': [row]}, {'F003': original}, shown)
    assert not facts and ledger[0]['reason'] == 'Rejected claim remains in corrected text'
    row.update(decision='KEEP', corrections=[], reason='原事实成立；未穷尽背景不构成错误。')
    facts, ledger = e.compile_visual({'items': [row]}, {'F003': original}, shown)
    assert facts['F003']['text'] == original['text'] and ledger[0]['text_source'] == 'ORIGINAL'
    assert not ledger[0]['changed']
    row['text'] += '上方为玻璃采光顶。'
    facts, ledger = e.compile_visual({'items': [row]}, {'F003': original}, shown)
    assert not facts and ledger[0]['status'] == 'UNVERIFIED'  # KEEP cannot silently expand either.


@pytest.mark.parametrize('initial_expansion', [False, True])
def test_additional_independent_scene_details_allow_exact_keep_without_new_review_layer(tmp_path, initial_expansion):
    from types import SimpleNamespace
    original, expansion = museum_fact_and_expansion()
    assets = {'V003': {'asset_id': 'asset-2', 'frames': [
        {'frame_id': 'asset-2-f0', 'source_timestamp_ms': None, 'relative_path': 'frame.jpg'}]}}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        if stage.endswith('_SCENE'):
            return {'assets': [dict(asset_id='asset-2', observations=[
                dict(text=original['text'], evidence_frame_ids=['asset-2-f0'], temporal_support='STATE'),
                dict(text='上方天花板为玻璃采光顶。', evidence_frame_ids=['asset-2-f0'], temporal_support='STATE')], uncertainties=[])]}
        assert context['independent_scenes'][0]['observations'][1]['text'] == '上方天花板为玻璃采光顶。'
        if initial_expansion and not stage.endswith('_REPAIR'):
            return {'items': [deepcopy(expansion)]}
        return {'items': [{**expansion, 'decision': 'KEEP', 'text': original['text'], 'corrections': [],
                           'reason': '原文事实均成立，额外背景细节无需补入。'}]}
    facts, ledger, _ = e.review_visual_facts({'F003': original}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == (3 if initial_expansion else 2)
    assert sum(stage.endswith('_REPAIR') for stage in calls) == int(initial_expansion)
    assert facts['F003']['text'] == original['text'] and ledger[0]['status'] == 'VERIFIED'
    assert ledger[0]['decision'] == 'KEEP' and not ledger[0]['changed']


def test_correction_can_delete_false_clause_and_replace_multiple_original_spans():
    original = {**fact(), 'text': '书店门前有一名真人在回头，与拍摄者互动。'}
    row = {**visual_row(), 'text': '商店门前有一个人偶。', 'corrections': [
        dict(rejected_text='书店', replacement_text='商店'),
        dict(rejected_text='一名真人在回头', replacement_text='一个人偶'),
        dict(rejected_text='，与拍摄者互动', replacement_text='')]}
    facts, ledger = e.compile_visual({'items': [row]}, {'F001': original}, SHOWN)
    assert ledger[0]['status'] == 'VERIFIED' and facts['F001']['text'] == row['text']


@pytest.mark.parametrize('case', ['missing', 'duplicate', 'foreign_frame', 'single_frame_change', 'drop_with_text'])
def test_unverified_visual_claims_never_fall_back_to_old_facts(case):
    row = visual_row(); rows = [row]
    if case == 'missing': rows = []
    if case == 'duplicate': rows *= 2
    if case == 'foreign_frame': row['evidence_frame_ids'] = ['other-asset-frame']
    if case == 'single_frame_change': row['temporal_support'] = 'CHANGE'
    if case == 'drop_with_text': row['decision'] = 'DROP'
    facts, ledger = e.compile_visual({'items': rows}, {'F001': fact()}, SHOWN)
    assert not facts and ledger[0]['status'] == 'UNVERIFIED'


def moment(mid='M01', fid='F001', parent='C01'):
    return {'id': mid, 'fact_id': fid, 'parent_chapter_id': parent}


def moment_row(mid='M01', **kwargs):
    return {'id': mid, 'decision': 'KEEP', 'anchor': '店门口的人偶', 'value_type': 'DISTINCT_DETAIL',
            'event_group_id': mid, 'comparison_reason': '相较普通路面，这一处店门装饰有明确的物件焦点',
            'scene_kind': 'OTHER', 'scene_basis_fact_ids': ['F' + mid[1:].zfill(3)],
            'evidence_frame_ids': ['f1'], 'focus_frame_id': 'f1', 'reason': '有辨识度的店门装饰', **kwargs}


@pytest.mark.parametrize('case', ['routine', 'missing', 'fake_action', 'foreign_frame', 'independent_in_chapter', 'foreign_focus'])
def test_highlight_requires_specific_grounded_value(case):
    row = moment_row(); rows = [row]
    if case == 'routine': row['value_type'] = 'ROUTINE'
    if case == 'missing': rows = []
    if case == 'fake_action': row['value_type'] = 'ACTION_CHANGE'
    if case == 'foreign_frame': row['evidence_frame_ids'] = ['foreign-frame']
    if case == 'foreign_focus': row['focus_frame_id'] = 'not-selected-frame'
    if case == 'independent_in_chapter': row['value_type'] = 'INDEPENDENT_SCENE'
    kept, ledger = e.compile_moments({'items': rows}, [moment()], {'F001': fact()})
    assert not kept and ledger[0]['status'] == 'UNVERIFIED'


@pytest.mark.parametrize('case', ['other_candidate_frame', 'fact_id', 'timestamp', 'empty_focus',
                                  'empty_comparison', 'blank_comparison', 'empty_anchor', 'empty_reason'])
def test_dynamic_moment_schema_limits_each_candidate_to_its_own_evidence(case):
    facts = {'F001': fact(), 'F002': {**fact('F002', 'V002'), 'evidence_frame_ids': ['other-f1'], 'frame_pts_ms': [5000]}}
    moments = [moment(), moment('M02', 'F002')]
    row = moment_row()
    if case == 'other_candidate_frame': row.update(evidence_frame_ids=['other-f1'], focus_frame_id='other-f1')
    if case == 'fact_id': row.update(evidence_frame_ids=['F001'], focus_frame_id='F001')
    if case == 'timestamp': row.update(evidence_frame_ids=[5000], focus_frame_id=5000)
    if case == 'empty_focus': row['focus_frame_id'] = ''
    if case == 'empty_comparison': row['comparison_reason'] = ''
    if case == 'blank_comparison': row['comparison_reason'] = '  \t'
    if case == 'empty_anchor': row['anchor'] = ''
    if case == 'empty_reason': row['reason'] = ''
    output = {'items': [row, moment_row('M02', evidence_frame_ids=['other-f1'], focus_frame_id='other-f1')]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(output, e.moment_request_schema(moments, facts))
    kept, ledger = e.compile_moments(output, moments, facts)
    assert [m['id'] for m in kept] == ['M02'] and ledger[0]['status'] == 'UNVERIFIED'


def test_dynamic_schema_allows_empty_evidence_only_for_an_explicit_drop():
    row = moment_row(decision='DROP', anchor='', evidence_frame_ids=[], focus_frame_id='', value_type='ROUTINE')
    schema = e.moment_request_schema([moment()], {'F001': fact()})
    jsonschema.validate({'items': [row]}, schema)
    kept, ledger = e.compile_moments({'items': [row]}, [moment()], {'F001': fact()})
    assert not kept and ledger[0]['status'] == 'NOT_SELECTED'
    row.update(decision='KEEP', value_type='DISTINCT_DETAIL', anchor='店门口的人偶')
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate({'items': [row]}, schema)


def test_initial_moment_request_includes_candidate_fact_and_frame_mapping():
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        assert context['candidate_evidence'] == {'M01': {'fact_id': 'F001', 'allowed_frame_ids': ['f0', 'f1'],
                                                        'allowed_scene_basis_fact_ids': ['F001']}}
        jsonschema.validate({'items': [moment_row()]}, schema)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate({'items': [moment_row(id='M99')]}, schema)
        return {'items': [moment_row()]}
    kept, _, _ = e.review_moments([moment()], [], {'F001': fact()}, ask)
    assert len(calls) == 1 and len(kept) == 1


def test_routine_is_an_explicit_editorial_rejection_not_a_model_failure():
    row = moment_row(decision='DROP', value_type='ROUTINE', reason='只是一般握把骑行')
    kept, ledger = e.compile_moments({'items': [row]}, [moment()], {'F001': fact()})
    assert not kept and ledger[0]['status'] == 'NOT_SELECTED'


def test_same_moment_frame_cannot_be_reused_under_different_fact_ids():
    kept, ledger = e.compile_moments({'items': [moment_row(), moment_row('M02')]},
        [moment(), moment('M02', 'F002')], {'F001': fact(), 'F002': fact('F002')})
    assert len(kept) == 1 and 'Duplicate' in ledger[1]['reason']


def test_same_event_across_assets_can_select_the_better_later_candidate():
    rows = [moment_row(decision='DROP', value_type='DUPLICATE', event_group_id='M02',
                       comparison_reason='另一片段的同一个人偶更清楚'), moment_row('M02')]
    kept, ledger = e.compile_moments({'items': rows}, [moment(), moment('M02', 'F002')],
                                   {'F001': fact(), 'F002': fact('F002', 'V002')})
    assert [m['id'] for m in kept] == ['M02']
    assert ledger[0]['status'] == 'NOT_SELECTED' and ledger[0]['event_group_id'] == 'M02'


@pytest.mark.parametrize('case', ['unknown_representative', 'cycle', 'two_kept', 'invalid_representative'])
def test_event_group_requires_an_actual_selected_representative(case):
    rows = [moment_row(decision='DROP', value_type='DUPLICATE', event_group_id='M02'), moment_row('M02')]
    if case == 'unknown_representative': rows[0]['event_group_id'] = 'M99'
    if case == 'cycle': rows[1].update(decision='DROP', value_type='DUPLICATE', event_group_id='M01')
    if case == 'two_kept': rows[0].update(decision='KEEP', value_type='DISTINCT_DETAIL')
    if case == 'invalid_representative': rows[1]['evidence_frame_ids'] = ['foreign']
    kept, ledger = e.compile_moments({'items': rows}, [moment(), moment('M02', 'F002')],
                                   {'F001': fact(), 'F002': fact('F002', 'V002')})
    assert ledger[0]['status'] == 'UNVERIFIED'
    assert [m['id'] for m in kept] == ([] if case in ('cycle', 'invalid_representative') else ['M02'])


def test_distinct_events_in_the_same_asset_do_not_get_removed_by_asset_id():
    rows = [moment_row(evidence_frame_ids=['f0'], focus_frame_id='f0'), moment_row('M02')]
    kept, ledger = e.compile_moments({'items': rows}, [moment(), moment('M02', 'F002')],
                                   {'F001': fact(), 'F002': fact('F002')})
    assert len(kept) == 2 and all(r['status'] == 'SELECTED' for r in ledger)


def test_routine_crowds_can_leave_no_highlight_without_a_minimum_count():
    rows = [moment_row(decision='DROP', value_type='ROUTINE', reason='只是普通海滩人群',
                       comparison_reason='人数和服装颜色没有构成具体回看焦点')]
    kept, ledger = e.compile_moments({'items': rows}, [moment()], {'F001': fact()})
    assert not kept and ledger[0]['status'] == 'NOT_SELECTED'


def test_independent_scene_does_not_have_to_be_a_rare_event():
    kept, _ = e.compile_moments({'items': [moment_row(value_type='INDEPENDENT_SCENE')]},
                              [moment(parent=None)], {'F001': fact()})
    assert len(kept) == 1


def test_static_specific_detail_needs_no_action_change_or_interaction():
    verified = {**fact(), 'text': '一只猫蜷在窗台上的毛毯里。', 'temporal_support': 'STATE',
                'evidence_frame_ids': ['f1'], 'frame_pts_ms': [5000]}
    row = moment_row(anchor='蜷在窗台毛毯里的猫', value_type='DISTINCT_DETAIL',
                     reason='具体而清楚的日常片刻', comparison_reason='这一姿态有单独证据，没有重复候选')
    kept, ledger = e.compile_moments({'items': [row]}, [moment()], {'F001': verified})
    assert len(kept) == 1 and ledger[0]['status'] == 'SELECTED'


def test_moment_review_receives_parent_focus_and_only_current_fact_references():
    known = {**fact(), 'text': '一只大象站在树荫下。', 'temporal_support': 'STATE'}
    chapters = [{'id': 'C01', 'fact_ids': ['F001'], 'selection_focus': {
        'experience_kind': 'ZOO_ANIMALS', 'focus': '看见树荫下的大象', 'fact_ids': ['F001']}}]
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        assert context['allowed_fact_ids'] == ['F001']
        assert context['chapters'][0]['selection_focus'] == chapters[0]['selection_focus']
        assert context['facts'][0]['text'] == known['text']
        assert not context['selection_focus_issues']
        return {'items': [moment_row(anchor='站在树荫下的大象')]}
    kept, ledger, _ = e.review_moments([moment()], chapters, {'F001': known}, ask)
    assert len(kept) == 1 and ledger[0]['status'] == 'SELECTED'


@pytest.mark.parametrize('bad_ids', [['F404'], ['F001', 'F002']])
def test_focus_outside_verified_parent_scope_is_not_partially_retained(bad_ids):
    chapters = [{'id': 'C01', 'fact_ids': ['F001'], 'theme': '并未核验的动物园体验', 'selection_focus': {
        'experience_kind': 'ZOO_ANIMALS', 'focus': '并未核验的老虎表演', 'fact_ids': bad_ids}}]
    before = deepcopy(chapters)
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        focus = context['chapters'][0]['selection_focus']
        assert focus == dict(experience_kind='UNCERTAIN', focus='', fact_ids=[])
        assert '并未核验' not in str(context)
        assert context['selection_focus_issues'][0]['code'] == 'SELECTION_FOCUS_OUT_OF_SCOPE'
        return {'items': [moment_row()]}
    kept, _, output = e.review_moments([moment()], chapters,
        {'F001': fact(), 'F002': fact('F002', 'V002')}, ask)
    assert kept and output['selection_focus_issues'] and chapters == before


def test_independent_aha_keeps_own_evidence_when_chapter_has_another_focus():
    chapters = [{'id': 'C01', 'fact_ids': ['F001'], 'selection_focus': {
        'experience_kind': 'CYCLING', 'focus': '骑行经过林荫道', 'fact_ids': ['F001']}}]
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        assert context['moments'][0]['parent_chapter_id'] is None
        assert context['allowed_fact_ids'] == ['F001', 'F002']
        return {'items': [moment_row(value_type='INDEPENDENT_SCENE', anchor='室内市场水果摊',
                                     scene_kind='MARKET_SHOPPING', scene_basis_fact_ids=['F002'])]}
    kept, ledger, _ = e.review_moments([moment(fid='F002', parent=None)], chapters,
        {'F001': fact(), 'F002': {**fact('F002', 'V002'), 'text': '室内市场有水果摊。'}}, ask)
    assert kept[0]['parent_chapter_id'] is None and ledger[0]['status'] == 'SELECTED'


@pytest.mark.parametrize('kind', e.scene_selection.EXPERIENCE_KINDS)
def test_parent_focus_uses_the_shared_scene_catalog(kind):
    chapter = {'id': 'C01', 'fact_ids': ['F001'], 'selection_focus': {
        'experience_kind': kind, 'focus': '本章已核验的具体主体', 'fact_ids': ['F001']}}
    scoped, issues = e.chapter_focus_context([chapter], {'F001': fact()})
    assert not issues and scoped[0]['selection_focus'] == chapter['selection_focus']


@pytest.mark.parametrize('kind,text', [
    ('ZOO_ANIMALS', '一只大象站在树荫下，长鼻垂在身前。'),
    ('COOKING', '案板上摆着切成薄片的胡萝卜，旁边有一把刀。'),
    ('DINING', '盘子里的饺子围成一圈，中间摆着一小碟蘸料。'),
    ('MARKET_SHOPPING', '摊位的竹篮里摆着红色番茄和细长的青椒。'),
    ('GARDEN', '石拱桥跨过池塘，桥洞在水面形成倒影。'),
    ('MUSEUM', '玻璃展柜里摆着有螺旋纹路的陶罐。'),
])
def test_scene_specific_rules_reach_existing_call_and_static_detail_can_pass(kind, text):
    known = {**fact(), 'text': text, 'temporal_support': 'STATE',
             'evidence_frame_ids': ['f1'], 'frame_pts_ms': [5000],
             'filename': 'misleading_cycling_family_label.mp4'}
    chapter = {'id': 'C01', 'fact_ids': ['F001'], 'selection_focus': {
        'experience_kind': kind, 'focus': text, 'fact_ids': ['F001']}}
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        policies = context['scene_moment_policy']
        rule = policies['policies'][kind]
        shared = e.scene_selection.policy_for(kind)
        assert rule['highlight_priorities'] == shared['highlight_priorities']
        assert rule['downrank'] and rule['evidence_limits'] and rule['activation'] and rule['independent_aha']
        assert policies['policies']['ZOO_ANIMALS']['highlight_priorities'] != policies['policies']['DINING']['highlight_priorities']
        assert 'misleading_cycling_family_label' not in str(context)
        assert e.scene_selection.moment_policy_prompt() in prompt
        row = moment_row(anchor=text, scene_kind=kind)
        jsonschema.validate({'items': [row]}, schema)
        return {'items': [row]}
    kept, ledger, raw = e.review_moments([moment()], [chapter], {'F001': known}, ask)
    assert calls == ['S10_PRODUCT_MOMENT_VALUE'] and len(kept) == 1
    assert ledger[0]['scene_kind'] == kind and ledger[0]['scene_basis_fact_ids'] == ['F001']
    assert ledger[0]['scene_policy_version'] == raw['scene_policy_version']
    assert 'scene_kind' not in kept[0] and 'scene_basis_fact_ids' not in kept[0]


def test_scene_evidence_scope_includes_valid_parent_focus_but_not_other_chapters():
    facts = {f'F00{i}': fact(f'F00{i}', f'V00{i}') for i in range(1, 4)}
    chapters = [
        {'id': 'C01', 'fact_ids': ['F001', 'F002'], 'selection_focus': {
            'experience_kind': 'PARK_LEISURE', 'focus': '湖畔野餐', 'fact_ids': ['F002']}},
        {'id': 'C02', 'fact_ids': ['F003'], 'selection_focus': {
            'experience_kind': 'CHILDREN_PLAY', 'focus': '滑梯活动', 'fact_ids': ['F003']}},
    ]
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        assert context['candidate_evidence']['M01']['allowed_scene_basis_fact_ids'] == ['F001', 'F002']
        bad = moment_row(scene_kind='CHILDREN_PLAY', scene_basis_fact_ids=['F003'])
        with pytest.raises(jsonschema.ValidationError): jsonschema.validate({'items': [bad]}, schema)
        if stage.endswith('_REPAIR'):
            assert context['issues'][0]['status'] == 'UNVERIFIED'
            return {'items': [moment_row(scene_kind='PARK_LEISURE', scene_basis_fact_ids=['F002'])]}
        return {'items': [bad]}
    kept, ledger, raw = e.review_moments([moment()], chapters, facts, ask)
    assert len(calls) == 2 and calls[-1].endswith('_REPAIR') and len(kept) == 1
    assert ledger[0]['scene_basis_fact_ids'] == ['F002']
    assert raw['original_output']['items'][0]['scene_basis_fact_ids'] == ['F003']


@pytest.mark.parametrize('decision', ['KEEP', 'DROP'])
@pytest.mark.parametrize('case', ['missing', 'unknown_kind', 'empty_basis', 'foreign_basis', 'duplicate_basis'])
def test_v07_scene_contract_failure_cannot_silently_count_as_verified(decision, case):
    row = moment_row(decision=decision)
    if decision == 'DROP': row['value_type'] = 'ROUTINE'
    if case == 'missing': row.pop('scene_kind'); row.pop('scene_basis_fact_ids')
    if case == 'unknown_kind': row['scene_kind'] = 'BASED_ON_FILENAME'
    if case == 'empty_basis': row['scene_basis_fact_ids'] = []
    if case == 'foreign_basis': row['scene_basis_fact_ids'] = ['F404']
    if case == 'duplicate_basis': row['scene_basis_fact_ids'] = ['F001', 'F001']
    calls = []
    def ask(stage, *args):
        calls.append(stage)
        return {'items': [deepcopy(row)]}
    kept, ledger, _ = e.review_moments([moment()], [], {'F001': fact()}, ask)
    assert not kept and ledger[0]['status'] == 'UNVERIFIED'
    assert len(calls) == 2 and calls[-1].endswith('_REPAIR')


def test_independent_aha_cannot_borrow_chapter_scene_even_with_overbroad_caller_scope():
    row = moment_row(value_type='INDEPENDENT_SCENE', scene_kind='CYCLING', scene_basis_fact_ids=['F001'])
    kept, ledger = e.compile_moments({'items': [row]}, [moment(fid='F002', parent=None)],
        {'F001': fact(), 'F002': fact('F002', 'V002')},
        scene_basis_scopes={'M01': ['F001', 'F002']}, require_scene_policy=True)
    assert not kept and ledger[0]['status'] == 'UNVERIFIED'


def test_legacy_moment_compile_does_not_claim_scene_policy_was_verified():
    row = moment_row(); row.pop('scene_kind'); row.pop('scene_basis_fact_ids')
    kept, ledger = e.compile_moments({'items': [row]}, [moment()], {'F001': fact()})
    assert kept and 'scene_policy_version' not in ledger[0] and 'scene_kind' not in ledger[0]


def test_copy_repair_does_not_self_authorize_publication():
    memory = scoped_memory()
    memory['evidence_groups'] = [{'asset_id': 'V001', 'facts': [memory['facts'][0], memory['facts'][2]]},
                                 {'asset_id': 'V002', 'facts': [memory['facts'][1]]}]
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        if stage.endswith('_NARRATIVE_BRIEF'): return {'items': []}
        if stage == 'WRITE': return {'items': [{'id': 'C01', 'title': '竹林骑行', 'story': '骑车经过竹林。'}]}
        row = copy_row([('骑车经过竹林。', ['F001'])]); row['sentences'][0]['source_index'] = 0
        if stage in ('REVIEW', 'REPAIR_VERIFY'): row.update(decision='BLOCK', reason='Fixture semantic rejection')
        return {'items': [row]}
    packet = write_and_review_with_test_images([memory], ('WRITE', 'REVIEW', 'REPAIR'), ask=ask, time_basis='UNKNOWN', stage_runs=[])
    assert 'REPAIR_VERIFY' in calls and not packet['reviewed']
    assert packet['repair_ledger'][0]['status'] == 'ACCEPTED'
    assert packet['repair_verification_ledger'][0]['status'] == 'BLOCKED'


def test_blind_scene_input_does_not_include_the_old_answer(tmp_path):
    from types import SimpleNamespace
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        if stage.endswith('_SCENE'):
            assert 'facts' not in context and '书店' not in str(context) and evidence
            return {'assets': [dict(asset_id='asset-0', observations=[dict(text='商店门前摆着人偶。',
                evidence_frame_ids=['f1'], temporal_support='STATE')], uncertainties=['店铺类别不清楚'])]}
        assert evidence and context['independent_scenes'][0]['uncertainties']
        return {'items': [visual_row()]}
    facts, ledger, _ = e.review_visual_facts({'F001': fact()}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == 2 and ledger[0]['status'] == 'VERIFIED' and '书店' not in facts['F001']['text']


def test_invalid_change_does_not_erase_other_valid_independent_scenes():
    output = {'assets': [dict(asset_id='asset-0', observations=[
        dict(text='人偶站在门口。', evidence_frame_ids=['f1'], temporal_support='STATE'),
        dict(text='人偶走出店门。', evidence_frame_ids=['f0'], temporal_support='CHANGE')], uncertainties=[])]}
    scenes, issues = e.collect_scenes(output, SHOWN, {'asset-0': 'V001'})
    assert scenes[0]['asset_id'] == 'V001'
    assert len(scenes[0]['observations']) == 1 and scenes[0]['observations'][0]['temporal_support'] == 'STATE'
    assert len(issues) == 1 and 'temporal' in issues[0]['reason']


@pytest.mark.parametrize('case', ['missing', 'duplicate', 'foreign_frame', 'single_frame_change'])
def test_invalid_independent_scenes_cannot_authorize_old_claims(case):
    row = dict(asset_id='V001', observations=[dict(text='店门口的人偶。',
               evidence_frame_ids=['f1'], temporal_support='STATE')], uncertainties=[])
    rows = [row]
    if case == 'missing': rows = []
    if case == 'duplicate': rows *= 2
    if case == 'foreign_frame': row['observations'][0]['evidence_frame_ids'] = ['foreign']
    if case == 'single_frame_change': row['observations'][0]['temporal_support'] = 'CHANGE'
    with pytest.raises(ValueError): e.validate_scenes({'assets': rows}, SHOWN)


def test_source_scope_repair_can_split_existing_clauses_without_expanding_content():
    memory = scoped_memory()
    memory['evidence_groups'] = [{'asset_id': 'V001', 'facts': [memory['facts'][0], memory['facts'][2]]},
                                 {'asset_id': 'V002', 'facts': [memory['facts'][1]]}]
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        if stage.endswith('_NARRATIVE_BRIEF'): return {'items': []}
        if stage == 'WRITE': return {'items': [dict(id='C01', title='竹林骑行', story='骑车经过竹林，看见路边水渠。')]}
        if stage == 'REVIEW':
            row = copy_row([('骑车经过竹林，看见路边水渠。', ['F001','F002'])])
            row['sentences'][0]['source_index'] = 0
        else:
            assert len(context['items'][0]['source_sentences']) == 2
            row = copy_row([('骑车经过竹林。', ['F001']), ('路边有水渠。', ['F002'])])
            for i, sentence in enumerate(row['sentences']): sentence['source_index'] = i
        return {'items': [row]}
    packet = write_and_review_with_test_images([memory], ('WRITE', 'REVIEW', 'REPAIR'), ask=ask, time_basis='UNKNOWN', stage_runs=[])
    assert packet['review_ledger'][0]['status'] == 'BLOCKED'
    assert packet['repair_verification_ledger'][0]['status'] == 'ACCEPTED'
    assert packet['reviewed']['C01']['story'] == '骑车经过竹林。路边有水渠。'


def test_model_voice_findings_are_retained_without_a_chapter_length_quota():
    row = copy_row([('骑车经过竹林。', ['F001'])])
    row['voice_issues'] = ['INVENTORY']
    reviewed, ledger = p.compile_copy({'items': [row]}, [scoped_memory()], review=True)
    assert reviewed['C01']['style_flags'] == ['INVENTORY']
    assert ledger[0]['style_flags'] == ['INVENTORY']


def test_single_frame_change_gets_one_visual_repair_not_an_automatic_downgrade(tmp_path):
    from types import SimpleNamespace
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        assert evidence
        if stage.endswith('_SCENE'):
            return {'assets': [dict(asset_id='asset-0', observations=[dict(text='门口站着人偶。',
                evidence_frame_ids=['f1'], temporal_support='STATE')], uncertainties=[])]}
        row = visual_row()
        if not stage.endswith('_REPAIR'): row['temporal_support'] = 'CHANGE'
        else: assert context['issues'][0]['status'] == 'UNVERIFIED'
        return {'items': [row]}
    facts, ledger, outputs = e.review_visual_facts({'F001': fact()}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == 3 and calls[-1].endswith('_REPAIR')
    assert facts['F001']['temporal_support'] == 'STATE' and ledger[0]['status'] == 'VERIFIED'
    assert any(o.get('stage') == 'VISUAL_CONTRACT_REPAIR' for o in outputs)


@pytest.mark.parametrize('recover', [False, True])
def test_false_visual_correction_gets_one_repair_and_never_passes_unchanged(tmp_path, recover):
    from types import SimpleNamespace
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        if stage.endswith('_SCENE'):
            return {'assets': [dict(asset_id='asset-0', observations=[], uncertainties=[])]}
        row = visual_row()
        if not (stage.endswith('_REPAIR') and recover): row.update(text=fact()['text'], corrections=[])
        if stage.endswith('_REPAIR'):
            assert len(context['facts']) == 1 and 'actual claim correction' in context['issues'][0]['reason']
        return {'items': [row]}
    facts, ledger, _ = e.review_visual_facts({'F001': fact()}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == 3 and calls[-1].endswith('_REPAIR')
    assert bool(facts) == recover
    assert ledger[0]['status'] == ('VERIFIED' if recover else 'UNVERIFIED')


@pytest.mark.parametrize('static_text', ['路边水渠有水流从台阶落下。', '一只大象站在树荫下。'])
def test_dropped_motion_description_rechecks_supported_static_part_once(tmp_path, static_text):
    from types import SimpleNamespace
    original = {**fact(), 'text': '镜头转向，' + static_text}
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        if stage.endswith('_SCENE'):
            return {'assets': [dict(asset_id='asset-0', observations=[dict(text=static_text,
                evidence_frame_ids=['f1'], temporal_support='STATE')], uncertainties=[])]}
        if stage.endswith('_REPAIR'):
            assert context['issues'][0]['code'] == 'POTENTIAL_STATIC_CONTENT_LOSS'
            assert context['independent_scenes'][0]['observations'][0]['text'] == static_text
            assert evidence
            return {'items': [{**visual_row(), 'text': static_text,
                'corrections': [dict(rejected_text='镜头转向，', replacement_text='')]}]}
        return {'items': [{**visual_row(), 'decision': 'DROP', 'text': '', 'corrections': [],
                          'evidence_frame_ids': [], 'reason': 'Cannot establish camera movement from a still frame'}]}
    facts, ledger, outputs = e.review_visual_facts({'F001': original}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == 3 and facts['F001']['text'] == static_text
    assert facts['F001']['temporal_support'] == 'STATE'
    assert ledger[0]['state_retention_review'] == 'RETAINED_AFTER_REVIEW'
    assert len([o for o in outputs if o.get('stage') == 'VISUAL_CONTRACT_REPAIR']) == 1


@pytest.mark.parametrize('reply', ['confirm_drop', 'failure', 'missing'])
def test_static_scene_does_not_automatically_resurrect_a_dropped_fact(tmp_path, reply):
    from types import SimpleNamespace
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        if stage.endswith('_SCENE'):
            return {'assets': [dict(asset_id='asset-0', observations=[dict(text='路边有一棵树。',
                evidence_frame_ids=['f1'], temporal_support='STATE')], uncertainties=[])]}
        if stage.endswith('_REPAIR'):
            if reply == 'failure': raise ValueError('Invalid review response')
            if reply == 'missing': return {'items': []}
        return {'items': [{**visual_row(), 'decision': 'DROP', 'text': '', 'corrections': [],
                          'evidence_frame_ids': [], 'reason': '图片中的树与原文商店人偶无关，原事实没有成立内容'}]}
    facts, ledger, _ = e.review_visual_facts({'F001': fact()}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == 3 and not facts
    assert ledger[0]['status'] == ('DROPPED' if reply == 'confirm_drop' else 'UNVERIFIED')
    assert ledger[0]['state_retention_review'] == ('CONFIRMED_DROP' if reply == 'confirm_drop' else 'UNRESOLVED')


def test_invalid_scene_reference_cannot_trigger_static_retention_recheck(tmp_path):
    from types import SimpleNamespace
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        if stage.endswith('_SCENE'):
            return {'assets': [dict(asset_id='asset-0', observations=[dict(text='有一只动物。',
                evidence_frame_ids=['foreign-frame'], temporal_support='STATE')], uncertainties=[])]}
        return {'items': [{**visual_row(), 'decision': 'DROP', 'text': '', 'corrections': [],
                          'evidence_frame_ids': []}]}
    facts, ledger, _ = e.review_visual_facts({'F001': fact()}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == 2 and not facts and ledger[0]['status'] == 'DROPPED'


def test_static_retention_and_contract_error_share_one_existing_repair_call(tmp_path):
    from types import SimpleNamespace
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    originals = {'F001': fact(), 'F002': fact('F002')}
    calls = []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        if stage.endswith('_SCENE'):
            return {'assets': [dict(asset_id='asset-0', observations=[dict(text='商店门前摆着人偶。',
                evidence_frame_ids=['f1'], temporal_support='STATE')], uncertainties=[])]}
        if stage.endswith('_REPAIR'):
            assert {r['fact_id'] for r in context['issues']} == {'F001', 'F002'}
            return {'items': [visual_row(), {**visual_row(), 'fact_id': 'F002'}]}
        return {'items': [{**visual_row(), 'decision': 'DROP', 'text': '', 'corrections': [],
                          'evidence_frame_ids': []},
                         {**visual_row(), 'fact_id': 'F002', 'temporal_support': 'CHANGE'}]}
    facts, ledger, _ = e.review_visual_facts(originals, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask)
    assert len(calls) == 3 and calls[-1].endswith('_REPAIR')
    assert set(facts) == {'F001', 'F002'} and all(r['status'] == 'VERIFIED' for r in ledger)
    assert next(r for r in ledger if r['fact_id'] == 'F001')['state_retention_review'] == 'RETAINED_AFTER_REVIEW'


@pytest.mark.parametrize('failed_at', ['SCENE', 'VISUAL', 'REPAIR'])
@pytest.mark.parametrize('error_type', ['stage_call', 'contract'])
def test_visual_provider_errors_leave_unverified_facts_and_failed_attempt_audit(tmp_path, failed_at, error_type):
    from types import SimpleNamespace
    assets = {'V001': {'asset_id': 'asset-0', 'frames': [
        {'frame_id': 'f1', 'source_timestamp_ms': 5000, 'relative_path': 'frame.jpg'}]}}
    calls, runs, failed = [], [], []
    def ask(stage, prompt, schema, context, evidence=()):
        calls.append(stage)
        current = 'SCENE' if stage.endswith('_SCENE') else 'REPAIR' if stage.endswith('_REPAIR') else 'VISUAL'
        if current == failed_at:
            if error_type == 'contract': raise x02.X02ContractError('Invalid visual contract')
            failed.append(failed_stage(stage))
            raise x02.X02StageCallError('Malformed model output', stage_run=failed[-1], code='MODEL_RESPONSE_NOT_JSON')
        if current == 'SCENE':
            return {'assets': [dict(asset_id='asset-0', observations=[], uncertainties=[])]}
        return {'items': [{**visual_row(), 'text': fact()['text'], 'corrections': []}]}
    facts, ledger, outputs = e.review_visual_facts({'F001': fact()}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask, stage_runs=runs)
    assert not facts and ledger[0]['status'] == 'UNVERIFIED'
    assert len(calls) == {'SCENE': 1, 'VISUAL': 2, 'REPAIR': 3}[failed_at]
    assert len(runs) == (1 if error_type == 'stage_call' else 0)
    if failed: assert runs[0] is failed[0] and runs[0].call_status == 'RESPONSE_INVALID'
    assert any(output.get('failure') for output in outputs)


def test_visual_auth_failure_stops_later_batches_and_does_not_retry(tmp_path):
    from types import SimpleNamespace
    assets = {aid: {'asset_id': 'source-' + aid, 'frames': [
        {'frame_id': f'{aid}-{i}', 'source_timestamp_ms': i * 100, 'relative_path': 'frame.jpg'} for i in range(10)]}
        for aid in ('V001', 'V002')}
    calls, runs = [], []
    def ask(stage, *args, **kwargs):
        calls.append(stage)
        raise x02.X02StageCallError('Access denied', stage_run=failed_stage(stage, 'HTTP_FAILED'), code='MODEL_HTTP_403')
    facts, ledger, _ = e.review_visual_facts({'F001': fact(), 'F002': fact('F002', 'V002')}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask, stage_runs=runs)
    assert len(calls) == len(runs) == 1 and not facts
    assert len(ledger) == 2 and all(row['status'] == 'UNVERIFIED' for row in ledger)
    assert 'non-retriable' in ledger[1]['reason']


def test_visual_real_gateway_403_keeps_failed_stage_and_stops_next_batch(tmp_path):
    from types import SimpleNamespace
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    (tmp_path / 'frame.jpg').write_bytes(b'fixture-image-transport-does-not-decode')
    assets = {aid: {'asset_id': 'source-' + aid, 'media_kind': 'VIDEO', 'frames': [
        {'frame_id': f'{aid}-{i}', 'canonical_offset_ms': i * 100,
         'source_timestamp_ms': i * 100, 'relative_path': 'frame.jpg'} for i in range(10)]}
        for aid in ('V001', 'V002')}
    calls, runs = [], []
    def transport(url, headers, body, timeout):
        calls.append(url)
        assert b'_audit_stage_failures' not in body  # Transport option, not model evidence.
        return 403, {'x-request-id': 'fixture-http-403'}, b'Forbidden'
    gateway = x02.QwenStageGateway(QwenChatCompletionsAdapter(api_key='fixture-key',
        model='qwen3.8-flash', base_url='https://fixture.invalid/v1', transport=transport))
    def ask(stage, prompt, schema, context, evidence=()):
        return gateway.call(stage, prompt, schema, evidence=evidence,
                            context={**context, '_audit_stage_failures': True}).output
    facts, ledger, outputs = e.review_visual_facts({'F001': fact(), 'F002': fact('F002', 'V002')}, assets,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'), ask, stage_runs=runs)
    assert len(calls) == len(runs) == 1 and not facts
    assert all(row['status'] == 'UNVERIFIED' for row in ledger)
    assert runs[0].stage == 'S09A_PRODUCT_VISUAL_00_SCENE'
    assert runs[0].call_status == 'HTTP_FAILED' and runs[0].request_id == 'fixture-http-403'
    assert runs[0].model_frame_count == 10 and len(runs[0].selected_evidence) == 10
    assert outputs[-1]['code'] == 'MODEL_HTTP_403' and 'non-retriable' in ledger[1]['reason']


@pytest.mark.parametrize('context,audited', [({}, False), ({'_audit_stage_failures': False}, False),
    ({'_audit_stage_failures': 'true'}, False), ({'_audit_stage_failures': True}, True),
    ({'_x02_policy_version': 'V04_1'}, True)])
def test_gateway_failure_audit_is_explicit_and_preserves_legacy_behavior(context, audited):
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    gateway = x02.QwenStageGateway(QwenChatCompletionsAdapter(api_key='fixture-key',
        model='qwen3.8-flash', base_url='https://fixture.invalid/v1',
        transport=lambda *args: (403, {'x-request-id': 'fixture-http-403'}, b'Forbidden')))
    with pytest.raises(x02.X02Error) as caught:
        gateway.call('S09A_PRODUCT_VISUAL_00', 'Fixture', {}, context=context)
    assert isinstance(caught.value, x02.X02StageCallError) == audited
    if audited:
        assert caught.value.code == 'MODEL_HTTP_403' and caught.value.stage_run.call_status == 'HTTP_FAILED'
    else:
        assert type(caught.value) is x02.X02Error


@pytest.mark.parametrize('recover', [False, True])
def test_invalid_value_json_has_bounded_retry_and_never_becomes_a_selection(recover):
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        if len(calls) == 1 or not recover: raise ValueError('Invalid structured output')
        return {'items': [moment_row()]}
    kept, ledger, output = e.review_moments([moment()], [], {'F001': fact()}, ask)
    assert len(calls) == 2 and calls[1].endswith('_RETRY') and output['call_failures']
    assert bool(kept) == recover
    assert ledger[0]['status'] == ('SELECTED' if recover else 'UNVERIFIED')


@pytest.mark.parametrize('error_type', ['value', 'stage_call'])
def test_moment_json_retry_can_still_receive_one_contract_repair(error_type):
    calls, runs = [], []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        if len(calls) == 1:
            if error_type == 'value': raise ValueError('Invalid JSON')
            raise x02.X02StageCallError('Invalid JSON', stage_run=failed_stage(stage), code='MODEL_RESPONSE_NOT_JSON')
        if len(calls) == 2: return {'items': [moment_row(evidence_frame_ids=[5000])]}
        assert stage.endswith('_REPAIR')
        return {'items': [moment_row()]}
    kept, ledger, output = e.review_moments([moment()], [], {'F001': fact()}, ask, stage_runs=runs)
    assert len(calls) == 3 and calls[1].endswith('_RETRY') and calls[2].endswith('_REPAIR')
    assert len(kept) == 1 and ledger[0]['status'] == 'SELECTED' and len(output['call_failures']) == 1
    assert len(runs) == (1 if error_type == 'stage_call' else 0)


def test_moment_timestamp_is_repaired_by_model_not_guessed_as_a_frame_id():
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        if stage.endswith('_REPAIR'):
            assert context['allowed_frame_ids']['M01'] == ['f0','f1']
            return {'items': [moment_row()]}
        return {'items': [moment_row(evidence_frame_ids=[5000])]}
    kept, ledger, output = e.review_moments([moment()], [], {'F001': fact()}, ask)
    assert len(calls) == 2 and calls[-1].endswith('_REPAIR')
    assert kept[0]['focus_frame_ids'] == ['f1'] and ledger[0]['status'] == 'SELECTED'
    assert output['original_output']['items'][0]['evidence_frame_ids'] == [5000]


@pytest.mark.parametrize('failure', ['rural_fact_id_then_timestamps', 'citywalk_empty_comparison'])
def test_recorded_moment_contract_failures_remain_blocked_after_one_repair(failure):
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        if failure == 'citywalk_empty_comparison':
            row = moment_row(comparison_reason='')
        elif stage.endswith('_REPAIR'):
            row = moment_row(evidence_frame_ids=[1000, 5000], focus_frame_id=5000)
        else:
            row = moment_row(evidence_frame_ids=['F001'], focus_frame_id='F001')
        with pytest.raises(jsonschema.ValidationError): jsonschema.validate({'items': [row]}, schema)
        return {'items': [row]}  # JSON mode may still ignore the supplied schema.
    kept, ledger, output = e.review_moments([moment()], [], {'F001': fact()}, ask)
    assert len(calls) == 2 and calls[-1].endswith('_REPAIR')
    assert not kept and ledger[0]['status'] == 'UNVERIFIED'
    assert output['contract_repair_output']['items'][0]['evidence_frame_ids'] == (
        ['f1'] if failure == 'citywalk_empty_comparison' else [1000, 5000])


def test_moment_repair_can_reference_already_selected_representative_in_full_batch():
    calls = []
    def ask(stage, prompt, schema, context, *, evidence=()):
        if "_FINAL_VERIFY" in stage:
            return scripted_final_verdict(context)
        calls.append(stage)
        if stage.endswith('_REPAIR'):
            assert len(context['comparison_candidates']) == 2 and [m['id'] for m in context['moments']] == ['M01']
            output = {'items': [moment_row(decision='DROP', value_type='DUPLICATE', event_group_id='M02')]}
            jsonschema.validate(output, schema)
            return output
        return {'items': [moment_row(event_group_id='unknown'), moment_row('M02')]}
    kept, ledger, _ = e.review_moments([moment(), moment('M02', 'F002')], [],
                                     {'F001': fact(), 'F002': fact('F002', 'V002')}, ask)
    assert len(calls) == 2 and [m['id'] for m in kept] == ['M02']
    assert ledger[0]['status'] == 'NOT_SELECTED' and ledger[1]['status'] == 'SELECTED'
