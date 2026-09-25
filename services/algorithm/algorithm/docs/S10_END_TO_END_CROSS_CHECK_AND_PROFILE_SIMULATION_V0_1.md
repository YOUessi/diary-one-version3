# S10 End-to-End Cross-Check & Profile Simulation V0.1

**状态：** CROSS-CHECK PASSED / REFINEMENTS APPLIED / S10 FROZEN BY CANONICAL V1.21
**日期：** 2026-08-27
**主工作文档：** `S10_EVIDENCE_ANCHOR_MEDIA_EDITORIAL_CONSOLIDATED_WORKING_V0_1.md`
**上游冻结输入：** `CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md`、`CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md`
**分阶段验证输入：** `S10_A2_EVIDENCE_ANCHOR_INTERNAL_CROSS_CHECK_V0_1.md`、`S10_B_MEDIA_DECISION_INTERNAL_CROSS_CHECK_V0_1.md`、`S10_C_CHAPTER_EDITORIAL_INTERNAL_CROSS_CHECK_V0_1.md`、`S10_D4_AHA_FINAL_MEDIA_INTERNAL_CROSS_CHECK_V0_1.md`

## 1. 检查目标与范围

本检查不重新设计 S10，而是把已经逐项确认的合同连成一条可执行链，检查：

1. A1、A2、B、C、D 之间是否存在字段、权限或状态断点；
2. V1.19 membership 与 V1.20 Chapter/Aha narrative independence 是否会被 S10 媒体选择绕过；
3. proven insufficiency、UNKNOWN、transient、contract invalid、terminal failure 是否始终走不同路径；
4. Preview/Final、一次有界 S09 re-selection、D1/D2 runtime activation 与原子发布是否互相兼容；
5. 高强度一天是否仍保持有界计算和最小 HQ 请求；
6. 不同用户画像是否会暴露明显的产品体验矛盾；
7. S11、S12、S13 是否能收到足够明确且不可变的下游输入。

本检查明确不决定：

- 任意 16 秒、73 秒等 Manual Video 的 Window 数量与精确位置；
- App 后台上传时机、Wi-Fi/蜂窝/电量策略、云存储/API/Agent 去向；
- S13 retry、checksum、timebase tolerance、source lifecycle 的工程数值；
- PHOTO/LIVE/VIDEO 的实际码率、分辨率、压缩率、字节和美元成本；
- App 的重复画面 badge、卡片布局、加载和失败视觉；
- 真实模型、阈值、搜索预算、个性化权重与标注校准；
- Firmware/SDK、共享状态、隐私、伦理或治理专项。

## 2. 检查结论摘要

~~~text
52 / 52 cross-stage boundary cases = expected deterministic outcome
10 / 10 user-profile simulations = no contract contradiction
32-window fine-grained ancient-town timeline = complete trace
30 / 30 global invariants preserved
6 interface refinements applied
0 new model calls required by the frozen direction
0 whole-day re-search paths introduced inside S10
0 additional user Sync/upload interactions introduced
0 new subjective product decisions silently added
~~~

结论：S10 从 selected Memory 到 final-media request intent 的架构闭环成立。检查发现的六项问题都是接口表述或执行顺序精化，不推翻已经确认的产品方向。用户已确认结论，S10 已由 Canonical V1.21 正式冻结。

## 3. 一条完整的执行链

### 3.1 正常规划路径

~~~text
S09 SelectedMemorySet + S10HandoffEnvelope
  ↓
A1  enumerate all grounded Content Beats
  ↓
A2  resolve one EvidenceAnchor + 0–2 Anchor Fallbacks per Beat
  ↓
B1–B3  choose legal format, exact source plan and immutable MediaDecision routes
  ↓
C HeroPreEligibility lightweight prepass
  ↓
C1–C2  compute capacity and choose Compact 2 or adaptive Standard 3/4/5
  ↓
C3  apply grounded chronology + Primary Hero + max one Passive Alternate
  ↓
D4.1  finalize exactly one visible PHOTO/LIVE_2S per selected Aha
  ↓
verify V1.20 narrative-decision references for every relevant Chapter/Aha pair
  ↓
D4.2  reconcile cross-memory render overlap without changing membership
  ↓
finalize/rebuild D1 survivor ledgers, D2 collision metadata and Hero metadata
  ↓
D3  emit one coalesced FinalMediaHQRequestManifest
  ↓
S11 grounded narrative → S12 final validation → S13 materialization/export
~~~

V1.20 的 Chapter/Aha stories gate 实际在 S09 决定。S10 这里只验证输入引用与一致性；若发现 same-story pair 被错误共选，必须报 input/relationship contract invalid，不能换画面制造“不同故事”。

