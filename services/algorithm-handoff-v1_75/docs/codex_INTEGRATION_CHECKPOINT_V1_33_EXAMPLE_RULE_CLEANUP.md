# codex · V1.33 — 案例硬编码清理（第一步）

日期：2026-09-02

状态：LOCAL_IMPLEMENTATION_AND_TECHNICAL_CHECKS_COMPLETE；未做新的真实素材全流程测试；未接入 Web；不是质量验收。

## 本步的目的与授权

用户指出：猫狗的情绪表达、古建筑的不同侧面、生日的故事重复，都是用来讨论共性问题的例子，不是类别白名单或关键词规则。用户同意先清理已经落地的案例硬编码，不重写整套链路。

本步只修改 `diary-one-cloud-intelligence` 算法仓库。不修改 Web、Firmware/SDK、正式 App、共享状态文件或原始素材；不重启服务、不调用模型 API。不增加人为构造的语义反例。技术检查与真实内容质量评价分开记录。

## 修正前基线

- 分支：`codex/validation-v01-v02-20260829`。
- HEAD：`8b79fb7faa4981cf352551e4f15dff24c92a3a7e`。
- 工作区已有未提交的 V04.1 修改；HEAD 不能代表当前实现。本步保留其他修改，不整文件回退。

| 修正前文件 | SHA-256 |
|---|---|
| `src/diary_one_ci/x02.py` | `158f157923e99d5381ae799cee47eb36afd4bf992401b4b065b98af9b3bd9ce1` |
| `src/diary_one_ci/contracts/x02_storyline_v02.json` | `d5951934fc6349d173a662d9bffbf51189d6005876f37cbb80b098691ba01e5e` |
| `tests/test_x02.py` | `6a8a92a8dd60e0d8540e38ab5210f44ef71aa66dc6b07b64e73ebb07786a6da5` |
| `contracts/x02_staged_preview_v04_1.schema.json` | `38e83afbcb0332692bc01643c4eff22661d539e4992c5db61aefeb7325be3bf6` |

## 撤回什么、保留什么

1. 撤回猫狗专用情绪模板、石板路关键词分支、强制固定标题、模型文案必须逐字复制事实的限制。已有 Writer 调用负责基于素材事实的自然表达，允许克制的氛围表达，但不得编造用户感受、经历或事实。代码只验证明确的格式、长度和引用关系，不能声称因此证明了语义正确。
2. 撤回 Aha 事实必须命中特定主体词、动作词的词表。结构模型引用的事实按引用与支持等级检查，不再由场景词典二次否定。自动候选只是提名，不代表独立价值已被证明。
3. 撤回两素材紧凑 Chapter 仅限文化建筑的类别限制。本步不校准其他数量、质量或去重参数；现有不同内容条件仍是研究实现，不能当作经过用户验证的普适判断。
4. 撤回生日、饮食、宠物、文化等类别专用的 Chapter/Aha 抑制表。只有已有结构模型明确把同一事实用作 Chapter 高潮/结果时，才沿用同一故事核心不重复的约束；自动分组的类别或自动 Beat 标签不能充当这种判断。未确定关系不伪装成已证明独立，留待真实评价。
5. 保留素材与帧引用、支持等级、字数、句数、去重导入、失败隔离、调用预算、输出结构和来源记录等明确合同。失败时只允许复制同一候选中符合长度的完整事实作为朴素兜底，不从类别词典拼接新的内容。

## 与旧记录的关系

- V1.12 的“不得用场景补丁代替通用逻辑”继续有效。
- 本记录取代 V1.32 第 4 节的文化专属两素材例外，以及第 6 节的逐字复制、固定标题和猫狗模板要求；不改写旧记录的历史文本。
- V1.22 中把轻情绪表达具体化为猫狗窄许可的部分，不再作为新研究链路的运行时限制。`production_v1.py` 是历史 reference-only 实现，本步不重写它，也不将其规则重新用于当前真实素材链路。
- 旧 Design-Gold 与语义构造测试不是图片识别质量证据，不得用来为新增场景门槛背书。

## 版本与 Web 边界

传输路由与结果结构仍为 V04.1，Writer 策略明确升级为 `DIARY_ONE_X02_WRITER_SURFACE_V02`，Storyline V02 的内容变化通过合同 SHA-256 区分。

只读检查发现，Web 的 `media-evidence.ts` 和类型定义仍固定要求 Writer V01。因此本步不重启服务、不宣称 Web 已使用新算法；下一小步需要单独完成 Web 的版本接入与验证。不能通过伪报 V01 绕过版本检查。

## 验证与尚未解决的问题

技术检查（2026-09-02，Asia/Shanghai）：

| 检查 | 结果 | 证明范围 |
|---|---|---|
| `PYTHONPATH=src python3 -B -m unittest discover -s tests -p '*x02*.py'` | 62 tests，全部通过 | 当前/历史接口、格式、引用、Schema、状态与清理后的技术行为 |
| `PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_bundle.py'` | 14 tests，全部通过 | 素材导入合同未被本步改坏 |
| `PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_x01.py'` | 21 tests，全部通过 | 临时本机服务的 health、V04.1/V03 结果与 sidecar；使用测试替身，不调用云端模型 |
| `git diff --check` | 通过 | 修改无空白格式错误 |

第一次受限环境运行服务测试时，本机端口测试被跳过；随后经权限批准重新运行，21 项全部通过，没有跳过。没有重启用户正在使用的服务。

六个把猫狗模板、逐字复制、构造否定句等作为语义验收标准的旧测试已移除。新增检查使用既有真实运行的数据摘录或纯 ID/角色结构，验证数据处理和接口；没有生成新的虚拟场景。旧测试套件其他部分仍是工程替身，不能用 97 项测试通过宣称内容质量通过。

真实素材质量：未验证。本步没有重新识图、没有生成新的真实测试结果，也没有新增 API 成本。任何既有运行日志的摘录或回放，只能用来检查数据传递，不能冒充新的图片质量验证。

本步没有解决整个固定分类体系、Storyline 聚类与分段、评分权重、所有去重条件，也没有完成通用故事独立性评价。不能把第一步的清理说成全链路修复。

## 本步修改后的关键指纹

这些指纹标识本地工作区，不代表已提交或已经部署。

| 文件 | SHA-256 |
|---|---|
| `src/diary_one_ci/x02.py` | `6f2dc05c93fc997eff264b7d070d8f717ceb25d14ff9a1a60e0fb677cbef37b1` |
| `src/diary_one_ci/contracts/x02_storyline_v02.json` | `1d8f4d2edb0810fe7fce72b0aac8bbd0e3d6a849dbdad1266f5617cf05693ecd` |
| `contracts/x02_staged_preview_v04_1.schema.json` | `e0a774e6fce581c9f3903945852092a7a27094b6b0b70f5c1cb08db132c95776` |
| `tests/test_x02.py` | `cf298c81426d0ae5a3d86e3206f486e27d58f39a4428592c3db4ddaaa09e17dd` |
| `tests/test_codex_x02_rule_cleanup.py` | `ab3539f77c6e447056064e0c385e9cd54f86d562450016db19ef5d1fd82c9469` |
| `tests/fixtures/codex_x02_real_run_data_excerpt.json` | `33c4884197c077a786fa9605f5d27f51c6738b119da9075dbb9d726b6e883154` |
| `tests/test_x01.py` | `42a57aec8d7f14ace05c36ba66bcd848a3fd0b7f49cc3065b58ca53575279e4a` |
