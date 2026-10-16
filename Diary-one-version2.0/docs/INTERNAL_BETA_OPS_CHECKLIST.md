# 多人内测 · 运维放行清单（代码已就绪后）

代码侧加固见 `PRD_COMMERCIAL_HARDENING_2026_10_10.md`。下列项**必须人肉部署**，预检脚本会标 FIX。

**最快公网路径（本机 Dev Lite + Cloudflare 临时 HTTPS）：** 见下方 §0。  
机器关机 = 全员不可用；稳定域名请改用 Named Tunnel 或云主机。

## 0. 一键顺序（推荐 · 办公室 PC）

```powershell
cd E:\AI耳机\diary-one\services\bff

# 1) 量产态 .env：随机 API_TOKEN、关 mock、尽量带上 SMTP
.\scripts\prepare-multiuser-beta.ps1 -HardenEnv

# 2) SMTP（多人 OTP 必做；只跑一次）
# .\scripts\set-smtp.ps1 -SmtpHost smtp.qq.com -Port 465 -User 'you@qq.com' -Password '授权码' -From 'you@qq.com'
# 然后再 -HardenEnv 一次，把 User 环境变量同步进 .env

# 3) 本机 BFF（Dev Lite）+ 真算法 Key
# .\scripts\set-dashscope-key.ps1   # 若尚未设置
.\scripts\start-dev-lite-background.ps1

# 4) 安装 cloudflared（若尚未安装）
# winget install Cloudflare.cloudflared

# 5) 公网 HTTPS 隧道，并写入 eas.json preview
.\scripts\start-public-tunnel.ps1 -ApplyEas

# 6) 预检
powershell -File ..\..\scripts\check-internal-beta-ready.ps1

# 7) 健康检查（把 URL 换成脚本打印的 PUBLIC_BFF_URL）
# curl.exe -sS https://xxxx.trycloudflare.com/health
```

TestFlight 构建（需你已 `eas login` + Apple 账号）：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
eas build --profile preview --platform ios
# 可选提交：先把 eas.json submit.preview.ios.ascAppId 换成真实 ASC App ID
# eas submit --profile preview --platform ios
```

脚本说明：

| 脚本 | 作用 |
|------|------|
| `services/bff/scripts/prepare-multiuser-beta.ps1 -HardenEnv` | 随机 `API_TOKEN`、`ALLOW_MOCK_PREVIEW=false`、SMTP/`EXPOSE_OTP_IN_RESPONSE` |
| `services/bff/scripts/start-public-tunnel.ps1` | Cloudflare quick tunnel → `:8790`；`-ApplyEas` 写 eas |
| `services/bff/scripts/apply-public-bff-url.ps1 -Url https://…` | 仅改 `eas.json` preview URL，token 置空 |
| `scripts/check-internal-beta-ready.ps1` | 占位符 / mock / Account OTP 等预检 |

临时隧道 URL **每次重启会变**；变了必须重跑 `-ApplyEas` 并 **重新 eas build**。要稳定主机名：Cloudflare Named Tunnel 或 Linux 云主机（见 `services/bff/docs/DEPLOY.md`）。

## 1. 公网 BFF

- [ ] HTTPS 可达：`GET https://…/health` → `allow_mock_preview: false`
- [ ] `API_TOKEN` ≠ `dev-token`（Lab 调试另用；**不要**打进 eas / 群公告）
- [ ] SMTP 可向测试邮箱发 OTP（`EXPOSE_OTP_IN_RESPONSE=false`）
- [ ] X02 / DashScope Key 仅在服务端
- [ ] MobileCLIP 权重可选（视频质量）；照片主路径可先不依赖
- [ ] 跑隧道的 PC 保持开机；Dev Lite / Docker 进程存活

## 2. App 构建

- [ ] `apps/mobile/eas.json` → `preview.env.EXPO_PUBLIC_DEV_BFF_URL` = 公网 HTTPS（无 `REPLACE_WITH_PUBLIC_BFF_HOST`）
- [ ] `EXPO_PUBLIC_DEV_BFF_TOKEN` 保持空字符串（OTP only）
- [ ] `EXPO_PUBLIC_INTERNAL_BETA=1`（已在 preview profile）
- [ ] `eas build --profile preview --platform ios` → TestFlight
- [ ] （可选）`submit.preview.ios.ascAppId` 换成真实 App Store Connect App ID

本地再跑：

```powershell
powershell -File E:\AI耳机\diary-one\scripts\check-internal-beta-ready.ps1
```

## 3. 内测员最短路径

逐步命令单（Apple / EAS / SMTP / Key）：[`INTERNAL_BETA_USER_RUNBOOK.md`](./INTERNAL_BETA_USER_RUNBOOK.md)  
Figma 验收边界：[`apps/mobile/docs/INTERNAL_BETA_FIGMA.md`](../apps/mobile/docs/INTERNAL_BETA_FIGMA.md)

1. 邮箱 OTP 登录  
2. Account → Privacy → 同意云 Evidence  
3. Device → Import from Photos → 选图 → 云 → Diary（Preparing → Ready）  
4. Memory 本地搜索；Share 拼贴预览  
5. Device 保持 Disconnected（无真 BLE）  
6. 登出会 wipe 本机库 + session（换人测）

## 4. 验收样例

- [ ] 邮箱 A / B 各出至少 1 个 chapter，互不覆盖  
- [ ] 断网失败后同图可重试（未成功写入 ledger）  
- [ ] 空日 / NO_GROUNDED 不抹旧 Ready  
- [ ] Disconnected Sync 不假成功  
