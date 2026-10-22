from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from shared.config import settings
from shared.models import Base

async_engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"ssl": False},
)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(
    settings.database_url_sync,
    pool_pre_ping=True,
    connect_args={"sslmode": "disable"},
)
SyncSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session() -> Session:
    return SyncSessionLocal()


async def init_db_async() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Existing volumes may predate owner_email; create_all won't ALTER.
        await conn.execute(
            text("ALTER TABLE cloud_jobs ADD COLUMN IF NOT EXISTS owner_email VARCHAR(320)")
        )
        await conn.execute(
            text("ALTER TABLE cloud_jobs ADD COLUMN IF NOT EXISTS input_fingerprint VARCHAR(64)")
        )
