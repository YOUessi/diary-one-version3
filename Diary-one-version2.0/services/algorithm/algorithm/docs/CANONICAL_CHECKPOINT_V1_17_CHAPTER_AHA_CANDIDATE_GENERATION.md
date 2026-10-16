# Diary One Canonical Checkpoint V1.17 — S07 Chapter / Aha Candidate Generation

**状态：** FROZEN
**冻结日期：** 2026-08-26
**决策来源：** 用户逐项确认 S07-A～F、确认 F1–F7 交叉检查修订、确认 P01–P13 V0.2 复跑结论，并显式确认冻结
**作用范围：** S07 Candidate unit、Chapter local Episode、Resumed/Local grouping、Aha 双门、candidate duplicate/alternative、seed/candidate audit、有界生成、Revision 与 S08 handoff
**继承关系：** 继承 V1.16–V1.1 与 V1.0 未被本文覆盖的规则
**验证依据：** `S07_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_1.md` 与 `S07_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_2.md`

> **当前后续覆盖：** [V1.18](CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md) 已冻结本文交给 S08 的四类 ValidationQuestion、动作树、VBU/美元双重预算、缓存、失败、Revision 与独立 outcome。本文关于 S08 完整预算“仍 OPEN”的历史表述由 V1.18 覆盖；S07 Candidate 合同继续有效。

## 1. 冻结结论

S07 只把 S06 的共享 content-active Moment seed 转换为有证据、可审计、有界的 Chapter/Aha 假设。Candidate 不是最终页面，也不是用户可见 Memory。

完整职责链为：

~~~text
S06 Role-Assigned Moment Packet
→ S07 bounded candidate generation
→ gate / duplicate / alternative / audit
→ ELIGIBLE Candidate
   or PROVISIONAL_VALIDATION_REQUIRED
   or SUPPRESSED_DUPLICATE
   or REJECTED

ELIGIBLE
→ downstream candidate pool

PROVISIONAL_VALIDATION_REQUIRED
→ bounded S08 validation frontier
→ independent ValidatedCandidate / AlternativeResolution / failure outcome
→ downstream candidate pool only when downstream eligibility is established

downstream candidate pool
→ S09 Editorial Set Selection
~~~

S07 不决定：

- 最终 1–5 Chapter / 0–3 Aha 集合；
- 第 5 个 Chapter 是否进入最终页面；
- 最终 title、story、time label、tag 或 Claim；
- 最终 hero、EvidenceAnchor、PHOTO/LIVE_2S/VIDEO_5S；
- S08 provider、模型、Token 或完整成本预算；
- 用户主观情绪、人物关系或未被 Evidence 支持的意图。

## 2. 核心术语

### 2.1 Candidate / 候选

一个内部、可追溯的记忆假设：当前 Revision 的 Evidence 可能支持一个 Chapter 或 Aha，值得进入后续验证或集合选择。

Candidate 不是：

- 一个 KEEP Observation 的自动副本；
- 最终 Chapter/Aha；
- 为满足全天数量而制造的对象；
- 模型自评分本身；
- 最终媒体或 Narrative。

### 2.2 CandidateContentUnit / 候选内容单元

一个由 KEEP Observation 支持、与当前 Candidate basis 相关、去重后仍提供独立内容贡献的内部证据单元。它只表示“未来可能支持一个精选素材位置”，不保证 S10 最终采用。

冻结规则：

1. 至少引用一个当前 Window 的 `STRONG/MODERATE` grounded item；
2. 具有一个 primary Window 与 underlying RawAsset；
3. 同一 Window 的多帧最多形成一个 CandidateContentUnit；
4. 同一 Auto 9s RawAsset 最多形成一个 CandidateContentUnit；
5. Manual Photo 最多形成一个 CandidateContentUnit；
6. 同一长 Manual Video 的多个 Window 只有在时间区间不同、grounded 内容不同且不属于 duplicate group 时，才可分别形成内容单元；
7. CONTEXT_ONLY 不形成 CandidateContentUnit；
8. DROP 不形成、支持或恢复 CandidateContentUnit。

### 2.3 EpisodeGroupSignature / 候选组签名

用于防止相邻关系逐步漂移成全天主题集合。至少包含：

