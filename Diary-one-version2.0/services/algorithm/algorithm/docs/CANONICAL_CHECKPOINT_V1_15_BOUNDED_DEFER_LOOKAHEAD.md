# Diary One Canonical Checkpoint V1.15 — Bounded DEFER Lookahead and Atomic Pending Resolution

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** S05-D 的 DEFER 后续证据预算、capture-time / capture-scope 约束、提前结束、连续 Pending Block 解析，以及 Preview 处理终点物化
**继承关系：** 继承 V1.14–V1.1 与 V1.0 未被覆盖的规则

> **当前 S06 覆盖：** V1.16 已冻结完整 `KEEP / CONTEXT_ONLY / DROP_FROM_MEMORY_OUTPUT` 角色合同、candidate-empty Moment、Transition 限制、duplicate reason 与 S07 handoff；本文 S05-D 的 Pending/lookahead 语义不变。

## 1. 冻结结论

S05-D 对 `DEFER` 采用有界、可提前结束、不会等待下一次 Sync 的 lookahead：

```text
DEFER Window
→ PendingTransitionBuffer
→ only already-available evidence in current Preview input
→ at most 2 usable subsequent Windows
→ at most 6 minutes of capture-time span
→ at most 3 consecutive Pending Windows including the origin
→ resolve early when the complete local seam pattern is decisive
→ otherwise stop at the first applicable limit
→ V1.14 unresolved Transition fallback
```

首版参数正式采用：

| 参数 | V1.15 值 | 状态与含义 |
|---|---:|---|
| `lookahead_usable_max` | 2 | 版本化首版 Baseline；最多读取两个可为边界判断增加有效信息的后续 Window |
| `lookahead_capture_span_max` | 6 min | 版本化首版 Baseline；从首个 Pending Window 到最新被考虑 Window 的 capture-time 总跨度上限 |
| `pending_block_max` | 3 | 版本化首版 Baseline；最初 DEFER Window + 最多两个连续仍待定的后续 Window |

这些值是当前实现必须遵守的 Baseline，不是脱离真实数据永久不变的自然常数。后续只能通过版本化 Benchmark、错误归因与新 Checkpoint 调整，不能在 Production 中静默漂移。

架构不变量：

- lookahead、时间跨度和 Pending 长度必须同时有界；
- 任一终止条件先到即停止，不要求用满所有预算；
- 只复用当前 Preview 输入中已经存在的 Window、S03 信号、S04 Observation、Moment Signature 与 BoundaryEvidenceLedger；
- 不等待下一次用户 Sync，不补帧、不回取 Auto Raw、不新增 Phone→Cloud Raw 上传；
- Pending 在确认前不能更新左右 Moment 的 Core/Tail；
- 多个 Pending Window 使用同一不可变证据快照评估，最后原子提交，不能边判断边污染后续判断；
- 一个已提交 Preview Revision 不允许留下悬挂的 Pending membership。

## 2. 术语释义

### 2.1 Pending Window / 待定 Window

一个已经进入 S05 时间线、但当前证据仍不能可靠确定应与相邻 Moment 合并还是切开的 Evidence Window。

```text
A：已确认局部 Moment
B：当前归属不清

A | [B pending]
```

Pending Window：

- 不是删除状态；
- 不等于低质量；
- 不自动成为 Transition Moment；
- 不自动成为 Aha 或 Chapter；
- 只是 S05 当前计算中的临时归属状态。

### 2.2 Pending Block / 连续待定块

时间线上彼此相邻、同时处于 Pending 的一个或多个 Window。一个 Pending Window 可以视为长度为 1 的 Pending Block；通常在多个连续待定 Window 出现时使用该术语。

```text
A | [B C] | D
     ↑ ↑
  Pending Block
```

A、D 不属于 Pending Block；它们是两侧可能提供参照的内容。

### 2.3 Lookahead / 有界向后查看

在 B 暂时无法判断时，查看少量已经存在于当前 Preview 输入中的后续 Window，判断后续语境能否解决 B 的归属。

Lookahead 不是：

- 等待用户下次 Sync；
- 请求 App 再上传素材；
- 回取完整视频或 Auto 的其他帧；
- 为这条 seam 单独调用强模型。

### 2.4 Usable subsequent Window / 可用后续 Window

