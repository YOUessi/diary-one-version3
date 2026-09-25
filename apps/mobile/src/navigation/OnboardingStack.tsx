import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { OnboardingStackParamList } from './types';
import SignInScreen from '../screens/onboarding/SignInScreen';
import EmailOtpScreen from '../screens/onboarding/EmailOtpScreen';
import {
  PairingStartScreen,
  PairingBluetoothPermissionScreen,
  PairingBluetoothDeniedScreen,
  PairingSearchingScreen,
  PairingFoundScreen,
  PairingConnectingScreen,
  PairingConnectedScreen,
} from '../screens/onboarding/pairingScreens';
import {
  PermissionBluetoothRequestScreen,
  PermissionBluetoothDeniedScreen,
  PermissionLocalNetworkRequestScreen,
  PermissionLocalNetworkDeniedScreen,
  PermissionPhotosRequestScreen,
  PermissionPhotosDeniedScreen,
  PermissionNotificationsRequestScreen,
  PermissionNotificationsDeniedScreen,
} from '../screens/onboarding/permissionScreens';
import SetupCompleteScreen from '../screens/onboarding/SetupCompleteScreen';
import HardwareBasicsScreen from '../screens/onboarding/HardwareBasicsScreen';

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

export default function OnboardingStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="SignIn" component={SignInScreen} />
      <Stack.Screen name="EmailOtp" component={EmailOtpScreen} />
      <Stack.Screen name="PairingStart" component={PairingStartScreen} />
      <Stack.Screen name="PairingBluetoothPermission" component={PairingBluetoothPermissionScreen} />
      <Stack.Screen name="PairingBluetoothDenied" component={PairingBluetoothDeniedScreen} />
      <Stack.Screen name="PairingSearching" component={PairingSearchingScreen} />
      <Stack.Screen name="PairingFound" component={PairingFoundScreen} />
      <Stack.Screen name="PairingConnecting" component={PairingConnectingScreen} />
      <Stack.Screen name="PairingConnected" component={PairingConnectedScreen} />
      <Stack.Screen name="PermissionBluetoothRequest" component={PermissionBluetoothRequestScreen} />
      <Stack.Screen name="PermissionBluetoothDenied" component={PermissionBluetoothDeniedScreen} />
      <Stack.Screen name="PermissionLocalNetworkRequest" component={PermissionLocalNetworkRequestScreen} />
      <Stack.Screen name="PermissionLocalNetworkDenied" component={PermissionLocalNetworkDeniedScreen} />
      <Stack.Screen name="PermissionPhotosRequest" component={PermissionPhotosRequestScreen} />
      <Stack.Screen name="PermissionPhotosDenied" component={PermissionPhotosDeniedScreen} />
      <Stack.Screen name="PermissionNotificationsRequest" component={PermissionNotificationsRequestScreen} />
      <Stack.Screen name="PermissionNotificationsDenied" component={PermissionNotificationsDeniedScreen} />
      <Stack.Screen name="SetupComplete" component={SetupCompleteScreen} />
      <Stack.Screen name="HardwareBasics" component={HardwareBasicsScreen} />
    </Stack.Navigator>
  );
}
