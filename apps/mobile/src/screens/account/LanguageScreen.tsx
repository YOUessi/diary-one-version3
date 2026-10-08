import React, { useState } from 'react';
import { Text, Pressable, StyleSheet, ScrollView, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { LanguagePreference, MemoryLanguagePreference } from '../../domain/appSettings';
import { languageDisplayLabel, memoryLanguageDisplayLabel } from '../../domain/appSettings';

const APP_OPTIONS: LanguagePreference[] = ['en', 'zh-Hans', 'system'];

/** Figma 71:1050 — flat rows, no bordered card. */
export default function LanguageScreen() {
  const language = useAppStore((s) => s.language);
  const memoryLanguage = useAppStore((s) => s.memoryLanguage);
  const setLanguage = useAppStore((s) => s.setLanguage);
  const setMemoryLanguage = useAppStore((s) => s.setMemoryLanguage);
  const [pickingApp, setPickingApp] = useState(false);
  const [pickingMemory, setPickingMemory] = useState(false);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>Language</Text>

        <Pressable style={styles.row} onPress={() => setPickingApp((v) => !v)}>
          <Text style={styles.rowLabel}>App Language</Text>
          <View style={styles.trailing}>
            <Text style={styles.rowValue}>{languageDisplayLabel(language)}</Text>
            <Text style={styles.chevron}>›</Text>
          </View>
        </Pressable>
        {pickingApp ? (
          <View style={styles.picker}>
            {APP_OPTIONS.map((code) => (
              <Pressable
                key={code}
                onPress={() => {
                  setLanguage(code);
                  setPickingApp(false);
                }}
                style={[styles.pill, language === code && styles.pillOn]}
              >
                <Text style={styles.pillText}>{languageDisplayLabel(code)}</Text>
              </Pressable>
            ))}
          </View>
        ) : null}

        <Pressable style={styles.row} onPress={() => setPickingMemory((v) => !v)}>
          <Text style={styles.rowLabel}>Memory Language</Text>
          <View style={styles.trailing}>
            <Text style={styles.rowValue}>{memoryLanguageDisplayLabel(memoryLanguage)}</Text>
            <Text style={styles.chevron}>›</Text>
          </View>
        </Pressable>
        {pickingMemory ? (
          <View style={styles.picker}>
            {(['same_as_app', 'en', 'zh-Hans'] as MemoryLanguagePreference[]).map((code) => (
              <Pressable
                key={code}
                onPress={() => {
                  setMemoryLanguage(code);
                  setPickingMemory(false);
                }}
                style={[styles.pill, memoryLanguage === code && styles.pillOn]}
              >
                <Text style={styles.pillText}>{memoryLanguageDisplayLabel(code)}</Text>
              </Pressable>
            ))}
          </View>
        ) : null}

        <Text style={styles.footer}>
          Memory titles and AI Story text follow your selected memory language.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  /** Figma 71:1050 — title 28; rows h54; accessory gap 6 */
  title: { ...type.titleSection, color: colors.ink, marginBottom: spacing.xxxl },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 54,
    marginBottom: spacing.md,
  },
  rowLabel: { ...type.bodyStory, color: colors.ink },
  trailing: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  rowValue: { fontSize: 13, lineHeight: 18, fontWeight: '500', color: colors.secondary },
  chevron: { fontSize: 17, color: colors.secondary, fontWeight: '300' },
  picker: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    paddingBottom: spacing.md,
  },
  /** Lab/local picker — not a Figma frame; keep compact chips */
  pill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  pillOn: { backgroundColor: colors.accentSoft },
  pillText: { ...type.captionEmphasis, color: colors.ink },
  footer: { ...type.caption, color: colors.tertiary, lineHeight: 18, marginTop: spacing.xl },
});
