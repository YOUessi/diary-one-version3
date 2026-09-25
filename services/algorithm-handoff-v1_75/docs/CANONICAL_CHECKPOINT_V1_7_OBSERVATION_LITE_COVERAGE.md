# Diary One Canonical Checkpoint V1.7 — Observation Lite Coverage

**状态：** `FROZEN`
**冻结日期：** 2026-08-25
**决策来源：** 用户显式确认
**作用范围：** S04 Observation Lite 的全 Window 覆盖、批处理、精确缓存与职责边界
**继承关系：** 继承 V1.6–V1.1 与 V1.0 未被覆盖的规则

> **当前部分覆盖：** V1.8 取消本文 `NEEDS_MORE_EVIDENCE` 后的 Auto 补帧路径。单帧不足改为 `INSUFFICIENT_EVIDENCE`，保留记录但退出 Memory 候选。

> **当前结构覆盖：** V1.9 保留逐 Window 记录和 batching，但取消 near-duplicate 语义复用及邻居参与 S04 理解。S04 只使用当前 Window；跨 Window continuity/boundary 由 S05 判断。

> **当前输出覆盖：** V1.10 已冻结 Observation Lite 的最小字段类别、顶层状态、逐条 Frame grounding 与 `STRONG/MODERATE/WEAK` evidence support；不再使用单一 Production Observation 总置信分。

## 1. 冻结结论

每个 accepted Evidence Window 都必须在时间线上拥有一个唯一、可追溯的 Observation Lite 记录槽位。

这不等于每个 Window 都单独调用一次云端模型：

```text
Every accepted Evidence Window
→ one traceable Observation Lite record

Multiple Windows
→ may share one batched request

Identical Evidence + identical pipeline version
→ may reuse the exact cached result
```

理解失败、输入不足或 Evidence 不可靠时，也必须留下 V1.10 定义的显式 `OBSERVED / PARTIAL / INSUFFICIENT_EVIDENCE / FAILED` 状态；`UNKNOWN` 只用于具体字段，不能跳过该时间点或编造事实补齐。

## 2. 四个数量必须分开

S04 的成本与覆盖至少分开记录：

1. `evidence_window_count`：逻辑时间窗口数量；
2. `observation_record_count`：逐 Window 的 Observation 记录数量；
3. `semantic_inference_unit_count`：实际执行或命中精确缓存的独立语义理解单元数量；
4. `model_request_count`：经过 batching 后的 API 请求数量。

高强度参考日正常规划为 220 个 Evidence Window，因此目标是 220 个 Observation 记录槽位，而不是 220 次 API 请求。请求数、语义理解次数和视觉输入帧数都可能更少，但不得通过删除时间线 Window 来伪造节省。

## 3. 输入合同

每个 Observation Lite 至少基于：

- `evidence_window_id` 与 RawAsset provenance；
- 实际上传的 Evidence Frame；
- V1.6 的 extraction / upload route manifest；
- S03 SignalPack；
- 可信的 capture time、source、media kind 与 duration 事实。

对于低画质、信号缺失或只剩部分 Evidence 的 Window，输入状态必须显式传递，不能默认为正常素材。

## 4. Auto 的一帧或三帧仍只对应一个 Observation

- `UPLOAD_1` Auto：一个 Window、一个 Observation；输入为一张代表帧及完整路由依据；
- `UPLOAD_3` Auto：一个 Window、一个 Observation；输入为三个带独立 offset 和 frame identity 的帧；
- `UPLOAD_1` 不得被解释为“九秒内没有任何变化”，它只表示 Phone 的保守门判断三张离散帧高度相似；
- 若一帧不足以可靠描述该 Window，Observation 标记 `INSUFFICIENT_EVIDENCE`；
- 该 Window 退出 Chapter/Aha 候选，不请求另外两帧，也不上传完整 9 秒视频。

## 5. Batching 只减少请求，不合并事实

多个 Window 可以放入一次低成本多模态请求，但必须满足：

