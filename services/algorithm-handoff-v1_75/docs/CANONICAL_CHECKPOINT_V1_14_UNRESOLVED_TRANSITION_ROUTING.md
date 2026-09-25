# Diary One Canonical Checkpoint V1.14 — Unresolved Transition Routing

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** S05-D 在有限证据用尽后对 unresolved transition Window 的物化方式，以及它进入 S06/S07 的简化路由
**继承关系：** 继承 V1.13–V1.1 与 V1.0 未被覆盖的规则

> **当前 DEFER 覆盖：** V1.15 已冻结“有限证据”的当前首版合同：最多 2 个可用后续 Window、最长 6 分钟、Pending Block 最多 3 个、完整 seam pattern 提前结束、同快照解析与原子提交。V1.14 的 fallback 语义不变。

> **当前 S06 覆盖：** V1.16 已冻结完整三角色合同，并将本文 Transition KEEP 收紧为“Evidence 可读、内容可独立理解、具有具体短暂事件信号”；独立 Aha 价值由 S07 判断，最终媒体质量由 S10 判断。`MEMORY_SUPPRESSED_DUPLICATE` 等只能作为 role reason。

## 1. 冻结结论

当一个 `DEFER` Window 已使用允许的有限后续证据，仍不能可靠判断应该归入左侧还是右侧 Moment 时，系统不再强行猜测归属。正式采用：

```text
DEFER
→ bounded lookahead / existing evidence
→ left attachment unresolved
  and right attachment unresolved
→ UNRESOLVED diagnostic
→ materialize an isolated Transition Moment
→ S06/S07 routing
```

这个内部 `Transition Moment` 后续只有三条内容路径：

```text
KEEP for Aha candidacy
CONTEXT_ONLY
DROP from Memory output
```

它不是新的用户可见内容类型，不自动成为 Aha，也不恢复为 Chapter 的“杂物桶”。

## 2. 术语释义

### 2.1 DEFER / 待定

当前 continuity evidence 与 boundary evidence 冲突或不足，但仍允许读取少量已经进入本次算法处理的后续 Window，因此暂缓提交边界决定。

`DEFER` 不是删除、失败、默认 MERGE 或默认 SPLIT。

### 2.2 Evidence exhausted / 允许证据用尽

表示当前版本允许使用的 bounded lookahead、时间范围或 Revision 输入已经到达上限，且现有证据仍不能可靠支持归左或归右。

它不代表世界上不存在更多信息，只代表系统不再为这条过渡素材继续增加当前处理成本或延迟。

### 2.3 Transition Window / 过渡 Window

位于两个局部 Episode 之间、对左右归属都缺少充分证据的 Window。例如办公室与餐厅之间的一条模糊电梯画面。

### 2.4 Transition Moment / 过渡 Moment

S05 为保证每个 Window 最终只有一个确定归属而建立的内部独立 Moment。它可以只包含一个 Window，也可以包含一个最小、连续、内部已确认相容的 unresolved pending block。

`Transition Moment` 是内部分段与审计结构，不是 Chapter、Aha 或 App 页面模块。

### 2.5 DROP from Memory output / 不进入记忆输出

只表示该 Window 不进入 Chapter、Aha 或最终精选素材。它不删除 RawAsset，不删除 Observation，不删除 BoundaryEvidenceLedger，也不影响 Manual 素材继续出现在独立 Manual 窗口。

## 3. DEFER 生命周期

```text
new Window
→ BoundaryEvidenceLedger
→ MERGE | SPLIT | DEFER

DEFER
→ PendingTransitionBuffer
→ limited later evidence
   ├─ evidence supports left/right placement → normal MERGE/SPLIT commit
   └─ still cannot place reliably → UNRESOLVED + isolated Transition Moment
```

冻结要求：

1. `DEFER` 期间 Window 只进入 V1.13 Pending，不更新已有 Core/Tail；
2. 后续证据能够可靠解决归属时，仍按 V1.12/V1.13 的正常 MERGE/SPLIT 路径提交；
3. 只有“允许证据用尽，并且左、右归属都不能可靠成立”时才使用 Transition fallback；
4. fallback 不再比较“勉强更像左边还是右边”，而是隔离不确定性；
5. `UNRESOLVED` 继续作为诊断状态保存，Transition Moment 是它在确定 partition 中的物化结果；
6. 已提交 Revision 中每个 accepted Window 仍恰好归属一个 Moment。

## 4. 如何物化 Transition Moment

单个过渡 Window：

```text
A | B | C
    ↑
isolated Transition Moment
```

