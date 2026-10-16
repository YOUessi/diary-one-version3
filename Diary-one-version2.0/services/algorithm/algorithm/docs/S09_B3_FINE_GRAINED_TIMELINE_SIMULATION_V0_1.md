# S09-B3 Fine-Grained Timeline Simulation V0.1

**状态：** SIMULATION COMPLETE / SUPPORTS FROZEN V1.19
**日期：** 2026-08-26
**被测设计：** S09-A1–B3 confirmed working contract
**冻结结果：** [Canonical Checkpoint V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md)

## 1. 目的与边界

本报告用多个虚构用户时间轴检查 S09-B3 的关系约束是否会：

- 错误合并同一地点中的不同视觉内容；
- 错误拆开同一 Episode 中视觉不同的片段；
- 把 Chapter 内独立 Aha 当成重复；
- 把 pair conflict 错误传递给整个 connected component；
- 仅凭 embedding、场景或活动相似误判重复；
- 在关系不确定时同时选择两个高度可疑的重复 Memory。

每个案例假设从 09:00 到 10:02 每 2 分钟产生一条 9 秒 Auto Video，共 32 条 Auto RawAsset。表格只描述可能被 Evidence 支持的可观察语义，不代表真实用户、训练标签或已冻结阈值。

本报告只检查 B3 的组合合法性，不提前决定 S09-C 的最终集合目标、权重或赢家。

---

## 2. 案例一｜古镇—现代奶茶店—返回古镇—街头表演

### 2.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 09:00 | 古镇入口、牌楼与同行者进入画面 | A1 到达古镇 |
| 09:02 | 检票/入口通行区域 | A1 到达古镇 |
| 09:04 | 导览图与同行者查看路线 | A1 到达古镇 |
| 09:06 | 穿过牌楼，前方出现石板路 | A2 开始步行 |
| 09:08 | 沿石板路前进 | A2 古镇步行 |
| 09:10 | 两侧传统店铺与连续步行 | A2 古镇步行 |
| 09:12 | 木质建筑立面与同行者 | A2 古镇步行 |
| 09:14 | 小桥、河道与行人 | A2 古镇步行 |
| 09:16 | 沿河道继续前进 | A2 古镇步行 |
| 09:18 | 进入一处传统院落 | A3 院落停留 |
| 09:20 | 院内雕刻/建筑细节 | A3 院落停留 |
| 09:22 | 离开院落，重新回到街道 | A3→A4 过渡 |
| 09:24 | 石板路、人群与连续行走 | A4 继续 citywalk |
| 09:26 | 路边摊位与同行者经过 | A4 继续 citywalk |
| 09:28 | 不同古建筑外立面 | A4 继续 citywalk |
| 09:30 | 现代奶茶店外立面出现在古镇街道旁 | A4→B1 入口过渡 |
| 09:32 | 推门进入明亮现代室内 | B1 进入奶茶店 |
| 09:34 | 菜单、点单与柜台 | B2 点单 |
| 09:36 | 店员制作饮品 | B2 制作过程 |
| 09:38 | 取到饮品 | B2 结果 |
| 09:40 | 坐下喝饮品 | B3 室内停留 |
| 09:42 | 桌面饮品与同行者交流 | B3 室内停留 |
| 09:44 | 收拾杯子、起身 | B3→B4 离开准备 |
| 09:46 | 穿过店门回到街道 | B4 离开奶茶店 |
| 09:48 | 再次出现石板路与传统建筑 | C1 恢复古镇步行 |
| 09:50 | 从另一座小桥经过 | C1 古镇步行 |
| 09:52 | 河道另一侧建筑与连续前进 | C1 古镇步行 |
| 09:54 | 转入另一条传统街巷 | C1 古镇步行 |
| 09:56 | 前方出现街头表演者和围观人群 | C2 局部事件开始 |
| 09:58 | 表演者完成一个可定位动作 | C2 局部 peak |
| 10:00 | 围观者鼓掌/互动 | C2 局部结果 |
| 10:02 | 离开表演区域，继续沿古镇行走 | C3 返回主线 |

### 2.2 可能的上游分段

