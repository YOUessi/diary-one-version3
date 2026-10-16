# 03｜安装、验证与运行手册

## 1. 环境

最低要求：

- Python 3.9+；
- 本地协议/回归测试不需要第三方 Python 包；
- 原视频标准化需要 Node.js、Playwright/Chromium 和相应媒体能力；
- 真实模型调用需要阿里云百炼 API Key；
- 原视频解码/诊断路径可能需要 `ffmpeg` / `ffprobe`。

本包不携带凭据，也不自动联网安装依赖。

## 2. 完整性校验

在交付包根目录执行：

```bash
python3 handoff_support/verify_handoff.py
```

它会校验：

- 全包清单；
- V1.75 candidate receipt；
- 55 个冻结运行时文件；
- 研究版本和策略版本；
- 不存在被打包的常见密钥文件。

## 3. 本地回归

```bash
PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_*.py'
```

原仓库冻结时基线：333/333 项执行通过、0 跳过、0 失败。便携包不包含私有三包请求/回复归档，所以 25 项只用于历史真实回放的测试会主动跳过；本地 socket 被沙箱禁止时另有 1 项跳过。当前便携包实测为 333 项发现、307 项执行通过、26 项跳过、0 失败。精确状态见 `evidence/portable_test_result.json`。若接手机器出现其他跳过或失败，必须先查明原因，不得直接删除测试。

可单独跑 V1.75 协议测试：

```bash
PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest tests.test_codex_experience_editor -v
```

## 4. 对已标准化 Bundle 做本地验证

默认命令不调用 API：

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
  python3 handoff_support/run_v1_75_bundle.py /path/to/codex_manifest.json
```

它只校验 Bundle 可被读取，并打印 V1.75 profile，不发送图片或文字。

## 5. 真实模型运行

先明确确认：Evidence 帧和派生事实文字会发往 `https://dashscope.aliyuncs.com` 的北京接口。然后设置凭据：

- macOS Keychain：service `DiaryOne DashScope API Key`，account 为当前 macOS 用户；或
- CI/非 macOS：环境变量 `DASHSCOPE_API_KEY`。

执行：

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
  python3 handoff_support/run_v1_75_bundle.py \
  /path/to/codex_manifest.json \
  --live \
  --confirm-dashscope-beijing \
  --output /secure/path/v1_75_run.json
```

安全约束：

- 没有同时提供两个显式 flag 时不会发请求；
- 输出文件必须不存在，避免覆盖旧证据；
- 每次使用新输出路径；
- 输出包含派生事实、审计与模型指标，应视作内部敏感数据；
- 不要把 API Key、原始素材或运行结果提交到公开仓库。

## 6. 从原视频开始的完整研究验证

本包包含历史标准化与运行工具供审计，但它们依赖原仓库的私有素材清单和归档 normalizer snapshot，不能被当作通用产品入口。

在原授权环境继续 V1.75 时，正确顺序是：

1. 固定 V1.75 candidate receipt；
2. 从素材包 1 原视频重新解码和抽帧；
3. 核对原文件 SHA、帧文件 SHA、资产数和帧数；
4. 完整执行 S04–S12；
5. 逐阶段记录模型、调用、Token、费用和时间；
6. 逐 Chapter/Aha 对照原素材进行人工评价；
7. 先复盘，再决定是否跑素材包 2/3；
8. 不只重放 S09，不在同一候选下根据结果改 Prompt 后继续冒充同版。

## 7. 新版本开发纪律

任何行为修改都应：

1. 写清真实问题证据；
2. 判断是共性结构问题还是单个案例；
3. 新建策略版本，不覆盖冻结收据；
4. 使用中性协议 fixture 验证结构，不把 fixture 当内容质量证据；
5. 跑全量回归；
6. 冻结不可覆盖的 candidate runtime 与哈希；
7. 使用真实素材从标准化开始跑完整链；
8. 分开报告实现、测试、真实质量、Web 接入和 Production 状态。

## 8. 常见诊断路径

- 没有 Chapter/Aha：先看 `decision_trace`，区分没有候选、关系关闭、Writer 阻断和 pipeline failure。
- Aha 为 0：检查 S09 `uncovered_fact_reviews`、finalists、selected set 和完整关系矩阵，不要先降低重复 gate。
- Chapter 混合：检查 S07 thesis、beat facts 和成员贡献，不要加“古镇/石板路”等词表规则。
- Writer 为空：检查短编号 round trip、claim IDs、长度与 `media_only_chapters`，不要发第二次 API 抽卡。
- 视频抽帧卡住：检查标准化器进度、浏览器/loopback 权限和单文件状态；不要把失败伪装成空素材。
- Web 结果与本地算法不同：先核对 Web 实际加载的 policy/version；当前 Web 不能默认视为 V1.75。
