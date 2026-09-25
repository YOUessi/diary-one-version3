import time

from shared.queue import blocking_pop_job
from worker.processor import process_job_sync


def main() -> None:
    print("Diary One worker started — waiting for jobs…")
    while True:
        job_id = blocking_pop_job(timeout=5)
        if not job_id:
            continue
        print(f"Processing job {job_id}")
        process_job_sync(job_id)
        print(f"Finished job {job_id}")


if __name__ == "__main__":
    main()
