# Diary One Canonical Checkpoint V1.20 — Aha–Chapter Narrative Independence

**状态：** FROZEN
**冻结日期：** 2026-08-27
**决策来源：** 用户确认“Chapter 核心/高潮/结果不得重复成为 Aha；Chapter 未成立时强局部 peak 仍可独立成为 Aha”，并确认 44-case 内部交叉检查结论
**作用范围：** S07 Aha standalone eligibility 的 Chapter-relative 解释、S09 Chapter–Aha pair narrative independence、co-selection conflict 与 cross-Revision behavior
**继承关系：** 继承 V1.19–V1.1 与 V1.0；只覆盖 V1.17/V1.19 中与本文冲突的 Chapter–Aha 共选解释
**验证依据：** [Targeted Amendment Working V0.1](S07_S09_AHA_CHAPTER_NARRATIVE_INDEPENDENCE_AMENDMENT_WORKING_V0_1.md)、[Internal Cross-Check V0.1](S07_S09_AHA_CHAPTER_NARRATIVE_INDEPENDENCE_INTERNAL_CROSS_CHECK_V0_1.md)
**明确不覆盖：** S10 Chapter/Aha final-render reuse、App 是否重复展示同一画面、S11 文案、S12 Claim、真实阈值/模型校准、上传工程、Firmware/SDK、共享状态、隐私/伦理/治理专题

## 1. 冻结结论

`embedded` 只表示 Aha 位于 Chapter 的时间、Episode 或 Evidence 范围内，不代表它天然具有独立 Memory 资格，也不代表 App 必须把它嵌入 Chapter 卡片。

~~~text
temporal containment
≠ narrative independence

selected Chapter
+ Aha is its core / climax / outcome / same-story restatement
→ MUST NOT COSELECT

no conflicting Chapter selected
+ Aha independently passes all Aha gates
→ MAY COMPETE AS STANDALONE AHA
~~~

因此：

1. 完整生日 Chapter 已选中时，作为其核心/高潮的“吹灭蜡烛”不能再占一个 Aha；
2. 如果完整生日 Chapter 未成立或未入选，同一个吹蜡烛 peak 仍可以作为 Aha Candidate 独立竞争，但不能因 Chapter 失败而自动降级获得资格；
3. 古镇观光过程中的甜品惊喜互动可以是不同故事；普通甜品静物照、Manual intent 或“看起来好吃”不能自动成为 Aha；
4. 同一事件相对不同 Chapter skeleton 可以得到不同 pair result；不存在“吹蜡烛永远不是 Aha”或“甜品永远是独立 Aha”的事件类别标签。

## 2. 全链路位置与权限

~~~text
S07
  bounded Aha Candidate
  Local Peak + standalone Independent Memory Value
        ↓
S08
  allowed objective validation only
        ↓
S09
  Chapter/Aha pair comparison
  ChapterAhaNarrativeIndependenceGate
  complete-set constraints
        ↓
S10
  one Anchor + one PHOTO/LIVE_2S
  only for already selected Aha membership
~~~

### 2.1 S07

S07 保留一个独立合法的 Aha Candidate，不因某个潜在 Chapter 存在就永久删除它。最终 Chapter 可能未入选、后续扩充或媒体不足；S07 不知道 winning set，不能提前决定 pair co-selection。

### 2.2 S09

S09 在每个仍具竞争力的 Chapter skeleton 接入 Aha 时，对具体 pair 执行本文 Gate。它使用已有 grounded CandidateContentUnit、peak、progression/outcome、Episode relation、core coverage 与 Evidence，不创建新 Candidate、不写故事、不重新看 Raw。

### 2.3 S10

S10 只消费已经合法通过 S09 membership 的 Aha。如果一个同故事 core Aha 被错误共选，S10 必须报告 relation/input contract invalid；不得通过换 Frame、Anchor、格式、RawAsset 或画面风格制造虚假的故事独立性。

## 3. 运行时术语

### 3.1 Chapter core story basis

由已有 grounded facts、CandidateContentUnit、progression/outcome、Episode relation 与 core coverage 确定的 Chapter 主要记忆命题。它不是 S11 尚未生成的标题或故事文案。

