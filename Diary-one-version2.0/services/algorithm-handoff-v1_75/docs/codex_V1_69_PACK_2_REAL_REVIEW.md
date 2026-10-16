# codex V1.69｜素材包 2 全新链路复盘

日期：2026-09-07。结论：**真实研究链完成，分组有正向进展，但成品质量仍未接受。**

## 1. 先看结论

本轮重新读取 20 张照片、6 个视频，标准化为 39 张证据图，完整运行现有 S04–S12 研究链；不复用旧语义事实。产出 **4 Chapter / 3 Aha**，生成约 **3 分 35 秒**，14 次 API，公开价快照估算 **¥0.06943845**。

最重要的正向结果：夜间餐车与小吃 18、19、20 自己成章，没有混入室内火锅；室内两件没被硬凑成章，16 的夹肉瞬间仍成为 Aha。鹿 Chapter 与鹿 Aha 的同故事关系本轮完整提供，三个重复鹿 Aha 被抑制。

但结果不能接受为成品：两章被 Writer 写反编号后退回通用标题/事实描述；驼群卡片出现从视觉事实一路传到文案的“两人骑乘”错误；Aha 仍偏长并有未被支持的叙事扩写。

本轮只运行包 2 一次，不修改算法/Prompt/模型路由，不重跑挑结果，不启动包 3，不切换 Web/App，不改 Firmware/SDK、R2、共享状态或长期记忆。S13 高清素材回取/正式导出未执行。本报告是算法侧技术与内容审阅，不是用户评分或 Production 验收。

## 2. 链路与素材去向总览

| 环节 | 本轮实际结果 |
|---|---|
| 本地标准化 | 26 个原素材重新处理、39 帧；无拍摄时间/GPS因子 |
| S04 看图与事实 | 9 个原计划批次全部返回，无单项重试；26 个观察、26 条事实保留；9 项非关键字段降级，0 观察失败 |
| S05–S07 整理/提案 | 19 个 Moment、5 个 Chapter 提案；S07 Plus 短编号未知引用 0 |
| S08–S09 整日选择 | 5 选 4 Chapter；6 个有效 Aha 候选选 3，另外 3 个因与鹿 Chapter 同故事被抑制 |
| S10 精选 | 鹿 4 选 3、驼群 4 选 3、驾车 5 选 3，各一次视觉调用；夜间组正好三件，无额外精选调用 |
| S11 文案 | Flash 一次写 7 张；5 条模型文案通过格式/引用，2 条编号错配被拒后使用本地事实兜底；未调用 API 重写 |
| S12 | 技术结果完整，S11 标记 COMPLETED_WITH_GROUNDED_FALLBACK；不代表七张都是合格成品 |

5 个 Chapter 候选分别是：

| 候选 | 成员编号 | 最终 |
|---|---|---|
| 鹿的具体遭遇 | 6、7、8、9 | C1：6、7、8 |
| 同一环境的驼群 | 10、11、12、13 | C2：10、11、13 |
| 夜间餐车与小吃 | 18、19、20 | C3：18、19、20 |
| 室内用餐 | 16、17 | 不足三件未成章；16 进入 A2 |
| 驾车沿途 | 21、22、23、24、25 | C4：21、22、23 |

最终卡片覆盖 **15/26 个不同素材**，其余 11 个仍在事实记录中。以下 1–26 是导入编号，不是拍摄时间；不从文件名或导入顺序推断真实行程。模型在内部使用 ENTRY/EXIT 或“到达—等候—吃到”之类解释，并不能证明这条时序。

## 3. 七张最终卡片：原文与逐项评价

以下照录真正的最终输出，不用被拒的 Writer 草稿冒充成品。Aha 标题是内部定位，正文才是主要展示内容。字数取最终通过的那条记录；特别注意不能把 C3/C4 被拒草稿的字数当成兜底正文的字数。

### C1｜长角鹿穿行于城郊

一只长角鹿在铺装院落中踱步，又低头啃食草边灌木，旁人举手机记录下它自在的身影。

素材：6、7、8；最终正文 39 个可见字符；来源：模型文案。

