# Diary One Cloud Intelligence — Read First

## 当前候选：V1.75 未覆盖事实审查（2026-09-15；本地回归通过，真实质量未验证）

先读 [V1.75 检查点](codex_CHECKPOINT_V1_75_UNCOVERED_FACT_AUDIT.md) 和 [V1.75 设计](codex_D5_V1_75_UNCOVERED_FACT_AUDIT_DESIGN_V01.md)。修改只来自 V1.74.1 素材包 1 的真实失败：S09 虽收到全部事实，却无法可靠识别哪些具体经历尚未进入 Chapter，漏过一条有完整现场和动作的事实；所选三项又被自身关系判断全部否决。V1.75 在原有一次 S09 中加入 Chapter membership、未覆盖事实逐条审查、受事实支持的 `revisit_hook`、最终可共存集合和完整逐对关系合同；未覆盖不等于高价值，Chapter 内但故事职责不同的 Aha 仍允许。333 项本地回归通过、外部 API 0、场景词规则 0；尚未冻结或用新模型回复验证，不切 Web/App，也不代表 Production ready。

## 前一候选：V1.74.1 全事实 Aha 编辑＋Writer 安全出口（2026-09-15；真实 Aha 质量未通过）

先读 [V1.74.1 素材包 1 真实复盘](codex_V1_74_1_PACK_1_REAL_REVIEW.md) 和 [V1.74 D5 设计](codex_D5_V1_74_EXPERIENCE_EDITOR_AND_SAFE_WRITER_EXIT_DESIGN_V01.md)。V1.74.1 已实现并冻结：S07 只负责 Chapter；S09 一次读取全部可用事实并选择原子 Aha；S04 为每条事实绑定代表帧；Writer 使用请求内短编号，失败时保留内部 Chapter 结构与精选素材但不发布坏文案。素材包 1 完整运行得到 4 Chapter / 0 Aha；Writer 与代表帧机制真实通过，但 S09 漏审未被 Chapter 覆盖的完整经历，且所选三项均与 Chapter 同故事，Aha 质量不通过。因此由上方 V1.75 取代继续验证，V1.74.1 历史快照保持不变。

## 最新真实验证：V1.73 Chapter 分组改善，Aha 与 Writer 出口仍不接受（2026-09-15）

先读 [V1.73 素材包 1 全新完整链复盘](codex_V1_73_PACK_1_REAL_REVIEW.md)。冻结候选从 20 个原视频重新标准化出 74 帧，并完整执行 S04–S12；最终返回 3 Chapter / 1 Aha，13 次 API、无重试，模型链约 215.83 秒，连同标准化约 334.74 秒，输入/输出 132,697 / 14,782 Token，历史公开价快照估算 ¥0.1072432。

街市、古寺水边、遛狗三条经历没有再因石板路或古建筑而混合，Chapter 分组在本包明显改善。但 S07 只提出 5 个且多为文字/地标识别的 Aha 候选，烤饼摊的完整现场被焦点压缩成招牌；S09 又用“不同对象和文字”证明两个候选独立，同时把其中一个与古寺 Chapter 判为同故事。程序正确拦下矛盾项，最终唯一 Aha 仍只是“古越龙山石碑”。Writer 另因一个长 UUID 抄错，拒绝了原本可用的街市文案并发布 151 字中英混杂事实兜底。V1.73 技术链完成但真实质量不接受，停止素材包 2、不切 Web/App。下一步先设计 Aha 候选/关系的唯一裁决和 Writer 短编号/失败出口，不继续补同义 Prompt 或场景规则。

## 实现阶段记录：V1.73 本地回归通过（冻结前记录；随后状态以上方真实复盘为准）

先读 [V1.73 实现检查点](codex_CHECKPOINT_V1_73_AHA_SET_EDITOR.md) 和 [D4 设计](codex_D4_AHA_SET_EDITOR_DESIGN_V01.md)。产品已确认所有记录统一允许 0–3 个 Aha，有充分候选时主动争取 2–3 个；同主题可以共存，但必须有不同回看体验。S07 现在只负责 Chapter 与最多 8 个原子 Aha 候选；新增 S09-A 用一次纯文字 Plus 调用编辑集合，S09-B 只校验编号、事实和闭合关系，不看场景词、不打代理分、不补位、不重试。无 Chapter 时也允许最多 3 个 Aha；S09 失败时 Chapter 保留、Aha 路径明确关闭。完整本地回归 322 项中 321 通过、1 项既有环境跳过，新增外部 API 0；这只证明实现和接线，尚未证明真实质量改善，也没有切换 Web/App 或 Production。

## 最新真实验证：V1.72.1 出口修复通过，Aha 集合质量仍不接受（2026-09-11）

先读 [V1.72.1 素材包 1 全新完整链复盘](codex_V1_72_1_PACK_1_REAL_REVIEW.md)，实现边界见 [V1.72.1 检查点](codex_CHECKPOINT_V1_72_1_FOCUS_FRAME_WRITER_EXIT.md)。311 项本地检查通过、1 项既有环境跳过；随后 20 个原视频重新标准化为 74 帧，完整执行 S04–S12，返回 3 Chapter / 3 Aha。10 次 API 调用，Writer 仅一次且使用 Plus；模型链约 192.43 秒，连同标准化约 310.18 秒，输入/输出 119,150 / 14,010 Token，历史公开价快照估算 ¥0.10271295。

焦点帧、单帧 Aha、24 字硬出口和禁止 Aha 确定性兜底均真实生效；三条 Aha 正文都是 11 字，没有重写或旁路发布。市集、祈福空间、运河三个 Chapter 分组清楚。但三条 Aha 都退化成“看到不同商铺招牌”，模型用不同商品/店铺实体代替不同故事；其中茶店卡价值与 OCR 均不足，烤饼卡又把真正的摊位现场感删成招牌说明。市场 Chapter 与三条 Aha 的已存在关系在 S10 后投影时丢失。V1.72.1 技术目标通过，内容质量不接受，不继续包 2、不切 Web/App。下一步建议先单独设计 Aha 集合编辑职责，再处理 S10 后关系投影；不继续追加同义 Prompt 或场景规则。

## 前一真实验证：V1.72 关系闭环生效，但 Writer 兜底绕过硬门槛（2026-09-10）

见 [V1.72 素材包 1 全新完整链复盘](codex_V1_72_PACK_1_REAL_REVIEW.md)。3 Chapter / 3 Aha 和完整的 9 条 Chapter/Aha、3 条 Aha/Aha 关系均成功返回，Chapter 分组较 V1.71 清楚；但模型三条 Aha 文案均超过 24 字，本地硬门槛拦下后，确定性兜底因丢失策略字段又把 61/111/37 字原事实发布为成品。V1.72 不接受，冻结证据由 V1.72.1 取代而未被改写。

## 最新真实验证：V1.71 素材包 1 完成；Aha 共同选择仍未闭环（2026-09-10）

先读 [V1.71 素材包 1 全新完整链与逐卡复盘](codex_V1_71_PACK_1_REAL_REVIEW.md)。同一 48 文件封存候选重新标准化 20 个视频为 74 帧，完整执行 S04–S12，返回 3 Chapter / 3 Aha；11 次调用、0 重试，模型链约 208.57 秒，连同标准化约 325.51 秒，输入/输出 125,394 / 12,330 Token，历史公开价快照估算 ¥0.0757568。

街市、古镇水巷的覆盖和最终三张精选有进展，但内容质量不接受：S07 的三个 `aha_relations` 均为空，9 个 Chapter/Aha 关系全部缺失仍被执行；两个小狗 Aha 与林径遛狗 Chapter 高度同故事；一个 Aha 的单条事实横跨狗、电瓶车、茶店多个时刻；三条 Aha 为 49/45/50 字仍被标记主文案就绪；另有“古寺”“小舟而行”等未被事实充分支持的措辞。下一步建议先修选单逐对关系闭环、Aha 原子 Moment 和一次调用的可执行长度合同，再重跑包 1；暂不把当前 V1.71 继续当作包 2 质量候选，不切 Web/App、不改其他项目。

## 当前实现：V1.71 分段记录背景＋共同选单，本地检查完成（2026-09-10）

先读[V1.71实施检查点](codex_CHECKPOINT_V1_71_RECORDING_EDITOR.md)。按用户“不等功能样机、先优化算法”的指示，落实已认可D2的首步：有据素材不再仅因事件类别丢掉Aha比较资格；同一S07给出本批记录背景和明确Chapter＋Aha推荐；S09执行子集，不按旧权重重排、不自动补位。普通/特别日不设硬分类，不能从导入量推断佩戴时长或用户兴趣；部分选单错误有明确诊断，不连带回退整个组合。

新增独立研究入口，不切Web/App。全量300项本地检查中299通过、1项环境跳过；三包既有事实范围8→20、4→26、18→55，仅表示可比较资格增加。三包函数回放和单件真实素材组件检查通过；均为离线接线验证，新增外部API 0，未证明真实质量改善。S10/Writer、GPS和正式增量触发、无Chapter Aha数量及第5章例外保持未改。下一阶段同版三包各一次新完整研究链，逐包反馈；下方V1.70质量未接受结论不变。检查点和私有事实仅本地归档。

