from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "diary-one-bff",
        "version": "0.1.0",
    }
