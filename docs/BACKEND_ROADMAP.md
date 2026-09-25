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
| POST `/v1/auth/otp/*` | ✅ SMTP | ⚠️ 仅 dev_code | 登录 |
| POST `/v1/day-revisions` | ✅ | ✅ | 上传 Bundle |
| GET `/v1/jobs/{id}` | ✅ | ✅ | 轮询 |
| day_revision **幂等** | ✅ | ✅ | 防重复扣费/双任务 |

---

## 按顺序做（挨个开工）

### 阶段 1 — Dev Lite 内测主链（你现在）

1. ✅ 盘点（本文）  
2. ✅ **幂等 + 任务落盘**（BFF 重启可恢复 poll + 续跑 pending）  
3. ✅ `scripts/smoke-dev-lite.ps1` 一键冒烟  
4. ⏳ 真 qwen + 关 mock（你配 `DASHSCOPE_API_KEY`）  
5. ⏳ SMTP 真 OTP（`set-smtp.ps1`）  

### 阶段 2 — 与量产对齐

6. ✅ 量产 `auth_otp` ← `shared/otp.py` + SMTP 环境变量  
7. ⏳ Docker compose 本地跑通 worker（`smoke-docker.ps1` 验 OTP/session）  
8. `day_revision_id` DB 唯一索引（可选；失败重试与唯一约束冲突，暂应用层幂等）  

### 阶段 3 — 商用

9. OSS 替换 MinIO  
10. ✅ `session_token` Bearer 校验 day-revisions / jobs（Dev Lite + 量产 BFF）  
11. 监控 / 限流 / 日志  

---

## 本地怎么起

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\start-dev-lite.ps1          # 需 DASHSCOPE 时先 set-dashscope-key
.\scripts\smoke-dev-lite.ps1          # 冒烟（阶段 1-3 后）
```

手机：Lab Apply → Ping → Demo / B 相册。

---

更新：随 commit 改「状态」列；测过记入 `docs/TEST_LOG.md`。
