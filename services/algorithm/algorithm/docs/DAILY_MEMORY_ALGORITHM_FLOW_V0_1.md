# Diary One Daily Memory Algorithm Flow V0.1

状态：ARCHITECTURE MAP / AMENDED THROUGH CANONICAL V1.25
用途：从一天的输入素材到最终 Diary 导出的完整算法流程索引。
方法：先固定全链路，再逐阶段讨论、实验和冻结；本文不代表所有阶段已经实现。

当前覆盖：S00 以 V1.1 为准；S01 以 V1.2 为准；S02 Auto/Manual 以 V1.3/V1.4 为准；S03 最小信号集以 V1.5 为准；Auto 1-or-3 与 Manual 候选抑制以 V1.6 为准；S04 全 Window 覆盖以 V1.7 为准；无感上传与 Auto 不补帧以 V1.8 为准；S03 信号拆分、S04 Window-local 事实和精确缓存复用以 V1.9 为准；S04 最小事实卡、状态、逐条 Frame grounding 与 evidence support grade 以 V1.10 为准；S05 连续 partition 以 V1.11 为准；S05 双向边界证据账本与四状态决策以 V1.12 为准；S05 多原型 Context Signature、Core/Tail/Pending 隔离和 commit-on-MERGE 以 V1.13 为准；证据用尽后的 unresolved Transition Moment 与 Aha/Context/Drop 路由以 V1.14 为准；DEFER 的两条可用后续 Window、6 分钟、3 Pending 有界 Baseline、完整 seam pattern 提前结束和原子解析以 `CANONICAL_CHECKPOINT_V1_15_BOUNDED_DEFER_LOOKAHEAD.md` 为准。

S06 当前覆盖：每个 accepted Observation 的唯一主角色、状态门、普通/Transition KEEP 条件、CONTEXT_ONLY/DROP、候选内容为空、同 Moment 重复抑制与 S07 handoff，以 `CANONICAL_CHECKPOINT_V1_16_OBSERVATION_ROLE_ASSIGNMENT.md` 为准。

S07 当前覆盖：Chapter/Aha Candidate、Long-Manual exception、局部 Resumed/Local group、Aha 双门、duplicate/alternative、seed/candidate audit、有界生成、Revision 与 S08 handoff，以 `CANONICAL_CHECKPOINT_V1_17_CHAPTER_AHA_CANDIDATE_GENERATION.md` 为准。

S08 当前覆盖：one-question ValidationTask、四类允许问题、双轴结果、最低充分动作树、Evidence exposure、VBU/真实美元双重预算、exact cache、retry/failure、Revision/stale、ValidatedCandidate/AlternativeResolution 与 S09 handoff，以 `CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md` 为准。

S09 当前覆盖：current-Revision selectable pool、SelectionRecord、typed relation graph、五种 executable constraint、八层 set objective、state-conditioned deterministic search、两阶段 lineage、Day State、Preview/Final capacity、fifth gate、canonical output 与 S10/S12 readiness，以 `CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md` 为准。

S10 当前覆盖：Chapter/Aha narrative independence 以 V1.20 为准；Content Beat、EvidenceAnchor、MediaDecision、Chapter 2/3–5 项、Hero、一次有界 re-selection、D1/D2、HQ request、Aha 单媒体、cross-Memory reuse 与 activation revalidation 以 V1.21 为准。

S11 当前覆盖：Facts、Claim Ledger、composition、中文 Title/Story/Time/Aha、Canonical Tag/Entity Index、Writer runtime 与 actual-language verification 以 V1.22 为准。

S12/S13 当前覆盖：两阶段只读验证与 atomic authorization 以 V1.23 为准；selected HQ materialization、bounded activation、receipt、export 与 publish adapter 以 V1.24 为准；S00–S13 全流程编排与本地 reference 以 V1.25 为准。

## 1. 最终目标

针对高强度参考日：

~~~text
5 小时佩戴
+ 150 个 Auto 9s Video
+ 20 个 Manual Photo
+ 10 个 Manual 15s Video
+ 3 个 Manual 60s Video
+ 3 个 Manual 120s Video

= 186 RawAsset / 34 分钟视频
~~~

算法将这些素材转换为：

~~~text
主要目标 3–4 Chapters
极强内容日允许第 5 个 Chapter
× 每章 3–5 个精选素材
+ 2–3 个 Aha Moments
~~~

这是“有足够强内容”的高强度 Benchmark 目标。产品全局冻结规则仍是：

~~~text
CHAPTER_DAY   → 1–5 Chapter + 0–3 Aha
HIGHLIGHT_DAY → 0 Chapter + exactly 1 strong Aha
EMPTY_DAY     → 0 Chapter + 0 Aha
~~~

3–4 是丰富日的目标区间，不是配额；第 5 个必须通过 V1.1 exceptional gate。没有足够证据时不凑数量。False Memory / Unsupported Claim / False Merge 的代价高于少生成一个 Memory。

## 2. 用户视角的一条直线

~~~text
原始素材
→ 变成低数据量、可理解的 Evidence
→ 看懂每个局部窗口发生了什么
→ 把全天时间流切成相对纯净的 Moments
→ 找出值得成为 Chapter / Aha 的候选
→ 从候选中选择一组互不重复、真正值得保留的 Memory
→ 为每个 Memory 选择准确的画面或短片
→ 只依据证据写标题和文字
→ 校验后导出 Diary
~~~

## 3. 算法与执行总图

~~~text
S00 DailyMemoryRun / Day Snapshot
  ↓
S01 RawAsset Intake
  ↓
S02 Evidence Builder
  ↓
S03A Window Intrinsic Signal + S03B Timeline Edge Signal
  ↓
S04 Observation Lite
  ↓
S05 Full-day Moment Formation
  ↓
S06 KEEP / CONTEXT_ONLY / DROP
  ↓
