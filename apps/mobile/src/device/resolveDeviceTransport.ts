import { createLabDeviceTransport } from './labDeviceTransport';
import { createStubBleTransport } from './stubBleTransport';
import type { DeviceTransport } from './deviceTransport';
import { useAppStore } from '../store/useAppStore';

let active: DeviceTransport | null = null;

/** Resolve transport from current link state (lab vs future BLE). */
export function getActiveDeviceTransport(): DeviceTransport {
  const link = useAppStore.getState().deviceLinkState;
  if (link === 'lab_linked') {
    if (!active || active.kind !== 'lab') {
      active = createLabDeviceTransport();
    }
    return active;
  }
  if (link === 'hardware_linked') {
    // Future: return real BLE transport instance held after pair.
    if (!active || active.kind === 'lab') {
      active = createStubBleTransport();
    }
    return active;
  }
  return createStubBleTransport();
}

export function setActiveDeviceTransport(t: DeviceTransport | null) {
  active = t;
}

export function createTransportForPairing(preferLab: boolean): DeviceTransport {
  return preferLab ? createLabDeviceTransport() : createStubBleTransport();
}
