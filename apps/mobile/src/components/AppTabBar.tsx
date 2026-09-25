import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import type { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors, font, spacing } from '../theme';
import { useAppStore } from '../store/useAppStore';
import { appStrings } from '../domain/strings';

const TAB_KEYS: Record<string, keyof ReturnType<typeof appStrings>> = {
  DiaryTab: 'tabDiary',
  MemoryTab: 'tabMemory',
  DeviceTab: 'tabDevice',
  AccountTab: 'tabAccount',
};

/** Figma C05 — active ink, not warm accent. */
export function AppTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();
  const language = useAppStore((s) => s.language);
  const labels = appStrings(language);
  return (
    <View style={[styles.bar, { paddingBottom: Math.max(insets.bottom, spacing.sm) }]}>
      {state.routes.map((route, index) => {
        const focused = state.index === index;
        const key = TAB_KEYS[route.name];
        const label = key ? labels[key] : descriptors[route.key].options.title ?? route.name;
        return (
          <Pressable
            key={route.key}
            onPress={() => {
              const e = navigation.emit({ type: 'tabPress', target: route.key, canPreventDefault: true });
              if (!focused && !e.defaultPrevented) navigation.navigate(route.name);
            }}
            style={styles.tab}
            accessibilityRole="button"
            accessibilityState={{ selected: focused }}
          >
            <Text style={[styles.label, focused ? styles.labelActive : styles.labelIdle]}>{label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    flexDirection: 'row',
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.divider,
    backgroundColor: colors.paper,
    paddingTop: spacing.sm,
  },
  tab: { flex: 1, alignItems: 'center', justifyContent: 'center', minHeight: 44 },
  label: { fontSize: font.small, fontWeight: '600' },
  labelActive: { color: colors.ink },
  labelIdle: { color: colors.tertiary },
});
