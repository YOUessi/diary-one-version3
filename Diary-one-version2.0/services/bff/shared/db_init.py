"""Create tables and ensure MinIO bucket exists."""

import asyncio

from minio import Minio

from shared.config import settings
from shared.db import init_db_async
from shared.storage import ensure_bucket


def main() -> None:
    asyncio.run(init_db_async())
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
    ensure_bucket(client)
    print("Database and MinIO bucket ready.")


if __name__ == "__main__":
    main()
