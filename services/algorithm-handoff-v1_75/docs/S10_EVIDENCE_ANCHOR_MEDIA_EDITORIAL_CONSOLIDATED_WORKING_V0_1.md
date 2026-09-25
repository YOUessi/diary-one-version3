# S10 EvidenceAnchor & Media Editorial — Consolidated Working V0.1

**状态：** FROZEN BY `CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md`
**开始日期：** 2026-08-27
**上游冻结合同：** `CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md`、`CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md`
**下游边界：** S11 Grounded Narrative、S12 Final Validation、S13 HQ Render / Export

> 本文记录 S10 的逐项讨论、确认与交叉检查依据。S10 已由 Canonical V1.21 正式冻结；若本文与 V1.21 冲突，以 V1.21 为准。

## 1. S10 在全链路中的位置

~~~text
S09 SelectedMemorySet
→ S10 Content Beat / EvidenceAnchor / MediaDecision
→ S11 grounded title / story / tags
→ S12 final validation
→ S13 selected HQ source render / export
~~~

S09 已决定哪些 Chapter/Aha 成为当前 Revision 的 Memory。S10 不重新决定 Memory membership，只决定一个已选 Memory 应由哪些内容位置、精确证据位置与媒体形式呈现。

## 2. 继承的冻结方向

1. 必须先选 `EvidenceAnchor`，再决定 PHOTO / LIVE_2S / VIDEO_5S；不得分别先找“最好照片、最好 Live、最好视频”。
2. Chapter 可使用 PHOTO / LIVE_2S / VIDEO_5S；Aha 可使用 PHOTO / LIVE_2S，禁止 VIDEO_5S。
3. S10 只能在 S09 `S10HandoffEnvelope` 声明的当前已选 Memory scope 与白名单内工作。
4. KEEP 可进入 Anchor 候选；CONTEXT_ONLY 只能帮助理解和排序，`anchor_eligible=false`；DROP 禁止恢复。
5. S10 不得重新搜索全天、增加或替换 Chapter/Aha、改写 Candidate facts，或因画面漂亮改变 Memory membership。
6. S10 只产生最小 HQ source 请求计划；实际获取与渲染属于 S13。
7. Chapter/Aha 只有在 V1.20 `ChapterAhaNarrativeIndependenceDecision = NARRATIVELY_DISTINCT_PASS` 时才能作为时间重叠但故事独立的两个 Memory 共存；S10 不重新判断或绕过该关系。

## 3. S10 讨论路径

~~~text
S10-A1  Content Beat contract
→ S10-A2  Representative Evidence + exact EvidenceAnchor
→ S10-B   scoring signals + media format
→ S10-C   within-memory 3–5 set + order + hero + fallback
→ S10-D   HQ request + output/readiness contract
→ S10-E   cross-check + profile/media simulation
→ freeze S10
~~~

每个阶段单独讨论、举例、检查并确认；不能把内容发现、画面评分、数量编辑和渲染合同混为一个步骤。

## 4. S10-A1｜Content Beat 基础合同

**状态：CONFIRMED**

### 4.1 定义

`Content Beat` 是一个已选 Memory 中，具有独立内容意义、原则上值得占据一个展示位置的部分。

它不是 RawAsset、Frame、Window、媒体格式或新 Chapter，也不因新时间点、新机位或新文件自动成立。

### 4.2 先完整识别，再做 3–5 项编辑

~~~text
识别所有有证据、独立、非重复的 Content Beat candidates
→ S10-A2/B 判断 Anchor 与媒体可用性
→ S10-C 选择最终 3–5 个 Chapter media items
~~~

Content Beat 发现阶段不得强凑 3–5 个：

- 有 6 个真实 Beat 时，不在尚未比较 Anchor 与媒体可用性前过早删除；
- 只有 2 个真实 Beat 时，不为满足数量制造第三个重复 Beat；
- 最终 Chapter 少于 3 个可发布媒体项时如何处理，留到 S10-C readiness/fallback 合同决定。

### 4.3 来源与权限

1. Beat 必须来自当前已选 Memory 的 CandidateContentUnit refs，不重新读取或搜索全天素材。
2. 重复内容不因时间、机位、文件或视觉差异而自动形成多个 Beat。
3. 新阶段、动作、互动、转折或结果可以支持独立 Beat，但必须有 grounded content 与合法 KEEP Evidence。
4. 一条 CandidateContentUnit 不得被 S10 凭空拆成多个 Beat。长 Manual 只有在上游已经形成多个、时间与内容均不同的 CandidateContentUnit 时，才可能贡献多个 Beat。
5. CONTEXT_ONLY 可以帮助解释 Beat 的顺序或中断，但不能独立生成 Beat 或 Anchor；DROP 禁止进入。
6. Beat 阶段只判断内容位置，不提前选择精确画面、媒体格式或 Hero。

### 4.4 Chapter 与 Aha

- Chapter 可以包含多个 Content Beat，表达 Episode 的不同阶段、内容侧面或推进。
- Aha 是聚焦瞬间，原则上只有一个核心 Beat；邻近上下文不能把它扩成一个小 Chapter。

### 4.5 古镇案例

~~~text
09:00 进入牌坊
09:02 石板路行走
09:04 观察古建筑立面
09:06 再次拍到石板路
09:08 景区指示牌
09:30 进入现代奶茶店
09:40 回到古街继续行走
10:00 到达河边
~~~

可能的 Beat candidates：进入古镇、古街行走、观察建筑、奶茶短暂停留、河边结束。

- 09:02、09:06、09:40 是否属于同一“古街行走” Beat，必须按下一项 same/distinct 规则判断，不能只看时间或画面相似度；
- 09:04 虽与石板路同属古镇风格，但可能表达不同内容位置；
- 09:08 若只帮助确认地点，可保留为 supporting/context evidence，不必占展示位置；
- 奶茶店只有在已属于该 Memory 的 CandidateContentUnit 且具有独立内容贡献时才可成为 Beat；S10 不得跨 scope 把它加入；
- 本阶段不决定这些 Beat 最终选几个或使用何种媒体。

### 4.6 Aha 案例

生日 Chapter 可以包含准备蛋糕、点蜡烛、吹蜡烛、鼓掌、合照等 Beat。若“吹灭蜡烛”是该 Chapter 的核心/高潮，则不得再以 Aha 重复占位；若完整生日 Chapter 未成立，而吹灭 peak 独立通过 Aha 全部门槛，才可作为 standalone Aha。无论它是否合法入选，Aha 自身都只有一个核心 Beat，鼓掌与合照不能为了丰富 Aha 而被塞进同一个 Aha。

发生在生日时间范围内的独立突发事件，例如猫突然跳上蛋糕并引发大家明确反应，只有通过 Chapter–Aha 故事独立性 Gate 后，才可能与生日 Chapter 共存。详细修订见 `S07_S09_AHA_CHAPTER_NARRATIVE_INDEPENDENCE_AMENDMENT_WORKING_V0_1.md`。

## 5. S10-A1.1｜Same / Distinct Beat Decision

**状态：CONFIRMED**

### 5.1 上游独立性优先

CandidateContentUnit 在 S07/S08 已经过内容去重，并被认为仍有独立内容贡献。S10 默认保留这种独立性；只有存在明确的 `presentation redundancy` 证据时，才可把多个 ContentUnit 合并为同一个 Content Beat。

`presentation redundancy` 指两个事实或素材位置可能并非完全相同，但同时展示不会为用户增加可辨认的新内容。合并只影响最终展示位置，不删除 RawAsset、Evidence、CandidateContentUnit 或事实账本。

### 5.2 双向证据

每个需要比较的 pair 同时保存：

~~~text
SameBeatEvidence[]
DistinctBeatEvidence[]
~~~

Same 方向包括：相同核心动作、相同阶段/结果/展示作用、仅时间/角度/画面细节变化、删除一项不损失理解，以及上游 duplicate/alternate refs。

Distinct 方向包括：新的动作阶段、互动、转折、结果、内容焦点或 Episode 推进作用，以及 S08 已确认的 Long-Manual 内容多样性。

时间距离、场景相似或变化、RawAsset/Manual/Auto 来源、颜色风格与 embedding 相似度均只能 nominate 或辅助判断，不能单独决定 Same/Distinct。

### 5.3 三种唯一结果

~~~text
SAME_PRESENTATION_BEAT
DISTINCT_PRESENTATION_BEATS
UNRESOLVED_ALTERNATIVES
~~~

- `SAME_PRESENTATION_BEAT`：合并为一个 Beat；所有合法 Evidence 保留为后续 Anchor candidates；最终只占一个媒体位置。
- `DISTINCT_PRESENTATION_BEATS`：保持为不同 Beat candidates；是否都进入最终 3–5 项由 S10-C 决定。
- `UNRESOLVED_ALTERNATIVES`：不强行合并，也不能把成员分别计入已证明的内容丰富度；先形成 alternative group。S10-A2 若不能用精确 Evidence 解除歧义，S10-C 最多选择其中一个。

### 5.4 案例

1. 09:02 与 09:06 都只是石板路行走，没有新阶段或结果：`SAME_PRESENTATION_BEAT`。
2. 石板路行走与停下观察木雕建筑：即使同属古镇风格，也为 `DISTINCT_PRESENTATION_BEATS`。
3. 09:40 回到古街后若只是继续相同行走，归入已有 Beat；若 grounded facts 证明进入新的核心景点，可为不同 Beat。
4. 长 Manual 的“整理陶土、拉坯、展示成品”若已由 S08 确认内容多样性，保留三个 Beat；拉坯过程中的多个近景仍只对应一个 Beat。
5. 会议中幻灯片连续换页但活动与阶段未变，属于同一 Beat；出现明确决策结果时形成新的 Beat。

### 5.5 成本边界

本项只在一个已选 Memory 内比较已有 CandidateContentUnit，使用 grounded facts、progression、duplicate refs 与 validation findings；不新增 VLM/strong-model 调用、Raw/HQ 上传或全天搜索。

## 6. S10-A1.2｜ContentBeatInventory

**状态：CONFIRMED**

`ContentBeatInventory` 是一个已选 Memory 内全部 Beat candidates、关系、替代组、上下文与限制的完整清单和审计账本。它不选择 Frame、媒体格式、Hero 或用户可见文案。

### 6.1 构建顺序

~~~text
S10HandoffEnvelope scope/revision/whitelist validation
→ one atomic Beat candidate per legal CandidateContentUnit
→ compare presentation-redundancy nominees
→ merge proven SAME
→ preserve proven DISTINCT
→ create UNRESOLVED alternative groups
→ stable inventory order
→ ContentBeatInventory
~~~

### 6.2 建议结构

~~~text
ContentBeatInventory
  selected_memory_ref
  revision_ref
  memory_type
  beat_candidates[]
  unresolved_alternative_groups[]
  context_support_refs[]
  relation_decision_refs[]
  limitation_refs[]
  confirmed_distinct_capacity
  inventory_status
  construction_audit

ContentBeatCandidate
  beat_candidate_ref
  source_content_unit_refs[]
  grounded_fact_refs[]
  capture_span
  anchor_eligible_keep_evidence_refs[]
  context_only_support_refs[]
  limitation_refs[]
  relation_status
~~~

### 6.3 Invariants

1. 每个合法 CandidateContentUnit 必须恰好映射到一个 Beat candidate，或成为显式 unresolved alternative；非法输入必须显式隔离，不能静默消失。
2. 一条 CandidateContentUnit 不得被 S10 拆成多个 Beat。
3. 多条 CandidateContentUnit 只有在明确 SAME 证据下才可合并；合并后仍保留全部 source refs 与 Evidence。
4. 多成员 Beat 必须满足组内 pairwise compatibility；禁止用 `A≈B、B≈C` 自动推导 `A≈C` 的链式合并。
5. 若 same/distinct 关系形成矛盾链，输出 `BEAT_RELATION_CONFLICT` 并进入 unresolved；不得任意选择一个 partition。
6. unresolved alternative group 在后续 minimum/diversity proof 中最多贡献一个位置，未解除前不得共同入选。
7. CONTEXT_ONLY 只能进入 `context_only_support_refs`，不能进入 Anchor eligibility；DROP 禁止出现。
8. 合并后不足三个真实 Beat 仍如实输出，不能制造补位 Beat；S10-C 再决定 readiness/fallback。
9. Aha 恰好一个 core Beat；邻近 eligible Windows 只能支持该 Beat。若输入声明多个无关 core Beats，属于 contract invalid。
10. Inventory 按 Beat 最早 grounded capture time 排序，时间相同时使用 stable ID；该顺序只用于确定性记账，不提前冻结最终媒体叙事顺序。

### 6.4 Inventory 状态

~~~text
BEAT_INVENTORY_READY
BEAT_INVENTORY_READY_WITH_ALTERNATIVES
BEAT_INPUT_INVALID
~~~

- `READY`：Beat identity 已足够确定。
- `READY_WITH_ALTERNATIVES`：可进入 S10-A2，尝试由精确 Evidence 解除歧义。
- `INPUT_INVALID`：存在跨 Memory/Revision、非法 role、缺失 provenance 或其他合同错误；不得静默跳过。

### 6.5 古镇案例

~~~text
CU-01 进入牌坊
CU-02 石板路行走
CU-03 观察古建筑
CU-04 相似石板路行走
CU-05 河边结束

CU-02 SAME CU-04

Beat-01 [CU-01]        进入牌坊
Beat-02 [CU-02, CU-04] 古街行走
Beat-03 [CU-03]        观察古建筑
Beat-04 [CU-05]        河边结束

confirmed_distinct_capacity = 4
inventory_status = BEAT_INVENTORY_READY
~~~

### 6.6 成本边界

先从每条 ContentUnit 建立原子 candidate，只对可能展示重复的 pair 做关系判断；多项合并时再执行组内兼容检查。仍只使用现有结构化证据，不新增模型、Raw/HQ 上传或全天搜索。

## 7. S10-A1 Closeout

**状态：FROZEN BY CANONICAL V1.21**

S10-A1 已确认 Content Beat 定义、发现与最终 3–5 编辑分离、Same/Distinct/Unresolved 决策、ContentBeatInventory、全量记账和防链式误合并合同。它已随其他 S10 阶段通过 S10-E 全链路检查，并由 Canonical V1.21 冻结。

下一项进入 S10-A2：先定义 Representative Evidence shortlist 与 EvidenceAnchor 的合法对象和引用合同，再讨论 Anchor 评分。

## 8. S10-A2.1｜Anchor Eligibility 与合法目标

**状态：CONFIRMED**

`EvidenceAnchor` 是“这个 Beat 最终应落在原素材哪个精确位置”的可追溯证据地址，不是最终 PHOTO/LIVE_2S/VIDEO_5S，也不是已经取回的 HQ render。

### 8.1 先合法性，后评分

~~~text
Content Beat
→ AnchorEligibilitySet
→ Representative Evidence scoring / shortlist
→ EvidenceAnchor
→ Media Format Decision
~~~

合法性不能被高画质或高模型分数补救。白名单外、CONTEXT_ONLY、DROP 或不支持该 Beat 核心内容的位置，不得进入 `AnchorEligibilitySet`。

### 8.2 三种合法目标

~~~text
STILL_ASSET
FRAME_TIMEPOINT
EVIDENCE_SUPPORTED_INTERVAL
~~~

- `STILL_ASSET`：Manual Photo 本身；无视频 source timestamp，不伪造 `0.0s`。
- `FRAME_TIMEPOINT`：视频中的具体 Evidence Frame；使用实际解码 timestamp，目标抽帧 offset 只保留在 provenance。
- `EVIDENCE_SUPPORTED_INTERVAL`：一个 RawAsset 内由已有 temporal evidence 支持的精确区间。静态帧不能单独证明帧间连续动作，也不能伪造 interval。

Anchor 最终渲染位置必须落在一个 RawAsset 内；不得跨两个视频、跨 Photo/Video 或跨 Memory 拼接成一个 Anchor。

### 8.3 BeatAnchorRequirement

候选评分前必须为每个 Beat 固定统一的 Anchor 要求卡：

~~~text
BeatAnchorRequirement
  beat_candidate_ref
  core_grounded_fact_refs[]
  optional_supporting_fact_refs[]
  evidence_mode_requirement =
    STATIC_SUFFICIENT
    | TEMPORAL_HELPFUL
    | TEMPORAL_REQUIRED
    | UNKNOWN
  semantic_floor
  derivation_refs[]
  limitation_refs[]
~~~

- `STATIC_SUFFICIENT`：一个可信静态位置足以真实表达 Beat；
- `TEMPORAL_HELPFUL`：静态位置已足够，动态可能增加体验价值；
- `TEMPORAL_REQUIRED`：核心是变化/过程，必须有 temporal Evidence 才能完整表达；静态只能支持可见状态或结果；
- `UNKNOWN`：现有 grounded facts 无法判断，不能自动偏向动态。

Requirement 只能引用已有 grounded facts，不能生成新事实、媒体偏好或用户可见文案。多个 ContentUnit 合并为 SAME Beat 时，core 必须是共同支持的展示贡献或已有明确代表关系，不能把 incidental facts 全部 union。找不到共同 core 时应回到 A1 relation conflict/unresolved，不得靠 Anchor 评分掩盖。

**案例：** 古建筑立面为 `STATIC_SUFFICIENT`；吹灭蜡烛动作/火焰变化为 `TEMPORAL_REQUIRED`。只有熄灭后静态帧时，只能支持结果，不能获得完整动作 representativeness。

### 8.4 AnchorCandidate

~~~text
AnchorCandidate
  anchor_candidate_ref
  selected_memory_ref
  beat_candidate_ref
  source_content_unit_ref
  raw_asset_ref
  evidence_window_ref
  evidence_refs[]
  anchor_kind
  actual_source_timepoint or supported_source_interval
  grounded_fact_refs[]
  support_level
  temporal_support_status
  quality_signal_refs[]
  limitation_refs[]
  semantic_anchor_eligible
  hq_source_handle
  hq_source_handle_status
~~~

### 8.5 硬资格

Anchor candidate 必须同时满足：

1. 当前 Revision、当前 selected Memory 与当前 Beat scope；
2. 来自 Beat 合法 CandidateContentUnit 与 Handoff 白名单；
3. Evidence role = KEEP；
4. 至少一个与 Beat 核心内容一致的 STRONG/MODERATE grounded fact；WEAK 只能辅助；
5. RawAsset、Window、Frame、source offset 与 extraction provenance 完整；
6. Evidence 抽取成功，位置与 Anchor 类型一致；
7. CONTEXT_ONLY/DROP、跨 Memory、白名单外或伪造 source position 均禁止。

同一合法 Evidence 可以进入多个 Beat 的 eligibility set，但必须分别有 grounded support，且 S10-C 不得把同一个 Frame/source interval 重复选择成多个最终媒体项。

### 8.6 长 Manual

同一长 Manual RawAsset 的不同合法 Window 可以产生多个 Anchor candidates，前提是上游已有不同且通过必要验证的 CandidateContentUnit；每个 Anchor 必须留在自己的 Window。是否允许同一长 Manual 最终贡献多个媒体项留到 S10-C。

任意 16s/73s Manual 的 Window 规划继续 OPEN；S10 只使用上游合法 Window，不在此处补定。

### 8.7 语义资格与 HQ readiness 分离

~~~text
semantic_anchor_eligible = true | false

hq_source_handle_status =
  AVAILABLE
  NOT_YET_MATERIALIZED
  UNAVAILABLE
  UNKNOWN
~~~

`NOT_YET_MATERIALIZED` 不等于不可用；`UNAVAILABLE/UNKNOWN` 也不得伪装可渲染。语义 Anchor 可保留审计，但发布资格、fallback 与 failure routing 留到 S10-C/D。

### 8.8 成本边界

A2.1 只使用已有 Evidence 与 provenance 建立合法集合；不调用新模型、不上传 Raw/HQ、不回取 Auto 另外两帧、不请求完整 9s 视频，也不提前决定媒体形式。

## 9. S10-A2.2｜Representative Evidence Evaluation 与 Shortlist

**状态：CONFIRMED**

S10 不使用可补偿一切的单一 `overall_score`。合法 Anchor candidates 依次经过 presentation usability、分维度评价、dominance pruning 与分层比较，形成每 Beat 1–3 个非重复候选；无法可靠截断时保留 uncertain frontier。

### 9.1 Presentation Usability Gate

文件损坏、核心内容不可见、主体完全遮挡、严重模糊至无法辨认、interval 缺少必要时序证据或 source mapping 不可靠时，不得进入 Representative Evidence shortlist。它仍留在事实与审计账本，不能被描述为“内容未发生”。

### 9.2 AnchorEvaluationCard

~~~text
AnchorEvaluationCard
  anchor_candidate_ref
  beat_anchor_requirement_ref
  grounding_support
  semantic_representativeness
  beat_centrality
  subject_clarity
  interpretation_ambiguity
  blur
  exposure
  occlusion
  corruption
  temporal_completeness
  stability
  motion_value
  hq_source_status
  limitation_refs[]
  signal_provenance[]
~~~

主要离散等级：

- semantic：`CORE_DIRECT | CORE_PARTIAL | PERIPHERAL`；
- centrality：`DECISIVE | CENTRAL | SUPPORTING`；
- temporal：`COMPLETE | PARTIAL | STATIC_ONLY | UNKNOWN | NOT_APPLICABLE`；
- stability：`STABLE | USABLE | UNSTABLE | UNKNOWN`；
- motion value：`ESSENTIAL | HELPFUL | NONE | UNKNOWN | NOT_APPLICABLE`。

Motion Amount 不等于 Motion Value。Manual/Auto 来源本身也不自动增加 truth、semantic 或 quality 等级。

### 9.3 Dominance 与分层比较

若一个候选在所有相关重要维度均不优于另一个候选，且至少一个维度更差、没有独立 temporal/render 价值，则为 dominated candidate，只保留 audit。

剩余候选按以下层级比较，不做加权求和：

~~~text
1 grounded core support
2 semantic representativeness
3 beat centrality
4 subject clarity / interpretation ambiguity
5 temporal completeness when applicable
6 technical usability
7 stability / motion value when applicable
8 stable deterministic tie-break
~~~

画质只能在候选都能真实代表 Beat 时提高优先级；不能让不表达核心内容的漂亮画面胜出。语义最中心但完全不可观看的候选也不能越过 usability gate。

### 9.4 Shortlist

~~~text
RepresentativeEvidenceShortlist
  beat_candidate_ref
  shortlisted_anchor_refs[]        # 1–3
  uncertain_frontier_refs[]
  presentation_unusable_refs[]
  dominance_decision_refs[]
  evaluation_card_refs[]
  shortlist_status
  deterministic_tie_break_trace
~~~

正常 shortlist 为 1–3 个非重复候选，不为凑满三个加入相似帧。1–3 是 V1 可校准 Baseline；若缺失/冲突信号可能改变前三或第一候选，不任意截断，相关项进入 uncertain frontier。

### 9.5 状态与 UNKNOWN

~~~text
SHORTLIST_READY
SHORTLIST_READY_WITH_TRADEOFFS
SHORTLIST_UNRESOLVED
~~~

所有缺失信号显式为 `UNKNOWN`，不能当 0、平均值或自动劣势。若 UNKNOWN 不可能改变结果可以继续；可能改变 shortlist membership 或主候选时必须 unresolved。

HQ readiness 与 representative preference 分开记录；`AVAILABLE` 不代表内容更好，`NOT_YET_MATERIALIZED` 也不代表内容更差。

### 9.6 案例

对“进入古镇”Beat，稍暗但完整显示牌坊与进入动作的候选，优先于清晰漂亮但只拍到旁边商店的候选。对“吹灭蜡烛”，可辨认且落在火焰变化核心位置的候选，优先于画质更高但只显示准备阶段的蛋糕；若核心候选已严重模糊至不可观看，则它不能越过 usability gate。

### 9.7 成本边界

A2.2 复用 grounded facts 与已有 quality/stability/motion signals；不调用新模型、不上传 HQ，每 Beat 正常只向下一步传递 1–3 个候选。

## 10. S10-A2.3｜Primary Anchor、Fallback 与失败合同

**状态：CONFIRMED / A2 CROSS-CHECK PASSED**

每个 Beat 输出 0 或 1 个 Primary EvidenceAnchor、0–2 个有序 Fallback Anchors 与一个明确 resolution state；不得同时存在两个 Primary。

### 10.1 两层选择

~~~text
Preferred Semantic Anchor
→ Source Readiness Guard
→ Final Primary EvidenceAnchor
~~~

