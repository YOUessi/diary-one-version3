import type { Chapter, Topic } from '../model';

/** 从已发布记忆标签归纳 Topics；信号不足时返回空（整块隐藏）。 */
export function rebuildTopicsFromChapters(chapters: Chapter[]): Topic[] {
  const byTag = new Map<string, Set<string>>();
  for (const ch of chapters) {
    for (const tag of ch.tags) {
      const set = byTag.get(tag) ?? new Set<string>();
      set.add(ch.id);
      byTag.set(tag, set);
    }
  }

  const topics: Topic[] = [];
  for (const [name, ids] of byTag.entries()) {
    if (ids.size < 2) continue;
    topics.push({
      id: `topic-${name.toLowerCase().replace(/\s+/g, '-')}`,
      name,
      chapterIds: [...ids],
    });
  }
  return topics.sort((a, b) => b.chapterIds.length - a.chapterIds.length);
}
