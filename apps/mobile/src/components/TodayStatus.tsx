import { appStrings } from '../domain/strings';
import type { LanguagePreference } from '../domain/appSettings';
import { useAppStore } from '../store/useAppStore';
import React from 'react';
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import type { TodayStatus } from '../model';
import { colors, radius, spacing, type } from '../theme';

type Banner = {
  title: string;
  subtitle?: string;
  preparing?: boolean;
};

/** Figma Today banners (40:3 Unsynced etc). ZERO / NO_RECORDINGS are inline empty copy, not cards. */
export function getTodayBanner(status: TodayStatus, language: LanguagePreference = 'en'): Banner | null {
  const s = appStrings(language);
  switch (status) {
    case 'READY':
      return null;
    case 'UNSYNCED':
    case 'READY_NEW_RECORDINGS':
      return {
        title: s.newRecordings,
        subtitle: s.syncWhenReady,
      };
    case 'PREPARING':
      return { title: s.preparing, preparing: true };
    case 'READY_PREPARING':
      return { title: s.preparingNew, preparing: true };
    case 'ZERO_CURATED':
    case 'NO_RECORDINGS':
      return null;
    case 'PARTIAL':
      return {
        title: s.partial,
        subtitle: s.browseReady,
      };
    default:
      return null;
  }
}

/**
 * Figma D1/Today Status — white r12 h64, accent mark 4×28, no separate Sync chip.
 * Whole row is tappable when onSyncPress provided.
 */
export function TodayStatusBanner({
  status,
  onSyncPress,
}: {
  status: TodayStatus;
  onSyncPress?: () => void;
}) {
  const language = useAppStore((s) => s.language);
  const banner = getTodayBanner(status, language);
  if (!banner) return null;

  const body = (
    <>
      <View style={styles.mark} />
      <View style={styles.copy}>
        <View style={styles.titleRow}>
          {banner.preparing ? (
            <ActivityIndicator size="small" color={colors.accent} style={styles.spinner} />
          ) : null}
          <Text style={styles.title}>{banner.title}</Text>
        </View>
        {banner.subtitle ? <Text style={styles.sub}>{banner.subtitle}</Text> : null}
      </View>
    </>
  );

  if (onSyncPress && (status === 'UNSYNCED' || status === 'READY_NEW_RECORDINGS')) {
    return (
      <Pressable
        onPress={onSyncPress}
        style={styles.banner}
        accessibilityRole="button"
        accessibilityLabel={`${banner.title}. ${banner.subtitle ?? ''}`}
      >
        {body}
      </Pressable>
    );
  }

  return <View style={styles.banner}>{body}</View>;
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.card,
    borderRadius: radius.card,
    paddingVertical: 10,
    paddingHorizontal: spacing.md,
    height: 64,
    width: '100%',
  },
  mark: {
    width: 4,
    height: 28,
    borderRadius: radius.pill,
    backgroundColor: colors.accent,
  },
  copy: { flex: 1, gap: 2 },
  titleRow: { flexDirection: 'row', alignItems: 'center' },
  spinner: { marginRight: spacing.sm },
  title: { ...type.captionEmphasis, color: colors.ink, flexShrink: 1 },
  sub: { ...type.caption, color: colors.secondary },
});
