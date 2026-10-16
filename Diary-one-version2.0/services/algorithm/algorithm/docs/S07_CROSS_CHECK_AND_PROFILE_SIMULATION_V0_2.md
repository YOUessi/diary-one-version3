# S07 Cross-Check and Semantic Timeline Simulation V0.2

**状态：** `REVIEW COMPLETE / SUPPORTS FROZEN V1.17`
**日期：** 2026-08-26
**被测合同：** [S07 Candidate Generation Consolidated Working V0.2](S07_CANDIDATE_GENERATION_CONSOLIDATED_WORKING_V0_2.md)
**历史对照：** [S07 Cross-Check and Semantic Timeline Simulation V0.1](S07_CROSS_CHECK_AND_PROFILE_SIMULATION_V0_1.md)
**冻结结果：** 用户已确认；当前权威规则见 [Canonical Checkpoint V1.17](CANONICAL_CHECKPOINT_V1_17_CHAPTER_AHA_CANDIDATE_GENERATION.md)
**作用范围：** 将 V0.1 发现的 F1–F7 修正并入统一 S07 合同后，重新运行 P01–P13 语义时间轴，检查质量、候选容量、Trace 与上下游边界
**明确不覆盖：** 真实视觉识别准确率、真实用户评分、S08 provider/action 设计、S09 最终集合评分、S10 媒体审美与渲染、非标准 Manual 时长、App、Firmware/SDK、共享状态文件

> **当前后续状态：** F8 在本报告所属的 S07 阶段正确保持 OPEN；其 S08 action/cost/exposure 设计现已由 [V1.18](CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md) 冻结。

## 1. 本次复跑回答什么

本报告只回答三个问题：

1. F1–F7 修订是否真正解决 V0.1 暴露的结构问题；
2. 不同高概率用户日型能否在不凑数、不远距离主题聚类、不静默丢失的前提下生成合理 Candidate；
3. 五小时高强度参考日是否会让 S07 发生组合爆炸或引入新的云端模型成本。

这仍是基于“上游事实基本正确”的语义模拟，不是准确率 Benchmark。它能发现合同矛盾和明显边界错误，不能证明真实数据上的 precision、recall 或用户满意度。

## 2. V0.1 问题的落实检查

| Finding | V0.2 落实方式 | 检查结果 |
|---|---|---|
| F1：3 RawAsset 无例外硬门误杀长 Manual | 保留 Normal path；增加 1–2 RawAsset 的 Long-Manual exception，并要求至少 3 个时间与语义均不同的 CandidateContentUnit，之后进入 `MEDIA_DIVERSITY` 定向验证 | FIXED |
| F2：ordinary Moment 最多 2 个 Aha 会提前丢失第三峰值 | ordinary origin 改为最多 3 个互不重叠 Aha；Transition 仍最多 1；全天最终 0–3 不变 | FIXED |
| F3：8-Moment search horizon 与 group membership 混淆 | 8 只限制非相邻 relation nomination；已成立 group 可逐步扩展，当前 12 content-member safety cap 为可校准 Baseline | FIXED WITH CALIBRATION |
| F4：硬门与待验证状态混淆 | gate 使用 `PASS / NEEDS_VALIDATION / FAIL`；Candidate 使用四种唯一 disposition，并明确解析优先级 | FIXED |
| F5：参与 group 的 seed 缺少审计 | 每个 content-active seed 恰好一个 SeedAuditRecord，同时记录 originated、participated 与 no-candidate reasons | FIXED |
| F6：未验证的近重复可能被过早抑制 | S08 前只允许已证明的 identity/duplicate/dominance suppression；不确定解释保留在 alternative group | FIXED |
| F7：S08 admission 依赖尚未运行的 S09 | admission 改为“能否决定 provisional Candidate 的下游资格、解决 alternative dominance、确认长 Manual 多样性或具体局部峰值”；S08 另产出 outcome，不回写 S07 | FIXED |
| F8：3/8 只是数量 guardrail | 在 S07 明确标为 count guardrail；加权 action/token/exposure/monthly budget 继续留给 S08 | CORRECTLY OPEN |

## 3. 统一判断口径

每个画像按同一组条件复跑：

- **Truth**：Candidate 只使用当前 Revision 的 KEEP grounded facts；
- **Episode**：Chapter 必须是局部经历，不是全天主题；
- **Value**：素材数量不替代独立记忆价值；
- **Aha**：Local Peak 与 Independent Memory Value 分别成立；
- **Duplicate**：相似不等于同一 Memory；未证实 dominance 不提前删；
- **Trace**：每个 seed、candidate、scope stop、budget stop 与 Revision 变化可追溯；
- **Cost**：S07 只使用缓存结构化数据和轻量比较，不新增上传或模型调用。

