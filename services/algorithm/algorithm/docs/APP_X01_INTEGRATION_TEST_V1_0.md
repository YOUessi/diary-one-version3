# Diary One — App 联调与 X01 测试逻辑 V1.0

**文档状态：** 当前联调基线  
**整理日期：** 2026-08-19  
**适用版本：** RC13 iOS Sandbox + Cloud E00 + X01 Diary Research Preview V01  
**性质：** `E00 = ENGINEERING SMOKE`；`X01 = EXPERIMENTAL / NOT LEADERBOARD`  
**算法上位规则：** [CANONICAL_PROCESSING_RULES_V1_0.md](CANONICAL_PROCESSING_RULES_V1_0.md)

本文回答四个问题：

1. App 中任意尺寸、任意时长的相册图/视频，如何变成可复现的算法 Evidence；
2. E00、X01、Mock、通用 Remote V0.3 分别在验证什么；
3. iPhone、Mac 网关、Qwen 与 Diary Home 之间怎样联调；
4. 每一轮测试应如何选素材、看结果、记录错误和推进下一阶段。

本文不会把 X01 的临时实现写成冻结产品事实，也不会把一次成功请求解释为算法质量已经成立。

---

## 1. 项目与责任边界

| 范围 | 当前目录 | 责任 |
|---|---|---|
| 云端算法研究 | `diary-one-cloud-intelligence/` | E00、X01、Schema、模型 Adapter、Artifact、Trace、评测 |
| 正式 App 的临时算法 Sandbox | `device-gates/DiaryOne-RC13-Candidate-20260818/DiaryOne-iOS-Sandbox/` | 相册导入、固定 Test Session、Evidence 生成、上传、结果准入、Diary 展示 |
| 硬件 SDK 诊断 | `development/ios-sdk/QCSDKDemo/` | 蓝牙、Wi-Fi、设备协议与硬件能力验证 |

硬件 SDK 项目不承载正式 App、账号、相册、云端或 AI 产品逻辑。只有稳定验证过的硬件能力，才通过显式 device-capability 接口交给正式 App。

### 1.1 当前 App 与云端的责任划分

App 负责：

- 用户选择 `PHOTO_LIBRARY_TEST` 素材；
- 把一次选择固化成不可变 Test Session；
- 在手机本地生成统一 Evidence；
- 保存源素材 provenance、Evidence 身份和 bundle hash；
- 发起健康检查和 Evidence-only 请求；
- 对远端结果做严格准入校验；
- 追加 Processing Run，并在原生 Diary UI 中展示。

云端研究代码负责：

- 验证 bundle、frame、hash 与引用完整性；
- 调用选定的模型 Adapter；
- 形成实验性 Observation / Moment / Chapter / Aha；
- 执行置信度、证据引用、去重、数量和文本长度 Gate；
- 记录模型、请求、时延、token、成本和传输 Trace；
- 返回版本化、可审计的结果。

---

## 2. 四条路径必须严格区分

| 路径 | 输入 | 处理 | 输出用途 | 是否真实模型 | Leaderboard |
|---|---|---|---|---|---|
| Mock | 固定 Test Session | App 内确定性模拟 | 验证 UI、归档、状态机 | 否 | 否 |
| Remote V0.3 | 原始 Test Session 媒体 | 当前 FastAPI stub / 通用适配器 | 验证旧开发传输合同 | 当前不是实算法 | 否 |
| E00 | 标准实验 bundle 或 App Library bundle | Probe、逻辑 Asset、3 Frames、占位 Embedding、Smoke Moment、EVAL/Trace/Report | 验证工程闭环与 Artifact | 否 | 明确禁止 |
| X01 | App Library normalized Evidence | Qwen + 本地严格 Gate | 在 Diary Home 预览 Chapter/Aha/Empty | 是 | 明确禁止 |

### 2.1 不能混用的结论

