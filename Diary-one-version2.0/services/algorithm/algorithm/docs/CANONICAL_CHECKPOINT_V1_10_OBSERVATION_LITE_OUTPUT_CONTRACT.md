# Diary One Canonical Checkpoint V1.10 — Observation Lite Minimum Output Contract

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** S04 Observation Lite 的最小输出、状态、逐事实证据绑定与职责边界
**继承关系：** 继承 V1.9–V1.1 与 V1.0 未被覆盖的规则

> **当前 S06 覆盖：** V1.16 冻结 status-to-role 合同：`KEEP` 只允许 `OBSERVED/PARTIAL` 且必须引用当前 Window 的 `STRONG/MODERATE` grounded item；`INSUFFICIENT_EVIDENCE` 禁止 KEEP；`FAILED` 在当前已提交 Revision 中为 `DROP_FROM_MEMORY_OUTPUT`；多个 WEAK 不能投票升级。

## 1. 冻结结论

S04 对每个 Evidence Window 生成一张简洁、结构化、可核查的“事实观察卡”：

```text
Current Window Evidence
+ WindowIntrinsicSignal
+ trusted source facts
→ one Window-local Observation Lite
```

采用“固定结构字段 + 少量原子事实”的混合合同：

- 固定字段让不同 Window 可以稳定比较，并支撑 S05 Moment Formation；
- 原子事实保留固定分类难以表达、但画面直接支持的生活细节；
- 每个肯定性语义条目都必须绑定本 Window 内实际上传的 Frame；`UNKNOWN` 与输入缺失只记录原因，不伪造支持；
- S04 不生成长 Caption，不做重要性、Chapter、Aha 或个人意义判断。

## 2. 术语释义

### 2.1 Observation Lite

AI 对一个最小 Evidence Window 的低成本事实理解。它回答“当前证据直接支持什么”，不回答“这段生活意味着什么”。

### 2.2 原子事实（Atomic Fact）

一条只表达一个可核查事实的短句。例如：

- “桌面上有一个杯子。”
- “画面中可见两个人。”
- “第一帧为室外，后续帧为室内入口。”

不允许把多个观察、猜测、因果和意义写成一段叙事。

### 2.3 Evidence support grade

它表示某一条事实被当前输入画面支持的强弱，不是模型自报的准确概率，也不是整张 Observation 的总分。

### 2.4 Envelope / Payload / Validator

- Envelope：系统为一张观察卡绑定的“外壳”，保存 ID、时间、输入、版本和成本等不可由模型改写的事实；
- Payload：模型在外壳内部生成的事实理解内容；
- Validator：用明确规则检查输出是否合法的程序，不是另一个负责猜测内容的 AI。

## 3. 输入边界

V1.9 的 Window-local 输入合同继续生效。S04 只读取：

- 当前 `evidence_window_id` 实际上传的 Evidence Frame；
- 当前 Window 的 `WindowIntrinsicSignal`；
- 可信的 RawAsset 时间、来源、媒体类型与时长事实；
- extraction / upload route manifest；
- 当前 schema、model、prompt、parameter 与 pipeline version。

S04 不读取邻居 Window 的图片、Caption、Observation 或 Moment 归属。S03B `TimelineEdgeSignal` 交给 S05 使用，不进入当前 Window 的事实生成。

## 4. 系统拥有的 Observation Envelope

以下字段由确定性 Workflow 绑定，模型不得生成或改写：

- `observation_id`；
- `evidence_window_id` 与 `raw_asset_id`；
- capture time、source kind、media kind 与 Window offsets；
- `input_evidence_refs[]`：实际输入 Frame ID、content hash 与采样 offset；
- extraction / upload route 与输入完整性状态；
- `observation_status`；
- `memory_candidate_eligible`：只表示是否通过 S04 最低证据门，不表示会被选为 Memory；
- schema / taxonomy / model / prompt / parameter / pipeline version；
- inference attempt、processed time、exact-cache provenance；
- request、token、latency、retry 与 cost trace。

模型输出中的同名字段不得覆盖这些系统事实。

## 5. Observation 状态

顶层状态只允许：

```text
OBSERVED
PARTIAL
INSUFFICIENT_EVIDENCE
FAILED
```

含义如下：