S07 Chapter / Aha Candidate Generation
  ↓
S08 Targeted Enrichment & Evidence Validation
  ↓
S09 Editorial Set Selection
  ↓
S10 EvidenceAnchor & Media Editorial
  ↓
S11 ChapterFacts / Claim Ledger / Narrative
  ↓
S12 Final Validation & Day State
  ↓
S13 Selected HQ Rendering & Export
~~~

生成式模型不是总控 Agent。流程由确定性 Workflow 驱动，模型只在需要理解、判断和写作的位置工作。

## 4. 三种运行时机

### 4.1 每次导入：增量准备

素材 Sync 后先在 Phone 增量准备并进入持久上传队列：

~~~text
RawAsset Intake
→ Evidence
→ deterministic signals
→ UPLOAD_1 / UPLOAD_3 route
→ local pending-upload queue
~~~

用户不需要第二次上传操作。约 1.5h 新增有效覆盖后可开始无感后台上传，约 2h 默认批量上传并启动 Cloud Observation；Manual、用户主动生成或 Final 可以提前 flush。相同素材、相同算法版本和相同参数不重复付费处理。

### 4.2 滚动 Preview Revision

固定的 12:00、17:00、20:00 不再是产品规则。触发依据是自上次成功 Editorial Revision 后新增的有效佩戴覆盖：

~~~text
约 1.5h 新增有效覆盖 → eligible for preview
约 2h 新增有效覆盖   → default preview attempt
strong Manual / semantic delta / user action → may trigger earlier
~~~

Preview 只对新增且尚未理解的 Evidence 执行昂贵 perception，但基于截至当前的全天累计 Observation/Moment 做 Chapter/Aha 集合判断。已有 Chapter 优先保持 stable ID 并被丰富；新的独立强 Episode 才累加新 Chapter；重复或错误切碎做受控合并。

触发不保证新增 Memory。没有达到质量门槛时输出 `NO_CHANGE`。

### 4.3 当天 Finalization

当天结束或用户触发整理时：

~~~text
冻结 immutable day snapshot
→ 重新计算全日 Moment
→ Candidate / Selection / Anchor / Narrative
→ Final Validation
→ Export
~~~

后到素材创建新的 Day Revision，不修改正在 Finalize 的输入快照。

## 5. 分阶段逻辑

### S00｜DailyMemoryRun / Day Snapshot

目的：明确“正在处理哪一天、哪一版素材”，并决定何时产生可追溯的 Preview 或 Final Revision。

输入：

- User Local Day；
- 多次同步的素材批次；
- 自上次成功 Editorial Revision 后的新增有效 coverage；
- Manual intent、semantic delta 与用户主动生成信号；
- Pipeline、参数和模型版本。

处理：

- 将同一 Local Day 的素材追加到一个 DailyMemoryRun；
- 每次导入只在 Phone 增量准备新增 Evidence、便宜信号和待上传队列；
- 约 1.5 小时新增有效覆盖后 eligible，约 2 小时默认触发 Preview attempt；
- strong Manual、明显语义变化或用户主动生成可以提前触发；
- Sync 后 Evidence 的 Cloud transfer 自动执行，不增加第二个用户上传交互；
- 每个 Preview/Final Revision 都冻结自己的不可变输入快照；
- 用户体验采用稳定累加：同一 Episode 丰富原 Chapter，独立强 Episode 才新增，重复内容受控合并；
- Finalization 无条件运行；
- late data 创建 new revision。

输出：DailyInputSnapshot、PreviewRevision 或 FinalRevision；未发现合格新增 Memory 时允许 `NO_CHANGE`。

这一阶段不理解媒体语义。它只根据已缓存信号和 coverage 决定是否启动后续 Editorial Workflow，并保证结果可重跑、可比较。昂贵素材理解不得因 Revision 重复执行。

### S01｜RawAsset Intake

目的：保存真实输入事实，不让 AI 改写。

每个 RawAsset 至少包含：

~~~text
raw_asset_id
capture_source = DIARY_ONE_AUTO | DIARY_ONE_MANUAL
media_kind = PHOTO | VIDEO
captured_at_utc
capture_timezone / local_day
capture_session_id
duration
source_ref
content hash / original media profile
sync_batch_id / ingested_at_utc
device / sync provenance when available
~~~

规则：

- 拍摄时间决定生活顺序，拍摄时的本地日期决定 Diary 归属；
- 导入时间只做同步追踪，不得改写拍摄时间或 local day；
- 同一 raw_asset_id 重复导入必须幂等，只追加 sync provenance；
- 时间不可信、文件损坏或事实冲突的素材进入 QUARANTINED，不静默猜测；
- Auto 与 Manual 来源不可伪造；
- Manual 是用户主动记录信号，但不自动等于重要或优质；
- AI 结果不能覆盖时间、来源、时长等事实；
- 当天输入按可信时间排序。

输出：有序、可追溯的 RawAsset Ledger、IngestDelta 与 Intake Audit。只有 accepted-new 且时间可信的 Auto Asset 增加滚动 coverage。

### S02｜Evidence Builder

目的：不上传全天 Raw 的前提下，把不同长度媒体变成可理解的局部窗口。

当前高强度 Phone 抽取容量基线：

| RawAsset | Evidence Window | Phone Extraction Frame Plan |
|---|---:|---:|
| 150 × Auto 9s | 150 | 450 |
| 20 × Manual Photo | 20 | 20 |
| 10 × Manual 15s | 20 | 40 |
| 3 × Manual 60s | 12 | 24 |
| 3 × Manual 120s | 18 | 36 |
| **Total** | **220** | **570** |

570 是手机侧完整 Evidence 抽取计划，不是固定 Cloud 上传量。若比例 `p` 的 Auto 通过保守 `UPLOAD_1`，则：

