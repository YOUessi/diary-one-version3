# S07/S09 Aha–Chapter Narrative Independence — Targeted Amendment Working V0.1

**状态：DESIGN SOURCE / INTERNAL CROSS-CHECK PASSED / FROZEN BY CANONICAL V1.20**
**日期：2026-08-27**
**修改范围：** S07 Aha Independent Memory Value 与 S09 Chapter–Aha pair relation
**保持不变：** Aha interval、Local Peak Gate、Day State、数量上限、S10 单媒体与格式合同
**冻结承接：** `CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md`

> 本文是对冻结 V1.17/V1.19 的窄范围拟议修订。旧 Checkpoint 保持不可变历史；只有本文完成边界案例交叉检查并形成新的 Canonical Checkpoint 后，才正式覆盖旧定义中与本文冲突的部分。

## 1. 为什么需要这次收紧

已有合同允许 `EMBEDDED_DISTINCT_AHA`：Aha 可以发生在 Chapter 的时间/Episode 范围内，并在表达独立 local event 时与 Chapter 共存。

当前缺口是：“独立 local event”还没有被拆成足够严格的故事级判定。仅凭以下事实不能证明可以共存：

- Aha 位于 Chapter 时间线内部；
- Aha 有一个明显动作 peak；
- Chapter 与 Aha 使用不同 Frame、格式或 RawAsset；
- Aha 看起来更精彩；
- Aha 是 Chapter 中最有代表性的高潮；
- Aha 从完整 Chapter 中可以单独截出来。

如果 Aha 只是 Chapter 核心、高潮、结果或代表性瞬间的缩短表达，同时发布会让同一段 Memory 占据两个位置。

**确认后的产品原则：**

~~~text
temporal containment
≠ narrative independence

Chapter selected
+ Aha is Chapter core / climax / resolution / same-story restatement
→ must not co-select

Chapter not selected
+ the local peak independently passes all Aha gates
→ Aha may still be selected as standalone
~~~

## 2. 修改在全链路中的准确位置

~~~text
S07
  generate a bounded Aha Candidate
  test Local Peak + standalone Independent Memory Value
        ↓
S08
  validate only allowed objective facts
        ↓
S09 pair/set selection
  compare each Aha against each co-selectable Chapter
  run ChapterAhaNarrativeIndependenceGate
        ↓
S10
  only for the Aha that survived S09 membership
  select one EvidenceAnchor + one PHOTO/LIVE_2S media item
~~~

S07 不能因为某个潜在 Chapter 存在，就永久删除一个 Aha Candidate：最终 Chapter 可能未被选中、媒体不足或在后续 Revision 才形成。故事共存性必须由 S09 对具体 Chapter/Aha pair 与完整 set 判断。

S10 不负责纠正错误共选。若一个同故事 Aha 已进入 S10，说明上游 selection contract 漏判；S10 必须报 input/relation invalid，不能靠换画面制造“独立感”。

## 3. 术语

### 3.1 Temporal containment

Aha peak 位于 Chapter 的 capture interval、Episode 或 selected content scope 内。它只说明时间/范围关系，不说明二者具有不同故事价值，也不代表 App 要把 Aha 视觉嵌入 Chapter 卡片。

### 3.2 Chapter core story basis

由已有 grounded facts、CandidateContentUnit、progression/outcome、Episode relation 与 core coverage 共同确定的 Chapter 主要记忆命题。它不是 S11 后续生成的标题或故事文案。

运行时不得依赖尚未生成的 title/story 来判断独立性；“用一句话描述是否相同”只作为产品解释和人工 Benchmark 方法。

### 3.3 Chapter-core role

一个 Aha peak 对当前 Chapter 可能具有以下角色：

~~~text
CORE_COMPONENT
CLIMAX
RESOLUTION_OR_OUTCOME
REPRESENTATIVE_SUMMARY_PEAK
SIDE_EPISODE_LOCAL_EVENT
ROLE_UNRESOLVED
~~~

活动常识只能提名角色，不能单独定案。例如“吹蜡烛通常是生日核心”是强提示，但最终仍要结合当前 Chapter 的实际 core facts 与内容结构；“甜品通常是旅行支线”也不能自动证明独立。

### 3.4 Narrative independence

Aha 与 Chapter 虽可共享时间、地点或 Evidence，但表达不同的、可独立理解的局部记忆命题；它不是 Chapter 核心故事的截短版、代表图或自然结局。

## 4. ChapterAhaNarrativeIndependenceGate

只有下列五道 Gate 全部 PASS，Chapter 与 Aha 才能作为 `EMBEDDED_DISTINCT_AHA` 共存。

