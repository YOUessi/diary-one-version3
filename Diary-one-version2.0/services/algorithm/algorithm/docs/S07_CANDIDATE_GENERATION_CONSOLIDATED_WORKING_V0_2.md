# S07 Chapter / Aha Candidate Generation — Consolidated Working Contract V0.2

**状态：** `HISTORICAL WORKING RECORD / CANONICALIZED BY V1.17`
**日期：** 2026-08-26
**决策来源：** 用户确认 S07-A～F，并同意交叉检查 F1–F7 修订方向
**作用范围：** S07 Candidate unit、Chapter local Episode、Resumed/Local grouping、Aha gate、candidate duplicate/audit、bounded cost、Revision 与 S08 handoff
**权威状态：** 本文保留冻结前设计过程；当前规范以 [V1.17](CANONICAL_CHECKPOINT_V1_17_CHAPTER_AHA_CANDIDATE_GENERATION.md) 为准
**继承关系：** V1.17 继承 V1.16–V1.1 与 V1.0 未被覆盖的规则

> **当前后续状态：** 本文留给 S08 的 action-weight、cost、exposure 与 outcome 问题已由 [V1.18](CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md) 冻结；正文中的 OPEN 是 S07 设计当时的历史状态。

## 1. 结论摘要

S07 只把 S06 的共享 Moment seed 转换为结构化 Chapter/Aha 假设：

```text
S06 Role-Assigned Moment Packet
→ S07 bounded candidate generation
→ gate / duplicate / audit
→ ELIGIBLE Candidate
   or PROVISIONAL_VALIDATION_REQUIRED
   or SUPPRESSED_DUPLICATE
   or REJECTED
→ bounded S08 validation frontier
```

S07 不决定最终页面，不做全天 Set Selection，不选择最终媒体，不生成 Narrative，也不改写任何上游事实、角色或边界。

## 2. 术语

### 2.1 Candidate / 候选

一个内部、可追溯的记忆假设：现有 Evidence 可能支持一个 Chapter 或 Aha，值得进入后续验证或集合选择。

Candidate 不是：

- 最终 Chapter / Aha；
- 最终 title、story、hero、time label 或 tag；
- 一个 KEEP Observation 的自动副本；
- 一个模型自评分；
- 为填满全天数量而制造的对象。

### 2.2 CandidateContentUnit / 候选内容单元

一个由 KEEP Observation 支持、与 Candidate 主题相关、去重后仍提供独立内容贡献的内部单元。它是“未来可能支持一个精选素材位置”的证据单位，不是最终媒体选择。

规则：

- 必须至少引用一个当前 Window 的 `STRONG/MODERATE` grounded item；
- 必须有一个 primary Window 与 underlying RawAsset；
- 同一 Window 的多帧最多形成一个 CandidateContentUnit；
- 同一 Auto 9s RawAsset 最多形成一个 CandidateContentUnit；
- Manual Photo 最多形成一个 CandidateContentUnit；
- 同一长 Manual Video 的多个 Window 只有在时间区间不同、grounded 内容不同且不属于 duplicate group 时，才可形成多个 CandidateContentUnit；
- CONTEXT_ONLY 不形成 CandidateContentUnit；
- DROP 不形成、支持或恢复 CandidateContentUnit；
- CandidateContentUnit 数量不保证 S10 最终媒体质量或一定入选。

### 2.3 EpisodeGroupSignature / 候选组签名

用于防止相邻关系逐步漂移成全天主题集合。至少记录：

- 当前安全的 Episode basis；
- grounded Activity / progression；
- Context Motif 与少量结构化视觉语义；
- time、真实 capture gap 与可信 locality；
- 匿名 entity/object continuity；
- support、contradiction、member 与 provenance。

只有已经进入当前 Candidate 的 content member 才更新其 EpisodeGroupSignature。新的 Moment 必须同时通过局部关系、group-wide compatibility 与 material-gain gate，不能只与前一 Moment 相似就无限链式扩张。

### 2.4 GateDecision

每个必要 gate 只能返回：

```text
PASS
NEEDS_VALIDATION
FAIL
```

