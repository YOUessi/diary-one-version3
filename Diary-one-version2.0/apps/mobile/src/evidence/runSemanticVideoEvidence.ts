import * as FileSystem from 'expo-file-system/legacy';
import { planProbeTimestampsMs } from './probePlan';
import { extractVideoFramesAtTimes, normalizeVideoEvidenceFrame } from './nativeVideoDecoder';
import { routeSemanticClip } from './semanticRouter';
import { canonicalOffsetForRole, sampleRoleForIndex } from './selectFrames';
import { setLastSemanticRouteAudit } from './lastSemanticRoute';
import { MOBILECLIP_FP16_V07_PROFILE, type EvidenceFrameLevel, type SemanticRouteAudit } from './types';
import type { SpatialTransform } from '../pipeline/bundleTypes';
import { sha256File } from '../pipeline/sha256File';
import { analyzeMobileClip, MODEL_ID, MODEL_SHA256, PROMPT_SHA256, SAMPLING_PROFILE } from './mobileclip/analyzer';
import { coverageV07 } from './mobileclip/coverageV07';
import { balancedVideoWindows } from './videoWindows';
import { assertEvidenceBuildCurrent, type EvidenceBuildControl } from './buildControl';

export type FrameRow = {
  frame_id: string; window_index: number; window_count: number;
  sample_role: 'WINDOW_EARLY' | 'WINDOW_MIDDLE' | 'WINDOW_LATE';
  canonical_offset_ms: 1500 | 4500 | 7500; source_timestamp_ms: number;
  relative_path: string; sha256: string; width: 768; height: 1024;
  spatial_transform: SpatialTransform;
};
export type SemanticVideoBundleResult = {
  frames: FrameRow[]; evidence_sampling_profile: string; evidence_window_count: number;
  semanticRoute: SemanticRouteAudit;
};

