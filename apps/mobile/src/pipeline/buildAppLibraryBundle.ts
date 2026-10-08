import * as FileSystem from 'expo-file-system/legacy';
import * as VideoThumbnails from 'expo-video-thumbnails';
import { sha256File } from './sha256File';
import { ensureLocalFileUri } from './ensureLocalFileUri';
import { writeNormalizedFrame, EVIDENCE_FRAME } from './evidenceNormalize';
import { rememberRawAssetsFromBundleAssets } from './dedupeMedia';
import type { PickedMedia } from './types';
import {
  type AppLibraryBundle,
  type BundleExportVersion,
  BUNDLE_VERSION_ID,
  spatialTransformFor,
  type SpatialTransform,
} from './bundleTypes';
import { buildSemanticVideoEvidence } from '../evidence/runSemanticVideoEvidence';
import * as Crypto from 'expo-crypto';

const DEVICE_STUB = {
  device_id: 'PHOTO_LIBRARY_TEST',
  hardware_revision: 'N/A',
  firmware_version: 'N/A',
  sdk_version: 'diary-one-app-expo',
};

function newSessionId(): string {
  return Crypto.randomUUID();
}

function extFromName(name?: string, fallback = 'jpg'): string {
  if (!name) return fallback;
  const m = name.match(/\.([a-zA-Z0-9]+)$/);
  return (m?.[1] ?? fallback).toLowerCase();
}

type FrameRow = {
  frame_id: string;
  window_index: number;
  window_count: 1 | 2 | 4 | 6 | 10;
  sample_role: 'PHOTO_REPRESENTATIVE' | 'WINDOW_EARLY' | 'WINDOW_MIDDLE' | 'WINDOW_LATE';
  canonical_offset_ms: 1500 | 4500 | 7500;
  source_timestamp_ms: number | null;
  relative_path: string;
  sha256: string;
  width: 768;
  height: 1024;
  spatial_transform: SpatialTransform;
};

async function frameFromUri(
  sourceUri: string,
  destRelative: string,
  bundleDir: string,
  spatial: SpatialTransform,
  sourceW: number | undefined,
  sourceH: number | undefined,
  meta: Omit<FrameRow, 'relative_path' | 'sha256' | 'spatial_transform' | 'width' | 'height'>,
): Promise<FrameRow> {
  const destUri = `${bundleDir}${destRelative}`;
  await writeNormalizedFrame(sourceUri, destUri, spatial, sourceW, sourceH);
  const sha256 = await sha256File(destUri);
  return {
    ...meta,
    spatial_transform: spatial,
    relative_path: destRelative,
    sha256,
    width: EVIDENCE_FRAME.width,
    height: EVIDENCE_FRAME.height,
  };
}