先按 A2.2 选择最能代表 Beat 的语义优选；再检查 source 是否 `AVAILABLE` 或具有合法 handle 的 `NOT_YET_MATERIALIZED`。这样可以审计最终是否因 HQ readiness 使用了次优位置。

语义、中心位置和事实支持近似等价时，subject clarity、technical quality、source readiness、fallback failure-domain independence 与 stable ID 可依次作为后置比较。

### 10.2 Preferred 不可用

Preferred source 为 `UNAVAILABLE` 时，只能检查同 Beat 的下一候选。若它独立满足最低语义标准，可作为 Primary 并记录 `ANCHOR_RESOLVED_DEGRADED`；若替换会改变 Beat 含义，则不得使用。

Preferred source 为 `UNKNOWN` 时，若存在语义近似等价且明确可请求的候选，可使用后者；若替换有实质语义损失，则为 `ANCHOR_UNRESOLVED`。

### 10.3 Chapter 与 Aha floor

- Chapter 降级 Anchor 可以为 CORE_PARTIAL，但必须仍让用户理解该 Beat、不改变事实含义，并把限制传给 S11 Claim boundary。
- Aha 必须直接代表同一核心 peak；仅准备、结果、CORE_PARTIAL 或相邻漂亮画面不能替代。Aha Fallback 也必须直接代表同一 peak。

### 10.4 Fallback Anchors

每个 Primary 最多两个有序 Fallback。Fallback 必须来自同 Beat、独立满足合法性与语义 floor、不是 Primary 的无意义重复、source 为 `AVAILABLE` 或合法 `NOT_YET_MATERIALIZED`，并在 S10 中预先声明相对 Primary 的损失。

语义近似等价时，优先不同 RawAsset/source handle 以降低共同失败风险；不得为故障独立性牺牲真实性。没有合格 Fallback 时不补位。

Anchor Fallback 更换原素材位置；Media Fallback 保留 Anchor、改变 PHOTO/LIVE_2S/VIDEO_5S。二者必须分开，后者留给 S10-B/C。

### 10.5 Resolution states

~~~text
ANCHOR_RESOLVED
ANCHOR_RESOLVED_DEGRADED
ANCHOR_UNRESOLVED
NO_USABLE_ANCHOR
~~~

- `RESOLVED`：唯一 Primary 满足完整语义与 presentation floor，source 已可用或合法待请求；它不声明 HQ 已 materialize 或 render-ready。
- `RESOLVED_DEGRADED`：Preferred 无法成为 Primary，使用同 Beat 的较弱但仍真实候选，损失已记录。
- `UNRESOLVED`：关键 quality/readiness/关系未知或实质 tradeoff 无法安全决定。
- `NO_USABLE`：已经证明没有候选满足最低语义与呈现标准。

`NO_USABLE_ANCHOR` 至少区分：

~~~text
NO_ELIGIBLE_ANCHOR
ALL_PRESENTATION_UNUSABLE
ALL_SOURCE_UNAVAILABLE
AHA_CORE_PEAK_NOT_DIRECTLY_REPRESENTED
~~~

这些 reason 只说明本次 S10 attempt 没有可用展示位置，不能解释为事实未发生。

### 10.6 输出与不可变性

~~~text
AnchorResolution
  selected_memory_ref
  beat_candidate_ref
  preferred_semantic_anchor_candidate_ref
  primary_evidence_anchor_ref
  ordered_fallback_anchor_refs[]
  anchor_resolution_state
  semantic_floor_result
  degradation_reason_refs[]
  unresolved_reason_refs[]
  source_readiness_snapshot
  selection_trace
  policy_and_signal_versions
~~~

同一 S10 attempt 的 Primary/Fallback 决策不可原地改写。S13 后续失败时只能创建 `FallbackActivation`，记录 failed/activated refs 与 reason；新素材或新 Revision 产生新 S10 decision。

### 10.7 阶段边界

Beat Anchor 失败不在 A2.3 删除 Chapter/Aha。S10-C 再判断 Chapter 是否仍有足够媒体项；Aha 核心 Beat 无 Anchor 通常进入 media unresolved。A2.3 当时不决定 S10 是否可有界重入 S09；该下游问题现已由 C1.3 确认为“每 Revision 最多一次、只处理原 S10 batch 已证明媒体不足的批量 re-selection”。UNKNOWN、transient、contract invalid 或运行时新故障均不得使用该机会。

本项不调用模型、不上传 HQ、不搜索其他素材、不执行渲染、不更换 S09 membership。

## 11. S10-A2 Closeout

**状态：FROZEN BY CANONICAL V1.21**

A2.1–A2.3 已确认 Anchor eligibility、BeatAnchorRequirement、Representative Evidence evaluation/shortlist、唯一 Primary、同 Beat Fallback、source readiness 分离、resolution/no-usable states 与 immutable activation。内部 12-case cross-check 已通过，详见 `S10_A2_EVIDENCE_ANCHOR_INTERNAL_CROSS_CHECK_V0_1.md`。

下一阶段进入 S10-B：在 EvidenceAnchor 已确定后决定合法媒体格式与偏好，不反向改写 Anchor。

## 12. S10-B1｜Media Format Eligibility

**状态：CONFIRMED**

B1 只判断一个 resolved EvidenceAnchor 对 PHOTO/LIVE_2S/VIDEO_5S 是否具有格式资格，不决定最终格式、动态比例、Hero 或 3–5 媒体集合。

### 12.1 资格状态

~~~text
FORMAT_ELIGIBLE
FORMAT_CONDITIONAL
FORMAT_INELIGIBLE
FORMAT_UNRESOLVED
~~~

- `ELIGIBLE`：已有证据证明格式合法；
- `CONDITIONAL`：可计划，但最小 HQ 取回后必须通过确定性媒体检查，并预声明 Fallback；
- `INELIGIBLE`：已证明不满足；
- `UNRESOLVED`：关键信息缺失，不能当作合法。

### 12.2 类型矩阵

| Anchor kind | PHOTO | LIVE_2S | VIDEO_5S |
|---|---|---|---|
| STILL_ASSET | eligible | ineligible | ineligible |
| FRAME_TIMEPOINT from video | eligible | conditional/eligible under temporal rules | Chapter only and sufficient temporal support |
| EVIDENCE_SUPPORTED_INTERVAL | eligible when grounded focal timepoint exists | eligible when a valid 2s span exists | Chapter only when a supported 5s span exists |

Aha 继续禁止 VIDEO_5S。

### 12.3 PHOTO

PHOTO 需要合法 still、精确 video timepoint，或 interval 内明确的 grounded focal timepoint；画面通过 presentation usability，source 可用或合法待请求。禁止跨帧拼接、AI 补内容、无确定位置地从 interval 随机选帧，或默认把低分辨率 Evidence 当最终 HQ。

PHOTO 可以呈现 temporal Beat，但该动作/变化事实必须已经由 Anchor 背后的 temporal Evidence 支持；只有结果静态帧时，只能表达结果，不能继承完整过程 claim。

### 12.4 LIVE_2S

LIVE_2S 必须来自视频；一个 RawAsset 与合法 support scope 内存在包含 Primary Anchor 的连续 2s；source handle 为 `AVAILABLE` 或合法 `NOT_YET_MATERIALIZED`；无已知严重 corruption/occlusion/instability；动态至少可能增加内容价值。Aha interval 必须继续围绕同一 peak。

已有充分 temporal/stability 证据时为 `FORMAT_ELIGIBLE`。只有静态 Evidence、但 2s source span 可确定请求且没有负面信号时，V1 可为 `FORMAT_CONDITIONAL`，前提是预声明同 Anchor PHOTO Fallback，并由 S13 取回后执行 decode/stability/content-consistency 检查；失败不再搜索素材。

### 12.5 VIDEO_5S

VIDEO_5S 仅 Chapter；必须来自一个视频 RawAsset，有包含 Anchor、完全位于合法 support scope 的连续 5s；已有 temporal Evidence 支持完整短过程；motion value 为 HELPFUL/ESSENTIAL；temporal completeness 与 stability 可用。

V1 不允许仅凭静态帧把 VIDEO_5S 标为 conditional 后盲取素材。缺少充分时序证据时为 `FORMAT_INELIGIBLE` 或 `FORMAT_UNRESOLVED`。

### 12.6 区间边界

动态 interval 不必以 Anchor 对称，但必须包含 Anchor、位于 source bounds 和合法 Evidence/support Window；靠近边缘时只允许在合法范围内平移。禁止黑帧 padding、loop、变速凑时长、AI interpolation 或跨 Window/Beat/RawAsset 拼接。

**案例：** 9s Auto 的 Anchor 在 0.4s 时，LIVE 可用 `[0,2]`，不得请求负时间；Anchor 在 8.7s 时可用 `[7,9]`。73s Manual 的拉坯 Anchor 若位于 20–32s Window，5s interval 不得跨入 32s 后的展示作品 Window。16s/73s Window 规划继续 OPEN。

### 12.7 Motion 边界

Motion Amount 不等于 Motion Value。古建筑拍摄晃动很多仍可只用 PHOTO；孩子稳定地跑向家人可能 motion amount 不高但 motion value 高。B1 不因动态更吸引人而修改 Anchor、Beat 或 Memory。

### 12.8 输出

~~~text
MediaFormatEligibility
  evidence_anchor_ref
  beat_anchor_requirement_ref
  memory_type
  photo_status / reason_refs[]
  live_2s_status / reason_refs[]
  video_5s_status / reason_refs[]
  allowed_source_span
  required_post_fetch_validation[]
  required_media_fallback_refs[]
  source_readiness_snapshot
  policy_version
~~~

B1 不请求 HQ、不渲染、不决定最终格式、动态比例、Hero 或最终媒体集合。

## 13. S10-B2｜Preferred Media Format Decision

**状态：CONFIRMED**

B2 在 B1 已证明合法的格式中，为同一个 EvidenceAnchor 选择最适合表达该 Beat 的首选媒体形式。核心原则是：

> 选择能够完整、真实表达 Beat 的最简单格式；只有动态内容带来实质增量价值时，才从 PHOTO 升级为 LIVE_2S 或 VIDEO_5S。

它不设置“每个 Chapter 至少一个动态素材”或“全天至少几个 Live/Video”的配额。最终结果全部为 PHOTO 可以成立，只要 PHOTO 已经充分表达内容；动态也不能仅为了版式丰富而入选。

### 13.1 Dynamic Incremental Value

`Dynamic Incremental Value` 指相对于同一 Anchor 的 PHOTO，连续时间信息额外带来的内容或体验价值：

~~~text
NONE
MINOR
MATERIAL
ESSENTIAL
UNKNOWN
~~~

- `NONE`：动态没有增加用户可辨认的新信息或体验；
- `MINOR`：有轻微变化，但不值得增加取回、验证、存储与播放复杂度；
- `MATERIAL`：动态明显改善对内容或现场感的理解；
- `ESSENTIAL`：缺少动态会失去 Beat 的核心变化、动作或峰值；
- `UNKNOWN`：现有 Evidence 不足以可靠判断，不能假定动态更好。

增量价值可以来自两类证据：

1. `semantic gain`：动作方向、状态变化、先后关系、短过程或结果出现；
2. `experiential gain`：即使静态已经说明事实，连续运动仍显著保留现场体验，例如海浪推进、孩子跑向家人、烛火被吹灭。

摄像头晃动、画面位移或运动量大不等于动态价值高。

### 13.2 格式选择规则

#### PHOTO

当 PHOTO 已经完整、真实、清楚地表达 Beat，且动态增量为 `NONE` 或 `MINOR` 时，选择 PHOTO。

**案例：** 古建筑立面的纹样已经在一帧中清晰完整。镜头前后只有轻微手抖，没有新的动作、关系或体验价值，因此选择 PHOTO。

#### LIVE_2S

当连续 2 秒能够带来 `MATERIAL` 或 `ESSENTIAL` 的微动作、状态变化或现场体验，而延长到 5 秒不再产生实质增量时，选择 LIVE_2S。

**案例：** 孩子转身挥手的动作在 2 秒内完整发生；PHOTO 只能保留一个姿态，LIVE_2S 能清楚表达互动，5 秒则只增加动作前后的等待，因此选择 LIVE_2S。

#### VIDEO_5S

VIDEO_5S 仅可用于 Chapter。当 2 秒会实质截断一个有价值的短过程，而 5 秒能够更完整地表达其起点、推进和结果，并产生 `MATERIAL` 或 `ESSENTIAL` 增量时，选择 VIDEO_5S。

**案例：** 陶艺拉坯从双手扶稳、器形抬升到短暂成形需要约 4 秒。PHOTO 丢失过程，LIVE_2S 截断关键推进，合法且稳定的 5 秒可以完整表达，因此选择 VIDEO_5S。

若 LIVE_2S 与 VIDEO_5S 都足以表达核心，则选择更短的 LIVE_2S。

### 13.3 Evidence requirement 不等于用户可见格式

`TEMPORAL_REQUIRED` 表示算法必须依靠时序 Evidence 才能证明某个变化或过程真实发生，不代表最终一定要向用户展示动态媒体。

**案例：** 时序 Evidence 已证明蜡烛从点燃到熄灭。如果最终 PHOTO 精确落在吹灭发生的决定性瞬间，并足以真实呈现这个 Aha，仍可选择 PHOTO；证明事实所需的证据形式与最终呈现形式必须分开。

### 13.4 UNKNOWN 与条件格式

1. PHOTO 已充分表达核心，而动态增量为 `UNKNOWN`：选择 PHOTO，不为探索动态而增加 HQ 请求。
2. PHOTO 不足以表达核心，而动态增量或合法性仍为 `UNKNOWN`：输出 unresolved，不把未知当作动态可用。
3. B1 的 `FORMAT_CONDITIONAL` LIVE_2S 只有同时满足以下条件时才可成为 preferred format：
   - 预期动态增量至少为 `MATERIAL`；
   - 能预先规划同一 RawAsset 内的确定 2 秒区间；
   - 已声明同 Anchor 的 PHOTO Fallback；
   - 已声明 S13 取回后的 decode、stability 与 content-consistency 检查。

### 13.5 降级边界

理想动态格式不可用时，只有较低格式仍能真实表达同一核心内容，才允许降级：

- Chapter 可以记录有限的表达损失后降为较短动态或 PHOTO；
- Aha 若降级后无法直接呈现同一核心 peak，则不得降级为相邻、准备或结果画面；
- 不得通过改变 Anchor、Beat 含义或事实 claim 来伪造格式可用。

这里仅决定允许的格式方向；具体区间、Media Fallback 顺序与 Anchor Fallback 的协同留到 B3。

### 13.6 决策顺序

B2 不使用单一加权总分。对每个 EvidenceAnchor 依次判断：

~~~text
1 format legality
2 core expression floor
3 material dynamic incremental value
4 shortest sufficient format
5 stability / failure risk
6 lower relative resource class when near-equivalent
7 stable deterministic tie-break
~~~

资源等级目前只作相对判断：通常 `PHOTO < LIVE_2S < VIDEO_5S`。实际上传字节、云端调用、存储与播放成本尚未冻结为固定数字，不得伪造精确成本。

### 13.7 Resolution states

~~~text
MEDIA_FORMAT_RESOLVED
MEDIA_FORMAT_RESOLVED_CONDITIONAL
MEDIA_FORMAT_RESOLVED_DEGRADED
MEDIA_FORMAT_UNRESOLVED
NO_ELIGIBLE_MEDIA_FORMAT
~~~

- `RESOLVED`：首选格式已经合法且充分；
- `RESOLVED_CONDITIONAL`：仅在预声明取回后检查和 Fallback 的条件下成立；
- `RESOLVED_DEGRADED`：理想格式不可用，使用仍真实但有明确表达损失的格式；
- `UNRESOLVED`：关键信息未知，可能改变格式决定；
- `NO_ELIGIBLE`：已经证明没有格式能够满足该 Beat 的最低表达要求。

### 13.8 输出

~~~text
PreferredMediaFormatDecision
  evidence_anchor_ref
  media_format_eligibility_ref
  photo_expression_sufficiency
  live_2s_incremental_value
  video_5s_incremental_value
  preferred_format
  required_fallback_format
  format_resolution_state
  semantic_gain_refs[]
  experiential_gain_refs[]
  degradation_refs[]
  unresolved_reason_refs[]
  relative_resource_class
  policy_and_signal_versions
  decision_trace
~~~

### 13.9 阶段边界

B2 不决定：

- 每个 Chapter 最终选择哪 3–5 个媒体项；
- 动态素材数量或比例；
- Hero、叙事顺序或版式；
- LIVE_2S / VIDEO_5S 的精确起止区间；
- HQ source 请求与渲染；
- S10 失败后是否有界重入 S09。

## 14. S10-B3.1｜Exact Media Source Plan

**状态：CONFIRMED**

B3.1 把 B2 的首选媒体格式转换成一个可执行、可追溯的精确源位置计划。核心原则是：

> 先保证 Beat 的核心语义和必要动作阶段完整，再决定区间位置；“以 Anchor 为中心截取”只是在没有更多语义依据时的确定性兜底。

本项只计算时间点与时间区间，不请求、上传、下载或渲染 HQ source。

### 14.1 两个范围概念

`AllowedSourceSpan` 是允许取材的最大合法范围，为以下范围的交集：

~~~text
RawAsset source bounds
∩ upstream validated Evidence / Window scope
∩ S09 source allowlist scope
∩ current Beat support scope
~~~

原视频更长不代表范围外内容已经得到支持，不能为凑够时长向未知区域扩张。

`RequiredSemanticLandmarks` 是最终媒体必须保留的关键时间位置或动作阶段，例如动作起点、变化 peak、结果出现。它只来自已有 temporal Evidence 与 grounded facts，不由 S10 想象新阶段。

不是整个 supporting Evidence interval 的每一秒都必须进入媒体；只有表达 Beat 核心所必需的 landmarks 必须保留。

### 14.2 三种精确计划

#### PHOTO

- `STILL_ASSET`：使用该照片本身，不伪造视频时间点；
- `FRAME_TIMEPOINT`：使用实际 source/decode timestamp；
- `EVIDENCE_SUPPORTED_INTERVAL`：必须选择区间内已 grounded 的 focal timepoint，不能重新搜索“更漂亮的一帧”。

#### LIVE_2S

规划同一 RawAsset 内名义长度为 2 秒的连续 source interval：

- 对 `FRAME_TIMEPOINT` Anchor，interval 必须包含该 timepoint；
- 对 `EVIDENCE_SUPPORTED_INTERVAL` Anchor，interval 必须位于 supported interval 内，并包含该格式要求的 semantic landmarks；
- 不要求把一个长于 2 秒的 supporting interval 全部塞入 LIVE，只要求必要核心不丢失。

#### VIDEO_5S

规划同一 RawAsset 内名义长度为 5 秒的连续 source interval；仅 Chapter 可用。它必须容纳 B2 判定为 VIDEO_5S 所必需的短过程和 semantic landmarks。

算法合同固定名义 2 秒与 5 秒；帧率、编码 timebase 造成的毫秒级渲染容差留给 S13 工程合同，不能在 S10 伪造精度。

### 14.3 区间选择顺序

存在多个合法计划时按以下顺序比较，不做加权求和：

~~~text
1 contains Anchor timepoint or required focal landmark
2 contains every required semantic landmark
3 remains inside AllowedSourceSpan
4 avoids adjacent unrelated/boundary content
5 improves temporal completeness
6 improves stability, clarity and technical usability
7 centered or boundary-shifted deterministic placement
8 stable deterministic tie-break
~~~

第 7 项中的 boundary-shift 指 Anchor 靠近视频开头或结尾时，把完整区间向合法方向平移。例如 9 秒视频内 Anchor 为 `0.4s`，LIVE 使用 `[0,2]`；Anchor 为 `8.7s`，使用 `[7,9]`。禁止负时间、黑帧补齐或循环。

### 14.4 无合法区间

出现以下情况时不得强行生成计划：

1. `AllowedSourceSpan` 小于目标格式所需的连续 2 秒或 5 秒；
2. 必要 semantic landmarks 无法同时放入目标时长；
3. 只能通过跨 Window、Beat、RawAsset 或白名单边界完成；
4. 只能通过截掉核心阶段、变速、loop、padding、AI interpolation 或拼接完成；
5. 关键 source bounds、timestamp 或支持范围未知，且未知会改变区间合法性。

已证明不可能时为 `MEDIA_SOURCE_PLAN_INFEASIBLE`；关键信息仍未知时为 `MEDIA_SOURCE_PLAN_UNRESOLVED`。两者不能混用。

如果 B2 的 preferred format 因此不可执行，只能进入 B3.2 预声明的 Fallback；不能在附近继续搜索或静默扩大 Evidence 范围。

### 14.5 Conditional LIVE 一次性计划

B1/B2 允许的 Conditional LIVE 必须在 HQ 取回前生成唯一 provisional 2 秒区间：

- 有动作方向或 landmark 证据时按语义规划；
- 只有单一 timepoint 时先居中，再在 source 边缘合法平移；
- S13 只验证该预声明区间的 decode、stability 与 content consistency；
- 失败后不滑动区间、不连续试取、不补要 Auto 其他 Evidence Frames，直接激活预声明 Fallback。

### 14.6 案例

1. 9 秒 Auto 的 Anchor 在 `0.4s`：LIVE 取 `[0,2]`；Anchor 在 `8.7s`：取 `[7,9]`。
2. 吹蜡烛变化发生在 `18.2–19.4s`，合法范围为 `17.8–20.4s`：LIVE 可取 `[18,20]`，不必机械地把 peak 放在正中心。
3. 拉坯关键过程为 `22.4–26.3s`，合法 Window 为 `20–32s`：VIDEO 可取 `[22,27]`，使开始、推进和短暂成形均保留。
4. 原视频仍有内容，但现有支持范围只有连续 1.4 秒：LIVE_2S 不可执行，不能向两侧未知内容扩张。
5. 一个 Beat 的全部必要阶段至少横跨 7 秒：VIDEO_5S 不得截核心、加速或拼接。若其他格式仍满足核心，进入 Fallback；否则 media unresolved。
6. Conditional LIVE 只有 `4.5s` 静态 Anchor，合法范围为 `0–9s`，且无其他方向证据：唯一 provisional plan 为 `[3.5,5.5]`；取回失败后不尝试 `[3,5]`、`[4,6]` 等其他区间。

### 14.7 输出与状态

~~~text
ExactMediaSourcePlan
  evidence_anchor_ref
  preferred_media_format_decision_ref
  source_raw_asset_ref
  allowed_source_span
  required_semantic_landmark_refs[]
  requested_still_ref or requested_timepoint or requested_interval
  interval_duration
  source_plan_state
  conditional_validation_requirements[]
  infeasible_reason_refs[]
  unresolved_reason_refs[]
  policy_and_signal_versions
  planning_trace

source_plan_state =
  MEDIA_SOURCE_PLAN_RESOLVED
  | MEDIA_SOURCE_PLAN_CONDITIONAL
  | MEDIA_SOURCE_PLAN_INFEASIBLE
  | MEDIA_SOURCE_PLAN_UNRESOLVED
~~~

同一 S10 attempt 的 plan 不得被 S13 原地滑动或改写；失败激活必须产生新记录。

### 14.8 成本与阶段边界

B3.1 只处理 refs、timestamps、合法范围和已有质量信号，不新增模型调用或媒体传输。可以为 S10-C 的候选 Beat 先建立低成本计划；只有 S10-C 最终选中的媒体项才进入 S10-D/S13 的最小 HQ 请求路径。

B3.1 不决定 3–5 set、Hero、顺序、动态数量、Fallback 执行顺序或 S09 re-entry。

## 15. S10-B3.2｜Fallback Route 与 Failure Routing

**状态：CONFIRMED**

B3.2 不规定“永远先降成 PHOTO”或“永远先换 Anchor”。它先判断终止性失败影响哪一层，再从 S10 已预声明的有限路线中激活第一个仍然合法且最能保留原意的方案。

### 15.1 三个对象

- `Media Fallback`：EvidenceAnchor 不变，只改变 PHOTO/LIVE_2S/VIDEO_5S 格式；
- `Anchor Fallback`：仍表达同一 Beat，但改用 A2 已预声明的另一个 EvidenceAnchor；
- `Fallback Route`：一个完整、可执行的 `Anchor + media format + ExactMediaSourcePlan` 组合。

运行时只激活预声明 Route，不重新选择 Anchor、重新规划区间或搜索其他素材。

### 15.2 失败分层

