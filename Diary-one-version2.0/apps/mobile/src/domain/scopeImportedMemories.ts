import type { Chapter, SmallMemory } from '../model';

/** Cloud ids are only guaranteed within a revision, never across picker batches/days. */
export function scopeImportedMemories(batchId: string, chapters: Chapter[], small: SmallMemory[]) {
  const scope = (id: string) => `${batchId}:${id}`;
  return {
    chapters: chapters.map((chapter) => ({ ...chapter, id: scope(chapter.id),
      moments: chapter.moments.map((moment) => ({ ...moment, id: scope(moment.id) })) })),
    smallMemories: small.map((memory) => ({ ...memory, id: scope(memory.id) })),
  };
}
