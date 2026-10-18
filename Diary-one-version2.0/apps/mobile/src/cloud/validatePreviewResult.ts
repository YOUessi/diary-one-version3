import type { X02PreviewResult } from './types';
import { ALGORITHM_LOCK } from '../config/algorithmLock';
import { admitDeliveryState } from './deliveryAdmit';
import { isFormalConsumerApp, isLabToolsEnabled } from '../config/buildProfile';
import { validateResultBinding, type ResultInput } from './validateResultBinding';

export type ValidateOutcome =
  | { ok: true; honestEmpty?: boolean }
  | { ok: false; reason: string };

/** fail-closed：对齐 BFF result_admit + eval-web 消费门槛（PRD DAT01 / AI03）。 */
export function validatePreviewResult(result: X02PreviewResult, input?: ResultInput): ValidateOutcome {
  if (!result || typeof result !== 'object') return { ok: false, reason: 'Invalid result object' };
  try {
    if (!input && isFormalConsumerApp) throw new Error('Missing submitted input for validation');
    if (input) validateResultBinding(result, input, isFormalConsumerApp);
  } catch (error) {
    return { ok: false, reason: error instanceof Error ? error.message : 'Invalid result binding' };
  }
  if (result.schema_version !== ALGORITHM_LOCK.previewSchema) {
    return { ok: false, reason: `Unexpected schema_version: ${result.schema_version}` };
  }
  if (!Array.isArray(result.chapters) || !Array.isArray(result.ahas)) {
    return { ok: false, reason: 'Missing chapters or ahas array' };
  }
  if (!Array.isArray(result.selected_memory_outcomes)) {
    return { ok: false, reason: 'Missing selected_memory_outcomes' };
  }

  for (const ch of result.chapters) {
    if (!ch.id || !ch.title || typeof ch.story !== 'string') {
      return { ok: false, reason: 'Invalid chapter shape' };
    }
    if (ch.publication_status === 'STAGED_PREVIEW_VALIDATED') {
      const outcome = result.selected_memory_outcomes.find(
        (o) => o.memory_type === 'CHAPTER' && o.memory_id === ch.id,
      );
      if (!outcome) {
        return { ok: false, reason: `Chapter ${ch.id} missing outcome` };
      }
    }
  }

  for (const a of result.ahas) {
    if (!a.id || typeof a.story !== 'string') {
      return { ok: false, reason: 'Invalid aha shape' };
    }
    if (a.publication_status === 'STAGED_PREVIEW_VALIDATED') {
      const outcome = result.selected_memory_outcomes.find(
        (o) => o.memory_type === 'AHA' && o.memory_id === a.id,
      );
      if (!outcome) {
        return { ok: false, reason: `Aha ${a.id} missing outcome` };
      }
    }
  }

  const labAllowMock =
    isLabToolsEnabled && (process.env.EXPO_PUBLIC_ALLOW_MOCK_DIARY ?? '').trim() === '1';
  if (result.dev_lite_fallback === true && !labAllowMock) {
    return {
      ok: false,
      reason: 'Rejected mock fallback (dev_lite_fallback). PRD AI03.',
    };
  }

  const publish = (
    result as {
      _publish?: {
        publish_admit?: boolean;
        admit_reason?: string;
        is_mock_fallback?: boolean;
        source?: string;
      };
    }
  )._publish;

  if (
    (publish?.is_mock_fallback === true || publish?.source === 'dev_lite_fallback') &&
    !labAllowMock
  ) {
    return { ok: false, reason: 'Rejected mock _publish payload.' };
  }
  if (publish && publish.publish_admit === false) {
    return { ok: false, reason: `Not admitted: ${publish.admit_reason ?? 'unknown'}` };
  }

  // Formal consumer App: require BFF _publish envelope.
  if (isFormalConsumerApp && !publish && !labAllowMock) {
    return { ok: false, reason: 'Missing _publish envelope (consumer App / AI03).' };
  }

  const deliveryAdmit = admitDeliveryState(result.delivery_state, {
    isMock: result.dev_lite_fallback === true,
    allowMock: labAllowMock,
  });
  if (!deliveryAdmit.admit) {
    return { ok: false, reason: `Delivery not admitted: ${deliveryAdmit.reason}` };
  }

  const visibleOutcomes = result.selected_memory_outcomes.filter(
    (o) => o.visibility_state === 'VISIBLE_PREVIEW',
  );
  const stagedChapters = result.chapters.filter(
    (c) => c.publication_status === 'STAGED_PREVIEW_VALIDATED',
  );
  if (stagedChapters.length > 0 && visibleOutcomes.length === 0) {
    return { ok: false, reason: 'Staged chapters without VISIBLE_PREVIEW outcomes' };
  }

  return { ok: true, honestEmpty: deliveryAdmit.honestEmpty };
}
