# Diary One Canonical Checkpoint V1.16 — S06 Observation Role Assignment and S07 Handoff

**状态：** FROZEN
**冻结日期：** 2026-08-26
**决策来源：** 用户逐项确认 S06-A～F，并确认交叉检查收紧项
**作用范围：** S06 对普通 Moment 与 Transition Moment 的 Observation 主角色、候选内容为空的处理、局部重复抑制、Revision 一致性，以及向 S07 的交接边界
**继承关系：** 继承 V1.15–V1.1 与 V1.0 未被覆盖的规则

## 1. 冻结结论

S06 在 S05 已经提交完整 Moment partition 之后运行。它不重新分段，而是为当前 Revision 中每个 accepted Observation 分配且只分配一个主角色：

~~~text
KEEP
CONTEXT_ONLY
DROP_FROM_MEMORY_OUTPUT
~~~

完整阶段顺序为：

~~~text
S04 Window-local Observation facts
→ S05 contiguous Moment partition and boundary ledgers
→ S06 one primary role per Observation
→ derive one Moment-level routing result
→ emit one shared handoff packet per Moment
→ S07 Chapter / Aha Candidate Generation
~~~

主角色互斥，但每个角色可以携带多个 reason code 与证据引用。

S06 的核心职责是回答：

> 当前 Observation 是否具有可靠的内容贡献；若不具有，它是否仍有明确的上下文用途；否则是否应退出 Memory 内容路径。

S06 不回答：

- 这个 Moment 是否最终值得成为 Chapter；
- 这个局部峰值是否最终值得成为 Aha；
- 全日应选择多少 Chapter / Aha；
- 最终展示哪张照片或哪段视频；
- 标题、故事、意义或用户情绪；
- 是否应重新打开或修改 S05 边界。

## 2. 术语释义

### 2.1 Primary Role / 主角色

每个 accepted Observation 在同一个已提交 Revision 中必须恰好拥有一个主角色。一个 Observation 不能同时既是 KEEP 又是 CONTEXT_ONLY，也不能没有角色。

### 2.2 Role Reason / 角色原因

解释为什么分配该角色的一个或多个可审计原因。例如：

- reliable_content_contribution；
- unique_context_utility；
- insufficient_evidence；
- processing_failed；
- MEMORY_SUPPRESSED_DUPLICATE；
- no_downstream_utility。

这些名称只是说明性例子；完整 Production reason-code taxonomy 仍为 OPEN。

Reason 不是第四种角色。特别是 MEMORY_SUPPRESSED_DUPLICATE 只能是 CONTEXT_ONLY 或 DROP_FROM_MEMORY_OUTPUT 的原因，不能与三种主角色并列。

### 2.3 Candidate-empty Moment / 候选内容为空的 Moment

一个 S05 Moment 仍包含 Observation，但 S06 分配后没有任何 KEEP。

它不是结构为空，也不表示该时间段不存在。它只表示当前 Revision 中没有内容可以继续竞争 Chapter/Aha。

### 2.4 Candidate Seed / 候选种子

S06 为一个具有 KEEP 的 Moment 输出的共享交接资料包。它只是 S07 的输入，不是 ChapterCandidate、AhaCandidate 或最终页面。

### 2.5 Context Envelope / 上下文包

没有 KEEP、但存在 CONTEXT_ONLY 的 Moment 向下游提供的精简结构。它用于限制误读、保留顺序或解释局部转场，不生成用户可见 Memory。

## 3. S06 的不可变输入与提交顺序

S06 只读取同一个 immutable Day Revision 中的：

- 已提交 S05 Moment membership 与 Moment type；
- 按时间排序的 Observation；
- S04 顶层状态、逐条 grounded facts、support grade 与 limitations；
- Window / RawAsset / Frame / source / capture facts；
- S03/S05 continuity evidence 与 boundary evidence 的引用；
- 当前版本允许使用的局部相似度、重复组与 Moment Signature 信息。

角色分配使用以下顺序：

~~~text
validate one immutable Revision
→ apply S04 status eligibility
→ evaluate reliable content contribution
→ apply ordinary or Transition KEEP gate
→ resolve local duplicate groups as a group
→ if not KEEP, evaluate positive context utility
→ otherwise DROP
→ atomically commit all Observation roles for the Moment
→ derive Moment-level route
→ emit S07 handoff
~~~

