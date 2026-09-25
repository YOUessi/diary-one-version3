# PRD 云端接入 + App Evidence（去重/抽帧/压缩）

依据：产品定义书 V0.1「功能划分」——硬件 / App / 云与智能模型。

## 云端：去哪拿服务

| PRD 能力 | 平台 | 说明 |
|----------|------|------|
| 视觉理解 / 结构 / 文案 | **阿里云百炼 DashScope** | 唯一算法供应商；新人免费 Token |
| 认证 OTP | **自研 BFF** + **163/QQ SMTP** | 不另买 Auth0；短信可后接阿里云短信 |
| 异步任务 | **Dev Lite** → Docker Redis+Worker | 内测本机；量产再上云 |
| 媒体存储 | Dev 本地盘 → **阿里云 OSS** | 只存最小 Evidence，不扫全库 |
| 账号/任务元数据 | Dev 文件 → **Postgres** | Docker 或阿里云 RDS |
| 幂等/原子发布 | **自研** | 不买第三方「发布平台」 |

步骤见 `REAL_CLOUD_SETUP.md`。

## App：Observation 生产（必须在端上）

| 能力 | 实现 |
|------|------|
| **去重** | `dedupeMedia.ts` + SQLite `raw_assets`（`original_sha256`） |
| **压缩** | `evidenceNormalize.ts` → 768×1024 JPEG 0.84 |
| **抽帧** | `buildAppLibraryBundle.ts` + `expo-video-thumbnails`；导入已开视频 |
| **最小 Evidence** | `original_included: false`；只上传 frames + bundle.json |

导入入口：`launchEvidenceImport.ts`（图+视频 → 去重 → 管线）。
