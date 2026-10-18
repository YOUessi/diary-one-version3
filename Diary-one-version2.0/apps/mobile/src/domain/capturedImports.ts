import type { CapturedOriginal } from '../model';
import { PHOTO_LIBRARY_TEST_SOURCE, type MediaIntakeSource } from './mediaIntake';

export type ImportedSource = { uri: string; media_kind: 'PHOTO' | 'VIDEO'; creationTimeMs?: number; durationMs?: number }
  & Pick<import('../pipeline/types').PickedMedia, 'captureDayKey' | 'captureTimeRaw' | 'captureTimeSource' | 'captureUtcOffset' | 'confirmedDayKey'>;

/** The gallery contains selected originals, regardless of AI curation outcome. */
export function capturedImports(batchId: string, dayKey: string, bundleDir: string,
  sources: Record<string, ImportedSource>, assets: { asset_id?: string; frames?: { relative_path?: string }[] }[],
  intakeSource: MediaIntakeSource = PHOTO_LIBRARY_TEST_SOURCE): CapturedOriginal[] {
  return Object.entries(sources).map(([assetId, source]) => {
    const frame = assets.find((asset) => asset.asset_id === assetId)?.frames?.[0]?.relative_path;
    return {
    id: `${batchId}:original:${assetId}`,
    intakeSource,
    dateKey: dayKey,
    kind: source.media_kind === 'VIDEO' ? 'video' : 'photo',
    posterUri: frame ? `${bundleDir}${frame}` : source.media_kind === 'PHOTO' ? source.uri : undefined,
    playbackUri: source.uri,
    durationSec: source.media_kind === 'VIDEO' && source.durationMs ? source.durationMs / 1000 : undefined,
    capturedAtLabel: source.creationTimeMs && Number.isFinite(source.creationTimeMs)
      ? new Date(source.creationTimeMs).toLocaleString() : undefined,
  }; });
}
