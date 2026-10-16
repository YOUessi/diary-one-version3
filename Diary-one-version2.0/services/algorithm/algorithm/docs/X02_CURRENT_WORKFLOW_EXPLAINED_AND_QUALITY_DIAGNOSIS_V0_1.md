# Diary One X02 当前 Workflow 全链路说明与质量诊断 V0.1

状态：DRAFT DIAGNOSTIC / NOT FROZEN / NOT PRODUCTION

日期：2026-09-01

用途：让产品、算法和测试人员能沿着同一条处理链路，对某一个细微步骤给出精确建议。

范围：只记录算法仓库、当前 Web 测试适配层和真实运行证据；不修改 Firmware、SDK、正式 App 或共享状态文件。

## 0. 先说明这份文档是什么

这不是重新设计一套新算法，也不是用新的想法覆盖已经冻结的 S00–S13。

本文同时区分四种内容：

- 【冻结目标】：已经讨论并冻结的产品与算法原则。
- 【当前实现】：X02 当前真实执行的代码，而不是名称看起来像什么。
- 【本轮证据】：最新真实素材运行中实际发生了什么。
- 【诊断建议】：为了让测试结果可用，下一步应优先修正什么；尚未冻结。

后续反馈可以直接引用编号，例如：

- “我不同意 T01-4 的抽帧方式。”
- “S07-5 这个 Chapter 候选案例应该合并。”
- “P0-4 的 Aha 定义需要再讨论。”

本文不展示、也不要求模型输出隐藏思维链。所谓“过程可见”，指每一步的输入、证据、规则、候选、淘汰原因、负责人、时间、Token 和成本都可审计，而不是让模型写一段无法验证的内心推理。

### 0.1 本文核对的版本

- 本文核对的 V02 算法实现基线（本文档提交前）：commit b0380b0953adc16287a34078d5ef62c28a36aa6f。
- 当前 V02 X02 文件 SHA-256：94de9117d2b112ef5785439feedfab1cbff8f5d4a867f429c8229228f7321ebc。
- 最新真实运行使用的算法基线：commit 38a5affed3317707b1d1e8d7393ebf0ab0ae18a8。
- 最新真实运行使用的 V01 X02 文件 SHA-256：1a69c1c71d8c72f31713c894176683a26b89641de5abd5e236868c85df91c758。
- 本文核对的 Web 测试页实现基线：commit 690eedbe002240c09a5fafb4bf0f2d04608e555b。
- 最新真实运行 Session：e2b37756-5f14-42af-93e4-581a3bd30918。
- 最新真实运行 Run：13527f8a-4a8d-4a08-aa24-70d54498f958。
- Run Audit SHA-256：9ea42d497bf6b6fedfb639df8951e4b72c9c74ccdb278b5b08392092206f797d。
- 运行完成时间：2026-09-01 22:57:32，中国标准时间。

必须区分“当前代码”和“已经跑过的证据”：

- 最新真实运行是 X02 V01，下面所有本轮数字和失效案例都来自这次 V01 Run Audit。
- 算法仓库随后提交了 V02 Observation Semantic Contract，增加版本化 Episode 兼容规则和更精确、隐私最小化的失败诊断。
- V02 没有经过同一批真实素材的付费重跑，不能说它已经解决本轮质量问题。
- 当前 Web 仍只接受 V01 endpoint/schema，而算法 HEAD 已改为 V02；V02 Web handshake 尚未完成。若直接以当前 HEAD 重启算法服务，现有 Web V01 调用不会自动兼容。
- V02 没有改变 S05–S13 的主要简化逻辑；因此本文对这些阶段的诊断仍适用于当前 HEAD。

### 0.2 以后怎样给到足够具体的反馈

一条可执行反馈最好包含：

| 字段 | 含义 | 示例 |
|---|---|---|
| Run | 针对哪次运行 | 13527f8a… |
| Stage | 问题首先出现在哪一步 | S07 |
| Object | 具体对象 | Chapter Candidate 2 |
| Current | 当前算法做了什么 | 把第 2–6 项组成一个 Chapter |
| Expected | 你认为应该怎样 | 菜摊单独作为市集 Beat，河岸留在古镇漫步 |
| Evidence | 依据哪几项素材 | 第 2、5、6 项 |
| Severity | 影响程度 | BLOCKING / MAJOR / MINOR |
| Comment | 产品或感性判断 | 市井和沿河风景在这一组里没有清楚主线 |

同一个最终 Chapter 可以拆成多条不同 owner 的反馈：

- S04：第 2 项被标成哪个 Episode 是否正确。
- S05：第 6→7 项是否应该 SPLIT。
- S07：第 2–6 项是否应该成为同一个候选。
- S09：为什么候选 A、B 同时入选。
- S10：第 5 项是否应该当 Hero。
- S11：标题和 Story 是否自然。

这样修改时可以回到真正负责的阶段，而不是让 Writer 或最终页面替前面所有错误背锅。

---

## 1. 先给结论：当前结果“不可用”的判断成立

这次不是单一的 Writer 文案问题，也不是简单把 Chapter 数量从 2 调到 3–4 就能解决。

本轮真实因果链是：

1. Web 把 20 个视频当作一个合成测试日，但用导入顺序代替真实拍摄时间。
2. 每个视频统一抽 3 帧，没有区分 Auto 9 秒与 Manual 15/60/120 秒合同。
3. S04 实际看懂了 16 个视频，但另外 4 个视频仅因模型输出了词表外 subject code，就被整项标记 FAILED。
4. 这 4 个 FAILED 使相邻边界连续出现 DEFER；当前实现又把 DEFER 和 SPLIT 一样直接切开，20 项被切成 13 个 Moment。
5. S07 主要依赖宽泛 Episode Code。只要都叫 HISTORIC_TOWN_WALK，菜摊、青石板路、河岸、建筑入口就可能被放进同一候选，却没有检查它们是否共同承担一个清楚的 Chapter 故事职责。
6. S09 首要最大化“覆盖了多少素材”，因此选择了两个同属古镇漫步的碎片候选，而没有惩罚同一 Episode 被重复切成两个近似 Chapter。
7. S10 对 5 项以上候选固定取 5 项，主要依赖模型自报质量、题材新颖度和时间分散；还没有真正实现 Content Beat、Evidence Anchor 和强去重。
8. S11 把候选中所有事实都交给 Writer。Writer于是把 15 条和 19 条事实分别串成 464 字和 634 字的“逐帧清单”。
9. 三个 Aha 候选其实都是普通的狗嗅闻或行走，独立记忆价值本来就弱；Writer 又连续两次写成 23、23、27 字，超过 20 字硬门，最终三个全部被阻断。

因此，最终看到的：

- 2 个 Chapter，不代表系统正确地判断“今天只值得 2 章”；
- 0 个 Aha，也不代表系统正确地判断“今天没有 Aha”；
- 当前只是错误结构、弱候选和 Writer 失败共同形成的表面结果。

### 1.1 问题不在“数量少”本身

冻结原则一直允许 1–5 Chapter 和 0–3 Aha，不要求凑数。真正的问题是：

- 古镇内容被错误切碎，又被错误重组；
- 市井与青石板路没有明确故事关系，却被宽泛 Episode Code 包在一起；
- 部分可用素材因输出合同错误退出；
- Aha 候选不够像真正的独立精彩瞬间；
- 最终文字没有做内容取舍，只做事实罗列。

如果只提高数量下限，系统只会生成更多低质量 Chapter/Aha。

---

## 2. 整条 Workflow 的基本原则

在看每一步之前，先固定五条不会改变的总原则。

### G01｜先理解，再分段，再选故事，再选画面，最后写字

正确顺序是：

