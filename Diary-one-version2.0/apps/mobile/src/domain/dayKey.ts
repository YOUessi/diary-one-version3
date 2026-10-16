export function diaryTodayKey(): string {
  return dateKeyFromLocalDate(new Date());
}

/** Local calendar day key YYYY-MM-DD (device timezone). */
export function dateKeyFromLocalDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/**
 * IMP02 — prefer earliest known capture time for Diary day attribution.
 * Returns null when no asset has capture metadata (caller must not silently invent).
 */
export function dayKeyFromCaptureTimes(timesMs: Array<number | undefined | null>): string | null {
  const known = timesMs.filter((t): t is number => typeof t === 'number' && Number.isFinite(t) && t > 0);
  if (!known.length) return null;
  const earliest = Math.min(...known);
  return dateKeyFromLocalDate(new Date(earliest));
}