- 当前安全的 Episode basis；
- grounded activity / progression；
- Context Motif 与少量结构化视觉语义；
- capture time、真实 gap 与可信 locality；
- 匿名 entity/object continuity；
- support、contradiction、member 与 provenance。

只有已经进入当前 Candidate 的 content member 才更新 EpisodeGroupSignature。新 Moment 必须同时通过局部关系、group-wide compatibility 与 material-gain gate，不能只因与前一个 Moment 相似就无限链式扩张。

### 2.4 GateDecision

每个必要 gate 只能返回：

~~~text
PASS
NEEDS_VALIDATION
FAIL
~~~

- `PASS`：当前 Evidence 已足够；
- `NEEDS_VALIDATION`：基础 Evidence 已成立，只剩一个局部、明确、允许范围内可解决的问题；
- `FAIL`：硬条件不成立，或缺失无法在允许 Evidence 范围内可靠解决。

Chapter/Aha 的 Memory Value Gate 在 V1 只允许 `PASS / FAIL`。S08 可以核查事实、关系、时间变化或结构化媒体多样性，但不能为一个价值不足的 Candidate 创造主观价值。

### 2.5 CandidateDisposition

每个 materialized hypothesis 必须恰好具有一个当前 Revision 的 disposition：

~~~text
ELIGIBLE
PROVISIONAL_VALIDATION_REQUIRED
SUPPRESSED_DUPLICATE
REJECTED
~~~

解析优先级：

1. 合同无效或任一不可验证的硬门 FAIL → `REJECTED`；
2. 其余硬门可成立，但当前 Evidence 已证明与保留 Candidate 重复或被支配 → `SUPPRESSED_DUPLICATE`；
3. 无 FAIL，至少一个允许验证的 gate 为 NEEDS_VALIDATION，且具有合法 ValidationQuestion → `PROVISIONAL_VALIDATION_REQUIRED`；
4. 其余情况 → `ELIGIBLE`。

Duplicate 不能掩盖 Evidence 不足。一个 REJECTED Candidate 可以把 duplicate 保存为 secondary reason，但不能因此改成 SUPPRESSED。

### 2.6 SeedAuditRecord

Seed universe 只包含 S06 明确输出的 content-active shared candidate seed。每个 seed 恰好一条：

~~~text
seed_id
originated_candidate_ids[]
participated_candidate_ids[]
no_candidate_reasons[]
~~~

- `originated_candidate_ids`：该 seed 作为 owner 创建的 SINGLE、group 或 Aha；
- `participated_candidate_ids`：该 seed 作为内容成员加入、但由更早 seed owner 创建的 group；
- 两个列表引用所有已经 materialize 的 hypothesis，不论其 disposition；
- 两个列表均为空时，必须至少一个 `no_candidate_reason`；
- 任一列表非空时仍可记录其他 route 未产生候选的原因，但不能把 seed 总体误记为无候选；
- context-only 与 output-inactive Moment 没有 content seed，继续使用 S06 route audit。

## 3. 输入与不可越权边界

S07 只读取同一 immutable Revision 中：

- S04 Observation facts、status、support、UNKNOWN 与 limitations；
- S05 Moment membership、ordinary/Transition type、capture time、gap、Signature 与 ledger refs；
- S06 KEEP/CONTEXT_ONLY/DROP role、reason、candidate route 与 duplicate refs；
- RawAsset/Window/Frame/source/media/capture provenance；
- pipeline、schema、taxonomy、model、prompt 与 parameter versions。

S07 禁止：

- 混用旧 Revision role 与新 Revision Moment；
- 改写 S04 facts 或 support grade；
- 改写 S05 membership、Core/Tail、seam、ledger 或 Transition type；
- 静默改写 S06 role；
- 用 CONTEXT_ONLY 生成内容事实、Claim、内容单元或精选计数；
- 恢复 DROP；
- 在本阶段生成 Narrative 或最终媒体决定。

若真实评测证明上游事实、边界或角色错误，必须在对应上游版本修正，不能让 S07 隐式绕过。

## 4. Candidate route

| S06 route | S07 route |
|---|---|
| ordinary content-active | Chapter + Aha eligibility |
| Transition content-active | Aha eligibility only |
| context-only Moment | Context Envelope only |
| output-inactive Moment | audit only |

Chapter path FAIL 不自动降级为 Aha。Aha 必须独立通过自己的 gate。

