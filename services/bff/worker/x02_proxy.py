import json
from pathlib import Path

import httpx

from shared.config import settings


async def run_x02_preview(bundle_dir: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = settings.x02_base_url.rstrip("/")
    headers = {"Accept": "application/json"}
    if settings.x02_token:
        headers["Authorization"] = f"Bearer {settings.x02_token}"

    async with httpx.AsyncClient(timeout=httpx.Timeout(900.0)) as client:
        health = await client.get(f"{base}/health", headers=headers)
        health.raise_for_status()
        health_json = health.json()
        preview_path = health_json.get("previewPath") or "/x02/v0.4.1/preview"
        if not preview_path.startswith("/"):
            preview_path = f"/{preview_path}"
        url = f"{base}{preview_path}"

        files: list[tuple[str, tuple[str, bytes, str]]] = []
        files.append(
            (
                "manifest",
                ("bundle.json", manifest_path.read_bytes(), "application/json"),
            )
        )

        profile_path = bundle_dir / "app_client_profile.json"
        if profile_path.exists():
            files.append(
                (
                    "app_client_profile",
                    (
                        "app_client_profile.json",
                        profile_path.read_bytes(),
                        "application/json",
                    ),
                )
            )

        frames_dir = bundle_dir / "frames"
        if frames_dir.exists():
            for frame_file in sorted(frames_dir.glob("*.jpg")):
                frame_id = frame_file.stem
                files.append(
                    (frame_id, (frame_file.name, frame_file.read_bytes(), "image/jpeg")),
                )
        else:
            for asset in manifest.get("assets", []):
                for frame in asset.get("frames", []):
                    rel = frame.get("relative_path", "")
                    frame_id = frame.get("frame_id", "")
                    local = bundle_dir / rel if rel else None
                    if local and local.exists() and frame_id:
                        files.append(
                            (frame_id, (local.name, local.read_bytes(), "image/jpeg")),
                        )

        res = await client.post(url, headers=headers, files=files)
        res.raise_for_status()
        return res.json()
