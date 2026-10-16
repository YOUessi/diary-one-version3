# Diary One End-to-End Pipeline Logic — Team Sync V0.1

**状态：** TEAM SYNC DOCUMENT / AMENDED THROUGH CANONICAL V1.25
**日期：** 2026-08-29
**目的：** 用一份文档说明从用户一天的原始素材，到 Chapter/Aha、媒体、文字和最终 Diary 导出的完整逻辑结构
**当前权威范围：** S00–S13 以 V1.1–V1.25 冻结检查点为准
**历史说明：** 本文 S10–S13 的部分展开保留其最初方向稿；若出现“未冻结／可以删除”等旧表述，以 V1.20–V1.25 的后置 amendment 和 Canonical 文件为准
**仓库边界：** 本文只描述算法与逻辑接口，不修改 App、Firmware/SDK 或共享状态文件

---

## 0. 团队首先需要统一的三件事

### 0.1 最终产品目标

系统的任务不是“总结所有拍摄内容”，而是：

~~~text
从一天大量、稀疏、重复、质量不稳定的第一人称素材中
→ 理解发生了哪些局部生活片段
→ 找出真正值得记住的经历与瞬间
→ 选择一组互不重复、证据可靠的 Chapter / Aha
→ 为每个 Memory 选择准确的展示素材
→ 只依据证据写文字
→ 校验并导出 Diary
~~~

丰富日的目标是 3–4 个 Chapter；第 5 个是严格例外。Chapter Day 可以有 0–3 个 Aha；高质量丰富日希望得到 2–3 个，但不是配额。内容不足时允许更少，甚至 EMPTY_DAY。

**案例：** 用户拍摄了大量通勤、办公室和重复街景，但只有“古镇游览”“孩子生日”和“傍晚与家人散步”真正具有记忆价值。系统不应为了达到 4 个 Chapter，把普通午餐硬凑成一章。

### 0.2 质量优先级

~~~text
False Memory / False Merge
>
Missing Memory / 轻微切碎
~~~

也就是说：漏掉一个不确定瞬间通常可以接受；把不同经历错误合并，或者写出没有证据的事实，更不可接受。

**案例：** 吹蜡烛的关键瞬间被挡住时，宁可没有这条 Aha，也不能根据“这是生日场景”推测蜡烛一定被吹灭。

### 0.3 这不是一个 Super Agent

完整链路由确定性 Workflow 驱动。不同阶段各自解决一个问题，模型只在需要视觉理解、局部判断或文字表达时工作。

~~~text
事实不能被选择层改写
边界不能被文案层改写
候选不能被媒体美感反向创造
供应商故障不能变成内容失败
~~~

**案例：** 一张照片很好看，只能提高 S10 的媒体可用性；它不能反向证明这段普通街景值得成为 Chapter。

---

## 1. 状态标记

| 标记 | 团队含义 |
|---|---|
| FROZEN | 已确认的产品或算法架构规则；实现不能静默改变 |
| VERSIONED BASELINE | 当前可执行数值；未来只能由真实数据、显式版本和新检查点调整 |
| PROPOSED / NOT FROZEN | 为理解完整链路而给出的暂定逻辑；不能视为最终算法决定 |
| OPEN | 仍需要专项讨论、实验或工程确认 |
| IMPLEMENTATION GAP | 目标已经存在，但 Production 实现尚未完成 |

特别注意：

- S00–S09 的主干结构以 V1.1–V1.19 冻结；
- S10 以 V1.20/V1.21 为准；
- S11、S12、S13 分别以 V1.22、V1.23、V1.24 为准；
- V1.25 冻结全流程编排并提供本地 reference，但不代表云端 Production 已部署。

---

## 2. 一张图看完整链路

~~~text
REAL LIFE
  ↓
S00  DailyMemoryRun / immutable Revision
  ↓
S01  RawAsset Ledger
  ↓
S02  Evidence Window / Evidence Frame
  ↓
S03A Window Intrinsic Signal
  + S03B Timeline Edge Signal
  ↓
S04  Window-local Observation Lite
  ↓
S05  contiguous Moment partition
      + Continuity Evidence Ledger
      + Boundary Evidence Ledger
  ↓
S06  KEEP / CONTEXT_ONLY / DROP
  ↓
S07  Chapter Candidate / Aha Candidate
      + Duplicate / Alternative / Audit
  ↓
S08  targeted Validation
      → ValidatedCandidate / AlternativeResolution
  ↓
S09  SelectedMemorySet
      → selected Chapters / Ahas / Day State proposal
  ↓
S10  EvidenceAnchor + MediaDecision
      → 3–5 Chapter media items
      → focused Aha media
  ↓
S11  ChapterFacts / AhaFacts
      → Claim Ledger
      → grounded title / story / tags
  ↓
S12  Final Validation
      → CHAPTER_DAY / HIGHLIGHT_DAY / EMPTY_DAY
  ↓
S13  selected HQ request + render + export
      → User Diary Export
      → Internal Audit Run
~~~

最重要的对象演进：

~~~text
RawAsset
→ Evidence
→ Observation
→ Moment
→ Role-assigned content
→ Candidate
→ Validated / Eligible Candidate
→ Selected Memory
→ Anchored Media Plan
→ Grounded Narrative
→ Validated Diary
→ Export
~~~

---

## 3. 高强度参考日的容量收缩

用户一天较高强度使用：

| 输入 | 数量 |
|---|---:|
| Auto 9s Video | 150 |
| Manual Photo | 20 |
| Manual 15s Video | 10 |
| Manual 60s Video | 3 |
| Manual 120s Video | 3 |
| RawAsset 总数 | 186 |

Phone 端逻辑 Evidence：

| 类型 | Window | 抽取帧 |
|---|---:|---:|
| Auto | 150 | 450 |
| Manual Photo | 20 | 20 |
| Manual 15s | 20 | 40 |
| Manual 60s | 12 | 24 |
| Manual 120s | 18 | 36 |
| 总计 | 220 | 570 |

570 是 Phone 抽取计划，不是固定上传量。若比例 p 的 Auto 进入 UPLOAD_1：

~~~text
Cloud first-pass frames = 570 - 300p
~~~

从此以后，数据量逐级收缩：

~~~text
186 RawAssets
→ 220 logical Windows / Observations
→ bounded Moment partition
→ bounded S07 hypotheses
→ Final S08 frontier ≤ 8 provisional Candidates
→ S08 necessary tasks ≤ 16
→ rich-day target 3–4 Chapters + 2–3 Ahas
→ each Chapter 3–5 selected media items
~~~

S08 不重新理解 220 个 Window；S09/S10 也不回到全天 Raw 重新搜索。

**案例：** 即使用户在古镇连续佩戴 5 小时，后半段也只处理已经形成的 Candidate 和 CandidateContentUnit，而不是每到一个阶段都把 186 个 RawAsset 再发给模型一遍。

---

## 4. 核心对象词典

