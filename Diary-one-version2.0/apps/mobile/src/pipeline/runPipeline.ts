import * as FileSystem from 'expo-file-system/legacy';
import { Alert } from 'react-native';
import { buildAppLibraryBundle } from './buildAppLibraryBundle';
import type { PickedMedia, PipelineTask } from './types';
import { useAppStore } from '../store/useAppStore';
import { checkResearchHealth } from '../cloud/researchClient';
import { submitResearchPreview } from '../backend/researchCloudService';
import { submitProductionDayRevision, pollProductionCloudJob, checkProductionHealth } from '../backend/productionCloudService';
import type { CloudProcessingTarget } from '../backend/types';
import { mapPreviewToDiary } from '../cloud/mapPreviewResult';
import { validatePreviewResult } from '../cloud/validatePreviewResult';
import { commitDiaryBatch, flushPersist } from '../store/hydrate';
import { mapTodayStatusFromPreview } from '../cloud/mapTodayStatus';
import { diaryTodayKey } from '../domain/dayKey';
import {
  createStableDayRevisionId,
  selectionFingerprint,
} from '../domain/dayRevision';
import { PHOTO_LIBRARY_TEST_SOURCE, type MediaIntakeSource } from '../domain/mediaIntake';
import { attachChapterMediaFromBundle } from './attachChapterMedia';
import { rememberPipelineTask } from '../db/ledger';
import { recordPipelineLedger } from '../db/assetLedger';
import { requireProductionBearer, resolveProductionBearer } from '../backend/resolveProductionBearer';
import { isFormalConsumerApp, isLabToolsEnabled } from '../config/buildProfile';

import { groupMediaByDay } from '../domain/importDays';
import { scopeImportedMemories } from '../domain/scopeImportedMemories';
import { capturedImports } from '../domain/capturedImports';
import { sha256SubmittedManifest } from './sha256File';

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const activeRunners = new Set<string>();

function rejectMockBff(): boolean {
  // Formal consumer App (Expo Go default / beta / store) never accepts mock.
  return isFormalConsumerApp;
}

function resolveCloudTarget(): {
  target: CloudProcessingTarget;
  endpoint: string;
  token: string;
} {
  const s = useAppStore.getState();
  const productionUrl = s.productionApiBaseUrl.trim();
  const researchUrl = s.researchEndpoint.trim();

  // Formal App: Production BFF only (PRD SYS02).
  if (isFormalConsumerApp) {
    return {
      target: 'production',
      endpoint: productionUrl,
      token: resolveProductionBearer(),
    };
  }

  if (s.cloudProcessingTarget === 'production' || (productionUrl && !researchUrl)) {
    if (productionUrl) {
      return {
        target: 'production',
        endpoint: productionUrl,
        token: resolveProductionBearer(),
      };
    }
  }

  if (isLabToolsEnabled && s.cloudProcessingTarget === 'research' && researchUrl) {
    return {
      target: 'research',
      endpoint: researchUrl,
      token: s.researchToken,
    };
  }

  if (productionUrl) {
    return {
      target: 'production',
      endpoint: productionUrl,
      token: resolveProductionBearer(),
    };
  }
  if (isLabToolsEnabled && researchUrl) {
    return {
      target: 'research',
      endpoint: researchUrl,
      token: s.researchToken,
    };
  }

  return { target: 'production', endpoint: '', token: resolveProductionBearer() };
}

async function pollUntilDone(
  endpoint: string,
  token: string,
  taskId: string,
  jobId: string,
  assertOwner: () => void,
) {
  for (let i = 0; i < 180; i++) {
    assertOwner();
    if (!useAppStore.getState().pipelineTasks.some((task) => task.id === taskId)) {
      throw new Error('Import cancelled.');
    }
    const poll = await pollProductionCloudJob(endpoint, token, jobId);
    assertOwner();
    if (poll.state === 'paused') throw new Error(`CLOUD_JOB_PAUSED:${poll.message}`);
    if (poll.state === 'succeeded') {
      if (!poll.result) {
        throw new Error('Cloud job succeeded but returned no result payload');
      }
      return poll.result;
    }
    if (poll.state === 'failed') {
      throw new Error(`CLOUD_JOB_FAILED:${poll.message || 'Cloud job failed'}`);
    }
    if (i % 2 === 0) {
      patchTask(taskId, {
        status: 'cloud_processing',
        message: poll.message ? `Cloud: ${poll.message}` : `Polling job… (${i + 1})`,
      });
    }
    await sleep(1500);
  }
  throw new Error('Production job timed out while polling (4.5 min)');
}

