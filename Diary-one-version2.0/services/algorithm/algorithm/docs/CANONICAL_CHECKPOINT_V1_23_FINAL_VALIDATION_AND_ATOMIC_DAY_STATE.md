# Diary One Canonical Checkpoint V1.23 — S12 Final Validation & Atomic Day State

**状态：** FROZEN
**冻结日期：** 2026-08-29
**覆盖阶段：** S12A Pre-materialization Validation + S12B Activation/Export Validation
**继承：** V1.19–V1.22
**仓库边界：** 只定义算法验证、状态与发布接口；不修改 App、Firmware/SDK、共享状态文件或真实云数据库

## 1. 核心结论

S12 不是“最后再润色一下”的修理层，而是一个只读、确定性、可审计的发布法官。

它回答两个不同问题：

1. **S12A：** 当前 Revision 的 Memory、媒体计划、文字和索引在 HQ materialization 之前是否结构完整、语义合法？
2. **S12B：** S13 实际激活了哪些 route，所有受影响的 S11/S12 artifact 是否已重验，是否可以形成原子发布计划？

因此实际发布链冻结为：

```text
S09 selected membership
→ S10 active media plan + fallback/D1/D2 metadata
→ S11 verified narrative/index
→ S12A pre-materialization validation
→ S13A selected-HQ materialization
→ if activation delta: affected S11 revalidation
→ S12B activation/export validation
→ S13B atomic export/publish adapter
```

S12 不删除 Memory、媒体或 Claim，不生成替代文案，也不在 validator 里重跑 solver。失败必须返回真正 owner。

## 2. 为什么必须拆成两阶段

S10 已冻结：Primary 在 S13 才可能被证明 terminal，随后激活 Fallback、D1 survivor 或 Hero Alternate。这个变化可能影响：

- 可见格式；
- active source 与 presentation redundancy；
- Chapter 正文数量；
- Hero；
- 某些依赖媒体的 Claim；
- Title/Story/Tag 与实际媒体的一致性。

只在 S13 前验证一次，会让“验证通过的是旧投影、用户看到的是新投影”。只在 S13 后验证，又会浪费明显不合法计划的 HQ 成本。两阶段解决这个矛盾。

**案例：** 古镇 Chapter 的木雕 LIVE_2S terminal，S13 激活同一 Anchor 的 PHOTO Fallback。S12A 已证明该 Memory 与 Primary 计划合法；S13A 后，S11 只重验木雕相关媒体一致性；S12B 再确认数量、Hero、Claim 和 checksum。不能直接拿旧 S12A 结果发布。

## 3. S12A 输入与输出

### 3.1 输入

```text
CurrentRunEnvelope
S09ResultBundle
S10FinalMediaProjection
S10HQRequestManifest
S11NarrativeBundle
PriorPublishedHeadRef?
VersionedValidationPolicy
```

所有输入必须具有同一 `revision_id + snapshot_id + active_projection_fingerprint`。旧 Revision 的合法对象只能通过显式 continuity ref 进入，不能混入 current arrays。

### 3.2 输出

```text
S12PreMaterializationDecision
  revision_id / snapshot_id
  day_state
  gate_results[]
  exact S09/S10/S11 fingerprints
  materialization_scope[]
  expected_published_head
  decision
  owner_action?
  immutable fingerprint
```

合法 decision：

```text
MATERIALIZATION_ALLOWED
NO_MATERIALIZATION_EMPTY_EXPORT_ALLOWED
HOLD_RETRYABLE
OWNER_REPLAN_REQUIRED
BLOCKED_NO_SAFE_CURRENT_REVISION
VALIDATION_CONTRACT_INVALID
```

## 4. S12A 固定 Gate 顺序

Validator 按固定顺序运行；先失败的 gate 可以停止高成本后续检查，但 audit 必须说明未运行项。

### G01 Contract & Lineage

- schema、version、required refs 完整；
- S00–S11 均指向 current Revision/Snapshot；
- policy/model/parameter/taxonomy refs 可解析；
- fingerprint 没有自引用、stale 或混版。

失败：`VALIDATION_CONTRACT_INVALID`。

**案例：** S11 Story 来自 R6，但 S10 media plan 来自 R5。即使文字和画面看起来匹配，也不能发布。