- Mock 成功只证明 App UI/归档链路工作。
- Remote V0.3 成功只证明通用 multipart 与 V0.3 合同工作；当前 stub 不证明云端视觉算法工作。
- E00 成功只证明 Smoke Path 可追溯、可复现；placeholder embedding 与两两分组没有算法意义。
- X01 成功证明 Evidence → live model → strict validation → Diary 的实验闭环；它不证明 E01 基线、Production backend 或用户价值成立。
- X01 返回 `EMPTY_DAY` 是合法算法结果，不是请求失败。

---

## 3. 当前端到端联调图

```text
iPhone Photos Picker
  ↓
固定 Test Session / ImportBatch
  ↓
本地读取任意尺寸、任意时长图像或视频
  ↓
生成 768×1024、portrait 3:4 JPEG Evidence
  ↓
每个 Asset 固定 3 个 canonical frame slot
  ↓
DIARY_ONE_APP_LIBRARY_BUNDLE_V01
  ├─ bundle.json / manifest
  ├─ normalized JPEG frames
  └─ source provenance only; no originals
  ↓
GET /health（TLS + bearer + certificate pinning）
  ↓ modelReady=true
POST /x01/v0.1/preview（Evidence-only multipart）
  ↓
Mac X01 Gateway
  ↓
Qwen Adapter
  ↓
本地 Schema / Evidence / Precision Gates
  ↓
DIARY_ONE_X01_PREVIEW_V01
  ↓
iOS X01 validation + common DiaryResult validation
  ↓
append-only Processing Run
  ↓
Diary Home：Chapter / Aha / Empty Day
```

---

## 4. 固定 Test Session 规则

一次 Test Session 是一次不可变 Evidence 集合：

```text
同一 Test Session + algorithm vA → Run A
同一 Test Session + algorithm vB → Run B
素材集合变化                     → 新 Test Session
```

### 4.1 为什么必须固定

- 同一批证据才能比较算法版本；
- 失败重试不能悄悄换素材；
- App、bundle、云端结果可以通过 session ID、asset ID、fingerprint/hash 对齐；
- 历史 Run 只追加，不覆盖，便于比较质量、成本与时延。

### 4.2 并发与状态保护

导入、bundle 生成或算法处理进行中时，App 必须阻止会改变证据集的操作，包括：

- 再次导入；
- 切换、删除或清空当前 Session；
- 切换处理 Adapter；
- 并发发起第二个 Run；
- 在旧请求返回前让另一个 Session 接收其结果。

处理前应快照当前固定 Session；返回后再次核对 Session 身份。身份变化时结果必须拒绝，不能显示到错误的一天。

---

## 5. 任意相册素材如何标准化

当前 App Library 路径的目标是让用户无需事先拥有 3:4 或恰好 9 秒的素材。

### 5.1 输入兼容性

允许：

- 任意常见照片尺寸与横竖方向；
- 任意正时长视频，不要求恰好 9 秒；
- 同一 Session 混合图片和视频；
- capture time 缺失的测试素材，但必须保留“缺失”事实。

这条兼容路径是研究输入桥，不代表正式 wearable capture 的 Benchmark 数据分布。

### 5.2 统一画面

每个 Evidence frame 在 App 本地生成：

- 输出尺寸：`768 × 1024`；
- 方向：portrait；
- 比例：`3:4`；
- 几何策略：center-crop + aspect-fill；
- 编码：JPEG；
- 当前质量参数：`0.84`。

标准化不得篡改以下 provenance：

- 原始 asset ID；
- 原始 capture time（如可获取）；
- 原始媒体类型；
- 原始像素宽高；
- 原始视频时长；
- 原始文件字节数；
- 原始内容 hash；
- Evidence 是怎样从原始素材派生的。

### 5.3 照片的三个 Evidence slot

照片没有真实视频时间轴。当前兼容策略是把同一张标准化静态图写入三个 canonical slot：

```text
canonical 1.5 s → same normalized still
canonical 4.5 s → same normalized still
canonical 7.5 s → same normalized still
```

模型和评测必须知道源类型是 `PHOTO`，不能把三个重复 frame 当作三个动作阶段。

### 5.4 任意时长视频的三个 Evidence slot

