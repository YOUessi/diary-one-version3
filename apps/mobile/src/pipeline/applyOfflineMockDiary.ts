import { Alert } from 'react-native';
import { diaryTodayKey } from '../domain/dayKey';
import { applyDiaryDayUpdate, applyTodayStatus } from '../store/applyDiaryDay';
import { useAppStore } from '../store/useAppStore';
import type { Chapter, SmallMemory } from '../model';

/** Guaranteed Expo Go path: write sample memories without cloud/gallery. */
export function applyOfflineMockDiary(): void {
  const dayKey = diaryTodayKey();
  const id = `offline-${Date.now()}`;
  const chapter: Chapter = {
    id: `${id}-ch`,
    title: 'Offline test memory',
    dateKey: dayKey,
    dateLabel: new Date().toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    }),
    weakTime: 'Afternoon',
    aiStory:
      'This chapter was inserted on-device to verify Diary UI without BFF. Replace with Demo photo → cloud when pipeline is green.',
    tags: ['Test', 'Offline'],
    moments: [{ id: `${id}-m0`, label: 'Moment 1' }],
  };
  const small: SmallMemory[] = [
    { id: `${id}-aha`, text: 'Offline small memory — tap Diary to confirm UI update.' },
  ];
  applyDiaryDayUpdate(dayKey, [chapter], small);
  applyTodayStatus('READY');
  useAppStore.setState({
    pipelineTasks: [
      {
        id: `task-offline-${Date.now()}`,
        createdAt: new Date().toISOString(),
        dayKey,
        dayRevisionId: `dayrev_offline_${Date.now()}`,
        intakeSource: 'PHOTO_LIBRARY_TEST',
        status: 'succeeded',
        message: 'Offline mock Diary write (no cloud)',
        sourceCount: 0,
      },
      ...useAppStore.getState().pipelineTasks,
    ],
  });
  Alert.alert(
    'Diary updated (offline)',
    'Open the Diary tab — you should see “Offline test memory”. Then retry Demo photo for cloud.',
  );
}
