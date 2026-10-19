/** MobileCLIP evidence routing. The fixed FP16 v07 profile is the active phone path. */

export type SemanticClassification = {
  identifier: string;
  confidence: number;
};

export type SemanticEmbedding = {
  vector: number[];
  fullClassifications?: SemanticClassification[];
  classifications: SemanticClassification[];
};

export type SemanticProbePoint = {
  ordinal: number;
  requestedMs: number;
  actualPtsMs: number;
  classifications: SemanticClassification[];
  meanLuma: number | null;
  darkPixelRatio: number | null;
  sharpness: number | null;
  eligibleForSelection: boolean;
  qualityReasonCodes: string[];
};

export type PairwiseSemanticRelation = {
  cosineSimilarity: number;
  classificationSimilarity: number | null;
  combinedSimilarity: number;
};

export type WithinClipSemanticRelations = {
  meanAdjacentSimilarity: number | null;
  transitionCount: number | null;
  adjacentRelations: PairwiseSemanticRelation[];
  cumulativeChangeDetected: boolean;
  cumulativeSplitIndex: number | null;
  cumulativeSplitMs: number | null;
  cumulativeSeparation: number | null;
  cumulativeCrossSimilarity: number | null;
  contextChangeDetected: boolean;
  contextSplitIndex: number | null;
  contextSplitMs: number | null;
  contextLeftKind: string | null;
  contextRightKind: string | null;
  contextPurity: number | null;
};

export type SemanticRoutingProfile = {
  enabled: boolean;
  profileId: string;
  modelId: string;
  expectedModelSha256: string | null;
  probeStepMs: number;
  includeFinalFrame: boolean;
  blankMeanLumaMax: number;
  blankDarkPixelRatioMin: number;
  blankSharpnessMax: number;
  sceneMergeSimilarityMin: number;
  cumulativeChangeEnabled: boolean;
  cumulativeMinSegmentPoints: number;
  cumulativeSeparationMin: number;
  cumulativeCrossSimilarityMax: number;
  cumulativeAdjacentSupportMax: number;
  cumulativeSupportedSeparationMin: number;
  cumulativeStrongSeparationMin: number;
  cumulativeStrongCrossSimilarityMax: number;
  cumulativeNearBoundarySeparationMin: number;
  cumulativeNearBoundaryCrossSimilarityMax: number;
  cumulativeNearBoundaryAdjacentMax: number;
  contextChangeEnabled: boolean;
  endpointContextChangeEnabled: boolean;
  contextMinSegmentPoints: number;
  contextPurityMin: number;
  featureWeight: number;
  classificationWeight: number;
  transitionSimilarityMax: number;
  frame1MaxTransitions: number;
  frame3MaxTransitions: number;
  frame5MaxTransitions: number;
  frame1MaxScenes: number;
  frame3MaxScenes: number;
  frame5MaxScenes: number;
  frame1MeanMin: number;
  frame1RelaxedMeanMin: number;
  frame1CoherentCrossSimilarityMin: number;
  frame1CoherentSeparationMax: number;
  frame3MeanMin: number;
  frame5MeanMin: number;
};

export type EvidenceFrameLevel = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

export type SemanticRouteDecision = {
  targetFrameCount: EvidenceFrameLevel;
  reasonCodes: string[];
  semanticGateApplied: boolean;
  modelId: string | null;
  analyzerDegraded: boolean;
  withinClip: WithinClipSemanticRelations;
  semanticSceneCount: number | null;
  semanticSegmentCount: number | null;
  recommendedAnchorMs: Record<string, number[]>;
  selectedTimestampsMs: number[];
  probePoints: SemanticProbePoint[];
  validComponents: string[];
  degradationCodes: string[];
  computeMs: number;
};

export type SemanticRouteAudit = SemanticRouteDecision & {
  profileId: string;
  durationMs: number;
  analyzerKind: 'mobileclip_onnx' | 'native_vision' | 'remote_bff' | 'fallback_expo_go';
};

