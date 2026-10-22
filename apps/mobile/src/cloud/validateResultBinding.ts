import { ALGORITHM_LOCK } from '../config/algorithmLock';
import type { AppLibraryBundle } from '../pipeline/bundleTypes';

type Row = Record<string, unknown>;
export type ResultInput = { manifest: AppLibraryBundle; manifestSha256: string; frameSha256?: Record<string, string>; productIdentities?: Record<string, string> };
const row = (value: unknown): Row => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid contract object');
  return value as Row;
};
const rows = (value: unknown): Row[] => {
  if (!Array.isArray(value)) throw new Error('Missing contract array');
  return value.map(row);
};
const text = (value: unknown): value is string => typeof value === 'string' && !!value.trim();
function ids(value: unknown, empty = false): string[] {
  if (!Array.isArray(value) || (!empty && !value.length) || value.some(v => !text(v)) || new Set(value).size !== value.length) throw new Error('Invalid or duplicate reference list');
  return value as string[];
}
const equal = (a: unknown, b: unknown): boolean => {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((v, i) => equal(v, b[i]));
  if (a && b && typeof a === 'object' && typeof b === 'object' && !Array.isArray(a) && !Array.isArray(b)) {
    const x = a as Row, y = b as Row;
    return Object.keys(x).length === Object.keys(y).length && Object.keys(x).every(k => Object.hasOwn(y, k) && equal(x[k], y[k]));
  }
  return false;
};
/** Same identity projection as the algorithm; source IDs are not necessarily App IDs. */
export function appAssetId(source: string): string {
  const value = source.startsWith('asset_') ? source.slice(6) : source;
  const hex = value.replace(/-/g, '');
  if (/^[0-9a-f]{32}$/i.test(hex)) return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`.toLowerCase();
  return value;
}

/** BFF owns full JSON Schema validation. This independently validates input identity and every displayed reference. */
export function validateResultBinding(value: unknown, input: ResultInput, requireEnvelope: boolean): void {
  const result = row(value);
  const schema = String(result.schema_version);
  const contracts = ALGORITHM_LOCK.resultContractSha256 as Record<string, string>;
  const contract = contracts[schema];
  if (!contract) throw new Error('Unsupported result contract');
  if (!/^[a-f0-9]{64}$/.test(input.manifestSha256) || !text(input.manifest.session?.session_id)
    || result.bundle_manifest_sha256 !== input.manifestSha256 || result.session_id !== input.manifest.session.session_id) {
    throw new Error('Cloud result belongs to different evidence or session. Retry the saved cloud job.');
  }
  if (requireEnvelope || result._publish !== undefined) {
    const envelope = row(result._publish);
    if (envelope.input_bound !== true || envelope.result_contract_version !== ALGORITHM_LOCK.resultContractVersion
      || envelope.result_contract_sha256 !== contract || envelope.bundle_manifest_sha256 !== input.manifestSha256
      || envelope.session_id !== result.session_id || envelope.bundle_version !== input.manifest.bundle_version) {
      throw new Error('Cloud server has not verified this input contract. Update the service, then retry the saved job.');
    }
  }
  const product = schema === ALGORITHM_LOCK.productPreviewSchema;
  const trace = row(result.trace);
  const decision = row(result.decision_trace);
  if (result.experimental !== true || result.production_ready !== false || !text(trace.pipeline_version)
    || !Array.isArray(trace.stage_metrics) || !text(trace.provider) || !text(trace.model)) throw new Error('Incomplete result policy markers');
  let productVersion = 0;
  if (product) {
    const match = /^EXPERIENCE_HIGHLIGHTS_NATURAL_COPY_V0([1-7])$/.exec(String(result.editor_policy));
    productVersion = match ? Number(match[1]) : 0;
    if (!productVersion || trace.pipeline_version !== `X02_PRODUCT_EDITOR_V0${productVersion}`
      || !Object.hasOwn(decision, 'fact_coverage') || !Object.hasOwn(decision, 'semantic_review')
      || !Object.hasOwn(decision, 'prompt_sha256')) throw new Error('Inconsistent product policy markers');
    if (productVersion < 6 && rows(result.chapters).some(c => Object.hasOwn(c, 'selection_focus') || Object.hasOwn(c, 'hero_frame_id'))) throw new Error('Legacy policy cannot declare the newer image contract');
  } else if (trace.pipeline_version !== 'X02_STAGED_REAL_MEDIA_PREVIEW_V04_1'
    || result.validation_scope !== 'STAGED_PREVIEW_ONLY' || result.leaderboard_eligible !== false
    || !text(result.chapter_media_policy_version) || !text(result.storyline_contract_version)) {
    throw new Error('Incomplete V04.1 result markers');
  }
  if (!(product ? ['COMPLETE', 'INCOMPLETE'] : ['COMPLETE', 'PARTIAL_UNRESOLVED']).includes(String(result.coverage_status))) throw new Error('Missing coverage marker');
  const assets = new Map<string, Row>(); const appIds = new Set<string>(); const owners = new Map<string, string>();
  for (const asset of input.manifest.assets) {
    const source = asset.asset_id;
    if (!text(source) || assets.has(source) || appIds.has(appAssetId(source)) || !['PHOTO', 'VIDEO'].includes(String(asset.media_kind))) throw new Error('Ambiguous input asset identity');
    assets.set(source, asset); appIds.add(appAssetId(source));
    for (const frame of rows(asset.frames)) {
      if (!text(frame.frame_id) || owners.has(frame.frame_id) || !text(frame.sha256)
        || !/^[a-f0-9]{64}$/.test(String(frame.sha256))
        || (input.frameSha256 !== undefined && input.frameSha256[frame.frame_id] !== frame.sha256)) throw new Error('Unverified or duplicate input frame bytes');
      owners.set(frame.frame_id, source);
    }
  }
  if (!assets.size || !owners.size) throw new Error('Missing submitted evidence');
  const unresolved = ids(result.unresolved_asset_ids, true);
  if (unresolved.some(id => !assets.has(id) && !appIds.has(id))
    || (result.coverage_status === 'COMPLETE' && unresolved.length)
    || (result.coverage_status === 'PARTIAL_UNRESOLVED' && !unresolved.length)) throw new Error('Inconsistent unresolved input markers');
  const checkFrames = (refs: unknown, source: string, empty = false) => {
    const list = ids(refs, empty);
    if (list.some(id => owners.get(id) !== source)) throw new Error('Evidence frame belongs to another source asset');
    return list;
  };
  const observations = new Map<string, Row>(); const observedSources = new Set<string>(); const observedFacts = new Map<string, { fact: Row; source: string }>();
  for (const obs of rows(result.observations)) {
    const source = obs.source_asset_id;
    if (!text(obs.id) || observations.has(obs.id) || !text(source) || !assets.has(source) || observedSources.has(source)
      || obs.asset_id !== appAssetId(source) || obs.media_kind !== assets.get(source)!.media_kind) throw new Error('Invalid observation input lineage');
    observations.set(obs.id, obs); observedSources.add(source);
    checkFrames(obs.evidence_frame_ids, source, true);
    for (const fact of rows(obs.facts)) {
      if (!text(fact.fact_id) || observedFacts.has(fact.fact_id)) throw new Error('Duplicate observation fact');
      checkFrames(fact.evidence_frame_ids, source);
      observedFacts.set(fact.fact_id, { fact, source });
    }
  }
  for (const source of assets.keys()) if (!observedSources.has(source) && !unresolved.includes(source) && !unresolved.includes(appAssetId(source))) throw new Error('Input asset omitted from result coverage');
  const moments = new Map<string, Set<string>>();
  if (product && rows(result.moments).length) throw new Error('Product moments must be published only as chapters or ahas');
  if (!product) for (const moment of rows(result.moments)) {
    if (!text(moment.id) || moments.has(moment.id)) throw new Error('Duplicate moment');
    const sources = new Set(ids(moment.observation_ids).map(id => {
      const observation = observations.get(id); if (!observation) throw new Error('Moment references an unknown observation');
      return String(observation.source_asset_id);
    }));
    if (!equal([...sources].sort(), ids(moment.source_asset_ids).sort()) || !equal([...sources].map(appAssetId).sort(), ids(moment.asset_ids).sort())) throw new Error('Moment source lineage mismatch');
    moments.set(moment.id, sources);
  }
  const verified: Row = productVersion >= 4 ? row(decision.verified_facts) : {};
  const internalAssets = new Map(input.manifest.assets.map((asset, index) => [asset.asset_id, `V${String(index + 1).padStart(3, '0')}`]));
  if (product && productVersion <= 3) {
    // Early Product runs used this deterministic S04 catalog before visual review existed.
    for (const observation of observations.values()) {
      if (!['OBSERVED', 'PARTIAL'].includes(String(observation.status))) continue;
      const source = String(observation.source_asset_id);
      for (const fact of rows(observation.facts)) {
        if (!['STRONG', 'MODERATE'].includes(String(fact.support_grade))) continue;
        const frames = checkFrames(fact.evidence_frame_ids, source);
        const id = `F${String(Object.keys(verified).length + 1).padStart(3, '0')}`;
        verified[id] = { ...fact, id, asset_id: internalAssets.get(source), source_asset_id: source,
          observation_id: observation.id, frame_pts_ms: frames.map(fid => rows(assets.get(source)!.frames).find(f => f.frame_id === fid)!.source_timestamp_ms) };
      }
    }
  }
  for (const [id, value] of Object.entries(verified)) {
    const fact = row(value), source = String(fact.source_asset_id);
    const original = observedFacts.get(String(fact.fact_id));
    if (fact.id !== id || (productVersion >= 4 && fact.visual_reviewed !== true) || !original || original.source !== source
      || fact.asset_id !== internalAssets.get(source) || observations.get(String(fact.observation_id))?.source_asset_id !== source) throw new Error('Verified fact input lineage mismatch');
    checkFrames(fact.evidence_frame_ids, source);
  }
  const structureChapters = new Map<string, Row>(); const structureMoments = new Map<string, Row>();
  if (product) {
    const structure = row(decision.selected_structure);
    for (const chapter of rows(structure.chapters)) {
      const publicId = input.productIdentities?.[`chapter:${chapter.id}`];
      if (!publicId || structureChapters.has(publicId)) throw new Error('Missing or duplicate structural chapter identity');
      for (const id of ids(chapter.fact_ids)) if (!verified[id]) throw new Error('Unknown structural chapter fact');
      structureChapters.set(publicId, chapter);
    }
    for (const moment of rows(structure.moments)) {
      const kind = moment.parent_chapter_id === null ? 'aha' : 'highlight';
      const publicId = input.productIdentities?.[`${kind}:${moment.id}`];
      if (!publicId || structureMoments.has(publicId)) throw new Error('Missing or duplicate structural moment identity');
      structureMoments.set(publicId, moment);
    }
  }
  const allMemoryIds = new Set<string>(); const published = new Set<string>();
  function claimMap(memory: Row, allowedSources?: Set<string>): Map<string, Row> {
    const claims = new Map<string, Row>();
    for (const fact of rows(memory.claims)) {
      const id = product ? fact.id : fact.fact_id;
      if (!text(id) || claims.has(id)) throw new Error('Missing or duplicate memory claim');
      let source: string;
      if (product) {
        if (!text(fact.source_asset_id) || !assets.has(fact.source_asset_id)) throw new Error('Unknown claim source');
        source = fact.source_asset_id;
        if (!equal(fact, verified[id])) throw new Error('Claim differs from its versioned evidence catalog');
        if (!text(fact.observation_id) || observations.get(fact.observation_id)?.source_asset_id !== source) throw new Error('Claim observation lineage mismatch');
      } else {
        const observed = observedFacts.get(id);
        if (!observed || !equal(fact, observed.fact)) throw new Error('Claim differs from observation evidence');
        source = observed.source;
      }
      if (allowedSources && !allowedSources.has(source)) throw new Error('Claim belongs to another memory');
      checkFrames(fact.evidence_frame_ids, source); claims.set(id, fact);
    }
    if (!claims.size) throw new Error('Memory has no grounded claims');
    return claims;
  }
  function checkMemory(memory: Row, kind: 'CHAPTER' | 'AHA' | 'HIGHLIGHT', parent?: Row) {
    if (!text(memory.id) || allMemoryIds.has(memory.id) || !text(memory.story)) throw new Error('Invalid or duplicate public memory');
    allMemoryIds.add(memory.id);
    if (kind !== 'HIGHLIGHT') {
      if (memory.publication_status !== 'STAGED_PREVIEW_VALIDATED') throw new Error('Unpublished memory in public result');
      published.add(`${kind}:${memory.id}`);
    } else if (memory.parent_chapter_id !== parent?.id) throw new Error('Highlight belongs to another chapter');
    const allowedSources = !product ? new Set(ids(memory.moment_ids).flatMap(id => {
      const source = moments.get(id); if (!source) throw new Error('Memory references unknown moment'); return [...source];
    })) : undefined;
    const claims = claimMap(memory, allowedSources);
    let chapterFacts = claims;
    if (product) {
      if (kind === 'CHAPTER') {
        const structure = structureChapters.get(String(memory.id));
        if (!structure) throw new Error('Chapter is missing its structural identity');
        chapterFacts = new Map(ids(structure.fact_ids).map(id => [id, row(verified[id])]));
        for (const id of claims.keys()) if (!chapterFacts.has(id)) throw new Error('Copy claim belongs to another structural chapter');
      } else {
        const structure = structureMoments.get(String(memory.id));
        const expectedParent = parent ? structureChapters.get(String(parent.id)) : undefined;
        if (!structure || (parent ? structure.parent_chapter_id !== expectedParent?.id : structure.parent_chapter_id !== null)
          || !claims.has(String(structure.fact_id)) || claims.size !== 1) throw new Error('Moment belongs to another structural chapter or fact');
        if (expectedParent && !ids(expectedParent.fact_ids).includes(String(structure.fact_id))) throw new Error('Highlight fact is outside its parent structure');
      }
    }
    const media = rows(memory.selected_media);
    if (!media.length || media.length > (kind === 'CHAPTER' ? 5 : 1) || (!product && kind === 'CHAPTER' && media.length < 3)) throw new Error('Invalid selected media count');
    const selected = new Set<string>();
    for (const m of media) {
      const source = m.source_asset_id;
      if (!text(source) || !assets.has(source) || selected.has(source) || m.asset_id !== appAssetId(source)
        || m.media_kind !== assets.get(source)!.media_kind || (allowedSources && !allowedSources.has(source))) throw new Error('Selected media input identity mismatch');
      selected.add(source);
      const frames = checkFrames(m.evidence_frame_ids, source);
      if (!product && (!text(m.observation_id) || observations.get(m.observation_id)?.source_asset_id !== source)) throw new Error('Selected observation mismatch');
      if (product) {
        const matching = [...chapterFacts.values()].filter(f => f.source_asset_id === source);
        if (!matching.length || frames.some(f => !matching.some(c => (c.evidence_frame_ids as string[]).includes(f)))) throw new Error('Selected frame is not grounded in memory claims');
        if (m.media_kind === 'PHOTO') {
          if ((productVersion >= 6 && m.range_basis !== 'STILL_IMAGE') || m.start_ms !== null || m.end_ms !== null
            || (productVersion >= 4 ? m.focus_pts_ms !== null : m.focus_pts_ms != null)) throw new Error('Photo cannot claim a video time range');
        } else {
          const duration = assets.get(source)!.original_duration_ms;
          if (!Number.isInteger(m.start_ms) || !Number.isInteger(m.end_ms) || Number(m.start_ms) < 0 || Number(m.end_ms) <= Number(m.start_ms)
            || !Number.isInteger(duration) || Number(duration) <= 0 || Number(m.end_ms) > Number(duration)
            || !['WHOLE_SOURCE_CLIP', 'EVIDENCE_CONTEXT_WINDOW_NOT_EVENT_BOUNDARIES'].includes(String(m.range_basis))) throw new Error('Video range exceeds source bounds');
          if (m.range_basis === 'WHOLE_SOURCE_CLIP' && (m.start_ms !== 0 || m.end_ms !== duration)) throw new Error('Whole-clip range differs from input duration');
          if ((productVersion >= 4 ? m.focus_pts_ms !== null : m.focus_pts_ms != null) && (!Number.isInteger(m.focus_pts_ms) || Number(m.focus_pts_ms) < Number(m.start_ms)
            || Number(m.focus_pts_ms) > Number(m.end_ms) || !rows(assets.get(source)!.frames).some(f => frames.includes(String(f.frame_id)) && f.source_timestamp_ms === m.focus_pts_ms))) throw new Error('Focus timestamp is not an evidence frame in the selected range');
        }
        if (kind === 'CHAPTER' && productVersion >= 6) {
          if (!text(m.representative_frame_id) || m.representative_frame_id !== frames[0] || !text(m.selection_reason)
            || !['PRIMARY', 'SUPPORT', 'DETAIL', 'CONTEXT'].includes(String(m.selection_role))) throw new Error('Invalid representative image');
          for (const id of ids(m.selection_fact_ids)) {
            const fact = claims.get(id);
            if (!fact || fact.source_asset_id !== source || !(fact.evidence_frame_ids as string[]).includes(m.representative_frame_id)) throw new Error('Representative image is not supported by its selection facts');
          }
        }
      }
    }
    if (kind === 'CHAPTER') {
      const heroes = media.filter(m => m.role === 'HERO');
      if (heroes.length !== 1 || heroes[0].asset_id !== memory.hero_asset_id) throw new Error('Cover is not its selected hero');
      if (product) {
        if (!text(memory.preview_story)) throw new Error('Missing product chapter preview');
        for (const sentence of rows(memory.sentence_claims)) for (const id of ids(sentence.fact_ids)) if (!claims.has(id)) throw new Error('Sentence references another chapter claim');
        if (productVersion >= 6) {
          if (memory.hero_frame_id !== heroes[0].representative_frame_id || !text(memory.hero_reason)) throw new Error('Cover frame differs from selected representative');
          for (const id of ids(row(memory.selection_focus).fact_ids)) if (!chapterFacts.has(id)) throw new Error('Selection focus references another chapter');
        }
        const highlights = rows(memory.highlights);
        if (highlights.length > 2) throw new Error('Too many chapter highlights');
        for (const highlight of highlights) checkMemory(highlight, 'HIGHLIGHT', memory);
      }
    }
  }
  for (const chapter of rows(result.chapters)) checkMemory(chapter, 'CHAPTER');
  for (const aha of rows(result.ahas)) checkMemory(aha, 'AHA');
  const seenOutcomes = new Set<string>(); const visible = new Set<string>();
  for (const outcome of rows(result.selected_memory_outcomes)) {
    if (!text(outcome.memory_id) || !['CHAPTER', 'AHA'].includes(String(outcome.memory_type)) || !['VISIBLE_PREVIEW', 'DIAGNOSTIC_ONLY'].includes(String(outcome.visibility_state))) throw new Error('Invalid publication outcome');
    const key = `${outcome.memory_type}:${outcome.memory_id}`;
    if (seenOutcomes.has(key) || allMemoryIds.has(String(outcome.memory_id)) && !published.has(key)) throw new Error('Duplicate or nested-highlight publication outcome');
    seenOutcomes.add(key); if (outcome.visibility_state === 'VISIBLE_PREVIEW') visible.add(key);
  }
  if (visible.size !== published.size || [...published].some(key => !visible.has(key))) throw new Error('Published memories do not match visible outcomes');
  if (productVersion >= 7) {
    const structuralOutcomes = new Set([...structureChapters.keys()].map(id => `CHAPTER:${id}`));
    for (const [id, moment] of structureMoments) if (moment.parent_chapter_id === null) structuralOutcomes.add(`AHA:${id}`);
    if (seenOutcomes.size !== structuralOutcomes.size || [...seenOutcomes].some(key => !structuralOutcomes.has(key))) throw new Error('Outcomes do not match selected structure');
  }
  if (result.delivery_state === 'NO_GROUNDED_MEMORY' && (published.size || seenOutcomes.size || result.semantic_day_state !== 'EMPTY_DAY')) throw new Error('Inconsistent honest-empty result');
}