审阅：分组与精选基本成立：院落中的鹿、低头进食、旁人举机记录，是同一具体遭遇的不同侧面。7、8 画面相似，但 8 增加了人的拍摄行为，不能只凭背景相同就砍章。三个鹿 Aha 被明确 SAME_STORY 关系抑制，没有与本章重述。这是关系填写完整时原机制有效的正向证据。内部的 ENTRY/EXIT 不能证明照片真实先后。

### C2｜草原上的双峰驼群

多只双峰驼散落于开阔草地，远处山影与电塔相映，其中一匹驮着两人缓缓前行。

素材：10、11、13；最终正文 36 个可见字符；来源：模型文案。

审阅：同一驼群和连续可对应的环境支持合章；11、12 高度相似，最后保留 11 而省略 12，是正常精选。但“两人骑乘”不受 11 的证据图及原始照片支持；画面看到的是双峰。S04 先写错，S07 把它当作 PEAK，S10 还称它为“人文互动”的差异化贡献，Writer 最后写进成品。不能把四阶段重复说同一个错误当成四份独立证据。

### C3｜生活片段

夜间户外街景，可见一辆蓝橙色餐车停于路边，前方有白色低矮护栏，背景有路灯、树木、停放车辆及数人坐于户外。

素材：18、19、20；最终正文 52 个可见字符；来源：本地完整事实复制兜底。

审阅：夜间餐车远景、顾客近景、桌面小吃三件独立成章，没有拉入室内 16、17，修复方向在本轮真实分组上成立。但 Writer 给本章编号配上了驾车文案和驾车事实引用，原校验拒绝后复制本章的一条事实兜底，所以最后标题是“生活片段”，正文是较长的原始观察，而非模型写出的“夜市烟火气”。素材本身没有被换错。

### C4｜生活片段

从车内视角拍摄的高速公路场景，前方有多个车道，远处可见山脉和右侧居民楼，车速平稳行驶，仪表盘显示娱乐内容及导航界面。

素材：21、22、23；最终正文 58 个可见字符；来源：本地完整事实复制兜底。

审阅：五段驾车视频的共同经历基本清楚；最终选了 21、22、23。21 与 22 的公路/中控画面很相似，S10 用“外部风景/车内技术”解释其差异，但两段都已有这些内容，第二个槽位的新增价值值得比较。24、25 的山路被省略。Writer 编号互换后本章也退回事实描述；这不是第二个夜市 Chapter。23 后段乘客微笑确有画面支持，但 S10 实际只看到该视频首帧的道路图，其关于人物的判断依赖上游文字。

### A1｜相机静立台阶

三台单反相机并排置于户外台阶，镜头朝前，背带印着‘EOS 70D’字样，暗示一场未开始的拍摄。

素材：3；最终正文 46 个可见字符；来源：模型文案。

审阅：三台相机并列是真实且可以有趣的小发现；只有两张相似相机照片也可以独立产出 Aha，无须强凑 Chapter。正文加入型号并补写“未开始的拍摄”，而图像只能证明设备摆放，不能证明拍摄尚未开始。S07 的摄影活动建议仅是编辑说明，不是事实；是否受其影响需要单变量验证，不能在这里断言唯一原因。

### A2｜筷尖夹起焦香

一人用筷子夹起烤肉片，火锅、烤盘、酸黄瓜与调味碟围坐桌边，灰台面映出烟火日常。

素材：16；最终正文 39 个可见字符；来源：模型文案。

审阅：室内餐食没有凑够 Chapter，但其中夹起烤肉的瞬间进入 Aha，符合小素材包仍可保留精彩的目标。它与夜间小吃属于不同具体经历，本轮未发现同故事重述。文案仍罗列锅、盘、酸黄瓜、调料、台面，焦点被稀释；这些细节不必因为可识别就全部写出。

### A3｜荒地拾得橙色

黑衣人蹲在灌木旁，俯身注视沙地上散落的橙色物件与纸片，无声的细节里藏着偶然的发现。

素材：26；最终正文 41 个可见字符；来源：模型文案。

