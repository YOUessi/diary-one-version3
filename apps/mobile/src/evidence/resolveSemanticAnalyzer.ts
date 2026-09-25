import { createFallbackSemanticAnalyzer } from './fallbackAnalyzer';
import { createNativeVisionAnalyzer } from './nativeVisionAnalyzer';
import { createRemoteSemanticAnalyzer } from './remoteSemanticAnalyzer';
import type { SemanticAnalyzer } from './semanticAnalyzer';
import { useAppStore } from '../store/useAppStore';

export function resolveSemanticAnalyzer(options?: {
  bffBaseUrl?: string;
  bffToken?: string;
  preferRemote?: boolean;
}): SemanticAnalyzer {
  const state = useAppStore.getState();
  const bffUrl = (options?.bffBaseUrl ?? state.productionApiBaseUrl ?? '').trim();
  const token = options?.bffToken ?? state.productionApiToken ?? 'dev-token';

  const native = createNativeVisionAnalyzer();
  if (native && !options?.preferRemote) {
    return native;
  }
  if (bffUrl) {
    try {
      return createRemoteSemanticAnalyzer(bffUrl, token);
    } catch {
      /* fall through */
    }
  }
  if (native) return native;
  return createFallbackSemanticAnalyzer();
}

export function describeAnalyzer(analyzer: SemanticAnalyzer): string {
  if (analyzer.degraded) {
    return `${analyzer.kind} (degraded — not Vision quality)`;
  }
  return analyzer.kind;
}