### 3.2 发布前终止失败路径

~~~text
S13 attempts active TIER_1 materialization
  ├─ success → continue publish validation
  ├─ transient / UNKNOWN → retry or HOLD; no content change
  └─ proven terminal failure
       ↓
     activate only predeclared TIER_2 route
       ↓
     Chapter: D2 resolves route collisions with healthy Primaries locked
     Aha: keep the same peak and apply D4.2 runtime overlap policy
       ↓
     if exactly one Chapter member remains exhausted:
       use only a prevalidated D1 single-loss survivor
     if an Aha exhausts every route:
       no one-item survivor exists; HOLD/BLOCK current Revision
       ↓
     emit immutable HQRequestActivationDelta
       ↓
     revalidate affected final-media projection and dependent S11/S12 artifacts
       ↓
     atomically publish one complete Revision, or do not publish it
~~~

D1/D2 是有界的预计算容灾合同，不是正常路径上重复调用模型或重新编辑故事。运行时不得重新搜索全天、创建 Route、改写 Beat、改变 Chapter order，或再触发 S09 membership search。

## 4. 三十项全局 Invariants

1. S09 决定 Memory membership；S10 不静默新增、删除或替换 Chapter/Aha。
2. S10 只使用当前 `S10HandoffEnvelope` 的 whitelist 与当前 Revision scope。
3. KEEP 才能成为 Anchor；CONTEXT_ONLY 只辅助理解；DROP 永不恢复。
4. Content Beat 是展示意义位置，不等于 RawAsset、Window、Frame 或媒体格式。
5. 每个 Beat 要么产生一个 MediaDecision，要么留下显式失败/invalid 记录，不能静默消失。
6. 一条 MediaDecision 只有一个 Primary 和最多两个有序 Fallback。
7. Fallback 数量不增加 Chapter/Aha 的可见媒体数量。
8. Anchor 先于格式；漂亮格式不能反向改换到不支持核心事实的位置。
9. PHOTO/LIVE/VIDEO 的选择服从最小充分原则，不设置动态比例配额。
10. Chapter 仅允许 PHOTO/LIVE_2S/VIDEO_5S；Aha 仅允许 PHOTO/LIVE_2S。
11. Aha 始终只有一个核心 Beat 和一个 active visible media position。
12. Chapter 标准集合为 3–5；仅严格 Compact Pair 可以为 2；0–1 永远不可发布。
13. 一个 Beat 最多占一个 Chapter 正文位置。
14. 同一 Source Family 默认最多二项，严格 multi-beat 例外最多三项，绝无第四项例外。
15. 同主题可以保留不同实例/内容侧面；同实例轻微角度变化不能靠时间距离绕过去重。
16. Chapter target size 在完整 hard constraints 后确定，不先锁五项再删。
17. Chapter 正文按可信拍摄时间排序；Hero、格式和 Fallback 不改写顺序。
18. 相对先后不可靠时使用 CoTemporalGroup，并禁止无证据的“先、然后”Claim。
19. Hero 必须来自最终 Chapter set、为静态 PHOTO、优先代表核心意义。
20. Hero 最多一个 Passive Alternate；它不增加正文数量，也不在正常路径取 HQ。
21. V1.20 的 narrative independence 高于媒体避重；same-story core pair 不进入 D4.2。
22. D4.2 默认避免 Chapter/Aha 重复画面，但只有 no-loss alternative 才能替换。
23. 没有 no-loss alternative 时 exact reuse 合法，且共享 materialization、不合并 Memory identity。
24. Primary 健康时永不为另一成员的 Fallback 让位。
25. D1 只允许一次单成员 survivor activation；不做链式或双成员删除。
26. proven pre-finalization media insufficiency、transient、UNKNOWN、contract invalid 与 runtime terminal failure 严格分流。
27. 每 Revision 最多一次批量、attempt-scoped S09 re-selection，只处理原 S10 batch 已证明的媒体不足。
28. HQ 仅在 finalization gate 后请求；TIER_2 Fallback 正常路径只有 metadata 成本。
29. 任意 runtime activation 必须产生不可变 delta，并在发布前重验受影响的 narrative/claim/validation artifacts。
30. 用户只看到完整、原子发布的 Revision；不会被要求再次 Sync、选素材或确认后台 HQ 上传。

## 5. 跨阶段接口审计

