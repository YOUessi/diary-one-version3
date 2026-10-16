# codex D5｜V1.75 Chapter 覆盖审查与最终 Aha 集合设计 v0.1

日期：2026-09-15。状态：**已实现并完成本地回归；尚未进行新的真实模型验证。**

本设计只回应 [V1.74.1 素材包 1 真实复盘](codex_V1_74_1_PACK_1_REAL_REVIEW.md) 已经证明的问题：S09 虽然收到了全部 35 条事实，但没有可靠识别“哪些事实尚未被 Chapter 使用”，因此漏过一个完整、正在发生、可单独回看的现场，并先选出三项随后又被自身关系判断否决的 Aha。

它不修改 Chapter 聚类、S04 视觉识别、S10 媒体精选、Writer、Web/App 或模型层级；不增加场景词特例、API 重试、抽卡或确定性自动补位。

## 1. 在全链路中的位置

```text
S04 视觉事实与事实代表帧（不变）
  ↓
S07 Chapter 组织与选择（不变）
  ↓
S09 一次纯文字 Plus
  ├─ 读取全部可用事实
  ├─ 读取每条事实的 Chapter membership
  ├─ 逐条审查未被 Chapter 覆盖的事实
  ├─ 比较最多 8 个 finalists
  ├─ 输出已经能够共存的最终 0–3 个 Aha
  └─ 输出完整 Chapter/Aha 与 Aha/Aha 关系
  ↓
S10–S12（不变）
```

新增审查仍在原有一次 S09 调用内完成，因此正常调用次数不增加。

## 2. Chapter membership 的含义

每条进入 S09 的事实新增两个请求内字段：

- `chapter_membership`：该事实被哪些已选 Chapter 使用；使用请求内短编号，例如 `C01`。
- `coverage_status`：`INSIDE_SELECTED_CHAPTER` 或 `OUTSIDE_SELECTED_CHAPTERS`。

membership 只回答“是否已经被 Chapter 使用”，不回答“是否精彩”。

- Chapter 外事实不自动成为 Aha；它只获得一次不可省略的价值审查。
- Chapter 内事实不自动失去 Aha 资格；如果它有不同于 Chapter 主故事的独立回忆职责，且逐对关系为 `DISTINCT_STORY`，仍可入选。

例子：一个 Chapter 的主线是整段出游，一项发生在其中但具有独立体验核心的短暂互动，仍可能成为 Aha；反之，一块不在 Chapter 内的普通标识牌不会因为“未覆盖”而自动入选。这里描述的是通用结构，不是运行时场景规则。

## 3. 未覆盖事实逐条审查

输入新增 `coverage_audit.uncovered_fact_ids`。模型必须按照该列表顺序，对每条事实恰好返回一次：

```json
{
  "fact_id": "F026",
  "intrinsic_value": "WORTH_REVISITING | WEAK | UNRESOLVED",
  "revisit_hook": "由完整事实支持的可回看体验核心",
  "reason": "简短编辑判断"
}
```

`revisit_hook` 必须来自完整事实，指向具体动作、互动、变化、状态、构图或发现。名称、对象、裁切、文字或地点标签本身不能单独充当体验价值证明。

这一步的目的不是增加 Aha 数量，而是消除“模型看见了事实却无声略过”的盲区。程序只检查是否完整、引用是否合法以及字段是否有效，不根据动词、对象数量、稀有度或具体场景自动评分。

## 4. finalists 与最终集合

模型随后从完整事实池列出最多 8 个 finalists。每项同样必须说明 `intrinsic_value`、`revisit_hook` 和理由。最终 `selected_ahas`：

- 只能来自 `WORTH_REVISITING` finalist；
- 若属于未覆盖事实，其逐条审查也必须为 `WORTH_REVISITING`；
- 最多 3 个，有充分内容时主动寻找 2–3 个，但不设最低数量；
- 每个 Aha 锁定一条事实和一张 S04 代表帧；
- 必须是已经完成冲突处理的最终可共存集合，而不是等程序删除的临时列表。

## 5. 完整关系合同

若有 `c` 个 Chapter、`a` 个最终 Aha，模型必须返回：

- `c × a` 条 Chapter/Aha 关系；
- `a × (a - 1) / 2` 条无序 Aha/Aha 关系。

任何选中 Aha 只要与一个 Chapter 或更早 Aha 为 `SAME_STORY` 或 `UNRESOLVED`，都不应出现在最终集合。程序继续 fail closed：缺失、重复、越界或未确定的关系不会被猜成 `DISTINCT_STORY`，也不会从落选事实自动补位。

## 6. 明确不做的事

- 不把未覆盖当成精彩度分数。
- 不强迫每条未覆盖事实进入 finalists 或最终 Aha。
- 不把 Chapter 内素材一刀切排除出 Aha。
- 不增加小狗、古镇、摊位、石板路等场景专用规则。
- 不构造虚拟识别错误来增加运行时 gate。
- 不增加第二次 S09、Writer 重写或其他 API 抽卡。
- 不修改 S04、S07、S10、S11、S12、Web/App、S13、GPS 或增量上传。

## 7. 验证边界

本地协议测试只能证明：字段完整性、短编号映射、未覆盖审查、Chapter 内 Aha 保留、缺失审查 fail closed、完整关系执行和既有回归没有断裂。它不证明模型会在真实内容中选中更好的 Aha。

下一步必须冻结独立候选，并从素材包 1 的原始视频重新标准化、重新执行完整 S04–S12。不能只重放或单独修补 S09。真实结果需分别检查：未覆盖事实是否全部被审查、最终集合是否仍自相矛盾、Aha 是否具有独立回看价值、Chapter 是否保持原有质量、Token/时间/费用是否发生显著变化。
