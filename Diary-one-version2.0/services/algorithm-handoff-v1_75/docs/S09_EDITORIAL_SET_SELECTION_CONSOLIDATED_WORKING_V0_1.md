# S09 Editorial Set Selection — Consolidated Working V0.1

**状态：** REVIEW COMPLETE / BASIS FOR FROZEN V1.19
**确认日期：** 2026-08-26
**上游合同：** `CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md`
**下游边界：** S10 EvidenceAnchor & Media Editorial
**当前权威规则：** [Canonical Checkpoint V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md)

> 本文保留 S09 的逐项讨论与确认依据。S09 已由 V1.19 冻结；若本文与 V1.19 冲突，以 V1.19 为准。

## 1. S09 在全链路中的位置

~~~text
S07 Candidate Generation
→ S08 Targeted Validation
→ S09 Editorial Set Selection
→ S10 EvidenceAnchor & Media Editorial
~~~

S09 只决定当天应保留哪一组 Chapter/Aha Memory。它不重新理解 Raw/Evidence，不改写 Observation/Moment/Candidate，不选择具体 Frame 或媒体格式，也不撰写 Narrative。

## 2. S09-A1｜Selectable Pool 与 Hard Eligibility

**状态：CONFIRMED**

### 2.1 术语

- `Selectable Pool`：允许参加 S09 集合选择的候选池；入池不等于最终入选。
- `Hard Eligibility`：不可被分数、权重或数量目标补救的入池硬条件。
- `ValidatedCandidate wrapper`：引用原 S07 Candidate 的 S08 验证凭证；不复制或改写原 Candidate 的 content identity。
- `PoolExclusionAudit`：保存未入池对象及原因的审计账本；不是候选池。

### 2.2 两条合法入池路径

~~~text
S07 Candidate
├─ 已直接满足全部 S09 前置条件
│  └─ DIRECT_ELIGIBLE → Selectable Pool
├─ 存在必要 S08 ValidationTask，且全部 PASS
│  └─ VALIDATED_ELIGIBLE → Selectable Pool
└─ rejected / unresolved / operational / stale
   └─ PoolExclusionAudit only
~~~

候选池逻辑上继承：

~~~text
S07 direct ELIGIBLE Candidates
+ S08 VALIDATED_FOR_S09 wrappers
→ normalize by current Candidate content identity
→ one selectable entry per Candidate
~~~

### 2.3 单一内容身份

1. 同一个 S07 Candidate 与其 `ValidatedCandidate` wrapper 不能形成两个池成员。
2. wrapper 只提升同一 Candidate 的下游资格证明，不产生新的 Memory 内容。
3. 当前 Revision 内每个 Candidate content identity 最多生成一个 selectable entry。
4. prior Revision lineage 只作为稳定性信息，不允许把旧 Revision Candidate 直接混入当前池。

这里允许的 normalization 仅指“一个合法 S07 Candidate + 指向它的合法 S08 wrapper”合并成一个选择入口。若两个物理 S07 Candidate record 异常声明同一 current content identity、一个 wrapper 指向不一致 Candidate，或同一 identity 出现跨 Revision 混用，则为 `IDENTITY_CONFLICT / SELECTION_CONTRACT_INVALID`：隔离受影响对象并进入 B3/D3 impact assessment，不能选择第一条、静默去重或伪装成正常 wrapper normalization。

### 2.4 Hard Eligibility

池成员必须同时满足：

1. 属于当前 user/day、DailyMemoryRun、Revision 与输入 snapshot；
2. Candidate、Seed、Episode/Moment/Observation/Evidence refs 合法且可追溯；
3. S07 disposition 允许下游选择；
4. 如存在必要 S08 task，所有必要 task 均为 PASS，并存在合法 current-Revision wrapper；
5. 不属于 `REJECTED_BY_EVIDENCE`、`UNRESOLVED_EVIDENCE`、`UNVALIDATED_OPERATIONAL` 或 `STALE_FOR_CURRENT_REVISION`；
6. Candidate type、content identity 与上游事实未被 S09 修改；
7. 所有关联 `AlternativeResolution` 已附带给 S09，供后续关系约束使用。

### 2.5 禁止补位

数量目标不是最低配额。任何 excluded、unresolved、operational 或 stale Candidate 都不能因为当天 Chapter/Aha 数量不足而恢复入池。

**案例：** 当天已有两个可信 Aha；第三个吹蜡烛候选因人物遮挡而 `UNRESOLVED_EVIDENCE`。最终可以只有两个 Aha，第三个只保留审计记录。

### 2.6 wrapper 去重案例

“生日吹蜡烛 Aha”在 S07 中需要确认火焰是否真的熄灭。S08 PASS 后，S09 只生成一个 `VALIDATED_ELIGIBLE` entry；原 Candidate 与 wrapper 不得分别计数。

### 2.7 A1 输出

~~~text
S09SelectablePool
  direct_eligible_candidate_refs[]
  validated_candidate_refs[]
  normalized_selectable_entries[]
  alternative_resolution_refs[]

PoolExclusionAudit[]
  source_ref
  exclusion_class
  upstream_outcome_ref
  current_revision_applicability
  reason_code
~~~

## 3. S09-A2｜SelectionRecord

**状态：CONFIRMED**

### 3.1 定义

`SelectionRecord` 是当前 Revision 中一个 selectable Candidate 的规范化“候选选择卡”。它只组织 S09 比较所需的上游事实、引用和版本，不创建新的 Memory 事实，不修改 Candidate，也不等于最终选择结果。

### 3.2 最小字段结构

~~~text
SelectionRecord
  identity_and_version
  memory_scope
  trust_basis
  memory_value_basis
  relation_inputs
  revision_lineage_and_provenance
~~~

#### A. identity_and_version

- `selection_record_id`；
- `candidate_instance_ref`；
- `candidate_type = CHAPTER | AHA`；
- Chapter 的 `SINGLE / ADJACENT_GROUP / RESUMED_EPISODE / LOCAL_EPISODE_GROUP` form；
- `revision_id`、`snapshot_id`；
- upstream Candidate fingerprint；
- `eligibility_source = DIRECT_ELIGIBLE | VALIDATED_ELIGIBLE`。

`selection_record_id` 必须由 Candidate identity、当前 Revision 与 SelectionRecord schema/policy version 确定性生成。

#### B. memory_scope

- capture interval；
- source/owner/participant Moment refs；
- CandidateContentUnit refs；
- KEEP RawAsset refs；
- EpisodeGroupSignature ref；
- Chapter coverage path 与 Aha origin Moment / peak Window 等 type-specific refs。

#### C. trust_basis

- upstream gate decision refs；
- S08 outcome、validated assertion 与 wrapper refs；
- limitation、contradiction 与 inference-risk refs；
- Evidence provenance。

不得重新制造一个 Candidate 总置信分，也不得把不同事实的 support grade 压成一个误导性 overall confidence。

#### D. memory_value_basis

- Memory Value Gate 的 reason 与 supporting refs；
- Episode coherence basis；
- Manual intent refs；
- distinct KEEP RawAsset count；
- non-redundant CandidateContentUnit count；
- Normal / Long-Manual path 与已验证 exception refs。

Manual intent 与 truth/reliability 必须分离保存。主动拍摄可以支持个人相关性，不能提高一个事实本身的真实性。

#### E. relation_inputs

- alternative/duplicate group refs；
- RawAsset、ContentUnit、时间区间、Episode 与 grounded semantic signature refs；
- S09-B 建图所需的稳定 overlap keys。

这里只保存关系计算输入，不提前写入“它一定重复”之类的关系结论。

#### F. revision_lineage_and_provenance

- prior Revision Candidate / user-visible Memory refs；
- upstream `continues / expands / merges / splits / supersedes` lineage；
- pipeline、schema、taxonomy、parameter 与 policy versions；
- deterministic build trace。

### 3.3 不属于 Candidate 固有属性的量

以下量取决于它与其他 Candidate 或当前已选集合的关系，不能预先固化成 SelectionRecord 的“自身分数”：

- `distinctness`；
- `day_coverage_gain`；
- `redundancy_penalty`；
- `revision_stability_gain/cost`；
- `fifth_chapter_incremental_value`。

它们应在 S09-B/C 基于当前 relation graph 与 selected set 计算，并保留计算 trace。

### 3.4 明确禁止

SelectionRecord 不包含：

- 一个决定一切的总分；
- 新的 Observation、Candidate Fact 或 Narrative；
- 具体 Frame/hero 选择；
- `PHOTO / LIVE_2S / VIDEO_5S` 决定；
- 模型自由文本推理作为硬事实。

### 3.5 案例

“古镇 A+C 恢复主线”和“古镇 A+B+C 完整 outing”各生成一条 SelectionRecord。Record 保存 Episode、时间、RawAsset、内容范围和 alternative refs；它不会因一个候选出现石板路、另一个出现古建筑就提前决定它们不同。是否互斥、被包含或具有真实新增内容，由 S09-B 的关系证据决定。

## 4. S09-B1｜Candidate Relation Taxonomy

**状态：CONFIRMED**

### 4.1 图结构

