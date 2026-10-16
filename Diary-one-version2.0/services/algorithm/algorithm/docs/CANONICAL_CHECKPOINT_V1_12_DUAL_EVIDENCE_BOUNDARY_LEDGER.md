# Diary One Canonical Checkpoint V1.12 — Dual-Evidence Boundary Ledger

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** S05-B 每个相邻 Window 切口的双向证据账本与四状态边界决策架构
**继承关系：** 继承 V1.11–V1.1 与 V1.0 未被覆盖的规则

> **当前 Signature 覆盖：** V1.13 已冻结 Multi-Prototype CoreContextSignature + TailSignature + PendingTransitionBuffer，并规定只有 committed MERGE 才能更新现有 Core/Tail。

> **当前 unresolved transition 覆盖：** V1.14 规定有限证据用尽且仍不能归左/归右时，不强制二选一；在确定 partition 中物化独立 Transition Moment，`UNRESOLVED` 诊断继续保留。

> **当前 DEFER 覆盖：** V1.15 规定当前 lookahead 为最多 2 个可用后续 Window、最长 6 分钟、Pending Block 最多 3 个；完整 seam pattern 可提前结束，多 Pending 使用同一快照并原子提交。

> **当前 S06 覆盖：** V1.16 明确角色在本文边界决定之后产生；`KEEP / CONTEXT_ONLY / DROP` 均不能成为新的 boundary evidence 或反向证明 MERGE/SPLIT，既有双向 ledger 不因角色改变而丢失。

## 1. 冻结结论

S05 对时间排序后每两个相邻 Window 之间的切口建立一张可追溯 `BoundaryEvidenceLedger`：

```text
Continuity Evidence
支持“仍属于同一局部 Episode”

Boundary Evidence
支持“这里开始了新的局部 Episode”

→ MERGE | SPLIT | DEFER | UNRESOLVED
```

两类证据分别保存，不先互相抵消成一个不可解释的总相似分。决策同时参考当前相邻 `TimelineEdgeSignal`、新 Observation 和当前 `Moment Signature`，不能只比较前一条素材。

本检查点冻结架构与不变量，不冻结时间阈值、embedding 距离、信号权重、模型或概率门。

## 2. 术语释义

### 2.1 Seam / 切口

按时间排序后两个相邻 Window 之间可能连接或切开的地方。例如 `B | C` 中的竖线就是一个 seam。

### 2.2 Ledger / 证据账本

保存“用了哪些证据、证据来自哪里、支持哪个方向、最终为什么作出决定”的结构化记录。它不是一段模型解释文字。

### 2.3 Continuity Evidence

支持切口两侧仍属于同一局部 Episode 的证据。中文可理解为“连续证据”。

### 2.4 Boundary Evidence

支持切口两侧属于两个不同局部 Episode 的证据。中文可理解为“边界证据”。

### 2.5 Moment Signature

当前 provisional Moment 已积累出的结构化事实轮廓，例如可靠 Scene/Activity 分布、embedding 表示、匿名实体提示、时间范围和矛盾。它不是长 Caption，也不包含 Chapter/Aha 价值判断。

### 2.6 事实可靠性与边界方向不是一回事

V1.10 `support_grade` 回答：

> “这条 Scene、Activity 或事实本身被画面支持得多可靠？”

Boundary ledger 回答：

> “这条可靠事实对当前切口更支持连续、支持切开，还是无法判断？”

例如“从街道进入餐厅”可以是 `STRONG` 的 Scene change，但它既可能是同一次外出的自然转场，也可能是新 Episode 的开始。因此不能把 `STRONG Scene change` 自动转换成 `SPLIT`。

### 2.7 TimelineEdgeSignal 与 BoundaryEvidenceLedger 的区别

- S03B `TimelineEdgeSignal` 保存 A/B 之间的基础测量，例如时间间隔、embedding 距离和视觉变化；
- S05 `BoundaryEvidenceLedger` 记录这些测量与 Observation、Moment Signature 如何分别支持 continuity 或 boundary，以及最后怎样得到决策。

