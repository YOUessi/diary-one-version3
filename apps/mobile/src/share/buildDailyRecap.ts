import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import type { Chapter } from '../model';

const RECAP_WIDTH = 1080;
const RECAP_HEIGHT = 1920;

export async function buildDailyRecapAsset(chapters: Chapter[]): Promise<string | null> {
  if (chapters.length === 0) return null;

  const uri =
    chapters[0].heroUri ??
    chapters[0].moments.find((m) => m.posterUri)?.posterUri ??
    chapters.find((c) => c.heroUri)?.heroUri;

  if (!uri) return null;

  const resized = await manipulateAsync(
    uri,
    [{ resize: { width: RECAP_WIDTH } }],
    { compress: 0.88, format: SaveFormat.JPEG },
  );

  const letterboxed = await manipulateAsync(
    resized.uri,
    [{ resize: { width: RECAP_WIDTH, height: RECAP_HEIGHT } }],
    { compress: 0.88, format: SaveFormat.JPEG },
  );

  return letterboxed.uri;
}