结果标签：

```text
PASS
PASS / PROVISIONAL VALIDATION
PASS / DECLARED PRECISION TRADE-OFF
FAIL / STRUCTURAL BLOCKER
```

## 4. P01–P13 V0.2 复跑

### P01｜城市办公室工作日

- 重复办公素材去重后不足 Coverage 或 Memory Value，不能因 RawAsset 多而成章；
- 会议、与同事午餐若分别通过完整 Chapter gates，可各自产生 SINGLE；
- 普通咖啡、走廊与画面变化不通过 Aha 双门；
- 合法结果可以只有 1–2 Chapter、0 Aha。

**结果：** `PASS`。没有配额填充，也没有把日常 motion/scene delta 当作高光。

### P02｜古镇 Citywalk—奶茶—继续 Citywalk

- M1+M2 具备形成 ADJACENT_GROUP 的条件；
- A/C 若有同一具体步行主线恢复证据，具备形成 RESUMED_EPISODE 的条件，奶茶 M3 保留为 interruption ref；
- 若 M3 对同一次 outing 提供独特内容，M1–M5 还具备形成 LOCAL_EPISODE_GROUP alternative 的条件；
- 同一最早 owner 最多 materialize 2 个 grouped hypotheses；本例通常保留 RESUMED 与 LOCAL 两种不同 Memory basis，较小 ADJACENT scope 只有在已证实 dominated 时才 suppression，否则必须记录 `GROUP_HYPOTHESIS_CAP_REACHED` 及最小 Evidence refs；
- 不确定的 RESUMED 与 LOCAL 解释先进入 alternative group，不能提前 suppression；
- group owner 之外的 M2/M4/M5 通过 `participated_candidate_ids` 完整留痕。

**结果：** `PASS`。V0.1 的 missing seed trace 已由 SeedAuditRecord 解决，A/C 不会因 B 被永久 split，也不会抹掉 B；grouped cap 的取舍不再静默。

### P03｜一条 120s 家庭仪式视频 + 一张照片

- distinct RawAsset = 2，不满足 Normal path；
- 若长 Manual 的至少 3 个 Window 分别支持准备、核心动作、结果等真实不同内容，可形成至少 3 个 CandidateContentUnit；
- 该 Chapter 进入 Long-Manual exception，状态必须为 `PROVISIONAL_VALIDATION_REQUIRED`；
- S08 只确认这些 Window 是否真的构成不同内容位置；通过时另行输出 downstream-eligible ValidatedCandidate，不回写原 provisional Candidate；
- 一个具体吹蜡烛、谢幕或拥抱 peak 可独立提名 Aha，但 Chapter 不再因素材文件数少被直接误杀。

**结果：** `PASS / PROVISIONAL VALIDATION`。F1 的结构性漏召回已解决；真实多样性和最终媒体可用性仍分别属于 S08、S10。

### P04｜居家远程工作日

- 90 个近重复 Auto 不会变成 90 个内容单元；
- 上午/下午桌面办公即使可建立 resumed 关系，也会因 Memory Value 不足而拒绝；
- Manual Coffee Photo 不凭 Manual intent 自动成为 Aha；
- 可以得到 `NO_CHANGE / EMPTY_DAY`。

**结果：** `PASS`。高素材量没有绕过质量门。

### P05｜上午与晚上两次相似遛狗

- 两段活动跨越长时间和独立 Episode，超出局部 relation 与 unsupported-gap 边界；
- 不只因 activity、scene 或 embedding 相似而 grouping；
- 不只因视觉相似而 candidate-level duplicate；
- 两个 SINGLE 可以同时留给 S09 做全天集合冗余判断。

**结果：** `PASS`。S07 局部去重与 S09 全天编辑边界保持清楚。

### P06｜徒步中存在 35 分钟无有效 Evidence

- blur/motion spike 不产生 Aha；
- 30 分钟 unsupported gap 阻断 M1→M2 的同一 Chapter 推断；
- 必须记录 `SCOPE_STOP_UNSUPPORTED_GAP`，不能静默切断；
- M2+M3 仍可形成后半段局部 Chapter，具体到达或互动可提名 Aha。

**结果：** `PASS / DECLARED PRECISION TRADE-OFF`。它可能漏掉“整次徒步”，但符合当前宁可漏记、也不跨无证据长间隔虚构连续性的原则；该 regret 留给真实数据测量。

### P07｜聚餐 Manual 连拍 + 一次碰杯

