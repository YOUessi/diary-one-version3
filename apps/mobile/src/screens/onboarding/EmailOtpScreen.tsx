import React, { useRef, useState } from 'react';
import {
  Alert,
  TextInput,
  Text,
  StyleSheet,
  View,
  Pressable,
  type TextInput as TextInputType,
} from 'react-native';
import { requestEmailOtp, verifyEmailOtpRemote } from '../../backend/authRemoteService';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';

type Route = RouteProp<OnboardingStackParamList, 'EmailOtp'>;
type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'EmailOtp'>;

/** Figma 127:1195 — six discrete OTP boxes + Continue + Resend. */
export default function EmailOtpScreen() {
  const { email } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const hiddenRef = useRef<TextInputType>(null);

  const digits = code.replace(/\D/g, '').slice(0, 6).split('');
  const ready = digits.length >= 6;

  const onContinue = async () => {
    setBusy(true);
    try {
      const result = await verifyEmailOtpRemote(email, code);
      if (!result.ok) {
        Alert.alert(
          'Invalid code',
          result.reason === 'invalid_code'
            ? 'Enter the 6-digit code from your email (or the beta alert).'
            : result.reason,
        );
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
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <FigmaBackHeader />
      <View style={styles.body}>
        <Text style={styles.title}>Check your email</Text>
        <Text style={styles.lead}>Enter the 6-digit code sent to {email}.</Text>

        <Pressable style={styles.boxes} onPress={() => hiddenRef.current?.focus()}>
          {Array.from({ length: 6 }).map((_, i) => (
            <View key={i} style={[styles.box, digits[i] ? styles.boxFilled : null]}>
              <Text style={styles.digit}>{digits[i] ?? ''}</Text>
            </View>
          ))}
        </Pressable>
        <TextInput
          ref={hiddenRef}
          value={code}
          onChangeText={(t) => setCode(t.replace(/\D/g, '').slice(0, 6))}
          keyboardType="number-pad"
          maxLength={6}
          autoFocus
          caretHidden
          style={styles.hidden}
        />

        <Pressable
          style={[styles.primary, (!ready || busy) && styles.primaryDisabled]}
          disabled={!ready || busy}
          onPress={() => void onContinue()}
        >
          <Text style={styles.primaryLabel}>{busy ? 'Verifying…' : 'Continue'}</Text>
        </Pressable>
        <Pressable onPress={() => void onResend()} style={styles.resendHit}>
          <Text style={styles.resend}>Resend code</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  body: { flex: 1, paddingHorizontal: layout.gutterDiary },
  title: { ...type.titleLarge, color: colors.ink, marginBottom: spacing.sm },
  lead: { ...type.bodyStory, color: colors.secondary, marginBottom: spacing.xxxl },
  /** Figma 127:1195 — OTP 52×56 r10 gap 8; Verify 52×r12 */
  boxes: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    marginBottom: spacing.xxxl,
  },
  box: {
    width: 52,
    height: 56,
    borderRadius: 10,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.divider,
    alignItems: 'center',
    justifyContent: 'center',
  },
  boxFilled: { borderColor: colors.ink },
  digit: { ...type.titleChapter, color: colors.ink },
  hidden: { position: 'absolute', opacity: 0, height: 1, width: 1 },
  primary: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryDisabled: { opacity: 0.4 },
  primaryLabel: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
  resendHit: { minHeight: layout.minTouch, justifyContent: 'center', marginTop: spacing.sm },
  resend: { ...type.caption, color: colors.secondary },
});
