import type { EvidenceFrameLevel, SemanticRouteDecision } from './types';

/** Pick representative timestamps for the routed frame ladder. */
export function selectFrameTimestampsMs(decision: SemanticRouteDecision): number[] {
  const key = String(decision.targetFrameCount);
  const fromLadder = decision.recommendedAnchorMs[key];
  if (fromLadder?.length) {
    return fromLadder.slice(0, decision.targetFrameCount);
  }
  return decision.selectedTimestampsMs.slice(0, decision.targetFrameCount);
}

export function sampleRoleForIndex(
  index: number,
  total: number,
): 'WINDOW_EARLY' | 'WINDOW_MIDDLE' | 'WINDOW_LATE' {
  if (total <= 1) return 'WINDOW_MIDDLE';
  const ratio = index / (total - 1);
  if (ratio <= 0.34) return 'WINDOW_EARLY';
  if (ratio >= 0.66) return 'WINDOW_LATE';
  return 'WINDOW_MIDDLE';
}

export function canonicalOffsetForRole(
  role: 'WINDOW_EARLY' | 'WINDOW_MIDDLE' | 'WINDOW_LATE',
): 1500 | 4500 | 7500 {
  if (role === 'WINDOW_EARLY') return 1500;
  if (role === 'WINDOW_LATE') return 7500;
  return 4500;
}

export function frameLevelLabel(level: EvidenceFrameLevel): string {
  return `SEMANTIC_FRAME_${level}`;
}