- 每条 `SelectionRecord` 是一个 node；
- Candidate 之间由有类型、有证据、有选择影响的 edge 连接；
- 同一 Candidate pair 可以同时存在多条 edge，不能压缩成单一“相似度关系”；
- edge 只影响当前集合选择，不回写或删除上游 Candidate。

### 4.2 关系类型与选择影响

| relation type | 含义 | selection effect |
|---|---|---|
| `IDENTITY_CONFLICT` | 同一 Candidate identity 被重复物化 | contract invalid；不能继续选择 |
| `CHAPTER_RAW_ASSET_CONFLICT` | 两个 Chapter 共享 underlying RawAsset | `MUST_NOT_COSELECT` |
| `EXCLUSIVE_ALTERNATIVE` | 同一局部问题的替代解释 | `MUST_NOT_COSELECT` |
| `SAME_MEMORY_REDUNDANCY` | 表达同一段 Memory | `MUST_NOT_COSELECT` |
| `NESTED_DOMINANCE` | A 包含 B，且 B 无独立新增意义 | `MUST_NOT_COSELECT`，并记录 directed dominator |
| `PARTIAL_OVERLAP` | 共享部分内容，但双方可能有独立贡献 | 可以共存，产生 set-level redundancy cost |
| `EMBEDDED_DISTINCT_AHA` | Aha 位于 Chapter 内，但表达独立局部事件 | 允许共享 Evidence 并共存 |
| `DISTINCT_EPISODE` | 时间/Episode 独立，即使生活语义相似 | 允许共存 |
| `UNRESOLVED_POTENTIAL_CONFLICT` | 有实质冲突迹象但证据无法安全定类 | 不声称 duplicate；当前 set 最多选一个 |

### 4.3 选择影响优先级

~~~text
contract invalid
→ hard MUST_NOT_COSELECT
→ unresolved at-most-one guard
→ partial-overlap set cost
→ coexist allowed
~~~

“允许共存”不等于必须同时选择；最终是否同时占用当天名额由 S09-C 的集合目标决定。

### 4.4 Chapter/Aha 特殊边界

1. Chapter–Chapter 当前 Baseline 只要共享 underlying RawAsset 就具有 hard conflict；
2. Chapter–Aha 可以共享 Evidence，但必须区分 `EMBEDDED_DISTINCT_AHA` 与 `SAME_MEMORY_REDUNDANCY`；
3. Aha–Aha 指向同一具体 peak 时为 hard redundancy；
4. semantic/style/object 相似本身不建立 hard edge。

### 4.5 案例

- “古镇 A+C 恢复主线”与“古镇 A+B+C 完整 outing”可以同时具有 RawAsset conflict、alternative 与 nested/partial-overlap edge，但不能同时选择；
- “生日 Chapter”与其中独立的“吹灭蜡烛 Aha”可形成 `EMBEDDED_DISTINCT_AHA` 并共存；
- 上午与晚上两次遛狗若时间、RawAsset 与 Episode 均独立，则不能仅因 embedding、狗、街道和步行相似判重。

## 5. S09-B2｜Relation Evidence 与 Pair Ledger

**状态：CONFIRMED**

### 5.1 结构化两两比较

S09 对当前 `SelectionRecord[]` 做 deterministic/lightweight pair comparison：

~~~text
SelectionRecord[]
→ candidate pairs
→ existing structured evidence only
→ CandidatePairLedger[]
→ typed relation edges
~~~

S09 不为建图新增媒体上传、VLM/strong-model 调用、Raw 请求、Auto 补帧或 Observation 重写。

即使使用 S07 gate 前理论最大 122 个 hypothesis 作为容量参考，也只有 7,381 个 pair。这里比较 ID、集合交集、时间、Episode 与已 grounded 的结构化语义；真实 telemetry 出现瓶颈前，不引入复杂 ANN/blocking 系统。

### 5.2 CandidatePairLedger

每个被比较的 Candidate pair 至少保存：

~~~text
CandidatePairLedger
  pair_id
  candidate_a_ref
  candidate_b_ref
  same_memory_evidence[]
  distinct_memory_evidence[]
  hard_constraints[]
  contradictions[]
  relation_decisions[]
  selection_effects[]
  reason_codes[]
  source_refs[]
  policy_and_algorithm_versions
~~~

账本必须双向保存“像同一 Memory 的证据”和“是不同 Memory 的证据”。没有 overlap evidence 不等于已经证明 distinct；没有 distinct evidence 也不等于已经证明重复。

### 5.3 证据优先级

1. S07 alternative/duplicate/dominance refs 与 S08 `AlternativeResolution`；
2. Candidate identity、RawAsset、CandidateContentUnit、peak 等 exact overlap；
3. Moment、Episode、capture interval、continuity/boundary 与 interruption structure；
4. grounded activity/progression/outcome、anonymous entity continuity、Context Motif 与 EpisodeGroupSignature；
5. embedding、scene、object、style similarity。

第 5 级只能 nominate 关系，不能单独建立 hard conflict、same-memory 或 distinct-episode 结论。

### 5.4 最低判定边界

- `SAME_MEMORY_REDUNDANCY` 至少同时需要结构关系与 grounded Memory basis 支持；
- `NESTED_DOMINANCE` 还必须证明被包含 Candidate 没有 material independent contribution；
- `DISTINCT_EPISODE` 需要明确的时间/Episode boundary 或不同 event progression；
- exact Chapter–Chapter RawAsset overlap 直接建立 hard conflict；
- Chapter–Aha Evidence overlap 不自动建立 conflict；
- 同地点、同风格、同活动、高 embedding 或 capture proximity 均不能单独定案；
- overlap 与 distinct evidence 同时成立时，优先定为 `PARTIAL_OVERLAP`；仍无法安全定类时使用 `UNRESOLVED_POTENTIAL_CONFLICT`。

### 5.5 典型案例

- 古镇石板路与古建筑画面可以通过同一 Episode、连续步行、Context Motif 与人物/时间连续性建立同一或部分重叠关系，而不是仅按物体标签拆开；
- 上午与晚上遛狗虽然 embedding 相似，但独立时间、Episode、RawAsset 与生活边界支持 `DISTINCT_EPISODE`；
- 两条独立 RawAsset 若都记录同一分钟、同一蛋糕与同一次吹蜡烛结果，可以建立 `SAME_MEMORY_REDUNDANCY`。

## 6. S09-B3｜Executable Selection Constraints

**状态：CONFIRMED**

**验证依据：** `S09_B3_FINE_GRAINED_TIMELINE_SIMULATION_V0_1.md`，包含 4 个独立案例、每例 32 个两分钟 Auto 时间点，共 128 个语义时间点。

### 6.1 五种约束结果

| constraint | 含义 |
|---|---|
| `CONTRACT_BLOCKED` | 身份、Revision 或引用合同错误；隔离受影响 record |
| `FORBID_COSELECT` | 两个或显式 group 中最多选择一个 |
| `CONSERVATIVE_AT_MOST_ONE` | 关系未解决；当前 Revision 质量优先，最多选择一个 |
| `ALLOW_WITH_REDUNDANCY_COST` | 可以共存，但计入 set-level redundancy |
| `ALLOW_COSELECT` | 当前关系本身不禁止共选 |

所有 at-most-one 都不是 exactly-one。约束允许两个 Candidate 都不被选择。

### 6.2 Hard constraints

1. 同一 underlying RawAsset 的 Chapter selected count ≤ 1；
2. 显式 `EXCLUSIVE_ALTERNATIVE` group selected count ≤ 1；
3. `SAME_MEMORY_REDUNDANCY` pair selected count ≤ 1；
4. `NESTED_DOMINANCE` pair selected count ≤ 1，并保存 directed dominator；
5. `UNRESOLVED_POTENTIAL_CONFLICT` pair 当前 Revision selected count ≤ 1，reason 为 `CONSERVATIVE_RELATION_GUARD`；
6. `PARTIAL_OVERLAP` 不建立 hard ban，而进入 S09-C marginal value/redundancy 计算；
7. `EMBEDDED_DISTINCT_AHA` 与 `DISTINCT_EPISODE` 不建立禁止共选约束。

relation/dominance direction 不能直接宣布 winner。赢家仍由 S09-C 在满足全部约束的合法集合中决定。

### 6.3 Pair conflict 不传递

~~~text
A conflicts B
B conflicts C
A does not conflict C

→ {A, C} remains legal
~~~

不能把普通 connected component 自动压成“整组最多一个”。只有具有显式 group identity 与 cardinality contract 的 Alternative group，或共享资源形成的明确 group constraint，才能产生 group-level limit。

### 6.4 Contract error

重复 Candidate identity、跨 Revision 引用或非法 provenance：

- 不静默去重；
- 隔离受影响 SelectionRecord；
- 记录 `SELECTION_CONTRACT_INVALID`；
- 未受影响的合法 pool 可以继续；
- 不能让错误 record 进入选中集合。

### 6.5 模拟结论

- 古镇 resumed 与 broader outing 不会同时选择，但 embedded 街头表演 Aha 可以共存；
- Birthday Chapter 与多个不同 local peak Aha 可以共存，同一吹蜡烛 peak 不会重复计数；
- 通勤 A—咖啡 B—演示 C 的 chain conflict 不会错误压制合法的 A+C；
- 同一会议室中有完整 boundary 的两场会议不会仅因 embedding/style 相似判重；
- boundary Evidence 缺失时使用 Revision-local conservative guard，不永久改写上游 disposition。

