import React from 'react';
import { Linking } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { PERMISSION_DEGRADED_FOOTNOTE } from '../../domain/onboardingPermissionCopy';
import type { OnboardingStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<OnboardingStackParamList>;

export function PermissionBluetoothRequestScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
      eyebrow="BLUETOOTH PERMISSION"
      title="Pairing needs Bluetooth"
      lead="Diary One uses Bluetooth to discover and connect to your device. This request appears only after you choose Find Diary One."
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionLocalNetworkRequest')}
      secondaryLabel="Simulate denied"
      onSecondary={() => navigation.navigate('PermissionBluetoothDenied')}
    />
  );
}

export function PermissionBluetoothDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
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
      title="Allow local network for Sync"
      lead="Diary One may need local network access the first time Sync uses Wi-Fi. This permission should only be requested if the final SDK actually requires it."
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionPhotosRequest')}
      secondaryLabel="Simulate denied"
      onSecondary={() => navigation.navigate('PermissionLocalNetworkDenied')}
    />
  );
}

export function PermissionLocalNetworkDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
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
      title="Allow Photos access"
      lead="Save to Photos needs permission to add this Original to your system photo library. Your Original remains available in Captured by You even if you do not allow access."
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('PermissionNotificationsRequest')}
      secondaryLabel="Simulate denied"
      onSecondary={() => navigation.navigate('PermissionPhotosDenied')}
    />
  );
}

export function PermissionPhotosDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
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
      title="Stay updated when memories are ready"
      lead="After you have experienced Memories Ready once, you can choose to allow notifications for new curated memories and important device alerts."
      calloutBody="iOS system permission prompt appears here"
      primaryLabel="Continue"
      onPrimary={() => navigation.navigate('SetupComplete')}
      secondaryLabel="Simulate denied"
      onSecondary={() => navigation.navigate('PermissionNotificationsDenied')}
    />
  );
}

export function PermissionNotificationsDeniedScreen() {
  const navigation = useNavigation<Nav>();
  return (
    <OnboardingScaffold
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
