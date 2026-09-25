import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import type { RootTabParamList } from './types';
import DiaryStack from './DiaryStack';
import MemoryStack from './MemoryStack';
import AccountStack from './AccountStack';
import DeviceStack from './DeviceStack';
import { AppTabBar } from '../components/AppTabBar';

const Tab = createBottomTabNavigator<RootTabParamList>();

export default function MainTabs() {
  return (
    <Tab.Navigator tabBar={(props) => <AppTabBar {...props} />} screenOptions={{ headerShown: false }}>
      <Tab.Screen name="DiaryTab" component={DiaryStack} options={{ title: 'Diary' }} />
      <Tab.Screen name="MemoryTab" component={MemoryStack} options={{ title: 'Memory' }} />
      <Tab.Screen name="DeviceTab" component={DeviceStack} options={{ title: 'Device' }} />
      <Tab.Screen name="AccountTab" component={AccountStack} options={{ title: 'Account' }} />
    </Tab.Navigator>
  );
}