前者是“测到了什么”，后者是“这些测量对当前分段意味着什么”。Ledger 引用 Edge，不复制或改写 Edge 原值。

## 3. 一条相邻切口对应一张账本

对于排序后相邻 Window `A → B`，逻辑上必须存在一张独立账本，至少绑定：

- Day Revision 与 boundary ledger identity；
- `from_window_id=A`、`to_window_id=B`；
- 对应的 `TimelineEdgeSignal` identity/version；
- 两侧 Observation identity/status/version；
- 当前 Moment Signature identity/version；
- `continuity_evidence[]`；
- `boundary_evidence[]`；
- neutral / unknown / unavailable diagnostics；
- working state；
- lookahead usage 与状态转换 Trace；
- committed materialized action；
- boundary algorithm/version/parameter/provenance。

模型不得改写 Window 顺序、capture facts、Edge 原值或 Observation 原事实。具体 JSON 字段名留给 Production Schema，但上述可追溯关系必须保留。

新或晚到 Window `X` 插入 `A → B` 时：

```text
invalidate ledger(A,B)
create ledger(A,X)
create ledger(X,B)
```

旧 Observation 不重算。受影响 Moment partition 的重算范围与 stable ID 策略仍保持 OPEN。

## 4. 每条 Evidence Item 的逻辑内容

一条 continuity/boundary evidence item 至少表达：

- signal family；
- 实际观察值或引用；
- 支持方向：continuity / boundary / neutral / unknown；
- 来源可靠性或 V1.10 grounded fact support；
- 对应 Window、Edge、Fact 或 metadata reference；
- missing / contradiction / uncertainty reason；
- 生成该项的算法与版本。

`unknown` 和 `unavailable` 必须显式记录，不能当作 0，也不能伪装成 continuity。

即使未来加入校准后的 `p_boundary` 或聚合分数，原始双向 evidence items 与 provenance 仍必须保留；单一总分不能成为唯一事实来源。

## 5. 可进入账本的信号家族

| 信号家族 | 可能支持 Continuity | 可能支持 Boundary | 重要限制 |
|---|---|---|---|
| Time gap | 较短且与当前采集节奏一致 | 明显间隔或中断 | 阈值未冻结；短不等于同一 Episode |
| Capture session | 同一可信 Session | Session discontinuity | Session 只是结构证据，不是活动真相 |
| Scene | 环境保持相对一致 | 可靠 Scene change | Scene change 不能单独决定 SPLIT |
| Activity | 活动保持相对一致 | 可靠 Activity change | Activity 相同不能单独决定 MERGE |
| Embedding / visual | 视觉距离较近 | 视觉距离明显增大 | 相似不证明同一次生活事件 |
| Anonymous entity/object hint | 局部实体或核心物体有延续提示 | 核心构成明显改变 | 不识别身份，不把外观相似当同一个人 |
| Trusted location | 可信位置相近 | 可信位置明显改变 | 缺失为 UNKNOWN；阈值未冻结 |
| Change / contradiction | 没有可靠矛盾 | 出现可靠矛盾或 transition hint | Window 内 change 不能伪造精确边界时刻 |
| Observation status/support | 可靠事实可以参与 | 可靠变化事实可以参与 | `WEAK/UNKNOWN/INSUFFICIENT_EVIDENCE/FAILED` 不能独立证明 MERGE |

其他信号只有在来源、含义、版本与错误模式明确后才能加入，不得用大量咖啡馆、遛狗、书店等场景补丁代替通用逻辑。

## 6. 两本账不能提前相减

每个 seam 同时维护：

```text
continuity_evidence[]
boundary_evidence[]
```

原因是现实转场可能同时具有两种证据：

```text
街道
→ 同一群人进入餐厅

Scene change            → boundary evidence
time/entity continuity  → continuity evidence
```

如果先压成一个中间总分，两种证据可能互相抵消，系统只剩“0.52”却不知道为什么不确定。双向账本必须保留这种冲突，交给 `DEFER` 与有限 lookahead 处理。

允许算法为排序或 Benchmark 计算派生分数，但必须满足：

