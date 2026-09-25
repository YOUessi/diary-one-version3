# S11 Grounded Narrative & Claim Ledger — Consolidated Working V0.1

**状态：** DESIGN CLOSED / FROZEN BY `CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md`
**开始日期：** 2026-08-27
**上游冻结合同：** `CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md`、`CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md`、`CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md`
**继承的基础方向：** `CANONICAL_PROCESSING_RULES_V1_0.md` Writer boundary、Claim source taxonomy、Canonical Concept + Display Label
**下游边界：** S12 Final Validation、S13 Selected HQ Materialization / Export

> 本文保留 S11 的逐项讨论、确认、历史 OPEN 状态与交叉检查依据。S11 当前结论以 Canonical V1.22 为准；较早段落中的“下一检查点／S11 未冻结”是当时状态，不覆盖文末 closeout。V1.0/X01 的历史实验长度仍不能替代 V1.22 合同。

## 1. S11 在全链路中的位置

~~~text
S09
  selected Chapter/Aha membership + scope + relations
        ↓
S10
  final Content Beats + EvidenceAnchors + media projection
  chronology + Hero + limitations + claim compatibility
        ↓
S11
  ChapterFacts / AhaFacts
  → Claim Ledger
  → Narrative Content Plan
  → grounded title / time label / story / tags
        ↓
S12
  final fact / claim / media / revision / publish validation
        ↓
S13
  selected-source materialization / export
~~~

S11 的任务不是创作用户的人生，而是把已经确定的 Memory Facts 压缩成用户愿意阅读、同时可追溯的短文字。

## 2. 输入、输出与权限

### 2.1 输入

S11 只消费既有、current、可追溯的结构化输入：

1. S09 `SelectedMemoryEntry`、Memory scope、core basis、CandidateContentUnit refs、relations、lineage 与 limitations；
2. V1.20 `ChapterAhaNarrativeIndependenceDecision`；
3. S10 `ContentBeatInventory`、Anchor/MediaDecision、最终 Chapter set、chronology、Hero、Aha single-media、cross-memory projection；
4. S08 validation findings 与对应 Evidence refs；
5. RawAsset/device 时间等合法 metadata refs；
6. 已存在且来源明确的用户文字或用户确认事实；
7. S10 Route/format 产生的 claim narrowing、CoTemporalGroup 与 `NO_RELATIVE_TEMPORAL_CLAIM` 等限制。

### 2.2 输出

~~~text
ChapterFacts / AhaFacts
ClaimLedger
NarrativeContentPlan
GroundedNarrative
D5IndexDecision
  CanonicalTagDecision
  EntityIndexLinks
DisplayLabels
NarrativeReadiness / limitations / audit
~~~

具体 Production schema、字段与 readiness states 在逐项讨论后冻结；本节只确定对象边界。

### 2.3 S11 明确禁止

S11 不得：

- 新增、删除、替换或重新排序 Chapter/Aha membership；
- 改写 S10 正文成员、Hero、Aha media、Anchor、format 或 source plan；
- 恢复 CONTEXT_ONLY/DROP 为肯定性用户事实；
- 重新搜索全天、读取新 Raw/HQ 或请求额外上传；
- 添加无证据的人物身份/关系、地点身份、情绪、意图、因果、对白或持续活动；
- 把稀疏采样描述为未经证明的全程连续行为；
- 覆盖、改写或冒充用户自己写下的文字；
- 用更流畅、更诗意的文字掩盖 Evidence 不足；
- 声明最终 `PUBLISH_READY`，该权限属于 S12。

## 3. S11 讨论路径

~~~text
S11-A  Memory Fact Projection
  A1 narrative-readable fact scope
  A2 fact roles / visibility / limitations
  A3 ChapterFacts / AhaFacts output

S11-B  Claim Ledger
  B0 deterministic semantic ClaimCandidateProjection
  B1 atomic proposition
  B2 individual source / support / assertability / surface decision
  B3 composition validator for C provisional groups

S11-C  Narrative Content Plan
  C1 core vs optional claims
  C2 provisional groups / order / coverage / media alignment
  C3a cross-Revision continuity
  C3b1 Chapter/Aha visible text form separation
  C3b2 Aha standalone context + support base decision
  C3b3 Aha observable emphasis + provisional plan

S11-D  User-visible Writing
  D1 Chapter story length + grounded atmosphere
  D2 title
  D3 time label
  D4 Aha Moment Line wording / length
  D5 canonical tags + display labels
  D6 language / voice / personalization

S11-E  Writer Verification + S12 Handoff
  E1 generated span-to-claim / tone trace
  E2 unsupported / overstatement / user-text protection
  E3 readiness / immutable artifact / runtime revalidation

S11-F  cross-check + profile/timeline simulation
→ freeze S11
~~~

讨论顺序以依赖关系为准。D1 的 Chapter Story 产品方向已由用户先行确认，因此先记入本文；它不会反向跳过 A/B/C 的事实和 Claim 设计。

生产执行顺序与讨论编号分开，锁定为：

~~~text
A3 ChapterFacts / AhaFacts
→ B0 deterministic semantic ClaimCandidateProjection
→ B2 ClaimSemanticDecision + ClaimSurfaceDecision
→ C provisional Narrative Content Plan + Claim groups
→ B3 composition validation
   └─ invalid group → bounded monotonic recompose in C → B3
→ D user-visible writing
→ E actual span / implicit-language verification
   ├─ wording-only fix, plan unchanged → bounded D rewrite → E
   ├─ Claim/relation/group must change → bounded C → B3 → D → E
   └─ rewrite/replan budget exhausted → S11 narrative block → S12 handoff
→ S12 final publication validation
~~~

B1 定义 Claim 语义；它不要求先写自然句再反向抽取 Claim。B3 验证 C 规划出的语义组合；只有 D 完成后才能看到的真实措辞、指代与隐含关系，最终由 E 再验证。E 只有在 plan 完全不变时才能局部改写；凡是需要删除/替换 planned Claim 或 relation 的情况都必须回到 C/B3。所有回路绑定 versioned hard budget，由此避免 B、C、D、E 之间的无界循环。

## 4. S11-D1｜V1 Chapter Story Length 与 Grounded Atmosphere

**状态：CONFIRMED**

### 4.1 产品方向

V1 每个可发布 Chapter 的 `story` 为：

~~~text
default = 1 sentence
maximum = 2 sentences
~~~

Chapter 可能覆盖数小时，但 Story 不复述全过程。S10 的 3–5 个精选媒体已经承担主要内容表达，S11 只负责点明核心经历并增加有限余韵。

不能因为 Chapter 更长、媒体更多或算法发现更多 Facts，就机械增加句子。第二句是可选项，只有在它增加推进、转折、收束或有依据的氛围时才使用；不得为了满足“两句”而重述第一句。

若连一句安全、真实、可追溯的核心表达都无法生成，则进入 narrative unresolved/invalid 路径，不能用空泛氛围句补足。具体 readiness state 留到 S11-E。

### 4.2 一至两句的内部职责

推荐结构不是固定模板，而是责任边界：

~~~text
Sentence 1
  grounded core experience
  + optional concrete distinct detail

Sentence 2 (optional)
  progression / contrast / closure
  or grounded / non-mental atmosphere
~~~

第一句必须承载 Chapter core，不得只写“这是值得记住的一天”之类空泛判断。第二句不得引入计划外的独立故事、另一个 Memory、新人物关系、未经验证的新事件或未经确认的用户感受；可以使用 Content Plan 已选择且通过 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED + COMPOSITION_COMPOSABLE` 的 progression、contrast、closure 或 Story Support Claims。

### 4.3 Grounded Atmosphere 三层边界

#### A. Evidence-grounded atmosphere｜允许

有视觉、音频、时间或结构化 Evidence 支持时，可以表达：

- 雨、雪、夕阳、夜色、灯光；
- 人群密度、鼓掌、明显欢呼；
- 已验证的移动节奏、停留状态或室内外视觉差异；
- 画面或音频可直接支持的热闹、安静、明暗或光影变化。

氛围词仍需和 Evidence 强度匹配。例如只有无声静态帧时，不能仅凭画面没人就肯定声称“非常安静”。

“从室外进入室内”“从古街到河边”“从准备推进到完成”不是氛围本身，而是 movement/progression/action-result Claims；必须先独立验证相应关系，Atmosphere 只能消费其已验证结果，不能替它提供 Evidence。

#### B. Non-factual narrative tone｜允许但克制

可使用不改变生活事实、也不声明用户内心的修辞性收束，例如：

- “留下了一点旧街的余韵”；
- “成为这段路上的一个短暂停顿”；
- “让几段日常画面有了自然的收束”。

这类表达不能承担核心 Claim，不能掩盖空洞内容，也不得固定套用造成所有 Chapter 同质化。

#### C. User state / relationship attribution｜默认禁止

没有 `USER_CONFIRMED` 或同等级合法证据时，禁止：

- “你很开心 / 放松 / 感动 / 满足”；
- “这是你最喜欢的地方”；
- “和挚友 / 爱人 / 心爱的宠物”；
- “度过了难忘、完美、治愈的一天”；
- 对用户目的、期待、遗憾或因果的推断。

冻结原则：

~~~text
allow atmosphere
≠ infer the user's inner state
~~~

#### D. 内部编辑判断不得直接写给用户

算法内部可以判断某个事实或素材“更有代表性”“属于核心内容”“覆盖主要画面”，但这些是选材与规划语言，不是 Story 应有的用户语言。下列表述即使没有事实错误，也默认进入措辞改写：

- “A、B、C 构成了这段经历的主要画面”；
- “这些是本章最具代表性的内容”；
- “记录了这段经历的核心部分”；
- “本章主要呈现了……”；
- 任何像算法在解释“为什么选了这些素材”的句子。

对外 Story 应直接呈现场景、动作、变化或有限氛围，而不是解释编辑选择。内部的 `representativeness`、`coverage`、`core/support` 判断继续保留在 Content Plan 和审计字段中；写作层只消费它们，不复述它们。

例如同样使用“古镇漫步＋牌坊＋木雕＋屋檐”这些已验证内容：

> 上午走在古镇街巷里，牌坊、木雕和古建筑屋檐，让这段路多了几分旧城气息。

这句话直接把用户带回场景；“几分旧城气息”属于克制的非心理氛围，不声称用户喜欢、感动或难忘。若传统建筑属性不足以支持该氛围，则继续降级为纯场景表达：

> 上午走在古镇街巷里，眼前有牌坊、木雕和古建筑屋檐。

`META_EDITORIAL_PHRASING` 是 surface wording 问题，不自动否定底层 Claims；D/E 应在不增加新 Claim 的前提下做一次局部改写。

### 4.4 Title、Story、Time Label、Tags 的职责分离

| Surface | V1 职责 |
|---|---|
| Title | 用短语定义 Memory 核心，不承担完整故事 |
| Story | 1–2 句核心经历＋有限氛围 |
| Aha Moment Line | 用一个自然句直接表达单一 peak；不另设 generated Title/Story |
| Time Label | 承担准确时间/时段表达 |
| Canonical Tags | 承担稳定活动、场景、主题索引 |
| Display Labels | 把 canonical concept 转换成用户可读标签 |
| Claim Ledger | 在后台约束所有事实性文字 |

Tags 不是 Story 的“事实垃圾桶”。Story 仍必须有真实核心，但不按时间点和对象逐条列清单。

Title 字数、Story 字符数、Time Label 格式、Tags 数量和 Aha 文本长度尚未冻结。V1.0/X01 的 `title ≤ 100 / story ≤ 700 / time label ≤ 80 / tags ≤ 4` 仅为历史实验门，不自动进入本合同。

### 4.5 案例

#### 古镇 Chapter

过于死板：

> 09:00 进入古街，09:24 看到大殿，09:44 看到塔楼，10:02 到达河边。

符合方向：

> 从牌坊走进古街，木雕、塔楼和河岸依次出现在这段漫步里。传统建筑的层层变化，也给这段路留下了一点旧街的余韵。

前者把 Story 写成日志清单；后者只有在“进入、依次、不同建筑层次”均有 relation/entity Evidence 时才符合方向，并使用不声明用户内心的轻量收束。若只有共同 Chapter membership、没有可靠顺序，应降为 summary，例如：

> 走在古街上，眼前有牌坊、木雕和塔楼，也有临水的河岸。

这些细节仍需共同 Memory identity；若“木雕”或“河岸”不在合法 Facts/Claim Ledger 中，相应词必须删除。“眼前有……”只做共同场景汇总，不暗示四者的准确先后。

#### 生日 Chapter

过度推断：

> 你和最亲密的朋友度过了一个完美而难忘的生日。

符合方向：

> 蛋糕、烛光和最后的合照，串起了这场生日聚会。几段围在一起的画面，也为这个晚上留下了完整的收束。

“朋友关系”“完美”“难忘”需要额外确认；“最后”“串起”“完整收束”同样需要 chronology、same-event membership 与 closure Evidence。若这些关系不足，应降为：

> 蛋糕旁亮着烛光，几个人围在桌边合了影。桌边的笑脸，也给这个晚上留下一点热闹的余韵。

“热闹”仍需人群、表情、动作或音频等合法 atmosphere basis。

#### 普通会议 Chapter

空泛美化：

> 这是高效而充实的一场会议，大家完成了重要进展。

符合方向：

> 上午的会议里，有白板前的讨论，也有桌边记下的内容。

如果没有结果证据，不能写“高效”“完成进展”；“上午”需要 Time Fact，“白板前的讨论”和“桌边记下的内容”需要 same-event membership。关系不足时可只保留已独立成立的场景事实。普通日常可以有克制的叙事语气，不能靠语气制造结果。

### 4.6 成本与体验边界

短 Story：

- 降低 unsupported-claim 与长文本漂移风险；
- 更适合移动端快速阅读；
- 降低生成、验证、翻译与重生成成本；
- 让媒体保持 Chapter 主体地位；
- 也增加“所有句子都很像”的风险，因此后续 D6 必须设计 anti-template repetition，但不能靠增加事实或长度解决。

本项不决定具体模型、prompt、temperature、语言风格选项、个性化强度或 UI 截断方式。

## 5. 下一检查点

进入 S11-A1：确定 `NarrativeReadableFactScope`。核心问题是：Writer 可以读取整个 selected Memory 的哪些 grounded Facts；最终媒体未直接展示但仍在 Memory scope 内的 Facts，是否以及以什么等级进入 Title/Story/Aha Moment Line/Tags；CONTEXT_ONLY 和 limitations 如何只限制文字而不生成肯定 Claim。

## 6. S11-A1｜NarrativeReadableFactScope

**状态：CONFIRMED**

### 6.1 核心原则

Writer 的事实输入不应被缩窄为“只能描述最终 3–5 个媒体”，也不能等于“selected Memory 内所有记录都可以自由写”。V1 采用分层投影：

~~~text
entire current selected-Memory fact scope
+ active S10 final-media projection
+ current validation / metadata / user-confirmation refs
→ normalize and validate fact identity
→ assign narrative-use class
→ only then expose a bounded fact view to Writer
~~~

冻结结论：

> Writer 可以读取整个 selected Memory 内的可靠 Facts，但必须经过四级用途分流。未被最终媒体展示的可靠 Facts 可以作为辅助信息，不能压过最终媒体与 Memory 核心；CONTEXT_ONLY 只限制表达；selected Aha 的核心事实不得被 Chapter Story 重新占用。

因此：

~~~text
Story is not limited to visible pixels
but its core must remain aligned with
selected Memory identity + final media coverage
~~~

### 6.2 四级 Narrative Use Class

#### `CORE_ASSERTABLE`

可驱动 Chapter Title/Story 核心、Aha Moment Line peak 与符合资格的 canonical tag。至少满足：

1. 属于 current selected Memory、Revision 与 policy scope；
2. 是 Memory core/identity/progression/outcome 的必要或代表性事实；
3. 来源为合法 `USER_CONFIRMED / OBSERVED / DEVICE_METADATA / validated MAP_LOOKUP / safely DERIVED`；
4. 有可追溯 source/Evidence/dependency refs；
5. 与 active S10 media projection、V1.20 relations 和 limitations 兼容；
6. 未被 contradict、invalidate、reserve 给另一个 selected Memory 或更窄 Route 覆盖。

`CORE_ASSERTABLE` 不要求每个事实都肉眼出现在媒体里。例如可靠 device metadata 确认地点，地点名仍可成为核心；但最终媒体集合必须继续与该 Memory 的核心身份一致，不能出现“文字讲茶摊、媒体全是建筑”的主题漂移。

#### `SUPPORT_ASSERTABLE`

属于 selected Memory、由可靠 KEEP Evidence 支持，但不是最终媒体直接展示或不是 Memory identity 核心的事实。它只能：

- 为 Story 提供一处克制的连接、细节、推进或收束；
- 在不改变核心的情况下帮助 1–2 句话自然衔接；
- 作为 Claim Ledger 中明确标记 `not_directly_visible` 的辅助 Claim 候选。

它不能：

- 单独定义 Title；
- 抢占 Story 第一句的核心；
- 把 Chapter 改写成另一个主题；
- 因数量多就投票升级成 CORE；
- 自动变成 canonical tag，避免次要细节污染检索/个性化。

#### `CONSTRAINT_ONLY`

不生成肯定性用户事实，只用于降低、禁止或限定表达：

- CONTEXT_ONLY Observation；
- `NO_RELATIVE_TEMPORAL_CLAIM`；
- CoTemporalGroup / order limitation；
- 地点、人物、动作、情绪或因果不确定；
- S10 `PRESENTATION_NARROWING`；
- soft relation/visibility limitation；
- weak hint、UNKNOWN field 或 non-impacting uncertainty。

例如模糊景区指示牌可以阻止 Writer 把环境写成普通办公室，也可以提名需要验证的地点概念；但在没有其他可靠来源时，不能直接写出具体古镇名称。

#### `FORBIDDEN`

完全不暴露为 Writer 的可表达事实：

- DROP_FROM_MEMORY_OUTPUT；
- 其他未选 Memory/Candidate 的内容；
- stale Revision、invalid lineage、错误 policy 或白名单外事实；
- 无依赖链的 INFERRED、UNKNOWN、模型自由补充；
- 已被事实/Evidence/用户纠正撤销的内容；
- inactive/failed Route 不再支持的 action/format-specific Claim；
- 与当前 Memory/Aha reservation 冲突的事实；
- 仅因为 embedding、类别常识或画面风格推断出的地点、情绪、关系、意图与因果。

### 6.3 合法 Fact Source 与用途不是同一概念

继承 V1.0 source taxonomy：

~~~text
USER_CONFIRMED
OBSERVED
DEVICE_METADATA
MAP_LOOKUP
DERIVED
INFERRED
UNKNOWN
~~~

source type 只描述“事实从哪里来”，不自动决定它能用于哪里：

- `USER_CONFIRMED` 仍须 current、相关、没有被用户撤回；
- `OBSERVED` 仍须引用 STRONG/MODERATE grounded Evidence 与正确 Memory scope；
- `DEVICE_METADATA` 适合时间/地点等其真实能力范围，不能证明情绪；
- `MAP_LOOKUP` 必须有 lookup provenance、时效与 entity match validation；
- `DERIVED` 必须保存全部 parent facts 与确定性 derivation rule；
- `INFERRED` 默认不得成为核心肯定事实；
- `UNKNOWN` 永远不能被 Writer 填成一个听起来合理的答案。

同一 source type 可以得到不同 use class。例如一个 `OBSERVED` 塔楼是 CORE，一个 `OBSERVED` 普通茶摊可能只是 SUPPORT；分类取决于 Memory role、证据、media alignment 与事实重要性，而不是来源名称。

### 6.4 Final Media Visibility 的作用

每个可读 Fact 必须记录其与 active final media 的关系，至少区分：

~~~text
DIRECTLY_VISIBLE
INDIRECTLY_COVERED
NOT_SELECTED_BUT_GROUNDED
NOT_VISUALLY_APPLICABLE
VISIBILITY_UNRESOLVED
~~~

- `DIRECTLY_VISIBLE`：active media 本身直接支持；
- `INDIRECTLY_COVERED`：最终 set/sequence 支持整体 progression 或 relation，但不是单帧直接可见；
- `NOT_SELECTED_BUT_GROUNDED`：仍在 selected Memory KEEP scope，但未进入最终媒体；
- `NOT_VISUALLY_APPLICABLE`：可靠时间、地点 metadata 或用户确认等不要求出现在像素里；
- `VISIBILITY_UNRESOLVED`：不能假装为 visible，按后续 A2 assertability/limitation 处理。

可见性不是 truth 的唯一来源，但它决定文字与媒体错位风险。`NOT_SELECTED_BUT_GROUNDED` 默认只能 SUPPORT；要升级为 CORE，必须有 Memory-core necessity、可靠非视觉来源或 final set 的整体 core coverage 支持，不能只因 Fact 很有趣。

### 6.5 Selected Chapter 与 Aha 的 Fact Reservation

V1.20 narrative independence 在 S11 继续生效。如果 Chapter 与一个 embedded-distinct Aha 同时被选中：

1. Aha 的 core peak proposition 默认保留给 Aha；
2. Chapter 不得把该 peak 写成自身高潮、结果、代表性高光或 Title 核心；
3. Chapter 可以保留必要的 broad transition/context，但必须表达不同 proposition，不能换同义词重复 Aha；
4. exact render reuse 不授权 exact Claim reuse；媒体共用与文字事实范围是两个合同；
5. Aha 未被选中时，其合法 Fact 若本来属于 Chapter scope，可按普通 Chapter use-class 规则判断，不能因曾是 Candidate 永久封锁。

**案例：** 古镇 Chapter＋奶茶第一口惊喜 Aha 共存时，Chapter 写建筑游览与河边收束；Aha 写第一口反应。Chapter 不能再写“途中喝到一杯令人惊喜的奶茶”，否则文字重新制造 same-memory redundancy。

### 6.6 Aha Fact Scope 更严格

Aha 的 readable scope 只包含：

- 构成上游 selected peak identity 的 predicate、core arguments 与 visible change；
- 与该 peak 紧邻、可单独验证的 before/after reaction 或 result support；
- 与该 peak 直接相关、可能解除局部歧义的可信时间/地点/user-confirmed metadata；
- limitations 与 selected Chapter fact reservation。

Aha 不能借用整个 Chapter 的准备、过程、结果或 title context 把自己扩写成微型 Chapter。`AHA_PEAK_CORE` 只能使用上游已经选定的 peak predicate/core arguments/visible change；任何可分离的 before/after reaction 或 result 必须进入 `AHA_ADJACENT_SUPPORT`，除非该 reaction/result 本身就是上游选定的 `core_peak_event_ref`。局部活动阶段/地点只可成为 context candidate。support Window 可以产生合法 support Claim，但不能把多个反应重标为 peak core 来绕过用户可见预算。

### 6.7 Active Projection 与 Runtime Reprojection

`NarrativeReadableFactScope` 必须绑定 active S10 projection fingerprint，而不是只绑定初始 Primary：

1. Media Fallback 仅改变格式但 Claim support 不变：可以复用兼容 facts；
2. Fallback 带 `PRESENTATION_NARROWING`：降低相应 Fact 的 assertability/use class；
3. D1 删除正文成员：删除或降级依赖该成员的 facts；
4. Hero Alternate 只改变 cover 且事实支持不变：不重写 Story，但重验 cover-related Claim/provenance；
5. Aha Route 从完整动作 LIVE 降为结果 PHOTO：不能继续表达未被其他 Evidence 支持的完整动作；
6. resulting scope fingerprint 改变时，依赖的 Claim Ledger/Narrative 必须重新验证，不能沿用旧文字直接发布。

### 6.8 输出

~~~text
NarrativeReadableFactScope
  revision_ref
  selected_memory_ref
  memory_type
  active_s10_projection_ref
  active_projection_fingerprint
  chapter_aha_reservation_refs[]
  fact_entries[]
    canonical_fact_ref
    fact_source_type
    grounded_evidence_refs[]
    validation_refs[]
    derivation_dependency_refs[]
    memory_role
    media_visibility_role
    narrative_use_class =
      CORE_ASSERTABLE
      | SUPPORT_ASSERTABLE
      | CONSTRAINT_ONLY
      | FORBIDDEN
    claim_strength_ceiling_ref
    allowed_surface_candidate_refs[]
    limitation_refs[]
    reservation_refs[]
    exclusion_reason_refs[]
  context_constraints[]
  forbidden_fact_audit[]
  scope_state =
    FACT_SCOPE_READY
    | FACT_SCOPE_READY_WITH_LIMITATIONS
    | FACT_SCOPE_UNRESOLVED
    | FACT_SCOPE_CONTRACT_INVALID
  policy_and_signal_versions
  scope_fingerprint
  decision_trace
~~~

`claim_strength_ceiling` 与 `allowed_surface_candidate_refs` 只在 A1 保留接口；具体等级和 Title/Story/Time/Tag 映射由 A2 决定。

### 6.9 案例

1. **古镇最终四项，普通茶摊未精选：** 茶摊是可靠 KEEP，但非核心，`SUPPORT_ASSERTABLE + NOT_SELECTED_BUT_GROUNDED`；可克制连接，不能定义 Title。
2. **模糊指示牌：** CONTEXT_ONLY，`CONSTRAINT_ONLY`；不能单独确认具体古镇名。
3. **可靠 GPS/用户确认地点：** `NOT_VISUALLY_APPLICABLE` 仍可为 CORE candidate；实际 Title 使用资格由 A2 检查 entity/time/provenance。
4. **用户写“和妈妈过生日”：** current 且未撤回的 USER_CONFIRMED relation 可进入 core candidate；Writer 不改成“和家人”或“和挚友”冒充用户原话。
5. **Chapter＋独立甜品 Aha：** 甜品 peak 对 Aha 为 CORE，对 Chapter 为 reserved/forbidden core；Chapter 只讲 citywalk 主线。
6. **LIVE 吹蜡烛降为结果 PHOTO：** “蜡烛已熄灭”可保留；“一口吹灭”若无其他动作 Evidence 则降级/禁止。
7. **同秒两张照片无先后：** Facts 可保留，`NO_RELATIVE_TEMPORAL_CLAIM` 进入 CONSTRAINT_ONLY；不能写“先 A、然后 B”。
8. **漂亮 DROP 建筑图：** 不因适合氛围而恢复，始终 FORBIDDEN。
9. **地图 lookup 名称相似但 entity match 未确认：** `VISIBILITY_UNRESOLVED/CONSTRAINT_ONLY`，不能选一个最像的地名。
10. **Aha support after：** 鼓掌可帮助确认吹蜡烛 peak，但不能让 Aha Story再并列讲“之后大家合照”。

### 6.10 Invariants、成本与边界

1. selected Memory scope 是事实池硬边界；
2. final media 影响 narrative priority/compatibility，但不是唯一 truth 来源；
3. 未精选 KEEP Fact 默认最多 SUPPORT，不能抢核心；
4. CONTEXT_ONLY 永不产生肯定 Claim；
5. DROP/其他 Memory/stale/invalid facts 不暴露给 Writer；
6. source type 不自动等于 narrative permission；
7. selected Aha core 不被 Chapter 文字重新占用；
8. Aha 不借 Chapter scope 扩写；
9. runtime projection 改变必须重算或重验 fact scope；
10. 同一 inputs、projection、policy 与 versions 必须得到相同 scope；
11. A1 只投影现有 refs，不调用新模型、不读 Raw/HQ、不做 MAP_LOOKUP、不生成文字；
12. MAP_LOOKUP 是否执行、用户文字优先级细节、Claim 强度与 surface mapping 留给后续明确合同。

## 7. 下一检查点

进入 S11-A2：把 `narrative_use_class` 拆成可执行的三个维度——Fact importance、assertability ceiling、allowed surfaces。需要决定 CORE/SUPPORT Fact 分别能否进入 Title、Story core、Story support、Aha Moment Line、Time Label、Canonical Tags 与 Atmosphere，以及非视觉 Facts 如何避免文字与媒体脱节。

## 8. S11-A2｜Fact Importance、Assertion Ceiling 与 Allowed Surfaces

**状态：CONFIRMED**

### 8.1 为什么不能只用一个 Fact 等级

“事实可信”不等于“适合放在标题”，也不等于“适合成为 Tag”。同一 Fact 至少需要分开回答三个问题：

~~~text
How important is it to this Memory?
How specifically may it be asserted?
On which user-visible surfaces may it appear?
~~~

例如茶摊确实出现过，事实可以非常可信，但它仍可能只是古镇 Chapter 的次要细节：可以在第二句克制出现，却不应成为 Title 或 `茶饮` Tag。

### 8.2 Fact Importance Roles

一个 Fact 可以有多个 importance roles，但每个 role 都必须有 derivation refs：

~~~text
IDENTITY_CORE
STORY_CORE
SUPPORTING_DETAIL
CONSTRAINT
~~~

#### `IDENTITY_CORE`

决定“这是什么 Memory”的稳定事实或概念，例如：

- 生日聚会；
- 古街/传统街区漫步；
- 陶艺制作；
- 可靠确认的颐和园游览；
- 用户明确确认的“和妈妈过生日”。

它可以成为 Title/Tag 候选，但仍须通过具体 surface gate；身份事实不能只由类别常识、单张风格图或未经确认的地点 lookup 产生。

#### `STORY_CORE`

构成 Chapter 一至两句话中主要经历、推进、转折或结果的事实。它可以与 IDENTITY_CORE 重叠，也可以是身份之下的具体发展，例如“从牌坊走到河边”“从拉坯推进到成品”。

#### `SUPPORTING_DETAIL`

真实但不决定 Memory 身份或核心故事的细节，例如途中普通摊位、短暂路过、一个不影响主线的小物件。默认只能进入 Story support 候选。

#### `CONSTRAINT`

不形成肯定内容，只限制时序、地点、关系、动作、情绪、因果或表达强度。它不进入用户文字，但必须进入 Writer instruction/validator。

### 8.3 Assertion Ceiling

每个可表达 Fact 必须有最高表达具体度：

~~~text
EXACT_DIRECT
SAFE_GENERALIZATION_ONLY
NON_FACTUAL_TONE_ONLY
NO_ASSERTION
~~~

#### `EXACT_DIRECT`

可以按 Claim Ledger 中已规范化的具体事实直接陈述。例如可靠 GPS＋entity match 支持“颐和园”，或 temporal Evidence 支持“吹灭蜡烛”。Writer 仍不能增加评价、因果或关系。

#### `SAFE_GENERALIZATION_ONLY`

具体 Fact 不足，但已有一个由 Evidence 独立支持、更宽泛且仍真实的 canonical parent proposition。Writer 只能使用该 parent：

~~~text
specific 西塘古镇 unresolved
+ traditional-street environment grounded
→ “传统街区” allowed
→ “西塘古镇” forbidden
~~~

安全泛化必须引用已存在 parent fact/taxonomy mapping；不能让 Writer 临时发明一个听起来稳妥的宽泛说法。

#### `NON_FACTUAL_TONE_ONLY`

只能参与不改变生活事实的克制语气/收束，不能产生事件、地点、人物或状态 Claim。例如“留下了一点余韵”。它不得成为 Title core 或 Claim Ledger 的事实替代品。

#### `NO_ASSERTION`

只能作为限制、审计或 exclusion；不得进入任何用户可见文字。

### 8.4 V1 不向用户展示算法犹豫

V1 Grounded Narrative 默认禁止用下列词把不确定 Fact 包装进 Diary：

~~~text
可能
似乎
大概
看起来像是
也许
~~~

处理顺序冻结为：

~~~text
specific claim unsupported
→ use an independently grounded safe parent proposition
→ otherwise omit the claim
→ never surface model uncertainty as diary prose
~~~

这不表示算法隐藏不确定性。UNKNOWN、冲突、limitation 与被省略原因仍完整保存在 Claim Ledger/Audit 中；只是用户可见 Story 不写成检测报告。

**例外边界：** 如果用户原文自己写了“可能”“也许”，S11 不得擅自删除或改写用户表达；用户文字保护规则后续单独定义。

### 8.5 Allowed Surfaces

~~~text
TITLE
STORY_CORE
STORY_SUPPORT
AHA_MOMENT_LINE
TIME_LABEL
CANONICAL_TAG
ATMOSPHERE
~~~

`allowed_surfaces` 只表示“有资格参加该 surface 的后续选择”，不代表必须出现，也不代表同一 Fact 要重复出现在多个 surface。

#### 默认映射

| Importance role | TITLE | STORY_CORE | STORY_SUPPORT | AHA_MOMENT_LINE | TIME_LABEL | CANONICAL_TAG | ATMOSPHERE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `IDENTITY_CORE` | eligible | eligible | eligible | selected Aha peak, C3b2-required local context, or C3b3-eligible observable qualifier | only temporal fact | eligible if canonical | only with atmosphere basis |
| `STORY_CORE` | conditional | eligible | eligible | selected Aha peak, C3b2-required local context, or C3b3-eligible observable qualifier | only temporal fact | only if identity-level concept | only with atmosphere basis |
| `SUPPORTING_DETAIL` | no | no | eligible | only legal Aha adjacent support, minimal local context, or observable qualifier | normally no | no by default | eligible when grounded |
| `CONSTRAINT` | no | no | no | no | constrains only | no | constrains only |

表中 `TITLE` eligibility 只适用于拥有 generated Title 的 Memory surface contract（V1 即 Chapter）。C3b1 确认后，selected Aha 即使 Fact 为 `IDENTITY_CORE`，generated `TITLE` 也必须 Block；其 narrative core 只进入 `AHA_MOMENT_LINE`。

Title 与 Tag 的门比 Story 更严格：

- Title 定义用户看到的 Memory 身份；
- Canonical Tag 影响检索、聚合与个性化；
- 次要细节进入它们会造成长期主题污染；
- 因此 Supporting Detail 默认两者均禁止；若未来证明某细节反复具有核心价值，应先在 Fact importance 层升级，而不是给 Tag 单独开后门。

### 8.6 Surface-specific 资格

#### TITLE

必须为 current、稳定、identity-central、非 reserved、非 incidental，且 assertion ceiling 至少为 `SAFE_GENERALIZATION_ONLY`。Title 不能只依赖氛围、Hero 美感或一个非核心对象。

#### STORY_CORE

必须为 IDENTITY/STORY CORE，能直接支持第一句的核心经历，并与 active final media 的整体 core coverage 一致。不能用多个 Supporting Detail 投票形成一个新核心。

#### STORY_SUPPORT

可以使用 SUPPORT，但不得改变第一句含义、引入另一个 Memory 或挤占 selected Aha。具体一至两句话可选择多少条 support Claim，留给 S11-C。

#### AHA_MOMENT_LINE

V1 selected Aha 的唯一 generated narrative surface。Aha 的 event core 必须映射为 `AHA_PEAK_CORE` 并绑定该 Aha 的同一 `core_peak_event_ref`；非 peak Fact 只有映射为合法 `AHA_ADJACENT_SUPPORT`、`AHA_LOCAL_CONTEXT_CANDIDATE` 或 `AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 时才有资格参加后续 Content Plan。三者分别表示 peak 的紧邻反应/结果、可能解除局部歧义的背景，以及可直接验证并附着于某个基础 Claim 的动作速度／突发边界／强度变化／感知属性；它们都不预判 C3b2/C3b3 的最终选择，也不能升级为第二个 event core。importance role 本身不会让不同 narrative role 互相冒充。Aha Fact 不因 identity-central 就自动获得 generated `TITLE`；C3b1 已确认 V1 generated Aha Title 为 forbidden。

#### TIME_LABEL

只消费可靠 capture/device/user-confirmed temporal facts 与已冻结 timezone/day scope；不能由内容相似度或画面明暗猜测“清晨/傍晚”。Time Label 的粒度与格式留给 D3。

#### CANONICAL_TAG

只能使用稳定 canonical concept，并以 identity/core 事实为主。Display Label 是 canonical tag 的本地化/用户可读映射，不创建新概念。Tag 数量和 taxonomy 仍待 D5。

**D5b1 contract-alignment amendment：** A2/B0/B2/C2 中历史字段名`CANONICAL_TAG`继续作为“有资格进入 D5 结构化索引”的 umbrella candidate target，不提前决定最终存储类型。D5 必须进一步分流：可复用、语言无关的 class-level concept 才能形成`CanonicalTagAssignment`；可信 exact place/person/pet/venue 等高基数实体形成 typed`EntityIndexLink`。两条路径继承同一 Fact／Claim／Evidence／Revision 真值门，不能借类型分流扩大 eligibility。

#### ATMOSPHERE

只使用 4.3 已确认的 evidence-grounded atmosphere 或 `NON_FACTUAL_TONE_ONLY`；不能借 atmosphere surface 添加用户情绪、关系或价值判断。该独立 surface 在 V1 只服务拥有 atmosphere 合同的 Chapter；generated Aha 没有独立 `ATMOSPHERE`/Tone 槽，也不得把 `NON_FACTUAL_TONE_ONLY` 偷渡进 `AHA_MOMENT_LINE`。Aha 可在 C3b3 中选择 0–1 个另有 Claim/Evidence 的 observable emphasis qualifier；28.12 Light-Affect v1.1 另行允许 0–1 个与事实图分离的受控 lexical permission，不属于 atmosphere surface。

### 8.7 非视觉 Facts 与媒体一致性

`NOT_VISUALLY_APPLICABLE` 不等于低可信，例如 GPS、capture time、用户确认关系。但这些 Facts 进入 Title/Story/Aha Moment Line 时必须满足：

1. source 本身能证明该属性；
2. 与 selected Memory 的时间/entity scope 一致；
3. 不与 final media/other facts 冲突；
4. 不让文字主题超出媒体集合所覆盖的 Memory 核心；
5. 在 Claim Ledger 中明确标记为 non-visual source，不能伪装为从画面识别。

最终媒体不必逐字显示每个事实，但用户打开 Chapter 时，文字和媒体必须仍然像同一段经历。

### 8.8 冲突与降级

1. 两个可信 source 给出不同具体地点：`NO_ASSERTION`/unresolved，不任意选一个；
2. 具体地点不成立但 broader environment 独立 grounded：降为 `SAFE_GENERALIZATION_ONLY`；
3. 人物存在但关系未知：可以描述“围在一起的人”之类已有 broader fact，不能写“朋友/家人”；
4. 动作只剩结果 Evidence：使用结果 Fact，不能用“可能做了动作”；
5. 时序不可靠：Facts 可表达，但 `NO_RELATIVE_TEMPORAL_CLAIM` 阻断“先、随后、最后”；
6. 一个 Fact 对 Title eligible、但 prior published Title 仍合法且新 Fact 只稍微更具体：实际是否替换留给 S11-C/D cross-Revision，不在 A2 制造 churn。

### 8.9 输出

~~~text
NarrativeFactUsageDecision
  revision_ref
  selected_memory_ref
  active_fact_scope_ref
  canonical_fact_ref
  importance_roles[]
    IDENTITY_CORE
    | STORY_CORE
    | SUPPORTING_DETAIL
    | CONSTRAINT
  assertion_ceiling =
    EXACT_DIRECT
    | SAFE_GENERALIZATION_ONLY
    | NON_FACTUAL_TONE_ONLY
    | NO_ASSERTION
  exact_assertion_fact_ref
  safe_parent_fact_ref
  allowed_surfaces[]
  blocked_surfaces[]
  media_visibility_role
  non_visual_source_refs[]
  chapter_aha_reservation_refs[]
  temporal_claim_constraints[]
  limitation_refs[]
  policy_and_signal_versions
  usage_fingerprint
  decision_trace

FactSurfaceEligibilityMatrix
  selected_memory_ref
  revision_ref
  fact_usage_decision_refs[]
  title_candidate_fact_refs[]
  story_core_candidate_fact_refs[]
  story_support_candidate_fact_refs[]
  aha_moment_line_peak_candidate_fact_refs[]
  aha_moment_line_adjacent_support_candidate_fact_refs[]
  aha_moment_line_minimal_local_context_candidate_fact_refs[]
  aha_moment_line_observable_emphasis_candidate_fact_refs[]
  time_label_candidate_fact_refs[]
  canonical_tag_candidate_fact_refs[]
  atmosphere_candidate_fact_refs[]
  constraint_refs[]
  forbidden_fact_audit_ref
  matrix_state
  matrix_fingerprint
~~~

### 8.10 案例

1. **可靠西塘定位：** `IDENTITY_CORE + EXACT_DIRECT + TITLE/STORY/CANONICAL_TAG-umbrella` eligible；不要求地名出现在像素里。D5b1 后置分流为 verified`PlaceEntityIndexLink`，而不是为每个地点创建 taxonomy concept。
2. **只能确认传统街区：** `IDENTITY_CORE + SAFE_GENERALIZATION_ONLY`；写“传统街区”，不写“可能是西塘”。
3. **普通茶摊：** `SUPPORTING_DETAIL + EXACT_DIRECT + STORY_SUPPORT only`；不进入 Title/Tag。
4. **夕阳清楚可见：** 若时间/光线 Evidence 一致，可进入 ATMOSPHERE；仍不能推出用户“很治愈”。
5. **人物关系未知：** “朋友”被 NO_ASSERTION；若“几个人围在蛋糕旁”独立 grounded，可用 safe broader fact。
6. **用户确认妈妈：** relation Fact 可为 IDENTITY/STORY CORE；是否保留用户原句或转述留给用户文字合同。
7. **同秒照片：** 对象 Facts 可进入 Story，时间 constraint 禁止“先后”。
8. **结果 PHOTO：** “蜡烛熄灭后”可 EXACT；“吹灭”无动作 Evidence时禁止，不写“可能吹灭”。
9. **Aha reserved peak：** 对 Aha 为 `AHA_MOMENT_LINE + AHA_PEAK_CORE` candidate；对 V1 generated Aha `TITLE` 为 blocked，对 Chapter 所有 core surfaces 也因 reservation blocked。
10. **漂亮但外围的灯笼：** 可以是 grounded atmosphere candidate；若非 Memory identity，不进入“灯会”Title/Tag。
11. **地图两个同名地点：** entity conflict，地点为 NO_ASSERTION；不能按距离或模型偏好静默选一个。
12. **用户原话含‘也许’：** 保护 user-authored surface，不套用 generated-narrative 禁词删除；算法自己不得仿写成肯定事实。
13. **视频可验证流动速度：** 只有连续视频／时序 Evidence 足以支持“流速较慢”时，该 Fact 才能成为 `AHA_OBSERVABLE_EMPHASIS_CANDIDATE`；它仍须经 C3b3 选择，不能仅为文案更生动就写“缓缓”。

### 8.11 Invariants、成本与边界

1. importance、assertion ceiling 与 allowed surfaces 三轴分离；
2. credible Fact 不自动获得 Title/Tag 资格；
3. Supporting Detail 默认不进入 Title/Tag；
4. safe generalization 必须有 grounded parent fact；
5. 无 safe parent 时省略，不显示算法犹豫；
6. user-visible Story 不用 hedging 掩盖 unsupported Claim；
7. constraint/forbidden Facts 无用户可见 surface；
8. non-visual source 必须显式标记并保持 scope compatibility；
9. Time Label 只用合法 temporal sources；
10. Tag eligibility 不创建 taxonomy concept；
11. selected Aha reservation 对所有 Chapter core surfaces 生效；
12. V1 Aha generated narrative 只允许 `AHA_MOMENT_LINE`，不把 peak 映射到 generated `TITLE`；Moment Line 内的 peak、adjacent support、minimal local context 与 observable emphasis qualifier 必须使用不同 narrative role；
13. V1 generated Aha 没有独立 `ATMOSPHERE`/Tone surface，`NON_FACTUAL_TONE_ONLY` 不能替代 evidence-bearing observable qualifier；28.12 light-affect permission 是窄 lexical exception，不承担事实或 atmosphere role；
14. A2 只做结构化映射，不生成标题/Story/Moment Line/Tag，不调用模型或外部 lookup。

## 9. 下一检查点

进入 S11-A3：设计 `ChapterFacts / AhaFacts` 正式输出。重点是完整保留事实 inventory 与最终 1–2 句 Claim 选择之间的边界：A3 是否应保存全部可表达 Facts，还是提前只保留少量 Facts；Chapter 与 Aha 的 identity/core/progression/support/constraint 如何组织；如何避免为了短 Story 过早删除审计和未来 Revision 仍需要的事实。

## 10. S11-A3｜ChapterFacts / AhaFacts Complete Projection

**状态：CONFIRMED**

### 10.1 核心原则｜短 Story 不等于短 Facts Inventory

V1 Chapter Story 默认一句、最多两句，但 A3 不提前把事实删成两三条：

~~~text
A3
  complete normalized fact projection
  + roles / visibility / permissions / limitations
        ↓
B/C
  select the smallest sufficient Claim set
        ↓
D
  realize 1–2 user-visible sentences
~~~

冻结结论：

> ChapterFacts 保存 selected Memory 内完整、去重、分角色的可表达 Facts 与限制，不在 A3 做 Top-K；AhaFacts 只保存一个 core peak、必要紧邻支持和 metadata。最终一到两句话的 Claim 选择留给 S11-B/C。

完整 inventory 的意义不是让 Writer 写得更多，而是保证：

- Claim 选择有真实替代空间；
- Fallback/Survivor 后可以准确重验；
- 未选 Fact 仍有审计原因；
- 新 Revision 可以复用稳定事实；
- S12 能证明文字没有越过 Fact 边界；
- 用户短文字不会建立在被过早删减的随机小样本上。

### 10.2 Canonical Fact Identity 与去重

同一 normalized proposition 在一个 MemoryFacts projection 中只保存一个 canonical Fact entry：

1. 多个 Evidence/Observation 支持同一事实时，合并 support refs，不复制事实；
2. 同一 Fact 可以拥有多个 importance roles/allowed surfaces，通过 refs 进入不同分组；
3. 相似但可独立为真的命题不得仅因 wording 接近而合并；
4. 不能把多个 atomic facts union 成一个新复合事实，除非上游已有合法 progression/relation/derived fact；
5. safe parent proposition 与具体 child fact 保持不同 identity；
6. contradicted/invalidated fact 不物理删除旧 artifact，而在 current projection 中标记不可用并保留 audit。

**案例：** “看到塔楼”和“走到河边”是两个可独立为真的 Facts；“沿路从塔楼走到河边”还需要 grounded order/progression relation，不能由 Writer 或 A3 自由拼接。

### 10.3 ChapterFacts 分组

ChapterFacts 以引用分组，不复制事实内容：

~~~text
identity_fact_refs[]
story_core_fact_refs[]
progression_relation_fact_refs[]
supporting_detail_fact_refs[]
atmosphere_basis_fact_refs[]
temporal_fact_refs[]
location_entity_fact_refs[]
user_confirmed_fact_refs[]
canonical_tag_candidate_fact_refs[]
constraint_refs[]
reserved_for_selected_aha_refs[]
forbidden_fact_audit_ref
~~~

#### Identity

至少有一个稳定的 Memory identity basis，且必须与 S09 selected Memory/core basis、S10 final media coverage 一致。找不到 identity 不用氛围句补救，进入 unresolved/invalid。

#### Story Core

保存所有有资格竞争 Story 核心的 Facts，不在 A3 选择赢家。一个长 Chapter 可以有多个 core candidates，但后续 C 必须压缩为最小充分 Claim set。

#### Progression / Relation

单独保存进入、转折、恢复、结果、同时间组、无相对顺序等关系。对象 Facts 存在不自动证明它们的叙事关系。

#### Supporting Detail

保存真实次要细节，但明确不得因数量、画面美感或生成便利升级为核心。

#### Atmosphere Basis

只保存可支持 4.3 Grounded Atmosphere 的证据基础或 `NON_FACTUAL_TONE_ONLY` permission，不直接生成修辞。

#### Constraints / Reservation / Forbidden Audit

- Constraint 不进入用户可见 Fact list，但必须传给 Writer/validator；
- selected Aha core 单独 reservation；
- Forbidden 只保留 ref、reason 与 provenance，不传给生成候选。

### 10.4 AhaFacts 严格结构

AhaFacts 不是缩小版 ChapterFacts。每个 selected Aha 必须围绕唯一 peak：

~~~text
one origin Moment
one core_peak_event_ref
one or more atomic peak_fact_refs for that same event
0–2 necessary adjacent support groups
0..N observable emphasis candidate facts
trusted time/location/user-confirmed metadata
chapter-reservation refs
limitations / forbidden audit
~~~

这里的 `necessary adjacent support groups` 是上游为 peak 验证/解释保留的完整 eligible inventory，不表示它们已经获得用户可见 necessity。C3b2 仍默认选择 0，并对最多两组 support 逐项评估后才可选 0–1 组进入 Moment Line。

多个 atomic peak facts 可以共同描述同一个 peak event，例如同一次“甜品切开”与“流心出现”的 predicate/core arguments/visible change；它们必须共同构成上游已选定的同一 peak identity。可分离的“立即停顿”“同行者回应”属于 adjacent support，不得塞入 `atomic_peak_fact_refs[]`；局部活动阶段/地点属于 context candidate。只有当某个 reaction/result 本身就是上游选定的 peak identity 时，才可成为 `AHA_PEAK_CORE`。

C3b2 确认后，`trusted time/location/user-confirmed metadata` 中同时进入 Aha 自身 Fact/Claim scope、grounded、与 active media/core peak 相容、可能解除局部歧义且不扩成 Chapter 背景的 Fact，可以成为 `AHA_LOCAL_CONTEXT_CANDIDATE`。A3/B2 只判 candidate eligibility，不提前宣称它“必要”；necessity、singleton group identity、selection 与 removal test 只由 C3b2 决定。metadata 存在不等于必须写入 Moment Line；exact time 仍主要属于 Time Label，Chapter 的路线、准备与后续也不得借 context 名义回流 Aha。

同一 AhaFacts 中，只有已经规范化为可独立验真的动作速度、突发边界、可观察强度变化或感知属性 Fact，才可进入 `observable_emphasis_candidate_fact_refs[]`。A3 只保存完整候选，不决定它是否值得出现在用户文字中；B2 验证其 surface 与 attachment eligibility，C3b3 才默认从 0 开始、最多选择 1 项。纯粹“更有氛围”的 permission、用户心理或编辑评价不进入该数组。

AhaFacts 禁止纳入：

- 整个 Chapter 的准备、过程与结局；
- 另一个局部高光；
- 为凑文字而加入的邻近漂亮画面；
- 被 V1.20 reservation 给 Chapter core 的 same-story facts；
- 超出 S07 Aha interval 的内容。

### 10.5 用户文字与 metadata 分离

用户原文/用户确认事实、device metadata、observed facts 与 derived relations 在 projection 中分别保留 source type，不融合成无来源的自然语言摘要：

- user-authored text 保存 immutable ref，不在 A3 改写；
- user-confirmed proposition 可进入 Fact roles，但继续指向确认记录；
- capture/device metadata 只在其能力范围内使用；
- derived Fact 保存全部 parent refs 与 rule；
- 一个事实由多类 source 共同支持时保留各自 provenance。

具体“用户原文是否优先于 AI Story、是否并排展示或是否允许转述”是用户体验定义，留到 S11-D/E 单独询问，不在 A3 偷定。

### 10.6 Active Media Coverage Map

ChapterFacts/AhaFacts 必须携带 fact-to-active-media coverage，而不是让 Writer重新猜：

~~~text
FactMediaCoverageEntry
  canonical_fact_ref
  active_media_consumer_refs[]
  active_anchor_refs[]
  coverage_role =
    DIRECT
    | SET_LEVEL_INDIRECT
    | NONVISIBLE_GROUNDED
    | NONVISUAL_SOURCE
    | UNRESOLVED
  route_specific_claim_compatibility
  limitation_refs[]
~~~

一个 final media 可以支持多个 Facts，一个 Fact 也可由多个 media/evidence 支持；但“一张媒体很有代表性”不能让它自动支持同 Memory 的全部 Facts。

### 10.7 Completeness 与 Readiness

A3 只有在全部 current eligible fact refs 都有最终去向时才完成：

~~~text
FACTS_READY
FACTS_READY_WITH_LIMITATIONS
FACTS_UNRESOLVED
FACTS_CONTRACT_INVALID
~~~

- `READY`：所有 relevant facts、roles、coverage、constraints、reservation 与 audit 完整；
- `READY_WITH_LIMITATIONS`：可安全写作，但存在明确的禁止/降级边界；
- `UNRESOLVED`：可能改变 identity/core/allowed surfaces 的事实、冲突或 coverage 未解决；
- `CONTRACT_INVALID`：Revision、scope、lineage、fact identity、source/provenance 或 projection 引用非法。

`READY_WITH_LIMITATIONS` 不等于 Writer 可以忽略限制；限制必须成为生成与验证输入。`UNRESOLVED/INVALID` 不通过更宽泛的空话自动继续。

### 10.8 输出

~~~text
ChapterFacts
  selected_memory_ref
  stable_memory_id
  revision_ref
  active_s10_projection_ref
  active_projection_fingerprint
  memory_identity_basis_refs[]
  canonical_fact_entries[]
    canonical_fact_ref
    normalized_proposition_ref
    source_type_refs[]
    evidence_and_validation_refs[]
    importance_roles[]
    assertion_ceiling
    allowed_surfaces[]
    media_visibility_role
    fact_media_coverage_ref
    derivation_dependency_refs[]
    limitation_refs[]
    reservation_refs[]
  identity_fact_refs[]
  story_core_fact_refs[]
  progression_relation_fact_refs[]
  supporting_detail_fact_refs[]
  atmosphere_basis_fact_refs[]
  temporal_fact_refs[]
  location_entity_fact_refs[]
  user_confirmed_fact_refs[]
  canonical_tag_candidate_fact_refs[]
  constraint_refs[]
  reserved_for_selected_aha_refs[]
  forbidden_fact_audit_ref
  fact_media_coverage_map_ref
  facts_state
  policy_and_signal_versions
  facts_fingerprint
  construction_audit

AhaFacts
  selected_memory_ref
  stable_memory_id
  revision_ref
  active_s10_projection_ref
  active_projection_fingerprint
  origin_moment_ref
  core_peak_event_ref
  atomic_peak_fact_refs[]
  adjacent_support_groups[0..2]
    adjacent_support_group_ref
    direction
      BEFORE
      | AFTER
      | COTEMPORAL_REACTION
    support_event_ref
    member_fact_refs[]
    relation_refs[]
    core_peak_event_ref
    group_fingerprint
  temporal_location_metadata_refs[]
  local_context_candidate_fact_refs[]
  observable_emphasis_candidate_fact_refs[]
  user_confirmed_fact_refs[]
  selected_chapter_reservation_refs[]
  atmosphere_basis_fact_refs[]
  constraint_refs[]
  forbidden_fact_audit_ref
  fact_media_coverage_map_ref
  facts_state
  policy_and_signal_versions
  facts_fingerprint
  construction_audit
~~~

`local_context_candidate_fact_refs[]` 只引用同一 AhaFacts 内已经存在的 canonical Fact（常来自 local activity/scene 或 `temporal_location_metadata_refs[]`），不复制 Fact，也不创建 group。它表达“可能解除 standalone 歧义”，不是“已经必要”；C3b2 才产生 singleton group identity 与 necessity/selection decision。

`observable_emphasis_candidate_fact_refs[]` 同样只引用 current AhaFacts 内既有 canonical Facts，不把形容词字符串当作事实。每项必须能在后续 Claim Ledger 中形成一个绑定 `emphasis_target_claim_ref + emphasis_attachment_relation_ref` 的限定 Claim。AhaFacts 中既有 `atmosphere_basis_fact_refs[]` 继续服务完整事实投影与未来 surface 审计，但 V1 generated Aha 不从该数组消费独立 Tone；C3b3 读取前述 evidence-bearing observable candidates，并按 28.12 另外消费既有 base action/entity semantics 与 versioned light-affect lexicon，不把 lexical permission写回 AhaFacts。

`adjacent_support_groups[0..2]` 的唯一 producer 是 A3，0–2 为三种 direction 合计上限，不是每侧各 2 组。每组至少一个 member Fact 与一条把该组绑定到同一 `core_peak_event_ref` 的合法 relation；所有 member Facts 必须描述同一个 `support_event_ref`，两个可分离 reaction/result 不能打包成一组绕过上限。Group identity 由 `(revision_ref, active_projection_fingerprint, core_peak_event_ref, support_event_ref, direction, sorted_member_fact_refs, sorted_relation_refs)` 确定性产生。B2 只验证并携带 A3 的既有 `adjacent_support_group_ref`，C3b2 只评估/选择，任何下游都不得重新拆组、并组或生成新的 adjacent support group identity。

`support_event_ref` 必须解析到 current AhaFacts/active projection 中已经存在、且所有 member Facts 都明确引用的 normalized event identity；该 event 必须位于 S07 已确定的 Aha interval/scope 内。A3 只把 existing event/fact/relation refs 组织成 support group，不得新建 Moment、Window、event boundary、peak 或 support-event identity。无法唯一解析、跨 interval 或需要 A3 推断新 event 时，AhaFacts 进入 `FACTS_CONTRACT_INVALID`。

### 10.9 Cross-Revision 与 Runtime

1. 每个 Revision 产生不可变 ChapterFacts/AhaFacts；
2. canonical Fact identity、source、Evidence、roles、surface permission 与 active projection 均一致时可复用；
3. 新 Fact 只稍微改善 wording 不必删除旧 identity；
4. S10 activation delta 改变 coverage/claim compatibility 时，生成新 projection 或明确的 fact-projection delta；
5. D1 删除的 media member 若是某 Fact 唯一支持，Fact 必须降级/移除其 surface permission；
6. selected Aha/Chapter relation 改变时重新计算 reservation；
7. prior narrative 不因 Fact inventory 增多就自动重写，是否改变由后续 Claim/Narrative continuity gate 决定。

### 10.10 案例

#### 古镇 Chapter

~~~text
Identity
  traditional-street walk

Story Core
  enter through gate
  observe distinct traditional architecture
  reach riverside

Progression
  gate → street → riverside

Support
  pass ordinary street stalls

Atmosphere Basis
  architecture details / riverside light

Constraint
  exact town name unresolved

Reserved for selected Aha
  first-sip surprise interaction
~~~

最终 Story 仍只选极少 Claim；完整 Facts 不等于全部写出。

#### 陶艺长 Manual

上游已验证准备、拉坯、成品三个不同 Beat：三个 core facts 与 `ACTION_RESULT/PROGRESSION` relation 分开保存。A3 不把它们预写成“完成了一件满意的作品”；“满意”仍无 user-state Evidence。

#### 生日＋独立猫跳上蛋糕 Aha

Birthday ChapterFacts 保存蛋糕、烛光、围聚、合照等 core；猫跳上蛋糕 peak 进入 `reserved_for_selected_aha_refs`。AhaFacts 只保存跳上蛋糕、即时反应和必要前后支持，不把整场生日复制进去。

#### 普通会议

白板、桌边记录和讨论可完整保存；若没有 outcome Evidence，`完成重要进展` 进入 forbidden/constraint，而不是因 Facts 太普通就生成一个积极结果。

### 10.11 Invariants、成本与边界

1. A3 保存完整 normalized eligible inventory，不做 Top-K；
2. 完整不等于复制 Raw/Observation 文本，只保存 canonical refs 与 roles；
3. 同一 Fact 一份 identity、多 Evidence、多 role refs；
4. composite/progression Fact 必须有合法 relation/dependency；
5. ChapterFacts 与 selected Memory/core/final media 始终对齐；
6. AhaFacts 只有一个 peak event，不扩成小 Chapter；
7. support/constraint/forbidden 不因数量升级；
8. 每个 eligible/restricted fact 都有明确去向；
9. user text、observed、metadata、derived provenance 不融合丢失；
10. active media coverage 由 S10 refs 映射，不由 Writer猜测；
11. A3 不生成 Claim/Title/Story/Moment Line/Tag，不调用 Writer/VLM/外部 lookup；
12. 计算与存储规模随 selected Memory canonical facts 增长，不随全天 RawAsset 像素或 HQ 大小增长；
13. A3 是 `adjacent_support_group_ref` 的唯一 producer，所有 direction 合计最多 2 组；B2/C3b2/B3 不重新分组；
14. local context 在 A3 只保存 candidate Fact refs，不创建 group、不判断用户可见 necessity；
15. observable emphasis 在 A3 只保存 evidence-bearing candidate Fact refs，不选择措辞、不消费 Tone permission；
16. `support_event_ref` 只能引用 current Aha scope 内既有 normalized event identity，A3 不创建新 event/interval/boundary。

## 11. S11-A Closeout 与下一检查点

**状态：DESIGN CLOSED / PENDING S11 CROSS-CHECK / NOT FROZEN**

S11-A 已确认：整个 selected Memory 的可靠事实可进入分层投影；Fact importance、assertion ceiling 与 surfaces 分离；用户文案不展示算法犹豫；ChapterFacts 保存完整 normalized inventory；AhaFacts 严格围绕单一 peak；Chapter/Aha reservation、active-media coverage 与 runtime reprojection 均有明确合同。

下一步进入 S11-B1：定义 atomic Claim。需要区分“一个用户句子”和“一个可独立验证的事实命题”，并决定一句自然语言是否可以包含多个 Claim，以及连接词、顺序词和氛围修辞如何单独审计。

## 12. S11-B1｜Atomic Claim 与自然句子

**状态：CONFIRMED**

### 12.1 用户体验合同

V1 锁定：

> 一句自然文案可以组合多个 Atomic Claim，但不能因为它们被写在同一句话里就共享证据；每个事实、限定词和关系词都必须独立合法。

原因：

1. 如果强制“一句只能有一个 Claim”，Chapter Story 会像数据库清单，失去自然节奏；
2. 如果整句只做一次总体验证，一个被支持的事实可能掩护同句中的臆测；
3. 因此，用户看到的是自然的一至两句话，系统内部看到的是可逐项验证的 Claim 组合；
4. Claim 拆分与审计只服务于内部可靠性，不向用户展示编号、置信度或算法犹豫。

本检查点不锁定“一句最多组合几个 Claim”。该数量直接影响文案密度与阅读体验，留到 S11-C 结合实际 Content Plan 与案例单独决策。

### 12.2 Production ClaimCandidateProjection

Production 不先让 Writer 写句子再猜 Claim。B0 从 A3 的 canonical Facts 与已经验证的 relation/dependency 中，确定性地产生 surface-independent semantic candidates：

~~~text
ClaimCandidateProjection
  candidate_projection_ref
  selected_memory_ref
  revision_ref
  active_projection_fingerprint
  atomic_claim_candidates[]
  claim_qualifier_attachment_candidates[]
    emphasis_attachment_relation_ref
    qualifier_claim_ref
    emphasis_target_claim_ref
    emphasis_qualifier_type
    source_fact_and_relation_refs[]
  strict_subclaim_refs_by_claim{}
  grounded_parent_closure_refs_by_claim{}
  implicit_assertion_candidates[]
    title_assertion_refs[]
    time_label_assertion_refs[]
    canonical_tag_assertion_refs[]
  implicit_surface_assertion_attachment_candidates[]
    assertion_attachment_ref
    target_surface
    base_assertion_ref
    modifier_assertion_ref
    attachment_type
    source_fact_and_relation_refs[]
  tone_permission_candidates[]
  source_fact_and_relation_refs[]
  candidate_projection_fingerprint
~~~

规则：

1. `atomic_claim_candidates` 只把已有 Fact/Relation 标准化为命题，不生成自然语言；
2. Claim identity 由 surface-independent semantics 与 source/dependency refs 决定；
3. Title、Time Label、Tag 即使不是完整句子，也必须映射到一个 `implicit_normalized_assertion_ref` 后才能验真；
4. `tone_permission_candidates` 与 factual Claim 分离，只声明某类氛围修辞是否有合法 basis；
5. B0 不创建新事实、不选择最终 surface、不调用 Writer/VLM；
6. 每个 Claim 的 strict-subclaim 与 grounded-parent closure 在同一个不可变 projection 中预生成并去重；
7. B2 replacement 只能引用这些既有 refs；若合法 parent 因新事实只存在于新 projection，则先生成新的不可变 B0 projection revision，再完整重跑 B2；
8. D 生成自然语言后，E 再把实际文字 span 映射回已批准 Claim/Tone permission，检查是否偷偷增加含义。
9. A3 observable-emphasis candidate Fact 进入 B0 时，必须产生独立 qualifier Claim 与 `ClaimQualifierAttachment`；B0 只投影已有 Fact/Relation，不选择它是否进入 Moment Line，也不把 Tone permission 改装成 qualifier；
10. 可独立为真的非句子 surface modifier 必须使用独立 `ImplicitSurfaceAssertion`；B0 只在已有 Fact/Relation 能证明 attachment 时，确定性产生 `ImplicitSurfaceAssertionAttachment` candidate。B0 不决定 C2 是否选择它，也不能由 Writer临时创建 attachment。

非句子 surface 与 Tone 的最小对象：

~~~text
ImplicitSurfaceAssertion
  assertion_ref
  atomic_claim_ref
  target_surface  # TITLE | TIME_LABEL | CANONICAL_TAG
  normalized_assertion_ref
  source_semantic_spec_ref?  # TIME_LABEL 时必填
  candidate_eligibility?     # TIME_LABEL: BASE_ELIGIBLE | CONTINUITY_RETAIN_ONLY
  candidate_projection_ref

ImplicitSurfaceAssertionAttachment
  assertion_attachment_ref
  target_surface  # V1 current use: TITLE
  base_assertion_ref
  modifier_assertion_ref
  attachment_type
    GROUNDED_SCOPE_MODIFIER
    | GROUNDED_EXACT_ENTITY_MODIFIER
    | GROUNDED_OBSERVABLE_CONTEXT_MODIFIER
  source_fact_and_relation_refs[]
  candidate_projection_ref

TonePermissionCandidate
  tone_candidate_ref
  basis_kind  # EVIDENCE_GROUNDED | NON_FACTUAL_POLICY_PERMISSION
  basis_refs[]
  allowed_tone_scope_ref
  candidate_projection_ref
~~~

`AHA_MOMENT_LINE` 是句子型 narrative surface，像 Chapter Story 一样直接使用 Atomic Claims；它不是 Title/Time/Tag 一类 implicit non-sentence assertion，因此不进入 `ImplicitSurfaceAssertion`。`ImplicitSurfaceAssertionAttachment` 也不用于 Aha observable emphasis；后者继续使用独立的 `ClaimQualifierAttachment` 合同。

**D5b1 contract-alignment amendment：** `implicit_assertion_candidates.canonical_tag_assertion_refs[]`和`target_surface=CANONICAL_TAG`在 B0 仍保留兼容名称，但语义为 typed D5 index candidate umbrella。B0 只标准化 exact assertion，不决定它最终成为`CanonicalTagAssignment`还是`EntityIndexLink`；该类型路由属于 D5，并且不得改变 assertion、Evidence 或 assertability ceiling。

Time Label assertion 必须引用 D3 deterministic policy 产生的 exact `source_semantic_spec_ref`，并原样携带 `candidate_eligibility`；B0 只把该 spec materialize 成可验真的 assertion，不读取 prior published artifact，也不把 `CONTINUITY_RETAIN_ONLY` 升级成 base candidate。Title/Tag 没有该 D3 spec 时，这两个 optional 字段保持为空。

`ClaimQualifierAttachment` 让 base Claim identity 与 optional qualifier 分离。例如“流心淌出”仍是一条稳定 base Claim，“该流动速度较慢”是另一条 Claim，二者通过 attachment 相连。这样 qualifier 失效时可以只删除一个窄 span，不把整个 peak Claim 重新命名。C3b3 的 observable qualifier 必须沿用该 B0 attachment，B2/C3b3 不得临时新建。

### 12.3 Atomic Claim 的定义

Atomic Claim 是：

> 可能被用户可见 surface 表达、并且可以被独立判断为成立或不成立的最小标准化事实命题。

Atomic 不是按逗号、词数或语法形式机械切分，而是按“能否独立改变真假”判断：

- 如果一部分可能成立、另一部分可能不成立，必须拆成不同 Claim；
- 如果一个修饰语删除后，剩余事实仍然成立，该修饰语通常需要自己的 Claim 或限定字段；
- 如果两个事实之间的顺序、因果、持续或集合关系可能单独不成立，该关系必须是独立 Claim；
- 如果一句话使用更宽泛的上位事实，必须引用 A2 已允许的 grounded parent proposition，不能为了减少 Claim 数量临时概括。

例：

> 从牌坊走进古街，木雕、塔楼和河岸依次出现。

至少包含：

1. 发生了“从牌坊进入古街”的移动/进入事件；
2. 木雕出现；
3. 塔楼出现；
4. 河岸出现；
5. 三者按所写顺序出现。

前四项都有 Evidence，不代表第 5 项自动成立。若时间关系不足，应删掉“依次”或改写，而不是让整句共享一个笼统的“古镇游览”证据。

### 12.4 Atomicity Test

每个候选 Claim 依次通过四个问题：

1. **独立真假测试**：其中一个成分为假时，其余成分能否仍为真？能则拆分；
2. **独立证据测试**：不同成分是否依赖不同 Fact/Evidence？是则拆分；
3. **关系增义测试**：顺序、因果、持续、范围、次数或比较是否增加了新事实？是则单独建 Claim；
4. **安全上位测试**：若改成更宽泛表述，是否存在已经 grounded 的 parent Fact？不存在则不能用概括逃避拆分。

例：

> 红色塔楼立在河岸边。

内部至少区分：

- 塔楼存在；
- 塔楼为红色；
- 塔楼与河岸具有“在旁边”的空间关系。

若只有塔楼与河岸分别出现、没有空间关系 Evidence，可以保留两个 presence Claim，但不能写“立在河岸边”。

### 12.5 Claim 的最小结构

~~~text
AtomicClaim
  claim_ref
  target_memory_ref
  claim_kind
  subject_ref
  predicate_ref
  object_or_value_ref
  qualifier_refs[]
  temporal_scope_ref
  spatial_scope_ref
  polarity
  negative_assertion_basis_ref
  quantifier_scope_ref
  modality_and_assertion_ceiling
  source_fact_refs[]
  evidence_dependency_refs[]
  relation_dependency_refs[]
  derivation_ref
~~~

字段含义：

- `subject / predicate / object`：谁或什么，发生了什么，与什么对象/结果相关；
- `qualifier`：颜色、方式、程度等会改变事实含义的修饰；
- `temporal / spatial scope`：该事实发生在哪段时间、哪个位置；
- `polarity`：发生、未发生或明确缺失；
- `negative_assertion_basis`：若为否定/缺失命题，证明观察域闭合的依据；
- `quantifier`：一个、多个、全部、再次、持续多久等范围；
- `modality`：该 Fact 允许多具体地断言；
- `source/evidence/dependency`：Claim 分别由哪些事实、证据和关系支撑；

`target_surface`、media compatibility 与 Chapter/Aha reservation 不属于 Atomic Claim identity；它们进入 B2 的 `ClaimSurfaceDecision`。这样同一命题在 Title、Story、Aha Moment Line、Tag 中保持同一个 semantic identity，但可以得到不同 surface decision。

对 C3b3 的 optional observable emphasis，`qualifier_refs[]` 不把速度／突发性直接焊进 base event Claim；它使用独立 Atomic Claim 与 `ClaimQualifierAttachment`。只有删除后会使 base predicate/core argument 本身不完整的属性，才留在 base Claim 的必要语义结构中，并且不再占 C3b3 emphasis 名额。

B1 只定义 Claim 的最小语义单元；Claim 的支持状态、冲突状态与 Ledger 生命周期在 S11-B2 定义。

### 12.6 关系词本身也是事实

以下词语不能被当作文风填充物，它们会增加可验证含义：

| 语义类别 | 常见表达 | 需要的独立支持 |
| --- | --- | --- |
| 顺序 | 随后、接着、最后、依次 | 事件时间关系 |
| 持续 | 一路、一直、整整、始终 | 连续性与时间覆盖 |
| 完整范围 | 所有、每一处、整座、全部 | 集合边界与完整性 |
| 次数 | 再次、又一次、第一次 | 可比较的历史/当日事件 |
| 因果 | 因此、于是、引得、让……变得 | 因果 Evidence，不只是先后 |
| 转折/对比 | 却、反而、从……到…… | 两侧事实及其对比/变化关系 |
| 结果 | 终于完成、取得进展、顺利结束 | 结果事实与必要前置关系 |

例：

> 蜡烛熄灭后，房间里响起笑声。

需要：蜡烛熄灭、笑声出现、笑声晚于熄灭三个部分。若 Evidence 只支持先后，可以写“之后”；不能升级为“吹灭蜡烛引得大家笑起来”，因为“引得”额外声明了因果。

### 12.7 Factual Claim 与 Tone Span 分离

V1 允许 grounded atmosphere，但氛围修辞不是事实证据。合同在语义上区分：

- `FACTUAL_CLAIM_SPAN`：对世界、事件、时间、地点、人物或物体作事实断言；
- `RELATION_CLAIM_SPAN`：声明顺序、空间、因果、持续、对比或结果；
- `NON_FACTUAL_TONE_SPAN`：不声称用户内心状态、只负责节奏与氛围的修辞。

B/C 阶段只规划 Claim refs 与适用 surface 的 `TonePermissionCandidate`；D 负责写自然句；E 才对真实输出标注上述 spans，并检查实际措辞的隐含含义。B1 的句子拆分案例是审计说明，不是生产时必须先写文案的执行顺序。C3b3 已进一步确认：V1 generated Aha 不适用通用 `NON_FACTUAL_TONE_SPAN`，事实性强调只允许另有 Claim/Evidence 的 observable qualifier；28.12 Light-Affect v1.1 另行允许一个不进入事实图、受 exact permission 约束的轻量 lexical span。

Tone Span 必须满足：

1. 有 A2 `ATMOSPHERE` surface 允许的 `EVIDENCE_GROUNDED` basis，或明确的 `NON_FACTUAL_TONE_ONLY / NON_FACTUAL_POLICY_PERMISSION`；
2. 不新增物体、事件、时间、地点或用户情绪事实；
3. 不能为相邻 Claim 提供 Evidence；
4. 删除 Tone Span 后，句子的事实内容不应改变；
5. 若一个词既可能是修辞又可能被普通用户理解为事实，按事实 Claim 审计。

`NON_FACTUAL_POLICY_PERMISSION` 不要求伪造一条视觉 Fact，但必须引用版本化 tone policy、绑定当前 Memory，并通过“不新增事实/不推断用户状态”检查；它不是任意诗意表达的通行证。

例：

> 晚光落在河岸，也给这段古街漫步留下一点温柔的余韵。

- “晚光落在河岸”是 Factual Claim，需要时间/视觉 Evidence；
- “温柔的余韵”可作为 Tone Span；
- 但它不能证明用户感到温柔、治愈、幸福或不舍。

反例：

> 你终于在河岸找到了久违的平静。

“终于”“找到了”“久违”“平静”共同声明了历史、结果和用户内心状态；没有用户明确输入时不能把它们降格解释成普通氛围修辞。

### 12.8 Negative / Absence Claim 的闭世界门

Diary One 是稀疏采样系统，“没有拍到”不等于“没有发生”。以下 Claim 需要额外的 closed-world basis：

- 没有人出现；
- 用户没有停留；
- 整段路上没有下雨；
- 会议没有产生结果；
- 某事件从未发生。

只有用户明确确认、设备确定状态、完整覆盖记录或其他能证明观察域闭合的 Evidence，才允许否定/缺失 Claim。普通 Auto 间隔采样、单张照片、局部视频或 VLM 未检测到对象，一律不能支持 absence。

例：一帧空街只能支持“该帧中未观察到明显人群”，不能写“古街上没有人”；无结果画面只能禁止正向结果推断，不能反向声称“会议没有成果”。

### 12.9 失效 Claim 的最小改写原则

当一句话中的某个 Claim 未通过验证，不必机械删除整句话：

1. 首先移除或替换失效的限定词/关系词；
2. 其余独立成立的 Claim 可以保留；
3. 如果失效 Claim 是整句主干或改变 Memory identity，则整句回到 Content Plan 重建；
4. 不能以模糊词、被动语态或氛围修辞隐藏失效事实；
5. 用户最终只看到自然改写后的结果，不看到内部失败提示。

例：

原句：

> 从牌坊走进古街，木雕、塔楼和河岸依次展开。

若只有顺序 Evidence 不足，可改为：

> 走在古街上，眼前有牌坊、木雕和塔楼，也有临水的河岸。

这些细节共同出现在同一段古街漫步中，仍需 selected Memory membership/identity 支持。若连该集合关系也不足，则继续拆开或放弃组合，不得把“眼前有……”当作无意义的语法连接。

### 12.10 案例交叉检查

#### 案例 A｜古镇游览

时间线支持牌坊 → 木雕 → 塔楼 → 河岸时：

> 从牌坊走进古街，木雕、塔楼和河岸依次展开。

可以通过；每个场景事实和 progression relation 分别绑定 Evidence。

如果只知道这些元素属于同一 Chapter、不知道准确顺序：

> 走在古街上，眼前有牌坊、木雕和塔楼，也有临水的河岸。

可在 membership/identity relation 受支持时通过，但不能保留“依次”。

#### 案例 B｜生日聚会

> 蜡烛熄灭后，大家围着蛋糕笑了起来。

包含熄灭、围聚、笑声/笑容以及时间关系。即使它们都出现，也不能自动改成“吹蜡烛让大家笑了起来”，后者多了因果 Claim。

#### 案例 C｜陶艺长 Manual

> 从拉坯到成形，泥土慢慢有了器物的轮廓。

需要起点状态、终点状态和 progression relation。只有拉坯画面与成品画面、但中间连续性不足时，可以表达前后结果，不得声称完整制作过程被持续记录。

#### 案例 D｜普通会议

> 白板记录和桌边讨论，为上午的会议带来了重要进展。

“白板记录”“桌边讨论”“上午会议”可以分别成立，但“带来重要进展”同时包含因果、结果和价值判断；没有 outcome Evidence 时必须删除，而不是用积极语气补齐。

#### 案例 E｜Aha 与 Chapter 事实隔离

生日 Chapter 可以写蛋糕、烛光与围聚；若“猫突然跳上蛋糕”已被选为独立 Aha，Chapter 句子不能用“聚会中最意外的是猫跳上蛋糕”重新夺回 peak。该 Claim 即使事实成立，也因 reservation 不允许用于 Chapter Story Core。

### 12.11 Invariants、成本与边界

1. Sentence 不等于 Claim；一句自然句允许包含多个 Atomic Claim；
2. 每个 Claim 独立绑定 Fact/Evidence，不共享笼统句级证据；
3. 可独立改变真假的主体、动作、属性、范围与关系必须拆分；
4. 顺序、因果、持续、完整范围、次数、结果与对比都需要独立支持；
5. Tone Span 不新增事实、不推断用户内心、不充当 Evidence；
6. 一个 Claim 失败时优先最小改写，但不得掩盖失败；
7. 当前 active media 与 Chapter/Aha reservation 仍然约束 Claim；
8. Atomic Claim 拆分只存在于内部，用户不看到 Claim 标签或算法置信度；
9. B1 不决定最终句数之外的 Claim 数量上限，也不生成最终文案；
10. Atomic Claim identity 与 surface decision 分离；Chapter Story/Aha Moment Line 直接使用 Atomic Claims，Title/Tag/Time Label 的事实含义映射到 implicit assertion，Tone 使用独立 permission；
11. 稀疏采样中的未检测不能支持 Negative/Absence Claim；
12. 计算发生在 A3 已投影的 canonical Facts 上，不重新读取全天 Raw Assets，不增加 VLM/API 调用；
13. C3b3 optional qualifier 在 B0 中使用独立 Claim＋attachment，不与 base Claim identity 融合，也不由 B2/Writer临时创造。

## 13. 下一检查点

下一步进入 S11-B2：建立 Claim Ledger 的 semantic 与 surface 决策状态。重点定义一个 Claim 如何从候选进入 `CLAIM_SEMANTIC_*`，再得到 `SURFACE_*`，以及多 Evidence、冲突、active-media 变化和 Chapter/Aha reservation 如何共同决定它能否进入 Title、Story、Aha Moment Line、Tag 或 Atmosphere。

## 14. S11-B2｜Claim Ledger 支持状态与下游阻断合同

**状态：CONFIRMED**

### 14.1 产品质量合同｜目标数量不是发布配额

V1 锁定：

> 3～4 个 Chapter、2～3 个 Aha 是质量达标后的目标区间，不是必须完成的数量配额；没有可靠核心文案的候选不发布。

这里仅继承 S09 对“丰富日”的质量合格后软偏好，不创建 S11 数量目标，也不覆盖 S09 的 `CHAPTER_DAY / HIGHLIGHT_DAY / EMPTY_DAY`、Preview/Final 容量、第五章、retention、lineage 或 ordering 规则。合法日可以从一开始就少于该丰富日偏好。

具体规则：

1. 候选的原 Story Core 失效时，先从同一 selected Memory 的其他合法 `STORY_CORE` Facts 重建；
2. Chapter 至少需要一个可靠 `CHAPTER_STORY_CORE` Claim；Aha 至少需要一个 `target_surface=AHA_MOMENT_LINE` 且指向其 `core_peak_event_ref` 的 `AHA_PEAK_CORE` Claim；
3. 同一 selected Memory 内仍无法形成所需核心时，S11 输出 Claim-set failure，不自行删除、替换或补位；
4. 当前 Revision 不能继续到正常发布：由后续 S12/编排层按冻结合同保持仍合法 prior，或在无 prior 时 `BLOCKED_NO_PUBLISHABLE_REVISION`；
5. S11 不搜索未选 Candidate，不拉入“第四名”，也不触发新的 S09 selection attempt；
6. V1.21 的一次有界 S09 re-selection 仍只服务于其已冻结的 proven pre-batch media insufficiency，不扩展到 narrative failure；
7. 不发布只有媒体、Title、Tag 而没有 Story Core 的残缺 Chapter；
8. 不使用“记录了这段美好时光”等空泛万能句补齐数量；
9. Aha 没有可靠、独立的 peak Claim 时同样阻断当前 Revision，不把普通 Chapter 片段包装成 Aha。

这条合同的目标是让数量服务于质量，而不是让低质量文案服务于数量。

### 14.2 Claim Ledger 的职责

Claim Ledger 是 S11 内部的“逐项事实审计账本”。它不直接写最终句子，而是回答：

1. 这个 Atomic Claim 是否被对应 Fact/Evidence 支持；
2. 它的具体程度是否超过 assertion ceiling；
3. 它是否允许进入当前 surface；
4. 它是否与 active S10 media projection 相容；
5. 它是否违反 Chapter/Aha reservation；
6. 如果当前说法不能使用，是否存在一个已经 grounded 的安全改写；
7. 最终为什么通过、为什么改写、为什么禁止。

Ledger 的事实身份、semantic decision 与 surface decision 分开。事实层先判断命题是否成立，surface 层再判断它是否允许出现在特定位置：

~~~text
ClaimSemanticDecision
  (atomic_claim_ref, candidate_projection_ref)

ClaimSurfaceDecision
  (atomic_claim_ref, target_surface, active_projection_fingerprint)
~~~

因此，同一事实可以在 `STORY_SUPPORT` 合法、在 `TITLE` 不合法；同一个 Aha peak Claim 可以作为 `AHA_PEAK_CORE` 合法、在 Chapter Story Core 因 reservation 被禁止。

~~~text
ClaimSurfaceDecision
  atomic_claim_ref
  candidate_projection_ref
  target_surface
    TITLE
    | STORY_CORE
    | STORY_SUPPORT
    | AHA_MOMENT_LINE
    | TIME_LABEL
    | CANONICAL_TAG
    | ATMOSPHERE
  active_projection_fingerprint
  surface_assertion_ref
  memory_type
  narrative_claim_role?
    CHAPTER_STORY_CORE
    CHAPTER_STORY_SUPPORT
    AHA_PEAK_CORE
    AHA_ADJACENT_SUPPORT
    AHA_LOCAL_CONTEXT_CANDIDATE
    AHA_OBSERVABLE_EMPHASIS_CANDIDATE
  core_peak_event_ref?
  adjacent_support_group_ref?
  emphasis_target_claim_ref?
  emphasis_qualifier_type?
    OBSERVABLE_MOTION_RATE
    | OBSERVABLE_ONSET_ABRUPTNESS
    | OBSERVABLE_INTENSITY_CHANGE
    | OBSERVABLE_SENSORY_ATTRIBUTE
  emphasis_attachment_relation_ref?
  aha_role_partition_check?
  media_compatibility_ref
  chapter_aha_reservation_ref
  surface_decision_state
    SURFACE_SUPPORTED
    SURFACE_BLOCKED
    SURFACE_CONTRACT_INVALID
  reason_codes[]
~~~

Title、Time Label 与 Tag 的非句子文字必须先指向 B0 `implicit_normalized_assertion_ref`；Aha Moment Line 与 Chapter Story 直接使用 Atomic Claims；Atmosphere 使用独立 `TonePermissionDecision`，不伪装成 Atomic Claim。

`narrative_claim_role` 只对 Chapter Story 与 `AHA_MOMENT_LINE` Claims 必填；Title/Time Label/Tag 不填，避免与 `target_surface` 重复建模。`AHA_PEAK_CORE/AHA_ADJACENT_SUPPORT/AHA_LOCAL_CONTEXT_CANDIDATE/AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 只能配对 `target_surface=AHA_MOMENT_LINE`；`core_peak_event_ref` 对四者必填。`adjacent_support_group_ref` 只对 `AHA_ADJACENT_SUPPORT` 必填；`AHA_LOCAL_CONTEXT_CANDIDATE` 在 B2 不带 group ref，因为 C3b2 尚未做 necessity test，后续由 C3b2 按 `(surface_policy_ref, revision_ref, active_projection_fingerprint, core_peak_event_ref, atomic_claim_ref)` 确定性建立 immutable singleton group。`AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 必填 `emphasis_target_claim_ref + emphasis_qualifier_type + emphasis_attachment_relation_ref`，attachment 必须 exact resolve 到 current B0 `ClaimQualifierAttachment`，且 target 必须解析到同 Revision/projection/core peak 下的一个 Aha base Claim；它在 B2 只取得候选资格，C3b3 才检查 target 是否最终被 C3b2 选入并决定 0–1 项。其他 role 的 emphasis fields 必须为空。V1 Aha peak 对 `target_surface=TITLE` 必须 `SURFACE_BLOCKED`，不能借 Title 绕过 C3b1。

`aha_role_partition_check` 对所有 Aha narrative decisions 必填，并以 upstream selected `core_peak_event_ref` 为唯一准绳：

1. peak predicate、不可缺少的 core arguments 与该 event 自身 visible change → `AHA_PEAK_CORE`；
2. 可分离的 before/after reaction 或 result → `AHA_ADJACENT_SUPPORT`；
3. local activity phase/place/scene state/user-confirmed local role → `AHA_LOCAL_CONTEXT_CANDIDATE`；
4. 附着于既有 base Claim、可直接验证且不创建新事件的动作速度／突发边界／强度变化／感知属性 → `AHA_OBSERVABLE_EMPHASIS_CANDIDATE`；
5. reaction/result 只有在上游本来就把它选为 peak identity 时才属于第 1 类，Writer/B2 不能临时升级；
6. 同一 normalized proposition、strict subclaim/parent 伪装或语义等价改写不能同时进入两个 role；否则 `SURFACE_CONTRACT_INVALID + AHA_ROLE_LAUNDERING`。

~~~text
TonePermissionDecision
  tone_candidate_ref
  candidate_projection_ref
  basis_kind
    EVIDENCE_GROUNDED
    NON_FACTUAL_POLICY_PERMISSION
  basis_refs[]
  target_memory_ref
  active_projection_fingerprint
  decision_state
    TONE_ALLOWED
    TONE_BLOCKED
    TONE_CONTRACT_INVALID
  reason_codes[]
~~~

通用 `TonePermissionDecision` 不适用于 V1 generated Aha。Chapter 可以按 D1/C 的既有合同消费合法 atmosphere permission；Aha 的“缓缓、一下子、明显变亮”等表达会改变事件断言，必须作为 `AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 接受 Claim/Evidence 审计，不能伪装成无事实 Tone。“惊喜、幸福、难忘、高光”等用户状态或编辑价值判断也不能借该角色通过。28.12 的 `AhaLightAffectiveFramingDecision` 是独立窄许可，不是该通用 Tone decision 的复用。

### 14.3 ClaimSemanticDecision 四种终态

#### `CLAIM_SEMANTIC_SUPPORTED`（简称 `SEMANTIC_SUPPORTED`）

Claim 的事实、关系、限定、Evidence、assertion ceiling、negative/quantifier 与 conflict checks 全部通过，可以进入 `ClaimSurfaceDecision`。

`SEMANTIC_SUPPORTED` 不代表允许出现在每个 surface，更不代表一定写进最终文案；surface 资格由 14.7 判断，最终是否选择由 S11-C 决定。

#### `CLAIM_SEMANTIC_REWRITE_REQUIRED`（简称 `SEMANTIC_REWRITE_REQUIRED`）

当前 Claim 不能直接使用，但存在明确、已 grounded、不会增加新事实的安全替代 Claim。

合法改写仅包括：

1. 删除无支持的限定词；
2. 删除无支持的顺序、因果、持续、次数或范围关系；
3. 改用 A2 已存在的 grounded parent proposition；
4. 在不改变事实身份的前提下，退回 source assertion ceiling 允许的具体度；
5. 引用 B0 当前 projection 已预生成的严格更弱 replacement candidate；若 Content Plan 已存在，则返回 C 重新组合剩余合法 Claims。

`SEMANTIC_REWRITE_REQUIRED` 的原 Claim 不能被渲染；只有重新验证为 `CLAIM_SEMANTIC_SUPPORTED` 且 surface 通过的 replacement Claim 才能进入文案。

改写必须终止：

1. replacement 只能删除 qualifier/relation/quantifier，或沿 A2 已存在的 acyclic grounded-parent graph 向上泛化；
2. 每一步必须严格减少 semantic specificity，不得增加新的 Fact、Relation 或 surface permission；
3. 保存 `candidate_projection_ref / candidate_projection_fingerprint / rewrite_parent_claim_ref / rewrite_depth / semantic_fingerprint`；
4. 同一 fingerprint 不得再次进入当前 chain；
5. B2 不创建游离 Claim；若 replacement 不在当前 projection，必须生成新的不可变 B0 projection revision 后重跑；
6. 触及 versioned hard attempt budget、parent graph 耗尽或无法继续严格降级时，进入 `CLAIM_SEMANTIC_BLOCKED`；
7. B2 不通过递归 Writer调用尝试无限润色。

#### `CLAIM_SEMANTIC_BLOCKED`（简称 `SEMANTIC_BLOCKED`）

Claim 的语义没有合法支持，并且没有安全 replacement。

典型原因包括：

- Evidence 不足；
- assertion ceiling 被突破；
- relation/quantifier 无支持；
- Evidence 冲突仍未解决；
- 用户内心状态被擅自推断；
- 把 Tone Span 当作事实 Claim；
- negative/absence Claim 缺少 closed-world basis。

`SEMANTIC_BLOCKED` Claim 不进入 surface gate 或 Writer，不用模糊词掩盖，也不因目标数量不足而重新放行。

#### `CLAIM_SEMANTIC_CONTRACT_INVALID`（简称 `SEMANTIC_CONTRACT_INVALID`）

输入或引用本身不满足工程合同，系统无法可靠完成判定。

典型原因包括：

- Fact/Evidence ref 缺失或悬空；
- policy/signal version 不匹配；
- active projection fingerprint 过期；
- source provenance 丢失；
- schema 必填字段损坏。

它不是“素材普通”或“证据不足”，而是工程异常。受影响 Memory 暂不发布并进入可观测、可重试的错误路径；禁止把它自动降级成泛化文案。

### 14.4 为什么终态中没有 `PENDING`

`CANDIDATE` 可以作为本次计算中的短暂状态，但不能成为一个交付给 Writer 的终态。

1. A3 为 `FACTS_UNRESOLVED` 时，不启动该 Memory 的 Claim Ledger；
2. Claim 所需 Evidence 在本次 Revision 内用尽仍无法判断时，进入 `CLAIM_SEMANTIC_BLOCKED`；
3. 工程依赖不完整时进入 `CLAIM_SEMANTIC_CONTRACT_INVALID`；
4. 不让 Writer 等待未知证据，也不在后续 Revision 中静默复活旧 Claim；
5. 新素材或新 Revision 到来后，可以基于新事实重新生成新的 Ledger decision。

这与前序 Window `defer` 的处理不同：S11 已位于发布前写作阶段，不能把不确定 Claim 留在用户文案管线里无限等待。

### 14.5 判定检查矩阵

每个 Claim 依次保留以下检查结果，而不是只保存一个总分：

| 检查层 | 检查项 | 通过条件 | 失败后的默认方向 |
| --- | --- | --- | --- |
| Semantic | Fact identity | 有 canonical Fact/grounded parent | Rewrite、semantic block 或 contract invalid |
| Semantic | Evidence support | 主体、谓词、对象分别有合法依赖 | Rewrite 或 semantic block |
| Semantic | Assertion ceiling | 文案具体度不超过上限 | Rewrite |
| Semantic | Relation support | 顺序、空间、因果、持续等独立成立 | Rewrite 或 semantic block |
| Semantic | Quantifier support | 次数、范围、完整性、比较成立 | Rewrite |
| Semantic | Negative assertion | 否定/缺失 Claim 有 closed-world basis | Semantic block |
| Semantic | Conflict check | 无未解决的互斥 Evidence | Rewrite 或 semantic block |
| Surface | Surface permission | Fact 可用于目标 surface/role | Surface block/retarget plan |
| Surface | Media compatibility | 与 active S10 projection 的角色一致 | Rebuild 或 surface block |
| Surface | Reservation | 未侵占 selected Aha/Chapter reserved core | Surface block |
| Both | Freshness | refs/version/fingerprint 属于当前 Revision | Layer-specific contract invalid |

不能把这些检查压成一个模糊 confidence score，因为相同总分可能分别代表“轻微具体度过高”和“完全违反 Aha reservation”，处理方式不同。

### 14.6 Evidence 聚合与冲突

1. 多条 Evidence 可以增强可追溯性，但不能把 assertion ceiling 抬高到源 Fact 允许范围之外；
2. 同一帧、同一 observation 或同一 derived parent 的重复副本不算独立投票；
3. 多个弱 Evidence 不能仅靠数量把 unsupported Claim 变成事实；
4. derived Evidence 的依赖失效时，依赖它的 Claim 随之重新判定；
5. 冲突不按“票数多数”让 Writer自行决定；使用上游已冻结的 provenance/validation 结果；
6. 若 exact Claim 冲突，但 B0 当前 projection 已包含不受冲突影响的 grounded-parent replacement ref，可以选择该 ref；不存在时不得由 B2 临时发明；
7. 若连安全 parent 也受冲突影响，Claim 进入 `CLAIM_SEMANTIC_BLOCKED`；
8. B2 不重新定义 User-confirmed、metadata、observed 与 derived source 的真值优先级，只消费上游已经验证的结果。

例：视觉像“周庄”，但 exact location metadata 未确认：

- “在周庄散步”不能通过；
- 若已有 grounded parent Fact `traditional-town walk`，可改为“在古镇街巷间散步”；
- 如果连“古镇”也只是模型猜测，则不能通过反复出现的相似建筑强行升级。

### 14.7 Surface-specific Decision

只有 `CLAIM_SEMANTIC_SUPPORTED` Claim 才进入 surface gate。Ledger 必须按 surface 与 narrative role 分别判定：

~~~text
TITLE
STORY_CORE
STORY_SUPPORT
AHA_MOMENT_LINE
TIME_LABEL
CANONICAL_TAG
ATMOSPHERE
~~~

其中 `TITLE / TIME_LABEL / CANONICAL_TAG` 通过 implicit normalized assertion 接入 `ClaimSurfaceDecision`；`STORY_CORE / STORY_SUPPORT / AHA_MOMENT_LINE` 通过 Atomic Claims 接入；`ATMOSPHERE` 通过独立 `TonePermissionDecision` 接入。Ledger 审计这些 surface 的事实含义，但不把非事实 Tone 当作 Claim。

Surface 状态只有：

- `SURFACE_SUPPORTED`：surface permission、active-media compatibility、适用时的 narrative role 与 reservation 全部通过；
- `SURFACE_BLOCKED`：语义可成立，但 Fact 为 `CONSTRAINT_ONLY/FORBIDDEN`、surface 不允许、媒体不相容、role 不合法或 reservation 冲突；
- `SURFACE_CONTRACT_INVALID`：surface assertion、projection、role、reservation 或版本引用损坏。

同一 Atomic Claim 可以同时拥有 `STORY_SUPPORT=SURFACE_SUPPORTED` 与 `TITLE=SURFACE_BLOCKED`；不存在覆盖所有 surfaces 的单一 claim-level permission 状态。

例：

- “木雕细节”可作为 Story Support；若它不能代表整个 Chapter identity，则不可成为 Title；
- “晚光”可作为 Atmosphere basis；它不能代替 Story Core；
- exact time metadata 可以进入 Time Label，但未必需要写进 Story；
- selected Aha peak 可用于 `AHA_MOMENT_LINE + AHA_PEAK_CORE`，但对 V1 generated Aha Title 被禁止，并在 Chapter Story Core 被 reservation 阻止；
- 用户确认的地点名在 provenance 合法时可进入 Story/Tag，即使 final media 没有直接显示文字；但仍需符合 active-media narrative alignment。

**D5b1 contract-alignment amendment：** 上一条中的`Tag`表示 B2 对 D5 index umbrella 的`SURFACE_SUPPORTED`资格，不等于 exact 地点必须物化为 Canonical Concept。D5 对 supported assertion 确定性路由：class-level reusable concept →`CanonicalTagAssignment`；exact stable entity → typed`EntityIndexLink`。B2 的 permission、active-media compatibility 与 provenance 结论保持不变。

Memory type 采用不同核心门：

- Chapter：至少一个 `CHAPTER_STORY_CORE`，其他 Claim 可作为 progression/support/atmosphere basis；
- Aha：所有 core Claims 必须在 `AHA_MOMENT_LINE` surface 指向同一个 `core_peak_event_ref`；B2 最多保留 0–2 组合法邻近 support，并可保留来自 Aha 自身 Facts、与同一 peak scope 相容的 minimal local context candidates 与 evidence-bearing observable emphasis candidates；C3b1 用户可见计划最多选择 1 组 adjacent support，C3b2 最多选择 1 组必要 local context，C3b3 最多选择 1 项 observable qualifier，三者都不能升级为第二个 core event；
- B2 不把 Aha 扩成“准备—过程—结果”的小 Chapter；
- Chapter 的一至两句规则不自动套给 Aha；Aha 单一 `MOMENT_LINE` 形态由 C3b1 确认，具体字符长度与异常降级形式留到 S11-D4。

每个 Aha `AHA_PEAK_CORE/AHA_ADJACENT_SUPPORT/AHA_LOCAL_CONTEXT_CANDIDATE/AHA_OBSERVABLE_EMPHASIS_CANDIDATE` surface decision 必须使用 `target_surface=AHA_MOMENT_LINE` 并保存同一个非空 `core_peak_event_ref`；`AHA_ADJACENT_SUPPORT` 还必须保存能唯一解析到 A3 `adjacent_support_groups[0..2]` 中既有对象的 `adjacent_support_group_ref`，B2 不得拆组/并组/重建 group identity；`AHA_LOCAL_CONTEXT_CANDIDATE` 只能来自当前 AhaFacts 的 local scene/activity phase、trusted location 或 user-confirmed local Fact，不能引用 parent Chapter Story 当作 Evidence，也不能携带尚未由 C3b2 生成的 group ref。`AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 必须来自当前 AhaFacts 的既有 observable Fact，attachment relation 必须证明它只限定同一 scope 的 target Claim，而不新增 peak/support/context 事件。缺字段、非法 attachment 或 role laundering 不是普通 Block，而是 `SURFACE_CONTRACT_INVALID`。

### 14.8 Active Projection 与 Revision 行为

1. Ledger decision 永远绑定 active S10 projection fingerprint；
2. 当 S10/S13 按 V1.21 产生合法、不可变的 Route activation、D1-approved single-loss survivor 或 Hero Alternate delta 时，旧 decision 不可直接复用；
3. 如果 Fact 仍 grounded 但不再直接可见，可按 A1 visibility/use class 重新判断是 Story Support、Constraint 还是 Block；
4. 如果 Story Core 与实际媒体组合失去一致性，必须回到 Content Plan 重建，不能只改几个字继续发布；
5. 新 Revision 生成新的不可变 Ledger；旧 Ledger 保留为 audit，不被静默覆盖；
6. 只有 claim semantics、source/dependencies、surface、reservation 与 active projection 均未改变时，才可复用先前 decision。

S11 不删除、替换或重排媒体成员；正文 chronology 继续由 V1.21 冻结合同控制。

### 14.9 Claim-set eligibility 与 S11 权限终点

Claim Ledger 完成后，为每个 selected Memory 计算预写作资格，而不是发布资格：

~~~text
ClaimSetEligibility
  CLAIM_SET_ELIGIBLE
  CLAIM_SET_REBUILD_REQUIRED
  CLAIM_SET_BLOCKED
  CLAIM_SET_CONTRACT_INVALID
~~~

- `CLAIM_SET_ELIGIBLE`：Chapter 至少有一个 `SURFACE_SUPPORTED + CHAPTER_STORY_CORE`，或 Aha 至少有一个 `target_surface=AHA_MOMENT_LINE + SURFACE_SUPPORTED + AHA_PEAK_CORE` 且指向同一 `core_peak_event_ref`；可以进入 C；
- `CLAIM_SET_REBUILD_REQUIRED`：原先计划的核心失效，但同一 selected Memory 仍有其他合法核心可尝试；
- `CLAIM_SET_BLOCKED`：同一 selected Memory 已无合法核心；S11 阻止当前 Revision 继续，不删除该成员、不发布剩余子集、不寻找补位；
- `CLAIM_SET_CONTRACT_INVALID`：工程输入损坏；不发布、不降级，进入重试与诊断。

`ClaimSetEligibility` 不是 `PUBLISH_READY`。D/E 尚未完成，最终发布权仍属于 S12。S11 failure 只形成带原因的阻断结果；V1 按用户确认的方案 A 保持 S09 membership 与原子发布边界。

### 14.10 输出结构

~~~text
ClaimLedger
  selected_memory_ref
  stable_memory_id
  revision_ref
  active_s10_projection_ref
  active_projection_fingerprint
  candidate_projection_ref
  candidate_projection_fingerprint
  ledger_entries[]
    atomic_claim_ref
    claim_semantic_fingerprint
    source_fact_refs[]
    evidence_dependency_refs[]
    individual_fact_and_relation_check
    negative_assertion_check
    conflict_and_freshness_check
    semantic_decision_state
    semantic_reason_codes[]
    rewrite_parent_claim_ref
    rewrite_depth
    replacement_claim_ref
    replacement_basis_refs[]
    replacement_candidate_projection_ref
    replacement_candidate_projection_fingerprint
    claim_audit_ref
  surface_decisions[]
    atomic_claim_ref
    candidate_projection_ref
    target_surface
    implicit_assertion_ref?
    memory_type
    narrative_claim_role?
    core_peak_event_ref?
    adjacent_support_group_ref?
    aha_role_partition_check?
    surface_permission_check
    media_compatibility_check
    reservation_check
    surface_decision_state
    surface_reason_codes[]
    surface_audit_ref
  tone_permission_decisions[]
    tone_candidate_ref
    candidate_projection_ref
    basis_kind
    basis_refs[]
    target_memory_ref
    decision_state
    reason_codes[]
  supported_claim_surface_pairs[]
  semantic_rewrite_required_claim_refs[]
  semantic_blocked_claim_refs[]
  semantic_contract_invalid_claim_refs[]
  surface_blocked_pairs[]
  surface_contract_invalid_pairs[]
  claim_set_eligibility
  policy_and_signal_versions
  ledger_fingerprint
  construction_audit
~~~

`implicit_assertion_ref` 对 `TITLE/TIME_LABEL/CANONICAL_TAG` 必填；对 `STORY_CORE/STORY_SUPPORT/AHA_MOMENT_LINE` 必须为空，因为这些 narrative surfaces 已由 `atomic_claim_ref + narrative_claim_role` 直接表达。Chapter narrative surface 必填 `CHAPTER_STORY_CORE/CHAPTER_STORY_SUPPORT`，且 Aha refs/check 均为空；`AHA_MOMENT_LINE` 必填 `AHA_PEAK_CORE/AHA_ADJACENT_SUPPORT/AHA_LOCAL_CONTEXT_CANDIDATE/AHA_OBSERVABLE_EMPHASIS_CANDIDATE + core_peak_event_ref` 中的合法 role 与 `aha_role_partition_check`。其中只有 adjacent support 填 `adjacent_support_group_ref`；local context singleton group 由 C3b2 后建，B2 不保存 group ref；observable emphasis 只填 attachment 三字段，B2 不预先决定它是否进入用户文字。非 narrative surfaces 的全部 narrative fields 均为空。`ATMOSPHERE` 不进入该数组的事实性 implicit assertion，而使用独立 tone decision；该 tone decision 在 V1 generated Aha 上必须不适用。

推荐的 `reason_codes` 至少包括：

~~~text
NO_GROUNDED_FACT
EVIDENCE_INSUFFICIENT
ASSERTION_CEILING_EXCEEDED
RELATION_UNSUPPORTED
QUANTIFIER_UNSUPPORTED
CLOSED_WORLD_EVIDENCE_MISSING
SURFACE_NOT_ALLOWED
MEDIA_INCOMPATIBLE
AHA_RESERVED
CHAPTER_RESERVED
AHA_PEAK_REF_MISSING
AHA_SUPPORT_GROUP_INVALID
AHA_LOCAL_CONTEXT_CANDIDATE_INVALID
AHA_OBSERVABLE_EMPHASIS_CANDIDATE_INVALID
AHA_EMPHASIS_ATTACHMENT_INVALID
UNEXPECTED_LOCAL_CONTEXT_GROUP_REF
AHA_ROLE_LAUNDERING
AHA_MOMENT_LINE_SURFACE_REQUIRED
AHA_TITLE_FORBIDDEN_V1
AHA_NONFACTUAL_TONE_FORBIDDEN_V1
SOURCE_CONFLICT
USER_STATE_INFERENCE
TONE_USED_AS_FACT
TONE_PERMISSION_MISSING
TONE_ADDS_FACT
TONE_USER_STATE_INFERENCE
FORBIDDEN_FACT
STALE_PROJECTION
MISSING_DEPENDENCY
PROVENANCE_MISSING
SCHEMA_INVALID
REWRITE_BUDGET_EXHAUSTED
~~~

`UNEXPECTED_LOCAL_CONTEXT_GROUP_REF` 专门表示 B2 输入/decision 中出现了本应由后置 C3b2 才创建的 context group ref；candidate 自身的 scope/source/role 不合法则使用 `AHA_LOCAL_CONTEXT_CANDIDATE_INVALID`。两者不能混成同一个旧 group reason。

### 14.11 案例交叉检查

#### 案例 A｜古镇 exact location 改写

Candidate：

> 下午在周庄的石板路上慢慢散步。

如果下午时间与石板路成立，但“周庄”未确认：exact Claim 为 `CLAIM_SEMANTIC_REWRITE_REQUIRED`。只有 B0 projection 中存在 grounded `traditional-town/old-street` parent replacement 时，才可改成：

> 下午沿着古镇的石板路散步。

“慢慢”会断言可观察的移动速度，不能靠氛围 permission 通过：有足够连续时序 Evidence 时，它最多成为 `AHA_OBSERVABLE_EMPHASIS_CANDIDATE`；没有时必须删除。即使候选合法，是否值得进入 Aha 仍由 C3b3 决定。

#### 案例 B｜顺序词局部失效

Candidate：

> 看过木雕后，接着走到了河岸。

木雕、河岸、行走都成立，但准确先后无 Evidence：relation Claim 为 `CLAIM_SEMANTIC_REWRITE_REQUIRED`。可以保留两个事实并重新组合，不能保留“后/接着”。

#### 案例 C｜生日 Aha reservation

“猫跳上蛋糕”的 Atomic Claim 为 `CLAIM_SEMANTIC_SUPPORTED`。它对于 Aha 是 `target_surface=AHA_MOMENT_LINE + SURFACE_SUPPORTED + AHA_PEAK_CORE`；对于 generated Aha Title 是 `SURFACE_BLOCKED + AHA_TITLE_FORBIDDEN_V1`；对于生日 Chapter Story Core 也是 `SURFACE_BLOCKED`，并记录 `reason_code=AHA_RESERVED`。事实为真不等于所有 surface 都可使用。

#### 案例 D｜会议结果被禁止

Candidate：

> 白板讨论带来了重要进展。

白板与讨论成立，但“带来”因果和“重要进展”结果没有 outcome Evidence。若剩余 Fact 足够，可重建成“上午围绕白板展开了一段讨论”；若连“展开讨论”也不可靠，则 Block，不能用“充实的上午”补位。

#### 案例 E｜第三个 Chapter 无核心文案

当天原本选出三个 Chapter。第三个候选只有模糊环境素材，全部核心候选 Claim 均被 Block：

1. 先检查同一 Memory 是否有其他合法 `STORY_CORE`；
2. 没有则输出 `CLAIM_SET_BLOCKED`；
3. S11 不撤出第三个候选、不发布剩余两个的临时子集，也不寻找第四名补位；
4. 当前 Revision 进入下游 HOLD/BLOCK；有仍合法 prior 时继续显示 prior，无 prior 时不发布该 Revision；
5. 不显示残缺 Chapter，不生成万能 Story；
6. 若这种情况频繁发生，应修正上游 Chapter core eligibility，不在 S11 增加 late re-selection。

#### 案例 F｜工程合同损坏

Fact 看似完整，但 Claim 指向旧的 active projection fingerprint。该项进入对应层的 `*_CONTRACT_INVALID`，触发诊断/重试；不能把它解释为“素材不够好”，也不能绕过检查直接让 Writer写。

### 14.12 Invariants、成本与边界

1. 只有 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED` 的 pair 可以进入 Content Plan；
2. `CLAIM_SEMANTIC_REWRITE_REQUIRED` 的原 Claim 永不直接渲染，replacement 必须来自绑定 projection 的既有 closure、重新验真，且改写链严格单调、有界、无重复；
3. `CLAIM_SEMANTIC_BLOCKED / SURFACE_BLOCKED` 不因数量不足、文案更好听或 Evidence 重复而放行；
4. semantic/surface/tone 各自的 `*_CONTRACT_INVALID` 与普通内容不足严格分离；
5. 每个 decision 绑定 Claim、surface、Revision 与 active projection；
6. 多 Evidence 不提升 source assertion ceiling，冲突不按票数处理；
7. Tone/万能句不能满足 Story Core；
8. Chapter 必须有 `CHAPTER_STORY_CORE`；Aha 必须在 `AHA_MOMENT_LINE` 上有同一 `core_peak_event_ref` 下的 `AHA_PEAK_CORE`；
9. Claim-set failure 不授权 S11 改变 S09 membership 或触发补位；
10. 3～4 Chapter / 2～3 Aha 只继承丰富日软偏好，最终质量不可为数量让步；
11. Negative/Absence Claim 必须通过 closed-world gate；
12. Ledger 不调用 VLM、不读取 Raw Asset 像素，只审计 A3 canonical refs 与已计算 Evidence；
13. `AHA_PEAK_CORE/AHA_ADJACENT_SUPPORT/AHA_LOCAL_CONTEXT_CANDIDATE/AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 只允许进入 `AHA_MOMENT_LINE`；peak/support/context/qualifier role 不得互换，同一或语义等价 proposition 不得跨 role 重复以绕过预算，V1 generated Aha Title 不能成为旁路；
14. generated Aha 不消费 `NON_FACTUAL_TONE_ONLY`；observable qualifier 必须有 Atomic Claim、合法 attachment 与 Evidence，且不能单独满足 Aha peak core；
15. Ledger 判定可缓存，但任一语义、依赖、surface、reservation 或 projection 变化都会使缓存失效。

## 15. 下一检查点

下一步进入 S11-B3：检查多个 individually supported Claims 组合后是否仍然成立。重点包括跨 Claim 矛盾、重复表达、错误指代、时间/空间跳跃、把先后写成因果、以及多个真实事实拼接后形成一个整体上不真实的故事。

## 16. S11-B3｜Cross-Claim Composition Truth

**状态：CONFIRMED**

### 16.1 产品体验合同｜非相邻 Facts 可以概括，但不能伪装成连续过程

V1 锁定：

> 同一 Chapter 内的非相邻 Claims 可以按共同 Memory identity 进行概括性组合；只有具备独立关系证据时，才能写成连续、顺序、转折或因果过程。

具体含义：

1. 时间相隔较远本身不阻止两个事实共同代表一个长 Chapter；
2. 两个事实必须已经由上游归入同一个 selected Memory，S11 不负责重新合并被拆开的 Moments；
3. `same Memory membership` 只支持概括性共现，不自动支持相邻、持续、路线、先后或因果；
4. 长 Chapter 可以用多个时段的不同关键内容表达其主题，不必退化成单个画面的说明；
5. 文案不得让用户误以为设备连续记录了中间全部过程；
6. 已被 selected Aha 保留的插入事件不能重新成为 Chapter Story Core；
7. 最终叙述默认尊重已知时间顺序，与 S10 final media chronology 一致，不为戏剧性任意倒序。

### 16.2 为什么每个 Claim 都是真的，整句话仍可能是假的

多个 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED` Claims 放在一起，会产生单项 Claim 之外的新含义：

- **邻接含义**：用户可能理解为两个事件紧接发生；
- **过程含义**：用户可能理解为中间没有中断；
- **共享主体**：用户可能理解为两个画面中的人/建筑是同一个对象；
- **共享地点**：用户可能理解为两个事件发生在同一空间；
- **因果含义**：句法可能让先发生的事件看起来导致后一个事件；
- **完整范围**：列出若干素材可能被理解为覆盖了整段过程；
- **价值结论**：几个普通事实可能被包装成“完成、成功、难忘”；
- **指代含义**：第二句中的“它、这里、随后”可能错误指向前一句。

因此，B2 的单 Claim 通过是必要条件，但不是 Claim 组合通过的充分条件。

例：

- “上午看到了木雕”成立；
- “临近中午到了河岸”成立；
- 直接组合成“看完木雕便走到河岸”仍可能不成立，因为“便”增加了紧邻关系。

### 16.3 Composition Mode 必须显式声明

C 先用 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED` pairs 形成 provisional Claim group；该 group 在进入 D 写作前，必须由 B3 声明并验证一种主要组合模式：

#### `ATOMIC_SINGLETON`

通用单项模式：恰好一个 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED` pair，不含 relation edge。仍检查 target surface、narrative role（如适用）、reservation、media alignment、Revision 与 active projection。可用于单 Claim Chapter Story 或单个 Title/Time Label/Tag assertion；Aha peak 必须在 `target_surface=AHA_MOMENT_LINE` 下继续使用专门的 `AHA_PEAK_WITH_CONTEXT`，不能借 singleton 或 generated Title 绕过 single-peak gate。

#### `AHA_PEAK_WITH_CONTEXT`

仅供 `AHA_MOMENT_LINE`：一个 `core_peak_event_ref` 下的 peak core，加当前 Aha surface policy 允许的 0–1 组 necessary minimal local context、0–1 组 visible adjacent support，以及 0–1 个附着于已选 base Claim 的 observable emphasis qualifier。A3/B2 可提供 0–2 组合法 upstream support；C3b1 的 V1 用户可见预算最多选择 1 组。C3b2 可从当前 AhaFacts/Claim Ledger 的合法 `AHA_LOCAL_CONTEXT_CANDIDATE` Claims 中最多选择 1 项，并按 `(surface_policy_ref, revision_ref, active_projection_fingerprint, core_peak_event_ref, atomic_claim_ref)` 确定性建立只含该 Claim 的 immutable singleton group；C3b3 再从合法 `AHA_OBSERVABLE_EMPHASIS_CANDIDATE` Claims 中选择 0–1 项。B3 分别验证三类 candidate/selected subset、各自 count、同一 Revision/active projection/core peak、对应 narrative role、role partition/laundering，以及 context/support/qualifier 不重复。Context 只解决独立理解，support 只表达紧邻反应/结果，qualifier 只限定已选事件属性；三者都不得取得第二 core、扩成准备—过程—结果或借 Chapter-wide narrative 才能理解。

#### `SUMMARY_MEMBERSHIP`

表示多个事实共同属于同一 selected Memory，但不声明准确相邻、连续或因果。

允许非相邻 Facts；要求共同 Memory identity 和 surface permission。适合长 Chapter 的一至两句概括。

#### `TEMPORAL_SEQUENCE`

表示 Claims 按已知顺序发生。每条相邻 edge 都需要 temporal Evidence；时间顺序成立仍不等于全程连续。

#### `INTERRUPTION_AND_RESUMPTION`

表示主题 A 被短暂事件 B 打断后又回到 A。需要上游 continuity/boundary decision 和 resumption Evidence。若 B 已成为独立 Aha，Chapter 可以保留 A 前后内容，但不能把 B 写成 Chapter peak。

#### `CONTRAST`

表示两个事实在明确维度上形成差异，例如室外传统街巷与室内现代奶茶店。两侧事实、比较维度和归属必须成立；不能只因视觉风格不同就自动制造故事转折。

#### `ACTION_RESULT`

表示动作与结果属于同一实体/过程，例如拉坯到成形。需要 entity continuity、动作和结果依赖，不能把两个相似物体拼成前后状态。

#### `CAUSE_RESULT`

表示一个事件导致另一个事件。需要明确 causal Evidence；单纯时间先后永不自动升级为因果。

#### `SPATIAL_ROUTE`

表示从一个地点移动到另一个地点。需要位置、移动和路线/到达关系；两个地点分别出现不代表路径被记录。

一组 Claims 可以包含辅助 relation，但每条会改变用户理解的 relation edge 都必须单独验证。

### 16.4 Summary 与 Process 的语言边界

#### 概括性表达

> 上午走在古镇街巷里，眼前有牌坊、木雕和古建筑屋檐，也有临水的河岸。

这句话主要使用 `SUMMARY_MEMBERSHIP`：说明这些事实共同属于该 Chapter，不声明素材连续。

即使是概括，也需要检查：

- 它们确属同一 selected Memory；
- 没有跨越被上游判定为独立 Chapter 的边界；
- 没有使用 selected Aha reserved peak；
- “多个、不同、几处”等量词有 distinct entity Evidence；
- 用户不会被误导为同一建筑或同一地点。

#### 过程性表达

> 从牌坊进入古街后，木雕、古建筑屋檐和河岸依次出现。

除各个 object Claims 外，还需要进入、先后和 progression relations。若任一 edge 不成立，必须改回 summary、拆句或删除关系词。

#### 连续性过度表达

> 一路从牌坊逛过所有古建筑，最后走到河岸。

同时声明连续性、完整范围、路线和终点；仅凭几个每两分钟采样的离散素材不能成立。

### 16.5 Composability Tests

Claim group 依次通过：

1. **Memory identity**：所有 Claims 是否属于同一 selected Memory/revision；
2. **Individual eligibility**：每个 Claim 是否为 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED`；
3. **Relation edge**：显式和隐式关系是否都有独立 Evidence；
4. **Entity resolution**：同名/相似对象是否被错误当成同一实体，或同一实体被重复计数；
5. **Temporal coherence**：时间是否冲突、倒置或被暗示为连续；
6. **Spatial coherence**：地点与路线关系是否成立；
7. **Polarity/attribute coherence**：发生/未发生、拥挤/安静等状态是否被无时间条件地并置；
8. **Quantifier coherence**：多个、全部、再次、不同等是否有集合与去重依据；
9. **Reservation**：是否侵占 selected Aha/Chapter reserved core；
10. **Referent clarity**：代词、省略主语和“这里/随后”等是否只有一个合法指向；
11. **Media alignment**：整个组合是否仍与 active final media core 一致；
12. **Emergent meaning**：组合后是否出现任何单 Claim 中不存在的新结论。
13. **Memory-type/surface-policy gate**：Chapter group 是否围绕同一 Chapter core；Aha group 是否以 `AHA_MOMENT_LINE` 为 target、core Claims 是否全部指向同一个 `core_peak_event_ref`、upstream available support 是否不超过 A3 的 2 组、visible selected support 是否不超过 active policy 的 V1 1 组、selected minimal local context 是否不超过 C3b2 的 1 组且每组只有一个 atomic Claim、selected observable emphasis 是否不超过 C3b3 的 1 项、三类事实 selected 是否分别是同 Revision/projection/core peak 下的合法候选子集、role 是否匹配、是否互不重复，且均未升级为第二事件；28.12 light-affect permission 另检 0–1 count、exact target、action compatibility、scope/risk 与不进入事实图。
14. **Aha role-partition gate**：peak predicate/core arguments/visible change、可分离 reaction/result、local phase/place/scene、附着于既有 Claim 的可观察限定是否分别保持 `AHA_PEAK_CORE / AHA_ADJACENT_SUPPORT / AHA_LOCAL_CONTEXT_CANDIDATE / AHA_OBSERVABLE_EMPHASIS_CANDIDATE`；同一或语义等价 proposition 是否通过换 role、parent/subclaim 改写或重复 group 绕过预算；qualifier 是否借强调名义新增用户心理、价值判断或第二事件。

### 16.6 Composition Decision

#### `COMPOSITION_COMPOSABLE`（简称 `COMPOSABLE`）

所有 Claims 和 relation edges 均合法，组合没有制造额外不真实含义；C 可确认该 group 并进入 D。

#### `COMPOSITION_RECOMPOSE_REQUIRED`（简称 `RECOMPOSE_REQUIRED`）

Claims 各自可以使用，但当前组合方式不合法。可采取：

- 删除无支持的 connector；
- 从 process 改为 summary；
- 按真实时间重新排序；
- 拆成两句；
- 消除错误指代；
- 删除重复或低价值 Claim；
- 将被 reservation 阻止的 Claim 移出该 surface。

重组结果必须重新通过整个 group check。

重组是有界、单调的：

1. 只能删除 Claim/relation、从 process 降为 summary、拆小 group、按已知 chronology 重排或修正 referent plan；
2. 不得加入 B2 未批准的新 Claim；
3. 每次必须严格减少不受支持的语义或 group complexity；
4. 保存 `recompose_parent_group_ref / recompose_depth / group_semantic_fingerprint`，禁止重复 fingerprint；
5. 触及 versioned hard attempt budget、候选子图耗尽或无法继续单调简化时，进入 `COMPOSITION_GROUP_BLOCKED`；
6. 不形成 C↔B3 的无限 Writer循环。

#### `COMPOSITION_GROUP_BLOCKED`（简称 `GROUP_BLOCKED`）

这些 Claims 不能在当前 Memory/surface/模式下共同出现。它不必自动 Block 每个 individual Claim；它们可以分别进入其他合法 group，或只保留更能代表 Memory core 的一个。

#### `COMPOSITION_CONTRACT_INVALID`（简称 `CONTRACT_INVALID`）

Claim refs、relation refs、entity mapping、revision 或 projection 不一致，无法做可靠组合判断。进入工程诊断路径，不交给 Writer猜测。

### 16.7 Entity、相似素材与量词

视觉/语义相似不等于同一个实体，也不等于不同实体：

1. 两个时间较远的古建筑外观，如果上游已有 distinct entity/appearance Evidence，可共同用于长 Chapter；
2. 它们不因“都是古建筑”而被自动去重；
3. 若只知道是相似建筑画面、无法判断同一座还是不同座，可以保留安全的上位事实，但不能写“多座、不同建筑、又一座”；
4. 同一建筑的相近角度不能仅靠素材数量升级成“多座建筑”；
5. 外观与独立木雕细节可按 `DUAL_ASPECT` 作为不同信息面，但不能假设木雕必属于外观中的同一建筑，除非 entity relation 成立；
6. B3 只消费上游 entity/distinctness facts，不重新打开 Raw Assets 做识别。

例：

- 09:20 建筑 A 外观；
- 11:10 建筑 B 外观；
- 上游确认 A/B 为不同实体。

可以概括“上午看到了几处不同的古建筑外观”。若 A/B identity 未解决，只能使用不带数量结论的“古建筑外观成为这段漫步的重要内容”。

### 16.8 Interruption、A｜B｜C 与 Aha Reservation

时间线：

~~~text
A  09:00–10:40  古镇街巷/古建筑
B  10:45–11:00  现代奶茶店
C  11:05–12:00  回到古镇街巷/河岸
~~~

S11 不自行决定 A/C 是否合并；它继承上游 membership 与 boundary decision。

若上游认定 A/C 属于同一 Chapter：

1. 可以用 `SUMMARY_MEMBERSHIP` 概括 A/C；
2. 不得写“全程、一路、一直”，因为 B 构成实际中断；
3. 只有 resumption Evidence 完整时，才可写“短暂停留后又回到古街”；
4. 如果 B 是 selected Aha，Chapter 不写 B 的 peak，只保留必要边界约束；
5. 如果 B 不是 Aha、只是 Chapter 内次要 Beat，可在不改变 Chapter identity 时作为 support/contrast；
6. 如果 B 已被上游判断为独立 Chapter，S11 不能为了句子顺滑把它重新并回 A/C。

### 16.9 Planned cross-sentence dependency 与 E-stage 实文验证

Chapter 的一至两句 Story 需要按整体而不是逐句校验。C/B3 先检查 planned Claim order 与 planned referents；D 写出真实语言后，E 必须重新检查实际 spans、代词、连接词和隐含顺序：

1. 第二句中的“它、这里、这时、随后”必须有唯一 referent；
2. 两句各自无连接词，也可能因排列顺序让用户理解为先后；
3. 已知时间 Claims 默认按时间排列；
4. 若刻意使用非时间顺序，必须采用不会暗示事件顺序的 summary grammar；
5. 第二句不能把第一句的 Tone Span 当成事实主体；
6. 同一事实换一种说法重复出现，不会因重复而更重要；
7. Title、Story 和 Tag 的重复/信息预算由 S11-C 处理，但 B3 标记 semantic duplicate refs；
8. 实际措辞出现任何不在 plan 中的 Claim/relation 时，E 不得直接接受，必须进入有界 rewrite 或 Block；
9. 本节的一至两句与跨句规则只适用于 Chapter；Aha 的单一 `MOMENT_LINE` surface 与单峰预算由 C3b1 定义，具体字符数、标点与异常降级形式仍留给 S11-D4。

反例：

> 上午看到了河岸。随后，木雕细节让这里更有历史感。

“随后”要求时间顺序；“这里”可能错误指向河岸；“更有历史感”还引入比较和价值判断。每个单独素材真实，并不使这两句组合合法。若这些词只在 D 的实际输出中出现，即使 C 的语义 plan 原本合法，E 仍必须拦截。

### 16.10 输出结构

~~~text
ClaimCompositionLedger
  selected_memory_ref
  stable_memory_id
  revision_ref
  active_projection_fingerprint
  composition_groups[]
    group_ref
    memory_type
    target_surface
    composition_mode
    narrative_claim_roles[]
    aha_contract?
      surface_policy_ref
      core_peak_event_ref
      provisional_aha_surface_plan_ref
      provisional_aha_surface_plan_fingerprint
      provisional_plan_revision_projection_policy_check
      provisional_composition_group_ref
      provisional_composition_group_fingerprint
      enclosing_group_ref_exact_match_check
      ordered_claims_relations_fingerprint_match_check
      upstream_adjacent_support_group_refs[]
      selected_visible_adjacent_support_group_refs[]
      omitted_adjacent_support_group_refs[]
      support_omission_reason_codes[]
      available_minimal_local_context_group_refs[]
      selected_minimal_local_context_group_refs[0..1]
      omitted_minimal_local_context_group_refs[]
      local_context_omission_reason_codes[]
      standalone_context_decision_ref
      available_observable_emphasis_qualifier_refs[]
      selected_observable_emphasis_qualifier_refs[0..1]
      omitted_observable_emphasis_qualifier_refs[]
      observable_emphasis_omission_reason_codes[]
      observable_emphasis_decision_ref
      selected_light_affective_framing_permission_refs[0..1]
      omitted_light_affective_framing_permission_refs[]
      light_affective_framing_omission_reason_codes[]
      light_affective_framing_decision_ref
      light_affective_framing_policy_version
      support_selection_replay_check
      observable_emphasis_selection_replay_check
      light_affective_framing_selection_replay_check
      plan_decisions_selected_refs_match_check
      b3_entry_allowed_check
      peak_consistency_check
      upstream_support_count_check
      visible_selected_support_count_check
      visible_support_subset_check
      selected_local_context_count_check
      selected_local_context_atomicity_check
      selected_local_context_subset_check
      context_support_distinctness_check
      selected_observable_emphasis_count_check
      selected_observable_emphasis_subset_check
      emphasis_target_selected_claim_check
      emphasis_attachment_relation_check
      context_support_emphasis_distinctness_check
      selected_light_affective_framing_count_check
      light_affective_target_selected_event_entity_check
      light_affective_action_trigger_compatibility_check
      light_affective_scope_risk_exclusion_check
      light_affective_not_in_claim_relation_graph_check
      unplanned_nonfactual_tone_span_forbidden_check
      user_state_value_inference_exclusion_check
      no_second_event_via_emphasis_check
      aha_role_partition_check
      semantic_equivalent_role_laundering_check
    ordered_claim_refs[]
    relation_edges[]
      from_claim_ref
      to_claim_ref
      relation_type
      support_refs[]
      relation_decision  # RELATION_SUPPORTED | RELATION_BLOCKED | RELATION_CONTRACT_INVALID
    entity_coreference_map_ref
    planned_referent_map_ref
    temporal_coherence_check
    spatial_coherence_check
    polarity_attribute_check
    quantifier_distinctness_check
    reservation_check
    planned_referent_clarity_check
    planned_implicit_meaning_audit
    semantic_duplicate_refs[]
    composition_decision
    recompose_actions[]
    aha_recompose_owner?
      C3B2_BASE_SELECTION
      | C3B3_OBSERVABLE_EMPHASIS
      | C3B3_LIGHT_AFFECTIVE_FRAMING
    recompose_parent_group_ref
    recompose_depth
    group_semantic_fingerprint
    reason_codes[]
    audit_ref
  composable_group_refs[]
  recompose_required_group_refs[]
  blocked_group_refs[]
  contract_invalid_group_refs[]
  policy_and_signal_versions
  composition_fingerprint
~~~

对 Chapter group，`aha_contract` 必须 absent；对 Aha group，`target_surface=AHA_MOMENT_LINE` 且整个 `aha_contract` 必填，其中 exact provisional `AhaNarrativeSurfacePlan` ref/fingerprint、Revision/projection/policy check、plan 提名的 provisional composition group ref/fingerprint、enclosing `group_ref` exact match、ordered Claims/relation edges fingerprint match、policy/core peak、support/local-context/observable-emphasis 三套 count/subset/role checks、context atomicity、三类事实内容 distinctness、role-partition/laundering checks、support/emphasis selection replay、light-affect permission/target/action/risk checks、plan 与 C3b2/C3b3 decisions 的 exact match、`b3_entry_allowed=true`、`standalone_context_decision_ref`、`observable_emphasis_decision_ref` 与 `light_affective_framing_decision_ref` 均不可缺。

硬绑定必须满足：

~~~text
ClaimCompositionLedger.composition_groups[i].group_ref
  == aha_contract.provisional_composition_group_ref
  == deref(provisional_aha_surface_plan_ref).provisional_composition_group_ref

composition_groups[i].group_semantic_fingerprint
  == aha_contract.provisional_composition_group_fingerprint
  == deref(provisional_aha_surface_plan_ref).provisional_composition_group_fingerprint
~~~

fingerprint 必须覆盖 ordered Claim refs、全部 relation edges/support/qualifier attachment refs，以及与事实图分离的 light-affect permission class/target/policy ref，不能只比较 selected set。其 canonical fingerprint payload 明确排除 fingerprint 字段自身、`aha_contract` 内的 validation/back-reference fields 与后置 audit refs，避免自引用；plan 与 B3 对同一 canonical composition payload 独立计算后比较。任一 ref/fingerprint/ordered-claims/relation mismatch、plan/policy fingerprint 不匹配，selected support 不能解析为同 Revision/projection/core peak 下的 `SURFACE_SUPPORTED + AHA_ADJACENT_SUPPORT`，selected context 的 singleton Claim 不能解析为同 scope 下的 `SURFACE_SUPPORTED + AHA_LOCAL_CONTEXT_CANDIDATE`，selected qualifier 不能解析为 `SURFACE_SUPPORTED + AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 并附着于该 plan 已选 base Claim，plan selected refs 与 C3b2/C3b3 immutable decisions 不同，light-affect permission 未通过 28.12 的 decision/target/action/scope/risk gate，permission 被混入 Claim/relation graph，generated Aha 出现未计划的 non-factual Tone，或任何同义/parent-subclaim role laundering 成立时，均为 `COMPOSITION_CONTRACT_INVALID`，不能按零 support/context/emphasis/affect 默默通过。

composition group 三方绑定失败时至少记录 `PROVISIONAL_COMPOSITION_GROUP_MISMATCH`；它是 lineage/contract error，不进入普通 recompose。

B3 composition decision 必须显式引用它验证的 exact provisional plan；随后才创建一个新的 immutable `B3_VALIDATED` plan artifact，保存 `parent_provisional_plan_ref + b3_composition_decision_ref`。B3 decision 不引用后置 validated plan，避免 plan↔decision 生命周期循环。

`RECOMPOSE_REQUIRED` 必须填写唯一 `aha_recompose_owner` 并按失败所有者回路由：若失败涉及 peak/support/context 基础组合，标记 `C3B2_BASE_SELECTION`，返回 C3b2，完成新的 base decision 后再经过 C3b3；若失败只涉及 optional observable qualifier 或其与基础组合的交互，标记 `C3B3_OBSERVABLE_EMPHASIS`；若只涉及已许可 light affect 与当前 plan 的可安全组合问题，标记 `C3B3_LIGHT_AFFECTIVE_FRAMING`。后两者都保留 exact C3b2 decision并返回 C3b3 严格简化，分别省略 qualifier 或 affect permission。非 Aha group 的该字段必须为空；无法唯一定位所有者时按更上游的 `C3B2_BASE_SELECTION` 处理，不能让多个 stage 同时静默修改。合同引用、policy 或 lineage 损坏仍为 `COMPOSITION_CONTRACT_INVALID`，不能借 recompose 重建引用或直接按零 permission 吞掉。

### 16.11 案例交叉检查

#### 案例 A｜三小时古建筑 Chapter

09:20 的建筑外观、10:10 的木雕细节、11:10 的另一建筑外观、11:35 的河岸都属于同一 selected Memory。可以按 summary 组合，不要求相邻；若要写“依次”，必须有完整顺序 Evidence。

#### 案例 B｜现代奶茶店插入

A/C 已由上游判为同一古镇 Chapter，B 为 selected Aha。Chapter 可概括 A/C，但不能写“一路逛到河岸”或把“喝到惊喜甜品”作为 Chapter peak。Aha 单独表达 B。

#### 案例 C｜两张相似建筑

两张图都像古建筑，但 distinct entity 未确认。“两座不同古建筑”被 Block；安全上位概括只能在已有 parent Fact 支持下使用。不能因为时间相隔 20 分钟就自动认定不同，也不能因为相似就自动认定相同。

#### 案例 D｜陶艺动作到结果

拉坯和成品分别成立。若 entity continuity 与 action-result relation 成立，可写“拉坯后的泥坯，已经有了器物的轮廓”；只有另有过程覆盖 Evidence 时，才能写“逐渐／一点点成形”。若只是两个相似陶器，两个 Claim 只能分别成立，组合成制作结果会被 Group Block。

#### 案例 E｜街道拥挤与安静

09:10 人群密集、11:40 街巷相对安静都可能成立。直接写“这是一条既拥挤又安静的街”会消除时间条件；有 temporal/contrast Evidence 时应明确两个时段，否则只选择其中更能代表 Chapter 的 Claim。

#### 案例 F｜生日与猫跳蛋糕

蛋糕、围聚、猫跳上蛋糕都是真实 Claims。selected Aha reservation 仍阻止它们被组合成 Chapter 的高潮句；“每项都真实”不能绕过 narrative independence。

#### 案例 G｜普通会议的虚假结论

讨论、白板、记录三个 Claim 都成立，把它们并列后写成“团队最终取得了重要进展”仍是 emergent unsupported outcome，必须 Block 结果 Claim 或重组为无结果推断的概括。

### 16.12 Invariants、成本与边界

1. Individually `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED` 不等于组合后自动真实；
2. 每个 composition group 必须声明 mode，并验证所有显式/隐式 relations；
3. `SUMMARY_MEMBERSHIP` 允许非相邻 Claims，但不支持连续、相邻或因果；
4. S11 不修改上游 Chapter membership、boundary、Aha independence 或 entity decision；
5. 时间距离不自动 Split，same Memory 也不自动证明连续；
6. 事实排列默认遵循已知 chronology，不为文案效果任意重排；
7. distinct entity、quantifier 与 DUAL_ASPECT 均使用上游 Evidence，不靠措辞推断；
8. Aha reserved peak 不因组合而回流 Chapter Core；
9. Group Block 不必 Block individual Claim，但该组合不能进入 Writer；
10. Tone 不能承担 relation edge，也不能掩盖时间/实体冲突；
11. Aha core group 只能以 `AHA_MOMENT_LINE` 为 target 并围绕一个 `core_peak_event_ref`；A3/B2 upstream support 最多 2 组，C3b1 visible support 最多 1 组，C3b2 minimal local context 最多 1 组且每组恰好一个 atomic Claim，C3b3 observable emphasis 最多 1 项，28.12 light-affect permission 最多 1 项；三类事实 selected 与独立 affect permission 必须与 C3b2/C3b3 immutable decisions 完全一致，均不得升级为第二 core；
12. C/B3 只验证 planned composition，D 的实际 spans/指代/隐含关系必须由 E 再验证；
13. Recompose 严格单调、有界、无重复，耗尽后 Group Block；
14. B3 不决定每句 Claim 数量上限、不选择最终信息预算、不生成文案；
15. B3 只处理 canonical refs 与 relation graph，不读取 Raw pixels，不新增 VLM/API 成本；
16. Aha enclosing composition `group_ref + canonical payload fingerprint` 必须与 provisional plan 提名的 group exact match，不能只比较 selected Claim set 后替换 order/relation/qualifier attachment graph；
17. generated Aha 的 composition 不接受独立 Tone span；observable qualifier 必须由 evidence-bearing Claim 与合法 attachment 支持；唯一例外是 28.12 已计划的 0–1 light-affective lexical permission，它保持在 Claim/relation graph 之外并接受独立 target/action/scope/risk 验证。

## 17. S11-B Closeout 与下一检查点

**状态：DESIGN CLOSED / S11-A+B CROSS-CHECK PASSED / B3 LIGHT-AFFECT v1.1 AMENDMENT APPLIED / NOT FROZEN**

S11-B 已确认：B0 从 A3 确定性产生 surface-independent Claim candidates；用户可见自然句与 Atomic Claim 分离；每个事实、限定与关系独立验真；Claim Ledger 使用 namespaced 四种终态；质量目标不转化为数量配额；S11 不改变 S09 membership 或补位；多个真实 Claims 还需通过 composition truth；长 Chapter 的非相邻 Facts 可以 summary 组合，但不得伪造连续过程；D 的真实措辞最终由 E 做 span 与 implicit-language verification。

进入 C 前的交叉检查已确认：

1. B0→B2→C→B3→D→E 依赖闭合，plan-changing failure 不在 E 内偷偷局部修补；
2. Claim semantic identity、surface decision、implicit assertion 与 Tone permission 分离；
3. rewrite/recompose/replan 均严格单调、有界、无重复；
4. Negative/Absence 使用 closed-world gate；
5. Aha core 绑定单一 peak；A3/B2 完整投影保留 0–2 组合法 support 与可验证 qualifier candidates，C3b1 定义 visible support/context/emphasis 的各自上限，C3b2 联合确定最终 0–1 support 与 0–1 necessary local context，C3b3 再决定 0–1 observable qualifier，并可按 28.12 提供 0–1 个与事实图分离的 light-affect permission；它们均不升级为第二事件；
6. S11 不撤出、补位、重选或改变 S09 membership，失败按方案 A 进入当前 Revision HOLD/BLOCK；
7. V1.21 runtime delta、chronology 与原子发布边界保持不变；
8. 独立复核未发现残留 P1/P2。

下一步进入 S11-C：Narrative Content Plan。它只从 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED` pairs 中建立 provisional groups，经 B3 得到 `COMPOSITION_COMPOSABLE` 后，决定 Chapter Title/Story、Aha Moment Line、Atmosphere 与 Tags 分别选择什么；并处理 Chapter 一至两句话的信息预算、Aha 单峰预算、跨 surface 去重复以及 Chapter 与 Aha 的表达差异。

## 18. S11-C1｜Chapter Narrative Content Budget

**状态：CONFIRMED**

### 18.1 用户体验合同｜不数 Atomic Claims，控制 Content Groups

V1 锁定：

> Chapter Story 不设置每句 Atomic Claim 硬上限；采用“一项核心内容组＋最多一项支持内容组＋最多一项轻量氛围”的整体预算。

原因：

1. 一个自然短语可能包含 object、attribute、location 与 relation 等多个 Atomic Claims，机械计数不能可靠代表阅读负担；
2. 不同语言的语法拆分粒度不同，固定 Claim 数会造成跨语言不一致；
3. 用户真正感受到的是“这句话同时让我理解几件事”，因此使用 semantic content group 控制密度；
4. B1/B2/B3 仍逐 Claim 验真，C1 只决定从合法 Claims 中选择多少信息；
5. 3–5 个精选媒体不要求全部被 Story 点名，媒体、Title、Time Label 与 Tags 各自承担一部分信息。

### 18.2 V1 Chapter Story 总预算

~~~text
CORE_GROUP       exactly 1
SUPPORT_GROUP    0..1
TONE_SPAN        0..1

Story sentences
  default 1
  maximum 2

Atomic Claim hard maximum
  NOT SET
~~~

预算不是填空任务：

- `SUPPORT_GROUP=0` 完全合法；
- `TONE_SPAN=0` 完全合法；
- Core 足够时默认一句结束；
- 不能为了显得丰富而强行使用所有槽位；
- 不能把一个超载 Group 拆成第三句话绕过最大两句合同。

### 18.3 CORE_GROUP

每个 Chapter 恰好一个 Core Group，负责回答：

> 这段 Memory 最核心、最值得让用户一眼理解的经历是什么？

结构：

~~~text
CORE_GROUP
  one identity-aligned core proposition
  + 1..3 representative concrete details
~~~

规则：

1. core proposition 必须为 `CHAPTER_STORY_CORE`，与 S09 selected Memory identity、S10 active media core 对齐；
2. representative details 必须为 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED`；
3. 细节数量是 1～3 的上界合同，不要求每次取满三项；
4. 每个新增细节必须让用户获得新的具体理解，而不是同义重复；
5. 同一对象的不同角度只有在 `DUAL_ASPECT` 或其他独立信息关系成立时，才能占两个 detail roles；
6. selected Aha reserved peak 不能进入 Chapter Core Group；
7. Core Group 必须经 B3 得到 `COMPOSITION_COMPOSABLE`；
8. 如果没有一个可靠 core proposition 和至少一个具体 detail，输出 `CONTENT_PLAN_BLOCKED`，不能只靠 Tone 建立 Chapter Story。

代表细节按以下顺序选择：

1. Memory core coverage；
2. 对用户理解的独立增量；
3. 与 active final media 的可解释一致性；
4. 具体但不超过 assertion ceiling；
5. 跨 detail 非重复；
6. 已知 chronology 下的自然组织能力。

不使用“素材越多越优先”或“Manual 一定优先”替代以上判断。

### 18.4 SUPPORT_GROUP

每个 Chapter 最多一个 Support Group。它只能承担一个主要职责：

~~~text
PROGRESSION
CONTRAST
FACTUAL_CLOSURE_OR_RESULT
NECESSARY_CONTEXT
DISTINCT_SUPPORTING_ASPECT
~~~

规则：

1. Support Group 不是第二个 Core，也不能引入另一个 Memory；
2. 一个 Group 只选择一个主要职责，不能同时塞入路线、人物、结果和氛围；
3. relation 与必要 endpoints 均须独立通过 B2/B3；
4. Support 删除后若不损失用户对 progression/contrast/closure/context 的实质理解，应删除；
5. selected Aha 可以作为 boundary/constraint 被考虑，但其 peak 不进入 Support；
6. 普通漂亮画面、重复 object 或“让文字更长”不能获得 Support 资格；
7. Support 可以与 Core 写在同一句，也可以在通过第二句门后独立成句。

### 18.5 TONE_SPAN

每个 Chapter 最多一个很短的 Tone Span：

1. 必须已有 `TONE_ALLOWED`；
2. 可以附着在第一句或第二句，不自动获得独立句子；
3. 不增加人物、事件、地点、时间、关系、结果或用户内心事实；
4. 不承担 Core/Support/Relation；
5. 与其他 Chapter 的 Tone 不能固定套用同一句模板；
6. 删除后事实内容必须完全不变；
7. Tone 与 factual closure 分离：“到达河岸”是 Claim，“留下一点余韵”可以是 Tone。

### 18.6 一句还是两句

~~~text
ONE_SENTENCE_SUFFICIENT
SECOND_SENTENCE_JUSTIFIED
~~~

默认 `ONE_SENTENCE_SUFFICIENT`。只有第二句满足以下任一条件才使用：

1. 一个合法 Support Group 无法在不使第一句过载的前提下自然表达；
2. progression/contrast/closure 需要独立句子才能避免错误关系或指代；
3. 一个 `TONE_ALLOWED` span 对阅读体验有材料增量，且不能自然附着第一句；
4. 删除第二句会明确损失一种 C1 允许的独立叙事职责。

同时必须满足：

- 第二句不重复 Core；
- 不引入第二个 Core 或另一个 Memory；
- 不超过一个 Support Group 与一个 Tone Span 的总预算；
- 两句整体通过 B3，D 后再通过 E actual-language verification。

如果第二句只是在不同措辞下重说第一句，必须回到一句。

### 18.7 “精选媒体不等于全部点名”合同

Chapter 的 3–5 个 final media items 与 Story 是互补关系：

1. Story 不逐项生成 caption；
2. 3–5 个媒体不要求对应 3–5 个名词；
3. 没进入 Story 的媒体仍可以通过视觉内容、Tag 或用户查看来表达价值；
4. Story 优先覆盖 Memory identity 和最有代表性的 1～3 个 concrete details；
5. Dominant Motif 的重复实例只有带来不同实体/方面/时段意义时才进入文字；
6. Story 未点名某项媒体不等于该媒体应从 S10 set 删除；
7. C1 不修改 S10 set、Hero 或 chronology。

### 18.8 规划与有界重组

C1 只在合法候选上做有限结构化选择：

~~~text
CLAIM_SEMANTIC_SUPPORTED
+ SURFACE_SUPPORTED
→ choose one provisional CORE_GROUP
→ optionally choose one SUPPORT_GROUP
→ optionally choose one TONE_ALLOWED candidate
→ B3 composition validation
→ sentence-count justification
~~~

当 B3 拒绝 group：

1. 优先删除最低增量 detail；
2. process mode 可降为 summary mode；
3. Support 可删除，不得把它升级为 Core；
4. Tone 可删除，不得用它掩盖 Claim 缺口；
5. replan 必须沿 B3 已冻结的单调、有界、无重复路径；
6. Core 仍无法成立时 `CONTENT_PLAN_BLOCKED`；
7. C1 不调用 VLM、不重新读取 Raw、不改变 S09/S10。

### 18.9 输出结构

~~~text
ChapterNarrativeContentPlan
  selected_memory_ref
  stable_memory_id
  revision_ref
  active_projection_fingerprint
  claim_ledger_ref
  candidate_projection_ref
  core_group
    core_proposition_claim_ref
    representative_detail_claim_refs[1..3]
    composition_mode
    composition_group_ref
    memory_identity_alignment_check
    active_media_alignment_check
    reservation_check
    detail_increment_audits[]
  support_group?
    support_function
    support_claim_refs[]
    relation_refs[]
    composition_group_ref
    deletion_test
    material_increment_audit
  tone?
    tone_candidate_ref
    tone_permission_decision_ref
    intended_attachment
  sentence_budget
    default_sentence_count
    maximum_sentence_count
    sentence_count_decision
    second_sentence_justification
  atomic_claim_hard_max = NOT_SET
  plan_state
    CONTENT_PLAN_READY
    CONTENT_PLAN_REBUILD_REQUIRED
    CONTENT_PLAN_BLOCKED
    CONTENT_PLAN_CONTRACT_INVALID
  reason_codes[]
  policy_versions
  content_plan_fingerprint
  construction_audit
~~~

`CONTENT_PLAN_READY` 只代表内容槽位与语义组合可进入 D，不代表实际文案已写完，更不代表 `PUBLISH_READY`。

### 18.10 案例交叉检查

#### 案例 A｜三小时古镇 Chapter

Final media 有牌坊、建筑外观、木雕、另一座建筑、河岸共五项。

~~~text
Core proposition
  old-town walk

Representative details
  gate
  wood carving
  distinct traditional roofline

Optional Support
  reach riverside, only if progression relation is grounded

Optional Tone
  late-light aftertaste, only if TONE_ALLOWED
~~~

Story 不必把五项全部列出；第二座建筑仍可由媒体表达。如果“不同建筑”身份未确认，就不能用数量词挤进 Core。

#### 案例 B｜生日 Chapter＋独立猫 Aha

~~~text
Core
  cake + candlelight + gathering

Support
  group photo closure, only if chronology/closure is grounded

Reserved
  cat jumps onto cake → selected Aha peak, excluded from Chapter plan
~~~

不能因为猫的画面最精彩，就把它加入 Chapter 的三个 representative details。

#### 案例 C｜陶艺长 Manual

~~~text
Core
  pottery-making activity
  wheel shaping
  formed object

Support
  ACTION_RESULT, only if entity continuity is grounded
~~~

若 action-result 不成立，仍可保留安全 Core details，但不能靠第二句声称“完成作品”。

#### 案例 D｜普通会议

~~~text
Core
  meeting discussion
  whiteboard
  table-side notes

Support
  none, unless a real progression/result exists

Tone
  optional restrained daily-work rhythm
~~~

不使用“高效、重要进展、圆满完成”来填 Support 槽位。

#### 案例 E｜简单散步

只有一条可靠核心和一个 concrete detail：

> 傍晚沿着河边走了一段路。

一句足够；Support 和 Tone 都可以为空。不能因为预算“最多允许”而强行增加第二句。

#### 案例 F｜超载文案

> 九点穿过牌坊，沿石板路依次看过木雕、塔楼、三座建筑，随后去奶茶店喝甜品，最后来到河岸，留下了难忘的回忆。

即使个别事实成立，这句话仍混入过多 details、多个 relations、可能的 selected Aha 与用户状态。C1 应保留一个 Core Group，最多一个 Support；其余交给媒体/Aha/Tag，不通过长句压缩全部日程。

### 18.11 Invariants、成本与边界

1. V1 不设置每句 Atomic Claim 硬上限；
2. 每个 Chapter 恰好一个 Core Group；
3. Core Group 只有一个 identity-aligned proposition 与 1～3 个 representative details；
4. 每个 Chapter 最多一个 Support Group，且只有一个主要职责；
5. 每个 Chapter 最多一个 Tone Span，Tone 不承担事实；
6. Story 默认一句、最多两句，第二句必须通过 deletion/material-increment test；
7. 3–5 个媒体不要求全部进入 Story，未点名不触发媒体删除；
8. selected Aha reserved peak 不进入 Chapter Core/Support；
9. Support/Tone 不因槽位存在而必须填满；
10. C1 不决定 Title/Story/Tag 的重复预算，留给 C2；
11. C1 不决定 Aha 文本结构；该结构随后由 C3b1 确认为单一 `AHA_MOMENT_LINE`，具体字符长度仍留给 D4；
12. C1 不生成最终文字、不声明 publish readiness、不修改 membership/media；
13. C1 只处理有限 Claim refs/group graph，不新增视觉理解或上传成本。

## 19. 下一检查点

下一步进入 S11-C2：Title、Story、Time Label、Canonical Tags 的跨 Surface 信息分工与去重复。需要决定 Title 已表达“古镇漫步”后，Story 是否允许自然地再次出现“古镇漫步”，以及怎样区分必要的身份呼应与浪费阅读空间的机械重复。

## 20. S11-C2｜Cross-Surface Information Ownership 与 Controlled Echo

**状态：CONFIRMED**

### 20.1 用户体验合同｜允许必要重叠，禁止无增量重复

V1 锁定：

> Title 与 Story 允许必要的语义重叠，但禁止无增量的机械重复；Story 保持最低限度的独立可理解性，并把主要篇幅用于 Title 尚未表达的具体内容。

补充合同：

1. Story 必须在不显示 Title、Time Label 与 Tags 时仍能让用户大致理解核心经历；
2. 必要时允许 Story 主动呼应一次 Title identity；
3. identity echo 所在句必须同时增加 concrete detail、relation、progression 或其他材料信息；
4. 同一个 identity 在 Story 中最多主动呼应一次；
5. 只换同义词复述 Title 仍属于重复，不因字面不同而通过；
6. 去重复按 normalized semantics 判断，不只比较字符串；
7. 最低独立可理解不要求 Story 重复 exact time、全部 Tags 或完整 Title 文案。

### 20.2 各 Surface 的信息职责

| Surface | 主要职责 | 不应承担 |
| --- | --- | --- |
| Title | 用一个简洁 identity 定义“这是什么 Memory” | 完整过程、多个细节、无依据情绪评价 |
| Story | 具体经历、代表细节、必要关系与有限 Tone | 时间日志、Tag 列表、Title 的空泛改写 |
| Time Label | 准确时间、时段或日期范围 | 故事情绪、事件价值判断 |
| Canonical Tags | 稳定活动/场景/主题索引 | 自然句、进展/因果、用户感受 |
| Display Labels | 将 canonical concept 转成用户可读标签 | 创造新的事实或分类 |

一个事实可以因功能不同合法出现在多个 surfaces。例如 `pottery` 同时作为 Title identity 和 Canonical Tag 是合法 functional overlap；但 Story 不能只写“这是一段陶艺体验”而不增加任何内容。

### 20.3 Story 的最低独立可理解性

使用 `STORY_STANDALONE_COMPREHENSION_TEST`：

~~~text
temporarily hide
  Title
  Time Label
  Tags

read Story alone
→ can a user roughly identify the main experience?
~~~

通过不要求 Story 重写所有 metadata，但必须：

1. 有可理解的主体/活动/场景核心，不能只写“这里、这一刻、这段经历”；
2. 不依赖 Tag 才知道用户在做什么；
3. 不依赖 Title 才能区分“散步、会议、生日、制作”等基本 Memory type；
4. 可以通过 concrete details 自然暗示 identity，不强制 exact Title phrase；
5. 如果 concrete details 仍不足以识别，允许一次受控 identity echo；
6. 独立可理解不等于完整复述，仍受 C1 一至两句预算约束。

例：

Title：`古镇漫步`

可独立理解且不 exact echo：

> 上午走在古镇街巷里，牌坊、木雕和古建筑屋檐，让这段路多了几分旧城气息。

可受控 echo：

> 这段古镇漫步里，牌坊、木雕和古建筑屋檐，让沿途多了几分旧城气息。

不通过：

> 这是一段古镇漫步。

第三句只重复 Title，没有 detail/relation/material increment。

### 20.4 Controlled Identity Echo Gate

Story 中的 identity overlap 只有同时通过以下条件才合法：

1. `identity_ref` 与 Title 指向同一个 grounded Memory identity；
2. Story 若不出现该 identity，会变得含糊、断裂或难以独立理解；
3. 同句至少新增一个 `CHAPTER_STORY_CORE/CHAPTER_STORY_SUPPORT` concrete detail 或合法 relation；
4. Story 内尚未出现过等价 identity echo；
5. wording 不制造比 Title 更具体的新身份；
6. removal test 证明删除 echo 会明显降低理解，而不是只略微改变文风；
7. 即使 echo 合法，也不能挤掉 C1 必需的 concrete details。

Decision：

~~~text
IDENTITY_ECHO_REQUIRED
IDENTITY_ECHO_OPTIONAL_BUT_MATERIAL
IDENTITY_ECHO_REDUNDANT
IDENTITY_ECHO_CONTRACT_INVALID
~~~

`OPTIONAL_BUT_MATERIAL` 只在自然度/独立理解确有材料提升时保留；纯偏好或“听起来更完整”不足以通过。

### 20.5 Title ↔ Story

合法：

- Title 给 identity，Story 给 concrete details；
- Story 为独立可理解呼应一次 identity，并在同句增加新信息；
- Story 使用比 Title 更具体、但已 grounded 的 detail；
- Title 与 Story 共享核心语义，但承担不同职责。

不合法：

- Story 第一整句只是 Title 的主谓句版本；
- 第二句再次重复同一 identity；
- 使用同义词掩盖重复，例如 Title“陶艺体验”、Story“这次做陶的经历很特别”，但“很特别”也无 Evidence；
- Title 已写 exact location，Story 重复 location 却不添加任何 event/detail；
- Story 因依赖 Title 而只剩“这里很有氛围”。

Title 的最终字数、句法和命名风格留给 S11-D2；C2 只定义信息 ownership 与 overlap legality。

### 20.6 Time Label ↔ Title / Story

Time Label 拥有准确时间表达。默认：

1. exact timestamp/range 不写入 Story；
2. Story 可使用“上午、傍晚、夜里”等 broad time phrase，但必须对 progression、scene change、light/atmosphere 或理解有材料意义；
3. 如果 broad time 只是重复 Time Label，应删除；
4. Title 默认不加入时间；只有时间本身构成 identity 时可以使用，例如“夜游古镇”，且必须有 grounded night context；
5. Title“夜游古镇”与 Time Label“20:10–21:35”功能不同，可以共存；
6. Story 不能把 Time Label 的范围升级成“整个上午、整晚、一直”，除非有 continuity/coverage Evidence。

例：

~~~text
Title      夜游古镇
Time       20:10–21:35
Story      夜里沿河漫步，灯笼亮在岸边，水面留着清晰的倒影。
~~~

该案例假定 Time range 已通过 D3d actual-boundary gate。“夜”在三个 surface 出现并非自动重复：Title 定义 identity，Time 给准确范围，Story 若需要可保持独立理解；但每处都必须有自己的功能。

### 20.7 Canonical Tags ↔ Title / Story

Canonical Tags 是索引层，采用 functional overlap：

1. Tag 与 Title/Story 语义重叠不自动删除；
2. Title“陶艺体验”仍可保留 canonical tag `POTTERY`；
3. Story 可以自然使用“陶艺、拉坯”等词，不因 Tag 已存在就禁用；
4. Story 不能把多个 Tags 拼成“陶艺、手作、室内、周末体验”式清单；
5. Tag 不能承载 Story 中缺失的 core，使一个无法独立理解的 Story 变得勉强可懂；
6. Display Label 只能翻译/本地化 canonical concept，不生成更具体的品牌、地点或用户关系；
7. Tag 数量、排序与最终显示形式留给 D5，不在 C2 冻结。

### 20.8 Semantic Overlap Classification

每一组 cross-surface overlap 归入：

~~~text
REQUIRED_IDENTITY_ECHO
MATERIAL_NATURAL_OVERLAP
FUNCTIONAL_INDEX_OVERLAP
REDUNDANT_RESTATEMENT
OVERLAP_CONTRACT_INVALID
~~~

- `REQUIRED_IDENTITY_ECHO`：Story 独立理解所需；
- `MATERIAL_NATURAL_OVERLAP`：自然语言需要且同句有明显新内容；
- `FUNCTIONAL_INDEX_OVERLAP`：Tag/Time/Title 因职责不同合法共享语义；
- `REDUNDANT_RESTATEMENT`：删除后理解与功能不受损，应删除；
- `OVERLAP_CONTRACT_INVALID`：identity/assertion/surface/version 引用不一致。

判断不能只做 embedding/string similarity：

1. 同义表达可能是重复；
2. 同一个词在不同职责下可能不是重复；
3. 需要比较 normalized assertion、surface role、material increment 与 removal test；
4. 不因相似度高就删除用户理解所必需的 identity；
5. 不因字面不同就保留无增量改写。

### 20.9 Cross-Surface Removal Test

对疑似重复 span/claim：

1. 临时删除它；
2. 检查 Story 是否仍可独立理解；
3. 检查所在 surface 的主要职责是否仍完整；
4. 检查是否损失 concrete detail、relation、exact time 或 indexing function；
5. 检查删除后是否造成错误指代或更强依赖其他 surface；
6. 无材料损失则标记 `REDUNDANT_RESTATEMENT`；
7. 有材料损失但 overlap 合法则保留，并记录 overlap class；
8. 删除不能让 Story 跌破 C1 Core Group 合同。

### 20.10 输出结构

~~~text
CrossSurfaceInformationPlan
  selected_memory_ref
  stable_memory_id
  revision_ref
  active_projection_fingerprint
  chapter_content_plan_ref
  title_identity_assertion_ref
  title_grounded_modifier_assertion_ref?
  title_modifier_attachment_ref?
  title_modifier_materiality_check?
  story_core_and_support_refs[]
  time_label_surface_plan
    base_time_label_decision_ref
    candidate_time_label_assertions[]
      assertion_ref
      candidate_eligibility
        BASE_ELIGIBLE
        | CONTINUITY_RETAIN_ONLY
      cross_surface_overlap_audit_ref
      surface_ownership_audit_ref
    base_selected_time_label_assertion_ref?
    time_label_omission_permission_ref?
    base_time_label_plan_state
      TIME_LABEL_ASSERTION_SELECTED
      | TIME_LABEL_OMITTED_BY_CONTRACT
      | TIME_LABEL_PLAN_CONTRACT_INVALID
  canonical_tag_assertion_refs[]
  story_standalone_comprehension_check
  identity_echo_decision
  identity_echo_count
  overlap_edges[]
    left_surface
    right_surface
    shared_normalized_assertion_refs[]
    overlap_class
    material_increment_check
    removal_test
    decision
    reason_codes[]
  redundant_span_or_assertion_refs[]
  surface_ownership_audits[]
  plan_state
    CROSS_SURFACE_PLAN_READY
    CROSS_SURFACE_REWRITE_REQUIRED
    CROSS_SURFACE_PLAN_BLOCKED
    CROSS_SURFACE_CONTRACT_INVALID
  policy_versions
  cross_surface_fingerprint
  construction_audit
~~~

该 plan 仍是 semantic plan，不生成最终词句。D2a 后置确认 Title 为一个 identity core＋0–1 modifier；因此 modifier 若存在，必须使用独立 `ImplicitSurfaceAssertion` 与 B0 既有 `ImplicitSurfaceAssertionAttachment`，不能焊进 identity Claim 后逃避独立验真。modifier 为空时，三个 optional 字段必须同时为空；存在时，B3 必须验证 core、modifier 与 attachment 的组合真值，且 `cross_surface_fingerprint` 必须覆盖这些引用。D 写作后，E 必须用实际 spans 重跑 overlap、modifier attachment 与 standalone comprehension checks。

Time Label 是可省略、且可能存在 single／dual／exact 等多个当前合法候选的 deterministic metadata surface，因此不能继续使用一个 mandatory `time_label_assertion_ref` 假定它永远存在且已经是最终选择。C2 只保存 current Revision 的**基础判定**、B2 已批准的候选 assertions、每个候选自己的 cross-surface/ownership audit 与显式 omission permission；跨 Revision 的最终可见选择由 C3a＋D3f 产生新的不可变 decision，不回写或后填 C2 artifact，避免生命周期自引用。双时段或 exact range 以一个 normalized composite `ImplicitSurfaceAssertion` 表达完整用户语义，并在内部携带两侧／两端 support 与 relation refs；它不是让 formatter 临时拼接两个未经组合验证的 assertion。D3f 选择非 base 的 continuity candidate 时，必须携带该候选已通过的 C2 audit，不能默认 base candidate 的 overlap 结论对它同样成立。

**D5b1 contract-alignment amendment：** `canonical_tag_assertion_refs[]`继续保存 B2 已批准的 D5 index umbrella assertions，不能在 C2 提前删掉 exact entity assertion。D5 后续建立 typed child decisions：Concept assignments 与 Entity links 分开计数、验证和更新；C2 cross-surface overlap audit 继续作用于两类，不因路由类型而失效。

### 20.11 案例交叉检查

#### 案例 A｜古镇漫步

~~~text
Title
  古镇漫步

Story
  这段古镇漫步里，牌坊、木雕和古建筑屋檐，让沿途多了几分旧城气息。

Time Label
  上午

Tags
  OLD_TOWN_WALK
  TRADITIONAL_ARCHITECTURE
~~~

Story 的一次 identity echo 合法，因为同句增加三个 concrete details；Time/Tags 各自承担准确时间和索引职责。

#### 案例 B｜生日聚会

~~~text
Title
  生日聚会

Story
  蛋糕旁亮着烛光，几个人围在桌边。
~~~

Story 没 exact 复述 Title，但仍可独立理解。若只写“这是一场生日聚会”，则无增量。

#### 案例 C｜陶艺体验

~~~text
Title
  陶艺体验

Story
  拉坯后的泥坯，已经有了器物的轮廓。

Tag
  POTTERY
~~~

Tag 与 Title 重叠合法；Story 用 concrete action/result 表达，不拼接 Tag 列表。

#### 案例 D｜夜游古镇

Title、Time Label、Story 都可能使用“夜”概念，但职责不同。若 Story 已靠灯笼、夜色、河岸倒影独立可懂，可以删除额外的“夜间”字样；若删除后身份变得含糊，可以保留一次。

#### 案例 E｜客户演示的机械重复

~~~text
Title
  客户演示

Story
  这是一场客户演示。

Tag
  PRESENTATION
~~~

Story 为 `REDUNDANT_RESTATEMENT`；Tag 不能拯救它。Story 必须加入白板、屏幕讲解、问答等已 grounded concrete content，否则 C1/C2 Block。

#### 案例 F｜同义词伪装

Title 是“河边散步”，Story 写“这是一次沿河而行的经历”。字面不同但 normalized assertion 基本相同，且没有新 detail/relation，仍判定重复。

### 20.12 Invariants、成本与边界

1. Story 在隐藏 Title/Time/Tags 后仍最低限度可理解；
2. Story 最多主动呼应一次 Title identity；
3. identity echo 所在句必须同时提供材料新增信息；
4. 同义改写不绕过 redundancy gate；
5. Title、Story、Time、Tag 按职责去重复，不做全局字符串去重；
6. exact time 默认由 Time Label 承担，Story 只有在有叙事价值时重复 broad time；
7. Tag 与 Title/Story 可 functional overlap，但 Tag 不补 Story core；
8. Display Label 不创建新事实；
9. Story 不逐项解释 Tags 或媒体；
10. C2 本身不冻结 Title 字数、Tag 数量、Aha 文本结构或 App 具体布局；Aha 文本结构随后由 C3b1 单独确认，不回写成 C2 的职责；
11. C2 不修改 C1 内容预算、S09 membership 或 S10 media；
12. 去重复只比较 normalized refs 与有限 graph，不新增 VLM/API/上传成本。

## 21. S11-C3 拆分与输入决策

S11-C3 分成两个独立检查点：

1. `C3a Cross-Revision Narrative Continuity`：同一个 Memory 在后续 Sync/Revision 中，何时保留、局部修订或重建已展示文字；
2. `C3b Chapter/Aha Content Plan Separation`：Chapter 与 Aha 分别应规划怎样的用户可见内容。

用户已确认 C3a 的产品原则：同一个已经向用户展示、stable identity 未改变的 Memory，Title/Story 默认保留；只有事实纠错、核心身份或材料性进展变化、以及 active media 不再兼容时才改变。不能因为模型换代、文风偏好或 Finalization 到来就重新润色。

## 22. S11-C3a｜Cross-Revision Narrative Continuity

**状态：CONFIRMED**

### 22.1 目标与适用范围

Cross-Revision Narrative Continuity 解决的不是“旧句还能不能生成得更漂亮”，而是：用户已经看过的一段 Memory，后续 Sync 增加素材或系统进入新 Revision 时，什么变化足以打断文字连续性。

本合同适用于：

- 已向用户展示的 generated Preview Title/Story；
- 已向用户展示的 generated Final Title/Story；
- C3b1 已确认的 generated `AHA_MOMENT_LINE`；
- 已向用户展示、由确定性规则生成的 Time Label；它参与同一 Memory 的整体连续性聚合，但不进入 Writer 或 generated wording decision；
- 未发布内部草稿可以重新计算，但必须保持 deterministic、versioned 和可审计，不能仅因内部重算就造成外显文案变化。

本合同不允许 S11 借“文字连续性”修改 S09 membership、S10 media、S12 发布边界或 retention。用户原文/用户编辑文字使用独立 provenance，受 22.8 的保护规则约束。

C3a 先核对 protected user surface 的 presentation satisfaction，再分别做 generated wording 与 deterministic metadata 的 applicability gate。若整个 Memory 既没有上一条用户可见 generated artifact，也没有上一条用户可见 deterministic metadata artifact，才返回整体 `CONTINUITY_NOT_APPLICABLE`。若只有 prior Time Label，则只对 Time Label 运行其 owner contract，不能借此把从未发布过的 Title／Story 伪装成 `TEXT_RETAIN`；这些 generated surfaces 仍各自走首次生成链。未发布内部 draft 不得伪装成 prior published artifact，也不得成为任一 surface 的 continuity baseline。

applicability 还必须逐 surface 判断：上一版可能已有 generated Title、但没有 Story，或当前 Revision 新增一个合法 surface。已有 prior 的 surface 进入四状态；无 prior 的 surface 不创造第五个 `TEXT_*` 状态，而是标记 `NOT_APPLICABLE_NO_PRIOR_GENERATED_SURFACE`，独立走首次生成链。只有该首次生成通过 B3/D/E 后，才能被整体聚合为已满足。

优先级固定为：

~~~text
truth correction
> identity / core correctness
> active-media compatibility
> material representation
> cross-Revision continuity
> stylistic preference
~~~

因此，连续性不能保护已经错误或与媒体失配的文字；但“可以写得更好听”也不能越过连续性门。

### 22.2 四状态决策

只有存在上一条用户可见、provenance 为 `GENERATED` 的 surface，且引用合同完整时，才进入以下四种内容决策。无 prior、用户文字与合同损坏分别由前置 applicability/provenance/contract gate 处理，不伪装成第五种内容结果。

#### `TEXT_RETAIN`

复用上一用户可见 Revision 的**原始措辞**，不是重新生成一句语义相近的话。

适用条件：

- 原 Claims、identity、assertion ceiling 与 surface permission 仍合法；
- 与当前 active S10 projection 仍一致；
- 新素材没有让原文变得错误、明显失真或失去代表性；
- 所有变化都只属于风格优化、更多相似细节或弱补充。

#### `TEXT_PATCH`

只修改受影响的最小 span，必要时修改一整句；未受影响的 Title/句子/span 原样保留。

适用条件：

- 变化是材料性的，但没有改变整个 Memory identity 或 Content Plan 骨架；
- 可通过删除、替换或补入一个已验证 Claim 恢复真实性与代表性；
- patch 不需要偷偷引入新的关系、因果、用户心理或第二个故事。

#### `TEXT_REBUILD`

原 Content Plan 的 core/group 结构已不再成立，需要基于当前合法 Facts 和 active projection 重新规划文字。

典型原因：

- stable Memory 的核心身份发生材料性变化；
- 原 Story Core 不再被当前媒体/Claim Ledger 支持；
- 新 Revision 出现真正改变这一段经历理解方式的 progression、contrast 或 closure；
- Aha peak identity 在合法上游 Revision 中发生材料性改变。

`TEXT_REBUILD` 仍不改变上游选材；它只重建相应 narrative surface。

#### `TEXT_BLOCK`

当前 Revision 已无法生成安全、真实、与 active media 一致的最低文本。

`REQUIRED` surface 的 `TEXT_BLOCK`，或没有合法 omission permission 的 optional surface failure，才依照用户确认的方案 A 使当前 Revision 整体进入 narrative HOLD/BLOCK；合同明确允许省略的 optional surface 不单独阻断 Revision。S11 不撤出成员、寻找补位或发布临时子集。若产品 retention 允许，上一条仍合法的已发布 Revision 可以继续显示；但不能把已经失效的旧文字复制到新 Revision 冒充有效结果。

#### 四状态之前的 Contract Gate

1. prior artifact/ref/provenance/version/lineage 完整：`SURFACE_CONTINUITY_CONTRACT_VALID`，才允许做 `TEXT_*` 内容决策；
2. prior ref 悬空、provenance 缺失、版本无法校验或 lineage 损坏：`SURFACE_CONTINUITY_CONTRACT_INVALID`；
3. contract invalid 是工程异常，不是内容不够好，不能降级成 `TEXT_BLOCK`；
4. 用户原文或用户编辑 surface 不混入 generated surface decisions；保存到独立 `protected_user_surfaces[]`，不进入 generated `TEXT_*` 决策；
5. `TEXT_RETAIN/PATCH/REBUILD/BLOCK` 只允许消费 provenance 为 `GENERATED` 的 prior surface；
6. 单个 generated surface 没有 prior 时，记录其首次生成状态，不能因为同一 Memory 的另一个 surface 有 prior 就错误执行 `TEXT_RETAIN`。

#### 四状态必须回到既有验证链

~~~text
TEXT_RETAIN
  → lineage / dependency / compatibility revalidation
  → exact prior wording reuse; no Writer call

TEXT_PATCH, wording only; Content Plan and Claim refs unchanged
  → bounded surface-specific D rewrite → E

TEXT_PATCH with any Claim / relation / group change
  → dispatch by surface/memory type
    Chapter Title/Story → C1/C2 re-evaluation → B3 → D1/D2 → E
    AHA base Claim / relation / group change
                        → C3b2 base replan → C3b3 emphasis + light-affect decisions → B3 → D4 → E
    AHA qualifier-only change, base decision still valid
                        → C3b3 emphasis replan → B3 → D4 → E
    AHA light-affect permission-only change, base/qualifier decisions still valid
                        → C3b3 light-affect replan → B3 → D4 → E
    Time Label          → C2 current candidate plan → D3f deterministic continuity selection
                          → B3 when composition applies → D3e → E
    Canonical Tag       → current metadata surface plan/validator
                          → B3 when composition applies → D5 → E

TEXT_REBUILD
  → the same surface/memory-specific dispatch above

attempt budget exhausted or no safe required core
  → TEXT_BLOCK
~~~

`TEXT_RETAIN` 只有在 prior E decision 的依赖与 policy/version fingerprint 仍新鲜时才能直接复用该验证结果；否则保持 exact wording，但必须重跑必要的 E checks。wording-only patch 只有在 Content Plan、Claim refs 与 prior B3 decision/dependency fingerprint 全部仍有效时，才可复用 B3 并直接进入有界 D→E；任何改变 Claim/relation/group 的 patch 或任意 rebuild 都必须重跑 B3，且任何路径都不能绕过 E 的真实措辞验证或让 Writer直接修改 Claim 计划。

#### Per-surface 到整体状态的确定性聚合

每个 surface 从当前 surface contract 继承 `REQUIRED` 或 `OPTIONAL_BY_CONTRACT`，C3a 不自行决定某字段可选。generated natural-language surfaces 使用 `generated_surface_decisions[]`；Time Label 等确定性 metadata surface 使用 owner-stage immutable decision，并通过 `deterministic_surface_decisions[]`映射进同一聚合，不进入 Writer，也不创建与 C3a 竞争的整体状态机。聚合顺序固定为：

1. 任一 generated/protected/deterministic surface contract invalid：`CONTINUITY_CONTRACT_INVALID`；
2. 任一 protected user surface 的展示满足关系仍为 `PRESENTATION_POLICY_UNRESOLVED`：聚合为 `CONTINUITY_PRESENTATION_POLICY_UNRESOLVED`，保留 reason code 并交给后续 UX/presentation gate；它不是重新跑 C/B3/D/E 可以解决的 narrative replan；
3. `SATISFIES_REQUIRED_VISIBLE_SURFACE` 的受保护用户文字按 presentation contract 视为该展示位已满足，从 generated required set 中排除，绝不再触发同一位置的 Writer；
4. `DOES_NOT_SATISFY_REQUIRED_VISIBLE_SURFACE` 的用户文字不能代替 required generated surface；只有这类仍未满足的 generated surface 才进入相应首次生成链；
5. 完成上述 protected-surface 处理后，若既没有 prior user-visible generated surface，也没有 prior user-visible deterministic surface：`CONTINUITY_NOT_APPLICABLE`；若只有 prior deterministic surface，则整体 applicability 使用 deterministic-only 分支，同时所有 no-prior generated surfaces 仍独立运行首次生成，不能被跳过；
6. 任一 required generated surface 的首次生成、patch/rebuild，或任一 deterministic surface 的 owner-stage decision 尚未完成其 surface-specific plan／validation／formatting：`CONTINUITY_REPLAN_REQUIRED`；
7. 任一 `REQUIRED` generated surface 为 `TEXT_BLOCK/INITIAL_BUILD_BLOCKED`：方案 A 整个当前 Revision 为 `CONTINUITY_BLOCKED`；
8. `OPTIONAL_BY_CONTRACT` surface 只有在存在明确 omission permission，且删除后对应的 surface-specific plan 与 cross-surface contract 仍合法时才可省略；D3c2 的 Time Label omission permission 属于此类合法输入。否则按 required failure 处理，不能由实现临时决定；
9. 所有 required surfaces 通过、所有 optional surfaces 合法完成或被合同允许省略：`CONTINUITY_READY`。

### 22.3 默认保留与材料变化门

默认决策为 `TEXT_RETAIN`。只有至少一个材料变化检查通过，才允许进入 `TEXT_PATCH/TEXT_REBUILD`。

#### 必须改变或重新判断

1. **事实纠错：** 旧文中的对象、动作、地点、时间、人物关系、顺序、数量或限定词被证明错误；
2. **Claim permission 改变：** assertion ceiling、reservation、surface permission 或 Evidence dependency 失效；
3. **核心身份改变：** 合法上游 Revision 改变 Memory identity/core，而非 Writer自己重新命名；
4. **active media 失配：** S10/V1.21 合法 immutable delta 使原 core/detail 不再被当前展示素材支持；
5. **材料性精确化：** 新的可靠事实把一个原本过宽或容易误解的核心身份精确到用户明显关心的层级；
6. **材料性进展：** 新事实真正增加转折、推进或收束，并改变用户对整段 Chapter 的理解。

#### 不足以改变

1. 模型、Prompt、Writer、词库或 policy version 的版本号更新本身；若新 policy 实际改变 Claim 合法性，则按“Claim permission 改变”重新判断；
2. 新句“更优美”“更像日记”或内部评分略高；
3. 新增更多同类建筑、同类街景或相似视角；
4. 同一 Claim 置信度略升，但 normalized proposition 没变；
5. 新增一个弱 Supporting Detail，删除它不影响核心理解；
6. Preview 进入 Final，但事实、选材和核心均未改变；
7. Time Label 或 Canonical Tags 的独立、合法更新；
8. 为了避免模型觉得旧句“重复”而主动换一种说法。

新 Fact 本身不等于材料变化。必须通过至少一种检查：

~~~text
TRUTH_CORRECTION_TEST
IDENTITY_CHANGE_TEST
ACTIVE_MEDIA_ALIGNMENT_TEST
MATERIAL_DELETION_TEST
MATERIAL_SUBSTITUTION_TEST
~~~

- `MATERIAL_DELETION_TEST`：若不把新信息写入用户文案，Memory 是否会明显不完整、失真或缺少真正的转折/收束？
- `MATERIAL_SUBSTITUTION_TEST`：若替换旧表达，提升的是事实准确性/核心代表性，还是只有文风偏好？只有前者允许改变。

### 22.4 各 Surface 的稳定阈值

#### Title｜最高稳定阈值

Title 是用户识别同一个 Memory 的主要锚点，默认比 Story 更稳定。只在以下情况修改：

- 原 identity 错误或不再成立；
- 新的可靠 identity 显著减少误解；
- 核心活动/地点/事件发生材料性改变；
- 原 Title 与当前 active media 核心明显不兼容。

例如 GPS/用户确认把地点可靠精确为周庄，只说明 exact assertion 已具备候选资格；是否 patch 仍必须通过后置 D2d。若当天只有这一段古镇经历且“古镇漫步”仍真实清楚，保持 `TEXT_RETAIN`；若同日存在另一个古镇 Chapter 造成材料性歧义，或旧 exact 地名错误，才允许最小 `TEXT_PATCH`。仅多拍到两栋类似古建筑时同样不修改 Title。

#### Story｜允许材料性局部修订

Story 可以因事实纠错、材料性 progression/contrast/closure 或 active-media incompatibility 做最小 patch。新增相似素材、更多弱细节或更好文风不触发改写。

#### Time Label｜独立确定性更新

Time Label 可依据合法 temporal facts 独立更新，不要求 Title/Story 一起重写。若 Story 中没有受影响的 broad-time Claim，则保持原文。

#### Canonical Tags / Display Labels｜独立分类更新

validated taxonomy/classification 变化可以更新 Tag/Label，但不能仅因 Tag 改变就重写自然语言。Display Label 本地化变化也不改变底层 Title/Story。

#### Aha Moment Line｜selected Aha 的 required narrative surface

C3b1 确认后，selected Aha 的 generated narrative surface 为 `AHA_MOMENT_LINE`，默认 `REQUIRED`；generated Aha Title/Story 不进入 continuity surface set。无 prior Moment Line 时走 `INITIAL_BUILD_REQUIRED`，已有 prior 时使用 C3a 四状态。只有后续 presentation contract 明确判定受保护用户文字已满足该 visible surface，才能免除相应 generated initial build。

### 22.5 Active Media Runtime Revalidation

S10/V1.21 允许的 Route activation、D1-approved single-loss survivor 或 Hero Alternate delta 到来时：

1. 先以新的 `active_projection_fingerprint` 按 14.8 生成/复核不可变 Claim Ledger，并重跑 Claim/Surface compatibility；
2. 原文仍与核心和当前媒体一致：`TEXT_RETAIN`；
3. 只有一个细节失去支持，其他结构不变：删除/替换该 span，`TEXT_PATCH`；
4. Chapter Story Core/identity 不再一致，但同一 selected Chapter 仍有合法核心：按 Chapter 路由 `TEXT_REBUILD`；
5. Aha 的原 `core_peak_event_ref` 仍合法，只是 Moment Line 的 wording/必要 context plan 不再兼容：可按 Aha 路由 `TEXT_PATCH/TEXT_REBUILD`，但 core peak ref 不变；
6. Aha 原 `core_peak_event_ref` 已不再受到支持：`TEXT_BLOCK`；S11 runtime 不得从同一 AhaFacts 中换选另一个 peak；
7. 只有合法上游新 Revision 明确改变 selected Aha peak identity 与 lineage 时，新的 peak 才能进入新的 C3a/C3b2/C3b3 rebuild；不能把 runtime media delta 当成换 peak 授权；
8. Chapter 已无合法核心：`TEXT_BLOCK`；
9. 输入引用或 lineage 合同损坏：`SURFACE_CONTINUITY_CONTRACT_INVALID`，并聚合为 `CONTINUITY_CONTRACT_INVALID`，不能伪装成 `TEXT_BLOCK`；
10. 全程不由 S11 删除、替换、重排媒体或请求 S09 补位。

### 22.6 跨 Revision 的不可变记录

每个新 Revision 生成新的不可变 continuity decision/artifact，不能原地覆盖上一版本。即使 `TEXT_RETAIN`，也要记录“复用了哪一条已发布文字”，而不是只复制字符串后丢失 lineage。

至少保存：

- previous/current Revision refs；
- prior user-visible artifact ref 与 prior visibility state；
- prior/current active projection fingerprints；
- 每个 surface 的 applicability、provenance、contract state，以及适用时的 `TEXT_*` decision；
- retained/changed span refs；
- old/new normalized Claim refs；
- materiality checks 与 reason codes；
- user-authored protection state；
- policy/signal versions 与 decision fingerprint。

相同输入、版本、prior artifact 与 active projection 必须产生相同 decision/fingerprint。

### 22.7 输出结构

~~~text
NarrativeContinuityDecision
  selected_memory_ref
  stable_memory_id
  revision_ref
  prior_revision_ref?
  continuity_applicability
    APPLICABLE_PRIOR_GENERATED
    | APPLICABLE_PRIOR_DETERMINISTIC_ONLY
    | NOT_APPLICABLE_NO_PRIOR_VISIBLE_SURFACE
  prior_user_visible_artifact_ref?
  prior_visibility_state?
    PREVIEW_PUBLISHED
    | FINAL_PUBLISHED
  active_s10_projection_ref
  prior_active_projection_fingerprint?
  current_active_projection_fingerprint
  generated_surface_decisions[]
    surface
    prior_surface_artifact_ref?
    prior_surface_provenance?
      GENERATED
    generated_continuity_applicability
      APPLICABLE_PRIOR_GENERATED_SURFACE
      | NOT_APPLICABLE_NO_PRIOR_GENERATED_SURFACE
    surface_requiredness
      REQUIRED
      | OPTIONAL_BY_CURRENT_SURFACE_CONTRACT
    optional_omission_permission_ref?
    surface_contract_state
      SURFACE_CONTINUITY_CONTRACT_VALID
      | SURFACE_CONTINUITY_CONTRACT_INVALID
    surface_contract_reason_codes[]
    initial_build_state?
      INITIAL_BUILD_REQUIRED
      | INITIAL_BUILD_VALIDATED
      | INITIAL_BUILD_BLOCKED
      | INITIAL_BUILD_OMITTED_BY_CONTRACT
      | INITIAL_BUILD_CONTRACT_INVALID
    initial_build_artifact_ref?
    decision?
      TEXT_RETAIN
      | TEXT_PATCH
      | TEXT_REBUILD
      | TEXT_BLOCK
    prior_claim_refs[]
    current_claim_refs[]
    retained_span_refs[]
    changed_span_refs[]
    materiality_checks[]
    active_media_compatibility_check
    reason_codes[]
  deterministic_surface_decisions[]
    surface = TIME_LABEL
    owner_stage = D3F
    prior_surface_artifact_ref?
    deterministic_continuity_applicability
      APPLICABLE_PRIOR_DETERMINISTIC_SURFACE
      | NOT_APPLICABLE_NO_PRIOR_DETERMINISTIC_SURFACE
    surface_requiredness = OPTIONAL_BY_CURRENT_SURFACE_CONTRACT
    optional_omission_permission_ref?
    deterministic_continuity_decision_ref
    composition_validation_ref?
    formatted_surface_ref?
    actual_surface_verification_ref?
    mapped_aggregate_state
      DETERMINISTIC_SURFACE_READY
      | DETERMINISTIC_SURFACE_OMITTED_BY_CONTRACT
      | DETERMINISTIC_SURFACE_REPLAN_REQUIRED
      | DETERMINISTIC_SURFACE_CONTRACT_INVALID
    reason_codes[]
  title_display_ownership_decision_ref?
  protected_user_surfaces[]
    surface
    protected_user_artifact_ref
    protected_surface_provenance
      USER_AUTHORED
      | USER_EDITED_GENERATED
    surface_requiredness
      REQUIRED
      | OPTIONAL_BY_CURRENT_SURFACE_CONTRACT
    protection_contract_state
      USER_SURFACE_PROTECTION_CONTRACT_VALID
      | USER_SURFACE_PROTECTION_CONTRACT_INVALID
    protected_surface_satisfaction
      SATISFIES_REQUIRED_VISIBLE_SURFACE
      | DOES_NOT_SATISFY_REQUIRED_VISIBLE_SURFACE
      | PRESENTATION_POLICY_UNRESOLVED
    presentation_policy_ref?
    reason_codes[]
  immutable_lineage_ref
  policy_and_signal_versions
  continuity_state
    CONTINUITY_NOT_APPLICABLE
    | CONTINUITY_READY
    | CONTINUITY_REPLAN_REQUIRED
    | CONTINUITY_PRESENTATION_POLICY_UNRESOLVED
    | CONTINUITY_BLOCKED
    | CONTINUITY_CONTRACT_INVALID
  continuity_fingerprint
  construction_audit
~~~

`decision` 只在 `APPLICABLE_PRIOR_GENERATED_SURFACE + SURFACE_CONTINUITY_CONTRACT_VALID` 时存在。`initial_build_state` 只在单 surface 无 prior 时存在；required surface 在 `INITIAL_BUILD_VALIDATED` 之前不能算作完成，optional surface 只有持有明确 omission permission 才能进入 `INITIAL_BUILD_OMITTED_BY_CONTRACT`。用户文字只进入独立 protection array；contract invalid surface 不生成内容性 `TEXT_*` decision。`deterministic_surface_decisions[]` 只保存 owner decision 的聚合映射，不复制或改写其内部规则；当前只正式接入 D3f Time Label，未来 D5 若需要接入 Canonical Tags，必须由 D5 自己确认后扩展，不能在本次 D3 修正中预判。Time Label 只有在适用的 B3 validation、D3e formatting 与 E verification 均已完成，或持有合法 omission permission 时，才可映射为 `DETERMINISTIC_SURFACE_READY/OMITTED_BY_CONTRACT`；中间状态必须保持 `REPLAN_REQUIRED`。C3a policy 先指导 per-surface routing，最终 aggregate bundle 再收集已经完成的 child refs；D3f、D3e 与 E child artifacts 不反向引用这个后置 aggregate bundle，从而避免生命周期循环。

建议 reason codes 至少包括：

~~~text
NO_MATERIAL_CHANGE
NO_PRIOR_VISIBLE_GENERATED
NO_PRIOR_GENERATED_SURFACE
INITIAL_SURFACE_BUILD_REQUIRED
STYLE_ONLY_CHANGE_REJECTED
FINALIZATION_ONLY_CHANGE_REJECTED
FACT_CORRECTION_REQUIRED
IDENTITY_MATERIALIZED
CORE_IDENTITY_CHANGED
MATERIAL_PROGRESSION_ADDED
MATERIAL_CONTRAST_ADDED
MATERIAL_CLOSURE_ADDED
ACTIVE_MEDIA_DETAIL_INCOMPATIBLE
ACTIVE_MEDIA_CORE_INCOMPATIBLE
RESERVATION_CHANGED
USER_AUTHORED_TEXT_PROTECTED
USER_PRESENTATION_POLICY_UNRESOLVED
PROTECTED_SURFACE_DOES_NOT_SATISFY
OPTIONAL_SURFACE_OMITTED_BY_CONTRACT
NO_SAFE_NARRATIVE_CORE
SURFACE_CONTINUITY_CONTRACT_INVALID
CONTINUITY_CONTRACT_INVALID
~~~

### 22.8 用户原文与用户编辑保护

1. 带有 user-authored provenance 的 Title/Story/Note 保持 immutable ref；
2. AI 不把用户文字当作可自动润色的 generated surface，也不静默覆盖；
3. 用户编辑了原 AI Title/Story 后，编辑结果按 user-authored surface 保护；
4. 若用户文字与新事实发生冲突，保留原文及 provenance，不由 S11 偷改；受影响的 generated narrative 按 required/optional surface contract 进入首次生成、replan 或 Block，并交给后续用户文字/产品处理；
5. Chapter Title 的显示优先级与恢复语义由后置 D2f 决定；Story／Note 等其他 surface 的用户文字与 AI 文字谁优先显示、是否并排、是否提示冲突，仍属于后续 UX 合同，本检查点不冻结其 App 交互。

因此，“已有受保护用户文字”不自动等于所有 required visible surfaces 均已满足。对 Chapter Title，D2f 已确认：当前非空、合同有效的 protected user Title 满足该 visible Title surface，且 generated Title 不再并排生成或展示；用户明确清空 Title 时，AI 不自动复活，但无 Title 是否满足 Production requiredness 仍由已暂缓的 D2e 决定。其他 surface 只有 presentation contract 明确返回 `SATISFIES_REQUIRED_VISIBLE_SURFACE` 才算完成；返回 `DOES_NOT_SATISFY_REQUIRED_VISIBLE_SURFACE` 时仍需生成相应 AI surface；尚未确定则保持 `PRESENTATION_POLICY_UNRESOLVED`，不能由实现默认选择。

对 Chapter Title，D2f 已建立“只有明确恢复操作才允许重新显示 AI Title”的语义合同；具体按钮、文案和交互位置仍属于 App 设计。Story／Note 等其他 surface 若未来提供用户主动“重新生成/恢复 AI 文案”的操作，该明确指令必须进入单独的 user-authorized rewrite 路径；它不属于后台 Sync 的自动改写，也不能由 C3a 擅自假设该交互已经存在。

### 22.9 案例交叉检查

#### 案例 A｜新增相似古建筑

上一 Preview：

~~~text
Title  古镇漫步
Story  上午走在古镇街巷里，牌坊、木雕和古建筑屋檐，让这段路多了几分旧城气息。
~~~

后续 Sync 又出现两栋相似古建筑，但 stable identity、active media core 与 Story Claims 均未改变。结果：Title/Story 均 `TEXT_RETAIN`，不能仅因为新模型能写出另一句而改文案。

#### 案例 B｜河岸形成材料性收束

后续可靠时间线与 Continuity Evidence 表明，古街漫步最后明确走到河岸；河岸也进入 active media，并让 Chapter 从“建筑浏览”形成“街巷到水边”的真实收束。

~~~text
Title  古镇漫步                         → TEXT_RETAIN
Story  上午从古镇街巷走到河岸，牌坊、木雕和水边的光影，让这段路有了自然的收束。
                                          → TEXT_PATCH or TEXT_REBUILD
~~~

只有“从街巷走到河岸”和 closure 均有已验证 Evidence 时才能这样修改；若河岸只是又一个漂亮但外围的画面，则仍 `TEXT_RETAIN`。

#### 案例 C｜可靠地点精确化

上一 Title 为“古镇漫步”，新 GPS/用户确认把地点可靠精确为周庄：

~~~text
当天只有这一段古镇经历、旧 Title 仍清楚
  Title  古镇漫步                       TEXT_RETAIN

同日另有一段古镇 Chapter，形成真实识别冲突
  Title  古镇漫步 → 周庄古镇漫步         TEXT_PATCH

Story 若原文没有错误且仍独立可理解       TEXT_RETAIN
~~~

exact fact 本身不自动覆盖 continuity；具体材料性门见 D2d。也不能为了让两处都出现“周庄”而同步重写 Story。

#### 案例 D｜木雕识别纠错

旧 Story 写“屋檐下的木雕”，后来合法 Evidence 证明它是彩绘木板。旧事实已错误，必须删除或改正相应 span：`TEXT_PATCH`；若“木雕”同时承担整个 core identity，则进入 `TEXT_REBUILD`。事实纠错优先于连续性。

#### 案例 E｜Preview 进入 Final

Finalization 只确认原 membership/media/text，未增加材料事实，也未改变 active projection。Title/Story 精确复用：`TEXT_RETAIN`。不产生“Final 版更正式”的自动润色。

#### 案例 F｜唯一支撑素材失效

S10 D1 合法移除唯一支撑“河岸倒影”的媒体：

- “河岸倒影”只是一个可删除 detail：Story `TEXT_PATCH`；
- 它是 Story 唯一 Core：Story `TEXT_REBUILD`；
- 同一 selected Memory 已无安全核心：`TEXT_BLOCK`，当前 Revision HOLD/BLOCK。

#### 案例 G｜用户改过 Title

用户把 AI Title“古镇漫步”改成“和妈妈逛周庄”。后续自动 Sync 不覆盖该文字。若“妈妈/周庄”尚未作为可生成 Fact 验证，AI 也不能反向抄入自己的 Story；用户文字继续按原 provenance 保存。后置 D2f 已确认该非空 user Title 独占可见 Title surface，generated Title 不并排展示；只有明确 `RESTORE_AI_TITLE` 才能恢复当前合法 AI Title。

#### 案例 H｜同一 Aha 增加邻近支持

同一个 `core_peak_event_ref` 未改变，只新增合法 before/after support。若原 Aha 可见文字已能独立表达 peak，则 `TEXT_RETAIN`；只有 support 改变了 peak 的必要理解或 peak identity 时才 patch/rebuild。不能把相邻支持自动扩成小 Chapter。

### 22.10 Invariants、成本与边界

1. 已发布文本默认保留，修改必须有材料变化理由；
2. `TEXT_RETAIN` 复用 exact wording，不做同义改写；
3. Title 的稳定阈值高于 Story；
4. patch 必须保持最小范围，不能借机重写未受影响部分；
5. 事实纠错、identity/core 正确性与 active-media compatibility 高于连续性；
6. 新相似素材、模型换代、风格偏好与 Finalization 本身不触发改写；
7. Time/Tag 的合法独立变化不强迫 prose 改写；
8. 用户原文/用户编辑从不被 AI 静默覆盖；
9. 每个 Revision 产生 immutable、可回放、可比较的 continuity artifact；
10. S11 不撤出、补位、删改媒体或发布临时子集；
11. continuity gate 主要比较既有 Claims、fingerprints 与 span refs，不新增 VLM、上传或媒体理解成本；
12. 只有 `TEXT_PATCH/TEXT_REBUILD` 才需要调用有限 Writer，`TEXT_RETAIN` 可明显降低生成成本与用户可见文案抖动；
13. C3a 本身不冻结 App 上 user/AI 文案的布局、冲突提示或编辑交互；后置 D2f 只补充 Chapter Title 的可见所有权与显式恢复语义，Story／Note 等其他 surface 仍保持开放；
14. C3a 本身不冻结 Aha 的最终文案形态；该形态随后由 C3b1 确认为单一 `MOMENT_LINE`，字符与异常降级形式仍进入 D4。
15. 整体或单 surface 无 prior user-visible generated artifact 时不伪造 `TEXT_RETAIN`，而是进入相应首次生成链；
16. contract invalid 与内容性 `TEXT_BLOCK` 分离；
17. 改变 Claim/relation/group 的 patch 与任意 rebuild 必须重入既有 surface-specific C/B3/D/E 链；plan/Claims 不变且 prior B3 fingerprint 仍有效的 wording-only patch 才可复用 B3、走有界 D/E，Writer始终不能直接改 Claim；
18. required/optional surface 资格来自当前 surface contract，并按 22.2 固定顺序聚合；
19. 受保护用户文字是否满足 required visible surface 由 presentation contract 决定，未决时不默认通过；
20. 有合法 omission permission 的 optional surface failure 不单独触发方案 A 整体 Block；
21. protected surface satisfaction 必须先于 no-prior generated applicability 聚合，已满足的用户文字绝不再次触发 Writer；
22. Claim/group patch 与 rebuild 按 surface/memory type 分流：Chapter 走 C1/C2，Aha Moment Line 的 base Claims 走 C3b2、observable qualifier 与 light-affect permission 走 C3b3，metadata 走各自合同；
23. 同一 peak 下仅新增一个更好的 observable qualifier candidate 不触发改写；若既有 qualifier 失去 Evidence，优先最小删除／替换该限定 span，不借机重写整句。
24. 同一 peak 下新获得 light-affect permission 不触发已发布文本改写；既有 affect span 失去 permission 时优先最小删除并重新经过 D4/E，不借机改写其他事实 wording。

## 23. S11-C3b 输入决策

用户已确认：

> V1 Chapter 保持 `Title + 1–2 句 Story`；Aha 不采用“Title＋Story”双层结构，只输出一条独立、简短的 `Moment Line`。Moment Line 只表达一个 peak，最多带一个有必要的紧邻反应；C3b2 进一步确认可再带 0–1 组独立理解所必需的 minimal local context；C3b3 允许同一句加入 0–1 个有直接 Evidence 的 observable qualifier，并按 28.12 Light-Affect v1.1 允许 0–1 个与事实图分离、由当前动作触发的轻量语气 span；仍不设置独立 Tone/氛围句。Time/Tag 继续作为独立 metadata surface。

## 24. S11-C3b1｜Chapter/Aha 用户可见文字形态分离

**状态：CONFIRMED / LIGHT-AFFECT v1.1 AMENDMENT APPLIED BY 28.12**

### 24.1 所在链路与边界

C3b1 是 Aha surface policy，先于具体 Revision 的 continuity/content planning 被读取。运行路径分为：

~~~text
C3b1 User-visible Text Form Contract

first build
  AhaFacts → Claim Ledger → C3b2 base decision
  → C3b3 emphasis + light-affect decisions + provisional Aha plan
  → B3 composition validation → D4 → E

later Revision
  AhaFacts → Claim Ledger → C3a continuity gate
    ├─ protected Moment Line satisfies current presentation contract
    │  → no generated Writer call
    ├─ no prior generated Moment Line + INITIAL_BUILD_REQUIRED
    │  → C3b2 first base decision → C3b3 emphasis + light-affect decisions/first plan → B3 → D4 → E
    ├─ TEXT_RETAIN → dependency/E revalidation
    ├─ TEXT_PATCH, wording only; plan/Claims unchanged
    │  → bounded D4 rewrite → E
    ├─ TEXT_PATCH with qualifier-only change; base decision still valid
    │  → C3b3 replan → B3 → D4 → E
    ├─ TEXT_PATCH with light-affect-only change; base/qualifier decisions still valid
    │  → C3b3 light-affect replan → B3 → D4 → E
    ├─ TEXT_PATCH with base Claim/relation/group change or TEXT_REBUILD
    │  → C3b2 base replan → C3b3 emphasis + light-affect decisions → B3 → D4 → E
    └─ TEXT_BLOCK / contract invalid / presentation-policy unresolved
       → inherit C3a aggregate HOLD/error/UX gate; no Writer call
~~~

C3b1 只决定 Chapter 与 Aha 的 narrative surface 形态，不重新判断：

- S07–S09 的 Chapter/Aha membership、边界、single-peak selection；
- V1.20 已冻结的 Chapter/Aha narrative independence 与 reservation；
- S10 的 active media、Hero/Supporting/Playback；
- A3/B2 已确认的 `core_peak_event_ref` 与 0–2 upstream adjacent support 上限，以及 B3 的 composition legality；
- App 的卡片布局、字号、换行、动效或入口。

### 24.2 两种 Memory 的输出合同

~~~text
Chapter
  Title
  Story                default 1 sentence, maximum 2
  Time Label           separate metadata surface
  Canonical Tags       separate metadata surface

Aha
  Moment Line          one logical narrative field
  Time Label           separate metadata surface, if current surface contract includes it
  Canonical Tags       separate metadata surface, if current surface contract includes them
  no generated Aha Title
  no separate Aha Story
  no separate Aha Atmosphere/Tone field
~~~

`one logical narrative field` 不等于 App 必须在屏幕上物理显示成一行；窄屏自然换行属于 UI。算法合同的含义是：Aha 只有一个叙事字段，不再制造第二个 Title/Story 层级。

V1 正常输出目标为一个完整自然句，不规划第二句内容槽。最终字符上限、标点、本地化膨胀和异常降级形式留给 S11-D4；C3b1 不用硬字符数反向压缩或删改事实。

### 24.3 为什么 Aha 不使用 Title＋Story

1. Aha 已由单一 `core_peak_event_ref` 定义，额外 Title 容易只是同义复述；
2. Title＋Story 会诱导 Writer补背景、过程和结尾，把 Aha 扩成缩小版 Chapter；
3. 用户扫看 Aha 时，需要先看到“发生了什么”，而不是先读一个分类标题；
4. 单一 Moment Line 更容易维持 Chapter/Aha 的故事独立性；
5. 少一个生成 surface，也减少 Claim 对齐、去重复、翻译和跨 Revision 抖动成本；
6. App 若需要视觉标题，可使用固定 UI label 或产品组件名，但不能由算法临时再生成一个 Aha Title。

### 24.4 Moment Line 的内容责任

Moment Line 必须以同一个 `core_peak_event_ref` 为中心：

~~~text
exactly one PEAK_GROUP
+ 0..1 necessary minimal local context
+ 0..1 immediate reaction/support
+ 0..1 observable emphasis qualifier in the same sentence
+ 0..1 permitted light-affective lexical span in the same sentence
+ no Chapter-wide background
+ no second peak
+ no broad progression or closure
~~~

#### `PEAK_GROUP`｜必需

- 至少一个 `CLAIM_SEMANTIC_SUPPORTED + SURFACE_SUPPORTED + AHA_PEAK_CORE`；
- 所有 core Claims 指向同一 `core_peak_event_ref`；
- 只包含上游 selected peak identity 的 predicate、core arguments 与该 event 自身 visible change；可分离 reaction/result 必须进入 adjacent support，不能重标为 core；
- 必须让用户知道发生了一个什么具体事件、动作或可见变化；
- 不能只写“一个惊喜时刻”“这一刻很特别”等空泛评价；
- Moment Line 自身至少写出 peak 的动作/事件/可见变化，不能只剩“这一刻”“很特别”等指代；C3b2 进一步确认：隐藏 parent Chapter 文字后仍须基本可懂，可结合自己的 active Aha media，且只允许加入 0–1 组确有必要的 minimal local context。

#### Minimal local context｜可选，最多一个

C3b2 已确认的 context 与 immediate support 分开计数：context 只解决“这个 peak 在什么局部场景/活动阶段中才不会含糊”，support 才描述紧邻反应或结果。B2 只把合法 Fact 标为 `AHA_LOCAL_CONTEXT_CANDIDATE`；C3b2 才为 selected candidate 建立每组恰好一个 Atomic Claim 的 minimal-context singleton group。具体 deletion test、own-media co-read 与 parent-Chapter-hidden test 见第 26 节。

#### Immediate reaction/support｜可选，最多一个

只有同时满足以下条件才进入 Moment Line：

1. 来自 A3 合法的 adjacent support group，并已在 B2 得到 `target_surface=AHA_MOMENT_LINE + SURFACE_SUPPORTED + AHA_ADJACENT_SUPPORT`；
2. selected ref 必须是当前 `available_adjacent_support_group_refs[]` 的成员，且属于同一 Revision、active projection 与 `core_peak_event_ref`；
3. 与 peak 紧邻，已有合法 relation support refs，并须在最终纳入前通过 B3；
4. 用于解释 peak 的即时结果、他人可观察反应或最低理解；
5. 删除后会明显损失 peak 的意义或可理解性；
6. 不形成第二个独立事件、后续小故事或 Chapter closure；
7. 不因为 A3 最多允许 0–2 support groups，就强行把两组都写入用户文字。

因此，A3 的“0–2 组可用 adjacent support”是完整事实投影上限；C3b1 的“0–1 组进入 Moment Line”是更窄的用户可见预算，两者不冲突。
C3b1 只定义资格与上限；具体 Revision 在两个合法 support 中选哪一个、或保持 0，由 C3b2 第 26.5 节与 context 联合做确定性评估，并把逐候选结果写入同一 immutable decision。

#### Observable emphasis qualifier｜可选，最多一个

C3b3 已确认：Aha 不生成第二句氛围话，也不拥有独立 `TONE_SPAN`。只有已经在 A3/B2 中形成 `AHA_OBSERVABLE_EMPHASIS_CANDIDATE`、能直接限定某个已选 base Claim 的事实性表达，才可能在同一句中出现，例如视频确实支持的“缓缓淌出”或边界 Evidence 确实支持的“一下子暗了下来”。

该预算默认选择 0、最多 1；它与 context/support 分开计数，但不得创造新的事件、对象、用户心理或价值判断。`惊喜、幸福、难忘、好吃、高光` 不是 observable qualifier；`突然、立刻、慢慢、格外、非常` 也不因常见或更生动就自动合法。具体 evidence gate、删除测试与选择顺序见第 28 节。

#### Light affective framing｜可选，最多一个，非事实许可

28.12 Light-Affect v1.1 允许同一 Moment Line 使用 0–1 个由当前动作触发的轻量语气 span。它不进入 Atomic Claim 或 relation graph，不能代替 peak/context/support/observable qualifier，也不恢复独立 Tone／Atmosphere surface。

当前中文初始范围只包含 versioned companion-animal action classes，例如动作与低风险场景确实相容时的`调皮地／活泼地`。物种类别本身不够；用户／人物内心、意图、关系、长期性格、伤害、冲突与群体情绪都不允许。具体 permission artifact、B3/D4/E 分工与案例见 28.12。

### 24.5 Moment Line 不是什么

#### 不是标题

不推荐：

> 古镇里的甜品时刻

它只给主题，没有说发生了什么。

#### 不是 Chapter 摘要

不允许：

> 逛完古镇后走进奶茶店，点了甜品，吃完又继续去了河边。

它包含背景、过程和后续，已经是一个小 Chapter。

#### 不是情绪推断

不允许：

> 这一口甜品带来了满满的幸福和惊喜。

“幸福、惊喜、好吃、最喜欢”仍需合法用户确认或同等级 Evidence；Aha 质量高不等于可以推断用户内心。

#### 不是媒体说明书

不推荐：

> 这张照片记录了甜品切开的画面。

它解释素材，不呈现事件，属于与 4.3-D 相同的 meta editorial phrasing。

### 24.6 案例交叉检查

#### 案例 A｜古镇 Chapter＋甜品 Aha

~~~text
Chapter Title
  古镇漫步

Chapter Story
  上午走在古镇街巷里，牌坊、木雕和古建筑屋檐，让这段路多了几分旧城气息。

Aha Moment Line
  甜品切开时，流心从中间淌了出来。
~~~

Aha 不另写“甜品时刻”Title，也不复述古镇游览背景。Chapter 不重新夺回甜品 peak。

#### 案例 B｜Peak＋即时反应

当视频/连续帧与 timing relation 共同支持时：

> 甜品切开时，流心从中间淌了出来，桌边的人随即笑了起来。

前半句是 peak，后半句是一组紧邻可观察反应。“随即”必须有 temporal adjacency Evidence；若笑的时间或对象关系不可靠，就删除后半句，保留 peak-only 版本。

#### 案例 C｜生日 Chapter＋猫 Aha

~~~text
Chapter
  蛋糕旁亮着烛光，几个人围在桌边。

Aha
  猫跳上蛋糕时，桌边有人伸手去拦。
~~~

只有“跳上”和“伸手去拦”的动作、对象与紧邻关系均被验证时才可使用完整句；否则 Aha 降为“猫跳上了蛋糕”。若要写“几个人一起伸手”，还必须额外验证多人主体、同步性和 collective action。吹蜡烛若已属于生日 Chapter 同一故事核心，不能仅因画面精彩又包装成独立 Aha。

#### 案例 D｜陶艺中的独立意外

> 泥坯塌了下去。

只有“同一泥坯＋塌下动作＋突发边界”均成立时，这才是合法 peak。若要增加“刚成形”，还必须证明成形与塌下之间的紧邻时间关系；只有一张变形后的泥坯照片时，不能反推出“突然塌下”。

#### 案例 E｜错误的双层重复

~~~text
Aha Title
  流心时刻

Aha Story
  甜品切开时，流心从中间淌了出来。
~~~

V1 不采用该结构。Title 只是在 Story 前重复一次事件类别，没有增加用户价值。

### 24.7 结构化合同

前置 policy 与 Revision plan 必须拆开，避免让 C3b1 policy 反向依赖尚未产生的 Claim/B3 artifact：

~~~text
AhaNarrativeSurfacePolicy
  surface_policy_ref
  policy_version
  memory_type
    AHA
  narrative_surface
    AHA_MOMENT_LINE
  surface_requiredness
    REQUIRED
  generated_aha_title
    FORBIDDEN
  separate_aha_story
    FORBIDDEN
  normal_sentence_target
    ONE_COMPLETE_SENTENCE
  second_sentence_content_slot
    NOT_PLANNED
  peak_group_required
    true
  upstream_support_group_budget_ref
    A3_B2_MAX_2
  visible_support_group_budget
    min = 0
    max = 1
  visible_minimal_local_context_group_budget
    min = 0
    max = 1
  visible_observable_emphasis_budget
    min = 0
    max = 1
  visible_light_affective_framing_permission_budget
    min = 0
    max = 1
  separate_aha_atmosphere_surface
    FORBIDDEN
  nonfactual_tone_permission_for_generated_aha
    FORBIDDEN
  observable_emphasis_policy
    MAX_ONE_WHEN_GROUNDED_AND_SELECTED_BY_C3B3
  light_affective_framing_policy
    MAX_ONE_PERMISSION_WHEN_ACTION_TRIGGERED_BY_C3B3_LIGHT_AFFECT_V1_1
  unplanned_nonfactual_tone_policy
    FORBIDDEN
  parent_chapter_narrative_dependency
    FORBIDDEN
  own_active_aha_media_coread
    ALLOWED
  chapter_wide_narrative_background_allowed
    false
  minimal_standalone_context_policy
    MAX_ONE_WHEN_NECESSARY_BY_C3B2
  second_peak_allowed
    false
  metadata_surfaces
    OWNED_SEPARATELY_BY_CURRENT_SURFACE_CONTRACT
  policy_state
    AHA_SURFACE_POLICY_READY
    | AHA_SURFACE_POLICY_CONTRACT_INVALID
  surface_policy_fingerprint
  construction_audit

AhaNarrativeSurfacePlan
  selected_memory_ref
  stable_memory_id
  revision_ref
  surface_policy_ref
  plan_artifact_phase
    PROVISIONAL
    | B3_VALIDATED
  parent_provisional_plan_ref?
  core_peak_event_ref
  active_projection_fingerprint
  claim_ledger_ref
  peak_core_claim_refs[]
  available_adjacent_support_group_refs[0..2]
  selected_visible_adjacent_support_group_refs[0..1]
  omitted_adjacent_support_group_refs[]
  support_omission_reason_codes[]
  visible_support_subset_check
  available_minimal_local_context_group_refs[]
  selected_minimal_local_context_group_refs[0..1]
  omitted_minimal_local_context_group_refs[]
  local_context_omission_reason_codes[]
  selected_local_context_subset_check
  standalone_context_decision_ref
  available_observable_emphasis_qualifier_refs[]
  selected_observable_emphasis_qualifier_refs[0..1]
  omitted_observable_emphasis_qualifier_refs[]
  observable_emphasis_omission_reason_codes[]
  selected_observable_emphasis_subset_check
  observable_emphasis_decision_ref
  selected_light_affective_framing_permission_refs[0..1]
  omitted_light_affective_framing_permission_refs[]
  light_affective_framing_omission_reason_codes[]
  selected_light_affective_framing_permission_count_check
  light_affective_framing_decision_ref
  light_affective_framing_policy_version
  light_affective_framing_fingerprint
  provisional_composition_group_ref
  provisional_composition_group_fingerprint
  b3_composition_decision_ref?
  b3_entry_allowed
  narrative_independence_check
  chapter_reservation_check
  plan_state
    AHA_SURFACE_PLAN_PROVISIONAL_PENDING_B3
    | AHA_SURFACE_PLAN_COMPOSABLE
    | AHA_SURFACE_PLAN_REPLAN_REQUIRED
    | AHA_SURFACE_PLAN_BLOCKED
    | AHA_SURFACE_PLAN_CONTRACT_INVALID
  policy_versions
  surface_plan_fingerprint
  construction_audit
~~~

`AhaNarrativeSurfacePolicy` 是 C3a/C3b2/C3b3/B3 的前置、versioned 输入，不包含 selected Memory、Revision、Claim Ledger 或 composition group。`AhaNarrativeSurfacePlan.available_adjacent_support_group_refs[]` 只能从当前 Claim Ledger 中同 Revision/projection/core peak、且已通过 `AHA_MOMENT_LINE + SURFACE_SUPPORTED + AHA_ADJACENT_SUPPORT` 的 groups 确定性导出。Local context 在 B2 仍是无 group ref 的 `SURFACE_SUPPORTED + AHA_LOCAL_CONTEXT_CANDIDATE` Claim；C3b2 才按已冻结 identity tuple 为每个 eligible candidate 建立 immutable singleton group，并形成 `available_minimal_local_context_group_refs[]`。C3b3 只从同 scope 的 `SURFACE_SUPPORTED + AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 中形成 `available_observable_emphasis_qualifier_refs[]`，并验证 qualifier target 已属于 C3b2 的 exact base selection；28.12 light-affect decision 则从 exact base action/entity semantics 与 versioned lexicon 产生 0–1 permission，并保持在 Claim/relation graph 外。三类事实 selected refs 必须分别为相应 available refs 的子集，affect permission 必须精确引用 decision/target/class/policy。该 Plan 由 C3b3 针对具体 Revision 产生 provisional artifact；B3 验证后产生引用该 provisional artifact 的新 immutable plan/decision，不原地补写。实际 wording 仍须经过 D，最终事实 span/implicit-claim 与 light-affect span 验证仍须经过 E。

Phase/state 可达性固定为：

~~~text
PROVISIONAL
  → AHA_SURFACE_PLAN_PROVISIONAL_PENDING_B3 only

B3_VALIDATED
  → AHA_SURFACE_PLAN_COMPOSABLE
  | AHA_SURFACE_PLAN_REPLAN_REQUIRED
  | AHA_SURFACE_PLAN_BLOCKED
  | AHA_SURFACE_PLAN_CONTRACT_INVALID
~~~

只有 C3b2 Ready decision 允许进入 C3b3；C3b2 本身不再创建 plan。随后 observable-emphasis decision 必须为正常 0／1 终态，light-affect decision 也必须为 `NO_LIGHT_AFFECTIVE_FRAMING_PERMISSION / ONE_LIGHT_AFFECTIVE_FRAMING_PERMISSION`，且共同满足 `b3_entry_allowed=true`，C3b3 才创建 `PROVISIONAL` plan；C3b2 的 Replan/Blocked/Contract Invalid，以及任一 C3b3 Contract Invalid 都不创建 plan artifact。`PROVISIONAL` plan 的 `parent_provisional_plan_ref` 与 `b3_composition_decision_ref` 必须为空。B3 对 exact provisional plan 完成评估后，无论成功或失败，都创建一个 `B3_VALIDATED` immutable audit plan，保存 `parent_provisional_plan_ref + b3_composition_decision_ref`；只有 `AHA_SURFACE_PLAN_COMPOSABLE` 可以进入 D4，另外三种状态均不得进入 Writer。B3 不能原地补写 provisional artifact。

### 24.8 Cross-Revision、成本与 Invariants

1. 已发布 Moment Line 进入 C3a；同一 peak 新增弱 support 时默认 `TEXT_RETAIN`；
2. peak identity 不变时，不因 Writer升级或措辞更漂亮而重写；
3. `AHA_MOMENT_LINE` 恰好围绕一个 `core_peak_event_ref`；
4. A3/B2 可提供最多两组 upstream support，用户可见计划最多消费一组必要 immediate reaction/support；C3b2 最多消费一组必要 minimal local context；C3b3 最多消费一个 observable qualifier，并可提供一个 28.12 light-affect permission；三类事实 selected 必须分别是同 Revision/projection/core peak 下的合法候选子集，affect permission 必须通过 exact target/action/scope/risk gate；
5. context、support 与 observable qualifier role 分离、互不重复，都不升级为第二 peak、后续故事或 Chapter closure；light affect 不占 Claim role，也不能承担任何事实或 relation；
6. Aha 不生成独立 Title、不生成第二个 Story field，也不生成独立 Atmosphere/Tone field；
7. Time/Tag 是独立 metadata surface，不占用 Moment Line 的 peak 预算；
8. Moment Line 不依赖无证据用户情绪、关系、意图或价值判断制造“高光感”；`NON_FACTUAL_TONE_ONLY` 仍禁用，只有 28.12 exact permission 的 light-affective lexical span 例外；
9. C3b1 不改变 Chapter 的 Title＋1–2 句 Story 合同；
10. C3b1 不改变 S09/S10 选择与媒体，不调用 VLM、不重新上传素材；
11. 单字段结构减少一次标题生成、跨 surface 去重与后续翻译验证成本；
12. C3b1 不冻结字符数、UI 物理行数或 App 展示组件；
13. 前置 `AhaNarrativeSurfacePolicy`、C3b2 base decision、C3b3 emphasis/light-affect decisions 与后置 Revision-specific plan 分离，不形成 artifact 生命周期循环；
14. provisional plan 的唯一 producer 是 C3b3；C3b2 只产生 base support/context decision，B3 只验证 exact plan；
15. A2/B2/B3/C3a 对该 narrative surface 统一使用 `AHA_MOMENT_LINE`，V1 generated Aha Title 或独立 Tone 不得作为旁路；28.12 permission 只能在该 Moment Line 内实现。

## 25. 下一检查点

进入 S11-C3b2：Aha Standalone Context Budget。需要决定：Aha 在脱离所属 Chapter、单独出现在 Aha 列表或卡片中时，Moment Line 是否必须独立说清楚“发生了什么”，以及允许补入多少最小场景上下文，才能既不含糊、又不扩成小 Chapter。

## 26. S11-C3b2｜Aha Standalone Context Budget

**状态：CONFIRMED**

### 26.1 用户确认的产品定义

V1 锁定：

> Aha 隐藏所属 Chapter 的 Title、Story 和其他 Chapter 内容后，仍应让用户基本看懂发生了什么；允许结合这条 Aha 自己的 active media 阅读。Moment Line 必须写出具体 peak 事件，最多只补一组确有必要的局部背景，不得搬入完整 Chapter 背景。

本节只决定 `AHA_MOMENT_LINE` 的 standalone context budget，不重新判断：

- Aha 是否被选择、属于哪个 Chapter、是否满足 narrative independence；
- `core_peak_event_ref`、Aha active media、时间边界与 adjacent support inventory；
- Chapter/Aha membership、reservation、Final media 或 HQ materialization；
- App 卡片布局、物理行数、通知文案或无媒体展示形式；
- C3b3 是否选择 observable qualifier、是否提供 28.12 light-affect permission，以及最终 provisional plan 的生成；
- D4 的最终字符上限、标点和本地化长度。

C3b2 仍处于 semantic Content Plan 层：它检查 base planned Claims、arguments、referents 与 presentation dependencies，不在这里生成最终句子，也不选择强调限定或 light-affect permission。下文案例文字只用于说明合同；C3b3 在 base decision 之后决定 0–1 observable qualifier、0–1 light-affect permission并形成 provisional plan，D4 才产生真实措辞，E 必须用实际 spans 重新执行 explicit-event、裸指代、Chapter dependency、media-dependency、qualifier-support 与 affect-permission checks。

### 26.2 概念释义

#### Standalone｜脱离 Chapter 仍基本可懂

这里不是要求 Aha 文案像一篇完整小故事，而是要求把 parent Chapter 隐藏后，用户仍能回答：

> 这条 Aha 具体发生了什么？

它不要求交代当天路线、此前准备、之后去了哪里，也不要求解释“为什么这是一次重要旅程”。

#### Own-media co-read｜可结合 Aha 自己的素材阅读

V1 standalone 的正式测试场景是：

~~~text
parent Chapter Title / Story / other Chapter media = hidden
this Aha active media                         = visible and current
Aha Moment Line                              = visible
~~~

自己的素材可以帮助用户确认“是哪一个泥坯、哪一块甜品、哪只猫”这类实例级细节；但不能代替文字中的核心动作/变化，也不能为不受支持的地点、人物关系、情绪或因果补证。

#### Minimal local context｜最小局部背景

它是一项围绕同一 peak 的局部场景 Fact，例如一个必要的活动阶段或可信地点。它只负责解除含糊，不负责补全 Chapter 故事。

#### Removal test｜删除测试

暂时删除候选 context，重新执行 parent-Chapter-hidden test：

- 事件、指代和 peak identity 仍清楚：context 是冗余，删除；
- 删除后发生了什么或这个 peak 的局部含义变得材料性含糊：可以保留；
- 即使加入一项 context 仍无法基本看懂：若同一 peak 尚有未尝试、严格更简单/安全的辅助组合则进入 Replan；组合耗尽或 core 本身不完整则 Block，不能再加第二项背景。

### 26.3 三类 base 内容必须分开计数

~~~text
PEAK_GROUP                         exactly 1
MINIMAL_LOCAL_CONTEXT_GROUP       0..1
IMMEDIATE_REACTION_SUPPORT_GROUP  0..1
~~~

C3b2 只拥有以上三类 base 内容。C3b3 的 `OBSERVABLE_EMPHASIS_QUALIFIER 0..1` 使用独立预算，既不能在本节冒充 peak/context/support，也不能反过来改变本节已经确定的 base selection。

#### Peak core arguments｜不占 context 名额

把事件本身说完整所必需的主体、动作、对象和可见变化属于 `PEAK_GROUP`。

例：

> 泥坯塌了下去。

“泥坯”不是附加背景，而是“什么塌了”的 core argument。不能把它省成“它塌了”，再声称已经遵守零 context。

#### Minimal local context｜最多一组，每组一个 Atomic Claim

合法类型只包括：

~~~text
LOCAL_ACTIVITY_PHASE       例如“拉坯时”
TRUSTED_LOCAL_PLACE        例如“奶茶店里”
LOCAL_SCENE_STATE          例如与 peak 同时成立的局部场景状态
USER_CONFIRMED_LOCAL_ROLE  仅在用户已确认且理解确实需要时
~~~

每组必须恰好包含一个底层已通过 `AHA_LOCAL_CONTEXT_CANDIDATE` surface decision 的 Atomic Claim。B2 不创建该 group；C3b2 才按固定 identity tuple 建立 immutable singleton group。若一句背景同时断言“和朋友在奶茶店庆祝生日”，内部至少包含人物关系、地点和活动三个可独立为真的命题，不能伪装成一个 context group。

如果人物/对象本身执行 peak 动作，或缺少它就不知道“谁／什么发生了变化”，它属于 `PEAK_GROUP` core argument，而不是 `USER_CONFIRMED_LOCAL_ROLE` context。Context 名额不能用来转移本应写完整的 peak 主体。

默认选择数量是 0，而不是 1。只有 removal test 通过才使用该名额。

#### Immediate reaction/support｜独立预算，最多一组

它继续遵守 C3b1：只描述 peak 的紧邻、已验证反应或结果，例如“桌边的人随即笑了起来”。它使用 `AHA_ADJACENT_SUPPORT`，不能冒充 context；context 也不能冒充 support 来绕过各自上限。

两类 base 辅助信息在结构上可以同时存在，但必须分别必要、分别 grounded，并仍保持一个 peak 和一个自然句。若 D4 发现完整计划的长度/自然度预算无法同时承载，它只能返回 replan，不能自行删除已验证 Claim；若计划含 qualifier，先返回 C3b3 省略 qualifier；仍失败时才返回 C3b2 产生省略 support 的新 base decision，随后重新经过 C3b3 与 B3：

~~~text
explicit PEAK_GROUP
→ necessary MINIMAL_LOCAL_CONTEXT
→ optional IMMEDIATE_REACTION_SUPPORT
→ optional OBSERVABLE_EMPHASIS_QUALIFIER
~~~

不能为了保留更精彩的反应，删掉使事件独立可懂所必需的 context。
如果连 `PEAK_GROUP + necessary context` 都无法在 D4 合同内安全表达，只能尝试不改变 Claims 的有界 wording rewrite；仍失败则 Block，不能删除必要 context 后发布含糊版本。

### 26.4 Own media 能做什么、不能做什么

#### 可以

1. 让用户看出文字中的“泥坯”具体是哪一个；
2. 帮助确认场景中可见对象与文字属于同一个 active Aha；
3. 在 event predicate 已经写清时，减少不必要的颜色、外观和位置复述；
4. 使一句简洁 Moment Line 保持自然，而不必写成媒体说明书。

#### 不可以

1. 让“这一刻很特别”“它变成这样了”之类空泛文案通过；
2. 让用户从画面自行补出文字没有写明的核心动作；
3. 用媒体猜测“朋友、家人、喜欢、惊喜、最好吃”等未确认信息；
4. 用 parent Chapter 的 Story 或其他媒体解释当前 Aha；
5. 将过期/替换前的 Aha media 当成当前 context；
6. 因为画面能看懂，就省略所有可追溯的 core Claim。

本合同把 `AHA_CARD_WITH_OWN_ACTIVE_MEDIA` 作为 V1 hard test profile。`TEXT_ONLY_PORTABILITY` 只记录诊断状态，不作为本节 hard gate：若未来通知、搜索结果或其他入口不显示媒体，必须建立对应 presentation contract，不能默认复用一个依赖媒体的句子。

### 26.5 Support 与 Context 的联合确定性选择

C3b1 已定义 adjacent support 的资格和 0–1 用户可见上限。为避免出现“context 有生产者、support 没有生产者”，C3b2 必须联合完成两类 base 辅助信息的候选评估与最终选择，并形成 immutable `AhaStandaloneContextDecision`；C3b3 只能在该 exact base selection 上增加 0–1 observable qualifier、提供 0–1 light-affect permission并生成 `AhaNarrativeSurfacePlan`，不能替 C3b2 随机改选 support/context。

每个 selected Aha 依次执行：

1. 验证 current Revision、`core_peak_event_ref`、active projection 与唯一 own active Aha media；
2. 验证并重放 current immutable B2 `aha_role_partition_check`，确认 peak/support/context candidate 没有 semantic-equivalent role laundering；C3b2 不重新分类 role，不一致直接 `LOCAL_CONTEXT_CONTRACT_INVALID`；
3. 从当前 Claim Ledger 收集同 scope 的 0–2 个 `SURFACE_SUPPORTED + AHA_ADJACENT_SUPPORT` groups；
4. 从当前 AhaFacts/B0/B2 收集 `SURFACE_SUPPORTED + AHA_LOCAL_CONTEXT_CANDIDATE` Claims，不读取 parent Chapter prose；C3b2 为每项 eligible Claim 确定性建立一个 immutable singleton candidate group；
5. 对每个 support group 独立检查 same-peak、temporal adjacency、observable reaction/result、第二事件风险、material deletion 与 media alignment，并产生可回放 evaluation；
6. support 默认选 0。只有对 peak 意义/即时结果有材料增量的 candidate 才进入 ranked set，最多 provisional 选择 1 组；
7. 以 `PEAK_GROUP + provisional selected support` 作为无 context baseline，运行 `PARENT_CHAPTER_HIDDEN_TEST`；support 不能修复缺失的 core argument，也不能冒充 local context；
8. baseline 已基本可懂时确定 `NO_LOCAL_CONTEXT_NEEDED`；若仍有局部材料性含糊，则逐项比较每个 context group 的 `without_context` 与 `with_context` 结果，最多选择 1 组能以最小语义解除含糊的 candidate；
9. 对 provisional support/context 做 semantic distinctness 与 joint-complexity check。若两者语义重复，必要 standalone context 优先，support 以明确 reason code 省略；若是 role laundering，则 Contract Invalid，而不是普通去重；
10. 若需要两个以上 context 才能说清、任何单项 context 都无效，或 core arguments 本身缺失，不能借用 Chapter 背景、生成第二句或换 peak；
11. Ready attempt 只形成 `c3b3_entry_allowed=true` 的 base decision，其中 support/context final selected refs 已冻结；C3b2 不创建 provisional plan；
12. C3b3 对 exact Ready decision 选择 0–1 observable qualifier、提供 0–1 light-affect permission并生成 provisional `AhaNarrativeSurfacePlan`，再由 B3 验证 role、subset、attachments、relations、组合真值与 affect permission compatibility；
13. D4 只对 B3-validated plan 写一个 Moment Line，E 再对真实 spans、代词、限定词和隐含关系做最终检查。

#### Adjacent support 的确定性排序

多个 support 都合法时，依次比较：

~~~text
material contribution to understanding the selected peak
→ tighter verified temporal adjacency to the peak
→ stronger direct evidence and active-media alignment
→ fewer relation dependencies
→ narrower semantic scope
→ stable deterministic ref order as final tie-break only
~~~

“画面更好看”“反应更热闹”或 Writer偏好不进入排序。完全没有材料增量时保持 0 support。

#### Local context 的确定性排序

多个单项 context 都能解除同一含糊时，依次比较：

~~~text
resolves ambiguity within the already-fixed peak identity or event scope; never changes core_peak_event_ref
→ resolves necessary local activity phase
→ resolves necessary trusted local place
→ narrower semantic scope
→ fewer relation dependencies
→ stable deterministic ref order as final tie-break only
~~~

final tie-break 只解决完全等价候选的确定性，不代表 ref 更小的辅助信息更重要。

#### 有界组合预算与状态边界

设 `S` 为合法 upstream support group 数，按 A3 合同 `0 ≤ S ≤ 2`；`C` 为当前 AhaFacts 中合法 context singleton candidate 数。C3b2 只允许枚举：

~~~text
support choice ∈ {none, one of S}
context choice ∈ {none, one of C}
maximum unique auxiliary combinations = (S + 1) × (C + 1)
~~~

每个 semantic combination fingerprint 最多尝试一次。初始目标唯一确定为：先通过 material gate 与 support ranking 选择最高优先级 support（没有合格项才为 none），再针对 `peak + preferred support` 选择最低必要的 context（不需要则为 none）。不能因为 `(none, none)` 信息最少，就跳过一个已经通过 material gate 的首选 support。

初始组合失败后的顺序也唯一：先尝试同一辅助项数量下、按既有 rank 次序下一个**可证明更安全**的 support/context candidate；然后才尝试删除非必要 support 的严格简化组合，并为新的 support choice 重算 context necessity。任何 fallback 都不得删除仍为 standalone 所必需的 context，也不得改变 `core_peak_event_ref`。

每个 attempt 必须以该 attempt 自己的 support choice 重算 `baseline_without_context` 与全部 context necessity evaluations；不能在删除/替换 support 后复用上一 attempt 的 context removal 结论，否则可能把本来需要的 context 错误省略。

- `NO_LOCAL_CONTEXT_NEEDED / ONE_LOCAL_CONTEXT_REQUIRED`：所有 base 计划级检查已通过；final context 分别为 0/1，final support 为 0/1，且与该 attempt 的 provisional selections 相同；设置 `c3b3_entry_allowed=true`，进入 C3b3，但尚不产生 plan；
- `LOCAL_CONTEXT_REPLAN_REQUIRED`：当前组合失败，但同一固定 peak 下仍存在至少一个未尝试、严格更简单或可证明更安全的合法组合；provisional arrays 保存失败组合，两个 final selected arrays 必须为空、`c3b3_entry_allowed=false`，不进入 C3b3，选择下一个唯一 fingerprint；
- `LOCAL_CONTEXT_BLOCKED`：缺少合法 core 组合、单项 context 均不能解除含糊，或全部 `(S + 1) × (C + 1)` 组合已耗尽；provisional arrays 可保存最后一个失败组合用于 audit，但两个 final selected arrays 必须为空、`c3b3_entry_allowed=false`，不进入 C3b3/B3，按方案 A 聚合 Block；
- `LOCAL_CONTEXT_CONTRACT_INVALID`：own active media ref 缓存/lineage/fingerprint、Revision、Claim、role-partition 或 group identity 损坏；provisional/final selected arrays 全为空、`c3b3_entry_allowed=false`，不进入 C3b3/B3，走工程诊断。

字段矩阵冻结为：

~~~text
Decision state                         provisional support/context   final support/context   c3b3_entry_allowed
NO_LOCAL_CONTEXT_NEEDED                0..1 / 0                       same as provisional      true
ONE_LOCAL_CONTEXT_REQUIRED             0..1 / 1                       same as provisional      true
LOCAL_CONTEXT_REPLAN_REQUIRED          attempted 0..1 / 0..1          empty / empty            false
LOCAL_CONTEXT_BLOCKED                  last attempt 0..1 / 0..1       empty / empty            false
LOCAL_CONTEXT_CONTRACT_INVALID         empty / empty                  empty / empty            false
~~~

Blocked 若在形成任何合法 attempt 前就发现 core 不完整，provisional arrays 也为空；表中的 “last attempt” 只用于确实已有失败组合时的 audit snapshot。

B3 若返回涉及 peak/support/context base 组合的 `RECOMPOSE_REQUIRED`，只能在对应失败 `B3_VALIDATED` audit plan 已创建后，创建一个新的 C3b2 immutable attempt；该 attempt 必须使用 `B3_RECOMPOSE_REQUIRED` trigger，并回链 parent context decision、触发的 B3 composition decision 与 failed validated plan。随后按“同复杂度但可证明更安全 → 严格简化”的唯一剩余顺序选择尚未尝试的 base combination；Ready 后仍必须重新经过 C3b3 才能产生新 plan。若 B3 失败只涉及 optional qualifier，则不消耗 C3b2 combination budget，直接由 C3b3 以同一 Ready base decision 严格简化。若无剩余 base combination，直接 Block。输入引用损坏与内容不足因此始终分开，工程合同损坏不能解释成“这个 Aha 不够好”。

### 26.6 Standalone tests

每条计划必须通过：

1. **Planned explicit peak predicate**：语义计划中有可实现为具体动作、事件或可见变化的 peak Claim；
2. **Planned core-argument completeness**：最低主体/对象/动作与 planned referent 均已提供，不计划依赖裸指代；
3. **Parent-Chapter-hidden test**：不看 Chapter Title/Story/其他媒体仍基本可懂；
4. **Own-media freshness/alignment**：只结合 current active Aha media；
5. **Context necessity removal test**：selected context 删除后确有材料性理解损失；
6. **Single-context atomicity**：最多一组且恰好一个 Atomic Claim；
7. **Aha-scope provenance**：context 来自当前 AhaFacts/Claim Ledger，而非 parent prose；
8. **Support candidate replayability**：0–2 个 support 均有独立 evaluation、rank inputs 与 omission reason；
9. **Support/context selection completeness**：final selected refs 与同一 immutable decision/plan 一致；
10. **Role partition/laundering**：peak、reaction/result、local context 不换 role 或用同义/parent-subclaim 重复；
11. **Context/support distinctness**：同一 Claim/group 不重复占两个预算；
12. **No Chapter background expansion**：无路线、准备、后续、整段活动概括或第二 peak；
13. **Relation truth**：`在……时、刚、随即、又` 等关系词各有独立 Evidence；
14. **Reservation/media alignment**：没有侵占 parent Chapter reserved core，也没有超出 active Aha media/Fact scope；
15. **No unsupported user-state**：不靠推断情绪、关系或价值判断使 Aha 显得精彩。

`Standalone` 不等于 text-only 自足。合法状态分为：

~~~text
TEXT_SELF_SUFFICIENT
OWN_MEDIA_ASSISTED_BUT_EVENT_EXPLICIT
TEXT_UNDERSPECIFIED_EVEN_WITH_MEDIA   # Block / replan
~~~

第二种允许媒体帮助识别实例，但 event predicate 与 core arguments 仍必须写明；第三种不能发布。

### 26.7 结构化合同

~~~text
AhaStandaloneContextDecision
  selected_memory_ref
  stable_memory_id
  revision_ref
  surface_policy_ref
  core_peak_event_ref
  active_projection_fingerprint
  claim_ledger_ref
  presentation_test_profile
    AHA_CARD_WITH_OWN_ACTIVE_MEDIA
  parent_chapter_inputs_hidden[]
    TITLE
    STORY
    OTHER_CHAPTER_MEDIA
  own_active_aha_media_ref
  own_active_aha_media_fingerprint
  peak_core_claim_refs[]
  planned_explicit_peak_predicate_check
  planned_core_argument_completeness_check
  aha_role_partition_check
  upstream_adjacent_support_group_refs[0..2]
  adjacent_support_candidate_evaluations[]
    support_group_ref
    same_peak_scope_check
    temporal_adjacency_check
    observable_reaction_or_result_check
    second_event_risk_check
    material_deletion_test
    active_media_alignment_check
    rank_inputs
    candidate_decision
  ranked_adjacent_support_group_refs[]
  provisional_selected_adjacent_support_group_refs[0..1]
  final_selected_adjacent_support_group_refs[0..1]
  omitted_adjacent_support_group_refs[]
  support_omission_reason_codes[]
  baseline_without_local_context_plan_check
  available_minimal_local_context_groups[]
    group_ref
    atomic_context_claim_ref
    context_type
    core_peak_event_ref
    source_fact_refs[]
    relation_dependency_refs[]
    surface_decision_ref
    singleton_group_identity_fingerprint
  candidate_context_evaluations[]
    group_ref
    baseline_without_context_check
    with_context_check
    necessity_removal_result
    chapter_background_expansion_check
    relation_truth_check
    rank_inputs
    candidate_decision
  ranked_minimal_local_context_group_refs[]
  provisional_selected_minimal_local_context_group_refs[0..1]
  final_selected_minimal_local_context_group_refs[0..1]
  omitted_minimal_local_context_group_refs[]
  local_context_omission_reason_codes[]
  selected_context_necessity_check
  single_context_atomicity_check
  selected_context_subset_check
  context_support_distinctness_check
  context_support_joint_selection_check
  chapter_background_exclusion_check
  reservation_check
  planned_own_media_dependency_class
    TEXT_SELF_SUFFICIENT
    OWN_MEDIA_ASSISTED_BUT_EVENT_EXPLICIT
    TEXT_UNDERSPECIFIED_EVEN_WITH_MEDIA
  planned_text_only_portability_diagnostic
    TEXT_ONLY_PORTABLE
    TEXT_ONLY_AMBIGUOUS_SEPARATE_CONTRACT_REQUIRED
    NOT_EVALUATED
  replan_trigger_kind
    INITIAL
    | C3B2_INTERNAL
    | B3_RECOMPOSE_REQUIRED
  replan_parent_decision_ref?
  replan_trigger_b3_composition_decision_ref?
  replan_trigger_b3_validated_plan_ref?
  replan_trigger_b3_recompose_owner_check?
  replan_trigger_lineage_check
  attempt_index
  attempted_auxiliary_combination_fingerprint
  attempted_auxiliary_combination_fingerprints[]
  remaining_auxiliary_combination_fingerprints[]
  combination_budget_check
  c3b3_entry_allowed
  decision
    NO_LOCAL_CONTEXT_NEEDED
    ONE_LOCAL_CONTEXT_REQUIRED
    LOCAL_CONTEXT_REPLAN_REQUIRED
    LOCAL_CONTEXT_BLOCKED
    LOCAL_CONTEXT_CONTRACT_INVALID
  reason_codes[]
  policy_versions
  standalone_context_fingerprint
  construction_audit
~~~

`AhaStandaloneContextDecision` 是 Revision-specific immutable artifact，也是在 C3b2 内联合确定 visible adjacent support 与 minimal local context 的唯一决策源。两个 `candidate_*_evaluations[]` 保存逐候选删除测试、关系检查与 rank inputs，provisional/final support 与 context snapshots 使 `context_support_distinctness_check` 可完整回放，不依赖一个未记录的外部选择。

Retry lineage 固定为：

1. `INITIAL`：三个 replan refs 全为空；
2. `C3B2_INTERNAL`：`replan_parent_decision_ref` 必填，两个 B3 trigger refs 为空；
3. `B3_RECOMPOSE_REQUIRED`：parent Ready decision、触发它的 B3 composition decision 与对应失败 `B3_VALIDATED` plan refs 全部必填，且 `aha_recompose_owner=C3B2_BASE_SELECTION`；
4. `replan_trigger_lineage_check` 必须证明 failed validated plan → exact parent provisional plan → parent context decision，以及 B3 decision 的 `RECOMPOSE_REQUIRED + C3B2_BASE_SELECTION` 状态；
5. 任一 ref 缺失、跨 Revision/projection/policy 或链路不一致为 `LOCAL_CONTEXT_CONTRACT_INVALID`，不能当普通内部 retry。

只有 `NO_LOCAL_CONTEXT_NEEDED / ONE_LOCAL_CONTEXT_REQUIRED` 且 `c3b3_entry_allowed=true`，才允许把该 immutable base decision 送进 C3b3；C3b2 不构造、也不反向引用 provisional `AhaNarrativeSurfacePlan`。Replan/Blocked/Contract Invalid 均不得把半成品 base selection 送进 C3b3/B3。C3b3 产生独立 immutable emphasis decision 与 provisional plan，B3 只验证并产生新的 immutable composition/validated-plan artifact，不回写上游 decisions。D4/E 也分别产生新 artifact，保持完整 lineage。

推荐 reason codes 至少包括：

~~~text
PEAK_EVENT_NOT_EXPLICIT
CORE_ARGUMENT_MISSING
PLANNED_BARE_DEICTIC_REFERENCE
PARENT_CHAPTER_DEPENDENCY
OWN_AHA_MEDIA_STALE_OR_MISSING
AHA_ROLE_LAUNDERING
SUPPORT_NO_MATERIAL_INCREMENT
SUPPORT_SELECTION_INCOMPLETE
SUPPORT_CONTEXT_SEMANTIC_REDUNDANCY
LOCAL_CONTEXT_NOT_NEEDED
LOCAL_CONTEXT_REQUIRED
LOCAL_CONTEXT_COUNT_EXCEEDED
LOCAL_CONTEXT_NOT_ATOMIC
LOCAL_CONTEXT_OUTSIDE_AHA_SCOPE
LOCAL_CONTEXT_NOT_SURFACE_SUPPORTED
LOCAL_CONTEXT_RELATION_UNSUPPORTED
CONTEXT_SUPPORT_ROLE_COLLISION
AUXILIARY_COMBINATION_DUPLICATE
AUXILIARY_COMBINATION_BUDGET_EXHAUSTED
B3_REPLAN_TRIGGER_LINEAGE_INVALID
CHAPTER_BACKGROUND_EXPANSION
TEXT_ONLY_SURFACE_CONTRACT_REQUIRED
~~~

### 26.8 案例交叉检查

#### 案例 A｜古镇 Chapter 中的甜品 Aha

~~~text
Parent Chapter（测试时隐藏）
  上午走在古镇街巷里……

Aha own media
  甜品被切开，流心出现

Moment Line
  甜品切开时，流心从中间淌了出来。
~~~

该句已经说清事件。加入“奶茶店里”虽然真实，也没有通过 necessity removal test；默认删除，不因地点听起来更完整就占用 context。

不允许：

> 逛完古镇走进奶茶店后，甜品切开时流心淌了出来。

“逛完古镇走进奶茶店”搬入 parent Chapter progression，并非局部 standalone context。

#### 案例 B｜陶艺 peak 不需要背景

> 泥坯塌了下去。

“泥坯＋塌下”已经给出 core arguments 与 event predicate。自己的视频帮助用户看出具体是哪一个泥坯，但不能把文字缩成“它塌了”。若要增加“突然”，仍须另有突发边界 Evidence；本案例不默认该限定词成立。

#### 案例 C｜确需一个活动阶段

若同一 Aha 的 Evidence 已验证“正在拉坯”与“同一泥坯此时塌下”的共时关系，而且去掉活动阶段会把 peak 与之后搬动/整理时的塌落混淆，可以写：

> 拉坯时，泥坯塌了下去。

“拉坯时”是唯一 `LOCAL_ACTIVITY_PHASE`；若 active media 与 peak Claim 已足以消除该歧义，就回到案例 B，不为了更生动而保留。

#### 案例 D｜生日 Chapter＋猫 Aha

> 猫跳上了蛋糕。

已经 standalone。不要补：

> 大家正在过生日、准备吹蜡烛时，猫跳上了蛋糕。

前半句包含 parent Chapter 活动、准备阶段和多人范围，既不 atomic，也把 Aha 扩成生日故事摘要。

#### 案例 E｜Context＋即时反应同时存在

只有 activity phase、塌下动作、旁人反应和“随即”关系分别通过时，结构上才允许：

> 拉坯时，泥坯塌了下去，旁边的人随即伸手扶住。

其中“拉坯时”占一组 context，“伸手扶住”占一组 adjacent support。任一项删除后没有材料损失，就不应进入 base decision；C3b3 如再选择 qualifier，仍须单独通过预算。若 D4 发现长度预算不足，先返回 C3b3 省略 qualifier；仍不足时再返回 C3b2，按 peak → necessary context → reaction 的优先级产生省略 support 的新 base decision，随后重新经过 C3b3 与 B3。Writer 不得在句子里静默删项。

#### 案例 F｜Own media 不能拯救裸指代

不允许：

> 它塌了，这一刻很意外。

即使媒体里只有一个泥坯，“它”仍把 core argument 完全交给媒体；“很意外”又可能推断用户状态。安全版本是：

> 泥坯塌了下去。

#### 案例 G｜可信地点也不自动写入

GPS/用户确认能证明 Aha 在奶茶店，只说明“奶茶店里”有 candidate 资格。若：

> 甜品切开时，流心从中间淌了出来。

已经清楚，则地点仍为 `LOCAL_CONTEXT_NOT_NEEDED`。只有地点对区分同一 peak identity 或解除实际歧义具有材料作用时，才可选择；它不能仅用于增添氛围。

#### 案例 H｜Text-only 入口

Aha 卡片在自己的媒体旁显示“泥坯塌了下去”，符合 V1 hard profile。若未来锁屏通知只显示这句话，也可以记录为 `TEXT_ONLY_PORTABLE`。如果另一条合法卡片文案不看媒体仍能知道对象类别与具体事件，但会缺少当前卡片由画面提供的实例级辨认或局部场景信息，则记录 `TEXT_ONLY_AMBIGUOUS_SEPARATE_CONTRACT_REQUIRED`，由未来通知 UX 单独判断是否可复用；它不能缺失 core argument，也不能促使本节擅自加长所有 Aha。

### 26.9 Cross-Revision、失败路径与成本

1. 已发布 Moment Line 若在当前 active media 下仍明确、真实，新增一个地点/context candidate 不触发改写；C3a 默认 `TEXT_RETAIN`；
2. 原句与 current active media 失配，或实例指向/局部语义因此变得材料性含糊时，可在同一 peak 下重新执行 C3b2，再经 C3b3，必要时 `TEXT_PATCH/TEXT_REBUILD`；裸指代是文字自身缺陷，任何 Revision 都不得通过，不能归因于媒体变化；
3. context Claim 失效时删除相应 span；不能保留旧背景，也不能换一个 peak；
4. 当前组合失败但仍有未尝试的合法辅助组合时先产生 `LOCAL_CONTEXT_REPLAN_REQUIRED` attempt；没有单项合法 context 能解除含糊或组合预算耗尽后，required Moment Line 才按方案 A 进入 `TEXT_BLOCK/CONTINUITY_BLOCKED`；S11 不撤出 Aha、不补位；
5. 若产品 retention 合同允许，仍合法的 prior published Revision 可继续展示，不能把失效旧文复制给新 Revision；
6. C3b2 只处理 AhaFacts、Claim Ledger、active-media refs 与有限候选集合，不读取 Raw pixels、不调用 VLM/LLM、不请求上传；
7. 主要新增成本是少量 deterministic graph/subset/removal checks，远低于一次云端视觉推理；
8. context 默认 0，减少 token、翻译、验证与跨 Revision 抖动；
9. text-only portability 只是一次 metadata diagnostic，不为不存在的 UI surface 预生成第二套文案。

### 26.10 Invariants

1. Aha 不依赖 parent Chapter narrative 才能基本看懂；
2. V1 hard profile 允许结合 own current active Aha media，但 core event 必须在文字中明确；
3. `PEAK_GROUP` 恰好一个；subject/object/action 等 core arguments 不占 context 名额；
4. minimal local context 默认 0、最多 1 组、每组恰好一个 Atomic Claim；
5. adjacent support 仍最多 1 组；context/support 分开计数、role 不互换、Claim 不重复；
6. context 只在 removal test 证明必要时保留，不用于装饰、氛围或信息堆积；
7. context 必须来自当前 AhaFacts/Claim Ledger，同 Revision/projection/core peak 且 surface-supported；
8. exact time 默认属于 Time Label；地点存在也不自动进入 Moment Line；
9. Chapter 的路线、准备、过程、结局、第二 peak 与用户心理不得借 context 回流；
10. own media 不补 unsupported Claim，也不允许裸指代或空泛评价；
11. 两项 context 都有用时也不能同时写入；单项无法解决时，有未尝试合法组合才 Replan，组合耗尽或 core 不完整则 Block；
12. C3b2 不改变 S07–S10 选择、Aha media、reservation、HQ 或上传策略；
13. C3b2 不调用 Writer、不选择 qualifier、不创建 provisional plan；C3b3 之后才进入 B3，由 D4 写作、E 验证真实 spans；
14. text-only surface 需要单独 presentation contract，不反向扩大当前卡片文案；
15. `AHA_PEAK_CORE` 只包含上游 selected peak identity；可分离 reaction/result 与 local context 不得通过 role laundering 绕过预算；
16. A3/B2 只产出 local-context candidate eligibility，不提前决定 necessity，也不创建 context group；
17. C3b2 是 visible support/context 联合选择的唯一决策源，逐候选结果、rank、omission 与 final selected refs 必须可回放；
18. 每个 `(support choice, context choice)` fingerprint 最多尝试一次；只有 Ready decision 可进入 C3b3，不能直接进入 B3；
19. 涉及 base selection 的 B3-triggered retry 必须回链 parent decision、B3 composition decision 与 failed `B3_VALIDATED` plan；qualifier-only retry 由 C3b3 接管，内部 retry 不伪造 B3 trigger；
20. 所有 decision/plan/validation artifact 不可变并保留完整 lineage。

## 27. 下一检查点

进入 S11-C3b3：Aha Tone & Emphasis Budget。需要决定：Moment Line 除了具体 peak 与合法局部 context/reaction 外，是否允许加入一小段克制的氛围或强调；若允许，哪些必须来自可观察 Evidence，哪些“惊喜、难忘、幸福、高光”等词仍必须禁止，避免算法替用户定义感受。

## 28. S11-C3b3｜Aha Tone & Observable Emphasis Budget

**状态：CONFIRMED BASELINE / AMENDED BY 28.12 ON 2026-08-28 / CURRENT CONTRACT = BASELINE + LIGHT-AFFECT v1.1**

### 28.1 用户确认的产品定义

V1 锁定：

> Aha 不生成独立氛围句，也不设置单独的 Tone/Atmosphere 内容槽。Moment Line 可以在同一个自然句中加入最多一个可观察强调限定，但该限定必须有直接 Evidence、不得推断用户感受，默认仍然选择 0。

因此，Aha 的完整语义预算为：

~~~text
exactly 1 PEAK_GROUP
+ 0..1 necessary MINIMAL_LOCAL_CONTEXT_GROUP       # C3b2
+ 0..1 IMMEDIATE_REACTION_SUPPORT_GROUP             # C3b2
+ 0..1 OBSERVABLE_EMPHASIS_QUALIFIER                # C3b3
+ 0 separate TONE_SPAN / ATMOSPHERE sentence        # forbidden
~~~

这里的“同一个自然句”是算法内容合同，不是 UI 必须物理显示成一行。最终字符上限、标点和本地化长度仍由 D4 决定。

C3b3 不重新判断：

- Aha 是否入选、属于哪个 Chapter、`core_peak_event_ref` 或 active media；
- C3b2 已冻结的 peak/support/context base selection；
- Chapter 的 grounded atmosphere 合同；
- 用户原文如何与 AI 文案并排、覆盖或引用；
- S07–S10 的选材、HQ、上传、云存储或 API 路由。

### 28.2 概念释义｜Tone 与 Observable Qualifier 不相同

#### Tone / Atmosphere｜语气或氛围

Tone 让句子“感觉更柔和、更有余韵”，但不对应一个可独立验证的生活事实，例如：

> 这一刻留下了一点温柔的余韵。

这类表达在 Chapter D1 的既有 grounded-atmosphere 合同下可能有自己的判断路径；但 V1 generated Aha 没有该 surface，不能消费 `NON_FACTUAL_TONE_ONLY` 或 `TonePermissionDecision`。

#### Observable emphasis qualifier｜可观察强调限定

它不是装饰，而是对一个已选事件 Claim 增加可验真的窄属性，例如：

- `缓缓`：断言动作速度较慢；
- `一下子`：断言变化起点集中、边界突发；
- `明显变亮`：断言可观察强度发生变化；
- `清楚地响起一声`：断言对应录音中存在可辨识声音。

这些词会改变用户对事件的理解，所以必须拥有 Atomic Claim、Evidence 与 attachment relation，不能由 Writer临场发挥。

#### Attachment｜附着关系

每个 qualifier 必须明确限定哪一个已选 base Claim。例：

~~~text
base Claim
  流心沿切口淌出

qualifier Claim
  该流动事件的可观察速度较慢

attachment
  qualifier → exact flow-event Claim
~~~

如果 qualifier 找不到唯一 target，或实际上描述了另一个动作／事件，它就不是合法强调限定。

### 28.3 允许的四类 qualifier 与 Evidence 门

#### `OBSERVABLE_MOTION_RATE`

描述同一动作的可观察速度，例如流动、移动、展开、倒下的快慢。

最低要求：

1. source modality 能记录时间变化，通常是连续视频、可靠连续帧或等价时序 Evidence；
2. event onset/offset 或足够的运动轨迹可验证；
3. qualifier target 与所测动作是同一个 event identity；
4. 单张结果照片不能证明“慢慢／迅速”。

#### `OBSERVABLE_ONSET_ABRUPTNESS`

描述变化是否集中发生，例如“一下子暗了”“突然塌下”。

最低要求：

1. 有变化前、变化发生与变化后的合法边界 Evidence；
2. 采样空洞不足以解释同一变化时，不写“突然”；
3. 只有结果状态时，只能陈述结果，不能反推突发过程。

#### `OBSERVABLE_INTENSITY_CHANGE`

描述可记录的亮度、声量、运动幅度等强度变化。

最低要求：

1. 明确 intensity dimension 与比较基线；
2. before/after 或同等测量范围一致；
3. `明显、格外、非常` 不能只靠模型主观感觉；
4. 物理强度变化不能被改写成情绪强度。

#### `OBSERVABLE_SENSORY_ATTRIBUTE`

只允许设备实际捕获并能验证的感知属性，例如视频音轨中清楚出现的一声响动，或画面中可直接验证的表面变化。

最低要求：

1. Evidence modality 确实能捕获该属性；
2. active Aha media 与该属性相容；
3. 摄像头／麦克风未捕获的味道、气味、口感和身体感受不能生成；
4. `好吃、香、治愈、舒服` 不因画面看起来如此就成为 observable Fact。

### 28.4 明确禁止的内容

#### 用户内心状态推断

generated Aha 默认禁止：

~~~text
惊喜
幸福
感动
治愈
喜欢
满意
舍不得
~~~

笑、停顿、伸手等可观察行为可以成为 peak/support Fact，但不能自动证明其内心含义。

#### 编辑价值判断

generated Aha 默认禁止：

~~~text
难忘
高光
精彩
特别
值得纪念
最美
最好
~~~

Aha 被选中只证明它满足上游 Aha 质量合同，不证明系统可以在用户文字中自称“高光”或“难忘”。

#### 无 Evidence 的常见副词与程度词

以下词不是永久词库禁令，但每次使用都必须有对应 Claim/Evidence；没有时一律省略：

~~~text
突然
立刻
慢慢
缓缓
格外
明显
非常
一下子
~~~

#### 独立感叹、万能句与媒体说明

不允许：

> 太棒了！

> 这一刻真的很特别。

> 镜头记录下了这个惊喜瞬间。

它们没有增加 grounded event precision，却制造了情绪、评价或 meta narration。

### 28.5 用户原文与用户确认信息的边界

1. 用户自己输入的“这个太好吃了！”属于 protected user-authored text，S11 不删除、不改写，也不把它伪装成 AI 生成 Claim；
2. 用户明确确认过“我当时很惊喜”时，可记录为 `USER_CONFIRMED_EVALUATION_CANDIDATE`，但 C3b3 不自动把“惊喜”混入 generated Moment Line；
3. 该候选统一路由到后续 D6/E2 的 user-text、voice 与 presentation contract，决定是展示原话、引用、并排还是不使用；
4. 未完成该 UX 合同前，系统既不抹掉用户表达，也不替用户转述；
5. user-confirmed evaluation 不占 observable qualifier 名额，因为两者的来源、产品语义与审计责任不同。

### 28.6 候选选择流程

每个 C3b2 Ready decision 依次执行：

1. 验证 `c3b3_entry_allowed=true`，以及 Revision、surface policy、active projection、`core_peak_event_ref` 与 Claim Ledger 完整一致；
2. 确定 exact base selected Claim set：全部 peak core Claims，加 C3b2 最终选中的 context singleton Claim 与 support group member Claims；
3. 收集同 scope 的 A3 observable candidate Facts 及其 B2 surface decisions，完整保留 supported、blocked 与 invalid audit；只有 `SURFACE_SUPPORTED + AHA_OBSERVABLE_EMPHASIS_CANDIDATE` 才进入 eligible set；不读取 parent Chapter prose，也不消费 `TonePermissionDecision`；
4. 对每个 eligible candidate 验证 `emphasis_target_claim_ref` 确实位于 exact base selected Claim set；target 只是 upstream available、但未被 C3b2 选中时，该 qualifier 必须省略；
5. 验证 attachment relation、Evidence modality、active-media alignment、same-event scope 与 qualifier type；
6. 执行用户状态／价值判断分类；任何推断或编辑评价都不得进入 ranked set；
7. 执行 material deletion test：删除 qualifier 后若只是不够生动，选择 0；只有确实损失一个已 grounded、对该瞬间有辨识价值的感知差异时，才保留候选；
8. 检查 qualifier 不创建第二事件、不重复 peak/support/context、不承担 context necessity 或 relation edge；
9. 对所有 eligible 且通过 C3b3 gates 的项做确定性排序，最多选择 1 项；没有通过项即输出 0；
10. 对 selected qualifier 与 C3b2 base Claims 建立 provisional composition payload，包含 exact ordered Claim refs 与 attachment relation；
11. 产生 immutable `AhaObservableEmphasisDecision`，再按 28.12 产生 immutable `AhaLightAffectiveFramingDecision`；两个 decision 都是正常 0／1 终态后，才创建引用 C3b2/C3b3 decisions 的 provisional `AhaNarrativeSurfacePlan`；
12. B3 验证 exact plan，D4 只实现该 plan，E 分别核对真实事实限定 span／Evidence 与可选 light-affect span／permission。

#### Material deletion test｜材料性删除测试

允许选择：

> 流心沿着切口缓缓淌了出来。

前提是视频明确支持较慢流速，并且这个速度差异是该瞬间的一部分。删除“缓缓”后 base event“流心淌出”仍为真，但会丢失一个真实、可感知且对瞬间有辨识作用的属性。

不允许仅因为：

- 句子读起来更有画面；
- Writer认为更优美；
- Aha 需要显得更精彩；
- 同类文案里常用这个词；
- 画面质量高或素材被评为 HQ。

如果删除 qualifier 会让 base Claim 本身变成错误或不完整，说明它不是 optional emphasis，而是 peak predicate/core argument 的组成部分；必须回到 B0/B2 修正 Claim decomposition，不能靠 C3b3 补洞。

#### 确定性排序

多个候选都合法时，依次比较：

~~~text
material perceptual distinction for the already-fixed Moment
→ stronger direct Evidence and correct modality
→ tighter alignment with current active Aha media
→ fewer relation / measurement dependencies
→ narrower semantic scope
→ target role priority: PEAK before SUPPORT before CONTEXT
→ stable deterministic ref order as final tie-break only
~~~

“更有情绪”“更文学”“更像高光”不进入排序。默认选择数量为 0，不为填满 1 个名额而保留弱候选。

### 28.7 B3 Recompose 与有界尝试

C3b3 不建立长串文案搜索：

1. 初次 decision 已评估全部候选，只选 rank 最高且通过所有 gate 的 0–1 项；
2. 若 B3 的 `RECOMPOSE_REQUIRED` 明确标记 `aha_recompose_owner=C3B3_OBSERVABLE_EMPHASIS`，创建一个新的 C3b3 immutable retry，回链 exact failed validated plan 与 composition decision，并严格简化为 0 qualifier；
3. observable-qualifier 基线仍最多形成“可含 qualifier／qualifier-free”两个分支；28.12 light-affect permission 只增加一次严格的 affect-free 简化，整个同一 C3b2 base decision 的 B3 full-plan fingerprints 总上限改为 3；
4. qualifier-free plan 若仍因 base composition 失败，必须返回 C3b2，不能继续尝试更多形容词；
5. 引用、schema、lineage 或 attachment 损坏为 Contract Invalid，不通过删除 qualifier 掩盖；
6. 每个 full-plan fingerprint 最多进入 B3 一次，避免循环与不可控成本。

这条策略体现产品优先级：一个真实但没有修饰词的 Aha，优于为了保留“精彩感”而增加工程复杂度或文案风险。

### 28.8 结构化合同

~~~text
AhaObservableEmphasisDecision
  selected_memory_ref
  stable_memory_id
  revision_ref
  surface_policy_ref
  core_peak_event_ref
  active_projection_fingerprint
  claim_ledger_ref
  c3b2_standalone_context_decision_ref
  c3b2_decision_state_check
  c3b3_entry_permission_check
  base_selected_claim_refs[]
  base_selected_claims_fingerprint
  evaluated_observable_emphasis_candidates[]
    qualifier_claim_ref
    qualifier_type
      OBSERVABLE_MOTION_RATE
      | OBSERVABLE_ONSET_ABRUPTNESS
      | OBSERVABLE_INTENSITY_CHANGE
      | OBSERVABLE_SENSORY_ATTRIBUTE
    emphasis_target_claim_ref
    emphasis_attachment_relation_ref
    evidence_dependency_refs[]
    surface_decision_ref
    surface_decision_state_check
    target_is_selected_base_claim_check
    same_revision_projection_peak_check
    media_modality_compatibility_check
    active_aha_media_alignment_check
    user_state_or_value_classification
      OBSERVABLE_EVENT_PROPERTY
      | USER_STATE_INFERENCE
      | EDITORIAL_VALUE_JUDGMENT
      | UNCAPTURED_SENSATION
    material_deletion_test
    no_second_event_check
    role_distinctness_check
    rank_inputs
    candidate_decision
      QUALIFIER_ELIGIBLE_MATERIAL
      | QUALIFIER_BLOCKED_SURFACE
      | QUALIFIER_OMITTED_NO_MATERIAL_GAIN
      | QUALIFIER_BLOCKED_USER_STATE_OR_VALUE
      | QUALIFIER_BLOCKED_MODALITY_OR_EVIDENCE
      | QUALIFIER_CONTRACT_INVALID
  eligible_observable_emphasis_qualifier_refs[]
  ranked_observable_emphasis_qualifier_refs[]
  selected_observable_emphasis_qualifier_refs[0..1]
  omitted_observable_emphasis_qualifier_refs[]
  observable_emphasis_omission_reason_codes[]
  user_confirmed_evaluation_candidate_refs[]
  user_confirmed_evaluation_routing
    DEFERRED_TO_D6_E2_USER_TEXT_CONTRACT
  qualifier_count_check
  selected_qualifier_subset_check
  selected_target_attachment_check
  base_selected_refs_match_c3b2_check
  context_support_emphasis_distinctness_check
  unplanned_nonfactual_tone_candidate_forbidden_check
  no_second_event_via_emphasis_check
  retry_trigger_kind
    INITIAL
    | B3_EMPHASIS_RECOMPOSE_REQUIRED
  retry_parent_emphasis_decision_ref?
  retry_trigger_b3_composition_decision_ref?
  retry_trigger_b3_validated_plan_ref?
  retry_trigger_b3_recompose_owner_check?
  retry_lineage_check
  attempted_full_plan_fingerprints[]
  remaining_full_plan_fingerprints[]
  full_plan_attempt_budget_check
  b3_entry_allowed
  decision
    NO_OBSERVABLE_EMPHASIS_SELECTED
    ONE_OBSERVABLE_EMPHASIS_SELECTED
    OBSERVABLE_EMPHASIS_CONTRACT_INVALID
  reason_codes[]
  policy_versions
  observable_emphasis_fingerprint
  construction_audit
~~~

字段可达性固定为：

~~~text
Decision state                           selected qualifier   b3_entry_allowed   provisional plan
NO_OBSERVABLE_EMPHASIS_SELECTED          0                    true               create
ONE_OBSERVABLE_EMPHASIS_SELECTED         1                    true               create
OBSERVABLE_EMPHASIS_CONTRACT_INVALID     empty                false              do not create
~~~

候选都不够好、没有材料增量、在 B2 被正常 `SURFACE_BLOCKED`，或属于用户状态／价值判断时，正常结果是 `NO_OBSERVABLE_EMPHASIS_SELECTED`，不是 Block；这些项仍保留在 evaluated audit，但不进入 eligible/ranked refs。只有 Revision/projection/policy、Claim、attachment、decision lineage、B2 `SURFACE_CONTRACT_INVALID` 或候选 inventory 合同损坏时，才进入 `OBSERVABLE_EMPHASIS_CONTRACT_INVALID`。

Decision 不反向引用 plan。`AhaNarrativeSurfacePlan` 引用 exact `standalone_context_decision_ref + observable_emphasis_decision_ref + light_affective_framing_decision_ref`，把三类事实 selected refs、独立 affect permission 与 provisional composition payload 一起冻结。B3 再创建独立 composition decision 与 `B3_VALIDATED` plan；全链保持不可变、无 artifact cycle。

推荐 reason codes 至少包括：

~~~text
NO_OBSERVABLE_EMPHASIS_NEEDED
OBSERVABLE_EMPHASIS_SELECTED
EMPHASIS_NO_MATERIAL_PERCEPTUAL_GAIN
EMPHASIS_TARGET_NOT_SELECTED
EMPHASIS_ATTACHMENT_INVALID
EMPHASIS_MODALITY_UNSUPPORTED
EMPHASIS_EVIDENCE_INSUFFICIENT
EMPHASIS_ACTIVE_MEDIA_MISALIGNED
EMPHASIS_COUNT_EXCEEDED
EMPHASIS_CREATES_SECOND_EVENT
EMPHASIS_ROLE_COLLISION
UNPLANNED_NONFACTUAL_AHA_TONE_FORBIDDEN
USER_STATE_INFERENCE_FORBIDDEN
EDITORIAL_VALUE_JUDGMENT_FORBIDDEN
UNCAPTURED_SENSATION_FORBIDDEN
USER_CONFIRMED_EVALUATION_DEFERRED
B3_EMPHASIS_RETRY_LINEAGE_INVALID
FULL_PLAN_ATTEMPT_BUDGET_EXHAUSTED
~~~

### 28.9 案例交叉检查

#### 案例 A｜流心速度有连续视频 Evidence

9 秒视频完整记录切开后流心持续数秒沿切口移动，时序轨迹足以支持较慢流速：

> 流心沿着切口缓缓淌了出来。

`缓缓` 可作为一个 `OBSERVABLE_MOTION_RATE` qualifier。若只有切开后的静态照片，只能写：

> 流心从切口淌了出来。

不能从结果照片推断速度。

#### 案例 B｜泥坯结果不证明“突然”

只有塌下后的泥坯照片：

> 泥坯塌了下去。

可以成立时，也不能自动升级为：

> 泥坯突然塌了下去。

“突然”需要变化前、起点与变化后的边界 Evidence。用户觉得事件本身意外，也不能替代该时序证据。

#### 案例 C｜灯光变化

连续视频与曝光校正后的 Evidence 都证明灯光在短时间内由亮转暗，可以写：

> 店里的灯一下子暗了下来。

这里“灯”与“暗下来”属于 peak core，“一下子”是突发边界 qualifier。若自动曝光变化无法排除，则 qualifier Block；若连真实灯光变化也无法确认，整个 base Claim 也必须回到 B2，而不是只删词。

#### 案例 D｜可观察的笑不等于“开心”

合法 support 可能是：

> 桌边的人笑了起来。

不允许改成：

> 桌边的人开心地笑了起来。

“笑”是可观察行为，“开心”是内心状态推断。即使笑声很大，也只能在对应音频 Evidence 与 plan 允许时表达可观察声量，不能推出幸福或满意。

#### 案例 E｜古镇画面不自动产生“静谧”Aha

古建筑、石板路和暖色光线可以服务 Chapter 的 grounded atmosphere；但不能仅因画面漂亮，为某条 Aha 增加：

> 静谧又治愈的一刻。

它既没有具体 peak，又包含氛围与用户感受，不属于 C3b3。

#### 案例 F｜用户自己写“太好吃了”

用户原文：

> 这个太好吃了！

系统完整保留 user-authored ref。generated Moment Line 仍只能按 Evidence 写具体事件，例如：

> 甜品切开时，流心从中间淌了出来。

两者未来是否并排展示由 D6/E2 的 UX 合同决定；C3b3 不删除用户原话，也不把“好吃”复制进 AI 文案。

#### 案例 G｜多个限定词堆叠

不允许：

> 流心突然又缓缓地、格外明显地淌了出来。

即使部分词各自可能有 Evidence，V1 也最多选择 1 个 qualifier；同时出现“突然＋缓缓”还可能产生时间尺度冲突。安全版本只保留排名最高且不冲突的一项，或全部省略。

#### 案例 H｜B3 发现 qualifier 造成组合歧义

若 C3b3 选择“一下子”，但它与 support 中的时序关系组合后产生不受支持的紧邻含义，B3 返回 emphasis-owned `RECOMPOSE_REQUIRED`。C3b3 不继续寻找更文学的替代词，直接生成 qualifier-free plan；若 base Claims 仍合法，则继续 D4。

### 28.10 Cross-Revision、成本与失败边界

1. 新 Revision 只新增一个更强的 qualifier candidate，但既有 Moment Line 仍真实、明确：C3a `TEXT_RETAIN`，不为“更有画面”重写；
2. 已发布 qualifier 的 Evidence 失效，而 base Claims 仍合法：优先 `TEXT_PATCH` 删除／替换最小 qualifier span，并重新经过必要的 C3b3/B3/D4/E；
3. qualifier 删除后句法不自然，D4 可以在不改变 Claim set 的前提下做 bounded wording patch，不能借机改写整个 Moment；
4. base peak/support/context 改变时先回 C3b2，再进入 C3b3；只改变 optional qualifier 时不重跑 S07–S10；
5. 全部 qualifier 候选被省略是正常成功，不降低 Aha 资格，也不触发补位；
6. Contract Invalid 与“没有好 qualifier”严格分离；前者走工程诊断，后者输出 0 qualifier；
7. C3b3 只读取 AhaFacts、Claim Ledger、C3b2 decision、Evidence refs 与 active-media metadata，不读取 Raw pixels；
8. C3b3 不调用 VLM/LLM、不请求新上传、不触发云存储 materialization；
9. 主要成本是有限候选的 deterministic attachment、Evidence 与删除测试；D4 仍只生成一条 Moment Line；
10. 28.12 修订后，同一 base decision 最多三个 B3 full-plan attempts：initial、至多一次 affect-free 严格简化、至多一次 qualifier-free 严格简化；不尝试更多语气词或排列，避免成本和延迟失控。

### 28.11 Invariants

1. V1 generated Aha 没有独立 Title、Story、Atmosphere 或 Tone span；
2. `NON_FACTUAL_TONE_ONLY` 与 `TonePermissionDecision` 不进入 generated `AHA_MOMENT_LINE`；
3. observable qualifier 默认 0、最多 1，只能出现在同一个 Moment Line 中；
4. qualifier 必须有 Atomic Claim、surface decision、Evidence、合法 target 与 attachment relation；
5. qualifier target 必须属于 exact C3b2 base selected Claim set；未选 base candidate 不能被 qualifier 重新带回；
6. motion rate、abruptness、intensity 与 sensory attribute 各自使用能捕获该属性的 modality；结果照片不证明过程速度／突发性；
7. qualifier 不创建第二事件、不补 core argument、不承担 context necessity、不冒充 adjacent support；
8. `惊喜、幸福、难忘、好吃、高光` 等用户状态／价值判断默认不进入 generated Aha；
9. user-authored text 保持原样，user-confirmed evaluation 单独路由，不自动转成 AI qualifier；
10. qualifier 只有在 material deletion test 证明真实感知差异值得保留时才选择，不为文风或填满预算使用；
11. C3b2 是 support/context base decision 的唯一 producer；C3b3 是 observable-emphasis decision 与 provisional Aha plan 的唯一 producer；
12. B3 验证 exact plan 与 C3b2/C3b3 selected refs、attachment graph 和 fingerprints，不能静默改选；
13. D4 只能实现 validated qualifier，不能自行增加“突然、缓缓、非常”等词；E 必须对真实 span 重新验真；
14. qualifier-only B3 failure 最多严格简化为 0 qualifier；base failure 返回 C3b2，不进行无界替词；
15. 新 qualifier candidate 本身不触发 cross-Revision rewrite；失效 qualifier 优先最小 patch；
16. C3b3 不改变上游选择、媒体、HQ、上传、存储或发布边界，也不新增视觉推理成本。

### 28.12 Versioned Amendment v1.1｜Light Affective Framing

**状态：USER CONFIRMED / EFFECTIVE FOR CURRENT CHINESE TESTING / BASELINE SUPERSEDED ONLY WHERE EXPLICITLY LISTED**

**确认日期：** 2026-08-28

#### 28.12.1 为什么需要修订

真实但完全中性的句子可能退化为监控字幕，例如：

> 猫跳上桌，碰倒了纸杯。

用户已确认：Aha 可以在不牺牲事实底线的前提下，尝试加入少量共识性的人类语感，例如动作确实相容时的`调皮地／活泼地`。本修订不把这些词伪装成客观事实，也不恢复独立 Tone 句；它建立一个与 Atomic Claim 分离、由产品显式治理的轻量表达许可。

#### 28.12.2 三种内容必须分开

| 类型 | 例子 | 是否事实 Claim | 当前合同 |
|---|---|---:|---|
| Observable qualifier | `缓缓、一下子、明显变亮` | 是 | 继续使用原 C3b3 Evidence／attachment gate，0–1 |
| Light affective framing | `调皮地、活泼地` | 否 | 新增受控 lexical permission，0–1，默认 0 |
| User state／value／intent inference | `幸福、治愈、难忘、故意捣乱` | 否且风险高 | 继续禁止 |

`LIGHT_AFFECTIVE_FRAMING`不是`NON_FACTUAL_TONE_ONLY`、不是 Chapter atmosphere、不是第二句，也不能承担 peak、context、support、relation 或 qualifier 的事实责任。

#### 28.12.3 当前中文 V1.1 的窄适用范围

初始版本只开放经版本化词表列明的**低风险 companion-animal 当前动作**，不开放模型自由类推：

~~~text
LIGHT_AFFECTIVE_FRAMING
  permission_count              = 0..1
  realized_span_count           = 0..1
  default                       = 0
  initial_target_scope          = VERSIONED_COMPANION_ANIMAL_ACTION_CLASSES_ONLY
  current-action trigger        = REQUIRED
  species/category alone        = INSUFFICIENT
  target event/entity           = EXACT AND AUDITABLE
  harm / distress / conflict    = NOT ELIGIBLE
  user/human inner state        = FORBIDDEN
  intent / relationship claim   = FORBIDDEN
  permanent personality claim   = FORBIDDEN
  causal or crowd-state claim   = FORBIDDEN
  free lexicon expansion        = FORBIDDEN
  same-day repetition control   = DEFERRED_TO_D6
  locale-specific mapping       = REQUIRED
~~~

当前中文测试词类从两类开始：

1. `PLAYFUL_COMPANION_ANIMAL_ACTION → 调皮地`：必须是当前画面中可定位的、低风险且无伤害的活跃互动／轻微意外；
2. `ENERGETIC_COMPANION_ANIMAL_ACTION → 活泼地`：必须有连续动作支持反复奔跑、跳跃、追逐等高活动状态。

“出现猫”不能单独触发`调皮地`，“出现狗”也不能单独触发`活泼地`。`可爱、乖巧、聪明、好奇、开心`当前不进入初始词表；不是判断这些词永远不可用，而是它们分别更依赖审美、服从、能力、意图或内心状态，V1.1 暂无足够窄的边界。

#### 28.12.4 决策与 artifact 合同

~~~text
AhaLightAffectiveFramingDecision
  selected_memory_ref
  stable_memory_id
  revision_ref
  surface_policy_ref
  core_peak_event_ref
  active_projection_fingerprint
  c3b2_standalone_context_decision_ref
  observable_emphasis_decision_ref
  base_selected_claim_refs[]
  evaluated_light_affect_candidates[]
    affect_class
      PLAYFUL_COMPANION_ANIMAL_ACTION
      | ENERGETIC_COMPANION_ANIMAL_ACTION
    target_event_claim_ref
    target_entity_ref
    target_entity_class
    current_action_trigger_claim_refs[]
    locale_lexicon_policy_ref
    current_action_compatibility_check
    category_alone_insufficient_check
    target_in_base_selected_claims_check
    low_risk_scene_check
    no_harm_distress_conflict_check
    no_user_or_human_inner_state_check
    no_intent_relationship_personality_check
    no_new_causal_or_crowd_state_check
    candidate_decision
      LIGHT_AFFECT_PERMISSION_ELIGIBLE
      | LIGHT_AFFECT_OMITTED_ACTION_MISMATCH
      | LIGHT_AFFECT_OMITTED_RISK_OR_SCOPE
      | LIGHT_AFFECT_CONTRACT_INVALID
  selected_light_affective_framing_permission_refs[0..1]
  omitted_light_affective_framing_permission_refs[]
  omission_reason_codes[]
  permission_count_check
  selected_target_check
  b3_entry_allowed
  decision
    NO_LIGHT_AFFECTIVE_FRAMING_PERMISSION
    | ONE_LIGHT_AFFECTIVE_FRAMING_PERMISSION
    | LIGHT_AFFECTIVE_FRAMING_CONTRACT_INVALID
  policy_versions
  light_affective_framing_fingerprint
  construction_audit
~~~

C3b3 仍是 provisional `AhaNarrativeSurfacePlan` 的唯一 producer。Plan 必须保存 exact light-affect decision ref、0–1 selected permission ref、target event/entity、affect class、policy version 与 fingerprint；这些字段进入 plan fingerprint，但不进入 `ordered_claim_refs[]` 或 `relation_edges[]`，因为它们不是事实 Claim。

#### 28.12.5 运行顺序

~~~text
C3b2 fixed peak / context / support base decision
→ C3b3 observable qualifier decision                  # factual, 0..1
→ C3b3 light-affect permission decision               # non-factual permission, 0..1
→ provisional AhaNarrativeSurfacePlan
→ B3 validates Claims/relations and affect permission/target compatibility
→ D4 realizes exact plan; permitted affect span may still be omitted
→ E verifies every factual span and separately audits any realized affect span
~~~

一个 permission 表示“可以在这个 exact target 上使用这一类中文语气”，不表示 Writer 必须使用。若事实性自然表达已经足够、使用后生硬、产生重复或超过 D4a 正常 20 字目标，D4 应保持 0 realized span。Light affect 永远不能成为进入 21–24 字软扩展的理由；必要时先删 light-affect span，再判断事实内容是否符合软扩展门。

#### 28.12.6 B3、D4 与 E 的责任

1. **B3：** 验证 permission 来自 exact C3b3 decision、target 属于 current base plan、action trigger 相容、scope/risk gate 通过，并确认它没有进入 Claim/relation graph；
2. **D4：** 只能在 permission 允许的 affect class 与 locale lexicon 内实现 0–1 个 span，不能临场扩张为`故意、开心、可爱`或修改人物／动物身份；
3. **E：** 将真实 span 标为 `LIGHT_AFFECTIVE_FRAMING_SPAN`，核对 class、target、lexicon、数量、attachment 与排除项；不能把它验成 Evidence-backed Fact；
4. **S12：** 继续执行最终发布 gate；任何未计划的非事实语气仍阻断当前 draft；
5. permission 正常为 0 不阻断 Aha，permission artifact／lineage 损坏不能通过“反正可以不用”静默吞掉。

#### 28.12.7 案例

动作连续、对象与低风险结果都成立时，可以许可：

> 猫咪调皮地跃上桌，碰倒了纸杯。

只看到猫安静坐着时，不能因物种先验写：

> 调皮的猫咪安静地坐在桌边。

狗在连续视频中反复奔跑、转身和追逐时，可以许可：

> 狗狗活泼地绕着草地跑了几圈。

仍然禁止：

> 调皮的小猫故意捣乱，把大家都逗开心了。

其中`故意`是意图，`捣乱`是更强价值判断，“大家都开心”是群体内心状态；它们都不能借 light-affect permission 进入。

#### 28.12.8 Cross-Revision、成本与版本边界

1. 新 Revision 仅新增 light-affect permission，不触发已发布真实 Moment Line 重写；
2. 已发布 affect span 失去 action/scope/risk permission 时，优先最小删除该 span并重过 D4/E；
3. permission 变化不重跑 S07–S10，不换 Aha、不换媒体、不补位；
4. 本决策只消费已经存在的 entity、action、relation 与 risk semantics，不读取 Raw pixels、不新增抽帧、上传、HQ、VLM 或外部 API；
5. 主要新增成本是小词表匹配、permission audit 与 E span check，远低于一次新的视觉理解调用；
6. 同日重复控制、具体 Writer voice 与候选策略留给 D6；
7. 英文及其他 locale 必须分别评估词义强度、礼貌、文化接受度与动物拟人化习惯，不能直译中文`调皮／活泼`后直接上线；
8. 人物、儿童、物体、天气或其他 affect classes 均不在本次初始开放范围，需真实数据与新的显式版本决定。

#### 28.12.9 有效性与覆盖关系

本 amendment 只覆盖下列旧结论：generated Aha “任何非事实语气都不得进入 Moment Line”。当前有效规则改为：**独立 Tone／Atmosphere、`NON_FACTUAL_TONE_ONLY` 与未计划的评价仍禁止；只有经本节 exact permission 的 0–1 个 light-affective lexical span 可以进入同一 Moment Line。**

28.1–28.11 关于单一 peak、observable qualifier Evidence gate、用户状态／价值判断禁令、无独立 Tone 句、默认克制、bounded retry、上游选择与成本边界的其余原则继续有效。后续 B3、C3b1、D4、E 与 S12 必须消费 `LIGHT-AFFECT-v1.1` policy version，不得引用旧的绝对禁令阻止本节已许可 span，也不得把本节解释成开放任意情绪修辞。

## 29. 下一检查点

进入 S11-D2：Chapter Title。需要决定 V1 Title 的首要体验目标是否锁定为“让用户一眼认出这段经历”，并在此基础上允许多少克制的氛围感；同时定义 Title 的信息来源、长度、与 Story/Tag 的去重复，以及哪些过度文学化或替用户抒情的命名必须禁止。

建议的起点是：Title 优先做清晰的经历身份锚点，而不是一句小诗。例如 `古镇漫步` 比较稳定；`被旧时光拥抱的上午` 虽然更文学，但既不利于快速识别，也可能替用户定义感受。具体边界需要作为下一项用户体验决策确认。

## 30. S11-D2｜Chapter Title

**状态：CURRENT CHINESE TEST DESIGN CLOSED / PRINCIPLES 1–7 CONFIRMED / D2e + EN/MULTILINGUAL DEFERRED / S11 NOT FROZEN**

### 30.1 所在链路与本轮边界

D2 位于已经通过 B3 的 Chapter Title Content Plan 之后、E 的实际文字验证之前：

~~~text
ChapterFacts / Claim Ledger
→ B0/B2 Title assertion candidates and surface decisions
→ C2 Title identity/modifier plan
→ B3 composition validation
→ D2 Title wording
→ E span / implicit-assertion verification
~~~

D2 只决定如何把已验证的 Title identity 写成用户可见短语，不重新决定 Chapter membership、Story 内容、Aha reservation、媒体、时间或 Tags。

D2 按独立检查点逐项确认；当前已确认首要体验责任、基本命名结构、中文测试长度预算、identity source priority、跨 Revision exact-specificity continuity、user-authored／user-edited Title 的显示所有权，以及同日 Title distinctness。用户已明确要求：Title failure 的 fallback／Block 暂不冻结，等待真实素材与用户测试后再判断，当前不能仅因 Title 不确定就自动阻断 Chapter。英文／多语言长度与 presentation 合同仍须在海外 Production 前单独确认；模型、Prompt、voice 与 anti-template repetition 由 D6／实现检查点处理，不在 D2 偷定。

### 30.2 用户确认的首要体验原则

V1 锁定：

> Chapter Title 的第一责任，是让用户一眼认出“这段经历是什么”。它可以带有少量、已有 Evidence 支持的氛围感，但氛围只能服务于识别，不能压过经历身份，也不能替用户抒情。

优先级为：

~~~text
recognizable Memory identity
> truthful specificity
> concise natural wording
> optional grounded atmosphere
> literary novelty
~~~

因此，Title 不是越文学越好。只要身份清楚、真实、自然，`古镇漫步` 这样的简单命名可以优于更复杂的修辞。

### 30.3 这条原则带来的直接边界

#### 应当做到

1. 用户扫一眼即可大致区分这是古镇漫步、陶艺、生日聚会、会议还是河岸散步；
2. Title identity 必须来自 B0/B2 已验证、C2 已选并由 B3 验证组合的 Title Claim／implicit assertion；
3. exact 地点、活动或 occasion 只有在 grounded 且对 Chapter identity 重要时才使用；
4. 少量氛围修饰必须有对应 Evidence，并且删除后核心身份仍然清楚；
5. Story 与媒体继续承担具体过程和细节，Title 不把整个 Chapter 压缩成一条清单。

#### 不应做到

1. 不写完整 Story 或时间轴；
2. 不罗列多个素材对象；
3. 不用“难忘、治愈、幸福、最美”等词替用户定义感受；
4. 不写“本章记录了……”之类编辑说明；
5. 不为了新鲜感，把稳定身份改成难以识别的诗句；
6. 不夺回已经 reserved 给 Aha 的 peak。

### 30.4 案例检查

#### 古镇 Chapter

推荐：

> 古镇漫步

核心活动与场景清楚，没有替用户表达情绪。

需要谨慎：

> 晚光下的古镇漫步

只有“晚光”在当前 Chapter scope、active media 与时间 Evidence 中都成立，而且它确实帮助识别这段 Chapter 时才保留；若只是更好听，删除修饰，回到 `古镇漫步`。

不推荐：

> 被旧时光拥抱的上午

它更像文学句，经历身份不清，还可能把“被拥抱”的情绪体验强加给用户。

#### 陶艺 Chapter

推荐：

> 陶艺体验

不推荐：

> 指尖与泥土的温柔相遇

后者没有直接说清活动，并引入“温柔相遇”的拟人和感受。

#### 生日 Chapter＋独立猫 Aha

Chapter 可以使用：

> 生日聚会

不应使用：

> 猫跳上蛋糕的生日

如果“猫跳上蛋糕”已经是独立 Aha peak，Title 不能为了更抓眼球而重新夺回它。

#### 普通会议 Chapter

推荐：

> 白板讨论

前提是白板确属这段会议的核心识别信息，而不是一个偶然出现的背景物。不能仅因希望显得积极就写：

> 高效突破会

“高效、突破”分别引入效率和结果判断，没有 outcome Evidence 时必须禁止。

### 30.5 尚未确认的 D2 问题

以下内容仍保持开放，不能从本轮原则自动推出：

1. 英文／其他语言的 word、grapheme、display-width 与本地化膨胀预算；
2. Title 无法安全生成时的 Block／fallback（D2e 已暂缓，等待真实素材与用户测试）。

### 30.6 Invariants

1. Title 第一责任是快速识别 Chapter identity；
2. grounded atmosphere 只能做次级修饰，不能替代 identity；
3. 文学新颖度低于真实性、可识别性与稳定性；
4. Title 不承担 Story、Time Label、Tag list 或 Aha peak；
5. Title 不推断用户心理、关系、价值或结果；
6. Title 默认使用一个核心 identity 加 0–1 个 grounded modifier 的简洁短语，不写完整句或素材清单；
7. 中文测试使用 2–10 字默认目标、12 字软上限且禁止语义截断；英文／多语言不得机械复用该数字；
8. Title source 必须先服从上游 Memory identity；identity centrality 高于具体程度、视觉显眼度与文学表现力；
9. 用户已经看过的 generated Title 默认保持连续；新增 exact specificity 只有在材料性消除歧义或纠正误导时才允许最小 patch；
10. 在 D2e 重新开启并获得真实数据之前，Title uncertainty 本身不能成为自动阻断或删除 Chapter 的新理由；
11. 当前有效的 user-authored／user-edited Title 独占可见 Title surface，后台 AI 不覆盖、不并排展示，也不把用户文字自动升级成事实 Evidence；
12. 用户清空 Title 不触发 AI Title 自动复活；只有明确的 user-authorized restore action 才能恢复 generated Title；
13. 同日 generated Title distinctness 是软优化目标；真实性、identity centrality 与 continuity 高于标题唯一性，没有可靠 disambiguator 时允许重名；
14. distinctness 不能改写受保护的 user Title，也不能用同义改写、无依据氛围词或局部视觉细节伪造差异；
15. D2 不改变 B0/B2 surface decisions、C2 plan、B3 composition 或 S07–S10 上游选择。

## 31. S11-D2a｜Basic Title Naming Structure

**状态：CONFIRMED**

### 31.1 用户确认的结构

V1 Chapter Title 默认结构锁定为：

~~~text
exactly 1 TITLE_IDENTITY_CORE
+ 0..1 TITLE_GROUNDED_MODIFIER
→ one concise phrase

complete sentence      FORBIDDEN
detail enumeration     FORBIDDEN
second identity core   FORBIDDEN
~~~

这里的“一个核心 identity”不是“只能有一个词”，而是只允许一个完整、稳定、可识别的经历身份。例如 `古镇漫步` 同时含场景与活动，但它们共同形成一个 normalized Memory identity，不是两个并列标题。

### 31.2 概念释义

#### `TITLE_IDENTITY_CORE`｜核心经历身份

用户仅看这个部分，也应能大致知道这段 Chapter 是什么。它可以是：

- grounded activity，例如 `陶艺体验`；
- grounded occasion，例如 `生日聚会`；
- grounded scene＋activity composite，例如 `古镇漫步`；
- 其他已经由 B0/B2 验证、C2 选定并通过 B3 的 normalized identity。

它不是若干素材对象的投票结果，也不能由 D2 临时从 Story 中概括。

#### `TITLE_GROUNDED_MODIFIER`｜有依据的次级修饰

它在不改变核心 identity 的前提下，增加确有识别价值的范围、地点精度、天气、光线或其他已验证限定。例如：

~~~text
TITLE_IDENTITY_CORE
  古镇漫步

optional modifier
  雨中的

result
  雨中的古镇漫步
~~~

modifier 默认数量为 0。只有删除它会明显降低这段 Chapter 的辨识度，而且对应 Fact 已通过 Title surface gate 时，才保留 1 项。仅仅更好听、更有画面或填满结构不构成材料增量。

### 31.3 结构门

每个 Title plan 必须通过：

1. **Single identity core**：只有一个 normalized Chapter identity；
2. **Standalone recognition**：core 不依赖 modifier、Story 或 Tag 才能识别；
3. **Modifier count**：0–1，且只限定同一个 core；
4. **Modifier materiality**：删除测试证明它增加实际辨识价值；
5. **No second story**：modifier 不引入第二活动、另一个 Chapter 或完整 progression；
6. **No detail list**：牌坊、木雕、河岸等素材细节不能靠并列变成 Title；
7. **No full sentence**：不包含完整叙事主谓结构、路线或结果；
8. **Reservation**：不使用 selected Aha reserved peak；
9. **Surface truth**：core 与 modifier 都来自 B0/B2/C2/B3 已批准的 Title assertions；
10. **Assertion decomposition**：core 使用唯一 `title_identity_assertion_ref`；可选 modifier 使用独立 `title_grounded_modifier_assertion_ref + title_modifier_attachment_ref`，不能把可独立为假的限定焊进 core；
11. **No user-state/value inference**：不添加用户心理、关系、结果或价值评价。

D2 只能实现已经通过的 core＋modifier plan。它不能自行增加第二个 modifier，也不能因为一句话更顺而更换 identity。若 wording 需要改变 Claim／modifier 计划，必须回到 B0/B2/C2/B3；不能在 Writer 内静默处理。

### 31.4 案例检查

#### 合法 core-only

> 古镇漫步

一个完整 identity，不需要为了“更像标题”增加修饰。

#### 合法 core＋一个 modifier

> 雨中的古镇漫步

只有雨天确实 grounded、贯穿或材料性定义这段 Chapter，并且 Title surface 已批准时才成立。

#### exact 地点属于同一 identity

> 西塘古镇漫步

只有“西塘”已可靠确认、对 Chapter identity 重要且与 active media/scope 相容时才使用；否则回到安全的 `古镇漫步`。它不是由 Writer根据建筑风格猜出的地点。

#### 不合法的细节清单

> 牌坊、木雕与河岸

三项可以进入 Story 或媒体，但没有形成一个清楚的 Title identity。不能用并列数量代替身份判断。

#### 不合法的完整句

> 我们在古镇逛了一上午

它包含主体、活动和时间范围，更接近 Story；“我们”和“一上午”也分别需要额外 Evidence。

#### 不合法的双 core

> 古镇漫步与奶茶时光

如果奶茶是独立 Aha、独立 Chapter 或仅为 interruption，它不能与古镇漫步并列成两个 Title core。若上游本身无法提供一个统一 identity，D2 不通过拼接来修复。

### 31.5 Invariants

1. Title 是简洁短语，不是完整句；
2. 每个 Title 恰好一个 identity core；
3. grounded modifier 默认 0、最多 1；
4. modifier 只提高识别，不改变 core、不制造第二故事；
5. 素材细节不能通过并列形成 Title；
6. `古镇漫步` 这类 scene＋activity 可以是一个 normalized composite identity；
7. core 与 modifier 必须由 B0/B2/C2/B3 批准，D2 不创造新 Claim；
8. 本节的中文长度由 D2b 单独确认；英文／多语言 localization 与 fallback 仍未冻结。

## 32. S11-D2b｜Chinese Title Length Budget

**状态：CONFIRMED FOR CURRENT CHINESE TESTING / ENGLISH & MULTILINGUAL PENDING**

### 32.1 用户确认的中文测试合同

当前中文测试锁定：

~~~text
generated Chinese Chapter Title
  normal target     = 2..10 visible characters
  justified soft extension = 11..12 visible characters
  semantic truncation      = FORBIDDEN
  ellipsis as generation   = FORBIDDEN
~~~

`2–10` 是默认目标范围，不是为了凑长度而填词的配额；`12` 是软上限，不是把第 13 个字符直接切掉的硬刀口。

### 32.2 为什么允许 2 字 Title

`陶艺、露营、登山、早餐` 等词在相应 Chapter 中可能已经构成完整、稳定的 identity。若它们通过 31.3 的 standalone recognition gate，就应直接使用，不为了达到 4 字而补成 `陶艺时光、露营记录` 等空泛表达。

因此，下限只阻止空字符串、单字含糊标签与结构损坏，不授权 D2 添加“时光、日记、记录、片段”等填充词。

### 32.3 11–12 字软扩展门

只有同时满足以下条件，Title 才可超过 10 字：

1. 超出部分属于不可安全删除的 identity core 或 grounded exact proper name；
2. 已先删除所有非必要 modifier；
3. 不存在已经 grounded、不会造成材料性身份损失的更短 surface form；
4. 没有通过素材罗列、完整句或第二 core 绕过长度目标；
5. active UI/presentation contract 可以完整展示或合法换行；
6. 最终长度不超过 12 个中文测试计量单位。

“更好听、更完整、更有氛围”不构成软扩展理由。可选 modifier 不得挤占必要 proper name／identity core。

### 32.4 超过默认目标时的处理顺序

~~~text
Title > 10
→ remove non-material optional modifier
→ use an already-approved safe shorter surface form, if identity is preserved
→ bounded D2 wording rewrite without Claim change
→ if essential identity is 11..12 and presentation supports it: allow soft extension
→ if still >12: do not truncate; return length/presentation replan state
~~~

D2 不得：

- 截断专有地点名；
- 生成带省略号的半个 Title；
- 删除会改变 Chapter identity 的核心词；
- 使用未经 Claim Ledger 批准的简称；
- 为适配单行 UI 把文字改成另一个事实。

超过 12 字不自动等于内容错误。它说明当前中文 wording 与 presentation budget 尚未同时满足，必须进入有界重写或后续 presentation/fallback 合同；不能静默发布残缺标题。

### 32.5 中文计量口径

当前测试按 Unicode normalization 后的用户可见 grapheme clusters 计量，而不是 UTF-8 bytes、模型 tokens 或代码单元：

1. 去除首尾空白；
2. 不通过插入空格或标点绕过预算；
3. Title 默认短语结构不主动生成句号；
4. 数字、拉丁字母与 emoji 混排的视觉宽度可能与中文字不同，先记录诊断；正式多语言版本必须使用 locale/display-width 合同重新判断；
5. App 的字体、Dynamic Type、单／双行和截断方式不由 D2b 偷定。

### 32.6 案例检查

#### 完整 2 字 identity

> 陶艺

若 Chapter identity 已明确，可以直接通过；不补成 `陶艺时光`。

#### 常规范围

> 古镇漫步

> 雨中的古镇漫步

二者分别是 core-only 与 core＋one modifier；后者仍需 modifier materiality。

#### 较长但仍自然的 exact identity

> 上海自然博物馆参观

只有 exact entity 与参观活动都 grounded 时成立。不能为了缩短而把地点改成另一个不等价名称，也不能仅因识别到建筑外观就猜 exact entity。

#### 长度合格但结构失败

> 牌坊木雕河岸漫步

即使字符数没有超限，也可能违反 single identity／no detail enumeration。长度通过不能覆盖 31.3 的结构门。

#### 超长完整句

> 我们在雨后的古镇街巷里慢慢散步

它不仅较长，还包含完整叙事、主体、天气、速度和活动范围。D2 应回到已批准的 identity，例如 `雨中的古镇漫步`；不能简单裁掉末尾几个字。

### 32.7 英文与多语言必须后置单独定义

Diary One 的核心出海市场在海外。当前先用中文测试，不表示中文 `2–10 / 12` 规则可以直接用于英文或其他语言。

海外 Production 前必须完成独立 `D2-EN / Multilingual Title Budget`，至少定义：

1. 英文默认 content-word／word-count 范围，而不是套用 2–10 characters；
2. proper nouns、品牌、地名、缩写、连字符词和冠词的处理；
3. grapheme count、display width、字体、Dynamic Type、单／双行与 accessibility；
4. 从中文到英文及其他语言的 localization expansion；
5. 语义短写、合法别名、换行、截断与 ellipsis 的权限边界；
6. 英文及核心海外语言的人工标签、评分和真实设备 UI 测试；
7. 各 locale 的独立 policy version、eval set 与 release gate。

该项是海外 Production 的 required checkpoint，不是可选优化。未定义／未验证的 locale 不得机械继承中文长度数字后直接上线。

### 32.8 Invariants

1. 当前中文 generated Title 默认目标 2–10 字；
2. 11–12 字只允许 identity／proper-name 必要软扩展；
3. 不为满足下限添加填充词；
4. 不为满足上限截断 identity、proper name 或生成省略号；
5. 长度门不能让结构、Claim、reservation 或用户状态门失效；
6. 超过 10 字先删除非必要 modifier，再做不改变 Claim 的有界短写；
7. 超过 12 字进入 length/presentation replan，不静默裁剪；
8. 中文计量不等于英文／多语言计量；
9. 海外 Production 前必须冻结并验证独立 locale contracts；
10. D2b 不决定 App 最终单／双行布局或 Dynamic Type。

## 33. S11-D2c｜Title Identity Source Priority

**状态：CONFIRMED**

### 33.1 用户确认的核心规则

V1 锁定：

> Title 先继承上游已经成立的 Memory identity，再选择最能代表这个 identity 的简洁表达。具体地点、更显眼的人物／物体、更漂亮的画面或更高质量的素材，都不能自动抢走标题。

因此，D2c 不重新聚类、不重新选择 Chapter 主题，也不通过 Title 改写上游 Memory identity。它要求上游唯一的 `title_identity_assertion_ref` 已经通过本节的 centrality 规则；D2 只在 B0/B2 已验证、C2 已授权、B3 已验证组合、仍与当前 Revision 相容、且表达同一 normalized assertion 的 surface candidates 中选择措辞来源。

如果“生日聚会”和“奶茶店晚餐”仍以两个不同 identity assertions 竞争，选择必须回到 B0/B2/C2 并重过 B3。D2c 只验证结果；发现上游选成局部身份时返回 replan，不能在 Writer 内静默换成另一个 assertion。

### 33.2 概念释义

#### `Memory identity`｜这段记忆的核心身份

它回答的是：“如果只能用一个稳定概念区分这段 Chapter，它是什么？”例如 `古镇漫步、生日聚会、陶艺体验`。它由上游的时间、语义、continuity、boundary 与用户主动采集等证据共同形成，不由 D2 看着一张漂亮照片临时决定。

#### `Identity centrality`｜身份中心性

它表示某个候选对整段 Chapter 的代表程度。最简单的删除测试是：

> 如果不提这个候选，用户是否仍能准确认出这段经历；如果把它当作标题，是否会把局部细节误写成整段经历？

覆盖整段 Chapter、能区分相邻 Memory、且删除后会造成明显身份损失的候选，中心性更高。

#### `Specificity`｜具体程度

它表示一个表述有多精确，例如 `古镇`、`西塘古镇`、`西塘烟雨长廊` 逐渐更具体。更具体不等于更中心：一个准确识别出的奶茶店，也可能只是三小时古镇漫步中的短暂停留。

#### `Visual salience`｜视觉显眼度

它表示某个人、物体或画面有多抓眼，例如蛋糕、猫、木雕特写或鲜艳招牌。显眼度可以帮助媒体选择，但不能代替 Chapter identity 判断。

### 33.3 两阶段选择门

Title source 必须按以下顺序决定，不能倒置：

~~~text
Stage A — Identity-centrality gate
  upstream title identity assertion 必须属于上游 Memory identity
  + 能代表 Chapter 的主要时间与内容范围
  + 与当前 scope / active media 相容
  + Evidence 足够且仍然有效
  + 没有占用 selected Aha reserved peak

Stage B — Expression priority
  仅在表达同一 approved assertion、且 identity centrality 基本相当的候选之间
  比较哪一种表达更清楚、自然、稳定
~~~

如果 Stage A 发现上游 assertion 不能代表 Memory identity，就直接返回 B0/B2/C2 replan，不再让更具体或更好看的局部候选参与竞争。如果没有合法 surface candidate 能表达该 assertion，D2 不把多个细节强行拼成 Title，而是返回 wording／presentation replan。

### 33.4 同等中心性下的表达优先级

以下顺序只用于 **identity centrality 基本相当** 的候选，不是越靠前就可以跳过 Stage A：

1. **定义身份的 occasion／activity**：如 `生日聚会、陶艺体验、白板讨论`；
2. **定义身份的地点＋activity**：地点确实区分这段经历时，如 `上海自然博物馆参观、古镇漫步`；
3. **中心人物／对象**：仅当整段 Chapter 确实围绕该人物／对象，且其身份、关系或可用名称已经 grounded；
4. **通用 scene**：只有它仍足以区分 Memory 时才作为安全 fallback，例如没有更稳定活动身份时的 `河岸散步`。

这里的 `occasion` 指生日、婚礼、演出等有明确事件性质的场合；`activity` 指散步、陶艺、开会、参观等持续行为；`scene` 指古镇、河岸、办公室等环境。它们不是固定的全局高低顺序，真正的第一排序始终是“谁更代表这段 Memory”。

### 33.5 确定性排序

多个候选都通过资格门时，按以下因素逐层比较；前一项不能被后一项覆盖：

~~~text
upstream Memory identity match
> identity centrality / omission loss
> Chapter temporal and content coverage
> stable specificity and Evidence strength
> compatibility with active media
> fewer unsupported dependencies
> fixed source-type tie-break
> stable reference order, final tie only
~~~

补充约束：

1. exact proper name 的置信度只证明“名称是否可靠”，不证明它对 Chapter 更重要；
2. HQ、Hero、Manual、画面美观、出现次数和视觉显眼度都不能单独决定 Title；
3. 用户主动拍摄可作为上游 centrality Evidence 之一，但不能自动压过 Chapter 的持续主线；
4. Writer 不得把普通事实升级成意图，例如只因人在博物馆就写 `专程参观`；`专程`需要独立的 intent Evidence；
5. 如果 selected Aha 已保留某个 peak，Title source 必须避开该 peak，即使它是全章最抓眼的画面。

### 33.6 案例检查

#### 生日聚会发生在奶茶店

时间轴的大部分内容是朋友相聚、蛋糕与庆祝，奶茶店只是发生地点。

推荐：

> 生日聚会

不推荐：

> 奶茶店晚餐

即使店名和地点识别得非常准确，也不能压过 occasion identity。只有这段 Memory 本身是“探访某家特色奶茶店”，店铺才可能成为 core。

#### 在艺术中心参加陶艺活动

推荐：

> 陶艺体验

如果艺术中心只是容器，写成 `艺术中心参观` 会误导整段经历。只有该地点对区分活动具有材料价值，并通过 modifier 门时，才可考虑 grounded 地点修饰。

#### 以目的地为身份的博物馆参观

当整段 Chapter 的到达、展厅行走和展品观看都围绕同一个已确认目的地时，可以使用：

> 上海自然博物馆参观

这里 exact 地点通过，不是因为它比“参观”更具体，而是地点与活动共同构成了 Memory identity。

#### 三小时古镇行走

素材包含牌坊、不同古建筑外观、木雕、石板路和河岸。推荐：

> 古镇漫步

不推荐：

> 牌坊木雕河岸

多个漂亮细节可以进入 Story 和媒体，但它们没有任何一个比持续三小时的古镇漫步更能代表全章。

#### 办公室里的白板会议

如果白板协作贯穿会议并能区分这段经历，可以使用：

> 白板讨论

如果白板只在某一帧偶然出现，稳定身份仍是会议，则应回到更保守的 `团队会议`；不能因为白板更容易视觉识别就让它成为 core。

#### 整段 Chapter 围绕同一只宠物

若时间线持续记录与同一只已可靠关联的猫互动，这只猫本身可以成为中心对象，例如使用已经批准的名称 `陪豆包玩耍`。如果猫只在生日聚会中短暂跳上桌面，它只是局部 peak，不能把 `生日聚会` 改成猫的 Chapter。

#### 猫的瞬间已经成为独立 Aha

即使猫跳上蛋糕是最抓眼的画面，Chapter 仍使用：

> 生日聚会

不能使用：

> 猫跳上蛋糕

后者既缩小了 Chapter identity，也夺回了 Aha reserved peak。

### 33.7 最小决策合同

为避免实现时把“显眼”误当成“中心”，每次 Title source 决策至少记录：

~~~text
TitleIdentitySourceDecision
  upstream_memory_identity_ref
  upstream_title_identity_assertion_ref
  upstream_title_grounded_modifier_assertion_ref?
  upstream_title_modifier_attachment_ref?
  eligible_surface_candidate_refs[]
  selected_identity_source_ref = exactly 1, when selected
  selected_identity_kind      = occasion | activity | place_activity |
                                central_person_object | scene
  centrality_and_coverage_result
  evidence_and_scope_result
  aha_reservation_result
  decision_state
~~~

`decision_state` 仅允许：

- `TITLE_IDENTITY_SOURCE_SELECTED`：恰好一个合格来源被选择；
- `TITLE_IDENTITY_SOURCE_REPLAN_REQUIRED`：上游 assertion 不足以代表 Memory identity，或没有合法 surface candidate 能安全表达它；
- `TITLE_IDENTITY_SOURCE_BLOCKED`：关键 Evidence、scope、media 或 reservation 门未通过；
- `TITLE_IDENTITY_SOURCE_CONTRACT_INVALID`：出现多个 selected source、缺失上游 identity ref 或结构损坏。

这些状态只控制 Title 生成，不改变 Chapter membership、Aha、HQ、上传或媒体选择。

### 33.8 Invariants

1. D2c 继承而不重选上游 Memory identity；
2. identity centrality 永远先于 source-type priority；
3. specificity、proper-name confidence 与 visual salience 都不等于 centrality；
4. HQ、Hero、Manual、素材数量或画面美观不能单独决定 Title；
5. occasion／activity、place＋activity、person／object、scene 的顺序只在同等中心性候选间生效；
6. Title source 必须覆盖 Chapter 的主要时间与内容范围，不能用局部细节冒充整段经历；
7. selected Aha reserved peak 不得成为 Chapter Title source；
8. 无合格单一来源时返回 replan／block，不拼接细节、不猜用户意图；
9. stable reference order 只能打破所有实质因素均相同的最终平局；
10. D2c 不改变 B0/B2/C2/B3 计划，也不改变 S07–S10 的选择结果。

## 34. S11-D2d｜Cross-Revision Exact-Specificity Continuity

**状态：CONFIRMED**

### 34.1 用户确认的核心规则

V1 锁定：

> 新 specificity 本身不足以覆盖用户已经形成的 Title continuity。旧 Title 仍然真实、清楚且能稳定识别同一段 Memory 时，保持原文；只有 exact 信息能够材料性消除歧义，或旧 Title 已经错误／误导时，才做最小 patch。

因此，后续 Sync 识别出更多地点细节，不等于系统应当持续“优化”用户已经看过的标题。连续性是产品价值，不是生成质量不足。

### 34.2 适用范围

D2d 只处理：

1. 同一个 `stable_memory_id` 的后续 Revision；
2. 先前已经向用户展示、provenance 为 `GENERATED` 的 Chapter Title；
3. 新增或更正的 exact place／venue／entity information；
4. 上游 Chapter identity、membership 与 narrative skeleton 没有被 D2 自行改变。

以下情况不属于 D2d：

- Title 尚未向用户展示：直接按当前最完整合法 Evidence 做首次生成；
- 用户自定义或用户编辑 Title：继续受 protected user surface 合同保护，不能由 D2d 自动覆盖；
- 新证据改变了 normalized Memory identity：返回 C1/C2/B3，并按 C3a `TEXT_REBUILD` 处理；
- 只是模型、Prompt、词库或风格评分发生变化：不得触发 patch。

### 34.3 默认判断顺序

~~~text
new exact assertion arrives
→ validate Evidence / scope / currentness / active-media compatibility
→ revalidate prior Title truth and identity
→ test material ambiguity in the current visible Chapter set
→ choose existing C3a state

prior Title still true + no material ambiguity
  → TEXT_RETAIN, exact prior wording reuse

identity unchanged + exact span fixes material ambiguity or factual error
  → if assertion / attachment refs change: B0/B2/C2 → B3 replan
  → TEXT_PATCH, minimum affected span only

normalized identity changed
  → C1/C2/B3 replan → TEXT_REBUILD

mandatory correction has no safe legal wording
  → TEXT_BLOCK / replan under the existing contract
~~~

D2d 不新增第五种 continuity 状态，也不把 `TEXT_RETAIN/PATCH/REBUILD/BLOCK` 重新定义一遍。

### 34.4 什么叫“材料性消除歧义”

至少满足下列一种，exact specificity 才足以触发 Title patch：

1. 当前同一天的用户可见 Chapter set 中，有两个或更多不同 Memory 使用同一 broad Title，用户仅看标题难以区分；
2. broad Title 会让用户合理地把这段 Memory 认成另一段已经存在的经历；
3. 新事实证明旧 Title 的 exact 名称错误，继续保留会形成事实误导。

以下理由不够：

1. exact 名称置信度提高了，但旧 Title 的 proposition 没变；
2. 新名称显得更高级、更完整或更像旅行日记；
3. 地点可识别，但它仍只是活动容器，不是 Chapter identity；
4. 想让新一版看起来“有更新”；
5. 新 Title 的内部语言评分比旧 Title 略高。

### 34.5 最小 patch 规则

允许 patch 时：

1. 只添加、删除或替换解除歧义／纠错所需的最小 Title span；
2. 未受影响的 identity wording 原样保留，不借机改写语气；
3. 新 exact span 若改变 assertion／attachment refs，必须先由 B0/B2 验证、C2 重建 Title plan 并通过 B3；只有 refs 与 plan 完全不变时才属于 wording-only patch；之后仍须通过 D2a structure、D2b length、D2c centrality 与 E verification；
4. 如果 exact 信息只是可选增量，而 patch 会违反长度或 presentation 合同，回到 `TEXT_RETAIN`；
5. 如果旧 Title 已经错误，不能因长度困难继续保留错误文字；应尝试合法短写，再进入 replan／block；
6. proper name 必须来自已批准的 exact entity assertion，不能由建筑风格、招牌局部或常识猜测；
7. patch 不增加新的上传、VLM 调用或视觉推理；只消费当前 Claim Ledger 已有、已验证的结构化事实。

### 34.6 案例检查

#### 当天只有一段古镇经历

先前用户已看到：

> 古镇漫步

后续 Sync 确认地点是西塘。旧 Title 仍然真实、清楚，也没有另一段古镇 Chapter 需要区分。

决策：

> `TEXT_RETAIN`：继续显示“古镇漫步”

不能只因为 `西塘古镇漫步` 更具体就改动。

#### 同一天先后去了两个古镇

上午与下午是两个独立 Chapter，原来都显示 `古镇漫步`。后续 exact Evidence 分别确认西塘与乌镇。

允许最小 patch：

> 西塘古镇漫步

> 乌镇古镇漫步

这里 exact location 解决了真实的识别冲突，没有改变两个 Chapter 各自的身份。

#### 地点只是活动容器

用户已看到 `陶艺体验`，后续确认活动发生在某艺术中心。只有这一段陶艺 Chapter，且地点不定义活动身份。

决策：

> `TEXT_RETAIN`：继续显示“陶艺体验”

不能为了加入新地点而改成 `某艺术中心陶艺体验`。

#### 旧 exact 地点被证明错误

旧 Title 是 `西塘古镇漫步`，后续可靠 Evidence 证明实际地点是乌镇。

决策：

> `TEXT_PATCH`：只把“西塘”更正为“乌镇”

这是 truth correction，不是可选的 specificity enrichment。若事实变化同时推翻整个 Chapter identity，则必须 rebuild，而不是只换地名。

#### 首次展示前已经确认 exact 地点

如果 Title 从未向用户展示，而当前 Evidence 已可靠确认西塘，并且地点对 identity 重要，可以首次直接生成 `西塘古镇漫步`。这不属于跨 Revision patch，也不存在需要保护的 prior wording。

#### 新 exact Title 超出长度预算

旧 Title `古镇漫步` 仍然正确，新 exact 名称很长且只是可选增量。

决策：

> 保留“古镇漫步”，不能截断 proper name，也不能为了显示新信息生成省略号。

如果旧名称本身错误，则不能继续展示错误 Title；必须寻找已批准的安全短写，仍失败时进入 replan／block。

### 34.7 最小审计记录

~~~text
TitleSpecificityContinuityDecision
  stable_memory_id
  revision_ref
  prior_generated_title_ref
  new_exact_assertion_ref
  prior_truth_result
  normalized_identity_unchanged
  current_visible_set_ambiguity_result
  exact_assertion_materiality_result
  length_and_presentation_result
  c3a_decision = TEXT_RETAIN | TEXT_PATCH | TEXT_REBUILD | TEXT_BLOCK
  changed_span_refs[], only when TEXT_PATCH
  reason_codes[]
~~~

审计必须能回答：为什么这次具体化足以打扰用户，或为什么系统选择保持不变。

### 34.8 Invariants

1. 对已展示 generated Title，默认是 `TEXT_RETAIN`；
2. 新 exact specificity 不自动等于材料变化；
3. 同日可见 Chapter 的真实识别冲突可以触发最小 exact patch；
4. 事实纠错高于 continuity，错误 Title 不得因“稳定”而保留；
5. identity 改变走 rebuild，不伪装成 wording-only patch；
6. optional specificity 与长度冲突时保留原 truthful Title；mandatory correction 不得保留错误内容；
7. patch 只改必要 span，不顺带润色其他 wording；
8. user-authored／user-edited Title 不进入 generated auto-patch；
9. D2d 复用 C3a 四状态，不创建平行状态机；
10. D2d 不修改 Chapter membership、Aha、媒体、上传、存储或发布边界。

## 35. S11-D2e｜Title Failure Handling

**状态：DEFERRED BY USER / REAL-DATA DECISION REQUIRED / NOT FROZEN**

### 35.1 用户决定

本检查点不锁定“Title 无法安全生成就阻断整个 Chapter”。用户明确指出：在尚未观察真实素材分布、真实失败形态与真实用户反应之前，直接阻断过于武断。

当前决定是：

> 先不阻断，也不提前冻结最终 fallback。保留问题，等真实素材导入、人工分析、打标签、评分与用户测试之后，再决定 Chapter 应使用 broad Title、无 Title 展示、固定 UI 占位，还是在特定条件下阻断。

这是有意的产品研究暂缓，不是遗漏，也不是默认选择了其中任一方案。

### 35.2 暂缓的具体范围

以下问题全部保持开放：

1. generated Chapter Title 在 Production 是否始终 `REQUIRED`；
2. 无安全 Title 时是否允许只显示 Time Label＋媒体；
3. 是否允许固定 UI placeholder，以及 placeholder 是否进入用户可见卡片；
4. broad identity 最低可以退到多宽；
5. 什么情况下 Title failure 只是 wording failure，什么情况下暴露上游 Chapter identity failure；
6. 是否存在任何足以阻断 Chapter 的 Title-only 条件；
7. 各种 fallback 对全天 3–4 个 Chapter 数量、质量与用户信任的实际影响。

在该检查点重新开启前，任何实现都不能把此前建议的“Title required＋失败即阻断”当作已确认产品定义。

### 35.3 真实测试阶段的临时观察方式

为了让后续判断有数据，而不是再次凭感觉讨论，测试阶段采用观察性处理：

1. 保留已经由上游选出的 Chapter candidate，不因 Title uncertainty 自动删除或阻断；
2. 如果现有 D2a–D2d 合同能够生成安全、真实、可识别的 Title，可把它作为 provisional draft 进入人工评价；
3. 如果无法生成安全 Title，明确记录 `title_unresolved_for_eval = true`，不伪造一个看似完整的标题；
4. 同时记录最安全 broad candidate、失败所在 gate、缺失 Evidence 与可能的 presentation alternatives；
5. 让评测人员分别判断“宽泛标题、Time Label＋媒体、固定 UI 占位、暂不展示该 Chapter”的真实体验；
6. 该观察方式只服务算法／产品测试，不等于 Production 发布合同。

`title_unresolved_for_eval` 是测试标记，不是新的 Production state，也不能被下游解释成已经批准发布。

### 35.4 需要收集的证据

D2e 重新决策前，至少观察：

1. Title unresolved 在不同用户画像、高低强度日与 Chapter 类型中的发生率；
2. 问题来自 exact 地点缺失、activity 不清、occasion 不清、人物关系不清，还是上游聚类本身不稳定；
3. 人工评测者对 broad Title 的识别准确率与自然度评分；
4. 无 Title／固定占位是否让用户觉得内容未完成、难以扫读或反而可以接受；
5. 保留或排除这些 Chapter 对全天 3–4 个目标数量和整体质量的影响；
6. 用户是否会主动修改标题，以及修改发生在什么失败类型；
7. 不同语言和海外用户是否出现不同容忍度。

样本量、评分阈值和最终 release gate 留到真实测试方案中定义，本节不凭空设数字。

### 35.5 案例检查

#### 地点不确定，但经历身份清楚

Evidence 足以确认用户持续在古镇步行，但不能确认是西塘还是乌镇。

测试阶段可评价 provisional draft：

> 古镇漫步

不猜 exact 地点，也不因缺少 exact proper name 阻断 Chapter。

#### 室内素材分散，身份仍不清楚

素材中有人、桌面、饮品与投影，但现有 Evidence 无法可靠判断是聚会、用餐还是会议。

当前不直接阻断 Chapter，也不自动生成：

> 午后时光

而是保留 Chapter candidate 与 `title_unresolved_for_eval`，交给真实数据分析判断：这是可接受的无 Title Chapter，还是上游 identity 失败，或是否存在用户认可的固定 presentation fallback。

#### broad Title 是否足够

如果算法只能从 `西塘古镇漫步` 退到 `古镇漫步`，评测不仅问它是否真实，还要问用户是否仍能快速认出这段经历。真实但毫无识别价值与真实且足够好，需要由实际评分区分。

### 35.6 暂缓期间的 Invariants

1. 当前不冻结 Title-only Chapter Block；
2. Title uncertainty 不自动删除、替换或重聚类 Chapter candidate；
3. “先不阻断”不授权模型猜事实、添加用户情绪或生成空泛填充词；
4. 无安全 Title 时必须显式记录 unresolved，不能伪装成 Title 已通过；
5. provisional draft 与 evaluation marker 都不等于 Production readiness；
6. 不新增平行于 C3a 的正式 continuity 状态；
7. D2e 必须在真实素材、人工评分与用户测试后重新开启并做最终决策；
8. 本暂缓不改变 Chapter membership、媒体、Aha、上传、存储或发布边界。

## 36. S11-D2f｜User Title Display Ownership

**状态：CONFIRMED**

### 36.1 用户确认的核心规则

V1 锁定：

> 用户自定义或编辑后的 Title 拥有可见 Title surface 的最高优先级。后台 Sync、AI Revision 与模型升级都不能自动覆盖、并排展示或偷偷换回 generated Title。只有用户明确执行“恢复 AI 标题”时，系统才可以重新显示当前合法的 generated Title；单纯清空不构成恢复授权。

“最高优先级”指用户对可见字段的所有权，不表示用户写下的每个词都会自动成为算法事实。

### 36.2 Title 可见所有权状态

按当前最新、合同有效的用户动作确定：

~~~text
no protected user Title / no user clear intent
  → current valid generated Title may own visible surface

non-empty USER_AUTHORED or USER_EDITED_GENERATED Title
  → user Title exclusively owns visible surface
  → generated Title hidden; no background overwrite

explicit user clear intent
  → generated Title remains hidden
  → no-Title Production handling remains pending in D2e

explicit RESTORE_AI_TITLE action
  → release current user suppression for this Title surface
  → show current valid generated Title, or enter current generation/eval path
~~~

时间上更新的明确用户动作可以改变显示状态；后台算法事件不能替代用户动作。

### 36.3 非空用户 Title 的处理

1. 保存 immutable user artifact ref 与 provenance：`USER_AUTHORED` 或 `USER_EDITED_GENERATED`；
2. 对 Chapter Title 返回 `SATISFIES_REQUIRED_VISIBLE_SURFACE`，不再为同一可见位置调用 generated Title Writer；
3. App 只显示用户 Title，不同时展示“AI Title＋用户 Title”两个竞争标题；
4. 上游 normalized Memory identity、Claim Ledger、Tag 与检索流程继续按自己的 Evidence 运行，不被用户措辞替换；
5. 用户 Title 可以作为 user-authored searchable text 保存，但不得未经独立确认就变成 Atomic Claim、Canonical Tag、Story Fact 或 Aha qualifier；
6. 后续 Sync 即使获得更精确的地点或更好的文案，也只更新内部合法状态，不自动改写用户 Title；
7. generated D2b 字数、禁词和语气规则不用于删改用户文字；App 输入长度与显示布局必须另行定义，算法不得静默截断。

### 36.4 用户文字与事实冲突

如果用户 Title 与后续系统 Evidence 不一致：

1. 原用户文字及 provenance 继续保留，S11 不自动纠错；
2. 冲突可记录为独立 diagnostic／future UX signal，但不能偷偷改字；
3. 用户 Title 中的关系、地点、情绪或评价不能因出现在可见标题里就传播到 generated Story、Tag 或 Aha；
4. 是否提示用户存在冲突属于 App／UX 后续定义，不在 D2f 创建弹窗或额外交互；
5. 用户明确再次编辑、清空或恢复 AI Title 时，才按新的用户动作改变显示所有权。

### 36.5 清空与恢复不是同一个动作

用户把 Title 清空，记录显式 `USER_CLEARED_TITLE` intent，而不是简单删除 user artifact 后让系统误以为“从未编辑过”。

~~~text
USER_CLEARED_TITLE
  → do not surface prior/generated AI Title automatically
  → preserve prior user/generated artifacts in lineage
  → presentation requiredness follows deferred D2e

RESTORE_AI_TITLE
  → explicit user authorization
  → select latest current, valid generated Title if available
  → if unavailable, follow current generation/evaluation path
  → never revive a stale or invalid old Title merely because it once existed
~~~

D2f 只定义语义与审计要求，不要求当前 App 立刻增加某个按钮。若 App 尚未提供明确恢复动作，就不存在恢复 AI Title 的授权。

### 36.6 案例检查

#### 用户改写 AI Title

AI 原 Title：

> 古镇漫步

用户改成：

> 和妈妈逛西塘

后续继续显示用户 Title。即使算法不能验证“妈妈”关系，也不删改用户文字；同时不能把“妈妈”自动写入 Story、人物关系或 Tag。

#### 后续 Sync 获得更精确地点

用户 Title 是 `和妈妈逛古镇`，后续算法确认地点为西塘。系统内部可以保存 exact place，但不能自动改成 `和妈妈逛西塘`，因为这仍是对用户字段的改写。

#### 用户写下主观评价

用户把 Title 改为：

> 最幸福的一天

该文字可以作为 user-authored Title 原样显示。generated Title 禁止生成的主观词，不适用于删除用户原话；但系统不能因此断言用户幸福，也不能把“幸福”传播到 AI Story 或 Aha。

#### 用户清空 Title

用户删除 `和妈妈逛西塘` 并保存空值。系统记录 `USER_CLEARED_TITLE`，不自动显示此前的 `古镇漫步`。测试／Production 如何展示空 Title，继续由 D2e 决定。

#### 用户明确恢复 AI Title

只有收到可审计的 `RESTORE_AI_TITLE` 用户动作，系统才解除该字段的 user suppression。如果 `古镇漫步` 仍是当前合法 Title，可以重新显示；如果旧 AI Title 已失效，则不能复活旧文，应进入当前合法生成／评估路径。

### 36.7 最小决策合同

~~~text
TitleDisplayOwnershipDecision
  stable_memory_id
  revision_ref
  current_generated_title_ref?
  protected_user_title_ref?
  user_clear_intent_ref?
  explicit_restore_action_ref?
  visible_title_owner
    GENERATED
    | USER
    | NONE_BY_USER_CLEAR_PENDING_D2E
  visible_title_ref?
  protected_surface_satisfaction
  generated_writer_required
  conflict_diagnostic_refs[]
  decision_reason_codes[]
  ownership_fingerprint
~~~

`generated_writer_required=false` 适用于当前非空 user Title 已满足可见字段的情况；系统仍维护上游 semantic identity，但无需浪费一次 Title Writer 调用。`NONE_BY_USER_CLEAR_PENDING_D2E` 不等于 Production 已允许无 Title，只表示 D2f 禁止自动恢复 generated Title。

### 36.8 Invariants

1. 当前非空 user Title 独占可见 Chapter Title surface；
2. generated Title 不与 user Title 并排展示，不在后台覆盖；
3. user-authored／user-edited provenance 与 generated provenance 永不混合；
4. 用户文字不自动成为系统 Fact、relation、Tag、Story 或 Aha Evidence；
5. generated Title 规则不用于静默删改用户 Title；
6. 用户清空 Title 与恢复 AI Title 是两个不同动作；
7. 只有显式、可审计的 `RESTORE_AI_TITLE` 才授权恢复 generated Title；
8. 恢复时只能使用当前仍合法的 generated Title，不复活 stale／invalid artifact；
9. 非空 user Title 已满足 visible Title surface 时，不再调用 generated Title Writer；
10. clear 后无 Title 的最终 Production 处理继续属于 D2e，不由 D2f偷定；
11. D2f 不修改 Chapter identity、membership、媒体、Aha、上传、存储或发布边界。

## 37. S11-D2g｜Same-Day Generated Title Distinctness

**状态：CONFIRMED**

### 37.1 用户确认的核心规则

V1 锁定：

> 同一天的 Chapter Title 应优先做到可区分，但不能为了不同而编造差异。真实性、identity centrality、用户文字所有权与跨 Revision continuity，全部高于标题唯一性；没有可靠 disambiguator 时允许 generated Titles 重名。

因此，distinctness 是用户扫读体验的优化目标，不是单个 Chapter 的事实门，也不是新的 Chapter Block 条件。

### 37.2 适用范围

D2g 检查同一个 current daily output projection 中的用户可见 Chapter Titles：

1. generated Titles 可以在本节规则下进行首次措辞选择或 bounded patch；
2. user-authored／user-edited Title 进入可见冲突观察，但绝不能为了 distinctness 被自动改写；
3. 不要求不同日期的所有历史 Chapter 全局唯一；日期、Time Label、媒体和检索层仍承担长期区分；
4. Aha 没有 generated Title，不进入该集合；
5. D2g 不改变 Chapter membership，也不为了标题重名合并或拆分 Chapter。

### 37.3 “重名”不能只看字符串

至少检查两种 collision：

1. **Display-string collision**：标准化空白与标点后，两个可见 Title 字符串相同；
2. **Normalized-identity collision**：字面不同，但表达的是同一个 normalized assertion，例如 `河岸散步` 与 `漫步水边`。

第二种情况下，仅靠同义改写并没有帮助用户区分 Memory，不能算 distinctness 已解决。Embedding 或 string similarity 可以帮助发现候选，但最终必须回到 normalized identity、Evidence 与 Chapter scope 判断。

重名本身不表示任何 Title 错误。两个独立、真实的 Memory 可以拥有相同活动身份。

### 37.4 决策顺序

~~~text
validate every Title through confirmed D2a–D2d gates and D2f ownership
→ preserve D2e failure/fallback deferral
→ build same-day display / normalized-identity collision groups
→ search only already-approved, identity-central disambiguators
→ verify that the disambiguator truly differs across the collided Memories
→ re-run structure / length / continuity / user-ownership checks

safe grounded distinction exists
  → apply the minimum generated-Title distinction

only partial or non-material distinction exists
  → keep truthful Titles; record residual ambiguity

no safe distinction exists
  → allow duplicate Titles; Time Label and media remain visible context
~~~

必须先让每个 Title 独立成立，再做 set-level 区分。不能牺牲单个标题的真实性来优化整组外观。

### 37.5 合法 disambiguator

disambiguator 必须已经由 B0/B2/C2/B3 批准，并继续通过 D2c centrality。可考虑：

1. 两个 Chapter 各自不同且可靠的 exact place／destination；
2. 真正不同的 activity subtype 或 occasion；
3. 只有在整段 Chapter 确实围绕其展开时，使用不同的中心人物／对象；
4. 只有时间本身构成 identity 时，使用 `夜游、日出` 等 grounded time-related core／modifier。

不得使用：

1. 随机同义改写，例如 `河岸散步／漫步水边`；
2. 无依据氛围词，例如为了不同而写 `晨光漫步／悠然河畔`；
3. 仅因不同媒体更漂亮而加入的局部对象；
4. selected Aha reserved peak；
5. 未确认地点、人物关系、用户情绪、意图或价值判断；
6. 仅重复 Time Label 功能、但不构成 identity 的 `上午／下午` 前缀。

若只确认一个 Chapter 的 exact place，另一个 Chapter 的地点仍未知，可以使用该 exact place 的前提是它本来就通过 D2c、对该 Memory 有材料识别价值；但不能因此声称另一段发生在“其他地方”，也不能把 collision 标成完全解决。

### 37.6 与 continuity 和用户文字的关系

1. 首次生成时，可以直接选择已批准的 distinct surfaces；
2. 后续新增 Chapter 造成真实同日歧义时，只有符合 D2d 材料性门，才允许对 generated Title 做最小 `TEXT_PATCH`；
3. 不因新 collision 顺带润色旧 Title；
4. user Title 永不进入 auto-patch；若它与 generated Title 重名，只能在后者存在合法 disambiguator 时修改 generated Title；
5. 没有合法 disambiguator 时保留重名，不把 user ownership 降级；
6. distinctness failure 不触发 D2e Title-only Block，也不创建新的 C3a continuity 状态。

### 37.7 案例检查

#### 两个 exact 目的地均可靠

上午在西塘，下午在乌镇，两个 Chapter 的地点与漫步活动均 grounded：

> 西塘古镇漫步

> 乌镇古镇漫步

二者的 exact place 真正区分两段 Memory，可以通过。

#### 两段都是同一河岸散步

用户上午和傍晚分别沿同一河岸步行，现有 Evidence 没有形成不同的活动 subtype 或其他 identity-central 信息。

允许：

> 河岸散步

> 河岸散步

Time Label 与媒体可以帮助用户区分。不能为了唯一性把它们强行写成 `晨光漫步／悠然河畔`。

#### 夜晚本身构成不同 identity

一段是普通日间古镇步行，另一段有可靠夜间、灯光与持续游览 Evidence，且上游 identity 已分别批准：

> 古镇漫步

> 夜游古镇

这里不是为了换词，而是第二段真实拥有不同的 time-related activity identity。

#### 只做同义替换

> 陶艺体验

> 做陶手作

如果两者指向完全相同的 normalized activity assertion，同义替换没有增加识别信息，仍属于 semantic collision；不能把语言多样性冒充 Memory distinctness。

#### 一个用户 Title 与一个 generated Title 重名

用户把上午 Chapter 命名为 `河岸散步`，下午 generated Title 也是 `河岸散步`。系统不能改用户 Title；只有下午存在可靠地点或活动差异时才调整 generated Title，否则保留重名。

#### 一段地点已确认，另一段仍未知

第一段 exact Evidence 支持 `西塘古镇漫步`，第二段只能支持 `古镇漫步`。如果“西塘”本来就是第一段的材料性 identity，可以显示这两个标题，但审计仍记录第二段存在 residual ambiguity；不能推断第二段一定不在西塘。

### 37.8 最小 set-level 决策合同

~~~text
DailyTitleDistinctnessDecision
  s09_result_bundle_ref
  selected_memory_set_ref
  daily_run_identity_ref
  title_surface_entries[]
    stable_memory_id
    title_ref
    visible_title_owner = GENERATED | USER
    entry_visibility_state
      PROVISIONAL_GENERATED
      | PRIOR_VISIBLE_GENERATED
      | PROTECTED_USER_VISIBLE
    normalized_title_assertion_ref?
  collision_groups[]
    collision_type = DISPLAY_STRING | NORMALIZED_IDENTITY
    member_stable_memory_ids[]
    eligible_disambiguator_refs[]
    applied_generated_title_patch_refs[]
    residual_ambiguity
    group_decision
      NO_COLLISION
      | GROUNDED_DISTINCTION_APPLIED
      | PARTIAL_GROUNDED_DISTINCTION
      | DUPLICATE_ALLOWED_NO_SAFE_DISAMBIGUATOR
      | DISTINCTNESS_CONTRACT_INVALID
  distinctness_fingerprint
~~~

`PARTIAL_GROUNDED_DISTINCTION` 只说明可见信息有所增加，不能伪装成冲突已经完全解决。除 contract invalid 外，任何 group decision 都不是 Chapter Block。

### 37.9 成本与执行边界

1. collision detection 使用现有 Title strings、normalized assertions 与 Claim refs，不重新读取 Raw／HQ；
2. 不新增上传、VLM 或外部 lookup；
3. 当前每日通常只有 3–4 个 Chapter，set-level 比较本身成本可以忽略；
4. 只有确有合法 distinction 且需要新 wording 时，才进入既有 bounded D2→E rewrite；
5. 不为了语言多样性额外生成多轮候选，该问题属于 D6 anti-template repetition，且仍受真实性门约束。

### 37.10 Invariants

1. 每个 Title 的独立真实性先于 set-level distinctness；
2. distinctness 是软目标，不是发布事实门或 Chapter Block 条件；
3. 没有可靠 disambiguator 时允许 generated Titles 重名；
4. 同义改写不等于 Memory 已区分；
5. disambiguator 必须真实、材料性、identity-central，并通过现有结构与长度门；
6. Time Label 已能表达的普通上午／下午信息不为标题唯一性重复写入；
7. user Title 不因 collision 被自动改写；
8. 后续 collision 只允许符合 D2d 的最小 generated patch；
9. collision 不改变 Chapter membership、Aha reservation、媒体或上游 identity；
10. D2g 不增加上传、视觉推理或无界 Writer 成本。

## 38. S11-D2 Current-Chinese-Testing Closeout Cross-Check

**状态：CROSS-CHECK PASSED WITH CONTRACT-ALIGNMENT AMENDMENTS / CURRENT CHINESE D2 DESIGN CLOSED / EXPLICIT DEFERRALS REMAIN / S11 NOT FROZEN**

### 38.1 检查范围与结论

本轮逐项交叉核对：

~~~text
D2a structure
↔ D2b Chinese length
↔ D2c identity source
↔ D2d cross-Revision continuity
↔ D2e explicit real-data deferral
↔ D2f user Title ownership
↔ D2g same-day distinctness

against
  S09 S09ResultBundle / SelectedMemorySet
  B0/B2 Title assertions and surface decisions
  C2 CrossSurfaceInformationPlan
  B3 composition validation
  C3a continuity / protected user surfaces
  future E actual-language verification
~~~

结论：用户已确认的七项 Title 原则可以同时成立；没有需要推翻的产品定义。交叉检查发现并修正了五项接口／旧案例不一致，修正只让上下游显式对齐，没有扩大 D2 权限。

### 38.2 已完成的 contract-alignment amendments

1. **Title modifier 可独立验真：** B0 增加 `ImplicitSurfaceAssertionAttachment` 的唯一确定性生产者；C2 `CrossSurfaceInformationPlan` 由单一 identity ref 扩展为 `identity ref + optional modifier assertion ref + attachment ref + materiality check`；解决 `雨中的古镇漫步` 中“雨”可能独立为假、却没有单独引用的问题；
2. **D2 真实上游链路：** D2 的直接 Title 输入改为 `B0/B2 → C2 → B3`；C1 继续负责 Chapter Story budget，不再被误写成 Title assertion selector；
3. **exact specificity 与 continuity：** C3a 的旧“周庄”案例改为服从 D2d；仅知道更精确地点不自动 patch，真实同日歧义或事实纠错才允许最小修改；
4. **用户 Title presentation：** C3a 增加 `title_display_ownership_decision_ref?`，旧案例改为引用 D2f；非空用户 Title 满足可见 Title surface，clear 后的 Production requiredness 仍归 D2e；
5. **同日集合引用：** D2g 不再使用未冻结的泛称 `daily_output_projection_ref`，改为引用 S09 `S09ResultBundle + SelectedMemorySet + run identity`；provisional generated、prior visible generated 与 protected user entries 分开记录。

### 38.3 七项规则的交叉结果

| 检查项 | 交叉结论 |
| --- | --- |
| D2a ↔ B0/B2/C2/B3 | 一个 identity core；0–1 modifier 独立 assertion＋attachment，组合后再进 Writer |
| D2b ↔ D2a/D2g | 超长先删 optional modifier；若 distinctness 因此无法实现，允许重名，不截断语义 |
| D2c ↔ C2/B3 | identity centrality 先于 source type、具体程度和视觉显眼度；Writer 不换 assertion |
| D2d ↔ C3a | 默认 exact wording retain；真实歧义／纠错才 patch；新增 assertion／attachment 先重过 B0/B2/C2/B3；identity change 才 rebuild |
| D2e ↔ C3a/E/S12 | 测试阶段 Title unresolved 不自动删除／阻断 Chapter，但 unresolved 也不等于 Production ready |
| D2f ↔ C3a/E2 | 用户 Title 独占可见字段且不进 generated E 验真；用户文字不反向成为 AI Evidence |
| D2g ↔ S09/D2d/D2f/E | set-level distinctness 只改 generated Title；无可靠差异允许重名；最终实际 wording 仍须过 E |

### 38.4 当前中文 Title 执行链

~~~text
S09ResultBundle + SelectedMemorySet
→ B0/B2 eligible Title implicit assertions
→ C2 choose exactly 1 identity assertion
     + 0..1 grounded modifier assertion / attachment
→ B3 validate composition
→ C3a continuity applicability
→ D2f visible-owner gate
   ├─ protected non-empty user Title
   │    → show user Title; no generated Title Writer
   ├─ user clear intent
   │    → do not revive AI Title; D2e remains deferred
   └─ generated surface required for current test
        → D2a/D2b/D2c wording
        → D2d retain or bounded patch rule
        → D2g same-day set comparison
        → E actual span / implicit assertion / attachment verification
→ S12 remains final publication authority
~~~

D2g 在首次生成时检查 provisional candidates，在后续 Revision 中同时读取 prior visible Titles；任何新 generated wording 在 E／S12 之前都不能标记为用户可见或 publish-ready。

### 38.5 明确保留的开放项

当前只关闭“中文测试所需的 D2 产品与算法逻辑”，不伪装成全球 Production 完成：

1. **D2e：** Title failure／fallback／Title-only Block 等真实数据后的产品决定；
2. **D2-EN／multilingual：** 英文及其他核心市场语言的长度、display width、localization expansion 与设备 UI release gate；
3. **D6：** 模型、Prompt、voice、temperature、candidate/retry budget 与 anti-template repetition；
4. **E：** 最终实际 wording 的 span-to-assertion、modifier attachment、unsupported language 与 user-text protection 验证；
5. **App：** 用户编辑／清空／恢复 AI Title 的具体控件、文案与布局。

这些开放项不推翻 D2 已确认原则；其中 D2e 与 multilingual 是显式 deferred，D6/E/App 是后续既定阶段的责任。

### 38.6 Closeout Invariants

1. 当前中文 D2 的七项确认规则不再重复讨论，除非真实数据或后续交叉检查提供反证；
2. D2e 暂缓不被实现解释为“默认阻断”或“默认允许 Production 无 Title”；
3. 英文／多语言不能复用中文字符预算直接上线；
4. D2 不读取 Raw／HQ、不新增上传、VLM 或外部 lookup；
5. D2 不改变 S09/S10 membership、媒体、Aha reservation 或 identity；
6. user Title 与 generated Title provenance 永不混合；
7. E 与 S12 未完成前，D2 output 不等于 publish-ready；
8. 本节关闭 D2 当前中文设计，不冻结整个 S11。

## 39. S11-D3｜Time Label

**状态：FROZEN FOR CURRENT CHINESE TESTING / PRINCIPLES 1–9 LOCKED / CLOSEOUT CROSS-CHECK PASSED / EXPLICIT DEFERRALS REMAIN / S11 NOT FROZEN**

### 39.1 所在链路与本轮边界

D3 的讨论编号位于 User-visible Writing，但 Time Label 不是 Writer 自由生成的句子。D3a–D3d 中涉及“选择哪一种时间语义”的规则，必须作为 versioned deterministic policies 被上游 assertion／plan 链消费；D3e 才是把最终已选择语义变成用户可见字符串的 formatter。生产执行顺序为：

~~~text
A3 temporal Facts + timezone / user-local-day scope
+ existing Boundary / Continuity Evidence
+ D3a–D3d versioned semantic policies
+ D3f prior-independent candidate-envelope policy
→ B0 materialize current TIME_LABEL ImplicitSurfaceAssertion candidates
→ B2 validate each candidate's truth / support / surface permission
→ C2 form current base Time Label surface plan + eligible candidate set / omission permission
→ C3a routing policy + D3f apply prior-published continuity and hysteresis
→ B3 validate the finally selected composite assertion, when composition applies
→ D3e deterministically format the validated final semantic key
→ E actual-label / implicit temporal assertion verification
→ materialize C3a aggregate record + final TimeLabelSurfaceOutcome
~~~

这条顺序不要求把文档章节重新编号；它明确区分“讨论先后”和“运行依赖”。D3f 的 25%／35% candidate-envelope 参数可被 B0 作为**不读取 prior artifact**的 versioned policy 输入，用来 materialize current `CONTINUITY_RETAIN_ONLY` candidates；真正读取 prior published outcome 并做 retain／replace 的 D3f decision 仍位于 C2 之后。D3f 只能从 current Revision 已由 B0/B2/C2 提供的合法候选中选择，不能在 B3 之后创造一个新的 single／dual／exact assertion。C2 保存 base plan，D3f 保存新的 continuity decision；两者都保持 immutable，不能互相后填引用。这里的“C3a routing policy”先决定分支；携带 downstream child refs 的 C3a aggregate record 在 B3/D3e/E 完成后才物化，因此 child artifacts 不需要反向引用后置 aggregate。

D3 只决定如何安全表达“什么时候”。它不重新决定 Chapter/Aha membership、时间边界、持续关系、素材顺序、媒体、Title 或 Story，也不把上传／Sync／云端处理时间当作拍摄时间。Chapter 与 Aha 的语义形状不同，因此分别采用“经历时间段”和“高潮单点”的粒度合同；不能为了界面统一而强迫两者显示同一种精度。

### 39.2 用户确认的基础体验原则

V1 已确认两项基础原则：

1. **Chapter 先诚实表达经历所在时间段：**

> Time Label 的第一责任，是帮助用户快速定位“这段经历大概发生在什么时候”，不是声称算法知道活动精确从哪一分钟开始、到哪一分钟结束。对 Chapter 默认优先使用 grounded broad period；只有 boundary 与 continuity Evidence 足以支持时，才允许 exact range。

2. **Aha 可在证据充分时表达高潮单点：**

> Aha 绑定单一 peak 与精确 EvidenceAnchor；如果该 Anchor 的绝对拍摄时间可被可靠追溯，Aha 可以使用 exact point。若只能知道视频开始时间、模糊时间段或不可靠 offset，则回退到 broad period，不能把视频开始时间冒充高潮发生时间。

优先级为：

~~~text
temporal truth
> semantic fit: Chapter interval / Aha point
> quick chronological orientation
> stable and grounded granularity
> visual precision / apparent completeness
~~~

因此，更精确的数字不自动代表更准确。`上午` 可能比 `09:02–10:58` 更诚实。

### 39.3 概念释义

#### `Capture timestamp`｜素材拍摄时间

设备记录某张照片或某段视频开始／结束的时间。它能证明素材在该时间被采集，不能单独证明现实活动也恰好在这一刻开始或结束。

#### `Observed evidence span`｜已观测证据范围

当前 Memory 中最早与最晚合法观测之间的时间范围。例如第一条古镇素材为 09:02、最后一条为 10:58，可以记录 observed span 为 `09:02–10:58`。

它表达的是：

> 在这个范围内存在与该 Memory 相容的观测。

它不自动表达：

> 这项活动从 09:02 连续进行到 10:58。

#### `Boundary Evidence`｜边界证据

能够支持活动／Memory 起点或终点的证据，例如已验证的进入／离开、开始／结束事件、用户确认、可信行程事实，或其他已经在上游通过的 boundary relation。第一条和最后一条素材本身不是充分 boundary Evidence。

#### `Continuity Evidence`｜连续性证据

能够支持范围内素材确属同一持续经历、且没有被未解释中断破坏的证据。Continuity Evidence 不能代替起止边界；有连续主线仍不表示算法看到了真实开始和结束。

#### `Event/activity interval`｜现实活动范围

对现实经历何时开始、何时结束的主张。它比 observed span 更强，只有对应 boundary 与 scope Evidence 完整时，才能成为 exact Time Label range 的语义。

#### `Broad period`｜宽时间段

中文测试版 V1 已确认使用 `凌晨、清晨、上午、中午、下午、晚上` 六段。它牺牲分钟级精度，换取更稳定、自然且不夸大边界的时间定位；具体固定分界见 D3b，跨时段处理见已确认的 D3c／D3c1。

### 39.4 Chapter Time Label 的当前合同

1. 默认输出 grounded broad period，不默认输出 observed first/last timestamps；
2. 第一条素材时间不自动等于 Chapter 开始时间；
3. 最后一条素材时间不自动等于 Chapter 结束时间；
4. Auto 每两分钟采样形成的是离散观测，不自动支持持续、全程或精确边界；
5. Manual photo／video 的开始结束时间先证明该媒体的 capture interval，不自动证明整个 Chapter interval；
6. exact range 必须另行通过 start-boundary、end-boundary、continuity、scope 与 timezone checks；具体强度门见已确认的 D3d；
7. 若 exact range 不够安全，回到 broad period，不通过四舍五入或整点化伪造活动边界；
8. upload、Sync、cloud ingest、analysis 与 publish timestamps 不进入用户可见拍摄 Time Label；
9. Time Label 不写活动、地点、情绪或价值判断；这些分别属于 Title／Story／Tag 等 surface；
10. Chapter 合同不自动套给 Aha；Aha 采用第 40 节已确认的“可靠 exact point，否则 broad period”合同。

### 39.5 为什么不能把首尾素材直接显示成范围

假设：

~~~text
08:56  用户已进入古镇，但设备尚未产生可用素材
09:02  第一条合法古镇观测
09:04  下一条 Auto 观测
...
10:58  最后一条合法古镇观测
11:06  用户才真正离开古镇，但没有可用素材
~~~

直接显示 `09:02–10:58` 会让用户自然理解为活动在这两个时刻精确开始和结束，但算法实际只知道观测范围。默认显示 `上午` 不会制造这层虚假边界。

如果未来确有可靠的 08:56 entering boundary、11:06 leaving boundary 与中间 continuity，exact candidate 应基于这些事实，而不是继续使用素材首尾时间假装边界。

### 39.6 案例检查

#### Auto 素材覆盖近两小时

09:02 到 10:58 之间持续有古镇 Auto 素材，但没有可靠进入／离开 Evidence。

推荐：

> 上午

不推荐：

> 09:02–10:58

后者只能作为内部 observed span，不能作为活动范围发布。

#### Chapter 中有一张 15:42 Manual Photo

该照片证明用户在 15:42 主动拍下一个画面，不能让整个 Chapter 的 Time Label 变成 `15:42`。Chapter 仍须基于完整 Memory scope 选择 broad period 或合法 range。

#### 两分钟 Manual Video

视频 metadata 为 19:30–19:32，只证明该视频的录制范围。若它属于一段更长的晚餐 Chapter，不能把 Chapter 写成 `19:30–19:32`；当前更安全的候选可能是 `晚上`。

#### 可靠课程边界

用户确认课程从 14:00 开始、15:30 结束，上游 boundary／scope／continuity 全部通过。`14:00–15:30` 可以成为 exact range candidate，但仍须依次通过 D3d exact-range gate、D3f Revision decision 与 D3e formatter。

#### 中午前后跨时段

素材从 11:50 延续到 13:20。它不能由本节直接被硬塞进 `上午` 或 `下午`；固定分界见 D3b，dominant period 与跨时段 label 见 D3c／D3c1。

#### 晚上才 Sync 上午素材

上午素材在 22:00 上传云端。Time Label 仍来自上午 capture temporal facts，不能显示 `晚上`。

### 39.7 最小 temporal view

~~~text
TimeLabelTemporalView
  selected_memory_ref
  stable_memory_id
  revision_ref
  memory_type = CHAPTER | AHA
  s09_run_identity_ref
  user_local_day
  timezone_and_day_scope_ref
  eligible_capture_timestamp_refs[]
  observed_first_timestamp?
  observed_last_timestamp?
  observed_span?
  start_boundary_evidence_refs[]
  end_boundary_evidence_refs[]
  continuity_evidence_refs[]
  temporal_assertion_ceiling
    BROAD_PERIOD_ONLY
    | EXACT_POINT_ELIGIBLE
    | EXACT_RANGE_ELIGIBLE
  display_granularity_decision_ref?
  time_label_candidate_semantic_specs[]
  limitations[]
  temporal_view_fingerprint
~~~

`EXACT_*_ELIGIBLE` 先表示事实层允许该粒度，不单独等于最终字符串。`time_label_candidate_semantic_specs[]` 也是给 B0 materialize assertions 的前置语义规格，不是已经通过 B2/C2 的 assertion refs。D3a 已确认：Aha 一旦通过当前 resolved Anchor、timestamp、timezone 与 scope checks，优先采用 exact point；Chapter exact range 的实际显示还必须经过 D3d、D3f 与 D3e。

### 39.8 成本与执行边界

1. Time Label 使用现有 timestamps、timezone、Boundary Evidence 与 Continuity Evidence；
2. 不读取新 Raw／HQ，不新增上传、VLM、LLM 或外部 lookup；
3. broad-period mapping 与格式化应为确定性、versioned 逻辑，不调用 Writer；
4. E 仍须验证真实 label 是否表达了比 `temporal_assertion_ceiling` 更强的时间含义；
5. D3 不修复上游错误 timestamp、timezone 或 boundary contract；输入损坏进入 contract diagnostic，不靠模糊文字掩盖。

### 39.9 Invariants

1. Time Label 的第一责任是诚实的时间定位，不是显示最多数字；
2. observed span 不等于 event/activity interval；
3. 第一／最后素材不自动成为活动起止边界；
4. Chapter 默认 broad period；exact range 必须同时满足后续 boundary、continuity、scope 与 timezone gate；
5. Manual capture interval 不自动成为 Chapter interval；
6. Sync／upload／processing／publish time 不进入 capture Time Label；
7. 不用整点化、四舍五入或区间扩张伪造未知边界；
8. D3 只消费合法 temporal assertions，不从画面明暗猜 `清晨／傍晚`；
9. Aha 在 resolved EvidenceAnchor 的绝对时间可靠时可显示 exact point；否则回到 broad period，不能从视频开始时间或 Chapter range 推出；
10. D3 不改变 membership、boundary、continuity、媒体或其他 narrative surfaces。

## 40. S11-D3a｜Chapter / Aha Time Granularity Separation

**状态：CONFIRMED**

### 40.1 决策

Chapter 与 Aha 使用不同的 Time Label 粒度合同：

| Memory 类型 | 默认粒度 | 更精确粒度的条件 | 失败回退 |
|---|---|---|---|
| Chapter | `CHAPTER_BROAD_PERIOD` | 只有 start boundary、end boundary、continuity、scope 与 timezone 均足以支持时，才成为 `CHAPTER_EXACT_RANGE_ELIGIBLE`；实际显示须继续通过 D3d／D3f／D3e | broad period |
| Aha | `AHA_EXACT_POINT` 优先 | resolved EvidenceAnchor 的绝对拍摄时间可安全追溯，且确实对应该 Aha peak | `AHA_BROAD_PERIOD` |

这不是对 Aha 的“特殊奖励”，而是语义不同：

- Chapter 表达一段经历，不能由第一／最后观测伪造起止范围；
- Aha 表达一个已被 S09/S10 选中的瞬间，若这个瞬间已有精确 Anchor，就可以诚实地显示其单点时间；
- Aha 的 exact point 只定位该 peak，不证明整个事件、视频或 Chapter 的持续范围。

### 40.2 照片与视频的单点时间来源

#### Manual Photo / `STILL_ASSET`

若照片本身的 capture timestamp、timezone 与 user-local-day scope 均合法，`STILL_ASSET` 可以直接提供 Aha 单点时间。这里使用照片的真实拍摄时间，不生成虚构的 `0.0s` 视频 offset。

#### Video / `FRAME_TIMEPOINT`

视频必须使用 resolved `FRAME_TIMEPOINT` 对应的实际 source/decode timestamp：

1. Anchor 必须确实绑定该 Aha 的 peak，而不是任意“看起来差不多”的帧；
2. source asset、source timebase、实际解码 timestamp 与绝对 capture time 的映射必须可追溯；
3. 若上游保留的是相对 offset，只有当 video start timestamp、offset、timebase 与 Anchor provenance 均合法时，才能确定性换算绝对单点时间；
4. 实现应优先消费 S10 resolved EvidenceAnchor 已解析的规范 timestamp，不在 D3 中再次凭目标抽帧 offset 粗略重算；
5. 只有视频 asset start/end、却没有 peak frame/timepoint 时，不能把视频开始时间写成 Aha 时间。

例如 2 分钟 Manual Video 于 19:30 开始，并不代表其中的惊喜瞬间发生在 19:30。只有解析到该 peak 的合法 Frame Timepoint 后，才可能显示 exact point。

### 40.3 exact point 的语义上限

假设合法 Anchor timestamp 为 `20:17:08`，未来若界面采用分钟格式，可形成 `20:17` 候选。它只表示：

> 该 Aha 的证据瞬间位于用户当地时间 20:17 这一分钟内。

它不表示：

- 活动在 20:17 开始或结束；
- 整段视频只发生在 20:17；
- Chapter 的边界是 20:17；
- 用户在 20:17 才开始参与该经历；
- 算法知道用户在这一分钟内未被拍到的全部行为。

分钟显示的舍入／截断语义、是否显示秒与 locale format 已由 D3e 中文测试合同确认；本节不允许显示层把 `20:17:59` 改写成语义不清的“20:18 左右”。

### 40.4 禁止使用的时间来源

Aha exact point 不得来自：

1. Sync、upload、cloud ingest、analysis、render 或 publish time；
2. 视频 asset start time，除非 peak 的 resolved Anchor 恰好且可证明位于该时刻；
3. 计划抽帧位置、请求 offset 或 nominal frame index，而没有实际解码 timestamp；
4. 画面明暗、店铺营业状态、用户衣着或相似素材推测出的钟点；
5. Chapter 的 observed first/last timestamp；
6. Writer 为了文案自然度自行补出的时间。

若 exact point 不满足合同，降为 `AHA_BROAD_PERIOD`。若连 timezone／user-local-day 都不足以安全确定 broad period，则返回 temporal contract diagnostic；不能猜一个 label 来掩盖输入缺失。普通 unresolved 的无感省略与 contract invalid 分流见已确认的 D3c2。

### 40.5 最小粒度决策对象

~~~text
TimeLabelGranularityDecision
  selected_memory_ref
  stable_memory_id
  revision_ref
  memory_type = CHAPTER | AHA
  resolved_evidence_anchor_ref?       # Aha exact point 必需
  source_timestamp_ref?
  timezone_and_day_scope_ref
  point_time_derivation
    STILL_CAPTURE_TIMESTAMP
    | RESOLVED_FRAME_TIMESTAMP
    | NONE
  display_granularity
    CHAPTER_BROAD_PERIOD
    | CHAPTER_EXACT_RANGE_ELIGIBLE
    | AHA_EXACT_POINT
    | AHA_BROAD_PERIOD
  exact_point_timestamp?
  broad_period_candidate?
  derivation_provenance_refs[]
  fallback_reason?
  limitations[]
  granularity_policy_version
  decision_fingerprint
~~~

`CHAPTER_EXACT_RANGE_ELIGIBLE` 仍只是候选资格；它不表示本轮已经批准 exact range 的产品显示。`AHA_EXACT_POINT` 则必须有一个当前 active、resolved、可追溯的 EvidenceAnchor 与 source timestamp。

### 40.6 案例检查

#### 生日 Chapter 与猫跳上蛋糕 Aha

生日聚会是一段经历，边界不完整：Chapter 显示 `晚上`。猫跳上蛋糕的照片 capture timestamp 为 20:17:32 且 provenance 合法：Aha 可形成 `20:17` 候选。

二者并不冲突：`晚上`帮助用户定位聚会所在时段；`20:17`定位其中独立成立的惊喜 peak。

#### 9 秒 Auto Video 内的 peak

Auto Video 开始于 20:17:04，resolved `FRAME_TIMEPOINT` 的实际 source/decode timestamp 映射为 20:17:08。Aha 可形成 `20:17` 候选，因为单点来自 peak frame，不是因为视频“差不多在 20:17”。

#### 两分钟视频只有开始时间

Manual Video 从 19:30 录到 19:32，但系统只知道“惊喜发生在这段视频里”，尚未解析精确 peak frame。不能显示 `19:30`；Aha 应回退到 `晚上`。

#### Anchor Fallback 改变了时间

Primary Anchor 在取源时失效，S10 切换到表达同一 peak 的预声明 Fallback Anchor；新 Anchor 的合法 timestamp 落在 20:18。D3 必须重新验证并重算 Time Label，不能继续盲用旧 Anchor 的 `20:17`。若 fallback 已不再精确对应该 peak，则 exact point 资格一并失效。

#### 晚上 Sync 白天的 Aha

Aha 的 peak 拍摄于 10:24，用户 22:00 才 Sync。其 Time Label 仍来自 10:24 的 capture/Anchor facts，与 22:00 无关。

### 40.7 Anchor Fallback 与 Revision 连续性

1. **Media Fallback 不改变 Anchor：** 只从 VIDEO_5S 改为 PHOTO 等格式时，若 resolved EvidenceAnchor 不变，Time Label 不应改变；
2. **Anchor Fallback 必须重验时间：** active Anchor 改变后，重新检查 source timestamp、timezone、day scope 与 peak compatibility；
3. **不得保留 stale point：** 新 Anchor 不支持 exact point 时，降为 broad period，而不是为了视觉稳定继续展示旧分钟；
4. **事实正确优先于表面稳定：** provenance 证明旧 timestamp 错误时允许纠正；
5. **无事实变化不得抖动：** 同一 Anchor、同一 timezone/day scope 与同一 policy version 下，Writer、Title 或媒体格式变化不能让 Time Label 改来改去；
6. 具体跨 Revision 保留／修订规则由 C3a 总原则与已确认的 D3f Time Label 专用合同处理；D5 只负责 Tags。

### 40.8 成本与执行边界

1. D3a 直接消费 S10 已 resolved 的 EvidenceAnchor 与 timestamps，不为 Time Label 新增抽帧或媒体解码；
2. 不新增 Raw／HQ 读取、上传、VLM、LLM 或外部 lookup；
3. timestamp 映射、资格判断与 fallback 均为 deterministic、versioned 逻辑；
4. 不因为 Aha 使用 exact point 而要求云端补取 Auto Video 的另外两帧；现有 `1-or-3` 上传合同保持不变，证据不足就回退；
5. 本节不改变 S09 peak selection、S10 Anchor/MediaDecision 或 Chapter/Aha membership。

### 40.9 Invariants

1. Chapter 与 Aha 不为界面整齐而共享错误的时间粒度；
2. Chapter 默认 broad period；Aha 仅在 peak Anchor 绝对时间可靠时使用 exact point；
3. 照片 capture timestamp 可锚定照片瞬间；视频 start timestamp 不自动锚定视频内 peak；
4. `FRAME_TIMEPOINT` 使用实际 source/decode timestamp，目标 offset 只属于 provenance；
5. exact Aha point 是瞬间定位，不是 event、video 或 Chapter duration；
6. Anchor Fallback 后必须重验，不保留与 active Anchor 脱钩的 stale time；
7. exact 失败回到 broad period，不补帧、不猜测、不调用 Writer；
8. Sync／upload／processing 时间永不冒充 capture time；
9. 本节确认粒度分离，不冻结整个 D3 或 S11。

## 41. S11-D3b｜Chinese V1 Broad-Period Vocabulary

**状态：CONFIRMED**

### 41.1 决策

中文测试版 V1 使用六个互斥 broad periods：

| 用户当地时间 | Time Label |
|---|---|
| 00:00–05:00 | 凌晨 |
| 05:00–08:00 | 清晨 |
| 08:00–12:00 | 上午 |
| 12:00–14:00 | 中午 |
| 14:00–18:00 | 下午 |
| 18:00–24:00 | 晚上 |

所有区间采用“包含左端、不包含右端”的半开规则：

~~~text
[00:00, 05:00) → 凌晨
[05:00, 08:00) → 清晨
[08:00, 12:00) → 上午
[12:00, 14:00) → 中午
[14:00, 18:00) → 下午
[18:00, 24:00) → 晚上
~~~

因此不存在同一个时间同时落入两段的问题。`24:00` 不作为同一 user-local-day 内的普通 timestamp；它等价于下一天的 `00:00`，进入下一日的 `凌晨`。

### 41.2 映射输入合同

D3b 不直接读取 UTC 数字、服务器时间或显示字符串，而消费已经通过 scope 检查的用户当地时间：

~~~text
trusted capture instant
+ timezone_and_day_scope_ref
→ user_local_timestamp
→ deterministic broad-period mapping
~~~

要求：

1. capture instant 的 provenance 合法；
2. timezone 与 user-local-day 已被上游明确解析；
3. 同一 mapping 使用 versioned policy，不依赖 Writer；
4. 缺少可信 timezone/day scope 时返回 contract diagnostic，不默认按服务器时区、当前所在地或 Sync 时区计算；
5. D3b 不从画面明暗、天气、店铺状态或语义内容改变固定时段映射。

例如一张照片 UTC 时间相同，但用户拍摄时所在时区不同，其当地 broad period 可以不同；D3b 必须依据该素材已经确认的 local-time scope，而不是用户今天打开 App 时的时区。

### 41.3 单点与单区间的确定性结果

1. **单点：** 合法 user-local timestamp 唯一映射到六段之一；
2. **完整落在同一段的 capture interval：** 可以得到单一 broad-period candidate；
3. **跨越分界的 capture interval：** 返回 `MULTI_PERIOD`，不能擅自采用开始时间所属段；
4. **多个 Chapter support points：** D3b 分别映射每个点，但不在本节决定最终取 dominant period 还是 compound label；
5. **Aha exact point：** 即使最终显示 exact point，仍可保留对应 broad period 作为合法 fallback；
6. **Aha peak 未定位、但整个 source interval 落在同一段：** broad-period fallback 可以使用该段；若 source interval 跨段，则留给 D3c 处理，不能只取视频开始段。

这保证词表映射与“多条证据怎样汇总”分离：D3b 只解决每个合法 temporal item 落在哪一段，D3c 才解决一个 Memory 横跨多个时段时怎么显示。

### 41.4 边界案例检查

| 用户当地时间 | 结果 | 原因 |
|---|---|---|
| 04:59:59 | 凌晨 | 尚未到 05:00 |
| 05:00:00 | 清晨 | 左端包含 |
| 07:59:59 | 清晨 | 尚未到 08:00 |
| 08:00:00 | 上午 | 左端包含 |
| 11:59:59 | 上午 | 尚未到 12:00 |
| 12:00:00 | 中午 | 左端包含 |
| 13:59:59 | 中午 | 尚未到 14:00 |
| 14:00:00 | 下午 | 左端包含 |
| 17:59:59 | 下午 | 尚未到 18:00 |
| 18:00:00 | 晚上 | 左端包含 |
| 23:59:59 | 晚上 | 仍属于当天 |
| 次日 00:00:00 | 次日凌晨 | 已切换 user-local-day |

#### 17:40 的古镇素材

中文 V1 固定映射为 `下午`。即使冬季画面已经很暗，也不能绕过合同改成 `晚上`；画面明暗不是可靠钟点 Evidence。

#### 19:30–19:32 的 Manual Video

若 Aha peak 尚未精确定位，但 source interval 完整落在 `晚上`，可以回退为 `晚上`，不能显示未经证明的 `19:30` exact point。

#### 17:59:40–18:00:20 的视频

若 peak 未定位，该 interval 同时触及 `下午`与`晚上`。D3b 输出 `MULTI_PERIOD`，不能因为视频从 17:59 开始就写成 `下午`，也不能因为结束于 18:00 后就直接写成 `晚上`。

#### 上午拍摄、晚上 Sync

素材当地拍摄时间为 10:24，22:00 才 Sync。映射仍为 `上午`；Sync time 不参与。

### 41.5 `傍晚`的处理

中文 V1 暂不把 `傍晚`做成仅凭固定钟点即可输出的第七段：它比其他词更依赖季节、地理位置与真实日落；而当前合同又禁止从画面明暗猜测。

案例：同样是 17:40，冬季北方可能已经接近夜晚，夏季南方仍可能日照很强，固定写成 `傍晚`并不总自然。后续只有满足以下至少一种条件时，才重新讨论：

1. 有可靠 locale/date/sunset Evidence 与明确成本合同；
2. 真实用户测试证明一个固定 `傍晚`区间的体验收益明显高于误称风险；
3. 产品愿意将 `傍晚`定义为纯语言习惯而非真实光照状态，并接受相应 locale 差异。

在重新确认之前，Writer、VLM 与显示层都不能自行生成 `傍晚`。

### 41.6 海外本地化边界

六段词表只适用于当前中文测试版，不直接翻译或复用到英文及其他海外 locale。海外 Production 至少须另行确认：

1. 各 locale 的自然 day-part vocabulary；
2. 固定区间还是 locale-specific 区间；
3. 12/24 小时制与 exact-point 格式；
4. timezone、DST、跨日与旅行场景；
5. UI 长度、无障碍读法与 locale-specific eval set；
6. release gate 与失败回退。

这与已经确认的海外 Title 守则一致：中文显示合同不是天然 locale-neutral；具体英文／多语言合同仍保持 deferred，必须在海外 Production 前单独完成。

### 41.7 最小映射结果

~~~text
BroadPeriodMappingResult
  temporal_source_ref
  input_kind = POINT | INTERVAL | SUPPORT_SET
  user_local_day
  timezone_and_day_scope_ref
  local_point_timestamp?
  local_interval_start?
  local_interval_end?
  mapping_state
    SINGLE_PERIOD
    | MULTI_PERIOD
    | INVALID_TIME_SCOPE
  resolved_period?
    凌晨 | 清晨 | 上午 | 中午 | 下午 | 晚上
  touched_periods[]
  policy_version
  provenance_refs[]
  diagnostic_reason?
  mapping_fingerprint
~~~

`MULTI_PERIOD` 不是错误，也不等于直接显示组合词；它只是明确告诉下一步：当前 temporal Evidence 跨过了至少一个已确认分界。

### 41.8 成本与执行边界

1. 六段映射是本地确定性逻辑，不调用 LLM、VLM 或外部 lookup；
2. 不新增媒体上传、抽帧、Raw／HQ 读取；
3. 只消费现有 capture timestamp 与 timezone/day-scope facts；
4. 词表与分界必须 versioned，方便真实数据测试后调整；
5. D3b 不改变 Chapter/Aha membership、boundary、continuity、Anchor 或媒体；
6. `傍晚`与海外合同的暂缓不阻断中文 V1 测试。

### 41.9 Invariants

1. 六段互斥且覆盖一个完整 user-local-day；
2. 边界时刻统一归入右侧新时段；
3. `24:00`归下一日，不同时属于两天；
4. 只按可信 user-local capture time 映射，不按 Sync/server/current-location time；
5. 不用画面明暗或内容语义绕过固定映射；
6. 跨段 interval 返回 `MULTI_PERIOD`，不默认归开始段或结束段；
7. `傍晚`在重新确认前不是合法中文 V1 输出；
8. 中文词表不直接作为海外 Production 合同；
9. 本节确认词表与单项映射，不冻结跨时段汇总规则、整个 D3 或 S11。

## 42. S11-D3c｜Conservative Cross-Period Display

**状态：CONFIRMED**

### 42.1 决策

中文测试版 V1 确认：

> Chapter 单时段优先；只有必要且证据充分时，才允许相邻双时段。Aha 不继承 Chapter 的双时段合同。

不考虑 prior published label 时，current Revision 的基础结果空间为：

~~~text
CHAPTER_SINGLE_PERIOD
CHAPTER_DUAL_ADJACENT_PERIOD
CHAPTER_CROSS_PERIOD_UNRESOLVED
CHAPTER_TEMPORAL_SCOPE_DIAGNOSTIC

AHA_EXACT_POINT
AHA_SINGLE_BROAD_PERIOD
AHA_CROSS_PERIOD_UNRESOLVED
~~~

`下午至晚上`在本节只是 `AFTERNOON_TO_EVENING` 的语义占位符。最终界面使用“至”“到”、连接符或其他自然表达，属于后续 formatter／UI copy 合同；不能让措辞选择反向改变算法判定。

本节与 D3c1 产生的是 current-revision **base decision**，不是跨 Revision 后的最终用户可见 decision。若 prior label 存在，D3f 可以在已确认的 25%–35% truthful stability band 内选择另一个仍受 current Evidence 支持的 continuity candidate；事实纠错、关系失效或候选 assertion 不存在时不得保留旧语义。

### 42.2 Chapter 单时段优先

满足任一条件时，Chapter 应优先保留单一 broad period：

1. 所有合法 temporal support 都落在同一时段；
2. 虽触及相邻时段，但其中一个时段具有明确 dominant support；
3. 另一时段只有极少、稀疏或边缘证据，不足以改变用户对 Chapter 主要发生时间的理解；
4. 两侧虽有内容，但缺少足以支持同一主线跨越分界的 relation/continuity Evidence；
5. 使用双时段会放大一个不重要的边界穿越，而不能提升时间定位价值。

单时段优先不是为了让 UI 更短而隐藏真实结构；它要求非主时段确实不足以成为用户理解该 Chapter 时间范围的重要组成部分。dominance 的归一化算法和阈值在 D3c1 确认。

### 42.3 Chapter 双时段资格

`CHAPTER_DUAL_ADJACENT_PERIOD` 必须同时满足：

1. 恰好涉及两个相邻 broad periods；
2. 两侧都存在当前 selected Chapter membership 内的合法 temporal support；
3. 两侧 support 都达到 D3c1 的 minimum-material-support gate；
4. 对首次构建／current base decision，没有任何一侧达到 dominant-period gate；已发布双时段仅能在 D3f 的 retention-only gate 内例外保留，不能反向改写本节 base decision；
5. 跨越时段分界的 same-Episode relation／Continuity Evidence 足够；
6. 不存在未解决的强 boundary contradiction；
7. 双时段比任一单时段更诚实地帮助用户定位这段经历；
8. 输出不会暗示算法看到了连续录像或活动每一分钟都未中断。

双时段的事实语义上限是：

> 当前 Chapter 在两个相邻时段内都具有充分、可追溯的同一 Episode 支持，并有合法关系连接两侧。

它不自动声称：

- 从第一个时段开始到第二个时段结束始终连续活动；
- observed first/last time 就是现实活动边界；
- 中间没有任何未拍摄空白；
- 所有中间素材都属于 Chapter；
- 用户主观感受在两个时段内保持不变。

### 42.4 可接受与不可接受的关系形态

#### 可进入双时段 gate

- 一个 `SINGLE` Moment 自身跨越时段分界，且现有 seam/Continuity Evidence 支持同一局部 Episode；
- `ADJACENT_GROUP` 或 `LOCAL_EPISODE_GROUP` 在分界两侧均有 content member，并已有明确 same-Episode link；
- 分界两侧没有 `INTERRUPTION_REF`、Blocker 或未解决的 boundary contradiction；
- 稀疏观测之间的关系已由上游支持，而不是 D3 根据时间接近重新推断。

#### 不自动进入双时段 gate

- `RESUMED_EPISODE`：它已经明确包含中断；使用“下午至晚上”可能让用户误读为未中断延续；
- 仅第一条在一个时段、最后一条在另一个时段，中间没有足够 support；
- 两侧只是地点、建筑风格、活动类型或 embedding 相似；
- 两侧属于不同故事，却因时间靠近被错误放在一个显示字符串里；
- 非相邻时段或三个以上时段；
- 需要 D3 修改 S05/S07/S09 membership 才能成立。

`RESUMED_EPISODE` 若未来需要表达两个不连续时段，应另行设计不会暗示连续性的 UI，例如并列式而不是“至”；当前不在 V1 双时段合同内。

### 42.5 Aha 的跨时段边界

Aha 保持 D3a 的独立粒度合同：

1. resolved peak timestamp 合法：显示 exact point；
2. peak 未定位，但整个合法 source/peak interval 落在一个 broad period：回退单一 broad period；
3. peak 未定位且合法 interval 跨越 broad-period boundary：返回 `AHA_CROSS_PERIOD_UNRESOLVED`；
4. 不按视频哪一侧时长更长猜 peak；
5. 不显示 `下午至晚上`这类双时段 Aha label；
6. unresolved 时按 D3c2 无感省略 Time Label；合同损坏仍进入明确 diagnostic，不能伪装成 omission。

案例：17:59:40–18:00:20 的视频内存在 Aha，但 peak frame 未解析。即使 18:00 后有 20 秒、之前也有 20 秒，仍不能猜是 `下午`或`晚上`，也没有必要显示一个覆盖 40 秒素材的双时段标签。

### 42.6 案例检查

#### 连续古镇 citywalk

同一次古镇 citywalk 从 16:40 延伸到 18:40，两侧都有充分 temporal support，跨 18:00 的 same-Episode relation 与 Continuity Evidence 均成立，没有明显 dominant period。可以进入 `AFTERNOON_TO_EVENING` 双时段候选。

这表示 Chapter 在下午和晚上都有充分支持，不表示系统拥有两小时连续录像。

#### 古街后进入奶茶店

17:50 仍在古街，18:05 已进入奶茶店并形成不同故事。即使时间相邻，也不能把两个故事拼成 `下午至晚上` Chapter；应服从既有 semantic boundary、Moment 与 selected membership。

如果 S09 已分别选为两个 Chapter，它们各自计算自己的 Time Label；D3 不重新合并。

#### 午餐跨过 12:00

午餐素材从 11:50 到 13:20，核心活动和绝大多数 normalized temporal support 都位于 `中午`。应显示 `中午`，不机械写成 `上午至中午`。

#### 下午游览、晚上恢复游览

下午古镇游览，中间进入奶茶店，晚上又回到古镇；S07/S09 可能合法形成 `RESUMED_EPISODE` Chapter。即使两侧分别位于 `下午`和`晚上`，当前也不直接使用带连续感的 `下午至晚上`。若一个时段明确 dominant，可显示该单时段；否则进入 cross-period unresolved，等待后续非连续表达或失败呈现合同。

#### 上午到晚上只有两条相似建筑素材

上午一张牌坊、晚上一张牌坊，即使视觉相似，也不生成 `上午至晚上`。非相邻时段与巨大未解释 gap 首先触发 temporal scope diagnostic；相似度不能补齐 Episode relation。

### 42.7 最小跨时段决策对象

~~~text
CrossPeriodDisplayDecision
  selected_memory_ref
  stable_memory_id
  revision_ref
  memory_type = CHAPTER | AHA
  broad_period_mapping_refs[]
  touched_periods[]
  temporal_support_summary_ref?
  dominant_period?
  cross_period_relation_state
    SAME_EPISODE_SUPPORTED
    | RESUMED_OR_INTERRUPTED
    | CONTRADICTED
    | UNRESOLVED
    | NOT_APPLICABLE
  base_decision_state
    CHAPTER_SINGLE_PERIOD
    | CHAPTER_DUAL_ADJACENT_PERIOD
    | CHAPTER_CROSS_PERIOD_UNRESOLVED
    | CHAPTER_TEMPORAL_SCOPE_DIAGNOSTIC
    | AHA_EXACT_POINT
    | AHA_SINGLE_BROAD_PERIOD
    | AHA_CROSS_PERIOD_UNRESOLVED
  selected_periods[0..2]
  semantic_label_key?
  time_label_candidate_semantic_specs[]
    semantic_label_kind
    semantic_label_key
    candidate_eligibility
      BASE_ELIGIBLE
      | CONTINUITY_RETAIN_ONLY
    semantic_support_basis_ref
  relation_evidence_refs[]
  boundary_contradiction_refs[]
  limitations[]
  policy_version
  decision_fingerprint
~~~

`semantic_label_key` 保存 base decision 的稳定语义，例如 `AFTERNOON_TO_EVENING`；它不保存 Writer 临时生成的中文字符串。`CONTINUITY_RETAIN_ONLY` 不是第二个 base result：它只表示该 semantic spec 在 current facts 下仍真实、可供 B0 materialize 为候选 assertion；没有匹配的 prior published semantic key 时，后置 D3f 不得选择。D3c/D3c1 output 位于 B0 之前，因此只输出 semantic specs 与 support basis，不能提前引用尚未生成的 B0 assertion refs。

### 42.8 成本与执行边界

1. D3c 只消费 selected membership、现有 temporal mapping、Continuity/Boundary Evidence 与 S07 relation refs；
2. 不重新读取 Raw/HQ，不新增上传、抽帧、VLM、LLM 或 embedding；
3. 不按双时段需求回写 S05 seam、S07 Candidate 或 S09 selected set；
4. 跨时段状态通过确定性、versioned rule 产生；
5. 三个以上或非相邻时段进入 diagnostic 不会增加模型成本；
6. D3c 不决定最终中文连接词，也不建立海外 locale 合同。

### 42.9 Invariants

1. Chapter 单时段优先，相邻双时段是有证据门槛的例外；
2. 双时段只覆盖两个相邻 broad periods；
3. 第一／最后素材不能直接生成双时段；
4. 双时段需要两侧 material support 与 same-Episode relation，不靠相似度或时间接近；
5. `RESUMED_EPISODE` 不自动使用暗示连续性的“至”式标签；
6. 非相邻或三个以上时段不生成过宽组合词；
7. Aha 不使用 Chapter 的双时段合同；
8. 双时段不声称连续录像、完整 duration 或真实起止边界；
9. D3c 不改变任何上游 membership、boundary、relation 或媒体；
10. 本节确认显示原则，不冻结 temporal-support 归一化参数、整个 D3 或 S11。

## 43. S11-D3c1｜Normalized Temporal Support & Dominance Gate

**状态：CONFIRMED**

本节定义不受 Auto／Manual 采集密度影响的 `Normalized Temporal Support`，再计算 dominant period 与双时段资格。

### 43.1 V1 Baseline

确认使用“5 分钟 temporal support cell”，而不是直接数照片、视频或 Window：

~~~text
current S09 selected Chapter membership
→ eligible KEEP content Window temporal refs
→ project each trusted support time into user-local 5-minute cell
→ cap each cell at one temporal-support unit
→ aggregate occupied cells by broad period
→ dominance / dual-period gates
~~~

基础规则为：

1. 只使用 current Revision、current selected Chapter membership 内的合法 KEEP content temporal refs；
2. `CONTEXT_ONLY`、`DROP_FROM_MEMORY_OUTPUT`、interruption refs、rejected Candidate 与 selected Chapter 之外的全天素材不增加正向 support；
3. 不使用 S10 最终 3–5 个精选媒体计数，因为媒体编辑会人为改变时间分布；
4. 同一 5 分钟 cell 内无论有 1 条 Auto、5 张 Manual Photo 还是多条重复 Evidence，时间分布贡献最多为 1；
5. 没有观测的 cell 保持空白，不用前后素材填满中间时间；
6. support cell 只表示“该 5 分钟格内存在合法观测”，不声称活动持续了 5 分钟；
7. cell 必须按 user-local-day 与六段边界对齐，不能跨 broad-period boundary；
8. `cell_width=5min`、dominance threshold 与 minimum-support 都是 versioned calibration parameters，不是自然常数。

选择 5 分钟的理由：它大于 Auto 的 2 分钟采样周期，通常能把同一小段内 2–3 条 Auto 压成一个 support unit；同时又没有 10–15 分钟 cell 那么粗，不至于明显吞掉短 Chapter 跨越时段边界的结构。

### 43.2 初始判定门

~~~text
support_cell_width = 5 minutes
dominant_period_share_min = 0.70
dual_period_minor_share_min = 0.30
dual_period_min_cells_each_side = 2
dual_period_max_period_count = 2
dual_period_requires_adjacent_periods = true
dual_period_requires_same_episode_relation = true
~~~

current Revision 的 base decision 执行顺序为：

1. 只触及一个时段：`CHAPTER_SINGLE_PERIOD`；
2. 触及非相邻时段或三个以上时段：`CHAPTER_TEMPORAL_SCOPE_DIAGNOSTIC`，不先算多数票；
3. 恰好触及两个相邻时段，任一侧 share ≥ 70%：选择该 dominant 单时段；
4. 没有一侧达到 70%，两侧各至少 2 个 occupied cells、minor share ≥ 30%，且 same-Episode relation gate 通过：`CHAPTER_DUAL_ADJACENT_PERIOD`；
5. 一侧只有 1 个 cell 且另一侧 cell 数更多：将少数侧视为稀疏边缘支持，选择 cell 较多的单时段，并记录 `SPARSE_MINOR_PERIOD_COLLAPSED`；
6. 两侧各只有 1 个 cell、数量相同或 relation 不足：`CHAPTER_CROSS_PERIOD_UNRESOLVED`，不靠随机 tie-break；
7. `RESUMED_EPISODE` 即使比例满足，也不通过当前“至”式 same-Episode relation gate；
8. Aha 不运行 cell dominance；继续使用 exact point／单段 interval／cross-period unresolved 三态。

70% 与 30% 在同一个 normalized support denominator 上计算；70/30 的临界情况按单时段优先处理，避免同一输入同时命中两个 base result。

为了让后置 D3f 保持稳定、同时不允许它凭空创造 assertion，B0 还可在同一 current Evidence 上 materialize 两类 `CONTINUITY_RETAIN_ONLY` 候选：

1. **dual-retention-eligible candidate：** minor share ≥25%、两侧各至少 2 cells、恰好相邻、same-Episode relation 仍成立且无 contradiction；即使 base decision 因 dominant 70% 已选择 single，该 dual assertion 仍可作为“当前仍真实但只允许保留既有双时段”的候选；
2. **single-retention-eligible candidate：** minor share <35%、该 single key 对应 current majority period、两侧各至少 2 cells、same-Episode relation 仍成立且无 contradiction；即使 base decision 已在 30%–35% 区间选择 dual，该 single assertion 仍可作为“当前仍真实但只允许保留既有单时段”的候选；
3. continuity-only candidate 没有匹配的 prior published semantic key 时不可选择，也不能用于首次构建；
4. B0 建候选时不读取 prior artifact；candidate 只表示当前 Evidence 允许保留该语义，最终 retain／replace 才由 D3f 结合 prior artifact 决定。

### 43.3 案例预演

#### Manual 连拍不能制造 dominant period

17:52 用户连续拍了 10 张相似 Manual Photo；18:05、18:10、18:15 各有合法 Auto/Manual content support。

不能计算为：

~~~text
下午 10 : 晚上 3
~~~

归一化后，17:52 的连拍只占一个 5 分钟 cell；晚上占三个不同 cells。若其余 Chapter/continuity 条件合法，时间分布不会被一次连拍扭曲为“下午占绝对多数”。

#### 两小时古镇 citywalk

16:40–18:40 的合法 support 大致形成：

~~~text
下午 16 cells
晚上  8 cells
share ≈ 67% / 33%
~~~

两侧均超过 2 cells，minor share 超过 30%，且 same-Episode relation 成立，因此可以形成 `下午至晚上`双时段候选。

#### 午餐跨过 12:00

11:50–13:20 大致形成：

~~~text
上午  2 cells
中午 16 cells
share ≈ 11% / 89%
~~~

`中午`达到 dominant gate，最终仍为单时段。

#### 只有两个稀疏点

17:56 一条、18:03 一条，两侧各只有一个 cell。即使语义相似，也不足以证明双时段对用户有价值；返回 cross-period unresolved，不用 first/last 拼接。

#### 古街与奶茶店各自素材很多

下午古街与晚上奶茶店各有大量 occupied cells，但上游 boundary 表明它们是不同故事。数量再多也不能通过 same-Episode relation gate，更不能靠 50/50 比例合并成一个双时段 Chapter。

### 43.4 成本判断

高强度参考日约 220 个 Window。建立 occupied-cell set 与六段计数是线性、内存级计算：

~~~text
time  = O(number of eligible temporal refs)
space = O(number of occupied 5-minute cells)
~~~

不增加上传、抽帧、VLM、LLM、embedding 或 HQ 成本；主要成本是实现与真实数据校准，而不是云端算力。

### 43.5 Canonical Temporal Support Point

每个 eligible support Window 必须先解析成一个确定性的 `canonical_temporal_support_point`，再进入 5 分钟 cell。优先级为：

1. Manual Photo／`STILL_ASSET`：使用可信 capture timestamp；
2. Video Window：优先使用该 KEEP content unit 的 primary grounded `EvidenceRef` 实际 source/decode timestamp；
3. 若没有合法 primary Frame timestamp，但整个 normalized Window 是 current membership 内的 eligible KEEP content Window，才允许使用其 capture interval midpoint；
4. capture interval、timezone 或 day scope 不合法时，该 Window 不产生正向 temporal support，并保留 exclusion reason；
5. 同一 Window 的多个 Facts／Frames 不生成多个 support points；
6. 同一 RawAsset 的多个、已被 S07 合法保留的 distinct Manual Windows 可以分别产生 point，但落在同一 cell 后仍只计一次；
7. 不使用 S10 最终 EvidenceAnchor 或精选媒体来选择 support point，避免编辑结果反向改写 Chapter 的整体时间分布。

这里允许 Window midpoint，只因为该 Window 本身已经是 selected Chapter membership 内的合法 KEEP content Window；midpoint 只用于落入 cell，不成为 exact Aha point，也不证明现实活动边界。

### 43.6 Cell Construction 与计数

~~~text
cell_index
  = floor(minutes_since_user_local_day_start / 5)

cell_key
  = (user_local_day, cell_index, broad_period)
~~~

规则：

1. 一个 support point 只进入一个 cell；
2. 同一 cell 可以保存多个 provenance refs，但 `occupied_weight = 1`；
3. 5 分钟 grid 从 user-local-day 的 00:00 开始；当前六个 broad-period boundaries 都与 grid 对齐，因此一个 cell 不跨两个 period；
4. 空 cell 不补零时长、不向前后扩张，也不被 Continuity Evidence 自动填满；
5. `period_support_count` 等于该 period 的 occupied cell 数；
6. `period_support_share = period_support_count / total_occupied_cell_count`；
7. relation gate 独立于 share 计算；足够数量不能覆盖 boundary contradiction；
8. 完全相同的 inputs 与 policy version 必须产生相同 cells、shares 与 decision。

### 43.7 最小归一化结果

~~~text
NormalizedTemporalSupportSummary
  selected_chapter_ref
  stable_memory_id
  revision_ref
  s09_run_identity_ref
  user_local_day
  timezone_and_day_scope_ref
  eligible_temporal_support_refs[]
  excluded_temporal_support_refs[]
    temporal_ref
    exclusion_reason
  support_cell_width = PT5M
  occupied_cells[]
    cell_key
    broad_period
    canonical_support_point_refs[]
    source_window_refs[]
    occupied_weight = 1
  period_support[]
    broad_period
    occupied_cell_count
    support_share
  touched_periods[]
  dominant_period_candidate?
  dominant_gate_pass
  dual_period_material_gate_pass
  cross_period_relation_decision_ref?
  base_cross_period_decision_ref
  continuity_candidate_semantic_specs[]
  threshold_policy_version
  support_summary_fingerprint
~~~

`excluded_temporal_support_refs[]` 必须保留原因，例如 `NOT_SELECTED_MEMBERSHIP`、`CONTEXT_ONLY`、`DROP_FROM_MEMORY_OUTPUT`、`INTERRUPTION_REF`、`INVALID_TIME_SCOPE` 或 `NO_CANONICAL_SUPPORT_POINT`；不能只删除记录后让 denominator 悄悄变化。

### 43.8 参数版本与真实数据调整

V1 确认：

~~~text
support_cell_width = 5 minutes
dominant_period_share_min = 0.70
dual_period_minor_share_min = 0.30
dual_period_min_cells_each_side = 2
dual_period_max_period_count = 2
dual_period_requires_adjacent_periods = true
dual_period_requires_same_episode_relation = true
~~~

这些数值是可执行 Baseline，不是永久自然常数。未来只允许通过：

1. 真实用户时间线与素材导入；
2. Gold Time Label／人工标签；
3. 单时段误判率、双时段过度生成率与 unresolved 率；
4. Auto／Manual 密度分层评测；
5. 用户对定位准确性与自然度的评分；
6. 新的 versioned Checkpoint；

来调整。不得在 Production 中无版本热改阈值，使同一 Revision 无法回放。

### 43.9 Invariants

1. 不按 RawAsset、照片、视频、Frame 或精选媒体数量直接投票；
2. 同一 5 分钟 cell 的正向 temporal weight 永远不超过 1；
3. cell occupancy 是证据分布，不是 5 分钟活动 duration；
4. 只使用 current selected Chapter membership 内的合法 KEEP content temporal refs；
5. context、drop、interruption 与未选全天素材不增加正向 support；
6. 视频优先使用 primary grounded EvidenceRef timestamp，midpoint 仅作受限 fallback；
7. 不填补未观测 cell，不用 Continuity Evidence 伪造连续时间覆盖；
8. dominance 数量门与 same-Episode relation gate 相互独立，二者都必须通过；
9. Aha 不运行 Chapter cell dominance；
10. D3c1 只产生 current base decision 与 current candidate envelope；最终跨 Revision 可见选择属于 D3f；
11. 参数变化必须 versioned、可回放并经过真实数据 Benchmark；
12. 本节确认归一化与初始阈值，不冻结失败呈现、整个 D3 或 S11。

## 44. S11-D3c2｜Nullable Time Label & Surface-Level Omission

**状态：CONFIRMED**

### 44.1 决策

当 Time Label 自身无法安全决定时，采用 surface-level omission：

> 如果 Memory 本身、媒体与 Narrative 均合法，只是 Time Label 落入 `CROSS_PERIOD_UNRESOLVED`，则保留 Chapter／Aha，但省略 Time Label；不显示“当天”“时间未知”等低价值占位，也不要求用户处理。

正式区分三类结果：

| 情况 | 建议处理 | 是否影响 Memory 本体 |
|---|---|---|
| 时间标签证据不足，但 selected Memory 仍合法 | `TIME_LABEL_OMITTED_EVIDENCE_UNRESOLVED` | 不阻断 Chapter/Aha |
| 当前数据暂少，后续 Revision 可能补足 | 当前无感省略，后续重新计算 | 不要求用户交互 |
| timezone/day identity、Revision 或引用合同损坏 | `TIME_LABEL_CONTRACT_INVALID`，返回责任阶段 | 若已无法确认属于哪一天，不允许用错误日期正常发布 |

不建议显示 `当天`，因为 Diary 页面本来已经处于当天，它几乎没有定位价值，还会掩盖算法实际没有得出 Time Label。也不建议强选一个时段，因为那会把排版一致性放在 temporal truth 之前。

### 44.2 结构化空值合同

Time Label 省略必须是显式状态，而不是一个内容不明的空字符串：

本节定义 final surface outcome 的状态形状，不表示 D3c2 会在 C2／D3f 之前提前生成用户字符串。该 outcome 只有在 D3f 已完成、且 PRESENT 分支已由 D3e formatter 处理后才封装。

~~~text
TimeLabelSurfaceOutcome
  selected_memory_ref
  stable_memory_id
  revision_ref
  memory_type = CHAPTER | AHA
  outcome_state
    TIME_LABEL_PRESENT
    | TIME_LABEL_OMITTED_EVIDENCE_UNRESOLVED
    | TIME_LABEL_CONTRACT_INVALID
  rendered_label?                    # PRESENT 时必填；其他状态必须为空
  formatted_time_label_ref?          # PRESENT 时必填
  semantic_label_key?                # PRESENT 时必填
  selected_time_label_assertion_ref? # PRESENT 时必填，且必须属于 current Revision
  omission_permission_ref?           # OMITTED 时必填
  omission_reason?                   # OMITTED 时必填
  contract_failure_owner?            # CONTRACT_INVALID 时必填
  source_time_label_revision_decision_ref
  source_c3a_continuity_decision_ref
  user_interaction_required = false
  policy_version
  outcome_fingerprint
~~~

要求：

1. `TIME_LABEL_OMITTED_EVIDENCE_UNRESOLVED` 是合法产品结果，不等于工程失败；
2. `rendered_label` 缺席时仍必须带明确 outcome state；不能只传 `""`、空格或 `null` 让客户端猜语义，也不传“当天／未知”占位；
3. Writer 不得为填满 UI 自行生成时间；
4. E/S12 验证当前结果与 selected current assertion／omission permission 一致，防止接口已省略但界面仍展示旧 label；
5. App 的正式 presentation contract 未来必须支持 Time Label nullable 并自然收起对应空间，但本节不修改 App；
6. 省略只影响 Time Label surface，不删除 Title、Story、Tag、媒体、Chapter/Aha identity 或 selected membership。

### 44.3 普通 unresolved 与合同损坏分离

#### 普通 Evidence unresolved

以下情况可以只省略 Time Label：

- Chapter 两侧 temporal support 太稀疏；
- 同一 Chapter 的 cross-period relation 仍不足；
- Aha source interval 跨时段，但 peak 未定位；
- legitimate long/resumed Chapter 暂无安全的单段、双段或 exact range；
- 当前 Preview Evidence 尚少，Final 或后续 Revision 可能解决。

前提是 selected Memory 的 day identity、membership、媒体与 Narrative 合同仍然合法。

#### Temporal contract invalid

以下不能伪装成普通省略：

- capture instant 无法解析或与 provenance 冲突；
- timezone/day scope 损坏，导致无法确认 user-local-day；
- Revision、selected memory、Evidence 或 assertion refs 不一致；
- 当前 label 指向 stale Anchor／旧 policy result；
- 同一 Memory 的时间事实自相矛盾且影响日期归属。

若问题已经影响“这条 Memory 属于哪一天”，受影响 Memory 不能在可能错误的日期走正常发布路径，必须返回明确责任阶段。若 day identity 仍可靠、只是更细 label 的局部引用损坏，仍须先修复合同；不能把工程错误解释为“证据不足”。

### 44.4 Revision 行为

1. Preview 当前 unresolved：无感省略，不弹窗、不新增上传交互；
2. 后续 Evidence 到达：在新 Revision 重新运行确定性 D3 decision；
3. 新 Revision 解决后，Time Label 可以自然出现；
4. 旧 label 在当前 Evidence 下仍合法时可以保持；
5. 旧 label 已不受 current active projection 支持时必须移除，不能为了视觉稳定保留 stale assertion；
6. 具体跨 Revision retain/replace/add/omit 已由既有 C3a 总原则与 D3f Time Label 专用合同确认；D5 属于 Tags，不承担 Time Label 连续性。本节继续只负责 truth-first 与无感省略行为。

### 案例 A｜Chapter 两侧各一个稀疏点

17:56 与 18:03 各一条合法 support，仍不足以决定单时段或双时段。Chapter 的 Title、Story 与媒体均合法：保留 Chapter，Time Label 留空；不显示随机选择的 `下午`或`晚上`。

### 案例 B｜Aha 视频跨过 18:00

视频为 17:59:40–18:00:20，peak 未解析。Aha 独立价值与媒体均合法：保留 Aha，省略 Time Label；不显示双时段，也不请求补帧。

### 案例 C｜晚到素材解决了问题

Preview 时只有两个稀疏点，因此无 Time Label。后续无感 Sync 带来更多 current Revision Evidence，达到 `晚上` dominant gate；新 Revision 可以自然出现 `晚上`，不弹窗、不要求用户重新操作。

### 案例 D｜拍摄时区损坏

素材 capture instant 与 timezone/day scope 相互矛盾，连它属于哪一个 user-local-day 都无法确认。这不是普通“标签不好算”，而是 temporal contract invalid；不能只隐藏标签后把 Memory 发布到可能错误的日期。

### 44.5 成本与执行边界

1. 省略结果不新增模型、上传、取源或补帧成本；
2. 不为了避免 UI 空位而扩大 Evidence scope；
3. 不修改 S09 membership、S10 media、其他 S11 surfaces 或全天数量；
4. 不触发用户确认弹窗；
5. nullable presentation 的 App 实现属于后续正式 App 工作，不在本算法仓库改动范围内。

### 44.6 Invariants

1. Time Label 可以为空；Memory 不因普通时间证据不足而被牺牲；
2. 不显示“当天”“时间未知”或 Writer 补写的占位；
3. 结构化 omission 与 contract invalid 必须分离；
4. 省略不改变其他 surface、identity、membership 或媒体；
5. later Revision 可以无感补出 label；
6. current Evidence 不再支持旧 label 时不得保留 stale assertion；
7. user-local-day 身份损坏不能只靠隐藏标签掩盖；
8. 本节确认失败呈现原则，不冻结 exact-range gate、App UI、整个 D3 或 S11。

## 45. S11-D3d｜Chapter Exact Range Eligibility Gate

**状态：CONFIRMED**

### 45.1 决策

中文 V1 保留 exact range 能力，但它是稀有、白名单式结果：

> 普通 camera-derived Chapter 默认不显示精确起止范围。只有“真实开始”和“真实结束”都由可追溯的 actual boundary Evidence 证明，且它们属于同一 Chapter Episode，才允许显示例如 `14:00–15:30`。

不考虑 prior published label 时，Chapter Time Label 的 base eligibility 优先级为：

~~~text
CHAPTER_EXACT_RANGE, only after D3d PASS
→ otherwise existing CHAPTER_SINGLE_PERIOD
→ otherwise existing CHAPTER_DUAL_ADJACENT_PERIOD
→ otherwise TIME_LABEL_OMITTED_EVIDENCE_UNRESOLVED
~~~

exact range 不能因为视觉上“更专业”而越过 gate；一旦合法通过，它可以取代 broad/dual label，因为此时真实起止范围比宽时段提供更多且不失真的定位价值。

D3d PASS 必须在 B0 中 materialize 为 current exact-range composite assertion，再经过 B2／C2；D3f 看到该 current candidate 后执行 truth-first replacement，随后在适用时进入 B3。D3f 不能读取两个 boundary 后自行拼接一个未经过 assertion 链的 range。

### 45.2 允许的 boundary sources

至少满足以下一种完整 boundary pair：

1. **`USER_CONFIRMED_ACTUAL_INTERVAL`：** 用户已经明确确认现实活动实际从何时开始、何时结束；不是系统临时要求用户补填；
2. **`TRUSTED_ACTUAL_START_STOP_PAIR`：** purpose-built app/device 已记录同一现实活动的实际 start/stop，并有稳定 event identity 与 provenance；
3. **`VERIFIED_ENTER_EXIT_PAIR`：** grounded entering/leaving Evidence 明确对应同一地点／活动 scope，时间可追溯，中间 same-Episode relation／Continuity Evidence 合法，且没有 boundary contradiction。

当前产品没有某种 source 时，不为 exact range 新增集成、外部 lookup 或用户交互；它只表示未来该 source 存在时的资格合同。

### 45.3 明确禁止的替代品

以下都不能单独或互相拼接成 Chapter exact range：

1. Chapter 第一条与最后一条素材时间；
2. `observed_first_timestamp / observed_last_timestamp`；
3. Auto 每两分钟采样覆盖；
4. Manual Photo 时间或 Manual Video capture interval；
5. Calendar、行程表、预约或课程表中的计划时间，除非另有 actual confirmation；
6. Sync、upload、ingest、analysis 或 publish time；
7. 一个真实 boundary 加另一个推测 boundary；
8. 从 time gap、画面明暗、地点相似或内容进展推测出的起止分钟；
9. 5 分钟 temporal support cells 的首尾；
10. Writer 为文案完整而补出的整点。

### 45.4 完整 gate

~~~text
actual_start_boundary_ref exists
AND actual_end_boundary_ref exists
AND both boundary refs are current and provenance-valid
AND both assert ACTUAL, not PLANNED time
AND both resolve to the same Chapter Episode identity/scope
AND start < end
AND both remain inside the current user-local-day
AND boundary precision supports the display precision
AND each boundary's possible-time interval maps to one stable display-minute bucket
AND floor_to_minute(start) < floor_to_minute(end)
AND continuity / same-Episode relation is sufficient
AND no unresolved boundary contradiction
AND Chapter form is not an interrupted RESUMED_EPISODE
→ CHAPTER_EXACT_RANGE_ELIGIBLE

otherwise
→ retain existing broad/dual/omitted outcome
~~~

分钟级 `HH:mm–HH:mm` 显示要求每个 boundary 的语义不确定上限不超过 60 秒，并且其全部可能时间必须落在同一个 display-minute bucket 内。仅有“≤60 秒”仍不够：例如一个可能范围跨过 13:59 与 14:00，就不能安全决定显示哪一分钟。两个 boundary 即使真实有序，若 floor 后落在同一个 displayed minute，也不能生成 `20:17–20:17`；D3d 应直接 `NOT_ELIGIBLE` 并保留既有 broad/omitted fallback，而不是让 formatter 临时重选粒度。设备 timestamp 有秒值但 boundary 语义本身模糊时仍不能通过。通过 gate 后，秒数如何转成分钟字符串才由 D3e formatter 执行。

`NOT_ELIGIBLE` 与 `CONTRACT_INVALID` 必须分开：合法 Evidence 只是没有满足白名单时，正常回到 broad/dual/omitted；boundary ref 损坏、actual/planned 类型矛盾或 Revision scope 错乱时，返回责任阶段，不能伪装成普通“不够精确”。

### 45.5 案例检查

#### 用户确认实际课程时间

用户已有确认记录：课程实际 14:00 开始、15:30 结束；两侧 boundary、scope、timezone 与中间 Episode 均通过。可以成为 `14:00–15:30` exact-range candidate。

#### Calendar 只写了计划时间

日程写着课程 14:00–15:30，但用户可能迟到或提前离开，素材也没有 actual boundary。不能显示 exact range；回到 `下午`。

#### 古镇素材首尾很密集

09:02–10:58 每两分钟都有 Auto Observation，但没有真实进入／离开 Evidence。仍显示 `上午`，不能显示 `09:02–10:58`。

#### 真实进入与离开

09:06 有 grounded 进入景区 gate，11:03 有 grounded 离开同一景区 gate；两者属于同一 visit identity，中间 continuity 与 scope 合法，没有冲突。可以进入 exact-range gate；最终分钟格式仍由 formatter 决定。

#### 两分钟晚餐视频

Manual Video 为 19:30–19:32，但只是晚餐 Chapter 中的一段。它只证明媒体 capture interval，不能把 Chapter 显示为 `19:30–19:32`；回到 `晚上`。

#### 真实但落在同一分钟的短区间

actual start 为 20:17:08、actual end 为 20:17:49，两者都真实、可追溯且属于同一 Episode，但中文 V1 分钟格式会把两端都映射为`20:17`。因此 D3d 判定 exact range `NOT_ELIGIBLE`，继续使用合法 broad/omitted fallback；不能把`20:17–20:17`交给 formatter 后再让 formatter猜测替代语义。

#### 下午游览、晚上恢复

古镇活动中间被奶茶店打断，之后恢复，形成 `RESUMED_EPISODE`。即使 A/C 各自有时间，也不能用一个连续 exact range 覆盖中断；当前继续使用安全 broad label 或 omission。

### 45.6 最小资格决策

~~~text
ChapterExactRangeEligibilityDecision
  selected_chapter_ref
  stable_memory_id
  revision_ref
  chapter_form
  user_local_day
  timezone_and_day_scope_ref
  start_boundary_assertion_ref?
  end_boundary_assertion_ref?
  boundary_pair_class?
    USER_CONFIRMED_ACTUAL_INTERVAL
    | TRUSTED_ACTUAL_START_STOP_PAIR
    | VERIFIED_ENTER_EXIT_PAIR
  start_actualness_check
  end_actualness_check
  start_semantic_uncertainty_seconds?
  end_semantic_uncertainty_seconds?
  start_minute_bucket_stability_check
  end_minute_bucket_stability_check
  distinct_ordered_display_minutes_check
  same_episode_identity_check
  continuity_and_scope_check
  boundary_contradiction_check
  same_user_local_day_check
  ordered_interval_check
  resumed_episode_exclusion_check
  decision_state
    CHAPTER_EXACT_RANGE_ELIGIBLE
    | CHAPTER_EXACT_RANGE_NOT_ELIGIBLE
    | CHAPTER_EXACT_RANGE_CONTRACT_INVALID
  exact_start_timestamp?
  exact_end_timestamp?
  fallback_time_label_decision_ref?
  reason_codes[]
  boundary_policy_version
  decision_fingerprint
~~~

`CHAPTER_EXACT_RANGE_ELIGIBLE` 时 start/end、pair class 与全部 checks 必须完整；`NOT_ELIGIBLE` 必须引用既有 broad/dual/omitted fallback；`CONTRACT_INVALID` 必须指定失败 owner，不能产出用户可见 range。

### 45.7 跨日与非连续 Episode

1. 当前 Daily Memory V1 exact range 只覆盖同一 user-local-day；
2. 跨午夜 Episode 不被截成两个虚假 exact boundaries，也不显示 `23:30–00:30`；其跨日归属与显示保持后续开放；
3. `RESUMED_EPISODE` 的 A/C 中间存在 interruption，不能用单一连续 range 覆盖；
4. 未来若设计多段 interval presentation，必须使用新的明确语义与 UI，不复用本节单 range；
5. 本节不改变 S07/S09 已选 Chapter form。

### 45.8 成本判断

该 gate 只消费已有 boundary assertions、timezone/day scope、Chapter identity 与 Continuity Evidence，全部为确定性验证；不新增 VLM、LLM、上传或传感器读取。绝大多数普通相机 Chapter 会快速落回 broad period，不产生额外云端算力压力。

### 45.9 Invariants

1. exact range 是白名单例外，camera-derived broad period 仍是默认；
2. start 与 end 都必须是 actual、current、可追溯 boundary；
3. planned time 不等于 actual time；
4. first/last observation、Manual capture interval 与 temporal cells 不成为现实活动边界；
5. 两个 boundary 必须属于同一 Chapter Episode identity/scope；
6. 单边真实、另一边推测仍不合法；
7. minute display 的 boundary semantic uncertainty 均不得超过 60 秒，每个可能时间区间只能落入一个稳定 minute bucket，且 start/end 映射后的 displayed minutes 必须严格递增；
8. `RESUMED_EPISODE` 与跨日 Episode 不使用当前单一 exact range；
9. `NOT_ELIGIBLE` 正常回退，`CONTRACT_INVALID` 不得伪装成普通回退；
10. 不为 exact range 新增用户交互、外部集成或模型调用；
11. 本节确认 eligibility；formatter 已由 D3e 单独确认，跨日、多段范围、整个 D3 或 S11 仍未在本节冻结。

## 46. S11-D3e｜Chinese V1 Time Label Formatter

**状态：CONFIRMED**

### 46.1 决策

中文测试版采用以下显示合同：

虽然 D3e 在讨论中先于 D3f 确认，Production 必须先完成 C3a＋D3f continuity selection，并在适用时通过 B3，formatter 才能运行。章节编号不代表执行顺序。

| 语义类型 | 格式 | 案例 |
|---|---|---|
| Aha exact point | 24 小时制 `HH:mm` | `09:06`、`20:17` |
| Chapter exact range | `HH:mm–HH:mm`，无空格 | `14:00–15:30` |
| Chapter/Aha single broad period | 六段中文词 | `上午`、`晚上` |
| Chapter dual adjacent period | `{左时段}到{右时段}` | `下午到晚上` |
| omitted | 不渲染字符串 | 无占位 |

### 46.2 使用“到”而不是“至”或分隔点

- `下午到晚上`比`下午至晚上`更自然、少一些说明书语气；
- `下午 · 晚上`容易被理解为两个并列标签，而不是同一 Chapter 跨过相邻时段；
- D3c 已经用 same-Episode gate 控制连续性风险，因此 formatter 不需要用含糊分隔符再次回避语义；
- 这是 Time Label 的简短元数据，不进入 Story 的文学表达。

### 46.3 分钟格式

1. 小时固定两位，使用 `09:06`而不是`9:06`，保证列表对齐与稳定宽度；
2. 使用 24 小时制，不同时显示“上午 09:06”或 AM/PM；
3. 不显示秒；
4. source timestamp 映射到其所在分钟，采用 floor/truncate，不四舍五入到下一分钟；
5. 因此 `20:17:59` 显示为 `20:17`，它表示该 Evidence 位于 20:17 这一分钟内，不表示正好发生在 20:17:00；
6. range 两端使用相同分钟规则，例如 `14:00:42–15:30:20`显示为`14:00–15:30`；
7. D3d 必须已经排除 start/end 落入同一 displayed minute 的 candidate；formatter 若仍收到这类输入，应返回 format contract invalid，不能自行回到 broad/omitted 或输出`20:17–20:17`；
8. exact range 使用 en dash `–`，两侧不加空格；
9. formatter 不加入“约”“左右”“大概”等新断言；Evidence 不够精确时应在 D3d 失败，而不是靠模糊词补救。

### 46.4 案例检查

#### Aha 在一分钟末尾发生

实际 peak timestamp 为 20:17:59.300，显示 `20:17`，不能四舍五入为 `20:18`。

#### Chapter exact range

actual start 为 09:06:21，actual end 为 11:03:48，且 D3d 已通过，显示 `09:06–11:03`。

#### 相邻双时段

D3c 已确定 `AFTERNOON_TO_EVENING`，显示 `下午到晚上`；不因为画面很暗改成包含未确认`傍晚`的文字。

#### Time Label 省略

D3c2 输出 omission state，formatter 不生成空格、破折号、“当天”或“未知”。

#### 非法的同一分钟 range 输入

若上游错误传入 20:17:08–20:17:49，formatter 不输出`20:17–20:17`，也不擅自改成`晚上`；它返回 `TIME_LABEL_FORMAT_CONTRACT_INVALID`，由责任链回到 D3d／B0/C2 修复。

### 46.5 Formatter 输入输出

~~~text
FormattedTimeLabel
  selected_memory_ref
  stable_memory_id
  revision_ref
  source_time_label_revision_decision_ref
  selected_time_label_assertion_ref
  source_b3_composition_decision_ref?
  semantic_label_kind
    AHA_EXACT_POINT
    | CHAPTER_EXACT_RANGE
    | SINGLE_BROAD_PERIOD
    | DUAL_ADJACENT_PERIOD
  semantic_label_key
  locale = zh-CN-test-v1
  timezone_and_day_scope_ref
  source_point_timestamp?
  source_range_start_timestamp?
  source_range_end_timestamp?
  minute_conversion = FLOOR_TO_CONTAINING_MINUTE
  display_string
  formatter_policy_version
  format_fingerprint
~~~

`TIME_LABEL_OMITTED_EVIDENCE_UNRESOLVED` 不生成 `FormattedTimeLabel`，但继续保留 D3c2 的 `TimeLabelSurfaceOutcome`。formatter 必须消费 D3f 最终选择的 current `selected_time_label_assertion_ref`；不能直接格式化 C2 base result，也不能格式化只属于 prior Revision 的 stale assertion。formatter 只把已确认语义变成字符串；它不能选择另一时段、改变 exact/broad 粒度或修复上游 Evidence。

`FormattedTimeLabel` 只代表成功 artifact。若 semantic kind、selected assertion、minute ordering、locale/policy 或 Revision refs 不满足合同，formatter 输出独立 `TIME_LABEL_FORMAT_CONTRACT_INVALID` diagnostic，且不生成 `FormattedTimeLabel`；final `TimeLabelSurfaceOutcome` 必须进入 `TIME_LABEL_CONTRACT_INVALID`，不能降级为 omission。

`format_fingerprint` 必须覆盖 semantic key、locale、minute conversion、separator、zero-padding 与 formatter version；只比较最终字符串不足以区分语义来源。

### 46.6 海外与 App 边界

该格式只适用于中文测试版。英文／海外 Production 必须单独确认 12/24 小时制、locale formatter、day-period words、range separator、数字方向、无障碍读法和布局；不能机械翻译。

本节只定义算法输出语义与参考显示字符串，不修改正式 App。App 端字体、间距、VoiceOver 与组件收起行为属于后续 App presentation contract。

### 46.7 成本与 Invariants

1. formatter 是 deterministic local logic，不调用 Writer、LLM、VLM 或外部 API；
2. Aha exact point 固定 `HH:mm`；Chapter exact range 固定 `HH:mm–HH:mm`；
3. 小时两位、24 小时制、不显示秒、不同时重复 broad period；
4. seconds floor 到 containing minute，不四舍五入；
5. range 两端同规则；同一分钟输入属于上游／format contract invalid，不生成重复 range，也不由 formatter 重选 broad label；
6. 双时段使用“到”，只实现 D3c 已批准的相邻双时段语义；
7. omission 不产生任何 placeholder string；
8. formatter 不添加“约／左右／大概”来绕过 Evidence gate；
9. semantic decision 与 display string 分层保存；
10. 中文格式不直接成为海外 Production 合同；
11. 本节确认中文 formatter；跨 Revision continuity 已由 D3f 单独确认，App rendering、整个 D3 或 S11 不在本节冻结。

## 47. S11-D3f｜Cross-Revision Time Label Stability

**状态：CONFIRMED**

### 47.1 确认的体验原则

> 时间事实纠错优先；但当前后两种标签都仍然真实时，优先保持用户已经看到的标签。不能因为新增一两个边缘 Window 或比例在阈值附近波动，就让同一个 Memory 在 `下午 → 下午到晚上 → 下午`之间来回跳。

Time Label 是 deterministic metadata surface，不新增一套与 C3a 竞争的文字连续性体系。确认与 C3a 映射为：

| Time Label transition | C3a 关系 | 执行方式 |
|---|---|---|
| `TIME_LABEL_RETAIN` | `TEXT_RETAIN` | 复用 prior semantic key 与 display；必要时重验 |
| `TIME_LABEL_REPLACE` | atomic `TEXT_PATCH` | D3 重新确定性格式化，不调用 Writer |
| `TIME_LABEL_ADD` | no-prior initial build | 从 omission 变为合法 label |
| `TIME_LABEL_OMIT` | optional omission by contract | prior label 已失效且无安全 fallback |
| `TIME_LABEL_CONTRACT_INVALID` | surface contract invalid | 返回 owner，不伪装成 omission |

这只是把既有 C3a 聚合合同落到 Time Label；不改变 C3a 的四状态定义，也不把 Time Label 交给 D5 Tags。

### 47.2 确认的稳定带（hysteresis）

D3c1 的首次生成规则仍为 70%/30%。对于已经发布的单／双时段标签，确认增加一个小的进入／退出差值：

~~~text
first_build_dual_minor_share_min = 0.30
published_single_to_dual_minor_share_min = 0.35
published_dual_retain_minor_share_min = 0.25
dual_min_cells_each_side = 2
same_episode_relation must remain valid
~~~

含义：

1. 首次构建仍按当前 30% minor-share Baseline；
2. 已发布单时段升级为双时段，需要少数侧达到 35%，避免一过 30% 就立刻改变；
3. 已发布双时段只要少数侧仍至少 25%、两侧仍各有至少 2 cells、relation 仍合法，就保持双时段；
4. 少数侧低于 25%、不足 2 cells、relation 失效或出现 boundary contradiction，才退回合法单时段／omission；
5. 25%–35% 是稳定带：prior label 若仍真实就保留，不由当前比例强制翻转；
6. 事实纠错、timezone 修复、Anchor 变化或 exact boundary pair 到来不受稳定带阻止；truth correction 永远优先。

这组 ±5 percentage-point 参数和 D3c1 一样必须 versioned，并在真实 Preview timeline 中评测 label-flip rate、错误保留率与更新延迟。

### 47.3 确认的材料变化门

允许 Time Label 改变的情况：

1. omission 后新 Evidence 已通过当前 eligibility gate；
2. single ↔ dual 跨过上述稳定带，且 relation/material support 仍合法；
3. 白名单 actual boundary pair 到来，broad/dual 升级为 exact range；
4. prior exact boundary、Aha Anchor、timezone 或 day scope 被证明错误／失效；
5. S09 current Revision 合法改变 selected scope、Chapter form 或 stable lineage；
6. prior label 本身违反当前 truth/contract，必须纠错。

不允许改变的情况：

1. 只是新增相似素材，semantic outcome 与 support band 未材料变化；
2. Sync/import/Finalization 本身发生，但 current facts 没变；
3. 模型、Prompt、Writer 风格或媒体格式变化；
4. S10 Media Fallback 保持同一 EvidenceAnchor；
5. formatter 文案版本变化但 semantic key 未变；此时只能记录 `PRESENTATION_RERENDER`，不能制造新的 Memory semantic Revision；
6. 为了让 Preview 看起来“更新了”。

### 47.4 Aha 与 exact range 的 truth-first 例外

1. Aha resolved Anchor 与 source timestamp 未变：exact point 必须 retain；
2. Media format PHOTO/LIVE/VIDEO 改变、Anchor 不变：Time Label 不变；
3. Anchor Fallback 改变了 Anchor ref／真实 timestamp，但仍映射到相同 displayed minute：必须绑定 current assertion，并记录 `AHA_ANCHOR_CHANGE`；用户可见 semantic key 不变，因此可 `TIME_LABEL_RETAIN + PRESENTATION_RETAIN`，这不是沿用 stale ref；
4. Anchor Fallback 改变实际 displayed minute：重验后 replace，不能用稳定性保留旧分钟；
5. exact point 失效但 broad fallback 合法：replace 为 broad；两者都不合法：omit；
6. Chapter actual boundary pair 新增并通过 D3d：可以从 broad/dual 升级 exact range；
7. exact boundary refs／timestamps 变化但 formatted range key 不变：重绑 current assertion、记录 `EXACT_BOUNDARY_CHANGE`，visible label 可 retain；range key 改变则 replace；
8. exact range 的任一 boundary 失效：立即回到当前合法 broad/dual/omitted，不受 hysteresis 保护。

### 47.5 案例预演

#### 防止单／双时段来回跳

~~~text
Revision 1  下午 6 cells / 晚上 1 cell
            → 下午

Revision 2  下午 6 / 晚上 4 = 60% / 40%
            → 晚上 minor share 40% ≥ 35%
            → 下午到晚上

Revision 3  晚到的下午素材使比例变成 72% / 28%
            → 28% 位于 25%–35% 稳定带
            → 保持 下午到晚上

Revision 4  晚上合法 cells 被纠错到只剩 1 个
            → minimum support 失效
            → 回到 下午
~~~

Revision 3 不按静态 70/30 立即改回“下午”，因为“下午到晚上”仍有两侧充分支持且没有失真；Revision 4 则是事实支持真正失效，稳定性不能保护它。

#### omission 后补足

Preview 只有 17:56 与 18:03 两个稀疏点，Time Label omitted；后续 Revision 形成 4 个可靠晚上 cells 并得到明确 single-period result，执行 `TIME_LABEL_ADD`，无感出现`晚上`。

#### Aha Anchor Fallback

prior Aha 为 20:17；Fallback Anchor 重验后实际位于 20:18。旧 point 已与 active Anchor 脱钩，必须 replace 为 20:18，不能以“用户已经看过”为由保留 20:17。

#### 只把“至”改成“到”

semantic key 仍为 `AFTERNOON_TO_EVENING`，只是 formatter policy 改变。记录 presentation rerender，不声称 Memory、Evidence 或时间判断发生变化。

### 47.6 S09 Preview/Final 边界

1. 只有 prior user-visible published Revision 才作为稳定性 baseline；内部草稿不算；
2. S09 `NO_CHANGE_REUSE`：只有在 S09 明确不创建新的 downstream semantic Revision、且完整 dependency/policy fingerprint 仍相同时，才可复用现有 Time Label decision 与 formatter artifact；一旦创建 current S11 Revision，就必须生成／解析 current candidate assertion，不能把 prior ref 改名成 current；
3. S09 `HOLD_PREVIOUS_REVISION`：不发布当前未完成的 Time Label 变化；
4. stable identity `CONTINUES/EXPANDS` 才进入同一 Memory 的 Time Label continuity；
5. merge/split/type transition 按 S09 lineage 为新 current instance 重算，不能让一个旧 label 同时继承给多个 child；
6. 除上述 exact artifact reuse 分支外，continuity 决策产生新的 immutable artifact，不原地覆盖 prior。

### 47.7 确定性执行顺序

~~~text
current C2 Time Label surface plan
+ prior published Time Label outcome, if any
→ validate refs / lineage / policy compatibility
→ derive current base semantic decision
→ restrict to current B0/B2-approved candidate assertions
→ apply truth-first overrides
→ apply broad-period hysteresis when eligible
→ select current assertion or explicit omission permission
→ emit deterministic result + intended C3a mapping
→ B3 composite validation, when applicable
→ D3e formatter
→ E actual-label verification
→ materialize C3a aggregate record
→ TimeLabelSurfaceOutcome
~~~

执行规则固定为：

1. ref、Revision、lineage、timezone/day scope 或 policy compatibility 损坏时，直接 `TIME_LABEL_CONTRACT_INVALID`；不能进入稳定带，也不能伪装成 omission；
2. 没有 prior published Time Label outcome 时，按 C2 base decision 首次构建：双时段 minor-share 门仍为 30%；
3. prior outcome 为 omission、current base 已合法出现 label 时，使用 `TIME_LABEL_ADD`；current 仍需 omission 时继续输出显式 omission；
4. prior/current exact point、exact range、Anchor 或 actual boundary 发生材料性变化时，先执行 truth-first replace/omit，不运行 broad-period hysteresis；
5. prior 为 single 时，只有 prior semantic key 仍对应 current majority period，且 current candidate set 中存在同 key 的合法 assertion，才可在 minor share <35% 时 retain；达到 35% 且 dual base/candidate 合法时 replace 为 dual；
6. prior 为 dual 时，只有 current candidate set 中仍有相同 dual key、minor share ≥25%、两侧各至少 2 cells、same-Episode relation 仍成立且无 contradiction，才可 retain；minor share <25% 或任一资格失效时 replace 为 current legal single，若无 safe fallback 则 omit；
7. `TIME_LABEL_RETAIN` 复用的是 prior semantic key／合格 display，不是 prior Revision 的 assertion ref。当前 decision 必须选择语义等价的 **current** assertion ref；
8. D3f 只能选择 `BASE_ELIGIBLE` 或与 prior key 精确匹配的 `CONTINUITY_RETAIN_ONLY` candidate，且该候选必须已有合法 C2 cross-surface/ownership audit；不能自行读取原始时间点生成新 assertion，也不能借用 base candidate 的 audit；
9. deterministic owner decision 先输出 intended C3a mapping；适用的 B3、D3e 与 E 完成后，后置 C3a aggregate 才将其记录为 READY／合法 omission。它不写入 `generated_surface_decisions[]`，也不调用 Writer。

### 47.8 最小跨 Revision 决策合同

~~~text
TimeLabelRevisionDecision
  selected_memory_ref
  stable_memory_id
  revision_ref
  prior_revision_ref?
  prior_published_time_label_outcome_ref?
  prior_visibility_state?
    PREVIEW_PUBLISHED
    | FINAL_PUBLISHED
  current_cross_surface_plan_ref
  base_time_label_decision_ref
  current_candidate_time_label_assertions[]
    assertion_ref
    semantic_label_kind
    semantic_label_key
    candidate_eligibility
      BASE_ELIGIBLE
      | CONTINUITY_RETAIN_ONLY
    cross_surface_overlap_audit_ref
    surface_ownership_audit_ref
  prior_outcome_state?
    TIME_LABEL_PRESENT
    | TIME_LABEL_OMITTED_EVIDENCE_UNRESOLVED
  prior_semantic_label_key?
  current_base_semantic_label_key?
  continuity_applicability
    APPLICABLE_PRIOR_PUBLISHED_TIME_LABEL
    | NOT_APPLICABLE_NO_PRIOR_PUBLISHED_TIME_LABEL
  prior_label_current_truth_check?
  prior_label_current_candidate_ref?
  decision_state
    TIME_LABEL_RETAIN
    | TIME_LABEL_REPLACE
    | TIME_LABEL_ADD
    | TIME_LABEL_OMIT
    | TIME_LABEL_CONTRACT_INVALID
  selected_time_label_assertion_ref?
  omission_permission_ref?
  truth_override
    NONE
    | FACT_CORRECTION
    | TIMEZONE_OR_DAY_SCOPE_CHANGE
    | AHA_ANCHOR_CHANGE
    | EXACT_BOUNDARY_CHANGE
    | SELECTED_SCOPE_OR_LINEAGE_CHANGE
  hysteresis_snapshot?
    prior_label_kind
    majority_period?
    minor_period?
    minor_share?
    occupied_cells_each_side[]
    relation_decision_ref?
    applied_enter_threshold?
    applied_exit_threshold?
  presentation_action
    PRESENTATION_RETAIN
    | PRESENTATION_RERENDER
    | PRESENTATION_ADD
    | PRESENTATION_REMOVE
    | NO_PRESENTATION_OUTPUT
  c3a_mapping
    TEXT_RETAIN
    | TEXT_PATCH
    | INITIAL_BUILD
    | OPTIONAL_OMISSION_BY_CONTRACT
    | SURFACE_CONTRACT_INVALID
  reason_codes[]
  time_label_continuity_policy_version
  source_policy_versions
  decision_fingerprint
  construction_audit
~~~

字段约束：

1. `RETAIN/REPLACE/ADD` 必须填写 current `selected_time_label_assertion_ref`；`OMIT` 必须填写 explicit `omission_permission_ref`；`CONTRACT_INVALID` 两者都不得伪造；
2. `RETAIN` 的 current candidate semantic key 必须与 prior key 相同；`REPLACE` 必须记录 old/new key 与材料变化原因；
3. `hysteresis_snapshot` 只用于 Chapter single/dual broad-period transition；Aha exact point、Chapter exact range、omission truth correction 与 contract invalid 不使用；
4. `c3a_mapping` 是进入既有 aggregate 的语义映射，不表示 Time Label 变成 Writer 文案，也不创建第二套 C3a `TEXT_*` artifact；
5. `PRESENTATION_RERENDER` 只允许 semantic key 不变而 locale/formatter contract 合法变化；它不能冒充 Memory 时间语义变化；
6. fingerprint 必须覆盖 prior visible outcome、current candidate set、base decision、hysteresis inputs、truth override、selected current assertion／omission ref 与全部 policy versions。

### 47.9 边界案例补充

#### 首次构建正好 30%

下午 7 cells、晚上 3 cells，刚好 70%/30%。按 D3c1 的 base tie rule，首次构建仍优先`下午`；如果 prior 已合法显示`下午到晚上`，且两侧各至少 2 cells、same-Episode relation 仍成立，则可在 D3f 按 25% retention floor 保留双时段。相同 current facts 因 prior user-visible state 不同而得到不同 continuity result是预期行为，但 prior、规则和 fingerprint 都必须可回放。

#### prior single 不是 current majority

prior 显示`下午`，新 Revision 的 current support 已变为下午 3／晚上 6。即使 minor share 33% 位于稳定区，`下午`已不是 current majority，不能用 hysteresis 保留；应依据 current 合法 candidate replace 为`下午到晚上`或`晚上`，否则 omit。

#### 内部草稿发生变化

内部未发布 draft 从`下午`变成`下午到晚上`，不运行 hysteresis；它没有成为用户的认知锚点。只有 Preview/Final 已展示 outcome 才构成 continuity baseline。

#### Formatter 版本变化

semantic key、current assertion 与 Evidence 全部不变，只把旧中文连接词重新渲染为已确认的“到”。记录 `PRESENTATION_RERENDER`，不声称 Time Label semantic decision 或 Memory Revision 因内容而改变。

### 47.10 成本与 Invariants

1. D3f 只比较 current candidate set、prior published outcome 与少量 normalized cell statistics，时间复杂度与 candidate 数量线性相关；
2. 不新增上传、抽帧、VLM、LLM、embedding、HQ 读取或用户交互；
3. 首次双时段门为 30%，published single→dual 为 35%，published dual retention floor 为 25%；三项必须共同 versioned；
4. 25%–35% 只是一段 truthful stability band，不是允许保留错误标签的容错区；
5. 事实纠错、timezone/day scope、Anchor、exact boundary 与 current lineage 变化优先于 hysteresis；
6. 双时段 retain 始终要求两侧各至少 2 cells、相邻时段、same-Episode relation 与无 contradiction；
7. prior single 只有仍对应 current majority period 才能 retain；
8. prior published label 必须绑定 current equivalent assertion；不得沿用 stale prior assertion ref；
9. omission 是显式 optional surface outcome，contract invalid 是工程／数据合同异常，二者不可互换；
10. formatter 在 D3f 与适用的 B3 validation 之后运行；
11. deterministic Time Label 进入 C3a 整体聚合，但不进入 Writer-generated surface array；
12. 相同 current inputs、prior published outcome 与 policy versions 必须产生相同 decision/fingerprint；
13. 本节确认 Time Label 跨 Revision 稳定原则，不冻结整个 D3 或 S11。

## 48. S11-D3 Current-Chinese-Testing Closeout Cross-Check

**状态：PASSED WITH CONTRACT-ALIGNMENT AMENDMENTS / CURRENT CHINESE D3 DESIGN FROZEN / EXPLICIT DEFERRALS REMAIN / S11 NOT FROZEN**

### 48.1 检查范围与结论

本轮把 D3a–D3f 与上游冻结／已确认合同逐项交叉核对：

~~~text
A3 temporal Fact projection
↔ B0 implicit assertion production
↔ B2 truth / support / surface permission
↔ C2 cross-surface semantic ownership
↔ C3a cross-Revision continuity
↔ B3 composition validation
↔ D3e deterministic formatting
↔ future E actual-label verification

and
  S05 sparse Observation + Boundary / Continuity Evidence
  S07 Candidate form / RESUMED_EPISODE / interruption refs
  S09 selected membership / lineage / Preview-Final states
  S10 EvidenceAnchor / Media vs Anchor Fallback
  D1 Story / D2 Title / future D5 Tags ownership
  upload / compute / App boundary
~~~

结论：D3 的九项已确认体验原则可以同时成立，没有需要推翻的产品决定。交叉检查发现的是接口位置、生命周期命名和旧前向引用问题，已在本轮完成 contract-alignment amendments。用户于 2026-08-28 明确确认后，当前中文测试版 D3 Time Label 设计正式冻结为 S11 的阶段性合同；本次冻结不包含 48.6 的开放项，不把整个 S11 标为 FROZEN，也不等于全球 Production、App 实现或 E/S12 validator 已完成。

### 48.2 本轮完成的结构修正

1. **C2 从 mandatory 单 ref 改为 nullable candidate plan：** Time Label 允许 single／dual／exact 多个 current 候选，也允许显式 omission；C2 保存 base decision 与候选集，不假定一个永远存在的 final ref；
2. **语义规则回到 assertion 链上游：** D3a–D3d 与 D3f prior-independent candidate envelope 是 B0/B2/C2 消费的 versioned deterministic policies；B0 之前只输出 semantic specs，不提前引用尚未生成的 assertion；读取 prior outcome 的 D3f selection 仍在 C2 后，且不能在 B3 后创造新时间语义；
3. **base 与 final 分离：** D3c／D3c1 的 70%/30% 只产生 current base decision；D3f 再结合 prior published outcome，在 truthful candidate envelope 内产生 continuity-adjusted selection；
4. **continuity-only candidate 显式化：** B0 不读取 prior artifact，只按 current facts 把 25%–35% 稳定区内仍真实的 single／dual 语义 materialize 为 current `CONTINUITY_RETAIN_ONLY` assertion；D3f 只在 prior key 匹配时选择，避免“为了稳定而沿用 stale prior assertion”；
5. **C3a 聚合接入 deterministic surface：** Time Label 使用 D3f owner decision 映射进同一整体 continuity aggregate，但不进入 generated wording array、不调用 Writer；旧“交给 D5”路由已修正，D5 继续只负责 Tags；
6. **Formatter 调整到最终语义之后：** Production 顺序固定为 C2 base → C3a/D3f → applicable B3 → D3e → E；讨论编号不再被误读为运行顺序；同一分钟 exact range 由 D3d 上游拒绝，formatter 不再越权重选 broad/omitted；
7. **final outcome 的生命周期闭合：** omission/present/contract-invalid 的 `TimeLabelSurfaceOutcome` 只在 D3f 完成、PRESENT 分支已格式化后封装，并引用 current assertion 或 explicit omission permission；
8. **S09 reuse 边界补齐：** exact `NO_CHANGE_REUSE` 且不创建 downstream semantic Revision 时可复用完整 artifact；一旦创建 current S11 Revision，就必须使用 current assertion，不能把 prior ref 改名；
9. **旧案例和前向引用清理：** 删除`上午 09:00–12:00`这类混合 broad＋exact 的错误案例，补上 exact boundary 前提，并把已完成的 D3c2／D3d／D3e／D3f 从“后续待定”改为准确引用。

### 48.3 上下游交叉结果

| 检查项 | 结果 | 约束结论 |
|---|---|---|
| S05 稀疏观测 ↔ D3c1 | PASS | occupied cell 只证明该格有观测；不填补空白、不把稀疏采样写成持续时长 |
| Boundary / Continuity Evidence ↔ D3c/D3d | PASS | Continuity 支持 same-Episode，不能替代 actual start/end；exact range 仍须白名单 boundary pair |
| S07 Candidate form ↔ D3c | PASS | `RESUMED_EPISODE` 不使用暗示连续的当前双时段／单 range；D3 不改写 seam、interruption 或 Candidate form |
| S09 selected membership ↔ D3c1 | PASS | Chapter distribution 只消费 current selected KEEP content refs；不使用全天未选素材或 S10 最终 3–5 媒体投票 |
| S09 lineage ↔ D3f | PASS | 只有 published baseline＋`CONTINUES/EXPANDS`进入同一 stable ID continuity；merge/split/type transition 按 lineage 重算 |
| S09 `HOLD_PREVIOUS_REVISION` ↔ D3f | PASS | 当前未完成变化不单独发布；保持 last published Revision，不拼出半完成 label |
| S10 EvidenceAnchor ↔ Aha exact point | PASS | exact point 来自 resolved Anchor 的实际 source/decode timestamp；视频 start 或 target offset 不冒充 peak |
| S10 Media/Anchor Fallback ↔ D3f | PASS | 同 Anchor 换格式不改时间；Anchor 改变必须 truth-first 重验，稳定带不保护旧分钟 |
| B0/B2/C2/B3 ↔ D3 | PASS AFTER AMENDMENT | single／dual／exact 都先成为可追溯 implicit assertion；composite semantics 在适用时过 B3 |
| C3a ↔ D3f | PASS AFTER AMENDMENT | Time Label 专用 transition 映射进既有聚合；没有第二套整体 continuity state machine |
| D1/D2/D5 ownership ↔ D3 | PASS | Time Label 不写活动、地点、情绪；Story/Title 不因 label 独立更新而被迫改写；Tags 仍归 D5 |
| 成本／上传 ↔ 全 D3 | PASS | 全部为已有 metadata、refs、cells 与规则计算；不补帧、不取 HQ、不新增模型或用户上传交互 |

### 48.4 结果空间完整性检查

| Memory type | 可见／非可见结果 | 当前合同 |
|---|---|---|
| Chapter | exact range | 仅 D3d actual boundary whitelist PASS，且 displayed start minute < end minute；D3f truth-first；D3e `HH:mm–HH:mm` |
| Chapter | single broad period | 六段词表＋D3c1 base／D3f stability |
| Chapter | adjacent dual broad period | 两侧 material support＋same-Episode＋30/35/25 versioned gates；D3e 使用“到” |
| Chapter | omitted | ordinary unresolved；保留 Memory，不显示 placeholder |
| Chapter | contract invalid | 返回 failure owner；若 day identity 损坏，不在可能错误日期正常发布 |
| Aha | exact point | resolved peak Anchor actual timestamp；D3e `HH:mm` |
| Aha | single broad period | exact 不合法但完整 source/peak interval 落在一段 |
| Aha | omitted | peak 未定位且 interval 跨段等普通 unresolved；不显示双时段 |
| Aha | contract invalid | Anchor/timezone/day/ref 合同损坏；不伪装成 omission |

没有发现状态缺口：Chapter 与 Aha 的 present、ordinary omission 和 contract invalid 均可被区分；首次生成、retain、replace、add、omit 与 exact no-change reuse 也都有明确路径。

### 48.5 当前九项确认原则

1. Chapter 默认表达诚实的 broad period，observed first/last 不等于活动起止；
2. Aha 在 resolved EvidenceAnchor 实际时间可靠时使用 exact point，否则安全降级；
3. 中文 V1 使用六个互斥半开时段：凌晨、清晨、上午、中午、下午、晚上；
4. Chapter 单时段优先，只有相邻双时段具备两侧 material support 与 same-Episode relation 时才允许；Aha 不使用双时段；
5. Chapter temporal support 使用 user-local-day 对齐的 5 分钟 occupied cells，单 cell 权重上限为 1；
6. Time Label 是 optional nullable surface；ordinary unresolved 无感省略，contract invalid 单独处理；
7. Chapter exact range 只接受完整 actual boundary pair 白名单，不用首尾素材、计划时间或 Manual capture interval冒充；
8. 中文 formatter 使用 24 小时制、零补位、秒数 floor、en dash range 与“到”连接；semantic key 与 display string 分离；
9. 跨 Revision 使用 30% 首次 dual、35% published single→dual、25% published dual retention，并始终让事实纠错、Anchor／boundary／day-scope 变化优先。

### 48.6 明确保留的开放项

当前不伪装成全球 Production 或 App 实现完成：

1. `傍晚`是否进入中文词表；
2. 英文及其他海外市场的 12/24 小时制、day-period wording、range separator、layout 与 accessibility 合同；
3. 跨午夜／多日 Episode 的归属与显示；
4. `RESUMED_EPISODE` 或其他非连续经历是否使用并列多时段 UI；
5. nullable Time Label 在正式 App 中如何收起布局、如何做 VoiceOver；
6. 5 分钟 cell、70/30 与 30/35/25 阈值在真实用户数据上的 calibration；
7. Production provider/schema/runner、E/S12 validator 与 telemetry 实现；
8. 隐私、伦理与治理专项按既定全局顺序在核心 pipeline 打通后处理。

16 秒、73 秒等任意时长 Manual Video 的 Window 数量与精确位置继续保持既有 OPEN；D3 只消费上游已经合法形成的 Window／content-unit temporal refs，不在本节重新打开或偷定该问题。

### 48.7 Closeout Invariants

1. 九项当前中文体验原则没有被接口修正改变；
2. D3 不修改 S05/S07/S09/S10 的 membership、boundary、relation、Anchor 或媒体；
3. base decision、continuity decision、formatted artifact 与 final surface outcome 分层且 immutable；
4. stability 只能在 current Evidence 仍支持的候选之间选择；
5. optional omission 不阻断合法 Memory，contract invalid 不被吞掉；
6. 任何 user-visible label 都能追溯到 current／exact-reuse-compatible assertion、policy、Revision 与 Evidence；
7. D3 不增加云端视觉理解、上传、HQ 或用户交互成本；
8. 本 closeout 正式冻结当前中文测试版 D3 设计；只要没有真实数据反证或新的显式 versioned checkpoint，后续阶段必须继承九项原则与本轮 contract-alignment amendments；整个 S11 仍未冻结。

## 49. D3 冻结记录与下一检查点

**冻结日期：** 2026-08-28

**冻结范围：** 当前中文测试版 D3 Time Label 的九项原则、D3a–D3f 合同、48.2 contract-alignment amendments、结果空间与 Closeout Invariants。

**不在冻结范围：** 48.6 明列开放项、正式 App presentation、海外 locale、Production provider/schema/runner、E/S12 implementation、隐私／伦理专项，以及任意时长 Manual Video Window 规划。

**变更规则：** 后续真实数据若提供反证，或团队明确批准新的 versioned checkpoint，才可修订；不得由实现、模型版本或临时 UI 需要静默改写。

D3 至此结束。逻辑上的下一阶段是 D4 Aha Moment Line wording／length，但本次冻结动作没有启动 D4，也没有授权 Git 提交或同步。

## 50. S11-D4｜Aha Moment Line Wording & Length

**状态：CURRENT CHINESE D4 DESIGN FROZEN / D4a–D4e CLOSEOUT CROSS-CHECK PASSED WITH 3 LOCALIZATION ALIGNMENTS / ENGLISH AND OTHER LOCALE CONTRACTS DEFERRED / D6 + E + S12 IMPLEMENTATION OPEN / S11 NOT FROZEN**

### 50.1 所在链路与本阶段目标

D4 位于 Aha 的事实、单一 peak、必要上下文／即时支持、可观察限定与组合合法性都已经确定之后：

~~~text
B3_VALIDATED AhaNarrativeSurfacePlan
+ C3b3 observable-emphasis decision
+ C3b3 Light-Affect v1.1 permission decision
+ C3a current surface continuity decision
+ D4 locale-specific realization policy
→ D4 bounded Moment Line realization
→ one AhaMomentLineDraft
→ E actual span / claim / relation / qualifier / light-affect verification
→ S12 final publication validation
~~~

上图是当前中文已验证 plan 的直接路径。对未来其他 locale，D4e 会在 canonical base plan 与 D4 realization 之间先形成`LocaleAhaNarrativeSurfacePlan`，再经过 target-locale B3；不能把中文 B3 结果当作目标语言 surface 已自动通过。

D4 的任务不是重新挑选“写什么”，而是把已经验证的 exact plan 写成一条自然、直接、易扫读的用户文字。First build、`TEXT_PATCH/TEXT_REBUILD` 才进入相应 D4 realization；合法 `TEXT_RETAIN` 复用 prior exact wording 并只做依赖／E revalidation，不为了文风重新调用 Writer。

### 50.2 继承且不再重开的合同

1. V1 generated Aha 只有一个 `AHA_MOMENT_LINE` narrative field；没有 generated Title、第二个 Story field或独立 Atmosphere/Tone；
2. 正常目标是一条完整自然句；“一个 logical field”不等于 App 物理单行显示；
3. 恰好围绕一个 `core_peak_event_ref`，必须明确写出 peak 动作／事件／可见变化；
4. 只能实现 B3-validated plan 中的 exactly 1 peak group、0–1 necessary minimal local context、0–1 immediate support、0–1 observable qualifier，以及 28.12 已许可但可不实现的 0–1 light-affective lexical span；
5. D4 不新增、删除、替换、重标或交换 Claim role，也不自行创造 light-affect class／target／词表；若已选事实内容无法安全实现，必须返回明确 owner，不在 Writer 内偷改 plan；
6. 不生成 Chapter-wide 背景、第二 peak、准备—过程—结局、小 Chapter summary 或媒体说明；
7. 不使用无 Evidence 的用户心理、关系、味觉／体感、意图或编辑价值判断制造“高光感”；28.12 permission 只允许受控的低风险宠物动作语气，不改变该禁令；
8. D4 不改 S07–S10 membership、Aha/Chapter independence、EvidenceAnchor、媒体或刚冻结的 D3；
9. 模型、Prompt、voice、temperature、候选与 retry budget 属于 D6；实际 wording 的真实性属于 E；App 字体、物理行数与截断属于正式 presentation contract。

### 50.3 D4 讨论拆分

~~~text
D4a  Chinese V1 length envelope + counting
D4b  sentence realization / directness / punctuation
D4c  bounded compression + owner-routed failure
D4d  cross-Revision retain / minimal patch / rebuild
D4e  localization boundary + closeout cross-check
~~~

每一项单独讨论和确认。除用户在 2026-08-28 明确批准并已记录为 28.12 Light-Affect v1.1 的窄 amendment 外，D4 不因进入新阶段重新打开 C3b1–C3b3 或 D3。

## 51. S11-D4a｜Chinese V1 Moment Line Length Envelope

**状态：FROZEN FOR CURRENT CHINESE TESTING / PRINCIPLES 1–6 LOCKED / USER CONFIRMED / D4 NOT FROZEN**

### 51.1 推荐的中文测试 Baseline

~~~text
generated Chinese Aha Moment Line
  normal target                 = 4..20 visible grapheme clusters
  justified soft extension     = 21..24 visible grapheme clusters
  complete-event semantic gate = REQUIRED
  one logical sentence         = REQUIRED
  semantic truncation          = FORBIDDEN
  ellipsis as generation       = FORBIDDEN
~~~

这里的 `4` 不是填字配额。只要一句更短的表达已经自然、独立地说清 peak，就不能添加“这一刻、画面里、记录下”等空泛词凑长度；低于 normal target 但语义完整的极短句可作为诊断案例保留，由 D4b 的 complete-sentence／standalone gate 决定，而不是由 Writer补字。

`20` 也不是 substring truncation 的刀口。Aha 文字越长，通常意味着暴露给用户的 Claim、关系或修饰越多，事实出错与“系统替我编故事”的感受都会增加；因此 V1 把 20 个可见字符作为正常目标。只有已经验证且无法安全压缩的必要关系，才讨论一个很窄的 21–24 字软扩展；软扩展不是增加文采的空间。

### 51.2 为什么收紧为 20＋24

1. peak-only 常见为约 7–16 个可见字符，大部分 Aha 不需要接近 20；
2. Aha 应让用户一眼看到“发生了什么”，而不是阅读一个小型 Chapter；20 字能强化两种产品形态的区别；
3. 每增加一个从句、关系词或氛围修饰，都可能扩大事实错误与虚假编纂的表面积；
4. peak 加一组即时 support 通常仍可在不改变 exact plan 的前提下压缩至 20 字以内；
5. C3b2 已证明必要的 local context 或 immediate support 不能仅为了卡字数被 Writer 静默删除，因此保留 21–24 的窄软扩展候选；
6. 超过 24 后，优先怀疑措辞冗余、plan 信息密度或 presentation 不匹配，并显式返回 replan，而不是截断事实；
7. 当前仍是中文测试 Baseline，后续必须用真实 Aha 时间线、卡片阅读测试与错误率校准，不伪装成永久自然常数。

### 51.3 21–24 字软扩展门

只有同时满足以下条件才允许超过 20：

1. 当前 plan 已通过 B3，超出部分表达的是其中不可静默丢弃的 peak core、必要 context、必要 support 或合法 relation；D4c1 后置确认 selected observable qualifier 仍属可选内容，只有完整句不超过 20 时才保留，不能单独成为软扩展理由；
2. 已删除所有不承载 Claim 的套话、重复主体、meta narration 与纯文风词；
3. 不存在保持 exact Claim/relation set 的更短自然表达；
4. 仍是一条自然句，没有用分号、破折号或多个独立分句伪装第二个 Story；
5. 字符数不超过 24；
6. `length_policy_version` 与 soft-extension reason 可审计。

“更好听、更有画面、更像高光”不是软扩展理由。软扩展也不授权 D4 新增 qualifier、第二事件或 Chapter 背景。

### 51.4 超出 24 时的原则

~~~text
Moment Line > 24
→ remove non-semantic filler / meta phrasing
→ use a shorter wording that preserves the exact validated plan
→ one bounded D4 wording rewrite
→ if still >24: D4_LENGTH_REPLAN_REQUIRED
→ route by failing content owner in D4c
→ never substring-truncate or append ellipsis
~~~

D4a 现在只确认“不能截断、必须显式 replan”的原则；具体先回 C3b3 删除 optional qualifier，还是回 C3b2 重审 support/context，必须在 D4c 结合 necessity 与 owner contract 再确认，不能在本节偷定。

### 51.5 中文计量口径

当前测试按 Unicode normalization 后的用户可见 grapheme clusters 计量：

1. 去除首尾空白；
2. 汉字、数字、拉丁字符、emoji 与标点都按用户可见 cluster 计入，不能按 UTF-8 bytes、模型 token 或代码单元计数；
3. 句末标点属于实际显示内容，计入预算；
4. 不通过增加空格、拆行或更换全／半角标点绕过预算；
5. physical width、Dynamic Type、单／双行与截断方式仍由未来 App presentation contract 处理；
6. 英文及其他 locale 必须另建 word/content-word、grapheme、display width、proper noun、wrapping 与 accessibility 合同，不能照搬中文 20／24。

### 51.6 案例检查

#### Peak-only｜正常短句

> 泥坯塌了下去。

约 7 个可见字符，已经完整表达 peak；不能为了靠近 20 字补成“镜头记录下泥坯塌下去的特别一刻”。

#### Peak＋minimal local context｜正常范围

> 拉坯时，泥坯塌了下去。

约 11 个可见字符。`拉坯时`只有在 C3b2 已选为必要 activity-phase context 时出现；D4 不能仅因句子更完整自行补入。若 own media 与 peak clause 已足够独立理解，应直接写`泥坯塌了下去。`

#### Peak＋immediate support｜正常范围

> 甜品切开，流心淌出，桌边的人随即笑了。

约 19 个可见字符。只有 peak、reaction 与`随即`关系全部在 B3-validated plan 中时才合法；这个案例说明，同一组已验证内容通常可以在 20 字以内自然表达，而不必写成小故事。

#### Context＋qualifier＋support｜D4c1 后置路由案例

> 拉坯时，泥坯缓缓塌下，旁边的人随即伸手扶住。

约 22 个可见字符。D4a 初次讨论时把它记录为 soft-extension candidate；D4c1 随后明确：`缓缓`虽为 grounded qualifier，仍是可选 emphasis，不能用它占用只为必要事实开放的 21–24。一次 same-plan rewrite 仍无法在 20 字内保留全部 exact 内容时，应先回 C3b3 生成 qualifier-free plan，而不是直接软扩展；必要 context／support／relation 才继续接受软扩展检查。

#### 错误的截断

不允许：

> 甜品切开时，流心从中间淌出，桌边的人随即……

省略号把已选 support 截成半个事实，也让用户不知道发生了什么。正确处理是完整短写，或返回 D4c owner-routed replan，不发布残句。

#### 长度合格但语义失败

> 这一刻真的很特别。

即使远低于 20 字，也没有表达 peak，并含编辑价值判断；长度通过不能覆盖 C3b1–C3b3 与 E 的事实门。

### 51.7 成本与边界

1. 计数与长度 gate 是 deterministic local logic，不增加 VLM、上传、HQ 或外部 API；
2. 正常只生成一条 Moment Line；超过预算最多触发一个 bounded same-plan wording rewrite，具体 retry 总预算留到 D4c/D6 对齐；
3. 字数不是质量分，不参与 Aha selection、排序或全天 2–3 个数量目标；
4. 长度失败不授权 D4 删除 Aha、换素材、改 peak 或让 Chapter 吞回该事件；
5. D4a 不冻结句法顺序、标点风格、owner-routed replan 细节、模型配置、海外 locale 或整个 D4。

### 51.8 D4a Closeout Invariants

1. 当前中文测试版正常目标为 4–20 个可见 grapheme clusters；短而完整不补字；
2. 21–24 只作为必要已验证内容无法安全压缩时的窄软扩展，不作为增加氛围、文采或第二事件的空间；
3. 长度预算不能覆盖 complete-event、single-peak、Claim、relation、qualifier 与 Evidence gate；
4. 超过 24 不做 substring truncation、不生成省略号；先做一次保持 exact plan 的 bounded wording rewrite，仍超限则显式进入 `D4_LENGTH_REPLAN_REQUIRED`；
5. 中文按 normalization 后的用户可见 grapheme clusters 计量，句末标点计入；英文及其他 locale 不照搬 20／24；
6. D4a 不改变上游 Aha membership、peak、plan、媒体、全天数量，也不增加上传、HQ、VLM、外部 API 或用户交互。

## 52. D4a 冻结记录

**冻结日期：** 2026-08-28

**用户确认：** 中文 Aha Moment Line 正常控制在 20 字以内，以减少新增事实与“虚假编纂感”；必要且已验证的内容无法安全压缩时，允许 21–24 字窄软扩展。

**冻结范围：** 51.1–51.8 的中文 V1 长度 envelope、soft-extension gate、超限原则、grapheme 计量、案例边界、成本边界与六项 Closeout Invariants。

**不在冻结范围：** D4b 句式／主体／直接性／标点、D4c owner-routed replan 细节、D4d Revision continuity、D4e localization closeout、D6 模型配置、E actual wording verifier、正式 App presentation、海外 locale 以及整个 D4／S11。

**变更规则：** 后续真实数据若提供反证，或团队明确批准新的 versioned checkpoint，才可修订；不得由 Writer、模型版本、Prompt 或临时 UI 需要静默放宽。

**后置合同对齐（2026-08-28）：** D4c1 解决了 51.4 当时显式留待后续的 owner-routing 问题，并收紧 51.3／51.6 中 qualifier 的软扩展资格：observable qualifier 仍可在 20 字内保留，但不能单独把句子带入 21–24。该澄清不改变 D4a 的 20／24 总边界、必要事实软扩展、禁止截断或其他冻结原则。

D4a 至此结束。后续 D4b–D4e 必须继承本节长度与真实性约束。

## 53. S11-D4b1｜Peak-centered Sentence Skeleton

**状态：FROZEN FOR CURRENT CHINESE TESTING / PRINCIPLES 1–6 LOCKED / LIGHT-AFFECT v1.1 AMENDMENT CROSS-CHECKED / D4 NOT FROZEN**

### 53.1 本检查点只决定什么

D4b1 只决定 Aha Moment Line 的信息中心与基本句子骨架：**先让用户直接知道这个瞬间发生了什么，但“直接”不等于监控录像式的生硬字幕。**自然度优先来自更贴切的事实性动词；28.12 Light-Affect v1.1 也允许最多一个由当前动作触发的轻量共识语气词。

本检查点仍不冻结：是否省略主语、人物如何称呼、感叹号等标点白名单、D6 具体 voice／同日重复策略，以及失败后的完整 owner routing；这些分别进入 D4b2、D4b3、D6 与 D4c。Light affect 是否进入合同已经由 28.12 关闭，不再保持开放。

### 53.2 推荐的四种骨架

~~~text
1. Peak。
2. Necessary local context，Peak。
3. Peak，Immediate support。
4. Necessary local context，Peak，Immediate support。
~~~

其中：

1. `Peak` 永远是语义中心，必须明确表达动作、事件或可见变化；
2. 如果 own media 加 peak 已能独立理解，直接使用骨架 1 或 3，不添加 context；
3. 只有 C3b2 已确认的 necessary local context 才能放在 peak 前；物理上先写 context，不代表它变成叙事中心；
4. 只有 B3 已验证的 immediate support 与 relation 才能跟在 peak 后；
5. `Observable qualifier` 只能贴附在它已绑定的 peak／support 内，不能独立形成第五段；
6. `Light affective framing`只能在 28.12 permission 指定的 event/entity 上实现，不增加新的内容段或事实 Claim；
7. 一条句子可以有多个短分句，但不能扩写成“准备—过程—结果”的小 Chapter。

### 53.3 为什么推荐 peak-centered

1. 它与 Aha“一个被挑出的精彩瞬间”的产品定义一致；
2. 用户第一眼就能判断文字是否与素材相符，降低 AI 解释和编纂感；
3. context 与 support 都有明确位置，不会反过来吞没 peak；
4. 四种骨架正好覆盖上游已冻结的 `1 peak + 0–1 context + 0–1 support + 0–1 attached qualifier`；light affect 只做 lexical framing，不创造第五个内容槽位；
5. 骨架越有限，后续 E 越容易逐段核验实际文字是否忠于 plan；
6. peak-centered 约束的是信息结构，不要求只使用最生硬的动词，也不排斥被明确治理的轻量语气。

### 53.4 案例检查

#### 案例 A｜Peak 已经能独立理解

推荐：

> 泥坯塌了下去。

不推荐：

> 镜头记录下泥坯塌下去的特别一刻。

前者直接表达可见变化；后者增加了 `镜头记录下` 的媒体说明与 `特别` 的编辑评价，却没有增加 Moment 事实。

#### 案例 B｜需要最小活动上下文

推荐：

> 拉坯时，泥坯塌了下去。

`泥坯`仍是 peak 的 core argument，不能因已有画面而省成“它塌了”。`拉坯时`仅在去掉后会把“成形过程中塌下”与之后搬动／整理时的塌落混淆，并已被 C3b2 选为必要 context 时出现；若不存在这项歧义，应退回更短的“泥坯塌了下去。”

#### 案例 C｜peak 后有即时反应

推荐：

> 甜品切开，流心淌出，桌边的人随即笑了。

不推荐：

> 甜品被切开的那一刻，香甜流心带来了满桌惊喜。

前者只在相应 Evidence 已支持时表达 peak、可见结果与即时反应；后者添加了无法由画面直接证明的味觉 `香甜`、因果 `带来了` 与群体情绪 `满桌惊喜`。

#### 案例 D｜从生硬事实到克制的人类语感

素材中一只猫跳上桌，碰倒了纸杯：

安全但偏生硬：

> 猫跳上桌，碰倒了纸杯。

优先尝试的自然事实表达：

> 猫咪跃上桌面，顺势碰倒了纸杯。

`跃上`仍对应可观察动作；`顺势`只有在动作连续与先后关系已被验证时才能出现。这里只改善动词和节奏，不需要新增情绪判断。

在 28.12 light-affect permission 获准时，也可以写：

> 猫咪调皮地跃上桌，碰倒了纸杯。

这里的`调皮地`不被伪装成客观 Fact，也不表示猫的长期性格；它是对当前低风险、无伤害动作的一次受控拟人化表达。

仍然不允许：

> 调皮的小猫故意捣乱，把大家都逗开心了。

`故意`增加了动物意图，`捣乱`增加了价值判断，“大家都开心”又推断了群体内心；轻量语气不能成为这些新 Claim 的入口。

#### 案例 E｜不是看到物种就自动套词

连续视频里，狗反复绕着草地奔跑、转身和追逐，可以进入候选：

> 狗狗活泼地绕着草地跑了几圈。

但如果狗只是安静趴着，不能仅根据“狗通常活泼”仍然添加`活泼`。同理，出现猫不自动等于`调皮`；**类别只帮助选词，当前动作才是触发条件。**

### 53.5 已确认的当前定义

D4b1 分为两层：

1. **默认层：自然事实表达。**保持 peak-centered，优先使用与 Evidence 对齐、但比机械动词更自然的表达；
2. **可选层：轻量共识语气。**每条最多一个，只描述当前动作给人的低风险共识感受，不描述用户感受，不推断意图、关系、因果或长期性格。

确认的 V1.1 约束为：

~~~text
LIGHT_AFFECTIVE_FRAMING
  count                         = 0..1
  default                      = 0
  initial target scope         = VERSIONED_COMPANION_ANIMAL_ACTION_CLASSES_ONLY
  current-action trigger       = REQUIRED
  species/category alone       = INSUFFICIENT
  user/human inner state       = FORBIDDEN
  intent / relationship claim  = FORBIDDEN
  permanent personality claim  = FORBIDDEN
  harm / distress / conflict   = NOT ELIGIBLE
  same-day lexical repetition  = CONTROLLED LATER IN D6
  locale-specific lexicon      = REQUIRED BEFORE OVERSEAS RELEASE
~~~

`调皮地、活泼地`作为当前中文待测试候选；`幸福、治愈、感动、难忘、高光、故意`仍不进入该层。词表不能只凭模型常识自由扩张，必须 versioned、可审计，并由真实用户样本校准。

### 53.6 与冻结 C3b3 的冲突及正确修订路径

原冻结 C3b3 明确规定：generated Aha 不消费 non-factual Tone，D4 也不得在 B3-validated plan 之外新增内容。因此，`调皮地／活泼地`不能被 D4 Writer 临场自由添加，也不能假装成有直接 Evidence 的 `OBSERVABLE_EMPHASIS_QUALIFIER`。

用户已经确认采用本提议，28.12 已建立显式 versioned amendment：

~~~text
observable event/action semantics
+ bounded product lexicon
→ C3b3-light-affect permission decision
   - one affect class at most
   - exact target event/entity
   - action-trigger compatibility
   - risk and exclusion checks
→ include permission ref in AhaNarrativeSurfacePlan
→ B3 validates permission/target compatibility without treating it as Fact
→ D4 realizes one locale-specific lexical span at most
→ E verifies the actual span stayed inside permission
~~~

这不会增加抽帧、上传、HQ 或新的视觉模型调用；它消费已经形成的动作语义，主要增加一层很小的策略判断和文本审计。真正风险不是算力，而是模板化、文化差异和把拟人化越界成意图／内心推断。

### 53.7 D4b1 Closeout Invariants

1. Aha Moment Line 始终以 exact peak 为信息中心，context 只可必要前置，support 只可即时后置；
2. “直接”不等于生硬：默认先用 Evidence 对齐的自然事实动词与节奏改善人类语感；
3. light-affective framing 默认 0、最多 1，必须来自 28.12 exact permission，D4 不得自由扩词；
4. 物种／类别本身不足以触发语气；当前动作、target、低风险 scope 与排除项必须全部通过；
5. light affect 不承担事实、relation、用户内心、意图、长期性格或群体反应，也不能成为超过 D4a 正常 20 字目标的理由；
6. D4b1 不改变 peak、context、support、qualifier、Aha membership、媒体、上传与全天数量，不新增视觉理解成本。

### 53.8 冻结记录

**冻结日期：** 2026-08-28

**冻结范围：** 53.1–53.7 的 peak-centered 四种骨架、自然事实表达优先、28.12 light-affect 许可边界、案例与六项 Closeout Invariants。

**不在冻结范围：** D4b2 主语／称呼、D4b3 标点／句法细则、D4c failure routing、D6 同日重复／voice／具体候选策略、E 实现、正式 App presentation、海外 locale 以及整个 D4／S11。

**变更规则：** 后续真实数据若提供反证，或团队明确批准新的 versioned checkpoint，才可修订；不能由 Writer、模型常识或临时 Prompt 静默扩大 affect scope／lexicon。

**后置 localization 对齐（D4e cross-check）：** 28.12 当前 permission 视为中文 locale instance。跨 locale 只共享 grounded action target 与基础 affect semantic eligibility；每个 target locale 必须从自己的词义／文化风险合同派生 0–1 realization permission，不能把中文`调皮／活泼`permission 直接迁移。该扩展不改变当前中文行为。

## 54. 下一检查点

D4b1 与 C3b3 Light-Affect v1.1 至此冻结。下一步进入 D4b2：主语省略与人物／动物称呼。核心产品问题是：在第一人称设备素材里，算法何时可以写`我／我们／朋友／家人`，何时只能使用`桌边的人／旁边的人／猫咪`等不推断身份关系的称呼；同时决定何时可以自然省略主语，而不会变成`它／这里／这一刻`等裸指代。

## 55. S11-D4b2｜Subject Omission & Referent Naming

**状态：FROZEN FOR CURRENT CHINESE TESTING / PRINCIPLES 1–7 LOCKED / USER CONFIRMED / D4 NOT FROZEN**

### 55.1 概念释义与本检查点边界

- **主语省略：** 中文句子不重复说“谁”，但读者仍能唯一知道动作是谁做的。例如`猫咪跃上桌面，碰倒了纸杯。`第二个动作省略了重复的`猫咪`。
- **指称／Referent：** 文字用什么名称指向画面里的人、动物或物体，例如`妈妈、桌边的人、猫咪、它`。

D4b2 只决定怎样安全、自然地称呼已在 B3 plan 中存在的实体，不重新识别人脸、不建立人物关系、不判断宠物归属，也不增加新的 identity Claim。

### 55.2 推荐的称呼优先级

~~~text
1. current user-confirmed name / relationship
2. grounded canonical category or proper name
3. grounded local neutral descriptor
4. generic existential reference
5. omit actor only when event meaning remains unique
~~~

对应中文案例：

1. 用户明确确认`妈妈`或`豆包`：可以使用该名称，但只能在同一有效 scope 内；
2. 类别已确认：使用`猫咪、狗狗、甜品、泥坯`；
3. 关系未知但位置明确：使用`桌边的人、旁边的人、戴红帽的人`；
4. 连位置也没有材料价值：可使用`有人`；
5. 动作执行者不重要且省略不会暗示用户本人时，改写为对象／事件中心表达。

越往下信息越少，但不能为了更亲切越级猜`朋友、家人、同事、我的猫`。

### 55.3 第一人称素材不自动等于“我”

推荐 V1 锁定：

1. 第一人称视角只证明相机位置，不证明账号用户就是设备佩戴者；
2. 即使画面中出现一只手，也不自动证明它是用户本人；
3. Manual capture／用户按下拍摄键只证明主动采集意图，不证明用户执行了画面中的动作；
4. generated Moment Line 使用`我`，至少需要 current `USER_SELF_CONFIRMED` identity-action mapping——即用户已明确确认“当前素材中的该动作由我完成”——或未来另行批准的等价 wearer/session identity 合同；
5. `我们`除上述 self mapping 外，还要求可验证的共同动作／共同参与范围；仅看到其他人不能写`我们`；
6. `朋友、家人、妈妈、同事、主人`等关系词必须来自 current user-confirmed 或同等级 trusted relation，不从年龄、同桌、同行时间、相似长相或场景常识推断。

因此，在当前尚未完成 wearer/session identity 合同的 V1 测试里，generated Aha **默认不使用`我／我们`**。这不会删除用户自己写下的第一人称文字；protected user-authored text 继续保持原样。

### 55.4 什么时候可以自然省略主语

允许：

1. 同一句前半段已经给出唯一主体，后半段只是该主体的连续动作；
2. 执行者不是 Moment 的材料事实，可以使用对象中心或状态变化表达；
3. 省略后不会被自然理解成用户本人，也不会改变主动／被动、数量或 relation。

不允许：

1. 同一句有两个人／动物都可能成为后续动作主体；
2. 谁做了动作正是 peak 或 support 的关键；
3. 省略会让`伸手、笑了、吹灭、拿起`等动作错误挂到最近实体；
4. 只能依赖 parent Chapter 或画面猜`它／这里／这时／这一刻`指什么；
5. 为了卡 20 字删除 core argument，例如把`泥坯塌了下去`缩成`它塌了`。

### 55.5 动物称呼的窄规则

1. `猫咪／狗狗`是当前中文 voice 的类别称呼，不声明年龄；
2. `小猫／小狗`可能声明幼龄或体型，只有 Evidence／用户确认支持时使用；
3. 宠物名字只有 current user-confirmed canonical name 才能使用；
4. 多次出现同一动物不自动证明`我的猫／我家狗狗`；ownership 仍需确认；
5. 28.12 light affect 只修饰已合法指称的 animal action，不能把`猫`升级成`我家调皮的小猫`。

### 55.6 案例检查

#### 案例 A｜同一主体的自然省略

推荐：

> 猫咪跃上桌面，碰倒了纸杯。

`碰倒`的主体唯一延续为`猫咪`，无需重复写“猫咪又碰倒了纸杯”。

#### 案例 B｜第一人称画面里切开甜品

当前安全版本：

> 甜品切开，流心淌了出来。

更自然且已有 immediate relation Evidence 时，优先写：

> 甜品一切开，流心就淌了出来。

没有 wearer identity 合同时，不写：

> 我切开甜品，流心淌了出来。

`一……就……`只在切开与流心淌出的即时关系已验证时使用；它改善自然度，但不指定谁切开。`我切开`则额外断言“动作执行者就是用户”。如果未来 session 能可靠证明这一点，或用户明确确认，才允许使用`我`。

#### 案例 C｜关系未知的人伸手

推荐：

> 猫咪跃上蛋糕，桌边的人伸手去拦。

不推荐：

> 猫咪跃上蛋糕，朋友赶紧伸手去拦。

画面可以证明位置与动作，却不能单靠同桌证明`朋友`关系；`赶紧`还需要动作速度／紧迫性 Evidence。

#### 案例 D｜多主体时不能裸用“它”

画面里同时有猫和狗：

不安全：

> 猫和狗跑到桌边，它碰倒了纸杯。

`它`有两个合法指向。若 Evidence 已确认是猫，应写：

> 猫和狗跑到桌边，猫碰倒了纸杯。

如果无法确认，相关 support／peak Claim 本身就不能进入最终句子，D4不能靠代词掩盖不确定性。

#### 案例 E｜用户确认的名字

用户已在有效 scope 内确认猫名为`豆包`，且 entity continuity 成立：

> 豆包跃上桌面，碰倒了纸杯。

名字确认不等于 ownership、性格或关系都被确认；仍不能自动写`我家调皮的豆包`。

### 55.7 成本与边界

1. 主要消费既有 entity refs、planned referent map、user-confirmed identity／relation 与同句语法检查；
2. 不新增人脸识别、人物关系识别、抽帧、上传、HQ、VLM 或外部 lookup；
3. V1 默认不用`我／我们`会牺牲少量日记式亲密感，但显著降低设备借用、共享佩戴与动作归属错误；
4. 英文等语言不能照搬中文主语省略规则；其 pronoun、gender、number、article 与 relationship naming 必须在 D4e 建立 locale-specific contract；
5. D4b2 不改变 protected user text，也不决定 App 是否允许用户把中性称呼编辑成自己的关系称呼。

### 55.8 D4b2 Closeout Invariants

1. 第一人称相机位置不自动证明账号用户、设备佩戴者与动作执行者是同一主体；
2. 当前 V1 generated Aha 默认不使用`我／我们`；只有 current user-confirmed self-action mapping 或未来明确批准的可靠 wearer/session identity 合同可以例外；
3. `朋友、家人、妈妈、同事、主人、我的宠物`等关系／ownership 必须有 current user-confirmed 或同等级 trusted relation；
4. 称呼按“已确认名称／关系 → grounded 类别／专名 → 中性局部描述 → 有人 → 安全省略”的顺序降级，不能为了亲切越级猜身份；
5. 只有 referent 唯一、动作归属不变且不会自然暗示用户本人时，才可省略重复主语；core argument 不为卡字数变成裸`它／这里／这一刻`；
6. `猫咪／狗狗`不声明幼龄，`小猫／小狗`与宠物名字／ownership 各自需要相应 Evidence 或用户确认；light affect 不改变 identity 合同；
7. protected user text 保持原样；本规则不增加人脸／关系识别、抽帧、上传、HQ、VLM 或外部 lookup，海外 locale 另建 pronoun/referent 合同。

### 55.9 冻结记录

**冻结日期：** 2026-08-28

**冻结范围：** 55.1–55.8 的主语省略、referent naming priority、第一人称默认、人物关系／宠物称呼、案例、成本边界与七项 Closeout Invariants。

**不在冻结范围：** 未来 wearer/session identity source 的具体产品与工程合同、App 人物／宠物标注交互、D4b3 标点／句法、D4c failure routing、D6 voice、E 实现、海外 locale 以及整个 D4／S11。

**变更规则：** 后续可靠身份来源、真实用户数据或团队明确批准的新 versioned checkpoint 才可修订；不能因第一人称画面看起来“像用户本人”或为了语气亲密而静默升级称呼。

## 56. 下一产品决策

D4b2 至此冻结。下一步进入 D4b3：中文 Moment Line 的句法与标点。重点确认默认句末、内部逗号预算、是否允许感叹号，以及哪些连接词会把一个 Moment 扩写成小故事。

## 57. S11-D4b3｜Chinese Syntax & Punctuation

**状态：FROZEN FOR CURRENT CHINESE TESTING / PRINCIPLES 1–7 LOCKED / USER CONFIRMED / D4 NOT FROZEN**

### 57.1 推荐 Baseline

~~~text
logical sentence count         = 1
default terminal punctuation   = 。
internal Chinese commas        = 0..2
ellipsis                       = FORBIDDEN
semicolon / colon / em dash    = FORBIDDEN
question mark                  = FORBIDDEN FOR GENERATED EVENT LINE
exclamation mark               = FORBIDDEN FOR CURRENT CHINESE V1
newline as content separator   = FORBIDDEN
all visible punctuation        = COUNTED BY D4a
~~~

“一句”指一个完整 logical sentence，不等于只能有一个短分句。Context、peak 与 immediate support 最多形成：

~~~text
Peak。
Context，Peak。
Peak，Support。
Context，Peak，Support。
~~~

两枚内部逗号已经覆盖 D4b1 的最大骨架；若还需要分号、冒号、破折号或第三枚逗号，优先说明句子正在变成小 Chapter、解释说明或素材列表，应返回 wording／plan 检查，而不是继续加标点。

### 57.2 句法优先级

1. 优先具体动词与自然中文节奏，不使用`镜头记录了／画面中出现／这是……的一刻`等 meta narration；
2. 执行者不重要时优先对象／事件中心表达，不为了避免`我`而机械堆叠被动句；
3. `一……就……、随即、接着、随后、终于、最终`等词都会声明关系或叙事位置，只能实现 B3 已验证的 relation；
4. `然后／后来／最终`容易扩成准备—过程—结果，单一 Aha 默认不用；
5. 不用并列清单压入多个对象／动作；顿号`、`默认不作为 generated Aha 的内容组织工具；
6. 句末标点表达语气，不得反过来制造一个上游没有批准的情绪层。

### 57.3 为什么默认使用句号

1. Aha 已通过选材、媒体和轻量语气表达精彩，不需要每条都靠感叹号宣布“这是高光”；
2. 感叹号不新增事实，却会提高系统替用户兴奋、夸张或模板化的感受；
3. 同一天 2–3 个 Aha 若都以`！`结尾，节奏容易像营销文案而不像私人记忆；
4. 句号并不要求文字冷淡，自然动词、节奏和 28.12 light affect 已可以提供人类语感；
5. 当前中文 V1 已确认不开放感叹号；未来只有真实数据与新的 versioned permission 才能重开，不能由 Writer 自由选择。

### 57.4 案例检查

#### 案例 A｜句号不等于生硬

推荐：

> 猫咪调皮地跃上桌，碰倒了纸杯。

不必为了强调 Aha 自动写：

> 猫咪调皮地跃上桌，碰倒了纸杯！

自然感来自`猫咪、调皮地、跃上`与动作本身；感叹号不是必需的高光标签。

#### 案例 B｜两枚逗号覆盖最大骨架

> 拉坯时，泥坯缓缓塌下，旁边的人伸手扶住。

它对应`Context，Peak，Support。`。如果还要继续补“随后大家重新开始”，就已经进入后续故事，不属于同一个 Moment Line。

#### 案例 C｜关系词必须有计划

有 immediate relation Evidence 时可以写：

> 甜品一切开，流心就淌了出来。

只有两张不连续结果照片时，不可以为了顺口写`一……就……`；应退回不声明即时关系的事实表达，或由上游重新判断 relation。

#### 案例 D｜不把 Aha 写成说明或标题

不推荐：

> 高光时刻：猫咪跃上桌面——纸杯随之倒下！

冒号制造标题层，破折号制造解释层，感叹号再附加兴奋语气；它绕开了 V1 单一 Moment Line 的产品结构。

#### 案例 E｜省略号仍然禁止

不允许：

> 猫咪跃上桌面，纸杯随后……

它既截断事实，又用悬念制造未发生的叙事期待；必须完整短写或进入 D4c replan。

### 57.5 已确认结论

中文 V1 锁定：**一个完整句子、默认句号、最多两枚内部中文逗号；不使用问号、省略号、分号、冒号、破折号或换行组织内容；感叹号暂不开放给 generated Aha。**

这是一个保守的 V1 起点。若真实用户测试明确显示句号版本普遍过于平淡，再单独设计可审计的 exclamatory permission，而不是让 Writer 凭“感觉精彩”随机加`！`。

### 57.6 D4b3 Closeout Invariants

1. generated Aha 只有一个完整 logical sentence，不通过换行或标点伪造第二个内容槽；
2. 当前中文 V1 统一以`。`结束，句末标点计入 D4a 字符预算；
3. 内部中文逗号最多两枚，只服务`Context，Peak，Support。`四种合法骨架；
4. 问号、省略号、分号、冒号、破折号、内容换行与 generated 感叹号当前禁止；
5. `一……就……、随即、随后、终于、最终`等 relation-bearing 词只能实现已由 B3 验证的 relation，不能仅为顺口添加；
6. 不使用标点建立 generated Title、解释层、悬念、素材列表或准备—过程—结果的小 Chapter；
7. 本规则不修改 plan、Claim、关系、用户原文或 App 物理换行；海外 locale 的 punctuation／sentence-boundary contract 在 D4e 单独定义。

### 57.7 冻结记录

**冻结日期：** 2026-08-28

**冻结范围：** 57.1–57.6 的中文句子数、句末、内部逗号预算、标点白名单、relation-bearing 词边界、案例与七项 Closeout Invariants。

**不在冻结范围：** protected user text 自带标点、正式 App 的物理换行／截断、未来 exclamatory permission、D4c 压缩与失败路由、D6 voice、E 实现、海外 locale 以及整个 D4／S11。

**变更规则：** 只有真实用户数据或新的显式 versioned checkpoint 才可重开；不能由 Writer、Prompt 或“这条看起来精彩”静默增加感叹号或第二句结构。

## 58. 下一产品决策

D4b3 至此冻结。下一阶段进入 D4c：bounded compression 与 owner-routed failure。先讨论 D4c1——当合法 Moment Line 超出目标长度时，哪些内容可以按什么顺序省略，哪些必须保留并在无法表达时 Block。

## 59. S11-D4c1｜Compression Priority & Semantic Preservation

**状态：FROZEN FOR CURRENT CHINESE TESTING / PRINCIPLES 1–8 LOCKED / USER CONFIRMED / D4 NOT FROZEN**

### 59.1 所在链路与本检查点目标

D4c1 位于 B3 已验证完整 plan、D4 首次产生具体中文 wording 之后。它不重新评选 Aha，也不把“短”凌驾于“真实”之上；它只回答：**当文字超过 D4a 的 20／24 字 envelope 时，怎样做单调、可审计的简化。**

~~~text
B3_VALIDATED exact plan
→ D4 initial wording
→ length + syntax check
   ├─ ≤20 and valid → continue E
   ├─ 21..24, only necessary validated factual content → soft extension → E
   └─ otherwise → D4c1 ordered compression / owner routing
~~~

### 59.2 推荐的固定优先级

~~~text
KEEP ALWAYS
  exact PEAK core arguments + predicate

KEEP WHEN STILL NECESSARY
  minimal local context required for standalone understanding

REMOVE / SIMPLIFY IN THIS ORDER
  0. unplanned filler / meta wording / redundant function words
  1. realized LIGHT_AFFECTIVE_FRAMING span
  2. selected OBSERVABLE_EMPHASIS_QUALIFIER, through C3b3 replan
  3. selected IMMEDIATE_SUPPORT, through C3b2 replan

NEVER SILENTLY REMOVE
  peak core
  still-necessary local context
  required core argument / referent
  validated relation while retaining both dependent clauses
~~~

排序理由：light affect 只改善语气，不承担事实；observable qualifier 是真实但可选的窄属性；immediate support 是额外反应／结果；necessary context 则决定 Aha 脱离 Chapter 后是否仍能看懂。Peak 是 Aha 存在的根本，永不因长度被 Writer 删除或替换。

### 59.3 同一 plan 内可以怎样压缩

在改变任何上游内容前，D4 最多做一次 same-plan wording rewrite：

1. 删除`镜头记录下、在这个瞬间、可以看到`等不承载 Claim 的 meta/filler；
2. 删除不改变事实的重复主体与虚词；
3. 使用更短但语义、强度、时序与指向相同的自然表达；
4. 调整语序以减少重复，但不得改变谁做了什么、先后／即时／因果关系或 qualifier attachment；
5. 不能把删除了 Claim／relation 的结果谎称为“同义压缩”。

案例：

较长写法：

> 甜品被切开以后，里面的流心淌了出来，桌边的人随即笑了起来。

若 exact plan 只包含“甜品切开、流心淌出、桌边的人随即笑”，可以压缩为：

> 甜品切开，流心淌出，桌边的人随即笑了。

这里删除的是被动结构、重复方位和完成体冗余，没有删除 peak、reaction 或`随即`relation。若`从中间淌出`本身是 selected Claim，则不能擅自删掉`从中间`。

### 59.4 先删 light affect，不用它突破 20 字

若一句 factual wording 本可在 20 字以内，只因`调皮地／活泼地`等 span 超过 20，D4 直接保持该 permission 为“已许可但未实现”，不进入 21–24 软扩展。

例如不含 light affect 的完整事实共 18 个 visible grapheme clusters（含标点）：

> 猫咪跃上桌，碰倒纸杯，有人扶住杯子。

加入`调皮地`后变为 21，超过正常目标。此时优先保留完整动作／support，省略 light affect；不能为了保留语气词删除`有人扶住杯子`，也不能让 light affect 成为 21–24 软扩展理由。

### 59.5 qualifier 与 support 必须由 owner 重做 plan

D4 Writer 不能自行删除已经进入 B3 plan 的事实内容：

| 失败内容 | 正确 owner | 允许动作 | 禁止动作 |
|---|---|---|---|
| light-affect span | D4 realization | permission 保留，realized span 取 0 | 改成另一个未许可情绪词 |
| observable qualifier | C3b3 | 建立 qualifier-free immutable decision／plan，再过 B3 | Writer 静默删`缓缓／一下子` |
| immediate support | C3b2 | 重做 support/context decision，确认删除后 standalone 仍成立，再过 C3b3/B3 | Writer 只删半句或保留失去依附的`随即` |
| necessary context | C3b2 | 只能验证更短 wording 是否表达同一 context；仍必要则保留 | 为卡字数删掉后发布含糊 Aha |
| peak core／core argument | 上游 Claim/selection owner；D4 当前 Revision Block | 不在 D4c 改 peak；明确返回 failure | 换成别的事件、裸`它`、删除谓词或撤出 Aha补位 |

### 59.6 案例检查

#### 案例 A｜先删 qualifier，而不是删必要背景

假设`拉坯时`是消除歧义所必需的 context，`缓缓`是合法但可选 qualifier：

> 拉坯时，泥坯缓缓塌下，旁边的人随即伸手扶住。

该句共 22 个 visible grapheme clusters（含标点）。假设`旁边的人`、`随即`与`伸手扶住`分别对应不能删改的 exact referent、relation 与 support action，而且一次 same-plan wording rewrite 已证明不存在更短自然等价表达；此时虽然没有超过 24，`缓缓`仍只是可选 qualifier，不能用它占用“只为必要事实开放”的 21–24 软扩展。因此返回 C3b3 形成 20 字的 qualifier-free plan：

> 拉坯时，泥坯塌下，旁边的人随即伸手扶住。

不能先删`拉坯时`，因为那可能让用户无法区分成形中塌下与之后搬动时塌落。

#### 案例 B｜support 可以删除，但 relation 必须一起删除

若 support 不是 standalone understanding 所必需、且 qualifier-free 仍超限，可由 C3b2 重做为 peak＋context：

> 拉坯时，泥坯塌了下去。

不能生成：

> 拉坯时，泥坯塌下，随即。

也不能只删动作却保留暗示 adjacency 的`随即`。

#### 案例 C｜必要内容仍放不下时 Block

如果 peak core 加仍然必要的 context 在一次 same-plan rewrite、去除 light affect、qualifier 与非必要 support 后仍超过 24，D4c 不继续牺牲语义。当前 required Moment Line 进入显式 Block／HOLD；Aha 不被删除、不找补位，也不发布残句。

### 59.7 已确认结论

当前中文测试版冻结上述顺序：**先压缩纯 wording，再省略已实现的 light affect；仍不合格时依次由 C3b3 去 qualifier、由 C3b2 去非必要 support；peak 与仍必要 context 永不为长度静默删除，最小合法内容仍无法表达就 Block。**

D4c1 只冻结语义优先级和 owner，不在本节确定整个 Writer/replan 的全局次数；具体 hard attempt budget 与最终状态机留给 D4c2。

### 59.8 D4c1 Closeout Invariants

1. 在改变 plan 前，最多执行一次不改变 Claim、relation、强度、指向与 attachment 的 same-plan wording rewrite；
2. 超长时按`unplanned filler／冗余 wording → realized light affect → observable qualifier → 非必要 immediate support`的固定顺序简化；
3. light-affect permission 可以保留，但 realized span 必要时取 0；light affect 永远不能成为 21–24 软扩展理由；
4. selected qualifier 只能由 C3b3 产生 qualifier-free immutable decision／plan，D4 Writer 不能静默删除；
5. selected support 只能由 C3b2 重新判断，删除时必须同时删除依赖它的 relation，并重新执行 context necessity；
6. peak predicate、core arguments、唯一 referent 与仍必要的 local context 永不为长度被静默删除、泛化或替换；
7. 21–24 只保留必要且已验证、无法安全短写的内容；可选 qualifier、support 或 light affect 不能占用该区间；
8. 最小合法内容仍无法表达时，当前 required Moment Line 进入显式 Block／HOLD；不删除 Aha、不搜索补位、不让 Chapter 吞回该事件，也不发布残句或含糊短句。

### 59.9 冻结记录

**冻结日期：** 2026-08-28

**用户确认：** 同意 light affect、observable qualifier、非必要 immediate support 依次让位；peak 与仍必要 local context 必须保留，即使结果是当前 Revision 暂不发布。

**冻结范围：** 59.1–59.8 的压缩顺序、same-plan 边界、owner routing、soft-extension 资格、案例与八项 Closeout Invariants。

**不在冻结范围：** D4c2 的 attempt budget／最终状态名、D4d Revision continuity、D4e localization、D6 provider／模型／候选／transport retry、E actual wording verification、App fallback、海外 locale 以及整个 D4／S11。

**变更规则：** 只有真实数据或新的显式 versioned checkpoint 才可修订；不得由 Writer、Prompt、模型版本或成本压力静默改变删减顺序。

## 60. 下一产品决策

D4c1 至此冻结。下一步进入 D4c2：给上述路径设置一个全局有界的 semantic realization attempt envelope，并把正常通过、继续改写、owner replan、内容阻断与工程合同损坏分成不同状态。

## 61. S11-D4c2｜Bounded Realization Attempts & Terminal Routing

**状态：FROZEN FOR CURRENT CHINESE TESTING / PRINCIPLES 1–10 LOCKED / USER CONFIRMED / D4 NOT FROZEN**

### 61.1 所在链路与本检查点目标

D4c2 不重新决定“先删什么”；它继承 D4c1，并回答两个问题：

1. 同一条 Aha 在同一 Revision 中最多允许形成多少个有意义的文案版本；
2. 合法路径用尽后，怎样区分内容性 Block 与工程 Contract Invalid。

本节冻结的是**语义层 attempt 上限**，不是模型供应商的 HTTP 请求次数。模型、Prompt、temperature、一次请求返回几个 candidates、网络超时是否重试与 transport retry budget 仍属于 D6／工程合同；E 的具体真实 span 验证规则也仍在后续讨论。D4c2 只要求这些后续机制不能重置或绕过本节的语义上限。

### 61.2 概念释义

#### Semantic realization attempt｜一次语义实现尝试

指在一个明确、已通过 B3 的 exact plan 上形成一条 canonical `AhaMomentLineDraft`，随后执行长度、句法、标点与结构预检。它关注“这一次在写哪一组已批准内容”，不等于一次网络请求。

#### Attempt fingerprint｜尝试指纹

由 current Revision、Aha surface、B3-validated plan、realization class、locale／length／voice policy 等共同形成的唯一标识。相同指纹失败后不能换个 request id 再跑一遍；只能复用既有结果或进入下一个严格简化状态。

#### Terminal｜当前路径终止

表示本 Revision 已没有仍符合冻结原则的合法下一步，不表示删除 Aha，也不表示系统可以临场换素材或换 peak。

### 61.3 推荐上限：最多四类 canonical draft

每个 `(stable_memory_id, revision_ref, AHA_MOMENT_LINE)` 最多形成以下四类 draft；不适用的类别直接跳过，不能把空出来的名额换成额外同义词重试：

| 顺序 | attempt class | 允许变化 | 不允许变化 |
|---:|---|---|---|
| 1 | `INITIAL_EXACT_PLAN` | 按 exact B3 plan 首次自然实现；已许可 light affect 可实现 0–1 | 改 Claim、relation、peak、referent 或 plan |
| 2 | `SAME_PLAN_CONCISE` | 最多一次纯 wording 压缩；必要时把 realized light affect 置 0 | 删除 planned Claim／relation，改变强度或换事件 |
| 3 | `QUALIFIER_FREE` | 仅在存在 selected qualifier 时，由 C3b3 建立 0 qualifier plan，重新过 B3 后实现一次 | 改 C3b2 base selection，寻找别的 qualifier，重新加入 light affect |
| 4 | `SUPPORT_FREE_MINIMAL` | 仅在 C3b2 证明 support 非必要时，删除 support、重算 context necessity；随后以 0 qualifier、0 realized light affect 过 C3b3/B3 并实现一次 | 删除必要 context、重新加入较低优先级内容、换 peak 或补位 |

因此：

~~~text
common path                         = 1 draft
same-plan wording repair            = at most 1 additional draft
qualifier-free owner replan         = at most 1 additional draft
support-free owner replan           = at most 1 additional draft
hard maximum                        = 4 canonical drafts / Aha / Revision
~~~

`LIGHT_AFFECT_DROP`不另开第五类：它属于`SAME_PLAN_CONCISE`，可以是安全的确定性删除，也可以是一次保持事实 plan 不变的短写。`SUPPORT_FREE_MINIMAL`中的 context 必须重新做 necessity test；若删除 support 后新证明一组 context 必要，可以保留该 context。这不是恢复可选内容，而是维持 standalone correctness。

### 61.4 单调性与预算不能重置

1. 每个 attempt class 在同一 surface／Revision 中最多产生一个 canonical draft；
2. 失败的 exact attempt fingerprint 永不重复运行；重复 App 打开、重复 Sync callback 或 worker 重启只读取 immutable result；
3. 没有 qualifier 时直接跳过`QUALIFIER_FREE`，但不能因此增加第二次`SAME_PLAN_CONCISE`；
4. qualifier 一旦因长度让位，后续 support-free plan 也保持 0 qualifier；light affect 一旦让位，后续也保持 0 realized span；
5. support 删除后必须重算 context necessity，但不能搜索新 support、第二 context、新 peak 或更宽 identity；
6. 只有 dependency／Evidence／policy fingerprint 发生材料变化并依法创建新的 Revision，才获得新 Revision 的 attempt envelope；retry 本身不能制造新 Revision；
7. 后续 E 若把 draft 作为 wording-only failure 返回 D4，必须消费同一 envelope 中尚未使用的合法 class，不能另起一套计数；具体 E reason→owner 映射仍由 E 冻结；
8. D6 即使在一次 provider call 内生成多个候选，也只能选择一个 canonical draft 落入当前 attempt class；候选数量和 transport retry 不得创造第五种语义状态。
9. D4 长度回路只请求 exact qualifier-free 或 support-free strict plan，不重置 C3b3 已冻结的 B3 fingerprint 上限；support-free 新 base decision 也不能借机重新遍历 affect／qualifier 排列，只形成当前 D4 路由要求的单一严格简化 plan。

这里的“单调”指可选表达负担只会减少：light affect 不再实现、qualifier 归零、support 最终归零。Context 因 removal test 重新证明为必要时可以出现，因为它的优先级高于这些可选内容；但它若导致最小合法句仍放不下，只能 Block，不能再次把 qualifier／support 加回来循环搜索。

### 61.5 状态机与 owner

~~~text
D4_INITIAL_OR_REENTRY
  → canonical draft + deterministic D4 checks
      ├─ pass
      │    → D4_DRAFT_READY_FOR_E
      ├─ same exact plan still has concise slot
      │    → D4_SAME_PLAN_REWRITE_REQUIRED
      ├─ selected qualifier is next legal removal
      │    → D4_OWNER_REPLAN_REQUIRED(owner=C3B3_OBSERVABLE_EMPHASIS)
      ├─ non-necessary support is next legal removal
      │    → D4_OWNER_REPLAN_REQUIRED(owner=C3B2_BASE_SELECTION)
      ├─ legal attempt classes exhausted / minimum content cannot fit
      │    → D4_REQUIRED_SURFACE_BLOCKED
      └─ ref / Revision / schema / fingerprint / policy contract invalid
           → D4_REALIZATION_CONTRACT_INVALID
~~~

状态含义：

| 状态 | 含义 | 下游行为 |
|---|---|---|
| `D4_DRAFT_READY_FOR_E` | D4 长度／句法／结构预检通过 | 进入 E；仍不等于 `PUBLISH_READY` |
| `D4_SAME_PLAN_REWRITE_REQUIRED` | exact plan 不变且唯一短写名额尚未使用 | 只运行一次`SAME_PLAN_CONCISE` |
| `D4_OWNER_REPLAN_REQUIRED` | 必须修改 planned optional content | 回唯一 owner，产生新 immutable plan 并重过 B3；旧 draft 不进入 E |
| `D4_REQUIRED_SURFACE_BLOCKED` | 没有合法下一类 attempt 或最小内容仍失败 | first build 映射`INITIAL_BUILD_BLOCKED`，后续 Revision 映射`TEXT_BLOCK`，再按既有 C3a 聚合为`CONTINUITY_BLOCKED` |
| `D4_REALIZATION_CONTRACT_INVALID` | 引用、lineage、schema、policy 或 fingerprint 损坏 | 工程诊断并聚合`CONTINUITY_CONTRACT_INVALID`；不能伪装成普通内容 Block |

只要某一 draft 通过 D4，就立即进入 E，不为了“再看看能不能写得更好”继续消耗后续 attempt。D4 也不声明最终发布成功；E 与 S12 仍分别拥有实际 wording 验真与最终发布权。

### 61.6 当前 Revision 的产品行为

1. required Aha Moment Line 进入`D4_REQUIRED_SURFACE_BLOCKED`后，不从当天其他候选中补一个 Aha，不减少 membership，不让 parent Chapter 吞回它；
2. 当前未完成 Revision 不发布残句、空字符串、固定占位或只包含其他成功 Memory 的临时子集；
3. 若存在上一条已发布且在 current Evidence 下仍然合法的 Revision，是否继续显示仍沿用既有 C3a retention／presentation 合同；D4c2 不复制已失效旧文字到新 Revision；
4. Contract Invalid 与内容写不下分开统计：前者是系统完整性问题，后者是合法内容在当前文字合同内无法安全实现；
5. failure audit 必须保存最后一个 legal plan、最后一个 draft、实际字符数、失败 gate、已用 attempt classes 与唯一 next／terminal reason。

### 61.7 案例检查

#### 案例 A｜普通情况只生成一次

> 猫咪调皮地跃上桌，碰倒了纸杯。

共 15 个 visible grapheme clusters，plan、句法与标点均合法。`INITIAL_EXACT_PLAN`直接进入 E，不再生成“猫咪淘气地……”等风格备选。

#### 案例 B｜light affect 在唯一 concise attempt 中让位

初稿：

> 猫咪调皮地跃上桌，碰倒纸杯，有人扶住杯子。

共 21 字，超限部分只有不能使用软扩展的 light affect。`SAME_PLAN_CONCISE`将 realized span 置 0：

> 猫咪跃上桌，碰倒纸杯，有人扶住杯子。

共 18 字，通过后停止；不另开“light-affect retry”。

#### 案例 C｜第三类 attempt 保住 support，只删 qualifier

假设一次 same-plan concise 已证明 exact referent、relation 与 support action 无更短自然等价表达：

> 拉坯时，泥坯缓缓塌下，旁边的人随即伸手扶住。

22 字不能靠可选`缓缓`进入软扩展。C3b3 生成 qualifier-free plan，第三类 draft 为：

> 拉坯时，泥坯塌下，旁边的人随即伸手扶住。

20 字通过，因此保住了比 qualifier 优先级更高的 immediate support，不进入第四类。

#### 案例 D｜第四类 attempt 才删除非必要 support

假设`吹制玻璃时`是必要 context，`突然`是 selected qualifier，后半句是有材料增量但非 standalone 必需的 support：

> 吹制玻璃时，玻璃泡突然塌下，旁边的人随即伸手托住。

初稿 25 字；same-plan concise 仍失败。qualifier-free draft 为：

> 吹制玻璃时，玻璃泡塌下，旁边的人随即伸手托住。

它仍有 23 字，而且 support 是可选内容，不能占用 21–24 软扩展。C3b2 删除 support、重算并继续保留必要 context，第四类 draft 为：

> 吹制玻璃时，玻璃泡塌了下去。

14 字通过。系统不能再把`突然`加回来，也不能换另一条反应。

#### 案例 E｜没有合法下一类时提前终止

> “星河杯青少年机器人总决赛”现场，六号机器人翻过最后一道障碍。

若完整赛事名称确由用户确认、对区分正式比赛与排练确实必要，又没有可信短名；peak core 也不能再缩，且当前 plan 本来就没有 light affect、qualifier 或 support，那么 same-plan concise 失败后应直接 Block。无需为了凑满四次重复请求模型，更不能擅自缩成含糊的“比赛现场”。

#### 案例 F｜Contract Invalid 不走压缩阶梯

如果 draft 引用的 B3 plan 属于 prior Revision，系统不能先删 qualifier 看能否“修好”。它直接进入`D4_REALIZATION_CONTRACT_INVALID`，由工程责任阶段修复引用；否则一条看似自然的句子会建立在错误版本的事实之上。

### 61.8 成本、效率与四次上限的理由

1. 正常路径每条 Aha 只形成 1 个 draft；只有明确失败才继续；
2. 对单个需要重建全部 2–3 个 Aha 的 Revision，正常为 2–3 个 logical drafts，极端情况下才是 8–12 个；这不是全天跨多次 Revision 的绝对上限；
3. 一天多次 Sync 不自动重写全部 Aha：没有材料变化且依赖仍有效的 surface 走 C3a `TEXT_RETAIN`，不调用 Writer；真正的 day-level call／token cap 必须在 D6 结合材料性 Revision 次数另行冻结；
4. 上述路径不增加抽帧、上传、HQ、VLM 或 Raw media 读取；grapheme、标点、attempt fingerprint 与路由检查都是 deterministic local logic，C3b2/C3b3/B3 重用既有 Claim／Evidence；
5. 选择 4 而不是 3，是为了在“完整 plan → 简洁 wording → 去 qualifier → 去 support”之间保留质量梯度；若只有 3 次，要么跳过 same-plan 修复，要么被迫一次删掉 qualifier 与 support，可能损失本可保留的真实内容；
6. 上限 4 不是要求跑满；任何阶段通过或不存在下一合法 owner 都立即停止；
7. D6 仍需另外冻结每个 logical attempt 的 provider call、candidate、token、latency、transport retry、缓存与 day-level budget，并保证它们不能扩大本节语义状态空间。

### 61.9 已确认结论

当前中文测试版冻结：**每条 required Aha Moment Line、每个 Revision 最多 4 类 canonical draft；普通情况 1 次，依次最多增加一次 same-plan concise、一次 qualifier-free、一次 support-free。跳过的类别不转换成额外重试，E 回流不重置预算，合法路径耗尽后进入内容 Block，合同损坏单独进入 Contract Invalid。**

### 61.10 D4c2 Closeout Invariants

1. 每个 required Aha Moment Line、每个 Revision 最多形成`INITIAL_EXACT_PLAN → SAME_PLAN_CONCISE → QUALIFIER_FREE → SUPPORT_FREE_MINIMAL`四类 canonical draft；
2. 普通成功路径只形成一个 draft；任一阶段通过即停止，不为文风偏好继续生成；
3. 每类 attempt 最多一次；不适用的类别跳过，不能兑换成额外同义词、同级 retry 或第五种语义状态；
4. exact attempt fingerprint 失败后不得重复；App 重开、Sync callback、worker 重启与 provider request id 变化都不重置 envelope；
5. 只有 dependency／Evidence／policy 发生材料变化并依法形成新 Revision 才获得新 envelope；retry 本身不创建 Revision；
6. light affect、qualifier 与 support 按冻结顺序单调让位；support 删除后必须重算 context necessity，但不得恢复较低优先级内容或搜索新 peak／support；
7. qualifier 与 support 改变分别返回 C3b3／C3b2 唯一 owner，产生 immutable strict plan 并重新通过 B3；D4 Writer 不直接改 plan；
8. `D4_DRAFT_READY_FOR_E`只表示进入 E，不等于发布成功；后续 E／D6 回路必须共用本 envelope，不能建立平行计数；
9. 合法路径耗尽映射 required surface Block，并按既有 C3a 聚合暂停当前 Revision；不删除 Aha、不补位、不发布残句或临时子集；
10. ref／lineage／schema／policy／fingerprint 损坏进入 Contract Invalid 而非内容 Block；D6 的 provider、candidate、Token、transport retry、cache 与 day-level budget 必须有界且不能扩大本节语义状态空间。

### 61.11 冻结记录

**冻结日期：** 2026-08-28

**用户确认：** 同意“最多四类、通常一次”的 semantic attempt envelope，以及 required Moment Line 合法路径耗尽后不发布当前 Revision、也不自动换 Aha 的终止行为。

**冻结范围：** 61.1–61.10 的 attempt 定义、四类上限、单调顺序、fingerprint／Revision reset 边界、状态机、产品行为、案例、成本口径与十项 Closeout Invariants。

**不在冻结范围：** D4d cross-Revision wording continuity、D4e localization、D6 provider／模型／Prompt／candidate／transport retry／day-level cost、E actual wording verification、App fallback、海外 locale、Production infrastructure 以及整个 D4／S11。

**变更规则：** 只有真实失败分布、成本 Benchmark 或新的显式 versioned checkpoint 才可修订；不得由模型版本、供应商 SDK、worker 重启或临时降级逻辑静默扩大 attempt 数量。

**后置 localization 对齐（D4e cross-check）：** 61.3 当前中文 key 完整化为`(stable_memory_id, revision_ref, target_locale_policy_ref, AHA_MOMENT_LINE)`；每个 locale 仍最多四类且通常一次。不同 locale 不共享或重置彼此 envelope，D6 另行建立跨 locale day-level 总预算。当前中文测试的上限与顺序不变。

## 62. 下一产品决策

D4c2 至此冻结。整体云端部署与成本边界已完成一次阶段性说明；现在进入 D4d：在后续 Sync／Revision 中，什么时候保留旧 Moment Line、什么时候只修最小 span、什么时候必须重建或 Block。该阶段不重新打开 D4a–D4c2。

## 63. S11-D4d｜Cross-Revision Moment Line Stability

**状态：FROZEN / D4d1 + D4d2 + D4d3 CONFIRMED / CROSS-CHECK PASSED WITH 2 CONTRACT-ALIGNMENT AMENDMENTS**

### 63.1 D4d 在链路中的位置

D4d 是 C3a 四状态合同在 Aha `MOMENT_LINE` 上的实现细化，不创建与 C3a 竞争的第二套 continuity 状态机：

~~~text
后续 Sync 产生合法 current Revision
  → S09 stable lineage / selected Aha
  → S10 current active Aha media projection
  → current AhaFacts / Claim Ledger
  → C3a applicability + contract gate
  → D4d1 exact-retain gate
      ├─ pass                         → C3a TEXT_RETAIN
      ├─ material change confirmed    → D4d2 区分 TEXT_PATCH / TEXT_REBUILD
      ├─ original peak unsupported    → C3a TEXT_BLOCK
      └─ contract invalid             → C3a Contract Invalid
  → 对需要新文字的路径进入 C3b2/C3b3/B3/D4/E
  → S12 final publish validation
~~~

D4d 不重新选择 Aha、`core_peak_event_ref`、Aha media、Chapter 归属或全天数量；也不读取新 Raw/HQ、不请求补帧、不重新跑视觉理解。它只消费上游已经合法形成的 current Revision 结果。

### 63.2 D4d 的拆分

为避免把“能不能改”和“具体怎么改”混在一起，D4d 分三步：

1. `D4d1 Exact Retain & Material Change Entry`：确认何时必须原样保留，何时才有资格进入改写；
2. `D4d2 Minimal Patch vs Sentence Rebuild`：对已确认的材料变化，区分最小 span 修补与整句重建；
3. `D4d3 Continuity Artifact & Lifecycle Closeout`：确认 Preview／Final baseline、immutable record、Block/Hold 与成本边界。

本轮只讨论 D4d1。D4d2 未确认前，`material change`只代表“允许进入变化判断”，不提前决定应改几个字或重写整句。

## 64. S11-D4d1｜Exact Retain & Material Change Entry

**状态：CONFIRMED / FROZEN**

### 64.1 本检查点只回答一个问题

当用户后续再次 Sync，新素材形成了 current Revision，而同一 Aha 已经向用户展示过一句 Moment Line：

> 旧句是否仍应一字不改地保留，还是已经出现足够重要的事实／媒体变化，允许进入 D4d2？

D4d1 不比较哪句“更好听”，也不生成新句；它是 Writer 之前的 deterministic gate。

### 64.2 术语释义

#### Prior user-visible baseline｜上一条已发布且用户可访问的基线文案

指同一 `stable_memory_id` 下，属于当前 published head、最近一次成功发布且用户可以访问、provenance 为 `GENERATED` 的 Preview 或 Final Moment Line。这里按“用户可能已经看过”保护连续性，不要求 telemetry 证明用户真的打开过；未发布的内部草稿、模型候选与失败 draft 都不算 baseline。该解释由 D4d3 68.2／68.3 与 S09 published-baseline 合同完成后置对齐。

#### Exact retain｜原样保留

指继续使用用户上次看到的完整字符串，包括原词序和标点；不能生成一句意思相近的新句来冒充保留。

#### Current-equivalent Claim mapping｜当前版本的等价事实映射

新 Revision 会产生新的 Claim refs，所以“原样保留”不要求继续引用旧 ref；它要求旧句中的每个事实 span，都能映射到 current Revision 中语义等价、仍有 Evidence 和 surface permission 的 Claim。文字可以完全相同，但验证引用必须更新到当前版本。

例如旧句“猫咪跃上桌，碰倒了纸杯。”在新 Revision 中仍由当前 Claims 支持，就可以原样展示；系统不能只复制字符串、却继续挂着已经过期的 Claim refs。

#### Material change｜材料变化

不是“多了新信息”，而是：如果继续保留旧句，它会变得错误、明显误导、不再能独立理解，或与当前展示媒体不兼容。只有达到这一程度，才允许打破用户已经建立的文字记忆。

### 64.3 D4d1 是从属 gate，不是第五套状态

内部可以保存以下 gate result，随后必须映射回 C3a 的既有合同：

| D4d1 gate result | 含义 | C3a／后续映射 |
|---|---|---|
| `NOT_APPLICABLE_NO_PRIOR` | 该 surface 没有已展示 generated baseline | `INITIAL_BUILD_REQUIRED` |
| `RETAIN_GATE_PASS` | 旧句在 current Revision 中仍完整合法 | `TEXT_RETAIN` |
| `RETAIN_GATE_FAIL_MATERIAL` | 至少一项材料变化成立，原 peak 仍合法 | 进入 D4d2，区分 `TEXT_PATCH / TEXT_REBUILD` |
| `RETAIN_GATE_FAIL_PEAK_UNSUPPORTED` | 原 selected peak 已无 current 支持 | `TEXT_BLOCK`；S11 不临场换 peak |
| `RETAIN_GATE_CONTRACT_INVALID` | lineage、ref、provenance 或 schema 损坏 | C3a Contract Invalid；不是内容 Block |

用户原文或用户编辑后的 Moment Line 不进入这张表，而是继续遵守 C3a 的 protected user surface 合同。若新的 Aha 使用了不同 `stable_memory_id`，旧 Aha 文案也不是它的 continuity baseline；新 Aha 走首次生成，旧 Aha 的生命周期由 S09 决定，D4d 不把两者强行拼成一次 patch。

### 64.4 `TEXT_RETAIN` 的八项合取门

只有以下八项全部通过，才映射为 `TEXT_RETAIN`：

1. 存在合法、已展示、provenance 为 `GENERATED` 的 prior Moment Line；
2. `stable_memory_id` 与 immutable lineage 连续，prior/current Revision refs 均可解析；
3. 原 Aha 的 durable peak identity 仍是 current selected peak；旧 ref 可以换成 current ref，但事件身份不能被 Writer偷换；
4. 旧句每个事实、对象、动作、关系和顺序 span 都能映射到 current-equivalent Claims；
5. 已写入的 qualifier 与 light-affect span 仍分别持有 current Evidence／permission；
6. current active Aha media 仍支持旧句实际写出的 peak 与细节；
7. 旧句在当前自己的 Aha card／media 下仍能独立理解，不依赖 parent Chapter 才成立；
8. 旧句仍符合当前 locale、长度、句法、标点及 surface policy，且没有任何材料变化测试通过。

八项通过后的行为固定为：

~~~text
reuse exact prior visible wording
+ rebuild current Claim/span/dependency mapping
+ run only required current compatibility / E revalidation
+ create a new immutable continuity artifact for current Revision
+ no D4 Writer call
~~~

因此，`TEXT_RETAIN`不是“把旧数据库记录原封不动搬过来”，而是“文字不变、当前证据映射和审计记录更新”。

### 64.5 只有五类原因可以打开变化入口

#### A. `FACT_OR_PERMISSION_CORRECTION`

旧句中的对象、动作、顺序、关系、限定词或 light-affect permission 已被 current Evidence 否定或撤销。事实正确性高于连续性。

#### B. `ACTIVE_MEDIA_MATERIAL_MISMATCH`

S10 合法更新 active media 后，旧句写出的动作／细节已不再被当前用户看到的素材支持。只丢失局部细节时进入 D4d2；原 peak 整体失去支持时直接 `TEXT_BLOCK`。

#### C. `STANDALONE_MATERIAL_CHANGE`

旧句过去可以独立理解，但 current projection／事实结构变化后，缺少一项必要 context 会造成材料性歧义。只是“加上背景会更丰富”不算。

#### D. `MATERIAL_MISREPRESENTATION_OR_NARROWING`

新事实证明旧句虽然字面未必全错，却已经过宽、会明显误导，或遗漏了理解该 peak 所必需的材料性限定。普通地点精确化、置信度上升或同类素材增加不自动满足本项。

#### E. `LEGAL_UPSTREAM_PEAK_IDENTITY_CHANGE`

只有 S09/S10 的合法新 Revision 与 lineage 明确改变 selected Aha peak，才允许进入 `TEXT_REBUILD`。D4d、Writer 或“更精彩”的新素材都不能自行换 peak。

### 64.6 明确不构成改写理由

以下变化只要没有同时触发 64.5，就必须原样保留：

1. 新增更多相似照片、相似角度或同一事件的更清晰素材；
2. 同一 peak 新增可选 before/after support，但旧句已经独立完整；
3. 新获得一个 observable qualifier 候选，例如`突然`、`缓缓`；
4. 新获得一个 light-affect permission，例如可把猫写成`调皮地`；
5. 新模型、新 Prompt、新词库或更高的内部文风分数；
6. Preview 变成 Final，但事实、选材、active media 与 permissions 没变；
7. Time Label、Tag 或 Display Label 独立更新；
8. 新地点名、新人物名或其他 exact fact 只是可选精确化，旧句并未因此失真或产生材料性歧义；
9. 为避免同一天几条文字“看起来重复”而改同义词或标点；
10. 旧句仍合法，只是系统现在认为可以写得更有情绪、更像日记。

### 64.7 案例检查

#### 案例 A｜古建筑又多了几个角度：原样保留

已展示：

> 木门打开，院里的古建筑映入眼前。

后续 Sync 又增加牌坊、屋檐和同一院落的两个清晰角度。它们让素材更丰富，但没有让旧句错误、失配或难以独立理解。

结果：`RETAIN_GATE_PASS → TEXT_RETAIN`。不能改成“穿过牌坊，古建筑铺展开来”来追求更漂亮。

#### 案例 B｜新增邻近反应：原样保留

已展示：

> 甜品切开，流心淌了出来。

后续素材又拍到同伴立刻笑了。旧句已经完整表达同一个 peak，“同伴笑了”只是可选 support。

结果：`TEXT_RETAIN`。不能因为新 support 可用，就把 Aha 自动扩成“切开甜品，流心淌出，大家都笑了”。

#### 案例 C｜新获得轻情绪许可：原样保留

已展示：

> 猫咪跃上桌，碰倒了纸杯。

新 Revision 允许使用共识性的`调皮`，但原句依然真实、自然、独立完整。

结果：`TEXT_RETAIN`。不能在后台 Sync 后悄悄改成“调皮的猫咪跃上桌……”。新 permission 是“可以用”，不是“必须改”。

#### 案例 D｜原有限定词失去证据：打开最小修订入口

已展示：

> 泥坯缓缓塌了下去。

current Evidence 只能确认泥坯塌下，已经不能支持速度限定`缓缓`。

结果：`RETAIN_GATE_FAIL_MATERIAL`。D4d1 只确认必须修；D4d2 再判断是否最小删除`缓缓`即可，不能借机把整句润色成另一种文风。

#### 案例 E｜只新增精确地点：通常原样保留

已展示：

> 古镇街口，木门缓缓打开。

后续可靠信息确认地点是周庄。如果当前只有这一段古镇 Aha，旧句仍明确且没有错误。

结果：`TEXT_RETAIN`。只有同日存在另一个容易混淆的古镇 Aha，且地点对独立理解确实必要时，才可能通过材料性歧义测试进入 D4d2。

#### 案例 F｜active media 只丢失局部细节：进入 D4d2

已展示：

> 甜品切开，金色流心淌了出来。

S10 合法切换后的 active media 仍清楚显示切开和流心，但颜色受光线影响，已不能可靠支持`金色`。

结果：`RETAIN_GATE_FAIL_MATERIAL`，原 peak 仍合法；D4d2 优先检查最小删除颜色 span，而不是重写整句。

#### 案例 G｜原 peak 在当前媒体中失去支持：Block，不换事件

已展示：

> 木门缓缓打开。

合法 active projection 更新后，current Aha media 只剩一张关闭木门的静态照片，current Claims 也不再支持“打开”这一 peak。

结果：`RETAIN_GATE_FAIL_PEAK_UNSUPPORTED → TEXT_BLOCK`。S11 不能顺手改写成“木门静静立在街边”，因为那已经换了 peak；是否产生合法新 peak 只能回到上游新 Revision。

#### 案例 H｜Preview 进入 Final：原样保留

Preview 已展示：

> 小船穿过桥洞，水面晃起波纹。

Finalization 没有改变事实、peak、active media 或 permissions。

结果：`TEXT_RETAIN`，包括原词序和标点；不能为了“Final 更正式”重新生成。

#### 案例 I｜上游依法改变 peak：重建入口

旧 Revision 的 selected peak 是“小船穿过桥洞”；后续 S09/S10 的合法 immutable Revision 明确把同一 stable Aha lineage 的 selected peak 改为“船靠岸”，并提供完整 current Claims 与 media。

结果：`LEGAL_UPSTREAM_PEAK_IDENTITY_CHANGE`成立，进入`TEXT_REBUILD`；这项变化只能来自上游，不是 D4 Writer 在两个画面中自行选择更精彩的一个。

### 64.8 成本与效率

1. D4d1 本身只比较 stable identity、current Claim 映射、permissions、active projection fingerprint 与 prior span refs，是确定性结构判断；
2. `TEXT_RETAIN`不调用 D4 Writer，只做必要的 current dependency／E revalidation，并为 current Revision保存新的 immutable continuity artifact；
3. 本步骤不增加抽帧、上传、HQ、VLM 或 Raw media 读取；
4. 一天多次 Sync 时，多数“新增相似素材但核心没变”的 Aha 会直接 retain，可同时降低文字 API 成本与用户看到文案反复变化的体验成本；
5. policy/model 版本变化本身不触发重写；只有新 policy 真的使旧 span 不合法，才按 permission change 进入 D4d2；
6. D4d1 不冻结 E verifier 是否使用模型、其缓存期限或 provider 价格；这些仍属于 E/D6，但不得借验证之名生成同义改写。

### 64.9 D4d1 Closeout Invariants

1. 已展示 generated Aha Moment Line 默认 exact retain，改变必须先通过材料变化门；
2. exact retain 保留完整 wording 与标点，同时重新绑定 current-equivalent Claims／dependencies，不能沿用过期 refs；
3. 新 Revision 的 Claim ref 变化本身不等于事实变化；判断依据是 durable peak identity 与 normalized proposition 是否仍等价；
4. 新增可选 support、qualifier、light-affect permission、相似素材或更好文风均不触发改写；
5. 事实／permission 失效、current active media 材料失配、独立理解所需 context 变化、材料性误导或合法上游 peak change，才打开变化入口；
6. 原 peak 失去支持时进入`TEXT_BLOCK`，S11 不换 peak、不补 Aha、不发布伪装成新 Revision 的旧句；
7. 不同`stable_memory_id`之间不继承文案 baseline；新 Memory 走首次生成，旧 Memory 走 S09 lifecycle；
8. prior baseline 只来自真正 user-visible 的 generated artifact；内部草稿和失败候选不参与 continuity；
9. D4d1 gate result 必须映射回 C3a，不能形成平行的用户可见状态机；
10. 本步骤不增加媒体计算，只让确有材料变化的少数 Revision 进入 D4d2／Writer 链。

### 64.10 已确认结论

当前中文测试版冻结：**一条已经展示过的 Aha Moment Line，只要仍然真实、独立可懂、与 current active media 相符且符合当前文字合同，就必须连词序和标点一起原样保留；后来新增的可选 support、qualifier、light-affect permission 或“更好听”的表达，都不能触发后台改写。文字 retain 时仍要重建 current Claim/span/dependency 映射，不得沿用过期 refs。只有 64.5 的材料变化才允许进入 D4d2；原 peak 失去支持时直接 Block，不由 S11 换 peak。**

### 64.11 冻结记录

**冻结日期：** 2026-08-28

**用户确认：** 确认 D4d1 的 exact-retain 默认值、材料变化入口、current-equivalent Claim mapping、原 peak unsupported 时 Block，以及新增可选内容不触发后台改写。

**冻结范围：** 64.1–64.10 的适用问题、术语、从属 gate results、八项 retain 门、五类材料变化、非触发项、案例、成本边界与十项 Closeout Invariants。

**不在冻结范围：** D4d2 patch/rebuild 精确边界、D4d3 lifecycle closeout、D4e localization、D6 provider／模型／Prompt／candidate／transport retry／day-level cost、E actual wording verification、App fallback、海外 locale、Production infrastructure 以及整个 D4／S11。

**变更规则：** 只有真实用户测试显示文字稳定性或事实纠错体验存在反证，或新的显式 versioned checkpoint，才可修订；不得由模型升级、文风分数、重复 Sync 或新可选素材静默改写。

**后置合同对齐（D4d3 cross-check）：** 64.2 的`user-visible baseline`按 S09 统一解释为“已成功发布且用户可访问”，不要求实际打开 telemetry。该修正扩大连续性保护，不改变 exact-retain、材料变化或 current-equivalent Claim mapping 的冻结原则。

## 65. D4d1 → D4d2 Transition

D4d1 已冻结“什么时候才允许改”。现在进入 D4d2，只讨论已经通过材料变化门以后，应做最小修补还是重新规划整句。D4d2 不重新打开 exact-retain 门，也不新增 Aha、素材或 peak。

## 66. S11-D4d2｜Minimal Patch vs Sentence Rebuild

**状态：CONFIRMED / FROZEN**

### 66.1 本检查点的问题与边界

D4d2 只消费 D4d1 的`RETAIN_GATE_FAIL_MATERIAL`，并回答：

> 旧句的核心事件仍是同一件事，只需修复受影响部分；还是旧句的事件结构已经不再成立，必须按 current Facts 重建整句？

D4d2 不处理`RETAIN_GATE_PASS`，不把`TEXT_BLOCK`救回，不修改上游 selected peak，也不亲自生成 wording。它只建立 immutable change plan，并把任务交给正确 owner 与 D4/E。

### 66.2 术语释义

#### Span｜文字片段

指一句话中能单独映射到某个 Claim、relation、qualifier、light-affect permission 或语法连接作用的连续文字。例如“缓缓”“金色”“同伴笑了”和连接词“后”都可以是不同 span。

#### Semantic slot｜语义位置

不是固定字符位置，而是句子承担的一项意义角色，例如：

~~~text
必要 context｜拉坯时
核心主体    ｜泥坯
核心动作    ｜塌下
可观察限定  ｜缓缓
邻近支持    ｜师傅伸手扶住
轻情绪语气  ｜调皮地
~~~

#### Semantic skeleton｜语义骨架

Aha Moment Line 的核心事件结构：**主要是谁／什么对象，发生了什么 peak 动作或可见变化，作用于什么核心对象或产生什么核心结果。** Context、support、qualifier 与 light affect 可以附着在骨架上，但不能冒充骨架。

#### Stable core anchor｜稳定核心锚点

旧句中仍被 current Claims、permissions 与 active media 支持，并直接表达同一 selected peak 的核心文字。它是 patch 时优先原样保护的部分。

#### Rebuild｜重建

不是要求故意把每个词都换掉，而是表示旧 Content Plan 的核心结构已不能安全沿用，必须用 current Facts 重新经过 owner planning、B3、D4 和 E。新句可以自然复用仍合法的旧词，但不能为了表面连续而被旧句结构绑住。

### 66.3 不用字符比例决定 PATCH 或 REBUILD

D4d2 不采用“改动不超过 20%”“最多改 3 个字”等门槛，原因是中文 Moment Line 很短：

- `猫咪 → 小狗`可能只改两个字，却改变了核心主体；
- 同时删除`调皮地`和`同伴笑了`可能改很多字，但核心事件“猫咪跃上桌、碰倒纸杯”完全没变。

因此，字符 diff、变更字数和编辑距离只进入 audit，不拥有决策权。决策只看 semantic skeleton、Claim/role 结构和用户对“是否还是同一个瞬间”的理解。

### 66.4 三种内部 realization mode

D4d2 可以记录三种 realization mode，但它们必须映射回 C3a 的两种既有结果，不形成新的用户可见状态：

| realization mode | C3a decision | 含义 |
|---|---|---|
| `MINIMAL_SPAN_PATCH` | `TEXT_PATCH` | 只删除、替换或增加可定位的必要 span；其余合法 wording 原样保护 |
| `CONSTRAINED_SENTENCE_PATCH` | `TEXT_PATCH` | semantic skeleton 不变，但局部删除后句法断裂，需要连同最小语法桥、语序或语态一起修复 |
| `FULL_SENTENCE_REBUILD` | `TEXT_REBUILD` | peak identity 或核心 Claim/relation/plan 结构改变，旧句不再是安全骨架 |

`CONSTRAINED_SENTENCE_PATCH`仍然是 patch：它不能增加新事件、新可选细节或新情绪，只允许为同一 current plan 恢复自然中文。`FULL_SENTENCE_REBUILD`也不等于“必须写得完全不同”；它表示必须重新验证整个句子的内容计划。

### 66.5 `TEXT_PATCH` 的八项合取门

只有以下八项全部满足，D4d2 才能选择某种 patch：

1. prior/current 属于同一`stable_memory_id`和合法 lineage；
2. durable peak identity 未变，核心主体、核心动作、核心作用对象／结果仍指向同一事件；
3. 旧句至少存在一个 current-valid 的 stable core anchor；
4. 失效或新必要内容能定位到明确 semantic slots，而不是整条 core Claim graph；
5. 不需要新增第二事件、改变先后／因果／反应关系、扩大时间范围或借用 parent Chapter；
6. 未受影响的事实 span 仍有 current-equivalent Claims 且与 active media 相容；
7. 删除／更正后能在 D4a–D4c 合同内形成自然、独立可懂的一句；
8. 新加入的内容只能是恢复真实性或 standalone correctness 所必需的 current Claim，不能用新的可选内容填补被删位置。

八项中任一项失败，且 current Revision 仍有合法 selected peak 时，进入`FULL_SENTENCE_REBUILD → TEXT_REBUILD`；原 peak 已无支持则保持 D4d1 的`TEXT_BLOCK`，不能通过 rebuild 换事件。

### 66.6 Patch 的固定最小化顺序

对同一 current Revision，patch 必须按以下顺序建立，不能先让 Writer自由重写：

1. **删除失效的可选 span：** 先删除 qualifier、light affect、非必要 support 或非必要 detail；
2. **保护稳定核心：** current-valid 的 core wording 与未受影响 span 默认 exact retained；
3. **必要时更正局部事实：** 只有删除后仍会错误或明显误导，才用 current verified Claim 替换；
4. **必要时增加最小 context：** 只有 D4d1 已证明旧句不再 standalone，才增加一组由 C3b2 证明必要的 context；
5. **修复最小语法桥：** 局部修改留下悬空的`后／才／便／的／被`、错误标点或语序时，只修复使句子自然所需的相邻部分；
6. **立即停止：** 新句一旦恢复真实、自然、独立可懂就停止，不加入新的 optional support、qualifier、light affect 或“更有画面”的同义表达。

这里的默认策略是“删除旧的无效可选内容”，不是“找一项新的可选内容替上”。例如原`缓缓`失效，即使 current Claims 另有`突然`候选，也先删除`缓缓`，不能自动换成`突然`。

### 66.7 必须 `TEXT_REBUILD` 的条件

出现下列任一情况，不能以“只改几个字”为由做 patch：

1. 合法上游 Revision 改变 selected peak identity；
2. 核心主体／主要对象身份改变，例如猫变成狗、妈妈变成朋友，而该身份属于 peak core；
3. 核心动作、状态变化、作用对象或核心结果改变；
4. 先后、同时、触发、反应或其他核心 relation graph 改变；
5. 必要 context 的纠正同时改变用户对事件类型的理解，例如原本判断为拉坯，后来证明是揉面；
6. 旧句已经没有可安全保留的 stable core anchor；
7. 强行保护旧语序会让新句错误、明显误导、依赖 Chapter 才懂，或必须偷偷加入未验证 Claim；
8. current Content Plan 的 core/group 结构需要重新选择，而不是只删除失效 optional node；
9. patch 表面上只换少数字，但实际把用户看到的“这一瞬间是什么”改成了另一件事。

同时失效多个 span 不自动等于 rebuild：如果失效的都只是可删除 optional spans，且同一 stable core anchor 完整保留，仍可做一次有界 patch。

### 66.8 Owner routing 与 D4c2 attempt envelope

D4d2 不允许 Writer直接修改 plan；路由固定为：

~~~text
TEXT_PATCH, only wording / grammar bridge changes
  + prior Content Plan and current-equivalent Claims still valid
    → bounded D4 patch realization → E

TEXT_PATCH, qualifier changes only
    → C3b3 qualifier decision → B3 → D4 → E

TEXT_PATCH, light-affect permission changes only
    → C3b3 light-affect decision → B3 → D4 → E

TEXT_PATCH, base Claim / context / support / relation changes
    → C3b2 base replan → C3b3 decisions → B3 → D4 → E

TEXT_REBUILD
    → current C3b2 full base plan → C3b3 decisions → B3 → D4 → E

original peak unsupported
    → TEXT_BLOCK; no D4 Writer
~~~

所有 patch/rebuild 路径共用该 Moment Line 当前 Revision 的 D4c2 semantic attempt envelope。`MINIMAL_SPAN_PATCH`或`CONSTRAINED_SENTENCE_PATCH`不是额外的第五次机会；其 current exact plan 的首次实现仍计作`INITIAL_EXACT_PLAN`，E 回流也不能重置预算。

### 66.9 案例检查

#### 案例 A｜删除失效 qualifier：最小 span patch

旧句：

> 泥坯缓缓塌了下去。

`缓缓`失去 Evidence，其他 core Claims 不变：

> 泥坯塌了下去。

结果：`MINIMAL_SPAN_PATCH → TEXT_PATCH`。只删除`缓缓`，不改成“泥坯一下子垮了”。

#### 案例 B｜删除失效 light affect：最小 span patch

旧句：

> 调皮的猫咪跃上桌，碰倒纸杯。

light-affect permission 被撤销，但同一 peak 仍完整：

> 猫咪跃上桌，碰倒纸杯。

结果：`MINIMAL_SPAN_PATCH`。不能用`活泼的`补位，也不能重写其余事实 wording。

#### 案例 C｜颜色细节失去支持：优先删除，不找近义替代

旧句：

> 甜品切开，金色流心淌了出来。

active media 仍支持切开和流心，但不再可靠支持`金色`：

> 甜品切开，流心淌了出来。

结果：`MINIMAL_SPAN_PATCH`。即使模型认为`浓郁流心`更好听，也不能把一个失效细节替换成新的可选形容。

#### 案例 D｜邻近 support 失效：删除 support，不换另一条反应

旧句：

> 甜品切开，流心淌出，同伴笑了。

current Evidence 不再支持`同伴笑了`，但 peak 自身已经独立完整：

> 甜品切开，流心淌出。

结果：`TEXT_PATCH`。C3b2 删除失效 support；原 core wording 已经自然，因此继续 exact 保留`甜品切开，流心淌出`。即使另有“同伴竖起拇指”候选，也不自动替换。

#### 案例 E｜删除内容后留下语法连接词：允许最小语法桥修复

旧句：

> 猫咪跃上桌后，碰倒了纸杯。

current Evidence 仍支持“跃上桌”，但不再支持“碰倒纸杯”。直接只删后半句会留下“猫咪跃上桌后。”，因此连同失去作用的`后`一起删除：

> 猫咪跃上桌。

结果：仍是`MINIMAL_SPAN_PATCH`；`后`属于 grammatical bridge，不是新的事实。

#### 案例 F｜真实 surface policy 变化要求调整语态：受限整句 patch

旧句：

> 纸杯被猫咪碰倒了。

current Facts、peak 与 active media 均未改变，但一个经过正式版本化的新中文 surface policy 明确不再允许该位置使用被动句；这是真实 policy incompatibility，不是“主动句更好听”的偏好。为满足 current contract，必须调整语态和语序：

> 猫咪碰倒了纸杯。

结果：`CONSTRAINED_SENTENCE_PATCH → TEXT_PATCH`。虽然语序变化较大，但主体、动作、对象和 Content Plan 完全相同；不得顺便加入`调皮地`或其他反应。若只是新模型偏爱主动句、旧句仍符合 current policy，则 D4d1 应当`TEXT_RETAIN`，不能进入本案例。

#### 案例 G｜新增 context 只是为了恢复独立理解：patch

旧句：

> 木门打开了。

合法 active projection 变化后，卡片中同时出现多个门，旧句会产生材料性歧义；current C3b2 证明`牌坊旁`是唯一必要 context：

> 牌坊旁，木门打开了。

结果：`MINIMAL_SPAN_PATCH`。若没有真实歧义，只是“牌坊旁”更有画面，则 D4d1 本应 retain，不能到本步添加。

#### 案例 H｜只改两个字，却换了核心主体：必须 rebuild

旧句：

> 猫咪跃上桌，碰倒了纸杯。

current verified Facts 证明核心主体其实是小狗。可见文字表面只需把`猫咪`换成`小狗`，但用户理解的事件主体已经改变。

结果：`FULL_SENTENCE_REBUILD → TEXT_REBUILD`。系统必须重新验证 referent、动作 attachment、active media 与整句 plan；重建后的句子可以保留仍合法的“跃上桌，碰倒了纸杯”，但不能把它当作无语义影响的两字 patch。

#### 案例 I｜两个 optional spans 同时失效，core 未变：仍可 patch

旧句：

> 猫咪调皮地跃上桌，碰倒纸杯，同伴笑了。

`调皮地` permission 与`同伴笑了` support 同时失效，但“猫咪跃上桌、碰倒纸杯”仍是同一完整 peak：

> 猫咪跃上桌，碰倒纸杯。

结果：仍可`TEXT_PATCH`。删除字符较多不等于 rebuild，因为 semantic skeleton 和 stable core anchor 没变。

#### 案例 J｜事件类型发生变化：rebuild

旧句：

> 拉坯时，泥坯塌了下去。

后续 verified Facts 证明画面并非拉坯，而是在揉面；这不是换一个地点词，而是改变用户对动作类型与对象的整体理解。

结果：`TEXT_REBUILD`。不能只把`拉坯`替换成`揉面`后沿用旧 Claim graph。

#### 案例 K｜原 peak 已无支持：不是 rebuild，而是 Block

旧句：

> 木门缓缓打开。

current Claims 已不支持“打开”，但有另一张漂亮的静态门照片。

结果：`TEXT_BLOCK`。`FULL_SENTENCE_REBUILD`不能成为“换一个事件继续写”的后门。

### 66.10 Change plan 最小输出

D4d2 至少形成以下 immutable plan；完整跨 Revision lifecycle artifact 留到 D4d3：

~~~text
AhaMomentLineChangePlan
  stable_memory_id
  prior_revision_ref
  current_revision_ref
  prior_moment_line_artifact_ref
  d4d1_material_change_ref
  c3a_decision
    TEXT_PATCH | TEXT_REBUILD
  realization_mode
    MINIMAL_SPAN_PATCH
    | CONSTRAINED_SENTENCE_PATCH
    | FULL_SENTENCE_REBUILD
  prior_core_peak_identity_ref
  current_core_peak_identity_ref
  stable_core_anchor_span_refs[]
  invalidated_span_refs[]
  protected_retained_span_refs[]
  allowed_edit_span_refs[]
  grammatical_bridge_edit_refs[]
  necessary_addition_claim_refs[]
  forbidden_optional_replacement_refs[]
  current_content_plan_ref
  owner_route
  b3_revalidation_required
  d4c2_attempt_envelope_ref
  reason_codes[]
  change_plan_fingerprint
~~~

`protected_retained_span_refs[]`不是让 Writer把旧字符串硬拼到错误句法中；若最小语法修复确实需要触碰相邻 span，必须在`grammatical_bridge_edit_refs[]`中明确说明。任何未列入 allowed/bridge 的改动都由 E 判为越界。

### 66.11 成本、效率与产品体验

1. PATCH/REBUILD 判定只比较 current Claim graph、role、span map 与 active projection，不增加视觉模型、上传、HQ 或 Raw 读取；
2. 最常见的 permission/detail 失效走短 edit instruction，token 与文字抖动均小于自由重写；
3. `CONSTRAINED_SENTENCE_PATCH`可能仍需要一次完整句输出，但输入空间被 current exact plan 与 allowed edits 严格限制；
4. `TEXT_REBUILD`成本高于 patch，但只在核心语义变化时发生，并继续受 D4c2 每 Revision 最多四类 canonical draft 约束；
5. 删除旧 optional span 后不自动寻找新 optional replacement，可减少 C3b2/C3b3 搜索、Writer tokens 与用户感知上的“系统总在改文案”；
6. D4d2 不冻结 provider、模型、Prompt、token 数字或具体价格；这些在 D6 统一建立 day-level budget 和 benchmark。

### 66.12 D4d2 Closeout Invariants

1. PATCH/REBUILD 按 semantic skeleton 与 Claim/role 结构判断，不按改动字符数、比例或编辑距离判断；
2. 核心主体、动作、作用对象／结果与 durable peak identity 均未改变，且存在 current-valid stable core anchor，才有 patch 资格；
3. patch 默认 exact 保护未受影响 wording，只开放 invalidated／necessary span 与最小 grammatical bridge；
4. 失效 optional content 默认删除，不以新的 qualifier、light affect、support、detail 或漂亮同义词补位；
5. 新增内容只允许恢复 truth、active-media compatibility 或 standalone correctness，并必须来自 current verified Claim 与正确 owner；
6. 局部编辑导致句法断裂时可做`CONSTRAINED_SENTENCE_PATCH`，但 semantic skeleton 不得改变，也不得借机润色整句；
7. 核心主体／动作／对象／结果、relation graph、事件类型或合法 selected peak 改变时必须`TEXT_REBUILD`，即使表面只改少数字；
8. 多个 optional spans 同时删除不自动升级为 rebuild，只要 stable core anchor 与 current plan 骨架仍完整；
9. qualifier／light affect／base Claim-context-support 分别回 C3b3／C3b3／C3b2 owner，Writer不直接改 plan；
10. 所有 patch/rebuild 共用 current Revision 的 D4c2 attempt envelope，不因 realization mode 新增 retry；
11. original peak unsupported 保持`TEXT_BLOCK`，rebuild 不能换 peak、补位或恢复另一事件；
12. D4d2 只输出 immutable change plan；E 必须验证真实输出没有越过 allowed edits、引入新 Claim 或改写 protected spans。

### 66.13 已确认结论

当前中文测试版冻结：**PATCH/REBUILD 不按字符差异判断，而按用户看到的是否仍是同一瞬间以及 semantic skeleton 是否仍成立。删除失效 qualifier、light affect、detail 或 support 属于 patch；多个 optional spans 同时删除也不自动升级为 rebuild。核心主体／动作／对象／结果、relation graph、事件类型或合法 selected peak 改变时必须 rebuild，即使表面只改少数字。局部删除造成句法断裂时可以做受限整句 patch，但不能加入任何新的可选内容。**

### 66.14 冻结记录

**冻结日期：** 2026-08-28

**用户确认：** 确认以 semantic skeleton 而非字符差异区分 patch/rebuild，失效 optional content 默认删除、不补位，语法桥可受限修复，核心身份／动作／关系变化必须 rebuild，以及所有路径共用 D4c2 attempt envelope。

**冻结范围：** 66.1–66.13 的术语、semantic 判定、三种内部 realization mode、八项 patch 门、最小化顺序、rebuild 条件、owner routing、案例、change plan、成本边界与十二项 Closeout Invariants。

**不在冻结范围：** D4d3 baseline／Preview-Final／publish lifecycle／fallback、D4e localization、D6 provider／模型／Prompt／candidate／transport retry／day-level cost、E actual wording verification、App fallback 具体视觉形态、海外 locale、Production infrastructure 以及整个 D4／S11。

**变更规则：** 只有真实 patch/rebuild 错分样本、用户测试反证或新的显式 versioned checkpoint 才可修订；不得用字符百分比、模型偏好或工程方便静默改变语义边界。

## 67. D4d2 → D4d3 Transition

D4d2 已冻结“允许改时应最小修补还是重建”。现在进入 D4d3，收口哪个已发布版本是 baseline、计算期间显示什么、何时原子替换、失败后能否继续显示 prior、Preview／Final 状态与并发 Revision 顺序。D4d3 不重新决定文案内容。

## 68. S11-D4d3｜Published Baseline, Atomic Visibility & Lifecycle Closeout

**状态：CONFIRMED / FROZEN / TWO-PHASE ARTIFACT ALIGNMENT APPLIED**

### 68.1 本检查点在全链路中的位置

D4d3 位于 D4d1/D4d2 与 S12 发布之间：

~~~text
last successfully published Daily Memory Revision
  + current S09/S10 Revision
  + D4d1 retain/material decision
  + D4d2 patch/rebuild change plan when applicable
  + current B3/D4/E results
        ↓
D4d3 lifecycle / publication-head decision
        ↓
S12 final publish validation
        ↓
atomic visible-head switch or hold existing head
~~~

D4d3 不拥有 S09 membership／lineage、S10 media、D4 wording 或 S12 最终发布权；不增加上传、不调用模型，也不规定 App 卡片的具体 loading 动效。它只定义算法与发布编排必须遵守的版本语义。

### 68.2 术语释义

#### Published head｜当前已发布版本头

用户此刻可以访问到的最新一套完整 Daily Memory Revision。它是一个完整快照，不是“最新算到哪就拼到哪”的零散结果。

#### User-visible baseline｜用户可见基线

指同一 stable Memory lineage 中，属于 published head、已经成功发布且用户可以访问的最新 generated surface artifact。它不要求通过 telemetry 证明用户真的点开过；只要已发布并可访问，就应按用户可能已经看过来保护连续性。

内部 draft、发布失败的 Revision、stale worker 结果和只写入数据库但未切换 published head 的 artifact 都不是 baseline。

#### Atomic publish｜原子发布

当前完整 Revision 只有两种外显结果：要么仍不可见，要么一次性成为新的 published head。不能先换 media、后补文字，也不能只发布三个成功 Aha 中的两个。

#### Hold previous｜保持上一版

当前 Revision 计算中、失败或不具备 publish readiness 时，继续服务原 published head；不是把旧 refs 复制到 current Revision，也不是宣称当前处理成功。

#### Compare-and-swap / CAS｜带前置版本核对的原子切换

发布 current Revision 前必须核对：它开始规划时所依赖的`expected_published_head_ref`仍是现在的 published head。若另一较新 Revision 已经先发布，旧任务不能覆盖它，必须重新对齐或作废。

### 68.3 Baseline 的确定顺序

每次 current Revision 只允许选择一个 baseline：

1. 读取当前 Daily Memory 的`published_head_revision_ref`；
2. 在该完整 published head 中，按`stable_memory_id`与合法 lineage 找到最近的 generated Moment Line artifact；
3. 确认 artifact 当时确已成功发布，且未被正式 withdraw／merge-away／supersede／invalidate；
4. 若该 Memory 在 published head 中没有 prior generated Moment Line，则走`INITIAL_BUILD_REQUIRED`，不能回头搜索更老历史版本凑 baseline；
5. 若最新 published head 中的对应 artifact 已正式失效，也不能跳过它、自动复活 R1/R2 等更老 wording；任何历史恢复必须形成显式 current Revision。

因此，baseline 是“当前 published head 的合法祖先”，不是“历史上分数最高的一句”或“最近一个成功的内部草稿”。

### 68.4 Preview 与 Final 的基线规则

1. 没有 Final 时，最新成功发布的 Preview 可以成为下一次 Sync 的 baseline；
2. Preview→Final 只要 Facts、peak、active media 与 text permissions 不变，Moment Line 继续 exact retain；Final publication 可以更新 lifecycle/ref，但不能为了“更正式”改 wording；
3. Final 只有经过当前完整链路与 S12 后才能成为`FINAL_PUBLISHED` baseline；
4. Final 失败时，合法 prior Preview 可以继续显示，但必须保持`PREVIEW_PUBLISHED`身份，不能被改名或暗示为 Final；
5. 已有 Final published head 后，普通同日 Preview 不能反向覆盖或降级它；后续事实纠错若必须改变 Final，必须由 S09/S12 批准显式、versioned correction Revision，不能伪装成普通 Preview；
6. Preview/Final 只是 lifecycle 状态，不改变 D4d1/D4d2 的真实性、retain、patch、rebuild 与 Block 门。

具体 App 是否显示“预览版／最终版”标签仍是 presentation 设计；算法必须保留真实状态，不能让 UI 只能通过猜测判断。

### 68.5 计算期间与成功发布时的产品行为

#### 当前 Revision 仍在计算

- 原 published head 保持完整可见；
- 不先清空旧文案，不展示半成品，不把内部 draft 暴露给用户；
- 不要求用户再次点击上传或确认；后台 Sync／计算状态与 Memory 内容分离。

#### 当前 Revision 全链路成功

只有同时满足以下条件才可请求 S12 发布：

1. S09/S10 current selected set、lineage 与 media projection ready；
2. 所有 required generated/deterministic surfaces 已完成或按明确合同合法省略；
3. D4d1/D4d2、B3、D4、E refs 均属于同一 current Revision/fingerprint；
4. current Aha text 与 current Aha media 已共同验证，未混用 prior/current refs；
5. S12 全量通过；
6. 发布瞬间 CAS 仍证明`expected_published_head_ref == actual_published_head_ref`。

通过后才执行一次 atomic head switch。即使 Moment Line 文字因`TEXT_RETAIN`完全相同，只要 current Revision 的 media、Claims、lineage 或 lifecycle 更新，新 artifact 仍要保存 current refs，并在整版发布后成为下一 baseline。

### 68.6 失败与 fallback 的确定性分流

~~~text
current Revision not ready / blocked / contract invalid
  ├─ eligible prior published head exists
  │    → HOLD_LAST_PUBLISHED_VALID
  │       keep the entire prior head with its original refs/state
  └─ no eligible prior published head
       → BLOCKED_NO_PUBLISHABLE_REVISION
          publish no partial/current placeholder result
~~~

Prior fallback 的 eligibility 固定为：

1. prior 确实是 last successfully published head，而不是内部结果；
2. prior 的完整 text/media artifact 与 storage handles 仍可服务；
3. 没有 current authoritative Evidence 证明 prior 可见事实、peak、identity 或 media 已错误／失效；
4. 没有正式 withdrawal、merge-away、supersede、retention expiry 或不可兼容 migration；
5. 普通 current uncertainty、worker error、search limit 或 lineage unresolved 本身不等于 prior 失效，继续继承 S09`HOLD_PREVIOUS_REVISION`；
6. policy/model 版本变化本身不追溯性使 prior 失效，除非正式 migration 明确判定其 unsafe／illegal。

若 prior 已被 current authoritative Evidence 明确证明错误或失效，它就不是合法 fallback。D4d3 返回“没有安全 prior”，映射 S09/S12 的`BLOCKED_NO_PUBLISHABLE_REVISION`／上游 correction-withdrawal 路径；不能为了界面不断档继续展示已知错误文字，也不能自动回滚到更老历史版本。

本节只冻结算法的 serving eligibility：**已知错误 prior 不再是合法 active fallback。** App 最终选择隐藏受影响内容、显示中性“更新中”状态还是其他不陈述事实的 presentation，仍需后续 App/S12 UX 合同；S11 不生成万能占位句。

### 68.7 整版原子性与禁止 hybrid Revision

以下组合全部禁止：

1. current media + prior text，但未建立 current-equivalent Claim mapping 与 current E validation；
2. prior media + current text；
3. current 三个 Aha 中两个成功就先发布两个；
4. current Chapter/Aha membership 已变，却只更新部分 narrative；
5. 将 prior Preview 文字复制到 current Final artifact、但不保留真实 lineage；
6. current required Moment Line Block 后发布空字符串、固定占位、media-only Aha 或临时较小子集；
7. 在 current Revision 失败时把 prior artifact 的 ref 改名成 current ref。

`TEXT_RETAIN`不是 hybrid：它要求 exact wording 复用，同时建立 current Claim/span/dependency mapping，并与 current media 在 current Revision 中共同过验；只有整版发布后才成为 current artifact。

### 68.8 并发 Sync 与乱序完成保护

同一天可能出现 R2、R3 同时计算，D4d3 冻结以下顺序：

1. 每个 current Revision 保存`expected_published_head_ref`与单调`revision_sequence`；
2. Revision 计算完成不等于可以发布，S12/CAS 必须在最后一刻核对 published head；
3. 若 R2 先于 R3 完成，且 head 仍是 R1，R2 可以依法发布；R3 在发布前必须以新 head R2 重新做 continuity applicability／dependency revalidation，不能继续拿 R1 当 baseline；
4. 若 R3 已先发布，迟到的 R2 必须进入`STALE_PUBLICATION_ATTEMPT`并停止，不能把用户版本倒退；
5. stale 结果可以保留 audit，但不能成为 baseline、不能补写 current refs，也不能重置 D4c2 attempt budget；
6. 工程层未来可做 debounce/coalescing 减少频繁 Revision，但不能通过合并任务绕过 material-change、lineage 或原子发布检查。

`STALE_PUBLICATION_ATTEMPT`是工程发布结果，不是第五种 C3a 内容状态。

### 68.9 案例检查

#### 案例 A｜R2 正在后台计算：继续显示 R1

12:00，R1 Preview 已成功发布“猫咪跃上桌，碰倒纸杯。”；14:00 用户再次 Sync，R2 开始处理。

R2 在 S09–E 任一阶段仍未完成时，App 继续服务完整 R1。不能先把 Aha 卡片清空，也不显示 Writer 草稿。R2 全部通过后才一次切换。

#### 案例 B｜新增相似素材且没有材料变化：不制造可见新版本

R2 只增加同一猫咪事件的相似角度，S09 selection／scope／state／lineage 与全部 downstream fingerprints 均无变化。

结果：S09`NO_CHANGE_REUSE`，published head 仍是 R1；内部 audit 可记录本次计算，但不创建用户感知不到的新发布 Revision，也不调用 Writer。

#### 案例 C｜Patch 成功：整版原子替换

R1：

> 泥坯缓缓塌了下去。

R2 证明`缓缓`失效，D4d2 形成最小 patch：

> 泥坯塌了下去。

在 R2 的 current text、current media、其他 required surfaces 与 S12 全部通过前，用户仍看完整 R1；通过后整版切到 R2，R2 artifact 成为下一 baseline。中间不存在空卡片或“新媒体＋旧文字”的半版本。

#### 案例 D｜三个 Aha 中一个失败：不发布成功的两个

R2 同时处理三个 Aha，其中两个 E 通过，一个 required Moment Line Block。

结果：current R2 整体不发布。若 R1 仍合法，继续显示完整 R1；不能先发布两个新 Aha，也不能用空文案保留第三张卡。

#### 案例 E｜Final 失败：旧 Preview 仍只是 Preview

R1 是成功发布的 Preview；当天 Final R2 因一个 required surface 无法验证而 Block。

结果：R1 可以继续显示，但其状态仍为`PREVIEW_PUBLISHED`。系统不能因为到了晚上就把 R1 标为 Final，也不能把失败 R2 的 Final ref 指向 R1。

#### 案例 F｜首次生成失败且没有 prior

当天第一次产出 Aha，Moment Line 最低合法内容仍无法生成。

结果：`BLOCKED_NO_PUBLISHABLE_REVISION`。不发布 media-only Aha、“精彩瞬间”占位句或残缺 Daily Memory Revision。

#### 案例 G｜prior 已被证明错误：不能为不断档继续显示

R1 写：

> 猫咪跃上桌，碰倒纸杯。

current authoritative Evidence 证明核心主体是小狗，但 R2 重建暂时失败。R1 的核心可见事实已经失效，因此不再具备 fallback eligibility。

结果：算法返回无安全 prior，并进入上游 correction/withdrawal + S12/App presentation 路径；不能继续把 R1 当成“上一版仍有效”，也不能自动复活更老 R0。具体隐藏或中性更新状态留给 UX 合同。

#### 案例 H｜R3 先发布，迟到的 R2 不得覆盖

R2 与 R3 都从 R1 开始计算，但 R3 先完成并合法发布。R2 随后完成时发现`expected_head=R1`、`actual_head=R3`。

结果：R2 为`STALE_PUBLICATION_ATTEMPT`，不发布。它不能因为开始得更早就把用户从 R3 倒退回 R2。

#### 案例 I｜文字 retain、media/current refs 更新：仍要形成 current artifact

R2 合法更换了更清晰但语义等价的 active media，旧句仍完全支持：

> 小船穿过桥洞，水面晃起波纹。

D4d1 为`TEXT_RETAIN`，D4 Writer不运行；但 R2 仍建立 current Claim/span/dependency mapping，并把同一句与 current media 共同过验。整版发布后 R2 成为 baseline，而不是把 R1 text ref 混入 R2。

#### 案例 J｜Preview→Final 没有事实变化：文字不动，状态依法更新

R1 Preview 的 Aha wording 已通过；Final R2 只完成 day lifecycle 收口，没有材料变化。

结果：Moment Line exact retain；R2 经完整发布后成为`FINAL_PUBLISHED` baseline。用户看到的句子不变，但系统保留真实 Final refs/state，不把 R1 原地改名。

### 68.10 两阶段 immutable lifecycle artifacts

Cross-check 发现：发布前 D4d3 不能引用尚未产生的 S12/CAS 结果，也不能在发布后回填同一个 immutable 对象。因此生命周期拆为两个顺序对象。

#### Phase 1｜发布前计划

~~~text
AhaMomentLinePublicationPlan
  daily_memory_run_ref
  stable_memory_id
  revision_sequence
  current_revision_ref
  expected_published_head_ref?
  baseline_revision_ref?
  baseline_moment_line_artifact_ref?
  baseline_visibility_state?
    PREVIEW_PUBLISHED | FINAL_PUBLISHED
  baseline_eligibility
    ELIGIBLE_LAST_PUBLISHED
    | NOT_APPLICABLE_NO_PRIOR
    | INELIGIBLE_INVALIDATED
    | INELIGIBLE_UNAVAILABLE
  s09_editorial_action
  d4d1_gate_result?
  d4d2_change_plan_ref?
  c3a_surface_decision?
  current_content_plan_ref?
  current_moment_line_artifact_ref?
  current_active_projection_ref?
  current_e_verification_ref?
  proposed_orchestration_action
    NO_CHANGE_REUSE_PUBLISHED_HEAD
    | KEEP_PUBLISHED_HEAD_DURING_COMPUTE
    | HOLD_LAST_PUBLISHED_VALID
    | REQUEST_ATOMIC_PUBLISH_CURRENT
    | BLOCKED_NO_PUBLISHABLE_REVISION
  prior_current_ref_mix_check
  whole_revision_completeness_check
  reason_codes[]
  policy_and_algorithm_versions
  publication_plan_fingerprint
  construction_audit
~~~

只有`REQUEST_ATOMIC_PUBLISH_CURRENT`进入 S12 publication validation。其他 action 也保存计划记录，但不伪造 S12 成功。

#### Phase 2｜发布尝试后的提交记录

~~~text
AhaMomentLinePublicationCommitRecord
  publication_plan_ref
  current_revision_ref
  expected_published_head_ref?
  head_at_commit_attempt_ref?
  s12_publication_validation_ref?
  publication_cas_result
    CAS_PASS
    | STALE_PUBLICATION_ATTEMPT
    | NOT_ATTEMPTED
  resolved_commit_action
    ATOMIC_PUBLISHED_CURRENT
    | NO_CHANGE_REUSED_PUBLISHED_HEAD
    | HELD_LAST_PUBLISHED_VALID
    | BLOCKED_NO_PUBLISHABLE_REVISION
    | STALE_RESULT_NOT_PUBLISHED
  resulting_published_head_ref?
  resulting_visibility_state?
    PREVIEW_PUBLISHED | FINAL_PUBLISHED
  reason_codes[]
  commit_policy_version
  commit_record_fingerprint
  commit_audit
~~~

两个对象都一次写成、不可回填：Plan 只引用 D4d3 之前已经完成的 current refs；Commit Record 才引用后置 S12/CAS 结果。只有 S12 通过且`CAS_PASS`时，`ATOMIC_PUBLISHED_CURRENT`才能更新 published head。该拆分不新增用户状态，也不改变用户确认的 hold／atomic publish 行为。

### 68.11 成本、存储与可观测性

1. D4d3 只读写 refs、fingerprints、状态与小型 audit artifact，不调用 Writer/VLM，不增加抽帧、上传或 HQ materialization；
2. immutable lifecycle artifact 不要求复制 Raw/HQ 媒体文件，只引用各 Revision 已有的合法 media artifacts；实际存储 retention policy 仍属平台工程；
3. Hold previous 可避免失败重试期间反复生成／发布文字，也避免用户看到卡片闪动；
4. CAS／stale check 是低成本数据库／编排操作，却能防止高影响的版本倒退；
5. D6/day-level benchmark 至少记录：Sync 次数、内部 Revision 数、material Revision 数、retain/patch/rebuild/block 数、Writer logical attempts、成功发布 Revision 数、hold 数与 stale publication 数；
6. 多次 Sync 的主要文字成本仍来自真正进入 patch/rebuild 的 material Revision，D4d3 本身不是模型成本来源；
7. 具体数据库、队列、事务、缓存、TTL、历史清理与跨设备同步实现留给 Production engineering，不在本节绑定供应商。

### 68.12 D4d3 Closeout Invariants

1. baseline 只来自当前 published head 中 last successfully published、可访问且 lineage 合法的 artifact；未发布内部结果与更老历史版本不参与自动 fallback；
2. “user-visible”按已发布且可访问判断，不要求用户打开 telemetry；
3. current Revision 计算期间保持完整 prior published head，不清空、不展示草稿、不要求额外交互；
4. current Revision 只有在全部 required surfaces、current text/media refs、E、S12 与 CAS 全部通过后才原子切换；
5. 禁止 prior/current text、media、Claim、lineage 混搭，`TEXT_RETAIN`也必须建立 current mapping/artifact；
6. 任一 required Aha Moment Line 失败都不发布 current 临时子集；合法 prior 存在时保持整版 prior；
7. Final 失败不把 prior Preview 改名为 Final；Final 发布后普通 Preview 不得反向降级覆盖；
8. ordinary uncertainty／worker failure／lineage unresolved 不自动使 prior 失效，继承 S09`HOLD_PREVIOUS_REVISION`；
9. prior 若被 authoritative Evidence 或正式 lifecycle 明确 invalidate，就不再是合法 fallback；不自动回滚更老历史，算法返回无安全可发布版本；
10. known-invalid prior 的具体隐藏／中性更新 UI 留给 App/S12，但 S11 不生成占位事实句；
11. 并发 Revision 发布必须 CAS；迟到 stale 结果不覆盖新 head、不成为 baseline、不重置 attempt budget；
12. D4d3 使用“发布前 Plan＋发布后 Commit Record”两个顺序 immutable artifacts，不回填、不循环引用；不新增媒体计算或模型调用，也不改变 S09、S10、S12 owner 权限。

### 68.13 已确认结论

当前中文测试版冻结：**用户再次 Sync 后，合法的完整 published head 继续无感显示，直到 current Revision 全链路通过并原子替换；任何一个 required Aha 失败都不发布半套结果。Final 失败时 prior Preview 可继续显示但不冒充 Final；并发任务使用 CAS，旧结果不能覆盖新 head。只有 prior 仍合法时才可 fallback；已被 authoritative Evidence 证明核心错误的 prior 不再继续 serving，也不自动回滚更老历史，算法返回无安全可发布版本，具体隐藏／中性更新 UI 后置。**

### 68.14 冻结记录

**冻结日期：** 2026-08-28

**用户确认：** 确认合法 prior 无感保持、整版原子发布、禁止 partial/hybrid、Preview/Final 身份真实、并发 CAS 防倒退、known-invalid prior 不继续 fallback，以及无安全版本时的具体 UI 后置。

**冻结范围：** 68.1–68.13 的 published baseline、Preview/Final、计算中行为、原子发布、fallback eligibility、hybrid 禁止、并发顺序、案例、两阶段 lifecycle artifacts、成本边界与十二项 Closeout Invariants。

**不在冻结范围：** known-invalid prior 的 App 具体隐藏／中性状态、数据库／队列／事务实现、历史存储 retention、D4e localization、D6 provider／模型／Prompt／candidate／transport retry／day-level cost、E/S12 implementation、海外 locale、Production infrastructure 以及整个 D4／S11。

**变更规则：** 只有真实版本闪动／倒退／错误 fallback 样本、用户测试反证或新的显式 versioned checkpoint 才可修订；不得由 worker 完成顺序、模型版本或临时 UI 需要静默改变 published head。

**Cross-check amendment：** 68.10 从单一可回填 lifecycle object 拆为发布前`AhaMomentLinePublicationPlan`与发布后`AhaMomentLinePublicationCommitRecord`，避免前向引用 S12/CAS 与 immutable 回填；不改变产品行为。

## 69. D4d1–D4d3 Full Cross-Check

**状态：PASSED WITH 2 CONTRACT-ALIGNMENT AMENDMENTS / D4d FROZEN AND CLOSED / D4 NOT FROZEN**

### 69.1 检查范围与结论

本轮交叉检查：

~~~text
S09 published retention / lineage / NO_CHANGE / HOLD / Preview-Final
↔ S10 current active media projection
↔ C3a TEXT_RETAIN / PATCH / REBUILD / BLOCK
↔ C3b2 base context/support owner
↔ C3b3 qualifier/light-affect owner
↔ B3 current plan composition validation
↔ D4a–D4c2 wording / length / bounded attempt envelope
↔ future E actual wording verification
↔ future S12 whole-Revision publication validation
↔ D4d1 retain gate
↔ D4d2 patch/rebuild plan
↔ D4d3 published lifecycle
~~~

结论：D4d1–D4d3 的产品原则可以同时成立，没有需要推翻的用户决定。检查发现两处结构对齐问题，均已修正：baseline 的“用户可见”语义统一到 S09；D4d3 lifecycle 拆为发布前／发布后两个不可变对象。D4d 现已形成闭合链路。

### 69.2 两项 contract-alignment amendments

1. **Baseline 不依赖打开 telemetry：** D4d1 64.2 原“用户真正看过”容易被误实现为必须记录用户打开。现与 S09 对齐为“已经成功发布且用户可访问”；这是更保守的连续性保护，不改 material-change 门。
2. **发布 lifecycle 两阶段化：** D4d3 68.10 原单对象同时包含 pre-S12 plan 与 post-S12/CAS result，存在前向引用和回填风险。现拆为 immutable Publication Plan → S12/CAS → immutable Commit Record。

### 69.3 上下游交叉结果

| 检查项 | 结果 | 约束结论 |
|---|---|---|
| S09 published baseline ↔ D4d1/D4d3 | PASS AFTER AMENDMENT | 只读取 published head；内部 draft、失败 Revision、实际打开 telemetry 与更老历史均不冒充 baseline |
| S09 `NO_CHANGE_REUSE` ↔ D4d1 | PASS | selection 与 downstream fingerprints 均相同时不制造可见 Revision、不调用 Writer |
| S09 `HOLD_PREVIOUS_REVISION` ↔ D4d3 | PASS | ordinary uncertainty／failure 保持合法完整 prior，不拼 current partial |
| S09 invalidation/withdrawal ↔ fallback | PASS | retention 不保护已知错误；known-invalid prior 不作为 active fallback，也不自动复活更老版本 |
| S10 active media ↔ retained wording | PASS | 新 Revision 中 exact text 仍绑定 current media/current Claims；hold prior 时保持整套 prior text/media |
| C3a four states ↔ D4d gates | PASS | D4d gate/mode/action 均为从属决策，不创建第五种内容状态 |
| C3b2/C3b3 owners ↔ D4d2 patch | PASS | context/support、qualifier、light affect 回各自 owner；Writer不直接改 plan |
| B3 ↔ patch/rebuild | PASS | 任何 Claim/relation/group 变化与所有 rebuild 都重过 current B3 |
| D4c2 attempt envelope ↔ later Revision | PASS | 每 current Revision 只有同一四类 semantic envelope；patch mode、E 回流与 stale worker 均不重置 |
| E ↔ protected/allowed spans | PASS | E 后续必须验证 current output 没有改动受保护 span或新增 Claim |
| S12 ↔ D4d3 lifecycle | PASS AFTER AMENDMENT | pre-publish plan 不引用 S12；post-validation commit record 保存 S12/CAS 与实际 head action |
| Preview/Final ↔ continuity | PASS | Finalization 本身不改 wording；Final failure 不冒充成功，Final head 不被普通 Preview 降级 |
| 并发 Revision ↔ published head | PASS | expected-head CAS 阻止迟到旧任务倒退用户版本 |
| 成本／上传 ↔ D4d | PASS | D4d 全部消费现有 refs/Claims/fingerprints；不新增上传、抽帧、HQ、VLM，Writer只用于材料性 patch/rebuild |

### 69.4 结果空间完整性

| 当前情况 | D4d 内容结果 | 发布／展示行为 |
|---|---|---|
| 无 prior generated Moment Line | initial build | 全链路通过后原子发布；失败且无 prior 则不发布 |
| prior 完整合法、无材料变化 | `TEXT_RETAIN` | exact wording＋current mapping；需要 current Revision 时整版发布，否则 exact reuse |
| 同一 peak、局部 optional／必要 span 变化 | `TEXT_PATCH` | owner-routed bounded patch；成功后整版发布 |
| 核心结构或合法 upstream peak 改变 | `TEXT_REBUILD` | current full plan/B3/D4/E；成功后整版发布 |
| original peak unsupported | `TEXT_BLOCK` | 不换 peak；合法 prior 可 hold，已知失效 prior 不 fallback |
| current contract invalid | Contract Invalid | 工程诊断；普通不确定性下合法 prior 可 hold，不伪装成内容 Block |
| current Revision partial success | aggregate not ready | 不发布临时子集，保持合法完整 prior |
| Final blocked | blocked | prior Preview 可保持 Preview 身份，不冒充 Final |
| CAS head mismatch | stale publication attempt | 不发布旧结果；rebase 或停止 |

### 69.5 D4d Consolidated Closeout Invariants

1. D4d 只处理已发布 generated Aha Moment Line 的跨 Revision 连续性，不重新选 Aha、peak、media 或 membership；
2. baseline 只来自 current published head 中成功发布且可访问的合法 artifact，不依赖用户打开 telemetry；
3. 仍真实、独立可懂、与 current media 相容且符合 current contract 的 wording 必须 exact retain；新 optional 内容和风格偏好不触发改写；
4. retain 的字符串不变，但 current Revision 必须建立 current-equivalent Claim/span/dependency mapping，不能沿用 stale refs；
5. PATCH/REBUILD 依据 semantic skeleton，不依据字符差异；失效 optional 默认删除、不补位；
6. core identity/action/object/result/relation 或合法 selected peak 改变时 rebuild；original peak unsupported 时 Block，不能以 rebuild 换事件；
7. patch/rebuild 回唯一 owner、重过适用的 B3/D4/E，并共用 current Revision 的 D4c2 attempt envelope；
8. current 计算期间保持合法完整 prior；current 只有 required surfaces、text/media、E、S12 与 CAS 全部通过才原子发布；
9. 不发布 partial/hybrid/placeholder Revision，也不把 prior refs 改名成 current refs；
10. ordinary uncertainty 可 hold prior；authoritative invalidation 后 prior 不再是合法 fallback，也不自动回滚更老历史；
11. Preview/Final 保持真实 lifecycle，Final failure 不改名，Final head 不被普通 Preview 降级；
12. 并发发布使用 expected-head CAS；stale 结果不覆盖、不成为 baseline、不重置 budget；
13. 发布前 Plan 与发布后 Commit Record 分开 immutable materialize，不循环引用或回填；
14. D4d 不新增上传、Raw/HQ、抽帧或视觉模型成本；主要节省来自 retain 与有界 patch。

### 69.6 D4d 冻结记录

**冻结日期：** 2026-08-28

**冻结范围：** D4d1 64.1–64.10、D4d2 66.1–66.13、D4d3 68.1–68.13，以及 69.2 的两项 contract-alignment amendments、69.3/69.4 cross-check 与十四项 consolidated invariants。

**不在冻结范围：** App 对 known-invalid prior 的具体隐藏／更新中 presentation、D4e localization、D6 provider／Prompt／voice／cost、E/S12 implementation、数据库/队列/CAS 具体实现、海外 locale、Production infrastructure 以及整个 D4／S11。

**变更规则：** 只有真实跨 Revision 失败样本、用户体验反证、上游 canonical contract 修订或新的显式 versioned checkpoint 才可重开；不得由模型版本、worker 顺序或工程捷径静默改变。

**后置 localization 对齐（D4e cross-check）：** 当前中文只有一个 presentation locale，因此 D4d3 的`published head`等价于中文完整展示包。未来多 locale 时，每个稳定`target_locale_id`维护自己的 last complete presentation bundle；`target_locale_policy_ref`保存在 artifact 与 dependency checks 中，但不能成为 baseline 分区键，否则单纯 policy 升级会错误丢失旧 baseline、诱发重写。最终 CAS 同时核对 authoritative semantic head 与该稳定 locale 的 presentation head：同一 locale bundle 内的 text、media、Claims 与 lifecycle 必须绑定同一个 semantic Revision；不同 locale 可以独立 ready/hold；authoritative semantic invalidation 则使所有从该错误 Revision 派生的 locale bundles 同时失去 fallback eligibility。

~~~text
locale_moment_line_baseline_key
  = (stable_memory_id, target_locale_id, AHA_MOMENT_LINE)

publication dependencies / CAS guards
  expected_authoritative_semantic_head_ref
  expected_locale_bundle_head_ref
  target_locale_policy_ref
~~~

其中`target_locale_policy_ref`是合法性依赖，不是稳定 head identity。Policy version 变化后，旧 surface 若仍合法就继续 exact retain；只有实际不兼容／不合法时才进入 patch／rebuild／block。

## 70. D4d → D4e Transition

D4d 已通过完整交叉检查并关闭。下一步进入 D4e：区分哪些 Aha Moment Line 原则可跨语言共享，哪些必须为英文和其他海外 locale 单独设计；完成后才能对整个 D4 做 closeout cross-check。

## 71. S11-D4e｜Localization Boundary & Release Contract

**状态：CONFIRMED / FROZEN LOCALIZATION ARCHITECTURE / CURRENT CHINESE TEST PROFILE ONLY / ENGLISH AND OTHER LOCALE NUMBERS NOT YET DEFINED**

### 71.1 本检查点只决定 localization 边界

D4e 当前不为英文临时猜一个字符数，也不选择翻译模型。它先冻结三件事：

1. 哪些是所有 locale 都必须继承的事实／产品结构；
2. 哪些是 locale-specific wording/presentation contract，不能照搬中文；
3. 一个海外 locale 在允许 Production 生成 Aha 文案前，必须通过哪些 release gates。

当前中文测试继续使用已冻结 D4a–D4d。D4e 不把中文测试阻塞到英文完成，但英语和其他目标 locale 未建立合同前，不得以中文数字或直接翻译冒充海外 Production ready。

### 71.2 Universal semantic contract 与 locale-specific realization

| 跨语言共享，不重新决定 | 每个 locale 必须单独定义 |
|---|---|
| selected Aha、stable ID、single peak、Chapter relation | word/content-word/grapheme/display-width budget |
| active media、Evidence、Claim Ledger、assertion ceiling | 句法、语序、sentence boundary、标点 |
| 0–1 necessary context、0–1 support、0–1 qualifier | 主语省略、pronoun、gender、number、article |
| light-affect 的 grounded action target 与基础 semantic eligibility | 0–1 locale-specific permission、具体词汇、强度、文化风险 |
| truth、standalone、media compatibility、no invented Claim | 人名／地名／宠物名的转写、缩写、所有格和称呼 |
| D4d retain/patch/rebuild/block 的语义判断 | line wrapping、字体宽度、Dynamic Type、accessibility |
| D4c2 每 Revision 的有界 semantic attempt 原则 | locale voice、自然度、禁用词与 verifier 细则 |

共享的是“写什么、凭什么写、什么时候允许改”；本地化的是“该语言怎样自然、安全、可显示地表达”。

共享层提供同一个 required peak core、必要性判断与已排序 optional inventory。每个 locale 再形成 immutable `LocaleAhaNarrativeSurfacePlan`：必须保留同一 peak 与该 locale 中仍必要的 context；只有在本语言长度／语法合同确有需要时，才按 D4c 已冻结顺序单调删除 light affect、qualifier 或非必要 support。不能因为另一个 detail 更短就换 optional Claim，更不能换 peak。

### 71.3 不以中文 surface 作为翻译源

Production 路径必须是：

~~~text
same locale-neutral Aha base plan
+ same factual Claim / relation / observable-qualifier refs
+ target-locale light-affect permission, 0..1
+ target-locale realization policy
→ target-locale B3 surface-plan validation
→ target-locale D4 realization
→ target-locale E actual wording verification
~~~

禁止默认路径：

~~~text
Chinese Moment Line
→ generic translation
→ overseas publish
~~~

原因：中文可以省略主语、冠词和单复数，英文等语言往往必须显式选择；直接翻译会迫使翻译器猜 actor、gender、relationship、tense 或 article，从而在 Claim plan 之外新增断言。不同 locale 必须消费同一 canonical plan，而不是互相翻译已经压缩过的 surface。

中文或任一 locale 已获准的 light-affect wording 不能把 permission 自动传给另一语言；目标 locale 只能从同一 grounded action target／base eligibility 派生自己的 0–1 permission，无法证明安全 mapping 时取 0。人工确认的翻译可以作为 user-authored／editorial artifact 另行保留，但不改变自动生成默认链路。

### 71.4 当前中文合同不能机械外推

以下当前只对中文测试有效：

- 正常 4–20、必要事实软扩展 21–24 visible grapheme clusters；
- 一个中文 logical sentence、句号结尾、最多两枚内部中文逗号；
- 中文主语省略与`猫咪／狗狗／旁边的人`等称呼降级；
- `调皮地／活泼地`等中文 light-affect 候选；
- 中文连接词、语序、词义强度与自然节奏。

英文不能使用“20 characters”作为等价上限。其他语言也不能仅把 20／24 换算为平均字数；德语复合词、法语冠词、西班牙语性数、日语书写系统、阿拉伯语方向与不同字体宽度都可能产生不同 presentation 结果。

### 71.5 每个 target locale 的 required contract

一个 locale 从 Research 进入 Production 前，至少必须冻结并验证：

1. `locale_id`、区域变体、只在已证明兼容的语言变体之间使用的 fallback chain 与 policy version；不得把中文到英文或任意不同语言的静默 fallback 写进该 chain；
2. normal／soft-extension 的 word、content-word、grapheme 与 display-width 预算，以及什么事实有资格使用扩展；
3. 一个 Moment Line 的 sentence/clause 数、标点白名单与 relation-bearing connectors；
4. subject/pronoun、gender、number、article、possessive 与 unknown-person referent contract；
5. proper noun、地名、人名、宠物名、缩写与 transliteration 规则；
6. locale-specific light-affect lexicon、动作触发、禁用词、文化风险与人工审核；
7. prohibited inference 与 Claim-to-span verifier，确保没有因语法需要猜身份／关系／意图；
8. 真实素材 eval set，覆盖不同用户画像、活动、动物、人物、地点、稀疏素材与高风险歧义；
9. native-speaker 人工评分：真实、自然、不过度编纂、情绪强度、可接受称呼与重复感；
10. 真机 UI：字体、单／双行、截断禁止、Dynamic Type、屏幕阅读器、RTL 与长专名；
11. target-locale E verifier、失败路由、patch/rebuild continuity 与 regression set；
12. latency/token/cost benchmark、缓存策略与 locale release sign-off。

每项 required gate 必须`PASS`，或在确实不适用时保存显式`NOT_APPLICABLE_WITH_JUSTIFICATION`；缺失、未测或无理由跳过时，该 locale 为`LOCALE_CONTRACT_NOT_READY`。这是 locale release-readiness，不是第五种 narrative 内容状态。未就绪 locale 不得把中文规则机械继承后上线；它不阻断已获批准的其他 locale，也不把整个 Memory membership 改掉。

### 71.6 跨 locale 的 continuity

1. 每个 locale 的 generated wording artifact 与 published baseline 分开保存；中文原句不成为英文 exact-retain baseline；
2. 用户切换 App 语言不等于 Memory Facts 发生材料变化，不触发 S09 reselection；它只选择／构建目标 locale surface；
3. 同一 locale 后续 Sync 继续使用 D4d exact retain／patch／rebuild；不同 locale 之间只共享 canonical plan、Claims 与 permissions，不要求文字 diff 相似；
4. 切回曾经使用过的 locale 时，若该 locale artifact 与 current dependencies/policy 仍有效，可复用或 revalidate；不能引用 stale Claim refs；
5. target locale policy 版本升级本身不触发改写；只有旧 surface 实际不再合法时才进入该 locale 的 D4d path；
6. 一个 locale 生成失败不允许拿另一语言的 generated sentence 静默冒充目标语言结果。App 是否明确展示可选择的已支持语言，属于后续 UX 合同。

每个 locale 的 D4c2 semantic attempt envelope 独立，以`(stable_memory_id, revision_ref, target_locale_policy_ref, AHA_MOMENT_LINE)`为 key，仍然最多四类且通常一次。中文 attempt 不消耗英文名额，英文失败也不重置中文名额；D6 必须另设跨全部 locale 的 day-level 总成本上限。

### 71.7 案例检查

#### 案例 A｜中文 20 字不等于英文 20 characters

中文：

> 猫咪跃上桌，碰倒了纸杯。

英文若机械限制 20 characters，可能被迫删掉 actor/object 或截断。正确做法是由 English contract 定义 word/content-word 与 display-width 预算，再从同一 Claims 生成完整自然句，而不是截取翻译结果。

#### 案例 B｜中文省略动作执行者，英文不能自行猜“我”

中文：

> 甜品切开，流心淌了出来。

英文 realizer 不能因为语法需要主语，就自动写成`I cut the dessert...`。没有 self-action mapping 时，应使用目标 locale 合法的 event-centered／passive／generic construction，或按 locale contract Block；不能让翻译器创造“我”。

#### 案例 C｜`调皮`不能直接等于 `naughty`

中文当前动作可能获准使用轻量`调皮地`，但英文`naughty`在不同语境可能更负面、更像责备。English light-affect lexicon 必须由 native-speaker 样本和风险测试确认；没有 mapping permission 时只写事实动作。

#### 案例 D｜专名导致本地化膨胀

中文短名“周庄”在英文界面可能使用`Zhouzhuang Ancient Town`。如果 exact place 对独立理解并非必要，应继续遵守必要性门，不为“更具体”强塞长专名；若确实必要，则 English soft-extension 与 UI wrapping 必须能安全容纳，不能截成含糊片段。

#### 案例 E｜切换语言不是改写中文历史

用户先以中文查看 Aha，随后切换英语。系统从同一 current plan 生成／读取 English artifact；中文 baseline 保持不变。切回中文时，若 current dependencies 仍等价，继续显示原中文 wording，不因英语表达不同而重写。

#### 案例 F｜目标 locale 未准备好

某语言只有通用机器翻译，没有长度、pronoun、light-affect、UI 和 native-speaker eval contract。

结果：`LOCALE_CONTRACT_NOT_READY`。不能把中文 Moment Line 自动翻译后标记 Production ready；中文测试与已经通过 release gate 的其他 locale 可以继续。

#### 案例 G｜英文更长时只能删除可选内容

中文 plan 合法包含`peak + qualifier + optional support`；English contract 下完整自然表达超过该 locale hard envelope。

正确路径是使用 English 自己的 D4c2 envelope，先省略 locale-specific light affect，再删除 optional qualifier／非必要 support；如果 context 对 standalone 必要，则不能删除。最小 required core/context 仍无法安全表达时，该 English surface Block，不能改选一个更短的 Aha peak，也不能影响已经合法发布的中文 surface。

### 71.8 成本与工程边界

1. 多 locale 共享素材理解、Evidence、Facts、Claims、selected peak 与 Content Plan，不按语言重复跑抽帧、上传、VLM 或 HQ；
2. 增量成本主要是每个实际生成 locale 的独立、有界 Writer attempts、E verification、缓存与人工评测；启用 N 个 locale 不应自动复制 N 份视觉推理；
3. eager 预生成所有语言、按用户 locale lazy 生成，还是混合缓存策略，留给 D6/Production cost benchmark；
4. locale artifact 只保存文字与 refs，不要求复制媒体；
5. 本节不选择翻译／生成 provider，不冻结 token 价格，也不实现 App language selector；
6. 海外 Production 的主要风险不是视觉算力，而是未经验证的语法推断、文化语气、专名膨胀、UI 截断与自然度。

### 71.9 D4e Closeout Invariants

1. Aha membership、single peak、factual Claims/relations、grounded affect target/base eligibility、truth 与 continuity semantics 跨 locale 共享；light-affect realization permission 与文字 presentation 按 locale 独立；
2. target locale 默认从 canonical current plan 生成，不以中文压缩 surface 作为通用机器翻译源；
3. 当前中文 20／24 grapheme、主语省略、标点、称呼与 light-affect 词表只属于中文测试 profile；
4. 英文及其他 locale 必须分别定义 word/content-word、grapheme、display width、syntax、pronoun、proper noun、affect、accessibility 与 verifier 合同；
5. 未完成 required release gates 的 locale 为`LOCALE_CONTRACT_NOT_READY`，不得机械继承中文规则或静默发布翻译结果；
6. 每个 locale 保存独立 generated artifact 与 published baseline；切换语言不触发 Memory reselection，也不互相改写 baseline；
7. 同一 locale 继续继承 D4d exact retain／patch／rebuild；policy version 变化本身不触发润色；
8. 一个 locale 失败不使用另一语言 sentence 静默冒充，不改变已批准 locale 的 Memory membership；
9. 每个 locale 从共享 base plan 形成自己的 immutable surface plan；只能按冻结优先级删除本语言放不下的 optional 内容，不能删除必要 context、替换 Claim 或更换 peak；
10. D4c2 attempt envelope 按 target locale policy 分开且每个仍最多四类；D6 另行控制跨 locale 的 day-level 总预算；
11. 多 locale 共享视觉／事实计算，增量成本集中在 text generation、verification、eval 与 UI；
12. D4e 当前冻结的是 localization 架构与 release gate，不提前猜 English 数值、模型或 App 交互。

### 71.10 最小 locale surface plan

~~~text
LocaleAhaNarrativeSurfacePlan
  stable_memory_id
  revision_ref
  canonical_aha_base_plan_ref
  target_locale_id
  target_locale_policy_ref
  factual_claim_refs[]
  relation_refs[]
  observable_qualifier_ref?
  grounded_affect_eligibility_ref?
  target_locale_light_affect_permission_ref?
  required_peak_core_ref
  necessary_context_ref?
  retained_optional_refs[]
  locale_dropped_optional_refs[]
  locale_drop_reason_codes[]
  no_claim_substitution_check
  no_peak_change_check
  requires_current_b3_validation = true
  d4c2_attempt_envelope_key
  locale_contract_readiness_ref
  policy_and_algorithm_versions
  locale_surface_plan_fingerprint
  construction_audit
~~~

该 plan 位于 target-locale B3 之前，因此不回填`b3_validation_ref`；它只声明必须经过 current B3。只有 B3 通过后的 immutable validated artifact 才可进入 target-locale D4。`locale_dropped_optional_refs[]`只能记录 D4c 顺序允许的单调删除，不能用另一个更短 Claim 补位。

### 71.11 已确认结论

冻结 localization 架构：**当前中文测试合同不机械外推到英文；target locale 从 locale-neutral canonical base plan 与 current Claims 生成，经 locale-specific permission、B3、D4、E，不默认翻译中文 surface。每个 locale 单独定义长度、语法、指代、专名、light affect、UI、验证、成本与 release gate；各 locale 有独立 surface plan、attempt envelope、artifact 与 continuity baseline，但共享视觉理解和事实计算。未就绪 locale 不得上线，也不使用另一语言静默顶替。**

### 71.12 冻结记录

**冻结日期：** 2026-08-28

**用户确认：** 确认当前先完成中文测试 D4、不临时猜英文长度；海外 locale 直接消费 canonical plan 而非默认翻译中文；每 locale 独立合同、permission、验证、baseline 与发布门；未就绪 locale 不上线。

**冻结范围：** 71.1–71.11 的 universal/localized 边界、canonical-plan realization path、中文不可机械外推、十二项 locale release gates、跨 locale continuity、per-locale attempt envelope、案例、成本、最小 plan 与十二项 Closeout Invariants。

**不在冻结范围：** 英文及其他 locale 的具体长度／词数／display width／词表／UI 数值、目标市场优先级、provider/Prompt、eager/lazy generation、App language fallback、D6 cost、E/S12 implementation 与 Production infrastructure。

**变更规则：** 只有 target-locale 真实样本、native-speaker 评测、真机 UI、成本 Benchmark 或新的显式 versioned checkpoint 才可填充／修订 locale 数值；不得由通用翻译器、中文数字或模型偏好静默决定。

## 72. S11-D4 Full Closeout Cross-Check

**状态：PASSED WITH 3 LOCALIZATION ALIGNMENTS / CURRENT CHINESE D4 DESIGN FROZEN / GLOBAL PRODUCTION NOT READY / S11 NOT FROZEN**

### 72.1 检查范围与结论

本轮不是重新设计 D4，而是从最终用户看到的一条 Aha Moment Line 反向检查：

1. 它是否只表达已经通过 Evidence／Facts／Claims／B3 的事实；
2. 它是否仍围绕一个 selected peak，不把 Aha 写成 Chapter；
3. 它是否能在中文短句合同内自然表达，并在放不下时安全降级；
4. 它在事实修订、版本竞争、重复打开 App 与语言切换时，是否不会无故改写或发布混合版本；
5. 它是否没有把中文规则误当成全球规则；
6. 它是否没有提前侵入 D5 Tags、D6 Writer runtime、E verification、S12 lifecycle implementation 与 App UI 的职责。

结论：**D4a–D4e 的主链闭合，没有发现需要推翻用户已确认产品定义的冲突。发现的三处问题均为多语言接口未显式化，而不是中文合同本身错误；三项对齐修订已经写回对应小节。当前中文 Aha Moment Line D4 设计可以阶段性冻结。**

这里的“阶段性冻结”只表示 D4 设计不再无理由漂移；不表示模型、Prompt、provider、英文数值、App UI 或 Production 系统已经完成。

### 72.2 三项 Localization Alignment

#### Alignment 1｜Light Affect 拆成共享资格与本语言表达许可

- 跨 locale 共享：动作证据、情绪修饰的 base semantic eligibility、修饰对象；
- 按 locale 独立：是否允许实现、允许哪个低风险词、语序和语气；
- 当前 D4b1 冻结的 permission 是中文测试 profile 的实例，不能自动授权英文使用对应翻译词。

**案例：** 中文可把猫咪跃上桌写成“调皮地跃上桌”，不代表英文一定可用`naughty`。英文词表未通过本地评测时，只保留“跃上桌”这一事实，不改变 Aha peak。

#### Alignment 2｜D4c2 Attempt Envelope 按 Locale 隔离

- key 对齐为`(stable_memory_id, revision_ref, target_locale_policy_ref, AHA_MOMENT_LINE)`；
- 每个 locale／revision 仍最多四类 semantic attempt，通常一次即可；
- 某语言失败不重置另一语言，也不消耗另一语言的 attempt；
- 新 policy key 只是隔离合法 attempt 的审计边界，不自动授权生成；只有 C3a 材料变化门成立、旧 surface 实际不再合法并形成合法 current Revision 时，才可进入新的 D4 envelope；
- D6 必须再定义跨 locale、按天的总调用／成本上限，防止语言数量线性放大费用。

**案例：** 中文第一次生成即通过，英文因必要专名过长尝试一次安全压缩。英文这次尝试不改写中文，也不会占用中文已结束的 envelope；但两次调用都计入未来 D6 当日总预算。

#### Alignment 3｜D4d Baseline、Atomic Publish 与 CAS 按 Locale Bundle 管理

- 每个稳定`target_locale_id`有独立、完整、已成功发布且可访问的 presentation bundle 与 baseline；
- `target_locale_policy_ref`是 artifact 的校验依赖，不是 baseline 分区键；单纯 policy 版本变化不制造“无 prior”或强制改写；
- 一个 bundle 内的文字、媒体 refs、Claims refs、policy version 与 lifecycle record 必须指向同一 semantic revision；
- 不同 locale 可以分别处于 ready／hold，不要求同时发布；
- authoritative semantic revision 被判无效时，由它派生的全部 locale bundle 均失去发布资格；
- CAS 继续阻止旧 revision 覆盖新 revision，同时核对 authoritative semantic head 与稳定 locale presentation head。

**案例：** 中文 bundle 已完整发布，之后中文 policy 从 v1 升到 v2，但原句仍满足 v2。因为 baseline 按稳定中文 locale 保存，系统继续 exact retain，不把 v2 当成一个“新语言”重写。英文合同尚未就绪时，切换英文也不能把中文句子临时翻译后冒充英文 bundle。若后来发现 selected peak 本身无证据，则中文和英文派生物都不能继续作为 current result。

### 72.3 上下游逐项交叉检查

| 检查接口 | 结论 | 闭环说明 |
|---|---|---|
| C3b1 Aha shape ↔ D4a／D4b | PASS | Aha 仍只有一个 required Moment Line 和一个 selected peak；没有新增 Aha title／long story。 |
| Facts／Claims／C3b2 ↔ D4 | PASS | Writer 只实现 plan，不新增人物关系、主观感受、因果、地点或“我”的动作。 |
| C3b3／B3 ↔ D4 | PASS | 只有 current validated plan 才能进入 D4；本地化 plan 也必须重新经过该 locale 的 B3，不把中文 validation 机械继承过去。 |
| D4a 长度 ↔ D4c 压缩 | PASS | 中文常规 4–20 个可见字符；21–24 只保留必要信息；禁止截断、填充和为追求长度而改事实。 |
| D4b1 Peak／Affect ↔ D4e | PASS AFTER ALIGNMENT 1 | Peak 与 base evidence 共享；具体轻情绪词由 locale permission 独立决定。 |
| D4b2 指代 ↔ D4e | PASS | 目标语言不能为满足语法自行发明“I”、亲属、关系或动作执行者；必要时换合法句式，否则 Block。 |
| D4b3 中文标点 ↔ D4e | PASS | 中文 sentence-ending punctuation 只属于中文 profile；其他语言自行定义，不继承字符数字。 |
| D4c1 简化顺序 ↔ D4e | PASS | 各 locale 只能按冻结顺序单调删除 optional 内容；不能删 necessary context、替换 Claim 或改 selected peak。 |
| D4c2 尝试上限 ↔ D4e | PASS AFTER ALIGNMENT 2 | Attempt 按 locale／revision 隔离；跨 locale 总成本由 D6 单独收口。 |
| C3a 四状态／D4d ↔ D4e | PASS AFTER ALIGNMENT 3 | 每个 locale 独立生成、hold 与发布，但共享同一 authoritative semantic revision。 |
| S09 lineage／published state ↔ D4d | PASS | exact-retain、patch、rebuild、Preview／Final、atomic commit 与 stale-write protection 均有明确依据。 |
| S10 active media ↔ D4d | PASS | D4 不能独立替换媒体；发布 bundle 引用同一 revision 下已批准的 active media set。 |
| D4 ↔ D5 Tags | PASS / NOT STARTED | Moment Line 可有氛围但不承担结构化描述；事实型、检索型、分类型信息仍留给 D5。 |
| D4 ↔ D6／E／S12 | PASS / OPEN | D4 只产出有界 surface artifact；D6 管运行时与成本，E 做实际文案验证，S12 才拥有生命周期实施与发布。 |
| 上传／视觉成本 | PASS | 多语言不重复抽帧、上传、VLM、HQ 或事实推理；仅增加实际使用 locale 的文字生成、验证、缓存与评测。 |
| 用户原始／手写内容 | PASS | D4 只管理系统生成的 Aha Moment Line，不改写用户原始素材、caption 或 Manual 窗口内容。 |

### 72.4 结果空间完整性检查

| 输入情形 | 唯一允许结果 | 案例 |
|---|---|---|
| 中文完整自然表达为 4–20 字 | `D4_DRAFT_READY_FOR_E` | “猫咪调皮地碰倒了纸杯。”事实、语气、长度均合法，交给 E 检查实际文字。 |
| 20 字内放不下，但 21–24 字只多出必要信息 | 使用 soft extension 后进入 E | 不写地点就无法区分事件，地点经必要性门通过，因此保留到 23 字。 |
| 超长部分仅是 light affect／optional qualifier／support | 按 D4c1 顺序删除后再验证 | 先删“调皮地”，而不是删掉谁碰倒了什么。 |
| 最小 peak core + necessary context 仍超过 24 字 | `D4_REQUIRED_SURFACE_BLOCKED` | 专名和对象均不可安全省略，不能截成半句，也不能换一个更短的 peak。 |
| 已发布句子及依赖仍等价 | `TEXT_RETAIN`，不调用 Writer | 用户再次打开 App，事实没变，继续显示原句而不是随机换说法。 |
| 仅局部事实发生有效修订 | `TEXT_PATCH` | 地点 display name 被纠正，只修改受影响 claim span，再走 B3／D4／E。 |
| selected peak、必要 context 或 claim skeleton 改变 | `TEXT_REBUILD` | 原来选“切开甜品”，新证据表明 peak 应是“流心淌出”，必须重建，不做字符替换。 |
| 原 selected peak 已被证伪且无合法替代 | `TEXT_BLOCK` | 不用想象细节补救，也不保留 known-invalid baseline。 |
| locale contract 未就绪 | `LOCALE_CONTRACT_NOT_READY` | 法语没有指代、长度、UI 与 verifier 合同，只阻断法语上线；不影响已合法中文 bundle。 |
| 某 locale bundle 只成功写入文字，媒体／claims 尚未提交 | 不发布该 locale | Atomic publish 不允许用户看到跨 revision 的半套结果。 |
| authoritative semantic revision 被判无效 | 所有派生 locale bundle 失效 | 不是只修中文 wording；事实源失效会穿透所有语言。 |
| 旧任务晚于新任务返回 | CAS 拒绝旧结果 | revision 12 已成为 current，revision 11 的英文结果不能覆盖它。 |

以上覆盖了正常通过、必要扩展、安全压缩、内容阻断、合同未就绪、连续性保留、局部修订、语义重建、并发失败与多语言失效传播；未发现会落入“默认猜测”或“无限重试”的无主分支。

### 72.5 D4 Consolidated Invariants

1. 每个 Aha 必须只有一条 Moment Line，围绕一个已选 peak；
2. 中文测试常规目标为 4–20 个可见字符，21–24 只允许必要信息；
3. 不允许语义截断、为长度填充、为了短而替换 Claim 或更换 peak；
4. 内容保留优先级为 peak core > necessary context > immediate support > observable qualifier > locale-specific light affect；
5. 不从第一人称画面推断“我”的动作，不从共现推断人物关系；
6. 中文当前使用完整短句及中文句末标点；该规则不自动外推；
7. Writer 只能实现 immutable validated plan，不能自行选事实；
8. 超长时只按冻结顺序做单调删除；最小合法表达仍失败则 Block；
9. 每个 locale／revision 最多四类 semantic attempt，D6 另设跨 locale 当日总预算；
10. `D4_REQUIRED_SURFACE_BLOCKED`与`D4_REALIZATION_CONTRACT_INVALID`必须分开记录；
11. 已发布依赖等价时默认 exact retain，不为了新鲜感重写；
12. Patch／rebuild 由 claim skeleton 与语义变更决定，不由字符差异决定；
13. 发布单位是单一 locale 下的完整 bundle，禁止混合 revision；
14. CAS 必须阻止旧 revision、旧 policy 或过期任务覆盖 current；
15. 目标 locale 从 canonical facts／claims／base plan 生成，不默认翻译中文 surface；
16. 每个 locale 有独立合同、permission、B3、D4、E、baseline 与 release gate；
17. 多语言复用视觉、事实与 peak selection，不重复上传或视觉推理；
18. D4 无最终 publish authority；D6、E、S12 与 App presentation 的职责保持开放且不被越权。

### 72.6 显式保留到后续阶段的问题

以下内容没有被本次“冻结”偷偷决定：

1. D5 Tags 的 canonical tag、用户可见 label、数量、必选性与去重；
2. D6 的 provider、模型、Prompt、temperature、缓存、跨 locale 日预算和实际单位成本；
3. E 的具体 verifier、评分阈值、人工复核样本与失败归因；
4. S12 的数据库结构、job orchestration、CAS 实现、回滚和监控；
5. 英文及其他 locale 的 word／content-word／grapheme／display-width 数值、pronoun 策略、专名规则、轻情绪词表与 release benchmark；
6. App 的语言选择、未就绪语言提示、换行、字体、无障碍和 fallback 交互；
7. 真实用户素材上的校准、标签、评分、A/B Test 与 Production gate；
8. 隐私、伦理与 retention policy，仍按既定全局顺序留待核心内容链打通后处理。

### 72.7 D4 阶段性冻结记录

**冻结日期：** 2026-08-28

**冻结对象：** 当前中文测试版 Aha Moment Line 的 D4a 长度、D4b 语义／指代／标点、D4c 压缩与尝试边界、D4d continuity／publication contract，以及 D4e localization architecture。

**交叉检查结果：** 通过；仅增加 72.2 的三项 localization alignment，未修改用户已确认的核心产品体验。

**冻结效力：** 后续 D5／D6／E／S12 必须继承 72.5；若真实数据证明需要修改，必须给出失败样本、影响链、成本／体验分析与显式 versioned checkpoint，不能静默改规则。

**全局状态：** D4 已阶段性冻结；S11 尚未冻结，D5／D6／E 仍待设计；Production 尚不可用。

## 73. D4 → D5 Transition

D4 已回答“一个已经选定且有证据的 Aha，用哪一句短而自然的话呈现”。下一阶段 D5 将单独回答“哪些结构化标签帮助用户浏览、检索和理解，但不把 Moment Line 写成僵硬说明”。

D5 的第一个检查点应是 **D5a Tag Product Role**，依次明确：

1. canonical tag 与用户可见 label 是否是同一层；
2. 哪些 tag 是系统内部使用，哪些可以展示给用户；
3. 每个 Chapter／Aha 是否必须有 tag，以及数量上限；
4. tag 与 Moment Line、Chapter 1–2 句 story 的职责边界；
5. 相似 tag 的合并、时间／地点／活动／对象 tag 的证据门；
6. 中文测试与海外 localization 的共享／独立部分。

**案例：** Moment Line 可以写“老街转角，遇见一碗桂花冰粉。”；D5 可能另存`古镇`、`citywalk`、`甜品`等结构化概念。是否把这些概念原样展示、展示几个、能否把“古镇”推成精确地点，都必须在 D5a 之后逐项决定，不能由 D4 文案生成器顺手决定。

本节只建立下一步问题边界，**没有冻结任何 D5 数量或展示规则**。

## 74. S11-D5a｜Canonical Tag Product Role & Data Meaning

**状态：CONFIRMED / FROZEN PRODUCT ROLE / PRINCIPLES 1–10 LOCKED / D5 NOT FROZEN / TAXONOMY AND COUNTS NOT YET DEFINED**

### 74.1 所在链路、目标与本节不做什么

D5a 位于事实与 Claim 已经成立、Memory 已经选定之后，也位于具体 taxonomy、数量、UI 与检索排序之前：

~~~text
Selected Chapter / Aha
+ current ChapterFacts / AhaFacts
+ Claim Ledger / B2 surface eligibility
+ C2 cross-surface plan
→ D5 canonical concept mapping and assignment decision
→ B3 when tag composition requires validation
→ D5 display-label realization
→ E actual tag/label verification
→ S12 publication validation
→ retrieval / aggregation / future personalization inputs
~~~

本节只回答：**Canonical Tag 在产品和数据中到底代表什么。**

本节暂不决定：

- 具体有哪些活动、场景、地点、对象或主题概念；
- taxonomy 是两层还是三层；
- 每个 Chapter／Aha 最多几个 internal tags；
- App 是否展示、展示几个、放在哪里；
- 搜索排序权重、向量模型、个性化权重；
- Production classifier／LLM／数据库／索引供应商；
- 用户标签、隐私、数据 retention 与对外数据使用政策。

先冻结语义，是为了避免后面把`coffee / café / coffee shop / coffee time`当成四种数据，把一个 UI 数量限制误当成整个记忆检索系统的容量。

### 74.2 术语释义

| 术语 | 在 Diary One 中的含义 | 简单案例 |
|---|---|---|
| `Canonical Concept` | 由系统维护、语言无关、带稳定 ID 和版本定义的标准概念 | `ACTIVITY.POTTERY` |
| `Canonical Tag Assignment` | 某个 current Chapter／Aha 与某个 Canonical Concept 之间，经过 Evidence 与 Claim 验证的结构化关系 | Chapter C17 被合法映射到`ACTIVITY.POTTERY` |
| `Display Label` | 某个 Canonical Concept 在指定语言和产品界面里的可读名称 | 中文“陶艺”，英文“Pottery” |
| `Alias / Search Term` | 用户可能输入或系统用来理解查询的同义词、相关词；它不是新的 canonical concept | “拉坯”“制陶”可以帮助查找`ACTIVITY.POTTERY` |
| `Taxonomy` | Canonical Concepts、类别维度、上下位关系、定义、版本与废弃映射组成的受控概念目录 | `POTTERY_WHEEL_THROWING`属于更广的`POTTERY` |
| `Facet` | 概念所属的语义维度，避免把不同含义的标签放进同一扁平词袋 | Activity、Scene、Entity、Place 等；具体集合留给 D5b |
| `Embedding` | 把内容或查询转换成可比较数值向量的语义表示，适合找“意思相近” | 搜“手作”可能召回没有同名字面 Tag 的陶艺记忆 |

因此，**Canonical Concept 不是中文词；Canonical Tag Assignment 也不是把一个字符串塞进数组。** “陶艺”可以改成更自然的 Display Label，但底层 concept ID 与历史检索身份不应因此改变。

### 74.3 推荐的四层结构

~~~text
Layer 1  Grounded Memory Semantics
         Facts / Claims / relations / selected-memory identity
                ↓
Layer 2  Canonical Concept Registry
         stable concept IDs + facet + definitions + hierarchy + versions
                ↓
Layer 3  Memory-to-Concept Assignments
         exact scope + evidence + assignment relation + lineage + status
                ↓
Layer 4  Consumers
         retrieval index / aggregation / evaluation / optional Display Labels
~~~

这四层必须分开：

1. Fact 真实，不代表它一定值得成为索引；
2. Concept 存在，不代表当前 Memory 一定拥有它；
3. Memory 拥有内部 Assignment，不代表 App 必须展示该 Label；
4. App 不展示 Label，也不应删除内部检索索引；
5. Display Label 换语言或改措辞，不应改写 Fact、Assignment 或自然语言 Story；
6. 检索命中一个 Memory，不等于系统已经证明用户偏爱该主题。

### 74.4 D5a 推荐冻结的十项产品原则

#### 原则 1｜Canonical Tag 首先是内部索引，不是卡片装饰

Canonical Tag 的首要职责是让记忆可被稳定检索、聚合、去歧义和分析。Display Label 是否显示是后置 UI 决策，不能反向限制内部语义结构。

**案例：** App 1.0 暂时不在 Aha 卡片展示任何标签，内部仍可保存合法的`EVENT.DESSERT_EATING` Assignment，未来用户搜索“甜品”时仍能找到它。

#### 原则 2｜每个 Assignment 都必须有事实含义和 Evidence

Tag 不因“模型觉得像”或“对运营有用”就进入正式索引。它必须引用 current normalized assertion、source Facts／Claims、Evidence、Memory scope、assertability ceiling 与 taxonomy mapping version。

**案例：** 画面只有传统屋檐和石板路，没有可信地点证据，可以映射到合法的 broad context concept，例如“传统历史街区”；不能为了搜索价值直接标成“周庄”。

#### 原则 3｜Tag 表达记忆内容，不表达用户偏好

`POTTERY` Assignment 只表示这段 Memory 的核心内容与陶艺有关，不表示“用户喜欢陶艺”“用户是陶艺爱好者”或“应向用户推荐陶艺课程”。偏好必须由未来独立、可解释的多次行为信号合同产生。

**案例：** 用户路过陶艺店被 Auto 拍到一次，即使该内容最终成为合法 Chapter，也不能仅凭一个 Tag 建立`LIKES_POTTERY=true`。

#### 原则 4｜Tag Decision 必须执行，但 Assignment 可以为零

推荐每个准备发布的 Chapter／Aha 都产生一个可审计的`CanonicalTagDecision`；如果没有足够稳定、identity-level 的 canonical concept，合法结果应是零 Assignment，而不是强塞“生活、日常、回忆、其他”等低价值词。

**案例：** 一个短暂、难以辨认但仍可作为 Aha 的可见变化，Moment Line 有 Evidence，taxonomy 却没有安全概念。它仍可发布并通过时间、文本和 embedding 检索；Canonical Tag Decision 记录`NO_ELIGIBLE_CANONICAL_TAG`。

#### 原则 5｜Internal Assignment 与 Display Label 分开

内部检索需要多少个有区分度的 Assignment，与用户界面展示几个 Label 是两个问题。D5 后续分别设置 bounded internal assignment contract 与更窄的 display selection contract；不能继续沿用 X01“自由字符串、最多 4”同时承担两者。

**案例：** 一个 Chapter 内部可能合法保留 Activity、Scene 两个不同 facet 的索引关系，但卡片上可能只展示一个最有帮助的 Label，甚至不展示。UI 少一个 Label 不删除内部 Assignment。

#### 原则 6｜Chapter 与 Aha 分别判断，不自动继承

Aha 位于某个 Chapter 的时间线或场景中，不代表它自动复制 Chapter 的全部 tags；Chapter 也不能吞并 Aha 的独立 peak tag。两者共享事实时仍须通过各自 Memory scope 与 assignment relation。

**案例：** Chapter 是古镇 citywalk，中间 Aha 是切开桂花冰粉。Chapter 可拥有 citywalk／传统街区概念；Aha 的核心可以是甜品事件。Aha 是否另有古镇 context assignment 必须由 D5c 证据门决定，不能因为 parent Chapter 有就自动复制。

#### 原则 7｜一个 Concept 可以有多个词，但不能制造重复概念

同义词、拼写变体、语言翻译与搜索词映射到同一个 concept ID。只有定义和适用范围确实不同，才建立不同 concept，并保存清楚的 relation。

**案例：** `coffee / café / 咖啡 / 咖啡时间`不应自动成为四个 tags。若产品未来区分“咖啡饮品”和“咖啡馆场景”，应建立不同 facet／concept definition，而不是靠字符串猜。

#### 原则 8｜Canonical Tag 不独自承担全部检索

未来检索应是混合结构：Canonical Tags 提供稳定过滤和可解释聚合；Embedding 提供相近语义召回；时间、地点、人物／实体、Chapter-Aha relation 提供结构化限定；用户原文继续作为受保护文本索引。

**案例：** 用户搜索“那次做手工”，query mapper 可把“手工”映射到 broad concept，并结合 embedding 召回“陶艺体验”；系统不需要为了每种自然说法都给 Memory 再存一个 Tag。

#### 原则 9｜上游 Scene／Activity 分类不是自动的用户记忆标签

S04 的`OTHER_INDOOR`、`MOBILITY`等粗分类服务 Moment Formation，可能成为 D5 mapping 的证据输入，但不自动进入长期检索 taxonomy。D5 必须重新检查它是否稳定、identity-central、可被用户理解且有检索区分度。

**案例：** `OTHER_INDOOR`能帮助算法判断场景连续，却几乎没有用户检索价值；不能因为上游有这个 class 就在每个室内 Chapter 上保存“其他室内”。

#### 原则 10｜Tag 是带版本的系统判断，不冒充永久 Gold Label

Assignment 必须保留 taxonomy、mapper、Evidence、policy、Revision 与 audit。真实用户标签和人工 Gold 数据未来可用于评测／校准，但模型产生的 Tag 不能直接当训练真值。Taxonomy 调整必须显式迁移、保留 deprecated／replacement relation，不能静默重写历史含义。

**案例：** 未来把 broad`CRAFT`拆成`POTTERY / WOODWORK / TEXTILE`时，旧 Assignment 不能无证据批量猜成某个 child；可以继续保留 broad concept，或在现有 Evidence 足够时通过 versioned remap 得到更具体结果。

### 74.5 对“数据价值”的具体保护

如果 Canonical Tags 要成为长期数据资产，至少必须避免四种污染：

| 污染类型 | 错误做法 | 正确约束 |
|---|---|---|
| 词面污染 | 同一概念保存多个自由字符串 | stable concept ID + locale labels／aliases |
| 事实污染 | 看见建筑就猜具体古镇 | assertion ceiling + Evidence-backed mapping |
| 作用域污染 | Aha 自动继承 Chapter 所有 tags | 每个 Memory 独立 decision + exact scope |
| 偏好污染 | 记录过一次就判定用户喜欢 | content assignment 与 preference signal 分离 |

此外，Assignment 不能只是`memory_id + tag_string`。未来至少要知道：

- 这个概念以什么关系属于该 Memory；
- 它是 Chapter 还是 Aha 的 identity／core；
- 来源是哪些 current Facts／Claims／Evidence；
- 映射时采用哪个 taxonomy 和 policy；
- 当前是否 active、retained、replaced、deprecated 或 invalidated；
- 是否与 current active media 及 current Revision 兼容。

这样检索、数据分析和个性化才能区分“Memory 的主要活动是陶艺”“背景里出现陶艺物件”“用户主动拍了一张陶艺照片”“用户多次明确回看陶艺内容”，而不是把它们压成同一个布尔值。

### 74.6 推荐的最小职责对象（结构草案，字段未冻结）

~~~text
CanonicalConcept
  canonical_concept_id
  facet_ref
  semantic_definition
  parent_concept_refs[]
  allowed_assignment_relation_types[]
  taxonomy_version
  lifecycle_state
    ACTIVE | DEPRECATED | MERGED | SPLIT_PENDING_REVIEW
  replacement_or_successor_refs[]

CanonicalTagAssignment
  stable_memory_id
  memory_type                 # CHAPTER | AHA
  revision_ref
  canonical_concept_ref
  assignment_relation_type   # exact enum deferred to D5b
  normalized_assertion_ref
  source_fact_refs[]
  source_claim_refs[]
  evidence_refs[]
  assertability_ceiling
  active_projection_fingerprint
  taxonomy_and_mapper_versions
  assignment_state
  assignment_fingerprint
  construction_audit

CanonicalTagDecision
  stable_memory_id
  revision_ref
  eligible_assignment_refs[]
  selected_internal_assignment_refs[]
  rejected_or_omitted_candidate_audits[]
  decision_state
    TAG_ASSIGNMENTS_READY
    | NO_ELIGIBLE_CANONICAL_TAG
    | TAG_DECISION_CONTRACT_INVALID
  policy_versions
  decision_fingerprint

DisplayLabelMapping
  canonical_concept_ref
  target_locale_id
  target_locale_policy_ref
  display_label
  accessibility_label?
  label_version
  label_state
~~~

该草案的关键不是字段名称，而是三个对象必须独立：**概念是什么、某段 Memory 是否拥有它、用户在某种语言里看到什么词。** D5b–D5f 会逐项校正并冻结正式结构。

### 74.7 更多案例交叉检查

#### 案例 A｜古镇三小时漫步

多个 Window 分别出现石板路、牌坊、木雕、传统建筑和连续步行。它们可以共同支持一个 broad context／activity concept，但“周庄”仍需要可信地点 Evidence。

正确结果可能是稳定的`TRADITIONAL_HISTORIC_DISTRICT + CITY_WALK`类 Assignment；不是把`石板路、牌坊、木雕、屋檐、建筑、古镇、旅游`七个自由词全部塞进搜索索引。具体 facet 与层级留给 D5b。

#### 案例 B｜古镇里的现代奶茶店

古镇 Chapter 的中间短暂进入奶茶店，不会让整个 Chapter 自动变成`DINING`；它是否形成独立 Aha／Moment 已由 S07–S09 决定。D5 只能对已经选定的 Chapter/Aha 分别映射概念，不能靠 Tag 重新 split 或 merge。

#### 案例 C｜小猫碰倒纸杯

若 Aha peak 是猫咪碰倒纸杯，`CAT`或相应 event concept 是否为 core tag 要由后续 taxonomy 和 mapping gate决定；`调皮`是受控 wording permission，不是事实型 Canonical Tag，也不能形成“用户喜欢猫”的偏好结论。

#### 案例 D｜只有模糊室内片段

Memory 可以有可靠时间、媒体和一条安全 Moment Line，但没有稳定的 identity-level concept。结果是零 canonical assignment，而不是为了报表完整率填`INDOOR / DAILY_LIFE / OTHER`。检索仍可使用时间、文本与 embedding。

#### 案例 E｜用户手写“和妈妈喝咖啡”

用户文字原样保护并可进入 user-authored text search；它不能未经独立确认就把`MOTHER_RELATION`或`COFFEE`写入系统 canonical assignment。若用户确认／其他合法 Facts 满足 D5c，才由独立 Tag Decision 建立对应关系。

#### 案例 F｜Label 改名

中文 UI 把“城市漫步”改成更自然的“逛街散步”。如果 concept definition 没变，只更新 Display Label；历史检索 ID、Assignment、Chapter Story 和 Aha Moment Line 都不改。

### 74.8 成本与效率判断

按上述边界，Canonical Tag 不应成为高成本环节：

1. 它消费已经存在的 Facts、Claims、Embedding 与 taxonomy，不新增抽帧、上传、Raw/HQ 或视觉模型调用；
2. 优先使用 versioned deterministic mapping、轻量 classifier 或 embedding-to-concept retrieval，再对少量歧义项做有界验证；具体 router 留给后续；
3. 同一`fact/projection fingerprint + taxonomy/policy version`可以缓存 Tag Decision；重复打开 App 不重算；
4. Display Label 是小型 locale mapping，不应调用自由 Writer，也不复制媒体；
5. taxonomy migration 主要重算 metadata refs／search index，不应重新生成 Chapter/Aha membership 与自然语言；
6. 最大风险不是单次算力，而是错误或不稳定 tags 长期污染检索、统计和个性化，因此宁可合法为零，也不追求虚假的 100% tag coverage。

### 74.9 D5 后续拆分路径

~~~text
D5a  Product role & data meaning
     “Tag 代表什么，不代表什么”

D5b  Concept registry / facets / hierarchy
     “概念目录怎样组织，如何避免平铺与重复”

D5c  Evidence-to-concept eligibility
     “什么证据允许哪个具体或 broad concept”

D5d  Assignment selection / ranking / internal count
     “一个 Chapter/Aha 内部到底保留哪些、多少个”

D5e  Display Label / localization / visible selection
     “用户看到什么词、几个、不同语言怎么显示”

D5f  Continuity / taxonomy migration / invalidation
     “后续 Sync 或概念升级时什么时候保留、替换、迁移”

D5g  Retrieval / data-value / cost cross-check
     “搜索、聚合、个性化输入和成本是否真正闭环”
~~~

每个阶段都必须带案例，完成后再对整个 D5 做 closeout cross-check。

### 74.10 已确认的产品边界

用户确认以下六点，作为 D5a 冻结基础：

1. **Canonical Tag 是内部、语言无关、稳定且有 Evidence 的记忆索引；Display Label 是独立的可选用户展示层。**
2. **每个 Chapter／Aha 必须运行 Tag Decision，但允许零 Assignment；不能为了覆盖率强塞泛化废词。**
3. **Tag 只描述 Memory 内容，不直接代表用户兴趣／偏好。**
4. **Chapter 与 Aha 分别判断，不自动互相继承 tags，也不允许 D5 反向改变 membership。**
5. **Canonical Tags 与 Embedding、时间、地点、relation、用户原文共同组成未来混合检索，不要求 Tag 承担所有语义召回。**
6. **UI 展示数量不限制内部索引；具体 taxonomy、facet、内部数量与展示数量分别留给 D5b–D5e。**

以上边界已经冻结。下一步进入 D5b，先讨论“Flat Tag List 还是 Faceted Taxonomy”，再讨论 Activity／Scene／Place／Entity／Event／Theme 中哪些维度真正适合 Diary One V1。

### 74.11 D5a 冻结记录

**冻结日期：** 2026-08-29

**用户确认：** 确认 Canonical Tag 关乎未来整个记忆检索体系与数据价值，并同意 74.10 六项产品边界。

**冻结范围：** 74.1–74.10 的术语分层、四层责任结构、十项产品原则、数据污染边界、结构草案的职责拆分、案例、成本方向、D5 分阶段路径，以及六项确认结论。

**不在冻结范围：** 具体 taxonomy／facet／concept 清单、层级深度、内部 tag 数量、Display Label 数量与 UI、搜索排序、Embedding 模型、个性化权重、用户标签、Production schema/provider，以及隐私／retention／对外数据政策。

**变更规则：** 只有真实检索失败样本、taxonomy migration 反证、数据质量评测或新的显式 versioned checkpoint 才可重开；不得由 UI 数量、自由 Writer、模型版本或运营临时词表静默改变 Canonical Tag 的数据含义。

## 75. S11-D5b1｜Taxonomy Shape: Flat List vs Facets vs Full Knowledge Graph

**状态：CONFIRMED / FROZEN TAXONOMY SHAPE / REGISTRY PRINCIPLES 1–6 + BOUNDARIES 1–5 LOCKED / D5b NOT FROZEN / FACET MEMBERSHIP NOT YET LOCKED**

### 75.1 本检查点只决定底层形状

D5a 已冻结“Tag 代表什么”。D5b1 只选择 concept registry 的总体结构，不在本节列完所有概念，也不冻结每个 Memory 的 tag 数量。

要解决的核心问题是：

> “陶艺、室内、周庄、妈妈、生日、猫咪、下午”这些信息，是否都应该作为同一种 Tag 放在一个数组里？

我的判断是：**不应该。** 它们分别表达活动、环境、真实地点实体、人物实体／关系、场合、核心对象和时间。混为一层以后，检索可以勉强工作，但聚合、统计、版本迁移和个性化都会逐渐失真。

### 75.2 三种结构比较

| 方案 | 结构 | 优点 | 主要问题 | 适合 Diary One V1？ |
|---|---|---|---|---|
| A. Flat Tag List | 所有词都放进一个字符串／ID 数组 | 最快实现、UI 容易展示 | 活动／地点／人物／对象混在一起；同义词重复；无法解释统计；数量上限互相挤占 | 不推荐 |
| B. Controlled Faceted Taxonomy | Canonical Concepts 按稳定语义维度组织；实体、时间等另有专门索引 | 可解释、可扩展、便于混合检索与数据分析；复杂度可控 | 需要先定义 facet 边界与 mapping gate | **推荐** |
| C. Full Knowledge Graph | 把人物、地点、事件、对象及所有关系都建立完整图谱 | 表达力最强 | V1 工程、实体消歧、关系验证与迁移成本过高；容易在证据不足时过度建模 | 现在不推荐，保留演进接口 |

推荐 B，不是因为知识图谱没有价值，而是 Diary One 当前应先建立**少量稳定概念维度＋专门实体索引＋已有 Claim／relation graph**。这已经能支持高价值检索，同时避免把 S11 变成一个试图完整理解现实世界的无限 ontology 项目。

### 75.3 推荐的总体数据形状

~~~text
Memory: Chapter or Aha
│
├─ Canonical Facet Assignments
│    ├─ Activity candidates
│    ├─ Setting / Context candidates
│    ├─ Central Subject candidates
│    └─ Occasion candidates
│         # 最终 V1 facets 留给 D5b2 冻结
│
├─ Entity Links
│    ├─ known person / relationship refs
│    ├─ known pet refs
│    ├─ exact place / venue refs
│    └─ other stable named-entity refs
│
├─ Deterministic Metadata
│    ├─ user-local day / time range
│    ├─ Chapter vs Aha
│    └─ capture / lifecycle metadata
│
├─ Claims + Relations
│    └─ exact actions, changes, details and grounded relations
│
└─ Embeddings + protected searchable text
     └─ long-tail semantic recall and user wording
~~~

这里的四个 facet 只是 D5b2 的候选，不在 D5b1 先行冻结。D5b1 要冻结的是：**不同类型的信息使用不同、可组合的索引结构，不再全部冒充 Canonical Tag。**

### 75.4 为什么 Exact Place／Person／Pet 不应变成普通 Tag

#### Exact Place

`周庄古镇`是一个真实地点实体，可能有 place ID、坐标、别名和行政层级；`传统历史街区`是一个可复用的环境概念。两者可以共同支持检索，但数据身份不同。

~~~text
PlaceEntity: ZHOUZHUANG_ANCIENT_TOWN
Setting Concept: TRADITIONAL_HISTORIC_DISTRICT
Activity Concept: CITY_WALK
~~~

如果把全球每一家店、每个景区都加入 Canonical Concept taxonomy，concept registry 会无限增长，地点改名、同名与关店也会污染 tag migration。正确方式是 Exact Place 进入 place/entity index，地点类型和环境语义进入 Canonical Facet。

#### Person / Relationship

`妈妈`不是一个适合所有用户共享的 canonical tag：它是当前用户与某个实体之间的受保护关系。应保存 verified person/entity link 与 relationship fact，而不是把“妈妈”当作通用内容分类。

#### Pet

“猫”可以是 class-level Central Subject concept；“豆包”则应是用户确认的具体 pet entity。搜索“猫咪记忆”可使用 Subject concept，搜索“豆包”使用 entity link；两者不应互相覆盖。

### 75.5 推荐的 Registry 与 Runtime 原则

#### 原则 1｜Runtime 使用受控 Concept Registry

线上模型只能：

- 选择 active concept；
- 选择已定义的 safe parent concept；
- 或返回无合法 concept。

它不能在每次处理时自由创造新 Tag。新 concept 可以由真实数据发现流程提出，但必须离线评审、定义、去重、版本化后才能进入 active registry。

**案例：** 模型觉得“桂花冰粉时光”很有感觉，也不能临时创建该 concept；它可以使用已经存在且证据支持的 dessert／food-related concept，或不分配。

#### 原则 2｜每个 Concept 必须有明确 Facet

不能只有`concept_id=COFFEE`而不知道它表示饮品对象、喝咖啡活动还是咖啡馆场景。Facet 和 semantic definition 共同决定 Assignment 的含义。

**案例：** `SUBJECT.COFFEE_DRINK`、`ACTIVITY.DRINKING_COFFEE`和`SETTING.CAFE`可以是三个不同概念；画面只看见杯子时不能自动得到后两者。

#### 原则 3｜只存最具体且被支持的 Assignment

若 Evidence 足以支持 child concept，只保存该最具体 Assignment；父级用于 query-time ancestor expansion，不把 child、parent、grandparent 全部写成三个独立 Tag。

~~~text
assigned: ACTIVITY.POTTERY_WHEEL_THROWING
query expansion: POTTERY_WHEEL_THROWING → POTTERY → CRAFT
~~~

如果 Evidence 只能支持 broad`CRAFT`，就只分配 broad concept，不能猜 child。

**案例：** 用户搜“手工”时可以通过父级扩展找到拉坯记忆；内部不必同时保存“拉坯、陶艺、手工、创作”四个重复 Assignment。

#### 原则 4｜`UNKNOWN / OTHER`是处理状态，不是长期内容概念

上游可使用`UNKNOWN / OTHER_INDOOR / OTHER`保证分类器总有合法输出，但它们默认不进入用户长期检索索引，也不计入用户画像。

**案例：** 模糊室内片段可以保持无 canonical assignment；不能让用户以后搜索结果里出现大量“其他室内”。

#### 原则 5｜长尾动作留给 Claims／Embedding，不无限扩张 Taxonomy

不是每个 peak 动作都需要一个永久 concept。可复用、稳定、有明确检索价值的概念进入 taxonomy；一次性的细动作继续保存在 Claims、Moment Line 与 embedding 中。

**案例：** “猫咪碰倒纸杯”可以通过 Subject=`CAT`、实际 Moment Line 和 embedding 被找到；V1 不必立即建立`CAT_KNOCKING_OVER_PAPER_CUP`概念。

#### 原则 6｜体系允许演进，但不能静默改义

V1 可以采用较浅、受控的 hierarchy，并为未来 graph relations 留 refs。概念 label 可以更新；semantic definition 材料改变时必须新建 concept 或显式 versioned migration，不能让同一 ID 今天代表“饮品”、明天代表“咖啡馆活动”。

### 75.6 Faceted 不等于把用户搜索复杂化

用户仍然可以输入一句自然语言，检索系统在后台拆解：

#### 查询 A｜“我在周庄散步的那次”

~~~text
周庄       → exact PlaceEntity index
散步       → Activity concept / alias expansion
那次       → Memory retrieval intent
结果       → place filter + activity index + embedding rerank
~~~

#### 查询 B｜“和妈妈喝咖啡”

~~~text
妈妈       → verified user-specific person/relation index
喝咖啡     → Activity concept
结果       → entity relation + activity + time/relevance ranking
~~~

#### 查询 C｜“豆包调皮的瞬间”

~~~text
豆包       → verified pet entity
猫         → Subject concept, if useful
调皮       → protected wording / semantic query signal, not factual Tag
具体动作   → Moment Line / Claim / embedding
~~~

Facet 是后台保证数据干净的结构，不要求用户学习筛选器，也不要求 App 首版展示这些技术类别。

### 75.7 对数据统计与个性化的直接影响

Flat list 中看到`周庄、古镇、散步、旅行、建筑、妈妈、下午`，系统很难知道每个词能否同等计数。Faceted architecture 可以明确：

- Activity Assignment 可以统计“记录过哪些核心活动”；
- Setting Assignment 可以统计“哪些环境反复出现”；
- PlaceEntity 可以按具体地点聚合；
- Person/Pet Entity Link 可以检索共同记忆，但继续受用户确认与权限约束；
- Occasion 可以形成生日／节庆等高价值记忆入口；
- Time 继续由 D3 metadata 处理；
- 任何一项都不自动等于用户偏好，偏好模型仍需独立证据。

这使后续数据分析能够比较同类关系，而不是把“下午”和“陶艺”放在同一个 tag frequency 表里。

### 75.8 成本与工程复杂度

| 结构 | 初期成本 | 长期成本 | 主要风险 |
|---|---:|---:|---|
| Flat list | 低 | 很高 | 清洗、同义词、迁移与错误画像不断累积 |
| Faceted taxonomy | 中 | 可控 | 前期需要严谨定义 facet／concept 边界 |
| Full graph | 高 | 高 | 实体消歧和关系验证超过 V1 需求 |

Faceted 方案不会增加媒体上传或视觉理解成本。主要新增的是小型 concept registry、mapping validator、metadata index 与 migration audit；这些投入直接保护后续检索和数据价值。相比先生成自由标签、积累大量历史数据后再清洗，前置定义更便宜。

### 75.9 与 A2／B2 既有`Exact Place → CANONICAL_TAG eligible`的对齐

A2 8.10 的案例曾把“可靠西塘定位”记为`TITLE/STORY/TAG eligible`；B2 14.7 也允许 provenance 合法的用户确认地点进入`CANONICAL_TAG`surface。这些条款冻结的是：**可靠 exact place 不能因为不是像素事实就失去用户表达与索引资格。** 当时 D5 尚未区分 Canonical Concept 与 Exact Entity，因此`CANONICAL_TAG`承担了较宽的“可索引 metadata surface”候选含义。

D5b1 建议做一个存储责任细化，而不降低能力：

1. exact place Fact 继续可以依法进入 Title／Story；
2. 在 D5 检索输出中，它形成`PlaceEntityIndexLink`并保留同样的 Evidence／Claim／Revision 验证；
3. broad place type／environment，例如`HISTORIC_TOWN / TRADITIONAL_HISTORIC_DISTRICT`，仍由 Canonical Concept／Setting Facet 表达；
4. 检索时 PlaceEntity 与 Canonical Facets 可以联合过滤；
5. 若 App 后续显示“周庄”location chip，它来自 verified PlaceEntity Display Name，而不是伪装成普通 Canonical Tag Label；
6. 不为全球每个景点、店铺和地址创建 taxonomy concept。

因此，这是`CANONICAL_TAG eligibility umbrella → typed D5 index eligibility`的类型细化，不是把地点从检索中删除。用户确认 D5b1 后，A2、B0、B2、C2 与 S11 输出边界已同步增加明确 contract-alignment amendment；旧字段名仅为兼容 umbrella，不再被解释成 exact place 必须成为 taxonomy concept。

**案例：** “周庄古镇漫步”可以同时由`PlaceEntity=周庄古镇`、`Setting=传统历史街区`和`Activity=citywalk`支持。搜“周庄”走实体索引，搜“古镇”走 Setting，搜“散步”走 Activity；三条路径可以组合召回同一 Chapter。

### 75.10 D5b1 已确认的五点

1. **Diary One V1 采用 Controlled Faceted Taxonomy，不采用自由 Flat Tag List，也不在当前建设完整 Knowledge Graph。**
2. **Canonical Facets、Exact Entity Links、时间／结构 metadata、Claims／Embedding 分层保存，但可在检索时组合。**
3. **Runtime 只能选择已注册 concept／safe parent 或返回零结果；新 concept 走离线、versioned review。**
4. **Assignment 默认只保存最具体且有证据的 concept；父级通过 taxonomy expansion 检索，不重复占 tag 名额。**
5. **UNKNOWN／OTHER、长尾一次性动作、精确地点／人物／宠物身份不强塞进普通 Canonical Tag。**

以上五点已经冻结。下一检查点 D5b2 再逐项决定 V1 Facet Set：Activity、Setting、Central Subject、Occasion 是否进入；Place、Person/Pet、Time、Theme、Mood、Capture Type 分别应该放在哪一层。

### 75.11 D5b1 冻结记录

**冻结日期：** 2026-08-29

**用户确认：** 同意 Controlled Faceted Taxonomy、typed Entity Links、runtime closed registry、most-specific supported assignment／query-time parent expansion，以及 UNKNOWN／OTHER／长尾动作／exact entity 不强塞普通 Canonical Tag。

**冻结范围：** 75.1–75.10 的三方案比较、分层数据形状、Canonical Facets 与 Exact Entity／metadata／Claim／Embedding 边界、六项 registry/runtime 原则、查询案例、数据统计与成本判断、A2/B0/B2/C2 exact-place alignment，以及五项确认结论。

**不在冻结范围：** 最终 V1 facet set、概念清单、hierarchy 深度与 parent policy、Entity resolution 实现、internal/display 数量、搜索排序、完整 Knowledge Graph、Production schema/engine，以及真实数据校准。

**上游对齐已应用：** 历史`CANONICAL_TAG`候选字段继续作为 D5 index umbrella；exact entity 不失去资格，而是在 D5 物化为 typed`EntityIndexLink`。该修订不新增 Evidence、不会把地点从检索中删除，也不改变 Title／Story permission。

**变更规则：** 只有真实检索／聚合失败、entity-vs-concept 反例、taxonomy migration 数据或新的显式 versioned checkpoint 才可重开；不得由 UI、模型自由词或短期运营标签静默退回 Flat Tag List。

## 76. S11-D5b2–D5g｜Canonical Memory Index Closeout

**状态：FROZEN BY CANONICAL V1.22**

详细 normative contract 已汇总到 `CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md`。本节记录从 D5b1 到 D5 closeout 的最终决定，避免历史“下一步”被误读为当前 OPEN。

### 76.1 D5b2｜V1 Facet Set

V1 使用四个 Facet：

~~~text
ACTIVITY
SETTING
CENTRAL_SUBJECT
OCCASION
~~~

Exact Place／Person／Pet／Venue 进入 typed Entity Link；Time／Memory Type／Capture Type 进入 deterministic metadata；Theme 由 query-time hybrid retrieval 组合；Mood／Preference 没有独立事实合同时不进入 Canonical Tag。

**案例：** “周庄古镇漫步”使用 CITY_WALK＋HISTORIC_DISTRICT，并把周庄保存为 PlaceEntity；“下午”不是 Tag。

### 76.2 D5c｜Assignment Quality & Count

每个 Memory 必须执行 Tag Decision，但允许零结果。V1 internal baseline 为 0–4 项、每 Facet 0–1；非空时恰好一个 PRIMARY，其余 SECONDARY。只分配最具体且有 STRONG／可独立成立的 MODERATE support 的 active concept。

**案例：** 古镇 Chapter 途中出现普通茶杯，不获得 FOOD_OR_DESSERT；它不决定 Chapter 身份。

### 76.3 D5d｜Display Label

算法最多输出 0–2 个 registry-derived Display Label Candidate；它们不是自由 Writer 字符串，也不要求 App 必须展示。UI 数量不反向限制内部 Assignment。

**案例：** 内部可有 CITY_WALK、HISTORIC_DISTRICT、ARCHITECTURE、TRAVEL_OUTING 四项，当前中文交接候选只给“城市漫步／古镇街区”。

### 76.4 D5e｜Chapter/Aha 与 Revision

Chapter 与 Aha 分别决策、不自动继承。Claim／active projection／semantic definition 未变时 exact retain；label 更新不等于 Assignment 改变；concept split 时不猜 child。

**案例：** 古镇 Chapter 与猫碰倒纸杯 Aha 共存时，Aha 可为 CAT/CAFE，不继承 Chapter 的旅行标签。

### 76.5 D5f｜Registry & Migration

Runtime 使用 closed, versioned, acyclic registry；模型只能选 active concept、safe parent 或零结果。`UNKNOWN/OTHER`不写入长期索引；semantic 改义必须新 ID 或显式 migration。

**案例：** 只能证明“手工”时分配 CRAFT，不能猜 POTTERY；明确拉坯后才能使用更具体 child。

### 76.6 D5g｜Retrieval / Data Value / Cost

检索组合 Entity、Canonical Facet、时间／结构 metadata、Claim／protected text 与 embedding。Tag frequency 只表示记录内容，不直接生成偏好。D5 不新增媒体/VLM 调用，成本主要是 registry mapping、metadata index 与 audit。

## 77. S11-D6｜Writer Runtime & Cost Envelope

**状态：FROZEN BY CANONICAL V1.22**

1. Writer 只读取 B3-validated plan、current Claims/relations/qualifiers、active media limitations、locale/voice policy 与 protected-text instructions。
2. 输出必须是 structured surface artifact，保存 span→Claim/relation/tone refs 与 provider/model/prompt/parameter/token/latency/retry/cache/cost provenance。
3. 继承 D4c2 四级单调简化；每个适用 attempt class 最多一个 logical provider call、只落一个 canonical draft。
4. exact fingerprint 命中 cache；transport retry 有界且不能创造第五个语义状态。
5. provider/transient/budget failure 进入 HOLD 或合法 prior retain，不能生成万能句，也不能改变 Day State。
6. Tag、Time Label、continuity aggregation 与 E validator 默认不调用 Writer。

**案例：** 古镇 Story 第一次 provider timeout 时保持 retry/HOLD；不能用“记录下美好时光”冒充完成。

## 78. S11-E｜Actual-language Verification

**状态：FROZEN BY CANONICAL V1.22**

E 在实际文字生成后验证：

- 每个事实 span、关系词、数量词、先后词、否定词和程度词；
- 跨句 referent、隐含顺序与 Chapter/Aha reservation；
- Story 1–2 句、Aha 单峰≤20 中文可见字符；
- controlled identity echo、Tag/Entity/Time 分工；
- protected user text；
- locale release contract；
- light-affect narrow permission 与 unsupported user-state words。

终态：`SURFACE_VERIFIED / SURFACE_REWRITE_SAME_PLAN_REQUIRED / OWNER_REPLAN_REQUIRED / NARRATIVE_CONTENT_BLOCKED / NARRATIVE_CONTRACT_INVALID`。只有第一项进入 S12。

**案例：** “小猫调皮地碰倒了纸杯”只有动作有 Evidence、CAT subject 成立且使用 versioned narrow permission 时通过；“留下难忘一刻”没有用户确认时阻断。

## 79. S11-F｜Full Cross-check

**状态：PASSED / FROZEN BY CANONICAL V1.22**

已检查：

1. S09 membership 不被 S11 改变；
2. V1.20 same-story／embedded-distinct reservation 一致；
3. S10 Primary/Fallback/D1/Hero activation 后 affected revalidation 闭环；
4. Facts、Claims、composition、plan、actual spans 五层不互相冒充；
5. D3 Time Label 不被 D5/Writer 接管；
6. exact entities 不污染 taxonomy；
7. Tag 不冒充 preference；
8. provider failure 不冒充 EMPTY_DAY；
9. S11 只交 `READY_FOR_S12`，不自称 publish-ready；
10. current Chinese profile 与海外 locale release 分离。

旅行、家庭生日、手作、宠物、美食、普通上班、稀疏高光、多次 Sync、用户自写标题与海外 locale 十类画像均未发现需要重开 S00–S10 的冲突。

## 80. S11 最终冻结范围

**FROZEN：** A–E 完整主干、current-Chinese Title/Story/Time/Aha、D5 四分面索引、typed Entity Link、D6 runtime/cost envelope、actual-language verification、cross-revision/activation revalidation 与 F closeout。

**显式 deferred / OPEN：**

- D2e Title failure／用户 clear 后 Production presentation；在真实测试前不自动删除或阻断 Chapter；
- English/其他 locale 的数量、折行、可访问性、eval set 与 release gate；
- 真实 concept/threshold/provider/cost/latency calibration；
- 用户文字除 Title 外的 App presentation；
- embedding/search/personalization/full graph；
- privacy/ethics/retention/governance。

以上不推翻 S11 架构冻结，但阻止对相关 locale、成本数字或云端 Production readiness 作出未经验证的承诺。

## 81. S11 Freeze Record

**冻结日期：** 2026-08-29

**Canonical 文件：** `CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md`

S11 到此 design closed。后续 S12 只能验证 exact S11 artifacts，不能自行删 Claim、改文字、造 Tag 或重建用户体验。真实数据反例必须通过新的 versioned checkpoint 修订对应窄合同。
