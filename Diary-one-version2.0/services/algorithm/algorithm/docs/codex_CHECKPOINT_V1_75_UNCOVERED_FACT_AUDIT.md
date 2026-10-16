# Diary One Algorithm V1.75｜未覆盖事实审查检查点

日期：2026-09-15。状态：**本地实现与回归通过；等待独立候选冻结和真实素材验证。**

## 1. 基线与原因

- 直接基线：V1.74.1。
- 基线候选收据 SHA-256：`a613c4de30fdca8fa4d38c8c3bf66d5fac2f45cd021b66d8eb357052009bf96a`。
- 基线真实结果 SHA-256：`43e4bdd77c01f4f1a267352b02c9ce32c25b1bd4ce83480115fd55377fbe7a89`。
- 真实证据：S09 收到 35 条事实却漏过一条未进入任何 Chapter、具备具体现场和动作的事实；所选 3 项又均被同一回复判为与 Chapter 同故事，最终 0 Aha。

这不是从虚拟反例推导出的修改，也不是针对某种物体或场景的特例。

## 2. 修改范围

运行源码只修改：

- `src/diary_one_ci/codex_experience_editor.py`
- `src/diary_one_ci/codex_d5_research.py`

测试只修改 `tests/test_codex_experience_editor.py`。设计依据见 [V1.75 设计](codex_D5_V1_75_UNCOVERED_FACT_AUDIT_DESIGN_V01.md)。

## 3. 冻结合同

- 策略：`CODEX_D5_FULL_FACT_AHA_EDITOR_V02`。
- 搜索合同：`FULL_FACT_CHAPTER_COVERAGE_AUDIT_SINGLE_RELATION_AUTHORITY_V02`。
- 研究档案：`CODEX_V1_75_UNCOVERED_FACT_AUDIT`。
- S09 输入：全部可用支持事实 + 每条事实的 Chapter membership。
- 未覆盖事实：必须逐条审查，审查不等于入选。
- finalist：最多 8 个，必须给出受事实支持的 `revisit_hook`。
- Aha：0–3 个，必须是最终可共存集合；一条事实、一张 S04 代表帧。
- 关系：选中集合的 Chapter/Aha 与 Aha/Aha 逐对关系必须完整；缺失或未确定 fail closed。
- 调用：S09 仍为一次纯文字 Plus；无重试、无抽卡、无自动补位。

## 4. 本地验证

- V1.75 协议与集成测试：11 项通过。
- 全仓回归：333 项通过，0 失败。
- 外部 API 调用：0。
- 真实图像语义断言：0；协议 fixture 只验证结构、引用和执行，不冒充真实质量证据。
- 场景词运行规则：0。

已验证的关键边界：

1. Chapter 外事实缺少审查时留下明确诊断，且不能借该缺失审查入选。
2. Chapter 外事实即使被审查，也不被程序自动选中。
3. Chapter 内事实在自身值得回看且与 Chapter 关系为 `DISTINCT_STORY` 时，仍可成为 Aha。
4. `SAME_STORY`、`UNRESOLVED` 或缺失关系继续关闭相应 Aha，不补位。
5. 既有 Chapter、代表帧、Writer 短编号和安全出口回归通过。

## 5. 结论边界

- V1.75 实现：通过。
- 本地协议与回归：通过。
- 真实模型质量：未验证。
- Web/App 生效：未执行。
- Production readiness：未证明。

## 6. 明确排除

未修改 Firmware/SDK、正式 App、Web 默认、R2、共享状态、长期记忆、S13、GPS、增量上传或公开部署；未运行素材包 2/3；未发送任何素材或事实到外部 API；未提交或推送 GitHub。

下一步是创建不可覆盖的 V1.75 候选快照，然后只对素材包 1 做一次从标准化开始的完整 S04–S12 真实运行，并在继续其他素材包前先复盘质量。