~~~text
Day baseline uploaded frames = 570 - 300p
~~~

当前冻结合同：

- Auto 9s：Phone 端 1 个 Window，固定且恰好抽取 1.5 / 4.5 / 7.5s 三个位置；只有三帧两两高度相似、质量信号完整且没有变化或不确定时上传一帧，否则上传全部三帧；
- Manual Photo：固定 1 个静态 Evidence / 1 帧；
- Manual Video：15s 固定 2 Window / 4 帧，60s 固定 4 / 8，120s 固定 6 / 12；每个连续窗口在约 1/3 与 2/3 位置取帧；
- Window 与 Frame Plan 全部指回 RawAsset，并按全天时间重新排序。

当前尚未实现：

- 从真实媒体生成 JPEG Evidence；
- Phone similarity / quality gate、`UPLOAD_1 | UPLOAD_3` route manifest 与无感上传队列；
- shot boundary / motion / semantic change 驱动的内容自适应窗口；
- temporal strip 或低分辨率动态 proxy；
- 实际 Phone compute、bytes 与视觉质量测量。

输出：

~~~text
EvidenceWindow[]
EvidenceFrame[]
Evidence provenance
~~~

### S03A｜Window Intrinsic Signal

目的：用便宜、稳定的信号描述每个 Window 自身，不调用生成式模型。

V1 最小信号：

- capture time / capture session identity；
- capture source / media kind / duration；
- blur、曝光、遮挡、稳定性；
- Window 内变化、motion amount 与 motion peak hint；
- Window 自身 perceptual representation；
- versioned lightweight visual embedding；
- Evidence reliability、provenance、error / UNKNOWN reason。

对 Auto，S03A 在 Phone 根据三帧两两 similarity、quality、变化与不确定性产生保守的 `UPLOAD_1` 或 `UPLOAD_3` route hint；缺失或冲突一律走 `UPLOAD_3`。路由只改变本次 Cloud 输入量，不删除 Phone Evidence 或 RawAsset。

可选信号：trusted GPS、audio-present / speech gate、可信 device motion metadata。缺失必须明确为 UNKNOWN，不能当作 false。

低画质不等于删除。它可能仍然提供边界、音频或上下文证据。S03 不做 Caption、人物/情绪/活动结论、Chapter/Aha 分数或最终 DROP。

输出：每个 Evidence Window 的 `WindowIntrinsicSignal`。

### S03B｜Timeline Edge Signal

目的：描述按时间排序的 Window 之间的关系，不改写任何 Window 自身事实。

至少包含：

- from/to Window ID；
- time gap / capture session continuity；
- visual similarity / perceptual distance；
- embedding distance；
- change / contradiction hint；
- version 与 provenance。

新或晚到素材插入时间线时，只失效和重建相邻的 Edge，不重新计算旧 Window 的 S03A 或 S04。默认从时间相邻 Edge 开始，更远邻域留给 S05 Benchmark。

输出：`TimelineEdgeSignal[]`。

### S04｜Observation Lite

目的：回答“这里能观察到什么”，不回答“这对用户意味着什么”。

输入：

- 实际上传到 Cloud 的 Evidence；
- 当前 Window 的 `WindowIntrinsicSignal`；
- 来源、时间和时长。

对 `UPLOAD_1` 的 Auto，Observation 必须知道 Phone 原本固定抽取了三帧及路由依据。若单帧不足以可靠理解，标记 `INSUFFICIENT_EVIDENCE` 并退出 Memory 候选；不请求另外两帧，也不上传完整 9 秒视频。

覆盖合同：

- 每个 accepted Evidence Window 都保留一个唯一、可追溯的 Observation Lite 记录槽位；
- 高强度参考日 220 Window 对应 220 个逻辑 Observation 记录，不等于 220 次模型请求；
- Auto 无论 `UPLOAD_1` 还是 `UPLOAD_3`，都只产生一个 Window Observation；
- 批处理可以减少 API 请求，但每个 Window 必须独立返回，不能混写 visible facts；
- 只有完全相同的 Evidence 输入与 pipeline 版本可以命中 Observation cache；near-duplicate 不复制语义事实；
- 顶层状态只使用 `OBSERVED / PARTIAL / INSUFFICIENT_EVIDENCE / FAILED`；`UNKNOWN` 只用于具体字段；
- 不确定时不能借用邻居素材补写当前 Window；失败与证据不足必须严格区分。

系统 Envelope 至少保存：

- Observation / Window / RawAsset ID 与可信 capture facts；
- 实际输入 Frame IDs、hash、offset 与 upload route；
- 顶层状态与 S04 最低候选门；
- schema、taxonomy、model、prompt、parameter 与 pipeline version；
- exact-cache、attempt、token、latency、retry 与 cost provenance。

允许输出：

- versioned coarse scene / directly supported activities；
- 当前 Window 内的匿名 visible entity / object；
- 少量、单一、可核查的 atomic facts；
- 由至少两个实际输入 Frame 支持的 within-window changes；
- 明确 limitations 与字段级 `UNKNOWN`。

每个肯定性 Scene、Activity、Entity、Object、Atomic Fact 和 Change 都必须引用当前 Window 的 supporting Frame，并分别标记 `STRONG / MODERATE / WEAK` evidence support。`UNKNOWN` 与输入缺失只记录明确原因，不伪造支持。`WEAK` 不能单独成为用户可见 Memory Claim。不设置单一 Production `observation_confidence`。

禁止输出：

- 长 Caption 或把多个事实拼成叙事；
- 是否值得记住；
- 是否属于 Chapter / Aha；
- 用户情绪、人物关系或主观意义；
- 人物姓名、身份、意图或因果；
- 永久保存决定；
- 没有 Evidence 支持的持续行为。

高强度容量示例：

~~~text
220 Window 全覆盖
8 Window / low-cost multimodal call
4 calls concurrent
≈ 28 Observation calls / 7 waves
~~~