- `OBSERVED`：至少存在一条 `STRONG` 或 `MODERATE` grounded item，且当前 Evidence 足以形成可用、直接支持的 Window 描述；
- `PARTIAL`：至少存在一条 `STRONG` 或 `MODERATE` grounded item，但输入中的显著部分缺失、模糊、遮挡或只得到部分理解；
- `INSUFFICIENT_EVIDENCE`：不存在 `STRONG` 或 `MODERATE` grounded item，无法形成可供 Memory pipeline 使用的直接事实；
- `FAILED`：请求、模型输出或合同校验失败；这是处理失败，不代表该时间点没有内容。

`UNKNOWN` 用于 scene/activity 等字段的未知值或明确原因，不作为第五种顶层状态。

候选门规则：

| 状态 | S04 最低候选门 |
|---|---|
| `OBSERVED` | `memory_candidate_eligible=true` |
| `PARTIAL` | `true`；状态有效性已要求至少一条 `STRONG` 或 `MODERATE` grounded item |
| `INSUFFICIENT_EVIDENCE` | `false`；不补帧、不上传完整 Auto 9s |
| `FAILED` | 当前 Revision 为 `false`；允许按重试策略使用同一份已上传 Evidence 重试，不请求新 Evidence |

通过最低候选门不等于 KEEP、Chapter 或 Aha；这些属于 S06 以后。

## 6. 最小 Perception Payload

Payload 可以理解为“AI 填写的观察内容区”。模型可以生成的最小内容为：

### 6.1 `scene`

- 一个版本化 `scene_family`，允许 `UNKNOWN`；
- 可选的短 `scene_detail`；
- 肯定性 Scene 的 supporting Frame IDs 与 support grade；
- `UNKNOWN` 时使用 reason code，不伪造 Scene 支持。

Scene 只描述可见环境，不推断地点名称、到访目的或事件意义。

### 6.2 `activities[]`

- 只记录画面直接支持的粗粒度活动；
- 使用版本化 Activity Family，允许 `UNKNOWN`；
- 每项绑定 supporting Frame IDs 与 support grade。

“手拿杯子”可以是可见事实；仅凭办公楼画面写“正在上班”不可以。

### 6.3 `visible_entities[]` 与 `visible_objects[]`

- 只记录当前 Window 内明显可见、对理解画面有作用的人、动物或物体；
- 人物只使用 Window-local 匿名描述，例如 `person_1`；
- 不识别姓名，不推断人物关系、身份、性别、年龄或情绪；
- Window-local entity ID 不自动延伸到另一个 Window。

每项都必须绑定 supporting Frame IDs 与 support grade。S04 不做穷举式物体清单。

### 6.4 `atomic_facts[]`

每条至少包含：

- `fact_id`；
- 一条简短、单一、可核查的 `statement`；
- 一个或多个 `support_frame_ids`；
- `support_grade`；
- 可选的 `uncertainty_reason_codes[]`。

原子事实用于补充 Scene / Activity taxonomy 无法完整表达的可见细节，不得退化成长 Caption。

### 6.5 `within_window_changes[]`

- 只描述实际上传的同一 Window 多帧之间直接可见的状态变化；
- 每条至少引用两个按时间排序的 Frame；
- 表述“采样点分别看到了什么”，不能声称中间过程连续发生，也不能推断因果。

`UPLOAD_1` 的 Auto 通常没有可生成的语义变化项。S03A 的数值 change hint 不能单独被改写成具体语义事件。

### 6.6 `limitations[]`

明确记录影响理解的原因，例如：

- blur；
- occlusion；
- darkness / overexposure；
- missing or corrupt input；
- ambiguous subject or action；
- sparse temporal evidence。

限制必须与 `PARTIAL` / `INSUFFICIENT_EVIDENCE` 等状态保持一致。

## 7. 逐条证据强度，不设总置信分

`support_grade` 只允许：

```text
STRONG
MODERATE
WEAK
```

- `STRONG`：当前输入对该条目有清楚、直接的视觉支持；若多个相关 Frame 可用，它们之间不存在明显冲突；
- `MODERATE`：存在直接支持，但只有单帧、局部遮挡、轻度模糊或其他明确限制；
- `WEAK`：只能形成模糊提示，保留用于不确定性、上下文或后续验证，不能单独成为用户可见 Memory Claim。

不设置单一 `observation_confidence`。一个平均总分会掩盖“部分事实很可靠、部分事实完全不可靠”的差异。

