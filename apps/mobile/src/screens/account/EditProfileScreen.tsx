import React, { useRef, useState } from 'react';
import {
  Text,
  Pressable,
  TextInput,
  StyleSheet,
  Alert,
  Image,
  View,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { PROFILE_DISCARD_ALERT } from '../../domain/discardCopy';
import { DiscardConfirmCard } from '../../components/DiscardConfirmCard';
import { isDevFailSimulationEnabled } from '../../config/devFailSimulation';

type SaveState = 'idle' | 'saving' | 'failed';

/** Figma 127:1117 — centered avatar, white name field, muted email field. */
export default function EditProfileScreen() {
  const navigation = useNavigation();
  const saved = useAppStore((s) => s.localProfile);
  const setLocalProfile = useAppStore((s) => s.setLocalProfile);
  const [nickname, setNickname] = useState(saved.nickname);
  const [avatarUri, setAvatarUri] = useState(saved.avatarUri);
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [avatarPreparing, setAvatarPreparing] = useState(false);
  const [discardOpen, setDiscardOpen] = useState(false);
  const saveFailAlternate = useRef(false);

  const dirty =
    nickname.trim() !== saved.nickname || (avatarUri ?? '') !== (saved.avatarUri ?? '');

  const goBack = () => {
    if (!dirty) {
      navigation.goBack();
      return;
    }
    setDiscardOpen(true);
  };

  const pickAvatar = async () => {
    if (saving || avatarPreparing) return;
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('Photos access needed', 'Allow Photos to choose a profile image.');
      return;
    }
    setAvatarPreparing(true);
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.9,
      });
      if (!result.canceled && result.assets[0]?.uri) {
        setAvatarUri(result.assets[0].uri);
      }
    } finally {
      setAvatarPreparing(false);
    }
  };

  const save = () => {
    const trimmed = nickname.trim();
    if (!trimmed) return;
    setSaveState('saving');
    setTimeout(() => {
      if (isDevFailSimulationEnabled() && saveFailAlternate.current) {
        saveFailAlternate.current = false;
        setSaveState('failed');
        return;
      }
      if (isDevFailSimulationEnabled()) saveFailAlternate.current = true;
      setLocalProfile({
        ...saved,
        nickname: trimmed,
        avatarUri,
      });
      setSaveState('idle');
      navigation.goBack();
    }, 550);
  };

  const initial = nickname.trim().slice(0, 1).toUpperCase() || '?';
  const saving = saveState === 'saving';
  const failed = saveState === 'failed';

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <FigmaBackHeader onBack={goBack} />
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Edit Profile</Text>

        <Pressable
          onPress={() => void pickAvatar()}
          style={styles.avatarWrap}
          disabled={saving || avatarPreparing}
        >
          {avatarUri ? (
            <Image source={{ uri: avatarUri }} style={styles.avatarImage} />
          ) : (
            <View style={styles.avatar}>
              <Text style={styles.avatarLetter}>{initial}</Text>
            </View>
          )}
        </Pressable>
        <Text style={styles.avatarHint}>
          Tap your avatar to choose a photo using the system Photos picker.
        </Text>

        <Text style={styles.label}>Display Name</Text>
        <TextInput
          value={nickname}
          onChangeText={setNickname}
          style={styles.input}
          placeholderTextColor={colors.tertiary}
          editable={!saving}
        />

        <Text style={styles.label}>Email / Sign-in</Text>
        <View style={styles.readOnlyBox}>
          <Text style={styles.readOnlyText}>{saved.email ?? 'Local test profile'}</Text>
        </View>
        <Text style={styles.emailNote}>
          Email and sign-in method are managed by your account and cannot be edited here.
        </Text>

        {avatarPreparing ? (
          <View style={styles.savingRow}>
            <ActivityIndicator color={colors.accent} />
            <Text style={styles.savingText}>Preparing photo…</Text>
          </View>
        ) : null}
        {failed ? (
          <Text style={styles.error}>Couldn&apos;t save. Your changes are still here.</Text>
        ) : null}
        {saving ? (
          <View style={styles.savingRow}>
            <ActivityIndicator color={colors.accent} />
            <Text style={styles.savingText}>Saving…</Text>
          </View>
        ) : null}
      </ScrollView>

      <View style={styles.footer}>
        <Pressable
          onPress={save}
          style={[styles.saveBtn, !nickname.trim() && styles.saveDisabled]}
          disabled={!nickname.trim() || saving || avatarPreparing}
        >
          <Text style={styles.saveLabel}>{failed ? 'Try Again' : 'Save'}</Text>
        </Pressable>
      </View>

      <DiscardConfirmCard
        visible={discardOpen}
        title={PROFILE_DISCARD_ALERT.title}
        message={PROFILE_DISCARD_ALERT.message}
        keepLabel={PROFILE_DISCARD_ALERT.keepEditing}
        discardLabel={PROFILE_DISCARD_ALERT.discard}
        onKeepEditing={() => setDiscardOpen(false)}
        onDiscard={() => {
          setDiscardOpen(false);
          navigation.goBack();
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.xl,
  },
  title: { ...type.titleLarge, color: colors.ink, marginBottom: spacing.xl },
  avatarWrap: { alignSelf: 'center', marginBottom: spacing.md },
  /** Figma 127:1117 — avatar 88 */
  avatar: {
    width: 88,
    height: 88,
    borderRadius: 44,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarImage: { width: 88, height: 88, borderRadius: 44 },
  avatarLetter: { fontSize: 28, fontWeight: '600', color: colors.ink },
  avatarHint: {
    ...type.caption,
    color: colors.secondary,
    textAlign: 'center',
    marginBottom: spacing.xxxl,
    paddingHorizontal: spacing.md,
  },
  label: { ...type.caption, color: colors.secondary, marginBottom: spacing.sm },
  /** Figma 127:1117 — fields/CTA 52×r12 */
  input: {
    backgroundColor: colors.card,
    borderRadius: 12,
    minHeight: 52,
    paddingHorizontal: spacing.md,
    ...type.bodyStory,
    color: colors.ink,
    marginBottom: spacing.lg,
  },
  readOnlyBox: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    minHeight: 52,
    paddingHorizontal: spacing.md,
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  readOnlyText: { ...type.bodyStory, color: colors.secondary },
  emailNote: { ...type.caption, color: colors.tertiary, lineHeight: 18, marginBottom: spacing.md },
  error: { ...type.caption, color: colors.accent, marginBottom: spacing.sm },
  savingRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm },
  savingText: { ...type.caption, color: colors.secondary },
  footer: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.md },
  saveBtn: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  saveDisabled: { opacity: 0.4 },
  saveLabel: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
});
