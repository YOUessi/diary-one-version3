import * as FileSystem from 'expo-file-system/legacy';
import type { Chapter } from '../model';
import { buildDailyRecapSlides } from './buildDailyRecapSlides';
import { encodeDailyRecapViaBff } from './encodeDailyRecapViaBff';

export type DailyRecapAsset = {
  videoUri: string;
  posterUri: string;
  hasAudio: boolean;
};

/**
 * Daily Recap MP4 — **PC BFF ffmpeg only** (Expo Go requirement).
 * Does not use phone-native video encoders.
 */
export async function buildDailyRecapAsset(chapters: Chapter[]): Promise<DailyRecapAsset | null> {
  const slides = await buildDailyRecapSlides(chapters);
  if (slides.length === 0) return null;

  const posterUri = slides[0];
  const stamp = Date.now();
  const outBase = `${FileSystem.cacheDirectory}daily_recap_${stamp}`;

  const videoUri = await encodeDailyRecapViaBff(slides, `${outBase}_bff.mp4`);

  return {
    videoUri,
    posterUri,
    hasAudio: false,
  };
}
