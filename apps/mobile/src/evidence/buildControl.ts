/** Native work already in flight must settle before cancellation is observed. */
export type EvidenceBuildControl = { signal?: AbortSignal; assertCurrent?: () => void };

export function assertEvidenceBuildCurrent(control: EvidenceBuildControl): void {
  if (control.signal?.aborted) {
    const error = new Error('Evidence preparation cancelled');
    error.name = 'AbortError';
    throw error;
  }
  control.assertCurrent?.();
}