ChapterCandidate 只允许四种 form：

~~~text
SINGLE
ADJACENT_GROUP
RESUMED_EPISODE
LOCAL_EPISODE_GROUP
~~~

AhaCandidate 只表达一个 origin Moment 内的局部峰值。V1 不跨 Moment 合成 Aha。

## 5. Chapter 共用硬门

所有 ChapterCandidate 必须通过：

1. **Source Gate**：所有 content members 均为当前 Revision 的 ordinary content-active Moments；
2. **Truth Gate**：所有内容单元只引用允许的 KEEP grounded facts；
3. **Local Episode Gate**：能够谨慎表达一段局部经历，而不是全天主题；
4. **Coherence Gate**：不存在破坏核心 Episode 的强矛盾；
5. **Coverage Gate**：存在足够非重复内容支持未来 3–5 个精选位置；
6. **Memory Value Gate**：至少一个明确正向记忆价值理由，不是仅因“发生过”；
7. **Inference Risk Gate**：无需虚构地点、意图、人物关系、情绪或连续录像；
8. **Internal De-duplication Gate**：内容单元与 Candidate scope 未被重复虚增。

Manual intent 可以支持 memory value，但不绕过 Truth、Coverage、Coherence、Inference Risk 或去重。

### 5.1 Normal Chapter path

~~~text
distinct KEEP RawAsset count >= 3
AND non-redundant CandidateContentUnit count >= 3
~~~

三个近重复 RawAsset 去重后不足三个内容单元时，Coverage Gate 仍 FAIL。

### 5.2 Long-Manual exception path

为了避免误杀由一条长 Manual 视频承载的完整 Episode，允许：

~~~text
distinct KEEP RawAsset count = 1 or 2
AND at least one source is Manual Video
AND non-redundant CandidateContentUnit count >= 3
AND units come from temporally distinct Manual Windows
AND grounded content shows real progression / complementary facets
AND all other Chapter gates PASS
~~~

满足条件只得到：

~~~text
CandidateDisposition = PROVISIONAL_VALIDATION_REQUIRED
validation_target = MEDIA_DIVERSITY
LongManualDiversityConfirmationGate = NEEDS_VALIDATION
~~~

进入例外前，初步时间差异、grounding 与去重条件必须已经成立。S08 只更严格地确认同一长视频中的这些 Window 是否足以作为多个真实不同的内容位置；它不判断最终构图、美感或渲染。

- PASS：S08 另行输出 downstream-eligible ValidatedCandidate；
- FAIL/无法在允许 Evidence 内解决：S08 输出 rejected validation outcome；
- 未进入当前 S08 budget frontier：保留 provisional audit，不进入最终输出。

原 S07 Candidate 始终保持 provisional，S08 不回写其 disposition。

## 6. Chapter form

### 6.1 SINGLE

一个 ordinary content-active Moment 只有同时满足以下条件，才能独立形成 SINGLE：

- 单独通过全部 Chapter gates；
- 不依赖邻居补全核心 Episode；
- Context 只能限制解释，不能救活缺失内容；
- 自身足够理解、完整且值得作为一章。

### 6.2 ADJACENT_GROUP

两个或更多直接相邻的 ordinary content-active Moments 只有同时满足以下条件，才能形成 ADJACENT_GROUP：

- 中间没有其他 committed Moment；
- 除时间相邻外，至少一个独立 Episode link；
- 至少两个不重复 signal families 相互支持；
- 每个 member 至少贡献一个相关、非重复 CandidateContentUnit；
- 组合显著增加完整性、过程或理解，不只是增加 RawAsset 数；
- S05 seam 完整保留，不改写为 MERGE。

中间存在 Transition、context-only、output-inactive 或普通独立 Moment 时，不能标为 ADJACENT_GROUP，必须使用 RESUMED/LOCAL 规则或不组合。

### 6.3 RESUMED_EPISODE

表达同一具体活动主线被中断后恢复：

~~~text
A: activity thread
B: interruption Moment(s)
C: same activity thread resumes

content members = A + C
interruption refs = B
~~~

必要条件：

