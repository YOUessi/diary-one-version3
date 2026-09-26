# Diary One Server

商用形态后端：**BFF（FastAPI）+ 异步 Worker + PostgreSQL + Redis + MinIO（S3 兼容）**。

App 在 monorepo：`apps/mobile`。真相源目录：`services/bff`（本目录）。

## 架构

```text
apps/mobile (Expo)
    │  POST /v1/day-revisions (multipart)
    │  GET  /v1/jobs/{id}
    │  POST /v1/auth/otp/* · /v1/share/daily-recap/render
    ▼
BFF :8790 ──► PostgreSQL (jobs)
    │         MinIO (evidence bundles)
    └── Redis queue ──► Worker ──► X02 (:8787)
```

## 推荐：无 Docker 内测（Expo Go）

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\start-dev-lite-background.ps1   # 或 start-dev-lite.ps1 -Adapter fixture
.\scripts\smoke-dev-lite.ps1
.\scripts\smoke-recap.ps1                 # 需本机 ffmpeg
.\scripts\stop-dev-lite.ps1               # 停 8787/8790
```

真云：先 `.\scripts\set-dashscope-key.ps1`，再 `start-dev-lite.ps1`（默认 qwen）。

手机 Lab：`http://<LAN>:8790` · Token `dev-token`。

## Docker 量产栈

```powershell
cd E:\AI耳机\diary-one\services\bff
copy .env.example .env
# 编辑 .env：API_TOKEN、X02_BASE_URL=http://host.docker.internal:8787
docker compose up -d --build
docker compose run --rm bff python -m shared.db_init
.\scripts\smoke-docker.ps1
# Recap（容器内需 ffmpeg — Dockerfile 已装）:
.\scripts\smoke-recap.ps1
```

宿主机改代码不重建镜像：

```powershell
.\scripts\start-bff.ps1
.\scripts\start-worker.ps1
```

更多：`docs/EXPO_GO_DEV_LITE.md` · `docs/DEPLOY.md` · 仓库根 `docs/BACKEND_ROADMAP.md`。

## 环境变量

见 `.env.example`（含 `SMTP_*`、`EXPOSE_OTP_IN_RESPONSE`）。

## 目录

| 路径 | 说明 |
|------|------|
| `bff/` | 对外 HTTP API |
| `worker/` | 队列消费、调 X02 |
| `shared/` | 配置、DB、OTP、sessions、recap |
| `dev_lite/` | 无 Docker 联调 BFF |
| `scripts/` | start/stop/smoke |
