# S08 Targeted Enrichment & Evidence Validation — Consolidated Working V0.1

**状态：** REVIEW COMPLETE / BASIS FOR FROZEN V1.18
**日期：** 2026-08-26
**作用范围：** S08 验证任务、问题类型、动作选择、证据范围、加权预算、缓存、重试、失败归因、Revision、输出合同与 S09 handoff
**继承关系：** 继承 V1.17–V1.1 与 V1.0 未被本文覆盖的规则
**明确不覆盖：** S09 最终集合选择、S10 最终媒体、S11 Narrative、S12 最终 Claim Validation、App 后台上传工程、Firmware/SDK、共享状态文件、16s/73s 等非标准 Manual Window
**当前下游：** S09 已由 [Canonical Checkpoint V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md) 冻结；本文的 S08 合同继续有效

## 1. S08 在全链路中的位置

~~~text
S07 PROVISIONAL_VALIDATION_REQUIRED Candidate
→ one-question ValidationTask
→ cheapest capable bounded action
→ PASS / FAIL / INCONCLUSIVE
   or operational NOT_EVALUATED
→ independent S08 outcome
→ only validated downstream eligibility enters S09
~~~

S08 只回答一个已经被 S07 定义清楚的局部问题。它不是第二次 S07，也不是让强模型重新理解全天。

S08 不负责：

- 判断一件事是否值得记住；Memory Value 已由 S07 判断；
- 从全天素材中发现新 Chapter/Aha；
- 改写 S04 fact、S05 Moment、S06 role 或 S07 Candidate；
- 决定全天最终 3–4 个 Chapter 或 2–3 个 Aha；
- 选择最漂亮的照片、hero、LIVE_2S 或最终剪辑；
- 写 title、story、tag 或用户情绪；
- 补取 Auto UPLOAD_1 的另外两帧或完整 9 秒 Raw；
- 默认请求完整 Manual Raw。

**案例：** S07 已确认“吹生日蜡烛”具有独立记忆价值，但现有帧还不能确定火焰是否真的熄灭。S08 只验证“火焰是否从点燃变为熄灭”，不能顺便重新判断整场生日是否值得成为 Chapter。

## 2. 核心对象与双轴结果

### 2.1 ValidationTask

一个 ValidationTask 只回答一个可以被证据支持或反驳的具体问题。

一个 Candidate 如果有两个彼此独立的未知项，必须拆成两个任务。V1 每个 Candidate 最多允许两个必要 ValidationTask；超过两个表示它不是“局部补证”，而是在请求重新理解，S08 将其视为 handoff contract invalid。

**案例：** “是否回到了同一片古镇区域”和“长视频是否包含三个不同内容位置”是两个问题，不能放进一句 Prompt 让模型自由总结。

### 2.2 ExecutionStatus

任务最终执行状态只有：

~~~text
COMPLETED
NOT_RUN_BUDGET
NOT_RUN_POLICY
PROVIDER_FAILED
CONTRACT_INVALID
~~~

- COMPLETED：本地规则或模型正常完成，并得到合法结构化结果；
- NOT_RUN_BUDGET：VBU、真实成本或月度 headroom 不允许启动；
- NOT_RUN_POLICY：数据许可、speech gate、provider data policy 或 exposure policy 不允许启动；
- PROVIDER_FAILED：允许的同级尝试用尽，仍没有合法响应；
- CONTRACT_INVALID：输入、引用、问题、范围或输出合同不合法。

### 2.3 EvidenceDecision

证据结论只有：

~~~text
PASS
FAIL
INCONCLUSIVE
NOT_EVALUATED
~~~

合法组合：

| ExecutionStatus | 合法 EvidenceDecision |
|---|---|
| COMPLETED | PASS / FAIL / INCONCLUSIVE |
| NOT_RUN_BUDGET | NOT_EVALUATED |
| NOT_RUN_POLICY | NOT_EVALUATED |
| PROVIDER_FAILED | NOT_EVALUATED |
| CONTRACT_INVALID | NOT_EVALUATED |

服务失败、预算不足、政策未授权和合同错误都不是内容失败。

**案例：** 模型 API 超时两次时，结果是 PROVIDER_FAILED + NOT_EVALUATED，而不是“吹蜡烛没有发生”。

## 3. 输入与 admission

S08 输入至少包括：

