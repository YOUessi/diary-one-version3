# codex V1.48｜包 1 新旧完整运行复盘

2026-09-04。状态：REAL_PAIR_COMPLETED_QUALITY_NOT_ACCEPTED。顾问式技术初评，不是用户评分；没有启用到测试页。

## 1. 先说结论

新版不能视为质量修复。旧版产出 2 个 Chapter、新版 3 个，两版各选出 3 个 Aha，但最终都因 Writer 输出未通过而未展示。新版的信息交接确实进入 S10/S11，然而分组、代表性和文案仍有明显问题；“更多卡片”不等于“更好的记忆”。

本轮先完成包 1 的这组对照后停止。不自动追加包 2/3、换模型或继续调提示词；不根据单图、单句新建关键词禁令。

| 指标 | 旧版 V1.45 | 新版 V1.46 |
| --- | ---: | ---: |
| 原始输入 | 20 视频 | 同样 20 视频 |
| 各自重新抽取的 Evidence | 74 帧 | 74 帧，画面指纹逐项相同 |
| 真正完成的视觉批次 | 7 | 7 |
| 仍有可用事实的素材 | 16/20 | 20/20 |
| Writer 前选中的 Chapter / Aha | 2 / 3 | 3 / 3 |
| 最终展示 Chapter / Aha | 2 / 0 | 3 / 0 |
| Chapter 精选数 | 3、3 | 5、3、3 |
| 模型调用（含既有一次 Writer 重试） | 12 | 12 |
| 输入 / 输出 token | 128,948 / 14,837 | 132,740 / 17,817 |
| 算法运行耗时，不含抽帧 | 205.10 秒 | 242.99 秒 |
| 独立抽帧耗时 | 116.41 秒 | 115.91 秒 |
| 抽帧加算法的逐版测量时间 | 约 5 分 22 秒 | 约 5 分 59 秒 |
| 模型推理估算费用 | ¥0.04159770 | ¥0.04663650 |

两版实际状态都是 `READY_WITH_ITEM_BLOCKS`：有 Chapter 可展示，但 Aha 被阻断。调用完成和 JSON/引用通过都不是质量验收。S13 HQ 物化未执行，上传公网、存储、视频渲染和正式 App 耗时/成本不在这里。

含先前测试日志错误导致的空输入调用，整轮已知模型估算总费用 **¥0.08932755（不到 0.09 元）**；所有 25 次真实调用均有 token 用量，没有把未知用量记成零。这不是典型高强度用户日，更不是单用户月度账单；本轮没有显著成本压力，继续按用户指示暂不做严格成本优化。

## 2. 为什么不能把变化都归因于新版

两版采用相同模型 `qwen3-vl-flash-2026-01-22`、相同帧、相同导入次序。7 个 S04 请求的提示词指纹、Schema、Evidence 编号与图像指纹均完全相同，但模型输出不同：

- 旧版 M04/M05/M06 的英文事实分别长 463/491/474 字符；M16 两条分别 238/229 字符。程序现有 200 字符上限把这些事实过滤，四段素材没有事实继续进入分组。
- 新版这些素材恰好返回较短的中文事实，因此全部保留。S04 没有代码变更，不能把这 4 段的恢复称为 V1.46 交接模块的效果。
- 同一 M17，旧版给出高显著程度的动物事件，新版给出 NONE/NONE；M12 的发现事件判断也不同。这说明上游标签存在本轮可见的波动，不证明哪次必然正确。
- 两版分组已经不同，S10/S11 比较的也不是完全相同的候选集合。完整运行可显示端到端表现，单次一对不能隔离交接模块的因果收益。

## 3. 本轮确认的问题与位置

