# Diary One Canonical Checkpoint V1.18 — S08 Targeted Enrichment & Evidence Validation

**状态：** FROZEN
**冻结日期：** 2026-08-26
**决策来源：** 用户确认 S08-A～C，并授权在无产品级阻塞时独立完成 S08-D～F；P01–P17 交叉检查未发现结构性 blocker
**作用范围：** S08 one-question task、允许问题、动作选择、证据范围、加权预算、缓存、重试、失败归因、Revision、输出与 S09 handoff
**继承关系：** 继承 V1.17–V1.1 与 V1.0 未被本文覆盖的规则
**验证依据：** [S08 Working V0.1](S08_TARGETED_ENRICHMENT_VALIDATION_CONSOLIDATED_WORKING_V0_1.md) 与 [S08 Cross-Check V0.1](S08_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_1.md)

> **当前下游覆盖：** [V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md) 已冻结 S09 selectable pool、relation/constraint、set objective/search、lineage、Day State、Preview/Final capacity、fifth gate、output/readiness。本文将 S09 Set Selection 继续列为 OPEN 的历史表述由 V1.19 覆盖；S08 合同继续有效。

## 1. 冻结结论

S08 只对 S07 已经声明的局部未知项做最低成本、最低暴露、可审计的定向验证。

~~~text
S07 PROVISIONAL_VALIDATION_REQUIRED Candidate
→ one-question ValidationTask
→ A0 exact cache
→ A1 structured validator
→ choose one cheapest capable bounded modality when needed
→ at most one capability escalation
→ independent S08 outcome
→ validated downstream eligibility only
→ S09 Editorial Set Selection
~~~

S08 不是：

- 第二次 S07 或全天素材重理解；
- Memory Value 生成器；
- S09 Top-K 或最终 3–4 Chapter / 2–3 Aha 选择器；
- S10 hero/精选媒体选择器；
- S11 Writer；
- S12 最终 Claim Validator；
- Auto 补帧、Raw 回取或上传合同扩张入口。

**案例：** “吹生日蜡烛”已经通过 S07 的独立价值门后，S08 只验证火焰是否真的熄灭；它不能重新决定生日是否值得记录，也不能顺便写故事。

## 2. One-question ValidationTask

每个 ValidationTask 只能回答：

- 一个 question type；
- 一个 normalized proposition；
- 一个 target gate；
- 一组明确 PASS/FAIL mapping。

一个 Candidate 的必要 ValidationTask 最多为 2。超过 2 表示 Candidate 需要重新理解，而不是局部补证；当前 handoff 为 CONTRACT_INVALID。

Alternative 的 shared task 可以引用两个 Candidate member，但仍只回答一个 pairwise relation/dominance proposition。

**案例：** “A/C 是否恢复同一古镇 outing”和“奶茶店 B 是否增加实质内容”必须是两个任务，不能合并成“请总结这次古镇游玩”。

## 3. 双轴结果

### 3.1 ExecutionStatus

~~~text
COMPLETED
NOT_RUN_BUDGET
NOT_RUN_POLICY
PROVIDER_FAILED
CONTRACT_INVALID
~~~

- COMPLETED：得到合法的确定性或模型结果；
- NOT_RUN_BUDGET：VBU、真实费用或月度 headroom 不允许启动；
- NOT_RUN_POLICY：数据许可、speech gate、provider data policy 或 exposure policy 不允许启动；
- PROVIDER_FAILED：允许的同级 provider 尝试用尽；
- CONTRACT_INVALID：输入、引用、问题、范围或输出合同非法。

### 3.2 EvidenceDecision

~~~text
PASS
FAIL
INCONCLUSIVE
NOT_EVALUATED
~~~

组合不变量：

| ExecutionStatus | EvidenceDecision |
|---|---|
| COMPLETED | PASS / FAIL / INCONCLUSIVE |
| NOT_RUN_BUDGET | NOT_EVALUATED |
| NOT_RUN_POLICY | NOT_EVALUATED |
| PROVIDER_FAILED | NOT_EVALUATED |
| CONTRACT_INVALID | NOT_EVALUATED |

