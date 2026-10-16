# codex · V1.35 — 模型负责内容分组，标签退出内容裁决

日期：2026-09-03。状态：LOCAL_IMPLEMENTATION_AND_TECHNICAL_CHECKS_COMPLETE；未接入 Web、未执行新的真实素材全链路测试，不是质量验收。

## 已确认的范围

用户同意：保留 Canonical Tag 的描述、检索与数据价值；由现有一次 Structure 模型调用组织 Chapter 候选，程序只检查明确的素材、引用、容量和使用约束，不以粗标签代替内容关系判断。本轮只修改算法仓库，不改 Web、Firmware/SDK、正式 App、共享状态，不调用云端模型，不调画质/事实支持等权重或用户可见文案要求。

真实依据：第二步核查记录中的 Person 2 混合 Chapter，其成员包含鹿、相机、公路和餐车。问题在于程序用共同粗分类生成分组，而非已经验证过它们属于同一段体验。参见 [第二步核查](codex_REVIEW_02_CLASSIFICATION_CLUSTERING_SCORING.md)。本轮不增加虚构语义错误、场景例外或关键词规则。

## 修改前基线（已核对，无漂移）

- HEAD：`8b79fb7faa4981cf352551e4f15dff24c92a3a7e`；分支：`codex/validation-v01-v02-20260829`。工作区已有未提交修改，本步保留。
- `src/diary_one_ci/x02.py`：`964881f549ec2ab42b96892e0484b4dac35c1402080cf3dd4b433b5e1734cbaf`。
- `src/diary_one_ci/contracts/x02_storyline_v02.json`：`1d8f4d2edb0810fe7fce72b0aac8bbd0e3d6a849dbdad1266f5617cf05693ecd`。
- `contracts/x02_staged_preview_v04_1.schema.json`：`e0a774e6fce581c9f3903945852092a7a27094b6b0b70f5c1cb08db132c95776`。

## 实现边界与前后依赖

1. 不再生成按主题标签、Episode 类别或数量均分拼出的 Chapter 候选；只消费模型提案。不新增模型重试。合法空提案也不以粗标签补齐。
2. 不给模型预先计算允许的主题列表，不要求八种主题之一；不按主题强制改写模型的组织方式。保留既有成员、事实、Beat 引用与可用性检查，模型的归组说明不再被固定标签拼接句覆盖。
3. 同标签不能证明重复，异标签不能证明独立。撤回 Chapter 对比中的标签冲突、标签多样性奖励，以及同一依赖在 Aha 排序中的标签独立性项；保留原始素材不可重复使用等明确约束。既有质量评分权重和位置阈值不重新校准。
4. 当前导入顺序不等于拍摄时间。分组中的导入跨度、穿插数仅作诊断，不按它们或 Episode 标签重新切分模型分组。两成员的互补意义交给模型；程序仍检查两成员及支持事实，不用不同词面证明不同内容。
5. 程序输出的通过仅代表结构/引用通过，不是语义正确。模型失效不应产生伪造的标签兜底 Chapter。Aha 搜索不依赖某个素材先进入 Chapter；Aha 自身候选、去重、评分的其他逻辑不扩展重做。

旧 V1.34 与 Storyline V02 文件作为历史保留。新语义合同使用 Storyline V03 与独立 Schema 文件，不能伪报成已接入 Web 的版本。Web 本来尚未接入 Writer V02，本轮仍不部署。

## 接口与兼容性

- 当前传输路径/结果大版本仍为 X02 V04.1；其中的 `storyline_contract_version` 明确升级为 `DIARY_ONE_X02_STORYLINE_V03`。Writer 继承 V1.33 的 V02，不另增版本号。
- 新合同：`src/diary_one_ci/contracts/codex_x02_storyline_v03.json`。新输出 Schema：`contracts/codex_x02_staged_preview_v04_1_storyline_v03.schema.json`。旧 Storyline V02 与旧输出 Schema 保留为历史，不偷偷改写。
- `focus_code` 不再为必填八选一；兼容入口可接收字符串注记，未提供则输出空字符串。它不影响候选 ID、归组、重复判断或排序，也不是新的 Canonical Tag。素材的 Canonical Tag 与事实保留。
- 模型选择的 `storyline_basis` 不再按类别改写；`beat_map.contribution` 原样去除首尾空白后保留。`reason` 保存在候选账本的 `model_grouping_reason`，不按其中关键词验证内容关系。
- 旧字段名 `one_story_gate` 保留为诊断容器，但新增明确范围 `STRUCTURE_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION`；程序不再将其 PASS 宣称为内容正确。导入位置统计继续记录，`split_challenge` 标记为 `NOT_PROGRAMMATICALLY_EVALUATED`。
- 相同成员的候选 ID 不再取决于标签或导入次序。它是研究版本的候选 ID 迁移，不声称跨旧版本发布状态可以直接复用。
- 本步没有删除上游“双向证据账本 + 四状态”架构；只停止把粗标签与不可信时间的导入跨度当成 Chapter 分组证明。上游 Moment 在结构模型中是上下文，不是强制 Chapter 边界。

