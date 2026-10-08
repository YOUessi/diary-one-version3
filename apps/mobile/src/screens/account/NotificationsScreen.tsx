import React from 'react';
import { Text, StyleSheet, Switch, View, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';

/** Figma 71:1021 */
export default function NotificationsScreen() {
  const settings = useAppStore((s) => s.notificationSettings);
  const setNotificationSettings = useAppStore((s) => s.setNotificationSettings);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>Notifications</Text>

        <View style={styles.row}>
          <View style={styles.copy}>
            <Text style={styles.label}>Memories Ready</Text>
            <Text style={styles.desc}>When a new curated memory is actually ready.</Text>
          </View>
          <Switch
            value={settings.memoriesReady}
            onValueChange={(memoriesReady) =>
              setNotificationSettings({ ...settings, memoriesReady })
            }
            trackColor={{ false: colors.divider, true: colors.ink }}
            thumbColor={colors.card}
          />
        </View>

        <View style={styles.row}>
          <View style={styles.copy}>
            <Text style={styles.label}>Important Device Alerts</Text>
            <Text style={styles.desc}>
              Storage almost full or a critical device/firmware error.
            </Text>
            <Text style={styles.note}>
              Low battery is handled primarily by Diary One hardware feedback in V1 and is not a
              default phone push notification.
            </Text>
          </View>
          <Switch
            value={settings.deviceAlerts}
            onValueChange={(deviceAlerts) =>
              setNotificationSettings({ ...settings, deviceAlerts })
            }
            trackColor={{ false: colors.divider, true: colors.ink }}
            thumbColor={colors.card}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  /** Figma 71:1021 — title 28; row gap 12; label 17/510 */
  title: { ...type.titleSection, color: colors.ink, marginBottom: spacing.xxxl },
  row: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    marginBottom: spacing.xxxl,
    gap: 12,
  },
  copy: { flex: 1, gap: 2 },
  label: { ...type.bodyStory, fontWeight: '500', color: colors.ink },
  desc: { ...type.caption, color: colors.secondary, lineHeight: 20 },
  note: { ...type.caption, color: colors.tertiary, lineHeight: 18, marginTop: spacing.sm },
});
