# Figma 侧栏全 Pages × 代码对照矩阵

**文件：** [Diary One V1 — Design System & Prototype (0916）](https://www.figma.com/design/7NSDFSkyxO38CaELtAtayL/) · `7NSDFSkyxO38CaELtAtayL`  
**读法说明：** MCP `get_metadata` 不传 page id 时只会回 `00 Cover`；本表均按 **显式 page id** 拉取顶层 Layers（2026-10-14 全量复核）。  
**Nexleap 席位：** Full / Pro（权限足够）。

图例：**✅** 已读且代码对齐 · **⚠️** 已读、有意识偏差或文档页 · **➖** 非 App 路由（handoff/空页/批注） · **🔧** 仅 DEV

---

## 侧栏全部 Pages（一张不漏）

| # | 侧栏名 | page id | 顶层 Layers（摘要） | 代码落点 | 状态 |
|---|--------|---------|---------------------|----------|------|
| 1 | **00 Cover** | `0:1` | 无子节点 | — | ➖ |
| 2 | **01 Getting Started** | `4:2` | Handoff Notes/Map、Data & State、Interaction、Stack Gate、Sequence、Decision Log、Baseline Audit、R3 Matrix/Copy/Readiness/E2E、R4 Backlog/Mock/Acceptance（16 顶帧） | 开发契约；不实现为 UI 屏 | ⚠️ 已读·契约 |
| 3 | **02 Foundations** | `4:3` | `6:2` Foundations / Overview（Color / Type / Spacing / Radius / Elevation） | `src/theme.ts`（paper/ink/accent、type ramp、spacing、radius、layout） | ✅ |
| 4 | **03 Components** | `4:4` | 空 canvas | 组件外置到 C01–C08 | ➖ |
| 5 | **04 Screens** | `4:5` | ~159 顶层：Diary/Memory/Device/Account/Share/Onboarding/Pairing/Permissions/Hardware/讨论帧等 | 全表见 `FIGMA_04_COVERAGE.md` | ✅ 生产帧 |
| 6 | **05 Prototype** | `4:6` | 冻结流、R5 协议、交互 Delta 等 | 导航/播放/返回规则 → Stack + MomentPlayer | ⚠️ 规则对齐 |
| 7 | **06 Utilities** | `4:7` | Hardware Asset Queue、Lifestyle Media Queue | 硬件/媒体占位规则；勿自创造型 | ⚠️ 资产队列 |
| 8 | **C01 Tag** | `13:2` | `D1/Tag` Tone=Primary/Neutral + Documentation | `components/MemoryTag.tsx`（不可点） | ✅ |
| 9 | **C02 Chapter Card** | `16:2` | Editorial Block SELECTED vs iOS Compact REJECTED；`D1/Chapter Card` | `components/ChapterBlock.tsx`（hero~198、整卡进详情） | ✅ |
| 10 | **C03 Mini Memory Calendar** | `20:47` | Collapsed/Expanded；Prototype Target Aug 15 | `components/MemoryCalendar.tsx` + Diary 日历屏 | ✅ |
| 11 | **C04 Small Memory** | `23:2` | With Media / Text Only | `components/SmallMemory.tsx`（无 onPress） | ✅ |
| 12 | **C05 Bottom Tab Bar** | `25:2` | Active=Diary/Memory/Device/Account | `components/AppTabBar.tsx` + `MainTabs.tsx` | ✅ |
| 13 | **C06 Today Status** | `40:2` | Unsynced / Preparing / Ready+New / Ready+Preparing / No Recordings / 0 Curated | `components/TodayStatus.tsx` + Diary banner | ✅ |
| 14 | **C07 Inline Media** | `283:2` | APP045 文档；Media Action；Inline Media 八态（Poster…Unavailable） | `MomentPlayer.tsx` / `MomentMedia.tsx` | ✅ |
| 15 | **C08 Your Story** | `284:2` | Editor 四态；Confirmation 四态；Entry 四态 | `YourStorySheet` + ChapterDetail + Remove 路由 | ✅ |
| 16 | **01 Preference Onboarding** | `2145:2` | 真帧：`00 Welcome`→`01 Moments`→(custom)→`02 Show less`→`03 Summary`（15 状态帧含 Ø/N 变体） | `PreferenceSurveyScreen` + `preferenceSurvey.ts` — 文案/选项与 Figma 一致；选中描边 1.5 | ✅ |
| 17 | **按钮批注** | `2275:2989` | 功能批注/设备交互批注（非生产屏） | 不实现；评论/产品改板后再动 | ➖ |

---

## 04 Screens 生产帧（侧栏「04」下 Layers 的实现入口）

权威逐帧：`FIGMA_04_COVERAGE.md`（Diary / Memory / Share / Account / Device / Onboarding）。

| 区块 | 对照结论 |
|------|----------|
| Diary 七态 + 日历/历史/空日 | ✅ |
| Chapter / Your Story / Motion / Short Clip | ✅ |
| Memory Home / Search 五态 / Captured / Topics / Original | ✅ |
| Share R6-S4 全系 | ✅ |
| Account / Prefs / Privacy / Auth / OTP | ✅ |
| Device Home / Disconnected / Settings / Auto Capture | ✅（见下偏差） |
| Pairing / Permissions / Hardware 7 / Setup Complete | ✅（Start 软路径 ⚠️） |
| Preference 问卷 | ✅ |
| 讨论帧 2085+ / 长胶卷 | ➖ 不对齐代码 |

---

## 有意识偏差（对照 Figma 画板原文仍保留）

| 项 | Figma 画板 | 代码 | 原因 |
|----|------------|------|------|
| Device 断开电量 | `72% last known` | 无遥测 → `Unavailable` | 内测诚实；无 BLE |
| Pairing Connected | `Connected · Battery 72%` | `Connected` | 同上 |
| Pairing Start | 无次要 CTA | `Continue without a device` | 无硬件可进主链 |
| Device / Diary | 无上传区 | **Upload photos & videos** | 无硬件测 M2 |
| Privacy | 无 CLOUD EVIDENCE | 有同意开关 | 上云必需 |
| Diary 空态 | 无 Import | 有 Upload 按钮 | 同 M2 测通路 |

---

## Layers 深度说明

- **每一页顶层 Layers** 已通过 `get_metadata(pageId)` 拉取（04 约 3800+ 节点行、Getting Started ~2000+、Preference ~450+）。  
- **嵌套至叶子的每一个 TEXT/RECT** 不逐条改代码；实现契约是：**组件页 C01–C08 + 04 可路由 FRAME + Foundations token**。  
- 若要对某单帧做像素终验：对该 `node-id` 再调 `get_design_context` + 真机截图。

---

## 本次复核后代码动作

1. 本矩阵落盘（侧栏 17 项全覆盖）。  
2. Device / Pairing 诚实偏差保持（与内测计划一致）；不回退假 72%。  
3. 继续以 `FIGMA_04_COVERAGE.md` 为 04 路由真理源。