“用一句话描述是否相同”可用于人工评审和标签规范，但 Production Gate 不能依赖下游自由文本。

### 3.2 Chapter role of Aha

~~~text
CORE_COMPONENT
CLIMAX
RESOLUTION_OR_OUTCOME
REPRESENTATIVE_SUMMARY_PEAK
SIDE_EPISODE_LOCAL_EVENT
ROLE_UNRESOLVED
~~~

活动常识只可提名角色。最终角色必须结合当前 Chapter 的实际 core facts；相同事件在不同 Chapter 中可以具有不同角色。

### 3.3 Narrative independence

Aha 与 Chapter 虽可共享时间、地点、RawAsset 或 Evidence，但表达一个不同、可独立理解的局部记忆命题；它不是 Chapter 核心故事的截短版、代表图、高潮或自然结局。

## 4. ChapterAhaNarrativeIndependenceGate

五道 Gate 必须全部 PASS，Chapter/Aha pair 才能成为 `EMBEDDED_DISTINCT_AHA`。

### Gate 1｜Aha standalone validity

Aha 必须已经合法通过：

- Local Peak Gate；
- Independent Memory Value Gate；
- 必要 S08 validation；
- 单 origin Moment、单 KEEP peak 与既有 interval；
- 不依赖未入选 Chapter 才能理解基本事实。

### Gate 2｜Different grounded memory proposition

Aha 必须增加不同于 Chapter core story 的局部事件谓词、互动、变化、现象或结果。

以下不能 PASS：

- Chapter core 的短版本；
- 最漂亮、最戏剧化或最有代表性的一幕；
- 同主体、同动作、同结果，仅角度、时间点、格式或 RawAsset 不同；
- 只能解释为“Chapter 的高潮画面”。

### Gate 3｜Not Chapter core/climax/outcome

Aha 对当前 Chapter 的角色必须为 `SIDE_EPISODE_LOCAL_EVENT`。只要已证明是 `CORE_COMPONENT / CLIMAX / RESOLUTION_OR_OUTCOME / REPRESENTATIVE_SUMMARY_PEAK`，即 FAIL。

### Gate 4｜Chapter-without-Aha semantic robustness

暂时排除该 Aha peak 对 Chapter core story 的特有贡献后，Chapter 必须继续：

- 保有相同 core story identity；
- 在语义层仍是完整、可识别的 Episode；
- 保有主要 progression/outcome 或其他核心组织关系；
- 不需要改写成另一个故事才能成立。

这是 pair-level 语义反事实，不删除真实 RawAsset/Evidence/媒体，不重新计算 S10 的 2–5 项媒体容量，也不预先决定 Chapter 正文是否继续使用相关 Beat。

### Gate 5｜Aha-without-Chapter independence

不借用 Chapter title/story 或 Aha interval 外的 Beat，Aha 仍必须：

- 基本事实可独立理解；
- peak 可由自身 Evidence 直接定位；
- 有区别于 Chapter 的独立记忆价值；
- 适合由一个 Anchor 与一个用户可见媒体项表达。

## 5. 决策状态与 S09 映射

~~~text
NARRATIVELY_DISTINCT_PASS
SAME_STORY_CORE_FAIL
SAME_STORY_RESTATEMENT_FAIL
AHA_CONTEXT_DEPENDENT_FAIL
NARRATIVE_RELATION_UNRESOLVED
NARRATIVE_RELATION_CONTRACT_INVALID
~~~

| Decision | S09 mapping | Co-selection effect |
|---|---|---|
| `NARRATIVELY_DISTINCT_PASS` | `EMBEDDED_DISTINCT_AHA` | allow；仍须通过完整 set marginal contribution/constraints |
| `SAME_STORY_CORE_FAIL` | directed `NESTED_DOMINANCE`，Chapter dominates | must not co-select |
| `SAME_STORY_RESTATEMENT_FAIL` | `SAME_MEMORY_REDUNDANCY` | must not co-select |
| `AHA_CONTEXT_DEPENDENT_FAIL` | Aha standalone floor fail | 不能借 Chapter 获得 Aha 资格 |
| `NARRATIVE_RELATION_UNRESOLVED` | `UNRESOLVED_POTENTIAL_CONFLICT` | current Revision at most one |
| contract invalid | block affected pair/set | 不用相似度、排序或数量兜底 |