8 Window/request 与 4 路并发只是待实跑的工程参数，不是冻结配置。后续 Benchmark 比较 batch、cache、reuse 与模型方案，但不得用删除逻辑 Window 的方式降低覆盖。

输出：符合 V1.10 最小合同的 Window-local Observation 列表。跨 Window continuity / boundary 不在 S04 判断。

### S05｜Full-day Moment Formation

目的：把完整时间序列切成局部、语义相对纯净的生活 Episode。

输入：Window-local Observation[] + TimelineEdgeSignal[]。

基础分段合同：

- S05 是对按 capture facts 排序后的 Window 序列做连续分段，不是全天语义聚类；
- 每个 accepted Observation 在 provisional partition 中恰好出现一次；
- Moment 之间不重叠、不重复，Moment 内成员保持时间连续和原顺序；
- 非相邻 Window 不进入同一个 Moment；中断后恢复的 Episode 关系留给 S07 以后；
- `INSUFFICIENT_EVIDENCE` / `FAILED` 不从时间线删除，也不能独立证明 MERGE；
- S05 只在 Window 之间切分，不伪造 sub-Window boundary；
- Moment 数量是内部切片数量，不等于 Chapter/Aha 数量。

比较对象：

~~~text
Immediate TimelineEdgeSignal
+ New Observation
+ Current Moment Signature
+ limited lookahead when DEFER
~~~

Moment Signature 采用：

~~~text
Multi-Prototype CoreContextSignature
+ TailSignature
+ PendingTransitionBuffer
~~~

其中：

- Core 只由已经确认属于当前 Moment 的可靠 Window 构成，至少表达 Activity Thread、grounded Context Motif、少量有界视觉 prototype、Scene/Activity distribution、可信 time/session/location、匿名 entity/object hint、support/contradiction 与完整 provenance；
- Tail 只保存最近少量已经确认 MERGE 的可靠 Window，用来识别近期自然变化；长度、时间跨度与衰减方式留给真实数据校准；
- Pending 临时保存 `DEFER` Window、关联 ledger 和 lookahead Trace，不是已确认成员，也不能改写 Core/Tail；
- 单一 embedding centroid 只可作为低成本辅助或诊断，不能成为 Context 的唯一表示；
- 新 Window 可以与 Core 中任一兼容 prototype 或互补 Motif 形成 continuity evidence，但单次匹配不能独立决定 MERGE；
- 只有 committed `MERGE` 才按时间顺序更新 Core/Tail；`DEFER → MERGE` 时原子性提交 Pending；`SPLIT` 时 Pending 不得污染旧 Core；
- `WEAK/UNKNOWN/INSUFFICIENT_EVIDENCE/FAILED` 不更新语义 Core；最终提交的 partition 仍须把每个 Window 确定地归属且只归属一次。

例如“石板路 → 传统建筑立面 → 石板路”不要求三条 Window 共享同一个物体。石板路与传统建筑可以分别形成互补 Motif 和视觉 prototype；若时间、Session、步行 Activity 与其他边界证据也支持连续，三者可以属于同一局部游览。相反，仅有相似风格不能证明真实地点是古镇、用户意图是 Citywalk，或把全天分散素材聚成同一 Moment。

每个相邻 seam 建立独立 `BoundaryEvidenceLedger`：

~~~text
continuity_evidence[]
+ boundary_evidence[]
+ neutral / unknown diagnostics
→ working state
→ committed action
~~~

证据至少可来自 time gap、capture session、Scene、Activity、embedding/visual distance、匿名 entity/object hint、可信 location 与 contradiction。每条 evidence item 必须保留方向、来源可靠性、引用和算法版本。

V1.10 的事实 `support_grade` 与边界方向不能混为一谈：一条 Scene change 可以被画面强支持，但仍可能只是同一次 Episode 内的转场。

边界状态：

~~~text
MERGE
SPLIT
DEFER
UNRESOLVED
~~~

当前原则：

- 所有 Observation 都参与边界判断；
- continuity 与 boundary evidence 分开保存，单一总分不能取代两本账；
- Scene、Activity、embedding、time gap、Manual、低画质或 UNKNOWN 均不能单独决定边界；
- `WEAK/UNKNOWN/INSUFFICIENT_EVIDENCE/FAILED` 不能制造肯定性 continuity；
- continuity 足够且 boundary 不足时 MERGE，反之 SPLIT；
- 两边都强或两边都弱时 DEFER；
- V1.15 当前版本化 Baseline：最多 2 个可用后续 Window、最长 6 分钟 capture span、最多 3 个连续 Pending Window；
- App Sync/import batch 不作为 Session 或 Moment 边界，当前 Preview 输入结束时不等待下次 Sync；
- 能形成完整 local seam pattern 时提前结束；只解决一个切口而另一个仍 DEFER 时继续使用剩余预算；
- 连续 Pending 使用同一不可变证据快照，从预算内左右参照向内解析并原子提交，不能贪心污染 Core/Tail；
- 右侧 Anchor 必须出现在两个可用 lookahead 的预算内且不越过其他硬上限；若 origin 与两条后续 Window 均 Pending，Block 长度已到 3，不再读取下一条来挽救当前 Block；
- 仍 unresolved 时 Precision-first 切开；若 transition Window 对左右都无法可靠归属，则独立物化为内部 Transition Moment，不强行归左或归右；
- 不仅比较前一条素材；
- 不用大量具体场景补丁代替通用边界逻辑。

一个已提交 Revision 必须具有确定的 Window membership；若 working state 仍为 `UNRESOLVED`，materialize 为保守切分并保留诊断。对于不能可靠归左或归右的过渡素材：

~~~text
A | B | C
    ↑
internal Transition Moment
~~~

