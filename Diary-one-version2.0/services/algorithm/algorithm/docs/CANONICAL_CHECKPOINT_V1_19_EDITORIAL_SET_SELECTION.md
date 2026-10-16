# Diary One Canonical Checkpoint V1.19 — S09 Editorial Set Selection

**状态：** FROZEN
**冻结日期：** 2026-08-27
**决策来源：** 用户逐项确认 S09-A1–D3、F6 Preview split overflow、F7 canonical ordering，并在 freeze-readiness review 通过后最终确认冻结
**作用范围：** S09 selectable pool、SelectionRecord、Candidate relation、集合约束、集合目标、确定性搜索、跨 Revision lineage、Day State proposal、Preview/Final 数量、第五章、输出与 S10/S12 readiness
**继承关系：** 继承 V1.18–V1.1 与 V1.0 未被本文覆盖的规则
**验证依据：** [S09 Working V0.1](S09_EDITORIAL_SET_SELECTION_CONSOLIDATED_WORKING_V0_1.md)、[S09 Cross-check V0.1](S09_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_1.md)、[B3 Fine-Grained Simulation](S09_B3_FINE_GRAINED_TIMELINE_SIMULATION_V0_1.md)、[Full Selection Fine-Grained Simulation](S09_FULL_SELECTION_FINE_GRAINED_SIMULATION_V0_1.md)
**明确不覆盖：** S10 具体媒体算法、S11 Narrative、S12 最终 Claim/发布验证、App 后台上传工程、Firmware/SDK、共享状态文件、16s/73s 等非标准 Manual Window、隐私/伦理/治理专题

## 1. 冻结结论

S09 只在 S07/S08 已经形成的可信 Candidate 上，选择一个合法、低重复、具有实质记忆贡献、跨 Revision 可解释的全天 Memory 集合。

~~~text
S07 direct ELIGIBLE Candidate
or S08 VALIDATED_FOR_S09 wrapper
→ current-Revision Selectable Pool
→ SelectionRecord
→ typed relation graph + executable constraints
→ pre-search protected-prior lineage constraints
→ state-conditioned deterministic set search
→ CHAPTER_DAY / HIGHLIGHT_DAY / EMPTY_DAY proposal
→ Preview capacity / Final fifth-Chapter decision
→ final lineage + canonical output order
→ S10 Evidence whitelist or S12 empty validation
~~~

S09 不是 Candidate 单体排行榜，也不是简单 Top-K。它不能创建新事实、重新看 Raw、补 Auto 帧、调用新的视觉/强模型、选择 hero、决定媒体格式、写标题或宣告 `PUBLISH_READY`。

**案例：** 古镇、客户演示和生日三个 Candidate 单体都很强；另有两个表达同一古镇 outing 的候选。S09 选择覆盖古镇、演示、生日且不重复的一套，而不是按单体分数取前四名。

## 2. Selectable Pool 与 Hard Eligibility

### 2.1 两条合法入池路径

~~~text
S07 Candidate
├─ 已直接满足全部 S09 前置条件
│  └─ DIRECT_ELIGIBLE
├─ 存在必要 S08 ValidationTask，且全部 PASS
│  └─ VALIDATED_ELIGIBLE
└─ rejected / unresolved / operational / stale
   └─ PoolExclusionAudit only
~~~

逻辑输入为：

~~~text
S07 direct ELIGIBLE Candidates
+ S08 VALIDATED_FOR_S09 wrappers
→ normalize by current Candidate content identity
→ one selectable entry per Candidate
~~~

### 2.2 单一内容身份

1. 同一个 S07 Candidate 与其合法 `ValidatedCandidate` wrapper 只形成一个池成员；
2. wrapper 是验证凭证，不创建新的 Memory 内容；
3. 当前 Revision 每个 Candidate content identity 最多一个 selectable entry；
4. prior Revision 只提供 lineage 证据，旧 Candidate instance 不能混入当前池；
5. normalization 只允许“Candidate + 指向它的合法 wrapper”。

以下不是 normalization，而是合同错误：

- 两个 S07 Candidate record 异常声明同一 current identity；
- wrapper 指向不一致 Candidate；
- 同一 identity 跨 Revision 混用。

这些情况输出 `IDENTITY_CONFLICT / SELECTION_CONTRACT_INVALID`，隔离受影响对象并执行影响评估；不能选择第一条、静默去重或伪装成正常 duplicate suppression。

### 2.3 Hard Eligibility

池成员必须同时满足：

1. 属于当前 user/day、`DailyMemoryRun`、Revision 与 input snapshot；
2. Candidate、Seed、Episode/Moment/Observation/Evidence refs 合法、current、可追溯；
3. S07 disposition 允许下游选择；
4. 有必要 S08 task 时，全部必要 task PASS 且 wrapper 合法；
5. 不属于 `REJECTED_BY_EVIDENCE / UNRESOLVED_EVIDENCE / UNVALIDATED_OPERATIONAL / STALE_FOR_CURRENT_REVISION`；
6. Candidate type、content identity 与上游事实未被 S09 改写；
7. 所有关联 `AlternativeResolution` 已附带。

数量目标不是最低配额。任何 excluded、unresolved、operational 或 stale Candidate 都不能为了凑 3–4 Chapter 或 2–3 Aha 恢复入池。

### 2.4 输出

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