## 当前设计：D2 整日编辑决策短设计完成，尚未实现（2026-09-10）

先读 [D2短设计](codex_D2_WHOLE_DAY_EDITORIAL_DESIGN_V01.md)。承接V1.70真实复盘，只定义三个变化：有据素材不再仅凭事件类别失去Aha比较资格；S07明确推荐Chapter＋Aha组合，S09执行而不以剩余候选补位；计划重点与精选后实际支持的重点清楚交接。复用既有事实/成员字段，拟以整日选单替代完整排序，不新增总审调用、场景规则或未知关系硬阻断。S10代表帧/大候选组和Writer另行实施，不声称本设计已修复。46个运行文件无漂移，新增API 0；仅设计与算法阅读索引变动，不切Web/App、不改产品数量与交互。下方V1.70内容质量未接受及历史记录保持有效。

## 最新：V1.70 三包真实研究链完成，内容质量仍未接受（2026-09-08）

先读 [三包综合结论与下一步](codex_V1_70_THREE_PACK_FINDINGS_AND_PLAN.md)，逐卡详情见 [包2](codex_V1_70_PACK_2_REAL_REVIEW.md)、[包3](codex_V1_70_PACK_3_REAL_REVIEW.md)。用户明确批准北京百炼出站后已完成包2/3；下方授权暂停仅为历史。三包同一46文件封存，102素材/187帧，各一次新标准化及S04–S12，输出3C/1A、4C/3A、4C/3A，共50次API、历史快照估算¥0.28952265，无重试或Writer重写；实际模型、usage和输入/源码摘要核验通过。

排序生效不等于组合质量通过：包2因不可发布两件组未列排序而整路Chapter回退；包1/2同输入旧S09对照名单相同，包3名单确有改变，但三个Aha都来自同一个落选园区故事。上海夜街与山顶分组有进展，精选主线兑现、视频代表证据、7/7 Aha偏长、标题格式失败扩大成正文兜底等真实问题仍保留。下一建议先收敛整日组合与Aha分工设计，再分开处理交接、S10与Writer；本轮不继续调参/抽卡、不切Web/App、不执行S13、不触及其他项目。含私有事实的复盘仅本地留存。下方历史结论不改写。

## 当前真实验证：V1.70 包1完成；包2/3本地就绪、等待出站授权（2026-09-08）

见 [包1逐卡复盘与暂停点](codex_V1_70_PACK_1_REAL_REVIEW.md)。同一46文件封存候选完成20视频/74帧的新研究链：3 Chapter＋1 Aha，11次调用，约5分11秒，历史费率估算 ¥0.07438925。新排序两路均生效，小狗同故事不再双发；但部分素材先被候选章占用、后被精选省略，Aha仍41字。相同新S07输出交给旧S09的本地对照得到相同名单，因此不能把本包进步归因于排序本身。包2/3分别39/74帧已本地校验，包2外发在进程启动前被安全审批拒绝，两包均无API attempt或结果。等待明确向北京百炼接口外发这两包证据的授权后续跑，不重跑包1、不改规则、不切Web/App。下方实现与更早结论保留为历史。

## 当前实现：V1.70 编辑顺序交接已封存；未做新一轮真实质量验证（2026-09-07）

见 [V1.70 S07 → S09 编辑优先顺序检查点](codex_CHECKPOINT_V1_70_EDITORIAL_ORDER.md)。已按批准的 D1 设计，让结构模型在原调用中交出两路简短优先顺序，研究入口 S09 实际消费；合法排序不再被原代理排名覆盖，原候选资格、三件底线、容量和同故事规则保留。排序缺损仅对应一路明确回退，不加重试或语义拦截。287 项本地检查中 286 通过、1 项环境跳过；三包旧真实记录离线回放和封存副本验证通过，新增外部 API 0。46 文件候选已封存，43 个既有文件不变；S04、S10、Writer 及 Web/App 默认策略未变。只证明接线有效，不证明内容质量修复。下一步同版三包各一次全新完整运行，逐包反馈。下方草案与 V1.69 结果作为阶段历史保留。

## 当前设计：D1 经历选择与 Chapter/Aha 分工草案（2026-09-07；未实现）

见 [D1 简明职责与真实案例](codex_D1_EXPERIENCE_SELECTION_AND_AHA_DRAFT.md)。承接三包复盘，明确“提出经历/发现—比较整日取舍—相关卡片分工—精选兑现主线”的既有环节职责；不增加四次调用。当前 S07 只读事实而不直接看图，已有原则不重复堆叠为新提示。首个拟议实现范围为 S07→S09 的编辑选择交接，S10 输入、Writer 错绑和视觉模型另做，不同时更改。44 个冻结源码/合同无漂移；本轮仅文档，新增 API 0，未冻结新的体验边界、未切 Web/App。下方 V1.69 真实质量未接受结论保持不变。

## 最新：V1.69 三包全新研究链完成，内容质量仍未接受（2026-09-07）

先读 [三包共性问题与下一步方案](codex_V1_69_THREE_PACK_FINDINGS_AND_PLAN.md)，包 3 详情见 [7 张卡片与 56 个素材去向](codex_V1_69_PACK_3_REAL_REVIEW.md)。用户明确允许包 3 的 74 张证据图及相关文字发送北京 DashScope 后，沿用已完成标准化续跑；下方外发暂停记录仅作历史，不代表当前仍被阻断。

同一 44 文件冻结候选，三包各一次全新 S04–S12 研究链，输出 3C/3A、4C/3A、4C/3A，共 53 次 API、估算 ¥0.28013660；包含原有 S04 三次单项隔离重试，没有 Writer API 重写。S07 未知短引用 0，实际模型/usage 回执齐全；源码和合同无漂移。包 3 为 26 次调用、约 5 分 46 秒、¥0.12955145。

技术贯通不是质量验收：候选漏掉具体经历、Aha 排名代理量饱和、分工缺失、跨卡引用导致 3 个 Chapter 退成完整事实兜底、视觉错误传播及 9/9 Aha 偏长均已记录。下一建议先处理经历选择与 Chapter/Aha 分工，Writer 绑定另列独立工程修复；尚未实施，不追加抽卡重跑、不切 Web/App、不执行 S13 或修改 R2/Firmware/SDK/共享状态。报告含私有事实，仅本地留存。以下各段保留为阶段历史。

## 素材包 3 进行中：标准化完成，外发执行被系统审批拦住（2026-09-07）

同一 V1.69 下，56 个原素材已重新标准化为 74 张证据图，帧摘要全部核对、44 个源码/合同无漂移。外部模型命令在进程启动前被自动审批拒绝：现有概括授权未被接受为本包向北京 DashScope 外发的明确目的地授权。没有 API attempt、调用目录或模型结果，新增 API 费用 0；没有绕行或改规则。暂停记录见 [本地执行保留回执](../var/codex_v1_69_full_chain_execution/pack_3/round_1/codex_external_call_hold.json)。用户明确确认该目的地后可用原执行工具续跑，无须重新抽帧。三包综合质量结论尚未形成，下方包 1/2 的已完成结论保持不变。

## 最新真实验证：V1.69 素材包 2 完成；分组有进展，成品仍未接受（2026-09-07）

见 [V1.69 素材包 2 逐卡复盘](codex_V1_69_PACK_2_REAL_REVIEW.md)。20 照片＋6 视频全新标准化为 39 帧，26 个观察/26 条事实保留；14 次真实 API，无重试或 Writer 重写，生成约 3 分 35 秒，估算 ¥0.06943845。最终 4 Chapter / 3 Aha，覆盖 15 个不同素材；44 个冻结源码/合同无漂移。

夜间餐车/小吃 18–20 独立成章，室内两件未凑章而保留 16 为 Aha；鹿的三个同故事 Aha 正确抑制。但 Writer 将夜间/驾车两章的编号与正文互换，引用校验拦住后退回“生活片段＋完整事实”；驼群的“双人骑乘”错误从 S04 经 S07/S10 传播至文案；三条 Aha 为 46/39/41 字且有无依据扩写。质量未接受，不把分组进展等同全链修复。本轮未改规则、未切 Web/App、未执行 S13 或包 3；下一阶段建议保持同版跑包 3 后统一归纳。下方包 1 及更早结论保留为历史。

## 最新真实验证：V1.69 素材包 1 完成；内容质量未接受（2026-09-07）

先读 [V1.69 素材包 1 全新研究链与逐卡复盘](codex_V1_69_PACK_1_REAL_REVIEW.md)。20 个原视频重新解码、抽取 74 帧，完整运行现有 S04–S12 研究链，得到 3 Chapter / 3 Aha；13 次 API 调用，含 S04 两次既有单项隔离重试，Writer 仅一次。总生成约 5 分 32 秒，公开价快照估算 ¥0.0811467。20 个观察、31 条事实保留；S07 短编号未知引用为 0，44 个冻结源码/合同无漂移。

