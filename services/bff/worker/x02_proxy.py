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
        if health_json.get("modelReady") is False:
            raise RuntimeError(
                "X02ModelNotReady: DashScope/qwen adapter not ready — set DASHSCOPE_API_KEY on the X02 host"
            )
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

        attached: set[str] = set()
        for asset in manifest.get("assets") or []:
            for frame in asset.get("frames") or []:
                frame_id = str(frame.get("frame_id") or "")
                rel = str(frame.get("relative_path") or "")
                if not frame_id:
                    continue
                candidates = []
                if rel:
                    candidates.append(bundle_dir / rel)
                candidates.append(bundle_dir / "frames" / f"{frame_id}.jpg")
                local = next((path for path in candidates if path.exists()), None)
                if local is None:
                    raise FileNotFoundError(f"Evidence frame missing for {frame_id}")
                files.append((frame_id, (local.name, local.read_bytes(), "image/jpeg")))
                attached.add(frame_id)

        if not attached:
            raise FileNotFoundError("No Evidence frames found to send to X02")

        res = await client.post(url, headers=headers, files=files)
        if res.is_error:
            detail = res.text[:2000]
            try:
                payload = res.json()
                message = payload.get("message") or payload.get("error") or detail
                code = payload.get("code") or payload.get("error") or str(res.status_code)
                raise RuntimeError(f"X02 {res.status_code} {code}: {message}")
            except RuntimeError:
                raise
            except Exception:
                raise RuntimeError(f"X02 {res.status_code}: {detail}") from None
        return res.json()