- immutable revision_id 与 snapshot_id；
- S07 candidate_instance_id 与 candidate fingerprint；
- Candidate disposition = PROVISIONAL_VALIDATION_REQUIRED；
- target gate；
- 一个明确 unknown 或 contradiction；
- current grounded support；
- allowed Evidence、modality 与 time scope；
- explicitly disallowed source/refetch；
- PASS/FAIL 对下游资格或 alternative resolution 的明确映射；
- expected action/cost class；
- schema、rule、model-policy 与 budget-policy versions。

只有以下四类问题可以进入 V1 S08：

~~~text
LOCAL_PEAK_CONFIRMATION
EPISODE_RELATION_CONFIRMATION
MEDIA_DIVERSITY_CONFIRMATION
ALTERNATIVE_RESOLUTION
~~~

ELIGIBLE、REJECTED、SUPPRESSED_DUPLICATE Candidate 不进入 S08。

**案例：** 一个普通通勤 Candidate 已经 ELIGIBLE，它直接进入 S09 pool；不能为了“更放心”再调用一次视觉模型。

## 4. 四类允许问题

### 4.1 LOCAL_PEAK_CONFIRMATION

范围必须保持在一个 origin Moment、一个 KEEP peak，以及最多 3 个连续 eligible Windows / 3 分钟。

允许确认具体可观察变化、动作或局部事实；不允许重新判断 Memory Value。

**案例：** 确认生日蜡烛是否真的熄灭。若火焰在所有允许帧中都被遮挡，结果为 INCONCLUSIVE，而不是扩大到整段视频。

### 4.2 EPISODE_RELATION_CONFIRMATION

只可使用 Candidate content members、interruption/context refs 与已有 Continuity/Boundary ledgers。不得做全天搜索，也不得重写 S05 seam。

**案例：** 古镇步行 A、奶茶店 B、继续古镇步行 C。S08 可以确认 A 与 C 是否有同一局部 outing 的恢复证据，但不能把全天所有古建筑素材重新聚成一个主题。

### 4.3 MEDIA_DIVERSITY_CONFIRMATION

只验证指定 Long-Manual Windows 是否真的是时间和语义上不同的内容位置。它不评价美感，也不选择最终媒体。

**案例：** 120 秒家庭表演视频中的“准备、表演、鼓掌”若分别有不同 grounded fact 和非重复 Window，可以 PASS；三个几乎相同的舞台站立画面应 FAIL。

### 4.4 ALTERNATIVE_RESOLUTION

只处理一个 local alternative group 中预先声明的一个关系或 dominance 问题。一个任务最多直接比较两个 Candidate member；更大的 group 必须拆成有界任务。

允许的标准化 resolution：

~~~text
MEMBER_A_DOMINATES
MEMBER_B_DOMINATES
BOTH_DISTINCT
UNRESOLVED
~~~

**案例：** “古镇步行”与“古镇步行 + 奶茶店 + 寺庙”两个候选之间，只验证后者是否增加实质记忆内容，不能让模型顺便评选全天最佳 Chapter。

## 5. 共同证据边界

- KEEP 可以支持肯定事实；
- CONTEXT_ONLY 只能限制解释或说明 interruption，不能新增 Candidate 内容；
- DROP 只能出现在 audit/provenance，不能被 S08 恢复；
- 所有媒体输入必须由 ValidationTask 显式列出；
- 证据不足时返回 INCONCLUSIVE；
- 不允许通过追加 Raw、补帧或全日检索解决不确定；
- Aha 的 origin、peak 和 interval 不得被验证结果扩大；
- S08 产生的是 validation finding，不是新的 S04 fact。

**案例：** 奶茶店 B 是 CONTEXT_ONLY 时，它可以说明古镇路线中发生过一次室内中断，但不能因此成为 Chapter 的第四个精选内容单元。

## 6. 最低充分能力选择树

这不是所有 Candidate 都顺序跑完的线性阶梯。统一起点只有 A0 → A1；之后根据问题选择一个最便宜且有能力回答的分支。

### A0｜EXACT_VALIDATION_CACHE

完全相同的任务、证据、动作与版本可以复用已有合法结果，不调用模型。

**案例：** Preview 已验证同一 120 秒 Manual 的三个 Window；Final 的 evidence hash、问题与版本完全相同，直接复用 payload，再为 Final Revision 创建新的 outcome wrapper。

### A1｜STRUCTURED_EVIDENCE_CHECK

使用已有时间、grounded facts、duplicate groups、content units、Continuity/Boundary ledgers 与 Candidate relation 做专用确定性验证。