support grade 的自动校准、模型间一致性与下游具体阈值必须通过 Benchmark 决定；枚举本身不冒充真实概率。

## 8. Grounding 与合同校验

Grounding 可以理解为“每句话都必须指回它依据的画面”。

确定性 Validator 是规则校验程序，不负责补写或猜测事实。它至少执行：

1. 所有肯定性语义条目引用一个或多个当前 Window 的实际输入 Frame；
2. `within_window_changes[]` 至少引用两个有明确时间顺序的 Frame；
3. 禁止引用同一 batch 中其他 Window 的 Frame；
4. `UNKNOWN` 或输入缺失必须携带明确原因，不能伪造 supporting Frame 或 support grade；
5. Scene / Activity / status / support grade 必须属于当前版本枚举；
6. 模型不得改写系统 Envelope、capture facts 或 route manifest；
7. 任何人物身份、关系、情绪、意图、因果或个人意义推断均视为越界；
8. 合同校验失败不得静默当作正常 Observation。

校验失败可以使用完全相同的 Evidence 按受限策略重试；仍失败则记录 `FAILED` 与完整 attempt trace。

## 9. 可以说与不能说

| 当前 Evidence | 可以输出 | 不能输出 |
|---|---|---|
| 桌上有餐盘和两个杯子 | “桌上可见餐盘和两个杯子” | “用户正在和朋友愉快聚餐” |
| 第一帧街道、后续帧室内入口 | “采样画面从街道变为室内入口” | “用户走进商店购物” |
| 一个人面向电脑 | “一人位于电脑前” | “同事正在处理工作邮件” |
| 模糊、严重遮挡的单帧 | `PARTIAL` 或 `INSUFFICIENT_EVIDENCE` | 用邻居素材补写当前事实 |

## 10. 成本与输出控制

- 多个 Window 仍可 batching，但必须逐 Window 独立输出和校验；
- 输出以短字段、枚举和少量原子事实为主，不生成重复 Caption；
- 完全相同输入与完整 pipeline fingerprint 才能命中 V1.9 exact cache；
- 原子事实、entity、object 和 activity 的最大数量由真实质量/token Benchmark 校准，本检查点不武断冻结；
- 模型、图片分辨率、batch size、并发、timeout 与 retry 次数继续保持 OPEN。

## 11. FROZEN 与 OPEN

### FROZEN

- S04 使用固定结构字段与少量原子事实的混合输出；
- 系统 Envelope 与模型 perception payload 分离；
- 顶层状态为 `OBSERVED | PARTIAL | INSUFFICIENT_EVIDENCE | FAILED`；
- `UNKNOWN` 是字段值，不是顶层状态；
- 每个肯定性 Scene / Activity / Entity / Object / Atomic Fact / Change 都必须绑定本 Window Frame；`UNKNOWN` 与输入缺失必须记录原因；
- 使用逐条 `STRONG | MODERATE | WEAK` 证据强度；
- 不设置单一 Observation 总置信分；
- `WEAK` 事实不能单独成为用户可见 Memory Claim；
- Window 内变化至少引用两个有序 Frame，不推断未拍到的连续过程；
- S04 不生成长 Caption，不判断重要性、Chapter、Aha、情绪、关系、意图或意义；
- `INSUFFICIENT_EVIDENCE` 不补帧、不上传完整 Auto 9s；
- `FAILED` 与证据不足严格区分。

### OPEN / Benchmark 校准

- Production JSON Schema 的字段命名与最大数组长度；
- Scene / Activity taxonomy 的后续版本；
- support grade 的模型提示、校准与一致性；
- `OBSERVED` / `PARTIAL` / `INSUFFICIENT_EVIDENCE` 的实测判定门；
- 模型、图片分辨率、batch、token、并发、timeout 与 retry；
- 多语言原子事实规范；
- S08 对 `MODERATE` 事实的补充验证规则。

## 12. 当前实现 GAP

- 当前仓库尚无符合本合同的 Production Observation Lite schema、runner 或 Validator；
- 当前 X01 的 `observed_facts + uncertainty + confidence` 是隔离实验合同，不等于本检查点；
- 尚未实现逐事实 Frame grounding、support grade、状态机、batch isolation 与 exact-cache provenance；
- 尚未使用真实 wearable 数据校准状态和证据强度；
- 本检查点只冻结 S04 输出，不实现或冻结 S05 Moment Formation 算法。