对真实时长为 `D` 的视频，App 在源时间轴抽取：

```text
source timestamp 1 = D × 1/6  → canonical slot 1.5 s
source timestamp 2 = D × 1/2  → canonical slot 4.5 s
source timestamp 3 = D × 5/6  → canonical slot 7.5 s
```

源时间戳与 canonical slot 都要写入 manifest。这样短视频和长视频都能进入同一 Evidence 合同，同时仍可追溯回真实源位置。

### 5.5 逻辑时间轴

- 有 capture time：相对最早 capture time 计算 timeline offset；
- 无 capture time：当前兼容 fallback 为 picker 顺序 `index × 120 s`；
- fallback 是实验性排序手段，不得伪装成真实拍摄时间；
- Production 的 timezone / local-day 语义仍是待冻结合同。

### 5.6 Bundle 完整性

App Library bundle 必须满足：

- schema 为 `DIARY_ONE_APP_LIBRARY_BUNDLE_V01`；
- `research_only=true`；
- 每个 Asset 恰好三个 Evidence frame；
- frame ID 全局唯一；
- manifest 中引用的每个文件都位于 bundle 内；
- 原始媒体文件和 materialized 9 秒视频都不在 bundle 内；
- `bundle.json` 最后写入，作为原子完成标记；
- 失败时清理不完整临时产物；
- bundle 和关键 Artifact 具备内容 hash。

---

## 6. E00 在 App 中怎样测试

E00 的作用是先证明数据和工程链路，不判断 Chapter/Aha 质量。

### 6.1 App 操作

1. 打开 `Device` → `Developer Tools`。
2. 在 `Cloud E00 Smoke Test` 区域选择相册图片或视频。
3. 首次建议选同一天、同一活动的 `4–12` 项；素材尺寸和时长不限。
4. 点击 `Prepare Cloud E00 Bundle`。
5. 已有固定 Session 时，可点击 `Prepare Current Session Bundle` 重用相同证据。
6. 需要离线检查时，点击 `Share Cloud E00 Bundle` 导出给 Mac。

### 6.2 Mac 侧 E00 应验证

```text
Bundle validation
→ source/provenance probe
→ logical asset mapping
→ canonical frame references
→ deterministic placeholder embedding
→ smoke moment grouping
→ EVAL_V01 minimum evaluation
→ transfer/cost trace
→ content-addressed artifacts
→ HTML report
```

### 6.3 E00 成功标准

- bundle 可校验且 hash 稳定；
- manifest 与所有 frame 一一对应；
- `originals_uploaded=0`；
- 每次相同输入得到相同逻辑对象与 Artifact hash；
- trace 和 report 完整；
- 明确标记 `leaderboard_eligible=false`；
- 不产生或宣称真实 Chapter/Aha 质量。

---

## 7. X01 在 App 中怎样联调

X01 复用 E00 已准备好的 normalized Evidence，不重复导入，也不上传原图/原视频。

### 7.1 前置条件

- Mac 上 X01 服务已启动；
- Qwen API key 仅存在 Mac 登录钥匙串或服务进程环境中；
- iPhone 不保存 Qwen API key；
- iPhone 与 Mac 当前研究环境网络可达；
- 非 loopback 服务必须使用 TLS、测试 bearer 和 App 内证书 pinning；
- App 已生成当前固定 Session 的 Cloud E00 bundle；
- 素材数量不超过 `/health` 返回的 `maxAssets`，当前服务上限为 24。

### 7.2 App 操作顺序

1. 在 Developer Tools 中确认当前 Test Session 正确。
2. 若尚无 bundle，先点 `Prepare Cloud E00 Bundle`。
3. 在 `X01 Chapter / Aha Preview` 填写已配对的 Mac X01 地址。
4. 点击 `Check X01 Server`。
5. 只有状态显示 `Ready · provider / model · up to N items`，生成按钮才应启用。
6. 点击 `Generate on Diary Home`。
7. 等待上传、模型调用和双层合同校验。
8. 成功后 App 自动追加新 Run，关闭 Developer Tools，并切换到 Diary Home。
9. 结果可能是 Chapter、Aha 或合法 `EMPTY_DAY`。

