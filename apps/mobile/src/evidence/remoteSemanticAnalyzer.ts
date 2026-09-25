import type { SemanticAnalyzer } from './semanticAnalyzer';

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
      uris.forEach((uri, index) => {
        form.append(`probe_${index}`, {
          uri,
          name: `probe_${index}.jpg`,
          type: 'image/jpeg',
        } as unknown as Blob);
      });
      const headers: Record<string, string> = { Accept: 'application/json' };
      if (token) headers.Authorization = `Bearer ${token}`;
      const res = await fetch(`${root}/v1/evidence/semantic-analyze`, {
        method: 'POST',
        headers,
        body: form,
      });
      const body = (await res.json().catch(() => ({}))) as {
        modelId?: string;
        results?: Array<{ vector: number[]; classifications: Array<{ identifier: string; confidence: number }> }>;
        detail?: string;
        degraded?: boolean;
      };
      if (!res.ok) {
        throw new Error(body.detail ?? `semantic-analyze HTTP ${res.status}`);
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
