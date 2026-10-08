import type { SemanticAnalyzer } from './semanticAnalyzer';
import { appendRnFile, postMultipartText } from '../cloud/rnFormData';

export function createRemoteSemanticAnalyzer(
  baseUrl: string,
  token: string,
): SemanticAnalyzer {
  const root = baseUrl.replace(/\/+$/, '');
  return {
    kind: 'remote_bff',
    degraded: false,
    async analyzeImageUri(uri) {
      const batch = await this.analyzeImageUris!([uri]);
      return batch[0];
    },
    async analyzeImageUris(uris: string[]) {
      const form = new FormData();
      for (let index = 0; index < uris.length; index += 1) {
        appendRnFile(form, `probe_${index}`, uris[index]!, `probe_${index}.jpg`);
      }
      const headers: Record<string, string> = { Accept: 'application/json' };
      if (token) headers.Authorization = `Bearer ${token}`;
      const posted = await postMultipartText(`${root}/v1/evidence/semantic-analyze`, form, headers);
      type SemanticBody = {
        modelId?: string;
        results?: Array<{ vector: number[]; classifications: Array<{ identifier: string; confidence: number }> }>;
        detail?: string;
        degraded?: boolean;
      };
      let body: SemanticBody = {};
      try {
        body = JSON.parse(posted.text) as SemanticBody;
      } catch {
        body = {};
      }
      if (!posted.ok) {
        throw new Error(body.detail ?? `semantic-analyze HTTP ${posted.status}`);
      }
      const results = body.results ?? [];
      if (results.length !== uris.length) {
        throw new Error('semantic-analyze result count mismatch');
      }
      return results.map((item) => ({
        vector: item.vector,
        classifications: item.classifications ?? [],
        modelId: body.modelId,
        degraded: body.degraded === true,
      }));
    },
  };
}
