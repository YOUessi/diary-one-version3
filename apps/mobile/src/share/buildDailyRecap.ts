import { Platform } from 'react-native';
import * as FileSystem from 'expo-file-system/legacy';
import type { Chapter } from '../model';
import { buildDailyRecapSlides } from './buildDailyRecapSlides';
import { encodeDailyRecapNative } from './encodeDailyRecapNative';
import { encodeDailyRecapViaBff } from './encodeDailyRecapViaBff';

export type DailyRecapAsset = {
  videoUri: string;
  posterUri: string;
  hasAudio: boolean;
};

function pickAudioUri(chapters: Chapter[]): string | undefined {
  for (const ch of chapters) {
    for (const m of ch.moments) {
      const uri = m.playbackUri;
      if (uri && (uri.startsWith('file://') || uri.startsWith('/'))) {
        return uri.startsWith('file://') ? uri : `file://${uri}`;
      }
    }
  }
  return undefined;
}

export async function buildDailyRecapAsset(chapters: Chapter[]): Promise<DailyRecapAsset | null> {
  const slides = await buildDailyRecapSlides(chapters);
  if (slides.length === 0) return null;

  const posterUri = slides[0];
  const stamp = Date.now();
  const outBase = `${FileSystem.cacheDirectory}daily_recap_${stamp}`;
  const audioUri = pickAudioUri(chapters);

  const tryNative = async (): Promise<string> => {
    if (Platform.OS !== 'ios') throw new Error('skip_native');
    return encodeDailyRecapNative(slides, `${outBase}.mp4`, audioUri);
  };

  const tryBff = async (): Promise<string> => encodeDailyRecapViaBff(slides, `${outBase}_bff.mp4`);

  let videoUri: string | null = null;
  const errors: string[] = [];

  if (Platform.OS === 'ios') {
    try {
      videoUri = await tryNative();
    } catch (e) {
      errors.push(e instanceof Error ? e.message : String(e));
    }
  }

  if (!videoUri) {
    try {
      videoUri = await tryBff();
    } catch (e) {
      errors.push(e instanceof Error ? e.message : String(e));
    }
  }

  if (!videoUri) {
    throw new Error(errors.join(' | ') || 'recap_encode_failed');
  }

  return {
    videoUri,
    posterUri,
    hasAudio: Boolean(audioUri),
  };
}