~~~text
原始素材
→ Evidence
→ Observation
→ Moment
→ Chapter/Aha Candidate
→ 全日集合选择
→ 最终媒体
→ 有证据的文字
→ 校验与导出
~~~

Writer 不能修复错误聚类，漂亮图片也不能反向创造一个 Chapter。

### G02｜模型不是总控 Agent

确定性 Workflow 负责：

- 阶段顺序；
- 输入输出合同；
- 数量边界；
- 候选合法性；
- 失败归属；
- 版本、成本和血缘。

模型只在局部承担：

- 看图；
- 对已结构化事实提出有限候选；
- 对已批准 Claims 写文案。

### G03｜Precision first，但不能把工程合同失败伪装成“内容不值得”

冻结的价值排序是：

~~~text
False Memory / False Merge / Unsupported Claim
高于
Missing Memory / 轻微过切 / 错过不确定瞬间
~~~

这意味着宁可少生成，也不要编造。但“模型多写了一个词表外标签”“Writer 多写了 3 个字”属于工程或合同失败，不能伪装成素材没有价值。

### G04｜Chapter 和 Aha 是两种不同的故事职责

- Chapter：一段相对完整的经历或局部 Episode。
- Aha：一个局部、单峰、可独立记住的瞬间。

Aha 可以发生在 Chapter 的时间线里，但必须讲不同的事情。例如：

- “古镇漫步”可以是 Chapter；
- 漫步途中猫碰倒纸杯，可以是 Aha；
- 生日 Chapter 中的吹蜡烛通常是同一故事高潮，不应再重复成为 Aha。

### G05｜数量是结果，不是配额

- 丰富日目标：3–4 Chapter；极强内容日严格例外允许第 5 个。
- 每章通常 3–5 个精选素材；严格 Compact Gate 可为 2 个。
- 0–3 Aha；丰富日希望 2–3，但不降低质量门。
- 没有足够证据时允许更少。

---

## 3. “冻结产品链路”与“当前测试链路”不是一回事

### 3.1 冻结的生产形态

同步与增量准备：

~~~text
S00 → S01 → S02 → S03 → 无感后台 Evidence 队列
~~~

Rolling Preview 或 Final：

~~~text
S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S12A
→ S13A 只物化已选 HQ → 必要的 S11 重验 → S12B → S13B 原子导出
~~~

### 3.2 最新已真实跑通的 Web + X02 V01 实际形态

~~~text
Web 选择素材
→ 浏览器逐项解码、统一抽 3 帧、标准化
→ 一次性上传整个 Evidence Bundle
→ X02 分 4 批做 S04 看图
→ 一次模型调用同时提出 S05–S07 结构建议
→ 简化的确定性边界、角色、候选与集合选择
→ 启发式选择 5 个媒体
→ 同一个 Qwen VL 模型写 Chapter/Aha
→ 简化校验
→ 返回 Preview；S13 不执行
~~~

### 3.3 阶段覆盖真值表

| Stage | 冻结产品目的 | 当前 X02 实际覆盖 | 结论 |
|---|---|---|---|
| S00 | 同一天的 immutable Snapshot / Revision | 每次导入形成一个独立测试 Session | 仅测试替代，不是正式 Revision |
| S01 | 可信 RawAsset 事实账本 | 文件名、大小、哈希、时长、导入顺序 | 缺真实来源、拍摄时间、时区、Session |
| S02 | Auto/Manual 不同时长的 Window/Frame 合同 | 每项统一 3 帧 | 与冻结 Manual 合同不一致 |
| S03 | 画质、变化、Embedding、时间线 Edge | 基本未实现 | Stage 名存在，核心信号缺失 |
| S04 | Window-local Observation | 已实现批量看图和逐项结果 | 有 20% 合同型整项失败 |
| S05 | 双账本、Core/Tail/Pending、有限 lookahead | 只比较相邻枚举和 motif | 不是冻结的 Moment Engine |
| S06 | KEEP / CONTEXT_ONLY / DROP | 已实现简单规则 | 本轮 16 KEEP / 4 DROP |
| S07 | 局部 Chapter/Aha 候选 | 简化 episode group + 模型提议 | 故事职责和 Aha 门过弱 |
| S08 | one-question 定向补证 | 实际没有独立任务 | 名称合并但能力缺席 |
| S09 | 八层集合目标与关系图 | 小规模枚举，优先素材覆盖 | 导致同 Episode 重复切章 |
| S10 | Beat / Anchor / Media / Hero | 质量、差异、时间分散启发式 | 还不是完整媒体编辑 |
| S11 | Claim Ledger 后的自然表达 | 全事实直接交给 Writer | 造成逐帧事实清单 |
| S12 | 两阶段只读硬门 | 结果组装和基础合同检查 | 不能证明语义发布安全 |
| S13 | Selected-only HQ 与原子导出 | 明确未执行 | Web 仅 Evidence Preview |

这张表很重要：页面上显示“Stage completed”，只表示该测试阶段的函数执行完，不表示冻结版本的完整能力已经实现。

当前算法 V02 只对 S04 语义兼容合同、结果身份、失败审计和 endpoint 做了增量升级。Web 仍为 V01，所以“当前仓库代码存在”与“当前测试页已经使用”仍是两个不同事实。

---

## 4. 最新真实运行的全局账单

### 4.1 输入与输出

| 项目 | 本轮结果 |
|---|---:|
| 导入素材 | 20 个视频 |
| 原视频总时长 | 298.697 秒，约 4 分 59 秒 |
| 浏览器 Evidence | 60 帧 |
| Evidence 上传量 | 7,558,843 bytes，约 7.56 MB |
| 合成时间轴 | 第 1 项 0 分钟，第 20 项 38 分钟 |
| 成功 Observation | 16 |
| FAILED Observation | 4 |
| Moment | 13 |
| Chapter 候选 | 3 个合格；另有不合格提议 |
| Writer 前选中 | 2 Chapter + 3 Aha |
| 最终可见 | 2 Chapter + 0 Aha |
| 输出模式 | CHAPTER_DAY |

### 4.2 时间、Token 和模型成本

| 流程 | 时间 | 模型调用 | 输入 Token | 输出 Token | 估算成本 |
|---|---:|---:|---:|---:|---:|
| 浏览器抽帧、标准化、原文件哈希 | 93.717 秒 | 0 | 0 | 0 | 不含本地计算成本 |
| S04 四批视觉理解 | 131.849 秒 | 4 | 62,328 | 9,174 | $0.00320975 |
| S05–S07 结构提议 | 40.696 秒 | 1 | 12,595 | 3,188 | $0.00092656 |
| S08–S10 确定性处理 | 约 0.005 秒 | 0 | 0 | 0 | $0 |
| S11 Writer 两次 | 52.304 秒 | 2 | 18,164 | 4,300 | $0.00127425 |
| 服务端 X02 总计 | 224.910 秒 | 7 | 93,087 | 16,662 | $0.00541056 |
| 用户端从开始到结果 | 318.779 秒 | — | — | — | — |

本轮单次 API 美元成本不高；眼前的主要风险是质量和约 5 分 19 秒的等待时间。不能据此直接宣布 186 项高强度日成本安全，因为当前输入只有 20 项、S08/S13 未执行、没有真实 Auto 1-or-3、没有 HQ，且多项处理仍然串行。

本轮所有七次模型调用都使用 qwen3-vl-flash-2026-01-22，没有单独的 Writer 模型路由。

---

## 5. 测试适配层：素材进入算法以前发生了什么

### T00｜把一次导入定义成一个“合成测试日”

目的：在 GPS、可靠拍摄时间、Diary One 设备来源都缺失时，先让手机素材能够跑通算法。

【当前 V01/V02 共同实现】

