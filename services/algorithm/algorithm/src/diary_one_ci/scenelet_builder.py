"""Deterministic, domain-independent global scenelet map.

No AI inference, filename interpretation, or raw video required. Uses only
already-transmitted fact/observation references and optional verified temporal
metadata/features; scenelet proposals are hypotheses, NOT observed events or
ground truth. Never infer a continuous route from import order.
"""
from collections import defaultdict
from hashlib import sha256
import math
import re

SCHEMA = 'DIARY_ONE_SCENELET_MAP_V01'
CLOCK_SOURCES = frozenset({'DEVICE_VERIFIED','DEVICE_CLOCK_SYNCED','EXIF_OFFSET','LIBRARY_METADATA_VERIFIED'})
CONFIDENCE_SOURCES = frozenset({'VERIFIED','TRUSTED'})
_UNICODE_TOKEN = re.compile(r'[A-Za-z0-9]{2,}|[\u3400-\u9fff]')


def tokens(text):
    """Unicode-aware character bigrams plus ASCII words, not language-specific scene keywords."""
    s = str(text or '').casefold()
    result = set(x for x in re.findall(r'[a-z0-9]{2,}', s))
    chars = ''.join(c for c in s if '\u3400' <= c <= '\u9fff')
    result.update(chars[i:i + 2] for i in range(len(chars) - 1))
    if len(chars) == 1:
        result.add(chars)
    return result


def cosine(a,b):
    if not (isinstance(a,(list,tuple)) and isinstance(b,(list,tuple))
            and len(a)==len(b) and len(a)>0 and len(a)<=4096):
        return None
    try:
        x,y=[float(v) for v in a],[float(v) for v in b]
    except (TypeError,ValueError):
        return None
    if not all(math.isfinite(v) for v in x+y):
        return None
    norms=math.sqrt(sum(v*v for v in x))*math.sqrt(sum(v*v for v in y))
    return max(-1.,min(1.,sum(v*w for v,w in zip(x,y))/norms)) if norms>1e-10 else None


def time_record(asset):
    """Verify clock provenance before treating a capture offset as elapsed time."""
    source=asset.get('capture_time_source') or asset.get('captureTimeSource')
    confidence=asset.get('capture_time_confidence') or asset.get('captureTimeConfidence')
    stamp=asset.get('capture_time_ms',asset.get('creationTimeMs'))
    if (source in CLOCK_SOURCES and confidence in CONFIDENCE_SOURCES
            and type(stamp) in (int,float) and math.isfinite(stamp)
            and 946684800000<=stamp<=4102444800000):
        return {'capture_time_ms':int(stamp),'time_reliability':'VERIFIED',
                'time_source':source}
    return {'capture_time_ms':None,'time_reliability':'UNKNOWN',
            'time_source':'IMPORT_SEQUENCE_ONLY'}


def records(assets, facts, observations=()):
    by_asset=defaultdict(list)
    for fid,fact in facts.items():
        aid=fact.get('asset_id')
        if aid in assets:
            by_asset[aid].append((fid,fact))
    obs_by_asset={}
    for o in observations or ():
        if isinstance(o,dict) and isinstance(o.get('source_asset_id'),str):
            obs_by_asset[o['source_asset_id']]=o
    output=[]
    for aid,asset in sorted(assets.items(), key=lambda x:(x[1].get('sequence_index',0),x[0])):
        sequence=asset.get('sequence_index')
        if type(sequence) is not int or sequence<0:
            raise ValueError('Invalid source sequence; refusing to infer chronology')
        rows=by_asset[aid]
        statement=' '.join(f.get('text','') for _,f in rows)
        obs=obs_by_asset.get(asset.get('asset_id'),{})
        frame_ids=[fr.get('frame_id') for fr in asset.get('frames',[]) if isinstance(fr,dict)]
        visual_vectors=[fr.get('embedding') for fr in asset.get('frames',[]) if isinstance(fr,dict) and fr.get('embedding')]
        # Optional embeddings must be from the same configured model; never compare
        # if this declared identity is missing or inconsistent.
        emb_model=asset.get('embedding_model_id') or None
        embedding=visual_vectors[0] if emb_model and visual_vectors else None
        output.append({'asset_id':aid,'source_sequence_index':sequence,
            'source_asset_id':asset.get('asset_id'),
            'fact_ids':[fid for fid,_ in rows],
            'evidence_frame_ids':list(dict.fromkeys(frame for _,fact in rows
                for frame in fact.get('evidence_frame_ids',[]) if frame in frame_ids)),
            'activity_kind':obs.get('activity_code') or 'UNKNOWN',
            'setting_kind':obs.get('setting_code') or 'UNKNOWN',
            'event_kind':obs.get('event_kind') or 'UNKNOWN',
            'subject_codes':list(obs.get('subject_codes') or []),
            'text_tokens':tokens(statement),
            'text_excerpt':statement[:280],
            'embedding_model_id':emb_model,
            'embedding':embedding,
            **time_record(asset)})
    return output


