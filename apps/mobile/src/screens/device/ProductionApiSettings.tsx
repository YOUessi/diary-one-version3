import React, { useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet, Alert } from 'react-native';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';

export function ProductionApiSettings() {
  const baseUrl = useAppStore((s) => s.productionApiBaseUrl);
  const token = useAppStore((s) => s.productionApiToken);
  const setProductionApiBaseUrl = useAppStore((s) => s.setProductionApiBaseUrl);
  const setProductionApiToken = useAppStore((s) => s.setProductionApiToken);
  const [draftUrl, setDraftUrl] = useState(baseUrl);
  const [draftToken, setDraftToken] = useState(token);

  const save = () => {
    setProductionApiBaseUrl(draftUrl.trim());
    setProductionApiToken(draftToken.trim() || 'dev-token');
    if (draftUrl.trim()) {
      useAppStore.getState().setCloudProcessingTarget('production');
    }
    Alert.alert('Saved', 'Production BFF saved. Cloud target set to Production.');
  };

  const test = async () => {
    const url = draftUrl.trim();
    if (!url) {
      Alert.alert('Missing URL', 'Enter your production BFF base URL when deployed.');
      return;
    }
    try {
      const res = await fetch(`${url.replace(/\/+$/, '')}/health`);
      Alert.alert(res.ok ? 'Reachable' : 'Unreachable', `GET /health → ${res.status}`);
    } catch (e) {
      Alert.alert('Connection failed', e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <View style={[styles.wrap, { marginHorizontal: layout.gutterDiary }]}>
      <Text style={styles.title}>Production API (BFF)</Text>
      <Text style={styles.hint}>
        Expo Go: run diary-one-server Dev Lite (no Docker). Phone URL is your PC LAN IP port 8790,
        token dev-token. See docs/EXPO_GO_DEV_LITE.md. Saving here also switches cloud target to
        Production BFF.
      </Text>
      <TextInput
        value={draftUrl}
        onChangeText={setDraftUrl}
        placeholder="http://192.168.x.x:8790"
        placeholderTextColor={colors.tertiary}
        autoCapitalize="none"
        style={styles.input}
      />
      <TextInput
        value={draftToken}
        onChangeText={setDraftToken}
        placeholder="dev-token (match server API_TOKEN)"
        placeholderTextColor={colors.tertiary}
        autoCapitalize="none"
        secureTextEntry
        style={styles.input}
      />
      <View style={styles.row}>
        <Pressable onPress={() => void test()} style={styles.btnSecondary}>
          <Text style={styles.btnSecondaryText}>Test /health</Text>
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
