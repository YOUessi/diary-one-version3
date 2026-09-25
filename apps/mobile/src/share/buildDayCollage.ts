import { buildChapterPhotoCollage } from './buildPhotoCollage';
import type { Chapter } from '../model';

export async function buildDayPhotoCollage(chapters: Chapter[]): Promise<string | null> {
  if (chapters.length === 0) return null;
  return buildChapterPhotoCollage(chapters[0]);
}
