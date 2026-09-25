import React from 'react';
import { Text, Pressable, StyleSheet, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, spacing, radius } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<MemoryStackParamList, 'TopicsList'>;

export default function TopicsListScreen() {
  const navigation = useNavigation<Nav>();
  const topics = useAppStore((s) => s.topics);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <Pressable onPress={() => navigation.goBack()} style={styles.back}>
        <Text style={styles.backText}>‹</Text>
      </Pressable>
      <Text style={styles.title}>Your Topics</Text>
      <Text style={styles.sub}>Themes Diary One noticed in your memories.</Text>
      <ScrollView contentContainerStyle={styles.scroll}>
        {topics.map((t) => (
          <Pressable
            key={t.id}
            style={styles.row}
            onPress={() => navigation.navigate('TopicDetail', { topicId: t.id })}
          >
            <Text style={styles.rowTitle}>{t.name}</Text>
            <Text style={styles.chevron}>›</Text>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  back: { paddingHorizontal: layout.gutterDiary, minHeight: layout.minTouch, justifyContent: 'center' },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300' },
  title: {
    fontSize: font.title,
    fontWeight: '700',
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
  },
  sub: {
    fontSize: font.small,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.xs,
    marginBottom: spacing.md,
  },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: layout.minTouch,
    paddingVertical: spacing.sm,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  rowTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  chevron: { fontSize: font.body, color: colors.tertiary },
});
