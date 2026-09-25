import React from 'react';
import { Text, Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, font, layout, spacing, radius } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AutomaticCaptureMode } from '../../domain/appSettings';

const OPTIONS: { mode: AutomaticCaptureMode; title: string; subtitle: string }[] = [
  { mode: 'standard', title: 'Standard', subtitle: 'Capture every 2 min 9 sec' },
  { mode: 'high', title: 'High frequency', subtitle: 'Capture every 1 min 9 sec' },
];

export default function AutomaticCaptureScreen() {
  const linked = useAppStore((s) => s.deviceLinkState) === 'lab_linked';
  const mode = useAppStore((s) => s.automaticCaptureMode);
  const setAutomaticCaptureMode = useAppStore((s) => s.setAutomaticCaptureMode);

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
            onPress={() => setAutomaticCaptureMode(opt.mode)}
            style={[styles.option, selected && styles.optionOn, disabled && styles.optionDisabled]}
          >
            <Text style={styles.optionTitle}>{opt.title}</Text>
            <Text style={styles.optionSub}>{opt.subtitle}</Text>
            {selected ? <Text style={styles.check}>✓</Text> : null}
          </Pressable>
        );
      })}

      <Text style={styles.note}>
        This changes capture frequency only. Memories and small memories are still created later from the synced material.
      </Text>
      {!linked ? (
        <Text style={styles.unavailable}>Connect Diary One to change automatic capture.</Text>
      ) : null}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: layout.gutterDiary },
  title: { fontSize: 28, fontWeight: '600', color: colors.ink },
  lead: { fontSize: font.body, color: colors.secondary, marginVertical: spacing.md, lineHeight: 22 },
  option: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  optionOn: { borderColor: colors.ink, backgroundColor: colors.surface },
  optionDisabled: { opacity: 0.5 },
  optionTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  optionSub: { fontSize: font.small, color: colors.secondary, marginTop: 4 },
  check: { fontSize: font.micro, color: colors.accent, marginTop: spacing.xs, fontWeight: '600' },
  note: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginTop: spacing.lg },
  unavailable: { fontSize: font.small, color: colors.tertiary, marginTop: spacing.sm },
});
