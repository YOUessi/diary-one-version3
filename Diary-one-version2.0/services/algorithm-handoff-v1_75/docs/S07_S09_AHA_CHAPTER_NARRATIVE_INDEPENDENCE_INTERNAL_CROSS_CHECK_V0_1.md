# S07/S09 Aha–Chapter Narrative Independence — Internal Cross-Check V0.1

**状态：VALIDATION SOURCE / CROSS-CHECK PASSED / V1.20 FROZEN**
**日期：2026-08-27**
**被检合同：** `S07_S09_AHA_CHAPTER_NARRATIVE_INDEPENDENCE_AMENDMENT_WORKING_V0_1.md`
**案例数：** 44

## 1. 检查目标

本检查只验证这次窄范围修订是否能够：

1. 阻止 Chapter 核心、高潮、结果被重复选成 Aha；
2. 保留同一时间线内真正不同的小故事；
3. 不给“吹蜡烛、甜品、山顶”等事件类型贴永久标签；
4. 在 Chapter 未入选时保留 standalone Aha path；
5. 不让不同 Frame、格式、RawAsset 或强烈情绪绕过 same-story conflict；
6. 在多 Chapter、cross-Revision 与 unresolved 场景中保持确定性；
7. 不改变 Day State、数量上限、S10 单媒体或 HQ 合同。

本检查不判断实际模型准确率，不设置新的相似度/置信度阈值，不修改 App、Firmware/SDK、共享状态或旧 Canonical Checkpoint。

## 2. 必须保持的 Invariants

| ID | Invariant |
|---|---|
| I01 | temporal containment 不授予 Aha 共选资格 |
| I02 | Chapter core/climax/outcome 与同故事重述必须 hard block |
| I03 | `PARTIAL_OVERLAP` cost 不能绕开 narrative gate |
| I04 | 同一事件相对不同 Chapter skeleton 可以得到不同 pair result |
| I05 | Chapter 未选中不自动让 Aha PASS，只恢复其独立竞争资格 |
| I06 | 不同 Frame/format/RawAsset 不创造故事独立性 |
| I07 | 同 RawAsset/Evidence overlap 不自动否定真实独立故事 |
| I08 | unresolved 不默认独立，当前 Revision 至多选一个 |
| I09 | S09 不新建 Aha Candidate，S10 不纠正 membership |
| I10 | 故事反事实不重算 S10 2–5 项媒体容量 |
| I11 | 多 Chapter set 中任一 hard pair conflict 都不能被其他 PASS 抵消 |
| I12 | Aha 数量、Day State、single-media 与 format 合同保持不变 |

## 3. Case Matrix A｜Chapter 核心、高潮与结果

| ID | Chapter core story | Aha Candidate | 关键判断 | Expected |
|---|---|---|---|---|
| A01 | 完整生日聚会 | 吹灭蜡烛 | 当前 Chapter 的核心仪式/高潮 | `SAME_STORY_CORE_FAIL` |
| A02 | 求婚准备—求婚—回应 | 单膝跪地递戒指 | Chapter core proposition 的精确 peak | `SAME_STORY_CORE_FAIL` |
| A03 | 马拉松全过程 | 冲过终点 | 自然 resolution/outcome | `SAME_STORY_CORE_FAIL` |
| A04 | 婚礼仪式 | 交换戒指 | 必要核心组成 | `SAME_STORY_CORE_FAIL` |
| A05 | 毕业典礼 | 上台领取证书 | Chapter 主要 outcome | `SAME_STORY_CORE_FAIL` |
| A06 | 做陶器全过程 | 展示刚完成的作品 | progression 的自然结果 | `SAME_STORY_CORE_FAIL` |
| A07 | 登山过程 | 抵达山顶 | Chapter outcome；高视觉价值不改变关系 | `SAME_STORY_CORE_FAIL` |
| A08 | 演唱会完整经历 | 终场谢幕 | Chapter climax/result | `SAME_STORY_CORE_FAIL` |

**结果：** 8/8 PASS。Gate 3 单独失败即可阻止共选；不要求其他四道 Gate 也同时失败。

## 4. Case Matrix B｜时间线内的不同小故事

