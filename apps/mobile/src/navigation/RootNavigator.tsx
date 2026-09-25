import React, { Suspense } from 'react';
import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { useAppStore } from '../store/useAppStore';
import OnboardingStack from './OnboardingStack';
import { colors } from '../theme';

const MainTabs = React.lazy(() => import('./MainTabs'));

export default function RootNavigator() {
  const onboardingComplete = useAppStore((s) => s.onboardingComplete);
  if (!onboardingComplete) return <OnboardingStack />;
  return (
    <Suspense
      fallback={
        <View style={styles.fallback}>
          <ActivityIndicator color={colors.accent} />
        </View>
      }
    >
      <MainTabs />
    </Suspense>
  );
}

const styles = StyleSheet.create({
  fallback: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.paper },
});
