# S09 Editorial Set Selection — Cross-check & Profile Simulation V0.1

**状态：** REVIEW COMPLETE / SUPPORTS FROZEN V1.19
**检查日期：** 2026-08-27
**被测合同：** `S09_EDITORIAL_SET_SELECTION_CONSOLIDATED_WORKING_V0_1.md`
**冻结上游：** S00 V1.1、S01 V1.2、S02 V1.3/V1.4/V1.6/V1.8、S03/S04 V1.5/V1.7/V1.9/V1.10、S05 V1.11–V1.15、S06 V1.16、S07 V1.17、S08 V1.18
**下游边界：** S10–S12 direction only；不得在本检查中偷冻 S10 媒体算法
**冻结结果：** [Canonical Checkpoint V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md)

> 本文用于寻找 S09 A1–D3 的结构冲突、优先级漏洞、跨 Revision 问题和不可执行定义。`FOUND` 不代表已修复；所有修订必须回写主工作合同并再次验证后，S09 才可能冻结。

## 1. 检查方法

1. 逐项追踪 S00→S09 与 S09→S10/S12 的对象、Revision、Evidence 与权限边界；
2. 检查 hard eligibility、relation、search objective、retention、Day State 与 downstream readiness 的执行顺序；
3. 使用高概率用户画像和两分钟语义时间轴构造 adversarial cases；
4. 检查数量合同、无感/不补帧、Manual 独立窗口、precision-first 与成本不变量；
5. 将问题分成：可直接按既有冻结原则修复、需要用户决策、真实数据校准。

## 2. 上下游边界矩阵

| boundary | S09 当前行为 | 初检 |
|---|---|---|
| S00 Revision/snapshot | 每个 SelectionRecord 与 bundle 绑定 current immutable Revision；late data 新建 Revision | PASS |
| S01 Sync/capture | memory scope 使用 capture interval；Sync batch 不作为生活边界 | PASS |
| S02 upload/no-refetch | S09 不上传媒体、不补 Auto 帧、不重读 Raw | PASS |
| S03/S04 facts | 只读结构化 signals/grounded facts，不产生新 visible fact | PASS |
| S05 Moment | Episode/continuity/boundary 作为关系证据，不回写 partition | PASS |
| S06 role | KEEP 才能进入内容；CONTEXT_ONLY 仅传给 S10 context；DROP 不恢复 | PASS |
| S07 Candidate | 只选择 ELIGIBLE current Candidate；不改 content identity/disposition | PASS WITH F1 |
| S08 validation | wrapper 单一身份；unresolved/operational/stale 不入池 | PASS AFTER F4 FIX |
| V1.1 rolling | stable accumulation、controlled merge、3–4 target、fifth exception | PASS AFTER F2/F3/F6 FIX |
| S10 media | S09 只给 selected scope/KEEP allowlist，不选 Anchor/format | PASS WITH F8 |
| S11 narrative | S09 不写 Claim/Narrative | PASS |
| S12 validation | S09 不宣告 PUBLISH_READY；membership change 必须重入 S09 | PASS / future S12 contract must align |

## 3. 初检发现

