import type { Chapter, SmallMemory, TodayStatus } from '../model';
import { rebuildTopicsFromChapters } from '../domain/rebuildTopics';
import { useAppStore } from './useAppStore';

export type ApplyDiaryDayOptions = {
  /**
   * PRD DIA04 / DAT01 — honest empty (NO_GROUNDED) must not wipe prior Ready memories.
   * When true and incoming is empty while prior exists → keep prior, only status updates elsewhere.
   */
  preservePriorIfIncomingEmpty?: boolean;
};

/** 将云端/算法返回的当日记忆合并进 store（保留其他日期与用户补记）。 */
export function applyDiaryDayUpdate(
  dayKey: string,
  incomingChapters: Chapter[],
  smallMemories: SmallMemory[],
  options?: ApplyDiaryDayOptions,
) {
  useAppStore.setState((state) => {
    const priorSameDay = state.chapters.filter((c) => c.dateKey === dayKey);
    const priorSmall = state.smallMemoriesByDate[dayKey] ?? [];

    if (
      options?.preservePriorIfIncomingEmpty &&
      incomingChapters.length === 0 &&
      smallMemories.length === 0 &&
      (priorSameDay.length > 0 || priorSmall.length > 0)
    ) {
      // Keep prior day content; topics unchanged.
      return {};
    }

    const otherChapters = state.chapters.filter((c) => c.dateKey !== dayKey);
    // DAT02 — bind Your Story only by stable chapter id; never by title/date proximity.
    const merged = incomingChapters.map((inc) => {
      const prev = priorSameDay.find((c) => c.id === inc.id);
      return prev?.yourStory ? { ...inc, yourStory: prev.yourStory } : inc;
    });
    const incomingIds = new Set(incomingChapters.map((c) => c.id));
    // DAT02 T08 — prior notes on replaced ids stay as their own memories (traceable, not rebound).
    const orphanStories = priorSameDay.filter(
      (c) => Boolean(c.yourStory?.trim()) && !incomingIds.has(c.id),
    );
    const allChapters = [...merged, ...orphanStories, ...otherChapters];
    // DAT01 — full day replace when cloud returns any content; if chapters arrive with
    // an empty ahas list, keep prior small memories (omit-field vs intentional wipe).
    const nextSmall =
      smallMemories.length > 0
        ? smallMemories
        : incomingChapters.length > 0
          ? priorSmall
          : smallMemories;
    return {
      chapters: allChapters,
      smallMemoriesByDate: {
        ...state.smallMemoriesByDate,
        [dayKey]: nextSmall,
      },
      topics: rebuildTopicsFromChapters(allChapters),
    };
  });
}

export function applyTodayStatus(status: TodayStatus) {
  useAppStore.setState({ todayStatus: status });
}
