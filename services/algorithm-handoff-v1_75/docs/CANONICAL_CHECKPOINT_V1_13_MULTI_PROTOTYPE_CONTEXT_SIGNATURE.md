# Diary One Canonical Checkpoint V1.13 — Multi-Prototype Context Moment Signature

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** S05-C 多原型 Context Signature、Core/Tail/Pending 更新边界，以及真实数据校准槽位
**继承关系：** 继承 V1.12–V1.1 与 V1.0 未被覆盖的规则

> **当前 unresolved transition 覆盖：** V1.14 已冻结证据用尽且仍不能归左/归右时的 fallback：Pending 不写入相邻 Core，而是物化独立 Transition Moment，再进入 Aha 候选、CONTEXT_ONLY 或 DROP 路由。

> **当前 DEFER 覆盖：** V1.15 已冻结当前 Pending/lookahead 长度 Baseline、完整 seam pattern 提前结束、同一不可变证据快照解析，以及完成后原子更新 Core/Tail。

> **当前 S06 覆盖：** V1.16 只在 S05 提交后分配 Observation 内容角色；S06 不因 KEEP、Context 或 Drop 改写本文的 Core/Tail/Pending、Moment membership 或 boundary decision。

## 1. 冻结结论

S05 的 `Moment Signature` 不能只保存一个平均 embedding，也不能要求同一 Moment 的每个 Window 出现相同物体。正式采用：

```text
Moment Signature
= Multi-Prototype CoreContextSignature
+ TailSignature
+ PendingTransitionBuffer
```

它的目标是同时解决：

1. 防止 A≈B、B≈C、C≈D 导致整段逐步漂移；
2. 允许“石板路、古建筑、老街店铺、院落”等不同视觉外观共同支持一个“传统历史街区”上下文；
3. `DEFER` Window 在确认前不污染已经建立的 Core；
4. 将稳定架构与未来真实用户数据要校准的参数严格分开。

## 2. 术语释义

### 2.1 Context / 上下文语境

不是单个物体，而是多个 Window 共同表现出的环境、活动和时间关系。例如：

```text
石板铺装
+ 传统建筑立面
+ 老街店铺
+ 连续步行
+ 相近时间与 Session
→ “传统历史街区漫步”的上下文证据
```

### 2.2 Motif / 语境线索

从 grounded Observation 中派生的可重复小线索，例如“石板铺装”“传统屋檐”“老街店面”。Motif 必须引用来源 Fact、Window 和 Frame；它不是凭空生成的标签。

### 2.3 Prototype / 视觉原型

代表一种典型视觉外观的样本或向量。可以理解为“同一环境中的一种代表性长相”。

### 2.4 Multi-Prototype / 多原型

同一个 Context 可以保存少量不同视觉原型，而不是强行平均成一张不存在的“平均画面”。例如古镇语境可以同时保存石板路、建筑立面、牌坊和店铺原型。

### 2.5 CoreContextSignature / 核心语境轮廓

由已经确认属于当前 Moment 的可靠 Window 构成，更新较慢，用于表达当前 Moment 相对稳定的上下文。

### 2.6 TailSignature / 近期轮廓

由最近少量、已经确认 MERGE 的可靠 Window 构成，更新较快，用于识别自然转场与最新状态。

### 2.7 PendingTransitionBuffer / 待确认缓冲区

临时保存处于 `DEFER` 的 Window。Pending 不是 Moment 的已确认成员，在决策完成前不能改写 Core 或 Tail。

### 2.8 ContextThemeHypothesis / 上下文主题假设

由多个 grounded Motif 和结构信号共同支持的中间假设，例如“传统历史街区”。它用于 S05 continuity 判断，不是已确认地点名称、最终 Chapter 标题或用户意图。

## 3. Moment Signature 的三部分

### 3.1 Multi-Prototype CoreContextSignature

Core 至少能够表达：

- 已确认成员 Window 与贡献引用；
- reliable Scene / Activity distribution；
- Activity Thread，例如持续或反复出现的 `MOBILITY / WALKING`；
- grounded context motifs 与反证；
- bounded visual prototypes；
- 可选的单一 centroid 诊断，但不能作为唯一视觉表示；
- trusted time / capture session / coarse location structure；
- 匿名 entity/object hint distribution，不代表身份识别；
- evidence-support distribution、UNKNOWN gaps 与 contradictions；
- signature algorithm/version/parameter/provenance。

Core 不是一段生成式 Caption，不包含“值得记住”“古镇 Citywalk Chapter”等编辑判断。

### 3.2 TailSignature

Tail 保存最近一小段已确认成员的结构化表示：

