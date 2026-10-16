# Diary One Canonical Checkpoint V1.1 — Rolling Daily Memory

**状态：** `FROZEN`
**冻结日期：** 2026-08-25
**决策来源：** 用户显式重开并确认
**作用范围：** DailyMemoryRun 触发、白天增量产出、Chapter/Aha 全天数量、增量成本纪律
**继承关系：** 仅覆盖本文明确列出的 V1.0 规则；其余定义继续继承 `CANONICAL_PROCESSING_RULES_V1_0.md`

## 1. 本次覆盖的旧规则

本检查点正式覆盖：

1. `CHAPTER_DAY` 的 Chapter 硬上限从 4 调整为 5；
2. 丰富日的主目标保持 3–4 Chapter，第 5 个只作为高强度日例外；
3. 白天不再依赖 12:00、17:00、20:00 等固定钟点触发；
4. 同一 User Local Day 允许多个 Preview Revision，用户体验采用稳定累加与受控合并；
5. 昂贵的素材理解必须增量缓存，不得因 Preview Revision 重复处理旧 Evidence。

## 2. Daily Output 数量合同

```text
CHAPTER_DAY
→ 1–5 Chapters
→ + 0–3 Aha

HIGHLIGHT_DAY
→ 0 Chapter
→ exactly 1 strong Aha

EMPTY_DAY
→ 0 Chapter
→ 0 Aha
```

对于有足够强内容的高强度日：

```text
主要目标：3–4 Chapter + 2–3 Aha
例外上限：5 Chapter
```

3–4 是目标区间，不是配额；真实内容不足时允许更少。第 5 个 Chapter 只有同时满足以下条件才可进入最终集合：

1. 自身达到与前 4 个相同的 Truth、coherence 和 memory-value 门槛；
2. 是独立完整 Episode，与已选 Chapter 不重复；
3. 不能合理并入已有 Chapter；
4. 删除它会遗漏当天一段重要生活；
5. 它不是 Aha 尺度的短暂局部瞬间。

Aha 继续保持 0–3。Aha 被扩展或升级为 Chapter 后，不得以相同 Memory 同时占用一个 Aha 名额。

## 3. 滚动素材触发

触发依据是自上次成功 Editorial Revision 以后新增的有效佩戴覆盖，不是上传时间，也不是把 9 秒视频时长相加。

在 120 秒 Auto capture interval 的规划基线下：

```text
约 1.5 小时有效覆盖 ≈ 45 个连续有效 Auto Asset
约 2 小时有效覆盖   ≈ 60 个连续有效 Auto Asset
```

45/60 只是无漏拍情况下的容量换算。真实判断必须考虑 capture gap、暂停、重复、无效素材和可信时间轴。

### 3.1 每次导入都执行

- RawAsset Intake、去重与可信时间排序；
- 对新增素材生成或规划 Evidence；
- 计算便宜的质量、重复、运动、场景变化与 Manual intent 信号；
- 按素材、算法版本和参数缓存结果。

这一步不要求生成 Chapter/Aha，也不重复处理旧素材。

### 3.2 Preview eligibility

- 新增有效覆盖达到约 1.5 小时后，进入可尝试 Editorial Preview 的状态；
- 新增有效覆盖达到约 2 小时后，默认触发一次 Preview selection attempt；
- 强 Manual cluster、明显语义变化或用户主动“生成今天”可以绕过时长门槛；
- 触发算法不等于必须新增 Memory；没有合格内容时允许 `NO_CHANGE`。

### 3.3 Finalization

- 用户明确结束当天、当天最后一次导入或日终 Finalization 时，无条件进行 Final；
- 一天只导入一次时，直接对完整输入执行一次 Final；
- 错过中间阈值时不补跑多个历史任务，下一次导入只生成一个截至当前的累计 Revision；
- late data 创建新的 Day Revision，不静默修改正在 Finalize 的 immutable snapshot。

固定钟点可以作为后台调度提示，但不再是产品语义或 Chapter/Aha 生成条件。

## 4. Revision 与受控累加

```text
OPEN_DAY
→ PREVIEW_REVISION_1 .. N
→ FINAL_REVISION
```

每个 Revision 都冻结自己的输入快照并可复现。新 Revision 对用户表现为“今天的日记继续生长”，但算法仍基于截至当前的全天累计 Evidence 做集合级判断。

| 新 Evidence 与已有 Memory 的关系 | 动作 |
|---|---|
| 同一 Episode 的延续 | 更新并丰富原 Chapter，保持 stable ID |
| 新的独立强 Episode | 累加新 Chapter |
| 已有 Episode 内的独立局部高光 | 新增 Aha 或精选素材 |
| 重复或错误切碎 | 受控合并，不重复计数 |
| 内容弱或 Evidence 不足 | 不新增 |

已有用户可见 Memory 不因简单排名下降而删除。只有重复、事实错误、错误分段或证据失效才允许合并、撤回或降级。质量优先于表面稳定，但所有变化必须可追溯。

## 5. 成本不变量

1. 每个 Evidence 的昂贵 perception 在相同素材、模型、Prompt、参数版本下最多执行一次；
2. 旧 Evidence 不因新 Revision 重新上传或重新进入多模态理解；
3. Moment、Candidate 和 Set Selection 优先使用缓存的结构化 Observation；
4. 未变化 Chapter 的 enrichment、Narrative 和 MediaDecision 应复用；
5. 强模型只验证新增、变化或仍不确定的局部候选；
6. HQ source request 与最终媒体渲染只面向真正入选的 Memory。

对于 5 小时高强度参考日，规划目标是约两次 Preview attempt 加一次 Final，而不是多次完整重跑全天视觉理解。

## 6. 状态边界

### FROZEN

- User Local Day 仍是 DailyMemoryRun 的组织单位；
- 1.5 小时 eligibility、2 小时默认 Preview attempt；
- Manual / semantic delta / user action 可以提前触发；
- 白天为稳定累加与受控合并；
- 丰富日目标 3–4 Chapter，第 5 个为严格例外；
- Aha 上限 3；
- asset perception 只增量执行一次；
- 触发不保证产出。

### OPEN / 待真实数据校准

- 有效 coverage 对 capture gap 的精确计算；
- strong Manual cluster 和 semantic delta 的阈值；
- 用户主动结束当天与自动 Finalization 的 UI/时间策略；
- Preview 稳定性、合并提示和用户已看内容的呈现方式；
- 真实模型、上传、能耗与渲染成本。

## 7. 当前实现 GAP

- X01 V01 仍是最多 4 Chapter 的隔离实验合同，不实现本检查点；
- 当前仓库尚无完整 DailyMemoryRun、Preview Revision 或滚动触发实现；
- 现有 Evidence planning 还没有完成真实媒体抽取、端侧成本和传输测量；
- V1.1 的 Production schema、状态机和持久化合同必须在对应阶段单独设计和验证。
