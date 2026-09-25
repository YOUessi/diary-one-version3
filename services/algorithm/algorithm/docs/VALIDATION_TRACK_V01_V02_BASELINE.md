# Diary One Validation Track V01–V02 Baseline

**状态：** DESIGN-GOLD CONFORMANCE PASSED / REAL-MEDIA ACCURACY NOT CLAIMED

**日期：** 2026-08-29

**继承：** Canonical V1.1–V1.25 与 S00–S13 Production-shaped V1.0

**本轮范围：** 评分协议、Gold Label 合同、确定性评估器、细粒度语义日案例

**明确排除：** Firmware/SDK、正式 App、共享状态文件、真实媒体理解、外部模型、云部署、真实成本与准确率结论

## 1. 它位于全局流程的哪里

```text
冻结的产品与算法合同 S00–S13
              ↓
V01：先定义“怎样才算对、错在哪里”
              ↓
V02：用高概率用户日与故障案例验证规则是否自洽
              ↓
V03+：真实素材、人工标注、模型与阈值校准
              ↓
Production engineering：云服务、队列、存储、监控、成本与发布
```

V01–V02 不重新设计 Pipeline，也不拿模拟语义代替真实素材实验。它们先建立一把稳定、可追责的尺子，避免未来更换模型或阈值时，只凭“看起来不错”判断。

## 2. V01 回答什么

V01 只回答四件事：

1. 一个用户日案例必须提供哪些输入证据和 Gold Label；
2. 两个 Memory 即使 ID 或文案不同，怎样判断它们表达的是同一段经历；
3. 错误属于事实阻断、质量问题，还是必须交给人判断；
4. 如何生成可复跑、可定位问题、但不制造虚假总分的 Scorecard。

### 案例

古镇 Chapter 的预测 ID 从 `D01-P-CH1` 改成 `RENAMED-0`，只要它仍然是 Chapter、覆盖同一时间段，并包含 `ancient_town_walk` 身份证据，就仍然匹配。评估器不会因为内部 ID 不同误判失败。

## 3. 为什么不设一个“总分”

以下结果不可相互抵消：

| 类别 | 含义 | 案例 | 处置 |
|---|---|---|---|
| `BLOCKING` | 事实或产品不变量被破坏 | 把通勤和办公误合成同一 Chapter；凭食物外观写“好吃” | 不允许发布该结果 |
| `QUALITY` | 没有造假，但编辑质量不足 | 同一古镇主线被切成两个 Chapter；少了一张关键素材 | 进入算法调整或重选 |
| `REVIEW` | 证据允许多种合理产品选择 | 公园吹泡泡是否值得独立成为 Aha | 交给人工/用户测试，不擅自冻结 |

如果把它们加权成一个总分，多个“素材选得好”可能掩盖一次 False Memory。V01 因此只输出互相独立的维度、问题代码和数量，不输出 compensating overall score。

## 4. 六个独立检查维度

| 维度 | 检查内容 | 案例 |
|---|---|---|
| `TRUTH` | 所写事实、语义、媒体是否有 STRONG/MODERATE Evidence | 未出现食用反应时，`food_delicious` 阻断 |
| `MEMORY_IDENTITY_AND_BOUNDARY` | Day State、数量、Memory 身份、误拆/误合/漏选 | A–茶店–C 的古镇主线不因短插曲被永久拆开 |
| `CHAPTER_AHA_INDEPENDENCE` | Aha 是否拥有与 Chapter 不同的故事职责 | 生日吹蜡烛属于生日主故事，不再复制成 Aha |
| `MEDIA_EDITORIAL` | Chapter 标准 3–5、严格 Compact 2、Aha 1 项，以及关键素材、重复、Hero、格式、归属 | Aha 恰好 1 项媒体；同一 media_id 不跨 Memory 复用 |
| `NARRATIVE_CONTRACT` | Chapter/Aha 表面合同与中文长度 | Chapter 1–2 句；Aha Moment Line ≤20 可见字符 |
| `MEMORY_INDEX` | Canonical Concept 与 Entity 是否获准 | 不把未注册或未批准的标签写进长期索引 |

这里的文字检查只覆盖可确定的合同。Prediction 中的 `asserted_atoms` 代表已经由 S11 Claim Ledger 从实际正文绑定出的语义主张；V01 检查这些主张是否有证据，但不会从自由文本中重新抽取主张。自然度、是否打动用户、轻情绪词是否合适，以及正文到主张的真实抽取准确性，仍需要人工和真实用户评价。

## 5. Gold Label 合同

每个 Day Eval Case 都包含：

```text
2 分钟语义时间轴
→ STRONG / MODERATE / WEAK / UNKNOWN Evidence
→ Day State 与 Chapter/Aha 数量范围
→ required / optional / forbidden Memory
→ 每个 Memory 的身份原子、可接受时间范围、必要/可选/禁止事实
→ 媒体、Narrative、Canonical Concept 与 Entity 约束
→ 需要人工判断的问题
```

### 两类 Gold 必须分开

