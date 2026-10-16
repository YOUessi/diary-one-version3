# Codex V1.64 重复测试：运行矩阵与可追溯性

离线生成时间：2026-09-04T12:05:55.319099+00:00。算法基线仍为 V1.63；V1.64 是本轮评估记录版本。

## 阅读边界

- 分母是 **3 套真实素材**，每套计划重复 3 轮，共 9 个运行槽位；不是 9 个独立用户或 9 个独立素材样本。
- 仅汇总 pack_1～3/round_1～3；不纳入工具初始化失误归档。没有最终结果的调用失败不记为 0 Chapter / 0 Aha。
- HTTP 429 属于服务端请求限制/配额故障，不计为内容质量失败；其成功前置调用仍计入已知耗时与费用。
- 缺失 provider usage 的请求按未知处理，不能因为程序填了 0 token 就认定免费。费用为记录内费率快照估算，不是账单。
- 图片/事实复用只是核查线索，不自动判错；Chapter/Aha 数量不是质量分数。此处不作视觉质量或用户满意度结论。
- `RETURNED` / `COMPLETED_RESULT` 仅表示函数返回了结构化结果，不等于全部阶段成功，也不等于可发布；需同时检查 delivery、coverage 与每张卡的 publication_status。
- 上游观察请求失败造成的素材缺失、Writer 请求无响应和逐项 fallback 分开记录，不将这些差异归为纯模型随机性。普通字段降级可与完整素材覆盖并存。
- 正文字数按非空白 Unicode 字符计数，含标点；不是 token 数，也不是英文生产环境长度合同。

## 运行矩阵

| 素材包/轮次 | 状态/交付分类 | 可交付 Chapter / Aha | 素材/帧 | 本地准备秒 | 算法墙钟秒 | 调用/429 | 已知输入/输出 token | usage 未知调用 | 已知估算人民币 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 / 1 | FAILED_HTTP_429 / 无结果 | — / — | 20/74 | 117.65 | 88.29 | 8/3 | 66805/6074 | 3 | 0.019132 |
| 1 / 2 | COMPLETED_RESULT / 完整可交付 | 3 / 3 | 20/74 | 117.15 | 207.16 | 11/0 | 126167/15151 | 0 | 0.041652 |
| 1 / 3 | COMPLETED_RESULT / 降级可交付 | 3 / 3 | 20/74 | 116.96 | 321.38 | 11/0 | 121475/13430 | 1 | 0.038366 |
| 2 / 1 | COMPLETED_RESULT / 完整可交付 | 4 / 3 | 26/39 | 41.74 | 178.01 | 14/0 | 95118/13850 | 0 | 0.035043 |
| 2 / 2 | COMPLETED_RESULT / 完整可交付 | 4 / 3 | 26/39 | 40.21 | 203.18 | 15/0 | 101739/15079 | 0 | 0.037879 |
| 2 / 3 | COMPLETED_RESULT / 阻断，仅内部候选 | —（内部 2/3） | 26/39 | 40.05 | 304.15 | 13/0 | 85141/12299 | 1 | 0.031220 |
| 3 / 1 | FAILED_HTTP_429 / 无结果 | — / — | 56/74 | 45.37 | 91.11 | 20/12 | 48964/6838 | 12 | 0.017602 |
| 3 / 2 | COMPLETED_RESULT / 降级可交付 | 3 / 3 | 56/74 | 43.33 | 359.91 | 24/0 | 176044/27512 | 0 | 0.067675 |
| 3 / 3 | COMPLETED_RESULT / 完整可交付 | 1 / 3 | 56/74 | 42.96 | 339.85 | 22/0 | 165008/24191 | 0 | 0.061038 |

状态分布：`{"FAILED_HTTP_429": 2, "COMPLETED_RESULT": 7}`。
交付分类分布：`{"NO_RESULT": 2, "COMPLETE_DELIVERABLE": 4, "DEGRADED_DELIVERABLE": 2, "BLOCKED_INTERNAL_CANDIDATES": 1}`。
全部已尝试请求：138 次；已知 1120885 token；17 次 usage 未知；已知估算 ¥0.349605，另有 17 次费用未知。

## 可交付运行中的流程观察统计

主表只统计完整覆盖且可交付（含文案 fallback 降级）的运行；不纳入阻断内部候选、无结果失败及进行中运行。拒因计数可能一条提议对应多个原因，不能将拒因项数直接当提议数。以下长度只是观察值，不新增阻断规则。

