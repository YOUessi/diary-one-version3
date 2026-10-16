# Diary One AI Algorithm：交给 Claude 的完整 Workflow 与交叉验证材料 V0.1

> 最新修正（2026-09-03）：当前本地实现先读 [codex V1.35 模型负责内容分组](codex_INTEGRATION_CHECKPOINT_V1_35_MODEL_OWNED_GROUPING.md)，以及 [V1.34 辅助说明隔离](codex_INTEGRATION_CHECKPOINT_V1_34_STORYLINE_THESIS_ISOLATION.md)。Storyline V03 撤回粗标签自动分组、标签否决/重复判断与主题多样性奖励，保留 Canonical Tag。以下主体为历史审计材料，不能把其中旧聚类规则当作当前实现。Web 尚未接入，真实质量未验收。

> 最新修正（2026-09-02）：先读 [codex V1.33 案例硬编码清理](codex_INTEGRATION_CHECKPOINT_V1_33_EXAMPLE_RULE_CLEANUP.md)。本文件主体与 V1.32 均包含历史限制，不能再将猫狗模板、场景词命中、文化专属两素材例外、逐字复制和固定标题作为当前设计要求。Writer V02 是本地修改，Web 仍绑定 V01，尚未做新一轮真实质量验收。
>
> 审阅方法：用户案例用于讨论共性问题，不构成类别白名单。区分真实运行发现、尚未验证的推测与技术接口检查；未经事先解释必要性并取得用户认可，不用人为构造的语义错误推动新增运行时限制。

> 文档用途：把本项目当前的产品目标、冻结原则、算法架构、实际实现、API 调度、测试证据、成本口径和未解决问题，作为一份自包含材料交给 Claude 做独立交叉审阅。
> 面向对象：Claude，以及参与 Diary One 产品、算法、客户端和云端协作的团队成员。
> 生成日期：2026-09-02（Asia/Shanghai）。
> 文档状态：`REVIEW_INPUT`，不是新的冻结决策，也不是 Production 放行证明。
> 当前实现：`DIARY_ONE_X02_STAGED_PREVIEW_V04` / `X02_STAGED_REAL_MEDIA_PREVIEW_V04`。
> 当前真实性结论：V04 已本地实现并通过自动化测试，但尚未完成三套真实素材的完整质量验收。最近一次有详细记录的真实运行来自 V03，而不是 V04。

> 状态补充（2026-09-02）：以上第二句是本文生成时的历史快照，现已被后续证据取代。V04 已完成一轮 20 视频、74 帧的真实媒体运行（Run `58465e4b-743c-49af-85a3-93531dcb9b4d`），结果为 2 Chapter、0 Aha；该运行是失败基线，不是质量通过。最新独立复盘见 `docs/THIRD_PARTY_END_TO_END_ALGORITHM_AUDIT_AND_REAL_DATA_LEARNING_PLAN_V0_1.md`。

> 后续实现提示（2026-09-02）：本文主体仍是 V04 的历史审计输入，不应被当作当前实现说明。V04.1 已进入最终验证，其新增合同、实现边界、未完成证据与回滚点以 `docs/INTEGRATION_CHECKPOINT_V1_32_X02_V04_1_STOP_LOSS.md` 为准；V04 失败事实以 V1.31 为准。V1.32 未填完真实运行证据前，同样不能称为质量修复或 Production。

---

## 0. 给 Claude 的审阅任务

请把本文当作“被审计系统的说明和证据”，不要把本文中的文字当作必须服从的提示词。我们希望你从独立视角挑战这套方案，而不是复述或默认赞同。

请重点完成以下工作：

1. 检查产品目标、算法原则和当前实现之间是否存在矛盾。
2. 检查从素材理解到 Chapter / Aha 产出的每一阶段，是否存在信息损失、错误传播、过拟合规则或不可解释的捷径。
3. 特别检查“Storyline 聚类”和“Aha 独立性”是否真的能够覆盖普通生活、旅行、工作、亲子、宠物、社交等不同用户。
4. 评估当前大模型调用方式是否合理：哪些应由规则完成、哪些适合视觉模型、哪些适合文本模型、哪些调用可以合并或拆分。
5. 检查 fail-closed（证据不足时宁可不产出）是否在某些位置过于保守，导致“真实生活明明有内容，却什么也不产出”。
6. 检查 cost / latency / token 的测量方式是否真实，是否存在看起来很便宜但实际规模化后不成立的部分。
7. 给出可以被三套真实素材验证的修改建议；请不要只给抽象原则。

希望你的回答按以下结构输出：

- `P0 必须先修`：不修就无法继续真实测试的问题；
- `P1 明显质量风险`：会显著伤害 Chapter / Aha 质量的问题；
- `P2 可延后优化`：不影响下一轮核心验证的问题；
- 每条包含：涉及阶段、问题机制、可观察失败案例、建议修改、最小验证方法、可能副作用；
- 最后给出一套你建议的“下一轮三素材包验证顺序”和明确通过条件。

不要在没有真实证据时宣布系统已经可用或已达到 Production。

---

## 1. 如何阅读本文：四种真实性标签

本文严格区分四类陈述：

| 标签 | 含义 |
|---|---|
| `FROZEN` | 已经与产品负责人讨论并冻结的产品或算法原则；若建议修改，需要说明收益、代价和回归风险 |
| `IMPLEMENTED` | 当前 V04 代码里已经存在，并有自动化测试覆盖 |
| `REAL_EVIDENCE` | 已经通过真实素材和真实模型运行得到的证据 |
| `OPEN / GAP` | 尚未实现、尚未真实验证，或当前实现与冻结目标仍有差距 |

必须避免以下错误等价：

- 文档写过 ≠ 代码已实现；
- 代码已实现 ≠ 真实内容质量已修复；
- 自动化测试通过 ≠ 真实模型输出稳定；
- 单个用户素材通过 ≠ 对不同用户具有泛化能力；
- Preview 可运行 ≠ Production 可发布；
- 估算成本很低 ≠ 月度真实 cohort 成本达标。

---

## 2. 产品目标与参考素材规模

### 2.1 最终产品目标（`FROZEN`）

系统不是要把一天的所有素材做成“完整纪录片”，而是从大量第一人称日常素材中形成一份可信、精炼、值得回看的 Daily Memory：

- 内容丰富的一天：优先形成 `3～4 个 Chapter`；
- 第 5 个 Chapter 仅作为严格例外，不是日常目标；
- 每个 Chapter 通常包含 `3～5 个精选素材`；
- 每天最多 `3 个 Aha Moment`；
- Aha 追求“这一瞬间本身值得记住”，不是为了填满数量；
- 素材较少时也应积极寻找生活中的发现、变化、互动、反应或小惊喜，但不能为了有 Aha 而编造意义；
- Chapter 主要表达一段持续经历；Aha 主要表达一个局部高点或独立记忆点。

### 2.2 一天的高强度参考输入（`FROZEN`）

假设用户每天佩戴约 5 小时：

- Auto Video：每 2 分钟自动拍摄 9 秒，共约 `150 段`；
- Manual Photo：`20 张`；
- Manual Video：
  - 10 段 × 15 秒；
  - 3 段 × 1 分钟；
  - 3 段 × 2 分钟；
- 总计约 `186 个 RawAsset`。

这里的 186 只是容量和成本设计参考，不是每次测试必须凑齐的配额。

### 2.3 一天可能产生的输出状态（`FROZEN`）

| 状态 | 定义 |
|---|---|
| `CHAPTER_DAY` | 1～5 个 Chapter，并可有 0～3 个 Aha |
| `HIGHLIGHT_DAY` | 没有足够连续经历形成 Chapter，但有且仅有 1 个强 Aha |
| `EMPTY_DAY` | 证据确实不足，既无合格 Chapter 也无合格 Aha |
| `PIPELINE_BLOCKED` | 工程、模型、合同或 Writer 失败导致流程无法给出可信结果；不能伪装成 `EMPTY_DAY` |

---

## 3. 核心原则

### 3.1 可信性优先（`FROZEN`）

错误地把不同经历合在一起、编造情绪或把普通动作夸成惊喜，比少选一个 Chapter 更严重。总体损失不对称为：

`虚假记忆 / 错误合并 > 漏掉部分记忆 / 轻微过度切分`

但这不意味着每一层都应无限保守。当前最重要的产品问题之一，恰恰是多层保守规则叠加后可能让内容被连续淘汰，最终“什么都没有”。

### 3.2 分层职责（`FROZEN`）

- 感知层回答“画面中能看见什么”；
- 时序结构层回答“哪些片段属于同一段经历”；
- 编辑选择层回答“哪些经历和瞬间最值得呈现”；
- Writer 只负责把已经被证明的事实写得自然，不能创造新事实；
- Validator 只验证，不能悄悄重写不合格内容；
- 评估数据先收集，不能自动改变阈值或学习用户偏好。

### 3.3 双向证据（`FROZEN`）

相邻内容是否属于同一段故事，不能只问“它们像不像”，必须同时记录：

- `Continuity Evidence`：支持它们继续属于同一经历的证据；
- `Boundary Evidence`：支持这里发生切换、转场或新经历的证据。

然后输出四种状态：

- `JOIN`：支持连接；
- `SPLIT`：支持切开；
- `DEFER`：现有证据不足，暂不归左也不归右；
- `DROP` 是后续素材角色，不是边界决定。

无法归左或归右的过渡内容，不强行合并；可以单独进入 Aha 候选、上下文候选，最终仍无价值时再删除。

