# Diary One AI Algorithm
# 第三方全链路审计与真实数据学习计划 V0.1

> 文档性质：独立顾问审计报告，不是算法冻结结论，不是 Production Ready 声明。
>
> 审计日期：2026-09-02
>
> 审计对象：Diary One Algorithm 仓库中的 X02 V04 Research Preview、已有 S00–S13 设计、最新真实 V04 Run 与当前评估体系。
>
> 审计视角：假定审计者此前从未参与本项目，不为既有方案辩护，只根据产品目标、代码、运行记录和可验证结果作判断。
>
> 版本边界：本报告只审计算法与本地 Web 研究链路，不修改 Firmware、SDK、正式 App 或共享状态文件。

---

## 0. 如何阅读本报告

本文严格区分四类内容：

| 标记 | 含义 |
|---|---|
| `运行事实` | 已经在真实素材 Run 中发生，可由 Run Audit、Client Trace 或评估文件复核 |
| `代码事实` | 当前代码或合同中已经存在的行为，不代表产品上合理 |
| `顾问判断` | 基于证据作出的独立诊断，仍应通过更多真实数据验证 |
| `顾问建议` | 推荐的修改方向、数据规模或指标；除非以后正式确认，否则均不是冻结定义 |

特别说明：

1. 本报告中出现的样本量、阈值和通过率均为启动实验用的建议值，不应直接写成不可更改的产品合同。
2. 本报告不会承诺“训练后每个用户一定满意”。个人记忆具有主观性。我们能建立的是：事实有证据、错误有上限、评估可复现、偏好可学习、用户可纠正。
3. 之前的 `FOR_CLAUDE_ALGORITHM_WORKFLOW_AND_CROSS_VALIDATION_PACK_V0_1.md` 曾写明 V04 尚无真实 Run。此后已经产生一轮真实 V04 Run，因此那一条状态描述已过期；旧文档现只增加了一条显式状态补充，保留原历史文字，本报告以本次 V04 证据为准。

---

## 1. 执行摘要

### 1.1 一句话结论

当前 V04 已经是一个**可追踪、可运行、有一定事实约束的研究原型**，但还不是一个**能稳定理解一天、正确拆分故事、选出精彩点并让用户满意的记忆产品**。

### 1.2 最新真实 Run 说明了什么

最新 V04 真实 Run 使用 20 个视频、74 帧 Evidence，最终产出：

- 2 个 Chapter；
- 0 个 Aha；
- Chapter 之一跨越第 1、2、7、9、12、18 项，把早间街市、沿途摊位和夜市烤饼串成同一个故事；
- 另一个 Chapter 跨越第 3–19 项，把古街、河畔、树林、遛狗和古建筑串成一个大故事；
- 3 个模型提出的 Storyline 全部被确定性规则拒绝；
- 3 个已通过内容筛选的 Aha 全部因为 Writer 两次写超过 20 字而被删除。

这不是“结果数量偶尔偏少”这么简单。它暴露出的是整条链路的结构性问题：

1. 一个视频最终只形成一个资产级 Observation，长视频内部的多个内容可能被压扁；
2. 一个 Observation 被迫归入一个 Primary Focus，真实生活中的多重语义被单标签化；
3. Storyline 用“相同 Focus + 相邻成员间隔不超过 8”进行链式连接，可能横跨大量中断；
4. One Story Gate 目前主要验证候选是否符合自己先设定的 Focus，不能真正证明“它只讲一个故事”；
5. Aha 选择近似按候选先后取前 3 个，缺少价值排序与候选间去重；
6. 内容已经成立时，文案格式失败仍会把整条记忆删除；
7. 当前 Web 测试用导入顺序模拟时间线，无法验证真实时间分段和中断后续接；
8. 20 个素材已让用户等待约 5.4 分钟，若沿用当前串行方式处理高强度日，时间与成本均存在明显放大风险。

### 1.3 最重要的判断

**现在不适合直接对现有整条链路做端到端训练。**

原因不是数据不够多，而是当前学习目标还没有被正确拆开：

- “画面里客观有什么”与“用户觉得什么值得记住”不是同一标签；
- “相邻片段是否连续”与“分散片段是否属于同一 Storyline”不是同一任务；
- “素材画质”与“记忆价值”不是同一个质量分；
- “故事内容成立”与“文案有没有超过 20 字”不能共享一个生死开关。

如果直接用当前结果和简单星级训练，模型很可能学会复现现有错误，而不是改善用户体验。

### 1.4 建议采用两层修改路线

第一层是 **V04.1 止损版**：先修复会直接毁掉结果的逻辑，包括 Aha 被 Writer 删除、链式超长聚类、伪 One Story Gate、候选按先后截断、时间可信度未区分、标签和评分合同缺陷。

第二层是 **V05 结构版**：把处理单位改为：

```text
Frame
  → Window Observation
  → Content Unit
  → Asset Rollup
  → Moment
  → Storyline Candidate
  → Daily Chapter / Aha Set
  → Media / Copy / Tags
```

这里最关键的变化是：**不再把“一个文件”默认等同于“一个语义单元”，也不再把“一个 Primary Focus”默认等同于“一个故事”。**

### 1.5 当前能力的独立评分

以下是顾问评分，不是测试结论：

| 能力 | 5 分制判断 | 说明 |
|---|---:|---|
| 可追踪性与审计 | 4.0 | Run、阶段状态、候选去向和模型用量已有较好记录 |
| 视觉事实约束 | 3.0 | 有 Fact 与 Evidence Frame 绑定，但 OCR、关系、事件强度仍可能误判 |
| 时间线可信度 | 1.0 | 当前真实测试仍使用导入顺序构造 2 分钟间隔 |
| Chapter 聚类 | 1.5 | 能形成主题，但容易过度合并，也会漏掉稀疏但重要的故事 |
| Aha 有效性 | 0.5 | 有候选路径，但本轮最终为 0，选择与 Writer 均有致命问题 |
| 文案自然度 | 1.5 | 有事实约束，但仍偏事实清单，且格式失败会删除内容 |
| Canonical Tag 完整性 | 1.5 | 架构方向合理，当前词表覆盖不足 |
| 成本与时延可扩展性 | 1.5 | 20 个视频约 5.4 分钟，当前固定批次和串行处理不适合高强度日 |
| 训练准备度 | 1.0 | 有评估外壳，但缺少可训练 Gold、用户级拆分和盲评流程 |
| 用户满意度闭环 | 1.0 | 尚未形成轻量反馈、修改行为和长期回看指标闭环 |

---

## 2. 产品目标与审计基准

### 2.1 目标输入规模

高强度参考日为：

- 5 小时佩戴；
- Auto 每 2 分钟拍 9 秒，共约 150 段 Auto Video；
- Manual Photo 20 张；
- Manual Video：10 段 15 秒、3 段 1 分钟、3 段 2 分钟，共 16 段；
- 合计约 186 个 Raw Assets；
- 视频总时长约 34 分钟，另有 20 张照片。

### 2.2 目标输出

一般希望一天得到：

- 3–4 个 Chapter；
- 丰富日可以接受 5 个，但不是为了凑数；
- 每个 Chapter 选择 3–5 个精选素材；
- 一般日 1–2 个 Aha，丰富日可达 2–3 个；
- 数量是质量筛选后的结果，不是无条件配额。

### 2.3 用户体验原则

- 用户 Sync 后，后续上传与处理应无感进行；
- 中间结果采用替换、合并、拆分和修订，不无限累加；
- Manual 素材可以在 Chapter/Aha 候选中因相似而被抑制，但必须保留在 Manual 窗口和事实账本；
- Chapter 是一段相对完整的生活经历或发现线，一到两句话即可；
- Aha 是能独立回看的局部精彩、意外或发现，不是 Chapter 的重复缩写；
- 文案可以有克制的共识性情绪，但不能虚构关系、情绪、因果、偏好或主观体验；
- 中文 Aha 当前目标不超过 20 个可见字符；这是一项展示合同，不应反向杀死已经成立的记忆内容。

### 2.4 审计的核心问题

本报告不只问“代码有没有运行”，而是问：

1. 每一步的输入单位是否正确？
2. 上一步的错误会不会在后面被放大且无法修正？
3. 算法是在发现故事，还是在把素材塞进预设桶？
4. 输出少是因为没有内容，还是因为工程合同误杀？
5. 当前成本和等待时间能否承受 186 个素材？
6. 真实用户反馈能否成为无泄漏、可训练、可复现的数据？
7. 用户能否纠正结果，而不破坏事实账本？

---

## 3. 当前全链路：从素材到结果

### 3.1 当前研究链路

```text
用户在 Web 选择一批手机素材
  ↓
浏览器生成抽帧 Evidence，并人为按导入顺序分配时间
  ↓
S00–S02 绑定测试日、加载 Bundle 与 Evidence
  ↓
S04 依次执行多批视觉理解，并生成资产级 Observation
  ↓
S04 确定性校验
  ↓
S05–S07 执行一次模型 Structure Proposal
  ↓
S03–S07 执行确定性 Boundary、Moment、Role 与 Candidate 逻辑
  ↓
V04 Storyline Focus 分组与 One Story Gate
  ↓
S08/S09 选择全天 Chapter / Aha 集合
  ↓
S10 选择展示媒体
  ↓
S11 Writer 写标题、故事、Aha，并生成 Tags
  ↓
S12 只读校验；失败项被阻断
  ↓
Web 显示 Staged Preview
```

这段顺序描述的是当前真实执行，而不是理想顺序。当前 V04 并没有在视觉模型前运行一套能显著减少 VLM 输入的 S03 Cheap Signal；真实 Run 是先执行 4 批 S04 Perception，再进入模型结构提案和 S03–S07 的确定性结构逻辑。

### 3.2 目标中的正式链路

正式产品还应包含：

- App 侧增量 Sync、后台上传与断点续传；
- 真实 capture time、设备来源、时区与时间可信度；
- Rolling Preview 的版本替换；
- 当日 Finalization；
- S08 只针对真正不确定点补证；
- S13 对最终选中素材请求 HQ、渲染并导出；
- 用户修改、撤销、删除、重排、反馈及其审计边界；
- 线上成本、超时、降级、并发、缓存和版本回滚。

最新 V04 Web Run 中，S13 明确未执行；S08 也没有形成完整的“只为一个未知点补证”的生产流程。因此不能把这轮 Run 称为完整 Production 验证。

---

## 4. 最新真实 V04 Run：事实与因果复盘

### 4.1 Run 身份

`运行事实`

