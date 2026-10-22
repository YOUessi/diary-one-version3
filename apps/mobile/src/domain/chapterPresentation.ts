import type { Chapter, MemoryMedia } from '../model';

export type ChapterMediaEntry = { id: string; media?: MemoryMedia; texts: string[] };

/** Annotate the selected frame with its highlight; don't show the same media twice. */
export function chapterMediaEntries(chapter: Chapter): ChapterMediaEntry[] {
  const entries: ChapterMediaEntry[] = chapter.moments.map(media => ({ id: media.id, media, texts: [] }));
  for (const highlight of chapter.highlights ?? []) {
    if (!highlight.media?.length) {
      entries.push({ id: highlight.id, texts: [highlight.text] });
      continue;
    }
    highlight.media.forEach((media, i) => {
      const entry = entries.find(e => e.media?.posterUri && e.media.posterUri === media.posterUri
        && e.media.playbackUri === media.playbackUri
        && (e.media.focusTimeSec == null || media.focusTimeSec == null || e.media.focusTimeSec === media.focusTimeSec));
      if (entry?.media) {
        entry.media = { ...entry.media,
          ...(media.focusTimeSec != null ? { focusTimeSec: media.focusTimeSec } : {}) };
        if (i === 0) entry.texts.push(highlight.text);
      } else {
        entries.push({ id: media.id, media, texts: i === 0 ? [highlight.text] : [] });
      }
    });
  }
  return entries;
}
