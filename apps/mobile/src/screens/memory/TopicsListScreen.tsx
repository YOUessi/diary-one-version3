import React from 'react';
import { Text, Pressable, StyleSheet, ScrollView, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<MemoryStackParamList, 'TopicsList'>;

/** Figma 67:936 — 2-col covers 171×82 r12 + label 17 under. */
export default function TopicsListScreen() {
  const navigation = useNavigation<Nav>();
  const topics = useAppStore((s) => s.topics);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <Text style={styles.title}>Your Topics</Text>
      <Text style={styles.sub}>Themes Diary One noticed in your memories.</Text>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.grid}>
          {topics.map((t) => (
            <Pressable
              key={t.id}
              style={styles.card}
              onPress={() => navigation.navigate('TopicDetail', { topicId: t.id })}
            >
              <View style={styles.cover}>
                <View style={styles.coverOrb} />
                <View style={styles.coverWave} />
              </View>
              <Text style={styles.cardTitle}>{t.name}</Text>
            </Pressable>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  title: {
    ...type.titleSection,
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
  },
  sub: {
    ...type.caption,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.xs,
    marginBottom: spacing.xl,
  },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', rowGap: spacing.md },
  card: { width: '48%' },
  cover: {
    width: '100%',
    aspectRatio: 171 / 82,
    borderRadius: 12,
    backgroundColor: colors.surface,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  coverOrb: {
    position: 'absolute',
    top: '16%',
    right: '16%',
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.accentSoft,
  },
  coverWave: {
    position: 'absolute',
    left: '-10%',
    right: '-10%',
    bottom: -18,
    height: 40,
    borderRadius: 999,
    backgroundColor: colors.card,
    opacity: 0.85,
  },
  cardTitle: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.ink },
});