| 字段 | 值 |
|---|---|
| Run ID | `58465e4b-743c-49af-85a3-93531dcb9b4d` |
| Session ID | `776e2afb-abb1-4259-8aed-5a20e4dd5394` |
| 记录时间 | `2026-09-02T06:21:53.692569Z` |
| Pipeline | `X02_STAGED_REAL_MEDIA_PREVIEW_V04` |
| Schema | `DIARY_ONE_X02_STAGED_PREVIEW_V04` |
| 模型 | `qwen3-vl-flash-2026-01-22` |
| 模式 | `FRESH_FULL_RUN` |
| 输入 | 20 个视频，74 帧 Evidence |
| 上传 Evidence | 9,022,849 bytes |
| 模型调用 | 7 次 |
| Input Tokens | 114,196 |
| Output Tokens | 13,581 |
| 服务耗时 | 209.383 秒 |
| 浏览器抽帧 | 114.882 秒 |
| 用户总等待 | 324.510 秒，约 5.4 分钟 |
| 代码配置估算成本 | 0.00520846 美元 |
| 最终结果 | 2 Chapter，0 Aha |

### 4.2 Chapter 候选发生了什么

`运行事实`

确定性分组只生成并选中了两个可用候选：

1. `LOCAL_COMMERCE`：6 个成员，来源序号为 1、2、7、9、12、18；
2. `ROUTE_SCENERY`：10 个成员，来源序号为 3–6、8、10–11、14–15、19。

模型另外提出三个更细的 Storyline，但全部被硬规则拒绝：

| 模型 Storyline | 被拒绝原因 | 顾问解释 |
|---|---|---|
| `LOCAL_COMMERCE_MARKET_CORE` | `STORYLINE_BASIS_FOCUS_MISMATCH` | 模型不能真正挑战已有 Focus 体系 |
| `ROUTE_SCENERY_WALKING_PATHS` | `STORYLINE_MEMBER_PRIMARY_FOCUS_MISMATCH` | 只要成员被确定性函数分到别的 Focus，模型建议即失效 |
| `CULTURE_ARCHITECTURE_DISCOVERY` | `STORYLINE_CONTENT_UNIT_COUNT_INVALID` | 只有 2 个成员，而当前最低需要 3 个 |

这意味着模型不是一个真正的“结构发现者”，更接近在确定性桶内提交建议。当前确定性分类一旦错，模型很难纠正。

### 4.3 为什么“市集街巷”聚类过大

`运行事实`

最终 Chapter 的时间范围是“第 1–18 项”，内部记录了 12 个 interruption observations。它同时包含：

- 中式牌坊和街市；
- 多个蔬菜、水果摊；
- 中途其他场景；
- 夜市白色顶棚和“衢州烤饼”招牌。

`代码事实`

当前“间隔受限”检查主要看相邻两个同 Focus 成员的最大序号差。只要：

```text
成员 A → 间隔不超过 8 → 成员 B → 间隔不超过 8 → 成员 C
```

链就可以继续延伸。它没有可靠限制：

- 候选的总跨度；
- 中断内容占比；
- 从早市到夜市是否已经变成两个 Episode Instance；
- 中断后是否有足够“恢复原故事”的证据。

`顾问判断`

这是典型的 single-link chaining 问题：局部相邻关系成立，不代表全局仍是同一故事。

### 4.4 为什么“古街河畔行”也过大

`运行事实`

该候选包含古街石板路、河边小船、垂柳倒影、树林步行、遛狗和古建筑。虽然都能宽泛归入“沿路景致”，但用户想回看的很可能是几个不同的记忆职责：

- 古镇漫步；
- 河畔自然景观；
- 古建筑文化发现；
- 宠物同行或局部互动。

`顾问判断`

“Route Scenery”是一个过宽的上位主题，足以说明内容相关，却不足以证明它们应该成为同一个 Chapter。

### 4.5 One Story Gate 为什么没有拦住

`代码事实`

当前候选只要通过结构和 Focus 一致性校验，就会记录类似：

- thesis 来自 Primary Focus；
- 每个成员都有 beat contribution；
- 候选内部没有另一个 Primary Focus；
- 然后判定 `PASS`。

`顾问判断`

这是一个循环证明：

```text
先按同一个 Focus 把素材放在一起
→ 再因为它们都是同一个 Focus
→ 证明它们是同一个故事
```

真正的 One Story Gate 应该主动寻找反证，而不是只确认已有标签。例如：

- 能否将候选切成两个各自更完整、主题更清楚的故事？
- 中断是否比连续内容更多？
- 第一项与最后一项是否仍共享具体事件实例，而不只是共享“逛街”这种大类？
- 每个成员承担的 Beat 是否真有推进，还是仅仅被统一贴为 `DISCOVERY`？

### 4.6 文化建筑为什么消失

`运行事实`

模型提出了 `CULTURE_ARCHITECTURE_DISCOVERY`，但因为仅 2 个成员而被拒绝。

`顾问判断`

“至少 3 个文件”不是稳定的故事充分性定义：

- 一段 2 分钟视频内部可能有 3 个清楚的文化细节；
- 两个文件可能分别是建筑外观与木雕细节，已经构成完整的双面发现；
- 反过来，5 个高度重复的石板路文件也不必然构成好 Chapter。

最低门槛应改为“足够的 Content Units / Beats / Evidence”，而不是固定文件数。

### 4.7 Aha 为什么最终为 0

`运行事实`

系统找到 5 个 eligible Aha：

- 两个遛狗片段，被标为 `PLAYFUL_ANIMAL`；
- 一艘载红花的小船，被标为 `DISCOVERY`；
- 祈福相关发现；
- 石碑或标牌相关发现。

当前先选择了最早出现的 3 个：两个遛狗片段和红花小船；后两个被 `AHA_PREVIEW_CAPACITY_REACHED` 排除。

随后 Writer 两轮输出如下：

| Aha | 第一次 | 第二次 | 上限 |
|---|---:|---:|---:|
| 遛狗片段 1 | 33 字 | 38 字 | 20 字 |
| 红花小船 | 34 字 | 39 字 | 20 字 |
| 遛狗片段 2 | 32 字 | 38 字 | 20 字 |

三项全部被 `NO_VALID_WRITER_OUTPUT_AFTER_BOUNDED_RETRY` 阻断，最终用户看见 0 个 Aha。

`顾问判断`

这里至少有三个独立问题：

1. **事件膨胀**：普通跟随犬只行走不一定等于“调皮、活泼的局部精彩”；
2. **候选间不去重**：两个相似遛狗片段同时占用三个名额中的两个；
3. **展示合同绑架内容**：内容候选已经成立，却因为文案超过 20 字而整项消失。

正确做法应是：内容先进入 `CONTENT_READY`，文案若失败则使用安全短句回退，并把自然文案放到后台重写，而不是删除记忆。

### 4.8 Tags 暴露的问题

`运行事实`

“市集街巷”最后只得到 `CENTRAL_SUBJECT.FOOD_OR_DESSERT`。

`代码事实`

当前 Tag Maps 缺少或没有充分覆盖：

- `COMMERCIAL_MARKET`；
- `BROWSING`；
- `MARKET_VISIT`；
- 更细的本地文化、市集、摊贩与发现类标签。

`顾问判断`

Canonical Tags 对未来检索很重要，不能只靠少量映射后以“多数票 + 每个 facet 取一个”的方式代替完整本体设计。

### 4.9 OCR 和隐私无关但与事实质量相关的问题

`运行事实`

Observation 和 Claim 中出现了具体牌匾文字、路牌文字，素材中也可能出现车牌。

`顾问判断`

即使暂时不展开完整隐私与伦理体系，也必须处理事实可靠性：

- OCR 文字可能错；
- 小字可能被模型补全；
- 车牌等细节通常与记忆叙事无关；
- 低置信 OCR 不应直接进入用户文案或搜索主索引。

建议把 OCR 作为独立事实类型，带置信度、区域坐标和“是否允许进入叙事”的开关。

### 4.10 成本和时延的放大风险

`运行事实`

20 个视频：

- 抽帧约 1.91 分钟；
- 服务约 3.49 分钟；
- 总等待约 5.4 分钟；
- 114,196 input tokens；
- 当前配置估算约 0.0052 美元。

`顾问建议，仅作线性敏感性分析`

如果机械按素材数量从 20 放大到 186，而没有并发、动态批次、缓存和增量处理：

- 抽帧可能约 17.8 分钟；
- 服务可能约 32.5 分钟；
- 总等待可能约 50.3 分钟；
- 单日模型配置估算约 0.048 美元；
- 30 天约 1.45 美元。

这不是正式 Benchmark，只说明当前串行方案的量级风险。真实高强度日还可能受到：

- 2 分钟视频带来更多帧；
- S08 补证；
- 重试；
- Writer、标签或未来 Embedding 调用；
- 32k 上下文或价格档位变化；
- 网络与并发限制。

因此不能仅凭 20 素材的低 API 金额判断“成本没有风险”。当前更大的近期风险其实是用户等待时间和 Token 浪费。

---

## 5. 十一项跨阶段结构问题

### 5.1 串行且有损的错误传播

如果 S04 把一个场景误判为 `ROUTE_SCENERY`，后面的 S07、S09、S11 都会在错误标签上继续工作。当前缺少允许下游用强证据挑战上游标签的正式通道。

### 5.2 处理单位错误

一个 Asset 不一定只有一个语义。一段 73 秒视频可以经历：走进店、点单、甜品上桌、第一口反应。把它压成一个 Observation，会丢失边界和局部高潮。

### 5.3 单一 Primary Focus 过度简化

一段“古牌坊下的早市”同时具有：历史建筑、地方市集、步行进入、当地文化发现。单一 Focus 会强迫算法提前放弃其中三条解释。

### 5.4 Episode、Topic、Storyline 混用

“都发生在古镇”是 Day Episode；“都看见古建筑”是 Topic；“从牌坊进入老街并发现木雕细节”才可能是 Storyline。当前规则仍容易把前两者当成第三者。

### 5.5 时间代理不可信

导入顺序被映射为每项相隔 2 分钟，只能用于界面和顺序实验，不能用于真实 Continuity、长中断、回归同一故事或“上午/夜市”的结论。

### 5.6 一个 quality_score 混合太多含义

当前分数容易同时承担：清晰度、证据充分、审美、故事相关、个人价值和可展示性。一个模糊但珍贵的生日瞬间可能因此被误删。

### 5.7 候选生成和选择目标错位

候选生成应高召回，选择阶段再高精度。当前很多硬门槛在候选阶段就不可逆删除，导致稀疏文化故事和少量素材日被过早判死。

