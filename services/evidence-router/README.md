# Evidence router · 历史 Dev Lite 兼容配置

当前手机默认路径为 `apps/mobile/src/evidence/mobileclip` 的 MobileCLIP-S0 FP16 v07；原生 `DiaryOneVision` 名称只保留作视频解码，不代表使用 Apple Vision 语义模型。

本目录的 `semantic_profile_defaults.json` 仍被 BFF `dev_lite/semantic_routes.py` 引用，用于旧远端语义分析工具的兼容参数；不是 App 当前默认模型选择器，因此保留。旧 Windows MobileCLIP 权重配置参见 `docs/WINDOWS_MOBILECLIP_BFF.md`；不能把该历史工具的运行状况计作本轮手机算法验收。
