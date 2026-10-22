import React from 'react';
import { Text, StyleSheet, ScrollView, View, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { SettingsRow } from '../../components/SettingsRow';
import { colors, font, layout, spacing, type } from '../../theme';
import type { AccountStackParamList } from '../../navigation/types';
import { useAppStore } from '../../store/useAppStore';

type Nav = NativeStackNavigationProp<AccountStackParamList, 'PrivacyData'>;

function consentLabel(
  consent: boolean | null,
  version: string | null,
): string {
  if (consent === true) {
    return version
      ? `Cloud evidence: agreed (${version})`
      : 'Cloud evidence: agreed';
  }
  if (consent === false) {
    return 'Cloud evidence: browse on device only (upload blocked)';
  }
  return 'Cloud evidence: not set (setup survey skipped or not run)';
}

export default function PrivacyDataScreen() {
  const navigation = useNavigation<Nav>();
  const cloudEvidenceConsent = useAppStore((s) => s.cloudEvidenceConsent);
  const cloudEvidenceConsentVersion = useAppStore((s) => s.cloudEvidenceConsentVersion);
  const setCloudEvidenceConsent = useAppStore((s) => s.setCloudEvidenceConsent);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>Privacy & Data</Text>
        <Text style={styles.lead}>
          Manage the memory data and account data Diary One stores for you.
        </Text>
        <Text style={styles.consentStatus}>
          {consentLabel(cloudEvidenceConsent, cloudEvidenceConsentVersion)}
        </Text>
        <Text style={styles.consentHint}>
          Signing in is not upload consent. Cloud upload runs only when status is agreed — change it
          here anytime.
        </Text>

        <FigmaEyebrow>CLOUD EVIDENCE</FigmaEyebrow>
        <View style={styles.card}>
          <Pressable
            onPress={() => setCloudEvidenceConsent(true)}
            style={styles.choiceRow}
            accessibilityRole="button"
          >
            <Text style={styles.choiceLabel}>Allow cloud evidence upload</Text>
            <Text style={styles.choiceMark}>{cloudEvidenceConsent === true ? '✓' : ''}</Text>
          </Pressable>
          <Pressable
            onPress={() => setCloudEvidenceConsent(false)}
            style={styles.choiceRow}
            accessibilityRole="button"
          >
            <Text style={styles.choiceLabel}>Browse on this device only</Text>
            <Text style={styles.choiceMark}>{cloudEvidenceConsent === false ? '✓' : ''}</Text>
          </Pressable>
        </View>

        <FigmaEyebrow>YOUR DATA</FigmaEyebrow>
        <View style={styles.card}>
          <SettingsRow
            label="Stored Memories & Captured by You"
            onPress={() => navigation.navigate('PrivacyDetail', { section: 'stored_memories' })}
          />
          <SettingsRow
            label="Memory Profile & Stories"
            onPress={() => navigation.navigate('PrivacyDetail', { section: 'memory_profile' })}
          />
          <SettingsRow
            label="Export My Data"
            onPress={() => navigation.navigate('PrivacyDetail', { section: 'export_data' })}
          />
        </View>

        <FigmaEyebrow>ACCOUNT & DATA</FigmaEyebrow>
        <View style={styles.card}>
          <SettingsRow
            label="Delete Account & Data"
            destructive
            onPress={() => navigation.navigate('PrivacyDetail', { section: 'delete_account' })}
          />
        </View>

        <FigmaEyebrow>POLICIES</FigmaEyebrow>
        <View style={styles.card}>
          <SettingsRow
            label="Privacy Policy"
            onPress={() => navigation.navigate('PrivacyDetail', { section: 'privacy_policy' })}
          />
          <SettingsRow
            label="Terms"
            onPress={() => navigation.navigate('PrivacyDetail', { section: 'terms' })}
          />
        </View>

        <Text style={styles.footer}>
          Automatic raw clips are transitional processing input and are not kept long-term when they are
          not selected. Manual Originals remain until you delete them.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingBottom: spacing.xl },
  /** Figma 71:993 — title 28; list rows ~52 */
  title: {
    ...type.titleSection,
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  lead: {
    ...type.bodyStory,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  consentStatus: {
    fontSize: font.small,
    fontWeight: '600',
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: 4,
  },
  consentHint: {
    fontSize: font.micro,
    color: colors.tertiary,
    lineHeight: 18,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
  /** Figma 71:993 — flat rows (no bordered cards); CLOUD EVIDENCE is product extension */
  card: {
    marginHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  choiceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 52,
    paddingVertical: spacing.sm,
  },
  choiceLabel: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.ink, flex: 1, paddingRight: spacing.sm },
  choiceMark: { fontSize: 17, color: colors.ink, fontWeight: '700', minWidth: 20 },
  footer: {
    fontSize: 13,
    lineHeight: 18,
    color: colors.tertiary,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.md,
  },
});