| 包/轮 | 原生 Aha 提议/拒绝 | 最终 Aha 来源 | S10 正好三件且未比较/全部 S10 Chapter | Aha 正文>24/全部 Aha | Chapter 正文>48/全部 Chapter |
|---|---:|---|---:|---:|---:|
| 1/2 | 4/4 | DETERMINISTIC_EVENT_PEAK: 3 | 1/3 | 3/3 | 1/3 |
| 1/3 | 4/4 | DETERMINISTIC_EVENT_PEAK: 3 | 1/3 | 3/3 | 1/3 |
| 2/1 | 4/4 | DETERMINISTIC_EVENT_PEAK: 3 | 1/4 | 3/3 | 4/4 |
| 2/2 | 4/4 | DETERMINISTIC_EVENT_PEAK: 3 | 0/4 | 3/3 | 0/4 |
| 3/2 | 5/5 | DETERMINISTIC_EVENT_PEAK: 3 | 0/3 | 3/3 | 2/3 |
| 3/3 | 5/5 | DETERMINISTIC_EVENT_PEAK: 3 | 0/1 | 3/3 | 0/1 |

可交付结果 6 轮，来自 3 套素材。原生 Aha 提议已知 26 条，拒绝 26 条；未知提议总数的运行 0 轮。
最终 Aha 来源：`{"DETERMINISTIC_EVENT_PEAK": 18}`。
原生 Aha 拒因：`{"AHA_CONTRACT_INVALID": 14, "EVENT_KIND_NOT_INDEPENDENT_PEAK": 10, "EVENT_SALIENCE_TOO_LOW": 1, "EVENT_FACT_REFERENCE_INVALID": 1}`；详细原因：`{"aha.narrative_duty length is invalid": 14}`。
S10 正好三件且未比较 3/18 次，其中最终发布的 Chapter 3 个。各来源混合计数：Aha 正文 >24 字 18/18；Chapter 正文 >48 字 8/18；不能据此单独评价模型 Writer。

### Writer 来源分层

只统计可交付卡片。模板/fallback 不混入 MODEL_WRITER 写作长度分母。

| 正文来源 | Aha >24/全部 | Chapter >48/全部 |
|---|---:|---:|
| MODEL_WRITER | 15/15 | 6/14 |
| DETERMINISTIC_GROUNDED_FALLBACK | 3/3 | 2/4 |

### 交付与稳定性比较边界

- 包1R2：完整可交付；delivery=`READY_PRIMARY_COPY`，coverage=`COMPLETE`；Writer 来源 `{"MODEL_WRITER": 6}`；未解决素材 `无`。
- 包1R3：降级可交付；delivery=`READY_WITH_GROUNDED_COPY_FALLBACK`，coverage=`COMPLETE`；Writer 来源 `{"DETERMINISTIC_GROUNDED_FALLBACK": 6}`；未解决素材 `无`。
  比较混杂：`WRITER_REQUEST_FAILED_FALLBACK_IS_NOT_MODEL_WRITING; MIXED_OR_FALLBACK_COPY_COMPARE_MODEL_WRITER_SEPARATELY`。
- 包2R1：完整可交付；delivery=`READY_PRIMARY_COPY`，coverage=`COMPLETE`；Writer 来源 `{"MODEL_WRITER": 7}`；未解决素材 `无`。
- 包2R2：完整可交付；delivery=`READY_PRIMARY_COPY`，coverage=`COMPLETE`；Writer 来源 `{"MODEL_WRITER": 7}`；未解决素材 `无`。
- 包2R3：阻断，仅内部候选；delivery=`PIPELINE_BLOCKED`，coverage=`PARTIAL_UNRESOLVED`；Writer 来源 `{"MODEL_WRITER": 5}`；未解决素材 `10.jpg, 11.jpg, 12.jpg`。
  比较混杂：`INCOMPLETE_OBSERVATION_INPUT_DO_NOT_ATTRIBUTE_OUTPUT_DIFFERENCES_TO_RANDOMNESS; PERCEPTION_TRANSPORT_OR_PROVIDER_FAILURE`。
- 包3R2：降级可交付；delivery=`READY_WITH_GROUNDED_COPY_FALLBACK`，coverage=`COMPLETE`；Writer 来源 `{"MODEL_WRITER": 5, "DETERMINISTIC_GROUNDED_FALLBACK": 1}`；未解决素材 `无`。
  比较混杂：`MIXED_OR_FALLBACK_COPY_COMPARE_MODEL_WRITER_SEPARATELY`。
- 包3R3：完整可交付；delivery=`READY_PRIMARY_COPY`，coverage=`COMPLETE`；Writer 来源 `{"MODEL_WRITER": 4}`；未解决素材 `无`。

## 固定输入与版本核查

- 包 1：准备完成 3/3 轮；原始文件/顺序跨轮一致 `True`；标准化帧跨轮一致 `True`；文件实测哈希不匹配 0 个；实际结果策略一致 `True`（有结构化返回记录 2 份，不代表均可交付）。
- 包 2：准备完成 3/3 轮；原始文件/顺序跨轮一致 `True`；标准化帧跨轮一致 `True`；文件实测哈希不匹配 0 个；实际结果策略一致 `True`（有结构化返回记录 3 份，不代表均可交付）。
- 包 3：准备完成 3/3 轮；原始文件/顺序跨轮一致 `True`；标准化帧跨轮一致 `True`；文件实测哈希不匹配 0 个；实际结果策略一致 `True`（有结构化返回记录 2 份，不代表均可交付）。