### 5.8 Chapter 与 Aha 没有真正联合选择

Aha 不能只判断“是否在 Chapter 时间线中”，而要判断“是否承担了不同记忆职责”。当前两个集合仍主要分开处理，容易重复或相互挤压。

### 5.9 Writer 和内容生死耦合

Writer 是表达层，不应该拥有删除已成立记忆的权力。格式错误应进入 Copy Fallback，不应变成内容不存在。

### 5.10 评估只能批评结果，不能训练组件

现有 Human Evaluation V02 可以记录某个 Run 的意见，但缺少：用户事前 Day Map、缺失故事、边界、候选排序、替代分法、评审角色、盲评状态和训练授权。

### 5.11 成本优化没有进入架构

当前固定每批 6 个 Assets，而不是按帧数、图像字节、预计 Token 和模型上下文动态组批。六个 2 分钟视频与六张照片不应使用同一批次合同。

---

## 6. S00–S13 独立逐阶段审计

## S00 — Day Run / Snapshot

### 当前职责

定义这次处理属于哪一天、哪次 Run、使用哪个输入快照和算法版本。

### 主要问题

- `运行事实`：当前 Web 把“一次导入”当作“一天”；
- `运行事实`：没有 GPS 和真实拍摄时间时，导入顺序被当作时间顺序；
- `顾问判断`：同一素材不同排序可能得到不同 Moment、Storyline 和 Aha，结果不可被当成真实日序列质量。

### 修改建议

每个 Run 必须记录：

- `timeline_source = CAPTURE_TIME | FILE_TIME | IMPORT_ORDER_SYNTHETIC`；
- `timeline_confidence = HIGH | MEDIUM | LOW`；
- 时区来源；
- 是否允许时间语义进入文案；
- 是否可参与“真实分段”评估。

当时间为合成时，仍可评价视觉理解、主题聚类和写作，但不得把边界准确率计入正式成绩。

### 案例

用户先选了夜市视频，再选早市视频。若系统按导入顺序推断“从夜市走到早市”，这是测试适配层制造的假故事，不是算法发现。

### 应测指标

- 时间来源覆盖率；
- 时间冲突率；
- 同一批素材不同导入顺序的结果稳定性；
- 使用真实时间与合成时间时的边界差异。

## S01 — Media Normalize / Decode

### 当前职责

识别照片或视频、读取时长和尺寸、解码可用性、准备后续 Evidence。

### 主要问题

- 长视频、旋转视频、可变帧率、HDR、损坏尾帧可能造成耗时或抽帧失败；
- 目前“文件是否可解码”与“内容是否值得记住”必须完全分开；
- 一批内单个异常文件不应阻断其他素材。

### 修改建议

- 每资产独立超时、失败隔离和可复现 reason code；
- 保存原始时长、有效时长、解码覆盖率；
- 对超长视频先建立轻量时间索引，再按 Window 取样；
- 不因 normalize 失败推断内容无价值，只标记 `TECHNICAL_UNAVAILABLE`。

### 案例

一段 2 分钟视频最后 3 秒损坏。系统应仍使用前 117 秒可解码内容，而不是让整个素材和同批其他 5 个素材一起失败。

### 应测指标

- 成功解码率；
- 单资产 P50/P95 处理时间；
- 局部损坏恢复率；
- 批次级联失败率。

## S02 — Window / Frame Evidence

### 当前职责

从视频的一个或多个 Window 中抽帧，为视觉理解提供证据；照片直接成为 Evidence。

### 当前优点

- 9 秒 Auto 已有固定三帧的手机侧合同；
- 云端可采用保守的 1-or-3 上传，不需要回头请求另外两帧；
- Manual 长视频根据实际时长使用多个 Window，是正确方向。

### 主要问题

- `运行事实`：20 个视频抽出 74 帧，浏览器串行准备约 115 秒；
- `代码事实`：当前帧使用 `CENTER_CROP_ASPECT_FILL`，可能裁掉边缘主体；
- 固定时间点可能错过很短的动作峰值；
- 资产级 Observation 没有保留每个 Window 的独立语义。

### 修改建议

1. 每个 Window 至少保留一张低分辨率全画幅锚点；
2. 中心裁切只作为补充，不是唯一证据；
3. 用运动、场景变化或声音峰值触发至多 1 张额外帧；
4. 保留 `window_id`，后续 Observation 必须按 Window 生成；
5. 抽帧并行化，但设置设备温度、内存和最大并发；
6. 相似度只减少云端上传，不改变本地固定抽帧合同。

### 案例

16 秒视频：可用两个局部 Window，每个 Window 先取早/晚证据；若两个 Window 视觉近乎相同，则云端可只上传最有代表性的一个 Window 证据。

73 秒视频：应有多个 Window，且每个 Window 分别形成 Observation；如果第 20 秒在逛店、第 60 秒在喝奶茶，不能合成一个模糊标签。

### 应测指标

- 关键内容 Frame Recall；
- 中心裁切主体丢失率；
- 每分钟抽帧时间；
- 相似度减帧后的语义漏失率；
- Window 内与 Window 间覆盖率。

## S03 — Cheap Signals / Edge Preparation

### 当前职责

在昂贵视觉模型前后提供低成本信号，例如感知哈希、清晰度、场景变化、时间间隔、轻量 Embedding 和相邻关系。

### 主要问题

- `顾问判断`：当前研究链路中 Cheap Signals 并没有显著减少 VLM 覆盖，所有资产仍会进入视觉理解；
- 当前批次按 6 个 Assets 固定组包，不按帧数或 Token；
- 相似度如果过早用于删除，会漏掉“同类但不同意义”的古建筑；
- 便宜信号和最终语义决策的职责仍不够清楚。

### 修改建议

Cheap Signals 只做四件事：

1. 技术质量估计；
2. 近重复候选标记；
3. 场景变化提示；
4. 为 VLM 动态组批和补帧提供预算依据。

它不应单独决定“是不是同一 Chapter”。组批应受以下上限共同约束：

- 最大帧数；
- 最大图片字节；
- 预计视觉 Token；
- 最大资产数；
- 同批语义连续性只是软约束。

### 案例

两张古建筑外观相隔 20 分钟、结构明显不同。感知相似度可能较高，但它们可能是旅途中的两个关键建筑；Cheap Signal 只标记“同类”，由 Storyline 与媒体去重层判断是否都保留。

### 应测指标

- VLM Token 节省率；
- 被 Cheap Signal 抑制内容的人工漏失率；
- 动态批次超限率；
- 同等质量下的成本下降。

## S04 — Observation Lite

### 当前职责

把视觉 Evidence 转成受控结构：场景、活动、主体、事件、motifs、事实、质量与限制。

### 当前优点

- Facts 能绑定 Evidence Frame；
- 非关键字段错误可降级，而不一定删除整个 Observation；
- 本轮 20 个 Observation 都被接受，3 个发生字段降级，没有整项失败。

### 主要问题

- 当前一个资产只形成一个 Observation，而不是一个 Window 一个 Observation；
- 当前最多 6 个资产的所有 Evidence 帧会进入同一条模型消息，语义上下文没有物理隔离；Prompt 要求“独立分析”不能保证模型不借用相邻素材的信息；
- 事实、场景、事件强度、个人价值混在同一模型输出中；
- 受控词表会将真实生活强行压进少量代码；
- motifs 归一化当前只保留 ASCII 小写字母、数字、下划线和横线，模型若返回中文 motif 会被清空；
- OCR 可能被当成强事实；
- 部分模型 HTTP、非 JSON 或结构化输出错误会被直接向上抛出，可能终止整个 Day Run，不只是让当前 6 个资产失败；
- 当前 JSON Object 模式并不等于服务端严格 Schema 保证。

这里还需要澄清当前“Grounding”的真实强度：

- Observation Validator 主要证明引用的 Frame ID 属于该素材；
- Writer Validator 主要证明引用的 Claim ID 在允许集合中；
- 二者都没有独立证明“这句语义断言确实能由对应画面推出”。

因此，现阶段的 Grounding 更准确地说是“引用链合法”，不能被团队误解为“事实蕴含已经通过验证”。

### 修改建议

把 S04 拆成两个内部层次：

```text
Perception Fact Layer
  - 可见对象、动作、场景、OCR、质量、证据帧、置信度

Semantic Interpretation Layer
  - episode hypotheses、activity、event hypothesis、multi-facet labels
```

并且：

- 每 Window 一个 Observation；
- 传输层可以并发或批量调度，但每个 Asset/Window 的模型语义上下文应彼此隔离；不能用共享消息节省少量调用，却牺牲局部事实合同；
- 一个字段可以有 `top_k hypotheses + confidence`，而不是只给一个答案；
- OCR 使用独立置信度和叙事准入规则；
- motif 支持 Unicode，或在 Prompt 中明确只允许稳定英文 canonical code；
- 失败后按二分法缩小并落到单资产隔离；可重试错误不得终止整天，真正不可恢复错误也必须保留已完成资产；
- 将事实改成可验证 predicate，并对高影响 Claim 增加独立语义 Verifier；
- 对关系、情绪、意图保持 `UNKNOWN`，除非有用户事实。

### 案例

画面是“牌坊下有菜摊，人正在走过”。客观事实可以确定；但它同时可能属于：

- 古镇入口；
- 早市；
- 当地生活发现；
- 城市漫步的起点。

S04 应保留多个语义假设，不能在这里永久选掉三个。

### 应测指标

- Fact Precision / Recall；
- 事实置信度校准误差；
- Episode Top-k Recall；
- Event Kind 混淆矩阵；
- OCR 字符准确率和错误进入叙事率；
- 批次失败隔离率。

## S05 — Moment Formation

### 当前职责

通过相邻 Observation 的 Continuity Evidence 和 Boundary Evidence，把全天时间线切成局部 Moment。

### 当前优点

- 双向证据账本是正确架构：不仅找“为什么连”，也找“为什么断”；
- JOIN / SPLIT / DEFER 的显式状态有利于审计。

### 主要问题

- `代码事实`：episode 或 setting 变化通常直接增加 Boundary；
- `代码事实`：只要 edge 不是 JOIN，Moment 构建就新开一组，因此 DEFER 在实际分组时等同 SPLIT；
- 设计中已有 Pending Window / Pending Block，但当前 V04 没有实现真正的有限前后看；
- 合成时间线使真实边界评估失真；
- 只看相邻边无法解决“古镇 A → 奶茶店 B → 古镇 C”的跨中断续接。

### 修改建议

Moment Formation 与 Storyline Resumption 分两层：