B 后续只进入三路内容判断：`KEEP → Aha Candidate`、`CONTEXT_ONLY` 或 `DROP_FROM_MEMORY_OUTPUT`。Transition 不自动成为 Aha 或 Chapter；`DROP` 也不删除 RawAsset、Observation、BoundaryEvidenceLedger 或独立 Manual 窗口中的内容。

`A | B | C` 只表示 S05 的两个相邻边界已切开，不代表三个独立 Chapter。若 A、C 是同一次局部活动在 B 后恢复，S07 仍可建立 `RESUMED_EPISODE` 候选并让多个 Moment 共同服务于一个 Chapter Candidate。

Moment 只记录 `first_observed_at / last_observed_at` 和真实 capture gaps，不把两者之间解释为连续录像或持续活动。

输出：按时间排序、互斥且完整覆盖 S05 输入的 MomentSegment 列表、内部 Transition 标记，以及每个相邻 seam 的双向 BoundaryEvidenceLedger。

### S06｜KEEP / CONTEXT_ONLY / DROP

目的：在 S05 已提交完整 partition 后，决定每个 Observation 在该 Moment 中扮演什么内容角色，并形成 S07 的共享交接资料包。

~~~text
KEEP                   → 可靠内容资格
CONTEXT_ONLY           → 非 Claim 的正向上下文用途
DROP_FROM_MEMORY_OUTPUT → 退出 Memory 内容候选
~~~

规则：

- 先完整分段，再分配角色；
- 同一 Revision 中每个 accepted Observation 恰好一个主角色，可附多个 reason；
- `KEEP` 只允许 `OBSERVED/PARTIAL`，且至少引用一个当前 Window 的 `STRONG/MODERATE` grounded item；
- `INSUFFICIENT_EVIDENCE` 禁止 KEEP；只有独特、非 Claim 的上下文用途才可 CONTEXT_ONLY；
- `FAILED` 当前已提交 Revision 固定为 DROP，但底层时间、失败、Observation 与 ledger 保留；
- 多个 WEAK 不能投票升级，也不能改写 S04 facts/support；
- 普通 KEEP 还必须对当前 Moment 有可靠内容贡献；
- CONTEXT_ONLY 必须通过正向用途与去除测试，不能作为模糊兜底；
- DROP 只退出 Memory candidate/output，不删除 RawAsset、Evidence、Observation、S05 membership、ledger 或独立 Manual 窗口；
- S06 role 不能成为或改写 S05 boundary evidence；无论角色如何，既有双向 ledger 均继续保留；
- 同 Moment 明显重复按组处理；若内容本身通过 KEEP，至少保留一个基于 evidence reliability 的代表；
- `MEMORY_SUPPRESSED_DUPLICATE` 是 Context/Drop 的 reason，不是第四主角色；
- 对 V1.14 Transition Moment，KEEP 还要求内容可独立理解并具有具体短暂事件信号，而且只获得 Aha 候选资格；
- S06 只检查 Evidence 可读性；Aha 独立价值由 S07 判断，最终媒体质量由 S10 判断；
- 没有 KEEP 只表示候选内容为空，不删除 Moment，也不自动合并左右 Moment；
- 每个 Moment 输出一个共享 Packet；content-active 才输出 candidate seed，context-only 只输出 Context Envelope，全部 DROP 只保留结构与 audit 引用。

输出：Role-Assigned Moment Packet、Moment-level route、Context Envelope 与 audit references；精确 Production Schema 仍为 OPEN。

### S07｜Chapter / Aha Candidate Generation

目的：把 S06 content-active seed 转换为有证据、可审计、有界的 Candidate，但不决定最终页面。

Chapter 候选只允许来自局部 Episode：

~~~text
SINGLE
ADJACENT_GROUP
RESUMED_EPISODE
LOCAL_EPISODE_GROUP
~~~

禁止只因主题类似就把全天远距离片段拼成一章。

所有 Chapter 必须分别通过 Source、Truth、Local Episode、Coherence、Coverage、Memory Value、Inference Risk 与 Internal De-duplication gate。

~~~text
Normal path:
  distinct KEEP RawAsset >= 3
  non-redundant CandidateContentUnit >= 3

Long-Manual exception:
  1–2 RawAsset
  at least one Manual Video
  >= 3 temporally and semantically distinct grounded Manual-window units
  → always PROVISIONAL_VALIDATION_REQUIRED: MEDIA_DIVERSITY
~~~

局部 relation 使用当前版本化 Baseline：

~~~text
forward nomination horizon = 8 committed Moments
RESUMED intermediate max = 2 committed Moments
unsupported capture gap max = 30 minutes
group content-member safety max = 12
~~~

已成立 adjacent/local group 可以在 local + group-wide + material-gain 三门持续通过时逐步扩展到第 8 个 Moment 之外，但不能靠 pairwise similarity 无限传递。

Aha 必须同时通过：

~~~text
Local Peak Evidence
×
Independent Memory Value
~~~

- exactly one origin Moment 与 one KEEP peak Window；
- 最多 3 个连续 eligible Windows/3 分钟；
- ordinary Moment 最多 3 个互不重叠 Aha Candidate；
- Transition 最多 1 个，且只能依赖自身 KEEP；
- V1 不跨 Moment 组合 Aha；
- motion、scene change、漂亮画面或 Manual intent 不能单独通过。

Candidate disposition 为：

~~~text
ELIGIBLE
PROVISIONAL_VALIDATION_REQUIRED
SUPPRESSED_DUPLICATE
REJECTED
~~~

S07 只抑制当前 Evidence 已经证明的局部 duplicate/dominance；不确定的不同解释进入 alternative group。跨较长时间、不同 Episode 的相似素材不能只凭 embedding、scene、object 或 style 判重，全天冗余留给 S09。

