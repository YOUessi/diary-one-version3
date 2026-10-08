/**
 * Device transport contract (SYN01 / BLE readiness).
 * Hardware GATT UUID contract not yet available — StubBle refuses fake success.
 * Lab transport powers Expo Go / internal testing without BLE.
 */

export type DeviceBatteryReport = {
  percent: number | null;
  reportedAt: string;
};

export type PendingRecordingSummary = {
  count: number;
  oldestCapturedAt?: string;
};

export type DeviceTransportKind = 'lab' | 'ble_stub' | 'ble';

export type DeviceTransport = {
  kind: DeviceTransportKind;
  /** Human label for Device settings / Lab. */
  label: string;
  isAvailable(): boolean;
  scan(timeoutMs?: number): Promise<{ deviceId: string; name: string } | null>;
  connect(deviceId: string): Promise<{ ok: true } | { ok: false; reason: string }>;
  disconnect(): Promise<void>;
  readBattery(): Promise<DeviceBatteryReport>;
  listPendingRecordings(): Promise<PendingRecordingSummary>;
  /**
   * Pull recordings into phone cache. Returns local file URIs ready for evidence intake.
   * Stub/lab may return empty — never invent media.
   */
  pullRecordings(): Promise<{ uris: string[]; message: string }>;
  /** Push automatic-capture preference to device firmware (no-op until BLE contract). */
  applyAutomaticCaptureMode(mode: string): Promise<{ ok: boolean; message: string }>;
};

export function transportError(reason: string): never {
  throw new Error(reason);
}
