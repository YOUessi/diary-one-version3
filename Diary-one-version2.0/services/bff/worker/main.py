import time
from concurrent.futures import Future, ThreadPoolExecutor

from shared.queue import blocking_pop_job
from shared.quota import worker_max_concurrent
from worker.processor import process_job_sync


def main() -> None:
    max_c = worker_max_concurrent()
    print(f"Diary One worker started — max concurrent={max_c}", flush=True)
    with ThreadPoolExecutor(max_workers=max_c) as pool:
        inflight: set[Future] = set()
        while True:
            done = {f for f in inflight if f.done()}
            for f in done:
                try:
                    f.result()
                except Exception as e:  # noqa: BLE001
                    print(f"Worker task error: {e}", flush=True)
            inflight -= done

            if len(inflight) >= max_c:
                time.sleep(0.4)
                continue

            job_id = blocking_pop_job(timeout=5)
            if not job_id:
                continue
            print(f"Processing job {job_id} (inflight={len(inflight) + 1}/{max_c})", flush=True)
            inflight.add(pool.submit(_run, job_id))


def _run(job_id: str) -> None:
    process_job_sync(job_id)
    print(f"Finished job {job_id}", flush=True)


if __name__ == "__main__":
    main()