~~~text
Episode A: 09:00–09:30 古镇 citywalk 前段
Interruption B: 09:32–09:46 奶茶店室内停留
Episode C: 09:48–10:02 古镇 citywalk 恢复
Local Peak P: 09:56–10:00 街头表演局部事件
~~~

### 2.3 假设进入 S09 的候选

- `CH-A`：A+C `RESUMED_EPISODE`，表达古镇 citywalk；
- `CH-B`：A+B+C `LOCAL_EPISODE_GROUP`，表达包含奶茶停留的完整 outing；
- `AH-P`：街头表演局部 Aha；
- 普通“喝奶茶”若未通过独立 Memory Value Gate，不会因为是室内切换就进入 S09。

### 2.4 Pair Ledger 与 B3 约束

| pair | same/overlap evidence | distinct evidence | constraint |
|---|---|---|---|
| CH-A ↔ CH-B | 共享 A/C RawAsset、同一 outing、alternative | B 是否提供奶茶独立贡献待比较 | `FORBID_COSELECT` |
| CH-A ↔ AH-P | Aha 位于 C 内并共享 Evidence | AH-P 表达独立局部动作与结果 | `ALLOW_COSELECT` |
| CH-B ↔ AH-P | Aha 位于 broader outing 内 | AH-P 仍是独立 local peak | `ALLOW_COSELECT` |

### 2.5 B3 可以与不可以决定的内容

合法：

~~~text
{CH-A, AH-P}
{CH-B, AH-P}
{AH-P}
{}
~~~

非法：

~~~text
{CH-A, CH-B}
{CH-A, CH-B, AH-P}
~~~

B3 不能决定 CH-A 或 CH-B 谁更好；这需要 S09-C 比较奶茶段的真实新增价值、主题完整性、风险和 Revision stability。

### 2.6 检查结论

- 石板路、院落、古建筑和小桥视觉不同，但 Episode/time/context continuity 可以把它们理解为同一古镇 citywalk；
- 奶茶店是 interruption，不自动 split A/C；
- 街头表演可以作为 embedded distinct Aha 与古镇 Chapter 共存；
- broad 与 resumed Chapter 因共享 RawAsset 不能同时进入最终 set。

---

## 3. 案例二｜生日准备—惊喜进入—吹蜡烛—拆礼物

### 3.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 09:00 | 房间内布置气球 | A1 聚会准备 |
| 09:02 | 调整桌面装饰 | A1 聚会准备 |
| 09:04 | 摆放餐具和食物 | A1 聚会准备 |
| 09:06 | 蛋糕盒被放到桌边 | A1 聚会准备 |
| 09:08 | 在蛋糕附近准备蜡烛 | A1 聚会准备 |
| 09:10 | 门打开，主角/来宾进入 | B1 惊喜进入 |
| 09:12 | 房内人员做出迎接反应 | B1 惊喜反应 |
| 09:14 | 可观察的拥抱或问候 | B1 惊喜结果 |
| 09:16 | 人员落座、开始交流 | B2 聚会开始 |
| 09:18 | 分享零食/饮品 | B2 聚会进行 |
| 09:20 | 多人持续交流 | B2 聚会进行 |
| 09:22 | 有人取出蛋糕 | C1 蛋糕仪式开始 |
| 09:24 | 蛋糕被端到主角面前 | C1 蛋糕仪式 |
| 09:26 | 点亮蜡烛 | C1 蛋糕仪式 |
| 09:28 | 多人唱歌 | C1 蛋糕仪式 |
| 09:30 | 主角停留在蜡烛前 | C2 许愿阶段 |
| 09:32 | 吹蜡烛动作与火焰变化 | C2 local peak |
| 09:34 | 鼓掌和可观察反应 | C2 peak 结果 |
| 09:36 | 开始切蛋糕 | C3 仪式后续 |
| 09:38 | 分装蛋糕 | C3 仪式后续 |
| 09:40 | 多人吃蛋糕 | C3 聚会继续 |
| 09:42 | 礼物包装进入画面 | D1 拆礼物开始 |
| 09:44 | 打开包装 | D1 拆礼物过程 |
| 09:46 | 礼物内容出现 | D2 local peak/结果 |
| 09:48 | 感谢、拥抱或明确互动 | D2 结果 |
| 09:50 | 多人准备合影 | E1 合影准备 |
| 09:52 | 多人面向相机停留 | E1 合影 |
| 09:54 | 合影结束、恢复交流 | E2 聚会尾段 |
| 09:56 | 开始收拾部分桌面 | E2 聚会尾段 |
| 09:58 | 清理餐具 | E2 收尾 |
| 10:00 | 桌面基本清理完成 | E2 收尾 |
| 10:02 | 少量人员继续交流 | E2 收尾 |

