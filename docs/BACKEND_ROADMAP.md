# 后端开发路线图（在现有代码上补齐）

**真相源：** `diary-one/services/bff/`  
**手机联调：** Dev Lite `:8790`（无 Docker）  
**量产：** Docker BFF + Worker + Postgres + Redis + MinIO  

App 合同：`apps/mobile/src/backend/productionCloudService.ts`、`authRemoteService.ts`

---

## 模块盘点

| 模块 | 路径 | 状态 | 说明 |
|------|------|------|------|
| Dev Lite 主服务 | `dev_lite/app.py` | ✅ 主链可用 | health / OTP / day-revisions / jobs |
| Dev Lite 语义 | `dev_lite/semantic_routes.py` | ⚠️ | Windows analyze 501；路由在 App TS |
| 量产 BFF | `bff/main.py` + `routes/*` | ✅ | day-revisions + jobs；OTP=`shared/otp.py` |
| Worker | `worker/processor.py` | ✅ | MinIO → X02 |
| 共享模型 | `shared/models.py` | ✅ | `CloudJob` 无 day_revision 唯一约束 |
| X02 | 本机 `:8787` | 外置 | `DASHSCOPE_API_KEY` + qwen |

### 端点 vs App

| 端点 | Dev Lite | 量产 BFF | App 使用 |
|------|----------|----------|----------|
| GET `/health` | ✅ + x02 | ✅ 简版 | Lab Ping |
| POST `/v1/auth/otp/*` | ✅ SMTP | ✅ shared/otp + SMTP env | 登录 |
| POST `/v1/day-revisions` | ✅ | ✅ | 上传 Bundle |
| GET `/v1/jobs/{id}` | ✅ | ✅ | 轮询 |
| day_revision **幂等** | ✅ | ✅ | 防重复扣费/双任务 |

---

## 按顺序做（挨个开工）

### 阶段 1 — Dev Lite 内测主链

1. ✅ 盘点（本文）  
2. ✅ **幂等 + 任务落盘**（BFF 重启可恢复 poll + 续跑 pending）  
3. ✅ `scripts/smoke-dev-lite.ps1` 一键冒烟  
4. ⏳ 真 qwen + 关 mock（`DASHSCOPE_API_KEY` + `-Quality`）  
5. ✅ SMTP 真 OTP（QQ；量产 compose 已接）  

### 阶段 2 — 与量产对齐

6. ✅ 量产 `auth_otp` ← `shared/otp.py` + SMTP 环境变量  
7. ✅ Docker compose healthcheck + README / stop-dev-lite  
8. `day_revision_id` DB 唯一索引（可选；失败重试与唯一约束冲突，暂应用层幂等）  
9. ✅ **云端大量素材通道脚本**（`open-cloud-bulk-channel.ps1` / `smoke-cloud-pack.ps1`）— 见 `docs/CLOUD_BULK_CHANNEL.md`  

### 阶段 3 — → **10 月 20 日左右内测包**（目标节点）

| 节点 | 含义 | 验收 |
|------|------|------|
| **N1 链路绿** | Expo Go / 内测包：相册→BFF→X02 百炼→Diary 章节 | Lab B 真照片 + PC `-RequireGrounded` pack |
| **N2 质量门** | 大量素材筛选/出稿与本地 eval 同合同；`ALLOW_MOCK_PREVIEW=false` | ≥1 真实 pack 有 chapters，无 mock_fallback |
| **N3 账号** | OTP / Apple·Google（能配则配） | 登录进 4 Tab |
| **N4 分享** | Collage / Illustrated / Recap（PC ffmpeg） | Lab / Diary Share |
| **N5 包** | EAS / 内测分发（非 Expo Go 长驻） | TestFlight 或 Android 内测 APK |

**明确不做进 10/20 包：** BLE 真耳机；本地自训小模型上线（对比体量另轨，adapter 可后换）。

### 阶段 4 — 商用加深（包后）

10. OSS 替换 MinIO  
11. ✅ `session_token` Bearer 校验 day-revisions / jobs  
12. 限流 / 监控 / 订阅计量（按 job / token）  
13. 本地处理模型 adapter（你训练中）↔ 百炼 可切换对比  

---

## 本地怎么起

```powershell
cd E:\AI耳机\diary-one\services\bff
# UI / Expo 无 Key：
.\scripts\start-dev-lite-background.ps1

# 云端大量素材（百炼质量）：
.\scripts\open-cloud-bulk-channel.ps1 -Quality -MediaDir D:\packs\day1 -RequireGrounded
```

手机：Lab Apply → Ping → **B 相册**（勿用 Demo 验收质量）。

---

更新：随 commit 改「状态」列；测过记入 `docs/TEST_LOG.md`；通道说明 `docs/CLOUD_BULK_CHANNEL.md`。
