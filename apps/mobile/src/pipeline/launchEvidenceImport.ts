import { Alert, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { fromPickerAssets } from './fromPicker';
import { PHOTO_LIBRARY_TEST_SOURCE, PHOTO_LIBRARY_USER_SOURCE } from '../domain/mediaIntake';
import { enqueuePipeline } from './runPipeline';
import { createDemoPickedPhoto } from './createDemoPhoto';
import { createSimulationPickedVideo } from './createSimulationVideo';
import { dedupePickedMedia } from './dedupeMedia';
import { validatePickedMedia } from './validatePickedMedia';
import { ensureDevCloudConsentForLab } from '../config/applyDevCloudDefaults';
import { useAppStore } from '../store/useAppStore';

/** IMP01 — system picker；图+视频 → 校验 → 去重 → 抽帧/压缩 → 云。 */
export async function launchEvidenceImportFromLibrary(
  intakeSource: typeof PHOTO_LIBRARY_TEST_SOURCE | typeof PHOTO_LIBRARY_USER_SOURCE = PHOTO_LIBRARY_USER_SOURCE,
): Promise<void> {
  ensureDevCloudConsentForLab();
  if (useAppStore.getState().cloudEvidenceConsent !== true) {
    Alert.alert(
      'Cloud consent required',
      'Turn on Account → Privacy & Data → Allow cloud evidence (or Lab 1b), then import again.',
    );
    return;
  }
  const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (!perm.granted) {
    Alert.alert(
      'Photos access needed',
      Platform.OS === 'android'
        ? 'Allow photos, or use Demo photo in Lab (Expo Go Android often limits gallery).'
        : 'Allow photo access to run the local evidence pipeline.',
    );
    return;
  }
  const result = await ImagePicker.launchImageLibraryAsync({
    // PRD：相册主动选入图/视频；抽帧逻辑在 buildAppLibraryBundle
    mediaTypes: ['images', 'videos'],
    allowsMultipleSelection: Platform.OS === 'ios',
    selectionLimit: Platform.OS === 'ios' ? 6 : 1,
    quality: 1,
    exif: false,
    videoMaxDuration: 120,
  });
  if (result.canceled || !result.assets.length) return;

  const picked = fromPickerAssets(result.assets);
  const validated = validatePickedMedia(picked);
  if (!validated.ok) {
    Alert.alert('Invalid media', validated.reason);
    return;
  }

  const { unique, skippedSessionDupes, skippedLedgerDupes } = await dedupePickedMedia(validated.items);
  if (!unique.length) {
    Alert.alert(
      'All duplicates',
      `Skipped ${skippedSessionDupes + skippedLedgerDupes} duplicate(s). Nothing new to process.`,
    );
    return;
  }

  const taskId = enqueuePipeline(unique, intakeSource);
  if (!taskId) {
    Alert.alert('Pipeline busy', 'Wait for the current cloud processing task to finish.');
    return;
  }
  const skipNote =
    skippedSessionDupes + skippedLedgerDupes > 0
      ? ` Skipped ${skippedSessionDupes + skippedLedgerDupes} duplicate(s).`
      : '';
  Alert.alert(
    'Pipeline started',
    `${unique.length} item(s) queued (validate → dedupe → compress/frames → Evidence).${skipNote} Watch Active tasks, then Diary.`,
  );
}

/** Bypass gallery — for Expo Go Android when picker/permissions fail. */
export async function launchDemoEvidenceImport(): Promise<void> {
  try {
    ensureDevCloudConsentForLab();
    if (useAppStore.getState().cloudEvidenceConsent !== true) {
      Alert.alert(
        'Cloud consent required',
        'Turn on Account → Privacy & Data → Allow cloud evidence (or Lab 1b), then tap Demo again.',
      );
      return;
    }
    const item = await createDemoPickedPhoto();
    // Demo 每次新文件；允许重复跑真云（skipKnownLedger=false）
    const { unique } = await dedupePickedMedia([item], { skipKnownLedger: false });
    const taskId = enqueuePipeline(unique, PHOTO_LIBRARY_TEST_SOURCE);
    if (!taskId) {
      Alert.alert('Pipeline busy', 'Wait for the current task to finish.');
      return;
    }
    Alert.alert(
      'Demo pipeline started',
      'Synthetic photo → Bundle → BFF → Diary. Watch Active tasks, then open Diary tab.',
    );
  } catch (e) {
    Alert.alert('Demo import failed', e instanceof Error ? e.message : String(e));
  }
}

/** Lab / Device — keeps PHOTO_LIBRARY_TEST intake label. */
export async function launchEvidenceImport(): Promise<void> {
  return launchEvidenceImportFromLibrary(PHOTO_LIBRARY_TEST_SOURCE);
}

/** Bundled assets/motion clip → same cloud pipeline as gallery video. */
export async function launchSimulationVideoImport(): Promise<void> {
  try {
    ensureDevCloudConsentForLab();
    if (useAppStore.getState().cloudEvidenceConsent !== true) {
      Alert.alert(
        'Cloud consent required',
        'Turn on Account → Privacy & Data → Allow cloud evidence (or Lab 1b), then import again.',
      );
      return;
    }
    const item = await createSimulationPickedVideo();
    const { unique } = await dedupePickedMedia([item], { skipKnownLedger: false });
    const taskId = enqueuePipeline(unique, PHOTO_LIBRARY_TEST_SOURCE);
    if (!taskId) {
      Alert.alert('Pipeline busy', 'Wait for the current task to finish.');
      return;
    }
    Alert.alert(
      'Simulation video queued',
      'Bundled sim-morning.mp4 → frames → BFF → Diary. Watch Active tasks.',
    );
  } catch (e) {
    Alert.alert('Simulation import failed', e instanceof Error ? e.message : String(e));
  }
}
