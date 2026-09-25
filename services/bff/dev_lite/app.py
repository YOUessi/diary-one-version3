"""
Diary One · Dev Lite BFF（无 Docker）

手机 Expo Go → http://<LAN>:8790
  ├─ POST /v1/auth/otp/request|verify
  ├─ POST /v1/day-revisions  → 磁盘存包 → 后台调本机 X02 :8787
  └─ GET  /v1/jobs/{id}

算法服必须绑 127.0.0.1:8787（无需 TLS）。本服务对外 0.0.0.0:8790。
"""
from __future__ import annotations

import asyncio
import json
import os
import random
import secrets
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
JOBS_DIR = DATA / "jobs"
OTP_PATH = DATA / "otp.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT.parent / ".env", extra="ignore")

    api_token: str = "dev-token"
    x02_base_url: str = "http://127.0.0.1:8787"
    x02_token: str = ""
    # Expo Go 内测：响应里带回验证码，无需真实发信；量产务必 false
    expose_otp_in_response: bool = True
    otp_ttl_seconds: int = 600
    # X02 不可达时返回合同形状假结果，仅测 App 管线；非算法质量证据
    allow_mock_preview: bool = True


settings = Settings()
bearer = HTTPBearer(auto_error=False)
_jobs: dict[str, dict[str, Any]] = {}
_otp: dict[str, dict[str, Any]] = {}
_lock = asyncio.Lock()


def _ensure_dirs() -> None:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)


def _load_otp() -> None:
    global _otp
    if OTP_PATH.exists():
        try:
            _otp = json.loads(OTP_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            _otp = {}


def _save_otp() -> None:
    OTP_PATH.write_text(json.dumps(_otp, ensure_ascii=False, indent=2), encoding="utf-8")


def require_token(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
) -> None:
    if not settings.api_token:
        return
    if creds is None or creds.credentials != settings.api_token:
        raise HTTPException(status_code=401, detail="unauthorized")


app = FastAPI(title="Diary One Dev Lite BFF", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    _ensure_dirs()
    _load_otp()


@app.get("/health")
async def health() -> dict[str, Any]:
    x02_ok = False
    x02_detail: Any = None
    try:
        headers = {"Accept": "application/json"}
        if settings.x02_token:
            headers["Authorization"] = f"Bearer {settings.x02_token}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{settings.x02_base_url.rstrip('/')}/health", headers=headers)
            x02_ok = r.is_success
            if r.is_success:
                x02_detail = r.json()
    except Exception as e:  # noqa: BLE001
        x02_detail = {"error": str(e)}

    return {
        "status": "ok",
        "mode": "dev_lite",
        "docker_required": False,
        "api_token_required": bool(settings.api_token),
        "expose_otp_in_response": settings.expose_otp_in_response,
        "allow_mock_preview": settings.allow_mock_preview,
        "x02": {
            "base_url": settings.x02_base_url,
            "reachable": x02_ok,
            "detail": x02_detail,
        },
    }


class OtpRequest(BaseModel):
    email: str = Field(min_length=3)


class OtpVerify(BaseModel):
    email: str = Field(min_length=3)
    code: str = Field(min_length=4, max_length=12)


@app.post("/v1/auth/otp/request")
async def otp_request(body: OtpRequest) -> dict[str, Any]:
    """ACC03 内测：生成 6 位码。默认在 JSON 返回，便于 Expo Go 无邮箱通道验收。"""
    email = body.email.strip().lower()
    code = f"{random.randint(0, 999999):06d}"
    async with _lock:
        _otp[email] = {
            "code": code,
            "expires_at": time.time() + settings.otp_ttl_seconds,
            "attempts": 0,
        }
        _save_otp()

    out: dict[str, Any] = {
        "ok": True,
        "email": email,
        "message": "OTP issued for internal beta. Use code from response when expose_otp is on.",
        "ttl_seconds": settings.otp_ttl_seconds,
    }
    if settings.expose_otp_in_response:
        out["dev_code"] = code
        out["delivery"] = "response_only"
    else:
        out["delivery"] = "email_not_configured"
    return out


@app.post("/v1/auth/otp/verify")
async def otp_verify(body: OtpVerify) -> dict[str, Any]:
    email = body.email.strip().lower()
    digits = "".join(c for c in body.code if c.isdigit())
    async with _lock:
        entry = _otp.get(email)
        if not entry:
            raise HTTPException(status_code=400, detail="no_otp_requested")
        if time.time() > float(entry["expires_at"]):
            raise HTTPException(status_code=400, detail="otp_expired")
        entry["attempts"] = int(entry.get("attempts", 0)) + 1
        if entry["attempts"] > 8:
            raise HTTPException(status_code=429, detail="too_many_attempts")
        if digits != entry["code"]:
            _save_otp()
            raise HTTPException(status_code=400, detail="invalid_code")
        del _otp[email]
        _save_otp()

    session_token = secrets.token_urlsafe(24)
    return {
        "ok": True,
        "email": email,
        "session_token": session_token,
        "profile": {"email": email, "nickname": email.split("@")[0] or "Guest"},
    }


@app.post("/v1/day-revisions", dependencies=[Depends(require_token)])
async def create_day_revision(request: Request) -> dict[str, Any]:
    form = await request.form()
    manifest_part = form.get("manifest")
    if manifest_part is None:
        raise HTTPException(status_code=400, detail="manifest required")

    manifest_bytes = await manifest_part.read()
    try:
        manifest_json = json.loads(manifest_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"manifest must be JSON: {e}") from e

    rev_field = form.get("day_revision_id")
    if rev_field is None:
        rev_id = f"dayrev_{uuid.uuid4()}"
    elif hasattr(rev_field, "read"):
        rev_id = (await rev_field.read()).decode("utf-8").strip() or f"dayrev_{uuid.uuid4()}"
    else:
        rev_id = str(rev_field).strip() or f"dayrev_{uuid.uuid4()}"

    job_id = str(uuid.uuid4())
    job_dir = JOBS_DIR / job_id
    frames_dir = job_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "bundle.json").write_bytes(manifest_bytes)

    profile_part = form.get("app_client_profile")
    if profile_part is not None and hasattr(profile_part, "read"):
        (job_dir / "app_client_profile.json").write_bytes(await profile_part.read())

    for key, part in form.items():
        if key in ("manifest", "app_client_profile", "day_revision_id"):
            continue
        if not hasattr(part, "read"):
            continue
        frame_bytes = await part.read()
        (frames_dir / f"{key}.jpg").write_bytes(frame_bytes)

    _jobs[job_id] = {
        "job_id": job_id,
        "day_revision_id": rev_id,
        "status": "pending",
        "message": "Queued (dev_lite)",
        "bundle_version": manifest_json.get("bundle_version"),
        "result": None,
        "error": None,
    }

    asyncio.create_task(_process_job(job_id, job_dir))
    return {"job_id": job_id, "day_revision_id": rev_id, "status": "pending"}


