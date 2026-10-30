"""Cross-domain *metamorphic* tests for Chapter transition evidence protection.

These cases exercise content-agnostic properties over all six Diary One user
personas. They are synthetic transition-contract tests, not visual-semantic
accuracy, real video benchmarks, or evidence of a correct Chapter boundary.
"""
from copy import deepcopy

import pytest

from diary_one_ci import chapter_transition as t


# Fields reflect the six fixed user personas, but the transition detector
# must not look at scene names, language, activity type, or duration.
SCENARIOS = (
    ('unscripted_daily', 'OTHER',
     '午间在桌旁吃饭', '夜间在厨房做饭'),
    ('travel_citywalk', 'CITYWALK',
     '海滨步道', '历史建筑参观'),
    ('family_outing', 'FAMILY_OUTING',
     '公园里推婴儿车', '儿童在游乐设施玩耍'),
    ('hands_busy_hobby', 'COOKING',
     '厨房切菜', '陶艺工坊制陶'),
    ('light_outdoor', 'CYCLING',
     '林间骑行', '停在草地看远处的桥'),
    ('fishing', 'FISHING',
     '抛竿等待', '鱼上钩并拿在手里'),
)


def transition_case(kind, first, second):
    facts = {
        'F101': {'asset_id': 'A101', 'text': first},
        'F201': {'asset_id': 'A201', 'text': second},
    }
    draft = {'chapters': [
        {'id': 'C01', 'experience_kind': kind, 'theme': first,
         'fact_ids': ['F101'], 'focus_fact_ids': ['F101']},
        {'id': 'C02', 'experience_kind': kind, 'theme': second,
         'fact_ids': ['F201'], 'focus_fact_ids': ['F201']},
    ]}
    # Only the first proposed experience still occurs in a Chapter.
    reviewed = {'chapters': [{'id':'C01', 'fact_ids':['F101']}]}
    return facts, draft, reviewed


@pytest.mark.parametrize('persona,kind,first,second', SCENARIOS)
def test_lost_anchor_requires_review_independent_of_scenario(
    persona, kind, first, second
):
    facts, draft, reviewed = transition_case(kind, first, second)
    originals = deepcopy((facts,draft,reviewed))
    candidate = t.unrepresented_anchor_proposals(
        t.draft_anchor_proposals(draft,facts),reviewed,facts
    )
    assert [row['draft_chapter_id'] for row in candidate] == ['C02'], persona
    assert candidate[0]['anchor_fact_ids'] == ['F201']
    assert candidate[0]['anchor_asset_ids'] == ['A201']
    # Requires evidence review, NOT a guaranteed new Chapter.
    audit = t.transition_audit(draft,reviewed,facts)
    assert audit['records'][1]['transition'] == 'OMITTED'
    assert audit['records'][1]['needs_explicit_editorial_disposition']
    assert (facts,draft,reviewed) == originals


@pytest.mark.parametrize('persona,kind,first,second', SCENARIOS)
def test_same_episode_merge_with_all_facts_kept_does_not_force_chapters(
    persona, kind, first, second
):
    facts, draft, _ = transition_case(kind, first, second)
    # All facts are represented: a single Chapter is allowed regardless of
    # whether a later *semantic* planner judges two experiences distinct.
    merged = {'chapters': [{'id':'C01','fact_ids':['F101','F201']}]}
    extra = t.unrepresented_anchor_proposals(
        t.draft_anchor_proposals(draft,facts),merged,facts
    )
    assert extra == [], persona
    audit = t.transition_audit(draft,merged,facts)
    assert audit['records'][1]['transition'] == 'MERGED_WITH_ANOTHER_DRAFT'
    assert audit['records'][1]['unaccounted_fact_ids'] == []


@pytest.mark.parametrize('persona,kind,first,second', SCENARIOS)
def test_loss_detection_not_tuned_to_naming_chapter_number_or_language(
    persona, kind, first, second
):
    facts, draft, reviewed = transition_case(kind, first, second)
    proposals = t.draft_anchor_proposals(draft,facts)
    selected=t.unrepresented_anchor_proposals(proposals,reviewed,facts)
    # Change theme and ID strings without changing fact assignment.
    renamed = deepcopy(draft)
    renamed['chapters'][0]['id'] = 'A_日常'
    renamed['chapters'][1]['id'] = 'B_Diario'
    renamed['chapters'][0]['theme'] = 'Χρονικό'
    renamed['chapters'][1]['theme'] = 'ملحوظة'
    changed = t.unrepresented_anchor_proposals(
        t.draft_anchor_proposals(renamed,facts), reviewed, facts)
    assert [x['anchor_fact_ids'] for x in selected] == [
        x['anchor_fact_ids'] for x in changed], persona
    assert [x['anchor_asset_ids'] for x in selected] == [
        x['anchor_asset_ids'] for x in changed], persona