1. continuity 与 boundary 聚合值分别记录；
2. 原始 evidence items 不丢失；
3. 分数版本、特征与阈值可复现；
4. 不把未经校准的值称为真实概率。

## 7. 四状态决策架构

working decision 只允许：

```text
MERGE
SPLIT
DEFER
UNRESOLVED
```

架构级判断矩阵：

| Continuity Evidence | Boundary Evidence | Working decision |
|---|---|---|
| 足够强 | 不足或不明确 | `MERGE` |
| 不足或不明确 | 足够强 | `SPLIT` |
| 两边都强或明显冲突 | 两边都强或明显冲突 | `DEFER` |
| 两边都弱、缺失或未知 | 两边都弱、缺失或未知 | `DEFER` |
| lookahead 用尽仍无法解决 | — | `UNRESOLVED`，committed action 为保守切分；无法归左/归右的 transition Window 按 V1.14 独立 |

这里的“足够强”是决策层的证据充分性，不等于 V1.10 单条事实的 `STRONG`。具体如何从多项事实、metadata 与 Edge 汇总成“足够”，必须由 Benchmark 校准。

### 7.1 `MERGE`

表示当前证据足以支持 seam 两侧进入同一 provisional Moment，并且没有尚未解决的可靠边界矛盾。

### 7.2 `SPLIT`

表示当前证据足以支持 seam 两侧属于不同 provisional Moment，或继承 V1.11 的 unresolved conservative split。

### 7.3 `DEFER`

表示当前证据冲突或不足，但仍有有限后续 Window 可以帮助判断。`DEFER` 不是默认 MERGE，也不能永久悬挂。

### 7.4 `UNRESOLVED`

表示允许的 lookahead 已用尽，仍不能可靠判断。它是诊断结果；已提交 Revision 的 materialized membership 继续按 precision-first 切开。如果 transition Window 对左右均无法可靠归属，则依据 V1.14 将它独立为内部 Transition Moment，同时保留 unresolved 原因。

## 8. 比较对象不是只有前一条 Window

每次判断新 Observation 是否延续当前 Moment 时，至少读取：

```text
Immediate TimelineEdgeSignal
+ New Window-local Observation
+ Current Moment Signature
+ limited lookahead when state is DEFER
```

Immediate Edge 负责描述局部变化；Moment Signature 防止系统因为“每相邻两条都略相似”而逐步漂移到完全不同的 Episode。

Moment Signature 只汇总可靠、结构化信息。`WEAK`、`UNKNOWN`、`INSUFFICIENT_EVIDENCE` 与 `FAILED` 可以保留为诊断和缺口，但不能给 continuity ledger 增加虚假的肯定性语义。

本文最初把 Moment Signature 的 core/tail 结构、更新、衰减与防漂移规则留给 S05-C；其架构部分现已由 V1.13 冻结，具体参数仍保持 OPEN。

## 9. 明确禁止的单信号捷径

当前没有下列自动规则：

- Scene 变化 → 必然 `SPLIT`；
- Activity 相同 → 必然 `MERGE`；
- embedding 相似 → 必然 `MERGE`；
- embedding 距离大 → 必然 `SPLIT`；
- 时间间隔短 → 必然 `MERGE`；
- 时间间隔长 → 必然 `SPLIT`；
- Manual 素材 → 自动成为独立 Moment；
- 低画质、`UNKNOWN` 或 `FAILED` → 自动删除或自动粘连前后。

这些信号都可以进入相应账本，但单项含义、组合方式与阈值必须可解释、可版本化并由真实数据校准。若未来要引入极少量 hard rule，必须单独冻结，不得在实现中暗加。

## 10. 三个典型例子

### 10.1 同一外出中的场景转场

```text
街道 → 餐厅入口
```

- Scene change 支持 boundary；
- 短时间、同 Session、匿名实体延续可能支持 continuity；
- 两边都有可靠证据时进入 `DEFER`，而不是见到 Scene change 就 `SPLIT`。

### 10.2 同一环境在较晚时间再次出现

```text
上午在家 → 白天外出 → 晚上回家
```

