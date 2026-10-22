/**
 * PRD：App 端去重 — 会话内 + 历史 original_sha256 账本。
 * 同一内容只生成一次最小 Evidence，避免重复压缩/抽帧/上云扣费。
 */
import { sha256File } from './sha256File';
import { ensureLocalFileUri } from './ensureLocalFileUri';
import { findRawAssetBySha, upsertRawAsset } from '../db/rawAssetLedger';
import type { PickedMedia } from './types';

export type DedupeResult = {
  unique: PickedMedia[];
  skippedSessionDupes: number;
  skippedLedgerDupes: number;
};

export async function dedupePickedMedia(
  items: PickedMedia[],
  options?: { skipKnownLedger?: boolean; assertActive?: () => void; onProgress?: (index: number, total: number) => void },
): Promise<DedupeResult> {
  const skipKnown = options?.skipKnownLedger !== false;
  const unique: PickedMedia[] = [];
  const seenSha = new Set<string>();
  let skippedSessionDupes = 0;
  let skippedLedgerDupes = 0;

  for (let i = 0; i < items.length; i++) {
    options?.assertActive?.();
    options?.onProgress?.(i + 1, items.length);
    const item = items[i];
    const localUri = await ensureLocalFileUri(item.uri, `dedupe-${i}`);
    options?.assertActive?.();
    const sha = await sha256File(localUri);
    options?.assertActive?.();
    if (seenSha.has(sha)) {
      skippedSessionDupes += 1;
      continue;
    }
    seenSha.add(sha);

    if (skipKnown) {
      const known = await findRawAssetBySha(sha);
      options?.assertActive?.();
      if (known) {
        skippedLedgerDupes += 1;
        // 仍刷新 last_seen，便于审计
        await upsertRawAsset({
          originalSha256: sha,
          assetKey: known.assetKey,
          mediaKind:
            item.mediaType === 'video' ? 'VIDEO' : item.mediaType === 'image' ? 'PHOTO' : 'UNKNOWN',
          fileName: item.fileName,
          byteSize: item.fileSize,
        });
        continue;
      }
    }

    unique.push({ ...item, uri: localUri });
  }

  return { unique, skippedSessionDupes, skippedLedgerDupes };
}

export async function rememberRawAssetsFromBundleAssets(
  assets: {
    asset_id?: string;
    original_sha256?: string;
    media_kind?: string;
    source_display_name?: string;
    original_bytes?: number;
  }[],
): Promise<void> {
  for (const a of assets) {
    const sha = (a.original_sha256 ?? '').trim();
    if (!sha) continue;
    const kind =
      a.media_kind === 'VIDEO' ? 'VIDEO' : a.media_kind === 'PHOTO' ? 'PHOTO' : 'UNKNOWN';
    await upsertRawAsset({
      originalSha256: sha,
      assetKey: a.asset_id ?? sha.slice(0, 12),
      mediaKind: kind,
      fileName: a.source_display_name,
      byteSize: a.original_bytes,
    });
  }
}
