# Diary One Real-media Test Lab

独立的 Diary One Web 实素材测试面。它把手机相册中的一批照片与视频视为一个测试日，生成标准化 Evidence，调用本机研究算法桥，并展示 Chapter、Aha、最新合同检查、可审计决策轨迹、分阶段时间/Token/成本与颗粒化人工评价。

## codex 当前接入 V1.63（2026-09-04，动物通用观察分类）

当前新导入使用 Bundle V04，完整画面等比例缩放到768×1024画布，留边而不裁切。用户已同意V1.63动物通用观察分类：物种留在事实，卡片暂不生成猫狗专属标签。新增主体策略回执，旧服务/结果不冒充新版；旧结果不自动重算。分组、Aha与Writer策略未改。见[V1.63检查点](docs/codex_CHECKPOINT_WEB_V1_63_SUBJECT_POLICY.md)与[V1.62检查点](docs/codex_CHECKPOINT_WEB_V1_62_FULL_FRAME.md)。以下V1.61记录保留为既有接入背景。

接入当前精选子集接收、Aha 非导入相邻去重、单次 Writer 和中文软长度策略。Aha 20 字为目标，21–24 字正常接收；更长文案保留并在该 Aha 主卡片和评价卡片标记“偏长，待评价”，不重写、不截断。格式/引用通过不代表内容准确或自然。

健康检查与本轮结果分别记录实际策略（当前包括新增主体粒度策略），旧服务不能冒充新版。当前表面检查对偏长给出 REVIEW，不按长度 BLOCK；旧结果不会因为页面升级自动获得新算法结果。所有自动评价标记仍只作辅助，人类评价不被自动填充。

仅本地使用，公网/内部多人测试继续暂停。不修改 S00–S10 规则、模型选择、原素材或正式 App。本次接入不是新一轮真实素材全链路质量验收。详见 [codex Web V1.61 检查点](docs/codex_CHECKPOINT_WEB_V1_61_WRITER_EXIT.md)。

## 历史接入 V1.37（2026-09-03）

在 Storyline V03 / Writer V02 上增加独立的 `Chapter Media V01`：正式 Chapter 最低 3 项、最多 5 项，不再保留旧双素材例外，也不默认填满。超过 3 项时，每个已选 Chapter 最多增加一次现有视觉模型调用，比较每项已上传的代表预览帧；恰好 3 项直接保留。不重做聚类、不读取拍摄时间、不增补上传。

模型给出优先顺序与展示数量；若排序有效但数量偏少，会保留前三项。调用失败或排序不完整时按画质保留三项并显式提示“尚未确认去重效果”，不因为精选失败删掉合格 Chapter。选择理由、未展示成员及单独的时间/Token/成本记录可查。未展示不代表删除原文件或 Chapter 成员。

本轮仅完成本地实现与技术验证，真实视觉模型的选择质量尚未通过新一轮全流程评价。使用原本地入口，不发布公网。对应算法存档：`../diary-one-cloud-intelligence/docs/codex_CHECKPOINT_V1_37_CHAPTER_MEDIA_SELECTION.md`。

## 前一检查点 V1.36（2026-09-03）

- Web V1.36 对接算法 V1.35：`Storyline V03 / Writer V02`，传输路由仍为 `/x02/v0.4.1/preview`，输入为 Bundle V03。
- 页面分别显示本页目标、已连接服务、本轮实际结果的版本；服务与结果不一致时不展示成新版本成功结果。旧结果不会因页面更新而变成新算法结果。
- Chapter 的模型分组说明可以没有固定分类标签；“结构与引用检查通过”不等于语义聚类正确。不会重新引入八选一的主题要求。
- 本轮只做接口与页面接入，未调用付费模型；真实质量需使用新版本重新导入并完整运行后评价。公开/内部多人测试继续暂停，仅本地使用。
- 存档见 [codex Web V1.36 检查点](docs/codex_CHECKPOINT_WEB_V1_36_STORYLINE_V03_WRITER_V02.md)。

## 当前全链路位置

```text
冻结的产品/算法合同 Canonical V1.25（S00–S13）
  ↓
本 Web：手机素材导入、仅保留导入顺序、Evidence、本轮评价
  ↓
X02：真实素材分阶段 Preview
  ↓
Chapter / Aha 结果 + 最新可见合同检查 + 人工标签
  ↓
后续真实数据校准、App 后台工程与 Production 验证
```

必须区分两件事：

- 页面按最新冻结合同检查 Chapter、Aha、文案、媒体数量和 Canonical Tag；
- 当前真实模型执行是 `X02_STAGED_REAL_MEDIA_PREVIEW_NOT_PRODUCTION`：S04 小批感知、S03/S05–S07 结构、S08–S09 集合选择、S10 媒体精选、S11 Writer 和 S12 校验已经分责；S13 HQ 导出仍未执行，因此不能称为 Production engine。

## 本轮测试合同

