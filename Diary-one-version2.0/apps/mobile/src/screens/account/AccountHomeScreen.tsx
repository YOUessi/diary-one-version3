import React from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet, Alert, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaScreenHeader, FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { colors, spacing, radius, layout, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AccountStackParamList } from '../../navigation/types';
import type { TodayStatus } from '../../model';
import { languageDisplayLabel } from '../../domain/appSettings';
import { isInternalBetaBuild, showInternalLabTools } from '../../config/buildProfile';

type Nav = NativeStackNavigationProp<AccountStackParamList, 'AccountHome'>;

const TODAY_STATES: TodayStatus[] = [
  'READY',
  'UNSYNCED',
  'PREPARING',
  'READY_NEW_RECORDINGS',
  'READY_PREPARING',
  'ZERO_CURATED',
  'NO_RECORDINGS',
  'PARTIAL',
];

const APP_VERSION = '1.0.0';

function SettingsRow({
  label,
  value,
  onPress,
}: {
  label: string;
  value?: string;
  onPress: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <View style={styles.rowTrailingWrap}>
        {value ? <Text style={styles.rowValue}>{value}</Text> : null}
        <Text style={styles.rowChevron}>›</Text>
      </View>
    </Pressable>
  );
}

export default function AccountHomeScreen() {
  const navigation = useNavigation<Nav>();
  const preferences = useAppStore((s) => s.preferences);
  const localProfile = useAppStore((s) => s.localProfile);
  const todayStatus = useAppStore((s) => s.todayStatus);
  const setTodayStatus = useAppStore((s) => s.setTodayStatus);
  const language = useAppStore((s) => s.language);
  const sessionToken = useAppStore((s) => s.sessionToken);

  const profileSub = localProfile.email ?? 'Local test profile';
  const initial = localProfile.nickname.slice(0, 1).toUpperCase();
  const signedInCloud = Boolean(sessionToken.trim());

  const logOut = () => {
    const wipeLocal =
      isInternalBetaBuild ||
      (process.env.EXPO_PUBLIC_STORE_RELEASE ?? '').trim() === '1';
    Alert.alert(
      'Log out',
      wipeLocal
        ? 'This clears your OTP session and wipes local memories / pipeline on this device so the next tester starts empty (multi-user beta).'
        : 'Diary One keeps your memories on this device. Logging out clears only local profile in this test build.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Log out',
          style: 'destructive',
          onPress: () => {
            const store = useAppStore.getState();
            store.setSessionToken('');
            store.setLocalProfile({
              nickname: 'Guest',
              email: undefined,
            });
            if (wipeLocal) {
              void import('../../store/hydrate').then((m) => m.resetLocalAppData());
            }
          },
        },
      ],
    );
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.gutter}>
        <FigmaScreenHeader title="Account" />
      </View>
      {isInternalBetaBuild || showInternalLabTools ? (
        <View style={styles.betaBanner}>
          {isInternalBetaBuild ? (
            <>
              <FigmaEyebrow>Internal beta</FigmaEyebrow>
              <Text style={styles.betaCopy}>
                UI follows Figma 04. Account and cloud features may use test backends.
              </Text>
            </>
          ) : null}
          {showInternalLabTools ? (
            <Pressable
              style={styles.replayTop}
              onPress={() => useAppStore.getState().setOnboardingComplete(false)}
            >
              <Text style={styles.replayTopLabel}>Replay sign-in (onboarding)</Text>
              <Text style={styles.replayTopHint}>Returns to Sign in to Diary One</Text>
            </Pressable>
          ) : null}
        </View>
      ) : null}
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.profileCard}>
          <Pressable onPress={() => navigation.navigate('EditProfile')} style={styles.profileRow}>
            {localProfile.avatarUri ? (
              <Image source={{ uri: localProfile.avatarUri }} style={styles.avatarImage} />
            ) : (
              <View style={styles.avatar}>
                <Text style={styles.avatarLetter}>{initial}</Text>
              </View>
            )}
            <View style={styles.profileCopy}>
              <Text style={styles.profileName}>{localProfile.nickname}</Text>
              <Text style={styles.profileSub}>{profileSub}</Text>
            </View>
            <View style={styles.editRow}>
              <Text style={styles.editTrailing}>Edit</Text>
              <Text style={styles.editChevron}>›</Text>
            </View>
          </Pressable>

          <View style={styles.cardDivider} />

          <Text style={styles.cardEyebrow}>WHAT MATTERS TO YOU</Text>
          {preferences.length === 0 ? (
            <>
              <Text style={styles.prefHint}>Tell Diary One what matters to you.</Text>
              <Pressable onPress={() => navigation.navigate('PreferenceAdd')} style={styles.addHit}>
                <Text style={styles.addPref}>+ Add what matters to you</Text>
              </Pressable>
              {showInternalLabTools ? (
                <Pressable
                  onPress={() => navigation.navigate('PreferenceSurvey', { step: 0, mode: 'account' })}
                  style={styles.addHit}
                >
                  <Text style={styles.addPrefMuted}>Start preference survey</Text>
                </Pressable>
              ) : null}
            </>
          ) : (
            <>
              <View style={styles.prefChips}>
                {preferences.slice(0, 4).map((p) => (
                  <View key={p.id} style={styles.prefChip}>
                    <Text style={styles.prefChipText}>{p.title}</Text>
                  </View>
                ))}
                {preferences.length > 4 ? (
                  <View style={styles.prefChip}>
                    <Text style={styles.prefChipText}>+{preferences.length - 4}</Text>
                  </View>
                ) : null}
              </View>
              <View style={styles.prefActions}>
                <Pressable onPress={() => navigation.navigate('PreferenceAdd')}>
                  <Text style={styles.addShort}>+ Add</Text>
                </Pressable>
                <Pressable
                  onPress={() => navigation.navigate('MemoryPreferences')}
                  style={styles.manageHit}
                >
                  <Text style={styles.manageLabel}>Manage</Text>
                  <Text style={styles.manageChevron}>›</Text>
                </Pressable>
              </View>
              {showInternalLabTools ? (
                <Pressable
                  onPress={() => navigation.navigate('PreferenceSurvey', { step: 0, mode: 'account' })}
                  style={styles.addHit}
                >
                  <Text style={styles.addPrefMuted}>Retake preference survey</Text>
                </Pressable>
              ) : null}
            </>
          )}
        </View>

        {isInternalBetaBuild ? (
          <>
            <FigmaEyebrow>Cloud account</FigmaEyebrow>
            <SettingsRow
              label={signedInCloud ? 'Signed in' : 'Sign in to Diary One'}
              value={signedInCloud ? localProfile.email ?? 'Session active' : 'Required for import'}
              onPress={() => {
                if (signedInCloud) {
                  Alert.alert(
                    'Cloud session',
                    `Signed in as ${localProfile.email ?? 'your email'}. Log out to switch testers.`,
                  );
                  return;
                }
                navigation.navigate('SignIn', { mode: 'account' });
              }}
            />
            <SettingsRow
              label="Preference questionnaire"
              onPress={() => navigation.navigate('PreferenceSurvey', { step: 0, mode: 'account' })}
            />
          </>
        ) : null}

        <FigmaEyebrow>PLAN</FigmaEyebrow>
        {isInternalBetaBuild || showInternalLabTools ? (
          <SettingsRow
            label="Billing"
            value="Not available"
            onPress={() =>
              Alert.alert(
                'Billing not available',
                'Plan tiers in Figma are placeholders. This build does not sell subscriptions (PRD ACC / D11).',
              )
            }
          />
        ) : (
          <SettingsRow
            label="Current Plan"
            value="Basic"
            onPress={() => navigation.navigate('Plan')}
          />
        )}

        <FigmaEyebrow>PRIVACY & DATA</FigmaEyebrow>
        <SettingsRow label="Privacy & Data" onPress={() => navigation.navigate('PrivacyData')} />

        <FigmaEyebrow>APP SETTINGS</FigmaEyebrow>
        <SettingsRow label="Notifications" onPress={() => navigation.navigate('Notifications')} />
        <SettingsRow
          label="Language"
          value={languageDisplayLabel(language)}
          onPress={() => navigation.navigate('Language')}
        />

        {showInternalLabTools ? (
          <>
            <FigmaEyebrow>Phone test · cloud loop</FigmaEyebrow>
            <Text style={styles.hint}>
              Open lab → Apply BFF → Ping → Import photos. OTP uses the same BFF.
            </Text>
            <SettingsRow
              label="Evidence pipeline lab"
              onPress={() => navigation.navigate('InternalLab')}
            />
            <SettingsRow
              label="Replay sign-in (onboarding)"
              onPress={() => {
                useAppStore.getState().setOnboardingComplete(false);
              }}
            />
          </>
        ) : null}

        <FigmaEyebrow>SUPPORT</FigmaEyebrow>
        <SettingsRow label="Help & Feedback" onPress={() => navigation.navigate('HelpFeedback')} />

        <FigmaEyebrow>ABOUT</FigmaEyebrow>
        <View style={styles.rowStatic}>
          <Text style={styles.rowLabel}>App Version</Text>
          <Text style={styles.rowValue}>{APP_VERSION}</Text>
        </View>
        <SettingsRow label="Licenses" onPress={() => navigation.navigate('Licenses')} />

        <Pressable onPress={logOut} style={styles.logout}>
          <Text style={styles.logoutText}>Log Out</Text>
        </Pressable>

        {showInternalLabTools ? (
          <>
            <FigmaEyebrow>Internal · Today state</FigmaEyebrow>
            <View style={styles.chips}>
              {TODAY_STATES.map((s) => (
                <Pressable
                  key={s}
                  onPress={() => setTodayStatus(s)}
                  style={[styles.chip, todayStatus === s && styles.chipActive]}
                >
                  <Text style={[styles.chipText, todayStatus === s && styles.chipTextActive]}>{s}</Text>
                </Pressable>
              ))}
            </View>
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
  /** Figma Memory Profile Hero — r16 sheet, p20 */
  profileCard: {
    backgroundColor: colors.card,
    borderRadius: radius.sheet,
    padding: layout.gutterDiary,
    marginBottom: spacing.sm,
    gap: spacing.md,
  },
  profileRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    minHeight: 64,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarImage: { width: 56, height: 56, borderRadius: 28 },
  avatarLetter: { ...type.titleChapter, color: colors.ink },
  profileCopy: { flex: 1, gap: 2 },
  profileName: { ...type.bodyEmphasis, color: colors.ink },
  profileSub: { ...type.caption, color: colors.secondary },
  editRow: { flexDirection: 'row', alignItems: 'center', gap: 4, width: 72, justifyContent: 'flex-end' },
  editTrailing: { ...type.captionEmphasis, color: colors.secondary, textAlign: 'right' },
  editChevron: { ...type.bodyStory, color: colors.secondary },
  cardDivider: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.divider,
  },
  cardEyebrow: {
    ...type.metadata,
    fontWeight: '600',
    color: colors.tertiary,
    letterSpacing: 0.8,
    marginBottom: spacing.sm,
  },
  prefHint: { ...type.caption, color: colors.secondary, marginBottom: spacing.sm },
  addHit: { minHeight: layout.minTouch, justifyContent: 'center' },
  addPref: { ...type.captionEmphasis, color: colors.secondary },
  addPrefMuted: { ...type.caption, color: colors.accent },
  prefChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  prefChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
  },
  prefChipText: { ...type.captionEmphasis, color: colors.ink },
  prefActions: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: layout.minTouch,
  },
  addShort: { ...type.bodyStory, fontWeight: '600', color: colors.ink },
  manageHit: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  manageLabel: { ...type.bodyStory, fontWeight: '600', color: colors.secondary },
  manageChevron: { ...type.bodyStory, color: colors.tertiary },
  hint: {
    ...type.caption,
    color: colors.secondary,
    marginBottom: spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 52,
  },
  rowStatic: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 52,
  },
  rowLabel: { ...type.bodyEmphasis, color: colors.ink },
  rowTrailingWrap: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  rowValue: { ...type.caption, color: colors.secondary, textAlign: 'right' },
  rowChevron: { fontSize: 17, color: colors.secondary, fontWeight: '500', lineHeight: 24 },
  logout: {
    marginTop: spacing.md,
    minHeight: 52,
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  /** Figma Log Out — secondary, not accent */
  logoutText: { ...type.bodyEmphasis, color: colors.secondary },
  chips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  chip: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    minHeight: 32,
    justifyContent: 'center',
  },
  chipActive: { backgroundColor: colors.accentSoft },
  chipText: { fontSize: 10, color: colors.secondary },
  chipTextActive: { color: colors.accent, fontWeight: '600' },
  betaBanner: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.sm,
    gap: 4,
  },
  betaCopy: { ...type.caption, color: colors.secondary, lineHeight: 20 },
  replayTop: {
    marginTop: spacing.sm,
    borderWidth: 1,
    borderColor: colors.accent,
    borderRadius: radius.pill,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    alignItems: 'center',
  },
  replayTopLabel: { ...type.bodyStory, fontWeight: '700', color: colors.accent },
  replayTopHint: { ...type.metadata, color: colors.secondary, marginTop: 4 },
});