一个后续 Window 若能向 continuity ledger 或 boundary ledger 增加至少一项可追溯、非纯 UNKNOWN、可能改变当前判断的信息，则可计入 `lookahead_usable_max`。

可用信息可以来自：

- grounded Scene / Activity / Motif / entity-object hint；
- 可信 capture time、capture scope 或 location metadata；
- S03A intrinsic signal 或 S03B TimelineEdgeSignal；
- 与 Core、Tail 或右侧局部语境的可解释兼容或矛盾。

若一个 Window 只有 `FAILED`、纯 UNKNOWN 或完全没有新增边界信息，它不消耗“两个可用 Window”计数，但：

- 仍保留在时间线；
- 仍消耗 capture-time 范围；
- 若自身也无法归属，仍计入 `pending_block_max`；
- 不能制造肯定性 MERGE。

### 2.5 Evidence Anchor / 证据锚点

用于帮助解释 Pending Block 归属的稳定参照。

- `LeftAnchor`：Pending Block 左侧已经提交的 Moment Core/Tail；
- `RightEvidenceAnchor`：在允许 lookahead 内出现、具有足够 grounded 信息的后续 Window 或右侧局部种子。

RightEvidenceAnchor 只是当前边界计算的参照，不等于已经形成用户可见 Moment，也不能在原子提交前更新任何已确认 Core。

### 2.6 Immutable evidence snapshot / 不可变证据快照

解析一个 Pending Block 时固定使用同一版本的：

- Window 顺序；
- Window-local Observation；
- TimelineEdgeSignal；
- seam ledger；
- 左侧 Core/Tail；
- 当前允许的右侧证据。

评估期间不能先把 B 写入左侧 Core，再用被 B 改写后的 Core 判断 C。

### 2.7 Atomic commit / 原子提交

先完成整个允许范围内的判断，再一次性写入 Moment membership、Core/Tail 更新与状态 Trace。用户不会看到“只提交一半”的中间 partition。

## 3. 三个同时生效的预算

### 3.1 Window 预算

从最初 DEFER Window B 开始，最多考虑两个“可用”的后续 Window。以下例子假设 C、D 都为当前 ledger 增加了有效信息：

```text
B origin
C lookahead #1
D lookahead #2
```

在该假设下，E 是第三个可用后续 Window，不属于本次 B 的允许证据：

```text
B → C → D → E
            ↑   ↑
      budget end  forbidden for this resolution
```

系统不能因为 C、D 仍不清楚，就继续偷看 E。

### 3.2 Capture-time 预算

首版使用：

```text
newest_considered.capture_end
- first_pending.capture_start
≤ 6 minutes
```

Photo 的 `capture_end = capture_start`。时间计算使用 S01/S02 已规范化且可追溯的 capture time；不得用 import time 或 Sync time 替代生活时间。

若可靠 capture time 缺失，不能猜测时间连续；Window/Block/Preview 其他上限仍然生效。

6 分钟的首版依据：

- Auto 约每 2 分钟一次，两个后续 Auto 通常落在约 4 分钟内；
- 允许少量调度与视频时长余量；
- 当前固定 Manual 视频模式最长 2 分钟，局部内部 Window 能落在该范围内；
- 防止为了一个不确定片段跨越十几分钟甚至更远寻找解释。

V1.15 不重开 16 秒、73 秒等非标准 Manual 时长的 S02 Window 合同；它只消费 S02 已接受并排序的 Window。

### 3.3 Pending Block 预算

首版：

```text
pending_block_max = 3
```

它包含：

```text
1 origin DEFER Window
+ at most 2 subsequent Windows that also remain Pending
```

Pending Block 达到 3 时立即视为物理缓冲上限。即使两个“可用证据”计数尚未全部消费，也不再扩大 Block；这是为了防止连续 FAILED/UNKNOWN/冲突内容无限占用状态。

## 4. Capture scope 与 Sync 边界

### 4.1 App Sync / import batch 不是生活边界

用户多次打开 App、分批导入或触发后台上传，只是数据到达方式。S05 按 capture time 处理累计 Evidence：

- 可以跨 Sync/import batch 使用已经进入当前 Preview input 的相邻 Window；
- 不因 batch ID 改变自动 SPLIT；
- 不因同一 batch 自动 MERGE。

### 4.2 Capture session 不能单独拍板

