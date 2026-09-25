import type { X02PreviewResult } from './types';
import { ALGORITHM_LOCK } from '../config/algorithmLock';

export type ValidateOutcome =
  | { ok: true }
  | { ok: false; reason: string };

/** fail-closed：与 eval-web 消费侧一致的最小合同门槛。 */
export function validatePreviewResult(result: X02PreviewResult): ValidateOutcome {
  if (result.schema_version !== ALGORITHM_LOCK.previewSchema) {
    return { ok: false, reason: `Unexpected schema_version: ${result.schema_version}` };
  }
  if (!Array.isArray(result.chapters) || !Array.isArray(result.ahas)) {
    return { ok: false, reason: 'Missing chapters or ahas array' };
  }
  if (!Array.isArray(result.selected_memory_outcomes)) {
    return { ok: false, reason: 'Missing selected_memory_outcomes' };
  }

  for (const ch of result.chapters) {
    if (!ch.id || !ch.title || typeof ch.story !== 'string') {
      return { ok: false, reason: 'Invalid chapter shape' };
    }
    if (ch.publication_status === 'STAGED_PREVIEW_VALIDATED') {
      const outcome = result.selected_memory_outcomes.find(
        (o) => o.memory_type === 'CHAPTER' && o.memory_id === ch.id,
      );
      if (!outcome) {
        return { ok: false, reason: `Chapter ${ch.id} missing outcome` };
      }
    }
  }

  for (const a of result.ahas) {
    if (!a.id || typeof a.story !== 'string') {
      return { ok: false, reason: 'Invalid aha shape' };
    }
    if (a.publication_status === 'STAGED_PREVIEW_VALIDATED') {
      const outcome = result.selected_memory_outcomes.find(
        (o) => o.memory_type === 'AHA' && o.memory_id === a.id,
      );
      if (!outcome) {
        return { ok: false, reason: `Aha ${a.id} missing outcome` };
      }
    }
  }

  if (result.delivery_state === 'PIPELINE_BLOCKED') {
    return { ok: false, reason: `Pipeline blocked: ${result.delivery_state}` };
  }

  const visibleOutcomes = result.selected_memory_outcomes.filter(
    (o) => o.visibility_state === 'VISIBLE_PREVIEW',
  );
  const stagedChapters = result.chapters.filter(
    (c) => c.publication_status === 'STAGED_PREVIEW_VALIDATED',
  );
  if (stagedChapters.length > 0 && visibleOutcomes.length === 0) {
    return { ok: false, reason: 'Staged chapters without VISIBLE_PREVIEW outcomes' };
  }

  return { ok: true };
}
