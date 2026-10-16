# 今天打包 TestFlight · 一张纸（2026-10-14）

对照：`Diary_One_App_产品定义书_PRD_V0.1_2026-09docx.docx`（§26 **M2**）+ 本会话内测约定。

---

## 0. 诚实范围（先对齐，避免今天白干）

| 今天能交付 | 今天不能诚实宣称 |
|------------|------------------|
| **M2**：相册选图 → Evidence → 公网 BFF → 通义模型 → Diary | 53 条 PRD 全验收、M3/M4/M5 |
| Figma 04 主屏 UI + 跳转（内测口径） | 真 BLE / 硬件同步 |
| 邮箱 OTP、云 Evidence 同意、Memory/Share/问卷 | App Store 正式上架 A1–A8 |
| 服务端**一把** DashScope Key 直接调模型 | 手机内嵌模型 Key / 免 OTP 直连模型 |

PRD 原文：**「当前首要目标优先达成 M2」**；不代表「全天容量、全部非硬件、硬件闭环」。

---

## 1. 前后端 / 算法 · 现在谁干什么（清晰）

```text
┌─────────────────────────────────────────────────────────────┐
│  iPhone TestFlight (EAS preview)                            │
│  · Figma UI / 导航 / 本地 Memory / Share 拼装               │
│  · 鉴权：邮箱 OTP → session_token（每人一把）               │
│  · 不持 DashScope Key；不持共享 API_TOKEN                   │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS + Bearer session
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  公网 Cloudflare 隧道 → 本机 BFF :8790 (Dev Lite)           │
│  · OTP / 配额 / day-revisions / Share 渲染 / Evidence 语义   │
│  · MobileCLIP（本机已加载）                                  │
│  · API_TOKEN 仅工程师 curl；勿进 IPA                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  本机 X02 :8787 (adapter=qwen)                              │
│  · 统一 DASHSCOPE_API_KEY → 直接调通义模型                  │
│  · 模式：STAGED REAL MEDIA PREVIEW（内测真链路，非 S13 全量）│
└─────────────────────────────────────────────────────────────┘
```

| 层 | 代码位置 | 今天状态 |
|----|----------|----------|
| App UI | `apps/mobile` | Figma 04 主路径齐；Device 诚实未连接 |
| Evidence / Import | `apps/mobile/src/pipeline` | 消费者路径齐 |
| BFF | `services/bff` + Dev Lite | 本机 `/health` 绿；需公网隧道常开 |
| 算法 X02 | diary_one_ci / x01_server qwen | `modelReady` + DashScope |
| 语义选帧 | MobileCLIP on BFF | 本机 available |

---

## 2. Agent 已做好（你不必再改代码才能打预览包）

- [x] 配对 / Device 假电量诚实化  
- [x] 隐私/条款 env（无正式页不死链）  
- [x] 内测文档 + 操作单  
- [x] `check-internal-beta-ready.ps1` 工程预检绿  
- [x] **已重开公网隧道并写入 `eas.json` preview**（见下；**PC 勿关机**）

当前已写入 `eas.json` 的公网 URL（**PC 保持开机；cloudflared 勿杀**；重启变 URL 则重跑隧道再 build）：

```text
https://elder-mailman-awareness-debut.trycloudflare.com
```

你本机自检：

```powershell
curl.exe -4 -sS "https://elder-mailman-awareness-debut.trycloudflare.com/health"
# 要看 allow_mock_preview: false
```

---

## 3. 你今天必须亲自完成（按顺序复制）

### 步骤 A · 确认本机云还活着（5 分钟）

```powershell
curl.exe -sS http://127.0.0.1:8790/health
# 要看：allow_mock_preview=false  smtp_configured=true  x02.reachable=true  mobileclip.available=true

curl.exe -4 -sS "https://$(Get-Content 'E:\AI耳机\diary-one\services\bff\.local\last-public-bff-url.txt' | ForEach-Object { $_ -replace 'https://','' })/health"
# 若 last-public 文件只有完整 URL：
curl.exe -4 -sS "$(Get-Content 'E:\AI耳机\diary-one\services\bff\.local\last-public-bff-url.txt' -Raw).Trim()/health"
```

