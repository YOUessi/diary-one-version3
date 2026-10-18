/** DayRevision identity for a single cloud-processing submission (handoff DAT01 / REL01). */

/**
 * Stable id for the same owner + day + selection so BFF idempotency can reuse the job
 * without cross-account 409 when the next tester picks the same Demo assets.
 */
export function createStableDayRevisionId(
  dayKey: string,
  selectionFingerprint: string,
  ownerSalt?: string,
): string {
  const fp = selectionFingerprint.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 40) || 'empty';
  const owner = (ownerSalt ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9@._-]/g, '')
    .slice(0, 24);
  const ownerPart = owner ? `_${simpleSalt(owner)}` : '';
  return `dayrev_${dayKey}_${fp}${ownerPart}`;
}

function simpleSalt(s: string): string {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return (h >>> 0).toString(36);
}

/** Unique id when fingerprint is unavailable (should be rare). */
export function createDayRevisionId(dayKey: string): string {
  const stamp = Date.now();
  const rand = Math.random().toString(36).slice(2, 8);
  return `dayrev_${dayKey}_${stamp}_${rand}`;
}

/** Cheap fingerprint of selected assets for retry / idempotency (not a crypto hash). */
export function selectionFingerprint(items: { uri: string; fileSize?: number; durationMs?: number }[]): string {
  const parts = items
    .map((i) => `${i.uri.split('/').pop() ?? i.uri}:${i.fileSize ?? 0}:${i.durationMs ?? 0}`)
    .sort();
  let h = 0;
  const s = parts.join('|');
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return `s${(h >>> 0).toString(36)}`;
}
