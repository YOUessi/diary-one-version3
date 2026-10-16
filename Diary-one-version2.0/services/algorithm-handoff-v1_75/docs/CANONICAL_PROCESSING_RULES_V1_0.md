# Diary One Processing & Algorithm Rules — Consolidated V1.0

**状态：** Canonical consolidation
**基于：** `Diary One Cloud Intelligence — Canonical Architecture V1.0`（2026-08-18）
**整理日期：** 2026-08-19
**目的：** 将已确定的定义、算法规则、端云原则、评测口径与当前实验实现放进一个可快速被人或模型读取的文件。

> 本文不新增产品决策。`FROZEN` 继承 2026-08-18 Canonical Architecture；昨天后续实现的 E00/X01 只作为 `IMPLEMENTED` 或 `EXPERIMENTAL` 记录。若实验代码与冻结规则冲突，以冻结规则为准并登记 `GAP`。

> **当前覆盖：** 2026-08-25 的 [V1.1](CANONICAL_CHECKPOINT_V1_1_ROLLING_DAILY_MEMORY.md) 覆盖 DailyMemoryRun 触发、白天 Revision 累加，并将丰富日目标设为 3–4 Chapter、第 5 个设为严格例外；[V1.2](CANONICAL_CHECKPOINT_V1_2_RAW_ASSET_INTAKE.md) 冻结 S01 RawAsset；[V1.3](CANONICAL_CHECKPOINT_V1_3_AUTO_THREE_FRAME_EVIDENCE.md) 与 [V1.4](CANONICAL_CHECKPOINT_V1_4_MANUAL_EVIDENCE.md) 冻结 S02 Auto/Manual Evidence；[V1.5](CANONICAL_CHECKPOINT_V1_5_SIGNAL_PACK_BASELINE.md) 冻结 S03 最小信号；[V1.6](CANONICAL_CHECKPOINT_V1_6_EVIDENCE_UPLOAD_ROUTING.md) 冻结 Phone 三帧与 Cloud `1-or-3`，并允许相似 Manual 从 Memory 候选中抑制；[V1.7](CANONICAL_CHECKPOINT_V1_7_OBSERVATION_LITE_COVERAGE.md) 冻结 S04 全 Window Observation 记录与 batching；2026-08-26 的 [V1.8](CANONICAL_CHECKPOINT_V1_8_BACKGROUND_UPLOAD_NO_REFETCH.md) 冻结 Sync 后无感批量上传和 Auto 不补帧；[V1.9](CANONICAL_CHECKPOINT_V1_9_SIGNAL_SPLIT_WINDOW_LOCAL_OBSERVATION.md) 将 S03 拆为 Window 自身信号与时间线 Edge，并冻结 S04 Window-local 事实与仅精确缓存复用；[V1.10](CANONICAL_CHECKPOINT_V1_10_OBSERVATION_LITE_OUTPUT_CONTRACT.md) 冻结 S04 的结构化事实卡、逐条 Frame grounding、状态与证据支持等级，并取消 Production Observation 总置信分；[V1.11](CANONICAL_CHECKPOINT_V1_11_CONTIGUOUS_MOMENT_SEGMENTATION.md) 冻结 S05 连续、互斥、完整覆盖的 Moment partition，并禁止跨时间相似聚类成为同一 Moment；[V1.12](CANONICAL_CHECKPOINT_V1_12_DUAL_EVIDENCE_BOUNDARY_LEDGER.md) 冻结每个相邻 seam 的 continuity/boundary 双向证据账本与四状态决策架构；[V1.13](CANONICAL_CHECKPOINT_V1_13_MULTI_PROTOTYPE_CONTEXT_SIGNATURE.md) 冻结多原型 Context Core/Tail/Pending、grounded Motif 与 commit-on-MERGE 更新边界；[V1.14](CANONICAL_CHECKPOINT_V1_14_UNRESOLVED_TRANSITION_ROUTING.md) 冻结证据用尽后 unresolved transition 的独立物化，以及 Aha 候选、CONTEXT_ONLY、DROP 三路后续边界；[V1.15](CANONICAL_CHECKPOINT_V1_15_BOUNDED_DEFER_LOOKAHEAD.md) 冻结当前两条可用后续 Window、6 分钟、3 Pending 的有界 Baseline、完整 seam pattern 提前结束、同快照解析与原子提交。本文其余未被覆盖的内容继续有效；正文保留 V1.0 历史原文。

> **当前 S06 覆盖：** [V1.16](CANONICAL_CHECKPOINT_V1_16_OBSERVATION_ROLE_ASSIGNMENT.md) 冻结每个 accepted Observation 的唯一 `KEEP / CONTEXT_ONLY / DROP_FROM_MEMORY_OUTPUT` 主角色、S04 status gate、普通/Transition KEEP、candidate-empty Moment、同 Moment duplicate reason、同 Revision Packet 与 S07 handoff。V1.16 覆盖本文及 V1.6/V1.14 中与第四角色、空 Moment 删除、Transition 媒体质量或角色反向成为边界证据有关的旧表述。

> **当前 S07 覆盖：** [V1.17](CANONICAL_CHECKPOINT_V1_17_CHAPTER_AHA_CANDIDATE_GENERATION.md) 冻结 Chapter/Aha Candidate、Normal 与 Long-Manual Chapter path、局部 SINGLE/ADJACENT/RESUMED/LOCAL form、Aha 双门与 interval、duplicate/alternative、seed/candidate audit、有界 relation/group/candidate cap、immutable Revision 与 S08 provisional handoff。V1.17 覆盖本文中与 S07 candidate generation 有冲突的旧说明；S09 由 V1.19 覆盖，S10 Media 与真实数据阈值仍未冻结为实现结论。