1. `TRANSIENT_DELIVERY_OR_RENDER_FAILURE`：临时网络、服务或渲染错误。由 S13 执行其有界重试合同；尚未被声明为 terminal 时不得激活算法 Fallback。
2. `FORMAT_TERMINAL_FAILURE`：当前动态区间无法通过 decode、stability、content consistency 或格式渲染检查，但 Anchor 的 grounded focal position 仍有效。只使当前 Route/format plan 失效。若只是 Anchor 周围的动态内容与预期不符、而 focal frame 仍真实表达核心，也属于本层。
3. `ANCHOR_TERMINAL_FAILURE`：Anchor 映射错误、focal core 本身不可见、语义验证推翻 Anchor 或 provenance 无法成立。该 Anchor 的全部媒体格式失效。不能把“动态周边失败”误升级为 Anchor 失败，也不能把“Anchor 本身错误”降格为格式失败。
4. `SOURCE_TERMINAL_FAILURE`：RawAsset/source handle 丢失、损坏或确定不可访问。所有引用同一 source failure domain 的 Route 失效。
5. `POLICY_OR_LEGALITY_FAILURE`：来源越出白名单、权限或合法 scope。所有受影响 Route 禁止使用；不得通过格式降级绕过。
6. `SOURCE_PLAN_INFEASIBLE_OR_UNRESOLVED`：在 S10 已发现精确计划不可执行或关键合法性未知。该 Route 不得进入 executable primary/fallback list。

“terminal”只表示对应层已完成规定检查或重试、不能继续执行，不表示 Beat 事实没有发生。

### 15.3 路线数量上限

V1 每个 Beat 最多保存：

~~~text
1 Primary Route
+ up to 2 ordered Fallback Routes
= at most 3 executable routes
~~~

两条 Fallback 是 Media 与 Anchor Fallback 合计总数，不是每个 Anchor 各有两条。A2 可以继续保留最多两个 Fallback Anchors 作为语义与审计候选，但 B3.2 最多将其中必要部分转成两条 executable fallback routes。

Conditional LIVE 要求的同 Anchor PHOTO Fallback 占用一个 Fallback Route；仍可保留一个不同 Anchor/RawAsset 的容灾 Route。找不到合法 Fallback 时如实记录，不为凑满数量加入弱路线。

### 15.4 预排序原则

Route 在 S10 构建时按以下层级预排序，不在失败发生后重新评分：

~~~text
1 same Beat and legal scope
2 same Aha core peak when memory_type = AHA
3 full core preservation over presentation degradation
4 lower semantic/presentation loss
5 same Anchor over Anchor change when meaning is equivalent
6 failure-domain independence when meaning remains equivalent
7 lower resource/risk class when near-equivalent
8 stable deterministic tie-break
~~~

所以同 Anchor PHOTO 通常优先，但不是绝对规则。如果 PHOTO 会失去关键动作，而另一个 Fallback Anchor 的动态媒体能够完整保留同一核心，则后者排在前面。

### 15.5 激活算法

S13 报告 terminal failure 后：

~~~text
identify failure scope
→ invalidate every route inside that scope
→ scan preordered fallback routes
→ activate first still-valid route
→ otherwise report fallback exhausted
~~~

- format failure 只淘汰当前格式/区间 Route；
- anchor failure 跳过同 Anchor 的全部 Route；
- source failure 跳过同 RawAsset/source handle failure domain 的全部 Route；
- policy/legality failure 跳过全部受影响来源。

不得因为一条 Route 失败而重新排列未受影响 Route，也不得动态生成第四条路线。

### 15.6 Chapter、Aha 与 claim compatibility

- Chapter Fallback 可以有明确的 presentation loss，但必须仍达到 A2 的最低 Beat 可理解标准，且不改变事实核心；
- Aha 的每一条 Route 都必须直接表达同一 peak，不允许准备、事后结果或邻近漂亮画面替代；
- Fallback 对下游 claim 的影响记录为：

~~~text
FULLY_COMPATIBLE
PRESENTATION_NARROWING
INCOMPATIBLE
~~~

`INCOMPATIBLE` Route 不得进入 fallback list。`PRESENTATION_NARROWING` 必须把限制传给后续 S10-D/S11/S12 readiness 与表达边界；具体跨阶段激活时机留到 S10-D 集成合同决定。

### 15.7 案例

1. 古建筑 LIVE 过度晃动，但同 Anchor Frame 清晰完整：`FORMAT_TERMINAL_FAILURE`，激活同 Anchor PHOTO。
2. 孩子跑向家人的 LIVE 失败；同 Anchor PHOTO 只显示跑到一半，另一个 Fallback Anchor 的 LIVE 完整记录抵达：备用 Anchor LIVE 的语义损失更低，应排在 PHOTO 前。
3. Primary RawAsset 已损坏：`SOURCE_TERMINAL_FAILURE`，同一文件的 PHOTO/LIVE/VIDEO Route 全部跳过，激活不同 RawAsset 的 Fallback Anchor。
4. 吹蜡烛 Aha 的 LIVE 失败；同 Anchor PHOTO 精确呈现吹灭 peak 时可回退。若 PHOTO 只有熄灭后的结果，且没有其他直接 peak Anchor，则 fallback exhausted、Aha media unresolved。
5. 一次网络超时仍属 transient：S13 先执行规定的有限重试，不立即把动态降为 PHOTO。
6. Anchor timestamp/provenance 被证明映射错误：该 Anchor 的所有格式均失效，不能因为其中一帧“看起来不错”继续使用。

### 15.8 FallbackRoute 与 Activation

~~~text
FallbackRoute
  fallback_route_ref
  beat_candidate_ref
  evidence_anchor_ref
  media_format
  exact_media_source_plan_ref
  route_order
  change_kind_from_primary =
    FORMAT_ONLY
    | ANCHOR_ONLY
    | ANCHOR_AND_FORMAT
  semantic_preservation
  claim_compatibility
  failure_domain_refs[]
  route_resolution_state
  limitation_refs[]

FallbackActivation
  fallback_activation_ref
  s10_attempt_ref
  failed_route_ref
  terminal_failure_scope
  terminal_failure_reason_ref
  invalidated_route_refs[]
  activated_route_ref
  change_kind
  semantic_or_presentation_loss
  activation_trace
~~~

Primary/Fallback Route order与旧 decision 不得被原地改写。每次 terminal failure 与 activation 都创建新记录；同一 attempt 最多按预声明顺序走完三条 Route。

### 15.9 成本与边界

路线预声明仍是轻量元数据工作；B3.2 不决定是否预取 Fallback HQ source，实际请求时机留到 S10-D。三条 Route 上限限制了最坏尝试次数、请求组合和审计复杂度。

B3.2 不重新搜索 Memory/全天、不改变 Beat/Memory membership、不决定最终 3–5 set、Hero、排序、S13 重试次数或 S09 re-entry。

## 16. S10-B3.3｜Unified MediaDecision 与 S10-C Handoff

**状态：CONFIRMED**

`MediaDecision` 是一个 Content Beat 交给 S10-C 的完整媒体候选包：

~~~text
Content Beat
+ AnchorResolution
+ PreferredMediaFormatDecision
+ Primary ExactMediaSourcePlan
+ up to 2 Fallback Routes
= exactly 1 MediaDecision candidate
~~~

### 16.1 已知失败与运行时失败分离

S10 当前已经知道不可执行的 Route，不能继续作为 Primary、等到 S13 再失败：

1. preferred Route 可执行：成为 Primary；
2. preferred Route 已确定不可执行，下一条 Route 仍达到 semantic floor：下一条直接成为 Primary，并记录 degraded 与原 preferred trace；
3. 关键信息未知且可能改变 Anchor、格式或区间：`MEDIA_DECISION_UNRESOLVED`；
4. 所有 Route 均已证明不可用：`NO_USABLE_MEDIA_DECISION`。

运行时 Fallback 只处理 S10 决策时尚未发生、由 S13 后续确认的 terminal failure。

最终 executable list 必须按以下顺序构建：

~~~text
build preferred route candidate
→ evaluate all known legality/plan states
→ exclude known infeasible routes
→ if UNKNOWN can change actual Primary, stop as decision unresolved
→ otherwise quarantine unresolved fallback-only candidates with limitation
→ choose actual Primary
→ rebase remaining fallback order and change_kind against actual Primary
→ retain original preferred trace and degradation reason
~~~

因此，一个已被提升为实际 Primary 的旧 fallback 不再以 fallback 身份保留；其余 Route 的 `change_kind_from_primary` 必须相对新的实际 Primary 重新计算。该重建发生在 MediaDecision 首次定稿前，不属于运行时改写。

**案例：** 已知一个拉坯 VIDEO_5S 无法容纳全部必要阶段，但 PHOTO 仍真实表达成形结果时，PHOTO 在 S10 直接成为 degraded Primary；不能把已知不可执行的 VIDEO 交给 S13。

### 16.2 MediaDecision states

~~~text
MEDIA_DECISION_RESOLVED
MEDIA_DECISION_RESOLVED_CONDITIONAL
MEDIA_DECISION_RESOLVED_DEGRADED
MEDIA_DECISION_UNRESOLVED
NO_USABLE_MEDIA_DECISION
MEDIA_DECISION_INPUT_INVALID
~~~

- `RESOLVED`：唯一 Primary 的 Anchor、格式与精确源计划均合法确定；
- `RESOLVED_CONDITIONAL`：Primary 需取回后验证，但已具备同核心、非条件的 executable Fallback；
- `RESOLVED_DEGRADED`：理想 Route 不可用，当前 Primary 仍真实可用且损失明确；
- `UNRESOLVED`：关键 UNKNOWN 可能改变实际媒体决策；
- `NO_USABLE`：已证明没有 Route 满足最低要求；
- `INPUT_INVALID`：Memory/Revision/Beat/白名单/provenance/version 等合同不一致。

`RESOLVED` 不表示 HQ 已经 materialize 或 render-ready，只表示当前媒体计划可合法执行。

### 16.3 Conditional 的安全条件

Conditional Primary 只有同时满足以下条件，才可成为 `MEDIA_DECISION_RESOLVED_CONDITIONAL`：

1. Primary 有唯一 provisional ExactMediaSourcePlan；
2. 取回后 deterministic validation 已声明；
3. 至少一条 ordered Fallback Route 在 S10 层已经 resolved、非 conditional，并独立达到同一 semantic floor；
4. Fallback 不改变 Beat 事实含义；
5. Conditional 失败影响的 scope 不会同时自动淘汰该格式 Fallback；source-level 共同失败风险必须另行披露。

条件不满足时为 `MEDIA_DECISION_UNRESOLVED`，不能以“可能可用”计入 S10-C。

这里的“非 conditional Fallback”只表示它不依赖额外的动态 content/stability 验证，不表示 HQ source 已经下载成功。其 source 仍可能为合法的 `NOT_YET_MATERIALIZED`，并继续携带 source-level 风险。

`fallback_coverage` 必须使用明确等级，不能只写一个模糊布尔值：

~~~text
NO_FALLBACK_COVERAGE
FORMAT_FAILURE_COVERED
ANCHOR_FAILURE_COVERED
SOURCE_FAILURE_COVERED
MIXED_FAILURE_COVERAGE
~~~

只有至少一条 Fallback 位于不同 source failure domain，才可声明 `SOURCE_FAILURE_COVERED`；同一 RawAsset 的另一个 timepoint 或格式不能提供 source-level coverage。

### 16.4 S10-C 数量记账

1. 一个 `MediaDecision` 最多贡献一个最终媒体项；
2. Primary 与最多两个 Fallback 合计仍只算一个，不增加内容丰富度；
3. `RESOLVED`、安全的 `RESOLVED_CONDITIONAL` 与达到最低标准的 `RESOLVED_DEGRADED` 可以作为一个 selectable candidate 交给 S10-C；
4. `UNRESOLVED`、`NO_USABLE`、`INPUT_INVALID` 不计入 selectable candidate 数量；
5. 一个 `UNRESOLVED_ALTERNATIVES` group 的多个 MediaDecision 最终最多选择一个；
6. 多个 MediaDecision 的 Primary 若指向相同 Frame、still 或实质相同 source interval，属于 `PRIMARY_PRIMARY_COLLISION`，S10-C 最多选择一个；
7. `PRIMARY_FALLBACK_COLLISION` 或 `FALLBACK_FALLBACK_COLLISION` 不提前制造第二个媒体项，也不自动证明两个 Beat 不可共同选择，但必须作为 failure-time activation conflict 传给 S10-C/D；最终有效 Route 仍不得产生重复媒体；
8. collision 判断使用 canonical render identity，而不只比较不同层的 ref 字符串。

**案例：** 五个古镇 Beat 的状态依次为 resolved、resolved-with-two-fallbacks、resolved-conditional、resolved-degraded、no-usable，交给 S10-C 的 selectable candidates 为四个，不是七个或五个。

### 16.5 S10-C 权限边界

S10-C 选择整个 MediaDecision，不得：

- 为了动态比例、Hero 或版式主动激活 Fallback；
- 把 Primary LIVE 改成 PHOTO 来平衡媒体组合；
- 从同一个 Beat 同时选择 Primary 与 Fallback；
- 修改 ExactMediaSourcePlan；
- 为凑够 3–5 项恢复 unresolved/no-usable Route；
- 把 Fallback Route 当作新的 Beat 或新的内容多样性。

Fallback 只由对应 terminal failure 激活。

### 16.6 MediaDecision

~~~text
MediaDecision
  media_decision_ref
  s10_attempt_ref
  selected_memory_ref
  revision_ref
  memory_type
  beat_candidate_ref

  anchor_resolution_ref
  preferred_media_format_decision_ref
  preferred_route_candidate_ref
  primary_route_ref
  ordered_fallback_route_refs[]       # 0–2

  media_decision_state
  s10c_counting_status
  semantic_floor_result
  claim_compatibility
  fallback_coverage
  route_collision_matrix_ref

  conditional_validation_requirements[]
  degradation_refs[]
  limitation_refs[]
  unresolved_reason_refs[]
  no_usable_reason_refs[]

  source_readiness_snapshot
  policy_and_signal_versions
  construction_trace
~~~

`preferred_route_candidate_ref` 保留理想 Route；`primary_route_ref` 是当前实际可执行的初始 Route。若二者不同，必须解释已知降级原因。

后续 activation 不改写 `primary_route_ref`。当前有效 Route 由 Primary 加不可变 `FallbackActivation[]` 推导，而不是覆盖旧记录。

### 16.7 MediaDecisionInventory

每个已选 Memory 输出一个面向 S10-C 的总账：

~~~text
MediaDecisionInventory
  selected_memory_ref
  revision_ref
  media_decision_refs[]
  s10c_selectable_refs[]
  unresolved_refs[]
  no_usable_refs[]
  input_invalid_refs[]
  unresolved_alternative_group_refs[]
  known_primary_render_collision_groups[]
  known_activation_collision_groups[]
  failure_time_coverage_limitations[]
  inventory_status
  construction_audit
~~~

Inventory 列出候选和冲突，不在 B3.3 选择最终 3–5 项。最终 distinct selectable capacity 由 S10-C 在 unresolved group、render collision 与其他 set constraints 下计算，不能直接把 `s10c_selectable_refs` 数量当最终容量。

`route_collision_matrix_ref` 至少区分 `PRIMARY_PRIMARY`、`PRIMARY_FALLBACK` 与 `FALLBACK_FALLBACK`。前者是 S10-C co-selection hard conflict；后两者是 activation-time conflict，S10-D 必须定义 deterministic resolution/failure rule，不能等冲突发生后临时保留两个重复媒体。

### 16.8 Invariants

1. 每个合法 Beat 恰好产生一个 MediaDecision，或产生显式 input-invalid 记录；不能静默消失；
2. resolved 状态恰好一个 Primary，Fallback 为 0–2；
3. Primary 与所有 Fallback 均须在同一 Memory/Beat 合法 scope；
4. Aha 所有 Route 直接表达同一 core peak；
5. known infeasible/unresolved Route 不得进入 executable list；
6. Conditional resolved 必须有非条件同核心 Fallback；
7. 任一 Route 的 `claim_compatibility=INCOMPATIBLE` 时不得进入 Primary/Fallback；
8. 同一 attempt 的 decision、Route order 与 source plan 不得原地改写；
9. fallback count 不增加 S10-C 内容数量或多样性；
10. 版本、Revision 或白名单不一致时 fail closed 为 input invalid；
11. Primary/全部 Fallback Route 间的 canonical render identity collision 必须在 handoff 前显式记账。

### 16.9 成本与边界

B3.3 只组合已存在的结构化 refs、状态与审计信息，不新增模型调用、媒体上传、HQ 取回或渲染。

B3.3 当时不决定 Aha supporting item、Chapter 最终 set、Hero、排序、同一长 Manual 最终贡献数或 S09 重入。它们现已由后续阶段分别确认：Aha 恰好一个用户可见媒体项；Chapter 为严格 Compact 2 或 Standard 3–5；Hero、时间顺序与同源占位见 C；每 Revision 最多一次的 proven-insufficiency 批量重选见 C1.3。B3.3 本身仍不得提前改变这些下游结果。

## 17. S10-B Closeout

**状态：FROZEN BY CANONICAL V1.21**

S10-B1–B3.3 已确认格式合法性、最小充分媒体选择、精确源位置、失败分层、最多三条执行路线、不可变 Fallback activation，以及 MediaDecision/S10-C handoff。内部案例检查发现并修正 final Route rebasing、failure scope、fallback coverage、route collision、non-conditional 释义与 fallback-only UNKNOWN 六项接口缺口，详见 `S10_B_MEDIA_DECISION_INTERNAL_CROSS_CHECK_V0_1.md`。

S10-B 已随 A/C/D 通过 S10-E 综合交叉检查，并由 Canonical V1.21 冻结。

## 18. S10-C1.1｜Chapter Media Capacity 与 Compact Chapter 产品例外

**状态：CONFIRMED**

S10-C1 先计算一个已选 Chapter 实际拥有多少个互不重复、可安全选择的媒体候选，再进入集合编辑。它不把 `s10c_selectable_refs` 的原始数量直接当成容量。

### 18.1 Proven Distinct Media Capacity

~~~text
selectable MediaDecision refs
− unresolved alternative over-count
− PRIMARY_PRIMARY canonical render collisions
− other hard co-selection conflicts
= proven distinct media capacity
~~~

Primary 与 Fallback 合计仍只贡献一个候选。Conditional MediaDecision 只有满足 B3.3 的安全 Fallback 合同时才能计入。容量表示最多有多少个已证明可共同选择的不同媒体项，不表示 S10-C 必须全部使用。

### 18.2 已确认的数量方向

~~~text
capacity >= 3
→ STANDARD_CHAPTER_CANDIDATE
→ S10-C2 从中选择最终 3–5 项

capacity = 2
→ COMPACT_CHAPTER_CANDIDATE
→ 必须再通过 C1.2 的双素材质量与叙事门

capacity = 0 or 1
→ INSUFFICIENT_CHAPTER_MEDIA
→ 不发布为单素材 Chapter，不自动改成 Aha
~~~

标准 Chapter 继续以 3–5 个媒体项为目标；超过 5 个候选时不强制全部使用。双素材 Compact Chapter 是明确、受门控的产品例外，不是把标准范围普遍改成 2–5，也不是媒体不足时的自动降级。

### 18.3 Compact Chapter 的用户体验方向

通过 C1.2 的双素材 Chapter：

1. 使用明确设计的双素材布局，不显示空的第三位置；
2. 不向用户显示“降级”“素材不足”或算法错误等内部标签；
3. Preview 可以在后续 Revision 无感扩充为标准 3–5 项，并保持同一 Memory stable identity；
4. Final 若仍只有两个高质量、互补的媒体项，也可以保留为 Compact Chapter；
5. 扩充、保持或失败均不要求用户再次上传、确认或执行其他交互。

本算法仓库只冻结产品所需的输出状态与数据合同；具体双素材页面布局属于 App 设计实现，不在此仓库修改。

### 18.4 禁止行为

- 不为凑第三项恢复 duplicate、CONTEXT_ONLY、DROP、unresolved 或 media unusable 内容；
- 不把一个 Beat 的 Primary 与 Fallback 当成两个媒体项；
- 不用同一画面的裁切、不同格式或近重复制造“双素材”；
- 不在 S10 内把单素材 Chapter 重新命名成 Aha；
- 不因媒体数量不足自行更换 S09 selected Memory。

### 18.5 合同传播

当前仓库中早期总览与 S12 草案仍有“每章 3–5 项”的概括表述。S10 冻结时必须把它们统一修订为“标准 3–5；通过严格门控的 Compact Chapter 允许 2 项”，避免下游验证误删合法 Compact Chapter。

这项例外不改变 S09 已冻结的 Memory membership、Chapter/Aha 数量或 Selection 规则，只改变一个已选 Chapter 的合法媒体呈现下限。

## 19. S10-C1.2｜Compact Chapter Pair Gate 与 Dominant Motif

**状态：CONFIRMED**

Compact Chapter 的两个 MediaDecision 不仅必须“不是重复”，还必须共同形成一个真实、可理解且足以表达 Chapter 的正向组合。C1.2 不重新判断 S09 已选 Memory 是否足够精彩，只判断这两个媒体位置能否把它安全呈现。

### 19.1 六道 Pair Gate

#### Gate 1｜Two distinct Beats

两个 MediaDecision 必须来自两个已证明不同的 Content Beats。以下组合失败：

- 同一 Beat 的不同角度或不同格式；
- Primary 与 Fallback；
- unresolved alternative group 的两个成员；
- canonical render identity 相同或实质近重复的两个位置。

#### Gate 2｜Core coverage

至少一个媒体项必须直接覆盖 Chapter core；两项不能都只是环境、路牌、工具或其他外围细节。

#### Gate 3｜Independent material contribution

第二项必须增加新的阶段、结果、环境、互动、具体对象、重要特征或代表性覆盖。删除它后若用户理解几乎无损，则它是 filler，不能靠“数量正好为二”通过。

#### Gate 4｜Positive pair relation

Pair 至少建立一种 grounded relation：

~~~text
PROGRESSION
ACTION_RESULT
ESTABLISHING_FOCAL
INTERACTION_RESPONSE
MEANINGFUL_CONTRAST
DUAL_ASPECT
DOMINANT_MOTIF_VARIATION
~~~

- `PROGRESSION`：进入 → 到达；
- `ACTION_RESULT`：制作 → 成品；
- `ESTABLISHING_FOCAL`：环境 → 核心活动；
- `INTERACTION_RESPONSE`：动作 → 回应；
- `MEANINGFUL_CONTRAST`：同一 Episode 中有意义的场景/状态变化；
- `DUAL_ASPECT`：同一体验中两个不同的内容侧面；
- `DOMINANT_MOTIF_VARIATION`：同一核心主题下，两个不同实例、重要特征或路线阶段。

不要求一定存在戏剧性的时间推进，但不能只是两个互不相关的碎片。

#### Gate 5｜Compact presentation floor

- 至少一项必须完整、直接地表达 Chapter core；
- 另一项可以存在轻微 presentation degradation，但必须仍真实、清楚并有独立贡献；
- `CORE_PARTIAL` 或只表达外围内容的 Route 不能作为 Compact Pair 的有效项；
- 两项均为 degraded 时失败。

#### Gate 6｜Fallback pair robustness

Primary Pair 通过后，还要检查最多 `3 × 3` 条预声明 Route 组合。任一可能成为最终有效输出的 Fallback 若会造成重复、丢失核心或破坏 Pair relation，则该 Route 标记为 `COMPACT_PAIR_INCOMPATIBLE`，不能用于这个 Compact Chapter。

删除不兼容 Route 后若仍有安全执行路径，可以继续并记录 coverage limitation；否则 Compact Pair unresolved/failed。该检查只比较已有 metadata 与 route identity，不请求媒体。

### 19.2 Dominant Motif

`Dominant Motif` 是一个 Chapter 中反复出现、并真正构成 Memory 核心的主要内容主题。它必须由已有 Candidate facts、Content Beats 与时间线支持，而不能只由颜色、风格或 embedding 相似推断。

以下证据共同支持 dominant：

1. Motif 出现在多个有界、可追溯的内容位置；
2. 它属于 Chapter core grounded facts，而非偶然背景；
3. 多个位置共同覆盖了 Episode 的主要内容；
4. 删除该 Motif 会实质改变 Chapter 是关于什么的。

**核心修正：** “同属古建筑”可以是 Chapter coherence，不是 duplicate proof。去重必须继续下钻到具体建筑实例、核心结构、展示作用与旅程阶段。

### 19.3 Dominant Motif 内部差异

同主题媒体可以共同入选，只要至少有一项正向差异被 grounded：

