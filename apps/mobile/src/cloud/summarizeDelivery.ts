import type { X02PreviewResult } from './types';
import type { PipelineDeliverySummary } from '../pipeline/types';

/** Call after contract validation. Never infer completeness from HTTP success. */
export function summarizeDelivery(result: X02PreviewResult): PipelineDeliverySummary {
  const savedMemoryCount = [...(result.chapters ?? []), ...(result.ahas ?? [])]
    .filter((memory) => memory.publication_status === 'STAGED_PREVIEW_VALIDATED').length;
  const delivery = result.delivery_state ?? '';
  const reason: PipelineDeliverySummary['reason'] =
    result.coverage_status === 'PARTIAL_UNRESOLVED' ? 'UNRESOLVED_EVIDENCE'
      : delivery === 'READY_WITH_ITEM_BLOCKS' || delivery.includes('BLOCKED')
        || (result.selected_memory_outcomes ?? []).some((memory) => memory.visibility_state === 'DIAGNOSTIC_ONLY')
        ? 'ITEMS_WITHHELD'
        : delivery === 'READY_WITH_GROUNDED_COPY_FALLBACK' ? 'COPY_FALLBACK' : undefined;
  return { outcome: reason ? 'partial' : savedMemoryCount ? 'saved' : 'empty',
    savedMemoryCount, ...(reason ? { reason } : {}) };
}