A1 不是重跑 S07。它只执行当前 question type 的严格 Validator。

**案例：** Long-Manual 三个 Window 已分别绑定“准备乐器、演奏、观众鼓掌”，时间区间不同且不在 duplicate group，MEDIA_DIVERSITY 可以由 A1 直接 PASS。

### A2-V｜TARGETED_LIGHTWEIGHT_VISION

只对允许范围内最多 3 张现有 Evidence frame 提一个封闭视觉问题。

**案例：** 输入吹蜡烛前、中、后三帧，只问火焰是否从可见点燃变成可见熄灭。

### A2-T｜EXISTING_TEMPORAL_PROXY

只有动作顺序是必要证据、静态帧不足，而且当前合同中已经存在允许使用的低分辨率 temporal proxy 时才能选择。

每个任务最多使用 2 个局部 proxy excerpt、总时长不超过 6 秒；S08 不从完整 Raw 新生成 proxy。

**案例：** 三张帧无法判断球是接住还是扔出，但现有 2 秒低分辨率 proxy 可以显示动作方向，因此选择 A2-T。

### A2-A｜GATED_AUDIO_OR_ASR

只有声音本身是 Candidate 成立的必要事实，同时 speech gate 与数据许可通过时才使用。每个任务只允许一个局部 audio excerpt，总时长不超过 15 秒。

audio excerpt 必须已经存在于当前允许的 Evidence package，或者已经由上游合法准备；S08 不得回取完整 Manual Raw 再临时切出音频。

**案例：** “孩子第一次说出妈妈”的 Aha 依赖实际发声，可以使用局部 ASR；普通喝咖啡 Chapter 只是想写更丰富文案时不得启动 ASR。

### A3｜BOUNDED_STRONG_MODEL

只有前一级动作正常完成、却因 capability limit 无法判断，而且结果会改变下游资格时才允许升级。A3 使用与前一级完全相同或更小的 Evidence payload，不得增加 Raw、Frame、Proxy 或 Audio。

**案例：** 轻量模型无法判断 A/C 是否回到同一古镇局部路线，强模型可以检查已有招牌、地标、顺序和 ledgers，但不能查看新的素材。

### STOP｜INCONCLUSIVE

最强允许动作仍不能判断，或者源证据缺失、遮挡、超出政策范围时停止。

**案例：** 吹蜡烛关键时刻完全被人挡住。系统宁可错过该 Aha，也不能根据生日场景猜测蜡烛已经熄灭。

## 7. 能力升级与问题路由

默认路由：

| QuestionType | 首选 | 允许升级 |
|---|---|---|
| LOCAL_PEAK_CONFIRMATION | A1 → A2-V | 动作必需时 A2-T；声音必需时 A2-A；复杂但证据存在时 A3 |
| EPISODE_RELATION_CONFIRMATION | A1 | 必要时 A2-V；极少 A3 |
| MEDIA_DIVERSITY_CONFIRMATION | A1 | 必要时 A2-V；已有动态证据且动作差异必要时 A2-T |
| ALTERNATIVE_RESOLUTION | A1 | 必要时 A2-V；复杂局部语义时 A3 |

每个任务最多两个 paid capability step。A0/A1 不计入 paid step；A3 一定是最后一步。

只有以下 INCONCLUSIVE reason 可以申请能力升级：

~~~text
CAPABILITY_LIMIT
MODALITY_MISMATCH_WITHIN_ALLOWED_SCOPE
~~~

以下 reason 必须直接 STOP：

~~~text
SOURCE_EVIDENCE_ABSENT_OR_OCCLUDED
POLICY_SCOPE_LIMIT
NO_ALLOWED_MODALITY
CONTRADICTION_NOT_RESOLVABLE
~~~

**案例：** 模型能看见路牌但无法理解两个别名是否指向同一区域，属于 CAPABILITY_LIMIT；关键路牌根本没拍到，属于 SOURCE_EVIDENCE_ABSENT，不能升级强模型。

## 8. Evidence exposure envelope

媒体暴露和算力成本分别记录，不能用一个分数互相抵消。

| Action | 最大媒体范围 | 默认暴露等级 |
|---|---|---|
| A0/A1 | 无新增第三方媒体 | E0 |
| A2-V | 最多 3 张现有 Evidence frame | E1 |
| A2-T | 最多 2 个现有低分辨率 excerpt，总计不超过 6 秒 | E2 |
| A2-A | 一个局部 audio excerpt，不超过 15 秒 | E2-AUDIO |
| A3 | 与前一步相同或更小，不得扩大 | 保持原等级，另记 strong exposure event |