| id | finding | risk | disposition |
|---|---|---|---|
| F1 | A1 的 Candidate+wrapper 合法 normalization 与两个异常同 identity record 的 contract conflict 尚未显式区分 | 实现可能把重复物化静默去重 | FIXABLE FROM EXISTING B3 |
| F2 | C3 主要描述 prior Memory 与 current winning item 的比对，但 retention constraint 必须在 C2 winner 产生前已可用 | 先选后匹配会选出违反 retention 的 plan | FIXABLE ARCHITECTURE |
| F3 | D1 多 standalone Aha 写“选择最强一个”，未先处理 prior published valid HIGHLIGHT Aha 的 retention | 新 Aha 可能按 ranking 错误替换旧 Aha | FIXABLE FROM FROZEN V1.1 |
| F4 | D1/D3 将 operational limitation 描述得过于二元；S08 policy frontier/budget 本来允许 recall-limited output，但 EMPTY_DAY 又不能由真正 operational blind spot伪装 | 可能一有未验证候选就全日阻断，或反向把失败当空日 | NEED IMPACT CLASSIFICATION |
| F5 | C2 仍以单一 winning plan 为主要术语，D1 后来才增加 state-conditioned incumbents | 实现可能先选后裁剪以满足 Day State | FIXABLE CONTRACT CLARIFICATION |
| F6 | Preview 已发布四章后，合法 split correction 可能产生五个 child/current Chapters；D2 又关闭 Preview fifth gate | 保留错误合并、遗漏 child 或违反 Preview cap 三者冲突 | RESOLVED BY CONFIRMED HOLD POLICY |
| F7 | Selected Chapter/Aha 的 canonical output order 尚未定义 | 相同集合可能跨运行或端出现顺序抖动 | RESOLVED BY CONFIRMED CHRONOLOGICAL CONTRACT |
| F8 | D3 将 S10 whitelist 完整作为 readiness 条件，但 `allowed_hq_source_handles` 可能要到 S10/S13 才能确认 | 可能在媒体选择前过早阻断合法 Memory | FIXABLE BOUNDARY CLARIFICATION |
| F9 | `PROVEN_DUPLICATE`、`SAME_MEMORY_REDUNDANCY`、`SUPPRESSED_DUPLICATE` 等 reason 属不同层但尚无 enum mapping | 监控/实现可能混淆事实、关系与 lifecycle reason | PRODUCTION SCHEMA WORK |
| F10 | material/strong/near-equivalent、objective discretization、state budget 与 fifth importance 无数值 | 目前可冻结架构，不能声称参数已可生产部署 | REAL-DATA CALIBRATION |
| F12 | 同一 DailyMemoryRun 中途切换 pipeline/selection policy 时，policy-only disappearance 不属于允许的 eviction reason | 可能阻断 Revision 或造成跨版本抖动 | S09 SAFE HOLD/BLOCK APPLIED；S00 VERSION ORCHESTRATION OPEN |

## 4. 已确认不构成问题的高风险边界

1. Chapter–Chapter shared RawAsset 为 hard conflict；Chapter–Aha Evidence overlap 需按 Memory relation 判断；
2. Pair conflict 不传递，不把 connected component 自动压成 at-most-one；
3. Manual 相似内容可以从 Memory 中抑制，但不从独立 Manual 窗口或事实账本删除；
4. `UNRESOLVED_POTENTIAL_CONFLICT` 是 current-Revision guard，不永久改写 Candidate disposition；
5. 第五章是 set-level marginal gate，不是单体 rank #5；
6. `EMPTY_DAY` 是成功处理后的内容结论，不是网络、预算或合同失败状态；
7. S10/S12 不得静默用另一 Memory 修补当前选择。

## 5. 画像模拟矩阵（已完成细粒度与 adversarial 验证）

| profile | high-probability material pattern | expected S09 stress |
|---|---|---|
| P01 routine office commuter | 长时间相似桌面/走廊/通勤，少量 Manual 咖啡 | EMPTY vs weak-content quota |
| P02 family birthday | setup/cake/song/candle/gift，Manual 密集且近重复 | Chapter+Aha overlap、same peak duplicate |
| P03 sparse decisive moment | 大量普通素材 + 一段短促清晰求婚 | HIGHLIGHT standalone gate |
| P04 high-intensity traveler | 五个独立完整强 Episode | fifth Chapter gate |
| P05 rolling tourist Preview | 古镇 resumed、后续 workshop/birthday，多次 Sync | retention、Preview reserve、lineage |
| P06 same-looking knowledge worker | 同一会议室两场不同会议 | embedding false merge |
| P07 multiple standalone peaks | 无 Chapter、两个独立 Aha，跨 Preview | HIGHLIGHT exactly-one + retention |
| P08 operationally limited day | 合法 direct Candidate + S08 provider failure | recall limitation vs whole-day block |
| P09 split correction at cap | prior 4 Chapters，其中一个后证实应 split | D2/C3 conflict |
| P10 post-Final late data | 已有 5 valid Chapters 后到第六 Episode | hard cap + retention audit |
| P11 Manual-heavy creator | 少数长 Manual，多内容位置 | wrapper identity、S10 allowlist |
| P12 low-capture/noisy wearer | FAILED/UNKNOWN、重复和模糊 Auto | empty proof vs operational failure |

