# S08 Cross-Check and Semantic Timeline Simulation V0.1

**状态：** REVIEW COMPLETE / SUPPORTS V1.18 FREEZE
**日期：** 2026-08-26
**被测合同：** [S08 Targeted Enrichment & Evidence Validation — Consolidated Working V0.1](S08_TARGETED_ENRICHMENT_VALIDATION_CONSOLIDATED_WORKING_V0_1.md)
**冻结结果：** 当前权威规则见 [Canonical Checkpoint V1.18](CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md)
**当前下游：** S09 已由 [Canonical Checkpoint V1.19](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md) 冻结
**作用范围：** S08 问题、动作、证据、预算、缓存、失败、Revision、输出与 S09 handoff 的结构检查和高概率用户语义时间轴模拟
**明确不覆盖：** 真实视觉/音频准确率、真实用户评分、真实 provider 价格、真实网络、App、Firmware/SDK、共享状态文件、S09–S13 详细算法、非标准 Manual Window

## 1. 这次检查回答什么

本报告只回答：

1. S08 是否仍然只做局部验证，没有重新变成全日理解；
2. Preview 3 / Final 8 的 Candidate count 之外，动作、重试、强模型和多次 Preview 是否真正有界；
3. Provider failure、证据失败和不确定是否被正确区分；
4. Preview→Final、Late Data 和并发结果是否会污染 Revision；
5. 不同生活日型能否得到合理且可解释的验证路径。

这是语义合同模拟，不运行图片、视频、音频或付费模型。PASS 表示架构内部一致，不表示真实准确率已经达标。

## 2. 交叉检查发现与修正

| Finding | 风险 | V0.1 最终修正 | 状态 |
|---|---|---|---|
| F1：把动作写成固定线性阶梯 | 每个 Candidate 都可能重复跑视觉、时序、音频和强模型 | 只有 A0→A1 是共同起点，之后选择一个最低充分模态；最多一次能力升级 | FIXED |
| F2：只使用 Preview 3 / Final 8 count | 候选数少但调用、重试和 Token 仍可能爆炸 | 增加 VBU、task/candidate/day/A3 cap，所有 dispatch 和 retry 都消耗预算 | FIXED |
| F3：把 Preview budget 当成每个 Revision 的额度 | 用户多次打开 App 会线性放大花费 | Preview 4 VBU 是同一 diary day 所有 Preview 的累计池 | FIXED |
| F4：多任务 Candidate 逐个试跑 | 可能明知无法完成第二任务仍浪费第一个任务成本 | paid action 前执行 atomic minimum reservation | FIXED |
| F5：把价格配置写进语义 cache key | 单纯价格变化会让正确结果无意义失效并重复调用 | price config 只参与新 dispatch reservation/trace，不参与 semantic payload identity | FIXED |
| F6：cache key 直接依赖 Revision instance ID | Preview→Final 无法复用 | semantic/action fingerprint 与 Revision wrapper 分离；当前 Revision 重新绑定 | FIXED |
| F7：Provider failure 与 Evidence FAIL 混用 | 服务故障会误删真实 Memory | ExecutionStatus 与 EvidenceDecision 双轴；Operational failure 只能 NOT_EVALUATED | FIXED |
| F8：强模型升级顺便扩大输入 | 局部验证会重新变成 Raw/全天理解 | A3 使用相同或更小 payload；no-refetch/no-default-Raw 保持 | FIXED |
| F9：Alternative 的 PASS/FAIL 没有逐 member 映射 | 一个 proposition 的真假可能误伤整个 alternative group | pass_mapping/fail_mapping 必须逐 member 产生 Candidate outcome | FIXED |
| F10：音频/时序 action 暗中要求回取 Raw | 违反既有上传合同 | proxy/audio 必须已存在且已获允许；S08 不回取 Raw 临时生成 | FIXED |
| F11：未知 provider 价格仍可发送 | VBU 静态权重无法保证美元成本 | 无可信价格或保守上界时 NOT_RUN_BUDGET / PRICE_UNAVAILABLE | FIXED |
| F12：迟到结果自动挂到最新 Revision | 旧快照事实可能污染新结果 | 保存旧 outcome，标 STALE；新 Revision 仅 exact payload reuse 后创建新 wrapper | FIXED |
| F13：四个 execution status 无法准确表达数据许可未通过 | 塞进 budget、contract 或 evidence inconclusive 都会污染归因 | 增加 NOT_RUN_POLICY + NOT_EVALUATED；仅已运行且受证据范围限制的结果使用 INCONCLUSIVE | FIXED |