每个普通 seed 最多 1 SINGLE、2 grouped hypotheses、3 Aha；Transition 最多 1 Aha。达到 cap 或 scope limit 必须留 Trace，不能静默丢弃。S07 不设全天 editorial Top-K。

S07 默认只使用缓存结构化数据与轻量比较，不新增上传、Auto 补帧、Raw request 或模型调用。只有具有明确 ValidationQuestion 的 provisional Candidate 才能申请 S08：Preview 最多 3 个、Final 最多 8 个。这只是数量 guardrail，不是完整成本预算。

S08 返回独立 ValidatedCandidate/AlternativeResolution/failure outcome，不回写 S07 Candidate disposition。

输出：ChapterCandidate、AhaCandidate、Alternative/Duplicate group、SeedAuditRecord、CandidateAuditRecord、S08ValidationRequest 与 S07RunTrace。

当前 V1.17 详细规则覆盖以下旧的说明性信号列表；这些信号仍只能作为对应 gate 的输入，不能替代 gate：

- episode continuity；
- semantic coherence；
- significance；
- personal relevance；
- evidence confidence；
- distinctiveness；
- inference risk。

Aha 是局部峰值，不是低分 Chapter。

相似 Manual 不享有候选豁免权，但素材仍完整保留在 RawAsset 事实账本与 App 独立 Manual 窗口。

### S08｜Targeted Enrichment & Evidence Validation

目的：只对 S07 已经声明的局部未知项花必要成本，并建立可信的 S09 eligibility。

V1.18 route：

~~~text
PROVISIONAL_VALIDATION_REQUIRED
→ one-question ValidationTask
→ A0 exact cache
→ A1 structured validator
→ choose one cheapest capable bounded modality
→ at most one capability escalation
→ independent S08 outcome
~~~

允许问题只有：

- `LOCAL_PEAK_CONFIRMATION`；
- `EPISODE_RELATION_CONFIRMATION`；
- `MEDIA_DIVERSITY_CONFIRMATION`；
- `ALTERNATIVE_RESOLUTION`。

ExecutionStatus 与 EvidenceDecision 分离：

~~~text
COMPLETED → PASS / FAIL / INCONCLUSIVE
NOT_RUN_BUDGET → NOT_EVALUATED
NOT_RUN_POLICY → NOT_EVALUATED
PROVIDER_FAILED → NOT_EVALUATED
CONTRACT_INVALID → NOT_EVALUATED
~~~

动作：

- A0 exact cache：0 VBU；
- A1 structured check：0 VBU；
- A2-V：最多 3 张已有 frame，minimum 1 VBU；
- A2-T：已有低分辨率 proxy，最多 2 excerpt / 6s，minimum 2 VBU；
- A2-A：已获许可的局部 audio，最多 15s，minimum 1 VBU；
- A3：相同或更小 payload 的 bounded strong model，minimum 4 VBU。

每个 Candidate 最多 2 个必要 task，每 task 最多 2 个 paid capability step。Preview 所有 Revision 全日累计最多 4 VBU；S08 全日累计最多 16 VBU；每天最多 2 个 task 启动 A3。真实 dispatch 还必须通过 provider 价格与 cohort monthly cost guardrail。

Provider failure 只能同级 retry/fallback；只有正常完成后的 capability semantic inability 才能升级。源证据缺失、遮挡、政策限制或无允许模态时直接停止。

S08 不补取 Auto `UPLOAD_1` 另外两帧，不请求默认 Raw，不做全天搜索，不修改 S04–S07。所有必要 task PASS 才生成 content identity 不变的 ValidatedCandidate；AlternativeResolution 独立输出。Budget/policy/provider/contract failure 不等于 Evidence FAIL。

输出：ValidationPlan、ValidationTask/Attempt/Outcome、CandidateValidationOutcome、ValidatedCandidate、AlternativeResolution 与 S08RunTrace。Production JSON Schema、provider/model/prompt/price 和真实阈值仍为 OPEN。

### S09｜Editorial Set Selection

**状态：FROZEN V1.19**

目的：从 S07/S08 已经合法的 Candidate 中选择一组整体最好的 Memory，而不是做单体 Top-K。

~~~text
DIRECT_ELIGIBLE + VALIDATED_ELIGIBLE
→ one SelectionRecord per current Candidate identity
→ typed relation graph + five executable constraints
→ pre-search protected-prior lineage constraints
→ state-conditioned deterministic set search
→ Day State + Preview/Final capacity
→ final lineage + canonical order
→ S10 whitelist or S12 empty validation
~~~

核心规则：

- excluded、unresolved、operational、stale Candidate 永不为了凑数入池；
- Chapter–Chapter RawAsset conflict、same Memory、alternative、nested、partial overlap、embedded Aha、distinct Episode 与 unresolved conflict 分开处理；
- pair conflict 不传递；embedding/scene/style 只能 nominate，不能单独证明重复或 distinct；
- 集合按 legality、每项边际贡献、Episode coverage、可信独立价值、低冗余/低风险、质量合格数量、Revision stability、精简/确定性八层顺序比较；
- 搜索同时维护 Chapter、Highlight 与 Empty 三种 state-conditioned 结果，不先选 winner 再裁剪；
- valid published Memory 不能仅因后来 ranking 下降而消失；merge/split 使用两阶段 lineage 与 group ledger；
- `CHAPTER_DAY` 优先于 `HIGHLIGHT_DAY`，`EMPTY_DAY` 必须有 exact empty proof；
- Preview 最多 4 Chapter / 2 Aha；Final 普通最多 4 / 3；第五章必须通过严格 set-level gate，全天 Chapter 硬上限为 5；
- 纯 Preview split overflow 保持上一版，等待 Final 完整决定，不隐藏 child 或假 merge；
- Chapter/Aha 成员确定后各自按 capture chronology + stable identity 确定性排序；
- S10/S12 不得静默替换 S09 membership。

