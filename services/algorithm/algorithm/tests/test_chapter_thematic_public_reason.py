"""Regression: model can discuss revisiting a place internally, without
publishing unverified 'returned again' travel chronology as a Chapter fact.
"""
from diary_one_ci import chapter_theme_hierarchy as h
from diary_one_ci.product_editor import compile_structure_wire


def test_unproven_again_in_private_reason_cannot_block_a_valid_chapter():
    assets={'V001':{'asset_id':'clip-A','sequence_index':0},
            'V002':{'asset_id':'clip-B','sequence_index':1}}
    facts={'F001':{'id':'F001','asset_id':'V001','text':'白色帆形建筑',
                   'visual_reviewed':True,'evidence_frame_ids':['A-0']},
           'F002':{'id':'F002','asset_id':'V002','text':'水面与船只',
                   'visual_reviewed':True,'evidence_frame_ids':['B-0']}}
    input_chapter={'title':'海港景观和建筑','experience_kind':'CITYWALK',
                   'episode_ids':['E01'],'source_indices':[0,1],
                   'anchor_fact_ids':['F001'],
                   'reason':'再次回到上一个地方，虽然图片并未证明整个路线'}
    wire=h.build_wire([input_chapter],assets,facts)
    assert wire['chapters'][0]['grouping_reason']!=''
    assert '再次' not in wire['chapters'][0]['grouping_reason']
    assert '归途' not in wire['chapters'][0]['grouping_reason']
    assert input_chapter['reason'].startswith('再次')
    compiled,_,errors,_=compile_structure_wire(wire,facts,assets,5)
    assert not errors
    assert len(compiled)==1
