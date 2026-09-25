# Diary One Canonical Checkpoint V1.22 — S11 Grounded Narrative & Memory Index

**状态：** FROZEN FOR V1.0 CURRENT-CHINESE TEST PROFILE
**冻结日期：** 2026-08-29
**覆盖阶段：** S11-A–F
**继承：** V1.19 S09、V1.20 Chapter/Aha Narrative Independence、V1.21 S10 EvidenceAnchor & Media Editorial，以及 S11 working document 中已经确认的 A–D 合同
**仓库边界：** 只覆盖 Cloud Intelligence 算法与接口；不修改 App、Firmware/SDK 或共享状态文件

## 1. 冻结结论

S11 的任务是把已经由 S09 选定、由 S10 建立最终媒体投影的 Memory，转换成：

```text
完整且分角色的 ChapterFacts / AhaFacts
→ 可逐项验真的 Claim Ledger
→ 有界 Narrative Content Plan
→ grounded Title / Story / Moment Line / Time Label
→ CanonicalTagDecision + EntityIndexLinks
→ actual-language verification
```

它不是自由写作层，也不是第二个 Candidate/Selection/Media Agent。

本检查点冻结以下主干：

1. Chapter 默认一句、最多两句；文字直接呈现场景、动作、变化或克制氛围，不解释算法为什么选素材。
2. Chapter Title 当前中文测试目标为 2–10 个可见字符；确有语义必要时可软延伸到 11–12，禁止截断或填充。
3. Aha 只有一条 `MOMENT_LINE`，当前中文测试不超过 20 个可见字符；必须围绕单一 peak。
4. 每个事实、关系、限定词与实际文字 span 都必须回到 Claim/Evidence；多个真事实组合后仍要验证整体语义。
5. Chapter 与 embedded-but-distinct Aha 可以处于同一时间线，但必须拥有不同故事职责；同一生日高潮不能重复生成 Aha。
6. Canonical Tag 使用受控、语言无关、可版本迁移的分面体系；精确地点、人物和宠物身份进入 typed Entity Link，不冒充普通 Tag。
7. Writer 只消费已批准的 Content Plan；模型/provider 故障不能变成事实变化，也不能用万能句补齐。
8. S11-E 对最终实际文字做发布前验证；S11 自己不宣布 Diary 已可发布，最终权限属于 S12。

## 2. S11 输入与输出合同

### 2.1 必需输入

- current immutable Revision 与 DailyInputSnapshot；
- S09 SelectedMemorySet、Day State proposal、lineage 与 Chapter/Aha pair decisions；
- S10 active final media projection、Hero、EvidenceAnchor、HQ request intent 与 limitations；
- S04–S08 已验证 Facts、relations、Evidence refs 与 failure/unknown states；
- prior published generated surfaces 与 protected user text（若存在）；
- locale、voice、taxonomy、model、prompt 与 parameter policy refs。

### 2.2 正式输出

```text
S11NarrativeBundle
  revision_id
  snapshot_id
  locale_profile_ref
  memory_outputs[]
    ChapterFacts | AhaFacts
    ClaimLedger
    NarrativeContentPlan
    GroundedNarrative
    D5IndexDecision
      CanonicalTagDecision[]
      EntityIndexLink[]
    DisplayLabelCandidate[]
    ProtectedUserTextRef[]
    SurfaceVerificationDecision[]
  writer_provenance
  validation_provenance
  immutable fingerprint
```

### 2.3 S11 没有的权限

- 不改变 S09 membership、Day State 或数量；
- 不把 S10 `CONTEXT_ONLY`/外围素材升级为正文；
- 不新增 Evidence、人物关系、地点、情绪、意图或因果；
- 不请求 Auto 另外两帧，不搜索全天 Raw，不触发 HQ；
- 不覆盖或重写用户自己的文字；
- 不发布、不更新 published head、不把失败伪装成 EMPTY_DAY。

## 3. D5｜Canonical Memory Index

### 3.1 V1 分面集合

V1 冻结四个 Canonical Facet：

