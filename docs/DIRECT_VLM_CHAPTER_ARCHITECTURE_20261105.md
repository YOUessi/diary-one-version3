# Diary One — Direct VLM Chapter V01

## 目标

将云端 Chapter 的 S04/S07/S09/S11 多阶段分章编辑替换为 **VLM 单次接收全量已抽帧 JPEG 并直接生成完整 Chapter**。手机不新增语义理解或原视频上传，不提供人工路线图，不训练模型、不额外运行 LLM Judge。

## 工程数据流

1. 手机 MobileCLIP 选帧 → 现有 researchClient → 现有 BFF day-revisions 上传接口和对象存储（不改）。
2. 原 Worker x02_proxy 继续通过 /x02/v0.4.1/preview 上传 manifest、所有 JPEG（不改）。
3. x01_server 默认 DIARY_ONE_X02_EDITOR=direct_vlm，调用全新的 direct_vlm.run_direct_vlm，跳过旧 S04/S07/S09/S11。
4. Qwen StageGateway 在同一个请求内按采集顺序送全部 JPEG，保留逐图 source asset ID、Frame ID 和原帧 PTS，模型自主决定 1–14 章。
5. 输出 title、story、hero_frame_id、gallery_frame_ids、experience_frame_ids、key_moments、editorial_summary、day_summary；BFF 使用独立 Direct VLM schema 验证。
6. App 校验新 schema hash 与来源、Frame ID、唯一图库图片等契约，再用现有 attachDiaryMediaFromBundle 绑定本机实际图片，不依靠猜测源图。

新算法源码：services/algorithm/algorithm/src/diary_one_ci/direct_vlm.py。
BFF 契约：services/bff/shared/direct_result_contract.py 与 shared/contracts/direct_vlm_chapter_v01.schema.json。
手机端验证：apps/mobile/src/cloud/validateDirectVlmResult.ts。

## 输出安全性与费用

- 每次对全部图片做一次全局编辑，最多因格式/引用错误重试一次，绝不无限调用或悄悄转回旧流水线。
- 当前基础 Base64 模式最多 250 张图片、合计 JPEG 35 MiB，超限显式失败。超过 250 张的长日记需要后续接入公网可访问的有时效签名图片 URL 才能一次完整多图输入；内网 MinIO 直连 URL 不可用于外网模型。
- 通过 DIARY_ONE_DIRECT_VLM_BUDGET_CNY 配置每任务预算保护（默认 ¥1.20 预估守卫），模型 usage 中的输入/输出 tokens 与每次调用费用写入 trace。
- 现有 strict JSON/ID/图片 hash/来源与真实时间范围校验。不能把模型图片描述当作已人工视觉核验的事实：新版本明确 visual_fact_reviewed=false、semantic_copy_verified=false、production_ready=false。
- 老算法仍作为回滚方案，但不会参与新模式计算，不会被赋予虚构的 S04 Fact ID。

## 配置与回滚

- 新框架（新版服务默认）：DIARY_ONE_X02_EDITOR=direct_vlm。
- 指定新模型：DIARY_ONE_DIRECT_VLM_MODEL=qwen3.8-flash。还需要已授权的 DASHSCOPE_API_KEY；不要在代码或 Git 记录密钥。
- 回滚原云端编辑逻辑：DIARY_ONE_X02_EDITOR=product_v1 并重启 X02 算法服务；更旧分段逻辑是 legacy。
- X02 /health 对外声明新 schemaVersion 和 editorPolicy，BFF Worker API 路径不变。
- BFF 与手机也必须部署含有新 schema hash 的配套版本，否则正式 App 会拒绝新结果。不能只更新算法服务一侧。

## 测试与发布门禁

- Python 新框架与 BFF 校验：PYTHONPATH=services/algorithm/algorithm/src:services/bff python -m pytest -q services/algorithm/algorithm/tests/test_direct_vlm.py services/bff/tests/test_direct_vlm_contract.py
- iOS/Android TS 类型检查：在 apps/mobile 内执行 npm run typecheck。
- 真实悉尼组：161 段、232 张本地原始 JPEG 通过真实提供商实测，并验证返回新 schema 后能通过 BFF apply_admission。
- 上线前仍需独立部署预发布环境，验收费用/超时、缺失重要场景、非生活片头和多次抽帧覆盖。单次直接 VLM 语义效果高于基线的结论不能由 JSON 结构检查推导。


## 2026-11-05 Chronology correction（时间信息显式传递）

- 原算法虽然按图片顺序发送，但 Qwen 逐图文本只有 asset_id / frame_id / 片内 source_timestamp_ms / canonical_offset_ms，未传明确 sequence_index、完整视频相对时间；提示词亦过分强调跨时间合并。
- Direct VLM 现在在 **每张 JPEG 前面**明确附带 CLIP_SEQUENCE_1_BASED。悉尼源视频有经校验的 10 秒连续编号切片，补 SOURCE_VIDEO_CLIP_START_MS 和 SOURCE_VIDEO_FRAME_TIME_MS（相对于视频起点，不是绝对拍摄时钟）；其他正常手机用户无此编号时只传顺序，不伪造相邻片段间隔。手机 capture_time_confidence=VERIFIED 且来源可信时才传 VERIFIED_CAPTURE_TIME_UNIX_MS。
- 模型提示词调整为按时间线组织经历，并明确新的地点与活动通常意味着新的 Chapter；同一地点连续可合章，不因恰好属于 citywalk 就合并不同区域；同一地标隔很久再次出现，不默认并到前一章。不会固定每120秒必须开新章。
- S04/S07 旧模型路径完全不变，只有 Direct VLM stage 追加时间标签；新单元测试使用内存模拟 Provider 请求，确认时间标签出现在对应 JPEG 之前。
- 这是算法输入/提示词契约修复；具体分章稳定性仍须用删除前72秒的新干净数据组进行独立真实 VLM 质量对照。不能把时间标签测试通过当作质量实测改善。