def pair_similarity(a,b):
    ta,tb=a['text_tokens'],b['text_tokens']
    lexical=len(ta&tb)/len(ta|tb) if ta and tb else 0.
    image=(cosine(a['embedding'],b['embedding'])
        if a['embedding_model_id'] and a['embedding_model_id']==b['embedding_model_id'] else None)
    return {'lexical':round(lexical,4),'visual':round(image,4) if image is not None else None,
            'activity_same':a['activity_kind']==b['activity_kind']!='UNKNOWN',
            'setting_same':a['setting_kind']==b['setting_kind']!='UNKNOWN'}


def scenelet_cut(a,b,sim):
    """Adaptive novelty boundary. No fixed segment count or hard 'different place = Chapter'."""
    if a['capture_time_ms'] is not None and b['capture_time_ms'] is not None:
        gap=b['capture_time_ms']-a['capture_time_ms']
        if gap<0:
            return 'UNTRUSTED_OR_OUT_OF_ORDER_CLOCK'
        # Long gaps are candidate scene boundaries, not proof of a new activity.
        if gap>25*60*1000:
            return 'VERIFIED_TIME_GAP'
    if not a['fact_ids'] or not b['fact_ids']:
        return None   # missing evidence never justifies a new independent experience
    if (a['activity_kind']!='UNKNOWN' and b['activity_kind']!='UNKNOWN'
        and a['activity_kind']!=b['activity_kind']
        and sim['lexical']<.37):
        return 'ACTIVITY_AND_VISUAL_NOVELTY'
    if (a['setting_kind']!='UNKNOWN' and b['setting_kind']!='UNKNOWN'
        and a['setting_kind']!=b['setting_kind']
        and sim['lexical']<.12 and (sim['visual'] is None or sim['visual']<.75)):
        return 'SETTING_AND_VISUAL_NOVELTY'
    if sim['visual'] is not None and sim['visual']<.48 and sim['lexical']<.06:
        return 'DISTINCT_VISUAL_SUBJECTS'
    return None


