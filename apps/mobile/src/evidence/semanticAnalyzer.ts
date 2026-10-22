import type { SemanticClassification } from './types';

export type SemanticAnalyzeResult = {
  vector: number[];
  classifications: SemanticClassification[];
  fullClassifications?: SemanticClassification[];
  degraded?: boolean;
  modelId?: string;
};

export interface SemanticAnalyzer {
  readonly kind: 'mobileclip_onnx' | 'native_vision' | 'remote_bff' | 'fallback_expo_go';
  readonly degraded: boolean;
  analyzeImageUri(uri: string): Promise<SemanticAnalyzeResult>;
  analyzeImageUris?(uris: string[]): Promise<SemanticAnalyzeResult[]>;
}