/** One bounded optimizer per <=10s window. Reuse the exact probe JPEG selected. */
export async function buildSemanticVideoEvidence(params: {
  assetId: string; localVideoUri: string; durationMs: number; bundleDir: string;
  spatial: SpatialTransform; sourceW?: number; sourceH?: number;
} & EvidenceBuildControl): Promise<SemanticVideoBundleResult> {
  assertEvidenceBuildCurrent(params);
  if (!Number.isFinite(params.durationMs) || params.durationMs <= 0 || params.durationMs > 120_000) {
    throw new Error('当前端上抽帧支持最长 120 秒的视频，请先分段。');
  }
  const duration = Math.round(params.durationMs);
  if (duration < 1 || params.spatial !== 'ASPECT_FIT_LETTERBOX') throw new Error('MobileCLIP FP16 v07 requires V04 aspect-fit evidence.');
  const ranges = balancedVideoWindows(duration);
  const windows = ranges.length;
  const frames: FrameRow[] = [], audits: Record<string, unknown>[] = [];
  let lastAudit: SemanticRouteAudit | undefined;
  for (let window = 0; window < windows; window++) {
    assertEvidenceBuildCurrent(params);
    const start = ranges[window].startMs, length = ranges[window].endMs - start;
    const requested = planProbeTimestampsMs(length, MOBILECLIP_FP16_V07_PROFILE).map(t => t + start);
    const decoded = await extractVideoFramesAtTimes(params.localVideoUri, requested, `${params.bundleDir}probes_${params.assetId}_${window}/`, [start, start + length]);
    assertEvidenceBuildCurrent(params);
    // A decoder may map the final request to an already decoded PTS. Never count it twice.
    const seen = new Set<number>();
    const thumbs = decoded.filter(frame => {
      const pts = Math.round(frame.actualPtsMs);
      if (!Number.isFinite(pts) || pts < start || pts >= start + length) {
        throw new Error(`Video decoder timestamp ${frame.actualPtsMs}ms is outside [${start}, ${start + length})ms for request ${frame.requestedMs}ms`);
      }
      if (seen.has(pts)) return false;
      seen.add(pts); return true;
    }).sort((a, b) => a.actualPtsMs - b.actualPtsMs);
    const analyzed = await analyzeMobileClip(thumbs.map(t => t.uri), { signal: params.signal, assertCurrent: params.assertCurrent });
    assertEvidenceBuildCurrent(params);
    const probes = thumbs.map((thumb, i) => ({ requestedMs: thumb.requestedMs,
      actualPtsMs: Math.round(thumb.actualPtsMs), embedding: analyzed[i], ...analyzed[i].quality }));
    const eligible = probes.filter(p => p.eligibleForSelection);
    if (!eligible.length) throw new Error(`视频第 ${window + 1} 段没有可用画面，请检查原视频。`);
    const baseline = routeSemanticClip({ profile: MOBILECLIP_FP16_V07_PROFILE,
      modelId: MODEL_ID, analyzerDegraded: false, probes });
    let selected = baseline.selectedTimestampsMs;
    let coverage: ReturnType<typeof coverageV07> | null = null;
    // Same v07 applicability boundary: a FIXED_10 baseline is preserved.
    if (selected.length >= 1 && selected.length <= 5) {
      const labels = analyzed[0].fullClassifications.map(c => c.identifier).sort();
      coverage = coverageV07({ points: eligible.map(p => p.actualPtsMs),
        vectors: eligible.map(p => p.embedding.vector), baseline: selected,
        scores: eligible.map(p => labels.map(label => p.embedding.fullClassifications.find(c => c.identifier === label)!.confidence)) });
      selected = coverage.anchors;
    }
    if (!selected.length || new Set(selected).size !== selected.length) throw new Error('Invalid MobileCLIP frame selection');
    const count = selected.length as EvidenceFrameLevel;
    lastAudit = { ...baseline, targetFrameCount: count, selectedTimestampsMs: selected,
      recommendedAnchorMs: { ...baseline.recommendedAnchorMs, [String(count)]: selected },
      profileId: SAMPLING_PROFILE, durationMs: length, analyzerKind: 'mobileclip_onnx',
      reasonCodes: [...baseline.reasonCodes, coverage ? `V07_${coverage.reason}` : 'V07_PRESERVE_FIXED_10'],
    };
    for (let i = 0; i < selected.length; i++) {
      assertEvidenceBuildCurrent(params);
      const thumb = thumbs.find(t => Math.round(t.actualPtsMs) === selected[i]);
      if (!thumb) throw new Error('Selected frame is missing from decoded probes');
      const role = sampleRoleForIndex(i, selected.length);
      const relative = `frames/${params.assetId}_w${window}_${i}.jpg`;
      await normalizeVideoEvidenceFrame(thumb.uri, `${params.bundleDir}${relative}`);
      assertEvidenceBuildCurrent(params);
      const sha256 = await sha256File(`${params.bundleDir}${relative}`);
      assertEvidenceBuildCurrent(params);
      frames.push({ frame_id: `${params.assetId}-w${window}-f${i}`, window_index: window,
        window_count: windows, sample_role: role, canonical_offset_ms: canonicalOffsetForRole(role),
        source_timestamp_ms: selected[i], relative_path: relative,
        sha256, width: 768, height: 1024, spatial_transform: params.spatial });
    }
    audits.push({ startMs: start, endMs: start + length, windowLayout: 'BALANCED_MAX_10S_V1', modelSha256: MODEL_SHA256,
      promptSha256: PROMPT_SHA256, inference: 'ONNX_RUNTIME_RN_CPU_FP16_INTERNAL_FP32_IO',
      baselinePolicy: 'PHONE_SEMANTIC_ROUTER_WITH_ENDPOINT_V05', coverage,
      // Phone intake does not implement desktop session budgets/manual protections.
      parityScope: 'V07_OPTIMIZER_NOT_DESKTOP_SESSION_ROUTER', ...lastAudit });
  }
  if (!lastAudit) throw new Error('No video windows');
  assertEvidenceBuildCurrent(params);
  const auditPath = `${params.bundleDir}semantic_route_${params.assetId}.json`;
  try {
    await FileSystem.writeAsStringAsync(auditPath, JSON.stringify({
      schema: 'MOBILECLIP_S0_FP16_V07_PHONE_RUN_V1', durationMs: duration, windows: audits,
    }, null, 2));
    assertEvidenceBuildCurrent(params);
  } catch (error) {
    try { await FileSystem.deleteAsync(auditPath, { idempotent: true }); } catch { /* Preserve the original failure. */ }
    throw error;
  }
  setLastSemanticRouteAudit(lastAudit);
  return { frames, evidence_sampling_profile: SAMPLING_PROFILE, evidence_window_count: windows, semanticRoute: lastAudit };
}
