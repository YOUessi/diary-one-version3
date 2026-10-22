import type { LanguagePreference } from './appSettings';
import type { PipelineTaskStatus, PipelineTask } from '../pipeline/types';
import { appStrings, appLocale } from './strings';

export function requiresEvidenceRebuild(error = ''): boolean {
  return /EVIDENCE_IMAGE_INVALID|EVIDENCE_IMAGE_MODULE_MISSING|evidence_format_or_dimensions_mismatch/.test(error);
}

export function pipelineFailureDetail(error: string, language: LanguagePreference): string {
  const zh = appLocale(language) === 'zh-CN';
  if (error.includes('EVIDENCE_IMAGE_MODULE_MISSING')) return zh
    ? '请更新到最新测试版本后重新导入照片。错误编号：IMAGE_MODULE'
    : 'Update to the latest test build, then import again. Error code: IMAGE_MODULE';
  if (/EVIDENCE_IMAGE_INVALID|evidence_format_or_dimensions_mismatch/.test(error)) return zh
    ? '图片未能转换为所需格式，本次结果未保存。请更新到最新测试版本，重新从相册选择这些照片；若仍失败，请反馈所选照片。错误编号：IMAGE_FORMAT'
    : 'An image could not be converted to the required format. This result was not saved. Update to the latest test build and select these photos from the library again; if it still fails, report the selected photo. Error code: IMAGE_FORMAT';
  return error.slice(0, 500);
}

export function pipelineStatusLabel(status: PipelineTaskStatus, language: LanguagePreference) {
  const s = appStrings(language);
  return { queued: s.queued, building_evidence: s.buildingEvidence, bundle_ready: s.bundleReady,
    uploading: s.uploading, cloud_processing: s.cloudProcessing, succeeded: s.succeeded, failed: s.failed }[status];
}

export function pipelineTaskLabel(task: PipelineTask, language: LanguagePreference) {
  const s = appStrings(language);
  if (task.status === 'succeeded') {
    if (task.deliverySummary?.outcome === 'partial') {
      return task.deliverySummary.savedMemoryCount ? s.partialSaved : s.partialNotSaved;
    }
    // Previously saved tasks may only contain the cloud state in their message.
    if (/READY_WITH_ITEM_BLOCKS|PARTIAL_UNRESOLVED|READY_WITH_GROUNDED_COPY_FALLBACK/.test(task.message)) return s.partial;
    if (task.deliverySummary?.outcome === 'empty' || /0 memories|No new memories|empty day/.test(task.message)) return s.noNewMemories;
  }
  return pipelineStatusLabel(task.status, language);
}

export function pipelineTaskDetail(task: PipelineTask, language: LanguagePreference) {
  if (task.status === 'failed' && task.error) return pipelineFailureDetail(task.error, language);
  if (task.status !== 'succeeded' || task.deliverySummary?.outcome !== 'partial') return undefined;
  const s = appStrings(language), summary = task.deliverySummary;
  const explanation = summary.reason === 'UNRESOLVED_EVIDENCE' ? s.partialEvidenceHint
    : summary.reason === 'COPY_FALLBACK' ? s.partialCopyHint : '';
  return [summary.savedMemoryCount ? s.partialSavedHint : s.partialNotSavedHint, explanation].filter(Boolean).join(' ');
}
