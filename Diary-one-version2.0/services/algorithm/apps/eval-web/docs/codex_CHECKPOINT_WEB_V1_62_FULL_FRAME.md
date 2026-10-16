# codex Web V1.62 — 完整画面输入

2026-09-04。状态：`LOCAL_GEOMETRY_AND_TRANSPORT_VERIFIED_NOT_REAL_MODEL_QUALITY_ACCEPTED`。

承接 V1.61。本轮按网站技能维护现有Web，保留项目结构、样式、依赖、锁文件和 `.openai/hosting.json`；不初始化/发布站点，不恢复内部多人测试，不自动刷新用户当前素材与评价，不调用模型。

实际照片/视频绘制由 aspect-fill 改为 aspect-fit，完整源画面缩放到768×1024画布内，空余留边。新输入声明 Bundle V04 / ASPECT_FIT_LETTERBOX，旧V03不被重定义。抽帧数、Window计划、JPEG质量、序列顺序、无GPS/真实时间等不变。约16:9横图内容约768×432，完整性改善不意味着分辨率提升。

版本握手要求服务支持V04及letterbox，返回记录必须匹配本地实际输入。内部接收兼容旧V03，但不会把旧数据标成新处理。页面标记V1.62完整画面输入，提示旧结果必须重新导入；历史结果与评价不改。

验证：构建、58项测试、ESLint、页面/导入模块独立严格类型检查通过。7组实际素材尺寸的几何回归调用正式绘制函数（画布记录替身），核对无裁切、不拉伸、居中、最大适配；不是图片语义测试或浏览器视觉QA。Python接口替身完整通过新版Web接收，旧能力缺失/版本不匹配正常拒绝。

本机页面HTTP200，算法health确认支持V04/letterbox；当前服务仅本地监听。标签粒度方案尚待用户选择，标签实现未改；Chapter/Aha分工、Writer与其他算法策略未改。新增模型调用、token和费用0。

完整实现、验收边界与算法指纹见相邻算法仓库 `docs/codex_CHECKPOINT_V1_62_FULL_FRAME_INPUT.md`。
