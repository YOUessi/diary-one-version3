import React, { useEffect } from 'react';
import { Alert, Linking, StyleSheet, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { OnboardingHeroArt } from '../../components/OnboardingHeroArt';
import { colors, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';
import { useAppStore } from '../../store/useAppStore';

type Nav = NativeStackNavigationProp<OnboardingStackParamList>;

const PAIR_EYEBROW = 'SETUP · PAIR DEVICE';

export function PairingStartScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      title="Pair your Diary One"
      lead="Power on Diary One and keep it near your iPhone. No pairing button is required."
      visual={<OnboardingHeroArt kind="pair" />}
      visualHint="Diary One nearby · abstract hardware placeholder"
      primaryLabel="Find Diary One"
      onPrimary={() => navigation.navigate('PairingBluetoothPermission')}
      secondaryLabel="Continue without a device"
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
      title="Looking for Diary One…"
      lead="Keep Diary One powered on and nearby while your iPhone searches."
      visual={<OnboardingHeroArt kind="searching" />}
      calloutTitle="Searching…"
      secondaryLabel="Cancel"
      onSecondary={() => navigation.navigate('PairingStart')}
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
      visual={<OnboardingHeroArt kind="found" />}
      calloutTitle="Diary One · Found"
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
      title="Connecting…"
      lead="Keep Diary One nearby. This usually takes only a moment."
      visual={<OnboardingHeroArt kind="connecting" />}
      calloutTitle="Connecting…"
      secondaryLabel="Cancel"
      onSecondary={() => navigation.navigate('PairingFound')}
    />
  );
}

export function PairingConnectedScreen() {
  const navigation = useNavigation<Nav>();
  useEffect(() => {
    useAppStore.getState().setDeviceLinkState('hardware_linked');
  }, []);
  return (
    <OnboardingScaffold
      eyebrow={PAIR_EYEBROW}
      showBack={false}
      title="Diary One connected"
      lead="Bluetooth pairing is complete. Wi-Fi Sync is a separate step used later when recordings are transferred."
      visual={<OnboardingHeroArt kind="connected" />}
      calloutTitle="Connected"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionBluetoothRequest')}
    />
  );
}

const styles = StyleSheet.create({
  note: { ...type.caption, color: colors.secondary, lineHeight: 20 },
});
