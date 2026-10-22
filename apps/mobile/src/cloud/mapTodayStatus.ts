import type { TodayStatus } from '../model';
import type { X02PreviewResult } from './types';
import { summarizeDelivery } from './summarizeDelivery';

/** Use the same delivery classification as the persisted task summary. */
export function mapTodayStatusFromPreview(
  result: X02PreviewResult,
  opts?: { preservedPriorReady?: boolean },
): TodayStatus {
  const summary = summarizeDelivery(result);
  if (summary.outcome === 'partial') return 'PARTIAL';
  if (summary.outcome === 'saved' || (result.selected_memory_outcomes ?? []).some(
    (outcome) => outcome.visibility_state === 'VISIBLE_PREVIEW',
  )) return 'READY';
  return opts?.preservedPriorReady ? 'READY' : 'ZERO_CURATED';
}
