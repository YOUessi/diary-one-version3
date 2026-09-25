# S10-D4 Aha Final Media — Internal Cross-Check V0.1

**状态：CROSS-CHECK PASSED / REFINEMENTS APPLIED / S10 FROZEN BY CANONICAL V1.21**
**日期：2026-08-27**
**被检合同：** S10-D4.1 Aha Single Visible Media、S10-D4.2 Cross-Memory Render Distinctness
**上游硬前提：** Canonical V1.20 Aha–Chapter Narrative Independence
**案例数：** 36

## 1. 检查目标

验证 D4 是否同时做到：

1. 每个 Aha 始终只有一个用户可见媒体项；
2. support Window、Poster、Primary/Fallback 不会膨胀媒体数量；
3. same-story Chapter/Aha 永远到不了 render reuse；
4. 合法不同故事默认减少用户可见重复，但不牺牲真实性和质量；
5. 裁切、编码或动态区间包含不能绕过 duplicate detection；
6. no-loss alternative 不会越权创建新 Beat/Anchor/Route 或主动激活 Fallback；
7. necessary exact reuse 可共享成本但不合并 Memory identity；
8. runtime failure、cross-Revision、UNKNOWN 与 HQ manifest 行为确定。

本检查不使用真实媒体、模型、上传或渲染，不证明用户对重复画面的真实容忍度，也不决定 App 最终布局。

## 2. Invariants

| ID | Invariant |
|---|---|
| I01 | Aha visible media count 恒等于一 |
| I02 | Aha 只允许 PHOTO/LIVE_2S，禁止 VIDEO_5S |
| I03 | Aha active media identity 同时承担 Hero；poster 不是新内容 |
| I04 | 所有 Aha Route 直接表达同一 peak |
| I05 | V1.20 narrative PASS 是 cross-memory reconciliation 硬前提 |
| I06 | distinct-render preference 低于 truth/core/quality/robustness/prior continuity |
| I07 | Aha Primary 不为视觉避重主动降级 |
| I08 | no-loss alternative 只能来自当前 attempt 已有 hard-valid finalist |
| I09 | cosmetic variant 与 material interval overlap 不能伪装 distinct |
| I10 | 无无损替代时 exact reuse 合法且不触发 S09 re-selection |
| I11 | shared materialization 不合并 Memory/claim/lineage/count |
| I12 | runtime fallback 不为软避重移动健康媒体或重排更优 Route |
| I13 | soft duplicate UNKNOWN 不阻断；base legality UNKNOWN 仍阻断 |
| I14 | 不新增模型、HQ 预取、全天搜索或用户交互 |

## 3. Case Matrix A｜Aha 单媒体与格式

| ID | 场景 | Expected |
|---|---|---|
| A01 | 一张决定性照片完整呈现求婚 peak | 1 × PHOTO；不请求动态 |
| A02 | 两秒完整呈现孩子回头挥手 | 1 × LIVE_2S；poster 为同一 identity 派生 |
| A03 | before/peak/after 共 3 个 support Windows | 只选 peak 的 1 个媒体；support 不变成三项 |
| A04 | PHOTO/LIVE 都合法，B2 选择 LIVE | 最终只显示 LIVE；PHOTO 仅可作为预声明 Fallback |
| A05 | 1 Primary＋2 Fallback | 仍计一个媒体位置；运行时最多一条 active Route |
| A06 | Aha 有合法 5 秒视频源 | VIDEO_5S 仍禁止，不因 source 可用放宽 |
| A07 | LIVE 卡片需要静态 poster | poster 不增加 Hero/member/HQ source count |
| A08 | 全部 Route proven terminal unavailable | `AHA_MEDIA_INSUFFICIENT`；不发 title-only/空卡片；pre-batch proven 可进入唯一 failure batch，runtime exhaustion 则 HOLD/BLOCK、不新增重选 |
| A09 | `HIGHLIGHT_DAY` 页面只有一个 Aha | 仍只有一个媒体，不因页面稀疏增加 supporting item |
| A10 | embedded distinct Aha | 与 standalone 使用相同单媒体/格式/同-peak floor |

**结果：** 10/10 PASS。

## 4. Case Matrix B｜V1.20 关系前置

| ID | Chapter/Aha pair | Expected |
|---|---|---|
| B01 | Birthday Chapter＋吹蜡烛 Aha | V1.20 same-story core 阻断；不进入 D4.2 |
| B02 | 古镇观光 Chapter＋甜品惊喜互动 Aha | narrative PASS 后可进入 D4.2 |
| B03 | 古镇观光＋普通甜品静物 | Aha standalone floor FAIL；不能因画面 distinct 共选 |
| B04 | 两个 RawAsset 分别拍同一次求婚 | same-story 阻断；source distinct 无效 |
| B05 | 无法确定 peak 是 Chapter core 还是 side event | unresolved，当前 Revision 至多一个；D4.2 不兜底 |
| B06 | Aha 对 Chapter A PASS、对同 set Chapter B core conflict | 完整 set 非法；A 的 PASS 不抵消 B conflict |

**结果：** 6/6 PASS。

## 5. Case Matrix C｜Render relation 与 no-loss alternative

