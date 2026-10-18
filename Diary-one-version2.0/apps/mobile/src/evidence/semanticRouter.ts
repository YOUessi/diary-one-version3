import { pairwiseRelation } from './similarity';
import type {
  EvidenceFrameLevel,
  SemanticEmbedding,
  SemanticProbePoint,
  SemanticRouteDecision,
  SemanticRoutingProfile,
  WithinClipSemanticRelations,
} from './types';

function contextKind(point: SemanticProbePoint): string | null {
  const labels = new Set(point.classifications.slice(0, 5).map((c) => c.identifier));
  const openDetail = new Set([
    'land',
    'road',
    'street',
    'path',
    'water',
    'plant',
    'palm_tree',
    'foliage',
    'vegetation',
  ]);
  const builtDetail = new Set(['portal', 'window', 'door', 'interior_room', 'interior_shop']);
  if (
    labels.has('sky') ||
    labels.has('blue_sky') ||
    (labels.has('outdoor') && [...labels].some((l) => openDetail.has(l)))
  ) {
    return 'OPEN_AIR';
  }
  if ([...labels].some((l) => builtDetail.has(l))) return 'BUILT_THRESHOLD';
  if (
    labels.has('structure') &&
    [...labels].some((l) => ['material', 'raw_glass', 'conveyance', 'building'].includes(l)) &&
    !labels.has('sky') &&
    !labels.has('blue_sky')
  ) {
    return 'BUILT_THRESHOLD';
  }
  return null;
}

function bestCumulativeChange(
  pairwiseSimilarities: number[][],
  minimumAdjacentSimilarity: number | null,
  profile: SemanticRoutingProfile,
): { split: number | null; separation: number | null; crossMean: number | null; detected: boolean } {
  const n = pairwiseSimilarities.length;
  const minSeg = profile.cumulativeMinSegmentPoints;
  if (n < minSeg * 2) return { split: null, separation: null, crossMean: null, detected: false };

  let best: { separation: number; negCross: number; split: number; crossMean: number } | null = null;
  for (let split = minSeg; split <= n - minSeg; split++) {
    const left: number[] = [];
    const right: number[] = [];
    const cross: number[] = [];
    for (let i = 0; i < split; i++) {
      for (let j = i + 1; j < split; j++) left.push(pairwiseSimilarities[i][j]);
    }
    for (let i = split; i < n; i++) {
      for (let j = i + 1; j < n; j++) right.push(pairwiseSimilarities[i][j]);
    }
    for (let i = 0; i < split; i++) {
      for (let j = split; j < n; j++) cross.push(pairwiseSimilarities[i][j]);
    }
    if (!left.length || !right.length || !cross.length) continue;
    const leftMean = left.reduce((a, b) => a + b, 0) / left.length;
    const rightMean = right.reduce((a, b) => a + b, 0) / right.length;
    const crossMean = cross.reduce((a, b) => a + b, 0) / cross.length;
    const separation = Math.min(leftMean, rightMean) - crossMean;
    const candidate = { separation, negCross: -crossMean, split, crossMean };
    if (
      !best ||
      candidate.separation > best.separation ||
      (candidate.separation === best.separation && candidate.negCross > best.negCross)
    ) {
      best = candidate;
    }
  }
  if (!best) return { split: null, separation: null, crossMean: null, detected: false };
  const adjacent = minimumAdjacentSimilarity;
  const supportedStandard =
    best.separation >= profile.cumulativeSeparationMin &&
    best.crossMean <= profile.cumulativeCrossSimilarityMax &&
    (best.separation >= profile.cumulativeSupportedSeparationMin ||
      (adjacent !== null && adjacent <= profile.cumulativeAdjacentSupportMax));
  const strongSustained =
    best.separation >= profile.cumulativeStrongSeparationMin &&
    best.crossMean <= profile.cumulativeStrongCrossSimilarityMax;
  const nearBoundary =
    adjacent !== null &&
    adjacent <= profile.cumulativeNearBoundaryAdjacentMax &&
    best.separation >= profile.cumulativeNearBoundarySeparationMin &&
    best.crossMean <= profile.cumulativeNearBoundaryCrossSimilarityMax;
  return {
    split: best.split,
    separation: best.separation,
    crossMean: best.crossMean,
    detected: supportedStandard || strongSustained || nearBoundary,
  };
}

