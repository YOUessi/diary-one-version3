# Diary One 内测 · 同事后续详细步骤（TestFlight）

**仓库路径：** `https://github.com/Nexleap-Tech/Diary_one/tree/main/Diary-one-version2.0`  
**工作目录：** 克隆后进入 `Diary-one-version2.0/apps/mobile`  
**Bundle ID：** `com.nexleap.diaryone.dev`  
**云端 BFF（已写进 eas.json，勿改）：** `https://bff.diary.luxe`

云主机上的 DashScope、SMTP、API_TOKEN 已经配好，**不用也不要**写进 App 或 Git。

---

## 0. 开始前准备

你需要有权限登录：

| 账号 | 用途 |
|------|------|
| Apple Developer / App Store Connect | Sign in with Apple、建 App、收 TestFlight |
| Expo / EAS 账号 | `eas build` / `eas submit` |
| （可选）Google Cloud | 只有要启用「Continue with Google」时才需要 |

本机建议：

- Node.js 18+（或团队常用版本）
- Git
- 能访问 GitHub、expo.dev、developer.apple.com

先确认云端还活着（任选网络能访问的机器）：

```powershell
curl.exe -sS https://bff.diary.luxe/health
```

期望 JSON 里大致有：`status` 为 ok、`smtp_configured` 为 true、`x02.reachable` 为 true。  
若整段失败，先找负责云主机的人看 ECS 是否 Running，不要自己改 App 里的 BFF 地址。

---

## 1. 拉取代码

```powershell
git clone https://github.com/Nexleap-Tech/Diary_one.git
cd Diary_one\Diary-one-version2.0\apps\mobile
npm install
```

以后只在这个目录做打包相关修改。更完整的交接摘要见同目录上级的 `docs/TEAM_PACK_HANDOFF.md`。

---

## 2. Apple：给 Bundle ID 勾选 Sign in with Apple