- A、C 为非相邻 ordinary content-active Moments；
- 最多跨越 2 个 committed intermediate Moments；
- locality/time anchor 与 activity/thread anchor 中至少两个独立 signal families 支持；
- C 有恢复同一具体主线的证据，不只是主题、建筑风格或 embedding 相似；
- B 完整保留为 interruption refs；
- 不声称 A 到 C 之间持续录像或活动从未停止；
- blocker、强矛盾或无支持长 gap 立即停止关系。

### 6.4 LOCAL_EPISODE_GROUP

表达同一次局部 outing、visit 或 occasion 中的多个不同小 Episode。

必要条件：

- content members 均为 ordinary content-active Moments；
- 存在安全、可核查的共同 occasion envelope；
- 不能仅以相同地点、视觉风格或泛化主题推断统一意图；
- 每个 content member 提供独特贡献；
- 中间非内容 Moment 明确记录为 interruption/context/blocker；
- Candidate span 是时间线上有界、可追溯的连续范围，不能从全天任意挑选相似 Moment。

LOCAL_EPISODE_GROUP 可以内部记录 resumed relation，但不能抹掉中断 Moment。

### 6.5 S07 relation label

~~~text
INCLUDED_COMPONENT
INTERRUPTION_REF
BLOCKER
~~~

这些 label 只描述当前 Candidate 关系，不是新的 S06 role，也不能反向改写 S05/S06。

## 7. 有界 relation nomination 与 group extension

V1.17 冻结当前版本化 Baseline：

~~~text
relation_nomination_forward_horizon = 8 committed Moments
resumed_intervening_moment_max = 2
unsupported_capture_gap_max = 30 minutes
group_member_safety_max = 12 content members
~~~

规则：

1. “8”限制一个 seed 主动寻找非相邻 relation hypothesis 的 forward horizon，并按 committed Moment 的时间线位置计数；
2. 已成立的 adjacent/local group 可以逐个向后扩展到 horizon 之外；
3. 每次扩展必须同时通过 local relation、EpisodeGroupSignature compatibility 与 material-gain gate；
4. 不能只靠 pairwise similarity 做传递链；
5. 达到 12 content members、blocker、group drift 或超过 30 分钟无有效 Evidence gap 时立即停止；
6. interruption/context/blocker refs 不计入 12 个 content members，但所有被跨越的 committed Moments 必须出现在 span trace；
7. 达到范围上限记录 `SCOPE_LIMIT_REACHED`，尾部 Moment 可独立提名，不能静默消失；
8. capture gap 使用规范化 capture time，不使用 import/Sync time；
9. capture time 缺失不能证明连续。

这些数字是已冻结的 V1.17 执行 Baseline，不是永久自然常数。未来调整必须以真实 Benchmark、版本化参数和新 Checkpoint 显式重开。

## 8. Aha Candidate

### 8.1 interval

每个 AhaCandidate 必须具有：

- exactly one `origin_moment_id`；
- exactly one KEEP `peak_window_id`；
- 可选紧邻 before/after support Window；
- 总计最多 3 个连续 eligible Windows；
- `latest.capture_end - earliest.capture_start <= 3 minutes`；
- 不跨 origin Moment，不跨 DROP。

eligible support Window 只允许 origin Moment 内紧邻 peak 的 KEEP，或明确为 non-claim 的 CONTEXT_ONLY。Peak 本身必须是 KEEP。DROP、FAILED 或跨 Moment Window 不进入 interval。

支持 Window 是理解范围，不是三个最终媒体。S10 最终只选择一个 Aha EvidenceAnchor。

### 8.2 LocalPeakGate

至少存在一种：

- 当前 Window 多帧直接支持可观察变化；
- 相对当前 Moment Core 出现明确的新动作、人物、对象或短暂现象；
- 存在具体、短暂、可独立定位的互动、动作、结果或自然现象。

motion、embedding change、scene change、Manual intent、漂亮画面或 Live Photo 适配性只能提名，不能单独 PASS。

若已有可靠主体/场景与强局部事件提示，只差一个允许范围内可核查的动作事实，LocalPeakGate 可以 NEEDS_VALIDATION。只有 motion、blur 或 UNKNOWN 时必须 FAIL。

### 8.3 IndependentMemoryValueGate

Aha 必须：

- 可独立理解；
- 具体而非普通活动；
- 适合由单一局部 Anchor 表达；
- 删除后会丢失一个不同的互动、变化、现象或重要细节；
- 不是对 Chapter 完整 Episode 的简单缩写或摘要。