**案例：** 同一“吹蜡烛 Aha”在 S07 产生 Candidate，S08 确认火焰确实熄灭。S09 只得到一个 `VALIDATED_ELIGIBLE` entry，不能把 Candidate 和 wrapper 计成两个 Aha。

## 3. SelectionRecord

`SelectionRecord` 是当前 Revision 中一个 selectable Candidate 的规范化“候选选择卡”。它只整理上游事实、引用和版本，不创建事实、不改变 Candidate，也不等于最终选择结果。

~~~text
SelectionRecord
  identity_and_version
  memory_scope
  trust_basis
  memory_value_basis
  relation_inputs
  revision_lineage_and_provenance
~~~

### 3.1 identity_and_version

- `selection_record_id`；
- `candidate_instance_ref`；
- `candidate_type = CHAPTER | AHA`；
- Chapter form：`SINGLE / ADJACENT_GROUP / RESUMED_EPISODE / LOCAL_EPISODE_GROUP`；
- `revision_id / snapshot_id`；
- upstream Candidate fingerprint；
- `eligibility_source = DIRECT_ELIGIBLE | VALIDATED_ELIGIBLE`。

`selection_record_id` 必须由 Candidate identity、Revision 与 SelectionRecord schema/policy version 确定性生成。

### 3.2 memory_scope

- capture interval；
- source/owner/participant Moment refs；
- CandidateContentUnit refs；
- KEEP RawAsset refs；
- EpisodeGroupSignature ref；
- Chapter coverage path；
- Aha origin Moment / peak Window 等 type-specific refs。

### 3.3 trust_basis

- upstream gate decision refs；
- S08 outcome、validated assertion 与 wrapper refs；
- limitation、contradiction 与 inference-risk refs；
- Evidence provenance。

不得重新制造 Candidate 总置信分，也不得把不同事实的支持度压成一个 overall confidence。

### 3.4 memory_value_basis

- Memory Value Gate reason 与 supporting refs；
- Episode coherence basis；
- Manual intent refs；
- distinct KEEP RawAsset count；
- non-redundant CandidateContentUnit count；
- Normal / Long-Manual path 与 validated exception refs。

Manual intent 与 truth/reliability 分开保存。主动拍摄支持个人相关性，但不提高事实真实性。

### 3.5 relation_inputs 与 provenance

- alternative/duplicate group refs；
- RawAsset、ContentUnit、时间、Episode 与 grounded semantic signature refs；
- prior user-visible Memory refs；
- upstream lineage hints；
- pipeline、schema、taxonomy、parameter、policy versions；
- deterministic build trace。

`distinctness / day_coverage_gain / redundancy_penalty / revision_stability / fifth_chapter_incremental_value` 都是 set-dependent 量，不能固化成 Candidate 自身分数。

SelectionRecord 禁止包含新 Observation、自由文本硬事实、hero/frame 选择、媒体格式或决定一切的总分。

## 4. Candidate Relation Graph

### 4.1 多边图

- 每条 SelectionRecord 是 node；
- Candidate pair 由有类型、有证据、有 selection effect 的 edge 连接；
- 同一 pair 可以同时存在多条 edge；
- edge 只约束当前集合，不删除或回写上游 Candidate。

### 4.2 关系类型

| relation | 含义 | selection effect |
|---|---|---|
| `IDENTITY_CONFLICT` | 同一 Candidate identity 被异常重复物化 | contract invalid |
| `CHAPTER_RAW_ASSET_CONFLICT` | 两个 Chapter 共享 underlying RawAsset | must not co-select |
| `EXCLUSIVE_ALTERNATIVE` | 同一局部问题的替代解释 | must not co-select |
| `SAME_MEMORY_REDUNDANCY` | 表达同一段 Memory | must not co-select |
| `NESTED_DOMINANCE` | A 包含 B 且 B 无独立新增意义 | must not co-select；记录 dominator |
| `PARTIAL_OVERLAP` | 共享部分内容且双方可能各有贡献 | allow with set-level redundancy cost |
| `EMBEDDED_DISTINCT_AHA` | Aha 位于 Chapter 内但表达独立 local event | allow co-select |
| `DISTINCT_EPISODE` | 时间/Episode 独立，即使语义相似 | allow co-select |
| `UNRESOLVED_POTENTIAL_CONFLICT` | 有冲突迹象但无法安全定类 | current Revision at most one |

优先级：

~~~text
contract invalid
→ hard must-not-co-select
→ unresolved at-most-one
→ partial-overlap cost
→ coexist allowed
~~~

### 4.3 CandidatePairLedger

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

账本必须同时保存“像同一 Memory”的证据和“是不同 Memory”的证据。没有 overlap evidence 不等于 distinct；没有 distinct evidence 也不等于 duplicate。

### 4.4 证据优先级

1. S07 alternative/duplicate/dominance refs 与 S08 `AlternativeResolution`；
2. Candidate identity、RawAsset、ContentUnit、peak 等 exact overlap；
3. Moment、Episode、capture interval、continuity/boundary、interruption；
4. grounded activity/progression/outcome、anonymous entity、Context Motif、EpisodeGroupSignature；
5. embedding、scene、object、style similarity。

第 5 级只能 nominate 关系，不能单独证明 same Memory、distinct Episode 或 hard conflict。

### 4.5 最低判定边界