只有 COMPLETED + FAIL 可以表示证据否定。Budget、policy、provider 和 contract 问题不能伪装成内容失败。

**案例：** 音频许可未通过时结果为 NOT_RUN_POLICY + NOT_EVALUATED，而不是“孩子没有说出妈妈”。

## 4. S08 admission

只有 S07 disposition 为 PROVISIONAL_VALIDATION_REQUIRED 的 Candidate 可以申请 S08，并且：

- 已通过 S07 Memory Value；
- 具有明确、允许范围内可解决的 ValidationQuestion；
- 没有更可靠、等价且已 ELIGIBLE 的 Candidate；
- 验证结果能改变下游 eligibility 或解决 local alternative；
- 不违反 upload/no-refetch/data policy；
- 输入 Revision/snapshot immutable 且所有引用合法。

ELIGIBLE、REJECTED、SUPPRESSED_DUPLICATE 不进入 S08。

Preview frontier ≤3 Candidate，Final frontier ≤8 Candidate 的 V1.17 count guardrail 继续有效，但不代替 V1.18 action budget。

**案例：** 已经 ELIGIBLE 的通勤 Chapter 不能为了“更保险”占用 S08；一个没有具体未知项的 provisional 也不能用开放式 Prompt 偷渡。

## 5. 四类允许问题

### 5.1 LOCAL_PEAK_CONFIRMATION

只确认一个 origin Moment、一个 KEEP peak、最多 3 个连续 eligible Windows / 3 分钟内的具体变化、动作或局部事实。

**案例：** 确认火焰是否从点燃变为熄灭。

### 5.2 EPISODE_RELATION_CONFIRMATION

只使用 Candidate content members、interruption/context refs 与既有 Continuity/Boundary ledgers，确认一个局部 Episode relation。不得全日搜索或重写 S05 seam。

**案例：** 古镇 A、奶茶店 B、古镇 C 中，确认 A/C 是否属于同一 outing 的恢复。

### 5.3 MEDIA_DIVERSITY_CONFIRMATION

只确认 Long-Manual 指定 Windows 是否具有真实的时间和语义差异，不评价构图、美感或最终媒体。

**案例：** 120 秒表演视频中的准备、演奏、鼓掌是否真是三个不同内容位置。

### 5.4 ALTERNATIVE_RESOLUTION

只处理 local alternative group 中一个预声明的 pairwise relation/dominance question。

标准化 resolution：

~~~text
MEMBER_A_DOMINATES
MEMBER_B_DOMINATES
BOTH_DISTINCT
UNRESOLVED
~~~

pass_mapping 与 fail_mapping 必须逐 member 声明 Candidate outcome。

**案例：** 验证“古镇 + 奶茶 + 寺庙”是否比“古镇步行”增加了实质内容，而不是评选全天最佳 Chapter。

## 6. Evidence boundary

- KEEP 可以支持事实；
- CONTEXT_ONLY 只限制解释或表达 interruption；
- DROP 只保留在 audit/provenance；
- 所有媒体输入必须在 task allowlist；
- 证据不足返回 INCONCLUSIVE；
- 不追加 Raw、Auto frame 或全天检索；
- Aha origin/peak/interval 不得扩大；
- validation finding 独立保存，不改写 S04 fact；
- S08 不修改 S05 Moment、S06 role 或 S07 Candidate disposition。

**案例：** CONTEXT_ONLY 的奶茶店可以说明古镇路线被室内活动打断，但不能因此成为 Chapter 的精选内容单元。

## 7. 最低充分能力选择树

### A0｜EXACT_VALIDATION_CACHE

完全相同的 task、Evidence、action 与语义版本可以复用合法 payload，模型调用为 0。

**案例：** Preview 与 Final 内容完全相同，只建立 Final wrapper，不再次发送三张帧。

