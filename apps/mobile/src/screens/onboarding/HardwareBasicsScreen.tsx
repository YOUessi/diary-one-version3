import React from 'react';
import { Pressable, StyleSheet, Text, View, ScrollView } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { OnboardingHeroArt } from '../../components/OnboardingHeroArt';
import { HARDWARE_BASICS } from './hardwareBasicsContent';
import { colors, layout, spacing, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';

type Route = RouteProp<OnboardingStackParamList, 'HardwareBasics'>;
type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'HardwareBasics'>;

/** Figma 75:993 — eyebrow + dots + visual shell + nested callout + Continue. */
export default function HardwareBasicsScreen() {
  const { step } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const page = HARDWARE_BASICS[step];
  if (!page) {
    navigation.replace('HardwareBasics', { step: 0 });
    return null;
  }

  const onPrimary = () => {
    if (step >= HARDWARE_BASICS.length - 1) {
      navigation.navigate('PreferenceSurvey', { step: 0, mode: 'onboarding' });
      return;
    }
    navigation.push('HardwareBasics', { step: step + 1 });
  };

  const onBack = () => {
    if (step > 0) navigation.goBack();
    else navigation.navigate('SetupComplete');
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <View style={styles.top}>
        <Pressable onPress={onBack} style={styles.back} hitSlop={12}>
          <Text style={styles.backText}>‹</Text>
        </Pressable>
        <Text style={styles.eyebrow}>{page.eyebrow}</Text>
        <View style={styles.dots}>
          {HARDWARE_BASICS.map((_, i) => (
            <View key={i} style={[styles.dot, i === step && styles.dotOn]} />
          ))}
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>{page.title}</Text>
        <Text style={styles.lead}>{page.lead}</Text>

        <View style={styles.visualShell}>
          <OnboardingHeroArt kind={page.art} />
          <View style={styles.callout}>
            <Text style={styles.calloutTitle}>{page.calloutTitle}</Text>
            <Text style={styles.calloutBody}>{page.calloutBody}</Text>
          </View>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <Pressable style={styles.primary} onPress={onPrimary}>
          <Text style={styles.primaryLabel}>{page.primary}</Text>
        </Pressable>
        {step < HARDWARE_BASICS.length - 1 ? (
          <Pressable
            style={styles.secondary}
            onPress={() => navigation.navigate('PreferenceSurvey', { step: 0, mode: 'onboarding' })}
          >
            <Text style={styles.secondaryLabel}>Skip device basics</Text>
          </Pressable>
        ) : null}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  top: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.md },
  back: { minHeight: 44, justifyContent: 'center', width: 40 },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300' },
  eyebrow: {
    ...type.metadata,
    fontWeight: '600',
    color: colors.secondary,
    letterSpacing: 0.8,
    textAlign: 'center',
    marginTop: -28,
    marginBottom: spacing.sm,
  },
  dots: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 6,
    marginBottom: spacing.md,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.divider,
  },
  dotOn: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.ink },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.lg,
    flexGrow: 1,
  },
  title: { ...type.titleSection, color: colors.ink, marginBottom: spacing.sm },
  lead: { ...type.bodyStory, color: colors.secondary, marginBottom: spacing.xl },
  /** Figma 75:993 — visual r16; inner callout r12; CTA 52×r12 */
  visualShell: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.md,
    paddingBottom: spacing.md,
    gap: spacing.md,
  },
  callout: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: spacing.lg,
  },
  calloutTitle: { ...type.bodyStory, fontWeight: '600', color: colors.ink, marginBottom: 6 },
  calloutBody: { ...type.caption, color: colors.secondary, lineHeight: 20 },
  footer: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.md,
    gap: spacing.sm,
  },
  primary: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryLabel: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
  secondary: { minHeight: layout.minTouch, alignItems: 'center', justifyContent: 'center' },
  secondaryLabel: { ...type.bodyStory, color: colors.accent, fontWeight: '600' },
});
