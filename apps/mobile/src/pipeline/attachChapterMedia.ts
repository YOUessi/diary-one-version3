import * as FileSystem from 'expo-file-system/legacy';
import type { Chapter, MemoryMedia, MemoryOrder, SmallMemory } from '../model';
import type { PreviewAha, PreviewChapter, PreviewSelectedMedia } from '../cloud/types';
import type { AppLibraryBundle } from './bundleTypes';
import { resolveBundleSourceUri } from './localMediaPaths';
import { sha256File } from './sha256File';

type FrameRef = {
  relative_path?: string;
  frame_id?: string;
  sha256?: string;
  source_timestamp_ms?: number | null;
};

type BundleAsset = {
  asset_id?: string;
  media_kind?: string;
  original_sha256?: string;
  original_duration_ms?: number | null;
  sequence_index?: number;
  frames?: FrameRef[];
};

export type SourceUriEntry = { uri: string; media_kind: 'PHOTO' | 'VIDEO' | string; creationTimeMs?: number };

type AssetFrames = { uris: string[]; frameIds: string[]; mediaKind?: string;
  frames?: FrameRef[]; durationMs?: number | null; sequenceIndex?: number };

export type ChapterMediaHints = {
  heroAssetId?: string;
  heroFrameId?: string;
  selectedMedia?: PreviewSelectedMedia[];
  momentIds: string[];
  timeLabel?: string;
  highlights?: PreviewChapter['highlights'];
};

/** Build asset_id → ordered local file URIs from an App Library Bundle on disk. */
export function buildBundleAssetUriIndex(
  bundleDir: string,
  assets: BundleAsset[],
): Map<string, AssetFrames> {
  const index = new Map<string, AssetFrames>();
  for (const asset of assets) {
    if (!asset.asset_id) continue;
    const uris: string[] = [];
    const frameIds: string[] = [];
    for (const frame of asset.frames ?? []) {
      if (!frame.relative_path) continue;
      uris.push(`${bundleDir}${frame.relative_path}`);
      frameIds.push(frame.frame_id ?? '');
    }
    if (uris.length) {
      index.set(asset.asset_id, { uris, frameIds, mediaKind: asset.media_kind,
        frames: asset.frames, durationMs: asset.original_duration_ms, sequenceIndex: asset.sequence_index });
    }
  }
  return index;
}

function frameUriForAsset(
  index: Map<string, AssetFrames>,
  assetId: string,
  evidenceFrameIds?: string[],
): string | undefined {
  const entry = index.get(assetId);
  if (!entry?.uris.length) return undefined;
  if (evidenceFrameIds?.length) {
    for (const fid of evidenceFrameIds) {
      const i = entry.frameIds.indexOf(fid);
      if (i >= 0) return entry.uris[i];
    }
    throw new Error(`Selected frame is missing for asset ${assetId}`);
  }
  return entry.uris[0];
}

function memoryOrder(selected: PreviewSelectedMedia[], index: Map<string, AssetFrames>,
  sources?: Record<string, SourceUriEntry>): MemoryOrder {
  const ids = selected.map(m => m.source_asset_id ?? m.asset_id);
  const times = ids.map(id => sources?.[id]?.creationTimeMs)
    .filter((n): n is number => typeof n === 'number' && Number.isFinite(n) && n > 0);
  const sequence = ids.map(id => index.get(id)?.sequenceIndex)
    .filter((n): n is number => typeof n === 'number' && Number.isInteger(n) && n >= 0);
  return {
    ...(times.length ? { capturedAtMs: Math.min(...times) } : {}),
    ...(sequence.length ? { sourceSequenceIndex: Math.min(...sequence) } : {}),
  };
}