- 相似菜品照片不会重复增加 CandidateContentUnit；
- M1–M4 可形成有共同 occasion envelope 的 LOCAL_EPISODE_GROUP；
- 碰杯的多帧、多照片只对应同一个具体 peak，不复制成多个 Aha；
- Manual 没有 duplicate 或 Truth 豁免。

**结果：** `PASS`。Manual 独立窗口仍保留原素材，但 Memory Candidate 保持精简。

### P08｜一个演唱会 Moment 内多个峰值

- M1 可形成一个 SINGLE Chapter；
- 嘉宾登场、明确互动、彩带、返场分别先按具体事件去重；
- ordinary origin 最多保留 3 个互不重叠且各自通过双门的 Aha hypothesis；
- 若存在第 4 个合格峰值，不能静默丢弃，必须以 `AHA_SEED_CAP_REACHED` 记录 truncation trace；
- S09 最终全天仍最多选择 3 个 Aha。

**结果：** `PASS`。V0.1 的第三峰值必丢问题已解除；超过 3 个真实峰值时的截断 regret 作为 Baseline 监测项保留。

### P09｜同一商场内的办事链

- 相同地点与时间接近只支持 locality，不足以虚构统一目的；
- 若连续移动与共同 outing envelope 足够，可提名谨慎的 LOCAL_EPISODE_GROUP；
- 药店、超市、午餐、取件的 SINGLE hypotheses 可作为不同解释保留；
- 关系或 dominance 尚待核查时进入 alternative group，不提前 suppression。

**结果：** `PASS`。不写“高效完成计划”等推测性 Narrative，也不会因 scope 较大就自动支配更具体的 SINGLE。

### P10｜一个项目被切成十个细 Moment

- M1–M8 可通过局部关系建立初始 group；
- M9、M10 可逐步扩展，因为每一步均通过 local relation、EpisodeGroupSignature compatibility 与 material gain；
- 十个 content members 未超过当前 12-member safety cap；
- 完成结果不会因 8-Moment nomination horizon 被机械切掉；
- S05 的十个 Moment 与全部 seams 仍保持不变。

**结果：** `PASS`。F3 的 architecture ambiguity 已解除；12 的真实 truncation regret 仍待数据校准。

### P11｜晚到素材产生新 Revision

- R1 Candidate 与 audit 不修改；
- R2 对插入素材后的完整 Snapshot 重新建立 relation；
- unchanged fingerprint 可复用确定性计算 payload，但必须绑定 R2 的 instance/provenance；
- 不能把 R1 candidate instance ID 当作 R2 ID；
- lineage 可表达 continues/expands/splits/supersedes，用户可见 stable ID 留给下游。

**结果：** `PASS`。Revision immutability、cache reuse 与 identity 不再混淆。

### P12｜Transition 内出现短暂街头表演

- Transition 永远不能进入 Chapter content；
- 只能凭自身 KEEP 判断 local peak 与独立价值；
- 不借左右 ordinary Moments 补事实；
- 通过时最多一个 Aha，否则 REJECTED。

**结果：** `PASS`。边界不明确本身仍不是 Aha 信号。

### P13｜五小时高强度参考日

输入保持原 Reference：

```text
150 Auto Video
+ 20 Manual Photo
+ 16 Manual Video
= 186 RawAsset / 220 Evidence Window
```

采用偏高但可能出现的上游输出：

```text
28 committed Moments
→ 20 ordinary content-active
→ 2 Transition content-active
→ 3 context-only
→ 3 output-inactive
```

V0.2 gate 前理论 Candidate hypothesis 上限：

```text
20 ordinary × 1 SINGLE              = 20
20 ordinary × 2 grouped hypotheses  = 40
20 ordinary × 3 Aha                 = 60
2 Transition × 1 Aha                = 2

total                               = 122
```

这些是轻量、结构化、带 disposition 的内部 hypothesis，不是 122 次模型调用，也不是 122 个用户输出。它们之后仍经过 gate、duplicate/alternative resolution、S08 最多 Preview 3 / Final 8 的验证前沿，以及 S09 最终 1–5 Chapter / 0–3 Aha 集合选择。

**结果：** `PASS`。S07 没有组合爆炸的结构性证据；真实成本瓶颈仍在 S08 enrichment 和 S10 HQ/render，不应通过全天 S07 Top-K 牺牲召回。

## 5. 容量与复杂度复核

### 5.1 relation comparison

28 个 committed Moments、forward horizon = 8 时，若把相邻与非相邻 relation nomination 都计入，并让每个位置最多看后续 8 个位置，有界前向比较数最多为：

```text
20 × 8 + (7 + 6 + 5 + 4 + 3 + 2 + 1)
= 188 comparisons
```