- 用户每次选择的一组文件，默认就是一个新测试日。
- 文件选择顺序被保存为时间顺序。
- 第 N 项被赋予 N × 2 分钟的 timeline offset。
- 不读取或使用真实 GPS。
- 不区分这条素材来自 Diary One Auto、Diary One Manual，还是普通手机拍摄。
- 当前最多允许 240 项，不再是早期的 24 项。

【本轮案例】

20 个视频被解释为从第 0 分钟到第 38 分钟，每 2 分钟一项。但原视频只有约 5 分钟，真实拍摄跨度未知。

【问题】

- 文件选择顺序不等于拍摄顺序。
- 2 分钟固定间隔会制造不存在的连续性，也会隐藏真实的半小时或数小时中断。
- 无法测试“古镇 → 奶茶店 → 回到古镇”的真实 resumed episode。
- 无法评价 1.5 小时/2 小时 Preview 触发。

【可反馈点 T00】

- T00-1：测试阶段是否必须尽量读取可信拍摄时间。
- T00-2：没有可信时间时，是否让测试者手动分上午/下午/晚上或拖拽排序。
- T00-3：一次导入是否永远等于一个测试日，还是允许同一天追加素材。

### T01｜浏览器生成 Evidence

目的：把原图或原视频转成体积更小、模型可看的代表性画面。

【当前实现】

- 所有画面被中心裁剪为 3:4 竖图，768 × 1024 JPEG，质量参数 0.84。
- 每个视频按实际时长的 1/6、1/2、5/6 取 3 帧。
- 这三帧在合同中仍被标成 1.5、4.5、7.5 秒的 canonical offsets。
- 照片会生成 3 份相同 Evidence；云端视觉模型只取中间一份，但 Bundle 仍保存并上传三份。
- 浏览器计算原文件 SHA-256，但不上传原文件。
- 每项当前串行处理，本轮每个视频约用 4.6 秒。

【冻结目标】

- Auto 9 秒：Phone 固定抽 1.5/4.5/7.5 秒三帧；Cloud 采用保守 1-or-3。
- Manual Photo：1 个静态 Evidence / 1 帧。
- Manual Video：15 秒 2 Window/4 帧，60 秒 4/8，120 秒 6/12。
- 当前 Web 的统一三帧只是临时测试适配，不是产品合同。

【本轮案例】

最长视频 29.4 秒仍只抽 3 帧；最短视频 4.0 秒也抽 3 帧。一个 29 秒视频中的短暂事件可能完全落在三个采样点之间。

【问题】

- 无法真实测试长 Manual Video 的语义覆盖。
- 中心裁剪可能切掉横屏视频两侧的重要人物或动作。
- 照片三份相同 JPEG 造成不必要上传。
- canonical offset 与真实 source timestamp 不是同一含义，UI 容易让人误以为模型看的是视频第 1.5/4.5/7.5 秒。

【可反馈点 T01】

- T01-1：当前手机素材测试是否先保留原始画幅，避免中心裁剪影响判断。
- T01-2：是否在测试页明确显示“实际取帧时间”和“逻辑位置”两列。
- T01-3：长视频是否立即按冻结 Manual Window 合同处理。
- T01-4：照片是否只生成并上传 1 帧。

### T02｜一次性上传 Evidence Bundle

目的：把 Manifest 和 Evidence 交给本地云端算法。

【当前实现】

- 浏览器先完成全部素材的抽帧、标准化与哈希。
- 再把约 7.56 MB 的 Bundle 通过一次 multipart request 上传。
- 原图/原视频不上传，HQ 也不请求。
- 服务端验证 Bundle 后开始 X02。

【冻结目标】

正式 App 中，用户点击 Sync 后不再出现第二次上传交互。Evidence 进入持久后台队列并无感批量上传；相同素材、相同版本不重复付费。

【问题】

当前测试页还不是正式 App 的后台上传实现。关闭页面、网络中断、断点续传、缓存复用都没有被这轮验证。

【可反馈点 T02】

- T02-1：测试页是否需要先做分批上传与断点续跑。
- T02-2：测试者是否需要看到原始大小、Evidence 大小与压缩比例。

---

## 6. S00–S02｜日状态、事实账本和 Evidence 合同

### S00｜我们到底在处理哪一天、哪一个版本

【冻结目标】

- 同一 Local Day 可以多次 Sync。
- 每个 Preview/Final Revision 固定一份不可变输入快照。
- 约 1.5 小时新增有效覆盖后 eligible，约 2 小时默认尝试 Preview。
- 中间体验允许累加，但通过 enrich、merge、replace、revision 控制质量，不能机械叠加。
- 当天 Finalization 重新基于全日事实做集合判断。

【当前实现】

一次 Web 导入就是一个 Session；没有同日追加、稳定 Memory ID、Preview Revision、NO_CHANGE 或 late-data Revision。

【本轮影响】

本轮只能评价“一次性导入 20 项后的离线结果”，不能证明滚动生成体验。

【可反馈点 S00】

- S00-1：第一次真正接入 App 测试时，Preview 是覆盖旧结果还是以可解释方式修订。
- S00-2：用户何时能看到“这一章正在被丰富”，而不是重复出现新章。

### S01｜RawAsset 事实账本

【冻结目标】

RawAsset 至少保留：

- Auto/Manual 来源；
- Photo/Video；
- 可信拍摄时间、时区、Local Day；
- Capture Session；
- 时长、原始媒体规格与内容哈希；
- Sync provenance。

AI 不得改写这些事实。

【当前实现】

保存文件名、媒体类型、时长、宽高、字节、原文件哈希、导入顺序；没有可信 capture source、capture time、timezone、session。

【本轮影响】

算法无法知道哪些素材是用户主动拍的，也无法把真实时间间隔用于边界判断。Manual 作为“主动记录信号”的价值完全没有进入链路。

【可反馈点 S01】

- S01-1：真实 App 联调前，最小必须补齐哪些来源与时间字段。
- S01-2：普通手机测试素材如何明确模拟 Auto 和 Manual。

### S02｜Evidence Window 与 Frame

【冻结目标】

不同来源与时长使用不同 Window 合同；所有 Frame 都能追溯到 RawAsset。Auto 单帧上传不够时直接退出候选，不进行二次补帧。

【当前实现】

每个 Asset 只有一个逻辑 Observation，统一三帧；没有 Window-level 对象供 60 秒、120 秒视频形成多个局部 Observation。

【本轮影响】

X02 当前更接近“每个文件理解一次”，不是“每个 Evidence Window 理解一次”。长视频内部可能包含多个场景、转场或峰值，但被压成一个标签。

【可反馈点 S02】

- S02-1：测试页下一版是否应先实现 Manual 15/60/120 秒冻结合同。
- S02-2：未知时长的视频按实际时长映射几个 Window，仍是待单独确认的开放项。

---

## 7. S03｜便宜信号层

目的：在调用大模型之前，先用低成本方法描述每个 Window 自身和相邻 Window 的变化。

【冻结目标】

S03A Window Intrinsic Signal：

- 模糊、曝光、遮挡、稳定性；
- Window 内运动量、变化与可能峰值；
- 轻量视觉 Embedding；
- Evidence 可靠性与错误原因；
- Auto 1-or-3 路由依据。

S03B Timeline Edge Signal：

- 真实时间间隔；
- Capture Session 是否连续；
- 视觉相似度与 Embedding 距离；
- 变化、矛盾与可信 GPS。

Embedding 的通俗含义：把一张画面的语义和视觉特征压成一串数字，使算法可以比较“像不像”。它只能提供证据，不能独自决定两个素材属于同一故事。

【当前实现】

