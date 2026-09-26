# Figma 04 Screens 对照清单

权威画板列表：`E:\AI耳机\.figma_fetch\page_04.txt`（139 个顶层 FRAME）。

图例：**✅** 路由/状态已覆盖且主文案对齐 · **⚠️** 逻辑有、像素或专态与画板不完全一致 · **➖** 画板组/说明帧，非独立 App 路由 · **🔧** 仅 `__DEV__` / 研发用途

最后更新：2026-09-23

---

## Diary（Today & 历史）

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Diary Home / READY | 31:2 | ✅ | `DiaryHomeScreen` |
| Diary Home / UNSYNCED | 40:313 | ✅ | `TodayStatusBanner` + Sync |
| Diary Home / PREPARING | 40:454 | ✅ | 横幅「Preparing your memories...」 |
| Diary Home / READY + NEW RECORDINGS | 40:597 | ✅ | `READY_NEW_RECORDINGS` |
| Diary Home / READY + PREPARING | 40:742 | ✅ | `READY_PREPARING` |
| Diary Home / NO RECORDINGS | 40:885 | ✅ | `NO_RECORDINGS` |
| Diary Home / Aug 15 Jump | 40:1396 | ✅ | 日历选日 + `selectDateKeyWithPrepare` |
| Diary Home / 0 CURATED MEMORY | 103:1365 | ✅ | `ZERO_CURATED` |
| Diary / Calendar Expanded | 131:1432 | ✅ | `DiaryCalendarExpandedScreen` |
| Diary / Calendar Preparing Day | 131:1689 | ✅ | 横幅 + 日历格 spinner + 列表淡化 |
| Diary / Loading Earlier Memories | 131:2039 | ✅ | `historyLoadState === 'loading'` |
| Diary / History Load Failed | 131:2157 | ✅ | failed + retry |
| Diary / Empty Past Day | 175:2214 | ✅ | 空日文案 |
| Chapter Detail / Morning Fishing | 43:1095 | ✅ | `ChapterDetailScreen` |
| Chapter Detail / Your Story Empty | 112:1232 | ✅ | Your Story 空态 |
| Chapter Detail / Motion Playing | 176:1966 | ⚠️ | Motion 仍图/短视频占位；播放态描边 + Playing |
| Daily Recap / 9:16 MP4 | 184:2213+ | ✅ | 幻灯片 MP4；iOS 原生或 BFF ffmpeg |
| Chapter Detail / Short Clip Playing | 176:2021 | ⚠️ | 短视频走 `MomentPlayer` |
| Today PARTIAL（PRD/模型） | — | ✅ | 画板无独立帧；`TodayStatus` + Dev 切换 |

---

## Memory

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Memory Home | 44:806 | ✅ | `MemoryHomeScreen` |
| Memory / Home Unsynced | 131:2530 | ✅ | 顶栏 unsynced 横幅 |
| Memory / Home No Topics | 131:2612 | ✅ | 无 Topics 时隐藏区块 |
| Memory / Search | 174:1921 | ✅ | 空态文案已对齐画板 |
| Basic Search / Internal Phase · Search | 346:122 | ✅ | 与 174:1921 同路由 |
| Memory / Search Results | 44:888 | ✅ | 本地 AND 搜索 |
| Memory / Search Loading | 131:2687 | ✅ | |
| Memory / Search No Results | 131:2757 | ✅ | |
| Memory / Search Failed | 131:2826 | ✅ | 隔次模拟失败 |
| Memory / Captured by You | 65:913 | ✅ | |
| Captured by You / Photos | 132:1812 | ✅ | filter=photo |
| Captured by You / Videos | 132:1882 | ✅ | filter=video |
| Captured by You / Empty | 132:1952 | ✅ | |
| Original Viewer / Captured by You | 65:1042 | ✅ | `OriginalViewerScreen` |
| Original Viewer / Delete Original Confirm | 125:1156 | ✅ | |
| Memory / Your Topics | 67:936 | ✅ | |
| Topic / Fishing | 67:1027 | ✅ | `TopicDetailScreen` |

---

## Share（R6-S4）

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| R6-S4 / SHARE — MEMORY / DAY | 184:1974–75 | ➖ | 说明文本 |
| Share Memory / Selector | 184:1976 | ✅ | `transparentModal` + 透明 `contentStyle`，章节保持可见 |
| Photo Collage Preparing/Preview/Failed | 184:2049+ | ✅ | 顶栏 Cancel：`ShareFlowCancelHeader` |
| Illustrated Style Picker / Selected | 184:2115+ | ✅ | |
| Illustrated Preparing/Preview/Failed | 184:2148+ | ✅ | |
| Daily Recap Preparing/Preview/Failed | 184:2213+ | ✅ | |
| Daily Recap / Readiness Changed | 184:2282 | ✅ | `ShareDayReadinessSheet` |

