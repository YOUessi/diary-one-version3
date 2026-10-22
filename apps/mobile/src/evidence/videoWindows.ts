/** Keep all windows <=10s without a final, sub-frame-sized remainder. */
export function balancedVideoWindows(durationMs: number): { startMs: number; endMs: number }[] {
  if (!Number.isInteger(durationMs) || durationMs < 1 || durationMs > 120_000) {
    throw new Error('Invalid video duration');
  }
  const count = Math.ceil(durationMs / 10_000);
  return Array.from({ length: count }, (_, i) => ({
    startMs: Math.floor(i * durationMs / count),
    endMs: Math.floor((i + 1) * durationMs / count),
  }));
}

export const BALANCED_V07_SAMPLING_PROFILE = 'MOBILECLIP_S0_FP16_COVERAGE_V07_BALANCED_V1';
