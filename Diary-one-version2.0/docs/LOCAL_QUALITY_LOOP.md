# 本机真质量闭环（优先 · TestFlight 可后置）

目标：同一 Wi‑Fi 下，**正式用户 App**（Expo Go 默认无 Lab）+ **真 DashScope + mock=false + OTP**，相册 Import → Diary。  
验收口径：[`FORMAL_APP_ACCEPTANCE.md`](./FORMAL_APP_ACCEPTANCE.md)。  
**不做**本轮：`eas build` / TestFlight；工程师 Demo 须显式 `EXPO_PUBLIC_ENABLE_LAB=1`。

## 0. 一次性准备（PC）

```powershell
cd E:\AI耳机\diary-one\services\bff

# DashScope（若尚未设置）
.\scripts\set-dashscope-key.ps1 -Key 'sk-...'

# SMTP 真收信（若尚未设置；有则 OTP 不回显 dev_code）
.\scripts\set-smtp.ps1 -SmtpHost smtp.qq.com -Port 465 -User 'you@qq.com' -Password '授权码' -From 'you@qq.com'

# 一键：harden .env + 后台起 qwen Dev Lite
.\scripts\start-quality-loop.ps1
```

通过标准（脚本末尾 Quality gate）：

| 检查 | 期望 |
|------|------|
| `allow_mock_preview` | `false` |
| X02 | reachable |
| `provider` | **不是** `fixture`（应为 dashscope / qwen 类） |
| SMTP | 已配置更佳；未配则 OTP 可能仍暴露 `dev_code` |

Lab Ping 应看到 **`mock=no`**（不是 mock=yes）。

手机 `.env` / Lab Apply 指向当前 LAN，例如 `http://192.168.x.x:8790`。IP 变了跑：

```powershell
.\scripts\setup-commercial-dev.ps1 -OpenFirewall
```

## 1. 手机最短路径（相册 → Diary）

1. 手机与 PC **同一 Wi‑Fi**；Expo Go 扫 Metro 二维码  
2. **Account → Continue with Email → OTP**（有 SMTP 查邮箱；无则看弹窗/dev_code）  
3. **Privacy / 问卷**：Allow cloud evidence  
4. **Lab（__DEV__）**：Apply .env → **Ping**（`mock=no` · x02=up）  
5. **Device → Import photos**（内测）或 Lab **Demo photo → cloud → Diary**  
6. Diary：Preparing → Ready；点进 Chapter，文案/图可认；无媒体则诚实「Media unavailable」  
7. 失败：不抹旧 Ready；可同图重试  

详细勾选仍可用 `PHONE_FULL_TEST.md`，但质量闭环以本节 **mock=no + 真 Chapter** 为准。

## 2. 纪律（PRD）

- App 内测包拒 mock 结果（AI03）——本机质量路径也必须 `ALLOW_MOCK_PREVIEW=false`  
- 不要用 `start-dev-lite-background.ps1 -Adapter fixture` 当质量验收  
- `API_TOKEN` 仅 Lab；多人用 OTP，勿群发长 token  
- TestFlight / 公网隧道：**后置**；见 `INTERNAL_BETA_OPS_CHECKLIST.md` §0  

## 3. 常见失败

| 现象 | 处理 |
|------|------|
| Ping `mock=yes` / provider=fixture | `set-dashscope-key` 后 `start-quality-loop.ps1` |
| Demo 空日记 / job failed | 看 BFF/X02 日志；确认 Key 非 `sk-sp-` |
| OTP 无邮件 | `set-smtp.ps1` + 重启；或临时看 `expose_otp` |
| Android 选图挂 | 用 Lab Demo；或串行 Add another |

## 4. 下一步

质量闭环跑通后 → [`ALGORITHM_CONTENT_REVIEW.md`](./ALGORITHM_CONTENT_REVIEW.md) 做 Citywalk / 陪伴分层抽检。  
发几十人包时再回到公网隧道 + `eas build`。
