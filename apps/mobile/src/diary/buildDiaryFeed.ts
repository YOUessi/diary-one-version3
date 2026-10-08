import type { Chapter, SmallMemory } from '../model';

export type DiaryFeedItem =
  | { kind: 'day_header'; label: string; sub?: string }
  | { kind: 'chapter'; chapter: Chapter }
  | { kind: 'small'; memory: SmallMemory };

function shortDay(dateKey: string): string {
  const [y, m, d] = dateKey.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function dayHeaderLabel(dateKey: string, todayKey: string): { label: string; sub?: string } {
  const sub = shortDay(dateKey);
  if (dateKey === todayKey) return { label: 'Today', sub };
  if (dateKey === offsetDay(todayKey, -1)) return { label: 'Yesterday', sub };
  const [y, m, d] = dateKey.split('-').map(Number);
  const weekday = new Date(y, m - 1, d).toLocaleDateString('en-US', { weekday: 'long' });
  return { label: weekday, sub };
}

function offsetDay(key: string, delta: number): string {
  const [y, m, d] = key.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + delta);
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
}

export function buildDayFeed(
  dateKey: string,
  todayKey: string,
  chapters: Chapter[],
  smallMemories: SmallMemory[],
): DiaryFeedItem[] {
  const items: DiaryFeedItem[] = [];
  const header = dayHeaderLabel(dateKey, todayKey);
  items.push({ kind: 'day_header', label: header.label, sub: header.sub });

  const dayChapters = chapters.filter((c) => c.dateKey === dateKey);
  for (const ch of dayChapters) {
    items.push({ kind: 'chapter', chapter: ch });
  }
  for (const sm of smallMemories) {
    items.push({ kind: 'small', memory: sm });
  }
  return items;
}

export function buildEarlierFeed(
  chapters: Chapter[],
  todayKey: string,
  limit: number,
): { dateKey: string; items: DiaryFeedItem[] }[] {
  const keys = [...new Set(chapters.map((c) => c.dateKey).filter((k) => k !== todayKey))]
    .sort((a, b) => b.localeCompare(a))
    .slice(0, limit);
  return keys.map((dateKey) => ({
    dateKey,
    items: buildDayFeed(dateKey, todayKey, chapters, []),
  }));
}
