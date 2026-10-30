"""R5_23 P0: S07 scene-anchor retention and auditable S08 transitions.

Tests use synthetic facts, no real image claims, API calls or model inference.
"""
from types import SimpleNamespace

from diary_one_ci import chapter_transition as t
from diary_one_ci import product_editor as p


def four_scene_fixture():
    facts = {
        'F1': {'asset_id': 'V1', 'text': '海港'},       # harbor
        'F2': {'asset_id': 'V2', 'text': '市场'},       # market
        'F3': {'asset_id': 'V3', 'text': '教堂'},       # church
        'F4': {'asset_id': 'V4', 'text': '植物园'},     # garden
        'F4b': {'asset_id': 'V5', 'text': '园林雕塑'},
    }
    draft = {'chapters': [
        {'id':'C01','theme':'港湾','fact_ids':['F1'],
         'focus_fact_ids':['F1'],'experience_kind':'CITYWALK'},
        {'id':'C02','theme':'市场','fact_ids':['F2'],
         'focus_fact_ids':['F2'],'experience_kind':'CITYWALK'},
        {'id':'C03','theme':'教堂','fact_ids':['F3'],
         'focus_fact_ids':['F3'],'experience_kind':'OTHER'},
        {'id':'C04','theme':'植物园','fact_ids':['F4','F4b'],
         'focus_fact_ids':['F4','F4b'],'experience_kind':'GARDEN'},
    ]}
    # The actual Sydney failure shape: market absorbed by harbor, church
    # given reused C02, all garden facts removed from reviewed Chapters.
    final = {'chapters': [
        {'id':'C01','theme':'海港与城中漫步','fact_ids':['F1','F2']},
        {'id':'C02','theme':'教堂内部','fact_ids':['F3']}
    ]}
    return facts, draft, final


def test_sydney_shape_detects_merge_chapter_id_reuse_and_missing_garden():
    facts, draft, final = four_scene_fixture()
    result = t.transition_audit(draft, final, facts)
    assert result['draft_chapter_count'] == 4
    assert result['final_chapter_count'] == 2
    by_id = {x['draft_chapter_id']: x for x in result['records']}
    assert by_id['C01']['transition'] == 'MERGED_WITH_ANOTHER_DRAFT'
    assert by_id['C02']['transition'] == 'MERGED_WITH_ANOTHER_DRAFT'
    assert by_id['C02']['best_reviewed_chapter_id'] == 'C01'
    assert by_id['C02']['same_id_reused_for_different_facts'] is True
    assert by_id['C03']['best_reviewed_chapter_id'] == 'C02'
    assert by_id['C03']['transition'] == 'RENUMBERED_OR_REGROUPED'
    assert by_id['C04']['transition'] == 'OMITTED'
    assert result['omitted_draft_chapters'] == ['C04']
    assert result['has_reused_id_collision'] is True
    assert set(result['editorial_dispositions_required']) >= {'C02','C04'}


def test_collect_anchor_assets_before_review_does_not_require_final_chapter():
    facts, draft, final = four_scene_fixture()
    proposals = t.draft_anchor_proposals(draft, facts)
    assert t.anchor_asset_ids(proposals) == ['V1','V2','V3','V4','V5']
    assert proposals[-1]['anchor_fact_ids'] == ['F4','F4b']
    assert proposals[-1]['status'] == 'ANCHORS_AVAILABLE'
    # Selection is an audit obligation, not a forced publication assertion.
    result = t.transition_audit(draft, final, facts,verified_facts={'F1','F2','F3','F4'})
    assert next(x for x in result['records'] if x['draft_chapter_id']=='C04')['verified_anchor_fact_ids'] == ['F4']


def test_unknown_foreign_focus_and_same_asset_do_not_inject_evidence():
    facts, draft, _ = four_scene_fixture()
    draft['chapters'][3]['fact_ids'].append('F_NOT_KNOWN')
    draft['chapters'][3]['focus_fact_ids'] = ['F4','F4','F_NOT_KNOWN','F1','F4b']
    facts['F4b']['asset_id'] = 'V4'
    proposals = t.draft_anchor_proposals(draft,facts,max_anchor_assets_per_chapter=1)
    garden = proposals[-1]
    assert garden['focus_fact_ids'] == ['F4','F4b']
    assert garden['anchor_fact_ids'] == ['F4']
    assert garden['anchor_asset_ids'] == ['V4']
    assert 'F_NOT_KNOWN' not in garden['draft_fact_ids']