> **当前 S08 覆盖：** [V1.18](CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md) 冻结 one-question ValidationTask、四类允许问题、双轴结果、A0/A1 与最低充分模态选择、bounded strong escalation、Evidence exposure envelope、VBU/真实美元双重预算、exact cache、retry/failure attribution、Revision/stale 与独立 ValidatedCandidate/AlternativeResolution。V1.18 覆盖本文及 V1.17 中将 S08 完整 action/cost/output 继续标为 OPEN 的历史表述；provider/model/price/prompt/schema 与真实校准仍为 OPEN。

> **当前 S09 覆盖：** [V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md) 冻结 selectable pool、SelectionRecord、typed relation graph、五种 executable constraint、八层 ordered set objective、state-conditioned deterministic search、两阶段 lineage、Day State、Preview/Final capacity、fifth gate、canonical output、S10 whitelist 与 downstream readiness。V1.19 覆盖本文及团队同步材料中将 S09 视为简单评分、Top-K 或未冻结建议的旧表述；Production schema、solver/state budget、reason enum、真实阈值、policy migration 与用户校准仍为 OPEN。

> **当前 S10 覆盖：** [V1.20](CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md) 冻结 Chapter/Aha same-story 与 embedded-distinct 边界；[V1.21](CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md) 冻结 Beat、Anchor、MediaDecision、Chapter/Aha 最终媒体、Hero、HQ request、bounded re-selection、D1/D2、cross-Memory reuse 与 activation revalidation。旧文中将 S10 细则视为 OPEN 的描述不再代表当前状态。

> **当前 S11–S13 覆盖：** [V1.22](CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md) 冻结 Grounded Narrative、Claim、Canonical Tag/Entity Index、Writer 与 actual-language verification；[V1.23](CANONICAL_CHECKPOINT_V1_23_FINAL_VALIDATION_AND_ATOMIC_DAY_STATE.md) 冻结 S12A/S12B 只读验证与 atomic authorization；[V1.24](CANONICAL_CHECKPOINT_V1_24_SELECTED_HQ_MATERIALIZATION_AND_EXPORT.md) 冻结 selected HQ、bounded activation、receipt、export/publish adapter；[V1.25](CANONICAL_CHECKPOINT_V1_25_PRODUCTION_SHAPED_PIPELINE_V1_0.md) 冻结 S00–S13 full-flow orchestration 并提供 media-free local reference。它们不等于真实云端 Production 已部署。

---

# 1. 决策语义与权威顺序

## 1.1 状态

| 状态 | 定义 |
|---|---|
| `FROZEN` | 明确冻结；除非显式重开，否则不得修改 |
| `BASELINE` | 当前实现/工程基线；可由真实实验升级 |
| `EXPERIMENTAL` | 隔离实验参数或路径；不得自动成为产品事实 |
| `OPEN` | 尚未决策；必须在指定阶段显式决定 |
| `SUPERSEDED` | 已被新方案替代，不能恢复成“当前设计” |
| `GAP` | 当前实现与目标规则不一致或尚未完成 |

## 1.2 冲突处理

1. 2026-08-18 之后用户明确重开的新决策。
2. Canonical Architecture V1.0 的 `FROZEN` 内容。
3. 本文对该基线的归纳。
4. 当前代码、实验默认值和 UI 文案。
5. 更早的讨论稿。

代码“已经这样写”不等于产品规则已经改变。

---

# 2. 总目标与损失函数

## 2.1 目标 — FROZEN

Diary One Cloud Intelligence 不是“把视频交给 VLM 总结”，而是：

> 在稀疏 wearable capture 条件下，以高 Precision、低 AI Cost、低 Phone→Cloud 数据量，把生活 Evidence 转换为对用户本人有意义的个人 Memory。

## 2.2 一级 KPI — FROZEN

1. Memory Quality
2. AI Cost
3. Upload MB / Wearing Hour
4. Phone Processing / Energy
5. End-to-End Latency

不能只优化模型 API 单价。

## 2.3 质量损失方向 — FROZEN

```text
False Memory / Unsupported Claim / False Merge
>
Missing Memory / Mild Over-segmentation
```

含义：

- 不为了页面丰满生成弱 Chapter。
- 不因两个片段看起来类似就跨时间错误合并。
- 没有足够证据时允许 `EMPTY_DAY`。
- Moment 宁可局部切碎，Chapter 层仍可重新组织；被污染的 Moment 会污染所有下游。

## 2.4 成本与时效 — FROZEN / BASELINE

| 项目 | 规则 |
|---|---|
| Cohort AI inference guardrail | `≤ US$1.50 / user / month` |
| Engineering expected target | 约 `≤ US$0.90` |
| Internal warning | 约 `$1.20` |
| Heavy user | 可以高于 `$1.50`，因为约束是 cohort average，不是单用户硬上限 |
| Latency | 不追求实时；允许约 1 小时甚至 overnight |
| 使用假设 | 约 15 wear days/month、5h reference day、40% intensity；当前约 900 Auto/month 的规划基线 |

成本账本至少分：Perception、Enrichment、ASR、Chapter、Aha、Narrative、Validation、Strong escalation、Retry waste；同时统计：

```text
$/user/month
$/wearing hour
$/100 assets
$/DailyMemoryRun
```

---

# 3. 核心对象定义

## 3.1 `RawAsset` — FROZEN

事实层对象，保存：

- 原始媒体引用；
- capture time / capture type；
- GPS / device metadata；
- media profile；
- sync provenance。

AI 结果不能覆盖事实字段。

## 3.2 `SourceSession`

连续研究时间轴。用于 P0/P1 Capture Simulator 和 Source-level Gold，不等于最终设备产生的单条 RawAsset。

同一 SourceSession 可以重放不同 capture policy，例如：

```text
120s / 9s
60s / 9s
90s / 6s
```

