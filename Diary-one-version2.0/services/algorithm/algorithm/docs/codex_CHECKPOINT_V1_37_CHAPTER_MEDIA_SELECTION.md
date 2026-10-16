# codex V1.37 — Chapter 展示精选与三项底线

2026-09-03。状态：LOCAL_IMPLEMENTATION_AND_WEB_INTEGRATION_VERIFIED_NOT_REAL_MODEL_QUALITY_VERIFIED。

## 范围与真实依据

用户确认：只处理 Chapter 内展示素材精选，3 项是最低数量，4～5 项不是必须填满的目标；相似素材择优保留，不通过过度去重删除整章。不重写聚类、时间、Aha 或 Writer 规则，不修改 Firmware/SDK、共享状态、原始素材；公开测试仍暂停。

最新真实运行 `670b2417-d3a5-424b-a3c0-a1df6eb031cd` 使用 Storyline V03 / Writer V02，26 项输入，Chapter 展示数量为 4、4、2、5。S10 当前 `min(5, len(members))` 会填满名额。已直接查看 Person 2 的 13、12、11、10.jpg；11 与 12 构图高度接近。这个真实反馈与代码共同构成本次调整依据，不构造语义反例，不把骆驼或文件名写入规则。

## 已核对基线

`x02.py` SHA-256 为 `6cdcefdd564502cb11ac282153bc84902cbf7ede11894bed85a7a891ffc2ba1e`，Storyline V03 文件为 `3da709072857288d1301a56a936d8d03dfd3c1654c88d9d9e09176071180122b`，与 V1.35 一致。Web 已按 V1.36 接入。已有未提交改动全部保留。

## 实现约束

- 增量版本 `DIARY_ONE_X02_CHAPTER_MEDIA_V01` 独立记录展示策略；Storyline V03 的内容分组方式与 Writer V02 不变。新展示下限优先于旧双素材例外，两个素材仍保留事实与诊断候选，但不能作为正式 Chapter。
- 对超过 3 个成员的已选 Chapter，S10 使用现有视觉模型直接比较已上传的代表画面，每章最多一次、每项一张当前预览帧、最多 12 帧；不增加抽帧或补传，不增加模型重试，仍受全轮调用预算约束。恰好 3 项不需要新增视觉比较调用。
- 模型给出成员优先顺序与建议展示数量；允许相似但有价值的差异，第四/第五项需要相对于前三项的新增展示价值。程序仅校验引用、完整排序和数量，不凭标签或关键词裁决内容关系。
- 只更改展示子集，Chapter 成员、事实和原始素材不删。建议数量低于 3 时保留排序最前的 3 项；模型调用失败或排序不可用时明确采用画质排序的三项回退，不把失败冒充去重成功，也不因此删除已有合格 Chapter。
- 新增 S10 时间、Token、成本与选择来源审计，Web 同步版本和三项校验。技术测试不代表真实模型质量通过。

## 完成与验证

- 算法相关 77 项、服务 21 项、素材输入 14 项检查通过，共 112 项；Web 构建与 53 项检查通过。Web 本步相关页面/接口严格类型检查通过，两仓 `git diff --check` 通过。
- 服务测试首次在端口受限时跳过一项；取得本轮网络权限后重跑，21 项全部通过，无跳过。没有用跳过的结果宣称服务验证完成。
- 新增测试复用真实运行的成员 ID/质量记录和已有接口替身，检查 4→3 展示不改变成员、最低三项、保留 4/5 的能力、二项不发布、失败不整章丢失，以及 S10 时间/Token/帧数记账。文件名、画面对象、人工示例排序均未写入运行规则；不构造语义反例。
- Web 使用实际 Python pipeline 的接口替身结果，确认三项结果能通过正式响应处理；缺失媒体策略版本、旧版本或仅两项结果不能伪装成新版本成功结果。
- 本轮没有付费模型调用，也没有把接口替身或人工看过四张图当成模型去重质量已通过。具体画面比较效果需要用户重新导入并完整运行后评价。

## 部署与后续

仅本地。停止旧的已空闲测试服务并启动新服务；沿用 `http://localhost:3000/` 与 `http://127.0.0.1:8787`。健康检查必须出现 `chapterMediaPolicyVersion=DIARY_ONE_X02_CHAPTER_MEDIA_V01`。已保存的旧运行与人工评价不改写。

新增比较复用现有 Qwen 视觉网关：每章超过三项才调用，最多四章/四次；每章最多 12 个既有预览帧，沿用 4 MiB 请求上限，不重试，并优先预留现有 Writer 调用预算。超过比较预算时会显示画质回退，不声称完成去重。视频只比较当前静态预览，不宣称已比较完整动作。

旧 Storyline V03 文件未改写，仍保留分组候选的历史两成员描述；当前媒体发布策略显式覆盖其发布例外。结构模型被告知正式 Chapter 至少三项；若仍返回两项，保留其事实和诊断候选，在集合选择前判为不满足展示数量，不硬拼无关素材凑数。

本步结束，不继续调整 Aha、Writer 或用户评分。不发布公网，未将含其他阶段修改的整个工作区打包提交推送。

## 关键文件指纹

- `src/diary_one_ci/x02.py`：`4fc7433361959142b8a109be5abfdfaf4b72b27bfa94fcd3eadc7a98334f6d1b`
- `src/diary_one_ci/x01_server.py`：`e64d552aa3eac15b753b671aaed5850953015d992f5ff12ca7957e41bcbe700b`
- `src/diary_one_ci/codex_chapter_media.py`：`9a8e13828a4ba2120bfb79b015da5657923e9fc317e531a0951c994f4c8703e3`
- `contracts/codex_x02_staged_preview_v04_1_media_v01.schema.json`：`8ac32d76ec0a62170407a377fc46532c0cfc584e747a79178109e0724996d2b8`
- `tests/test_codex_x02_chapter_media.py`：`c215eac7d425e165b6b303d2782df1d50340a0b92c77b3ad2abbdc349a7d0184`
- Web `app/page.tsx`：`144d0044080e9a9bd55c4caac8e65b95593d3fefc402fdaa3219435eba9298e9`
- Web `app/lib/media-evidence.ts`：`f553ef18a6395fdafd6b28e6dcdad0a9fc7c068c11053f238f091fd9730e78e1`
- Web `app/lib/result-contract.ts`：`6ad66d36b03838e9aacadba7cd7c37b7a2675198869ea3f6f2b3b85d2ca90fad`
- Web `app/lib/contract-findings.ts`：`cce02178bf97c2c9366682f2a1e8fbe328bc35ba22d4befb7856ec3253bc432a`
- Web `app/lib/contracts.ts`：`6e812de1225a45e9e2c37fd95a610f4ff17fbf0dbd1fbd4091df0c5acfc3f79b`