Aha 可以发生在 Chapter 内，但必须表达一个可独立定位的局部事件。Manual intent 可以支持个人相关性，但不能单独通过。

IndependentMemoryValueGate 在 V1 只能 PASS/FAIL，不能 NEEDS_VALIDATION。S08 不创造主观价值。

### 8.4 数量限制

~~~text
ordinary origin Moment
→ at most 3 non-overlapping Aha Candidates

Transition origin Moment
→ at most 1 Aha Candidate
~~~

Transition Aha 只能依赖自身 KEEP，不能借左右 Moment 补全。边界不明确本身不是 local peak 或 memory value。

多个 interval 指向同一具体事件时进入 duplicate group，不因 Window/Frame 数不同而重复计数。

## 9. Candidate duplicate 与 alternative

### 9.1 S07 duplicate scope

S07 只比较同一局部 Episode/event 的 Candidate：

- 完全相同 Candidate；
- 同一 Memory basis 的不同生成方式；
- nested scope 中没有新增意义的 dominated Candidate；
- 同一具体 peak 的多个 Aha。

跨较长时间、不同 Episode 的相似生活内容不能仅因 embedding、scene、object 或 style 相似被 S07 判重。全天集合冗余属于 S09。

### 9.2 S08 前 suppression

只有以下情况可直接 `SUPPRESSED_DUPLICATE`：

- identity/refs/basis 完全相同；
- 当前 Evidence 已证明两个 Candidate 表达同一 Memory；
- 当前 Evidence 已证明较大 scope 没有新增内容、价值或完整性；
- representative selection 不依赖尚未执行的 validation。

若差异需要 S08 才能确认，保留相关 Candidate 并加入 `alternative_hypothesis_group_id`。

- 若 alternative 成员各自事实与价值已足够，无论最终选哪个都可独立使用，可以保持 ELIGIBLE，把集合取舍留给 S09；
- 若只有解决 relation/dominance 后才能安全决定下游资格，相关成员必须具有 `AlternativeResolutionGate = NEEDS_VALIDATION`，成为 provisional，并共享一个局部 ValidationQuestion；
- 没有 NEEDS_VALIDATION gate 的 ELIGIBLE Candidate 不得偷渡 S08。

suppressed alternate refs 只用于 provenance，不得：

- 扩张 retained Candidate 的事实；
- 增加 CandidateContentUnit/RawAsset count；
- 增加精选媒体资格；
- 改变 source Moment membership。

### 9.3 Representative priority

1. grounded Evidence 更可靠；
2. Episode/peak basis 更具体；
3. inference risk 与 limitations 更少；
4. 非重复内容覆盖更充分；
5. 已足够时 scope 更小；
6. 完全相同时使用稳定 deterministic tie-break。

S07 不比较最终构图、美感、音效或渲染质量。Manual 不自动获胜。

## 10. Candidate 与 seed audit

每个生成过的 hypothesis 必须有 CandidateAuditRecord，至少保存：

- Candidate ID、type、Revision 与 snapshot；
- source/owner/participant Moment IDs；
- CandidateContentUnit、RawAsset、Window、Frame 与 fact refs；
- context/interruption/blocker refs；
- 每个 gate 的 PASS/NEEDS_VALIDATION/FAIL；
- 唯一 CandidateDisposition；
- primary reason 与 secondary reasons；
- duplicate/alternative/representative refs；
- limitations、contradictions、versions 与 provenance。

最低 reason families：

~~~text
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
~~~

Revision mismatch、未知 ID、越权 Evidence 等是合同错误，不能伪装成普通质量拒绝或 EMPTY_DAY。

## 11. Candidate 数量与成本

### 11.1 per-seed cap

~~~text
ordinary content-active seed:
  owned SINGLE Chapter Candidate <= 1
  owned grouped Chapter hypotheses <= 2
  origin Aha Candidates <= 3

Transition content-active seed:
  Chapter Candidate = 0
  origin Aha Candidate <= 1
~~~

Group 只由时间线上最早的 content member owner 创建；其他 member 通过 `participated_candidate_ids` 引用。S07 不枚举 AB、BC、ABC 等全部组合。

达到 cap 必须记录：

~~~text
AHA_SEED_CAP_REACHED
GROUP_HYPOTHESIS_CAP_REACHED
~~~