审阅：原事实说人站在灌木旁低头看地面，Writer 却写“蹲在灌木旁”；所提供的三帧也不支持这个新增姿态。“偶然的发现”只是评价性包装，橙色物件具体是什么、为什么值得记住，本轮证据未说明。该候选被 DISCOVERY/MEDIUM 纳入后入选，不能据此断言它就是有用户价值的 surprise，也不应该反过来硬规定普通物件不能做 Aha。

## 4. 真实问题一：分组正确，Writer 配错卡片编号

这不是 S07 编号还原错误，也不是程序把输入章节顺序传错。已逐项核对 Writer 发送内容和原始返回：

| 固定 Chapter 编号 | 请求时绑定的素材/事实 | Writer 返回的内容/事实 |
|---|---|---|
| `dfbee641-5d28-5212-8fc8-0103c7343658` | 夜间 18、19、20 | “车窗里的风景流转”，引用 21、22、23 |
| `dbe18cea-4ad6-562f-b6d5-9f51f76a55c0` | 驾车 21、22、23 | “夜市烟火气”，引用 18、19、20 |

两组编号都是合法存在的编号，但绑定对象不对。现有 `WRITER_CLAIM_REFERENCE_INVALID` 检查正确阻止错配正文发布；之后按此前单次 Writer 政策直接复制各自 Chapter 的一条事实，没有 API 第二轮。

所以最终两章**没有展示别章的素材或文案**，但都变成“生活片段”与 52/58 字的观察描述，丢掉了自然文案和主题标题。技术兜底保住卡片不等于满足产品体验。审计中的 fallback attempt=3 是内部阶段编号，实际 Writer API 只有一次，不是调用了三次。

后续优化方向：优先减少多卡内容与长编号配对的负担，让绑定尽量由程序保持；用这次真实回复检查既有保护，再以单变量研究比较简化输出/请求内编号等方案。不关闭引用校验、不按文意猜着交换两个结果、不反复生成碰运气。**S07 的短编号已经有效，不代表直接照搬到 Writer 就必然解决这次互换。** 本轮未实施这些方案。

## 5. 真实问题二：错误视觉事实被后续当作可靠依据放大

素材 11（`11.jpg`）的标准化图和原始照片均核看：可见双峰骆驼，没有支持“两人骑乘”的画面。可追踪路径是：

1. S04 将 11 写成“一只背负双人骑乘”，12 也出现类似描述，并自标 STRONG。
2. S07 引用该事实，把它指定为驼群 Chapter 的 PEAK。
3. S10 虽再次接收图像，仍说该画面是“双人骑乘”的“特写”，据此解释为什么它提供了人文互动的不同侧面。
4. S11 写出“其中一匹驮着两人缓缓前行”。引用编号全部合法，因此格式/引用校验通过。

这里真正暴露的是：**上游解释被重复使用，后续的文字一致性容易被误当作真实支持**。不能从一次运行判定模型为什么误认，或断言换分辨率/换模型就能修复；也不能因本例新增“骆驼规则”。

后续优化方向：保留这个真实案例，结合包 3 检查类似的证据强度问题；优先研究现有看图任务对“可确认事实/不确定推断”的区分，以及 S10 对图片和上游文字的依赖。若做对照，应保持原图不变，比较有/无上游叙事提示等单变量；先证明改善，再考虑接入。不是给全部素材追加一层昂贵复审或构造语义反例。

## 6. 跨包共性与尚需评价的取舍

### 已有跨包证据

- **Writer 聚焦不足和无依据扩写：** 包 1 三条 Aha 为 40/44/40 字，包 2 为 46/39/41 字；六条全部超过 24 字容差，且都已经正确标记偏长。包 1 的“消失于小径尽头”、包 2 的“尚未开始拍摄”与“站着改成蹲着”均是实际输入/输出差异。不是缺少字数提示，不能再只靠堆提示或重写来解决。
- **Chapter/Aha 关系完整性决定结果：** 包 1 小狗关系缺失，最终重复；包 2 鹿关系完整，三个重复 Aha 正确退出。说明当前机制不是一概失效，重点应是重要卡片对的关系是否完整、是否与最终选择仍对应。未提供关系的无关组合不能全部算质量错误。
- **精选的文字理由不等于真实视觉增量：** 包 2 的两段公路很相似，却被解释成两个明显不同侧面；驼群则将不存在的骑乘当作视觉差异。不能只查看“模型理由写得通顺”就验收精选。包 1 的小狗边缘画面问题也指向素材质量与具体瞬间价值并非同一件事。

