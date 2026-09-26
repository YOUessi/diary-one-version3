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
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.api_auth import require_api_bearer
from shared.otp import OtpMailConfig, OtpRequestBody, OtpService, OtpStore, OtpVerifyBody
from shared.recap_render import ffmpeg_available
from shared.sessions import SessionStore

from dev_lite.job_store import (
    idempotent_reuse_status,
    load_revision_index,
    read_job_meta,
    reload_jobs_from_disk,
    save_revision_index,
    write_job_meta,
)
from dev_lite.semantic_routes import router as semantic_router, semantic_analyze_batch
from dev_lite.share_recap import router as share_recap_router

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
JOBS_DIR = DATA / "jobs"
OTP_PATH = DATA / "otp.json"
SESSIONS_PATH = DATA / "sessions.json"
_revision_index: dict[str, str] = {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT.parent / ".env", extra="ignore")

    api_token: str = "dev-token"
    x02_base_url: str = "http://127.0.0.1:8787"
    x02_token: str = ""
    # 有 SMTP 时必须 false；无 SMTP 时可为 true 仅作应急（商用真测应配 SMTP）
    expose_otp_in_response: bool = True
    otp_ttl_seconds: int = 600
    # 真云默认 false：X02 失败不得用假结果冒充算法质量
    allow_mock_preview: bool = False
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_security: str = "ssl"  # ssl | starttls | none


settings = Settings()
# 配了 SMTP 则默认不回传验证码（仍可被 EXPOSE_OTP_IN_RESPONSE 覆盖）
if settings.smtp_host and os.environ.get("EXPOSE_OTP_IN_RESPONSE") is None:
    settings.expose_otp_in_response = False
bearer = HTTPBearer(auto_error=False)
_jobs: dict[str, dict[str, Any]] = {}
_sessions = SessionStore(SESSIONS_PATH)


def _otp_mail_config() -> OtpMailConfig:
    return OtpMailConfig(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password=settings.smtp_password,
        smtp_from=settings.smtp_from,
        smtp_security=settings.smtp_security,
        otp_ttl_seconds=settings.otp_ttl_seconds,
        expose_otp_in_response=settings.expose_otp_in_response,
        strict_smtp_required=True,
    )


_otp_service = OtpService(_otp_mail_config(), OtpStore(OTP_PATH))


def _ensure_dirs() -> None:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)


async def _form_bytes(part: Any) -> bytes:
    """Starlette may return UploadFile or plain str for multipart fields."""
    if part is None:
        raise HTTPException(status_code=400, detail="missing form field")
    if hasattr(part, "read"):
        return await part.read()
    return str(part).encode("utf-8")


def require_token(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
) -> None:
    header = f"Bearer {creds.credentials}" if creds else None
    require_api_bearer(header, settings.api_token, _sessions, invalid_status=401)


app = FastAPI(title="Diary One Dev Lite BFF", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def access_log(request: Request, call_next):  # type: ignore[no-untyped-def]
    started = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - started) * 1000
    path = request.url.path
    if path != "/health":
        print(
            f"[dev_lite] {request.method} {path} → {response.status_code} ({ms:.0f}ms)",
            flush=True,
        )
    return response


app.include_router(semantic_router)
app.include_router(share_recap_router, dependencies=[Depends(require_token)])


@app.post("/v1/evidence/semantic-analyze")
async def semantic_analyze_multipart(request: Request) -> dict[str, Any]:
    """Accept probe_0, probe_1, … JPEG parts (batch)."""
    form = await request.form()
    files: list[UploadFile] = []
    for key in sorted(form.keys()):
        if not key.startswith("probe_"):
            continue
        part = form[key]
        if hasattr(part, "read"):
            files.append(part)  # type: ignore[arg-type]
    return await semantic_analyze_batch(files)



def _persist_job(job_id: str, job_dir: Path) -> None:
    job = _jobs.get(job_id)
    if not job:
        return
    write_job_meta(job_dir, job)
    rev = str(job.get("day_revision_id") or "").strip()
    if rev:
        _revision_index[rev] = job_id
        save_revision_index(DATA, _revision_index)


def _job_dir_for(job_id: str) -> Path:
    return JOBS_DIR / job_id


def _hydrate_job_from_disk(job_id: str) -> dict[str, Any] | None:
    """Load job into memory from job_meta.json or legacy result.json."""
    if job_id in _jobs:
        return _jobs[job_id]
    job_dir = _job_dir_for(job_id)
    meta = read_job_meta(job_dir)
    if meta:
        _jobs[job_id] = meta
        return meta
    result_path = job_dir / "result.json"
    if result_path.exists():
        meta = {
            "job_id": job_id,
            "day_revision_id": "",
            "status": "succeeded",
            "message": "Loaded from disk",
            "bundle_version": None,
            "result": json.loads(result_path.read_text(encoding="utf-8")),
            "error": None,
        }
        _jobs[job_id] = meta
        return meta
    return None