### A1｜STRUCTURED_EVIDENCE_CHECK

使用时间、grounded facts、duplicate group、content unit 与双向 ledgers 执行 question-specific deterministic Validator。

A1 不重新运行 S07。

**案例：** 三个 Long-Manual Window 已有不同时间、不同事实且不重复时，MEDIA_DIVERSITY 可直接 PASS。

### A2-V｜TARGETED_LIGHTWEIGHT_VISION

最多使用 3 张已有 Evidence frame，只问一个封闭视觉问题。

**案例：** 三帧只用于判断蜡烛火焰状态变化。

### A2-T｜EXISTING_TEMPORAL_PROXY

仅在动作顺序是必要证据、静态帧不足且已有允许的低分辨率 proxy 时使用。最多 2 个局部 excerpt，总时长不超过 6 秒；S08 不从 Raw 新生成 proxy。

**案例：** 已有 2 秒 proxy 用于判断球是接住还是扔出。

### A2-A｜GATED_AUDIO_OR_ASR

只有声音是 Candidate 成立的必要事实，并且 speech/data gate 通过时使用。最多一个已经允许的 audio excerpt，不超过 15 秒；不得回取完整 Manual Raw 临时切音频。

**案例：** 确认孩子是否真的说出“妈妈”；不能为了写普通 Chapter 文案而运行 ASR。

### A3｜BOUNDED_STRONG_MODEL

只有较低能力正常完成但出现允许的 semantic inability、结果会改变 eligibility、预算仍允许时启动。A3 使用相同或更小 payload，不增加 Evidence。

**案例：** 强模型可以在同三张古镇路牌帧内理解别名关系，但不能查看全天照片。

### STOP

源证据缺失、遮挡、无允许模态、政策范围限制或最强动作仍无法判断时停止。

**案例：** 吹蜡烛关键瞬间完全被遮挡，Candidate 保持不确定并退出当前 S09。

## 8. 能力升级

所有任务共同起点只有 A0→A1。之后选择一个最低充分分支，而不是依次运行 A2-V、A2-T、A2-A。

每个 Task 最多两个 paid capability step；A3 必须是最后一步。

可以升级：

~~~text
CAPABILITY_LIMIT
MODALITY_MISMATCH_WITHIN_ALLOWED_SCOPE
~~~

必须停止：

~~~text
SOURCE_EVIDENCE_ABSENT_OR_OCCLUDED
POLICY_SCOPE_LIMIT
NO_ALLOWED_MODALITY
CONTRADICTION_NOT_RESOLVABLE
~~~

Provider failure 和 invalid output 只能同级 retry/fallback，不允许借机升级 A3。

**案例：** 模型看见路牌但不能理解两个名称的关系，可以升级；画面根本没有路牌，不能升级。

## 9. Exposure envelope

| Action | 最大媒体范围 | 暴露等级 |
|---|---|---|
| A0/A1 | 无新增第三方媒体 | E0 |
| A2-V | ≤3 张现有 frame | E1 |
| A2-T | ≤2 个已有 proxy excerpt、总计 ≤6 秒 | E2 |
| A2-A | 1 个已有 audio excerpt、≤15 秒 | E2-AUDIO |
| A3 | 与前一步相同或更小 | 保持原等级并另记 strong exposure |

跨 provider fallback 只有在数据政策等价或更严格、且 payload 获得授权时允许。

**案例：** 轻量供应商故障后可以切换同级、同政策 provider，但不能附带发送完整视频。

## 10. VBU 加权预算

### 10.1 action weight

1 VBU 是一次 bounded A2-V light attempt 的相对规划重量，不等于固定美元或 Token。

| Action attempt | minimum VBU |
|---|---:|
| A0 | 0 |
| A1 | 0 |
| A2-V | 1 |
| A2-A | 1 |
| A2-T | 2 |
| A3 | 4 |

实际 reservation：

