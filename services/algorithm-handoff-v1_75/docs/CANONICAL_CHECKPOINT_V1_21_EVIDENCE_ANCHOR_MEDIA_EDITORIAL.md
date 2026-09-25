# Diary One Canonical Checkpoint V1.21 — S10 EvidenceAnchor & Media Editorial

**状态：** FROZEN
**冻结日期：** 2026-08-27
**决策来源：** 用户逐项确认 S10-A1–D4、V1.20 Chapter/Aha narrative independence 接入、S10-E 全链路检查结论，并最终确认冻结
**作用范围：** S10 Content Beat、EvidenceAnchor、媒体格式与精确源计划、Chapter 2–5 项编辑、顺序、Hero、Fallback、发布前单成员容灾、HQ request tiers、Aha 单媒体与 Chapter/Aha render distinctness
**继承关系：** 继承 V1.20–V1.1 与 V1.0 未被本文覆盖的规则；本文不改变 S09 membership、Day State、Preview/Final Memory 数量或 V1.20 narrative independence
**验证依据：** [S10 Working V0.1](S10_EVIDENCE_ANCHOR_MEDIA_EDITORIAL_CONSOLIDATED_WORKING_V0_1.md)、[S10 End-to-End Cross-Check](S10_END_TO_END_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_1.md)、[A2 Cross-Check](S10_A2_EVIDENCE_ANCHOR_INTERNAL_CROSS_CHECK_V0_1.md)、[B Cross-Check](S10_B_MEDIA_DECISION_INTERNAL_CROSS_CHECK_V0_1.md)、[C Cross-Check](S10_C_CHAPTER_EDITORIAL_INTERNAL_CROSS_CHECK_V0_1.md)、[D4 Cross-Check](S10_D4_AHA_FINAL_MEDIA_INTERNAL_CROSS_CHECK_V0_1.md)
**明确不覆盖：** S11 文案与 Claim 写法、S12 完整 validator、S13 上传/渲染工程数值、任意时长 Manual Window 规划、App UI、Firmware/SDK、共享状态文件、隐私/伦理/治理专项

## 1. 冻结结论

S10 只把 S09 已选中的 Memory 转换成真实、可追溯、数量有界的最终媒体呈现计划。它不重新决定用户当天有哪些 Chapter/Aha。

~~~text
S09 SelectedMemorySet + S10HandoffEnvelope
→ A1 grounded Content Beat inventory
→ A2 exact EvidenceAnchor resolution
→ B legal format + exact source + immutable MediaDecision routes
→ C Chapter final set + chronology + static Hero
→ D4 Aha single media + cross-memory render reconciliation
→ D1/D2 bounded runtime-resilience metadata
→ D3 coalesced HQ request manifest
→ S11 grounded narrative
→ S12 final validation
→ S13 selected-source materialization / export
~~~

冻结的核心产品结果：

1. Chapter 标准展示 3–5 个精选媒体项；只有通过严格门控的 Compact Chapter 可以展示 2 项；0–1 项不可发布；
2. Aha 恰好展示 1 个 PHOTO 或 LIVE_2S，不是微型 Chapter，也没有独立 Hero；
3. 每个用户可见位置都必须对应一个 grounded Content Beat、一个精确 EvidenceAnchor 与一个可执行 MediaDecision；
4. 先确定真实内容与证据，再选 PHOTO/LIVE_2S/VIDEO_5S；画面漂亮不能覆盖事实、权限或核心意义；
5. S10 正常路径只请求最终 active media 所需的 HQ source，Fallback 与备用 Hero 默认只有 metadata 成本；
6. 用户完成 Sync 后，S10/S13 不得新增第二次上传确认或素材选择交互；
7. 媒体不足、UNKNOWN、transient、contract invalid 与 runtime terminal failure 必须分流，不能都解释为“换一个 Memory”；
8. 用户只看到完整、原子发布的 Revision，不看到空卡片、缺图、半成品或内部 Fallback 尝试。

## 2. 权限与阶段边界

### 2.1 S10 可以做什么

- 在当前 selected Memory scope 内识别展示意义不同的 Content Beats；
- 从 S09 whitelist 的 KEEP Evidence 中选择 Anchor；
- 为 Anchor 选择合法且最小充分的媒体格式；
- 在一个 Chapter 内选择最终正文集合、顺序与 Hero；
- 为 terminal failure 预声明有界 Fallback 与 survivor metadata；
- 输出 HQ source request intent 与精确消费范围。

### 2.2 S10 不可以做什么

