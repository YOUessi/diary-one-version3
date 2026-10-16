import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import type { Chapter } from '../model';
import { RECAP_HEIGHT, RECAP_MAX_SLIDES, RECAP_WIDTH } from './dailyRecapConstants';

function chapterHeroUri(chapter: Chapter): string | undefined {
  return (
    chapter.heroUri ??
    chapter.moments.find((m) => m.posterUri)?.posterUri ??
    undefined
  );
}

/** Letterboxed 9:16 JPEG paths for each chapter (up to RECAP_MAX_SLIDES). */
export async function buildDailyRecapSlides(chapters: Chapter[]): Promise<string[]> {
  const uris: string[] = [];
  for (const chapter of chapters.slice(0, RECAP_MAX_SLIDES)) {
    const src = chapterHeroUri(chapter);
    if (!src) continue;
    const resized = await manipulateAsync(
      src,
      [{ resize: { width: RECAP_WIDTH } }],
      { compress: 0.9, format: SaveFormat.JPEG },
    );
    const letterboxed = await manipulateAsync(
      resized.uri,
      [{ resize: { width: RECAP_WIDTH, height: RECAP_HEIGHT } }],
      { compress: 0.9, format: SaveFormat.JPEG },
    );
    uris.push(letterboxed.uri);
  }
  return uris;
}