`capture_session_id` 或 session discontinuity 可以进入 boundary ledger，但不能独立决定 MERGE、SPLIT 或 lookahead stop。

提前关闭允许证据范围的 `capture_scope_stop` 至少要求版本化的复合证据，例如：

```text
trusted capture-session discontinuity
+ meaningful capture-time discontinuity
+ no reliable local continuity counter-evidence
```

具体时间阈值、session metadata 可信度与组合权重继续由真实数据校准。本检查点冻结的是“不能把 App Sync 当 Session，也不能用单一 Session 信号拍板”。

## 5. 单个 Pending Window 的提前结束

对：

```text
A：左侧 Moment
B：Pending Window
C：允许范围内的后续 Window
```

在同一证据快照中同时判断 A—B 与 B—C 两个相邻 seam。只有形成完整、无未解决强冲突的局部结构时才提前结束：

| A—B | B—C | 已提交结构 | 含义 |
|---|---|---|---|
| `MERGE` | `SPLIT` | `A+B | C` | B 归左 |
| `SPLIT` | `MERGE` | `A | B+C` | B 归右 |
| `MERGE` | `MERGE` | `A+B+C` | 三者属于同一连续局部 Moment |
| `SPLIT` | `SPLIT` | `A | B | C` | B 的左右边界均已被证据确认 |

若任一必要 seam 仍是 `DEFER`，而预算内仍有后续可用 Window，则继续等待；不能用“一个明确切口 + 一个模糊切口”冒充完整归属答案。

### 5.1 EvidenceSufficiencyGate

提前形成 MERGE/SPLIT 仍继承 V1.12：

- continuity 与 boundary ledger 分别保存；
- 支持方向达到决策充分性；
- 相反方向没有尚未解决的可靠强冲突；
- 单一 Scene、Activity、embedding、time gap、Session、Manual 或 quality 信号不能拍板；
- 每项证据保留 Window/Edge/Fact/metadata provenance；
- 不把未经校准的派生分数称为真实概率。

首版评测 Baseline 要求至少两个非重复信号家族相互印证。由同一画面派生、错误高度相关的 Scene label 与 embedding 相似，不能机械地重复计票。具体 signal-family taxonomy、强度聚合与阈值保持 OPEN，必须通过 Gold Benchmark 校准。

### 5.2 `A | B | C` 不等于三个 Chapter

`SPLIT/SPLIT` 只说明 B 是边界明确的独立连续时间片段，不代表 B 必须成为独立 Chapter，也不代表 A、C 永远不能再关联。

例如：

```text
A：古建筑景区游览
B：进入现代奶茶店并喝奶茶
C：离店后继续游览古建筑景区
```

若两侧边界证据充分，S05 可以得到：

```text
A | B | C
```

S07 仍可在时间、局部 outing、Activity 恢复与其他证据共同支持时，把 A、C 建立为 `RESUMED_EPISODE` 候选，并让 A/B/C 共同服务于同一个 Chapter Candidate。S05 Moment count 从来不等于 Chapter count。

若 B 只是一次短暂镜头扫过现代室内，Scene change 单独不足以形成 `SPLIT/SPLIT`，仍可能 DEFER 或最终 MERGE。

## 6. 多个连续 Pending Window 的解析

### 6.1 不允许贪心污染

禁止：

```text
先把 B 勉强写入 A
→ 用被 B 改写的 Core 判断 C
→ 再用 A+B+C 判断 D
```

这会把第一次错误放大为链式错误合并。

### 6.2 正确解析顺序

在允许预算内：

1. 固定同一不可变证据快照；
2. 建立或更新所有相邻 seam ledger；
3. 先保留 block 内已经被充分 continuity evidence 支持的相邻 MERGE；
4. 从可用 LeftAnchor 与预算内 RightEvidenceAnchor 向内解析；
5. 归属只能沿着相邻且已确认的 seam 传播，遇到 DEFER/UNRESOLVED 即停止，不能跨过未知 seam 跳跃吸收；
6. 完成全部判断后原子提交；
7. 只隔离最小 unresolved block。

不进行 Pending Block 内所有 Window 的全组合比较；默认只使用相邻 ledger、左侧 Core/Tail 和预算内右侧局部证据。

### 6.3 右侧 Anchor 必须在两次可用 lookahead 与其他硬上限内

合法例子：

```text
A [B] C

B = origin pending
C = lookahead #1 and possible RightEvidenceAnchor
```