| Facet | 回答的问题 | 合法例子 | 不进入这里的内容 |
|---|---|---|---|
| `ACTIVITY` | 这段记忆主要在做什么 | CITY_WALK、POTTERY | 一次性细动作、用户意图 |
| `SETTING` | 核心环境是什么 | HISTORIC_DISTRICT、HOME | 精确店名、GPS 地址 |
| `CENTRAL_SUBJECT` | 主要在看/记录什么类别 | CAT、HISTORIC_ARCHITECTURE | 具体宠物姓名、路过对象 |
| `OCCASION` | 是否属于可复用的明确场合 | BIRTHDAY、TRAVEL_OUTING | 凭氛围猜节日、日常时间段 |

以下信息明确不作为 V1 Canonical Facet：

- exact Place/Person/Pet/Venue：进入 `EntityIndexLink`；
- Time、Memory Type、Capture Type、Revision：进入确定性 metadata；
- Theme：由 Claims、Tag、Entity、时间和 embedding 在 query-time 组合，不固化为模糊主题词；
- Mood：没有用户确认时不建立；即使确认，也属于独立用户事实/检索信号；
- Preference：Tag frequency 不能直接生成“喜欢”；偏好系统必须拥有独立证据合同；
- 一次性长尾动作：保留在 Claim、Moment Line 与 embedding。

**案例：** “周庄古镇漫步”可以同时得到 `ACTIVITY.CITY_WALK`、`SETTING.TRADITIONAL_HISTORIC_DISTRICT` 与 `PlaceEntity=周庄古镇`。用户搜“周庄”走实体索引，搜“古镇街巷”走 Setting，搜“散步”走 Activity。

### 3.2 Registry 合同

每个 active Concept 至少包含：

```text
concept_id                 # locale-neutral, immutable identity
facet
semantic_definition
parent_id?
active / deprecated state
locale_labels{}
safe_aliases{}
introduced_registry_version
migration_target?
```

规则：

1. Runtime 只能选择 active concept、合法 safe parent 或零结果，不能自由造词。
2. 一个 concept 只属于一个 Facet；parent 必须同 Facet，层级无环。
3. 默认只保存最具体且被 Evidence 支持的 concept；parent 仅在 query-time 展开。
4. `UNKNOWN/OTHER`是处理状态，不进入长期索引或用户画像。
5. label 可随 locale 更新；semantic definition 改义必须新 concept 或显式 migration。
6. registry 更新不能静默重解释既有历史 Assignment。

**案例：** Evidence 只能证明“在做手工”时可分配 `ACTIVITY.CRAFT`；不能因为画面里像泥土就猜 `ACTIVITY.POTTERY`。若明确看到拉坯，则保存更具体的 POTTERY，搜索“手作”由 parent expansion 找回。

### 3.3 Assignment 数量与质量门

每个 Chapter/Aha 都必须执行 Tag Decision，但允许零 Assignment。

V1 internal baseline：

```text
0–4 CanonicalTagAssignment / Memory
每个 Facet 0–1
有 Assignment 时恰好 1 个 PRIMARY，其余为 SECONDARY
只使用 STRONG 或可独立成立的 MODERATE support
每项必须引用 current Claim + Evidence + Revision
```

0–4 是四分面带来的内部可解释上界，不是 UI chip 配额。不得为了填满四项强塞泛词。

排序固定为：

1. 与 Memory identity 的中心性；
2. Evidence/Claim 支持强度；
3. 已支持范围内的 specificity；
4. 检索区分度；
5. 与已选 Assignment 的非重复增量；
6. stable concept ID tie-break。

**案例：** 古镇 Chapter 可以把 `CITY_WALK`设为 PRIMARY，传统街区和传统建筑为 SECONDARY。途中出现一次普通茶杯，不获得 `FOOD_OR_DESSERT`，因为它不决定该 Chapter 身份。

### 3.4 Chapter 与 Aha 分别判断

Tag 不能在 Chapter 与 Aha 之间自动继承。

**案例：** 古镇 Chapter 与“猫碰倒纸杯”的独立 Aha 共存。Chapter 可以是 CITY_WALK/HISTORIC_DISTRICT；Aha 可以是 CAT/CAFE。Aha 不因为嵌在古镇时间线就继承 TRAVEL_OUTING，Chapter 也不因为 Aha 有猫就获得 CAT。

### 3.5 Display Label