- 搜索全天 RawAsset 或把未选 Candidate 拉回；
- 新增、删除、替换 Chapter/Aha membership；
- 把 CONTEXT_ONLY 或 DROP 恢复为最终媒体；
- 新建事实、改写 CandidateContentUnit、推断无 Evidence 的情绪或结果；
- 重新做 S06/S07 Moment segmentation；
- 因封面漂亮、媒体可用或成本更低而改变 Memory identity；
- 读取、上传、存储或渲染 HQ source；
- 决定 App 后台上传时间、目的地、网络/电量条件或存储生命周期。

### 2.3 Evidence role

~~~text
KEEP
→ may become Content Beat evidence and EvidenceAnchor

CONTEXT_ONLY
→ may explain place, continuity, boundary or order
→ anchor_eligible = false

DROP
→ audit/fact retention only
→ never restored by S10
~~~

## 3. S10-A1｜Content Beat

### 3.1 定义

`Content Beat` 是一个已选 Memory 内具有独立展示意义、原则上值得占据一个用户可见媒体位置的内容部分。它不是 RawAsset、Window、Frame、时间点或格式。

发现与编辑必须分开：

~~~text
enumerate all grounded Beat candidates
→ resolve Anchor and MediaDecision
→ choose final Chapter 2–5 set or one Aha position
~~~

不能在 A1 阶段为了“每章 3–5 项”提前删到五个，也不能在只有两个真实 Beat 时制造第三个。

### 3.2 Same / Distinct / Unresolved

上游 CandidateContentUnit 的独立性默认保留。只有明确的 `presentation redundancy` Evidence 才能把多个 ContentUnits 合并为一个 Beat。

~~~text
SAME_PRESENTATION_BEAT
DISTINCT_PRESENTATION_BEAT
PRESENTATION_RELATION_UNRESOLVED
~~~

判定必须同时检查：

- same evidence：相同主体/动作/结果/展示作用、删除其中一个不损失用户理解；
- distinct evidence：不同阶段、实例、互动、转折、结果、内容侧面或独立贡献；
- evidence limitation：风格、地点、时间距离或 embedding 只能提名关系，不能单独决定。

关系不具有无条件传递性。A≈B、B≈C 不代表 A≈C；多项合并前必须检查组内兼容，禁止链式误合并。

### 3.3 长 Manual 边界

同一长 Manual 只有在上游已经形成多个、内容与时间均不同的合法 CandidateContentUnit 时，才可贡献多个 Beat。S10 不凭 16 秒、73 秒或其他时长自行切 Window。

## 4. S10-A2｜EvidenceAnchor

### 4.1 定义与三种合法目标

`EvidenceAnchor` 是“这个 Beat 应落在原素材哪个精确位置”的可追溯地址，不是最终 render，也不意味着 HQ 已存在。

~~~text
STILL_ASSET
FRAME_TIMEPOINT
EVIDENCE_SUPPORTED_INTERVAL
~~~

- Manual Photo 使用 `STILL_ASSET`，不伪造 `0.0s` 视频时间；
- 视频静态位置使用实际解码时间的 `FRAME_TIMEPOINT`；
- 动作/变化使用已有 temporal Evidence 支持的单一 RawAsset interval；
- 不跨文件、跨 Photo/Video 或跨 Memory 拼接一个 Anchor。

### 4.2 BeatAnchorRequirement

每个 Beat 在比较候选前固定：

~~~text
STATIC_SUFFICIENT
TEMPORAL_HELPFUL
TEMPORAL_REQUIRED
UNKNOWN
~~~

静态帧不能单独证明帧间动作。吹灭蜡烛只有结果帧时，只能支持“蜡烛已熄灭”，不能假装完整记录吹灭过程。

### 4.3 Anchor 硬资格与比较顺序

Anchor 必须来自当前 Revision、selected Memory、Beat scope、KEEP Evidence 与 S09 whitelist，并具有完整 RawAsset/Window/Frame/source-offset provenance。

候选先通过 presentation usability，再按下列顺序分层比较：

~~~text
1 grounded core support
2 semantic representativeness
3 beat centrality
4 subject clarity / interpretation ambiguity
5 temporal completeness when applicable
6 technical usability
7 stability / motion value when applicable
8 stable deterministic tie-break
~~~

不使用能补偿硬失败的单一 overall score。高画质不能让外围内容超过核心内容；严重损坏、主体不可辨或 source mapping 不可靠也不能因意义重要而通过 usability floor。

### 4.4 Resolution 与 Fallback

每个 Beat 最终输出：

