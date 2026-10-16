# S09 Full Selection — Fine-Grained Profile Simulation V0.1

**状态：** SIMULATION COMPLETE / SUPPORTS FROZEN V1.19
**日期：** 2026-08-27
**被测设计：** S09 A1–D3 confirmed working contract
**补充关系测试：** `S09_B3_FINE_GRAINED_TIMELINE_SIMULATION_V0_1.md`
**冻结结果：** [Canonical Checkpoint V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md)

## 1. 目的与口径

本文新增五个高概率/高风险用户案例，每例使用连续 64 分钟、每两分钟一条 Auto 9s 的语义时间轴，共 32 个 Auto 时间点。与 B3 已有四例合计：

~~~text
new full-selection cases = 5 × 32 = 160 timepoints
existing B3 cases        = 4 × 32 = 128 timepoints
combined                 = 288 timepoints
~~~

表格描述“假设 Evidence 可以支持的可观察语义”，不是训练标签，也不冻结相似度、重要性或模型阈值。Manual 事件单独注明。每例在时间轴后继续检查 pool、relation、set、Revision、Day State 与 downstream readiness。

## 2. P01｜普通通勤与例行办公：不能为了数量产生 Memory

### 2.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 09:00 | 公寓走廊、走向电梯 | 普通离家 |
| 09:02 | 电梯内部、无明显互动 | 普通过渡 |
| 09:04 | 小区出口与步行 | 普通通勤 |
| 09:06 | 路口等待信号灯 | 普通通勤 |
| 09:08 | 公交站排队 | 普通通勤 |
| 09:10 | 上车、寻找座位 | 普通通勤 |
| 09:12 | 公交车内固定视角 | 普通通勤 |
| 09:14 | 车窗与道路 | 普通通勤 |
| 09:16 | 公交车内近重复画面 | 普通通勤 |
| 09:18 | 下车 | 普通过渡 |
| 09:20 | 办公楼入口 | 到达办公楼 |
| 09:22 | 电梯上楼 | 普通过渡 |
| 09:24 | 走到固定工位 | 例行办公 |
| 09:26 | 打开电脑 | 例行办公 |
| 09:28 | 浏览邮件界面、无可确认结果 | 例行办公 |
| 09:30 | 相似桌面与键盘 | 例行办公 |
| 09:32 | 去茶水间 | 普通过渡 |
| 09:34 | 咖啡机与杯子；用户拍一张 Manual Photo | 普通咖啡 |
| 09:36 | 返回工位 | 普通过渡 |
| 09:38 | 相似桌面画面 | 例行办公 |
| 09:40 | 进入小会议室 | 例行站会 |
| 09:42 | 同事与普通进度页 | 例行站会 |
| 09:44 | 持续听取进度，无可确认转折 | 例行站会 |
| 09:46 | 简短讨论，无明确成果 | 例行站会 |
| 09:48 | 离开会议室 | 例行站会结束 |
| 09:50 | 返回工位 | 例行办公 |
| 09:52 | 键盘与文档页面 | 例行办公 |
| 09:54 | 查看手机后继续工作 | 例行办公 |
| 09:56 | 取水 | 普通过渡 |
| 09:58 | 再次回到相似桌面 | 例行办公 |
| 10:00 | 持续普通电脑工作 | 例行办公 |
| 10:02 | 相似工位画面 | 例行办公 |

### 2.2 S09 模拟

- Manual 咖啡照片保留在独立 Manual 窗口，但 Manual intent 不自动产生 Aha；
- 通勤、咖啡与例行站会均无足够 Independent Memory Value；
- 若全天后续也只有同类素材，S07 无 ELIGIBLE Memory Candidate；
- S09 exact search 得到 empty proof。

~~~text
Day State = EMPTY_DAY
Chapters = 0
Ahas = 0
Readiness = EMPTY_READY_FOR_S12
~~~

**检查：** 数量目标没有把咖啡/通勤补成 Chapter；Manual 原素材没有从产品独立窗口消失。

## 3. P03｜稀疏但明确的求婚瞬间：HIGHLIGHT_DAY