| 接口 | 上游保证 | 下游权限 | 禁止行为 | 结果 |
|---|---|---|---|---|
| S09 → A1 | selected type、scope、KEEP/CONTEXT/DROP、lineage、whitelist | 完整枚举 scope 内 Beats | 搜索全天、用漂亮素材换 Memory | PASS |
| A1 → A2 | Beat identity、core facts、same/distinct/unresolved | 找精确 EvidenceAnchor | 凭空拆长 Manual、把 Window 当 Beat | PASS |
| A2 → B | 1 Primary Anchor、0–2 Fallback Anchors、resolution | 选合法媒体格式与源区间 | 因格式偏好改 Anchor 含义 | PASS |
| B → C | 每 Beat 一个 MediaDecision、Route/collision metadata | 计算真正 distinct capacity 与 set | 把 Fallback 当额外内容项 | PASS |
| C prepass → C2 | 每 candidate 的静态 Hero feasibility | 只筛合法完整 set | 给所有候选做完整 Hero/HQ 计划 | PASS |
| C2 → C3 | final member set 与 target size | 排时间、选 Hero | 用 Hero 反向改 member set | PASS |
| S09/V1.20 → D4 | pair-specific narrative decision | 只处理已合法共存 pair 的媒体呈现 | 用不同 Frame 掩盖 same-story 冲突 | PASS |
| C/D4 → D4.2 | hard-valid Chapter projection 与 locked Aha Primary | 选已有 no-loss projection或记录必要复用 | 主动启用弱 Fallback 只为视觉不同 | PASS |
| final projection → D1/D2 | 确定成员、Route、Hero、collision matrix | 预计算有界失败响应 | 运行时重新评分/找素材 | PASS |
| D3 → S13 | tier、exact scope、fingerprint、activation predicate | 获取/渲染所需源 | 默认上传整天或全部 Fallback | PASS |
| runtime delta → S11/S12 | resulting required set 与 route-specific limitations | 重验受影响文案、Claim 与发布资格 | 沿用引用已删除媒体的旧故事 | PASS after R3 |
| S12 → publish | 完整合法的最终 projection | 原子发布或拒绝 | 部分卡片先出现后删除 | PASS |

## 6. 五十二个跨阶段边界案例

### 6.1 A｜身份、权限与 Beat（10）

| ID | 场景 | 预期结果 | 检查 |
|---|---|---|---|
| A01 | 两条 ContentUnit 都是同一牌坊的近似正面 | presentation SAME；一个 Beat | PASS |
| A02 | 石板路、古建筑立面、木雕细节风格相似 | 按内容语义成为不同 Beat，不靠 style embedding 强合并 | PASS |
| A03 | A≈B、B≈C，但 A/C 有明确不同内容 | 禁止链式传递合并；保留 distinct/unresolved 审计 | PASS |
| A04 | 景区指示牌只帮助确认地点，标为 CONTEXT_ONLY | 可辅助理解，不生成 Beat/Anchor | PASS |
| A05 | DROP 中有一张构图漂亮的建筑照 | 永不恢复进 Hero 或正文 | PASS |
| A06 | 73 秒陶艺 Manual 上游已有准备、拉坯、成品三个合法 ContentUnit | S10 可消费三个 Beat，仍受同源上限/例外约束 | PASS |
| A07 | 73 秒 Manual 上游只有一个合法 ContentUnit | S10 不凭时长拆三段；Window 规划保持 OPEN | PASS |
| A08 | 一个 Beat 同时有 Auto frame 与 Manual photo | 仍是一个内容位置，A2 比较 Anchor | PASS |
| A09 | 一条 Evidence 同时支持“进入庭院”和“看到木雕” | 可分别进入 eligibility；若 final render 相同，C 阻断重复占位 | PASS |
| A10 | whitelist、Revision 或 policy fingerprint 不匹配 | input/contract invalid；不继续猜测 | PASS |

### 6.2 B｜Anchor、格式、精确源与 Route（10）

| ID | 场景 | 预期结果 | 检查 |
|---|---|---|---|
| B01 | Manual Photo 直接呈现建筑正面 | `STILL_ASSET`，不伪造视频 timestamp | PASS |
| B02 | 9 秒 Auto Video 的已上传帧直接呈现门楼 | 使用实际 frame provenance 的 `FRAME_TIMEPOINT` | PASS |
| B03 | 吹灭蜡烛需看到火焰变化，已有连续证据 | `EVIDENCE_SUPPORTED_INTERVAL`，可评估 LIVE | PASS |
| B04 | 动作 Beat 只有动作后的静态结果 | 不能冒充完整动作；Anchor/format 按证据不足处理 | PASS |
| B05 | Auto 首帧不足以确认内容，另外两帧未按 1-or-3 合同上传 | 当前候选排除/不足；云端不二次请求用户上传 | PASS |
| B06 | HQ handle 为 NOT_YET_MATERIALIZED，但合法可请求 | 语义 Anchor 可成立；不等于 render-ready | PASS |
| B07 | 语义最优 Anchor source UNKNOWN，另有近似等价且明确可请求者 | 可选择后者并记录 tradeoff；不得掩盖实质损失 | PASS |
| B08 | LIVE conditional，PHOTO 能直接表达同一核心 | LIVE Primary＋PHOTO 非条件 Fallback 合法 | PASS |
| B09 | 原 S10 batch 内已证明所有合法 source 都永久不可用 | proven media insufficiency，可进入唯一批次重选 | PASS |
| B10 | provider timeout 或上传仍在正常队列 | transient/HOLD；不得记作内容不足 | PASS |