---

## Your Story & Original Video（APP045）

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Your Story Editor Empty/Existing | 134:1842, 123:1169 | ✅ | Sheet |
| Saving / Save Failed / Discard | 123:1236+ | ✅ | |
| Remove Confirm / Failed / Removing / Removed | 307:2211+ | ✅ | |
| Load Failed / Saved | 308:2231, 309:2723 | ✅ | |
| Original Video Poster/Playing/Paused/Muted 组合 | 308:2381+ | ✅ | `OriginalVideoPlayer` |
| APP045 Interaction Guide | 316:2457 | ➖ | 设计说明 |

---

## Account & Preferences

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Account Home | 44:1414 | ✅ | 有 email 时显示邮箱 |
| Account Home / With Preferences | 174:2002 | ✅ | 偏好芯片 + Manage |
| APP095 Local Profile — Account | 369:2596 | ✅ | 无 email →「Local test profile」 |
| Account / Edit Profile | 127:1117 | ✅ | |
| APP095 Edit / Saving / Save Failed / Discard / Blank | 369:2576+ | ✅ | 空昵称不可保存 |
| Account / Memory Preferences | 68:988 | ✅ | 数据来自种子/用户 |
| Memory Preferences Add/Edit/Delete | 126:1117+ | ✅ | |
| Privacy & Data / Notifications / Language | 71:993+ | ✅ | |
| Help & Feedback | 127:1139 | ✅ | Device Basics 7 步 |
| Auth Sign In / Email OTP | 127:1179+ | ✅ | Onboarding |
| Preference survey（会议 2026-09-23） | — | ✅ | 登录后可跳过；写入 Preferences + 云同意；**非 Figma 帧** |
| Current Plan / Licenses | 画板 Account 行 | ✅ | `PlanScreen` / `LicensesScreen` |
| APP095 Interaction Contract | 371:2608 | ➖ | 文本契约 |

---

## Device

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Device Home（Connected） | 44:1347 | ✅ | Lab link + 诚实电量 |
| Device / Disconnected | 269:2102 | ✅ | Not connected / Unavailable |
| Device / Automatic Capture | 69:1000 | ✅ | 选中态描边 + ✓，无 “Selected” 文案 |
| Device / Settings | 69:1020 | ✅ | `‹` 返回；静态 Name/Firmware 行 |
| R2 Group 10 DEVICE deferred | 137:1868 | ➖ | 说明：深度能力延后 |
| Research / evidence pipeline | — | 🔧 | 仅 `__DEV__` 在 Device 页展示 |

---

## Onboarding：Pairing · Permissions · Hardware

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Pairing Start → Connected 全链 | 128:1117+ | ✅ | Connected 不伪造 72% 电量 |
| Permissions 请求/拒绝 ×4 | 130:1117+ | ✅ | Open Settings |
| Hardware Basics 01–07 | 75:993+ | ✅ | `HardwareBasicsScreen` |
| Onboarding Transition / Setup Complete | 201:2102 | ✅ | |

---

## 非路由画板

| 类型 | ids | 说明 |
|------|-----|------|
| Screen Group / R2 Group 标题条 | 98:993+, 137:1841+ | Figma 分区标题 |
| R6-S4 脚注 TEXT | 184:2365 | 实现说明 |

---

## 产品纪律自检

| 规则 | 状态 |
|------|------|
| Tag 不可点 | ✅ `MemoryTag` 为 View；章节 `tagRow` `pointerEvents="none"` |
| Small Memory 无详情 | ✅ |
| 搜索仅本地字面 | ✅ `localSearch` |
| Sync ≠ 云端处理 | ✅ Device Sync vs Research pipeline 分离 |
| 未连接不伪造电量/同步时间 | ✅ |
| Captured 不含相册测试源（用户路径） | ✅ 证据导入仅 `__DEV__` / Lab |
| Diary 空态无额外 Import 按钮 | ✅ 对齐 Figma 文案，导入仅 Lab |

---

## 建议后续（可选）

1. Motion / Short clip：接真实 motion 资源后再对齐播放态画板。
2. Share 流程各屏顶部 Cancel 与画板间距微调（非阻塞）。
4. 生产包：确认 `__DEV__` 关闭后 Device 与 Account 无研发入口（Account 已有 Internal 区块需同样审视）。