### 3.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 20:00 | 公园入口与普通步行 | 普通散步 |
| 20:02 | 林荫路与同行者背影 | 普通散步 |
| 20:04 | 相似道路 | 普通散步 |
| 20:06 | 路边长椅 | 普通散步 |
| 20:08 | 继续前进 | 普通散步 |
| 20:10 | 路灯与步道 | 普通散步 |
| 20:12 | 相似步行画面 | 普通散步 |
| 20:14 | 短暂停留看水面 | 普通停留 |
| 20:16 | 继续步行 | 普通散步 |
| 20:18 | 远处人群 | 普通散步 |
| 20:20 | 自动素材因遮挡仅显示地面 | FAILED/低信息 |
| 20:22 | 自动素材运动模糊 | FAILED/低信息 |
| 20:24 | 同行者转向用户但动作不明确 | peak 前 context |
| 20:26 | 自动素材被衣物局部遮挡 | UNKNOWN |
| 20:28 | 两人停下，画面不完整 | peak 前 context |
| 20:30 | 用户手动启动 15s Video；可见对方单膝跪下并拿出戒指 | Manual local peak |
| 20:32 | Auto 画面模糊，仅见靠近/拥抱轮廓 | peak 后有限 support |
| 20:34 | 用户手动拍一张戴戒指的手部 Photo | 同一 peak 结果 |
| 20:36 | 继续拥抱/交流但画面遮挡 | peak 后 context |
| 20:38 | 恢复普通步行 | 普通散步 |
| 20:40 | 公园道路 | 普通散步 |
| 20:42 | 相似路灯和步道 | 普通散步 |
| 20:44 | 坐到长椅但无新事件 | 普通停留 |
| 20:46 | 手部与戒指偶尔入画 | peak 后重复 |
| 20:48 | 普通交流，内容不可确认 | 普通停留 |
| 20:50 | 起身继续走 | 普通过渡 |
| 20:52 | 离开湖边 | 普通散步 |
| 20:54 | 公园出口方向 | 普通散步 |
| 20:56 | 相似步行 | 普通散步 |
| 20:58 | 出口附近 | 普通散步 |
| 21:00 | 离开公园 | 普通过渡 |
| 21:02 | 街道普通步行 | 普通过渡 |

### 3.2 S09 模拟

- 有一个清晰、具体、独立的求婚 peak；Manual Video 与结果 Photo 指向同一 Aha，不重复计数；
- 普通散步不通过 Chapter Memory Value；
- 求婚素材只有两个有效 RawAsset/内容位置，不满足 Normal Chapter，15s 也不构成长 Manual exception；
- Aha 自身可理解，不依赖未入选 Chapter。

~~~text
Day State = HIGHLIGHT_DAY
Chapters = 0
Ahas = exactly 1
Readiness = READY_FOR_S10
~~~

**检查：** 强瞬间不被降成 EMPTY；也没有为了“求婚很重要”绕过 Chapter 的完整 Episode/素材门。

## 4. P04｜高强度旅行日：第五章必须真正独立

### 4.1 陶艺 Episode 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 09:00 | 进入陶艺工作室 | 到达 |
| 09:02 | 穿围裙、找到工位 | 准备 |
| 09:04 | 桌面陶土与工具 | 准备 |
| 09:06 | 老师示范揉土 | 示范 |
| 09:08 | 用户开始揉土 | 实作开始 |
| 09:10 | 把陶土放上转盘 | 实作 |
| 09:12 | 双手进行定中心 | 实作 |
| 09:14 | 形状初步升高 | 进展 |
| 09:16 | 陶坯轻微塌陷 | 局部失败 |
| 09:18 | 老师协助调整 | 修正 |
| 09:20 | 用户重新开始定中心 | 再尝试 |
| 09:22 | 陶坯恢复稳定 | 进展 |
| 09:24 | 拉高杯壁 | 进展 |
| 09:26 | 调整杯口 | 进展 |
| 09:28 | Manual Photo：成形中的杯子 | 主动记录进展 |
| 09:30 | 使用工具修整外壁 | 修整 |
| 09:32 | 清除多余陶土 | 修整 |
| 09:34 | 杯形基本完成 | 结果形成 |
| 09:36 | 老师检查作品 | 结果确认 |
| 09:38 | 用户在底部做标记 | 完成动作 |
| 09:40 | 作品从转盘移到托板 | 完成结果 |
| 09:42 | 选择釉色样本 | 后续选择 |
| 09:44 | 与老师确认烧制安排 | 后续安排 |
| 09:46 | Manual Photo：完成的陶坯 | 主动记录结果 |
| 09:48 | 清洗工具 | 收尾 |
| 09:50 | 清理桌面 | 收尾 |
| 09:52 | 脱下围裙 | 离开准备 |
| 09:54 | 浏览其他作品 | 离开准备 |
| 09:56 | 领取取件凭证 | 可观察结果 |
| 09:58 | 走向出口 | 离开 |
| 10:00 | 离开工作室 | Episode 结束 |
| 10:02 | 室外街道 | 后续过渡 |

### 4.2 同一天另外四个独立 Episode

| 时间范围 | Episode | 完整性假设 |
|---|---|---|
| 06:00–07:10 | 热气球升空—飞行—降落 | 完整且强 |
| 12:00–13:10 | 与多年未见朋友重逢午餐 | 到达、互动、告别完整 |
| 16:00–16:40 | 有准备与回应的求婚 | 完整 Episode，不只是 peak |
| 20:00–21:10 | 灯会入场—巡游—主表演—离场 | 完整且强 |

