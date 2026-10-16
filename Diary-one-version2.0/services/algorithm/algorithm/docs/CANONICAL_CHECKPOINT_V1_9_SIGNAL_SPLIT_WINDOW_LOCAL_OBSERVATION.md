# Diary One Canonical Checkpoint V1.9 — Signal Split and Window-Local Observation

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** S03 的 Window 自身信号/时间线关系信号拆分，以及 S04 的 Window-local 事实理解与缓存边界
**继承关系：** 继承 V1.8–V1.1 与 V1.0 未被覆盖的规则

> **当前输出覆盖：** V1.10 在本文 Window-local 边界内进一步冻结 Observation Lite 的最小输出、状态、逐条 Frame grounding 与 evidence support grade。

> **当前下游覆盖：** V1.11–V1.15 已冻结 S05 的连续 Moment partition、双向边界证据账本、四状态决策、多原型 Core/Tail/Pending、commit-on-MERGE、unresolved transition 隔离 fallback，以及当前有界 DEFER/lookahead Baseline；具体信号阈值、Motif/prototype 参数和真实数据再校准仍需 Benchmark。

> **当前 S06 覆盖：** V1.16 冻结每个 Observation 的唯一内容角色；角色可以引用本文与 S05 的 facts/ledger，但不能改写 Window-local facts，也不能反向成为 S05 boundary evidence。

## 1. 冻结结论

S03 不再使用一个混合对象同时保存“Window 自己的固定信息”和“Window 与邻居的可变关系”。正式拆成：

```text
S03A WindowIntrinsicSignal
→ Window 自身卡片
→ 内容不因前后素材变化而改变

S03B TimelineEdgeSignal
→ 两个 Window 之间的连线
→ 新素材插入时只更新受影响的连线
```

S04 Observation Lite 只依据当前 Window 自己的 Evidence 生成事实，不读取邻近 Window 的图片或语义结果。跨 Window 的连续性、边界和 Moment 归属统一由 S05 判断。

## 2. S03A｜WindowIntrinsicSignal

`WindowIntrinsicSignal` 是一张 Window 自身卡片，至少包含：

- `evidence_window_id`、RawAsset identity 与 capture facts；
- Auto / Manual、Photo / Video、duration；
- frame extraction / missing / corruption；
- brightness、exposure、blur、occlusion、stability；
- Window 内 Frame 之间的变化、矛盾或场景切换提示；
- versioned lightweight visual embedding；
- visual reliability 与 `UNKNOWN` reason；
- signal algorithm/version/parameter/compute provenance。

其中决定 Auto `UPLOAD_1 | UPLOAD_3` 所必需的 quality、三帧两两 similarity 和 within-window change 必须在 Phone 上传前完成。其他不参与上传路由的固有信号可以由 Phone 或低成本后端计算，具体运行位置留给 Benchmark，但相同输入与版本只生成一次。

`WindowIntrinsicSignal` 不包含“与当前前一条/后一条 Window 的关系”，因此新素材插入时间线时不需要重算旧 Window 卡片。

## 3. Embedding 的边界

Embedding 是把当前 Window 的视觉内容转换成一组可比较数字，可以理解为该画面在视觉地图上的坐标。

它可以用于：

- 快速比较视觉相似度；
- 发现明显场景变化；
- 为 S03B 生成 Window 间距离。

它不能单独证明：

- 发生了什么活动；
- 人物身份或关系；
- 是否值得成为 Chapter/Aha；
- 两个视觉相似 Window 一定属于同一生活事件。

## 4. S03B｜TimelineEdgeSignal

`TimelineEdgeSignal` 描述两个按时间排序的 Window 之间的关系，至少包含：

- `from_window_id` / `to_window_id`；
- capture time gap；
- capture session continuity；
- visual similarity / perceptual distance；
- embedding distance；
- change / contradiction hint；
- edge algorithm/version/provenance。

它不改写任一 Window 的固有事实。

滚动导入示例：

```text
原时间线：A → B
原连线：  edge(A,B)

后到素材：A → X → B
失效：    edge(A,B)
新增：    edge(A,X) + edge(X,B)
```

系统只更新受影响的 Edge，不重新抽取 A/B、不重新计算 A/B 的 intrinsic signal，也不重新理解 A/B 的 Observation。