### 3.4 时间接近不是同一故事，视觉相似也不是同一故事（`FROZEN`）

例如：古镇散步 → 进入现代奶茶店 → 回到古镇散步。

- 奶茶店可能是一个独立 Moment 或 Aha；
- 前后的古镇内容不应因为中间插入奶茶店就永远断成两个无关故事；
- 但也不能只因为都在“古镇”就把集市摊贩、牌楼木雕、青石板自然散步全部混成一个 Chapter；
- 需要更高层的 Storyline：路线漫步、文化建筑发现、当地市集生活可以成为不同叙事线。

### 3.5 Manual 素材没有“免去重特权”（`FROZEN`）

Manual 素材即使是用户主动拍摄，也可以因相似、低质量或不适合当前故事而从 Chapter / Aha 候选中抑制。它仍保留在：

- RawAsset 事实账本；
- App 独立 Manual 素材窗口。

### 3.6 结果修订而非无上限累加（`FROZEN`）

用户每天可能多次打开 App 和 Sync。中间预览可以产生 Chapter / Aha，但随着新素材进入，应修订、替换、合并既有结果，而不是每次都只追加。全天数量目标仍然以最终 Daily Memory 为准。

### 3.7 用户上传体验（`FROZEN`）

- 用户只进行一次明确的 `Sync`；
- 后续符合条件的云端上传应为后台、批量、无感；
- 不能为算法补证据再次要求用户操作；
- Auto Video 若只上传 1 帧仍无法判断，直接放弃该候选，不从云端再请求另外两帧。

### 3.8 Production 形态（`FROZEN`）

目标是 `Modular Monolith + Async Worker`，而不是一开始拆成大量微服务，也不是把整天素材交给一个“超级 Agent”自由发挥。模型能力通过统一 Gateway 管理，业务规则和供应商 SDK 解耦。

### 3.9 触发、Revision 与队列（`FROZEN`）

- 累积约 1.5 小时有效采集覆盖后，系统可以开始准备抽帧和后台上传；
- 约 2 小时有效覆盖是默认可尝试产生一次 Preview 的基线；
- 重要 Manual 输入、明显语义变化或用户当天 finalization 可以更早触发；
- 固定 12:00 / 17:00 / 20:00 不是核心算法门槛；素材覆盖和变化更重要；
- 同一天的新素材创建新 Revision，不能静默原地改写已经进入 Finalizing 的输入快照；
- 生命周期目标：`OPEN → FINALIZING → READY → PUBLISHED → CLOSED`；
- Stage 状态：`PENDING / RUNNING / SUCCEEDED / FAILED_RETRYABLE / FAILED_TERMINAL / STALE / SKIPPED`；
- 异步队列按 at-least-once 设计，因此任务必须幂等；
- Provider failure 与 semantic inability 必须分开归因；
- 昂贵的素材感知未来可以按精确 fingerprint 增量缓存，但同一天的结构与集合选择可以在新 Revision 上重新计算。

---

## 4. 关键概念释义

| 名称 | 通俗含义 | 在本系统中的作用 |
|---|---|---|
| `RawAsset` | 一张原始照片或一段原始视频 | 最原始的事实单位，不能因候选淘汰而从事实账本消失 |
| `Frame` | 从视频某一时间点抽出的一张图 | 视觉模型实际查看的证据 |
| `Window` | 一段视频内部的局部时间窗口 | 避免用单帧代表较长视频；每个 Window 通常取前后两个位置 |
| `Evidence Bundle` | 发给算法服务的标准化证据包 | 包含素材顺序、类型、时长和归一化帧，不含原视频 |
| `Observation` | 对单个素材的、受证据约束的结构化观察 | 例如场景、活动、主体、事件类型和事实引用 |
| `Embedding` | 把画面或文本压缩成可比较的数字向量 | 可帮助发现语义相似，但不能单独决定故事归属；当前 V04 主路径没有把通用 embedding 作为最终 Storyline 决策器 |
| `Edge` | 两个相邻 Observation 之间的关系 | 保存 Continuity / Boundary Evidence 和 JOIN / SPLIT / DEFER |
| `Moment` | 时间线上连续、局部一致的一小段经历 | 比 Chapter 小，是结构层的中间单位 |
| `Pending Window` | 暂时无法归入左右 Moment 的 Window | 等待有限的后续证据，不无限悬置 |
| `Pending Block` | 连续多个 Pending Window 形成的过渡块 | 可独立进入 Aha / Context / Drop 判断 |
| `Episode` | 粗粒度经历类别 | 如古镇游览、集市、咖啡停留；只能作为证据之一，不能直接等同于 Chapter |
| `Storyline` | 跨多个局部素材成立的一条明确经历线 | 例如“古镇文化建筑发现”或“当地市集生活”，是 V04 Chapter 候选的核心 |
| `Beat` | Storyline 中某个素材承担的叙事作用 | 如进入、推进、发现、互动、高潮、结果、离开 |
| `Candidate` | 尚未被最终选中的 Chapter 或 Aha 方案 | 需要经过合同、冲突、质量与集合选择 |
| `Canonical Tag` | 受控词表中的标准标签 | 用于未来检索、统计和数据价值，不是装饰性自由文案 |
| `Grounding` | 输出说法能否追溯到具体视觉事实 | 防止模型把常识或猜测写成用户真实经历 |
| `Fail-closed` | 无法验证时不公开输出 | 防止虚假记忆；但失败必须可观测，不能伪装为空白的一天 |

---

## 5. 两套必须分开的架构视图

### 5.1 目标中的 Production-shaped Pipeline（`FROZEN`）

```text
S00 RawAsset Ingest
  ↓
S01 Media Normalize / Decode
  ↓
S02 Window + Frame Evidence
  ↓
S03 Cheap Signals / Adjacent Edges
  ↓
S04 Observation Lite
  ↓
S05 Moment Segmentation
  ↓
S06 Material Role
  ↓
S07 Chapter + Aha Candidates
  ↓
S08 Targeted Enrichment / Validation
  ↓
S09 Daily Set Selection
  ↓
S10 Media Selection
  ↓
S11 Grounded Writing + Canonical Tags
  ↓
S12 Read-only Validation
  ↓
S13 HQ Materialization / Export / Audit
```

### 5.2 当前 Web + X02 V04 Research Preview（`IMPLEMENTED`）

```text
浏览器读取用户选择的一批照片/视频
  ↓ 本地解码、抽帧、裁切、压缩
Evidence Bundle（原媒体不上传）
  ↓ multipart POST
X02 V04 Gateway
  ↓
S04：分批视觉理解
  ↓
简化的 Edge + Moment
  ↓
S06：KEEP / CONTEXT_ONLY / DROP
  ↓
V04 Storyline 候选：规则候选 + 1 次模型提案
  ↓
当前 S09：完整候选集合组合选择
  ↓
当前 Aha 候选与选择
  ↓
S10 选择展示帧
  ↓
S11 Writer：1 次，必要时仅对不合格项重试 1 次
  ↓
合同验证 + Web 展示 + 运行审计
```

当前 Preview 不是目标 Pipeline 的全部实现。尤其 S08 和 S13 仍不完整；S05 的双向证据与 bounded defer 也只是简化实现。

---

## 6. S00～S13 完整流程对照

### S00 — RawAsset Ingest

**目标：** 建立一天的素材事实账本。

**输入：** Auto / Manual 原始照片和视频，以及素材类型、采集时间、时长、来源、可选 GPS 等元数据。

**主要规则（`FROZEN`）：**

- 每个 RawAsset 有稳定 ID；
- Manual 被候选层抑制不等于从事实账本删除；
- 一次 Sync 后的后台处理对用户无感；
- 滚动预览结果可被后续素材修订。

**当前 Web（`IMPLEMENTED`）：**

- 每次选择的一批素材都当作一个独立测试日；
- 没有 GPS 和可靠拍摄时间；
- 浏览器选择顺序被当作合成时间顺序；
- 每次必须是 `FRESH_FULL_RUN`，不复用跨运行语义缓存；
- 最多 240 个素材，请求体最多 512 MiB。

**风险（`OPEN / GAP`）：**

- 手机相册顺序不等于真实采集时间；
- 测试素材多为用户主动手机拍摄，与未来第一人称自动采集分布不同；
- 第三人称、精选照片、断续录像会让测试结果偏向“人工已筛选素材”。

### S01 — Media Normalize / Decode

**目标：** 把不同编码、分辨率和方向的媒体转换成可稳定处理的标准输入。

**当前 Web（`IMPLEMENTED`）：**

- 原始媒体在浏览器本地解码；
- 生成 768×1024、3:4 中心裁切的标准 Evidence Frame；
- 原始照片和视频不会直接进入模型请求；
- 损坏、不可解码、超时的素材记录明确失败，不让整日任务永久卡住。

**风险（`OPEN / GAP`）：**

- 中心裁切可能剪掉主体；
- 测试浏览器串行处理会造成较长等待；
- 当前 Evidence 适合研究预览，不是未来 App 最终媒体管线合同。

### S02 — Window / Frame Evidence

**目标：** 用尽可能少的帧代表视频中的重要变化。

#### 未来 Auto Video 合同（`FROZEN`）

9 秒 Auto Video 在手机侧固定抽取：

- 1.5 秒；
- 4.5 秒；
- 7.5 秒。

手机侧形成固定三帧证据，但云端采用保守 `1-or-3` 上传：

- 三帧彼此高度相似且无不确定性：上传 1 帧；
- 否则上传 3 帧；
- 只上传 1 帧后云端仍无法确认：直接排除，不回拉剩余两帧。

