import type { DeviceTransport } from './deviceTransport';

/**
 * BLE stub until vendor GATT contract lands.
 * Never reports a successful hardware connection — keeps Device honest.
 */
export function createStubBleTransport(): DeviceTransport {
  return {
    kind: 'ble_stub',
    label: 'BLE (awaiting hardware SDK)',
    isAvailable: () => false,
    async scan() {
      return null;
    },
    async connect() {
      return {
        ok: false,
        reason:
          'ble_sdk_unavailable: Expo Go has no Diary One BLE module. Build Dev Client after GATT contract.',
      };
    },
    async disconnect() {},
    async readBattery() {
      return { percent: null, reportedAt: new Date().toISOString() };
    },
    async listPendingRecordings() {
      return { count: 0 };
    },
    async pullRecordings() {
      return { uris: [], message: 'ble_sdk_unavailable' };
    },
    async applyAutomaticCaptureMode() {
      return { ok: false, message: 'ble_sdk_unavailable' };
    },
  };
}
