import * as SQLite from 'expo-sqlite';

import type { Chapter, SmallMemory, Topic, MemoryPreference, CapturedOriginal, TodayStatus } from '../model';

import type { LocalProfile } from '../domain/localProfile';

import { DEFAULT_LOCAL_PROFILE } from '../domain/localProfile';

import type { PipelineTask } from '../pipeline/types';

import type { DeviceLinkState } from '../store/useAppStore';
import type { BundleExportVersion } from '../pipeline/bundleTypes';
import type { AssetLedgerEntry } from './assetLedger';

import {

  DEFAULT_LANGUAGE,

  DEFAULT_NOTIFICATION_SETTINGS,

  type LanguagePreference,

  type NotificationSettings,

} from '../domain/appSettings';



const DB_NAME = 'diary_one_v1.db';



export type PersistedSnapshot = {

  chapters: Chapter[];

  smallMemoriesByDate: Record<string, SmallMemory[]>;

  topics: Topic[];

  preferences: MemoryPreference[];

  localProfile: LocalProfile;

  researchEndpoint: string;

  researchToken: string;

  productionApiBaseUrl?: string;

  productionApiToken?: string;

  sessionToken?: string;

  cloudProcessingTarget?: import('../backend/types').CloudProcessingTarget;

  capturedOriginals: CapturedOriginal[];

  todayStatus?: TodayStatus;

  pipelineTasks?: PipelineTask[];

  deviceLinkState?: DeviceLinkState;

  devicePendingRecordings?: boolean;

  lastSyncedAt?: string | null;

  notificationSettings?: NotificationSettings;

  language?: LanguagePreference;

  memoryLanguage?: import('../domain/appSettings').MemoryLanguagePreference;

  automaticCaptureMode?: import('../domain/appSettings').AutomaticCaptureMode;

  historyVisibleCount?: number;

  bundleExportVersion?: BundleExportVersion;

  onboardingComplete?: boolean;

  pipelineAssetLedger?: AssetLedgerEntry[];

};



let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;



async function getDb() {

  if (!dbPromise) dbPromise = SQLite.openDatabaseAsync(DB_NAME);

  return dbPromise;

}



export async function initDatabase(): Promise<void> {

  const db = await getDb();

  await db.execAsync(`

    CREATE TABLE IF NOT EXISTS app_snapshot (

      id INTEGER PRIMARY KEY CHECK (id = 1),

      json TEXT NOT NULL,

      updated_at TEXT NOT NULL

    );

  `);

}



export async function loadSnapshot(): Promise<PersistedSnapshot | null> {

  const db = await getDb();

  const row = await db.getFirstAsync<{ json: string }>(

    'SELECT json FROM app_snapshot WHERE id = 1',

  );

  if (!row?.json) return null;

  try {

    return JSON.parse(row.json) as PersistedSnapshot;

  } catch {

    return null;

  }

}



export async function saveSnapshot(snapshot: PersistedSnapshot): Promise<void> {

  const db = await getDb();

  const json = JSON.stringify(snapshot);

  await db.runAsync(

    `INSERT INTO app_snapshot (id, json, updated_at) VALUES (1, ?, ?)

     ON CONFLICT(id) DO UPDATE SET json = excluded.json, updated_at = excluded.updated_at`,

    json,

    new Date().toISOString(),

  );

}



export async function clearSnapshot(): Promise<void> {

  const db = await getDb();

  await db.runAsync('DELETE FROM app_snapshot WHERE id = 1');

}



export function emptySnapshot(): PersistedSnapshot {

  return {

    chapters: [],

    smallMemoriesByDate: {},

    topics: [],

    preferences: [],

    localProfile: DEFAULT_LOCAL_PROFILE,

    researchEndpoint: '',

    researchToken: '',

    sessionToken: '',

    capturedOriginals: [],

    todayStatus: 'READY',

    pipelineTasks: [],

    deviceLinkState: 'disconnected',

    devicePendingRecordings: false,

    lastSyncedAt: null,

    notificationSettings: DEFAULT_NOTIFICATION_SETTINGS,

    language: DEFAULT_LANGUAGE,

    historyVisibleCount: 3,

    bundleExportVersion: 'V04',

  };

}