- 不同具体建筑实例；
- 不同核心结构或特征，如牌坊、塔楼、庭院、屋顶、木雕；
- 同一建筑中实质不同的内容位置，而不是轻微机位变化；
- 不同路线/游览阶段；
- 删除一项会损失主题范围或代表性。

建筑名称或精确地理位置未知时，也可用可见结构、环境与路线 progression 证明不同内容；不能只依赖 embedding distance。

### 19.4 时间距离与类别数量

时间距离只能作为 coverage/progression 支持信号，不能单独决定 distinct：

- 两分钟内可以看到两座完全不同的建筑；
- 三十分钟后也可能重新拍到同一座牌坊；
- 不设置“相隔 20 分钟自动不同”等固定阈值。

同样不设置“古建筑最多两项”等类别硬配额。一个以建筑欣赏为核心的 3–5 项 Chapter 可以包含 2–3 个甚至更多建筑媒体，只要每增加一项都提供新的实例、特征、旅程阶段或代表性覆盖。C2 继续使用 marginal contribution 控制同主题冗余，不为表面多样化强塞无关内容。

### 19.5 案例

1. 裱花过程 + 完成蛋糕：`ACTION_RESULT`，PASS。
2. 古镇牌坊进入 + 河边结束：`PROGRESSION`，PASS。
3. 入口牌坊 + 途中寺庙大殿：即使都属古建筑，也可为 `DOMINANT_MOTIF_VARIATION`，PASS。
4. 同一牌坊正面两次轻微换角度：删除其一不损失理解，FAIL duplicate。
5. 同一建筑整体外观 + 内部庭院：若分别展示实质不同建筑内容，可 PASS；只有视角移动而无新内容则 FAIL。
6. 古街行走 + 奶茶短暂停留：奶茶已是同一 Memory 的合法独立 Beat，且共同表达游逛—休息时可为 `MEANINGFUL_CONTRAST`；若只是外围偶然画面则 FAIL。
7. `09:10` 牌坊与 `09:12` 塔楼可因实例/结构不同 PASS；`09:10` 与 `09:40` 同一牌坊近似正面照不能只因时间远而 PASS。

### 19.6 输出

~~~text
CompactChapterPairDecision
  selected_memory_ref
  revision_ref
  media_decision_refs[2]
  pair_relation_type
  chapter_core_coverage_refs[]
  independent_contribution_refs[]
  dominant_motif_ref
  within_motif_distinctness_refs[]
  pair_quality_result
  fallback_pair_compatibility_matrix_ref
  compact_pair_state =
    COMPACT_PAIR_PASS
    | COMPACT_PAIR_UNRESOLVED
    | COMPACT_PAIR_FAIL
  failure_or_limitation_refs[]
  policy_and_signal_versions
  decision_trace
~~~

Dominant Motif 与 Pair Gate 均复用现有结构化 Evidence，不新增 VLM/strong-model、Raw/HQ 请求或 App 交互。该同主题差异原则也将由 S10-C2 的标准 3–5 set 继承。

## 20. S10-C1.3｜Insufficient Chapter Media、Atomic Publish 与一次有界重选

**状态：CONFIRMED**

当一个已选 Chapter 只有 0–1 个合法媒体项，或两个候选已经被证明无法通过 Compact Pair Gate 时，S10 不发布单素材 Chapter、不自动改成 Aha，也不直接从其他 Candidate 换入替代者。当前 Revision 先产生显式媒体不足记录，再由编排层判断是否允许一次有界 S09 re-selection。

### 20.1 用户可见 Revision 必须原子发布

新 Revision 必须在完整通过当前发布链路后整体可见，不能把部分成功、部分残缺的中间结果暴露给用户：

- 新结果未通过前继续显示上一成功发布 Revision；
- 不先显示单素材/空占位 Chapter，再突然删除或替换；
- 不弹出要求重新上传、重新 Sync 或手动选择替代素材的交互；
- 失败不等于 `EMPTY_DAY`；
- Manual 素材仍留在独立 Manual 窗口和事实账本。

上一成功版本只有在其事实、媒体与政策仍合法时才可继续显示；retention 不能保护已经被证明错误、越权或必须撤回的内容。此类 correction/withdrawal 走专门合法路径，不能用“保持旧版”掩盖。

### 20.2 先完成检查，再批量收集

S10 不在发现第一个失败 Chapter 时立刻重选。它先完成原 selected set 中所有 Memory 的低成本 S10 检查，再一次性生成：

~~~text
S10MediaFailureBatch
  current_selection_attempt_ref
  proven_media_insufficiency_refs[]
  operational_or_unknown_refs[]
  contract_invalid_refs[]
  unaffected_success_refs[]
  batch_completion_status
~~~

这样一次重选可以同时处理多个已证明失败的 Memory，避免按 Chapter 反复进入 S09。

### 20.3 允许重选的唯一失败类别

只有 `PROVEN_MEDIA_INSUFFICIENCY` 可进入本机制，例如：

- proven distinct media capacity 为 0 或 1；
- capacity 为 2，但 Compact Pair 已确定 FAIL；
- 已证明没有合法 Anchor、格式或 ExactMediaSourcePlan；
- 所有预声明 Route 已证明不可用或 source terminal unavailable；
- 后续 C2/C3 若证明不存在任何合法最终 set，也可沿同一机制登记，但不能增加第二次机会。

失败必须是确定性的媒体可呈现性结论，不能把“暂时没跑通”写成内容失败。

### 20.4 禁止因这些原因重选

以下情况不允许排除当前 Memory 后换人：

- transient network/provider/render failure；
- source 或关键 Evidence 仍为 `UNKNOWN`；
- budget、timeout 或服务不可用；
- policy/version compatibility 未证明；
- lineage、Revision、白名单、provenance 或 input contract invalid；
- 任何可能改变 Day State、retention 或 membership 但尚未解决的 operational blind spot。

这些情况根据已有 Revision 与阶段进入 HOLD/BLOCK，不能伪装成 Memory 质量不足。

### 20.5 一次、有界、批量的 S09 re-selection

每个 Revision 最多允许一次：

~~~text
complete original S10 batch
→ create attempt-scoped S10FailureExclusionSet
→ create a new S09 selection_attempt_id
→ same revision / snapshot / candidate pool / policy version
→ rerun all S09 set, lineage and capacity constraints
→ reuse unaffected S10 artifacts when fingerprints match
→ run S10 only for newly selected or invalidated items
→ success, or stop as re-selection exhausted
~~~

`S10FailureExclusionSet` 只在这次新 attempt 中排除已证明媒体不足的 revision-scoped Memory instance。它不是永久 rejected、duplicate 或低价值结论；新素材或新 Revision 可以使该 Memory 重新参加。

S10 不能指定替代 Candidate，S09 必须重新执行完整 selection objective、constraints、published retention、lineage、Preview/Final cap 与 fifth gate。第二次 S10 仍失败时停止，不生成第三个 selection attempt。

### 20.6 Preview / Final 用户结果

#### 新 Preview，无 prior published Revision

- re-selection 成功：只展示完整通过的新结果；
- 仍失败：不发布当前 Revision，状态为 blocked/no-publishable，不是 EMPTY_DAY；
- 不显示残缺 Chapter、空卡片或面向用户的算法错误。

#### 已有成功发布的 Preview

- 当前 Revision 未完整通过前，继续显示仍合法的 last successfully published Revision；
- re-selection 成功后原子切换到新 Revision；
- re-selection 仍失败时 `HOLD_PREVIOUS_REVISION`，不制造用户可见闪烁或部分更新。

#### Final Revision

- 先允许同一套一次有界 re-selection；
- 成功后正常进入 Final 下游；
- 仍失败时 `BLOCKED_NO_PUBLISHABLE_REVISION`；
- 仍合法的 prior Preview 可以继续访问，但不能被偷偷改名为 Final；
- 无 prior 时保持 blocked，也不能解释为 EMPTY_DAY。

### 20.7 输出

~~~text
ChapterMediaInsufficiencyRecord
  selected_memory_ref
  revision_ref
  original_selection_attempt_ref
  proven_distinct_media_capacity
  compact_pair_state
  failure_class =
    PROVEN_MEDIA_INSUFFICIENCY
    | OPERATIONAL_OR_UNKNOWN
    | CONTRACT_INVALID
  reason_refs[]
  user_visible_revision_impact
  audit_trace

S10BoundedReselectionRequest
  revision_ref
  snapshot_ref
  original_selection_attempt_ref
  failure_batch_ref
  attempt_scoped_exclusion_refs[]
  unaffected_reusable_artifact_refs[]
  re_selection_attempt_count          # must be 1
  policy_and_candidate_pool_fingerprint
  request_state
~~~

### 20.8 成本与边界

有界重选不重跑 S04–S08、不重新理解全天、不新增 Raw 上传。它只重跑 S09 集合求解，并对新进入 selected set、且没有可复用 artifact 的 Memory 执行必要 S10 元数据决策。

本项不定义 App 的具体“正在整理”视觉样式；只要求无阻塞弹窗、无再次上传交互、无残缺 Revision 曝光。具体状态提示属于后续 App 产品设计。

## 21. S10-C1 Closeout

**状态：FROZEN BY CANONICAL V1.21**

S10-C1 已确认标准 3–5、严格双素材 Compact Chapter、Dominant Motif 同主题多样性、0–1 项不足处理、原子发布，以及每 Revision 最多一次的批量 S09 有界重选。下一阶段进入 S10-C2：从容量足够的 MediaDecision 中选择最终 3–5 项或已通过的 Compact Pair。

## 22. S10-C2.1｜Adaptive 3 / 4 / 5 Target Size

**状态：CONFIRMED**

标准 Chapter 不固定输出五项，也不先给单个 MediaDecision 排名后机械取 Top-K。S10-C2 先比较合法完整集合，再按 set-level incremental value 决定最终是 3、4 或 5 项。

这里的“合法完整集合”包含 C2.2 hard constraints、C2.3 source occupancy，以及 C3.2.2 预先计算的轻量 `HeroPreEligibility` coverage。target size 不能在这些约束应用前先锁死；实现上虽分章节说明，执行上必须先完成全部 per-candidate feasibility metadata，再开始 C2 set search。

~~~text
2 items
→ only a confirmed CompactChapterPairDecision

3 items
→ standard complete baseline

4 items
→ add only with material set-level increment

5 items
→ add only through stricter fifth-item gate
~~~

### 22.1 三项基础集合

先枚举/搜索合法三项组合，而不是独立挑三张“最高分”媒体：

~~~text
candidate 3-item sets
→ hard-constraint validation
→ Chapter core coverage
→ distinct Beat / relation coverage
→ coherence and non-redundancy
→ C2.2 hierarchical comparison
→ best legal base set
~~~

若没有合法三项集合，但存在已通过 C1.2 的 Compact Pair，则输出两项 Compact Chapter；两者都不存在时进入 C1.3 insufficiency/re-selection 路径。

### 22.2 Set Incremental Value

第四/第五项相对于当前合法集合的增量分为：

~~~text
NONE
MINOR
MATERIAL
UNKNOWN
~~~

- `NONE`：没有增加用户可辨认的新内容；
- `MINOR`：只有画面变化或轻微补充，不足以增加一个展示位置；
- `MATERIAL`：增加新的阶段、互动、结果、具体对象、重要特征、Dominant Motif 实例或重要时间线覆盖；
- `UNKNOWN`：现有 Evidence 无法可靠判断，不能当作 MATERIAL。

更清晰、更漂亮但表达同一 Beat 的媒体，应替换集合中的较弱项，不作为增量项并存。

### 22.3 第四项门

第四项必须：

1. 自身 MediaDecision 可合法选择；
2. 与当前三项不存在 hard conflict 或 presentation redundancy；
3. 增加至少一项 `MATERIAL` 内容贡献；
4. 删除后会出现明确的阶段、结果、对象、特征或代表性覆盖损失；
5. 加入后集合仍保持 Chapter coherence。

不满足时保持三项，即使候选容量大于三。

### 22.4 第五项严格门

第五项必须通过第四项全部条件，并同时证明：

1. 它表达的内容没有被现有四项充分覆盖；
2. 它代表 Chapter-important 的缺失阶段、对象、结果、长时间覆盖或 Dominant Motif 范围；
3. 它的贡献不能通过替换现有某一项以更简洁的方式获得；
4. 加入后不会使集合在具体实例、展示作用、源位置或视觉呈现上显得拖沓；
5. 它达到正常 presentation floor，不用 degraded/filler 内容凑第五项。

第五项不是固定配额；五个候选中只有三个产生 material contribution 时，最终仍输出三项。

### 22.5 不设置格式或类别配额

- 不要求至少一个 LIVE 或 VIDEO；
- 不要求 PHOTO/LIVE/VIDEO 混合；
- 不要求不同语义类别各占一个位置；
- 不要求时间轴等距离抽样；
- 不限制 Dominant Motif 最多占几个位置。

一个古建筑 Chapter 可以包含多个不同建筑，只要每项通过 within-motif distinctness 与增量门。反过来，也不能因为媒体格式不同就把同一建筑/同一 Beat 重复加入。

### 22.6 案例

1. 古镇候选包含入口牌坊、寺庙大殿、独立塔楼、河边建筑、重复石板路、普通路牌与偶然奶茶画面：前四项可形成四项 Chapter；第五项只有在奶茶已是重要独立 Beat 或其他内容有不可替代增量时才加入。
2. 生日的准备蛋糕、点蜡烛、吹蜡烛、鼓掌、合照分别覆盖不同阶段，可合法输出五项。
3. 咖啡短聚已有朋友入座、咖啡食物、交谈互动三个位置；另外四张咖啡特写没有独立增量，保持三项。
4. 建筑欣赏旅程有五座 grounded 为不同实例的重要建筑时，可以全部为同一 Dominant Motif，不强塞路牌或餐饮制造跨类别多样性。

### 22.7 输出

~~~text
ChapterMediaTargetSizeDecision
  selected_memory_ref
  revision_ref
  compact_pair_decision_ref
  best_legal_base_set_ref
  fourth_item_increment_decision_ref
  fifth_item_gate_decision_ref
  final_target_size              # 2 | 3 | 4 | 5
  target_size_state
  rejected_increment_refs[]
  limitation_refs[]
  policy_and_signal_versions
  decision_trace
~~~

C2.1 不决定最终媒体顺序、Hero、Aha supporting item 或同一 RawAsset 占位上限。它只确定合法集合的自适应数量与停止规则。

## 23. S10-C2.2｜Chapter Media Set Constraints 与 Hierarchical Objective

**状态：CONFIRMED**

S10-C2.2 比较完整的 Chapter media sets，而不是给每个媒体项计算一个决定一切的 overall score。真实性、核心覆盖与内容推进不能被高画质补偿；画质只在语义与集合贡献近似等价时决定胜负。

### 23.1 Set hard constraints

标准 Chapter set 必须同时满足：

1. selected count 与 C2.1 的 target size 一致，且为 3–5；Compact Chapter 使用已确认的两项 Pair，不混入本搜索；
2. 所有成员来自同一 selected Memory、Revision、S10 attempt 与合法 MediaDecisionInventory；
3. 每个成员为 S10-C selectable state，且恰好来自一个不同 Content Beat；
4. unresolved alternative group 最多选择一个；
5. 不存在 `PRIMARY_PRIMARY_COLLISION` 或其他 hard co-selection conflict；
6. 不存在 proven presentation redundancy、canonical render duplicate 或同一 Beat 的格式变体并存；
7. 至少一项直接覆盖 Chapter core，集合整体达到 required core coverage；
8. 每一项均有 material marginal contribution，删除后会产生可说明的内容损失；
9. 所有 Primary Route 均合法，format/source plan 不越出白名单与 Evidence scope；
10. relation、policy、lineage、version 或 provenance unresolved/invalid 不得由画质或数量补救。
11. 集合必须通过 C2.3 的 RawAsset source occupancy contract；同一源文件不能靠不同 Frame、interval 或格式绕过占位上限。
12. 集合必须至少包含一个 C3.2.2 `HeroPreEligibility=PASS` 的成员；该条件只保证存在合法封面，不允许 Hero 美感反向主导集合内容。

任何 hard constraint 失败的集合直接淘汰。冲突不沿普通图链传递；只有 explicit group/cardinality contract 才产生 group-level limit。

### 23.2 SetEvaluationCard

~~~text
ChapterMediaSetEvaluationCard
  media_set_candidate_ref
  media_decision_refs[]
  hard_constraint_results[]
  chapter_core_coverage
  per_item_material_contribution_refs[]
  beat_role_coverage[]
  progression_and_result_coverage
  dominant_motif_coverage
  set_coherence
  set_redundancy
  inference_risk
  presentation_quality_profile
  source_occupancy_profile
  hero_preeligibility_coverage
  route_and_fallback_robustness
  prior_published_continuity
  target_size_increment_refs[]
  limitation_refs[]
  policy_and_signal_versions
~~~

各维度保留独立信号与 reason refs，不压成 overall score。

### 23.3 分层比较目标

合法集合按以下顺序比较；只有前一层相同或 policy-defined near-equivalent 时，才进入下一层：

~~~text
1 legality / truth / scope
2 Chapter core coverage
3 every item has material marginal contribution
4 meaningful Beat progression and representative coverage
5 set coherence, redundancy and inference risk
6 semantic representativeness and presentation quality
7 route/fallback robustness and source readiness
8 prior-published media continuity when near-equivalent
9 parsimony and deterministic tie-break
~~~

#### Layer 1｜Legality / Truth / Scope

只比较通过全部 hard constraints 的集合。非法引用、冲突、UNKNOWN outcome-changing state 或白名单越界直接失败。

#### Layer 2｜Chapter Core Coverage

优先选择直接呈现 Chapter 核心、结果与关键内容的集合。漂亮但外围的媒体不能胜过仍清楚可用的核心位置。

#### Layer 3｜Material Contribution

集合中每项都执行删除测试。删除后用户没有真实内容损失的项不得入选，也不能因为 target size 偏好保留。

#### Layer 4｜Meaningful Coverage

优先覆盖重要 Beat、过程/转折/结果、长 Episode 的关键阶段，以及 Dominant Motif 内真正不同的实例与特征。它不是钟表时间均匀度、RawAsset 使用率或类别数量。

#### Layer 5｜Coherence / Redundancy / Inference Risk

集合整体应像同一段 Memory；控制具体实例、展示作用与呈现位置重复。类别相同可以强化 Dominant Motif，一组漂亮但互不相关的碎片不能靠美感建立 coherence。

#### Layer 6｜Semantic & Presentation Quality

当前五层近似时，再比较主体清晰度、构图可理解性、模糊、曝光、遮挡、稳定性与观看体验。所有候选已通过 usability floor；略有技术缺陷但直接表达核心的位置，可以胜过高清外围画面。

#### Layer 7｜Route / Fallback Robustness

内容与画质近似时，优先 Primary 更确定、Fallback 更完整、source failure domain 更独立、activation collision 更少的集合。

#### Layer 8｜Revision Stability

多个集合质量近似时，优先保留上一成功发布 Revision 中仍合法的媒体位置。新内容有 material gain 时可以替换/扩充；仅稍微更漂亮的近似画面不能让 Chapter 每次 Sync 重新洗牌。

#### Layer 9｜Parsimony / Determinism

仍然近似等价时遵守 C2.1 自适应数量，偏好更精简的合法结果；随后使用稳定时间键与 identity key 确保相同输入、版本和参数得到相同输出。

### 23.4 画质边界

“意义优先”不允许不可观看媒体进入。严重模糊、核心不可见、损坏或无法理解的位置已经在 A2 Presentation Usability Gate 被淘汰。

本层允许的是：一张仍然可辨认、略暗或略有噪点但记录关键动作的媒体，优先于一张非常漂亮却只表达外围内容的媒体。

### 23.5 选择算法与成本

在典型少量 MediaDecision 下，S10-C 可以枚举 3–5 项合法子集；候选较多时使用保持相同 objective order 的 deterministic branch-and-bound。搜索预算或 benchmark 尚未冻结为 Production 数值，不能因超时静默退化为单体 Top-K。

整个比较只使用已有 cards、relations、refs 与离散信号，不新增模型调用、HQ 请求或媒体渲染。

### 23.6 案例

1. 古镇集合 A 为入口牌坊、寺庙、塔楼、河边建筑；集合 B 为牌坊、高清石板路、漂亮店铺、奶茶特写。Chapter core 为建筑游览时，A 的核心与代表性覆盖优先。
2. 生日集合 A 包含仍可辨认但略暗的吹蜡烛、点蜡烛、鼓掌与合照；集合 B 是四张高清蛋糕/餐桌照片。A 更真实表达过程，应优先。
3. 若两个集合的 Beat/核心覆盖完全相同，一组画面更清晰稳定，则选择画质更好的一组。
4. 若新 Revision 只有一个近似替代帧稍微更清晰，旧媒体仍合法且质量近似，则保持旧位置；若新增了此前缺失的重要结果 Beat，则允许替换或扩充。

### 23.7 输出

~~~text
ChapterMediaSetDecision
  selected_memory_ref
  revision_ref
  target_size_decision_ref
  winning_media_set_ref
  selected_media_decision_refs[]
  rejected_legal_set_refs[]
  hard_constraint_audit_refs[]
  hierarchical_comparison_trace
  prior_revision_continuity_trace
  unresolved_or_failure_refs[]
  decision_state
  policy_and_signal_versions
~~~

C2.2 只决定集合成员，不决定用户可见顺序、Hero、具体版式或 Aha supporting item。

## 24. S10-C2.3｜RawAsset Source Occupancy 与 Long-Manual Multi-Beat Exception

**状态：CONFIRMED**

S10-C2.3 控制同一份原始素材在一个 Chapter 最终集合中可以占几个用户可见位置。它既不把一段包含真实过程的长 Manual 强行压成一个位置，也不允许通过切帧、换格式或切成多个近似片段让一个源文件占满 Chapter。

### 24.1 术语与证据边界

- `RawAsset`：用户一次采集或导入的一份原始照片/视频文件；
- `Canonical Source Family`：同一 RawAsset 的派生物，或已经被 lineage/canonical duplicate Evidence 证明来自同一原始内容的文件集合；
- `Source Occupancy`：一个待选 Chapter media set 中，追溯到同一 Canonical Source Family 的最终媒体项数量；
- `Validated Multi-Beat Source`：上游已经产生多个不同 CandidateContentUnit/Content Beat，并通过必要验证证明它们在同一 RawAsset 内表达不同内容位置的源文件。

不同 Frame、PHOTO/LIVE_2S/VIDEO_5S 格式、不同 source interval 或不同派生文件名，不会自动变成独立来源。只有已有 lineage/canonical Evidence 可以把多个文件归为同一 Source Family；S10 不凭相似感觉猜测来源关系。

视频时长不是多占位置的资格。两分钟 Manual 不自动获得三个位置；十五秒 Manual 若上游已证明存在两个不同 Beat，也不因时长短而被机械禁止。S10 只消费上游已经验证的 ContentUnit、Window、Beat、Anchor 与 support scope，不在本阶段重新切分任意 16 秒、73 秒或其他 Manual 时长。

### 24.2 V1 占位合同

#### Standard Chapter（3–5 项）

1. 同一 Canonical Source Family 默认最多占 **2** 个位置；
2. 只有通过 `VALIDATED_MULTI_BEAT_SOURCE_EXCEPTION`，上限才可提高为 **3**；
3. **3 是 V1 硬上限**，同一 Source Family 不得占 4–5 个位置；
4. 上限只限制来源集中度，不要求不同媒体格式、不同类别或等距离时间采样；
5. 两个同源位置仍须分别通过 C2.2 的 distinct Beat、material contribution 与 non-redundancy hard constraints。

普通 Auto 9 秒视频与 Manual Photo 通常只能贡献一个位置，因为一个 ContentUnit/Beat 不能在 S10 被重新拆成多个 Beat。它们不是因为来源类型受到歧视，而是没有上游已验证的多个内容单元。

#### Compact Chapter（2 项）

Compact Pair 默认优先使用不同 Source Family，但允许两个位置来自同一 RawAsset。该组合必须同时通过：

1. C1.2 全部 Compact Pair Gates；
2. 两个上游已验证的不同 Content Beat；
3. 各自有独立、合法的 Anchor 与 source scope；
4. 最终 source intervals 不存在实质重叠；仅为保留必要 semantic landmark 的最小边界重叠可以接受，但不得重复同一核心动作；
5. 存在 grounded positive pair relation，且删除任一项都会产生明确内容损失；
6. Primary 与可激活 Fallback 组合不会把两项变成 canonical render duplicate。