## 6. 细粒度模拟完成度

新增 `S09_FULL_SELECTION_FINE_GRAINED_SIMULATION_V0_1.md`：

- P01 普通通勤/办公：32 points；
- P03 稀疏求婚 HIGHLIGHT：32 points；
- P04 五 Episode 高强度旅行：32 points；
- P07 多 standalone Aha / retention：32 points；
- P08 direct Chapter + provider failure：32 points。

与 B3 的古镇、生日、chain conflict、同会议室四例合计 288 个两分钟语义时间点。自动行数检查为每个新增案例恰好 32，新增合计 160。

## 7. Adversarial Revision 检查

### R01｜HIGHLIGHT exactly-one + prior retention

~~~text
R1: M-A = admission-result Aha, published HIGHLIGHT_DAY
R2: M-A still valid + new gift Aha M-B
~~~

当前 D1 若只按“更强”选择可能错误替换 M-A。正确约束应先保留 M-A，再将 M-B 记为 single-Aha-limit retained-prior exclusion。**F3 confirmed.**

### R02｜Aha 升级 Chapter + 新独立 Aha

~~~text
R1: M-A = proposal Aha
R2: same M-A obtains preparation/action/outcome → Chapter
    new M-B = independent celebration peak
~~~

合法结果为 `CHAPTER_DAY: M-A Chapter + M-B Aha`。M-A 保留 stable ID并记录 `AHA_TO_CHAPTER`；HIGHLIGHT exactly-one 不再适用于 CHAPTER_DAY。**PASS.**

### R03｜Preview 四章中的一章被 split

~~~text
R1 Preview: M1(combined A+C), M2, M3, M4 = 4 Chapters
R2 Preview: new boundary evidence proves M1 must split to M1a + M1b
            current valid Chapter count becomes 5
~~~

三条现有规则同时生效：错误 segmentation 必须允许修正；Preview fifth gate closed；prior content 不应无解释消失。用户已确认采用：

1. 纯 `SEGMENTATION_CORRECTED` overflow 在 Preview 保持 R1；
2. 不发布 partial corrected four，不隐藏或拒绝任一 child，不为 Preview 开第五章；
3. current corrected plan、split lineage 与 Evidence 留在内部 attempt/audit；
4. Final 对 corrected P4/P5 执行完整 selection 与 fifth gate；
5. 若涉及 `FACT_INVALIDATED / EVIDENCE_INVALIDATED`，不得用 HOLD 继续保留已知错误内容。

输出 `HOLD_PREVIOUS_REVISION / PREVIEW_SPLIT_CORRECTION_DEFERRED_TO_FINAL`。**PASS AFTER F6 CONFIRMED POLICY.**

### R04｜Final 五章后 Late Data 第六 Episode

五个 prior Chapters 均仍有效时，新 Episode 不得形成第六章，也不能按普通 ranking 驱逐 prior；保留 audit `DAY_CHAPTER_CAP_REACHED_VALID_PRIOR_RETAINED`。**PASS under current product cap.**

### R05｜merge/split 无 primary core

当 N→1 merge 或 1→N split 没有可信 primary core 时，C3 使用新 ID并保留 parents/children lineage，不按时间或 ID 猜继承者。若 group relation 本身清楚则 READY；若 group relation 不清楚则 LINEAGE_UNRESOLVED。**PASS, but F2 requires group ledger before search.**

### R06｜唯一潜在 Memory operationally unresolved

若唯一潜在 Chapter/Aha 因 provider/budget operational outcome 未验证，当前不能建立 empty proof。若已有 prior，HOLD；无 prior 则 BLOCKED。**PASS with D1 intent.**

### R07｜合法非空 direct set + unrelated operational Candidate

