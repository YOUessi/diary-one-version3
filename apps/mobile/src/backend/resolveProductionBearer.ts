import { useAppStore } from '../store/useAppStore';

/** BFF accepts OTP session_token or static API_TOKEN (Lab). */
export function resolveProductionBearer(): string {
  const s = useAppStore.getState();
  const session = s.sessionToken.trim();
  if (session) return session;
  const api = s.productionApiToken.trim();
  if (api) return api;
  return (process.env.EXPO_PUBLIC_DEV_BFF_TOKEN ?? 'dev-token').trim() || 'dev-token';
}
