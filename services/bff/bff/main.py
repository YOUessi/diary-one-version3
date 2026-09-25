from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bff.routes import auth_otp, day_revisions, health, jobs, share_recap
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

app.include_router(health.router)
app.include_router(auth_otp.router)
app.include_router(day_revisions.router)
app.include_router(jobs.router)
app.include_router(share_recap.router)
