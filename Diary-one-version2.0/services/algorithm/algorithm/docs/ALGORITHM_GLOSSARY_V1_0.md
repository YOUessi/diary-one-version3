# Diary One Algorithm Glossary V1.0

**状态：** TEAM EXPLANATION / ALIGNED THROUGH CANONICAL V1.25
**日期：** 2026-08-29
**用途：** 给产品、设计、算法和工程团队统一解释常见英文/算法概念；正式规则仍以 Canonical Checkpoint 为准

## 1. 输入与 Evidence

| 术语 | 简单解释 | 案例 |
|---|---|---|
| RawAsset | 用户真实拍到的一张照片或一段视频，是不可被 AI 改写的输入事实 | 一段 9 秒 Auto 视频 |
| Evidence | 为算法提供的、可追溯到 RawAsset 的证据 | 视频中实际上传的一帧 |
| Window | 从一段媒体或全天时间轴中划出的局部观察范围 | 60 秒 Manual 被分成 4 个连续 Window |
| Evidence Frame | Window 中供视觉理解的代表画面 | Auto 在 1.5/4.5/7.5 秒抽的三帧 |
| 1-or-3 | Phone 固定抽三帧；足够相似且信号完整时 Cloud 只收一帧，否则收三帧 | 三帧都是同一静止桌面→上传一帧 |
| no-refetch | Cloud 收到一帧后若仍无法理解，直接放弃该 Auto 候选，不再要求补两帧 | 错过一个模糊片段，不增加工程交互 |
| Provenance | “这个结论从哪里来”的完整来源链 | Claim→Observation→Frame→RawAsset |
| Fingerprint | 对 exact 输入和策略计算的稳定摘要，用来判断能否安全复用 | 同一 Evidence+模型版本命中 cache |
| Embedding | 把内容语义压成一串数字，方便比较“像不像”或语义检索 | 石板路与古建筑画面可能在向量空间接近 |

Embedding 不是事实。它可以提示“像古镇”，不能单独证明地点就是周庄，也不能证明用户喜欢古镇。

## 2. Observation 与 Moment

| 术语 | 简单解释 | 案例 |
|---|---|---|
| Observation Lite | 只描述当前 Window 能看到的少量事实卡 | “室外、石板路、传统建筑” |
| Window-local | 只用当前 Window 的 Evidence，不借邻居补写事实 | 当前帧没看到猫，就不能因下一帧有猫而写当前也有 |
| Timeline Edge | 两个相邻 Window 之间的变化/连续提示 | 室外古街→室内奶茶店变化明显 |
| Moment | 时间连续、语义相对纯净的内部生活片段 | 09:00–09:46 的古镇步行片段 |
| Boundary Evidence | 支持“这里应该切开”的证据 | 场景从古建筑街道变成现代室内 |
| Continuity Evidence | 支持“这里仍在继续”的证据 | 人物、路线和活动在相邻窗口保持 |
| 双向证据账本 | 同时记录支持合并和支持切开的证据，而不是只给一个相似度 | 奶茶店前后既有古镇 continuity，也有中间真实 break |
| MERGE | 证据支持相邻内容属于同一 Moment | 连续沿河步行 |
| SPLIT | 证据支持建立边界 | 从街道进入长时间会议 |
| DEFER | 现在证据不够，暂时等待少量后续 Window | 门口过渡画面，下一帧才看清进入店内 |
| UNRESOLVED | 有界证据已经用尽，仍无法可靠判断 | 单独成为 Transition Moment，不硬塞左右 |
| Pending Window | 尚在 DEFER、等待后续证据的一个 Window | 模糊门口画面 |
| Pending Block | 连续几个一起等待解决的 Pending Windows | 门口→推门→模糊室内三段过渡 |
| Context Signature | Moment 当前核心语境的结构化摘要，可有多个视觉原型 | 同一古镇同时包含石板路、建筑立面、河岸 |
| Transition Moment | 无法安全归左或归右的保守独立内部片段 | 短暂、模糊的进店过渡 |

## 3. Candidate、Selection 与 Revision

| 术语 | 简单解释 | 案例 |
|---|---|---|
| KEEP | 有资格成为 Memory 内容的 Observation | 清晰的古镇入口 |
| CONTEXT_ONLY | 只帮助解释边界/环境，不占最终内容位 | 路牌或短过渡 |
| DROP_FROM_MEMORY_OUTPUT | 不进入 Memory 候选，但不删除 RawAsset | 遮挡严重的重复街景 |
| Candidate | “可能成为 Chapter/Aha”的内部假设，不是最终结果 | 古镇游览 Candidate |
| Content Unit | Candidate 中一个可区分的内容意义 | 入口、木雕、河岸 |
| ValidationTask | 只回答一个局部未知项的补证任务 | “这是不是同一只猫？” |
| VBU | S08 动作相对成本单位，不是美元 | 强模型动作比结构检查消耗更多 VBU |
| SelectionRecord | S09 用来统一比较 Candidate 的结构化卡片 | 价值、证据、冲突、稳定性等字段 |
| Conflict Graph | 记录 Candidate 间重复、冲突、嵌套、可共存关系 | 生日 Chapter 与吹蜡烛 Aha 为 same-story conflict |
| Day State | 当天最终是 Chapter Day、Highlight Day 还是 Empty Day | 只有一个强求婚 Aha→HIGHLIGHT_DAY |
| Revision | 某个时间点冻结的一版输入和结果；创建后不可原地改写 | 上午 Preview R2，晚上新增素材形成 R3 |
| Preview | 白天可修订的阶段结果 | 古镇 Chapter 先出现，晚上再被丰富 |
| Final | 对 immutable 全天快照进行的最终整理 | 21:00 开始 Final，21:03 新素材进入新 Revision |
| Lineage | 同一 Memory 在多 Revision 之间的延续/合并/替换关系 | 古镇 Chapter R2→R3 保持 stable identity |

