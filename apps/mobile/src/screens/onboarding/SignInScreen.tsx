import React, { useState } from 'react';
import { Alert, TextInput, Text, StyleSheet, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { colors, font, radius, spacing } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';
import { isStoreRelease } from '../../config/buildProfile';
import { completeWithoutHardware } from '../../onboarding/completeWithoutHardware';
import { requestEmailOtp, resolveAuthApiHint } from '../../backend/authRemoteService';

type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'SignIn'>;

export default function SignInScreen() {
  const navigation = useNavigation<Nav>();
  const [email, setEmail] = useState('');
  const [busy, setBusy] = useState(false);

  const oauthStub = (provider: string) => {
    Alert.alert(
      `${provider} sign-in`,
      'Account sign-in is not connected in this build. Use email to continue.',
    );
  };

  const onContinue = async () => {
    const trimmed = email.trim();
    if (!trimmed.includes('@')) return;
    setBusy(true);
    try {
      const result = await requestEmailOtp(trimmed);
      if (!result.ok) {
        Alert.alert(
          'Could not request code',
          `${result.reason}\n\nBFF: ${resolveAuthApiHint()}\nStart Dev Lite on your PC (see diary-one-server/docs/EXPO_GO_DEV_LITE.md).`,
        );
        return;
      }
      if (result.devCode) {
        Alert.alert(
          'Internal beta OTP',
          `Code for ${trimmed}:\n\n${result.devCode}\n\n(Real email delivery not configured yet.)`,
        );
      } else if (!result.devCode && result.message.includes('local-only')) {
        Alert.alert(
          'Local-only mode',
          'No BFF URL configured. Enter any 6-digit code, or set Production BFF in Lab / EXPO_PUBLIC_DEV_BFF_URL.',
        );
      }
      navigation.navigate('EmailOtp', { email: trimmed });
    } finally {
      setBusy(false);
    }
  };

  return (
    <OnboardingScaffold
      showBack={false}
      title="Sign in to Diary One"
      lead="Your memories, profile, and Captured by You originals stay with your account."
      primaryLabel={busy ? 'Sending…' : 'Continue with Email'}
      primaryDisabled={busy || !email.trim().includes('@')}
      onPrimary={() => void onContinue()}
      secondaryLabel={__DEV__ ? 'Skip to Diary (no device)' : undefined}
      onSecondary={__DEV__ ? () => completeWithoutHardware() : undefined}
    >
      <View style={styles.oauthStack}>
        {isStoreRelease ? (
          <Text style={styles.storeNote}>
            Sign in with email for this release. Apple and Google will be added when the account
            service launches.
          </Text>
        ) : (
          <>
            <Text style={styles.oauth} onPress={() => oauthStub('Apple')}>Continue with Apple</Text>
            <Text style={styles.oauth} onPress={() => oauthStub('Google')}>Continue with Google</Text>
            <Text style={styles.or}>or</Text>
          </>
        )}
        <Text style={styles.fieldLabel}>Email address</Text>
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="you@example.com"
          placeholderTextColor={colors.tertiary}
          keyboardType="email-address"
          autoCapitalize="none"
          style={styles.input}
        />
      </View>
      <Text style={styles.legal}>
        By continuing, you agree to the Terms and acknowledge the Privacy Policy.
      </Text>
    </OnboardingScaffold>
  );
}

const styles = StyleSheet.create({
  oauthStack: { gap: spacing.md, marginBottom: spacing.lg },
  oauth: {
    fontSize: font.body,
    fontWeight: '600',
    color: colors.ink,
    textAlign: 'center',
    paddingVertical: spacing.md,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.pill,
  },
  storeNote: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginBottom: spacing.sm },
  or: { textAlign: 'center', color: colors.tertiary, fontSize: font.small },
  fieldLabel: { fontSize: font.small, color: colors.secondary, marginBottom: 4 },
  input: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    fontSize: font.body,
    color: colors.ink,
  },
  legal: { fontSize: font.micro, color: colors.tertiary, lineHeight: 18, marginTop: spacing.md },
});
