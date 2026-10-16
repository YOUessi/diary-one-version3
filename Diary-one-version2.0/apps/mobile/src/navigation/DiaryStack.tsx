import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { DiaryStackParamList } from './types';
import DiaryHomeScreen from '../screens/diary/DiaryHomeScreen';
import DiaryCalendarExpandedScreen from '../screens/diary/DiaryCalendarExpandedScreen';
import ChapterDetailScreen from '../screens/diary/ChapterDetailScreen';
import SearchScreen from '../screens/memory/SearchScreen';
import ShareMemorySelectorScreen from '../screens/share/ShareMemorySelectorScreen';
import ShareDaySelectorScreen from '../screens/share/ShareDaySelectorScreen';
import DayPhotoCollageFlowScreen from '../screens/share/DayPhotoCollageFlowScreen';
import YourStoryRemoveConfirmScreen from '../screens/diary/YourStoryRemoveConfirmScreen';
import YourStoryRemoveFailedScreen from '../screens/diary/YourStoryRemoveFailedScreen';
import PhotoCollageFlowScreen from '../screens/share/PhotoCollageFlowScreen';
import IllustratedShareFlowScreen from '../screens/share/IllustratedShareFlowScreen';
import DailyRecapFlowScreen from '../screens/share/DailyRecapFlowScreen';
import {
  transparentModalScreenOptions,
  transparentModalSheetOptions,
} from './transparentModalOptions';

const Stack = createNativeStackNavigator<DiaryStackParamList>();

export default function DiaryStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="DiaryHome" component={DiaryHomeScreen} />
      <Stack.Screen name="CalendarExpanded" component={DiaryCalendarExpandedScreen} />
      <Stack.Screen name="ChapterDetail" component={ChapterDetailScreen} />
      <Stack.Screen name="Search" component={SearchScreen} />
      <Stack.Screen
        name="ShareMemorySelector"
        component={ShareMemorySelectorScreen}
        options={transparentModalScreenOptions}
      />
      <Stack.Screen
        name="ShareDaySelector"
        component={ShareDaySelectorScreen}
        options={transparentModalScreenOptions}
      />
      <Stack.Screen name="DayPhotoCollageFlow" component={DayPhotoCollageFlowScreen} />
      <Stack.Screen
        name="YourStoryRemoveConfirm"
        component={YourStoryRemoveConfirmScreen}
        options={transparentModalSheetOptions}
      />
      <Stack.Screen
        name="YourStoryRemoveFailed"
        component={YourStoryRemoveFailedScreen}
        options={transparentModalSheetOptions}
      />
      <Stack.Screen name="PhotoCollageFlow" component={PhotoCollageFlowScreen} />
      <Stack.Screen name="IllustratedShareFlow" component={IllustratedShareFlowScreen} />
      <Stack.Screen name="DailyRecapFlow" component={DailyRecapFlowScreen} />
    </Stack.Navigator>
  );
}