1. **Moment** 只做局部连续分段；
2. **Storyline** 可以在后面基于强恢复证据把 A 与 C 归为同一故事，但必须保留 B 为独立 Moment；
3. DEFER 进入有限 Pending Block，观察后续 1–2 个可靠 Content Units 后再决定；
4. 若证据用尽仍无法归左或归右，则作为独立单元进入 Aha 候选；不成立则丢弃，不强塞左右。

### 案例

```text
09:00 古镇牌坊
09:02 菜摊
09:04 石板路
09:20 奶茶店点单
09:24 甜品上桌
09:40 回到古街木雕店
09:44 古建筑外观
```

局部 Moment 应至少为 A、B、C 三段。后续 Storyline 可以判断 A+C 是“古镇文化漫步”的两段续接，B 则可能成为“奶茶小憩”或一个独立 Aha。不能在 S05 就把三段全部合并，也不能永久禁止 A+C 再连接。

### 应测指标

- Boundary F1；
- Pk / WindowDiff；
- DEFER 最终决策准确率；
- 中断后 Storyline 恢复 Precision / Recall；
- 过分割与欠分割的用户级比例。

## S06 — Material Role Assignment

### 当前职责

为 Observation 指定 `KEEP`、`CONTEXT_ONLY` 或 `DROP`，决定它在 Memory 生成中的作用。

### 主要问题

- `代码事实`：无效 quality 会回退到恰好 `0.35`；
- `代码事实`：只有 `< 0.35` 才进入 `CONTEXT_ONLY`；因此无效 quality 的 0.35 仍可能成为 KEEP；
- 视觉质量与记忆价值被单一 quality_score 绑定；
- Manual 素材虽不享有免去重权，但其主动拍摄行为仍可能是个人价值信号，当前没有单独保留。

### 修改建议

拆分至少五个维度：

- `visual_usability`：是否看得清；
- `evidence_adequacy`：事实是否有足够证据；
- `story_relevance`：对候选故事是否有贡献；
- `novelty`：是否提供新信息；
- `personal_value_prior`：Manual、停留、重复主动拍摄等弱先验。

Role 应是候选相关的，而不是资产永久属性。同一素材可以在 Chapter A 中 `CONTEXT_ONLY`，在 Aha B 中 `KEEP`。

### 案例

一张轻微模糊的生日吹蜡烛照片，视觉可用性一般，但个人价值很高。它不能因为画质低直接 DROP；同时它也未必应成为独立 Aha，因为它可能与生日 Chapter 是同一个故事职责。

### 应测指标

- 每类 DROP 的人工误杀率；
- 模糊但高价值素材保留率；
- Role 与最终用户保留行为的相关性；
- 无效分数字段的降级覆盖测试。

## S07 — Chapter / Aha Candidate Generation

### 当前职责

高召回地提出可能的 Chapter Storyline 和 Aha，不负责最终数量。

### 主要问题：Chapter

- 单 Primary Focus 和硬编码优先级决定候选身份；
- 目前 Focus 数量和定义不足以覆盖生活多样性；
- 模型 Storyline 不能有效挑战确定性 Focus；
- “至少 3 个文件”会误杀证据密集的短故事；
- 间隔不超过 8 的链式分组会形成超长跨度；
- One Story Gate 没有真正比较拆分方案；
- 同一个 basis 下，Beat 可能被机械地全部标为 `DISCOVERY`，并不是真正叙事推进。

### 主要问题：Aha

- 事件峰值与独立记忆价值没有分成两个判断；
- 普通遛狗被放大为 `PLAYFUL_ANIMAL`；
- Discovery 与 Event 路径虽已出现，但排序和去重不完整；
- 稀疏日应该努力发现小精彩，但不能靠降低事实门槛来凑数。

### 修改建议

Chapter 候选采用高召回的多路生成：

1. 局部连续 Episode Candidate；
2. 中断后恢复的 Storyline Candidate；
3. 同一 Day Episode 下的不同故事职责候选；
4. 多面发现候选，例如外观 + 内部细节；
5. 模型提出的替代切分；
6. 人类规则生成的 split alternatives。

候选保留多 Facet：

```text
setting: HISTORIC_STREET
activity: WALKING / BROWSING
subject: HISTORIC_ARCHITECTURE / MARKET_STALL
experience: LOCAL_CULTURE_DISCOVERY
episode_instance: OLD_TOWN_MORNING_01
```

One Story Gate 必须回答：

- 具体 thesis 是什么？
- 每个 Content Unit 对 thesis 有什么不可替代贡献？
- 是否存在更好的二分或三分？
- 总跨度和中断占比是否合理？
- 首尾是否属于同一 Episode Instance 或有明确 Resumption Evidence？
- 候选是否只是共享大类主题？

Aha 采用两个分数头：

- `local_peak_groundedness`：局部事件或发现是否真实发生；
- `independent_memory_value`：是否值得脱离 Chapter 单独回看。

### 案例：同一上午三个古镇 Chapter 是否合理

如果三小时素材丰富，可以形成：

1. 古镇散步：石板路、河畔、桥、行走推进；
2. 古镇文化体验：牌楼、建筑外观、木雕细节；
3. 当地生活发现：早市、摊贩、地方食物。

它们共享“古镇旅游”这一大 Episode，但承担不同 Storyline Duty。相反，如果只有三张高度相似的石板路，不应为了 3 个 Chapter 而拆分。

### 应测指标

- Gold Storyline Candidate Recall；
- 候选池平均规模；
- 人工补充但系统未生成的 Missing Candidate Rate；
- One Story Purity；
- 过合并、过切分；
- Aha Event 与 Discovery 分路径的 Recall@K。

## S08 — Targeted Enrichment / Validation

### 当前职责

当一个候选只缺一个关键证据时，以最低成本补证，不做全量二次理解。

### 主要问题

- 当前 Web V04 尚未完整验证这一生产形态；
- 如果 S07 结构本身错误，S08 补再多证据也只是强化错误候选；
- 补证问题、预算和停止条件需要与候选具体绑定；
- 不能在 1 帧不确定后再次向 App 请求另外两帧；已有产品决策是错过就错过，不增加工程往返。

### 修改建议

只允许四类明确问题：

1. 候选内部是否为同一具体对象或地点实例；
2. 某个 Content Unit 是否含候选必需 Beat；
3. Aha 的动作前后是否成立；
4. 某一 Claim 是否有足够可见证据。

动作顺序：

```text
复用已上传 Evidence
→ 使用本地 Cheap Signal
→ 在已有 3 帧中选择更多帧参与模型
→ 若仍不确定，候选降级或排除
```

不设计“云端再向手机取另外两帧”的复杂闭环。

### 案例

一张帧像是木雕，但细节太小。S08 可以使用同一已上传 Window 的另外两帧确认；若仍看不清，就把“木雕”改为“建筑细节”或排除该 Claim，而不是要求用户再次上传原视频。

### 应测指标

- 每个被救回候选的增量 Token；
- 补证后 Precision 提升；
- 无效补证率；
- 单日 S08 预算超限率。

## S09 — Daily Editorial Set Selection

### 当前职责

从全天候选中选出一组互补、清楚、有代表性的 Chapter 和 Aha。

### 当前优点

- 已有 Pair Ledger 和 Exact Search 框架；
- 已声明数量不是配额；
- 当前 Objective 名义上把合法性、独立故事数量和 Focus 多样性置于素材覆盖之前。

### 主要问题

- 当前候选池本身只有两个可用 Chapter，S09 无法恢复已经在 S07 被删掉的文化候选；
- `INDEPENDENT_STORYLINE_COUNT` 仍容易把“选得更多”置于“每一个真的更好”之前；
- 相同 Focus + Gap 冲突可能压掉同类但不同 Episode Instance；
- Aha 实际按候选顺序受 3 个容量限制，本轮两个相似遛狗占了两个位置；
- Chapter 与 Aha 没有统一做“故事职责覆盖与重复惩罚”；
- Rolling Revision 的稳定性尚未用真实多次 Sync 验证。

### 修改建议

选择目标应按以下顺序约束：

1. 事实与 One Story 合法；
2. 每项独立价值超过最低线；
3. 严重错误合并和重复为硬惩罚；
4. 覆盖当天用户认为重要的 Storyline；
5. Chapter 间职责互补；
6. Aha 与 Chapter、Aha 与 Aha 之间职责独立；
7. 数量只在质量相近时作为 tie-break；
8. Revision Stability 与新信息收益共同决定是否替换。

不建议训练一个单一“总分”直接决定一切。应保留多目标和硬约束。

### 案例

候选集包含：古镇散步、古建筑文化、当地市集、两个相似遛狗、红花小船、祈福发现。合理结果可能是 3 个 Chapter + 红花小船或祈福 Aha，而不是 2 个大 Chapter + 两个重复遛狗 Aha。

### 应测指标

- Selected Chapter Precision；
- Desired Storyline Recall；
- Chapter Set Purity；
- Missing / Over-merge / Over-split；
- Aha NDCG / Recall@K；
- 集合内重复率；
- Revision Churn 与有意义替换率。

## S10 — Final Media Selection

### 当前职责

为每个 Chapter 选 3–5 个媒体，为 Aha 选一个核心媒体，并确定 Hero。

### 主要问题

- 当前 Chapter 选择倾向“首项 + Hero + 尾项 + 补满”，不等于真正覆盖 Story Beats；
- 候选本身错误时，S10 会把错误故事包装得更完整；
- 3–5 是最终展示范围，不应变成尽量填到 5；
- Manual 主动拍摄是个人价值信号，但不能凌驾于重复和画质；
- 目前 Web Preview 主要显示 Evidence Photo，不代表最终视频/照片格式决策已验证。

### 修改建议

先列出 Chapter 必须覆盖的 Beats，再选媒体：

```text
Entry / Context
Progression / Variety
Core Discovery or Interaction
Closure or Representative End
```

每个媒体需要说明：

- 覆盖哪个 Beat；
- 相比已选媒体新增了什么；
- 为什么是 Hero；
- 为什么没有选相似素材；
- 最终展示照片还是视频。

### 案例

古建筑 Chapter 有牌坊外观、另一座不同建筑外观、木雕细节、重复石板路。可以选两张时间相隔较远且建筑确实不同的外观，再加木雕细节；不必因为都叫“古建筑”就全部去重，也不应选三张同一建筑不同角度。

### 应测指标

- Beat Coverage；
- 媒体间近重复率；
- Hero 人工偏好胜率；
- 3、4、5 素材版本的用户偏好；
- 被用户替换 Hero 的比例。