| 对象 | 简单含义 | 不能被误解成 |
|---|---|---|
| RawAsset | 一张真实照片或一段真实视频的事实记录 | AI 已理解的内容 |
| Evidence Window | 为算法观察一个局部时间位置而建立的窗口 | 最终 Chapter |
| Evidence Frame | Window 中实际提供给算法的代表画面 | 对整段视频的完整理解 |
| WindowIntrinsicSignal | 当前 Window 自身的便宜信号 | Caption 或 Memory 判断 |
| TimelineEdgeSignal | 相邻 Window 之间的变化与连续提示 | 最终 Moment boundary |
| Embedding | 把画面语义压成可比较的数字向量 | 事实、地点或用户意图 |
| Observation Lite | 只描述当前 Window 可看到的事实卡 | 故事或长期活动结论 |
| Moment | 时间上连续、语义相对纯净的内部生活片段 | 用户最终看到的 Chapter |
| BoundaryEvidenceLedger | 相邻位置支持连续与支持切开的双向证据账本 | 单一相似度分数 |
| KEEP | 可成为 Memory 内容的可靠 Observation | 一定会被最终选中 |
| CONTEXT_ONLY | 只帮助限制解释或说明过渡 | 隐形的 KEEP |
| DROP | 退出 Memory 输出候选 | 删除原素材 |
| Candidate | 有证据支持、可能成为 Chapter/Aha 的内部假设 | 最终 Memory |
| Revision | 某一时刻冻结的、不可变的一版全天输入与结果 | 可以被后到素材原地修改的对象 |
| ValidationTask | 只回答一个具体未知项的局部任务 | 重新理解全天的开放式 Prompt |
| SelectionRecord | S09 为了统一比较而建立的 Candidate 选择卡 | 新的 Candidate 或新事实 |
| Conflict Graph | 记录哪些 Candidate 重复、冲突、嵌套或可共存的关系图 | 按视觉相似度自动删除 |
| Lineage | 同一 Memory 在不同 Revision 之间的继续、扩展、合并或替换关系 | 直接复用旧 Revision 对象 |
| Content Beat | 一个已选 Memory 中值得用一个媒体项表达的独立内容位置 | 新的 Chapter |
| EvidenceAnchor | 最能代表一个已选 Memory 内容位置的精确证据点 | 最终媒体格式本身 |
| HQ Source Window | 只围绕已选 Anchor 请求的高质量源素材时间范围 | 全天原始素材上传 |
| Temporal Proxy | 低分辨率、短时序的动作证据 | 完整原视频 |
| ASR | 把语音转换成文字 | 自动理解情绪或人物关系 |
| VBU | S08 不同动作的相对成本重量 | 固定美元价格 |
| Claim Ledger | 用户可见文字中每个事实的证据清单 | 自由创作素材 |

---

## 5. 三种运行时机

### 5.1 用户每次 Sync：增量准备

~~~text
new RawAsset
→ Intake
→ Evidence extraction
→ cheap signals
→ UPLOAD_1 / UPLOAD_3 routing
→ persistent background queue
~~~

用户只操作一次 Sync。后续 Evidence 上传必须无感完成，不再增加上传交互。

**案例：** 用户上午导入古镇素材，下午又导入生日素材。两批素材进入同一 Local Day，但只对新增素材做抽帧和便宜信号。

### 5.2 Rolling Preview：白天可修订结果

~~~text
about 1.5h new valid coverage → eligible
about 2h new valid coverage   → default attempt
strong Manual / semantic delta / user action → may trigger earlier
~~~

Preview 对新增且尚未理解的 Evidence 执行昂贵处理，但基于截至当前的全天累计结果重新做 Moment、Candidate 和 Selection。没有足够新价值时可以 NO_CHANGE。

**案例：** 上午已经出现“古镇游览”Chapter；下午新增的是同一次古镇路线，系统优先丰富原 Chapter，而不是机械新增“古镇游览 2”。

### 5.3 Finalization：当天最终整理

~~~text
freeze immutable day snapshot
→ full-day Moment recompute from cached Observations
→ Candidate / Validation / Selection
→ Anchor / Narrative / Final Validation
→ selected HQ render / Export
~~~

Late Data 创建新 Revision，不修改正在 Finalize 的快照。

**案例：** 21:00 Final R5 已开始，21:03 新导入的一张照片创建 R6；它不能悄悄改变 R5 的 Chapter 内容。

---

## 6. 贯穿案例

后文每个阶段都使用同一个简化日型：

~~~text
09:40–10:30  古镇石板路、牌坊、传统建筑 A
10:32–10:48  进入现代奶茶店 B
10:50–11:30  继续古镇步行、寺庙和河边 C

18:30–18:35  家庭生日：
               准备蛋糕 D
               吹蜡烛 E
               鼓掌与合照 F

其余时间      通勤、办公室、重复街景与低质量素材
~~~

这一天可能最终形成：

- Chapter：古镇游览；
- Chapter：家庭生日；
- Aha：吹灭蜡烛；
- 其他普通或重复内容不一定进入 Diary。

这只是用于解释流程，不是预先指定的算法答案。

---

## 7. S00｜DailyMemoryRun / Day Snapshot

**状态：FROZEN V1.1**

### 目标

明确处理哪一个用户 Local Day、哪一版输入，以及何时启动 Preview/Final。

### 输入

- Local Day；
- 多次 Sync 批次；
- 新增有效佩戴 coverage；
- Manual intent / semantic delta / user action；
- pipeline、parameter、model versions；
- 上一成功 Revision 与已发布 Memory lineage。

### 处理逻辑

1. 同一 Local Day 的 accepted RawAsset 追加到同一 DailyMemoryRun；
2. 每次 Preview/Final 冻结 immutable input snapshot；
3. 相同素材、相同算法版本不重复执行昂贵理解；
4. Preview 采用稳定累加：丰富、合并或增加强 Episode，不随机重排；
5. Final 无条件运行；
6. Late Data 创建新 Revision；
7. 没有足够变化时允许 NO_CHANGE。

### 输出

~~~text
DailyMemoryRun
DailyInputSnapshot
PreviewRevision | FinalRevision
Trigger / NO_CHANGE audit
~~~

### 明确不做

- 不理解画面；
- 不决定 Chapter/Aha；
- 不用导入时间改写生活时间。

### 案例

上午古镇素材形成 Preview R2；晚上生日素材形成 R3。R3 的输入包含截至当时的古镇和生日素材，但不会重新收费理解 R2 已缓存且未变化的古镇 Evidence。

---

## 8. S01｜RawAsset Intake

**状态：FROZEN V1.2**

### 目标

建立不可被 AI 改写的事实账本。

### 输入

用户 Sync 后的 Auto/Manual 照片与视频及其设备事实。

### 处理逻辑

1. 使用 captured_at 和 capture timezone 决定生活顺序与 Local Day；
2. ingested_at 只记录何时同步；
3. raw_asset_id / content hash 保证重复导入幂等；
4. 记录来源、媒体类型、时长、Session 和 provenance；
5. 文件损坏、时间冲突等进入 QUARANTINED；
6. Manual 表示主动记录意图，但不自动表示重要；
7. 按可信拍摄时间排序。

### 输出

~~~text
RawAssetLedger
IngestDelta
IntakeAudit
~~~

### 明确不做

- 不生成语义；
- 不猜地点、人物或意图；
- 不删除被 Memory 层抑制的 Manual。

### 案例

用户晚上才导入上午 10:00 的古镇照片。它必须进入上午的时间位置，而不是被放到晚上的生日后面。

---

## 9. S02｜Evidence Builder

**状态：FROZEN V1.3 / V1.4 / V1.6 / V1.8**

### 目标

把不同媒体变成有界、可理解的局部证据，不默认上传全天 Raw。