~~~text
0 or 1 Primary EvidenceAnchor
0–2 ordered Fallback Anchors
one resolution state
~~~

状态为：

~~~text
ANCHOR_RESOLVED
ANCHOR_RESOLVED_DEGRADED
ANCHOR_UNRESOLVED
NO_USABLE_ANCHOR
~~~

Fallback 必须来自同一 Beat、独立满足最低语义 floor，并优先选择不同 source/failure domain 的近似等价候选；不能为故障独立牺牲真实性。

### 4.5 语义资格与 HQ readiness 分离

~~~text
semantic_anchor_eligible = true | false

hq_source_handle_status =
  AVAILABLE
  | NOT_YET_MATERIALIZED
  | UNAVAILABLE
  | UNKNOWN
~~~

`NOT_YET_MATERIALIZED` 不等于不可用；`AVAILABLE` 也不代表内容更好。UNKNOWN 不得当作 0、平均值或自动失败。

## 5. S10-B｜MediaDecision

### 5.1 格式资格

~~~text
Chapter: PHOTO | LIVE_2S | VIDEO_5S
Aha:    PHOTO | LIVE_2S
~~~

先检查格式能否真实表达 Anchor，再按最小充分原则选择：

- PHOTO 已足够时，不为“更高级”自动选择动态；
- LIVE_2S 只有在两秒连续性有实质体验增量时优先；
- VIDEO_5S 只有在五秒过程比两秒 Live 有实质新增时用于 Chapter；
- Aha 永远禁止 VIDEO_5S；
- 不设置动态素材比例或格式配额。

### 5.2 Exact Media Source Plan

每条 Route 必须绑定一个精确、可执行的 source plan：

~~~text
EXACT_STILL_SOURCE
EXACT_FRAME_SOURCE
EXACT_INTERVAL_SOURCE
~~~

区间必须落在 Anchor/Evidence 支持范围与单一 RawAsset 内。不得为了凑 2 秒/5 秒跨入另一个 Beat、无 Evidence 区域或 source 边界。

### 5.3 Primary、Fallback 与 conditional

每个合法 Beat 恰好产生一个 MediaDecision；一个 MediaDecision 代表一个用户可见内容位置：

~~~text
1 Primary Route
0–2 ordered Fallback Routes
~~~

Primary＋Fallback 仍只计一个媒体位置。Conditional Primary 必须至少有一条非条件、同核心、claim-compatible Fallback；否则不能成为 resolved decision。

已知不可行 Route 在 MediaDecision 首次定稿前移除并重建 Route order；运行时只能激活预声明 Route，不能新增第四条、重新找 Anchor 或搜索素材。

### 5.4 失败分类

~~~text
KNOWN_ROUTE_FAILURE
TRANSIENT_OPERATIONAL_FAILURE
UNKNOWN_FAILURE_STATE
CONTRACT_INVALID
~~~

- known failure 才允许检查下一预声明 Route；
- transient/UNKNOWN 进入 retry/HOLD；
- contract invalid 进入 BLOCK；
- `PRESENTATION_NARROWING` 必须传给下游 Claim boundary；
- claim incompatible Route 永不进入 executable list。

## 6. S10-C｜Chapter Editorial

### 6.1 Proven Distinct Media Capacity

Chapter capacity 不是 selectable MediaDecision 数量，而是扣除下列因素后仍可共同发布的真实上界：

- unresolved alternatives；
- Primary–Primary canonical render collision；
- same Beat 或 presentation duplicate；
- source occupancy violation；
- Hero availability failure；
- chronology/core coverage/claim incompatibility。

### 6.2 Compact 2 与 Standard 3–5

~~~text
capacity 0–1
→ INSUFFICIENT; never publish; never auto-convert to Aha

capacity 2
→ only a strict CompactChapterPairDecision PASS

capacity >=3
→ choose adaptive Standard 3 / 4 / 5
~~~

Compact Pair 必须通过独立贡献、核心覆盖、关系、非重复、质量、Fallback compatibility 与 Hero availability 等全部 Gate。两项仅为同一画面、同一实例轻微角度或不同格式时必须 FAIL。

### 6.3 Adaptive 3 / 4 / 5

三项是完整 Standard baseline；第四项只有带来 material set-level increment 才加入；第五项使用更严格的增量门。目标数量必须在全部 hard constraints 后决定，不能先选五项再机械删除。

比较完整 set 时依次保护：

1. Chapter core coverage；
2. 每个成员的独立 material contribution；
3. non-redundancy；
4. grounded progression/contrast/result；
5. Hero coverage；
6. source/failure robustness；
7. presentation quality；
8. prior continuity 与 stable deterministic tie-break。

