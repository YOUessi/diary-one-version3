import type { AppLibraryBundle } from '../pipeline/bundleTypes';

type Obj = Record<string, any>;
const obj = (v: unknown): Obj => {
  if (!v || typeof v !== 'object' || Array.isArray(v)) throw new Error('Direct VLM object expected');
  return v as Obj;
};
const arr = (v: unknown): Obj[] => {
  if (!Array.isArray(v)) throw new Error('Direct VLM array expected');
  return v.map(obj);
};
const txt = (v: unknown): v is string => typeof v === 'string' && !!v.trim();
const refs = (value: unknown, known: Set<string>, allowEmpty = false): string[] => {
  if (!Array.isArray(value) || (!allowEmpty && !value.length) || value.some(x => !txt(x))
    || new Set(value).size !== value.length || value.some(x => !known.has(x))) {
    throw new Error('Unknown or duplicate direct VLM frame references');
  }
  return value as string[];
};
function appId(source: string): string {
  const value = source.startsWith('asset_') ? source.slice(6) : source;
  const hex = value.replace(/-/g, '');
  if (/^[0-9a-f]{32}$/i.test(hex)) {
    return [hex.slice(0, 8), hex.slice(8, 12), hex.slice(12, 16), hex.slice(16, 20), hex.slice(20)].join('-').toLowerCase();
  }
  return value;
}