同时保存未 materialize hypothesis 的最小 Evidence refs。Cap 截断不是 gate FAIL，不能静默忽略。

### 11.2 不设全天 S07 editorial Top-K

Candidate pool 不因最终页面只有少量 Memory 而提前截成全天 Top-K。工程异常 safety limit 必须：

- 记录 `SAFETY_LIMIT_REACHED`；
- 不静默删除；
- 测量被截断类型与 regret；
- 只有真实数据证明需要时才版本化调整。

### 11.3 S07 默认成本合同

S07：

- 使用缓存的 S03/S04/S05/S06 结构化数据与现有 embedding；
- 只做 deterministic/lightweight local comparison；
- 不增加 VLM/strong-model 调用；
- 不上传新媒体；
- 不补取 Auto `UPLOAD_1` 的另外两帧；
- 不请求完整 Auto/Manual Raw；
- 不等待下一次 Sync；
- 不做全天 O(n²) all-pairs 或任意子集枚举。

至少记录：seed count、comparison count、candidate count by type/disposition、duplicate ratio、scope stop、cap hit、cache hit、CPU time 与 S08 handoff count。

五小时高强度参考日的容量推导不是产品配额：

~~~text
28 committed Moments
→ 20 ordinary content-active
→ 2 Transition content-active

gate 前 Candidate hypothesis theoretical max = 122
bounded forward relation comparisons at horizon 8 <= 188
S07 new Cloud media upload = 0
S07 new model call = 0
~~~

真实成本瓶颈预期位于 S08 enrichment 与 S10 HQ/render，不能用此推导代替真实 telemetry。

## 12. S08 admission 与 handoff

### 12.1 route

- `ELIGIBLE`：进入 S09 可用的 downstream pool，不消耗 S08 validation frontier，也不冒充经过额外验证的 ValidatedCandidate；
- `REJECTED`：不进入 S08/S09；
- `SUPPRESSED_DUPLICATE`：不进入 S08/S09；
- 无明确、可解决 ValidationQuestion 的 provisional：改为 REJECTED；
- 合法 provisional：可申请进入有界 S08 frontier。

### 12.2 admission condition

只有 `PROVISIONAL_VALIDATION_REQUIRED` 可以申请 S08，并至少满足一种：

- validation 可决定该 Candidate 的 downstream ELIGIBLE/REJECTED 资格；
- validation 可解决 alternative group relation/dominance；
- validation 可确认 Long-Manual MEDIA_DIVERSITY；
- validation 可确认已有可靠主体/场景基础的具体 local peak。

同时必须：

- 已通过独立 Memory Value 初筛；
- 没有更可靠、等价且已 ELIGIBLE 的 Candidate；
- 问题局限在 Candidate 自身允许 Evidence 范围；
- 不违反既有 upload/no-refetch 合同。

这不是 S09 Top-K，也不宣称已知道最终集合。

### 12.3 count guardrail

~~~text
Preview Revision S08 frontier <= 3 Candidates
Final Revision S08 frontier <= 8 Candidates
~~~

这是 Candidate 数量 guardrail，不是模型调用数、Token 或美元预算。

未进入 frontier 的 provisional Candidate：

- 保持当前 Revision provisional audit；
- 记录 `NOT_ADMITTED_BUDGET` 或其他原因；
- 未验证不能进入最终输出；
- 不用于凑 Chapter/Aha 数；
- 新 Revision 可以重新评估。

### 12.4 ValidationQuestion minimum contract

- candidate/revision/snapshot refs；
- target gate；
- 一个具体 unknown 或 contradiction；
- current grounded support；
- allowed Evidence/modality/time scope；
- explicitly disallowed source/refetch；
- PASS/FAIL 各自产生的 downstream eligibility/resolution；
- expected cost class、versions 与 provenance。

S07 不选择 provider。S08 返回新的 ValidatedCandidate、AlternativeResolution 或失败 outcome，不回写 S07/S06/S05/S04。原 S07 Candidate disposition 保持不可变。

## 13. Revision、ID 与 lineage

