# S07 Cross-Check and Semantic Timeline Simulation V0.1

**状态：** `HISTORICAL REVIEW / FINDINGS RESOLVED BY V0.2 AND FROZEN V1.17`
**日期：** 2026-08-26
**作用范围：** S07 Chapter / Aha Candidate Generation 的 A～F 统一检查，以及不使用真实图片的用户画像语义时间轴模拟
**明确不覆盖：** S01–S06 准确率实现、S08 具体模型与上传动作、S09 最终集合选择、S10 媒体审美与渲染、Narrative、App、Firmware/SDK、共享状态文件

> 本文保留最初 V0.1 合同的检查证据与 F1–F8 发现，不回写历史结果。F1–F7 并入统一工作合同后的独立复跑见 [S07 Cross-Check and Profile Simulation V0.2](S07_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_2.md)；当前权威规则以 [V1.17](CANONICAL_CHECKPOINT_V1_17_CHAPTER_AHA_CANDIDATE_GENERATION.md) 为准。

## 1. 检查方法

本轮不生成图片、不伪造真实用户数据，也不运行视觉模型。每个模拟样本只描述：

- 用户类型与高概率生活结构；
- capture time 上可能出现的 Auto / Manual 素材；
- S05 可能提交的有序 Moment；
- S06 可能交付的 KEEP / CONTEXT_ONLY / DROP 结果；
- 按当前已讨论 S07-A～F 合同推导出的 Candidate、duplicate、reject 与 S08 handoff；
- 与产品目标相比是否出现误组、漏组、误升 Aha、候选爆炸或成本风险。

模拟默认上游事实正确。若某个问题本质属于 S04 识别错误、S05 分段错误或 S06 角色错误，记录为上游依赖，不允许 S07 反向改写上游。

## 2. 被测试的 S07 工作合同

### 2.1 Candidate 与 route

- 一个 S06 seed 不自动等于一个 Candidate；
- 普通 content-active Moment 可提名 Chapter / Aha；
- Transition content-active Moment 只可提名 Aha；
- context-only 与 output-inactive Moment 不生成内容 Candidate；
- ChapterCandidate 与 AhaCandidate 是不同对象，不能互相自动降级；
- Candidate 不生成最终 title、story、hero 或用户可见 Claim。

### 2.2 Chapter scope

- `SINGLE`：一个普通 content-active Moment 独立构成局部 Episode；
- `ADJACENT_GROUP`：直接相邻的普通 content-active Moments 共同表达一个 Episode；
- `RESUMED_EPISODE`：活动主线被中间 Moment 打断后恢复；
- `LOCAL_EPISODE_GROUP`：同一次局部经历中的多个不同小 Episode；
- 当前讨论稿要求 Chapter 至少 3 个 distinct KEEP RawAsset，且去重后仍有至少 3 个非重复内容单元；
- S07 grouping 不改写 S05 Moment membership 或 seam。

### 2.3 Aha scope

- 一个 Aha 只有一个 origin Moment 和一个 KEEP peak Window；
- 可带紧邻支持 Window，总计最多 3 个连续 Window；
- 最早与最晚支持 Window 的 capture span 最多 3 分钟；
- V1 不跨 Moment 组合 Aha；
- `Local Peak Evidence` 与 `Independent Memory Value` 必须分别通过；
- ordinary Moment 当前讨论稿最多产生 2 个 Aha，Transition 最多 1 个。

### 2.4 Duplicate、数量、Revision 与 S08

- S07 只处理同一局部 Episode / event 的候选重复；全天集合冗余留给 S09；
- 完全重复或被更小充分范围支配的 Candidate 可抑制；不确定的不同解释进入 alternative group；
- 当前讨论稿每个普通 seed 最多 1 个 SINGLE、2 个 grouped Chapter hypotheses、2 个 Aha；
- 当前讨论稿局部关系范围最多 8 个已提交 Moment，RESUMED 最多跨 2 个中间 Moment，超过 30 分钟无 Evidence gap 停止；
- Preview 最多向 S08 交付 3 个验证候选，Final 最多 8 个；
- 同一 Candidate 必须来自同一 immutable Revision；新 Revision 不修改旧 Candidate。