~~~text
reserved_vbu =
max(
  action_min_vbu,
  ceil(projected_action_cost / versioned_reference_light_call_cost)
)
~~~

无可信价格或保守上界时不得 dispatch，记录 NOT_RUN_BUDGET / PRICE_UNAVAILABLE。

**案例：** temporal provider 的预计费用若相当于 3 个 reference light call，必须预留 3 VBU，而不是静态表中的 2。

### 10.2 V1.18 versioned limits

| Scope | Limit |
|---|---:|
| Necessary ValidationTask / Candidate | 2 |
| Paid capability step / Task | 2 |
| Provider attempt / capability step | ≤2，且第二次仍须通过所有预算与政策门 |
| Reserved + consumed dispatch VBU / Task | 6 |
| Reserved + consumed dispatch VBU / Candidate | 8 |
| All Preview Revisions combined / diary day | 4 |
| All S08 Revisions combined / diary day | 16 |
| Task entering A3 / diary day | 2 |

Preview 4 VBU 是全日累计池，不因 App 打开或 Revision 数量重置。Final 使用当天剩余预算；无 Preview 时最多使用完整 16 VBU。

**案例：** 用户一天打开 App 四次，同一问题缓存复用为 0；所有 Preview 的新 paid dispatch 合计仍不能超过 4 VBU。

### 10.3 atomic minimum reservation

多任务 Candidate 启动第一个 paid action 前，必须能同时预留所有必要任务最便宜可用首步的 VBU。强模型升级在实际升级前重新 reservation。

**案例：** 两个任务最低各 1 VBU、当前只剩 1 时，两个都不启动，避免完成一半仍无法建立 eligibility。

### 10.4 actual money

每次 dispatch 还必须记录并服从：

- provider 原币价格、换算版本、预计/实际美元；
- Validation、ASR、Strong escalation、Retry waste 分账；
- cohort average ≤US$1.50/user/month；
- engineering target 约 US$0.90；
- internal warning 约 US$1.20。

S08 的真实月度份额与 reference-light 单价保持 versioned configuration，等待 Benchmark，不在架构中伪造固定百分比。

达到预警预测后：

1. A0/A1 继续；
2. 停止新 Preview paid action 与新 A3；
3. Final 只运行最高 decision-yield 的最低 A2；
4. 无总体 headroom 时 paid task 为 NOT_RUN_BUDGET；
5. 预算状态不改变 Evidence truth。

**案例：** 月度预测到 US$1.20 时，古镇 Preview 不启动强模型；Final 可优先运行一个 1 VBU、能解决两个 alternative 的 shared task。

## 11. Budget scheduler

1. 对 frontier 内合法任务先运行 A0/A1；
2. 已 PASS/FAIL/terminal INCONCLUSIVE 不再付费；
3. 为剩余 Candidate 建立 atomic minimum reservation bundle；
4. 按 decision yield 排序；
5. dispatch 前再次检查 revision、budget、exposure 与 provider policy；
6. 任一 cap 到达即停止并留痕。

排序 Baseline：

~~~text
shared_candidate_count_resolved DESC
mandatory_gate_count_resolved DESC
minimum_reserved_vbu ASC
stable_task_fingerprint ASC
~~~

decision yield 只计算可解决 gate/member 数，不评价 Memory 的感人程度，不替代 S09。

**案例：** 一个 1 VBU shared task 能解决两个 alternative，先于一个 2 VBU 单 Candidate task；这不代表它最终一定被选入 Diary。

## 12. Exact cache 与幂等

### 12.1 semantic fingerprint

至少包含：

- question type、normalized proposition、target gate；
- PASS/FAIL mapping；
- candidate content fingerprint；
- ordered Evidence hashes、offsets、roles；
- allowed modality/time scope 与 disallowed source；
- rule/taxonomy/policy versions。

### 12.2 action execution fingerprint

另外包含：

- action 与实际 input hashes；
- preprocessing version；
- provider capability tier；
- model/prompt/parameter/schema versions；
- exposure-policy version。