- 每个 Candidate instance 属于且只属于一个 immutable Revision；
- same snapshot + same inputs + same versions 必须确定性复现；
- `candidate_instance_id` 是 Revision-scoped，提交后不可修改；
- fingerprint 至少包含 ordered Evidence refs、roles、content units、relation edges 与 versions；
- fingerprint 不能只依赖可能变化的 Moment ID；
- 新素材或 Late Data 创建新 Revision；
- 旧 Candidate 与 audit 保持不可变；
- 未变化 fingerprint 可以复用确定性计算结果或 cache payload；
- 跨 Revision 仍须生成/绑定当前 Revision instance 与 provenance，不得复用旧 instance identity；
- lineage 可以记录 `continues / expands / merges / splits / supersedes`；
- 用户可见 Chapter stable ID 属于 S09/publish，不由 Candidate ID 冒充。

## 14. 输出合同

S07 至少输出：

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

`ChapterCandidate[]/AhaCandidate[]` 只承载 ELIGIBLE 与 PROVISIONAL Candidate。CandidateAuditRecord 覆盖全部 hypothesis，包括 SUPPRESSED 与 REJECTED，并可派生 rejected-candidate audit 视图。

内容引用与 context 引用必须分离：

- content refs 只来自 KEEP；
- context refs 只做 non-claim 限制；
- DROP 只可出现在 audit/provenance；
- 同一 RawAsset 的多个 Window 保留 source offsets；
- 不生成 title、story、hero 或最终 Claim。

## 15. Validator 不变量

提交 S07 输出前至少验证：

1. 所有引用属于同一 Revision/snapshot；
2. 所有 Chapter content members 为 ordinary content-active；
3. Transition 没有进入 Chapter content；
4. 每个 Aha 只有一个 origin Moment 与一个 KEEP peak Window；
5. Aha interval 不超过 3 eligible Windows/3 minutes，不跨 Moment 或 DROP；
6. CONTEXT_ONLY 没有生成 CandidateContentUnit、Claim 或媒体计数；
7. DROP 没有被恢复；
8. Normal Chapter 同时满足 RawAsset 与内容单元门；
9. Long-Manual exception 的 S07 Candidate 始终 provisional，并具有 MEDIA_DIVERSITY ValidationQuestion；
10. RESUMED 没有跨越超过 2 个 intermediate Moments；
11. relation nomination 没有越过 8-Moment horizon；
12. group 没有超过 12 content-member safety cap；
13. group 每次扩展具有 local、group-wide 与 material-gain trace；
14. 每个 content-active seed 恰好一个 SeedAuditRecord；
15. 每个 hypothesis 恰好一个 CandidateDisposition；
16. PROVISIONAL 必须具有合法 ValidationQuestion；
17. suppression 不依赖尚未运行的 validation；
18. alternate refs 不增加 retained Candidate 内容；
19. Preview/Final S08 frontier 分别不超过 3/8；
20. 输出没有 Narrative 或最终媒体决定；
21. S07 没有新增 upload/refetch/model call；
22. same input/version 可确定性复现；
23. Memory Value Gate 没有以 NEEDS_VALIDATION 进入 S08；
24. 跨 Revision cache reuse 没有复用旧 Candidate instance identity；
25. REJECTED/SUPPRESSED 没有出现在下游可选 Candidate 数组，但具有 CandidateAuditRecord；
26. S08 request/outcome 没有回写 S07 Candidate disposition；
27. 需 S08 解决的 alternative member 具有 AlternativeResolutionGate，不存在无 gate 的 ELIGIBLE Candidate 偷渡验证。

## 16. 典型行为

### 16.1 古镇—奶茶—古镇

~~~text
A: 古镇步行
B: 奶茶店
C: 继续古镇步行
~~~

- A↔C 可在具体主线恢复证据成立时形成 RESUMED，B 为 interruption ref；
- A+B+C 可在 B 对同一次 outing 有独特贡献时形成 LOCAL group；
- 两者表达不同 Memory basis 时可进入 alternative group；
- B 普通喝饮品不自动成为 Aha；
- 所有 S05 seams 保留。

同一 owner 最多 materialize 2 个 grouped hypotheses。Nested alternative 因 cap 未 materialize 时必须记录 GROUP_HYPOTHESIS_CAP_REACHED；只有已证实 dominated 时才允许 suppression。

### 16.2 120s 家庭表演视频 + 一张照片

