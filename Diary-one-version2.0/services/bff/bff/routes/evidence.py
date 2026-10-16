"""Evidence semantic endpoints for production BFF (same contract as Dev Lite)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, UploadFile

from bff.auth import require_bearer
from dev_lite.semantic_routes import router as semantic_router
from dev_lite.semantic_routes import semantic_analyze_batch

router = APIRouter(dependencies=[Depends(require_bearer)])
router.include_router(semantic_router)


@router.post("/v1/evidence/semantic-analyze")
async def semantic_analyze_multipart(request: Request) -> dict[str, Any]:
    form = await request.form()
    files: list[UploadFile] = []
    for key in sorted(form.keys()):
        if not key.startswith("probe_"):
            continue
        part = form[key]
        if hasattr(part, "read"):
            files.append(part)  # type: ignore[arg-type]
    return await semantic_analyze_batch(files)