### 不直接定为错误

- 室内两件没成章是最低三件规则正常工作，且保留一个用餐 Aha，不能因此说内容全被砍掉。
- 7、8 两张鹿图相似，但 8 有旁人举机的独立贡献，未判定必须删到两件导致整章消失。
- 21、22 两段公路高度相似，建议把其新增价值与 24/25 山路比较；不是立即硬删，也不先规定驾车必须几种景观。
- 26 的橙色物件是否是有意义的小发现，需要用户兴趣与真实情境判断。系统选了三条不等于三条都值得保留；但也不按物件类别禁止它成为 Aha。
- 没有可靠时间时，图片可以支持同一环境/共同经历，却不能直接推出“先遇鹿后吃饭”等全天次序。

## 7. 所有素材的去向与画面回查

本次目视核查了全部 39 张标准化证据图，并额外查看 11.jpg 原始照片。未逐秒播放全部原视频，不声称已评估所有快速事件的抽帧遗漏。

| 编号 | 原文件 | 主要内容及去向 | 本轮证据图 |
|---|---|---|---|
| 1 | 01.jpg | 走廊与门；未进入 Chapter/Aha，事实保留。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_456800df-070a-475b-811b-43073442eaf2/frame_w00_4500.jpg>) |
| 2 | 02.jpg | 荒野公路、旗帜、远山；未进入 Chapter/Aha，事实保留。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_1b289519-642f-4d39-8c15-89cd78939733/frame_w00_4500.jpg>) |
| 3 | 03.jpg | 三台相机俯视；A1。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_8b30f98f-34a7-46ca-8fba-68d781e02f77/frame_w00_4500.jpg>) |
| 4 | 04.jpg | 同组相机侧面；未独立成卡，与 3 高相似，未发现必须再展示的理由。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_8c25f06c-ebfc-4f30-8e2f-a684c9d6023e/frame_w00_4500.jpg>) |
| 5 | 05.jpg | 车内乘客戴耳机休息；未进入候选，事实保留。是否值得留下需用户兴趣评价。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_4ffe5f31-1b0d-4632-8908-ecf833951d13/frame_w00_4500.jpg>) |
| 6 | 06.jpg | 鹿在院落行走；C1；其 Aha 被同故事关系抑制。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_fcf21b8d-4b1c-465d-8412-d54d4b64ed2d/frame_w00_4500.jpg>) |
| 7 | 07.jpg | 鹿低头进食；C1；其 Aha 被同故事关系抑制。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_b4932556-36f9-4f8a-81d7-b6eea152f43c/frame_w00_4500.jpg>) |
| 8 | 08.jpg | 旁人拍摄进食的鹿；C1；其 Aha 被同故事关系抑制。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_c301f5c6-dd37-4378-8132-58d84d762e74/frame_w00_4500.jpg>) |
| 9 | 09.jpg | 院落/道路上的鹿与行人；进入鹿 Chapter 候选，S10 未选入。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_d3467699-5c9e-42d1-83e6-74abb124d4d0/frame_w00_4500.jpg>) |
| 10 | 10.jpg | 开阔地驼群；C2。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_9fe84abc-8d5e-4dcf-8b77-a1865f300721/frame_w00_4500.jpg>) |
| 11 | 11.jpg | 站立双峰驼与卧地驼群；C2；S04 错写双人骑乘。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_15302340-c165-47e4-8db3-502622148919/frame_w00_4500.jpg>) |
| 12 | 12.jpg | 与 11 高相似的驼群图；进入驼群候选，S10 未选入。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_d314a365-1afd-4a89-8f09-565ddcf3ed81/frame_w00_4500.jpg>) |
| 13 | 13.jpg | 驼群较近角度；C2。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_ee5db843-ac6b-42ba-8fb3-4c3922b289fe/frame_w00_4500.jpg>) |
| 14 | 14.jpg | 银色车侧面；未成卡，事实保留。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_32449633-9693-4deb-8374-08275deaf17b/frame_w00_4500.jpg>) |
| 15 | 15.jpg | 同车侧后方；未成卡，事实保留。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_a60aec7f-7153-40dc-8c4c-baa173a54426/frame_w00_4500.jpg>) |
| 16 | 16.jpg | 室内火锅/烤肉、筷子夹肉；室内组仅两件未成章，A2 保留。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_d71b2488-fcc5-4302-8fff-4cacaa3defb4/frame_w00_4500.jpg>) |
| 17 | 17.jpg | 室内生肉片；室内组仅两件未成章，未进入有效 Aha 集合。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_1d37813a-2a14-435c-837a-8bf217eb233e/frame_w00_4500.jpg>) |
| 18 | 18.jpg | 夜间餐车远景；C3。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_3b306637-f504-4569-89df-150820deb56d/frame_w00_4500.jpg>) |
| 19 | 19.jpg | 同餐车近景、顾客与工作人员；C3。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_369e17df-827c-4c04-831b-bf23a1a152f2/frame_w00_4500.jpg>) |
| 20 | 20.jpg | 夜间桌上小吃与纸杯；C3。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_5111fc58-d949-4d13-8d11-359f7fadd4dc/frame_w00_4500.jpg>) |
| 21 | VID_20240708_174945.mp4 | 车内看高速路、远山与建筑；C4。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_8035a864-264f-49e6-8135-62a11b5444fc/frame_w00_1500.jpg>)、[帧2](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_8035a864-264f-49e6-8135-62a11b5444fc/frame_w00_4500.jpg>)、[帧3](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_8035a864-264f-49e6-8135-62a11b5444fc/frame_w00_7500.jpg>) |
| 22 | VID_20240708_174950.mp4 | 与 21 接近的公路及中控屏；C4，展示增量值得评价。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_0f63e57d-5a5b-4bf9-81a8-0b2b924661cb/frame_w00_1500.jpg>)、[帧2](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_0f63e57d-5a5b-4bf9-81a8-0b2b924661cb/frame_w00_4500.jpg>)、[帧3](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_0f63e57d-5a5b-4bf9-81a8-0b2b924661cb/frame_w00_7500.jpg>) |
| 23 | VID_20240708_175943.mp4 | 乡村道路转向车内乘客微笑；C4。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_e6006af6-b9f3-48e9-8dc8-e0d8093af3c6/frame_w00_1500.jpg>)、[帧2](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_e6006af6-b9f3-48e9-8dc8-e0d8093af3c6/frame_w00_4500.jpg>)、[帧3](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_e6006af6-b9f3-48e9-8dc8-e0d8093af3c6/frame_w00_7500.jpg>) |
| 24 | VID_20240708_185454.mp4 | 山前直路与红帐篷；进入驾车候选，S10 未选入。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_192e6342-222a-481b-8d6b-9e997fc29d32/frame_w00_1500.jpg>)、[帧2](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_192e6342-222a-481b-8d6b-9e997fc29d32/frame_w00_4500.jpg>)、[帧3](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_192e6342-222a-481b-8d6b-9e997fc29d32/frame_w00_7500.jpg>) |
| 25 | VID_20240708_185908.mp4 | 山间弯路与树木；进入驾车候选，S10 未选入；部分抽帧抖动模糊。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_c0fdf1a3-b243-493d-81a4-f366a698d281/frame_w00_1500.jpg>)、[帧2](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_c0fdf1a3-b243-493d-81a4-f366a698d281/frame_w00_7500.jpg>)、[帧3](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_c0fdf1a3-b243-493d-81a4-f366a698d281/frame_w01_1500.jpg>)、[帧4](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_c0fdf1a3-b243-493d-81a4-f366a698d281/frame_w01_7500.jpg>) |
| 26 | VID_20240708_191416.mp4 | 荒地旁站立的人、地上橙色物件；A3。 | [帧1](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_b187d278-e765-49f2-8b56-43dc20b312ff/frame_w00_1500.jpg>)、[帧2](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_b187d278-e765-49f2-8b56-43dc20b312ff/frame_w00_4500.jpg>)、[帧3](<ORIGINAL_REPOSITORY/var/codex_v1_69_full_chain_execution/pack_2/round_1/evidence/asset_b187d278-e765-49f2-8b56-43dc20b312ff/frame_w00_7500.jpg>) |