### Gate 1｜Aha standalone validity

Aha 自身已经通过：

- S07 Local Peak Gate；
- S07 Independent Memory Value Gate；
- 必要 S08 validation；
- 单一 origin Moment、单一 KEEP peak 与既有 interval 边界；
- 不依赖未入选 Chapter 才能理解其基本事实。

如果只是一张甜品照片、普通喝饮料、明显运动量或漂亮构图，没有可证实的局部互动、变化、现象或重要细节，本 Gate 失败。

### Gate 2｜Different grounded memory proposition

Aha peak 必须增加一个与 Chapter core story 不同的局部事件谓词、互动、变化、现象或结果。下列情况 FAIL：

- 只是把 Chapter core 用更短时间范围重述；
- 只是从 Chapter 中挑出最漂亮或最有代表性的一幕；
- 主体、动作和结果均与 Chapter core 相同，仅角度/格式/时间点不同；
- Aha 的意义只能表述为“Chapter 的高潮画面”。

不同地点、对象、画面风格或 embedding 只能提名差异，不能单独 PASS。

### Gate 3｜Not a Chapter core/climax/outcome role

Aha 对当前 Chapter 的角色必须是 `SIDE_EPISODE_LOCAL_EVENT`。以下任一已被 Evidence 支持时 FAIL：

- Chapter 的必要核心组成；
- Chapter progression 的主要高潮；
- Chapter 的自然 resolution/outcome；
- 足以代表或摘要整个 Chapter 的核心 peak。

该角色是相对当前 Chapter 判断，不给事件类型贴永久标签。同一个“吃甜品”在古镇观光 Chapter 中可能是支线，在古镇美食 Chapter 中可能就是核心；同一个“吹蜡烛”在完整生日 Chapter 中通常是核心，但在没有生日 Chapter 的集合中仍可独立走 Aha path。

### Gate 4｜Chapter-without-Aha robustness

在结构化反事实评估中，暂时排除 Aha peak 对 Chapter core story 的特有贡献后，Chapter 必须仍然：

- 保有相同 core story identity；
- 在语义层仍是完整、可识别的 Episode，而不是只剩零散片段；
- 保有其主要 progression/outcome 或其他原本成立的核心组织关系；
- 不需要改写成另一段故事才能成立。

若移除后 Chapter 丢失核心、高潮、自然结果或代表性主轴，本 Gate FAIL。

这里的“移除”是 pair-level counterfactual audit，不会真的删除 RawAsset、Evidence、Chapter media 或事实账本内容，也不重新计算 S10 的 2–5 项最终媒体容量。通过本 Gate 只证明 Chapter 的存在理由不依赖该 Aha；Chapter 正文最终是否仍使用相关 Beat/媒体，留给后续 D4.2 决定。

### Gate 5｜Aha-without-Chapter independence

不借用 Chapter 的标题、叙事或其他未进入 Aha interval 的 Beat，Aha 仍必须：

- 基本事实可独立理解；
- local peak 可由自身 Evidence 直接定位；
- 具有区别于 Chapter 的记忆价值；
- 适合由一个 EvidenceAnchor 和一个用户可见媒体项表达。

如果必须展示 Chapter 的准备＋过程＋结果，才能理解所谓 Aha，它不是单一独立 Aha。

## 5. 唯一决策状态与 S09 映射

~~~text
NARRATIVELY_DISTINCT_PASS
SAME_STORY_CORE_FAIL
SAME_STORY_RESTATEMENT_FAIL
AHA_CONTEXT_DEPENDENT_FAIL
NARRATIVE_RELATION_UNRESOLVED
NARRATIVE_RELATION_CONTRACT_INVALID
~~~

映射规则：

| Gate result | S09 relation/effect |
|---|---|
| `NARRATIVELY_DISTINCT_PASS` | `EMBEDDED_DISTINCT_AHA`；允许共存，但仍需通过 marginal contribution 与完整 set 目标 |
| `SAME_STORY_CORE_FAIL` | `NESTED_DOMINANCE`；Chapter dominates，同一 set 不共选 |
| `SAME_STORY_RESTATEMENT_FAIL` | `SAME_MEMORY_REDUNDANCY`；同一 set 不共选 |
| `AHA_CONTEXT_DEPENDENT_FAIL` | Aha 不满足独立 Aha floor；不能依赖该 Chapter 获得资格 |
| `NARRATIVE_RELATION_UNRESOLVED` | `UNRESOLVED_POTENTIAL_CONFLICT`；当前 Revision 至多选一个 |
| contract invalid | 阻断该 pair/set，不用相似度或排序兜底 |

