from fastapi import HTTPException

from shared.sessions import SessionStore


def parse_bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ").strip() or None


def require_api_bearer(
    authorization: str | None,
    api_token: str,
    sessions: SessionStore | None,
    *,
    invalid_status: int = 401,
) -> None:
    """Accept static API_TOKEN (Lab) or OTP session_token.

    Empty API_TOKEN + no Authorization → open (local lab).
    Empty API_TOKEN + invalid Bearer → reject (do not treat garbage as open).
    """
    token = parse_bearer(authorization)
    if not token:
        if not api_token:
            return
        raise HTTPException(status_code=401, detail="unauthorized")

    if api_token and token == api_token:
        return

    if sessions and sessions.resolve_email(token):
        return

    raise HTTPException(status_code=invalid_status, detail="unauthorized")