#### 未来 Manual 合同（`FROZEN`）

| 素材 | Window | Frame |
|---|---:|---:|
| Photo | 1 | 1 |
| 15 秒视频 | 2 | 4 |
| 60 秒视频 | 4 | 8 |
| 120 秒视频 | 6 | 12 |

每个 Window 约在局部的 1/3 与 2/3 位置取证据。

#### 当前手机相册测试合同（`IMPLEMENTED`）

| 实际素材 | Window | Frame |
|---|---:|---:|
| Photo | 1 | 1 |
| Video ≤10 秒 | 1 | 3 |
| Video >10～30 秒 | 2 | 4 |
| Video >30～90 秒 | 4 | 8 |
| Video >90 秒 | 6 | 12 |

**风险（`OPEN / GAP`）：**

- 这是测试适配，不应误写成正式 App 的最终抽帧合同；
- 没有通过真实 wearable 素材验证 1-or-3 的准确率和节省比例；
- 固定采样可能错过非常短的事件高点。

### S03 — Cheap Signals / Edge Preparation

**目标（`FROZEN`）：** 在不调用生成式模型的情况下提取便宜信号，并分别形成 Window 内部信号和相邻 Window 边界信号。

- S03A：Window 自身质量、模糊、重复、视觉变化等；
- S03B：相邻内容间的语义、场景、活动、时间和变化证据；
- 不在此阶段生成故事或情绪文案。

**当前 V04（`IMPLEMENTED，但简化`）：**

- 主要依赖 S04 的结构化 Observation 后计算相邻边界；
- 同 Episode、同非 UNKNOWN Setting、共享 motif 可构成 continuity；
- Episode 改变、Setting 改变或任一素材被 DROP 可构成 boundary；
- 任一侧 UNKNOWN / OTHER 时倾向 `DEFER`；
- continuity 存在且无 boundary 才 `JOIN`，否则通常 `SPLIT`。

**重要差距（`OPEN / GAP`）：**

- 这还不是完整的多原型语义边界系统；
- 没有充分实现视觉 / 活动 /场景 /主体 /语义主题的独立证据账本；
- 没有真正实现 bounded lookahead 后再处理 DEFER；
- 粗粒度 Episode 或 Setting 一旦分类错误，会向后传播。

### S04 — Observation Lite

**目标（`FROZEN`）：** 对每个素材独立回答“能从这些帧确定看见什么”，并给后续结构层提供可追溯事实。

**当前 V04（`IMPLEMENTED`）：**

- 每批最多 6 个素材；
- 一个视觉模型调用必须为批次内每个素材输出且只输出一个 Observation；
- 事实必须引用该素材实际提交的 Frame ID；
- 单条事实最多 200 字符；
- 支持等级：`STRONG / MODERATE / WEAK`；
- 不允许从画面臆测精确地点、身份、关系、情绪、偏好、味道、意图和因果；
- 个别非法事实可以被丢弃；若全部事实无效，则该 Observation 为 insufficient；
- 非关键字段非法时保守降级为 `UNKNOWN` 或 `NONE`，而不是让有效事实一起消失；
- 缺失、重复、供应商坏 JSON 等结构问题记为 `FAILED`，不能伪装成弱证据。

#### 当前受控语义词表（`IMPLEMENTED`）

**Setting：**

`HISTORIC_STREET`、`COMMERCIAL_MARKET`、`NATURE_TRAIL`、`CAFE_TEA_SHOP`、`HOME`、`WORKPLACE`、`INDOOR_PUBLIC`、`URBAN_STREET`、`TRANSIT`、`OTHER`、`UNKNOWN`

**Activity：**

`WALKING`、`BROWSING`、`EATING_DRINKING`、`CRAFT`、`GATHERING`、`WORKING`、`OBSERVING`、`TRANSIT`、`OTHER`、`UNKNOWN`

**Episode：**

`HISTORIC_TOWN_WALK`、`MARKET_VISIT`、`NATURE_WALK`、`CAFE_STOP`、`HOME_LIFE`、`WORK`、`MEAL`、`CRAFT_SESSION`、`BIRTHDAY_GATHERING`、`SOCIAL_GATHERING`、`URBAN_WALK`、`TRANSIT`、`OTHER`、`UNKNOWN`

**Central Subject：**

`HISTORIC_ARCHITECTURE`、`CAT`、`DOG`、`FOOD_DESSERT`、`CRAFT_OBJECT`、`PEOPLE`、`LANDSCAPE`、`STREET_SCENE`、`OTHER`、`UNKNOWN`

**Event Kind：**

`NONE`、`ACTION`、`INTERACTION`、`TRANSITION`、`DISCOVERY`、`REACTION`、`RESULT`、`CEREMONY`、`PLAYFUL_ANIMAL`、`FOOD_MOMENT`、`OTHER`

**Salience：** `NONE / LOW / MEDIUM / HIGH`

#### 当前素材角色初判（`IMPLEMENTED`）

- Observation 为 FAILED / INSUFFICIENT → `DROP_FROM_MEMORY_OUTPUT`；
- 质量分 < 0.35 或仅有 WEAK 事实 → `CONTEXT_ONLY`；
- 其余 → `KEEP`。

这里的 `quality_score` 是当前 Research Preview 的实验性工程信号。冻结的 Production Observation 原则是不使用一个模糊的“总置信分”替代逐事实 support、来源和不确定性。

**风险（`OPEN / GAP`）：**

- 封闭词表容易在普通生活或新场景上落入 OTHER / UNKNOWN；
- 每个素材只给一个主 Episode / Setting / Activity，可能过早压扁多义性；
- 后续 Storyline 过度依赖这些单标签，会重复出现硬编码 taxonomy 的盲点；
- “高质量画面”与“对故事有用”目前仍混在部分评分中。

### S05 — Moment Segmentation

**目标（`FROZEN`）：** 使用双向证据账本，把连续 Window 切成局部 Moment；不能只靠视觉相似或粗粒度类别。

**当前 V04（`IMPLEMENTED，但简化`）：**

- 仅把连续 `JOIN` 的 Observation 合并成 Moment；
- `SPLIT` 断开；
- `DEFER` 没有完整的有限未来证据求解；
- 可以记录 continuity 和 boundary 的简化理由。

**风险（`OPEN / GAP`）：**

- 古镇石板路 → 古建筑 → 石板路可能因为主标签变化被错误切分；
- 古镇 → 奶茶店 → 古镇无法在 Moment 层完整表达“插曲后恢复同一长期经历”；
- 因此 V04 引入更高层 Storyline，但底层错误仍会影响候选证据。

### S06 — Material Role

每个素材在记忆生产中只能有一种角色（`FROZEN`）：

| 角色 | 含义 |
|---|---|
| `KEEP` | 可以作为 Chapter / Aha 的可见素材 |
| `CONTEXT_ONLY` | 可帮助理解前后文，但不作为最终精选素材 |
| `DROP_FROM_MEMORY_OUTPUT` | 不进入 Chapter / Aha；仍可留在事实和 Manual 账本 |

当前 V04 已实现该三分法，但角色规则仍需要真实样本校准。

### S07 — Candidate Generation

#### 目标 Chapter 候选合同（`FROZEN`）

- 正常 Chapter 至少 3 个不同 KEEP RawAsset；
- 至少 3 个非冗余内容单元；
- 候选最多 12 个成员；
- 支持四种时间形态：
  - `SINGLE`；
  - `ADJACENT_GROUP`；
  - `RESUMED_EPISODE`；
  - `LOCAL_EPISODE_GROUP`。

#### 目标 Aha 候选合同（`FROZEN`）

- 局部高点 + 独立记忆价值；
- 一个明确 origin；
- 一个 KEEP peak；
- 最多 3 个连续 Window，且不超过约 3 分钟；
- 与所在 Chapter 时间重叠并不自动禁止；关键是它是否讲述不同的、可以单独成立的记忆点。

例子：

- 生日聚会里的吹蜡烛通常只是 Chapter 高潮，不应重复成为独立 Aha；
- 古镇游览中的一次有趣甜品发现，可以成为独立 Aha，因为它与“古镇漫步”是不同的局部记忆；
- 小猫跳上桌碰倒纸杯，可以成为“调皮的小插曲”，但“调皮”只能作为普遍、轻量的共识性语气，不能扩写成用户的真实感受。

---

## 7. V04 Storyline：当前 Chapter 聚类的核心实现

### 7.1 为什么引入 Storyline

V03 真实测试表明，按粗粒度 Episode 聚合再追求覆盖率，会把以下内容混在一起：

- 古镇牌楼和木雕；
- 青石板路与自然漫步；
- 当地集市和摊贩；
- 普通街景或过渡镜头。

它们可能发生在同一次古镇旅行，但不等于同一个 Chapter。V04 尝试从“同一大场景”升级到“同一叙事主线”。

### 7.2 Storyline 合同（`IMPLEMENTED`）

**Basis：**

- `EVENT_PROGRESSION`
- `ACTIVITY_THREAD`
- `DISCOVERY_SERIES`
- `SOCIAL_INTERACTION`

**Primary Focus：**

- `LOCAL_COMMERCE`
- `SOCIAL_EVENT`
- `FOOD_EXPERIENCE`
- `WORK_ACTIVITY`
- `CRAFT_ACTIVITY`
- `PET_INTERACTION`
- `CULTURE_ARCHITECTURE`
- `ROUTE_SCENERY`

**Beat Role：**