未发现需要重开 V1.1–V1.17 的结构性冲突。

## 3. 与上下游逐段检查

| Stage | 检查问题 | 结论 | 案例 |
|---|---|---|---|
| S00 | 多次 Preview 是否重复获得预算 | Preview 预算按 diary day 累计，Revision 不重置 | 用户打开 App 四次，Preview 合计仍最多 4 VBU |
| S01 | S08 是否改写 RawAsset truth | 不改写，只引用 immutable source/evidence IDs | 导入时间不能被验证模型改成拍摄时间 |
| S02 | 是否补取 Auto/完整 Raw | 禁止；proxy/audio 必须已允许且存在 | UPLOAD_1 单帧看不清时直接不确定，不请求另外两帧 |
| S03 | 是否重新计算 Phone route/signal | 不重新路由；只读已有结构 | 云端不能因候选重要把 UPLOAD_1 改成 UPLOAD_3 |
| S04 | 是否写回新 fact | validation finding 独立保存，不改写 fact card | “火焰熄灭”只属于 TaskOutcome，不修改旧 Observation |
| S05 | 是否改变 Moment boundary | 不改变，只读 ledgers/context | 古镇 A/C relation PASS 也不把奶茶 B 的 seams 抹掉 |
| S06 | 是否恢复 DROP/提升 CONTEXT_ONLY | 禁止 | 奶茶 B 可限制解释，不能变成 Chapter 内容 |
| S07 | 是否修改 Candidate disposition | 不修改；另产 ValidatedCandidate wrapper | Long-Manual 原 Candidate 继续 provisional，wrapper 才可进 S09 |
| S09 | 是否提前做最终 Top-K | 不做，只建立 eligibility/resolution | shared task 先执行不代表该 Chapter 最终被选 |
| S10 | 是否选择美图/hero | 不做 | media diversity PASS 不等于选定表演中的最佳画面 |
| S11 | 是否生成故事/情绪 | 不做 | ASR 只确认说了什么，不写“全家感动” |
| S12 | 是否替代最终 Claim Validation | 不替代 | S08 验证候选资格，最终文案仍需 S12 逐 Claim 检查 |
| S13 | 是否直接发布 | 不发布 | ValidatedCandidate 仍须经过 S09–S12 |

## 4. 统一模拟口径

每个画像按以下顺序：

~~~text
S07 provisional request
→ A0 exact cache
→ A1 structured validator
→ one cheapest capable paid modality if needed
→ at most one capability escalation
→ dual-axis outcome
→ Candidate-level resolution
~~~

默认 Baseline：

- Preview frontier ≤3 Candidate；
- Final frontier ≤8 Candidate；
- 每 Candidate ≤2 必要任务；
- 每 Task ≤2 paid capability step；
- 每 Task ≤6 VBU；
- 每 Candidate ≤8 VBU；
- 全日 Preview 累计 ≤4 VBU；
- 全日 S08 累计 ≤16 VBU；
- 每日最多 2 个 Task 启动 A3。

## 5. P01–P17 用户画像与语义时间轴

### P01｜普通办公室日，没有 provisional

~~~text
08:30 通勤
09:10 到办公室
12:20 午餐
18:10 回家
~~~

S07 的合格 Candidate 已为 ELIGIBLE，没有局部未知项。

- S08 task：0；
- paid action：0；
- 结果：直接进入 S09 pool；
- 检查：S08 不为“更放心”重复调用模型。

**结论：** PASS。

### P02｜生日吹蜡烛，清晰三帧

~~~text
19:30 点燃蜡烛
19:31 吹蜡烛
19:32 鼓掌
~~~

S07 已通过 Independent Memory Value，但 local peak 的火焰变化需要确认。

- Question：LOCAL_PEAK_CONFIRMATION；
- A1：现有结构无法确认火焰状态；
- A2-V：三张允许帧，1 VBU；
- 输出：COMPLETED + PASS；
- Candidate：VALIDATED_FOR_S09。

**结论：** PASS；局部视觉足够，没有升级。

### P03｜120 秒家庭表演 + 一张照片

~~~text
15:00 准备乐器
15:01 演奏
15:02 鼓掌谢幕
15:03 家庭合照
~~~