跨 provider fallback 只有在数据政策等价或更严格、并且当前 payload 获得授权时才允许。

**案例：** A2-V 已把三张生日帧发给供应商 A。供应商 A 故障时，只有供应商 B 满足相同数据政策才可同级 fallback；不能因为 B 可用就附带发送完整生日视频。

## 9. S08-D｜加权预算

### 9.1 为什么不能只数 Candidate

Preview 3 / Final 8 只限制 provisional Candidate 数量。一个 Candidate 可能有两个任务、一次强模型升级和一次失败重试，因此还必须限制 action weight。

**案例：** 三个 Preview Candidate 如果每个都跑轻量视觉、时序、ASR、强模型和重试，Candidate 数仍是 3，但成本已经失控。

### 9.2 Validation Budget Unit

V1 使用相对单位 VBU。1 VBU 表示一次限定范围的 A2-V 轻量视觉尝试的规划重量，不等于固定美元或固定 Token。

| Action attempt | 最低 VBU |
|---|---:|
| A0 exact cache | 0 |
| A1 structured check | 0 |
| A2-V lightweight vision | 1 |
| A2-A gated audio/ASR | 1 |
| A2-T temporal proxy | 2 |
| A3 bounded strong model | 4 |

实际 reservation 使用：

~~~text
reserved_vbu =
max(
  action_min_vbu,
  ceil(projected_action_cost / versioned_reference_light_call_cost)
)
~~~

因此供应商价格改变时，强模型不会因为静态表格而被低估。每次真实 dispatch 都消耗 VBU；provider retry 也消耗，不把 retry waste 隐藏掉。

**案例：** 某个 temporal provider 的预计价格相当于 3 次 reference light call，即使表中最低为 2，实际也必须预留 3 VBU。

### 9.3 V1.18 versioned budget baseline

| 范围 | 上限 |
|---|---:|
| Necessary ValidationTask / Candidate | 2 |
| Paid capability step / Task | 2 |
| Provider attempt / capability step | 2，包括首次与一次同级 retry/fallback |
| Reserved + consumed dispatch VBU / Task | 6 |
| Reserved + consumed dispatch VBU / Candidate | 8 |
| 所有 Preview Revisions 合计 / diary day | 4 |
| S08 全部 Revisions 合计 / diary day | 16 |
| 启动 A3 的 Task / diary day | 2 |

Preview 的 4 VBU 是全天累计池，不是每次打开 App 都重新获得 4 VBU。Final 使用当天剩余 VBU；如果当天没有 Preview，Final 最多可使用完整 16 VBU。

这里的上限是可校准 Baseline，不是模型价格或质量真理。

**案例：** 用户一天打开 App 四次并产生四个 Preview。四次 Preview 合计仍只有 4 VBU；同一个问题命中 exact cache 时为 0，不会因打开次数翻四倍收费。

### 9.4 多任务 Candidate 的原子最低预留

若一个 Candidate 有两个必要任务，启动第一个 paid action 前，必须能够同时预留两个任务各自最便宜可用首步的总 VBU。不能明知第二个任务无预算，仍先花钱完成第一个。

强模型升级不需要预先永久占用，但必须在升级前重新 reservation。

**案例：** 一个 Chapter 同时需要 relation 与 media diversity 两个任务，两者最低各需 1 VBU。如果只剩 1 VBU，则两个任务都不启动，Candidate 记为 NOT_RUN_BUDGET，避免半验证浪费。

### 9.5 月度美元 guardrail

VBU 只保证结构有界，不能代替真实价格。每次 paid dispatch 还必须通过 Model Gateway 的真实成本 reservation：

- 记录 provider 原币价格、换算版本、预计与实际美元；
- 纳入 Perception、Enrichment、ASR、Validation、Strong escalation、Retry waste 分账；
- 服从 cohort average 每用户每月不超过 US$1.50 的总 guardrail；
- 工程目标约 US$0.90，内部预警约 US$1.20；
- S08 的月度份额和 reference-light 单价由真实 Benchmark 配置，不在架构中伪造固定比例。

若当前 action 没有可信的版本化价格或保守费用上界，则不能发送 paid request，结果按 NOT_RUN_BUDGET + NOT_EVALUATED 记录，并注明 PRICE_UNAVAILABLE。

