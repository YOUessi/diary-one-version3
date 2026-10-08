# 现在就要完成（不含真耳机 BLE）

BLE / 真电量 / 真采集：**仍不做**。

已在本机跑通：Docker 量产栈 · 真 MinIO · 真 SMTP（QQ）· X02 千问 · day-revision 出稿。

---

## 云端日记 → Chapter：已经完成，Expo Go 就能测

链路：手机相册 → 校验/去重/抽帧 → `POST /v1/day-revisions` → Worker → X02 千问 → `GET /v1/jobs` → App `mapPreviewToDiary` → **Diary Tab 当天 Chapter**。

PC 冒烟用的是 1×1 测试 JPEG：任务 **succeeded**，但算法判定 `PIPELINE_BLOCKED` / `UNRESOLVED_DAY`，**0 条 chapter**（证据不够，不是功能没做）。

**要在软件里看到 Chapter，必须用真实照片/视频**（有内容的日常图，不要纯色小图）。

### 现在用 Expo Go 测（不必等 TestFlight）

电脑保持：Docker Desktop Running + `docker compose` 栈 + `.\scripts\start-x02.ps1`（千问 :8787）。

手机（同一 Wi‑Fi）：

1. Expo Go 打开本项目（Metro）。
2. Account → Evidence pipeline lab → **Apply .env BFF defaults**（`.env` 里是 `http://192.168.31.74:8790`，IP 变了就改 `apps/mobile/.env` 后重启 Metro）。
3. Account → Privacy：**打开云证据同意**。
4. Device / Demo：选 **今天拍的 2～5 张真实照片**（或短视频）→ 走云端处理。
5. 等几分钟（千问）→ Diary 当天应出现 Chapter；Lab 任务成功文案类似 `Diary updated · N memories`。

登录 OTP 用 `2796726144@qq.com` 收邮件验证码。

Vision **不在 Expo Go 里**。语义抽帧要 EAS 包（下面第 3 节）。

---

## 还需要你做的

### TestFlight / Vision（同一条 iOS 包）

需要 Apple 开发者年费 + Expo 登录：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npx eas-cli login
npx eas-cli init
npx eas-cli build --platform ios --profile preview
```

preview 已开 `EXPO_PUBLIC_INCLUDE_VISION=1`。装的是 EAS 包，不是 Expo Go。

---

停 Docker：`cd E:\AI耳机\diary-one\services\bff` → `docker compose down`  
重启千问：`.\scripts\start-x02.ps1`
