import React, { useEffect, useRef, useState } from 'react';
import { Alert, Platform, TextInput, Text, StyleSheet, View, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import Constants from 'expo-constants';
import * as AppleAuthentication from 'expo-apple-authentication';
import * as Google from 'expo-auth-session/providers/google';
import * as WebBrowser from 'expo-web-browser';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, radius, spacing, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';
import { completeWithoutHardware } from '../../onboarding/completeWithoutHardware';
import {
  requestEmailOtp,
  resolveAuthApiHint,
  completeOAuthLogin,
} from '../../backend/authRemoteService';
import { isStoreRelease } from '../../config/buildProfile';

WebBrowser.maybeCompleteAuthSession();

const allowInternalSkip =
  !isStoreRelease &&
  (__DEV__ ||
    Constants.appOwnership === 'expo' ||
    (process.env.EXPO_PUBLIC_ALLOW_SKIP_ONBOARDING ?? '').trim() === '1');

/** App Store production: email only (APP_STORE_RELEASE A2). Expo Go / preview keep OAuth UI. */
const showOAuthButtons = !isStoreRelease;

type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'SignIn'>;

type GoogleAuthConfig = {
  clientId: string;
  iosClientId: string;
  androidClientId: string;
  webClientId: string;
};

function resolveGoogleAuthConfig(): GoogleAuthConfig | null {
  const web = (process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID ?? '').trim();
  const ios = (process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID ?? '').trim();
  const android = (process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID ?? '').trim();
  const expo = (process.env.EXPO_PUBLIC_GOOGLE_EXPO_CLIENT_ID ?? '').trim();
  const fallback = android || ios || web || expo;
  if (!fallback) return null;
  return {
    clientId: fallback,
    iosClientId: ios || fallback,
    androidClientId: android || fallback,
    webClientId: web || fallback,
  };
}

function GoogleContinueButton({
  busy,
  onToken,
}: {
  busy: boolean;
  onToken: (token: string) => void;
}) {
  const config = resolveGoogleAuthConfig();
  if (!config) {
    return (
      <Pressable
        style={styles.googleBtn}
        disabled={busy}
        onPress={() =>
          Alert.alert(
            'Google Client ID missing',
            'Create a Google Cloud OAuth client (type: Web) and set EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID in apps/mobile/.env, then restart Metro.',
          )
        }
      >
        <Text style={styles.googleLabel}>Continue with Google</Text>
      </Pressable>
    );
  }
  return <GoogleConfiguredButton busy={busy} config={config} onToken={onToken} />;
}

function GoogleConfiguredButton({
  busy,
  config,
  onToken,
}: {
  busy: boolean;
  config: GoogleAuthConfig;
  onToken: (token: string) => void;
}) {
  const [, googleResponse, promptGoogle] = Google.useIdTokenAuthRequest(config);
  const usedToken = useRef<string | undefined>();

  useEffect(() => {
    const token = googleResponse?.type === 'success' ? googleResponse.params.id_token : undefined;
    if (!token || usedToken.current === token) return;
    usedToken.current = token;
    onToken(token);
  }, [googleResponse, onToken]);

  return (
    <Pressable
      style={styles.googleBtn}
      disabled={busy}
      onPress={() => {
        void promptGoogle();
      }}
    >
      <Text style={styles.googleLabel}>Continue with Google</Text>
    </Pressable>
  );
}

/** Figma 127:1179 — Apple black / Google white / email field / Continue with Email. */
export default function SignInScreen() {
  const navigation = useNavigation<Nav>();
  const [email, setEmail] = useState('');
  const [busy, setBusy] = useState(false);

  const finishOAuth = async (provider: 'apple' | 'google', identityToken: string) => {
    setBusy(true);
    try {
      const result = await completeOAuthLogin(provider, identityToken);
      if (!result.ok) {
        Alert.alert(
          `${provider} sign-in failed`,
          `${result.reason}\n\nBFF: ${resolveAuthApiHint()}`,
        );
        return;
      }
      navigation.navigate('PairingStart');
    } finally {
      setBusy(false);
    }
  };

  const onApple = async () => {
    if (Platform.OS !== 'ios') {
      Alert.alert('Apple sign-in', 'Use an iPhone. Android uses Google or email.');
      return;
    }
    const available = await AppleAuthentication.isAvailableAsync();
    if (!available) {
      Alert.alert('Apple sign-in unavailable', 'This device does not support Sign in with Apple.');
      return;
    }
    try {
      const cred = await AppleAuthentication.signInAsync({
        requestedScopes: [
          AppleAuthentication.AppleAuthenticationScope.EMAIL,
          AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
        ],
      });
      if (!cred.identityToken) {
        Alert.alert('Apple sign-in', 'No identity token returned.');
        return;
      }
      await finishOAuth('apple', cred.identityToken);
    } catch (e) {
      const code = (e as { code?: string }).code;
      if (code === 'ERR_REQUEST_CANCELED') return;
      Alert.alert('Apple sign-in failed', e instanceof Error ? e.message : String(e));
    }
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
          `${result.reason}\n\nBFF: ${resolveAuthApiHint()}`,
        );
        return;
      }
      if (result.devCode) {
        Alert.alert('Internal beta OTP', `Code for ${trimmed}:\n\n${result.devCode}`);
      } else {
        Alert.alert('Check your email', result.message || 'If SMTP is configured, the code was sent.');
      }
      navigation.navigate('EmailOtp', { email: trimmed });
    } finally {
      setBusy(false);
    }
  };

  const canEmail = !busy && email.trim().includes('@');

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <View style={styles.body}>
        <Text style={styles.title}>Sign in to Diary One</Text>
        <Text style={styles.lead}>
          Your memories, profile, and Captured by You originals stay with your account.
        </Text>

        <View style={styles.stack}>
          {showOAuthButtons ? (
            <>
              <Pressable style={styles.appleBtn} disabled={busy} onPress={() => void onApple()}>
                <Text style={styles.appleLabel}>Continue with Apple</Text>
              </Pressable>
              <GoogleContinueButton
                busy={busy}
                onToken={(token) => void finishOAuth('google', token)}
              />
              <Text style={styles.or}>or</Text>
            </>
          ) : null}

          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="Email address"
            placeholderTextColor={colors.tertiary}
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
          />

          <Pressable
            style={[styles.emailBtn, !canEmail && styles.emailBtnDisabled]}
            disabled={!canEmail}
            onPress={() => void onContinue()}
          >
            <Text style={styles.emailLabel}>{busy ? 'Sending…' : 'Continue with Email'}</Text>
          </Pressable>
        </View>

        {allowInternalSkip ? (
          <Pressable style={styles.skipBtn} disabled={busy} onPress={() => completeWithoutHardware()}>
            <Text style={styles.skip}>Skip to Diary (no device)</Text>
            <Text style={styles.skipHint}>Internal test — skip sign-in and pairing</Text>
          </Pressable>
        ) : null}

        <Text style={styles.legal}>
          By continuing, you agree to the Terms and acknowledge the Privacy Policy.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  body: {
    flex: 1,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.xl,
    justifyContent: 'flex-start',
  },
  title: { ...type.titleLarge, color: colors.ink, marginBottom: spacing.sm },
  lead: { ...type.bodyStory, color: colors.secondary, marginBottom: spacing.xxxl },
  /** Figma 127:1179 — content gap 16; controls 52×r12 */
  stack: { gap: spacing.md },
  appleBtn: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  appleLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.paper },
  googleBtn: {
    backgroundColor: colors.card,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.divider,
  },
  googleLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.ink },
  or: { ...type.caption, color: colors.tertiary, textAlign: 'center', marginVertical: spacing.xs },
  input: {
    backgroundColor: colors.card,
    borderRadius: 12,
    minHeight: 52,
    paddingHorizontal: spacing.md,
    ...type.bodyStory,
    color: colors.ink,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  emailBtn: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emailBtnDisabled: { opacity: 0.4 },
  emailLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.paper },
  skipBtn: {
    marginTop: spacing.xl,
    borderWidth: 1,
    borderColor: colors.accent,
    borderRadius: radius.pill,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  skip: { ...type.bodyStory, fontWeight: '700', color: colors.accent },
  skipHint: { ...type.metadata, color: colors.secondary, marginTop: 4 },
  legal: {
    ...type.caption,
    color: colors.tertiary,
    lineHeight: 18,
    marginTop: spacing.xxxl,
    marginBottom: spacing.lg,
  },
});
