/**
 * Intake validation before dedupe / Evidence normalize.
 * Fail closed on unsupported or empty assets (Expo Go picker quirks).
 */
import type { PickedMedia } from './types';

const MAX_PHOTO_BYTES = 40 * 1024 * 1024;
const MAX_VIDEO_BYTES = 200 * 1024 * 1024;
const MAX_VIDEO_DURATION_MS = 10 * 60 * 1000;

export type MediaValidationResult =
  | { ok: true; items: PickedMedia[] }
  | { ok: false; reason: string };

export function validatePickedMedia(items: PickedMedia[]): MediaValidationResult {
  if (!items.length) {
    return { ok: false, reason: 'No media selected.' };
  }

  const accepted: PickedMedia[] = [];
  for (const item of items) {
    if (!item.uri || item.uri.trim() === '') {
      continue;
    }
    if (item.mediaType === 'unknown') {
      continue;
    }
    if (item.mediaType === 'image') {
      if (item.fileSize != null && item.fileSize > MAX_PHOTO_BYTES) {
        return { ok: false, reason: 'A photo is too large (max 40 MB).' };
      }
      if (item.width != null && item.height != null && (item.width < 32 || item.height < 32)) {
        continue;
      }
      accepted.push(item);
      continue;
    }
    if (item.mediaType === 'video') {
      if (item.fileSize != null && item.fileSize > MAX_VIDEO_BYTES) {
        return { ok: false, reason: 'A video is too large (max 200 MB).' };
      }
      if (item.durationMs != null && item.durationMs > MAX_VIDEO_DURATION_MS) {
        return { ok: false, reason: 'A video is longer than 10 minutes.' };
      }
      accepted.push(item);
    }
  }

  if (!accepted.length) {
    return { ok: false, reason: 'No valid photos or videos after validation.' };
  }
  return { ok: true, items: accepted };
}