## 7. S09-C1｜Set-level Editorial Objective

**状态：CONFIRMED**

### 7.1 为什么不能直接取单体 Top-K

S09 选择的是当天完整的 Chapter + Aha 集合，而不是彼此独立的高分 Candidate。两个 Candidate 即使单独都很强，放在同一集合中仍可能表达同一 Memory、造成重复，或让较弱内容仅因数量目标而占位。

因此，Baseline 不把全部因素压缩成一个 overall score，也不执行“分别给 Chapter/Aha 排名后直接取 Top-K”。它采用质量优先的分层比较：只有前一层相同或近似相同时，才比较下一层。

### 7.2 分层选择目标

#### 第一层：Legality 与 Trust

只比较满足 S09-A/B 所有合同、hard eligibility 与 co-selection constraints 的合法集合。存在非法 record、hard conflict 或 unresolved at-most-one 违规的集合直接淘汰，任何分数与数量目标都不能补救。

**案例：** 两个古镇 Chapter 共用同一个 Manual Video RawAsset。即使两者单独质量都高，也不能同时进入最终集合。

#### 第二层：每个 selected item 都有 Material Marginal Memory Contribution

`Material Marginal Memory Contribution`（实质性边际记忆贡献）指：从当前集合删除该 item 后，用户会真实失去一个值得记住的独立经历、进展、结果、转折或高光，而不只是少一种相似说法。

没有实质增量的 Candidate 不得为了接近数量目标而入选。

**案例：** “古镇漫步”“古镇石板路与建筑”“继续逛古镇”若都表达同一 outing 且后两者没有独立进展，就不能为了凑足三个 Chapter 全部保留；“古镇漫步”与“朋友生日聚会”则具有明确的独立贡献。

#### 第三层：Meaningful Episode Coverage

优先覆盖更多值得形成 Memory 的独立强 Episode。这里的 coverage 是“有意义经历的覆盖”，不是钟表时间覆盖、素材数量覆盖或 RawAsset 使用率。

**案例：** 当天包括古镇游览、普通通勤、重要客户演示和生日聚会，应优先覆盖古镇、演示与生日；不能因为通勤持续更久、Auto 素材更多，就自动给通勤一个 Chapter。

#### 第四层：Trusted Independent Memory Value

当 Episode coverage 相近时，优先选择证据更可靠、活动过程更完整、变化或结果更清楚、推断风险更低，并且具有更强独立 Memory value 的集合。

**案例：** 一组连续办公室桌面画面，与“进入会议室—完成演示—客户反馈—会后交流”的完整过程相比，即使素材数量接近，也应优先选择后者。

#### 第五层：Set-level Redundancy 与 Inference Risk

在 Chapter–Chapter、Chapter–Aha 和 Aha–Aha 三种关系中共同控制重复。Aha 可以嵌入 Chapter，但必须表达独立的局部转折、成果、惊喜或情绪高点，不能只是换标题复述 Chapter。

**案例：** “朋友生日聚会”Chapter 与“吹蜡烛时大家突然唱起生日歌”Aha 可以共存；“古镇漫步”Chapter 与“今天在古镇散步”Aha 没有独立高光，后者不应入选。

#### 第六层：Quality-qualified Count Preference

丰富日的期望区间保持为 3–4 Chapters、2–3 Ahas，第五个 Chapter 仅在有额外独立且重要的 Memory 时考虑。这些数量是质量合格后的偏好区间，不是必须补足的最低配额。

**案例：** 如果当天只有“重要会议”和“生日晚餐”两个强 Episode，可以只输出两个 Chapter；不能用普通通勤和买水补成四个。

#### 第七层：Revision Stability

当两个合法集合的质量近似时，优先保留已经展示给用户的 Memory identity，并通过同一 lineage 做 `continues / expands / merges / splits / supersedes` 修订。稳定性只用于近似质量下的选择，不能保护已被新证据推翻的错误结果。

这里的 soft stability preference 不覆盖 V1.1 已冻结的 published-Memory retention guard：一个事实、Evidence 与 Episode 划分仍有效的已发布 Memory，不能仅因后来 ranking 下降而被逐出。Retention guard 先决定哪些已发布 Memory 必须有合法当前继任者；第七层只在多个合法继任方案之间偏好更稳定的方案。

**案例：** 中午已展示“古镇游览”，下午素材只是延伸同一 outing，应优先扩充原 Memory；如果新证据证明中午错误合并了两次独立出行，则允许 split 或 supersede。

#### 第八层：Parsimony 与 Determinism

如果两套集合仍近似等价，优先选择更精简的一套；随后使用固定的、可审计的 tie-break，例如稳定时间键与 identity key，确保相同输入、Revision 和 policy version 重复运行时得到相同结果。

### 7.3 明确顺序

~~~text
1. legal and trustworthy
2. every selected item materially contributes
3. cover meaningful distinct Episodes
4. maximize trusted independent Memory value
5. minimize redundancy and inference risk
6. prefer the quality-qualified target count band
7. preserve Revision stability when quality is near-equivalent
8. prefer the smaller set, then deterministic tie-break
~~~

数量偏好不能越过前五层，Revision stability 不能越过事实与质量，deterministic tie-break 不能伪装成 Memory value。

### 7.4 参数边界

“material”“strong”“near-equivalent”以及各层内部的数值阈值暂不冻结。它们将在真实用户素材、人工标签、用户反馈与离线评估中校准。当前确认的是目标语义、比较顺序和不可越过的边界，而不是一组假精确权重。

## 8. S09-C2｜Deterministic Constrained Set Search

**状态：CONFIRMED**

### 8.1 Baseline 选择

S09 使用确定性的约束集合搜索：先构造 Chapter skeleton，再为仍可能获胜的 skeleton 接入 Aha，最后按 S09-C1 对完整 Chapter + Aha plan 做联合比较。

“先 Chapter、后 Aha”只是搜索遍历顺序，不是先独立确定 Chapter winner。Aha compatibility、Chapter–Aha redundancy 与完整集合价值仍可改变最终选择。

搜索输入除 SelectionRecord 与 B3 relation/constraint graph 外，还必须包含 C3 Phase-A 产生的 prior-published lineage compatibility/group ledgers 与 protected-prior successor constraints。Retention 不能在 winner 产生后补做。

同一次 traversal 同时维护 state-conditioned incumbents：

~~~text
best_chapter_day_plan
best_highlight_day_plan
empty_day_feasibility_proof
~~~

“winning plan”只指 D1 按冻结状态顺序选定的对应 incumbent。不得先产生一个不分 Day State 的 winner，再删除成员以强行满足状态形状。

S09 不使用：

- candidate overall score Top-K；
- 分别选完 Chapter 与 Aha 后直接拼接；
- 随机搜索；
- 新媒体上传、RawAsset 重读、VLM/strong-model 调用或新 embedding。

### 8.2 搜索起点与形状边界

搜索从空 plan 开始，不预设最低数量：

~~~text
selected Chapters = []
selected Ahas = []

Chapter count <= 5
Aha count <= 3
~~~

空集合和低数量集合必须在搜索空间中存在，防止数量目标变成补位配额。第五 Chapter 只有在 S09-D 的 exceptional gate 开放时才具有最终资格。

**案例：** 当天只有会议与生日两个强 Episode，`2 Chapters + 1 Aha` 是合法 plan；普通通勤不能为了达到 3–4 Chapters 被强行加入。

### 8.3 Chapter skeleton construction

按 policy-versioned deterministic traversal order 逐个处理 Chapter SelectionRecord。每一步创建 `include` 与 `exclude` 分支；include 后立即执行：

1. contract 与 current-Revision 检查；
2. B3 hard/group/unresolved constraints；
3. C3 protected-prior successor/group constraints；
4. Chapter count cap；
5. 已可证明的 material-contribution invalidation；
6. 已可证明无法超过对应 state incumbent 的 higher-tier upper bound。

只有具有充分证明的情况才能停止分支。如果没有 sound upper bound，必须保留该分支，不能以“看起来分数低”为由剪掉。

**案例：** `C1=古镇 A+C 恢复主线` 与 `C2=更广 outing alternative` 互斥，`C3=客户演示`、`C4=生日聚会` 独立。搜索可以保留 `{C1,C3,C4}` 与 `{C2,C3,C4}`，但不得生成 `{C1,C2,C3,C4}`。

### 8.4 Aha attachment

对每个仍可能获胜的 Chapter skeleton，以同样的 include/exclude 方式接入最多三个 Aha，并同时执行：

- Aha–Aha same-peak / alternative constraints；
- Chapter–Aha `SAME_MEMORY_REDUNDANCY`；
- Chapter–Aha `EMBEDDED_DISTINCT_AHA`；
- `PARTIAL_OVERLAP` redundancy accumulation；
- current-Revision unresolved guard；
- Aha count cap 与 material contribution。

所有 surviving complete plans 再共同进入 C1 比较。不得先固定一个 Chapter winner，再只为它寻找 Aha。

