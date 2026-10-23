# Diary One · R5_21 Chapter 恢复修复 · 2026-10-23

当前分支：`fix/2026-10-23-r5-21-chapter-recovery`。完整日期与变更说明见 **[2026-10-23 · R5_21 更新说明](docs/releases/version4/2026-10-23-R5_21.md)**。

- 基于 iOS 构建5源码，累计加入 R5_19—R5_21 的云算法和 BFF 修复：传输有界重试、视觉/编辑阶段断点恢复、不完整结果拦截、章节候选图覆盖及边界局部修复、脱敏网络诊断。
- 手机仍为 **MobileCLIP-S0 FP16 v07**，云模型仍为 **qwen3.8-flash**；本分支没有新的 App 构建或云端部署。
- 2026-10-23 发布前复验：算法 **1151通过 / 25历史素材缺失跳过 / 158子测试通过**；BFF **203通过 / 7跳过**。
- phase_10 最终文案与内容审核尚未完成，已有实验总结果仍为 **23/24组有效、19个Chapter**。同请求代理/直连对照通过选图结构检查，不等于整条链路终审通过。

## iOS 构建5交付背景（2026-10-22 历史记录）

> 此前分支 `fix/version4-evidence-preflight` 已纳入构建4之后的接口/链路修复。2026-10-22 已部署匹配BFF/Worker并完成 **1.0.0（5）签名归档**；该交付记录当时尚未执行TestFlight上传及新包真机验收。见 [构建5交付记录](docs/releases/version4/BUILD5.md)。以下保留其历史范围，不代表本分支R5_21已经上线。

> 修复内容：[任务归属、重复提交、额度补偿与恢复](docs/releases/version4/JOB_RELIABILITY.md)。逐版进度及反思见 [第一版到第四版复盘](docs/releases/version4/PROGRESS_AND_RETROSPECTIVE.md)。下方描述原版本4快照，其GitHub分支保持不变。

原分支 `版本4` 保存 **iOS 1.0.0（构建4）** 的打包源码，来源于 2026-10-21 已完成的签名归档。App 构建入口：`apps/mobile`。

- 包含 Chapter 首页摘要、章内高光与原视频定位、历史 Aha 展示，以及完整比例预览、独立控制栏、全屏播放和退出时保留进度。
- 包含此前照片格式/尺寸归一化与视频导入反馈修复。
- 保留 **MobileCLIP-S0 FP16 v07**、云端 **R5_18 / qwen3.8-flash** 和公网 BFF 配置。
- 仓库提供 App、BFF、云端算法源码。源码上传不代表云端已重新部署或 TestFlight 已更新。

请先阅读 [版本4说明与验证记录](docs/releases/version4/README.md)，构建按 [Xcode 内测步骤](README_build.md) 操作。本分支来自原 `version3.0` 提交，目录使用清理后的结构，原分支保持不变。

---

以下为 2026-10-21 **初次清理源码目录时的历史说明**；其中无提交/远端、模拟器构建与待完成状态均为当时记录。版本4当前范围和限制以上方链接为准。

# Diary One version3 · 干净源码目录

更新：2026-10-21。当前工作目录是 `Diary_one_version3_clean`，App 唯一构建入口为 `apps/mobile`。

来源为 `Diary_one_main_algorithm` 的 `version3.0` / `b5eb6118c306281ba680a8652967a5903999fa48` 加本地未提交修复（包含 R5_18）。本目录独立初始化为 `version3.0-clean`，尚无提交或远端。原目录保留；本次未推送或覆盖 GitHub 分支。

## 项目结构

| 目录 | 用途 |
|---|---|
| `apps/mobile` | Expo / React Native App，MobileCLIP-S0 FP16 v07 |
| `services/bff` | BFF、Worker、鉴权、上传和结果保存 |
| `services/algorithm/algorithm` | qwen3.8-flash 云端 Chapter / Aha 算法，当前 R5_18 |
| `docs` | 合同、交接和历史决策；带日期文件保留其当时结论 |
| `scripts` | 构建、检查与团队辅助工具 |

已经移除另一套顶层旧项目、旧导出及10个无调用文件；清理范围、保留理由和回归证据见 [清理记录](docs/CODE_CLEANUP.md)。测试日志和安装产物在工作区 `work_logs/evidence/rebuild-audit-20261021-045231`，与源码分开。

## 从干净环境运行检查

当前实测工具为 Node.js 22.23.1、Python 3.13.13、Xcode 26.6。依赖由锁文件或安装声明重新安装；不复制旧 node_modules、Pods 或虚拟环境。

```sh
cd apps/mobile
npm ci
npm run typecheck
npm run lint
npm run test:core
npm run test:evidence
npm run test:onnx
npm run test:video-evidence
npm run test:native-config
```

在仓库根目录准备 Python 环境（不需要云端密钥即可执行本地回归）：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r services/bff/requirements.txt -e 'services/algorithm/algorithm[test]'
(cd services/algorithm/algorithm && ../../../.venv/bin/python -m pytest tests -q)
(cd services/bff && PYTHONPATH=. ../../.venv/bin/python -m pytest tests -q)
```

## 构建与服务

公网 BFF 配置保持 `https://bff.diary.luxe`，App 只使用用户会话；DashScope、SMTP、API_TOKEN 不进入 App 或本目录。云端 R5_18 上一轮已部署，本次目录清理没有部署或修改服务器。

本次重新构建的目标是 **iOS arm64 模拟器 Release 包**。构建、安装和数据保持结果以 [清理记录](docs/CODE_CLEANUP.md) 为准；不等同于真机 IPA 或 TestFlight。真机分发可按 [TestFlight 步骤](docs/TestFlight打包详细步骤.md) 完成 Apple 签名与公司项目配置，目录统一使用当前 `apps/mobile`。

保留 S0 FP16 v07 与 qwen3.8-flash，不更换模型。部分内容拒绝会显示部分交付；历史25份私有素材缺失，不能计为通过。文案事实准确性、独立 Aha 选图展示、内容重生成入口、Android 原生抽帧、真机和签名分发仍有未完成项，源码清理及自动测试不代表这些能力全部验收完成。
