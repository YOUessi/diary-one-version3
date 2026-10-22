import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import type { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors, elevation, layout, radius, spacing, type } from '../theme';
import { useAppStore } from '../store/useAppStore';
import { appStrings } from '../domain/strings';

const TAB_KEYS: Record<string, keyof ReturnType<typeof appStrings>> = {
  DiaryTab: 'tabDiary',
  MemoryTab: 'tabMemory',
  DeviceTab: 'tabDevice',
  AccountTab: 'tabAccount',
};

function TabIcon({ name, active }: { name: string; active: boolean }) {
  const fill = active ? colors.ink : colors.secondary;
  if (name === 'DiaryTab') {
    return (
      <View style={styles.iconBox}>
        <View style={[styles.diaryBar, { backgroundColor: fill }]} />
        <View style={styles.diaryLines}>
          <View style={[styles.diaryLine, { backgroundColor: fill, width: 11 }]} />
          <View style={[styles.diaryLine, { backgroundColor: fill, width: 9 }]} />
          <View style={[styles.diaryLine, { backgroundColor: fill, width: 10 }]} />
        </View>
      </View>
    );
  }
  if (name === 'MemoryTab') {
    return (
      <View style={styles.iconBox}>
        <View style={[styles.memBack, { backgroundColor: fill, opacity: active ? 0.55 : 0.45 }]} />
        <View style={[styles.memFront, { backgroundColor: fill }]} />
      </View>
    );
  }
  if (name === 'DeviceTab') {
    return (
      <View style={styles.iconBox}>
        <View style={[styles.deviceBody, { borderColor: fill }]}>
          <View style={[styles.deviceLens, { backgroundColor: fill }]} />
        </View>
      </View>
    );
  }
  return (
    <View style={styles.iconBox}>
      <View style={[styles.accountHead, { borderColor: fill }]} />
      <View style={[styles.accountBody, { borderColor: fill }]} />
    </View>
  );
}

/** Figma D1/Bottom Tab Bar — floating white pill, active = ink (not accent). */
export function AppTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();
  const language = useAppStore((s) => s.language);
  const labels = appStrings(language);

  return (
    <View style={[styles.wrap, { paddingBottom: Math.max(insets.bottom, spacing.sm) }]} pointerEvents="box-none">
      <View style={styles.pill}>
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
              <TabIcon name={route.name} active={focused} />
              <Text style={[styles.label, focused ? styles.labelActive : styles.labelIdle]}>{label}</Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    paddingHorizontal: layout.gutterDiary,
  },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    maxWidth: layout.contentWidth,
    height: layout.tabBarHeight,
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    backgroundColor: colors.card,
    borderRadius: radius.pill,
    ...elevation.floating,
  },
  tab: {
    width: 76,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 2,
  },
  label: {
    ...type.metadata,
    textAlign: 'center',
    width: 70,
  },
  labelActive: { color: colors.ink },
  labelIdle: { color: colors.tertiary },
  iconBox: {
    width: 24,
    height: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  diaryBar: {
    position: 'absolute',
    left: 4,
    top: 3,
    width: 3,
    height: 16,
    borderRadius: 1,
  },
  diaryLines: {
    position: 'absolute',
    left: 9,
    top: 4,
    gap: 3,
  },
  diaryLine: { height: 2, borderRadius: 1 },
  memBack: {
    position: 'absolute',
    left: 9,
    top: 2,
    width: 12,
    height: 12,
    borderRadius: 3,
  },
  memFront: {
    position: 'absolute',
    left: 3,
    top: 5,
    width: 14,
    height: 14,
    borderRadius: 3,
  },
  deviceBody: {
    width: 18,
    height: 12,
    borderWidth: 1.5,
    borderRadius: 3,
    alignItems: 'center',
    justifyContent: 'center',
  },
  deviceLens: { width: 4, height: 4, borderRadius: 2 },
  accountHead: {
    width: 8,
    height: 8,
    borderRadius: 4,
    borderWidth: 1.5,
    marginBottom: 1,
  },
  accountBody: {
    width: 14,
    height: 7,
    borderTopLeftRadius: 7,
    borderTopRightRadius: 7,
    borderWidth: 1.5,
    borderBottomWidth: 0,
  },
});
