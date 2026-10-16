# codex V1.63 — 动物通用观察分类

2026-09-04。状态：`LOCAL_POLICY_WIRING_VERIFIED_REAL_MODEL_QUALITY_PENDING`。

## 决定、位置和边界

用户明确同意：观察分类统一ANIMAL，具体物种继续保留在事实文字中，暂不生成猫狗专属标签。这也覆盖真实猫狗，是粒度取舍，不是物种识别能力提升。本检查点 supersede V1.62“标签粒度待决定”状态；旧检查点及真实运行保持原样。

位置为S04分类/schema/校验到最终canonical标签发布。仅修改算法与相邻现有Web的回执；不改Chapter/Aha分工、候选资格、去重、Writer、精选、帧计划、模型和调用次数。不触碰Firmware/SDK、正式App、共享状态、原始素材、历史评价或封存App R1。开始时V1.62的x02.py、bundle.py、x01_server.py指纹全部匹配，无基线漂移。

## 实现

- 新策略 `subject_granularity=DIARY_ONE_X02_SUBJECT_GRANULARITY_V02`，当前V04.1启用，历史X02 V03保持旧行为。
- 深拷贝旧S04 schema，仅将CAT/DOG替换为ANIMAL，不原地修改旧枚举。提示明确非人类动物使用ANIMAL、具体主体保留事实；其他不匹配主体使用OTHER，不猜近似类别。
- 初次S04及拆批/单项重试、校验和失败快照共用同一策略。仍返回CAT/DOG时，只删除非法代码并记字段降级，不转换成ANIMAL，不删除素材或改写事实。
- Chapter/Aha两个canonical出口都停止发布猫狗专属标签。ANIMAL是内部观察码，不擅自新增冻结registry未注册的`CENTRAL_SUBJECT.ANIMAL`。
- Web健康检查和新结果必须包含正确主体回执，旧结果不被重标。V1.62完整画面输入保持。
- 无新增词典、物种特例、关键词匹配或模型审核步骤。下游分组代码没改，但输入粒度变化可能间接影响分组和选材，仍需真实全链验证。

## 证据与验证

真实run `60645614-2249-46f1-9dcc-af455e53e73f` 的13/12.jpg、08/07/06.jpg标准化观察被逐项摘取为测试fixture。明确标注`NORMALIZED_OBSERVATION_SNAPSHOT_NOT_RAW_MODEL_OUTPUT`，不冒充未保存的原始回复，不恢复隐藏非法词。5项新增测试验证：schema隔离、旧错误代码不传播、事实文字/引用保留、ANIMAL接线及失败诊断、当前/历史入口隔离。ANIMAL替换仅作接口结构测试，不代表新的视觉推理，也不保证旧事实文字视觉判断正确。

算法246项：245通过、1项既有本地端口权限测试跳过。Web构建、58项测试、ESLint及页面/导入模块独立严格类型检查通过；未宣称全仓Cloudflare模板类型检查或浏览器视觉QA。独立只读审查核对了全部接线及fixture来源，未发现本范围漏接。

本机算法已重载，`http://127.0.0.1:8787/health`实际返回新主体策略；`http://127.0.0.1:3000/` HTTP200。沿用既有站点，按网站技能仅本地维护，不发布公网、不主动刷新用户页面。代理本次新增模型调用/token/费用均为0；不代表同期无人使用测试页。

## 同期真实运行：不能混淆版本

17:29:48完成run `139169ca-201a-49de-8bad-e4dbb632b470`，session `ef18445c-5f1c-4426-b940-641b2f4fcf27`：3 Chapter、3 Aha、13次模型调用，READY_PRIMARY_COPY。完整审计已保存，但HTTP回传发生BrokenPipe，表明客户端连接断开，原因不能仅凭日志确定。

该run使用Bundle V04/ASPECT_FIT_LETTERBOX，但无主体策略回执，发生在本次服务重载之前，因此属于V1.62，不能作为V1.63分类质量证据。本步不展开其质量复盘、不自动重跑。

## 指纹与交接

- x02.py：`a609c1c6a6506657674351ef5d3682bc62937296d3560919517c16041fa7aed3`
- 真实fixture：`27abea2ae96f0509690f9011871b3c19e563c2c8283bd691c051551922b1fc1b`
- 未改bundle.py：`67a0bd1da43bd8e49bfb22d6f47761a1e702581f4d0c71d8fd8d2a2f67ab4074`
- 未改x01_server.py：`00433af5202f17d2ce329f7c5c5fcd51cb4ace8400e4f9576d2dfb64db9f1399`
- 未改canonical registry：`a76343f872a0c9e18d69b9037c4aeb04bd5f14fa24709833406ec9c815436009`
- 未改Writer出口：`5c8b78102491674d002e26326500a114fc9931d8a0eef5a8572e920e05941ddc`
- 未改内容提示：`de3beb060f361eaf377a19f36b6bf71ca1223b5db2b8af6f86f0b9e3e66de433`
- 未改精选模块：`7c7fd4bdc45ffe7344c94fefa47653c71ff089b46d4b8043ddddbe54a461167e`
- 未改App R1 tar：`bba1db3866560fa9c43d7fe1c8153a26551b256644dad26bf4d2fff28e2dde99`

所有既有未提交工作保留，不混入提交/推送。下一步是新版本真实全链测试与评价，不是直接宣告质量合格。
