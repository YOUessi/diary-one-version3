import type { Chapter, SmallMemory } from '../model';
import type { X02PreviewResult } from './types';

function formatDateLabel(dayKey: string): string {
  const [y, m, d] = dayKey.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

function isVisibleChapter(result: X02PreviewResult, chapterId: string, publication: string) {
  if (publication !== 'STAGED_PREVIEW_VALIDATED') return false;
  const outcome = result.selected_memory_outcomes.find(
    (o) => o.memory_type === 'CHAPTER' && o.memory_id === chapterId,
  );
  return outcome?.visibility_state === 'VISIBLE_PREVIEW';
}

function isVisibleAha(result: X02PreviewResult, ahaId: string, publication: string) {
  if (publication !== 'STAGED_PREVIEW_VALIDATED') return false;
  const outcome = result.selected_memory_outcomes.find(
    (o) => o.memory_type === 'AHA' && o.memory_id === ahaId,
  );
  return outcome?.visibility_state === 'VISIBLE_PREVIEW';
}

export function mapPreviewToDiary(
  result: X02PreviewResult,
  dayKey: string,
): { chapters: Chapter[]; smallMemories: SmallMemory[] } {
  const dateLabel = formatDateLabel(dayKey);

  const chapters: Chapter[] = result.chapters
    .filter((ch) => isVisibleChapter(result, ch.id, ch.publication_status))
    .map((ch) => ({
      id: ch.id,
      title: ch.title,
      dateKey: dayKey,
      dateLabel,
      weakTime: ch.time_label || undefined,
      aiStory: ch.story,
      tags: ch.tags.slice(0, 2),
      detailTags: ch.tags.length > 2 ? ch.tags.slice(2) : undefined,
      moments: ch.moment_ids.map((id, index) => ({
        id,
        label: ch.time_label && index === 0 ? ch.time_label : `Moment ${index + 1}`,
      })),
    }));

  const smallMemories: SmallMemory[] = result.ahas
    .filter((a) => isVisibleAha(result, a.id, a.publication_status))
    .map((a) => ({ id: a.id, text: a.story }));

  return { chapters, smallMemories };
}
