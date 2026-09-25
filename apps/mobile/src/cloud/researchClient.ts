import * as FileSystem from 'expo-file-system/legacy';

import type { AppLibraryBundle } from '../pipeline/bundleTypes';

import type { ResearchHealth, X02PreviewResult } from './types';

import { useAppStore } from '../store/useAppStore';



import { ALGORITHM_LOCK } from '../config/algorithmLock';

const DEFAULT_PREVIEW_PATH = ALGORITHM_LOCK.x02PreviewPath;



function base(endpoint: string) {

  return endpoint.trim().replace(/\/+$/, '');

}



function auth(token: string): Record<string, string> {

  const t = token.trim();

  return t ? { Authorization: `Bearer ${t}` } : {};

}



export async function checkResearchHealth(endpoint: string, token: string): Promise<ResearchHealth> {

  const res = await fetch(`${base(endpoint)}/health`, {

    headers: { Accept: 'application/json', ...auth(token) },

  });

  if (!res.ok) {

    throw new Error(`Health check failed (${res.status})`);

  }

  return (await res.json()) as ResearchHealth;

}



export async function resolvePreviewUrl(endpoint: string, token: string): Promise<string> {

  const health = await checkResearchHealth(endpoint, token);

  const path = health.previewPath?.startsWith('/')

    ? health.previewPath

    : DEFAULT_PREVIEW_PATH;

  return `${base(endpoint)}${path}`;

}



type FrameRef = { frame_id: string; relative_path: string };



export async function buildBundleMultipartForm(
  bundleDir: string,
  manifest: AppLibraryBundle,
  clientProfile?: { memory_preferences: string[] },
  extraFields?: { day_revision_id?: string },
): Promise<FormData> {
  const form = new FormData();

  if (extraFields?.day_revision_id) {
    form.append('day_revision_id', extraFields.day_revision_id);
  }

  if (clientProfile?.memory_preferences.length) {

    form.append('app_client_profile', {

      string: JSON.stringify(clientProfile),

      type: 'application/json',

      name: 'app_client_profile.json',

    } as unknown as Blob);

  }

  form.append('manifest', {

    string: JSON.stringify(manifest),

    type: 'application/json',

    name: 'bundle.json',

  } as unknown as Blob);



  for (const asset of manifest.assets) {

    const frames = (asset.frames as FrameRef[]) ?? [];

    for (const frame of frames) {

      const uri = `${bundleDir}${frame.relative_path}`;

      const name = frame.relative_path.split('/').pop() ?? `${frame.frame_id}.jpg`;

      form.append(frame.frame_id, {

        uri,

        type: 'image/jpeg',

        name,

      } as unknown as Blob);

    }

  }

  return form;

}



export async function runResearchPreview(

  endpoint: string,

  token: string,

  bundleDir: string,

  bundleJsonPath: string,

): Promise<X02PreviewResult> {

  const raw = await FileSystem.readAsStringAsync(bundleJsonPath);

  const manifest = JSON.parse(raw) as AppLibraryBundle;

  const prefs = useAppStore.getState().preferences.map((p) =>
    p.title ? `${p.title}: ${p.text}` : p.text,
  );

  const form = await buildBundleMultipartForm(bundleDir, manifest, {
    memory_preferences: prefs,
  });



  const previewUrl = await resolvePreviewUrl(endpoint, token);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15 * 60 * 1000);

  let res: Response;
  try {
    res = await fetch(previewUrl, {
      method: 'POST',
      headers: { Accept: 'application/json', ...auth(token) },
      body: form,
      signal: controller.signal,
    });
  } catch (e) {
    clearTimeout(timeout);
    if (e instanceof Error && e.name === 'AbortError') {
      throw new Error('Preview timed out after 15 minutes. Check server logs and retry.');
    }
    throw e;
  }
  clearTimeout(timeout);



  if (!res.ok) {

    let detail = `Preview failed (${res.status})`;

    try {

      const err = (await res.json()) as { message?: string; error?: string };

      if (err.message) detail = err.message;

      else if (err.error) detail = err.error;

    } catch {

      /* ignore */

    }

    throw new Error(detail);

  }



  return (await res.json()) as X02PreviewResult;

}