## S11 — Claims / Writer / Canonical Tags

### 当前职责

从已批准 Facts 中选 Claims，生成 Chapter 标题和一到两句话、Aha 短句，并生成可检索 Canonical Tags。

### 当前优点

- Writer 必须引用 Fact IDs；
- 禁止无证据的关系、情绪、偏好、因果和夸张词；
- Chapter 标题和 Aha 字数有显式校验；
- 有一次受限重试。

### 主要问题

- 本轮 Aha 第二次重试反而更长；
- Writer 既写又被同一合同证明合规，缺少独立的内容规划和验证；
- Chapter 文案仍像事实清单；
- Aha 格式失败会删除内容；
- Tags 词表和映射不全，内部多标签信息被压为有限展示标签；
- 低置信 OCR 可能进入 Claim；
- 中文 20 字合同不能直接复用到英语等海外语言。

### 修改建议

把 S11 拆为：

1. `Content Plan`：决定要表达哪 1–3 个 Claims；
2. `Grounded Writer`：写自然文案；
3. `Independent Validator`：事实、禁词、长度、语言与格式校验；
4. `Safe Copy Fallback`：Writer 失败时使用确定性短句；
5. `Background Rewrite`：不阻断 Memory 的情况下再优化表达。

状态应为：

```text
CONTENT_READY_COPY_READY
CONTENT_READY_COPY_FALLBACK
CONTENT_BLOCKED_FOR_EVIDENCE
```

而不是把 Copy 失败和内容无效混为一谈。

Canonical Tags 应：

- 内部允许多标签；
- UI 每个 facet 可以只展示一个；
- 词表版本化；
- 记录父子层级和同义词；
- 把 Episode、Setting、Activity、Subject、Occasion、Experience 分开；
- 训练检索标签与用户展示标签分开。

### 案例

红花小船的保守回退短句可以是“河畔小船载着红花”。它少于 20 字、有画面感且不虚构。如果模型写成 34 字，不应该让这个 Aha 从结果中消失。

### 应测指标

- Claim Grounding Precision；
- 合同一次通过率与回退率；
- 用户对自然度的成对偏好；
- 用户修改文案比例；
- Tag Micro/Macro F1；
- 英文及目标语言的独立通过率。

## S12 — Read-only Final Validation

### 当前职责

只检查，不跨阶段静默修复；确保最终输出结构、事实、媒体、文案和标签满足合同。

### 当前优点

- 不允许 S12 偷偷重写上游结构；
- 阻断原因能够归责到具体阶段。

### 主要问题

- 当前很多校验偏 Schema 和字段规则，语义校验不足；
- Frame ID/Claim ID 属于允许集合，只能证明引用合法，不能证明画面语义蕴含最终断言；
- One Story 的 `PASS` 已经由上游循环逻辑给出，S12 没有真正复核；
- Writer 字数是硬阻断，而部分更严重的故事混合却能通过；
- `EMPTY_DAY` 可能由工程合同失败造成，却看起来像“用户这一天没有值得记住的内容”。

### 修改建议

S12 增加只读语义检查：

- Chapter 内是否存在两个竞争 thesis；
- 每个最终 Clause 是否能由其绑定的 Predicate 与 Evidence 独立支持；
- 总跨度和中断比是否异常；
- 选中 Aha 是否互相重复；
- Aha 是否只是 Chapter 同一故事的缩写；
- Claim 是否包含低置信 OCR；
- Copy 失败是否已有安全回退；
- 输出为 0 时，是 `NO_CONTENT`、`NO_GROUNDED_CANDIDATE` 还是 `PIPELINE_FAILURE`。

对用户的空结果文案应中性，例如：“这批素材还没有形成足够清楚的章节。”不能暗示用户的一天没有价值。

### 案例

如果系统已有 3 个有效 Aha Candidate，但 Writer 全部超长，S12 应输出 3 个 Copy Fallback 并记录 Writer Failure；不能输出 `EMPTY_DAY` 或 0 Aha。

### 应测指标

- 语义错误漏过率；
- 错误空日率；
- 上游失败归责准确率；
- Validator 与人工审核的一致率。

## S13 — HQ Materialization / Export

### 当前职责

只对最终选中的素材请求或定位 HQ 原件，渲染用户可见 Memory，并导出完整审计记录。

### 当前状态

- `运行事实`：本轮为 `NOT_EXECUTED_IN_WEB_PREVIEW`；
- 当前只能审计 Preview Evidence，不可据此宣称 HQ 画质、视频裁剪、下载、导出或最终 App 展示已通过。

### 修改建议

- 先完成内容选择，再取 HQ，避免全量云存储和带宽；
- 每个最终媒体必须可追溯到 Raw Asset 与 Frame/Window；
- HQ 获取失败不应让整个 Chapter 消失，可降级为 Preview 或替换备选；
- 导出包分离用户内容、运行审计与评估数据；
- 记录源文件可用性、转码、裁剪、封面和渲染版本。

### 案例

Chapter 已选中 4 个素材，其中一个 HQ 原视频损坏。系统应从同一 Beat 的备选素材替换，或暂用清晰 Preview；不能删除整个 Chapter，也不能静默换成无关画面。

### 应测指标

- HQ 命中率；
- HQ 失败替换成功率；
- 最终媒体与 Preview 身份一致率；
- 导出完整性与端到端耗时。

---

## 7. 优先级：P0 / P1 / P2

## 7.1 P0：不修就不能相信下一轮质量结果

| 编号 | 问题 | 必须达到的结果 |
|---|---|---|
| P0-1 | 时间来源不可信 | 合成顺序明确标记，不参与真实边界结论 |
| P0-2 | Asset 级 Observation 压扁长视频 | 至少保留 Window 级 Observation 和 Content Unit 身份 |
| P0-3 | One Story Gate 循环证明 | 引入拆分挑战、竞争 thesis、总跨度和中断比例 |
| P0-4 | Primary Focus 不可被挑战 | 模型或多 Facet 证据可以提出合法替代 Storyline |
| P0-5 | Aha 顺序截断与重复 | 按独立价值排序，Aha-Aha 去重，时间仅作 tie-break |
| P0-6 | Writer 失败删除内容 | 增加 `CONTENT_READY_COPY_FALLBACK` |
| P0-7 | 质量分合同缺陷 | 拆分评分，并修复 0.35 回退与 `<0.35` 的边界错误 |
| P0-8 | 缺少可训练 Gold | 建立 Owner Day Map、边界、候选、排序和缺失项标注 |
| P0-9 | 6 资产共享语义上下文，部分调用错误可终止整天 | Asset/Window 语义隔离；以帧、字节、Token 动态调度；失败后缩小并保留已完成结果 |
| P0-10 | 空结果归因不清 | 区分没有内容、没有可靠候选与工程失败 |
| P0-11 | 当前 Grounding 只证明引用链合法 | Predicate/Clause 级语义蕴含验证，高影响 Claim 使用独立 Verifier |

## 7.2 P1：结构可用后立即补齐

- S08 的候选绑定式补证与成本预算；
- 真实时间与多次 Sync 的 Rolling Revision；
- Chapter/Aha 联合选择；
- Story Beat 驱动的 3–5 媒体选择；
- Canonical Tag 完整本体与多语言表示；
- OCR 置信度与叙事准入；
- 用户轻量修改：删除、补入、拆分、合并、换 Hero、隐藏或提升 Aha；
- Quick Review 与 Expert Review 两套评估界面；
- 多场景回归集：旅行、普通日、工作、家庭、宠物、稀疏日、低质量日。

## 7.3 P2：质量链路稳定后再做

- 组件级微调或偏好训练；
- 长期个性化；
- 增量云端队列、并发与缓存优化；
- 多语言 Writer 与海外 Release Gate；
- 大规模在线实验；
- Production HQ、导出、存储生命周期和完整隐私治理。

---

## 8. V04.1：建议的止损版本

V04.1 的目标不是一次重写全部架构，而是让下一轮真实测试不再被已知工程缺陷污染。

### 8.1 必做修改

1. Aha 候选按 `独立记忆价值 × 证据强度 × 新颖度` 排序；
2. Aha-Aha 去重，两个相似遛狗不能默认占两个名额；
3. Writer 两次失败后生成安全短句，不删除 Candidate；
4. One Story Gate 增加总跨度、中断比例、候选二分挑战；
5. `source_order_gap <= 8` 不再单独允许跨越全天链式连接；
6. 模型候选允许挑战确定性 Focus，但必须给可审计证据；
7. Culture/Architecture 等稀疏候选允许“2 个高信息 Content Units”路径；
8. 修复 motif 的中文清空风险；
9. 修复 quality `0.35` 回退仍 KEEP 的边界不一致；
10. 补齐市集、浏览、本地生活等 Tags；
11. Asset/Window 语义上下文隔离、动态调度，以及失败缩小重试；单次模型错误不能终止整天；
12. 标记合成时间线，不在文案中使用真实时间含义；
13. Human Review 记录每个 Chapter、媒体、文案、Aha、缺失项和建议，而非只有整体星级。
14. 明确区分“引用链合法”和“语义有画面支持”，为高影响 Claim 增加独立检查。

### 8.2 V04.1 不应假装解决的内容

- 它仍不能完全替代 Window → Content Unit 的 V05 结构；
- 它不能证明穿戴式 Auto 数据表现，因为当前是手机素材；
- 它不能证明三个人之外的泛化；
- 它不能证明长期个性化；
- 它不能证明 Production 时延和成本；
- 它不能通过多写 Prompt 根治结构分段问题。

### 8.3 V04.1 下一轮最低验收

以下是验收原则，不是冻结数值：

- 已成立 Aha 不再仅因文案超长而消失；
- 同一类重复 Aha 不连续占满容量；
- 第 1–18 项的链式候选必须被拆分挑战；
- 模型提出的文化候选有可解释的救回或拒绝路径；
- 每个候选能显示“为什么进、为什么没进、输给谁”；
- 合成时间不能被误写成真实早晚或持续时长；
- 一批失败不影响其他批次；
- 结果评估能精确指向 Chapter、媒体、文案或缺失故事。

---

## 9. V05：建议的结构修正

## 9.1 新的核心对象层级

### Frame

某一个准确时间点的视觉证据，不承担完整语义。

### Window Observation

短时间范围内可见的事实与局部动作。一个长视频可以有多个。

### Content Unit

语义连续且能独立说明“这里发生了什么”的最小单位。它可以：

- 由同一视频的一个或多个 Window 组成；
- 把一个长视频拆成多个 Content Units；
- 在两个短文件高度连续时合并为一个 Content Unit。