价格配置只影响当前 reservation/trace，不进入语义 cache identity。

candidate_instance_id/revision_id 不作为跨 Revision payload identity；当前 Revision 必须重新验证 eligibility，并创建自己的 wrapper。

合法 COMPLETED 的 PASS/FAIL/INCONCLUSIVE 可以 exact-cache；provider failure 不能作为语义结果缓存；near-duplicate 不能复用。

**案例：** 两段石板路虽然相似，但 hash、时间和 Candidate relation 不同，不能复制旧的“路线恢复”结论。

### 12.3 idempotency

~~~text
idempotency_key =
task_id + action_execution_fingerprint + capability_step_index + attempt_index
~~~

at-least-once 队列重复投递先读取已提交 attempt，不产生第二笔调用。

**案例：** Worker 写入成功后断线，重复任务只能返回原 attempt，不能再次发送家庭照片。

## 13. Retry、fallback 与 semantic inability

### Provider failure

- 每 capability step 最多 2 次 provider attempt；
- 第二次可 same-provider retry 或 same-tier fallback；
- 必须重新通过所有 VBU、美元、policy 与 exposure cap；
- 每次 dispatch 计费、计 exposure、计 retry waste；
- 尝试用尽为 PROVIDER_FAILED + NOT_EVALUATED；
- 不允许 A3。

### Invalid output

- 未知 Evidence ID、越权引用、schema 无法解析均无效；
- 预算允许时可同级重试一次；
- 再次无效为 CONTRACT_INVALID + NOT_EVALUATED；
- 不接受自由文本，不升级强模型。

### Semantic inability

- 模型正常完成且输出合法，却无法区分，才可能升级；
- 只允许一次 capability escalation；
- 不进行同级多数投票；
- A3 后仍不确定为 COMPLETED + INCONCLUSIVE。

**案例：** Provider 超时只能同级 fallback；模型正常看图但无法理解古镇别名关系，才可能升级 A3。

## 14. Candidate short-circuit

- 任一必要 task FAIL，Candidate 为 REJECTED_BY_EVIDENCE；
- terminal INCONCLUSIVE 或 operational failure 后，其余未启动 paid task 停止；
- free A0/A1 可以预先运行并缓存；
- 未启动 task 只记录 plan disposition = SHORT_CIRCUITED_NO_ELIGIBILITY，不伪造 outcome。

**案例：** Long-Manual media diversity 已 FAIL 后，不再花钱验证该 Candidate 与另一个 Chapter 的 dominance。

## 15. Revision 与 stale result

- Task 只属于一个 immutable Revision/snapshot；
- dispatch 前再次检查 current applicability；
- Late Data 创建新 Revision；
- 旧结果保留原状态并标 STALE_FOR_CURRENT_DOWNSTREAM；
- stale outcome 不直接进入当前 S09；
- 新 Revision 只能 exact-cache payload，并建立新 wrapper；
- spend/exposure 记在实际发生的原 Revision/day；
- S08 不回写 S07。

**案例：** Preview R2 在 Final R3 后才返回 PASS。R2 结果保留；R3 只有完全相同 fingerprint 才能复用，并且必须生成 R3 outcome。

## 16. 输出合同

S08 至少输出：

~~~text
ValidationPlan
ValidationTask[]
ValidationAttempt[]
ValidationTaskOutcome[]
CandidateValidationOutcome[]
ValidatedCandidate[]
AlternativeResolution[]
S08RunTrace
~~~

### ValidationPlan

包含 Revision/snapshot、policy versions、frontier refs、task、schedule、budget snapshot/reservation 与 plan disposition。

### ValidationTask

包含 Candidate refs、question/target/proposition、support、allowlist/disallowlist、PASS/FAIL mapping、minimum route、fingerprint 与 versions。

### ValidationAttempt

包含 idempotency、action/provider/model、input hashes、exposure、latency/failure、Token/cost/VBU、cache provenance 与 structured payload。

