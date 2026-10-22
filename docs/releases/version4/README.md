# 版本4：iOS 1.0.0（4）

## 代码范围与来源

本分支在 `version3.0` 的 `b5eb6118c306281ba680a8652967a5903999fa48` 之上，保存清理目录中的已打包源码快照。原 `version3.0` 分支不变。主目录为 `apps/mobile`、`services/bff`、`services/algorithm/algorithm`；没有保留另一套旧 App 路径。

源码交付包：`DiaryOne-iOS-beta-build4-source.zip`，923 个文件。

- ZIP SHA256：`cf14d801b787a3917e586bf7f2c2920c1562cac9bc828ae32d421f1f15e6cf51`
- App 构建输入快照 SHA256：`b606be0d41ec0d67ffb94e2e9613a972c70a8218e8f95d2d63b57b86b6e859ca`（251 个文件）。
- [原始源码包清单](source-package-manifest.json)、[App 构建清单](app-build-source-manifest.json)。上传时仅更新入口说明/分支说明并添加验证记录，功能源码和模型与归档一致。

## 本次包含

1. Chapter 首页摘要、章内高光及其对应原视频定位、历史 Aha 和缩略图、嵌套媒体持久化。
2. 完整比例视频预览；控制栏位于画面下方；系统全屏播放；退出全屏复用同一播放器、保留进度和播放状态。
3. 此前版本的照片格式/尺寸归一化、原生编码验证、导入反馈和错误提示修复。
4. MobileCLIP-S0 FP16 v07、云端 R5_18 / qwen3.8-flash；BFF 保持 `https://bff.diary.luxe`，服务端密钥不进入 App 或源码。

## 已有构建与验证证据

- 2026-10-21：iphoneos arm64 Release 签名 Archive 成功；[归档核验](archive-verification.json) 共26项通过。
- 当时 App 核心189项通过，typecheck通过，lint无错误/4个既有警告；[原生配置4项](native-config-20261021.txt)、[ONNX生命周期/补丁21项](onnx-native-patch-20261021.txt)通过。
- [播放器验证范围](playback-verification.json)：模拟器确认完整预览、进入全屏和原生控制；退出保留进度由用户手动确认。使用历史动物园素材回放（8个视频、14帧），没有新云模型调用。
- GitHub 上传前的检查另见 `publish-verification.json` 及 `core-tests-20261022.txt`、`typecheck-20261022.txt`、`lint-20261022.txt`；它们不代表新增真机或云端全链路验收。

## 尚未由本次记录确认

- 构建4在真实 iPhone 上的安装和运行、原生拖动与旋转尚无新增验收；TestFlight是否上传/处理完成由用户操作后的状态为准。
- App 主 dSYM 匹配；React、ReactNativeDependencies、hermesvm 的完整依赖符号仍缺失。
- Android 原生适配和正式隐私政策/条款 URL 仍待完成。历史25份缺失素材未计通过，不宣称所有内容质量问题已解决。
- 本次只上传 GitHub 源码，不改变线上 BFF/算法、不运行新云模型请求，也不提交 App Store 或 TestFlight。

## 构建与安装

按根目录 [README_build.md](../../../README_build.md) 使用 Xcode。需要有权限的 Apple Developer 团队和该 Bundle ID；生成并签名后，员工内部测试选择 `TestFlight Internal Only`。

此仓库不是可安装 IPA，也不包含本机 `.xcarchive`、签名私钥、描述文件、服务器凭据、node_modules、Pods 或测试账号数据。模型权重是构建所需公开模型资产，保留在 App 的模型目录。
