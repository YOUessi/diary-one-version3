import {
  initDatabase,
  loadSnapshot,
  saveSnapshot,
  clearSnapshot,
  type PersistedSnapshot,
} from '../db/sqlite';
import { hydrateAssetLedger, serializeAssetLedger } from '../db/assetLedger';

import { useAppStore, buildPersistedSlice } from './useAppStore';

import {

  seedChapters,

  seedSmallMemories,

  seedTopics,

  seedPreferences,

  seedCaptured,

} from '../model';

import { diaryTodayKey } from '../domain/dayKey';

import { DEFAULT_LOCAL_PROFILE } from '../domain/localProfile';
import { PHOTO_LIBRARY_TEST_SOURCE } from '../domain/mediaIntake';
import type { PipelineTask } from '../pipeline/types';
import { applyDevCloudDefaults } from '../config/applyDevCloudDefaults';

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

    return { ...cap, dateKey };

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

    cloudProcessingTarget: snap.cloudProcessingTarget ?? 'research',

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

    selectedDateKey: diaryTodayKey(),

  });

}



function applyFreshSeed() {

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

    onboardingComplete: false,

    selectedDateKey: diaryTodayKey(),

  });

}



let saveTimer: ReturnType<typeof setTimeout> | null = null;



export async function bootstrapStore(): Promise<void> {

  await initDatabase();

  const snap = await loadSnapshot();

  if (snap && snap.chapters.length > 0) {

    applySnapshotToStore(snap);

  } else {

    applyFreshSeed();

  }

  applyDevCloudDefaults();

}



export async function resetLocalAppData(): Promise<void> {

  await clearSnapshot();

  applyFreshSeed();

  const s = useAppStore.getState();

  await saveSnapshot(buildPersistedSlice(s));

}



export function schedulePersist(): void {

  if (saveTimer) clearTimeout(saveTimer);

  saveTimer = setTimeout(() => {

    const s = useAppStore.getState();

    void saveSnapshot({
      ...buildPersistedSlice(s),
      pipelineAssetLedger: serializeAssetLedger(),
    });

  }, 400);

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

];



export function subscribePersist(): () => void {

  return useAppStore.subscribe((state, prev) => {

    const slice = buildPersistedSlice(state);

    const prevSlice = buildPersistedSlice(prev);

    const changed = PERSIST_KEYS.some((k) => slice[k] !== prevSlice[k]);

    if (changed) schedulePersist();

  });

}


