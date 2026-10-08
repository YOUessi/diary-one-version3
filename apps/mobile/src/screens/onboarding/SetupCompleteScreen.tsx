import React from 'react';
import { Text, StyleSheet, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { colors, spacing, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'SetupComplete'>;

/** Figma 201:2102 — title 34; duration 13; hardware placeholder r16×220; CTA 52×r12. */
export default function SetupCompleteScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow="SETUP COMPLETE"
      showBack
      onBack={() => navigation.goBack()}
      title="Diary One is connected"
      lead="Next, we’ll show you the key controls for wearing, capturing, and syncing."
      visual={
        <View>
          <Text style={styles.duration}>Takes about 30 seconds.</Text>
          <View style={styles.card}>
            <Text style={styles.cardLabel}>Device basics · 7 short steps</Text>
          </View>
        </View>
      }
      primaryLabel="Start device basics"
      onPrimary={() => navigation.navigate('HardwareBasics', { step: 0 })}
    />
  );
}

const styles = StyleSheet.create({
  duration: { ...type.caption, color: colors.secondary, marginBottom: spacing.lg },
  card: {
    minHeight: 220,
    backgroundColor: colors.surface,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
    padding: spacing.md,
  },
  cardLabel: { ...type.caption, color: colors.tertiary, textAlign: 'center' },
});