- recent committed Window IDs；
- recent Scene / Activity / motifs；
- recent prototypes 或 embedding references；
- recent time gaps、session 与 contradiction；
- Tail 版本与 contributor provenance。

Tail 的 Window 数量、时间跨度和衰减方式保持 OPEN，但必须有界。

### 3.3 PendingTransitionBuffer

Pending 至少保存：

- 尚未提交的 Window IDs 与顺序；
- 对应 BoundaryEvidenceLedger；
- pending Window 的 Observation status 与可靠事实；
- lookahead 已使用数量；
- 可能的 merge/split seam；
- state-transition Trace。

Pending 必须有界，且不能被当作已确认 Core 证据。

## 4. 为什么单一 centroid 不够

单一 embedding centroid 会把不同视觉模式平均到一起：

```text
石板路 embedding
+ 古建筑 embedding
+ 店铺 embedding
→ 一个模糊平均点
```

这会造成两个问题：

1. 新的石板路画面可能离平均点反而不够近；
2. 平均点可能接近许多普通街景，降低区分度。

因此：

- centroid 可以保留为低成本 baseline 或诊断；
- continuity 判断必须允许新 Window 匹配 Core 中任一兼容 prototype；
- 不能只因匹配一个 prototype 就 MERGE，仍需时间、Session、Activity 和 boundary evidence；
- prototype 不是全日聚类中心，只在当前连续 Moment 内有效。

prototype 的数量、选择、替换、合并和距离阈值必须通过真实数据 Benchmark 校准，本检查点不武断冻结。

## 5. Context Motif 与主题假设

S05 可以从 V1.10 的 grounded Scene、Activity、Object 和 Atomic Fact 派生版本化 Motif。例如：

| Grounded Observation | 可派生 Motif |
|---|---|
| “道路由石板铺成” | stone-paved street |
| “可见传统屋檐与木质立面” | traditional architecture |
| “沿街分布小型店铺” | old-street retail pattern |
| 多个 Window 支持步行 | walking activity thread |

每个 Motif 必须保留：

- source fact / Window / Frame references；
- source support grade；
- motif mapper/version；
- contradiction / ambiguity；
- 是否只在当前 Window 出现，还是被多个 Window 重复支持。

多个 Motif 可以形成 `ContextThemeHypothesis`，但必须遵守：

1. 主题假设是派生上下文，不改写 S04 原事实；
2. 一个孤立物体不能单独建立宽泛主题；
3. 主题必须保留支持证据与反证；
4. “传统历史街区风格”不等于已确认真实古镇；
5. 真实地点名称需要可信 GPS、地名文字、用户输入或其他独立证据；
6. S05 只用主题假设辅助 continuity，不在此生成 Chapter 标题。

Motif taxonomy、主题形成算法与最低证据要求保持 OPEN，并通过真实数据校准。

## 6. Core / Tail / Pending 的更新合同

### 6.1 新 Moment 初始化

- 新 Moment 的第一个 `OBSERVED` 或 `PARTIAL` Window 可用其 `STRONG/MODERATE` grounded items 初始化 Core 与 Tail；
- `WEAK` 不进入语义 Core；
- 若第一个 Window 为 `UNKNOWN / INSUFFICIENT_EVIDENCE / FAILED`，只初始化时间、Session、状态和缺口，语义 Core 保持空。

### 6.2 `MERGE` 提交

只有 boundary working decision 已提交为 `MERGE` 时：

1. Window 才正式成为当前 Moment 成员；
2. 更新 Tail；
3. 依据版本化规则更新 Core motifs、prototypes 和 distributions；
4. 保存更新前后 signature fingerprint 与 contributor refs。

单个新 Window 不能无痕覆盖已有 Core。

### 6.3 `DEFER`

- Window 进入 Pending；
- Core 与 Tail 保持不变；
- 后续 lookahead 只追加 Pending 和新账本；
- 不允许用 Pending 更新后的“新 Core”反过来证明自己应该 MERGE。

这条规则用于防止自我强化式错误合并。

### 6.4 `DEFER → MERGE`

当后续证据解决不确定性并确认 MERGE：

- Pending Window 按时间顺序原子性提交到当前 Moment；
- 再更新 Tail 和 Core；
- 保存是哪条后续证据解决了哪个 seam。

### 6.5 `SPLIT` 或 `UNRESOLVED → materialized SPLIT`

- 当前 Core/Tail 在边界前封口；
- Pending 不写入旧 Core；
- Pending 中属于新侧的 Window 用于初始化新 Moment；
- 能被后续证据可靠归入新侧的 Window 用于初始化新 Moment；仍不能归左/归右的 Window 按 V1.14 隔离为 Transition Moment；
- unresolved 诊断继续保留。

