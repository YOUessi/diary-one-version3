import React from 'react';
import { Text, Pressable, StyleSheet, Alert, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AutomaticCaptureMode } from '../../domain/appSettings';
import { applyAutomaticCaptureToDevice } from '../../device/automaticCaptureScheduler';

const OPTIONS: { mode: AutomaticCaptureMode; title: string; subtitle: string }[] = [
  { mode: 'standard', title: 'Standard', subtitle: 'Capture every 2 min 9 sec' },
  { mode: 'high', title: 'High frequency', subtitle: 'Capture every 1 min 9 sec' },
];

/** Figma 69:1000 — left radio, white cards, footer disclaimer. */
export default function AutomaticCaptureScreen() {
  const link = useAppStore((s) => s.deviceLinkState);
  const linked = link === 'lab_linked' || link === 'hardware_linked';
  const mode = useAppStore((s) => s.automaticCaptureMode);
  const setAutomaticCaptureMode = useAppStore((s) => s.setAutomaticCaptureMode);

  const onSelect = async (next: AutomaticCaptureMode) => {
    setAutomaticCaptureMode(next);
    const result = await applyAutomaticCaptureToDevice();
    if (!result.ok) {
      Alert.alert('Saved on phone', result.message);
    } else if (link === 'lab_linked') {
      Alert.alert('Preference saved', result.message);
    }
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <Text style={styles.title}>Automatic Capture</Text>
      <Text style={styles.lead}>Choose how often Diary One captures in the background.</Text>

      {OPTIONS.map((opt) => {
        const selected = mode === opt.mode;
        const disabled = !linked;
        return (
          <Pressable
            key={opt.mode}
            disabled={disabled}
            onPress={() => void onSelect(opt.mode)}
            style={[styles.option, selected && styles.optionOn, disabled && styles.optionDisabled]}
            accessibilityRole="radio"
            accessibilityState={{ selected, disabled }}
          >
            <View style={styles.optionCopy}>
              <Text style={styles.optionTitle}>{opt.title}</Text>
              <Text style={styles.optionSub}>{opt.subtitle}</Text>
            </View>
            {selected ? <Text style={styles.check}>✓</Text> : null}
          </Pressable>
        );
      })}

      <Text style={styles.footer}>
        This changes capture frequency only. Memories and small memories are still created later from
        the synced material.
      </Text>

      {!linked ? (
        <Text style={styles.unavailable}>Connect Diary One to change automatic capture.</Text>
      ) : null}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  /** Figma 69:1000 — page title 28/590 */
  title: {
    ...type.titleSection,
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  lead: {
    ...type.bodyStory,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.xl,
  },
  option: {
    marginHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    minHeight: 76,
    borderRadius: 12,
    backgroundColor: colors.card,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  optionOn: {
    borderColor: colors.ink,
  },
  optionDisabled: { opacity: 0.45 },
  optionCopy: { flex: 1 },
  optionTitle: { ...type.bodyStory, fontWeight: '500', color: colors.ink },
  optionSub: { ...type.caption, color: colors.secondary, marginTop: 3 },
  check: { ...type.titleChapter, color: colors.ink, fontWeight: '600', lineHeight: 28 },
  footer: {
    ...type.caption,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.md,
    lineHeight: 20,
  },
  unavailable: {
    marginTop: spacing.lg,
    paddingHorizontal: layout.gutterDiary,
    ...type.caption,
    color: colors.tertiary,
  },
});