真实质量仍未接受：C3 与 A2 重复讲同一段林间小狗同行，S07 缺失这对卡片的分工关系后以未确定状态放行；三条 Aha 为 40/44/40 字，已标记偏长，一条存在无证据结尾。报告保留全部六条原文与二十个素材去向，区分明确错误与自然步道两件未成章等内容取舍。本轮只跑包 1，未继续包 2/3、未改规则、未切换 Web/App、未进行 S13 正式导出。下一阶段建议保持候选不变，逐包积累真实证据；不将数量增加或接线成功宣称为质量修复。下方接线/实验结论作为历史保留。

## 主干优化工作入口（2026-09-07；不替代下方 V1.68 质量结论）

最新完成 [V1.69：S07 Plus＋短编号研究接线](codex_CHECKPOINT_V1_69_S07_PLUS_SHORT_REFERENCES.md)。仅新增显式研究网关，43 个既有运行源码/合同不变，44 文件候选已封存；其他阶段仍用原 Flash，Web/App 默认未切换。280 项本地检查中 279 项通过、1 项环境跳过；四份真实短编号回复及两包完整旧链离线回放通过，夜市三件可进入后续筛选、室内两件按原三件底线处理，重复候选名仍按原未确定关系处理。新增 API 调用 0 次；这是接线完成，不是新方案真实质量通过。下一阶段三包各一次全新研究链，逐包反馈，本阶段未自动启动。

此前完成 [B3：短编号 4 次真实验证](codex_MAINLINE_B3_SHORT_REFERENCES_RESULTS_20260907.md)。同一 Plus、事实与任务要求，只用请求内短编号并精确还原，4 次均无未知编号或引用错绑拒绝，16 条候选全部通过既有结构/引用检查（其中两条仅两件，不代表最终可发布）。夜市与餐厅仍分开；Aha 分工、无依据时序、说省略却保留两件组及一次重复候选名仍需检查。估算 ¥0.166792，模型约 2.5 分钟，无重试；43 个运行源码/合同未改、Web/App 未切换。当时建议保留短编号并回到三包全链研究验证，B3 本轮未自动接入或续跑；后续接线见上方 V1.69。

此前完成 [B2：结构模型 8 次单变量对照](codex_MAINLINE_B2_MODEL_COMPARISON_RESULTS_20260907.md)。原事实/Prompt/Schema 不变，仅将 Flash 与固定 Qwen3.7 Plus 比较。Plus 两轮均未将餐厅与夜市混合，但四次回复均有编号错误，17 条 Chapter 提案仅 2 条通过既有结构/引用检查；无依据时序和 Aha 分工仍未稳定解决，不切换模型。总估算 ¥0.2770，模型调用约 8 分钟，无重试。43 个运行源码/合同摘要不变，Web/App 未切换。这是 S07 局部诊断，不是最终卡片数量或全链路验收；当时建议验证请求内短编号映射，后续见上方 B3。

已完成[全链路综合复核](codex_ALGORITHM_COMPREHENSIVE_REVIEW_20260907.md)、[阶段 A：真实评价基线](codex_MAINLINE_STAGE_A_20260907.md)及[B1：辅助提示 8 次结构对照](codex_MAINLINE_B1_HINT_ABLATION_RESULTS_20260907.md)。B 两轮仍提出室内用餐/夜市混合组，不接入提示删除；引用错误导致组被拒绝不能算内容修复。8/8 模型请求完成，历史估算约 ¥0.0593，无重试；这是局部诊断，不是全链路验收。43 个运行源码/合同文件未改，Web/App 未切换；下一建议仅对照结构模型能力，不继续叠加同义提示。

## 当前入口：codex V1.68 真实质量未接受；素材包 2 触发停止条件（2026-09-05）

先读 [V1.68 Chapter 以具体经历为先](codex_CHECKPOINT_V1_68_EXPERIENCE_FIRST_CHAPTER.md)。
真实运行与逐卡纠偏见 [V1.68 真实素材包阶段结果](codex_V1_68_REAL_PACK_RESULTS.md)。
Owner 已确认：共享宽泛主题不足以自动合章；跨场景需有共同活动或探索主线，不能凭导入顺序编造连续；
不足三件可以少章，独立内容仍可参加 Aha。V1.68 只修正现有 S07 分组说明和版本回执，
不新增 schema、程序语义 gate、模型调用或场景词规则；275 项本地检查中 274 项通过、
1 项因测试沙箱禁用本地 socket 而跳过，无失败。
同一冻结候选下，素材包 1 完成一次真实全链，3 个 Chapter 的具体经历边界初步通过；完整四帧证明
`林径步移` 的祈福设施、林木水边、石桥台阶与后续林间路径存在真实连接，不是无关素材填充。
该包判定为 `PASS_WITH_DEFECTS`：同一小狗林径故事被 Chapter 与 Aha 重复发布，且内部理由含无时间依据的进程词。
素材包 2 随后完成 26 素材/39 帧、15 次调用的真实链，但 `烟火里的食光` 仍仅凭泛化饮食活动合并室内火锅与夜市小吃；
夜市自身已有三件可成章素材，模型却漏掉餐车远景并跨场景补入室内素材。它触发冻结停止条件，V1.68 真实质量不接受。
素材包 3 已本地标准化为 56 素材/74 帧，但按停止纪律未外发、没有 API attempt 或模型结果。
V1.68 没有中途修改或抽卡重跑，也未宣称 Web/App 生效或 Production readiness。

## 前一入口：codex V1.67 三包真实回归完成，内容质量尚未接受（2026-09-05）

先读 [V1.67 三包真实结果与下一方向](codex_V1_67_REAL_PACK_RESULTS.md)，
逐卡评价用 [19 张原文与素材对照](codex_V1_67_CARD_REVIEW_APPENDIX.md)，
实现范围见 [V1.67 单一素材清单与统一引用检查点](codex_CHECKPOINT_V1_67_SINGLE_SOURCE_STRUCTURE.md)。
本步只减少 S07 的重复成员/事实总表与 Aha 身份体系，通过新格式转换沿用旧内部候选接口。
270 项回归中 269 项通过、1 项环境跳过；真实旧回复回放通过不等于新模型质量通过。
42 文件同一冻结候选完成三包各一次新研究链，结果为 3C/3A、4C/3A、3C/3A，50 次调用均完整返回。
古镇、足球恢复，市集和金殿同故事重复未再发布；但宽泛主题合章、跨卡重述和事实外推仍需改进。
下一步回到 Chapter 聚类依据及 Chapter/Aha 独立价值，不继续堆叠字段补丁或场景特例。
Owner 已在封存后接受具体经历优先：仅共享宽泛主题不足以自动合章；跨场景需有共同活动或探索主线支撑，
导入顺序不能证明连续；不足三件可以少章，独立内容仍可参加 Aha。该决策进入下一阶段，V1.67 结果不回写。
未切换 Web/App，未修改 R2 或公开部署；S13 正式回取/导出不在本次研究验证范围。
以下 V1.66 及更早入口作为阶段历史保留，不覆盖本轮状态。

## 前一入口：codex V1.66 三包真实回归完成，质量未通过（2026-09-05）

先读 [V1.66 三包真实结果与下一方向](codex_V1_66_REAL_PACK_RESULTS.md)，
逐卡评价用 [16 张原文与素材对照](codex_V1_66_CARD_REVIEW_APPENDIX.md)，
实现范围见 [V1.66 表达分工检查点](codex_CHECKPOINT_V1_66_EDITORIAL_ALLOCATION.md)。

本次只在既有 S07 调用内增加 Chapter/Aha 分工，让 S09、S10、Writer 消费同一关系；
未改模型、最低三件、候选资格、标签或 Writer 调用次数。运行 262 项回归：261 项通过、1 项环境跳过。
三包同一冻结算法各一次全链，输出分别 2C/3A、3C/2A、3C/3A，47 次调用完整返回。
但古镇与足球仍因重复清单不一致丢章，市集与金殿重复未解决，三个 Writer 实际分工提示均为空。
因此只认定实现与实验完成，不认定真实质量修复。下一小步优先精简重复字段与身份绑定，不加场景特例。

三包是既有开发回归素材，不是新用户未见测试集。本次为函数入口全链研究测试，
未验证 Web HTTP/UI 启用状态，也未切换 Web / App、未修改 R2 封存交付，公网测试仍暂停。
以下 V1.65 及更早入口作为阶段历史保留，不覆盖此处状态。

## 前一入口：codex V1.65 本地小步修复（2026-09-04）

先读[第三方复核与 V1.65 接收修复](codex_CHECKPOINT_V1_65_STRUCTURE_ACCEPTANCE.md)：只去掉当前路径的内部 Aha 说明长度误拦，并从已验证的 Chapter 详细事实引用汇总冗余清单。真实错绑、数量容量和内容选择规则未放开。255 项测试完成，无失败、1 项环境跳过；原始回复离线回放通过，但没有新模型调用、Web 启用或真实质量通过结论。