对 Chapter–Aha pair，generic `PARTIAL_OVERLAP` cost 不能绕过本文 Gate。Aha 一旦是 Chapter core/climax/outcome 或同故事重述，即使有轻微新增反应、细节或画面，也不能获准共存。

## 6. Set search 与多 Chapter 行为

### 6.1 Pair-specific

同一 Aha 可以相对 Chapter A 为 `EMBEDDED_DISTINCT_AHA`，相对 Chapter B 为 `NESTED_DOMINANCE`，在没有冲突 Chapter 入选时又可以走 standalone path。S09 不得先给 Aha 全局贴“embedded 可用/不可用”标签。

### 6.2 All-relevant-pairs

一个完整 set 含多个 Chapter 时，同一 Aha 必须与每个存在时间、Episode、Evidence 或 Memory-basis overlap 的已选 Chapter 分别得到安全结果。任一 hard same-story/nested conflict 都使该共选组合非法；不能由它与另一个 Chapter 的 PASS 抵消。

### 6.3 Chapter 已入选

同故事 Aha 不占 Aha 名额。对应 peak 仍可作为 Chapter Beat、正文或 Hero 候选，并继续保留在 RawAsset、Manual 窗口、Evidence 与事实账本中。

### 6.4 Chapter 未入选

Aha 只恢复独立竞争资格，不自动 PASS：

- `CHAPTER_DAY` 中可与不冲突的其他 Chapter 共存；
- 没有合法 Chapter plan 时，可按既有规则竞争 `HIGHLIGHT_DAY exactly one strong Aha`；
- Chapter Candidate 或 S10 媒体失败不能现场创造新 Aha Candidate。

## 7. Cross-Revision

1. prior Aha 后来因新增素材扩展为完整 Chapter：沿用 `AHA_TO_CHAPTER`，可保留 stable Memory identity，原 Aha 不重复占位；
2. prior Chapter 仍有效，新 Evidence 证明真正独立 side event：新 Aha 可在通过本文 Gate 后共存；
3. 新 RawAsset 只提供同一 Chapter core 的更清晰画面：属于 Evidence/媒体更新，不创建新 Aha；
4. relation 不确定时不随机继承、合并或共选，按 unresolved 处理。

## 8. 输出合同

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
  chapter_role_of_aha
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

不使用单一故事独立性分数。每道 Gate 保留离散状态与 same/distinct Evidence；关键 UNKNOWN 不能当 PASS。

## 9. Canonical 案例

| Chapter | Aha Candidate | Canonical result |
|---|---|---|
| 完整生日聚会 | 吹灭蜡烛 | 同故事 core；不共选 |
| 完整生日聚会 | 猫突然跳上蛋糕并引发集体反应 | 独立 side event；全部 Gate PASS 后可共存 |
| 古镇观光 | 普通甜品静物照片 | Aha standalone floor FAIL |
| 古镇观光 | 第一口甜品后的明确惊喜互动 | 故事独立时可共存 |
| 古镇美食体验 | 同一甜品互动 | 当前 Chapter core；不共存 |
| 登山过程 | 抵达山顶 | 自然 outcome；不共存 |
| 登山过程 | 途中短暂彩虹 | 独立自然现象；可共存候选 |
| 没有完整生日 Chapter | 清晰吹蜡烛 peak | 独立过全部 Gate 时可走 standalone path |
| 不同 RawAsset 拍到同一求婚 | 同一求婚 peak | 来源不同不创造故事独立性 |
| 故事关系 Evidence 不足 | 任意 peak | unresolved；当前 Revision 至多选一个 |

## 10. 成本与确定性

1. S09 最多 5 Chapter、3 Aha，完整 Chapter–Aha pair 上界为 15；
2. Gate 优先复用已有结构化 refs，不新增 Raw/HQ 上传、媒体解码、渲染或 App 交互；
3. embedding、scene/object/style、事件常识与 Manual intent 只能 nominate，不能单独 PASS；
4. 不依赖 S11 文案，不预设新增模型调用；
5. 相同 Revision、pair inputs、Evidence、policy 与 versions 必须得到相同离散结果；
6. 真实角色识别准确率、阈值与模型需求留给标注 Benchmark，不由实现静默改变。