“家中画面相似”可以提供视觉 continuity hint，但中间 Episode、时间与 Session 变化提供 boundary evidence。V1.11 禁止把上午和晚上直接放进同一个 Moment。

### 10.3 未知 Window 位于两个不同片段之间

```text
清晰办公 → 模糊未知 → 清晰餐厅
```

未知 Window 不提供肯定 continuity。系统保留其时间与 Edge，必要时 `DEFER`；lookahead 后仍不能证明同一 Episode，则 `UNRESOLVED + materialized SPLIT`。

## 11. 成本与增量边界

高强度参考日 220 个 Window 最多产生约 219 个相邻 seam ledger。它们默认使用已有 metadata、S03B Edge、S04 Observation 与轻量计算：

- 不新增 Phone→Cloud Raw 上传；
- 不要求每个 seam 调用多模态或强推理模型；
- 不重新执行旧 Window 的 S04 perception；
- lookahead 必须有界；
- 每个 ledger 的计算、缓存、重算与成本可单独追踪。

晚到素材只直接失效相邻旧 Edge 与 boundary ledger。是否为保证全日 partition 一致性而继续 full-day 重算 Moment，或只重算局部区间，仍按 V1.11 保持 OPEN。

## 12. FROZEN 与 OPEN

### FROZEN

- 每个相邻 Window seam 都有独立、可追溯的 BoundaryEvidenceLedger；
- continuity evidence 与 boundary evidence 分开保存；
- unknown / neutral / unavailable 显式记录，不当作 continuity；
- 每个 evidence item 可追溯到 Window、Edge、grounded fact 或可信 metadata；
- 事实可靠性与边界方向分离；
- 单一总分不能取代双向 evidence items；
- working decision 为 `MERGE | SPLIT | DEFER | UNRESOLVED`；
- 两边都强或两边都弱时先 `DEFER`，不武断 MERGE；
- lookahead 用尽仍 unresolved 时，保留诊断并 materialize 为保守切分；无法归左/归右的 transition Window 按 V1.14 独立；
- 决策同时参考 Immediate Edge、New Observation 与 Current Moment Signature；
- `WEAK/UNKNOWN/INSUFFICIENT_EVIDENCE/FAILED` 不能制造肯定性 continuity；
- Scene、Activity、embedding、time gap、Manual 或低画质均不能单独决定边界；
- 默认不为每个 seam 调用强 VLM，也不新增 Raw 上传；
- late insertion 只直接失效受影响的 Edge 与 seam ledger。

### OPEN / 下一步讨论或 Benchmark 校准

- Context Signature 的 prototype、Motif、Core/Tail 聚合与校准参数；
- continuity/boundary evidence level 的具体聚合方法；
- time gap、session、Scene、Activity、embedding、entity、location 与 contradiction 的阈值和权重；
- V1.15 当前 DEFER Baseline 的 Production engine、真实数据再校准与版本化参数升级；
- 可选 `p_boundary` 的训练、校准与使用方式；
- BoundaryEvidenceLedger 的 Production JSON Schema 与 reason-code taxonomy；
- 可被证据解决的 transition placement 架构已由 V1.15 覆盖；具体 EvidenceSufficiencyGate 与 reason-code schema 继续 OPEN；证据用尽后的隔离 fallback 以 V1.14 为准；
- full-day 或局部 Moment 重算、stable ID 与 Revision 映射；
- 真实 wearable Gold 上的 False Merge、False Split、Boundary F1 与 DEFER diagnostics。

## 13. 当前实现 GAP

- 当前仓库没有 Production BoundaryEvidenceLedger schema、builder、decision engine 或 Validator；
- V1.13 已冻结 Moment Signature 更新架构，但当前仍没有对应 schema、更新实现或四状态 Trace；
- E00 pairing 与 X01 模型分组都不符合本检查点；
- 尚未实现 late insertion 的 seam-ledger invalidation；
- 尚无真实 wearable Gold 用于校准证据充分性、阈值或 lookahead；
- V1.14/V1.15 已覆盖 unresolved fallback 与当前有界 DEFER Baseline；本检查点仍不冻结具体权重、阈值、模型或完整 S06/Chapter/Aha 判断。
