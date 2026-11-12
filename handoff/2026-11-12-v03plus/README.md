# Nexleap Diary One V03+｜手机抽帧 → 单次云端 VLM → 3秒 Motion

2026-11-12。后端工程交接源码（NOT a production-ready model-quality claim）。

这是覆盖了原 V04 交接包的全新版本，不是重命名。云端恢复 V03 的原始简短Prompt和最多8图合同；研究候选选择性补充约302字符的四条V04规则；保留同一套已存在的手机MobileCLIP FP16 V07、V05端点门控和iOS 3秒Motion源码。

## 关键区别

- 原 V03（默认）：Direct VLM仅一次性输入已选JPEG，建议每章3–6张，最多8张；研究中已见英文和跨章问题，不要宣称完全可上线。
- V03+（研究开关）：在**完全不改变原V03分章规则**的前提下，只增强封面代表性、图库互补、重要主体视觉证据、简体中文。不是V04长Prompt，不引入10–20图配额或按全日Round-Robin截图库。
- 用户认可的本地8810网页offset=10&method=jpeg对应**原V03**，不是V03+。两个版本同一JPEG时仍可能产生不同结果。
- V03+结构门禁禁止多章源Clip交叉、跨章重复、非法引用、填满上限连续分桶；不改写Story、不静默裁剪；不能证明语义全对。研究已执行18次真实Qwen，最简候选8次中4次结构通过；**不应直接切换生产默认**。
- 原手机V05 Motion：源10秒视频在手机本地，按焦点帧截取3秒静音MOV和JPG用于App内动态封面；applePhotosPaired=false，尚未实现系统照片库HEIC/MOV配对Live Photo。
- 模型 image_encoder.onnx 和 prompts.f32.bin 由于授权/许可与受控分发要求没有加入ZIP。不能把缺少权重的包直接用于原生模型推理。

## 项目内容

- source/apps/mobile：完整Expo React Native、TypeScript、Swift、bundle、上传和UI源码快照（需按团队许可补入对应MobileCLIP模型权重）。
- source/services/algorithm/algorithm：冻结V03编辑器和V03+研究开关、Qwen API网关、数据包解析、原有测试。
- source/services/bff：DayRevision认证上传、Job、来源哈希与结果Schema校验、默认禁止V03+研究发布。
- docs：原始JPEG的A/B统计摘要与实验限制，不含用户素材或API密钥。
- INTEGRATION_GUIDE.md、API_CONTRACT.md、GALLERY_POLICY.md、tests/handoff_smoke.py：接入/限制/独立本地验证。

## 运行

1. 阅读 INTEGRATION_GUIDE.md 和 API_CONTRACT.md。
2. Python（已安装依赖）执行 python3 tests/handoff_smoke.py。
3. 模型权重按手机assets/models/mobileclip-s0-fp16/manifest.json的真实SHA256，从授权渠道配置；不得从未知下载替换。
4. 手机从root/source/apps/mobile执行npm ci && npm run typecheck；使用iOS原生Dev Client/TestFlight，Expo Go无法运行真正MobileCLIP/Swift解码。
5. 云端Qwen API密钥仅后端持有，使用安全私有环境变量配置。测试V03+研究路线时设置DIARY_ONE_X02_EDITOR=direct_vlm_v03plus；发布闸门DIARY_ONE_ALLOW_V03PLUS_PUBLISH默认关。
6. HTTP POST /v1/day-revisions，GET /v1/jobs/{job_id}。核心时序和字段以源码为准。

核心BFF Schema SHA256: 9b0402bd07ca25fe93aaf17ea1260f82947730661d71ad75b89e25425cf8532c
