import { useAppStore } from '../store/useAppStore';
import type { AuthOutcome } from './types';

/** ACC03 placeholder — stores email on device after OTP; no remote IdP in this build. */
export function verifyEmailOtpLocal(email: string, code: string): AuthOutcome {
  const digits = code.replace(/\D/g, '');
  if (digits.length < 6) {
    return { ok: false, reason: 'invalid_code' };
  }
  const profile = useAppStore.getState().localProfile;
  useAppStore.getState().setLocalProfile({
    ...profile,
    email: email.trim(),
  });
  return { ok: true };
}

export function oauthProviderUnavailable(provider: string): void {
  // Caller shows Alert — keeps copy in screen layer per Figma.
  void provider;
}
