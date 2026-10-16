# Diary One Server · 部署与演进

## 当前形态（v0.1）

- **BFF**：无状态，可水平扩展（需共享 Postgres / Redis / MinIO）。
- **Worker**：消费 Redis 队列；CPU/IO 密集，按队列深度扩容。
- **X02**：仍跑在宿主机或独立算法服务；Worker 通过 `X02_BASE_URL` 调用。

## 本地 / 内测（推荐）

```powershell
cd diary-one-server
copy .env.example .env
docker compose up -d --build
docker compose exec bff python -m shared.db_init
```

验证：`curl http://localhost:8790/health`

## 环境变量（生产前必改）

| 变量 | 说明 |
|------|------|
| `API_TOKEN` | 强随机 Bearer；App Production 配置同一值 |
| `DATABASE_URL` | 托管 Postgres（启用 SSL） |
| `REDIS_URL` | 托管 Redis |
| `MINIO_*` / 换 AWS S3 | 对象存储；后续可把 `shared/storage.py` 改为 S3 SDK |
| `X02_BASE_URL` | 内网算法服务地址 |

## 云上最小拓扑（商用参考）

```text
Internet → TLS LB → BFF (ECS/Cloud Run × N)
                      ↓
            RDS Postgres + ElastiCache Redis + S3
                      ↓
                 Worker (ECS/Cloud Run Jobs × N) → X02 / 模型网关
```

## 安全清单

- [ ] HTTPS 终止在 LB，BFF 不对外裸 HTTP
- [ ] `API_TOKEN` / DB 密码进密钥管理（非 .env 进镜像）
- [ ] MinIO/S3 bucket 私有；仅 Worker 可读 job 前缀
- [ ] CORS 限制为 App 正式域名（替换 `allow_origins=["*"]`）
- [ ] 请求体大小限制（Evidence multipart）
- [ ] 结构化日志 + job 失败告警

## 与 App 的契约

- `POST /v1/day-revisions` — multipart（与 X02 相同字段）
- `GET /v1/jobs/{id}` — `status`: pending | processing | succeeded | failed；成功时带 `result`（X02 JSON）

版本升级时 **只增字段**，App 侧 `validatePreviewResult` 保持 fail-closed。
