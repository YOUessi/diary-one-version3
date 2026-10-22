import type { LanguagePreference } from './appSettings';
import type { PipelineTaskStatus, PipelineTask } from '../pipeline/types';
import { appStrings, appLocale } from './strings';

export function requiresEvidenceRebuild(error = ''): boolean {
  return /EVIDENCE_INPUT_INVALID|EVIDENCE_IMAGE_INVALID|EVIDENCE_IMAGE_MODULE_MISSING|evidence_format_or_dimensions_mismatch|evidence_hash_mismatch|evidence_decode_failed|missing_input_frame/.test(error);
}

export function pipelineFailureDetail(error: string, language: LanguagePreference): string {
  const zh = appLocale(language) === 'zh-CN';
  if (error.includes('EVIDENCE_IMAGE_MODULE_MISSING')) return zh
    ? '请更新到最新测试版本后重新导入照片。错误编号：IMAGE_MODULE'
    : 'Update to the latest test build, then import again. Error code: IMAGE_MODULE';
  if (/EVIDENCE_IMAGE_INVALID|evidence_format_or_dimensions_mismatch/.test(error)) return zh
    ? '图片未能转换为所需格式，本次结果未保存。请更新到最新测试版本，重新从相册选择这些照片；若仍失败，请反馈所选照片。错误编号：IMAGE_FORMAT'
    : 'An image could not be converted to the required format. This result was not saved. Update to the latest test build and select these photos from the library again; if it still fails, report the selected photo. Error code: IMAGE_FORMAT';
  if (requiresEvidenceRebuild(error)) return zh
    ? '所选素材的上传文件不完整或未通过检查。请重新从相册选择照片或视频导入，不要重发这次失败的素材包。错误编号：EVIDENCE_INPUT'
    : 'The uploaded media is incomplete or failed validation. Select the original photos or videos again instead of resending this bundle. Error code: EVIDENCE_INPUT';
  if (/Cloud session expired|AUTH_REQUIRED|SESSION_(?:EXPIRED|REQUIRED)/i.test(error)) return zh
    ? '登录状态已失效或当前账号无权访问。请重新登录后继续。错误编号：SESSION'
    : 'Your session expired or this account cannot access the request. Sign in again to continue. Error code: SESSION';
  if (/Upload limit|day_revision_.*limit/i.test(error)) return zh
    ? '处理次数已达上限，或还有任务正在处理。请稍后重试。错误编号：UPLOAD_LIMIT'
    : 'The processing limit was reached or other jobs are still running. Try again later. Error code: UPLOAD_LIMIT';
  if (/^CLOUD_JOB_FAILED:X02\b/.test(error)) return zh
    ? '云端处理服务暂未完成请求。请稍后重试；若持续失败，请反馈操作时间和错误编号。错误编号：CLOUD_SERVICE'
    : 'The cloud processing service could not complete the request. Retry later; if it persists, report the time and error code. Error code: CLOUD_SERVICE';
  if (/network|internet|offline|timed out|timeout|poll unavailable|poll interrupted/i.test(error)) return zh
    ? '网络请求暂未完成。请检查网络后重试；如果已有云端任务，将继续查询原任务。错误编号：NETWORK'
    : 'The network request did not complete. Check your connection and retry; an existing cloud job will be queried again. Error code: NETWORK';
  if (/result_contract_rejected|not_admitted|RESULT_CONTRACT/i.test(error)) return zh
    ? '云端结果未通过完整性检查，本次结果未保存。请反馈此错误编号，已有日记不受影响。错误编号：RESULT_CONTRACT'
    : 'The cloud result failed validation and was not saved. Report this error code; existing diary entries are kept. Error code: RESULT_CONTRACT';
  if (/DAY_REVISION_CONFLICT/.test(error)) return zh
    ? '本次请求与已有任务的信息不一致。请反馈此错误编号，不要反复提交。错误编号：REVISION_CONFLICT'
    : 'This request conflicts with an existing job. Report this error code instead of submitting repeatedly. Error code: REVISION_CONFLICT';
  if (/ENOSPC|no space|disk.*full/i.test(error)) return zh
    ? '可用存储空间不足。请释放空间后重试。错误编号：STORAGE'
    : 'There is not enough storage. Free some space and retry. Error code: STORAGE';
  return zh
    ? '本次处理未完成。请稍后重试；若仍失败，请反馈错误编号及操作时间。错误编号：PIPELINE_FAILED'
    : 'Processing did not complete. Retry later; if it persists, report the error code and time. Error code: PIPELINE_FAILED';
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