已有 direct ELIGIBLE Chapter 合法，另一个 provisional Aha provider failed。整天直接阻断会违背 S08 bounded frontier 的目的；忽略 limitation 又会虚称完整召回。需要把 exclusion impact 分为 recall-only 与 state/retention-critical。**F4 confirmed.**

### R08｜S10 HQ handle 尚未物化

S10 的职责包括 Anchor/format/HQ request planning。S09 必须给出 allowlist 与 handle availability，而不是要求所有 HQ handle 已存在才 READY；否则阶段顺序倒置。**F8 confirmed.**

### R09｜高价值晚间 Memory 不应改变输出时间顺序

~~~text
09:00 M1 = ancient-town Chapter
14:00 M2 = pottery-workshop Chapter
20:00 M3 = birthday Chapter, highest editorial value
~~~

三者的成员资格先由 C1/C2 确定；随后 Chapter 按最早 selected KEEP `capture_start` 输出为 M1→M2→M3。M3 的更高价值不能把它移到数组首位。若两个 entry 时间完全相同，使用 stable ID / allocation key tie-break；不得依赖输入数组或数据库返回顺序。**PASS AFTER F7 CONFIRMED CONTRACT.**

## 8. 复杂度复核

S07 gate-before 理论分布可达约 60 Chapter hypothesis + 62 Aha hypothesis：

~~~text
Chapter subsets up to 5 = 5,985,198
Aha subsets up to 3    = 39,774
naive Cartesian plans  = 238,055,265,252
pair comparisons       = 7,381
~~~

结论：

- pair graph 成本很小；
- 不能实现 naive complete Cartesian enumeration；
- C2 的 state-conditioned constrained search、hard pruning、sound upper bound 与 deterministic expanded-state guard 是必要结构；
- 真实 selectable pool 通常远低于 gate-before 上限，但必须在真实分布压测；
- 若 state budget hit，readiness 继续按 C2/D3 的 exactness proof，不允许假装 optimal。

新增 finding：

| id | finding | disposition |
|---|---|---|
| F11 | 理论 naive plan 数约 238B；solver/branch-and-bound 实现与 benchmark 尚未完成 | ENGINEERING + REAL-DATA BENCHMARK, not a reason to add model calls or upstream Top-K |

## 9. 当前修复队列

### 可依据已冻结原则直接修复

1. F1：区分 wrapper normalization 与异常 duplicate identity；
2. F2：建立 pre-search lineage compatibility/group ledger，将 retention 变成 C2 constraint；
3. F3：HIGHLIGHT prior Aha retention 优先；
4. F5：C2 明确同时维护 state-conditioned incumbents；
5. F8：HQ handle availability 由 S10 处理，S09 只保证 allowlist/provenance 完整。

### 需要形成明确 impact contract

6. F4：operational/policy exclusion 对 nonempty selection、EMPTY_DAY 与 prior retention 的不同影响。

### 已由用户确认并回写

7. F6：Preview split correction overflow 使用 `HOLD_PREVIOUS_REVISION`，等待 Final 完整决定 P4/P5；
8. F7：成员确定后，Chapter/Aha 使用独立的 deterministic chronological canonical order。

### 继续保持 OPEN

9. F9 reason enum mapping；
10. F10 真实阈值与 objective discretization；
11. F11 solver/state budget benchmark。
12. F12 same-day policy pin/migration strategy（S00 integration；S09 safe fallback 已明确）。

## 10. 下一步

1. F1–F8 全部回写主工作合同；
2. 重新执行文档不变量与场景检查；
3. 完成 freeze-readiness report；
4. 用户已最终确认；V1.19 canonical checkpoint 已生成。

## 11. Cross-check fixes applied