## 3. 冻结文档交叉检查

| Check | 结果 | 说明 |
|---|---|---|
| S07 不改写 S04 facts | PASS | Candidate 只引用 grounded facts、UNKNOWN 与 limitations |
| S07 不改写 S05 partition | PASS | Grouping 是 Chapter 关系，不是 Moment merge |
| S07 不改写 S06 roles | PASS | Candidate 抑制不删除 KEEP，也不恢复 DROP |
| Transition 只竞争 Aha | PASS | 与 V1.14/V1.16 一致 |
| Manual 无候选豁免 | PASS | 与 V1.6/V1.16 一致 |
| Aha 不是低分 Chapter | PASS | Chapter reject 不触发 Aha 自动降级 |
| Aha 可与 Chapter 共享 Evidence | PASS WITH LATER GATE | S07 可共存；S09 必须控制最终语义重复 |
| 无全天主题聚类 | PASS | 只允许局部关系和有界搜索 |
| 同 Revision 与 immutable snapshot | PASS | 与 V1.1/V1.15/V1.16 一致 |
| Auto `UPLOAD_1` 不补帧 | PASS | S07/S08 handoff 不授权补取另外两帧 |
| Chapter 3 RawAsset | CONFLICT RISK | S09 原文是“原则上”；讨论稿在 S07 提前变成硬门，可能误杀长 Manual Episode |
| Aha 双硬门与 validation-required | AMBIGUOUS | “必须通过”与“尚待 S08 才能确认”缺少三态 Gate 定义 |
| S08 selection-impact priority | CIRCULAR RISK | S09 尚未运行时不能直接声称知道最终集合影响，需要非最终 admission planner |
| Group candidate seed audit | MISSING | 最早成员生成 group 时，其他参与 seed 的 disposition 尚未定义 |
| 8-Moment 范围 | AMBIGUOUS | 当前把“搜索 horizon”与“Candidate membership 上限”混为一谈 |
| Near-duplicate before S08 | AMBIGUOUS | 未确认 dominance 时过早 suppression 可能删掉验证后更好的候选 |
| S08 3/8 count budget | PARTIAL | 数量有界，但不同 validation action 的真实成本不等价，仍需 S08 加权预算 |

## 4. 用户画像语义时间轴模拟

### P01｜城市办公室工作日：高重复、低高光

**画像：** 通勤、办公室、会议、午餐；Auto 较多，Manual 很少。
**目标风险：** 为凑 3–4 Chapter，把普通工作画面强行升格。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 08:00–08:25 | M1 地铁/步行通勤；5 Auto，3 个非重复 KEEP |
| 08:30–09:50 | M2 办公桌工作；大量相似 Auto，S06 后只剩 1–2 个有效 KEEP |
| 10:00–10:45 | M3 会议；8 Auto + 1 Manual Photo，4 个非重复 KEEP |
| 11:00–11:15 | M4 走廊/电梯；context-only |
| 11:30–12:20 | M5 与同事午餐；5 Auto + 2 Manual，4 个非重复 KEEP |

**S07 trace：**

- M1 虽满足 3 RawAsset，但若没有明确记忆价值，可拒绝 Chapter；
- M2 不因素材多而成立，重复后内容不足；
- M3、M5 可以分别提名 SINGLE Chapter；
- M4 不生成 Candidate；
- 普通咖啡、走廊或场景变化不成为 Aha。

**结果：** PASS。预期只有 1–2 个强 Chapter，可能 0 Aha；没有配额填充。

### P02｜周末古镇 Citywalk：中途奶茶后恢复