- `PASS`：当前 Evidence 已足够；
- `NEEDS_VALIDATION`：基础 Evidence 已成立，存在一个局部、明确、允许范围内可解决的问题；
- `FAIL`：硬条件不成立，或缺失内容无法在允许范围内可靠解决。

“是否值得用户喜欢”不能作为昂贵模型的模糊 validation question。S08 只验证事实、关系、时间变化或结构化媒体多样性等可核查问题。

Chapter / Aha 的 Memory Value Gate 在 V1 只允许 `PASS / FAIL`。S08 可以核查事实或局部关系，但不能替系统创造主观价值，也不能把一个价值不足的 Candidate 救活。

### 2.5 CandidateDisposition

```text
ELIGIBLE
PROVISIONAL_VALIDATION_REQUIRED
SUPPRESSED_DUPLICATE
REJECTED
```

- `ELIGIBLE`：所有必要 gate 均 PASS；
- `PROVISIONAL_VALIDATION_REQUIRED`：没有 FAIL，至少一个 gate 为 NEEDS_VALIDATION，且存在合法 ValidationQuestion；
- `SUPPRESSED_DUPLICATE`：当前 Evidence 已证明其与保留 Candidate 重复或被可靠支配；
- `REJECTED`：至少一个硬 gate FAIL，或候选合同无效。

Candidate disposition 只属于当前 Revision，不改写 S06 role。

若同一 hypothesis 同时命中多种情况，按以下顺序确定唯一 disposition：

1. 合同无效或任一不可验证的硬门 FAIL → `REJECTED`；
2. 其余硬门可成立，但当前 Evidence 已证明与保留 Candidate 重复或被支配 → `SUPPRESSED_DUPLICATE`；
3. 无 FAIL，至少一个允许验证的 gate 为 NEEDS_VALIDATION → `PROVISIONAL_VALIDATION_REQUIRED`；
4. 其余情况 → `ELIGIBLE`。

Duplicate suppression 不是用来掩盖 Evidence 不足的替代状态；被 REJECTED 的 Candidate 仍可把 duplicate 作为 secondary reason 保存。

### 2.6 SeedAuditRecord

一个 S06 content-active seed 可能同时产生 SINGLE、Aha 并参与 group，因此不使用互斥的单一“emitted/joined”枚举。每个 seed 必须恰好有一条 SeedAuditRecord：

```text
seed_id
originated_candidate_ids[]
participated_candidate_ids[]
no_candidate_reasons[]
```

规则：

- 这里的 seed universe 只指 S06 明确输出的 content-active shared candidate seed；context-only 与 output-inactive Moment 没有 content seed，继续使用其既有 route audit；
- `originated_candidate_ids`：由该 seed 作为 owner 创建的 SINGLE、group 或 Aha；
- `participated_candidate_ids`：该 seed 作为内容成员加入、但由更早 seed owner 创建的 group；
- 两个列表都引用已经 materialize 的 hypothesis ID，不论其最终 disposition；具体结论从 CandidateAuditRecord 读取；
- 两个 Candidate 列表均为空时，必须至少有一个 `no_candidate_reason`；
- 只要任一 Candidate 列表非空，仍可记录其他路径未生成候选的原因，但不能把 seed 总体误记为无候选。

## 3. 输入边界

S07 只读取同一 immutable Revision 中：

- S04 Observation facts、status、support、UNKNOWN 与 limitations；
- S05 Moment membership、ordinary/Transition type、time、gaps、Signature 与 ledger refs；
- S06 KEEP / CONTEXT_ONLY / DROP role、reason、candidate route 与 duplicate refs；
- RawAsset / Window / Frame / source / media / capture provenance；
- pipeline、schema、taxonomy、model、prompt 与 parameter versions。

S07 不允许：

- 混用旧 Revision 的 role 与新 Revision 的 Moment；
- 改写 S04 facts；
- 改写 S05 membership、Core/Tail、seam 或 Transition type；
- 静默改写 S06 role；
- 用 CONTEXT_ONLY 生成 Claim 或内容单元；
- 恢复 DROP；
- 在本阶段新增用户可见 Narrative。

## 4. Candidate unit 与 route

### 4.1 ChapterCandidate

ChapterCandidate 只来自一个或多个 ordinary content-active Moments，允许：

```text
SINGLE
ADJACENT_GROUP
RESUMED_EPISODE
LOCAL_EPISODE_GROUP
```

