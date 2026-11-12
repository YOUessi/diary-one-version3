# 完整项目整合测试记录（2026-11-12）

本包从上一版完整项目源码复制到**独立目录**，将纯算法SDK实际整合进去，不覆盖Mac原开发工程。

| 子系统 | 实际测试结果 |
|---|---|
| 完整手机TypeScript | tsc --noEmit 通过 |
| 手机Node核心测试 | 203通过，0失败 |
| 云端算法Python全部测试 | 1,362通过，25跳过；176子测试通过 |
| BFF Python全部测试 | 216通过，7跳过 |
| 新增真实完整项目单次VLM模拟集成测试 | 通过 |

## 单次Qwen + BFF联通范围

测试在临时目录生成两张真实JPEG，构造来源SHA和V04 Bundle，使用完整项目原有X02 QwenStageGateway/x01.QwenChatCompletionsAdapter，拦截并模拟一次HTTP响应：
- 验证Qwen请求包含原JPEG完全相同的字节、正确图像序号和非思考模式。
- 只有一次全局编辑调用；返回原Story、选中Frame ID和Hero。
- 结果通过真实BFF的输入绑定及Direct VLM结果合同，最多10张。
- 无外部网络、无真实API收费、无人工标注或用户素材。

测试文件：source/services/algorithm/algorithm/tests/test_full_onecall_sdk_integration.py。

## 历史回归迁移

旧测试会要求20张图库被接受、旧转换器自动修剪图、重排章节、无Key Moment自动补足、英语输出触发额外语言API等。这些行为已被新算法禁用，因此已将相关测试重写为**新失败即拒绝的正向测试**，没有跳过或标为预期失败；旧的原始版本仍保留在之前完整项目交接包中供复核。

全部历史多阶段测试单独使用 DIARY_ONE_X02_EDITOR=staged_v041 运行，是为了测试其历史schema，而不是切换本包真正Direct VLM默认模式。

## 没有执行的项目

- iOS真机完整10秒视频抽帧/3秒原生MOV播放。
- 真实Qwen API在新整合包上的跨场景语义质量实验及现场全日成本压测。
- 生产用户认证和队列的实机部署验收。
- 原生Apple相册Live Photo配对、Android原生等价实现。

交接包不带API密钥、个人媒体或MobileCLIP受控权重。上线前需要完成上述工作并复核章节语义/地标证据。