当前 X02 没有真正计算上述画质、Embedding、运动或真实时间 Edge。名为 S03_S07_DETERMINISTIC_STRUCTURE 的步骤主要是在 S04 以后比较枚举标签。

【本轮影响】

- 古建筑正面、木雕细节、石板路、河岸虽然可能共同属于古镇漫步，但当前没有多原型语义表示去表达这种“不同画面、同一活动”。
- 相反，森林石阶和古镇石板路也可能因为共享 stone motif 看起来相近，却没有足够的反向边界信号。

【问题】

当前算法过度依赖模型一次性给出的 Episode/Setting Code。只要上游标签稍有错误，后续结构就随之错误。

【可反馈点 S03】

- S03-1：哪些便宜信号应优先真实实现：时间、画质、Embedding、运动，还是 Session。
- S03-2：测试页面需要显示哪些相似/变化证据，才能让人理解为什么 JOIN 或 SPLIT。

---

## 8. S04｜Observation Lite：逐个 Window 看到了什么

目的：只回答“当前 Window 里能直接观察到什么”，不回答“值不值得记住”。

【冻结规则】

- 每个 accepted Window 都有且只有一个终态：OBSERVED、PARTIAL、INSUFFICIENT_EVIDENCE、FAILED。
- 事实只能引用当前 Window 实际输入的 Frame。
- 不借相邻素材补当前事实。
- 不推断真实地点、人物身份、关系、用户情绪、意图、口味或因果。
- 每条事实保存 Evidence 支持等级。
- 证据不足与模型/合同失败必须分开。

【当前实现】

- X02 每批处理最多 6 个 Asset。
- 20 个视频被分为 6、6、6、2 四批，当前顺序执行。
- 视频每项向模型呈现三帧；照片只呈现中间帧。
- 使用封闭的 setting、activity、episode、subject、event 枚举。
- Qwen Prompt 中附带了 JSON Schema，但 API transport 仅要求 json_object，不是严格 schema transport。
- 模型输出后由确定性 Validator 检查；任一关键字段不合法，当前整项 Observation 进入 FAILED。

【V02 新增但尚未付费实跑】

- Setting、Activity、Event 与 Episode 使用同一份版本化兼容合同生成 Prompt 和执行校验。
- 被拒绝的候选会保存 validation rule、JSON field path、合同版本/hash、封闭枚举快照和候选 hash。
- 不保存原媒体、事实原文、motif 或隐藏思维链。
- 仍然 fail closed：词表外 subject code 仍会使该项 FAILED；V02 改善了原因可见性，没有自动修复这一类输出。

【本轮证据】

- 16 项 OBSERVED。
- 第 12、13、15、17 项 FAILED。
- 四项失败原因完全相同：subject_codes contains a value outside the closed vocabulary。
- 这四项不是被视觉质量门判为“看不清”，而是模型输出了词表外值。
- 当前 V01 Audit 没有保留足够的原始候选细节供产品判断这些画面本来是什么；V02 会补充有界结构诊断，但还没有用同一批素材实证。

【为什么严重】

20% 素材因格式/词表不一致退出，会直接影响后续：

- 丢失古镇逛街画面；
- 制造连续 DEFER；
- 增加单项 Moment；
- 破坏 resumed episode；
- 降低 Chapter 候选数量；
- 使真实素材质量问题与模型合同问题混在一起。

【本轮语义案例】

第 2 项同时出现古街、行人和菜摊，被标成 HISTORIC_TOWN_WALK，而第 1、18 项相似市集内容被标成 MARKET_VISIT。当前没有二级“古镇中的市集段落”表达，因此同类内容被不同 Episode Code 分开，不同叙事内容又可能被同一宽泛 Code 合并。

【诊断】

这是当前第一个 P0 阻断点。在修复前，继续调整 Chapter 数量、阈值或 Writer，都会在不完整事实上优化。

【可反馈点 S04】

- S04-1：Episode 是否应该只做粗类别，另有更细的 scene/activity thread。
- S04-2：词表外但事实可用时，是定向重试、明确 alias 映射，还是降级为 OTHER；不能静默猜。
- S04-3：每项失败时，页面是否显示失败字段、模型原值、规则和受影响的下游。
- S04-4：是否要区分“模型没看懂”和“模型看懂但输出合同不合格”。

---

## 9. S05｜Moment Formation：全天连续时间线怎样切段

Window 是一个局部证据片段；Moment 是若干时间上连续、语义相对纯净的 Window 组成的内部段落。Moment 不是最终 Chapter。

### 9.1 冻结目标

每个相邻切口都保存两本账：

- Continuity Evidence：支持继续属于同一段的证据。
- Boundary Evidence：支持这里发生切换的证据。

判断状态：

- MERGE：合入当前 Moment。
- SPLIT：从这里新开 Moment。
- DEFER：现在证据不足，先暂存。
- UNRESOLVED：有限证据用尽仍无法确定，保守切开并保留诊断。

当前 Moment 应使用：

- Core：已经确认属于这一段的稳定主题与多个视觉原型。
- Tail：最近的可靠片段。
- Pending：暂时不能归左或归右的过渡片段。
- 最多 2 个可用后续 Window、6 分钟、3 个连续 Pending 的有限 lookahead。

例如“石板路 → 古建筑立面 → 石板路”不要求三项看到同一个物体。只要时间、步行活动、建筑/街巷互补 motif 与边界证据共同支持，它们可以属于同一 Moment。

### 9.2 当前实际规则

当前只比较相邻两个 Observation：

- Episode Code 完全相同：加一条 continuity。
- Setting Code 完全相同：加一条 continuity。
- motif 有交集：加一条 continuity。
- Episode 不同：加一条 boundary。
- Setting 不同：加一条 boundary。
- 任一侧 DROP：加 LOW_EVIDENCE_SIDE。
- 任一 Episode 为 UNKNOWN/OTHER：DEFER。
- 有 continuity 且无 boundary：JOIN。
- 其他情况：SPLIT。

生成 Moment 时，只有 JOIN 会合并；SPLIT 和 DEFER 都立刻开始新 Moment。

也就是说，当前没有真正实现 Core、Tail、Pending、有限 lookahead、Transition Moment 的后续三路判断。页面虽然显示“双向账本”，但实际证据类型和决策器仍然非常简化。

### 9.3 本轮结果

20 个 Observation 被切成 13 个 Moment：

- 第 2–6 项合成一个 Moment。
- 第 8–10 项合成一个 Moment。
- 第 19–20 项合成一个 Moment。
- 其余大多是单项 Moment。
- 四个 FAILED 造成第 11–18 项之间连续七条 DEFER/SPLIT 型切口。

### 9.4 古镇 → 奶茶店 → 古镇案例

冻结逻辑应该是：

- S05 保持 A、B、C 的真实连续顺序，奶茶店 B 可以成为独立 Moment。
- S07 再判断 A 与 C 是否为同一次局部古镇活动的 resumed episode。
- B 是否成为 Aha，取决于它有没有独立事件峰值；不是自动成为 Chapter 或 Aha。

当前 X02 会把 A、B、C 切开，但没有完整 resumed episode 关系图，主要依赖模型在 S07 重新把相同 Episode Code 提议到一起，容易不稳定。

【诊断】

这是第二个 P0 阻断点。当前“Moment”还不能承担我们此前冻结的语义聚类责任。

【可反馈点 S05】

- S05-1：古镇内部哪些变化仍是同一 Moment，哪些应成为子段。
- S05-2：短暂室内插曲后回到主线，Chapter 应恢复合并还是形成两个独立故事。
- S05-3：DEFER 最终单拎出来后，哪些条件允许它尝试 Aha，哪些直接只做 Context/Drop。
- S05-4：页面应如何显示左右证据和 lookahead，才能让测试者判断切分是否合理。