### 4.3 S09 模拟

- 五个 Chapter 全部使用独立 RawAsset、时间与 Episode progression；
- 陶艺中的塌陷/恢复可作为内容进展，但不必另拆 Chapter；
- 求婚若已有完整 Chapter，同一求婚 peak Aha 必须证明独立表达，否则不重复占位；
- P5 的每个删除投影都会失去一个未被其他 Memory 覆盖的强 Episode。

~~~text
Preview = at most 4 Chapters + at most 2 Ahas
Final = 5 Chapters only if every D2 gate PASS
Fifth result = PASS in this constructed evidence-rich case
~~~

**对照变体：** 若第五项改为“去灯会的出租车”，Important Day Omission 与 Chapter-scale Gate FAIL，Final 保持四章。

## 5. P07｜没有 Chapter 的两个独立 Aha：跨 Revision retention

### 5.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 14:00 | 图书馆固定座位 | 普通学习 |
| 14:02 | 翻阅资料 | 普通学习 |
| 14:04 | 相似桌面 | 普通学习 |
| 14:06 | 查看手机通知列表 | 普通动作 |
| 14:08 | 手机屏幕出现录取结果；用户手动拍 Photo | Aha A peak |
| 14:10 | 可见明显庆祝动作 | Aha A result |
| 14:12 | 给他人展示手机 | Aha A result |
| 14:14 | 返回座位 | 普通过渡 |
| 14:16 | 相似桌面 | 普通学习 |
| 14:18 | 继续阅读 | 普通学习 |
| 14:20 | 写笔记 | 普通学习 |
| 14:22 | 相似桌面 | 普通学习 |
| 14:24 | 短暂离座 | 普通过渡 |
| 14:26 | 走廊饮水 | 普通过渡 |
| 14:28 | 返回图书馆 | 普通过渡 |
| 14:30 | 继续阅读 | 普通学习 |
| 14:32 | 相似桌面 | 普通学习 |
| 14:34 | 写笔记 | 普通学习 |
| 14:36 | 朋友出现在走道远处 | B 前 context |
| 14:38 | 朋友走近并拿出包装物 | B 前 context |
| 14:40 | 朋友递出意外礼物 | Aha B peak |
| 14:42 | 用户接过并出现可见惊喜反应 | Aha B result |
| 14:44 | Manual Photo：礼物与两人 | Aha B result |
| 14:46 | 简短拥抱 | Aha B result |
| 14:48 | 朋友离开 | B 结束 |
| 14:50 | 用户回到座位 | 普通过渡 |
| 14:52 | 查看礼物 | peak 后重复 |
| 14:54 | 礼物放到桌边 | peak 后 context |
| 14:56 | 继续普通学习 | 普通学习 |
| 14:58 | 相似桌面 | 普通学习 |
| 15:00 | 写笔记 | 普通学习 |
| 15:02 | 相似桌面 | 普通学习 |

### 5.2 Revision 模拟

~~~text
Preview R1 input ends at 14:30
→ no Chapter
→ AH-A passes standalone
→ publish HIGHLIGHT_DAY with stable M-A

Preview R2 input reaches 15:02
→ no Chapter
→ AH-A and AH-B both pass standalone
→ HIGHLIGHT_DAY exactly-one
~~~

按 V1.1 retention，若 M-A 仍有效，R2 不能仅因 AH-B 更戏剧化替换它。应继续 M-A，并把 AH-B 记录为 `HIGHLIGHT_DAY_SINGLE_AHA_LIMIT_VALID_PRIOR_RETAINED`。这验证了 cross-check F3；该修复已回写主合同。

## 6. P08｜Direct Chapter + S08 provider failure：不能全日误阻断，也不能伪装完整召回

### 6.1 两分钟时间轴