### G02 Day State & Capacity

```text
CHAPTER_DAY   = 1–5 Chapter + 0–3 Aha
HIGHLIGHT_DAY = 0 Chapter + exactly 1 strong standalone Aha
EMPTY_DAY     = 0 Chapter + 0 Aha
```

3–4 Chapter 与 2–3 Aha 是丰富日目标，不是配额；第 5 Chapter 必须持有 S09 exceptional gate。

**案例：** 只有一个清晰求婚 Aha、没有完整 Chapter，可以是 HIGHLIGHT_DAY；不能为了“完整”把邻近通勤素材拼成 Chapter。

### G03 Membership & Candidate Eligibility

- 输出 IDs 与 S09 selected set 完全相同；
- 没有 REJECTED、SUPPRESSED、UNRESOLVED 或 operational-failure Candidate；
- S10/S11 没有静默补位或删除；
- bounded re-selection 若发生，必须是当前 Revision 唯一合法 batch 并有 lineage。

失败返回 S09/S10 owner；S12 不自行换 Candidate。

### G04 Chapter/Aha Narrative Independence

- 每个 selected Chapter×Aha pair 有 current V1.20 decision；
- same-story climax 不共选；
- embedded-distinct Aha 的 peak 从 Chapter narrative reservation 中排除；
- exact media reuse 不授权 exact Claim reuse。

**案例：** 生日 Chapter 已以吹蜡烛为高潮，吹蜡烛 Aha 不通过；古镇主线与独立奶茶插曲可以通过，但 Chapter 文案不能再把奶茶 peak 写成自身高潮。

### G05 Memory Scope & Evidence Roles

- Chapter/Aha content units 都属于原 Candidate scope；
- visible media 不来自 DROP；
- CONTEXT_ONLY 只限制/解释，不占最终可见位置；
- unresolved Transition 没有被偷渡为肯定事实；
- Anchor 指向合法 Evidence/Raw provenance。

### G06 Media Projection

Chapter：

- Standard 3–5；
- 只有 Compact Pair 全门通过时允许 2；
- Hero 恰好一个且来自正文集合；
- media format、chronology、source occupancy、Dominant Motif 与 D1/D2 metadata 合法。

Aha：

- 恰好一个可见 PHOTO/LIVE_2S；
- 无独立 Hero；
- route 全部绑定同一 peak；
- support/context 不能替代 peak。

### G07 Claim & Narrative

- 每个 required generated surface 已 `SURFACE_VERIFIED`，或拥有合法 explicit omission；
- Chapter Story 1–2 句且存在核心；
- Aha Moment Line 单峰、中文当前测试 ≤20 可见字符；
- Title、Time、Tags、Entity Links 分工正确；
- unsupported emotion/preference/causality/continuity 不存在；
- protected user text 未被覆盖；
- current active projection 与 narrative fingerprint 一致。

### G08 Canonical Index

- 每个 Memory 有 Tag Decision，即使结果为零；
- Concept 来自 current closed registry；
- 每 Facet 至多一项，最具体且被支持；
- exact entity 使用 Entity Link；
- Display Label 由 locale registry 派生；
- Tag 不声明 preference。

### G09 Cross-Memory Presentation

- Chapter 之间没有非法 Raw/content ownership 冲突；
- Chapter/Aha 重复遵守 V1.20/V1.21；
- necessary exact reuse 有显式 decision，consumer identity 分离、materialization 可共享；
- 同日 Title distinctness 与 narrative repetition 不制造错误替换。

### G10 Cost & Provenance

- provider/model/prompt/parameter/token/latency/retry/cache/cost 字段完整；
- S08 VBU 与实际美元口径不混用；
- visible consumer、render/materialization、unique HQ request、dormant fallback 分账；
- request count 不超过 current S10 manifest；
- 预算不足是 HOLD/BLOCK，不是 EMPTY_DAY。

### G11 Prior Publication Safety

- exact valid prior 可在 current 未完成时继续显示；
- prior 已因事实、Evidence、policy 或用户修正被撤销时不得 fallback；
- Preview/Final 状态真实，不把 Preview 自动标 Final；
- expected published head 在 plan 中冻结，避免并发覆盖。

### G12 Materialization Admission