@app.get("/v1/jobs/{job_id}", dependencies=[Depends(require_token)])
async def get_job(job_id: str) -> dict[str, Any]:
    job = _jobs.get(job_id)
    if not job:
        # cold restart: look for result file
        result_path = JOBS_DIR / job_id / "result.json"
        if result_path.exists():
            result = json.loads(result_path.read_text(encoding="utf-8"))
            return {
                "job_id": job_id,
                "status": "succeeded",
                "message": "Loaded from disk",
                "result": result,
            }
        raise HTTPException(status_code=404, detail="Job not found")

    body: dict[str, Any] = {
        "job_id": job["job_id"],
        "status": job["status"],
        "message": job["message"],
        "day_revision_id": job["day_revision_id"],
    }
    if job["status"] == "succeeded" and job.get("result"):
        body["result"] = job["result"]
    if job["status"] == "failed":
        body["message"] = job.get("error") or job.get("message") or "failed"
    return body


def _mock_preview(manifest: dict[str, Any]) -> dict[str, Any]:
    """合同形状占位：仅用于无 X02 / 无 Key 时验 App 写回。"""
    n = len(manifest.get("assets") or [])
    ch_id = f"mock-ch-{uuid.uuid4().hex[:8]}"
    aha_id = f"mock-aha-{uuid.uuid4().hex[:8]}"
    title = f"Imported day · {n} asset(s)"
    story = "Dev lite mock preview. Start X02 with a DashScope key for real V1.75 output."
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
                "moment_ids": [f"m-{i}" for i in range(max(1, min(3, n or 1)))],
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


async def _call_x02(job_dir: Path) -> dict[str, Any]:
    manifest_path = job_dir / "bundle.json"
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

        files: list[tuple[str, tuple[str, bytes, str]]] = [
            ("manifest", ("bundle.json", manifest_path.read_bytes(), "application/json")),
        ]
        profile = job_dir / "app_client_profile.json"
        if profile.exists():
            files.append(
                (
                    "app_client_profile",
                    ("app_client_profile.json", profile.read_bytes(), "application/json"),
                )
            )
        frames_dir = job_dir / "frames"
        if frames_dir.exists():
            for frame_file in sorted(frames_dir.glob("*.jpg")):
                files.append(
                    (
                        frame_file.stem,
                        (frame_file.name, frame_file.read_bytes(), "image/jpeg"),
                    )
                )

        res = await client.post(f"{base}{preview_path}", headers=headers, files=files)
        res.raise_for_status()
        return res.json()


async def _process_job(job_id: str, job_dir: Path) -> None:
    job = _jobs[job_id]
    job["status"] = "running"
    job["message"] = "Calling X02…"
    try:
        result = await _call_x02(job_dir)
        (job_dir / "result.json").write_text(
            json.dumps(result, ensure_ascii=False), encoding="utf-8"
        )
        job["status"] = "succeeded"
        job["message"] = "X02 preview succeeded"
        job["result"] = result
    except Exception as e:  # noqa: BLE001
        if settings.allow_mock_preview:
            manifest = json.loads((job_dir / "bundle.json").read_text(encoding="utf-8"))
            result = _mock_preview(manifest)
            result["dev_lite_fallback"] = True
            result["dev_lite_x02_error"] = str(e)
            (job_dir / "result.json").write_text(
                json.dumps(result, ensure_ascii=False), encoding="utf-8"
            )
            job["status"] = "succeeded"
            job["message"] = f"Mock preview (X02 unavailable: {e})"
            job["result"] = result
        else:
            job["status"] = "failed"
            job["error"] = str(e)
            job["message"] = "Cloud processing failed"


def main() -> None:
    import uvicorn

    host = os.environ.get("DEV_LITE_HOST", "0.0.0.0")
    port = int(os.environ.get("DEV_LITE_PORT", "8790"))
    print(
        f"Dev Lite BFF on http://{host}:{port} · token={settings.api_token!r} · "
        f"X02={settings.x02_base_url} · expose_otp={settings.expose_otp_in_response}",
        flush=True,
    )
    uvicorn.run(
        "dev_lite.app:app",
        host=host,
        port=port,
        reload=False,
        app_dir=str(ROOT.parent),
    )


if __name__ == "__main__":
    main()
