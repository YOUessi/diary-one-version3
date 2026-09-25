"""Daily Recap — slideshow MP4 via ffmpeg (9:16)."""
from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path

RECAP_WIDTH = 1080
RECAP_HEIGHT = 1920


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def render_slideshow_mp4(
    slide_paths: list[Path],
    output_path: Path,
    *,
    fps: int = 24,
    slide_duration_sec: float = 2.5,
) -> None:
    if not slide_paths:
        raise ValueError("no_slides")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg_not_installed")

    work = output_path.parent / f"_recap_work_{uuid.uuid4().hex}"
    work.mkdir(parents=True, exist_ok=True)
    try:
        for i, src in enumerate(slide_paths):
            dest = work / f"slide_{i:03d}.jpg"
            dest.write_bytes(src.read_bytes())

        input_pattern = str(work / "slide_%03d.jpg")
        framerate = 1.0 / slide_duration_sec if slide_duration_sec > 0 else 0.4
        vf = (
            f"scale={RECAP_WIDTH}:{RECAP_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={RECAP_WIDTH}:{RECAP_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"fps={fps}"
        )
        cmd = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            str(framerate),
            "-start_number",
            "0",
            "-i",
            input_pattern,
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "ffmpeg_failed")
    finally:
        shutil.rmtree(work, ignore_errors=True)