~~~text
S09 does not:
  reread Raw
  upload/refetch media
  add model calls
  choose frames/formats
  write narrative
  declare PUBLISH_READY
~~~

输出：`S09ResultBundle / SelectedMemorySet / DayStateProposal / EditorialRevisionDelta / S10HandoffEnvelope / readiness`。

**案例：** 09:00 古镇、14:00 陶艺、20:00 生日都入选时，即使生日价值最高，成员资格先由集合目标决定，输出再按时间为古镇→陶艺→生日。普通通勤不能为达到 3–4 章补位。

### S10｜EvidenceAnchor & Media Editorial

**状态：FROZEN V1.20/V1.21。** 目的：在 Memory 已选中后，再决定最终展示哪一刻、用什么媒体。

顺序必须是：

~~~text
Memory Selected
→ Representative Evidence
→ EvidenceAnchor
→ Media Format
→ Render request
~~~

Chapter 媒体：

~~~text
PHOTO
LIVE_2S
VIDEO_5S
~~~

Aha 媒体：

~~~text
PHOTO
LIVE_2S
~~~

冻结结果还包括：

- Chapter Standard 3–5，strict Compact Pair Gate 可允许 2；
- Aha 恰好一个 PHOTO/LIVE_2S，无独立 Hero；
- Chapter Hero 恰好一个且来自正文；
- Primary + 0–2 Fallback、一次 D1、D2 healthy-primary lock；
- selected-only HQ request，dormant fallback 不预取；
- Chapter/Aha exact reuse 只有必要时合法，consumer identity 分离；
- runtime activation 后必须重验 affected S11/S12 artifacts。

Motion Amount 不等于 Motion Value。

输出：每个 Memory 的 EvidenceAnchor 与 MediaDecision。

### S11｜ChapterFacts / Claim Ledger / Narrative

**状态：FROZEN V1.22 current-Chinese test profile。** 目的：把已经确定的 Memory Facts 表达为用户能阅读的内容，并建立干净的记忆索引。

先生成：

~~~text
ChapterFacts / AhaFacts
Claim Ledger
~~~

每条 Claim 都必须记录：

- Evidence 来源；
- Observation 来源；
- evidence support grade；
- 是否经过 validation；
- 是否允许进入用户文字。

Writer 只能表达 Claim Ledger 中的事实，不能：

- 重新选择 Chapter/Aha；
- 添加人物关系；
- 添加用户情绪或意图；
- 把稀疏观察写成持续发生；
- 覆盖用户自己写下的记忆。

输出：grounded Title/Story/Time/Aha Moment Line、四分面 CanonicalTagDecision、typed EntityIndexLink、0–2 DisplayLabelCandidate 与 actual-language verification。

Chapter 默认一句、最多两句；Aha 只有一个中文当前测试≤20可见字符的 Moment Line。Tag 可以为零，不能自由造词，也不等于用户偏好。

### S12｜Final Validation & Day State

**状态：FROZEN V1.23。** 目的：在物化前与 runtime activation 后分别做只读硬门。

检查：

- Chapter/Aha 数量与状态机；
- Chapter 的 distinct RawAsset 数量；
- Chapter 间素材冲突；
- Chapter/Aha 语义重复；
- 所有 Claim 是否有 Evidence；
- Anchor 是否属于候选引用的 Evidence；
- 媒体格式是否合法；
- 不确定内容是否必须返回 exact owner replan/HOLD/BLOCK；
- Pipeline / model / prompt / parameter provenance 是否完整。

最终状态：

~~~text
CHAPTER_DAY
HIGHLIGHT_DAY
EMPTY_DAY
~~~

S12 不删除、降级或改写 exact artifact。失败返回 S09/S10/S11/S13 owner，或 HOLD/BLOCK；S12A 通过后才允许 S13A，S13A activation 后必须经过 affected S11 revalidation 与 S12B。发布使用 expected-head CAS。

### S13｜Selected HQ Rendering & Export

**状态：FROZEN PRODUCTION-SHAPED CONTRACT V1.24。** 目的：只为已经选中的 Memory 请求和生成最终媒体。

流程：

~~~text
Selected EvidenceAnchor
→ request selected HQ source window
→ render PHOTO / LIVE_2S / VIDEO_5S
→ receipt / checksum / provenance
→ predeclared activation if terminal
→ affected revalidation + S12B
→ atomic export / publisher CAS adapter
~~~

不默认上传全天 Auto Raw。

Transient/unknown 只 retry/HOLD，不能提前激活 Fallback；route 不得改变 Anchor 或 semantic scope。真实 codec、云存储、队列、CAS 与 HQ bytes 尚未实现，本地 reference receipt 明确不冒充真实 render。

对外导出分为两份：

#### User Diary Export

- day state；
- Chapter title/story/time；
- 每章 3–5 个媒体项；
- Aha；
- hero / media reference；
- 用户文本引用，但算法不得覆盖用户文本。

不向用户展示内部模型分数、淘汰原因和 Token。

#### Internal Audit Run

- immutable input snapshot；
- RawAsset → Evidence → Observation → Moment → Candidate → Memory provenance；
- rejected candidates；
- boundary evidence；
- model / prompt / parameter versions；
- token、cost、latency、retry、failure trace；
- evaluator 与人工标注引用。

## 6. 跨阶段成本原则

~~~text
T0 deterministic
→ T1 local lightweight
→ T2 embedding / classifier
→ T3 cheap multimodal
→ T4 selective strong reasoning
~~~

路由目标是满足任务所需的最低成本能力，而不是默认最强模型。

高强度日必须持续记录：

~~~text
AI cost / DailyMemoryRun
AI cost / wearing hour
AI cost / 100 assets
Phone→Cloud MB / wearing hour
Phone processing / energy
Finalization latency
Retry waste
~~~

