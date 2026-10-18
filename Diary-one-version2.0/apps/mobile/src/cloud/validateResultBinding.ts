import { ALGORITHM_LOCK } from '../config/algorithmLock';
import type { AppLibraryBundle } from '../pipeline/bundleTypes';

export type ResultInput = { manifest: AppLibraryBundle; manifestSha256: string };

/** Server performs the full frozen schema; the client independently binds it to its input. */
export function validateResultBinding(result: unknown, input: ResultInput, requireEnvelope: boolean): void {
  if (!result || typeof result !== 'object' || Array.isArray(result)) throw new Error('Invalid result object');
  const row = result as Record<string, unknown>;
  const envelope = row._publish as Record<string, unknown> | undefined;
  if (row.bundle_manifest_sha256 !== input.manifestSha256 || row.session_id !== input.manifest.session.session_id) {
    throw new Error('Result does not match the submitted input');
  }
  if (requireEnvelope && (envelope?.input_bound !== true ||
      envelope.result_contract_sha256 !== ALGORITHM_LOCK.previewContractSha256 ||
      envelope.bundle_manifest_sha256 !== input.manifestSha256 ||
      envelope.bundle_version !== input.manifest.bundle_version)) {
    throw new Error('Missing or incompatible server contract verification');
  }
  const assets = new Map(input.manifest.assets.map((asset) => [asset.asset_id, asset]));
  const frameOwners = new Map<string, unknown>();
  for (const [assetId, asset] of assets) {
    for (const frame of (asset.frames ?? []) as { frame_id: string }[]) {
      if (frameOwners.has(frame.frame_id)) throw new Error('Duplicate input frame');
      frameOwners.set(frame.frame_id, assetId);
    }
  }
  const visible = new Set<string>();
  if (!Array.isArray(row.selected_memory_outcomes)) throw new Error('Missing outcomes');
  for (const outcome of row.selected_memory_outcomes) {
    if (outcome.visibility_state === 'VISIBLE_PREVIEW') {
      const key = `${outcome.memory_type}:${outcome.memory_id}`;
      if (visible.has(key)) throw new Error('Duplicate visible outcome');
      visible.add(key);
    }
  }
  const published = new Set<string>();
  for (const [kind, rows] of [['CHAPTER', row.chapters], ['AHA', row.ahas]] as const) {
    if (!Array.isArray(rows)) throw new Error('Missing memory array');
    for (const memory of rows) {
      if (!memory || typeof memory.id !== 'string' || !memory.id || typeof memory.story !== 'string' ||
          memory.publication_status !== 'STAGED_PREVIEW_VALIDATED') throw new Error('Invalid public memory');
      const key = `${kind}:${memory.id}`;
      if (published.has(key)) throw new Error('Duplicate public memory');
      published.add(key);
      if (!Array.isArray(memory.selected_media) || !memory.selected_media.length) throw new Error('Missing selected media');
      if (!memory.selected_media.some((media: { asset_id: unknown }) => media.asset_id === memory.hero_asset_id)) {
        throw new Error('Hero is not selected');
      }
      for (const media of memory.selected_media) {
        const asset = assets.get(media.asset_id);
        if (!asset || media.source_asset_id !== media.asset_id || media.media_kind !== asset.media_kind ||
            !Array.isArray(media.evidence_frame_ids) || !media.evidence_frame_ids.length ||
            media.evidence_frame_ids.some((id: string) => frameOwners.get(id) !== media.asset_id)) {
          throw new Error('Selected media does not match input lineage');
        }
      }
    }
  }
  if (published.size !== visible.size || [...published].some((key) => !visible.has(key))) {
    throw new Error('Published memories do not match visible outcomes');
  }
  if (row.delivery_state === 'NO_GROUNDED_MEMORY' && published.size) throw new Error('Empty result contains memories');
}
