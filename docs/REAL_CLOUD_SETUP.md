# 真云接入（百炼 + 真邮件 OTP）

**原则：所有质量相关路径必须真跑。** fixture / Mock preview 仅本机 UI 排障，不计入验收。

---

## 1. 阿里云百炼 DashScope（算法 V1.75）— 必做

新人有免费 Token 额度（华北2 北京，约 90 天），够 Expo Go 真链验收。

1. 打开 [百炼控制台](https://bailian.console.aliyun.com/) → 右上角选 **华北2（北京）** → 同意开通  
2. 进入 [API Key](https://bailian.console.aliyun.com/?tab=model#/api-key) → **创建 API Key**  
3. 复制 **通用** Key（`sk-…`）。不要用 `sk-sp-` / `sk-ws-` 套餐专属 Key  
4. 本机写入（不要提交 Git、不要贴到聊天）：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\set-dashscope-key.ps1 -Key "sk-你的密钥"
.\scripts\start-dev-lite.ps1
```

默认已是 `-Adapter qwen`，且 **关闭** `allow_mock_preview`。  
手机 Lab → Demo：必须等真 X02 成功才写 Diary；失败会 Task Failed（不再假绿）。

健康检查：浏览器打开 `http://<LAN>:8790/health`  
- `x02.detail.provider` 应为 qwen / modelReady=true  
- `allow_mock_preview` = false  

---

## 2. 真邮件 OTP（SMTP）— 必做（你说全部要真）

任选免费通道之一：

| 方案 | 怎么拿 |
|------|--------|
| **163 邮箱** | 设置 → POP3/SMTP → 开启 → 生成**授权码**；主机 `smtp.163.com` 端口 `465` SSL |
| **QQ 邮箱** | 设置 → 账户 → POP3/SMTP → 授权码；`smtp.qq.com:465` SSL |
| **Resend / Brevo** | 各自控制台 SMTP（有免费额度） |

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\set-smtp.ps1 -SmtpHost smtp.163.com -Port 465 -User "你@163.com" -Password "授权码" -From "你@163.com"
.\scripts\start-dev-lite.ps1
```

配好后：`expose_otp_in_response=false`，App **不再弹窗码**，请查收邮件。  
`/health` 里 `smtp_configured=true`。

---

## 3. 手机复测（真云）

1. 关掉旧的 fixture X02/BFF 窗口，只用新开的两扇  
2. Expo Go → Lab：**Apply → Ping**（`x02=up`）→ **A Demo**  
3. Sign-in：填真实邮箱 → 查邮件 OTP → Continue  

---

## 4. 安全

- Key / 授权码只进 **Windows User 环境变量** 或本机 `.env`（已 gitignore）  
- 禁止写进仓库、Issue、截图发群  
- 额度：百炼控制台可开「免费额度用完即停」

把 Key 配好后跟我说一声「Key 好了」，我帮你起栈并盯 `/health` 是否 `modelReady=true`。
