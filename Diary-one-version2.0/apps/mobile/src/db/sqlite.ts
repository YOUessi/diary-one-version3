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

  preferenceSurveyComplete?: boolean;
  preferenceSurveyResponse?: import('../model').PreferenceSurveyResponse | null;

  cloudEvidenceConsent?: boolean | null;

  cloudEvidenceConsentVersion?: string | null;

  pipelineAssetLedger?: AssetLedgerEntry[];

};



let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;



async function getDb() {

  if (!dbPromise) dbPromise = SQLite.openDatabaseAsync(DB_NAME).catch((error) => { dbPromise = null; throw error; });

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

    CREATE TABLE IF NOT EXISTS local_actions (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      cleanup_pending INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS raw_assets (
      original_sha256 TEXT PRIMARY KEY NOT NULL,
      asset_key TEXT NOT NULL,
      media_kind TEXT NOT NULL,
      file_name TEXT,
      byte_size INTEGER,
      first_seen_at TEXT NOT NULL,
      last_seen_at TEXT NOT NULL,
      use_count INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS story_revisions (
      owner TEXT NOT NULL,
      chapter_id TEXT NOT NULL,
      revision INTEGER NOT NULL,
      text TEXT,
      previous_text TEXT,
      created_at TEXT NOT NULL,
      PRIMARY KEY (owner, chapter_id, revision)
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

    const snapshot = JSON.parse(row.json) as PersistedSnapshot;
    const notes = await db.getAllAsync<{ chapter_id: string; revision: number; text: string | null }>(
      `SELECT chapter_id, revision, text FROM story_revisions WHERE owner = ?
       ORDER BY revision ASC`,
      storyOwner(snapshot.localProfile),
    );
    const latest = new Map(notes.map((note) => [note.chapter_id, note]));
    snapshot.chapters = snapshot.chapters.map((chapter) => {
      const note = latest.get(chapter.id);
      return note ? { ...chapter, yourStory: note.text ?? undefined, yourStoryRevision: note.revision } : chapter;
    });
    return snapshot;

  } catch (error) {
    // A read failure must never be treated as a new empty library.
    throw new Error(`Could not load saved data: ${error instanceof Error ? error.message : String(error)}`);
  }

}



export type PublishedAsset = { asset_id?: string; original_sha256?: string; media_kind?: string;
  source_display_name?: string; original_bytes?: number };

export async function saveSnapshot(snapshot: PersistedSnapshot, assertCurrent?: () => void,
  publishedAssets?: PublishedAsset[]): Promise<void> {

  const db = await getDb();

  const json = JSON.stringify(snapshot);

  if (assertCurrent || publishedAssets) {
    await db.withExclusiveTransactionAsync(async (tx) => {
      assertCurrent?.();
      await tx.runAsync(
        `INSERT INTO app_snapshot (id, json, updated_at) VALUES (1, ?, ?)
         ON CONFLICT(id) DO UPDATE SET json = excluded.json, updated_at = excluded.updated_at`,
        json, new Date().toISOString(),
      );
      const now = new Date().toISOString();
      for (const asset of publishedAssets ?? []) {
        const sha = asset.original_sha256?.trim();
        if (!sha) throw new Error('Published asset is missing its content hash.');
        await tx.runAsync(
          `INSERT INTO raw_assets (original_sha256, asset_key, media_kind, file_name, byte_size,
            first_seen_at, last_seen_at, use_count) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
           ON CONFLICT(original_sha256) DO UPDATE SET last_seen_at=excluded.last_seen_at`,
          sha, asset.asset_id ?? sha.slice(0, 12), asset.media_kind ?? 'UNKNOWN',
          asset.source_display_name ?? null, asset.original_bytes ?? null, now, now,
        );
      }
      assertCurrent?.();
    });
    return;
  }

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
  await db.runAsync('DELETE FROM story_revisions');
  await db.runAsync('DELETE FROM raw_assets');

}

export async function setLocalCleanupPending(pending: boolean): Promise<void> {
  const db = await getDb();
  await db.runAsync('INSERT INTO local_actions (id, cleanup_pending) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET cleanup_pending = excluded.cleanup_pending', pending ? 1 : 0);
}

export async function hasLocalCleanupPending(): Promise<boolean> {
  const db = await getDb();
  const row = await db.getFirstAsync<{ cleanup_pending: number }>('SELECT cleanup_pending FROM local_actions WHERE id = 1');
  return row?.cleanup_pending === 1;
}

export function storyOwner(profile: LocalProfile): string {
  return profile.email?.trim().toLowerCase() || 'local-profile';
}

/** Durable optimistic write. Removal appends a tombstone with recoverable previous text. */
export async function commitStoryRevision(input: {
  owner: string;
  chapterId: string;
  expectedRevision: number;
  text: string | undefined;
  previousText: string | undefined;
  assertCurrent: () => void;
}): Promise<number> {
  const db = await getDb();
  const next = input.expectedRevision + 1;
  await db.withExclusiveTransactionAsync(async (tx) => {
    input.assertCurrent();
    const current = await tx.getFirstAsync<{ revision: number }>(
      'SELECT revision FROM story_revisions WHERE owner = ? AND chapter_id = ? ORDER BY revision DESC LIMIT 1',
      input.owner, input.chapterId,
    );
    if ((current?.revision ?? 0) !== input.expectedRevision) {
      throw new Error('Your note changed. Close the editor and reopen it before saving.');
    }
    input.assertCurrent();
    await tx.runAsync(
      'INSERT INTO story_revisions (owner, chapter_id, revision, text, previous_text, created_at) VALUES (?, ?, ?, ?, ?, ?)',
      input.owner, input.chapterId, next, input.text ?? null, input.previousText ?? null, new Date().toISOString(),
    );
    input.assertCurrent();
  });
  return next;
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