| finding | applied correction | recheck |
|---|---|---|
| F1 | A1 明确只有 Candidate+合法 wrapper 可 normalization；异常同 identity record 为 contract invalid | PASS |
| F2 | C3 改为 Phase-A all-record pair/group compatibility → C2 retention constraints → Phase-B final lineage | PASS |
| F3 | D1 HIGHLIGHT exactly-one 先保留 valid prior Aha，再比较无 prior/已失效场景 | PASS |
| F4 | D1/D3 增加 `ExcludedUncertaintyImpactAssessment`；recall-only 可带 limitation 继续，state/retention-critical 阻断 | PASS WITH REAL TELEMETRY NEEDED |
| F5 | C2 同一 traversal 维护 Chapter/Highlight/Empty state-conditioned incumbents | PASS |
| F6 | Preview 纯 split-correction overflow 保持上一发布版；不做 partial correction，不开 Preview fifth，Final 再决策 | PASS |
| F7 | 成员确定后按 capture chronology + stable identity tie-break 形成 canonical output order | PASS |
| F8 | S09 只要求 Evidence/source whitelist 与 handle status 完整，不要求 HQ 已 materialize | PASS |
| F12 | 主合同增加 same-day policy compatibility assessment；无显式 migration proof 时 HOLD/BLOCK，禁止 policy-only eviction | PASS；PIN/MIGRATION IMPLEMENTATION OPEN |

## 12. 修复后不变量抽查

1. wrapper normalization 不再掩盖 identity contract error；
2. retention constraint 在 plan search 前生效，不再依靠 winner 后修补；
3. HIGHLIGHT R1→R2 多 Aha 案例保留 prior stable Memory；
4. direct Chapter + provider-failed Aha 可输出非空 plan并保留 recall limitation；
5. provider-failed 唯一 Candidate 不能产生 EMPTY proof；
6. state-conditioned search 不先选后裁；
7. S10 可以在 HQ 尚未 materialize 时接收合法 scope并决定 fallback/request；
8. Preview split overflow 不产生 partial correction、假 merge 或隐藏 child；
9. canonical order 不反向改变 membership、价值比较、retention 或数量；
10. 所有 hard constraints、Preview/Final count 与 fifth gate 保持不变。

## 13. 画像结果汇总

| profile | expected selected result | Day State/readiness | result |
|---|---|---|---|
| P01 routine office | 0 Chapter / 0 Aha；Manual coffee 仅留独立窗口 | EMPTY / exact proof required | PASS |
| P02 family birthday | 1 Birthday Chapter + distinct surprise/candle/gift Aha subset；same peak deduped | CHAPTER_DAY | PASS |
| P03 sparse proposal | 0 Chapter + 1 proposal Aha | HIGHLIGHT_DAY | PASS |
| P04 high-intensity traveler | Preview <=4/2；Final five only after D2 weakest-marginal gate | CHAPTER_DAY | PASS |
| P05 rolling tourist | preserve/expand ancient-town stable ID；new independent Episodes add within reserve | CHAPTER_DAY/NO_CHANGE possible | PASS |
| P06 same-looking meetings | two Chapters allowed when boundary/progression distinct | CHAPTER_DAY | PASS |
| P07 multiple standalone peaks | first published valid Aha retained；new distinct Aha excluded by exactly-one | HIGHLIGHT_DAY | PASS AFTER F3 FIX |
| P08 operationally limited | direct Chapter continues with recall limitation；unique failed candidate cannot produce EMPTY | CHAPTER_DAY or HOLD/BLOCK | PASS AFTER F4 FIX |
| P09 split at Preview cap | keep prior Preview；retain corrected five-child attempt for Final P4/P5 decision | HOLD_PREVIOUS_REVISION | PASS AFTER F6 FIX |
| P10 post-Final sixth | retain five valid prior Chapters；sixth audit only | CHAPTER_DAY | PASS / product cap tradeoff |
| P11 Manual-heavy creator | validated long-Manual wrapper single identity；S10 gets only allowed KEEP positions | CHAPTER_DAY | PASS |
| P12 noisy wearer | evidence-inconclusive exclusions can support precision-first EMPTY；operational failure cannot | EMPTY or HOLD/BLOCK | PASS AFTER F4 FIX |

当前 12 个 profile 全部通过；F7 canonical ordering 的 deterministic rerun case 也通过。未发现需要回退修改 S00–S08 冻结合同的问题。

