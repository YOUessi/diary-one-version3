# version3.0-clean 清理与重新构建

日期：2026-10-21。源目录 `Diary_one_main_algorithm` 保持原样；新目录为 `Diary_one_version3_clean`，来源是 `version3.0` / b5eb611 加当前未提交修复。独立 Git 分支 `version3.0-clean` 无提交、无远端。

## 已清理

- 仅迁入旧 `Diary-one-version2.0` 有效项目，展平至根目录。排除另一套顶层 apps/services；原仓库两套项目有909个重叠路径，其中743相同、166不同，未把不同文件盲目合并。
- 排除18个 `.verify_export` 旧导出、1个 `.claude` 配置和被忽略的环境、凭据、缓存及运行产物。
- 删除10个已核对无调用旧文件，共715行：本地OTP占位实现、旧连接卡/导出入口、旧问卷图标、旧权限文案、未使用搜索代理、旧UI基础组件、旧直方图语义降级器、未使用的PNG压缩字节画质代理。
- 删除 `services/algorithm-handoff-v1_75` 中157份重复交接文件，合计3,147,276字节。逐文件与 `services/algorithm/algorithm` 比对完全相同，后者全部保留。
- 简化重复交付状态分支，移除未使用导入、合并重复导入。移除启动/重置时按演示编号覆盖真实视频播放地址的行为，以及失去调用的演示替换函数；演示素材解析器仍供Lab显式模拟使用。
- 更新当前README及构建入口，旧日期交接文档明确标为历史；旧远端语义工具说明不再误称默认手机模型是Apple Vision。
- Python 3.13干净安装暴露X02所需 `legacy-cgi` 未纳入包依赖的问题，已在pyproject声明条件依赖。首次失败记录保留，修复后完整回归通过。

## 保留及限制

静态入口图扫描225个TS/TSX文件，209个可达；清理后215个、209个可达，无未解析相对导入。剩余6个候选不是“6个确定缺陷”：包括声明文件、证据API导出、兼容分析器/协议入口、备用本地编码路径。它们需按兼容支持范围决定去留。

未直接import的包也可能供原生自动链接、Babel或组件依赖使用。本轮未贸然删除依赖；`expo-video-thumbnails`等候选保留待单独缩减依赖测试。BFF的Dev Lite/生产分享路由和部分历史算法工具存在相似实现，此次没有改动其行为。不能据此宣称全仓库已零冗余。

手机模型仍是S0 FP16 v07，模型SHA `7ea0ab32ddbbd1c51b6158f12ccb669968de37125dd7455f04b6e1988cb9a141`。云端为R5_18 / qwen3.8-flash，云算法语义实现未在此次清理修改；服务器没有重新部署。

## 新环境验证

| 检查 | 本次结果 |
|---|---|
| npm ci | 新安装775包，无旧node_modules链接 |
| Python环境 | 新建.venv；依赖版本见根目录requirements-validated.txt，可作为pip约束使用 |
| App核心 | 120 passed（包含演示ID冲突时保持真实播放地址） |
| ONNX生命周期/原生补丁 | 21 passed |
| 视频证据/算法适配 | 21 passed |
| 原生配置 | 4 passed |
| S0 v07参考 | 28抽帧案例、5像素案例；最大目标函数差1.3813e-7 |
| 云算法 | 1067 passed，25 skipped，158 subtests passed；跳过项缺历史素材 |
| BFF | 71 passed |
| 类型/lint | 通过；lint 0错误、4条现有警告 |
| macOS AVFoundation边界 | 10 passed，覆盖尾窗/16ms偏移/旋转/低帧率/损坏视频 |
| iOS Release新构建/安装 | 通过；新arm64模拟器包，安装二进制SHA与构建产物一致 |
| 升级、冷启动与播放 | 原有登录/中文/1Chapter/0独立Aha/素材/任务完整保留；火车和草地分别播放正确原片 |

CocoaPods/原生工程由新目录prebuild生成，DerivedData位于本次独立证据目录。允许使用包管理器的官方包下载缓存，但没有复制旧项目Pods、原生workspace、node_modules、虚拟环境或编译产物。

本次构建目标为iOS arm64模拟器，不能安装到真实iPhone。真机、TestFlight、Android、BLE及新全流程公网生成不属于此轮完成声明。既有内容质量限制、独立Aha选图与重新生成入口未因清理而自动解决。

## 原始证据

工作区 `work_logs/evidence/rebuild-audit-20261021-045231`：

- `clean-copy-receipt.json`：复制来源与逐文件SHA。
- `removed-code.json`、`source-before-cleanup/`：10个旧文件清单和备份。
- `removed-duplicate-handoff.json`：157份重复文件及保留副本位置/SHA。
- `import-audit.json`、`import-audit-clean.json`：清理前后入口图。最后补查移除1个PNG字节代理，因此最终215个TS/TSX文件、209个可达。
- `mobile/`：依赖、测试、prebuild、Pods、构建和资源收据。
- `algorithm-tests.txt`、`bff-tests.txt`：本轮完整测试；首次依赖错误在first-attempt文件保留。
- `simulator/`：升级前后数据及界面证据，凭据不输出。

额外隔离核对：原目录1075个已复制源码文件SHA均保持；96个云算法/BFF Python文件与旧工作区完全相同。生成的4份原生配置不引用旧工作目录。源码清单911文件的密钥模式扫描未命中；这不替代发布前人工凭据检查。

## 最终构建回执

最终App源码快照SHA：`771b23c6152009c3a1b6a2ca9b3be8cb311771cf9d144a8e21b6ba23bf59c15d`。构建前后无源码漂移，ONNX生命周期补丁标记与视频编码模块注册通过，模型与prompt资源SHA匹配。初次全量编译过程中又移除1个未调用旧函数，其构建候选因源码清单变化未交付；最终构建重新核对通过，随后无卸载覆盖安装、实际播放和冷启动均通过。

交付包在工作区 `deliverables/DiaryOne-version3-clean-20261021/`：干净源码ZIP、iOS模拟器.app ZIP及SHA256SUMS。包内无旧依赖、缓存、私钥、环境文件或会话。新目录保持无提交/无远端，原目录未改变。
