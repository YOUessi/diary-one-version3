"""Bounded, image-grounded repair after a moment's final copy is rejected."""
from copy import deepcopy
from itertools import product
from tempfile import TemporaryDirectory
import re

from jsonschema import Draft202012Validator

PROMPT = '''这是一次有限候选选择，不是重新创作文案。只处理这一条小记忆/高光中被拒绝的文字。
实际附图是同一条记忆已经审核选定的锚点，不能借用章节或其他素材。原文、旧观察和拒绝理由都不是新事实。
candidate_copies由程序从原文截取，未经过真实性认定。只能选择其中一条，不能输出或编辑文字、引用、选图。
逐字核对候选的主体、外形、动作、修饰和关系是否都能在附图中直接看见；短句也不能凭常识猜，不能把姿态解释成休息、等待或欣赏。
选择画面直接支持、通顺且保留核心的候选；不为完整句式或生动文笔补词。若全部不成立、不确定、断章取义或不值得保留，返回{"choice_id":null}。
withdrawn_relations只是已被否定的关系约束，不是可发布的替代事实。protected_fields为已有精确图像审核的原文，程序保持不变。
只能返回{"choice_id":"候选编号"}或{"choice_id":null}，不附加文字、解释、supported或decision。选择不代表通过，另一个独立请求会只看同样的实际图像核验。
'''


_QUALIFIERS = re.compile(r'不确定|不能确认|未能确认|没有|并非|不是|疑似|似乎|可能|或许|大概|也许|仿佛|好像|看不清|不|未|没|无')


def validate_reduction(original, candidate, relations=()):
    """An exact contiguous reduction, never a new assertion or a truth proof."""
    source = original.strip().rstrip('。.')
    kept = candidate.strip().rstrip('。.')
    if not kept or kept == source or kept not in source:
        raise ValueError('Rejected copy must shrink to one exact original span without new words')
    if _QUALIFIERS.findall(source) != _QUALIFIERS.findall(kept):
        raise ValueError('Reduction must not erase negation or uncertainty')
    for relation in relations:
        subject = relation['subject']
        if subject in source and subject not in kept:
            raise ValueError('Reduction must preserve the complete original relation subject')
        if relation['reference'] in kept:
            raise ValueError('Repaired copy still contains a withdrawn relation reference')
    return {'source': original, 'retained': candidate, 'rule': 'SINGLE_EXACT_ORIGINAL_SPAN_NO_NEW_WORDS'}


def withdrawn_relations(packet, memory_id):
    """Return negative editing constraints, never alternative visual facts."""
    result = []
    for batch in packet.get('final_verification_batches', []):
        claims = {c['claim_id']: c for c in batch.get('input', {}).get('claims', [])
                  if c['memory_id'] == memory_id}
        spatial = batch.get('spatial_verification') or {}
        rejected = {r['target_id'] for r in spatial.get('compiled_observations', [])
                    if r.get('supported') is False}
        for target in spatial.get('relation_targets', []):
            claim = claims.get(target['claim_id'])
            if claim and target['target_id'] in rejected:
                result.append({k: target[k] for k in ('subject', 'reference', 'source_quote')})
    return result


def reduction_choices(original, relations, *, max_length, approved_text=()):
    """Bounded literal spans only; no synonym generation or inferred visual facts."""
    source = original.strip().rstrip('。.')
    spans = re.split(r'[，。！？；,.!?;]', source)
    spans.extend(approved_text)
    for relation in relations:
        subject = relation['subject']
        if not subject:
            continue
        for match in re.finditer(re.escape(subject), source):
            spans.extend((subject, source[:match.end()]))
    valid = set()
    for span in spans:
        span = span.strip().rstrip('。.')
        if len(span) > max_length:
            continue
        try:
            validate_reduction(original, span, relations)
        except ValueError:
            continue
        valid.add(span)
    return sorted(valid, key=lambda span: (-len(span), span))[:4]


