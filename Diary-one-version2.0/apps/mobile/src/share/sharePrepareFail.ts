import { isDevFailSimulationEnabled } from '../config/devFailSimulation';

/** Alternates simulated share-prepare failure when Lab “Simulate failures” is on. */
let sharePrepareFailNext = false;

export function shouldSimulateSharePrepareFailure(): boolean {
  if (!isDevFailSimulationEnabled()) return false;
  if (sharePrepareFailNext) {
    sharePrepareFailNext = false;
    return true;
  }
  sharePrepareFailNext = true;
  return false;
}
