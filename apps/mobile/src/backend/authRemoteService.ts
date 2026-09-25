import { useAppStore } from '../store/useAppStore';

function authBase(): { url: string; token: string } {
  const s = useAppStore.getState();
  const fromStore = s.productionApiBaseUrl.trim();
  const fromEnv = (process.env.EXPO_PUBLIC_DEV_BFF_URL ?? '').trim();
  const url = fromStore || fromEnv;
  const token = s.productionApiToken.trim() || (process.env.EXPO_PUBLIC_DEV_BFF_TOKEN ?? 'dev-token');
  return { url: url.replace(/\/+$/, ''), token };
}

export type OtpRequestResult =
  | { ok: true; email: string; devCode?: string; message: string }
  | { ok: false; reason: string };

export type OtpVerifyResult =
  | { ok: true; email: string; nickname?: string }
  | { ok: false; reason: string };

/** ACC03 — BFF Dev Lite / production OTP. Falls back to local-only when BFF unset. */
export async function requestEmailOtp(email: string): Promise<OtpRequestResult> {
  const trimmed = email.trim();
  if (!trimmed.includes('@')) {
    return { ok: false, reason: 'invalid_email' };
  }
  const { url } = authBase();
  if (!url) {
    return {
      ok: true,
      email: trimmed,
      message: 'No BFF URL — use any 6-digit code (local-only mode).',
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
    // Local-only fallback for UI walkthrough without BFF
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
      profile?: { email?: string; nickname?: string };
      detail?: string;
    };
    if (!res.ok) {
      return { ok: false, reason: body.detail ?? `otp_verify_failed_${res.status}` };
    }
    const profile = useAppStore.getState().localProfile;
    useAppStore.getState().setLocalProfile({
      ...profile,
      email: body.profile?.email ?? email.trim(),
      nickname: body.profile?.nickname ?? profile.nickname,
    });
    return { ok: true, email: body.email ?? email.trim(), nickname: body.profile?.nickname };
  } catch (e) {
    return { ok: false, reason: e instanceof Error ? e.message : String(e) };
  }
}

export function resolveAuthApiHint(): string {
  const { url } = authBase();
  return url || '(set Production BFF URL in Lab, or EXPO_PUBLIC_DEV_BFF_URL)';
}
