from fastapi import Header, HTTPException

from bff.routes.auth_otp import session_store
from shared.api_auth import require_api_bearer
from shared.config import settings


def require_bearer(authorization: str | None = Header(default=None)) -> None:
    require_api_bearer(
        authorization,
        settings.api_token,
        session_store(),
        invalid_status=401,
    )
