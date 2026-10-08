import React, { useState } from 'react';
import { Text, StyleSheet, ScrollView, Pressable, Alert, ActivityIndicator, Linking } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { DiscardConfirmCard } from '../../components/DiscardConfirmCard';
import { colors, font, layout, spacing } from '../../theme';
import type { AccountStackParamList } from '../../navigation/types';
import {
  PRIVACY_SECTION_COPY,
  PRIVACY_URL_PENDING_NOTE,
  TERMS_URL_PENDING_NOTE,
  privacyPolicyUrl,
  termsUrl,
} from './privacyContent';
import { buildPersistedSlice, useAppStore } from '../../store/useAppStore';
import { exportLocalDataService, wipeLocalDataService } from '../../backend/privacyService';

type Route = RouteProp<AccountStackParamList, 'PrivacyDetail'>;

export default function PrivacyDetailScreen() {
  const { section } = useRoute<Route>().params;
  const navigation = useNavigation<NativeStackNavigationProp<AccountStackParamList>>();
  const copy = PRIVACY_SECTION_COPY[section];
  const [busy, setBusy] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const exportData = async () => {
    setBusy(true);
    try {
      const snapshot = buildPersistedSlice(useAppStore.getState());
      await exportLocalDataService(snapshot);
    } catch (e) {
      Alert.alert('Export failed', e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const confirmDeleteLocal = () => {
    setDeleteOpen(false);
    void wipeLocalDataService().then(() => {
      Alert.alert('Done', 'Local data was reset to the demo seed.');
      navigation.popToTop();
    });
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>{copy.title}</Text>
        <Text style={styles.body}>{copy.body}</Text>
        {section === 'privacy_policy' ? (
          privacyPolicyUrl() ? (
            <Pressable style={styles.btn} onPress={() => void Linking.openURL(privacyPolicyUrl())}>
              <Text style={styles.btnText}>Open privacy policy</Text>
            </Pressable>
          ) : (
            <Text style={styles.pending}>{PRIVACY_URL_PENDING_NOTE}</Text>
          )
        ) : null}
        {section === 'terms' ? (
          termsUrl() ? (
            <Pressable style={styles.btn} onPress={() => void Linking.openURL(termsUrl())}>
              <Text style={styles.btnText}>Open terms of use</Text>
            </Pressable>
          ) : (
            <Text style={styles.pending}>{TERMS_URL_PENDING_NOTE}</Text>
          )
        ) : null}
        {section === 'export_data' ? (
          <Pressable style={styles.btn} onPress={() => void exportData()} disabled={busy}>
            {busy ? (
              <ActivityIndicator color={colors.paper} />
            ) : (
              <Text style={styles.btnText}>Export local data (JSON)</Text>
            )}
          </Pressable>
        ) : null}
        {section === 'delete_account' ? (
          <Pressable style={styles.btnDanger} onPress={() => setDeleteOpen(true)}>
            <Text style={styles.btnDangerText}>Delete local data on this iPhone</Text>
          </Pressable>
        ) : null}
      </ScrollView>

      <DiscardConfirmCard
        visible={deleteOpen}
        title="Delete local data?"
        message="Removes memories, captured originals, profile, and settings from this iPhone. This cannot be undone."
        keepLabel="Cancel"
        discardLabel="Delete"
        onKeepEditing={() => setDeleteOpen(false)}
        onDiscard={confirmDeleteLocal}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  title: { fontSize: 28, fontWeight: '600', color: colors.ink, marginBottom: spacing.md },
  body: { fontSize: font.body, lineHeight: 24, color: colors.secondary },
  pending: {
    marginTop: spacing.md,
    fontSize: font.small,
    lineHeight: 20,
    color: colors.tertiary,
  },
  btn: {
    marginTop: spacing.lg,
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnText: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
  btnDanger: {
    marginTop: spacing.lg,
    borderWidth: 1,
    borderColor: colors.accent,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnDangerText: { fontSize: 15, lineHeight: 20, color: colors.accent, fontWeight: '600' },
});