async function runCloudPreview(
  target: CloudProcessingTarget,
  endpoint: string,
  token: string,
  taskId: string,
  bundleDir: string,
  jsonPath: string,
  dayRevisionId: string,
  assertOwner: () => void,
) {
  if (target === 'production') {
    const bearer = token || requireProductionBearer();
    const existingJob = useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)
      ?.productionJobId;
    // REL01 — resume original job if we already submitted (no new billable task).
    if (existingJob) {
      patchTask(taskId, {
        status: 'cloud_processing',
        message: `Resuming job ${existingJob.slice(0, 8)}…`,
      });
      return pollUntilDone(endpoint, bearer, taskId, existingJob, assertOwner);
    }
    assertOwner();
    const { jobId } = await submitProductionDayRevision(
      endpoint, bearer, dayRevisionId, bundleDir, jsonPath,
    );
    assertOwner();
    patchTask(taskId, {
      status: 'cloud_processing', productionJobId: jobId, dayRevisionId,
      message: `Uploaded · job ${jobId.slice(0, 8)}…`,
    });
    // Persist the accepted job before waiting for its result. Lost acknowledgements
    // retry the same frozen revision; a 409 is never silently given a new identity.
    await flushPersist();
    assertOwner();
    return pollUntilDone(endpoint, bearer, taskId, jobId, assertOwner);
  }
  if (isFormalConsumerApp || !isLabToolsEnabled) {
    throw new Error('Research / X02 direct path is disabled in the consumer App (PRD SYS02).');
  }
  return submitResearchPreview(endpoint, token, bundleDir, jsonPath);
}

function patchTask(taskId: string, patch: Partial<PipelineTask>) {
  useAppStore.setState((state) => {
    const pipelineTasks = state.pipelineTasks.map((t) =>
      t.id === taskId ? { ...t, ...patch } : t,
    );
    const updated = pipelineTasks.find((t) => t.id === taskId);
    if (updated) {
      recordPipelineLedger(updated);
      if (
        patch.status === 'succeeded' ||
        patch.status === 'failed' ||
        patch.productionJobId ||
        patch.status === 'cloud_processing'
      ) {
        rememberPipelineTask(updated);
      }
    }
    return { pipelineTasks };
  });
}

