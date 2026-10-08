# Figma 04 Screens 对照清单

权威画板列表：`E:\AI耳机\.figma_fetch\page_04.txt`（顶层 FRAME；含 Screen Group / R2 标题条与说明 TEXT）。

图例：**✅** 路由/状态已覆盖且主文案对齐 · **⚠️** 逻辑有、与画板有意识偏差（见备注） · **➖** 画板组/说明帧，非独立 App 路由 · **🔧** 仅 `__DEV__` / 研发用途

最后更新：2026-10-07（全帧盘点）

---

## Diary（Today & 历史）

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Diary Home / READY | 31:2 | ✅ | `DiaryHomeScreen`（像素锁定，勿大改） |
| Diary Home / UNSYNCED | 40:313 | ✅ | `TodayStatusBanner` + Sync |
| Diary Home / PREPARING | 40:454 | ✅ | Preparing your memories... |
| Diary Home / READY + NEW RECORDINGS | 40:597 | ✅ | `READY_NEW_RECORDINGS` |
| Diary Home / READY + PREPARING | 40:742 | ✅ | `READY_PREPARING` |
| Diary Home / NO RECORDINGS | 40:885 | ✅ | `NO_RECORDINGS` |
| Diary Home / Aug 15 Jump | 40:1396 | ✅ | 日历选日 + prepare |
| Diary Home / 0 CURATED MEMORY | 103:1365 | ✅ | `ZERO_CURATED` |
| Diary / Calendar Expanded | 131:1432 | ✅ | 周一；格 ~47×44；选中 r12 |
| Diary / Calendar Preparing Day | 131:1689 | ✅ | 横幅 + spinner + 列表淡化 |
| Diary / Loading Earlier Memories | 131:2039 | ✅ | `historyLoadState` |
| Diary / History Load Failed | 131:2157 | ✅ | Lab「Simulate failures」开启后隔次失败（默认关） |
| Diary / Empty Past Day | 175:2214 | ✅ | 空日文案 |
| Chapter Detail / Morning Fishing | 43:1095 | ✅ | `ChapterDetailScreen`（锁定） |
| Chapter Detail / Your Story Empty | 112:1232 | ✅ | |
| Chapter Detail / Motion Playing | 176:1966 | ✅ | accent 描边 + Playing |
| Chapter Detail / Short Clip Playing | 176:2021 | ✅ | `MomentPlayer` |
| Today PARTIAL（PRD） | — | ✅ | Dev 切换；无独立画板 |

---

## Memory

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Memory Home | 44:806 | ✅ | `MemoryHomeScreen`（锁定） |
| Memory / Home Unsynced | 131:2530 | ✅ | 顶栏 Sync 横幅 |
| Memory / Home No Topics | 131:2612 | ✅ | 无 Topics 隐藏区块 |
| Memory / Search | 174:1921 | ✅ | 空态 + Try example |
| Memory / Search Results | 44:888 | ✅ | 本地 AND |
| Memory / Search Loading | 131:2687 | ✅ | |
| Memory / Search No Results | 131:2757 | ✅ | |
| Memory / Search Failed | 131:2826 | ✅ | Lab「Simulate failures」开启后隔次失败（默认关） |
| Basic Search / Internal Phase · * | 346:122+ | ✅ | 与 Memory Search 同路由 |
| Memory / Captured by You | 65:913 | ✅ | |
| Captured by You / Photos · Videos · Empty | 132:1812+ | ✅ | filter |
| Original Viewer | 65:1042 | ✅ | |
| Original Viewer / Delete Confirm | 125:1156 | ✅ | 居中卡 r16；Cancel 文字 + 黑底 Delete Original 154×44 r12 |
| Memory / Your Topics | 67:936 | ✅ | |
| Topic / Fishing | 67:1027 | ✅ | |

---

## Share（R6-S4）

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| R6-S4 / SHARE — MEMORY · DAY | 184:1974–75 | ➖ | 分区标题 TEXT |
| Share Memory / Selector | 184:1976 | ✅ | `transparentModal` |
| Photo Collage Preparing / Preview / Failed | 184:2049+ | ✅ | Preparing Cancel；Preview=`SharePreviewShell`（顶栏+白卡）；Failed 无顶栏‹ |
| Illustrated Style Picker · Selected | 184:2115, 187:2108 | ✅ | 初始未选、Create 禁用；选中 accent 描边 |
| Illustrated Preparing / Preview / Failed | 184:2148+ | ✅ | Preview 同 `SharePreviewShell` |
| Daily Recap Preparing / Preview / Failed | 184:2213+ | ✅ | Preview 同壳 + 9:16 视频 |
| Daily Recap / Readiness Changed | 184:2282 | ✅ | `ShareDayReadinessSheet` |
| R6-S4 脚注 | 184:2365 | ➖ | 实现说明 TEXT |
| Share Day / Selector | — | ✅ | 无独立画板；`ShareDaySelectorScreen` 对齐 Memory Selector |

