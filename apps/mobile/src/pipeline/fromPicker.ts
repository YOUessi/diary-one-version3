import type { ImagePickerAsset } from 'expo-image-picker';
import type { PickedMedia } from './types';
import { dateKeyFromLocalDate } from '../domain/dayKey';

/** Best-effort capture time from EXIF / asset fields (IMP02). */
function captureMetadata(a: ImagePickerAsset): Partial<PickedMedia> {
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
      const match = /^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})(Z|[+-]\d{2}:\d{2})?$/.exec(normalized);
      const offset = match?.[3] || (typeof exif.OffsetTimeOriginal === 'string' ? exif.OffsetTimeOriginal : undefined);
      if (match && Number.isFinite(Date.parse(`${match[1]}T12:00:00Z`)) &&
          new Date(`${match[1]}T12:00:00Z`).toISOString().slice(0, 10) === match[1]) {
        const timestamp = offset && /^(Z|[+-]\d{2}:\d{2})$/.test(offset)
          ? Date.parse(`${match[1]}T${match[2]}${offset}`) : NaN;
        return { captureDayKey: match[1], captureTimeRaw: dateTime,
          captureUtcOffset: offset, captureTimeSource: Number.isFinite(timestamp) ? 'EXIF_OFFSET' : 'EXIF_LOCAL',
          creationTimeMs: Number.isFinite(timestamp) ? timestamp : undefined };
      }
    }
  }
  const rawCreated = (a as { creationTime?: number; duration?: number }).creationTime;
  if (typeof rawCreated === 'number' && rawCreated > 0) {
    // expo may return seconds or ms
    const timestamp = rawCreated < 1e12 ? Math.round(rawCreated * 1000) : Math.round(rawCreated);
    if (Number.isFinite(timestamp) && Number.isFinite(new Date(timestamp).getTime())) {
      return { creationTimeMs: timestamp, captureDayKey: dateKeyFromLocalDate(new Date(timestamp)),
        captureTimeSource: 'ASSET_TIMESTAMP', captureTimeRaw: String(rawCreated) };
    }
  }
  return { captureTimeSource: 'UNKNOWN' };
}

export function fromPickerAssets(assets: ImagePickerAsset[]): PickedMedia[] {
  return assets.map((a) => ({
    uri: a.uri,
    mediaType: a.type === 'video' ? 'video' : a.type === 'image' ? 'image' : 'unknown',
    width: a.width,
    height: a.height,
    fileSize: a.fileSize,
    durationMs: a.duration != null ? Math.round(a.duration) : undefined,
    fileName: a.fileName ?? undefined,
    ...captureMetadata(a),
  }));
}
