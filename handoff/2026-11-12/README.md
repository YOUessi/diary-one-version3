# Nexleap Diary One — 单次 Direct VLM + 端侧抽帧 + 动态封面源码交接包

**交接日期：2026-11-12。**

这是从 Mac 当前 Diary_one_chapter_v2 工作树提取的真实 TypeScript、Swift 和 Python 源码，再在交接副本上统一修改为**每章最多10张图**。原工作树未被修改。此交接包用于后端工程集成，不代表已经在生产部署或通过全场景语义验收。

## 内容

- source/apps/mobile/：Expo React Native 手机端完整相关源码，MobileCLIP-S0 FP16 V07、V05端点门控、iOS AVFoundation解码、Bundle V04/V05、异步上传、3秒动态封面。
- source/services/algorithm/algorithm/：完整 Python Direct VLM V04 实现，单次全日JPEG → Qwen3.8-Flash → Chapter JSON，允许最多一次失败重试。
- source/services/bff/：生产认证上传、Job轮询、返回结果与原始JPEG来源哈希校验。
- baseline_v04/：当时 Mac 的原始相关核心源码，图库上限20，仅供对比和追溯。不要覆盖交接版 source/ 。
- tests/handoff_smoke.py：无需外部API或模型权重的代码与max10合同自测。
- SOURCE_MANIFEST.json / PATCH_MANIFEST.json：原始文件SHA和打包修改追踪。

## 重要事实

1. 云端 VLM 一次看全部端侧已选JPEG，不上传10秒原视频到模型。支持最多250张JPEG，原始JPEG字节数≤35MiB；超出必须显式失败，不能偷偷丢掉时间线后段。
2. 后端返回hero_frame_id、representative_frame_id、source_asset_id、focus_pts_ms等可验证索引；**动态封面不是后端生成**。
3. 手机本地在最后Chapter确定后，从仍保留的10秒原始视频导出3秒静音MOV与JPG，供App内motion展示。**不是已保存至Apple Photos的原生HEIC/MOV配对 Live Photo**（isApplePhotosPaired=false）。
4. 端侧MobileCLIP模型权重 image_encoder.onnx 与 prompts.f32.bin **不在ZIP里**。原仓库明确限制由授权团队通过受控渠道提供，详见 source/apps/mobile/assets/models/mobileclip-s0-fp16/README.md 和 manifest.json。不要从GitHub随意替换版本，也不要未经许可公开分发模型文件。
5. 交接版每章**最多10张（建议3–8张）**，不以10为目标；模型选择图仍需要语义质量测试。禁止把20张截成前10张冒充精选。

## 最快开始

1. 阅读 INTEGRATION_GUIDE.md 和 API_CONTRACT.md。
2. Python 环境安装jsonschema等后运行：python3 tests/handoff_smoke.py（无需模型权重、无网络）
3. 在受控开发机取得对应FP16 ONNX/Prompt文件，校验模型manifest中的SHA256后再执行Expo原生构建。
4. 运行生产BFF认证、POST /v1/day-revisions、GET /v1/jobs/{job_id}、云端Direct VLM和手机客户端结果校验。
5. 验收 V05 3秒Motion要用iOS原生Dev Client或TestFlight；Expo Go不支持本链路的本地模型与AVFoundation模块。

注意：source 中的手机代码来自包含未提交实验修改的 Mac 工作树快照；SOURCE_MANIFEST.json精确保留原始文件哈希，不能以旧Git HEAD推断所有代码已在线上存在。