### ValidationTaskOutcome

包含 execution status、evidence decision、reason、validated assertion、support/contradiction refs、action/attempts 与 revision applicability。

validated assertion 只能回答 proposition。

### CandidateValidationOutcome

~~~text
VALIDATED_FOR_S09
REJECTED_BY_EVIDENCE
UNRESOLVED_EVIDENCE
UNVALIDATED_OPERATIONAL
STALE_FOR_CURRENT_REVISION
~~~

聚合：

1. 任一必要 task FAIL → REJECTED_BY_EVIDENCE；
2. 所有必要 task PASS → VALIDATED_FOR_S09；
3. 无 FAIL但有 INCONCLUSIVE → UNRESOLVED_EVIDENCE；
4. 无 FAIL但有 budget/policy/provider/contract failure → UNVALIDATED_OPERATIONAL；
5. Revision 不适用 → STALE_FOR_CURRENT_REVISION。

### ValidatedCandidate

只在所有必要 task PASS 时生成。它引用原 S07 Candidate、task outcomes 与 findings，并声明：

~~~text
downstream_eligibility = ELIGIBLE_FOR_S09
content_identity_unchanged = true
~~~

### AlternativeResolution

保存 group/member refs、标准化 resolution、supporting outcomes、Revision 与 S09 constraints；不删除或改写 Candidate。

### S08RunTrace

记录 question/action/status count、cache、retry、escalation、VBU、Token、费用、媒体暴露、budget/cap/short-circuit、latency 与 stale。

**案例：** 5 个验证中 3 个 A1 零调用、1 个 A2-V、1 个预算未运行时，Trace 必须逐项显示，不能只写“验证了 5 个”。

## 17. S09 handoff

~~~text
S09 selectable pool
= S07 ELIGIBLE Candidates
+ S08 ValidatedCandidates
~~~

同时附带 AlternativeResolution 与全部 rejected/unresolved/operational/stale audit。

UNRESOLVED、UNVALIDATED_OPERATIONAL、STALE 不能为了凑全天数量进入 S09。

**案例：** 当天只有两个明确 Aha 时，一个遮挡严重的第三 Aha 仍不能被拿来补足 3 个。

## 18. Validator 不变量

提交 S08 输出前至少验证：

1. 只接收同一 Revision/snapshot 的合法 S07 provisional；
2. 每 Task 一个 question/proposition/target；
3. 每 Candidate ≤2 必要 Task；
4. 只使用四类问题；
5. KEEP/CONTEXT_ONLY/DROP 无越界；
6. Evidence 只来自 allowlist；
7. 无 Auto refetch、默认 Raw、全天搜索；
8. A2-V ≤3 frame；
9. A2-T 使用已有 proxy，≤2 excerpt / ≤6s；
10. A2-A 通过 gate，使用已有 audio / ≤15s；
11. A3 不扩张 payload；
12. provider/output failure 不升级 A3；
13. 只有允许 semantic inability 升级；
14. paid steps、attempts、task/candidate/Preview/day/A3 cap 合法；
15. 每次 dispatch 前完成 VBU、美元与 exposure reservation；
16. retry waste 完整记录；
17. cache fingerprint 精确且不因价格变化误失效；
18. 跨 Revision reuse 建新 wrapper；
19. ExecutionStatus/EvidenceDecision 组合合法；
20. operational state 没有变成 Evidence FAIL；
21. ValidatedCandidate 的所有必要 task PASS；
22. ValidatedCandidate 不改变原 content identity；
23. AlternativeResolution 不删除/修改 S07 Candidate；
24. stale 不进入当前 S09；
25. 无 Narrative、最终媒体、新 Candidate 或新 Memory Value；
26. same input/policy/version 可确定性重放。

## 19. 典型行为

### 19.1 清晰生日峰值

A2-V 使用三帧确认火焰熄灭，1 VBU，PASS，生成 ValidatedCandidate。

