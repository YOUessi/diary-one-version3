import React from 'react';
import { Linking } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import type { OnboardingStackParamList } from '../../navigation/types';
import { useAppStore } from '../../store/useAppStore';
import { appStrings } from '../../domain/strings';

type Nav = NativeStackNavigationProp<OnboardingStackParamList>;

/** Legacy routes explain permissions; only the feature itself requests OS access. */
function PermissionInformationScreen() {
  const navigation = useNavigation<Nav>();
  const strings = appStrings(useAppStore((s) => s.language));
  return (
    <OnboardingScaffold
      titleSize="section"
      title={strings.permissionInfo}
      lead={strings.permissionLead}
      calloutBody={strings.permissionsLater}
      primaryLabel={strings.continue}
      onPrimary={() => navigation.navigate('PreferenceSurvey', { step: 'welcome' })}
      secondaryLabel={strings.openSettings}
      onSecondary={() => Linking.openSettings()}
    />
  );
}

export const PermissionBluetoothRequestScreen = PermissionInformationScreen;
export const PermissionBluetoothDeniedScreen = PermissionInformationScreen;
export const PermissionLocalNetworkRequestScreen = PermissionInformationScreen;
export const PermissionLocalNetworkDeniedScreen = PermissionInformationScreen;
export const PermissionPhotosRequestScreen = PermissionInformationScreen;
export const PermissionPhotosDeniedScreen = PermissionInformationScreen;
export const PermissionNotificationsRequestScreen = PermissionInformationScreen;
export const PermissionNotificationsDeniedScreen = PermissionInformationScreen;
