import { appStrings, appLocale } from '../domain/strings';
import { useAppStore } from '../store/useAppStore';
import { clearImportFeedback, useImportFeedbackStore } from '../store/useImportFeedbackStore';

/** Stable, actionable feedback without exposing native paths, tokens or stack traces. */
export function showImportFailure(error: unknown, stage = 'READ'): void {
  const language = useAppStore.getState().language;
  const zh = appLocale(language) === 'zh-CN';
  const message = error instanceof Error ? error.message : String(error);
  const code = /ENOSPC|disk.*full|no space|空间不足/i.test(message) ? 'STORAGE'
    : /network|internet|iCloud|PHPhotosErrorDomain.*(3164|3169)|网络|互联网/i.test(message) ? 'DOWNLOAD' : stage;
  const hint = code === 'STORAGE'
    ? (zh ? '手机可用空间不足。请释放一些空间后重新选择素材。' : 'Your phone is low on storage. Free some space, then select the media again.')
    : code === 'DOWNLOAD'
      ? (zh ? '素材原文件未能下载。请确认网络可用，在“照片”中打开所选素材并等待原文件下载完成，再重试。' : 'The original media could not be downloaded. Check your connection, open it in Photos and let it finish downloading, then retry.')
      : (zh ? '未能读取或检查所选素材。请先尝试只选一份素材；若仍失败，可将下方错误编号反馈给我们。' : 'The selected media could not be read or checked. Try one file first. If it still fails, report the error code below.');
  useImportFeedbackStore.setState({ feedback: { kind: 'error', title: appStrings(language).cannotImport,
    message: `${hint}\n${zh ? '错误编号' : 'Error code'}：IMPORT_${code}`, dismiss: clearImportFeedback } });
}