策略以每份结果的 `result.decision_trace.runtime_policies` 为准；失败但未返回结果的运行只保留计划策略，不冒充已验证。

冻结快照纳入 40 个文件；冻结副本不匹配 0 个，当前仓库对应文件不匹配 0 个。已返回结果的实际策略记录 7 份、相互一致 `True`；全部运行计划策略一致 `True`。

## 每包端到端组成耗时

每轮分钟数 = 当轮本地标准化耗时 + 当轮算法墙钟耗时。不包括实验排队、人工等待；不是浏览器完整交互性能测试。失败轮是到失败为止的耗时，不能当作更快完成。

| 素材包 | R1 分钟 / 分类 | R2 分钟 / 分类 | R3 分钟 / 分类 |
|---|---|---|---|
| 1 | 3.43 / 无结果 | 5.41 / 完整可交付 | 7.31 / 降级可交付 |
| 2 | 3.66 / 完整可交付 | 4.06 / 完整可交付 | 5.74 / 阻断，仅内部候选 |
| 3 | 2.27 / 无结果 | 6.72 / 降级可交付 | 6.38 / 完整可交付 |

### 阶段份额（可交付的完整覆盖运行）

含 Writer 降级轮，失败等待也是真实耗时。耗时份额以这些运行的算法墙钟总和为分母，不含本地标准化；token/费用份额仅对已知 usage/估算费用求占比。

| 阶段 | 秒数合计 | 算法耗时份额 | 已知 token 份额 | 已知费用份额 |
|---|---:|---:|---:|---:|
| S04_PERCEPTION | 849.75 | 52.80% | 67.81% | 62.77% |
| S05_S07_STRUCTURE_PROPOSAL | 471.33 | 29.28% | 16.10% | 24.20% |
| S10_MEDIA_SELECTION | 89.39 | 5.55% | 13.14% | 9.10% |
| S11_WRITER_ATTEMPT_1 | 198.48 | 12.33% | 2.95% | 3.94% |

## 分阶段实测

阶段时长为该阶段调用耗时之和，不与本地抽帧时间混算；整个运行总时间使用独立墙钟记录。

| 包/轮 | 阶段 | 调用 | 已知耗时秒 | 已知输入/输出 token | usage 未知 | 已知估算人民币 |
|---|---|---:|---:|---:|---:|---:|
| 1/1 | S04_PERCEPTION | 7 | 87.97 | 66805/6074 | 2 | 0.019132 |
| 1/1 | S05_S07_STRUCTURE_PROPOSAL | 1 | 0.22 | 0/0 | 1 | 0.000000 |
| 1/2 | S04_PERCEPTION | 7 | 119.23 | 91833/8423 | 0 | 0.026409 |
| 1/2 | S05_S07_STRUCTURE_PROPOSAL | 1 | 61.44 | 13789/4845 | 0 | 0.009336 |
| 1/2 | S10_MEDIA_SELECTION | 2 | 13.33 | 15465/841 | 0 | 0.003581 |
| 1/2 | S11_WRITER_ATTEMPT_1 | 1 | 13.07 | 5080/1042 | 0 | 0.002325 |
| 1/3 | S04_PERCEPTION | 7 | 116.50 | 91833/8277 | 0 | 0.026190 |
| 1/3 | S05_S07_STRUCTURE_PROPOSAL | 1 | 57.01 | 13399/4362 | 0 | 0.008553 |
| 1/3 | S10_MEDIA_SELECTION | 2 | 12.64 | 16243/791 | 0 | 0.003623 |
| 1/3 | S11_WRITER_ATTEMPT_1 | 1 | 135.13 | 0/0 | 1 | 0.000000 |
| 2/1 | S04_PERCEPTION | 9 | 96.98 | 60596/7537 | 0 | 0.020395 |
| 2/1 | S05_S07_STRUCTURE_PROPOSAL | 1 | 51.74 | 13480/4023 | 0 | 0.008056 |
| 2/1 | S10_MEDIA_SELECTION | 3 | 14.23 | 16544/1028 | 0 | 0.004024 |
| 2/1 | S11_WRITER_ATTEMPT_1 | 1 | 15.02 | 4498/1262 | 0 | 0.002568 |
| 2/2 | S04_PERCEPTION | 9 | 103.75 | 60596/7519 | 0 | 0.020368 |
| 2/2 | S05_S07_STRUCTURE_PROPOSAL | 1 | 63.37 | 13357/4897 | 0 | 0.009349 |
| 2/2 | S10_MEDIA_SELECTION | 4 | 21.36 | 23296/1461 | 0 | 0.005686 |
| 2/2 | S11_WRITER_ATTEMPT_1 | 1 | 14.63 | 4490/1202 | 0 | 0.002476 |
| 2/3 | S04_PERCEPTION | 9 | 225.99 | 55248/6713 | 1 | 0.018357 |
| 2/3 | S05_S07_STRUCTURE_PROPOSAL | 1 | 59.10 | 13238/4268 | 0 | 0.008388 |
| 2/3 | S10_MEDIA_SELECTION | 2 | 9.13 | 13502/589 | 0 | 0.002909 |
| 2/3 | S11_WRITER_ATTEMPT_1 | 1 | 9.85 | 3153/729 | 0 | 0.001566 |
| 3/1 | S04_PERCEPTION | 19 | 90.82 | 48964/6838 | 11 | 0.017602 |
| 3/1 | S05_S07_STRUCTURE_PROPOSAL | 1 | 0.20 | 0/0 | 1 | 0.000000 |
| 3/2 | S04_PERCEPTION | 19 | 201.06 | 119151/15880 | 0 | 0.041693 |
| 3/2 | S05_S07_STRUCTURE_PROPOSAL | 1 | 126.04 | 27693/9185 | 0 | 0.017931 |
| 3/2 | S10_MEDIA_SELECTION | 3 | 19.80 | 24972/1334 | 0 | 0.005747 |
| 3/2 | S11_WRITER_ATTEMPT_1 | 1 | 12.90 | 4228/1113 | 0 | 0.002304 |
| 3/3 | S04_PERCEPTION | 19 | 212.23 | 119151/15911 | 0 | 0.041739 |
| 3/3 | S05_S07_STRUCTURE_PROPOSAL | 1 | 111.72 | 27906/7156 | 0 | 0.014920 |
| 3/3 | S10_MEDIA_SELECTION | 1 | 8.03 | 15160/458 | 0 | 0.002961 |
| 3/3 | S11_WRITER_ATTEMPT_1 | 1 | 7.73 | 2791/666 | 0 | 0.001418 |

