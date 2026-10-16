# Diary One Canonical Checkpoint V1.3 — Auto Three-Frame Evidence

**状态：** `FROZEN`
**冻结日期：** 2026-08-25
**决策来源：** 用户显式确认直接锁定固定三帧
**作用范围：** S02 中 Diary One Auto 9 秒视频的默认 Evidence 表示
**继承关系：** 继承 V1.2、V1.1 与 V1.0 未被覆盖的规则

> **当前部分覆盖：** V1.6 保留本文固定三帧抽取合同，但将默认云端输入改为保守的 `UPLOAD_1 | UPLOAD_3`。本文关于“三帧全部作为默认 Observation 输入”和“不自适应减少上传帧数”的条款不再是当前规则。

## 1. 冻结结论

每个合法的 Diary One Auto 9 秒视频，在 V1 中固定产生恰好三张代表帧：

```text
1.5 s
4.5 s
7.5 s
```

三帧共同构成该 Auto RawAsset 在 Phone 端的标准视觉 Evidence。Phone 不根据内容减少抽取帧数；Cloud 按 V1.6 在一帧或三帧之间保守路由，也不默认上传完整 9 秒视频。

## 2. 为什么采用固定三帧

1. 覆盖视频前、中、后三个位置，降低单张中间帧漏掉场景变化的风险；
2. 输入确定、可重跑、可跨模型和跨实验比较；
3. 不依赖尚未验证的端侧内容分类器或动态阈值；
4. 每条 Auto 的 Phone 抽取量固定，Cloud 上传量与模型输入量可按 V1.6 单独核算；
5. 能先建立可信 Baseline，再用相同 Benchmark 判断动态 proxy 或完整视频是否真正提升 Memory Quality。

## 3. Evidence 合同

每一帧至少记录：

- `frame_id`；
- `raw_asset_id`；
- 目标 offset 与实际解码 timestamp；
- 原始宽高、方向与任何空间变换；
- Evidence 输出尺寸、编码、bytes 与 hash；
- extraction version；
- extraction status 与失败原因。

三帧必须全部指回同一 RawAsset，不得用另一条素材的画面填补。若某个位置无法可靠解码，记录缺失或失败，不复制邻近帧伪装成成功抽取。

实际解码允许选择最接近目标 offset 的合法视频帧；时间容差、关键帧 seek 与精确解码策略留给真实媒体实验校准，但实际 timestamp 必须进入 provenance。

## 4. 云端输入与缓存

- 三帧是该 Auto Asset 的 Phone Evidence 合同，不再等同于固定 Cloud 输入量；
- Cloud 正常输入依 V1.6 为 `UPLOAD_1` 或 `UPLOAD_3`；不确定、变化或信号不完整时必须上传三帧；
- `UPLOAD_3` 的三帧可以分别传输，也可以在不损失 frame identity 和 provenance 的前提下做批次或视觉打包；
- `UPLOAD_1` 未上传的两帧不进入 Cloud Observation；按 V1.8，Cloud 不请求补帧，单帧不足时该 Window 退出 Memory 候选；
- 相同 RawAsset、Evidence version、模型和参数下，已经完成的 perception 结果必须复用；
- 后续 Preview Revision 与 Final 不得重复上传或重新理解已有结果。

## 5. 事实边界

三张静态帧只能证明三个离散时刻可见的内容，不能单独证明：

- 动作在整个 9 秒内持续发生；
- 帧间发生的精确动作顺序；
- 未出现在三帧中的短暂峰值；
- 声音、语言或因果关系。

Observation 必须表达不确定性，不能把三张离散图像写成连续视频事实。

## 6. 成本容量

高强度参考日中：

```text
150 Auto Video × 3 Frames = 450 Auto Evidence Frames
```

结合已规划的 Manual Photo / Video Evidence，高强度日 Phone 总抽取计划为 570 张代表帧。Cloud 实际上传帧数按 V1.6 为 `570 - 300p`，其中 `p` 是 Auto 进入 `UPLOAD_1` 的比例；滚动 Preview 不得重复上传或理解已有 Evidence。

## 7. 非默认升级路径

以下能力不属于 V1 默认输入，但可在独立实验中比较：

- low-resolution temporal proxy；
- 更密集的局部帧；
- 完整 9 秒视频；
- 音频或 gated ASR。

升级只能用于少量明确模糊、动态价值高或最终验证困难的 Evidence。它们不能静默取代固定三帧 Baseline。

## 8. FROZEN 与 OPEN

### FROZEN

- Auto 视频逻辑时长为 9 秒；
- 每条 Auto 恰好规划三个目标位置：1.5 / 4.5 / 7.5 秒；
- Phone 端不自适应减少三帧抽取；Cloud 端按 V1.6 保守选择一帧或三帧；
- V1 不默认上传完整 9 秒视频；
- 三帧 provenance 与 perception 可缓存；
- 三帧不得被解释为连续动作事实。

### OPEN / 待真实媒体实验校准

- Evidence JPEG/AVIF 等编码与质量；
- 输出分辨率和上传 bytes 目标；
- 精确解码容差与失败恢复；
- `UPLOAD_3` 时三图分别输入还是保持 frame identity 的视觉打包；
- selective temporal proxy 的升级门槛；
- 真实 Phone compute、energy、上传量和模型成本。

## 9. 当前实现状态

- `src/diary_one_ci/evidence.py` 已实现三个固定目标 offset 的确定性 planning；
- `tests/test_evidence_builder.py` 已覆盖高强度日 150 Auto → 450 Auto Frame 的计划数量与可追溯性；
- 尚未实现从真实视频精确解码三张 Evidence、编码、hash、上传与设备侧成本测量；
- X01/App Library 的任意相册媒体兼容路径不等于本检查点的真实 Diary One Auto 输入。