禁止边判断边修改 S04 facts、S05 Core/Tail 或 Moment membership。

相同 immutable input snapshot、相同 schema/algorithm/parameter version 必须得到相同角色结果。

## 4. 状态到角色的硬门

V1.10 的四种顶层状态在 S06 中解释如下：

| S04 status | KEEP | CONTEXT_ONLY | DROP_FROM_MEMORY_OUTPUT |
|---|---|---|---|
| OBSERVED | 可通过后续门 | 可 | 可 |
| PARTIAL | 只使用已被支持字段，可通过后续门 | 可 | 可 |
| INSUFFICIENT_EVIDENCE | 禁止 | 仅限非 Claim 的独特上下文用途 | 默认路径 |
| FAILED | 禁止 | 禁止作为内容角色 | 当前已提交 Revision 的固定路径 |

补充规则：

1. UNKNOWN 是字段值，不是第五种顶层状态；
2. 一个 OBSERVED/PARTIAL Observation 想成为 KEEP，必须至少有一个与当前贡献相关的 STRONG 或 MODERATE grounded item；
3. grounded item 只能引用当前 Window 实际输入 Frame；
4. PARTIAL 只能使用被当前证据支持的字段，不能补写缺失部分；
5. INSUFFICIENT_EVIDENCE 不存在 STRONG/MODERATE item，因此不能 KEEP；
6. INSUFFICIENT_EVIDENCE 的 WEAK item 只能作为不确定性、上下文或以后验证的提示，不能成为用户可见 Claim；
7. FAILED 是处理失败，不代表现实中没有内容；其系统 Envelope、时间位置、失败原因与 ledger 仍保留，但当前 Observation 的主角色为 DROP_FROM_MEMORY_OUTPUT；
8. 多个 WEAK 提示不能通过数量投票升级为 STRONG/MODERATE，也不能在 S06 合成为确定事实；
9. S06 不改写任何 S04 support grade。
10. MODERATE 可以通过 KEEP 的事实门，但原 support grade、限制与 Frame grounding 必须原样交给下游；S08 可以定向验证，S06 不得静默升级。

## 5. 普通 Moment 的 KEEP 合同

普通 Moment 中，一个 Observation 只有同时通过以下两个门，才可以成为 KEEP：

~~~text
Reliable Fact Gate
AND
Moment Content Contribution Gate
~~~

### 5.1 Reliable Fact Gate

必须同时满足：

- status 为 OBSERVED 或 PARTIAL；
- 至少一个与本次内容贡献直接相关的 STRONG/MODERATE grounded item；
- 事实引用当前 Window Frame；
- 不借用相邻 Window 补写本 Window；
- 不把 WEAK、UNKNOWN 或缺失字段升级为肯定性事实。

### 5.2 Moment Content Contribution Gate

必须至少满足一项：

1. 建立该 Moment 的主要可见活动或环境；
2. 增加一个不同且有意义的阶段、动作或局部变化；
3. 增加可被可靠观察、对理解该 Episode 有实际帮助的互补背景或 Motif；
4. 用自身 STRONG/MODERATE 事实，为 Moment 中一个重要事实增加独立佐证或覆盖。

第 4 项不能改写原来的 support grade，也不能把多个 WEAK 合成确定事实。

### 5.3 单独不足以获得 KEEP 的信号

以下任一项单独存在都不够：

- 画面漂亮；
- 来源是 Manual；
- 用户主动拍摄；
- 与 Moment 视觉相似；
- 与相邻素材时间接近；
- 模型认为 interesting；
- 只具有边界用途；
- 为了凑 Chapter/Aha 或精选素材数量。

Manual intent 可以作为以后候选价值的信号，但不能绕过 Truth Gate、内容贡献门或重复抑制。

### 5.4 KEEP 的准确含义

KEEP 只表示该 Observation 可以作为可靠内容证据继续进入候选路径。

KEEP 不表示：

- 一定形成 Chapter/Aha；
- 一定成为最终 3～5 个精选素材之一；
- 一定适合最终展示；
- 一定具有独立记忆价值；
- 一定在后续 Revision 中保持不变。

普通 Moment 的价值、意义、显著性、个人相关性与候选组合由 S07 以后判断。

## 6. CONTEXT_ONLY 合同