## 逐轮成品及复用线索

### 包 1 · 第 1 轮

状态：`FAILED_HTTP_429`，无结果；delivery=`None` / coverage=`None`；源记录：`var/codex_v1_64_repeat_review/pack_1/round_1/codex_full_run.json`。

当前无可评估成品；不视为产出数量为零。

### 包 1 · 第 2 轮

状态：`COMPLETED_RESULT`，完整可交付；delivery=`READY_PRIMARY_COPY` / coverage=`COMPLETE`；源记录：`var/codex_v1_64_repeat_review/pack_1/round_2/codex_full_run.json`。

**CHAPTER 1：《林间小径与犬影》**（标题 7 字；正文 46 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

青石曲径穿密林，落叶铺地；一只棕白狗背对镜头缓步前行，树干涂白、红灯祈福，静谧中添了缕生趣。

素材：09ed75eff07f6aac0133ab3e542c4b3d.mp4, 6576b04fcedee8130e6c9d1650be78e0.mp4, c9a75a21437b5d5462cf39a8c0cbba28.mp4。标签：SETTING.OUTDOOR_NATURE, ACTIVITY.WALKING。

**CHAPTER 2：《古街水岸与石刻》**（标题 7 字；正文 45 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

青石巷道连着“禹贡古村”牌坊，沿河白墙映柳影，石阶旁“古越龍山”红字在绿意中显出岁月深痕。

素材：250b1bad4d5d8da24c53ebe4151bb7ab.mp4, 522e4d072f337def753aed8c7a94ed1c.mp4, 8a1e021316c7825618fc85ba70d5da7c.mp4, b719cb94a859f6662df605abfc7b0b43.mp4, d0d0dc192e11c9a244b79518023ffa1e.mp4。标签：ACTIVITY.CITY_WALK, SETTING.TRADITIONAL_HISTORIC_DISTRICT, CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE。

**CHAPTER 3：《市集烟火气》**（标题 5 字；正文 50 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

湿石街面摊贩错落，青菜瓜果铺展其上；橙灯笼下“衢州烤饼”招牌亮眼，冰柜边甜筒与食客身影勾勒日常温度。

素材：38b14f584a73d255b2dd64f74bf85158.mp4, 9efd85d7058904b564a37946fb5a4fc2.mp4, f1434c6d71a443e8641d1bab33fbbe0e.mp4。标签：CENTRAL_SUBJECT.FOOD_OR_DESSERT。

**AHA 1：《市场初见》**（标题 4 字；正文 35 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

灰衣人走过湿石街，菜摊上青豆黄瓜堆成小山，雨后地面反光映出人间烟火气。

素材：38b14f584a73d255b2dd64f74bf85158.mp4。标签：CENTRAL_SUBJECT.CRAFT_OBJECT。

**AHA 2：《犬影轻移》**（标题 4 字；正文 42 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

棕白狗背对镜头沿青石小路缓行，尾巴自然垂落，高树环抱的枯叶坡面，是林间最温柔的过客。

素材：6576b04fcedee8130e6c9d1650be78e0.mp4。标签：ACTIVITY.WALKING, SETTING.OUTDOOR_NATURE。

