# Diary One · 版本4构建入口

当前源码为 iOS 1.0.0（4）；版本说明和已完成验证见 [版本4记录](docs/releases/version4/README.md)。以下步骤用于重新生成本机工程；已经签名的 Archive 保存在原交付机器，未提交到 Git。


更新：2026-10-21。请先读 [README](README.md) 和 [清理记录](docs/CODE_CLEANUP.md)。

- 唯一源码目录为 `apps/mobile`；本目录已去掉 `Diary-one-version2.0` 这一层和另一套旧 App。
- 公网 BFF 保持 `https://bff.diary.luxe`，共享 Token 为空；服务端密钥不能写入 App。
- iOS 模拟器使用本地 Xcode 构建；本轮是否成功请看清理记录。模拟器包不能安装到真实 iPhone。
- 真机 / TestFlight 需要 Apple Developer 团队、Bundle ID、App Store Connect App 和签名。已有 [EAS步骤](docs/TestFlight打包详细步骤.md) 可用，也可使用以下本地 Xcode 路径。
- 手机模型为 MobileCLIP-S0 FP16 v07，云模型为 qwen3.8-flash，云端代码为 R5_18。

## iOS 内测：本地 Xcode

本轮沿用 preview 身份 `com.nexleap.diaryone.dev`。先在 Xcode → Settings → Accounts 登录有权限的 Apple Developer 账号，再选择拥有此 Bundle ID 的团队。付费个人会员也可分发 TestFlight；已有公司团队的 Bundle ID 需要该团队权限，不能直接换到无权限的个人团队。

在 `apps/mobile` 安装依赖后，首次生成原生工程：

```sh
npm ci
EXPO_NO_DOTENV=1 EXPO_PUBLIC_INCLUDE_VISION=1 EXPO_PUBLIC_INTERNAL_BETA=1 EXPO_PUBLIC_STORE_RELEASE=0 npx expo prebuild --platform ios --no-install
cd ios
pod install
cd ..
node scripts/configure-xcode-beta.cjs --write
open ios/DiaryOneDev.xcworkspace
```

已有当前原生工程时，直接执行最后两行即可。配置脚本将 eas.json 的 preview 公共参数写入被 Git 忽略的 `ios/.xcode.env.local`，确保从 Xcode 界面 Archive 也包含公网 BFF。不会写入服务端密钥、修改 Apple 团队或提交构建。修改 preview 环境字段后应重新运行脚本，再重新 Archive。当前完整隐私政策/条款 URL 尚待团队提供，空值不能当成正式协议已上线。

Xcode 选择 DiaryOneDev target → Signing & Capabilities → 正确 Team，保持 Bundle ID 不变；核对 Sign in with Apple 能力。选择 Any iOS Device (arm64)，Product → Archive。成功后在 Organizer 验证并上传 App Store Connect，再在 TestFlight 添加测试员。Xcode 路径不要求 Expo/EAS 登录；`ascAppId` 占位值只用于尚未配置的 EAS Submit 路径，不能把它当真实 App ID。

未签名的真机 Archive 只证明 iphoneos 编译通过，不能直接安装，也不替代签名、真机运行及 TestFlight 验收。不要把模拟器 `.app` 当成 IPA 分发。Android 适配留后续，本轮不生成 APK。