没有通过 KEEP 的 Observation，只有在存在明确、具体且不重复的下游用途时，才可以成为 CONTEXT_ONLY。

### 6.1 Positive Context Utility / 正向上下文用途

至少满足一项：

1. 帮助理解两个 KEEP 内容之间的可见过程或顺序；
2. 防止下游把短暂路过、拍摄空白或场景变化写成持续活动；
3. 提供一个不适合作为主要内容、但能约束附近 KEEP 解释的 grounded context；
4. 提供 WEAK 但明确标记为非 Claim 的不确定提示，供安全限制或以后验证使用。

### 6.2 Removal Test / 去除测试

判断问题为：

> 如果不把该 Observation 放入下游活跃上下文，S07 是否会明显更容易误解、过度描述或错误连接这段经历？

- 若会，并且该作用尚未被其他 Observation 或 ledger 充分覆盖，可以 CONTEXT_ONLY；
- 若不会，应当 DROP_FROM_MEMORY_OUTPUT。

CONTEXT_ONLY 不能成为“可能以后有用”的兜底垃圾桶。

### 6.3 CONTEXT_ONLY 的限制

CONTEXT_ONLY：

- 不生成 Chapter/Aha Candidate；
- 不计入 Chapter 的 3～5 个精选素材；
- 不能独立产生用户可见 Memory Claim；
- 不能被 S11 Writer 当作肯定性事实来源；
- 可以限制叙事、说明时间顺序、支持审计或提示验证；
- 不会因为以后画面看起来漂亮而在 S10 被直接升级为精选素材。

## 7. DROP_FROM_MEMORY_OUTPUT 合同

若 Observation 既没有可靠内容贡献，也没有明确的正向上下文用途，则分配 DROP_FROM_MEMORY_OUTPUT。

典型原因包括：

- FAILED；
- INSUFFICIENT_EVIDENCE 且没有独特上下文用途；
- 严重遮挡、损坏或不可理解；
- 完全重复且没有额外事实或上下文贡献；
- 只有审美吸引力，没有可靠语义贡献；
- 唯一理由只是 Manual、时间相邻或“舍不得丢”；
- 其全部上下文作用已经被更可靠 Observation 或 ledger 覆盖。

DROP_FROM_MEMORY_OUTPUT 只影响 Memory candidate/output：

- 不删除 RawAsset；
- 不删除 Evidence；
- 不删除 Observation；
- 不删除 S05 membership；
- 不删除 continuity/boundary ledger；
- 不删除失败与版本 Trace；
- 不影响 Manual 素材继续出现在独立 Manual 窗口。

低审美质量本身不自动等于 DROP；只有证据不可读或缺乏内容/上下文贡献时，才影响 S06 角色。

## 8. S06 角色与 S05 边界的因果方向

S06 在 S05 之后运行，因此：

- KEEP、CONTEXT_ONLY、DROP 不能成为新的 S05 continuity/boundary evidence；
- 角色不能证明此前的 MERGE、SPLIT、DEFER 或 UNRESOLVED；
- 无论最终角色是什么，S03/S05 已保存的双向证据账本继续存在；
- CONTEXT_ONLY 可以在下游帮助解释一个已存在的边界；
- DROP 也不使已有边界证据消失；
- S06 不允许因内容价值高低而重新合并、切分或更新 Moment Core/Tail。

这避免使用“先由边界产生角色，再由角色反向证明边界”的循环自证。

## 9. Transition Moment 的特殊 KEEP 合同

### 9.1 先区分普通中间 Moment

位于 A、C 之间并不自动意味着 Transition Moment。

例如：

~~~text
A：古建筑景区行走
B：进入奶茶店并喝奶茶
C：继续古建筑景区行走
~~~

如果 B 有充分证据成为独立局部 Episode，B 是普通 Moment。它可以按普通规则进入 Chapter/Aha 候选；A、C 是否是 Resumed Episode 留给 S07。

Transition Moment 只指 V1.14 fallback：允许证据用尽后仍无法可靠归左或归右，因而隔离的最小 unresolved block。

### 9.2 Transition KEEP 的附加门

Transition Observation 想获得 KEEP，除通过普通 KEEP 门外，还必须满足：

1. 该 Transition Moment 只依靠自身 Observation 就能理解发生了什么；
2. 不借用左、右 Moment 的事实补全事件；
3. 存在一个可能独立成立的短暂具体事件信号；
4. 不是纯电梯、走廊、移动、模糊转场或边界不确定本身；
5. 当前 Evidence 足够看懂并支持相关事实。

