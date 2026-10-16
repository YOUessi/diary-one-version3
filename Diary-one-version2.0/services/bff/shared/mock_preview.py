from __future__ import annotations

import uuid
from typing import Any


def preview_has_no_memories(result: dict[str, Any]) -> bool:
    chapters = result.get("chapters") or []
    ahas = result.get("ahas") or []
    if chapters or ahas:
        return False
    delivery = str(result.get("delivery_state") or "")
    semantic = str(result.get("semantic_day_state") or "")
    if delivery in ("NO_GROUNDED_MEMORY",) or semantic in ("EMPTY_DAY",):
        return True
    outcomes = result.get("selected_memory_outcomes") or []
    return len(outcomes) == 0


def _asset_ids(manifest: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for asset in manifest.get("assets") or []:
        aid = asset.get("asset_id")
        if isinstance(aid, str) and aid:
            out.append(aid)
    return out


def mock_preview_result(manifest: dict[str, Any]) -> dict[str, Any]:
    """Contract-shaped placeholder so Expo Go can write Diary without grounded X02 memories."""
    asset_ids = _asset_ids(manifest)
    n = len(asset_ids)
    hero_id = asset_ids[0] if asset_ids else f"mock-asset-{uuid.uuid4().hex[:8]}"
    selected = asset_ids[: max(1, min(3, n or 1))] or [hero_id]
    ch_id = f"mock-ch-{uuid.uuid4().hex[:8]}"
    aha_id = f"mock-aha-{uuid.uuid4().hex[:8]}"
    title = f"Imported day · {n} asset(s)"
    story = (
        "Cloud pipeline reached X02, but this Evidence day had no grounded memory. "
        "This is a local mock chapter so Expo Go can keep testing Diary / Share."
    )
    return {
        "schema_version": "DIARY_ONE_X02_STAGED_PREVIEW_V04_1",
        "delivery_state": "STAGED_PREVIEW_DELIVERED",
        "semantic_day_state": "HAS_CONTENT",
        "chapters": [
            {
                "id": ch_id,
                "title": title,
                "time_label": "Afternoon",
                "story": story,
                "tags": ["Import", "Dev"],
                "moment_ids": [f"m-{i}" for i in range(len(selected))],
                "hero_asset_id": hero_id,
                "selected_media": [
                    {
                        "asset_id": aid,
                        "source_asset_id": aid,
                        "role": "HERO" if i == 0 else "SUPPORT",
                        "media_kind": "PHOTO",
                        "preview_format": "PHOTO_EVIDENCE",
                        "evidence_frame_ids": [],
                        "quality_score": 1.0,
                        "motifs": [],
                        "observation_id": f"obs-{i}",
                    }
                    for i, aid in enumerate(selected)
                ],
                "publication_status": "STAGED_PREVIEW_VALIDATED",
            }
        ],
        "ahas": [
            {
                "id": aha_id,
                "story": "A small memory from your photo library import (mock).",
                "publication_status": "STAGED_PREVIEW_VALIDATED",
            }
        ],
        "selected_memory_outcomes": [
            {
                "memory_type": "CHAPTER",
                "memory_id": ch_id,
                "visibility_state": "VISIBLE_PREVIEW",
            },
            {
                "memory_type": "AHA",
                "memory_id": aha_id,
                "visibility_state": "VISIBLE_PREVIEW",
            },
        ],
    }
