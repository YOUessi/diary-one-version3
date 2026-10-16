# S10-B Media Format & MediaDecision — Internal Cross-Check V0.1

**状态：** CROSS-CHECK PASSED / REFINEMENTS APPLIED / S10 FROZEN BY CANONICAL V1.21
**日期：** 2026-08-27
**被检查文档：** `S10_EVIDENCE_ANCHOR_MEDIA_EDITORIAL_CONSOLIDATED_WORKING_V0_1.md`

## 1. 检查范围

本检查覆盖：

~~~text
S10-B1  Media Format Eligibility
→ S10-B2  Preferred Media Format
→ S10-B3.1 Exact Media Source Plan
→ S10-B3.2 Fallback Route / Failure Routing
→ S10-B3.3 MediaDecision / S10-C Handoff
~~~

本检查不决定 Chapter 最终 3–5 set、Hero、排序、Aha supporting item、HQ 预取策略、S13 重试次数或 S09 re-entry，也不调用模型、上传媒体或执行渲染。

## 2. 核心检查问题

1. 是否始终 Anchor-first，格式不能反向改变 Beat 或 Memory；
2. PHOTO/LIVE_2S/VIDEO_5S 资格是否保持 Chapter/Aha 边界；
3. 最小充分媒体是否真正阻止无价值动态；
4. 精确区间是否可执行、合法且不越出 Evidence scope；
5. 已知不可执行与未来 runtime failure 是否严格分离；
6. format、anchor、source、policy failure 是否不会互相误判；
7. Conditional Route 是否有真正可执行的安全 Fallback；
8. Primary + Fallback 是否仍只计一个媒体候选；
9. Aha peak 是否不会被准备/结果画面替代；
10. 多 Route 与跨 Beat collision 是否显式记账；
11. Fallback activation 是否不可变、有限且不触发新搜索；
12. 是否仍保持无新模型、无 HQ 媒体传输的成本边界。

## 3. 检查方法

每个案例沿同一链路逐项推演：

~~~text
AnchorResolution
→ MediaFormatEligibility
→ PreferredMediaFormatDecision
→ ExactMediaSourcePlan
→ Primary/Fallback Routes
→ MediaDecision state
→ S10-C counting effect
~~~

UNKNOWN、INFEASIBLE、terminal failure 与 input invalid 分开测试；没有使用一个总分替代合同判断。

## 4. 发现并已应用的 Refinements

### F1｜Known degradation 后必须重建实际 Route list

**风险：** preferred Route 已知不可执行、旧 Fallback 被提升为 Primary 后，如果仍保留原来的 `change_kind_from_primary` 与顺序，会产生相对错误的 activation 路由。

**修正：** 首次定稿前先排除 known-infeasible Route；关键 UNKNOWN 能改变 Primary 时停止为 unresolved；否则隔离 unresolved fallback-only candidate。随后选择实际 Primary，并相对实际 Primary 重新计算其余 Fallback order/change kind，同时保留原 preferred trace。

### F2｜Content consistency failure 必须区分 format 与 anchor scope

**风险：** 动态周边与预期不符但 focal frame 仍有效时，若误判为 Anchor failure，会不必要地淘汰 PHOTO；反之，Anchor 本身映射错误若只判 format failure，会保留错误内容。

**修正：** focal core 仍 grounded 时为 format-level；focal core/provenance 本身被推翻时为 anchor-level。

### F3｜Fallback coverage 不能使用模糊布尔值

**风险：** 同 RawAsset PHOTO Fallback 只覆盖动态格式失败，不能覆盖 source 丢失，却可能被误解为“已有完整容灾”。

**修正：** 增加 `NO_FALLBACK_COVERAGE / FORMAT_FAILURE_COVERED / ANCHOR_FAILURE_COVERED / SOURCE_FAILURE_COVERED / MIXED_FAILURE_COVERAGE`。只有不同 source failure domain 才可声明 source coverage。

### F4｜Primary collision 与 activation-time collision 必须分开

**风险：** 两个 Beat 的 Primary 不重复，但各自 Fallback 指向同一个 Frame；若未来同时激活，可能生成两个重复媒体项。

**修正：** `route_collision_matrix_ref` 区分 `PRIMARY_PRIMARY / PRIMARY_FALLBACK / FALLBACK_FALLBACK`。Primary collision 是 S10-C hard conflict；其余为 S10-D activation-time conflict，必须显式解决，不能静默产生重复项。

### F5｜Non-conditional 不等于 HQ 已经存在

**风险：** “非条件 Fallback”可能被工程误读为文件已经下载或绝不会失败。

**修正：** non-conditional 只表示不依赖额外动态 content/stability 验证；source 仍可为合法 `NOT_YET_MATERIALIZED`，source-level 风险继续保留。

### F6｜Unresolved fallback-only candidate 不应无条件阻断健康 Primary

**风险：** 一个不影响当前 Primary 的可选备用 Route 为 UNKNOWN，如果让整个 MediaDecision unresolved，会不必要地降低可选容量。

**修正：** UNKNOWN 若可能改变实际 Primary，decision unresolved；若只影响额外 fallback coverage，则隔离该 Route、记录 limitation，健康 Primary 仍可 resolved。

## 5. 案例矩阵