S06 只判断“是否具备进入独立 Aha 价值判断的最低资格”，不在此处完成 Aha scoring。

### 9.3 三个阶段的职责拆分

| 阶段 | 判断 |
|---|---|
| S06 | Evidence 是否可读、事件能否独立理解、是否存在具体短暂事件信号 |
| S07 | 是否真正具有独立 Aha 记忆价值、独特性与非重复性 |
| S10 | 最终画面、构图、稳定性、声音、动作与媒体格式是否适合展示 |

因此，S06 的 Evidence 可读性不能被解释为最终媒体质量选择。

### 9.4 Transition 路由

~~~text
Transition KEEP
→ Aha candidacy only

Transition CONTEXT_ONLY
→ context envelope only

Transition DROP_FROM_MEMORY_OUTPUT
→ audit / timeline trace only
~~~

Transition KEEP 不进入 Chapter Candidate。S06 的结果不能重新打开 S05 unresolved seam，也不能污染左右 Moment。

## 10. Manual 与局部重复抑制

### 10.1 阶段拆分

重复处理分为：

- S06：同一 Moment 内明显近重复、没有额外事实贡献的 Observation；
- S07：同一局部 Episode 或候选组合中的重复；
- S09：全日候选集合之间的语义冗余；
- S10：最终精选媒体的代表性与展示质量。

### 10.2 S06 的 duplicate-group 规则

S06 必须按组处理明显重复，不能进行危险的两两贪心删除。

若 duplicate group 所表达的内容本身通过 KEEP 门：

- 至少保留一个可靠代表为 KEEP；
- 代表优先依据 grounded fact 完整性、support、输入可读性与确定性 tie-break；
- 不以最终审美质量替代 S10；
- 其他成员根据是否仍有独特上下文用途成为 CONTEXT_ONLY 或 DROP_FROM_MEMORY_OUTPUT；
- 附加 MEMORY_SUPPRESSED_DUPLICATE reason。

若整个 group 本身不通过 KEEP 门，则不因为“至少留一个”而强行产生 KEEP。

Manual 不享有重复豁免。跨较长时间、不同 Session 或不同 Episode 的视觉相似素材，不能仅凭外观自动判重。

## 11. Moment-level 路由与候选内容为空

S06 完成角色提交后，为每个 Moment 推导以下内部路由：

| 角色组成 | 内部路由结果 | 下游 |
|---|---|---|
| 普通 Moment 至少一个 KEEP | content-active ordinary | 一个共享候选种子，可进入 S07 Chapter/Aha 路径 |
| Transition Moment 至少一个 KEEP | content-active transition | 一个共享候选种子，只进入 S07 Aha 路径 |
| 无 KEEP，至少一个 CONTEXT_ONLY | context-only | 不生成内容候选，只输出 Context Envelope |
| 全部 DROP_FROM_MEMORY_OUTPUT | output-inactive | 不进入内容判断，只保留结构与审计引用 |

这些是路由结果，不是新的 S05 Moment type；具体 Production 枚举名称仍为 OPEN。

### 11.1 不存在正常的结构空 Moment

S05 的每个已提交 Moment 必须至少包含一个 accepted Observation。

若出现零 Observation 的 Moment：

- 这是无效 partition；
- 不能静默提交；
- 必须触发 Validator；
- 具体恢复机制留给 Production 工程设计。

### 11.2 没有 KEEP 时禁止的动作

S06 不得：

- 把 CONTEXT_ONLY 升级为 KEEP 来补位；
- 为凑全天数量改变角色；
- 删除该 Moment 的 S05 membership；
- 自动合并左右 Moment；
- 抹去真实 capture gap；
- 让中间 Moment 的不可见性证明 A、C 连续。

~~~text
A：content-active
B：context-only 或 output-inactive
C：content-active
~~~

S06 仍保留 A | B | C 的 S05 partition。S07 只有在独立证据支持时，才可以讨论 A、C 的 RESUMED_EPISODE。

## 12. 向 S07 的交接合同

S06 为每个 S05 Moment 输出一个共享 Role-Assigned Moment Packet。精确 Production 名称与 JSON Schema 仍为 OPEN，但语义至少包含：

