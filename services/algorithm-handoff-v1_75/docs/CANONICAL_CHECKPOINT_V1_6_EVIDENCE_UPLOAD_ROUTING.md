# Diary One Canonical Checkpoint V1.6 — Evidence Upload Routing

**状态：** `FROZEN`
**冻结日期：** 2026-08-25
**决策来源：** 用户显式确认
**作用范围：** Auto 三帧的 Phone→Cloud 上传路由，以及相似 Manual 对 Memory 候选的抑制
**继承关系：** 继承 V1.5–V1.1 与 V1.0 未被覆盖的规则

> **当前部分覆盖：** V1.8 保留本文 Phone 三帧抽取和 Cloud 1-or-3 路由，但取消 Cloud 补帧请求。`UPLOAD_1` 单帧不足时直接退出 Memory 候选。

> **当前 S06 覆盖：** V1.16 将 `MEMORY_SUPPRESSED_DUPLICATE` 明确为 `CONTEXT_ONLY` 或 `DROP_FROM_MEMORY_OUTPUT` 的 reason，而不是第四主角色；S06 处理同 Moment 明显重复，S07/S09 处理更广的候选与集合冗余，S10 决定最终媒体代表。

## 1. 本次覆盖

本检查点部分覆盖 V1.3：

- 保留“每条 Auto 9 秒视频固定抽取 1.5 / 4.5 / 7.5 秒三帧”；
- 覆盖“三帧全部作为默认云端输入”和“V1 不自适应减少上传帧数”；
- 云端正常上传合同改为保守的 `1-or-3`。

同时明确：Manual intent 不再使相似 Manual 自动免于 Memory 候选抑制。

## 2. Auto：抽取合同与上传合同分离

```text
Phone extraction contract
→ fixed 3 frames at 1.5 / 4.5 / 7.5s

Phone similarity / quality gate
→ conservative decision

Cloud upload contract
→ 1 frame OR all 3 frames
```

固定三帧保证手机侧始终拥有可比较的时间证据；上传路由只决定云端本次需要看到多少帧，不修改 RawAsset 或 Evidence provenance。

## 3. 保守 1-or-3 路由

### `UPLOAD_1`

只有同时满足以下条件才允许只上传一帧：

1. 三个目标位置均成功解码；
2. 三帧均通过最低完整性检查；
3. 三帧两两都达到“高度相似”的保守阈值；
4. 没有明显场景切换、局部变化或 motion/contradiction hint；
5. similarity 与 quality 计算完整且版本可信；
6. 路由没有任何不确定状态。

代表帧从三帧中选择 visual reliability 最高的一张；同等条件下优先 4.5 秒中间帧。

### `UPLOAD_3`

出现以下任一情况时上传全部三帧：

- 任意一对没有达到高度相似阈值；
- 任意帧显示明显变化、运动或场景差异；
- quality / similarity 信号缺失或冲突；
- 路由不确定；
- 后续实验发现某类素材的一帧路由存在不可接受的内容漏失。

V1 正常路由不增加 `UPLOAD_2`，避免更复杂的聚类、排序和失败分支。抽帧失败属于异常路径，必须报告实际可用帧数和失败原因，不能伪装成正常 `UPLOAD_1`。

## 4. Phone 与 Cloud provenance

无论上传一帧还是三帧，传输清单必须记录：

- `extracted_frame_count = 3`；
- `uploaded_frame_count = 1 | 3`；
- 三个 frame ID、offset、hash 与 quality status；
- pairwise similarity 或等价的路由证据；
- selected representative frame ID；
- routing decision / reason；
- similarity algorithm、version、parameter 与 compute provenance。

未上传帧不进入本次 Cloud Observation。按 V1.8，Cloud 不再请求另外两帧；单帧证据不足时记录 `INSUFFICIENT_EVIDENCE` 并退出 Memory 候选，不上传完整 9 秒视频。

## 5. 成本模型

高强度日 Auto 基线为 150 条、固定抽取 450 帧。若有比例 `p` 的 Auto 通过 `UPLOAD_1`：