### 6.3 C｜Chapter 集合、顺序与 Hero（12）

| ID | 场景 | 预期结果 | 检查 |
|---|---|---|---|
| C01 | 牌坊、大殿、塔楼三项互补 | Standard 3 | PASS |
| C02 | 制作过程＋成品两项高度互补 | 六 Gate 通过后可为 Compact 2 | PASS |
| C03 | 两项只是同一建筑不同裁切 | Compact FAIL，不发布双素材伪 Chapter | PASS |
| C04 | 只有一个合法媒体项 | proven insufficiency；不转 Aha、不补 CONTEXT_ONLY | PASS |
| C05 | 三项已完整，第四项只是同 Beat 更清晰版本 | 替换弱项而非增加位置，保持三项 | PASS |
| C06 | 第四项加入独立阶段，第五项加入独立结果 | 分别通过增量门后可输出五项 | PASS |
| C07 | 三小时都是古建筑，但为不同建筑实例/内部侧面 | 可保留 3–5 个；同类别不等于重复 | PASS |
| C08 | 同一牌坊相隔 40 分钟再次近似拍摄 | 时间远不自动 distinct；抑制重复 | PASS |
| C09 | 同一长 Manual 的准备、过程、成品三 Beat | 严格同源三项例外可 PASS；第四项禁止 | PASS |
| C10 | 最后拍摄的塔楼最能代表 Chapter | 可做 Hero，但正文仍保持真实时间位置 | PASS |
| C11 | 两项同秒且无可信先后 | CoTemporalGroup＋stable order；禁止相对时间 Claim | PASS |
| C12 | 最佳语义集合无合法静态 Hero，另一个近似集合有 | C2 只从 Hero-covered hard-valid sets 中选择；不跨 scope 找漂亮封面 | PASS |

### 6.4 D｜HQ、失败、Fallback、D1/D2（10）

| ID | 场景 | 预期结果 | 检查 |
|---|---|---|---|
| D01 | 四项 Chapter 每项 1 Primary＋2 Fallback | 正常路径只激活四个 TIER_1；八个 Fallback 为 dormant TIER_2 | PASS |
| D02 | Hero PHOTO 与正文 VIDEO 来自同一 source | source fetch 可合并，consumer/derivative identity 分开 | PASS |
| D03 | Primary 首次渲染超时 | retry/HOLD；不提前启用 Fallback | PASS |
| D04 | Primary proven terminal，第一 Fallback 合法且无冲突 | 激活预声明 Route，生成 immutable delta | PASS |
| D05 | A-Fallback 与 B 健康 Primary 相同 | 锁定 B；跳过 A-F1，尝试 A-F2 | PASS |
| D06 | 两个失败成员的第一 Fallback 相撞，但存在无冲突组合 | D2 在最多 `3^5` metadata 组合内确定性保留全员 | PASS |
| D07 | 一个正文成员全部 Route 用尽，4→3 survivor 已预验证 | 激活一次 D1 survivor，原子发布三项 | PASS |
| D08 | 两个正文成员全部 Route 用尽 | 不做双删除；HOLD/BLOCK | PASS |
| D09 | runtime fallback 带来 claim narrowing | 激活后重验受影响 S11/S12 artifacts，再允许发布 | PASS after R3 |
| D10 | 已发布后发生云存储事故 | 不使用 D1 静默改已发布内容；进入 S13 存储恢复边界 | PASS |

### 6.5 E｜Aha、V1.20 与跨 Memory 复用（10）

