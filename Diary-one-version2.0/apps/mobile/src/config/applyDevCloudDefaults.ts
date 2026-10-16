/**
 * Seed Production BFF URL from EXPO_PUBLIC_DEV_BFF_* on startup.
 * Formal consumer: URL only — never shared token, never silent cloud consent (PRI01).
 * Lab (EXPO_PUBLIC_ENABLE_LAB=1): may set token / auto-consent for engineer demos.
 */
import { useAppStore } from '../store/useAppStore';
import { CLOUD_EVIDENCE_CONSENT_VERSION } from '../onboarding/preferenceSurvey';
import { resolveConfiguredBffUrl } from '../backend/bffUrl';
import { isFormalConsumerApp, isLabToolsEnabled, isStoreRelease } from './buildProfile';

/** Lab-only helper. No-op on formal consumer App. */
export function ensureDevCloudConsentForLab(): void {
  if (isStoreRelease || isFormalConsumerApp || !isLabToolsEnabled) return;
  const consent = useAppStore.getState().cloudEvidenceConsent;
  if (consent === false || consent === true) return;
  useAppStore.getState().setCloudEvidenceConsent(true);
}

function resolvePublicBffUrl(): string {
  return resolveConfiguredBffUrl({
    envUrl: process.env.EXPO_PUBLIC_DEV_BFF_URL,
    envAlias: process.env.EXPO_PUBLIC_BFF_BASE_URL,
  });
}

export function applyDevCloudDefaults(): void {
  if (isStoreRelease) return;

  const url = resolvePublicBffUrl();
  if (!url) return;

  if (isFormalConsumerApp) {
    // Expo Go / beta / store-like: production URL, clear shared token, never silent consent.
    useAppStore.setState({
      productionApiBaseUrl: url,
      productionApiToken: '',
      cloudProcessingTarget: 'production',
      researchEndpoint: '',
      researchToken: '',
    });
    return;
  }

  // Lab only
  const rawToken = (
    process.env.EXPO_PUBLIC_DEV_BFF_TOKEN ??
    process.env.EXPO_PUBLIC_API_TOKEN ??
    ''
  ).trim();
  useAppStore.setState({
    productionApiBaseUrl: url,
    productionApiToken: rawToken,
    cloudProcessingTarget: 'production',
  });
  if (useAppStore.getState().cloudEvidenceConsent == null) {
    useAppStore.setState({
      cloudEvidenceConsent: true,
      cloudEvidenceConsentVersion: CLOUD_EVIDENCE_CONSENT_VERSION,
    });
  }
}
