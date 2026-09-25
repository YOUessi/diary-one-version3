import { useAppStore } from '../store/useAppStore';

/** PRD §16 — skip pairing/basics; Device remains honest Not connected. */
export function completeWithoutHardware() {
  useAppStore.getState().setOnboardingComplete(true);
}
