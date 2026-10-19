/** Port of frozen coverage_v07.py, GLOBAL variant (regional inference disabled).
 * Selects 1..5 frames for <=12 probes; preserves baseline within 0.020 gain.
 * This optimizer does not replace the baseline/session routing stages. */
import { cosineSimilarity } from '../similarity';

export const COVERAGE_POLICY = 'CONTENT_COVERAGE_V07_20261008';
export type CoverageInput = { points: number[]; vectors: number[][]; scores: number[][]; baseline: number[] };

export function coverageV07({ points, vectors, scores, baseline }: CoverageInput) {
  const n = points.length;
  if (!n || n > 12 || vectors.length !== n || points.some((p, i) => !Number.isFinite(p) || (i > 0 && p <= points[i - 1]))) throw new Error('Invalid v07 probe timeline');
  if (baseline.length < 1 || baseline.length > 5) throw new Error('v07 needs a 1..5 frame baseline');
  if (vectors.some(v => v.length !== vectors[0].length || !v.every(Number.isFinite))) throw new Error('Invalid v07 vectors');
  const old = baseline.map(t => points.reduce((best, p, i) => Math.abs(p - t) < Math.abs(points[best] - t) ? i : best, 0)).sort((a, b) => a - b);
  if (new Set(old).size !== old.length) throw new Error('Duplicate baseline anchors');
  const sims = vectors.map(a => vectors.map(b => cosineSimilarity(a, b)));
  const probs = scores.length ? scores.map(row => {
    if (!row.length || row.length !== scores[0].length || !row.every(Number.isFinite)) throw new Error('Invalid prompt scores');
    const positive = row.map(v => Math.max(0, v));
    const sum = positive.reduce((a, b) => a + b, 0);
    return sum < 1e-8 ? null : positive.map(v => v / sum);
  }) : [];
  if (scores.length && scores.length !== n) throw new Error('Prompt count mismatch');
  const labels = probs.length === n && probs.every(p => p !== null)
    ? probs.map(a => probs.map(b => Math.max(0, 1 - 0.5 * a!.reduce((s, v, i) => s + Math.abs(v - b![i]), 0)))) : null;
  const scaled = (s: number) => Math.max(0, Math.min(1, (s - 0.45) / 0.55));
  const metrics = (indices: number[]) => {
    const nearest = sims.map(row => Math.max(...indices.map(j => scaled(row[j]))));
    const mixed = nearest.map((v, i) => labels ? (0.64 * v + 0.08 * Math.max(...indices.map(j => labels[i][j]))) / 0.72 : v);
    const bottom = Math.max(1, Math.ceil(n * 0.2));
    const tail = [...mixed].sort((a, b) => a - b).slice(0, bottom).reduce((a, b) => a + b, 0) / bottom;
    let redundant = 0;
    indices.forEach((a, i) => indices.slice(i + 1).forEach(b => { if (sims[a][b] >= 0.93) redundant++; }));
    const objective = 0.78 * mixed.reduce((a, b) => a + b, 0) / n + 0.22 * tail - 0.10 * (indices.length - 1) - 0.028 * redundant;
    return { objective, globalCoverage: nearest.reduce((a, b) => a + b, 0) / n, tailCoverage: tail, redundantPairs: redundant };
  };
  const original = metrics(old);
  let best: number[] = [], bestRank: number[] = [], bestMetrics = original;
  const visit = (indices: number[]) => {
    const m = metrics(indices);
    const rank = [Math.round(m.objective * 1e9) / 1e9, -indices.length, indices.filter(i => old.includes(i)).length, ...indices.map(i => -i)];
    const firstDifference = rank.findIndex((v, i) => v !== bestRank[i]);
    if (!best.length || (firstDifference >= 0 && rank[firstDifference] > bestRank[firstDifference])) {
      best = [...indices]; bestRank = rank; bestMetrics = m;
    }
  };
  const enumerate = (prefix: number[], next: number, count: number) => {
    if (!count) { visit(prefix); return; }
    for (let i = next; i <= n - count; i++) enumerate([...prefix, i], i + 1, count - 1);
  };
  for (let k = 1; k <= Math.min(5, n); k++) enumerate([], 0, k);
  let reason: string;
  if (bestMetrics.objective <= original.objective + 0.020) {
    best = old; bestMetrics = original; reason = 'PRESERVE_V05_BELOW_NET_GAIN_TOLERANCE';
  } else reason = best.length > old.length ? 'COVERAGE_GAIN_JUSTIFIES_EXTRA_FRAME' : best.length < old.length ? 'LOW_MARGINAL_COVERAGE_REMOVES_EXTRA_FRAME' : 'BETTER_COVERAGE_SAME_FRAME_BUDGET';
  return { policyId: COVERAGE_POLICY, anchors: best.map(i => points[i]), baseline: [...baseline], original, proposed: bestMetrics, reason, regional: false };
}
