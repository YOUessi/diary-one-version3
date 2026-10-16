# S10-C Chapter Editorial — Internal Cross-Check V0.1

**状态：** CROSS-CHECK PASSED / REFINEMENTS APPLIED / S10 FROZEN BY CANONICAL V1.21
**日期：** 2026-08-27
**被检查文档：** `S10_EVIDENCE_ANCHOR_MEDIA_EDITORIAL_CONSOLIDATED_WORKING_V0_1.md`

## 1. 检查范围

本检查覆盖：

~~~text
S10-C1  proven capacity / Compact Chapter / bounded re-selection
→ S10-C2  2–5 member set / adaptive 3–5 / dominant motif / source occupancy
→ S10-C3.1  grounded chronology
→ S10-C3.2  static Hero / meaning-first selection / passive alternate ref
~~~

本检查不决定 Aha supporting item、正文 Route 的运行时 collision resolution、S13 retry 数值、HQ 上传时机、云存储生命周期、App 版式或任意 16s/73s Manual 的上游 Window 规划。

## 2. 核心检查问题

1. capacity upper bound 是否不会被误当成最终可发布 set；
2. Compact Chapter 是否仍为严格例外，而不是普遍改成 2–5；
3. 0–1 项是否不会自动改成 Aha 或恢复弱素材；
4. 第四、第五项是否真正要求 material increment；
5. Dominant Motif 是否允许同主题不同实例，而不放过同实例重复；
6. 同一长 Manual 是否既能表达真实过程，又不会占满 Chapter；
7. Hero availability 是否只作为可发布条件，而不会让美感主导正文集合；
8. Hero 是否始终属于最终 set、保持静态 V1 与同 Anchor scope；
9. Chapter 时间线是否不会因 Hero、格式或 Fallback 改写；
10. Preview/Final 是否保持原子发布与一次有界重选；
11. transient、UNKNOWN、contract invalid 与 proven insufficiency 是否严格分流；
12. 是否仍保持无新增模型、无提前 HQ、无用户额外交互的成本边界。

## 3. 检查方法

每个案例沿同一决策链推演：

~~~text
MediaDecisionInventory
→ distinct capacity
→ Compact/Standard eligibility
→ HeroPreEligibility prepass
→ complete-set constraints
→ adaptive target size
→ source occupancy
→ chronology
→ Primary Hero / Passive Alternate
→ Preview/Final publish impact
~~~

检查使用结构化离散状态与删除测试，不使用一个 overall score，也没有调用模型、请求 HQ 或生成真实媒体。

## 4. 发现并已应用的 Refinements

### F1｜HeroPreEligibility 必须是 C2 前的轻量 prepass

**风险：** 文档按 C2→C3 讲解，但 C2 hard constraint 又要求至少一个 Hero PASS；若执行顺序不明确，会产生 C2↔C3 循环依赖。

**修正：** 明确执行链为 A2/B1/B3 metadata → lightweight HeroPreEligibility → C2 set search → C3 order/Hero finalization。Prepass 不选择 Hero。

### F2｜Prepass 不能为所有候选生成完整封面计划

**风险：** 若把 feasibility check 实现为候选级完整 HQ/render planning，会造成计划数量膨胀，并模糊 S10/S13 边界。

**修正：** Prepass 只检查同 Anchor PHOTO eligibility 与 source-plan feasibility；完整 plan 只输出给最终 Primary Hero 与最多一个 Passive Alternate。

### F3｜Target size 必须在全部 set hard constraints 后确定

**风险：** 先锁定五项、再应用 source occupancy 或 Hero coverage，可能把本应输出三/四项的 Chapter 错判为整体失败。

**修正：** “合法集合”显式包含 C2.2、C2.3 与 HeroPreEligibility coverage；3→4→5 的停止判断在这些约束之后执行。

### F4｜搜索未完成不能伪装成没有合法 Hero

**风险：** budget/timeout 下尚未找到 Hero-covered set，如果记为 proven insufficiency，会错误排除整个 Memory 并触发 S09 re-selection。

**修正：** 只有 exhaustive/deterministic search 证明所有合法 set 均失败才可记录 `HERO_CONTRACT_UNSATISFIED`；搜索未完成仍为 operational/UNKNOWN。

## 5. 案例矩阵