Transition Moment 永远不能成为 Chapter content member。它只可作为 interruption / gap / constraint reference。

### 4.2 AhaCandidate

AhaCandidate 只表达一个 origin Moment 内的一个局部峰值：

- ordinary content-active Moment 可提名；
- Transition content-active Moment 可提名；
- V1 不跨 Moment 合成 Aha；
- Aha 不是低分 Chapter，也不是 Chapter 的缩写。

### 4.3 Route

| S06 route | S07 route |
|---|---|
| ordinary content-active | Chapter + Aha eligibility |
| Transition content-active | Aha eligibility only |
| context-only Moment | Context Envelope only |
| output-inactive Moment | audit only |

Chapter path FAIL 不自动触发 Aha；Aha 必须独立通过自己的 gate。

## 5. Chapter Candidate gates

### 5.1 所有 Chapter 共用的必要 gate

1. **Source Gate**：所有 content members 均为当前 Revision 的 ordinary content-active Moments；
2. **Truth Gate**：所有内容单元只引用允许的 KEEP grounded facts；
3. **Local Episode Gate**：能够谨慎表达一段局部经历，而不是全天主题；
4. **Coherence Gate**：成员之间不存在破坏核心 Episode 的强矛盾；
5. **Coverage Gate**：存在足够非重复内容支持未来 3–5 个精选位置；
6. **Memory Value Gate**：至少有一个明确的正向记忆价值理由，不是仅因“发生过”；
7. **Inference Risk Gate**：无需虚构地点、意图、人物关系、情绪或连续录像；
8. **Internal De-duplication Gate**：内容单元与候选范围未被重复虚增；Candidate 之间的 duplicate disposition 另按第 8 节处理。

Manual intent 可以支持 memory value，但不绕过 Truth、Coverage、Coherence 或 duplicate gate。

### 5.2 Normal Chapter path

```text
distinct KEEP RawAsset count >= 3
AND non-redundant CandidateContentUnit count >= 3
```

数量满足不代表自动通过。三个近重复 RawAsset 去重后不足三个内容单元，Coverage Gate 仍 FAIL。

### 5.3 Long-Manual exception path

为避免误杀由长 Manual 视频承载的完整 Episode，允许：

```text
distinct KEEP RawAsset count = 1 or 2
AND at least one source is Manual Video
AND non-redundant CandidateContentUnit count >= 3
AND units come from temporally distinct Manual Windows
AND grounded content shows real progression / complementary facets
AND all other Chapter gates PASS
```

满足这些条件只得到：

```text
PROVISIONAL_VALIDATION_REQUIRED
validation_target = MEDIA_DIVERSITY
LongManualDiversityConfirmationGate = NEEDS_VALIDATION
```

进入这条例外路径前，CandidateContentUnit 的初步时间差异、grounding 与去重条件必须已经成立，其他 Chapter gates 必须 PASS；S08 只对“同一长视频里的这些 Window 是否足以作为多个真实不同的内容位置”做一次更严格确认，不负责最终构图、美感或渲染。确认 PASS 时，S08 输出 downstream-eligible 的 ValidatedCandidate；确认 FAIL 或在允许 Evidence 范围内无法可靠解决时，S08 输出 rejected validation outcome。原 S07 Candidate 始终保持 provisional 且不可被 S08 回写。若只是没有进入当前 S08 budget frontier，则只保留当前 Revision 的 provisional audit，不能进入最终输出。

### 5.4 SINGLE

一个 ordinary content-active Moment 可以独立形成 ChapterCandidate，当且仅当：

- 单独通过全部 Chapter gates；
- 不依赖邻居补全核心 Episode；
- 相邻 Context 只能限制解释，不能救活缺失内容；
- 候选自身足够理解、完整且值得作为一章。

### 5.5 ADJACENT_GROUP

两个或更多时间线上直接相邻的 ordinary content-active Moments 可以形成 ADJACENT_GROUP，当且仅当：

- 中间没有任何其他 committed Moment；
- 时间相邻之外，至少有一个独立的 Episode link；
- 至少两个不重复 signal families 相互支持；
- 每个 member 至少贡献一个相关、非重复 CandidateContentUnit；
- 组合显著增加完整性、过程或理解，不只是增加 RawAsset 数；
- S05 seam 继续保留，不被改写为 MERGE。