### 固定 Evidence 合同

| RawAsset | Evidence |
|---|---|
| Auto 9s | 1 Window；Phone 固定抽 1.5 / 4.5 / 7.5s 三帧 |
| Manual Photo | 1 Window / 1 帧 |
| Manual 15s | 2 Window / 4 帧 |
| Manual 60s | 4 Window / 8 帧 |
| Manual 120s | 6 Window / 12 帧 |

Auto Cloud 路由：

~~~text
三帧两两高度相似
+ quality signals complete
+ no change / no uncertainty
→ UPLOAD_1

otherwise
→ UPLOAD_3
~~~

### 输出

~~~text
EvidenceWindow[]
EvidenceFrame[]
UploadRouteManifest
Evidence provenance
~~~

### 明确不做

- Cloud 不请求 UPLOAD_1 未上传的另外两帧；
- 不默认上传完整 Auto 9s；
- S08 也不能回来补取；
- 16s、73s 等非标准 Manual Window 仍为 OPEN。

### 案例

古镇 A 中三帧分别是石板路、建筑立面和路牌，不能因“都在古镇”只上传一帧；存在内容变化或不确定时应走 UPLOAD_3。

---

## 10. S03A｜Window Intrinsic Signal

**状态：FROZEN V1.5 / V1.9**

### 目标

用便宜信号描述 Window 自己，不调用生成式模型。

### 主要信号

- time / session / source / duration；
- blur、曝光、遮挡、稳定性；
- within-window change、motion amount、motion peak hint；
- perceptual representation；
- lightweight visual embedding；
- reliability、UNKNOWN/error reason；
- 可选 trusted GPS、audio-present、speech gate。

### 输出

~~~text
WindowIntrinsicSignal
~~~

### 明确不做

- 不写 Caption；
- 不判断人物关系或情绪；
- 不给 Chapter/Aha 分数；
- 低画质不自动删除。

### 案例

生日 E 的三帧显示明显亮度与火焰变化，S03A 只记录“变化明显”和 motion hint；它不能直接写“孩子吹灭了蜡烛”。

---

## 11. S03B｜Timeline Edge Signal

**状态：FROZEN V1.9**

### 目标

描述时间线上相邻 Window 的关系。

### 主要信号

- from/to Window；
- time gap；
- capture session continuity；
- visual / embedding distance；
- change / contradiction hint；
- provenance 和 version。

新素材插入时只重建相邻 Edge，不重算不受影响的旧 Window。

### 输出

~~~text
TimelineEdgeSignal[]
~~~

### 明确不做

- Edge 不是最终 boundary；
- 相似度不能单独决定 MERGE；
- Sync batch 不能作为生活边界。

### 案例

A→B 从室外古建筑变为室内奶茶店，边界提示增强；B→C 又回到室外。S03B 只记录变化，不决定 A/C 是否属于同一次 outing。

---

## 12. S04｜Observation Lite

**状态：FROZEN V1.7 / V1.9 / V1.10**

### 目标

回答“这个 Window 里能可靠观察到什么”。

### 输入

- 当前 Window 实际上传的 Evidence；
- 当前 Window 自身信号；
- capture facts。

### 处理逻辑

1. 每个 accepted Window 保留一个逻辑 Observation 槽位；
2. batching 可以减少请求，但不能把不同 Window 的事实混写；
3. 只引用当前 Window；
4. 肯定事实逐项绑定 supporting Frame；
5. 每条事实标记 STRONG / MODERATE / WEAK；
6. 只允许 OBSERVED / PARTIAL / INSUFFICIENT_EVIDENCE / FAILED；
7. 证据不足不补帧、不借邻居；
8. 只有完全相同输入和版本可以 exact-cache。

### 输出

~~~text
Window-local Observation Lite[]
Scene / Activity / Entity / Object
Atomic Facts / within-window Change
Limitations / UNKNOWN reasons
Cost and model provenance
~~~

### 明确不做

- 不判断是否值得记住；
- 不产生 Chapter/Aha；
- 不写长叙事；
- 不推断用户情绪、人物身份或因果；
- 不设置一个掩盖细节的总置信分。

### 案例

奶茶店 B 可以观察到“室内、饮品杯、柜台、手持饮品”；不能写“用户休息并享受惬意时光”。

---

## 13. S05｜Full-day Moment Formation

**状态：FROZEN V1.11–V1.15**

### 目标

把全天 Window 时间序列切成连续、互斥、完整覆盖的内部生活 Episode。

### 输入

~~~text
ordered Observation Lite[]
+ TimelineEdgeSignal[]
~~~

### 处理结构

~~~text
Immediate Edge
+ New Observation
+ Multi-Prototype CoreContextSignature
+ TailSignature
+ bounded PendingTransitionBuffer
→ BoundaryEvidenceLedger
→ MERGE / SPLIT / DEFER / UNRESOLVED
~~~

两本证据账：

~~~text
continuity_evidence[]
boundary_evidence[]
~~~

当前 DEFER Baseline：

- 最多读取 2 个可用后续 Window；
- 最长 6 分钟 capture span；
- Pending Block 最多 3 Window；
- 仍不能判断时 precision-first materialize；
- 无法归左/归右的过渡 Window 独立成为 Transition Moment。

### 输出

~~~text
MomentSegment[]
TransitionMoment markers
BoundaryEvidenceLedger per seam
Moment signatures and resolution trace
~~~

### 明确不做

- 不做全天主题聚类；
- 非相邻 Window 不进入同一 Moment；
- Moment 数不等于 Chapter 数；
- 不把 first/last observation 写成连续录像覆盖。

### 案例

~~~text
A 古镇 | B 奶茶店 | C 古镇
~~~

S05 可以切成三个 Moment。它不会因为 A/C 相似就跨过 B 合成一个 Moment；是否属于同一次 outing 的恢复关系留给 S07。

---

## 14. S06｜Observation Role Assignment

**状态：FROZEN V1.16**

### 目标

在 Moment partition 已确定后，为每个 Observation 分配唯一内容角色。

~~~text
KEEP
CONTEXT_ONLY
DROP_FROM_MEMORY_OUTPUT
~~~

### 处理逻辑

- KEEP 只允许 OBSERVED/PARTIAL，并至少有一个 STRONG/MODERATE grounded item；
- CONTEXT_ONLY 必须有明确、非 Claim 的正向用途；
- FAILED 固定 DROP；
- INSUFFICIENT_EVIDENCE 禁止 KEEP；
- 同 Moment 重复内容可以保留一个可靠代表；
- Transition KEEP 只获得 Aha 候选资格；
- 无 KEEP 只表示 Moment candidate-empty，不删除 Moment；
- DROP 不删除 RawAsset、Observation、ledger 或 Manual 窗口。

### 输出

~~~text
RoleAssignedMomentPacket
content-active seed
ContextEnvelope
RoleAudit
~~~

### 明确不做

- 不改变 S04 fact；
- 不改变 S05 membership 或 seam；
- 不判断最终 Memory；
- 不因为 Manual 就绕过相似抑制。

### 案例

奶茶店 B 如果只是重复、普通且对古镇经历有时间解释价值，可以成为 CONTEXT_ONLY；它仍保留在事实账本和 Manual 窗口，但不必成为 Chapter 内容。

---

## 15. S07｜Chapter / Aha Candidate Generation