通过时记录内部 `SINGLE_SOURCE_COMPACT_RISK`，但不向用户显示“风险”“降级”或“素材不足”标签。若存在语义、核心覆盖和画质近似等价的不同来源 Pair，按 C2.2 Layer 7 优先不同来源；不能为了来源多样性牺牲更高层的真实性和 Chapter 核心表达。

### 24.3 三项同源严格例外

同一 Source Family 占三个位置时，以下条件必须全部满足：

1. 上游已经确认至少三个不同 CandidateContentUnit/Content Beat，S10 不现场创造第三个 Beat；
2. 三个位置分别绑定独立合法的 Anchor 与 support scope；
3. source intervals 实质不重叠；必要的最小边界重叠不得重复核心动作、结果或展示作用；
4. 三项表达不同事实、阶段、互动、结果、具体对象、重要特征或 Dominant Motif 实例；
5. 每项均通过 material deletion test，删除后存在可以解释的 Chapter 内容损失；
6. 三项之间存在 progression、action-result、representative motif coverage 或其他 grounded set-level 关系；
7. 不是同一动作的不同时间点、轻微机位变化、不同裁切或 PHOTO/LIVE/VIDEO 格式变体；
8. 所有 Primary Route 合法，任何可能激活的 Fallback 冲突均已进入 route collision ledger；
9. exception state 必须为 `PASS`。`UNKNOWN`、Evidence 不足或 contract invalid 均不能放宽到三个位置。

如果有意义和画质近似等价的独立 RawAsset，可以在 C2.2 的后层比较中替换一个同源项以提高 source robustness；但“存在独立来源”不是高于核心覆盖的硬配额。

### 24.4 Fallback 与运行时边界

Source Occupancy 先按候选集合的 Primary realization 判定。预声明 Fallback 仍要检查 activation-time source occupancy 与 canonical render collision：

- Fallback 不得把两个位置激活成相同画面或同一核心片段；
- 可能造成四个及以上同源位置的 Route 组合不能被共同激活；
- 需要三项同源的 Fallback realization 时，也必须已有同一套 exception Evidence；
- S10-C 不在失败发生后临时搜索新 RawAsset、切新 interval 或更换 Content Beat；
- 具体 Fallback 冲突的确定性执行/阻断顺序由后续 S10-D 使用既有 collision ledger 定义。

Source failure domain 与 Source Family 是不同概念：前者描述共同故障风险，后者描述是否来自同一原始内容。两个不同 RawAsset 即使暂时存储在同一服务中，也不能仅因共享故障域就被误判为同一素材。

### 24.5 案例

1. **73 秒陶艺 Manual：** 准备泥料、拉坯成形、展示成品已经分别通过上游验证，三个 interval 实质不同且均不可删除，可通过三项同源例外。
2. **60 秒生日 Manual：** 点蜡烛、吹蜡烛、众人鼓掌分别表达准备、核心动作与回应，可通过；若所谓三项只是吹蜡烛动作的三个相邻时间点，则只能保留一个。
3. **15 秒建筑视频：** 开头、中间、结尾都是同一座建筑的轻微视角移动，即使画面不同也通常只有一个 Beat，只能占一个位置。
4. **2 分钟古镇 Manual：** 牌坊、寺庙、塔楼被上游证明为不同实例与路线阶段时，可以占三个位置；第四段近似石板路不得使同一源占第四个位置。
5. **五项 Chapter 全来自同一 2 分钟视频：** 不允许。最多选择三个真实不同的重要节点；其余位置使用其他合法来源，或按 C2.1 保持三项。完整原 Manual 仍保留在独立 Manual 窗口。
6. **双素材演出 Compact：** 演出开始与谢幕均来自同一段长 Manual，若是两个不同 Beat、具有 progression 且 Pair/Fallback 均安全，可以通过并记录 `SINGLE_SOURCE_COMPACT_RISK`。
7. **同一视频被重复导入两次：** 已有 canonical duplicate/lineage Evidence 时归入同一 Source Family，不能用两个文件 ID 绕过上限；没有证据时 S10 不凭空合并，但已有的 identity-collision nomination 若仍为 UNKNOWN，不能被忽略。
8. **两份独立视频都拍到同一动作：** 虽然 Source Family 不同，仍可能因 C2.2 presentation redundancy 被抑制；来源不同不等于内容一定不同。

### 24.6 输出

~~~text
ChapterSourceOccupancyDecision
  selected_memory_ref
  revision_ref
  media_set_candidate_ref
  source_family_occupancy[]
    source_family_ref
    selected_media_decision_refs[]
    primary_occupancy_count
    allowed_occupancy_limit
    multi_beat_exception_state =
      NOT_NEEDED
      | PASS
      | FAIL
      | UNRESOLVED
    exception_evidence_refs[]
  compact_same_source_state =
    NOT_APPLICABLE
    | DISTINCT_SOURCES
    | SINGLE_SOURCE_PASS
    | SINGLE_SOURCE_FAIL
    | SINGLE_SOURCE_UNRESOLVED
  fallback_activation_occupancy_refs[]
  source_identity_limitation_refs[]
  occupancy_decision_state
  policy_and_signal_versions
  decision_trace
~~~

### 24.7 Invariants、成本与边界

1. Source Occupancy 不能被不同格式、裁切、interval、派生 ID 或重复导入绕过；
2. 一个 Content Beat 仍最多贡献一个最终媒体项；
3. 默认上限为二，严格例外上限为三，V1 不存在第四项同源例外；
4. 时长、Manual 来源或用户主动拍摄行为都不能单独证明多 Beat；
5. 同源多项不会删除、压缩或改写独立 Manual 窗口与事实账本中的原始素材；
6. 本项不新增 VLM/strong-model、HQ 请求、媒体渲染、上传或 App 交互；
7. 本项不改变 S09 Memory membership，不重新打开 Manual Window 规划，也不决定最终顺序、Hero 或 Aha supporting item。

## 25. S10-C2 Closeout 与下一检查点

**状态：FROZEN BY CANONICAL V1.21**

S10-C2 已确认 Compact/Standard 容量入口、自适应 3/4/5 项数量、完整集合 hard constraints、分层选择目标、Dominant Motif 同主题差异，以及同一 RawAsset 默认二项、严格例外三项的来源占位合同。

下一步进入 S10-C3：只在 Chapter 最终成员已经确定后，设计用户可见媒体顺序与 Hero 选择。它不回头改变 C2 选中的成员，也不提前处理 Aha supporting item。

## 26. S10-C3.1｜Grounded Chapter Media Chronology

**状态：CONFIRMED**

S10-C3.1 只为 C2 已经选定的 Chapter media members 计算用户可见顺序。排序不得反向影响集合成员、数量、Compact/Standard 状态或 S09 Memory membership。

V1 采用 `GROUND_TRUTH_CHRONOLOGY_FIRST`：Chapter 打开后的媒体序列以可信拍摄时间线为主，不为画面吸引力、格式交替或“更像故事”而改写先后。Hero 是独立展示角色，留到 C3.2；一个后段媒体成为 Hero，不会把它移动到 Chapter 时间线第一项。

### 26.1 排序依据

排序只使用已有结构化时间与关系 Evidence，优先级如下：

~~~text
1 same-source validated source offset / temporal landmark order
2 trusted non-overlapping capture-time intervals
3 explicit upstream temporal precedence relation
4 co-temporal group + stable identity tie-break
~~~

具体规则：

1. 同一 RawAsset 的多个已验证 Beat，优先按原文件中的 source offset、Anchor time 与必要 semantic landmark 顺序排列；
2. 不同 RawAsset 若可信 capture-time intervals 明确不重叠，较早者在前；
3. 时间相同、范围重叠或精度不足时，只能用已有、可追溯的 `BEFORE/AFTER`、progression 或其他 temporal precedence Evidence 解开先后；
4. `ACTION_RESULT`、`INTERACTION_RESPONSE` 等语义关系可以验证顺序，但不能仅凭“动作通常应在结果前”的常识覆盖可信时间事实；
5. import time、Sync time、upload time、处理完成时间、数组顺序、文件名、Manual/Auto 优先级、模型分数与媒体格式均不得成为真实时间排序依据。

### 26.2 Co-temporal Group

若两个或多个 Beat 的可信时间范围重叠，且没有 Evidence 支持更精确的先后，则建立 `CoTemporalGroup`：

- 组内使用 stable identity key 产生确定性显示顺序；
- 相同输入、Revision、policy 与 signal version 必须得到相同结果；
- 该顺序只解决界面位置，不证明现实中的先后；
- S11 Narrative 与 S12 Claim Validation 必须收到 `NO_RELATIVE_TEMPORAL_CLAIM`，不得把稳定排序写成“先……然后……”；
- 若组内真实顺序会实质改变 Chapter 含义，则不能用 stable tie-break 掩盖，必须标记 `ORDER_MATERIAL_UNRESOLVED`。

`ORDER_MATERIAL_UNRESOLVED` 或相互矛盾的可信时间证据属于 contract/temporal failure，不是 `PROVEN_MEDIA_INSUFFICIENCY`，因此不能触发 C1.3 的 S09 候选替换。当前 Revision 按原子发布规则 HOLD/BLOCK，不能静默伪造顺序。

### 26.3 Membership first，ordering second

排序必须在 C2 `ChapterMediaSetDecision` 固定后执行：

- 不能因为第一张不够漂亮而更换集合成员；
- 不能为 PHOTO/LIVE/VIDEO 交替而换位；
- 不能为平均覆盖三个小时而把后拍内容提前；
- 不能把同主题建筑聚到一起而跨过一个已经入选的中间 Beat；
- 时间线存在未展示空档时，不补 filler，也不恢复 CONTEXT_ONLY/DROP；
- Compact Chapter 使用同一排序合同，不另造“主图在前”的例外。

### 26.4 Hero 与 Fallback 不改写顺序

用户可见媒体位置绑定 `ContentBeat` 的 canonical grounded time，而不是当前激活 Route 的文件时间：

- Primary 切换到预声明 Fallback 时，媒体仍留在原 Beat 的位置，避免运行时重新洗牌；
- Fallback 必须继续表达同一 Beat 合法 scope，不能因来源较早或较晚改变 Chapter chronology；
- Hero 可以来自时间线任一位置，但只承担封面/入口职责；
- Hero 是否在展开后的媒体序列中重复展示、以及允许的格式，留给 C3.2 决定。

### 26.5 Cross-Revision 稳定性

1. 同一组成员与相同可信时间事实必须保持相同顺序；
2. 新 Revision 新增一个合法媒体项时，将其插入真实时间位置，不追加到末尾；
3. 媒体成员被替换但继承同一 Beat 时，保持该 Beat 的时间位置；
4. 若上游时间事实被合法修订，则真实性优先于旧位置稳定性，并记录 `ORDER_CHANGED_BY_TIME_CORRECTION`；
5. 不能为了避免用户看到位置变化而保留已经被证明错误的旧顺序。

### 26.6 案例

1. **古镇 A–B–C：** `09:00` 牌坊、`09:20` 寺庙、`09:45` 奶茶、`10:00` 塔楼均入选时，顺序保持牌坊 → 寺庙 → 奶茶 → 塔楼；不能为了聚合古建筑改成牌坊 → 寺庙 → 塔楼 → 奶茶。
2. **恢复主线但中间 Beat 未入选：** 牌坊 A 与塔楼 C 入选、奶茶 B 未入选时，直接显示 A → C；时间空档不要求补一项。
3. **生日流程：** 准备蛋糕 → 点蜡烛 → 吹蜡烛 → 鼓掌 → 合照按可信拍摄时间排列；不能把最漂亮的合照移到时间线开头。
4. **73 秒陶艺 Manual：** 准备泥料、拉坯、成品按同一视频 source offsets 排列；不同截取格式不改变顺序。
5. **同秒照片：** 两张照片都为 `10:05:00`，且无更精确 Evidence 时进入同一 CoTemporalGroup，稳定显示但不生成先后 Claim；若已有可信动作—结果顺序则按该 Evidence 排列。
6. **后段 Hero：** `10:00` 塔楼最能代表 Chapter，可以在 C3.2 成为 Hero；展开时间线后它仍位于 `09:00` 牌坊、`09:20` 寺庙之后。
7. **Fallback 激活：** `09:20` 寺庙 LIVE 失败后切换到该 Beat 的 PHOTO Fallback，仍保留第二个位置，不因 PHOTO 文件 metadata 差异被移动。
8. **时间证据冲突：** 两个设备分别给出互相矛盾且无法消解的动作/结果顺序，而先后会改变用户理解时，不能用 stable ID 假装真实顺序，当前 Revision 必须 HOLD/BLOCK。

### 26.7 输出

~~~text
ChapterMediaOrderDecision
  selected_memory_ref
  revision_ref
  chapter_media_set_decision_ref
  ordered_entries[]
    presentation_order_index
    media_decision_ref
    content_beat_ref
    canonical_beat_time_or_interval
    order_basis
    co_temporal_group_ref
    relative_temporal_claim_permission
  co_temporal_groups[]
  temporal_precedence_refs[]
  order_material_conflict_refs[]
  prior_revision_order_trace
  order_decision_state =
    ORDER_READY
    | ORDER_READY_WITH_CO_TEMPORAL_GROUP
    | ORDER_MATERIAL_UNRESOLVED
    | ORDER_CONTRACT_INVALID
  policy_and_signal_versions
  decision_trace
~~~

### 26.8 Invariants、成本与边界

1. C3.1 不改变 C2 成员或数量；
2. Hero、格式、美感、Manual 优先级与 Fallback 激活不能改写 canonical Beat order；
3. stable tie-break 只保证确定性，不升级为现实时间 Evidence；
4. 时间顺序 UNKNOWN 时不得生成虚假的因果或 progression Claim；
5. 本项只处理一个 Chapter 内部顺序，不改变 S09 的 Chapter/Aha 跨 Memory canonical order；
6. 本项不新增模型调用、上传、HQ 请求、渲染或 App 交互；
7. 本项不决定 Hero 类型、Hero 是否单独展示或 Aha supporting item。

## 27. 下一检查点

进入 S10-C3.2：定义 Chapter Hero 的候选范围、选择层级、格式与 Fallback，并明确 Hero 是从已选 2–5 项中产生，还是可以额外使用一个不属于正文集合的媒体。

## 28. S10-C3.2.1｜Hero Membership 与 V1 Static Cover Contract

**状态：CONFIRMED**

`Hero` 是 Chapter 在卡片、列表或入口表面使用的代表性封面，不是 Chapter 时间线第一项，也不是独立内容成员。

V1 采用：

~~~text
hero content identity
= exactly one member of the confirmed Chapter media set

hero surface format
= static PHOTO representation of the same ContentBeat / EvidenceAnchor
~~~

Hero 必须绑定 C2 已选 Compact/Standard Chapter 的一个 `MediaDecision`。不得从未入选 Candidate、CONTEXT_ONLY、DROP、另一个 Memory 或全天素材池中额外找一张漂亮封面。

### 28.1 Hero 不增加内容数量

1. Standard Chapter 的 Hero 仍属于已选 3–5 项之一，不成为第六项；
2. Compact Chapter 的 Hero 必须来自两项 Pair 之一，不成为第三项；
3. `hero_member_ref` 与正文成员共享同一个 ContentBeat、EvidenceAnchor、事实 scope 与 stable content identity；
4. Hero 可以来自时间线任一位置，但不改变 C3.1 `presentation_order_index`；
5. App 在卡片封面与展开页如何复用该视觉属于呈现设计，但任何内容计数、去重与 lineage 都只计算一次。

### 28.2 V1 Hero 格式

V1 Chapter Hero 固定使用静态 `PHOTO` surface representation：

- 正文成员 Primary 为 PHOTO 时，Hero 可以复用该成员同一合法 PHOTO source plan；
- 正文成员 Primary 为 LIVE_2S 或 VIDEO_5S 时，只要同一 resolved EvidenceAnchor 的 PHOTO eligibility 合法，可以规划一个静态 Hero cover frame；
- 静态 Hero cover 不把正文 Primary 从 LIVE/VIDEO 改成 PHOTO；
- 它不等于 Fallback activation，也不占用 MediaDecision 的 0–2 条 runtime Fallback Route；
- 它不能越出该 Beat、Anchor、RawAsset/source scope 或 claim-compatible Evidence；
- B1 PHOTO eligibility 失败或 unresolved 时，不能为做封面强行截取不合法 Frame。

`HeroPhotoRepresentationPlan` 是同一已选内容成员的 presentation derivative，不是新的媒体候选。S10 只输出精确引用与计划；S13 才在需要时取回 HQ source 并渲染，S10 不提前下载或生成封面。

### 28.3 不允许的 Hero 来源

- 未进入 `ChapterMediaSetDecision` 的漂亮候选；
- 与 selected Hero member 不同 Beat 的替代画面；
- 只提供地点气氛、但没有成为正文成员的 CONTEXT_ONLY 素材；
- 同一主题但属于另一个 Chapter/Aha 的媒体；
- 为封面重新搜索全天、调用模型创造的新 Anchor；
- AI 生成、跨素材拼接、改变事实的修图或没有 provenance 的合成图；
- 仅因 Manual、人物脸部、色彩鲜艳或模型美学分高而越过成员约束的素材。

### 28.4 Dynamic Hero 边界

LIVE_2S Hero、VIDEO Hero、自动播放封面或动态轮播不进入 V1 默认合同。它们只能在后续独立实验中，经过稳定性、渲染性能、耗电、流量、首屏加载与用户体验验证后再决定是否开放。

即使未来开放 Dynamic Hero，也不能改变“Hero 必须绑定已选正文成员、不得成为额外内容项、不得改写时间线”的身份原则。

### 28.5 案例

1. **生日 VIDEO Hero：** “吹蜡烛”已作为 VIDEO_5S 正文成员入选，可以使用同一 EvidenceAnchor 的静态吹蜡烛 Frame 做 Hero；正文仍播放五秒视频。
2. **后段塔楼 Hero：** 塔楼照片最能代表古镇 Chapter，可以成为封面；展开后仍按真实时间排在牌坊和寺庙之后。
3. **未入选奶茶照片：** 奶茶画面很漂亮，但未进入古建筑 Chapter media set，不能作为该 Chapter Hero。
4. **Compact Chapter：** 制作过程与成品两项中选择一个做 Hero，不能另外加入第三张“工作室环境照”。
5. **动态项无合法 PHOTO：** 某 VIDEO_5S 的 PHOTO eligibility 已失败，不能强截一帧做 Hero；它仍可作为正文成员，Hero 候选需从其他已选成员产生。
6. **同一封面跨表面出现：** Chapter 卡片显示 Hero，打开后同一内容身份仍出现在正文时间线中；算法只计一个媒体成员，不视为重复选入。

### 28.6 输出

~~~text
ChapterHeroCandidateInventory
  selected_memory_ref
  revision_ref
  chapter_media_set_decision_ref
  chapter_media_order_decision_ref
  hero_candidates[]
    selected_media_decision_ref
    content_beat_ref
    evidence_anchor_ref
    body_primary_format
    hero_surface_format = PHOTO
    hero_photo_eligibility_ref
    hero_photo_source_plan_ref
    hero_candidate_state =
      ELIGIBLE
      | INELIGIBLE
      | UNRESOLVED
    limitation_refs[]
  excluded_nonmember_refs[]
  inventory_state
  policy_and_signal_versions
  construction_audit
~~~

### 28.7 Invariants、成本与边界

1. 每个 Chapter 最多一个最终 Hero identity；
2. Hero identity 必须来自最终 media set，不能引入额外内容成员；
3. Hero 静态 representation 必须留在同一 Beat 与 EvidenceAnchor；
4. Hero 不改变正文 Primary format、Fallback state、媒体数量或时间顺序；
5. Hero cover plan 不计入 runtime Fallback Route 上限，但仍须满足 format/source/provenance/claim contracts；
6. S10-C3.2.1 不决定哪个合法成员最终胜出，也不决定无合法 Hero 时的发布处理；
7. 本项不新增模型调用、上传、HQ 请求或渲染；最多为最终一个 Hero 向 S13 输出一个同源静态 representation plan；
8. 本项不修改 App、Firmware/SDK 或共享状态文件。

## 29. 下一检查点

进入 S10-C3.2.2：在合法 Hero candidates 中定义选择层级、跨 Revision 稳定性与“没有理想封面”时的处理。核心产品问题是 Hero 应优先代表 Chapter 的核心意义，还是优先选择视觉上最漂亮的已选媒体。

## 30. S10-C3.2.2｜Meaning-First Hero Selection 与 Hero Availability Gate

**状态：CONFIRMED**

Hero 采用分层比较，不计算一个可以让美感补偿真实性或核心意义的 overall score。V1 原则是：

~~~text
Chapter core meaning first
→ standalone recognizability
→ memorable central content
→ presentation quality
→ execution robustness
→ revision stability
~~~

纯视觉美感只能在前面的意义层近似等价时决定胜负。

### 30.1 HeroPreEligibility：避免 C2 选完才发现没有封面

C2 最终集合搜索前，先基于已经存在的 A2/B1/B3 metadata 为每个 selectable MediaDecision 生成轻量 `HeroPreEligibilityCard`。它不选择 Hero，只判断该成员是否可能满足 V1 静态封面最低合同。

执行顺序必须明确为：

~~~text
A2 / B1 / B3 per-candidate metadata
→ lightweight HeroPreEligibility feasibility prepass
→ C2 complete-set search and target-size decision
→ C3.1 chronology
→ C3.2 final Hero inventory / winner / passive alternate
~~~

Prepass 只验证同一 Anchor 的 PHOTO eligibility 与 source-plan feasibility，不为所有候选生成完整 HQ/render plan。只有最终 Primary Hero 与最多一个 Passive Alternate 才输出完整静态 representation plan，避免形成 C2↔C3 循环依赖或候选级计划膨胀。

~~~text
HeroPreEligibilityCard
  media_decision_ref
  content_beat_ref
  evidence_anchor_ref
  membership_scope_validity
  hero_core_relation =
    DIRECT_CORE
    | CORE_REPRESENTATIVE
    | CONTEXT_ONLY
    | INCOMPATIBLE
    | UNKNOWN
  standalone_understandability
  photo_eligibility_ref
  claim_compatibility
  presentation_usability
  exact_source_plan_feasibility
  hero_preeligibility = PASS | FAIL | UNKNOWN
  reason_refs[]
  policy_and_signal_versions
~~~

`PASS` 必须同时满足：

1. 该媒体本来就是当前 Chapter 的合法 selectable member；
2. Hero 与 Chapter core 的关系为 `DIRECT_CORE` 或 `CORE_REPRESENTATIVE`；
3. 脱离前后媒体后仍可独立理解，不会把外围内容误装成 Chapter 主题；
4. 同一 Beat/EvidenceAnchor 的 PHOTO eligibility、claim compatibility 与 source-plan feasibility 均合法；
5. 静态画面至少达到 Hero minimum usability floor。

`CONTEXT_ONLY`、`UNKNOWN`、无法合法生成 PHOTO 或只在动态中才可理解的成员不能计为 PASS。

每个 Compact/Standard Chapter set 至少需要一个 `HeroPreEligibility=PASS`。这是 C2 hard constraint，只保证“存在一个真实可用的封面”，不比较哪个更漂亮，也不允许封面偏好覆盖 C2.2 的核心成员选择层级。

### 30.2 Hero 候选 hard gate

集合确定后，C3.2.1 Inventory 中的最终 Hero candidate 仍须逐项通过：

1. 仍属于当前最终 media set；
2. Beat、Anchor、PHOTO source plan 与 Revision fingerprint 未失效；
3. 直接或充分代表 Chapter core；
4. 单独显示时主体、事件或代表性对象可理解；
5. 不依赖超出 Evidence 的裁切、猜测或 Narrative 才成立；
6. 达到静态封面 minimum usability；
7. 没有 outcome-changing UNKNOWN、policy/claim conflict 或 provenance invalid。

只有通过 hard gate 的候选进入分层比较。漂亮但主题错误的画面不能进入候选池后再靠低权重惩罚。

### 30.3 分层选择目标

#### Layer 1｜Legality / Truth / Scope

Hero 必须真实、合法、属于 selected set，并能从同一 EvidenceAnchor 生成静态封面。任一 hard failure 直接淘汰。

#### Layer 2｜Chapter Core Representativeness

优先选择用户只看封面也能正确理解 Chapter 核心的候选。核心动作、核心对象、代表性地点或结果优先于漂亮的外围环境。