| ID | 场景 | 预期结果 | 检查 |
|---|---|---|---|
| E01 | Birthday Chapter＋吹蜡烛 Aha | same-story core；S09 不共选，D4.2 不执行 | PASS |
| E02 | Birthday Chapter 未入选，吹蜡烛本身独立过全部 Gate | 可竞争 standalone Aha，但不自动获选 | PASS |
| E03 | Birthday Chapter＋猫跳上蛋糕并引发独立反应 | 五 Gate PASS 后可共存 | PASS |
| E04 | 古镇建筑游览 Chapter＋普通甜品静物 | Aha standalone floor FAIL | PASS |
| E05 | 古镇建筑游览 Chapter＋第一口甜品惊喜互动 | Chapter/Aha 可独立成立；D4.2 再处理媒体重复 | PASS |
| E06 | Chapter 与 Aha 原计划 exact render，有 no-loss Chapter alternative | 锁定 Aha，选择已有无损 Chapter projection | PASS |
| E07 | exact reuse 无任何 no-loss alternative | 允许复用；一个 materialization、两个 consumer/Memory | PASS |
| E08 | Chapter 5 秒视频包含 Aha 核心 2 秒 | material temporal overlap，不以格式不同伪装 distinct | PASS |
| E09 | Aha Primary terminal，合法 PHOTO Fallback 仍直接表达同 peak | 激活单一媒体位置；不新增第二项 | PASS |
| E10 | Aha 所有 Route 在 S13 阶段才 terminal exhausted | 当前 Revision HOLD/BLOCK；无 Aha survivor、无新 S09 re-selection | PASS after R2 |

## 7. 32-Window 古镇细粒度时间线

### 7.1 输入语义

以下只是结构化语义模拟，不生图、不伪造 RawAsset，也不替代未来真实数据标注。

| 时间 | 可能采集到的画面语义 | S10 处理要点 |
|---|---|---|
| 09:00 | 古镇入口牌坊全景 | “进入古镇”核心候选，KEEP |
| 09:02 | 穿过牌坊的行走视角 | 与 09:00 可形成进入动作 evidence；不自动新 Beat |
| 09:04 | 石板路近景 | 古街行走候选；若只有纹理则代表性有限 |
| 09:06 | 两侧古建筑店面 | 建筑街景候选，可与石板路 distinct |
| 09:08 | 景区地图与方向牌 | 可能仅 CONTEXT_ONLY，帮助地点/方向 |
| 09:10 | 第一座牌坊正面 | 独立建筑实例候选 |
| 09:12 | 同一牌坊侧面轻微换角度 | 若无新内容，presentation duplicate |
| 09:14 | 进入小庭院 | 新空间/阶段，可成为 distinct Beat |
| 09:16 | 屋檐、瓦片与斗拱 | 只有形成独立建筑侧面价值时才保留 |
| 09:18 | 游客遮挡的庭院 | 可作 supporting；画面不可用不否定事实 |
| 09:20 | 寺庙大殿外观 | 不同建筑实例，Dominant Motif 内可 distinct |
| 09:22 | 香炉与殿前空间 | 若只是大殿附属普通角度，可能合并/不入最终 set |
| 09:24 | 大殿内部结构 | 与外观有实质不同内容，可独立贡献 |
| 09:26 | 木雕细节清楚可辨 | `DUAL_ASPECT` 候选，需能独立理解其意义 |
| 09:28 | 同一木雕再次近拍 | 若只更近/更清晰，替换而不是新增 Beat |
| 09:30 | 路边茶摊 | 古镇生活侧面；是否入 Chapter 取决于增量价值 |
| 09:32 | 回到古街继续行走 | continuity evidence，通常不另占位置 |
| 09:34 | 与 09:04 相似的石板路 | 时间变远不自动 distinct，优先抑制重复 |
| 09:36 | 走近石桥 | 从街巷向河边推进，可形成 progression |
| 09:38 | 桥上河道与沿岸建筑 | 河边空间候选 |
| 09:40 | 远处独立塔楼 | 新建筑实例候选 |
| 09:42 | 接近塔楼 | supporting/progression；不因距离变化自动新 Beat |
| 09:44 | 塔楼正面结构完整 | 塔楼代表 Anchor/潜在 Hero |
| 09:46 | 人群经过塔楼前 | 若主体被遮挡，保留事实但不胜任代表媒体 |
| 09:48 | 进入现代奶茶店 | 形成短暂现代室内 side episode/break |
| 09:50 | 点单与店员互动 | 奶茶过程 evidence；是否为独立 Beat 取决于上游 scope |
| 09:52 | 奶茶制作过程 | 过程 supporting；不能凭“看起来好吃”产生 Aha |
| 09:54 | 第一口后出现明确惊喜互动 | 若有 grounded reaction，可成为独立 Aha peak candidate |
| 09:56 | 朋友回应与笑 | 支持 09:54 的局部互动；不自动成为 Aha 第二媒体 |
| 09:58 | 离开奶茶店 | boundary evidence，帮助确认短暂插曲结束 |
| 10:00 | 回到古街与古建筑环境 | 支持 A–B–C 恢复同一 citywalk 主线 |
| 10:02 | 河边古建筑与行程收束 | 古镇 Chapter 的结束/结果候选 |

### 7.2 一次可能的合法全链路结果

假设上游 Evidence 充分且 S09 选择：