### 12.1 Revision 与 Moment 身份

- Day / run / Revision 引用；
- immutable input snapshot 引用；
- Moment ID 与 ordinary/Transition type；
- first_observed_at / last_observed_at；
- 真实 capture gaps；
- 按时间排序的 member Observation IDs。

### 12.2 Observation 角色与证据

- 每个 Observation 的唯一主角色；
- 一个或多个 role reason；
- RawAsset / Window / Frame IDs；
- source / media type；
- KEEP 对应的允许事实 ID 与 grounding；
- CONTEXT_ONLY 对应的上下文提示及 non-claim 限制；
- DROP 的排除原因与审计引用；
- status、support grade、UNKNOWN、limitations 与 failure trace。

### 12.3 结构与 Provenance

- 相关 continuity/boundary ledger 引用；
- Moment Signature / duplicate-group 引用；
- schema / taxonomy / model / prompt / parameter / pipeline versions；
- exact-cache、attempt、latency 与 cost provenance。

同一份 Packet 使用引用而不是复制 Raw 或重复上传媒体。

### 12.4 S07 可以做什么

S07 可以：

- 从普通 content-active Moment 生成 Chapter/Aha candidates；
- 从 Transition content-active Moment 生成 Aha candidates；
- 在已允许的局部范围建立 SINGLE、ADJACENT_GROUP、RESUMED_EPISODE 或 LOCAL_EPISODE_GROUP；
- 评估 coherence、significance、personal relevance、distinctiveness、redundancy 与 inference risk；
- 拒绝价值不足、重复或证据风险过高的种子。

### 12.5 S07 不可以做什么

S07 不可以：

- 改写 S04 Perception Facts；
- 改写 S05 membership 或边界；
- 静默改写 S06 主角色；
- 用 CONTEXT_ONLY 生成用户可见 Claim；
- 把 CONTEXT_ONLY 计入精选媒体数量；
- 把 DROP 内容重新带回候选；
- 仅因全天主题相似做任意远距离组合；
- 在 Candidate Generation 阶段提前生成最终 Narrative。

若真实评测显示某个 S06 DROP 错误，应通过新版本修正 S06，而不是允许 S07 隐式绕过。

## 13. 候选数量与成本边界

S06 采用以下控制：

1. 每个 Moment 只输出一个共享 Packet；
2. 每个 content-active Moment 只产生一个共享 seed，不按 KEEP 数量复制输入；
3. 普通 Moment 的 Chapter/Aha eligibility 共享同一份数据；
4. Context-only 与 output-inactive Moment 不生成内容 seed；
5. S06 不枚举 Moment 的所有可能组合；
6. 一个 seed 不等于 S07 最多只能产生一个 candidate；局部峰值与候选数量由 S07 单独设计；
7. S07 只能沿允许且有证据支持的局部关系建立组合；
8. 只有少量实际候选才允许进入 S08 定向增强。

V1.16 不增加：

- Phone→Cloud Raw 上传；
- Auto 补帧或回取；
- 完整视频默认上传；
- 新的媒体理解调用；
- 每个 Observation 的生成式调用；
- S06 的全天任意两两组合。

S06 默认使用缓存的 S04 结构化 facts、S03/S05 信号与确定性/轻量比较。若未来真实 Benchmark 证明需要新增模型能力，必须用新 Checkpoint 明确成本、收益与暴露范围。

## 14. Revision 与可追溯性

- S06 角色必须与 S05 Moment、S04 Observation 来自同一个 immutable Revision；
- 不允许混用旧角色与新 Moment membership；
- 同输入同版本必须确定性复现；
- 一个已提交 Revision 中角色不得因为配额不足而漂移；
- 新素材或版本变化可以在新 Revision 中产生新角色结果；
- S06 自身不决定旧 unresolved seam 是否重开；
- stable Moment ID、局部重算与 Final 后 reopening 继续为 Revision 专题；
- S07 拒绝一个 candidate 不回写或污染 S06；
- 每次角色变化必须保留前后版本与原因 Trace。

## 15. Validator 不变量

提交 S06 输出前至少验证：