| ID | Chapter core story | Aha Candidate | 关键判断 | Expected |
|---|---|---|---|---|
| B01 | 普通生日聚餐 | 猫突然跳上蛋糕并引发集体反应 | 独立突发事件；移除后生日主线仍完整 | `NARRATIVELY_DISTINCT_PASS` |
| B02 | 生日聚餐 | 配送员突然唱歌，所有人惊讶回应 | 不属于生日主流程，具有独立互动 | `NARRATIVELY_DISTINCT_PASS` |
| B03 | 古镇观光 | 第一口甜品后出现清晰惊喜互动 | 不同局部活动/结果；观光主线仍完整 | `NARRATIVELY_DISTINCT_PASS` |
| B04 | 登山过程 | 途中短暂出现彩虹 | 独立自然现象，不是登山 outcome | `NARRATIVELY_DISTINCT_PASS` |
| B05 | 演唱会观看 | 歌手突然走到用户面前互动 | 独立局部互动，不是演出主线高潮 | `NARRATIVELY_DISTINCT_PASS` |
| B06 | 博物馆参观 | 工匠临时邀请用户体验一次操作 | 不同局部事件，可单 Anchor 表达 | `NARRATIVELY_DISTINCT_PASS` |
| B07 | 古镇 citywalk | 路边艺人突然完成高难度动作 | 独立表演 peak；步行主线不依赖它 | `NARRATIVELY_DISTINCT_PASS` |
| B08 | 公园野餐 | 孩子突然发现并指向一只小动物 | 独立局部发现，若 Evidence/价值门均 PASS | `NARRATIVELY_DISTINCT_PASS` |

**结果：** 8/8 PASS。这里的 PASS 只表示 Chapter–Aha 可共存，不替代 Aha 自身的 Local Peak、Independent Memory Value 与 S08 Evidence Gate。

## 5. Case Matrix C｜看似精彩但不能成为独立 Aha

| ID | 输入情况 | 错误捷径 | Expected |
|---|---|---|---|
| C01 | 古镇 Chapter 中一张普通甜品静物照 | “甜品类别不同，所以是 Aha” | standalone Gate FAIL |
| C02 | 用户手动拍一张咖啡照片 | “Manual intent 自动代表重要” | standalone Gate FAIL |
| C03 | 吹蜡烛 Chapter 用 VIDEO，Aha 想用 PHOTO | “格式不同，所以故事不同” | `SAME_STORY_RESTATEMENT_FAIL` |
| C04 | 两台设备分别拍到同一次吹蜡烛 | “RawAsset 不同，所以可共存” | `SAME_STORY_RESTATEMENT_FAIL` |
| C05 | 求婚 Chapter 中对方流泪回应 | “人物反应是新增内容” | response 仍是同故事 outcome；`SAME_STORY_CORE_FAIL` |
| C06 | 专门观看日落的 Chapter | 最漂亮的太阳落下瞬间 | 代表性 climax；`SAME_STORY_CORE_FAIL` |
| C07 | 古镇 Chapter 中出现景区牌匾 | “新对象/文字带来 semantic delta” | 无独立 peak/value，Aha FAIL |
| C08 | 普通行走画面 motion 很大 | “运动量高，适合 Live” | motion/media suitability 不创造 Aha |

**结果：** 8/8 PASS。视觉、来源与格式信号均没有越过故事关系和 Aha 双门。

## 6. Case Matrix D｜同一 Aha，相对不同 Chapter skeleton

| ID | Aha Candidate | Compared Chapter | Expected |
|---|---|---|---|
| D01 | 古镇甜品惊喜互动 | 古镇建筑观光 Chapter | `NARRATIVELY_DISTINCT_PASS` |
| D02 | 同一甜品互动 | 古镇美食体验 Chapter | `SAME_STORY_CORE_FAIL` |
| D03 | 歌手走近用户互动 | 整场演唱会观看 Chapter | `NARRATIVELY_DISTINCT_PASS` |
| D04 | 同一歌手互动 | 粉丝见面互动 Chapter | `SAME_STORY_CORE_FAIL` |
| D05 | 途中彩虹 | 登山 progression Chapter | `NARRATIVELY_DISTINCT_PASS` |
| D06 | 同一彩虹 | 专门追逐并观看彩虹的 Chapter | `SAME_STORY_CORE_FAIL` |

**结果：** 6/6 PASS。事件类别没有被永久标记；pair-specific 判定得到保留。

## 7. Case Matrix E｜Set、Day State 与 standalone path