其中 A、C 是左右局部 Episode，B 对两边都无法可靠归属。B 两侧的已提交 membership 均保持切开，不能用 B 更新 A 或 C 的语义 Core。

如果 Pending 中有多个连续 Window：

- 只把最小 unresolved block 隔离；
- block 内只有已被独立 continuity evidence 支持的相邻 Window 才能 MERGE；
- block 内仍 unresolved 的 seam 继续保守切开；
- 不能因为都“不知道属于哪里”就把多个不相关 Window 合成一个 Transition Moment。

Transition 标记不能成为新的边界证据来源；它只是已有 unresolved 证据的结果，避免循环自证。

## 5. S06/S07 三路简化路由

### 5.1 KEEP → Aha Candidate

Transition Moment 中的素材只有同时满足下列方向，才允许标记为 `KEEP` 并进入 S07 Aha Candidate：

- 素材本身可被独立理解，不依赖强行归入左/右 Episode；
- grounded Observation 足以支持相关事实，Evidence 本身可读；
- 具有一个可能独立成立的具体短暂事件信号；
- 不是纯移动、低信息转场、边界不明确本身或同 Transition 内无贡献的重复表达；
- 通过 V1.16 普通 KEEP 门与 Transition 附加门。

`KEEP` 只是获得 Aha 候选资格，不代表已经具有独立记忆价值，也不代表最终媒体合格或一定输出。S07 判断 Aha 价值与候选重复，S08/S09 进行验证与集合选择，S10 决定最终媒体。

Transition Moment 不因被隔离而自动成为独立 Chapter 候选。

### 5.2 CONTEXT_ONLY

素材没有通过 V1.16 Transition KEEP 门，但仍具有明确、未被其他内容或 ledger 覆盖的正向上下文用途时，标记为 `CONTEXT_ONLY`。例如清楚的电梯、门口、走廊或短暂移动画面可以约束下游如何解释场景转换。

`CONTEXT_ONLY`：

- 不进入 Chapter/Aha 的精选素材计数；
- 可以继续服务于边界解释、审计与 Narrative 的安全限制；
- 不能凭自身产生用户可见记忆。

### 5.3 DROP

若素材没有通过 V1.16 Transition KEEP 门，也没有必要的正向上下文用途，则使用 S06 `DROP`：

- 从 Chapter/Aha candidate pool 和最终 Memory 输出中排除；
- 保留事实、状态、失败原因、边界引用和版本 Trace；
- 不触发 RawAsset 删除；
- Manual 素材仍按 V1.6 保留在独立 Manual 窗口。

因此这里的“删掉”严格解释为 `DROP_FROM_MEMORY_OUTPUT`，不是物理删除或事实抹除。

## 6. 示例

### 6.1 可以进入 Aha 候选

```text
A：办公室工作
B：街头艺人的短暂精彩表演
C：餐厅用餐
```

B 无法可靠归入办公室或餐厅，但自身内容清晰、可独立理解，并具有具体短暂事件信号，因此可获得 Aha candidacy；实际独立价值仍由 S07 判断：

```text
A | B | C
    ↓
Transition Moment
    ↓
KEEP → Aha Candidate
```

### 6.2 只作上下文

```text
A：办公室工作
B：电梯和离开建筑的画面
C：餐厅用餐
```

B 没有通过 Transition KEEP 门，但具有未被其他 Evidence 覆盖的转场解释用途：

```text
Transition Moment → CONTEXT_ONLY
```

### 6.3 不进入 Memory

```text
A：办公室工作
B：严重模糊、遮挡且无可用事实
C：餐厅用餐
```

B 既没有通过 Transition KEEP 门，也没有必要的上下文贡献：

```text
Transition Moment → DROP_FROM_MEMORY_OUTPUT
```

其 RawAsset、Observation status 与边界诊断仍保留。

## 7. 为什么不强制归左或归右

强制二选一会产生两类风险：

1. 将无关素材污染一个已经稳定的 Moment Core，增加 False Merge；
2. 为一个不重要的过渡画面增加复杂评分、规则和调参成本。

Transition fallback 接受少量内部 over-segmentation，以换取：

- 更低的错误合并风险；
- 更简单、可解释的状态机；
- 更明确的 Aha / Context / Drop 分工；
- 不把内部 Moment 数量误当成用户可见 Chapter 数量。

这符合 Diary One 已冻结的 precision-first 原则：漏掉一条不确定素材的 Memory 资格，通常比制造错误生活事件更可接受。

## 8. 成本边界

本规则默认复用已有：

- BoundaryEvidenceLedger；
- PendingTransitionBuffer；
- Window-local Observation；
- S03/S04 的质量、时间、Activity、Scene、Motif 与 prototype 信号。