S07 使用 Long-Manual exception，必须验证 MEDIA_DIVERSITY。

- A0：无缓存；
- A1：三个 Window 具有不同时间区间、不同 grounded fact、不同 duplicate group；
- 输出：COMPLETED + PASS，0 VBU；
- Candidate：VALIDATED_FOR_S09。

**结论：** PASS；专用确定性 Validator 可以避免重复视觉调用。

### P04｜古镇—奶茶店—古镇

~~~text
10:00–10:30 古镇石板路与古建筑 A
10:32–10:48 进入现代奶茶店 B
10:50–11:20 回到古镇路线 C
~~~

S07 保留 RESUMED_EPISODE 与 LOCAL_EPISODE_GROUP 两个 alternative。

- Task 1：A/C 是否恢复同一局部 outing；
- A1：时间、路径顺序、A/C motif 与 ledgers 足够，PASS；
- Task 2：B 是否给 broader candidate 增加独立实质内容；
- A2-V：A/B/C 各一张代表帧，1 VBU，PASS mapping = BOTH_DISTINCT；
- 输出：两个 Candidate 各按自己的 gate 聚合，S07 Candidate 不被改写。

**结论：** PASS；A/C 可以服务同一 Chapter，同时 B 是否纳入保持为单独问题。

### P05｜上午和晚上两次相似遛狗

~~~text
07:20 小区遛狗
20:10 同一小区再次遛狗
~~~

外观相似但相隔很久，是两个 Episode。

- S07：两个 ELIGIBLE SINGLE，可由 S09 处理全天冗余；
- S08：0 task；
- 检查：不能利用 similarity 创建 EPISODE_RELATION task 偷渡合并。

**结论：** PASS。

### P06｜演唱会三个清晰峰值

~~~text
20:00 开场
20:35 最喜欢的歌曲
21:10 嘉宾出现
22:00 返场
~~~

S07 最多提名三个互不重叠 Aha；假设三个均有明确局部问题。

- Preview frontier：3；
- 三个 A2-V 各 1 VBU，共 3；
- 第四峰值在 S07 已有 cap trace，不进入 S08；
- S08 不因页面目标再创造第四个 Aha。

**结论：** PASS；Candidate cap 与 paid budget 同时有效。

### P07｜吹蜡烛关键时刻被遮挡

~~~text
前帧：能看到点燃蜡烛
中帧：人物遮住蛋糕
后帧：蛋糕仍被遮住
~~~

- A2-V：正常完成，但 SOURCE_EVIDENCE_ABSENT_OR_OCCLUDED；
- 输出：COMPLETED + INCONCLUSIVE；
- A3：禁止，因为不是 capability limit；
- Candidate：UNRESOLVED_EVIDENCE。

**结论：** PASS；宁可错过，不根据场景常识猜。

### P08｜孩子第一次说“妈妈”，但音频许可未通过

~~~text
18:40 Manual Video
画面：孩子看向家长
关键事实：是否实际说出“妈妈”
~~~

- Question：LOCAL_PEAK_CONFIRMATION；
- pre-dispatch policy gate：audio 当前不允许；
- 输出：NOT_RUN_POLICY + NOT_EVALUATED；
- A2-A：不运行；
- Candidate：UNVALIDATED_OPERATIONAL。

**结论：** PASS；声音必要也不能绕过数据许可。

### P09｜轻量视觉 provider 首次超时

- 第一次 A2-V：provider timeout，1 VBU；
- same-tier fallback：成功，1 VBU；
- 输出：COMPLETED + PASS；
- A3：未启动；
- retry waste 与第二次 exposure 单独记录。

**结论：** PASS；服务故障没有触发强模型。

### P10｜模型返回越权 Evidence ID

- A2-V 第一次返回未知 frame_id；
- 同级一次重试仍返回非法引用；
- 输出：CONTRACT_INVALID + NOT_EVALUATED；
- Candidate：UNVALIDATED_OPERATIONAL；
- 不接受自由文本，不升级 A3。

**结论：** PASS。

### P11｜视觉语义确实困难，但证据存在

~~~text
A：牌坊写景区正式名
C：路牌写同一区域旧称
~~~