**AHA 3：《石刻微光》**（标题 4 字；正文 40 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

‘古越龍山’四字在湿润石阶旁鲜红醒目，绿苔覆阶，树影婆娑，仿佛时光在此停驻低语。

素材：b719cb94a859f6662df605abfc7b0b43.mp4。标签：ACTIVITY.CITY_WALK, SETTING.TRADITIONAL_HISTORIC_DISTRICT, CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE。

复用线索（需结合故事判断，不自动判错）：

- 《林间小径与犬影》 / 《犬影轻移》：共享素材 6576b04fcedee8130e6c9d1650be78e0.mp4；共享事实 2 条。
- 《古街水岸与石刻》 / 《石刻微光》：共享素材 b719cb94a859f6662df605abfc7b0b43.mp4；共享事实 1 条。
- 《市集烟火气》 / 《市场初见》：共享素材 38b14f584a73d255b2dd64f74bf85158.mp4；共享事实 1 条。

### 包 1 · 第 3 轮

状态：`COMPLETED_RESULT`，降级可交付；delivery=`READY_WITH_GROUNDED_COPY_FALLBACK` / coverage=`COMPLETE`；源记录：`var/codex_v1_64_repeat_review/pack_1/round_3/codex_full_run.json`。

**CHAPTER 1：《生活片段》**（标题 4 字；正文 70 字；来源 `DETERMINISTIC_GROUNDED_FALLBACK`；`STAGED_PREVIEW_VALIDATED`）

视频显示一座中式牌坊，横匾书有'種山鵝秀'，两侧立柱有竖排文字，下方为湿滑石板街面，有多人穿行、摊位及电动车，背景可见传统屋顶与红色遮阳棚。

素材：04179d4c3503adbfa13bf00bad1ffb39.mp4, 38b14f584a73d255b2dd64f74bf85158.mp4, f1434c6d71a443e8641d1bab33fbbe0e.mp4。标签：CENTRAL_SUBJECT.FOOD_OR_DESSERT。

**CHAPTER 2：《生活片段》**（标题 4 字；正文 40 字；来源 `DETERMINISTIC_GROUNDED_FALLBACK`；`STAGED_PREVIEW_VALIDATED`）

林间铺设石板步道，两侧覆盖落叶与低矮灌木，远处可见延伸路径及稀疏树林，环境幽静。

素材：09ed75eff07f6aac0133ab3e542c4b3d.mp4, 6576b04fcedee8130e6c9d1650be78e0.mp4, c9a75a21437b5d5462cf39a8c0cbba28.mp4。标签：SETTING.OUTDOOR_NATURE, ACTIVITY.WALKING。

**CHAPTER 3：《生活片段》**（标题 4 字；正文 37 字；来源 `DETERMINISTIC_GROUNDED_FALLBACK`；`STAGED_PREVIEW_VALIDATED`）

石碑上刻有红色汉字‘古越龍山’，立于绿树环绕的石阶旁，地面湿润，植被茂密。

素材：250b1bad4d5d8da24c53ebe4151bb7ab.mp4, 522e4d072f337def753aed8c7a94ed1c.mp4, 8a1e021316c7825618fc85ba70d5da7c.mp4, b719cb94a859f6662df605abfc7b0b43.mp4, f5840e15a65526b128c68a22385a5247.mp4。标签：ACTIVITY.CITY_WALK, SETTING.TRADITIONAL_HISTORIC_DISTRICT, CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE。

**AHA 1：《这一刻》**（标题 3 字；正文 88 字；来源 `DETERMINISTIC_GROUNDED_FALLBACK`；`STAGED_PREVIEW_VALIDATED`）

视频第一组帧显示多层横杆悬挂大量带红绳的木牌，部分为红色葫芦形装饰，背景为传统屋檐与绿树；第二组帧显示石桥台阶、石槽及水渠旁石凳，第三组帧为挂有红灯笼与红布条的树干，旁有香炉。

素材：09ed75eff07f6aac0133ab3e542c4b3d.mp4。标签：SETTING.OUTDOOR_NATURE, CENTRAL_SUBJECT.CRAFT_OBJECT。

**AHA 2：《这一刻》**（标题 3 字；正文 318 字；来源 `DETERMINISTIC_GROUNDED_FALLBACK`；`STAGED_PREVIEW_VALIDATED`）

Framew00_1500showsapersoningreyshirtwalkingpastparkedscootersandtricyclesonawetstonestreetbesideabuildingwithasignreading'……社区居民'(CommunityResidents);framesw00_4500andw00_7500showaroadsidevegetablestallwithpilesofproduceincludingtomatoes,greenbeans,bambooshoots,andpeachesdisplayedontraysandincontainersonstoneground.。

素材：38b14f584a73d255b2dd64f74bf85158.mp4。标签：CENTRAL_SUBJECT.CRAFT_OBJECT。

**AHA 3：《这一刻》**（标题 3 字；正文 37 字；来源 `DETERMINISTIC_GROUNDED_FALLBACK`；`STAGED_PREVIEW_VALIDATED`）

