import React from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet, Alert, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaScreenHeader, FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { colors, spacing, radius, font, layout } from '../../theme';
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

/** Matches app.json expo.version (Figma About). */
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
      <Text style={styles.rowTrailing}>
        {value ? `${value} ` : ''}
        ›
      </Text>
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

  const profileSub = localProfile.email ?? 'Local test profile';
  const initial = localProfile.nickname.slice(0, 1).toUpperCase();

  const logOut = () => {
    Alert.alert('Log out', 'Diary One keeps your memories on this device. Logging out clears only local profile in this test build.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Log out',
        style: 'destructive',
        onPress: () => {
          useAppStore.getState().setLocalProfile({
            nickname: 'Guest',
            email: undefined,
          });
        },
      },
    ]);
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaScreenHeader title="Account" />
      {isInternalBetaBuild ? (
        <View style={styles.betaBanner}>
          <FigmaEyebrow>Internal beta</FigmaEyebrow>
          <Text style={styles.betaCopy}>
            UI follows Figma 04. Account and cloud features may use test backends.
          </Text>
        </View>
      ) : null}
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Pressable
          onPress={() => navigation.navigate('EditProfile')}
          style={styles.profileRow}
        >
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

        <FigmaEyebrow>What matters to you</FigmaEyebrow>
        {preferences.length === 0 ? (
          <>
            <Text style={styles.hint}>Tell Diary One what matters to you.</Text>
            <Pressable onPress={() => navigation.navigate('PreferenceAdd')}>
              <Text style={styles.addPref}>+ Add what matters to you</Text>
            </Pressable>
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
            <Pressable onPress={() => navigation.navigate('PreferenceAdd')} style={styles.prefActions}>
              <Text style={styles.addShort}>+ Add</Text>
            </Pressable>
            <Pressable
              onPress={() => navigation.navigate('MemoryPreferences')}
              style={styles.manageRow}
            >
              <Text style={styles.manageLabel}>Manage</Text>
              <Text style={styles.manageChevron}>›</Text>
            </Pressable>
          </>
        )}

        <FigmaEyebrow>Plan</FigmaEyebrow>
        <View style={styles.listCard}>
          <SettingsRow label="Current Plan" value="Basic" onPress={() => navigation.navigate('Plan')} />
        </View>

        <FigmaEyebrow>Privacy & data</FigmaEyebrow>
        <View style={styles.listCard}>
          <SettingsRow label="Privacy & Data" onPress={() => navigation.navigate('PrivacyData')} />
        </View>

        <FigmaEyebrow>App settings</FigmaEyebrow>
        <View style={styles.listCard}>
          <SettingsRow label="Notifications" onPress={() => navigation.navigate('Notifications')} />
          <SettingsRow
            label="Language"
            value={languageDisplayLabel(language)}
            onPress={() => navigation.navigate('Language')}
          />
        </View>

        {showInternalLabTools ? (
          <>
            <FigmaEyebrow>Phone test · cloud loop</FigmaEyebrow>
            <Text style={styles.hint}>
              Open lab → Apply BFF → Ping → Import photos. OTP uses the same BFF.
            </Text>
            <View style={styles.listCard}>
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
            </View>
          </>
        ) : null}

        <FigmaEyebrow>Support</FigmaEyebrow>
        <View style={styles.listCard}>
          <SettingsRow label="Help & Feedback" onPress={() => navigation.navigate('HelpFeedback')} />
        </View>

        <FigmaEyebrow>About</FigmaEyebrow>
        <View style={styles.listCard}>
          <View style={styles.rowStatic}>
            <Text style={styles.rowLabel}>App Version</Text>
            <Text style={styles.rowValue}>{APP_VERSION}</Text>
          </View>
          <SettingsRow label="Licenses" onPress={() => navigation.navigate('Licenses')} />
        </View>

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
  scroll: { paddingBottom: spacing.xl },
  profileRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.lg,
    gap: spacing.md,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.accentSoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarImage: { width: 52, height: 52, borderRadius: 26 },
  avatarLetter: { fontSize: font.h2, fontWeight: '700', color: colors.accent },
  profileCopy: { flex: 1 },
  profileName: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  profileSub: { fontSize: font.small, color: colors.secondary, marginTop: 2 },
  editRow: { flexDirection: 'row', alignItems: 'center', gap: 2 },
  editTrailing: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  editChevron: { fontSize: font.small, color: colors.tertiary },
  hint: {
    fontSize: font.small,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  prefChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  prefChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  prefChipText: { fontSize: font.small, fontWeight: '600', color: colors.ink },
  prefActions: { paddingHorizontal: layout.gutterDiary, paddingVertical: spacing.sm },
  addShort: { fontSize: font.body, fontWeight: '600', color: colors.accent },
  manageRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: 4,
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.md,
    minHeight: layout.minTouch,
  },
  manageLabel: { fontSize: font.body, fontWeight: '600', color: colors.accent },
  manageChevron: { fontSize: font.body, color: colors.tertiary },
  addPref: {
    fontSize: font.body,
    fontWeight: '600',
    color: colors.accent,
    paddingHorizontal: layout.gutterDiary,
    paddingVertical: spacing.md,
  },
  listCard: {
    marginHorizontal: layout.gutterDiary,
    backgroundColor: colors.card,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.divider,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    minHeight: layout.minTouch,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  rowStatic: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    minHeight: layout.minTouch,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  rowLabel: { fontSize: font.body, color: colors.ink },
  rowValue: { fontSize: font.body, color: colors.secondary },
  rowTrailing: { fontSize: font.body, color: colors.tertiary },
  logout: {
    marginTop: spacing.lg,
    marginHorizontal: layout.gutterDiary,
    minHeight: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutText: { fontSize: font.body, fontWeight: '600', color: colors.accent },
  chips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    paddingHorizontal: layout.gutterDiary,
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
  betaCopy: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
});
