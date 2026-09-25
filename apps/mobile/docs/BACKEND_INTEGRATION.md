# Diary One App · 后端配套说明

Figma/PRD 能力 → App 内 `src/backend/` 实现映射（**非**独立量产服务器仓库）。

| 产品能力 | 后端模块 | 当前实现 |
|----------|----------|----------|
| 设备 Sync（SYN01） | `deviceSyncService` | Lab link + 状态机；真 BLE 待 SDK |
| Cloud Processing | `researchCloudService` / `productionCloudService` | X02 multipart 研究 API；量产 REST 契约已预留 |
| 本机资料 / OTP（ACC01–03） | `authLocalService` | 本机校验 OTP，写入 `localProfile.email` |
| 导出 / 删本地（PRI） | `privacyService` | JSON 导出 + SQLite 重置 |
| Memory Preferences → 云 | `researchCloudService` | 随 Bundle 提交 `app_client_profile` |
| 正式账号 Apple/Google | `authLocalService` | 占位 Alert，无远端 IdP |
| 量产 BFF 服务 | **`../diary-one-server/`** | Docker：Postgres + Redis + MinIO + BFF + Worker |

## 环境配置

| 字段 | 用途 |
|------|------|
| `researchEndpoint` + `researchToken` | PC 局域网 X02（handoff 8787） |
| `productionApiBaseUrl` + `productionApiToken` | 未来量产 BFF（`POST /v1/day-revisions` 等） |
| `cloudProcessingTarget` | `research` \| `production` |

研发入口：**Account → Evidence pipeline lab**（`__DEV__`）。
