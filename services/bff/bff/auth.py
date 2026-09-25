from fastapi import Header, HTTPException

from shared.config import settings


def require_bearer(authorization: str | None = Header(default=None)) -> None:
    if not settings.api_token:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.api_token:
        raise HTTPException(status_code=403, detail="Invalid token")