预算压力下降级顺序：

1. A0/A1 始终可运行；
2. 达到内部预警预测时，停止新的 Preview paid action 与新的 A3；
3. Final 只按 decision yield 运行最便宜的 A2；
4. 总 guardrail 没有 headroom 时，只保留 A0/A1，其余 NOT_RUN_BUDGET；
5. 预算不足绝不改写为 Evidence FAIL。

**案例：** 月度预测已到 US$1.20 预警线时，一个古镇 Preview 不再启动强模型；Final 仍可用 1 VBU 的局部视觉验证解决一个高决策收益问题。

## 10. 预算内调度

顺序：

1. 对 frontier 内所有合法任务先运行 A0/A1；
2. 已 PASS、FAIL 或 terminal INCONCLUSIVE 的任务不再付费；
3. 为仍需付费的 Candidate 建立 atomic minimum reservation bundle；
4. 按 decision yield 排序；
5. 逐次 dispatch，调用前再次检查 revision、budget、exposure 与 provider policy；
6. 达到任一上限立即停止，保留 audit。

decision yield 只衡量“这次验证能解决多少个明确 gate / Candidate”，不评价哪个 Memory 更感人，也不替代 S09。

排序键：

~~~text
shared_candidate_count_resolved DESC
mandatory_gate_count_resolved DESC
minimum_reserved_vbu ASC
stable_task_fingerprint ASC
~~~

**案例：** 一个 1 VBU 的 shared alternative task 能同时解决两个 Candidate，而另一个 2 VBU 任务只解决一个 Candidate；前者先运行，但这不表示它最终一定被 S09 选中。

## 11. S08-E｜精确缓存与幂等

### 11.1 两层 fingerprint

ValidationTask semantic fingerprint 至少包含：

- normalized question type 与 proposition；
- target gate；
- PASS/FAIL mapping；
- candidate content fingerprint；
- ordered Evidence content hashes、time offsets 与 role；
- allowed modality/time scope 与 disallowed source；
- rule/taxonomy/policy versions。

Action execution fingerprint 另外包含：

- chosen action；
- 实际 frame/proxy/audio hashes 与 preprocessing version；
- provider capability tier；
- model、prompt、parameter、schema versions；
- exposure-policy version。

价格配置只参与当前预算 reservation 与 attempt trace，不参与语义 payload 的 cache identity；单纯价格变化不能让已经完成的 PASS/FAIL/INCONCLUSIVE 失效。

candidate_instance_id 和 revision_id 不作为跨 Revision payload cache identity，但当前 Revision 必须重新验证 eligibility，并创建新的 task/outcome wrapper。

**案例：** Preview 与 Final 的 Candidate instance ID 不同，但内容、问题、Evidence 与版本完全相同，可以复用模型 payload；Final 仍生成自己的 outcome，不能把 Preview ID 当成 Final ID。

### 11.2 哪些结果可缓存

- PASS、FAIL、INCONCLUSIVE 的合法 COMPLETED payload 可以 exact-cache；
- 同级 INCONCLUSIVE 命中缓存后，可以直接判断是否允许下一能力层，不重复调用原层；
- PROVIDER_FAILED 不作为语义结果缓存；
- CONTRACT_INVALID 输入必须修复后形成新 fingerprint；
- near-duplicate、相似场景或相同自然语言问题都不能代替 exact match。

**案例：** 两段石板路画面很相似，但 Evidence hash 和 capture time 不同，不能复制“同一古镇路线恢复”的旧验证结论。

### 11.3 at-least-once queue

每个 dispatch 使用：

~~~text
idempotency_key =
task_id + action_execution_fingerprint + capability_step_index + attempt_index
~~~

重复队列投递必须先检查已提交 attempt，不能产生第二笔模型调用。

**案例：** Worker 在写入成功后网络断开，队列重复投递同一任务。系统返回已保存 attempt，而不是再次把三张家庭照片发给模型。

## 12. 重试、fallback 与失败归因

### 12.1 Provider failure

transport error、timeout、rate limit、provider unavailable 等属于 Provider failure：

- 同一 capability step 最多两次 provider attempt；
- 第二次可以是同 provider retry 或满足数据政策的 same-tier fallback；
- 第二次 attempt 仍必须同时满足 task、candidate、Preview/day、月度美元与 exposure cap；
- 每次 dispatch 都消耗 VBU、记录 latency/cost/exposure；
- 不允许因此升级 A3；
- 尝试用尽后为 PROVIDER_FAILED + NOT_EVALUATED。