### 6.4 Dominant Motif

同一上午都在古镇或同为古建筑，不等于只能保留一张：

- 不同建筑实例可共同展示；
- 建筑外观与有独立意义的内部木雕/庭院可作为不同 aspect；
- 同一牌坊换角度、换裁切或相隔更久仍可能是重复；
- 时间距离只能提供差异 Evidence，不能单独授权 distinct；
- 删除测试仍能完整理解且无新内容时，应删除重复项。

### 6.5 Source Occupancy

同一 RawAsset/Source Family 对一个 Chapter 的占位：

~~~text
default max = 2
strict upstream-validated multi-beat exception max = 3
hard cap = 3
~~~

格式、裁切、派生 ID、重复导入或 source offset 不得绕过上限。长 Manual 的第三项必须真实表达另一个独立阶段；绝无第四项同源例外。

### 6.6 Grounded Chronology

正文按可信 capture chronology 排序，不按美感、格式交替或模型生成的“故事感”重写时间线。

先后无法可靠确定但不改变内容时，使用 `CoTemporalGroup` 与 stable order，并向 S11/S12 传递 `NO_RELATIVE_TEMPORAL_CLAIM`。若顺序不确定会改变事实含义，则 HOLD/BLOCK，不能靠输入数组顺序兜底。

### 6.7 Hero

V1 Chapter Hero：

- 必须来自最终 Chapter media set；
- 必须是静态 PHOTO 或同一已选媒体合法派生的静态 cover；
- 代表核心意义优先于纯画质；
- 不增加正文数量，不改变时间顺序；
- 通过 C2 前的轻量 `HeroPreEligibility` 保证 set 至少有合法 Hero；
- 完整 Hero plan 只为一个 Primary 与最多一个 Passive Alternate 生成；
- Passive Alternate 正常路径只保存 ref，不提前取 HQ；
- 没有理想封面可以带 limitation 发布；没有合法封面才属于 hard failure。

## 7. 一次有界 S09 Re-selection

S10 不直接更换 Memory。只有原始 S10 batch 完成前已确定的 `PROVEN_MEDIA_INSUFFICIENCY`，才可由编排层请求一次 S09 re-selection。

~~~text
complete original S10 low-cost batch
→ collect all proven insufficiencies
→ create attempt-scoped S10FailureExclusionSet
→ one new S09 selection_attempt_id
→ same revision/snapshot/candidate pool/policy
→ rerun complete S09 set constraints
→ reuse compatible unaffected S10 artifacts
→ run S10 only for new/invalidated items
→ success, or stop permanently for this Revision
~~~

可进入：

- Chapter proven distinct capacity 0–1；
- capacity 2 且 Compact Pair proven FAIL；
- 所有合法 Anchor/format/source plans 已证明不可用；
- 全部完整 set 已证明违反 Hero contract；
- Aha 所有合法 Route 在原始 S10 batch 内已证明不可用。

不可进入：

- transient network/provider/render failure；
- source、Evidence、failure cause 或 search result 为 UNKNOWN；
- budget/timeout/service unavailable；
- lineage、Revision、policy、provenance 或 input contract invalid；
- S10 finalization/S13 阶段才发生的新 terminal failure；
- 仅为减少 Chapter/Aha 画面重复。

第二个 S10 attempt 仍失败时停止，没有第三次机会。新结果始终原子发布；prior 仍合法时保持 prior，无 prior 时 blocked/no-publishable，不解释为 EMPTY_DAY。

## 8. S10-D1/D2｜发布前有界容灾

### 8.1 D1 Single-Loss Survivor

D1 只处理 S10 finalization 后、当前 Revision 原子发布前，恰好一个 Chapter 正文成员所有预声明 Route 被证明 terminal unavailable 的情况。

预计算路径：

~~~text
5 → 4 Standard
4 → 3 Standard
3 → 2 only prevalidated Compact Pair
2 → 1 invalid
~~~

survivor 必须是原 set 减去该成员的精确子集，重新通过 core coverage、non-redundancy、source occupancy、chronology、Hero 与 Compact/Standard hard constraints。

每 Revision 最多一次 single-loss activation。第二项失败、两个成员同时 exhausted、UNKNOWN、transient、contract invalid 或发布后存储事故都不能使用 D1。

### 8.2 D2 Route Activation Collision

D2 只处理 Chapter Fallback activation 后的 `PRIMARY_FALLBACK / FALLBACK_FALLBACK` collision。健康 Primary 永远锁定，不为故障成员让位。