- `ENTRY`
- `PROGRESSION`
- `DISCOVERY`
- `INTERACTION`
- `CONTRAST`
- `PEAK`
- `RESULT`
- `EXIT`
- `ATMOSPHERE_SUPPORT`

**边界：**

- 一个 Storyline 最多 12 个成员；
- 相邻成员的素材顺序差最多为 8；
- 模型最多可提出 12 个 Storyline 提案。

### 7.3 Primary Focus 规则（`IMPLEMENTED`）

当前 V04 先通过确定性规则给每个 KEEP Observation 分配一个主 Focus：

- Transit → 不形成主 Focus；
- Market Episode / Market Setting / commerce motif → `LOCAL_COMMERCE`；
- Birthday / Social Gathering → `SOCIAL_EVENT`；
- Work → `WORK_ACTIVITY`；
- Craft → `CRAFT_ACTIVITY`；
- Meal / Cafe / Eating → `FOOD_EXPERIENCE`；
- Cat / Dog + 高显著互动或相关事件 → `PET_INTERACTION`；
- Historic Architecture + observing / discovery / culture motif → `CULTURE_ARCHITECTURE`；
- Walking + 路线场景，或 Landscape / Street / Historic subject → `ROUTE_SCENERY`；
- 其他不能确认的内容 → 无主 Focus。

### 7.4 候选来源（`IMPLEMENTED`）

V04 同时使用两类候选：

1. **确定性候选**
   - 按相同 Primary Focus 聚合 KEEP Observation；
   - 成员间 source-order gap 不超过 8；
   - 最少 3 个、最多 12 个成员。
2. **模型提案候选**
   - 一次纯结构化 / 文本模型调用读取已经验证的 Observations 和 Moments；
   - 模型可以提出跨局部 Moment 的 Storyline；
   - 模型不再读取原图。

### 7.5 模型候选的硬校验（`IMPLEMENTED`）

模型提案只有全部满足以下条件才会进入候选池：

- 3～12 个成员；
- 成员全部为 KEEP；
- 每个成员的 Primary Focus 必须与确定性规则一致；
- 每个成员的事实引用有效；
- 每个成员恰好一个 Beat；
- 相邻成员 source-order gap ≤8；
- Storyline thesis 能追溯到事实；
- basis 与 Focus 合同匹配；
- 与已有候选完全重复时拒绝。

V04 已去掉“所有成员必须拥有完全相同 Episode”的硬门槛，因此文化建筑线可以跨相近 Episode 组合。

模型输出的自由文本 Beat contribution 不直接公开。系统会将其替换为受控表达：

`Beat Role / Setting / Activity / Event Kind`

### 7.6 One Story Gate（`IMPLEMENTED`）

每个候选输出：

- Storyline identity；
- 时间段和中断信息；
- 涉及的 Episode；
- 每个素材的 Beat；
- continuity evidence；
- boundary evidence；
- 一个故事是否成立的判定。

### 7.7 当前选择目标（`IMPLEMENTED`）

系统对完整合格候选池做组合搜索，最多选择 4 个 Chapter。候选冲突包括：

- 共享同一 RawAsset；
- 同 Focus 且间隔很近，被视作同一记忆的冗余候选。

当前优化元组按优先级为：

1. 选中候选数量；
2. Focus 多样性；
3. 候选平均质量总和；
4. Beat Role 多样性；
5. 覆盖素材数；
6. 时间顺序稳定 tie-break。

### 7.8 Storyline 当前最重要的风险（`OPEN / GAP`）

这是希望 Claude 重点挑战的部分：

1. **单一 Primary Focus 过早压缩语义。** 一张“古建筑里的摊贩”可能同时支持文化、商业和路线，但当前必须先选一个。
2. **固定八类 Focus 可能再次形成 taxonomy 硬编码。** 育儿、运动、学习、演出、医院、购物、家庭烹饪等普通生活可能无法形成 Chapter。
3. **Focus 与 Basis 映射过于固定。** 同一文化线既可能是发现系列，也可能是活动推进。
4. **没有完整的内部 Partition Challenge。** 系统没有系统性尝试把一个候选拆成两个，并比较“拆开是否更纯”。
5. **没有完整的竞争解释账本。** 被拒绝的分组方案没有成为可审计的 Alternative Resolution。
6. **没有实现内容单元粒度。** 当前主要在 Observation / Moment 层工作，尚未充分识别一个视频中多个不同内容单元。
7. **gap 是素材顺序，不是真实时间。** 当前 Web 无时间戳，因此 `8` 只是代理变量。
8. **候选数量优先。** 组合目标首先最大化 Chapter 数量，可能把“尽量 3～4 个”错误实现为“只要过粗门槛就尽量多选”。
9. **广义 Gate2 设计没有完全落地。** 原设计还包括 thesis signature、occasion envelope、split alternatives、contradiction、bounded resume evidence；V04 只实现了其中一部分。
10. **没有真实 V04 质量证据。** 单元测试能证明合同执行，但不能证明古镇案例真的切分正确。

---

## 8. S08 — Targeted Enrichment / Validation

### 8.1 目标（`FROZEN`）

只有当某个候选的一个关键事实不确定、且补充一次证据可能改变选择结果时，才允许发起一次受限问题。不能让模型重新自由理解整天。

原则：

- 一次只问一个明确事实问题；
- 选择最低充分模态；
- 有严格预算、缓存、重试、失败和 stale 管理；
- 证据用尽仍不明确时，不强行成立候选。

只有 S07 disposition 为 `PROVISIONAL_VALIDATION_REQUIRED`、问题确实可能改变 eligibility 或解决 local alternative 的 Candidate 才能进入 S08。已经 ELIGIBLE、REJECTED 或 SUPPRESSED_DUPLICATE 的内容不能为了“更保险”消耗验证预算。

#### 四类允许问题

| Question Type | 只允许确认什么 | 例子 |
|---|---|---|
| `LOCAL_PEAK_CONFIRMATION` | 一个 origin Moment、一个 KEEP peak、最多 3 个连续 Window / 3 分钟内的局部变化 | 火焰是否从点燃变成熄灭 |
| `EPISODE_RELATION_CONFIRMATION` | Candidate 成员和既有边界账本中的一个局部关系 | 古镇 A、奶茶 B、古镇 C 中 A/C 是否是同一 outing 的恢复 |
| `MEDIA_DIVERSITY_CONFIRMATION` | Long Manual 指定 Window 是否有真实时间 / 语义差异 | 表演视频里准备、演奏、鼓掌是否是不同内容位置 |
| `ALTERNATIVE_RESOLUTION` | 已声明 local alternative group 中的一对 dominance / distinctness | A dominates、B dominates、both distinct 或 unresolved |

#### 最低充分能力路径

```text
A0 EXACT_VALIDATION_CACHE
  ↓ 未命中
A1 STRUCTURED_EVIDENCE_CHECK
  ↓ 确实需要模型时，只选择一个最低充分分支
A2-V TARGETED_LIGHTWEIGHT_VISION（≤3 张已有 Frame）
或 A2-T EXISTING_TEMPORAL_PROXY（≤2 段、总计 ≤6 秒已有 proxy）
或 A2-A GATED_AUDIO_OR_ASR（≤1 段、≤15 秒、政策已允许）
  ↓ 只有语义能力不足且结果会改变 eligibility
A3 BOUNDED_STRONG_MODEL（同样或更小 payload）
  ↓
STOP
```

- A2-V / A2-T / A2-A 不是依次全部运行，而是选择一个最低充分分支；
- 每个 Task 最多两个付费 capability step；
- Provider failure / invalid output 只能同等级 retry / fallback，不能借机升级 Strong Model；
- 源证据缺失、遮挡、政策不允许或矛盾不可解决时必须 STOP；
- S08 finding 独立保存，不能改写 S04 facts、S05 Moment、S06 role 或 S07 disposition。

#### 冻结的 VBU 预算边界

`VBU` 是相对预算单位，不等于固定美元或 token：

| Action | 最低 VBU |
|---|---:|
| A0 / A1 | 0 |
| A2-V / A2-A | 1 |
| A2-T | 2 |
| A3 | 4 |

主要上限：

- 每 Candidate 必要 ValidationTask ≤2；
- 每 Task paid capability step ≤2；
- 每 capability step provider attempt ≤2；
- 每 Task VBU ≤6；
- 每 Candidate VBU ≤8；
- 一天所有 Preview Revision 合计 VBU ≤4；
- 一天所有 S08 Revision 合计 VBU ≤16；
- 每天进入 A3 的 Task ≤2；
- Preview frontier ≤3 Candidate，Final frontier ≤8 Candidate。

真实 dispatch 还必须记录供应商原币、换算版本、预计 / 实际美元以及 Validation、ASR、Strong escalation、Retry waste 分账。预算不足表示 `NOT_RUN_BUDGET`，不能被写成内容验证失败。

### 8.2 当前状态（`OPEN / GAP`）

X02 V04 Research Preview 没有完整执行冻结版 S08。当前主要依赖 S04 已有 Evidence 和候选硬校验。任何“V04 已经实现完整 S08”的说法都是错误的。

---

## 9. S09 — Daily Set Selection

### 9.1 目标（`FROZEN`）

从全部合格候选中选择一组互相不冲突、覆盖一天主要经历、同时不重复的 Chapter / Aha。它不是简单 Top-K，也不是强行凑 3～4 Chapter 和 2～3 Aha。

应考虑：

- 质量；
- 故事纯度；
- 日内覆盖；
- 相互冗余；
- 素材冲突；
- 主题多样性；
- 对用户的记忆价值；
- 数量只是软目标。