### 7.3 不得省略健康检查

App 对当前输入的精确 endpoint 做健康检查。编辑 endpoint 后，之前的 Ready 状态必须失效，不能沿用旧地址的验证结果。

健康检查至少确认：

- HTTP 状态成功；
- `status=ok`；
- schema 精确为 `DIARY_ONE_X01_PREVIEW_V01`；
- provider 与 model 非空；
- `modelReady=true`；
- `maxAssets` 可接受当前 Session。

---

## 8. X01 研究 API

### 8.1 健康检查

```http
GET /health
Accept: application/json
Authorization: Bearer <research-transport-token>
```

关键响应语义：

```json
{
  "status": "ok",
  "schemaVersion": "DIARY_ONE_X01_PREVIEW_V01",
  "provider": "qwen",
  "model": "qwen3-vl-flash-2026-01-22",
  "modelReady": true,
  "maxAssets": 24
}
```

文档与日志中不得记录真实 API key、真实 bearer token、私钥或完整证书 pin。

### 8.2 生成请求

```http
POST /x01/v0.1/preview
Content-Type: multipart/form-data; boundary=...
Accept: application/json
Authorization: Bearer <research-transport-token>
```

multipart 只包含：

- bundle manifest；
- manifest 声明的 normalized JPEG Evidence frames。

明确不包含：

- 原始照片；
- 原始视频；
- materialized 9 秒视频；
- Qwen API key。

当前服务器请求体上限为 128 MB，最多 24 个 logical assets。App 当前交互请求超时为 300 秒；这只是研究联调参数，不是 Production SLA。

### 8.3 返回合同

返回 `DIARY_ONE_X01_PREVIEW_V01`，主要包含：

- session 与 bundle hash；
- observations；
- local moments；
- Chapters；
- Aha；
- output mode；
- Evidence-backed claims；
- provider/model/request/token/cost/latency trace；
- `experimental=true`；
- `leaderboard_eligible=false`；
- `originals_uploaded=0`。

---

## 9. X01 云端处理与 Gate

### 9.1 当前模型输入选择

- bundle 中每个 Asset 保留三个 Evidence frame；
- 当前模型输入首先取每个 Asset 的中间 frame；
- VIDEO 可增加额外 frame 以补充时间变化；
- 默认模型帧预算为 48；至少保证每个 Asset 一个中间 frame，且该预算可通过研究环境配置；
- 这是 X01 实验策略，不是冻结的 Observation/Temporal 理解策略。

### 9.2 当前默认模型

- Provider：Alibaba Cloud Model Studio；
- Adapter：OpenAI-compatible Chat Completions；
- 默认 snapshot：`qwen3-vl-flash-2026-01-22`；
- Qwen 是 X01 当前默认研究模型，不是 Production 供应商冻结结论；
- fixture 只能用于确定性合同测试，不可作为用户可见 Diary 结果；
- OpenAI adapter 只作为显式 cross-vendor challenger，不是静默 fallback。

### 9.3 本地严格校验

模型 JSON 永远按不可信输入处理。云端本地 Gate 至少执行：

- Chapter confidence `≥ 0.76`；
- Aha confidence `≥ 0.84`；
- Chapter 最多 4 个；
- Aha 最多 3 个；
- 当前 Aha hero 必须为 PHOTO；
- 已选 Chapter 不能共享 underlying asset moments；
- Chapter/Aha token Jaccard `≥ 0.72` 时视为语义重复并抑制；
- claim 仅允许 `OBSERVED` 或 `DERIVED`；
- 每条 claim 必须引用已知、且属于该候选 Asset 的 frame ID；
- 未知引用、越权引用、重复 ID、无效 ledger 直接拒绝；
- title 最长 100 字符；
- story 最长 700 字符；
- time label 最长 80 字符；
- tags 最多 4 个；
- 有 Chapter 时为 `CHAPTER_DAY`；无 Chapter 且有 Aha 时为 `HIGHLIGHT_DAY`；两者均无时为 `EMPTY_DAY`。

