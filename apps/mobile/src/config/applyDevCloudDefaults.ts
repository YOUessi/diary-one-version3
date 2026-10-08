/**
 * Expo Go 联调：从 EXPO_PUBLIC_DEV_BFF_* 灌入 Production BFF。
 * __DEV__ 下每次启动都覆盖，避免 SQLite 里旧空值挡住联调。
 */
import { useAppStore } from '../store/useAppStore';
import { CLOUD_EVIDENCE_CONSENT_VERSION } from '../onboarding/preferenceSurvey';

/** Dev / Expo Go：未明确拒绝时，打开云同意，否则 Demo 上传会被拦。 */
export function ensureDevCloudConsentForLab(): void {
  if (process.env.EXPO_PUBLIC_STORE_RELEASE === '1') return;
  if (!__DEV__) return;
  const consent = useAppStore.getState().cloudEvidenceConsent;
  if (consent === false) return;
  if (consent === true) return;
  useAppStore.getState().setCloudEvidenceConsent(true);
}

export function applyDevCloudDefaults(): void {
  if (process.env.EXPO_PUBLIC_STORE_RELEASE === '1') return;

  const url = (process.env.EXPO_PUBLIC_DEV_BFF_URL ?? '').trim().replace(/\/+$/, '');
  const token = (process.env.EXPO_PUBLIC_DEV_BFF_TOKEN ?? 'dev-token').trim() || 'dev-token';
  if (!url) return;

  if (__DEV__) {
    useAppStore.setState({
      productionApiBaseUrl: url,
      productionApiToken: token,
      cloudProcessingTarget: 'production',
    });
    // Skip / 未做问卷时 consent=null，会 fail-closed；内测默认同意（可在 Privacy 关掉）
    if (useAppStore.getState().cloudEvidenceConsent == null) {
      useAppStore.setState({
        cloudEvidenceConsent: true,
        cloudEvidenceConsentVersion: CLOUD_EVIDENCE_CONSENT_VERSION,
      });
    }
    return;
  }

  const s = useAppStore.getState();
  const patch: Partial<{
    productionApiBaseUrl: string;
    productionApiToken: string;
    cloudProcessingTarget: 'production' | 'research';
  }> = {};

  if (!s.productionApiBaseUrl.trim()) patch.productionApiBaseUrl = url;
  if (!s.productionApiToken.trim()) patch.productionApiToken = token;
  if (s.cloudProcessingTarget !== 'production' && (patch.productionApiBaseUrl || s.productionApiBaseUrl.trim())) {
    patch.cloudProcessingTarget = 'production';
  }
  if (Object.keys(patch).length) useAppStore.setState(patch);
}
