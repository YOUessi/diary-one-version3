# 需要你补充的事项（开发侧已就绪）

开发侧可做项见 `docs/REMAINING_GAPS.md`。下列依赖你的账号/密钥/硬件/真机。

**Expo Go 内测操作卡：** `docs/EXPO_GO_INTERNAL_BETA.md`  
**手机一次试全功能：** `docs/PHONE_FULL_TEST.md`

## 0. 现在就能真机内测（优先）

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

1. `set-smtp.ps1`
2. `EXPOSE_OTP_IN_RESPONSE=false` 复测

## 4. Docker 量产栈

需 **WSL2** + Docker Desktop = Running，再 `.\scripts\up-docker-stack.ps1`。  
**Expo Go 内测不依赖 Docker。**

## 5. EAS / TestFlight · 6. BLE

暂缓；见 `WINDOWS_IOS_DEV_CLIENT_VISION.md`。

## 7. 验收

`TEST_PLAN.md` → `TEST_LOG.md`；对照 `FIGMA_04_COVERAGE.md`。
