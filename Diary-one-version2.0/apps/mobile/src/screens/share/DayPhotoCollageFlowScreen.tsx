import React, { useCallback, useEffect, useState } from 'react';
import { Alert, StyleSheet, Text } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { formatShortDay } from '../../domain/formatMedia';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { colors } from '../../theme';
import { chaptersForDate, useAppStore } from '../../store/useAppStore';
import { buildDayPhotoCollage } from '../../share/buildDayCollage';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { saveImageToPhotos, shareImageUri } from '../../share/shareActions';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFailedView, SharePreparingView } from '../../components/SharePhaseViews';
import { SharePreviewShell } from '../../components/SharePreviewShell';

type Route = RouteProp<DiaryStackParamList, 'DayPhotoCollageFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'DayPhotoCollageFlow'>;

const dayCollageCache = new Map<string, string>();

export default function DayPhotoCollageFlowScreen() {
  const { dateKey, phase } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapters = useAppStore((s) => chaptersForDate(s.chapters, dateKey));
  const [uri, setUri] = useState<string | null>(dayCollageCache.get(dateKey) ?? null);

  const runPrepare = useCallback(async () => {
    try {
      const out = await buildDayPhotoCollage(chapters);
      if (!out || shouldSimulateSharePrepareFailure()) {
        navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'failed' });
        return;
      }
      dayCollageCache.set(dateKey, out);
      setUri(out);
      navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'preview' });
    } catch {
      navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'failed' });
    }
  }, [chapters, dateKey, navigation]);

  useEffect(() => {
    if (phase === 'preparing') void runPrepare();
  }, [phase, runPrepare]);

  const back = () => navigation.goBack();

  if (phase === 'preparing') {
    return (
      <SafeAreaView style={styles.safePhase} edges={['top', 'bottom']}>
        <SharePreparingView cardLabel="Collage" status="Preparing your collage…" onCancel={back} />
      </SafeAreaView>
    );
  }

  if (phase === 'failed') {
    return (
      <SafeAreaView style={styles.safePhase} edges={['top', 'bottom']}>
        <ShareFailedView
          title="Couldn't prepare this share."
          subtitle="Your Diary is unchanged."
          onRetry={() => navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'preparing' })}
          onBack={back}
        />
      </SafeAreaView>
    );
  }

  const previewUri = uri ?? dayCollageCache.get(dateKey);

  return (
    <SharePreviewShell
      heading="Photo collage"
      title={formatShortDay(dateKey)}
      dateLabel={formatChapterDateLong(dateKey)}
      imageUri={previewUri}
      onBack={back}
      onShare={() =>
        previewUri && void shareImageUri(previewUri).catch((e) => Alert.alert('Share failed', String(e)))
      }
      onSave={() =>
        previewUri &&
        void saveImageToPhotos(previewUri)
          .then(() => Alert.alert('Saved', 'Collage saved to Photos.'))
          .catch((e) => Alert.alert('Save failed', String(e)))
      }
      onTryAnother={() => navigation.replace('ShareDaySelector', { dateKey })}
    />
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  safePhase: { flex: 1, backgroundColor: colors.paper },
});