~~~text
lock all healthy Primaries
→ try failed members' predeclared Fallbacks in bounded combinations
→ choose a collision-free full-member assignment when one exists
→ otherwise allow at most one D1-approved exhausted member
→ two exhausted or no valid survivor = HOLD/BLOCK
~~~

每 Chapter 最多五项、每项最多三条 Route，理论组合上界 `3^5 = 243`，只比较 metadata，不调用模型、不读取媒体、不重新计算内容价值。

### 8.3 Activation 不可变性

Fallback、D1 survivor 与 Hero Alternate 的激活必须创建新 artifact/delta，不能原地改写 MediaDecision、Chapter set 或 Hero decision。激活不改变 Beat identity、正文 chronology 或 S09 membership。

## 9. S10-D3｜HQ Source Request Tiers

`HQ` 指足以生成最终 PHOTO/LIVE_2S/VIDEO_5S 的高质量源素材，不自动等于传感器 RAW、整段原视频、已经上云的文件或模型理解输入。

### 9.1 Finalization Gate

只有完成下列工作后才可输出 manifest：

1. S09 membership 已确定；
2. Chapter hard-valid set/order/Hero 与 Aha single media 已完成；
3. V1.20 pair decisions 合法，D4.2 winning projection/necessary reuse 已确定；
4. 唯一 bounded re-selection 已结束或无需进入；
5. winning projection 的 Routes、D1/D2/Hero metadata 已 final/rebuild；
6. 不存在 outcome-changing/base-contract unresolved、UNKNOWN 或 invalid；
7. source reuse/coalescing precheck 已完成。

仅影响 D4.2 软近重复、已记录为 `RENDER_RELATION_LIMITATION` 的 UNKNOWN 可以继续；涉及 source identity、provenance、Anchor 或 legality 的 UNKNOWN 仍阻断。

### 9.2 四级请求合同

~~~text
TIER_0_REUSE
  exact compatible materialization already exists

TIER_1_REQUIRED_PRIMARY
  active final body/Aha media and active Hero derivative

TIER_2_ON_DEMAND_FALLBACK
  media Fallback and Passive Alternate metadata
  request only after proven terminal activation

TIER_3_NOT_REQUESTED
  unselected, CONTEXT_ONLY, DROP, undeclared or excluded content
~~~

正常路径只请求 TIER_1；TIER_2 默认零 HQ transfer/render 成本。复用必须基于 source/render fingerprint，不能凭视觉相似。

### 9.3 最小充分范围与 coalescing

S10 必须声明精确 frame/interval、consumer、format 与 purpose。同一 source 可合并取回，但不能扩大每个 consumer 的 Evidence/Claim scope，也不能默认上传整段、整小时或全天。

如果底层能力只能获取完整 source object，S13 必须同时保留：

- S10 算法必要范围；
- 工程实际传输范围；
- 多取原因与成本审计。

### 9.4 无感交互

用户完成 Sync 后，TIER_1/TIER_2 的后台执行不得弹出新的上传确认、素材选择或重新 Sync 要求。具体上传时间、Wi-Fi/蜂窝、电量、destination、取消与 retry 属于 App/S13 OPEN 项。

## 10. S10-D4｜Aha 与跨 Memory 呈现

### 10.1 Aha Single Visible Media

每个已选 Aha：

~~~text
one core Content Beat
→ one EvidenceAnchor
→ one MediaDecision
→ exactly one active visible PHOTO or LIVE_2S
~~~

邻近 support Windows 只帮助确认 peak 前后变化、互动与事实，不成为第二、第三个可见媒体项。Aha active media 本身同时承担卡片入口、内容与 Hero 角色；LIVE poster 是同一媒体派生物，不是独立 Hero。

所有 Aha Primary/Fallback 都必须直接表达同一个 core peak；准备、普通过程、结果、邻近漂亮画面或 CORE_PARTIAL 不得替代。

### 10.2 Aha failure timing

- 原始 S10 batch 前已证明 all routes unavailable：可共享全 Revision 唯一 failure batch；
- UNKNOWN/transient/contract invalid：HOLD/BLOCK，不重选；
- finalization/S13 阶段 Primary terminal：只激活下一条同 peak Fallback；
- runtime all-routes exhaustion：没有 D1 survivor，HOLD/BLOCK，也不新增 S09 attempt；
- 已发布后事故：进入 S13 storage recovery。

### 10.3 V1.20 是硬前提

