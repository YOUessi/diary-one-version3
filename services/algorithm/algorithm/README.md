# Diary One Algorithm V1.75｜工程移交包

交付日期：2026-09-16  
交付对象：接手 Diary One Chapter / Aha 算法研发、验证与后端集成的程序员  
当前候选：`V1.75`  
候选收据 SHA-256：`70442cf035a4f2f1416606b13b4b70caff41b810ed9b63be6442c08a432f127f`

## 先说结论

这是一个**可运行、可测试、可继续研发**的算法工程交付包，但不是 Production 发布包。

- V1.75 运行源码已冻结；原仓库冻结时 333/333 项执行通过、0 跳过。
- 最新真实完整链证据仍来自 V1.74.1：4 Chapter / 0 Aha；Writer 与事实代表帧机制通过，Aha 质量不通过。
- V1.75 针对该次真实失败增加“Chapter 覆盖关系 + 未覆盖事实逐条审查 + 最终可共存 Aha 集合”，但尚未完成新的真实模型质量验证。
- Web 测试页、正式 App、Firmware/SDK、S13 HQ 导出、GPS 与 Production 后端均不属于本交付包的已完成范围。

接手者不得把“代码通过测试”“真实模型链返回”“内容质量通过”“Production ready”混成同一结论。

## 10 分钟接手路径

1. 阅读本文件。
2. 阅读 [01_SYSTEM_AND_WORKFLOW.md](01_SYSTEM_AND_WORKFLOW.md)，理解产品目标和实际 V1.75 链路。
3. 阅读 [02_IMPLEMENTATION_AND_INTERFACES.md](02_IMPLEMENTATION_AND_INTERFACES.md)，找到代码入口和数据合同。
4. 执行：

   ```bash
   python3 handoff_support/verify_handoff.py
   PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 \
     python3 -m unittest discover -s tests -p 'test_*.py'
   ```

5. 便携交付包因主动排除了私有真实请求/回复归档，默认结果应为 333 项发现、307 项执行通过、25 项私有回放跳过；另有 1 项本地 socket 测试可能因沙箱跳过。详情见 `evidence/portable_test_result.json`。
6. 阅读 [03_RUNBOOK.md](03_RUNBOOK.md)，再决定是否使用真实模型。任何真实运行都必须明确确认数据目的地。
7. 阅读 [04_STATUS_RISKS_AND_NEXT_STEPS.md](04_STATUS_RISKS_AND_NEXT_STEPS.md)，从“素材包 1 全新完整链”继续，不要先切 Web 或 Production。
8. 修改算法前阅读 [05_FROZEN_DECISIONS.md](05_FROZEN_DECISIONS.md)，避免把用户案例写成运行时特例。

## 包内结构

| 路径 | 用途 | 权威性 |
|---|---|---|
| `src/diary_one_ci/` | V1.75 冻结运行源码 | 当前实现权威源 |
| `contracts/` | 输入、输出、评估 JSON Schema | 接口权威源 |
| `tests/` | 333 项本地协议、回归与集成测试 | 工程行为证据，不是内容质量证据 |
| `fixtures/`, `examples/` | 确定性合同样例 | 结构验证，不能当真实图像质量样本 |
| `docs/` | 从 V1.0 到 V1.75 的完整设计与历史记录 | V1.75 文件优先，旧文件仅为历史 |
| `tools/` | 冻结、标准化、实验和历史运行工具 | 多数是研究工具，不是公共 API |
| `handoff_support/` | 本交付包专用验证与 Bundle 运行入口 | 接手起点 |
| `evidence/` | V1.75 候选收据、本地测试回执和最近真实复盘 | 版本/证据锚点 |
| `MANIFEST.sha256`, `artifact_manifest.json` | 全包文件完整性 | 移交校验依据 |

## 信任顺序

出现文档冲突时，按以下顺序处理：

1. 本交付包的 `README.md` 与 01–05 文件；
2. `evidence/codex_candidate.json` 中的源码哈希和研究档案；
3. `docs/codex_CHECKPOINT_V1_75_UNCOVERED_FACT_AUDIT.md`；
4. `docs/codex_D5_V1_75_UNCOVERED_FACT_AUDIT_DESIGN_V01.md`；
5. `docs/00_READ_FIRST.md`；
6. 其他带版本号的历史文件。

历史记录不得被静默改写。若基线、Schema、Prompt、模型路由或输出合同发生变化，创建新版本和新检查点，保留旧快照。

## 本包未包含

- 任何 API Key、Bearer Token、证书或账号凭据；
- 三位测试者的原始照片、视频或标准化帧；
- 含真实素材事实全文的私有模型请求/回复日志；
- Web 工程、正式 App 工程、Firmware/SDK；
- 云部署资源、域名、数据库、对象存储或 S13 HQ 文件。

## 移交验收

接手者完成以下项目才算工程接收成功：

- 完整性校验通过；
- 测试无失败，且跳过项只属于已声明的私有归档缺失或本地 socket 环境限制；
- 能解释 V1.75 与 V1.74.1 的唯一行为差异；
- 能指出 S07、S09、S10、S11 各自职责；
- 知道真实模型验证尚未完成，不能直接切 Web；
- 知道未覆盖事实“必须审查但不强制入选”；
- 知道 Chapter 内事实仍可在故事职责不同且关系为 `DISTINCT_STORY` 时成为 Aha；
- 知道禁止自动补位、重复 API 重写、场景专用规则和虚构反例 gate。