**画像：** 连续步行游览，中间短暂停留喝奶茶。
**目标风险：** S05 切开后 A、C 永远无法重组，或把奶茶错误吞进步行 Moment。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 09:00–09:15 | M1 石板路与步行；4 Auto，3 KEEP |
| 09:15–09:30 | M2 建筑立面与沿街店铺；5 Auto，4 KEEP |
| 09:30–09:50 | M3 奶茶店室内与饮品；Auto + Manual，3 KEEP |
| 09:50–10:20 | M4 恢复街巷步行；6 Auto，4 KEEP |
| 10:20–10:45 | M5 寺庙/院落参观；Auto + Manual，4 KEEP |
| 10:50 | M6 上车离开；明确 blocker |

**S07 trace：**

- M1+M2 可形成 ADJACENT_GROUP；
- M1/M2 与 M4 可建立 RESUMED relation，M3 作为 interruption ref；
- 若 M3 对整次 outing 有独特贡献，可形成 M1–M5 LOCAL_EPISODE_GROUP；
- M3 不因“进入室内”自动成为 Aha；只有具体互动或短暂事件才进入 Aha；
- M6 终止局部扩张。

**结果：** PASS WITH MISSING TRACE。关系逻辑成立，但 M2/M4/M5 参与 group 后需要明确 `JOINED_GROUP(candidate_id)` seed disposition，不能被误记为无候选。

### P03｜家庭仪式：一条长 Manual 视频承载完整事件

**画像：** 家长记录孩子两分钟表演或生日仪式，只拍一条 120s Manual Video 和一张照片。
**目标风险：** RawAsset 数量少，但内容时间结构丰富。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 18:15–18:17 | M1 一次完整表演/仪式；1 Manual 120s Video（6 Windows，其中 5 KEEP）+ 1 Manual Photo |

**S07 trace（当前讨论稿）：**

- distinct RawAsset = 2；
- 非重复、可选择的局部内容单元约 4–5；
- Episode coherent、worth remembering，并可形成 3–5 个不同时间点的媒体；
- 由于 S07 硬性要求 3 distinct RawAsset，Chapter 被拒绝；
- 其中一个吹蜡烛/谢幕局部峰值可能成为 Aha。

**结果：** FAIL / CRITICAL。完整 Episode 被 Chapter 硬门误杀，最终只剩 Aha，效果上形成了已明确禁止的“完整 Episode 被迫只以 Aha 出现”。这不是主动降级代码，但产品结果等价。

### P04｜居家远程工作：大量素材但信息单一

**画像：** 五小时主要在家办公，Auto 规律采集，手动拍过一杯咖啡。
**目标风险：** 数量驱动候选、Manual 自动获选。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 09:00–12:00 | M1 桌面办公；90 Auto 中绝大多数重复，少量 KEEP |
| 10:30 | M1 内一张 Manual Coffee Photo |
| 12:00–12:30 | M2 简单午餐；少量 KEEP |
| 12:30–14:00 | M3 继续桌面办公；与 M1 是较晚恢复，但价值弱 |

**S07 trace：**

- 大量 Auto 不等于丰富 Episode；
- M1/M3 的 resumed relation 即使语义成立，也因独立记忆价值不足而拒绝；
- Coffee Photo 只有 Manual intent、没有具体峰值，不能成为 Aha；
- 可以合法得到 NO_CHANGE / EMPTY_DAY。

**结果：** PASS。验证质量门与不凑数原则。

### P05｜宠物主人：上午与晚上两次相似遛狗

**画像：** 两次路线相似的遛狗，中间是完全不同的生活阶段。
**目标风险：** 视觉和 activity 相似导致全天主题聚类或候选去重。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 07:00–07:35 | M1 早晨公园遛狗；5 个非重复 KEEP |
| 12:00–13:00 | M2 居家/午餐；独立 Episode |
| 19:00–19:40 | M3 晚间同一路线遛狗；5 个非重复 KEEP |