| Gold 来源 | 可证明什么 | 可否声称真实准确率 |
|---|---|---|
| `DESIGN_GOLD` | 合同、规则、评估器与案例是否自洽 | 不可以 |
| `HUMAN_ADJUDICATED_GOLD` | 在真实素材和正式标注协议下的算法表现 | 满足至少 2 位独立标注者与 adjudication 记录后，另行报告 |

V02 当前 12 天全部是 `DESIGN_GOLD`，并被合同强制标记为 `accuracy_eligible=false`。因此“16/16 conformance pass”不能改写成“算法准确率 100%”。本版 Narrative 合同还明确限定为 `zh-CN`；英文和其他海外语言必须建立 locale-specific 字数/词数、呈现与评测合同，不能机械复用中文字符限制。

## 6. Memory 等价与对应规则

Gold 与预测不做逐字或逐 ID 比较。一个预测 Memory 进入某个 Gold Memory 的候选对应，必须同时满足：

1. 类型一致：Chapter 对 Chapter，Aha 对 Aha；
2. 至少共享一个 `identity_atom`；
3. 预测覆盖 Gold 可接受时间范围的比例达到该案例门槛；本版默认 50%，避免只有一个两分钟碎片却冒充完整长 Chapter；
4. 多个候选冲突时，确定性地优先满足 required Memory、身份与必要事实、时间重叠。

对应关系只是为了找到“该比较谁”，不是质量分。

### 案例

- `ancient_town_walk + 09:00–10:04` 可以对应古镇 Chapter；
- 只包含 `tea_shop_visit` 的 Memory 不能因时间落在其中就冒充古镇 Chapter；
- 一个预测同时拥有 `morning_commute` 和 `office_work_block` 两个独立身份时，直接记录 `FALSE_MERGE`。

## 7. V02 的 12 个高概率用户日

所有案例都已展开为显式 2 分钟窗口，共 609 个 Timeline Window；JSON 中可逐条查看每个时间点，而不是只写一段故事梗概。

| Day | 用户画像与时间范围 | 细语义变化 | Gold 输出 | Nominal 结果 |
|---|---|---|---|---|
| D01 | 旅行 citywalk，09:00–10:02 | 牌坊→石板路→木雕→茶店→小猫跳桌→回古街 | 1 古镇 Chapter + 1 独立小猫 Aha | PASS |
| D02 | 家庭生日，18:00–18:40 | 晚餐→蛋糕→吹蜡烛→掌声→分蛋糕 | 1 生日 Chapter，0 Aha | PASS |
| D03 | 徒步，07:00–08:00 | 林道→爬坡→山脊→彩虹→下山 | 1 徒步 Chapter + 1 彩虹 Aha | PASS |
| D04 | 普通工作日，多段稀疏采集 | 地铁→重复工位→会议室→地铁 | EMPTY_DAY | PASS |
| D05 | 稀疏手动采集，19:30–19:56 | 晚餐→甜点→戒指出现与拥抱 | HIGHLIGHT_DAY，恰好 1 Aha | PASS |
| D06 | 周末美食，11:00–12:30 | 市场→热汤面→街边小吃→共享餐桌→甜点 | 1 美食 Chapter，不推断“好吃” | PASS |
| D07 | 居家宠物，09:00–11:00 | 打盹→窗边→追线团→窗边→再打盹 | 1 Chapter，控制重复素材 | PASS |
| D08 | Manual 陶艺，14:00–15:30 | 揉泥→拉坯→刻纹→上釉→未完成泥坯 | 1 过程 Chapter，不写“做完” | PASS |
| D09 | 都市工作社交，08:00–18:30 | 通勤→办公/会议→朋友晚餐 | 3 个相互独立 Chapter | PASS |
| D10 | 博物馆，10:00–13:00 | 入口→雕塑→画廊→休息→文物→出口 | 1 长 Chapter，保留不同展厅方面 | PASS |
| D11 | 家庭公园，15:00–16:20 | 林荫路→野餐→追泡泡→游乐场→离园 | 1 Chapter；泡泡 Aha 暂列 optional | REVIEW |
| D12 | 两次 Sync，06:30–07:30 / 20:00–21:20 | 晨跑一批→晚间演出一批 | 2 独立 Chapter，不因多批次混合 | PASS |

### D01 的关键连续性案例

```text
09:00–09:30  古镇入口、石板路、古建筑、木雕
09:32–09:36  进入现代茶饮店
09:38–09:46  小猫跳上桌，形成独立峰值
09:48–09:52  饮品与甜点，插曲收束
09:54–10:02  回到古街与石板路
```

处理结果：茶店插曲不会让前后古镇主线永久 split；小猫动作因为有独立故事职责，可单独成为 Aha；Chapter 与 Aha 互相禁止借用对方的核心语义。

### D09 的三段边界案例

```text
08:00–08:30  通勤
09:00–12:00  办公与会议
18:00–18:30  朋友晚餐
```