~~~text
Chapter C1 = 古镇建筑 citywalk
Aha A1 = 奶茶第一口的独立惊喜互动
ChapterAhaNarrativeIndependenceDecision = NARRATIVELY_DISTINCT_PASS
~~~

A1 可以完整识别入口、古街、庭院/大殿、木雕、河边/塔楼、奶茶短暂停留、返回与结束等 Beat candidates。A2/B 只为各 Beat 选择其合法 Anchor 和格式，不把 32 个 Window 机械变成 32 个媒体项。

一个合法的 C2/C3 Chapter projection 可以是：

| 正文位置 | 选择 | 原因 |
|---|---|---|
| 1 | 09:00 入口牌坊 PHOTO/LIVE | 建立进入与地点 |
| 2 | 09:24 大殿内部 PHOTO | 与外观不同的实质建筑侧面 |
| 3 | 09:44 塔楼 PHOTO | 不同实例，强代表性，可为 Hero |
| 4 | 10:02 河边收束 PHOTO/VIDEO | 表达路线推进与结束 |

Aha A1 只展示 09:54 的一张 PHOTO 或一段 LIVE_2S；09:52 和 09:56 只作 supporting evidence。Chapter 去掉该 peak 后仍保持“古镇建筑 citywalk”核心，Aha 不借 Chapter 文案也可理解为一次明确的甜品惊喜互动，因此 V1.20 的双向独立性成立。

若 Chapter provisional set 原来包含 09:54，而上述 09:24/10:02 组合是同等完整的 no-loss alternative，D4.2 选择不重复的 Chapter projection；若删除 09:54 会实质损害 Chapter 且无等价替代，则允许必要 exact reuse。两种路径都不会重选 Memory，也不会要求用户再次上传。

### 7.3 A–B–C continuity 检查

~~~text
A = 09:00–09:46 古镇主线
B = 09:48–09:58 奶茶店短暂 side episode
C = 10:00–10:02 返回古镇主线
~~~

B 的独立意义不自动把 A/C 永久 split。S06/S07 的 continuity/boundary evidence 可以同时表达：B 是真实插曲，A 与 C 仍属于同一古镇 citywalk Chapter。S10 只消费已经由上游确定的 Memory scope，不在媒体阶段重新做 Moment segmentation。

## 8. 十类用户画像模拟

| ID | 用户与高概率素材 | 预期输出/风险 | 结果 |
|---|---|---|---|
| P01 | 旅行者：三小时古镇，大量相似建筑、路面、店铺 | 允许不同建筑实例和独立侧面；压制同实例换角度；3–5 项 Chapter | PASS |
| P02 | 家庭记录者：生日准备、点蜡烛、吹蜡烛、鼓掌、合照 | 生日 Chapter 可 4–5 项；吹蜡烛若为高潮不得重复成 Aha | PASS |
| P03 | 普通上班族：会议、午饭、通勤，内容稀疏且割裂 | 不为数量把不同 Memory 拼成 Chapter；合法 Compact 或不发布 | PASS |
| P04 | 手作爱好者：一个长 Manual 拍完整陶艺过程 | 只消费上游已验证 Beats；最多三项同源严格例外；Window 规划不偷定 | PASS |
| P05 | 徒步用户：登山、山顶、短暂彩虹 | 山顶是 Chapter outcome 不重复 Aha；独立彩虹可过 V1.20 后成为 Aha | PASS |
| P06 | 演出/运动用户：高运动、灯光变化、画面抖动 | motion value 不等于可用性；动态必要时选 LIVE/VIDEO，Hero 仍为合法静态 | PASS |
| P07 | 稀疏高光日：没有完整 Chapter，只有清晰求婚 peak | 可形成 HIGHLIGHT_DAY 的单一 standalone Aha；不补成微型 Chapter | PASS |
| P08 | 美食用户：菜品静物多、真实反应少 | 不从食物类别/外观推断“好吃”；普通静物不能自动成为 Aha | PASS |
| P09 | 亲子用户：Manual Photo 与 Auto 重复拍到同一动作 | Manual 也可被 presentation 去重；仍保留在 Manual 窗口与事实账本 | PASS |
| P10 | 碎片化通勤：频繁进出商店、地铁、街道 | 上游未形成完整 Memory 时 S10 不跨 scope 拼故事；pending/defer 不由 S10删除事实 | PASS |

所有画像都沿用相同硬合同；真实用户偏好只影响未来标注与受控校准，不允许实现用用户画像绕过 provenance、membership、数量或 narrative independence。

## 9. 高强度一天的规模与成本上界

### 9.1 输入规模复核

~~~text
Auto Video    150 × 9s  = 1,350s = 22.5 min
Manual Photo   20
Manual Video   10 × 15s + 3 × 60s + 3 × 120s
               = 690s = 11.5 min