## 8. 时间、token 与成本

模型链北京时间 10:29:51–10:32:45；另计重新标准化 40.83 秒。总生成耗时不含人工复盘。

| 阶段 | 调用次数 | 耗时 | 输入 token | 输出 token | API 估算人民币 |
|---|---:|---:|---:|---:|---:|
| 本地标准化 | 0 | 40.83 秒 | 0 | 0 | 0 |
| S04 | 9 | 102.35 秒 | 60,596 | 7,444 | ¥0.02025540 |
| S07 | 1 | 40.99 秒 | 11,862 | 2,334 | ¥0.04239600 |
| S10 | 3 | 16.03 秒 | 17,868 | 1,088 | ¥0.00431220 |
| S11 | 1 | 14.83 秒 | 4,479 | 1,202 | ¥0.00247485 |
| 其余本地校验/调度 | 0 | 约 0.16 秒 | 0 | 0 | 0 |
| 合计 | 14 | 215.19 秒 | 94,805 | 12,068 | ¥0.06943845 |

S07 固定 `qwen3.7-plus-2026-05-26`，其余固定 `qwen3-vl-flash-2026-01-22`，thinking=false；服务商返回型号与请求逐项相同，14 次 HTTP 200、finish_reason=stop、usage 已知完整。没有 HTTP 重试、S04 单项重试或 Writer 重写。

