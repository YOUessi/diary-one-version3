import type { Chapter, SmallMemory, TodayStatus } from '../model';
import { mergeDiaryDay, type ApplyDiaryDayOptions } from '../domain/mergeDiaryDay';
import { useAppStore } from './useAppStore';

/** Full day revisions replace the day; explicitly tagged picker batches merge incrementally. */
export function applyDiaryDayUpdate(dayKey: string, incomingChapters: Chapter[],
  smallMemories: SmallMemory[], options?: ApplyDiaryDayOptions) {
  useAppStore.setState((state) => mergeDiaryDay(state, dayKey, incomingChapters, smallMemories, options));
}

export function applyTodayStatus(todayStatus: TodayStatus) {
  useAppStore.setState({ todayStatus });
}