处理结果：时间连续性、身份原子和故事职责均不同，应形成 3 个 Chapter。把通勤和办公合成一个 Memory 会触发 `FALSE_MERGE`，即使文案读起来通顺也不能通过。

### D11 唯一保留的产品判断

“孩子追泡泡”可能只是家庭公园 Chapter 中的一段，也可能对部分用户有足够独立价值成为 Aha。V02 没有替用户冻结答案，而是将其标记为 `OPTIONAL_REVIEW`；当前 nominal 输出不强制生成 Aha，因此整体状态是 REVIEW 而非失败。

## 8. 四个故障注入

只让正常案例通过，无法证明评估器真的会抓错。本轮额外注入四类典型错误：

| Trial | 故意制造的问题 | 预期级别 | 实际归因 |
|---|---|---|---|
| T-D01-FALSE-SPLIT | 古镇主线在茶店前后被拆成两个 Chapter | QUALITY | `FALSE_SPLIT` 命中 |
| T-D02-SAME-STORY-AHA | 吹蜡烛同时作为生日 Chapter 高潮和独立 Aha | BLOCKING | `SAME_STORY_AHA` 命中 |
| T-D06-UNSUPPORTED-TASTE | 仅凭食物画面写入 `food_delicious` | BLOCKING | `UNSUPPORTED_ASSERTION` 命中 |
| T-D09-FALSE-MERGE | 通勤与办公被合成一个 Chapter | BLOCKING | `FALSE_MERGE` 命中 |

预期 Error Code 使用“必须包含”而非“必须完全相等”：一个错误可能同时导致数量不足、遗漏 Memory 或媒体缺失，评估器应完整保留这些连带结果。

## 9. 运行结果

```text
12 Design-Gold days
609 explicit two-minute timeline windows
16 trials total

Nominal references:
  11 PASS
   1 REVIEW

Failure injections:
   1 QUALITY_FAIL
   3 BLOCKING_FAIL

Expected status/error attribution:
  16 PASS
   0 FAIL

Accuracy claim:
  NOT_ELIGIBLE_DESIGN_GOLD_ONLY
Overall score:
  deliberately absent
Frozen S00–S13 mutation performed by validation run:
  false

Input fingerprint:
  1f6886fce43968607fae756b1a8e4c210eee975ced4b8e81067d1c631cc4c315
Scorecard fingerprint:
  e5269b860709fb82e7e8c94790834047b098a9627890fa3761f9845277f2378d
```

## 10. 可运行资产

| 资产 | 用途 |
|---|---|
| `contracts/day_eval_case_v01.schema.json` | 单个用户日与 Gold Label 的 JSON 合同 |
| `contracts/validation_suite_v01.schema.json` | 多日、多 Trial 输入合同 |
| `contracts/validation_scorecard_v01.schema.json` | 评估结果合同 |
| `fixtures/validation_v01/semantic_day_suite_v01.json` | 12 日、609 Window、16 Trial 的版本化 fixture |
| `src/diary_one_ci/validation_v01.py` | 合同校验、对应、问题归因与 Scorecard |
| `src/diary_one_ci/validation_cases_v01.py` | 可重复生成 reference suite 的源定义 |
| `tests/test_validation_v01.py` | 合同、反例、确定性、标签注册表与输出测试 |

运行：

```bash
PYTHONPATH=src python3 -m diary_one_ci.cli validation-v01 validate fixtures/validation_v01/semantic_day_suite_v01.json
PYTHONPATH=src python3 -m diary_one_ci.cli validation-v01 run fixtures/validation_v01/semantic_day_suite_v01.json --artifacts artifacts
```

## 11. 本轮能与不能得出的结论

可以得出：

- 冻结的关键产品规则能够被表达为版本化、可执行的日级验证合同；
- 正常、误拆、误合、同故事重复 Aha、无证据主观推断可被分开归因；
- Chapter/Aha、媒体、文字合同、Canonical Index 不再只靠人工阅读文档检查；
- 模拟案例中唯一真正需要产品判断的泡泡 Aha 已显式保留为 REVIEW，没有被技术默认值掩盖。

不能得出：

- 真实素材下的 Chapter/Aha precision、recall 或用户满意度；
- S00–S10 真实引擎已实现或模型已能稳定产出这些结果；
- Writer 自然度、英文/多语言质量、手机能耗、云成本、延迟已达标；
- 可以进入云端 Production。

## 12. 下一验证门

V03 应使用获得授权的真实 wearable 素材，不再用设计语义替代感知：

1. 固定数据纳入、脱敏和版本规则；
2. 至少两位独立标注者按 V01 合同标注，再做 adjudication；
3. 先测 Evidence/Observation/Moment，再测最终 Chapter/Aha，避免只看最终结果而无法归因；
4. 同时记录真实模型调用、上传量、P50/P95 延迟和每用户日成本；
5. 只有 Human Gold 报告可以讨论真实准确率，且 Blocking/Quality/Review 仍分别呈现。

V03 不需要推翻 V1.0 Pipeline；它用真实证据校准阈值、模型与局部策略。