def test_only_verified_draft_anchors_are_reserved_as_media_candidates(tmp_path):
    facts, draft, final = four_scene_fixture()
    proposals = t.draft_anchor_proposals(draft,facts)
    reserved = t.media_reservations(proposals,verified_facts={'F1','F2','F3','F4'})
    assert reserved == {
        'DRAFT_ANCHOR_C01':['F1'],
        'DRAFT_ANCHOR_C02':['F2'],
        'DRAFT_ANCHOR_C03':['F3'],
        'DRAFT_ANCHOR_C04':['F4']
    }
    verified = {
        fid:{**f, 'visual_reviewed':True,'evidence_frame_ids':[f['asset_id']+'-f0']}
        for fid,f in facts.items() if fid in {'F1','F2','F3','F4'}
    }
    assets = {
        aid:{'asset_id':aid,'frames':[{'frame_id':aid+'-f0',
            'source_timestamp_ms':5000, 'relative_path':'frames/'+aid+'.jpg'}]}
        for aid in ('V1','V2','V3','V4')
    }
    grouping={'C01':['F1','F2'],'C02':['F3'],**reserved}
    _,_,audit=p.media_selection_candidates(
        verified,assets,SimpleNamespace(manifest_path=tmp_path/'bundle.json'),
        preferred_assets=['V1','V2','V3'],
        max_frames=4,chapter_fact_groups=grouping)
    assert audit['shown_frame_count']==4
    assert {v['asset_id'] for v in audit['shown_frames']}=={'V1','V2','V3','V4'}
    assert next(v['status'] for v in audit['chapter_coverage']
                if v['chapter_id']=='DRAFT_ANCHOR_C04')=='COVERED'


def test_rejected_anchors_cannot_be_forced_into_candidate_pool():
    facts,draft,_=four_scene_fixture()
    proposals=t.draft_anchor_proposals(draft,facts)
    reserved=t.media_reservations(proposals,verified_facts={'F1','F2','F3'})
    assert reserved.get('DRAFT_ANCHOR_C04') is None
    report=t.transition_audit(draft,{'chapters':[]},facts,verified_facts={'F1','F2','F3'})
    assert report['records'][-1]['visual_review_status']=='NO_VERIFIED_ANCHOR'


def test_no_valid_focus_remains_explicitly_unknown_not_guess_from_all_facts():
    facts,draft,_=four_scene_fixture()
    draft['chapters']=[{
        'id':'C08','theme':'foo','fact_ids':['F4'],'focus_fact_ids':['F_UNKNOWN']}]
    proposals=t.draft_anchor_proposals(draft,facts)
    assert proposals[0]['status']=='NO_VALID_DRAFT_ANCHOR'
    assert not proposals[0]['anchor_asset_ids']
    assert not t.media_reservations(proposals,verified_facts=facts)



def test_only_omitted_focus_assets_require_extra_review_after_merge():
    facts,draft,final=four_scene_fixture()
    proposed=t.draft_anchor_proposals(draft,facts)
    lost=t.unrepresented_anchor_proposals(proposed,final,facts)
    assert [p['draft_chapter_id'] for p in lost]==['C04']
    assert lost[0]['lost_anchor_fact_ids']==['F4','F4b']
    assert t.anchor_asset_ids(lost)==['V4','V5']
    # A legitimate same-activity merge retaining all focus facts is not
    # changed by any artificial candidate reservations.
    restored={'chapters':[{'id':'C01','fact_ids':list(facts)}]}
    assert t.unrepresented_anchor_proposals(proposed,restored,facts)==[]
    # If an editor only keeps the first Garden focus fact, the second remains
    # eligible for review, not the already retained first.
    partial={'chapters':[{'id':'C01','fact_ids':['F1','F2','F3','F4']}]}
    missing=t.unrepresented_anchor_proposals(proposed,partial,facts)
    assert [x['draft_chapter_id'] for x in missing]==['C04']
    assert missing[0]['anchor_fact_ids']==['F4b']
    assert missing[0]['anchor_asset_ids']==['V5']