### Asset Rollup

保存原文件、Manual/Auto 来源、时长、质量和所有 Window 的映射。它是账本对象，不再是故事对象。

### Moment

时间上局部连续的一组 Content Units。

### Storyline Candidate

能够说明一个具体记忆职责的候选，可跨一个短中断恢复，但必须有 Resumption Evidence。

### Chapter / Aha

从全天候选中联合选择出的用户记忆；Chapter 是一段故事，Aha 是独立局部精彩或发现。

## 9.2 多 Facet 取代单 Primary Focus

每个 Content Unit 可同时拥有：

- Setting；
- Activity；
- Subject；
- Episode Hypothesis；
- Experience / Discovery；
- Event Peak；
- Episode Instance；
- Temporal Segment；
- Personal Value Prior；
- Evidence Confidence。

Primary Focus 可以在某个候选内部临时选择，但不再成为资产永久标签。

## 9.3 真正的 One Story Gate

建议使用“生成—反证—比较”的流程：

1. 生成一个候选 thesis；
2. 为每个 Content Unit 写一句 contribution；
3. 找出不能贡献的成员；
4. 生成最佳二分和三分方案；
5. 比较原候选与拆分候选的：纯度、完整性、重复、跨度、中断、用户价值；
6. 只有原候选显著更合理时才 PASS；
7. 证据接近时保留多个方案给 S09 或人工评估，不强行提前唯一化。

## 9.4 Storyline 恢复

古建筑景区 A → 奶茶店 B → 古建筑景区 C 的处理建议：

- A、B、C 在局部时间线上保持三个 Moment；
- A 与 C 如果共享具体地点实例、路线推进、建筑风格序列或明确回到原路线，可成为一个带中断的 Storyline；
- B 如果只是短暂停留，可以独立成为 Aha 或小 Chapter；
- B 若持续很久且形成完整饮品体验，则它是独立 Chapter；
- 若 A、C 只是两个不同古镇区域，仅共享“古建筑”大类，则不应自动合并。

## 9.5 Chapter 与 Aha 联合选择

为每个候选增加 `memory_duty`：

- `EPISODE_SUMMARY`；
- `CULTURAL_DISCOVERY`；
- `LOCAL_LIFE_DISCOVERY`；
- `EVENT_PEAK`；
- `PERSONAL_INTERACTION`；
- `VISUAL_SURPRISE`；
- `TRANSITION_CONTEXT`。

选择时比较 Duty，而不是只比较时间重叠。吹蜡烛通常是生日 Chapter 的核心 Beat，不必再做 Aha；古镇旅行中的红花小船可以承担 `VISUAL_SURPRISE`，即使位于古镇 Chapter 时间线内，也有资格成为独立 Aha。

## 9.6 Writer 与事实分离

内容对象在 Writer 之前就必须完整成立。Writer 只负责表达，不负责决定记忆存在与否。

建议引入：

```text
Memory Content Object
  - thesis
  - beats
  - selected_claim_ids
  - selected_media_ids
  - memory_duty

Copy Object
  - locale
  - title
  - body
  - writer_version
  - validator_status
  - fallback_status
```

这样将来切换 Qwen Writer、其他模型或英语 Writer，不会改变 Chapter/Aha 本身。

---

## 10. 真实素材如何变成可训练数据

## 10.1 先区分两种真值

### Evidence Truth：客观证据真值

由不认识素材主人的标注员根据画面判断：

- 看到了什么；
- 是否发生了动作；
- 场景是否变化；
- 哪些帧支持事实；
- 哪些内容看不清；
- 是否存在 OCR；
- 两个单元是否有视觉连续或边界证据。

### Owner Preference：主人偏好真值

由素材本人判断：

- 哪些经历最代表这一天；
- 哪些素材有个人意义；
- 希望怎样分 Chapter；
- 哪些 Aha 值得单独保存；
- 哪个 Hero 更喜欢；
- 文案是否自然、是否像自己、是否愿意保留。

两者必须分开。不能让盲标员猜用户关系、情绪和偏好，也不能把用户说“这是我最爱的店”反向训练成“只看画面就能知道这是最爱”。

## 10.2 最小授权边界

即使完整隐私治理以后再展开，用真实素材做训练前仍必须区分：

- 仅用于本次处理；
- 允许内部人工评估；
- 允许算法离线测试；
- 允许模型训练；
- 允许发送第三方模型 API；
- 保存期限与删除请求。

这些不是要求现在完成全部伦理产品设计，而是训练数据是否合法、可追踪的最低前提。授权范围必须随素材、派生帧、Embedding、标签和训练样本传递。

## 10.3 数据层级

建议数据主键层级：

```text
User
  └── Day / Trip
       └── Sync Session
            └── Asset
                 └── Window
                      └── Frame
```

任何训练、验证和测试拆分都必须优先在 User 层完成，不能随机把同一人的相邻素材拆到训练集和测试集。

## 10.4 标注层次

### L0 — Provenance 与技术状态

- 用户、日期、设备、素材来源；
- Manual / Auto；
- 时长、方向、时间可信度；
- 授权范围；
- 解码、抽帧、画质问题。

### L1 — Owner Day Map，必须在看 AI 结果前完成

素材主人先回答：

- 今天主要发生了什么；
- 希望看到哪些 1–5 个 Chapter；
- 哪些小瞬间值得成为 Aha；
- 哪些内容明确不重要；
- 哪些故事允许合并，哪些必须分开。

如果主人先看了 AI，再补答案，会产生锚定偏差，不能作为独立 Gold。

### L2 — Frame / Window Evidence

由盲标员标：

- 可见事实；
- 主体、动作、场景；
- 关键帧；
- 质量；
- OCR 与置信度；
- 是否漏掉关键动作。

### L3 — Content Unit 与 Boundary

- Window 如何合成 Content Unit；
- Asset 内是否要切开；
- 相邻单元 JOIN / SPLIT / DEFER；
- Continuity Evidence；
- Boundary Evidence；
- 中断后是否恢复；
- 接受多个合理分法，而不是强迫唯一答案。

### L4 — Storyline Gold

- Storyline thesis；
- 成员 Content Units；
- Episode Instance；
- 每个成员的 Beat contribution；
- 必须拆分和可以合并的替代方案；
- 缺失 Storyline；
- 过合并、过切分和污染成员。

### L5 — Aha 与集合偏好

- Event Aha 与 Discovery Aha 分开；
- 是否真实局部峰值；
- 是否有独立记忆价值；
- 与 Chapter 是否重复；
- Aha-Aha 是否重复；
- 候选成对排序；
- 用户希望保留、隐藏或提升。

### L6 — Media / Writer / Tags

- 3–5 个媒体是否覆盖 Story Beats；
- Hero 成对偏好；
- 文案事实性；
- 文案自然度与虚构感；
- 用户修改后的版本；
- Canonical Tag 多标签 Gold；
- 中文和目标语言分别评估。

## 10.5 不能只标选中的内容

为了避免选择偏差，每个标注日还必须抽查：

- 系统选中的候选；
- eligible 但未选中的候选；
- 被规则拒绝但风险较高的候选；
- 随机未使用素材；
- 用户主动补充的 Missing Storyline / Missing Aha。

否则系统永远只会证明自己选中的东西不错，却不知道漏掉了什么。

## 10.6 评审角色

建议至少三类角色：

1. **Owner**：提供主观价值和最终偏好；
2. **Blind Evidence Annotator**：只看素材，不知道 Owner 解释和模型答案；
3. **Adjudicator / Expert**：处理分歧、维护 Rubric 和困难案例。

每条标注记录：

- reviewer role；
- 是否 Owner；
- 是否看过模型输出；
- rubric version；
- 标注耗时；
- 置信度；
- 分歧和裁决。

---

## 11. 防止过拟合和数据泄漏

### 11.1 拆分顺序

必须按以下优先级隔离：

```text
User 隔离
  > Day / Trip 隔离
  > Session 隔离
  > Asset 隔离
  > Window / Frame 隔离
```

同一用户、同一次旅行、同一视频的相邻帧不能跨 Train / Validation / Test。

### 11.2 近重复清理

使用：

- 文件哈希；
- 感知哈希；
- 视觉 Embedding 近邻；
- 拍摄时间和设备信息；
- 视频片段重叠检测。

任何近重复只能留在一个数据分区。

### 11.3 当前三套素材的正确定位

- 素材包 1 已经影响过规则设计，应固定为 Development Regression Set；
- 素材包 2、3 在第一次完整盲跑前可作为探索性诊断；
- 一旦团队看过结果并据此改规则，它们也成为 Development Set；
- 三套素材都不能作为正式泛化证明；
- 手机素材不能代表穿戴式第一人称 Auto 数据分布。

### 11.4 锁定测试集

正式 Holdout 应满足：

- 用户从未出现在训练或开发中；
- 素材从未参与 Prompt、规则或本体设计；
- 评估人员不知道版本身份；
- 运行前固定代码、Prompt、模型、价格配置和 Rubric；
- 失败后不能边看测试集边修，再把同一集合称为测试集。

### 11.5 模型和 Prompt 泄漏

要记录：

- Prompt 版本；
- Few-shot 案例来源；
- 是否包含测试素材描述；
- 外部模型版本；
- 缓存命中；
- 规则是否因某个 Holdout 案例临时添加。

---

## 12. 建议的数据阶段与规模

以下数字是顾问建议的启动范围，不是冻结指标。每一阶段是否扩大，应根据学习曲线和错误饱和度决定。

## Phase A — Rubric Discovery

建议：

- 20–30 位参与者；
- 每人 2–3 天；
- 共 40–90 个用户日；
- 覆盖旅行、普通日、工作、家庭、宠物、稀疏和低质量日。

目的：

- 定义 Content Unit、Storyline 和 Aha 的共同语言；
- 找到标注歧义；
- 修正词表和 UX 反馈方式；
- 暂不训练模型。

退出条件：

- 标注员对事实和边界有可接受一致性；
- Owner 能在 3–5 分钟内完成 Day Map；
- 大多数分歧可由 Rubric 解释，而不是靠猜。

## Phase B — Prompt / Rule / Ranker Prototype

建议：

- 60–120 位参与者；
- 200–400 个用户日；
- 约 10,000–30,000 个 Content Units；
- 额外收集 60–100 个 Hard Days。

Hard Days 包括：

- 同一地点长时间相似内容；
- 中途离开再返回；
- 很少素材但有一个精彩点；
- 多个宠物或多人互动；
- 室内外快速切换；
- 低光、模糊、遮挡；
- 长视频内部多事件；
- 多次 Sync 和顺序混乱。

