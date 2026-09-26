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
      'Cloud account deletion is not available in this build. You can delete all local data from this iPhone, which resets memories, originals, profile, and settings to the demo seed.',
  },
  privacy_policy: {
    title: 'Privacy Policy',
    body:
      'Diary One processes recordings to create memories you can revisit. Signing in is not cloud-upload consent: uploading selected evidence requires a separate agreement (recorded with a version). Policy details will be published with the App Store release. This build stores research API settings only on device.',
  },
  terms: {
    title: 'Terms',
    body:
      'Terms of use will be published with the App Store release. By continuing setup you acknowledged that policies apply when the service is live.',
  },
};