最新完整链实验见[V1.64 共性问题报告](codex_V1_64_COMMON_FINDINGS_AND_DECISIONS.md)：被测算法是冻结 V1.63，九轮已结束，六轮完整输入可预览、一轮观察不全受阻、两轮无结果。V1.64 是实验编号，不是算法升级；结果质量仍不接受，原修改建议按 V1.65 的收窄结论推进。

最近记录的 Web 集成检查点仍是[V1.63](codex_CHECKPOINT_V1_63_ANIMAL_SUBJECT_GRANULARITY.md)，包括 V1.62 完整画面与用户确认的动物通用观察分类。V1.65 本步未重查或重启页面；不能把源码版本冒称 Web 已启用版本。公网测试仍暂停。

App接入独立使用已封存的[R2/V1.63候选](codex_APP_HANDOFF_R2_V1_63.md)，固定source/schema/profile并已同步04；Owner明确不等V1.65或质量完善再接线。R2只通过合成离线接口验证，没有自动切换App/Web默认或部署，不能当成V1.65质量修复。

以下为较早阶段历史摘要，涉及“当前/最新”的表述以对应阶段为准，不覆盖上面的 V1.65 入口及 V1.64 实验结果。

**文档状态：** 当前研发入口
**整理日期：** 2026-09-04
**当前冻结检查点：** V1.25（S00–S13 Full-flow Contract；继承 V1.24–V1.1 与 V1.0 未覆盖内容）
**最近已验证 Web 集成检查点：** codex V1.37（Chapter Media V01：展示精选与三项底线）；继承 Storyline V03 / Writer V02；V1.31 真实失败基线保留。V1.46 本轮未重启服务或验证页面启用状态。
**当前验证基线：** V1.36 接入后的真实运行 670b2417 已发现展示重复与旧双素材例外问题；V1.37 技术检查完成，尚未做新一轮真实模型全流程质量验证
**当前实现基线：** codex V1.49 已在当前 V04.1 的 S04 将“事实简洁目标”和“事实保存边界”分离：200 字符仍是生成目标，201–1000 字符且原有证据/结构校验通过的事实原样保存；不截断、不摘要、不改写。使用 V1.48 七批真实旧版输出离线回放后，有事实素材由 16/20 恢复为 20/20，存活事实由 20 条恢复为 27 条；这只验证确定性信息不再误丢，不代表分组、Writer 或最终质量修复。全仓 216 项测试通过、1 项既有 socket 测试跳过；无模型调用、Web 改动或部署。
**最新 Writer 真实专项：** codex V1.51 完成固定 V1.48 输入、仅换 Flash 的两次调用；初稿六条漏引用，重试补齐后 3 Chapter/2 Aha 通过格式校验，石碑 Aha 仍为 24 字。文案质量未接受，没有运行模型切换或 Web 部署。约 13.03 秒模型耗时，估算 ¥0.00373320；下一建议是完整反馈同一草稿已有的多个格式问题，不添加语义规则。
**专项核查依据：** codex V1.50 定位了 P2 Writer 出口：请求已有 20 字要求和精确重试反馈，真实回复仍超长；新版重试另有重复编号。程序回退只复制整条短事实，本轮没有合格可复制项。V1.50 仅诊断文档；随后模型单变量对照结果以 V1.51 为准。
**最新真实完整对照：** codex V1.48 已完成包 1 的旧/新版独立运行，每版 20 视频、74 帧。用户明确授权 Evidence 发往北京 Qwen；严格成本控制不再作为测试前置。旧版最终 2 Chapter/0 Aha，新版 3 Chapter/0 Aha；两版各选出三条 Aha 但 Writer 失败。已记录事实长度导致的素材损失、分组/精选/文案问题，质量不接受。整轮推理估算 ¥0.08932755，含第一次日志适配错误导致的空输入请求。仅实验工具修正，不修改冻结算法、Web 或用户测试页；下一阶段优先审查确定性信息损失与 Writer 出口，不自动重跑/加规则。
**适用范围：** 云端算法、Evidence、Moment、Chapter/Aha、模型网关、App 联调与研究测试

## 1. 阅读顺序

最新先读 [codex V1.51 固定输入 Writer 模型对照结果](codex_V1_51_WRITER_MODEL_ONLY_RESULTS.md)。两次真实 Flash 调用完成，格式出口为 3 Chapter/2 Aha，仍有一条 24 字 Aha 失败；初稿六条缺引用，重试补引用但正文未改。质量未接受、未接入 Web，不是新的整日素材测试。下一建议是用真实回复修复既有格式错误的一次性完整反馈。

下一阶段先读 [codex V1.50 Aha Writer 出口核查](codex_V1_50_AHA_WRITER_EXIT_DIAGNOSIS.md)。已定位失败链路，并纳入 V1.38–V1.44 的既有实验结论；不重新叠加失败过的字数提示方案。模型对照仍为待执行，不是已修复或已接入。

当前先读 [codex V1.49 S04 事实保留检查点](codex_CHECKPOINT_V1_49_S04_FACT_RETENTION.md)，了解已经单独修复的确定性事实误丢及其明确边界。随后读 [codex V1.48 逐卡真实复盘](codex_V1_48_PERSON1_RESULTS_REVIEW.md)，执行边界见 [完整链路对照检查点](codex_V1_48_PERSON1_FULL_PIPELINE_COMPARISON.md)。V1.49 没有重跑模型、接入 Web 或证明质量通过；V1.48 的 3 个 Chapter / 0 Aha 仍是最近真实完整结果。

输入与源码基线见 [codex V1.47 三包完整链路对照准备](codex_V1_47_FULL_PIPELINE_AB_PREPARATION.md)。原预算提议作为历史保留，后续以 V1.48 为准。

当前算法实现见 [codex V1.46 内容交接实现与验证](codex_CHECKPOINT_V1_46_CONTENT_BRIEF_HANDOFF.md)。仅完成一个共性机制的本地实施；部署状态、真实模型质量和用户评价分开记录。

设计依据见 [codex V1.45 共性机制核查与优先改进项](codex_COMMON_CONTENT_HANDOFF_REVIEW_V1_45.md)。这是实施前的分析记录，原文保留；区分已有能力、已确认的信息传递缺口、未证实的质量原因，不重开所有算法阶段。三个既有素材包用于开发/回归，不能未经核查就称为未见测试集。

最近真实结果见 [codex V1.44 同输入 Flash / Plus 逐条对照](codex_WRITER_MINIMAL_PLUS_V1_44.md)。Plus 未显示整体优势，编号复制错误与文案关系错误分开记录；原结果保留，其中围绕 C3 单个案例的后续建议已由 V1.45 取代。

Flash 对照基线见 [codex V1.43 精简 Writer 真实结果与六条逐项审阅](codex_WRITER_MINIMAL_V1_43.md)。格式恢复、输入减少，但仍有无依据补写；保留原始结果，不把格式成功等同质量修复。

前一轮真实结果见 [codex V1.42 实验结果](codex_WRITER_FOCUS_V1_42_RESULTS.md) 与 [实验检查点](codex_CHECKPOINT_V1_42_WRITER_FOCUS_EXPERIMENT.md)。保留未通过的原始输出，不把技术审阅记录冒充质量修复。

人工参考见 [codex V1.41 描述重点审阅](codex_WRITER_FOCUS_REVIEW_V1_41.md)。它没有作为答案发送给模型，也不是用户评分或已生效的运行规则。

原始模型结果见 [codex V1.40 六条文案审阅](codex_WRITER_V1_40_USER_REVIEW.md) 与 [该轮检查点](codex_CHECKPOINT_V1_40_WRITER_FULL_PASS.md)。只运行 Writer，不等于全链路；没有启用新运行模型。重写未触发，不声称该轮验证了该分支。

此前对照见 [codex V1.39 Writer 模型对照](codex_CHECKPOINT_V1_39_WRITER_MODEL_COMPARISON.md)。模型与费率仅用于当时的隔离实验，没有切换运行模型；V1.46 同样未切换模型。短句格式通过、自然度与事实表达、用户认可和全链路验证是不同结论。

历史未通过实验见 [codex V1.38 Aha Writer 修复验证未通过](codex_CHECKPOINT_V1_38_AHA_WRITER_REPAIR.md)。请求实验 V03/V04 均未通过真实检查，不能把技术测试通过说成质量修复。当时未改变 V1.37 页面，输出 Surface V02 合同仍被当前源码继承。

最近已验证 Web 集成见 [codex V1.37 Chapter 展示精选](codex_CHECKPOINT_V1_37_CHAPTER_MEDIA_SELECTION.md)。当前完整输出 Schema 为 `contracts/codex_x02_staged_preview_v04_1_media_v01.schema.json`；Storyline V03 负责分组，媒体策略负责三项下限和展示子集，V1.46 未修改这些合同。以下旧检查点中的“Web 未接入”是历史状态，由 V1.36 / V1.37 接入记录取代；本轮页面状态不据此推断。

