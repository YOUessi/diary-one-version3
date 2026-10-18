import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { colors, font, radius, spacing, layout } from '../theme';
import { useAppStore } from '../store/useAppStore';
import { collectBackendHealth, type BackendHealth } from '../backend';

function line(label: string, value: string, ok?: boolean) {
  return (
    <View style={styles.line}>
      <Text style={styles.lineLabel}>{label}</Text>
      <Text style={[styles.lineValue, ok === true && styles.ok, ok === false && styles.bad]}>
        {value}
      </Text>
    </View>
  );
}

export function BackendConnectivityCard() {
  const cloudTarget = useAppStore((s) => s.cloudProcessingTarget);
  const [result, setResult] = useState<{ target: string; health: BackendHealth | null } | null>(null);
  const health = result?.target === cloudTarget ? result.health : null;
  const loading = result?.target !== cloudTarget;

  useEffect(() => {
    let active = true;
    void collectBackendHealth().then((value) => {
      if (active) setResult({ target: cloudTarget, health: value });
    }).catch(() => { if (active) setResult({ target: cloudTarget, health: null }); });
    return () => { active = false; };
  }, [cloudTarget]);

  return (
    <View style={styles.card}>
      <Text style={styles.title}>Services</Text>
      <Text style={styles.sub}>Honest status — no fake cloud or device data.</Text>
      {loading && !health ? (
        <ActivityIndicator color={colors.accent} style={{ marginTop: spacing.sm }} />
      ) : health ? (
        <>
          {line('Device', health.device.linked ? 'Lab linked' : 'Not connected', health.device.linked)}
          {line(
            'Cloud target',
            cloudTarget === 'production' ? 'Production BFF' : 'Research X02',
          )}
          {line(
            'Research API',
            health.research.configured
              ? health.research.reachable
                ? 'Reachable'
                : 'Configured · unreachable'
              : 'Not configured',
            health.research.configured ? health.research.reachable : undefined,
          )}
          {line(
            'Production API',
            health.production.configured
              ? health.production.reachable
                ? 'Reachable'
                : 'Configured · unreachable'
              : 'Not configured',
            health.production.configured ? health.production.reachable : undefined,
          )}
          {line(
            'Account',
            health.account.mode === 'email_verified'
              ? health.account.email ?? 'Email on device'
              : 'Local test profile',
          )}
        </>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
    padding: spacing.md,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.divider,
    backgroundColor: colors.card,
  },
  title: { fontSize: font.body, fontWeight: '700', color: colors.ink },
  sub: { fontSize: font.micro, color: colors.tertiary, marginTop: 2, marginBottom: spacing.sm },
  line: { flexDirection: 'row', justifyContent: 'space-between', gap: spacing.sm, marginTop: 6 },
  lineLabel: { fontSize: font.small, color: colors.secondary },
  lineValue: { fontSize: font.small, fontWeight: '600', color: colors.ink, flexShrink: 1, textAlign: 'right' },
  ok: { color: colors.accent },
  bad: { color: '#9B3B3B' },
});