**案例：** 生日 Chapter 可与独立的“突然合唱”及“拆开意外礼物”两个 Aha 共存；另一条记录同一次吹蜡烛的 Aha 与“突然合唱/吹蜡烛”同 peak 时最多保留一个。

### 8.5 EditorialPlanState 与删除测试

搜索中的 plan state 至少保存：

~~~text
EditorialPlanState
  selected_chapter_refs[]
  selected_aha_refs[]
  meaningful_episode_refs[]
  independent_peak_refs[]
  marginal_contribution_trace[]
  active_constraint_refs[]
  redundancy_and_risk_trace[]
  revision_stability_trace
  objective_vector
  traversal_and_search_trace
~~~

这些字段只引用和聚合已经 grounded/validated 的上游 Episode、progression、outcome 与 peak，不创造新的事实。

完整 plan 必须执行 member-removal test：依次移除每个 selected item，判断是否真实失去一个独立经历、进展、结果、转折或高光。没有 material marginal contribution 的成员使该 plan 不合格。

**案例：** “古镇漫步 Chapter”“古镇建筑与石板路 Chapter”“街头表演 Aha”中，若第二个 Chapter 只是第一项的相似表述，删除它没有 Memory 损失；删除街头表演则会失去独立局部事件，因此前者不能占位而后者可保留。

### 8.6 完整 plan 的比较

`objective_vector` 不压缩为一个 overall score，而按 C1 的八层顺序比较。前一层未达到 policy-defined equivalence 时，不允许用后一层补偿。

**案例：** “古镇 + 客户演示 + 生日，附街头表演与吹蜡烛 Aha”优于“两个重复古镇 Chapter + 普通通勤 + 生日，附复述古镇的 Aha”，即使后者数量更多。

### 8.7 Safe pruning

Baseline 只允许以下安全剪枝：

1. hard/contract constraint 已违反；
2. type count 已超过 policy cap；
3. 基于固定贡献 refs，已证明 selected member 无独立贡献，且加入更多成员不可能恢复；
4. 使用 sound optimistic upper bound，已证明该分支即使获得剩余候选的最理想贡献，也无法在更高优先层超过当前最佳完整 plan。

任何 heuristic ordering 只能帮助更早找到 incumbent，不是候选资格或最终价值判断。完整搜索时遍历顺序不得改变结果；预算受限时，遍历 policy/version/order 必须完整留痕。

### 8.8 成本、预算与确定性

S09 只处理当前最多约 122 个 gate-before theoretical hypothesis 的较小结构化 graph；真实 selectable pool 通常还会经过 disposition 与 validation 过滤。主要成本是本地/云端 CPU 与内存，不产生新的媒体理解或模型调用成本。实际 latency 必须用真实分布压测，不在设计阶段假定具体毫秒数。

为防止异常组合爆炸：

- primary guard 使用确定性的 `expanded_state_count`，不是机器波动较大的 wall-clock；
- 相同 input snapshot、Revision、policy version 与 traversal order 必须产生相同 best-found plan；
- wall-clock 只可作为 operational emergency stop，不能静默改变可发布选择；
- 达到 state budget 时，不删 Candidate、不放松 hard constraints，也不声称全局最优。

### 8.9 Search status

~~~text
EXACT_WITHIN_POLICY
  search completed; winning plan is optimal under current policy/objective discretization

BEST_LEGAL_WITH_SEARCH_LIMIT
  deterministic state budget reached; return best legal plan found with optimality_proven=false

SEARCH_OPERATIONAL_FAILURE
  non-policy operational abort; do not disguise as an exact editorial result
~~~

预算受限结果是否可以进入 Preview/Final 发布，由后续 S09-D/S12 合同决定；C2 只保证其合法性、局限说明与可追溯性。

### 8.10 输出审计

S09 至少输出 winning plan、其他 surviving plan 的比较摘要、每个 selected item 的 marginal contribution、所有生效约束、search status、expanded state count、policy/version/order 与 deterministic trace。

未选择 Candidate 的原因必须与 search status 一致：当 `optimality_proven=false` 时，不得把“未进入 best-found plan”误写成“已经证明全局更差”。

## 9. S09-C3｜Cross-Revision Continuity & Stable Memory Identity

**状态：CONFIRMED**

### 9.1 两种稳定性必须分离

1. `published-memory retention guard`：仍然有效、已成功发布的 Memory 不能仅因后续 ranking 下降而消失；这是 V1.1 的硬边界。
2. `soft stability preference`：多个合法且质量近似的当前继任方案之间，优先变化更小、可保留原 identity 的方案；这是 C1 第七层。

Retention guard 不保护错误事实、已失效 Evidence、错误分段或已证明 duplicate；soft preference 不能使非法 Candidate 入池、越过事实质量或放松 B3 constraints。

### 9.2 Stable ID 与 Revision instance ID

~~~text
stable_memory_id
  durable user-facing Memory identity across published Revisions

revision_memory_instance_id
  immutable representation of that Memory in one Revision
~~~

同一 Memory 在新 Revision 中必须产生新的 instance，但可以继续使用同一 stable ID。不得原地修改旧 Revision，也不得用旧 Candidate instance ID 冒充当前对象。

**案例：** R1 的 `M-001=古镇主街` 与 R2 的 `M-001=古镇主街+寺庙` 共用 stable ID，但分别具有 R1/R2 immutable instance。

### 9.3 对照基线

Lineage 只比较：

~~~text
last successfully published Memory Set
vs.
current Revision winning EditorialPlan
~~~

失败、未发布、内部试算、stale Preview 或旧 Candidate instance 不构成用户可见继承基线。Baseline 将“成功发布且用户可以访问”视为 visible；是否实际打开过页面属于产品 telemetry/UI 专题，不在 S09 猜测。

**案例：** R2 计算完成但发布失败，R3 必须与仍对用户可见的 R1 建立 lineage，不能继承 R2。

### 9.4 CrossRevisionLineageLedger

Lineage 必须分两阶段执行，不能先产生 winner 再检查 retention：

~~~text
Phase A — before final C2 winner
  last published Memory Set
  × all current SelectionRecords
  → pair/group compatibility ledgers
  → protected-prior successor constraints
  → feed constraints into C2 search

Phase B — after state-conditioned plan is chosen
  chosen current entries
  + Phase A ledgers
  → finalize lineage decisions and stable-ID actions
~~~

Phase A 不宣布最终 merge/split winner，但必须确定：每个仍受保护的 prior Memory 有哪些合法 current successor 选择、哪些 group relation 可能成立、哪些情况 unresolved/blocked。否则 C2 可能先选出一个无法满足 V1.1 retention 的 plan。

每个有实质匹配可能的 prior Memory/current SelectionRecord pair 保存：

~~~text
CrossRevisionLineageLedger
  prior_published_memory_ref
  current_selected_record_ref
  same_memory_evidence[]
  different_memory_evidence[]
  scope_change_evidence[]
  invalidating_evidence[]
  lineage_decision
  stable_id_action
  reason_codes[]
  source_refs[]
  policy_and_algorithm_versions
~~~

N→1 merge 与 1→N split 不能由互不知情的 pair decision 拼接。另保存：

~~~text
CrossRevisionLineageGroupLedger
  prior_published_memory_refs[]
  current_selection_record_refs[]
  proposed_cardinality = ONE_TO_ONE | MANY_TO_ONE | ONE_TO_MANY
  shared_core_evidence[]
  distinct_child_or_parent_evidence[]
  primary_core_evidence[]
  compatibility_constraints[]
  readiness = READY_FOR_SEARCH | LINEAGE_UNRESOLVED | LINEAGE_CONTRACT_BLOCKED
  reason_codes[]
  policy_and_algorithm_versions
~~~

Group ledger 只建立当前搜索约束与可能 lineage，不创建新 Candidate。Phase B 仅能从 Phase A 已允许的 relation 中完成 stable-ID mapping。

匹配证据顺序：

1. RawAsset、Evidence、Episode、peak、content-unit 等稳定引用；
2. capture interval、活动 progression/outcome、boundary 与 interruption；
3. grounded Context Motif、anonymous entity 与地点连续性；
4. S07 current-Revision lineage hints；
5. embedding、scene、object/style similarity。

第 5 级只可 nominate，不得单独继承 stable ID 或宣告 same Memory。

### 9.5 Lineage decisions 与 ID 动作

#### `CONTINUES`

同一 Memory 核心不变，只发生重新物化或轻微补充。保留 stable ID，创建新 Revision instance。

#### `EXPANDS`

同一 Episode 获得新的阶段、结果或有效内容范围。保留 stable ID，不新建“同名 Memory 2”。

#### `MERGES`

多个 prior Memory 被当前证据证明是同一 Episode 的错误切碎：

- 若一个 prior Memory 明确保留主要 core，当前 Memory 继承其 stable ID，其他 ID 标为 `merged_into`；
- 若无可信 primary core，创建新 stable ID，所有 prior ID 指向新的 merged Memory；
- 不以发布时间早晚或 ID 顺序伪造语义核心。

#### `SPLITS`

一个 prior Memory 被当前证据证明错误包含多个 Episode：