| 编号 | 位置 | 真实证据 | 共性问题与下一步 |
| --- | --- | --- | --- |
| P1 | S04 事实接收 | 旧版 M04/05/06/16 都有模型事实，却因文本超过 200 字符而丢尽；画面仍保留 | 长度/语言不合格式被转成“无足够证据”，扩大了素材损失。优先审查事实保存与展示长度的职责分离；证据引用仍须正确，不截断原文伪造事实、不直接放宽全部校验 |
| P2 | S11 文案及重试 | 两版各 3 个 Aha 全部未展示；旧版重试仍超长，新版重试把相同编号同时放入 Chapter 和 Aha | 内容已选好却在表达出口丢失。下一阶段单独修复 Writer 的输出合同/重试可靠性，不把问题误认成没有精彩素材，也不改成强制凑 Aha |
| P3 | S05–S07 分组 | 新版 C2 = M03 祈福景物 + M09/M15 林径；共同说明称为带精神元素的林间旅程 | 主题说明写得通，不等于分组关系足够成立。当前无时间/GPS，不能由“树木/石阶”推成同段游程；需对共同体验是否成立作真实组级评价 |
| P4 | S10 代表性 | 新版 C3 从 9 项选 3 项，只留 M08/M10/M17，M11/M14/M19 沿河画面全部省略 | 精选可能保住差异，却丢掉这章最重要的一类体验。需评价“整个精选集合代表什么”，不是按建筑/河流规定必选名额 |
| P5 | S11 重点与可信度 | 新版 C1 加“在阳光下”；C2 写“山野间的信仰轮廓”；未展示 Aha 写“朱红如血”“岁月重量” | 有内容说明仍会铺陈、夸饰或补关系。按具体句子对照事实和画面评价，不增加这些词的运行时黑名单 |

P1 的直接代码证据：`x02.py` 的事实接收使用 `_bounded_string(..., 1, 200, "fact.text")`；发送给模型的事实 Schema 仅规定 string，没有相应 maxLength，提示词要求简洁中文，但本轮没有稳定遵守。M17/M18 另各丢掉一条超长事实，尚有其余事实存活。不是虚构反例，不是图片损坏，也不是预算裁掉素材。

优先顺序建议：**先处理可确定的事实误丢和 Writer 出口失败，再改组级与精选质量。** 两者拆成短阶段交付，不同时重写整条链路。这里是后续建议，不是本轮已经实施的算法变化。

后续记录：P1 已由 [codex V1.49 S04 事实保留检查点](codex_CHECKPOINT_V1_49_S04_FACT_RETENTION.md) 在当前 V04.1 本地实现并用本轮七批真实原始回复完成确定性回放验证；V1.48 本页原始结果和质量结论不改写。P2 及其余问题仍未解决。

## 4. 最终 Chapter 原文与逐卡初评

以下文字为未改写的真实输出。M 编号仅为固定导入编号，不是时间；点击编号可看原抽帧。标题、内容、素材均可分别给建议。

### 旧版

#### 旧版 C1｜雨中市集

中式牌坊'种山秀'下，湿滑石板路上摊位林立，行人撑伞穿行，一男子在菜摊前低头整理蔬菜，白色顶棚摊位设饮料设备，橙色招牌标有'运'字及'衢州烤饼'。

- 分组成员：[M01](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_3c580d3e-79d4-4b7c-8282-4e5dd5951615/frame_w00_1500.jpg>)、[M02](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_4c991c5e-f49c-4bbb-84f2-cf53cccac115/frame_w00_1500.jpg>)、[M07](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_89268a3d-d40f-4673-85c0-aafad5ad1cb9/frame_w00_1500.jpg>)、[M12](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_9c0a663b-dd6e-42f5-84f2-e030fc50dbf4/frame_w00_1500.jpg>)、[M18](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e18ac5d7-f97d-45f3-8c5d-1738f0086ca9/frame_w00_1500.jpg>)。
- 最终精选：[M01](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_3c580d3e-79d4-4b7c-8282-4e5dd5951615/frame_w00_1500.jpg>)、[M07](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_89268a3d-d40f-4673-85c0-aafad5ad1cb9/frame_w00_1500.jpg>)、[M12](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_9c0a663b-dd6e-42f5-84f2-e030fc50dbf4/frame_w00_1500.jpg>)；封面：[M12](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_9c0a663b-dd6e-42f5-84f2-e030fc50dbf4/frame_w00_1500.jpg>)。
- 完整记录编号：`9383c71d-280f-5af2-9f17-58bf1f6b3519`。

