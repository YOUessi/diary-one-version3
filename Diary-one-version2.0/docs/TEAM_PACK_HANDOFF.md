# Diary One · 交给打包同事的交接（2026-10-16）

云端后端与登录 UI 已在本机仓库 + 阿里云上就绪。  
**Apple Developer 后台、Google Cloud 控制台必须用公司账号点一次**（代理无法登录这两个网站）。点完后只剩 EAS 打包。

---

## 已完成（不用再做）

| 项 | 状态 |
|----|------|
| ECS `47.111.96.5` · Ubuntu | 在跑 |
| 域名 `https://bff.diary.luxe` → Caddy → BFF `:8790` | `/health` 绿 |
| Docker：BFF / Worker / Postgres / Redis / MinIO | 在跑 |
| X02 通义（宿主机 `:8787` + socat 桥到 `172.27.96.193`） | `reachable=true`，`modelReady=true` |
| SMTP（QQ 发信，测试员用自己的邮箱收 OTP） | `smtp_configured=true` |
| App 登录 UI（Figma `127:1179`） | Apple + Google + Email 都显示 |
| `app.json` | `usesAppleSignIn: true`，Bundle ID `com.nexleap.diaryone.dev` |
| `eas.json` preview | `EXPO_PUBLIC_DEV_BFF_URL=https://bff.diary.luxe` |
| 算法（内测 M2） | Evidence → BFF → X02/qwen → Chapter；偏好软筛选、Topics、Search summary。不含耳机 BLE、不含 S13 商用签字 |

自检：

```powershell
curl.exe -sS https://bff.diary.luxe/health
```

期望：`status=ok`，`allow_mock_preview=false`，`smtp_configured=true`，`x02.reachable=true`。

**云主机重启：** Docker / Caddy 一般自启；X02 + socat 已装 systemd（`diary-x02` / `diary-x02-socat`）。若健康检查里 `x02.reachable=false`：

```bash
sudo systemctl restart diary-x02 diary-x02-socat
curl -sS http://127.0.0.1:8790/health
```

---

## 打包前必须由持有账号的人做（约 20 分钟）

### 1. Apple · Sign in with Apple

1. https://developer.apple.com/account → Certificates, Identifiers & Profiles → **Identifiers**
2. 打开 **`com.nexleap.diaryone.dev`**（没有就新建 App ID，Bundle ID 必须一字不差）
3. 勾选 **Sign in with Apple** → Configure（默认即可）→ **Save**
4. App Store Connect 新建 App（同一 Bundle ID），记下数字 **Apple ID**
5. 把数字填进 `apps/mobile/eas.json` → `submit.preview.ios.ascAppId`（替换 `REPLACE_WITH_APP_STORE_CONNECT_APP_ID`）

### 2. Google · OAuth Client（要真能点 Continue with Google）

1. https://console.cloud.google.com → 建项目 → APIs → **Google Auth Platform / OAuth consent**（External，测试用户可先加内测邮箱）
2. Credentials → Create OAuth client：
   - **Web**：记下 Client ID
   - **iOS**：Bundle ID = `com.nexleap.diaryone.dev`，记下 Client ID
3. 写入 `apps/mobile/eas.json` 的 `build.preview.env`（不要提交到公开仓库以外的聊天）：

```json
"EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID": "xxxx.apps.googleusercontent.com",
"EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID": "yyyy.apps.googleusercontent.com"
```

未填时：按钮仍在，点击会提示缺 Client ID。Apple 与邮箱 OTP 不依赖这两项。

---

## 打包命令（同事执行）

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npx eas-cli login
npx eas-cli build --profile preview --platform ios
npx eas-cli submit --profile preview --platform ios
```

TestFlight 加内部测试员。

验收：Apple 登录或邮箱 OTP → 同意云 Evidence → 相册导入图/视频 → Diary 出 Chapter。Device 保持未连接（无耳机）。

---

## 不要做

- 把 `DASHSCOPE_API_KEY`、SMTP 授权码、`API_TOKEN` 写进 App 或群公告
- 用 trycloudflare 覆盖 `EXPO_PUBLIC_DEV_BFF_URL`
- 本轮接 BLE / 真耳机