- 若一个 child 明确保留原 core，它继承旧 stable ID；其他 child 获得新 ID并记录 `split_from`；
- 若无法证明 primary child，所有 child 获得新 ID，旧 ID 保存 `split_into[]`；
- 一个旧 stable ID 不能同时被多个 child 复用。

#### `SUPERSEDES`

旧 Memory 的核心解释错误，当前内容不是其自然延续：旧 ID 不直接复用，当前 Memory 获得新 ID并保存 replacement relation。若只是同一事件中局部 Claim correction、Memory identity 未改变，则可保留 ID并记录 correction，不必使用 supersedes。

#### `NEW_INDEPENDENT`

当前是 prior set 中不存在的独立 Episode/peak，分配新 stable ID，不强行匹配旧 Memory。

### 9.6 Chapter/Aha 类型迁移

stable ID 表达 Memory identity，不永久绑定 presentation type。同一 Memory 从 Aha 扩充为完整 Chapter 时可保留 stable ID，并记录 `AHA_TO_CHAPTER`；原 Aha 不得继续重复占位。

`CHAPTER_TO_AHA` 只允许由错误分段、Evidence 失效等已允许原因触发，不能因数量压力或普通 ranking 下滑发生。

**案例：** R1 只有清晰求婚瞬间，`M-010` 为 Aha；R2 获得准备—求婚—结果的完整 Episode，`M-010` 转为 Chapter，而不是同时保留同 Memory Aha。

### 9.7 Published-Memory retention guard

一个 prior published Memory 若在当前 Revision 中仍满足：

1. 核心事实与 supporting Evidence 有效；
2. Episode/peak identity 未被当前证据推翻；
3. 未被证明 duplicate；
4. 存在合法 current-Revision successor Candidate；

则 winning plan 必须覆盖其一个合法 successor。后来出现更高排名 Candidate 不是 eviction reason。

该要求在 C2 中编码为 protected-prior successor constraint，而不是在 winner 产生后再做补丁式替换。若一个 prior Memory 有多个可能 successor，至少选择一个且不得选择互斥的多个；若 Phase A 无法形成安全 successor set，则在搜索前标记 lineage unresolved/blocked。

当前允许撤回、合并或降级的 reason class 仅为：

~~~text
PROVEN_DUPLICATE
FACT_INVALIDATED
SEGMENTATION_CORRECTED
EVIDENCE_INVALIDATED
~~~

若 prior Memory 仍有效却因 Candidate cap、current contract error 或缺少合法 successor 而消失，这是 `LINEAGE_CONTRACT_BLOCKED`，不能伪装成内容质量下降或 EMPTY_DAY。

**案例：** 下午新增一个更精彩 Episode，不能仅因分数更高而删除上午已经发布且仍有效的古镇 Chapter。该约束要求 S09-D 对 Preview 发布容量保持保守，避免白天过早占满五个位置。

### 9.8 Ambiguous lineage

当无法安全判断 current item 继续、合并或替代哪个 prior Memory 时：

~~~text
LINEAGE_UNRESOLVED
~~~

- 不随机继承 stable ID；
- 不静默撤回 prior Memory；
- 当前 plan 可以保存为内部结果，但不能伪装成 lineage-ready published Revision；
- publication readiness 由 S09-D/S12 检查。

**案例：** prior set 有两个相邻古镇 Chapter，current set 只有一个范围模糊的 Candidate，但证据无法判断它是其中一个的扩充还是二者合并；系统不得仅按较早 ID 选择继承者。

### 9.9 NO_CHANGE

如果 current winning plan 与 last published set 的 stable identity、Memory scope、type 与 lifecycle 均无实质变化，则输出 `NO_CHANGE`，不制造用户不可感知的新发布 Revision。内部计算与 audit 可以保存。

### 9.10 C3 输出

~~~text
RevisionLineageDecision[]
  prior_memory_refs[]
  current_memory_refs[]
  decision
  stable_id_actions[]
  type_transition
  allowed_change_reason
  evidence_refs[]
  readiness = READY | LINEAGE_UNRESOLVED | LINEAGE_CONTRACT_BLOCKED

EditorialRevisionDelta
  added[]
  continued[]
  expanded[]
  merged[]
  split[]
  superseded[]
  withdrawn[]
  no_change
~~~

## 10. S09-D1｜Executable Day State Proposal

**状态：CONFIRMED**

### 10.1 Day State 与运行结果分离

S09 只允许提出三个内容状态：

~~~text
CHAPTER_DAY
HIGHLIGHT_DAY
EMPTY_DAY
~~~

`DAY_STATE_NOT_PROPOSED` 不是第四种 Day State，而是本次 Revision 因合同、lineage、search 或 operational 问题没有资格提出新状态。`NO_CHANGE` 也不是 Day State，而是沿用上一成功发布结果的 Editorial action。

算法失败、预算不足或 lineage 阻塞不能伪装成 `EMPTY_DAY`。

### 10.2 判定前置条件

进入状态判断前必须确认：

1. current Revision/snapshot 与输入引用合法；
2. C2 search 已完成，或其 limitation 足以支持所提出的非空结论；
3. 没有会隐藏潜在有效 Memory 的 contract failure；
4. prior published Memory retention/lineage 已 READY；
5. 所有 excluded unresolved/operational Candidate 已完成 D3 impact assessment；
6. 没有把 network/provider/budget/timeout 等 operational failure 当成内容不足。

不能满足时输出：

~~~text
DAY_STATE_NOT_PROPOSED
blocker_class
preserve_last_published_revision
~~~

Operational exclusion 不自动阻断已有合法非空 plan：若它只能限制 recall，而不会改变当前 Day State 合法性或 prior retention，可带 limitation 继续；若它可能决定 EMPTY/non-empty、HIGHLIGHT/CHAPTER 或 protected-prior successor，则必须阻断。

**案例：** 生日 Candidate 是当天唯一潜在 Memory，却因网络故障未完成必要 S08 验证。当前不能宣告 EMPTY_DAY；Preview 保留上一成功发布结果并记录 operational failure。若当天已有一个独立、直接 ELIGIBLE 的学校表演 Chapter，而失败的只是额外颁奖 Aha，则 Chapter 可以在明确 `RECALL_ONLY` limitation 下继续。

### 10.3 状态判定顺序

~~~text
revision is state-decidable?
├─ no  → DAY_STATE_NOT_PROPOSED
└─ yes
   ├─ any legal Chapter plan?
   │  └─ yes → CHAPTER_DAY
   └─ no
      ├─ any Aha passes HIGHLIGHT_DAY_STANDALONE_GATE?
      │  └─ yes → HIGHLIGHT_DAY with exactly one Aha
      └─ no
         ├─ complete proof of no publishable Memory?
         │  └─ yes → EMPTY_DAY
         └─ no  → DAY_STATE_NOT_PROPOSED
~~~

状态优先级是 frozen state-machine semantics，不是让 Aha-only plan 与合法 Chapter plan 按戏剧性竞争。

### 10.4 CHAPTER_DAY

形状：

~~~text
1–5 Chapters
0–3 Ahas
~~~

至少存在一个同时满足 current eligibility、B3 constraints、set-level marginal contribution、lineage retention 与 count policy 的合法 Chapter plan。第五 Chapter 还必须通过 D2 exceptional gate。

只要有合法完整 Chapter，就不能因为某个 Aha 更戏剧化而改成 HIGHLIGHT_DAY。

**案例：** “生日聚会”形成完整 Chapter，同时“吹蜡烛时突然合唱”形成独立 Aha，状态为 `CHAPTER_DAY: 1 Chapter + 1 Aha`。

### 10.5 HIGHLIGHT_DAY_STANDALONE_GATE

只有不存在合法 Chapter plan 时才检查 HIGHLIGHT_DAY。输出形状固定为：

~~~text
0 Chapter
exactly 1 strong Aha
~~~

该 Aha 必须同时满足：

1. S07 Local Peak Gate PASS；
2. S07 Independent Memory Value Gate PASS；
3. 所有必要 S08 validation PASS；
4. 不依赖一个未入选 Chapter 才能理解；
5. 自身 grounded Evidence 足以支持具体局部事件；
6. 无实质 contradiction 或高 inference risk；
7. 与 prior published Memory 不重复；
8. 当前 Revision relation/lineage 合法。

此 gate 只读取已有结构化证据，不增加模型调用。证据无法证明 standalone 时不能猜测 PASS。

**正例：** 一段 Manual Video 独立记录了求婚发生与回应，但素材不足以形成完整 Episode；可成为 HIGHLIGHT_DAY。

**反例：** 只有桌上戒指照片，无法确认是否发生求婚；不能因“看起来重要”成为 HIGHLIGHT_DAY。

### 10.6 多个 standalone Aha

V1.1 已冻结 HIGHLIGHT_DAY 为 exactly one Aha。若没有 Chapter、但存在多个通过 standalone gate 的 Aha，先执行 C3 retention：

