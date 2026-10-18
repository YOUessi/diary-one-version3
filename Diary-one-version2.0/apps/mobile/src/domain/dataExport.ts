import type { PersistedSnapshot } from '../db/sqlite';

/** Public export is deliberately separate from the credential-bearing backup format. */
export function buildUserDataExport(snapshot: PersistedSnapshot) {
  return {
    chapters: snapshot.chapters,
    smallMemoriesByDate: snapshot.smallMemoriesByDate,
    topics: snapshot.topics,
    preferences: snapshot.preferences,
    localProfile: snapshot.localProfile,
    capturedOriginals: snapshot.capturedOriginals,
    notificationSettings: snapshot.notificationSettings,
    language: snapshot.language,
    memoryLanguage: snapshot.memoryLanguage,
    cloudEvidenceConsent: snapshot.cloudEvidenceConsent,
    cloudEvidenceConsentVersion: snapshot.cloudEvidenceConsentVersion,
  };
}