- `SAME_MEMORY_REDUNDANCY` 至少需要结构关系 + grounded Memory basis；
- `NESTED_DOMINANCE` 还需证明被包含 Candidate 无 material independent contribution；
- `DISTINCT_EPISODE` 需要明确时间/Episode boundary 或不同 progression；
- Chapter–Chapter exact RawAsset overlap 直接 hard conflict；
- Chapter–Aha Evidence overlap 不自动 conflict；
- 同地点、同风格、同活动、高 embedding、时间接近均不能单独定案；
- overlap 与 distinct 证据都成立时优先 `PARTIAL_OVERLAP`，仍无法安全定类时用 `UNRESOLVED_POTENTIAL_CONFLICT`。

**案例：** 第一个片段是古镇石板路、第二个是古建筑、第三个又是石板路。只要 Episode、连续步行、Context Motif、人物和时间连续性支持，它们可以属于同一古镇 citywalk；不能只按画面对象拆开。

## 5. Executable Selection Constraints

| constraint | 含义 |
|---|---|
| `CONTRACT_BLOCKED` | identity、Revision 或引用合同错误；隔离受影响 record |
| `FORBID_COSELECT` | pair 或显式 group 最多选择一个 |
| `CONSERVATIVE_AT_MOST_ONE` | 关系未解决；当前 Revision 最多选择一个 |
| `ALLOW_WITH_REDUNDANCY_COST` | 可以共存，但计入集合冗余 |
| `ALLOW_COSELECT` | 当前关系不禁止共选 |

所有 at-most-one 都不是 exactly-one；两个 Candidate 可以都不选。

硬约束：

1. 同一 underlying RawAsset 的 Chapter selected count ≤ 1；
2. 显式 `EXCLUSIVE_ALTERNATIVE` group selected count ≤ 1；
3. `SAME_MEMORY_REDUNDANCY` pair selected count ≤ 1；
4. `NESTED_DOMINANCE` pair selected count ≤ 1；
5. `UNRESOLVED_POTENTIAL_CONFLICT` pair current-Revision selected count ≤ 1；
6. `PARTIAL_OVERLAP` 进入 redundancy/marginal comparison，不建立 hard ban；
7. `EMBEDDED_DISTINCT_AHA / DISTINCT_EPISODE` 不建立 co-selection ban。

Pair conflict 不传递：

~~~text
A conflicts B
B conflicts C
A does not conflict C
→ {A, C} remains legal
~~~

只有显式 group identity/cardinality 或明确共享资源 group 才能建立 group-level constraint，不能把普通 connected component 自动压成“整组最多一个”。

## 6. Set-level Editorial Objective

S09 使用 lexicographic / ordered objective，不把全部因素压成 overall score。只有前一层相同或达到 policy-defined equivalence，才比较下一层。

### 6.1 八层顺序

1. **Legality 与 Trust**：只比较满足 eligibility、contract 与 co-selection constraints 的合法集合；
2. **Material Marginal Memory Contribution**：移除每个成员都会真实失去一个独立经历、进展、结果、转折或高光；
3. **Meaningful Episode Coverage**：覆盖更多值得成为 Memory 的独立强 Episode，不以素材数量或时长代替；
4. **Trusted Independent Memory Value**：优先 Evidence 更可靠、过程更完整、结果更清楚、推断风险更低的集合；
5. **Set-level Redundancy 与 Inference Risk**：共同控制 Chapter–Chapter、Chapter–Aha、Aha–Aha 重复；
6. **Quality-qualified Count Preference**：丰富日偏好 3–4 Chapter、2–3 Aha；仅在前五层合格后生效；
7. **Revision Stability**：多个近似质量的合法 successor 方案中偏好 identity 更稳定、变化更小者；
8. **Parsimony 与 Determinism**：仍等价时偏好更精简集合，再用固定稳定键 tie-break。

数量偏好不能越过前五层；Revision stability 不能保护错误事实；deterministic tie-break 不能伪装成 Memory value。

### 6.2 Published retention 与 soft stability 不同

- published-Memory retention guard 是硬约束：仍有效的已发布 Memory 不能仅因后来 ranking 下降而消失；
- soft stability preference 只在多个合法 successor plan 近似等价时决定更稳定者。

### 6.3 参数边界

`material / strong / near-equivalent`、objective discretization 与各层阈值不在 V1.19 冻结数值。它们必须通过真实 labeled data、人工评分、用户反馈和离线评测显式校准；实现不得静默改变八层顺序或不可补偿边界。

**案例：** 当天只有重要会议和生日晚餐两个强 Episode，可以输出两个 Chapter；不能用普通通勤、买水补成四章。

## 7. Deterministic Constrained Set Search

### 7.1 Baseline

~~~text
construct Chapter skeletons
→ attach Ahas to every still-competitive skeleton
→ evaluate complete Chapter + Aha plans jointly
~~~

“先 Chapter、后 Aha”只是遍历顺序，不是先固定 Chapter winner。Aha compatibility、Chapter–Aha redundancy 与完整集合价值仍可改变最终选择。

搜索输入必须包括：

- SelectionRecord[]；
- B3 relation/constraint graph；
- C3 Phase-A prior/current lineage pair/group ledgers；
- protected-prior successor constraints。

同一 traversal 同时维护：

~~~text
best_chapter_day_plan
best_highlight_day_plan
empty_day_feasibility_proof
~~~

