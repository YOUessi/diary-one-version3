import * as FileSystem from 'expo-file-system/legacy';
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import type { Chapter } from '../model';
import { composeCollageViaBff, composeIllustratedViaBff } from './composeShareViaBff';

const PREP_WIDTH = 1080;

function collectChapterImageUris(chapter: Chapter): string[] {
  const raw = [
    chapter.heroUri,
    ...chapter.moments.map((m) => m.posterUri ?? m.playbackUri),
  ].filter((u): u is string => Boolean(u));
  // Prefer stills — skip remote sample videos for collage tiles
  const stills = raw.filter((u) => !/\.(mp4|mov|m4v)(\?|$)/i.test(u));
  const list = stills.length ? stills : raw;
  const uniq: string[] = [];
  for (const u of list) {
    if (!uniq.includes(u)) uniq.push(u);
  }
  return uniq.slice(0, 4);
}

async function prepJpeg(uri: string): Promise<string> {
  const out = await manipulateAsync(
    uri,
    [{ resize: { width: PREP_WIDTH } }],
    { compress: 0.88, format: SaveFormat.JPEG },
  );
  return out.uri;
}

/** Real multi-tile collage via BFF Pillow (Expo Go + LAN Dev Lite). */
export async function buildChapterPhotoCollage(chapter: Chapter): Promise<string | null> {
  const uris = collectChapterImageUris(chapter);
  if (!uris.length) return null;
  const prepared = await Promise.all(uris.map((u) => prepJpeg(u)));
  const stamp = Date.now();
  const dest = `${FileSystem.cacheDirectory}collage_${chapter.id}_${stamp}.jpg`;
  return composeCollageViaBff(prepared, dest);
}

/** Illustrated A/B/C via BFF Pillow — distinct layouts for Expo Go. */
export async function buildIllustratedShare(
  chapter: Chapter,
  style: 'A' | 'B' | 'C',
): Promise<string | null> {
  const source = chapter.heroUri ?? chapter.moments.find((m) => m.posterUri)?.posterUri;
  if (!source) return null;
  const prepared = await prepJpeg(source);
  const stamp = Date.now();
  const dest = `${FileSystem.cacheDirectory}illustrated_${chapter.id}_${style}_${stamp}.jpg`;
  return composeIllustratedViaBff(prepared, style, dest, chapter.title);
}