- 只允许 S10 manifest 中 active requests；
- dormant fallback 只保留 metadata；
- source interval、format、Anchor、route priority 完整；
- EMPTY_DAY 不触发 HQ；
- validation pass 才允许 S13A 花费实际 materialization 成本。

## 5. S12 不执行静默修理

旧方向文档曾列出“删除不合法 Memory/媒体/Claim”。V1.23 正式收紧为：

> S12 只验证 exact immutable proposal；任何内容变化必须由 owner 产生新 artifact，再重新验证。

原因：validator 若一边裁剪一边通过，会隐藏产品规则、破坏 lineage，并可能导致媒体、文字和数量互相失配。

固定路由：

| 失败所有者 | 返回路径 |
|---|---|
| Candidate/membership/Day State | S09；仅用尚未消耗的合法 bounded path |
| Beat/Anchor/media set/Hero/route | S10 |
| Fact/Claim/content plan/wording/tag | S11 exact owner |
| transient HQ/render/storage | S13 retry/HOLD |
| schema/ref/fingerprint/CAS | engineering contract invalid |

**案例：** 五项古镇媒体中一项来自 CONTEXT_ONLY。S12 不删除后把四项直接发布；它返回 S10 `MEDIA_SCOPE_REPLAN_REQUIRED`。S10 只有在已有合法 exact projection 中才能重建，随后 S11/S12 重新运行。

## 6. S13A → S12B Handoff

S13A 返回：

```text
MaterializationReceipt[]
ActivationDelta[]
TerminalFailure[]
Checksum / timebase / render policy refs
actual cost / latency / retry
```

每个 `ActivationDelta` 必须列出：

- from/to route；
- affected Memory/media/Hero；
- source/format/scope 是否变化；
- 必须重验的 S11 surfaces；
- 必须重跑的 S12 gates；
- immutable parent refs。

无法准确计算 affected set 时，不允许假定“没有影响”，必须重验整个 Memory；contract ref 损坏则 invalid。

## 7. S12B Activation & Export Validation

S12B 固定检查：

1. S12A decision 仍 current；
2. 每个 active visible consumer 恰好一张成功 receipt；
3. checksum、format、source interval、Anchor 与 semantic scope 匹配；
4. fallback 只在 Primary terminal 后按预声明顺序激活；
5. transient/unknown 不得激活 Fallback；
6. D1 每 Chapter 最多一次且 exact survivor 已预验证；
7. D2 锁定健康 Primary，不为了去重牺牲更好合法媒体；
8. Hero Alternate 只来自预声明 ref；
9. affected S11 artifact 已在 active projection 上重验；
10. G02–G11 对 resulting projection 重新通过；
11. expected published head 未变化；
12. user export 与 internal audit 都可完整生成。

输出：

```text
S12ActivationDecision
  ACTIVATE_CURRENT_REVISION
  REUSE_STILL_VALID_PRIOR
  HOLD_RETRYABLE
  BLOCKED_NO_SAFE_REVISION
  ACTIVATION_CONTRACT_INVALID
```

`ACTIVATE_CURRENT_REVISION`只是发布授权，不是已经发布。S13B/publisher adapter 执行 CAS 后，才产生不可变 Commit Record。

## 8. Lifecycle 与原子性

### 8.1 可见性

- current Revision 全部通过前，不展示内部半成品；
- still-valid prior 可以继续显示；
- known-invalid prior 不得因“比空白好”继续显示；
- blocked 不等于 EMPTY_DAY；
- App 的“更新中/隐藏/错误”具体 UI 不由 S12 文案化。

### 8.2 CAS

发布计划保存：

```text
expected_published_head
current_revision_id
validated_export_fingerprint
audit_fingerprint
activation_decision_fingerprint
```

只有 compare-and-swap 成功才能更新 published head。失败返回 `STALE_PUBLICATION_ATTEMPT`，不覆盖更新的 Revision，也不修改已经生成的 immutable artifacts。

### 8.3 Preview / Final

Preview 和 Final 使用同一事实/媒体/文字硬门；区别只在生命周期、capacity 与 Finalization trigger。Final 不因时间到达而自动复用 Preview 的状态标签。

## 9. Failure Semantics

