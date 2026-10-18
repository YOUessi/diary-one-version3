import { Alert } from 'react-native';
import {
  initDatabase,
  loadSnapshot,
  saveSnapshot,
  clearSnapshot,
  setLocalCleanupPending,
  hasLocalCleanupPending,
  type PersistedSnapshot,
  type PublishedAsset,
} from '../db/sqlite';
import { clearAssetLedger, hydrateAssetLedger, serializeAssetLedger } from '../db/assetLedger';
import { clearLocalMediaFiles } from '../domain/localDataFiles';

import { useAppStore, buildPersistedSlice } from './useAppStore';
import { applyBundledMotion } from '../assets/motionAssets';

import {

  seedChapters,

  seedSmallMemories,

  seedTopics,

  seedPreferences,

  seedCaptured,

} from '../model';

import { diaryTodayKey } from '../domain/dayKey';
import { formatChapterDateLong } from '../domain/formatChapterDate';

import { DEFAULT_LOCAL_PROFILE, type LocalProfile } from '../domain/localProfile';
import { PHOTO_LIBRARY_TEST_SOURCE } from '../domain/mediaIntake';
import type { PipelineTask } from '../pipeline/types';
import { applyDevCloudDefaults } from '../config/applyDevCloudDefaults';
import { commercialEmptySlice } from './emptyCommercialState';
import { mergeDiaryDay } from '../domain/mergeDiaryDay';
import type { Chapter, SmallMemory, TodayStatus } from '../model';

import {

  DEFAULT_LANGUAGE,

  DEFAULT_MEMORY_LANGUAGE,

  DEFAULT_AUTOMATIC_CAPTURE_MODE,

  DEFAULT_NOTIFICATION_SETTINGS,

} from '../domain/appSettings';



function offsetDay(key: string, delta: number): string {

  const [y, m, d] = key.split('-').map(Number);

  const dt = new Date(y, m - 1, d);

  dt.setDate(dt.getDate() + delta);

  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;

}



function dateLabelForKey(dateKey: string): string {

  const [y, m, d] = dateKey.split('-').map(Number);

  const dt = new Date(y, m - 1, d);

  return dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

}



function shiftSeedDates() {

  const today = diaryTodayKey();

  const yesterday = offsetDay(today, -1);

  const twoDaysAgo = offsetDay(today, -2);



  const chapterDateById: Record<string, string> = {

    'ch-morning-fishing': today,

    'ch-afternoon-citywalk': today,

    'ch-dinner-friends': yesterday,

    'ch-studio-morning': twoDaysAgo,

    'ch-fishing-before-rain': offsetDay(today, -19),

    'ch-fishing-river-calm': offsetDay(today, -38),

    'ch-late-afternoon-water': offsetDay(today, -13),

  };



  const chapters = seedChapters.map((c) => {

    const dateKey = chapterDateById[c.id] ?? today;

    return { ...c, dateKey, dateLabel: dateLabelForKey(dateKey) };

  });



  const smallMemoriesByDate = {

    [today]: seedSmallMemories['2026-08-16'] ?? [],

    [yesterday]: seedSmallMemories['2026-08-15'] ?? [],

  };



  const capturedOriginals = seedCaptured.map((cap) => {
    const dateKey = cap.dateKey === '2026-08-16' ? today : yesterday;
    const timePart = cap.capturedAtLabel?.includes(' · ')
      ? cap.capturedAtLabel.split(' · ').slice(1).join(' · ')
      : undefined;
    const capturedAtLabel = timePart
      ? `${formatChapterDateLong(dateKey)} · ${timePart}`
      : formatChapterDateLong(dateKey);
    return { ...cap, dateKey, capturedAtLabel };
  });



  return { chapters, smallMemoriesByDate, capturedOriginals };

}



function normalizePipelineTasks(tasks: PipelineTask[] | undefined): PipelineTask[] {
  return (tasks ?? []).map((t) => ({
    ...t,
    dayRevisionId: t.dayRevisionId ?? `legacy-${t.id}`,
    intakeSource: t.intakeSource ?? PHOTO_LIBRARY_TEST_SOURCE,
  }));
}