Source-level Gold 不随 capture policy 改变。

## 3.3 `LogicalAsset` / `ProxyAsset` — BASELINE

从连续 Source 推导出的逻辑时间窗：

```text
asset_id
source_id
source_start_ms
source_end_ms
duration_ms
```

默认只记录窗口，不生成独立 9 秒视频。只有某个实验确实需要视频输入时才 materialize，以避免：

- 重复存储；
- 不必要转码；
- 编码损失污染 Benchmark；
- capture policy 改变后重复生成文件。

## 3.4 `EvidenceRef` / `Evidence Window`

`EvidenceRef` 是可追溯到 RawAsset 的最小证据引用。Observation 可以和 RawAsset 一对一，也可以将一条长 Manual 视频拆成多个 Evidence Window。

`Evidence Window` 还是 Aha 的基础单位：Aha 可以出现在一个较长 Moment 内部的短局部峰值。

## 3.5 `Observation` — FROZEN

> AI 对最小可理解 Evidence 的结构化 perception。

> **当前输出覆盖：** V1.9 要求 Observation 只理解当前 Window；V1.10 要求固定字段 + 原子事实、逐语义条目绑定 Frame，并使用 `STRONG/MODERATE/WEAK` 证据支持等级，不再使用单一 Production `observation_confidence`。下方 V1.0 列表仅保留历史定义。

Observation 只回答“看到了/听到了什么”，不回答：

- 重要不重要；
- 是否是 Aha；
- 属于哪个 Chapter；
- 用户是否喜欢；
- 是否永久保存；
- 对用户意味着什么；
- 人物关系或情绪。

### Observation Lite

每条素材尽量都有的低成本信号，目标是支撑 continuity / boundary，而不是完整理解：

- time / GPS / Manual-Auto / duration；
- representative frames；
- quality / blur / exposure / occlusion / duplicate；
- embedding；
- coarse scene / activity；
- entity continuity hints；
- speech/audio gate；
- provenance / confidence。

### Observation Enriched

只对模糊、重要、最终候选或验证困难的 Evidence 使用更昂贵模型补充。

## 3.6 `Moment` — FROZEN

> 时间流中局部、语义相对纯净的生活 Episode。

Moment 不是完整活动，不是主题 Collection，也不等于持续时间内用户一直做某事。稀疏采集只能支持：多个 Observation 很可能属于同一个局部片段。

Moment 负责“切片”；Chapter 负责“组织意义”。

## 3.6A Observation Role Assignment — FROZEN V1.16

S06 在 S05 已提交完整 Moment partition 后，为每个 accepted Observation 分配且只分配一个主角色：

```text
KEEP
CONTEXT_ONLY
DROP_FROM_MEMORY_OUTPUT
```

- `KEEP` 只允许 `OBSERVED/PARTIAL`，且至少有一条当前 Window 的 `STRONG/MODERATE` grounded fact；
- `INSUFFICIENT_EVIDENCE` 禁止 KEEP，只能在具有独特、非 Claim 上下文用途时 CONTEXT_ONLY；
- `FAILED` 在当前已提交 Revision 中为 DROP；
- 多个 WEAK 不能投票升级或改写 S04 facts/support；
- CONTEXT_ONLY 不生成用户可见 Claim，也不计入精选媒体；
- DROP 不删除 RawAsset、Evidence、Observation、S05 membership、ledger 或独立 Manual 窗口；
- S06 role 不能成为或改写 S05 boundary evidence；
- 没有 KEEP 只退出内容候选，不删除或重并 S05 Moment；
- 普通 content-active Moment 可进入 Chapter/Aha candidacy；
- Transition content-active Moment 只进入 Aha candidacy；
- S06 检查 Evidence 可读性，S07 判断独立价值，S10 判断最终媒体质量；
- 每个 Moment 向 S07 交付一个共享 Packet，不按 KEEP 数量复制候选输入。

`MEMORY_SUPPRESSED_DUPLICATE` 是 CONTEXT_ONLY/DROP 的 reason，不是第四主角色。精确 Schema、threshold 与 reason taxonomy 仍需 Production 设计和真实数据校准。

## 3.7 `Event` — SUPERSEDED AS ENTITY

V1 不建立独立 Event 一级业务对象。Event Understanding 是内部算法过程；未来需要跨天旅行、项目、长期图谱时再重开。

## 3.8 `Chapter` — FROZEN

> 一天中值得作为独立、完整生活 Episode 再次呈现的 Editorial Object。

必要条件：

1. `Coherent`：能理解为一件事情；
2. `Worth remembering`：不是仅因发生过就展示；
3. `Distinct`：与当天其他 Chapter 足够不同。

Chapter：

```text
≠ Embedding Cluster
≠ Top-scoring Moments
```

采用：

```text
Candidate Generation
→ Semantic Scoring
→ Set Selection
```

V1.17 将 Candidate Generation 限定为局部 `SINGLE / ADJACENT_GROUP / RESUMED_EPISODE / LOCAL_EPISODE_GROUP`。Normal Chapter Candidate 至少需要 3 个 distinct KEEP RawAsset 与 3 个非重复 CandidateContentUnit；1–2 RawAsset 的 Long-Manual exception 必须保持 provisional，并经过 S08 MEDIA_DIVERSITY 验证。Candidate 不是最终 Chapter，全天 distinctness 与数量由 S09 决定。

## 3.9 `Aha` — FROZEN

> 短暂、局部，但具有独立记忆价值的瞬间；不需要构成完整 Episode。

核心：

```text
Local Semantic Delta
×
Independent Memory Value
```

Aha 不是低分 Chapter，也不是 Chapter 的缩略版。

