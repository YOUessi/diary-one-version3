"""S14 five-Chapter contract, verified parentage and capacity regression."""
from copy import deepcopy

from diary_one_ci import product_editor as p


def evidence():
    facts = {f'F{i:03}': {
        'id': f'F{i:03}', 'asset_id': f'V{i:03}',
        'visual_reviewed': True, 'text': '一段有直接图像证据的城市经历',
        'evidence_frame_ids': [f'frame-{i}']} for i in range(1, 7)}
    chapters = []
    for i in range(1,6):
        chapters.append({'id':f'C{i:02}', 'theme':f'独立体验{i}',
            'fact_ids':[f'F{i:03}'],
            'selected_asset_ids':[f'V{i:03}'], 'hero_asset_id':f'V{i:03}'})
    return facts,chapters


def moment(id='M90', fact='F001', parent=None, relations=None):
    if relations is None:
        relations=[{'chapter_id':f'C{i:02}','relation':'DISTINCT'} for i in range(1,6)]
    return {'id':id,'parent_chapter_id':parent,'fact_id':fact,'focus':'具有价值的场景细节',
        'revisit_reason':'值得回看的具体图像事实','chapter_relations':relations}


def test_s14_five_published_chapters_are_not_silently_truncated():
    facts,chapters=evidence()
    original=deepcopy(chapters)
    raw={'decisions':[{'asset_id':'V006','disposition':'REDUNDANT',
                       'reason':'语义已经纳入出版主题','covered_by_ids':['C05'],'moment':None}]}
    _,ledger=p.compile_recovery(raw, {'V006'}, chapters,[],facts,{},set())
    assert ledger[0]['status']=='VALIDATED'
    assert chapters == original


def test_complete_claimed_distinct_is_explicitly_challenged_and_can_be_nested():
    facts,chapters=evidence()
    raw={'decisions':[{'asset_id':'V001','disposition':'ADD_MEMORY',
                       'reason':'一处单独回顾的细节','moment':moment()}]}
    seen=[]
    def ask(stage,prompt,schema,context):
        seen.append(stage)
        return {'items':[{'moment_id':'M90','relations':{
            **{f'C{i:02}':'DISTINCT' for i in range(2,6)},
            'C01':'WITHIN_CHAPTER'}}]}
    corrected,response,context=p.review_coverage_relations(
        raw,chapters,facts,ask=ask,stage='S14B_PRODUCT_RELATION_REVIEW',
        review_claimed_distinct=True)
    assert seen==['S14B_PRODUCT_RELATION_REVIEW']
    m=corrected['decisions'][0]['moment']
    assert m['parent_chapter_id']=='C01'
    assert m['chapter_relations']==[{'chapter_id':'C01','relation':'WITHIN_CHAPTER'}]
    assert p.compile_recovery(corrected,{'V001'},chapters,[],facts,{},set())[1][0]['status']=='BLOCKED'
    accepted,ledger=p.compile_recovery(corrected,{'V001'},chapters,[],facts,{},set(),
                                       allow_reviewed_nested=True)
    assert ledger[0]['status']=='VALIDATED'
    assert len(accepted)==1 and accepted[0]['parent_chapter_id']=='C01'


def test_reviewed_nested_moment_respects_parent_fact_and_two_highlight_limit():
    facts,chapters=evidence()
    row=moment(parent='C01',relations=[{'chapter_id':'C01','relation':'WITHIN_CHAPTER'}])
    raw={'decisions':[{'asset_id':'V001','disposition':'ADD_MEMORY','reason':'可见细节','moment':row}]}
    previous=[moment('M11',parent='C01'),moment('M12',parent='C01')]
    added,ledger=p.compile_recovery(raw,{'V001'},chapters,previous,facts,{},set(),
                                    allow_reviewed_nested=True)
    assert not added and ledger[0]['status']=='BLOCKED'
    row['parent_chapter_id']='C02'
    _,ledger=p.compile_recovery(raw,{'V001'},chapters,[],facts,{},set(),
                                allow_reviewed_nested=True)
    assert ledger[0]['status']=='BLOCKED'