**S07 trace：**

- M1、M3 超出局部关系与 30 分钟无 Evidence gap；
- 不能建立 RESUMED_EPISODE；
- 不能只因 scene/activity/embedding 相似建立 duplicate group；
- 两者可分别成为有效 SINGLE Candidate；全天是否同时展示留给 S09。

**结果：** PASS。S07 与 S09 redundancy 边界清晰。

### P06｜徒步用户：连续活动中存在无采集长间隔

**画像：** 山路运动、画面晃动，中间设备暂停 35 分钟，之后继续同一条路线。
**目标风险：** motion 误升 Aha；30 分钟 gap 产生 false split。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 06:30–07:00 | M1 林道上行；部分 KEEP，部分 blur/drop |
| 07:00–07:35 | 无有效 Evidence |
| 07:35–08:00 | M2 山脊继续步行；KEEP |
| 08:05 | M3 山顶 Manual Photo / Video；具体到达与景观 Evidence |

**S07 trace：**

- 模糊和 motion spike 不产生 Aha；
- 当前 30 分钟规则阻断 M1→M2 grouping；
- M2+M3 仍可形成局部 Chapter；
- M3 若有具体到达/互动/短暂现象，可独立提名 Aha；纯风景好看并不自动通过。

**结果：** EXPECTED PRECISION TRADE-OFF。会漏掉“整次徒步”这一长 Episode，但符合当前宁可漏记、不跨无证据长间隔推断的原则。必须记录 `SCOPE_STOP_UNSUPPORTED_GAP`，后续用真实数据测量 regret，不能静默扩大。

### P07｜朋友聚餐：Manual 连拍与一次碰杯

**画像：** 用户主动拍很多菜品、合照和短视频，其中大量相似。
**目标风险：** Manual 近重复占满 Chapter 媒体和 Aha。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 18:30–18:45 | M1 到店与落座；Auto + Manual |
| 18:45–19:20 | M2 菜品连拍；10 Manual Photo，S06/S07 duplicate group 后只剩代表与少量独特菜品 |
| 19:20 | M3 碰杯；15s Manual Video + Photos，存在具体互动 peak |
| 19:30–20:00 | M4 用餐与甜点；Auto + Manual |

**S07 trace：**

- M1–M4 可形成 LOCAL_EPISODE_GROUP；
- 相似菜品照片不增加有效内容单元或精选媒体位；
- M3 可形成一个 Aha，不因多帧/多照片生成多个相同 Aha；
- Manual 不获得 duplicate 豁免。

**结果：** PASS。验证 candidate-level duplicate 和 Aha local peak。

### P08｜演唱会/节庆：一个长 Moment 内多个真实峰值

**画像：** 同一活动和场地持续较长时间，S05 合理地保持为一个大 Moment；期间出现多次独立短暂事件。
**目标风险：** 把 Aha 数量上限错误绑定到 Moment 数量。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 19:00–20:30 | M1 演唱会；多个 Auto/Manual，形成“嘉宾登场、互动、彩带、返场”等 3–4 个互不重叠的真实 peak interval |

**S07 trace（当前讨论稿）：**

- M1 可以形成一个 SINGLE Chapter；
- 3 个局部峰值都分别满足 Aha 双门；
- ordinary Moment Aha cap = 2，第三个峰值在进入 S09 前即被截断；
- 全天 Aha 最终上限本来是 3。

**结果：** FAIL / RECALL RISK。Aha 本来就是长 Moment 内的 sub-Moment 峰值，因此不能假定“超过两个说明 S05 过宽”。当前 per-Moment cap 2 缺乏产品依据。

### P09｜商场办事链：同地点、不同小任务

**画像：** 药店、超市、午餐、取快递都发生在同一商场或附近。
**目标风险：** 同地点和时间接近导致过度 LOCAL_EPISODE_GROUP。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 11:00–11:20 | M1 药店购买物品 |
| 11:25–11:50 | M2 超市采购 |
| 12:00–12:35 | M3 午餐 |
| 12:40–12:55 | M4 取快递后离开 |