def candidate_copies(draft, title_ok, body_ok, relations):
    sentence = draft['sentences'][0]
    titles = [draft['title']] if title_ok else reduction_choices(
        draft['title'], relations, max_length=16,
        approved_text=[sentence['text']] if body_ok else [])
    bodies = [sentence['text']] if body_ok else [span + '。' for span in reduction_choices(
        sentence['text'], relations, max_length=27,
        approved_text=[draft['title']] if title_ok else [])]
    result = []
    for title, body in product(titles, bodies):
        copy = {k: deepcopy(draft[k]) for k in ('id', 'title', 'title_fact_ids', 'sentences')}
        copy['title'] = title
        copy['sentences'][0]['text'] = body
        result.append({'choice_id': f'R{len(result) + 1:02d}', 'copy': copy})
    return result


def repair_final_moments(packet, items, stage, *, ask, time_basis, stage_runs,
                         evidence=(), evidence_scope=None):
    from . import product_editor as p, final_copy_evidence, final_copy_images, x02

    if packet.get('final_verification_terminal_failure'):
        return
    allowed = {m['id'] for m in items if m['kind'] in ('AHA', 'HIGHLIGHT')}
    verdicts = {r['id']: r for r in packet.get('final_verification_output', {}).get('items', [])}
    attempted = packet.setdefault('final_moment_repair_attempted_ids', [])
    for memory in packet.get('_final_verification_memories', []):
        mid = memory['id']
        verdict = verdicts.get(mid)
        if (mid not in allowed or mid in attempted or mid in packet['reviewed'] or not verdict
                or not memory.get('copy_evidence_scope', '').startswith('IMAGE_REVIEWED_MOMENT_ANCHOR_ONLY')):
            continue
        attempted.append(mid)
        record = {'id': mid, 'stage': stage + '_' + mid, 'status': 'BLOCKED',
                  'original': deepcopy(memory['draft']), 'original_verdict': deepcopy(verdict),
                  'raw_output': None}
        packet.setdefault('final_moment_repair_ledger', []).append(record)
        try:
            draft = memory['draft']
            if len(draft['sentences']) != 1 or len(verdict['sentences']) != 1:
                raise ValueError('Moment repair requires exactly one scoped sentence')
            sentence = draft['sentences'][0]
            check = verdict['sentences'][0]
            if check['source_index'] != sentence['source_index']:
                raise ValueError('Moment sentence verdict has a different source index')
            title_ok, body_ok = verdict['title_supported'], check['supported']
            if type(title_ok) is not bool or type(body_ok) is not bool or (title_ok and body_ok):
                raise ValueError('No explicit local copy rejection to repair')
            # Reconstruct the same exact claims/frames as the original final check.
            _, context = p.final_copy_verification_items([memory], {mid: draft})
            plan = final_copy_evidence.build_final_claim_batches(context, evidence, evidence_scope)
            if not plan['claims'] or any(not c.get('batch_id') for c in plan['claims']):
                raise ValueError('Repair has no complete input-bound anchor images')
            protected = [c for c in plan['claims']
                         if title_ok and c['field'] == 'TITLE' or body_ok and c['field'] == 'SENTENCE']
            if any(p.approved_claim_key(c, evidence) not in packet.get('_approved_exact_claims', {})
                   for c in protected):
                raise ValueError('Protected copy lacks unchanged image-bound approval')
            refs = {(r['source_asset_id'], r['frame_id']) for c in plan['claims'] for r in c['frame_refs']}
            bound = [entry for entry in evidence if (entry[0]['asset_id'], entry[1]['frame_id']) in refs]
            relations = withdrawn_relations(packet, mid)
            choices = candidate_copies(draft, title_ok, body_ok, relations)
            record['withdrawn_relations'] = deepcopy(relations)
            record['candidate_copies'] = deepcopy(choices)
            if not choices:
                record['reason'] = 'NO_EXTRACTIVE_CANDIDATE'
                continue
            schema = p.obj({'choice_id': {'enum': [None] + [c['choice_id'] for c in choices]}})
            request = {'id': mid, 'kind': memory['kind'], 'locale': 'zh-Hans', 'time_basis': time_basis,
                       'rejected_copy': {k: deepcopy(draft[k]) for k in ('title', 'title_fact_ids', 'sentences')},
                       'rejection': deepcopy(verdict), 'frame_refs': [dict(source_asset_id=a, frame_id=f) for a, f in sorted(refs)],
                       'protected_fields': (['title'] if title_ok else []) + (['sentences'] if body_ok else []),
                       'repair_mode': 'EXTRACTIVE_CANDIDATE_SELECTION_NO_FREE_TEXT',
                       'candidate_copies': choices, 'withdrawn_relations': relations}
            with TemporaryDirectory(prefix='diary-moment-repair-') as directory:
                attached, audit = final_copy_images.prepare_final_copy_images(
                    bound, directory, bundle_root=(evidence_scope or {}).get('bundle_root'))
                record['image_transform_audit'] = audit
                record['raw_output'] = ask(stage + '_' + mid, PROMPT, schema, request, evidence=attached)
            response = record['raw_output']
            if next(Draft202012Validator(schema).iter_errors(response), None):
                raise ValueError('Moment repair must select a supplied choice_id without any free text')
            choice_id = response['choice_id']
            if choice_id is None:
                record['reason'] = 'NO_GROUNDED_CORE_RETAINED'
                continue
            record['selected_choice_id'] = choice_id
            response = deepcopy(next(c['copy'] for c in choices if c['choice_id'] == choice_id))
            record['reduction_checks'] = []
            for field, old, new, passed in [
                ('title', draft['title'], response['title'], title_ok),
                ('sentence', sentence['text'], response['sentences'][0]['text'], body_ok),
            ]:
                if not passed:
                    record['reduction_checks'].append({'field': field, **validate_reduction(
                        old, new, request['withdrawn_relations'])})
            candidate = {**response, 'decision': 'PUBLISH', 'reason': 'Pending independent image verdict'}
            compiled, _ = p.compile_copy({'items': [candidate]}, [memory], review=True)
            if mid not in compiled:
                raise ValueError('Moment repair failed deterministic copy validation')
            child = {'reviewed': compiled, '_approved_exact_claims': deepcopy(packet.get('_approved_exact_claims', {}))}
            p.verify_final_chapter_copy(child, [memory], stage + '_VERIFY_' + mid, ask=ask,
                time_basis=time_basis, stage_runs=stage_runs, evidence=evidence, evidence_scope=evidence_scope,
                reuse_verified=True)
            record['verification'] = {k: deepcopy(child.get(k)) for k in
                ('final_verification_input', 'final_verification_output', 'final_verification_batches', 'final_verification_ledger', 'final_verification_relation_conflicts')}
            if child.get('final_verification_terminal_failure'):
                packet['final_verification_terminal_failure'] = True
            if mid in child['reviewed']:
                packet['reviewed'][mid] = child['reviewed'][mid]
                packet.setdefault('_approved_exact_claims', {}).update(child.get('_approved_exact_claims', {}))
                record['status'] = 'ACCEPTED_AFTER_INDEPENDENT_MOMENT_IMAGE_VERIFICATION'
            else:
                record['reason'] = 'Repaired moment did not pass independent image verification'
        except (KeyError, TypeError, ValueError, OSError, x02.X02Error) as exc:
            record.update(reason=str(exc) if isinstance(exc, ValueError) else type(exc).__name__,
                          error_type=type(exc).__name__)
            if p.final_provider_failure_is_terminal(exc):
                packet['final_verification_terminal_failure'] = True
            if isinstance(exc, x02.X02StageCallError) and all(run is not exc.stage_run for run in stage_runs):
                stage_runs.append(exc.stage_run)
        if packet.get('final_verification_terminal_failure'):
            break
