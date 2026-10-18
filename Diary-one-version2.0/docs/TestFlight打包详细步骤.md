# Diary One 内测 · 同事后续详细步骤（TestFlight）

> **后续补修优先于下文历史版本说明：** 当前云端 release 是 `v2-20261018T145747Z`，已部署完整结果校验并重跑真实模型链路通过。App 新增输入绑定、事务发布、日期/来源、小记忆保留及资料保存修复，须用当前源码重新构建；先读 [生成链路补修](生成链路补修_2026-10-18.md)。health 应返回此新版本。HQ 派生媒体仍未实现，真实素材和真机质量仍待验收。

> **登录问卷新增修改：** 构建时须包含本轮 `PreferenceSurveyScreen`、`surveyTagLibrary`、`surveyProfile` 以及本地回答状态/保存链路改动。先读 [登录问卷实现与验收](登录偏好问卷_实现与验收_2026-10-18.md)，按其中清单完成 iPhone 截图、键盘、返回、重开验证；本次没有提交新的 TestFlight 包。

> **2026-10-18 最终核查（模型修正后）：** BFF/Worker/X02 已部署 `v2-20261018T145747Z`；X02 已切换 `qwen3.8-flash`，同 Key 真实调用及合成图片完整生成链路通过，403 已解除。真实照片/视频真机质量仍待验收。可构建团队验证包，不能称商用放行。先读 [最终 PRD 与算法核查](最终核查_PRD与算法_2026-10-18.md) 的 B01–B12 和 [总交接](TEAM_PACK_HANDOFF.md)。前端尚有已知合同差异，未全画板真机验收；preview 已为 store 分发，仍须签名、Vision 原生编译和真机测试。Google 需 App 和服务器两处配置。


**历史仓库位置：** `https://github.com/Nexleap-Tech/Diary_one/tree/main/Diary-one-version2.0`（交接时核对本轮 commit SHA）
**工作目录：** 本轮交付快照或已确认提交内的 `Diary-one-version2.0/apps/mobile`
**Bundle ID：** `com.nexleap.diaryone.dev`
**云端 BFF（已写进 eas.json，勿改）：** `https://bff.diary.luxe`

云主机保存 DashScope、SMTP、API_TOKEN，**不要**写进 App 或 Git。SMTP 只确认配置存在；DashScope 当前 Key 允许 `qwen3.8-flash`，云端配置及调用已验证，保留该模型覆盖。新模型费用须按百炼账单校准。

---

## 0. 开始前准备

你需要有权限登录：

| 账号 | 用途 |
|------|------|
| Apple Developer / App Store Connect | Sign in with Apple、建 App、收 TestFlight |
| Expo / EAS 账号 | `eas build` / `eas submit` |
| （可选）Google Cloud | 只有要启用「Continue with Google」时才需要 |

本机建议：

- Node.js 24.16.x（本轮实测版本；勿继续使用旧 Node 18）
- Git
- 能访问 GitHub、expo.dev、developer.apple.com

先确认云端还活着（任选网络能访问的机器）：

```powershell
curl.exe -sS https://bff.diary.luxe/health
```

期望 `deployment_revision` 为 `v2-20261018T145747Z`、`status=ok`、`allow_mock_preview=false`、`smtp_configured=true`、`x02.reachable=true`。这些只证明运行和配置；2026-10-18 另有 `qwen3.8-flash` 真实完整链路成功记录，见部署文档，真机仍须独立验收。
若整段失败，先找负责云主机的人看 ECS 是否 Running，不要自己改 App 里的 BFF 地址。

---

## 1. 获取本轮准确源码

从指定 GitHub 仓库拉取本轮交接的 commit SHA，并进入 `Diary-one-version2.0/apps/mobile`；不要使用本机旧缓存或同级旧 apps/mobile。

```powershell
cd <交付目录>\Diary-one-version2.0\apps\mobile
npm ci
npm run typecheck
npm run lint -- --no-cache
npm run test:core
```

之后只在这个目录进行构建。若使用 Git 交接，记录实际 commit SHA 和工作区状态；若使用源码快照，记录交付摘要。测试使用 Node 24.16.x；Windows 测试子进程受权限限制时应重跑，不能记作通过。

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

服务端也要配置：由云负责人在现有 `.env` 加入 `GOOGLE_CLIENT_IDS=<Web ID>,<iOS ID>`，使用部署记录中带 release overlay 的 compose 命令重建 BFF。未配置会按新安全校验返回 503，不能通过放宽校验绕过。

注意：改完 `eas.json` 的 env 后必须重新 `eas build`，已装的旧包不会自动带上新 Client ID。

未填时：登录页仍有 Google 按钮，点击会提示缺少 Client ID；不影响 Apple / 邮箱。

---

## 5. 确认 eas.json 里 preview 关键配置

preview 的 `distribution` 必须保持 `store`，`ios.simulator=false`。本轮只按 preview 构建；production 的环境与正式发布范围需另行核查，不可直接复制内测成功结论。

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
npx eas-cli@latest login
npx eas-cli@latest whoami
npx eas-cli@latest build --profile preview --platform ios
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
npx eas-cli@latest submit --profile preview --platform ios --id <本轮成功的EAS构建ID>
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
5. Key 403 已通过切换 `qwen3.8-flash` 解决；继续用授权照片和视频测试真机生成。Today / Diary 只显示准入的真实记忆；允许 honest empty，但模型失败必须显示失败，不能记成空日或验收通过。重开确认结果仍可读，保留任务/版本/耗时和费用记录。
6. 继续按最终核查的 B03–B12 和 PRD T01–T12 验证来源、未知时间、历史小记忆、媒体引用、补记、分享、账号及 Figma 真机状态；不能只测试一次生成。
7. 确认流量打到 `https://bff.diary.luxe`（手机需能访问公网；公司网络若拦 HTTPS 可换手机蜂窝试一次）。

---

## 9. 出问题怎么查

| 现象 | 处理 |
|------|------|
| `curl https://bff.diary.luxe/health` 失败 | 找云主机负责人；确认 ECS Running。不要改 App 的 BFF URL 去绕临时隧道 |
| 收不到邮箱验证码 | 云端 SMTP 已配过；查垃圾箱；确认填的是测试员自己的邮箱。仍不行找运维看服务器 `.env` 里 SMTP，**不要**把授权码发到群里 |
| Apple 登录失败 / 没弹窗 | 确认 Identifier 已勾 Sign in with Apple 且 **重新 eas build** 后再装 |
| Google 按钮提示缺 Client ID | 完成第 4 步并重新 build |
| `eas submit` 报 ascAppId | 检查 `eas.json` 是否仍是 `REPLACE_WITH_APP_STORE_CONNECT_APP_ID` |
| 任务报 MODEL_HTTP_403 / API-Key restrictions | 本次旧模型访问限制已通过 `qwen3.8-flash` 解决；如再出现，先核对 X02 实际模型与 Key 允许范围、工作空间限制，保留失败记录；不能靠改 App URL 或开启 mock 解决 |
| health 绿但没有生成结果 | health 不做真实模型调用；检查对应 job，区分供应商失败、准入阻断和 honest empty |
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
npm ci
npx eas-cli@latest login
npx eas-cli@latest build --profile preview --platform ios
npx eas-cli@latest submit --profile preview --platform ios --id <本轮成功的EAS构建ID>
```

完成后：记录实际 build ID、App 版本/构建号和 `v2-20261018T145747Z` 云 release → 团队测试组安装 → 按第 8 节及最终核查验收。未关闭 P0/生成阻塞前，不扩大真实素材测试，不填写商用放行。
