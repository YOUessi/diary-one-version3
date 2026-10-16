import React from 'react';
import { Text, StyleSheet, ScrollView, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';

const NOTICES = [
  { name: 'React Native', license: 'MIT' },
  { name: 'Expo SDK', license: 'MIT' },
  { name: 'React Navigation', license: 'MIT' },
  { name: 'Zustand', license: 'MIT' },
  { name: '@gorhom/bottom-sheet', license: 'MIT' },
];

export default function LicensesScreen() {
  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <Text style={styles.title}>Licenses</Text>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.lead}>Open-source components used in Diary One.</Text>
        {NOTICES.map((row) => (
          <View key={row.name} style={styles.row}>
            <Text style={styles.rowName}>{row.name}</Text>
            <Text style={styles.rowLicense}>{row.license}</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  title: {
    ...type.titleSection,
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  lead: { ...type.caption, color: colors.secondary, marginBottom: spacing.md },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    minHeight: 52,
    paddingVertical: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  rowName: { ...type.bodyStory, color: colors.ink },
  rowLicense: { ...type.caption, color: colors.tertiary },
});