V1.17 要求一个 Aha 只有一个 origin Moment 与一个 KEEP peak Window，支持范围最多 3 个连续 eligible Windows/3 分钟；Local Peak 与 Independent Memory Value 分别成立。普通 Moment 最多产生 3 个非重叠 Aha Candidate，Transition 最多 1 个且只依赖自身 KEEP。Aha Candidate 不是最终 Aha。

## 3.10 `EvidenceAnchor` — FROZEN

Chapter/Aha 已经选中后，用来决定“最终呈现哪一刻”的时间锚点。必须先选 anchor，再选择 PHOTO / LIVE_2S / VIDEO_5S。

## 3.11 `ChapterFacts` / `Claim Ledger`

Writer 的事实输入。Writer 不能重新决定 Chapter，也不能通过写作添加事实。

## 3.12 `DailyMemoryRun` — FROZEN

按 `User Local Day` 组织，而不是每次 Sync 新开整日处理。一天多次 Sync 做 incremental asset perception，高阶 Chapter/Aha 主要在 Finalization。

---

# 4. Daily Output 状态机

## 4.1 Frozen contract

```text
CHAPTER_DAY
→ 1–4 Chapters
→ + 0–3 Aha

HIGHLIGHT_DAY
→ 0 Chapter
→ exactly 1 strong Aha

EMPTY_DAY
→ 0 Chapter
→ 0 Aha
```

规则：

- 1 个强完整 Episode → 1 Chapter。
- 2 个强完整 Episode → 2 Chapters。
- 不再把 1–2 个 Chapter 自动降级成 Aha。
- `OPTIONAL` candidate 不用于凑数量。
- 只有没有合格 Chapter、但存在一个强局部瞬间时才使用 HIGHLIGHT_DAY。

---

# 5. Capture、画幅与 Evidence

## 5.1 Stage 1 capture baseline

```text
capture interval: 120 s
logical duration: 9 s
canonical frame positions: 1.5 / 4.5 / 7.5 s
geometry: portrait 3:4
materialize logical video: false by default
```

P0 Source 优先使用原生 portrait 3:4、wearable-like POV、连续录像。横屏 16:9 只能作为工具链数据，不能默认成为主 Benchmark；固定裁切时必须记录 transform。

## 5.2 Firmware media candidate — BASELINE CANDIDATE

| Mode | Resolution | FPS | Bitrate | 语义 |
|---|---:|---:|---:|---|
| Auto Video | 1080 × 1440 portrait 3:4 | 30 CFR | 6 Mbps | 高量、效率优先 |
| Manual Video | 1536 × 2048 portrait 3:4 | 30 CFR | 10 Mbps | 低量、高 intent、质量优先 |
| Manual Photo | 独立高分辨率 still pipeline | — | — | 用户主动记录 |

仍为 `EXPERIMENTAL/OPEN`：codec、CBR/VBR、GOP、Auto 4/5/6 Mbps、Manual 10 Mbps 真实收益、FOV consistency、mode switch latency。

Auto/Manual 应尽量保持相同有效 FOV，避免切换模式出现明显“突然放大”。

## 5.3 App arbitrary-media compatibility — EXPERIMENTAL

普通 iPhone 相册输入可以任意尺寸、方向和正时长：

- photo/video 派生 Evidence 统一为 768×1024 portrait 3:4；
- center crop + aspect fill；
- 视频在实际时长的 `1/6, 1/2, 5/6` 采样，对应内部 `1.5/4.5/7.5s`；
- 照片的同一事实帧写入三个 canonical position；
- 原始 hash/bytes/geometry/duration 保留在 provenance；
- 原始媒体不进入 Bundle。

这条路径用于工程联调，不能替代 wearable Source Benchmark。

---

# 6. 端云数据路径与数据暴露

## 6.1 Evidence-first — FROZEN DIRECTION

```text
DEVICE
↓
Phone Source Cache
↓
Evidence Generation
↓
Cloud Intelligence
↓
Chapter / Aha / Anchor Selection
↓
Selective HQ Source Request
↓
Phone uploads selected HQ window
↓
Memory Rendering
```

不再默认：

```text
Phone → Cloud full raw all-day upload
```

完整 Auto Raw 先作为 temporary phone cache；选中 Memory 后才申请 HQ source。

## 6.2 Representation benchmark

| Route | Representation |
|---|---|
| R0 / E02 | 3 representative frames |
| R1 / E04 | Frames + low-res temporal proxy |
| R2 / E03 | Full 9s source |

目标是最大化 `Memory Quality / Uploaded MB`，不是只找最小数据量。

## 6.3 Raw-volume interpretation

按 6 Mbps × 9s：每 clip 约 6.75 MB；约 30 clips/wearing hour → 202.5 MB raw/wearing hour；规划约 900 Auto/month → 约 6.1 GB Device→Phone raw/month。

这不等于 Phone→Cloud 必须上传 6.1 GB。

## 6.4 Third-party exposure — FROZEN

第三方多模态 API 默认 Level 1：

- representative frames；
- structured metadata；
- 必要短 Evidence。

Full 9s 只能作为 Benchmark-only Level 2 experiment，不能自动成为 Production 政策。

`OUR STORAGE != MODEL PROVIDER`。供应商还必须单独审查训练用途、保留、企业数据控制、Region、合同与隐私条款。

---

# 7. Observation / Perception 规则

## 7.1 Hybrid 端云分工 — FROZEN

```text
PHONE
Metadata
+ Frame Sampling
+ Basic Quality
+ Representative Evidence
+ Audio Gate

→ CLOUD
Embedding
+ Scene / Activity
+ Moment Formation
+ Selective VLM / ASR / Enrichment
```

具体能力可以因设备性能和隐私策略移动，但不能回到“所有 Raw 默认强 VLM”。

## 7.2 分层推理漏斗 — FROZEN

```text
T0 deterministic
T1 local lightweight
T2 embedding / classifier
T3 cheap generative
T4 strong reasoning
```

