"""General evidence-backed editorial actions, NOT an in-cloud LLM Judge."""
from copy import deepcopy

import pytest

from diary_one_ci import chapter_editorial_decision_flow as editor


def ep(i,theme,kind,fact):
    return {'episode_id':f'E{i:02d}','start_index':(i-1)*3,'end_index':i*3-1,
        'theme':theme,'experience_kind':kind,'fact_count':1,
        'representative_verified_facts':[{
            'fact_id':f'F{i:02d}','source_index':(i-1)*3+1,'text':fact}]}


def test_content_first_advisory_flags_mixed_market_and_garden():
    episodes=[
      ep(1,'露天工艺市场','MARKET_SHOPPING','红色棚顶的工艺品摊位上摆放木雕手工艺品'),
      ep(2,'植物花坛和自然小径','GARDEN','植物园花坛中可见多肉植物与弯曲的自然小径'),
      ep(3,'港口码头历史帆船','CITYWALK','木质船体停泊于蓝色海湾，桅杆与帆布明显'),
    ]
    plan=[{'title':'市场和植物园','episode_ids':['E01','E02']},
          {'title':'码头帆船','episode_ids':['E03']}]
    audit=editor.action_hints(plan,episodes)
    actions=audit['actions']
    assert any(z['action']=='MIXED_THEME_REVIEW'
               and z['episode_ids']==['E01','E02']
               and 'F01' in z['supporting_fact_ids'] for z in actions)
    assert all(a.get('automatically_merge') is not True for a in actions)
    assert all(a.get('automatically_reassign') is not True for a in actions)


def test_repeated_concrete_subject_across_time_may_trigger_merge_not_forced_split():
    episodes=[
      ep(1,'圆形剧院外观与玻璃穹顶','CITYWALK','大型圆形剧院外观有玻璃穹顶和白色拱门'),
      ep(2,'市场购买工艺品','MARKET_SHOPPING','工艺品摊位有手工首饰和红色棚顶'),
      ep(3,'玻璃穹顶圆形剧院内景','CITYWALK','同一圆形剧院的玻璃穹顶映出白色拱门和灰色墙面'),
    ]
    plan=[{'title':'剧院建筑初见','episode_ids':['E01']},
          {'title':'市场','episode_ids':['E02']},
          {'title':'剧院内部','episode_ids':['E03']}]
    hints=editor.action_hints(plan,episodes)
    same=[a for a in hints['actions'] if a['action']=='SAME_THEME_CROSS_CHAPTER_MERGE_REVIEW']
    assert same and same[0]['chapter_indices']==[0,2]
    assert 'F01' in same[0]['supporting_fact_ids'] and 'F03' in same[0]['supporting_fact_ids']
    # A shared subject across source time is not a mandate to merge or split.
    assert same[0]['automatically_merge'] is False


def test_different_places_with_same_walking_label_not_automatically_merged():
    episodes=[
      ep(1,'石雕纪念建筑','CITYWALK','石雕纪念建筑有拱形大门与钟楼'),
      ep(2,'港口帆船','CITYWALK','港口有高耸的桅杆和木质帆船'),
      ep(3,'植物园自然步道','CITYWALK','花坛里面有绣球花与园林池塘'),
    ]
    grouping=[{'title':e['theme'],'episode_ids':[e['episode_id']]} for e in episodes]
    hint=editor.action_hints(grouping,episodes)
    assert all(a['action']!='SAME_THEME_CROSS_CHAPTER_MERGE_REVIEW'
               for a in hint['actions'])


def test_each_evidence_card_uses_real_fact_id_without_making_entity_claims():
    episodes=[ep(1,'室内历史建筑','CITYWALK','室内教堂有彩色玻璃与高耸的石柱')]
    cards=editor.episode_cards(episodes)
    assert cards[0]['episode_id']=='E01'
    assert cards[0]['real_visual_evidence'][0]['fact_id']=='F01'
    assert cards[0]['real_visual_evidence'][0]['source_index']==1
    assert cards[0]['facts_are_grounded']
    assert 'scenelet' not in cards[0]


def test_invalid_duplicate_episode_ownership_is_not_silently_accepted():
    e=[ep(1,'城市市场','MARKET_SHOPPING','路边市场售卖许多鲜花')]
    with pytest.raises(ValueError,match='EPISODE_OWNERSHIP'):
        editor.action_hints([{'title':'市场','episode_ids':['E01']},
                             {'title':'市场','episode_ids':['E01']}],e)


