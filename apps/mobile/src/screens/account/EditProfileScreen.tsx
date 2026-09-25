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
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { PROFILE_DISCARD_ALERT } from '../../domain/discardCopy';

type SaveState = 'idle' | 'saving' | 'failed';

export default function EditProfileScreen() {
  const navigation = useNavigation();
  const saved = useAppStore((s) => s.localProfile);
  const setLocalProfile = useAppStore((s) => s.setLocalProfile);
  const [nickname, setNickname] = useState(saved.nickname);
  const [avatarUri, setAvatarUri] = useState(saved.avatarUri);
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [avatarPreparing, setAvatarPreparing] = useState(false);
  const saveFailAlternate = useRef(false);

  const dirty =
    nickname.trim() !== saved.nickname || (avatarUri ?? '') !== (saved.avatarUri ?? '');

  const goBack = () => {
    if (!dirty) {
      navigation.goBack();
      return;
    }
    Alert.alert(PROFILE_DISCARD_ALERT.title, PROFILE_DISCARD_ALERT.message, [
      { text: PROFILE_DISCARD_ALERT.keepEditing, style: 'cancel' },
      { text: PROFILE_DISCARD_ALERT.discard, style: 'destructive', onPress: () => navigation.goBack() },
    ]);
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
      if (saveFailAlternate.current) {
        saveFailAlternate.current = false;
        setSaveState('failed');
        return;
      }
      saveFailAlternate.current = true;
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
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader onBack={goBack} />
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
        placeholder="Display name"
        placeholderTextColor={colors.tertiary}
        editable={!saving}
      />

      <Text style={styles.label}>Email / Sign-in</Text>
      <Text style={styles.readOnly}>{saved.email ?? 'Local test profile'}</Text>
      <Text style={styles.emailNote}>
        Email and sign-in method are managed by your account and cannot be edited here.
      </Text>

      <Text style={styles.localNote}>Your profile is saved on this iPhone only.</Text>

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

      <Pressable
        onPress={save}
        style={[styles.saveBtn, !nickname.trim() && styles.saveDisabled]}
        disabled={!nickname.trim() || saving || avatarPreparing}
      >
        <Text style={styles.saveLabel}>{failed ? 'Try Again' : 'Save'}</Text>
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: layout.gutterDiary },
  title: { fontSize: 28, fontWeight: '600', color: colors.ink, marginBottom: spacing.md },
  avatarWrap: { alignSelf: 'flex-start', marginBottom: spacing.xs },
  avatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarImage: { width: 72, height: 72, borderRadius: 36 },
  avatarLetter: { fontSize: 28, fontWeight: '600', color: colors.ink },
  avatarHint: { fontSize: font.small, color: colors.secondary, marginBottom: spacing.lg, lineHeight: 20 },
  label: { fontSize: font.small, color: colors.secondary, marginBottom: spacing.xs },
  input: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    fontSize: font.body,
    color: colors.ink,
    marginBottom: spacing.md,
  },
  readOnly: {
    fontSize: font.body,
    color: colors.ink,
    paddingVertical: spacing.sm,
    marginBottom: spacing.xs,
  },
  emailNote: { fontSize: font.micro, color: colors.tertiary, lineHeight: 18, marginBottom: spacing.md },
  localNote: { fontSize: font.small, color: colors.secondary, marginBottom: spacing.md },
  error: { fontSize: font.small, color: colors.accent, marginBottom: spacing.sm },
  savingRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm },
  savingText: { fontSize: font.small, color: colors.secondary },
  saveBtn: {
    marginTop: spacing.sm,
    backgroundColor: colors.ink,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  saveDisabled: { opacity: 0.4 },
  saveLabel: { color: colors.paper, fontWeight: '700' },
});