冻结版 S09 不是把这些因素压成一个随意加权总分，而是按以下八层 ordered / lexicographic objective 依次比较：

1. **Legality 与 Trust：** 只比较合同、资格和共选约束均合法的集合；
2. **Material Marginal Memory Contribution：** 移除任何成员都会真实损失一个独立经历、进展、结果、转折或高光；
3. **Meaningful Episode Coverage：** 覆盖值得成为记忆的独立强经历，不能用素材数量或时长冒充；
4. **Trusted Independent Memory Value：** 证据可靠、过程完整、结果清楚、推断风险低；
5. **Set-level Redundancy 与 Inference Risk：** 同时控制 Chapter–Chapter、Chapter–Aha、Aha–Aha 重复；
6. **Quality-qualified Count Preference：** 只有前五层已满足后，丰富日才偏好 3～4 Chapter、2～3 Aha；
7. **Revision Stability：** 近似质量方案中偏好用户可见身份更稳定者；
8. **Parsimony 与 Determinism：** 仍等价时选择更精简方案，再用固定键稳定决胜。

冻结版搜索还要求：

- Chapter 与 Aha 是一个联合计划；即使遍历时先建 Chapter skeleton，也必须让 Aha compatibility 和整体价值反过来影响最终 Chapter 方案；
- 每个成员执行 removal test，删掉后没有实质记忆损失的成员不能留在集合中；
- 同地点、同风格、同活动、高 embedding、时间接近都不能单独证明同一 Memory；
- Chapter 与 Chapter 共享同一 RawAsset 是硬冲突；Chapter 与 Aha 共享 Evidence 不自动冲突；
- pair conflict 不具有自动传递性；
- 搜索失败、预算失败或唯一潜在 Memory 尚未判定时不能伪装成 `EMPTY_DAY`。

### 9.2 当前 Chapter 选择（`IMPLEMENTED，但待验证`）

见第 7.7 节。它使用完整候选池做组合搜索，但“数量第一”的目标可能与质量优先原则冲突。

而且当前 V04 是先把 Chapter 集合固定，再选择 Aha，并没有实现上述 Chapter / Aha 联合计划，也没有完整的 removal test、Revision lineage 和第五章 exceptional increment gate。

### 9.3 当前 Aha 生成与选择（`IMPLEMENTED，但明显不完整`）

确定性 Aha 候选满足：

- Observation 为 KEEP；
- Salience 为 HIGH；或
- Salience 为 MEDIUM 且 Event Kind 属于局部峰值类别。

模型也可提出 Aha，但必须：

- 只引用一个 Observation；
- Event Kind 是允许的峰值事件；
- Salience 为 MEDIUM / HIGH；
- 所有事实引用有效。

候选按 Observation 去重。当前最终选择基本按素材时间顺序取前 3 个，并只有一个较窄的独立性规则：

- 如果是生日 Chapter 内的 ceremony / result，则通常判定为 Chapter 高潮，不再作为独立 Aha。

### 9.4 当前 Aha 的主要风险（`OPEN / GAP`）

1. **时间顺序偏置：** 更早的普通候选可能挤掉后面更精彩的候选。
2. **独立性规则过窄：** 目前只对生日类高潮有明确特殊处理。
3. **缺少独立记忆价值评分：** 事件显著不等于值得单独成为 Aha。
4. **Discovery Recall 不稳定：** 普通生活中的小发现可能被 S04 标成 ACTION / NONE，之后再也无法进入 Aha。
5. **多层保守导致零 Aha：** S04、KEEP、候选、Writer 任一层淘汰，最终都可能为 0。
6. **不能用配额补救：** 目标是积极寻找，但不能把普通镜头硬写成惊喜。
7. **候选来源不足：** 冻结构想还包括 local semantic delta、novelty spike、motion/event peak、Manual intent、personalization signal 和未来 audio signal；当前 V04 主要依赖 S04 Event Kind / Salience 及一次模型提案。

希望 Claude 给出一种比“按时间取前 3 个”更稳健、又不会鼓励虚构的 Aha 排序和独立性判断方法。

---

## 10. S10 — Final Media Selection

### 10.1 Chapter（`FROZEN` + `IMPLEMENTED`）

- 正常最终展示 3～5 个素材；
- 严格的 compact 例外可使用 2 个；
- V04 从候选成员中选择最多 5 个；
- hero 倾向质量较好、主体更明确、时间位置较居中；
- 强制考虑 first / hero / last；
- 其余按 motif / subject 新颖度、时间分散和质量补齐。

Production 目标媒体类型为 `PHOTO / LIVE_2S / VIDEO_5S`。Hero 必须恰好一个并来自正文集合；顺序必须是先确定 Representative Evidence / EvidenceAnchor，再决定展示为 Photo、Live 还是短 Video，不能分别先选“最好照片、最好 Live、最好视频”后再拼。

### 10.2 Aha（`FROZEN` + `IMPLEMENTED`）

- 最终恰好 1 个可见素材；
- 当前使用 Aha 的 core Observation。

Production Aha 只允许 `PHOTO / LIVE_2S`，不使用 `VIDEO_5S`。Support / Context 可以帮助理解，但不能变成第二个可见素材或第二个事件。

### 10.3 风险（`OPEN / GAP`）

- Beat coverage 没有被作为完整优化问题；
- motif / subject 多样性不一定等于叙事完整；
- 第一、英雄、最后的启发式可能保留低信息过渡帧；
- 当前 Web 展示的是 Evidence Frame，不是最终 HQ 原图 / 原视频。

---

## 11. S11 — Grounded Writer 与 Canonical Tags

### 11.1 写作定位（`FROZEN`）

Chapter 1.0 不要求长篇故事：

- Title：中文测试优先 2～10 个可见字符，确有必要可放宽到 12；
- Story：默认 1 句话，最多 2 句话；
- 文字可以有轻微氛围，但不能替用户编造心情；
- 死板的事实分类交给 Tag，不必把文案写成标签清单；
- Aha：一句话，中文测试控制在 20 个可见字符内；
- 英文及其他海外语言必须另做 locale-specific 长度、显示和评估合同，不能机械照搬中文字数。

正式 Claim Ledger 可记录的来源类型包括：

- `USER_CONFIRMED`
- `OBSERVED`
- `DEVICE_METADATA`
- `MAP_LOOKUP`
- `DERIVED`
- `INFERRED`
- `UNKNOWN`

`INFERRED` 默认不能承担核心用户事实；当前 V04 主要只公开由视觉 Observation 支持的 claims，并未实现上述全部来源。

### 11.2 当前 Writer 调用（`IMPLEMENTED`）

- Writer 只读取最终入选媒体对应的 Observations 和允许事实，不读取整日开放式素材摘要；
- 每个输出必须引用 Grounded Claim ID；
- 不得添加未出现的精确地点、身份、关系、情绪、喜好、味道、意图和因果；
- Chapter title 硬上限 12 个可见字符；
- Chapter story 目标 ≤48 个可见字符，但目前超出只记录审计，不硬阻断；
- Aha line 必须 1 句且 ≤20 个可见字符；
- 若部分项目不符合合同，只把不合格 ID 交给 Writer 做一次 bounded retry；
- 最多重试 1 次；
- 仍无合格叙述的项目逐项阻断；
- 若有入选候选但全部因 Writer 阻断，输出 `PIPELINE_BLOCKED`，不能返回 `EMPTY_DAY`。

当前敏感、无证据时会阻止的词包括：

`最爱、难忘、幸福、好吃、惊喜、悠闲、开心`

### 11.3 文风要求（`FROZEN`）

不接受：

> 牌坊和木雕，构成了上午这段街巷漫步的主要画面。

原因：像系统总结，不像自然回忆。

期望更接近：

> 牌坊之后，又遇见了藏在木雕里的老手艺。

但只有画面确实支持“先后”“木雕”“老手艺”时才能这样写。

允许有限度的共识性轻情绪，例如对小猫使用“调皮的小插曲”，但不能扩展成“我很开心”“它故意逗我”等未经证据支持的个人感受和意图。

### 11.4 Canonical Tags（`FROZEN` + `IMPLEMENTED`）

最多四个维度，每个维度最多一个：

- `ACTIVITY`
- `SETTING`
- `CENTRAL_SUBJECT`
- `OCCASION`

每个记忆 0～4 个 Tag。当前从 Observation 的 Episode / Setting / Activity / Subject 确定性投票产生，不允许自由生成。

**风险（`OPEN / GAP`）：**

- 词表覆盖仍有限；
- V03 真实结果出现集市缺少 Setting / Activity Tag；
- 当前敏感词黑名单既可能过于生硬，也不可能穷尽所有隐性编造；
- “轻情绪共识词”还没有形成可泛化、可测试的合同；
- Writer 单模型路由尚未证明最优，当前没有单独比较其他 Qwen 文本模型。

---

## 12. S12 — Read-only Validation

### 12.1 原则（`FROZEN`）

S12 只做最终验证：

- Schema 是否满足；
- Grounding 是否完整；
- 字数和句数是否满足；
- 媒体数是否满足；
- Candidate 和最终输出引用是否一致；
- Tag 是否来自词表；
- 日输出数量是否满足上限；
- 输出状态是否真实。

Validator 不能为了“让输出过关”而悄悄改标题、删事实或换素材。修订必须回到有权修改的阶段，并保留审计痕迹。

### 12.2 当前 V04（`IMPLEMENTED`）

- JSON Schema + 本地确定性合同为最终权威；
- Qwen JSON Object mode 只保证尝试返回 JSON，不等于严格 schema；
- 无法验证的模型字段被拒绝或降级；
- 每个失败阶段记录失败原因、请求 ID、token、耗时和成本。

