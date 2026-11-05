# Diary One — Direct VLM Compact V03：真实悉尼 Chapter 回归实验

日期：2026-11-05

## 1. 为什么修改

2026-11-05 第一批旧的 Direct VLM 对 10s/20s 组均输出契约失败，30s 组通过；对其他 10 个偏移组总通过率仅 3/10。旧 Prompt 要求模型直接抄长 Frame ID、在图库和 hero 字段间维持引用、逐章列出几十个 experience_frame_ids。失败后全量重新推理，导致重复费用与章节重规划。

第二版 Compact V02 改用数字 IMAGE_INDEX，但仍要求同时输出 start_clip/end_clip；实际调用 10s、20s、30s 三组全部出现图片序号与片段范围冲突。V02 真实模型并非没有理解：首次输出分别包含 6、8、8 个章节；但双重编号体系导致输出验证失败。运行后保留了完整模型响应和验证错误。

## 2. V03 的实际架构

**语义模型负责**
- 一次输入该组全部保留 JPEG，逐张附带 **IMAGE_INDEX_1_BASED**、**CLIP_SEQUENCE_1_BASED**、已验证的原视频累计时间。其他用户没有核验时钟时间时仅发送顺序，不编造时间。
- 仅输出章节序列及每章的 title、story、selected_images，适量 key_moments；可选 excluded_images。
- selected_images 第一个就是封面。全组自动根据场景和时间选择 Chapter 数量，不要求固定 5 或 8 章，不提供人工路线图和旧流水线视觉事实。

**确定性转换器负责**
- 将图片短序号映射为原始真实 Frame ID、source_asset_id、媒体时间范围和稳定 Chapter ID；
- 根据模型选中的实际 JPEG 的来源片段，推导章节覆盖时间范围，不再信任模型手工生成的另一个时间编号；
- 去重单章图库、修剪模型超限的低优先级图库尾部；缺少 key_moment 时仅使用既有封面生成无新事实的保守占位；
- 若模型章节顺序与真实源视频相悖，按可核实的首张证据时间排序，保留原模型的故事和图片，不重新生成；
- 拒绝未知图片序号、跨章复用同一图库图、排除画面进入图库、没有有效章节等不可安全修复的情况；
- BFF 再对 JPEG 全量哈希、Session、原始输入 SHA、图片来源、视频时间范围及发布结构进行校验。手机消费契约继续沿用 Direct VLM V01 外部 Schema；内部模型决策协议为 **DIRECT_VLM_COMPACT_EDITOR_V03**。

重要：**不改变 S04/S07/S09/S11 旧流水线，不悄悄降级回旧流水线。**

## 3. 实验输入

同样来自 Sydney Citywalk 原始视频，但使用不同 120s 采样偏移。所有组已预先删除 00:00–01:12 片头视频；没有向 VLM 提供片头航拍路线图。使用手机端 MobileCLIP FP16 V07 已抽取的真实 JPEG，不上传原视频或人工路线标签。

- 10s：160 段、235 张 JPEG
- 20s：160 段、226 张 JPEG
- 30s：160 段、234 张 JPEG
- 模型：Qwen3.8-Flash，输入/输出计价为 ¥0.8/¥2.7 每百万 Token（按当时配置）；记录真实 usage 和估算费用。
- 每组最大两次全图调用；只有格式/来源验证失败才触发有限重试。
- **质量对照的是已有各组先前的真实调用记录**，并非独立盲测或人工标注过的完整 GT。

## 4. 全部真实请求结果

| 组别 | 旧 Direct VLM 最终 | Compact V02（首次双重编号方案） | **Compact V03 新真实调用** | V03 调用 | V03 图库 | V03 估算成本 |
|---|---|---|---|---:|---:|---:|
| 10s | 两次调用，最终失败 | 两次调用，最终失败 | **8 Chapter / BFF 通过** | 1 | 63 张 | ¥0.16432070 |
| 20s | 两次调用，最终失败 | 两次调用，最终失败 | **8 Chapter / BFF 通过** | 2 | 37 张 | ¥0.31090579 |
| 30s | 7 Chapter / BFF 通过 | 两次调用，最终失败 | **8 Chapter / BFF 通过** | 1 | 40 张 | ¥0.15957007 |
| **合计** | **1/3 通过** | **0/3 通过** | **3/3 通过** | **4** | **140 张** | **¥0.63479656** |

**计费事实：**
- 旧 Direct VLM 三组实际累计约 **¥0.93981514**。
- Compact V02 的六次真实但结构失败调用累计约 **¥0.95733640**。
- Compact V03 的四次真实调用累计约 **¥0.63479656**。相比旧 Direct VLM 对照组累计成本减少约 32.5%，但这只是三个真实输入的实际耗费比较，不是可推广的成本统计结论。
- **本次新实施 V02+V03 两轮真实调用累计约 ¥1.59213296**。单独代码测试/离线旧结果重映射不再产生 VLM 费用；最初 Compact V02 的三次 SDK 前置校验失败没有发出模型请求，不计入费用。
- 20s V03 第一次真实输出 10 Chapter，仅因 C07/C08 按模型列表顺序颠倒而未通过当时的严格顺序检查；第二次输出 8 Chapter 后通过，实际花费两次调用。事后更新的时间顺序转换器对第一次真实响应进行离线重映射，得到了 **10 Chapter、31 张图库、BFF 通过**，不再需要新的模型费用。这个是**事后修复的对照**，不能把原本已经发生的第二次调用费用抹掉。

