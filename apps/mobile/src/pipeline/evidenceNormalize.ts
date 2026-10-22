/** Contract-sized JPEG evidence; original metadata is never copied into the bundle. */
import * as FileSystem from 'expo-file-system/legacy';
import * as ImageManipulator from 'expo-image-manipulator';
import { requireOptionalNativeModule } from 'expo';
import { Platform } from 'react-native';
import type { SpatialTransform } from './bundleTypes';

export const EVIDENCE_FRAME = { width: 768, height: 1024, jpegCompress: 0.84 } as const;

type NormalizedPhoto = { uri: string; width: number; height: number; format: string; spatialTransform: string };
const native = requireOptionalNativeModule<{
  normalizePhotoEvidenceFrame?: (source: string, dest: string, spatial: string) => Promise<NormalizedPhoto>;
}>('DiaryOneVision');

export async function writeNormalizedFrame(
  sourceUri: string,
  destUri: string,
  spatial: SpatialTransform,
  sourceW?: number,
  sourceH?: number,
): Promise<void> {
  const { width, height, jpegCompress } = EVIDENCE_FRAME;
  if (Platform.OS === 'ios') {
    if (!native?.normalizePhotoEvidenceFrame) throw new Error('EVIDENCE_IMAGE_MODULE_MISSING');
    const result = await native.normalizePhotoEvidenceFrame(sourceUri, destUri, spatial);
    if (!result || result.width !== width || result.height !== height || result.format !== 'JPEG' ||
        result.uri !== destUri || result.spatialTransform !== spatial) {
      await FileSystem.deleteAsync(destUri, { idempotent: true }).catch(() => {});
      throw new Error('EVIDENCE_IMAGE_INVALID');
    }
    return;
  }

  // Expo extent is Web-only. Unsupported platforms must not emit a stretched or misdeclared frame.
  if (Platform.OS !== 'web') throw new Error('EVIDENCE_IMAGE_MODULE_MISSING');
  if (!sourceW || !sourceH || !Number.isFinite(sourceW) || !Number.isFinite(sourceH) || sourceW <= 0 || sourceH <= 0) {
    throw new Error('EVIDENCE_IMAGE_INVALID');
  }
  const crop = spatial === 'CENTER_CROP_ASPECT_FILL';
  const scale = crop ? Math.max(width / sourceW, height / sourceH) : Math.min(width / sourceW, height / sourceH);
  const newW = Math.max(1, Math.round(sourceW * scale));
  const newH = Math.max(1, Math.round(sourceH * scale));
  const result = await ImageManipulator.manipulateAsync(sourceUri, [
    { resize: { width: newW, height: newH } },
    crop
      ? { crop: { width, height, originX: Math.round((newW - width) / 2), originY: Math.round((newH - height) / 2) } }
      : { extent: { width, height, originX: Math.round((width - newW) / 2), originY: Math.round((height - newH) / 2), backgroundColor: '#000000' } },
  ], { compress: jpegCompress, format: ImageManipulator.SaveFormat.JPEG });
  if (result.width !== width || result.height !== height) throw new Error('EVIDENCE_IMAGE_INVALID');
  await FileSystem.copyAsync({ from: result.uri, to: destUri });
}
