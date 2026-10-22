import * as FileSystem from 'expo-file-system/legacy';
import { requireOptionalNativeModule } from 'expo';

export type ExtractedVideoFrame = {
  uri: string;
  requestedMs: number;
  actualPtsMs: number;
  decodeTimeMs?: number;
};

const NativeDiaryOneVision = requireOptionalNativeModule<{
  isAvailable?: boolean;
  normalizeEvidenceFrame: (sourceUri: string, destUri: string) => Promise<void>;
  extractVideoWindowFrames: (
    videoUri: string,
    timestampsMs: number[],
    destDir: string,
    bounds: [number, number],
  ) => Promise<ExtractedVideoFrame[]>;
}>('DiaryOneVision');

/** AVFoundation decoding only. No Apple Vision model or inferred timestamps. */
export function isNativeVideoDecoderAvailable(): boolean {
  return Boolean(NativeDiaryOneVision?.extractVideoWindowFrames && NativeDiaryOneVision?.normalizeEvidenceFrame);
}

/** Render a real aspect-fit letterbox on iOS; never silently stretch the frame. */
export async function normalizeVideoEvidenceFrame(sourceUri: string, destUri: string): Promise<void> {
  if (!NativeDiaryOneVision?.normalizeEvidenceFrame) throw new Error('请重新构建 App 以安装视频帧归一化模块。');
  await NativeDiaryOneVision.normalizeEvidenceFrame(sourceUri, destUri);
}

export async function extractVideoFramesAtTimes(
  videoUri: string,
  timestampsMs: number[],
  destDir: string,
  bounds: [number, number],
): Promise<ExtractedVideoFrame[]> {
  if (NativeDiaryOneVision?.extractVideoWindowFrames) {
    await FileSystem.makeDirectoryAsync(destDir, { intermediates: true });
    return NativeDiaryOneVision.extractVideoWindowFrames(videoUri, timestampsMs, destDir, bounds);
  }
  throw new Error('请安装包含视频解码模块的 iOS 开发版或 TestFlight App；当前运行环境不支持精确抽帧。');
}