---

## 10. S06｜Observation Role：素材在 Memory 中扮演什么角色

目的：分段以后，决定每个 Observation 是否有资格参与记忆内容。

【冻结角色】

- KEEP：有可靠、可用于 Memory 的内容。
- CONTEXT_ONLY：不直接形成 Claim，但对时间、转场或理解有正向帮助。
- DROP_FROM_MEMORY_OUTPUT：不进入 Chapter/Aha 内容，但底层事实与 Manual 窗口仍保留。

【当前实现】

- FAILED 或 INSUFFICIENT_EVIDENCE → DROP。
- quality_score 小于 0.35 → CONTEXT_ONLY。
- 所有事实都是 WEAK → CONTEXT_ONLY。
- 其他 → KEEP。

【本轮结果】

- 16 KEEP。
- 4 DROP，全部来自 S04 合同失败。
- 0 CONTEXT_ONLY。

【问题】

当前角色判断几乎只看 S04 状态、模型自报 quality 和事实等级，没有实现：

- 同 Moment 重复抑制；
- 正向 Context 用途测试；
- Transition KEEP 的独立事件要求；
- Manual 相似内容在 Memory 候选中的合理抑制。

【可反馈点 S06】

- S06-1：页面是否需要逐项允许标注“应保留、只做上下文、应丢弃”。
- S06-2：某项画面普通但能证明从街道进入室内，是否应为 CONTEXT_ONLY。

---

## 11. S07｜生成 Chapter 和 Aha 候选

Candidate 的通俗含义：算法认为“这组内容可能成为一个 Chapter/Aha”，但它还没有被全日选中，也还没有决定最终展示哪些画面。

### 11.1 Chapter 冻结目标

Chapter Candidate 必须来自局部 Episode：

- 单个 Moment；
- 相邻 Moment Group；
- 短暂中断后的 Resumed Episode；
- 有界 Local Episode Group。

不能只因全天画面风格相似就远距离拼接。

普通 Chapter 至少需要：

- 3 个不同 RawAsset；
- 3 个非重复内容单元；
- 清楚的局部 Episode；
- 足够内容价值；
- 可接受的推断风险；
- 候选内部去重。

长 Manual Video 有单独例外，但仍要有 3 个时间和语义均不同的 grounded Window unit。

### 11.2 当前 Chapter 候选生成

当前有两路：

1. 确定性 episode group：把相同 Episode Code、相邻索引差不超过 2 的 KEEP Observation 组成候选。
2. 模型结构提议：模型从已验证 Observation 中提出一组 observation IDs。

确定性 Validator 主要检查：

- 至少 3 项；
- Observation 存在且不是 DROP；
- Episode Code 一致；
- Fact IDs 合法；
- 候选没有完全重复。

它没有真正检查“这些素材是否共同承担一个清楚的故事职责”。

### 11.3 本轮 Chapter 候选

合格的三个候选：

1. 确定性古镇组：第 2–10 项中的 8 个 HISTORIC_TOWN_WALK Observation。
2. 模型古镇组 1：第 2–6 项。
3. 模型古镇组 2：第 8、9、10、14、16、19、20 项。

另外：

- MARKET_VISIT 只有第 1、18 项，不满 3 项，被拒绝。
- NATURE_WALK 只有第 7、11 项，不满 3 项，被拒绝。

### 11.4 为什么“人间烟火”和“青石板路”会进同一 Chapter

直接原因不是图片相似度，而是：

- 第 2 项既有古街石板路，也有菜摊，被 S04 统一标成 HISTORIC_TOWN_WALK。
- 第 3–6 项也都是 HISTORIC_TOWN_WALK。
- S07 看到 Episode Code 一致，就允许它们进入同一候选。
- 没有“市集生活”“沿河景观”“建筑浏览”等更细的故事职责或 Content Beat gate。

因此一个很宽的“古镇漫步”标签，替代了真正的 Chapter 语义设计。

### 11.5 Aha 冻结目标

Aha 必须同时有：

- Local Peak Evidence：这里确实发生了一个短促峰值。
- Independent Memory Value：单独拿出来也值得记住，且与 Chapter 的故事职责不同。

普通走路、漂亮静物、镜头晃动、场景变化、Manual 意图都不能单独证明 Aha。

### 11.6 当前 Aha 候选

当前确定性逻辑把 event kind 属于 PLAYFUL_ANIMAL 等白名单、salience 为 MEDIUM/HIGH 的 Observation 直接做成 Aha 候选。

本轮选出的三个 Aha 是：

- 狗在石阶缝隙嗅闻。
- 狗沿石板路走过竹棚。
- 狗在林间石板路行走。

拱桥与石碑的模型提议因为不是独立事件峰值被拒绝，这一点方向正确；但三段普通狗行走也不应只因被模型标成 PLAYFUL_ANIMAL 就自动通过独立记忆价值门。

【诊断】

Chapter 候选的“故事职责”和 Aha 的“独立记忆价值”都没有真正实现。这是第三个 P0 阻断点。

【可反馈点 S07】

- S07-1：长时间古镇游览允许几个 Chapter，应该由哪些不同故事职责决定。
- S07-2：古建筑外观相隔 20–60 分钟、建筑本身不同，何时是合理多样性，何时是重复。
- S07-3：古镇市集是独立 Chapter、古镇 Chapter 的一个 Beat，还是只在素材足够时独立。
- S07-4：狗的普通行走是否一律不是 Aha；什么动作才算真正峰值。
- S07-5：Aha 是否应额外要求“用户愿意单独回看”的人工标签维度。

---

## 12. S08｜只对一个关键未知点补证

目的：候选大致成立，但只差一个关键问题时，用最小成本回答它，而不是重跑全天。

【冻结允许问题】

- LOCAL_PEAK_CONFIRMATION：这真的是一个峰值吗。
- EPISODE_RELATION_CONFIRMATION：两段是否属于同一局部 Episode。
- MEDIA_DIVERSITY_CONFIRMATION：少量长 Manual 的多个 Window 是否足够不同。
- ALTERNATIVE_RESOLUTION：两个互斥解释哪一个证据更强。

S08 可以使用已有结构化事实、最多 3 张已有 Frame、已有低清短 Proxy、已获许可的局部音频或一次更强模型。它不能补取 Auto 另外两帧、默认请求 Raw、做全天搜索或修改 S04–S07。

【当前实现】

当前没有独立的 ValidationTask、问题路由、Evidence exposure、VBU 预算或 ValidatedCandidate。名为 S08_S09_SET_SELECTION 的执行实际上直接进入集合选择。

【本轮错过的机会】

- 可以问：“狗嗅闻是否是清楚的独立动作峰值？”如果不能确认，就不进入 Aha。
- 可以问：“古镇组 1 与古镇组 2 是否承担两个不同故事职责？”如果不能确认，就不应为了覆盖更多素材拆成两章。
- 可以问：“四个 FAILED 是视觉证据不足还是字段合同错误？”这是 S04 owner 的修复，不应让 S09把它当内容缺失。

【诊断】

S08 缺席使不确定性直接变成错误选择。它是一个 P1 能力缺口，但在本轮古镇/Aha问题上影响显著。

【可反馈点 S08】

- S08-1：测试页是否展示每个补证问题及它花了哪些 Frame、Token、时间和费用。
- S08-2：哪些问题值得调用更强模型，哪些应直接保守放弃。

---

## 13. S09｜从全天候选中选出一组 Memory

目的：不是逐个候选打分取 Top-K，而是选择一组互不重复、覆盖关键经历、整体最好的 Chapter/Aha。

### 13.1 冻结目标

完整 S09 应建立 typed relation graph，区分：

