# 需要你补充的事项（开发侧已就绪）

代码侧已按路线图完成：**共享 OTP/SMTP、session Bearer 鉴权、Dev Lite 与量产 BFF 对齐、App 相册导入主链、登录 session 贯通云 API**。下列项依赖你的账号/密钥/硬件，无法由仓库单独完成。

## 0. Daily Recap 视频（Expo Go）

1. PC 安装 **ffmpeg** 并加入 PATH（`ffmpeg -version`）
2. Dev Lite 健康检查：`ffmpeg_available: true`
3. 手机 BFF URL 指向 PC → Diary → Share day → **Daily Recap**

详见 `docs/DAILY_RECAP_VIDEO.md`。iOS Dev Client 可不走 PC，用本机 `expo-video-encoder`。

## 1. 真云（P2）

1. [百炼控制台](https://bailian.console.aliyun.com/) 创建 **API Key**（`sk-…`）
2. `services/bff/scripts/set-dashscope-key.ps1 -Key 'sk-…'`
3. `.\scripts\start-dev-lite.ps1`（默认 qwen，**关 mock**）
4. 手机 Lab：**Apply → Ping**（`x02.reachable=true`）→ Demo 或 Diary **Import from library**

## 2. 真邮件 OTP（商用验收）

1. 准备 SMTP（发信域名、端口、账号）
2. `.\scripts\set-smtp.ps1` 或 User 环境变量 `SMTP_*`
3. 设 `EXPOSE_OTP_IN_RESPONSE=false` 后复测登录（不应再回传 `dev_code`）

## 3. Docker 量产栈（P3，可选本机）

```powershell
cd services/bff
copy .env.example .env
docker compose up -d --build
docker compose run --rm bff python -m shared.db_init
.\scripts\smoke-docker.ps1
```

Worker 需宿主机 X02 `:8787` 或容器内可达的算法地址。

## 4. EAS / TestFlight（暂缓 IPA 时可跳过）

- Apple Developer 账号
- `docs/WINDOWS_IOS_DEV_CLIENT_VISION.md`：Windows 用 EAS 云构建 Dev Client（真 Apple Vision）

## 5. 硬件（P3 后）

- BLE 配对与 `deviceLinkState` 真接线（当前 Onboarding 配对为 **UI 流程**，Device Tab 仍为 Not connected）

## 6. 建议你做的验收

- `docs/TEST_PLAN.md` 中 P0/P1 用例打勾 → 记入 `docs/TEST_LOG.md`
- 主链四 Tab + Share 四条 flow 目视对照 `apps/mobile/docs/FIGMA_04_COVERAGE.md`

有新任务可直接在本文件下方追加，或开 Issue。