function applySnapshotToStore(snap: PersistedSnapshot) {
  hydrateAssetLedger(snap.pipelineAssetLedger);

  useAppStore.setState({

    chapters: snap.chapters,

    smallMemoriesByDate: snap.smallMemoriesByDate,

    topics: snap.topics,

    preferences: snap.preferences.map((p) => ({
      ...p,
      title: p.title ?? p.text.slice(0, 24),
    })),

    localProfile: snap.localProfile,

    researchEndpoint: snap.researchEndpoint,

    researchToken: snap.researchToken,

    productionApiBaseUrl: snap.productionApiBaseUrl ?? '',

    productionApiToken: snap.productionApiToken ?? '',

    sessionToken: snap.sessionToken ?? '',

    cloudProcessingTarget: snap.cloudProcessingTarget ?? 'production',

    capturedOriginals: snap.capturedOriginals ?? [],

    todayStatus: snap.todayStatus ?? 'READY',

    pipelineTasks: normalizePipelineTasks(snap.pipelineTasks),

    deviceLinkState: snap.deviceLinkState ?? 'disconnected',

    devicePendingRecordings: snap.devicePendingRecordings ?? false,

    lastSyncedAt: snap.lastSyncedAt ?? null,

    notificationSettings: snap.notificationSettings ?? DEFAULT_NOTIFICATION_SETTINGS,

    language: snap.language ?? DEFAULT_LANGUAGE,

    memoryLanguage: snap.memoryLanguage ?? DEFAULT_MEMORY_LANGUAGE,

    automaticCaptureMode: snap.automaticCaptureMode ?? DEFAULT_AUTOMATIC_CAPTURE_MODE,

    historyVisibleCount: snap.historyVisibleCount ?? 3,

    bundleExportVersion: snap.bundleExportVersion ?? 'V04',

    onboardingComplete: snap.onboardingComplete ?? true,

    // Missing field must not imply "survey done" for commercial / beta (PRI01).
    preferenceSurveyComplete: snap.preferenceSurveyComplete ?? false,
    preferenceSurveyResponse: snap.preferenceSurveyResponse ?? null,

    cloudEvidenceConsent: snap.cloudEvidenceConsent ?? null,

    cloudEvidenceConsentVersion: snap.cloudEvidenceConsentVersion ?? null,

    selectedDateKey: diaryTodayKey(),

  });

}



/**
 * PRD DIA02 / CAP01 / PRI03 — commercial default is an empty honest library.
 * Demo Fishing seed is opt-in for Lab UI polish only (__DEV__).
 */
function applyCommercialEmpty(opts?: { onboardingComplete?: boolean }) {
  useAppStore.setState(commercialEmptySlice(opts));
}

/** Lab-only: load Figma demo seed. Never call from wipe / store release cold start. */
export function applyLabDemoSeed() {
  if (!__DEV__) return;
  const shifted = shiftSeedDates();
  useAppStore.setState({
    chapters: shifted.chapters,
    smallMemoriesByDate: shifted.smallMemoriesByDate,
    capturedOriginals: shifted.capturedOriginals,
    topics: seedTopics,
    preferences: seedPreferences,
    localProfile: DEFAULT_LOCAL_PROFILE,
    todayStatus: 'READY',
    pipelineTasks: [],
    deviceLinkState: 'disconnected',
    devicePendingRecordings: false,
    lastSyncedAt: null,
    notificationSettings: DEFAULT_NOTIFICATION_SETTINGS,
    language: DEFAULT_LANGUAGE,
    memoryLanguage: DEFAULT_MEMORY_LANGUAGE,
    automaticCaptureMode: DEFAULT_AUTOMATIC_CAPTURE_MODE,
    historyVisibleCount: 3,
    bundleExportVersion: 'V04',
    onboardingComplete: true,
    preferenceSurveyComplete: true,
    cloudEvidenceConsent: null,
    cloudEvidenceConsentVersion: null,
    selectedDateKey: diaryTodayKey(),
  });
}

function applyFreshSeed() {
  applyCommercialEmpty({ onboardingComplete: false });
}



let saveTimer: ReturnType<typeof setTimeout> | null = null;