Total RawAssets = 150 + 20 + 16 = 186
Total video duration = 2,040s = 34 min
~~~

Auto 端侧固定抽取三帧，因此 150 个 Auto source 对应 450 个端侧低成本 frame positions；云端按已冻结的保守 1-or-3 合同接收一帧或三帧，不发起“再补另外两帧”的二次请求。Manual Video 的 Window 数量尚未冻结，因此本检查不伪造全天统一 Window 总数。

### 9.2 S10 输出上界

| 对象 | Final 上界 | 正常丰富日示例 | 成本意义 |
|---|---:|---:|---|
| Chapter | 5 | 4 | 第五章仍须 S09 exceptional gate |
| Aha | 3 | 2–3 | 每个恰好一个可见媒体 |
| Chapter body media | 25 | 16（4×4） | 5 Chapter × 5 items |
| 全部可见 body/Aha media | 28 | 18–19 | 不含 Hero 派生 surface 的重复计数 |
| active body/Aha realization consumers | ≤28 | 18–19 | 每个可见位置一个 active realization |
| Chapter Hero derivative consumers | ≤5 | 4 | 来自已选正文 member，不是新内容项 |
| unique active HQ source requests | ≤28 | ≤18–19 | Hero 同源合并；跨位置复用还可进一步减少 |
| dormant media Fallback refs | ≤56 | metadata only | 每个可见位置最多两条；正常路径零 HQ fetch |
| Passive Alternate Hero refs | ≤5 | metadata only | 每 Chapter 最多一个；正常路径零 HQ fetch |
| D1 survivor subset audits | ≤25 | 通常 12–16 | 每 Chapter 最多按其成员数检查 |
| D2 metadata assignments | ≤1,215 | 通常远低于 | 5 Chapter × `3^5`；不调用模型/不读取媒体 |
| Chapter–Aha pair checks | ≤15 | 通常 8–12 | 5×3；复用已有结构化 Evidence |

Hero 来源于已选正文 member，因此不增加新的必要 source identity；它最多增加一个静态 derivative consumer/render，但不能被误报成新的内容项。最坏情况下 28 个 body/Aha consumers 加 5 个 Hero derivative consumers，共 33 个 active render consumers，而 unique HQ source requests 仍不超过 28，并会因同源 coalescing 或 exact reuse 进一步减少。Exact reuse 可以有两个 consumer refs，但只保留一个 shared materialization。

### 9.3 一次有界重选的成本

一次 bounded re-selection：

- 不重跑 S04–S08；
- 不重新理解 186 个 RawAssets；
- 不请求新的 Raw/HQ 上传；
- 只重跑同 candidate pool 的 S09 set solver；
- 复用 fingerprint 未变化的 S10 artifacts；
- 只为新入选或失效的 Memory 做必要 metadata 决策；
- 第二次仍失败即停止，不产生第三个 attempt。

因此它增加的是少量、低概率的结构化求解和 metadata 成本，不是把整天视觉理解与高清素材成本翻倍。

### 9.4 当前不能给出的数字

在 Manual Window、实际编码、设备取源能力、网络策略、模型调用位置和 S13 render pipeline 没有 benchmark 前，不能严谨声称：

- 每用户每天固定上传多少 MB/GB；
- 每用户每天固定花费多少美元；
- 端侧固定耗时、电量或峰值内存；
- D2 理论组合数就是实际运行次数；
- 1-or-3 一定节省某个固定百分比。

这些应由真实素材 benchmark 产生 P50/P95/P99，而不是在 S10 文档中猜数字。

## 10. 十条失败链路模拟

| ID | 失败发生点 | 正确路径 | 禁止路径 | 结果 |
|---|---|---|---|---|
| F01 | 原始 S10 batch 内一个 Chapter proven capacity=1 | 收入 batch，最多一次 S09 re-selection | 现场换 Candidate/转 Aha | PASS |
| F02 | 原始 batch 内两个 Chapter 都 proven fail | 完成全批后一次性重选 | 每发现一个就重选一次 | PASS |
| F03 | Anchor source 状态 UNKNOWN | HOLD/BLOCK | 伪装为 proven insufficiency | PASS |
| F04 | HQ 正常上传队列等待 | 等待或按 S13 retry | 提前删正文/换 Hero | PASS |
| F05 | Primary terminal，Fallback 成功 | immutable activation delta | 原地改 MediaDecision | PASS |
| F06 | Fallback 与健康 Primary 冲突 | 健康 Primary 锁定，尝试下一 Fallback | 移动健康 Primary | PASS |
| F07 | 一个 Chapter member exhausted | 仅在预验证 survivor PASS 时 D1 一次删除 | 从候选池补第六项 | PASS |
| F08 | 两个 Chapter members exhausted | HOLD/BLOCK | 连续两次 D1 缩减 | PASS |
| F09 | Aha Primary terminal、Fallback 成功 | 同 peak 单位置替换＋下游重验 | 同时展示 Primary/Fallback | PASS |
| F10 | Aha 所有 Route runtime exhausted | HOLD prior 或 blocked；无新 S09 attempt | 用 support frame、空卡或邻近漂亮图 | PASS |

