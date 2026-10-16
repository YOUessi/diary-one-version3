/**
 * Mirror of services/bff/shared/result_admit.py — App-side DAT01 / AI03 gate.
 * Keep in sync when BFF allowlist changes.
 */

export const READY_DELIVERY_STATES = new Set([
  'READY_PRIMARY_COPY',
  'READY_WITH_GROUNDED_COPY_FALLBACK',
  'READY_WITH_ITEM_BLOCKS',
  'STAGED_PREVIEW_DELIVERED',
]);

export type AdmitDecision = {
  admit: boolean;
  reason: string;
  /** Honest empty day — keep prior memories; do not wipe. */
  honestEmpty: boolean;
};

export function admitDeliveryState(
  delivery: string | undefined | null,
  opts?: { isMock?: boolean; allowMock?: boolean },
): AdmitDecision {
  const d = (delivery ?? '').trim();
  const isMock = Boolean(opts?.isMock);
  const allowMock = Boolean(opts?.allowMock);

  if (isMock && !allowMock) {
    return { admit: false, reason: 'mock_disallowed', honestEmpty: false };
  }
  if (d === 'PIPELINE_BLOCKED') {
    return { admit: false, reason: 'pipeline_blocked', honestEmpty: false };
  }
  if (d === 'NO_GROUNDED_MEMORY') {
    return { admit: true, reason: 'no_grounded_memory', honestEmpty: true };
  }
  if (d && !READY_DELIVERY_STATES.has(d)) {
    return { admit: false, reason: `unsupported_delivery:${d}`, honestEmpty: false };
  }
  if (!d && !isMock) {
    return { admit: false, reason: 'missing_delivery_state', honestEmpty: false };
  }
  return { admit: true, reason: 'ok', honestEmpty: false };
}
