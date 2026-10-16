# 商用级交付路径 vs 当前 Expo Go 联调

## 先说清边界（避免误解）

| 目标 | 用什么 | 说明 |
|------|--------|------|
| **现在：商用形态联调** | Expo Go + Dev Lite BFF + X02 | 同一套正式 UI / API 合同；可测登录 OTP、相册→云→Diary |
| **上架：商用发布** | EAS `production` / TestFlight → App Store | **不能**用 Expo Go 上架；需 Apple 开发者、隐私 URL、真发信或明确内测说明 |

Expo Go = 用商店里的壳跑你的 JS。**商用级产品代码可以在 Go 里验**，但最终用户安装的是签名 IPA。

---

## 你需要下载 / 开通的东西

### A. 今天联调（必做）

| 项 | 下载 / 开通 | 状态 |
|----|-------------|------|
| **Expo Go**（手机） | App Store / 应用商店，Client **57.x**，Supported SDKs **57** | 你已有 |
| **Node.js 20+**（电脑） | https://nodejs.org | 工程已用 |
| **Python 3.10+**（电脑） | https://www.python.org | 已能跑 BFF/X02 |
| **本仓库 monorepo** | `diary-one/apps/mobile` + `services/bff` + `services/algorithm` | `E:\AI耳机\diary-one` |

### B. 真算法质量（强烈建议，商用记忆生成）

| 项 | 你要做的 |
|----|----------|
| **阿里云百炼 API Key** | 控制台开通 DashScope，复制 Key |
| 写入用户环境变量 | `DASHSCOPE_API_KEY=sk-...`（不要提交 Git） |
| 启动 | `.\scripts\start-dev-lite.ps1 -Adapter qwen` |

没有 Key 也能测全流程（fixture + Mock Diary），但**不能声称算法质量**。

### C. 上架商用（后续，非 Expo Go）

| 项 | 你要做的 |
|----|----------|
| **Apple Developer Program**（99 美元/年） | 账号 + App ID `com.nexleap.diaryone` |
| **EAS 账号** | `npm i -g eas-cli` → `eas login` |
| **隐私政策 / 条款 HTTPS** | 填入 App 与 App Store Connect |
| **真实 SMTP / 邮件 OTP** | 企业邮或云邮件；关掉 `expose_otp_in_response` |
| （可选）**Docker Desktop** | 量产 Postgres/Redis/MinIO；Dev Lite 已可联调，不挡上架前功能验收 |

---

## 本机已为你配置的

- Dev Lite BFF `:8790` + X02 fixture `:8787`（无 Docker）
- App `.env` → `EXPO_PUBLIC_DEV_BFF_URL=http://<LAN>:8790`
- 启动后自动把 Production BFF / Token / cloud target 写入本机（见 `applyDevCloudDefaults`）
- 防火墙脚本放行 8790（需管理员跑一次）
- OTP 内测弹窗 `dev_code`；相册导入走 BFF job

一键自检：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\setup-commercial-dev.ps1
.\scripts\start-dev-lite-background.ps1
```