| ID | 场景 | Expected |
|---|---|---|
| E01 | 只有清晰吹蜡烛 peak，没有完整生日 Chapter | 已存在 Aha Candidate 且独立过 Gate 时，可走 standalone path |
| E02 | 生日 Chapter Candidate 存在但未进入 winning set；其他旅行 Chapter 入选 | 吹蜡烛 Aha 可与不冲突的旅行 Chapter 共同竞争，不因未选生日 Chapter 被永久抑制 |
| E03 | Chapter Candidate 失败，但上游从未生成合法 Aha Candidate | 不自动把 Chapter 降级/改名为 Aha |
| E04 | Chapter 在 S10 被证明媒体不足，bounded S09 re-selection 发生 | 只有原池中已独立合法的 Aha 才可被 S09 选择 |
| E05 | 没有任何合法 Chapter，两个 standalone Aha 均强 | 继续执行 `HIGHLIGHT_DAY exactly one`，本修订不改数量 |
| E06 | 一个 Aha 与 Chapter A 故事独立、但与同 set 的 Chapter B 是 core conflict | 完整 set 非法；A 对应 PASS 不能抵消 B 的 hard conflict |

**结果：** 6/6 PASS。没有引入“Chapter 失败自动降级 Aha”，也没有改变 Day State。

## 8. Case Matrix F｜Cross-Revision、时间与来源边界

| ID | 场景 | Expected |
|---|---|---|
| F01 | R1 只有吹蜡烛 Aha；R2 新增准备/聚会/结果形成生日 Chapter | `AHA_TO_CHAPTER`，原 Aha 不重复占位 |
| F02 | prior 生日 Chapter 仍有效；新 Evidence 证明猫跳蛋糕独立事件 | 新 Aha 可通过 Gate 后共存，保留 distinct lineage |
| F03 | prior 生日 Chapter；新设备补到更清晰吹蜡烛画面 | 只是同故事新 Evidence/媒体，不创建新 Aha |
| F04 | 同一 RawAsset 既含古镇行走又含突然街头表演 peak | source overlap 不自动 conflict；故事 Gate PASS 时可共存候选 |
| F05 | 不同 RawAsset 分别记录同一个求婚核心 | source 分离不创造故事独立性；hard conflict |
| F06 | Aha 时间略早于 Chapter start，但属于同一准备—高潮故事 | 时间不重叠不自动证明不同故事；按 Memory basis 判定 |
| F07 | Aha 位于 Chapter interval 内，但属于明确独立突发事件 | temporal containment 不阻止 Gate PASS |
| F08 | Evidence 无法确定该 peak 是 Chapter 核心还是支线 | `NARRATIVE_RELATION_UNRESOLVED`；当前 Revision 至多选一个 |

**结果：** 8/8 PASS。Cross-Revision、RawAsset 与时间边界没有覆盖故事证据。

## 9. 发现并应用的 Refinements

### R1｜Counterfactual 必须是语义反事实

初稿“Chapter-without-Aha”可能被误解为删除媒体后重新计算 S10 的 2–5 项容量。已修正为：只判断 Chapter core story 的存在理由、完整性与组织关系，不删除真实内容，也不重算媒体容量。

### R2｜Generic PARTIAL_OVERLAP 不得绕过 Gate

若 Aha 是 Chapter core/climax/outcome，即使包含轻微新增反应、细节或角度，也不能依靠 set-level redundancy cost 获准共选。已加入显式禁止。

### R3｜Multi-Chapter 必须执行 all-relevant-pairs 检查

一个 Aha 对 Chapter A 独立、对 Chapter B 冲突时，含 A/B/Aha 的完整 set 仍非法。已加入“任一 hard conflict 不可由其他 PASS 抵消”。

### R4｜“好吃”不是默认视觉事实

甜品类别、静物照片或 Manual intent 不足以证明体验高光。只有可验证的互动、变化、现象或重要细节才能进入 Aha Gate；主观味觉 Claim 仍受 Evidence/Claim boundary 约束。

## 10. 交叉检查结论

~~~text
44 / 44 cases = expected deterministic outcome
12 / 12 invariants preserved
4 refinements recorded/applied
0 Day State changes
0 count-policy changes
0 S10 media-contract changes
0 new model/HQ/upload requirements
~~~

**结论：** 修订逻辑通过本轮内部合同检查，可以进入“冻结前确认”阶段；尚未经过真实用户素材 Benchmark，因此不能宣称实现准确率已验证，也不能直接修改旧 V1.17/V1.19 Checkpoint。

## 11. 冻结承接

1. 用户已确认本轮交叉检查结论；
2. `CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md` 已承接冻结；
3. S10 dependency 已更新，可以恢复 D4.2；
4. 实现、标注规范和真实用户 Benchmark 留到后续工程/实验阶段。
