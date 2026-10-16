import type { SearchHit } from './localSearch';

export type SearchAgentSummary = {
  /** One-screen summary above results (not a chat). */
  headline: string;
  bullets: string[];
  /** How the summary was produced */
  mode: 'extractive_local';
};

/**
 * Lightweight “search agent”: extractive summary of chapter hits.
 * Frozen IA: first-level results stay Chapters; this is a summary strip, not conversational RAG.
 */
export function summarizeSearchHits(query: string, hits: SearchHit[]): SearchAgentSummary | null {
  const q = query.trim();
  if (!q || hits.length === 0) return null;

  const titles = hits.slice(0, 6).map((h) => h.chapter.title);
  const tagFreq = new Map<string, number>();
  for (const h of hits) {
    for (const t of h.chapter.tags) {
      tagFreq.set(t, (tagFreq.get(t) ?? 0) + 1);
    }
  }
  const topTags = [...tagFreq.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([t]) => t);

  const dates = hits
    .map((h) => h.chapter.dateLabel || h.chapter.dateKey)
    .filter(Boolean);
  const uniqueDates = [...new Set(dates)].slice(0, 3);

  const bullets: string[] = [];
  bullets.push(`Top matches: ${titles.join(' · ')}.`);
  if (topTags.length) {
    bullets.push(`Recurring tags: ${topTags.join(', ')}.`);
  }
  if (uniqueDates.length) {
    bullets.push(`Across: ${uniqueDates.join(', ')}.`);
  }
  const withNotes = hits.filter((h) => Boolean(h.chapter.yourStory?.trim())).length;
  if (withNotes > 0) {
    bullets.push(`${withNotes} of these have your own notes.`);
  }

  const headline =
    hits.length === 1
      ? `1 memory matches “${q}”.`
      : `${hits.length} memories match “${q}”.`;

  return { headline, bullets, mode: 'extractive_local' };
}
