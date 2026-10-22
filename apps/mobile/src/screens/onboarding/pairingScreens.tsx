import React from 'react';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import type { OnboardingStackParamList } from '../../navigation/types';
import { appStrings } from '../../domain/strings';
import { useAppStore } from '../../store/useAppStore';

type Nav = NativeStackNavigationProp<OnboardingStackParamList>;

export function PairingStartScreen() {
  const navigation = useNavigation<Nav>();
  const strings = appStrings(useAppStore((s) => s.language));
  return (
    <OnboardingScaffold
      eyebrow={strings.pairDevice}
      title={strings.pairTitle}
      lead={strings.pairLead}
      ctaPlacement="content"
      primaryLabel={strings.findDevice}
      onPrimary={() => navigation.navigate('PairingBluetoothPermission')}
      secondaryLabel={strings.withoutDevice}
      secondaryTone="muted"
      onSecondary={() => navigation.navigate('PreferenceSurvey', { step: 'welcome' })}
    />
  );
}

/** No hardware transport is integrated. Never simulate discovery or permission results. */
function DeviceConnectionScreen() {
  const navigation = useNavigation<Nav>();
  const connected = useAppStore((s) => s.deviceLinkState === 'hardware_linked');
  const strings = appStrings(useAppStore((s) => s.language));
  return (
    <OnboardingScaffold
      eyebrow={strings.pairDevice}
      title={connected ? strings.deviceConnected : strings.deviceConnectionTitle}
      lead={connected ? strings.deviceBasicsLead : strings.hardwareUnavailable}
      primaryLabel={connected ? strings.deviceBasics : strings.withoutDevice}
      onPrimary={() => connected
        ? navigation.navigate('HardwareBasics', { step: 0 })
        : navigation.navigate('PreferenceSurvey', { step: 'welcome' })}
    />
  );
}

// Retain route compatibility, including previously restored navigation state.
export const PairingBluetoothPermissionScreen = DeviceConnectionScreen;
export const PairingBluetoothDeniedScreen = DeviceConnectionScreen;
export const PairingSearchingScreen = DeviceConnectionScreen;
export const PairingFoundScreen = DeviceConnectionScreen;
export const PairingConnectingScreen = DeviceConnectionScreen;
export const PairingConnectedScreen = DeviceConnectionScreen;