## 技术验证与测试范围

| 检查 | 结果 | 证明范围 |
|---|---|---|
| X02 相关检查 | 70 项通过 | 当前和历史接口、引用、字段、版本、模型分组传递、结果 Schema |
| 素材导入合同检查 | 14 项通过 | 本步未破坏导入合同 |
| X01/服务与审计检查 | 20 项通过；1 项本机端口检查因权限跳过 | 版本与审计逻辑；不代表已部署 |
| `git diff --check` | 通过 | 文本格式 |

总计 104 项通过、1 项跳过。没有为了本步额外申请端口权限，没有启动或重启用户测试服务，没有新增 API 调用和模型 token 支出。

新增 8 项技术检查使用旧真实日志的两组成员引用与七份素材事实记录，或纯字段/ID 操作。原模型 thesis 和 Beat Map 并未留存，因此测试不编造它们；需要结构时使用明确标注的空文本或 ID 支架。标签字符串与导入位置变更只检查“这些字段不能暗中改变分组权力”，不标记某个虚构画面语义为正确/错误。

检查覆盖：模型成员集合不被自动候选替换；空提案不产生标签兜底；未归 Chapter 的素材仍进入 Aha 候选检查；组内说明不被标签句覆盖；标签注记不改变候选 ID、候选对关系或排序；重复素材约束仍有效；导入位置不制造拍摄时间；两成员事实支持要求仍有效；一次 Structure 调用仍是一次；输入事实与检索标签仍保留。

退出当前验收的四项旧测试，分别把“混合类别必须被拒绝”“古镇按词表拆三组”“导入跨度触发机械拆分”“词面不同证明两素材互补”作为正确答案。这些不能作为当前内容质量依据。旧 Storyline V02 文件的历史合同检查仍保留。测试网关改为显式给定成员 ID 的接口替身，不实现另一套语义分类器。

## 还没有解决或验证的内容

1. 没有重跑真实图片/视频，不知道新的结构模型会实际怎么分组，也不能把旧成员数据的技术传递称为旧结果已修复。
2. Structure 当前主要读取 Perception 的事实说明；若上游遗漏关键信息，本步无法弥补。抽帧、识图、可用性/角色判断未改。
3. Chapter 质量分仍沿用 40% 画质、30% 事实支持、20% 成员深度、10% Beat 类别多样性，以及原位置阈值。本步仅删除粗主题多样性加分/决策项，未证明剩余公式与满意度相关。
4. Aha 自身候选生成、Aha 之间的现有去重与其余排序未重做；只移除依赖 Chapter 粗标签推算“独立性”的项。当前不能承诺每天必有 Aha，或独立性已经验证。
5. 同一次结构调用被要求比较组间内容关系，但没有额外审查模型。程序的素材不重叠检查也不等于故事必然独立。失败、输出数量、自然表达和满意度要在后续完整运行中评价。
6. 依旧只有本地实现；Web 尚未接入 Storyline V03 / Writer V02。下一步接入 Web 要在授权其修改范围后单独完成，并进行真实素材全流程测试，不能用旧页面评价本次修改。

示例仅解释机制：两组模型候选标签相同但不共享素材时，程序不再直接判重复；标签不同也不额外加分。它们内容上是否值得分成两组，仍由真实素材评价检验，而不是程序凭标签断言。

## 修改后指纹

标识本地工作区，不代表已经提交、同步或部署。

| 文件 | SHA-256 |
|---|---|
| `src/diary_one_ci/x02.py` | `6cdcefdd564502cb11ac282153bc84902cbf7ede11894bed85a7a891ffc2ba1e` |
| `src/diary_one_ci/contracts/codex_x02_storyline_v03.json` | `3da709072857288d1301a56a936d8d03dfd3c1654c88d9d9e09176071180122b` |
| `contracts/codex_x02_staged_preview_v04_1_storyline_v03.schema.json` | `26313706708d07a84d2c1a206623daa1dfed96096953cdc4303ab8817e0d3abb` |
| `tests/test_x02.py` | `62328d6632923c8846bbe9a0938312053262d308a0fd234be3a2e6fca55efedc` |
| `tests/test_codex_x02_model_grouping.py` | `6d84ab44212aab001563a5b7964499c36c3c0b0ca78a91c33159400943e54645` |
| `tests/fixtures/codex_x02_grouping_reference_data.json` | `1850ff1a44726e5487995c65d07b126dee65da85855382c411b406b45150fd6c` |
| `tests/test_codex_x02_thesis_isolation.py` | `0ca35177315ed581a2300ee58ab14c4b5e7279cf84f265ac04e725efa7a4170a` |
| `tests/test_x01.py` | `265ee20201258816991fe093d9763a42d5b09961dfaa1eacc6d6e0252d4bd8a2` |
