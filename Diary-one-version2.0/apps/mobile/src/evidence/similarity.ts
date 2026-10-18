import type { SemanticClassification, SemanticEmbedding, SemanticRoutingProfile , PairwiseSemanticRelation } from './types';


export function normalizeVector(vector: number[]): number[] {
  const flat = vector.map((v) => Number(v));
  let norm = 0;
  for (const v of flat) norm += v * v;
  norm = Math.sqrt(norm);
  if (!Number.isFinite(norm) || norm <= 1e-12) {
    throw new Error('semantic descriptor has zero or invalid norm');
  }
  return flat.map((v) => v / norm);
}

export function cosineSimilarity(a: number[], b: number[]): number {
  const na = normalizeVector(a);
  const nb = normalizeVector(b);
  let dot = 0;
  for (let i = 0; i < na.length; i++) {
    dot += na[i] * nb[i];
  }
  return Math.max(-1, Math.min(1, dot));
}

export function weightedJaccard(
  a: SemanticClassification[],
  b: SemanticClassification[],
): number | null {
  if (!a.length || !b.length) return null;
  const left = new Map(a.map((x) => [x.identifier, x.confidence]));
  const right = new Map(b.map((x) => [x.identifier, x.confidence]));
  const keys = new Set([...left.keys(), ...right.keys()]);
  let denominator = 0;
  let numerator = 0;
  for (const key of keys) {
    const lv = left.get(key) ?? 0;
    const rv = right.get(key) ?? 0;
    denominator += Math.max(lv, rv);
    numerator += Math.min(lv, rv);
  }
  if (denominator <= 1e-12) return null;
  return numerator / denominator;
}

export function pairwiseRelation(
  a: SemanticEmbedding,
  b: SemanticEmbedding,
  profile: SemanticRoutingProfile,
): PairwiseSemanticRelation {
  const cosine = cosineSimilarity(a.vector, b.vector);
  const classification = weightedJaccard(a.classifications, b.classifications);
  let combined = cosine;
  if (classification !== null && profile.classificationWeight > 0) {
    const total = profile.featureWeight + profile.classificationWeight;
    combined =
      (profile.featureWeight * cosine + profile.classificationWeight * classification) / total;
  }
  return {
    cosineSimilarity: cosine,
    classificationSimilarity: classification,
    combinedSimilarity: Math.max(-1, Math.min(1, combined)),
  };
}
