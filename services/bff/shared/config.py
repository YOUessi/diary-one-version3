from pydantic_settings import BaseSettings, SettingsConfigDict


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
    expose_otp_in_response: bool = True
    otp_ttl_seconds: int = 600
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_security: str = "ssl"


settings = Settings()
