# Diary One｜AI Algorithm & Real-media Test Lab

这是 Diary One 当前算法和 Web 实素材测试台的**工程交接分支**。它用于团队接收、复现和继续研发，不是 Production 发布包。

## 当前结论

| 模块 | 版本/状态 | 可声称范围 |
|---|---|---|
| Algorithm | Codex V1.75 | 冻结快照完整；333 项发现，307 通过、26 声明性跳过、0 失败 |
| Web Test Lab | V1.63 | 源码快照完整；build/lint 通过 |
| Web → V1.75 | **未完成** | Web 仍不能作为 V1.75 真实质量证据 |
| V1.75 真实运行 | Pack 1：4 Chapter / 0 Aha；Pack 2：4 Chapter / 1 Aha；Pack 3：待完成 | 两轮已返回，但尚未完成人工质量验收 |
| Production | **NO** | S13、异步任务、正式存储、账号权限、SLA 与真实设备验收均未完成 |

> 不要把“代码可运行”“测试通过”“模型返回结果”“内容质量通过”和“Production ready”混为一个结论。

## 从这里开始

1. 先读 [`docs/handoff/00_START_HERE.md`](docs/handoff/00_START_HERE.md)。
2. 用 [`docs/handoff/01_VERSION_MATRIX.md`](docs/handoff/01_VERSION_MATRIX.md) 确认实际版本边界。
3. 按 [`docs/handoff/05_LOCAL_RUNBOOK.md`](docs/handoff/05_LOCAL_RUNBOOK.md) 完成本地接收。
4. 修改前先看 [`docs/handoff/06_KNOWN_ISSUES.md`](docs/handoff/06_KNOWN_ISSUES.md) 和 [`docs/handoff/08_ACCEPTANCE_CHECKLIST.md`](docs/handoff/08_ACCEPTANCE_CHECKLIST.md)。

## 仓库结构

```text
algorithm/                       V1.75 可独立校验的冻结工程包
apps/eval-web/                   V1.63 Web 实素材测试台快照
apps/diary-one-cloud-intelligence -> ../algorithm
                                 兼容旧 Web 相邻目录约定的软链接
docs/handoff/                    团队交接与当前事实
.github/                         PR 模板和 CODEOWNERS 示例
```

`algorithm/` 和 `apps/eval-web/` 都保留各自的 `MANIFEST.sha256`。Algorithm 的 55 个冻结运行文件与 V1.75 候选收据未改变；打包时仅将 7 处非运行时历史工具中的个人绝对路径替换为显式依赖配置，并生成 `V1.75-20260921-sanitized` 清单。Web 快照内容未改变。

## 数据边界

本仓库不包含 API Key、原始照片/视频、Evidence 帧、真实模型完整请求/回复、私有 Run Audit 或人工评价原文。只有匿名聚合状态进入交接文档。

正式 App、Firmware/SDK 和共享状态文件不在本分支范围内。

## Git 命名

- 本次交付分支：`codex/handoff-algorithm-v1.75-web-v1.63-20260921`
- 后续团队分支：`ai/<topic>`、`web/<topic>`、`api/<topic>`、`infra/<topic>`、`docs/<topic>`
- 版本冻结：`codex-handoff-algorithm-v1.75-web-v1.63-YYYYMMDD`
- 不使用 `final`、`latest2`、`new`、`test-ok` 等无法追溯的名称。

完整规则见 [`docs/handoff/09_GIT_NAMING_AND_OWNERSHIP.md`](docs/handoff/09_GIT_NAMING_AND_OWNERSHIP.md)。
