# Diary One Canonical Checkpoint V1.11 — Contiguous Moment Segmentation Foundation

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** S05 Moment Formation 的连续分段、成员归属、稀疏时间语义与阶段边界
**继承关系：** 继承 V1.10–V1.1 与 V1.0 未被覆盖的规则

> **当前边界覆盖：** V1.12 已冻结每个相邻 seam 的 continuity/boundary 双向证据账本与四状态决策架构；本文关于信号融合架构仍 OPEN 的部分由 V1.12 覆盖，具体阈值和权重继续 OPEN。

> **当前 Signature 覆盖：** V1.13 已冻结多原型 Context Core/Tail/Pending 及 commit-on-MERGE；具体 prototype、Motif 和阈值继续由真实数据校准。

> **当前 unresolved transition 覆盖：** V1.14 已冻结证据用尽且不能可靠归左/归右时的内部 Transition Moment，以及 Aha 候选、CONTEXT_ONLY、DROP 三路后续边界。

> **当前 DEFER 覆盖：** V1.15 已冻结当前两条可用后续 Window、6 分钟、3 Pending 的版本化 Baseline、完整 seam pattern 提前结束、同快照解析与原子提交。

> **当前 S06 覆盖：** V1.16 已冻结唯一三角色与 candidate-empty 路由；没有 KEEP 只使 Moment 退出内容候选，不删除、重并或改写本文的完整 S05 partition。

## 1. 冻结结论

S05 是按生活时间线进行“连续分段”的算法，不是把全天视觉或语义相似的内容聚成一类：

```text
ordered Window-local Observation[]
+ TimelineEdgeSignal[]
→ chronological MomentSegment[]
+ Boundary Evidence
```

每个 Moment 是排序后 Observation 序列中的一个连续区间。S05 先保证局部 Episode 纯净；跨时间恢复的相似活动只能在 S07 以后作为 `RESUMED_EPISODE` 等候选关系讨论，不能回头破坏 S05 的连续分段。

## 2. 术语释义

### 2.1 Segment / 分段

把一条有顺序的时间线切成若干连续片段。每个片段只包含在排序序列中彼此相邻的一段 Window。

### 2.2 Partition / 完整划分

一组不重叠、不重复且完整覆盖输入的分段。S05 对当前 Day Revision 的 accepted Observation 形成 provisional partition。

`provisional` 表示“当前 Revision 的算法分段”，不是永远不会修订，也不代表用户最终会看到该 Moment。

### 2.3 Semantic clustering / 语义聚类

只因为内容相似就把不同时间的素材归在一起。例如上午和晚上都在遛狗。它可以作为后续候选关系信号，但不是 S05 Moment Formation。

### 2.4 Resumed Episode / 恢复的 Episode

某件活动中断后在较晚时间重新开始。恢复后的部分是新的 Moment；S07 以后可以判断多个 Moment 是否应共同服务于一个 Chapter 候选。

### 2.5 Boundary / 边界

时间排序后两个相邻 Window 之间的“切口”。S05 判断该切口应连接还是切开。

## 3. 输入与排序边界

S05 只使用：

- 当前 Day Revision 中按可信 capture facts 确定顺序的 Observation Lite；
- V1.10 的 Window-local perception 与逐条 evidence support；
- 相邻 Window 的 `TimelineEdgeSignal`；
- Observation Envelope 中可信的时间、source、media、session 与 Window offsets。

S05 默认不重新读取 Raw 视频，也不让每一对 Window 调用强 VLM。

排序必须可复现：相同 immutable input snapshot 与相同版本必须得到相同 Window 顺序。相同或重叠 capture time 的精确 tie-break 规则留给 Production Schema 设计，但不能依赖不稳定的模型输出。

本检查点中的“连续”是指排序后的 Window 序列连续，不代表现实时间没有拍摄空白，也不要求相邻 Window 的实际时间范围无间隙。

## 4. Moment Partition 不变量

对进入 S05 的每个 accepted Observation，在 S05 provisional 输出中必须满足：

