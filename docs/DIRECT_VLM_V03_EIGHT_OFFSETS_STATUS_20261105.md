# Compact V03 八组真实偏移实测：旧 HTML 状态纠偏（2026-11-05）

## 为什么看见 DIRECT_VLM_OUTPUT_INVALID？

Mac 上的 sydney-direct-vlm-other-offsets-20261105/ALL_OTHER_OFFSETS_REAL_JPEG_REVIEW.html 属于旧 Direct VLM V01 测试，其失败是历史事实，不是当前 Compact V03 的最新状态。原先的 Compact V03 HTML 仅展示 10s、20s、30s，未覆盖其他五组。

为了避免混淆，两个旧 HTML 已加入醒目的历史记录标识及最新版入口。旧实验记录保持原样，仅展示层增加说明。

最新版统一页面：work_logs/evidence/sydney-direct-vlm-compact-v03-20261105/LATEST_V03_8_OFFSETS_REAL_JPEG_REVIEW.html

## V03 实际 API 回归

所有输入均预先删除源视频 00:00–01:12，使用真实 JPEG、Frame ID 来源校验和逐帧时间序号。模型为 Qwen3.8-Flash，程序为 Compact V03。此表是**模型输出经过 BFF 结构和原图来源绑定校验的结果**，不是独立语义质量评分。

| 偏移组 | 旧版 V01 | 最新 V03 | Chapter | 图库 | V03 API 调用 | 估算人民币成本 |
|---:|---|---|---:|---:|---:|---:|
| 10s | 失败 | 成功 | 8 | 63 | 1 | 0.16432070 |
| 20s | 失败 | 成功 | 8 | 37 | 2 | 0.31090579 |
| 30s | 成功 | 成功 | 8 | 40 | 1 | 0.15957007 |
| 50s | 失败 | 成功 | 7 | 33 | 1 | 0.15579662 |
| 60s | 失败 | 成功 | 10 | 29 | 1 | 0.15577870 |
| 70s | 失败 | 成功 | 11 | 34 | 1 | 0.15326618 |
| 90s | 失败 | 成功 | 9 | 71 | 1 | 0.15186838 |
| 100s | 失败 | 成功 | 9 | 65 | 1 | 0.14908183 |
| **合计** | **1/8 通过** | **8/8 通过** | **70** | **372** | **9** | **1.40058827** |

其中 50s、60s、70s、90s、100s 是本轮新增的五组真实模型调用，全部一次通过，共估算 ¥0.76579171。本轮 10s、20s、30s 引用既有真实 V03 记录，没有额外再次付费。八组分别输入，总计使用 1,809 张真实抽帧（同一原始视频不同相位，并非 8 个独立原始视频）。

## 必须继续处理的语义质量问题

- 60s 产生 10 章、70s 产生 11 章，存在过细拆章的风险。
- 10s、20s、70s、100s 的部分相邻章，所选来源图片推导的时间跨度存在重叠。确定性引用正确不表示 Chapter 时间边界严格互斥。
- 10s、50s、60s、70s 生成包含“周末”或 weekend 的描述，但没有可信拍摄星期信息。
- BFF 通过说明来源 JPEG、Frame ID、图库结构合法，不等于建筑专名、活动或故事事实已经人工核对。

## 可复核的 Mac 本地产物

- sydney-direct-vlm-compact-v03-20261105/LATEST_V03_8_OFFSETS_REAL_JPEG_REVIEW.html：最新统一网页，含八组所有章节正文及真实图库。
- 同目录 LATEST_V03_8_OFFSETS_SCOREBOARD.json：旧版与 V03 状态逐组对照。
- 同目录 LATEST_V03_EIGHT_GROUPS_QUALITY_AUDIT.json：时间跨度重叠和风险项。
- 同目录 offset_XXX/status.json、result.json、publish_envelope.json、attempt_audit：真实模型调用、结果、来源验证及费用记录。

原始模型回应及 JPEG 只在 Mac 本地保留，避免把个人潜在敏感图文上传到 GitHub；本次未部署线上云端服务。