**S07 trace：**

- 相同商场、时间相邻只能提供 locality，不足以推断统一“目的”；
- 如果时间轨迹、连续移动与共同 outing envelope 支持，可提名一个谨慎的 LOCAL_EPISODE_GROUP；
- M1–M4 仍可作为不同 SINGLE alternatives；
- Candidate 不能提前写成“高效完成所有计划”等用户意图 Narrative。

**结果：** PASS WITH VALIDATION NEED。结构允许正确 alternatives；near-duplicate / dominated 判定在关系仍不确定时不能提前抑制。

### P10｜手作/创作用户：一个 Episode 被切成十个细 Moment

**画像：** 两小时陶艺、烘焙、绘画或设备组装；工具、视角和阶段多次变化，但整体是同一项目。
**目标风险：** 把局部搜索 horizon 错当成 Candidate membership 上限。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 09:00–11:00 | M1–M10：准备、加工、细节操作、检查、调整、完成；每个 Moment 都有独特 KEEP，Moment 间连续且无 blocker |

**S07 trace（当前讨论稿）：**

- 前 8 个 Moment 可以形成 group；
- M9/M10 因“最多 8 个 Moment 范围”无法成为同一 Candidate 的成员；
- 完成结果可能被切掉，而它恰恰是 Chapter 完整性的重要部分；
- 最终 Chapter 只展示 3–5 个媒体，不代表 Candidate 只能引用 3–8 个 Moment。

**结果：** FAIL / ARCHITECTURE AMBIGUITY。必须把“向前寻找非相邻关系的 horizon”与“已经由连续、group-wide evidence 支持的 Candidate membership”分开。

### P11｜跨 Revision 晚到素材：旧关系被新中间内容改变

**画像：** 用户多次 Sync；一条较早 capture 的 Manual 素材晚到。
**目标风险：** 混用不同 Revision、直接修改旧 Candidate、错误复用缓存。

| Revision | 时间轴 |
|---|---|
| R1 | 09:00 M1 街区步行；09:40 M2 继续步行 |
| R2 | 晚到的 09:20 奶茶店 Manual 插入，重新形成 M1｜M3 奶茶｜M2 |

**S07 trace：**

- R1 Candidate 保持不可变；
- R2 使用新的完整 Snapshot、Moment partition 与 S06 role packet；
- R1 的简单 group 不能直接复用为 R2 group；
- R2 可生成 RESUMED 或 LOCAL group，并通过 Evidence fingerprint 建立 lineage；
- 用户可见 Chapter stable ID 由后续阶段决定，不能把 Revision-scoped Candidate ID 当成稳定产品 ID。

**结果：** PASS。Revision 架构成立，但 Candidate fingerprint 必须基于有序 Evidence/role/version，而不能只依赖可能变化的 Moment ID。

### P12｜办公室到餐厅之间的短暂街头表演

**画像：** 一个 unresolved Transition block 本身记录到清楚、短暂、可独立理解的表演。
**目标风险：** Transition 自动成为 Aha，或借左右语境补事实。

| Capture time | 可能的 S05/S06 输入 |
|---|---|
| 17:55 | M1 办公室 |
| 18:10 | T1 Transition Moment：街头艺人具体动作，1 KEEP peak Window |
| 18:20 | M2 餐厅 |

**S07 trace：**

- T1 不能进入 Chapter；
- T1 必须只凭自身 KEEP 通过 local peak 与 independent value；
- 边界不明确不是加分项；
- 若通过，只产生 1 个 Aha Candidate；否则 reject，不借 M1/M2 补全。

**结果：** PASS。Transition route 与三阶段职责清晰。

### P13｜五小时高强度参考日：候选容量压力