1. 每个 S05 accepted Observation 恰好一个主角色；
2. role count 与 Moment member count 完全一致；
3. 所有角色引用同一个 Revision；
4. KEEP 只来自 OBSERVED/PARTIAL；
5. 每个 KEEP 至少引用一个当前 Window 的 STRONG/MODERATE grounded item；
6. PARTIAL 只使用已支持字段；
7. INSUFFICIENT_EVIDENCE 不得 KEEP；
8. FAILED 必须 DROP_FROM_MEMORY_OUTPUT；
9. WEAK 不得单独形成用户可见 Claim；
10. CONTEXT_ONLY 标记 non-claim，且不进入精选计数；
11. DROP 不触发 RawAsset / Evidence / Observation / ledger 删除；
12. S06 role 不生成或改写 S05 boundary evidence；
13. Transition KEEP 的 route 不包含 Chapter；
14. MEMORY_SUPPRESSED_DUPLICATE 不是第四主角色；
15. eligible duplicate group 不因两两贪心抑制而失去全部代表；
16. 没有 KEEP 不改变 S05 partition；
17. 零成员 Moment 不得提交；
18. content seed 不按 KEEP Observation 数量复制；
19. Packet 不引用未知 RawAsset / Window / Frame / ledger；
20. schema、algorithm、parameter 与 provenance 完整。

## 16. 示例

### 16.1 古镇普通 Moment

~~~text
石板路上行走，事实清楚                  → KEEP
传统建筑立面，补充可靠环境背景            → KEEP
重复石板路画面，没有新增事实但能说明顺序    → CONTEXT_ONLY 或 DROP，取决于去除测试
几乎相同的 Manual 建筑照片                → duplicate group；至少一个可靠代表，其余 Context/Drop
镜头完全遮挡、处理成功但无可用事实          → DROP_FROM_MEMORY_OUTPUT
处理合同失败                              → FAILED + DROP_FROM_MEMORY_OUTPUT
~~~

相似度不要求所有 KEEP 共享同一个物体；石板路与建筑立面可以共同描述一个局部游览 Episode。

### 16.2 古镇—奶茶店—古镇

若奶茶店片段清楚支持“进入室内、可见饮品与饮用动作”，它是普通独立 Moment，而不是 unresolved Transition fallback。

~~~text
A：古镇行走
B：奶茶店局部 Episode
C：继续古镇行走
~~~

B 可按普通 Moment 进入 Chapter/Aha 候选；A、C 的 resumed relation 由 S07 判断。

### 16.3 办公室—过渡—餐厅

~~~text
A：办公室工作
B：证据用尽仍无法归左/归右的最小 Transition Moment
C：餐厅
~~~

- B 清楚记录短暂街头表演：通过附加门时 KEEP → Aha candidacy；
- B 清楚显示电梯或走廊，只解释转场：CONTEXT_ONLY；
- B 严重模糊且 ledger 已完整保存边界：DROP_FROM_MEMORY_OUTPUT。

无论 B 的角色是什么，都不能反向证明 A—B 或 B—C 的边界。

### 16.4 候选内容为空

~~~text
Moment B members:
Observation 1 → CONTEXT_ONLY
Observation 2 → DROP_FROM_MEMORY_OUTPUT

KEEP count = 0
~~~

B 不生成内容 candidate，但仍保留在 S05 partition；A、C 不因此自动合并。

## 17. 真实数据校准与指标

后续至少测量：

- KEEP precision / recall；
- KEEP 对 Chapter/Aha 最终入选的转化率；
- CONTEXT_ONLY usefulness；
- CONTEXT_ONLY 被下游误当 Claim 的违规率；
- DROP regret rate；
- FAILED / INSUFFICIENT 路由准确性；
- duplicate representative loss；
- Manual duplicate suppression regret；
- Transition→Aha precision；
- candidate-seed reduction ratio；
- role stability across Preview Revisions；
- role reason agreement；
- S06 latency、CPU、memory 与增量成本；
- S07 因缺失必要内容产生的 false rejection；
- 用户对遗漏与错误记忆的差异化反馈。

真实数据可以校准阈值、模型和 reason taxonomy，但不能在没有新版本与错误归因的情况下静默改变三角色语义或阶段边界。

## 18. FROZEN 与 OPEN

### FROZEN