1. 恰好属于一个 Moment；
2. 不在两个 Moment 中重复出现；
3. 不因质量差、`UNKNOWN`、`INSUFFICIENT_EVIDENCE` 或 `FAILED` 而从时间线消失；
4. Moment 内的 Observation 在排序序列中构成连续子序列；
5. Moment 按时间线排序，成员顺序保持不变；
6. 两个 Moment 之间至少存在一个明确的 boundary decision 与可追溯依据。

S05 不能通过删除难理解 Window 来获得更“干净”的分段。S06 才负责 `KEEP / CONTEXT_ONLY / DROP` 角色分配；没有 KEEP 的 Moment 可以在 S06 后移出用户内容，但 S05 的覆盖与边界 Trace 仍须保留。

## 5. 连续分段，不做跨时间合并

示例：

```text
A 上午遛狗
→ B 仍在遛狗
→ C 开会
→ D 晚上再次遛狗
```

S05 应形成：

```text
[A, B] → [C] → [D]
```

不得形成：

```text
[A, B, D] → [C]
```

原因不是 D 与 A/B 不相似，而是 C 已经中断了时间连续的局部 Episode。S07 可以把 `[A,B]` 与 `[D]` 标记为可能的 `RESUMED_EPISODE`，但 S05 Moment 本身保持连续、互斥。

## 6. Boundary 与最终成员确定

V1.0 已冻结的 working boundary states 继续有效：

```text
MERGE
SPLIT
DEFER
UNRESOLVED
```

- `MERGE`：切口两侧进入同一 provisional Moment；
- `SPLIT`：切口两侧进入不同 provisional Moment；
- `DEFER`：暂时等待有限 lookahead，尚未提交最终成员关系；
- `UNRESOLVED`：有限 lookahead 后仍无法可靠判断的诊断状态。

一个已提交的 Revision 必须具有确定的 Moment membership，不能让同一 Window 同时处于两个可能 Moment。继承 precision-first 原则：若 lookahead 用尽仍 unresolved，则 materialize 为保守切分；若 transition Window 对左右都无法可靠归属，则按 V1.14 独立为内部 Transition Moment，同时保留 `UNRESOLVED` 诊断和 Boundary Evidence。

具体信号融合、`DEFER` 等待范围、可被证据解决的 left/right placement 与阈值仍保持 OPEN；证据用尽后的 fallback 已由 V1.14 覆盖。

## 7. 不完整或失败的 Observation

- `OBSERVED` 和 `PARTIAL` 只能使用其有 Frame grounding 的事实；`WEAK` 不能独立证明应当合并；
- `INSUFFICIENT_EVIDENCE` 与 `FAILED` 保留时间、source、session、route 与可用 Edge，但不能提供肯定性语义连续证据；
- 未知不等于相似，也不等于发生了变化；
- 一个未知 Window 不能自动把前后 Episode 粘在一起，也不必仅因未知立即强制切开；
- 没有足够证据解决边界时进入 `DEFER / UNRESOLVED`，最终按 precision-first 规则处理。

因此这些 Window 在 `DEFER` 期间可以形成临时单 Window/Pending 表示，或在有充分可靠证据时归入相邻 Moment；证据用尽仍不能归左/归右时按 V1.14 独立。它们始终保留在 S05 Trace 中。

## 8. Window 仍是 S05 的最小分段单位

S05 只在 Window 之间建立边界，不在一个 Window 内伪造更细的切换时刻。

- Auto 9s Window 即使可能横跨真实边界，也仍只归属一个 provisional Moment；
- Manual 长视频已在 S02 被切为多个 Evidence Window，S05 使用这些既有 Window；
- `within_window_changes[]` 或 S03A change hint 可以提示该 Window 接近 transition，但不能证明未拍到的连续过程；
- 可被证据解决的 transition Window left/right placement 与标记 schema 保持 OPEN，必须在真实 Gold 数据中比较；证据用尽后的独立 fallback 已由 V1.14 冻结。

评测时可以按既有 Gold overlap 方法处理跨越真实边界的 Window；Production 输出不能声称比 Evidence 更精确的时间点。

## 9. Sparse-time semantics

Moment 记录：

- `first_observed_at`；
- `last_observed_at`；
- 成员 Window；
- Window 之间的真实 capture gaps；
- Boundary Evidence。