- 同一 Memory；
- 素材冲突；
- alternative；
- nested；
- partial overlap；
- Chapter 内嵌 Aha；
- distinct Episode；
- unresolved conflict。

集合目标依次考虑：

1. 合法性；
2. 每项边际贡献；
3. Episode coverage；
4. 可信独立价值；
5. 低冗余、低风险；
6. 质量合格数量；
7. Revision 稳定；
8. 精简与确定性。

### 13.2 当前 Chapter Set 实际目标

当前最多看 16 个候选，枚举最多 4 Chapter 的无素材重叠组合。比较目标按顺序是：

1. covered_asset_count；
2. episode_diversity；
3. chapter_count；
4. 模型自报 quality 总和；
5. 早出现的组合。

没有：

- 同一 Episode 被切成两个 Chapter 的惩罚；
- Chapter story duty 差异门；
- false split 风险；
- 完整 relation graph；
- Preview Revision 稳定。

### 13.3 本轮为什么选择了两个相似古镇 Chapter

- 单个确定性古镇组覆盖 8 项。
- 模型古镇组 1 覆盖 5 项。
- 模型古镇组 2 覆盖 7 项。
- 后两者不重叠，合起来覆盖 12 项。

由于 covered_asset_count 是第一目标，算法选择 5 + 7 的两个古镇组，而不是 8 项的一个古镇组。两章 Episode diversity 都只有 1，但覆盖更多素材的组合已经胜出。

所以最终出现：

- “古街市井”；
- “雨天街景”；

两者 Tag 完全相同，都是 CITY_WALK / HISTORIC_DISTRICT / HISTORIC_ARCHITECTURE，却没有被判为叙事重复。

### 13.4 当前 Aha Set

当前按时间顺序选择前 3 个合格 Aha，只有：

- 生日 Chapter 中 ceremony/result 高潮与 Chapter 重复时拒绝；
- 超过 3 个时停止。

没有全日 Aha 冗余、峰值强度、个人意义、类型多样性或“连续三次都是狗”的惩罚。

【诊断】

这是本轮最直接制造“聚类失误”的阶段。S07 提供了有问题的候选，S09 又用覆盖率把错误放大。

【可反馈点 S09】

- S09-1：同一长 Episode 何时允许拆成 2 个 Chapter。
- S09-2：如果两章 Tag 相同，是否必须证明故事职责不同。
- S09-3：覆盖更多素材和保持故事完整，哪一个优先。
- S09-4：Aha 是否需要类型多样性，还是只看单项质量。

---

## 14. S10｜选最终展示的 3–5 个素材

目的：Chapter 已经选定后，再选择最能讲清这段经历的画面，并指定一个 Hero。

【冻结目标】

先定义 Content Beat，再为每个 Beat 选择 Evidence Anchor：

- Content Beat：这个 Chapter 需要讲清的几个不同内容点，例如“进入古街”“沿河行走”“看到独特建筑”。
- Evidence Anchor：最能证明某个 Beat 的具体时刻。
- Media Decision：最终用 PHOTO、LIVE_2S 或 VIDEO_5S。
- HQ：只为已选 Anchor 请求高清源。

Chapter Standard 3–5 项，恰好一个 Hero；Aha 恰好一个可见媒体。

【当前实现】

- 候选成员少于 5：全选。
- 候选成员达到 5 或更多：固定取 5。
- 强制考虑第一项、模型自报质量最高的 Hero、最后一项。
- 其余按新增 motif/subject、与已选项的索引距离、quality 选择。
- Hero 由 quality、subject 数量和接近候选中部共同决定。
- 只返回 Evidence 静态预览，不生成 HQ、LIVE 或 5 秒视频。

【本轮结果】

- Chapter 1 候选正好 5 项，因此全部展示。
- Chapter 2 候选 7 项，展示第 8、9、14、16、20 项；第 14 项河岸拱桥成为 Hero。
- Writer 却仍收到 Chapter 2 全部 7 项的 19 条事实，不只收到 5 个最终展示媒体对应的内容。

【问题】

- “素材数量 3–5”被实现成“有 5 就一定取 5”，没有价值门。
- 没有明确 Beat，不能保证每张图承担不同叙事功能。
- 没有强近重复判断。
- 模型自报 quality 不等于真实构图、清晰度或用户偏好。
- 文字事实范围与最终媒体范围没有对齐。

【可反馈点 S10】

- S10-1：古镇 Chapter 中最合理的 3–5 个 Beat 是什么。
- S10-2：两张不同古建筑外观在时间与建筑差异满足什么条件时可同时保留。
- S10-3：Hero 优先代表故事，还是优先视觉质量。
- S10-4：Story 是否只能使用最终可见媒体能支持的主要内容。

---

## 15. S11｜Claims、文案和 Canonical Tags

目的：在故事和媒体都已经确定后，只依据批准事实生成自然、短、可回看的文字与检索索引。

### 15.1 冻结目标

先生成：

- ChapterFacts / AhaFacts；
- Claim Ledger；
- 允许进入用户文字的 Claims；
- Canonical Tag 与 Entity Index。

Writer 只能表达已批准 Claim，不得：

- 重新选 Chapter/Aha；
- 添加人物关系、用户情绪、意图或因果；
- 把几个离散画面写成持续发生；
- 添加没有证据的地点、口味或评价。

中文测试：

- Chapter Title 通常 2–10 字，必要时 11–12。
- Chapter Story 默认一句、最多两句，应该自然、有一点克制氛围，不做死板清单。
- Aha 只有一条不超过 20 个可见字符的 Moment Line。
- “小猫调皮”等共识性轻情绪词只能在真实动作支撑下窄范围使用。

### 15.2 当前 Writer 输入

当前没有真正的 Claim 取舍或 Content Plan。

对每个 Chapter，系统把候选所有 Observation 的所有 Facts 全部交给 Writer：

- Chapter 1：15 条事实。
- Chapter 2：19 条事实。

Prompt 虽然要求“避免 exhaustive fact recap”，但同时提供了大量事实，并允许 Writer 引用任意子集；没有确定性规则要求只选 2–4 个主 Claims，也没有给出主线、Beat 或叙事焦点。

### 15.3 本轮输出

- Chapter 1：“古街市井”，464 个可见字符。
- Chapter 2：“雨天街景”，634 个可见字符。
- 两段都是以分号连接的逐帧事实清单。

当前句数 Validator 只用句号、问号、叹号切句。大量分号连接的 634 字文本仍被计算为“一句话”，所以通过“最多两句”硬门。

48 字目前只是非阻断 writing target。这符合 V1.27：不能擅自把 48 变成无产品依据的硬删除门。但这也暴露出缺失的质量门——一句话并不等于简洁、自然或有故事。

### 15.4 Aha Writer 失败

三条 Aha Attempt 1：

- “棕白犬只佩戴蓝色背带，在石阶缝隙低头嗅探地面。”：23 字。
- “棕白犬只沿石板路前行，经竹棚下方，棚顶悬橙灯。”：23 字。
- “棕白狗在不规则石板弯曲小径上背对镜头行走，两侧为林地。”：27 字。

Attempt 2 返回了相同文本，仍然超过 20 字，三个全部阻断。

这证明 Prompt 中确实提前写了长度要求，但 Qwen 的 json_object 模式不会强制遵守字符上限；确定性 Validator 能发现失败，却没有一个可靠的短句修复器或更适合 Writer 的模型路由。

### 15.5 Claim 校验的缺口

当前只检查 Writer 返回的 claim_ids 是否属于提供的 Facts，并检查少量禁用词。它没有把文案中的具体文字 span 与 Claim 做逐句蕴含校验。

