/**
 * PRD App 侧「稳定账本」：按 original_sha256 去重，避免同一素材重复入 Evidence / 重复上云。
 */
import * as SQLite from 'expo-sqlite';

const DB_NAME = 'diary_one_v1.db';

export type RawAssetRecord = {
  originalSha256: string;
  assetKey: string;
  mediaKind: 'PHOTO' | 'VIDEO' | 'UNKNOWN';
  fileName?: string;
  byteSize?: number;
  firstSeenAt: string;
  lastSeenAt: string;
  useCount: number;
};

let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;

async function getDb() {
  if (!dbPromise) dbPromise = SQLite.openDatabaseAsync(DB_NAME);
  return dbPromise;
}

export async function initRawAssetLedger(): Promise<void> {
  const db = await getDb();
  await db.execAsync(`
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
  `);
}

export async function findRawAssetBySha(sha: string): Promise<RawAssetRecord | null> {
  await initRawAssetLedger();
  const db = await getDb();
  const row = await db.getFirstAsync<{
    original_sha256: string;
    asset_key: string;
    media_kind: string;
    file_name: string | null;
    byte_size: number | null;
    first_seen_at: string;
    last_seen_at: string;
    use_count: number;
  }>('SELECT * FROM raw_assets WHERE original_sha256 = ?', [sha]);
  if (!row) return null;
  return {
    originalSha256: row.original_sha256,
    assetKey: row.asset_key,
    mediaKind: row.media_kind as RawAssetRecord['mediaKind'],
    fileName: row.file_name ?? undefined,
    byteSize: row.byte_size ?? undefined,
    firstSeenAt: row.first_seen_at,
    lastSeenAt: row.last_seen_at,
    useCount: row.use_count,
  };
}

export async function upsertRawAsset(input: {
  originalSha256: string;
  assetKey: string;
  mediaKind: RawAssetRecord['mediaKind'];
  fileName?: string;
  byteSize?: number;
}): Promise<{ created: boolean; record: RawAssetRecord }> {
  await initRawAssetLedger();
  const existing = await findRawAssetBySha(input.originalSha256);
  const now = new Date().toISOString();
  const db = await getDb();
  if (existing) {
    await db.runAsync(
      `UPDATE raw_assets SET last_seen_at = ?, use_count = use_count + 1,
        file_name = COALESCE(?, file_name), byte_size = COALESCE(?, byte_size)
       WHERE original_sha256 = ?`,
      [now, input.fileName ?? null, input.byteSize ?? null, input.originalSha256],
    );
    return {
      created: false,
      record: {
        ...existing,
        lastSeenAt: now,
        useCount: existing.useCount + 1,
        fileName: input.fileName ?? existing.fileName,
        byteSize: input.byteSize ?? existing.byteSize,
      },
    };
  }
  await db.runAsync(
    `INSERT INTO raw_assets
      (original_sha256, asset_key, media_kind, file_name, byte_size, first_seen_at, last_seen_at, use_count)
     VALUES (?, ?, ?, ?, ?, ?, ?, 1)`,
    [
      input.originalSha256,
      input.assetKey,
      input.mediaKind,
      input.fileName ?? null,
      input.byteSize ?? null,
      now,
      now,
    ],
  );
  return {
    created: true,
    record: {
      originalSha256: input.originalSha256,
      assetKey: input.assetKey,
      mediaKind: input.mediaKind,
      fileName: input.fileName,
      byteSize: input.byteSize,
      firstSeenAt: now,
      lastSeenAt: now,
      useCount: 1,
    },
  };
}

/** PRI03 / multi-user beta — wipe raw-asset dedupe ledger on logout. */
export async function clearRawAssetLedger(): Promise<void> {
  await initRawAssetLedger();
  const db = await getDb();
  await db.runAsync('DELETE FROM raw_assets');
}
