type Releasable = { session: { release(): Promise<void> } };

export function throwIfAnalysisCancelled(signal?: AbortSignal): void {
  if (!signal?.aborted) return;
  const error = new Error('MobileCLIP analysis cancelled');
  error.name = 'AbortError';
  throw error;
}

/** One session and one in-flight inference per JS runtime. All release calls run
 * after inference settles, never from native-runtime destruction or an HMR hook. */
export function createSessionLifecycle<T extends Releasable>() {
  let queue: Promise<unknown> = Promise.resolve();
  let resource: T | undefined;
  let cleanupFailure: unknown;

  async function release() {
    if (resource) {
      try {
        await resource.session.release();
      } catch (error) {
        cleanupFailure = error;
        throw error;
      }
      resource = undefined;
    }
    cleanupFailure = undefined;
  }

  function enqueue<R>(operation: () => Promise<R>): Promise<R> {
    const pending = queue.then(operation);
    queue = pending.catch(() => undefined);
    return pending;
  }

  return {
    run<R>(load: () => Promise<T>, operation: (loaded: T) => Promise<R>, signal?: AbortSignal): Promise<R> {
      return enqueue(async () => {
        throwIfAnalysisCancelled(signal);
        if (cleanupFailure) throw new Error('MobileCLIP session cleanup failed; restart the app before retrying.');
        if (!resource) resource = await load();
        throwIfAnalysisCancelled(signal);
        try {
          const result = await operation(resource);
          throwIfAnalysisCancelled(signal);
          return result;
        } catch (error) {
          // A rejected native run/invalid output may leave the session unusable.
          // Never overlap its release with a still-pending run or swallow the
          // original failure. Aborts also release only after that run settles.
          try { await release(); } catch { /* Block subsequent runs until cleanup succeeds. */ }
          throw error;
        }
      });
    },
    release: () => enqueue(release),
  };
}