因此“引用了合法 Claim ID”不等于“整段文字的每个表达都被该 Claim 支持”。

### 15.6 Tags

当前 Tags 不是模型自由生成，而是按 Episode、Setting、Activity、Subject 多数投票，每个 Facet 最多一项。这比自由标签安全。

但本轮两个 Chapter 得到完全相同的三个 Tags，也反向证明两个 Chapter 的独立故事身份没有建立。

【诊断】

Writer 模型可以后续单独比较，但现在先换 Writer 模型不会修复错误 Chapter membership、错误 Aha 候选和没有 Content Plan。S11 是第四个 P0 阻断点，但不能被当作唯一问题。

【可反馈点 S11】

- S11-1：Chapter Story 是只表达 1 个主线 + 1 个氛围，还是允许 2–3 个 Beat。
- S11-2：除句数外，是否增加中文可见字符软区间和“分号清单”质量阻断。
- S11-3：Writer 应该收到全部合法 Facts，还是只收到 Editorial 预先选好的 Claims。
- S11-4：不同 Writer 模型的比较应使用同一份保存的 Writer Context，不重跑视觉理解。
- S11-5：Tag 相同的两个 Chapter 是否触发回到 S09 的叙事重复检查。

---

## 16. S12｜最终只读校验

目的：在物化前和实际媒体激活后，各做一次只读硬门。校验器不能自己删素材、改文案或替换候选；失败必须返回准确 owner。

【冻结检查】

- Day State 与 Chapter/Aha 数量是否合法。
- Chapter 素材与 Chapter 间冲突。
- Chapter/Aha 语义重复。
- Claims 是否都有 Evidence。
- Anchor 是否属于候选 Evidence。
- 媒体格式与 HQ route 是否合法。
- 失败应返回 S09、S10、S11、S13 replan 或 HOLD/BLOCK。

【当前实现】

当前 S12 运行约 0.32 毫秒，主要做结果组装、引用与媒体数量基础检查。没有完整：

- Chapter/Aha 语义重复 Validator；
- 文案 span-to-claim 校验；
- Anchor/HQ 两阶段验证；
- owner-specific replan；
- activation 后 S12B。

本轮 464/634 字事实清单仍被标为 STAGED_PREVIEW_VALIDATED。这个状态只表示 X02 当前简化合同通过，不能解释为产品质量已经验证。

【可反馈点 S12】

- S12-1：哪些质量问题必须阻断，哪些只记录 warning 等待真实用户评分。
- S12-2：Chapter 过长暂不武断硬删时，页面如何明确标成质量失败而不是“已验证”。

---

## 17. S13｜Selected HQ 与导出

目的：只为 S10 已经选中的 Anchor 获取高清源，生成最终 PHOTO、LIVE_2S 或 VIDEO_5S，并原子导出。

【冻结规则】

- 不默认上传全天 Auto Raw。
- 只 materialize 预先声明的 selected route。
- 失败只能 retry/HOLD 或按预声明 fallback，不改变事实和故事范围。
- 媒体激活变化后，受影响的 S11/S12 必须重验。
- User Diary Export 与 Internal Audit Run 分离。

【当前实现】

- originals_uploaded = 0。
- s13_status = NOT_EXECUTED_IN_WEB_PREVIEW。
- 当前页面展示的是抽取 JPEG Evidence，不是最终照片、Live Photo 或短视频。

【本轮影响】

当前测试可以评价“算法挑了哪几个原素材/证据帧”，不能评价最终视频剪辑、清晰度、画幅、加载体验或云存储成本。

【可反馈点 S13】

- S13-1：在结构质量可用前，不应投入大量 HQ/codec 工程。
- S13-2：后续真实 App 测试时，评估必须区分“Anchor 选对”与“最终媒体渲染好不好”。

---

## 18. 本轮 20 项素材如何一路流到结果

下表用“合成分钟”表示当前 Web 人为赋予的时间，不代表真实拍摄时间。

| 项 | 合成时间 | S04 简化语义 | Role / Moment | 最终去向 |
|---:|---:|---|---|---|
| 1 | 00 分 | 市集蔬果 | KEEP / M1 | MARKET 不足 3 项，未成 Chapter |
| 2 | 02 分 | 古街中的菜摊与行人 | KEEP / M2 | Chapter 1 |
| 3 | 04 分 | 面馆入口、狗嗅闻 | KEEP / M2 | Chapter 1；弱 Aha 候选 |
| 4 | 06 分 | 狗沿石板路、竹棚 | KEEP / M2 | Chapter 1；弱 Aha 候选 |
| 5 | 08 分 | 河岸、小船、柳树 | KEEP / M2 | Chapter 1 |
| 6 | 10 分 | 牌坊、摊位、扫地者 | KEEP / M2 | Chapter 1 |
| 7 | 12 分 | 林间石板路与狗 | KEEP / M3 | NATURE 不足 3 项；弱 Aha 候选 |
| 8 | 14 分 | 雨天道路、牌坊、车辆 | KEEP / M4 | Chapter 2 |
| 9 | 16 分 | 狗与传统建筑入口 | KEEP / M4 | Chapter 2 |
| 10 | 18 分 | 沿河石板步道 | KEEP / M4 | Chapter 2 候选，未进最终 5 媒体 |
| 11 | 20 分 | 林间台阶 | KEEP / M5 | NATURE 不足 3 项 |
| 12 | 22 分 | 输出词表合同失败 | DROP / M6 | 完全退出候选 |
| 13 | 24 分 | 输出词表合同失败 | DROP / M7 | 完全退出候选 |
| 14 | 26 分 | 河岸、石拱桥 | KEEP / M8 | Chapter 2 Hero |
| 15 | 28 分 | 输出词表合同失败 | DROP / M9 | 完全退出候选 |
| 16 | 30 分 | 祈福签、院门 | KEEP / M10 | Chapter 2 |
| 17 | 32 分 | 输出词表合同失败 | DROP / M11 | 完全退出候选 |
| 18 | 34 分 | 市集蔬果 | KEEP / M12 | MARKET 不足 3 项，未成 Chapter |
| 19 | 36 分 | 赵王殿建筑 | KEEP / M13 | Chapter 2 候选，未进最终 5 媒体 |
| 20 | 38 分 | 古越龙山石碑 | KEEP / M13 | Chapter 2 |

这张表显示：

- 古镇逛街内容不是“全部看不见”，而是部分被错误归类、部分因 S04 合同失败丢失、部分在候选最低数量门被淘汰、部分进入了过长的 Chapter 事实清单。
- 市集第 1 和第 18 项跨 34 个合成分钟，被同一 MARKET_VISIT 识别，但因只有 2 项无法成章。
- 两个 Chapter 不是两个清楚的故事，而是覆盖率目标切出的两个古镇片段。
- 三个 Aha 在 Writer 前确实存在，但质量弱且全部长度失败，所以页面最终显示 0。

---

## 19. 优先级诊断：先修什么，后修什么

### P0｜不修就不能继续相信质量测试

#### P0-1｜建立可信测试时间线与来源

至少让每项素材明确：

- 当前排序依据；
- 是否可信拍摄时间；
- 模拟 Auto/Manual；
- 真实时长；
- 若无时间，测试者是否人工分段。

否则 S05、resumed episode、全日数量和 Preview 都无法被真实评价。

#### P0-2｜停止把可修复的 S04 输出合同错误当成素材 FAILED

当前 V02 已补齐版本化兼容关系和失败诊断，但没有解决“词表外 subject code 导致整项 FAILED”本身。

需要比较：

- Provider strict structured output；
- item-level 定向重试；
- 明确且版本化的 alias mapping；
- 安全降级为 OTHER/UNKNOWN。

