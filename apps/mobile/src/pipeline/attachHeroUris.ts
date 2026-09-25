import * as FileSystem from 'expo-file-system/legacy';

import type { AppLibraryBundle } from './bundleTypes';

import type { Chapter } from '../model';



type FrameRef = { relative_path: string };



export async function attachHeroUrisFromBundle(

  chapters: Chapter[],

  bundleDir: string,

  bundleJsonPath: string,

): Promise<Chapter[]> {

  const raw = await FileSystem.readAsStringAsync(bundleJsonPath);

  const manifest = JSON.parse(raw) as AppLibraryBundle;

  const frameUris: string[] = [];

  for (const asset of manifest.assets) {

    const frames = (asset?.frames as FrameRef[]) ?? [];

    for (const frame of frames) {

      if (frame.relative_path) frameUris.push(`${bundleDir}${frame.relative_path}`);

    }

  }

  if (!frameUris.length) return chapters;



  return chapters.map((ch, index) => {

    const heroUri = frameUris[index % frameUris.length];

    const moments = ch.moments.map((m, mi) =>

      mi === 0 ? { ...m, posterUri: heroUri, playbackUri: heroUri } : m,

    );

    return { ...ch, heroUri, moments };

  });

}


