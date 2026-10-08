import React from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';

type Route = RouteProp<DiaryStackParamList, 'ShareMemorySelector'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ShareMemorySelector'>;

/** Figma 184:1976 — sheet r24, options r14 + 94×100 thumb. */
export default function ShareMemorySelectorScreen() {
  const { chapterId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));
  const thumb = chapter?.heroUri ?? chapter?.moments[0]?.posterUri;

  const close = () => navigation.goBack();

  return (
    <View style={styles.root}>
      <Pressable style={styles.dim} onPress={close} accessibilityLabel="Dismiss share options" />
      <SafeAreaView edges={['bottom']} style={styles.sheet}>
        <View style={styles.handle} />
        <View style={styles.handleRow}>
          <Text style={styles.sheetTitle}>Share memory</Text>
          <Pressable onPress={close} hitSlop={12} accessibilityLabel="Close" style={styles.closeHit}>
            <Text style={styles.close}>×</Text>
          </Pressable>
        </View>

        <Pressable
          style={styles.option}
          onPress={() => navigation.replace('PhotoCollageFlow', { chapterId, phase: 'preparing' })}
        >
          <OptionThumb uri={thumb} tint={false} />
          <View style={styles.optionCopy}>
            <Text style={styles.optionTitle}>Photo collage</Text>
            <Text style={styles.optionBody}>A clean layout using moments from this memory.</Text>
          </View>
        </Pressable>
        <Pressable
          style={styles.option}
          onPress={() => navigation.replace('IllustratedShareFlow', { chapterId, phase: 'picker' })}
        >
          <OptionThumb uri={thumb} tint />
          <View style={styles.optionCopy}>
            <Text style={styles.optionTitle}>Illustrated memory</Text>
            <Text style={styles.optionBody}>A stylized version created from this memory.</Text>
          </View>
        </Pressable>
      </SafeAreaView>
    </View>
  );
}

function OptionThumb({ uri, tint }: { uri?: string; tint: boolean }) {
  return (
    <View style={[styles.thumb, tint && styles.thumbTinted]}>
      {uri ? <Image source={{ uri }} style={styles.thumbImage} resizeMode="cover" /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'transparent' },
  dim: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.35)' },
  sheet: {
    backgroundColor: colors.paper,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.sm,
    paddingBottom: spacing.lg,
  },
  handle: {
    alignSelf: 'center',
    width: 36,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.divider,
    marginBottom: spacing.md,
  },
  handleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  sheetTitle: {
    fontSize: 28,
    lineHeight: 34,
    fontWeight: '600',
    letterSpacing: -0.2,
    color: colors.ink,
  },
  closeHit: {
    width: layout.minTouch,
    height: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  close: { fontSize: 26, color: colors.ink, fontWeight: '300', lineHeight: 32 },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: 14,
    backgroundColor: colors.card,
    padding: spacing.sm,
    marginBottom: spacing.md,
    minHeight: 116,
    gap: spacing.md,
  },
  thumb: {
    width: 94,
    height: 100,
    borderRadius: 10,
    backgroundColor: colors.surface,
    overflow: 'hidden',
  },
  thumbTinted: { backgroundColor: colors.accentSoft },
  thumbImage: { width: '100%', height: '100%' },
  optionCopy: { flex: 1, paddingRight: spacing.sm },
  optionTitle: { ...type.bodyStory, fontWeight: '600', color: colors.ink, marginBottom: 4 },
  optionBody: { ...type.caption, color: colors.secondary, lineHeight: 18 },
});