**状态：FROZEN V1.17**

### 目标

把 content-active Moment seed 转为有证据、可审计、有界的 Memory 假设。

### Chapter Candidate form

~~~text
SINGLE
ADJACENT_GROUP
RESUMED_EPISODE
LOCAL_EPISODE_GROUP
~~~

Normal Chapter：

~~~text
distinct KEEP RawAsset >= 3
non-redundant CandidateContentUnit >= 3
~~~

Long-Manual exception：

~~~text
1–2 RawAsset
+ at least one Manual Video
+ >=3 time/semantic distinct grounded Manual-window units
→ always provisional MEDIA_DIVERSITY validation
~~~

Relation Baseline：

- forward nomination horizon：8 committed Moments；
- RESUMED intermediate：最多 2；
- unsupported capture gap：最多 30 分钟；
- group content member：最多 12。

### Aha Candidate

~~~text
Local Peak Evidence
×
Independent Memory Value
~~~

- one origin Moment；
- one KEEP peak Window；
- 最多 3 个连续 eligible Windows / 3 分钟；
- ordinary Moment 最多 3 个非重叠 Aha；
- Transition 最多 1 个；
- V1 不跨 Moment 组合 Aha。

### Candidate 状态

~~~text
ELIGIBLE
PROVISIONAL_VALIDATION_REQUIRED
SUPPRESSED_DUPLICATE
REJECTED
~~~

### 输出

~~~text
ChapterCandidate[]
AhaCandidate[]
AlternativeHypothesisGroup[]
DuplicateCandidateGroup[]
SeedAuditRecord[]
CandidateAuditRecord[]
S08ValidationRequest[]
S07RunTrace
~~~

### 明确不做

- 不做全天 Top-K；
- 不选择最终 3–4 Chapter；
- 不生成 Narrative；
- 不选择最终媒体；
- 不新增上传、补帧或模型调用；
- 只有已证实 duplicate/dominance 才抑制。

### 案例

A/C 可以形成 RESUMED_EPISODE；A+B+C 可以形成 LOCAL_EPISODE_GROUP。如果两种解释都有独立意义且 dominance 未证实，它们进入 local alternative，而不是提前删除其中一个。

---

## 16. S08｜Targeted Enrichment & Evidence Validation

**状态：FROZEN V1.18**

### 目标

只回答 S07 已声明的一个局部未知项，以最低充分成本建立可靠 eligibility。

### 允许问题

~~~text
LOCAL_PEAK_CONFIRMATION
EPISODE_RELATION_CONFIRMATION
MEDIA_DIVERSITY_CONFIRMATION
ALTERNATIVE_RESOLUTION
~~~

### 动作选择

~~~text
A0 exact cache
→ A1 structured validator
→ choose one:
     A2-V lightweight vision
     A2-T existing temporal proxy
     A2-A gated audio / ASR
→ optional A3 bounded strong model
→ STOP when evidence is exhausted
~~~

最大媒体范围：

| Action | 范围 |
|---|---|
| A2-V | 最多 3 张已有 Frame |
| A2-T | 最多 2 个已有 proxy excerpt，总计 ≤6 秒 |
| A2-A | 一个已允许 audio excerpt，≤15 秒 |
| A3 | 与前一步相同或更小 |

预算 Baseline：

| 项目 | 上限 |
|---|---:|
| necessary task / Candidate | 2 |
| paid capability step / task | 2 |
| Preview 全日累计 | 4 VBU |
| S08 全日累计 | 16 VBU |
| A3 task / day | 2 |

结果双轴：

~~~text
Execution:
COMPLETED / NOT_RUN_BUDGET / NOT_RUN_POLICY /
PROVIDER_FAILED / CONTRACT_INVALID

Evidence:
PASS / FAIL / INCONCLUSIVE / NOT_EVALUATED
~~~

### 输出

~~~text
ValidatedCandidate[]
AlternativeResolution[]
CandidateValidationOutcome[]
Validation audit / cost / exposure trace
~~~

### 明确不做

- 不验证 Memory Value；
- 不重新理解全天；
- 不扩大 Evidence；
- Provider failure 不升级强模型；
- Budget/Policy/Provider/Contract failure 不等于内容 FAIL；
- 不回写 S04–S07。

### 案例

古镇 A/C relation 可以先由已有 ledgers 做 A1；证据不足但路牌清晰、只是轻模型理解不了时才允许 A3。若路牌根本没拍到，直接 INCONCLUSIVE，不补取 Raw。

---

## 17. S09｜Editorial Set Selection

**状态：FROZEN V1.19**

本节是团队解释层；完整权威合同见 [V1.19 Editorial Set Selection](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md)。V1.19 冻结结构、顺序与安全边界；真实阈值、Production schema 与 solver benchmark 继续 OPEN。

### 17.1 目标

不是选择分数最高的几个单体 Candidate，而是选择一组整体最好的 Daily Memory：

- 每个 Memory 自身有价值且有证据；
- 覆盖当天主要强 Episode；
- Chapter 之间不重复；
- Chapter 与 Aha 不表达同一个 Memory；
- 保持 Preview Revision 稳定；
- 不为达到数量目标加入弱内容。

### 17.2 输入接口

~~~text
S07 ELIGIBLE Chapter/Aha Candidates
+ S08 ValidatedCandidates
+ AlternativeResolution
+ Candidate / Seed audits
+ prior Revision lineage
+ day-level product limits
~~~

以下对象不得进入 selectable pool：

- S07 REJECTED；
- S07 SUPPRESSED_DUPLICATE；
- 未通过 S08 的 provisional；
- S08 UNRESOLVED_EVIDENCE；
- S08 UNVALIDATED_OPERATIONAL；
- stale Revision result。

### 17.3 冻结逻辑结构

#### Step 1｜Pool contract validation

确认所有 Candidate 属于当前 Revision，内容引用合法，所有必要 gate 已成立。

**案例：** 一个旧 Preview 的生日 Candidate 即使 PASS，也不能直接混入当前 Final，除非已经为当前 Revision 创建合法 wrapper。

#### Step 2｜Candidate normalization

把不同来源统一为可比较的 SelectionRecord，但不丢失 Candidate type、Episode basis、Validation 和 provenance。

SelectionRecord 保留六组多维、可追溯 basis：

- identity/version；
- Memory scope；
- trust/validation/provenance；
- Memory value、Episode coherence 与 Manual intent；
- relation inputs；
- prior Revision lineage 与 policy versions。

`distinctness / day coverage gain / redundancy / revision stability / fifth increment` 取决于当前 set，不能预写成 Candidate 自身属性。V1.19 禁止把所有信息压成一个“真理总分”。

**案例：** Manual 生日视频可以提高个人相关性，但如果事实证据弱，不能仅靠 Manual 权重胜过证据清晰的古镇 Chapter。

#### Step 3｜Conflict and relation graph

建立 Candidate 之间的集合关系：

~~~text
IDENTITY_CONFLICT
CHAPTER_RAW_ASSET_CONFLICT
EXCLUSIVE_ALTERNATIVE
SAME_MEMORY_REDUNDANCY
NESTED_DOMINANCE
PARTIAL_OVERLAP
EMBEDDED_DISTINCT_AHA
DISTINCT_EPISODE
UNRESOLVED_POTENTIAL_CONFLICT
~~~

