import React from 'react';
import { Text, StyleSheet, ScrollView, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { FigmaEyebrow } from '../../components/FigmaScreenHeader';
import { SettingsRow } from '../../components/SettingsRow';
import { colors, font, layout, radius, spacing } from '../../theme';
import type { AccountStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<AccountStackParamList, 'PrivacyData'>;

export default function PrivacyDataScreen() {
  const navigation = useNavigation<Nav>();

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>Privacy & Data</Text>
        <Text style={styles.lead}>
          Manage the memory data and account data Diary One stores for you.
        </Text>

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
          Automatic raw clips are transitional processing input and are not kept long-term when they are not selected. Manual Originals remain until you delete them.
        </Text>
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
    marginBottom: spacing.sm,
  },
  lead: {
    fontSize: font.body,
    color: colors.secondary,
    lineHeight: 22,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
  card: {
    marginHorizontal: layout.gutterDiary,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
  },
  footer: {
    fontSize: font.micro,
    color: colors.tertiary,
    lineHeight: 18,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.md,
  },
});
