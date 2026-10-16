# Diary One Canonical Checkpoint V1.2 — RawAsset Intake Truth Contract

**状态：** `FROZEN`
**冻结日期：** 2026-08-25
**决策来源：** 用户显式确认
**作用范围：** S01 RawAsset Intake、时间归属、多次导入、去重与异常隔离
**继承关系：** 继承 V1.1 Rolling Daily Memory 与 V1.0 未被覆盖的规则

## 1. 目的

S01 只建立一天素材的事实账本，使滚动 Preview 和最终 Diary 使用同一条可信时间轴。它不理解媒体意义，不判断重要性，也不生成 Chapter/Aha。

`RawAsset` 是不可被 AI 改写的事实对象。Observation、Moment、Chapter、Aha、Writer 或 Personalization 都不得覆盖其身份、来源、时间、时长、媒体属性和同步来源。

## 2. RawAsset 最低事实合同

每个 RawAsset 至少保存以下六组信息：

### 2.1 唯一身份

- stable `raw_asset_id`；
- 同一设备侧拍摄事实在多次同步中保持相同 ID；
- ID 不能因导入批次、算法版本或云端重试而变化。

### 2.2 拍摄来源

```text
capture_source = DIARY_ONE_AUTO | DIARY_ONE_MANUAL
media_kind = PHOTO | VIDEO
```

Manual 是用户主动记录的事实信号，但不自动等于重要、优质或必须入选。

### 2.3 时间事实

- `captured_at_utc`；
- `capture_timezone` / UTC offset；
- 拍摄时的 `local_day`；
- `capture_session_id` 或等价的连续采集来源；
- 时间来源与可信状态。

拍摄时间决定素材在生活时间轴中的顺序，拍摄时的本地日期决定 Diary 归属。`ingested_at`、`uploaded_at` 或 App 打开时间不得改写该归属。

跨时区时同时保留 UTC 与拍摄时区，不使用处理服务器时区。时间修正必须产生有 provenance 的事实修订，不能由模型静默猜测。

### 2.4 媒体事实

- Photo / Video；
- Video duration；
- 原始宽高、方向、bytes；
- codec / fps 等可用 media profile；
- content hash。

媒体事实描述原始输入，不能被后续裁切、转码或 Evidence 尺寸覆盖。

### 2.5 本地来源引用

- phone source cache 或受控研究源中的 `source_ref`；
- source reference 的有效状态；
- 原始素材是否仍可请求。

`source_ref` 是可追溯引用，不等于默认把全天 Raw 上传云端。

### 2.6 导入与设备来源

- `sync_batch_id`；
- `ingested_at_utc`；
- import sequence；
- pseudonymous device / firmware / SDK / sync provenance（在上游能够提供时记录）。

导入事实只回答“何时、从哪里进入系统”，不回答“何时发生”。

## 3. 多次导入与幂等

同一 User Local Day 可以有多次导入，但不能因此复制生活事实：

1. 已知 `raw_asset_id` 再次出现时返回 `ALREADY_KNOWN`，不新增 RawAsset；
2. 重复同步事件追加到 sync provenance，不覆盖首次拍摄事实；
3. content hash 用于发现重复传输和可能重复，不单独决定生活事件相同；
4. 不同 ID 即使 hash 相同，也必须结合 capture time、session 和 provenance 判断，不能自动吞掉用户的独立拍摄；
5. 云端重试和 at-least-once queue 必须保持幂等。

## 4. 时间可信与异常隔离

Intake 结果至少区分：

```text
ACCEPTED_NEW
ALREADY_KNOWN
QUARANTINED
```

以下情况进入 `QUARANTINED` 或明确异常状态，而不是静默猜测：

- capture time 缺失、越界或不可信；
- timezone / local day 无法可靠重建；
- media duration、kind 或格式与来源事实冲突；
- source reference 缺失、文件损坏或 hash 校验失败；
- ID 与已知事实发生不可解释冲突。

异常记录保留在审计账本中，但在解决前不参与生活时间轴、有效 coverage 或 Chapter/Aha 事实判断。

## 5. Rolling trigger 的 Intake 输出

每次导入输出一个确定性 `IngestDelta`，至少包括：

- accepted new asset IDs；
- already-known asset IDs；
- quarantined asset IDs 与原因；
- 新增有效 Auto 数量与 coverage；
- 新增 Manual 数量；
- 排序后的 RawAsset ledger fingerprint；
- sync provenance。

只有 `ACCEPTED_NEW`、时间可信且通过最低完整性检查的 Auto Asset 才能增加 V1.1 的 1.5/2 小时 coverage。Manual 是否提前触发 Preview 由后续便宜信号判断，S01 不直接判定其记忆价值。

## 6. 输出与非目标

S01 输出：

```text
Ordered RawAsset Ledger
+ IngestDelta
+ Intake Audit
```

S01 不做：

- 抽帧、裁切或转码；
- 视觉/音频理解；
- blur、duplicate similarity 或 embedding 判断；
- Moment、Chapter、Aha 或 Narrative；
- 原始素材默认上云。

这些能力分别属于 S02 及以后阶段。

## 7. 成本与验收

S01 不调用生成式或多模态模型。主要成本是 metadata 读取、hash、幂等查询与事实账本写入。

最低验收条件：

1. 相同导入重放不会增加 RawAsset 数量或 coverage；
2. 输入顺序不同，最终可信时间轴与 ledger fingerprint 相同；
3. 导入时间变化不会改变 local-day 归属；
4. 跨时区素材可由 UTC + capture timezone 重建原始本地日期；
5. 异常素材不会污染 coverage 或下游事实；
6. 所有接受、重复和隔离决定都有 reason 与 provenance。

## 8. FROZEN 与 OPEN

### FROZEN

- 拍摄时间是 Diary 归属与生活顺序的事实来源；
- 导入时间只用于同步追踪；
- UTC 与拍摄时区同时保存；
- RawAsset 跨导入保持稳定身份；
- 重复导入必须幂等；
- 异常素材保留记录但不静默猜测；
- AI 不得改写 RawAsset 事实；
- S01 为零 AI 调用。

### OPEN / 待接口与真实设备数据校准

- device clock 与 phone clock 冲突时的权威顺序；
- capture gap 如何切分 `capture_session_id`；
- 跨午夜 Manual Video 的最终 day assignment；
- 上游不能提供 stable ID 时的替代身份算法；
- media profile 与 device provenance 的 Production 必填/选填字段。

## 9. 当前实现 GAP

- `src/diary_one_ci/evidence.py` 中的 `RawAssetSpec` 只是 Evidence planning 的简化研究输入，不是 V1.2 Production RawAsset 合同；
- 当前 App Library Bundle 使用 `PHOTO_LIBRARY_TEST` 研究来源，不能伪装为 Diary One Auto/Manual capture；
- 尚未实现版本化 RawAsset Intake schema、IngestDelta、ledger fingerprint、quarantine reason 和多批次幂等测试。