每个 pair 使用双向 Evidence ledger，同时保存 same 与 distinct evidence。Embedding、scene、object、style 只能 nominate；pair conflict 不沿 connected component 传递。

**案例：** “古镇 A/C resumed”与“古镇 A+B+C broader”可能是 alternative；“上午遛狗”与“晚上遛狗”虽然语义相似，但不是同一 local conflict。

#### Step 4｜Hard set constraints

五种执行结果：

~~~text
CONTRACT_BLOCKED
FORBID_COSELECT
CONSERVATIVE_AT_MOST_ONE
ALLOW_WITH_REDUNDANCY_COST
ALLOW_COSELECT
~~~

同时执行当前数量边界：

- CHAPTER_DAY：1–5 Chapter + 0–3 Aha；丰富日目标 3–4，但不是配额；
- Preview：最多 4 Chapter / 2 Aha，第五章 gate 关闭；
- Final：普通最多 4 Chapter / 3 Aha；第 5 个必须通过七道 set-level exceptional gate；
- HIGHLIGHT_DAY：0 Chapter + exactly 1 strong Aha；
- EMPTY_DAY：0 Chapter + 0 Aha；
- Chapter 间当前 Baseline 不共享 underlying RawAsset；
- Aha 可以与 Chapter 引用相同 Evidence，但不能表达重复 Memory；
- Long-Manual exception 已经通过 S08 才可参加；
- 数量目标不是最低配额。

**案例：** 当天只有“生日”和“古镇”两个强 Chapter，就输出两个；不能把普通通勤作为第三章。

#### Step 5｜Set construction

V1.19 使用八层有序目标，而不是加权总分：

~~~text
1 legality and trust
2 every member materially contributes
3 meaningful Episode coverage
4 trusted independent Memory value
5 low redundancy and inference risk
6 quality-qualified target count
7 Revision stability when near-equivalent
8 parsimony and deterministic tie-break
~~~

Baseline 是 state-conditioned deterministic constrained search：先遍历 Chapter skeleton，再为仍可能获胜的 skeleton 接入 Aha，对完整 plan 联合比较；同时维护 Chapter、Highlight 与 Empty 三种结果。禁止先选 generic winner 再裁剪，也禁止 naive 238B Cartesian enumeration。

Search status 区分 `EXACT_WITHIN_POLICY / BEST_LEGAL_WITH_SEARCH_LIMIT / SEARCH_OPERATIONAL_FAILURE`；受限搜索不得伪装全局最优或 exact empty proof。

**案例：** 两个古镇 Candidate 单体都很强，但选择其中一个加生日，通常比同时选择两个古镇版本更能覆盖当天。

#### Step 6｜Revision stability

Lineage 分两阶段：search 前建立 prior/current pair/group compatibility 与 protected-successor constraints；plan 选定后再完成 `CONTINUES / EXPANDS / MERGES / SPLITS / SUPERSEDES / NEW_INDEPENDENT` 与 stable-ID 动作。

Preview 中仍有效的用户可见 Memory 受 hard retention guard 保护：

- enrich；
- preserve stable identity；
- controlled merge；
- 只在证据明显改变时 replace/remove。

后来 Candidate ranking 更高不是 eviction reason。稳定性不能保护错误事实，也不能阻止合法 merge/split/invalidation。纯 Preview split correction 若从四章变五章，保持上一版等待 Final，不发布 partial correction、不隐藏 child、不开 Preview 第五章。

**案例：** 上午已显示“古镇游览”，下午新素材补充寺庙，应丰富原 Memory；晚上新增生日则可以增加独立 Chapter。

#### Step 7｜Day state proposal

~~~text
revision state-decidable?
├─ no → DAY_STATE_NOT_PROPOSED
└─ yes
   ├─ any legal Chapter plan → CHAPTER_DAY
   └─ no Chapter
      ├─ standalone Aha passes → HIGHLIGHT_DAY exactly 1
      └─ no Aha
         ├─ exact no-Memory proof → EMPTY_DAY
         └─ otherwise → DAY_STATE_NOT_PROPOSED
~~~

Operational failure 不能伪装 EMPTY；recall-only limitation 可随合法非空 plan 继续，state/retention-critical exclusion 必须 HOLD/BLOCK。最终状态仍需 S12 校验。

**案例：** 某天没有 Chapter，但记录到一次清晰、独立且有价值的求婚瞬间，可以形成 HIGHLIGHT_DAY。

### 17.4 冻结输出接口

~~~text
S09ResultBundle
  SelectedMemorySet
  DayStateProposal
  EditorialRevisionDelta
  relation / fifth / capacity decisions
  selection and uncertainty audit
  search audit
  S10HandoffEnvelope[]
  downstream readiness
  policy/version compatibility
~~~

Chapter 与 Aha 成员确定后，各自在本类型数组中按 capture chronology 排序，时间完全相同再用 stable identity tie-break。这个 canonical order 不影响 membership；S10 仍决定 Chapter 内媒体顺序。

Readiness 区分 `READY_FOR_S10 / EMPTY_READY_FOR_S12 / NO_CHANGE_REUSE / HOLD_PREVIOUS_REVISION / BLOCKED_NO_PUBLISHABLE_REVISION`。S09 不声明 `PUBLISH_READY`。

### 17.5 S09 明确不做

- 不重新理解 Raw/Evidence；
- 不改写 Observation/Moment/Candidate；
- 不选择具体 Frame；
- 不决定 PHOTO/LIVE_2S/VIDEO_5S；
- 不写 Narrative；
- 不为凑数量恢复 unresolved Candidate；
- 不新增媒体上传、Raw 回取、补帧、VLM/strong-model 或 embedding 调用；
- 不允许 S10/S12 静默替换 membership。

### 17.6 FROZEN / OPEN 边界

已冻结：SelectionRecord 六组字段、typed relation、五种 constraint、八层 objective、deterministic search、两阶段 lineage、三种 Day State、Preview/Final capacity、第五章、canonical output 与 readiness。

继续 OPEN：Production reason enum/schema、真实阈值、solver/state-budget benchmark、same-day policy pin/migration 实现、S10 失败后是否允许有界 re-selection，以及真实标签、效果和成本。

---

## 18. S10｜EvidenceAnchor & Media Editorial

**当前状态：FROZEN BY V1.20/V1.21；以下段落保留早期讨论展开，冲突处以后置 Canonical 为准**

已经存在的方向：

~~~text
Memory Selected
→ Representative Evidence
→ EvidenceAnchor
→ Media Format
→ Render request
~~~

Chapter 允许：

~~~text
PHOTO
LIVE_2S
VIDEO_5S
~~~

Aha 允许：

~~~text
PHOTO
LIVE_2S
~~~

Aha 不使用 VIDEO_5S。

### 18.1 目标

在 Memory 已经被 S09 选中后，决定：

- 这个 Memory 需要展示哪些内容位置；
- 每个位置由哪一个 EvidenceAnchor 表示；
- 使用 PHOTO、LIVE_2S 还是 VIDEO_5S；
- 需要向 S13 请求哪些最小 HQ source window。

### 18.2 输入接口

~~~text
SelectedMemorySet
+ source Candidate content units
+ KEEP Evidence/Frame refs
+ source offsets
+ quality / stability / motion signals
+ validation findings
+ allowed HQ source handles
~~~

CONTEXT_ONLY 可以帮助理解顺序，但不能变成精选媒体；DROP 不能被恢复。