```text
A [B C] D

B = origin pending
C = lookahead #1 and still pending
D = lookahead #2 and possible RightEvidenceAnchor
```

这里假设 C、D 都属于“可用后续 Window”。若 C 只是纯 FAILED/UNKNOWN，D 可以成为第一个可用后续 Window；是否还能读取另一个可用 Window，仍同时受 6 分钟、Pending Block 长度与 Preview 终点限制。

非法扩张：

```text
A [B C D] E

B = origin
C = usable lookahead #1 and still pending
D = usable lookahead #2 and still pending
E = usable lookahead #3, forbidden for resolving B
```

若 C、D 都可用但仍 Pending，则 `pending_block_max = 3` 与 `lookahead_usable_max = 2` 同时到限。若 C 或 D 纯 FAILED/UNKNOWN，则可用计数可能尚未到 2，但 `pending_block_max = 3` 已先到限。两种情况下系统都在 B/C/D 范围内结算，不读取 E 来挽救当前判断。

### 6.4 Block 内部结果

假设：

```text
A [B C] D
```

可能得到：

```text
A+B+C | D
A | B+C+D
A | B+C | D
A+B | C+D
```

但每个 `+` 都必须有对应相邻 seam 的充分 continuity evidence；不能因为 B、C 都是不确定内容就自动合并。

若证据用尽后只有 B—C 被可靠支持为 MERGE，而两侧归属仍无法判断：

```text
A | [B+C] | D
```

`[B+C]` 可以物化为一个最小 Transition Moment。若 B—C 也 unresolved：

```text
A | [B] | [C] | D
```

内部 unresolved seam 继续保守切开，不能建立“不确定素材垃圾桶”。

### 6.5 Block 不重叠

同一 Window 在一次 S05 计算中最多属于一个 active Pending Block。新的连续 DEFER Window 只能追加到当前 Block；当前 Block 已提交或物化后，后续 Window 才能开始新的 Block。

## 7. 终止条件与 Preview 处理终点

等待在以下任一条件先到时结束：

1. 完整 seam pattern 已形成，可提前正常提交；
2. 已消费两个可用后续 Window；
3. capture-time 总跨度达到 6 分钟；
4. Pending Block 达到 3 个 Window；
5. 复合 `capture_scope_stop` 成立；
6. 当前 Preview input 到达处理终点。

必须在 Trace 中记录终止类别，但正式 reason-code 命名与 Production schema 继续 OPEN。至少需要区分：

- evidence-resolved early；
- usable-window limit；
- capture-time limit；
- pending-block limit；
- capture-scope stop；
- Preview input exhausted。

### 7.1 Preview 终点不等待下一次 Sync

当前 Preview 输入结束时：

```text
resolved Pending → normal atomic commit
unresolved Pending → V1.14 Transition fallback
```

已提交 Preview Revision 必须形成完整、连续、互斥的 Moment partition；Pending membership 只能保留在计算 Trace 中，不能成为悬挂的已提交输出。

未来新素材到达后是否重新打开旧 unresolved seam、局部重算范围与 stable Moment ID 仍属于 Revision 专题。本检查点不提前决定该机制。

## 8. 成本与复杂度边界

V1.15 默认复用已经计算的：

- S03A WindowIntrinsicSignal；
- S03B TimelineEdgeSignal；
- S04 Window-local Observation；
- V1.12 BoundaryEvidenceLedger；
- V1.13 Core/Tail/Pending Signature。

默认不增加：

- Phone→Cloud Raw；
- Auto 补帧或回取；
- 完整视频上传；
- 每个 DEFER seam 的强 VLM；
- Pending Block 内 O(k²) 的全量两两比较。

`k ≤ 3`，并且只处理相邻 seam 与至多两个 Anchor 方向，因此新增状态和比较是严格有界的轻量计算。实际延迟、DEFER rate 与额外比较次数仍须在真实实现中测量。

## 9. 评测与真实数据校准

V1.15 至少要求记录：

