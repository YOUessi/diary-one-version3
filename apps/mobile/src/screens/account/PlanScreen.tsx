import React from 'react';
import { Text, Pressable, StyleSheet, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, spacing, radius } from '../../theme';
import { FigmaEyebrow } from '../../components/FigmaScreenHeader';

export default function PlanScreen() {
  const navigation = useNavigation();
  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <Pressable onPress={() => navigation.goBack()} style={styles.back}>
        <Text style={styles.backText}>‹ Back</Text>
      </Pressable>
      <Text style={styles.title}>Current Plan</Text>
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
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  back: { paddingHorizontal: layout.gutterDiary, minHeight: layout.minTouch, justifyContent: 'center' },
  backText: { fontSize: font.body, color: colors.accent, fontWeight: '600' },
  title: {
    fontSize: font.title,
    fontWeight: '700',
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  card: {
    marginHorizontal: layout.gutterDiary,
    backgroundColor: colors.card,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.divider,
    padding: spacing.lg,
  },
  planName: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  planBody: { fontSize: font.small, color: colors.secondary, marginTop: spacing.sm, lineHeight: 20 },
  note: {
    fontSize: font.micro,
    color: colors.tertiary,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.lg,
  },
});