| ID | 场景 | 预期合同结果 | 结果 |
|---|---|---|---|
| C01 | 三项古镇：牌坊、寺庙、塔楼，各自不同 Beat/source | Standard 3；按时间排序；核心建筑可为 Hero | PASS |
| C02 | 五座不同古建筑构成三小时 Dominant Motif | 可输出 3–5；同类别无固定配额；逐项 deletion test | PASS |
| C03 | 同一牌坊五个轻微角度 | presentation redundancy；只能保留一个代表 | PASS |
| C04 | 牌坊与塔楼相隔两分钟但实例不同 | 时间短不等于 duplicate；可共同入选 | PASS |
| C05 | 同一牌坊相隔三十分钟再次拍摄 | 时间远不自动 distinct；相似展示作用时抑制 | PASS |
| C06 | 73 秒陶艺 Manual 含准备、拉坯、成品 | 三个已验证 Beat 可通过同源三项严格例外 | PASS |
| C07 | 15 秒建筑视频仅轻微移动机位 | 一个 Beat；不得切三段占三项 | PASS |
| C08 | 五个内容都来自同一 2 分钟视频 | 同源 V1 上限三；保持三项或引入其他合法来源 | PASS |
| C09 | Compact Pair 同源：制作过程＋成品 | Pair/interval/fallback gates 通过时可发布；内部记 single-source risk | PASS |
| C10 | capacity=2，但两项是同一画面不同格式 | Compact Pair FAIL；不得伪造双素材 | PASS |
| C11 | capacity=1，存在漂亮 CONTEXT_ONLY | 不恢复弱素材、不转 Aha；proven insufficiency | PASS |
| C12 | 三项完整，第四项只是更清晰的同 Beat 图 | 替换弱项而不是增加位置；保持三项 | PASS |
| C13 | 四项完整，第五项增加独立结果 Beat | 通过 stricter fifth-item gate，可输出五项 | PASS |
| C14 | 五个候选中第五项只有画面变化 | 增量 MINOR/NONE；最终仍为四项 | PASS |
| C15 | 最佳内容 set 无 Hero PASS，另一个近似 set 有核心 Hero | 前者不合法；C2 在同一 Memory 内选择后者 | PASS after F1/F3 |
| C16 | 略暗吹蜡烛 vs 高清蛋糕静物 | core-direct 吹蜡烛优先 Hero | PASS |
| C17 | 唯一 Hero 可用但构图普通 | `HERO_READY_WITH_LIMITATION`；正常发布，不重选 | PASS |
| C18 | 所有完整 set 已证明无静态 core Hero | `HERO_CONTRACT_UNSATISFIED`；进入同一次 batch/re-selection | PASS |
| C19 | Hero source readiness 为 UNKNOWN | HOLD/BLOCK；不得排除 Memory | PASS |
| C20 | 古镇顺序 A 牌坊→B 奶茶→C 塔楼，三项均入选 | 保持 A→B→C；不为主题聚合改成 A→C→B | PASS |
| C21 | 奶茶 B 未入选，古镇 A/C 恢复主线 | 显示 A→C；不补 filler | PASS |
| C22 | 两照片同秒、无先后 Evidence | CoTemporalGroup + stable order；禁止相对时间 Claim | PASS |
| C23 | 时间证据互相矛盾且先后改变含义 | `ORDER_MATERIAL_UNRESOLVED`；HOLD/BLOCK，不重选 | PASS |
| C24 | LIVE 正文切换 PHOTO Fallback | 仍绑定原 Beat order；Chapter 不重新洗牌 | PASS |
| C25 | 最后拍摄的塔楼最代表 Chapter | 可做 Hero；正文仍留在后段 | PASS |
| C26 | Primary Hero 一次渲染超时 | transient；重试/HOLD，不激活 Alternate | PASS |
| C27 | Primary Hero source terminal，备用合照合法 | 正文 set 仍完整时激活唯一被动备用 | PASS |
| C28 | Primary source 丢失且正文从三项降为两项，Pair 不成立 | Alternate Hero 不能掩盖正文失败；原子 HOLD/BLOCK | PASS |
| C29 | Primary 与 Alternate 同 RawAsset，另有近似独立来源候选 | meaning/quality 近似时优先独立来源备用 | PASS |
| C30 | 只有一个合格 Hero member | Alternate 允许为空；不降低门槛凑备用 | PASS |
| C31 | Preview Compact 后新增合法第三项 | 同一 Memory identity 下原子升级为 Standard 3 | PASS |
| C32 | Final 仍只有高质量双素材 Pair | 可保持 Compact，不显示降级标签 | PASS |
| C33 | 第一次 S10 proven fail，批量 S09 re-selection 后仍失败 | 停止；无第三 attempt；prior 合法 Revision 可继续显示 | PASS |
| C34 | 同一视频重复导入两个文件 ID | canonical duplicate Evidence 下同 Source Family，不能绕过上限 | PASS |
| C35 | 两个独立 RawAsset 共用同一存储服务 | failure domain 风险可相同，但不能误判为同一 Source Family | PASS |
| C36 | set search 因 budget 中断，尚未找到 Hero-covered set | operational/UNKNOWN；不得记 proven fail | PASS after F4 |

## 6. 多画像语义模拟

### P1｜旅行/古镇高强度记录

~~~text
09:00 入口牌坊
09:08 石板路
09:20 寺庙大殿
09:33 木雕细节
09:45 奶茶短暂停留
10:00 独立塔楼
10:18 河边建筑
10:35 再次经过相似石板路
~~~

若 Chapter core 为古镇建筑游览，牌坊、大殿、塔楼、河边建筑可组成四项 set；木雕只有在提供重要独立 aspect 时加入或替换。奶茶只有已是合法独立 Beat 且对游逛—休息有 material contribution 时进入。最终成员按真实时间排列，Hero 可为最代表性的塔楼/大殿但不改写时间线。