若中间存在 Transition、context-only、output-inactive 或普通独立 Moment，不能标为 ADJACENT_GROUP，转入 RESUMED / LOCAL 规则。

## 6. RESUMED_EPISODE 与 LOCAL_EPISODE_GROUP

### 6.1 RESUMED_EPISODE

RESUMED_EPISODE 表达同一活动主线被中断后恢复：

```text
A：活动主线
B：中断 Moment(s)
C：活动主线恢复

Candidate content members = A + C
interruption refs = B
```

必要条件：

- A、C 为非相邻 ordinary content-active Moments；
- 最多跨越 2 个 committed intermediate Moments；
- locality/time anchor 与 activity/thread anchor 等至少两个独立 signal families 支持；
- C 有“恢复同一具体主线”的证据，不只是主题或视觉相似；
- B 完整保留为 interruption refs，不能假装不存在；
- Candidate 不声称 A 到 C 之间连续录像或持续活动；
- 任何 blocker、强矛盾或无支持长 gap 均停止关系。

### 6.2 LOCAL_EPISODE_GROUP

LOCAL_EPISODE_GROUP 表达同一次局部 outing / visit / occasion 中的多个不同小 Episode。

必要条件：

- 内容成员均为 ordinary content-active Moments；
- 存在一个安全、可核查的共同 occasion envelope；
- 不能仅以相同地点、视觉风格或泛化主题推断统一意图；
- 每个 content member 提供独特贡献；
- 中间非内容 Moment 必须显式记录为 interruption / context / blocker；
- Candidate span 是时间线上有界、可追溯的连续范围，不能从全天任意挑选相似 Moment。

一个 LOCAL_EPISODE_GROUP 可以内部记录 A→C 的 resumed relation，但不能因此抹掉 B。

### 6.3 中间 Moment 的 S07 关系标签

```text
INCLUDED_COMPONENT
INTERRUPTION_REF
BLOCKER
```

它们只描述当前 Candidate 的关系，不是新的 S06 role，也不能反向改写 S05/S06。

### 6.4 有界 nomination 与可控 group extension

当前工作 Baseline：

```text
relation_nomination_forward_horizon = 8 committed Moments
resumed_intervening_moment_max = 2
unsupported_capture_gap_max = 30 minutes
group_member_safety_max = 12  # PROVISIONAL V1 BASELINE
```

规则：

- “8”限制从一个 seed 主动寻找非相邻 relation hypothesis 的 forward horizon；
- horizon 按 committed Moment 的时间线位置计数；
- 已成立的 adjacent/local group 可以逐个向后扩展到 8 之外；
- 每次扩展必须同时通过 local relation、EpisodeGroupSignature compatibility 与 material-gain gate；
- 不能只靠相邻 pairwise similarity 做传递链；
- 达到 12、blocker、group drift 或超过 30 分钟无有效 Evidence gap 时立即停止；
- “12”只计算 Chapter content members，不计算 interruption/context/blocker refs；所有被跨越的 committed Moment 仍必须完整出现在 span trace 中；
- 12 是当前待复核参数，不是永久自然常数；
- 达到上限必须记录 `SCOPE_LIMIT_REACHED`，尾部 Moment 可独立提名，不能静默消失；
- capture gap 使用规范化 capture time，不使用 import / Sync time；
- capture time 缺失不能证明连续。

## 7. Aha Candidate gates

### 7.1 Candidate interval

一个 AhaCandidate 必须包含：

- exactly one `origin_moment_id`；
- exactly one KEEP `peak_window_id`；
- 可选的紧邻 before/after support Window；
- 总计最多 3 个连续 eligible Windows；
- `latest.capture_end - earliest.capture_start <= 3 minutes`；
- interval 不跨 origin Moment，不跨 DROP；
- CONTEXT_ONLY support 只能限制解释，不能生成内容事实或 Anchor。

这里的 eligible support Window 只允许当前 origin Moment 内紧邻 peak 的 KEEP，或明确标注为 non-claim 的 CONTEXT_ONLY；peak 本身必须是 KEEP。DROP、FAILED 与跨 Moment Window 均不在 interval 内。

