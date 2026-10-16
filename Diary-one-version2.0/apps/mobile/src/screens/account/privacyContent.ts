import Constants from 'expo-constants';
import type { PrivacyDetailSection } from '../../navigation/types';

export const PRIVACY_SECTION_COPY: Record<
  PrivacyDetailSection,
  { title: string; body: string }
> = {
  stored_memories: {
    title: 'Stored Memories & Captured by You',
    body:
      'Curated memories, small memories, topics, and manual Captured by You originals are stored on this iPhone. Sync and cloud processing may temporarily use recordings; automatic raw clips that are not selected are not kept long-term.',
  },
  memory_profile: {
    title: 'Memory Profile & Stories',
    body:
      'Your nickname, memory preferences, and “what you remember” edits are stored locally and may be included when you export data. They influence expression only when supporting facts exist. An optional setup survey writes into the same preferences — it never invents moments you did not capture.',
  },
  export_data: {
    title: 'Export My Data',
    body:
      'Export a JSON snapshot of local Diary One data from this device. Export does not include cloud account credentials or research API tokens unless you choose to share them separately.',
  },
  delete_account: {
    title: 'Delete Account & Data',
    body:
      'Cloud account deletion is not available in this build. You can delete all local data from this iPhone, which clears memories, originals, profile, and settings to an empty library (demo seed is not restored).',
  },
  privacy_policy: {
    title: 'Privacy Policy',
    body:
      'Diary One processes recordings to create memories you can revisit. Signing in is not cloud-upload consent: uploading selected evidence requires a separate agreement (recorded with a version).',
  },
  terms: {
    title: 'Terms',
    body: 'Terms of use apply when you use Diary One and related cloud services.',
  },
};

/** Shown when the published URL env is not set (dev / pre-launch builds). */
export const PRIVACY_URL_PENDING_NOTE =
  'The full published page is not linked in this build yet. Cloud evidence upload still uses the in-app consent on Privacy & Data.';

export const TERMS_URL_PENDING_NOTE =
  'The full published page is not linked in this build yet. By continuing in Sign in you acknowledge these terms will apply when the service is live.';

function trimEnv(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function extraField(key: string): string {
  const extra = Constants.expoConfig?.extra as Record<string, unknown> | undefined;
  return trimEnv(extra?.[key]);
}

/**
 * Published privacy policy HTTPS URL.
 * Env: EXPO_PUBLIC_PRIVACY_POLICY_URL or EXPO_PUBLIC_PRIVACY_URL (alias).
 * Empty → in-app copy + pending note (no dead link).
 */
export function privacyPolicyUrl(): string {
  return (
    trimEnv(process.env.EXPO_PUBLIC_PRIVACY_POLICY_URL) ||
    trimEnv(process.env.EXPO_PUBLIC_PRIVACY_URL) ||
    extraField('privacyPolicyUrl')
  );
}

/**
 * Published terms HTTPS URL.
 * Env: EXPO_PUBLIC_TERMS_URL.
 * Empty → in-app copy + pending note (no dead link).
 */
export function termsUrl(): string {
  return trimEnv(process.env.EXPO_PUBLIC_TERMS_URL) || extraField('termsUrl');
}