1. 每个输出明确绑定自己的 `evidence_window_id`；
2. 每个 Window 的 visible facts 只能来自自己的 Evidence；
3. 同一 batch 中其他 Window 不参与当前 Window 的事实、continuity 或 boundary 输出；
4. 单个 Window 失败不能使整批结果被静默接受或丢失；
5. 重试、部分失败与每个输出的模型 provenance 都可追踪。

Batch size、并发数和图片包装方式属于 Benchmark 参数，不在本检查点冻结。

## 6. 精确缓存复用

完全相同的 Evidence、模型、prompt、参数和版本必须命中确定性缓存，不重复付费理解。

只有 Evidence identity/content、实际输入 Frame 集合、schema、model、prompt、parameter 与版本全部相同，才允许直接复用 Observation cache。

不同 Window 之间即使视觉高度相似，也不得复制 visible facts、activity、entity 或其他语义结果。Near-duplicate 只作为 S03B 相似度、batching/优先级或后续 Memory duplicate suppression 信号。Manual 的候选抑制仍在 V1.6 规定的后续阶段执行。

## 7. Observation Lite 的职责边界

允许描述的类别：

- Evidence 中可见或可直接支持的 facts；
- coarse scene / activity；
- 当前 Window 内的匿名 entity / object descriptors；
- visual reliability、uncertainty 与 contradiction；
- within-window change hint；
- Evidence 是否足以支持可用事实。

禁止在 S04 决定：

- 是否值得记住；
- 是否属于 Chapter 或 Aha；
- 用户情绪、人物关系、意图或主观意义；
- 永久保存或最终媒体选择；
- Evidence 不支持的持续行为或因果关系。

Observation Lite 是 perception 事实层，不是 Memory 价值判断层。

## 8. 成本与质量含义

在没有复用时，220 个 Window 若按每次 8 个批处理，约为 28 次请求；这只是容量示例，不是冻结配置。实际请求数还受 batch size、失败重试、输入限制和 duplicate reuse 影响。

V1.6 已使高强度日视觉上传帧数从 Phone 抽取的 570 帧变为：

```text
Full-day uploaded frames = 570 - 300p
```

因此 S04 必须同时记录 image count / bytes、视觉与文本 Token、cache/reuse hit、请求数、重试、latency 和费用。不能只用“调用次数”代表真实成本。

质量侧至少关注：

- Fact Precision；
- Unsupported Fact Rate；
- Window Coverage；
- UNKNOWN calibration；
- batching 的跨 Window 事实污染率；
- exact cache hit rate；
- `UPLOAD_1` 的 `INSUFFICIENT_EVIDENCE` 比例与候选召回损失；
- 对后续 Moment boundary 的影响。

## 9. FROZEN 与 OPEN

### FROZEN

- 每个 accepted Evidence Window 都有独立可追溯的 Observation 记录槽位；
- 高强度参考日 220 Window 对应 220 个逻辑 Observation 槽位，不等于 220 次请求；
- batching 可以减少请求，但不能合并 Window 的事实归属；
- 只有完全相同的 Evidence 输入和 pipeline 版本可以复用 Observation；
- near-duplicate 不得直接复用语义事实；
- Auto 的一帧或三帧输入都只生成一个 Window Observation；
- 失败、未知和证据不足必须显式表达；
- Observation Lite 只做事实理解，不判断 Chapter/Aha 或个人意义；
- selective enrichment 留给后续阶段。

### OPEN / Benchmark 校准

- Production JSON Schema 的精确字段名与数组上限；
- coarse scene / activity taxonomy 的后续版本；
- 模型、prompt、输出约束与图片分辨率；
- batch size、并发、timeout 与 retry；
- near-duplicate 对 batching、优先级和后续候选抑制的阈值；
- `INSUFFICIENT_EVIDENCE` 的可靠判定方式；
- 单日成本与 latency 实测。

## 10. 当前实现 GAP

- 当前仓库没有 Production Observation Lite schema、runner 或逐 Window 状态机；
- 尚未实现批处理隔离、Window-local 输入验证、部分失败、exact cache provenance 或 `INSUFFICIENT_EVIDENCE` candidate gate；
- X01 的单轮 Chapter/Aha 生成不是本检查点定义的 S04；
- 28 次请求与所有成本数字均是容量推导，尚无真实高强度 wearable Benchmark。
