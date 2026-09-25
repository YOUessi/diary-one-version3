import * as FileSystem from 'expo-file-system/legacy';
import type { AppLibraryBundle } from '../pipeline/bundleTypes';
import type { CloudJobPoll } from './types';
import type { X02PreviewResult } from '../cloud/types';
import { buildBundleMultipartForm } from '../cloud/researchClient';
import { resolveProductionBearer } from './resolveProductionBearer';

function base(url: string) {
  return url.trim().replace(/\/+$/, '');
}

function auth(token: string): Record<string, string> {
  const t = token.trim();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

/** Production BFF — multipart upload → async job (diary-one-server). */
export async function submitProductionDayRevision(
  apiBaseUrl: string,
  token: string | undefined,
  dayRevisionId: string,
  bundleDir: string,
  bundleJsonPath: string,
): Promise<{ jobId: string }> {
  const manifestRaw = await FileSystem.readAsStringAsync(bundleJsonPath);
  const manifest = JSON.parse(manifestRaw) as AppLibraryBundle;
  const prefs = useAppStore.getState().preferences.map((p) =>
    p.title ? `${p.title}: ${p.text}` : p.text,
  );

  const form = await buildBundleMultipartForm(
    bundleDir,
    manifest,
    { memory_preferences: prefs },
    { day_revision_id: dayRevisionId },
  );

  const res = await fetch(`${base(apiBaseUrl)}/v1/day-revisions`, {
    method: 'POST',
    headers: { Accept: 'application/json', ...auth(token ?? resolveProductionBearer()) },
    body: form,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Production API rejected day revision (${res.status})${text ? `: ${text}` : ''}`);
  }

  const body = (await res.json()) as { job_id?: string; jobId?: string };
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
  const res = await fetch(`${base(apiBaseUrl)}/v1/jobs/${encodeURIComponent(jobId)}`, {
    headers: { Accept: 'application/json', ...auth(token ?? resolveProductionBearer()) },
  });

  if (res.status === 404) {
    return {
      state: 'failed',
      message: 'Production job API not deployed. Start diary-one-server BFF + worker.',
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

  if (body.status === 'succeeded' && body.result) {
    return { state: 'succeeded', result: body.result };
  }
  if (body.status === 'failed') {
    return { state: 'failed', message: body.message ?? 'Cloud job failed' };
  }
  return { state: 'pending', message: body.message ?? 'Processing…' };
}