### 18.3 建议逻辑结构

#### Step 1｜Memory content beats

先确认已选 Memory 中需要被展示的 3–5 个非重复内容位置。内容位置来自 CandidateContentUnit，不重新搜索全天。

**案例：** 古镇 Chapter 可以有“牌坊进入、石板路行走、奶茶短暂停留、寺庙、河边结束”五个 beat；如果奶茶没有独立内容价值，可以只保留四个。

#### Step 2｜Representative Evidence shortlist

对每个 beat，只在其允许的 KEEP Evidence 中建立候选 Anchor shortlist。

选择信号：

- semantic representativeness；
- event centrality；
- visual quality；
- subject clarity；
- motion value；
- temporal completeness；
- stability；
- evidence confidence。

Motion Amount 不等于 Motion Value。

**案例：** 一段剧烈晃动的视频 motion 很大，但不能因此胜过稳定、清楚显示吹蜡烛前后的素材。

#### Step 3｜EvidenceAnchor

Anchor 是一个可追溯的精确内容位置，至少应包含：

~~~text
memory_ref
content_unit_ref
raw_asset_ref
evidence_window_ref
frame_ref or source time interval
semantic role
supporting facts
quality / limitation
~~~

先选 Anchor，再决定媒体格式。

**案例：** “吹灭蜡烛”的 Anchor 是火焰变化发生的具体时间位置；它不是“LIVE_2S”这个格式本身。

#### Step 4｜Media format decision

建议判断：

~~~text
single decisive instant + stable
→ PHOTO

short micro-action adds meaning + stable temporal source
→ LIVE_2S

Chapter action needs a short arc + source supports it
→ VIDEO_5S
~~~

格式不能反向改变 Memory selection。

**案例：** 古镇牌坊适合 PHOTO；吹蜡烛的动作若有稳定短时序可用 LIVE_2S；家庭表演的一个完整动作可能使用 Chapter VIDEO_5S。

#### Step 5｜Within-memory media set

Chapter 最终目标为 3–5 个精选媒体项：

- 覆盖不同内容 beat；
- 控制近重复；
- 保持时间或故事推进；
- 每项都能追溯到 Candidate 内容；
- 不让一条长 Manual 的相似位置占满整章。

Aha 是聚焦瞬间，具体是否允许一个主媒体加 supporting item 尚未冻结。

**案例：** 古镇 Chapter 不应选择三张几乎相同的石板路；应覆盖进入、建筑、活动或结尾等不同内容位置。

#### Step 6｜Media fallback

建议允许在同一 Memory、同一内容 beat 内：

~~~text
preferred dynamic format unavailable
→ fallback to PHOTO
or next valid Anchor in same beat
~~~

不得用其他 Memory 的漂亮素材替代。

**案例：** 吹蜡烛 LIVE_2S 过度晃动时，可以退回清晰 PHOTO；不能改用与吹蜡烛无关的合照，却仍称为吹蜡烛 Aha。

#### Step 7｜HQ Source Request Manifest

S10 只生成最小请求计划，S13 执行：

~~~text
selected anchor refs
requested source interval
target media format
fallback anchor
expected render constraints
~~~

不请求全天 Auto Raw。

**案例：** 古镇最终选择四个 Anchor，就只请求对应的四个源位置；不把当天 150 个 Auto 视频全部上传到 HQ storage。

### 18.4 建议输出接口

~~~text
MemoryMediaPlan[]
EvidenceAnchor[]
MediaDecision[]
HQSourceRequestManifest
MediaSelectionAudit
media_readiness =
  MEDIA_READY
  MEDIA_DEGRADED
  MEDIA_UNRESOLVED
~~~

### 18.5 S10 明确不做

- 不增加或替换 Chapter/Aha；
- 不改变 Candidate facts；
- 不恢复 CONTEXT_ONLY/DROP 为内容；
- 不写 title/story；
- 不执行最终 HQ render；
- 不因画面漂亮而创造 Memory。

### 18.6 仍需逐项讨论

- Chapter 3–5 项的正式选择与排序算法；
- Aha 最终媒体项数量；
- Hero 是否固定 PHOTO，以及何时可用 LIVE_2S；
- 一个 RawAsset 或长 Manual 能否贡献多个最终 Anchor；
- visual quality、motion value、stability 的阈值；
- EvidenceAnchor schema；
- PHOTO/LIVE_2S/VIDEO_5S 的可用性与 fallback；
- S10 MEDIA_UNRESOLVED 后由 S12 删除，还是允许一次有界 S09 re-selection；
- HQ source 的实际存储、请求、超时和失败合同；
- Preview 是否立即渲染 HQ，还是 Final 才执行；
- 成本、网络、电量与真实体验 Benchmark。

---

## 19. S11｜ChapterFacts / Claim Ledger / Narrative

**当前状态：FROZEN BY V1.22；以下为早期方向摘要**

### 目标

把已选 Memory 和已选媒体支持的事实，表达为用户可读内容。

### 处理顺序

~~~text
Selected Memory
+ Validation findings
+ EvidenceAnchor
→ ChapterFacts / AhaFacts
→ Claim Ledger
→ title / time label / story / tags
~~~

每条 Claim 必须记录来源、Evidence、Observation、支持等级、validation 和是否允许用户可见。

Writer 不允许：

- 重新选择 Memory；
- 添加人物关系；
- 添加情绪、意图或因果；
- 把稀疏采样写成持续活动；
- 覆盖用户自己写下的文字；
- 使用不在 Claim Ledger 中的事实。

### 输出

~~~text
ChapterFacts / AhaFacts
ClaimLedger
GroundedNarrative
CanonicalTags + DisplayLabels
~~~

### 案例

可以写“在古镇的石板路和传统建筑之间步行，途中短暂停留在奶茶店”；如果没有定位和主观证据，不能写“你最喜欢的古镇里度过了悠闲上午”。

---

## 20. S12｜Final Validation & Day State

**当前状态：FROZEN BY V1.23；以下为早期方向摘要**

### 目标

在发布前检查整个 Daily Memory 是否满足事实、数量、集合、媒体和文字合同。

### 必须检查

- 当前 Revision/snapshot 一致；
- Day State 与 Chapter/Aha 数量；
- Chapter raw/content coverage；
- Chapter 间 RawAsset 冲突；
- Chapter/Aha semantic redundancy；
- S08 unresolved/operational Candidate 未被偷渡；
- EvidenceAnchor 属于原 Candidate；
- Chapter 3–5 媒体项；
- 媒体格式合法；
- 每条 Claim 有 Evidence；
- 文案没有过度推断；
- provider/model/prompt/parameter/cost provenance 完整；
- HQ/render readiness。

### 输出状态

~~~text
CHAPTER_DAY
HIGHLIGHT_DAY
EMPTY_DAY
~~~

V1.23 已收紧失败权限：S12 只读验证 exact immutable proposal，不现场删除 Memory、媒体或 Claim。失败返回 S09/S10/S11/S13 exact owner 生成新 artifact，或 HOLD/BLOCK，并记录 audit。

不能用更流畅的文案掩盖证据不足。

### 案例

如果古镇 Chapter 原本选了五项媒体，其中一项来自 CONTEXT_ONLY 奶茶 Window，S12 返回 S10 replan；不能由 validator 删除后直接发布。S10 产生新的 exact projection 后，S11/S12 重新验证。

