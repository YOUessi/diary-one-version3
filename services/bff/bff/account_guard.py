from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from bff.auth import require_bearer


async def lock_account(session: AsyncSession, email: str, request: Request) -> None:
    """Serialize account writes and revalidate sessions after waiting for the lock."""
    await session.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:owner, 0))"), {"owner": email})
    require_bearer(request.headers.get("authorization"))
