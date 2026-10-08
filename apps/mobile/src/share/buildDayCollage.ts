import * as FileSystem from 'expo-file-system/legacy';
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import type { Chapter } from '../model';
import { composeCollageViaBff } from './composeShareViaBff';

const PREP_WIDTH = 1080;

function collectDayImageUris(chapters: Chapter[]): string[] {
  const uniq: string[] = [];
  for (const ch of chapters) {
    const candidates = [
      ch.heroUri,
      ...ch.moments.map((m) => m.posterUri).filter((u): u is string => Boolean(u)),
    ];
    for (const u of candidates) {
      if (u && !uniq.includes(u) && !/\.(mp4|mov|m4v)(\?|$)/i.test(u)) {
        uniq.push(u);
      }
      if (uniq.length >= 4) return uniq;
    }
  }
  return uniq;
}

/** Day collage: up to 4 stills across the day's chapters → BFF multi-tile. */
export async function buildDayPhotoCollage(chapters: Chapter[]): Promise<string | null> {
  if (chapters.length === 0) return null;
  const uris = collectDayImageUris(chapters);
  if (!uris.length) return null;
  const prepared = await Promise.all(
    uris.map(async (uri) => {
      const out = await manipulateAsync(
        uri,
        [{ resize: { width: PREP_WIDTH } }],
        { compress: 0.88, format: SaveFormat.JPEG },
      );
      return out.uri;
    }),
  );
  const stamp = Date.now();
  const dest = `${FileSystem.cacheDirectory}day_collage_${stamp}.jpg`;
  return composeCollageViaBff(prepared, dest);
}
