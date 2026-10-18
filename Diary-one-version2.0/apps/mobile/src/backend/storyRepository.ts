import { commitStoryRevision, storyOwner } from '../db/sqlite';
import { useAppStore } from '../store/useAppStore';

const writing = new Set<string>();

export async function saveYourStory(chapterId: string, text: string | undefined, expectedRevision: number) {
  const initial = useAppStore.getState();
  const chapter = initial.chapters.find((item) => item.id === chapterId);
  if (!chapter) throw new Error('Memory unavailable');
  if (writing.has(chapterId)) throw new Error('Your note is already being saved');
  const assertCurrent = () => {
    const state = useAppStore.getState();
    const current = state.chapters.find((item) => item.id === chapterId);
    if (state.sessionToken !== initial.sessionToken || !current ||
        (current.yourStoryRevision ?? 0) !== expectedRevision) {
      throw new Error('Memory or account changed. Reopen this note before saving.');
    }
  };
  writing.add(chapterId);
  try {
    assertCurrent();
    const revision = await commitStoryRevision({
      owner: storyOwner(initial.localProfile), chapterId, expectedRevision,
      text, previousText: chapter.yourStory, assertCurrent,
    });
    assertCurrent();
    useAppStore.setState((state) => ({ chapters: state.chapters.map((item) => item.id === chapterId
      ? { ...item, yourStory: text, yourStoryRevision: revision } : item) }));
  } finally {
    writing.delete(chapterId);
  }
}
