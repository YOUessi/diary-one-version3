import type { DeviceTransport } from './deviceTransport';

/** Internal lab link — no BLE, no fake battery, sync UI only. */
export function createLabDeviceTransport(): DeviceTransport {
  let linked = false;
  return {
    kind: 'lab',
    label: 'Internal lab link (no BLE)',
    isAvailable: () => true,
    async scan() {
      linked = false;
      return { deviceId: 'lab-device', name: 'Diary One Lab' };
    },
    async connect(deviceId) {
      if (deviceId !== 'lab-device') return { ok: false, reason: 'unknown_lab_device' };
      linked = true;
      return { ok: true };
    },
    async disconnect() {
      linked = false;
    },
    async readBattery() {
      return { percent: null, reportedAt: new Date().toISOString() };
    },
    async listPendingRecordings() {
      return { count: linked ? 1 : 0 };
    },
    async pullRecordings() {
      if (!linked) return { uris: [], message: 'lab_not_linked' };
      return {
        uris: [],
        message: 'Lab link does not transfer hardware recordings — use Evidence Lab import.',
      };
    },
    async applyAutomaticCaptureMode(mode) {
      return {
        ok: linked,
        message: linked
          ? `Lab noted automatic capture preference: ${mode} (not sent to hardware).`
          : 'lab_not_linked',
      };
    },
  };
}
