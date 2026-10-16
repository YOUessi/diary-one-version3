# S10-A2 EvidenceAnchor — Internal Cross-check V0.1

**状态：** CROSS-CHECK PASSED / REFINEMENTS APPLIED / S10 FROZEN BY CANONICAL V1.21
**检查日期：** 2026-08-27
**被检对象：** `S10_EVIDENCE_ANCHOR_MEDIA_EDITORIAL_CONSOLIDATED_WORKING_V0_1.md` 的 A2.1–A2.3
**上游合同：** V1.19 `S10HandoffEnvelope`、V1.3/V1.4 Evidence、V1.0 Anchor-first

## 1. 检查范围

本检查只验证：Anchor eligibility、Representative Evidence shortlist、Primary/Fallback、source readiness、Chapter/Aha floor、Revision immutability 与 no-substitution 边界。

不决定 PHOTO/LIVE_2S/VIDEO_5S、不决定 Chapter 3–5 set、不请求 HQ、不讨论 S09 re-selection。

## 2. 通过项

1. Anchor-first 未被媒体格式反向改写；
2. KEEP/CONTEXT_ONLY/DROP 与 S09 whitelist 权限一致；
3. Frame/Still/Interval 三类目标与 V1.3/V1.4 静态 Evidence 边界兼容；
4. 静态帧不能伪造连续动作；
5. 每 Beat 唯一 Primary、最多两个同 Beat Fallback 与 shortlist 1–3 一致；
6. Aha Fallback 不得使用相邻漂亮画面冒充 peak；
7. `UNRESOLVED` 与已证明 `NO_USABLE` 分开；
8. FallbackActivation 不改写旧 attempt；
9. A2 失败不删除事实、不换 Memory、不搜索全天；
10. A2 不新增模型、Raw/HQ 上传或 Auto 补帧。

## 3. Applied Refinement F1｜BeatAnchorRequirement

### 3.1 问题

A2.2 已定义候选评价维度，但尚未显式冻结“每个 Beat 哪些 grounded facts 是 Anchor 必须直接表达的核心”以及“该意义是否需要时序证据”。如果缺少这张要求卡：

- 不同候选可能分别针对 Beat 的不同侧面打分；
- `semantic_representativeness` 无统一比较对象；
- `temporal completeness / motion value` 可能偷偷变成媒体格式偏好；
- SAME 合并后的多个 ContentUnit 可能被错误地按全部事实 union，导致没有任何单 Anchor 能覆盖。

### 3.2 建议合同

~~~text
BeatAnchorRequirement
  beat_candidate_ref
  core_grounded_fact_refs[]
  optional_supporting_fact_refs[]
  evidence_mode_requirement =
    STATIC_SUFFICIENT
    | TEMPORAL_HELPFUL
    | TEMPORAL_REQUIRED
    | UNKNOWN
  semantic_floor
  derivation_refs[]
  limitation_refs[]
~~~

- `STATIC_SUFFICIENT`：一个可信静态位置可以真实表达 Beat；
- `TEMPORAL_HELPFUL`：静态已足够，动态可能增加体验价值；
- `TEMPORAL_REQUIRED`：核心 claim 是变化/过程，必须有时序 Evidence 才能完整表达；静态只能支持可见状态或结果；
- `UNKNOWN`：现有 grounded facts 不能判断，不能自动偏向动态。

Requirement 只能引用已有 grounded facts，不能生成新事实或用户可见文案。

### 3.3 SAME Beat 的核心

多个 ContentUnit 合并为 SAME Beat 时，core 必须是它们共同支持的展示贡献或已有明确代表关系，不能把所有 incidental facts 做 union。若找不到共同 core，说明 SAME 关系不成立或存在 relation conflict，应回到 A1 unresolved audit，不得靠 Anchor 评分掩盖。

### 3.4 案例

- “古建筑立面”：`STATIC_SUFFICIENT`；相机晃动不增加 motion value。
- “孩子跑向家人”：若 Beat 只表达“孩子来到家人身边”，可 `TEMPORAL_HELPFUL`；若核心是完整奔跑过程，则 `TEMPORAL_REQUIRED`。
- “吹灭蜡烛”：若核心 claim 是吹灭动作/火焰变化，则 `TEMPORAL_REQUIRED`；仅有熄灭后静态帧只能支持“蜡烛已熄灭”的结果，不得获得完整动作 representativeness。

## 4. Applied Refinement F2｜Resolution 不等于 HQ Ready

### 4.1 问题

A2.3 当前使用 `ANCHOR_READY`，但它允许 Primary source 为 `NOT_YET_MATERIALIZED`。这只能说明 Anchor 已经选定且 source 可请求，不能说明 HQ 已在云端或媒体可立即渲染。`READY` 容易被下游误读为 render-ready。

### 4.2 建议改名

~~~text
ANCHOR_RESOLVED
ANCHOR_RESOLVED_DEGRADED
ANCHOR_UNRESOLVED
NO_USABLE_ANCHOR
~~~

source readiness 继续独立保存：

~~~text
AVAILABLE
NOT_YET_MATERIALIZED
UNAVAILABLE
UNKNOWN
~~~

只有 S10-D/S13 的媒体请求与渲染合同才能声明后续 media/render readiness。

### 4.3 NO_USABLE reason 必须区分

~~~text
NO_ELIGIBLE_ANCHOR
ALL_PRESENTATION_UNUSABLE
ALL_SOURCE_UNAVAILABLE
AHA_CORE_PEAK_NOT_DIRECTLY_REPRESENTED
~~~

这些 reason 都不能解释为“事实没有发生”；它们只说明本次 S10 attempt 没有可用展示位置。

## 5. 案例矩阵

| Case | 输入重点 | 预期 A2 结果 | 检查 |
|---|---|---|---|
| C01 古镇牌坊 | 稍暗 core-direct vs 清晰 peripheral | core-direct Primary | PASS |
| C02 相似石板路 | 两个 SAME ContentUnit、多帧 | 一个 Beat、1 Primary、有限 Fallback | PASS |
| C03 古建筑静态 | motion amount 高、static 足够 | 不因晃动偏向 interval | PASS after F1 |
| C04 吹蜡烛 Aha | temporal interval + 合照 | interval 可选；合照不得 fallback | PASS |
| C05 只有熄灭后帧 | 无 temporal evidence | 只能支持结果，不能冒充动作 | PASS after F1 |
| C06 长 Manual | 多个已验证 Window | 各 Beat 只在本 Window 选 Anchor | PASS |
| C07 Preferred HQ unavailable | 同 Beat 有合格次优 | degraded resolution；保留 Preferred trace | PASS after F2 rename |
| C08 所有 source unavailable | 语义候选存在 | `NO_USABLE_ANCHOR/ALL_SOURCE_UNAVAILABLE` | PASS after F2 reason |
| C09 source unknown | 次优会造成实质语义损失 | `ANCHOR_UNRESOLVED` | PASS |
| C10 S13 Primary failure | 预声明 Fallback 存在 | 新建 FallbackActivation，不改旧 Primary | PASS |
| C11 Chapter 一个 Beat 失败 | 其他四个正常 | A2 只报告；S10-C 决定 set | PASS |
| C12 Aha 核心无 Anchor | 只有相邻漂亮画面 | 不替代；上报 no usable/unresolved | PASS |

## 6. 结论

A2.1–A2.3 主体架构一致，未发现需要推翻的路径。F1 `BeatAnchorRequirement` 与 F2 resolution 命名/reason refinement 已按确认落实；A2 已参加 S10-E 并由 Canonical V1.21 冻结。
