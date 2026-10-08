/**
 * Opt-in Figma failed-state simulation for Expo Go.
 * Default OFF so commercial test paths (Share / Save / Search) succeed on first try.
 * Toggle from Internal Lab when exercising failed boards.
 */
let enabled = false;

export function isDevFailSimulationEnabled(): boolean {
  return __DEV__ && enabled;
}

export function setDevFailSimulationEnabled(on: boolean): void {
  enabled = on;
}
