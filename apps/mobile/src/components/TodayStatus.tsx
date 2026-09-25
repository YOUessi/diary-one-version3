import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import type { TodayStatus } from '../model';
import { colors, font, layout, radius, spacing } from '../theme';

type Banner = { title: string; subtitle?: string; actionLabel?: string; onAction?: () => void };

export function getTodayBanner(status: TodayStatus): Banner | null {
  switch (status) {
    case 'READY':
      return null;
    case 'UNSYNCED':
      return {
        title: 'New recordings on Diary One',
        subtitle: 'Sync when you’re ready',
        actionLabel: 'Sync',
      };
    case 'PREPARING':
      return { title: 'Preparing your memories...' };
    case 'READY_NEW_RECORDINGS':
      return {
        title: 'New recordings on Diary One',
        subtitle: 'Sync when you’re ready',
        actionLabel: 'Sync',
      };
    case 'READY_PREPARING':
      return {
        title: 'Preparing new memories...',
        subtitle: 'Your ready memories stay below',
      };
    case 'ZERO_CURATED':
      return { title: 'No memories were created from today\'s recordings.' };
    case 'NO_RECORDINGS':
      return { title: 'No recordings today.' };
    case 'PARTIAL':
      return { title: 'Some memories need attention.', subtitle: 'You can still browse what’s ready.' };
    default:
      return null;
  }
}

export function TodayStatusBanner({
  status,
  onSyncPress,
}: {
  status: TodayStatus;
  onSyncPress?: () => void;
}) {
  const banner = getTodayBanner(status);
  if (!banner) return null;
  const onAction = banner.actionLabel === 'Sync' ? onSyncPress : banner.onAction;
  return (
    <View style={styles.banner}>
      <View style={styles.copy}>
        <Text style={styles.title}>{banner.title}</Text>
        {banner.subtitle ? <Text style={styles.sub}>{banner.subtitle}</Text> : null}
      </View>
      {banner.actionLabel && onAction ? (
        <Pressable
          onPress={onAction}
          style={styles.action}
          hitSlop={8}
          accessibilityRole="button"
          accessibilityLabel={banner.actionLabel}
        >
          <Text style={styles.actionText}>{banner.actionLabel}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    padding: spacing.md,
    marginBottom: spacing.md,
    minHeight: layout.minTouch,
  },
  copy: { flex: 1, paddingRight: spacing.sm },
  title: { fontSize: font.small, fontWeight: '600', color: colors.ink },
  sub: { fontSize: font.micro, color: colors.secondary, marginTop: 2 },
  action: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: layout.minTouch,
    justifyContent: 'center',
  },
  actionText: { fontSize: font.small, fontWeight: '600', color: colors.accent },
});
