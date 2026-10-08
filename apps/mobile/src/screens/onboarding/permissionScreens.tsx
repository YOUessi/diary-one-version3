import React from 'react';
import { Linking } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { PERMISSION_DEGRADED_FOOTNOTE } from '../../domain/onboardingPermissionCopy';
import type { OnboardingStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<OnboardingStackParamList>;

const simulateDenied = __DEV__
  ? {
      secondaryLabel: 'Simulate denied' as const,
    }
  : {};

export function PermissionBluetoothRequestScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow="BLUETOOTH PERMISSION"
      titleSize="section"
      title="Pairing needs Bluetooth"
      lead="Diary One uses Bluetooth to discover and connect to your device. This request appears only after you choose Find Diary One."
      calloutVariant="prompt"
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionLocalNetworkRequest')}
      {...simulateDenied}
      onSecondary={__DEV__ ? () => navigation.navigate('PermissionBluetoothDenied') : undefined}
    />
  );
}

export function PermissionBluetoothDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      titleSize="section"
      title="Bluetooth access is off"
      lead="Pairing is unavailable until Bluetooth access is enabled. Diary One will not repeatedly request permission."
      calloutBody={PERMISSION_DEGRADED_FOOTNOTE}
      primaryLabel="Open Settings"
      onPrimary={() => Linking.openSettings()}
      onBack={() => navigation.goBack()}
    />
  );
}

export function PermissionLocalNetworkRequestScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow="LOCAL NETWORK PERMISSION"
      titleSize="section"
      title="Allow local network for Sync"
      lead="Diary One may need local network access the first time Sync uses Wi-Fi. This permission should only be requested if the final SDK actually requires it."
      calloutVariant="prompt"
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionPhotosRequest')}
      {...simulateDenied}
      onSecondary={__DEV__ ? () => navigation.navigate('PermissionLocalNetworkDenied') : undefined}
    />
  );
}

export function PermissionLocalNetworkDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      titleSize="section"
      title="Local Network access is off"
      lead="Sync cannot use the required local network connection. Your existing memories remain available."
      calloutBody={PERMISSION_DEGRADED_FOOTNOTE}
      primaryLabel="Open Settings"
      onPrimary={() => Linking.openSettings()}
      onBack={() => navigation.goBack()}
    />
  );
}

export function PermissionPhotosRequestScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow="PHOTOS PERMISSION"
      titleSize="section"
      title="Allow Photos access"
      lead="Save to Photos needs permission to add this Original to your system photo library. Your Original remains available in Captured by You even if you do not allow access."
      calloutVariant="prompt"
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionNotificationsRequest')}
      {...simulateDenied}
      onSecondary={__DEV__ ? () => navigation.navigate('PermissionPhotosDenied') : undefined}
    />
  );
}

export function PermissionPhotosDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      titleSize="section"
      title="Photos access is off"
      lead="Diary One cannot save this Original to the system photo library. The Original in Diary One is unaffected."
      calloutBody={PERMISSION_DEGRADED_FOOTNOTE}
      primaryLabel="Open Settings"
      onPrimary={() => Linking.openSettings()}
      secondaryLabel="Continue"
      onSecondary={() => navigation.navigate('PermissionNotificationsRequest')}
    />
  );
}

export function PermissionNotificationsRequestScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow="NOTIFICATIONS PERMISSION"
      titleSize="section"
      title="Stay updated when memories are ready"
      lead="After you have experienced Memories Ready once, you can choose to allow notifications for new curated memories and important device alerts."
      calloutVariant="prompt"
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('SetupComplete')}
      {...simulateDenied}
      onSecondary={__DEV__ ? () => navigation.navigate('PermissionNotificationsDenied') : undefined}
    />
  );
}

export function PermissionNotificationsDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      titleSize="section"
      title="Notifications access is off"
      lead="Diary One continues to work normally without notifications. You can enable them later in Settings."
      calloutBody={PERMISSION_DEGRADED_FOOTNOTE}
      primaryLabel="Open Settings"
      onPrimary={() => Linking.openSettings()}
      secondaryLabel="Continue"
      onSecondary={() => navigation.navigate('SetupComplete')}
    />
  );
}
