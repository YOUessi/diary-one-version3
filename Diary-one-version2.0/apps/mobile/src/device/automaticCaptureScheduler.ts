import { getActiveDeviceTransport } from './resolveDeviceTransport';
import { useAppStore } from '../store/useAppStore';

/** Push Account automatic-capture preference toward the active transport. */
export async function applyAutomaticCaptureToDevice(): Promise<{ ok: boolean; message: string }> {
  const mode = useAppStore.getState().automaticCaptureMode;
  const transport = getActiveDeviceTransport();
  const result = await transport.applyAutomaticCaptureMode(mode);
  return result;
}

/** Refresh battery from transport into store (null stays honest when unknown). */
export async function refreshDeviceBatteryFromTransport(): Promise<void> {
  const transport = getActiveDeviceTransport();
  const report = await transport.readBattery();
  useAppStore.setState({ deviceBatteryPercent: report.percent });
}
