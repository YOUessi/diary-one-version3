import * as FileSystem from 'expo-file-system/legacy';
import { DEMO_PHOTO_JPEG_BASE64 } from './demoPhotoBase64';
import type { PickedMedia } from './types';

/**
 * Writes a real 768×1024 JPEG into cache — no ImageManipulator, no gallery.
 * Safe path for Expo Go Android when pipeline fails on picker/manipulate.
 */
export async function createDemoPickedPhoto(): Promise<PickedMedia> {
  const root = FileSystem.cacheDirectory;
  if (!root) throw new Error('cacheDirectory unavailable');
  const uri = `${root}demo-photo-${Date.now()}.jpg`;
  await FileSystem.writeAsStringAsync(uri, DEMO_PHOTO_JPEG_BASE64, {
    encoding: FileSystem.EncodingType.Base64,
  });
  const info = await FileSystem.getInfoAsync(uri);
  if (!info.exists || (info.size ?? 0) < 100) {
    throw new Error('Demo JPEG write failed (empty file).');
  }
  return {
    uri,
    mediaType: 'image',
    width: 768,
    height: 1024,
    fileSize: info.size,
    fileName: 'demo-photo.jpg',
  };
}
