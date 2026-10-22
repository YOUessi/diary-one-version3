import redis

from shared.config import settings


def redis_client() -> redis.Redis:
    return redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=None,
    )


def enqueue_job(job_id: str) -> None:
    # Bounded notification channel. Postgres retains the durable pending work.
    with redis_client().pipeline() as pipe:
        pipe.lpush(settings.queue_key, job_id)
        pipe.ltrim(settings.queue_key, 0, 999)
        pipe.execute()


def blocking_pop_job(timeout: int = 5) -> str | None:
    item = redis_client().brpop(settings.queue_key, timeout=timeout)
    if not item:
        return None
    return item[1]