初评：市集方向大体清楚，但文案逐项报物，73 个可见字符，重心散；把餐饮摊与菜市场归为同一集市体验是否合适，仍需用户评价。

#### 旧版 C2｜古镇步道

石碑刻'古越龍山'立于绿树石阶旁，沿河石板路铺展，白墙黑瓦倒影水中，远处石桥横跨，一人背对镜头行于台阶，右侧可见红灯笼与白墙黑门建筑。

- 分组成员：[M03](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_1500.jpg>)、[M08](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w00_1500.jpg>)、[M13](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_1500.jpg>)、[M14](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_8978b0fc-1868-486a-8fa5-fed6a2a5a6dc/frame_w00_1500.jpg>)、[M19](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w00_1500.jpg>)。
- 最终精选：[M13](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_1500.jpg>)、[M14](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_8978b0fc-1868-486a-8fa5-fed6a2a5a6dc/frame_w00_1500.jpg>)、[M19](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w00_1500.jpg>)；封面：[M13](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_1500.jpg>)。
- 完整记录编号：`3ced4bf7-1d67-5610-b530-35323cdad0c2`。

初评：文化发现与水边漫步仍混在一章；最终精选两段沿河画面加石碑，祈福牌和牌坊被省略。67 个可见字符的文案仍像画面清单。

### 新版

#### 新版 C1｜古街市集的湿石与烟火

牌坊下湿滑石板路上，摊贩陈列着豆角、番茄与青瓜，一旁“运汤 瑞阳宴集”摊位挂起橙灯，冰激凌甜筒在阳光下格外醒目。

- 分组成员：[M01](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_3c580d3e-79d4-4b7c-8282-4e5dd5951615/frame_w00_1500.jpg>)、[M06](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_09b55a58-2bdd-4309-8ba5-376c095cf058/frame_w00_1500.jpg>)、[M07](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_89268a3d-d40f-4673-85c0-aafad5ad1cb9/frame_w00_1500.jpg>)、[M12](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_9c0a663b-dd6e-42f5-84f2-e030fc50dbf4/frame_w00_1500.jpg>)、[M18](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e18ac5d7-f97d-45f3-8c5d-1738f0086ca9/frame_w00_1500.jpg>)。
- 最终精选：[M01](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_3c580d3e-79d4-4b7c-8282-4e5dd5951615/frame_w00_1500.jpg>)、[M06](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_09b55a58-2bdd-4309-8ba5-376c095cf058/frame_w00_1500.jpg>)、[M07](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_89268a3d-d40f-4673-85c0-aafad5ad1cb9/frame_w00_1500.jpg>)、[M12](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_9c0a663b-dd6e-42f5-84f2-e030fc50dbf4/frame_w00_1500.jpg>)、[M18](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e18ac5d7-f97d-45f3-8c5d-1738f0086ca9/frame_w00_1500.jpg>)；封面：[M01](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_3c580d3e-79d4-4b7c-8282-4e5dd5951615/frame_w00_1500.jpg>)。
- 完整记录编号：`ee127167-b73c-52c5-8276-2403d8cec1cd`。

初评：五项可看到入口、市场环境、摊位人物、餐饮摊、室内陈列，不能只因均有蔬果就判重复。M06/M07 有内容重叠但主体侧重不同，是否值得同时保留待评分。文案把不同素材接成“一旁”，又添加事实里没有的“阳光”，且仍超出 48 字预览写作目标（55 字）。

#### 新版 C2｜林径上的红灯笼与石阶

石板小径蜿蜒于林间，枯叶铺地；红灯笼树与祈福牌悬垂木构，石桥横跨水道，静默勾勒出山野间的信仰轮廓。