团队同步全链路时，先读 [V1.25 Production-shaped Pipeline V1.0](CANONICAL_CHECKPOINT_V1_25_PRODUCTION_SHAPED_PIPELINE_V1_0.md)，再读 [Validation Track V01–V02 Baseline](VALIDATION_TRACK_V01_V02_BASELINE.md) 了解当前如何验证。之后按需要进入阶段文件。[End-to-End Pipeline Logic — Team Sync V0.1](END_TO_END_PIPELINE_LOGIC_TEAM_SYNC_V0_1.md) 保留详细案例与历史讨论，但不能替代最新 Canonical Checkpoint。

1. 先读本文，确认当前阶段和状态边界。
2. 分组实现先读 [codex V1.35 模型负责内容分组](codex_INTEGRATION_CHECKPOINT_V1_35_MODEL_OWNED_GROUPING.md)，再读 [codex V1.34 内部主题说明隔离](codex_INTEGRATION_CHECKPOINT_V1_34_STORYLINE_THESIS_ISOLATION.md) 与 [codex V1.33 案例硬编码清理](codex_INTEGRATION_CHECKPOINT_V1_33_EXAMPLE_RULE_CLEANUP.md)。V1.35 的输出 Schema 与“Web 未接入”属于当时状态；当前素材策略及接入记录以 V1.37 为准，完整输出 Schema 为 `contracts/codex_x02_staged_preview_v04_1_media_v01.schema.json`。V1.32 保留为历史候选记录，其中固定主题聚类及被 V1.33 撤回的模板限制不再有效；V1.31 历史失败证据保留，当前验证状态见本文顶部。
3. 读验证基线 [VALIDATION_TRACK_V01_V02_BASELINE.md](VALIDATION_TRACK_V01_V02_BASELINE.md)，区分 Design-Gold conformance 与真实准确率。
4. 读 S13 合同 [CANONICAL_CHECKPOINT_V1_24_SELECTED_HQ_MATERIALIZATION_AND_EXPORT.md](CANONICAL_CHECKPOINT_V1_24_SELECTED_HQ_MATERIALIZATION_AND_EXPORT.md)。
5. 读 S12 合同 [CANONICAL_CHECKPOINT_V1_23_FINAL_VALIDATION_AND_ATOMIC_DAY_STATE.md](CANONICAL_CHECKPOINT_V1_23_FINAL_VALIDATION_AND_ATOMIC_DAY_STATE.md)。
6. 读 S11 合同 [CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md](CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md)。
   - 需要案例与失败验证时读 [S11–S13 End-to-End Cross-check V1.0](S11_S13_END_TO_END_CROSS_CHECK_V1_0.md)。
7. 读 S10 合同 [CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md](CANONICAL_CHECKPOINT_V1_21_EVIDENCE_ANCHOR_MEDIA_EDITORIAL.md) 与 Chapter/Aha 独立性 [V1.20](CANONICAL_CHECKPOINT_V1_20_AHA_CHAPTER_NARRATIVE_INDEPENDENCE.md)。
8. 读 S09 集合选择合同 [CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md](CANONICAL_CHECKPOINT_V1_19_EDITORIAL_SET_SELECTION.md)。
9. 读 S08 [V1.18](CANONICAL_CHECKPOINT_V1_18_TARGETED_ENRICHMENT_VALIDATION.md)、S07 [V1.17](CANONICAL_CHECKPOINT_V1_17_CHAPTER_AHA_CANDIDATE_GENERATION.md)、S06 [V1.16](CANONICAL_CHECKPOINT_V1_16_OBSERVATION_ROLE_ASSIGNMENT.md)。
10. 读 S05 [V1.11](CANONICAL_CHECKPOINT_V1_11_CONTIGUOUS_MOMENT_SEGMENTATION.md)–[V1.15](CANONICAL_CHECKPOINT_V1_15_BOUNDED_DEFER_LOOKAHEAD.md)。
11. 读 S04 [V1.7](CANONICAL_CHECKPOINT_V1_7_OBSERVATION_LITE_COVERAGE.md)–[V1.10](CANONICAL_CHECKPOINT_V1_10_OBSERVATION_LITE_OUTPUT_CONTRACT.md)。
12. 读 S02/S03 [V1.3](CANONICAL_CHECKPOINT_V1_3_AUTO_THREE_FRAME_EVIDENCE.md)–[V1.9](CANONICAL_CHECKPOINT_V1_9_SIGNAL_SPLIT_WINDOW_LOCAL_OBSERVATION.md)。
13. 读 S01 [V1.2](CANONICAL_CHECKPOINT_V1_2_RAW_ASSET_INTAKE.md) 与 S00 [V1.1](CANONICAL_CHECKPOINT_V1_1_ROLLING_DAILY_MEMORY.md)。
14. 再读继承基础 [CANONICAL_PROCESSING_RULES_V1_0.md](CANONICAL_PROCESSING_RULES_V1_0.md)。
15. 遇到英文/算法概念时读 [Algorithm Glossary V1.0](ALGORITHM_GLOSSARY_V1_0.md)。
16. 需要历史展开时读 [DAILY_MEMORY_ALGORITHM_FLOW_V0_1.md](DAILY_MEMORY_ALGORITHM_FLOW_V0_1.md) 与 [End-to-End Team Sync](END_TO_END_PIPELINE_LOGIC_TEAM_SYNC_V0_1.md)。
17. 处理 iPhone / Mac / API 研究联调时读 [APP_X01_INTEGRATION_TEST_V1_0.md](APP_X01_INTEGRATION_TEST_V1_0.md)。
18. 需要协议细节时再读：
   - [app-library-bundle-v03.md](app-library-bundle-v03.md)（当前 Web sequence-only 输入）
   - [app-research-export-v01.md](app-research-export-v01.md)（历史 E00/V01 边界）
   - [x01-diary-research-preview-v01.md](x01-diary-research-preview-v01.md)
   - `../contracts/*.schema.json`

不要把本文当成替代 Schema 或代码的接口定义；本文是低歧义索引。

## 2. 决策状态词

| 状态 | 含义 | 修改规则 |
|---|---|---|
| `FROZEN` | 已冻结产品/架构规则 | 必须显式重开后才能修改 |
| `BASELINE` | 当前工程或实验基线 | 可被真实实验结果升级 |
| `EXPERIMENTAL` | 隔离实验，不是产品事实 | 不得自动进入 Production |
| `OPEN` | 尚未决策 | 到指定节点显式决定，不能暗中假设 |
| `SUPERSEDED` | 已被替代 | 后续不得作为当前方案重新引用 |
| `GAP` | 当前实现与冻结目标之间的差异 | 必须保留可见，不能用文案掩盖 |

## 3. 一分钟全局图

```text
REAL LIFE
  ↓
Capture / RawAsset
  ↓
Phone Source Cache
  ↓
Normalized Evidence
  ↓
Observation Lite
  ↓
Moment (purity-first)
  ↓
Observation Role Assignment
  ↓
Chapter Candidate / Aha Candidate
  ↓
Targeted Enrichment + Evidence Validation
  ↓
Set Selection
  ↓
EvidenceAnchor → Media Editorial
  ↓
Grounded Narrative / Canonical Tags
  ↓
Daily Memory
```

核心损失方向：

> `False Memory / False Merge` 的代价高于 `Missing Memory / 轻微 Over-segmentation`。

## 4. 当前产品级冻结规则