**画像：** 使用最初约定的 150 Auto Video、20 Manual Photo、16 Manual Video，共 186 RawAsset / 220 Evidence Window。
**目标风险：** S07 Candidate 数量和关系比较发生组合爆炸。

本例不假设 220 Window 等于 220 Moment。采用一个偏高但仍可能出现的 S05 输出：

```text
28 committed Moments
→ 20 ordinary content-active
→ 2 Transition content-active
→ 3 context-only
→ 3 output-inactive
```

在当前 per-seed cap 下，生成前的理论上界为：

```text
20 ordinary × 1 SINGLE                   = 20
20 ordinary × 2 grouped hypotheses       = 40
20 ordinary × 2 Aha                      = 40
2 Transition × 1 Aha                     = 2

current theoretical maximum              = 102 Candidate hypotheses
```

若按 F2 把 ordinary Aha cap 调整为 3：

```text
revised theoretical maximum              = 122 Candidate hypotheses
```

这是 gate 和 duplicate 之前的结构化对象上界，不是模型调用数，也不是最终输出数。实际流程还会经过：

- Chapter coherence/value/media-coverage gate；
- Aha 双门；
- group 最早成员 ownership；
- exact/dominated duplicate suppression；
- alternative group 归并；
- S08 Preview 3 / Final 8 handoff guardrail；
- S09 最终 1–5 Chapter / 0–3 Aha 集合选择。

局部 relation nomination 若每个 Moment 只查看最多 8 个后续位置，比较量约随 `Moment count × 8` 增长，而不是 `Moment count²`。百级轻量 Candidate 对象不是主要费用；真正的费用来自 S08 temporal/audio/strong-model validation 和 S10 HQ/render。

**结果：** PASS WITH ENGINEERING GUARD。S07 不需要用全天 Top-K 牺牲召回。仍需记录 Candidate 总量、每类数量、comparison count、duplicate ratio 与 `SAFETY_LIMIT_REACHED`；若真实数据经常接近理论上界，再根据 trace 调整 per-seed cap，而不是预先删除长 Episode 成员。

## 5. 模拟后确认的问题

### F1｜3 distinct RawAsset 不能作为 S07 无例外硬门 — MUST FIX

P03 证明：长 Manual Video 可以由多个连续 Evidence Window 提供 3–5 个互不重复、时间上不同的内容单元。S09 的“原则上 3 distinct RawAsset”不能在 S07 被静默收紧成绝对硬门。

建议改为：

```text
Normal Chapter path
→ distinct KEEP RawAsset >= 3
→ non-redundant selectable evidence units >= 3

Long-Manual exception path
→ distinct KEEP RawAsset = 1 or 2
→ at least 3 temporally distinct, grounded, non-duplicate Evidence units
→ coherent complete Episode
→ PROVISIONAL_VALIDATION_REQUIRED: MEDIA_DIVERSITY
```

同一 Auto 9s 的三帧不能算三个内容单元；长 Manual 的不同 Window 只有在事实和时间位置确实不同、且不是 duplicate 时才可分别计数。

### F2｜ordinary Moment 的 Aha cap 应从 2 调整为 3 — MUST FIX

P08 证明 per-Moment cap 2 会在 S09 前丢失第三个真实局部峰值。建议：

```text
ordinary origin Moment → at most 3 non-overlapping Aha Candidates
Transition origin Moment → at most 1 Aha Candidate
```

全天最终仍由 S09 限制为 0–3；候选层允许三个不等于最终必须展示三个。

### F3｜8-Moment search horizon 与 group membership 必须拆开 — MUST FIX

建议：

```text
relation_nomination_forward_horizon = 8 committed Moments
resumed_intervening_moment_max = 2

established adjacent/local group
→ may extend incrementally beyond 8
→ every extension must pass local relation + group-wide compatibility + material-gain gates
→ stop at blocker / unsupported 30-min gap / group drift
```