### 3.2 假设进入 S09 的候选

- `CH-BIRTHDAY`：覆盖准备、惊喜、蛋糕与礼物的生日聚会 Chapter；
- `CH-CAKE`：只表达蛋糕仪式的 nested Chapter；
- `AH-SURPRISE`：09:10–09:14 的惊喜进入；
- `AH-CANDLE`：09:28–09:34 的吹蜡烛；
- `AH-GIFT`：09:42–09:48 的礼物揭示/互动；
- 收拾桌面本身不因时长充足而自动成为 Candidate。

### 3.3 Pair Ledger 与 B3 约束

| pair | relation | constraint |
|---|---|---|
| CH-BIRTHDAY ↔ CH-CAKE | RawAsset overlap + nested scope | `FORBID_COSELECT` |
| CH-BIRTHDAY ↔ AH-SURPRISE | embedded independent local event | `ALLOW_COSELECT` |
| CH-BIRTHDAY ↔ AH-CANDLE | embedded independent local event | `ALLOW_COSELECT` |
| CH-BIRTHDAY ↔ AH-GIFT | embedded independent local event | `ALLOW_COSELECT` |
| AH-SURPRISE ↔ AH-CANDLE | 不同时间、动作与结果 | `ALLOW_COSELECT` |
| AH-CANDLE ↔ AH-GIFT | 不同具体 peak | `ALLOW_COSELECT` |

若 Auto 与 Manual 分别生成两个“吹蜡烛”Aha hypothesis，它们指向同一 peak 时应在 S07 被去重；若仍进入 S09，则建立 `SAME_MEMORY_REDUNDANCY → FORBID_COSELECT`。

### 3.4 合法集合示例

~~~text
{CH-BIRTHDAY, AH-CANDLE}
{CH-BIRTHDAY, AH-SURPRISE, AH-CANDLE}
{CH-BIRTHDAY, AH-SURPRISE, AH-CANDLE, AH-GIFT}
{CH-CAKE, AH-GIFT}
~~~

“合法”只说明没有违反 B3；是否真的选择 1、2 或 3 个 Aha 仍取决于 S09-C 的独立价值和全天覆盖。

### 3.5 检查结论

- Chapter 和 Aha 共享 Evidence 不自动冲突；
- 一个 Chapter 内可以有多个不同 local peak，但不能重复同一具体事件；
- 清理、等待、普通交流不会为了补足数量自动变成 Memory；
- broad birthday Chapter 与 nested cake Chapter 不能同时占用两个 Chapter 名额。

---

## 4. 案例三｜通勤—咖啡店—办公室—重要演示：检查冲突不传递