Router 目标：选择满足任务要求的最低成本能力，而不是默认最强模型。

## 7.3 低质量不等于删除

模糊、遮挡或重复只降低 visual reliability。音频或其他信号仍可能有价值；不能仅因视觉差直接 DROP。

## 7.4 Scene / Activity taxonomy — Stage 1 BASELINE

分类服务于 Moment Formation，不服务于“完整理解世界”。优先少、稳定、可复标。

Scene Family：

```text
UNKNOWN
HOME
WORKSPACE
FOOD_SERVICE
RETAIL_CULTURE
OUTDOOR_URBAN
OUTDOOR_NATURE
TRANSPORT
SPORT_RECREATION
EVENT_SOCIAL_VENUE
OTHER_INDOOR
OTHER_OUTDOOR
```

Activity Family：

```text
UNKNOWN
MOBILITY
WORK
DINING
INTERACTION
BROWSING
SPORT
LEISURE
REST
OTHER
```

`PET` 不是 Activity Family。例如：

```text
遛狗 = MOBILITY/WALKING + pet_present=true
和狗互动 = INTERACTION + pet_present=true
```

这样避免分类器在 MOBILITY/PET 之间抖动并制造假边界。

---

# 8. Moment Formation

> **当前结构覆盖：** V1.11 明确 S05 是连续 partition；V1.12 要求双向 BoundaryEvidenceLedger；V1.13 将 Moment Signature 冻结为 Multi-Prototype CoreContextSignature + TailSignature + PendingTransitionBuffer；V1.14 规定证据用尽且仍不能归左/归右时隔离为内部 Transition Moment；V1.15 冻结 DEFER 的有界证据范围、提前结束、Pending Block 与原子解析。单一 centroid 不能成为 Context 的唯一表示，DEFER 不能污染已确认 Core。

## 8.1 主方法 — FROZEN

```text
Metadata
+ Embedding
+ Scene / Activity / Context
+ Limited Rules
+ DEFER / Lookahead
```

禁止将“每两个素材调用一次强 VLM”作为主方法。

## 8.2 比较对象 — FROZEN

```text
New Observation
vs
Current Moment Signature
```

不是只比较前一条 Observation。V1.13 已覆盖此处旧的单一 centroid 方向：当前 Signature 使用 grounded motifs、多 visual prototypes、scene/activity distribution、匿名 entity/object hints、可信 location、first/last observed 与 evidence diagnostics；centroid 最多作为辅助特征。

## 8.3 Boundary 状态 — FROZEN

```text
MERGE
SPLIT
DEFER
UNRESOLVED
```

- V1.15 当前版本化 Baseline：最多 2 个可用后续 Window、最长 6 分钟 capture span、最多 3 个连续 Pending Window；未来只能通过 Benchmark 与新 Checkpoint 调整。
- App Sync/import batch 不是 capture session 或 Moment 边界；当前 Preview 输入结束时不等待下一次 Sync。
- 提前结束必须得到完整 local seam pattern；多个 Pending 使用同一不可变证据快照，并在判断结束后原子提交。
- RightEvidenceAnchor 必须位于两个可用 lookahead 的预算内，并且不得越过其他硬上限；若 origin 与两个后续 Window 均 Pending，`pending_block_max = 3` 已先到限，不得再读取下一条来挽救当前 Block。
- 仍 unresolved → precision-first conservative split；不能可靠归左/归右的 transition Window 按 V1.14 独立物化，不强行二选一。
- Hard Rules 必须极少；禁止用大量 cafe/dog/bookstore case patch 膨胀系统。

## 8.4 Boundary signals

当前结构化信号包括：

- time gap；
- location change；
- scene change；
- activity change；
- entity continuity；
- embedding/semantic continuity；
- interruption pattern；
- evidence confidence / quality。

Scene change 不自动等于 Moment boundary；Activity 相同也不保证同一 Episode。

## 8.5 Sparse-time semantics

Moment 使用 `first_observed_at / last_observed_at` 和 Evidence 间隙，不应把其解释成连续录像覆盖的 start/end。

---

# 9. Chapter Intelligence

## 9.1 Candidate scope — FROZEN

只允许在局部 Episode 范围组合：

```text
SINGLE
ADJACENT_GROUP
RESUMED_EPISODE
LOCAL_EPISODE_GROUP
```

V1 禁止全日任意主题聚类，例如上午和晚上遛狗不能只因语义相似自动合成 `Today's Dog Walks`。

## 9.2 Scoring / selection signals

可使用：

- episode continuity；
- semantic coherence；
- significance；
- personal relevance；
- day coverage；
- redundancy；
- evidence confidence。

Personalization 只能改变选择权重，不能改 Perception Facts。

## 9.3 Set rules — FROZEN / BASELINE

- Final Chapter `≤ 4`。
- Chapter 与 Chapter 的 Moment Set 当前 baseline 互斥。
- 高分优先，但不是单纯 Top-K；需做集合级 coverage/redundancy 选择。
- 1–2 个强 Chapter 直接展示，不降级。

## 9.4 X01 current gates — EXPERIMENTAL

- Candidate self-reported confidence `≥ 0.76`。
- 当前分数是模型对 evidence support 的自评分，不是校准概率。
- hero asset 必须在 candidate 所引用的 assets 内。
- candidate 必须引用有效 Moment、Frame 和至少一个合法 Claim。
- title ≤ 100 chars；story ≤ 700 chars；time label ≤ 80 chars；tags 最多 4。
- selected Chapters 不能共享 underlying assets；最多 4。

---

# 10. Aha Intelligence

## 10.1 Candidate sources — FROZEN

- local semantic delta；
- interaction；
- novelty spike；
- motion/event peak；
- Manual intent；
- personalization signal；
- 后续 audio signal。