## 11. 发现并已应用的六项 Refinement

### R1｜讨论章节顺序与实际 finalization 顺序分开

D1/D2/D3/D4 的讨论编号不等于生产执行顺序。主文档已补充集成顺序：先完成 Chapter/Aha hard-valid projection 与 D4.2，再 final/rebuild D1/D2/Hero metadata，最后生成 D3 manifest。

### R2｜Aha media insufficiency 必须按发生时间分流

旧表述只说“沿用一次有界重选”，容易被读成 S13 失败后仍能重进 S09。现明确：

- 原 S10 batch 完成前已证明 all routes unavailable：可进入全 Revision 唯一 failure batch；
- UNKNOWN/transient/contract invalid：HOLD/BLOCK，不重选；
- finalization/S13 阶段才发生 terminal failure：先走预声明 Fallback；全部用尽则 HOLD/BLOCK，不新增 S09 attempt；
- 已发布后的 source 事故：属于 S13 存储恢复。

### R3｜Runtime activation 后必须重验受影响的 S11/S12 artifacts

Fallback、D1 survivor 或 Hero alternate 可能改变格式、可支持 Claim 范围或正文成员。仅验证媒体路由不足以保证旧 narrative 仍正确。现要求 activation delta 显式列出受影响范围，并在原子发布前重新验证依赖 artifacts；具体编排方式由 S11–S13 集成合同实现。

### R4｜阶段早期的 `OPEN`/closeout 状态同步到后续已确认结论

A2/B/C 早期段落保留了“重选、Aha 数量、C cross-check 仍 OPEN”的历史文字。现改为“当时不在本阶段决定，已由后续 C/D/E 确认”，避免团队按局部段落误读当前状态。

### R5｜consumer、render/materialization 与 source request 分账

一个可见媒体位置是一位 consumer；Hero derivative 或 Chapter/Aha exact reuse 可能共享 source/materialization。成本审计必须分别统计：

~~~text
visible consumer count
active render/materialization count
unique HQ source request count
dormant TIER_2 metadata count
~~~

不能把 28 个最大可见位置、56 个 Fallback refs 或多个 consumer refs直接等同于上传文件数。

### R6｜V1.20 的旧 OPEN 项由下游 S10 解决，不改写冻结历史

V1.20 冻结时明确不覆盖 Chapter/Aha final-render reuse；S10-D4.2 现在已经解决该下游问题。V1.20 文档保留其冻结时的范围说明，S10 新 Checkpoint 将作为后续、窄范围的补充合同，而不是回写历史文档假装当时已经决定。

## 12. 保持 OPEN 的问题

S10-E 没有把下列问题偷渡成默认答案：

1. 任意时长 Manual Video 的 Window 规划；
2. 实际图像/视频质量参数与成本数字；
3. 端侧相似度阈值、云端模型、真实搜索预算与个性化；
4. S13 的 retry、terminal 判定、checksum、atomic write 与长期存储恢复；
5. runtime activation 后 S11/S12 affected-artifact revalidation 的具体服务编排；
6. App 的后台上传时间、网络/电量门、destination 与本地生命周期；
7. App 是否在不同 surface 重复展示 exact reuse、是否显示 Aha badge；
8. 隐私、伦理与治理专项。

这些 OPEN 项不阻断 S10 产品/算法架构冻结，但会阻断相应 Production implementation 或成本承诺。

## 13. Freeze Result

S10 已满足并完成 Canonical Checkpoint 冻结：

- A1–D4 每个阶段均已讨论并确认；
- A2、B、C、D4 分阶段检查均通过；
- V1.20 narrative independence 已冻结并接入；
- 本次 52-case、10-profile、32-window 全链路检查通过；
- 新发现的六项接口 refinement 已回写主文档；
- 没有未决的 S10 核心用户体验选择；
- 工程数值和上传架构 OPEN 项已明确隔离。

当前状态为：

~~~text
DESIGN CLOSED
END-TO-END CROSS-CHECK PASSED
FROZEN BY CANONICAL V1.21
~~~

冻结文件为 `CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md`。下一阶段进入 S11，而不是在 S10-E 中提前设计 Narrative。
