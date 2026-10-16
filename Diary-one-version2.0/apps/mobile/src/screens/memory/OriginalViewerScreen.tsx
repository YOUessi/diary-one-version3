import React from 'react';
import { Text, Pressable, StyleSheet, View, Image, Alert } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Sharing from 'expo-sharing';
import * as MediaLibrary from 'expo-media-library/legacy';
import { colors, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';
import { OriginalVideoPlayer } from '../../components/OriginalVideoPlayer';

type Route = RouteProp<MemoryStackParamList, 'OriginalViewer'>;
type Nav = NativeStackNavigationProp<MemoryStackParamList, 'OriginalViewer'>;

/** Figma 65:1042 — black immersive viewer, cream media card, 3 bottom actions. */
export default function OriginalViewerScreen() {
  const { captureId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const item = useAppStore((s) => s.capturedOriginals.find((c) => c.id === captureId));

  const shareOriginal = async () => {
    if (!item) return;
    try {
      const fileUri = item.playbackUri ?? item.posterUri;
      if (fileUri && (await Sharing.isAvailableAsync())) {
        await Sharing.shareAsync(fileUri, { dialogTitle: 'Share original' });
        return;
      }
      Alert.alert('Share', 'No shareable file URI yet for this original.');
    } catch (e) {
      Alert.alert('Share failed', e instanceof Error ? e.message : String(e));
    }
  };

  const saveToPhotos = async () => {
    const mediaUri = item?.playbackUri ?? item?.posterUri;
    if (!mediaUri) {
      Alert.alert(
        'Not available',
        'Full-resolution originals arrive after device sync. Only synced media can be saved to Photos.',
      );
      return;
    }
    const perm = await MediaLibrary.requestPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('Permission needed', 'Allow Photos access to save this original.');
      return;
    }
    try {
      await MediaLibrary.saveToLibraryAsync(mediaUri);
      Alert.alert('Saved', 'Saved to your photo library.');
    } catch (e) {
      Alert.alert('Save failed', e instanceof Error ? e.message : String(e));
    }
  };

  const videoUri = item?.kind === 'video' ? item.playbackUri : undefined;
  const imageUri = item?.posterUri ?? (item?.kind === 'photo' ? item.playbackUri : undefined);

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <View style={styles.topBar}>
        <Pressable onPress={() => navigation.goBack()} style={styles.back} hitSlop={12}>
          <Text style={styles.backText}>‹</Text>
        </Pressable>
        <Text style={styles.viewerMeta} numberOfLines={1}>
          {item?.capturedAtLabel ?? 'Captured by You'}
        </Text>
      </View>

      <View style={styles.viewer}>
        {videoUri ? (
          <OriginalVideoPlayer uri={videoUri} durationSec={item?.durationSec} />
        ) : imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.image} resizeMode="cover" />
        ) : (
          <View style={styles.placeholder}>
            <View style={styles.placeholderOrb} />
            <View style={styles.placeholderWave} />
          </View>
        )}
      </View>

      <View style={styles.actions}>
        <Pressable style={styles.actionBtn} onPress={() => void saveToPhotos()}>
          <Text style={styles.actionIcon}>⇩</Text>
          <Text style={styles.actionText}>Save to Photos</Text>
        </Pressable>
        <Pressable style={styles.actionBtn} onPress={() => void shareOriginal()}>
          <Text style={styles.actionIcon}>↗</Text>
          <Text style={styles.actionText}>Share</Text>
        </Pressable>
        <Pressable
          style={styles.actionBtn}
          onPress={() => navigation.navigate('OriginalDeleteConfirm', { captureId })}
        >
          <Text style={styles.actionIcon}>⌫</Text>
          <Text style={styles.actionText}>Delete Original</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#000000' },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingLeft: spacing.sm,
    paddingRight: layout.gutterDiary,
    minHeight: 44,
    gap: 4,
  },
  back: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  backText: { fontSize: 34, color: colors.paper, fontWeight: '600', lineHeight: 36 },
  /** Figma — meta left of center, opacity 72% */
  viewerMeta: {
    flex: 1,
    fontSize: 13,
    lineHeight: 18,
    color: colors.paper,
    opacity: 0.72,
    textAlign: 'left',
  },
  /** Figma 65:1042 — media cream; Viewer Actions 353×72, buttons 112×64 */
  viewer: {
    flex: 1,
    marginHorizontal: layout.gutterDiary,
    marginTop: spacing.md,
    marginBottom: spacing.lg,
    borderRadius: 16,
    backgroundColor: colors.surface,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  image: { width: '100%', height: '100%' },
  placeholder: { flex: 1, width: '100%', backgroundColor: colors.paper },
  placeholderOrb: {
    position: 'absolute',
    top: '18%',
    right: '18%',
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.accentSoft,
  },
  placeholderWave: {
    position: 'absolute',
    left: '-20%',
    right: '-20%',
    bottom: -40,
    height: 160,
    borderRadius: 999,
    backgroundColor: colors.card,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.md,
    minHeight: 72,
  },
  actionBtn: {
    width: 112,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 64,
    gap: 4,
  },
  actionIcon: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.paper },
  actionText: {
    fontSize: 11,
    lineHeight: 14,
    letterSpacing: 0.1,
    color: colors.paper,
    opacity: 0.68,
    textAlign: 'center',
  },
});