---

## 21. S13｜Selected HQ Rendering & Export

**当前状态：FROZEN PRODUCTION-SHAPED CONTRACT BY V1.24；真实云端实现仍 OPEN**

### 目标

只为最终选中的 Anchor 请求 HQ source window，生成最终媒体并导出。

### 流程

~~~text
Validated MemoryMediaPlan
→ request selected HQ source interval
→ render PHOTO / LIVE_2S / VIDEO_5S
→ verify media-to-memory consistency
→ publish export
~~~

### User Diary Export

- Day State；
- Chapter title/story/time；
- 每 Chapter 3–5 个媒体项；
- Aha 与其媒体；
- hero/media refs；
- canonical tags / display labels；
- 用户文字引用，但算法不得覆盖用户文字。

用户界面不展示：

- 内部模型分数；
- 被淘汰 Candidate；
- Token 和成本；
- 内部失败诊断。

### Internal Audit Run

- immutable input snapshot；
- RawAsset → Evidence → Observation → Moment → Candidate → Memory provenance；
- role、boundary、duplicate、alternative、validation；
- selected/rejected reasons；
- Anchor 与 HQ request；
- model/prompt/parameter versions；
- token、cost、latency、retry、failure；
- evaluator / human label refs。

### 明确不做

- 不默认上传全天 Raw；
- 不在 render 阶段改变 Memory 事实；
- render 失败不等于内容不存在。

### 案例

家庭生日选择了合照 PHOTO 和吹蜡烛 LIVE_2S，S13 只请求这两个源位置。若 LIVE_2S render 失败，应回到已声明 fallback 或标记媒体失败，不能删除“生日发生过”的事实。

---

## 22. 贯穿案例的完整结果流

### 22.1 古镇部分

~~~text
S01
→ A/B/C RawAssets 按拍摄时间排序

S02
→ Auto/Manual 变成 Evidence Windows

S03
→ A/C 有户外步行与古建筑相关便宜信号
→ B 有明显室内变化

S04
→ A: 石板路、牌坊、传统建筑
→ B: 室内、柜台、饮品
→ C: 寺庙、河边、继续步行

S05
→ A | B | C 三个连续 Moment

S06
→ A/C KEEP
→ B 可能 KEEP 或 CONTEXT_ONLY，依据自身内容贡献

S07
→ RESUMED_EPISODE: A+C
→ possible LOCAL_EPISODE_GROUP: A+B+C
→ local alternative retained when dominance unknown

S08
→ confirm A/C relation
→ optionally resolve whether B adds material content

S09 V1.19
→ choose one nonredundant ancient-town Memory

S10 proposed
→ select 3–5 distinct beats and anchors
→ PHOTO / LIVE_2S / VIDEO_5S decisions

S11
→ grounded title/story

S12
→ verify facts, media and redundancy

S13
→ request only selected HQ source positions and export
~~~

### 22.2 生日部分

~~~text
D preparation
E candle peak
F applause / group photo

S05
→ one or a few contiguous birthday Moments

S06
→ reliable content KEEP

S07
→ birthday Chapter Candidate
→ candle Aha Candidate

S08
→ confirm local peak only when needed

S09 V1.19
→ birthday selected as an independent strong Episode
→ candle Aha kept only if not redundant

S10 proposed
→ Chapter: preparation / candle / applause / photo
→ Aha: focused PHOTO or LIVE_2S

S11–S13
→ grounded narrative, validation, HQ render and export
~~~

---

## 23. 成本与数据边界

### 23.1 最低充分能力

~~~text
T0 deterministic
→ T1 local lightweight
→ T2 embedding / classifier
→ T3 cheap multimodal
→ T4 selective strong reasoning
~~~

模型能力按任务需要升级，不默认选择最强模型。

### 23.2 Incremental cost

- 每次 Sync 只处理新增 Raw/Evidence；
- S04 expensive perception exact-cache；
- S05–S07 使用缓存结构化数据；
- S08 只有 bounded provisional frontier；
- S09 只比较 Candidate；
- S10 只处理 selected Memory 的 Evidence；
- S13 只请求 selected HQ source。

### 23.3 月度约束

- cohort average：≤US$1.50 / user / month；
- engineering target：约 US$0.90；
- internal warning：约 US$1.20；
- heavy user 可以高于平均，但整体 cohort 需受控；
- Validation、ASR、Strong escalation 和 Retry waste 分账。

### 23.4 当前数据边界

- Phone 持有完整 Raw source cache；具体保留期 OPEN；
- Cloud 默认接收 Evidence，不默认接收全部 Auto Raw；
- 第三方模型默认接收有界 Evidence；
- Auto UPLOAD_1 不补帧；
- S08 不扩大输入；
- S13 只请求 selected HQ source window；
- own backend、cloud storage、source cache 与 model provider 的最终存储/保留合同仍需单独工程与治理设计。

**案例：** 系统选择了四个古镇媒体项和四个生日媒体项，HQ 路径只处理这八个 Anchor 对应源位置，而不是当天所有 186 个 RawAsset。

---

## 24. 逻辑职责与工程职责不能混在一起

| 层 | 当前逻辑职责 | 当前边界 |
|---|---|---|
| Phone / App-side algorithm | Raw intake、Evidence extraction、便宜信号、1-or-3 route、无感待上传队列 | 本文不修改 App；后台网络、电量和 retry 工程另行设计 |
| Own backend / Cloud workflow | Observation、Moment、Role、Candidate、Validation、Selection、Media Plan、Narrative、Validation | 推荐 Modular Monolith + Async Worker；Production 尚未实现 |
| Model Gateway | model registry、structured output、cache、pricing、fallback、exposure、trace | 业务逻辑不能散落 provider SDK |
| Media source/render path | selected HQ source request、PHOTO/LIVE_2S/VIDEO_5S render | 只处理 selected Anchor；具体存储链路 OPEN |
| Product UI | Sync、Preview、Diary、Manual 独立窗口 | Manual 内容不因 Memory 抑制而消失 |
| Evaluation | Gold labels、error attribution、cost/latency、user feedback | 不用一个 Overall Score 掩盖不同错误 |

---

## 25. 当前阶段状态总表

| Stage | 当前状态 | 已有结论 | 下一类工作 |
|---|---|---|---|
| S00 | FROZEN V1.1 | rolling Preview、Revision、稳定累加、Final | Production orchestration |
| S01 | FROZEN V1.2 | RawAsset truth、idempotency、quarantine | Schema/ledger implementation |
| S02 | FROZEN V1.3/1.4/1.6/1.8 | Auto/Manual Evidence、1-or-3、no-refetch | Real extraction/upload benchmark |
| S03 | FROZEN V1.5/1.9 | intrinsic vs edge signals | Schema/threshold benchmark |
| S04 | FROZEN V1.7/1.9/1.10 | Window-local facts、grounding、status/cache | Production perception runner |
| S05 | FROZEN V1.11–1.15 | contiguous Moments、dual ledgers、DEFER | Engine/schema/Gold data |
| S06 | FROZEN V1.16 | KEEP/CONTEXT/DROP | Engine/schema/calibration |
| S07 | FROZEN V1.17 | Chapter/Aha candidates、alternative/audit | Engine/schema/calibration |
| S08 | FROZEN V1.18 | targeted validation、budget/cache/failure | Engine/provider benchmark |
| S09 | FROZEN V1.19 | pool、relation/constraint、set objective/search、lineage、Day State、capacity/fifth、output/readiness | Schema/solver/benchmark/calibration |
| S10 | FROZEN V1.20/V1.21 | Beat/Anchor/Media/Hero/HQ/activation | Engine/real media benchmark |
| S11 | FROZEN V1.22 | Facts/Claims/Narrative/Tags/Entities/verification | Real provider/data/locale calibration |
| S12 | FROZEN V1.23 | S12A/S12B read-only validation + atomic authorization | Database/CAS/App UX implementation |
| S13 | FROZEN CONTRACT V1.24 | selected HQ/materialization/activation/export | Real renderer/storage/cloud infrastructure |

