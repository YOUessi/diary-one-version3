import * as FileSystem from 'expo-file-system/legacy';
import { Alert } from 'react-native';
import { buildAppLibraryBundle } from './buildAppLibraryBundle';
import type { PickedMedia, PipelineTask } from './types';
import { useAppStore } from '../store/useAppStore';
import { checkResearchHealth } from '../cloud/researchClient';
import { submitResearchPreview } from '../backend/researchCloudService';
import { submitProductionDayRevision, pollProductionCloudJob } from '../backend/productionCloudService';
import type { CloudProcessingTarget } from '../backend/types';
import { mapPreviewToDiary } from '../cloud/mapPreviewResult';
import { validatePreviewResult } from '../cloud/validatePreviewResult';
import { applyDiaryDayUpdate, applyTodayStatus } from '../store/applyDiaryDay';
import { mapTodayStatusFromPreview } from '../cloud/mapTodayStatus';
import { dayKeyFromCaptureTimes, diaryTodayKey } from '../domain/dayKey';
import {
  createStableDayRevisionId,
  selectionFingerprint,
} from '../domain/dayRevision';
import { PHOTO_LIBRARY_TEST_SOURCE, type MediaIntakeSource } from '../domain/mediaIntake';
import { attachChapterMediaFromBundle } from './attachChapterMedia';
import { rememberRawAssetsFromBundleAssets } from './dedupeMedia';
import { rememberPipelineTask } from '../db/ledger';
import { recordPipelineLedger } from '../db/assetLedger';
import { requireProductionBearer, resolveProductionBearer } from '../backend/resolveProductionBearer';
import { isFormalConsumerApp, isLabToolsEnabled } from '../config/buildProfile';

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

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
) {
  for (let i = 0; i < 180; i++) {
    const poll = await pollProductionCloudJob(endpoint, token, jobId);
    if (poll.state === 'succeeded') {
      if (!poll.result) {
        throw new Error('Cloud job succeeded but returned no result payload');
      }
      return poll.result;
    }
    if (poll.state === 'failed') {
      throw new Error(poll.message || 'Cloud job failed');
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
      return pollUntilDone(endpoint, bearer, taskId, existingJob);
    }
    let revId = dayRevisionId;
    try {
      const { jobId } = await submitProductionDayRevision(
        endpoint,
        bearer,
        revId,
        bundleDir,
        jsonPath,
      );
      patchTask(taskId, {
        status: 'cloud_processing',
        productionJobId: jobId,
        dayRevisionId: revId,
        message: `Uploaded · job ${jobId.slice(0, 8)}…`,
      });
      return pollUntilDone(endpoint, bearer, taskId, jobId);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      // Cross-account or stale succeeded revision → one forced new identity.
      if (msg.startsWith('DAY_REVISION_CONFLICT:')) {
        revId = `${dayRevisionId}_r${Date.now().toString(36)}`;
        const { jobId } = await submitProductionDayRevision(
          endpoint,
          bearer,
          revId,
          bundleDir,
          jsonPath,
        );
        patchTask(taskId, {
          status: 'cloud_processing',
          productionJobId: jobId,
          dayRevisionId: revId,
          message: `Uploaded (new revision) · job ${jobId.slice(0, 8)}…`,
        });
        return pollUntilDone(endpoint, bearer, taskId, jobId);
      }
      throw e;
    }
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
  if (!items.length) {
    patchTask(taskId, { status: 'failed', message: 'No media selected', error: 'empty_selection' });
    return;
  }

  const taskDayKey =
    useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.dayKey ?? diaryTodayKey();
  const isTodayPipeline = taskDayKey === diaryTodayKey();
  const hadReadyForDay = useAppStore.getState().chapters.some((c) => c.dateKey === taskDayKey);
  if (isTodayPipeline) {
    useAppStore.setState({
      todayStatus: hadReadyForDay ? 'READY_PREPARING' : 'PREPARING',
    });
  }

  try {
    patchTask(taskId, {
      status: 'building_evidence',
      message: `Deduping + normalizing ${items.length} asset(s) (compress / frames)…`,
    });

    const sessionFolder = `bundle-${taskId}`;
    const root = FileSystem.documentDirectory;
    if (!root) throw new Error('documentDirectory unavailable');
    const bundleDir = `${root}bundles/${sessionFolder}/`;
    const bundleVersion = useAppStore.getState().bundleExportVersion;
    const { jsonPath, bundle } = await buildAppLibraryBundle(items, bundleDir, bundleVersion);

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
        const healthRes = await fetch(`${endpoint.replace(/\/+$/, '')}/health`);
        if (!healthRes.ok) {
          throw new Error(`Production health check failed (${healthRes.status})`);
        }
        const health = (await healthRes.json().catch(() => ({}))) as {
          allow_mock_preview?: boolean;
        };
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
      const preview = await runCloudPreview(
        target,
        endpoint,
        token,
        taskId,
        bundleDir,
        jsonPath,
        task?.dayRevisionId ?? taskId,
      );
      const valid = validatePreviewResult(preview);
      if (!valid.ok) {
        throw new Error(`Result validation failed: ${valid.reason}`);
      }
      // REL01 — only after admitted cloud success; failed retries may re-select same bytes.
      await rememberRawAssetsFromBundleAssets(
        (bundle.assets ?? []) as Array<{
          asset_id?: string;
          original_sha256?: string;
          media_kind?: string;
          source_display_name?: string;
          original_bytes?: number;
        }>,
      );
      const dayKey =
        useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.dayKey ?? diaryTodayKey();
      const mapped = mapPreviewToDiary(preview, dayKey);
      const chaptersWithHero = await attachChapterMediaFromBundle(
        mapped.chapters,
        preview.chapters,
        bundleDir,
        jsonPath,
      );
      const emptyIncoming =
        chaptersWithHero.length === 0 && mapped.smallMemories.length === 0;
      const priorForDay = useAppStore.getState().chapters.some((c) => c.dateKey === dayKey);
      const preserve = Boolean(valid.honestEmpty) || emptyIncoming;
      // PRD DIA04 / DAT01 — NO_GROUNDED / empty day must not erase prior Ready.
      applyDiaryDayUpdate(dayKey, chaptersWithHero, mapped.smallMemories, {
        preservePriorIfIncomingEmpty: preserve,
      });
      const preservedPriorReady = preserve && priorForDay;
      if (dayKey === diaryTodayKey()) {
        applyTodayStatus(
          mapTodayStatusFromPreview(preview, { preservedPriorReady }),
        );
      }
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
    const message = err instanceof Error ? err.message : String(err);
    patchTask(taskId, {
      status: 'failed',
      message: 'Pipeline failed',
      error: message,
    });
    // PRD DIA04 / T05 — keep prior Ready if that day still has content; do not invent Empty Day.
    const failDay =
      useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.dayKey ?? diaryTodayKey();
    if (failDay === diaryTodayKey()) {
      const stillHas = useAppStore.getState().chapters.some((c) => c.dateKey === failDay);
      useAppStore.setState({ todayStatus: stillHas ? 'READY' : 'PARTIAL' });
    }
    Alert.alert('Pipeline failed', message.slice(0, 500));
  }
}

/**
 * REL01 — resume poll only for jobs that already have productionJobId;
 * mark stuck pre-upload states failed so enqueue is not blocked forever.
 */
export function resumeInFlightCloudJobs(): void {
  const tasks = useAppStore.getState().pipelineTasks;
  const stuck = ['queued', 'building_evidence', 'bundle_ready'] as const;
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
    ) {
      const { endpoint, token } = resolveCloudTarget();
      if (!endpoint) continue;
      void (async () => {
        try {
          const preview = await pollUntilDone(endpoint, token || requireProductionBearer(), t.id, t.productionJobId!);
          const valid = validatePreviewResult(preview);
          if (!valid.ok) throw new Error(valid.reason);
          try {
            const raw = await FileSystem.readAsStringAsync(t.bundleJsonPath!);
            const manifest = JSON.parse(raw) as { assets?: unknown[] };
            await rememberRawAssetsFromBundleAssets(
              (manifest.assets ?? []) as Array<{
                asset_id?: string;
                original_sha256?: string;
                media_kind?: string;
                source_display_name?: string;
                original_bytes?: number;
              }>,
            );
          } catch {
            /* ledger best-effort on resume */
          }
          const mapped = mapPreviewToDiary(preview, t.dayKey);
          const chaptersWithHero = await attachChapterMediaFromBundle(
            mapped.chapters,
            preview.chapters,
            t.bundleDir!,
            t.bundleJsonPath!,
          );
          const emptyIncoming =
            chaptersWithHero.length === 0 && mapped.smallMemories.length === 0;
          const priorForDay = useAppStore.getState().chapters.some((c) => c.dateKey === t.dayKey);
          const preserve = Boolean(valid.honestEmpty) || emptyIncoming;
          applyDiaryDayUpdate(t.dayKey, chaptersWithHero, mapped.smallMemories, {
            preservePriorIfIncomingEmpty: preserve,
          });
          if (t.dayKey === diaryTodayKey()) {
            applyTodayStatus(
              mapTodayStatusFromPreview(preview, {
                preservedPriorReady: preserve && priorForDay,
              }),
            );
          }
          patchTask(t.id, {
            status: 'succeeded',
            message: emptyIncoming
              ? `Resumed · empty day · prior kept`
              : `Resumed · Diary updated · ${chaptersWithHero.length} memories`,
          });
        } catch (e) {
          const err = e instanceof Error ? e.message : String(e);
          patchTask(t.id, {
            status: 'failed',
            message: err.startsWith('JOB_NOT_FOUND')
              ? 'Cloud job gone — submit again'
              : 'Resume poll failed',
            error: err,
            productionJobId: err.startsWith('JOB_NOT_FOUND') ? undefined : t.productionJobId,
          });
        }
      })();
    }
  }
}