1. 打开 [Apple Developer](https://developer.apple.com/account) 并登录公司账号。
2. 左侧进入 **Certificates, Identifiers & Profiles** → **Identifiers**。
3. 在列表里找到 **`com.nexleap.diaryone.dev`**。  
   - 若没有：点 **+** → App IDs → App → Description 自定 → Bundle ID 选 Explicit，填 **`com.nexleap.diaryone.dev`**（一字不差）。
4. 打开该 Identifier，在 Capabilities 里勾选 **Sign in with Apple**。
5. 点 **Configure**（一般保持默认 Primary App ID），然后 **Save** → 确认保存。
6. 等几分钟让配置生效。之后必须用 **新的 EAS 构建** 才会带上该能力（改完后台却不重打 IPA 无效）。

---

## 3. App Store Connect：创建 App，拿到数字 Apple ID

1. 打开 [App Store Connect](https://appstoreconnect.apple.com) → **我的 App** → **+** → **新建 App**。
2. 填写：
   - 平台：iOS
   - 名称：内测可用，如 `Diary One Dev`（以公司规范为准）
   - 主要语言：按公司选择
   - Bundle ID：选 **`com.nexleap.diaryone.dev`**
   - SKU：自定唯一字符串（如 `diary-one-dev-001`）
3. 创建后进入该 App → **App 信息**（或页面 URL / 常规信息里）找到数字 **Apple ID**（一串数字，不是 Bundle ID）。
4. 用编辑器打开：

   `Diary-one-version2.0/apps/mobile/eas.json`

5. 找到：

```json
"submit": {
  "preview": {
    "ios": {
      "ascAppId": "REPLACE_WITH_APP_STORE_CONNECT_APP_ID"
    }
  }
}
```

6. 把 `REPLACE_WITH_APP_STORE_CONNECT_APP_ID` 换成刚才的数字 Apple ID（只保留数字，不要引号外多余空格）。`production` 段可暂不改，本轮只用 **preview**。

---

## 4.（可选）Google：填 Client ID

邮箱 OTP 和 Apple 登录不依赖本步。只有要让「Continue with Google」真正可用时才做。

1. 打开 [Google Cloud Console](https://console.cloud.google.com)，选中或新建项目。
2. 配置 **OAuth 同意屏幕**（External 即可；测试阶段把内测邮箱加进测试用户）。
3. **凭据** → **创建凭据** → **OAuth 客户端 ID**：
   - 类型 **Web 应用**：创建后复制 **客户端 ID**。
   - 再创建一个类型 **iOS**：Bundle ID 填 **`com.nexleap.diaryone.dev`**，复制 **客户端 ID**。
4. 仍编辑 `eas.json` → `build.preview.env`，在现有字段旁增加（值换成你的）：

```json
"EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID": "xxxx.apps.googleusercontent.com",
"EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID": "yyyy.apps.googleusercontent.com"
```

注意：改完 `eas.json` 的 env 后必须重新 `eas build`，已装的旧包不会自动带上新 Client ID。

未填时：登录页仍有 Google 按钮，点击会提示缺少 Client ID；不影响 Apple / 邮箱。

---

## 5. 确认 eas.json 里 preview 关键配置

打包前再扫一眼 `build.preview.env`，应类似：

| 键 | 期望值 |
|----|--------|
| `EXPO_PUBLIC_INTERNAL_BETA` | `1` |
| `EXPO_PUBLIC_STORE_RELEASE` | `0` |
| `EXPO_PUBLIC_DEV_BFF_URL` | `https://bff.diary.luxe` |
| `EXPO_PUBLIC_DEV_BFF_TOKEN` | 空字符串 `""` |
| Google 两项 | 可选，见上一节 |

**不要**改回任何 trycloudflare / 临时隧道地址。  
**不要**把服务器上的 `API_TOKEN`、DashScope Key、SMTP 密码写进 `eas.json`。

`app.json` 里应已有：

- `ios.bundleIdentifier`: `com.nexleap.diaryone.dev`
- `ios.usesAppleSignIn`: `true`

---

## 6. EAS 登录并构建 iOS preview

在 `Diary-one-version2.0/apps/mobile` 下：

```powershell
npx eas-cli login
npx eas-cli whoami
npx eas-cli build --profile preview --platform ios
```

说明：

1. 首次在该项目跑 EAS 时，若提示创建 / 关联 Expo 项目，按提示选团队已有项目或新建，并与 Apple 团队配对。
2. 若提示需要 Apple 登录或 App Store Connect API Key，用公司 Apple 账号完成；证书与描述文件一般交给 EAS 托管即可（选 managed / 让 EAS 生成）。
3. 构建在 Expo 云端执行，通常十几到几十分钟。完成后在终端或 [expo.dev](https://expo.dev) 打开 build 页面，确认状态为 **finished**，记下 IPA / build 链接。

构建失败常见原因：

- Bundle ID 与 Apple 后台不一致
- 未勾选 Sign in with Apple 却依赖该能力（勾完后重新 build）
- Apple 团队权限不足 / 协议未签

---

## 7. 提交到 TestFlight

`ascAppId` 已填正确数字后：

```powershell
npx eas-cli submit --profile preview --platform ios
```

也可在 expo.dev 的该次 build 页面点 **Submit**，选 App Store Connect。

然后到 App Store Connect：

1. 打开对应 App → **TestFlight**。
2. 等处理完成（有时还要点一次「合规 / 出口合规」等问卷，按内测实际情况填；无加密或仅 HTTPS 时按公司法务口径）。
3. **内部测试**（或外部测试）里添加测试员 / 测试组。
4. 测试员在 iPhone 上安装 **TestFlight**，接受邀请后安装本构建。

---

## 8. 安装后验收（内测范围）

本轮 **不测耳机 BLE**；设备页保持未连接即可。

建议路径：

1. 打开 App → 登录页应看到 **Apple / Google / Email**。
2. 任选一种登录：
   - **Apple**：系统 Apple 账号弹窗 → 成功进 App
   - **邮箱**：填测试员自己的邮箱 → 收 OTP → 登录
   - **Google**：仅在已填 Client ID 时测
3. 同意云 Evidence / 隐私相关提示（若有）。
4. 用相册导入 **图片和/或视频**（本轮主路径是相册导入，不是耳机采集）。
5. 等待云端处理，Today / Diary 出现 **Chapter**（通义链路，可能需数分钟）。
6. 确认流量打到 `https://bff.diary.luxe`（手机需能访问公网；公司网络若拦 HTTPS 可换手机蜂窝试一次）。

---

## 9. 出问题怎么查

| 现象 | 处理 |
|------|------|
| `curl https://bff.diary.luxe/health` 失败 | 找云主机负责人；确认 ECS Running。不要改 App 的 BFF URL 去绕临时隧道 |
| 收不到邮箱验证码 | 云端 SMTP 已配过；查垃圾箱；确认填的是测试员自己的邮箱。仍不行找运维看服务器 `.env` 里 SMTP，**不要**把授权码发到群里 |
| Apple 登录失败 / 没弹窗 | 确认 Identifier 已勾 Sign in with Apple 且 **重新 eas build** 后再装 |
| Google 按钮提示缺 Client ID | 完成第 4 步并重新 build |
| `eas submit` 报 ascAppId | 检查 `eas.json` 是否仍是 `REPLACE_WITH_APP_STORE_CONNECT_APP_ID` |
| 云端健康检查里 `x02.reachable=false` | 让有 SSH 权限的人在 ECS 执行：`sudo systemctl restart diary-x02 diary-x02-socat`，再查 `/health` |

---

## 10. 明确不要做的事

- 不要把 DashScope Key、SMTP 授权码、服务器 `API_TOKEN` 写进 App、`eas.json` 或公开聊天
- 不要把 `EXPO_PUBLIC_DEV_BFF_URL` 改回 trycloudflare 或其它临时隧道
- 不要在本轮对接真耳机 / BLE 配对作为验收必要条件
- 不要把本目录当成「上架正式版」；正式店版 Bundle 另议（如 `com.nexleap.diaryone`）

---

## 11. 最短命令清单（做完 2～4 节配置之后）

```powershell
cd <clone>\Diary_one\Diary-one-version2.0\apps\mobile
npm install
npx eas-cli login
npx eas-cli build --profile preview --platform ios
npx eas-cli submit --profile preview --platform ios
```

完成后：TestFlight 加内部测试员 → 按第 8 节验收。