---

## 26. 团队现在可以依赖什么

团队现在可以依赖：

1. S00–S13 的阶段职责、边界、两阶段发布顺序和主要 Baseline；
2. RawAsset → Evidence → Observation → Moment → Candidate 的不可逆责任分离；
3. no-refetch、no-default-Raw、exact cache 和 bounded validation；
4. Rich day 3–4 Chapter、第五章严格例外、Aha 非配额；
5. S09 使用 typed relation、八层 ordered objective、state-conditioned deterministic search 与 hard retention，不是简单 Top-K；
6. S10 必须 Anchor-first，不能先找最漂亮媒体再创造 Memory；
7. Writer 必须基于 Claim Ledger；
8. 最终必须同时输出用户 Diary 与内部 Audit；
9. S12 只读、不静默修理，S13 只执行 selected/predeclared routes；
10. V1.25 本地 reference 可验证全链路合同，但不等于真实云端 Production。

团队仍不能当成已经完成的事项：

1. S09 的真实 material/strong/near-equivalent 阈值与 objective discretization；
2. S09 Production schema/reason enum、solver/state budget 性能与 same-day policy migration 实现；
3. S00–S10 完整 Production engines；
4. 真实 VLM/Writer provider 与成本/时延结论；
5. HQ source 的真实存储、传输、renderer 与 codec 数值；
6. App 无感上传网络/电量/destination 实现；
7. 数据库、队列、CAS、recovery 与 SLO；
8. 真实数据阈值、用户评分、海外 locale、隐私/治理结论。

---

## 27. 后续工作顺序

S00–S13 全流程已由 V1.25 收口。下一阶段不重新设计 Pipeline，而按以下顺序验证并工程化：

~~~text
real labeled-day fixtures and error taxonomy
→ S00–S10 stage adapters/engines
→ real Writer + HQ materialization benchmark
→ persistent ledgers / queue / CAS / recovery
→ App background-upload integration contract
→ Chinese D2e user test + overseas locale release gates
→ privacy/security/governance
→ staged production rollout
~~~

---

## 28. 权威文档索引

本文件是团队解释层。发生冲突时，以对应 Canonical Checkpoint 为准。

| Stage | 权威或当前主文档 |
|---|---|
| 全局入口 | [Read First](00_READ_FIRST.md) |
| 全链路 | [Daily Memory Algorithm Flow](DAILY_MEMORY_ALGORITHM_FLOW_V0_1.md) |
| 继承基础 | [Canonical Processing Rules V1.0](CANONICAL_PROCESSING_RULES_V1_0.md) |
| S00 | [V1.1 Rolling Daily Memory](CANONICAL_CHECKPOINT_V1_1_ROLLING_DAILY_MEMORY.md) |
| S01 | [V1.2 RawAsset Intake](CANONICAL_CHECKPOINT_V1_2_RAW_ASSET_INTAKE.md) |
| S02 Auto | [V1.3 Auto Three-Frame Evidence](CANONICAL_CHECKPOINT_V1_3_AUTO_THREE_FRAME_EVIDENCE.md) |
| S02 Manual | [V1.4 Manual Evidence](CANONICAL_CHECKPOINT_V1_4_MANUAL_EVIDENCE.md) |
| S03 baseline | [V1.5 Signal Pack](CANONICAL_CHECKPOINT_V1_5_SIGNAL_PACK_BASELINE.md) |
| S02/S03 routing | [V1.6 Evidence Upload Routing](CANONICAL_CHECKPOINT_V1_6_EVIDENCE_UPLOAD_ROUTING.md) |
| S04 coverage | [V1.7 Observation Lite Coverage](CANONICAL_CHECKPOINT_V1_7_OBSERVATION_LITE_COVERAGE.md) |
| Upload/no-refetch | [V1.8 Background Upload and No Refetch](CANONICAL_CHECKPOINT_V1_8_BACKGROUND_UPLOAD_NO_REFETCH.md) |
| S03/S04 split | [V1.9 Signal Split and Window-local Observation](CANONICAL_CHECKPOINT_V1_9_SIGNAL_SPLIT_WINDOW_LOCAL_OBSERVATION.md) |
| S04 output | [V1.10 Observation Lite Output](CANONICAL_CHECKPOINT_V1_10_OBSERVATION_LITE_OUTPUT_CONTRACT.md) |
| S05 partition | [V1.11 Contiguous Moment Segmentation](CANONICAL_CHECKPOINT_V1_11_CONTIGUOUS_MOMENT_SEGMENTATION.md) |
| S05 ledgers | [V1.12 Dual Evidence Boundary Ledger](CANONICAL_CHECKPOINT_V1_12_DUAL_EVIDENCE_BOUNDARY_LEDGER.md) |
| S05 signature | [V1.13 Multi-Prototype Context Signature](CANONICAL_CHECKPOINT_V1_13_MULTI_PROTOTYPE_CONTEXT_SIGNATURE.md) |
| S05 transition | [V1.14 Unresolved Transition Routing](CANONICAL_CHECKPOINT_V1_14_UNRESOLVED_TRANSITION_ROUTING.md) |
| S05 lookahead | [V1.15 Bounded DEFER Lookahead](CANONICAL_CHECKPOINT_V1_15_BOUNDED_DEFER_LOOKAHEAD.md) |
| S06 | [V1.16 Observation Role Assignment](CANONICAL_CHECKPOINT_V1_16_OBSERVATION_ROLE_ASSIGNMENT.md) |
| S07 | [V1.17 Chapter/Aha Candidate Generation](CANONICAL_CHECKPOINT_V1_17_CHAPTER_AHA_CANDIDATE_GENERATION.md) |
| S08 | [V1.18 Targeted Enrichment and Validation](CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md) |
| S09 | [V1.19 Editorial Set Selection](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md) |
| Chapter/Aha independence | [V1.20](CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md) |
| S10 | [V1.21 EvidenceAnchor & Media Editorial](CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md) |
| S11 | [V1.22 Grounded Narrative & Memory Index](CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md) |
| S12 | [V1.23 Final Validation & Atomic Day State](CANONICAL_CHECKPOINT_V1_23_FINAL_VALIDATION_AND_ATOMIC_DAY_STATE.md) |
| S13 | [V1.24 Selected HQ Materialization & Export](CANONICAL_CHECKPOINT_V1_24_SELECTED_HQ_MATERIALIZATION_AND_EXPORT.md) |
| Full-flow V1.0 | [V1.25 Production-shaped Pipeline](CANONICAL_CHECKPOINT_V1_25_PRODUCTION_SHAPED_PIPELINE_V1_0.md) |
