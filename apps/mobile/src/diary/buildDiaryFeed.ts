import type { LanguagePreference } from '../domain/appSettings';
import { appStrings, appLocale } from '../domain/strings';
import { daysWithContent, type Chapter, type MemoryOrder, type SmallMemory } from '../model';

export type DiaryFeedItem =
  | { kind: 'day_header'; label: string; sub?: string }
  | { kind: 'chapter'; chapter: Chapter }
  | { kind: 'small'; memory: SmallMemory };

function shortDay(dateKey: string, language: LanguagePreference): string {
  const [y, m, d] = dateKey.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString(appLocale(language), { month: 'short', day: 'numeric' });
}

function dayHeaderLabel(dateKey: string, todayKey: string, language: LanguagePreference): { label: string; sub?: string } {
  const sub = shortDay(dateKey, language);
  const strings = appStrings(language);
  if (dateKey === todayKey) return { label: strings.today, sub };
  if (dateKey === offsetDay(todayKey, -1)) return { label: strings.yesterday, sub };
  const [y, m, d] = dateKey.split('-').map(Number);
  const weekday = new Date(y, m - 1, d).toLocaleDateString(appLocale(language), { weekday: 'long' });
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
  language: LanguagePreference = 'en',
): DiaryFeedItem[] {
  const items: DiaryFeedItem[] = [];
  const header = dayHeaderLabel(dateKey, todayKey, language);
  items.push({ kind: 'day_header', label: header.label, sub: header.sub });

  const entries = [
    ...chapters.filter(c => c.dateKey === dateKey).map(chapter => ({ memory: chapter,
      item: { kind: 'chapter', chapter } as DiaryFeedItem })),
    ...smallMemories.map(memory => ({ memory,
      item: { kind: 'small', memory } as DiaryFeedItem })),
  ];
  // Only compare real capture times. Unknown legacy entries keep their slots;
  // sequence indices are comparable inside one import batch, never across batches.
  const hasTime = (m: MemoryOrder) => Number.isFinite(m.capturedAtMs) && m.capturedAtMs! > 0;
  const reorderSlots = (positions: number[], key: (m: typeof entries[number]['memory']) => number) => {
    const ordered = positions.map(i => entries[i]).sort((a, b) => key(a.memory) - key(b.memory));
    positions.forEach((slot, i) => { entries[slot] = ordered[i]; });
  };
  reorderSlots(entries.flatMap((e, i) => hasTime(e.memory) ? [i] : []), m => m.capturedAtMs!);
  const batches = new Set(entries.map(e => e.memory.sourceBatchId).filter(Boolean));
  for (const batch of batches) {
    reorderSlots(entries.flatMap((e, i) => !hasTime(e.memory) && e.memory.sourceBatchId === batch
      && Number.isInteger(e.memory.sourceSequenceIndex) && e.memory.sourceSequenceIndex! >= 0 ? [i] : []),
    m => m.sourceSequenceIndex!);
  }
  items.push(...entries.map(e => e.item));
  return items;
}

export function historyDateKeys(chapters: Chapter[], smallByDate: Record<string, SmallMemory[]>, todayKey: string) {
  return [...daysWithContent(chapters, smallByDate)].filter(k => k !== todayKey)
    .sort((a, b) => b.localeCompare(a));
}

export function buildEarlierFeed(
  chapters: Chapter[],
  todayKey: string,
  limit: number,
  language: LanguagePreference = 'en',
  smallByDate: Record<string, SmallMemory[]> = {},
): { dateKey: string; items: DiaryFeedItem[] }[] {
  const keys = historyDateKeys(chapters, smallByDate, todayKey).slice(0, limit);
  return keys.map((dateKey) => ({
    dateKey,
    items: buildDayFeed(dateKey, todayKey, chapters, smallByDate[dateKey] ?? [], language),
  }));
}
