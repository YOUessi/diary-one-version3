import * as FileSystem from 'expo-file-system/legacy';
import { sha256File } from './sha256File';
import { ensureLocalFileUri } from './ensureLocalFileUri';
import { writeNormalizedFrame, EVIDENCE_FRAME } from './evidenceNormalize';
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
import type { ImportedSource } from '../domain/capturedImports';

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
  window_count: number;
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
  assertCurrent: () => void = () => {},
): Promise<{ bundle: AppLibraryBundle; jsonPath: string; sourceUris: Record<string, ImportedSource> }> {
  const spatial = spatialTransformFor(exportVersion);
  await FileSystem.makeDirectoryAsync(bundleDir, { intermediates: true });
  await FileSystem.makeDirectoryAsync(`${bundleDir}frames/`, { intermediates: true });

  const sessionId = newSessionId();
  const assets: Record<string, unknown>[] = [];
  /** Sidecar for App: map asset_id → local source URI (original not packed in bundle). */
  const sourceUris: Record<string, ImportedSource> = {};

  for (let sequenceIndex = 0; sequenceIndex < items.length; sequenceIndex++) {
    assertCurrent();
    const item = items[sequenceIndex];
    const assetId = `asset-${sequenceIndex}`;
    let localUri = await ensureLocalFileUri(item.uri, assetId);
    {
      // Picker file:// URLs may point into purgeable cache. Only this local copy is retained;
      // originals remain excluded from the uploaded evidence manifest.
      const sourceDir = `${bundleDir}sources/`;
      await FileSystem.makeDirectoryAsync(sourceDir, { intermediates: true });
      const target = `${sourceDir}${assetId}.${extFromName(item.fileName, item.mediaType === 'video' ? 'mp4' : 'jpg')}`;
      await FileSystem.copyAsync({ from: localUri, to: target });
      localUri = target;
    }
    assertCurrent();
    sourceUris[assetId] = {
      uri: localUri,
      media_kind: item.mediaType === 'video' ? 'VIDEO' : 'PHOTO',
      creationTimeMs: item.creationTimeMs,
      durationMs: item.durationMs,
      captureDayKey: item.captureDayKey,
      captureTimeRaw: item.captureTimeRaw,
      captureTimeSource: item.captureTimeSource,
      captureUtcOffset: item.captureUtcOffset,
      confirmedDayKey: item.confirmedDayKey,
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

    const durationMs = Math.round(item.durationMs ?? NaN);
    if (!Number.isFinite(durationMs) || durationMs <= 0) {
      throw new Error('Video duration is missing or invalid; reselect a readable video.');
    }
    // Preserve the main branch's owner fence and durable original/capture metadata.
    // Only decoded, model-selected frames may enter the evidence bundle. Errors
    // must reach the existing pipeline retry path instead of fabricating timing.
    const semantic = await buildSemanticVideoEvidence({
      assetId,
      localVideoUri: localUri,
      durationMs,
      bundleDir,
      spatial,
      sourceW: srcW,
      sourceH: srcH,
      assertCurrent,
    });
    assertCurrent();
    const { frames, evidence_sampling_profile, evidence_window_count } = semantic;

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

  // PRD REL01 / IMP03 — do NOT write raw_assets ledger here.
  // Ledger is recorded only after cloud admit succeeds (runPipeline), so failed
  // jobs can retry the same selection without "All duplicates".

  const jsonPath = `${bundleDir}bundle.json`;
  assertCurrent();
  await FileSystem.writeAsStringAsync(jsonPath, JSON.stringify(bundle, null, 2));
  assertCurrent();
  await FileSystem.writeAsStringAsync(
    `${bundleDir}source_uris.json`,
    JSON.stringify(sourceUris, null, 2),
  );
  assertCurrent();
  return { bundle, jsonPath, sourceUris };
}

/** @deprecated Use buildAppLibraryBundle */
export async function buildBundleV03(items: PickedMedia[], bundleDir: string) {
  return buildAppLibraryBundle(items, bundleDir, 'V03');
}
