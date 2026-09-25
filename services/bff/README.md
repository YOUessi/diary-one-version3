# Diary One Server

商用形态后端：**BFF（FastAPI）+ 异步 Worker + PostgreSQL + Redis + MinIO（S3 兼容）**。

与移动端 **`../diary-one-app`** 分离；App 使用 **Production BFF** 模式对接本服务。

## 架构

```text
diary-one-app (Expo)
    │  POST /v1/day-revisions (multipart)
    │  GET  /v1/jobs/{id}
    ▼
BFF :8790 ──► PostgreSQL (jobs)
    │         MinIO (evidence bundles)
    └── Redis queue ──► Worker ──► X02 研究 API (:8787)
```

## 快速启动（Windows / Docker，推荐）

```powershell
cd E:\AI耳机\diary-one-server
copy .env.example .env
docker compose up -d --build
docker compose run --rm bff python -m shared.db_init
python scripts/smoke_test.py
```

仅本地改代码、不重建镜像时：

```powershell
.\scripts\start-bff.ps1
.\scripts\start-worker.ps1
```

联调步骤见 **`../diary-one-app/docs/M2_RUNBOOK.md`**；**无 Docker Expo Go** 见 **`docs/EXPO_GO_DEV_LITE.md`**；部署见 **`docs/DEPLOY.md`**。

```powershell
# 推荐：无 Docker 内测栈
.\scripts\start-dev-lite.ps1 -Adapter fixture   # 或 -Adapter qwen（需 DASHSCOPE_API_KEY）
```


手机 App（`__DEV__`）→ Account → Evidence pipeline lab → **Production BFF** →  
`http://<你电脑局域网IP>:8790`，Token 与 `.env` 中 `API_TOKEN` 一致（默认 `dev-token`）。

## 环境变量

见 `.env.example`。

## 目录

| 路径 | 说明 |
|------|------|
| `bff/` | 对外 HTTP API |
| `worker/` | 队列消费、调 X02、写回 job 结果 |
| `shared/` | 配置、数据库、对象存储、模型 |