这些 confidence 是模型自评分的实验硬门槛，不是校准概率，也不是正式产品阈值。

### 9.4 当前已知规则差异

冻结规则要求：

```text
HIGHLIGHT_DAY = 0 Chapter + exactly 1 strong Aha
```

当前 X01 代码在无 Chapter 时仍可能选出最多 3 个 Aha。这是明确 `GAP`，后续必须修正或通过显式架构决策重开；当前结果不能据此改写冻结定义。

---

## 10. iOS 返回结果准入

云端 Gate 通过后，App 仍要再次验证。任何一层失败都不能把结果写进 Diary。

### 10.1 X01 专属检查

- schema 与 experiment 标识精确匹配；
- `experimental=true`；
- `leaderboard_eligible=false`；
- session ID 与当前固定 Session 一致；
- bundle hash 有效；
- Chapter/Aha 数量不超过限制；
- output mode 与对象集合一致；
- pipeline version 为 X01 V01；
- `originals_uploaded=0`；
- model calls 大于 0；
- provider/model 已记录且 provider 不是 fixture。

### 10.2 通用 DiaryResult 检查

- 返回 Asset ID 与提交证据严格匹配；
- Evidence fingerprint 不变；
- Moment/Chapter ID 唯一；
- Moment、Chapter、hero 和 timeline 引用都能解析；
- Chapter 顺序和覆盖关系一致；
- trace 的数量、时延与成本值合理；
- `PHOTO_LIBRARY_TEST` 不被伪装成硬件捕获来源；
- 用户自己写的 `What you remember` 不被 AI story 覆盖。

### 10.3 当前 App 映射近似

X01 返回的一个多 Asset Moment，当前会映射为 App 中逐 Asset 的 Moment 对象以适配既有 UI 数据结构。这是联调近似，不是 Production Moment 数据模型。

---

## 11. Diary Home 应看到什么

### 11.1 Chapter Day

- 1–4 个 Chapter；
- 可同时有 0–3 个独立 Aha；
- 每个可见对象必须能追溯到提交 Evidence；
- 页面显示 `X01 EXPERIMENTAL · NOT LEADERBOARD` 标记。

### 11.2 Highlight Day

- 0 个 Chapter；
- 冻结产品定义要求恰好 1 个 strong Aha；
- X01 当前存在上文所列数量 GAP。

### 11.3 Empty Day

- 0 Chapter；
- 0 Aha；
- Diary 显示 `No qualifying memory`；
- 这表示 Evidence 未达到当前高置信 Gate，是合法成功结果。

---

## 12. 第一次测试应该选多少素材

### 推荐：4–12 项

首轮不要随机混合整个月。选择同一天、同一个可描述活动的 4–12 张图/视频，例如：

- 到达咖啡馆；
- 坐下工作；
- 桌面、电脑、饮品；
- 与同行者互动；
- 离开或场景变化。

建议至少包含：

- 2–4 张能明确说明主活动的照片；
- 1–3 段有明显动作或变化的视频；
- 1–3 张邻近上下文图；
- 横图、竖图和不同视频时长各至少一项，用于兼容性检查。

数量越多并不等于质量越高。若素材跨多个无关日期、地点或事件，先拆成多个固定 Session，避免把“错误合并”混入首轮联调。

---

## 13. 分阶段测试矩阵