---

## 13. S13 — HQ Materialization / Export

### 13.1 目标（`FROZEN`）

- 已选内容再回到高质量原图 / 原视频进行最终物化；
- 用户可见导出与内部审计输出分离；
- 不能把中间 Evidence Frame 当成永久用户资产；
- 生产系统需要对象存储、生命周期、权限、删除、失败恢复和版本化合同。

### 13.2 当前状态（`OPEN / GAP`）

当前 Web Preview 不执行正式 S13：

- 只展示本地 Evidence Frame；
- 没有正式云存储写入；
- 没有 App 用户资产物化；
- 没有 Production 数据生命周期证明。

---

## 14. 当前 API 与数据调度

### 14.1 Web 到本地算法服务

**当前 V04 端点（`IMPLEMENTED`）：**

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/health` | 服务、模型和合同版本健康状态 |
| `POST` | `/x02/v0.4/preview` | 上传一次 Evidence Bundle 并执行完整 V04 Preview |
| `POST` | `/x02/v0.4/run-sidecar` | 写入客户端阶段耗时和人工评价等侧车证据 |

历史 V03 端点仍保留：

- `/x02/v0.3/preview`
- `/x02/v0.3/run-sidecar`

Web 当前只接受 V04，防止算法已经升级但前端悄悄显示 V03 结果。

### 14.2 Preview 请求

`POST /x02/v0.4/preview` 使用 multipart：

- `manifest`：JSON，描述 bundle、素材、帧、顺序和运行身份；
- 每个 Evidence Frame：独立 multipart 字段；
- 最大素材数：240；
- 最大请求体：512 MiB；
- 原始素材上传数：0；
- 模型只接触标准化 Evidence。

Sidecar 为 JSON：

- 最大 2 MiB；
- 绑定 session / run / bundle / pipeline / request；
- 可记录浏览器预处理耗时、用户评价和定位到具体 Chapter / Aha / asset / frame 的反馈。

### 14.3 本地与非本地安全边界（`IMPLEMENTED`）

- 仅 loopback 的研究服务可在开发阶段不启用 TLS / bearer token；
- 非 loopback 监听必须提供 TLS certificate、TLS key 和 bearer token；
- CORS 使用精确 allowlist；
- API key 只存在算法服务进程环境或 macOS Keychain；
- API key 不进入浏览器、不进入 App、不写入本文和审计文件。

当前公开内部测试已暂停；现阶段是本机研究测试页，不是公网生产服务。

### 14.4 正式 App / 云端的数据去向仍未冻结（`OPEN / GAP`）

当前 Web 只把标准化 Evidence 发给本地研究服务，因此不能回答未来正式系统中以下问题：

- 原始素材中的哪些进入长期云存储；
- 哪些只在手机保留；
- 哪些 Evidence 发给第三方模型 API，哪些只发给自有服务；
- 选中素材的 HQ 原件什么时候上传；
- 用户删除、撤回、换设备和账号注销如何传播；
- Preview 与 Final 的对象存储生命周期；
- 海外用户与中国大陆用户是否使用不同数据区域和模型路由。

这些问题被有意留到核心内容质量链路打通后再冻结，不应由当前测试实现反推答案。

---

## 15. 当前模型路由与调用次数

### 15.1 当前默认 Provider（`IMPLEMENTED`）

- Provider：Alibaba Model Studio / DashScope；
- API 形态：OpenAI-compatible Chat Completions；
- URL：`https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`；
- 当前模型：`qwen3-vl-flash-2026-01-22`；
- `response_format = {"type":"json_object"}`；
- `enable_thinking = false`；
- `stream = false`；
- 每次模型调用超时：180 秒；
- schema 会写入 prompt，但本地确定性校验仍是权威。

凭据来源：

1. 环境变量 `DASHSCOPE_API_KEY`；或
2. macOS Keychain service `DiaryOne DashScope API Key`。

本文不包含任何凭据值。

另有 OpenAI Responses API adapter，可使用 strict JSON Schema、`store=false` 和低细节图片输入，但它不是当前默认真实测试路径，也不能据此声称 OpenAI 路线已经验证。

### 15.2 一次 N 素材完整运行的调用计划（`IMPLEMENTED`）

1. **S04 Perception：** `ceil(N / 6)` 次多模态调用；每次最多 6 个素材，携带这些素材的全部选定 Evidence Frame。
2. **S05～S07 Structure Proposal：** 固定 1 次结构化文本调用；输入为已验证 Observations / Moments，不再传图。
3. **S11 Writer：**
   - 没有任何入选记忆：0 次；
   - 有入选记忆：1 次；
   - 存在不合格文案：只对不合格 ID 再重试 1 次。

因此：

- 常规调用数：`ceil(N / 6) + 2`；
- Writer 发生一次 bounded retry：`ceil(N / 6) + 3`。

当前无额外模型调用的阶段：S03、简化 S05、S06、当前 S08 / S09、S10、S12。S13 未执行。

### 15.3 对当前调度的疑问（`OPEN / GAP`）

1. 所有阶段使用同一个视觉模型是否合理，Writer 是否应改用更适合短中文文案的文本模型？
2. 每批 6 个素材是否是质量 / token / latency 的最佳点？目前只是工程合同，不是已校准最优值。
3. S04 把所有帧直接放入批次，长视频 Evidence 较多，token 会迅速增长。
4. Structure Proposal 只调用一次，若模型遗漏候选，本地八类 Focus 又覆盖不足，整条 Storyline 会消失。
5. Writer 只重试一次是合理的 fail-closed 边界，还是会让本来正确的记忆因文字格式错误而全部丢失？
6. 当前 S08 不完整，因此调用数低并不等于正式完整 Pipeline 成本。

### 15.4 目标中的 Model Gateway 要求（`FROZEN`，当前仅部分实现）

统一 Gateway 未来需要集中管理：

- model registry 与版本快照；
- 输入模态和 Evidence exposure envelope；
- structured output 与本地合同验证；
- batch、exact cache 和 idempotency；
- provider fallback；
- 模型层级升级；
- token / cost / latency / request ID；
- 供应商失败和语义能力不足的独立错误归因；
- 隐私区域与删除要求。

关键路由原则：

- Provider failure 可以 fallback 到同等级可替代 Provider；
- 不能因为供应商故障就自动升级到更昂贵 Strong Model；
- 只有当前模型在语义上确实无法完成受限任务时，才允许按预算和审计合同升级；
- Fixture 只能用于合同测试，不能被展示成真实用户 Memory；
- Provider / model / prompt / schema / price 的任一变化都必须在运行证据中可追溯。

---

## 16. 成本与耗时

### 16.1 产品成本目标（`FROZEN`）

- Cohort average：`≤ US$1.50 / user / month`；
- 工程目标：约 `$0.90 / user / month`；
- 预警线：约 `$1.20 / user / month`；
- 重度用户可以超过 `$1.50`，因为约束是 cohort average，不是每个用户硬封顶。

### 16.2 当前代码中的 Qwen 价格快照（`IMPLEMENTED 配置，但可能过期`）

对 `qwen3-vl-flash*`：

- 输入：CNY 0.15 / 1M tokens；
- 输出：CNY 1.50 / 1M tokens；
- 汇率配置：CNY 7.20 / USD；
- 价格 basis 日期：2026-08-18。

成本公式：

```text
native_cost =
  (input_tokens × input_rate_per_million
   + output_tokens × output_rate_per_million) / 1,000,000

estimated_cost_usd = native_cost / cny_per_usd
```

该价格只是可复现的代码配置，不是当前供应商账单真值。正式决策必须使用实时官方计费和实际账单复核。

### 16.3 最近一次完整记录的真实运行（`REAL_EVIDENCE，V03`）

Person 1 素材包：

| 指标 | 结果 |
|---|---:|
| 视频数 | 20 |
| 总视频时长 | 298.697 秒 |
| 原素材大小 | 42.2 MB |
| Evidence Frame | 74 |
| Evidence 大小 | 9.0 MB |
| 可用 Observation | 20 |
| 正常 / 降级 / 整体失败 | 17 / 3 / 0 |
| 模型调用 | 7 |
| 输入 tokens | 110,914 |
| 输出 tokens | 12,791 |
| 配置价格估算 | US$0.0049755 |
| 算法服务耗时 | 169.216 秒 |
| 用户总等待 | 284.582 秒 |
| 浏览器 Evidence 生成 | 115.203 秒 |
| 输出 | 2 Chapters + 1 Aha |

### 16.4 真实运行的正确解释

- 成本看起来很低，但只代表一个 20 视频测试包和当前不完整 Preview；
- 74 帧产生约 11 万输入 tokens，说明视觉 token 仍需严肃测量；
- 浏览器串行抽帧占用户等待约 40%，不能只优化模型耗时；
- 2 Chapter +1 Aha 的数量不代表质量通过；
- V03 的 Chapter 聚类和 Aha 选择未达可用标准；
- V04 尚无同等真实运行证据，因此不能用这组结果证明 V04 已修复。

---

## 17. 最近真实测试暴露的问题（V03）

### 17.1 Chapter 聚类错误

一个 Chapter 同时出现“人间烟火”和“青石板路 / 古镇漫步”，说明粗粒度 Episode 与 coverage-first 选择把不同 Storyline 混在了一起。

### 17.2 重要旅游内容被砍掉

古镇逛街和文化观察素材在多层过滤后没有形成清晰候选。问题不一定只在一个阈值，可能是：

```text
S04 单标签不准确
  → S05 错切 / 错连
  → 候选不成立
  → S09 覆盖偏置
  → S10 / Writer 再次淘汰