export async function buildAppLibraryBundle(
  items: PickedMedia[],
  bundleDir: string,
  exportVersion: BundleExportVersion = 'V04',
): Promise<{ bundle: AppLibraryBundle; jsonPath: string }> {
  const spatial = spatialTransformFor(exportVersion);
  await FileSystem.makeDirectoryAsync(bundleDir, { intermediates: true });
  await FileSystem.makeDirectoryAsync(`${bundleDir}frames/`, { intermediates: true });

  const sessionId = newSessionId();
  const assets: Record<string, unknown>[] = [];
  /** Sidecar for App: map asset_id → local source URI (original not packed in bundle). */
  const sourceUris: Record<string, { uri: string; media_kind: 'PHOTO' | 'VIDEO' }> = {};

  for (let sequenceIndex = 0; sequenceIndex < items.length; sequenceIndex++) {
    const item = items[sequenceIndex];
    const assetId = `asset-${sequenceIndex}`;
    const localUri = await ensureLocalFileUri(item.uri, assetId);
    sourceUris[assetId] = {
      uri: localUri,
      media_kind: item.mediaType === 'video' ? 'VIDEO' : 'PHOTO',
    };
    const isPhoto = item.mediaType !== 'video';
    const originalSha = await sha256File(localUri);
    const ext = extFromName(item.fileName, isPhoto ? 'jpg' : 'mp4');
    const srcW = item.width;
    const srcH = item.height;

    if (isPhoto) {
      const rel = `frames/${assetId}_0.jpg`;
      const frame = await frameFromUri(localUri, rel, bundleDir, spatial, srcW, srcH, {
        frame_id: `${assetId}-f0`,
        window_index: 0,
        window_count: 1,
        sample_role: 'PHOTO_REPRESENTATIVE',
        canonical_offset_ms: 4500,
        source_timestamp_ms: null,
      });
      assets.push({
        asset_id: assetId,
        source_display_name: item.fileName ?? assetId,
        media_kind: 'PHOTO',
        media_source: 'PHONE_LIBRARY_DAY_TEST',
        original_file_extension: ext,
        original_sha256: originalSha,
        original_bytes: item.fileSize ?? 0,
        original_width: item.width ?? 1,
        original_height: item.height ?? 1,
        original_duration_ms: null,
        original_included: false,
        sequence_index: sequenceIndex,
        logical_asset_duration_ms: 9000,
        materialized_video: false,
        evidence_sampling_profile: 'PHOTO_SINGLE_FRAME',
        evidence_window_count: 1,
        frames: [frame],
      });
      continue;
    }

    const durationMs = Math.max(1000, Math.min(item.durationMs ?? 9000, 120_000));
    let evidence_window_count: 1 | 2 | 4 | 6 | 10 = 1;
    let evidence_sampling_profile = 'VIDEO_SINGLE_WINDOW_THREE';
    let frames: FrameRow[] = [];

    try {
      const semantic = await buildSemanticVideoEvidence({
        assetId,
        localVideoUri: localUri,
        durationMs,
        bundleDir,
        spatial,
        sourceW: srcW,
        sourceH: srcH,
      });
      frames = semantic.frames as FrameRow[];
      evidence_sampling_profile = semantic.evidence_sampling_profile;
      evidence_window_count = semantic.evidence_window_count as typeof evidence_window_count;
    } catch {
      evidence_window_count =
        durationMs <= 10_000 ? 1 : durationMs <= 30_000 ? 2 : durationMs <= 90_000 ? 4 : 6;
      evidence_sampling_profile =
        evidence_window_count === 1
          ? 'VIDEO_SINGLE_WINDOW_THREE'
          : 'VIDEO_MULTI_WINDOW_TWO_PER_WINDOW';

      const canonicalOffsets =
        evidence_window_count === 1
          ? [1500, 4500, 7500]
          : Array.from({ length: evidence_window_count }, () => [1500, 7500] as const).flat();

      for (let fi = 0; fi < canonicalOffsets.length; fi++) {
        const offset = canonicalOffsets[fi];
        const window_index = evidence_window_count === 1 ? 0 : Math.floor(fi / 2);
        const sample_role: FrameRow['sample_role'] =
          offset === 4500 ? 'WINDOW_MIDDLE' : offset === 1500 ? 'WINDOW_EARLY' : 'WINDOW_LATE';
        const fraction = (fi + 1) / (canonicalOffsets.length + 1);
        const source_timestamp_ms = Math.max(
          0,
          Math.min(durationMs - 1, Math.round(durationMs * fraction)),
        );
        const thumb = await VideoThumbnails.getThumbnailAsync(localUri, {
          time: source_timestamp_ms,
          quality: 0.85,
        });
        const rel = `frames/${assetId}_${fi}.jpg`;
        frames.push(
          await frameFromUri(thumb.uri, rel, bundleDir, spatial, srcW, srcH, {
            frame_id: `${assetId}-f${fi}`,
            window_index,
            window_count: evidence_window_count,
            sample_role,
            canonical_offset_ms: offset as 1500 | 4500 | 7500,
            source_timestamp_ms,
          }),
        );
      }
    }

    assets.push({
      asset_id: assetId,
      source_display_name: item.fileName ?? assetId,
      media_kind: 'VIDEO',
      media_source: 'PHONE_LIBRARY_DAY_TEST',
      original_file_extension: ext,
      original_sha256: originalSha,
      original_bytes: item.fileSize ?? 0,
      original_width: item.width ?? 1,
      original_height: item.height ?? 1,
      original_duration_ms: durationMs,
      original_included: false,
      sequence_index: sequenceIndex,
      logical_asset_duration_ms: 9000,
      materialized_video: false,
      evidence_sampling_profile,
      evidence_window_count,
      frames,
    });
  }

  const bundle: AppLibraryBundle = {
    bundle_version: BUNDLE_VERSION_ID[exportVersion],
    research_only: true,
    session: {
      session_id: sessionId,
      exported_at: new Date().toISOString(),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    },
    device: DEVICE_STUB,
    normalization: {
      width: EVIDENCE_FRAME.width,
      height: EVIDENCE_FRAME.height,
      orientation: 'PORTRAIT',
      aspect_ratio: '3:4',
      spatial_transform: spatial,
      temporal_transform: 'PHONE_TEST_DURATION_WINDOWS_V01',
      canonical_frame_offsets_ms: [1500, 4500, 7500],
      evidence_profile_version: 'PHONE_TEST_DURATION_WINDOWS_V01',
    },
    assets,
  };

  await rememberRawAssetsFromBundleAssets(
    assets as Array<{
      asset_id?: string;
      original_sha256?: string;
      media_kind?: string;
      source_display_name?: string;
      original_bytes?: number;
    }>,
  );

  const jsonPath = `${bundleDir}bundle.json`;
  await FileSystem.writeAsStringAsync(jsonPath, JSON.stringify(bundle, null, 2));
  await FileSystem.writeAsStringAsync(
    `${bundleDir}source_uris.json`,
    JSON.stringify(sourceUris, null, 2),
  );
  return { bundle, jsonPath };
}

/** @deprecated Use buildAppLibraryBundle */
export async function buildBundleV03(items: PickedMedia[], bundleDir: string) {
  return buildAppLibraryBundle(items, bundleDir, 'V03');
}
