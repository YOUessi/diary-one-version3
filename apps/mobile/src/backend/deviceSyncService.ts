import { Alert } from 'react-native';
import { useAppStore } from '../store/useAppStore';
import type { TodayStatus } from '../model';
import type { DeviceSyncOutcome } from './types';

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

const SYNC_SOURCE_STATES: TodayStatus[] = ['UNSYNCED', 'READY_NEW_RECORDINGS'];

/** SYN01 — device → phone only; does not run cloud processing. */
export async function performDeviceSyncService(options?: {
  showAlerts?: boolean;
}): Promise<DeviceSyncOutcome> {
  const showAlerts = options?.showAlerts ?? true;
  const state = useAppStore.getState();

  if (state.deviceLinkState !== 'lab_linked') {
    if (showAlerts) {
      Alert.alert(
        'Not connected',
        'Pair Diary One hardware to sync recordings. Lab link is under Device settings for internal testing.',
      );
    }
    return { ok: false, reason: 'not_connected' };
  }

  if (!SYNC_SOURCE_STATES.includes(state.todayStatus)) {
    if (showAlerts) {
      Alert.alert('Up to date', 'Nothing new to sync from the device.');
    }
    return { ok: false, reason: 'nothing_to_sync' };
  }

  useAppStore.setState({ todayStatus: 'PREPARING' });
  await sleep(1200);
  const now = new Date().toISOString();
  useAppStore.setState({
    todayStatus: 'READY',
    lastSyncedAt: now,
    devicePendingRecordings: false,
  });
  return { ok: true, lastSyncedAt: now };
}