不能先生成一个 generic winner，再删除成员以满足 Day State。

### 7.2 搜索形状

~~~text
start Chapters = []
start Ahas = []
Chapter count <= 5
Aha count <= 3
~~~

空集合与低数量集合必须存在；数量目标不是配额。第五 Chapter 只有在 D2 gate 开放且 PASS 后具有最终资格。

### 7.3 Chapter skeleton 与 Aha attachment

按 policy-versioned deterministic order 对 Chapter 做 include/exclude branching；每次 include 立即检查：

1. current-Revision contract；
2. B3 hard/group/unresolved constraints；
3. protected-prior successor/group constraints；
4. type count cap；
5. 已可证明的无 material contribution；
6. sound upper bound。

对每个仍可能获胜的 Chapter skeleton，以相同方式接入 Aha，并同时检查 Aha–Aha、Chapter–Aha、partial overlap、unresolved guard、count cap 与 material contribution。

完整 plan 对每个成员执行 removal test；移除后没有实质 Memory 损失的成员不能留在 plan 中。

### 7.4 Safe pruning

只允许：

1. contract/hard constraint 已违反；
2. type count 超 cap；
3. 已证明成员无独立贡献且未来加入不能恢复；
4. sound optimistic upper bound 已证明分支无法在更高 objective tier 超过 incumbent。

Heuristic ordering 只能帮助尽早找到 incumbent，不是资格或价值判断。完整搜索时遍历顺序不得改变结果。

### 7.5 Search status

~~~text
EXACT_WITHIN_POLICY
  completed and optimal under current policy/objective discretization

BEST_LEGAL_WITH_SEARCH_LIMIT
  deterministic expanded-state budget reached
  best legal plan found; optimality_proven = false

SEARCH_OPERATIONAL_FAILURE
  non-policy operational abort
  not an editorial result
~~~

Primary budget 使用 deterministic `expanded_state_count`。Wall clock 只可作为 operational emergency stop，不能静默改变可发布结果。

### 7.6 理论容量

~~~text
60 Chapter hypotheses, subsets up to 5 = 5,985,198
62 Aha hypotheses, subsets up to 3       = 39,774
naive Cartesian plans                    = 238,055,265,252
122 Candidate pairs                      = 7,381
~~~

因此 V1.19 禁止 naive Cartesian enumeration，也禁止为省搜索而在上游做未经合同允许的 Top-K。Production solver/branch-and-bound 与 state budget 必须通过真实 selectable-pool 分布 benchmark。

S09 本身不新增模型或媒体理解成本；其主要成本是结构化 CPU/内存搜索与审计。

## 8. Cross-Revision Continuity 与 Stable Memory Identity

### 8.1 两种 ID

~~~text
stable_memory_id
  durable user-facing Memory identity across published Revisions

revision_memory_instance_id
  immutable representation in one Revision
~~~

同一 Memory 新 Revision 产生新 instance，但可继续使用 stable ID。旧 Revision 不得原地修改。

### 8.2 对照基线

只比较：

~~~text
last successfully published Memory Set
vs.
current Revision plan candidates
~~~

失败、未发布、内部试算或 stale Preview 不构成用户可见 lineage baseline。

### 8.3 两阶段 lineage

~~~text
Phase A — before C2 winner
  last published Memories × all current SelectionRecords
  → pair/group compatibility ledgers
  → protected-prior successor constraints
  → feed C2

Phase B — after state-conditioned plan chosen
  selected entries + Phase-A ledgers
  → final lineage decisions
  → stable-ID actions
~~~

N→1 merge 与 1→N split 必须使用 `CrossRevisionLineageGroupLedger`，不能由互不知情的 pair decision 拼接。

### 8.4 Lineage decisions

| decision | stable-ID rule |
|---|---|
| `CONTINUES` | 同一核心，保留 stable ID，新 instance |
| `EXPANDS` | 同一 Episode 增加阶段/结果，保留 stable ID |
| `MERGES` | primary core 明确则继承其 ID；否则新 ID，parents `merged_into` |
| `SPLITS` | primary child 明确则继承旧 ID；否则 children 新 ID，旧 ID `split_into[]` |
| `SUPERSEDES` | 核心解释改变，使用新 ID并保存 replacement relation |
| `NEW_INDEPENDENT` | 新 Episode/peak，分配新 stable ID |

一个旧 stable ID 不能同时分给多个 split child。不能按发布时间或 ID 顺序猜 primary core。

### 8.5 Chapter/Aha 类型迁移

同一 Memory 从 Aha 扩充为完整 Chapter 可以保留 stable ID，记录 `AHA_TO_CHAPTER`；原 Aha 不再重复占位。

`CHAPTER_TO_AHA` 只允许由错误分段、Evidence 失效等已允许原因触发，不能因数量压力或普通 ranking 下滑发生。

### 8.6 Published-Memory retention guard

Prior Memory 若仍满足：

1. 核心事实与 Evidence 有效；
2. Episode/peak identity 未被推翻；
3. 未被证明 duplicate；
4. 存在合法 current successor；

则 winning plan 必须覆盖一个合法 successor。后来出现更高 ranking Candidate 不是 eviction reason。

允许撤回、合并或降级的 reason class 仅为：

~~~text
PROVEN_DUPLICATE
FACT_INVALIDATED
SEGMENTATION_CORRECTED
EVIDENCE_INVALIDATED
~~~