`temporal containment ≠ narrative independence`。只有 `ChapterAhaNarrativeIndependenceDecision = NARRATIVELY_DISTINCT_PASS` 的 pair 才进入媒体复用判断。

Birthday Chapter 的吹蜡烛 core/climax 不能通过换 Frame 或格式成为另一个 Aha；古镇建筑 citywalk 中的独立甜品惊喜互动，在全部 V1.20 Gate PASS 后才可共存。

### 10.4 Cross-Memory Render Distinctness

对已通过 V1.20 的 Chapter/Aha pair：

~~~text
prefer distinct presentation
only when an existing no-loss Chapter alternative exists
otherwise allow necessary exact reuse
~~~

no-loss alternative 必须来自当前 attempt 的既有合法范围，并保持 target size、core coverage、chronology、Hero availability、quality、readiness 与 robustness；不能创建新 Beat/Anchor/Route、搜索全天或主动激活 weak Fallback。

Aha Primary 默认锁定，优先调整 Chapter。没有无损替代时，允许同一 canonical render 被两个 consumer 引用：

- shared materialization/fetch；
- separate Chapter/Aha Memory identity、count、lineage 与 Claim scope；
- 不触发 S09 re-selection；
- 不要求用户再次上传。

裁切、编码或轻微时间边界变化不能伪装 distinct。Chapter 5 秒视频包含 Aha 核心 2 秒属于 material temporal overlap。

runtime Fallback 后才产生 overlap 时，不移动健康媒体、不跳过语义更优 Route，只记录 activation-induced necessary reuse。

## 11. 集成执行与发布前重验

### 11.1 实际 finalization 顺序

讨论章节编号不等于生产执行顺序。冻结的集成顺序为：

~~~text
S09 selected membership
→ A1/A2/B Beat + Anchor + MediaDecision
→ C HeroPreEligibility + Chapter set/order/Hero
→ D4.1 Aha single media
→ verify V1.20 pair decisions
→ D4.2 cross-memory presentation projection
→ final/rebuild D1/D2/Hero metadata
→ D3 HQ request manifest
→ S11 → S12 → S13
~~~

### 11.2 Runtime activation 后的重验义务

S13 在发布前证明 terminal failure 时，可以按冻结合同激活预声明 Route/D1/Alternate，但 resulting projection 必须在发布前重新验证受影响的下游 artifact：

1. `PRESENTATION_NARROWING` 后重验 narrative/Claim scope；
2. D1 删除正文成员后重验 title/story/tag、progression/outcome 与完整性；
3. Hero Alternate 后重验 cover provenance/Claim；
4. revalidation 未完成时 Revision 继续 HOLD；
5. 用户只能看到通过重验后的完整结果。

具体采用 S13 回调、统一编排器或 materialization-before-S12 的服务顺序留给 S11–S13 集成专项；“发布前不可跳过重验”已冻结。

## 12. Cross-Revision 与原子发布

1. 同一 attempt 的 ContentBeat、Anchor、MediaDecision、set、Hero、projection 与 manifest 不原地改写；
2. 新素材或合法事实变化产生新 Revision；runtime activation 产生 immutable delta；
3. fingerprint 完全兼容时可复用旧 materialization；
4. prior-published continuity 高于纯美学/软避重偏好，避免画面无意义抖动；
5. 新 Revision 完整通过前继续显示仍合法 prior；
6. prior 已被事实、Evidence、policy 或合法性撤销时不得用 retention 掩盖；
7. blocked 不等于 EMPTY_DAY；Manual 原素材继续留在独立窗口与事实账本。

## 13. 成本与规模上界

### 13.1 高强度日输入参考

~~~text
150 Auto Video × 9s = 22.5 min
20 Manual Photo
10 × 15s + 3 × 60s + 3 × 120s Manual Video = 11.5 min

186 RawAssets
34 min total video
~~~

150 个 Auto source 在端侧固定抽三帧，共 450 个低成本 frame positions；云端采用已冻结的 1-or-3 上传合同，不在一帧不够时再请求另外两帧。Manual Window 总数仍未冻结。

### 13.2 Final 输出上界

~~~text
Chapters <= 5
Ahas <= 3
Chapter body media <= 25
body + Aha visible media <= 28
Chapter Hero derivative consumers <= 5
active render consumers <= 33
unique active HQ source requests <= 28 before further coalescing
dormant media Fallback refs <= 56
Passive Alternate Hero refs <= 5
D1 subset audits <= 25
D2 theoretical assignments <= 5 × 3^5 = 1,215
Chapter–Aha pair checks <= 15
~~~