@app.on_event("startup")
async def startup() -> None:
    global _jobs, _revision_index
    _ensure_dirs()
    _otp_service.mail = _otp_mail_config()
    _jobs, _revision_index = reload_jobs_from_disk(JOBS_DIR, DATA)
    for job_id, job in list(_jobs.items()):
        status = str(job.get("status") or "")
        if status not in ("pending", "processing"):
            continue
        job_dir = _job_dir_for(job_id)
        if not (job_dir / "bundle.json").exists():
            continue
        if status == "processing":
            job["status"] = "pending"
            job["message"] = "Resuming after restart"
            _persist_job(job_id, job_dir)
        asyncio.create_task(_process_job(job_id, job_dir))


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
        "smtp_configured": bool(settings.smtp_host.strip() and settings.smtp_from.strip()),
        "ffmpeg_available": ffmpeg_available(),
        "x02": {
            "base_url": settings.x02_base_url,
            "reachable": x02_ok,
            "detail": x02_detail,
        },
    }


@app.post("/v1/auth/otp/request")
async def otp_request(body: OtpRequestBody) -> dict[str, Any]:
    """ACC03：真 SMTP 发信；未配 SMTP 时仅在 expose_otp 下回传码（不推荐商用验收）。"""
    try:
        out = await _otp_service.request(body.email)
    except RuntimeError as e:
        if str(e) == "smtp_not_configured":
            raise HTTPException(status_code=502, detail="smtp_send_failed:smtp_not_configured") from e
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"smtp_send_failed:{e}") from e
    if out.get("_error") == "smtp_required":
        raise HTTPException(
            status_code=503,
            detail="smtp_required: set SMTP_HOST/SMTP_FROM or temporarily EXPOSE_OTP_IN_RESPONSE=true",
        )
    return out


@app.post("/v1/auth/otp/verify")
async def otp_verify(body: OtpVerifyBody) -> dict[str, Any]:
    result, err = await _otp_service.verify(body.email, body.code, sessions=_sessions)
    if err:
        status = 429 if err == "too_many_attempts" else 400
        raise HTTPException(status_code=status, detail=err)
    return result or {}


@app.post("/v1/day-revisions", dependencies=[Depends(require_token)])
async def create_day_revision(request: Request) -> dict[str, Any]:
    form = await request.form()
    manifest_part = form.get("manifest")
    if manifest_part is None:
        raise HTTPException(status_code=400, detail="manifest required")

    manifest_bytes = await _form_bytes(manifest_part)
    try:
        manifest_json = json.loads(manifest_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"manifest must be JSON: {e}") from e

    rev_field = form.get("day_revision_id")
    if rev_field is None:
        rev_id = f"dayrev_{uuid.uuid4()}"
    elif hasattr(rev_field, "read") or isinstance(rev_field, (str, bytes)):
        rev_id = (await _form_bytes(rev_field)).decode("utf-8").strip() or f"dayrev_{uuid.uuid4()}"
    else:
        rev_id = str(rev_field).strip() or f"dayrev_{uuid.uuid4()}"

    existing_id = _revision_index.get(rev_id)
    if existing_id:
        existing = _jobs.get(existing_id)
        if existing is None:
            meta = read_job_meta(JOBS_DIR / existing_id)
            if meta:
                _jobs[existing_id] = meta
                existing = meta
        if existing and idempotent_reuse_status(str(existing.get("status", ""))):
            return {
                "job_id": existing_id,
                "day_revision_id": rev_id,
                "status": existing.get("status", "pending"),
                "idempotent": True,
            }

    job_id = str(uuid.uuid4())
    job_dir = JOBS_DIR / job_id
    frames_dir = job_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "bundle.json").write_bytes(manifest_bytes)

    profile_part = form.get("app_client_profile")
    if profile_part is not None:
        (job_dir / "app_client_profile.json").write_bytes(await _form_bytes(profile_part))

    for key, part in form.items():
        if key in ("manifest", "app_client_profile", "day_revision_id"):
            continue
        if not (hasattr(part, "read") or isinstance(part, (str, bytes))):
            continue
        frame_bytes = await _form_bytes(part)
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
    _revision_index[rev_id] = job_id
    save_revision_index(DATA, _revision_index)
    _persist_job(job_id, job_dir)

    asyncio.create_task(_process_job(job_id, job_dir))
    return {"job_id": job_id, "day_revision_id": rev_id, "status": "pending"}


@app.get("/v1/jobs/{job_id}", dependencies=[Depends(require_token)])
async def get_job(job_id: str) -> dict[str, Any]:
    job = _hydrate_job_from_disk(job_id)
    if not job:
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
    job["status"] = "processing"
    job["message"] = "Calling X02…"
    _persist_job(job_id, job_dir)
    try:
        result = await _call_x02(job_dir)
        (job_dir / "result.json").write_text(
            json.dumps(result, ensure_ascii=False), encoding="utf-8"
        )
        job["status"] = "succeeded"
        job["message"] = "X02 preview succeeded"
        job["result"] = result
        _persist_job(job_id, job_dir)
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
            _persist_job(job_id, job_dir)
        else:
            job["status"] = "failed"
            job["error"] = str(e)
            job["message"] = "Cloud processing failed"
            _persist_job(job_id, job_dir)


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