### 19.2 遮挡生日峰值

A2-V 正常完成但证据缺失，INCONCLUSIVE，禁止强模型，当前不进入 S09。

### 19.3 Long-Manual 表演

A1 通过不同时间、facts 与 duplicate groups 验证准备/表演/鼓掌，0 VBU。

### 19.4 古镇—奶茶—古镇

A/C relation 与 B material gain 分成两个任务；可得到 RESUMED 与 broader LOCAL 两个各自有 gate 的 alternative，不改变 S05 seams。

### 19.5 多次 Preview

同一任务 exact-cache；全日所有 Preview paid spend 仍 ≤4 VBU，Final 使用全日剩余预算。

### 19.6 Provider outage

同级 retry/fallback；失败仍为 NOT_EVALUATED，不升级 A3，不删除 Candidate。

## 20. 状态边界

### FROZEN

- one-question task、每 Candidate 最多两个必要 task；
- 五个 ExecutionStatus、四个 EvidenceDecision 与合法矩阵；
- 四类 ValidationQuestion；
- KEEP/CONTEXT_ONLY/DROP 与局部 Evidence boundary；
- A0/A1 + 最低充分分支 + 最多一次能力升级；
- Provider failure 同级 fallback，semantic inability 才能升级；
- A2-V 3 frame、A2-T 2 excerpt/6s、A2-A 1 excerpt/15s、A3 不扩张的 V1.18 envelope；
- VBU action weights 与 task/candidate/Preview/day/A3 versioned caps；
- atomic reservation、decision-yield scheduler 与真实美元双重门；
- exact cache、queue idempotency、retry/failure attribution；
- immutable Revision、stale result 与跨 Revision wrapper；
- independent ValidatedCandidate/AlternativeResolution；
- S08 不回写 S04–S07，不替代 S09–S12。

### OPEN / 待真实数据或工程

- provider/model、prompt、schema、parameter、timeout 与 backoff；
- 动态价格、reference-light 单价与 S08 月度真实份额；
- VBU 权重与 4/16、6/8、A3/day=2 的真实校准；
- 每 Candidate 两 task 的 truncation regret；
- 3 frame / 6s proxy / 15s audio 的召回损失；
- A1/A2/A3 的 precision、INCONCLUSIVE 与 escalation lift；
- speech permission/data-policy 的产品实现；
- Production schema、budget service、router、cache、queue、runner、Validator；
- S09 Production selection engine、schema、solver 与真实校准（S09 架构已由 V1.19 冻结）；
- 16s/73s 非标准 Manual Window。

OPEN 参数必须通过 Benchmark 显式重开，不能由实现静默修改。

### IMPLEMENTATION GAP

- X01 仍是一轮实验模型调用，不是分阶段 S08；
- 当前没有 Production S08 engine、schema、budget scheduler、persistent cache、outcome aggregator 或真实用户标注；
- 当前没有 provider telemetry 证明成本与 envelope 数值；
- V1.18 是算法架构冻结，不是 Production readiness。

## 21. 复核证据

P01–P17 覆盖：

- 无 provisional 普通日；
- 生日 clear/occluded peak；
- Long-Manual 表演；
- 古镇—奶茶—古镇 resumed/alternative；
- 相似但分离的两次遛狗；
- 演唱会多峰；
- speech permission；
- provider timeout、invalid output、semantic escalation；
- 多次 Preview、Late Data、atomic budget；
- 186 RawAsset / 220 Window 高强度参考日进入 Final 8-Candidate frontier；
- 月度 warning 与 shared alternative task。

容量推导：

~~~text
Final frontier <= 8
tasks per Candidate <= 2
planned tasks <= 16
day paid VBU <= 16
paid dispatch <= 16
A3 task starts <= 2
~~~

未发现结构性 blocker。该检查不使用真实媒体、模型、价格或标签，因此不证明真实 precision/recall、用户满意度或 Production 成本。