def build_scene_map(assets,facts,observations=(), *, max_scenelets=400):
    """Full-coverage Scenelet segmentation. No truncation or silent omissions."""
    if max_scenelets<1:
        raise ValueError('Invalid scenelet safety limit')
    rows=records(assets,facts,observations)
    groups=[]
    edges=[]
    current=[]
    for row in rows:
        if current:
            previous=current[-1]
            sim=pair_similarity(previous,row)
            reason=scenelet_cut(previous,row,sim)
            edges.append({'left_asset_id':previous['asset_id'],'right_asset_id':row['asset_id'],
                'reason':reason or 'RELATED_OR_UNCERTAIN','similarities':sim,
                'time_basis':'VERIFIED_CAPTURE' if previous['capture_time_ms'] is not None
                    and row['capture_time_ms'] is not None else 'IMPORT_SEQUENCE_ONLY'})
            if reason:
                groups.append(current)
                current=[]
        current.append(row)
    if current:
        groups.append(current)
    if len(groups)>max_scenelets:
        # Do not silently truncate a long day and call it fully covered.
        raise ValueError('SCENELET_CAPACITY_EXCEEDED: use hierarchical chunking')
    scenes=[]
    for segment in groups:
        aids=[r['asset_id'] for r in segment]
        scid='S'+sha256('|'.join(aids).encode()).hexdigest()[:12]
        facts_here=list(dict.fromkeys(fid for r in segment for fid in r['fact_ids']))
        frames=list(dict.fromkeys(fid for r in segment for fid in r['evidence_frame_ids']))
        stamped=[r['capture_time_ms'] for r in segment if r['capture_time_ms'] is not None]
        act=[r['activity_kind'] for r in segment if r['activity_kind']!='UNKNOWN']
        contexts=[r['setting_kind'] for r in segment if r['setting_kind']!='UNKNOWN']
        scenes.append({'scenelet_id':scid,'asset_ids':aids,
            'fact_ids':facts_here,'evidence_frame_ids':frames,
            'source_sequence_start':segment[0]['source_sequence_index'],
            'source_sequence_end':segment[-1]['source_sequence_index'],
            'time_basis':'VERIFIED_CAPTURE' if len(stamped)==len(segment) else 'IMPORT_SEQUENCE_ONLY',
            'capture_start_ms':min(stamped) if len(stamped)==len(segment) else None,
            'capture_end_ms':max(stamped) if len(stamped)==len(segment) else None,
            'activity_kinds':list(dict.fromkeys(act)),
            'setting_kinds':list(dict.fromkeys(contexts)),
            'evidence_asset_count':sum(bool(r['fact_ids']) for r in segment),
            'needs_more_evidence':not facts_here})
    assert len({aid for s in scenes for aid in s['asset_ids']})==len(assets)
    return {'version':SCHEMA,'time_basis':'VERIFIED_CAPTURE' if rows and all(
        r['capture_time_ms'] is not None for r in rows) else 'IMPORT_SEQUENCE_ONLY',
        'asset_count':len(rows),'fact_count':len(facts),'scenelet_count':len(scenes),
        'scenelets':scenes,'boundaries':edges,
        'notice':'Scenelet cut means possible scene change, never a guaranteed independent Chapter or continuous route.'}


def editor_scene_summary(scene_map, *, max_scenelets=120):
    """Bounded model context with full coverage audit; fail visibly if truncated."""
    scenes=scene_map['scenelets']
    if len(scenes)>max_scenelets:
        # Hierarchical map covers every scenelet ID, while reducing the
        # model-facing context size. Chunk references are evidence pointers,
        # not fresh claims or guessed continuous travel segments.
        size=max(1,(len(scenes)+max_scenelets-1)//max_scenelets)
        groups=[]
        for offset in range(0,len(scenes),size):
            chunk=scenes[offset:offset+size]
            groups.append({'chunk_index':len(groups)+1,
                'scenelet_ids':[s['scenelet_id'] for s in chunk],
                'source_sequence_start':chunk[0]['source_sequence_start'],
                'source_sequence_end':chunk[-1]['source_sequence_end'],
                'fact_count':sum(len(s['fact_ids']) for s in chunk),
                'representative_fact_ids':list(dict.fromkeys(
                    x for s in (chunk[0],chunk[len(chunk)//2],chunk[-1])
                    for x in s['fact_ids'][:2])),
                'activity_kinds':list(dict.fromkeys(
                    k for s in chunk for k in s['activity_kinds']))})
        assert len(groups)<=max_scenelets
        return {'status':'HIERARCHICAL_COMPLETE','scenelet_count':len(scenes),
            'time_basis':scene_map['time_basis'],
            'source_asset_count':scene_map['asset_count'],
            'scenelet_groups':groups,'all_scenelet_ids_accounted':True,
            'note':'Full scene map retained in deterministic audit; groups summarize candidate regions, not independent Chapters.'}
    return {'status':'COMPLETE','time_basis':scene_map['time_basis'],
        'source_asset_count':scene_map['asset_count'],
        'scenelets':[{k:v for k,v in s.items() if k in ('scenelet_id','asset_ids',
            'fact_ids','source_sequence_start','source_sequence_end',
            'time_basis','capture_start_ms','capture_end_ms',
            'activity_kinds','setting_kinds','needs_more_evidence')}
            for s in scenes]}
