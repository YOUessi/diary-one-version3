# Expo Go · 无 Docker 全链路（内测）

你的电脑**不需要 Docker**。手机只连 **Dev Lite BFF :8790**；算法 X02 只在本机 `127.0.0.1:8787`。

## 你现在需要提供 / 准备的

| 项 | 是否必须 | 说明 |
|----|----------|------|
| 手机 ↔ 电脑 **同一 Wi‑Fi** | **必须** | 否则 Expo Go 连不上 `:8790` |
| Windows 防火墙放行 **8790** | **必须** | 管理员跑一次 `.\scripts\setup-commercial-dev.ps1 -OpenFirewall` |
| **`DASHSCOPE_API_KEY`**（阿里云百炼） | 真算法必须 | **今天没有 Key 也能测全流程**：fixture + Mock 回写 Diary |
| 真实 SMTP 发信 | 暂不必须 | OTP 在 API 响应里返回 `dev_code`，App 会弹窗显示 |
| Docker / Postgres / Redis / MinIO | 暂不必须 | 量产形态；Dev Lite 替代 |
| 本机 **ffmpeg** | Daily Recap 必须 | `install-ffmpeg-windows.ps1`；health 里 `ffmpeg_available: true` |

把 Key 设进用户环境变量（不要提交到 Git）：

```powershell
[System.Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-你的密钥", "User")
```

新开终端后生效。

## 一键起后端

```powershell
cd E:\AI耳机\diary-one\services\bff

# 写入 App .env（当前 LAN IP）
.\scripts\setup-commercial-dev.ps1

# 无弹窗后台起栈（fixture + mock，适合无 Key 内测）
.\scripts\start-dev-lite-background.ps1

# 或开两个窗口（默认 qwen 需 Key；无 Key 用 fixture）：
# .\scripts\start-dev-lite.ps1 -Adapter fixture

.\scripts\smoke-dev-lite.ps1
.\scripts\smoke-recap.ps1
```

浏览器打开脚本打印的：`http://<LAN>:8790/health`  
应看到 `"mode":"dev_lite"`，`x02.reachable: true`，Recap 时 `ffmpeg_available: true`。

## 手机 Expo Go 配置

1. 电脑：`cd E:\AI耳机\diary-one\apps\mobile` → `npx expo start --go --lan`
2. 手机 Expo Go SDK **57** 扫码 / 同网打开
3. **Skip to Diary** 或走完登录（OTP 弹窗码）
4. **Account → Evidence pipeline lab**
5. **1 · Apply .env BFF defaults**（或手填 `http://<电脑局域网IP>:8790` · Token `dev-token`）
6. **2 · Ping BFF /health** → 应见 `OK · x02=up · ffmpeg=yes`
7. **0 · Offline mock** → 回 Diary 确认 UI
8. **A · Demo photo → cloud → Diary** → Active tasks 成功后看 Diary 新章节  
   （Android 相册常挂：用 A，不要依赖 B）

登录 OTP：

1. Sign in 填邮箱 → Continue  
2. 弹窗会显示 **dev_code**（内测）→ 输入该 6 位 → Continue  

## 与正式量产的关系

| | Dev Lite（现在） | Docker 量产（以后） |
|--|------------------|---------------------|
| 存储 | 本机 `dev_lite/data/` | Postgres + MinIO |
| 队列 | asyncio 任务 | Redis + Worker |
| OTP | JSON `dev_code` | 真实邮件 |
| 算法 | 同 X02 / V1.75 | Worker 调同一 X02 |

App 对接 API 形状相同：`/v1/day-revisions`、`/v1/jobs/{id}`、`/v1/auth/otp/*`、`/v1/share/daily-recap/render`。