- Pending Window / Block 数量与长度分布；
- 每次 DEFER 实际消费的 usable Window 数；
- 实际 capture-time lookahead 分布；
- after-1 / after-2 resolved rate；
- window/time/block/session/Preview 各终止原因占比；
- left/right/through/isolated placement accuracy；
- False Merge、False Split 与 unresolved rate；
- `pending_block_max = 3` 的截断 regret；
- `6 min` 的截断 regret；
- 因不读取超出 usable/time/block/scope/Preview 任一上限的后续 Window 而产生的 missed resolution；
- atomic resolution 是否消除了 evaluation-order drift；
- S07 Resumed Episode 对 `A | B | C` 类场景的 Chapter 恢复能力；
- 额外计算成本与 Preview 延迟。

参数升级必须在不同用户、生活方式、地点、拍摄质量和 Auto/Manual 结构上分层评估。不能只因为某个案例能被额外后续 Window 解决，就静默扩大所有用户的 lookahead。

## 10. FROZEN、BASELINE 与 OPEN

### FROZEN

- S05-D 只使用当前 Preview input 已有证据，不等待下一次 Sync；
- App Sync/import batch 不是 Moment 边界或 capture session；
- lookahead、capture-time 与 Pending Block 必须同时有界，任一条件先到即停止；
- 单个信号不能使 DEFER 提前 MERGE/SPLIT；
- 提前结束必须形成完整 local seam pattern，而不是只解决一侧；
- Pending Block 使用同一不可变证据快照，禁止贪心污染 Core/Tail；
- attachment 只能沿相邻已确认 seam 传播，不能跨越 unresolved seam；
- RightEvidenceAnchor 必须位于允许的两个可用后续 Window 内，并且不得越过时间、Block、capture-scope 或 Preview 硬上限；
- 内部 Window 只有在独立 continuity evidence 充分时才能 MERGE；
- 只隔离最小 unresolved block，内部 unresolved seam 继续切开；
- 提交使用原子更新；已提交 Preview 不留下悬挂 Pending；
- `A | B | C` 是 Moment 层连续分段，不等于三个 Chapter；S07 可讨论 Resumed Episode；
- 默认不增加 Raw 上传、补帧、逐 seam 强模型或 O(k²) 比较。

### V1.15 BASELINE

- `lookahead_usable_max = 2`；
- `lookahead_capture_span_max = 6 min`；
- `pending_block_max = 3`；
- seam 提前决策至少需要两个非重复信号家族相互印证，并且相反账本没有未解决强冲突。

这些 Baseline 已被当前 Checkpoint 固定；未来可通过新版本与真实数据升级。

### OPEN / 下一阶段或真实数据校准

- continuity/boundary EvidenceSufficiencyGate 的具体权重、阈值和 signal-family taxonomy；
- capture-session metadata 可信度与复合 `capture_scope_stop` 的具体阈值；
- Production Pending/Block/Anchor/termination reason schema；
- late insertion、Preview 局部重算、旧 seam reopening 与 stable Moment ID；
- Final 后是否及何种条件允许重开旧 unresolved seam；
- V1.16 已冻结 S06 角色语义；Production role schema、engine、Validator 与真实数据校准；
- S07 Resumed Episode 与 local outing grouping 的正式合同；
- Aha 独立价值、媒体质量、重复与证据门；
- Gold 标注协议、样本量和用户分层。

## 11. 当前实现 GAP

- 当前仓库没有 Production Pending/lookahead/Anchor/atomic-resolution engine；
- 没有 `lookahead_usable_max`、capture span 或 Pending Block Validator；
- 没有 immutable evaluation snapshot 与 atomic commit Trace；
- 没有 Preview-end pending exhaustion Validator；
- 没有终止原因 Production schema；
- E00/X01 都不符合本检查点的分阶段 S05-D；
- 尚无真实 wearable Gold 可校准 2 Window、6 分钟、3 Pending 或两类信号 Baseline；
- S07 Resumed Episode 尚未实现，因此 `A | B | C` 的 Chapter 恢复能力尚未验证。
- V1.16 的 S06 role engine 与 shared S07 handoff 尚未实现。

## 12. 下一步准确节点

S05-D 的架构与首版参数已冻结，V1.16 也已完成 S06。下一步进入：

```text
S07｜Chapter / Aha Candidate Generation

先定义 Candidate unit、普通/Transition route、
Chapter local Episode scope、Resumed Episode、
Aha independent-value gate 与 reject audit。
```

下一步不重开本文 S05-D Baseline 或 V1.16 S06 role contract，也不提前进入 S08 enrichment、S09 集合选择、S10 最终媒体或 Narrative。
