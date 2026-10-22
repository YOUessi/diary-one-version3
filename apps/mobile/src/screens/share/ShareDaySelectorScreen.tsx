import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { formatShortDay } from '../../domain/formatMedia';
import { colors, layout, spacing, type } from '../../theme';
import { chaptersForDate, useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';

type Route = RouteProp<DiaryStackParamList, 'ShareDaySelector'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ShareDaySelector'>;

/** Figma Share Day — same sheet language as Share Memory Selector (184:1976). */
export default function ShareDaySelectorScreen() {
  const { dateKey } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapters = useAppStore((s) => chaptersForDate(s.chapters, dateKey));

  const close = () => navigation.goBack();

  return (
    <View style={styles.root}>
      <Pressable style={styles.dim} onPress={close} accessibilityLabel="Dismiss share day" />
      <SafeAreaView edges={['bottom']} style={styles.sheet}>
        <View style={styles.handle} />
        <View style={styles.titleBlock}>
          <Text style={styles.sheetTitle}>Share day</Text>
          <Pressable onPress={close} hitSlop={12} style={styles.closeHit} accessibilityLabel="Close">
            <Text style={styles.close}>×</Text>
          </Pressable>
        </View>
        <Text style={styles.dateTitle}>{formatShortDay(dateKey)}</Text>
        <Text style={styles.meta}>
          {chapters.length} {chapters.length === 1 ? 'memory' : 'memories'} on this day
        </Text>

        <Pressable
          style={styles.option}
          onPress={() => navigation.replace('DailyRecapFlow', { dateKey, phase: 'preparing' })}
        >
          <View style={styles.optionCopy}>
            <Text style={styles.optionTitle}>Daily Recap</Text>
            <Text style={styles.optionBody}>A 9:16 video-style recap of your day.</Text>
          </View>
        </Pressable>
        <Pressable
          style={styles.option}
          onPress={() => navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'preparing' })}
        >
          <View style={styles.optionCopy}>
            <Text style={styles.optionTitle}>Photo collage</Text>
            <Text style={styles.optionBody}>A clean layout using moments from this day.</Text>
          </View>
        </Pressable>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'transparent' },
  dim: { ...StyleSheet.absoluteFill, backgroundColor: 'rgba(0,0,0,0.18)' },
  sheet: {
    backgroundColor: colors.card,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: 10,
    paddingBottom: spacing.lg,
  },
  handle: {
    alignSelf: 'center',
    width: 41,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.divider,
    marginBottom: 20,
  },
  titleBlock: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
    minHeight: 44,
  },
  sheetTitle: {
    ...type.titleSection,
    color: colors.ink,
    flex: 1,
    paddingRight: spacing.md,
  },
  closeHit: {
    position: 'absolute',
    right: -4,
    top: -18,
    width: layout.minTouch,
    height: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  close: { fontSize: 26, color: '#404040', fontWeight: '400', lineHeight: 32 },
  dateTitle: { ...type.titleChapter, color: colors.ink },
  meta: { ...type.caption, color: colors.tertiary, marginBottom: spacing.lg, marginTop: 2 },
  option: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: 14,
    backgroundColor: colors.paper,
    padding: 13,
    marginBottom: 14,
    minHeight: 88,
    justifyContent: 'center',
  },
  optionCopy: { paddingRight: spacing.sm },
  optionTitle: { fontSize: 17, lineHeight: 24, fontWeight: '600', color: colors.ink, marginBottom: 8 },
  optionBody: { fontSize: 13, lineHeight: 18, color: colors.secondary },
});