### 4.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 09:00 | 离开住所门口 | A1 通勤开始 |
| 09:02 | 电梯内 | A1 通勤开始 |
| 09:04 | 走出建筑 | A1 通勤步行 |
| 09:06 | 人行道前进 | A1 通勤步行 |
| 09:08 | 通过路口 | A1 通勤步行 |
| 09:10 | 进入地铁站 | A2 公共交通 |
| 09:12 | 通过闸机 | A2 公共交通 |
| 09:14 | 站台等待 | A2 公共交通 |
| 09:16 | 进入车厢 | A2 公共交通 |
| 09:18 | 车厢内移动 | A2 公共交通 |
| 09:20 | 离开地铁站 | A3 通勤后段 |
| 09:22 | 沿办公区街道步行 | A3 通勤后段 |
| 09:24 | 咖啡店外立面与进入动作 | A3→B1 边界素材 |
| 09:26 | 排队 | B1 咖啡店 |
| 09:28 | 点单 | B1 咖啡店 |
| 09:30 | 饮品制作 | B1 咖啡店 |
| 09:32 | 取到饮品 | B2 咖啡结果 |
| 09:34 | 拿着饮品离店 | B2→C1 边界 |
| 09:36 | 进入办公楼大厅 | C1 办公室到达边界 |
| 09:38 | 办公楼电梯 | C1 到达办公室 |
| 09:40 | 进入工作区 | C1 到达办公室 |
| 09:42 | 放下饮品与设备 | C1 工作准备 |
| 09:44 | 打开电脑/资料 | C1 工作准备 |
| 09:46 | 与同事进入会议空间 | C2 演示准备 |
| 09:48 | 演示开始 | D1 重要演示 |
| 09:50 | 展示具体功能/内容 | D1 重要演示 |
| 09:52 | 对方提问或互动 | D1 重要演示 |
| 09:54 | 团队回应与调整 | D1 重要演示 |
| 09:56 | 演示继续并呈现结果 | D2 结果阶段 |
| 09:58 | 可观察的积极反应/鼓掌 | D2 结果阶段 |
| 10:00 | 记录后续事项 | D3 收束 |
| 10:02 | 演示结束、人员离开 | D3 收束 |

### 4.2 用于测试的三个 Chapter Candidate

只有各自已经通过上游 Memory Value Gate 时，以下候选才会进入 S09：

- `CH-A`：通勤/到达新办公区，包含 09:24 边界 RawAsset；
- `CH-B`：咖啡停留与办公室到达，包含 09:24 和 09:36 边界 RawAsset；
- `CH-C`：办公室到达后的重要演示，包含 09:36 但不包含 09:24。

如果通勤只是普通日常、没有独立记忆价值，`CH-A` 应在 S07 失败，不能为了测试图结构或凑数量而进入 S09。

### 4.3 关系与约束

~~~text
CH-A ↔ CH-B
  shared RawAsset 09:24
  → FORBID_COSELECT

CH-B ↔ CH-C
  shared RawAsset 09:36
  → FORBID_COSELECT

CH-A ↔ CH-C
  no shared RawAsset
  distinct Episode basis
  → ALLOW_COSELECT
~~~

### 4.4 关键合法性检查

合法：

~~~text
{CH-A, CH-C}
{CH-A}
{CH-B}
{CH-C}
{}
~~~

非法：

~~~text
{CH-A, CH-B}
{CH-B, CH-C}
{CH-A, CH-B, CH-C}
~~~

### 4.5 检查结论

尽管图上存在 `CH-A — CH-B — CH-C` 连通链，A 与 C 仍可同时选择。Pair conflict 不能自动传递；否则一个处于中间、范围较大的 B 会错误地压制两个彼此独立的 Memory。

---

## 5. 案例四｜同一会议室中的两场会议：检查画面相似误判

### 5.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 09:00 | 团队成员围坐在会议室 | A1 团队站会 |
| 09:02 | 屏幕/白板显示任务列表 | A1 团队站会 |
| 09:04 | 一名成员发言 | A1 团队站会 |
| 09:06 | 另一名成员回应 | A1 团队站会 |
| 09:08 | 白板上出现 blocker/任务变化 | A2 讨论问题 |
| 09:10 | 团队调整安排 | A2 讨论问题 |
| 09:12 | 分配后续事项 | A3 站会结果 |
| 09:14 | 站会结束、人员起身 | A3 站会结束 |
| 09:16 | 人员离开会议室 | B1 明确边界 |
| 09:18 | 空会议室 | B1 明确边界 |
| 09:20 | 新会议前整理桌面 | B2 重置阶段 |
| 09:22 | 连接电脑和投影 | B2 重置阶段 |
| 09:24 | 新演示页面出现在屏幕 | B2 新事件准备 |
| 09:26 | 远程客户/另一组人员进入画面 | C1 客户演示开始 |
| 09:28 | 双方问候 | C1 客户演示开始 |
| 09:30 | 展示产品页面 | C1 客户演示 |
| 09:32 | 展示具体功能 | C1 客户演示 |
| 09:34 | 对方提出问题 | C2 问答 |
| 09:36 | 演示中出现需要处理的情况 | C2 问答/调整 |
| 09:38 | 团队进行调整 | C2 调整 |
| 09:40 | 演示恢复 | C2 调整结果 |
| 09:42 | 显示可观察结果 | C3 演示结果 |
| 09:44 | 对方和团队做出反应 | C3 演示结果 |
| 09:46 | 双方讨论后续步骤 | C3 演示收束 |
| 09:48 | 记录行动项 | C3 演示收束 |
| 09:50 | 通话/会议结束 | C3 演示结束 |
| 09:52 | 团队留在会议室复盘 | D1 内部复盘 |
| 09:54 | 查看演示记录 | D1 内部复盘 |
| 09:56 | 整理下一步计划 | D1 内部复盘 |
| 09:58 | 收起设备 | D2 收尾 |
| 10:00 | 会议室恢复空置 | D2 收尾 |
| 10:02 | 用户离开会议室 | D2 收尾 |