28 是极端 Final 可见媒体上界，不是日常目标。四章各四项、加 2–3 个 Aha 的丰富日约为 18–19 个 body/Aha 可见媒体项。

Fallback、D1、D2、D4.2 正常都只增加小规模 metadata，不新增模型、Raw 上传或全天视觉理解。一次 bounded re-selection 只重跑 S09 set solver 与新/失效 Memory 的必要 S10 metadata，不重跑 S04–S08。

在真实编码、设备能力、Manual Window、网络和 S13 pipeline benchmark 前，不冻结 MB/GB、美元、电量、时延或固定节省比例。

## 14. Canonical 案例

| 场景 | 冻结结果 |
|---|---|
| 三小时古建筑，多个不同建筑外观 | 可保留 2–3 个甚至更多不同实例，最终仍由 3/4/5 set 增量门决定 |
| 同一牌坊相隔 40 分钟、角度略变 | 时间远不自动 distinct；展示作用相同则抑制 |
| 建筑外观＋内部木雕细节 | 有独立意义时可按不同 aspect 共同入选 |
| 73 秒陶艺视频，上游已有准备/拉坯/成品三个 Unit | 可走同源三项严格例外；S10 不自行定义 Window |
| 只有制作过程＋成品两项 | 全部 Compact Pair Gates PASS 后可发布双素材 Chapter |
| 三项 Chapter 只有一项合法 Hero | 正常发布；Alternate 可为空，不恢复外围漂亮图 |
| 古镇 A—奶茶 B—古镇 C | B 可是 side episode，A/C continuity 可保持；S10 不重新 split Moment |
| 古镇 citywalk＋第一口甜品惊喜 | V1.20 PASS 后可共存；Aha 只显示 peak 一个媒体 |
| Birthday Chapter＋吹蜡烛 Aha | same-story climax；不得共选，也不进入 render reuse |
| Chapter/Aha 只有同一画面最真实 | 无 no-loss alternative 时允许 exact reuse，共享 materialization |
| Chapter Primary terminal、Fallback 与健康项相撞 | 健康 Primary 锁定，尝试下一预声明 Fallback |
| Aha runtime all-routes exhausted | HOLD/BLOCK，不用 support frame、不删除后继续发布、不重进 S09 |

## 15. 验证证据

分阶段与全链路检查结果：

~~~text
A2: 12-case internal cross-check passed
B: media-decision cross-check passed; 6 refinements applied
C: 36 boundary cases + 5 profiles passed; 4 refinements applied
V1.20: 44 boundary cases + 12 invariants passed
D4: 36 boundary cases + 14 invariants passed; 4 refinements applied
S10-E: 52 cross-stage cases passed
S10-E: 10 user profiles passed
S10-E: 32-window ancient-town timeline traced
S10-E: 30 global invariants preserved
S10-E: 6 integration refinements applied
~~~

S10-E 的六项 integration refinement：

1. 讨论顺序与 actual finalization 顺序分离；
2. Aha media insufficiency 按发生时间精确分流；
3. runtime activation 后必须重验受影响 S11/S12 artifacts；
4. 阶段早期 `OPEN`/pending 文字与后续已确认结论对齐；
5. consumer、render/materialization、unique source request、dormant metadata 分账；
6. V1.20 冻结历史不回写，由 V1.21 解决其下游 render-reuse OPEN 项。

## 16. 状态边界

### FROZEN

- S10 membership/whitelist 权限边界；
- Content Beat 定义、完整 inventory、Same/Distinct/Unresolved 与防链式误合并；
- EvidenceAnchor 三种目标、BeatAnchorRequirement、分层比较、1 Primary＋0–2 Fallback；
- semantic eligibility 与 HQ readiness 分离；
- Chapter/Aha 格式资格与最小充分媒体选择；
- Exact Media Source Plan、MediaDecision、conditional/failure routing；
- Chapter Standard 3–5、strict Compact 2、0–1 insufficiency；
- adaptive 3/4/5、Dominant Motif、同源默认二/严格三/硬上限三；
- grounded chronology、CoTemporalGroup、static meaning-first Hero、一个 Passive Alternate；
- 每 Revision 一次、批量、attempt-scoped、仅 proven pre-batch insufficiency 的 S09 re-selection；
- D1 single-loss survivor 与 D2 healthy-primary-locked collision resolution；
- TIER_0/1/2/3 HQ request、source coalescing 与无第二次上传交互；
- Aha 恰好一个 PHOTO/LIVE_2S、无独立 Hero、strict same-peak Fallback；
- V1.20 PASS 后默认避免 Chapter/Aha render 重复、无损替代优先、必要 exact reuse 合法；
- integrated finalization order、immutable activation delta 与发布前 affected-artifact revalidation；
- Cross-Revision continuity、原子发布与成本上界定义。