- A2-V：COMPLETED + INCONCLUSIVE，CAPABILITY_LIMIT，1 VBU；
- A3：使用同三张帧和同一 ledger，4 VBU；
- A3 PASS；
- Task 共 5 VBU，未超过 6；
- Candidate：VALIDATED_FOR_S09。

**结论：** PASS；这是允许的能力升级，不扩大证据。

### P12｜一天多次打开 App

~~~text
10:00 Preview R1
12:00 Preview R2
15:00 Preview R3
18:00 Preview R4
21:00 Final R5
~~~

- R1 同一任务首次 A2-V：1 VBU；
- R2/R3 证据和版本相同：A0 exact cache，0；
- R4 新问题使用 3 VBU 后，Preview daily pool 达到 4；
- 后续新 Preview paid task：NOT_RUN_BUDGET；
- R5 exact task 继续 0；新 Final task 可使用 day total 剩余 12。

**结论：** PASS；App 打开次数不直接乘成本。

### P13｜Preview 结果迟于 Final Revision

~~~text
R2 task 正在运行
→ 新素材到达
→ Final R3 建立
→ R2 返回 PASS
~~~

- R2 outcome 保存；
- revision_applicability = STALE_FOR_CURRENT_DOWNSTREAM；
- 不直接挂到 R3；
- R3 若 semantic/action fingerprint 完全相同，复用 payload并建立 R3 wrapper；
- 若新增素材改变 Candidate content fingerprint，则 cache miss。

**结论：** PASS。

### P14｜两个必要任务，但只剩 1 VBU

候选需要 relation 与 media diversity 两个任务，最低 paid 首步各需 1 VBU。

- atomic minimum reservation 需要 2；
- 当前只剩 1；
- 两个 paid task 均不启动；
- 输出：NOT_RUN_BUDGET + NOT_EVALUATED；
- 不发生半验证花费。

**结论：** PASS。

### P15｜Final 高强度 frontier

使用既有高强度参考日：

~~~text
150 Auto Video
+ 20 Manual Photo
+ 10 × 15s Manual Video
+ 3 × 60s Manual Video
+ 3 × 120s Manual Video
= 186 RawAssets

150 Auto Windows
+ 20 Photo Windows
+ 20 + 12 + 18 Manual Video Windows
= 220 logical Evidence Windows
~~~

S08 不重新理解这 220 个 Window。S04–S07 已缓存结构化结果；即使 S07 高强度容量模拟产生最多 122 个轻量 hypothesis，Final 也只有最多 8 个合法 provisional Candidate 进入 S08 frontier。

假设这 8 个 Candidate 的路径为：

| Route | Candidate 数 | VBU |
|---|---:|---:|
| A1 直接解决 | 2 | 0 |
| A2-V PASS | 3 | 3 |
| A2-A PASS | 1 | 1 |
| A2-T PASS | 1 | 2 |
| A2-V INCONCLUSIVE → A3 PASS | 1 | 5 |
| 合计 | 8 | 11 |

- 未超过 Final frontier 8；
- 未超过 day total 16；
- A3 task count = 1；
- 没有全日 Raw 或额外 Auto frame。

**结论：** PASS；高强度并不等于所有 Candidate 都跑强模型。

### P16｜月度成本预测达到预警

- cohort forecast 已到内部 US$1.20 warning；
- A0/A1 继续；
- 新 Preview paid action 和 A3 停止；
- Final 只运行高 decision-yield 的最低 A2；
- 其余为 NOT_RUN_BUDGET，而非 Evidence FAIL。

**结论：** PASS；月度成本压力有可解释降级顺序。

### P17｜一个 shared task 解决两个 alternative

两个 Candidate 共享问题：“较大范围 Candidate 是否增加实质内容”。

- 只建立一个 shared ValidationTask；
- A2-V 只调用一次，1 VBU；
- pass/fail mapping 分别映射两个 member；
- 不重复收费，也不把一个 member 的 FAIL 扩散为整个 group FAIL。

**结论：** PASS。

## 6. 容量上界检查

### 6.1 Task 上界

~~~text
Final frontier <= 8 Candidates
necessary tasks per Candidate <= 2
therefore planned necessary tasks <= 16
~~~

A0/A1 最多对这 16 个任务运行一次专用检查，不产生第三方模型调用。

### 6.2 Paid dispatch 上界

每个 paid attempt 最低为 1 VBU，所有 retry 也消耗：

~~~text
S08 day total <= 16 VBU
therefore paid third-party dispatch <= 16 / diary day
~~~