- 一次文件选择 = 一个完整测试日；再次选择会新建并替换当前测试日。
- 不读取或使用 GPS、拍摄时间和时区。
- 文件排列顺序只表示本轮处理先后，并在加法式 `App Library Bundle V03` 中只记录为 `sequence_index`；不伪造拍摄日期、固定时间间隔或当天时长，页面允许手动上移、下移。Bundle 中必需的 `logical_asset_duration_ms=9000` 只是算法兼容所需的九秒标准化包络，绝不是素材间隔、拍摄时长或合成时间线。历史 V02 合同不被静默改写。
- 每次正式测试都是 `FRESH_FULL_RUN`：从原始素材重新生成 Evidence，跨轮语义缓存不参与质量结论。
- 照片生成 1 帧 Evidence；视频按实际时长采用测试专用 Window Profile：不超过 10 秒为 1 Window / 3 帧，10–30 秒为 2 Window / 4 帧，30–90 秒为 4 Window / 8 帧，超过 90 秒为 6 Window / 12 帧。
- 该手机测试 Profile 不覆盖冻结的 Auto 9 秒三帧合同，也不等同于未来正式 App 的采集模式判断。
- 新 Evidence 统一为 `768×1024`、portrait `3:4` 画布、aspect-fit letterbox、JPEG `0.84`；完整源画面等比例保留。
- 原始照片/视频不发给算法服务或模型；只有标准化 Evidence 会经本机网关交给所选云模型。
- 云端完整运行通常需要 3–9 分钟，当前单次接口不提供阶段心跳。页面会显示不确定进度与真实等待时长，允许用户主动取消，并仅在 15 分钟后触发保守超时，不会用 Evidence 已完成的 100% 进度冒充云端算法进度。
- X02 本地测试日默认最多 240 项，覆盖 186 项高强度日基准。V04.1 按每批最多 3 项，并同时限制帧数与 Evidence 体积来生成 Observation，再用结构化事实做全天聚合；超出 240 项时明确阻止，不会静默丢素材。
- 较少 Chapter 不能为了数量而填充。Aha 必须同时搜索事件与具体生活发现；零 Aha 只有在审计明确记录 `NO_GROUNDED_AHA_AFTER_SEARCH` 时才是合法语义结果。已有候选只因 Writer/工程合同失败而无法发布时必须显示 `PIPELINE_BLOCKED`，不能伪装成 `EMPTY_DAY`。
- 只有 `STAGED_PREVIEW_VALIDATED + VISIBLE_PREVIEW` 的记忆进入主 Chapter/Aha 卡片、数量、表面合同检查和正式逐项评价；识别不完整或交付受阻的候选单列为诊断内容，不得冒充正式结果或污染评分。

## 手机素材对结论的影响

Evidence会等比例缩放到 `768×1024` 画布；低清、抖动、模糊和缩小后的细节仍会降低理解质量。V1.62 / Bundle V04完整保留横屏画面，旧V03仍是历史center-crop合同。素材数量仍会影响经历覆盖与Chapter完整度。最大的不可消除偏差是采集行为：手机素材通常主动、精选、第三人称或不连续，而真实设备输入是持续、第一人称、约两分钟间隔的自动采集。

因此本轮可以验证：

- 语义理解；
- Chapter 边界与跨短插曲连续性；
- 精选素材、Dominant Motif 去重与保留；
- Chapter/Aha 故事职责；
- 中文文案、事实 Claim 与 Canonical Tag；
- 每个真实模型阶段的时延、Token 和估算成本。

本轮不能据此冻结：

- 穿戴场景准确率；
- 真实日均 Chapter/Aha 数量；
- 1.5/2 小时 Preview 触发效果；
- 多次 Sync 的替换与修订；
- GPS、地点 Entity、真实日界线；
- Production 队列、存储、电量、网络和总成本。

## 本地运行

需要 Node.js 22+，算法仓库位于相邻目录 `../diary-one-cloud-intelligence`。

终端 1：

```bash
npm run algorithm
```

默认从 macOS 登录钥匙串读取：

- service：`DiaryOne DashScope API Key`
- account：当前 macOS 用户

健康检查只能确认“凭证存在”，不能在不产生模型请求的情况下证明凭证有效。若首次生成提示凭证失效，请更新这条钥匙串记录并重启 `npm run algorithm`；Web 不保存或展示 API Key。

终端 2：

```bash
npm run dev
```

打开 `http://localhost:3000`。可按先后导入最多 240 项素材作为一个测试日；系统内部会小批理解并做全天聚合。浏览器目前仍一次准备完整 Evidence，因此超大测试日会增加本机内存与等待时间。

## 浏览器兼容

JPEG、PNG、WebP、H.264 MP4 等常见格式可直接使用。iPhone 原始 HEIC / HEVC 的浏览器支持并不一致；在 macOS 上优先使用 Safari。无法解码的项目会明确标记并阻止运行，不会被静默跳过。

## 数据与持久化

- 原始素材和预览 URL 只存在于当前浏览器 Session；刷新即清空。
- Web 不启用 D1/R2，也不持久化媒体字节。
- 每次成功运行会在算法仓库本地自动保存一份不含图片的 X02 Run Audit：`var/x02_runs/<session>/runs/<run-id>.run_audit.json`；`run_audit.json` 指向该 Session 的最新一轮。历史 X01 记录继续留在 `var/x01_runs/`。
- 客户端逐素材/逐流程计时与 Human Evaluation V02 会作为 Sidecar 自动保存到同一 Session。评价只收集，不会自动修改算法。
- 人工评价可分别绑定到整天、某个 Chapter/Aha、某张素材、某个 Evidence frame，以及边界、媒体、标题、正文、Tag、Aha 独立性等 Aspect。
- 导出按钮只下载当前运行的 manifest、算法结果、合同检查、Client Trace 和人工评价 JSON，不包含媒体字节或研究 Token。
- 本项目不连接 Diary One 硬件，不修改 Firmware/SDK、正式 App 或共享状态文件。

## 验证

```bash
npm test
```

当前版本接口测试复用相邻算法仓库已有的测试替身，检查 Python 实现的实际返回结构能否进入 Web。需要 Python 3.9+；不会调用云模型，也不代表真实图片理解或聚类质量通过。

算法侧：

```bash
cd ../diary-one-cloud-intelligence
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
