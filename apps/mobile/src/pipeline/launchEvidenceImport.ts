import { Alert, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { fromPickerAssets } from './fromPicker';
import { enqueuePipeline } from './runPipeline';
import { createDemoPickedPhoto } from './createDemoPhoto';

/** IMP01 — system picker only; queues evidence pipeline (P3). */
export async function launchEvidenceImport(): Promise<void> {
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
    mediaTypes: ['images'],
    allowsMultipleSelection: Platform.OS === 'ios',
    selectionLimit: Platform.OS === 'ios' ? 3 : 1,
    quality: 0.9,
    exif: false,
  });
  if (result.canceled || !result.assets.length) return;

  const items = fromPickerAssets(result.assets);
  const taskId = enqueuePipeline(items);
  if (!taskId) {
    Alert.alert('Pipeline busy', 'Wait for the current cloud processing task to finish.');
    return;
  }
  Alert.alert(
    'Pipeline started',
    `${items.length} photo(s) queued. Watch Active tasks below, then open Diary.`,
  );
}

/** Bypass gallery — for Expo Go Android when picker/permissions fail. */
export async function launchDemoEvidenceImport(): Promise<void> {
  try {
    const item = await createDemoPickedPhoto();
    const taskId = enqueuePipeline([item]);
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