/** BFF checks actual JPEG hashes. Device checks displayed lineage independently. */
export function validateDirectVlmResult(resultValue: unknown, manifest: AppLibraryBundle,
  frameSha256?: Record<string, string>): void {
  const result = obj(resultValue);
  const trace = obj(result.trace);
  if (result.schema_version !== 'DIARY_ONE_DIRECT_VLM_CHAPTER_V01'
    || result.editor_policy !== 'DIRECT_VLM_GLOBAL_EDITOR_V01'
    || trace.pipeline_version !== 'X02_DIRECT_VLM_CHAPTER_V01'
    || result.experimental !== true || result.production_ready !== false
    || result.delivery_state !== 'READY_PRIMARY_COPY'
    || result.coverage_status !== 'INPUT_ALL_FRAMES_SUBMITTED'
    || ![1, 2].includes(trace.model_calls)
    || !Array.isArray(trace.request_ids) || trace.request_ids.length !== trace.model_calls
    || result.unresolved_asset_ids?.length || arr(result.observations).length
    || arr(result.moments).length || arr(result.ahas).length) {
    throw new Error('Invalid direct VLM execution/coverage contract');
  }
  const frameOwners = new Map<string, { source: string; kind: string; duration?: number; timestamp?: number }>();
  const assets = new Map<string, { appId: string; kind: string }>();
  const appIds = new Set<string>();
  for (const raw of manifest.assets) {
    const asset = raw as {
      asset_id: string; media_kind: string; original_duration_ms?: number;
      frames: { frame_id: string; sha256: string; source_timestamp_ms?: number }[];
    };
    const aid = appId(asset.asset_id);
    if (!txt(asset.asset_id) || assets.has(asset.asset_id) || appIds.has(aid)) throw new Error('Duplicate input asset');
    assets.set(asset.asset_id, { appId: aid, kind: asset.media_kind });
    appIds.add(aid);
    for (const frame of asset.frames) {
      if (frameOwners.has(frame.frame_id) || (frameSha256?.[frame.frame_id] && frameSha256[frame.frame_id] !== frame.sha256)) {
        throw new Error('Input JPEG provenance mismatch');
      }
      frameOwners.set(frame.frame_id, {
        source: asset.asset_id, kind: asset.media_kind,
        duration: asset.original_duration_ms, timestamp: frame.source_timestamp_ms,
      });
    }
  }
  if (frameOwners.size === 0 || frameOwners.size > 250) throw new Error('Direct VLM input count invalid');
  const coverage = obj(obj(result.decision_trace).input_coverage);
  if (coverage.frames_submitted !== frameOwners.size || coverage.clips_received !== assets.size) {
    throw new Error('Not all uploaded frames were submitted');
  }
  const known = new Set(frameOwners.keys());
  const excluded = new Set(refs(result.excluded_non_lived_frame_ids, known, true));
  const publicIds = new Set<string>();
  const galleryIds = new Set<string>();
  for (const chapter of arr(result.chapters)) {
    if (!txt(chapter.id) || publicIds.has(chapter.id) || !txt(chapter.title)
      || !txt(chapter.story) || !txt(chapter.hero_frame_id)
      || chapter.publication_status !== 'STAGED_PREVIEW_VALIDATED'
      || !Array.isArray(chapter.tags) || chapter.tags.some((v: unknown) => !txt(v))
      || !Array.isArray(chapter.highlights) || chapter.highlights.length
      || !Array.isArray(chapter.claims) || chapter.claims.length) {
      throw new Error('Invalid direct chapter fields');
    }
    publicIds.add(chapter.id);
    const experience = refs(chapter.experience_frame_ids, known);
    if (experience.some(fid => excluded.has(fid))) throw new Error('Excluded experience');
    const moments = arr(chapter.key_moments);
    if (!moments.length) throw new Error('Missing chapter key moments');
    for (const moment of moments) {
      if (!txt(moment.description) || refs(moment.frame_ids, known).some(fid => excluded.has(fid))) {
        throw new Error('Unsupported key moment');
      }
    }
    const gallery = arr(chapter.selected_media);
    if (!gallery.length || gallery.length > 8) throw new Error('Invalid gallery count');
    const heroes = gallery.filter(m => m.role === 'HERO');
    if (heroes.length !== 1 || heroes[0].representative_frame_id !== chapter.hero_frame_id
      || heroes[0].asset_id !== chapter.hero_asset_id) throw new Error('Hero mismatch');
    for (const media of gallery) {
      if (!['HERO', 'SUPPORT'].includes(media.role)
        || !txt(media.representative_frame_id) || excluded.has(media.representative_frame_id)
        || galleryIds.has(media.representative_frame_id)) throw new Error('Gallery reused/excluded');
      const fid = media.representative_frame_id as string;
      galleryIds.add(fid);
      const expected = frameOwners.get(fid);
      if (!expected || expected.source !== media.source_asset_id || media.asset_id !== assets.get(expected.source)?.appId
        || media.media_kind !== expected.kind || JSON.stringify(media.evidence_frame_ids) !== JSON.stringify([fid])) {
        throw new Error('Gallery image not source-bound');
      }
      if (expected.kind === 'PHOTO') {
        if (media.range_basis !== 'STILL_IMAGE' || media.start_ms !== null || media.end_ms !== null
          || media.focus_pts_ms !== null) throw new Error('Photo fabricated video range');
      } else if (expected.duration && expected.duration > 0) {
        if (media.range_basis !== 'WHOLE_SOURCE_CLIP' || media.start_ms !== 0
          || media.end_ms !== expected.duration || media.focus_pts_ms !== expected.timestamp) {
          throw new Error('Video range mismatch');
        }
      } else if (media.range_basis !== 'EVIDENCE_ONLY_NO_VIDEO_RANGE'
        || media.start_ms !== null || media.end_ms !== null || media.focus_pts_ms !== null) {
        throw new Error('Video range without duration');
      }
    }
  }
  if (!publicIds.size || publicIds.size > 14) throw new Error('Direct chapter count invalid');
  const outcomeIds = new Set<string>();
  for (const outcome of arr(result.selected_memory_outcomes)) {
    if (outcome.memory_type !== 'CHAPTER' || outcome.visibility_state !== 'VISIBLE_PREVIEW'
      || !publicIds.has(outcome.memory_id) || outcomeIds.has(outcome.memory_id)) {
      throw new Error('Public outcome mismatch');
    }
    outcomeIds.add(outcome.memory_id);
  }
  if (outcomeIds.size !== publicIds.size) throw new Error('Unpublished chapter');
}
