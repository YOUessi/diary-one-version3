import React from 'react';
import { Text, Pressable, StyleSheet, View, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, font, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AccountStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<AccountStackParamList, 'MemoryPreferences'>;

export default function MemoryPreferencesScreen() {
  const navigation = useNavigation<Nav>();
  const preferences = useAppStore((s) => s.preferences);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>Memory Preferences</Text>
        <Text style={styles.lead}>
          Tell Diary One what matters to you. These preferences guide what may be worth remembering, but they are not hard rules.
        </Text>

        {preferences.map((p) => (
          <View key={p.id} style={styles.card}>
            <Text style={styles.cardTitle}>{p.title}</Text>
            <Text style={styles.cardBody}>{p.text}</Text>
            <View style={styles.cardActions}>
              <Pressable onPress={() => navigation.navigate('PreferenceEdit', { preferenceId: p.id })}>
                <Text style={styles.action}>Edit</Text>
              </Pressable>
              <Pressable onPress={() => navigation.navigate('PreferenceDeleteConfirm', { preferenceId: p.id })}>
                <Text style={styles.action}>Delete</Text>
              </Pressable>
            </View>
          </View>
        ))}

        <Pressable style={styles.addRow} onPress={() => navigation.navigate('PreferenceAdd')}>
          <Text style={styles.addPlus}>+</Text>
          <Text style={styles.addLabel}>Add what matters to you</Text>
        </Pressable>

        <Text style={styles.footer}>
          Preferences may change how Diary One prioritizes memories. They do not force every matching event to become a memory.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  title: { fontSize: 28, fontWeight: '600', color: colors.ink, marginBottom: spacing.sm },
  lead: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginBottom: spacing.lg },
  card: { marginBottom: spacing.lg },
  cardTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink, marginBottom: 4 },
  cardBody: { fontSize: font.body, color: colors.secondary, lineHeight: 22 },
  cardActions: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.sm },
  action: { fontSize: font.small, color: colors.accent, fontWeight: '600' },
  addRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginVertical: spacing.md },
  addPlus: { fontSize: 22, color: colors.ink, fontWeight: '300' },
  addLabel: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  footer: { fontSize: font.micro, color: colors.tertiary, lineHeight: 18 },
});