若仍有效的 prior Memory 因 cap、合同错误或 successor 缺失而消失，输出 `LINEAGE_CONTRACT_BLOCKED`，不能伪装成质量下降或 EMPTY_DAY。

### 8.7 Ambiguous lineage 与 NO_CHANGE

`LINEAGE_UNRESOLVED` 时不随机继承 ID、不静默撤回 prior，当前 plan 只能内部保存，不能伪装成 lineage-ready Revision。

若 stable identity、scope、type、state、lifecycle 均无实质变化，输出 `NO_CHANGE`；可保存 audit，但不制造无用户价值的新发布 Revision。

## 9. Day State Proposal

S09 只提出三个内容状态：

~~~text
CHAPTER_DAY
HIGHLIGHT_DAY
EMPTY_DAY
~~~

`DAY_STATE_NOT_PROPOSED` 是本次 Revision 无资格提出状态，不是第四种 Day State。`NO_CHANGE` 是 editorial action，不是 Day State。

### 9.1 判定前置条件

进入状态判断前必须确认：

1. current Revision/snapshot 与 refs 合法；
2. search 已完成，或 limitation 足以证明所提非空状态；
3. 没有会隐藏潜在有效 Memory 的 contract failure；
4. prior retention/lineage READY；
5. 所有 excluded unresolved/operational Candidate 已做 uncertainty impact assessment；
6. 没有把 network/provider/budget/timeout 当成内容不足。

不能满足时：

~~~text
DAY_STATE_NOT_PROPOSED
blocker_class
preserve_last_published_revision
~~~

### 9.2 固定判定顺序

~~~text
revision is state-decidable?
├─ no  → DAY_STATE_NOT_PROPOSED
└─ yes
   ├─ any legal Chapter plan?
   │  └─ yes → CHAPTER_DAY
   └─ no
      ├─ any Aha passes standalone gate?
      │  └─ yes → HIGHLIGHT_DAY with exactly 1 Aha
      └─ no
         ├─ complete proof of no publishable Memory?
         │  └─ yes → EMPTY_DAY
         └─ no  → DAY_STATE_NOT_PROPOSED
~~~

Chapter state 优先是产品状态机语义，不允许让 Aha-only plan 与合法 Chapter plan 按戏剧性竞争。

### 9.3 CHAPTER_DAY

~~~text
1–5 Chapters
0–3 Ahas
~~~

每个成员必须满足 eligibility、constraints、marginal contribution、lineage 与 count policy。第五 Chapter 还必须通过 Section 10 exceptional gate。

### 9.4 HIGHLIGHT_DAY

只在不存在合法 Chapter plan 时检查：

~~~text
0 Chapter
exactly 1 strong standalone Aha
~~~

Standalone Aha 必须：

1. S07 Local Peak Gate PASS；
2. S07 Independent Memory Value Gate PASS；
3. 必要 S08 validation PASS；
4. 不依赖未入选 Chapter 才能理解；
5. grounded Evidence 足以支持具体 local event；
6. 无实质 contradiction 或高 inference risk；
7. 不与 prior published Memory 重复；
8. relation/lineage 合法。

多个 Aha 均通过时先执行 retention：valid prior HIGHLIGHT Aha 的合法 successor 必须保留，新 Aha 不能仅因更精彩替换它。其他未选项记录：

~~~text
HIGHLIGHT_DAY_SINGLE_AHA_LIMIT
HIGHLIGHT_DAY_SINGLE_AHA_LIMIT_VALID_PRIOR_RETAINED
~~~

### 9.5 EMPTY_DAY

~~~text
0 Chapter
0 Aha
~~~

EMPTY 表示在允许且成功处理的 Evidence 中没有安全可发布 Memory，不表示用户客观上什么都没做。

允许 reason：

~~~text
NO_ELIGIBLE_MEMORY_CANDIDATE
NO_INDEPENDENT_MEMORY_VALUE
INSUFFICIENT_EVIDENCE_AFTER_ALLOWED_PROCESSING
ALL_CONTENT_OUTPUT_INACTIVE
~~~

Network/provider/budget/search/contract failure、lineage unresolved、prior successor 程序性缺失或未探索分支可能包含合法非空 plan 时，均不能输出 EMPTY。

`BEST_LEGAL_WITH_SEARCH_LIMIT` 且 best-found 为空时不能建立 empty proof。只有 exact search 或等价完整 infeasibility proof 可以。

### 9.6 Excluded uncertainty impact

~~~text
EVIDENCE_LIMITED_PRECISION_EXCLUSION
POLICY_OR_OPERATION_RECALL_ONLY
STATE_OR_RETENTION_CRITICAL
NON_IMPACTING_PROVEN
~~~

- Evidence 已用尽后仍 inconclusive，可 precision-first 排除；
- recall-only 可能漏掉额外内容，但不影响当前非空 plan、Day State 或 prior retention，可带 limitation 继续；
- state/retention-critical 可能改变 empty/non-empty、HIGHLIGHT/CHAPTER 或 prior successor，必须 HOLD/BLOCK；
- non-impacting 必须有证明。

**案例：** 已有 direct ELIGIBLE 的学校表演 Chapter，额外颁奖 Aha provider failed，可带 recall limitation 继续；若失败 Candidate 是全天唯一潜在 Memory，则不能输出 EMPTY。

