import React from 'react';
import { Text, StyleSheet, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { colors, font, spacing } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';
import { completeWithoutHardware } from '../../onboarding/completeWithoutHardware';

type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'SetupComplete'>;

export default function SetupCompleteScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow="SETUP COMPLETE"
      showBack
      onBack={() => navigation.goBack()}
      title="Diary One is connected"
      lead="Next, we’ll show you the key controls for wearing, capturing, and syncing."
      primaryLabel="Start device basics"
      onPrimary={() => navigation.navigate('HardwareBasics', { step: 0 })}
      secondaryLabel="Skip device basics"
      onSecondary={() => completeWithoutHardware()}
    >
      <Text style={styles.sub}>Takes about 30 seconds.</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Device basics · 7 short steps</Text>
      </View>
    </OnboardingScaffold>
  );
}

const styles = StyleSheet.create({
  sub: { fontSize: font.body, color: colors.secondary, marginBottom: spacing.lg },
  card: {
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: 12,
  },
  cardTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
});