`EMBEDDED_DISTINCT_AHA` 表示“时间/Episode 可能重叠，但故事独立”；它不是“从 Chapter 中随便摘一个精彩画面”。

对 Chapter–Aha pair，generic `PARTIAL_OVERLAP` cost 不能绕过本 Gate：Aha 一旦是该 Chapter 的 core/climax/outcome 或同故事重述，即使它还包含轻微新增反应、角度或细节，也不能仅按“部分重叠但有增量”获准共存。只有完整通过 Narrative Independence Gate 才能建立允许共选关系。

## 6. Set search 行为

### 6.1 Pair-specific，不给事件贴永久标签

同一个 Aha 可以：

- 与 Chapter A 为 `NESTED_DOMINANCE`；
- 与 Chapter B 为 `EMBEDDED_DISTINCT_AHA`；
- 在没有任何 Chapter 入选时通过 standalone Aha gate。

因此 S09 在每个仍具竞争力的 Chapter skeleton 接入 Aha 时，分别执行本 Gate。不能先把 Aha 全局标为“embedded 可用”或“永远不能用”。

若一个完整 set 含多个 Chapter，同一 Aha 必须与每个存在时间、Episode、Evidence 或 Memory-basis overlap 的已选 Chapter 分别得到安全结果。只要它与其中一个 Chapter 为 hard same-story/nested conflict，该完整 set 就不能共选这两个成员；不能用它与另一个 Chapter 的 PASS 抵消该冲突。

### 6.2 Chapter 已选中时

若 Aha 是该 Chapter 的 core/climax/outcome 或同故事重述：

- 不同时占用 Aha 名额；
- 相关 peak 仍可作为 Chapter 的一个 Beat、正文媒体或 Hero 候选；
- 不删除 RawAsset、Manual 窗口、Evidence 或事实记录；
- 不通过换 Frame、换格式或换 Anchor 绕开关系冲突。

### 6.3 Chapter 未成立或未入选时

如果不存在与该 Aha 冲突的已选 Chapter，Aha 仍可按原有规则被选择：

- `CHAPTER_DAY`：可与其他叙事独立的 Chapter 共存；
- `HIGHLIGHT_DAY`：没有合法 Chapter plan 时，可成为 exactly one strong standalone Aha；
- Chapter 候选失败不会自动让 Aha PASS，Aha 必须独立满足自己的全部 Gate。

**案例：** 当天只有清晰的吹蜡烛 peak，无法形成完整生日 Chapter；该 peak 若通过 Local Peak、Independent Memory Value、Evidence 与媒体下限，可以成为 standalone Aha。它不是因为 Chapter 失败而自动降级得到资格。

### 6.4 Cross-Revision

已有 Aha 后来因新增素材扩展为完整 Chapter 时，继续沿用 `AHA_TO_CHAPTER`：可以保留 stable Memory identity，但原 Aha 不再重复占位。

若 prior Chapter 仍存在、新增素材只证明一个真正独立的局部事件，则该 Aha 可以作为新独立 Memory 进入当前 set，但必须通过本 Gate 与 lineage/redundancy 检查。

## 7. 输出合同

~~~text
ChapterAhaNarrativeIndependenceDecision
  revision_ref
  selection_attempt_ref
  chapter_selection_record_ref
  aha_selection_record_ref
  temporal_relation
  chapter_core_fact_refs[]
  chapter_core_content_unit_refs[]
  chapter_progression_outcome_refs[]
  aha_peak_event_ref
  aha_peak_evidence_refs[]
  same_story_evidence_refs[]
  distinct_story_evidence_refs[]
  chapter_role_of_aha =
    CORE_COMPONENT
    | CLIMAX
    | RESOLUTION_OR_OUTCOME
    | REPRESENTATIVE_SUMMARY_PEAK
    | SIDE_EPISODE_LOCAL_EVENT
    | ROLE_UNRESOLVED
  standalone_aha_gate_state
  grounded_proposition_difference_state
  chapter_without_aha_state =
    CORE_STORY_PRESERVED
    | CORE_STORY_BROKEN
    | COUNTERFACTUAL_UNRESOLVED
  aha_without_chapter_state =
    INDEPENDENTLY_UNDERSTANDABLE
    | CHAPTER_CONTEXT_DEPENDENT
    | INDEPENDENCE_UNRESOLVED
  narrative_independence_state
  mapped_s09_relation
  co_selection_effect
  reason_refs[]
  policy_and_signal_versions
  decision_trace
~~~

不使用单一“故事独立性分数”。每道 Gate 保留离散结果与支持/反对证据；任何关键 UNKNOWN 都不能按 PASS 处理。

