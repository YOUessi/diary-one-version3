# Diary One｜冻结 V1 单次 VLM 恢复与图库质量门禁

2026-11-12，Mac 研究分支 experiment/2026-11-12-v1-direct-gallery-gate。**已开发与测试；默认关闭；没有合并或部署线上。**

## 实际改动

- 保留冻结 V1 关于自然完整经历、作品/地标可识别主体和事实保守性的正文，不把 Chapter 强制拆成每个画面或地标。
- 仅替换两句反复提到“10–20张、最多20张”的图库数量表达，模型所见的 selected_images Schema 不再提供数字图片配额。
- 模型负责自然分章、Story 和选图；程序负责校验：每章实际最多8张，非法图片/Key Moment/排除索引、跨章同 Clip 归属交叉、连续满上限的机械分桶、大段漏掉头尾素材，均拒绝整个结果。
- 不采用旧 Compact 转换器的静默裁剪、删除瞬间、跨时序重排；严格门禁先验收原始 JSON，再调用现有确定性来源映射，并且要求转换器没有任何修补。
- 不合格时最多用**完全相同的 Prompt、相同 JPEG**重新调用一次，保留每次原始输出、Request ID、Token 和费用。仍然失败则 fail-closed，不自动重写 Story 或切换 V02。
- 实验开关为 DIARY_ONE_X02_EDITOR=direct_v1_quality；不设置时仍执行原来的 direct_vlm。
- BFF 发布闸门 DIARY_ONE_ALLOW_DIRECT_V1_QUALITY_PUBLISH 默认关闭。没有开启时，X02 的成功实验结果不会自动进入正式 App。
- 结果结构兼容原 DIARY_ONE_DIRECT_VLM_CHAPTER_V01，原手机端 MobileCLIP-S0 FP16 V07 抽帧、原始视频和3秒 Live/Motion 算法**不变**；额外的 experiment/decision_trace 可识别研究 Profile。

## 真实 API 独立 A/B

模型 qwen3.8-flash，三组真实 MobileCLIP FP16 V07 JPEG，各种变体使用同一个输入集合。原冻结 V1 历史结果不重复计费；本轮15次真实 API 请求共约¥1.78435（Token费用估算，非平台最终账单）。

每格表示 Chapter / Gallery；✅ = 严格校验通过，❌ = 时间/引用合同失败。

| 输入 | 冻结 V1 | 去配额 / 模型Schema无图库张数上限（2次） | 同Prompt、模型Schema最多8张（2次） | 单句强化图库时间归属（1次） |
|---|---|---|---|---|
| 博物馆40s，86 JPEG | 4/25，时间交叉 | 4/20 ❌、6/27 ❌ | 2/16 ❌、10/78 ❌ | 5/34 ❌ |
| 国家公园70s，192 JPEG | 4/47，时间交叉 | 6/29 ✅、6/12 ✅ | 5/19 ✅、4/18 ✅ | 4/16 ✅ |
| 悉尼30s，234 JPEG | 8/160，非法索引和机械分桶 | 6/21 ✅、5/35 ❌ | 8/32 ✅、6/46 ❌ | 8/38 ❌ |

通过率：去配额3/6、Schema最多8图3/6、强化图库归属1/3。**明显减少了盲目凑满20图的现象，但没有稳定解决图库跨章；目前不允许设成默认。**

与原V1相比，悉尼第一次去配额生成6章21图，不再漏掉后面的植物园/海滨素材，标题包括歌剧院、岩石区、达令港、城市商业长廊、教堂和植物园；另一次同Prompt仍有交叉。国家公园通过率较好，但图库12–29张之间波动，且部分地点名仍未独立核准。博物馆2、4、6、10章波动，所有新版本仍交叉。

这里两个变体改变了模型侧的图库数量约束，属于有记录的 Prompt/Schema消融，不是绝对因果证明。模型非思考模式、未固定随机种子；语义准确性不能由结构通过代替。悉尼一次Story出现“品尝海鲜饭”，静态摊位图不一定支持“已品尝”，因此**并未宣称自然叙事和具体名词已经全面验收**。

## BFF与真实JPEG来源绑定

采用实际成功的两份 Qwen原始模型 JSON，重新加载对应真实 FP16 V07 JPEG（模拟 Bundle V04 研究素材；不是原始 MP4 文件）：

| 数据 | 原始JPEG | 原始Qwen输出 | 转换结果 | BFF校验 |
|---|---:|---|---|---|
| 国家公园70s | 192 | 6章/29图 | Story/标题原样保留 | V01 来源绑定通过，默认禁止发布，opt-in 通过 |
| 悉尼30s | 234 | 6章/21图 | Story/标题原样保留 | V01 来源绑定通过，默认禁止发布，opt-in 通过 |

该测试是**真实API输出 + 真实JPEG + FakeGateway传输重放**，不是新的真实API请求，不等同于 HTTP multipart 或真机 App 端到端测试。

回归测试：259 passed、7 skipped，旧Direct V03、V02、BFF合同均无回归问题。

## 源码及复现

- 新编辑器：services/algorithm/algorithm/src/diary_one_ci/direct_v1_single_quality.py
- 冻结原版V1 Prompt和Schema：services/algorithm/algorithm/src/diary_one_ci/v1_frozen_resources/
- X02 opt-in路由：services/algorithm/algorithm/src/diary_one_ci/x01_server.py
- BFF默认禁止发布：services/bff/shared/result_admit.py
- 端到端含真实JPEG文件的测试：services/algorithm/algorithm/tests/test_direct_v1_single_quality.py

Mac 私有原始实验根目录：
~/Documents/Nexleap/work_logs/evidence/v1-single-restore-20261112/

其中 site/*.html 提供每次运行的全部原始Story/封面/图库对照，results/ 保存原始Qwen JSON、token、request ID及失败原因；OFFLINE_REPLAY_RESULT.json 保留BFF离线验收收据。JPEG、API密钥和完整私有模型输出不会上传到GitHub。

## 后续架构判断

**保持冻结 V1自然叙事作为主基线。** 先完成独立语义质量评审和图库合同稳健性；若单次结果继续跨章或遗漏，不允许直接发布。只有在真实 Story经图片证据确认合格的情况下，才研究按需冻结该 Story、为失败的 Gallery/时间归属单独补救，避免让另一个 Planner 重写成细碎的流水账。尚没有经过验收的这种按需补救架构，因此不提前启用。
