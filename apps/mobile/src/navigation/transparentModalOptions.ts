import type { NativeStackNavigationOptions } from '@react-navigation/native-stack';

/** Keeps chapter/detail visible under share & sheet modals (Figma R6-S4). */
export const transparentModalScreenOptions: NativeStackNavigationOptions = {
  presentation: 'transparentModal',
  animation: 'fade',
  contentStyle: { backgroundColor: 'transparent' },
};

export const transparentModalSheetOptions: NativeStackNavigationOptions = {
  presentation: 'transparentModal',
  contentStyle: { backgroundColor: 'transparent' },
};
