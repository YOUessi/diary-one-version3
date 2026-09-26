import React from 'react';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { HARDWARE_BASICS } from './hardwareBasicsContent';
import type { OnboardingStackParamList } from '../../navigation/types';

type Route = RouteProp<OnboardingStackParamList, 'HardwareBasics'>;
type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'HardwareBasics'>;

export default function HardwareBasicsScreen() {
  const { step } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const page = HARDWARE_BASICS[step];
  if (!page) {
    navigation.replace('HardwareBasics', { step: 0 });
    return null;
  }

  const onPrimary = () => {
    if (step >= HARDWARE_BASICS.length - 1) {
      navigation.navigate('PreferenceSurvey', { step: 0 });
      return;
    }
    navigation.push('HardwareBasics', { step: step + 1 });
  };

  const onBack = () => {
    if (step > 0) navigation.goBack();
    else navigation.navigate('SetupComplete');
  };

  return (
    <OnboardingScaffold
      eyebrow={page.eyebrow}
      title={page.title}
      lead={page.lead}
      visualHint={page.visual}
      calloutTitle={page.calloutTitle}
      calloutBody={page.calloutBody}
      primaryLabel={page.primary}
      onPrimary={onPrimary}
      onBack={onBack}
    />
  );
}