1. 若 last published HIGHLIGHT Aha 仍有效且存在合法 current successor，该 successor 必须保留；新独立 Aha 不能仅因更精彩或 ranking 更高而替换它；
2. 若 prior Aha 已由允许 reason invalidated/merged/superseded，或不存在受保护 prior Aha，才按 C1 选择最可信、最独立、最能代表当前日的一个；
3. 若新 Candidate 是 prior Aha 的同一 Memory continuation/expansion，则它不是第二个 Aha，沿用 stable identity 后参与选择。

其他未选 Aha 记录：

~~~text
HIGHLIGHT_DAY_SINGLE_AHA_LIMIT
HIGHLIGHT_DAY_SINGLE_AHA_LIMIT_VALID_PRIOR_RETAINED
~~~

不能输出 `0 Chapter + 2/3 Aha`。若未来需要该产品形状，必须显式重开 V1.1。

**跨 Revision 案例：** R1 已发布“收到录取通知”Aha；R2 又出现独立“朋友送来礼物”Aha。若录取通知仍有效，R2 保留其 successor，礼物 Aha 记录 `HIGHLIGHT_DAY_SINGLE_AHA_LIMIT_VALID_PRIOR_RETAINED`，不能按普通排名换掉旧 Memory。

### 10.7 EMPTY_DAY

形状：

~~~text
0 Chapter
0 Aha
~~~

EMPTY_DAY 表示：在当前允许处理且处理成功的 Evidence 中，没有足以安全发布的 Chapter 或 standalone Aha；不表示用户客观上什么都没做。

允许的 reason 包括：

~~~text
NO_ELIGIBLE_MEMORY_CANDIDATE
NO_INDEPENDENT_MEMORY_VALUE
INSUFFICIENT_EVIDENCE_AFTER_ALLOWED_PROCESSING
ALL_CONTENT_OUTPUT_INACTIVE
~~~

以下情况不能输出 EMPTY_DAY：

- network/provider/operational budget failure；
- search/contract failure 可能隐藏合法非空 plan；
- lineage unresolved/blocked；
- prior published Memory 因程序问题缺少 current successor；
- 尚未探索的组合可能形成合法非空结果。

**案例：** 全天只有重复办公桌、普通走廊与通勤，所有流程正常结束且没有独立 Memory value，可以输出 EMPTY_DAY。

### 10.8 Search limitation 与 empty proof

当 C2 为 `BEST_LEGAL_WITH_SEARCH_LIMIT` 且 best-found plan 为空时，不能宣告 EMPTY_DAY，因为未探索分支可能包含非空合法组合。

只有 `EXACT_WITHIN_POLICY`，或存在等价的完整 infeasibility proof，才允许建立 empty-day proof。非空 best-found plan 可以形成带 `optimality_proven=false` 的 provisional state proposal，publication readiness 留给 D3/S12。

### 10.9 State-conditioned search output

C2 同一次 traversal 应保存：

~~~text
best_chapter_day_plan
best_highlight_day_plan
empty_day_feasibility_proof
~~~

D1 再按冻结的状态顺序选择。不得先得到一个通用 plan，再为匹配状态机临时删除或降级内容。这是 C2 输出视图的精化，不改变其确定性约束搜索架构。

### 10.10 NO_CHANGE

若 current winning plan 与 last published set 在 stable identity、scope、type、state 与 lifecycle 上均无实质变化：

~~~text
editorial_action = NO_CHANGE
day_state = preserve last published day_state
~~~

内部 Revision computation/audit 可以保存，但不制造无用户价值的新发布 Revision。

### 10.11 D1 输出

~~~text
DayStateProposal
  proposal_status = PROPOSED | DAY_STATE_NOT_PROPOSED | NO_CHANGE
  proposed_state = CHAPTER_DAY | HIGHLIGHT_DAY | EMPTY_DAY | null
  selected_plan_ref
  state_shape_check
  chapter_plan_feasibility
  highlight_standalone_gate
  empty_day_proof
  prior_state_transition
  search_status
  lineage_readiness
  blocker_class
  preserve_last_published_revision
  reason_codes[]
  policy_and_algorithm_versions
~~~

S09 只提出状态；S12 仍执行发布前最终验证。

## 11. S09-D2｜Fifth Chapter Gate & Preview Capacity Reserve

**状态：CONFIRMED**

### 11.1 Count policy

~~~text
Preview CHAPTER_DAY
  Chapters <= 4
  Ahas <= 2
  fifth Chapter gate = CLOSED

Final CHAPTER_DAY
  ordinary Chapters <= 4
  Ahas <= 3
  fifth Chapter only after exceptional gate PASS
~~~

Preview 不限制为三个 Chapter：第四个独立强 Episode 已经出现时可以继续累加；同时不在白天过早占满五个受 retention guard 保护的位置。Aha 没有第四个例外位置，因此 Preview 最多两个，为 Final 保留一个位置。

这些是发布容量，不是 Candidate generation Top-K。未发布的合法 Candidate 继续保留并在后续 Revision 重评。

### 11.2 第五章不是单体排名第五

S09 分别求解：

~~~text
P4 = best legal plan with 1–4 Chapters
P5 = legal plan with exactly 5 Chapters
~~~

对每个 P5，依次移除每个 Chapter，并重新优化剩余 Aha。按照 C1 高优先级目标，删除后损失最小的成员是该 P5 的 weakest marginal Chapter；如多个成员并列，全部进入 marginal set。只有连 weakest marginal contribution 都达到严格例外标准，五章方案才可能成立。

**案例：** 古镇、陶艺、朋友重逢、求婚与普通出租车构成五个候选。删除出租车几乎不损失重要 Memory，P5 失败，不能将“排行榜第五名”直接发布。

### 11.3 七道 exceptional gates

五章 plan 必须全部通过：

1. **Normal Chapter Gate**：五个成员分别达到相同的 Truth、coherence、Memory value、content-unit、Revision、lineage 与必要 validation 门槛；
2. **Distinct Complete Episode Gate**：weakest marginal member 仍是独立完整 Episode，不是已有经历的画面角度；
3. **Non-mergeable Gate**：不能合理并入另外四章；
4. **Important Day Omission Gate**：删除后会完全遗漏当天一段重要生活，其他 Chapter/Aha 无法表达；
5. **Chapter-scale Gate**：不是短暂 peak 或 Aha 尺度；
6. **Redundancy/Risk Gate**：与其他四章没有可避免的实质冗余或高推断风险；
7. **Set Increment Gate**：P5 必须在 meaningful Episode coverage / trusted independent Memory value 等 C1 高优先层真实优于 best <=4 plan；数量、排名或 stable-ID 便利不能单独使它 PASS。

Manual intent、明确 outcome、持续活动、重要互动或事件变化都可支持“important”，但任何单一信号均不能自动判定。无法可靠证明时第五章默认 FAIL。

### 11.4 Executable rule

~~~text
P5 is legal
AND every member passes normal Chapter gates
AND weakest marginal member passes all exceptional gates
AND P5 materially improves higher-tier day coverage/value over best <=4 plan
AND no member can be reasonably merged or represented as Aha
→ FIFTH_CHAPTER_PASS

otherwise
→ FIFTH_CHAPTER_FAIL
→ use best legal plan with <=4 Chapters
~~~

**PASS 案例：** 热气球、陶艺课程、与多年未见朋友重逢、求婚、夜间灯会分别有独立过程与可靠结果；删除任何一项都会遗漏明显不同的核心生活。

**FAIL 案例：** 生日 Chapter 内的吹蜡烛虽然精彩，但属于 Aha 尺度；不能成为第五章。

### 11.5 Fifth gate lifecycle

~~~text
Preview Revision
  FIFTH_CHAPTER_GATE = NOT_EVALUATED_PREVIEW

Final Revision or legitimate post-Final late-data Revision
  FIFTH_CHAPTER_GATE = EVALUATE
~~~

用户明确结束当天或单次导入直接走 Final 时，可以立即评估第五章；普通 Preview 不能开放第五章。

### 11.6 Preview reserve 不删除 Candidate

超过 Preview 发布容量的合法 Candidate：

- 不改写为 rejected/suppressed；
- 不从 Candidate/audit 删除；
- 不改变 S07/S08 disposition；
- 下一 Revision 与 Final 重新参加 full-day selection；
- 当前 S09 exclusion/audit 使用：

~~~text
DEFERRED_BY_PREVIEW_CHAPTER_RESERVE
DEFERRED_BY_PREVIEW_AHA_RESERVE
~~~

**案例：** R2 已发布四个 Chapter，晚上新出现生日 Candidate。普通 Preview 不发布第五章，但完整保留；Final 再执行 exceptional gate。

### 11.7 Preview 已满后的 retention

四个已发布且仍有效的 Preview Chapter 不能因新 Candidate 普通排名更高而被替换。只有 `PROVEN_DUPLICATE / FACT_INVALIDATED / SEGMENTATION_CORRECTED / EVIDENCE_INVALIDATED` 或合法 merge/type transition 才能释放位置。

**案例：** 午餐 Episode 已真实、完整发布；后来出现更精彩演唱会不能仅按分数删除午餐。演唱会在 Final 参加第五章判断。

这种累加体验会产生 first-arrival retention pressure。必须记录真实数据，后续评估是否需要显式重开 V1.1；当前不得通过伪造 duplicate 或错误 reason 绕过。

### 11.8 Preview split-correction overflow