function resolveSelectedMedia(id: string, selected: PreviewSelectedMedia[], assetIndex: Map<string, AssetFrames>,
  sourceUris?: Record<string, SourceUriEntry>, timeLabel?: string,
  enableMotion = false): MemoryMedia[] {
  return selected.map((media, index) => {
    const sourceId = media.source_asset_id ?? media.asset_id;
    const asset = assetIndex.get(sourceId);
    const frame = frameUriForAsset(assetIndex, sourceId,
      media.representative_frame_id ? [media.representative_frame_id] : media.evidence_frame_ids);
    if (!frame) throw new Error('Selected evidence frame is unavailable.');
    const kind = sourceUris?.[sourceId]?.media_kind ?? asset?.mediaKind;
    if (kind === 'VIDEO' && !sourceUris?.[sourceId]?.uri) {
      throw new Error('Selected video source is unavailable.');
    }
    const chosenFrameId = media.representative_frame_id ?? media.evidence_frame_ids?.[0];
    const selectedFrame = asset?.frames?.find(f => f.frame_id === chosenFrameId);
    const focus = media.focus_pts_ms ?? (enableMotion ? selectedFrame?.source_timestamp_ms : null);
    if (focus != null && (kind !== 'VIDEO' || !Number.isInteger(focus) || focus < 0
      || !(typeof asset?.durationMs === 'number' && focus < asset.durationMs)
      || !asset.frames?.some(f => media.evidence_frame_ids?.includes(f.frame_id ?? '') && f.source_timestamp_ms === focus))) {
      throw new Error('Selected video focus is not a valid evidence timestamp.');
    }
    return {
      id: `${id}-media-${media.asset_id}-${index}`,
      label: momentLabel(timeLabel, media, index, kind),
      posterUri: frame,
      playbackUri: playbackUriForAsset(sourceId, frame, kind, sourceUris),
      ...(focus != null ? { focusTimeSec: focus / 1000 } : {}),
      ...(enableMotion ? { sourceAssetId:sourceId,
        selectedFrameId:chosenFrameId,
        sourceDurationSec:typeof asset?.durationMs === 'number' ? asset.durationMs / 1000 : undefined } : {}),
    };
  });
}

function playbackUriForAsset(
  assetId: string,
  frameUri: string | undefined,
  mediaKind: string | undefined,
  sourceUris?: Record<string, SourceUriEntry>,
): string | undefined {
  const source = sourceUris?.[assetId];
  const kind = source?.media_kind ?? mediaKind;
  if (kind === 'VIDEO' && source?.uri) return source.uri;
  return frameUri ?? source?.uri;
}

function momentLabel(
  timeLabel: string | undefined,
  media: PreviewSelectedMedia | undefined,
  index: number,
  mediaKind: string | undefined,
): string {
  if (index === 0 && timeLabel) {
    return mediaKind === 'VIDEO' ? `${timeLabel} · Motion` : timeLabel;
  }
  if (media?.role === 'HERO' && timeLabel) {
    return mediaKind === 'VIDEO' ? `${timeLabel} · Motion` : timeLabel;
  }
  if (mediaKind === 'VIDEO') {
    return `Moment ${index + 1} · Motion`;
  }
  return `Moment ${index + 1}`;
}

/**
 * Resolve Figma Moments from cloud `hero_asset_id` + `selected_media` only.
 * No round-robin fallback (PRD AI02). VIDEO: poster = evidence JPG; playback = source MP4.
 */
export function applyChapterMediaHints(
  chapters: Chapter[],
  hintsByChapterId: Record<string, ChapterMediaHints>,
  assetIndex: Map<string, AssetFrames>,
  sourceUris?: Record<string, SourceUriEntry>,
  enableMotion = false,
): Chapter[] {
  return chapters.map((ch) => {
    const hints = hintsByChapterId[ch.id];
    // PRD AI02 — never round-robin unrelated bundle frames onto a chapter.
    if (!hints) {
      return ch;
    }

    const selectedHero = hints.selectedMedia?.find((m) => m.role === 'HERO') ??
      hints.selectedMedia?.find((m) => m.asset_id === hints.heroAssetId);
    if (selectedHero && hints.heroAssetId && selectedHero.asset_id !== hints.heroAssetId) {
      throw new Error('Hero asset does not match the selected hero.');
    }
    const heroSource = selectedHero?.source_asset_id ?? selectedHero?.asset_id;
    const heroFrame = selectedHero && heroSource
      ? frameUriForAsset(assetIndex, heroSource,
        hints.heroFrameId ? [hints.heroFrameId] : selectedHero.representative_frame_id
          ? [selectedHero.representative_frame_id] : selectedHero.evidence_frame_ids)
      : hints.heroAssetId ? frameUriForAsset(assetIndex, hints.heroAssetId) : undefined;

    const heroUri = heroFrame;

    // PRD AI02 — only cloud-selected media; never invent Moments from moment_ids
    // or fall back to unrelated bundle frames (allUris / round-robin).
    const selected = hints.selectedMedia?.length ? hints.selectedMedia : [];

    const moments = resolveSelectedMedia(ch.id, selected, assetIndex, sourceUris, hints.timeLabel, enableMotion);
    const highlights = ch.highlights?.map(highlight => {
      const selection = hints.highlights?.find(h => h.id === highlight.id)?.selected_media;
      return selection?.length ? { ...highlight,
        media: resolveSelectedMedia(highlight.id, selection, assetIndex, sourceUris, undefined, enableMotion) } : highlight;
    });

    return {
      ...ch,
      ...memoryOrder(selected, assetIndex, sourceUris),
      ...(highlights ? { highlights } : {}),
      heroUri: heroUri ?? moments[0]?.posterUri,
      // Empty moments → Chapter Detail shows Media unavailable (AI03 honesty).
      moments,
    };
  });
}