## 7. Core 与 Tail 的双重比较

新 Window 进入 V1.12 双向账本前，分别与 Core 和 Tail 比较：

| 与 Core | 与 Tail | 对账本的典型含义 |
|---|---|---|
| 上下文连续 | 近期也连续 | 增加 continuity evidence |
| 不连续 | 近期连续 | 可能逐步漂移或自然转场，优先 DEFER |
| 连续 | 近期不连续 | 可能是短暂干扰、异常或返回旧模式，优先 DEFER |
| 都不连续 | 都不连续 | 增加 boundary evidence，但仍与其他信号共同判断 |

“连续/不连续”不是单一 embedding 判定，而是时间、Session、Activity、Motif、prototype、Scene、location 与 contradiction 的双向证据结果。

Core 防止长链漂移；Tail 防止 Core 过于僵硬而把合理转场全部切开。

## 8. 古镇 Citywalk 示例

输入：

```text
W1 石板路
→ W2 只有古建筑
→ W3 再次出现石板路
```

可能的结构化处理：

### W1

- Atomic Fact：石板铺装道路；
- Activity：MOBILITY/WALKING；
- Motif：stone-paved street；
- 初始化一个传统街区 Context 的早期证据与石板路 prototype。

### W2

- 没有石板路，不要求与 W1 共享同一物体；
- Atomic Fact：传统屋檐、木质或历史风格立面；
- Motif：traditional architecture；
- 若时间、Session、步行 Activity 与位置连续，则向 continuity ledger 提供 Context 兼容证据；
- Scene/对象变化同时可以进入 boundary ledger；
- 两边均有证据时暂存 Pending，而不是立即 SPLIT。

### W3

- 再次支持 stone-paved street prototype；
- 同时与已出现的 traditional architecture motif 组成多视角 Context；
- 如果没有强 boundary contradiction，W3 可以帮助把 W2 的 DEFER 解析为同一连续游览；
- 确认 MERGE 后，再把 W2/W3 原子性写入 Core。

最终可能形成同一 Moment，也可能因强转场被保守切成相邻 Moments。即使切成多个 Moment，S07 仍可在局部连续 Episode 范围组成一个 Chapter Candidate。

## 9. “古镇 Citywalk”不是由视觉风格单独决定

形成“古镇或老街漫步”Chapter 候选至少需要组合证据：

- 时间与 Session 属于同一局部游览；
- Activity Thread 支持步行或游览，而不是只看到静态建筑；
- 多个 Window 提供互补且 grounded 的传统街区 Motif；
- 没有中间无关 Episode 或强 boundary contradiction；
- S07 的 local Episode grouping 与记忆价值门通过。

仅凭石板路、仿古建筑或相似滤镜不能断言：

- 真实地点一定是古镇；
- 用户正在进行 Citywalk；
- 分散在全天的相似画面属于同一 Moment。

没有可靠地点身份时，后续用户可见文字优先使用“老街漫步”“传统街区散步”等证据强度匹配的表述；具体 Narrative 仍由 S11/S12 验证。

## 10. 防止多原型变成全天主题聚类

Multi-prototype 只在 V1.11 已冻结的连续 Moment 候选范围内工作：

- 一个 Moment 的 prototype 不跨越已提交 SPLIT 自动延伸；
- 上午和晚上出现相似石板路仍是不同 Moment；
- 中间出现独立 Episode 时，后续相似内容走 S07 的 Resumed/Local Episode 关系；
- visual/context similarity 不能绕过时间、Session 与 BoundaryEvidenceLedger；
- prototype 不能成为人物身份、地点身份或 Chapter 价值的证明。

因此多原型解决的是“同一连续语境的多种外观”，不是恢复全日任意主题聚类。

## 11. 成本边界

默认实现使用已有：

- S03A Window embedding；
- S03B Edge；
- S04 grounded Scene / Activity / Object / Atomic Fact；
- capture time、Session 与可选 trusted location。

架构要求：

- 不新增 Phone→Cloud Raw 上传；
- 不为每个 Window 或 seam 默认调用强模型；
- Motif mapper、prototype update 与 signature comparison 必须可批量、可缓存、可版本化；
- prototype 数量与 Pending 长度必须有界；
- 额外语义归一化若需要模型，必须作为可测量的候选方案，不自动成为 Production 默认。

## 12. 真实数据、用户标注与算法校准边界

当前先冻结结构，后续使用真实素材与不同用户的标注、纠错和评分调整可校准部分。

至少应把标注错误类型分开：

