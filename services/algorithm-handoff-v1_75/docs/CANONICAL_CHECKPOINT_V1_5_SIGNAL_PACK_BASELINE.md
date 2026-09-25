# Diary One Canonical Checkpoint V1.5 — Signal Pack Baseline

**状态：** `FROZEN`
**冻结日期：** 2026-08-25
**决策来源：** 用户显式确认
**作用范围：** S03 Deterministic Signal Pack 的最小必要信号与质量边界
**继承关系：** 继承 V1.4、V1.3、V1.2、V1.1 与 V1.0 未被覆盖的规则

> **当前结构覆盖：** V1.9 将本文六组逻辑信号拆分为 `WindowIntrinsicSignal` 与 `TimelineEdgeSignal`。Window 固有信号可按输入缓存；相邻关系属于可局部失效的 Edge，不能与 Window 卡片共用不可变缓存语义。

## 1. 目的

S03 在生成式或多模态内容理解之前，用便宜、版本化、可重复计算的信号描述每个 Evidence Window。它为后续 continuity、boundary、重复判断、成本路由和不确定性提供依据，但不回答“发生了什么”或“是否值得记住”。

## 2. V1 最小 Signal Pack

V1 仍需要以下六组逻辑信号，但按 V1.9 分别存入 Window 自身卡片和时间线关系 Edge：

### 2.1 时间与 Session

- capture time / timeline range；
- capture session identity；
- 时间可信状态。

与前后 Window 的 time gap 和 session continuity 存入 `TimelineEdgeSignal`。

### 2.2 来源与媒体事实

- Auto / Manual；
- Photo / Video；
- RawAsset duration；
- Evidence Window duration 与 frame count。

### 2.3 Evidence 有效性与画质

- frame extraction success / missing；
- brightness / darkness；
- exposure；
- blur；
- severe occlusion；
- stability / corruption；
- visual reliability 与 reason。

### 2.4 Window 内变化

- 代表帧之间的视觉变化量；
- motion amount proxy；
- motion peak hint；
- frame-to-frame contradiction 或明显场景切换提示。

这些信号只说明“变化了多少”，不解释动作语义。

### 2.5 相邻重复与相似性

- perceptual hash / exact visual duplicate hint；
- Window 自身的 perceptual representation；
- duplicate 判断所用版本、阈值与比较对象。

与时间相邻 Window 的视觉相似度和 within-session near-duplicate hint 存入 `TimelineEdgeSignal`。S03 只产生信号和候选分组，不因相似度单独删除生活事实。

### 2.6 轻量视觉特征

- versioned image embedding 或等价的非生成式视觉表示；
- Window-level aggregation；
- compute model/version/device provenance。

Window embedding 存入 `WindowIntrinsicSignal`，与相邻 Window 的 embedding distance 存入 `TimelineEdgeSignal`。Embedding 是 continuity / change 信号，不是 Chapter、人物关系或活动真相。

## 3. 可选信号

- trusted GPS / coarse location continuity：只有来源可信且存在时使用；
- audio-present / speech-present gate：只判断是否值得进入后续音频路径，不做 ASR；
- device motion metadata：只有上游能够可靠提供时使用。

缺失的可选信号必须表示为 `UNKNOWN` / `NOT_AVAILABLE`，不能当作 false 或零值。

## 4. 低画质原则

```text
LOW_QUALITY ≠ DELETE
```

低画质 Evidence 仍可能提供：

- 时间和 Session continuity；
- 运动或转场提示；
- 音频入口；
- Moment boundary；
- 前后高质量 Evidence 的上下文。

S03 只能降低 visual reliability、标记原因或提供 routing hint，不能直接决定 DROP、Chapter/Aha 资格或永久删除。

## 5. 明确禁止

S03 不输出：

- 图像 Caption 或事件总结；
- 人物身份、关系、情绪或用户意图；
- activity / scene 的生成式结论；
- Chapter/Aha 分数；
- 记忆价值；
- 永久保存或删除决定；
- ASR 文本。

## 6. 输出合同

```text
WindowIntrinsicSignal
├── evidence_window_id
├── source / media facts
├── quality_and_reliability
├── within_window_change
├── lightweight_visual_feature
└── provenance / errors / unavailable_reasons

TimelineEdgeSignal
├── from_window_id / to_window_id
├── time_gap / session_continuity
├── visual_similarity / embedding_distance
└── edge version / provenance
```

相同 Evidence 和版本下，Window 固有信号可缓存。新/晚到素材只失效受影响的 Timeline Edge，不重新计算旧 Window 卡片。

## 7. 成本与运行位置

- S03 不调用生成式模型或 VLM；
- 优先使用 Phone 或低成本 CPU/轻量模型；
- 每项信号必须记录耗时、运行位置、版本和失败原因；
- 任何本地计算都必须进入 Phone processing / energy Benchmark；
- 信号计算失败不能阻断全天处理，应产生明确 `UNKNOWN` 与降级路径。

## 8. FROZEN 与 OPEN

### FROZEN

- V1 使用本检查点定义的六组最小信号；
- trusted GPS、audio/speech gate 和 device motion 仅为可选信号；
- S03 无生成式模型调用；
- 低画质不等于删除；
- S03 不决定内容语义、Memory 价值或最终 DROP；
- Window 固有信号与 Timeline Edge 分开版本化并保留 provenance；
- Window 固有信号可缓存，关系 Edge 可在时间线变化时局部失效；
- 缺失信号必须显式 UNKNOWN。

### OPEN / 待真实 Benchmark 校准

- blur、exposure、occlusion、motion 与 similarity 的具体算法和阈值；
- embedding 模型、维度、量化和 Phone/Cloud 运行位置；
- duplicate group 的时间邻域和代表素材规则；
- audio/speech gate 的模型与能耗；
- Signal Pack 对上传量、Moment quality 和 AI cost 的真实收益。

## 9. 当前实现 GAP

- 当前仓库只有 placeholder embedding 或零散研究信号，没有符合 V1.5 的正式 SignalPack；
- 尚未实现两个版本化输出合同、Edge 局部失效、失败/UNKNOWN 状态、缓存键或成本 Trace；
- 尚未用真实 wearable Evidence 校准任何质量、相似度、运动或 embedding 阈值。
