# 02｜实现地图、接口与状态

## 1. 唯一运行基线

包内 `src/` 与 `contracts/` 来自 V1.75 冻结快照，不是从当前脏工作区临时拷贝。其逐文件哈希记录在：

- `evidence/codex_candidate.json`
- `artifact_manifest.json`
- `MANIFEST.sha256`

研究入口：

```python
from diary_one_ci import codex_d5_research

gateway = codex_d5_research.make_gateway(api_key)
report = codex_d5_research.run_research(manifest_path, gateway)
```

底层实际调用：

```python
x02.run_x02_v041(
    manifest_path,
    gateway,
    recording_editor_policy=codex_experience_editor.POLICY_VERSION,
)
```

不要省略 `recording_editor_policy`；否则会落到其他历史路径，而不是 V1.75。

## 2. 当前版本标识

| 项目 | 值 |
|---|---|
| 算法候选 | `V1.75` |
| 研究档案 | `CODEX_V1_75_UNCOVERED_FACT_AUDIT` |
| Aha Editor | `CODEX_D5_FULL_FACT_AHA_EDITOR_V02` |
| Aha 搜索合同 | `FULL_FACT_CHAPTER_COVERAGE_AUDIT_SINGLE_RELATION_AUTHORITY_V02` |
| Writer 出口 | `DIARY_ONE_X02_WRITER_EXIT_V03` |
| 部署声明 | `RESEARCH_OPT_IN_ONLY` |

注意：`pyproject.toml` 的 `0.4.1`、包内 `__version__` 的历史 `0.3.0`、X02 接口 `V04.1` 与算法候选 `V1.75` 属于不同版本轴。接入和审计应以 candidate receipt、research profile 与 runtime policy 为准，不要只读取 Python 包版本来判断算法行为。这个历史版本轴尚未统一，属于后续工程清理项，不能在本次移交中静默改号。

## 3. 关键模块

| 模块 | 职责 |
|---|---|
| `bundle.py` | 读取和校验 App/Experiment Bundle；形成 evidence 输入 |
| `x02.py` | V04.1 主编排器；批次、候选、媒体、Writer、S12 审计与结果 |
| `codex_d5_research.py` | V1.75 显式研究入口、模型路由与单次 S09 接线 |
| `codex_experience_editor.py` | S07 Chapter-only、全事实 S09、coverage audit、关系矩阵和执行 |
| `codex_v174_writer.py` | Writer 请求内短编号编码/解码；文件名保留历史版本，但仍是 V1.75 使用的 Writer 适配层 |
| `codex_writer_exit.py` | 20 字目标、24 字硬门槛和安全发布出口 |
| `codex_chapter_media.py` | Chapter 3–5 个媒体的选择与 Hero 逻辑 |
| `codex_editorial_allocation.py` | Chapter/Aha 叙事职责关系 |
| `codex_structure_wire.py` | 结构模型的请求内引用与 schema 接线 |
| `codex_grounded_recording_editor.py` | 事实绑定、关系执行和共享确定性校验 |
| `x01_server.py` | 本地研究 HTTP 服务与 API Key 获取；默认 Web 路径不等于已启用 V1.75 |

`codex_d1_research.py` 到 `codex_d4_research.py`、`codex_aha_set_editor.py` 等是历史演进层和兼容依赖。不要在没有全链回归时删除；但新行为应进入新版本，不应静默修改旧检查点。

## 4. 输入接口

推荐交接输入是已经生成 Evidence 的 App Library Bundle。相关 Schema：

- `contracts/app_library_bundle_v03.schema.json`：当前 sequence-only 手机测试输入。
- `contracts/codex_app_library_bundle_v04.schema.json`：包含完整帧输入的 additive 测试合同。
- `contracts/codex_x02_staged_preview_v04_1_media_v01_input_v04.schema.json`：V04.1 媒体输入边界。

当前研究输入没有可靠时间时必须标记为 `SYNTHETIC_SEQUENCE_ONLY`；不得推断真实拍摄时刻、停留时长或连续行程。

## 5. 中间对象

### Observation / Fact

每条可用事实至少包含：

```json
{
  "fact_id": "...",
  "text": "事实描述",
  "evidence_frame_ids": ["..."],
  "representative_frame_id": "...",
  "support_grade": "STRONG | MODERATE | WEAK"
}
```

`representative_frame_id` 必须属于本事实的 `evidence_frame_ids`。非法时保留事实给 Chapter/账本，但从 Aha 路径排除，不用第一帧悄悄补上。

### Chapter

Chapter 候选必须有明确 thesis、beat/fact 引用、素材成员与来源资产。最终展示媒体 3–5 件；相似素材可以去掉一件，但不能因过度去重把原本 4 件的 Chapter 直接砍到 3 件以下后删除整个 Chapter。

### Aha

V1.75 Aha 是一个原子 Moment：一条事实、一张事实代表帧、一条受事实支持的 focus。它可以出现在某个 Chapter 的时间线内，但只有故事职责不同才可独立发布。

## 6. 输出接口

主要公共结果合同：`contracts/x02_staged_preview_v04_1.schema.json`。媒体和故事补充合同位于：

- `contracts/codex_x02_staged_preview_v04_1_media_v01.schema.json`
- `contracts/codex_x02_staged_preview_v04_1_storyline_v03.schema.json`

结果重点字段：

- `chapters`, `ahas`：当前可显示的完整卡片；
- `decision_trace`：候选、关系、媒体、Writer 与拒绝原因；
- `decision_trace.media_only_chapters`：结构/媒体通过但 Writer 文案不可发布的内部 Chapter；
- `runtime_policies`：本次真正生效的策略版本；
- `delivery_state` 与 `semantic_day_state`：必须分开判断；
- token、调用次数、时间、价格快照：按阶段保留。

## 7. 失败语义

| 情况 | 处理 |
|---|---|
| 单个事实代表帧非法 | 保留事实；只排除该事实的 Aha 资格 |
| S09 不可用 | Chapter 保留；Aha lane 明确关闭 |
| 未覆盖事实 review 缺失 | 记录诊断；该事实不能据此入选 |
| 任一必要关系缺失/未确定 | 对应 Aha fail closed |
| 两个 Aha 同故事 | 保留更早的有效项，关闭后项；不补位 |
| Writer Chapter 失败 | 内部保留 media-only Chapter；当前公共 Chapter 不发布坏文案 |
| Writer Aha 失败 | Aha 不发布；保留内部失败证据 |
| 部分 perception 失败 | 明确 `PARTIAL/UNRESOLVED`，不得伪装成 Empty Day |
| 全日确实没有内容 | 才可进入语义 Empty Day |

## 8. API 调度

`codex_d5_research.profile()` 是模型路由的可执行说明：

- S04 和常规视觉阶段走 Flash；
- `S05_S07_STRUCTURE_PROPOSAL`、`S09_AHA_EXPERIENCE_EDITOR`、`S11_WRITER_*` 走 Plus；
- S09 无图片输入，只接收事实文字和内部结构；
- Writer 一次调用；S09 一次调用；不做内容抽卡重试；
- 底层感知批次仍保留既有 413/资产局部失败隔离与总 attempt 保险丝，不等于 Writer/Aha 可以重写抽卡。