## 10. Preview、Final 与第五 Chapter

### 10.1 Count policy

~~~text
Preview CHAPTER_DAY
  Chapters <= 4
  Ahas <= 2
  fifth gate = CLOSED

Final CHAPTER_DAY
  ordinary Chapters <= 4
  Ahas <= 3
  fifth Chapter only after exceptional gate PASS
~~~

这些是发布容量，不是 Candidate Top-K。超过 Preview 容量的合法 Candidate 保留到后续 Revision/Final，不改为 rejected 或 suppressed。

### 10.2 第五章是 set-level gate

分别求：

~~~text
P4 = best legal plan with 1–4 Chapters
P5 = legal plan with exactly 5 Chapters
~~~

对每个 P5 依次删除每个 Chapter，并重新优化剩余 Aha；删除后损失最小者是 weakest marginal Chapter。并列者全部进入 marginal set。

五章 plan 必须全部通过：

1. Normal Chapter Gate；
2. Distinct Complete Episode Gate；
3. Non-mergeable Gate；
4. Important Day Omission Gate；
5. Chapter-scale Gate；
6. Redundancy/Risk Gate；
7. Set Increment Gate。

~~~text
P5 legal
+ every member passes normal gates
+ weakest marginal passes all exceptional gates
+ P5 materially improves higher-tier coverage/value over best <=4
+ no member can be merged or represented as Aha
→ FIFTH_CHAPTER_PASS

otherwise
→ FIFTH_CHAPTER_FAIL
→ use best legal <=4 plan
~~~

无法可靠证明时第五章默认 FAIL。普通 Preview 不评估第五章；Final 或合法 post-Final late-data Revision 才评估。

### 10.3 Preview reserve 与 retention

超过容量的合法 Candidate：

- 保留 disposition 与 audit；
- 下一 Revision/Final 重新参加 full-day selection；
- 当前使用 `DEFERRED_BY_PREVIEW_CHAPTER_RESERVE / DEFERRED_BY_PREVIEW_AHA_RESERVE`。

四个已发布且仍有效的 Preview Chapter 不能被后来更高 ranking Candidate 普通替换。只有已允许 invalidation/correction、合法 merge 或 type transition 才能释放位置。

### 10.4 Preview split-correction overflow

~~~text
pure SEGMENTATION_CORRECTED
+ prior Preview has 4 Chapters
+ corrected current count becomes 5
+ Preview fifth gate CLOSED
→ do not publish partial corrected four
→ do not hide/reject a child
→ do not fake merge
→ HOLD_PREVIOUS_REVISION
→ PREVIEW_SPLIT_CORRECTION_DEFERRED_TO_FINAL
~~~

Corrected plan、split lineage、children 与 Evidence 留在内部 audit；Final 对 corrected P4/P5 完整决策。

此 hold 只适用于事实仍成立、Episode grouping 需要拆分的纯 segmentation correction。若 prior 含 `FACT_INVALIDATED / EVIDENCE_INVALIDATED`，不得继续展示已知错误内容。

### 10.5 Final 第六 Episode

全天硬上限为 5 Chapter。五个 prior Chapter 均仍有效而 Late Data 新增第六 Episode 时：

- 不输出六章；
- 不按普通 ranking 驱逐 valid prior；
- 新 Episode 保留在 facts/Candidate/audit，但不进入 Diary；
- reason = `DAY_CHAPTER_CAP_REACHED_VALID_PRIOR_RETAINED`。

## 11. Output Contract

### 11.1 S09ResultBundle

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

`run_identity` 至少绑定 `user_local_day / daily_memory_run_id / revision_id / snapshot_id / selection_attempt_id`。Bundle immutable；re-selection 产生新 attempt，不能改写旧结果。

### 11.2 SelectedMemorySet

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

Entry 只保存引用与 S09 决策，不复制事实、不选择 Frame、不决定媒体格式。

### 11.3 Canonical output order

Membership 与 ordering 是两个独立步骤。C1/C2 先确定成员；成员、Day State 与 lineage 确定后才计算 output order。输出位置不能决定候选胜负、数量、第五章、retention 或 exclusion reason。

Chapter 在 `selected_chapters[]` 内排序：

1. selected KEEP content 最早 `capture_start` 升序；
2. 相同时，selected KEEP content 最晚 `capture_end` 升序；
3. 再相同时，`stable_memory_id` 升序；未分配时用 `stable_id_allocation_key`。

Aha 在 `selected_ahas[]` 内排序：

1. grounded `peak_capture_time` 升序；
2. 相同时用 stable ID / allocation key。

Resumed Chapter 使用 selected content 最早开始时间。Chapter 与 Aha 分类型排序，不建立跨类型价值榜。Embedded Aha 仍留在 Aha 数组。

排序输入缺失属于 contract invalid；不得退回输入数组、模型分数或数据库返回顺序。S10 仍独立决定一个 Chapter 内的 EvidenceAnchor 与媒体叙事顺序。

**案例：** 09:00 古镇、14:00 陶艺、20:00 生日三个 Chapter，即使生日价值最高，输出仍为古镇→陶艺→生日。

### 11.4 S10HandoffEnvelope

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
  hq_source_handle_status =
    AVAILABLE | NOT_YET_MATERIALIZED | UNAVAILABLE | UNKNOWN
  forbidden_scope_reason_refs[]