#### Layer 3｜Standalone Recognizability 与 Specificity

在不依赖前后内容时，优先主体清楚、事件明确、具有该 Chapter 特异性的画面。过于局部、容易误解或换到其他 Chapter 也成立的通用画面降低优先级。

#### Layer 4｜Central / Memorable Content

前三层近似时，再比较 grounded event centrality、关键互动、动作 peak、结果、代表性实例与记忆辨识度。不存在固定“结果一定优先”“人物脸一定优先”或“Manual 一定优先”。

#### Layer 5｜Presentation Quality

再比较清晰度、主体可见性、构图可理解性、曝光、遮挡、稳定性与已知封面裁切安全性。略暗但真实表达核心的可用画面，可以胜过高清但外围的静物。

#### Layer 6｜Source / Render Robustness

意义与画质近似时，优先 source plan 更确定、source readiness 更高、失败域更独立且渲染限制更少的候选。

#### Layer 7｜Cross-Revision Hero Stability

若上一成功发布 Revision 的 Hero member 在当前集合中仍存在、仍合法，且与当前最佳候选属于 policy-defined near-equivalent，则保留旧 Hero。只有核心表达、独立可理解性或画面质量存在 material gain 时才替换。

#### Layer 8｜Deterministic Tie-break

仍近似相同时使用 canonical Beat time、stable content identity 与固定 policy tie-break，保证相同输入与版本得到相同 Hero。

### 30.4 没有“理想封面”与没有“合法封面”必须分开

#### 至少一个合法，但都不完美

若至少一个候选通过 minimum gate，只是存在轻微偏暗、构图普通或其他非致命限制：

- 选择分层比较后的最佳合法候选；
- 输出 `HERO_READY_WITH_LIMITATION`；
- 正常发布，不因轻微美学差距重选 Memory；
- 不为寻找更漂亮封面扩大搜索或请求用户重新上传。

#### 当前 set 没有 Hero PASS，但同一 Memory 还有其他合法 set

C2 solver 淘汰无 Hero coverage 的集合，继续比较同一 selected Memory 的其他合法 2–5 项组合。这不是 S09 re-selection，也不增加 S10 attempt；它属于一次 C2 完整集合搜索。

#### 当前 Memory 的所有完整 set 都已证明没有合法 Hero

记录：

~~~text
PROVEN_MEDIA_INSUFFICIENCY
reason = HERO_CONTRACT_UNSATISFIED
~~~

该失败进入 C1.3 同一批次、同一次有界 S09 re-selection，不获得额外第二次机会。不得使用未入选素材、随机占位图、无 provenance 合成图或用户再次上传来补封面。

#### 仍有 UNKNOWN 或 contract invalid

- outcome-changing `UNKNOWN`：`HERO_AVAILABILITY_UNRESOLVED`，HOLD/BLOCK，不得伪装成 proven insufficiency；
- policy、lineage、Revision、claim 或 provenance invalid：走 contract-invalid 路径，不得换候选掩盖；
- re-selection exhausted 后仍 proven fail：遵循 C1.3 保留仍合法的上一成功 Revision，或无 prior 时 blocked/no-publishable。

### 30.5 Cross-Revision 行为

1. prior Hero 已不属于当前 media set 时不能继续作为 Hero；
2. prior Hero 仍是合法成员且质量近似时保持，避免每次 Sync 后无意义换封面；
3. 新增候选带来 material core/clarity/quality gain 时允许替换；
4. Hero 替换不改变 Memory stable identity、正文成员身份或 C3.1 时间顺序；
5. prior Hero 的 Evidence、policy 或 source 已失效时不得以“稳定”为由继续保留。

### 30.6 案例

1. **生日：** 略暗但仍清楚的吹蜡烛画面直接表达核心，优先于非常漂亮的蛋糕静物。
2. **古建筑：** Chapter 核心为整体游览时，代表性大殿外观通常优先于孤立木雕细节；若 Chapter core 本来就是木雕工艺，木雕细节可以优先。
3. **咖啡聚会：** 朋友交谈的可理解画面优先于精致咖啡杯；若 Chapter core 是咖啡拉花体验，则拉花成品可成为核心 Hero。
4. **同义候选：** 两张都直接表达塔楼并可独立理解时，选择更清晰、构图更适合封面的那张。
5. **跨 Revision：** 新照片只稍微更亮而意义相同，保持 prior Hero；新增此前缺失的核心互动画面时允许替换。
6. **不理想但可用：** 唯一核心 Hero 略有噪点但主体清楚，输出 `HERO_READY_WITH_LIMITATION`，不因美学不完美重选整个 Chapter。
7. **零合法 Hero：** 三个正文动态项都无法产生 claim-compatible 静态封面，当前 set 失败；若同一 Memory 存在包含合法静态 Hero 的其他三项 set，则 C2 选择后者。
8. **UNKNOWN：** Hero source handle 暂时状态未知，不能把它写成内容不足后排除 Memory，当前 Revision HOLD/BLOCK。

### 30.7 输出

~~~text
ChapterHeroDecision
  selected_memory_ref
  revision_ref
  chapter_media_set_decision_ref
  chapter_media_order_decision_ref
  hero_candidate_inventory_ref
  selected_hero_member_ref
  selected_hero_beat_ref
  selected_hero_anchor_ref
  hero_photo_representation_plan_ref
  passive_alternate_hero_plan_ref
  hierarchical_comparison_trace
  prior_revision_hero_trace
  rejected_hero_candidate_refs[]
  hero_limitation_refs[]
  hero_decision_state =
    HERO_READY
    | HERO_READY_WITH_LIMITATION
    | HERO_PROVEN_UNAVAILABLE
    | HERO_AVAILABILITY_UNRESOLVED
    | HERO_CONTRACT_INVALID
  policy_and_signal_versions
  decision_trace
~~~

### 30.8 Invariants、成本与边界

1. Hero 美感不能补偿错误主题、外围内容或 Evidence 不足；
2. HeroPreEligibility 只提供 set viability，不能变成 C2 的美学排序捷径；
3. 没有理想封面不等于没有合法封面；轻微美学不足不能触发 S09 re-selection；
4. 只有全部合法 set 已证明违反 Hero contract 才能记录 proven insufficiency；
5. UNKNOWN、contract invalid 与 operational failure 不能触发候选替换；
6. Hero selection 不改变正文集合、时间顺序、正文格式或 Memory identity；
7. 本项只复用已有 metadata，不新增模型调用、上传、HQ 请求或渲染；
8. 本项不决定 Hero source/runtime 失败后的备用封面激活顺序。
9. 只有 exhaustive/deterministic set search 已证明所有合法集合均无 Hero PASS 时才是 proven insufficiency；budget、timeout 或搜索未完成仍属于 operational/UNKNOWN。

## 31. 下一检查点

进入 S10-C3.2.3：定义 Hero 静态源或渲染失败时是否预先准备一个备用 Hero、备用数量，以及切换是否允许改变 Hero 所绑定的正文成员。

## 32. S10-C3.2.3｜Passive Alternate Hero Reference

**状态：CONFIRMED**

真正的源文件损坏应是低频异常，临时网络、上传等待或渲染超时也不能被误写成内容失败。S10 因此不建设独立的重型 Hero 容灾链，只为最终 Hero 保存最多一个被动备用引用：

~~~text
1 Primary Hero
+ 0 or 1 Passive Alternate Hero Reference
~~~

备用引用只包含已经计算完成的候选身份、静态封面计划与激活条件。它不提前上传、不提前请求 HQ、不提前渲染，也不产生额外模型调用。

### 32.1 备用候选范围

Passive Alternate 必须：

1. 来自同一 Chapter 最终 media set；
2. 已在 C3.2.1 Inventory 中为 `ELIGIBLE`；
3. 通过 C3.2.2 全部 Hero hard gate；
4. 在排除 Primary 后，按同一 meaning-first hierarchy 选择；
5. 在语义与画质近似时，优先与 Primary 位于不同 Source Family/source failure domain；
6. 保持静态 PHOTO、同一候选自身的 Beat/EvidenceAnchor 与合法 source plan；
7. 没有合格候选时允许为零，不能为凑备用降低 Hero floor。

备用可以绑定另一个已选正文成员；切换只改变封面身份，不增加正文项、不改变 Chapter media set，也不改变 C3.1 时间顺序。

### 32.2 临时失败不得激活备用

以下状态不触发 Hero 切换：

- transient network/provider timeout；
- HQ source 尚在正常无感上传队列；
- 一次性 decode/render/encode timeout；
- source readiness、policy 或 failure cause 仍为 `UNKNOWN`；
- budget、worker 或服务暂时不可用。

这些状态由 S13/基础设施重试或进入 HOLD；S10 不把它们解释为 Primary Hero 已永久失败，也不改变已发布 Hero。

重试次数、上传队列、checksum、atomic write、持久化确认与本地清理规则仍属于后续上传架构/S13 工程合同，不在 S10 假定具体数值。

### 32.3 允许激活的终止条件

Passive Alternate 只在 Primary 已被确定为不可继续使用时激活，例如：

- source terminal unavailable；
- integrity/checksum 已证明失败且无法从合法来源恢复；
- 文件已证明不可解码，而不是单次处理超时；
- Primary Hero 的 Evidence、claim、policy 或 provenance 资格被确定撤销；
- Hero 静态计划已被证明永久不可执行。

激活使用 S10 已保存的单一 alternate ref，不重新搜索、不重新排名、不调用模型，也不临时引入其他 selected/unselected member。

### 32.4 不能掩盖正文媒体失败

Hero alternate 只解决封面问题，不能掩盖正文项已经不可发布：

1. Primary Hero 对应正文成员的 MediaDecision 仍按 B3/S10-D 的自身 Route/Fallback 合同处理；
2. 只有正文集合在 route resolution 后仍满足 Compact/Standard 数量、去重、Hero coverage 与其他 hard constraints，才可切换封面后继续发布；
3. 若同一 source failure 同时使正文集合低于合法容量，必须走 Chapter 原子失败/HOLD/BLOCK，不能只换 Hero 假装 Chapter 完整；
4. Passive Alternate 不构成新的正文 Fallback Route，也不占用 B3 每个 MediaDecision 的 Route 上限。

### 32.5 Alternate 也不可用时

- 不尝试第三个 Hero；
- 不从未入选素材、CONTEXT_ONLY、其他 Memory 或全天池中补图；
- 不使用随机占位图或无 provenance 合成图伪装成功；
- 运行时/上传侧的新故障不触发新的 S09 re-selection；
- 继续遵守原子发布：保留仍合法的上一成功 Revision；无 prior 时保持 blocked/no-publishable。

若失败在原始 S10 batch 完成前已经被证明，则应回到既有 C1.3 分类，而不是等到运行时再伪装成 alternate exhaustion。

### 32.6 案例

1. **生日 Primary 永久丢失：** 吹蜡烛 Hero 的源文件已证明不可恢复，合照是已选成员且为被动备用；正文 Route 仍完整时可无感切换到合照。
2. **一次渲染超时：** 塔楼 Hero 首次生成超时，状态仍 transient；不能立即换成寺庙，先由 S13 重试或 HOLD。
3. **Compact Chapter：** 制作过程为 Primary、成品为唯一合法 Alternate；Primary terminal failure 且正文 Pair 仍合法时可以换封面。
4. **无合法备用：** 只有一个成员达到 Hero floor，备用为空；不恢复漂亮但外围的工作室照片。
5. **共同故障域：** Primary 与候选备用均来自同一 RawAsset，而另一个近似等价 Hero candidate 来自独立 RawAsset；优先独立来源候选作为备用。
6. **正文同时失效：** Primary source 丢失也使三项 Chapter 只剩两项，且 Compact Pair 不成立；即使备用 Hero 可用，也不能发布残缺 Chapter。
7. **上传尚未完成：** HQ source 仍在正常后台上传，不属于 terminal failure；保持 Primary 计划，不激活备用，也不要求用户再次 Sync。

### 32.7 输出

~~~text
PassiveAlternateHeroPlan
  selected_memory_ref
  revision_ref
  chapter_hero_decision_ref
  primary_hero_member_ref
  alternate_hero_member_ref          # optional, max one
  alternate_hero_anchor_ref          # optional
  alternate_photo_plan_ref           # optional
  primary_and_alternate_source_domains
  activation_allowed_terminal_classes[]
  activation_forbidden_transient_classes[]
  body_set_validity_dependency_ref
  alternate_plan_state =
    ALTERNATE_READY
    | NO_QUALIFIED_ALTERNATE
    | ALTERNATE_UNRESOLVED
    | ALTERNATE_CONTRACT_INVALID
  policy_and_signal_versions
  decision_trace
~~~

### 32.8 Invariants、成本与边界

1. 每个 Chapter 最多一个 Passive Alternate Hero Reference；
2. Primary 与 Alternate 均来自最终 media set；
3. Alternate 不提前上传、取回、渲染或调用模型；
4. transient/UNKNOWN 不得触发切换，只有 proven terminal condition 可以；
5. 激活时不重新搜索或排名，失败后也没有第三候选；
6. Alternate 不能掩盖正文容量、Route、重复或完整性失败；
7. 正常路径只有一个 Hero render；只有真实终止失败时才可能增加一次备用 HQ/渲染处理；
8. 本项不冻结 App 上传实现、S13 retry 数值、云存储生命周期或用户可见失败 UI。

## 33. S10-C Closeout 与下一检查点

**状态：FROZEN BY CANONICAL V1.21**

S10-C 已完成 Chapter 的 Compact/Standard 容量、最终 2–5 项集合、自适应数量、同源占位、真实时间线、静态 Hero、意义优先 Hero 选择，以及一个零预处理成本的被动备用引用设计。

内部交叉检查以 36 个边界案例与 5 类用户素材画像覆盖长短 Manual、Dominant Motif、Preview/Final、Fallback、Hero、时间线与异常分类，并应用四项接口修正：

1. HeroPreEligibility 明确为 C2 前的轻量 feasibility prepass；
2. 完整 Hero plan 只为 Primary 与最多一个 Passive Alternate 生成；
3. target size 必须在全部 set hard constraints 后确定；
4. 搜索未完成不得伪装为 proven Hero insufficiency。

完整记录见 `S10_C_CHAPTER_EDITORIAL_INTERNAL_CROSS_CHECK_V0_1.md`。S10-C 已参加并通过 S10-E 全阶段综合检查，并由 Canonical V1.21 冻结。

下一步进入 S10-D 前，先确认正文单项的全部 Route 在运行时永久失败时，是否允许不重新搜索、直接降为已经验证过的较小 survivor set。

## 34. S10-D1｜Single-Loss Survivor Set

**状态：CONFIRMED**

S10-D1 处理一种有界的发布前异常：C2 已经确认最终 Chapter media set，但在 S13 HQ materialization/render 完成、当前 Revision 原子发布之前，恰好一个正文成员的全部预声明 Route 被证明永久不可用。

V1 允许删除这一项，并只在“原集合减去该项”的精确 survivor set 已提前验证为完整合法时，无感发布较小 Chapter：

~~~text
5 → 4  Standard survivor
4 → 3  Standard survivor
3 → 2  only a prevalidated Compact Pair survivor
2 → 1  forbidden
~~~

它不搜索替代媒体、不引入新成员、不重新进入 S09，也不允许连续删除第二项。

### 34.1 Precomputed Single-Loss Survivor Ledger

C2/C3 完成后，针对最终 set 中每个成员分别验证一次“如果仅该成员永久失败，剩余精确集合是否仍可发布”。最终 set 最多五项，因此最多检查五个子集。

每个 survivor 必须重新通过：

1. 剩余成员全部属于原 final set、同一 Memory/Revision/S10 attempt；
2. count 为 3–4 时通过 Standard Chapter 全部 hard constraints；
3. count 为 2 时通过 C1.2 Compact Pair、same-source、Fallback pair 与 Hero gates；
4. Chapter core coverage 仍完整，删除项不是不可替代核心；
5. 每个剩余成员仍有 material contribution；
6. 无 presentation redundancy、canonical collision、alternative-group 或 co-selection conflict；
7. C2.3 source occupancy 仍合法；
8. 至少一个剩余成员为 Hero PASS；
9. C3.1 时间线可通过删除原位置后稳定压缩，不重新排序；
10. policy、claim、lineage、source-plan 与 version fingerprints 完整匹配。

该 Ledger 只使用已有 metadata，不请求 HQ、不渲染、不调用模型。

### 34.2 激活条件

Single-Loss Survivor 只有同时满足以下条件才可激活：

1. 恰好一个正文 `MediaDecision` 的 Primary 与全部预声明 Fallback Route 均为 proven terminal failure；
2. 对应 member 的 survivor entry 已为 `SURVIVOR_PASS`；
3. 其他成员没有 outcome-changing UNKNOWN、第二个 terminal failure 或 contract invalid；
4. 当前 set/route/policy/source fingerprints 与 Ledger 计算时一致；
5. 当前 Revision 尚未向用户原子发布；
6. 本 Revision 尚未使用过 single-loss survivor activation。

Primary Route 单独失败但同成员仍有合法 Fallback 时，优先执行原 MediaDecision Fallback，不删除正文成员。只有该成员全部 Route 用尽并被证明 terminal，才进入 D1。

### 34.3 禁止触发的状态

- transient network/provider/decode/render timeout；
- source 尚在正常无感上传或 HQ materialization 队列；
- source、failure cause、policy 或 route state 为 `UNKNOWN`；
- budget/worker 暂时不可用；
- input、Revision、lineage、claim、provenance 或 policy contract invalid；
- 两个及以上正文成员同时或先后全部 Route terminal failed；
- 当前 Revision 已经成功发布后发生的存储事故。

这些状态不能靠删除正文项伪装成功。transient/UNKNOWN 走 retry/HOLD，contract invalid 走 BLOCK；发布后的长期存储与恢复属于 S13/云存储合同。

### 34.4 激活后的集合行为

1. survivor members 恰好等于原 final set 减去失败成员；
2. 不从 MediaDecisionInventory 中补入第六候选、未入选候选或 CONTEXT_ONLY；
3. 原有相对时间顺序保持，只移除失败位置并压缩 index；
4. 若失败成员不是 Hero，保持原 Hero；
5. 若失败成员是 Primary Hero，只能使用仍在 survivor set 内的 C3.2.3 Passive Alternate；没有合法 Alternate 时该 survivor entry 必须为 FAIL；
6. 若失败成员恰好是 Passive Alternate，而 Primary Hero 仍合法，可以删除 Alternate 后发布，不再补另一个备用；
7. final target size 与 layout state 更新为 4、3 或 Compact 2，但不改变 Memory stable identity；
8. 用户不看到空位、“降级”、失败项或中间五项版本，最终结果一次性原子出现。

### 34.5 第二项失败与链式缩减

V1 每 Revision 最多一次 single-loss activation：

- 激活 survivor 后若第二个成员也 terminal failed，不继续 5→4→3 或 4→3→2；
- 不预计算双成员失败组合；
- 不临时搜索替代者；
- 保留仍合法的上一成功 Revision，无 prior 时 `BLOCKED_NO_PUBLISHABLE_REVISION`。

这一上限避免罕见基础设施异常把内容算法变成复杂的组合容灾系统。

### 34.6 与 C1.3 有界 S09 re-selection 的边界

- 若全部 Route failure 在原始 S10 batch 完成前已知，应进入正常 MediaDecision/C2 计算或 C1.3 failure batch，不使用 D1；
- D1 只处理 S10 finalization 后、原子发布前新出现的单成员 terminal failure；
- D1 激活失败不新增 S09 re-selection 机会；
- 已用过 C1.3 唯一 re-selection 的 Revision 也仍可使用一次 D1，因为二者处理不同时间点，但 D1 不能引入任何新 Candidate 或成员。

### 34.7 案例

1. **五项生日：** 准备蛋糕 terminal failed，剩余点蜡烛、吹蜡烛、鼓掌、合照仍完整且有 Hero，激活 5→4。
2. **四项古建筑：** 普通石板路 terminal failed，剩余牌坊、寺庙、塔楼仍表达核心，激活 4→3。
3. **核心项失败：** 四项中唯一直接表达活动核心的媒体失败，剩余三项只有环境，survivor FAIL，当前 Revision HOLD/BLOCK。
4. **三项陶艺：** 准备过程失败，剩余拉坯＋成品已经通过 Compact Pair 与 Hero gates，可激活 3→2。
5. **三项相似照片：** 一项失败后，剩余两项为同一建筑近似角度，Compact Pair FAIL，不能发布。
6. **Primary Route 失败：** VIDEO Primary 失败但同 Beat PHOTO Fallback 合法，激活 Fallback，仍为原数量，不进入 D1。
7. **上传等待：** 一个 HQ source 尚在后台队列，状态不是 terminal，不能删掉该项提前发布。
8. **Hero member 失败：** Passive Alternate 位于 survivor set 且仍合法，可同步切换封面；没有 Alternate 时 survivor FAIL。
9. **第二项失败：** 五项已激活 5→4 后又一成员 terminal，停止，不继续缩成三项。
10. **已发布后云文件事故：** 不使用 D1 静默修改已发布内容，交由持久化与恢复合同处理。

### 34.8 输出

~~~text
SingleLossSurvivorLedger
  selected_memory_ref
  revision_ref
  original_chapter_media_set_ref
  original_target_size
  survivor_entries[]
    assumed_failed_media_decision_ref
    exact_survivor_media_decision_refs[]
    survivor_count
    survivor_layout_state = STANDARD | COMPACT | INVALID
    hard_constraint_audit_refs[]
    compact_pair_decision_ref
    survivor_hero_ref
    order_projection_ref
    survivor_state =
      SURVIVOR_PASS
      | SURVIVOR_FAIL
      | SURVIVOR_UNRESOLVED
      | SURVIVOR_CONTRACT_INVALID
    reason_refs[]
  policy_and_signal_versions
  ledger_fingerprint

SingleLossSurvivorActivation
  revision_ref
  failed_media_decision_ref
  all_routes_terminal_evidence_refs[]
  survivor_ledger_entry_ref
  activated_survivor_set_ref
  hero_change_ref
  activation_count                 # exactly 1
  activation_state
  atomic_publish_impact
  decision_trace
~~~

### 34.9 Invariants、成本与边界

1. 只允许一个正文成员、一次 survivor activation；
2. survivor 只能是原 set 的精确子集，不补新成员；
3. transient/UNKNOWN/contract invalid 不得触发删除；
4. 5→4、4→3 必须重新通过 Standard hard constraints，3→2 必须通过 Compact gates；
5. Hero、顺序、source occupancy 与 core coverage 必须随 survivor 重新验证；
6. 用户只看到一个完整、原子发布的最终集合；
7. 最多检查五个 metadata 子集，不新增模型、上传、HQ 请求或渲染；
8. 本项不处理正文 Route activation collision、HQ 请求调度、Aha supporting item 或发布后存储恢复。

## 35. 下一检查点

进入 S10-D2：当某个正文 Primary 切换 Fallback 后，与其他健康 Primary 或另一个 Fallback 指向同一 canonical render 时，定义谁保留、谁跳过，以及是否进入 D1 survivor path。

## 36. S10-D2｜Deterministic Route Activation Collision Resolution

**状态：CONFIRMED**

`canonical render collision` 指两个不同正文位置在 Route 激活后会展示同一张照片、同一 source interval 或等价的最终画面。S10-B 已在 `route_collision_matrix_ref` 区分：

~~~text
PRIMARY_PRIMARY
PRIMARY_FALLBACK
FALLBACK_FALLBACK
~~~

`PRIMARY_PRIMARY` 已是 C2 hard conflict，不能进入 final set。D2 只处理发布前 Primary 合法失败后可能出现的 `PRIMARY_FALLBACK` 与 `FALLBACK_FALLBACK`。

V1 核心原则是：健康 Primary 不因另一个成员失败而被移动、降级或替换。

### 36.1 先分类失败，再进入 collision resolution

D2 不自行判断 Route 是否应该激活。只有 B3/S13 已把 Primary failure 分类为允许切换的确定状态后，D2 才解决激活组合：

- transient/UNKNOWN：不激活 Fallback，也不进入 collision resolution；
- known format/anchor/source failure 且存在合法预声明 Fallback：进入 D2；
- contract invalid：BLOCK，不尝试用 Route 组合掩盖；
- Primary 仍健康：锁定为 `HEALTHY_PRIMARY_LOCKED`。

### 36.2 Phase 1｜锁定健康 Primary

所有仍健康的 Primary Route 先进入 immutable active set：

