"""Anti-drop tests: verified specific subject beats uniform time-only sampling."""
from types import SimpleNamespace

import pytest

from diary_one_ci import chapter_media_pool as pool


def case(n=41):
    assets={};facts={}
    for i in range(n):
        aid=f'V{i+1:03d}';fid=f'F{i+1:03d}';src=f'source-{i:03d}'
        detail=('特别有辨识度的博物馆主楼，外墙刻有具体建筑名'
                if i in (5,35) else '普通平坦街道、道路边缘和远处行人')
        assets[aid]={'asset_id':src,'sequence_index':i,
          'original_duration_ms':10000,
          'frames':[{'frame_id':src+'-f0','relative_path':f'frames/{src}.jpg',
                     'source_timestamp_ms':5000}]}
        facts[fid]={'asset_id':aid,'source_asset_id':src,
           'text':detail,'visual_reviewed':True,
           'evidence_frame_ids':[src+'-f0']}
    return assets,facts


def picked(audit):
    return {c['asset_id'] for c in audit['shown_frames']}


def test_protected_real_subjects_survive_even_when_not_uniform_positions(tmp_path):
    a,f=case()
    bundle=SimpleNamespace(manifest_path=tmp_path/'bundle.json')
    old=pool.select_balanced_candidates(f,a,bundle,{'C01':list(f)},
                                             max_per_chapter=5,max_total=5)[2]
    assert 'V006' not in picked(old) and 'V036' not in picked(old)
    _,_,audit=pool.select_balanced_candidates(f,a,bundle,{'C01':list(f)},
            max_per_chapter=8,max_total=12,
            priority_fact_ids_by_chapter={'C01':['F006','F036']},
            episode_source_ranges_by_chapter={'C01':[
                {'episode_id':'E01','start_index':0,'end_index':10},
                {'episode_id':'E02','start_index':11,'end_index':30},
                {'episode_id':'E03','start_index':31,'end_index':40}]})
    assert audit['policy']=='CONTENT_FIRST_EPISODE_AND_ANCHOR_POOL_V02'
    assert {'V006','V036'}<=picked(audit)
    assert len(audit['shown_frames'])<=8
    assert not audit['priority_coverage_audit'][0]['protected_fact_ids_without_selected_frame']
    assert not audit['priority_coverage_audit'][0]['uncovered_episode_ids']
    assert all(c['fact_ids'] and c['frame_id'] in
       {fr['frame_id'] for fr in a[c['asset_id']]['frames']}
       for c in audit['shown_frames'])


def test_cross_time_fused_subject_remains_one_chapter_and_has_two_looks(tmp_path):
    a,f=case()
    bundle=SimpleNamespace(manifest_path=tmp_path/'bundle.json')
    _,evidence,audit=pool.select_balanced_candidates(
        f,a,bundle,{'C01':list(f)},
        max_per_chapter=4,max_total=6,
        priority_fact_ids_by_chapter={'C01':['F006','F036']},
        episode_source_ranges_by_chapter={'C01':[
          {'episode_id':'E01','start_index':0,'end_index':9},
          {'episode_id':'E04','start_index':33,'end_index':40}]})
    assert len(evidence)==4
    assert 'V006' in picked(audit) and 'V036' in picked(audit)
    assert audit['chapter_coverage'][0]['status']=='COVERED'


def test_unverified_priority_is_explicitly_rejected(tmp_path):
    a,f=case()
    f['F006']['visual_reviewed']=False
    with pytest.raises(ValueError,match='UNVERIFIED_OR_FOREIGN_PRIORITY_FACT'):
        pool.select_balanced_candidates(f,a,
            SimpleNamespace(manifest_path=tmp_path/'bundle.json'),
            {'C01':list(f)},max_per_chapter=8,max_total=8,
            priority_fact_ids_by_chapter={'C01':['F006']})


def test_episode_coverage_supplements_protected_anchor(tmp_path):
    a,f=case()
    _,_,audit=pool.select_balanced_candidates(f,a,
        SimpleNamespace(manifest_path=tmp_path/'bundle.json'),
        {'C01':list(f)},max_per_chapter=4,max_total=8,
        priority_fact_ids_by_chapter={'C01':['F006']},
        episode_source_ranges_by_chapter={'C01':[
          {'episode_id':'E01','start_index':0,'end_index':10},
          {'episode_id':'E02','start_index':11,'end_index':20},
          {'episode_id':'E03','start_index':21,'end_index':30},
          {'episode_id':'E04','start_index':31,'end_index':40}]})
    picked_indices=[a[row['asset_id']]['sequence_index'] for row in
                    audit['shown_frames']]
    assert any(0<=i<=10 for i in picked_indices)
    assert any(11<=i<=20 for i in picked_indices)
    assert any(21<=i<=30 for i in picked_indices)
    assert any(31<=i<=40 for i in picked_indices)
