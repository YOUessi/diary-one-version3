# Diary One · iOS 内测 · 你方逐步操作单

Agent 已完成代码侧阶段 0。下列步骤**只有你能做**（Apple 账号、SMTP、DashScope Key、公网隧道、EAS 登录）。

路径根目录：`E:\AI耳机\diary-one`

---

## 云端鉴权与模型（内测约定）

```text
TestFlight App  →  公网 BFF（每人邮箱 OTP session）
                 →  本机 X02（adapter=qwen）
                 →  通义 / DashScope（一把统一 API Key）
```

| 钥匙 | 放哪 | 谁用 |
|------|------|------|
| **`DASHSCOPE_API_KEY`** | 仅服务端（`set-dashscope-key.ps1` → User 环境） | **全员共用一把**；X02 直接调模型 |
| OTP `session_token` | 各测试员手机登录后 | App → BFF 上传 / 拉 Diary |
| `API_TOKEN` | 仅 `services/bff/.env` | 工程师 curl / Lab；**不要**打进 IPA / 群公告 |
| `EXPO_PUBLIC_DEV_BFF_TOKEN` | preview 保持 `""` | 正式内测包**不用**共享 BFF token |

**不要**把 DashScope Key 写进 App / `eas.json` / `EXPO_PUBLIC_*`。  
手机只连 BFF；**调模型只在服务端**（有 Key → 真模型；无 Key → fixture，日记会假）。

---

## A. 本机 BFF + SMTP + 算法 Key（约 1–2 小时）

```powershell
cd E:\AI耳机\diary-one\services\bff

# A1 — 量产态 .env（随机 API_TOKEN、关 mock）
.\scripts\prepare-multiuser-beta.ps1 -HardenEnv

# A2 — SMTP（多人 OTP 必填；把授权码换成你的）
.\scripts\set-smtp.ps1 `
  -SmtpHost smtp.qq.com `
  -Port 465 `
  -User '你的邮箱@qq.com' `
  -Password '邮箱授权码' `
  -From '你的邮箱@qq.com'
.\scripts\prepare-multiuser-beta.ps1 -HardenEnv

# A3 — 通义 / DashScope：内测全员共用这一把（服务端直接调模型）
.\scripts\set-dashscope-key.ps1
# 按提示粘贴 Key；只写本机 User 环境，勿进 git / eas / 手机

# A4 — 启动本机 Dev Lite BFF（后台）
.\scripts\start-dev-lite-background.ps1

# A5 — 公网 HTTPS 隧道，并写入 apps/mobile/eas.json preview
# 若未装 cloudflared： winget install Cloudflare.cloudflared
.\scripts\start-public-tunnel.ps1 -ApplyEas

# A6 — 预检（应全绿或仅 WARN）
powershell -File ..\..\scripts\check-internal-beta-ready.ps1

# A7 — 健康检查（把 URL 换成隧道打印的 PUBLIC_BFF_URL）
curl.exe -sS https://<你的隧道主机>/health
# 确认 JSON 里 allow_mock_preview 为 false
```

**纪律：**

- 跑隧道的 PC **保持开机**；关机 = 全员 OTP / Import 挂掉。
- 隧道 URL **一变** → 重跑 `start-public-tunnel.ps1 -ApplyEas` → **必须重新** `eas build`。
- Key / SMTP 密码只放在 `services/bff/.env`，不要写进 `eas.json` 或群公告。

可选正式隐私页（无页面前可跳过；App 显示友好占位、不死链）：

```text
# 写入 apps/mobile/.env 或 eas.json preview.env：
EXPO_PUBLIC_PRIVACY_POLICY_URL=https://你的站/privacy
# 或别名：EXPO_PUBLIC_PRIVACY_URL=https://你的站/privacy
EXPO_PUBLIC_TERMS_URL=https://你的站/terms
```

---

## B. Apple + EAS 打 IPA / TestFlight（约半天）

**前置：** 付费 Apple Developer 账号；本机已装 Node。

```powershell
cd E:\AI耳机\diary-one\apps\mobile

# B1 — 登录 Expo
npx eas-cli login

# B2 — 绑定 EAS 项目（首次；写入 projectId）
npx eas-cli init

# B3 — 确认 eas.json → build.preview.env
#   EXPO_PUBLIC_INTERNAL_BETA=1
#   EXPO_PUBLIC_DEV_BFF_URL = 当前公网 HTTPS（无 REPLACE_WITH_PUBLIC_BFF_HOST）
#   EXPO_PUBLIC_DEV_BFF_TOKEN = ""

# B4 — 打内测包
npx eas-cli build --profile preview --platform ios
```

App Store Connect：

1. 新建 App（Bundle ID 以工程 `app.json` / `app.config.js` 为准）。
2. 把 App 的 **Apple ID 数字** 填进 `eas.json`：

```json
"submit": {
  "preview": {
    "ios": { "ascAppId": "1234567890" }
  }
}
```

3. 提交 TestFlight：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npx eas-cli submit --profile preview --platform ios
```

4. App Store Connect → TestFlight → 加内部测试员 → 安装。

---

## C. 内测员最短验收

对照：`apps/mobile/docs/INTERNAL_BETA_FIGMA.md`

1. 邮箱 OTP 登录  
2. Account → Privacy → 同意云 Evidence  
3. Device → **Import from Photos** → 选图  
4. Diary：Preparing → Ready / Chapter  
5. Memory 本地搜索；Share 拼贴预览  
6. Device 保持 **Disconnected**（无真 BLE）

---

## D. 本轮不做 / 后置

- 真 BLE / 厂商同步  
- Sign in with Apple（正式接线）  
- 正式隐私政策 HTTPS（可先占位）  
- Named Tunnel / 云主机（替代临时 trycloudflare）  
- App Store production（见 `apps/mobile/docs/APP_STORE_RELEASE.md`）

---

## E. 出问题先查

| 现象 | 检查 |
|------|------|
| OTP 收不到 | SMTP 授权码、`.env` SMTP_*、邮件垃圾箱 |
| Import 失败 | `/health`、隧道是否活着、DashScope Key、云 Evidence 同意 |
| eas build 连错后端 | `eas.json` preview 的 `EXPO_PUBLIC_DEV_BFF_URL` 是否最新隧道 |
| Device 假连接 | 用「Continue without a device」；勿期望真耳机 |