## 8. 边界案例

| Chapter | Aha Candidate | 结果 | 原因 |
|---|---|---|---|
| 完整生日聚会 | 吹灭蜡烛 | 不共存 | Chapter 核心/高潮，同一故事 |
| 完整生日聚会 | 猫突然跳上蛋糕并引发集体反应 | 可共存候选 | 独立突发 local event；仍须通过全部 Aha Gate |
| 古镇观光 | 普通甜品静物照片 | Aha FAIL | 没有可证实 local peak；可留作 Chapter/Manual 素材 |
| 古镇观光 | 第一口甜品后的明确惊喜互动 | 可共存候选 | 不同局部事件，移除后观光主线仍完整 |
| 古镇美食之旅 | 核心招牌甜品体验 | 不共存 | 对该 Chapter 是核心内容，不因“甜品”类型自动独立 |
| 登山过程 | 抵达山顶 | 通常不共存 | 自然 resolution/outcome |
| 登山过程 | 途中短暂出现彩虹 | 可共存候选 | 独立、短暂自然现象 |
| 演唱会 | 终场高潮/谢幕 | 通常不共存 | Chapter climax/result |
| 演唱会 | 歌手突然走到用户面前互动 | 可共存候选 | 与演出主线不同的局部互动 |
| 婚礼流程 | 交换戒指 | 不共存 | 核心仪式组成 |
| 婚礼流程 | 小朋友突然送来一幅画 | 可共存候选 | 独立局部事件，若 Evidence 与价值 Gate 均 PASS |
| 生日 Chapter 不成立 | 清晰吹蜡烛 peak | 可走 standalone path | 没有共选 Chapter，但仍须独立通过全部 Aha Gate |
| 故事关系证据相互冲突 | 任意 peak | 至多选一个 | unresolved 不能冒充独立 |

## 9. 成本与实现纪律

1. S09 最多 5 Chapter、3 Aha，完整 pair 上界为 15；增加本 Gate 的结构化比较成本很低；
2. 优先复用 S07/S08/S09 已有 ContentUnit、peak、progression、outcome、relation 与 core coverage refs；
3. 本 Gate 不新增 Raw/HQ 上传、媒体解码、渲染或 App 交互；
4. 不依赖 S11 尚未生成的标题/故事；
5. embedding、场景、物体、风格与事件常识只能 nominate，不能单独 PASS；
6. 若已有结构化 Evidence 不足，输出 unresolved，不默认独立；
7. 是否需要模型辅助生成结构化 proposition 只能在真实数据实验中评估，V1 合同不预设新增模型调用。

## 10. 不受本修订影响的冻结规则

- Aha 单 origin Moment、单 KEEP peak、最多 3 个连续 eligible Windows/3 分钟；
- Local Peak 与 Independent Memory Value 均必须成立；
- 普通 origin 与 Transition origin 的 Candidate cap；
- S09 `CHAPTER_DAY / HIGHLIGHT_DAY / EMPTY_DAY`；
- Chapter day 最多 3 Aha、Highlight day exactly one strong Aha；
- 数量目标不是配额；
- S10 Aha 恰好一个用户可见媒体项，只允许 PHOTO/LIVE_2S；
- Chapter/Aha membership 由 S09 决定，S10 不能换故事；
- Manual 素材继续保留在事实账本和独立 Manual 窗口；
- Manual 任意时长视频 Window 合同继续 OPEN。

## 11. 交叉检查与冻结边界

内部交叉检查已经覆盖：

1. core/climax 与独立 side event 的边界是否稳定；
2. 同一事件相对不同 Chapter skeleton 时是否正确得到不同 pair result；
3. Chapter-without-Aha counterfactual 是否会错误伤害完整性；
4. 只有一个强 peak、没有 Chapter 时是否仍可进入 standalone path；
5. prior Aha→Chapter 与 prior Chapter＋new Aha 的 lineage 是否一致；
6. ordinary food/photo、漂亮画面与 Manual intent 是否不会误过 Aha Gate；
7. unresolved 是否始终 fail closed；
8. 本 Gate 是否会意外改变 Day State、数量目标或 S10 媒体合同。

上述 44 个案例与 12 项 Invariant 已通过，4 项 refinement 已回写，详见 `S07_S09_AHA_CHAPTER_NARRATIVE_INDEPENDENCE_INTERNAL_CROSS_CHECK_V0_1.md`。

用户已确认检查结论，冻结内容由 `CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md` 承接。V1.17/V1.19 历史 Checkpoint 保持原文不变，由 V1.20 在明确冲突范围内覆盖。
