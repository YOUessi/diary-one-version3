import * as FileSystem from 'expo-file-system/legacy';
import type { Chapter } from '../model';
import type { PreviewChapter, PreviewSelectedMedia } from '../cloud/types';
import type { AppLibraryBundle } from './bundleTypes';
import { resolveBundleSourceUri } from './localMediaPaths';
import { sha256File } from './sha256File';

type FrameRef = {
  relative_path?: string;
  frame_id?: string;
  sha256?: string;
};

type BundleAsset = {
  asset_id?: string;
  media_kind?: string;
  original_sha256?: string;
  frames?: FrameRef[];
};

export type SourceUriEntry = { uri: string; media_kind: 'PHOTO' | 'VIDEO' | string };

export type ChapterMediaHints = {
  heroAssetId?: string;
  heroFrameId?: string;
  selectedMedia?: PreviewSelectedMedia[];
  momentIds: string[];
  timeLabel?: string;
};

/** Build asset_id → ordered local file URIs from an App Library Bundle on disk. */
export function buildBundleAssetUriIndex(
  bundleDir: string,
  assets: BundleAsset[],
): Map<string, { uris: string[]; frameIds: string[]; mediaKind?: string }> {
  const index = new Map<string, { uris: string[]; frameIds: string[]; mediaKind?: string }>();
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
      index.set(asset.asset_id, { uris, frameIds, mediaKind: asset.media_kind });
    }
  }
  return index;
}

function frameUriForAsset(
  index: Map<string, { uris: string[]; frameIds: string[]; mediaKind?: string }>,
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
  assetIndex: Map<string, { uris: string[]; frameIds: string[]; mediaKind?: string }>,
  sourceUris?: Record<string, SourceUriEntry>,
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

    const moments = selected
      .map((media, index) => {
        const sourceId = media.source_asset_id ?? media.asset_id;
        const frame =
          frameUriForAsset(assetIndex, sourceId,
            media.representative_frame_id ? [media.representative_frame_id] : media.evidence_frame_ids);
        if (!frame) throw new Error('Selected evidence frame is unavailable.');
        const kind =
          sourceUris?.[sourceId]?.media_kind ??
          assetIndex.get(sourceId)?.mediaKind;
        if (kind === 'VIDEO' && !sourceUris?.[sourceId]?.uri) {
          throw new Error('Selected video source is unavailable.');
        }
        const playback = playbackUriForAsset(sourceId, frame, kind, sourceUris);
        return {
          id: `${ch.id}-media-${media.asset_id}-${index}`,
          label: momentLabel(hints.timeLabel, media, index, kind),
          posterUri: frame,
          playbackUri: playback,
        };
      })
      .filter((m): m is NonNullable<typeof m> => m != null);

    return {
      ...ch,
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
  const hints = mediaHintsFromPreviewChapters(previewChapters);
  const attached = applyChapterMediaHints(chapters, hints, index, sourceUris);
  // Resolve the complete selected set before the diary/dedupe transaction commits.
  const uris = new Set(attached.flatMap((chapter) => [chapter.heroUri,
    ...chapter.moments.flatMap((moment) => [moment.posterUri, moment.playbackUri])])
    .filter((uri): uri is string => Boolean(uri)));
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
  return attached;
}