| 标注/反馈 | 主要调整阶段 |
|---|---|
| Window 看错了什么 | S04 perception / motif source |
| 两个相邻 Window 是否同一局部 Episode | S05 boundary |
| Context Motif 或主题假设是否正确 | S05 Context Signature |
| 多个 Moment 是否应组成同一 Chapter | S07 candidate grouping |
| 这个 Chapter/Aha 对用户是否有价值 | S08/S09 scoring / personalization |
| 标题或文字是否准确 | S11/S12 narrative validation |

不能把用户“不喜欢这个 Chapter”直接解释为 S05 边界错误，也不能用主观偏好改写 S04 事实。

真实数据调整必须遵守：

1. architecture invariant 与可校准 parameter 分开；
2. embedding 模型、Motif mapper、prototype 数量、阈值、权重、Tail 长度和 lookahead 都有版本；
3. 每次调整在冻结的 Gold / held-out 数据上比较 False Merge、False Split、Context accuracy 与下游 Chapter 质量；
4. 不同用户、生活方式、地点和拍摄质量分层评估，不能只优化少数用户；
5. 用户偏好主要进入后续 Memory 价值与排序层，不反向篡改事实；
6. 不做不可追溯的在线自我修改；升级必须形成实验记录、错误归因和新 Checkpoint。

本检查点不提前冻结具体标签体系、评分尺度或样本量；这些在真实数据工作阶段单独设计。

## 13. FROZEN 与 OPEN

### FROZEN

- Moment Signature 采用 Multi-Prototype CoreContextSignature + TailSignature + PendingTransitionBuffer；
- 单一 centroid 不能成为 Moment Context 的唯一表示；
- 同一连续 Context 可包含多个互补视觉 prototype；
- Context Motif 必须源自 grounded Observation 并保留 Fact/Window/Frame provenance；
- ContextThemeHypothesis 是派生假设，不改写事实，也不是最终 Chapter 标题；
- 只有 committed MERGE 才能更新现有 Core/Tail；
- DEFER Window 只进入 Pending，不污染 Core/Tail；
- DEFER 解析为 MERGE 后，Pending 按顺序原子性提交；
- SPLIT 时 Pending 不写入旧 Core；
- `WEAK/UNKNOWN/INSUFFICIENT_EVIDENCE/FAILED` 不更新语义 Core；
- Core 与 Tail 分别参与 continuity/boundary 判断；
- 多原型只在连续局部 Episode 内工作，不恢复全日主题聚类；
- 古镇/Citywalk 等高层语境必须由多信号、多 Window grounded evidence 支持；
- 视觉风格不能单独证明真实地点身份或用户意图；
- 默认不增加 Raw 上传或逐 seam 强模型调用；
- 冻结架构与可校准参数必须分开，后续参数调整版本化、可评测、可回溯；
- 用户主观偏好不能改写 perception facts 或被直接当作 boundary truth。

### OPEN / 下一步讨论或真实数据校准

- prototype 数量、选择、替换、合并和距离算法；
- centroid 是否作为辅助特征及其权重；
- Motif taxonomy、mapper 与 ContextThemeHypothesis 形成规则；
- 多个独立线索达到 Context 支持的门；
- Core/Tail 各信号的聚合、衰减和矛盾处理；
- Tail 的 Window 数量或时间跨度；
- V1.15 Pending/lookahead Baseline 的 Production engine、真实数据再校准与参数升级；
- 可被证据解决的 transition placement 架构已由 V1.15 覆盖，具体 EvidenceSufficiencyGate 继续 OPEN；证据用尽后的 unresolved fallback 以 V1.14 为准；
- embedding 模型、维度与更新版本；
- 真实地点身份的 GPS/文字/用户输入验证合同；
- 标注 Schema、评分量表、用户分层、样本量与实验协议；
- full-day/local recompute 与 Moment stable ID。

## 14. 当前实现 GAP

- 当前仓库没有 Production CoreContextSignature、TailSignature、PendingTransitionBuffer 或 ContextThemeHypothesis schema；
- 尚未实现 grounded Motif mapper、多原型维护、commit-on-MERGE 或 pending isolation；
- E00 的单一 centroid 与 pairing 只有工程 Smoke 意义，不符合本检查点；
- X01 没有独立 S05 Context Signature；
- 尚无真实用户数据与 Gold 用于校准 Context、prototype、boundary 或 Chapter grouping；
- V1.14/V1.15 已覆盖 unresolved transition fallback 与当前有界 lookahead Baseline，V1.16 已冻结 S06 全量角色合同；S07 Candidate Generation 与 Chapter/Aha 最终选择仍未冻结。