### 5.2 候选关系

- `CH-STANDUP`：09:00–09:14 团队站会；
- `CH-DEMO`：09:26–09:50 客户演示；
- `D1` 复盘可以作为 CH-DEMO 的尾部内容；不因画面持续存在就自动成为第三 Chapter。

两场会议可能具有极高视觉相似度：同一会议室、桌子、屏幕、电脑和部分相同人物。但 distinct evidence 包括：

- 09:16–09:24 的完整结束、空房与重置边界；
- 不同参与者集合；
- 不同 activity/progression；
- 不同 observable outcome；
- 无共享 CandidateContentUnit/RawAsset。

因此关系为 `DISTINCT_EPISODE → ALLOW_COSELECT`。是否两场都值得成为 Chapter 仍取决于各自 Memory Value；普通日常站会可能在上游或 S09-C 落选。

### 5.3 边界证据缺失变体

如果 09:16–09:24 的所有 Evidence 都 FAILED/缺失，且两条 Candidate 仍表现为同一房间、相同人员和相邻时间：

- 不能凭空声称已经是两场独立会议；
- 也不能直接永久判为 duplicate；
- 当前 Revision 使用 `UNRESOLVED_POTENTIAL_CONFLICT`；
- B3 执行 `CONSERVATIVE_AT_MOST_ONE`；
- 新 Revision 获得可靠边界 Evidence 后可重新分类。

---

## 6. 四个案例的交叉检查结果

| 检查目标 | 结果 |
|---|---|
| 同一 Episode 内视觉对象变化不会自动 split | PASS |
| 明确 interruption 后可恢复主线 | PASS |
| broad/resumed alternative 不会同时选中 | PASS |
| Chapter 内不同 Aha 可共存 | PASS |
| 同一 peak 的多个载体不会重复计数 | PASS |
| pair conflict 不会沿 connected component 传递 | PASS |
| 同场景/同风格不自动判重 | PASS |
| 缺少边界证据时不会武断合并或双选 | PASS |
| 普通内容不会因为时间长或数量不足自动入池 | PASS |

## 7. 当前发现

1. B3 必须保留 pair-level constraint；只有显式 Alternative group 或共享资源集合才能建立 group/cardinality constraint。
2. `FORBID_COSELECT` 只能限制组合，不能直接决定赢家。
3. `UNRESOLVED_POTENTIAL_CONFLICT` 的 at-most-one 是 Revision-local safety guard，不是永久 duplicate disposition。
4. `ALLOW_COSELECT` 只表示组合合法，不表示两个候选都值得占用当天名额。
5. B3 未发现需要回退修改 S09-A1–B2 的结构性问题。

## 8. 后续状态

- B3 五种 executable constraint 已确认并回写 S09 主工作合同；
- S09-C 已确认按有序目标比较合法完整集合，不做简单 Top-K；
- Preview retention、cross-Revision lineage 与 conflict-pair winner 已由 C2/C3/D2 明确；
- 第五 Chapter 已由 D2 set-level marginal gate 明确；
- 真实数据中的关系标签、阈值与 calibration 继续保持 OPEN，但不构成架构冻结 blocker。
