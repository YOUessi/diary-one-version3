import { Alert, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { fromPickerAssets } from './fromPicker';
import { PHOTO_LIBRARY_TEST_SOURCE } from '../domain/mediaIntake';
import { enqueuePipeline } from './runPipeline';
import { createDemoPickedPhoto } from './createDemoPhoto';
import { createSimulationPickedVideo } from './createSimulationVideo';
import { dedupePickedMedia } from './dedupeMedia';
import { validatePickedMedia } from './validatePickedMedia';
import { useAppStore } from '../store/useAppStore';
import type { PickedMedia } from './types';
import { isLabToolsEnabled } from '../config/buildProfile';
import { resolveProductionBearer } from '../backend/resolveProductionBearer';

const MAX_BATCH = 6;

function requireSignIn(): boolean {
  if (resolveProductionBearer()) return true;
  Alert.alert(
    'Sign in required',
    'Open Account → Continue with Email and complete verification before uploading.',
  );
  return false;
}

function requireCloudConsent(retryHint: string): boolean {
  // Formal App: never silent-consent. User must opt in via Privacy / survey (PRI01).
  if (useAppStore.getState().cloudEvidenceConsent === true) return true;
  Alert.alert(
    'Cloud consent required',
    `Open Account → Privacy & Data → Allow cloud evidence upload, then ${retryHint}.`,
  );
  return false;
}

async function pickMediaBatch(): Promise<PickedMedia[] | null> {
  const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (!perm.granted) {
    Alert.alert(
      'Photos access needed',
      'Allow photos access to import selected photos and videos into Diary One.',
    );
    return null;
  }

  if (Platform.OS === 'android') {
    const collected: PickedMedia[] = [];
    while (collected.length < MAX_BATCH) {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images', 'videos'],
        allowsMultipleSelection: false,
        quality: 1,
        exif: true,
      });
      if (result.canceled || !result.assets?.length) break;
      collected.push(...fromPickerAssets(result.assets));
      if (collected.length >= MAX_BATCH) break;
      const more = await new Promise<boolean>((resolve) => {
        Alert.alert('Add another?', `${collected.length} selected (max ${MAX_BATCH}).`, [
          { text: 'Done', style: 'cancel', onPress: () => resolve(false) },
          { text: 'Add another', onPress: () => resolve(true) },
        ]);
      });
      if (!more) break;
    }
    return collected.length ? collected : null;
  }

  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ['images', 'videos'],
    allowsMultipleSelection: true,
    selectionLimit: MAX_BATCH,
    quality: 1,
    exif: true,
  });
  if (result.canceled || !result.assets?.length) return null;
  return fromPickerAssets(result.assets);
}

async function enqueueValidated(picked: PickedMedia[]): Promise<void> {
  const validated = await validatePickedMedia(picked);
  if (!validated.ok) {
    Alert.alert('Cannot import', validated.reason);
    return;
  }
  const { unique, skippedSessionDupes, skippedLedgerDupes } = await dedupePickedMedia(
    validated.items,
  );
  const skipped = skippedSessionDupes + skippedLedgerDupes;
  if (!unique.length) {
    Alert.alert(
      'Already imported',
      skipped
        ? 'These files were already processed successfully. Pick different photos or videos.'
        : 'Nothing new to import.',
    );
    return;
  }
  if (skipped) {
    Alert.alert('Skipped duplicates', `${skipped} already-processed file(s) skipped.`);
  }
  await enqueuePipeline(unique, PHOTO_LIBRARY_TEST_SOURCE);
}

/**
 * Hardware-free test / IMP path: system Photos library → Evidence → cloud → Diary.
 * Supports photos and videos (batch up to MAX_BATCH).
 */
export async function launchEvidenceImport(): Promise<void> {
  if (!requireSignIn()) return;
  if (!requireCloudConsent('try Upload again')) return;
  const picked = await pickMediaBatch();
  if (!picked?.length) return;
  await enqueueValidated(picked);
}

/** Alias used by Device / Diary upload CTAs. */
export async function launchEvidenceImportFromLibrary(): Promise<void> {
  return launchEvidenceImport();
}

/** Lab-only seeded demo photo. */
export async function launchDemoEvidenceImport(): Promise<void> {
  if (!isLabToolsEnabled) {
    Alert.alert('Not available', 'Demo import is Lab-only (set EXPO_PUBLIC_ENABLE_LAB=1).');
    return;
  }
  if (!requireCloudConsent('try Demo again')) return;
  const media = [await createDemoPickedPhoto()];
  await enqueueValidated(media);
}

/** Lab-only simulation video. */
export async function launchSimulationVideoImport(): Promise<void> {
  if (!isLabToolsEnabled) {
    Alert.alert('Not available', 'Simulation video is Lab-only.');
    return;
  }
  if (!requireCloudConsent('try again')) return;
  const media = [await createSimulationPickedVideo()];
  await enqueuePipeline(media, PHOTO_LIBRARY_TEST_SOURCE);
}
