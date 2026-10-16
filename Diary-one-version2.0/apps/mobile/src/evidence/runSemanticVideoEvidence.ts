import * as FileSystem from 'expo-file-system/legacy';
import { measureProbeQualityFromUri } from './probeQuality';
import { planProbeTimestampsMs } from './probePlan';
import { resolveSemanticAnalyzer, describeAnalyzer } from './resolveSemanticAnalyzer';
import { extractVideoFramesAtTimes } from './nativeVisionAnalyzer';
import { routeSemanticClip } from './semanticRouter';
import {
  canonicalOffsetForRole,
  sampleRoleForIndex,
  selectFrameTimestampsMs,
  frameLevelLabel,
} from './selectFrames';
import { setLastSemanticRouteAudit } from './lastSemanticRoute';
import {
  DEFAULT_SEMANTIC_ROUTING_PROFILE,
  routingProfileForModelId,
  type SemanticRouteAudit,
  type SemanticRoutingProfile,
} from './types';
import type { SpatialTransform } from '../pipeline/bundleTypes';
import { writeNormalizedFrame, EVIDENCE_FRAME } from '../pipeline/evidenceNormalize';
import { sha256File } from '../pipeline/sha256File';
import { createFallbackSemanticAnalyzer } from './fallbackAnalyzer';
import type { SemanticAnalyzer } from './semanticAnalyzer';

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

export type SemanticVideoBundleResult = {
  frames: FrameRow[];
  evidence_sampling_profile: string;
  evidence_window_count: number;
  semanticRoute: SemanticRouteAudit;
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

export async function buildSemanticVideoEvidence(
  params: {
    assetId: string;
    localVideoUri: string;
    durationMs: number;
    bundleDir: string;
    spatial: SpatialTransform;
    sourceW?: number;
    sourceH?: number;
    profile?: SemanticRoutingProfile;
  },
): Promise<SemanticVideoBundleResult> {
  const probeProfile = params.profile ?? DEFAULT_SEMANTIC_ROUTING_PROFILE;
  let analyzer: SemanticAnalyzer = resolveSemanticAnalyzer();
  const timestamps = planProbeTimestampsMs(params.durationMs, probeProfile);

  const probeDir = `${params.bundleDir}probes_${params.assetId}/`;
  const probeThumbs = await extractVideoFramesAtTimes(
    params.localVideoUri,
    timestamps,
    probeDir,
  );

  let analyzeResults;
  try {
    if (analyzer.analyzeImageUris) {
      analyzeResults = await analyzer.analyzeImageUris(probeThumbs.map((p) => p.uri));
    } else {
      analyzeResults = await Promise.all(probeThumbs.map((p) => analyzer.analyzeImageUri(p.uri)));
    }
  } catch {
    // BFF MobileCLIP not ready → degraded Expo fallback (still completes cloud path)
    analyzer = createFallbackSemanticAnalyzer();
    if (analyzer.analyzeImageUris) {
      analyzeResults = await analyzer.analyzeImageUris(probeThumbs.map((p) => p.uri));
    } else {
      analyzeResults = await Promise.all(probeThumbs.map((p) => analyzer.analyzeImageUri(p.uri)));
    }
  }

  const hasLabels = (analyzeResults[0]?.classifications?.length ?? 0) > 0;
  const profile =
    params.profile ??
    routingProfileForModelId(analyzeResults[0]?.modelId, hasLabels);

  const probes = await Promise.all(
    probeThumbs.map(async (thumb, index) => {
      const quality = await measureProbeQualityFromUri(thumb.uri, profile);
      const analyzed = analyzeResults[index];
      return {
        requestedMs: thumb.requestedMs,
        actualPtsMs: thumb.actualPtsMs,
        embedding: {
          vector: analyzed.vector,
          classifications: analyzed.classifications,
        },
        meanLuma: quality.meanLuma,
        darkPixelRatio: quality.darkPixelRatio,
        sharpness: quality.sharpness,
        eligibleForSelection: quality.eligibleForSelection,
        qualityReasonCodes: quality.qualityReasonCodes,
      };
    }),
  );

  const decision = routeSemanticClip({
    profile,
    modelId: analyzeResults[0]?.modelId ?? profile.modelId,
    analyzerDegraded: analyzer.degraded || analyzeResults.some((r) => r.degraded),
    probes,
  });

  const selectedMs = selectFrameTimestampsMs(decision);
  const frameCount = decision.targetFrameCount;
  const selectedDir = `${params.bundleDir}selected_${params.assetId}/`;
  const selectedThumbs = await extractVideoFramesAtTimes(
    params.localVideoUri,
    selectedMs,
    selectedDir,
  );
  const frames: FrameRow[] = [];

  for (let fi = 0; fi < selectedThumbs.length; fi++) {
    const thumb = selectedThumbs[fi];
    const source_timestamp_ms = Math.round(thumb.actualPtsMs);
    const role = sampleRoleForIndex(fi, selectedThumbs.length);
    const rel = `frames/${params.assetId}_${fi}.jpg`;
    frames.push(
      await frameFromUri(thumb.uri, rel, params.bundleDir, params.spatial, params.sourceW, params.sourceH, {
        frame_id: `${params.assetId}-f${fi}`,
        window_index: fi,
        window_count: frameCount as FrameRow['window_count'],
        sample_role: role,
        canonical_offset_ms: canonicalOffsetForRole(role),
        source_timestamp_ms,
      }),
    );
  }

  const audit: SemanticRouteAudit = {
    ...decision,
    profileId: profile.profileId,
    durationMs: params.durationMs,
    analyzerKind: analyzer.kind,
  };
  audit.degradationCodes = [
    ...audit.degradationCodes,
    `ANALYZER=${describeAnalyzer(analyzer)}`,
  ];

  const sidecarPath = `${params.bundleDir}semantic_route_${params.assetId}.json`;
  await FileSystem.writeAsStringAsync(sidecarPath, JSON.stringify(audit, null, 2));
  setLastSemanticRouteAudit(audit);

  return {
    frames,
    evidence_sampling_profile: frameLevelLabel(frameCount),
    evidence_window_count: frameCount,
    semanticRoute: audit,
  };
}
