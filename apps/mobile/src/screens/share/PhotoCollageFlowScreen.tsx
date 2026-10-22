import React, { useCallback, useEffect } from 'react';
import { Alert, StyleSheet, Text } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { buildChapterPhotoCollage } from '../../share/buildPhotoCollage';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { saveImageToPhotos, shareImageUri } from '../../share/shareActions';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFailedView, SharePreparingView } from '../../components/SharePhaseViews';
import { SharePreviewShell } from '../../components/SharePreviewShell';

type Route = RouteProp<DiaryStackParamList, 'PhotoCollageFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'PhotoCollageFlow'>;


export default function PhotoCollageFlowScreen() {
  const { chapterId, phase, previewUri } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));

  const runPrepare = useCallback(async (isCurrent: () => boolean) => {
    if (!chapter) {
      navigation.replace('PhotoCollageFlow', { chapterId, phase: 'failed' });
      return;
    }
    try {
      const out = await buildChapterPhotoCollage(chapter);
      if (!isCurrent()) return;
      if (!out || shouldSimulateSharePrepareFailure()) {
        navigation.replace('PhotoCollageFlow', { chapterId, phase: 'failed' });
        return;
      }
      navigation.replace('PhotoCollageFlow', { chapterId, phase: 'preview', previewUri: out });
    } catch {
      if (!isCurrent()) return;
      navigation.replace('PhotoCollageFlow', { chapterId, phase: 'failed' });
    }
  }, [chapter, chapterId, navigation]);

  useEffect(() => {
    let active = true;
    const token = useAppStore.getState().sessionToken;
    if (phase === 'preparing') void runPrepare(() => active && useAppStore.getState().sessionToken === token);
    return () => { active = false; };
  }, [phase, runPrepare]);

  const back = () => navigation.navigate('ChapterDetail', { chapterId });

  if (!chapter) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text>Memory unavailable.</Text>
      </SafeAreaView>
    );
  }

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
          subtitle="Your memory is unchanged."
          onRetry={() => navigation.replace('PhotoCollageFlow', { chapterId, phase: 'preparing' })}
          onBack={back}
        />
      </SafeAreaView>
    );
  }


  const onShare = async () => {
    if (!previewUri) {
      Alert.alert('No image', 'This memory has no shareable image yet.');
      return;
    }
    try {
      await shareImageUri(previewUri);
    } catch (e) {
      Alert.alert('Share failed', e instanceof Error ? e.message : String(e));
    }
  };

  const onSave = async () => {
    if (!previewUri) return;
    try {
      await saveImageToPhotos(previewUri);
      Alert.alert('Saved', 'Collage saved to Photos.');
    } catch (e) {
      Alert.alert('Save failed', e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <SharePreviewShell
      heading="Photo collage"
      title={chapter.title}
      dateLabel={formatChapterDateLong(chapter.dateKey)}
      body={chapter.aiStory}
      imageUri={previewUri}
      onBack={back}
      onShare={() => void onShare()}
      onSave={() => void onSave()}
      onTryAnother={() => navigation.replace('ShareMemorySelector', { chapterId })}
    />
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  safePhase: { flex: 1, backgroundColor: colors.paper },
});
