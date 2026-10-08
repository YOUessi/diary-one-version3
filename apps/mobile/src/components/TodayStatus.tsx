import React from 'react';
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import type { TodayStatus } from '../model';
import { colors, layout, radius, spacing, type } from '../theme';

type Banner = {
  title: string;
  subtitle?: string;
  actionLabel?: string;
  preparing?: boolean;
};

/** Figma Today banners (40:313 / 40:454 / 40:597 / 40:742). ZERO / NO_RECORDINGS are inline empty copy, not cards. */
export function getTodayBanner(status: TodayStatus): Banner | null {
  switch (status) {
    case 'READY':
      return null;
    case 'UNSYNCED':
    case 'READY_NEW_RECORDINGS':
      return {
        title: 'New recordings on Diary One',
        subtitle: "Sync when you're ready",
        actionLabel: 'Sync',
      };
    case 'PREPARING':
      return { title: 'Preparing your memories...', preparing: true };
    case 'READY_PREPARING':
      return { title: 'Preparing new memories...', preparing: true };
    case 'ZERO_CURATED':
    case 'NO_RECORDINGS':
      return null;
    case 'PARTIAL':
      return {
        title: 'Some memories need attention.',
        subtitle: "You can still browse what's ready.",
      };
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
  const onAction = banner.actionLabel === 'Sync' ? onSyncPress : undefined;
  return (
    <View style={styles.banner}>
      <View style={styles.copy}>
        <View style={styles.titleRow}>
          {banner.preparing ? (
            <ActivityIndicator size="small" color={colors.accent} style={styles.spinner} />
          ) : null}
          <Text style={styles.title}>{banner.title}</Text>
        </View>
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
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    minHeight: layout.minTouch,
  },
  copy: { flex: 1, paddingRight: spacing.sm },
  titleRow: { flexDirection: 'row', alignItems: 'center' },
  spinner: { marginRight: spacing.sm },
  title: { ...type.captionEmphasis, color: colors.ink, flexShrink: 1 },
  sub: { ...type.metadata, color: colors.secondary, marginTop: 2 },
  action: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
    minHeight: layout.minTouch,
    justifyContent: 'center',
  },
  actionText: { ...type.captionEmphasis, color: colors.accent },
});
