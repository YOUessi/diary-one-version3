import React, { Suspense } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { AccountStackParamList } from './types';
import AccountHomeScreen from '../screens/account/AccountHomeScreen';
import MemoryPreferencesScreen from '../screens/account/MemoryPreferencesScreen';
import PrivacyDataScreen from '../screens/account/PrivacyDataScreen';
import PrivacyDetailScreen from '../screens/account/PrivacyDetailScreen';
import HelpTopicScreen from '../screens/account/HelpTopicScreen';
import EditProfileScreen from '../screens/account/EditProfileScreen';
import NotificationsScreen from '../screens/account/NotificationsScreen';
import LanguageScreen from '../screens/account/LanguageScreen';
import HelpFeedbackScreen from '../screens/account/HelpFeedbackScreen';
import PlanScreen from '../screens/account/PlanScreen';
import LicensesScreen from '../screens/account/LicensesScreen';
import PreferenceAddScreen from '../screens/account/PreferenceAddScreen';
import PreferenceEditScreen from '../screens/account/PreferenceEditScreen';
import PreferenceDeleteConfirmScreen from '../screens/account/PreferenceDeleteConfirmScreen';
import PreferenceSurveyScreen from '../screens/onboarding/PreferenceSurveyScreen';
import SignInScreen from '../screens/onboarding/SignInScreen';
import EmailOtpScreen from '../screens/onboarding/EmailOtpScreen';
import { showInternalLabTools } from '../config/buildProfile';
import { transparentModalSheetOptions } from './transparentModalOptions';
import { colors } from '../theme';

const Stack = createNativeStackNavigator<AccountStackParamList>();
const InternalLabScreen = React.lazy(() => import('../screens/internal/InternalLabScreen'));

function InternalLabRoute() {
  return (
    <Suspense
      fallback={
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.paper }}>
          <ActivityIndicator color={colors.accent} />
        </View>
      }
    >
      <InternalLabScreen />
    </Suspense>
  );
}

export default function AccountStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="AccountHome" component={AccountHomeScreen} />
      <Stack.Screen name="MemoryPreferences" component={MemoryPreferencesScreen} />
      <Stack.Screen name="PreferenceAdd" component={PreferenceAddScreen} options={transparentModalSheetOptions} />
      <Stack.Screen name="PreferenceEdit" component={PreferenceEditScreen} options={transparentModalSheetOptions} />
      <Stack.Screen
        name="PreferenceDeleteConfirm"
        component={PreferenceDeleteConfirmScreen}
        options={transparentModalSheetOptions}
      />
      <Stack.Screen name="PrivacyData" component={PrivacyDataScreen} />
      <Stack.Screen name="PrivacyDetail" component={PrivacyDetailScreen} />
      <Stack.Screen name="HelpTopic" component={HelpTopicScreen} />
      <Stack.Screen name="EditProfile" component={EditProfileScreen} />
      <Stack.Screen name="Notifications" component={NotificationsScreen} />
      <Stack.Screen name="Language" component={LanguageScreen} />
      <Stack.Screen name="HelpFeedback" component={HelpFeedbackScreen} />
      <Stack.Screen name="Plan" component={PlanScreen} />
      <Stack.Screen name="Licenses" component={LicensesScreen} />
      <Stack.Screen name="PreferenceSurvey" component={PreferenceSurveyScreen} />
      <Stack.Screen name="SignIn" component={SignInScreen} />
      <Stack.Screen name="EmailOtp" component={EmailOtpScreen} />
      {showInternalLabTools ? <Stack.Screen name="InternalLab" component={InternalLabRoute} /> : null}
    </Stack.Navigator>
  );
}