三个支持 Window 是理解范围，不是三个最终媒体。S10 最终只选择一个 Aha EvidenceAnchor。

### 7.2 LocalPeakGate

至少存在一种：

- 当前 Window 多帧直接支持可观察变化；
- 相对当前 Moment Core 出现明确的新动作、人物、对象或短暂现象；
- 存在具体、短暂、可独立定位的互动、动作、结果或自然现象。

motion、embedding change、scene change、Manual intent、漂亮画面或 Live Photo 适配性只能提名，不能单独 PASS。

若已有可靠主体/场景与强局部事件提示，只差一个允许范围内可验证的动作事实，LocalPeakGate 可以 `NEEDS_VALIDATION`。只有 motion/blur/UNKNOWN 时必须 FAIL。

### 7.3 IndependentMemoryValueGate

Aha 必须：

- 可独立理解；
- 具体而非普通活动；
- 适合由单一局部 Anchor 表达；
- 删除后会丢失一个不同的互动、变化、现象或重要细节；
- 不是对某个 Chapter 完整 episode basis 的简单缩写或摘要；它可以发生在 Chapter 内，但必须表达一个可独立定位、删除后会丢失的局部事件。

Manual intent 可以支持个人相关性，但不能单独通过；S08 不能通过更强模型“创造”主观价值。

因此 IndependentMemoryValueGate 在 V1 必须直接 `PASS` 或 `FAIL`，不能返回 `NEEDS_VALIDATION`。允许进入 S08 的不确定性只能位于已有独立价值基础上的事实、关系或具体 local peak。

### 7.4 Ordinary / Transition 限制

```text
ordinary origin Moment
→ at most 3 non-overlapping Aha Candidates

Transition origin Moment
→ at most 1 Aha Candidate
```

Transition Aha 必须只依赖自身 KEEP，不能借左右 Moments 补全。边界不明确本身不是 local peak 或 memory value。

多个 Aha interval 若指向同一具体事件，进入 duplicate group，不因 Window/Frame 数不同而重复计数。

## 8. Candidate duplicate 与 reject audit

### 8.1 S07 duplicate 范围

S07 只比较同一局部 Episode/event 的 Candidate：

- 完全相同 Candidate；
- 同一 Memory basis 的不同生成方式；
- nested scope 中没有新增意义的 dominated Candidate；
- 同一具体 peak 的多个 Aha。

跨较长时间、不同 Episode 的相似生活内容不能仅因 embedding、scene、object 或 style 相似被 S07 判重。全天集合冗余留给 S09。

### 8.2 S08 前允许 suppression 的条件

只有以下情况可在 S07 直接 `SUPPRESSED_DUPLICATE`：

- identity / refs / basis 完全相同；
- 当前 Evidence 已经证明两个 Candidate 表达同一 Memory；
- 当前 Evidence 已经证明较大范围没有新增内容、价值或完整性；
- representative selection 不依赖尚未执行的 validation。

若差异需要 S08 才能确认，两个 Candidate 都保留并加入：

```text
alternative_hypothesis_group_id
```

若 alternative 成员各自的事实与价值已经足够、无论最终选哪个都可独立使用，它们可以保持 `ELIGIBLE`，把集合取舍留给 S09。若只有解决 relation/dominance 后才能安全决定其下游资格，则为相关成员记录 `AlternativeResolutionGate = NEEDS_VALIDATION`，使其成为 provisional 并提交一个共享、局部的 ValidationQuestion；不能让一个没有任何 NEEDS_VALIDATION gate 的 ELIGIBLE Candidate 偷渡进 S08。

suppressed Candidate 的 alternate refs 只用于 provenance：

- 不扩张 retained Candidate 的事实；
- 不增加 CandidateContentUnit 或 RawAsset count；
- 不增加精选媒体资格；
- 不改变 source Moment membership。

### 8.3 Representative 优先级

1. grounded Evidence 更可靠；
2. Episode / peak basis 更具体；
3. inference risk 与 limitations 更少；
4. 非重复内容覆盖更充分；
5. 已经足够时范围更小；
6. 完全相同时使用稳定 deterministic tie-break。

不在 S07 比较最终构图、美感、音效或渲染质量。Manual 不自动获胜。

