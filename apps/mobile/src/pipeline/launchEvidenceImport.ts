import { appStrings, appLocale } from '../domain/strings';
import { Alert, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { fromPickerAssets } from './fromPicker';
import { PHOTO_LIBRARY_TEST_SOURCE, PHOTO_LIBRARY_USER_SOURCE } from '../domain/mediaIntake';
import { diaryTodayKey } from '../domain/dayKey';
import { mediaDayKey } from '../domain/importDays';
import { enqueuePipeline } from './runPipeline';
import { createDemoPickedPhoto } from './createDemoPhoto';
import { createSimulationPickedVideo } from './createSimulationVideo';
import { dedupePickedMedia } from './dedupeMedia';
import { validatePickedMedia } from './validatePickedMedia';
import { useAppStore } from '../store/useAppStore';
import type { PickedMedia } from './types';
import { isLabToolsEnabled } from '../config/buildProfile';
import { resolveProductionBearer } from '../backend/resolveProductionBearer';
import { clearImportFeedback, useImportFeedbackStore } from '../store/useImportFeedbackStore';
import { showImportFailure } from './importFailure';

const MAX_BATCH = 6;
const copy = () => appStrings(useAppStore.getState().language);
const chinese = () => appLocale(useAppStore.getState().language) === 'zh-CN';
let importActive = false;

type ImportOperation = {
  assertActive: () => void;
  cancel: () => void;
  confirm: (title: string, message: string, label: string, dismissLabel?: string) => Promise<boolean>;
};

function notice(title: string, message: string) {
  useImportFeedbackStore.setState({ feedback: { kind: 'notice', title, message, dismiss: clearImportFeedback } });
}

function busy(operation: ImportOperation, message: string) {
  operation.assertActive();
  useImportFeedbackStore.setState({ feedback: { kind: 'busy',
    title: chinese() ? '正在准备导入' : 'Preparing import', message, dismiss: operation.cancel } });
}

function requireSignIn(): boolean {
  if (resolveProductionBearer()) return true;
  Alert.alert(
    copy().signInRequired,
    copy().signInHint,
  );
  return false;
}

function requireCloudConsent(): boolean {
  // Formal App: never silent-consent. User must opt in via Privacy / survey (PRI01).
  if (useAppStore.getState().cloudEvidenceConsent === true) return true;
  Alert.alert(
    copy().consentRequired,
    copy().consentHint,
  );
  return false;
}

async function pickMediaBatch(operation: ImportOperation): Promise<PickedMedia[] | null> {
  const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
  operation.assertActive();
  if (!perm.granted) {
    notice(
      copy().photosRequired,
      copy().photosHint,
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
      operation.assertActive();
      if (result.canceled || !result.assets?.length) break;
      collected.push(...fromPickerAssets(result.assets));
      if (collected.length >= MAX_BATCH) break;
      const more = await operation.confirm(copy().addAnother,
        chinese() ? `已选 ${collected.length} 份，最多 ${MAX_BATCH} 份。` : `${collected.length} selected (max ${MAX_BATCH}).`, copy().addAnother, copy().done);
      if (!more) break;
      busy(operation, chinese() ? '请选择下一份素材。' : 'Choose another file.');
    }
    return collected.length ? collected : null;
  }

  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ['images', 'videos'],
    allowsMultipleSelection: true,
    selectionLimit: MAX_BATCH,
    quality: 1,
    exif: true,
    // Photos may play a streamed preview while the original is only in iCloud.
    shouldDownloadFromNetwork: true,
    preferredAssetRepresentationMode: ImagePicker.UIImagePickerPreferredAssetRepresentationMode.Current,
  });
  operation.assertActive();
  if (result.canceled || !result.assets?.length) return null;
  return fromPickerAssets(result.assets);
}