石碑上刻有红色汉字‘古越龍山’，立于绿树环绕的石阶旁，地面湿润，植被茂密。

素材：b719cb94a859f6662df605abfc7b0b43.mp4。标签：ACTIVITY.CITY_WALK, SETTING.TRADITIONAL_HISTORIC_DISTRICT, CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE。

复用线索（需结合故事判断，不自动判错）：

- 《生活片段》 / 《这一刻》：共享素材 38b14f584a73d255b2dd64f74bf85158.mp4；共享事实 0 条。
- 《生活片段》 / 《这一刻》：共享素材 09ed75eff07f6aac0133ab3e542c4b3d.mp4；共享事实 0 条。
- 《生活片段》 / 《这一刻》：共享素材 b719cb94a859f6662df605abfc7b0b43.mp4；共享事实 1 条。

### 包 2 · 第 1 轮

状态：`COMPLETED_RESULT`，完整可交付；delivery=`READY_PRIMARY_COPY` / coverage=`COMPLETE`；源记录：`var/codex_v1_64_repeat_review/pack_2/round_1/codex_full_run.json`。

**CHAPTER 1：《城市里的鹿影》**（标题 6 字；正文 52 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

一只鹿在红墙灰瓦的街角空地上踱步，黄车与行人匆匆而过；另一处草坡上长角鹿低头啃食，有人举着手机静静记录。

素材：06.jpg, 07.jpg, 08.jpg。标签：无。

**CHAPTER 2：《驼群穿行丘陵》**（标题 6 字；正文 52 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

开阔草地上多峰骆驼或立或食，双峰驼背上两个坐姿清晰可见；远处输电塔与山峦相映，它们正缓缓移动于天地之间。

素材：10.jpg, 12.jpg, 13.jpg。标签：SETTING.OUTDOOR_NATURE。

**CHAPTER 3：《夜市烟火人间》**（标题 6 字；正文 56 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

蓝橙餐车亮着灯，三名顾客驻足；金属桌上摆满烤肉、串烧与笑脸纸杯，一双手正用筷子夹起食物，暖光映照出深夜的烟火气。

素材：16.jpg, 19.jpg, 20.jpg。标签：CENTRAL_SUBJECT.FOOD_OR_DESSERT。

**CHAPTER 4：《车窗外的路景》**（标题 6 字；正文 50 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

车内视角掠过高速与乡道：混凝土护栏、红白楼群、阴云下的远山，后排乘客悄然举手，镜头随道路向田野延伸。

素材：VID_20240708_174945.mp4, VID_20240708_174950.mp4, VID_20240708_175943.mp4。标签：无。

**AHA 1：《相机静默守望》**（标题 6 字；正文 49 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

三台黑相机并排立于台阶，镜头对准远方，其中一台肩带印着‘EOS 70D’，仿佛在无声等待下一个瞬间。

素材：03.jpg。标签：CENTRAL_SUBJECT.CRAFT_OBJECT。

**AHA 2：《初遇城市鹿影》**（标题 6 字；正文 38 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

一只鹿在铺装空地缓步前行，背景是红墙灰瓦与黄色工程车，视角高悬如从车窗俯瞰。

素材：06.jpg。标签：无。

**AHA 3：《乡道上的红帐篷》**（标题 7 字；正文 45 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

车窗外笔直乡道两侧黄黑防撞柱林立，远处两顶红帐篷与白货车静候山前，阴云低垂如未启程的旅途。

素材：VID_20240708_185454.mp4。标签：ACTIVITY.CITY_WALK。

复用线索（需结合故事判断，不自动判错）：

- 《城市里的鹿影》 / 《初遇城市鹿影》：共享素材 06.jpg；共享事实 1 条。

### 包 2 · 第 2 轮

状态：`COMPLETED_RESULT`，完整可交付；delivery=`READY_PRIMARY_COPY` / coverage=`COMPLETE`；源记录：`var/codex_v1_64_repeat_review/pack_2/round_2/codex_full_run.json`。

**CHAPTER 1：《城市边缘的鹿影》**（标题 7 字；正文 37 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

长角鹿在中式建筑与工程车之间踱步，一人举手机拍摄，小鹿又悄然现身铺装路面。

素材：06.jpg, 08.jpg, 09.jpg。标签：无。

**CHAPTER 2：《荒原上的驼队》**（标题 6 字；正文 36 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

五只双峰驼在草地上吃草或休憩，其中一只背负两人，远处高压电塔与山峦并存。

素材：10.jpg, 12.jpg, 13.jpg。标签：SETTING.OUTDOOR_NATURE。

**CHAPTER 3：《夜市烟火气》**（标题 5 字；正文 35 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

蓝橙餐车前排起队伍，热锅烤肉摆满桌面，串烧淋酱、笑脸纸杯映着街灯闪烁。

