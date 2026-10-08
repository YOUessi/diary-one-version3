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
          <Text style={styles.planName}>Basic</Text>
          <Text style={styles.planBody}>
            Diary One on this device with local memories, manual capture, and optional research API for
            preview processing. Subscription billing is not wired in this build.
          </Text>
        </View>
        <Text style={styles.note}>
          Upgrade paths will appear here when account and billing services are connected.
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
