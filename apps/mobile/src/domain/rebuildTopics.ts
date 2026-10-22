import type { Chapter, Topic, TopicFacet } from '../model';

const PERSON_HINTS =
  /\b(family|friend|friends|kids|child|partner|people|pet|pets|dog|cat|mom|dad)\b/i;
const PLACE_HINTS =
  /\b(home|city|street|park|lake|beach|cafe|coffee|office|gym|trip|travel|outdoors|nature)\b/i;
const EVENT_HINTS =
  /\b(fishing|running|workout|meeting|meal|meals|walk|citywalk|habit|learning|game|hobby)\b/i;

/** Heuristic facet for Topics (人 / 事 / 地). Soft only — not a hard ontology. */
export function classifyTopicFacet(name: string): TopicFacet {
  if (PERSON_HINTS.test(name)) return 'person';
  if (PLACE_HINTS.test(name)) return 'place';
  if (EVENT_HINTS.test(name)) return 'event';
  return 'other';
}

function tokensForChapter(ch: Chapter): Set<string> {
  const raw = [
    ...ch.tags,
    ...(ch.detailTags ?? []),
    ...ch.title.split(/[\s,/·|]+/),
  ]
    .map((t) => t.trim().toLowerCase())
    .filter((t) => t.length >= 2 && !/^(the|and|with|from|for|a|an)$/.test(t));
  return new Set(raw);
}

function jaccard(a: Set<string>, b: Set<string>): number {
  if (!a.size || !b.size) return 0;
  let inter = 0;
  for (const x of a) if (b.has(x)) inter += 1;
  return inter / (a.size + b.size - inter);
}

function clusterLabel(chs: Chapter[], tokenSets: Set<string>[]): string {
  const freq = new Map<string, number>();
  for (const set of tokenSets) {
    for (const t of set) freq.set(t, (freq.get(t) ?? 0) + 1);
  }
  const ranked = [...freq.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  if (ranked[0]?.[0]) {
    // Prefer an original tag casing if present
    for (const ch of chs) {
      for (const tag of ch.tags) {
        if (tag.toLowerCase() === ranked[0][0]) return tag;
      }
    }
    return ranked[0][0].replace(/\b\w/g, (c) => c.toUpperCase());
  }
  return chs[0]?.title?.slice(0, 28) || 'Theme';
}

/**
 * Free clustering of chapters into Topics:
 * 1) agglomerative merge by tag/title Jaccard (≥0.34)
 * 2) also keep classic “same tag on ≥2 chapters” topics when not absorbed
 * Signal insufficient → empty (hide Your Topics block).
 */
export function rebuildTopicsFromChapters(chapters: Chapter[]): Topic[] {
  if (chapters.length < 2) return [];

  const tokenSets = chapters.map(tokensForChapter);
  const parent = chapters.map((_, i) => i);
  const find = (i: number): number => {
    while (parent[i] !== i) {
      parent[i] = parent[parent[i]];
      i = parent[i];
    }
    return i;
  };
  const union = (a: number, b: number) => {
    const ra = find(a);
    const rb = find(b);
    if (ra !== rb) parent[rb] = ra;
  };

  for (let i = 0; i < chapters.length; i++) {
    for (let j = i + 1; j < chapters.length; j++) {
      if (jaccard(tokenSets[i], tokenSets[j]) >= 0.34) union(i, j);
    }
  }

  const groups = new Map<number, number[]>();
  for (let i = 0; i < chapters.length; i++) {
    const r = find(i);
    const list = groups.get(r) ?? [];
    list.push(i);
    groups.set(r, list);
  }

  const topics: Topic[] = [];
  const covered = new Set<string>();

  for (const idxs of groups.values()) {
    if (idxs.length < 2) continue;
    const chs = idxs.map((i) => chapters[i]);
    const sets = idxs.map((i) => tokenSets[i]);
    const name = clusterLabel(chs, sets);
    const id = `topic-cluster-${name.toLowerCase().replace(/\s+/g, '-')}`;
    const chapterIds = chs.map((c) => c.id);
    chapterIds.forEach((cid) => covered.add(cid));
    topics.push({
      id,
      name,
      chapterIds,
      facet: classifyTopicFacet(name),
    });
  }

  // Residual single-tag topics (tag shared by ≥2 chapters) if not already covered as a cluster name
  const byTag = new Map<string, Set<string>>();
  for (const ch of chapters) {
    for (const tag of [...ch.tags, ...(ch.detailTags ?? [])]) {
      const set = byTag.get(tag) ?? new Set<string>();
      set.add(ch.id);
      byTag.set(tag, set);
    }
  }
  for (const [name, ids] of byTag.entries()) {
    if (ids.size < 2) continue;
    const already = topics.some((t) => t.name.toLowerCase() === name.toLowerCase());
    if (already) continue;
    topics.push({
      id: `topic-${name.toLowerCase().replace(/\s+/g, '-')}`,
      name,
      chapterIds: [...ids],
      facet: classifyTopicFacet(name),
    });
  }

  return topics.sort((a, b) => b.chapterIds.length - a.chapterIds.length);
}
