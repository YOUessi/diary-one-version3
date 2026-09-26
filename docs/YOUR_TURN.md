# 需要你补充的事项（开发侧已就绪）

开发侧可做项见 `docs/REMAINING_GAPS.md`。下列依赖你的账号/密钥/硬件。

## 0. Daily Recap 视频（Expo Go）

1. PC 安装 **ffmpeg**（`services/bff/scripts/install-ffmpeg-windows.ps1`）
2. Dev Lite：`ffmpeg_available: true`
3. 手机 Share day → Daily Recap

## 1. 真云（P2）

1. 百炼 API Key → `set-dashscope-key.ps1`
2. `start-dev-lite.ps1`（默认 qwen）
3. Lab Ping → Demo

## 2. 真邮件 OTP

1. `set-smtp.ps1`
2. `EXPOSE_OTP_IN_RESPONSE=false` 复测

## 3. Docker 量产栈

见 `services/bff/README.md`（healthcheck 已加）。

## 4. EAS / TestFlight · 5. BLE

暂缓；见 `WINDOWS_IOS_DEV_CLIENT_VISION.md`。

## 6. 验收

`TEST_PLAN.md` → `TEST_LOG.md`；对照 `FIGMA_04_COVERAGE.md`。
