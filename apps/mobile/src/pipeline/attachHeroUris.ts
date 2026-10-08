import type { Chapter } from '../model';
import { attachChapterMediaFromBundle } from './attachChapterMedia';

/**
 * Legacy wrapper: round-robin frames when no preview chapter media hints.
 * Prefer `attachChapterMediaFromBundle(chapters, preview.chapters, …)`.
 */
export async function attachHeroUrisFromBundle(
  chapters: Chapter[],
  bundleDir: string,
  bundleJsonPath: string,
): Promise<Chapter[]> {
  return attachChapterMediaFromBundle(chapters, [], bundleDir, bundleJsonPath);
}