@pytest.mark.parametrize('persona,kind,first,second', SCENARIOS)
def test_a_smaller_moment_counts_as_provisional_representation(
    persona, kind, first, second
):
    facts, draft, reviewed = transition_case(kind, first, second)
    reviewed['moments'] = [
        {'id':'M01','fact_id':'F201','parent_chapter_id':None}
    ]
    dropped = t.unrepresented_anchor_proposals(
        t.draft_anchor_proposals(draft,facts),reviewed,facts)
    assert dropped == [], persona
    disposition = t.transition_audit(draft,reviewed,facts)['records'][1]
    assert disposition['transition']=='REPRESENTED_AS_MOMENT'
    assert disposition['represented_as_moment_fact_ids']==['F201']
    assert disposition['unaccounted_fact_ids']==[]
    assert disposition['needs_explicit_editorial_disposition']
    # The existence of the provisional Moment is NOT a claim that it
    # passed later image or copy review: it can still be rejected.


def test_partial_moment_representation_only_reviews_still_missing_anchor():
    facts,draft,reviewed=transition_case('FISHING','浮漂等待','鱼入网')
    facts['F202']={'asset_id':'A202','text':'鱼从水里被提起'}
    draft['chapters'][1]['fact_ids'].append('F202')
    draft['chapters'][1]['focus_fact_ids'].append('F202')
    reviewed['moments']=[{'id':'M02','fact_id':'F201'}]
    missing=t.unrepresented_anchor_proposals(
        t.draft_anchor_proposals(draft,facts),reviewed,facts)
    assert len(missing)==1
    assert missing[0]['anchor_fact_ids']==['F202']
    assert missing[0]['anchor_asset_ids']==['A202']
    disposition=t.transition_audit(draft,reviewed,facts)['records'][1]
    assert disposition['transition']=='PARTIALLY_REPRESENTED_AS_MOMENT'
    assert disposition['unaccounted_fact_ids']==['F202']


@pytest.mark.parametrize('bad_moments', [None,{},'',123,['bad',None,{}]])
def test_malformed_moment_rows_cannot_create_fabricated_review_evidence(bad_moments):
    facts,draft,reviewed=transition_case('CITYWALK','步道','展览')
    reviewed['moments']=bad_moments
    omitted=t.unrepresented_anchor_proposals(
        t.draft_anchor_proposals(draft,facts),reviewed,facts)
    assert len(omitted)==1 and omitted[0]['anchor_fact_ids']==['F201']



def test_long_repetitive_fishing_day_does_not_infer_four_chapters_from_duration():
    # Four provisional group labels over 160 sampled clips of one repeated
    # activity are not a reason for producing four Chapters. The true semantic
    # decision is left to Chapter planning; this audit must not fabricate loss.
    facts = {
        f'F{i:03d}': {'asset_id': f'V{i:03d}', 'text': '同一钓点抛竿或等待'}
        for i in range(160)
    }
    draft = {'chapters': [
        {'id': f'C{j+1:02d}', 'theme': '钓鱼',
         'experience_kind': 'FISHING',
         'fact_ids': [f'F{i:03d}' for i in range(j*40,(j+1)*40)],
         'focus_fact_ids': [f'F{i:03d}' for i in range(j*40,j*40+3)]}
        for j in range(4)
    ]}
    consolidated = {'chapters': [
        {'id': 'C01', 'fact_ids': list(facts)}
    ]}
    candidates = t.unrepresented_anchor_proposals(
        t.draft_anchor_proposals(draft,facts),
        consolidated, facts
    )
    audit = t.transition_audit(draft,consolidated,facts)
    assert candidates == []
    assert audit['draft_chapter_count'] == 4
    assert audit['final_chapter_count'] == 1
    assert audit['omitted_draft_chapters'] == []
    assert all(not x['unaccounted_fact_ids'] for x in audit['records'])
    assert all(x['transition'] == 'MERGED_WITH_ANOTHER_DRAFT'
               for x in audit['records'])
