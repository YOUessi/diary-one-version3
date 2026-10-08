import React from 'react';
import { Text, Pressable, StyleSheet, View, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AccountStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<AccountStackParamList, 'MemoryPreferences'>;

/** Figma 68:988 — white 20pt cards, gray Edit/Delete, black + Add. */
export default function MemoryPreferencesScreen() {
  const navigation = useNavigation<Nav>();
  const preferences = useAppStore((s) => s.preferences);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>Memory Preferences</Text>
        <Text style={styles.lead}>
          Tell Diary One what matters to you. These preferences guide what may be worth remembering,
          but they are not hard rules.
        </Text>

        {preferences.map((p) => (
          <View key={p.id} style={styles.card}>
            <Text style={styles.cardTitle}>{p.title}</Text>
            <Text style={styles.cardBody}>{p.text}</Text>
            <View style={styles.cardActions}>
              <Pressable onPress={() => navigation.navigate('PreferenceEdit', { preferenceId: p.id })}>
                <Text style={styles.action}>Edit</Text>
              </Pressable>
              <Pressable
                onPress={() => navigation.navigate('PreferenceDeleteConfirm', { preferenceId: p.id })}
              >
                <Text style={styles.action}>Delete</Text>
              </Pressable>
            </View>
          </View>
        ))}

        <Pressable style={styles.addRow} onPress={() => navigation.navigate('PreferenceAdd')}>
          <Text style={styles.addLabel}>+ Add what matters to you</Text>
        </Pressable>

        <Text style={styles.footer}>
          Preferences may change how Diary One prioritizes memories. They do not force every matching
          event to become a memory.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  title: { ...type.titleLarge, color: colors.ink, marginBottom: spacing.sm },
  lead: { ...type.bodyStory, color: colors.secondary, marginBottom: spacing.xl },
  /** Figma 68:988 — preference cards h120 r12; Add row h48 */
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    minHeight: 120,
  },
  /** Figma 126 — card title 17; body 13; Edit/Delete gray */
  cardTitle: { fontSize: 17, lineHeight: 24, fontWeight: '600', color: colors.ink, marginBottom: spacing.sm },
  cardBody: { fontSize: 13, lineHeight: 18, color: colors.secondary },
  cardActions: { flexDirection: 'row', gap: spacing.xl, marginTop: spacing.md },
  action: { fontSize: 13, lineHeight: 18, color: colors.secondary, fontWeight: '500' },
  addRow: { minHeight: 48, justifyContent: 'center', marginTop: spacing.sm },
  addLabel: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.ink },
  footer: { fontSize: 13, lineHeight: 18, color: colors.tertiary, marginTop: spacing.xl },
});
