import type { TodayStatus } from '../model';
import { diaryTodayKey } from './dayKey';

/** Figma Daily Recap / Readiness Changed — today not ready while recordings prepare. */
export function isDailyRecapBlockedForDate(dateKey: string, todayStatus: TodayStatus): boolean {
  if (dateKey !== diaryTodayKey()) return false;
  return todayStatus === 'PREPARING' || todayStatus === 'READY_PREPARING';
}
