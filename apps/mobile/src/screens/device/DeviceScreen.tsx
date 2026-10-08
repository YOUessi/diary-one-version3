import React from 'react';
import { View, Text, Pressable, StyleSheet, Alert, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaScreenHeader, FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { DeviceHeroMark } from '../../components/DeviceHeroMark';
import { colors, spacing, radius, layout, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { PipelineTaskList } from '../../components/PipelineTaskList';
import { BackendConnectivityCard } from '../../components/BackendConnectivityCard';
import { showInternalLabTools } from '../../config/buildProfile';
import { ResearchApiSettings } from './ResearchApiSettings';
import { performDeviceSync } from '../../device/deviceSync';
import type { DeviceStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<DeviceStackParamList, 'DeviceHome'>;

function DeviceMetricRow({
  label,
  value,
  last,
  mutedLabel,
}: {
  label: string;
  value: string;
  last?: boolean;
  mutedLabel?: boolean;
}) {
  return (
    <View style={[styles.metricRow, last && styles.metricRowLast]}>
      <Text style={[styles.metricLabel, mutedLabel && styles.metricLabelMuted]}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

function formatLastSynced(iso: string | null): string {
  if (!iso) return 'Unavailable';
  const dt = new Date(iso);
  const today = new Date();
  const sameDay =
    dt.getFullYear() === today.getFullYear()
    && dt.getMonth() === today.getMonth()
    && dt.getDate() === today.getDate();
  const time = dt.toLocaleString('en-US', { hour: 'numeric', minute: '2-digit' });
  if (sameDay) return `Today, ${time}`;
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
  const linked = deviceLinkState === 'lab_linked' || deviceLinkState === 'hardware_linked';
  const deviceBatteryPercent = useAppStore((s) => s.deviceBatteryPercent);
  const captureLabel = automaticCaptureMode === 'high' ? 'High frequency' : 'Standard';

  const onSync = () => {
    void performDeviceSync();
  };

  const statusRight = !linked
    ? 'Unavailable'
    : deviceBatteryPercent != null
      ? `${deviceBatteryPercent}% battery`
      : 'Battery level unavailable';

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.gutter}>
        <FigmaScreenHeader title="Device" />
      </View>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {showInternalLabTools ? <BackendConnectivityCard /> : null}

        <DeviceHeroMark connected={linked} />

        <View style={styles.statusRow}>
          <Text style={styles.statusTitle}>{linked ? 'Connected' : 'Not connected'}</Text>
          <Text style={styles.statusRight}>{statusRight}</Text>
        </View>

        <Text style={styles.sectionLabel}>On Device</Text>
        <View style={styles.metrics}>
          <DeviceMetricRow label="Storage" value={linked ? 'Available' : 'Unavailable'} mutedLabel />
          <DeviceMetricRow
            label="New recordings"
            value={linked ? (devicePendingRecordings ? 'Yes' : 'None') : 'Unavailable'}
            mutedLabel
          />
          <DeviceMetricRow
            label="Ready to sync"
            value={linked ? (devicePendingRecordings ? 'Ready' : 'Up to date') : 'Unavailable'}
            mutedLabel
          />
          <DeviceMetricRow
            label="Last synced"
            value={linked ? formatLastSynced(lastSyncedAt) : 'Unavailable'}
            mutedLabel
            last
          />
        </View>

        <Pressable
          style={[styles.syncBtn, !linked && styles.syncBtnDisabled]}
          onPress={onSync}
          disabled={!linked}
          accessibilityRole="button"
          accessibilityLabel="Sync"
        >
          <Text style={[styles.syncLabel, !linked && styles.syncLabelDisabled]}>Sync</Text>
        </Pressable>

        <Pressable
          style={styles.navBlock}
          onPress={linked ? () => navigation.navigate('AutomaticCapture') : undefined}
          disabled={!linked}
        >
          <View style={styles.navCopy}>
            <Text style={[styles.navTitle, !linked && styles.navTitleMuted]}>Automatic Capture</Text>
            <Text style={styles.navSub}>{linked ? captureLabel : 'Unavailable'}</Text>
          </View>
          <Text style={styles.navChevron}>›</Text>
        </Pressable>

        <Pressable style={styles.navBlock} onPress={() => navigation.navigate('DeviceSettings')}>
          <Text style={linked ? styles.navTitle : styles.navTitleMuted}>Device Settings</Text>
          <Text style={styles.navChevron}>›</Text>
        </Pressable>

        {showInternalLabTools ? (
          <>
            <FigmaEyebrow>Cloud processing (Expo Go)</FigmaEyebrow>
            <Text style={styles.pipelineLead}>
              Use Production BFF Dev Lite (:8790) for Demo → Diary. Device Sync is separate and stays
              Unavailable while headphones are not connected.
            </Text>
            <Pressable
              onPress={() => {
                const parent = navigation.getParent();
                parent?.navigate('AccountTab', { screen: 'InternalLab' });
              }}
              style={styles.pipelineBtn}
            >
              <Text style={styles.pipelineBtnText}>Open Evidence pipeline lab</Text>
            </Pressable>
            <Pressable
              onPress={() => {
                void import('../../config/applyDevCloudDefaults').then((m) => {
                  m.applyDevCloudDefaults();
                  m.ensureDevCloudConsentForLab();
                  Alert.alert('BFF defaults applied', 'Then open Lab → Ping → Demo photo.');
                });
              }}
              style={styles.pipelineBtn}
            >
              <Text style={styles.pipelineBtnText}>Apply .env BFF + cloud consent</Text>
            </Pressable>
            <Pressable
              onPress={() => {
                void import('../../pipeline/launchEvidenceImport').then((m) =>
                  m.launchDemoEvidenceImport(),
                );
              }}
              style={styles.pipelineBtn}
            >
              <Text style={styles.pipelineBtnText}>A · Demo photo → cloud → Diary</Text>
            </Pressable>
            <Pressable
              onPress={() => {
                void import('../../pipeline/launchEvidenceImport').then((m) => m.launchEvidenceImport());
              }}
              style={styles.pipelineBtn}
            >
              <Text style={styles.pipelineBtnText}>B · Import from photo library</Text>
            </Pressable>
            <PipelineTaskList tasks={pipelineTasks} />
            <FigmaEyebrow>Research API (optional)</FigmaEyebrow>
            <ResearchApiSettings />
          </>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  gutter: { paddingHorizontal: layout.gutterDiary },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: layout.tabBarHeight + spacing.xxxl,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
  },
  statusTitle: { ...type.titleChapter, color: colors.ink },
  statusRight: { ...type.caption, color: colors.secondary },
  sectionLabel: {
    ...type.titleChapter,
    color: colors.ink,
    marginBottom: spacing.sm,
  },
  metrics: { marginBottom: spacing.md },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    minHeight: 44,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  metricRowLast: { borderBottomWidth: 0 },
  metricLabel: { ...type.bodyStory, color: colors.ink },
  metricLabelMuted: { color: colors.secondary },
  metricValue: { ...type.captionEmphasis, fontWeight: '700', color: colors.ink },
  /** Figma 44:1347 — Sync 48×r12 */
  syncBtn: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xl,
  },
  syncBtnDisabled: { backgroundColor: '#B5B5B5' },
  syncLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.paper },
  syncLabelDisabled: { color: colors.card },
  navBlock: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: layout.minTouch,
    paddingVertical: spacing.sm,
    marginBottom: spacing.xs,
  },
  navCopy: { flex: 1 },
  navTitle: { ...type.bodyStory, color: colors.ink },
  navTitleMuted: { ...type.bodyStory, color: colors.secondary },
  navSub: { ...type.caption, color: colors.tertiary, marginTop: 2 },
  navChevron: { fontSize: 22, color: colors.tertiary, fontWeight: '300' },
  pipelineLead: {
    ...type.caption,
    color: colors.secondary,
    marginBottom: spacing.md,
    lineHeight: 20,
  },
  pipelineBtn: {
    backgroundColor: colors.surface,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.divider,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  pipelineBtnText: { ...type.bodyStory, fontWeight: '600', color: colors.ink },
});
