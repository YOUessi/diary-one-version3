# Chapter V2 · P0/P1/P2 工程状态

日期：2026-11-01。研究分支：feature/2026-10-30-chapter-v2-boundary。

## 整体结论

这是全局算法研究分支，代码已接入P0第二批/P1/P2的主要数据流，但**并非通过真实多领域实验验证的正式上线版本**。旧V03/V04证据包保持兼容；新功能仅通过可选V05证据包触发，尚未部署。

## P0 第二批：S08结构合并/删除与有界重规划

- 新增chapter_boundary_planner.py：完整S07草稿→S08事实锚点去向复核，独立模型给出KEEP_MERGED / KEEP_AS_MOMENT / RESTORE_CHAPTER / DROP_UNSUPPORTED / REVIEW_REQUIRED及事实ID。
- 每个决策只能引用本轮视觉核验过的事实，非法事实/未知章节ID fail-closed。
- 仅对真正丢失且经视觉核验的S07锚点触发S08B，必要时通过S08C最多一次有界重规划；未通过结构编译则保留旧结果并留下REPLAN_BLOCKED审计。
- 不因S07草稿要求强行保留被删章；同一活动也不必强行拆章。
- 还缺：同一真实源素材S08B/S08C完整API对照、模型语义审查误差和时延成本评测。

## P1：Scenelet与时间线

- scenelet_builder.py：根据候选事实、可选同版本embedding、活动/场景信息、可靠采集时间生成全局Scenelet地图。
- chapter_boundary_planner.propose_chapters：输出全日参考分段与scenelet证据映射；不是硬性的5章要求。
- 增加可选Bundle V05，仅V05可以附capture_time_ms / capture_time_source / capture_time_confidence，旧V04拒绝新增字段。未明确验证的时间不会当作拍摄时钟。
- Scenelet数量超过模型上下文限额时给出分层汇总与完整ID映射，底层审计不静默截断。
- 还缺：真实多领域独立场景标注与自动边界匹配效果评测；词汇与视觉阈值未经系统校准。

## P2：逐章选图、全局覆盖门禁、Motion Chapter

- chapter_media_pool.py：V05按章节独立提取已核验候选，轮询预算实现跨章节覆盖；S09A逐帧图像审查采用有界批处理。
- chapter_coverage_gate.py：分别审查语义场景覆盖与真实媒体覆盖；高证据场景未表示时标为待审核，不能机械要求新增章。
- iOS ChapterMotionExporter.swift：从已经入选的原始10s视频基于focus_pts截取3秒无声MOV，并重新导出源片同时间的静态图；没有上传原视频。
- buildLiveChapterCovers.ts：云端Chapter返回后仅针对最终入选的Chapter media/highlight生成动态资产；原生不可用时保留3秒来源窗口，原图不改变。
- ChapterMotionPlayer.tsx + Chapter UI：优先显示动态；旧V04维持原有静态/按需播放交互。
- 注意：这里是**App内动态Chapter**，还不是Apple Photos系统原生Live Photo的HEIC+MOV配对/相册写入，仍需单独设备端真机集成和实况标识验收。
- 还缺：iPhone实机运行、片段导出成功率、不同分辨率/帧率/边界帧实际测试、Android真实设备验证。

## 已核对的自动测试及其边界

- Python整体pytest: 1210 passed / 25 skipped / 158 subtests（本次分支的全面后端测试）。
- npm run typecheck: PASS。
- npm run test:core：针对V05动态模块静态引入引起的13项Unmocked expo失败，改成V05分支内按需动态导入后，201项全部通过。
- Apple Swift Xcode iOS SDK ChapterMotionExporter单文件typecheck: PASS，有iOS16废弃API告警，但无类型错误。
- V05时间协议及逐章候选专项: 14 passed，18 subtests。
- 未执行：全平台生产Archive/设备实机运行/真实DeepSeek-Qwen云端全链路A/B。
- 以上只证明接口、数据合同、回归通过，**不代表真实Chapter质量已经达到上线水平**。

## GitHub提交原则

阶段代码作为研发分支保存，不合并main，不自动部署。后续所有真实A/B都要固定数据/模型/时序来源、记录调用费及逐例人工评价，跨六类场景给出正反例，不能仅用悉尼人工5章作为真值。
