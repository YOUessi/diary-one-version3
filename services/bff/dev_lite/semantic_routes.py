"""
Dev Lite evidence semantic endpoints.

- POST /v1/evidence/semantic-analyze — JPEG probes → vectors + labels
    Windows: MobileCLIP via diary_one_app_evidence_v0_2_dev8_mobileclip_router
    when DIARY_ONE_MOBILECLIP_CHECKPOINT is set
- POST /v1/evidence/semantic-route — stateless audit echo (routing authority stays on phone TS)
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel, Field

from dev_lite.mobileclip_backend import (
    analyze_jpeg_bytes,
    ensure_reference_on_path,
    get_embedder,
    mobileclip_status,
)

router = APIRouter(prefix="/v1/evidence", tags=["evidence"])

EVIDENCE_ROUTER_ROOT = Path(__file__).resolve().parents[2] / "evidence-router"


class SemanticClassificationIn(BaseModel):
    identifier: str
    confidence: float = Field(ge=0.0, le=1.0)


class SemanticProbeIn(BaseModel):
    requested_ms: int = 0
    actual_pts_ms: int = 0
    vector: list[float]
    classifications: list[SemanticClassificationIn] = Field(default_factory=list)
    mean_luma: float | None = None
    dark_pixel_ratio: float | None = None
    sharpness: float | None = None
    eligible_for_selection: bool = True
    quality_reason_codes: list[str] = Field(default_factory=list)


class SemanticRouteRequest(BaseModel):
    duration_ms: int = Field(gt=0)
    profile_id: str = "APPLE_VISION_SEMANTIC_GATE_V07"
    model_id: str = "APPLE_VISION_FEATURE_PRINT_REVISION_2"
    analyzer_degraded: bool = False
    probes: list[SemanticProbeIn] = Field(min_length=1)


def _try_import_reference_router() -> Any | None:
    ensure_reference_on_path()
    try:
        from diary_one_app.engine.semantic import SemanticProbeEngine  # type: ignore

        return SemanticProbeEngine
    except Exception:
        return None


@router.post("/semantic-route")
async def semantic_route(body: SemanticRouteRequest) -> dict[str, Any]:
    """Stateless audit: echoes probe count; authoritative routing runs on device TS."""
    profile_path = EVIDENCE_ROUTER_ROOT / "semantic_profile_defaults.json"
    profile_defaults: dict[str, Any] = {}
    if profile_path.is_file():
        profile_defaults = json.loads(profile_path.read_text(encoding="utf-8"))
    reference = _try_import_reference_router()
    mc = mobileclip_status()
    return {
        "ok": True,
        "platform": platform.system(),
        "python": sys.version.split()[0],
        "probe_count": len(body.probes),
        "model_id": body.model_id,
        "analyzer_degraded": body.analyzer_degraded,
        "profile_id": body.profile_id,
        "profile_defaults_keys": list(profile_defaults.keys()),
        "reference_router_importable": reference is not None,
        "mobileclip": mc,
        "message": (
            "Authoritative semantic routing runs in apps/mobile TypeScript. "
            "On Windows, probe embeddings come from MobileCLIP via "
            "POST /v1/evidence/semantic-analyze when the checkpoint is configured."
        ),
        "target_frame_hint": min(10, max(1, len(body.probes))),
    }


async def semantic_analyze_batch(files: list[UploadFile]) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="no probes uploaded")

    # Prefer MobileCLIP whenever checkpoint is configured (Windows + any OS).
    embedder = get_embedder()
    if embedder is not None:
        blobs: list[bytes] = []
        for part in files:
            raw = await part.read()
            if not raw:
                raise HTTPException(status_code=400, detail="empty probe upload")
            blobs.append(raw)
        try:
            return analyze_jpeg_bytes(blobs)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=f"MobileCLIP analyze failed: {exc}") from exc

    st = mobileclip_status()
    if platform.system() == "Windows":
        raise HTTPException(
            status_code=501,
            detail=(
                "MobileCLIP not ready on Windows Dev Lite. "
                f"reason={st.get('reason')}. "
                "Set DIARY_ONE_MOBILECLIP_CHECKPOINT to mobileclip_s0.pt, install "
                "torch/timm/pillow (+ optional apple/ml-mobileclip for prompts), "
                "restart BFF. See docs/WINDOWS_MOBILECLIP_BFF.md"
            ),
        )
    raise HTTPException(
        status_code=501,
        detail=(
            "No semantic analyzer configured. On Windows use MobileCLIP checkpoint; "
            "on iPhone use DiaryOneVision Dev Client; "
            f"status={st.get('reason')}"
        ),
    )
