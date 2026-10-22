import React from 'react';
import { appStrings, appLocale } from '../../domain/strings';
import {
  View,
  Text,
  Pressable,
  StyleSheet,
  Alert,
  ScrollView,
  Switch,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaScreenHeader } from '../../components/FigmaScreenHeader';
import { DeviceHeroMark } from '../../components/DeviceHeroMark';
import { colors, spacing, radius, layout, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { PipelineTaskList } from '../../components/PipelineTaskList';
import { performDeviceSync } from '../../device/deviceSync';
import type { DeviceStackParamList } from '../../navigation/types';
import { showInternalLabTools } from '../../config/buildProfile';
import { showImportFailure } from '../../pipeline/importFailure';

type Nav = NativeStackNavigationProp<DeviceStackParamList, 'DeviceHome'>;

function BatteryGlyph({ muted }: { muted?: boolean }) {
  const stroke = muted ? colors.secondary : colors.ink;
  return (
    <View style={styles.battGlyph} accessibilityElementsHidden>
      <View style={[styles.battOutline, { borderColor: stroke }]}>
        <View
          style={[
            styles.battFill,
            { backgroundColor: stroke, width: muted ? 10 : 16.5 },
          ]}
        />
      </View>
      <View style={[styles.battTip, { backgroundColor: stroke }]} />
    </View>
  );
}

/** Figma 44:1347 Connected · 269:2102 Disconnected — editorial Device home. */
export default function DeviceHomeScreen() {
  const navigation = useNavigation<Nav>();
  const language = useAppStore((s) => s.language);
  const strings = appStrings(language);
  const chinese = appLocale(language) === 'zh-CN';
  const pipelineTasks = useAppStore((s) => s.pipelineTasks);
  const deviceLinkState = useAppStore((s) => s.deviceLinkState);
  const devicePendingRecordings = useAppStore((s) => s.devicePendingRecordings);
  const lastSyncedAt = useAppStore((s) => s.lastSyncedAt);
  const setDeviceLinkState = useAppStore((s) => s.setDeviceLinkState);
  const deviceBatteryPercent = useAppStore((s) => s.deviceBatteryPercent);
  const linked =
    deviceLinkState === 'hardware_linked' || deviceLinkState === 'lab_linked';

  // Design samples are fixtures, never substitute for missing device telemetry.
  const batteryLabel = deviceBatteryPercent != null
    ? `${deviceBatteryPercent}%${linked ? '' : (chinese ? '（上次记录）' : ' last known')}`
    : strings.unavailable;
  const pendingSync = linked && devicePendingRecordings;
  const syncRight = !linked ? strings.unavailable : pendingSync ? strings.notUploaded :
    lastSyncedAt ? strings.upToDate : strings.unavailable;
  const syncSub = !linked ? strings.connectionHint : pendingSync
    ? strings.newRecordings
    : lastSyncedAt ? `${chinese ? '更新于 ' : 'Updated '}${formatRelative(lastSyncedAt, chinese)}` : strings.syncUnavailable;

  const onConnect = () => {
    Alert.alert(
      strings.deviceConnectionTitle, strings.hardwareUnavailable,
    );
  };

  const onImportPhotos = () => {
    void import('../../pipeline/launchEvidenceImport').then((m) =>
      m.launchEvidenceImportFromLibrary(),
    ).catch((error) => showImportFailure(error, 'START'));
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.gutter}>
        <FigmaScreenHeader title={strings.tabDevice} />
      </View>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Status card — Figma white r12 */}
        <View style={[styles.statusCard, !linked && styles.statusCardDisconnected]}>
          <DeviceHeroMark connected={linked} compact />
          <View style={styles.nameRow}>
            <Text style={styles.deviceName}>Diary One</Text>
            <View style={[styles.dot, linked ? styles.dotOn : styles.dotOff]} />
            <Text style={styles.linkLabel}>{deviceLinkState === 'lab_linked' ? strings.labConnected : linked ? strings.connected : strings.disconnected}</Text>
          </View>
          <View style={styles.cardDivider} />
          <View style={styles.cardRow}>
            <Text style={styles.cardRowLabel}>{strings.battery}</Text>
            <View style={styles.batteryTrailing}>
              {linked && deviceBatteryPercent != null ? <BatteryGlyph /> : null}
              <Text style={[styles.cardRowValue, !linked && styles.cardRowValueMuted]}>
                {batteryLabel}
              </Text>
            </View>
          </View>
          <View style={styles.cardDividerInset} />
          <View style={styles.cardRow}>
            <Text style={styles.cardRowTitle}>{strings.camera}</Text>
            <Text style={[styles.cardRowValue, !linked && styles.cardRowValueMuted]}>
              {strings.unavailable}
            </Text>
          </View>
          <View style={styles.cardDividerInset} />
          <View style={[styles.cardRow, styles.cardRowLast]}>
            <Text style={styles.cardRowTitle}>{strings.desktopMode}</Text>
            <Text style={[styles.cardRowValue, !linked && styles.cardRowValueMuted]}>{strings.unavailable}</Text>
          </View>
        </View>

        {!linked ? (
          <View style={styles.alertRow}>
            <View style={styles.alertMark} />
            <View style={styles.alertCopy}>
              <Text style={styles.alertTitle}>{strings.disconnected}</Text>
              <Text style={styles.alertSub}>{strings.connectionHint}</Text>
            </View>
            <Pressable style={styles.connectBtn} onPress={onConnect} accessibilityRole="button">
              <Text style={styles.connectLabel}>{strings.connect}</Text>
            </Pressable>
          </View>
        ) : null}

        {/* Hardware-free test path: local photos & videos → Evidence → cloud → Diary */}
        <View style={styles.uploadCard}>
          <Text style={styles.uploadEyebrow}>{strings.photosEntry}</Text>
          <Text style={styles.uploadTitle}>{strings.uploadMedia}</Text>
          <Text style={styles.uploadLead}>
            {strings.uploadLead}
          </Text>
          <Pressable
            style={styles.uploadBtn}
            onPress={onImportPhotos}
            accessibilityRole="button"
            accessibilityLabel={strings.uploadMedia}
          >
            <Text style={styles.uploadBtnLabel}>{strings.choosePhotos}</Text>
          </Pressable>
          <PipelineTaskList tasks={pipelineTasks} />
        </View>

        {/* Sync */}
        <View style={styles.sectionHead}>
          <Text style={styles.sectionTitle}>{strings.sync}</Text>
          <Text
            style={[
              styles.sectionRight,
              (!linked || pendingSync) && styles.sectionRightAccent,
            ]}
          >
            {syncRight}
          </Text>
        </View>
        <Text style={styles.sectionSub}>{syncSub}</Text>
        {pendingSync ? (
          <Pressable
            onPress={() => void performDeviceSync()}
            style={styles.syncNowBtn}
            accessibilityRole="button"
            accessibilityLabel={strings.syncNow}
          >
            <Text style={styles.syncNowLabel}>{strings.syncNow}</Text>
          </Pressable>
        ) : null}
        <View style={styles.hairline} />

        {/* Storage */}
        <View style={styles.sectionHead}>
          <Text style={styles.sectionTitle}>{strings.storage}</Text>
        </View>
        <View style={styles.storageRow}>
          <Text style={styles.storageLabel}>{strings.onDevice}</Text>
          <Text style={styles.storageValue}>{strings.unavailable}</Text>
        </View>
        <View style={[styles.storageRow, styles.storageRowNext]}>
          <Text style={styles.storageLabel}>{strings.cloud}</Text>
          <Text style={styles.storageValue}>{strings.unavailable}</Text>
        </View>
        <View style={styles.hairline} />

        {/* Automatic Capture */}
        <View style={styles.switchRow}>
          <Text style={styles.switchLabel}>{strings.automaticCapture}</Text>
          <Text style={styles.sectionRightMuted}>{strings.unavailable}</Text>
          <Switch
            value={false}
            disabled
            accessibilityLabel={`${strings.automaticCapture} · ${strings.unavailable}`}
            trackColor={{ false: '#C8C5BF', true: colors.ink }}
            thumbColor={colors.card}
            ios_backgroundColor="#C8C5BF"
          />
        </View>
        <View style={styles.hairline} />

        <Pressable style={styles.linkRow} onPress={() => navigation.navigate('DeviceSettings')}>
          <Text style={styles.linkRowLabel}>{strings.deviceSettings}</Text>
          <Text style={styles.linkChevron}>›</Text>
        </Pressable>
        <View style={styles.hairline} />
        <Pressable
          style={styles.linkRow}
          onPress={() =>
            Alert.alert(
              strings.howToUse, strings.guideHint,
            )
          }
        >
          <Text style={styles.linkRowLabel}>{strings.howToUse}</Text>
          <Text style={styles.linkChevron}>›</Text>
        </Pressable>

        {showInternalLabTools && linked ? (
          <Pressable
            style={styles.labDisconnect}
            onPress={() => setDeviceLinkState('disconnected')}
          >
            <Text style={styles.labDisconnectText}>Lab · Disconnect</Text>
          </Pressable>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function formatRelative(iso: string, chinese: boolean): string {
  const ms = Date.now() - new Date(iso).getTime();
  const min = Math.max(1, Math.round(ms / 60000));
  if (min < 60) return chinese ? `${min} 分钟前` : `${min} min ago`;
  return chinese ? `${Math.round(min / 60)} 小时前` : `${Math.round(min / 60)} h ago`;
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  gutter: { paddingHorizontal: layout.gutterDiary },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: layout.tabBarHeight + spacing.xxxl,
  },
  statusCard: {
    backgroundColor: colors.card,
    borderRadius: radius.card,
    paddingBottom: spacing.md,
    marginBottom: spacing.xl,
    overflow: 'hidden',
    minHeight: 263,
  },
  statusCardDisconnected: { minHeight: 236 },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    gap: 8,
    marginTop: 4,
  },
  deviceName: { ...type.titleChapter, color: colors.ink, flexShrink: 1 },
  dot: { width: 7, height: 7, borderRadius: 3.5 },
  dotOn: { backgroundColor: colors.ok },
  dotOff: { backgroundColor: colors.tertiary },
  linkLabel: {
    ...type.captionEmphasis,
    color: colors.secondary,
    marginLeft: 'auto',
    textAlign: 'right',
  },
  cardDivider: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.divider,
    marginHorizontal: spacing.md,
    marginTop: spacing.md,
  },
  cardDividerInset: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.divider,
    marginHorizontal: spacing.md,
  },
  cardRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    minHeight: 32,
    paddingVertical: 6,
  },
  cardRowLast: { paddingBottom: 4 },
  cardRowLabel: { fontSize: 15, lineHeight: 20, color: colors.secondary },
  cardRowTitle: { fontSize: 16, lineHeight: 22, color: colors.ink },
  cardRowValue: { fontSize: 15, lineHeight: 20, color: colors.secondary, fontWeight: '500' },
  cardRowValueMuted: { color: colors.tertiary, fontWeight: '400' },
  batteryTrailing: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  battGlyph: { flexDirection: 'row', alignItems: 'center', width: 36, height: 20 },
  battOutline: {
    width: 29,
    height: 16,
    borderRadius: 4,
    borderWidth: 1.5,
    padding: 2,
    justifyContent: 'center',
  },
  battFill: { height: 10, borderRadius: 2 },
  battTip: { width: 3, height: 6, borderRadius: 1, marginLeft: 1 },
  alertRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xl,
    minHeight: 48,
    gap: 10,
  },
  alertMark: {
    width: 3,
    height: 43,
    borderRadius: 1,
    backgroundColor: colors.accent,
  },
  alertCopy: { flex: 1 },
  alertTitle: { fontSize: 15, fontWeight: '600', color: colors.ink },
  alertSub: { fontSize: 12, color: colors.secondary, marginTop: 2 },
  connectBtn: {
    width: 85,
    height: 44,
    borderRadius: radius.control,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
  },
  connectLabel: { fontSize: 14, fontWeight: '500', color: colors.paper },
  sectionHead: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  sectionTitle: { fontSize: 20, fontWeight: '600', color: colors.ink },
  sectionRight: { fontSize: 14, fontWeight: '500', color: colors.ink },
  sectionRightMuted: { color: colors.secondary },
  sectionRightAccent: { color: colors.accent },
  sectionSub: { ...type.caption, color: colors.secondary, marginTop: 4, marginBottom: 8 },
  syncHit: { marginBottom: 4 },
  syncNowBtn: {
    height: 44,
    borderRadius: radius.control,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  syncNowLabel: { fontSize: 15, fontWeight: '500', color: colors.paper },
  track: {
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.divider,
    width: '100%',
    overflow: 'hidden',
    marginBottom: 8,
  },
  trackFill: { height: 4, borderRadius: 2 },
  hairline: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.divider,
    marginVertical: spacing.sm,
  },
  lastKnown: { fontSize: 11, color: colors.tertiary },
  storageRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
    marginBottom: 4,
  },
  storageRowNext: { marginTop: 12 },
  storageLabel: { fontSize: 15, color: colors.secondary },
  storageValue: { fontSize: 14, fontWeight: '500', color: colors.ink },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 44,
  },
  switchLabel: { fontSize: 16, color: colors.ink },
  linkRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 44,
  },
  linkRowLabel: { fontSize: 16, color: colors.ink, flex: 1 },
  linkChevron: { fontSize: 24, color: colors.tertiary, lineHeight: 28 },
  uploadCard: {
    backgroundColor: colors.card,
    borderRadius: radius.card,
    padding: spacing.md,
    marginBottom: spacing.xl,
    gap: 8,
  },
  uploadEyebrow: {
    ...type.captionEmphasis,
    color: colors.tertiary,
    letterSpacing: 0.6,
  },
  uploadTitle: { ...type.titleChapter, color: colors.ink },
  uploadLead: { ...type.caption, color: colors.secondary, lineHeight: 20 },
  uploadBtn: {
    marginTop: 4,
    height: 52,
    borderRadius: 12,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadBtnLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.paper },
  labDisconnect: { marginTop: spacing.xl, alignItems: 'center', minHeight: 44, justifyContent: 'center' },
  labDisconnectText: { ...type.captionEmphasis, color: colors.accent },
});
