import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import type { TodayStatus } from '../model';
import { showInternalLabTools } from '../config/buildProfile';
import { colors, font, radius, spacing } from '../theme';

const ORDER: TodayStatus[] = [
  'READY',
  'UNSYNCED',
  'PREPARING',
  'READY_NEW_RECORDINGS',
  'READY_PREPARING',
  'ZERO_CURATED',
  'NO_RECORDINGS',
  'PARTIAL',
];

export function TodayStatusDevPicker({
  status,
  onChange,
}: {
  status: TodayStatus;
  onChange: (s: TodayStatus) => void;
}) {
  if (!showInternalLabTools) return null;

  const idx = ORDER.indexOf(status);
  const next = ORDER[(idx + 1) % ORDER.length];

  return (
    <View style={styles.wrap}>
      <Text style={styles.label}>Dev · Today status</Text>
      <Pressable onPress={() => onChange(next)} style={styles.btn}>
        <Text style={styles.btnText}>{status} → tap to cycle</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    marginBottom: spacing.sm,
    padding: spacing.sm,
    borderRadius: radius.control,
    borderWidth: 1,
    borderColor: colors.divider,
    borderStyle: 'dashed',
  },
  label: { fontSize: font.micro, color: colors.tertiary, marginBottom: 4 },
  btn: { minHeight: 36, justifyContent: 'center' },
  btnText: { fontSize: font.small, color: colors.accent, fontWeight: '600' },
});