export async function bootstrapStore(): Promise<void> {

  await initDatabase();

  if (await hasLocalCleanupPending()) {
    await resetLocalAppData();
    return;
  }
  const snap = await loadSnapshot();

  // Persist any prior snapshot (including empty commercial library). Only seed when no row.
  if (snap) {
    applySnapshotToStore(snap);
  } else {
    applyFreshSeed();
  }

  // PRD DEV01 / SYS02 — formal consumer App (incl. Expo Go): honest device + no research / shared token.
  try {
    const { showInternalLabTools, isFormalConsumerApp } = await import('../config/buildProfile');
    if (!showInternalLabTools) {
      useAppStore.setState({
        deviceLinkState: 'disconnected',
        devicePendingRecordings: false,
        lastSyncedAt: null,
        deviceBatteryPercent: null,
      });
    }
    if (isFormalConsumerApp) {
      useAppStore.setState({
        cloudProcessingTarget: 'production',
        researchEndpoint: '',
        researchToken: '',
        productionApiToken: '',
      });
    }
  } catch {
    /* ignore */
  }

  try {

    const withMotion = await applyBundledMotion(useAppStore.getState().chapters);

    useAppStore.setState({ chapters: withMotion });

  } catch {

    /* bundled clips missing */

  }

  applyDevCloudDefaults();

  // ACC03 — drop stale OTP sessions after BFF restart (UI must not stay "Signed in").
  try {
    const { isInternalBetaBuild, isStoreRelease } = await import('../config/buildProfile');
    const token = useAppStore.getState().sessionToken.trim();
    const url = useAppStore.getState().productionApiBaseUrl.trim();
    if (token && url && (isInternalBetaBuild || isStoreRelease)) {
      const { probeProductionSession } = await import('../backend/productionCloudService');
      const ok = await probeProductionSession(url, token);
      if (!ok) {
        useAppStore.setState({ sessionToken: '' });
      }
    }
  } catch {
    /* ignore */
  }

  // REL01 — resume any in-flight BFF jobs after process kill / cold start.
  try {
    const { resumeInFlightCloudJobs } = await import('../pipeline/runPipeline');
    resumeInFlightCloudJobs();
  } catch {
    /* ignore */
  }

}



let resetting = false;
let persistTail: Promise<void> = Promise.resolve();
let persistWarningOpen = false;

function reportPersistFailure(): void {
  if (persistWarningOpen || resetting) return;
  persistWarningOpen = true;
  Alert.alert('Could not save data', 'Some recent changes are still only in memory. Keep the app open and try saving again.', [
    { text: 'Close', onPress: () => { persistWarningOpen = false; } },
    { text: 'Try Again', onPress: () => { persistWarningOpen = false; void flushPersist().catch(reportPersistFailure); } },
  ]);
}

export async function resetLocalAppData(options?: { onboardingComplete?: boolean }): Promise<void> {
  if (resetting) throw new Error('Local cleanup is already in progress.');
  resetting = true;
  try {
    if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
    // Cancel publication from old async jobs before the first disk await.
    useAppStore.setState({ sessionToken: '', pipelineTasks: [] });
    await persistTail;
    await setLocalCleanupPending(true);
    applyCommercialEmpty({ onboardingComplete: options?.onboardingComplete ?? false });
    await clearSnapshot();
    await clearLocalMediaFiles();
    clearAssetLedger();

    // PRI03 / multi-user — also drop cloud credentials so next tester cannot reuse prior session.
    useAppStore.setState({
      sessionToken: '',
      productionApiToken: '',
      researchToken: '',
      researchEndpoint: '',
      cloudProcessingTarget: 'production',
      cloudEvidenceConsent: null,
      cloudEvidenceConsentVersion: null,
      deviceBatteryPercent: null,
      deviceLinkState: 'disconnected',
      devicePendingRecordings: false,
      lastSyncedAt: null,
    });

    try {

      const withMotion = await applyBundledMotion(useAppStore.getState().chapters);

      useAppStore.setState({ chapters: withMotion });

    } catch {

      /* ignore */

    }

    const s = useAppStore.getState();

    await saveSnapshot(buildPersistedSlice(s));
    await setLocalCleanupPending(false);
  } finally {
    resetting = false;
  }
}



export function schedulePersist(): void {
  if (resetting) return;

  if (saveTimer) clearTimeout(saveTimer);

  saveTimer = setTimeout(() => {

    void flushPersist().catch(reportPersistFailure);

  }, 400);

}

/** REL01 / ACC03 — flush OTP session & consent immediately (do not wait debounce). */
export async function flushPersist(completion?: { preferenceSurveyComplete: true; onboardingComplete?: true }): Promise<void> {
  if (resetting) {
    if (completion) throw new Error('Account data is being reset. Please reopen preferences.');
    return;
  }
  if (saveTimer) {
    clearTimeout(saveTimer);
    saveTimer = null;
  }
  const write = persistTail.then(() => {
    const s = useAppStore.getState();
    const snapshot = { ...buildPersistedSlice(s), ...completion, pipelineAssetLedger: serializeAssetLedger() };
    return saveSnapshot(snapshot);
  });
  persistTail = write.catch(() => {});
  await write;
}

