import React, { useState } from 'react';
import { Alert, TextInput, Text, StyleSheet, View } from 'react-native';
import { requestEmailOtp, verifyEmailOtpRemote } from '../../backend/authRemoteService';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { colors, font, radius, spacing } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';

type Route = RouteProp<OnboardingStackParamList, 'EmailOtp'>;
type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'EmailOtp'>;

export default function EmailOtpScreen() {
  const { email } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);

  const ready = code.replace(/\D/g, '').length >= 6;

  const onContinue = async () => {
    setBusy(true);
    try {
      const result = await verifyEmailOtpRemote(email, code);
      if (!result.ok) {
        Alert.alert('Invalid code', result.reason === 'invalid_code'
          ? 'Enter the 6-digit code from your email (or the beta alert).'
          : result.reason);
        return;
      }
      navigation.navigate('PairingStart');
    } finally {
      setBusy(false);
    }
  };

  const onResend = async () => {
    setCode('');
    const result = await requestEmailOtp(email);
    if (!result.ok) {
      Alert.alert('Resend failed', result.reason);
      return;
    }
    if (result.devCode) {
      Alert.alert('New code', result.devCode);
    } else {
      Alert.alert('Code sent', result.message);
    }
  };

  return (
    <OnboardingScaffold
      title="Check your email"
      lead={`Enter the 6-digit code sent to ${email}.`}
      primaryLabel={busy ? 'Verifying…' : 'Continue'}
      primaryDisabled={!ready || busy}
      onPrimary={() => void onContinue()}
      secondaryLabel="Resend code"
      onSecondary={() => void onResend()}
    >
      <TextInput
        value={code}
        onChangeText={setCode}
        placeholder="6-digit code"
        placeholderTextColor={colors.tertiary}
        keyboardType="number-pad"
        maxLength={6}
        style={styles.code}
      />
      <View style={styles.hintRow}>
        {code.padEnd(6, ' ').split('').slice(0, 6).map((ch, i) => (
          <Text key={i} style={styles.digit}>{ch.trim() || '·'}</Text>
        ))}
      </View>
    </OnboardingScaffold>
  );
}

const styles = StyleSheet.create({
  code: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    fontSize: font.body,
    color: colors.ink,
    letterSpacing: 8,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  hintRow: { flexDirection: 'row', justifyContent: 'center', gap: spacing.md },
  digit: { fontSize: 24, fontWeight: '600', color: colors.ink },
});