| 项目 | 当前规则 |
|---|---|
| Daily Output | `CHAPTER_DAY`：1–5 Chapter + 0–3 Aha；丰富日目标 3–4，第 5 个为严格例外；`HIGHLIGHT_DAY`：0 Chapter + 1 strong Aha；`EMPTY_DAY`：两者都无 |
| Day processing | 每次导入增量准备 Evidence；约 1.5h 新增有效覆盖后 eligible，约 2h 默认 Preview attempt；Manual / semantic delta / user Final 可提前触发 |
| Revision UX | 白天稳定累加、丰富已有 Chapter、受控合并；算法始终基于截至当前的全天累计 Evidence 判断 |
| RawAsset truth | 拍摄时间与拍摄时区决定生活顺序和 Diary 归属；导入时间只做同步追踪；重复导入幂等，异常事实隔离而不猜测 |
| Auto Evidence | Phone 每条合法 Auto 9s 视频固定抽取 1.5 / 4.5 / 7.5s 三帧；只有三帧两两高度相似且没有不确定时 Cloud 才上传代表性最好的一帧，否则上传全部三帧；不默认上传完整视频 |
| Manual Evidence | Photo 1 帧；15s Video 2 Window/4 帧；60s 4/8；120s 6/12；每窗口在约 1/3 与 2/3 取帧 |
| Manual duplicate | 相似 Manual 可以从 Chapter/Aha 候选与最终精选中抑制，但 RawAsset 始终保留在事实账本和独立 Manual 窗口；跨较长时间或不同 Episode 不凭外观自动判重 |
| Signals | S03A 保存 Window 自身卡片，S03B 保存 Window 间关系 Edge；新素材只局部更新相关 Edge；低画质不等于删除；无生成式调用 |
| Observation Lite | 每个 Window 独立理解，只引用自己的 Evidence；输出固定字段 + 少量原子事实；肯定性语义条目逐项绑定 Frame 与 `STRONG/MODERATE/WEAK` 支持等级；`UNKNOWN` 记录原因而不伪造支持；无单一总置信分；仅完全相同输入可复用缓存 |
| Chapter Candidate | 只来自局部 `SINGLE / ADJACENT_GROUP / RESUMED_EPISODE / LOCAL_EPISODE_GROUP`；Normal path 至少 3 个 distinct KEEP RawAsset 和 3 个非重复内容单元；长 Manual 例外必须进入定向验证 |
| Aha Candidate | 一个 origin Moment、一个 KEEP peak、最多 3 个连续 Window/3 分钟；Local Peak × Independent Memory Value；普通 Moment 最多 3 个，Transition 最多 1 个 |
| Candidate duplicate | S07 只处理同一局部 Memory；只有已证实 duplicate/dominance 才能抑制，未确认解释保留为 alternative；全天冗余留给 S09 |
| Candidate boundary | S07 不改写 S04–S06，不做全天 Top-K，不生成 Narrative/最终媒体，不新增上传、补帧或模型调用 |
| S08 validation | 每个任务只回答一个局部问题；仅允许 Local Peak、Episode Relation、Media Diversity、Alternative Resolution；先 exact cache/结构化检查，再选择最低充分模态；Provider failure 只同级处理，只有 semantic inability 可升级 |
| S08 result boundary | Budget、policy、provider、contract failure 不等于 Evidence FAIL；只有所有必要任务 PASS 才生成不改变原内容的 ValidatedCandidate；S08 不回写 S04–S07 |
| S09 selection | current-Revision selectable pool、typed conflict graph、八层 ordered objective、deterministic set search、Preview/Final capacity 与第五章严格例外；不按 Candidate Top-K 凑数 |
| S10 media | selected Memory 内先 Beat、再 Anchor、再格式/集合/Hero；Chapter Standard 3–5、strict Compact 2；Aha 恰好一个可见媒体；HQ 只请求 selected exact interval |
| S11 narrative | Facts→Claims→Content Plan→actual text；Chapter 默认一句最多两句；Aha 单一 Moment Line≤20 中文可见字符；四分面 Canonical Tags 与 typed Entity Links 分离 |
| S12 validation | S12A 物化前 + S12B activation 后两阶段只读验证；不静默删 Memory/媒体/Claim；known-invalid prior 不 fallback；发布使用 expected-head CAS |
| S13 export | Primary/Fallback/D1/Hero activation 只能使用预声明 route；transient 不等于 terminal；affected artifacts 必须重验；User Export 与 Internal Audit 分离 |
| Moment | 连续 partition + 双向边界账本 + Multi-Prototype Context Core/Tail/Pending；允许同一语境出现不同外观，但不跨时间聚类 |
| Unresolved transition | 有限证据用尽仍不能归左/归右时，独立为内部 Transition Moment；后续只走 Aha 候选、CONTEXT_ONLY 或 DROP，不强行污染相邻 Moment |
| DEFER lookahead | 当前 Preview 内最多 2 个可用后续 Window、最长 6 分钟、Pending Block 最多 3 个；完整 seam pattern 可提前结束，提交必须原子化 |
| Observation role | 每个 accepted Observation 每个 Revision 恰好一个主角色：`KEEP / CONTEXT_ONLY / DROP_FROM_MEMORY_OUTPUT`；可有多个 reason，但不得新增第四角色 |
| Role boundary | S06 不改写 S04 facts 或 S05 membership/boundary；没有 KEEP 只退出内容候选，不删除 Moment partition |
| Truth | Perception Facts 不得被 Personalization 或 Writer 改写 |
| Upload | 用户只操作一次 Sync；App 在约 1.5h eligible、约 2h default 或 Manual/user/Final trigger 后无感批量上传 Evidence 到自有后端；Auto Raw 不默认上云 |
| Third-party exposure | 默认 Level 1 Evidence，不默认完整 Raw |
| AI 成本 | Cohort average `≤ US$1.50 / user / month`；工程目标约 `$0.90`，预警约 `$1.20` |
| 延迟 | 不追求实时；允许约 1 小时或 overnight |
| Production shape | 后续优先 `Modular Monolith + Async Worker`，不是微服务群或 Super Agent |

## 5. 当前研究实现

| 代号 | 状态 | 作用 | Leaderboard |
|---|---|---|---|
| E00 | 已实现 | 工程 Smoke：Source/Bundle → Logical Asset → 3 Frames → placeholder embedding → smoke moment → EVAL/Trace/HTML | 禁止 |
| E01 | 待正式实现 | Zero-generative baseline；第一个可比较 Moment baseline | 可以，满足 Gold/Evaluator 后 |
| E02 | 排队 | 3 Frames + same Cheap VLM | 依实验协议 |
| E03 | 排队 | Full 9s + same Cheap VLM | 仅 Benchmark Level 2 |
| E04 | 排队 | Low-res temporal proxy + same logic | 依实验协议 |
| X01 | 已打通、实验性 | App → normalized Evidence → Qwen → Chapter/Aha/Empty → Diary Home | 禁止 |
| X02 | V04.1 + Writer V02 本地候选；Web 尚未接入 | import-order day → S04 → Storyline V02 → 集合/媒体选择 → 自然表达 Writer + 格式/引用检查 → S12；失败时可复制合规完整事实，S13 未执行 | 禁止；撤回案例硬编码不等于真实质量修复 |
| P-V1 | 已实现、reference-only | S00–S10 handoff validation → S11 → S12A → S13A → S12B → S13B reference artifacts | 禁止；不是云端 Production |
| V01–V02 | 已实现、Design-Gold baseline | 日级 Gold 合同 → 六维评估 → 12 日/609 Window/16 Trial → 可追责 Scorecard | 禁止声称真实准确率 |

## 6. 当前常量速查

