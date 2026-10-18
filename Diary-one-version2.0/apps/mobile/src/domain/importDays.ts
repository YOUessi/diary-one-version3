import { dateKeyFromLocalDate } from './dayKey';
import type { PickedMedia } from '../pipeline/types';

export function mediaDayKey(item: PickedMedia): string | undefined {
  const explicit = item.captureDayKey;
  if (explicit && /^\d{4}-\d{2}-\d{2}$/.test(explicit) &&
      Number.isFinite(Date.parse(`${explicit}T12:00:00Z`)) &&
      new Date(`${explicit}T12:00:00Z`).toISOString().slice(0, 10) === explicit) return explicit;
  const time = item.creationTimeMs;
  const date = typeof time === 'number' && time > 0 ? new Date(time) : null;
  if (date && Number.isFinite(date.getTime())) return dateKeyFromLocalDate(date);
  const confirmed = item.confirmedDayKey;
  return confirmed && /^\d{4}-\d{2}-\d{2}$/.test(confirmed) &&
    Number.isFinite(Date.parse(`${confirmed}T12:00:00Z`)) &&
    new Date(`${confirmed}T12:00:00Z`).toISOString().slice(0, 10) === confirmed ? confirmed : undefined;
}

/** Unknown dates must carry an explicit user choice before queueing. */
export function groupMediaByDay(items: PickedMedia[], _importDay?: string) {
  const groups = new Map<string, PickedMedia[]>();
  for (const item of items) {
    const day = mediaDayKey(item);
    if (!day) throw new Error('Confirm a date for media without capture metadata before importing.');
    const group = groups.get(day) ?? [];
    group.push(item);
    groups.set(day, group);
  }
  return [...groups.entries()].sort(([a], [b]) => a.localeCompare(b));
}