**V03 真正生成的 Chapter：**

10s：Sydney Opera House & Circular Quay；Harbour Bridge & Cahill Expressway；The Rocks District；Barangaroo Foreshore；Darling Harbour & Chinatown；CBD Heritage Arcades；Hyde Park & St Mary's Cathedral；Royal Botanic Garden。

20s：歌剧院与环形码头；岩石区集市与历史街区；海港桥下的绿地公园；达令港游艇码头；海事博物馆与历史船只；唐人街与维多利亚女王大厦；圣安德鲁大教堂与海德公园；皇家植物园的绿意探索。

30s：环形码头与歌剧院；岩石区市集；海港大桥下的步道；达令港与海事博物馆；中央车站与市场城；CBD步行街与圣玛丽大教堂；海德公园；皇家植物园与麦考利夫人之椅。

## 5. 实际图库人工复核：仍需改进的内容

**进步**：
- 20s 已在最终图库分别保留歌剧院、岩石区市场、桥下绿地、达令港、海事船只、唐人街/拱廊、教堂/公园、植物园的代表图片。
- 30s 的 8 章图库从海港、岩石区、市中心到植物园总体按视觉拍摄顺序演进，达令港和海事博物馆图片得到明显呈现。
- 结构型错误（虚构 Frame ID、封面与图库不一致）不再由模型手工承担，三组真实输入的完整 BFF 发布契约都通过。

**保留的缺陷**：
- 10s 组 C05 将 Darling Harbour 与 Chinatown 合在同一章，横跨两个不同城市区域，语义上有过度合并嫌疑。
- 10s 组 C06/C07 推导出的时间片段范围重叠 12 段；20s 组 C06/C07 重叠 10 段。模型选出的图库图片不重复，但来源经验范围仍未严格互斥，因此不能把这些结果视作最终精确 Chapter 边界。
- 30s 第五章“中央车站与市场城”中的“中央车站”需要额外视觉地标核定，当前通过 JSON / 图片来源检验不能证明地标名字必然正确。
- 10s 组有故事出现 “weekend”，但这个公开长视频的真实拍摄星期并未经验证；VLM 仍可能写出时间相关的无根据限定。
- 仅按各章节“入选图片的最早/最晚时间”派生证据范围，无法保证所有稀疏出现的独特经历被覆盖。三组推导的 evidence 片段联合覆盖分别为 144/160、123/160、103/160；这是时间片段范围覆盖，不等价于语义覆盖率，也不表示其他片段都应独立呈现。
- BFF 发布契约通过指引用合法、输入绑定和结构完整。**不是对文字真实性或图文一致性的语义质量背书**；结果继续标识 production_ready=false。

## 6. 自动化验证和下一步

- 通过 Python 新旧契约、X02 Gateway、失败后处理、BFF 及可靠性相关的 **183 项回归测试**（包含此前旧功能兼容性）。
- 此后新增时序排序修复，又在本地离线恢复 20s 的第一次真实响应，10 Chapter、31 图、BFF 通过；无额外实际模型调用。
- 接下来需要 P1 精确章节边界、重要场景真实展示门禁，以及无依据叙事措辞检查。新版本仍留在 feature 分支，尚未部署到线上业务环境，不应默默覆盖已经在用的生产算法。

## 7. 可复现产物（Mac 本地，不进入 GitHub）

- V02 原始输出及转换失败证据：work_logs/evidence/sydney-direct-vlm-compact-v02-20261105/offset_XXX/attempt_audit/
- V02 第一次生成事后重映射为合法输出：同目录 offset_XXX/posthoc_v03_transcode_first_attempt/
- **V03 真实 API 输出**：work_logs/evidence/sydney-direct-vlm-compact-v03-20261105/offset_XXX/result.json
- **V03 原始模型响应、错误、费用**：offset_XXX/attempt_audit/attempt_01.json 和必要时 attempt_02.json（这些文件有隐私文本，权限仅属主可读）。
- BFF 校验：offset_XXX/publish_envelope.json
- **真实图片 Chapter 可放大对比**：work_logs/evidence/sydney-direct-vlm-compact-v03-20261105/ALL_OTHER_OFFSETS_REAL_JPEG_REVIEW.html，三组对应 chapter_XX_real_gallery.jpg 和 all_chapters_visual_montage.jpg
- 执行脚本：work_logs/evidence/sydney-direct-vlm-compact-v03-20261105/run_compact_v03.py

必须继续保留“旧输出原文与新派生转换”的区别：只记录真实发生的模型调用次数与费用，不以 posthoc 回放掩盖既有付费失败。
