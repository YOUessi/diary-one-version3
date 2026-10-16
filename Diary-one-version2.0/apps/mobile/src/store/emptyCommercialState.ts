/**
 * PRD DIA02 / TOP01 / CAP01 / PRI03 — commercial cold start is an honest empty library.
 * Figma demo seed (Fishing etc.) is Lab-only via applyLabDemoSeed(), never default.
 */
import { diaryTodayKey } from '../domain/dayKey';
import { DEFAULT_LOCAL_PROFILE } from '../domain/localProfile';
import {
  DEFAULT_LANGUAGE,
  DEFAULT_MEMORY_LANGUAGE,
  DEFAULT_AUTOMATIC_CAPTURE_MODE,
  DEFAULT_NOTIFICATION_SETTINGS,
} from '../domain/appSettings';
import type {
  Chapter,
  SmallMemory,
  Topic,
  MemoryPreference,
  CapturedOriginal,
  TodayStatus,
} from '../model';
import type { PipelineTask } from '../pipeline/types';

export type CommercialEmptySlice = {
  todayStatus: TodayStatus;
  chapters: Chapter[];
  smallMemoriesByDate: Record<string, SmallMemory[]>;
  topics: Topic[];
  preferences: MemoryPreference[];
  capturedOriginals: CapturedOriginal[];
  pipelineTasks: PipelineTask[];
  localProfile: typeof DEFAULT_LOCAL_PROFILE;
  deviceLinkState: 'disconnected';
  devicePendingRecordings: false;
  lastSyncedAt: null;
  notificationSettings: typeof DEFAULT_NOTIFICATION_SETTINGS;
  language: typeof DEFAULT_LANGUAGE;
  memoryLanguage: typeof DEFAULT_MEMORY_LANGUAGE;
  automaticCaptureMode: typeof DEFAULT_AUTOMATIC_CAPTURE_MODE;
  historyVisibleCount: number;
  bundleExportVersion: 'V04';
  onboardingComplete: boolean;
  preferenceSurveyComplete: boolean;
  cloudEvidenceConsent: null;
  cloudEvidenceConsentVersion: null;
  selectedDateKey: string;
};

export function commercialEmptySlice(opts?: { onboardingComplete?: boolean }): CommercialEmptySlice {
  return {
    todayStatus: 'NO_RECORDINGS',
    chapters: [],
    smallMemoriesByDate: {},
    topics: [],
    preferences: [],
    capturedOriginals: [],
    pipelineTasks: [],
    localProfile: DEFAULT_LOCAL_PROFILE,
    deviceLinkState: 'disconnected',
    devicePendingRecordings: false,
    lastSyncedAt: null,
    notificationSettings: DEFAULT_NOTIFICATION_SETTINGS,
    language: DEFAULT_LANGUAGE,
    memoryLanguage: DEFAULT_MEMORY_LANGUAGE,
    automaticCaptureMode: DEFAULT_AUTOMATIC_CAPTURE_MODE,
    historyVisibleCount: 3,
    bundleExportVersion: 'V04',
    onboardingComplete: opts?.onboardingComplete ?? false,
    preferenceSurveyComplete: false,
    cloudEvidenceConsent: null,
    cloudEvidenceConsentVersion: null,
    selectedDateKey: diaryTodayKey(),
  };
}