export async function runPipeline(taskId: string, items: PickedMedia[]): Promise<void> {
  if (activeRunners.has(taskId)) return;
  if (!items.length && !useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.bundleJsonPath) {
    patchTask(taskId, { status: 'failed', message: 'No media selected', error: 'empty_selection' });
    return;
  }

  const ownerToken = useAppStore.getState().sessionToken;
  const assertOwner = () => {
    if (useAppStore.getState().sessionToken !== ownerToken ||
        !useAppStore.getState().pipelineTasks.some((t) => t.id === taskId)) {
      throw new Error('Import cancelled because the signed-in account changed.');
    }
  };

  const taskDayKey =
    useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.dayKey ?? diaryTodayKey();
  const isTodayPipeline = taskDayKey === diaryTodayKey();
  const hadReadyForDay = useAppStore.getState().chapters.some((c) => c.dateKey === taskDayKey) ||
    Boolean(useAppStore.getState().smallMemoriesByDate[taskDayKey]?.length);
  if (isTodayPipeline) {
    useAppStore.setState({
      todayStatus: hadReadyForDay ? 'READY_PREPARING' : 'PREPARING',
    });
  }

  try {
    activeRunners.add(taskId);
    patchTask(taskId, {
      status: 'building_evidence',
      message: items.length ? `Deduping + normalizing ${items.length} asset(s) (compress / frames)…` : 'Reusing saved evidence…',
    });

    const sessionFolder = `bundle-${taskId}`;
    const root = FileSystem.documentDirectory;
    if (!root) throw new Error('documentDirectory unavailable');
    const saved = useAppStore.getState().pipelineTasks.find((t) => t.id === taskId);
    const bundleDir = saved?.bundleDir ?? `${root}bundles/${sessionFolder}/`;
    const bundleVersion = useAppStore.getState().bundleExportVersion;
    // Once ready, the manifest/session ID, original copies and chosen frames are
    // immutable for this revision, including retries after a lost POST response.
    const { jsonPath, bundle, sourceUris } = saved?.bundleJsonPath
      ? { jsonPath: saved.bundleJsonPath,
          bundle: JSON.parse(await FileSystem.readAsStringAsync(saved.bundleJsonPath)) as import('./bundleTypes').AppLibraryBundle,
          sourceUris: JSON.parse(await FileSystem.readAsStringAsync(`${bundleDir}source_uris.json`)) as Record<string, import('../domain/capturedImports').ImportedSource> }
      : await buildAppLibraryBundle(items, bundleDir, bundleVersion, assertOwner);

    assertOwner();
    patchTask(taskId, {
      status: 'bundle_ready',
      bundleDir,
      bundleJsonPath: jsonPath,
      bundleVersion: bundle.bundle_version,
      message: (() => {
        const video = bundle.assets.find(
          (a) => (a as { media_kind?: string }).media_kind === 'VIDEO',
        ) as { semantic_route_summary?: string } | undefined;
        const summary = video?.semantic_route_summary;
        return summary
          ? `${bundle.bundle_version} · ${summary}`
          : `${bundle.bundle_version} written on device`;
      })(),
    });

    const { target, endpoint, token } = resolveCloudTarget();
    const task = useAppStore.getState().pipelineTasks.find((t) => t.id === taskId);
    const sourceBatchId = task?.sourceBatchId ?? task?.dayRevisionId ?? taskId;
    const originals = capturedImports(sourceBatchId, taskDayKey, bundleDir, sourceUris, bundle.assets, task?.intakeSource);
    useAppStore.setState((state) => ({ capturedOriginals: [
      ...state.capturedOriginals.filter((original) => !originals.some((item) => item.id === original.id)),
      ...originals,
    ] }));

    if (endpoint) {
      const consent = useAppStore.getState().cloudEvidenceConsent;
      if (consent !== true) {
        throw new Error(
          'Cloud evidence upload requires consent. Turn it on in Account → Privacy & Data.',
        );
      }
      if (target === 'production' && !resolveProductionBearer()) {
        throw new Error(
          'No BFF credentials. Sign in or set Production API token (store builds refuse lab dev-token).',
        );
      }
      patchTask(taskId, {
        status: 'uploading',
        message: target === 'production' ? 'Connecting to production API…' : 'Connecting to research API…',
      });
      if (target === 'production') {
        const health = await checkProductionHealth(endpoint);
        assertOwner();
        if (health.allow_mock_preview === true && rejectMockBff()) {
          throw new Error(
            'BFF allow_mock_preview=true is forbidden for the consumer App (PRD AI03). Run start-quality-loop.ps1 (mock=false).',
          );
        }
      } else {
        await checkResearchHealth(endpoint, token);
      }
      patchTask(taskId, {
        status: 'cloud_processing',
        message:
          target === 'production'
            ? 'Cloud processing… (may take several minutes)'
            : 'X02 v0.4.1 preview running… (may take several minutes)',
      });
      await flushPersist();
      const manifestSha256 = await sha256SubmittedManifest(bundle);
      assertOwner();
      const preview = await runCloudPreview(
        target,
        endpoint,
        token,
        taskId,
        bundleDir,
        jsonPath,
        task?.dayRevisionId ?? taskId,
        assertOwner,
      );
      assertOwner();
      const valid = await validatePreviewResult(preview, { manifest: bundle, manifestSha256 });
      assertOwner();
      if (!valid.ok) {
        throw new Error(`Result validation failed: ${valid.reason}`);
      }
      const dayKey =
        useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.dayKey ?? diaryTodayKey();
      const mapped = mapPreviewToDiary(preview, dayKey);
      const chaptersWithHero = await attachChapterMediaFromBundle(
        mapped.chapters,
        preview.chapters,
        bundleDir,
        jsonPath,
      );
      assertOwner();
      const emptyIncoming =
        chaptersWithHero.length === 0 && mapped.smallMemories.length === 0;
      const priorForDay = useAppStore.getState().chapters.some((c) => c.dateKey === dayKey) ||
        Boolean(useAppStore.getState().smallMemoriesByDate[dayKey]?.length);
      const preserve = Boolean(valid.honestEmpty) || emptyIncoming;
      // PRD DIA04 / DAT01 — NO_GROUNDED / empty day must not erase prior Ready.
      const scoped = scopeImportedMemories(sourceBatchId, chaptersWithHero, mapped.smallMemories);
      const preservedPriorReady = preserve && priorForDay;
      await commitDiaryBatch({ taskId, dayKey, sourceBatchId, chapters: scoped.chapters,
        smallMemories: scoped.smallMemories, preservePriorIfIncomingEmpty: preserve,
        todayStatus: dayKey === diaryTodayKey()
          ? mapTodayStatusFromPreview(preview, { preservedPriorReady }) : undefined,
        assets: bundle.assets, assertCurrent: assertOwner });
      assertOwner();
      if (emptyIncoming) {
        patchTask(taskId, {
          status: 'succeeded',
          message: `Cloud OK but 0 memories (${preview.semantic_day_state ?? preview.delivery_state ?? 'empty'}) · prior day kept`,
          bundleVersion: bundle.bundle_version,
        });
        Alert.alert(
          'Cloud finished — no new memories',
          `X02 returned an empty day (${preview.delivery_state ?? preview.semantic_day_state ?? 'unknown'}). Prior memories for this day were kept (PRD DIA04).`,
        );
      } else {
        patchTask(taskId, {
          status: 'succeeded',
          message: `Diary updated · ${chaptersWithHero.length} memories, ${mapped.smallMemories.length} small · ${preview.delivery_state ?? 'ok'}`,
          bundleVersion: bundle.bundle_version,
        });
      }
    } else {
      throw new Error(
        'No cloud API URL. Set EXPO_PUBLIC_DEV_BFF_URL (LAN or HTTPS) and restart Metro, then sign in with email OTP.',
      );
    }
  } catch (err) {
    if (useAppStore.getState().sessionToken !== ownerToken ||
        !useAppStore.getState().pipelineTasks.some((t) => t.id === taskId)) {
      // Only this task's app-owned folder; a cancelled builder may have recreated it.
      const root = FileSystem.documentDirectory;
      if (root && !useAppStore.getState().pipelineTasks.some((t) => t.id === taskId)) await FileSystem.deleteAsync(`${root}bundles/bundle-${taskId}/`, { idempotent: true }).catch(() => {});
      return;
    }
    const message = err instanceof Error ? err.message : String(err);
    patchTask(taskId, {
      status: 'failed',
      message: 'Pipeline failed',
      error: message,
      ...(message.startsWith('CLOUD_JOB_FAILED:') ? { productionJobId: undefined } : {}),
    });
    // PRD DIA04 / T05 — keep prior Ready if that day still has content; do not invent Empty Day.
    const failDay =
      useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.dayKey ?? diaryTodayKey();
    if (failDay === diaryTodayKey()) {
      const stillHas = useAppStore.getState().chapters.some((c) => c.dateKey === failDay) ||
        Boolean(useAppStore.getState().smallMemoriesByDate[failDay]?.length);
      useAppStore.setState({ todayStatus: stillHas ? 'READY' : 'PARTIAL' });
    }
    Alert.alert('Pipeline failed', message.slice(0, 500));
  } finally {
    activeRunners.delete(taskId);
  }
}

