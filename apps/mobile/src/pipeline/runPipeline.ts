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
import { diaryTodayKey } from '../domain/dayKey';
import { createDayRevisionId } from '../domain/dayRevision';
import { PHOTO_LIBRARY_TEST_SOURCE } from '../domain/mediaIntake';
import { attachHeroUrisFromBundle } from './attachHeroUris';
import { rememberPipelineTask } from '../db/ledger';
import { recordPipelineLedger } from '../db/assetLedger';

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function resolveCloudTarget(): {
  target: CloudProcessingTarget;
  endpoint: string;
  token: string;
} {
  const s = useAppStore.getState();
  if (s.cloudProcessingTarget === 'production' && s.productionApiBaseUrl.trim()) {
    return {
      target: 'production',
      endpoint: s.productionApiBaseUrl.trim(),
      token: s.productionApiToken.trim() || 'dev-token',
    };
  }
  return {
    target: 'research',
    endpoint: s.researchEndpoint.trim(),
    token: s.researchToken,
  };
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
    const { jobId } = await submitProductionDayRevision(
      endpoint,
      token,
      dayRevisionId,
      bundleDir,
      jsonPath,
    );
    patchTask(taskId, { status: 'cloud_processing', message: `Production job ${jobId}…` });
    for (let i = 0; i < 180; i++) {
      const poll = await pollProductionCloudJob(endpoint, token, jobId);
      if (poll.state === 'succeeded') return poll.result;
      if (poll.state === 'failed') throw new Error(poll.message);
      await sleep(1500);
    }
    throw new Error('Production job timed out while polling (4.5 min)');
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
      if (patch.status === 'succeeded' || patch.status === 'failed') {
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

  useAppStore.setState({ todayStatus: 'PREPARING' });

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
      patchTask(taskId, {
        status: 'uploading',
        message: target === 'production' ? 'Connecting to production API…' : 'Connecting to research API…',
      });
      if (target === 'production') {
        const healthRes = await fetch(`${endpoint.replace(/\/+$/, '')}/health`);
        if (!healthRes.ok) {
          throw new Error(`Production health check failed (${healthRes.status})`);
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
      const dayKey =
        useAppStore.getState().pipelineTasks.find((t) => t.id === taskId)?.dayKey ?? diaryTodayKey();
      const mapped = mapPreviewToDiary(preview, dayKey);
      const chaptersWithHero = await attachHeroUrisFromBundle(
        mapped.chapters,
        bundleDir,
        jsonPath,
      );
      applyDiaryDayUpdate(dayKey, chaptersWithHero, mapped.smallMemories);
      applyTodayStatus(mapTodayStatusFromPreview(preview));
      patchTask(taskId, {
        status: 'succeeded',
        message: `Diary updated · ${chaptersWithHero.length} memories, ${mapped.smallMemories.length} small · ${preview.delivery_state ?? 'ok'}`,
        bundleVersion: bundle.bundle_version,
      });
    } else {
      patchTask(taskId, { status: 'uploading', message: 'No API URL — mock upload…' });
      await sleep(400);
      patchTask(taskId, { status: 'cloud_processing', message: 'Mock worker (set API on Device)…' });
      await sleep(900);
      patchTask(taskId, {
        status: 'succeeded',
        message: 'Bundle saved locally. Configure cloud API in Account → Evidence pipeline lab.',
      });
      useAppStore.setState({ todayStatus: 'READY' });
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    patchTask(taskId, {
      status: 'failed',
      message: 'Pipeline failed',
      error: message,
    });
    useAppStore.setState({ todayStatus: 'PARTIAL' });
    Alert.alert('Pipeline failed', message.slice(0, 500));
  }
}

export function enqueuePipeline(items: PickedMedia[]): string | null {
  const active = useAppStore.getState().pipelineTasks.some(
    (t) => t.status !== 'succeeded' && t.status !== 'failed',
  );
  if (active) {
    return null;
  }
  const id = `task-${Date.now()}`;
  const dayKey = diaryTodayKey();
  const task: PipelineTask = {
    id,
    createdAt: new Date().toISOString(),
    dayKey,
    dayRevisionId: createDayRevisionId(dayKey),
    intakeSource: PHOTO_LIBRARY_TEST_SOURCE,
    status: 'queued',
    message: 'Queued',
    sourceCount: items.length,
  };
  useAppStore.setState((state) => ({
    pipelineTasks: [task, ...state.pipelineTasks],
  }));
  void runPipeline(id, items);
  return id;
}