| ID | 场景 | 预期合同结果 | 结果 |
|---|---|---|---|
| C01 | Manual Photo 清晰表达古建筑立面 | PHOTO eligible/preferred；单一 resolved Route；计 1 | PASS |
| C02 | 视频 Frame 清晰，周边只有手抖 | PHOTO 充分；motion amount 不升级为动态 | PASS |
| C03 | 2 秒内孩子完成挥手 | LIVE_2S material；5 秒无额外价值；选更短动态 | PASS |
| C04 | 拉坯必要短过程约 4 秒 | Chapter VIDEO_5S；区间覆盖起点/推进/结果 | PASS |
| C05 | 9 秒 Auto Anchor 位于 0.4s / 8.7s | `[0,2]` / `[7,9]`；不出现负时间或 padding | PASS |
| C06 | Evidence 支持范围只有 1.4 秒 | LIVE_2S source plan infeasible；不得向未知两侧扩张 | PASS |
| C07 | 全部必要阶段横跨 7 秒 | VIDEO_5S 不可执行；不加速、不拼接；检查合法降级 | PASS |
| C08 | Conditional LIVE + 同 Anchor resolved PHOTO | decision conditional；计 1；coverage 仅 format-level | PASS after F3/F5 |
| C09 | Conditional LIVE 无合格 Fallback | decision unresolved；不计入 S10-C | PASS |
| C10 | LIVE 周边动作不符，但 focal Frame 仍正确 | format failure；同 Anchor PHOTO 可继续 | PASS after F2 |
| C11 | Anchor timestamp/provenance 本身错误 | anchor failure；同 Anchor 全部格式失效 | PASS after F2 |
| C12 | 两个 handle 实际属于同一损坏 RawAsset domain | source failure 同时淘汰；不得伪称 source coverage | PASS after F3 |
| C13 | Aha LIVE 失败，PHOTO 只有吹灭后结果 | PHOTO 不直接表达 peak；禁止回退；media unresolved | PASS |
| C14 | 一个 Beat 有 Primary + 2 Fallback | 三条 Route 合计仍计一个 MediaDecision | PASS |
| C15 | unresolved alternative group 内两个 resolved MediaDecision | S10-C 最多选择一个 | PASS |
| C16 | 两个 Beat Primary 指向同一 canonical Frame | PRIMARY_PRIMARY hard conflict；最多选择一个 | PASS after F4 |
| C17 | 两个 Beat 只有 Fallback 指向同一 Frame | 记录 activation conflict；不提前增加数量 | PASS with S10-D obligation |
| C18 | 单次网络超时 | transient；S13 有界重试前不激活 Fallback | PASS |
| C19 | preferred VIDEO 已知 infeasible，PHOTO 合法 | PHOTO 直接成为 degraded Primary；Route 相对关系重建 | PASS after F1 |
| C20 | Revision/allowlist/policy version 不一致 | input invalid、fail closed | PASS |
| C21 | Primary resolved，额外 fallback candidate UNKNOWN | 不影响 Primary 时隔离备用 Route并记录 coverage limitation | PASS after F6 |
| C22 | Primary 和全部预声明 Fallback terminal failed | fallback exhausted；不生成第四 Route、不搜索全天 | PASS |

## 6. 数量膨胀专项模拟

一个 Chapter 的 Beat/MediaDecision 状态如下：

~~~text
Beat-A  resolved PHOTO                         → raw selectable 1
Beat-B  conditional LIVE + PHOTO fallback     → raw selectable 1
Beat-C  resolved VIDEO + two fallbacks         → raw selectable 1
Beat-D  resolved PHOTO, alternative-group G    → raw selectable 1
Beat-E  resolved LIVE,  alternative-group G    → raw selectable 1
Beat-F  no usable media                        → raw selectable 0
~~~

原始 `s10c_selectable_refs` 为 5；alternative group G 最多贡献一个，因此在未考虑其他碰撞前，proven distinct upper bound 为 4。若 Beat-C 与 Beat-D 又存在 Primary canonical render collision，则 upper bound 进一步降为 3。

Primary/Fallback Route 总数、动态格式数量或 Anchor 数量均不能增加这个容量。

## 7. 成本与执行边界复核

- 每 Beat 最多一个 Primary 加两个 Fallback Route；
- B 阶段仅处理结构化 Evidence、refs、timestamps、状态与已有 signals；
- Conditional 只规划一个 provisional interval，不滑动重试；
- 不新增 VLM/strong-model 调用；
- 不上传、下载或请求 HQ source；
- 只有 S10-C 最终选中项才可进入 S10-D/S13 请求路径。

成本与工程复杂度边界通过。

## 8. 结论与下游义务

S10-B 合同在应用 F1–F6 后通过内部交叉检查，没有发现需要推翻 B1–B3 核心方向的问题。

本检查当时记录的下游义务现已处理为：

1. S10-C：Compact 2 / Standard 3–5、Primary collision、Beat coverage、Hero、顺序与长 Manual source occupancy 已由 V1.21 冻结；
2. S10-D：Fallback collision、HQ request tiers、presentation narrowing 传播与 Aha single media 已由 V1.21 冻结；
3. S10-E：全阶段交叉检查与画像模拟已通过；
4. S13：terminal 判定、有界 retry、实际 decode/render tolerance 继续 OPEN。

任意 16s/73s Manual 的上游 Window 规划继续 OPEN；本检查没有越权补定。
