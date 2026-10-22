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

import ChapterDetailScreen from '../screens/diary/ChapterDetailScreen';
import YourStoryRemoveConfirmScreen from '../screens/diary/YourStoryRemoveConfirmScreen';
import YourStoryRemoveFailedScreen from '../screens/diary/YourStoryRemoveFailedScreen';
import ShareMemorySelectorScreen from '../screens/share/ShareMemorySelectorScreen';
import PhotoCollageFlowScreen from '../screens/share/PhotoCollageFlowScreen';
import IllustratedShareFlowScreen from '../screens/share/IllustratedShareFlowScreen';

const Stack = createNativeStackNavigator<MemoryStackParamList>();

export default function MemoryStack() {
  return (
    <Stack.Navigator initialRouteName="MemoryHome" screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ChapterDetail" component={ChapterDetailScreen} />
      <Stack.Screen name="ShareMemorySelector" component={ShareMemorySelectorScreen} options={transparentModalSheetOptions} />
      <Stack.Screen name="YourStoryRemoveConfirm" component={YourStoryRemoveConfirmScreen} options={transparentModalSheetOptions} />
      <Stack.Screen name="YourStoryRemoveFailed" component={YourStoryRemoveFailedScreen} options={transparentModalSheetOptions} />
      <Stack.Screen name="PhotoCollageFlow" component={PhotoCollageFlowScreen} />
      <Stack.Screen name="IllustratedShareFlow" component={IllustratedShareFlowScreen} />
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