| ID | 场景 | Expected |
|---|---|---|
| C01 | Chapter 建筑照、Aha 甜品反应，来源不同 | `DISTINCT_SOURCE_DISTINCT_RENDER`；保持原计划 |
| C02 | 同一长视频：Chapter 店铺环境、Aha 第一口反应 | `SHARED_SOURCE_DISTINCT_RENDER`；可共享 fetch、分别 render |
| C03 | Chapter/Aha 指向同一精确 Frame | `EXACT_CANONICAL_RENDER`；进入软避重 |
| C04 | 同一 Frame 只做裁切、调色、分辨率变化 | `COSMETIC_EQUIVALENT_RENDER`；不能伪装 distinct |
| C05 | Chapter VIDEO_5S 完整重放 Aha 核心 LIVE_2S | `MATERIAL_TEMPORAL_OVERLAP`；进入同一软避重 |
| C06 | 两个 interval 轻微边界不同但核心动作完全相同 | material overlap；不能靠毫秒差异避重 |
| C07 | 有同 target size、同 core/quality/robustness 的 Chapter alternative | 选 `DISTINCT_RENDER_SELECTED_NO_LOSS` 并重验证 D1/D2/Hero |
| C08 | 替代会降低 Chapter core、画质或失败鲁棒性 | 不算 no-loss；允许 `EXACT_REUSE_ALLOWED_NO_NO_LOSS_ALTERNATIVE` |

**结果：** 8/8 PASS。

## 6. Case Matrix D｜Hero、Fallback 与不可变性

| ID | 场景 | Expected |
|---|---|---|
| D01 | Chapter Hero 与 Aha poster 相同，另有近似等价合法 Hero | 在 continuity 允许时选 distinct Hero projection |
| D02 | Aha 画面被选为 Chapter 唯一代表性 core Hero | 回查 V1.20/meaning-first；可能 relation/hero contract invalid |
| D03 | 初始 media distinct；terminal failure 后 Aha Fallback 与 Chapter 相同 | 允许 `EXACT_REUSE_ALLOWED_BY_RUNTIME_FALLBACK` |
| D04 | 第一合法 Fallback 语义完整但重复；第二条 distinct 却语义更弱 | 不为软避重跳过第一条；保持 B3 顺序 |
| D05 | 一次网络超时 | transient；不激活 Fallback，也不产生 reuse decision |
| D06 | Aha LIVE 直接表达 peak，PHOTO 只有事后结果 | 不为避重主动降级 Aha；没有 Chapter no-loss alt 时 exact reuse |

**结果：** 6/6 PASS。

## 7. Case Matrix E｜Cross-Revision、UNKNOWN、HQ 与成本

| ID | 场景 | Expected |
|---|---|---|
| E01 | prior Revision 已必要复用且无内容变化 | 不单独发新 Revision；prior continuity 防 churn |
| E02 | 合法新 Revision 已产生，新增一个无损 distinct alternative | 可在本 Revision 减少重复并记录原因 |
| E03 | 两个 consumer 精确复用同一 render | 两个 consumer refs＋一个 shared materialization |
| E04 | 同源不同 interval/render | source fetch 可 coalesce；语义 scope 和 final render 分开 |
| E05 | 只是不确定两个合法 render 是否软近重复 | 保留原计划，记录 `RENDER_RELATION_LIMITATION`，不阻断 |
| E06 | source identity/provenance/Anchor legality 本身 UNKNOWN | 按 B3/S10 unresolved HOLD/BLOCK；不能借软偏好放行 |

**结果：** 6/6 PASS。

## 8. 发现并应用的 Refinements

### R1｜Aha readiness 必须区分内部冲突与跨 Memory 必要复用

D4.1 初稿中的“已知 canonical render identity 冲突”可能误伤 D4.2 合法 exact reuse。已改为：Aha 自身 unresolved/contract invalid 仍阻断；跨 Memory render relation 交由 D4.2，必要复用不是内部冲突。

### R2｜Soft UNKNOWN 与 base-contract UNKNOWN 必须分离

仅无法确定是否“看起来太像”时，不应阻断 truth/core 均合法的 Revision；保留原计划并记录 limitation。但 source identity、provenance、Anchor 或 legality UNKNOWN 仍是基础合同问题，必须 HOLD/BLOCK。

### R3｜不同 duration 也可能实质重复

若 Chapter 5 秒动态完整重放 Aha 核心 2 秒，不能因 interval 不完全相等逃避避重。已加入 `MATERIAL_TEMPORAL_OVERLAP`。

### R4｜Aha Primary 与 B3 Route order 不为软偏好改写

跨 Memory 避重只能在已有 no-loss Chapter projection 中发生；不主动降级 Aha、不激活 Fallback，也不在 failure 后跳过语义更优 Route。

## 9. 交叉检查结论

~~~text
36 / 36 cases = expected deterministic outcome
14 / 14 invariants preserved
4 refinements applied
0 S09 membership changes inside S10
0 active fallback used for aesthetic dedupe
0 new model/HQ/upload/user-interaction requirements
~~~

**结论：** S10-D4 通过内部合同检查，并已参加后续 S10-E 全链路检查。D4.1–D4.2 已由 Canonical V1.21 冻结。

该检查不证明真实用户对重复画面的容忍度、no-loss 判定准确率或 Production 实现性能；这些仍需后续标签与真实数据 Benchmark。