function bestContextChange(
  probePoints: SemanticProbePoint[],
  profile: SemanticRoutingProfile,
): {
  split: number | null;
  leftKind: string | null;
  rightKind: string | null;
  purity: number | null;
  detected: boolean;
} {
  const minSeg = profile.contextMinSegmentPoints;
  if (probePoints.length < minSeg * 2) {
    return { split: null, leftKind: null, rightKind: null, purity: null, detected: false };
  }
  const contexts = probePoints.map((p) => contextKind(p));
  let best: { purity: number; negSplit: number; left: string; right: string } | null = null;
  for (let split = minSeg; split <= contexts.length - minSeg; split++) {
    const left = contexts.slice(0, split).filter((c): c is string => c !== null);
    const right = contexts.slice(split).filter((c): c is string => c !== null);
    if (left.length < minSeg || right.length < minSeg) continue;
    for (const [leftKind, rightKind] of [
      ['OPEN_AIR', 'BUILT_THRESHOLD'],
      ['BUILT_THRESHOLD', 'OPEN_AIR'],
    ] as const) {
      const purity = Math.min(
        left.filter((c) => c === leftKind).length / left.length,
        right.filter((c) => c === rightKind).length / right.length,
      );
      const candidate = { purity, negSplit: -split, left: leftKind, right: rightKind };
      if (
        !best ||
        candidate.purity > best.purity ||
        (candidate.purity === best.purity && candidate.negSplit > best.negSplit)
      ) {
        best = candidate;
      }
    }
  }
  if (!best) return { split: null, leftKind: null, rightKind: null, purity: null, detected: false };
  const split = -best.negSplit;
  return {
    split,
    leftKind: best.left,
    rightKind: best.right,
    purity: best.purity,
    detected: best.purity >= profile.contextPurityMin,
  };
}

function endpointContextEdges(probePoints: SemanticProbePoint[]): Set<number> {
  if (probePoints.length < 3) return new Set();
  const families = [
    new Set(['interior_room', 'interior_shop']),
    new Set(['water']),
    new Set(['conveyance']),
  ];
  const pointLabels = probePoints.map(
    (p) => new Set(p.classifications.slice(0, 3).map((c) => c.identifier)),
  );
  const edges = new Set<number>();
  for (const family of families) {
    const firstHas = [...pointLabels[0]].some((l) => family.has(l));
    const nextTwo = pointLabels.slice(1, 3).map((s) => [...s].some((l) => family.has(l)));
    if (firstHas && !nextTwo.some(Boolean)) edges.add(0);
    const lastHas = [...pointLabels[pointLabels.length - 1]].some((l) => family.has(l));
    const prevTwo = pointLabels.slice(-3, -1).map((s) => [...s].some((l) => family.has(l)));
    if (lastHas && !prevTwo.some(Boolean)) edges.add(probePoints.length - 2);
  }
  return edges;
}

function combinations<T>(arr: T[], k: number): T[][] {
  if (k === 0) return [[]];
  if (arr.length < k) return [];
  const [head, ...tail] = arr;
  const withHead = combinations(tail, k - 1).map((c) => [head, ...c]);
  return [...withHead, ...combinations(tail, k)];
}