export function mediaHintsFromPreviewChapters(
  previewChapters: PreviewChapter[],
): Record<string, ChapterMediaHints> {
  const out: Record<string, ChapterMediaHints> = {};
  for (const ch of previewChapters) {
    out[ch.id] = {
      heroAssetId: ch.hero_asset_id,
      heroFrameId: ch.hero_frame_id,
      selectedMedia: ch.selected_media,
      momentIds: ch.moment_ids ?? [],
      timeLabel: ch.time_label || undefined,
      highlights: ch.highlights,
    };
  }
  return out;
}

async function loadSourceUris(bundleDir: string): Promise<Record<string, SourceUriEntry>> {
  try {
    const raw = await FileSystem.readAsStringAsync(`${bundleDir}source_uris.json`);
    return JSON.parse(raw) as Record<string, SourceUriEntry>;
  } catch {
    return {};
  }
}

/** Load bundle JSON and attach cloud-resolved media onto diary chapters. */
export async function attachChapterMediaFromBundle(
  chapters: Chapter[],
  previewChapters: PreviewChapter[],
  bundleDir: string,
  bundleJsonPath: string,
): Promise<Chapter[]> {
  return (await attachDiaryMediaFromBundle({ chapters, smallMemories: [] },
    { chapters: previewChapters, ahas: [] }, bundleDir, bundleJsonPath)).chapters;
}

/** Attach every visible media reference before the atomic diary/dedupe commit. */
export async function attachDiaryMediaFromBundle(
  mapped: { chapters: Chapter[]; smallMemories: SmallMemory[] },
  preview: { chapters: PreviewChapter[]; ahas: PreviewAha[] },
  bundleDir: string,
  bundleJsonPath: string,
): Promise<{ chapters: Chapter[]; smallMemories: SmallMemory[] }> {
  const raw = await FileSystem.readAsStringAsync(bundleJsonPath);
  const manifest = JSON.parse(raw) as AppLibraryBundle;
  const assets = (manifest.assets ?? []) as BundleAsset[];
  const index = buildBundleAssetUriIndex(bundleDir, assets);
  const sourceUris = await loadSourceUris(bundleDir);
  for (const asset of assets) {
    if (!asset.asset_id) continue;
    const source = sourceUris[asset.asset_id];
    if (source?.uri) source.uri = resolveBundleSourceUri(source.uri, bundleDir);
  }
  const hints = mediaHintsFromPreviewChapters(preview.chapters);
  const useMotion = manifest.bundle_version === 'DIARY_ONE_APP_LIBRARY_BUNDLE_V05';
  const attached = applyChapterMediaHints(mapped.chapters, hints, index, sourceUris, useMotion);
  const smallMemories = mapped.smallMemories.map(memory => {
    const selected = preview.ahas.find(a => a.id === memory.id)?.selected_media ?? [];
    const m = selected[0];
    if (!m) return memory; // Legacy text-only Aha remains readable.
    const posterUri = frameUriForAsset(index, m.source_asset_id ?? m.asset_id,
      m.representative_frame_id ? [m.representative_frame_id] : m.evidence_frame_ids);
    if (!posterUri) throw new Error('Selected small memory frame is unavailable.');
    return { ...memory, posterUri, ...memoryOrder(selected, index, sourceUris) };
  });
  // Resolve the complete selected set before the diary/dedupe transaction commits.
  const uris = new Set([...attached.flatMap((chapter) => [chapter.heroUri,
    ...[...chapter.moments, ...(chapter.highlights?.flatMap(h => h.media ?? []) ?? [])]
      .flatMap(moment => [moment.posterUri, moment.playbackUri])]),
    ...smallMemories.map(m => m.posterUri)].filter((uri): uri is string => Boolean(uri)));
  for (const uri of uris) {
    const info = await FileSystem.getInfoAsync(uri);
    if (!info.exists || info.isDirectory) throw new Error('Selected media is unavailable. Retry the import.');
    const sourceAsset = assets.find(asset => asset.asset_id && sourceUris[asset.asset_id]?.uri === uri);
    const frame = assets.flatMap(asset => asset.frames ?? []).find(frame => `${bundleDir}${frame.relative_path}` === uri);
    const expected = sourceAsset?.original_sha256 ?? frame?.sha256;
    if (!expected || await sha256File(uri) !== expected) {
      throw new Error('Selected media bytes changed. Restore the original media before retrying.');
    }
  }
  // Load the native/Expo-dependent exporter only for the opt-in V05 format.
  // Legacy V03/V04 must not initialize motion modules or change test bindings.
  const liveChapters = useMotion
    ? await (await import('./buildLiveChapterCovers')).buildLiveChapterCovers(attached,bundleDir)
    : attached;
  return { chapters: liveChapters, smallMemories };
}
