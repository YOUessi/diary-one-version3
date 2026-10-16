from fastapi import Header

from bff.routes.auth_otp import session_store
from shared.api_auth import require_api_bearer
from shared.config import settings
from shared.quota import CallerIdentity, resolve_caller


def require_bearer(authorization: str | None = Header(default=None)) -> CallerIdentity:
    require_api_bearer(
        authorization,
        settings.api_token,
        session_store(),
        invalid_status=401,
    )
    return resolve_caller(authorization, settings.api_token, session_store())