- 分组成员：[M03](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_1500.jpg>)、[M09](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_1500.jpg>)、[M15](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_1500.jpg>)。
- 最终精选：[M03](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_1500.jpg>)、[M09](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_1500.jpg>)、[M15](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_1500.jpg>)；封面：[M15](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_1500.jpg>)。
- 完整记录编号：`f07c3c4a-cdcf-5385-a178-0fa9df8d2eda`。

初评：将祈福景物与两段林径归在一起，共同体验关系仍不清楚；不是因为有 3 项就算聚类成立。文字还用“信仰轮廓”解释场景，超出具体体验。49 字，形式上 2 句不能证明内容自然。

#### 新版 C3｜禹贡古村的巷陌回响

石板巷通向“禹贡古村”牌坊，红灯笼高悬；白墙院落中祈福牌错落，长毛犬奔过街面，电动观光车悄然停驻石阶旁。

- 分组成员：[M04](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_82575557-6628-4715-82e5-73f3f761fcc4/frame_w00_1500.jpg>)、[M08](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w00_1500.jpg>)、[M10](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_bec8a5dd-76b0-4c98-8019-818e3d403378/frame_w00_1500.jpg>)、[M11](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_dba5ff94-dbad-47a5-82c8-fdc040ea1b6c/frame_w00_1500.jpg>)、[M13](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_1500.jpg>)、[M14](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_8978b0fc-1868-486a-8fa5-fed6a2a5a6dc/frame_w00_1500.jpg>)、[M16](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_8122576f-bfde-4917-814a-b2ac71e3fd08/frame_w00_1500.jpg>)、[M17](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_db700757-e55b-42c2-844e-ce363310a578/frame_w00_1500.jpg>)、[M19](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w00_1500.jpg>)。
- 最终精选：[M08](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w00_1500.jpg>)、[M10](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_bec8a5dd-76b0-4c98-8019-818e3d403378/frame_w00_1500.jpg>)、[M17](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_db700757-e55b-42c2-844e-ce363310a578/frame_w00_1500.jpg>)；封面：[M17](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_db700757-e55b-42c2-844e-ce363310a578/frame_w00_1500.jpg>)。
- 完整记录编号：`7f1d4d69-e287-5551-8c83-4b935de9c673`。

初评：原主题涵盖巷道、河景、碑刻，最终却只留牌坊、院落和犬的街巷片段，沿河体验全部消失。素材数量满足 3 项，但代表性仍不理想；标题还依赖未核准的招牌识字。52 字文案把门面、犬和观光车逐项拼接。

## 5. Aha 去向：有候选，最终无展示

旧版选中 M09 林间犬、M13 石碑、M17 巷中犬；新版选中 M03 祈福景物、M09 林间犬、M13 石碑。这些是机器候选，值得不值得单独成为 Aha 仍需人评，尤其要核查与 Chapter 的故事重叠。

| 版本 | 首次草稿 | 长度 | 重试结果 |
| --- | --- | ---: | --- |
| 旧版 | 棕白相间的狗背对镜头沿落叶覆盖的弯曲石径前行，尾巴摇动。 | 28 | 仍 28 字，未通过 20 字上限 |
| 旧版 | 石碑上红色'古越龍山'字样在绿树环绕的石阶旁清晰可见。 | 27 | 仍 25 字，未通过 20 字上限 |
| 旧版 | 戴蓝Harness的狗沿石板巷走远，红灯笼悬于白墙之上，电车驶过，茶店'洪明茶'门面可见。 | 45 | 仍 28 字，未通过 20 字上限 |
| 新版 | 悬挂红流苏的木质结构前，石桥与涂白树干静立，白墙黑瓦在背景里低语着古老仪式。 | 38 | 同编号同时返回在 chapters/ahas，WRITER_ITEM_DUPLICATED |
| 新版 | 棕白相间的狗披着浅色背带，沿不规则石板路向前走去，身后是密林与枯叶铺就的幽深路径。 | 41 | 同编号同时返回在 chapters/ahas，WRITER_ITEM_DUPLICATED |
| 新版 | 石阶旁绿树环抱，一方石碑上‘古越龍山’四字朱红如血，无声标记着此地曾有的岁月重量。 | 41 | 同编号同时返回在 chapters/ahas，WRITER_ITEM_DUPLICATED |

