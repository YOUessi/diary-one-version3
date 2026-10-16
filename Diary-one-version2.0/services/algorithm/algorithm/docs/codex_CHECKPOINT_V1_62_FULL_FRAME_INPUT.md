# codex V1.62 — 手机测试素材完整画面输入

2026-09-04。状态：`LOCAL_FULL_FRAME_TRANSPORT_VERIFIED_NOT_REAL_MODEL_QUALITY_ACCEPTED`。

## 位置、证据与边界

承接 V1.61 后用户的真实测试复盘和“好”：先修输入裁切与错误标签传播，不推进 Chapter/Aha 故事分工或 Writer。真实 run `60645614-2249-46f1-9dcc-af455e53e73f`（session `54d72604-32cf-4424-9033-91c5d87a3026`）26件素材中大量横片；原图尺寸、旧 manifest 的 CENTER_CROP_ASPECT_FILL 与浏览器实际缩放函数一致表明，16:9 横片旧处理只保留约42.2%的横向范围。

本检查点**仅完成完整画面输入**。主体标签粒度选择仍等待用户答复：建议观察层改用通用动物类别、具体名称保留事实；这种方案也会降低真实猫狗的物种级标签精度，不能自行视为已接受。没有修改主体枚举、canonical registry、标签投票、分组、Aha、Writer 或候选内部长度门槛。

修改范围：算法仓库及相邻现有 Web；不触碰 Firmware/SDK、正式 App、共享状态、历史真实运行/评价或封存 App R1。开始前 V1.61 的算法/Web指纹全部核对一致，没有基线漂移。此检查点仅 supersede 当前 Web 输入处理，不改写 V1.61 与既有冻结合同。

## 实现

- 新增 `DIARY_ONE_APP_LIBRARY_BUNDLE_V04`，空间处理为 `ASPECT_FIT_LETTERBOX`；等比例缩放完整原图到 768×1024 画布，空白处黑色留边，不拉伸、不裁切。照片、视频共用实际绘制函数。
- 帧数、时长 Window、JPEG质量、sequence-only顺序、无GPS/真实拍摄时间、原素材不上传均不变。16:9横片内容约768×432，保留完整画面的代价是细节像素减少，未顺便提高分辨率或增加请求。
- 新建输入schema及支持V04输入的输出schema，旧schema不变。V04沿用V03的严格字段、序列、帧引用、哈希和时间约束；不能把真实letterbox谎报成center-crop。
- 后端明确区分V03裁切与V04留边，记录 `APP_LIBRARY_BUNDLE_GATE_V04` 与 `aspect_fit_letterbox_declared`。历史E00/X02 V03和历史X01路由不能接入V04。
- 健康接口保留旧 `appLibraryBundleVersion=V03` 兼容字段，增加支持版本列表与空间变换列表；新Web必须确认V04和letterbox能力。返回结果版本必须匹配本次实际输入，不把历史V03结果重标成V04。
- S04只在新留边输入中补充“空白留边不是场景”说明；其余语义提示和调度不变。
- 本页显示V1.62完整画面输入，说明旧结果需重新导入；原有运行策略文字不再把输入版本混同Writer版本。

## 本地验证与限制

- 算法241项测试：240通过、1项既有本地端口权限测试跳过。
- Web构建、58项测试、ESLint、页面及导入模块独立严格类型检查通过；未宣称全仓Cloudflare模板类型检查通过。
- 新几何回归用真实run出现的7组尺寸执行正式绘制函数，核对全源图绘制、四边均在画布内、比例不变、居中和最大适配；不是虚构语义案例。画布由测试替身记录调用，未声称浏览器图像视觉QA或重新识别原图。
- 接口替身完整经过Python主链与Web接收，确认 `[1,3,4,8,12]` 帧计划不变、V04真实透传、旧V03不能假报新空间处理。该证据不代表真实模型质量。
- 本机算法已重新加载：`http://127.0.0.1:8787/health` 确认V04与letterbox支持，modelReady=true仅表示已有凭证可读取。
- 本地Web `http://127.0.0.1:3000/` HTTP 200；复用现有运行中的页面，不主动刷新用户当前素材/评价状态。公网与内部多人测试仍暂停。
- 新增外部模型调用、token和模型费用均为0。尚无新素材全流程真实模型结果，不能称为聚类/标签/文案质量修复。
- 现有大量未提交内容保留，不把其他阶段或其他工作混入一次提交/推送。

## 完成指纹

- bundle.py: `67a0bd1da43bd8e49bfb22d6f47761a1e702581f4d0c71d8fd8d2a2f67ab4074`
- x02.py: `bc2e92177ff8509bc511db8d0fc6b8c5ddea29239da2109ce84d98dde5699fd1`
- x01_server.py: `00433af5202f17d2ce329f7c5c5fcd51cb4ace8400e4f9576d2dfb64db9f1399`
- 新输入schema: `217eae77733df52bf50505525a70a9e0cf754f69c59d68055afb471a81d99726`
- 新输出schema: `10f8c36cc0548873cc7a1c88cd8216da167fbb6f05ac9bd83768f61729679b13`
- 未改 Writer出口: `5c8b78102491674d002e26326500a114fc9931d8a0eef5a8572e920e05941ddc`
- 未改内容提示: `de3beb060f361eaf377a19f36b6bf71ca1223b5db2b8af6f86f0b9e3e66de433`
- 未改精选模块: `7c7fd4bdc45ffe7344c94fefa47653c71ff089b46d4b8043ddddbe54a461167e`
- 未改 App R1 tar: `bba1db3866560fa9c43d7fe1c8153a26551b256644dad26bf4d2fff28e2dde99`
