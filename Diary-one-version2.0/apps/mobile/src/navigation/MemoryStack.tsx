import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { MemoryStackParamList } from './types';
import MemoryHomeScreen from '../screens/memory/MemoryHomeScreen';
import SearchScreen from '../screens/memory/SearchScreen';
import CapturedByYouScreen from '../screens/memory/CapturedByYouScreen';
import TopicDetailScreen from '../screens/memory/TopicDetailScreen';
import TopicsListScreen from '../screens/memory/TopicsListScreen';
import OriginalViewerScreen from '../screens/memory/OriginalViewerScreen';
import OriginalDeleteConfirmScreen from '../screens/memory/OriginalDeleteConfirmScreen';
import { transparentModalSheetOptions } from './transparentModalOptions';

const Stack = createNativeStackNavigator<MemoryStackParamList>();

export default function MemoryStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="MemoryHome" component={MemoryHomeScreen} />
      <Stack.Screen name="Search" component={SearchScreen} />
      <Stack.Screen name="CapturedByYou" component={CapturedByYouScreen} />
      <Stack.Screen name="TopicsList" component={TopicsListScreen} />
      <Stack.Screen name="TopicDetail" component={TopicDetailScreen} />
      <Stack.Screen name="OriginalViewer" component={OriginalViewerScreen} />
      <Stack.Screen
        name="OriginalDeleteConfirm"
        component={OriginalDeleteConfirmScreen}
        options={transparentModalSheetOptions}
      />
    </Stack.Navigator>
  );
}