同时必须保存原始候选值、失败字段、规则版本和下游影响。不能静默修，也不能只留一个泛化错误码。

#### P0-3｜实现真正的 S03/S05 Moment 基线

至少先有：

- 真实时间 gap；
- 多原型 motif/embedding 表示；
- continuity 与 boundary 分账；
- Core/Tail/Pending；
- 有界 DEFER lookahead；
- Transition 与 resumed episode handoff。

#### P0-4｜重做 S07/S09 的故事职责和集合目标

必须停止：

- 用宽泛 Episode Code 代替 Chapter 语义；
- 以素材覆盖量作为首要胜负；
- 同一 Episode 无惩罚地重复切章。

应让“古镇市集、沿河行走、建筑探访”先成为可解释的 Beat/子故事假设，再判断是一个 Chapter 的不同 Beat，还是两个独立 Chapter。

#### P0-5｜Aha 先过独立记忆价值，再交给 Writer

普通狗行走不能因为 PLAYFUL_ANIMAL 枚举就通过。Aha 候选需要：

- 可描述的动作变化；
- 明确的局部峰值；
- 单独回看价值；
- 与 Chapter 不同的叙事职责；
- 全日去重。

#### P0-6｜S11 先做 Content Plan 和 Claim Selection

Writer 不应收到“请从 19 条事实里自己决定”。先由 Editorial 层确定：

- 一个主线；
- 2–4 个决定性 Claim；
- 对应 3–5 个媒体 Beat；
- 允许的轻氛围；
- 禁止的过度表达。

然后再比较 Writer 模型。否则换更强模型只是让错误结构写得更流畅。

### P1｜结构可用后立即补齐

- 独立 S08 one-question 补证。
- S10 Content Beat / Evidence Anchor / 强近重复 gate。
- S11 文案 span-to-claim 校验。
- S12 真正的 Chapter/Aha 重复、Owner replan 与两阶段状态。
- 把 STAGED_PREVIEW_VALIDATED 改成不会让人误以为“质量已通过”的分层状态。

### P2｜质量链路稳定后优化效率

- 浏览器并行或流水线抽帧。
- S04 批次并发与缓存。
- 照片只传 1 帧。
- Writer 使用独立、更适合中文短文案的模型。
- 保存 Writer Context 做离线模型对比，不重复付视觉理解成本。
- 真实 186 项 benchmark、P50/P95/P99、网络、电量、缓存和失败注入。

---

## 20. 下一轮工作的建议顺序

不是立刻大改全部阶段，而是按可验证的顺序推进：

### Gate A｜先让输入和 Observation 可信

1. 让 Web 显示并控制排序、来源和时间可信度。
2. 实现冻结的 Photo/Manual Video Evidence 合同。
3. 修复 S04 item-level 合同失败，并把原始错误与下游影响展示出来。
4. 用同一批 20 个视频重跑，目标不是先得到漂亮 Chapter，而是保证 20 项都有可解释终态。

### Gate B｜再让 Moment 和 Candidate 可信

5. 实现最小 S03/S05，而不是继续用枚举相等替代。
6. 在页面逐切口审阅 JOIN/SPLIT/DEFER。
7. 对古镇、市集、林间、院落建立细粒度 story-duty 候选。
8. 实现 S08 的两个本轮关键问题：Aha 峰值、同 Episode 是否应拆章。
9. 修正 S09 目标并重跑，不调用 Writer也能先评价结构。

### Gate C｜最后评价媒体和文字

10. 为每个选中 Chapter 明确 3–5 个 Content Beat。
11. 让 S10 为 Beat 选 Anchor，而不是固定凑 5。
12. 只把已批准 Claims 给 Writer。
13. 保存同一 Writer Context，对不同 Qwen Writer 模型做独立 A/B。
14. 加入结构化、逐 Chapter/逐媒体/逐表达的人评。

### Gate D｜结构质量通过后做规模化

15. 用 20、60、120、186 项四档真实素材测延迟与成本。
16. 再决定批量并发、缓存、上传队列、HQ 和后续 App 后台。

---

## 21. 下一次产品讨论真正需要决策的事项

这些是感性或用户体验定义，应该由产品参与，而不是由工程默认：

1. 一个持续 2–3 小时的古镇游览，在什么情况下应该是一章，在什么情况下允许两章。
2. 古镇市集是古镇漫步中的一个 Beat，还是在素材与事件足够强时成为独立 Chapter。
3. Aha 的“值得单独回看”最低标准；普通宠物行走是否一律不算。
4. 当前没有可信时间的手机素材测试，采用人工排序、人工时间段，还是只测试视觉理解而不评价时间结构。
5. Chapter Story 除“一到两句话”外，是否需要一个非硬删除的中文长度舒适区，以及什么情况应标为明显不可用。

其他工程性事项，如审计字段、缓存、错误归属、逐阶段耗时、Token 与成本记录，不需要逐项等待产品确认。

---

## 22. 术语表

### RawAsset

原始照片或视频及其不可改写事实，例如来源、拍摄时间、时长和哈希。

### Evidence

为了让算法低成本理解素材而抽出的代表帧、短 Proxy 或局部片段。Evidence 不是最终展示媒体。

### Window

一段局部时间范围。9 秒 Auto 通常是一个 Window；长 Manual Video 会拆成多个 Window。

### Embedding

把画面特征压成数字向量，用来计算“相似或不同”。它是证据，不是故事结论。

### Observation

只描述一个 Window 中直接看到了什么的结构化事实卡。

### Moment

在真实时间线上连续、语义相对纯净的一段内部结构。Moment 不等于 Chapter。

### Continuity Evidence

支持左右 Window 属于同一段的证据，例如相同活动线程、互补古镇 motif、短时间间隔。

### Boundary Evidence

支持左右 Window 在这里发生切换的证据，例如明显场景/活动变化、长时间间隔、Session 改变。

### DEFER

当前证据不足，先不决定合并还是切开；应该放入 Pending 并使用有限后续证据，而不是立刻默认归左或归右。

### Pending Window / Pending Block

等待边界判断的一个 Window，或连续多个等待判断的 Window。它们暂时不能污染左侧 Moment 的稳定 Core。

### Candidate

可能成为 Chapter/Aha 的候选假设。候选不等于最终输出。

### Content Beat

一个 Chapter 中需要被一个媒体项清楚表达的不同内容点。

### Evidence Anchor

最能证明某个 Content Beat 或 Aha 峰值的具体时刻。

### Claim Ledger

允许 Writer 使用的事实账本。每条 Claim 都能追溯到 Observation 与 Evidence。

### Canonical Tag

来自封闭、版本化概念词表的检索标签。它服务未来记忆检索和数据价值，不能由模型自由造词。

### HQ

High Quality，指最终选中后才请求或生成的高清照片、Live 片段或短视频，不是当前页面的低成本 Evidence。

---

## 23. 本文的边界

本文证明：

- 我们已经能够精确指出最新一轮为什么不可用；
- 问题责任分布在多个阶段，不应只归咎于 Writer；
- 当前 X02 与冻结 S00–S13 之间的真实差距已经逐项列明；
- 下一轮可以按 Stage 和编号收集具体反馈。

本文不证明：

- 推荐修复方案已经冻结；
- 当前模型阈值已经校准；
- 这 20 个视频代表所有用户；
- 当前成本可以线性外推到 186 项生产日；
- X02 已达到真实用户质量、正式 App、云端 Production 或 S13 就绪。

下一步最合理的讨论起点不是“要不要生成 3 个还是 4 个 Chapter”，而是先从 P0-1、P0-2 开始，让输入时间线和每项 Observation 变得可信；随后再用相同素材逐切口审阅 S05、逐候选审阅 S07/S09。
