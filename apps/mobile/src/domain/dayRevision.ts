/** DayRevision identity for a single cloud-processing submission (handoff DAT01). */
export function createDayRevisionId(dayKey: string): string {
  const stamp = Date.now();
  const rand = Math.random().toString(36).slice(2, 8);
  return `dayrev_${dayKey}_${stamp}_${rand}`;
}
