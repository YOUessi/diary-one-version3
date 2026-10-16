# Windows + Android 模拟器自测（无 iPhone）

## 一、Android Studio（只需做一次）

你的机器上 Android Studio 在 `E:\77app*\app tool`，注册表显示 **尚未安装 SDK**（`InstallSdk=0`）。请：

1. 打开 **Android Studio**
2. **More Actions** → **SDK Manager**
   - **SDK Platforms**：勾选 **Android 14 (API 34)**
   - **SDK Tools**：勾选  
     - Android SDK Build-Tools  
     - Android SDK Platform-Tools  
     - **Android Emulator**  
     - Android SDK Command-line Tools (latest)
3. 点 **Apply** 等待下载（SDK 默认目录：`%LOCALAPPDATA%\Android\Sdk`）
4. **Device Manager** → **Create Device** → **Pixel 6** → 选 **API 34** 系统镜像 → Finish

## 二、自动配置环境变量

在项目根目录 PowerShell：

```powershell
cd E:\AI耳机\diary-one-app
powershell -ExecutionPolicy Bypass -File .\scripts\setup-android-windows.ps1
```

**关闭终端再开一个新窗口**，然后：

```powershell
adb version
```

应能输出版本号。

## 三、安装依赖并跑 App

1. 在 Android Studio **Device Manager** 里点 ▶ 启动模拟器  
2. 终端：

```powershell
cd E:\AI耳机\diary-one-app
npm install
npx expo run:android
```

- **第一次**会生成 `android/` 并编译 **development client**（约 10–30 分钟，视网速而定）
- 成功后模拟器里会出现 Diary One

日常开发：

```powershell
npx expo start --dev-client
```

终端按 **`a`** 推到 Android。

## 四、自测开关

| 功能 | 位置 |
|------|------|
| Today 状态 | Diary 页 **Internal · Today state** |
| 模拟设备连接 | Device → Device Settings → **Internal lab link** |
| 重置 Onboarding | Account → Privacy & Data → Delete account → **Delete local data** |

## 五、常见问题

- **`adb: command not found`**：重跑 setup 脚本并**新开终端**
- **没有设备**：模拟器要先启动；`adb devices` 应显示 `emulator-5554 device`
- **`SDK location not found`**：先完成 SDK Manager 安装，再 `npx expo run:android`
- **Hyper-V / 模拟器打不开**：Device Manager 里换 **x86_64** 镜像，或在 BIOS 开启虚拟化