function semanticAnchorRecommendations(
  probePoints: SemanticProbePoint[],
  adjacent: { combinedSimilarity: number }[],
  profile: SemanticRoutingProfile,
  pairwiseSimilarities: number[][] | null,
  forcedTransitionEdges: number[],
): { segmentCount: number | null; sceneCount: number | null; recommended: Record<string, number[]> } {
  if (!probePoints.length) return { segmentCount: null, sceneCount: null, recommended: {} };

  const transitionEdges = new Set<number>();
  adjacent.forEach((rel, index) => {
    if (rel.combinedSimilarity < profile.transitionSimilarityMax) transitionEdges.add(index);
  });
  forcedTransitionEdges.forEach((e) => transitionEdges.add(e));
  const ordered = [...transitionEdges].sort((a, b) => a - b);
  const segmentBounds: [number, number][] = [];
  let start = 0;
  for (const edge of ordered) {
    segmentBounds.push([start, edge]);
    start = edge + 1;
  }
  segmentBounds.push([start, probePoints.length - 1]);

  const representative = (bounds: [number, number]) => {
    const [left, right] = bounds;
    const midpoint = (probePoints[left].actualPtsMs + probePoints[right].actualPtsMs) / 2;
    let bestIdx = left;
    let bestKey = Infinity;
    for (let index = left; index <= right; index++) {
      const key = Math.abs(probePoints[index].actualPtsMs - midpoint) * 1000 + index;
      if (key < bestKey) {
        bestKey = key;
        bestIdx = index;
      }
    }
    return bestIdx;
  };

  const segmentRepresentatives = segmentBounds.map(representative);
  const sceneClusters: number[][] = [];
  for (let segmentIndex = 0; segmentIndex < segmentRepresentatives.length; segmentIndex++) {
    const candidate = segmentRepresentatives[segmentIndex];
    let matching: number | null = null;
    if (pairwiseSimilarities) {
      for (let ci = 0; ci < sceneClusters.length; ci++) {
        const cluster = sceneClusters[ci];
        if (
          cluster.some(
            (member) =>
              Math.abs(segmentIndex - member) >= 2 &&
              pairwiseSimilarities[candidate][segmentRepresentatives[member]] >=
                profile.sceneMergeSimilarityMin,
          )
        ) {
          matching = ci;
          break;
        }
      }
    }
    if (matching === null) sceneClusters.push([segmentIndex]);
    else sceneClusters[matching].push(segmentIndex);
  }

  const segmentDurations = segmentBounds.map(
    ([l, r]) => probePoints[r].actualPtsMs - probePoints[l].actualPtsMs,
  );
  const sceneRepresentatives: number[] = [];
  const representativeDurations: Record<number, number> = {};
  for (const cluster of sceneClusters) {
    let chosenSegment = cluster[0];
    let bestDur = -1;
    for (const idx of cluster) {
      if (
        segmentDurations[idx] > bestDur ||
        (segmentDurations[idx] === bestDur &&
          segmentBounds[idx][0] < segmentBounds[chosenSegment][0])
      ) {
        chosenSegment = idx;
        bestDur = segmentDurations[idx];
      }
    }
    const chosen = segmentRepresentatives[chosenSegment];
    sceneRepresentatives.push(chosen);
    representativeDurations[chosen] = cluster.reduce((s, i) => s + segmentDurations[i], 0);
  }
  sceneRepresentatives.sort((a, b) => a - b);

  const spreadSubset = (indices: number[], count: number): number[] => {
    if (count >= indices.length) return [...indices];
    if (count === 1) {
      return [
        indices.reduce((best, index) =>
          (representativeDurations[index] ?? 0) > (representativeDurations[best] ?? 0)
            ? index
            : best,
        indices[0]),
      ];
    }
    if (pairwiseSimilarities) {
      const candidates = combinations(indices, count);
      let bestSubset = candidates[0];
      let bestMax = Infinity;
      for (const subset of candidates) {
        let maxSim = -Infinity;
        for (let i = 0; i < subset.length; i++) {
          for (let j = i + 1; j < subset.length; j++) {
            maxSim = Math.max(maxSim, pairwiseSimilarities[subset[i]][subset[j]]);
          }
        }
        if (maxSim < bestMax) {
          bestMax = maxSim;
          bestSubset = subset;
        }
      }
      return bestSubset;
    }
    const positions = Array.from({ length: count }, (_, i) =>
      Math.round((i * (indices.length - 1)) / (count - 1)),
    );
    return positions.map((p) => indices[p]);
  };

  const recommended: Record<string, number[]> = {};
  for (const targetCount of [1, 3, 5, 10] as const) {
    if (probePoints.length < targetCount) continue;
    let selected: number[];
    if (targetCount === 1 && pairwiseSimilarities) {
      const candidates = probePoints.map((_, index) => index);
      selected = [
        candidates.reduce((best, index) => {
          const others = candidates.filter((o) => o !== index);
          const meanSim =
            others.reduce((s, o) => s + pairwiseSimilarities[index][o], 0) /
            Math.max(1, others.length);
          const score =
            meanSim * 1e6 +
            (1 - (probePoints[index].darkPixelRatio ?? 0)) * 1e3 +
            (probePoints[index].sharpness ?? 0) -
            index * 1e-6;
          const bestMean =
            candidates
              .filter((o) => o !== best)
              .reduce((s, o) => s + pairwiseSimilarities[best][o], 0) /
            Math.max(1, candidates.length - 1);
          const bestScore =
            bestMean * 1e6 +
            (1 - (probePoints[best].darkPixelRatio ?? 0)) * 1e3 +
            (probePoints[best].sharpness ?? 0) -
            best * 1e-6;
          return score > bestScore ? index : best;
        }, candidates[0]),
      ];
    } else {
      selected = spreadSubset(sceneRepresentatives, targetCount);
    }
    while (selected.length < targetCount) {
      const remaining = probePoints.map((_, i) => i).filter((i) => !selected.includes(i));
      const candidate = remaining.reduce((best, index) => {
        const maxSim = pairwiseSimilarities
          ? Math.max(...selected.map((chosen) => pairwiseSimilarities[index][chosen]))
          : 0;
        const minDist = Math.min(
          ...selected.map((chosen) =>
            Math.abs(probePoints[index].actualPtsMs - probePoints[chosen].actualPtsMs),
          ),
        );
        const score = -maxSim * 1e6 + minDist * 1e3 - index;
        const bestMaxSim = pairwiseSimilarities
          ? Math.max(...selected.map((chosen) => pairwiseSimilarities[best][chosen]))
          : 0;
        const bestMinDist = Math.min(
          ...selected.map((chosen) =>
            Math.abs(probePoints[best].actualPtsMs - probePoints[chosen].actualPtsMs),
          ),
        );
        const bestScore = -bestMaxSim * 1e6 + bestMinDist * 1e3 - best;
        return score > bestScore ? index : best;
      }, remaining[0]);
      selected.push(candidate);
    }
    recommended[String(targetCount)] = selected
      .map((index) => probePoints[index].actualPtsMs)
      .sort((a, b) => a - b);
  }

  return {
    segmentCount: segmentBounds.length,
    sceneCount: sceneClusters.length,
    recommended,
  };
}

