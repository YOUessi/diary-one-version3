import React from 'react';
import { View, Text, Pressable, StyleSheet, Alert, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaScreenHeader, FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { colors, spacing, radius, font, layout } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { PipelineTaskList } from '../../components/PipelineTaskList';
import { BackendConnectivityCard } from '../../components/BackendConnectivityCard';
import { showInternalLabTools } from '../../config/buildProfile';
import { ResearchApiSettings } from './ResearchApiSettings';
import { performDeviceSync } from '../../device/deviceSync';
import type { DeviceStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<DeviceStackParamList, 'DeviceHome'>;

function DeviceMetricRow({ label, value, muted }: { label: string; value: string; muted?: boolean }) {
  return (
    <View style={styles.metricRow}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={[styles.metricValue, muted && styles.metricMuted]}>{value}</Text>
    </View>
  );
}

function NavRow({
  label,
  value,
  onPress,
  disabled,
}: {
  label: string;
  value?: string;
  onPress?: () => void;
  disabled?: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || !onPress}
      style={[styles.navRow, disabled && styles.navRowDisabled]}
    >
      <Text style={[styles.navLabel, disabled && styles.navLabelDisabled]}>{label}</Text>
      <Text style={styles.navTrailing}>
        {value ? `${value} ` : ''}
        ›
      </Text>
    </Pressable>
  );
}

function formatLastSynced(iso: string | null): string {
  if (!iso) return 'Unavailable';
  const dt = new Date(iso);
  return dt.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export default function DeviceHomeScreen() {
  const navigation = useNavigation<Nav>();
  const pipelineTasks = useAppStore((s) => s.pipelineTasks);
  const deviceLinkState = useAppStore((s) => s.deviceLinkState);
  const devicePendingRecordings = useAppStore((s) => s.devicePendingRecordings);
  const lastSyncedAt = useAppStore((s) => s.lastSyncedAt);
  const automaticCaptureMode = useAppStore((s) => s.automaticCaptureMode);
  const linked = deviceLinkState === 'lab_linked';
  const deviceBatteryPercent = useAppStore((s) => s.deviceBatteryPercent);
  const captureLabel =
    automaticCaptureMode === 'high' ? 'High frequency' : 'Standard';

  const onSync = () => {
    void performDeviceSync();
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaScreenHeader title="Device" />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {showInternalLabTools ? <BackendConnectivityCard /> : null}

        <View style={styles.statusCard}>
          <View style={styles.dotRow}>
            <View style={[styles.dot, linked && styles.dotOn]} />
            <Text style={styles.statusTitle}>{linked ? 'Connected' : 'Not connected'}</Text>
          </View>
          {linked ? (
            <Text style={styles.statusSub}>
              {deviceBatteryPercent != null
                ? `${deviceBatteryPercent}% battery`
                : 'Battery level unavailable'}
            </Text>
          ) : (
            <Text style={styles.statusSub}>Unavailable</Text>
          )}
        </View>

        <FigmaEyebrow>On Device</FigmaEyebrow>
        <View style={styles.card}>
          <DeviceMetricRow
            label="Storage"
            value={linked ? 'Available' : 'Unavailable'}
            muted={!linked}
          />
          <DeviceMetricRow
            label="New recordings"
            value={linked ? (devicePendingRecordings ? 'Yes' : 'None') : 'Unavailable'}
            muted={!linked}
          />
          <DeviceMetricRow
            label="Ready to sync"
            value={linked ? (devicePendingRecordings ? 'Ready' : 'Up to date') : 'Unavailable'}
            muted={!linked}
          />
          <DeviceMetricRow
            label="Last synced"
            value={linked ? formatLastSynced(lastSyncedAt) : 'Unavailable'}
            muted={!linked}
          />
          <Pressable
            style={[styles.syncBtn, !linked && styles.syncBtnDisabled]}
            onPress={onSync}
            disabled={!linked}
          >
            <Text style={[styles.syncLabel, !linked && styles.syncLabelDisabled]}>Sync</Text>
          </Pressable>
        </View>

        <FigmaEyebrow>Automatic Capture</FigmaEyebrow>
        <View style={styles.card}>
          <NavRow
            label="Automatic Capture"
            value={linked ? captureLabel : 'Unavailable'}
            onPress={linked ? () => navigation.navigate('AutomaticCapture') : undefined}
            disabled={!linked}
          />
        </View>

        <FigmaEyebrow>Device Settings</FigmaEyebrow>
        <View style={styles.card}>
          <NavRow label="Device Settings" onPress={() => navigation.navigate('DeviceSettings')} />
        </View>

        {showInternalLabTools ? (
          <>
            <FigmaEyebrow>Research & cloud preview</FigmaEyebrow>
            <ResearchApiSettings />
            <Text style={styles.pipelineLead}>
              Builds App Library Bundle V04 (default) on this phone and calls your research X02 preview when URL
              is set. Does not enter Captured by You and does not replace device sync.
            </Text>
            <Pressable
              onPress={() => {
                void import('../../pipeline/launchEvidenceImport').then((m) => m.launchEvidenceImport());
              }}
              style={styles.pipelineBtn}
            >
              <Text style={styles.pipelineBtnText}>Import from photo library (evidence test)</Text>
            </Pressable>
            <PipelineTaskList tasks={pipelineTasks} />
          </>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingBottom: spacing.xl },
  statusCard: {
    marginHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
    paddingVertical: spacing.sm,
  },
  dotRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  dot: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.tertiary },
  dotOn: { backgroundColor: colors.accent },
  statusTitle: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  statusSub: { fontSize: font.small, color: colors.secondary, marginTop: 2 },
  card: {
    marginHorizontal: layout.gutterDiary,
    backgroundColor: colors.card,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.divider,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    minHeight: layout.minTouch,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  metricLabel: { fontSize: font.body, color: colors.ink },
  metricValue: { fontSize: font.body, color: colors.secondary },
  metricMuted: { color: colors.tertiary },
  syncBtn: {
    margin: spacing.md,
    backgroundColor: colors.ink,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  syncBtnDisabled: { backgroundColor: colors.divider },
  syncLabel: { fontSize: font.body, fontWeight: '700', color: colors.paper },
  syncLabelDisabled: { color: colors.secondary },
  navRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    minHeight: layout.minTouch,
  },
  navRowDisabled: { opacity: 0.85 },
  navLabel: { fontSize: font.body, color: colors.ink },
  navLabelDisabled: { color: colors.secondary },
  navTrailing: { fontSize: font.body, color: colors.tertiary },
  pipelineLead: {
    fontSize: font.small,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
    lineHeight: 20,
  },
  pipelineBtn: {
    marginHorizontal: layout.gutterDiary,
    backgroundColor: colors.surface,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.divider,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  pipelineBtnText: { color: colors.ink, fontWeight: '600', fontSize: font.body },
});
