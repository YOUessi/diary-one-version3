# codex App R2 接入封存｜锁定 V1.63

2026-09-04。状态：`SEALED_AND_DELIVERED_TO_04_OFFLINE_INTEGRATION_CANDIDATE`。23:27 北京时间完成封存；随后已将固定路径、hash、差异与入口同步 04。未部署、未切换 App/Web 默认、未验收真实质量。

## 决定与边界

Owner 经 04 明确要求：锁定最近可运行、可复现的 V1.63 用于 App 接入，不等待 V1.65 活动修复或质量最终验收。04 已记录 APP098。接线成功、真实算法质量、正式上线是不同结论；质量缺陷写入说明，不自动阻塞离线接线。

本步只在算法仓库新增独立 `handoffs/codex_app_20260904_r2/`、构包/离线校验工具与本检查点。不覆盖 R1，不改算法主干、Web、App、07、Firmware/SDK、共享状态。不启动服务、不读凭证、不访问模型、不加入真实素材或真实模型文字。

## 先核验的基线

- V1.63 来源：`var/codex_v1_64_repeat_review/codex_runtime`；按 `codex_preparation.json` 核验 40/40 运行与合同文件一致。
- `x02.py` 固定 `a609c1c6a6506657674351ef5d3682bc62937296d3560919517c16041fa7aed3`，不用当前 V1.65 工作区内容。
- `pyproject.toml` 不在实验 40 文件中，从 R1 已封存版本补入并核对当前未变，SHA `eb1ebdddb6708c99a16f5fbcbb733826b83eea8242f1a836f8cd04019cbb3270`；单列来源，不冒称在实验清单中。
- R1 总包 SHA `bba1db3866560fa9c43d7fe1c8153a26551b256644dad26bf4d2fff28e2dde99` 已只读复核；Git HEAD 仅为背景，不能替代逐字封存。

## 验证与交付计划

1. 精确封存上述 41 个源码/合同/配置文件，列 R1→R2 文件和接口差异。
2. 复用既有合成接口 Gateway/纯色图片，验证 V04 完整画面输入、历史兼容、结果状态及引用绑定；这些构造仅是工程合同测试，不是新语义反例、训练集或质量评分。
3. 独立复跑、校验归档与逐文件摘要、审查没有真实素材/凭证，然后给 04 固定路径、hash、输入输出差异与启动入口。启动入口说明不是启动授权。

日期仍为 sequence-only/null，不用上传日期冒充真实记忆日期。既有质量缺陷与 App 外层任务恢复分别列出，封存不声称算法提供了原生异步任务或可靠日边界。

## 实际交付与验证

- [完整接入说明](../handoffs/codex_app_20260904_r2/codex_README.md)；[外层 profile](../handoffs/codex_app_20260904_r2/codex_profile.json)；[文件差异](../handoffs/codex_app_20260904_r2/codex_r1_r2_file_differences.json)。profile只是外层固定配置资料，不是新的算法wire合同。
- [整包](../handoffs/codex_app_20260904_r2.tar) SHA256：`86a4adfd143e832c1c4897f23f99fe88563f2ef1bb3625ef3a010612d512c6be`，5,632,000字节。
- 源码tar SHA256：`f27855e67c4aca3b010c012a66ea0bf1ec2b4c6018d1b8800c6d26245b9bc138`，1,024,000字节。
- profile SHA256：`517167650043b32179a15b1eebcbe96b38cfdc456cc97777f65adff3536f5bc0`；[最终交付收据](../handoffs/codex_app_20260904_r2_delivery.json)含8项关键物件hash。
- 相对R1的41文件：33相同、5修改、3新增。R1完整包不改；当前V1.65的x02.py仍为`ab61205ef49806e6a0504e282d44e696395253e64d789f759e4f722edd476a5e`，未因封存回滚或修改。
- 包内 [离线证据](../handoffs/codex_app_20260904_r2/codex_examples/codex_offline_evidence.json) 和 [独立复验](../handoffs/codex_app_20260904_r2/codex_independent_verification.json)：Python3.12.14/Pillow12.3.0，10状态样例、9输入拒绝、7结果格式/引用检查通过，0真实模型调用；V03兼容、V04完整画面、软长度保留均验证。没有安装依赖。
- 合成产物116文件+自身清单；封包采用源文件与交付文件明确白名单，额外文件拒绝。本地缓存明确排除，171个tar成员与逐文件清单全部验hash通过。
- 模型请求schema从固定源码的合成阶段调用中导出，不把旧硬长度/CAT-DOG请求schema误当当前请求；没有启用供应商strict schema。
- 构包主流程与独立复跑均不调用真实模型、不发素材、不监听端口。本阶段未跑真实素材；接口检查不是图像质量/手机真机/HTTP/TLS/Production认证。

独立交叉核查在封包前纠正了两处交付风险：文件枚举由后缀过滤改为明确白名单；multipart字段正确为`manifest`而不是`bundle.json`（后者仅是文件名）。两者仅影响交付工具/说明，未改算法；已重点通知04。health确实包含pipelineVersion，但仍没有源码tar指纹，必须结合profile识别实际部署版本。

下一责任边界：04按APP098接入固定R2并验收App解析/画面输入；07管理外层任务与版本注入；05继续算法内容主干。封存R2后不原地追逐V1.65，未来以新候选明确替换。
