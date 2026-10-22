import { analyzeMobileClip } from './mobileclip/analyzer';
import type { SemanticAnalyzer } from './semanticAnalyzer';

/** No Apple Vision, BFF inference, or synthetic descriptor fallback. */
export function resolveSemanticAnalyzer(): SemanticAnalyzer {
  return { kind: 'mobileclip_onnx', degraded: false,
    analyzeImageUris: analyzeMobileClip,
    async analyzeImageUri(uri: string) { return (await analyzeMobileClip([uri]))[0]; },
  };
}
export function describeAnalyzer(analyzer: SemanticAnalyzer): string { return analyzer.kind; }
