"""Traceable global visual memory for a long first-person day.

This is *not* a scene recognizer or a geospatial resolver. It indexes every
actually verified frame fact, prioritizes distinctive sources, and proposes
cross-time lexical co-reference hypotheses for a subsequent independent LLM
editor to decide. Nothing here can manufacture a source frame or say that
two places are certainly identical from their captions alone.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math
import re

from .scenelet_builder import tokens, time_record

VERSION = 'GLOBAL_GROUNDED_VISUAL_MEMORY_V01'
_NAMED = re.compile(r'(?<![a-z])[A-Z][a-z]{2,}(?:[ -]+[A-Z][a-z]{2,}){1,4}')
_QUOTED = re.compile(r'[“「『"]([^”」』"]{2,38})[”」』"]')
_TOO_GENERIC = frozenset({
    '视频','画面','显示','镜头','前景','背景','一名','一段','有人','附近','远处',
    '可以','看到','可见','街道','建筑','植物','路边','一处','多名','经过',
    'the','with','this','that','street','people','frame','visible',
    'area','view','scene','looking','building','person','road',
})


def named_mentions(text):
    """Only literal named/quoted spans; no invented geographic entity."""
    text=str(text or '')
    result={a.strip().casefold() for a in _QUOTED.findall(text)}
    result.update(a.strip().casefold() for a in _NAMED.findall(text))
    return sorted(v for v in result if len(v)>=3 and v not in _TOO_GENERIC)


def build(assets, facts, observations=(), *, max_protected=48, max_threads=18):
    """Produce complete index + compact source-backed editor context.

    Both asset and fact IDs are canonical; source-index values are used only
    for relative order. Capture gaps are never guessed from imported order.
    """
    if max_protected<1 or max_threads<0:
        raise ValueError('Invalid global visual memory limits')
    source_by_asset={a.get('asset_id'):o for a,o in (
        (asset, observation) for asset in assets.values()
        for observation in observations or ()
        if isinstance(observation,dict)
        and observation.get('source_asset_id')==asset.get('asset_id'))}
    frequency=Counter()
    for f in facts.values():
        if f.get('visual_reviewed') and f.get('asset_id') in assets:
            frequency.update(tokens(f.get('text','')))
    n=sum(f.get('visual_reviewed') and f.get('asset_id') in assets
          for f in facts.values())
    by_source=defaultdict(list)
    all_facts=[]
    for fid,fact in facts.items():
        aid=fact.get('asset_id')
        if aid not in assets or fact.get('visual_reviewed') is not True:
            continue
        asset=assets[aid]
        frameids={f.get('frame_id') for f in asset.get('frames',[])}
        evidence=[id for id in fact.get('evidence_frame_ids',[]) if id in frameids]
        if not evidence:
            continue
        text=str(fact.get('text') or '')
        tt=tokens(text)
        rarity=sum(max(0.,math.log((n+1)/(frequency[token]+1)))
                   for token in tt if token not in _TOO_GENERIC)/max(1,math.sqrt(len(tt)))
        names=named_mentions(text)
        obs=source_by_asset.get(asset.get('asset_id'),{})
        event={'HIGH':2.,'MEDIUM':.7}.get(obs.get('event_salience'),0.)
        strong=1. if fact.get('support_grade')=='STRONG' else .3
        score=round(rarity+1.25*min(3,len(names))+event+strong,4)
        row={'fact_id':fid,'asset_id':aid,'source_asset_id':asset.get('asset_id'),
             'source_index':asset['sequence_index'],
             'evidence_frame_ids':evidence,'text':text,
             'named_mentions':names,'subject_tokens':sorted(tt),
             'evidence_priority_score':score}
        all_facts.append(row);by_source[aid].append(row)
    all_facts.sort(key=lambda x:(x['source_index'],x['fact_id']))
    # Source-asset registry retained for coverage/audit, including evidence-
    # empty assets, but a frame with no verified fact cannot be an anchor.
    source_index=[{'asset_id':aid,'source_asset_id':asset['asset_id'],
         'source_index':asset['sequence_index'],
         'time_record':time_record(asset),
         'fact_ids':[r['fact_id'] for r in by_source.get(aid,[])],
         'named_mentions':sorted(set().union(*(
             set(r['named_mentions']) for r in by_source.get(aid,[]))))}
        for aid,asset in sorted(assets.items(),key=lambda x:x[1]['sequence_index'])]
    used=set()
    priority=[]
    # Guarantee representatives from different parts of the source day
    # before allowing rare local labels to dominate the entire list.
    count=min(max_protected,len(all_facts))
    if count:
        sequence=sorted(all_facts,key=lambda x:x['source_index'])
        slots=sorted({round(i*(len(sequence)-1)/max(1,count-1))
                      for i in range(count)})
        for i in slots:
            item=sequence[i]
            if item['fact_id'] not in used:
                priority.append(item);used.add(item['fact_id'])
    # Then replace a low-quality time anchor with a more distinctive real
    # fact from the same broad region of the day.
    if priority:
        ordered=sorted(all_facts,key=lambda x:(-x['evidence_priority_score'],x['source_index']))
        top=ordered[:max_protected]
        # Preserve 50% distributed temporal anchors, 50% high-value facts.
        slots=max(1,min(len(priority),max_protected//2))
        spread_idx=sorted({round(k*(len(priority)-1)/max(1,slots-1))
                           for k in range(slots)})
        distributed=[priority[k] for k in spread_idx]
        used={x['fact_id'] for x in distributed}
        priority=distributed.copy()
        for x in top:
            if len(priority)>=max_protected:break
            if x['fact_id'] not in used:
                priority.append(x);used.add(x['fact_id'])
    # Lexical threads are candidates, NOT verified entity identity.
    named_sources=defaultdict(list)
    for row in all_facts:
        for mention in row['named_mentions']:
            named_sources[mention].append(row)
    threads=[]
    for term,refs in named_sources.items():
        ids=list(dict.fromkeys(x['source_index'] for x in refs))
        if len(ids)<2 or max(ids)-min(ids)<4:
            continue
        facts_seen=list(dict.fromkeys(x['fact_id'] for x in refs))
        threads.append({'literal_mention':term,'source_indices':sorted(ids),
            'candidate_fact_ids':facts_seen[:10],
            'relation_status':'POSSIBLE_CROSS_TIME_COREFERENCE_NOT_VERIFIED'})
    # Chinese descriptions often repeat the same concrete object phrase
    # rather than identical Latin proper names. Short Chinese bigrams also
    # match generic wording and produced false candidate identities (e.g.
    # "视频显示/画面有..."). Require a literal contiguous meaningful
    # >=4-character phrase in multiple independently verified facts.
    # Still only a co-reference *candidate*, never identity proof.
    generic_parts=('画面','视频','镜头','背景','前景','可见','显示',
                   '视角','其中','拍摄','包括','出现','一名','一条',
                   '处于','可以','以及','一段','比较','一个','这里')
    chinese=re.compile(r'[\u3400-\u9fff]{4,}')
    phrase_refs=defaultdict(list)
    for fact in all_facts:
        seen=set()
        for matched in chinese.findall(fact['text']):
            for length in range(4,min(8,len(matched))+1):
                for start in range(len(matched)-length+1):
                    phrase=matched[start:start+length]
                    if phrase in seen or any(part in phrase for part in generic_parts):
                        continue
                    if any(ch in phrase for ch in ('的','了','着','在','是','有')):
                        continue
                    seen.add(phrase)
                    phrase_refs[phrase].append(fact)
    lexical=[]
    for phrase,rows in phrase_refs.items():
        indexes=sorted(set(v['source_index'] for v in rows))
        if len(indexes)<2 or max(indexes)-min(indexes)<8:
            continue
        if len(indexes)>max(3,int(len(assets)*.15)):
            continue
        distinct=list(dict.fromkeys(r['fact_id'] for r in rows))
        lexical.append({'literal_mention':phrase,'source_indices':indexes,
            'candidate_fact_ids':distinct[:12],
            'relation_status':'POSSIBLE_CROSS_TIME_LITERAL_PHRASE_NOT_VERIFIED'})
    lexical.sort(key=lambda x:(-len(x['literal_mention']),
                               -(max(x['source_indices'])-min(x['source_indices']))))
    threads.sort(key=lambda x:(-(max(x['source_indices'])-min(x['source_indices'])),
                               -len(x['source_indices']),x['literal_mention']))
    threads=threads[:max_threads]
    for candidate in lexical:
        if len(threads)>=max_threads:break
        if any(candidate['literal_mention'] in t['literal_mention']
               or t['literal_mention'] in candidate['literal_mention']
               for t in threads):
            continue
        threads.append(candidate)
    summary={'version':VERSION,'source_count':len(source_index),
        'verified_fact_count':len(all_facts),
        'all_evidence_fact_ids':[x['fact_id'] for x in all_facts],
        'priority_anchors':[{'fact_id':x['fact_id'],'source_index':x['source_index'],
            'frame_id':x['evidence_frame_ids'][0],
            'text':x['text'][:180],'score_heuristic_not_quality':x['evidence_priority_score']}
            for x in priority],
        'cross_time_entity_candidates':threads,
        'source_index':source_index,
        'time_basis':'VERIFIED_PER_ASSET_OR_IMPORT_SEQUENCE_ONLY',
        'identity_proof':'NO_ENTITY_MATCH_IS_AUTO_CERTIFIED',
        'policy':'PRESERVE_FACT_IDS_AND_SOURCE_FRAME_REFERENCES; MODEL_MUST_VERIFY_THEMATIC_FUSION'}
    return summary


def editor_context(memory, *, max_anchors=42):
    """Safe bounded context for model prompts without losing full audit."""
    return {'version':memory['version'],
      'source_count':memory['source_count'],
      'verified_fact_count':memory['verified_fact_count'],
      'priority_anchors':memory['priority_anchors'][:max_anchors],
      'cross_time_entity_candidates':memory['cross_time_entity_candidates'],
      'scope_note':'Cross-time entity matches are uncertain textual candidates; never assert identity solely from shared words.',
      'time_basis':memory['time_basis']}