## 14. Freeze-readiness report

### 14.1 结论

~~~text
S09 architecture = FROZEN_V1_19
canonical checkpoint = V1.19
production readiness = NOT CLAIMED
remaining S09 product/architecture decision = NONE
final action = COMPLETED
~~~

这表示 S09 的职责、对象、决策顺序、安全边界与下游合同已经闭环，可以形成 canonical checkpoint；不表示 solver、schema、参数、服务或真实用户效果已经达到 Production。

### 14.2 通过依据

1. A1、A2、B1、B2、B3、C1、C2、C3、D1、D2、D3 共 11 个设计小节全部 `CONFIRMED`；
2. F1–F8 已回写并复核通过；F12 的 S09 safe HOLD/BLOCK 行为已明确；
3. 12 个高概率/高风险用户画像全部得到合同一致结果；
4. 4 个 B3 案例 + 5 个 full-selection 案例均为 32 个两分钟点，合计 288 个时间点；
5. R01–R09 覆盖 retention、type transition、split overflow、Final sixth、group lineage、operational blind spot、recall-only、HQ handle 与 canonical ordering；
6. 理论容量重新计算一致：Chapter subset 5,985,198；Aha subset 39,774；朴素组合 238,055,265,252；pair 7,381；
7. 未发现需要修改 S00–S08 已冻结合同的反向依赖；
8. S09 不新增媒体上传、RawAsset 重读、补帧、VLM/strong-model 或 embedding 成本。

### 14.3 建议进入 V1.19 的冻结内容

- selectable pool、Candidate/wrapper normalization 与 `SelectionRecord`；
- typed multi-edge relation graph、双向 `CandidatePairLedger` 与五种 executable constraint；
- 八层 set-level objective、state-conditioned deterministic constrained search 与 search status；
- pre-search retention constraints、两阶段 lineage、stable ID/revision instance 与 merge/split group ledger；
- `CHAPTER_DAY / HIGHLIGHT_DAY / EMPTY_DAY` 判定顺序、standalone Aha gate 与 exact empty proof；
- Preview 4/2、Final normal 4/3、严格第五章 gate、Preview split-correction hold 与 Final hard cap 5；
- uncertainty impact、downstream readiness、S10 Evidence whitelist 与禁止下游静默换 Memory；
- Chapter/Aha 各自的 deterministic chronological canonical output order；
- same-day policy version 不兼容时的安全 HOLD/BLOCK 行为。

### 14.4 继续 OPEN，但不是架构冻结 blocker

| item | remains open | frozen safety boundary |
|---|---|---|
| F9 | Production reason enum/schema mapping | 不得混淆事实、关系、选择与 lifecycle reason |
| F10 | material/strong/near-equivalent、objective discretization、fifth importance 的真实阈值 | 八层比较顺序与不可补偿边界不变 |
| F11 | solver/branch-and-bound 实现、state budget 与真实分布 benchmark | 不做 naive enumeration；受限搜索不得伪装 exact |
| F12 | S00 same-day version pin 与显式 migration 实现 | 无 compatibility proof 时 HOLD/BLOCK，不允许 policy-only eviction |
| downstream | S10 失败后是否允许有界重选、S10–S12 具体合同 | S10/S12 不得自行替换 S09 membership |
| implementation | Production service、persistent schema、telemetry、labeled-data calibration | 本次只冻结算法架构，不声称 Production ready |

### 14.5 明确不纳入本次冻结

- S10 EvidenceAnchor/精选媒体/格式算法；
- S11 title、story、tag、叙事与情绪表达；
- S12 Claim/发布验证；
- App 无感后台上传、云存储/API 路由与账户产品流程；
- Firmware/SDK 与共享状态文件；
- 16 秒、73 秒等非标准 Manual Window；
- 隐私、伦理与治理专题。

### 14.6 冻结动作边界

用户已最终确认，`CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md` 已生成，并更新项目入口/全链路索引。该动作只冻结 S09，不同时进入或冻结 S10。
