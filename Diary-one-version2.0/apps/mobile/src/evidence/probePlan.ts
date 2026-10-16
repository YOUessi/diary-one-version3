import type { SemanticRoutingProfile } from './types';

/** ~1 Hz probes plus optional last frame (matches SemanticRoutingProfile defaults). */
export function planProbeTimestampsMs(
  durationMs: number,
  profile: Pick<SemanticRoutingProfile, 'probeStepMs' | 'includeFinalFrame'>,
): number[] {
  const duration = Math.max(1, Math.round(durationMs));
  const requested: number[] = [];
  for (let t = 0; t < duration; t += profile.probeStepMs) {
    requested.push(t);
  }
  if (profile.includeFinalFrame) {
    requested.push(Math.max(0, duration - 1));
  }
  return [...new Set(requested)].sort((a, b) => a - b);
}

export function mapToEvidenceFrameLevel(count: number): 1 | 3 | 5 | 10 {
  if (count <= 1) return 1;
  if (count <= 3) return 3;
  if (count <= 5) return 5;
  return 10;
}