| 阶段 | 素材设计 | 目标输出 | 主要验证 | 通过条件 |
|---|---|---|---|---|
| T0 Bundle | 1 图、1 短视频、1 长视频、横竖混合 | 不看记忆 | 任意媒体标准化 | 3 frames/asset、3:4、hash、无 originals |
| T1 Empty | 弱关联、日常低信息素材 | `EMPTY_DAY` | Precision fail-closed | 请求 200、合法 Empty、无虚构 |
| T2 Chapter | 4–12 项同一完整活动 | 1 Chapter | 主 Episode、证据、标题/故事 | 所有 claim 可回看，未错误合并 |
| T3 Aha | 明显局部新奇/互动/动作峰值 | 1 strong Aha | Aha 与 Chapter 区分 | Aha 独立且不是低分 Chapter |
| T4 Multi-Chapter | 同一天两个时间分离、证据充分的 Episode | 2 Chapters | 边界和不重叠选择 | 无跨 Episode false merge |
| T5 Threshold | 接近门槛、语义重复素材 | 少选或不选 | confidence / dedupe Gate | 不凑数、不重复 |
| T6 Contract negative | 测试 fixture/篡改引用 | 拒绝 | 双层合同安全 | 不进入 Diary、不污染 Run |
| T7 Repeatability | 同一 Session 连续重跑 | 新 Run | 固定证据、追踪、版本比较 | Session 不变、Run 追加、trace 完整 |
| T8 Cost/Latency | 多组 4/8/12/24 项 | 任意合法输出 | 模型帧数、token、成本、时延 | 可按规模比较，无隐性原图传输 |

---

## 14. 2026-08-18 已完成的真机证据

已实际完成：

- iPhone 从相册选择任意尺寸/时长的 4 项媒体；
- App 本地生成 App Library normalized Evidence bundle；
- iPhone 对 Mac `GET /health` 成功；
- iPhone 对 X01 `POST /x01/v0.1/preview` 成功；
- Mac 使用 live Qwen adapter，而非 fixture；
- App 通过结果合同并跳转到 Diary Home；
- Diary 显示带 X01 标记的合法 `EMPTY_DAY`：`No qualifying memory`。

这次测试证明：

```text
arbitrary Photos media
→ local normalized Evidence
→ TLS research transport
→ live Qwen call
→ cloud precision gates
→ iOS contract admission
→ Diary Home empty-state
```

这次测试尚未证明：

- 正向 Chapter 是否稳定且高质量；
- 正向 Aha 是否成立；
- 多 Chapter 边界是否正确；
- confidence 是否经过校准；
- E01–E04 Benchmark 排名；
- wearable P1 数据表现；
- Production 上传、鉴权、后台任务与 SLA。

---

## 15. 常见故障与判断顺序

### 15.1 外层 HTTP 502，错误正文包含上游 401

含义通常是：iPhone 已经成功连到 Mac 网关，但 Mac 调 Qwen 时认证失败。

检查顺序：

1. 不要在 iPhone 里填写 Qwen API key；
2. 检查 Mac 钥匙串中 `DiaryOne DashScope API Key` 是否只有一条有效 key；
3. 隐藏输入在终端不显示字符是正常现象；重复粘贴可能把多个 key 串接起来；
4. 重新写入单个 key 后，再用最小 Qwen 请求验证；
5. 重启 X01 服务或重新检查 Ready；
6. 日志只能记录长度/掩码诊断，不能打印完整 key。

2026-08-18 的首次 401 原因就是隐藏输入重复粘贴后形成了拼接 key；修复为单个有效 key 后，最小 Qwen 请求和 X01 都返回成功。

### 15.2 `model_not_ready`

- key 不存在、不可读或格式无效；
- provider/model 配置未完成；
- 健康检查会返回未就绪，App 不应允许 Generate；
- 服务不得静默退回 fixture。

### 15.3 iPhone 无法连接 Mac

依次检查：

- iPhone 与 Mac 当前网络是否互通；
- endpoint 的 Mac LAN 地址和端口是否正确；
- X01 服务监听的不是仅 loopback 地址；
- TLS 证书是否与 App pin 配对；
- 测试 bearer 是否与该 research build 配对；
- endpoint 修改后是否重新点了 `Check X01 Server`。

### 15.4 Bundle/contract error

检查：

- 是否使用当前固定 Session 生成的 bundle；
- 是否恰好三个 frames/asset；
- 是否缺 frame、frame ID 重复或路径越界；
- bundle hash、session ID、asset IDs 是否匹配；
- 是否误把 strict continuous-source bundle 与 App Library bundle 混用；
- 是否在 bundle 生成后改变了 Session。

