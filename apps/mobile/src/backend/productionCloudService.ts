import * as FileSystem from 'expo-file-system/legacy';
import type { AppLibraryBundle } from '../pipeline/bundleTypes';
import type { CloudJobPoll } from './types';
import type { X02PreviewResult } from '../cloud/types';
import { buildBundleMultipartForm } from '../cloud/researchClient';
import { postMultipartText } from '../cloud/rnFormData';
import { resolveProductionBearer } from './resolveProductionBearer';
import { useAppStore } from '../store/useAppStore';
import { memoryPreferencesForUpload } from '../domain/memoryPreferencesCloud';

function base(url: string) {
  return url.trim().replace(/\/+$/, '');
}

function auth(token: string): Record<string, string> {
  const t = token.trim();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

/** Production BFF — multipart upload → async job (Dev Lite / Docker BFF). */
export async function submitProductionDayRevision(
  apiBaseUrl: string,
  token: string | undefined,
  dayRevisionId: string,
  bundleDir: string,
  bundleJsonPath: string,
): Promise<{ jobId: string }> {
  const manifestRaw = await FileSystem.readAsStringAsync(bundleJsonPath);
  const manifest = JSON.parse(manifestRaw) as AppLibraryBundle;
  const prefs = memoryPreferencesForUpload(useAppStore.getState().preferences);

  const form = await buildBundleMultipartForm(
    bundleDir,
    manifest,
    { memory_preferences: prefs },
    { day_revision_id: dayRevisionId },
  );

  const posted = await postMultipartText(`${base(apiBaseUrl)}/v1/day-revisions`, form, {
    Accept: 'application/json',
    ...auth(token ?? resolveProductionBearer()),
  });

  if (!posted.ok) {
    throw new Error(
      `Production API rejected day revision (${posted.status})${posted.text ? `: ${posted.text}` : ''}`,
    );
  }

  const body = JSON.parse(posted.text) as { job_id?: string; jobId?: string };
  const jobId = body.job_id ?? body.jobId;
  if (!jobId) {
    throw new Error('Production API did not return job_id');
  }
  return { jobId };
}

export async function pollProductionCloudJob(
  apiBaseUrl: string,
  token: string,
  jobId: string,
): Promise<CloudJobPoll> {
  try {
    const res = await fetch(`${base(apiBaseUrl)}/v1/jobs/${encodeURIComponent(jobId)}`, {
      headers: { Accept: 'application/json', ...auth(token ?? resolveProductionBearer()) },
    });

    if (res.status === 404) {
      return {
        state: 'failed',
        message: 'Production job API not deployed. Start Dev Lite (services/bff) or Docker BFF.',
      };
    }

    if (!res.ok) {
      return { state: 'failed', message: `Job poll failed (${res.status})` };
    }

    const body = (await res.json()) as {
      status?: string;
      result?: X02PreviewResult;
      message?: string;
    };

    if (body.status === 'succeeded') {
      if (!body.result) {
        return { state: 'failed', message: 'Cloud job succeeded without result payload' };
      }
      return { state: 'succeeded', result: body.result };
    }
    if (body.status === 'failed') {
      return { state: 'failed', message: body.message ?? 'Cloud job failed' };
    }
    return { state: 'pending', message: body.message ?? 'Processing…' };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { state: 'failed', message: `Job poll network error: ${msg}` };
  }
}
