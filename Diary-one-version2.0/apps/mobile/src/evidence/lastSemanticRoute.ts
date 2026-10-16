import type { SemanticRouteAudit } from './types';

let lastAudit: SemanticRouteAudit | null = null;

export function setLastSemanticRouteAudit(audit: SemanticRouteAudit | null): void {
  lastAudit = audit;
}

export function getLastSemanticRouteAudit(): SemanticRouteAudit | null {
  return lastAudit;
}

export function formatSemanticRouteSummary(audit: SemanticRouteAudit | null): string {
  if (!audit) return 'No semantic route yet. Import a video via lab B.';
  return [
    `frames=${audit.targetFrameCount} scenes=${audit.semanticSceneCount ?? '?'}`,
    `analyzer=${audit.analyzerKind}${audit.analyzerDegraded ? ' DEGRADED' : ''}`,
    `meanAdj=${audit.withinClip.meanAdjacentSimilarity?.toFixed(3) ?? 'n/a'}`,
    `reasons=${audit.reasonCodes.slice(0, 2).join(',')}`,
  ].join(' · ');
}
