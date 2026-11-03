## R5_26 全部偏移组真实云端运行（2026-11-04）

- [0s 与 80s 已发布版本及质量对照](SYDNEY_R526_0_80_FULL_PUBLICATION_20261103.md)
- [剩余10个偏移组的完整实测、发布标题、图文质量和失败恢复](SYDNEY_R526_OTHER_10_OFFSETS_ACTUAL_CLOUD_RESULTS_20261104.md)
- [剩余10组 R5_25 / R5_26 定量对照 CSV](SYDNEY_R526_OTHER_10_OFFSETS_VS_R525_20261104.csv)
- [已脱敏的机器可读取审计 JSON](SYDNEY_R526_OTHER_10_OFFSETS_PUBLIC_SUMMARY_20261104.json)

十组均产出真实最终result.json，但并不等于质量达标：10s为PIPELINE_BLOCKED；
110s错误将视频片尾的推广界面作为单独Chapter；30s/60s需通用安全合同修复才可发布。
本批分三份代码冻结来源：8组c806114、30s安全修复6b6e575、60s再修复8e533cc；
修复均已合入当前特性分支。需要同一合并源码SHA的严格可比性时应再独立复跑。

Mac本地实际图像对照：sydney-offset-sweep-r525-20261103/r526_other_10_groups_real_publication_comparison.html
（这份含真实JPG的页面不会上传GitHub）

# Diary One Chapter 评测资料

## 有效、按用户反馈修正的参考

- [Sydney R5_25 12组场景优先检查、歌剧院漏选分析和逐组结果](SYDNEY_R525_CORRECTED_SCENE_FIRST_AND_OPERA_AUDIT_20261103.md)
- [修正版指标 CSV](SYDNEY_R525_CORRECTED_SCENE_FIRST_BENCHMARK_V2.csv)
- [修正版指标 JSON](SYDNEY_R525_CORRECTED_SCENE_FIRST_BENCHMARK_V2.json)
- [12组相对源时间及JPG帧标识参考](SYDNEY_R525_USER_CORRECTED_REFERENCE_12_GROUPS_V2.json)

参考基于人工80s九个原始场景与12组真实JPG；最后重复出现的歌剧院**不作为必需的新章节**。一组最终4–5章均可接受，只要体验完整性成立。

## 已撤回的历史基准

首版 [12组报告](SYDNEY_R525_12_OFFSET_CHAPTER_COMPARISON_20261103.md)、同名旧 CSV/JSON 的“歌剧院结尾必须独立成章”和相关IoU/9段覆盖评价**已撤回**，只用于历史追溯。

## 隐私

真实原始 MP4、私有 API 收据及整组图片仅保留用户Mac本地，GitHub收录的只有说明、可重复计算的指标和来源片段/帧ID。