### 8.4 Candidate-level audit

每个生成过的 Candidate hypothesis 必须保存：

- Candidate ID、type、Revision 与 snapshot；
- source/owner/participant Moment IDs；
- CandidateContentUnit、RawAsset、Window、Frame 与 fact refs；
- context/interruption/blocker refs；
- 每个 gate 的 PASS / NEEDS_VALIDATION / FAIL；
- CandidateDisposition；
- primary reason 与 secondary reasons；
- duplicate / alternative / representative refs；
- limitations、contradictions、versions 与 provenance。

最低 reason families：

```text
CONTRACT_INVALID
EVIDENCE_INSUFFICIENT
EPISODE_RELATION_UNSUPPORTED
CHAPTER_COVERAGE_INSUFFICIENT
MEMORY_VALUE_INSUFFICIENT
LOCAL_PEAK_UNSUPPORTED
INFERENCE_RISK_TOO_HIGH
DUPLICATE_SUPPRESSED
DOMINATED_SCOPE
VALIDATION_REQUIRED
```

Revision mismatch、未知 ID、越权 Evidence 等是合同错误，不能伪装成普通内容质量拒绝或 EMPTY_DAY。

## 9. Candidate 数量与成本

### 9.1 Per-seed generation cap

普通 content-active seed：

```text
owned SINGLE Chapter Candidate <= 1
owned grouped Chapter hypotheses <= 2  # all group types combined
origin Aha Candidates <= 3
```

Transition content-active seed：

```text
Chapter Candidate = 0
origin Aha Candidate <= 1
```

Group 只由时间线上最早的 content member owner 创建；其他 member 在 SeedAuditRecord 的 `participated_candidate_ids` 中引用。S07 不枚举 AB、BC、ABC 等所有排列。

达到 seed cap 时必须记录具体 route 与 `AHA_SEED_CAP_REACHED` / `GROUP_HYPOTHESIS_CAP_REACHED`，以及未 materialize hypothesis 的最小 Evidence refs；不能把 cap 截断伪装成 gate FAIL，也不能静默忽略。

### 9.2 不设置全天 editorial Top-K

S07 结构化候选计算便宜。Candidate pool 不因页面最终只有 5+3 个对象就提前截成全天 Top-K。

工程异常上限只能作为 safety guard：

- 达到时记录 `SAFETY_LIMIT_REACHED`；
- 不得静默删除；
- 必须测量被截断候选类型与 regret；
- 真实数据证明需要时再版本化调整 per-seed 或 group cap。

### 9.3 S07 默认成本合同

- 使用缓存 S03/S04/S05/S06 结构化数据；
- 使用 deterministic / lightweight comparison 与已存在 embedding；
- 不增加 VLM / strong-model 调用；
- 不上传新媒体；
- 不补取 Auto `UPLOAD_1` 的另外两帧；
- 不请求完整 Auto / Manual Raw；
- 不等待下一次 Sync；
- relation comparison 随 Moment 数量近似线性增长，不做全天 O(n²) all-pairs。

至少记录：seed count、comparison count、candidate count by type/disposition、duplicate ratio、scope stop、cache hit、CPU time、S08 handoff count。

## 10. S08 admission 与 handoff

### 10.1 谁不进入 S08

- `ELIGIBLE` Candidate：直接进入 S09 可用的 downstream candidate pool，不消耗 S08 validation frontier，也不冒充经过额外验证的 `ValidatedCandidate`；
- `REJECTED`：不进入；
- `SUPPRESSED_DUPLICATE`：不进入；
- 没有明确、可解决 ValidationQuestion 的 provisional Candidate：改为 REJECTED，而不是模糊升级。

### 10.2 S08 admission 条件

只有 `PROVISIONAL_VALIDATION_REQUIRED` 可以申请进入 S08，并至少满足一种：

- validation 可决定该 provisional Candidate 的下游 ELIGIBLE / REJECTED 资格；
- validation 可解决 alternative group 的关系或 dominance；
- validation 可确认 Long-Manual `MEDIA_DIVERSITY`；
- validation 可确认一个已有可靠主体/场景基础的具体 local peak。

同时必须：

