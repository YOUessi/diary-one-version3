# 01｜系统目标与全链路 Workflow

## 1. 产品目标

Diary One 把用户佩戴第一人称摄像头耳机时产生的大量零散素材，整理为一天中值得回看的少量记忆卡片：

- 常规目标：全天 3–4 个 Chapter；内容特别丰富时可出现第 5 个，但不是硬配额。
- 每个 Chapter：3–5 个精选素材，表达一个清楚的经历或故事主线。
- Aha：0–3 个；有充分真实内容时主动寻找 2–3 个，素材稀少也应认真寻找生活中的小精彩，但不能为了数量强行生成。
- Chapter 文案：中文测试阶段 1–2 句话，有画面和克制氛围，不机械列举所有对象。
- Aha 文案：20 个可见字符为目标，24 个为硬上限；超过目标少量可以接受，超过硬上限不发布。
- 检索事实放在 canonical tags / facts；故事文案不承担罗列全部识别结果的职责。

高强度设计基线是：约 5 小时佩戴、每 2 分钟自动采集 9 秒视频，共约 150 个 Auto Video；用户另主动采集约 20 张照片、10 个 15 秒视频、3 个 1 分钟视频、3 个 2 分钟视频。这个规模是容量目标，不代表 V1.75 已完成 186 素材真实压力验证。

## 2. 两套输入合同必须区分

### 正式产品方向

- Auto 9 秒视频：手机侧固定抽 1.5 / 4.5 / 7.5 秒三帧。
- 云端采用保守的 1-or-3 上传合同；若一帧不足以判断，当前原则是排除该候选，不回拉另外两帧。
- Manual 素材可在 Chapter/Aha 候选中被相似度抑制，但仍保留在独立 Manual 窗口和事实账本。
- Sync 后的后续上传应无感，不增加二次用户交互。

### 当前 Web / 手机素材研究输入

- 接受用户导入的普通照片和视频，整批默认视为同一天。
- 当前测试素材可能没有可靠 GPS、拍摄时间和设备真实采集节奏。
- 只可使用导入顺序，不可把顺序伪装成真实时间。
- 视频根据时长生成测试 Evidence Windows；这不替代正式 Auto 9 秒三帧合同。

## 3. 产品概念全链 S00–S13

| 阶段 | 目标 | 主要输出 | V1.75 研究链状态 |
|---|---|---|---|
| S00 | 导入、触发、修订协调 | Day/Revision 上下文 | 仅合同/研究形态 |
| S01 | RawAsset 接入、去重、隔离坏文件 | 可信素材清单 | Bundle 层实现 |
| S02 | 生成 Evidence Windows | 帧与证据窗口 | Web/标准化器研究实现 |
| S03 | 低成本信号 | 质量、运动、相似度等 | 部分合同/历史实现 |
| S04 | 视觉事实理解 | Observation、事实、支持度、代表帧 | V1.75 实际执行 |
| S05 | 连续 Moment 切分 | 连续、无重叠 Moment | 研究链内部实现 |
| S06 | Observation 角色 | KEEP / CONTEXT_ONLY / DROP | 研究链内部实现 |
| S07 | Chapter 结构编辑 | Chapter 候选与最终 Chapter | V1.75 实际 Plus 调用；只负责 Chapter |
| S08 | 有界定向补证 | 经验证的补充证据 | 当前 V1.75 不新增调用 |
| S09 | 全日编辑与 Aha 选择 | 最终 Chapter/Aha 关系和 Aha 集合 | V1.75 核心修改；一次 Plus 文本调用 |
| S10 | 媒体精选 | Chapter 3–5 件、Hero；Aha 单帧 | 实际执行；按需视觉调用 |
| S11 | Grounded Writer | 标题、正文、claim 引用 | 一次 Plus；短编号 |
| S12 | 最终校验与状态 | 可见卡片、阻断项、审计 | 实际执行 |
| S13 | HQ 素材化与发布 | HQ、存储、原子发布 | **未执行** |