- distinct RawAsset = 2；
- 至少 3 个 Manual Windows 提供时间与内容差异时，可走 Long-Manual exception；
- S07 Candidate 保持 provisional，S08 验证 MEDIA_DIVERSITY；
- 不因 RawAsset < 3 直接拒绝完整 Chapter；
- 一个具体谢幕、吹蜡烛或拥抱 peak 可独立提名 Aha。

### 16.3 一个演唱会 Moment 内多个峰值

- 一个 SINGLE ChapterCandidate；
- 最多三个互不重叠、分别通过 Aha 双门的 Candidate；
- 同一事件的多 Window 合并为一个 Aha；
- 第四个合格 peak 必须记录 AHA_SEED_CAP_REACHED；
- S09 全天最终仍最多选择三个 Aha。

### 16.4 相似的上午与晚上遛狗

- 长时间分离、不同 Episode 的两次活动不因 scene/activity/embedding 相似而在 S07 grouping 或 duplicate；
- 两个 SINGLE 可以同时进入 S09；
- 全天展示冗余由 S09 决定。

## 17. 状态边界

### FROZEN

- Candidate、CandidateContentUnit、GateDecision、CandidateDisposition 与 SeedAuditRecord 语义；
- Chapter 四种 form 与所有共用硬门；
- Normal Chapter 与 Long-Manual exception；
- RESUMED/LOCAL 的局部证据、interruption 与不改写 S05 原则；
- Aha 单 origin、单 KEEP peak、最多 3 Window/3 分钟、双门与普通/Transition cap；
- candidate duplicate 只处理局部 Memory，全天冗余留给 S09；
- 只有已证实 duplicate/dominance 可在 S08 前 suppression；
- alternative resolution gate 与 S08 不回写；
- per-seed cap、无全天 S07 Top-K、cap/scope truncation 必须留痕；
- relation horizon 8、resumed intermediate 2、unsupported gap 30 分钟、group member 12 的 V1.17 versioned Baseline；
- S08 Preview 3/Final 8 Candidate count guardrail；
- S07 不新增 upload/refetch/model call；
- immutable Revision、fingerprint、audit 与 Validator 不变量。

### OPEN / 待真实数据或后续阶段

- 12-member cap 的 truncation regret 与 false-group risk；
- 30 分钟 unsupported gap 的 missed-continuity regret；
- ordinary seed Aha cap=3 与 grouped hypotheses cap=2 的 cap-hit/truncation regret；
- CandidateContentUnit similarity/semantic-gain threshold；
- Long-Manual MEDIA_DIVERSITY validator；
- unresolved alternative ratio 与 dominance validation lift；
- S08 action-weight、Token、媒体暴露、Revision/day/monthly cost budget；
- S09 scoring、set-level overlap 与 final quota enforcement；
- S10 最终媒体质量、同一长 Manual 多 Anchor 可用性与渲染；
- Production JSON Schema、reason taxonomy、fingerprint/lineage matcher；
- 不同用户、生活方式与拍摄质量分层 Benchmark；
- 16s、73s 等非标准 Manual Window 仍是 S02 OPEN，不由 V1.17 补定。

OPEN 意味着参数未来可以通过 Benchmark 显式重开，不意味着 Production 可以静默漂移。

### IMPLEMENTATION GAP

- 当前没有 Production S07 engine、schema、validator、persistent audit 或 lineage matcher；
- X01 仍是一轮实验调用，不是本检查点定义的分阶段 S07；
- 当前没有真实用户标签证明 Candidate precision/recall；
- S08/S09/S10 尚未按本交接合同实现；
- 本检查点是算法架构冻结，不是 Production readiness 声明。

## 18. 复核证据

V0.1 使用 13 类高概率用户时间轴发现 F1–F8，其中 F1–F7 在 V0.2 修正，F8 正确保留给 S08。

V0.2 对 P01–P13 复跑后未发现新的 S07 结构性 blocker：

- P03 通过 Long-Manual provisional path 避免低 RawAsset 误杀；
- P06 保留 30 分钟 gap 的 precision-first 取舍与 regret trace；
- P08 允许第三个真实峰值，并审计第四峰值截断；
- P10 允许已成立 group 在逐步三门检查下扩展到第 8 个 Moment 之外；
- P13 在 28 committed Moments 的偏高假设下仍为有界轻量计算。

本复核没有生成图片、运行真实视觉模型或使用真实用户标签，因此只证明合同内部一致与容量边界，不证明真实效果。