**案例：** 轻量视觉供应商超时后，可以切换另一个同级轻量视觉供应商；不能自动改用强模型并称为“提高准确率”。

### 12.2 Invalid structured output

模型返回无法解析的 schema、未知 Evidence ID 或越权引用时：

- 当前 attempt 记录 output contract failure；
- 若仍有同级 attempt 与预算，可重试一次；
- 仍不合法则 CONTRACT_INVALID + NOT_EVALUATED；
- 不接受自由文本猜测，也不升级强模型。

**案例：** 模型回答蜡烛已熄灭，但引用了任务未提供的 frame_id，结果无效；不能因为文字听起来合理就 PASS。

### 12.3 Semantic inability

模型正常返回合法结果，但明确表示当前能力无法在现有证据中区分，才属于 semantic inability。

- CAPABILITY_LIMIT 或允许范围内的 MODALITY_MISMATCH 可以升级一次；
- 源证据缺失、遮挡、政策限制不能升级；
- 同一层不做多数投票式重复调用；
- A3 后仍不确定则 COMPLETED + INCONCLUSIVE。

**案例：** 轻量模型看见两块不同文字的路牌但无法判断别名关系，可以升级；画面里根本没有路牌时不能升级。

### 12.4 Candidate short-circuit

必要任务按最低成本和最大失败信息量排序：

- 任一必要任务 FAIL，Candidate 立即 REJECTED_BY_EVIDENCE；
- 任一任务 terminal INCONCLUSIVE 或 operational failure 后，其余未启动 paid task 停止，记录 SHORT_CIRCUITED_NO_ELIGIBILITY；
- free A0/A1 可以预先完成并缓存；
- 未启动任务没有伪造 TaskOutcome，只保留 plan disposition。

**案例：** Long-Manual 的第一个必要 media-diversity 任务已经 FAIL，就不再花钱验证它与另一个 Candidate 的 dominance。

## 13. Revision、并发与迟到结果

- 每个 ValidationTask 只属于一个 immutable Revision/snapshot；
- paid dispatch 前再次检查该 Revision 是否仍可用于当前 downstream；
- 新素材或 Late Data 创建新 Revision，不修改旧任务；
- 旧 Revision 的运行结果照常保存，但标记 revision_applicability = STALE_FOR_CURRENT_DOWNSTREAM；
- stale result 不能直接进入当前 S09；
- 新 Revision 只有在 exact fingerprint 成立时才复用 payload，并创建新 wrapper；
- spend、retry waste 与 exposure 永远记在实际发生的原 Revision/day；
- S08 不回写 S07 Candidate disposition。

**案例：** Preview R2 的强模型在 Final R3 创建后才返回 PASS。R2 结果保留为审计；R3 若 Evidence 完全相同可 exact-cache 复用，否则必须重新计划。

## 14. S08-F｜输出合同

### 14.1 ValidationPlan

至少包含：

~~~text
revision_id
snapshot_id
policy_versions
frontier_candidate_refs[]
validation_tasks[]
schedule_order[]
budget_snapshot_before
budget_reservations[]
plan_dispositions[]
~~~

### 14.2 ValidationTask

至少包含：

~~~text
task_id
revision_id / snapshot_id
candidate_instance_refs[]
candidate_content_fingerprints[]
question_type
target_gate
normalized_proposition
current_grounded_support_refs[]
allowed_evidence_refs[]
allowed_modality / time_scope
explicitly_disallowed_sources[]
pass_mapping
fail_mapping
minimum_action_route
semantic_fingerprint
versions
~~~

### 14.3 ValidationAttempt

至少包含：

~~~text
attempt_id / idempotency_key
task_id
capability_step_index / attempt_index
action
provider / model / capability_tier
actual_input_hashes[]
exposure_class / media_count / bytes / duration
started_at / ended_at / latency
request_status / failure_attribution
input_tokens / output_tokens
projected_cost / actual_cost / currency / conversion_version
reserved_vbu / consumed_vbu
exact_cache_provenance
structured_payload_ref
~~~

### 14.4 ValidationTaskOutcome

至少包含：

~~~text
task_outcome_id
task_id
execution_status
evidence_decision
decision_reason
validated_assertion
supporting_evidence_refs[]
contradicting_evidence_refs[]
inconclusive_reason
completed_action
attempt_refs[]
revision_applicability
created_at
~~~

