# MobileCLIP-S0 FP16 受控资产

Git 只保存本说明和 `manifest.json`。`image_encoder.onnx` 与 `prompts.f32.bin` 保留在授权开发机，按仓库现有约定不提交。克隆仓库不会取得这两个文件，不能直接运行模型或打包原生 App。

由团队通过受控渠道提供同一版本的资产，放到本目录。不要从其他模型版本挑选同名文件，不修改 manifest 以接受不同权重。

| 文件 | bytes | SHA256 |
| --- | ---: | --- |
| `image_encoder.onnx` | 22857054 | `7ea0ab32ddbbd1c51b6158f12ccb669968de37125dd7455f04b6e1988cb9a141` |
| `prompts.f32.bin` | 24576 | `c70ffd4cd11c8ac42f8b36c0d15e352da92bffc3b83f60f5c0acae16e86bef45` |

从 `apps/mobile` 运行 `npm ci` 后，执行 `npm run test:evidence`。现有检查脚本会核对两个文件的大小和 SHA256；缺失或不匹配时失败。该命令验证桌面策略小样本和资产完整性，不是手机性能或模型质量验收。正式运行模型还需要包含 ONNX Runtime 和本地视频解码模块的原生开发/发布构建，Expo Go 无法执行这条链路。

模型来源、FP32→FP16 转换信息和原始 checkpoint SHA 记录在 manifest。v07 指抽帧策略，模型仍为 S0。使用和分发须遵守取得资产时适用的来源条款；上游[模型许可](https://github.com/apple-aiml-research/ml-mobileclip/blob/main/LICENSE_MODELS)与代码 MIT 许可不同，不能把本仓库接入、内部测试或能打包理解为商业许可。受控渠道应同时提供适用许可、归属和派生转换说明。

## EAS 打包边界

仓库根目录的 `.easignore` 用于此 monorepo 的常规 Git 工作流。EAS 会用它替代全部 `.gitignore` 规则；规则保留敏感文件、缓存和生成目录的排除，并在最后只对本目录的两份固定二进制做例外。它不会下载模型或验证模型许可，也不会自动触发上传。由本机发起且另行获准的构建会把已放置的这两份文件传给 EAS，因此上传前仍需确认资产使用范围并完成 SHA 检查。

从 GitHub/干净 CI 克隆发起的构建仍需团队提前配置受控资产，不能依赖开发机文件。不要把 `.easignore` 移到 `apps/mobile`，也不要设置不同的 `EAS_PROJECT_ROOT` 后沿用这些根相对路径。若以后启用 `cli.requireCommit: true`，需重新核对归档方式；不能假定忽略在 Git 外的资产仍会进入构建。

官方依据：[忽略与显式包含规则](https://docs.expo.dev/build-reference/easignore/)、[monorepo 归档根目录与限制](https://github.com/expo/fyi/blob/main/eas-build-archive.md)。2026-10-19 本次仅整理文件规则、验证本机资产哈希和路径清单，没有执行 EAS archive、build、上传、签名或真机安装。