| 常量 | 当前值 | 状态 |
|---|---:|---|
| Auto capture interval | 120 s | Stage 1 baseline |
| Logical asset duration | 9 s | Stage 1 baseline |
| Canonical frame positions | 1.5 / 4.5 / 7.5 s; exactly 3 per valid Auto 9s | Frozen V1.3 |
| Auto Cloud upload count | 1 or 3 frames; uncertain route always chooses 3 | Frozen V1.6 |
| Auto Cloud refetch | none; insufficient one-frame evidence exits Memory candidacy | Frozen V1.8 |
| Observation logical coverage | one record slot per accepted Evidence Window | Frozen V1.7 |
| Observation context | current Window only; cross-Window continuity belongs to S05 | Frozen V1.9 |
| Observation top-level status | `OBSERVED / PARTIAL / INSUFFICIENT_EVIDENCE / FAILED` | Frozen V1.10 |
| Observation confidence | no overall score; per-item `STRONG / MODERATE / WEAK` evidence support | Frozen V1.10 |
| Moment membership | every accepted Observation appears exactly once in one contiguous provisional Moment | Frozen V1.11 |
| Non-adjacent similar content | cannot share one S05 Moment; resumed relationship belongs to S07+ | Frozen V1.11 |
| Boundary evidence | separate continuity and boundary ledgers per adjacent seam; no single score as sole truth | Frozen V1.12 |
| Boundary working state | `MERGE / SPLIT / DEFER / UNRESOLVED`; unresolved materializes as conservative split | Frozen V1.12 |
| Moment Signature | Multi-Prototype CoreContextSignature + TailSignature + PendingTransitionBuffer | Frozen V1.13 |
| Signature update | only committed MERGE updates existing Core/Tail; DEFER stays isolated in Pending | Frozen V1.13 |
| Unresolved transition fallback | isolate as internal Transition Moment; never force left/right; route to Aha candidacy, context, or Memory-output DROP | Frozen V1.14 |
| DEFER usable lookahead | at most 2 subsequent usable Windows; never read a third to rescue the current DEFER | V1.15 versioned baseline |
| DEFER capture span | at most 6 min from first Pending capture start to newest considered capture end | V1.15 versioned baseline |
| Pending Block length | at most 3 consecutive Pending Windows including the origin | V1.15 versioned baseline |
| Preview Pending output | no dangling Pending membership; resolve or materialize V1.14 fallback at input end | Frozen V1.15 |
| Observation primary role | exactly one of `KEEP / CONTEXT_ONLY / DROP_FROM_MEMORY_OUTPUT` per accepted Observation per Revision | Frozen V1.16 |
| KEEP status gate | only `OBSERVED / PARTIAL`, with at least one current-Window `STRONG / MODERATE` grounded item | Frozen V1.16 |
| Insufficient / failed routing | `INSUFFICIENT_EVIDENCE` never KEEP; `FAILED` is DROP for the committed Revision | Frozen V1.16 |
| Candidate-empty Moment | leaves content candidacy but preserves S05 membership, ledgers, facts, RawAsset and Manual window | Frozen V1.16 |
| Transition KEEP route | Aha candidacy only; S07 judges independent value and S10 judges final media quality | Frozen V1.16 |
| S07 Chapter forms | `SINGLE / ADJACENT_GROUP / RESUMED_EPISODE / LOCAL_EPISODE_GROUP` | Frozen V1.17 |
| Normal Chapter coverage | `>=3` distinct KEEP RawAsset and `>=3` non-redundant CandidateContentUnit | Frozen V1.17 |
| Long-Manual Chapter exception | 1–2 RawAsset with Manual Video and at least 3 distinct grounded Manual-window units; always provisional MEDIA_DIVERSITY validation | Frozen V1.17 |
| Relation nomination horizon | 8 committed Moments forward | V1.17 versioned baseline |
| Resumed intermediate limit | at most 2 committed intermediate Moments | V1.17 versioned baseline |
| Unsupported capture gap | 30 minutes | V1.17 versioned baseline |
| Chapter group member cap | 12 content members; interruption/context/blocker refs excluded but traced | V1.17 versioned baseline |
| Aha interval | one origin, one KEEP peak, at most 3 contiguous eligible Windows and 3 minutes | Frozen V1.17 |
| Per ordinary seed cap | 1 SINGLE + 2 grouped hypotheses + 3 Aha | V1.17 versioned baseline |
| Per Transition seed cap | 0 Chapter + 1 Aha | Frozen V1.17 |
| S08 validation frontier | Preview `<=3`, Final `<=8` provisional Candidates; count guardrail, not cost budget | V1.17 versioned baseline |
| S08 question types | `LOCAL_PEAK_CONFIRMATION / EPISODE_RELATION_CONFIRMATION / MEDIA_DIVERSITY_CONFIRMATION / ALTERNATIVE_RESOLUTION` | Frozen V1.18 |
| S08 action envelope | A2-V ≤3 frames; A2-T existing proxy ≤2 excerpts/6s; A2-A allowed audio ≤15s; A3 same or smaller payload | V1.18 versioned baseline |
| S08 weighted budget | A2-V/A2-A=1 VBU, A2-T=2, A3=4; Preview all revisions/day ≤4 VBU; all S08/day ≤16; A3 task starts/day ≤2 | V1.18 versioned baseline |
| S09 selectable pool | only current-Revision direct eligible or fully validated Candidate identity; unresolved/operational/stale never fill quotas | Frozen V1.19 |
| S09 relation constraints | typed multi-edge graph; identity conflict, must-not-co-select, unresolved at-most-one, partial-overlap cost and allowed coexistence remain distinct | Frozen V1.19 |
| S09 set objective | eight ordered quality tiers + deterministic constrained search; not candidate Top-K or one overall score | Frozen V1.19 |
| S09 Preview/Final capacity | Preview `<=4 Chapter / <=2 Aha`; Final ordinary `<=4 / <=3`; fifth Chapter requires all exceptional gates; hard Chapter cap 5 | Frozen V1.19 |
| S09 revision/output | valid published Memory has retention protection; deterministic chronological output; S10/S12 cannot silently replace membership | Frozen V1.19 |
| Chapter final media | Standard 3–5; strict Compact Gate may allow 2; exactly one body member is Hero | Frozen V1.21 |
| Aha final media | exactly one PHOTO/LIVE_2S; no independent Hero | Frozen V1.21 |
| Chapter Story | default 1 sentence, maximum 2; second sentence needs material increment | Frozen V1.22 current-Chinese test |
| Chapter Title | 2–10 visible Chinese characters; justified soft extension to 11–12; no truncation/filler | Frozen V1.22 current-Chinese test |
| Aha Moment Line | one peak-centered sentence, at most 20 visible Chinese characters | Frozen V1.22 current-Chinese test |
| X02 Chapter Story concise target | aim ≤48 visible characters; over-target is audited, not blocked; hard gate remains 1–2 sentences | Integration V1.27 experimental writing target |
| X02 Writer V02 | 模型基于事实自然概括、生成标题；不要求逐字复制，不限定物种情绪模板。保留字数/句数/引用检查；失败兜底仅复制能符合长度的完整事实 | V1.33 本地清理；格式通过不证明语义正确，尚未接入 Web |
| X02 V04.1 Aha pair | `NO_CONFLICT_EVIDENCE` 只表示未发现同峰冲突，不证明两个 Memory 确定不同；selection 按 value rank，发布再按 input/import sequence（V03 为 `sequence_index`）+ candidate ID 稳定排序 | 导入顺序不是 chronology |
| X02 unresolved coverage | `UNRESOLVED_DAY + PIPELINE_BLOCKED`；不能伪装成 semantic `EMPTY_DAY` | V1.32 candidate contract |
| X02 V04.1 result checks | live runtime fail-closed audit + committed JSON Schema + Web Bundle/health-bound validation 三层互补，任何一层不能替代另外两层 | 最终仍需真实 instance 与页面证据 |
| Canonical facets | ACTIVITY / SETTING / CENTRAL_SUBJECT / OCCASION; 0–4 assignments, at most one per facet | Frozen V1.22 |
| Display label candidates | 0–2 registry-derived candidates; App display remains optional | Frozen V1.22 handoff |
| Final validation | S12A pre-materialization + S12B post-activation; validator has no silent repair permission | Frozen V1.23 |
| HQ activation | only predeclared bounded routes; transient does not activate fallback; affected artifacts revalidated | Frozen V1.24 |
| App normalized frame | 768 × 1024, portrait 3:4 | X01/E00 compatibility baseline |
| Arbitrary-video sampling | 1/6, 1/2, 5/6 actual duration | X01/E00 compatibility baseline |
| Chapter confidence | `≥ 0.76` | X01 experimental, not calibrated |
| Aha confidence | `≥ 0.84` | X01 experimental, not calibrated |
| X01 semantic duplicate cutoff | Jaccard `≥ 0.72` | X01 experimental |
| Rich-day Chapter target | 3–4/day | Frozen V1.1 target, not quota |
| Max Chapter | 5/day; the fifth requires the exceptional gate | Frozen V1.1 |
| Max Aha | 3/day in Chapter day; exactly 1 in Highlight day | Frozen |
| X01 server asset cap | 24 | Experimental transport limit |
| X02 local test-day asset cap | 240；V04.1 S04 每批最多 3 项、18 帧、4 MiB | V1.32 stop-loss candidate；覆盖 186 项高强度日基准 |
| X02 S04 recovery | 413／明确 asset-local 错误才可二分；timeout／5xx 仅原 root batch 原样重试 1 次；400/401/403/404/422/429、普通 transport failure、invalid response 不重试不拆；item-level failure 单项重试 1 次 | singleton >4 MiB preflight 不调用 provider；失败仍继续后续 root batch |
| X02 V04.1 call circuit | Perception + Structure + Writer 全链路最多 96 次 model-call attempts | 熔断后的未覆盖资产进入 `UNRESOLVED_DAY + PIPELINE_BLOCKED` 诊断，不是假 Empty Day |
| X02 phone-test perception exposure | Photo 1 帧；Video ≤10s 为 3 帧，较长视频按实际时长形成 2/4/6 Window、每 Window 2 帧 | 当前 Web 输出 App Library Bundle V03，只保留连续 `sequence_index`、禁止伪造时间；V04.1 兼容 V01/V02，历史 X02 V03 仍只接受 V01/V02；不覆盖 Auto 9秒三帧冻结合同 |
| X02 V04.1 phone-test time truth | 当前 App Library Bundle V01/V02/V03 一律 `SYNTHETIC_SEQUENCE_ONLY`、`timeline_date = null`、time reliability 全 false | `CAPTURE_TIME` 只能由未来带 timestamp provenance/timezone/order validation 的 additive contract 开启 |
| Recommended first X01 input | 4–12 related assets from one day | Test guidance |
| X01 default model | `qwen3-vl-flash-2026-01-22` | Experimental provider choice |

## 7. 必须记住的边界