validated_assertion 只能回答 normalized proposition，不能带入旁支故事。

### 14.5 CandidateValidationOutcome

~~~text
VALIDATED_FOR_S09
REJECTED_BY_EVIDENCE
UNRESOLVED_EVIDENCE
UNVALIDATED_OPERATIONAL
STALE_FOR_CURRENT_REVISION
~~~

聚合规则：

1. 任一必要 task COMPLETED + FAIL → REJECTED_BY_EVIDENCE；
2. 所有必要 task COMPLETED + PASS → VALIDATED_FOR_S09；
3. 无 FAIL，但存在 COMPLETED + INCONCLUSIVE → UNRESOLVED_EVIDENCE；
4. 无 FAIL，但存在 NOT_RUN_BUDGET、NOT_RUN_POLICY、PROVIDER_FAILED 或 CONTRACT_INVALID → UNVALIDATED_OPERATIONAL；
5. Revision 不再适用 → STALE_FOR_CURRENT_REVISION。

只有第一条是 Evidence 否定；第四条绝不能被统计为内容质量失败。

**案例：** 两个必要任务中，一个 PASS、一个 API 故障，则 Candidate 是 UNVALIDATED_OPERATIONAL，不是 REJECTED_BY_EVIDENCE。

### 14.6 ValidatedCandidate

只在所有必要 task PASS 时生成：

~~~text
validated_candidate_id
source_candidate_instance_id
source_candidate_fingerprint
revision_id / snapshot_id
passed_task_outcome_refs[]
validation_findings[]
downstream_eligibility = ELIGIBLE_FOR_S09
content_identity_unchanged = true
~~~

ValidatedCandidate 是原 S07 Candidate 的下游资格 wrapper，不复制或改写 content units、Moment membership、Evidence role。

**案例：** 长 Manual 通过 media diversity 后，S08 只附加“可进入 S09”的资格；不能把三个 Window 擅自改成四个精选素材。

### 14.7 AlternativeResolution

至少包含：

~~~text
alternative_resolution_id
alternative_group_id
member_candidate_refs[]
resolution
supporting_task_outcome_refs[]
revision_id / snapshot_id
downstream_constraints
~~~

它不删除 Candidate；S09 根据 resolution 和其他 gate 决定哪些 member 仍可选。

ValidationTask 的 pass_mapping 与 fail_mapping 必须逐 member 声明 CandidateValidationOutcome。一个 proposition 为 FAIL 不代表所有 alternative member 都失败；它可能使一个 member 被证据否定，同时使另一个 member 的该 gate 成立。只有各自所有必要 task 都 PASS 的 member 才生成 ValidatedCandidate。

**案例：** A_DOMINATES_B 只告诉 S09：B 没有新增实质内容。S08 不直接发布 A，也不删除 B 的历史 audit。

### 14.8 S08RunTrace

至少记录：

- frontier count、合法/非法 request count；
- task count by question type；
- A0/A1 resolution rate；
- paid action、capability escalation 与 A3 count；
- PASS/FAIL/INCONCLUSIVE/NOT_EVALUATED；
- provider failure、contract invalid、retry/fallback；
- exact cache hit 与跨 Revision reuse；
- planned/consumed VBU by Preview/Final/day；
- actual cost、Token、media bytes/duration 与 exposure events；
- budget/short-circuit/cap stop；
- latency 与 stale result count。

**案例：** 不能只报告“今天验证了 5 个 Candidate”；还要能看出其中 3 个是 A1 零模型解决、1 个轻量视觉、1 个预算未运行。

## 15. S09 handoff

S09 输入中的可选 Candidate pool 由两部分组成：

~~~text
S07 ELIGIBLE Candidates
+
S08 ValidatedCandidates
~~~

并附带：

- AlternativeResolution；
- rejected/unresolved/operational/stale audit；
- validation findings 与 evidence refs；
- S08 cost/exposure trace。

S09 不得把 UNRESOLVED、UNVALIDATED_OPERATIONAL 或 STALE Candidate 当作已验证对象。

**案例：** 一个生日 Aha 因遮挡 INCONCLUSIVE 时，即使 S09 当天缺少第三个 Aha，也不能拿它补足数量。

## 16. Validator 不变量

提交 S08 输出前至少验证：

