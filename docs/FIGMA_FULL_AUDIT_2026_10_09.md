# Figma 全量对照审计（2026-10-09）

**文件（实现真相源 2026-10-13）：** [Diary One V1 Copy](https://www.figma.com/design/mcPA0SAKRRJ3a1f6zwDO7Q/) · `fileKey=mcPA0SAKRRJ3a1f6zwDO7Q`  
**原文件：** [Diary One V1 — Design System & Prototype (0916）](https://www.figma.com/design/7NSDFSkyxO38CaELtAtayL/) · `7NSDFSkyxO38CaELtAtayL`（帧 id 兼容）  
**本地导出：** `diary-one/.figma_audit/`（INVENTORY / COMMENTS / HANDOFF_TEXT / page04_frames）  
**代码对照清单：** `apps/mobile/docs/FIGMA_04_COVERAGE.md`

---

## 0. 结论（先读这个）

1. **Figma 自己写明：** 本文件是 V1 **可执行视觉真相源**；实现应 **复现画板与组件**，而不是重新解释或擅自扩产品（见 Getting Started · Implementation Handoff）。  
2. **04 Screens 可路由画板：** 现有 App **路由/状态基本齐全**（见既有 `FIGMA_04_COVERAGE` ✅）。多人内测缺的是 **公网后端底座**，不是「缺一整页没写」。  
3. **19 条未解决评论（@Yvonne）多数是产品改版/增强建议**，与 **当前锁定画板文案** 或 **R2「Device deferred」** 冲突——**不能直接当开发任务照抄**，需设计改板或产品签字后再动代码。  
4. **「和 Figma 完全一致」的正确含义：**  
   - ✅ 对齐：**锁定屏 UI + 原型流规则 + Handoff Locked Rules**  
   - ❌ 不等于：把讨论区评论、未定稿增强（收藏 Agent、设备拍照按钮等）一次性全做进 V1  
5. **有意识产品偏差**（无 BLE 内测必需）仍建议保留，见下文 §4；若强制像素级「假电量 72%」会破坏诚实态纪律。

**MCP 限制：** 当前 Figma 账号在 Nexleap 为 **View seat**，`get_design_context` 已触发额度；本轮用 **REST API + 既有覆盖表** 完成全量盘点。升座后可再跑截图像素终验。

---

## 1. 文件结构盘点

| Page | id | 顶层节点 | 用途 |
|------|-----|----------|------|
| 00 Cover | 0:1 | 0 | 封面 |
| 01 Getting Started | 4:2 | 16 | Handoff / Implementation Map（**开发契约**） |
| 02 Foundations | 4:3 | 1 | Token / 基础 |
| 03 Components | 4:4 | 0 | （空/外置） |
| **04 Screens** | 4:5 | **159** | **主屏状态全集** |
| 05 Prototype | 4:6 | 18 | 冻结流、R5 协议、交互 Delta |
| 06 Utilities | 4:7 | 3 | 工具 |
| C01–C08 | 13:2… | 组件页 | Tag / Chapter / Calendar / Tab… |
| 01 Preference Onboarding | 2145:2 | 2 | 问卷 |
| 按钮批注 | 2275:2989 | 1 | 批注 |

04 内非生产路由（讨论/脑暴，**不对齐代码**）：`APP功能概览`、`开发讨论`、`首页/memory/device` 讨论帧、`分享的card`、长胶卷便签等（约 2085:* / 2096:* / 2118:* / 2122:*）。

---

## 2. Handoff 锁定规则（实现优先级最高）

摘自 Figma `82:2` / `84:2` / `05 Prototype`：

| 规则 | 含义 | App 现状 |
|------|------|----------|
| Visual language | 60% Editorial · 30% iOS · 10% Warm；Paper White 底 | 主题已按此方向 |
| Diary rules | Chapter 非白卡片；Small Memory 不可点 | ✅ |
| IA | Diary / Memory / Device / Account；Today 态不挡历史；Search 一级是 Chapters；Aha 不对用户露出 | ✅ |
| Known placeholders | Device Home + 8 Onboarding **硬件视觉占位**，勿自创工业造型 | ✅ 占位 |
| First-run | 点 Find 之前不先要蓝牙；Hardware **正好 7 页** | ✅ |
| Device deferred | **在 SDK/硬件稳定前不要用现 SDK 加深 Device** | ✅ 未深挖 |
| Search | semantic but **not conversational**；一级 Chapters | ✅ 本地字面（语义搜索增强属评论扩展） |
| Captured | 仅 Manual Originals；删 Original 不删 Memory 衍生 | ✅ 纪律 |
| Topics | 信号不足整块隐藏，不挪到 Account | ✅ |
| Moment | 仅 Chapter 内联播放；无 Moment Detail | ✅ |
| Tab | 各 Tab 保栈与滚动 | 需真机再验 |

---

## 3. 04 画板 ↔ 代码覆盖（摘要）

权威细表：`apps/mobile/docs/FIGMA_04_COVERAGE.md`（2026-10-07 全帧盘点）。

| 区块 | 结论 |
|------|------|
| Diary Today 七态 + 日历/历史 | ✅ 有路由/状态 |
| Chapter / Your Story / Motion | ✅ |
| Memory Home / Search 五态 / Captured / Topics | ✅ |
| Share Memory/Day（拼贴/插画/Recap） | ✅ |
| Account / Preferences / Privacy / Auth | ✅ |
| Pairing / Permissions / Hardware 7 / Setup Complete | ✅（配对有内测扩展入口） |
| Device Home / Disconnected / Settings / Auto Capture | ✅ 占位深度 |
| Preference Onboarding 2145 | ✅ 8 屏（与旧 Figma 3 步瓦片不同，以真机/测试手册为准） |
| 讨论帧 2085+ | ➖ 不对齐 |

**本轮 REST 抽检：** Hardware Basics 01–07 标题/正文与 `hardwareBasicsContent.ts` **一致**（如 “left return-to-center wheel…”）。  
评论要求「左转盘控制积极程度 / 双击右转盘」等 = **改产品**，Figma 正文尚未改 → **先改画板再改代码**。

---

## 4. 有意识偏差（多人无硬件内测仍建议保留）

| 偏差 | 原因 | 若「强制完全一致」 |
|------|------|-------------------|
| Pairing：**Continue without a device** | 无 BLE 无法进主路径 | 仅 Store 包隐藏；内测包保留 |
| Connected **不显示假 72%** | Handoff 要占位诚实；假电量违规 | 可做电池行 UI + `Unavailable` |
| Privacy：**CLOUD EVIDENCE** | 画板无、上云必需 | 保留 |
| Hardware Skip → 问卷 | 产品链路 | 与部分画板「无 Skip」需产品定 |
| Lab / Skip 登录 | 内测 | Store 藏 |

---

## 5. 全部 19 条评论处置（OPEN=19）

| # | 节点 | 评论要点 | 处置 |
|---|------|----------|------|
| 1 | Chapter Motion 176:1966 | tag 合并/可跳转 | **产品**；V1 Tag 不可点纪律优先；改板后再做 |
| 2 | Diary READY 31:2 | 首页缺设备状态 | **与 Device deferred / 评论 9 合并讨论**；非当前锁定屏必做 |
| 3–5 | Device 44:1347 | 传输进度、减 Sync 占位、拍照录像钮、mode 展示、教程钮 | **明确落入 R2 Group 10 Deferred**；硬件未定 **不做进 V1 内测** |
| 6 | Collage Preview 184:2067 | 可交互相册/偏好友分享 | **V2 分享形态**；不挡 V1 Share Sheet |
| 7–8 | Memory Preferences | 偏好=筛选？AI 提词规律？ | **产品/算法说明**；UI 已有偏好；后端偏好→筛选合同另轨 |
| 9 | Diary UNSYNCED | 与设备状态合并 | 同 #2 |
| 10 | Diary READY | 标签按人/事/物 | **算法/内容模型**；非纯 UI |
| 11 | Chapter Detail | 头图轮播/Live/每卡 title | **媒体形态增强**；现有 Motion/短片内联已对齐冻结规则 |
| 12 | Memory Home | 收藏相册 | **范围扩大**；无画板 → 不做进当前门禁 |
| 13 | Search Results | 搜索 Agent 总结 | **与「not conversational」冲突** → V2 |
| 14 | Your Topics | 事件/人/地聚类规则 | **算法产品**；UI 隐藏空 Topics 已做 |
| 15–18 | Hardware 03–06 | 左右转盘/认知负荷文案 | **评论≠画板正文**；正文已对齐代码；改板后同步 |
| 19 | Recap Preview | 从哪跳转来 | **文档/原型标注**；App：`Share day` → Daily Recap（见测试手册） |

---

## 6. 前后端开发对照「多人内测」（在 Figma 冻结范围内）

### 6.1 前端（对齐 Figma SoT）

| 优先级 | 事项 | 说明 |
|--------|------|------|
| P0 | 真机按 `EXPO_GO_FULL_TEST_GUIDE` §10.1 勾像素 | 代码度量已收；需设备终验 |
| P0 | Tab 保栈 / 日历合同 / Moment 单播 | Handoff Delta；回归用例 |
| P1 | 升 Figma 座后批量截图差分锁定屏 | View 额度不够 |
| P1 | Store 包隐藏 Skip/Lab；内测包保留 | `EXPO_PUBLIC_STORE_RELEASE` |
| P2 | 评论驱动改版 | **等设计改 04 画板** |

### 6.2 后端（Figma 不画、但多人内测硬依赖）

| 优先级 | 事项 | 说明 |
|--------|------|------|
| P0 | 公网 HTTPS + Docker 量产栈 | 见 `INTERNAL_BETA_FULL_GUIDE` 阶段 C |
| P0 | 真 qwen + `ALLOW_MOCK_PREVIEW=false` | 质量门 |
| P0 | OTP 多用户隔离 | session Bearer |
| P1 | 每用户日配额 + Worker 限并发 | 防打爆百炼 |
| P1 | 偏好自然语言 → 云端筛选合同 | 回应评论 7–8（算法+BFF） |
| P2 | MobileCLIP 公网可选 | 视频；照片主路径可先不依赖 |

### 6.3 明确不在「完全一致 V1」内（除非改板）

Device 拍照/录像/传输进度可视化深化、Memory 收藏、Search Agent、可交互相册、假电量、未改板的转盘文案。

---

## 7. 建议工作顺序（汇报用）

```
1) 产品+设计：过一遍 §5 评论表 → 标「改板 / 延后 / 拒绝」
2) 前端：P0 真机像素 + 冻结流回归（不扩评论）
3) 后端：多人底座 P0（公网/关 mock/OTP/配额）
4) 升 Figma 编辑/Dev 座 → 截图终验 → 修残余像素
5) 仅对「已改板」评论项排迭代
```

---

## 8. 安全提示

对话中粘贴过 **Figma Personal Access Token**。请到 Figma → Settings → Personal access tokens **轮换/作废**，勿写入仓库或 README。本审计脚本仅本机 `.figma_audit`，已在 `.gitignore` 建议忽略（若未忽略请补）。

---

## 9. 相关文档

- `docs/INTERNAL_BETA_FULL_GUIDE.md` — 多人内测阶段 A–D  
- `docs/EXPO_GO_FULL_TEST_GUIDE.md` — 真机逐按钮  
- `apps/mobile/docs/FIGMA_04_COVERAGE.md` — 逐帧覆盖  
- `docs/Diary_One_算法与软件工作计划_多人内测.docx` — 算法/软件计划 Word  