export function enqueuePipeline(
  items: PickedMedia[],
  intakeSource: MediaIntakeSource = PHOTO_LIBRARY_TEST_SOURCE,
): string | null {
  const active = useAppStore.getState().pipelineTasks.some(
    (t) => t.status !== 'succeeded' && t.status !== 'failed',
  );
  if (active) {
    // Prefer resume over hard-busy when a job id already exists (REL01).
    const inflight = useAppStore.getState().pipelineTasks.find(
      (t) =>
        t.productionJobId &&
        (t.status === 'cloud_processing' || t.status === 'uploading'),
    );
    if (inflight) {
      resumeInFlightCloudJobs();
      return inflight.id;
    }
    return null;
  }

  const captureDay = dayKeyFromCaptureTimes(items.map((i) => i.creationTimeMs));
  const dayKey = captureDay ?? diaryTodayKey();
  const fp = selectionFingerprint(items);
  const owner =
    useAppStore.getState().localProfile.email?.trim() ||
    useAppStore.getState().sessionToken.trim().slice(0, 12);
  const dayRevisionId = createStableDayRevisionId(dayKey, fp, owner);

  // REL01 — same selection keeps stable day_revision_id for BFF idempotency,
  // but NEVER reuse a failed productionJobId (client would poll a dead job forever).
  const id = `task-${Date.now()}`;
  const task: PipelineTask = {
    id,
    createdAt: new Date().toISOString(),
    dayKey,
    dayRevisionId,
    productionJobId: undefined,
    intakeSource,
    status: 'queued',
    message: captureDay
      ? `Queued · day from capture (${dayKey})`
      : 'Queued · capture time unknown → today',
    sourceCount: items.length,
    dayKeyFromCapture: Boolean(captureDay),
  };
  useAppStore.setState((state) => ({
    pipelineTasks: [task, ...state.pipelineTasks],
  }));
  void runPipeline(id, items);
  return id;
}
