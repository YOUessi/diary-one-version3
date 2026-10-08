import httpx
from fastapi import APIRouter

from shared.config import settings
from shared.recap_render import ffmpeg_available

router = APIRouter()


@router.get("/health")
async def health():
    x02_ok = False
    x02_detail: dict = {}
    try:
        headers = {"Accept": "application/json"}
        if settings.x02_token:
            headers["Authorization"] = f"Bearer {settings.x02_token}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{settings.x02_base_url.rstrip('/')}/health", headers=headers)
            x02_ok = r.is_success
            if r.is_success:
                try:
                    body = r.json()
                    if isinstance(body, dict):
                        x02_detail = {
                            "modelReady": body.get("modelReady"),
                            "adapter": body.get("adapter") or body.get("mode"),
                        }
                except Exception:  # noqa: BLE001
                    pass
    except Exception:  # noqa: BLE001
        x02_ok = False

    smtp_configured = bool(settings.smtp_host.strip() and settings.smtp_from.strip())
    return {
        "status": "ok",
        "service": "diary-one-bff",
        "version": "0.1.0",
        "mode": "production",
        "ffmpeg_available": ffmpeg_available(),
        "smtp_configured": smtp_configured,
        "expose_otp_in_response": settings.expose_otp_in_response,
        "x02": {"base_url": settings.x02_base_url, "reachable": x02_ok, **x02_detail},
        "allow_mock_preview": settings.allow_mock_preview,
    }
