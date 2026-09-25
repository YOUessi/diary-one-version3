import { manipulateAsync, SaveFormat, FlipType } from 'expo-image-manipulator';
import type { Chapter } from '../model';

const COLLAGE_WIDTH = 1080;

export async function buildChapterPhotoCollage(chapter: Chapter): Promise<string | null> {
  const uris = [
    chapter.heroUri,
    ...chapter.moments.map((m) => m.posterUri ?? m.playbackUri),
  ].filter((u): u is string => Boolean(u));
  const uri = uris[0];
  if (!uri) return null;
  const out = await manipulateAsync(
    uri,
    [{ resize: { width: COLLAGE_WIDTH } }],
    { compress: 0.9, format: SaveFormat.JPEG },
  );
  return out.uri;
}

export async function buildIllustratedShare(
  chapter: Chapter,
  style: 'A' | 'B' | 'C',
): Promise<string | null> {
  const source = chapter.heroUri ?? chapter.moments[0]?.posterUri;
  if (!source) return null;
  const resized = await manipulateAsync(
    source,
    [{ resize: { width: COLLAGE_WIDTH } }],
    { compress: 0.9, format: SaveFormat.JPEG },
  );
  if (style === 'A') return resized.uri;
  const flip = style === 'B' ? FlipType.Vertical : FlipType.Horizontal;
  const flipped = await manipulateAsync(resized.uri, [{ flip }], {
    compress: 0.9,
    format: SaveFormat.JPEG,
  });
  return flipped.uri;
}