目的：

- 比较 Prompt 和模型；
- 调整边界、候选和选择器；
- 训练轻量排序器；
- 不急于微调视觉大模型。

## Phase C — 组件级训练

建议先看学习曲线，再决定是否达到：

- 20,000–60,000 条相邻边；
- 5,000–15,000 个 Storyline Candidates；
- 5,000–15,000 个 Aha Candidates；
- 10,000–30,000 对媒体偏好；
- 5,000–15,000 对 Writer 文案偏好。

只有当 Prompt / Rule / Embedding Baseline 已经稳定，且新增数据仍明显改善，才进入微调。

## Phase D — Locked Offline Holdout

建议：

- 100–200 个用户日；
- 至少 50 位完全未见用户；
- 场景分层采样；
- 全程盲评；
- 版本冻结后一次运行。

目的：

- 判断事实、切分、Chapter、Aha、Writer 和 Tags 是否达到上线候选水平；
- 估计不同用户和场景的置信区间，而不是只看总体均值。

## Phase E — 内部 Beta 与长期满意度

建议：

- 100–300 位用户；
- 连续使用 14–28 天；
- 以用户或用户周为 A/B 单位；
- 观察 7 天和 30 天回看、删除、修改、关闭功能。

目的：

- 验证真实多次 Sync、Revision Stability、等待体验和长期价值；
- 防止只优化“第一次看起来不错”。

---

## 13. 哪些组件适合训练，哪些先不要训练

| 组件 | 近期建议 | 原因 |
|---|---|---|
| S00/S01 | 确定性工程 | 身份、时间、解码不需要学习模型决定 |
| S02 | 先规则 + 轻量事件检测 | 抽帧合同需要可预测和低成本 |
| S03 | Embedding / 轻量分类可学习 | 适合近重复、场景变化和动态组批 |
| S04 | 先 Prompt / 模型比较 | Ontology 未稳定前微调容易固化错误标签 |
| S05 | 可训练边界分类器 | 有足够正负边与真实时间后价值明确 |
| S06 | 多维评分 + 硬规则 | 不应用一个黑盒总分决定生死 |
| S07 Chapter | 高召回生成 + Storyline Ranker | 需要允许多个候选和多个可接受分法 |
| S07 Aha | Event 与 Discovery 两个模型头 | 两类 Aha 的证据和价值不同 |
| S08 | 先确定性预算策略 | 先证明补证问题和收益，再学习调度 |
| S09 | 约束优化器 | 学习 utility，但保留事实、重复和数量硬边界 |
| S10 | 成对媒体排序 | Owner 对 Hero 和素材组合的偏好适合 pairwise learning |
| S11 Writer | Prompt/Few-shot → 偏好训练 | 先稳定 Claim 和语言合同，再做风格个性化 |
| Tags | 多标签分类 | 必须先稳定 Canonical Ontology |
| S12/S13 | 确定性 | 最终验证、身份和导出不能依赖不可控生成 |

### 13.1 不建议当前做的事

- 不用用户的总星级直接端到端微调整条模型；
- 不把现有 V04 输出当作伪 Gold；
- 不让视觉模型从 Owner 评价学习猜测人物关系或内心情绪；
- 不用三套素材反复调参后再报告“测试通过”；
- 不因“希望每天都有 Aha”而训练模型夸大普通动作；
- 不在 Ontology 每周变化时训练昂贵模型。

### 13.2 Active Learning

真实数据积累后，优先送人工标注的不是随机简单样本，而是：

- 模型置信度低；
- 两个模型分歧大；
- 规则和模型冲突；
- Owner 删除但系统高分；
- Owner 主动补入但系统漏掉；
- One Story 拆分方案接近；
- Aha Event 与 Discovery 难区分；
- Writer 多次回退；
- 新用户、新场景、新设备分布。

---

## 14. 离线指标与用户满意度指标

## 14.1 事实与 Evidence

- Fact Precision / Recall；
- Evidence Frame Recall；
- Crop Loss Rate；
- OCR Accuracy；
- Unsupported Claim Rate；
- Confidence Calibration；
- 批次失败隔离率。

## 14.2 Moment 与 Storyline

- Boundary Precision / Recall / F1；
- Pk 与 WindowDiff；
- Resumption Precision / Recall；
- Storyline Candidate Recall；
- Member Purity；
- Core Beat Coverage；
- Over-merge / Over-split；
- Missing Storyline Rate；
- Interruption Ratio 分布。

## 14.3 Chapter Set

- Selected Candidate Precision；
- Owner Desired Storyline Recall；
- Chapter Pair Redundancy；
- Day Coverage；
- Chapter 数量分布，而非只看平均 3–4；
- Revision Stability；
- 用户保留、拆分、合并和删除率。

## 14.4 Aha

Event 和 Discovery 必须分别报告：

- Candidate Precision / Recall；
- Recall@K；
- NDCG；
- Independent Memory Value；
- Aha–Chapter 重复率；
- Aha–Aha 重复率；
- 错误 0 输出率；
- 普通动作被夸大为 Aha 的比例；
- 用户保留、隐藏和提升率。

## 14.5 Media

- Beat Coverage；
- 近重复率；
- Hero Pairwise Win Rate；
- 用户换 Hero 比例；
- 最终 3/4/5 媒体数量偏好；
- HQ 获取成功率。

## 14.6 Writer 与 Tags

- Claim Grounding；
- Contract Pass Rate；
- Copy Fallback Rate；
- 自然度成对偏好；
- “像事实清单”比例；
- 用户编辑距离；
- Tag Micro/Macro F1；
- 记忆检索成功率；
- 各语言独立指标。

## 14.7 系统指标

- 每用户日模型调用数；
- 输入/输出 Token；
- API、存储和带宽成本；
- P50/P95 端到端完成时间；
- 抽帧 P50/P95；
- 高强度日超时率；
- 重试和降级率；
- 增量 Sync 的缓存收益。

## 14.8 用户满意度

Quick Review 建议只问少量、可行动问题：

1. 这些 Chapter 是否代表了今天？
2. Chapter 之间是否分得清楚？
3. 有没有漏掉重要经历？
4. Aha 是否值得单独保留？
5. 文案是否自然且可信？

同时记录真实行为：

- 保留、删除、编辑；
- 拆分、合并；
- 补入素材；
- 更换 Hero；
- 隐藏或提升 Aha；
- 完成修改所需时间；
- 7 天和 30 天回看；
- 分享只作为辅助，不作为唯一目标；
- 是否关闭自动 Memory 功能。

Expert Review 只对抽样 Run 做深度逐项标注，不能让普通用户每天填写复杂表格。

---

## 15. 建议的初始质量门槛

以下仅用于 Phase A/B 建立第一版 Dashboard，必须经真实分布校准，不能直接冻结：

| 项目 | 建议起始观察线 | 性质 |
|---|---:|---|
| 高风险 Fact Precision | 约 98% 或更高 | 事实安全候选线 |
| Chapter Member Purity | 约 85% 或更高 | 需按场景报告 |
| Owner Desired Storyline Recall | 约 80% 或更高 | 防止只做高精度低召回 |
| 严重 False Merge 用户日占比 | 约 10% 或更低 | 重大体验错误 |
| Aha Candidate Precision | 约 75% 或更高 | Event / Discovery 分开算 |
| Owner 接受至少一个 Aha 的丰富日占比 | 先建立基线 | 不应预设为每天必有 |
| Unsupported User State Claim | 接近 0 | 硬安全目标 |
| Writer 失败导致内容消失 | 0 | 工程硬门槛 |
| 测试集用户泄漏 | 0 | 数据硬门槛 |

这些数值必须带置信区间，并按以下切片报告：

- 旅行 / 普通日 / 工作 / 家庭 / 宠物；
- 丰富日 / 稀疏日；
- 手机 / 穿戴设备；
- Manual / Auto；
- 长视频 / 短视频 / 照片；
- 新用户 / 已个性化用户。

不能只报告一个总体均值，因为总体均值可能掩盖某一类用户完全不可用。

---

## 16. 如何更接近“有效”和“满意”，而不是只追一个分数

### 16.1 多目标，不做单一满意度总分

推荐至少保留五个互相制衡的目标：

```text
Trust：每句话是否可信
Representation：是否代表这一天
Structure：故事是否分得清
Delight：是否发现了值得回看的小精彩
Effort：用户是否需要大量修改
```

单一点击率或分享率可能鼓励夸张、情绪化和猎奇，不适合做唯一优化目标。

### 16.2 用户修改的边界

用户修改应影响：

- 个人偏好；
- Storyline 选择；
- Aha 价值；
- Hero 与媒体排序；
- 文风偏好；
- User Confirmed Facts。

用户修改不应直接改写：

- 原始视觉 Evidence；
- 模型当时实际看见什么；
- 未经证据支持的客观事实标签。

### 16.3 满意度不能被短期新鲜感欺骗

第一次看到自动日记可能因为新鲜感而高分。必须继续观察：

- 7 天后是否愿意回看；
- 30 天后是否仍觉得有代表性；
- 是否越来越少修改；
- 是否持续关闭某类 Aha；
- Rolling Revision 是否让用户困惑。

### 16.4 不同场景分别验收

旅行日：重点看多 Storyline 和同地点细分。

普通日：重点看不夸大、不硬凑，同时能找到微小发现。

工作日：重点看重复内容压缩和信息敏感度。

家庭日：重点看关系不臆测、互动事实和个人价值。

宠物日：重点看普通动作与真正 Event Peak 的区分。

稀疏日：重点看少量素材能否形成 1 个好记忆，而不是强制空日或凑满。
低质量日：重点看 Context 保留、画质降级和错误事实控制。

---

## 17. 三套现有真实素材的下一轮使用方式

用户已允许算法仓库只读使用三个素材包。建议每次完整测试仍然跑全链路，不省略某个阶段；但在内部审计中为每一步保留明确 Checkpoint，这与“只跑局部 Gate”不是一回事。

### 17.1 测试前

- 固定素材清单与哈希；
- 固定导入顺序，或建立可解释的真实时间顺序；
- 记录是否有真实时间；
- Owner 在未看新版本输出前写 Day Map；
- 固定代码、Prompt、模型与合同版本。

### 17.2 每套素材完整运行

必须输出：

- S02 每个 Window 的帧覆盖；
- S04 每个 Window Observation；
- S05 每条 Boundary Edge；
- S07 所有候选、拆分替代和缺失候选；
- S09 被选/未选及比较对象；
- S10 每个媒体覆盖哪个 Beat；
- S11 每个 Claim、Copy 和 Tag；
- S12 每个阻断原因；
- 完整时间、Token、成本和重试。