## 4. V1.75 实际可执行链

```text
已标准化 Bundle
  ↓
S04 分批视觉理解
  - 每个可用事实保留 evidence_frame_ids
  - 每个事实由看过图片的模型指定 representative_frame_id
  - 非关键字段错误降级，不轻易删除整个 observation
  ↓
Moment / role / candidate preparation
  - 连续结构和 KEEP/CONTEXT_ONLY/DROP
  - 技术候选只保证可执行，不代替内容价值判断
  ↓
S07 Chapter-only（Plus，一次）
  - 组织具体经历
  - 推荐 Chapter
  - 不再提前压缩或选择 Aha
  ↓
S09 Aha Experience Editor（Plus，一次，纯文字）
  - 读取全部可用事实
  - 每条事实带 chapter_membership
  - 每条 Chapter 外事实必须逐条 review
  - 比较最多 8 个 finalists
  - 输出最终可共存的 0–3 个 Aha
  - 返回完整 Chapter/Aha 与 Aha/Aha 关系
  ↓
S10
  - Chapter 视觉精选 3–5 件
  - Aha 使用其唯一事实的 S04 代表帧
  ↓
S11 Writer（Plus，一次）
  - 请求内 C01/A01/F001/O001 短编号
  - 只使用批准事实
  - 不反复调用 API 重写
  ↓
S12
  - 校验文案、引用、媒体和关系
  - 发布完整卡片；保留内部 media-only Chapter；关闭无效 Aha
```

## 5. V1.75 的核心 S09 规则

1. `chapter_membership` 只描述事实是否已被某个 Chapter 使用，不是精彩度分数。
2. 所有 `OUTSIDE_SELECTED_CHAPTERS` 事实都必须恰好审查一次；审查不等于入选。
3. `revisit_hook` 必须来自完整事实，说明可回看的动作、互动、变化、状态、构图或发现；对象名、店名或 OCR 本身不能证明价值。
4. Aha 只能来自 `WORTH_REVISITING` finalist；未覆盖事实还必须在覆盖审查中同样被判为 `WORTH_REVISITING`。
5. Chapter 内事实仍可成为 Aha，但必须承担不同的回忆故事，且与所有 Chapter 的关系为 `DISTINCT_STORY`。
6. `selected_ahas` 是模型已经处理完冲突的最终集合，不是交给程序删除的临时列表。
7. 对 `c` 个 Chapter、`a` 个 Aha，必须返回 `c × a` 条 Chapter/Aha 关系与 `a(a-1)/2` 条 Aha/Aha 关系。
8. 缺失、重复、越界、`SAME_STORY` 或 `UNRESOLVED` 都 fail closed；程序不猜测为独立，也不自动补位。

## 6. Writer 与发布出口

- Writer 只调用一次；没有“超过字数再抽一次”的逻辑。
- 请求使用短编号，程序私下恢复真实 UUID，未知/越界引用直接拒绝。
- Chapter 文案失败：保留内部 Chapter 结构、3–5 个精选素材和事实账本，但不向当前公共结果发布坏文案；记录在 `decision_trace.media_only_chapters`。
- Aha 文案失败：不发布该 Aha，但保留候选、事实、代表帧和失败原因。
- 禁止把原始长事实、通用标题或模板套话伪装成成品。

## 7. 模型与成本

- 默认视觉/普通阶段：固定 Qwen VL Flash 快照。
- S07、S09、S11：固定 Qwen Plus 快照。
- `enable_thinking=false`；当前使用阿里云百炼北京兼容接口。
- V1.74.1 的 20 视频/74 帧完整链：15 次调用，输入/输出 144,084 / 16,596 Token，公开价快照估算约 ¥0.1068，模型链约 239 秒。
- V1.75 不增加模型调用阶段，但未覆盖事实审查会增加部分 S09 输出 Token；真实增量尚未测量。