async function enqueueValidated(picked: PickedMedia[], operation: ImportOperation): Promise<void> {
  const ownerToken = useAppStore.getState().sessionToken;
  const validated = validatePickedMedia(picked);
  if (!validated.ok) {
    notice(copy().cannotImport, chinese() ? validated.reasonZh : validated.reason);
    return;
  }
  const { unique, skippedSessionDupes, skippedLedgerDupes } = await dedupePickedMedia(
    validated.items,
    { assertActive: operation.assertActive, onProgress: (index, total) => busy(operation,
      chinese() ? `正在检查第 ${index}/${total} 份素材。视频较大时需要一些时间；此时尚未上传。`
        : `Checking file ${index}/${total}. Larger videos may take longer. Nothing has been uploaded yet.`) },
  );
  operation.assertActive();
  const skipped = skippedSessionDupes + skippedLedgerDupes;
  if (useAppStore.getState().sessionToken !== ownerToken) return;
  if (!unique.length) {
    notice(
      copy().alreadyImported,
      skipped
        ? copy().alreadyImportedHint
        : copy().nothingNew,
    );
    return;
  }
  const skippedMessage = skipped ? (chinese() ? `已跳过 ${skipped} 份重复素材。` : `${skipped} duplicate file(s) skipped.`) : '';
  const unknown = unique.filter((item) => !mediaDayKey(item));
  let ready = unique;
  if (unknown.length) {
    const day = diaryTodayKey();
    const confirmed = await operation.confirm(
      copy().captureDateMissing,
      skippedMessage + (chinese() ? `${unknown.length} 份素材没有拍摄日期，要归入 ${day} 的日记吗？这只设置日记日期，不会补造拍摄时间。` : `${unknown.length} selected file(s) have no capture date. Add them to ${day}? This sets the diary date only; it does not invent a capture time.`),
      chinese() ? `归入 ${day}` : `Use ${day}`,
    );
    if (!confirmed || useAppStore.getState().sessionToken !== ownerToken) return;
    ready = unique.map((item) => mediaDayKey(item) ? item : { ...item, confirmedDayKey: day });
  }
  operation.assertActive();
  if (!enqueuePipeline(ready, PHOTO_LIBRARY_USER_SOURCE)) notice(copy().importInProgress, copy().waitForImport);
  else notice(chinese() ? '已开始处理' : 'Processing started', skippedMessage + (chinese()
    ? `已接收 ${ready.length} 份素材，正在准备照片和视频帧。可在日记或设备页查看处理进度。`
    : `${ready.length} file(s) accepted. Preparing photos and video frames. Follow progress in Diary or Device.`));
}

/**
 * Hardware-free test / IMP path: system Photos library → Evidence → cloud → Diary.
 * Supports photos and videos (batch up to MAX_BATCH).
 */
export async function launchEvidenceImport(picker = pickMediaBatch): Promise<void> {
  // Keep the lock until native Photos settles, even if the user cancels our UI.
  // Starting a second picker while the first is downloading can lose its result.
  if (importActive) {
    if (!useImportFeedbackStore.getState().feedback) notice(copy().importInProgress,
      chinese() ? '上一次相册读取仍在结束，请稍候。如果一直没有结束，请重新打开 App 后重试。' : 'The previous Photos request is still finishing. Wait a moment; if it remains stuck, reopen the app.');
    return;
  }
  if (!requireSignIn()) return;
  const ownerToken = useAppStore.getState().sessionToken;
  if (!requireCloudConsent()) return;
  if (useAppStore.getState().pipelineTasks.some((t) => t.status !== 'failed' && t.status !== 'succeeded')) {
    notice(copy().importInProgress, copy().waitForImport);
    return;
  }
  importActive = true;
  let cancelled = false;
  let settleConfirmation: ((confirmed: boolean) => void) | undefined;
  let stage = 'READ';
  const operation: ImportOperation = {
    assertActive() {
      if (cancelled || useAppStore.getState().sessionToken !== ownerToken ||
          useAppStore.getState().cloudEvidenceConsent !== true) throw new Error('IMPORT_CANCELLED');
    },
    cancel() { cancelled = true; settleConfirmation?.(false); clearImportFeedback(); },
    confirm(title, message, label, dismissLabel) {
      operation.assertActive();
      return new Promise<boolean>((resolve) => {
        settleConfirmation = (value) => { settleConfirmation = undefined; resolve(value); clearImportFeedback(); };
        useImportFeedbackStore.setState({ feedback: { kind: 'confirm', title, message, dismissLabel,
          dismiss: () => settleConfirmation?.(false), confirm: { label, run: () => settleConfirmation?.(true) } } });
      });
    },
  };
  const unsubscribe = useAppStore.subscribe((state) => {
    if (state.sessionToken !== ownerToken || state.cloudEvidenceConsent !== true) operation.cancel();
  });
  try {
    busy(operation, chinese()
      ? '选好后会读取视频原文件；若保存在 iCloud 中，会先下载，请保持网络连接。较大的视频可能需要一些时间。'
      : 'After selection, the original files will be read. iCloud originals need a download, so stay connected. Larger videos may take longer.');
    const picked = await picker(operation);
    if (!picked?.length) return;
    operation.assertActive();
    stage = 'CHECK';
    await enqueueValidated(picked, operation);
  } catch (error) {
    if (!cancelled && useAppStore.getState().sessionToken === ownerToken &&
        useAppStore.getState().cloudEvidenceConsent === true) showImportFailure(error, stage);
  } finally {
    unsubscribe();
    settleConfirmation?.(false);
    importActive = false;
    if (useImportFeedbackStore.getState().feedback?.kind === 'busy') clearImportFeedback();
  }
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
  await launchEvidenceImport(async () => [await createDemoPickedPhoto()]);
}

/** Lab-only simulation video. */
export async function launchSimulationVideoImport(): Promise<void> {
  if (!isLabToolsEnabled) {
    Alert.alert('Not available', 'Simulation video is Lab-only.');
    return;
  }
  if (!requireCloudConsent()) return;
  const media = [await createSimulationPickedVideo()];
  await enqueuePipeline(media.map((item) => ({ ...item, confirmedDayKey: diaryTodayKey() })), PHOTO_LIBRARY_TEST_SOURCE);
}
