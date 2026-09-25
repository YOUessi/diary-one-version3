import type { Chapter } from '../model';

export type SearchHit = { chapter: Chapter; snippet?: string };

function pickSnippet(chapter: Chapter, q: string): string | undefined {
  const fields = [
    chapter.title,
    chapter.aiStory,
    chapter.yourStory ?? '',
    ...chapter.tags,
  ];
  for (const field of fields) {
    const lower = field.toLowerCase();
    const idx = lower.indexOf(q);
    if (idx >= 0) {
      const start = Math.max(0, idx - 20);
      const end = Math.min(field.length, idx + q.length + 40);
      return (start > 0 ? '…' : '') + field.slice(start, end) + (end < field.length ? '…' : '');
    }
  }
  return chapter.aiStory.slice(0, 80);
}

export function searchChapters(chapters: Chapter[], query: string): SearchHit[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const tokens = q.split(/\s+/).filter(Boolean);
  const hits: SearchHit[] = [];
  for (const chapter of chapters) {
    const hay = [
      chapter.title,
      chapter.aiStory,
      chapter.yourStory ?? '',
      ...chapter.tags,
      ...(chapter.detailTags ?? []),
    ]
      .join(' ')
      .toLowerCase();
    const matches =
      tokens.length === 1 ? hay.includes(tokens[0]) : tokens.every((t) => hay.includes(t));
    if (matches) hits.push({ chapter, snippet: pickSnippet(chapter, tokens[0]) });
  }
  return hits;
}