默认 Edge 以时间相邻 Window 为基础；是否比较更远邻居或维护小型候选邻域属于 S05 Benchmark 参数，不在本检查点冻结。

## 5. S04｜Window-local Observation

每个 Observation Lite 只读取：

- 当前 `evidence_window_id` 的实际上传 Evidence；
- 当前 Window 的 `WindowIntrinsicSignal`；
- 当前 RawAsset 的可信时间、来源与时长事实；
- V1.6/V1.8 route manifest 与输入状态。

S04 不读取邻近 Window 的图片、Caption 或 Observation，不在这一阶段决定两个 Window 是否属于同一 Moment。

允许输出当前 Window 内部的：

- visible facts；
- coarse scene / directly supported activity；
- 匿名 entity / object descriptors；
- within-window change；
- visual reliability 与 uncertainty；
- `INSUFFICIENT_EVIDENCE` 等状态。

跨 Window entity continuity、scene continuity、boundary 与 Moment merge/split 由 S05 使用下列输入统一判断：

```text
Window-local Observation[]
+ TimelineEdgeSignal[]
→ S05 Moment Formation
```

## 6. Batching 不改变独立理解

多个 Window 可以为了减少请求开销被放进同一模型请求，但这只是传输与执行 batching：

1. 每个 Window 具有独立输入分区和 `evidence_window_id`；
2. 每个输出只引用自己的 Frame；
3. 模型不得把同一请求中其他 Window 的事实写入当前输出；
4. 一个 Window 失败不使其他输出失去独立状态；
5. batch size 与并发继续由真实 token/latency Benchmark 决定。

## 7. 只允许精确缓存复用

以下条件全部相同时，可以直接复用已有 Observation：

- 相同 Evidence identity/content hash；
- 相同实际输入 Frame 集合；
- 相同 Observation schema、model、prompt、parameter 与版本。

不同 Window 即使视觉高度相似，也不能直接复制 visible facts、activity、entity 或其他语义结果。Near-duplicate 只可以用于：

- S03B 的相似度/重复提示；
- batching 或处理优先级；
- S06/S07 以后 Manual/Memory 候选抑制；
- 独立实验，但不得进入当前 Canonical 事实链。

这是对 V1.7 “near-duplicate 可复用语义核心”的正式覆盖。

## 8. 成本与增量不变量

- 每个 Window 的固有信号按输入和版本计算一次；
- 上传路由所需信号在 Phone 完成，不形成端云循环依赖；
- 新/晚到素材只更新自身卡片和受影响的 Timeline Edge；
- Window-local Observation 不因邻居变化而重算；
- 完全相同输入命中缓存；近似输入不复制事实；
- batching 可以减少请求开销，但不等于减少逻辑 Observation 数量。

## 9. FROZEN 与 OPEN

### FROZEN

- S03A 保存 Window 自身固有信号；
- S03B 保存 Window 之间的时间线关系；
- 新素材插入时只局部更新相关 Edge；
- Auto 上传路由所需信号必须在 Phone 上传前完成；
- S04 只依据当前 Window 的 Evidence 和固有信号生成事实；
- S04 不读取邻居图片或语义结果；
- S05 统一判断跨 Window 连续性与 Moment 边界；
- batching 不允许跨 Window 混写事实；
- 只有完全相同的输入和算法版本可以复用 Observation；
- near-duplicate 不得直接复用语义事实。

### OPEN / Benchmark 校准

- intrinsic embedding 模型、维度、量化与运行位置；
- quality、similarity、change 的算法和阈值；
- Timeline Edge 的邻域范围；
- batch size、视觉 Token 上限、并发和失败隔离实现；
- S05 continuity / boundary 的聚合与阈值、Context Motif/prototype 参数和 lookahead 配置。

## 10. 当前实现 GAP

- 当前仓库没有正式 `WindowIntrinsicSignal` 或 `TimelineEdgeSignal` schema；
- 尚未实现 late insertion 的局部 Edge invalidation；
- 尚未实现 Window-local Observation runner 与输入隔离测试；
- V1.7 中的 near-duplicate semantic reuse 尚未存在代码，但相关文档含义已由本检查点覆盖；
- 所有质量、成本和 Moment 收益仍需真实 wearable Benchmark。