Candidate 可以由 frame difference、motion peak、embedding change、subject appearance 等廉价信号先提名。

## 10.2 与 Chapter 的关系 — FROZEN

- Aha 与 Chapter 可以引用相同底层 Evidence。
- 最终输出必须控制 semantic redundancy。
- 不能因为素材适合 Live Photo 就反向把它选成 Aha。

## 10.3 X01 current gates — EXPERIMENTAL

- Candidate confidence `≥ 0.84`。
- 当前 hero 必须是 `PHOTO`。
- title/story 与已选 Chapter/Aha 的 token Jaccard `≥ 0.72` 时丢弃。
- 最多选择 3 个；但 `HIGHLIGHT_DAY` 按冻结规则应恰好 1 个，当前实现存在 GAP。

---

# 11. Representative Evidence 与 Media Editorial

## 11.1 Media types — FROZEN

Chapter：

```text
PHOTO
LIVE_2S
VIDEO_5S
```

Aha：

```text
PHOTO
LIVE_2S
```

Aha 不使用 5 秒 Video。

## 11.2 Hero — BASELINE / EXPERIMENTAL

- V1 Chapter Hero：PHOTO。
- Live Photo 稳定性、渲染、电耗和体验验证通过后，可实验 `Hero PHOTO → LIVE_2S`，甚至动态轮播。

## 11.3 Anchor-first — FROZEN

```text
Memory Selected
↓
Representative Evidence
↓
EvidenceAnchor
↓
Media Format Decision
↓
Render
```

不能分别先找“最好照片/最好视频/最好 Live”。

重要信号：semantic representativeness、event centrality、visual quality、subject clarity、motion value、temporal completeness、stability、evidence confidence。

> Motion Amount 不等于 Motion Value；剧烈晃动不代表适合 Live。

---

# 12. Narrative、Claim、Tag 与 Validation

## 12.1 Writer boundary — FROZEN

```text
ChapterFacts
↓
Claim Ledger
↓
Title / Story / Tag
↓
Claim Validation
↓
Publish
```

文本不是创作生活，而是表达已经确定的 Memory Facts。Writer 位于 Selection 下游，不能反向修改 Chapter/Aha。

## 12.2 Claim sources — FROZEN

```text
USER_CONFIRMED
OBSERVED
DEVICE_METADATA
MAP_LOOKUP
DERIVED
INFERRED
UNKNOWN
```

`INFERRED` 默认不能成为核心用户事实。

禁止无证据增加：人物关系、身份、情绪、意图、因果、地点、对白，以及 `old friend`、`beloved dog`、`productive day` 等表达。

## 12.3 Tag — FROZEN TARGET

```text
Canonical Concept
+ Display Label
```

禁止长期自由生成造成 `coffee / café / coffee shop / coffee time` 重复概念。

## 12.4 X01 claim validation — EXPERIMENTAL

- Claim type 只接受 `OBSERVED` 或 `DERIVED`。
- 每条 Claim 必须引用 Candidate 已声明且属于其 assets 的 frame IDs。
- 空 Claim、未知引用、无效 ledger、过长文案均拒绝。
- 目前 X01 在同一模型调用中同时生成 candidates、narrative 和 claims，是实验捷径，不是冻结 Production pipeline。

---

# 13. Personalization V1

## 13.1 Level 1 — FROZEN

- frequent activity；
- frequent location；
- entity cluster；
- tag history；
- Manual association；
- Chapter interaction signal。

暂不做：复杂 Knowledge Graph、关系推断、长期人物图谱、Autonomous Personal Agent。

```text
Personalization affects Selection
!= modifies Facts
```

用户删除 Memory 后，相关 personalization signal 至少要支持 invalidate / decrement / rebuild。

---

# 14. Model / Workflow Architecture

## 14.1 No Super Agent — FROZEN

```text
Deterministic Workflow
+ specialized models
+ selective reasoning
```

生成式推理集中在：ambiguous perception、candidate scoring、narrative、validation、targeted difficult verification。

## 14.2 Model Gateway — FROZEN TARGET

```text
Business Module
→ Model Gateway
→ Provider Adapter
```

业务代码不得散落供应商 SDK。Gateway 统一管理 model registry、modality、structured output、batch、cache、pricing、data exposure、fallback、escalation、cost trace。

Provider failure → fallback same tier；不能因供应商失败自动升级 Strong Model。只有 semantic inability 才允许 `T3 → T4`。

## 14.3 X01 adapter — EXPERIMENTAL

- 默认 Alibaba Model Studio `qwen3-vl-flash-2026-01-22`。
- OpenAI adapter 仅为显式 cross-vendor challenger。
- Fixture 只能做 contract test，不能展示为用户 Memory。
- 当前一轮多模态调用生成 Observation/Moment/Chapter/Aha 候选，再由本地严格校验。
- Qwen 选择每个 asset 的 4.5s 中间帧，并追加视频的其余帧，默认最多约 48 model frames；Bundle 本身仍包含每 asset 三帧。

Qwen 选择是当前研究默认，不是 Production provider 冻结结论。

---

# 15. DailyMemoryRun、Queue、Retry 与一致性

## 15.1 Run lifecycle — FROZEN

```text
OPEN
→ FINALIZING
→ READY
→ PUBLISHED
→ CLOSED
```

Pipeline stage：

```text
PENDING
RUNNING
SUCCEEDED
FAILED_RETRYABLE
FAILED_TERMINAL
STALE
SKIPPED
```

## 15.2 Processing — FROZEN

- 昂贵 asset perception 增量缓存。
- 当前阶段允许基于 cached observations 每天重新计算 full-day Moment，因为便宜且简单。
- Finalization 使用 immutable input snapshot。
- Late Data 创建 new revision，不修改当前 Finalizing Snapshot。