### 15.5 请求成功但没有 Chapter/Aha

先把它判断为合法 `EMPTY_DAY`，再检查：

- 输入是否只是零散、弱相关素材；
- Chapter/Aha confidence 是否低于 0.76/0.84；
- Aha hero 是否不是 PHOTO；
- 候选是否因 Evidence 引用或重复 Gate 被抑制；
- 是否需要用更连贯的一组 4–12 项素材做正向测试。

不要通过降低门槛或强制凑 Chapter 来“修复” Empty；先记录候选、失败原因和 Evidence 质量。

---

## 16. 每轮联调必须记录什么

至少保存：

- Test Session ID；
- 素材数量、类型、时间跨度和选择意图；
- bundle schema、bundle hash；
- App build / RC、cloud commit、pipeline version；
- provider、model snapshot、request ID；
- model frame count；
- input/output tokens；
- latency；
- native cost、汇率输入、estimated USD cost；
- Chapter/Aha/Empty 结果；
- 每个候选的 confidence 与 Gate 原因；
- 人工 review：正确、错误合并、错误记忆、漏选、叙事越界；
- 是否复现、如何修复、是否触发架构决策。

禁止只保存最终截图而丢失 Artifact、hash 与 Trace。

---

## 17. 下一步推进顺序

1. 用同一活动的 4–12 项素材完成一个高置信正向 Chapter。
2. 用明显局部互动、动作峰值或新奇细节完成一个 strong Aha。
3. 用同一天两个分离 Episode 验证两个 Chapter 和不重叠选择。
4. 修复 X01 `HIGHLIGHT_DAY` 最多 3 Aha 与冻结“恰好 1 Aha”的差异。
5. 将每轮输出与 Evidence、cost、latency 一起归档，不凭截图调阈值。
6. 回到正式 E01：Zero-generative、可比较、可进 Benchmark 的 Moment baseline。
7. 在 E01 Gold/Evaluator 就绪后，按 E02/E03/E04 做受控对照；X01 不进入排行榜。

---

## 18. 联调完成判定

只有同时满足下列条件，才能说“X01 App 联调闭环完成”：

- 任意相册图/视频可稳定生成可复现 Evidence；
- 原始媒体不进入 X01 上传体；
- endpoint 健康检查 fail-closed；
- live model 不会静默降级为 fixture；
- session、bundle、asset、frame、claim 全链路可追溯；
- 错误结果在云端或 App Gate 被拒绝；
- 合法 Empty、Chapter、Aha 三类路径均至少完成一次真机验证；
- 同一固定 Session 可追加重跑并比较 trace；
- 关键错误不会覆盖最后一次成功 Run；
- 所有结果明确标记 Experimental / Not Leaderboard。

当前状态是：**Evidence-only 真机链路与 Empty 路径已完成；Chapter、Aha、Multi-Chapter 正向质量路径仍待验证。**

---

## 19. 相关合同与实现文档

云端：

- [快速入口](00_READ_FIRST.md)
- [Canonical Processing Rules V1.0](CANONICAL_PROCESSING_RULES_V1_0.md)
- [App Research Export V01](app-research-export-v01.md)
- [X01 Diary Research Preview V01](x01-diary-research-preview-v01.md)
- `../contracts/app_library_bundle_v01.schema.json`
- `../contracts/x01_diary_preview_v01.schema.json`

App：

- `CLOUD_ALGORITHM_HANDOFF.md`
- `ALGORITHM_INTEGRATION_GUIDE.md`
- `TEST_RUNBOOK.md`
- `API_CONTRACT.md`
- `REMOTE_API_CONTRACT.md`
- `CONTRACT_GAP_REGISTER.md`
- `IMPLEMENTATION_STATUS.md`

如果本文与 Canonical Processing Rules 冲突，以 Canonical 为准；如果本文中的请求/返回字段与 Schema 冲突，以版本化 Schema 和双方合同测试为准，但必须登记文档差异。