默认不增加：

- Phone→Cloud Raw 上传；
- Auto 补帧或回取；
- 每个 unresolved seam 的强模型调用；
- 为强行左/右归属建立复杂场景补丁。

新增成本主要是有界状态记录和 S06/S07 的结构化路由，预计远低于 S04 multimodal Observation，但仍需在真实实现中测量。

## 9. 真实数据校准

后续标注应分开记录：

| 标注问题 | 对应调整 |
|---|---|
| B 实际应归左、归右还是独立 | S05 transition placement |
| DEFER 是否等待了合适数量的后续 Window | lookahead policy |
| 独立 B 是否具有 Aha 价值 | S07/S08 value gate |
| B 是否仍应作为上下文保留 | S06 role assignment |
| B 最终未展示是否合理 | S09 set selection / user feedback |

至少跟踪：

- DEFER rate；
- resolved-before-limit rate；
- unresolved transition rate；
- transition placement accuracy；
- False Merge / False Split；
- Transition→Aha precision；
- CONTEXT_ONLY usefulness；
- DROP regret rate；
- 跨 Preview Revision 的 boundary stability；
- 额外成本与延迟。

用户“不喜欢这个 Aha”不能直接被解释为 S05 分段错误；必须先区分事实、边界、独立价值、重复和呈现问题。

## 10. FROZEN 与 OPEN

### FROZEN

- `DEFER` 仍先使用有界的已有后续证据，不立即丢弃；
- 只有证据用尽且不能可靠归左或归右时，才进入 unresolved transition fallback；
- fallback 不强制归左或归右，而是物化独立 Transition Moment；
- `UNRESOLVED` 是诊断状态，Transition Moment 是确定 partition 中的内部结果，不新增第五种 boundary state；
- Transition Moment 不能污染左右 Moment 的 Core/Tail；
- 每个 accepted Window 在已提交 partition 中仍恰好归属一次；
- Transition Moment 后续只走 KEEP-for-Aha-candidacy、CONTEXT_ONLY 或 DROP 三条内容路径；
- Transition 不自动成为 Aha；S06 只授予 candidacy，S07 必须再通过独立记忆价值、重复与证据门；
- Transition Moment 不因隔离而自动成为 Chapter Candidate；
- `DROP` 只从 Memory candidate/output 排除，不删除 RawAsset、Observation、ledger 或 Manual 窗口内容；
- 默认不增加 Raw 上传、补帧或逐 seam 强模型调用；
- 真实数据必须分别校准边界归属、Aha 价值、上下文用途和最终用户反馈。

### OPEN / 下一节点或真实数据校准

- V1.15 当前 2 Window / 6 分钟 / 3 Pending Baseline 的真实数据再校准与版本化升级；
- EvidenceSufficiencyGate、capture-scope stop 和 termination reason 的具体阈值与 Production schema；
- Transition Moment / route reason 的 Production schema 与 reason-code taxonomy；
- V1.16 已冻结角色语义；Production role / route schema、reason taxonomy 与具体阈值；
- S07 Aha 独立价值、候选重复和证据门；
- S10 最终媒体质量门；
- late insertion 后局部重算、Preview 修订与 stable Moment ID；
- Final 后是否及何种条件允许重新打开旧 unresolved seam；
- Gold 标注协议、样本量与用户分层。

## 11. 当前实现 GAP

- 当前仓库没有 Production Pending/lookahead/Transition Moment engine；
- 尚未实现 Transition 的确定 partition Validator；
- V1.16 已冻结 KEEP-for-Aha、CONTEXT_ONLY、DROP 的语义，但正式 route schema/engine/Validator 尚未实现；
- E00/X01 都不符合本检查点的分阶段逻辑；
- 尚无真实 wearable Gold 用于测量 transition placement、Aha precision 或 DROP regret；
- V1.15 已冻结当前 lookahead/Pending Baseline，V1.16 已冻结 S06 全量角色合同；Production engine、S07 Aha scoring 与 Revision 重算策略仍未实现。

## 12. 下次继续的准确节点

V1.15 已完成 S05-D，V1.16 已完成 S06。下一步进入 S07 Chapter/Aha Candidate Generation：

```text
Candidate unit and route
→ Chapter local Episode scope
→ RESUMED_EPISODE / LOCAL_EPISODE_GROUP
→ Aha independent-value gate
→ candidate duplicate / reject audit
```

下一步不重开 V1.14 fallback、V1.15 lookahead 或 V1.16 role contract，也不提前进入 S08 enrichment、S09 集合选择或 Narrative。
