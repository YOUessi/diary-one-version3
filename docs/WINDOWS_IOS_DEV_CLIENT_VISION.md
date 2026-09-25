# Windows 上验真 Vision + 商业 iOS 路径（不忽悠版）

## 硬事实

| 事实 | 含义 |
|------|------|
| 你电脑是 **Windows** | **不能**在本机跑 `npx expo run:ios`（要 macOS + Xcode） |
| **Apple Vision** 是 iPhone 系统 API | 必须打进 **自定义 IPA**；**Expo Go 永远没有** `DiaryOneVision` |
| **EAS Build** 在云端用苹果机器编译 | Windows 开发者出 iOS 包的正规路径 |
| **最终上架** | EAS `production` → App Store Connect；**不是** Expo Go，也**不是** Dev Client |

---

## 你「现在手机调试」分两层

### A. 今天就能用（Expo Go + Windows PC）

可测：Figma 四 Tab、登录 OTP、去重/压缩/抽帧规则、语义**规则**（fallback）、Dev Lite 云管线。

**不能测：** 真 Feature Print / Classify（Vision）。

入口：`Account` → Evidence pipeline lab → **B 选视频** → **C 看路由**。

### B. 要验真 Vision（必须 Dev Client IPA）

Windows 流程：

1. **Apple Developer Program**（年费）— 真机安装/上架都要  
2. `npm i -g eas-cli` → `eas login` → `eas init`（关联项目）  
3. 注册设备 UDID：`eas device:create`（按提示用手机 Safari 安装描述文件）  
4. 云端出开发包：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npm run eas:build:ios:dev
# = eas build --profile development --platform ios
```

5. 构建完成后用 QR / 链接装到 **iPhone**（Ad Hoc / 内测安装）  
6. 打开的是 **Diary One Dev Client**，不是 Expo Go  
7. PC 仍跑 Metro：`npx expo start --dev-client --lan`  
8. Lab：**B 视频 → C 调试**，确认 `analyzer=native_vision`、非 degraded  

JS 热更新仍在 Windows；**只有原生模块变更**才要重新 EAS 出包。

---

## 和「商业上架」的关系

```text
现在 Expo Go     → 功能/UI/云管线联调（无真 Vision）
    ↓
EAS development  → 真 Vision + 全功能真机（内测壳，可带 Lab）
    ↓
EAS preview      → TestFlight 形态（通常关 Lab）
    ↓
EAS production   → App Store 商用包
```

仓库已有：`eas.json` 的 `development` / `preview` / `production`，`expo-dev-client`，`plugins: diary-one-vision`。

---

## 你缺什么就开不了真 Vision

- [ ] Apple 开发者账号  
- [ ] Expo/EAS 账号 + 项目已 link  
- [ ] iPhone UDID 已登记到描述文件  
- [ ] 至少成功一次 `eas build --profile development --platform ios`  
- [ ] 手机装的是 **Dev Client**，不是商店 Expo Go  

没有以上任一项，**任何人**都没法在 Windows 上「本地编译 iOS Vision」——这不是偷懒，是平台限制。
