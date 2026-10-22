import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from bff.routes import account, auth_otp, day_revisions, evidence, health, jobs, share_compose, share_recap
from shared.db import init_db_async
from shared.storage import ensure_bucket, minio_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db_async()
    ensure_bucket(minio_client())
    yield


app = FastAPI(title="Diary One BFF", version="0.1.0", lifespan=lifespan)

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
            f"[bff] {request.method} {path} → {response.status_code} ({ms:.0f}ms)",
            flush=True,
        )
    return response


app.include_router(health.router)
app.include_router(auth_otp.router)
app.include_router(account.router)
app.include_router(day_revisions.router)
app.include_router(jobs.router)
app.include_router(share_recap.router)
app.include_router(share_compose.router)
app.include_router(evidence.router)
