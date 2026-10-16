import { checkResearchHealth, runResearchPreview } from '../cloud/researchClient';

export async function pingResearchApi(endpoint: string, token: string) {
  return checkResearchHealth(endpoint, token);
}

export async function submitResearchPreview(
  endpoint: string,
  token: string,
  bundleDir: string,
  bundleJsonPath: string,
) {
  return runResearchPreview(endpoint, token, bundleDir, bundleJsonPath);
}