素材：16.jpg, 19.jpg, 20.jpg。标签：CENTRAL_SUBJECT.FOOD_OR_DESSERT, SETTING.CAFE_OR_TEA_SHOP。

**CHAPTER 4：《车窗里的风景》**（标题 6 字；正文 41 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

高速路旁住宅楼渐远，乡间绿意中后排乘客微笑挥手，车内后视镜与屏幕默默记录旅程变迁。

素材：VID_20240708_174945.mp4, VID_20240708_174950.mp4, VID_20240708_175943.mp4。标签：无。

**AHA 1：《相机静默守望》**（标题 6 字；正文 37 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

三台黑胶单反并排立于矮墙，肩带印着EOS 70D，脚边是未被察觉的观者身影。

素材：03.jpg。标签：CENTRAL_SUBJECT.CRAFT_OBJECT。

**AHA 2：《初遇长角鹿》**（标题 5 字；正文 33 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

一只长角鹿踏过铺装空地，红黄建筑与黄色工程车作背景，行人驻足凝望。

素材：06.jpg。标签：无。

**AHA 3：《筷尖夹起暖意》**（标题 6 字；正文 41 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

金属火锅旁，一双手持筷子夹起食物，烤炉红碗与酸黄瓜相映，烟火气里是共享的片刻安宁。

素材：16.jpg。标签：SETTING.CAFE_OR_TEA_SHOP, CENTRAL_SUBJECT.CRAFT_OBJECT。

复用线索（需结合故事判断，不自动判错）：

- 《城市边缘的鹿影》 / 《初遇长角鹿》：共享素材 06.jpg；共享事实 1 条。
- 《夜市烟火气》 / 《筷尖夹起暖意》：共享素材 16.jpg；共享事实 1 条。

### 包 2 · 第 3 轮

状态：`COMPLETED_RESULT`，阻断，仅内部候选；delivery=`PIPELINE_BLOCKED` / coverage=`PARTIAL_UNRESOLVED`；源记录：`var/codex_v1_64_repeat_review/pack_2/round_3/codex_full_run.json`。

以下仅为内部诊断候选，不是发布完成的成品；上游观察缺失混杂，不能按相同输入完整模型结果比较。

**CHAPTER 1：《鹿影穿行古今街巷》**（标题 8 字；正文 42 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_DIAGNOSTIC_ONLY`）

长角鹿在铺装院落中踱步，身后是红黄装饰的中式建筑与远山，仿佛自然悄然闯入了历史肌理。

素材：02.jpg, 06.jpg, 07.jpg。标签：无。

**CHAPTER 2：《车窗内外的路途变迁》**（标题 9 字；正文 48 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_DIAGNOSTIC_ONLY`）

高速公路上空旷车道延伸向远方，乡间路旁红帐篷与路障渐次浮现，车中屏幕映着地图，时光在视野里流动。

素材：VID_20240708_174945.mp4, VID_20240708_174950.mp4, VID_20240708_185454.mp4。标签：无。

**AHA 1：《街巷惊鹿》**（标题 4 字；正文 32 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_DIAGNOSTIC_ONLY`）

一只长角鹿在铺装院落中行走，背景是红黄装饰的中式建筑与远处山丘。

素材：06.jpg。标签：ACTIVITY.CITY_WALK, SETTING.TRADITIONAL_HISTORIC_DISTRICT, CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE。

**AHA 2：《夜市烟火》**（标题 4 字；正文 38 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_DIAGNOSTIC_ONLY`）

金属桌上串类食物淋着红酱，旁边纸杯印着笑脸，远处摊灯与车流在夜色里轻轻晃动。

素材：20.jpg。标签：CENTRAL_SUBJECT.FOOD_OR_DESSERT。