def test_capacity_limit_is_wrong_with_three_nested_but_zero_standalone():
    facts,chapters=evidence()
    rows=[{'asset_id':f'V{i:03}','disposition':'ADD_MEMORY',
           'reason':'恢复可见的章内高光',
           'moment':moment(f'M{i+89}',f'F{i:03}',f'C{i:02}',
               [{'chapter_id':f'C{i:02}','relation':'WITHIN_CHAPTER'}])}
          for i in (1,2,3)]
    rows.append({'asset_id':'V006','disposition':'CAPACITY_LIMIT','reason':'此前错误认为已满','moment':None})
    added,ledger=p.compile_recovery({'decisions':rows},{r['asset_id'] for r in rows},
                                    chapters,[],facts,{},set(),allow_reviewed_nested=True)
    assert len(added)==3
    assert all(m['parent_chapter_id'] is not None for m in added)
    assert ledger[-1]['status']=='BLOCKED'
    assert ledger[-1]['reason']=='Coverage claimed capacity limit while slots remain'


def test_invalid_relation_response_does_not_convert_unknown_parent():
    facts,chapters=evidence()
    raw={'decisions':[{'asset_id':'V001','disposition':'ADD_MEMORY','reason':'具体发现','moment':moment()}]}
    candidates=p.recovery_relation_candidates(raw,chapters,review_claimed_distinct=True)
    assert len(candidates)==1
    invalid={'items':[{'moment_id':'M90','relations':{'C01':'WITHIN_CHAPTER'}}]}
    corrected=p.apply_relation_review(raw,invalid,candidates,chapters)
    assert corrected['decisions'][0]['moment']['parent_chapter_id'] is None
    assert raw['decisions'][0]['moment']['parent_chapter_id'] is None


def test_post_relation_source_owner_never_becomes_duplicate_standalone():
    facts,chapters=evidence()
    raw={'decisions':[{'asset_id':'V001','disposition':'ADD_MEMORY',
                       'reason':'虽是独特的小片段仍使用同一个来源事实',
                       'moment':moment()}]}
    # The model reviewed and called this DISTINCT, but immutable full-day
    # evidence ownership says F001 belongs to the existing C01 episode.
    additions,ledger=p.compile_recovery(raw,{'V001'},chapters,[],facts,{},set(),
        allow_reviewed_nested=True,source_owned_nested=True)
    assert len(additions)==1 and additions[0]['parent_chapter_id']=='C01'
    assert ledger[0]['status']=='VALIDATED'
    assert raw['decisions'][0]['moment']['parent_chapter_id'] is None


def test_third_source_owned_highlight_reports_real_parent_cap_not_false_standalone():
    facts,chapters=evidence()
    facts.update({'F007':{'id':'F007','asset_id':'V007','visual_reviewed':True,
                          'evidence_frame_ids':['frame-7'],'text':'可见艺术装置'},
                  'F008':{'id':'F008','asset_id':'V008','visual_reviewed':True,
                          'evidence_frame_ids':['frame-8'],'text':'可见街头表演'}})
    chapters[0]['fact_ids']+=['F007','F008']
    def entry(aid,mid,fid):
        return {'asset_id':aid,'disposition':'ADD_MEMORY',
                'reason':'经过审查的图像细节','moment':moment(mid,fid)}
    rows=[entry('V001','M90','F001'),entry('V007','M91','F007'),
          entry('V008','M92','F008')]
    additions,ledger=p.compile_recovery({'decisions':rows},{r['asset_id'] for r in rows},
        chapters,[],facts,{},set(),allow_reviewed_nested=True,
        source_owned_nested=True)
    assert sorted(m['id'] for m in additions)==['M90','M91']
    third=next(r for r in ledger if r['asset_id']=='V008')
    assert third['status']=='VALIDATED'
    assert third['capacity_scope']=='CHAPTER_HIGHLIGHT'
    assert third['disposition']=='CAPACITY_LIMIT'
    assert third['covered_by_ids']==['C01']
    assert third['not_published_candidate']['id']=='M92'
    assert all(r['status']=='VALIDATED' for r in p.reconcile_published_capacity(
        ledger,additions,{m['id']:{'id':m['id']} for m in additions}))