~~~

- KEEP 可进入 S10 anchor shortlist；
- CONTEXT_ONLY 只帮助理解，`anchor_eligible=false`；
- DROP 禁止进入；
- S10 不得重新搜索全天、扩大 scope 或用漂亮媒体改变 Memory membership；
- S09 不要求 HQ source 在进入 S10 前已 materialize。

## 12. Downstream Readiness

S09 永不声明 `PUBLISH_READY`。最终发布资格只能由 S12 决定。

### 12.1 Readiness states

#### `READY_FOR_S10`

非空 plan 满足 current eligibility、constraints、marginal contribution、Day State/count、D2、lineage；search exact 或 membership/day state 已证明；无 outcome-changing error；无 state/retention-critical exclusion；S10 whitelist/provenance/status 完整。

#### `EMPTY_READY_FOR_S12`

EMPTY_DAY 有完整 empty proof 且无 operational blind spot；跳过 Memory media/narrative creation，进入 S12 empty validation。

#### `NO_CHANGE_REUSE`

Selection identity、scope、type、state、lineage 无实质变化。下游 fingerprint 相同时可复用 artifact；版本变化只重跑失效阶段，不改变 S09 membership。

#### `HOLD_PREVIOUS_REVISION`

普通 Preview 因 lineage、search、contract、state/retention-critical operational issue 或纯 split overflow 无法安全继续时，保持 last published Revision。Recall-only 本身不强制 HOLD。

#### `BLOCKED_NO_PUBLISHABLE_REVISION`

无 prior 可保持，或 Final 无法形成可靠下游输入。不得把旧 Preview 偷偷改名为 Final。

### 12.2 Search-limited readiness

`BEST_LEGAL_WITH_SEARCH_LIMIT` 默认 HOLD/BLOCK。只有同时证明：

~~~text
winning_membership_proven = true
day_state_proven = true
~~~

且证明覆盖 selected membership、Day State、第五章与 prior lineage，才可继续。找到一个合法 plan 不等于证明 winner。

### 12.3 Contract error impact

~~~text
NON_IMPACTING_PROVEN
POTENTIALLY_OUTCOME_CHANGING
~~~

只有前者可在完整留痕后继续；后者必须 HOLD/BLOCK。

### 12.4 Same-day policy compatibility

同一 `DailyMemoryRun` 原则上 pin 同一 pipeline/selection policy version。具体 pin/migration 属于 S00/工程集成。

Prior 与 current policy fingerprint 不同时，只有显式、versioned、可审计的 compatibility/migration result 能证明 eligibility、retention、lineage、Day State、count semantics 兼容，才可继续。

Prior valid Memory 若只因 policy 变化没有 successor，不能记为 duplicate、低价值、无边际贡献或正常 eviction。无法证明兼容时：

~~~text
Preview → HOLD_PREVIOUS_REVISION
Final/no prior → BLOCKED_NO_PUBLISHABLE_REVISION

POLICY_VERSION_COMPATIBILITY_UNPROVEN
POLICY_ONLY_PRIOR_DISAPPEARANCE
~~~

### 12.5 S10/S12 不得静默换 Memory

S10 遇到 `MEDIA_UNRESOLVED` 必须返回失败，不能换 Candidate、搜索未选素材、恢复 CONTEXT_ONLY/DROP 或用其他 Memory 媒体替代。

S12 可以拒绝媒体、Claim 或结果，但不能新增/替换 Chapter/Aha。Membership 变化必须显式重入 S09，产生新 selection attempt 并重新检查状态、数量、lineage 与 constraints。

“S10 失败后是否允许一次有界 S09 re-selection”留给 S10 专题；即使未来允许，也不能由 S10 直接换人。

### 12.6 SelectionExclusionAudit

每个 SelectionRecord 必须有最终去向。Reason 至少区分：

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
DAY_CHAPTER_CAP_REACHED_VALID_PRIOR_RETAINED
CONTRACT_QUARANTINED
NOT_IN_BEST_FOUND_PLAN_UNDER_SEARCH_LIMIT
~~~

只有 exact search 能使用 `LOWER_EXACT_SET_VALUE`。受限搜索不能声称未选 Candidate 已被证明全局更差。

## 13. 端到端边界

~~~text
CHAPTER_DAY / HIGHLIGHT_DAY + READY_FOR_S10
→ S10 → S11 → S12

EMPTY_DAY + EMPTY_READY_FOR_S12
→ skip Memory media/narrative
→ S12 validates empty state

NO_CHANGE_REUSE
→ reuse exact unchanged artifacts
  or rerun only version-invalidated downstream stages

HOLD_PREVIOUS_REVISION / BLOCKED_NO_PUBLISHABLE_REVISION
→ no normal publish path
~~~

S09 明确不做：

- Raw/Evidence re-read 或媒体上传；
- 删除 RawAsset、事实账本或独立 Manual 窗口中的原素材；相似 Manual 可以不进入 Memory，但原素材仍可由用户查看；
- Auto 补帧或完整 9s 回取；
- 新 VLM/strong-model/embedding 调用；
- Observation、Moment、Role、Candidate 重写；
- Frame、hero、EvidenceAnchor、媒体格式选择；
- Narrative、tag、情绪或 Claim 生成；
- Privacy/ethics/governance 决策；
- App、Firmware/SDK 或共享状态文件修改。

