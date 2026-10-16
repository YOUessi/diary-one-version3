import React, { useEffect } from 'react';
import { Alert, Linking, StyleSheet, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { OnboardingHeroArt } from '../../components/OnboardingHeroArt';
import { colors, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<OnboardingStackParamList>;

const PAIR_EYEBROW = 'SETUP · PAIR DEVICE';

export function PairingStartScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      title="Pair your Diary One"
      lead="Power on Diary One and keep it near your iPhone. No pairing button is required."
      visualHint="Diary One nearby · abstract hardware placeholder"
      ctaPlacement="content"
      primaryLabel="Find Diary One"
      onPrimary={() => navigation.navigate('PairingBluetoothPermission')}
      secondaryLabel="Continue without a device"
      secondaryTone="muted"
      onSecondary={() => navigation.navigate('PermissionBluetoothRequest')}
    />
  );
}

export function PairingBluetoothPermissionScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      title="Allow Bluetooth"
      lead="Diary One uses Bluetooth for pairing and everyday device control. Bluetooth is requested only when you choose Find Diary One."
      calloutBody="System permission appears after Continue"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PairingSearching')}
      {...(__DEV__
        ? {
            secondaryLabel: 'Simulate denied' as const,
            onSecondary: () => navigation.navigate('PairingBluetoothDenied'),
          }
        : {})}
    />
  );
}

export function PairingBluetoothDeniedScreen() {
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      title="Bluetooth is off for Diary One"
      lead="Pairing cannot continue until Bluetooth access is enabled. Diary One will not repeatedly ask for permission."
      calloutTitle="Pairing unavailable"
      primaryLabel="Open Settings"
      onPrimary={() => Linking.openSettings()}
    >
      <Text style={styles.note}>
        You can come back and try Find Diary One again after changing the permission.
      </Text>
    </OnboardingScaffold>
  );
}

export function PairingSearchingScreen() {
  const navigation = useNavigation<Nav>();
  useEffect(() => {
    const t = setTimeout(() => {
      Alert.alert(
        'No Diary One found',
        'This build has no hardware BLE module yet. Use Continue without a device, or enable Internal lab link under Device settings for sync UI tests.',
        [{ text: 'OK', onPress: () => navigation.navigate('PairingStart') }],
      );
    }, 2800);
    return () => clearTimeout(t);
  }, [navigation]);
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      showBack={false}
      headerLeading="cancel"
      onBack={() => navigation.navigate('PairingStart')}
      title="Looking for Diary One…"
      lead="Keep Diary One powered on and nearby while your iPhone searches."
      visual={
        <>
          <OnboardingHeroArt kind="searching" />
          <Text style={styles.heroCaption}>Searching…</Text>
        </>
      }
    />
  );
}

export function PairingFoundScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      title="Diary One found"
      lead="Your Diary One is nearby and ready to connect."
      visual={
        <>
          <OnboardingHeroArt kind="found" />
          <Text style={styles.heroCaption}>Diary One · Found</Text>
        </>
      }
      ctaPlacement="content"
      primaryLabel="Connect"
      onPrimary={() => navigation.navigate('PairingConnecting')}
    />
  );
}

export function PairingConnectingScreen() {
  const navigation = useNavigation<Nav>();
  useEffect(() => {
    const t = setTimeout(() => navigation.replace('PairingConnected'), 1800);
    return () => clearTimeout(t);
  }, [navigation]);
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      showBack={false}
      headerLeading="cancel"
      onBack={() => navigation.navigate('PairingFound')}
      title="Connecting…"
      lead="Keep Diary One nearby. This usually takes only a moment."
      visual={
        <>
          <OnboardingHeroArt kind="connecting" />
          <Text style={styles.heroCaption}>Connecting…</Text>
        </>
      }
    />
  );
}

export function PairingConnectedScreen() {
  const navigation = useNavigation<Nav>();
  /**
   * Reachable only if a future BLE path lands here. Do not mark hardware_linked
   * without a real transport — inventing link state fails Device honesty checks.
   */
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      showBack={false}
      title="Diary One connected"
      lead="Bluetooth pairing is complete. Wi-Fi Sync is a separate step used later when recordings are transferred."
      visual={
        <>
          <OnboardingHeroArt kind="connected" />
          <Text style={styles.heroCaption}>Connected</Text>
        </>
      }
      ctaPlacement="content"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionBluetoothRequest')}
    />
  );
}

const styles = StyleSheet.create({
  note: { ...type.caption, color: colors.secondary, lineHeight: 20 },
  heroCaption: {
    ...type.caption,
    color: colors.tertiary,
    textAlign: 'center',
    marginTop: 12,
  },
});
