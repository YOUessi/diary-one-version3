import io
import json
from pathlib import Path

from minio import Minio

from shared.config import settings


def minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket(client: Minio) -> None:
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)


def upload_bytes(client: Minio, object_name: str, data: bytes, content_type: str) -> None:
    ensure_bucket(client)
    client.put_object(
        settings.minio_bucket,
        object_name,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def upload_json(client: Minio, object_name: str, payload: dict) -> None:
    raw = json.dumps(payload).encode("utf-8")
    upload_bytes(client, object_name, raw, "application/json")


def download_bytes(client: Minio, object_name: str) -> bytes:
    resp = client.get_object(settings.minio_bucket, object_name)
    try:
        return resp.read()
    finally:
        resp.close()
        resp.release_conn()


def download_to_dir(client: Minio, prefix: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for obj in client.list_objects(settings.minio_bucket, prefix=prefix, recursive=True):
        name = obj.object_name
        if not name or name.endswith("/"):
            continue
        rel = name[len(prefix) :].lstrip("/")
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        data = download_bytes(client, name)
        target.write_bytes(data)