| 情况 | 状态 | 用户内容行为 |
|---|---|---|
| Provider 暂时失败，prior valid | HOLD / REUSE prior | 不生成替代事实 |
| Provider 暂时失败，无 prior | HOLD | 不伪装 EMPTY |
| Current Claim unsupported | owner replan/block | 不保留错误句 |
| HQ transient | HOLD_RETRYABLE | 不激活 Fallback |
| HQ terminal +合法 Fallback | activation delta→重验 | 通过后原子替换 |
| 所有 Aha routes exhausted | BLOCK/HOLD | 不用 support frame，不回 S09 |
| prior known invalid | BLOCKED_NO_SAFE_REVISION | 不继续显示 prior |
| CAS stale | STALE_PUBLICATION_ATTEMPT | 不覆盖新 head |
| 真实 EMPTY_DAY | empty export allowed | 0 Chapter/0 Aha，无 HQ |

## 10. 成本与效率

S12 两阶段均为结构化、确定性 validator，默认不调用 VLM/Writer、不读取 Raw、不请求新 HQ。

复杂度上界来自最终小集合：

- Chapter ≤5；Aha ≤3；
- visible body/Aha media ≤28；
- Chapter×Aha pair ≤15；
- S11 surfaces 与 tags 都是小型 arrays；
- activation 只重验 affected set，无法确定时才扩大到整个 Memory。

因此，两次 S12 不等于视觉处理做两遍；它用少量 metadata 检查换取发布安全。真实 P50/P95/P99 仍需部署 benchmark。

## 11. Canonical Cases

1. **三章两 Aha 丰富日：** 数量合法，但每对 Chapter/Aha 仍要独立决策；不能因数量漂亮跳过。
2. **五章：** 必须存在 S09 fifth gate；S12 不因“上限允许”自动接受。
3. **Compact Chapter：** 两项媒体只有 exact Pair Gate 全部通过才合法。
4. **Aha 两项媒体：** 直接失败；support 不能变第二个 visible item。
5. **古镇＋奶茶 Aha：** narrative-distinct pass 且 Chapter reservation 生效时可共存。
6. **生日＋吹蜡烛 Aha：** same-story climax，不能共选。
7. **Fallback 从 LIVE 变 PHOTO：** 同 Anchor/scope 也必须 affected revalidation。
8. **D1 删除一项：** 只有预验证 survivor、一次上限和最终数量/Story/Tag 全通过才可激活。
9. **Exact reuse：** 两个 consumer 可共享 materialization，但 Memory identity、Claim 与 audit 分离。
10. **English locale 未就绪：** 不套中文长度后发布；current Chinese 合法结果不受影响。

## 12. Frozen Invariants

1. S12A/S12B 两阶段；
2. S12 只读、不静默修理；
3. Day State 与数量精确匹配；
4. rich-day target 不变配额；
5. S09 membership 不被下游改变；
6. V1.20 pair coverage 完整；
7. S10 media scope/role/provenance 合法；
8. Chapter Standard/Compact 与 Aha single-media 合同保持；
9. 所有 user-visible Claim 已验证；
10. Canonical index 受控且可为零；
11. transient/operational failure 不等于内容失败；
12. runtime activation 必须有 immutable delta；
13. affected artifacts 必须重验；
14. known-invalid prior 不可 fallback；
15. CAS 之前不更新 published head；
16. stale publish 不覆盖新 Revision；
17. EMPTY_DAY 无 HQ；
18. validator 默认零模型调用；
19. cost/provenance 完整；
20. 用户只看到完整通过的 Revision。

## 13. OPEN / Implementation Boundary

- 真实数据库、队列、事务与 CAS 技术选型；
- App 对 known-invalid prior 的隐藏/更新中 presentation；
- locale-specific release profile；
- 真实 provider/media retry 时间、告警与 SLO；
- privacy、retention、deletion 与治理；
- 真实素材/用户标签下各 gate threshold 的校准。

这些是 Production 部署与产品验证工作，不改变 S12 的两阶段权限和原子性。

## 14. Freeze Record

S12 的详细合同至此冻结。V1.23 覆盖旧方向文档中“S12 可以现场删除不合法内容”的宽泛描述：从现在起，S12 只能接受 exact artifact、返回 owner 或阻断，不能一边修改一边宣称验证通过。