**结果：PASS。** 主题一致不会被误删，偶然风格相似也不会替代具体实例判断。

### P2｜家庭生日

~~~text
18:00 准备蛋糕
18:10 点蜡烛
18:12 吹蜡烛
18:13 鼓掌
18:20 合照
~~~

五项分别覆盖准备、动作、回应与结果时可输出五项；吹蜡烛略暗但 core-direct，可胜过高清蛋糕静物成为 Hero。若 Hero source terminal，合照可作为被动备用，但正文媒体仍独立验证。

**结果：PASS。** 意义优先、五项严格门与备用边界兼容。

### P3｜创作者/长 Manual 陶艺

一段 73 秒 Manual 已由上游验证为准备、拉坯、成品三个 Beat。三项可通过同源例外并按 source offset 排列；不能再加入同源第四段普通手部画面。若只有过程与成品两项，则需通过 Compact Pair。

**结果：PASS。** 未重新定义 73 秒 Window，只消费已有验证结果。

### P4｜普通工作日稀疏记录

只有会议白板、午餐与回家路三个互不连贯候选。S09 已选择的某一短会议 Memory 若只有两项互补媒体，可走 Compact；不能为达到三项把午餐或回家路拉入同一 Chapter。若无 Hero PASS，不能用漂亮午餐补封面。

**结果：PASS。** 没有为了数量或 Hero 破坏 Memory scope。

### P5｜亲子/运动动态场景

孩子起跑、跨过终点、家人回应分别为不同 Beat；正文可混合 VIDEO/LIVE/PHOTO，但集合不要求格式配额。Hero 仍使用核心 Beat 的静态 Anchor；正文 Fallback 切换不改变 Beat 顺序。

**结果：PASS。** motion value、静态 Hero 与真实时间线保持分离。

## 7. Preview / Final 与失败分流复核

| 状态 | Preview 行为 | Final 行为 |
|---|---|---|
| 新 Revision 全部通过 | 原子发布新结果 | 原子发布 Final |
| Compact 后新增第三项 | 同 identity 原子升级 Standard | 使用完整最终 set |
| 轻微 Hero 美学限制 | 正常发布 | 正常发布 |
| proven no legal set/Hero | 可进入唯一批量 re-selection | 可进入同一唯一机会 |
| transient/UNKNOWN | HOLD prior；无 prior 则 blocked | 不伪装 Final，不替换 Candidate |
| re-selection exhausted | prior 合法 Preview 可继续访问 | `BLOCKED_NO_PUBLISHABLE_REVISION` |

未发现“累加半成品”“先展示再删除”或要求用户重新 Sync 的路径。

## 8. 成本与复杂度复核

- C1–C3 只消费已有结构化 Evidence、relations、routes、timestamps 与 quality signals；
- HeroPreEligibility 为每 candidate 一次轻量 metadata feasibility check；
- 完整 Hero plan 只为一个 Primary 与最多一个 Passive Alternate 输出；
- Alternate 正常路径不取回、不渲染，不增加上传；
- set search 为小规模 2–5 子集枚举或保持相同 objective 的 deterministic branch-and-bound；
- 不新增 VLM/strong-model 调用；
- 不请求 Raw/HQ，不修改 App、Firmware/SDK 或共享状态文件。

成本与复杂度边界通过。Production 搜索预算、S13 retry、上传完整性与 render tolerance 仍须通过真实数据 benchmark 后冻结。

## 9. 下游义务处置与开放问题

1. **S10-D runtime set survivability：** 已由 V1.21 冻结为一次 single-loss、预验证的 5→4、4→3、3→2 Compact survivor；不得链式缩减。
2. **S10-D activation collision：** 已由 V1.21 冻结为健康 Primary 锁定、预声明 Fallback 有界组合求解。
3. **S10-D/S13 request timing：** 已由 V1.21 冻结 TIER_0/1/2/3 算法请求意图；实际调度仍属 S13/App OPEN。
4. **S13 infrastructure：** transient/terminal 判定、checksum、atomic upload、retry 与 source lifecycle 数值尚未冻结。
5. **S10-D Aha：** 已由 V1.21 冻结为恰好一个 PHOTO/LIVE_2S 用户可见媒体项；supporting Evidence 不成为第二项。
6. 任意 16s/73s Manual 的 Window 规划继续 OPEN，本检查未越权补定。

## 10. 结论

S10-C 在应用 F1–F4 后通过内部交叉检查。没有发现需要推翻 Compact Chapter、adaptive 3–5、Dominant Motif、source occupancy、chronology 或 meaning-first static Hero 的核心方向。

S10-C 当前标记为：

~~~text
DESIGN CLOSED
INTERNAL CROSS-CHECK PASSED
S10-E END-TO-END CROSS-CHECK PASSED
FROZEN BY CANONICAL V1.21
~~~

该检查提出的 D1/D2/D3/D4 下游问题均已在 V1.21 解决；S13 工程数值与任意时长 Manual Window 仍保持 OPEN。
