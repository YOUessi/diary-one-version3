# codex · Web V1.36 — 接入 Storyline V03 / Writer V02

日期：2026-09-03。状态：LOCAL_WEB_INTEGRATION_VERIFIED_NOT_REAL_QUALITY_VERIFIED。

## 授权与范围

用户明确允许将修改范围扩展到测试 Web 的版本接入部分。只对齐版本校验、类型、必要的结果说明和本地验证；不更改算法规则、素材采样、评分、评价定义、Firmware/SDK 或共享状态。公开/内部多人测试继续暂停，不发布、不修改 Sites 访问权限。不会调用付费模型。

使用既有 Sites 工程及其运行流程，不重新初始化、不改页面风格、不新增依赖。已有未提交改动保留。

## 已核对的算法基线

依据算法仓库 V1.35，当前文件无漂移：

- `src/diary_one_ci/x02.py`：`6cdcefdd564502cb11ac282153bc84902cbf7ede11894bed85a7a891ffc2ba1e`。
- `src/diary_one_ci/contracts/codex_x02_storyline_v03.json`：`3da709072857288d1301a56a936d8d03dfd3c1654c88d9d9e09176071180122b`。
- `contracts/codex_x02_staged_preview_v04_1_storyline_v03.schema.json`：`26313706708d07a84d2c1a206623daa1dfed96096953cdc4303ab8817e0d3abb`。

Web 修改前：

- `app/lib/media-evidence.ts`：`ea6118e933027e867296564ca9c91ae6bb915bdc6ea6f5d3d85c812b01b93021`。
- `app/lib/contracts.ts`：`0b560489329b2ce5dd5f3de73067f433b666812299f5703cbaef3ee1902e0a37`。
- `app/lib/result-contract.ts`：`23e6fa823b1c28a222ee0b202b9e56b61a88f03d54a60d70b7b2ef6b353d1447`。
- `app/page.tsx`：`fb406076f6ee0d3879990cb0a5eff0efe2f54b98ace2ff830b79d4712f7f1a64`。

## 本步接入方式

1. 健康检查和正式结果均要求 Storyline V03 / Writer V02；保留 X02 V04.1 传输路由、Bundle V03、全流程运行、事实/素材引用与交付状态校验，不靠放宽为任意版本来接入。
2. `focus_code` 只是可为空的字符串注记，页面不再把它当作必须存在的八选一主题；保留模型内部说明和逐成员说明。结构通过不显示成“内容一定正确”。
3. 页面分别显示目标、连接服务与本轮结果版本，连接前后的算法合同哈希及 Writer 版本必须一致。没有运行时明确显示尚未运行，不把本地代码版本当成真实测试结果。
4. 本轮只做版本/接口/构建验证，真实素材的质量验收另行完整运行。

## 验证结果

- `npm test`：构建成功；53 项技术测试通过，0 失败、0 跳过。
- 新增 `tests/codex-current-preview-version.test.mjs`，复用相邻算法仓库已有的 ScriptedGateway 和 Bundle V03 接口夹具。实际执行当前 Python pipeline，再把结果送入 Web 的正式响应处理函数；覆盖健康检查、空的可选 focus、Chapter 引用结构、新旧版本区分。没有新造视觉语义反例，没有新增语义运行时规则。
- 上述夹具仅代替模型接口，素材字节也不是可用于理解评价的真实图片。它只证明接口接通，不证明聚类、筛选、Aha 或文案质量。
- 本步页面和算法接口文件的独立严格 TypeScript 检查通过；`git diff --check` 通过。
- 全仓 `tsc --noEmit --incremental false` 仍有 3 处本步未修改的 Cloudflare 模板类型问题：`db/index.ts` 缺少 `cloudflare:workers` 类型，`worker/index.ts` 缺少 `Fetcher`、`D1Database` 类型。这不是本轮代码类型错误，但因此不能声称全仓 TypeScript 检查通过。本轮未扩展到部署模板修复。
- 结束前重新核对算法三个基线文件，哈希与上方一致。本步没有改动算法文件。

## 本地服务与交付

- Web 实际启动地址：`http://localhost:3000/`，轻量 GET 返回 HTTP 200；已请求在 Codex 打开该地址（UI 返回 queued）。
- 算法服务：`http://127.0.0.1:8787`；`/health` 返回当前 Storyline V03 / Writer V02，浏览器来源 `http://localhost:3000` 的 Preview 预检返回 HTTP 204。
- 服务公布的 Storyline 合同规范化哈希为 `21b3d7e404bc0209cd99d062ecc493e769d13517603bae913c19eb7474d99cca`；它与上方 JSON 文件原始字节哈希属于不同计算口径。Web 比较连接时与结果中的同一服务合同哈希。
- 服务已从 macOS Keychain 读取现有凭证，健康检查 `modelReady=true`；没有打印密钥，没有付费 API 请求，不能据此断言凭证仍有效或云模型可用。
- 启动曾被沙箱端口权限阻止；获得本轮网络权限后已正常启动。本轮保留本地服务供用户测试，不发布、不修改托管权限。
- 用户需刷新页面、重新导入一批真实素材并完整运行，查看“本轮实际算法版本”后再评价。既有旧结果保持旧版本属性，不冒充新结果。
- 保留仓库原有未提交改动。本轮已本地存档，未将混有其他阶段修改的整个工作区打包提交或推送。

## 修改后文件指纹

- `app/lib/media-evidence.ts`：`3840c9d41281488caa4cc0737680b3a8cd6e86cd56e25c7f34e5146de22968ba`。
- `app/lib/contracts.ts`：`d0fc971fa5bf21a96e56184119a2f28b1d6a9712a692a55279853807cd11687a`。
- `app/lib/result-contract.ts`：`23e6fa823b1c28a222ee0b202b9e56b61a88f03d54a60d70b7b2ef6b353d1447`（本轮未改）。
- `app/page.tsx`：`7963b8f366bb3f5371f3e80d56eb92081fdbaba77c5ac95fb6d86b4df44ae9cd`。
- `tests/codex-current-preview-version.test.mjs`：`ccd10383fca2648b3a121300138f2bddc3f41ceccda113653e14997f21bbe987`。
- `tests/rendered-html.test.mjs`：`adec3f6a84d1462c9f5a29ed5ee2e8032e97d51e2ba4939a9d81aca50ec5380d`。
- `tests/result-contract.test.mjs`：`4452fd6a1e939cf28af8a4c494124d76554bf14a01ddd95cea1bd77dc00f8005`。
- `package.json`：`5ecd758b959d00519fd30d23ae97899130aa5811fa86a289bfe70b1e9cbb9602`。
- `README.md`：`dec8d5aad7454d539e6d60d96be91eb2b326aa609560fa23e3029ae25366f0c1`。

## 下一步与停止点

本步到此停止，不连续扩展清理范围。下一步是用户在本地测试页完整运行真实素材，并按具体 Chapter、Aha、素材和表达提交评价，再据真实结果确定需要修正的共性逻辑。
