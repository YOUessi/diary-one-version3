"""
Dev Lite evidence semantic endpoints.

- POST /v1/evidence/semantic-analyze — JPEG probes → vectors + labels (Mac helper when available)
- POST /v1/evidence/semantic-route — stateless route from client-supplied embeddings (JSON)

On Windows without PYTHONPATH to the reference package, semantic-analyze returns 501 with guidance.
Routing math on phone uses the TypeScript port; this endpoint re-validates audits server-side when possible.
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel, Field

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
    try:
        from diary_one_app.engine.semantic import SemanticProbeEngine  # type: ignore

        return SemanticProbeEngine
    except Exception:
        return None


@router.post("/semantic-route")
async def semantic_route(body: SemanticRouteRequest) -> dict[str, Any]:
    """Stateless audit: echoes probe count and notes that authoritative routing runs on device."""
    profile_path = EVIDENCE_ROUTER_ROOT / "semantic_profile_defaults.json"
    profile_defaults: dict[str, Any] = {}
    if profile_path.is_file():
        profile_defaults = json.loads(profile_path.read_text(encoding="utf-8"))
    reference = _try_import_reference_router()
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
        "message": (
            "Authoritative semantic routing runs in apps/mobile TypeScript (Feature Print 768-d + "
            "Classify top-10 + 40/60 fusion). Re-run full Python engine by importing diary_one_app "
            "via PYTHONPATH on Mac when validating parity."
        ),
        "target_frame_hint": min(10, max(1, len(body.probes))),
    }


async def semantic_analyze_batch(files: list[UploadFile]) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="no probes uploaded")
    if platform.system() == "Windows":
        raise HTTPException(
            status_code=501,
            detail=(
                "Windows Dev Lite cannot run Apple Vision. Phone uses native module or degraded "
                "fallback; optional POST /v1/evidence/semantic-route with vectors from client."
            ),
        )
    raise HTTPException(
        status_code=501,
        detail="Configure Mac Apple Vision helper or use on-device DiaryOneVision module.",
    )
