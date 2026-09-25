# codex V1.57 — S10 有效精选接收修复

2026-09-04。状态：`LOCAL_IMPLEMENTATION_AND_REAL_RESPONSE_HANDOFF_REPLAY_VERIFIED_NOT_FULL_PIPELINE_QUALITY_ACCEPTED`。

## 边界与基线

承接 V1.56 真实素材流向核查，仅修复 S10 已返回有效精选却因未排完全部候选而被整组弃用的问题。不改聚类、Aha、Writer、模型调用、Web、App、Firmware/SDK、共享状态或封存交付包。

开工前已复核 V1.56 的当前文件指纹，未发现漂移：

- `codex_chapter_media.py`：`c61f6ed9de660a773e5daef611ccbcf7124b37db76e99577a2192cb3a2dfeaae`。
- `x02.py`：`b72fe93c3c7cb493f3ef3a5c7e8c60d6f647f1771266effe270c78fdf800f07b`。
- `x01_server.py`：`e64d552aa3eac15b753b671aaed5850953015d992f5ff12ca7957e41bcbe700b`。

素材依据是 V1.48 包 1 C3 的真实 9 项输入、M04/M08/M11 三项输出。固定保存原始回复和所需成员字段为 `tests/fixtures/codex_v1_48_s10_partial_ranking_real.json`，不把该选择宣布为人工质量真值。已有工作区改动全部保留。

## 已实现的最小变化

模型可仅返回精选顺序，也兼容完整排名；程序只保留实际返回的排名，不伪造落选项顺序。维持 3–5 项展示、引用/去重校验和无重试原则。接收修订单独版本化并进入每条 S10 审计；顶层媒体数量/展示策略 V01 与已有结果结构保持兼容。

具体规则：

- 返回至少 3 个有效、唯一、本 Chapter 内的素材编号，即可使用该排名，不再要求覆盖所有成员。
- 展示数量仍按 3–5 范围规范化，且不能超过实际返回排名的长度；例如只返回 3 个、却建议展示 5 个，不会擅自从未排名素材中补出 2 个。
- 兼容旧式完整排名。少于 3 个、未知/重复编号或错误数量类型，仍使用有明确标记的既有画质回退；不新增语义过滤或重试。
- Prompt 明确只返回精选项即可；Schema 增加唯一编号说明与约束，不要求完整排名。原字段名保留，以兼容既有响应。
- `ranked_observation_ids` 只记录实际使用的排名，新增 `ranking_scope=RETURNED_SUBSET/ALL_MEMBERS` 标明覆盖范围。模型失败时原有 `selection_source` 仍明确标识画质回退，不伪装成模型判断。
- 每项 S10 记录 `response_acceptance_version=DIARY_ONE_X02_CHAPTER_SELECTION_RESPONSE_V02`。顶层 `chapter_media_policy_version` 仍为 V01，表示未改动的 3–5 展示策略；识别本修复必须看新增接收版本或源码指纹，不能只看顶层 V01。

已检查仓库内排名消费者：媒体组装使用 `selected_observation_ids`，Writer 从最终媒体读取对应事实；没有要求落选项必须完整排名的下游逻辑。无需更改这两处代码。未知外部消费者未在本轮验收。

## 验证结果

| 同一份 V1.48 真实 S10 回复 | 修复前 | 修复后 |
| --- | --- | --- |
| 最终选择顺序 | M17、M08、M10 | M04、M08、M11，保持原模型顺序 |
| 选择来源 | 画质排序回退 | 模型选择 |
| 完整 Chapter 成员数 | 9 | 9 |
| 展示数量 | 3 | 3 |
| 沿河小船 M11 | 被回退替换 | 保留，并进入文案输入 |

离线回放还执行了现有媒体组装、Writer 上下文与出站 Prompt 构造：以历史候选成员/事实重建输入，最终出站 Writer 输入含所选三项的 5 条事实，包含 M11 的 `cf87fe59-663e-514c-aa3e-be251f1fd6bb`。没有将该输入发送到 API，也没有重写已保存的历史结果。重放前核对了原始回复与整轮结果哈希，fixture 回复与原回复相等。

- 先在修改前运行新增测试，真实三项回复仍被回退替换；修改后通过。
- 新增 5 项测试：真实回复原样接收、完整排名兼容、数量规范化不填充未排名项、编号/类型校验、3/4/5 项经媒体与 Writer 的接口贯通。
- 边界测试只变动真实编号的结构或既有接口替身；没有编造画面语义来新增算法规则。
- 相关测试 43 项通过。全仓运行 221 项：220 项通过、1 项既有本地端口权限限制测试跳过，没有失败。
- `git diff --check` 通过。新文件也完成空白检查。原 `x02.py`、`x01_server.py` 和既有媒体测试指纹不变。

## 交付范围与未完成事项

本轮仅修改一个运行文件 `src/diary_one_ci/codex_chapter_media.py`；新增一个真实回复 fixture、一份测试文件和本检查点。没有 API 调用，新增业务模型 token 和费用为 0。没有增设“河道必须入选”等内容规则。

这是本地接收及数据传递修复，**不是新模型质量、完整真实 pipeline 或 Web 部署验收**。没有重启/修改 Web、更新正式 App 交付包或覆盖旧实验/评价；现有 V1.48 结果不会自动变成新结果。后续真实整链路仍须重新运行与评分。

本步到此结束。下一独立任务是处理 Aha 去重中“导入相邻 + 大类相同就推断同一事件”的问题，然后另行处理 Writer 出口；不把它们混入此次修复。

## 完成指纹

- `src/diary_one_ci/codex_chapter_media.py`：`7c7fd4bdc45ffe7344c94fefa47653c71ff089b46d4b8043ddddbe54a461167e`。
- `tests/test_codex_x02_selection_acceptance.py`：`a2d0367743c3f4f2ab60c5b47d0c0388d3adfa486b11ed5c7da8009526dc9b7a`。
- `tests/fixtures/codex_v1_48_s10_partial_ranking_real.json`：`d3ef6030da3e2f0336c93e41629463aa3b0ff92fec3d875283163b4e60f11d19`。

本检查点就“必须完整排名”的接收要求替代 V1.37 中对应约束，不改写 V1.37/V1.56 历史记录；其余数量、归属、调用边界继续保持。
