import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { DeviceStackParamList } from './types';
import DeviceHomeScreen from '../screens/device/DeviceScreen';
import AutomaticCaptureScreen from '../screens/device/AutomaticCaptureScreen';
import DeviceSettingsScreen from '../screens/device/DeviceSettingsScreen';

const Stack = createNativeStackNavigator<DeviceStackParamList>();

export default function DeviceStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="DeviceHome" component={DeviceHomeScreen} />
      <Stack.Screen name="AutomaticCapture" component={AutomaticCaptureScreen} />
      <Stack.Screen name="DeviceSettings" component={DeviceSettingsScreen} />
    </Stack.Navigator>
  );
}
