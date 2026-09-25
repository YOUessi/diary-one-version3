import type { Chapter, SmallMemory, TodayStatus } from '../model';
import { rebuildTopicsFromChapters } from '../domain/rebuildTopics';
import { useAppStore } from './useAppStore';

/** 将云端/算法返回的当日记忆合并进 store（保留其他日期与用户补记）。 */
export function applyDiaryDayUpdate(
  dayKey: string,
  incomingChapters: Chapter[],
  smallMemories: SmallMemory[],
) {
  useAppStore.setState((state) => {
    const otherChapters = state.chapters.filter((c) => c.dateKey !== dayKey);
    const merged = incomingChapters.map((inc) => {
      const prev = state.chapters.find((c) => c.id === inc.id);
      return prev?.yourStory ? { ...inc, yourStory: prev.yourStory } : inc;
    });
    const allChapters = [...merged, ...otherChapters];
    return {
      chapters: allChapters,
      smallMemoriesByDate: {
        ...state.smallMemoriesByDate,
        [dayKey]: smallMemories,
      },
      topics: rebuildTopicsFromChapters(allChapters),
    };
  });
}

export function applyTodayStatus(status: TodayStatus) {
  useAppStore.setState({ todayStatus: status });
}