Canonical Assignment 与用户展示分离：

- 算法输出 0–2 个 `DisplayLabelCandidate`；
- 只从当前 locale 的 registry label 派生，不允许 Writer 自由改写；
- 缺少 locale label 时只省略展示候选，不删除内部 Assignment；
- App 是否展示、放在哪、是否允许用户关闭，属于 App presentation 合同；
- UI 数量不反向限制内部 0–4 Assignment。

当前 `0–2` 是保守的交接上界，不意味着 App V1 必须显示两个标签。

### 3.6 Entity Index Link

每条 Entity Link 必须保存：

```text
entity_id
entity_type = PLACE | PERSON | PET | VENUE | OTHER_NAMED_ENTITY
verified display name
Claim refs
Evidence / user-confirmation refs
Revision / provenance
permission / protection refs when applicable
```

**案例：** “豆包”是已确认宠物实体，存为 `PET` link；“猫咪”是 class-level Central Subject。两者可联合检索，但不能把所有用户的“妈妈”“豆包”写进共享 taxonomy。

### 3.7 Cross-Revision 与 migration

1. active projection、Claim 与 semantic definition 未变时 exact retain；
2. label 改变不等于 Assignment 改变；
3. Fact 失效或 Memory identity 改变时重新决策；
4. concept split 时不能猜 child，缺少新证据时保留合法 parent 或零结果；
5. deprecated concept 使用 versioned migration record，不原地改历史；
6. UI 文案变化不触发索引抖动。

### 3.8 检索与数据价值

V1 采用 hybrid retrieval：

```text
exact Entity filter / match
+ Canonical Facet match and ancestor expansion
+ deterministic time / memory metadata
+ Claim / protected searchable text
+ embedding semantic recall and rerank
```

Tag 是可解释索引，不承担所有召回；embedding 是相似性信号，不是事实。任何频次都只表示记录分布，不能自动变成用户偏好。

### 3.9 D5 成本

D5 不新增 Raw/HQ 上传，不要求新的 VLM 调用。它消费 S11 已验证 Facts/Claims，通过 closed-registry mapping 与确定性 validator 完成；主要成本是小型 metadata、registry lookup、索引写入和 migration audit。

## 4. D6｜Writer Runtime & Cost Envelope

### 4.1 Writer 的输入边界

Writer 只接收：

- current Memory 的 B3-validated Content Plan；
- exact Claim/relation/qualifier refs；
- active S10 media projection summary 与 limitations；
- current locale/voice/length policy；
- protected user-text instructions；
- prior generated surface（仅 continuity 适用时）。

Writer 不读取全天 Candidate 池，不自行看 Raw，不创建 Tag，不决定地点 lookup，也不改变 Content Plan。

### 4.2 Structured output

每个 logical attempt 必须返回结构化对象：

```text
surface_text
span_to_claim_refs[]
span_to_relation_refs[]
tone_permission_refs[]
protected_text_actions[]
provider / model / prompt / parameter refs
input/output token count
latency / retry / cache / cost provenance
```

缺字段、引用不存在、额外 surface 或自由 Tag 均为 contract invalid，不把裸文本送给用户。

### 4.3 有界 attempts

继承 D4c2 已冻结的四级单调简化路径。每个适用 attempt class：

- 最多一个 logical provider call；
- 只落一个 canonical draft；
- 相同 exact fingerprint 命中 cache，不再次调用；
- provider transport retry 必须有限、配置化并单独计数，不能创造第五个语义 attempt；
- 新 Revision 只有在 Content Plan/policy fingerprint 改变时才重置语义路径。

高强度 Final 的绝对逻辑上界：`(Chapter + Aha) × 4`，即最多 `8 × 4 = 32` 个语义 attempt；这是极端失败包络，不是日常目标。正常路径每个 Memory 预计一次通过。Tag、Time Label、continuity aggregation 和 S11-E 不调用 Writer。

### 4.4 Provider failure 与预算

- exact valid prior 可依法 retain 时继续保留 prior；
- transient/provider failure 进入 HOLD/retry，不改成内容不足；
- 所有有界 attempts 用尽且无安全 prior 时返回 `NARRATIVE_CONTENT_BLOCKED` 或 owner replan；
- 不生成“记录美好生活”等万能句；
- 运行必须接收 versioned day/run budget policy；预算耗尽停止新调用并保留真实状态；
- 在真实 provider 价格、cache hit、Token 与用户频次 benchmark 前，不冻结美元承诺。

