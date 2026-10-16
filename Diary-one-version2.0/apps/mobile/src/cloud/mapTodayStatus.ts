import type { TodayStatus } from '../model';
import type { X02PreviewResult } from './types';

/** 将 X02 预览结果映射为 Diary Today 横幅态（与 handoff delivery/coverage 对齐）。 */
export function mapTodayStatusFromPreview(
  result: X02PreviewResult,
  opts?: { preservedPriorReady?: boolean },
): TodayStatus {
  const delivery = result.delivery_state ?? '';
  if (delivery === 'PIPELINE_BLOCKED' || delivery.includes('BLOCKED')) {
    // T05 / AI03 — failure must not become Empty Day when prior Ready exists.
    return opts?.preservedPriorReady ? 'READY' : 'PARTIAL';
  }
  if (result.coverage_status === 'PARTIAL_UNRESOLVED') {
    return opts?.preservedPriorReady ? 'READY' : 'PARTIAL';
  }

  const visible = (result.selected_memory_outcomes ?? []).filter(
    (o) => o.visibility_state === 'VISIBLE_PREVIEW',
  );
  const hasPublished =
    result.chapters.some((c) => c.publication_status === 'STAGED_PREVIEW_VALIDATED')
    || result.ahas.some((a) => a.publication_status === 'STAGED_PREVIEW_VALIDATED');

  if (!hasPublished && visible.length === 0) {
    // DIA04 — honest empty / NO_GROUNDED keeps prior Ready when content preserved.
    if (opts?.preservedPriorReady || delivery === 'NO_GROUNDED_MEMORY') {
      return opts?.preservedPriorReady ? 'READY' : 'ZERO_CURATED';
    }
    return 'ZERO_CURATED';
  }
  if (visible.length > 0 && visible.length < (result.selected_memory_outcomes?.length ?? 0)) {
    return 'PARTIAL';
  }
  if (delivery === 'READY_WITH_GROUNDED_COPY_FALLBACK' || delivery === 'READY_WITH_ITEM_BLOCKS') {
    return 'PARTIAL';
  }
  return 'READY';
}