/**
 * REL01 — resume poll only for jobs that already have productionJobId;
 * mark stuck pre-upload states failed so enqueue is not blocked forever.
 */
export function resumeInFlightCloudJobs(): void {
  const ownerToken = useAppStore.getState().sessionToken;
  const stillOwns = (id: string) => useAppStore.getState().sessionToken === ownerToken &&
    useAppStore.getState().pipelineTasks.some((task) => task.id === id);
  const tasks = useAppStore.getState().pipelineTasks;
  const stuck = ['queued', 'building_evidence', 'bundle_ready', 'uploading'] as const;
  for (const t of tasks) {
    if (stuck.includes(t.status as (typeof stuck)[number]) && !t.productionJobId) {
      patchTask(t.id, {
        status: 'failed',
        message: 'Interrupted before cloud submit',
        error: 'stale_local_pipeline_state',
      });
    }
  }

  for (const t of useAppStore.getState().pipelineTasks) {
    if (
      t.productionJobId &&
      (t.status === 'cloud_processing' || t.status === 'uploading') &&
      t.bundleDir &&
      t.bundleJsonPath
      && !activeRunners.has(t.id)
    ) {
      const { endpoint, token } = resolveCloudTarget();
      if (!endpoint) continue;
      activeRunners.add(t.id);
      void (async () => {
        try {
          const preview = await pollUntilDone(endpoint, token || requireProductionBearer(), t.id, t.productionJobId!, () => {
            if (!stillOwns(t.id)) throw new Error('Import cancelled because the account changed.');
          });
          if (!stillOwns(t.id)) return;
          const raw = await FileSystem.readAsStringAsync(t.bundleJsonPath!);
          const manifest = JSON.parse(raw) as import('./bundleTypes').AppLibraryBundle;
          const manifestSha256 = await sha256SubmittedManifest(manifest);
          if (!stillOwns(t.id)) return;
          const valid = await validatePreviewResult(preview, { manifest, manifestSha256 });
          if (!stillOwns(t.id)) return;
          if (!valid.ok) throw new Error(valid.reason);
          const mapped = mapPreviewToDiary(preview, t.dayKey);
          const chaptersWithHero = await attachChapterMediaFromBundle(
            mapped.chapters,
            preview.chapters,
            t.bundleDir!,
            t.bundleJsonPath!,
          );
          if (!stillOwns(t.id)) return;
          const emptyIncoming =
            chaptersWithHero.length === 0 && mapped.smallMemories.length === 0;
          const priorForDay = useAppStore.getState().chapters.some((c) => c.dateKey === t.dayKey) ||
            Boolean(useAppStore.getState().smallMemoriesByDate[t.dayKey]?.length);
          const preserve = Boolean(valid.honestEmpty) || emptyIncoming;
          const scoped = scopeImportedMemories(t.sourceBatchId ?? t.dayRevisionId ?? t.id, chaptersWithHero, mapped.smallMemories);
          await commitDiaryBatch({ taskId: t.id, dayKey: t.dayKey,
            sourceBatchId: t.sourceBatchId ?? t.dayRevisionId ?? t.id,
            chapters: scoped.chapters, smallMemories: scoped.smallMemories,
            preservePriorIfIncomingEmpty: preserve,
            todayStatus: t.dayKey === diaryTodayKey()
              ? mapTodayStatusFromPreview(preview, { preservedPriorReady: preserve && priorForDay }) : undefined,
            assets: manifest.assets, assertCurrent: () => {
              if (!stillOwns(t.id)) throw new Error('Import cancelled because the account changed.');
            } });
          if (!stillOwns(t.id)) return;
          patchTask(t.id, {
            status: 'succeeded',
            message: emptyIncoming
              ? `Resumed · empty day · prior kept`
              : `Resumed · Diary updated · ${chaptersWithHero.length} memories`,
          });
        } catch (e) {
          if (!stillOwns(t.id)) return;
          const err = e instanceof Error ? e.message : String(e);
          patchTask(t.id, {
            status: 'failed',
            message: err.startsWith('JOB_NOT_FOUND')
              ? 'Cloud job gone — submit again'
              : 'Resume poll failed',
            error: err,
            productionJobId: err.startsWith('JOB_NOT_FOUND') || err.startsWith('CLOUD_JOB_FAILED:')
              ? undefined : t.productionJobId,
          });
        } finally {
          activeRunners.delete(t.id);
        }
      })();
    }
  }
}

