from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://diary:diary@localhost:5432/diary_one"
    database_url_sync: str = "postgresql+psycopg://diary:diary@localhost:5432/diary_one"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "diary-evidence"
    minio_secure: bool = False
    api_token: str = "dev-token"
    x02_base_url: str = "http://127.0.0.1:8787"
    x02_token: str = ""
    queue_key: str = "diary:cloud_jobs"
    # Default false — OTP in JSON is a lab convenience only (PRI04).
    expose_otp_in_response: bool = False
    otp_ttl_seconds: int = 600
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_security: str = "ssl"
    # PRD AI03 — mock chapters must never be the commercial default.
    allow_mock_preview: bool = False
    day_revision_daily_limit: int = 8
    day_revision_max_inflight: int = 2
    worker_max_concurrent: int = 1


settings = Settings()

# Align with Dev Lite: SMTP configured → do not echo OTP unless env overrides.
if settings.smtp_host.strip() and os.environ.get("EXPOSE_OTP_IN_RESPONSE") is None:
    settings.expose_otp_in_response = False
