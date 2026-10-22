# 算法质量门与当前未完成项

更新日期：2026-10-18。本页替代旧的“代码已齐”“Search Agent 已上线”等过宽结论。完整依据和 53 条需求见 [最终 PRD 与算法核查](最终核查_PRD与算法_2026-10-18.md)。

## 当前状态

- BFF/Worker/X02 本轮修改已部署 `v2-20261018T132121Z`，mock=false。
- 真生成被千问 API Key 权限 HTTP 403 阻塞；health 绿不等于能调用模型。
- X02 仍为 STAGED_PREVIEW，production_ready=false；S13 HQ 导出未执行，不能称商用终态。
- App 仍有完整引用/摘要准入、去重账本提交时序、来源、未知时间、小记忆留存/历史等问题，见 B03–B07。
- 基础搜索按 PRD SEA01–03 为本地词匹配；当前 SearchScreen 不使用 searchAgent.ts 的摘要，不交接成问答 Agent 或语义搜索。
- Topics 是 tag/title 启发式聚类；偏好云端软引导已具备，但 App 默认不上传，未经授权不要开启。
- Writer 当前为 zh-Hans 测试上下文，App 语言选择尚未驱动完整生成语言合同。
- Pillow 插画滤镜、拼图、ffmpeg Recap 不等于三种分享均达到 PRD 质量要求。

## 最小验证顺序

1. 修复供应商权限，保留服务器 release/备份；不要改供应商模型来掩盖未经评审的差异。
2. 修复最终核查 P0，执行现有测试及错误 manifest、未知引用、持久化失败、未知日期、增量小记忆用例。
3. EAS iOS 原生构建与 Vision 实机验证；仅用用户主动选择并同意的照片和视频跑实际 BFF 链路。
4. 留输入摘要、算法/模型/合同版本、成本、失败和重开证据，人工核查事实、重复高光、选图、文案和语言。
5. 对真实 Redis/Worker 故障和回复丢失做隔离恢复演练。不得拿单次 fixture 或单测通过代替真实内容质量。

本次复查算法 311 passed、25 skipped、104 subtests passed；BFF 41 passed。跳过项未验收。完整真实生成仍未通过，不应将测试数字写为商用质量签字。
