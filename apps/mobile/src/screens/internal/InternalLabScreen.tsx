import React, { useCallback, useState } from 'react';
import {
  Alert,
  ScrollView,
  Text,
  Pressable,
  StyleSheet,
  View,
  ActivityIndicator,
  Share,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { ResearchApiSettings } from '../device/ResearchApiSettings';
import { ProductionApiSettings } from '../device/ProductionApiSettings';
import { CloudProcessingTargetPicker } from '../../components/CloudProcessingTargetPicker';
import { PipelineTaskList } from '../../components/PipelineTaskList';
import { AssetLedgerList } from '../../components/AssetLedgerList';
import { launchEvidenceImport, launchDemoEvidenceImport, launchSimulationVideoImport } from '../../pipeline/launchEvidenceImport';
import { applyOfflineMockDiary } from '../../pipeline/applyOfflineMockDiary';
import { applyLabDemoSeed } from '../../store/hydrate';
import {
  formatSemanticRouteSummary,
  getLastSemanticRouteAudit,
} from '../../evidence/lastSemanticRoute';
import { isNativeVisionAvailable } from '../../evidence/nativeVisionAnalyzer';
import { useAppStore } from '../../store/useAppStore';
import { colors, font, layout, radius, spacing } from '../../theme';
import { PHOTO_LIBRARY_TEST_SOURCE } from '../../domain/mediaIntake';
import { ALGORITHM_LOCK } from '../../config/algorithmLock';
import { applyDevCloudDefaults, ensureDevCloudConsentForLab } from '../../config/applyDevCloudDefaults';
import { requestEmailOtp } from '../../backend/authRemoteService';
import {
  isDevFailSimulationEnabled,
  setDevFailSimulationEnabled,
} from '../../config/devFailSimulation';

/** P3/P4 — phone Expo Go closed loop; not in consumer navigation (IMP01). */
export default function InternalLabScreen() {
  const pipelineTasks = useAppStore((s) => s.pipelineTasks);
  const productionUrl = useAppStore((s) => s.productionApiBaseUrl);
  const cloudTarget = useAppStore((s) => s.cloudProcessingTarget);
  const cloudConsent = useAppStore((s) => s.cloudEvidenceConsent);
  const [healthLine, setHealthLine] = useState<string>('Not checked yet');
  const [busy, setBusy] = useState(false);
  const [failSimOn, setFailSimOn] = useState(() => isDevFailSimulationEnabled());

  const applyEnv = () => {
    applyDevCloudDefaults();
    ensureDevCloudConsentForLab();
    const s = useAppStore.getState();
    Alert.alert(
      'BFF applied',
      `URL: ${s.productionApiBaseUrl || '(empty)'}\nToken: ${s.productionApiToken || '(empty)'}\nTarget: ${s.cloudProcessingTarget}\nCloud consent: ${s.cloudEvidenceConsent === true ? 'yes' : String(s.cloudEvidenceConsent)}`,
    );
  };

  const shareDiagnostics = useCallback(async (text: string) => {
    try {
      await Share.share({ message: text });
    } catch {
      /* cancelled */
    }
  }, []);

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
        ffmpeg_available?: boolean;
        allow_mock_preview?: boolean;
        x02?: { reachable?: boolean };
        mobileclip?: { available?: boolean; reason?: string; model_id?: string };
      };
      if (!res.ok) {
        const line = `HTTP ${res.status} · ${url}`;
        setHealthLine(line);
        Alert.alert('Ping failed', line, [
          { text: 'Share URL', onPress: () => void shareDiagnostics(line) },
          { text: 'OK' },
        ]);
        return;
      }
      const mc = body.mobileclip?.available ? 'yes' : 'no';
      setHealthLine(
        `OK · mode=${body.mode ?? '?'} · x02=${body.x02?.reachable ? 'up' : 'down'} · ffmpeg=${
          body.ffmpeg_available ? 'yes' : 'no'
        } · mc=${mc} · mock=${body.allow_mock_preview ? 'yes' : 'no'} · ${url}`,
      );
      if (!body.ffmpeg_available) {
        Alert.alert(
          'BFF reachable — ffmpeg missing',
          'Daily Recap needs ffmpeg on the PC PATH, then restart Dev Lite.\n\nRun: services/bff/scripts/install-ffmpeg-windows.ps1',
        );
      } else if (!body.x02?.reachable) {
        Alert.alert(
          'BFF reachable — X02 down',
          'Cloud Demo will fail or use mock. Restart start-dev-lite-background.ps1 so :8787 is up.',
        );
      } else if (!body.mobileclip?.available) {
        Alert.alert(
          'BFF reachable — MobileCLIP off',
          `Video semantic select-frames needs MobileCLIP on the PC.\n\n${
            body.mobileclip?.reason ?? 'Set DIARY_ONE_MOBILECLIP_CHECKPOINT'
          }\n\nSee docs/WINDOWS_MOBILECLIP_BFF.md then restart start-dev-lite.ps1.`,
        );
      } else if (body.allow_mock_preview === false) {
        Alert.alert(
          'Mock preview is OFF',
          'Without DashScope Key, Demo often returns an empty Diary.\n\nFor Expo Go internal beta restart:\nservices/bff/scripts/start-dev-lite-background.ps1\n(sets ALLOW_MOCK_PREVIEW=true)',
        );
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      const line = `FAIL · ${msg} · ${url}`;
      setHealthLine(line);
      Alert.alert(
        'Ping failed',
        `Cannot reach BFF.\n${url}\n\n${msg}\n\nCheck:\n• Phone & PC same Wi‑Fi\n• Firewall allows TCP 8790 (admin: setup-commercial-dev.ps1 -OpenFirewall)\n• Dev Lite running: services/bff/scripts/start-dev-lite-background.ps1\n• URL uses PC LAN IP, not 127.0.0.1`,
        [
          { text: 'Share details', onPress: () => void shareDiagnostics(line) },
          { text: 'OK' },
        ],
      );
    } finally {
      setBusy(false);
    }
  }, [shareDiagnostics]);

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
            {'\n'}
            Cloud consent: {cloudConsent === true ? 'yes' : cloudConsent === false ? 'no' : 'not set'}
          </Text>
          <Text style={styles.health}>{healthLine}</Text>
          <Pressable style={styles.primaryBtn} onPress={applyEnv}>
            <Text style={styles.primaryLabel}>1 · Apply .env BFF defaults</Text>
          </Pressable>
          <Pressable
            style={styles.secondaryBtn}
            onPress={() => {
              ensureDevCloudConsentForLab();
              if (useAppStore.getState().cloudEvidenceConsent === false) {
                Alert.alert(
                  'Cloud consent is Off',
                  'Turn on Account → Privacy & Data → Allow cloud evidence, then retry Demo.',
                );
                return;
              }
              Alert.alert('Cloud consent', 'Enabled for Expo Go lab (can turn off in Privacy).');
            }}
          >
            <Text style={styles.secondaryLabel}>1b · Enable cloud consent (lab)</Text>
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
          Dev Lite (no Docker): http://&lt;PC-LAN&gt;:8790 · Token dev-token · diary-one/services/bff
          scripts/start-dev-lite-background.ps1 · Recap needs ffmpeg=yes
        </Text>

        <FigmaEyebrow>Research API (optional direct X02)</FigmaEyebrow>
        <ResearchApiSettings />

        <FigmaEyebrow>Figma failed boards</FigmaEyebrow>
        <View style={styles.card}>
          <View style={styles.failSimRow}>
            <View style={styles.failSimCopy}>
              <Text style={styles.failSimTitle}>Simulate failures</Text>
              <Text style={styles.failSimHint}>
                Default off so Share / Save / Search succeed on first try. On = alternate fail for
                Your Story, Edit Profile, Search, Remove, History load, Share prepare.
              </Text>
            </View>
            <Switch
              value={failSimOn}
              onValueChange={(on) => {
                setDevFailSimulationEnabled(on);
                setFailSimOn(on);
              }}
            />
          </View>
        </View>

        <FigmaEyebrow>Evidence import</FigmaEyebrow>
        <Pressable
          style={styles.importBtn}
          onPress={() => {
            applyLabDemoSeed();
            Alert.alert(
              'Lab demo seed loaded',
              'Figma Fishing sample is Lab-only. Wipe / cold start stays empty (PRD DIA02).',
            );
          }}
        >
          <Text style={styles.importLabel}>0a · Load Figma demo seed (Lab only)</Text>
          <Text style={styles.importHint}>
            Optional UI polish. Commercial cold start and Delete Account stay empty — no Fishing.
          </Text>
        </Pressable>
        <Pressable style={styles.importBtn} onPress={() => applyOfflineMockDiary()}>
          <Text style={styles.importLabel}>0 · Offline mock Diary (no cloud)</Text>
          <Text style={styles.importHint}>
            Instant UI check. Not a cloud quality path. Real M2 uses BFF with allow_mock_preview=false.
          </Text>
        </Pressable>
        <Pressable style={styles.importBtn} onPress={() => void launchDemoEvidenceImport()}>
          <Text style={styles.importLabel}>A · Demo photo → cloud → Diary</Text>
          <Text style={styles.importHint}>
            Real Bundle + BFF job. Does not use gallery. Use after Ping is OK.
          </Text>
        </Pressable>
        <Pressable style={styles.importBtn} onPress={() => void launchSimulationVideoImport()}>
          <Text style={styles.importLabel}>A2 · Simulation video → cloud → Diary</Text>
          <Text style={styles.importHint}>
            Bundled clip from assets/motion/sim-morning.mp4. Use this or real photos for cloud chapters.
          </Text>
        </Pressable>
        <Pressable style={styles.importBtn} onPress={() => void launchEvidenceImport()}>
          <Text style={styles.importLabel}>B · Import from photo library</Text>
          <Text style={styles.importHint}>
            Real photos. Often blocked on Expo Go Android — prefer A if B fails.
          </Text>
        </Pressable>
        <Pressable
          style={styles.importBtn}
          onPress={() => {
            const audit = getLastSemanticRouteAudit();
            const vision = isNativeVisionAvailable() ? 'DiaryOneVision=yes' : 'DiaryOneVision=no (Expo Go)';
            Alert.alert(
              'Semantic route debug',
              `${formatSemanticRouteSummary(audit)}\n\n${vision}\n\nImport a video with B to refresh.`,
            );
          }}
        >
          <Text style={styles.importLabel}>C · Semantic route debug</Text>
          <Text style={styles.importHint}>
            Last VIDEO semantic audit (1/3/5/10 frames). Native Vision + AVFoundation frames only in TestFlight / Dev Client.
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
  failSimRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  failSimCopy: { flex: 1, paddingRight: spacing.sm },
  failSimTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  failSimHint: { fontSize: font.micro, color: colors.tertiary, marginTop: 4, lineHeight: 16 },
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
