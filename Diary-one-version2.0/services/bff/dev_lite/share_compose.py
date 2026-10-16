"""Collage + illustrated still-image render for Expo Go (Pillow on PC)."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import Response

from shared.share_compose import compose_collage, compose_illustrated

router = APIRouter()
ROOT = Path(__file__).resolve().parent
WORK_ROOT = ROOT / "data" / "share_stills"


async def _form_bytes(part: Any) -> bytes:
    if part is None:
        return b""
    if hasattr(part, "read"):
        return await part.read()
    return str(part).encode("utf-8")


def _cleanup(work_dir: Path) -> None:
    shutil.rmtree(work_dir, ignore_errors=True)


@router.post("/v1/share/collage/render")
async def render_collage(request: Request, background_tasks: BackgroundTasks) -> Response:
    form = await request.form()
    count_raw = await _form_bytes(form.get("image_count"))
    try:
        image_count = int(count_raw.decode("utf-8").strip() or "0")
    except ValueError:
        image_count = 0
    if image_count <= 0:
        raise HTTPException(status_code=400, detail="image_count required")

    images: list[bytes] = []
    for i in range(min(image_count, 4)):
        part = form.get(f"image_{i}")
        if part is None:
            raise HTTPException(status_code=400, detail=f"image_{i} missing")
        data = await _form_bytes(part)
        if not data:
            raise HTTPException(status_code=400, detail=f"image_{i} empty")
        images.append(data)

    try:
        jpeg = compose_collage(images)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"collage_failed: {exc}") from exc

    job_id = str(uuid.uuid4())
    work_dir = WORK_ROOT / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "out.jpg").write_bytes(jpeg)
    background_tasks.add_task(_cleanup, work_dir)
    return Response(content=jpeg, media_type="image/jpeg")


@router.post("/v1/share/illustrated/render")
async def render_illustrated(request: Request, background_tasks: BackgroundTasks) -> Response:
    form = await request.form()
    style = (await _form_bytes(form.get("style"))).decode("utf-8").strip() or "A"
    title = (await _form_bytes(form.get("title"))).decode("utf-8").strip()
    part = form.get("image_0")
    if part is None:
        raise HTTPException(status_code=400, detail="image_0 missing")
    data = await _form_bytes(part)
    if not data:
        raise HTTPException(status_code=400, detail="image_0 empty")

    try:
        jpeg = compose_illustrated(data, style, title=title)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"illustrated_failed: {exc}") from exc

    job_id = str(uuid.uuid4())
    work_dir = WORK_ROOT / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "out.jpg").write_bytes(jpeg)
    background_tasks.add_task(_cleanup, work_dir)
    return Response(content=jpeg, media_type="image/jpeg")