它不把 `first_observed_at → last_observed_at` 表述为连续录像覆盖，也不声称用户在该区间始终进行同一活动。

例如 10:02 与 10:18 的两条 Observation 被归入同一 Moment，只能表达“这些稀疏观察可能属于同一局部 Episode”，不能表达“用户连续进行了 16 分钟该活动”。

## 10. Moment 数量与用户输出数量分离

S05 的 Moment 是内部算法切片，不是用户页面上的 Chapter：

```text
Moment count
≠ Chapter count
≠ Aha count
```

Precision-first 分段可能产生较多 Moment。S07–S09 仍负责候选生成、局部 Episode 组合、去重和集合选择，并继续遵守丰富日 3–4 Chapter、严格例外第 5 个以及不凑数原则。

不能为了让 Moment 数量接近 3–4 而提前错误合并；也不能把每个 Moment 自动转换成一个 Chapter。

## 11. Revision 与成本边界

- S04 的昂贵 perception 继续按 exact input/version 缓存，不因 S05 重算而重跑；
- S05 默认使用缓存 Observation、S03B Edge 与确定性/轻量算法，不新增 Raw 上传；
- V1.0 当前允许每个 Revision 基于缓存 Observation 重新计算 full-day Moment，因为相对便宜且更容易保证一致性；
- 局部增量重算、Moment stable ID 与 Preview 稳定映射仍需在 S05 后续设计中单独决定；
- Moment 切得更多不会直接增加 Chapter/Aha 配额，但可能影响后续候选计算量，必须记录。

## 12. FROZEN 与 OPEN

### FROZEN

- S05 是时间连续分段，不是全天语义聚类；
- 每个 accepted Observation 在 provisional S05 partition 中恰好出现一次；
- Moment 成员连续、有序、互斥且完整覆盖输入；
- 非相邻 Window 不进入同一个 Moment；
- Resumed Episode 关系留给 S07 以后，不回写 S05 Moment；
- 未知、证据不足或失败 Window 不从 S05 时间线删除；
- 未知或失败不能独立证明 MERGE；
- S05 只在 Window 之间切分，不伪造 sub-Window 边界；
- Moment 使用 `first_observed_at / last_observed_at` 与真实间隙，不声称连续覆盖；
- Moment 数量与 Chapter/Aha 数量完全分离；
- 已提交 Revision 必须有确定 membership；unresolved 最终按 precision-first 切开，不能归左/归右的 transition Window 按 V1.14 独立，并保留诊断；
- S05 不做 KEEP/DROP、Chapter、Aha、精选素材或个人意义判断。

### OPEN / 下一步讨论或 Benchmark 校准

- continuity/boundary evidence 的具体聚合方法、阈值与权重；
- Scene、Activity、embedding、entity hint、time gap、session 与 location 的权重和阈值；
- V1.15 有界 DEFER Baseline 的 Production engine、终止 Trace、真实数据再校准与参数升级；
- Transition Moment 的 Production schema；可被证据解决的完整 seam pattern 与 atomic placement 架构已由 V1.15 覆盖，具体 EvidenceSufficiencyGate 继续 OPEN；
- 相同或重叠 capture time 的 Production tie-break；
- MomentSegment / BoundaryEvidence 的 Production JSON Schema；
- Preview Revision 的 full-day recompute、局部重算与 stable Moment ID 策略；
- Moment 数量膨胀、False Split 与 False Merge 的实际平衡。

## 13. 当前实现 GAP

- 当前仓库没有符合本合同的 Production MomentSegment、BoundaryEvidence 或 partition Validator；
- E00 的两两 Smoke Moment 没有语义意义，不能代表 S05；
- X01 的模型分组不是本检查点定义的独立、可复现 S05；
- 尚未实现每个 accepted Observation 恰好一次的覆盖校验、连续性校验或 unresolved-to-split Trace；
- 尚未在真实 wearable Gold 数据上测量 Moment Purity、Boundary Miss、False Merge 与 False Split；
- V1.12–V1.15 已冻结双向账本、Signature、unresolved fallback 与当前有界 DEFER Baseline，V1.16 已冻结完整 S06；具体实现、阈值与 S07 Chapter/Aha Candidate Generation 仍是 GAP。
