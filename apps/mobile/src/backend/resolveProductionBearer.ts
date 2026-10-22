import { useAppStore } from '../store/useAppStore';
import { isFormalConsumerApp, isLabToolsEnabled } from '../config/buildProfile';

/** BFF accepts OTP session_token or static API_TOKEN (Lab only). PRD SYS02 / PRI04. */
export function resolveProductionBearer(): string {
  const s = useAppStore.getState();
  const session = s.sessionToken.trim();
  if (session) return session;

  // Formal consumer (Expo Go default / beta / store): OTP session only.
  if (isFormalConsumerApp) {
    return '';
  }

  // Lab only: allow Production API token / env token.
  if (!isLabToolsEnabled) return '';

  const api = s.productionApiToken.trim();
  if (api) return api;

  return (process.env.EXPO_PUBLIC_DEV_BFF_TOKEN ?? '').trim();
}

export function requireProductionBearer(): string {
  const token = resolveProductionBearer();
  if (!token) {
    throw new Error(
      isFormalConsumerApp
        ? 'Sign in with email OTP first. This App does not use a shared API token.'
        : 'No BFF credentials. Sign in (OTP) or set Production API token (Lab).',
    );
  }
  return token;
}