新版重试还生成了 23/26/26 个可见字符的 Aha 文字（沿用程序计数，包含标点、不计空白），即使忽略重复编号，仍未达到 20 字要求。这里不自动忽略错误、不绕过校验；保留原回复用于下一阶段处理。最终确定性回退也未成功，故没有 Aha 出口。这不是“所有 Aha 都被相似度砍掉”。

## 6. 分步骤费用与耗时

时间为每阶段真实调用耗时之和，含请求/传输等待；非模型思考时间。token 为供应商返回用量。费用使用本轮记录的北京模型阶梯价估算，不是结算账单。

| 版本 | 阶段 | 调用 | 秒 | 输入 token | 输出 token | 估算元 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 旧版 | S04 | 7 | 131.22 | 90,881 | 9,001 | 0.02713365 |
| 旧版 | S05–S07 | 1 | 47.25 | 12,553 | 3,890 | 0.00771795 |
| 旧版 | S10 | 2 | 10.12 | 11,082 | 660 | 0.00265230 |
| 旧版 | S11 | 2 | 16.43 | 14,432 | 1,286 | 0.00409380 |
| 新版 | S04 | 7 | 119.40 | 90,881 | 8,774 | 0.02679315 |
| 新版 | S05–S07 | 1 | 79.88 | 14,180 | 6,004 | 0.01113300 |
| 新版 | S10 | 2 | 13.00 | 19,627 | 812 | 0.00416205 |
| 新版 | S11 | 2 | 30.64 | 8,052 | 2,227 | 0.00454830 |

S04：看图提取事实；S05–S07：组织分组和候选；S10：选展示素材；S11：写文案及原有一次重试。其他本地确定性步骤无模型 token，时间包含在整条算法运行中；逐步骤明细保留在原 report 的 stage_metrics 中。不得把无模型 token 等同没有服务器成本。

## 7. 素材核对表

初评已查看每份素材的首帧，以及 M03/06/07/09/12/17 的后段抽帧，共 26 张；未声称逐帧观看全部原视频。每份视频全部 3–4 张 Evidence 都已送入本轮视觉模型。下表仅作找素材索引，不是新分类词表或训练标签。

