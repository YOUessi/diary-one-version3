import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { listAssetLedger } from '../db/assetLedger';
import { colors, font, radius, spacing } from '../theme';

export function AssetLedgerList() {
  const entries = listAssetLedger();
  if (!entries.length) {
    return <Text style={styles.empty}>No bundle runs recorded yet.</Text>;
  }
  return (
    <View style={styles.wrap}>
      {entries.slice(0, 8).map((e) => (
        <View key={e.taskId} style={styles.row}>
          <Text style={styles.status}>{e.status}</Text>
          <Text style={styles.meta}>
            {e.dayKey} · {e.sourceCount} file(s)
            {e.bundleVersion ? ` · ${e.bundleVersion}` : ''}
          </Text>
          <Text style={styles.time}>{new Date(e.recordedAt).toLocaleString()}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: spacing.sm },
  empty: { fontSize: font.small, color: colors.tertiary },
  row: {
    backgroundColor: colors.card,
    borderRadius: radius.control,
    borderWidth: 1,
    borderColor: colors.divider,
    padding: spacing.md,
  },
  status: { fontSize: font.small, fontWeight: '600', color: colors.ink },
  meta: { fontSize: font.micro, color: colors.secondary, marginTop: 2 },
  time: { fontSize: font.micro, color: colors.tertiary, marginTop: 4 },
});
