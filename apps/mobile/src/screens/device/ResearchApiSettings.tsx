import React, { useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet, Alert } from 'react-native';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { checkResearchHealth } from '../../cloud/researchClient';
import type { BundleExportVersion } from '../../pipeline/bundleTypes';
import { BUNDLE_VERSION_ID } from '../../pipeline/bundleTypes';

export function ResearchApiSettings() {
  const endpoint = useAppStore((s) => s.researchEndpoint);
  const token = useAppStore((s) => s.researchToken);
  const setResearchEndpoint = useAppStore((s) => s.setResearchEndpoint);
  const setResearchToken = useAppStore((s) => s.setResearchToken);
  const bundleExportVersion = useAppStore((s) => s.bundleExportVersion);
  const setBundleExportVersion = useAppStore((s) => s.setBundleExportVersion);
  const [draftUrl, setDraftUrl] = useState(endpoint);
  const [draftToken, setDraftToken] = useState(token);

  const save = () => {
    setResearchEndpoint(draftUrl.trim());
    setResearchToken(draftToken.trim());
    Alert.alert('Saved', 'Research API settings stored on this device only.');
  };

  const test = async () => {
    const url = draftUrl.trim();
    if (!url) {
      Alert.alert('Missing URL', 'Enter your PC LAN address, e.g. http://192.168.1.8:8787');
      return;
    }
    try {
      const health = await checkResearchHealth(url, draftToken);
      const supported = health.supportedAppLibraryBundleVersions?.slice(-2).join(', ') ?? 'n/a';
      Alert.alert(
        'Connected',
        `status=${health.status}\npreview=${health.previewPath ?? '/x02/v0.4.1/preview'}\nmodelReady=${health.modelReady ?? '?'}\nbundles: ${supported}`,
      );
    } catch (e) {
      Alert.alert('Connection failed', e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <View style={[styles.wrap, { marginHorizontal: layout.gutterDiary }]}>
      <Text style={styles.title}>Research API (X02)</Text>
      <Text style={styles.hint}>
        Start algorithm server on your PC (handoff runbook port 8787). iPhone must use LAN IP, not
        localhost. Token optional if server has no auth.
      </Text>
      <Text style={styles.subLabel}>Evidence bundle</Text>
      <View style={styles.versionRow}>
        {(['V05','V04', 'V03'] as BundleExportVersion[]).map((v) => (
          <Pressable
            key={v}
            onPress={() => setBundleExportVersion(v)}
            style={[styles.versionChip, bundleExportVersion === v && styles.versionChipOn]}
          >
            <Text style={[styles.versionText, bundleExportVersion === v && styles.versionTextOn]}>
              {v}
            </Text>
          </Pressable>
        ))}
      </View>
      <Text style={styles.versionHint}>
        Default {BUNDLE_VERSION_ID.V04} (letterbox). V05 adds verified capture provenance for Chapter V2; requires updated server. V03 remains center-crop.
      </Text>
      <TextInput
        value={draftUrl}
        onChangeText={setDraftUrl}
        placeholder="http://192.168.x.x:8787"
        placeholderTextColor={colors.tertiary}
        autoCapitalize="none"
        style={styles.input}
      />
      <TextInput
        value={draftToken}
        onChangeText={setDraftToken}
        placeholder="Bearer token (optional)"
        placeholderTextColor={colors.tertiary}
        autoCapitalize="none"
        secureTextEntry
        style={styles.input}
      />
      <View style={styles.row}>
        <Pressable onPress={test} style={styles.btnSecondary}>
          <Text style={styles.btnSecondaryText}>Test connection</Text>
        </Pressable>
        <Pressable onPress={save} style={styles.btnPrimary}>
          <Text style={styles.btnPrimaryText}>Save</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    marginBottom: spacing.md,
    padding: spacing.md,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.divider,
    backgroundColor: colors.card,
  },
  title: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  hint: { fontSize: font.small, color: colors.secondary, marginTop: spacing.xs, lineHeight: 20 },
  subLabel: { fontSize: font.small, fontWeight: '600', color: colors.ink, marginTop: spacing.md },
  versionRow: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.xs },
  versionChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  versionChipOn: { backgroundColor: colors.ink, borderColor: colors.ink },
  versionText: { fontSize: font.small, fontWeight: '600', color: colors.secondary },
  versionTextOn: { color: colors.paper },
  versionHint: { fontSize: font.micro, color: colors.tertiary, marginTop: spacing.xs, lineHeight: 16 },
  input: {
    marginTop: spacing.sm,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: font.body,
    color: colors.ink,
    minHeight: layout.minTouch,
  },
  row: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md },
  btnSecondary: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnSecondaryText: { fontSize: font.small, fontWeight: '600', color: colors.secondary },
  btnPrimary: {
    flex: 1,
    backgroundColor: colors.ink,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnPrimaryText: { color: colors.paper, fontWeight: '700' },
});