## 4. S10 媒体

| 术语 | 简单解释 | 案例 |
|---|---|---|
| Content Beat | 一个 Memory 内值得占一个展示位置的独立内容意义 | 入口、木雕、河岸是三个 Beat |
| EvidenceAnchor | Beat 在原素材中的精确证据位置 | `manual_03` 的 5.2–7.2 秒 |
| MediaDecision | 该位置最终用 PHOTO/LIVE/VIDEO，以及有哪些备选 | Primary LIVE_2S、Fallback PHOTO |
| Hero | Chapter 的封面/入口图，必须来自正文集合 | 三张正文中最适合静态入口的一张 |
| HQ Source | 足以生成最终展示媒体的高质量源，不等于默认上传传感器 RAW | 只请求 Anchor 附近 2 秒源窗口 |
| Fallback | Primary 被证明永久失败后才能激活的预声明备选 | LIVE 解码永久失败→同 Anchor PHOTO |
| Terminal failure | 已证明不能恢复的永久失败 | 源文件永久损坏 |
| Transient failure | 暂时失败，应该 retry/HOLD | 网络超时或队列等待 |
| D1 survivor | Chapter 一个媒体永久失败后，预先验证过的合法剩余集合 | 4 项删 1 后仍为合法 3 项 |
| D2 collision | Fallback 激活后与健康媒体重复时的有界处理 | 健康 Primary 不动，失败位尝试下一备选 |
| Exact reuse | 两个 Memory 必要时引用同一 render，但身份/Claims 分离 | Chapter 和独立 Aha 共用画面，各自仍是不同 Memory |

## 5. S11 文字与索引

| 术语 | 简单解释 | 案例 |
|---|---|---|
| Fact | 上游已确认的结构化事实 | “猫碰倒纸杯” |
| Atomic Claim | 用户文字中可以独立判断真假的最小命题 | “猫碰倒了纸杯”与“纸杯在桌上”可分别验真 |
| Claim Ledger | 每条 Claim 的证据、状态和可用 surface 账本 | 同一地点 Claim 可用于 Title，但普通茶摊只可作 Story support |
| Surface | 用户文字/索引的具体用途 | Title、Story、Moment Line、Time、Tag |
| Content Plan | Writer 之前已批准“写哪些 Claims、用什么关系”的计划 | 一组 core + 最多一组 support |
| Grounded Narrative | 只使用获批 Claims、能回到 Evidence 的用户文字 | “石板路连着旧屋，晚光落在水面。” |
| Canonical Concept | 语言无关、稳定、受控的内容概念 ID | `ACTIVITY.CITY_WALK` |
| Facet | Canonical Concept 的语义维度 | Activity、Setting、Central Subject、Occasion |
| Canonical Tag Assignment | 当前 Memory 对一个 Concept 的有证据分配 | 古镇 Chapter→CITY_WALK |
| Entity Link | 精确地点/人物/宠物身份的专门索引 | 周庄、妈妈、豆包 |
| Display Label | 从 registry 派生、可选择给用户看的本地化词 | “城市漫步” |
| Light affect | 不推断用户内心、只对明确对象/动作做窄幅共识性表达 | 有动作证据时“调皮的小猫” |
| Protected user text | 用户自己写的文字，AI 不能覆盖或冒充 | 用户手动改的 Chapter Title |

## 6. S12/S13 发布

| 术语 | 简单解释 | 案例 |
|---|---|---|
| S12A | HQ 物化前的结构/语义检查 | 先确认数量、Claims、route 都合法再花 HQ 成本 |
| Materialization | 把 selected HQ source 生成 PHOTO/LIVE/VIDEO 文件 | 对 exact 2 秒窗口编码 LIVE_2S |
| Receipt | 证明一次实际 materialization 的来源、格式、checksum、成本记录 | request/route/hash/bytes/latency |
| Activation Delta | Primary→Fallback 或 D1 等运行时变化的不可变记录 | LIVE→PHOTO，列出受影响 Story/Tag |
| S12B | activation 后对最终实际投影再次检查 | 确认 Fallback 后媒体和文字仍一致 |
| Atomic publish | 用户只能看到完整通过的一版，不看到半成品 | Export/Audit 都成功后一次切换 head |
| CAS | 只有 published head 仍是预期旧值时才更新，防止并发覆盖 | R6 不覆盖已经发布的 R7 |
| User Diary Export | App 真正需要的 Chapter/Aha/媒体/文字 | 不含模型分数与成本 |
| Internal Audit Run | 团队追错、评测、成本分析需要的全链路记录 | 保留 Evidence、Claim、retry、版本 |
| Production-shaped | 接口、状态、失败和审计结构像 Production，但未连接真实基础设施 | 本仓库 V1 reference |
| Production-ready | 真实模型、媒体、存储、CAS、数据、安全、SLO 均验证并可上线 | 当前尚未达到 |

## 7. 最容易混淆的五组概念

1. **Embedding ≠ Fact：** 相似数字不能证明地点、人物或情绪。
2. **Moment ≠ Chapter：** Moment 是连续内部片段；Chapter 可以用证据把 A–B–C 中的 A/C 组织成同一主线，但不改写 Moment partition。
3. **Candidate ≠ Selected Memory：** Candidate 只是内部假设；S09 才决定全天集合。
4. **Canonical Tag ≠ Display Label ≠ Preference：** 内部概念、用户显示词、用户偏好是三种不同数据。
5. **Contract frozen ≠ Production deployed：** 规则和 reference 可以完成，真实服务、模型、媒体与用户验证仍需后续工程。