1. Fallback 与健康 Primary canonical collision 时，健康 Primary 保留；
2. 冲突 Fallback 标记 `SKIPPED_COLLIDES_WITH_HEALTHY_PRIMARY`；
3. 失败成员继续尝试自己的下一条预声明 Fallback；
4. 不允许把健康 Primary 切换到自身 Fallback，为另一个成员腾出画面；
5. 不改变健康 Primary 的格式、Anchor、source、Hero 身份或时间线位置。

这避免一个局部故障引发多个正常正文位置连锁变化。

### 36.3 Phase 2｜Fallback 组合搜索

对 Primary 已合法失败的成员，只在各自现有、按 B3 固定顺序排列的 Fallback Route 中寻找与健康 Primary 及其他 Fallback 无冲突的组合。

组合必须同时满足：

1. 每个成员最多激活一条 Route；
2. 不存在 canonical render collision；
3. 不越出原 Beat/Anchor/Evidence/claim scope；
4. active realization 继续满足 C2.3 source occupancy；
5. Compact Pair 的 relation/core/Hero 仍成立；
6. Chapter order 继续绑定原 ContentBeat，不因 source time 改变；
7. 所有 Route 均来自原不可变 MediaDecision，不能临时生成第四 Route。

若存在保留全部正文成员的组合，按以下层级选择：

~~~text
1 keep all media members
2 keep all healthy Primaries locked
3 fewer / shallower Fallback activations
4 B3 predeclared Route order
5 stronger source/failure-domain robustness when near-equivalent
6 stable identity tie-break
~~~

不得在运行时重新调用模型或重新计算内容价值总分。

### 36.4 无法保留全部成员时

若全部无冲突 Route 组合都无法保留所有正文成员：

1. 最多允许一个成员进入 `ALL_ROUTES_EXHAUSTED_BY_FAILURE_OR_COLLISION`；
2. 只有对应 D1 `SingleLossSurvivorLedger` entry 为 PASS，才能删除该成员并原子发布 survivor；
3. 多个可能删除对象时，按下列保护层级决定谁保留：
   - 保护删除后没有合法 survivor 的成员；
   - 保护唯一直接 Chapter core member；
   - 保护唯一合法 Hero member；
   - 比较 C2 已有 material deletion loss 与 representative coverage，不新增 overall score；
   - 仍等价时使用 stable content identity tie-break；
4. 两个成员都将 Route exhausted、或所有单成员 survivor 均 FAIL/UNKNOWN 时，HOLD/BLOCK；
5. 不通过移动健康 Primary、引入未选成员或运行时搜索来强行保住数量。

上述层级只在已经无法保留全部成员时使用；不能为了偏好某个成员，放弃本来存在的全成员无冲突组合。

### 36.5 Hero、顺序与 Revision 行为

- Route activation 不改变 C3.1 canonical Beat order；
- Hero 的正文 member 仍存在时保持 Hero identity，静态 cover plan 独立按 C3.2 合同处理；
- 若成员因 D1 被删除且它是 Primary Hero，只能切换到仍在 survivor 中的 Passive Alternate；
- Fallback activation 与 survivor activation 均生成新的不可变 activation artifact，不原地改写原 MediaDecision、ChapterMediaSetDecision 或 HeroDecision；
- 用户只看到最终无冲突的完整 Revision，不看到 Route 尝试过程。

### 36.6 多个 Primary 同时失败

多个 Primary 可以同时进入 Fallback 组合搜索，只要每个成员最终找到合法 Route，成员数量不因此受限。

但若组合搜索后有两个及以上成员全部 Route exhausted：

- D1 只允许一次单成员删除，因此当前 Revision 不能继续；
- 不计算双成员 survivor；
- 不按处理顺序先删一个再假装第二个是新故障；
- 保留 prior 成功 Revision或无 prior 时 blocked/no-publishable。

### 36.7 案例

1. **Fallback vs 健康 Primary：** A 的 VIDEO 失败，第一 Fallback 与 B 的健康 PHOTO 为同一画面；锁定 B，跳过 A-F1，尝试 A-F2。
2. **不移动健康项：** B 自身存在另一个 PHOTO Fallback，也不能为了让 A-F1 使用 B-Primary 而主动降级 B。
3. **两个 Fallback 冲突但存在替代：** A-F1 与 B-F1 同为合照，A-F2 为吹蜡烛 PHOTO；选择 A-F2＋B-F1，保留全部成员。
4. **核心项保护：** A/B 只能争用同一 fallback，A 是唯一吹蜡烛核心、B 是辅助蛋糕；删除 B 的 survivor PASS 时保护 A、让 B 进入 D1。
5. **Hero 保护：** B 是唯一合法 Hero，删除 B 后 survivor Hero gate FAIL；若删除 A 的 survivor PASS，则保留 B。
6. **没有合法 survivor：** 两个争用成员任意删除都会损失核心或低于合法容量，HOLD/BLOCK。
7. **Compact Pair：** 两项 Pair 的一个 Fallback 与另一健康 Primary 重复，冲突 Route 跳过；若该成员没有其他 Route，Pair 只剩一项，不能发布。
8. **同时两 Primary 失败但可恢复：** A/B 各找到不同合法 Fallback，仍发布原数量，无需 D1。
9. **同时两成员 exhausted：** 即使五项剩三项看似数量足够，也不做双删除组合，当前 Revision BLOCK。
10. **source occupancy：** 三个 Fallback 虽画面不同，但共同激活会使同一 Source Family 占四项；该组合非法，继续寻找其他 Route。

### 36.8 输出

~~~text
ChapterRouteActivationResolution
  selected_memory_ref
  revision_ref
  original_chapter_media_set_ref
  route_collision_matrix_ref
  healthy_primary_locks[]
  failed_primary_refs[]
  candidate_route_assignments[]
  rejected_assignment_refs[]
  winning_active_routes[]
  skipped_collision_routes[]
  exhausted_member_refs[]
  single_loss_survivor_activation_ref
  hero_activation_impact_ref
  order_projection_ref
  resolution_state =
    FULL_SET_RESOLVED
    | SINGLE_LOSS_SURVIVOR_RESOLVED
    | TRANSIENT_OR_UNKNOWN_HOLD
    | MULTI_MEMBER_EXHAUSTED
    | ACTIVATION_CONTRACT_INVALID
  policy_and_signal_versions
  decision_trace
~~~

### 36.9 成本与确定性

Chapter 最多五个正文成员，每个 MediaDecision 最多一条 Primary 与两条 Fallback。即使枚举全部 route assignments，上界也只有 `3^5 = 243` 个 metadata 组合；健康 Primary 锁定后实际更少。

该搜索：

- 不调用模型；
- 不读取新媒体；
- 不请求 HQ；
- 不重新做 C2 内容选择；
- 相同 failure facts、routes、matrix、policy 与 fingerprints 必须得到相同结果。

### 36.10 Invariants 与边界

1. 健康 Primary 绝不为其他成员 Fallback 让位；
2. collision Route 只能跳过，不能同时激活；
3. 优先寻找保留全部成员的预声明组合；
4. 最多一个成员可进入 D1，两个 exhausted 必须停止；
5. 不能生成新 Route、搜索新素材、调用模型或改写旧 decision；
6. Fallback 不改变正文 Beat identity、顺序或数量计算；
7. D2 不决定 HQ 请求时机、S13 retry 数值、Aha supporting item 或上传工程。

## 37. 下一检查点

进入 S10-D3：定义正文 Primary、正文 Fallback、Hero Primary 与 Passive Alternate 的 HQ source 请求/渲染时机。上传架构尚未冻结，因此本步只能先决定算法应输出哪些 request tiers 与成本边界，不能擅自规定 App 的具体后台上传实现。

## 38. S10-D3｜Final-Media HQ Source Request Tiers

**状态：CONFIRMED**

### 38.1 HQ 在本合同中的准确含义

`HQ` 是 `High Quality Source` 的缩写，本合同中统一解释为：

> 足以生成用户最终可见 PHOTO、LIVE_2S 或 VIDEO_5S 的高清源素材。

它不自动等于：

- 传感器原始 RAW；
- 整段原视频或全天全部素材；
- 已经上传到云存储的文件；
- 直接提交给模型理解的输入；
- 比最终成片所需质量更高的无界源文件。

低成本预览帧、embedding 与证据摘要负责“理解和选择”；HQ source 只负责把已经选定的最终内容做成用户可见成片。S10 只输出请求意图与精确消费范围，实际取源、传输和渲染由下游 S13 执行。

### 38.2 Finalization Gate｜何时才允许产生 HQ 请求

一个 Revision 只有依次完成下列工作，才能输出 HQ request manifest：

1. 该 Revision 中应处理的 Chapter/Aha membership 已由 S09 确定；
2. Chapter provisional hard-valid set/order/Hero 与 D4.1 Aha single-media decision 已完成；
3. 所有 relevant Chapter/Aha pair 均有合法 V1.20 decision，且 D4.2 已选出 winning cross-memory presentation projection 或记录必要复用；
4. 允许的一次 bounded S09 re-selection 已成功结束，或已确认无需进入；
5. winning projection 的 Primary/Fallback Route、D1 survivor ledger、D2 collision plan 与 Hero metadata 已 final/rebuild 并不可变；
6. 当前 Revision 没有 outcome-changing/base-contract unresolved、UNKNOWN 或 contract-invalid 状态；仅影响 D4.2 软近重复判断、且已记录为 `RENDER_RELATION_LIMITATION` 的 UNKNOWN 可以继续；
7. 对所有最终消费项完成 source reuse 与 request coalescing 预检。

因此，S00–S10 的语义理解、候选筛选和集合搜索阶段不得预先请求全部候选 HQ。Finalization Gate 以当前 Revision 为单位，不要求等待全天结束；一次用户无感同步形成的增量 Revision 可以独立完成这一流程。

若用户已经手动完成 Sync，后续 HQ 请求不得再触发第二次上传确认、素材选择或其他新增交互。具体何时在后台传、传到哪里以及网络/电量条件仍属于 App 与上传架构的 OPEN 项，不由 S10 擅自冻结。

### 38.3 四级请求合同

#### TIER_0_REUSE｜已有合法结果直接复用

若相同不可变 source/render fingerprint 已成功 materialize，且其 source、精确 frame/interval、格式、render policy、Revision compatibility 与有效性均匹配，则直接复用：

- 不重复传输；
- 不重复解码或渲染；
- 可跨 Revision 复用未变化且仍合法的最终项；
- 复用事实必须可追溯，不能仅凭“看起来相似”判断。

#### TIER_1_REQUIRED_PRIMARY｜当前发布必须具备

只对当前 active final set 发出立即 materialize 意图：

- 每个正文成员当前激活的 Primary Route；
- 当前 Primary Hero PHOTO；
- Hero 若可从某个正文 Primary 的同一 HQ source 一并生成，不重复请求 source；
- 所有 TIER_1 消费项均属于 `required_to_publish = true`。

#### TIER_2_ON_DEMAND_FALLBACK｜先登记，证明需要时才请求

下列计划只保留 metadata 与 activation predicate，正常情况下不取 HQ：

- 正文 Fallback Route；
- Passive Alternate Hero；
- 已预计算但尚未激活的合法备用 realization。

只有 Primary 出现 B3/S13 已证明的 terminal failure，并经 D2 确认某条 Fallback 成为 active Route 后，才能生成该 Route 的 on-demand request activation。transient、UNKNOWN 或 contract-invalid 状态不得提前拉取 Fallback HQ。

#### TIER_3_NOT_REQUESTED｜不得请求

下列内容不进入最终媒体 HQ 请求：

- 未入选 Candidate；
- CONTEXT_ONLY 与 DROP；
- 已被 B3 排除、失效或未进入预声明 Route 的备选 realization；
- 仅用于 D1 预计算的 survivor variant；
- 同一时间段或全天候选池的其他素材；
- 仅为“也许以后有用”而保留的额外源文件。

合法但尚未激活的 Fallback 与 Passive Alternate 仍属于 TIER_2，不得误归为 TIER_3。TIER_3 也不决定本地原始素材的保存或删除；它只表示“本 Revision 的最终成片算法没有请求它”。

### 38.4 Source coalescing 与最小充分范围

同一 RawAsset 被多个最终消费项引用时，应先尝试合并 source request，再决定实际传输：

1. 同一精确 PHOTO frame 可以共享一次合法 materialization；
2. 同一视频中重叠或相邻 interval 可以携带 `coalescing_key`，供 S13/上传调度器判断是否一次取源更省；
3. 正文 VIDEO 与同源 Hero PHOTO 可以共享 source fetch，再各自生成不同最终 render；
4. consumer 的语义范围仍分别记录，不能因为合并请求而扩大其 Evidence/claim scope；
5. 不得为了工程方便默认上传整段、整小时或全天源素材；
6. 若底层只支持取完整 source object，S13 可以报告该能力事实，但不能反向改变 S10 的最小必要消费范围。

S10 输出的是“需要哪一帧/哪一时间段、用于哪个最终位置、需要什么格式”的精确意图。实际传输是否裁片、整文件复用、先入云存储还是直接进入媒体服务，留给后续上传架构统一决定。

### 38.5 失败后的增量激活与原子发布

TIER_1 请求发出后：

1. transient failure：由 S13 按其 retry policy 处理，当前 Revision HOLD；
2. Chapter member 的 proven terminal failure：只激活下一条预声明 TIER_2 Route，并进入 D2 collision resolution；
3. Aha 的 proven terminal failure：只按既有 Route order 激活下一条同 peak TIER_2 Route；若因此与 Chapter media 发生 exact/material overlap，沿用 D4.2 runtime necessary-reuse 规则，不进入 Chapter D2；
4. 一个 Chapter member 全部 Route exhausted：只允许进入已有 D1 single-loss survivor path；
5. Aha 全部 Route exhausted：没有 D1 survivor，当前 Revision HOLD/BLOCK，也不新增 S09 re-selection；
6. Chapter survivor 中被删除的成员不再属于 required set；
7. 两个 Chapter members exhausted、Hero 无合法替代或任一 hard constraint 失败：BLOCK，不发布残缺结果。

Fallback 或 Passive Alternate 的激活必须生成新的不可变 `HQRequestActivationDelta`，不得原地改写初始 manifest。无论内部经历多少次取源或 Route 尝试，只有 active body media 与 active Hero 都 ready 后，才能原子发布一个完整 Revision；用户不得看到缺图卡片、半成品 Chapter 或备用 Route 切换过程。

运行时激活还必须先重验所有受影响的下游 artifact，不能把“媒体 Route 已合法”误当成“旧 Narrative/Claim 仍然合法”：

1. Fallback 带有 `PRESENTATION_NARROWING` 时，S11/S12 必须按新 active Route 的事实支持范围重验表达；
2. D1 删除一个正文成员时，任何依赖该成员的 title/story/tag、progression/outcome Claim 与完整性判断都必须重验；
3. Hero Alternate 只改变入口画面时，也必须确认 poster/cover Claim 与 provenance 仍匹配；
4. 受影响 artifact 未完成重验前，Revision 继续 HOLD，不得原子发布；
5. 具体由 S13 回调 S11/S12、由统一编排器重新执行，还是在 S12 前完成 materialization，留给 S11–S13 集成设计；但“最终发布前必须重验”是本合同的硬义务。

### 38.6 输出

~~~text
FinalMediaHQRequestManifest
  selected_memory_refs[]
  revision_ref
  finalization_gate_audit_ref
  finalized_media_set_refs[]
  finalized_hero_refs[]
  request_entries[]
    consumer_refs[]
    media_decision_ref
    route_ref
    hero_ref
    request_tier =
      TIER_0_REUSE
      | TIER_1_REQUIRED_PRIMARY
      | TIER_2_ON_DEMAND_FALLBACK
      | TIER_3_NOT_REQUESTED
    source_identity_ref
    exact_source_scope
      frame_ref
      | interval_ref
      | source_object_capability_ref
    intended_final_format
    required_to_publish
    reuse_fingerprint
    coalescing_key
    activation_predicate_ref
    request_state
  excluded_candidate_refs[]
  source_reuse_audit_refs[]
  coalescing_plan_refs[]
  manifest_state =
    READY_TO_REQUEST_REQUIRED_PRIMARY
    | FINALIZATION_HOLD
    | FINALIZATION_BLOCKED
    | CONTRACT_INVALID
  policy_and_signal_versions
  manifest_fingerprint

HQRequestActivationDelta
  revision_ref
  base_manifest_ref
  proven_terminal_failure_refs[]
  route_activation_resolution_ref
  newly_active_request_entry_refs[]
  deactivated_consumer_refs[]
  survivor_activation_ref
  resulting_required_set_ref
  affected_narrative_claim_artifact_refs[]
  downstream_revalidation_required
  downstream_revalidation_state
  activation_state
  delta_fingerprint
~~~

`destination`、后台上传时间、网络条件、云存储路径和 API/Agent 路由不进入本结构；这些字段必须等上传架构专项设计后再定义。

### 38.7 成本案例

1. **四项 Chapter：** 四个正文成员各有 1 Primary＋2 Fallback，算法先只请求四个 active Primary，不会因为存在 Route 就一次请求十二份 HQ。
2. **Hero 与正文同源：** 正文是一段吹蜡烛 VIDEO，Hero 是其中一帧；两者共享一次 source fetch，分别生成 5 秒视频和静态封面。
3. **Fallback 从未使用：** Primary 正常完成，两个 Fallback 永远只有 metadata，产生零 HQ 传输。
4. **Primary 确定失败：** 第一 Fallback 经 D2 激活后才产生增量请求；第二 Fallback 继续休眠。
5. **跨 Revision 复用：** 晚间 Revision 保留下午已成功生成的三项，只为新增或真正变化的项请求 source。
6. **全天高强度使用：** 即使最终有 4 个 Chapter、每个 4 项，正文 active source 意图约为 16 项，而不是把全部候选、最多 48 条 Route 或当天所有原视频上传为最终媒体请求。
7. **不能合并的相似画面：** 两张古建筑外观虽然视觉近似，但来自不同建筑和不同 source identity；不能用同一个 HQ 结果替代另一项。
8. **底层只能整文件取源：** S10 仍声明精确 5 秒 interval；S13 可按设备能力取整文件，但必须保留“实际多取”与“算法必要范围”的区别，供成本审计。

### 38.8 Invariants、成本边界与 OPEN 项

1. 先选内容，后请求最终媒体 HQ；
2. 只为当前 active final set 请求 TIER_1；
3. Fallback 与 Passive Alternate 默认零 HQ 成本；
4. 复用必须基于不可变 fingerprint，不基于模糊相似；
5. 同源合并不能扩大语义消费范围；
6. S10 不读取、上传、存储或渲染 HQ，只输出 manifest；
7. HQ 请求失败不能改变 Beat identity、Chapter order 或内容价值判断；
8. 用户完成 Sync 后不得因本合同新增上传交互；
9. 具体分辨率、码率、压缩质量与端侧能力需在真实素材 benchmark 后冻结；
10. 后台上传时机、Wi-Fi/蜂窝/电量条件、云存储/API/Agent 去向、本地保留期、取消与 retry 次数继续保持 OPEN；
11. Aha 最终媒体已经由 S10-D4 确认为恰好一个 PHOTO/LIVE_2S 可见位置；D3 只映射其 request tier，不改变该产品合同；
12. 本项不改变“Manual 任意时长视频抽帧 Window 合同仍 OPEN”的既有边界。

## 39. 下一检查点

进入 S10-D4：定义一个 Aha 最终应展示几个用户可见媒体项，以及其 Primary/Fallback、Hero 关系和成本合同。该问题直接影响 Aha 是“一个聚焦高光”还是“一个微型 Chapter”，必须先做产品体验决策，再写算法规则。

## 40. S10-D4.1｜Aha Single Visible Media Contract

**状态：CONFIRMED**

### 40.1 产品定义

V1 每个已被 S09 选中的 Aha 最终恰好展示 **1 个用户可见媒体项**：

~~~text
one selected Aha Memory
→ one core Content Beat
→ one resolved EvidenceAnchor
→ one MediaDecision
→ exactly one active visible PHOTO or LIVE_2S
~~~

Aha 是一个聚焦高光，不是微型 Chapter。它可以使用邻近 Window、CONTEXT_ONLY、关系与时间证据帮助算法理解同一 peak，但这些支持材料不变成第二个用户可见媒体项。

本合同对 `CHAPTER_DAY` 中的 embedded Aha 与 `HIGHLIGHT_DAY` 中的 standalone Aha 同样适用；Day State 不改变 Aha 的媒体数量。

### 40.2 一个 MediaDecision，不是一个 Primary 加多个素材

每个 Aha 最终只能绑定一个已经通过 B3.3 的 `MediaDecision`：

- 恰好 1 条初始 Primary Route；
- 允许 0–2 条预声明 Fallback Route；
- Primary 与 Fallback 合计仍只代表同一个 Aha 媒体位置；
- 运行时任何时刻最多只有一条 active Route；
- Fallback 只替换失败 Route，不成为第二张图或第二段 Live；
- 每一条 Route 都必须直接表达同一个 core peak。

算法不能把 PHOTO 与 LIVE_2S 同时展示为“一静一动”两个素材，也不能把 peak 前的准备、peak 后的结果或漂亮的邻近画面作为 supporting item 加入 Aha。

### 40.3 格式与最小充分原则

Aha 只允许：

~~~text
PHOTO
LIVE_2S
~~~

继续禁止 `VIDEO_5S`。具体选择沿用 B1/B2：

- 一张照片已经完整、真实、清楚地呈现 peak 时，选择 PHOTO；
- 连续两秒对动作、变化或现场感有实质增量时，选择 LIVE_2S；
- PHOTO 与 LIVE 均合法时，不为“看起来更高级”自动选择动态；
- LIVE 失败后，只有 PHOTO 仍直接呈现同一 peak 才可回退；
- 只显示准备、普通过程或事后结果的画面不能冒充 Aha peak。

### 40.4 Aha 不设置独立 Hero

Aha 的 active media identity 同时承担卡片入口、高光内容与详情主媒体角色：

~~~text
aha_hero_identity = active_aha_media_identity
~~~

因此：

1. 不再额外选择一个 Hero member；
2. 不从未入选 Candidate、邻近 Beat、CONTEXT_ONLY 或全天素材池寻找漂亮封面；
3. PHOTO 的卡片预览与详情媒体属于同一媒体 identity；
4. LIVE_2S 可以从同一 Anchor/source plan 生成静态 poster frame，但 poster 只是同一动态媒体的展示派生物，不是第二个内容项、第二个 Hero 或新的 Fallback；
5. poster 不得使用另一个时间点改变 peak 含义；
6. 卡片与详情页是否采用不同裁切属于呈现层，但都必须保持同一 provenance、事实 scope 与核心内容。

### 40.5 Supporting Evidence 的准确作用

S07 允许 Aha interval 包含一个 peak Window 与最多两个紧邻 support Windows，作用是帮助确认：

- 动作是否真实发生；
- peak 前后的局部变化；
- 谁与谁发生互动；
- 当前画面是否确实属于同一局部事件。

它们不是三份最终媒体。例如：

~~~text
18:00:00 朋友端着蛋糕靠近        support before
18:00:02 用户吹灭蜡烛            KEEP peak
18:00:04 大家鼓掌                support after
~~~

算法可以用前后证据确认“吹灭蜡烛”的事实，但最终 Aha 只展示直接呈现 `18:00:02` peak 的一张 PHOTO 或一段 LIVE_2S。蛋糕靠近和鼓掌不能被加成第二、第三项。

### 40.6 Readiness 与失败下限

一个 Aha 只有在以下条件全部成立时，才可进入最终媒体请求：

1. 唯一 core Beat 合法；
2. 唯一 active Route 直接表达同一 peak；
3. 格式为 PHOTO 或 LIVE_2S；
4. EvidenceAnchor、source scope、provenance 与 claim compatibility 完整；
5. 若 Primary 为 conditional，至少存在 B3.3 要求的非条件同核心 Fallback；
6. Aha 自身不存在 unresolved 或 contract invalid，且其跨 Memory render relation 已进入 D4.2；D4.2 允许的必要 exact reuse 不属于 Aha 内部媒体冲突；
7. 卡片 poster 若需要，可以从同一 active media 合法派生。

若所有 Route 均失败，Aha 不允许：

- 发布空卡片或缺图占位；
- 只发布 title/story 而没有核心媒体；
- 使用邻近漂亮画面替代 peak；
- 自动扩展成 Chapter；
- 从全天重新搜索一个“差不多”的瞬间；
- 因为当天目标是 2–3 个 Aha 而降低媒体下限。