**AHA 3：《后座微笑》**（标题 4 字；正文 37 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_DIAGNOSTIC_ONLY`）

后排黑衣男子抬手微笑，车窗外绿意与远山掠过，后视镜里映出他笑意融融的瞬间。

素材：VID_20240708_175943.mp4。标签：无。

复用线索（需结合故事判断，不自动判错）：

- 《鹿影穿行古今街巷》 / 《街巷惊鹿》：共享素材 06.jpg；共享事实 1 条。

### 包 3 · 第 1 轮

状态：`FAILED_HTTP_429`，无结果；delivery=`None` / coverage=`None`；源记录：`var/codex_v1_64_repeat_review/pack_3/round_1/codex_full_run.json`。

当前无可评估成品；不视为产出数量为零。

### 包 3 · 第 2 轮

状态：`COMPLETED_RESULT`，降级可交付；delivery=`READY_WITH_GROUNDED_COPY_FALLBACK` / coverage=`COMPLETE`；源记录：`var/codex_v1_64_repeat_review/pack_3/round_2/codex_full_run.json`。

**CHAPTER 1：《城郊路与校门的夜色转换》**（标题 11 字；正文 49 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

白昼路边的绿植与护栏，悄然过渡到夜幕下写有‘苏州大学’的牌匾和‘中国人民大学苏州校区’的砖墙标识。

素材：No.1/照片/1.jpg, No.1/照片/13.jpg, No.1/照片/14.jpg。标签：无。

**CHAPTER 2：《生活片段》**（标题 4 字；正文 52 字；来源 `DETERMINISTIC_GROUNDED_FALLBACK`；`STAGED_PREVIEW_VALIDATED`）

从看台视角拍摄的大型体育场内景，场地上有人员聚集于红色拱门附近，观众席坐满，顶部灯光开启，跑道环绕球场。

素材：No.1/照片/10.jpg, No.1/照片/11.jpg, No.1/照片/2.jpg, No.1/照片/3.jpg, No.1/照片/5.jpg。标签：无。

**CHAPTER 3：《雪夜林径上的三道身影》**（标题 10 字；正文 45 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

头灯映着积雪松林，三人围在写有‘通告’的白牌前比划，一人蹲在带刺铁丝网旁，登山杖斜插雪地。

素材：No.3/照片/5.jpg, No.3/照片/7.jpg, No.3/照片/8.jpg。标签：SETTING.OUTDOOR_NATURE。

**AHA 1：《终场哨响时的比分定格》**（标题 10 字；正文 51 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

大型电子记分牌显示‘新迪元2034杯’U12总决赛6:2，下半场时间60:00，亚洲明德联胜杭州足健。

素材：No.1/照片/10.jpg。标签：CENTRAL_SUBJECT.FOOD_OR_DESSERT。

**AHA 2：《紫衣少年手捧金杯的瞬间》**（标题 11 字；正文 38 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

一群穿浅紫色球衣的男孩站在红跑道上，一人高举金色奖杯，多人佩戴橙色挂绳证件。

素材：No.1/照片/11.jpg。标签：CENTRAL_SUBJECT.CRAFT_OBJECT, OCCASION.BIRTHDAY。

**AHA 3：《金殿匾额下的香火长明》**（标题 10 字；正文 37 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

金色屋顶的中式殿堂正面特写，门楣‘金殿’二字醒目，门前石栏挂满锁具与香炉。

素材：No.3/照片/12.jpg。标签：ACTIVITY.CITY_WALK, SETTING.TRADITIONAL_HISTORIC_DISTRICT, CENTRAL_SUBJECT.FOOD_OR_DESSERT。

复用线索（需结合故事判断，不自动判错）：

- 《生活片段》 / 《终场哨响时的比分定格》：共享素材 No.1/照片/10.jpg；共享事实 0 条。
- 《生活片段》 / 《紫衣少年手捧金杯的瞬间》：共享素材 No.1/照片/11.jpg；共享事实 0 条。

### 包 3 · 第 3 轮

状态：`COMPLETED_RESULT`，完整可交付；delivery=`READY_PRIMARY_COPY` / coverage=`COMPLETE`；源记录：`var/codex_v1_64_repeat_review/pack_3/round_3/codex_full_run.json`。

**CHAPTER 1：《山巅金殿与晨昏旗影》**（标题 9 字；正文 43 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

观景台处一人持国旗迎日出日落，山岩上金殿群巍然矗立，锁链祈福牌与香炉映衬着传统仪式感。

素材：No.3/照片/10.jpg, No.3/照片/11.jpg, No.3/照片/12.jpg, No.3/照片/13.jpg, No.3/照片/15.jpg。标签：SETTING.OUTDOOR_NATURE, CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE。

**AHA 1：《颁奖时刻》**（标题 4 字；正文 37 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

少年球员手持金色奖杯立于红跑道，浅紫球衣与橙色挂绳在室内体育场中格外醒目。

素材：No.1/照片/11.jpg。标签：CENTRAL_SUBJECT.CRAFT_OBJECT, OCCASION.BIRTHDAY。

**AHA 2：《礼花飞溅》**（标题 4 字；正文 33 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

金色礼花从天而降洒落红台前，人群举手欢呼，烟雾缭绕中定格荣耀瞬间。

素材：No.1/照片/6.jpg。标签：无。

**AHA 3：《金殿门楣》**（标题 4 字；正文 35 字；来源 `MODEL_WRITER`；`STAGED_PREVIEW_VALIDATED`）

蓝底金字‘金殿’悬于雕花门楣，香炉锁链静置阶前，殿内神像轮廓隐约可见。

素材：No.3/照片/12.jpg。标签：ACTIVITY.CITY_WALK, SETTING.TRADITIONAL_HISTORIC_DISTRICT, CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE。

复用线索（需结合故事判断，不自动判错）：

- 《山巅金殿与晨昏旗影》 / 《金殿门楣》：共享素材 No.3/照片/12.jpg；共享事实 1 条。

## 完整机器可读记录

`var/codex_v1_64_repeat_review/codex_summary.json` 包含实际策略、逐调用 usage/费用、原始记录路径、卡片事实引用和哈希检查结果。未新增任何运行时语义规则。