若公网不通：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\start-dev-lite-background.ps1   # 若本地 8790 挂了
.\scripts\start-public-tunnel.ps1 -ApplyEas
```

DashScope（统一一把 Key，服务端调模型）：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\set-dashscope-key.ps1   # 若尚未设置；设完需重启 Dev Lite / X02
```

SMTP（OTP 收信）：

```powershell
.\scripts\set-smtp.ps1 -SmtpHost smtp.qq.com -Port 465 `
  -User '你的邮箱@qq.com' -Password '授权码' -From '你的邮箱@qq.com'
.\scripts\prepare-multiuser-beta.ps1 -HardenEnv
# 然后重启 Dev Lite
```

预检：

```powershell
powershell -File E:\AI耳机\diary-one\scripts\check-internal-beta-ready.ps1
```

### 步骤 B · Apple + EAS 打 IPA（半天主线）

**只有你能登录账号。**

```powershell
cd E:\AI耳机\diary-one\apps\mobile

npx eas-cli login
npx eas-cli init
# 把打印的 projectId 留在工程里（app.json / app.config extra.eas）

# 确认 eas.json preview：
#   EXPO_PUBLIC_DEV_BFF_URL = 当前隧道 HTTPS
#   EXPO_PUBLIC_DEV_BFF_TOKEN = ""
#   EXPO_PUBLIC_INTERNAL_BETA = 1

npx eas-cli build --profile preview --platform ios
```

App Store Connect：

1. 新建 App，Bundle ID = **`com.nexleap.diaryone.dev`**（与 `app.json` 一致）  
2. 把数字 **Apple ID** 填进 `eas.json` → `submit.preview.ios.ascAppId`  
3. 提交：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npx eas-cli submit --profile preview --platform ios
```

4. TestFlight → 加内部测试员 → 装包  

**纪律：** 隧道 URL 一变 → `-ApplyEas` → **必须重打 build**（旧 IPA 里的 BFF 地址是死的）。

### 步骤 C · 装上后最短验收（30 分钟）

1. 邮箱 OTP 登录  
2. Account → Privacy → 同意云 Evidence  
3. Device → **Import from Photos** → 选图  
4. Diary：Preparing → Ready / Chapter  
5. Memory 搜索；Share 拼贴预览  
6. Device 保持 **Disconnected**  

对照：`apps/mobile/docs/INTERNAL_BETA_FIGMA.md`

---

## 4. 前后端算法文件地图（找代码用）

| 能力 | 主要路径 |
|------|----------|
| 登录 OTP | `apps/mobile/src/backend/authRemoteService.ts` · BFF `/v1/auth/otp/*` |
| Bearer | `apps/mobile/src/backend/resolveProductionBearer.ts`（只用 session） |
| Import / Evidence | `apps/mobile/src/pipeline/launchEvidenceImport.ts` |
| Diary 写入 | `apps/mobile/src/store/applyDiaryDay.ts` · BFF day-revisions |
| 云准入 | `apps/mobile/src/cloud/deliveryAdmit.ts` |
| Share | `apps/mobile/src/…composeShareViaBff` · BFF `/v1/share/*` |
| BFF Dev Lite | `services/bff/dev_lite/` |
| X02 调模型 | User 环境 `DASHSCOPE_API_KEY` · `set-dashscope-key.ps1` |
| 运维一键 | `docs/INTERNAL_BETA_USER_RUNBOOK.md` |

---

## 5. 今天不要做（不挡「能内测」）

- 真 BLE / 厂商同步  
- Sign in with Apple 正式接线  
- Docker 量产高可用（Dev Lite + 隧道即可）  
- X02「Production S13 全 pipeline」签字  
- App Store production 审核材料  

---

## 6. 一句话

**代码侧可打 preview；今天卡点只剩：你登录 EAS/Apple → build → submit，以及保持本机隧道 + 统一 DashScope Key 存活。**  
交付名称请叫 **「M2 内测包」**，不要叫「53 条 PRD 全部正式完成」。