当 prior Preview 已发布四个 Chapter，而新 Boundary/Segmentation Evidence 证明其中一个 prior Chapter 必须 split，导致 current Preview 需要五个合法 Chapter 才能完整表达时：

~~~text
pure SEGMENTATION_CORRECTED
+ current corrected Chapter count = 5
+ Preview fifth gate = CLOSED
→ do not publish a partial four-child correction
→ HOLD_PREVIOUS_REVISION
→ PREVIEW_SPLIT_CORRECTION_DEFERRED_TO_FINAL
~~~

当前 corrected plan、split lineage、两个 child Candidate 与全部 Evidence 继续保存在内部 attempt/audit；不能把某个 child 改成 rejected，也不能为满足 cap 假装 merge。Final 重新执行 full-day selection 与 fifth gate：PASS 时可发布五章，FAIL 时发布最佳 <=4 plan，并明确记录未选 child 的 set-level reason。

这条规则只适用于“事实仍成立、但 Episode grouping 被证明需要拆分”的纯 segmentation correction。若 prior Memory 含 `FACT_INVALIDATED` 或 `EVIDENCE_INVALIDATED`，不能借 HOLD 继续保护已知错误内容，必须走相应撤回/修正与 publication-blocking 合同。

**案例：** R1 的 `M1=上午古镇+晚上再次古镇` 与另外三章共四章；R2 证明 M1 必须拆成两个独立 Episode，合计五章。R2 不临时隐藏任一 child，也不开 Preview 第五章，而是保持 R1，等待 Final 对 corrected P4/P5 做完整决策。

### 11.9 Final 后第六个 Episode

全天硬上限继续为五个 Chapter。若五个已发布 Chapter 均仍有效，Late Data 又产生第六个强 Episode：

- 不输出六章；
- 不因普通 ranking 删除旧 Chapter；
- 只有合法 merge/correction/invalidation 才能释放位置；
- 新 Episode 保留在事实账本、Candidate 与 selection audit 中，但不进入 Diary。

reason：

~~~text
DAY_CHAPTER_CAP_REACHED_VALID_PRIOR_RETAINED
~~~

这属于当前产品数量合同的显式取舍，不得报告为算法失败。

### 11.10 D2 outputs

~~~text
FifthChapterGateLedger
  best_up_to_four_plan_ref
  five_chapter_plan_ref
  marginal_chapter_refs[]
  normal_chapter_gate
  distinct_episode_gate
  non_mergeable_gate
  important_day_omission_gate
  chapter_scale_gate
  redundancy_gate
  set_increment_gate
  result = PASS | FAIL | NOT_EVALUATED_PREVIEW
  reason_codes[]
  evidence_refs[]

PreviewCapacityDecision
  chapter_publish_cap = 4
  aha_publish_cap = 2
  published_refs[]
  deferred_refs[]
  retention_pressure
  reason_codes[]

PreviewCorrectionHold
  prior_published_set_ref
  current_corrected_plan_ref
  split_lineage_refs[]
  overflow_count
  action = HOLD_PREVIOUS_REVISION
  reason = PREVIEW_SPLIT_CORRECTION_DEFERRED_TO_FINAL
~~~

D2 只使用现有结构化结果，不增加媒体上传、模型调用或 RawAsset 重读。

## 12. S09-D3｜Output Contract & Downstream Readiness

**状态：CONFIRMED**

### 12.1 S09 不能声明 PUBLISH_READY

S09 最多声明 selection 可以进入后续阶段：

~~~text
downstream_readiness = READY_FOR_S10
publication_readiness = NOT_YET_EVALUATED
~~~

即使 S09 合法，S10 仍可能无法形成合格媒体，S11 仍可能产生不受支持文字，S12 仍需验证整体合同。最终 `PUBLISH_READY` 只能由 S12 决定。

### 12.2 S09ResultBundle

~~~text
S09ResultBundle
  run_identity
  selectable_pool_summary
  selected_memory_set
  day_state_proposal
  editorial_revision_delta
  relation_decisions
  fifth_chapter_gate
  preview_capacity_decision
  selection_exclusion_audit[]
  excluded_uncertainty_impact_assessments[]
  search_audit
  s10_handoff_envelopes[]
  downstream_readiness
  policy_and_algorithm_versions
  policy_version_compatibility_assessment
~~~

`run_identity` 至少绑定 `user_local_day / daily_memory_run_id / revision_id / snapshot_id / selection_attempt_id`。Bundle 提交后 immutable；任何 re-selection 产生新的 attempt 与 audit，不能改写旧结果。

### 12.3 SelectedMemorySet 与 entry

~~~text
SelectedMemorySet
  selected_chapters[]
  selected_ahas[]
  proposed_day_state
  stable_identity_decisions[]
  set_fingerprint

SelectedMemoryEntry
  selected_memory_entry_id
  selection_record_ref
  current_candidate_ref
  memory_type = CHAPTER | AHA
  stable_memory_id or stable_id_allocation_key
  revision_memory_instance_id
  canonical_output_index
  memory_scope_refs[]
  candidate_content_unit_refs[]
  keep_evidence_refs[]
  context_only_refs[]
  limitation_refs[]
  marginal_contribution_trace
  relation_decision_refs[]
  lineage_decision_ref
~~~

Entry 只保存引用与 S09 决策，不复制上游事实、不选择 Frame、不决定媒体格式。

**案例：** “生日 Chapter”入选时只确定 Memory identity、范围与允许 Evidence；合照、吹蜡烛或礼物的最终媒体由 S10 决定。

#### 12.3.1 Canonical output order

集合成员选择与输出排序是两个独立步骤。C1/C2 先确定合法成员；只有成员、Day State 与 lineage 已确定后，才计算 deterministic canonical order。输出顺序不能参与候选胜负、数量判断、第五章 gate 或 retention，也不能成为未入选 reason。

Chapter 的 canonical order：

1. 按该 Chapter 所有 selected KEEP content 的最早 `capture_start` 升序；
2. 最早时间相同时，按该 Chapter selected KEEP content 的最晚 `capture_end` 升序；
3. 仍相同时，按 `stable_memory_id` 升序；尚未分配 stable ID 时按 `stable_id_allocation_key` 升序。

Aha 的 canonical order：

1. 按已由上游 Evidence 确定的 `peak_capture_time` 升序；
2. 相同时，按 `stable_memory_id` 升序；尚未分配 stable ID 时按 `stable_id_allocation_key` 升序。

每个 `SelectedMemoryEntry` 输出 `canonical_output_index`。用于排序的时间与 identity 必须来自当前合法结构化记录；缺失时属于 selection contract invalid，不能退回到数组输入顺序、模型分数或不稳定的数据库返回顺序。

补充边界：

- resumed Chapter 使用其 selected content 的最早开始时间，因此“上午古镇—奶茶中断—继续古镇”仍排在下午 workshop 之前；
- embedded distinct Aha 仍位于 `selected_ahas[]`，按自己的 peak time 排序，不插入 Chapter 数组；
- `selected_chapters[]` 与 `selected_ahas[]` 各自在本类型数组内排序，不建立跨类型的统一价值榜；
- canonical order 只稳定 S09 数据合同与下游展示交接；S10 仍独立决定一个 Chapter 内部的 EvidenceAnchor 和媒体叙事顺序；
- C1 第八层仍可用稳定时间键/identity key 解决完全等价 plan 的 membership tie；它不读取 `canonical_output_index`，也不等于用输出位置给 Candidate 排名；
- `set_fingerprint` 使用 canonical ordered identities 形成确定性序列，但集合价值与成员等价判断仍按 set semantics 执行。

**案例 1：** 09:00 古镇、14:00 陶艺、20:00 生日三个 Chapter 中，即使生日的记忆价值最高，输出仍为古镇→陶艺→生日；高价值不会把它改排到第一。

**案例 2：** 两个 Aha 的 peak 都落在 20:16:00，使用 stable ID / allocation key 做最终 tie-break；同一 Revision 重跑不会随机换序。

### 12.4 S10HandoffEnvelope 是 Evidence 白名单

~~~text
S10HandoffEnvelope
  selected_memory_ref
  candidate_content_unit_refs[]
  anchor_eligible_keep_evidence_refs[]
  context_only_non_anchor_refs[]
  raw_asset_refs[]
  source_offsets[]
  quality_motion_stability_refs[]
  validation_findings[]
  limitation_refs[]
  allowed_hq_source_handles[]
  hq_source_handle_status = AVAILABLE | NOT_YET_MATERIALIZED | UNAVAILABLE | UNKNOWN
  forbidden_scope_reason_refs[]
~~~

- KEEP 可以进入 EvidenceAnchor shortlist；
- CONTEXT_ONLY 只帮助理解顺序，`anchor_eligible=false`；
- DROP 不得进入白名单；
- S10 不得重新搜索全天或扩大 selected Candidate scope；
- 漂亮媒体不能反向改变 Memory selection。

S09 必须完整给出 Evidence/RawAsset/source-offset allowlist、handle provenance 与已知 availability status，但不要求所有 HQ handle 在进入 S10 前已经 materialize。Anchor、format、fallback 与最小 HQ request 正是 S10/S13 的职责；`NOT_YET_MATERIALIZED / UNAVAILABLE / UNKNOWN` 必须作为 limitation 传递，由 S10 判断是否仍能形成媒体计划或返回 `MEDIA_UNRESOLVED`。