- S06 在已提交 S05 partition 后运行，不重新分段；
- 每个 accepted Observation 每个 Revision 恰好一个主角色；
- 主角色只有 KEEP、CONTEXT_ONLY、DROP_FROM_MEMORY_OUTPUT；
- role reasons 可多值，但不是额外角色；
- KEEP 只允许 OBSERVED/PARTIAL，且至少有一个当前 Window STRONG/MODERATE grounded item；
- INSUFFICIENT_EVIDENCE 禁止 KEEP，只可在独特非 Claim 上下文用途下 CONTEXT_ONLY；
- FAILED 当前已提交 Revision 固定为 DROP_FROM_MEMORY_OUTPUT；
- 多个 WEAK 不能投票升级或改写 S04 support；
- 普通 KEEP 需要可靠事实门与 Moment 内容贡献门；
- KEEP 不是 Chapter/Aha、最终选片或独立价值保证；
- CONTEXT_ONLY 必须有正向、具体且未被覆盖的上下文用途；
- CONTEXT_ONLY 不生成用户可见 Claim，不计入精选媒体；
- DROP 只退出 Memory candidate/output，不删除底层事实、素材、membership、ledger 或 Manual 窗口；
- S06 role 不能成为或改写 S05 boundary evidence；
- Transition KEEP 需要独立可理解与具体短暂事件信号，只进入 Aha candidacy；
- S06 检查 Evidence 可读性，S07 判断独立价值，S10 判断最终媒体质量；
- MEMORY_SUPPRESSED_DUPLICATE 是 reason，不是第四主角色；
- S06 处理同 Moment 明显重复，S07/S09 处理更广候选与集合重复；
- eligible duplicate group 至少保留一个可靠代表；
- 没有 KEEP 只使 Moment 候选内容为空，不删除或重并 S05 partition；
- 普通 content-active Moment 可进入 Chapter/Aha 路径，Transition content-active 只进入 Aha；
- 每个 Moment 一个共享 Packet，不能按 KEEP 数量制造输入副本；
- S06 不新增 Raw 上传、补帧、回取或媒体理解调用；
- 同 Revision、同输入、同版本必须可复现，S07 不得反向改写 S06。

### OPEN / 下一节点或真实数据校准

- Production RoleAssignedObservation / Moment Packet JSON Schema；
- 完整 role-reason taxonomy；
- 内容贡献、去除测试与 duplicate-group 的具体阈值；
- S06 轻量实现的算法、特征、权重与 tie-break；
- S07 SINGLE / ADJACENT_GROUP / RESUMED_EPISODE / LOCAL_EPISODE_GROUP 的正式合同；
- S07 每个 seed 的 Chapter/Aha candidate 数量与去重策略；
- Aha 独立价值、Chapter 完整性与 candidate scoring；
- S08 Targeted Enrichment 的触发与成本门；
- S10 最终媒体质量与格式规则的实现参数；
- Preview stable Moment ID、局部重算、旧 seam reopening；
- Gold 标注协议、用户分层和个性化权重；
- Production fallback 与零成员无效 Moment 的恢复策略。

## 19. 当前实现 GAP

- 当前仓库没有 Production S06 role schema、engine 或 Validator；
- 没有普通 Moment Reliable Fact / Content Contribution gate；
- 没有 CONTEXT_ONLY removal test；
- 没有 FAILED / INSUFFICIENT 的正式 role router；
- 没有 group-aware Manual duplicate role assignment；
- 没有 Role-Assigned Moment Packet 与同 Revision Validator；
- 没有 content-active / context-only / output-inactive route engine；
- 没有 Transition KEEP 的正式 eligibility gate；
- 没有 S06→S07 shared-seed handoff；
- X01 仍在一轮模型调用中混合 Observation、Moment、Candidate 与 Narrative，不符合本分阶段合同；
- 尚无真实 wearable Gold 用于评估 KEEP precision、Context usefulness、DROP regret 或 role stability。

## 20. 下一步准确节点

S06 的完整角色合同至此冻结。下一步进入：

~~~text
S07｜Chapter / Aha Candidate Generation

先讨论：
S07-A Candidate 的单位、来源与 route
S07-B Chapter Candidate 的局部 Episode 范围
S07-C RESUMED_EPISODE / LOCAL_EPISODE_GROUP
S07-D Aha Candidate 的独立价值门
S07-E Candidate duplicate / reject audit
S07-F 成本、Revision 与 S08 handoff
~~~

下一步不提前进入 S08 强模型增强、S09 全日集合选择、S10 最终媒体或 S11 Narrative。