## 11. 验证证据

内部交叉检查结果：

~~~text
44 / 44 boundary cases = expected deterministic outcome
12 / 12 invariants preserved
4 refinements applied
0 Day State changes
0 count-policy changes
0 S10 media-contract changes
0 new model/HQ/upload requirements
~~~

四项 refinement：

1. Chapter-without-Aha 是语义反事实，不重算 S10 媒体容量；
2. `PARTIAL_OVERLAP` 不能绕过故事独立性 Gate；
3. 多 Chapter set 必须执行 all-relevant-pairs 检查；
4. “好吃”不能由甜品类别、静物照片或 Manual intent 直接推断。

## 12. 状态边界

### FROZEN

- temporal containment 与 narrative independence 分离；
- S07 保留独立 Aha Candidate、S09 做 pair-specific 共选判断；
- 五道 Narrative Independence Gate；
- 六种离散 Decision 与 S09 relation/effect 映射；
- core/climax/outcome/representative peak 不得重复成为 Aha；
- generic `PARTIAL_OVERLAP` 不得绕过 Gate；
- multi-Chapter all-relevant-pairs hard-conflict 行为；
- Chapter 未入选时 Aha 只恢复独立竞争、不自动降级；
- `AHA_TO_CHAPTER` 与新独立 side-event cross-Revision 行为；
- no single score、UNKNOWN fail-closed 与输出审计合同；
- 不改变 Day State、数量或 S10 单媒体合同。

### OPEN / 待真实数据或后续专项

- `CORE_COMPONENT / CLIMAX / OUTCOME / SIDE_EVENT` 的真实标注规范与准确率；
- structured proposition comparison 的实现与阈值；
- 是否需要受限模型辅助，以及相对纯结构化规则的增益/成本；
- 不同用户对“独立值得回忆”的个性化校准；
- S10-D4.2 Chapter/Aha 是否允许复用同一 canonical final render；
- App 是否、何处以及如何重复展示同一底层画面；
- Production schema、solver integration、validator、telemetry 与 labeled benchmark。

### IMPLEMENTATION GAP

- 当前没有 Production `ChapterAhaNarrativeIndependenceDecision` schema/engine；
- 当前没有真实用户标签证明故事角色判断准确率；
- 当前 X01/实验链路不能代表本 Gate 已实现；
- V1.20 是产品与算法架构冻结，不是 Production readiness。

## 13. 覆盖关系

V1.20 只在以下冲突范围内覆盖旧表述：

1. V1.17 `IndependentMemoryValueGate` 的 Chapter-relative 共存解释：Aha 可独立成为 Candidate，但与具体 Chapter 共选必须通过本文 Gate；
2. V1.19 `EMBEDDED_DISTINCT_AHA`：从“位于 Chapter 内的独立 local event”收紧为五 Gate 全 PASS；
3. V1.19 generic `PARTIAL_OVERLAP`：不能授权一个 core/climax/outcome Aha 与 Chapter 共存；
4. V1.19 生日、街头表演等案例：事件类别和不同 peak 本身不够，必须逐 pair 通过本文 Gate。

V1.17/V1.19 的 Candidate interval、数量、Day State、relation graph、set objective/search、lineage、readiness 与其他未冲突内容继续有效。

## 14. 术语释义

| term | 简明含义 |
|---|---|
| temporal containment | Aha 在 Chapter 时间/Episode 范围内；只描述范围，不授予共选资格 |
| narrative independence | Aha 与 Chapter 讲的是不同、可独立理解的局部记忆 |
| core story basis | Chapter 成立所依赖的结构化核心事实与组织关系，不是后写的文案 |
| counterfactual | 为检查依赖关系而做的“假设移除”；不真的删除素材 |
| standalone Aha | 不依赖冲突 Chapter、独立通过全部 Aha Gate 的单一高光 Memory |
| pair-specific | 同一个 Aha 要相对每一个具体 Chapter 分别判断，结果可以不同 |
