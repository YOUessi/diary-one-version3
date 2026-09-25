# Diary One Canonical Checkpoint V1.8 — Background Evidence Upload and No Refetch

**状态：** `FROZEN`
**冻结日期：** 2026-08-26
**决策来源：** 用户显式确认
**作用范围：** Sync 后 Evidence 的无感批量上传、端云数据边界，以及 `UPLOAD_1` 证据不足时的终止路径
**继承关系：** 继承 V1.7–V1.1 与 V1.0 未被覆盖的规则

## 1. 本次覆盖

本检查点覆盖 V1.6/V1.7 中的补帧路径：

- Cloud 不再请求 `UPLOAD_1` 未上传的另外两帧；
- 不为理解一条模糊 Auto 而上传完整 9 秒视频；
- 一帧证据不足时，该 Window 标记 `INSUFFICIENT_EVIDENCE` 并退出 Chapter/Aha 候选；
- 未确认的内容允许错过，不用工程复杂度追求全天细节的完美召回。

同时冻结：用户完成一次设备→App Sync 后，后续 Evidence 上传必须由 App 自动排队和无感执行，不增加第二个上传按钮、确认步骤或素材选择流程。

## 2. 四个动作的含义

```text
Sync
→ Device RawAsset 进入 Phone App

Background Upload
→ Phone App 将已准备好的 Evidence 自动提交到 Diary One 自有后端

Cloud Storage
→ 自有后端保存 Evidence、manifest 与处理结果

Worker / Agent / Model API
→ 后端执行算法，并只把当前任务所需 Evidence 交给模型
```

App 不直接调用第三方模型 API，也不在 Phone 保存第三方模型密钥。Agent/Worker 是处理执行者，不是素材存储位置。

## 3. Sync 后的无感生命周期

每次用户完成 Sync 后，Phone 自动执行：

1. RawAsset Intake 与幂等；
2. Evidence Window planning 与抽帧；
3. 便宜的质量、变化和相似度信号；
4. Auto `UPLOAD_1 | UPLOAD_3` 路由；
5. 将待上传 Evidence 与 manifest 放入本地持久队列。

默认调度：

```text
约 1.5h 新增有效覆盖
→ eligible for silent background upload

约 2h 新增有效覆盖
→ default batch upload + Cloud processing attempt

Manual trigger / user generate / Day Final
→ may flush the queue earlier
```

一天只 Sync 一次时，Final 路径直接无感上传完整待处理 Evidence batch。断网、暂停或后台时机不足时，队列等待并自动续传；算法契约不要求用户再次操作。

具体后台执行框架、Wi-Fi/蜂窝策略、电量条件、timeout 和 retry 属于 App 工程设计，本检查点不实现也不冻结。

## 4. 默认数据边界

### Phone 默认保留

- 完整 Auto 9 秒 Raw Video；
- `UPLOAD_1` 未上传的另外两张 Frame；
- 完整 Manual 原始媒体与 HQ source；
- 本地 RawAsset / Evidence provenance 和待上传队列状态。

### Diary One 自有后端接收

- Auto 路由后的 1 或 3 张 Evidence Frame；
- Manual 的规范化 Evidence Frame；
- Evidence / route manifest；
- 当前任务必要的时间、来源、SignalPack 与版本信息；
- Observation 及以后阶段的结构化结果与 Trace。

### 模型 API 仅接收

- 当前 batch 真正需要理解的 Evidence；
- Window ID 与最小必要事实；
- 必要的质量、变化和不确定性提示。

默认不向模型或自有 Cloud 上传完整 Auto 9 秒 Raw Video，也不默认上传完整 Manual Raw Video。Memory 入选后为最终 PHOTO / LIVE_2S / VIDEO_5S 请求局部 HQ source，继续继承 S10/S13 的选择性路径，并且不产生新的用户上传交互。

## 5. `UPLOAD_1` 证据不足的终止路径

```text
UPLOAD_1
→ Cloud Observation attempt

evidence sufficient
→ normal Observation

evidence insufficient
→ observation_status = INSUFFICIENT_EVIDENCE
→ memory_candidate_eligible = false
→ no frame refetch
→ no Raw Video upload
```

该 Window：

- 继续保留在 RawAsset 事实账本、时间线和内部 Audit；
- 可以提供时间、质量或边界 context；
- 不得贡献未经确认的 visible facts；
- 不得成为 Chapter/Aha 候选或精选媒体；
- 不阻止前后其他 Window 形成 Moment、Chapter 或 Aha。

同样地，`UPLOAD_3` 仍不足以支持事实时，也必须安全退出候选，而不是编造或继续升级完整 Raw。

## 6. 成本口径

高强度参考日中，若比例 `p` 的 150 条 Auto 进入 `UPLOAD_1`，正常首轮 Evidence 上传容量为：

```text
Auto baseline uploaded frames = 450 - 300p
Day baseline uploaded frames  = 570 - 300p
```

由于取消 Auto 补帧，公式不再增加 `UPLOAD_1` refetch。真实总成本仍需另计：

- extraction failure 与无效 Evidence；
- request retry waste；
- 后续选择性音频、temporal 或 HQ enrichment；
- 最终入选媒体的 source request 与 rendering。

因此 `570 - 300p` 是正常首轮 Evidence 容量，不是全天所有网络和推理成本。

## 7. Manual 非标准时长保持 OPEN

已确认的 Diary One Manual 模式继续是：

```text
15s  → 2 Window / 4 Frame
60s  → 4 Window / 8 Frame
120s → 6 Window / 12 Frame
```

16 秒、73 秒等非标准实际时长如何选择 Window/Frame 暂不冻结。当前 duration-based fallback 不能被当作产品规则；需要在确认设备是否会产生任意时长 Manual Video 后单独决定。

## 8. FROZEN 与 OPEN

### FROZEN

- 用户只执行一次 Sync；其后的 Evidence 上传无感自动进行；
- 每次 Sync 后先在 Phone 增量准备并进入持久上传队列；
- 约 1.5h 可开始无感上传，约 2h 默认批量上传并尝试 Cloud processing；
- Manual / user generate / Day Final 可以提前 flush；
- App 只向 Diary One 自有后端提交，不直接调用第三方模型；
- Cloud/模型默认只接收路由后的 Evidence，不接收完整 Raw；
- `UPLOAD_1` 证据不足直接退出 Memory 候选；
- 不补传另外两帧，不因此上传完整 9 秒视频；
- 无法确认的 Window 仍保留事实与审计记录。

### OPEN / 后续阶段

- 后台网络、电量和调度的 App 实现；
- Evidence 与 Raw 的具体本地/云端缓存期限；
- Cloud storage lifecycle 与失败恢复；
- batch byte/token 上限和并发；
- Manual 非标准时长规则；
- 入选媒体的局部 HQ source 请求接口。

## 9. 当前实现 GAP

- 当前仓库没有 Background Upload Queue、backend ingestion 或 async worker 实现；
- 尚未实现 `INSUFFICIENT_EVIDENCE` Observation 状态和 candidate gate；
- 尚未实现 Phone→own-backend→model 的分层 Trace；
- App/Firmware/SDK 未在本检查点中修改；
- 真实网络 bytes、后台成功率、Phone energy 和 Cloud cost 尚未 Benchmark。