def test_late_revisit_automatically_stays_valid_in_initial_harbor_chapter():
    episodes=[
      ep(1,'Opera House Waterfront','CITYWALK',
         'White shells of the Opera House at a waterfront promenade'),
      ep(2,'Historic Market Quarter','MARKET_SHOPPING',
         'Historic brick market food stalls with red awnings'),
      ep(3,'Royal Botanic Garden','GARDEN',
         'Garden cactus flower bed and palm-lined paths'),
      ep(4,'Opera House Return View','OUTDOOR_SCENERY',
         'Opera House white shells over the water'),
    ]
    before=[
      {'title':'Harbor Opera House and markets','episode_ids':['E01','E02','E04']},
      {'title':'Garden landscape and plants','episode_ids':['E03']}]
    result=editor.action_hints(before,episodes)
    assert not any(a['action']=='OUTLIER_EPISODE_REVIEW'
       and a['episode_ids']==['E04'] for a in result['actions'])
    wrong=[
      {'title':'Harbor Opera House and markets','episode_ids':['E01','E02']},
      {'title':'Garden landscape and Opera House','episode_ids':['E03','E04']}]
    moves=editor.action_hints(wrong,episodes)['actions']
    assert any(a['action']=='OUTLIER_EPISODE_REVIEW'
        and a['episode_ids']==['E04']
        and a['suggested_existing_chapter_index']==0
        for a in moves)


def test_generic_activity_label_never_proves_revisited_place_identity():
    episodes=[
      ep(1,'Citywalk around old building','CITYWALK',
         'Stones and brick walls of one historical building'),
      ep(2,'Citywalk around river boat','CITYWALK',
         'Watercraft crossing river by iron bridge'),
    ]
    a=editor.action_hints([
      {'title':'Historic architecture','episode_ids':['E01']},
      {'title':'River boat','episode_ids':['E02']}],episodes)
    assert not any(t['action']=='SAME_THEME_CROSS_CHAPTER_MERGE_REVIEW'
                   for t in a['actions'])


def test_slot_budget_editor_merges_related_themes_before_splitting_mixed_group():
    episodes=[
       ep(1,'Architecture by the waterfront','CITYWALK','Prominent white performance building'),
       ep(2,'Street historic markets','MARKET_SHOPPING','Market stalls and food baskets'),
       ep(3,'Harbour Bridge Coastal Walk','NATURE_WALK','Waterfront beside large steel bridge'),
       ep(4,'Darling Harbour Maritime Heritage','MUSEUM','Harbour ship and museum gallery'),
       ep(5,'Chinatown indoor markets','MARKET_SHOPPING','Shop stalls and colorful products'),
       ep(6,'CBD historic shopping arcades','CITYWALK','Indoor stone shopping arcade'),
       ep(7,'City park monuments','PARK_LEISURE','Stone fountain and bronze monument'),
       ep(8,'Royal botanic garden plants','GARDEN','Cactus flowerbed and garden tree roots'),
    ]
    grouping=[
       {'title':'Waterfront performance architecture','episode_ids':['E01']},
       {'title':'Street Historic Market','episode_ids':['E02']},
       {'title':'Harbour Bridge Coastal Walk','episode_ids':['E03']},
       {'title':'Darling Harbour Maritime Heritage','episode_ids':['E04']},
       {'title':'CBD Chinatown Shopping Arcades & Botanical Garden',
        'episode_ids':['E05','E06','E07','E08']}]
    suggestion=editor.budgeted_edit_recipe(grouping,episodes)
    assert suggestion['status']=='ADVISORY_LAYOUT_WITH_BUDGETED_MERGE_AND_SPLIT'
    assert suggestion['thematic_merge_pair_indices']==[2,3]
    assert len(suggestion['candidate_episode_layouts'])==5
    merged=next(a for a in suggestion['candidate_episode_layouts']
          if a['action']=='MERGE_RELATED_EXISTING_THEMES')
    assert merged['episode_ids']==['E03','E04']
    nature=next(a for a in suggestion['candidate_episode_layouts']
          if a['action']=='PROTECT_DISTINCT_NATURE_EXPERIENCES')
    assert nature['episode_ids']==['E07','E08']
    flat=[e for p in suggestion['candidate_episode_layouts'] for e in p['episode_ids']]
    assert sorted(flat)==[f'E{i:02d}' for i in range(1,9)]


def test_budgeted_merge_does_not_assume_any_adjacent_streets_are_same_topic():
    episodes=[
       ep(1,'White sculptural architecture','CITYWALK','Concrete design arts'),
       ep(2,'Fishing at river','FISHING','Fish on line near waterside'),
       ep(3,'Botanical flowerbeds','GARDEN','Different garden plants'),
       ep(4,'Street market','MARKET_SHOPPING','Stalls with jewelry')
    ]
    grouped=[
       {'title':'Art museums','episode_ids':['E01']},
       {'title':'Water fishing','episode_ids':['E02']},
       {'title':'Garden plus shop','episode_ids':['E03','E04']}]
    candidate=editor.budgeted_edit_recipe(grouped,episodes,chapter_limit=3)
    assert candidate['status']=='NO_SAFE_THEMATIC_SIBLING_MERGE'
    assert candidate['candidate_episode_layouts']==[]