1. 所有 task 只引用同一 Revision/snapshot 的合法 S07 provisional Candidate；
2. 每个 task 只有一个 question type、一个 proposition 与一个 target gate；
3. 每个 Candidate 不超过两个必要 task；
4. 只使用四类允许问题；
5. KEEP、CONTEXT_ONLY、DROP 的使用没有越界；
6. 所有 Evidence 都在 allowlist，且没有 Auto refetch 或默认 Raw request；
7. A2-V 不超过 3 帧；
8. A2-T 只使用已有 proxy，最多 2 个、总计不超过 6 秒；
9. A2-A 通过 speech/data gate，且 audio 不超过 15 秒；
10. A3 没有扩大 Evidence payload；
11. Provider failure 没有触发强模型升级；
12. 只有允许的 semantic inability reason 触发能力升级；
13. 每个 task paid capability step 不超过 2，A3 为最后一步；
14. 所有 dispatch 在调用前完成 VBU、美元与 exposure reservation；
15. Preview 全天累计、全日累计、task/candidate 与 A3 cap 均未超限；
16. retry/fallback 消耗与失败浪费已记录；
17. exact cache key 包含完整 Evidence/action/version fingerprint；
18. 跨 Revision reuse 创建当前 wrapper，没有复用旧 instance identity；
19. ExecutionStatus 与 EvidenceDecision 组合合法；
20. budget/policy/provider/contract failure 没有变成 Evidence FAIL；
21. ValidatedCandidate 的所有必要 task 均 PASS；
22. ValidatedCandidate content identity 与原 S07 Candidate 完全一致；
23. AlternativeResolution 没有删除或改写 S07 Candidate；
24. stale result 没有进入当前 S09；
25. S08 没有生成 Narrative、最终媒体或新 Memory Value；
26. same input、policy 与 versions 可以确定性重放 schedule/cache 决策。

## 17. 质量、成本与失败指标

真实数据阶段至少分开评估：

### Quality

- validation precision / false-pass rate；
- false-fail rate；
- INCONCLUSIVE rate 与原因分布；
- S09 eligibility lift；
- alternative resolution accuracy；
- Long-Manual diversity precision；
- local peak temporal hit。

### Efficiency

- A0/A1 resolution rate；
- VBU / resolved gate；
- paid attempts / validated Candidate；
- A3 rate；
- exact-cache reuse rate；
- Preview→Final incremental cost；
- provider retry waste。

### Coverage and exposure

- NOT_RUN_BUDGET / NOT_RUN_POLICY rate；
- budget truncation regret；
- media frame/proxy/audio exposure；
- cross-provider exposure；
- stale result rate；
- user/profile-level validation availability。

**案例：** A0/A1 resolution rate 很高但 false-pass 也高，不能只因为便宜就宣布成功；必须同时检查真实标注下的错误通过率。

## 18. 状态边界

### Proposed FROZEN after cross-check

- one-task-one-question 与双轴结果；
- 四类允许 ValidationQuestion；
- 最低充分能力选择树；
- Provider failure 同级 fallback、semantic inability 才能升级；
- Evidence exposure envelope 与 no-refetch/no-default-Raw；
- VBU 权重、task/candidate/Preview/day/A3 有界 Baseline；
- exact cache、at-least-once 幂等、Revision/stale 规则；
- independent ValidatedCandidate/AlternativeResolution；
- S08 不回写上游、不替代 S09/S10/S11/S12。

### OPEN / 待真实数据或后续工程

- provider/model 选择与动态价格；
- reference-light 单价与 S08 月度实际份额；
- VBU 4/16、task 6、candidate 8、A3/day=2 的质量成本校准；
- 3 frame、6s proxy、15s audio envelope 的召回损失；
- 具体 prompt、schema、timeout、backoff 时间与 provider fallback 顺序；
- 真实 speech permission/data-policy 产品实现；
- 真实 Long-Manual diversity、relation 与 local peak 模型；
- Production JSON Schema、runner、persistent cache、queue 与 Validator；
- 16s/73s 等非标准 Manual Window；
- S09 set selection 与最终数量。

OPEN 意味着通过 Benchmark 显式重开参数，不意味着实现可以静默改变语义。

### IMPLEMENTATION GAP

- 当前 X01 仍是一轮多模态模型调用，不是分阶段 S08；
- 当前没有 Production ValidationTask schema、budget service、router、cache 或 outcome aggregator；
- 当前没有真实用户标注证明四类 Validator 的 precision/recall；
- 本文是算法架构工作合同，不是 Production readiness 声明。
