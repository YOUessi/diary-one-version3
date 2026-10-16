import { useAppStore } from '../store/useAppStore';
import { pingResearchApi } from './researchCloudService';
import type { BackendHealth } from './types';

export async function collectBackendHealth(): Promise<BackendHealth> {
  const s = useAppStore.getState();
  const researchConfigured = Boolean(s.researchEndpoint.trim());
  const productionConfigured = Boolean(s.productionApiBaseUrl.trim());

  let researchReachable = false;
  let researchDetail: string | undefined;
  if (researchConfigured) {
    try {
      const h = await pingResearchApi(s.researchEndpoint, s.researchToken);
      researchReachable = h.status === 'ok' || h.status === 'healthy';
      researchDetail = h.previewPath ?? undefined;
    } catch (e) {
      researchDetail = e instanceof Error ? e.message : String(e);
    }
  }

  let productionReachable = false;
  let productionDetail: string | undefined;
  if (productionConfigured) {
    try {
      const res = await fetch(`${s.productionApiBaseUrl.replace(/\/+$/, '')}/health`, {
        headers: { Accept: 'application/json' },
      });
      productionReachable = res.ok;
      productionDetail = res.ok ? 'ok' : `HTTP ${res.status}`;
    } catch (e) {
      productionDetail = e instanceof Error ? e.message : String(e);
    }
  }

  const email = s.localProfile.email?.trim();
  return {
    research: { configured: researchConfigured, reachable: researchReachable, detail: researchDetail },
    production: { configured: productionConfigured, reachable: productionReachable, detail: productionDetail },
    device: { linked: s.deviceLinkState === 'lab_linked' },
    account: { email, mode: email ? 'email_verified' : 'local' },
  };
}
