import React from 'react';
import { Text, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, spacing, type } from '../../theme';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { FigmaEyebrow } from '../../components/FigmaScreenHeader';

export default function PlanScreen() {
  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <Text style={styles.title}>Current Plan</Text>
      <View style={styles.gutter}>
        <FigmaEyebrow>Plan</FigmaEyebrow>
        <View style={styles.card}>
          <Text style={styles.planName}>Not available</Text>
          <Text style={styles.planBody}>
            Subscription tiers in Figma are placeholders. This build does not sell Basic / Plus / Pro
            (PRD ACC / D11). Local memories and OTP cloud processing do not imply a paid plan.
          </Text>
        </View>
        <Text style={styles.note}>
          Billing will appear here only after account and commerce services are approved.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  title: {
    ...type.titleSection,
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  gutter: { paddingHorizontal: layout.gutterDiary },
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.divider,
    padding: spacing.lg,
  },
  planName: { ...type.titleChapter, color: colors.ink },
  planBody: { ...type.caption, color: colors.secondary, marginTop: spacing.sm },
  note: {
    ...type.metadata,
    color: colors.tertiary,
    marginTop: spacing.lg,
  },
});
