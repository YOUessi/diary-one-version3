import type { Chapter, SmallMemory } from '../model';
import { rebuildTopicsFromChapters } from './rebuildTopics';

export type ApplyDiaryDayOptions = {
  /**
   * PRD DIA04 / DAT01 — honest empty (NO_GROUNDED) must not wipe prior Ready memories.
   * When true and incoming is empty while prior exists → keep prior, only status updates elsewhere.
   */
  preservePriorIfIncomingEmpty?: boolean;
  /** A picker batch is incremental, never a complete replacement of the day. */
  sourceBatchId?: string;
};

export function mergeDiaryDay(
  state: { chapters: Chapter[]; smallMemoriesByDate: Record<string, SmallMemory[]> },
  dayKey: string,
  incomingChapters: Chapter[],
  smallMemories: SmallMemory[],
  options?: ApplyDiaryDayOptions,
) {
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
      return {
        ...inc,
        ...(options?.sourceBatchId ? { sourceBatchId: options.sourceBatchId } : {}),
        ...(prev ? { yourStory: prev.yourStory, yourStoryRevision: prev.yourStoryRevision } : {}),
      };
    });
    const incomingIds = new Set(incomingChapters.map((c) => c.id));
    // DAT02 T08 — prior notes on replaced ids stay as their own memories (traceable, not rebound).
    const retained = priorSameDay.filter(
      (c) => !incomingIds.has(c.id) && (
        Boolean(c.yourStory?.trim()) ||
        Boolean(options?.sourceBatchId && c.sourceBatchId !== options.sourceBatchId)
      ),
    );
    const allChapters = [...merged, ...retained, ...otherChapters];
    // DAT01 — full day replace when cloud returns any content; if chapters arrive with
    // an empty ahas list, keep prior small memories (omit-field vs intentional wipe).
    const nextSmall = options?.sourceBatchId
      ? [...priorSmall.filter((m) => m.sourceBatchId !== options.sourceBatchId),
          ...smallMemories.map((m) => ({ ...m, sourceBatchId: options.sourceBatchId }))]
          .filter((m, i, arr) => arr.findIndex((v) => v.id === m.id) === i)
      :
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
}
