# Diary One Canonical Checkpoint V1.4 — Manual Evidence

**状态：** `FROZEN`
**冻结日期：** 2026-08-25
**决策来源：** 用户显式确认
**作用范围：** S02 中 Diary One Manual Photo 与 Manual Video 的默认 Evidence 表示
**继承关系：** 继承 V1.3、V1.2、V1.1 与 V1.0 未被覆盖的规则

## 1. 冻结结论

Manual 素材采用固定、按媒体类型与视频时长分级的 Evidence 规则：

| Manual RawAsset | Evidence Window | Frames per Window | Total Frames |
|---|---:|---:|---:|
| Photo | 1 | 1 | 1 |
| 15s Video | 2 | 2 | 4 |
| 60s Video | 4 | 2 | 8 |
| 120s Video | 6 | 2 | 12 |

Manual 是用户主动记录的事实信号，因此允许比 Auto 使用更密集的 Evidence；它仍不绕过质量、事实与最终选择门槛。

## 2. Manual Photo

- 每张 Manual Photo 产生一个静态 Evidence；
- 标准 Evidence 使用一张规范化代理图，不复制成三个虚假时间位置；
- `source_timestamp` 为空或明确标记为 still；
- 原始高分辨率照片保留在 phone source cache；
- 只有 Memory 入选并确定 EvidenceAnchor 后，才请求 HQ source 用于最终渲染。

Evidence 的编码、分辨率和压缩质量由真实视觉与上传 Benchmark 决定，不在本检查点冻结。

## 3. Manual Video Window

Manual Video 按实际时长划分为连续窗口：

```text
15s  → 2 windows
60s  → 4 windows
120s → 6 windows
```

每个窗口：

- 覆盖原视频中的连续区间；
- 与相邻窗口无缺口、无重叠；
- 在窗口内约 1/3 与 2/3 位置各取一帧；
- 保存目标位置、实际解码 timestamp、window 边界与完整 provenance。

窗口只是最小可理解 Evidence，不提前决定 Moment、Chapter 或 Aha。后续阶段可以把多个窗口合并为同一 Moment，也可以在 Evidence 支持时分开。

## 4. 高强度日容量

```text
20 Manual Photo × 1 Frame       = 20
10 Manual 15s Video × 4 Frames  = 40
3 Manual 60s Video × 8 Frames   = 24
3 Manual 120s Video × 12 Frames = 36

Manual total = 120 Frames
Auto total   = 450 Frames
Day total    = 570 Frames
```

570 是高强度容量基线，不是要求人工生成 570 张测试素材，也不是所有帧每次 Preview 都重新送入模型。

## 5. 默认传输与升级

- 默认云端理解输入为上述静态 Evidence；
- 默认不上传完整 Manual Video；
- 相同 Evidence、模型、Prompt 和参数版本下只执行一次 perception；
- Preview 与 Final 复用已有 Observation；
- 对明确重要但静态帧无法判断的局部窗口，可以选择性请求 temporal proxy、音频、gated ASR 或局部 HQ source；
- 升级是局部例外，不能静默替代固定 Baseline。

## 6. 事实边界

固定帧不能单独证明：

- 帧间动作顺序或持续时间；
- 未出现在代表帧中的短暂事件；
- 语音内容、声音来源或因果关系；
- 用户为什么主动拍摄。

Manual intent 可以提高后续候选关注度，但不能让模型编造情绪、关系、意图或事件意义。

## 7. FROZEN 与 OPEN

### FROZEN

- Manual Photo = 1 Window / 1 Frame；
- 15s Video = 2 Windows / 4 Frames；
- 60s Video = 4 Windows / 8 Frames；
- 120s Video = 6 Windows / 12 Frames；
- 每个视频窗口固定取约 1/3 与 2/3 两帧；
- Window 连续覆盖实际视频且不预判 Moment；
- 默认不上传完整 Manual Video；
- 原始 HQ 只在 Memory 入选后按需请求。

### OPEN / 待真实媒体实验校准

- 设备容器时长相对 15/60/120 秒的允许误差；
- Evidence 编码、尺寸、质量与上传 bytes；
- 精确解码容差与失败恢复；
- temporal proxy、audio gate 与 ASR 的升级门槛；
- 真实 Phone compute、energy、上传量与模型成本。

## 8. 当前实现状态

- `src/diary_one_ci/evidence.py` 已实现 Manual Photo 与 duration-aware Manual Video 的确定性 planning；
- `tests/test_evidence_builder.py` 已覆盖 1/4/8/12 帧数量、窗口连续覆盖、时间排序和 RawAsset provenance；
- 尚未实现真实媒体解码、Evidence 编码与上传；
- App Library 任意相册媒体兼容路径不等于 Diary One Manual capture 事实。
