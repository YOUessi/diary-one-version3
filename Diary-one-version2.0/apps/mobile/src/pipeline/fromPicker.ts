import type { ImagePickerAsset } from 'expo-image-picker';
import type { PickedMedia } from './types';

/** Best-effort capture time from EXIF / asset fields (IMP02). */
function creationTimeMsFromAsset(a: ImagePickerAsset): number | undefined {
  const exif = a.exif as Record<string, unknown> | null | undefined;
  if (exif) {
    const dateTime =
      (typeof exif.DateTimeOriginal === 'string' && exif.DateTimeOriginal) ||
      (typeof exif.DateTimeDigitized === 'string' && exif.DateTimeDigitized) ||
      (typeof exif.DateTime === 'string' && exif.DateTime) ||
      null;
    if (dateTime) {
      // EXIF often "YYYY:MM:DD HH:MM:SS"
      const normalized = dateTime.replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3');
      const parsed = Date.parse(normalized);
      if (Number.isFinite(parsed)) return parsed;
    }
  }
  const rawCreated = (a as { creationTime?: number; duration?: number }).creationTime;
  if (typeof rawCreated === 'number' && rawCreated > 0) {
    // expo may return seconds or ms
    return rawCreated < 1e12 ? Math.round(rawCreated * 1000) : Math.round(rawCreated);
  }
  return undefined;
}

export function fromPickerAssets(assets: ImagePickerAsset[]): PickedMedia[] {
  return assets.map((a) => ({
    uri: a.uri,
    mediaType: a.type === 'video' ? 'video' : a.type === 'image' ? 'image' : 'unknown',
    width: a.width,
    height: a.height,
    fileSize: a.fileSize,
    durationMs: a.duration != null ? Math.round(a.duration * 1000) : undefined,
    fileName: a.fileName ?? undefined,
    creationTimeMs: creationTimeMsFromAsset(a),
  }));
}
