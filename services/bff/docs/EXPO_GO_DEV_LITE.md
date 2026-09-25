# Expo Go · 无 Docker 全链路（P3/P4 内测）

你的电脑**不需要 Docker**。手机只连 **Dev Lite BFF :8790**；算法 X02 只在本机 `127.0.0.1:8787`。

## 你现在需要提供 / 准备的

| 项 | 是否必须 | 说明 |
|----|----------|------|
| 手机 ↔ 电脑 **同一 Wi‑Fi** | **必须** | 否则 Expo Go 连不上 `:8790` |
| Windows 防火墙放行 **8790** | **必须** | 首次进站提示允许，或手动入站规则 |
| **`DASHSCOPE_API_KEY`**（阿里云百炼） | 真算法必须 | **今天没有 Key 也能测全流程**：用 fixture + Mock 回写 Diary |
| 真实 SMTP 发信 | 暂不必须 | OTP 在 API 响应里返回 `dev_code`，App 会弹窗显示 |
| Docker / Postgres / Redis / MinIO | 暂不必须 | 量产形态；Dev Lite 替代 |

把 Key 设进用户环境变量（不要提交到 Git）：

```powershell
[System.Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-你的密钥", "User")
```

新开终端后生效。

## 一键起后端（两窗口）

```powershell
cd E:\AI耳机\diary-one-server
# 先打通管线（无 Key）：
.\scripts\start-dev-lite.ps1 -Adapter fixture

# 有 Key、要真实 V1.75：
.\scripts\start-dev-lite.ps1 -Adapter qwen
```

浏览器打开脚本打印的：`http://<LAN>:8790/health`  
应看到 `"mode":"dev_lite"`，且 fixture 时 X02 `reachable: true`。

## 手机 Expo Go 配置

1. 开 App（Metro 已起）→ **Skip to Diary** 或走完登录。
2. **Account → Evidence pipeline lab**
3. **Cloud processing target → Production BFF**
4. Production API：`http://<你的局域网IP>:8790`
5. Token：`dev-token`
6. **Import from photo library** → 选 1～3 张图
7. 回 **Diary**：云处理横幅 → 出现新 Chapter / Small Memory

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

App 对接 API 形状相同：`/v1/day-revisions`、`/v1/jobs/{id}`、`/v1/auth/otp/*`。
