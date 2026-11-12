# Diary One 纯算法源码交接包

仅包括三段算法：手机端 MobileCLIP FP16 V05/V07 抽帧、云端一次 Direct VLM Chapter 编辑、手机端 3 秒动态封面。**无 UI、完整App、BFF服务、数据库、Worker、Web页面和旧多阶段流水线**。

## 目录

- mobile/src/evidence/：FP16 MobileCLIP-S0、稀疏视频探测、V05端点门控、V07覆盖优化、代表帧选择。
- mobile/src/pipeline/buildAppLibraryBundle.ts：封装标准 Bundle V04/V05，输出 JPEG、Frame ID、原始PTS与SHA256。
- mobile/modules/diary-one-vision/ios/：原始 Swift AVFoundation 解码、图像归一化、3秒MOV+JPG导出。
- mobile/src/pipeline/buildLiveChapterCovers.ts：最终 Chapter 入选媒体的3秒Motion。
- mobile/src/oneCallMotionAdapter.ts：算法专用适配器，模型选图 → 本地原视频 → Motion；没有App UI、DB依赖。
- cloud/diary_one_ci/：真实 Direct VLM Prompt/转换器、来源Bundle校验、最小独立Qwen网关。
- cloud/run_onecall.py：可嵌入现有Python后端的一次调用入口。
- cloud/contracts/：结果格式参考Schema；cloud/tests/smoke.py：离线无API测试。
- SDK_SOURCE_INDEX.json：实际源码依赖、来源快照；CHECKSUMS.sha256：文件完整性。

## 后端集成

后端只需接入 cloud/diary_one_ci/direct_vlm.py 的 run_direct_vlm(manifest_path, QwenStageGateway(...))，不需要运行这里的BFF/HTTP服务。模型单次看全天已选JPEG并生成 Chapter、Story、选图和Key Moments，结构失败最多一次完整重试。result保留 Hero Frame ID、素材来源与PTS供手机客户端使用。

详见 INTERFACES.md。

## Live 的真实含义

本套代码的Live是 **手机本地利用原始10秒视频生成3秒静音MOV+JPG，或3秒 source-window回放**。它不是云端VLM生成视频，也不是已经保存进Apple Photos相册的原生配对Live Photo。

## 图片策略与限制

每章最多10张，通常3–8张，不能把10张当配额，也不能超限后截断。原始代码存在的 Chapter 语义错图问题**尚未证明完全修复**；本包是算法源码交接而非生产级效果认证。

MobileCLIP授权模型文件 image_encoder.onnx 与 prompts.f32.bin 不包含在包内，需要从团队授权渠道提供，按 mobile/assets/models/mobileclip-s0-fp16/manifest.json 校验。

## 已验证与未验证

- 已通过手机算法TypeScript静态类型检查。
- 已通过云端生成的合成JPEG + 模拟Qwen响应的单次完整算法测试（不消耗API）。
- 还没有在真机重新执行3秒Motion/系统相册Live，也没有拿这份重新打包后的SDK进行真实Qwen质量复测。
- V05算法包修正了原代码与云端不一致的空间归一化：V04、V05都采用 ASPECT_FIT_LETTERBOX。