## 14. 典型合同案例

### 14.1 古镇—奶茶—古镇

A/C 有 continuity/context evidence 时可形成 resumed 古镇 Chapter；奶茶 B 是 interruption，不自动 split A/C。Broader A+B+C alternative 与 resumed A+C 不能同时选；街头表演若有独立 peak/result，可作为 embedded Aha 共存。

### 14.2 生日多个 local peak

Birthday Chapter 可与惊喜进入、突然合唱、礼物揭晓等不同 peak Aha 共存；Auto/Manual 两条都表达同一次吹蜡烛时只能保留一个 Memory。

### 14.3 普通办公日

长时间桌面、走廊、通勤与一张 Manual 咖啡照片都没有独立 Memory value，且处理完整无 operational blind spot，可得到 `EMPTY_DAY`。Manual 原素材仍保留在独立 Manual 窗口。

### 14.4 稀疏求婚

只有清晰求婚 peak，没有完整 Chapter progression 时，可得到 `HIGHLIGHT_DAY` exactly one Aha；重要性不能绕过 Chapter 完整性门。

### 14.5 五个强 Episode

热气球、陶艺、朋友重逢、求婚、灯会均为独立完整强 Episode，P5 weakest marginal 仍通过七道 gate，Final 可发布五章。把第五项改成普通出租车时必须 FAIL。

### 14.6 Rolling Preview split

Preview 已有四章，其中一章后被证明应 split 成两章。纯 segmentation correction 不发布 partial corrected four，也不开 Preview 第五章；保持 prior，Final 再决定 P4/P5。

## 15. 验证证据

V1.19 freeze review 已完成：

- 11 个设计小节 A1–D3 全部确认；
- 12 个高概率/高风险用户画像全部通过；
- B3 4 例 × 32 点 = 128；
- Full Selection 5 例 × 32 点 = 160；
- 合计 288 个两分钟语义时间点；
- R01–R09 覆盖 HIGHLIGHT retention、Aha→Chapter、split overflow、Final sixth、group lineage、operational blind spot、recall-only、HQ handle、canonical ordering；
- F1–F8 已修复；F12 的安全 HOLD/BLOCK 行为已写入；
- 未发现需要回退修改 S00–S08 冻结合同的问题。

## 16. 状态边界

### FROZEN

- 两条 selectable-pool 入池路径、单一 content identity 与 hard eligibility；
- SelectionRecord 六组字段与无 overall confidence；
- multi-edge relation graph、双向 Pair Ledger、关系证据优先级；
- 五种 executable constraint 与 non-transitive pair conflict；
- 八层 lexicographic set objective；
- state-conditioned deterministic constrained search、safe pruning、search status；
- Phase-A retention constraints + Phase-B lineage、stable/revision ID、group ledger；
- CHAPTER/HIGHLIGHT/EMPTY 固定判定顺序与 exact empty proof；
- uncertainty impact 四分类；
- Preview 4/2、Final normal 4/3、严格第五章与 hard cap 5；
- Preview pure split-correction hold；
- S09ResultBundle、SelectedMemorySet、S10 whitelist 与 readiness；
- deterministic chronological canonical order；
- policy incompatibility 的安全 HOLD/BLOCK；
- S10/S12 禁止静默替换 membership。

### OPEN / 待真实数据或工程

- Production reason enum/schema mapping；
- `material / strong / near-equivalent` 与 objective discretization；
- fifth importance 与各层真实阈值；
- solver/branch-and-bound、expanded-state budget 与 benchmark；
- S00 same-day policy pin 与 migration 实现；
- Selection service、persistent ledger、validator、telemetry 与 labeled-data calibration；
- S10 failure 后是否允许有界重入 S09；
- S10–S12 具体合同；
- 16s/73s 非标准 Manual Window。

OPEN 项只能通过真实数据、专项设计或新 Canonical Checkpoint 显式重开，不能由实现静默改变 V1.19。

### IMPLEMENTATION GAP

- X01 仍是一轮实验模型输出，不是分阶段 S09；
- 当前没有 Production SelectionRecord/Pair/Lineage/Plan schema；
- 当前没有 deterministic solver、state-budget benchmark 或 persistent selection audit；
- 当前没有真实用户标签证明 objective threshold 与 fifth gate 参数；
- V1.19 是算法架构冻结，不是 Production readiness。

## 17. 术语释义

| term | 简明含义 |
|---|---|
| Window | 时间轴上一小段素材/证据单位；S09 不重新抽 Window |
| embedding | 把画面语义变成可比较向量；在 S09 只能提供弱相似提示，不能独立决定合并/重复 |
| Candidate | S07/S08 交来的“可能成为 Memory”的内部假设，不是最终 Chapter/Aha |
| SelectionRecord | S09 为统一比较建立的候选选择卡 |
| Set | 当天准备共同发布的一整组 Chapter + Aha |
| marginal contribution | 删除一个成员后是否真实失去独立记忆内容 |
| lineage | 同一 Memory 跨 Preview/Final Revision 的继续、扩充、合并、拆分或替代关系 |
| incumbent | 搜索过程中当前已知最好的合法完整方案 |
| canonical order | 成员选定后用于稳定输出数组的确定性时间顺序，不是价值排名 |
| HOLD | 当前 Revision 不安全时保持上一成功发布版，不把失败伪装成新内容状态 |