function applySemanticGate(
  profile: SemanticRoutingProfile,
  within: WithinClipSemanticRelations,
  sceneCount: number | null,
  validComponents: string[],
): { level: EvidenceFrameLevel; reasonCodes: string[]; gateApplied: boolean } {
  const reasonCodes: string[] = [];
  const meanContinuity = within.meanAdjacentSimilarity;
  const transitionCount = within.transitionCount;
  let scenes = sceneCount;
  if (
    meanContinuity === null ||
    transitionCount === null ||
    !validComponents.includes('WITHIN_CLIP_SEMANTIC_SEQUENCE')
  ) {
    reasonCodes.push('SEMANTIC_RESULT_INVALID_FALLBACK_FRAME_3');
    return { level: 3, reasonCodes, gateApplied: false };
  }
  scenes = scenes ?? transitionCount + 1;
  const coherentSingleScene =
    scenes <= profile.frame1MaxScenes &&
    meanContinuity >= profile.frame1RelaxedMeanMin &&
    within.cumulativeCrossSimilarity !== null &&
    within.cumulativeCrossSimilarity >= profile.frame1CoherentCrossSimilarityMin &&
    within.cumulativeSeparation !== null &&
    within.cumulativeSeparation <= profile.frame1CoherentSeparationMax &&
    !within.contextChangeDetected;

  if (
    (scenes <= profile.frame1MaxScenes && meanContinuity >= profile.frame1MeanMin) ||
    coherentSingleScene
  ) {
    reasonCodes.push(
      coherentSingleScene && meanContinuity < profile.frame1MeanMin
        ? 'SEMANTIC_COHERENT_SINGLE_SCENE_SELECT_FRAME_1'
        : 'SEMANTIC_SEQUENCE_SELECT_FRAME_1',
    );
    return { level: 1, reasonCodes, gateApplied: true };
  }
  if (scenes <= profile.frame3MaxScenes && meanContinuity >= profile.frame3MeanMin) {
    reasonCodes.push('SEMANTIC_SEQUENCE_SELECT_FRAME_3');
    return { level: 3, reasonCodes, gateApplied: true };
  }
  if (scenes <= profile.frame5MaxScenes && meanContinuity >= profile.frame5MeanMin) {
    reasonCodes.push('SEMANTIC_SEQUENCE_SELECT_FRAME_5');
    return { level: 5, reasonCodes, gateApplied: true };
  }
  reasonCodes.push('SEMANTIC_SEQUENCE_SELECT_FIXED_10');
  return { level: 10, reasonCodes, gateApplied: true };
}

export type RouteSemanticInput = {
  profile: SemanticRoutingProfile;
  modelId: string;
  analyzerDegraded: boolean;
  probes: {
    requestedMs: number;
    actualPtsMs: number;
    embedding: SemanticEmbedding;
    meanLuma: number | null;
    darkPixelRatio: number | null;
    sharpness: number | null;
    eligibleForSelection: boolean;
    qualityReasonCodes: string[];
  }[];
};