## 5. E｜Actual-language Verification

S11-E 在 Writer 之后、S12 之前执行。它不相信“Prompt 已要求真实”，而是验证实际输出。

### 5.1 验证顺序

1. Revision、snapshot、policy、plan 与 projection fingerprint 一致；
2. 每个事实 span 能映射到 current supported Claim；
3. 每个关系词、先后词、数量词、否定词与程度词有独立许可；
4. 代词/省略主语只有一个合法 referent；
5. Chapter Story 为 1–2 句、默认一句、第二句有材料增量；
6. Aha 是单峰，中文当前测试不超过 20 个可见字符；
7. Title、Story、Time、Tag 的重复只保留功能性必要重叠；
8. selected Aha peak 不被 Chapter 重新写成高潮/结果；
9. light-affect 只能使用 versioned窄许可，如“猫咪调皮”“小狗活泼”，并绑定实际动作 Claim；
10. “幸福、难忘、惊喜、好吃、最爱”等用户状态/评价没有用户确认时阻断；
11. protected user text 未被覆盖、删除、冒充或静默转述；
12. locale length、punctuation、display 与 release gate 通过。

### 5.2 终态

```text
SURFACE_VERIFIED
SURFACE_REWRITE_SAME_PLAN_REQUIRED
OWNER_REPLAN_REQUIRED
NARRATIVE_CONTENT_BLOCKED
NARRATIVE_CONTRACT_INVALID
```

只有 `SURFACE_VERIFIED` 可以交给 S12。局部改写只能在 Claim/relations/plan 完全不变时进行；需要删 Claim、换关系或改变信息职责时必须返回 owner，不能由 E 静默修补事实。

### 5.3 案例

| 实际文字 | 结果 | 原因 |
|---|---|---|
| `石板路连着旧屋，走到河边时，晚光落在水面。` | PASS（证据齐全时） | 场景、推进、光线分别可追溯 |
| `牌坊和木雕构成了上午的主要画面。` | REWRITE | 在解释算法选材，表达呆板 |
| `你在最爱的古镇度过了悠闲上午。` | BLOCK | “最爱”“悠闲”推断偏好与内心状态 |
| `小猫调皮地碰倒了纸杯。` | PASS（窄许可） | 动作有证据，“调皮”只作猫行为的共识性轻表达 |
| `猫碰倒纸杯，留下难忘一刻。` | BLOCK | “难忘”是用户评价，没有依据 |

## 6. F｜S11 Cross-check

### 6.1 跨阶段检查

| 连接 | 结论 |
|---|---|
| S09 membership → S11 | PASS：S11 不增删/替换 Memory |
| V1.20 reservation → Chapter/Aha wording | PASS：same-story climax 不重复，embedded-distinct 可独立表达 |
| S10 active projection → Claims | PASS：文字必须兼容 active/fallback/D1 后投影 |
| Claim Ledger → actual spans | PASS：每条事实、relation、qualifier 独立验真 |
| D3 Time Label → continuity | PASS：确定性 surface 不交给 Writer |
| D5 Tag → exact place/person/pet | PASS：typed Entity Link 分流，不丢检索资格 |
| D5 → future personalization | PASS：内容索引不冒充偏好 |
| D6 failure → Day State | PASS：provider failure 不伪装 EMPTY_DAY |
| S11 → S12 | PASS：只交 verified artifact，不自称 publish-ready |
| localization → overseas release | PASS：中文数字不机械套用英文 |

### 6.2 用户画像检查

