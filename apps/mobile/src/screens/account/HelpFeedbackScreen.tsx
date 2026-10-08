import React, { useMemo, useState } from 'react';
import { Text, StyleSheet, ScrollView, View, TextInput } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { SettingsRow } from '../../components/SettingsRow';
import { colors, font, layout, radius, spacing, type } from '../../theme';
import type { AccountStackParamList, HelpTopicId } from '../../navigation/types';
import { HELP_TOPICS } from './helpContent';

type Nav = NativeStackNavigationProp<AccountStackParamList, 'HelpFeedback'>;

const BROWSE: HelpTopicId[] = ['pairing', 'sync', 'capture', 'memories', 'battery'];
const SUPPORT: HelpTopicId[] = ['report', 'feedback', 'device_basics', 'contact'];

export default function HelpFeedbackScreen() {
  const navigation = useNavigation<Nav>();
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return null;
    return HELP_TOPICS.filter(
      (t) => t.title.toLowerCase().includes(q) || t.body.toLowerCase().includes(q),
    );
  }, [query]);

  const open = (id: HelpTopicId) => navigation.navigate('HelpTopic', { topicId: id });

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Help & Feedback</Text>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Search Help"
          placeholderTextColor={colors.tertiary}
          style={styles.search}
        />

        {filtered ? (
          <View style={styles.card}>
            {filtered.length === 0 ? (
              <Text style={styles.empty}>No help articles match your search.</Text>
            ) : (
              filtered.map((t) => (
                <SettingsRow key={t.id} label={t.title} onPress={() => open(t.id)} />
              ))
            )}
          </View>
        ) : (
          <>
            <View style={styles.card}>
              {BROWSE.map((id) => {
                const t = HELP_TOPICS.find((x) => x.id === id)!;
                return <SettingsRow key={id} label={t.title} onPress={() => open(id)} />;
              })}
            </View>

            <FigmaEyebrow>SUPPORT</FigmaEyebrow>
            <View style={styles.card}>
              {SUPPORT.map((id) => {
                const t = HELP_TOPICS.find((x) => x.id === id)!;
                return <SettingsRow key={id} label={t.title} onPress={() => open(id)} />;
              })}
            </View>

            <Text style={styles.footer}>
              Report a Problem may include app/iOS version, firmware, device ID, connection/storage state and error logs only with your opt-in. User media and your added memory details are never attached automatically.
            </Text>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingBottom: spacing.xl },
  title: {
    ...type.titleLarge,
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
  /** Figma 127:1139 — search h48 r12; FAQ rows ~50 */
  search: {
    marginHorizontal: layout.gutterDiary,
    backgroundColor: colors.surface,
    borderRadius: 12,
    minHeight: 48,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    ...type.bodyStory,
    color: colors.ink,
    marginBottom: spacing.lg,
  },
  card: {
    marginHorizontal: layout.gutterDiary,
    paddingHorizontal: 0,
    marginBottom: spacing.sm,
    minHeight: 50,
    justifyContent: 'center',
  },
  empty: { fontSize: font.small, color: colors.secondary, paddingVertical: spacing.md },
  footer: {
    fontSize: font.micro,
    color: colors.tertiary,
    lineHeight: 18,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.md,
  },
});