const EMPTY_WITHIN: WithinClipSemanticRelations = {
  meanAdjacentSimilarity: null,
  transitionCount: null,
  adjacentRelations: [],
  cumulativeChangeDetected: false,
  cumulativeSplitIndex: null,
  cumulativeSplitMs: null,
  cumulativeSeparation: null,
  cumulativeCrossSimilarity: null,
  contextChangeDetected: false,
  contextSplitIndex: null,
  contextSplitMs: null,
  contextLeftKind: null,
  contextRightKind: null,
  contextPurity: null,
};

export function routeSemanticClip(input: RouteSemanticInput): SemanticRouteDecision {
  const started = Date.now();
  const { profile, modelId, analyzerDegraded, probes } = input;
  const reasonCodes: string[] = [];
  const degradationCodes: string[] = [];
  const validComponents: string[] = [];

  if (!profile.enabled) {
    return {
      targetFrameCount: 3,
      reasonCodes: ['SEMANTIC_ROUTING_DISABLED'],
      semanticGateApplied: false,
      modelId,
      analyzerDegraded,
      withinClip: EMPTY_WITHIN,
      semanticSceneCount: null,
      semanticSegmentCount: null,
      recommendedAnchorMs: {},
      selectedTimestampsMs: [],
      probePoints: [],
      validComponents: [],
      degradationCodes: ['SEMANTIC_ROUTING_DISABLED'],
      computeMs: 0,
    };
  }

  const probePoints: SemanticProbePoint[] = probes.map((p, ordinal) => ({
    ordinal,
    requestedMs: p.requestedMs,
    actualPtsMs: p.actualPtsMs,
    classifications: p.embedding.classifications,
    meanLuma: p.meanLuma,
    darkPixelRatio: p.darkPixelRatio,
    sharpness: p.sharpness,
    eligibleForSelection: p.eligibleForSelection,
    qualityReasonCodes: p.qualityReasonCodes,
  }));

  const eligibleIndices = probePoints
    .map((p, i) => (p.eligibleForSelection ? i : -1))
    .filter((i) => i >= 0);
  const eligibleEmbeddings = eligibleIndices.map((i) => probes[i].embedding);
  const eligibleProbePoints = eligibleIndices.map((i) => probePoints[i]);

  if (eligibleProbePoints.length !== probePoints.length) {
    degradationCodes.push('SEMANTIC_LOW_QUALITY_PROBES_EXCLUDED');
  }
  if (analyzerDegraded) {
    degradationCodes.push('SEMANTIC_ANALYZER_DEGRADED_NOT_VISION');
  }

  if (eligibleEmbeddings.length < 1) {
    return {
      targetFrameCount: 3,
      reasonCodes: ['SEMANTIC_NO_ELIGIBLE_PROBES'],
      semanticGateApplied: false,
      modelId,
      analyzerDegraded,
      withinClip: EMPTY_WITHIN,
      semanticSceneCount: null,
      semanticSegmentCount: null,
      recommendedAnchorMs: {},
      selectedTimestampsMs: probePoints.map((p) => p.actualPtsMs).slice(0, 3),
      probePoints,
      validComponents,
      degradationCodes: [...degradationCodes, 'SEMANTIC_PROBES_INCOMPLETE'],
      computeMs: Date.now() - started,
    };
  }

  const pairwiseSimilarities = eligibleEmbeddings.map((left, leftIndex) =>
    eligibleEmbeddings.map((right, rightIndex) =>
      leftIndex === rightIndex ? 1 : pairwiseRelation(left, right, profile).combinedSimilarity,
    ),
  );

  const minimumAdjacent =
    eligibleEmbeddings.length >= 2
      ? Math.min(...pairwiseSimilarities.map((row, i) => (i < row.length - 1 ? row[i + 1] : 1)))
      : null;

  let cumulativeSplit: number | null = null;
  let cumulativeSeparation: number | null = null;
  let cumulativeCross: number | null = null;
  let cumulativeDetected = false;
  if (profile.cumulativeChangeEnabled && eligibleEmbeddings.length >= 2) {
    const cum = bestCumulativeChange(pairwiseSimilarities, minimumAdjacent, profile);
    cumulativeSplit = cum.split;
    cumulativeSeparation = cum.separation;
    cumulativeCross = cum.crossMean;
    cumulativeDetected = cum.detected;
  }

  let contextSplit: number | null = null;
  let contextLeft: string | null = null;
  let contextRight: string | null = null;
  let contextPurity: number | null = null;
  let contextDetected = false;
  if (profile.contextChangeEnabled) {
    const ctx = bestContextChange(eligibleProbePoints, profile);
    contextSplit = ctx.split;
    contextLeft = ctx.leftKind;
    contextRight = ctx.rightKind;
    contextPurity = ctx.purity;
    contextDetected = ctx.detected;
  }

  let endpointEdges = new Set<number>();
  if (profile.endpointContextChangeEnabled) {
    endpointEdges = endpointContextEdges(eligibleProbePoints);
    if (endpointEdges.size) validComponents.push('SEMANTIC_ENDPOINT_CONTEXT');
  }

  let within: WithinClipSemanticRelations;
  if (eligibleEmbeddings.length >= 2) {
    const adjacent = eligibleEmbeddings
      .slice(0, -1)
      .map((left, i) => pairwiseRelation(left, eligibleEmbeddings[i + 1], profile));
    const combined = adjacent.map((a) => a.combinedSimilarity);
    const transitionEdges = new Set<number>();
    combined.forEach((value, index) => {
      if (value < profile.transitionSimilarityMax) transitionEdges.add(index);
    });
    if (cumulativeDetected && cumulativeSplit !== null) transitionEdges.add(cumulativeSplit - 1);
    if (contextDetected && contextSplit !== null) transitionEdges.add(contextSplit - 1);
    endpointEdges.forEach((e) => transitionEdges.add(e));

    within = {
      meanAdjacentSimilarity: combined.reduce((a, b) => a + b, 0) / combined.length,
      transitionCount: transitionEdges.size,
      adjacentRelations: adjacent,
      cumulativeChangeDetected: cumulativeDetected,
      cumulativeSplitIndex: cumulativeSplit,
      cumulativeSplitMs:
        cumulativeSplit !== null ? eligibleProbePoints[cumulativeSplit].actualPtsMs : null,
      cumulativeSeparation,
      cumulativeCrossSimilarity: cumulativeCross,
      contextChangeDetected: contextDetected,
      contextSplitIndex: contextSplit,
      contextSplitMs:
        contextSplit !== null ? eligibleProbePoints[contextSplit].actualPtsMs : null,
      contextLeftKind: contextLeft,
      contextRightKind: contextRight,
      contextPurity,
    };
    validComponents.push('WITHIN_CLIP_SEMANTIC_SEQUENCE');
    if (probePoints.some((p) => p.classifications.length)) {
      validComponents.push('SEMANTIC_CLASSIFICATIONS');
    } else if (profile.classificationWeight > 0 || profile.contextChangeEnabled) {
      degradationCodes.push('SEMANTIC_CLASSIFICATIONS_UNAVAILABLE');
    }
  } else {
    within = EMPTY_WITHIN;
    degradationCodes.push('SEMANTIC_PROBES_INCOMPLETE');
  }

  const forcedEdges = [
    ...(cumulativeDetected && cumulativeSplit !== null ? [cumulativeSplit - 1] : []),
    ...(contextDetected && contextSplit !== null ? [contextSplit - 1] : []),
    ...endpointEdges,
  ];

  const anchors = semanticAnchorRecommendations(
    eligibleProbePoints,
    within.adjacentRelations,
    profile,
    pairwiseSimilarities,
    forcedEdges,
  );

  const gate = applySemanticGate(profile, within, anchors.sceneCount, validComponents);
  reasonCodes.push(...gate.reasonCodes);

  const selectedTimestampsMs =
    anchors.recommended[String(gate.level)] ??
    eligibleProbePoints.map((p) => p.actualPtsMs).slice(0, gate.level);

  return {
    targetFrameCount: gate.level,
    reasonCodes,
    semanticGateApplied: gate.gateApplied,
    modelId,
    analyzerDegraded,
    withinClip: within,
    semanticSceneCount: anchors.sceneCount,
    semanticSegmentCount: anchors.segmentCount,
    recommendedAnchorMs: anchors.recommended,
    selectedTimestampsMs,
    probePoints,
    validComponents,
    degradationCodes,
    computeMs: Date.now() - started,
  };
}