---

## Your Story & Original Video（APP045）

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Your Story / Editor Empty · Existing | 134:1842, 123:1169 | ✅ | Sheet 顶 r16；标题 22；Save 88×44 r12 |
| Your Story / Saving · Save Failed · Discard | 123:1236+ | ✅ | Discard=`DiscardConfirmCard`（非系统 Alert）；Save Failed 需 Lab fail-sim |
| Build 2B APP045 Edit / Empty / Saving / Save Failed / Discard / Saved | 307:2125, 309:* | ✅ | 同 Sheet |
| Remove Confirm · Failed · Removing · Removed | 307:2211+ | ✅ | 卡 r12；黑底 Remove/Try Again；Failed 需 Lab fail-sim |
| Load Failed | 308:2231 | ✅ | Chapter Detail 内 |
| Original Video Poster / Playing / Paused / Muted · 组合 | 308:2381+, 309:2630, 312:* | ✅ | `OriginalVideoPlayer` |
| APP045 Interaction Guide | 316:2457 | ➖ | 设计说明 |

---

## Account & Preferences

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Account Home | 44:1414 | ✅ | Plan / Licenses 行齐全 |
| Account Home / With Preferences | 174:2002 | ✅ | |
| APP095 Local Profile — Account | 369:2596 | ✅ | Local test profile |
| Account / Edit Profile | 127:1117 | ✅ | |
| APP095 Edit / Saving / Save Failed / Discard / Blank | 369:2576+, 370:*, 372:2606 | ✅ | Discard=`DiscardConfirmCard`；Save Failed 需 Lab fail-sim |
| APP095 Interaction Contract | 371:2608 | ➖ | 文本契约 |
| Account / Memory Preferences | 68:988 | ✅ | |
| Memory Preferences Add / Edit / Delete | 126:1117+ | ✅ | Add/Edit 底栏 Sheet 顶 r16·Save 88×44；Delete Confirm 居中卡 r16 |
| Privacy & Data | 71:993 | ✅ | + CLOUD EVIDENCE（产品扩展，画板无） |
| Notifications | 71:1021 | ✅ | |
| Language | 71:1050 | ✅ | |
| Help & Feedback | 127:1139 | ✅ | |
| Auth / Sign In | 127:1179 | ✅ | 控件 52×r12；Skip 仅内部；Store 仅邮箱 |
| Auth / Email OTP | 127:1195 | ✅ | 六格 52×56 r10；Continue 52×r12 |
| Current Plan / Licenses | Account 行 | ✅ | `PlanScreen` / `LicensesScreen`（04 无独立帧） |
| Preference survey（8 屏） | 2145:2 | ✅ | 标题/Next/✓/Review 对齐 2145 + 测试手册 §2.5；8 类 tag 库（非 Figma 旧 3 步瓦片） |

---

## Device

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Device Home | 44:1347 | ✅ | Sync 48×r12；行高 44 |
| Device / Disconnected | 269:2102 | ✅ | Unavailable 诚实态 |
| Device / Automatic Capture | 69:1000 | ✅ | 标题 28；选项 r12/h76 |
| Device / Settings | 69:1020 | ✅ | 标题 28；Lab switch 仅 `__DEV__` |
| R2 Group 10 DEVICE deferred | 137:1868 | ➖ | 深度能力延后说明 |

---

## Onboarding：Pairing · Permissions · Hardware

| Figma FRAME | id | 实现 | 备注 |
|-------------|-----|------|------|
| Pairing / Start | 128:1117 | ⚠️ | 多「Continue without a device」（无 BLE 必需） |
| Pairing / Bluetooth Permission · Denied | 128:1127, 1139 | ✅ | |
| Pairing / Searching · Found · Connecting | 128:1150+ | ✅ | 状态 callout；Searching 无真 BLE 时 Alert |
| Pairing / Connected | 128:1176 | ⚠️ | 画板「Battery 72%」→ 仅显示 Connected（不伪造电量） |
| Permissions Request / Denied ×4 | 130:1117–1199 | ✅ | 白卡占位；Simulate denied 仅 DEV |
| Hardware Basics 01–07 | 75:993–1147 | ✅ | 文案对齐；末步进问卷 |
| Setup Complete | 201:2102 | ✅ | 无 Skip（Skip 在 Hardware） |

---

## 非路由画板

