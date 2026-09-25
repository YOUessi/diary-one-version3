/**
 * PRD App「压缩 / 归一化」— 产出最小 Evidence 帧（768×1024 JPEG）。
 * 原片不入包（original_included=false）；无 GPS/EXIF 外发。
 */
import * as FileSystem from 'expo-file-system/legacy';
import * as ImageManipulator from 'expo-image-manipulator';
import type { SpatialTransform } from './bundleTypes';

/** 合同固定输出尺寸（V03/V04 phone-test Evidence） */
export const EVIDENCE_FRAME = {
  width: 768,
  height: 1024,
  /** JPEG 质量：体积与观感折中；失败路径同值 */
  jpegCompress: 0.84,
} as const;

export async function writeNormalizedFrame(
  sourceUri: string,
  destUri: string,
  spatial: SpatialTransform,
  sourceW?: number,
  sourceH?: number,
): Promise<void> {
  const { width: TW, height: TH, jpegCompress } = EVIDENCE_FRAME;

  const fallback = async () => {
    const result = await ImageManipulator.manipulateAsync(
      sourceUri,
      [{ resize: { width: TW, height: TH } }],
      { compress: jpegCompress, format: ImageManipulator.SaveFormat.JPEG },
    );
    await FileSystem.copyAsync({ from: result.uri, to: destUri });
  };

  // CENTER_CROP：Expo Go Android 上 extent 不稳定 → 直接 resize 兜底
  if (spatial === 'CENTER_CROP_ASPECT_FILL') {
    await fallback();
    return;
  }

  try {
    const w = Math.max(1, sourceW ?? 3);
    const h = Math.max(1, sourceH ?? 4);
    const scale = Math.min(TW / w, TH / h);
    const newW = Math.max(1, Math.round(w * scale));
    const newH = Math.max(1, Math.round(h * scale));
    const originX = Math.round((TW - newW) / 2);
    const originY = Math.round((TH - newH) / 2);
    const result = await ImageManipulator.manipulateAsync(
      sourceUri,
      [
        { resize: { width: newW, height: newH } },
        {
          extent: {
            width: TW,
            height: TH,
            originX,
            originY,
            backgroundColor: '#000000',
          },
        },
      ],
      { compress: jpegCompress, format: ImageManipulator.SaveFormat.JPEG },
    );
    await FileSystem.copyAsync({ from: result.uri, to: destUri });
  } catch {
    await fallback();
  }
}
