import React, { useState } from 'react';
import { Text, Pressable, StyleSheet, ScrollView, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { SettingsRow } from '../../components/SettingsRow';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { LanguagePreference, MemoryLanguagePreference } from '../../domain/appSettings';
import { languageDisplayLabel, memoryLanguageDisplayLabel } from '../../domain/appSettings';

const APP_OPTIONS: LanguagePreference[] = ['en', 'zh-Hans', 'system'];

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

        <View style={styles.card}>
          <SettingsRow
            label="App Language"
            value={languageDisplayLabel(language)}
            onPress={() => setPickingApp((v) => !v)}
          />
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

          <SettingsRow
            label="Memory Language"
            value={memoryLanguageDisplayLabel(memoryLanguage)}
            onPress={() => setPickingMemory((v) => !v)}
          />
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
        </View>

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
  title: { fontSize: 28, fontWeight: '600', color: colors.ink, marginBottom: spacing.md },
  card: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    paddingHorizontal: spacing.md,
  },
  picker: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, paddingBottom: spacing.md },
  pill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  pillOn: { borderColor: colors.ink, backgroundColor: colors.surface },
  pillText: { fontSize: font.small, color: colors.ink },
  footer: { fontSize: font.micro, color: colors.tertiary, lineHeight: 18, marginTop: spacing.md },
});