/** Retry local validation/materialization/save against the original billable cloud job. */
export function retryStoredCloudResult(taskId: string): void {
  const state = useAppStore.getState();
  const task = state.pipelineTasks.find((item) => item.id === taskId);
  if (!task || task.status !== 'failed' || !task.bundleDir || !task.bundleJsonPath ||
      activeRunners.has(taskId) || state.pipelineTasks.some((item) =>
        item.status !== 'failed' && item.status !== 'succeeded')) return;
  patchTask(taskId, { status: 'cloud_processing', error: undefined, message: 'Retrying saved cloud request…' });
  if (task.productionJobId) resumeInFlightCloudJobs();
  else void runPipeline(taskId, []);
}

export function enqueuePipeline(
  items: PickedMedia[],
  intakeSource: MediaIntakeSource = PHOTO_LIBRARY_TEST_SOURCE,
): string | null {
  const state = useAppStore.getState();
  if (!items.length || state.pipelineTasks.some(
    (t) => t.status !== 'succeeded' && t.status !== 'failed',
  )) return null;

  const ownerToken = state.sessionToken;
  const owner = state.localProfile.email?.trim() || ownerToken.slice(0, 12);
  const groups = groupMediaByDay(items, diaryTodayKey());
  const queue = groups.map(([dayKey, media], index) => {
    const dayRevisionId = createStableDayRevisionId(dayKey, selectionFingerprint(media), owner);
    const task: PipelineTask = {
      id: `task-${Date.now()}-${index}`,
      createdAt: new Date().toISOString(),
      dayKey,
      dayRevisionId,
      sourceBatchId: dayRevisionId,
      intakeSource,
      status: 'queued',
      message: `Queued · ${dayKey}`,
      sourceCount: media.length,
      dayKeyFromCapture: media.every((item) => Boolean(item.captureDayKey || item.creationTimeMs)),
    };
    return { task, media };
  });
  useAppStore.setState((current) => ({
    pipelineTasks: [...queue.map(({ task }) => task), ...current.pipelineTasks],
  }));
  // One cloud run at a time, with a separate revision for every local capture day.
  void (async () => {
    for (const { task, media } of queue) {
      if (useAppStore.getState().sessionToken !== ownerToken ||
          !useAppStore.getState().pipelineTasks.some((t) => t.id === task.id)) break;
      await runPipeline(task.id, media);
    }
  })();
  return queue[0].task.id;
}