## 7. 各阶段的主要评价指标

| Stage | 主要指标 |
|---|---|
| Evidence | Temporal Hit、Representative Coverage、Uploaded MB、Phone compute |
| Observation | Fact Precision、Unsupported Fact Rate、Uncertainty quality |
| Moment | Boundary Miss Rate、Moment Purity、Boundary F1、False Merge |
| Chapter | User-approved Memory Precision、Bad Memory Rate、Core Memory Recall |
| Aha | Aha Precision、Independent Memory Value、Redundancy |
| Media | Temporal Hit、Semantic Hit、Memory-to-Media Consistency |
| Narrative | Unsupported Claim、Fact Coverage、Overstatement |
| System | Cost、Latency、Retry、Failure attribution |

不能用一个 Overall Score 掩盖 Truth、Relevance、Coverage、Media 和 System 之间的差异。

## 8. 当前实现状态

| Stage | 当前状态 |
|---|---|
| S00 | V1.1 触发、Revision、累加与成本规则已冻结；完整实现尚未开始 |
| S01 | V1.2 事实合同已冻结；Production schema、IngestDelta、quarantine 和幂等实现尚未开始 |
| S02 | V1.3/V1.4 已冻结 Auto 与 Manual Evidence 数量，V1.6 冻结 Auto Phone 三帧抽取与 Cloud 1-or-3 分离；planning 已实现；真实媒体抽取、编码、路由、上传与成本测量未实现 |
| S03 | V1.9 已将固有 Window 卡片与关系 Edge 拆分；V1.6/V1.8 的路由和无感上传继续有效；两个 schema、局部失效、阈值、队列与 Trace 未实现 |
| S04 | V1.10 已冻结结构化事实卡、顶层状态、逐条 Frame grounding 和 evidence support grade；V1.7–V1.9 的全 Window、无补帧、Window-local 与 exact cache 继续有效；Production JSON Schema、模型、runner、Validator 和状态机未实现 |
| S05 | V1.11–V1.15 已冻结连续 partition、双向边界账本、四状态决策、多原型 Signature、Core/Tail/Pending 更新、unresolved fallback，以及当前有界 lookahead/atomic resolution Baseline；Motif/prototype engine、聚合阈值、schema、Validator、lookahead engine 和 Revision 更新策略未实现 |
| S06 | V1.16 已冻结唯一三角色、状态门、普通/Transition KEEP、Context/Drop、candidate-empty、同 Moment 重复与 S07 handoff；Production schema、engine、Validator 与真实数据校准未实现 |
| S07 | V1.17 已冻结 Chapter/Aha Candidate、Long-Manual exception、Resumed/Local group、Aha 双门、duplicate/alternative、审计、有界生成、Revision 与 S08 handoff；Production schema、engine、Validator、persistent audit、lineage matcher 与真实数据校准尚未实现 |
| S08 | V1.18 已冻结 one-question task、四类问题、动作/暴露范围、VBU/美元预算、cache/retry/failure、Revision/stale、independent outcome 与 S09 handoff；Production schema、budget service、router、queue、persistent cache、runner、outcome aggregator 与真实校准尚未实现 |
| S09 | V1.19 已冻结 pool、relation/constraint、八层 set objective、deterministic search、lineage、Day State、Preview/Final capacity、fifth gate、canonical output 与 readiness；Production schema、solver、persistent audit、benchmark 与真实校准未实现 |
| S10 | V1.20/V1.21 已冻结完整产品/算法合同；Production engine 与真实 HQ 尚未实现 |
| S11 | V1.22 已冻结并有 closed-registry/Claim/surface 本地 reference；真实 Writer、persistent ledger 与 locale/data calibration 未实现 |
| S12 | V1.23 已冻结并有 S12A/S12B 本地 validator；真实 database/CAS/App UX 未实现 |
| S13 | V1.24 已冻结并有 predeclared-route/reference receipt/export；真实 renderer/storage/publisher 未实现 |
| Full flow | V1.25 已提供 S00–S13 local reference；S00–S10 仅验证 handoff，不代表完整 stage engines |

## 9. 逐步讨论与研发顺序

之后每次只讨论一个阶段，并按同一模板形成结论：

~~~text
目标
→ 输入合同
→ Baseline 算法
→ 可比较方案
→ 输出合同
→ 质量指标
→ 成本与时延
→ 失败模式
→ 实验
→ 决策
~~~

当前顺序：

1. S01 RawAsset Intake：逐项冻结真实输入事实与多次导入合同；
2. S02 Evidence Builder：Auto 与 Manual Evidence 已锁定；真实媒体抽取属于后续工程实现；
3. S03A/S03B：Window 自身信号、时间线 Edge、Auto 路由和 Manual 重复抑制边界已锁定；
4. S04 Observation Lite：Window-local 覆盖、最小输出、batching、精确缓存和证据不足退出已锁定；
5. S05 Moment Formation：V1.11–V1.15 已锁定连续分段、双向边界账本、多原型 Core/Tail/Pending、unresolved Transition fallback，以及当前有界 DEFER/atomic resolution Baseline；
6. S06 Observation 角色分配已由 V1.16 锁定；
7. S07 Chapter/Aha Candidate Generation 已由 V1.17 锁定；
8. S08 Targeted Enrichment & Evidence Validation 已由 V1.18 锁定；
9. S09 Editorial Set Selection 已由 V1.19 锁定；
10. S10 已由 V1.20/V1.21 锁定；
11. S11 已由 V1.22 锁定；
12. S12/S13 已由 V1.23/V1.24 锁定；
13. V1.25 已完成 full-flow contract 与本地 reference；下一步进入真实标注日、stage engines、云端工程、成本/时延与用户验证。

在当前阶段，不展开隐私、伦理、Production Region、复杂治理平台、自训练、Knowledge Graph 或 Super Agent。