- E00 的 placeholder embedding 和两两分组 Smoke Moment **没有算法意义**。
- X01 是经用户确认的隔离实验；它没有解除“Stage 1 不做 Chapter/Aha Production”的冻结规则。
- X02 是当前真实素材 Web 默认链路，但仍只是 staged preview：它没有执行 S13、App 后台 Sync、云队列/存储、published-head CAS 或设备发布门；不得因此宣称 Production 完成。
- 相册任意尺寸/时长入口只验证兼容、Evidence 和联调，不是正式 wearable Benchmark 数据。
- App 的 `PHOTO_LIBRARY_TEST` 永远不等于 `Captured by You`。
- `Mock`, generic `/v0.3/process`, E00 和 X01 是四条不同路径，不得混称为真实算法。
- Qwen 是当前 X01 默认研究模型，不是已冻结的 Production 供应商。
- 当前 X01 的 0.76/0.84 是模型自评分硬门槛，不是校准后的真实概率。
- X01 V01 仍保留最多 4 Chapter 和单次 Preview 的实验合同；它不代表 V1.1 已实现。
- V1.17 Candidate 是内部假设，不是最终 Chapter/Aha；V1.19 S09 才决定全天集合，S10 才决定最终媒体。
- V1.17 的 122 Candidate / 188 local comparison 是高强度模拟容量推导，不是产品配额、模型调用数或真实成本测量。
- V1.18 的 VBU 是相对规划单位，不是固定美元；真实 dispatch 仍必须通过当前价格与 cohort monthly guardrail。
- V1.18 的 Budget/Policy/Provider/Contract failure 都不能被当作内容 FAIL，也不能为了凑数进入 S09。
- V1.19 的 3–4 Chapter / 2–3 Aha 是质量合格后的丰富日偏好，不是配额；S09 不新增 Raw、补帧或模型调用。
- V1.23 冻结 S12A/S12B 两阶段发布验证；本地 reference 只输出 `REFERENCE_EXPORT_ALLOWED`，不执行真实 published-head CAS。
- V1.25 reference runner 中 S00–S10 是 handoff contract validation，不是这些阶段的完整算法实现；S11–S13 也是 media-free control-plane reference。
- V01–V02 的 12 天全部是 Design Gold；`16/16 conformance` 只证明合同和错误归因自洽，不是算法准确率，也不证明真实媒体理解。
- V01 Narrative 仅允许 `zh-CN`；英文和其他海外语言必须建立 locale-specific 合同，不能复用中文字符上限。
- `EMPTY_DAY` 是合法输出，不是失败。

## 8. 当前可见 GAP

1. 冻结规则要求 `HIGHLIGHT_DAY` 恰好 1 个 Aha；当前 X01 代码可在无 Chapter 时选择最多 3 个 Aha。
2. 冻结架构是分阶段 Observation → Moment → Role → Candidate → Targeted Validation → Set Selection → Media → Narrative → Validation；X01 当前仍是一轮 Qwen 调用加本地校验。
3. X01 把模型的多 Asset Moment 映射成 App 的逐 Asset Moment，尚不是完整 Production Moment 对象。
4. X01 的 Aha 仍没有 Production `Evidence Window`/LIVE_2S；V1.21–V1.25 已有 Anchor/render 合同与 reference receipt，但没有真实媒体 render。
5. X01 仍生成自由 Tags；V1.22/V1.25 已实现隔离的 closed-registry Canonical Tag reference，但尚未替换 X01 或部署索引服务。
6. E01–E04 和真实 P1 wearable data 尚未给出能升级架构的实验结论。
7. V1.1 的滚动 Preview Revision、稳定累加、第五 Chapter gate 和增量成本不变量尚未形成 Production 实现。
8. V1.2 RawAsset Intake 的版本化 schema、IngestDelta、ledger fingerprint、quarantine 和多批次幂等尚未实现。
9. V1.3 已有固定三帧 planning，但真实 Auto 视频解码、编码、上传与 Phone compute/energy 测量尚未实现。
10. V1.4 已有 Manual Evidence planning，但真实 Manual 媒体解码、代理图编码、上传和动态/音频升级尚未实现。
11. V1.5 Signal Pack 尚未形成版本化实现，也没有真实 wearable 数据上的质量、重复、运动和 embedding 阈值。
12. V1.6 的 Phone similarity、1-or-3 route manifest 与 Manual candidate duplicate suppression 尚未实现，也没有真机节能和内容漏失数据。
13. V1.7 的全 Window Observation 记录、batch isolation 与容量规划尚未形成 Production 实现；220 Window / 28 request 仍只是容量推导。
14. V1.8 的无感上传队列、自有 backend ingestion、分层 Trace 和 `INSUFFICIENT_EVIDENCE` candidate gate 尚未实现；App/Firmware/SDK 未修改。
15. V1.9 的 WindowIntrinsicSignal/TimelineEdgeSignal schema、late insertion 局部失效和 Window-local Observation 输入隔离尚未实现。
16. V1.10 已冻结 Observation Lite 最小语义合同，但 Production JSON Schema、逐事实 Frame grounding、support grade、状态机与 exact-cache provenance 尚未实现。
17. V1.11 已冻结连续 Moment partition，但 MomentSegment/BoundaryEvidence schema、partition Validator、边界算法与真实 wearable Gold Benchmark 尚未实现。
18. V1.12 已冻结双向边界证据账本与四状态架构，但 ledger schema、聚合方法、Moment Signature schema/engine、lookahead engine、阈值与 Validator 尚未实现。
19. V1.13 已冻结多原型 Context Signature 与 commit-on-MERGE，但 Motif mapper、prototype engine、Core/Tail/Pending schema、真实数据标注和校准实验尚未实现。
20. V1.14 已冻结 unresolved Transition Moment 与三路内容路由，V1.16 已正式覆盖 S06 角色合同，V1.17 已冻结 Transition 的 Aha value/candidate gate；Transition schema、engine 与真实数据评测尚未实现。
21. V1.15 已冻结当前有界 lookahead Baseline、Pending Block、提前结束和原子提交，但 Production engine、Validator、termination schema、Revision reopening 与真实数据校准尚未实现。
22. V1.16 已冻结 S06 三角色、状态门、Transition 限制、candidate-empty 路由、重复 reason 与 S07 handoff，但 Production role schema、engine、Validator、duplicate group、shared seed 与真实数据校准尚未实现。
23. V1.17 已冻结 S07 Chapter/Aha Candidate、Long-Manual exception、局部 group/Aha/duplicate/alternative、审计、有界成本与 S08 handoff，但 Production schema、engine、Validator、persistent audit、lineage matcher、S09–S10 实现及真实用户校准尚未完成。
24. V1.18 已冻结 S08 one-question task、四类问题、动作/暴露边界、VBU/美元双重预算、缓存、失败、Revision 与 S09 handoff，但 Production schema、budget service、router、queue、persistent cache、runner、outcome aggregator、真实 provider telemetry 与用户校准尚未完成。
25. V1.19 已冻结 S09 pool、relation、set objective、deterministic search、lineage、Day State、Preview/Final capacity、fifth gate、output/readiness；Production schema、solver、persistent ledgers、state-budget benchmark、reason enum、policy migration、真实阈值与用户校准尚未完成。
26. V1.21 已冻结 S10 Beat/Anchor/Media/Hero/HQ/activation 合同，但完整 engine、真实 source resolver、renderer 与 benchmark 尚未完成。
27. V1.22–V1.24 已冻结 S11/S12/S13，并有本地 control-plane reference；真实 Writer/VLM、persistent ledger、object store、CAS、HQ media bytes 与 cloud service 尚未完成。
28. V1.25 已贯通 reference artifacts 与 failure gates，但不能作为真实云端 Production readiness、准确率、时延或成本证明。
29. V01–V02 已建立日级 Design-Gold 验证与故障归因；V03/V04 提供了真实素材失败证据，V04.1 仍需 fresh full run 与 Human-Adjudicated Gold，不能声称真实准确率或 Production 成熟度。

## 9. 当前仓库边界

- 云端研究与本文档：`diary-one-cloud-intelligence/`
- 正式 App 的临时算法/媒体 Sandbox：`device-gates/DiaryOne-RC13-Candidate-20260818/DiaryOne-iOS-Sandbox/`
- 硬件 SDK 诊断项目：保持独立；稳定能力只通过显式 device-capability 接口交给正式 App。

## 10. 更新纪律

任何新结论都必须写成：

```text
Hypothesis
→ Implementation
→ Experiment
→ Error Attribution
→ Decision
→ Checkpoint
```

如果真实实验触发架构变化，应发布新的 Canonical Checkpoint，并在本入口更新版本；不要在代码中静默改变冻结含义。
# 2026-09-15：V1.74.1 素材包 1 真实链已返回，Aha 质量未通过

- 真实复盘：[codex_V1_74_1_PACK_1_REAL_REVIEW.md](codex_V1_74_1_PACK_1_REAL_REVIEW.md)
- 冻结候选收据：`a613c4de30fdca8fa4d38c8c3bf66d5fac2f45cd021b66d8eb357052009bf96a`。
- 真实结果：20 个视频、74 帧、4 Chapters、0 Aha、15 次调用、约 ¥0.10681115；结果 SHA-256 为 `43e4bdd77c01f4f1a267352b02c9ce32c25b1bd4ce83480115fd55377fbe7a89`。
- Writer 短编号和 S04 事实代表帧通过；S09 虽看到全部 35 条事实，却选择了 3 个随后被自己判为 Chapter 同故事的候选，并漏掉未进 Chapter 的完整摊位现场。V1.74.1 不可称为真实质量修复。
- 下一步是 V1.75 的 S09 通用结构修正；不得放松重复门槛、缺失关系默认独立、只重放 S09，或切换 Web/App。
