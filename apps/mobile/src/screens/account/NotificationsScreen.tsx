import React from 'react';
import { Text, StyleSheet, Switch, View, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, font, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';

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
          />
        </View>

        <View style={styles.row}>
          <View style={styles.copy}>
            <Text style={styles.label}>Important Device Alerts</Text>
            <Text style={styles.desc}>
              Storage almost full or a critical device/firmware error.
            </Text>
          </View>
          <Switch
            value={settings.deviceAlerts}
            onValueChange={(deviceAlerts) =>
              setNotificationSettings({ ...settings, deviceAlerts })
            }
          />
        </View>

        <Text style={styles.note}>
          Low battery is handled primarily by Diary One hardware feedback in V1 and is not a default phone push notification.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  title: { fontSize: 28, fontWeight: '600', color: colors.ink, marginBottom: spacing.lg },
  row: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
    gap: spacing.md,
  },
  copy: { flex: 1 },
  label: { fontSize: font.body, fontWeight: '600', color: colors.ink, marginBottom: 4 },
  desc: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
  note: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginTop: spacing.md },
});
