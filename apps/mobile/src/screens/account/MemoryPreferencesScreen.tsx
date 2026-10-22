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

/** Figma 68:988 — white cards h120 r12; Edit/Delete gray gap18; + Add row. */
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

        <View style={styles.cardStack}>
          {preferences.map((p) => (
            <View key={p.id} style={styles.card}>
              <Text style={styles.cardTitle}>{p.title}</Text>
              <Text style={styles.cardBody}>{p.text}</Text>
              <View style={styles.cardActions}>
                <Pressable
                  onPress={() => navigation.navigate('PreferenceEdit', { preferenceId: p.id })}
                  style={styles.actionHit}
                  hitSlop={4}
                >
                  <Text style={styles.action}>Edit</Text>
                </Pressable>
                <Pressable
                  onPress={() =>
                    navigation.navigate('PreferenceDeleteConfirm', { preferenceId: p.id })
                  }
                  style={styles.actionHit}
                  hitSlop={4}
                >
                  <Text style={styles.action}>Delete</Text>
                </Pressable>
              </View>
            </View>
          ))}
        </View>

        <Pressable style={styles.addRow} onPress={() => navigation.navigate('PreferenceAdd')}>
          <Text style={styles.addPlus}>+</Text>
          <Text style={styles.addLabel}>Add what matters to you</Text>
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
  title: { ...type.titleLarge, color: colors.ink, marginBottom: 22 },
  lead: { ...type.bodyStory, color: colors.secondary, marginBottom: 22 },
  cardStack: { gap: 12, marginBottom: 22 },
  /** Figma — pt14 pb12 px16 · gap8 · h120 */
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    paddingTop: 14,
    paddingBottom: 12,
    paddingHorizontal: 16,
    minHeight: 120,
    gap: 8,
  },
  cardTitle: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.ink },
  cardBody: { fontSize: 13, lineHeight: 18, color: colors.secondary },
  cardActions: { flexDirection: 'row', gap: 18, alignItems: 'center' },
  actionHit: { minHeight: 44, minWidth: 48, justifyContent: 'center' },
  action: { fontSize: 13, lineHeight: 18, color: colors.secondary, fontWeight: '500' },
  addRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    minHeight: 48,
    marginBottom: 22,
  },
  addPlus: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    letterSpacing: -0.1,
    color: colors.ink,
    width: 20,
  },
  addLabel: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.ink },
  footer: { fontSize: 13, lineHeight: 18, color: colors.tertiary },
});
