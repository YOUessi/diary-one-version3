"""Daily Recap video render for Expo Go (requires ffmpeg on PC)."""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from shared.recap_render import ffmpeg_available, render_slideshow_mp4

router = APIRouter()
ROOT = Path(__file__).resolve().parent
RECAP_DIR = ROOT / "data" / "recap_videos"


async def _form_bytes(part: Any) -> bytes:
    if part is None:
        return b""
    if hasattr(part, "read"):
        return await part.read()
    return str(part).encode("utf-8")


@router.post("/v1/share/daily-recap/render")
async def render_daily_recap(request: Request) -> FileResponse:
    if not ffmpeg_available():
        raise HTTPException(
            status_code=503,
            detail="ffmpeg_not_installed: install ffmpeg and add to PATH (see docs/DAILY_RECAP_VIDEO.md)",
        )

    form = await request.form()
    count_raw = await _form_bytes(form.get("slide_count"))
    try:
        slide_count = int(count_raw.decode("utf-8").strip() or "0")
    except ValueError:
        slide_count = 0
    if slide_count <= 0:
        raise HTTPException(status_code=400, detail="slide_count required")

    fps_raw = await _form_bytes(form.get("fps"))
    try:
        fps = int(fps_raw.decode("utf-8").strip() or "24")
    except ValueError:
        fps = 24

    dur_raw = await _form_bytes(form.get("slide_duration_sec"))
    try:
        slide_duration = float(dur_raw.decode("utf-8").strip() or "2.5")
    except ValueError:
        slide_duration = 2.5

    slides: list[bytes] = []
    for i in range(slide_count):
        part = form.get(f"slide_{i}")
        if part is None:
            raise HTTPException(status_code=400, detail=f"slide_{i} missing")
        data = await _form_bytes(part)
        if not data:
            raise HTTPException(status_code=400, detail=f"slide_{i} empty")
        slides.append(data)

    RECAP_DIR.mkdir(parents=True, exist_ok=True)
    job_id = str(uuid.uuid4())
    work_dir = RECAP_DIR / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, blob in enumerate(slides):
        p = work_dir / f"in_{i:03d}.jpg"
        p.write_bytes(blob)
        paths.append(p)

    out = work_dir / "recap.mp4"
    try:
        render_slideshow_mp4(
            paths,
            out,
            fps=max(1, min(fps, 60)),
            slide_duration_sec=max(0.5, min(slide_duration, 10.0)),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return FileResponse(
        path=out,
        media_type="video/mp4",
        filename=f"daily-recap-{job_id[:8]}.mp4",
    )
