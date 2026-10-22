import type { SemanticEmbedding } from '../types';
import { cosineSimilarity } from '../similarity';

/** Relative full-prompt endpoint gate, frozen V05 used as V07's baseline. */
export function endpointV05(points: SemanticEmbedding[], candidates: Set<number>): Set<number> {
  if (points.length < 3 || !candidates.size) return candidates;
  const rows = points.map(p => new Map((p.fullClassifications ?? []).map(c => [c.identifier, c.confidence])));
  if (!rows[0].size || rows.some(row => row.size !== rows[0].size || [...rows[0].keys()].some(k => !row.has(k)) || Math.abs([...row.values()].reduce((a, b) => a + b, 0) - 1) >= 1e-4)) {
    throw new Error('FP16 v07 requires complete model-matched prompt scores');
  }
  const distances = points.slice(1).map((p, i) => 1 - cosineSimilarity(points[i].vector, p.vector));
  const top = points.map(p => new Set(p.classifications.slice(0, 3).map(c => c.identifier)));
  const families = [['interior_room', 'interior_shop'], ['water'], ['conveyance']];
  const retained = new Set<number>();
  for (const edge of candidates) {
    if (edge !== 0 && edge !== points.length - 2) throw new Error('Non-endpoint edge');
    const endpoint = edge === 0 ? 0 : points.length - 1;
    const neighbors = endpoint === 0 ? [1, 2] : [endpoint - 1, endpoint - 2];
    const visual = distances[edge] > Math.max(...distances.filter((_, i) => i !== edge)) + 1e-6;
    for (const family of families) {
      if (!family.some(k => top[endpoint].has(k)) || neighbors.some(i => family.some(k => top[i].has(k)))) continue;
      const mass = family.reduce((s, k) => s + (rows[endpoint].get(k) ?? 0), 0);
      const neighbor = Math.max(...neighbors.map(i => family.reduce((s, k) => s + (rows[i].get(k) ?? 0), 0)));
      const competitor = Math.max(0, ...[...rows[endpoint]].filter(([k]) => !family.includes(k)).map(([, v]) => v));
      if (mass > neighbor + 1e-6 && (mass > competitor + 1e-6 || visual)) retained.add(edge);
    }
  }
  return retained;
}
