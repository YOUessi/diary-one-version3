import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, Text, View, StyleSheet } from 'react-native';
import { bootstrapStore, subscribePersist } from '../store/hydrate';
import { colors } from '../theme';

export function AppBootstrap({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let unsub: (() => void) | undefined;
    let mounted = true;
    void bootstrapStore().then(() => {
      if (!mounted) return;
      unsub = subscribePersist();
      setReady(true);
    }).catch(() => {
      if (mounted) setFailed(true);
    });
    return () => { mounted = false; unsub?.(); };
  }, [attempt]);

  if (failed) {
    return <View style={styles.splash}>
      <Text>Could not load your saved data.</Text>
      <Text>Your saved data has not been reset.</Text>
      <Pressable style={styles.retry} onPress={() => { setFailed(false); setAttempt((value) => value + 1); }}>
        <Text>Try Again</Text>
      </Pressable>
    </View>;
  }

  if (!ready) {
    return (
      <View style={styles.splash}>
        <ActivityIndicator color={colors.accent} />
      </View>
    );
  }
  return <>{children}</>;
}

const styles = StyleSheet.create({
  splash: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.paper },
  retry: { minHeight: 44, justifyContent: 'center', paddingHorizontal: 20 },
});
