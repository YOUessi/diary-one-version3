import React from 'react';
import { Text, Pressable, StyleSheet, View, Switch, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, font, layout, spacing, radius } from '../../theme';
import { InfoRow } from '../../ui';
import { useAppStore } from '../../store/useAppStore';
import { showInternalLabTools } from '../../config/buildProfile';

function SettingsMetricRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metricRow}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

export default function DeviceSettingsScreen() {
  const deviceLinkState = useAppStore((s) => s.deviceLinkState);
  const setDeviceLinkState = useAppStore((s) => s.setDeviceLinkState);
  const linked = deviceLinkState === 'lab_linked';

  const toggleLab = (value: boolean) => {
    if (!value) {
      setDeviceLinkState('disconnected');
      return;
    }
    Alert.alert(
      'Lab device link',
      'Enables sync UI testing without BLE hardware. Does not show fake battery or storage meters.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Enable', onPress: () => setDeviceLinkState('lab_linked') },
      ],
    );
  };

  const onResetDevice = () => {
    Alert.alert(
      'Reset Device',
      linked
        ? 'Factory reset is available from Diary One hardware when supported by your firmware.'
        : 'Connect Diary One to access reset.',
    );
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <Text style={styles.title}>Device Settings</Text>
      <View style={styles.card}>
        <SettingsMetricRow label="Device Name" value={linked ? 'Diary One' : 'Unavailable'} />
        <SettingsMetricRow label="Firmware" value={linked ? '1.0.0' : 'Unavailable'} />
        <InfoRow label="Reset Device" onPress={onResetDevice} />
      </View>
      {showInternalLabTools ? (
        <>
          <View style={styles.labRow}>
            <Text style={styles.labLabel}>Internal lab link (no BLE)</Text>
            <Switch value={linked} onValueChange={toggleLab} />
          </View>
          {linked ? (
            <Pressable
              style={styles.unpairBtn}
              onPress={() => {
                Alert.alert('Unpair lab device?', 'Disconnects the internal lab link only.', [
                  { text: 'Cancel', style: 'cancel' },
                  {
                    text: 'Unpair',
                    style: 'destructive',
                    onPress: () => setDeviceLinkState('disconnected'),
                  },
                ]);
              }}
            >
              <Text style={styles.unpairText}>Unpair lab device</Text>
            </Pressable>
          ) : null}
        </>
      ) : null}
      <Text style={styles.note}>
        Sync, firmware upgrade, and factory reset are separate steps. Connect Diary One to change
        device settings.
      </Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: layout.gutterDiary },
  title: {
    fontSize: 28,
    fontWeight: '600',
    color: colors.ink,
    marginBottom: spacing.md,
    paddingHorizontal: 0,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.divider,
    paddingHorizontal: spacing.md,
  },
  metricRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: layout.minTouch,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  metricLabel: { fontSize: font.body, color: colors.ink },
  metricValue: { fontSize: font.body, color: colors.secondary },
  labRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.lg,
    minHeight: layout.minTouch,
  },
  labLabel: { fontSize: font.body, color: colors.ink, flex: 1, paddingRight: spacing.md },
  note: { fontSize: font.micro, color: colors.tertiary, marginTop: spacing.md, lineHeight: 18 },
  unpairBtn: {
    marginTop: spacing.lg,
    minHeight: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  unpairText: { fontSize: font.body, fontWeight: '600', color: colors.accent },
});
