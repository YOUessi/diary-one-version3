import { useAppStore } from '../store/useAppStore';
import { resolveProductionBearer } from './resolveProductionBearer';
import { requireCloudAuth } from '../config/buildProfile';
import { resolveConfiguredBffUrl } from './bffUrl';

function authBase(): { url: string; token: string } {
  const s = useAppStore.getState();
  const url = resolveConfiguredBffUrl({
    storeUrl: s.productionApiBaseUrl,
    envUrl: process.env.EXPO_PUBLIC_DEV_BFF_URL,
    envAlias: process.env.EXPO_PUBLIC_BFF_BASE_URL,
  });
  return { url, token: resolveProductionBearer() };
}

export type OtpRequestResult =
  | { ok: true; email: string; devCode?: string; message: string }
  | { ok: false; reason: string };

export type OtpVerifyResult =
  | { ok: true; email: string; nickname?: string; sessionToken?: string }
  | { ok: false; reason: string };

/** ACC03 — BFF Dev Lite / production OTP. Falls back to local-only when BFF unset. */
export async function requestEmailOtp(email: string): Promise<OtpRequestResult> {
  const trimmed = email.trim();
  if (!trimmed.includes('@')) {
    return { ok: false, reason: 'invalid_email' };
  }
  const { url } = authBase();
  if (!url) {
    if (requireCloudAuth) {
      return {
        ok: false,
        reason:
          'BFF URL missing or still a placeholder. Set EXPO_PUBLIC_DEV_BFF_URL to your team BFF (LAN or HTTPS).',
      };
    }
    return {
      ok: true,
      email: trimmed,
      message: 'Lab: no BFF URL — use any 6-digit code (local-only).',
      devCode: undefined,
    };
  }
  try {
    const res = await fetch(`${url}/v1/auth/otp/request`, {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: trimmed }),
    });
    const body = (await res.json().catch(() => ({}))) as {
      ok?: boolean;
      dev_code?: string;
      message?: string;
      detail?: string;
    };
    if (!res.ok) {
      return { ok: false, reason: body.detail ?? `otp_request_failed_${res.status}` };
    }
    return {
      ok: true,
      email: trimmed,
      message: body.message ?? 'OTP sent',
      devCode: body.dev_code,
    };
  } catch (e) {
    return { ok: false, reason: e instanceof Error ? e.message : String(e) };
  }
}

export async function verifyEmailOtpRemote(email: string, code: string): Promise<OtpVerifyResult> {
  const digits = code.replace(/\D/g, '');
  if (digits.length < 6) {
    return { ok: false, reason: 'invalid_code' };
  }
  const { url } = authBase();
  if (!url) {
    if (requireCloudAuth) {
      return {
        ok: false,
        reason:
          'BFF URL missing or still a placeholder. Cannot verify OTP without the team cloud.',
      };
    }
    // Lab-only walkthrough without BFF
    const profile = useAppStore.getState().localProfile;
    useAppStore.getState().setLocalProfile({ ...profile, email: email.trim() });
    return { ok: true, email: email.trim() };
  }
  try {
    const res = await fetch(`${url}/v1/auth/otp/verify`, {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim(), code: digits }),
    });
    const body = (await res.json().catch(() => ({}))) as {
      ok?: boolean;
      email?: string;
      session_token?: string;
      profile?: { email?: string; nickname?: string };
      detail?: string;
    };
    if (!res.ok) {
      return { ok: false, reason: body.detail ?? `otp_verify_failed_${res.status}` };
    }
    const profile = useAppStore.getState().localProfile;
    const sessionToken = (body.session_token ?? '').trim();
    if (!sessionToken && requireCloudAuth) {
      return {
        ok: false,
        reason: 'BFF did not return session_token. Update BFF OTP verify / sessions store.',
      };
    }
    useAppStore.getState().setLocalProfile({
      ...profile,
      email: body.profile?.email ?? email.trim(),
      nickname: body.profile?.nickname ?? profile.nickname,
    });
    if (sessionToken) {
      useAppStore.getState().setSessionToken(sessionToken);
    }
    return {
      ok: true,
      email: body.email ?? email.trim(),
      nickname: body.profile?.nickname,
      sessionToken: sessionToken || undefined,
    };
  } catch (e) {
    return { ok: false, reason: e instanceof Error ? e.message : String(e) };
  }
}

export function resolveAuthApiHint(): string {
  const { url } = authBase();
  return url || '(set Production BFF URL in Lab, or EXPO_PUBLIC_DEV_BFF_URL)';
}

export type OAuthResult =
  | { ok: true; email: string; sessionToken?: string }
  | { ok: false; reason: string };

export async function completeOAuthLogin(
  provider: 'apple' | 'google',
  identityToken: string,
): Promise<OAuthResult> {
  const { url } = authBase();
  if (!url) {
    return {
      ok: false,
      reason: 'BFF URL missing. Set EXPO_PUBLIC_DEV_BFF_URL (preview) or Lab Apply before Apple/Google sign-in.',
    };
  }
  try {
    const res = await fetch(`${url}/v1/auth/oauth`, {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, identity_token: identityToken }),
    });
    const body = (await res.json().catch(() => ({}))) as {
      email?: string;
      session_token?: string;
      profile?: { email?: string; nickname?: string };
      detail?: string;
    };
    if (!res.ok) {
      return { ok: false, reason: body.detail ?? `oauth_failed_${res.status}` };
    }
    const email = (body.profile?.email ?? body.email ?? '').trim();
    const profile = useAppStore.getState().localProfile;
    useAppStore.getState().setLocalProfile({
      ...profile,
      email: email || profile.email,
      nickname: body.profile?.nickname ?? profile.nickname,
    });
    const sessionToken = (body.session_token ?? '').trim();
    if (sessionToken) {
      useAppStore.getState().setSessionToken(sessionToken);
    }
    return { ok: true, email, sessionToken: sessionToken || undefined };
  } catch (e) {
    return { ok: false, reason: e instanceof Error ? e.message : String(e) };
  }
}