**案例：** 奶茶店仅是古镇 Chapter 的 CONTEXT_ONLY interruption。S10 可以理解路线中断，但不能把奶茶照片选成古镇 Chapter 的精选媒体。

### 12.5 Excluded uncertainty impact

S08 bounded frontier/budget 的目的不是让任何未验证 Candidate 都阻断整天；但 operational failure 也不能伪装成内容不存在。S09 对每个 unresolved/operational exclusion 建立：

~~~text
ExcludedUncertaintyImpactAssessment
  excluded_candidate_ref
  upstream_outcome_class
  impact =
    EVIDENCE_LIMITED_PRECISION_EXCLUSION |
    POLICY_OR_OPERATION_RECALL_ONLY |
    STATE_OR_RETENTION_CRITICAL |
    NON_IMPACTING_PROVEN
  affected_state_shapes[]
  affected_prior_memory_refs[]
  limitation_refs[]
  reason_codes[]
~~~

- `EVIDENCE_LIMITED_PRECISION_EXCLUSION`：允许 Evidence 已用尽但仍 inconclusive；Candidate 继续不入池，其他合法结果可继续，EMPTY 可使用 `INSUFFICIENT_EVIDENCE_AFTER_ALLOWED_PROCESSING`；
- `POLICY_OR_OPERATION_RECALL_ONLY`：可能遗漏额外/更优内容，但当前非空 plan 的合法性、Day State 与 protected-prior successor 不依赖它；允许继续并显式标记 recall limitation；
- `STATE_OR_RETENTION_CRITICAL`：可能决定 empty/non-empty、HIGHLIGHT/CHAPTER、受保护 prior successor 或当前集合合法性；必须 HOLD/BLOCKED；
- `NON_IMPACTING_PROVEN`：已证明不会改变当前选择/状态。

**案例：** 已有 direct ELIGIBLE 的学校表演 Chapter，额外颁奖 Aha provider failed，可为 recall-only；若该失败 Candidate 是全天唯一潜在 Memory，则为 state-critical，不能输出 EMPTY_DAY。

### 12.6 Downstream readiness states

#### `READY_FOR_S10`

用于非空 CHAPTER_DAY/HIGHLIGHT_DAY，必须满足：

1. selected records 全部 current-Revision 合法；
2. eligibility、B3 constraints、marginal contribution、Day State/count、D2 与 lineage 全部通过；
3. search exact，或 membership/day state 已额外证明不受未探索分支影响；
4. 无 outcome-changing contract error；
5. 无 `STATE_OR_RETENTION_CRITICAL` exclusion；recall-only limitation 已完整附带；
6. S10 Evidence whitelist、source provenance 与 handle availability metadata 完整；不要求 HQ source 已实际 materialize。

#### `EMPTY_READY_FOR_S12`

EMPTY_DAY 具有完整 empty proof、无 operational blind spot；跳过 Memory media/narrative creation，直接进入 S12 的 empty-state validation。

#### `NO_CHANGE_REUSE`

selection identity、scope、type、state 与 lineage 无实质变化。若下游 input/policy fingerprint 也完全一致，可复用既有 S10/S11 artifacts；若下游版本变化，编排层可只重跑失效阶段，但不得改写 S09 selection。

#### `HOLD_PREVIOUS_REVISION`

普通 Preview 因 lineage unresolved、search 不足、outcome-changing contract failure 或 state/retention-critical operational failure 等不能安全继续；存在 prior published Revision 时保持上一版，不发布当前不完整结果。Recall-only exclusion 本身不强制 HOLD。

#### `BLOCKED_NO_PUBLISHABLE_REVISION`

没有 prior 可保持，或 Final selection 无法形成可靠下游输入。Final blocked 时不得把旧 Preview 偷偷改名为 Final。

### 12.7 Search-limited readiness

~~~text
EXACT_WITHIN_POLICY
→ may continue if all other readiness gates pass

BEST_LEGAL_WITH_SEARCH_LIMIT
→ default HOLD/BLOCKED
~~~

受限结果只有同时具备：

~~~text
winning_membership_proven = true
day_state_proven = true
~~~

才可继续。证明必须覆盖 selected membership、Day State、第五章结果与 prior Memory lineage；找到一个合法 plan 本身不够。

### 12.8 Contract error impact

每个 contract error 分类为：

~~~text
NON_IMPACTING_PROVEN
POTENTIALLY_OUTCOME_CHANGING
~~~

只有前者可在完整留痕后继续。后者必须 HOLD/BLOCKED。

**案例：** 重复物化副本被隔离，合法原记录仍存在，且证明不会改变任何 plan，可继续；若被隔离对象可能成为重要 Chapter，则不能发布一个缺内容的结果。

#### 12.8.1 Same-day policy-version compatibility

同一个 `DailyMemoryRun` 的多个 Revision 原则上应由编排层固定同一套 pipeline/selection policy version；具体 pin 与 migration 机制属于 S00/工程集成，不由 S09 发明。

S09 必须保存 prior published Revision 与 current Revision 的完整 policy/version fingerprint。两者不同时：

1. 只有存在显式、versioned、可审计的 compatibility/migration result，且能证明 eligibility、retention、lineage、Day State 与 count semantics 兼容，才可继续；
2. 若 prior valid Memory 只因 policy 变化而没有 current successor，不能把它记成 duplicate、低价值、无边际贡献或正常 eviction；
3. 兼容性无法证明时，分类为 `POTENTIALLY_OUTCOME_CHANGING`，Preview 使用 `HOLD_PREVIOUS_REVISION`，无可保持版本或 Final 使用 `BLOCKED_NO_PUBLISHABLE_REVISION`；
4. 不得以新版本的一次 best-found plan 代替 migration proof。

reason 至少保留：

~~~text
POLICY_VERSION_COMPATIBILITY_UNPROVEN
POLICY_ONLY_PRIOR_DISAPPEARANCE
~~~

**案例：** 中午 Preview R1 用 policy-v19 发布“古镇游览”；下午 R2 被意外切换到 policy-v20，阈值变化让该 Candidate 消失。没有显式 migration proof 时，R2 保持 R1，不能把古镇 Memory 解释成“价值下降后被淘汰”。

### 12.9 S10/S12 不得静默替换 Memory

S10 只能对 selected Memory 执行 `Content Beat → EvidenceAnchor → Media Format`。发生 `MEDIA_UNRESOLVED` 时必须返回失败，不能自行换 Candidate、搜索未选素材、恢复 CONTEXT_ONLY/DROP 或用其他 Memory 媒体替代。

S12 可以按其后续合同拒绝媒体、Claim 或整个结果，但不能新增/替换 Chapter/Aha。任何 membership 变化必须显式重入 S09，产生新的 selection attempt，并重新检查 Day State、数量、lineage 与集合约束。

“S10 失败后是否允许一次有界 S09 re-selection”留给 S10 专题；即使未来允许，也不能由 S10 直接换人。

### 12.10 SelectionExclusionAudit

每个 SelectionRecord 必须有最终去向，reason 至少区分：

~~~text
SELECTED
HARD_CONSTRAINT_EXCLUDED
SAME_MEMORY_REDUNDANCY
NO_MARGINAL_CONTRIBUTION
LOWER_EXACT_SET_VALUE
DEFERRED_BY_PREVIEW_CHAPTER_RESERVE
DEFERRED_BY_PREVIEW_AHA_RESERVE
HIGHLIGHT_DAY_SINGLE_AHA_LIMIT
HIGHLIGHT_DAY_SINGLE_AHA_LIMIT_VALID_PRIOR_RETAINED
FIFTH_CHAPTER_GATE_FAILED
DAY_CHAPTER_CAP_REACHED
CONTRACT_QUARANTINED
NOT_IN_BEST_FOUND_PLAN_UNDER_SEARCH_LIMIT
~~~

只有 exact search 才能使用 `LOWER_EXACT_SET_VALUE`。受限搜索未入选项只能表述为未进入 current best-found plan，不能声称已证明全局更差。

### 12.11 下游路线

~~~text
CHAPTER_DAY / HIGHLIGHT_DAY + READY_FOR_S10
→ S10 → S11 → S12

EMPTY_DAY + EMPTY_READY_FOR_S12
→ skip Memory media/narrative creation
→ S12 validates empty proof/state

NO_CHANGE_REUSE
→ reuse exact unchanged artifacts
  or rerun only version-invalidated downstream stages

HOLD_PREVIOUS_REVISION / BLOCKED_NO_PUBLISHABLE_REVISION
→ no normal publish path
~~~

## 13. S09 freeze closure

1. A1–D3 全链路与 S00–S08/S10–S12 边界交叉检查：已完成；
2. 12 个用户画像、288 个两分钟语义时间点与 adversarial Revision 模拟：已完成；
3. F1–F8 结构冲突、遗漏与不可执行定义修复：已完成；
4. freeze-readiness report 与用户最终确认：已完成；V1.19 canonical checkpoint 已生成。
