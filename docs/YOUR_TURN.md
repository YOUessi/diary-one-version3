# 需要你补充的事项（开发侧已就绪）

开发侧可做项见 `docs/REMAINING_GAPS.md`。下列依赖你的账号/密钥/硬件/真机。

**产品铁律：** Expo Go / 打包 = 正式用户 App（见 [`FORMAL_APP_ACCEPTANCE.md`](./FORMAL_APP_ACCEPTANCE.md)）。  
**本机质量：** [`LOCAL_QUALITY_LOOP.md`](./LOCAL_QUALITY_LOOP.md) · **内容抽检：** [`ALGORITHM_CONTENT_REVIEW.md`](./ALGORITHM_CONTENT_REVIEW.md)  
**公网 + TestFlight（搁置）：** `INTERNAL_BETA_OPS_CHECKLIST.md` §0  

## 0. 正式用户路径（Expo Go 默认 · 无 Lab）

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\start-quality-loop.ps1
# App: apps/mobile/.env → EXPO_PUBLIC_DEV_BFF_URL=http://<LAN>:8790 ，TOKEN 留空
# 勿设 EXPO_PUBLIC_ENABLE_LAB（正式验收）
cd ..\..\apps\mobile
npx expo start --go --lan
```

手机：**Email OTP → Privacy 同意 → Device Import → Diary**。  
禁止 Skip / Demo / Offline mock / shared `dev-token`。

## 0b. LAN 联调（UI / 无 Key 时）

1. **管理员** PowerShell 一次：  
   `cd E:\AI耳机\diary-one\services\bff`  
   `.\scripts\setup-commercial-dev.ps1 -OpenFirewall`
2. 后台已起过则跳过；否则：`.\scripts\start-dev-lite-background.ps1`
3. App：`cd E:\AI耳机\diary-one\apps\mobile` → `npx expo start --go --lan`  
   （`.env` 已指向当前 LAN，如 `http://192.168.31.74:8790`；IP 变了重跑 setup）
4. 手机按 **`docs/PHONE_FULL_TEST.md`** 从上到下试完；结果记 `TEST_LOG.md`

## 1. Daily Recap 视频（Expo Go）

1. PC 已装 **ffmpeg**（health 应 `ffmpeg_available: true`）
2. 手机 Share day → Daily Recap（走 BFF，不要指望 Go 里原生编码）

## 2. 真云（P2 / T7）

1. 百炼 API Key → `.\scripts\set-dashscope-key.ps1`
2. `.\scripts\start-dev-lite.ps1 -Adapter qwen`（不要开 mock）
3. Lab Ping → Demo，人工看记忆质量

## 3. 真邮件 OTP

1. `services/bff/scripts/set-smtp.ps1`（QQ/163 授权码）
2. `.\scripts\prepare-multiuser-beta.ps1 -HardenEnv`（同步进 `.env`，`EXPOSE_OTP_IN_RESPONSE=false`）
3. 重启 Dev Lite / BFF 后复测收信

## 4. Docker 量产栈

需 **WSL2** + Docker Desktop = Running，再 `.\scripts\prepare-multiuser-beta.ps1 -Up`  
（或 `.\scripts\up-docker-stack.ps1`）。  
**Expo Go / 临时隧道内测可先不依赖 Docker。**

## 5. 公网 HTTPS + EAS / TestFlight（主线 A）

开发侧脚本已齐；你需要：

1. 安装 `cloudflared`：`winget install Cloudflare.cloudflared`
2. 按 `INTERNAL_BETA_OPS_CHECKLIST.md` §0 跑：`-HardenEnv` → Dev Lite → `start-public-tunnel.ps1 -ApplyEas`
3. `curl.exe -sS https://….trycloudflare.com/health` → `allow_mock_preview: false`
4. `powershell -File scripts/check-internal-beta-ready.ps1` 无 FIX
5. `eas login` 后：
   ```powershell
   cd E:\AI耳机\diary-one\apps\mobile
   eas build --profile preview --platform ios
   ```
6. （可选）把 `eas.json` 里 `REPLACE_WITH_APP_STORE_CONNECT_APP_ID` 换成真实 ASC App ID 再 `eas submit`

临时隧道 URL 每次变都要重写 eas 并重新 build。稳定域名见 `services/bff/docs/DEPLOY.md`。

## 6. BLE

暂缓；见 `WINDOWS_IOS_DEV_CLIENT_VISION.md`。需硬件合同后再接真 transport。

## 7. 验收

`TEST_PLAN.md` → `TEST_LOG.md`；对照 `FIGMA_04_COVERAGE.md`。
