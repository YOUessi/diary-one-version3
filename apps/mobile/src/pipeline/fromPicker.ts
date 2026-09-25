import type { ImagePickerAsset } from 'expo-image-picker';
import type { PickedMedia } from './types';

export function fromPickerAssets(assets: ImagePickerAsset[]): PickedMedia[] {
  return assets.map((a) => ({
    uri: a.uri,
    mediaType: a.type === 'video' ? 'video' : a.type === 'image' ? 'image' : 'unknown',
    width: a.width,
    height: a.height,
    fileSize: a.fileSize,
    durationMs: a.duration != null ? Math.round(a.duration * 1000) : undefined,
    fileName: a.fileName ?? undefined,
  }));
}
