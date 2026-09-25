import React, { useCallback, useState } from 'react';
import { Alert, ScrollView, Text, Pressable, StyleSheet, View, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { ResearchApiSettings } from '../device/ResearchApiSettings';
import { ProductionApiSettings } from '../device/ProductionApiSettings';
import { CloudProcessingTargetPicker } from '../../components/CloudProcessingTargetPicker';
import { PipelineTaskList } from '../../components/PipelineTaskList';
import { AssetLedgerList } from '../../components/AssetLedgerList';
import { launchEvidenceImport, launchDemoEvidenceImport } from '../../pipeline/launchEvidenceImport';
import { applyOfflineMockDiary } from '../../pipeline/applyOfflineMockDiary';
import { useAppStore } from '../../store/useAppStore';
import { colors, font, layout, radius, spacing } from '../../theme';
import { PHOTO_LIBRARY_TEST_SOURCE } from '../../domain/mediaIntake';
import { ALGORITHM_LOCK } from '../../config/algorithmLock';
import { applyDevCloudDefaults } from '../../config/applyDevCloudDefaults';
import { requestEmailOtp } from '../../backend/authRemoteService';

/** P3/P4 — phone Expo Go closed loop; not in consumer navigation (IMP01). */
export default function InternalLabScreen() {
  const pipelineTasks = useAppStore((s) => s.pipelineTasks);
  const productionUrl = useAppStore((s) => s.productionApiBaseUrl);
  const cloudTarget = useAppStore((s) => s.cloudProcessingTarget);
  const [healthLine, setHealthLine] = useState<string>('Not checked yet');
  const [busy, setBusy] = useState(false);

  const applyEnv = () => {
    applyDevCloudDefaults();
    const s = useAppStore.getState();
    Alert.alert(
      'BFF applied',
      `URL: ${s.productionApiBaseUrl || '(empty)'}\nToken: ${s.productionApiToken || '(empty)'}\nTarget: ${s.cloudProcessingTarget}`,
    );
  };

  const pingBff = useCallback(async () => {
    const url = useAppStore.getState().productionApiBaseUrl.trim().replace(/\/+$/, '');
    if (!url) {
      setHealthLine('No Production URL — tap Apply .env BFF first');
      return;
    }
    setBusy(true);
    try {
      const res = await fetch(`${url}/health`);
      const body = (await res.json().catch(() => ({}))) as {
        mode?: string;
        x02?: { reachable?: boolean };
      };
      if (!res.ok) {
        setHealthLine(`HTTP ${res.status}`);
        return;
      }
      setHealthLine(
        `OK · mode=${body.mode ?? '?'} · x02=${body.x02?.reachable ? 'up' : 'down'} · ${url}`,
      );
    } catch (e) {
      setHealthLine(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }, []);

  const testOtp = async () => {
    const email = useAppStore.getState().localProfile.email ?? 'dev@diary.one';
    const result = await requestEmailOtp(email);
    if (!result.ok) {
      Alert.alert('OTP failed', result.reason);
      return;
    }
    Alert.alert(
      'OTP ok',
      result.devCode
        ? `dev_code = ${result.devCode}\n(use this on Sign-in screen)`
        : result.message,
    );
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>Internal lab</Text>
        <Text style={styles.lead}>
          Expo Go phone test loop. Source {PHOTO_LIBRARY_TEST_SOURCE} never appears in Captured by
          You. Cloud = PC Dev Lite BFF (:8790), not device Sync.
        </Text>
        <Text style={styles.lock}>
          {ALGORITHM_LOCK.candidate} · {ALGORITHM_LOCK.bundleV04} · {ALGORITHM_LOCK.x02PreviewPath}
        </Text>

        <FigmaEyebrow>Quick connect</FigmaEyebrow>
        <View style={styles.card}>
          <Text style={styles.meta}>
            Target: {cloudTarget}
            {'\n'}
            BFF: {productionUrl.trim() || '(not set)'}
          </Text>
          <Text style={styles.health}>{healthLine}</Text>
          <Pressable style={styles.primaryBtn} onPress={applyEnv}>
            <Text style={styles.primaryLabel}>1 · Apply .env BFF defaults</Text>
          </Pressable>
          <Pressable
            style={styles.secondaryBtn}
            onPress={() => void pingBff()}
            disabled={busy}
          >
            {busy ? (
              <ActivityIndicator color={colors.ink} />
            ) : (
              <Text style={styles.secondaryLabel}>2 · Ping BFF /health</Text>
            )}
          </Pressable>
          <Pressable style={styles.secondaryBtn} onPress={() => void testOtp()}>
            <Text style={styles.secondaryLabel}>3 · Test OTP API</Text>
          </Pressable>
        </View>

        <View style={styles.gutter}>
          <CloudProcessingTargetPicker />
        </View>

        <FigmaEyebrow>Production API (phone → PC)</FigmaEyebrow>
        <ProductionApiSettings />
        <Text style={styles.muted}>
          Dev Lite (no Docker): http://&lt;PC-LAN&gt;:8790 · Token dev-token · start-dev-lite.ps1
        </Text>

        <FigmaEyebrow>Research API (optional direct X02)</FigmaEyebrow>
        <ResearchApiSettings />

        <FigmaEyebrow>Evidence import</FigmaEyebrow>
        <Pressable style={styles.importBtn} onPress={() => applyOfflineMockDiary()}>
          <Text style={styles.importLabel}>0 · Offline mock Diary (no cloud)</Text>
          <Text style={styles.importHint}>
            Instant UI check. If this fails, tell us. If it works, Diary tab is fine — problem is cloud pipeline.
          </Text>
        </Pressable>
        <Pressable style={styles.importBtn} onPress={() => void launchDemoEvidenceImport()}>
          <Text style={styles.importLabel}>A · Demo photo → cloud → Diary</Text>
          <Text style={styles.importHint}>
            Real Bundle + BFF job. Does not use gallery. Use after Ping is OK.
          </Text>
        </Pressable>
        <Pressable style={styles.importBtn} onPress={() => void launchEvidenceImport()}>
          <Text style={styles.importLabel}>B · Import from photo library</Text>
          <Text style={styles.importHint}>
            Real photos. Often blocked on Expo Go Android — prefer A if B fails.
          </Text>
        </Pressable>

        <FigmaEyebrow>Active tasks</FigmaEyebrow>
        <PipelineTaskList tasks={pipelineTasks} />
        {!pipelineTasks.length ? (
          <Text style={styles.muted}>No tasks yet. Import media after Ping succeeds.</Text>
        ) : null}

        <FigmaEyebrow>Bundle ledger (local)</FigmaEyebrow>
        <AssetLedgerList />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingBottom: spacing.xl },
  title: {
    fontSize: 28,
    fontWeight: '600',
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.xs,
  },
  lead: {
    fontSize: font.small,
    color: colors.secondary,
    lineHeight: 20,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  lock: {
    fontSize: font.micro,
    color: colors.tertiary,
    lineHeight: 16,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
  card: {
    marginHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
    padding: spacing.md,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.divider,
    backgroundColor: colors.card,
    gap: spacing.sm,
  },
  meta: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
  health: { fontSize: font.micro, color: colors.ink, lineHeight: 16 },
  primaryBtn: {
    backgroundColor: colors.ink,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryLabel: { color: colors.paper, fontWeight: '700', fontSize: font.small },
  secondaryBtn: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryLabel: { color: colors.ink, fontWeight: '600', fontSize: font.small },
  importBtn: {
    marginHorizontal: layout.gutterDiary,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    marginBottom: spacing.lg,
    backgroundColor: colors.card,
  },
  importLabel: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  importHint: { fontSize: font.micro, color: colors.tertiary, marginTop: 4, lineHeight: 16 },
  gutter: { paddingHorizontal: layout.gutterDiary, marginBottom: spacing.sm },
  muted: {
    fontSize: font.small,
    color: colors.tertiary,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
});