若某 provider 的实际价格使 reserved_vbu 更高，dispatch 上界只会下降。

Preview 的所有 Revision 合计最多 4 个最低权重 paid dispatch。

### 6.3 Strong model 上界

~~~text
A3 start tasks <= 2 / diary day
A3 minimum weight = 4 VBU
~~~

两个 A3 至少消耗 8/16 day VBU，因此其余预算自然收紧。A3 仍受 task/candidate cap。

### 6.4 模态暴露理论上界

如果全天 16 VBU 全部用于同一种最低权重动作：

- A2-V：最多 16 dispatch × 3 frame = 48 frame exposure events；
- A2-A：最多 16 × 15 秒 = 240 秒局部音频 exposure；
- A2-T：最多 8 dispatch × 6 秒 = 48 秒低分辨率 proxy exposure；
- A3：最多 2 个 task 启动，并且只能复用已有 payload。

这些是最坏路径的第三方发送事件数，不是独特 RawAsset 数，也不是产品目标。

## 7. Failure attribution matrix

| 情况 | ExecutionStatus | EvidenceDecision | 是否进 S09 | 是否允许 A3 |
|---|---|---|---|---|
| 证据明确支持 | COMPLETED | PASS | 全部必要 task PASS 后可以 | 不需要 |
| 证据明确反驳 | COMPLETED | FAIL | 不可以 | 不允许 |
| 能力不足但证据存在 | COMPLETED | INCONCLUSIVE | 当前不可以 | 预算内可一次 |
| 证据缺失/遮挡 | COMPLETED | INCONCLUSIVE | 不可以 | 不允许 |
| 月度/日预算不足 | NOT_RUN_BUDGET | NOT_EVALUATED | 不可以 | 不允许 |
| 数据/暴露政策未授权 | NOT_RUN_POLICY | NOT_EVALUATED | 不可以 | 不允许 |
| Provider 尝试用尽 | PROVIDER_FAILED | NOT_EVALUATED | 不可以 | 不允许 |
| 输入/输出合同非法 | CONTRACT_INVALID | NOT_EVALUATED | 不可以 | 不允许 |
| 旧 Revision 迟到结果 | 保留原状态 | 保留原决定 | 当前 Revision 不可以 | 由新 Revision 重评 |

## 8. 不变量检查结果

Working V0.1 的 26 条 Validator 不变量逐项人工检查：

- 输入、问题和 role boundary：PASS；
- no-refetch、no-default-Raw、bounded media：PASS；
- action、escalation、retry 与 provider attribution：PASS；
- task/candidate/Preview/day/monthly budget：PASS；
- exact cache、idempotency、Revision/stale：PASS；
- result matrix、ValidatedCandidate 与 AlternativeResolution：PASS；
- S09–S13 职责隔离：PASS。

未发现循环依赖：S08 admission 不需要 S09；S09 读取 S08 outcome，但 S08 不需要最终集合。

## 9. 仍需真实数据校准，但不是冻结 blocker

1. VBU 权重是否准确反映真实 provider 价格；
2. Preview 4 / day 16 是否在成本与 validation lift 间最优；
3. 每 Candidate 最多 2 task 的 truncation regret；
4. 3 frame / 6s proxy / 15s audio envelope 的漏失率；
5. A1 专用 Validator 的 false-pass；
6. A2-V/A2-T/A2-A/A3 的真实 INCONCLUSIVE 与升级收益；
7. 两次 provider attempt 是否达到可靠性目标；
8. 不同用户画像的预算可用性与质量公平；
9. 月度 warning 降级对 Final Chapter/Aha 召回的影响；
10. S08 validation lift 是否足以证明其成本值得。

这些参数必须通过真实 labeled data 与 provider telemetry 显式重开，不能由实现静默修改。

## 10. 冻结建议

P01–P17 未发现新的结构性 blocker。建议：

- 将 Working V0.1 的 one-question task、四类问题、最低充分动作树、双轴结果、预算、缓存、失败、Revision 与独立输出冻结为 V1.18；
- 数字 Baseline 保持 versioned + 可校准；
- provider/model/price/prompt/schema 与真实阈值保持 OPEN；
- 本报告完成时的下一阶段是 S09；S09 现已由 V1.19 冻结，当前下一专项为 S10，仍不得提前实现 S11 Narrative。