- 已通过独立 memory-value 初筛；
- 没有更可靠、等价且已 ELIGIBLE 的 Candidate；
- 问题局限在 Candidate 自身允许 Evidence 范围；
- 不要求违反既有 upload / no-refetch 合同。

这不是 S09 Top-K，也不宣称已经知道最终集合。

### 10.3 Candidate handoff count guardrail

```text
Preview Revision S08 frontier <= 3 Candidates
Final Revision S08 frontier <= 8 Candidates
```

这是 Candidate 数量 guardrail，不是模型调用数或完整美元预算。S08 仍需按 action cost、token、媒体暴露与 monthly guardrail 建立加权预算。

未进入 frontier 的 provisional Candidate：

- 保持当前 Revision 的内部 provisional audit；
- 记录 `NOT_ADMITTED_BUDGET` 或其他原因；
- 未经验证不能进入最终输出；
- 不用于凑 Chapter/Aha 数量；
- 新 Revision 可重新评估。

### 10.4 ValidationQuestion 最小合同

- candidate / revision / snapshot refs；
- target gate；
- 一个具体 unknown 或 contradiction；
- current grounded support；
- allowed Evidence / modality / time scope；
- explicitly disallowed source/refetch；
- PASS/FAIL 分别会产生什么 downstream eligibility / resolution；
- expected cost class 与 provenance；
- versions。

S07 不选择 provider。S08 返回新的 ValidatedCandidate、AlternativeResolution 或失败结果，不能反向改写 S07/S06/S05/S04；原 S07 Candidate 的 disposition 仍保持 provisional，后续读取 S08 outcome 决定是否可进入 S09。

## 11. Revision、ID 与 lineage

- 每个 Candidate instance 属于且只属于一个 immutable Revision；
- same snapshot + same inputs + same versions 必须确定性复现；
- `candidate_instance_id` 是 Revision-scoped，提交后不可修改；
- Candidate fingerprint 至少包含 ordered Evidence refs、roles、content units、relation edges 与 versions；
- 跨 Revision lineage 可记录 `continues / expands / merges / splits / supersedes`；
- fingerprint 不能只依赖可能变化的 Moment ID；
- 新素材或 Late Data 创建新 Revision；
- 旧 Candidate 与 audit 保持不可变；
- 未变化 fingerprint 可以复用 S07 结果；
- 跨 Revision 复用的是确定性计算结果或缓存 payload；仍须生成或绑定当前 Revision 的 instance/provenance，绝不能把旧 Revision 的 `candidate_instance_id` 直接当作新 Revision ID；
- 用户可见 Chapter stable ID 留给 S09/publish，不由 Candidate ID 冒充。

## 12. 输出合同

S07 至少输出：

```text
ChapterCandidate[]
AhaCandidate[]
AlternativeHypothesisGroup[]
DuplicateCandidateGroup[]
SeedAuditRecord[]
CandidateAuditRecord[]
S08ValidationRequest[]
S07RunTrace
```

`ChapterCandidate[] / AhaCandidate[]` 只承载 `ELIGIBLE` 与 `PROVISIONAL_VALIDATION_REQUIRED` 的 materialized Candidate。`CandidateAuditRecord[]` 覆盖所有生成过的 hypothesis，包括 `SUPPRESSED_DUPLICATE` 与 `REJECTED`，并可派生 rejected-candidate audit 视图；因此任何失败或抑制都不会静默消失，也不会被下游误当成可选 Candidate。

Candidate 内容引用与 context 引用必须分离：

- content refs 只来自 KEEP；
- context refs 只做 non-claim 限制；
- DROP 只可出现在 audit/provenance；
- 同一 RawAsset 的多 Window 必须保留 source offsets；
- 不生成 title、story、hero 或最终 Claim。

## 13. Validator 不变量

提交 S07 输出前至少验证：