| 类型 | ids | 说明 |
|------|-----|------|
| Screen Group · R2 Group 标题 | 98:993+, 137:1841+ | Figma 分区 |
| R6-S4 脚注 TEXT | 184:2365 | |

---

## 产品纪律自检

| 规则 | 状态 |
|------|------|
| Tag 不可点 | ✅ |
| Small Memory 无详情 | ✅ |
| 搜索仅本地字面 | ✅ |
| Sync ≠ 云端处理 | ✅ |
| 未连接不伪造电量/同步时间 | ✅ |
| Captured 用户路径不含相册测试源 | ✅ |
| Diary 空态无额外 Import | ✅ |
| Lab / Internal 仅 `showInternalLabTools` | ✅ |

---

## 有意识偏差（保留）

1. Pairing Connected：仅「Connected」，不伪造 72% 电量。
2. Pairing Start：保留「Continue without a device」（无 BLE）。
3. Privacy：CLOUD EVIDENCE 同意控件（画板无，产品必需）。
4. Hardware 步骤 Skip + 07「Open Diary」→ Preference Survey（产品链路）。
5. Photos/Notifications Denied：保留 Continue 以便推进 onboarding。

## 本轮全帧盘点后已修

- Pairing Searching/Found/Connecting 状态 callout；Permissions 占位卡去掉假系统标题
- Search Loading 查询回显；Captured 空态隐藏副标题
- Your Story：空态无 header；Sheet 标题 Add/Edit；Remove note；失败无 Remove；去掉 Saved pill
- Device 断开右侧固定 Unavailable；Automatic Capture `titleLarge`
- Sign In 主按钮高度对齐 `layout.buttonHeight`
- Pairing Start hero 下 caption；BT Denied 去掉多余 Back
- Captured 筛空态与 All 空态同文案
- Share Preview（Collage / Illustrated / Recap）去掉顶栏 Cancel（画板无）
- Share Preview 改为 Figma 结构：‹ + 居中标题、白卡媒体+文案、Share/Save、Try another 次级灰
- Share Preview/Preparing 媒体比 4:5（page_05）；Style Picker 未选禁用 Create；Recap 默认静音 + ▶ 空闲
- Share 按 `share_nodes.json`：标题 28、CTA r12/h52、Preview 画布 r16、Selector sheet r24+缩略图、Failed/Readiness 字号与实心 CTA
- Device/Auth 按 `device_auth_nodes.json`：Sync 48×r12；Capture/Settings 标题 28；Sign In/OTP/Onboarding CTA 52×r12
- Permissions/Memory/Account 按 `perm_memory_nodes.json`：权限卡 r16；Search 框 48×r12；Notifications/Language 标题 28；Captured 筛选 h44/gap10；Hardware CTA 52×r12
- Account 杂项按 `account_misc_nodes.json`：Edit Profile/Help CTA·搜索 52/48×r12；Preferences 卡 r12；Topics/Privacy 标题 28；Original Viewer 媒体 r12
- Your Story / Calendar 按 `story_calendar_nodes.json`：Sheet 顶 r16、Save 44×r12；日历选中 r12

## 像素推进结论（非全稿截图终验）

| 状态 | 范围 |
|------|------|
| 已按本地 Figma 节点收紧度量 | Share、Device/Auth/Onboarding、Permissions(标题28)、Setup Complete(r16)、Captured/Original Viewer/Topics、Account 子页、Preference Sheet/Delete、Discard、Your Story/Calendar |
| 锁定勿大改 | Diary READY、Chapter Detail、Account Home、Memory Home |
| 有意识偏差保留 | 无假电量、Continue without device、CLOUD EVIDENCE、系统权限/分享/保存 Alert 等 |
| 代码侧度量收紧 | **已完成**（见测试手册 §10.1） |
| 仍需你测 | 真机对照 Figma 勾 §10.1；真 BLE / 高清 Motion 延后 |

## 仍延后

1. 真 BLE / 更高清 motion 资源。
2. 原生 Vision / Lab C（Expo Go 记录即可）。

## 种子日期（hydrate）

- 新装 / 清库：`shiftSeedDates` 把 Morning Fishing 等绑到 **Today**，Captured `capturedAtLabel` 同步重写。
- 旧 SQLite 快照可能仍是 2026-08-16；见 `EXPO_GO_FULL_TEST_GUIDE` §4.1。

## 云端媒体映射（已接）

- `PreviewChapter.hero_asset_id` → `Chapter.heroUri`
- `selected_media[]` → Moments（poster/playback 本地 bundle frame）
- 入口：`attachChapterMediaFromBundle`（`runPipeline`）；mock preview 亦带上述字段
