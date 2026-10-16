import * as FileSystem from 'expo-file-system/legacy';
import type { AppLibraryBundle } from '../pipeline/bundleTypes';
import type { CloudJobPoll } from './types';
import type { X02PreviewResult } from '../cloud/types';
import { buildBundleMultipartForm } from '../cloud/researchClient';
import { postMultipartText } from '../cloud/rnFormData';
import { requireProductionBearer, resolveProductionBearer } from './resolveProductionBearer';
import { useAppStore } from '../store/useAppStore';
import { buildAppClientProfile } from '../domain/memoryPreferencesCloud';

function base(url: string) {
  return url.trim().replace(/\/+$/, '');
}

function auth(token: string): Record<string, string> {
  const t = token.trim();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

/** Empty string must not skip fallback (`??` alone is wrong). */
function resolveBearer(token: string | undefined): string {
  const trimmed = (token ?? '').trim();
  if (trimmed) return trimmed;
  return resolveProductionBearer().trim() || requireProductionBearer();
}

function parseDetail(text: string): string {
  try {
    const j = JSON.parse(text) as { detail?: { message?: string } | string };
    if (typeof j.detail === 'string') return j.detail;
    if (j.detail && typeof j.detail === 'object' && j.detail.message) return j.detail.message;
  } catch {
    /* keep raw */
  }
  return text.trim();
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

  // PRD PRI01 / SYN03 / D07 — preferences are NOT uploaded by default.
  // Opt-in only via EXPO_PUBLIC_UPLOAD_MEMORY_PREFERENCES=1 after product approval.
  const allowPrefsUpload =
    (process.env.EXPO_PUBLIC_UPLOAD_MEMORY_PREFERENCES ?? '').trim() === '1';
  const profile = allowPrefsUpload
    ? buildAppClientProfile(useAppStore.getState().preferences)
    : undefined;

  const form = await buildBundleMultipartForm(bundleDir, manifest, profile, {
    day_revision_id: dayRevisionId,
  });

  const bearer = resolveBearer(token);
  const posted = await postMultipartText(`${base(apiBaseUrl)}/v1/day-revisions`, form, {
    Accept: 'application/json',
    ...auth(bearer),
  });

  if (!posted.ok) {
    if (posted.status === 401 || posted.status === 403) {
      useAppStore.getState().setSessionToken('');
      throw new Error(
        'Cloud session expired or unauthorized. Open Account → Continue with Email and sign in again.',
      );
    }
    if (posted.status === 409) {
      const detail = parseDetail(posted.text) || 'day_revision conflict';
      throw new Error(`DAY_REVISION_CONFLICT:${detail}`);
    }
    if (posted.status === 429) {
      const hint = parseDetail(posted.text) || 'Daily upload limit reached';
      throw new Error(`Upload limit (429): ${hint}`);
    }
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
    const bearer = resolveBearer(token);
    const res = await fetch(`${base(apiBaseUrl)}/v1/jobs/${encodeURIComponent(jobId)}`, {
      headers: { Accept: 'application/json', ...auth(bearer) },
    });

    if (res.status === 404) {
      const detail = parseDetail(await res.text().catch(() => ''));
      // BFF owner isolation also returns 404 "Job not found" — not "API undeployed".
      if (/not found|job/i.test(detail) || detail === '') {
        return {
          state: 'failed',
          message:
            'JOB_NOT_FOUND: Cloud job missing or belongs to another account. Clear the task and submit again after OTP sign-in.',
        };
      }
      return {
        state: 'failed',
        message: `Job poll 404: ${detail || 'unknown'}`,
      };
    }

    if (res.status === 401 || res.status === 403) {
      useAppStore.getState().setSessionToken('');
      return {
        state: 'failed',
        message:
          'Cloud session expired or unauthorized. Open Account → Continue with Email and sign in again.',
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

/** Cold-start session probe — any authenticated route is enough. */
export async function probeProductionSession(apiBaseUrl: string, token: string): Promise<boolean> {
  const bearer = (token ?? '').trim();
  if (!bearer || !apiBaseUrl.trim()) return false;
  try {
    // Non-existent job → 404 with auth OK; 401/403 means dead session.
    const res = await fetch(`${base(apiBaseUrl)}/v1/jobs/__session_probe__`, {
      headers: { Accept: 'application/json', ...auth(bearer) },
    });
    if (res.status === 401 || res.status === 403) return false;
    return true;
  } catch {
    // Network blip — keep local session; upload path will re-check.
    return true;
  }
}