/** Save before publishing profile changes; cancelled/account-switched writes roll back. */
export async function commitLocalProfile(profile: LocalProfile, assertCurrent: () => void): Promise<void> {
  if (resetting) throw new Error('Account data is being reset.');
  if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
  const write = persistTail.then(async () => {
    if (resetting) throw new Error('Account data is being reset.');
    assertCurrent();
    const snapshot = { ...buildPersistedSlice(useAppStore.getState()), localProfile: profile,
      pipelineAssetLedger: serializeAssetLedger() };
    await saveSnapshot(snapshot, assertCurrent);
    assertCurrent();
    useAppStore.setState({ localProfile: profile });
  });
  persistTail = write.catch(() => {});
  await write;
}

/** Diary, successful task and dedupe hashes share a single SQLite transaction. */
export async function commitDiaryBatch(input: {
  taskId: string; dayKey: string; sourceBatchId: string;
  chapters: Chapter[]; smallMemories: SmallMemory[]; preservePriorIfIncomingEmpty: boolean;
  todayStatus?: TodayStatus; assets: PublishedAsset[]; assertCurrent: () => void;
}): Promise<void> {
  if (resetting) throw new Error('Account data is being reset.');
  if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
  const write = persistTail.then(async () => {
    input.assertCurrent();
    const before = useAppStore.getState();
    const update = mergeDiaryDay(before, input.dayKey, input.chapters, input.smallMemories, {
      preservePriorIfIncomingEmpty: input.preservePriorIfIncomingEmpty,
      sourceBatchId: input.sourceBatchId,
    });
    const patch = { ...update,
      ...(input.todayStatus ? { todayStatus: input.todayStatus } : {}),
      pipelineTasks: before.pipelineTasks.map((task) => task.id === input.taskId
        ? { ...task, status: 'succeeded' as const, error: undefined, message: 'Diary saved' } : task),
    };
    const guard = () => {
      input.assertCurrent();
      if (resetting || useAppStore.getState().chapters !== before.chapters ||
          useAppStore.getState().smallMemoriesByDate !== before.smallMemoriesByDate) {
        throw new Error('Diary changed while saving. Please retry the import.');
      }
    };
    const snapshot = { ...buildPersistedSlice(before), ...patch, pipelineAssetLedger: serializeAssetLedger() };
    await saveSnapshot(snapshot, guard, input.assets);
    useAppStore.setState(patch);
  });
  persistTail = write.catch(() => {});
  await write;
}



const PERSIST_KEYS: (keyof ReturnType<typeof buildPersistedSlice>)[] = [

  'chapters',

  'smallMemoriesByDate',

  'topics',

  'preferences',

  'localProfile',

  'researchEndpoint',

  'researchToken',

  'productionApiBaseUrl',

  'productionApiToken',

  'sessionToken',

  'cloudProcessingTarget',

  'capturedOriginals',

  'todayStatus',

  'pipelineTasks',

  'deviceLinkState',

  'devicePendingRecordings',

  'lastSyncedAt',

  'notificationSettings',

  'language',

  'memoryLanguage',

  'automaticCaptureMode',

  'historyVisibleCount',

  'bundleExportVersion',

  'onboardingComplete',

  'preferenceSurveyComplete',
  'preferenceSurveyResponse',

  'cloudEvidenceConsent',

  'cloudEvidenceConsentVersion',

];



const FLUSH_NOW_KEYS: (keyof ReturnType<typeof buildPersistedSlice>)[] = [
  'sessionToken',
  'cloudEvidenceConsent',
  'cloudEvidenceConsentVersion',
  'localProfile',
  'productionApiBaseUrl',
];

export function subscribePersist(): () => void {

  return useAppStore.subscribe((state, prev) => {

    const slice = buildPersistedSlice(state);

    const prevSlice = buildPersistedSlice(prev);

    const changed = PERSIST_KEYS.some((k) => slice[k] !== prevSlice[k]);

    if (!changed) return;

    const critical = FLUSH_NOW_KEYS.some((k) => slice[k] !== prevSlice[k]);
    if (critical) {
      void flushPersist().catch(reportPersistFailure);
      return;
    }
    schedulePersist();

  });

}