已成立 group 的扩展是逐步且有 12 content-member cap，不重新做全天 all-pairs。加上每个 ordinary seed 最多 2 个 grouped hypotheses，规模仍随 Moment 数量近似线性增长，而不是枚举所有 Moment 子集。

### 5.2 S07 与 S08 成本不能混算

S07 默认新增：

```text
Cloud media upload       = 0
VLM / strong-model call  = 0
Auto refetch             = 0
full Raw request         = 0
```

S07 的主要消耗是读取缓存对象、比较局部 signature、创建 Candidate/audit 和计算 fingerprint。Preview 3 / Final 8 只限制进入 S08 的 provisional Candidate 数量；一个 Candidate 可能需要不同数量和价格的 validation action，因此它仍不能代表美元或 Token 预算。

## 6. 上下游边界复核

| 边界 | V0.2 行为 | 结果 |
|---|---|---|
| S04 → S07 | 只引用 grounded facts、UNKNOWN、support 与 limitations，不重写事实 | PASS |
| S05 → S07 | Chapter grouping 是候选关系，不 merge Moment、不删除 seam | PASS |
| S06 → S07 | KEEP 才生成内容单元；CONTEXT_ONLY 只限制解释；DROP 不恢复；Transition 不成章 | PASS |
| S07 → S08 | 只把有明确可解问题的 provisional Candidate 放入有界 validation frontier | PASS |
| S07 → S09 | S07 不做全天 editorial Top-K，不决定最终 1–5 Chapter / 0–3 Aha 集合 | PASS |
| S07 → S10 | CandidateContentUnit 不冒充最终精选媒体；Aha 支持 Window 不等于 Anchor | PASS |
| Revision | 每个 instance 属于一个 immutable Revision；跨 Revision 只复用计算，不复用 identity | PASS |
| 上传合同 | 不补 Auto 帧、不请求完整 Raw、不新增媒体上传 | PASS |
| 产品/工程范围 | 未修改 App、Firmware/SDK 或共享状态文件 | PASS |

## 7. 仍需保留的风险与 OPEN 项

以下不阻塞 S07 架构冻结，但必须显式保留，不能伪装成已经验证：

1. `group_member_safety_max = 12`：需要测量长项目截断 regret 与错误扩组率；
2. `unsupported_capture_gap_max = 30 minutes`：需要测量 P06 类连续活动的漏组率；
3. ordinary seed 的 Aha cap = 3：需要记录真实 `AHA_SEED_CAP_REACHED` 及被截断候选后续 regret；
4. ordinary seed 的 grouped hypothesis cap = 2：需要记录 `GROUP_HYPOTHESIS_CAP_REACHED`，尤其关注 P02 类 nested alternatives；
5. CandidateContentUnit：具体相似度、语义增益与跨 Window 去重阈值尚未校准；
6. Long-Manual exception：S08 `MEDIA_DIVERSITY` validator 与 S10 同源多媒体可用性尚未实现；
7. Alternative hypotheses：需要测量 unresolved alternative ratio 与 S08 dominance validation 收益；
8. S08：仍需 action-weight、Token、媒体暴露、Revision/day/monthly budget 与失败归因；
9. Production schema、reason taxonomy、fingerprint/lineage matcher 与 validator engine 尚未实现；
10. 16 秒、73 秒等非标准 Manual Window 方案仍是 S02 的既有 OPEN，不在 S07 偷偷补定；
11. 本轮没有真实图片、真实模型或用户标签，因此不证明真实 precision/recall。

所有数值调整都必须版本化，并保留调整前后 Trace 与 Benchmark 对照。

## 8. 冻结前结论

V0.2 重新运行 P01–P13 后，没有发现新的 S07 结构性 blocker：

- 长 Manual 不再被 3 RawAsset 规则误杀；
- 第三个真实 Aha 峰值不再在 S09 前必然丢失；
- 长局部 Episode 不再被 8-Moment nomination horizon 错切；
- seed 与 candidate 都有完整审计；
- 未确认 alternatives 不再提前删除；
- S08 admission 不再依赖未来的 S09 结果；
- 高强度参考日的 S07 仍是有界轻量计算。

因此，本报告建议把 V0.2 作为 **S07 freeze-ready Baseline**。可冻结的是架构、职责边界、gate/disposition、候选类型、审计、不补帧/不新增模型调用和当前有界 Baseline；不能冻结为“已经真实验证”的是第 7 节列出的阈值、模型、成本预算和效果指标。

用户已明确确认，本报告的 freeze-ready 结论已固化为 V1.17。本文继续作为验证证据保留，不替代 Canonical Checkpoint。