| 编号/首帧 | 内容索引 | 原文件 |
| --- | --- | --- |
| [M01](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_3c580d3e-79d4-4b7c-8282-4e5dd5951615/frame_w00_1500.jpg>) | 牌坊下的市集 | 04179d4c3503adbfa13bf00bad1ffb39.mp4 |
| [M02](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_4c991c5e-f49c-4bbb-84f2-cf53cccac115/frame_w00_1500.jpg>) | 路口与车辆 | 07e8712ba4f03e661543095f2de97f78.mp4 |
| [M03](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_1500.jpg>) | 祈福牌、石桥、挂灯笼的树 | 09ed75eff07f6aac0133ab3e542c4b3d.mp4 |
| [M04](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_82575557-6628-4715-82e5-73f3f761fcc4/frame_w00_1500.jpg>) | 盆景陶罐与巷道 | 250b1bad4d5d8da24c53ebe4151bb7ab.mp4 |
| [M05](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_896e37a7-d0dc-47d9-8e48-c4bd56797214/frame_w00_1500.jpg>) | 牵犬行走与院落 | 2887772e70f96d7ca9c19788cfd22751.mp4 |
| [M06](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_09b55a58-2bdd-4309-8ba5-376c095cf058/frame_w00_1500.jpg>) | 市场三轮车与蔬果摊 | 38b14f584a73d255b2dd64f74bf85158.mp4 |
| [M07](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_89268a3d-d40f-4673-85c0-aafad5ad1cb9/frame_w00_1500.jpg>) | 摊位人物与蔬菜 | 40312a8b2cae7d70627308cf9b02e137.mp4 |
| [M08](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w00_1500.jpg>) | 古村牌坊与巷道 | 522e4d072f337def753aed8c7a94ed1c.mp4 |
| [M09](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_1500.jpg>) | 林间小径与犬 | 6576b04fcedee8130e6c9d1650be78e0.mp4 |
| [M10](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_bec8a5dd-76b0-4c98-8019-818e3d403378/frame_w00_1500.jpg>) | 传统院落 | 7452dabf532b1523cd6603b58dc17122.mp4 |
| [M11](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_dba5ff94-dbad-47a5-82c8-fdc040ea1b6c/frame_w00_1500.jpg>) | 沿河步道与小船 | 8a1e021316c7825618fc85ba70d5da7c.mp4 |
| [M12](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_9c0a663b-dd6e-42f5-84f2-e030fc50dbf4/frame_w00_1500.jpg>) | 帐篷餐饮摊 | 9efd85d7058904b564a37946fb5a4fc2.mp4 |
| [M13](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_1500.jpg>) | 石碑与石阶 | b719cb94a859f6662df605abfc7b0b43.mp4 |
| [M14](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_8978b0fc-1868-486a-8fa5-fed6a2a5a6dc/frame_w00_1500.jpg>) | 水道倒影与石桥 | be742b95d01d6152ac0d325b9e8e3bf1.mp4 |
| [M15](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_1500.jpg>) | 林间石阶 | c9a75a21437b5d5462cf39a8c0cbba28.mp4 |
| [M16](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_8122576f-bfde-4917-814a-b2ac71e3fd08/frame_w00_1500.jpg>) | 传统建筑外观 | d0d0dc192e11c9a244b79518023ffa1e.mp4 |
| [M17](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_db700757-e55b-42c2-844e-ce363310a578/frame_w00_1500.jpg>) | 犬、巷道与店面 | e3dd8d2dd50b48518221f35ef2d5b94f.mp4 |
| [M18](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_e18ac5d7-f97d-45f3-8c5d-1738f0086ca9/frame_w00_1500.jpg>) | 室内蔬果陈列 | f1434c6d71a443e8641d1bab33fbbe0e.mp4 |
| [M19](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w00_1500.jpg>) | 沿河步道 | f5840e15a65526b128c68a22385a5247.mp4 |
| [M20](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/evidence/asset_c2208cb2-0bc4-4d2a-8541-54801f13c8b0/frame_w00_1500.jpg>) | 车内窗外 | f6ceb60207848d6bc74c8c4fd18638d7.mp4 |

## 8. 边界与可复核记录

- 执行与授权、两版源码指纹、失败适配记录见 [V1.48 检查点](codex_V1_48_PERSON1_FULL_PIPELINE_COMPARISON.md)；输入清单与冻结源码见 [V1.47](codex_V1_47_FULL_PIPELINE_AB_PREPARATION.md)。
- 本轮只发送已获明确授权的包 1 正规化图像与相关文字到北京百炼；原视频未发送，未公开发布。
- 本轮只修复实验日志适配器；两版冻结算法、模型、数量、阈值和质量规则均未临时更改；已确认新源码内容说明政策进入实际流程。
- 原始结果：[旧版报告](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/baseline/codex_attempt_02/codex_full_run.json>)、[新版报告](<ORIGINAL_REPOSITORY/var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/candidate/codex_attempt_02/codex_full_run.json>)。对应目录内 codex_stage_calls 逐次保存输入提示词、画面编号/指纹、模型原回复和用量；不保存 API key。
- 用户评分待收集：可以按“新版 C3 → M17 → 是否应保留”“新版 C1 → 第二处表达 → 修改建议”提供颗粒化建议。这里的初评不写成用户评分，不自动据此调整算法。
- 不修改/重启测试页，不触碰正式 App、Firmware/SDK、共享状态和长期记忆；不推送含其他阶段未提交修改的混合工作区。后续 Web 启用必须明确核对运行版本，不能把本次孤立对照误称为你已在 Web 跑过新版。
