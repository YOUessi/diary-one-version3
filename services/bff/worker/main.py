import time
from concurrent.futures import Future, ThreadPoolExecutor

from shared.queue import blocking_pop_job
from shared.quota import worker_max_concurrent
from worker.processor import process_job_sync, recoverable_job_ids


def main() -> None:
    max_c = worker_max_concurrent()
    print(f"Diary One worker started — max concurrent={max_c}", flush=True)
    with ThreadPoolExecutor(max_workers=max_c) as pool:
        inflight: dict[Future, str] = {}
        next_scan = 0.0
        while True:
            done = {f for f in inflight if f.done()}
            for f in done:
                try:
                    f.result()
                except Exception as e:  # noqa: BLE001
                    print(f"Worker task error: {e}", flush=True)
            for f in done:
                del inflight[f]

            if len(inflight) >= max_c:
                time.sleep(0.4)
                continue

            # Database scan repairs both a lost Redis notification and a worker crash.
            if time.monotonic() >= next_scan:
                try:
                    for candidate in recoverable_job_ids(max_c):
                        if candidate in inflight.values() or len(inflight) >= max_c:
                            continue
                        inflight[pool.submit(_run, candidate)] = candidate
                except Exception as e:  # noqa: BLE001
                    print(f"Recovery scan failed: {e}", flush=True)
                next_scan = time.monotonic() + 5
                if len(inflight) >= max_c:
                    continue
            try:
                job_id = blocking_pop_job(timeout=1)
            except Exception as e:  # noqa: BLE001
                print(f"Redis unavailable; using durable job scan: {e}", flush=True)
                time.sleep(1)
                continue
            if not job_id:
                continue
            if job_id in inflight.values():
                continue
            print(f"Processing job {job_id} (inflight={len(inflight) + 1}/{max_c})", flush=True)
            inflight[pool.submit(_run, job_id)] = job_id


def _run(job_id: str) -> None:
    process_job_sync(job_id)
    print(f"Finished job {job_id}", flush=True)


if __name__ == "__main__":
    main()