| 时间 | 假设 Auto 9s 可观察内容 | 语义阶段 |
|---|---|---|
| 18:00 | 学校礼堂入口与家长入场 | 表演 Episode 到达 |
| 18:02 | 找到座位 | 准备 |
| 18:04 | 舞台布置 | 准备 |
| 18:06 | 主持人出现 | 开始 |
| 18:08 | 第一组学生上台 | 表演进行 |
| 18:10 | 用户孩子所在小组入场 | 核心过程 |
| 18:12 | 小组开始表演 | 核心过程 |
| 18:14 | 连续可见动作 | 核心过程 |
| 18:16 | Manual 1min Video：核心表演段 | 主动记录 |
| 18:18 | 表演继续 | 核心过程 |
| 18:20 | 小组完成动作 | 局部结果 |
| 18:22 | 观众鼓掌 | 结果 |
| 18:24 | 小组谢幕 | 结果 |
| 18:26 | 学生离开舞台 | 结束 |
| 18:28 | 下一节目开始 | 后续 context |
| 18:30 | 普通观看 | 后续 context |
| 18:32 | Manual Photo：舞台全景 | 主动记录 |
| 18:34 | 主持人再次出现 | 颁奖前 context |
| 18:36 | 多名学生被叫到舞台 | 潜在颁奖事件 |
| 18:38 | 孩子站在队列中，但奖项语音不可从视觉确认 | Aha question |
| 18:40 | Manual 15s Video：主持人口播，画面可见递交物品 | Aha question |
| 18:42 | 递交完成与合照 | 潜在结果 |
| 18:44 | 下台 | 潜在事件结束 |
| 18:46 | 返回座位 | 过渡 |
| 18:48 | 普通观看 | 普通 context |
| 18:50 | 观众鼓掌 | 普通 context |
| 18:52 | 主持人总结 | 收尾 |
| 18:54 | 人群起身 | 离场 |
| 18:56 | 走出座位区 | 离场 |
| 18:58 | 礼堂出口 | 离场 |
| 19:00 | 室外与孩子会合 | Episode 后续 |
| 19:02 | Manual Photo：孩子与手中物品，但文字不可读 | 潜在结果 support |

### 6.2 S09 模拟

- “学校表演”Chapter 由清晰 progression、多个 KEEP RawAsset/ContentUnit 支持，S07 直接 ELIGIBLE；
- “获得某奖项”Aha 需要一个具体 S08 validation question；provider failure 后为 `UNVALIDATED_OPERATIONAL`，不能入池；
- 当前合法 Chapter 本身仍真实完整，operational Aha 不使它违法；
- 但结果必须记录 recall limitation，不能声称已完整评估所有潜在 Aha。

~~~text
Selected = school performance Chapter
Day State = CHAPTER_DAY
Operationally unresolved Aha = audit only
Readiness = may proceed only if impact is classified as recall-only,
            not state/retention-critical
~~~

**对照变体：** 如果唯一可能形成 Memory 的就是失败的 provisional Candidate，不能输出 EMPTY_DAY；应 `DAY_STATE_NOT_PROPOSED` 或保持 prior Revision。

## 7. 与 B3 四例的联合覆盖

| existing B3 case | full S09 reuse |
|---|---|
| 古镇—奶茶—返回—街头表演 | relation alternatives、embedded Aha、rolling expansion |
| 生日准备—吹蜡烛—礼物 | Chapter+Aha set、same-peak duplicate、Manual near-duplicate |
| 通勤—咖啡—客户演示 | non-transitive pair conflicts、ordinary content no quota |
| 同会议室两场会议 | distinct Episode despite embedding/style similarity |

新增五例与 B3 合计覆盖 288 个两分钟语义时间点；Revision-only 的 cap/split/late-data 场景在 cross-check 报告继续单独检查。

## 8. 本轮模拟直接发现

1. `HIGHLIGHT_DAY` exactly-one 必须先执行 prior valid Aha retention，再比较新 Aha；
2. S08 operational exclusion 需要 impact classification：recall-only 不应自动阻断已有合法非空 plan，state/retention-critical 则必须阻断；
3. Empty proof 必须比非空 plan 更严格；唯一潜在 Memory 因 operational failure 未决时不能输出 EMPTY_DAY；
4. 第五章 gate 能区分五个独立强 Episode 与“第四章加普通过渡”；
5. Preview reserve 不能改写 Candidate disposition；
6. Manual intent 支持相关性，但不补 Truth、Episode 或 standalone Evidence。

## 9. 已完成的 adversarial Revision follow-up

1. Preview 四章中的一个 Chapter split 后产生五个合法 child/current Chapters：采用 `HOLD_PREVIOUS_REVISION / PREVIEW_SPLIT_CORRECTION_DEFERRED_TO_FINAL`；
2. prior HIGHLIGHT Aha 升级为 Chapter，同时新增另一个独立 Aha：允许在 `CHAPTER_DAY` 中以同一 stable ID 做 `AHA_TO_CHAPTER`，并保留独立新 Aha；
3. Final 已有五章，Late Data 产生第六个强 Episode：维持五章硬上限，不按普通 ranking 驱逐仍有效 prior Memory；
4. lineage many-to-one / one-to-many 无明确 primary core：使用 group ledger；无法证明 primary 时分配新 ID并完整保留 lineage；
5. S10 whitelist 完整但 HQ handle 尚未准备：S09 输出 availability status，不要求进入 S10 前 materialize；
6. canonical ordering：成员确定后，Chapter/Aha 各自按 capture chronology + stable identity tie-break 稳定输出。

完整结论与修复证据见 `S09_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_1.md`。