1. 所有引用属于同一 Revision / snapshot；
2. 所有 Chapter content members 为 ordinary content-active；
3. Transition 没有进入 Chapter content；
4. 每个 Aha 只有一个 origin Moment 与一个 KEEP peak Window；
5. Aha interval 不超过 3 eligible Windows / 3 minutes，不跨 Moment 或 DROP；
6. CONTEXT_ONLY 没有生成 CandidateContentUnit、Claim 或媒体计数；
7. DROP 没有被恢复；
8. Normal Chapter 同时满足 RawAsset 与内容单元门；
9. Long-Manual exception 的 S07 Candidate 必须始终为 provisional，并具有 `MEDIA_DIVERSITY` ValidationQuestion；
10. RESUMED 没有跨越超过 2 个 intermediate Moments；
11. relation nomination 没有越过 8-Moment horizon；
12. group 没有超过当前 12-member safety cap；
13. group 每次扩展有 local、group-wide 与 material-gain trace；
14. 每个 seed 恰好有一个 SeedAuditRecord；
15. 每个生成过的 Candidate 有且只有一个 CandidateDisposition；
16. `PROVISIONAL_VALIDATION_REQUIRED` 必须有合法 ValidationQuestion；
17. suppression 不依赖尚未运行的 validation；
18. alternate refs 不增加 retained Candidate 内容；
19. Preview / Final S08 frontier 分别不超过 3 / 8；
20. 输出没有 Narrative 或最终媒体决定；
21. S07 没有新增 upload/refetch/model call；
22. same input/version 可确定性复现；
23. Memory Value Gate 没有以 NEEDS_VALIDATION 进入 S08；
24. 跨 Revision cache reuse 没有复用旧 Revision 的 candidate instance identity；
25. REJECTED / SUPPRESSED Candidate 没有出现在下游可选 Candidate 数组，但都有 CandidateAuditRecord；
26. S08 request/outcome 没有回写 S07 Candidate disposition，而是通过独立结果表达 downstream eligibility；
27. 需要 S08 解决的 alternative member 具有明确的 `AlternativeResolutionGate = NEEDS_VALIDATION`，不存在无 gate 的 ELIGIBLE Candidate 偷渡验证。

## 14. 典型例子

### 14.1 古镇—奶茶—古镇

```text
A：古镇步行
B：奶茶店
C：继续古镇步行
```

- A↔C 可以形成 RESUMED_EPISODE，B 为 interruption ref；
- A+B+C 可以形成 LOCAL_EPISODE_GROUP，前提是 B 对同一次 outing 有独特贡献；
- 两个 Candidate 若表达不同 Memory basis，可进入 alternative group；
- B 普通喝饮品不自动成为 Aha；
- 所有 S05 seams 保留。

### 14.2 一条 120s 家庭表演视频 + 一张照片

- distinct RawAsset = 2；
- 若至少 3 个 Manual Windows 具有时间和内容差异，可走 Long-Manual exception；
- Candidate 为 PROVISIONAL，S08 只验证媒体语义多样性；
- 不再因 RawAsset < 3 直接拒绝完整 Chapter；
- 一个具体谢幕/吹蜡烛 peak 仍可独立提名 Aha。

### 14.3 一个演唱会 Moment 内三个峰值

- 一个 SINGLE ChapterCandidate；
- 最多三个互不重叠、分别通过双门的 AhaCandidate；
- 同一事件的多个 Window 合并为一个 Aha；
- S09 最终仍最多选择三个，并控制与 Chapter 的语义重复。

## 15. 仍需真实数据或后续阶段决定

- `group_member_safety_max = 12` 的 truncation regret 与 false-group risk；
- 30 分钟 unsupported gap 的 missed-continuity regret；
- ordinary seed 最多 3 个 Aha 的 cap-hit rate 与 truncation regret；
- ordinary seed 最多 2 个 grouped hypotheses 的 cap-hit rate，尤其是 nested alternatives 的 truncation regret；
- CandidateContentUnit 的具体 similarity / semantic-gain threshold；
- Long-Manual media diversity 的 S08 validator；
- unresolved alternative ratio 与 dominance validation 收益；
- S08 action-weighted token、cost 与 exposure budget；
- S09 Candidate scoring、set-level overlap 与 final quota；
- S10 最终媒体质量、同一长 Manual 的多 Anchor 可用性与渲染；
- Production JSON Schema、reason taxonomy、stable lineage matcher；
- 真实不同用户、生活方式与拍摄质量分层 Benchmark。

这些 OPEN 项不能在 Production 中静默漂移。任何数值调整必须版本化、保留前后 Trace，并通过新的 Checkpoint 冻结。
