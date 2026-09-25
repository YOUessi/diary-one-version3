import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, font, radius, spacing } from '../theme';
import type { CloudProcessingTarget } from '../backend/types';
import { useAppStore } from '../store/useAppStore';

const OPTIONS: { id: CloudProcessingTarget; label: string; hint: string }[] = [
  { id: 'research', label: 'Research (X02)', hint: 'PC handoff server on LAN' },
  { id: 'production', label: 'Production BFF', hint: 'Future /v1/day-revisions + jobs' },
];

export function CloudProcessingTargetPicker() {
  const target = useAppStore((s) => s.cloudProcessingTarget);
  const setCloudProcessingTarget = useAppStore((s) => s.setCloudProcessingTarget);

  return (
    <View style={styles.wrap}>
      <Text style={styles.label}>Cloud processing target</Text>
      <View style={styles.row}>
        {OPTIONS.map((opt) => {
          const on = target === opt.id;
          return (
            <Pressable
              key={opt.id}
              onPress={() => setCloudProcessingTarget(opt.id)}
              style={[styles.chip, on && styles.chipOn]}
            >
              <Text style={[styles.chipTitle, on && styles.chipTitleOn]}>{opt.label}</Text>
              <Text style={[styles.chipHint, on && styles.chipHintOn]}>{opt.hint}</Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { marginBottom: spacing.md },
  label: { fontSize: font.small, fontWeight: '600', color: colors.ink, marginBottom: spacing.xs },
  row: { flexDirection: 'row', gap: spacing.sm },
  chip: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.sm,
  },
  chipOn: { backgroundColor: colors.ink, borderColor: colors.ink },
  chipTitle: { fontSize: font.small, fontWeight: '700', color: colors.ink },
  chipTitleOn: { color: colors.paper },
  chipHint: { fontSize: font.micro, color: colors.tertiary, marginTop: 4, lineHeight: 14 },
  chipHintOn: { color: 'rgba(255,255,255,0.75)' },
});