为保持工程硬上限，可暂设 `group_member_safety_max = 12` 作为 V1 候选值，并在真实 Moment 粒度数据上专门测量 truncation regret；这个 12 尚不应在本报告中标为 FROZEN。

### F4｜Candidate gate 必须是三态，不是表面双态 — MUST FIX

S07-D 的双硬门是产品语义，但工程执行需要：

```text
PASS
NEEDS_VALIDATION
FAIL
```

建议 Candidate disposition 使用：

```text
ELIGIBLE
PROVISIONAL_VALIDATION_REQUIRED
SUPPRESSED_DUPLICATE
REJECTED
```

`PROVISIONAL` 明确表示尚未通过最终 Truth/Relation gate，避免 `ACCEPTED_VALIDATION_REQUIRED` 被误解为已合格。

### F5｜需要 SeedDisposition — MUST FIX

每个 S06 content-active seed 必须得到一个且只有一个 seed-level disposition：

```text
EMITTED_CANDIDATE(candidate_id...)
JOINED_GROUP(candidate_id...)
NO_CANDIDATE(reason...)
```

Transition/context/output-inactive route 仍按已有 route audit 记录。Candidate-level disposition 与 seed-level disposition 不能混用。

### F6｜只有已证实的 duplicate/dominance 才能在 S07 抑制 — MUST FIX

- 完全相同 Candidate 可以在 S08 前合并；
- 当前 Evidence 已经证明“更大范围没有新增意义”时，可以抑制 dominated scope；
- 如果差异依赖 S08 才能确认，必须保留在 `alternative_hypothesis_group`；
- suppressed Candidate 的 alternate refs 只用于 provenance，不得扩张保留 Candidate 的事实、内容计数或媒体资格。

### F7｜S08 admission 不能依赖尚未发生的最终 S09 选择 — MUST FIX

将“可能改变最终集合”改为可在 S07/S08 admission 时判断的条件：

- validation 可改变 Candidate 自身 ELIGIBLE / REJECTED 状态；
- validation 可解决一个 alternative group 的 dominance；
- validation 可确认 Chapter media-diversity exception；
- Candidate 已通过独立价值初筛，且没有更可靠等价候选。

这只是验证前沿规划，不是最终 Top-K 或 Set Selection。

### F8｜S08 3/8 是数量 guardrail，不是完整成本预算 — KEEP OPEN FOR S08

Preview 3 / Final 8 可以暂时保留为 Candidate handoff 上限，但还必须在 S08 增加：

- 不同 action 的 cost weight；
- 每 Revision / 每日 / 每月成本预算；
- 已缓存 enrichment 的复用；
- provider failure 与 semantic inability 的独立归因；
- budget exhaustion regret。

在这些规则完成前，不能声称“最多 8 个候选”已经保证月均成本目标。

## 6. 可继续保留的 Baseline

- Aha 支持范围 `<= 3 contiguous Windows / <= 3 minutes`；
- V1 Aha 不跨 Moment；
- RESUMED 最多跨 2 个中间 Moment；
- 超过 30 分钟无有效 Evidence gap 时 precision-first 停止，并记录 regret；
- Preview S08 candidate frontier 3、Final 8，可作为数量 guardrail；
- Transition 最多 1 个 Aha Candidate；
- 不设全天 S07 Top-K；
- 不执行全天任意两两 Moment 比较；
- S07 不新增媒体上传、视觉理解或 Auto 补帧；
- same input snapshot + same versions 必须确定性复现；
- Late Data 只能进入新 Revision。

## 7. 本轮结论

S07 的主架构成立：Candidate 与最终输出分离、Chapter/Aha 路径分离、局部 Episode grouping、Aha 双门、candidate duplicate、immutable Revision 与 S08 targeted handoff 的方向均正确。

但当前版本还不能冻结。必须先修正 F1–F7，再重新跑本报告中的 P01–P13。F8 留给 S08 专题，但 S07 handoff 必须明确数量上限不是完整成本保证。