## 15.3 Queue / retry — FROZEN

- Queue 以 at-least-once 设计。
- 所有任务必须幂等。
- Provider failure 和 semantic inability 必须分开归因。

---

# 16. Benchmark 与评测

## 16.1 Stage 1 critical path — FROZEN

```text
S001
→ E00 Smoke
→ E01 Embedding Baseline
→ E02 Frame Cheap VLM
→ E03 Full 9s Cheap VLM
→ E04 Low-res Temporal Proxy
→ P0 Architecture Decision
→ P1 Native Revalidation
```

## 16.2 E00 — IMPLEMENTED, NOT ALGORITHMIC

```text
Source / App Evidence
→ Logical Assets
→ Frames
→ Embedding Adapter
→ Smoke Moment
→ EVAL_V01
→ Transfer/Cost Trace
→ HTML Report
```

当前实现：

- deterministic hash embedding，16 维；仅验证 adapter/provenance；
- smoke moment 将 observations 每两个一组；`algorithmically_meaningful=false`；
- EVAL_V01 使用 synthetic smoke gold；
- AI cost = 0、model calls = 0；
- artifact content-addressed，记录 JSON/hash/index/report；
- 不 materialize 9s clips；
- `leaderboard_eligible=false`。

任何 E00 F1 都没有架构决策意义。

## 16.3 E01 — FIRST VALID BASELINE

Zero-generative baseline，至少比较：

```text
Always Split
Always Merge
Time Only
Embedding + Structured Moment Engine
```

E01 才是第一个可进入正式 Moment Benchmark 的 baseline。

## 16.4 Evaluator layers — FROZEN

```text
Source Timeline Gold
↓
Capture Evaluation
↓
Observable Evidence
↓
Boundary Evaluation
↓
Predicted Moments
↓
Segment Evaluation
```

分别回答：设备是否有机会看到、看到后是否切对、最终 segment 结构是否合理。

### Observability

```text
OBSERVABLE
PARTIALLY_OBSERVABLE
UNOBSERVABLE
```

严格区分 Capture Error 与 AI Error。跨越真实 boundary 的 9s asset 需要按和 Gold Moment 的 overlap 投影，不能粗暴归到一边。

### Primary Moment metrics

- Boundary Miss Rate ↓
- Moment Purity / B³ Precision ↑
- Boundary F1 ↑

Secondary：Moment Completeness、False Split Discovery Rate、Moment Count Ratio、DEFER diagnostics。

### P1 top-level quality

不用单一 Overall Score：

- TRUTH：False Memory、Unsupported Claim、Severe Hallucination；
- RELEVANCE：User-approved Memory Precision、Bad Memory Rate；
- COVERAGE：Core Memory Recall、Critical Miss Rate；
- MEDIA：Temporal Hit、Semantic Hit、Memory-to-Media Consistency；
- SYSTEM：AI cost、Upload MB、Phone compute、Latency。

## 16.5 Gold-data discipline

```text
RAW_ANNOTATION (ANN_A / ANN_B independent)
→ REVIEWED_ANNOTATION (automatic diff)
→ GOLD_ANNOTATION (adjudication or AMBIGUOUS)
```

Benchmark Runner 默认只能读取 Gold；模型预测与标注文件物理隔离。

---

# 17. Data lifecycle 与隐私

## 17.1 Storage roles

| 数据 | 默认生命周期/原则 |
|---|---|
| Continuous research source | Research dataset policy；与产品用户数据分离 |
| Auto Raw on device/phone | Temporary source cache；具体 grace period OPEN |
| Representative frames / proxy | Temporary AI Evidence；小不等于永久保存 |
| Selected HQ source window | Temporary render source |
| Derived Chapter/Aha media | Persistent user Memory，直到用户删除/账户删除 |
| Manual originals | 用户主动记录；逻辑上长期保留直到用户删除 |
| Observation/Moment/Claims/Tags/Embeddings | 用户数据；生命周期与 User/Memory/Account 绑定 |

## 17.2 Logging — FROZEN DIRECTION

普通 application log 不得成为第二份用户数据库。禁止长期无差别记录完整 prompt、raw transcript、raw media URL、GPS、人物信息。

优先记录：request_id、asset_id、model、task、latency、tokens、cost、error code。Debug Evidence 通过受控 provenance 访问。

## 17.3 Deletion

删除必须沿 Provenance Graph 传播并 reference-aware；不能只删除 Chapter row，也不能暴力删除仍被其他 Memory/Manual 引用的 Source。

---

# 18. P1、基础设施与 Production 边界

## 18.1 P1 Shadow

真实硬件稳定后立即开始，不等正式 Backend：初始 3–5 testers、每人 3–5 wear days、约 20–50 total wearing hours。

必须记录 hardware/firmware/media profile、device→phone sync、phone evidence processing、phone→cloud bytes、HQ request、battery/thermal。

## 18.2 Infrastructure timing

现在应具备：公司控制的域名、Git、云账号、Private Object Storage、Model API Billing、Secrets、Budget Alerts。

现在不买：GPU、大型长期 CPU Server、Production DB cluster、CDN、Kubernetes、复杂 MLOps。

App Real Sync 时再引入 Staging API、PostgreSQL、Managed Queue、Async Worker、Object Storage；架构优先 Modular Monolith + Async Worker。

## 18.3 Production Region — OPEN L3

China Mainland / Global / Dual Region 在真实外部内测前锁定；P0/P1 R&D 不被它阻塞。

---

# 19. Superseded decisions

1. Auto Raw 全量默认上云 → Evidence-first + selective HQ。
2. Cheap VLM 固定 `<10% boundary` → 必须通过 E01–E04 Benchmark 决定全量低成本或选择性调用。
3. 每条 Asset 必须完整 VLM Caption → Observation Lite + selective enrichment。
4. Event 作为正式一级实体 → V1 仅为内部算法过程。
5. 每天固定 3–4 Chapters → 1–4 strong Chapters，不凑数。
6. 1–2 Chapters 自动降级 Aha → 取消；强完整 Episode 仍是 Chapter。