```

### 17.3 Aha 选择弱

- 主要按时间顺序选择；
- 后面更好的发现可能被早期普通候选挤掉；
- Aha 与 Chapter 的故事独立性不足；
- Writer 合同失败会进一步减少最终数量。

### 17.4 文案不自然

Chapter 文字偏长、偏系统总结；有时虽然事实正确，但像“给画面做报告”，不像记忆。

### 17.5 Tags 不完整

集市场景没有稳定产生 Setting / Activity 标签，影响未来检索体系。

### 17.6 评估反馈不够细

旧版反馈无法精确绑定：

- 哪个 Chapter；
- 哪个 Aha；
- 哪张图片 / 哪段视频 / 哪一帧；
- 是边界、选材、标题、正文、Tag，还是 Aha 独立性问题。

当前 Web 已朝细粒度评价结构修改，但还需要真实使用验证。

---

## 18. 当前 V04 已经修了什么、还没证明什么

### 18.1 已实现并有自动化测试的变化（`IMPLEMENTED`）

- V04 独立 schema / pipeline / API 路径；
- Web 拒绝展示旧 V01 / V03 结果；
- Observation 字段级降级，不再因一个非关键字段错误丢掉整个素材；
- 引入 Storyline Focus / Basis / Beat；
- 去掉 Chapter 成员必须完全同 Episode 的硬门槛；
- 确定性候选 + 模型提案候选；
- 完整候选池组合搜索，不再只看前 16 个；
- Writer 只读取入选媒体的允许事实；
- Writer bounded retry；
- Storyline 分组依据和每素材 Beat 可在 Web 展示；
- 运行和失败审计保留 stage latency / tokens / cost / request ID；
- 评价可绑定具体输出对象和素材证据。

### 18.2 尚未证明的内容（`OPEN / GAP`）

- V04 是否能把古镇素材稳定分成 2～3 条纯净 Storyline；
- V04 是否会因八类 Focus 限制漏掉普通生活 Chapter；
- “数量第一”的组合目标是否造成过度产出；
- Aha 是否能在三种用户素材中稳定找到真正独立的小精彩；
- Writer 是否能稳定生成自然、短、可信的中文；
- Canonical Tags 是否覆盖真实用户语义；
- 20、100、186、240 素材下的延迟和成本曲线；
- 手机侧 1-or-3 Auto 上传节省是否显著；
- Production 异步、存储、删除、权限和恢复能力。

### 18.3 当前已经识别出的合同漂移（`OPEN / GAP`）

以下不是 Claude 需要自行猜测的问题，而是本次整理时已经确认的实现与冻结定义差异：

1. 冻结定义要求 `HIGHLIGHT_DAY = 0 Chapter + exactly 1 strong Aha`；当前 V04 的 Aha selector 最多可选 3 个，只要没有 Chapter 且至少有一个公开 Aha 就标成 `HIGHLIGHT_DAY`。因此当前实现可能产生包含 2～3 个 Aha 的 `HIGHLIGHT_DAY`，需要在真实测试前决定由选择层还是最终状态合同修正。
2. 冻结定义允许第 5 个 Chapter 作为严格例外；V04 Preview 的代码上限是 4。它可以作为当前研究版本限制，但不能被误称为完整实现了第五章例外。
3. 冻结版产品 Preview 容量是最多 4 Chapter / 2 Aha；当前 V04 Research Preview 共用 `MAX_AHAS = 3`。若二者被视为同一类 Preview，这是容量合同漂移；若研究 Preview 有意例外，也应显式命名，而不是依赖读者猜测。
4. 冻结版 S09 是 Chapter / Aha 联合选择；当前 V04 先固定 Chapter，再按时间顺序选择 Aha，Aha 不能反向改变 Chapter 计划。
5. 冻结版数量偏好必须位于合法性、边际独立价值、有效覆盖、可信价值和冗余风险之后；当前 V04 的 Chapter objective 首先最大化数量。
6. 运行审计把当前确定性选择阶段标记为 `S08_S09_SET_SELECTION`，但完整冻结版 S08 并未执行；这个名字不能作为 S08 已实现的证据。
7. 当前选择器的算法标签含有 `PURITY_FIRST`，但实际目标元组先最大化 Chapter 数量，再看 Focus 多样性与质量。标签与真实优化顺序不完全一致，审阅应以代码中的 objective tuple 为准。

### 18.4 Personalization 边界（`FROZEN，当前 V04 未执行`）

V1 未来可以使用：高频活动、高频地点、匿名实体聚类、历史 Tag、Manual association 和 Chapter 交互信号。但它只影响 Selection，不得修改 Facts，也不能被用来推断人物关系、长期人物图谱或用户内心。用户删除 Memory 后，关联 personalization signal 至少要支持 invalidate / decrement / rebuild。

---

## 19. 三套真实素材的验证计划

以下目录由素材所有者授权用于后续算法测试，但本项目只能只读使用，不能修改、移动或删除：

- `OWNER_CONTROLLED_TEST_PACK_1/`
- `OWNER_CONTROLLED_TEST_PACK_2/`
- `OWNER_CONTROLLED_TEST_PACK_3/`

### 19.1 运行原则（`FROZEN`）

- 三个素材包分别作为独立的一天；
- 每次正式质量测试都跑完整 Pipeline；
- 不使用 Gate0 快捷抽样代替完整运行；
- 每次是 fresh full run；
- 不因为第一个包通过就直接宣布泛化；
- 先收集细粒度评价，达到一定数据量后再讨论阈值和规则修改；
- 不允许评价自动写回算法。

### 19.2 Gate 顺序

1. **Gate1：Evidence / Observation 可靠性**
   - 每个素材都被处理；
   - 坏素材不会卡死；
   - 字段级降级可解释；
   - 事实引用正确。
2. **Gate2：Storyline 分段与 Chapter 聚类**
   - 故事不混；
   - 不把同一长期经历因短暂插曲永久切断；
   - 重要经历不被漏掉；
   - 数量合理但不以数量代替纯度。
3. **Gate3：Aha 发现与独立性**
   - 积极发现小精彩；
   - 不把 Chapter 高潮重复包装成 Aha；
   - 不按时间先后机械抢占名额。
4. **Gate4：Media / Writer / Tags / UX**
   - 3～5 个素材相关且不重复；
   - 文案短、自然、可信；
   - Tags 可用于检索；
   - 失败状态对用户和评估者可理解。

### 19.3 Gate2 对旅行素材的预期

如果证据支持，应能形成 2～3 条候选 Storyline，例如：

- 当地集市 / 摊贩 / 街头生活；
- 古建筑 / 牌楼 / 木雕等文化发现；
- 青石板 / 河道 / 沿途景色等路线漫步。

这只是期望的可解释分法，不是提前写死答案。若真实画面不支持，就不能硬凑三条。

### 19.4 评价维度

- Chapter purity；
- Missing storyline recall；
- Over-split / Under-split；
- Aha discovery recall；
- Aha independence；
- Media relevance；
- Media redundancy；
- Fact grounding；
- Title / Story 自然度；
- Canonical Tag 正确性与覆盖；
- 每阶段时间；
- 每阶段模型调用、input/output token 和成本；
- 整体等待时间。

---

## 20. 希望 Claude 重点回答的具体问题

### 20.1 Storyline 与聚类

1. 先给每个 Observation 分配单一 Primary Focus，再聚类，是否从架构上就会过度压缩多义素材？
2. 是否应允许一个 Observation 拥有多个带置信度的 semantic facets，再由候选层决定它在不同 Storyline 中的作用？
3. 怎样实现“古镇 → 奶茶店 → 古镇”的恢复逻辑，同时不把所有古镇素材混成一条？
4. 是否应让每个候选主动生成 `split alternative`，比较整体一致性与拆分后纯度？
5. 如何把“同一主题持续较长时间，允许 2～3 张相似但时间相距较远的不同古建筑外观”写成可泛化规则，而不是古建筑特例？
6. `source-order gap ≤8` 应怎样替换或兼容真实时间、采集覆盖和语义恢复？
7. Chapter 数量是否应该从当前目标元组第一位下降为软奖励？建议怎样设计多目标函数？
8. 八类 Focus 应扩展、层级化、开放生成，还是用 embedding / prototype / LLM thesis 共同决定？

### 20.2 Aha

1. 怎样定义“局部高点”和“独立记忆价值”两个不同维度？
2. 怎样避免 Aha 被时间顺序决定？
3. 怎样识别小发现、小变化、小互动，而不是只有生日、宠物、食物等显式类别？
4. 怎样做到“尽量有 Aha”但不通过降低 grounding 或编造 surprise 来凑数？
5. Chapter 内发生的素材何时可以成为独立 Aha？能否提出跨场景通用的 independence test？
6. Aha Writer 失败时，是否应该先尝试确定性短句模板，而不是直接丢失整个正确候选？

### 20.3 Observation 与模型调用

1. 每批 6 个素材是否会造成跨素材污染或观察遗漏？
2. 一个素材只输出一个 Observation 是否足够？长视频是否应先形成多个 content unit？
3. 哪些字段最适合视觉模型，哪些应由 embedding / classifier / local CV 产生？
4. 当前所有阶段使用 qwen3-vl-flash 是否合理？Writer 是否应单独路由到 Qwen 的文本模型？
5. schema 写入 prompt + 本地校验是否足够，还是应增加 constrained decoding / function calling / 分阶段修复？
6. 怎样降低视觉 token，而不明显伤害 discovery recall？

### 20.4 Writer 与用户体验

1. 如何系统定义“轻微、共识性氛围词”，避免只有黑名单？
2. 怎样判定一句话虽然事实正确但“像报告、不像记忆”？
3. 是否应将事实文案和氛围润色拆成两个受限步骤，还是会增加成本和错误面？
4. 中文 ≤48 字 Chapter Story 是否仍过长？是否应改成更强的目标，而非只审计不阻断？
5. Writer 格式失败是否应该让结果 `PIPELINE_BLOCKED`，还是展示确定性 fallback 更符合用户体验？

### 20.5 成本、效率和 Production

1. 对 186 素材参考日，当前 `ceil(N/6)` 多模态调用是否合理？
2. 视觉帧 token 与输入素材数的近似增长模型应怎样建立？
3. 哪些阶段值得缓存，如何避免正式评测因缓存掩盖真实过程？
4. 浏览器抽帧串行耗时应如何优化；未来应由 App、边缘端还是云端负责？
5. 当前低成本是否主要因为 S08 / S13 尚未实现？
6. 达到月均 $0.90 工程目标，至少需要哪些 cohort 假设和压力测试？

---

## 21. 我们对建议的接受标准

我们更重视下面这种建议：

> 当前候选选择把 Chapter 数量放在目标元组第一位，会在存在 4 个刚过门槛但高度相似的候选时优先选择 4 个。建议把“每增加一个 Chapter 的边际收益”设计为递减软奖励，并让 purity / unique content units 先于数量；用 Person1 古镇包比较 V04 原目标与新目标的候选集合、纯度和遗漏率。

而不是：

> 可以提高聚类效果，优化 Prompt，并使用更强模型。

建议应尽量满足：

- 指向具体阶段和对象；
- 说明错误为什么发生；
- 提供最小实现或伪代码；
- 给出可重复的测试；
- 说明可能副作用；
- 不把某个旅行案例硬编码成全局规则。

---

## 22. 当前状态与后续路线

### 当前状态

| 项目 | 状态 |
|---|---|
| 冻结的 S00～S13 产品架构 | 已有 |
| V04 Storyline 工作树 | 已实现、未提交 |
| V04 算法自动化测试 | 124 个通过，1 个因测试沙箱禁用本地 socket 而跳过 |
| V04 Web 合同 | 已适配、未提交；lint、build、2 个 rendered HTML tests 通过 |
| V04 Person1 真实全流程 | 尚未运行 / 验收 |
| V04 Person2 / Person3 | 尚未运行 |
| Gate2 真实质量 | 未通过证明 |
| Gate3 Aha | 部分实现，已知明显缺口 |
| Gate4 Writer / Media / Tags | 部分实现，未验收 |
| S13 | 未执行 |
| Production | `FALSE` |

### 建议的实际工作顺序

1. 先用 Person1 完整运行 V04，验证 Storyline 是否真的修复 V03 的古镇混聚类；
2. 不立即改代码，先把每个 Chapter / Aha / asset / expression 的问题结构化记录；
3. 若 Gate2 仍失败，归纳跨场景共同机制，再改 Storyline；
4. Person1 Gate2 达到预期后，运行 Person2 / Person3 检查泛化；
5. 进入 Gate3，重做 Aha 排序与独立性，而不是只调阈值；
6. 进入 Gate4，验证媒体选择、短文案和 Canonical Tags；
7. 形成 V1.0 真实验证基线后，再讨论 App 后台、对象存储、异步队列和 Production S13。

Claude 可以反对这个顺序，但请说明为什么，以及替代顺序如何降低总体试错成本。

---

## 23. 代码与文档证据索引

### 23.1 当前代码工作树

- Repository：`diary-one-cloud-intelligence`
- Branch：`codex/validation-v01-v02-20260829`
- 基础 HEAD：`aa9917ad2948550d4ce891d0cc3ca7b8acd1e9db`
- V04 当前为未提交工作树，不能把上述 HEAD 当成包含 V04 的 commit。

### 23.2 当前未提交 V04 文件

- `src/diary_one_ci/x01_server.py`
- `src/diary_one_ci/x02.py`
- `tests/test_x01.py`
- `tests/test_x02.py`
- `contracts/x02_staged_preview_v04.schema.json`
- `src/diary_one_ci/contracts/x02_storyline_v01.json`

`var/` 是本地运行审计和输出目录，不应提交。

### 23.3 当前 Web 研究客户端

- Repository：`web-functional-sandbox`
- Branch：`main`
- 基础 HEAD：`4336bc80d56777158dd00c58b5be6e8caac6a2e9`
- V04 适配当前也是未提交工作树。
- 修改文件：
  - `app/globals.css`
  - `app/lib/contracts.ts`
  - `app/lib/media-evidence.ts`
  - `app/page.tsx`
  - `tests/rendered-html.test.mjs`
- 2026-09-02 复核：ESLint 通过；production build 通过；2 个 rendered HTML tests 通过。

### 23.4 核心文件 SHA-256（2026-09-02 快照）

| 文件 | SHA-256 |
|---|---|
| `src/diary_one_ci/x01_server.py` | `6e596962975b5ea392006e5ff134e06d41e43849363cf3f738495eda6a02295f` |
| `src/diary_one_ci/x02.py` | `7cecdc412def23a9ad7dde21b0c495dabc1fa269937789aa23c8a562d1636e9f` |
| `src/diary_one_ci/contracts/x02_storyline_v01.json` | `dddb03b4a5a35e4d7d83c0fee7dbb02dc4e8f30cabba074ebe84c5a229616e8b` |
| `contracts/x02_staged_preview_v04.schema.json` | `41c13a97a312318f0882bb411abce21b7c8ce5f89edb38584a250f42a548bb52` |
| `docs/00_READ_FIRST.md` | `5e2e02e2f9878c06a510de476a979df2b5ad616966bc4230822599bb799b70a4` |
| `docs/CANONICAL_CHECKPOINT_V1_25_PRODUCTION_SHAPED_PIPELINE_V1_0.md` | `577cb5bbb073fa9277b181bfe721b22176bdccd71585b4ff4a3fc28296346b0f` |
| `docs/CANONICAL_CHECKPOINT_V1_29_REAL_MEDIA_QUALITY_RECOVERY.md` | `4ed629288d7b23a6038be3166b9463119e9994b9d4c049a6c1011cbafe447e36` |
| `docs/INTEGRATION_CHECKPOINT_V1_30_X02_V03_GATE1_EVIDENCE_AND_FIELD_RELIABILITY.md` | `7059cc2a57a278ccd20053bf9c5e8c38d0f408765f5596e6587883b02e5a7f21` |
| `docs/GATE2_STORYLINE_SEGMENTATION_GENERALIZATION_WORKING_V0_1.md` | `f03804edd8b51778bde309b74388a5ecc3c8170a987799f475e3d91adab36315` |

Web 关键文件指纹：

| 文件 | SHA-256 |
|---|---|
| `app/lib/contracts.ts` | `86cc9c4fdf81c6390eda5c30130f327a0a61b8f4c42455b2d31475eebd3db2f4` |
| `app/lib/media-evidence.ts` | `b5e86b568206cdba6ad5ccea523c7299aa6203001a747da96e4a25a76d0d25ce` |
| `app/page.tsx` | `a68c16ccb2ecc522bc5862ae3533c01f39cf7f1561ab03dcc5142b2c9a1682ed` |
| `app/globals.css` | `34902af2a7362643304466c7e057275bfb79da5675a1dbcc729892115a81a30d` |
| `tests/rendered-html.test.mjs` | `1ec8e6bc595a8e7ef2eef0a9079fcf35456340b2612f3aa6950261f5cca24dfb` |

### 23.5 主要设计文档

- `docs/00_READ_FIRST.md`
- `docs/END_TO_END_PIPELINE_LOGIC_TEAM_SYNC_V0_1.md`
- `docs/CANONICAL_CHECKPOINT_V1_25_PRODUCTION_SHAPED_PIPELINE_V1_0.md`
- `docs/CANONICAL_CHECKPOINT_V1_29_REAL_MEDIA_QUALITY_RECOVERY.md`
- `docs/INTEGRATION_CHECKPOINT_V1_30_X02_V03_GATE1_EVIDENCE_AND_FIELD_RELIABILITY.md`
- `docs/GATE2_STORYLINE_SEGMENTATION_GENERALIZATION_WORKING_V0_1.md`
- `docs/X02_CURRENT_WORKFLOW_EXPLAINED_AND_QUALITY_DIAGNOSIS_V0_1.md`
- `docs/ALGORITHM_GLOSSARY_V1_0.md`

注意：部分历史文档仍描述 V01 / V03，或把 Gate2 标为“未实现”。它们是历史证据，不应覆盖当前 V04 工作树；同样，V04 工作树也不能反向改写历史 checkpoint。

---

## 24. 最后一条诚实结论

当前系统已经形成一条结构完整、可审计、可运行的研究 Pipeline，也开始从粗粒度 Episode 聚类转向 Storyline。但用户对最近真实结果的评价是“不可用”，这个判断是成立的：最后一次真实质量证据来自 V03，V04 还没有被真实素材证明；Aha 仍有明显的排序与独立性缺陷；S08、S13 和 Production 仍未完成。

因此这次交叉验证的目标不是替现有方案背书，而是找出下一轮真实测试之前最值得修正的结构性问题，并把每条建议转成可观测、可回归的实验。