1. 旅行者：长时间古建筑 Chapter 可分配 CITY_WALK/HISTORIC_DISTRICT/ARCHITECTURE；不同建筑由 S10 媒体表达，不把每座建筑造一个 Tag。
2. 家庭记录者：生日 Chapter 获得 BIRTHDAY；吹蜡烛若是同故事高潮，不再成为 Aha。
3. 手作爱好者：POTTERY 可作为 Activity；“完成作品”必须有 outcome Evidence。
4. 宠物记录者：CAT/DOG 与 exact pet Entity Link 分离；轻情绪词不能扩大事实。
5. 美食用户：FOOD_OR_DESSERT 可描述内容，不推断“好吃”。
6. 上班族：普通通勤/办公室不足以凑 Chapter，也不为覆盖率强塞 Tags。
7. 稀疏高光日：单一 standalone Aha 可形成 HIGHLIGHT_DAY；Aha 不生成小型 Chapter Title/Story。
8. 多次 Sync 用户：新增 Revision 优先 retain 仍合法文字和索引，不因同义词随机改写。
9. 用户自写标题：非空 protected user Title 获显示所有权，AI 不并排争夺；用户清空后不自动复活。
10. 海外用户：未释放 locale 不继承中文字符数上线，返回 locale release not ready。

### 6.3 冻结不变量

1. Facts 完整账本与短文案分离；
2. Claim 真值与 surface permission 分离；
3. 多个真 Claim 不自动组成真句子；
4. Chapter 默认一句、最多两句；
5. Aha 单峰、单句、无 generated Title/Story；
6. Time Label 为确定性 surface；
7. 用户文字不可被覆盖；
8. Tag 可为零、不可自由生成；
9. 四 Facet 各最多一项；
10. Entity 不污染 taxonomy；
11. Display Label 不限制内部索引；
12. Tag 不等于偏好；
13. Writer 不改变 plan；
14. Provider failure 不改变事实/Day State；
15. actual wording 必须再次验证；
16. runtime media activation 后必须重验 affected artifacts；
17. prior continuity 不保护已知错误；
18. S11 不发布、不更新 head；
19. current Chinese test profile 与海外 release 分离；
20. 所有对象 immutable、versioned、可审计。

## 7. 状态边界

### 7.1 FROZEN

- S11 A–E 的事实、Claim、composition、surface、continuity、中文 Title/Story/Time/Aha、D5、D6 与 actual-language verification 主干；
- 四 Facet、typed Entity Link、0–4 internal Assignment、0–2 Display Label Candidate；
- closed registry、most-specific supported assignment、query-time ancestor expansion；
- Writer structured output、有界 attempt/cache/cost provenance；
- S11 closeout cross-check 与本文件 20 条不变量。

### 7.2 显式 deferred / OPEN

- D2e：Title 无法安全生成或用户清空后，Production 最终 presentation/fallback；当前不自动删除或阻断 Chapter；
- English 与其他 locale 的 Title/Story/Moment Line 数量、折行、无障碍、eval set 与 release gate；
- 真实 concept coverage、mapping threshold、taxonomy expansion 与 human-label calibration；
- 实际 Writer provider/model/prompt、Token、价格、P50/P95/P99 时延与 retry 数值；
- 用户文字除 Title 外的 App 并排/替代/编辑 presentation；
- embedding model、search ranking、personalization 与完整 Knowledge Graph；
- 隐私、伦理、retention 与对外数据政策。

这些 OPEN 项不推翻 S11 的架构冻结，但会阻止对相应海外 locale、成本数字或完整云端 Production readiness 作出承诺。

## 8. 实现证据

本仓库提供：

- `contracts/canonical_concept_registry_v1.json`：closed seed registry；
- `contracts/production_pipeline_v1.schema.json`：全流程输入 schema；
- `src/diary_one_ci/production_v1.py`：D5 mapping、S11 surface/Claim gates 与两阶段发布参考；
- `fixtures/production_v1/ancient_town_reference_day.json`：古镇 Chapter＋独立宠物 Aha 案例；
- `tests/test_production_v1.py`：正向、actual-text span、Writer provenance、错误 Claim、自由 Tag、Tag facet、Aha wording、数量、pair、fallback 与 HOLD 测试。

实现只证明合同可执行与错误可阻断；它不代表真实模型准确率、HQ 渲染、云服务或 App 已完成。

## 9. Freeze Record

S11 至此形成 V1.0 current-Chinese test 的完整冻结合同。后续 S12 必须把 `S11_READY_FOR_S12` 当作发布前输入，而不能自行删 Claim、改文字或重建 Tag。任何真实数据反证通过新 versioned checkpoint 修订，不能静默改写本文件。
