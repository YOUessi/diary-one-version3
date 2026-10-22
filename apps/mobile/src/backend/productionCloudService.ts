import * as FileSystem from 'expo-file-system/legacy';
import type { AppLibraryBundle } from '../pipeline/bundleTypes';
import type { CloudJobPoll } from './types';
import type { X02PreviewResult } from '../cloud/types';
import { buildBundleMultipartForm } from '../cloud/researchClient';
import { postMultipartText } from '../cloud/rnFormData';
import { requireProductionBearer, resolveProductionBearer } from './resolveProductionBearer';
import { useAppStore } from '../store/useAppStore';
import { buildAppClientProfile, type AppClientProfileV01 } from '../domain/memoryPreferencesCloud';

function base(url: string) {
  return url.trim().replace(/\/+$/, '');
}

function auth(token: string): Record<string, string> {
  const t = token.trim();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

function expireMatchingSession(bearer: string) {
  const state = useAppStore.getState();
  // A response from account A may arrive after account B has signed in.
  if (state.sessionToken.trim() === bearer) state.setSessionToken('');
}

async function readResponse(url: string, headers?: Record<string, string>) {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      (async () => {
        const response = await fetch(url, { headers, signal: controller.signal });
        return { ok: response.ok, status: response.status, text: await response.text() };
      })(),
      new Promise<never>((_, reject) => {
        timer = setTimeout(() => { controller.abort(); reject(new Error('Cloud request timed out')); }, 30_000);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

export async function checkProductionHealth(apiBaseUrl: string) {
  const response = await readResponse(`${base(apiBaseUrl)}/health`);
  if (!response.ok) throw new Error(`Production health check failed (${response.status})`);
  return JSON.parse(response.text) as { allow_mock_preview?: boolean };
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
  const profilePath = `${bundleDir}submission-profile.json`;
  let profile: AppClientProfileV01 | undefined;
  if ((await FileSystem.getInfoAsync(profilePath)).exists) {
    const frozen = JSON.parse(await FileSystem.readAsStringAsync(profilePath)) as {
      dayRevisionId: string; profile: AppClientProfileV01 | null;
    };
    if (frozen.dayRevisionId !== dayRevisionId || !Object.hasOwn(frozen, 'profile')) {
      throw new Error('Saved submission context does not match this revision');
    }
    profile = frozen.profile ?? undefined;
  } else {
    profile = allowPrefsUpload ? buildAppClientProfile(useAppStore.getState().preferences) : undefined;
    // A lost acknowledgement must retry identical input even if settings change.
    await FileSystem.writeAsStringAsync(profilePath, JSON.stringify({ dayRevisionId, profile: profile ?? null }));
  }

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
      expireMatchingSession(bearer);
      throw new Error(
        'Cloud session expired or unauthorized. Open Account → Continue with Email and sign in again.',
      );
    }
    if (posted.status === 422) {
      let rejection: { detail?: { code?: unknown; reason?: unknown } } | undefined;
      try { rejection = JSON.parse(posted.text); } catch { /* legacy response uses the fallback below */ }
      if (rejection?.detail?.code === 'EVIDENCE_INPUT_INVALID') {
        const reason = rejection.detail.reason;
        // Preserve the machine code for recovery decisions, never a server path or stack.
        throw new Error(`EVIDENCE_INPUT_INVALID:${typeof reason === 'string' && /^[a-z_]{1,80}$/.test(reason)
          ? reason : 'invalid_upload'}`);
      }
    }
    if (posted.status === 409) {
      const detail = parseDetail(posted.text) || 'day_revision conflict';
      throw new Error(`DAY_REVISION_CONFLICT:${detail}`);
    }
    if (posted.status === 429) {
      const hint = parseDetail(posted.text) || 'Daily upload limit reached';
      throw new Error(`Upload limit (429): ${hint}`);
    }
    if (posted.status === 503) {
      // Acceptance may be uncertain after a lost DB acknowledgement. Preserve
      // the revision and frozen preferences so retry can recover the same job.
      throw new Error('CLOUD_SUBMISSION_UNAVAILABLE');
    }
    throw new Error(
      `Production API rejected day revision (${posted.status})${posted.text ? `: ${posted.text}` : ''}`,
    );
  }

  const body = JSON.parse(posted.text) as { job_id?: string; jobId?: string };
  const jobId = body.job_id ?? body.jobId;
  if (typeof jobId !== 'string' || !jobId.trim()) {
    throw new Error('Production API did not return job_id');
  }
  return { jobId: jobId.trim() };
}

export async function pollProductionCloudJob(
  apiBaseUrl: string,
  token: string,
  jobId: string,
): Promise<CloudJobPoll> {
  try {
    const bearer = resolveBearer(token);
    const res = await readResponse(`${base(apiBaseUrl)}/v1/jobs/${encodeURIComponent(jobId)}`,
      { Accept: 'application/json', ...auth(bearer) });

    if (res.status === 404) {
      const detail = parseDetail(res.text);
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
      expireMatchingSession(bearer);
      return {
        state: 'paused',
        message:
          'Cloud session expired or unauthorized. Open Account → Continue with Email and sign in again.',
      };
    }

    if (!res.ok) {
      return { state: 'paused', message: `Job poll unavailable (${res.status}); original job retained` };
    }

    const body = JSON.parse(res.text) as {
      job_id?: string;
      status?: string;
      result?: X02PreviewResult;
      message?: string;
    };

    if (!body || body.job_id !== jobId) {
      return { state: 'paused', message: 'Cloud response job identity mismatch; original job retained' };
    }

    if (body.status === 'succeeded') {
      if (!body.result) {
        return { state: 'paused', message: 'Cloud job succeeded without result payload' };
      }
      return { state: 'succeeded', result: body.result };
    }
    if (body.status === 'failed') {
      return { state: 'failed', message: body.message ?? 'Cloud job failed' };
    }
    if (body.status === 'queued' || body.status === 'running' || body.status === 'pending' || body.status === 'processing') {
      return { state: 'pending', message: body.message ?? 'Processing…' };
    }
    return { state: 'paused', message: 'Cloud job returned an unknown state; original job retained' };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { state: 'paused', message: `Job poll interrupted: ${msg}; original job retained` };
  }
}

/** Cold-start session probe — any authenticated route is enough. */
export async function probeProductionSession(apiBaseUrl: string, token: string): Promise<boolean> {
  const bearer = (token ?? '').trim();
  if (!bearer || !apiBaseUrl.trim()) return false;
  try {
    // Non-existent job → 404 with auth OK; 401/403 means dead session.
    const res = await readResponse(`${base(apiBaseUrl)}/v1/jobs/__session_probe__`,
      { Accept: 'application/json', ...auth(bearer) });
    if (res.status === 401 || res.status === 403) return false;
    return true;
  } catch {
    // Network blip — keep local session; upload path will re-check.
    return true;
  }
}
