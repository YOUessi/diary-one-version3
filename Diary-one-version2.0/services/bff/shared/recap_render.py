"""Daily Recap — slideshow MP4 via ffmpeg (9:16, Ken Burns + crossfade)."""
from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path

RECAP_WIDTH = 1080
RECAP_HEIGHT = 1920


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _slide_filter(index: int, fps: int, frames: int) -> str:
    w, h = RECAP_WIDTH, RECAP_HEIGHT
    return (
        f"[{index}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"zoompan=z='min(zoom+0.00035,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s={w}x{h}:fps={fps},format=yuv420p[v{index}]"
    )


def _render_simple_slideshow(
    ffmpeg: str,
    slide_paths: list[Path],
    output_path: Path,
    *,
    fps: int,
    slide_duration_sec: float,
) -> None:
    work = output_path.parent / f"_recap_simple_{uuid.uuid4().hex}"
    work.mkdir(parents=True, exist_ok=True)
    try:
        for i, src in enumerate(slide_paths):
            dest = work / f"slide_{i:03d}.jpg"
            dest.write_bytes(src.read_bytes())
        framerate = 1.0 / slide_duration_sec
        vf = (
            f"scale={RECAP_WIDTH}:{RECAP_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={RECAP_WIDTH}:{RECAP_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,fps={fps}"
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
            str(work / "slide_%03d.jpg"),
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


def render_slideshow_mp4(
    slide_paths: list[Path],
    output_path: Path,
    *,
    fps: int = 24,
    slide_duration_sec: float = 2.5,
    crossfade_sec: float = 0.45,
) -> None:
    if not slide_paths:
        raise ValueError("no_slides")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg_not_installed")

    n = len(slide_paths)
    fps = max(1, min(int(fps), 60))
    slide_duration_sec = max(0.8, min(float(slide_duration_sec), 10.0))
    crossfade_sec = max(0.0, min(float(crossfade_sec), slide_duration_sec * 0.4))
    frames = max(1, int(round(slide_duration_sec * fps)))
    fade = max(0.0, crossfade_sec)

    work = output_path.parent / f"_recap_work_{uuid.uuid4().hex}"
    work.mkdir(parents=True, exist_ok=True)
    staged: list[Path] = []
    try:
        for i, src in enumerate(slide_paths):
            dest = work / f"slide_{i:03d}.jpg"
            dest.write_bytes(src.read_bytes())
            staged.append(dest)

        cmd: list[str] = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
        hold = slide_duration_sec + (fade if n > 1 else 0.0)
        for p in staged:
            cmd.extend(["-loop", "1", "-t", f"{hold:.3f}", "-i", str(p)])

        if n == 1:
            vf = _slide_filter(0, fps, frames).replace("[v0]", "[out]")
            cmd.extend(["-filter_complex", vf, "-map", "[out]"])
        else:
            parts = [_slide_filter(i, fps, frames) for i in range(n)]
            chain = "v0"
            step = slide_duration_sec - fade
            for i in range(1, n):
                nxt = "out" if i == n - 1 else f"xf{i}"
                offset = step * i
                parts.append(
                    f"[{chain}][v{i}]xfade=transition=fade:duration={fade:.3f}:offset={offset:.3f}[{nxt}]"
                )
                chain = nxt
            cmd.extend(["-filter_complex", ";".join(parts), "-map", "[out]"])

        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        )
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "ffmpeg_failed")
    except RuntimeError:
        _render_simple_slideshow(
            ffmpeg,
            slide_paths,
            output_path,
            fps=fps,
            slide_duration_sec=slide_duration_sec,
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
