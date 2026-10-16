import React from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'SetupComplete'>;

/**
 * Figma 201:2102 — eyebrow → title 34 → lead → duration → placeholder r16×220 → CTA 52.
 * (Standalone so duration sits above the hardware card, not inside OnboardingScaffold.visual.)
 */
export default function SetupCompleteScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.eyebrow}>SETUP COMPLETE</Text>
        <Text style={styles.title}>Diary One is connected</Text>
        <Text style={styles.lead}>
          Next, we&apos;ll show you the key controls for wearing, capturing, and syncing.
        </Text>
        <Text style={styles.duration}>Takes about 30 seconds.</Text>
        <View style={styles.card}>
          <Text style={styles.cardLabel}>Device basics · 7 short steps</Text>
        </View>
      </ScrollView>
      <View style={styles.footer}>
        <Pressable
          style={styles.primary}
          onPress={() => navigation.navigate('HardwareBasics', { step: 0 })}
        >
          <Text style={styles.primaryLabel}>Start device basics</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.xl,
    gap: 18,
  },
  eyebrow: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '600',
    color: colors.secondary,
    letterSpacing: 0.8,
  },
  title: { ...type.titleLarge, color: colors.ink },
  lead: { ...type.bodyStory, color: colors.secondary },
  duration: { fontSize: 13, lineHeight: 18, color: colors.secondary },
  card: {
    height: 220,
    backgroundColor: colors.surface,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.md,
  },
  cardLabel: { ...type.caption, color: colors.tertiary, textAlign: 'center' },
  footer: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.lg,
  },
  primary: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryLabel: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
});
