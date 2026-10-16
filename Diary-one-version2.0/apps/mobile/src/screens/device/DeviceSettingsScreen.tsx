import React, { useState } from 'react';
import { Text, Pressable, StyleSheet, View, Switch, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { DiscardConfirmCard } from '../../components/DiscardConfirmCard';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { showInternalLabTools } from '../../config/buildProfile';

/** Figma 69:1020 — flat rows, no bordered card; Reset in secondary gray. */
export default function DeviceSettingsScreen() {
  const deviceLinkState = useAppStore((s) => s.deviceLinkState);
  const setDeviceLinkState = useAppStore((s) => s.setDeviceLinkState);
  const linked = deviceLinkState === 'lab_linked' || deviceLinkState === 'hardware_linked';
  const [unpairOpen, setUnpairOpen] = useState(false);

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

      <Pressable
        style={styles.row}
        onPress={() => {
          if (!linked) {
            Alert.alert('Unavailable', 'Connect Diary One to view device name.');
          }
        }}
      >
        <Text style={styles.rowLabel}>Device Name</Text>
        <View style={styles.rowTrailing}>
          <Text style={styles.rowValue}>{linked ? 'Diary One' : 'Unavailable'}</Text>
          <Text style={styles.chevron}>›</Text>
        </View>
      </Pressable>

      <View style={styles.row}>
        <Text style={styles.rowLabel}>Firmware</Text>
        <Text style={styles.rowValue}>{linked ? '1.0.0' : 'Unavailable'}</Text>
      </View>
      <View style={styles.divider} />

      <Pressable style={styles.resetRow} onPress={onResetDevice}>
        <Text style={styles.resetLabel}>Reset Device</Text>
      </Pressable>

      {showInternalLabTools ? (
        <>
          <View style={styles.labRow}>
            <Text style={styles.labLabel}>Internal lab link (no BLE)</Text>
            <Switch value={linked} onValueChange={toggleLab} />
          </View>
          {linked ? (
            <Pressable style={styles.unpairBtn} onPress={() => setUnpairOpen(true)}>
              <Text style={styles.unpairText}>Unpair lab device</Text>
            </Pressable>
          ) : null}
        </>
      ) : null}

      <DiscardConfirmCard
        visible={unpairOpen}
        title="Unpair lab device?"
        message="Disconnects the internal lab link only."
        keepLabel="Cancel"
        discardLabel="Unpair"
        onKeepEditing={() => setUnpairOpen(false)}
        onDiscard={() => {
          setUnpairOpen(false);
          setDeviceLinkState('disconnected');
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: layout.gutterDiary },
  /** Figma 69:1020 — title 28; rows h52 gap24; values 13 regular */
  title: {
    ...type.titleSection,
    color: colors.ink,
    marginBottom: 24,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 52,
    marginBottom: 24,
  },
  rowLabel: { ...type.bodyStory, fontWeight: '500', color: colors.ink },
  rowTrailing: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  rowValue: { fontSize: 13, lineHeight: 18, fontWeight: '400', color: colors.secondary },
  chevron: { fontSize: 17, color: colors.secondary, fontWeight: '500' },
  divider: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.divider,
    marginBottom: 24,
  },
  resetRow: { minHeight: 52, justifyContent: 'center' },
  resetLabel: { ...type.bodyStory, fontWeight: '500', color: colors.secondary },
  labRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.xl,
    minHeight: layout.minTouch,
  },
  labLabel: { ...type.bodyStory, color: colors.ink, flex: 1, paddingRight: spacing.md },
  unpairBtn: {
    marginTop: spacing.lg,
    minHeight: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  unpairText: { ...type.bodyStory, fontWeight: '600', color: colors.accent },
});
