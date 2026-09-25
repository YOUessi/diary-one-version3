/** Alternates simulated share-prepare failure (Figma failed states · test build). */
let sharePrepareFailNext = false;

export function shouldSimulateSharePrepareFailure(): boolean {
  if (sharePrepareFailNext) {
    sharePrepareFailNext = false;
    return true;
  }
  sharePrepareFailNext = true;
  return false;
}