---

# 20. Open decisions

| OPEN | 决策节点 |
|---|---|
| Phone Auto Raw cache grace period | P1 telemetry |
| Frames / Proxy / Adaptive Evidence | E01–E04 + P1 |
| Production Region | 外部内测前 |
| Total Cloud COGS guardrail | Region + P1 后 |
| Late Data 是否自动修改已看 Memory | App Alpha 前 |
| Live Hero 是否成为默认 | Media UX Benchmark |
| Auto bitrate / codec / VBR | Firmware Benchmark |
| Device 是否直接产生 AI proxy stream | P1 后 |
| Strong model routing thresholds | P1/model benchmark |
| Personalization lift 门槛 | Alpha data |
| S07 relation/group/Aha cap calibration | 分层真实用户 Benchmark |
| S08 provider/model/price and VBU calibration | 分层真实用户 + provider telemetry Benchmark |
| S09 objective thresholds、discretization、solver/state budget 与 reason schema | 分层真实用户 + solver benchmark |
| S11 中文 D2e Title failure handling | 真实素材、人工评分与用户测试 |
| English/target-locale narrative contracts | 海外 release 前独立 locale eval/release gate |
| S13 codec/timebase/retry/SLO 数值 | 真实设备素材 + cloud benchmark |
| Persistent ledgers/queue/CAS/storage topology | Production engineering |

---

# 21. Current implementation GAP register

| GAP | Frozen target | Current X01/E00 state |
|---|---|---|
| G-01 Highlight Aha count | HIGHLIGHT_DAY exactly 1 Aha | X01 可选择最多 3 个 |
| G-02 Staged editorial pipeline | Perception→Moment→Role→Candidate→Targeted Validation→Set Selection→Media→Writer→Validator | X01 一轮模型调用 + local validator |
| G-03 Moment object | 多 Observation 的局部 Episode | App mapping 仍是一 Asset 一 Moment；模型 grouping 只用于 candidate association |
| G-04 Aha window/media | sub-Moment Evidence Window + PHOTO/LIVE_2S | X01 只有 frame refs + PHOTO hero，无 Live/render |
| G-05 Tags | Canonical Concept + Display Label | X01 仍是自由字符串；V1.22/V1.25 另有 closed-registry reference，尚未部署到 X01/Production |
| G-06 Confidence | 需要数据校准 | 0.76/0.84 为研究默认自评分门槛 |
| G-07 Benchmark | E01–E04 + Gold | 尚未完成；X01/E00 禁止进榜 |
| G-08 Production gateway | Router/cache/fallback/data policy | 当前仅 adapter boundary 和本地 Mac gateway |
| G-09 HQ rendering | selected anchor → HQ request → render | V1.24/V1.25 有 contract/reference receipt；真实 media bytes 未实现 |
| G-10 Personalization | Level 1 selection influence | 未实现 |
| G-11 S07 Candidate engine | V1.17 bounded Candidate/duplicate/audit/Revision/S08-handoff contract | X01 仍是一轮模型输出；Production schema、engine、Validator、persistent audit 与 lineage 均未实现 |
| G-12 S08 Validation engine | V1.18 one-question action tree、VBU budget、cache/failure/Revision/outcome contract | X01 仍是一轮模型输出；Production schema、budget service、router、queue、persistent cache、runner 与 outcome aggregator 均未实现 |
| G-13 S09 Selection engine | V1.19 pool/relation/constraint/objective/search/lineage/state/capacity/output contract | X01 仍是一轮模型输出；Production schema、solver、persistent ledgers/audit、state-budget benchmark、policy migration 与真实校准均未实现 |
| G-14 S10 engine | V1.20/V1.21 Beat/Anchor/Media/Hero/HQ/activation | 产品合同冻结；完整 engine/source benchmark 未实现 |
| G-15 S11–S13 cloud services | V1.22–V1.24 narrative/index/validation/materialization/export | 本地 control-plane reference 已实现；真实 Writer、renderer、store、CAS 未实现 |
| G-16 Full-flow Production | V1.25 S00–S13 orchestration | reference handoff validation 通过；真实 stage services、load/failure/eval 未实现 |

---

# 22. Active / queued / not now

## ACTIVE / IMPLEMENTED RESEARCH

- E00 runnable smoke harness；
- App arbitrary-media normalized bundle；
- X01 live Qwen evidence-only preview；
- strict local/server/App contract validation；
- transfer/token/cost trace；
- Diary Home experimental output including valid Empty Day。

## QUEUED

- E01 Moment baseline + Gold；
- E02/E03/E04 representation comparison；
- positive Chapter/Aha X01 test matrix；
- P1 native wearable revalidation。

## DESIGNED / NOT PRODUCTION-IMPLEMENTED

- Chapter/Aha Production；
- EvidenceAnchor/Media Editorial；
- staged Narrative/Tags/Validation；
- Personalization L1；
- DailyMemoryRun backend；
- Production Model Gateway。

## NOT NOW

- Super Agent；
- Knowledge Graph；
- GPU ownership；
- microservice swarm / Kubernetes；
- large MLOps platform；
- cross-day Chapter；
- chatbot memory。

---

# 23. 工作方法 — FROZEN

```text
Hypothesis
→ Implementation
→ Experiment
→ Error Attribution
→ Decision
→ Checkpoint
```

每 3–4 个关键模块做一次 Global Architecture Review；P0/P1/Production 关键节点发布新的 Canonical Checkpoint。真实实验之前，不用新的模型演示或主观感受静默改架构。
