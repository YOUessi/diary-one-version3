# PRD V0.1 商用加固记录（2026-10-10）

对照：`Diary_One_App_产品定义书_PRD_V0.1` + Figma `7NSDFSkyxO38CaELtAtayL`（既有 `FIGMA_FULL_AUDIT_2026_10_09.md`）。

## 本轮代码落地（风险优先）

| PRD | 改动 |
|-----|------|
| DIA04 / DAT01 | 空云结果 / `NO_GROUNDED` **不抹**当日已有 Ready（`applyDiaryDay.ts` + `runPipeline.ts`） |
| DIA04 / T05 | 空结果保留旧内容时 **Today 横幅保持 READY**，不刷成 ZERO_CURATED；历史日任务不改 Today 态 |
| DAT01 / AI03 | App 准入对齐 BFF `result_admit`（`deliveryAdmit.ts` / `validatePreviewResult.ts`）；BFF `tests/test_result_admit.py` |
| DAT02 / T08 | Your Story **仅按 chapter id 回绑**；被替换 id 的补记章节保留可追溯（不按标题挪绑） |
| AI02 | 去掉 `allUris[0]` / `moment_ids` 假 Moment；仅 `selected_media` 解析本地帧 |
| AI03 / CH01 | 无媒体 → 空 Moments；详情 **Media unavailable** |
| DEV01 | Diary Sync 在 disconnected 时 Alert，不假同步；Device 诚实 Unavailable |
| PRI03 | 登出 wipe：空库 + 清 raw_assets / pipeline ledger + 清 session/token |
| ACC / D11 | 内测包 Billing = Not available |
| 多人内测 | OTP、Device 导入、owner 幂等、`scripts/check-internal-beta-ready.ps1` |
| PRI01 | 内测包**不再**静默 `cloudEvidenceConsent=true`（须 Privacy/问卷） |
| REL01 | 失败不复用 `productionJobId`；`raw_assets` 仅云准入成功后写入（可同素材重试） |
| DAT01 | 内测/商店强制 `_publish` envelope |
| D11 | Plan 文案改为 Not available（去掉 Basic） |
| IMP01 | Android 串行「Add another」最多 6；去重文案区分已准入 |
| UX | Diary Sync / Device Import 引导 OTP + Privacy 云同意 |
| DAT01 | Chapter 有而 ahas 空时不抹当日既有 Small Memory |
| ACC03 | Account 内 **Continue with Email / OTP**（`mode=account`，不重跑配对）+ 同意问卷入口 |
| ACC03 | 内测/商店：无 BFF URL / 占位 URL / 无 `session_token` → OTP **fail-closed**（禁本地假登录） |
| ACC03 | OTP / consent / BFF URL 变更 **立即 flushPersist**（防杀进程丢 session） |
| ACC03 | 冷启动 `probeProductionSession`；问卷缺字段默认未完成；Account skip 记完成 |
| REL01 | 上传/轮询 401/403 → 清 session；404≠未部署；僵死 queued 回收；409 换 revision 重试 |
| DAT01 | `day_revision_id` 加 owner salt，降同机换测员 409 |
| AI03 | eval-web delivery 与 BFF/App 对齐（含 STAGED；拒 PIPELINE_BLOCKED / publish_admit=false） |
| UX | Device 内测区展示 Cloud API 是否已配置 |
| SYS02 | 内测/商店冷启动清空 research 端点，强制 production target |
| 算法台 | 08 MobileCLIP 1/3/5/10 + sha256 去重；09 自带 Key→Chapter（SYS02 测试例外） |

## 验证

- BFF：`pytest tests/test_result_admit.py tests/test_day_revision_owner_idempotency.py` → 7 passed
- App：`npx tsc --noEmit` → **通过**（补 `expo-asset`/`expo-constants`、`absoluteFill`、`sha256File` ArrayBuffer、删未用 `attachHeroUris`）

## Figma

- 覆盖表：`apps/mobile/docs/FIGMA_04_COVERAGE.md` · 全量审计：`docs/FIGMA_FULL_AUDIT_2026_10_09.md`
- Handoff 纪律保持：Device deferred / 诚实未连接 / Topics 不足隐藏 / Small Memory 不可点
- MCP 账号 Nexleap = **View seat**（`get_design_context` / images 易 429）；PAT `/v1/me` 可用，图像导出仍 rate-limit
- **像素终验**需升 Dev/Full 座或等额度；评论驱动改版仍等设计改板（审计 §5）

## 部署侧（代码外，仍阻断几十人）

运维勾选表：`docs/INTERNAL_BETA_OPS_CHECKLIST.md`  
预检：`powershell -File scripts/check-internal-beta-ready.ps1`（当前常见 FIX：eas 占位 URL、本机 `.env` 仍 `API_TOKEN=dev-token`）

## 有意不做（开放决策 / 评论扩展）

D01 Session、D02 语义搜索、假电量 72%、评论区 Tag 可跳转、Device 拍照进度深化等 — 见 Figma 审计 §4–5。