### 17.3 评估

对每个结果直接指出：

- 哪个 Chapter 合并错了；
- 哪两个素材不该在一起；
- 哪个 Chapter 应被拆成什么；
- 哪个重要故事被漏掉；
- 哪个媒体重复或 Hero 不合适；
- 哪句文案哪里生硬或虚构；
- 哪个 Aha 不够独立；
- 哪个 Aha 被漏掉；
- 应修改哪个阶段，而不是笼统说“效果不好”。

### 17.4 对照方式

- 保留当前 V04 Run 作为 Baseline；
- V04.1 使用完全相同输入做 Fresh Full Run；
- 不复用跨 Run 语义缓存；
- 做盲排：评审不知道哪个是 V04、哪个是 V04.1；
- 比较完整 Set，不只比较单个标题；
- 失败必须归因到最早发生错误的阶段。

### 17.5 这三套素材能证明什么

可以证明：

- 已知回归是否修复；
- 运行是否稳定；
- 评估工具是否够细；
- 旅行类 Storyline 是否比当前更合理。

不能证明：

- 泛化到大多数用户；
- 穿戴 Auto 数据表现；
- 长期满意度；
- Production 成本与稳定性；
- 训练有效性。

---

## 18. 推荐的实际执行顺序

### Step 1 — 固定本报告与 V04 Baseline

保留 Run Audit、Client Trace、Human Review、代码 Hash 和当前输出，后续不可覆盖。

### Step 2 — 对现有 V04 Run 做一次有限回溯标注

把 20 个视频补充：Content Unit、候选拆分、Missing Storyline、Aha 排序和 Writer 评价。因为 Owner 已看过结果，这批标注只能作为 Development Evidence，不能作为盲测 Gold。

### Step 3 — 实现 V04.1 止损项

优先处理：

1. Aha 排序、去重与 Copy Fallback；
2. One Story 反证、总跨度与中断限制；
3. 模型候选挑战 Focus；
4. quality 与 motif 合同缺陷；
5. 动态批次和失败隔离；
6. 细粒度 Human Review。

### Step 4 — 三套素材全部做 Full Run

每套均跑 S00–S12 Preview 全流程；不能只看 Gate2，也不能跳过 Writer。S13 仍单独声明未测。

### Step 5 — 与用户做一次合并决策会议

只集中讨论真正影响体验的事项：

- 古镇三种 Storyline 是否符合用户直觉；
- Aha 的独立价值边界；
- 普通日是否允许 0 Aha；
- 用户需要哪些编辑能力；
- Chapter 数量与拆分偏好。

工程错误、存档、指标记录和批次恢复不需要逐项请求用户确认。

### Step 6 — 设计并实现 V05 Content Unit

先用离线可视化和标注验证 Window → Content Unit，再替换当前 Asset Observation。不要一边改基础单位一边训练最终 Ranker。

### Step 7 — 运行 Phase A 数据试点

先验证 Rubric、一致性、授权和反馈时长，不训练模型。

### Step 8 — 建立组件 Baseline

对每个任务比较：规则、Embedding、不同模型 Prompt、轻量 Ranker。只有组件瓶颈明确后才训练。

### Step 9 — Phase B/C 组件训练

训练边界、候选排序、Aha、媒体偏好和 Writer 偏好；保留硬事实与导出合同。

### Step 10 — Locked Holdout 与 Beta

先通过陌生用户离线盲测，再做 14–28 天内部 Beta；最后才能讨论 Production Ready。

---

## 19. 需要产品负责人参与的少数决策

以下属于感性体验或产品定义，建议在有真实对照样例时集中确认：

1. 什么样的小发现值得成为独立 Aha，而不是 Chapter 中的一个 Beat；
2. 普通日、稀疏日是否允许 0 Aha，以及用户看到的中性表达；
3. 同一大 Episode 下，用户更偏好 2 个宽 Chapter 还是 3 个更细 Chapter；
4. 用户可执行哪些修改：删除、补入、拆分、合并、换 Hero、提升/隐藏 Aha；
5. 修改是否只影响当天，还是形成长期个性化偏好；
6. 中文以外语言的标题、正文和 Aha 展示合同。

以下不需要频繁请求产品负责人确认：

- 修复 Writer 失败删除内容；
- 批次失败隔离；
- 正确记录时间、Token、成本；
- 用户级数据拆分；
- 防止测试集泄漏；
- 保存 Run 与证据 Hash；
- Schema 和回归测试完整性。

---

## 20. 顾问最终意见

Diary One 的难点不在于“让一个大模型看完照片后写一篇日记”，而在于建立一条不会把局部错误放大的记忆生产链：

```text
证据不能丢
→ 事实不能编
→ 时间不能假装精确
→ 局部单元不能被文件边界绑死
→ Storyline 必须能被反证
→ Chapter 与 Aha 要承担不同记忆职责
→ 表达失败不能删除内容
→ 用户修改要能形成偏好，但不能篡改视觉事实
→ 训练集与测试集必须按用户隔离
→ 满意度要看长期保留和回看，而不是一次星级
```

当前 V04 最有价值的成果不是“已经解决了聚类”，而是它已经提供了足够详细的 Run Trace，让团队能够看到错误在哪一层发生。下一步不应继续扩大 Prompt、切换 Writer 模型或快速收集大量星级，而应先：

1. 用 V04.1 阻止已知错误继续污染测试；
2. 用 V05 修正内容单位和 Storyline 判定；
3. 建立 Evidence Truth 与 Owner Preference 分离的真实数据体系；
4. 在陌生用户、陌生日和盲评下证明泛化；
5. 再用组件级训练提高质量、效率和个性化。

做到这些，系统不能保证每一天都让每一个用户惊喜，但可以逐步保证：

- 重要内容不因工程格式错误而消失；
- 故事混合和漏选能被测量并持续下降；
- Aha 是有证据且有独立价值的发现；
- 文案可信、自然、可回退；
- 用户的修改真正帮助下一次选择；
- 每一次质量提升都能在未见用户的真实数据上被证明。

---

## 21. 证据索引

### 21.1 审计时代码状态

- Git HEAD：`aa9917ad2948550d4ce891d0cc3ca7b8acd1e9db`
- V04 为未提交工作树实现，不能仅凭 HEAD 复现；必须同时保存下列文件 Hash。

### 21.2 最新真实 V04 Run

- Run Audit：`var/x02_runs/776e2afb-abb1-4259-8aed-5a20e4dd5394/runs/58465e4b-743c-49af-85a3-93531dcb9b4d.run_audit.json`
- SHA-256：`083d683f005beb4158bbe9138668cac47ba6c7a27cf4cf9db60ee60bd1d36a3a`
- Client Trace：`var/x02_runs/776e2afb-abb1-4259-8aed-5a20e4dd5394/client_trace.json`
- SHA-256：`64ca7fc7020557ce05e78589d713c1cdb1c430171caf7ab040c5da635452d193`
- Human Review：`var/x02_runs/776e2afb-abb1-4259-8aed-5a20e4dd5394/human_review.json`
- SHA-256：`3c2e2ea8984f51169871e000c78cfa37f18ed0467d44f7d9d5c040abf5b99f6e`
- Bundle Manifest SHA-256：`705f534ec4b310451463b1300f8c1bfbe04741c86814e73d3fc124fc508e4d68`
- Human Review 当前状态：`DRAFT / UNREVIEWED`，reviews 数量为 0；因此本报告不能把它当成人工验收结果。

### 21.3 核心实现

- `src/diary_one_ci/x02.py`
- 审计快照 SHA-256：`7cecdc412def23a9ad7dde21b0c495dabc1fa269937789aa23c8a562d1636e9f`
- 关键区域：
  - 固定批次与数量合同：约 35–53 行；
  - Qwen JSON 调用与 Evidence 注入：约 422–566 行；
  - invalid quality 回退到 0.35：约 1921–1932 行；
  - Role `<0.35` 判定：约 2104–2117 行；
  - Boundary 与 DEFER：约 2127–2164 行；
  - Moment 只对 JOIN 合并：约 2167–2181 行；
  - Primary Focus：约 2225–2278 行；
  - Storyline 生成、校验和 One Story Gate：约 2333–2808 行；
  - Aha Candidate 与 Set Selection：约 3018–3237 行；
  - Chapter Media：约 3240–3288 行；
  - Writer Prompt 与 Validator：约 3384–3517 行；
  - Canonical Tags：约 3659–3694 行；
  - motif ASCII 归一化：约 3920–3921 行。

### 21.4 合同与测试

- V04 Schema：`contracts/x02_staged_preview_v04.schema.json`
- 最终复核时 SHA-256：`41c13a97a312318f0882bb411abce21b7c8ce5f89edb38584a250f42a548bb52`
- Storyline Contract：`src/diary_one_ci/contracts/x02_storyline_v01.json`
- SHA-256：`dddb03b4a5a35e4d7d83c0fee7dbb02dc4e8f30cabba074ebe84c5a229616e8b`
- Tests：`tests/test_x02.py`
- “一个宽泛古镇 Episode 切成三个 Storyline”的测试约在 705–734 行；它使用脚本化的理想 Observation，只证明路由逻辑，不证明真实视觉模型能产生这些标签。

### 21.5 设计资料

- `docs/END_TO_END_PIPELINE_LOGIC_TEAM_SYNC_V0_1.md`
- `docs/X02_CURRENT_WORKFLOW_EXPLAINED_AND_QUALITY_DIAGNOSIS_V0_1.md`
- `docs/GATE2_STORYLINE_SEGMENTATION_GENERALIZATION_WORKING_V0_1.md`
- `docs/FOR_CLAUDE_ALGORITHM_WORKFLOW_AND_CROSS_VALIDATION_PACK_V0_1.md`
- `docs/ALGORITHM_GLOSSARY_V1_0.md`

---

## 22. 报告边界

本次没有：

- 修改任何算法代码；
- 修改任何冻结记录；旧 Claude Review Input 仅增加了本次 V04 Run 的显式状态补充，原历史文字保留；
- 修改 Firmware / SDK / 正式 App；
- 修改三套真实素材；
- 重新运行付费模型；
- 宣称 V04、V04.1 或 V05 已通过质量验收；
- 把建议阈值写成冻结产品结论。

本报告的用途是作为下一轮 V04.1、V05 与真实数据计划的审计输入。任何实现完成、自动化测试通过、真实模型质量通过、用户满意和 Production Ready，必须继续分开陈述。