当前 Aha 进入显式 `AHA_MEDIA_INSUFFICIENT`，但是否能使用全 Revision 唯一一次 bounded S09 re-selection，必须按失败发生时间与类别精确分流：

- 若在原始 S10 batch 完成前已经证明所有合法 Route 不可用，它可与 Chapter proven insufficiency 一起进入 C1.3 的同一 failure batch，并共享全 Revision 唯一一次机会；
- 若仍为 UNKNOWN、transient 或 contract invalid，必须 HOLD/BLOCK，不能重选；
- 若 S10 finalization 后、S13 发布前才出现 terminal failure，先按预声明顺序激活同 peak Fallback；全部 Route 用尽时当前 Revision HOLD/BLOCK。Aha 恰好只有一个媒体位置，不存在 D1 式单项删除 survivor，也不能因此新增一次 S09 re-selection；
- 若事故发生在 Revision 已发布后，进入 S13 存储恢复边界，不由 D4.1 静默删除或替换已发布 Aha。

D4.1 不新增独立重选次数，也不允许把 support Window、邻近漂亮画面或另一个 Aha Candidate 临时补进来。

### 40.7 HQ 请求映射

D3 四级合同直接适用于 Aha：

- active Aha Primary：`TIER_1_REQUIRED_PRIMARY`；
- 其 0–2 条 dormant Fallback：`TIER_2_ON_DEMAND_FALLBACK`；
- LIVE poster 与正文同源时合并取源，不增加独立 HQ source request；
- 未入选 Aha 候选、support Window 与未声明 realization：`TIER_3_NOT_REQUESTED`；
- 已成功生成且 fingerprint 完全兼容的结果：`TIER_0_REUSE`。

Fallback 只有在 proven terminal failure 后才按 B3 的预声明顺序激活；单媒体 Aha 不做正文集合式 Route 组合搜索。transient 或 UNKNOWN 不提前产生备用 HQ 成本。

### 40.8 输出

~~~text
AhaFinalMediaDecision
  selected_memory_ref
  revision_ref
  day_state
  aha_relation_role =
    EMBEDDED_DISTINCT_AHA
    | STANDALONE_HIGHLIGHT_AHA
  origin_moment_ref
  peak_window_ref
  core_content_beat_ref
  evidence_anchor_ref
  media_decision_ref
  visible_media_count = 1
  initial_primary_route_ref
  ordered_fallback_route_refs[]       # 0–2
  active_media_identity_ref
  active_format = PHOTO | LIVE_2S
  aha_hero_mode = ACTIVE_MEDIA_SELF
  live_poster_plan_ref
  non_visible_support_evidence_refs[]
  hq_request_manifest_entry_refs[]
  media_readiness_state =
    AHA_MEDIA_READY
    | AHA_MEDIA_READY_CONDITIONAL
    | AHA_MEDIA_INSUFFICIENT
    | AHA_MEDIA_UNRESOLVED
    | AHA_MEDIA_CONTRACT_INVALID
  limitation_refs[]
  policy_and_signal_versions
  decision_trace
~~~

### 40.9 案例

1. **合法已选的吹蜡烛 Aha：** 例如没有完整生日 Chapter、该 peak 以 standalone Aha 合法入选时，一段完整覆盖烛火熄灭的 LIVE_2S 为唯一媒体；蛋糕靠近与随后鼓掌只作 Evidence。本例只说明媒体合同，不授予与生日 Chapter 共选资格。
2. **清晰决定性照片：** 一张照片恰好捕捉求婚动作，已经足够表达 peak，选择 PHOTO，不为动态形式额外请求视频。
3. **孩子回头挥手：** LIVE_2S 有实质互动价值；卡片 poster 来自同一段 Live，不再选另一张封面。
4. **只有事后结果：** 画面只看到熄灭的蜡烛，没有直接呈现吹灭 peak；即使构图漂亮也不能成为该 Aha 媒体。
5. **准备＋结果需要两张才懂：** 若一个所谓 Aha 必须同时展示“走进店里”和“喝到奶茶”才能成立，它不符合单 peak/单媒体下限；S10 不把它拼成两项 Aha。
6. **LIVE terminal failure：** 同 Anchor PHOTO 仍精确呈现 peak 时，可激活 PHOTO Fallback；用户最终仍只看到一项。
7. **全部 Route 失败：** 不显示 title-only Aha，也不把 support Window 拉来补位；进入明确媒体不足路径。
8. **Standalone HIGHLIGHT_DAY：** 当天没有合法 Chapter、只有一个强求婚 Aha 时，仍然只展示该 peak 的一个 PHOTO 或 LIVE_2S，不因页面内容稀疏增加第二项。

### 40.10 Invariants、成本与边界

1. 每个最终 Aha 的用户可见媒体数量恒等于一；
2. support Window 数量不等于媒体数量；
3. Primary/Fallback Route 数量不等于媒体数量；
4. Aha active media 本身就是 Hero identity；
5. LIVE poster 是同源展示派生物，不是新内容；
6. 任何 Route 都必须直接表达同一 peak，Aha 不接受 CORE_PARTIAL 替代；
7. embedded 与 standalone Aha 使用相同媒体下限；
8. S10 不改变 S09 已选 Aha membership、全天数量或 canonical order；
9. 本项不决定 Chapter 与 embedded Aha 能否复用同一 canonical final render；
10. 本项不决定卡片尺寸、裁切、自动播放、动效或 App 布局；
11. 本项不新增模型调用、上传交互、HQ 预取或全天搜索；
12. Manual 任意时长视频 Window 合同继续保持 OPEN。

## 41. 下一检查点

原计划进入 S10-D4.2，讨论 Chapter 与 embedded Aha 是否允许引用同一 canonical final render。现已暂停该问题：必须先证明 Chapter/Aha 在故事层合法共存，才有资格讨论媒体复用。

## 42. S10 上游依赖修订｜Aha–Chapter Narrative Independence

**状态：UPSTREAM FROZEN BY CANONICAL V1.20 / S10 FROZEN BY CANONICAL V1.21**

已确认：

1. Chapter 已被选中时，其核心、高潮、自然结果或同故事缩写不得再重复成为 Aha；
2. Chapter 未成立或未入选时，同一个强局部 peak 仍可独立成为 Aha，但必须通过原有 Local Peak、Independent Memory Value、Evidence 与媒体门槛；
3. “位于 Chapter 时间线内”只是一项 temporal relation，不是共选资格；
4. 只有故事命题不同、不是 Chapter core/climax/outcome、移除后 Chapter 仍完整、脱离 Chapter 后 Aha 仍独立可理解时，才可映射为 `EMBEDDED_DISTINCT_AHA`；
5. 同故事 core 映射 `NESTED_DOMINANCE`，同故事重述映射 `SAME_MEMORY_REDUNDANCY`，无法判断映射 `UNRESOLVED_POTENTIAL_CONFLICT`；
6. S10 不用换 Frame、格式、Anchor 或画面风格把同一个故事伪装成两个 Memory。

该规则位于 S07/S09，详细工作合同见：

`S07_S09_AHA_CHAPTER_NARRATIVE_INDEPENDENCE_AMENDMENT_WORKING_V0_1.md`

S10-D4.1 的单媒体、格式、Hero 与 HQ 请求规则保持有效，但只作用于已经合法通过 S09 membership 的 Aha。D4.2 只有在 `ChapterAhaNarrativeIndependenceDecision = NARRATIVELY_DISTINCT_PASS` 后才可能执行。

## 43. 下一检查点

Aha–Chapter Narrative Independence Gate 已完成 44 个边界案例与 12 项 Invariant 的内部交叉检查，4 项 refinement 已回写，并由 `CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md` 冻结承接。

下一步恢复 S10-D4.2：只对已经 `NARRATIVELY_DISTINCT_PASS` 的 Chapter/Aha pair，讨论是否允许复用同一 canonical final render，以及 App 重复感与额外 HQ 成本的边界。

## 44. S10-D4.2｜Cross-Memory Render Distinctness 与 Necessary Exact Reuse

**状态：CONFIRMED**

### 44.1 适用前提

D4.2 只处理已经满足下列条件的 Chapter/Aha pair：

~~~text
ChapterAhaNarrativeIndependenceDecision
= NARRATIVELY_DISTINCT_PASS
~~~

若关系为 same-story core、restatement、context-dependent、unresolved 或 contract invalid，pair 根本没有共选资格，不能进入“换个画面是否就不重复”的讨论。

本项只解决用户可见媒体的重复感和最终媒体成本，不重新判断故事价值、Memory membership 或 Aha 数量。

### 44.2 三种必须分开的复用

#### A. Shared source，distinct semantic render

Chapter 与 Aha 可以来自同一个 RawAsset/HQ source，但使用不同、各自合法且具有不同内容作用的 frame/interval：

- Chapter 使用甜品店环境或进入店铺的片段；
- Aha 使用第一口后的明确惊喜 peak；
- 两者可合并 source fetch，但产生不同 final render。

这属于 `SHARED_SOURCE_DISTINCT_RENDER`，不是用户可见重复。

#### B. Exact / cosmetic-equivalent render reuse

以下统一视为用户可感知的同一画面，不能通过表面处理绕过：

- 同一 still/frame 与等价 final format；
- 同一 source interval、format 与 render policy；
- 只改变裁切、缩放、编码、分辨率、色彩或轻微时间边界；
- Aha 的核心 2 秒被 Chapter 动态媒体实质完整重放，虽外层时长不同；
- canonical render identity 相同或已被现有 Evidence 证明为实质等价。

它们进入 `EXACT_OR_MATERIAL_RENDER_REUSE` 审计。

#### C. Memory identity reuse

Chapter 与 Aha 继续拥有不同的 selected Memory refs、事实 scope、lineage 与下游 narrative/claim boundary。即使最后复用同一媒体 blob，也不能把两个 Memory ID 合并、让一个 Claim 自动继承另一个，或把一次渲染误记成一个 Memory。

### 44.3 核心策略｜默认避免，必要时允许

V1 采用：

~~~text
PREFER_DISTINCT_FINAL_RENDER
ALLOW_EXACT_REUSE_WHEN_NO_NO_LOSS_ALTERNATIVE
~~~

比较层级：

1. V1.20 narrative independence 与全部 legality/truth/scope；
2. Chapter/Aha core expression 与独立可理解性；
3. Chapter set completeness、material contribution 与代表性；
4. media presentation quality；
5. Route/source/Hero/failure robustness；
6. prior-published continuity，避免为轻微去重制造跨 Revision 抖动；
7. cross-memory exact/material render avoidance；
8. lower cost 与 stable deterministic tie-break。

因此，避重只作用在所有更高层均合法且 `policy-defined near-equivalent` 的方案之间。不能为了形式上的不同，选择语义更弱、画质更差、失败风险更高或不直接表达 Aha peak 的素材。

### 44.4 什么是 no-loss alternative

一个 distinct alternative 只有同时满足以下条件，才可替换原重复方案：

1. 已存在于当前 S10 attempt 的合法 whitelist、Candidate/Beat/Anchor/MediaDecision 范围；
2. 不搜索全天、不创建新 Beat/Anchor/Route；
3. Chapter target size 与 hard constraints 不降级；
4. Chapter core coverage、material contribution、chronology 与 Hero availability 不降低；
5. Aha 仍直接表达同一 peak；
6. presentation quality、source readiness 与 failure robustness 无 material loss；
7. 不要求主动激活仅为 terminal failure 预留的 Fallback；
8. 相关 D1 survivor、D2 collision、Hero 与 D3 HQ plan 可以用同一批 metadata 有界重建并完整通过。

只有颜色、裁切、格式名称或几百毫秒边界不同，但用户仍会看到同一核心画面，不构成 distinct alternative。

### 44.5 Reconciliation 的执行位置与边界

讨论顺序不等于运行时顺序。实际 Finalization 应为：

~~~text
Chapter provisional hard-valid finalist(s)
+ Aha single-media decision(s)
+ V1.20 narrative relation decisions
→ cross-memory render matrix
→ choose no-loss distinct projection when available
→ otherwise record necessary exact reuse
→ finalize/rebuild bounded D1/D2/Hero metadata for winning projection
→ emit D3 FinalMediaHQRequestManifest
~~~

D4.2 不原地改写 C2/C3/B3 artifact。若选择一个已有 no-loss alternative，应生成新的不可变 `CrossMemoryPresentationProjection`，引用原 finalist 与完整重验证结果。没有合法 projection 时保留原内容决策并记录必要复用。

为了避免组合膨胀：

- 只检查当前已选 Chapter/Aha 间的 cross-memory render pair；
- 每个 collision 只保留已有 hard-valid、higher-layer near-equivalent alternatives；
- 不生成新组合素材、不调用模型、不读取 HQ；
- 最多 5 Chapter × 3 Aha = 15 个 Chapter–Aha pair；
- exact/cosmetic/interval overlap comparison 使用现有 source plan 与 canonical identity metadata。

如果 UNKNOWN 只影响“两个合法 render 是否构成软近重复”，D4.2 不得因此阻断一个更高层均合法的 Revision，也不能猜测为 distinct；保留各自原计划并记录 `RENDER_RELATION_LIMITATION`。若 UNKNOWN 涉及 MediaDecision 本身必需的 source identity、provenance、Anchor 或 legality，则仍按 B3/S10 contract unresolved 处理，不能借软偏好边界放行。

### 44.6 Aha media 优先保持，Chapter 只在无损时调整

Aha 只有一个必须直接表达 peak 的媒体位置，因此 D4.2 默认锁定 Aha Primary media identity。优先检查 Chapter 是否已有无损方式避免重复：

1. Chapter Hero 与 Aha 重复：先看同一已选 Chapter set 中是否有意义/质量近似等价的合法 Hero candidate；
2. Chapter body 与 Aha 重复：只比较已存在的 hard-valid near-equivalent Chapter finalist/projection；
3. 不为避重把 Aha Primary 换成弱画面；
4. 不主动激活 Aha 或 Chapter Fallback；
5. 没有无损 Chapter alternative 时允许精确复用。

若 Chapter Hero 与 Aha 使用同一画面，还必须做一致性审计：若该画面实际是 Chapter 的 representative summary/core peak，则可能与 V1.20 `SIDE_EPISODE_LOCAL_EVENT` 前提冲突，应返回 relation/hero contract invalid，而不是用 D4.2 掩盖；若同一画面同时合法承载宽场景与独立局部 peak，才继续按必要复用处理。

### 44.7 Exact reuse 是允许的最后路径，不是失败

当不存在 no-loss distinct alternative 时：

- 保留各自最真实、最合适的媒体；
- 允许同一 canonical final render 被两个 consumer 引用；
- 输出 `CROSS_MEMORY_EXACT_RENDER_REUSE`；
- D3/S13 只 materialize 一次并复用结果，避免重复上传、解码与渲染；
- Chapter/Aha 的 visible item count、Memory count、lineage 与 claim scope 分别计算；
- 用户是否在两个 App surface 上都看到它、是否显示 Aha 标记，继续属于 App 呈现设计 OPEN 项。

必要复用不会触发 S09 re-selection，不会将合法 Aha 删除，也不会要求用户再次 Sync/上传。

### 44.8 Runtime Fallback 与跨 Revision

#### Fallback activation

如果初始 Primary 彼此 distinct，但 proven terminal failure 后某条预声明 Fallback 与另一 Memory 的健康媒体产生 exact/material overlap：

- 不移动或降级健康媒体；
- 不跳过语义更优的第一合法 Fallback，只为视觉不同改用更弱 Route；
- 允许 activation-induced exact reuse 并记录；
- transient/UNKNOWN 仍不激活 Fallback；
- same-story relation 若因此暴露为上游漏判，按 contract invalid，而不是复用例外。

#### Cross-Revision

- 新 Revision 已因新素材/事实合法产生，且出现 no-loss distinct alternative 时，可以减少旧重复；
- 不仅为了修复一个软重复偏好，单独制造没有内容变化的新 Revision；
- prior media 与 distinct alternative higher-layer near-equivalent 时，prior-published continuity 高于本项软避重，防止画面反复切换；
- 复用 fingerprint 不再兼容时不得沿用旧 render，按 D3 正常请求。

### 44.9 输出

~~~text
CrossMemoryRenderDistinctnessDecision
  revision_ref
  chapter_memory_ref
  aha_memory_ref
  narrative_independence_decision_ref
  chapter_consumer_ref
  aha_consumer_ref
  planned_render_relation =
    DISTINCT_SOURCE_DISTINCT_RENDER
    | SHARED_SOURCE_DISTINCT_RENDER
    | EXACT_CANONICAL_RENDER
    | COSMETIC_EQUIVALENT_RENDER
    | MATERIAL_TEMPORAL_OVERLAP
    | RENDER_RELATION_UNRESOLVED
  original_chapter_projection_ref
  locked_aha_media_decision_ref
  no_loss_alternative_refs[]
  winning_chapter_projection_ref
  hero_consistency_audit_ref
  final_reuse_state =
    DISTINCT_RENDER_KEPT
    | DISTINCT_RENDER_SELECTED_NO_LOSS
    | EXACT_REUSE_ALLOWED_NO_NO_LOSS_ALTERNATIVE
    | EXACT_REUSE_ALLOWED_BY_RUNTIME_FALLBACK
    | PRIOR_CONTINUITY_KEPT_EXACT_REUSE
    | RENDER_RELATION_LIMITATION
    | NARRATIVE_OR_CONTRACT_INVALID
  shared_materialization_key
  d1_d2_hero_revalidation_refs[]
  hq_manifest_impact_ref
  reason_refs[]
  policy_and_signal_versions
  decision_trace

CrossMemoryPresentationProjection
  revision_ref
  base_chapter_media_set_decision_ref
  base_chapter_hero_decision_ref
  selected_no_loss_alternative_ref
  projected_body_media_refs[]
  projected_hero_ref
  locked_aha_media_ref
  complete_hard_constraint_audit_refs[]
  projection_state
  projection_fingerprint
~~~

### 44.10 案例

1. **古镇＋甜品 Aha，有无损替代：** Chapter 原四项含甜品反应；另一个同等合法四项使用牌坊、木雕、河边、返程，仍完整表达观光。选择后者，Aha 单独展示甜品反应。
2. **同 RawAsset、不同作用：** Chapter 使用进入甜品店的环境 5 秒，Aha 使用第一口反应 2 秒；允许共享 source fetch，两个 final render distinct。
3. **只有同一画面足够真实：** Chapter 没有无损替代，换图会失去重要内容或画质明显下降；允许 exact reuse，不牺牲质量。
4. **裁切伪装：** Chapter 用原图，Aha 把同一帧裁成人脸近景；若核心画面仍相同，属于 cosmetic-equivalent，不算成功避重。
5. **动态包含：** Chapter 5 秒视频完整包含 Aha 的核心 2 秒；视为 material temporal overlap，按同一软避重规则处理。
6. **Aha 不降级：** Aha LIVE 直接表达甜品惊喜，PHOTO 只显示吃完后的笑脸；不能为了和 Chapter LIVE 不同而主动改用 PHOTO。
7. **Hero 重复：** Chapter 有近似等价的建筑 Hero 时换 Hero；若 Aha 画面实际成了 Chapter 核心代表，则回查 V1.20/meaning-first contract。
8. **Fallback 后才重复：** Aha Primary LIVE 失败后，第一合法 PHOTO Fallback 与 Chapter media 相同；允许必要复用，不跳到语义更弱的第二 Fallback。
9. **同故事生日：** Birthday Chapter＋吹蜡烛 Aha 在 V1.20 已被阻断，不能借“允许 exact reuse”进入 D4.2。
10. **跨 Revision 稳定性：** prior 已使用必要复用且仍合法；没有内容变化时不为软避重另发 Revision。
11. **两个 Aha 同一 peak：** 由 S09 Aha–Aha hard redundancy 阻断，不属于本项复用例外。
12. **HQ 成本：** 两个 consumer 精确复用时，manifest 保留两个消费引用、一个 shared materialization，不重复上传源文件。

### 44.11 Invariants、成本与边界

1. V1.20 narrative PASS 是 D4.2 的硬前提；
2. distinct render 是低层偏好，不高于真实性、核心表达、画质、鲁棒性与 prior continuity；
3. Aha Primary 默认锁定，Chapter 只在 no-loss 时调整；
4. 不主动激活 Fallback，不生成新 Route/Beat/Anchor，不搜索全天；
5. 裁切、编码或轻微时间边界不能伪装成 distinct；
6. 没有无损替代时 exact reuse 合法，不触发 S09 re-selection；
7. exact reuse 共享 materialization，但不合并 Memory identity、数量或 Claim；
8. runtime Fallback 导致的必要复用不移动健康媒体；
9. cross-Revision 不为软避重单独制造 churn；
10. 本项最多比较 15 个 Chapter–Aha pair 与有界 metadata alternatives，不新增模型/HQ 请求；
11. App 是否重复展示、Aha badge、布局与交互动效继续 OPEN；
12. D4 cross-check 与 S10-E 全链路检查均已通过；S10 已由 Canonical V1.21 冻结。

## 45. S10-D4 Closeout 与下一检查点

**状态：FROZEN BY CANONICAL V1.21**

D4.1–D4.2 已确认 Aha 恰好一个用户可见媒体项、无独立 Hero、PHOTO/LIVE_2S、严格同 peak Fallback、D3 HQ request mapping，以及 V1.20 PASS 后默认避免但必要时允许 Chapter/Aha exact render reuse。

D4 内部检查已完成 36 个边界案例、14 项 Invariant，并回写四项 refinement：Aha 内部冲突与跨 Memory 复用分离、soft UNKNOWN 与基础合同 UNKNOWN 分离、5 秒包含 Aha 核心 2 秒按 material overlap 处理，以及 Aha Primary/B3 Route order 不为软避重改写。详见 `S10_D4_AHA_FINAL_MEDIA_INTERNAL_CROSS_CHECK_V0_1.md`。

## 46. S10-E｜全链路检查结果

**状态：CROSS-CHECK PASSED / REFINEMENTS APPLIED / FROZEN BY CANONICAL V1.21**

S10-E 已把 A1/A2/B/C/D、Canonical V1.20、S09 bounded re-selection、S11/S12 revalidation obligation 与 S13 HQ handoff 连成一条链，并完成：

~~~text
52 / 52 cross-stage boundary cases passed
10 / 10 user-profile simulations passed
32-window ancient-town fine-grained timeline traced
30 / 30 global invariants preserved
6 interface refinements applied
~~~

完整记录见 `S10_END_TO_END_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_1.md`。

六项 refinement 为：

1. 区分讨论章节顺序与实际 finalization 顺序；
2. 按发生时间精确分流 Aha media insufficiency；
3. runtime Fallback/D1/Hero activation 后必须重验受影响的 S11/S12 artifacts；
4. 把阶段早期已由下游解决的 `OPEN`/pending 表述同步为当前状态；
5. 成本审计分开统计 consumer、render/materialization、unique source request 与 dormant metadata；
6. 保留 V1.20 冻结时的范围历史，由后续 S10 合同解决 final-render reuse。

没有发现需要新增用户体验决策或推翻现有 S10 核心方向的问题。

## 47. 集成 Finalization 与 Runtime 顺序

实际执行顺序统一为：

~~~text
S09 selected membership
→ A1/A2/B Content Beat + Anchor + MediaDecision
→ C HeroPreEligibility + Chapter final set/order/Hero
→ D4.1 Aha single media
→ verify V1.20 pair decisions
→ D4.2 cross-memory presentation reconciliation
→ finalize/rebuild D1/D2/Hero metadata
→ D3 HQ request manifest
→ S11 grounded narrative
→ S12 validation
→ S13 materialization/export
~~~

若 S13 在原子发布前证明 terminal failure，只能激活预声明 Route/D1/Alternate，生成 immutable delta，并让受影响的 final-media projection、Narrative 与 Claim 重新通过必要验证后再发布。具体服务调用次序由 S11–S13 集成专项确定，但不允许跳过重验。

## 48. Freeze Result 与下一检查点

用户已确认冻结，S10 当前结论为：

~~~text
DESIGN CLOSED
END-TO-END CROSS-CHECK PASSED
FROZEN BY CANONICAL V1.21
~~~

仍保持 OPEN：任意时长 Manual Window 规划、真实模型/阈值/成本 benchmark、S13 retry/checksum/lifecycle、App 后台上传与 destination、App 重复画面呈现，以及隐私/伦理/治理专项。这些不应在 S10 Checkpoint 中伪造答案。

Canonical Checkpoint 已生成：`CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md`。下一阶段进入 S11 Grounded Narrative / Claim Ledger；不能在本工作文档中提前混入 S11 设计。
