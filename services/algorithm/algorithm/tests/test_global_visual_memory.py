"""Global memory never forgets verified fact IDs or hallucinates entity matching."""
from diary_one_ci import global_visual_memory


def make(n=26):
    assets={}
    facts={}
    obs=[]
    for i in range(n):
        aid=f'V{i+1:03d}';sid=f'clip-{i:03d}'
        text=('Visitor photographed the Old Library Hall at the square'
            if i in (2,24) else f'Ordinary street scene {i} with people walking')
        assets[aid]={'asset_id':sid,'sequence_index':i,
            'frames':[{'frame_id':f'{sid}-f0'}]}
        facts[f'F{i+1:03d}']={'asset_id':aid,'text':text,'visual_reviewed':True,
            'evidence_frame_ids':[f'{sid}-f0'],'support_grade':'STRONG'}
        obs.append({'source_asset_id':sid,'event_salience':'MEDIUM' if i in (2,24) else 'LOW'})
    return assets,facts,obs


def test_auditable_lexical_cross_time_memories_and_not_verified_identity():
    a,f,o=make()
    m=global_visual_memory.build(a,f,o,max_protected=15)
    assert len(m['all_evidence_fact_ids'])==26
    assert len(m['source_index'])==26
    assert all(z['fact_id'] in f for z in m['priority_anchors'])
    assert all(z['frame_id'] in a[f[z['fact_id']]['asset_id']]['frames'][0]['frame_id']
               for z in m['priority_anchors'])
    threads=[z for z in m['cross_time_entity_candidates']
             if 'old library hall' in z['literal_mention']]
    assert len(threads)==1
    assert threads[0]['source_indices']==[2,24]
    assert threads[0]['relation_status']=='POSSIBLE_CROSS_TIME_COREFERENCE_NOT_VERIFIED'
    ctx=global_visual_memory.editor_context(m,max_anchors=8)
    assert len(ctx['priority_anchors'])<=8
    assert 'source_index' not in ctx


def test_does_not_treat_unverified_or_missing_frames_as_grounded_memory():
    a,f,o=make()
    f['F003']['visual_reviewed']=False
    f['F025']['evidence_frame_ids']=['someone-elses-frame']
    m=global_visual_memory.build(a,f,o)
    assert 'F003' not in m['all_evidence_fact_ids']
    assert 'F025' not in m['all_evidence_fact_ids']
    assert m['cross_time_entity_candidates']==[]


def test_no_assumed_capture_clock():
    a,f,o=make()
    m=global_visual_memory.build(a,f,o)
    assert all(q['time_record']['time_reliability']=='UNKNOWN'
        for q in m['source_index'])
