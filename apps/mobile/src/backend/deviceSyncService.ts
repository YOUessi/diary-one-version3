import { Alert } from 'react-native';
import { useAppStore } from '../store/useAppStore';
import type { TodayStatus } from '../model';
import type { DeviceSyncOutcome } from './types';
import { getActiveDeviceTransport } from '../device/resolveDeviceTransport';

const SYNC_SOURCE_STATES: TodayStatus[] = ['UNSYNCED', 'READY_NEW_RECORDINGS'];

/** SYN01 — device → phone only; does not run cloud processing. */
export async function performDeviceSyncService(options?: {
  showAlerts?: boolean;
}): Promise<DeviceSyncOutcome> {
  const showAlerts = options?.showAlerts ?? true;
  const state = useAppStore.getState();
  const linked =
    state.deviceLinkState === 'lab_linked' || state.deviceLinkState === 'hardware_linked';

  if (!linked) {
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

  const transport = getActiveDeviceTransport();
  useAppStore.setState({ todayStatus: 'PREPARING' });

  try {
    const pending = await transport.listPendingRecordings();
    const pull = await transport.pullRecordings();
    const battery = await transport.readBattery();
    const now = new Date().toISOString();

    useAppStore.setState({
      todayStatus: 'READY',
      lastSyncedAt: now,
      devicePendingRecordings: pending.count > 0 && pull.uris.length === 0,
      deviceBatteryPercent: battery.percent,
    });

    if (showAlerts && transport.kind === 'lab') {
      Alert.alert(
        'Lab sync complete',
        pull.message ||
          'Device UI updated. Use Evidence Lab to import photos — lab link does not invent recordings.',
      );
    }

    return { ok: true, lastSyncedAt: now };
  } catch (e) {
    useAppStore.setState({ todayStatus: state.todayStatus });
    const reason = e instanceof Error ? e.message : String(e);
    if (showAlerts) Alert.alert('Sync failed', reason);
    return { ok: false, reason: 'sync_failed', detail: reason };
  }
}