39 张独立证据图在 S04 各送一次，S10 另看 13 张，实际累计图像输入 52 次；未上传原视频。费用按冻结的 2026-09-07 北京公开价快照，不冒充账户实扣；不含存储、服务器、带宽和人工，也不能从一个手机素材包直接推算真实用户月成本。

## 9. 本轮收口与下一阶段

质量状态记为 **NOT_ACCEPTED**：夜间/室内边界本轮通过、鹿故事去重本轮有效；Writer 绑定与事实正确性仍有明确缺陷。不得用 COMPLETE 或 4＋3 数量覆盖这一结论。

维持已批准的逐包节奏：下一步建议同版完成包 3 一次新链，再汇总三包的共性问题与优先修改项。现在不切模型、不补规则、不为了漂亮输出重跑包 2。之后最优先讨论 Writer 绑定、视觉事实误差传播、精选增量与文案聚焦；体验取舍集中交给 Owner 决策，工程核查不反复请求确认。

版本与原件：

- [原始完整结果](../var/codex_v1_69_full_chain_execution/pack_2/round_1/codex_full_run.json)
- [本轮输入](../var/codex_v1_69_full_chain_execution/pack_2/round_1/codex_manifest.json)
- [全新标准化记录](../var/codex_v1_69_full_chain_execution/pack_2/round_1/codex_normalization.json)
- [S07 原始短编号及精确还原](../var/codex_v1_69_full_chain_execution/pack_2/round_1/codex_stage_calls/codex_010_s07_finished.json)
- [Writer 实际输入](../var/codex_v1_69_full_chain_execution/pack_2/round_1/codex_stage_calls/codex_014_request.json)
- [Writer 原始回复](../var/codex_v1_69_full_chain_execution/pack_2/round_1/codex_stage_calls/codex_014_response.json)
- [素材包 1 复盘](codex_V1_69_PACK_1_REAL_REVIEW.md)

冻结候选 SHA256：`a92f528b8ccc50e3d39db380d2e93bc5d187aebb3f9e78e069c331b782d261e8`。
原始结果 SHA256：`bec284c5aefa9d45716636ad5e0660b54064b436904762a4e0e0267acbcd2c78`。
Manifest SHA256：`44277440472ca0141cddf5e91748078ada8f21ae436297d9cace99e5cf2e4099`。
收尾核查：44 个运行源码/合同无漂移，39 帧摘要全部与 manifest 对应，无 S07 未知短编号；包 3 在本执行目录尚不存在。生成时原报告的 AWAITING_REAL_CONTENT_REVIEW 状态不覆写，以本复盘补充真实质量结论。私人原素材/模型日志只作本地研究记录，本轮未公开同步。