export const DEFAULT_SEMANTIC_ROUTING_PROFILE: SemanticRoutingProfile = {
  enabled: true,
  profileId: 'APPLE_VISION_SEMANTIC_GATE_V07',
  modelId: 'APPLE_VISION_FEATURE_PRINT_REVISION_2',
  expectedModelSha256: null,
  probeStepMs: 1000,
  includeFinalFrame: true,
  blankMeanLumaMax: 24,
  blankDarkPixelRatioMin: 0.95,
  blankSharpnessMax: 100,
  sceneMergeSimilarityMin: 0.75,
  cumulativeChangeEnabled: true,
  cumulativeMinSegmentPoints: 2,
  cumulativeSeparationMin: 0.18,
  cumulativeCrossSimilarityMax: 0.5,
  cumulativeAdjacentSupportMax: 0.6,
  cumulativeSupportedSeparationMin: 0.22,
  cumulativeStrongSeparationMin: 0.24,
  cumulativeStrongCrossSimilarityMax: 0.58,
  cumulativeNearBoundarySeparationMin: 0.1,
  cumulativeNearBoundaryCrossSimilarityMax: 0.5,
  cumulativeNearBoundaryAdjacentMax: 0.53,
  contextChangeEnabled: true,
  endpointContextChangeEnabled: false,
  contextMinSegmentPoints: 2,
  contextPurityMin: 0.7,
  featureWeight: 0.4,
  classificationWeight: 0.6,
  transitionSimilarityMax: 0.5,
  frame1MaxTransitions: 0,
  frame3MaxTransitions: 2,
  frame5MaxTransitions: 4,
  frame1MaxScenes: 1,
  frame3MaxScenes: 4,
  frame5MaxScenes: 9,
  frame1MeanMin: 0.72,
  frame1RelaxedMeanMin: 0.7,
  frame1CoherentCrossSimilarityMin: 0.65,
  frame1CoherentSeparationMax: 0.08,
  frame3MeanMin: 0.6,
  frame5MeanMin: 0.45,
};

/** Windows BFF MobileCLIP image-only (512-d, no prompt labels). */
export const MOBILECLIP_IMAGE_ROUTING_PROFILE: SemanticRoutingProfile = {
  ...DEFAULT_SEMANTIC_ROUTING_PROFILE,
  profileId: 'MOBILECLIP_S0_IMAGE_GATE_V01',
  modelId: 'MOBILECLIP_S0_FASTVIT_MCI0_IMAGE_512',
  featureWeight: 1,
  classificationWeight: 0,
  transitionSimilarityMax: 0.7,
  contextChangeEnabled: false,
  endpointContextChangeEnabled: false,
};

/** Windows BFF MobileCLIP + scene prompts (aligned to M4_MOBILECLIP_PROMPT_ROUTER_V01). */
export const MOBILECLIP_PROMPT_ROUTING_PROFILE: SemanticRoutingProfile = {
  ...DEFAULT_SEMANTIC_ROUTING_PROFILE,
  profileId: 'MOBILECLIP_S0_PROMPT_GATE_V04',
  modelId: 'MOBILECLIP_S0_IMAGE_512_SCENE_PROMPTS_V01',
  featureWeight: 0.65,
  classificationWeight: 0.35,
  transitionSimilarityMax: 0.5,
  cumulativeSeparationMin: 0.4,
  cumulativeSupportedSeparationMin: 0.4,
  cumulativeStrongSeparationMin: 0.4,
  cumulativeStrongCrossSimilarityMax: 0.45,
  contextChangeEnabled: true,
  endpointContextChangeEnabled: true,
  frame1MeanMin: 0.7,
};

export function routingProfileForModelId(
  modelId: string | undefined,
  hasClassifications: boolean,
): SemanticRoutingProfile {
  const id = modelId ?? '';
  if (id.includes('MOBILECLIP')) {
    if (hasClassifications || id.includes('SCENE_PROMPTS')) {
      return MOBILECLIP_PROMPT_ROUTING_PROFILE;
    }
    return MOBILECLIP_IMAGE_ROUTING_PROFILE;
  }
  return DEFAULT_SEMANTIC_ROUTING_PROFILE;
}

export type ProbePlanItem = {
  requestedMs: number;
  uri: string;
};

/** Fixed S0 FP16 model; endpoint V05 + global coverage V07. */
export const MOBILECLIP_FP16_V07_PROFILE: SemanticRoutingProfile = {
  ...MOBILECLIP_PROMPT_ROUTING_PROFILE,
  profileId: 'MOBILECLIP_S0_FP16_COVERAGE_V07',
  modelId: 'MOBILECLIP_S0_IMAGE_512_SCENE_PROMPTS_V01_FP16_INTERNAL',
  expectedModelSha256: '7ea0ab32ddbbd1c51b6158f12ccb669968de37125dd7455f04b6e1988cb9a141',
};