### OPEN / 待真实数据或后续专项

- 16 秒、73 秒及其他任意时长 Manual Video 的 Window 数量与精确位置；
- Beat/Anchor/quality/motion/duplicate 的真实模型、阈值、标注规范与用户个性化；
- Production deterministic search budget、pruning 与性能 benchmark；
- PHOTO/LIVE/VIDEO 的分辨率、码率、压缩、实际字节、电量、时延和美元成本；
- S13 timebase tolerance、decode/render retry、terminal classification、checksum、atomic write 与 source lifecycle；
- runtime activation 后 S11/S12 revalidation 的具体服务编排；
- App 后台上传时间、Wi-Fi/蜂窝/电量、destination、云存储/API/Agent 路由与本地保留；
- App 是否在不同 surface 重复展示 exact reuse、Aha badge、版式与动效；
- 隐私、伦理、治理与用户数据控制专项。

### IMPLEMENTATION GAP

- 当前没有完整 Production ContentBeat/EvidenceAnchor/MediaDecision/Chapter editorial engine；
- 当前没有 Production D1/D2/D3/D4 schema、orchestrator 与 validators；
- 当前没有真实 186-RawAsset 高强度日 benchmark 证明准确率、P50/P95/P99 成本或时延；
- 当前没有大规模用户标签证明 Dominant Motif、Aha peak、Hero 与 no-loss alternative 判断准确；
- S11–S13 尚未实现 activation-delta affected-artifact revalidation；
- V1.21 是产品与算法架构冻结，不代表 Production readiness。

## 17. 覆盖与继承关系

V1.21：

1. 继承 V1.19 的 S09 membership、Day State、Preview/Final count、lineage、readiness 与 whitelist；
2. 解决 V1.19 留给 S10 的“是否允许一次有界 S09 re-selection”，冻结为本文第 7 节合同；
3. 继承 V1.20 的 Chapter/Aha narrative independence，不降低或重做五道 Gate；
4. 解决 V1.20 当时明确不覆盖的 Chapter/Aha final-render reuse，冻结为本文第 10.4 节；
5. 不改变 V1.3 的 Auto 三帧证据、V1.4 的 Manual Evidence 或 V1.8 无二次补帧上传方向；
6. 不覆盖 S11 Narrative、S12 final validator 或 S13 工程数值；
7. 只在与本文冲突的 S10 旧草案表述上具有更高优先级。

## 18. 术语释义

| term | 简明含义 |
|---|---|
| Content Beat | 一个 Memory 内值得占一个展示位置的独立内容意义 |
| EvidenceAnchor | 该 Beat 在原素材中的精确、可追溯证据地址 |
| MediaDecision | 一个可见位置的 Primary/Fallback 格式与精确源计划 |
| presentation redundancy | 同时展示不会增加用户可辨认的新内容 |
| Compact Chapter | 严格 Pair Gate 通过后允许两项呈现的 Chapter |
| Dominant Motif | 长时间 Chapter 中占主导的同类主题，如古建筑；不等于全部重复 |
| Source Family | 不能靠裁切、格式或派生 ID 绕过的共同底层素材来源 |
| Hero | Chapter 的静态入口/封面角色，必须来自最终正文集合 |
| Passive Alternate | 正常路径不取 HQ、仅在 Hero terminal failure 后可能激活的一个备用 ref |
| proven insufficiency | 已确定没有合法可发布媒体的内容呈现失败，不是暂时没跑通 |
| bounded re-selection | 每 Revision 最多一次、只重跑 S09 set selection 的有界替换尝试 |
| terminal failure | 已证明不可恢复、允许进入预声明 Fallback 的永久失败 |
| survivor set | 原 Chapter set 删除一个 terminal-failed member 后预验证的精确合法子集 |
| no-loss alternative | 不损失数量、核心、质量、顺序、Hero 或鲁棒性的已有合法替代 projection |
| exact reuse | 两个 Memory 合法引用同一 canonical render，但保持各自 identity 与 Claim |
| HQ source | 足以生成最终可见媒体的高质量源，不自动等于 RAW 或整段视频 |
| materialization | 从 source 生成可供最终消费的媒体结果 |
| atomic publish | 用户只看到完整通过的 Revision，不看到内部中间状态 |
