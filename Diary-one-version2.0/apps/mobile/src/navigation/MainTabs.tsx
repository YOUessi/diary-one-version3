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
    <Tab.Navigator
      tabBar={(props) => <AppTabBar {...props} />}
      screenOptions={{
        headerShown: false,
        // NAV01 — keep each tab's stack & scroll; do not unmount inactive tabs.
        lazy: false,
        freezeOnBlur: true,
        sceneStyle: { backgroundColor: '#FAF9F6' },
      }}
    >
      <Tab.Screen name="DiaryTab" component={DiaryStack} options={{ title: 'Diary' }} />
      <Tab.Screen name="MemoryTab" component={MemoryStack} options={{ title: 'Memory' }} />
      <Tab.Screen name="DeviceTab" component={DeviceStack} options={{ title: 'Device' }} />
      <Tab.Screen name="AccountTab" component={AccountStack} options={{ title: 'Account' }} />
    </Tab.Navigator>
  );
}