```text
Auto uploaded frames = 450 - 300p
Day baseline uploaded frames = 570 - 300p
```

示例：

| `UPLOAD_1` Auto 比例 | Auto 上传帧 | 含 Manual 的全日帧 | 相比 570 减少 |
|---:|---:|---:|---:|
| 30% | 360 | 480 | 约 16% |
| 50% | 300 | 420 | 约 26% |
| 70% | 240 | 360 | 约 37% |

这些是正常首轮 Evidence 的容量推导，不是全天所有网络或推理成本。实际费用还取决于图片尺寸、视觉 Token 计价、请求打包、重试、后续选择性 enrichment 和文本开销。

手机仍需解码三帧；相似度判断应优先采用小尺寸灰度图、perceptual hash、SSIM 或等价的轻量计算，不默认部署复杂生成式或视觉语言模型。Phone latency、energy 与内存收益必须实测。

## 6. Manual 相似素材的 Memory 抑制

相似 Manual 可以从 Chapter/Aha 候选和最终精选素材中被抑制，原因是 App 已有独立 Manual 素材窗口。

规则：

1. 所有 Manual RawAsset 继续保留在事实账本与独立 Manual 窗口；
2. 同一局部 Episode 内的相似 Manual 建立 duplicate group；
3. Memory pipeline 优先保留质量、代表性与 Evidence confidence 最好的成员；
4. 其余成员根据是否仍有独特上下文用途，标记为 `CONTEXT_ONLY` 或 `DROP_FROM_MEMORY_OUTPUT`，并附加 `MEMORY_SUPPRESSED_DUPLICATE` reason；
5. 被抑制素材不得增加 Chapter/Aha 数量，也不得重复占用精选媒体位；
6. Manual intent 是候选信号，不是免除重复抑制的特权；
7. 跨较长时间、不同 Session 或不同生活 Episode 的视觉相似素材，不能仅凭外观自动视为重复。

完全重复导入仍由 S01 幂等处理；本节处理的是不同 RawAsset 之间的近重复 Memory 表达。

## 7. 阶段边界

- S02 固定抽取三帧；
- S03A 在 Phone 计算 route 所需的 quality、三帧 similarity 与 within-window change，并产生 `UPLOAD_1` / `UPLOAD_3` route hint；
- 上传层执行路由并保留传输 provenance；
- S04 基于实际上传 Evidence 生成 Observation；
- S06/S07 及以后决定 Manual duplicate group 的 context、candidate 与最终抑制；
- S03 不删除 RawAsset，也不直接决定 Chapter/Aha。

## 8. FROZEN 与 OPEN

### FROZEN

- Auto 手机侧固定抽取三帧；
- Auto 云端正常上传只允许保守的 1-or-3；
- 只有三帧两两高度相似且无不确定时才 `UPLOAD_1`；
- 其他正常情况全部 `UPLOAD_3`；
- 未上传帧不进入 Cloud；单帧不足时退出 Memory 候选，不补帧或上传完整 Raw；
- Manual 相似素材可从 Memory 候选与精选中抑制；
- Manual RawAsset 和独立 Manual 窗口不受该抑制影响。

### OPEN / 待真实 Benchmark 校准

- similarity 算法与高度相似阈值；
- representative quality 公式；
- Phone compute / energy / latency；
- 实际上传 bytes 与视觉 Token 节省；
- `UPLOAD_1` 对重要事件、Aha 和 Moment boundary 的漏失率；
- 未上传帧与原始 Raw 的 Phone cache 有效期；
- Manual duplicate group 的具体时间邻域和相似阈值。

## 9. 当前实现 GAP

- 当前 Evidence planning 只实现固定三帧抽取计划，没有 Phone similarity 或 1-or-3 routing；
- 尚未实现 route manifest、无感上传队列、`INSUFFICIENT_EVIDENCE` candidate gate 或相应 Trace；
- 尚未实现 Manual `MEMORY_SUPPRESSED_DUPLICATE` reason、三角色分配与候选层去重；
- 所有成本与质量收益仍需真实 wearable 素材和真机 Benchmark 验证。
