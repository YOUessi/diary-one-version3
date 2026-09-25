# Diary One · 商用功能测试计划（按模块）

**目的：** 开发期尽早暴露风险；每个功能点有「怎么测 / 通过标准 / 常见翻车」。  
**环境：** Expo Go SDK 57（Android/iOS）+ 本机 Dev Lite；上架前再用 EAS preview 复测一遍。

图例：⬜ 未测 · ✅ 通过 · ❌ 失败 · ⚠ 受限（环境限制，非产品缺陷）

---

## T0 环境与冒烟（每次开测先跑）

| # | 用例 | 步骤 | 通过标准 | 风险 |
|---|------|------|----------|------|
| T0.1 | Metro | `npx expo start --go --lan` | 手机能打开 App | 防火墙 / 不同网 |
| T0.2 | Dev Lite | `start-dev-lite.ps1 -Adapter fixture` | `/health` → mode=dev_lite | 未起 BFF |
| T0.3 | Lab Ping | Apply .env → Ping | OK · x02=up | Token / IP |
| T0.4 | Offline Diary | Lab **0 · Offline mock** | Diary 出现 Offline test memory | 若失败=UI/存储坏，先别怪云 |

---

## T1 账号 / 入门

| # | 用例 | 步骤 | 通过标准 | 风险 |
|---|------|------|----------|------|
| T1.1 | Skip | Skip to Diary | 进四 Tab；Device=Not connected | |
| T1.2 | OTP 弹窗码 | 邮箱 → 弹窗 code → Continue | 进配对/可 Skip 设备 | BFF 未起则 local-only |
| T1.3 | 错误码 | 输错 OTP | 拒绝，不进主页 | |
| T1.4 | Replay sign-in | Account → Replay | 再走登录 | |
| T1.5 | Apple/Google | 点按钮 | 诚实说明未接线（非假登录） | 审核假成功 |

---

## T2 云处理主链（核心风险）

| # | 用例 | 步骤 | 通过标准 | 风险 |
|---|------|------|----------|------|
| T2.1 | Demo→云 | Lab **A · Demo photo** | Task Succeeded；Diary 新 Chapter | 本地 Bundle / 上传 |
| T2.2 | 相册（iOS） | Lab B 选 1–3 图 | 同上 | Android Expo Go ⚠ |
| T2.3 | 失败语义 | 停 BFF 再 Demo | Task Failed + Alert；Today≠假 Empty | 假 Ready |
| T2.4 | Sync≠云 | Device Sync 禁用未连接 | 云任务仍走 Lab，不改电量 | 产品纪律 |
| T2.5 | Captured 隔离 | 导入后看 Captured | 无 PHOTO_LIBRARY_TEST 用户素材 | 隐私/来源 |

---

## T3 Diary

| # | 用例 | 通过标准 |
|---|------|----------|
| T3.1 | Today 各状态（Lab 切换） | 横幅文案对齐 Figma |
| T3.2 | 日历选日 / Preparing | spinner + 列表淡化 |
| T3.3 | Chapter Detail | 故事 / Tag 不可点 / 播放占位可接受 |
| T3.4 | Your Story | 保存 / 放弃 / 失败不丢已存 |
| T3.5 | 历史加载失败 | retry 可用 |

---

## T4 Memory

| # | 用例 | 通过标准 |
|---|------|----------|
| T4.1 | 搜索本地字面 | AND；无结果诚实 |
| T4.2 | Topics | 有数据才显示；详情可进章节 |
| T4.3 | Captured + Viewer | 删除确认；不混测试源 |
| T4.4 | Small Memory | **无**独立详情页 |

---

## T5 Share

| # | 用例 | 通过标准 |
|---|------|----------|
| T5.1 | Memory / Day selector | 透明 modal，底层可见 |
| T5.2 | Collage / Illustrated / Recap | Cancel；失败可重试 |
| T5.3 | Recap readiness changed | 横幅/sheet，不假成功 |

---

## T6 Device / Account

| # | 用例 | 通过标准 |
|---|------|----------|
| T6.1 | 未连接 | Unavailable；无假电量 |
| T6.2 | Lab link（仅 __DEV__） | 可 Sync 模拟；Store 包无 Lab |
| T6.3 | Automatic Capture | 选中 ✓，无 “Selected” 文案 |
| T6.4 | Edit Profile | 空昵称不可存；头像选图取消保留旧 |
| T6.5 | Preferences CRUD | 增删改持久 |
| T6.6 | Privacy / Language / Help | 页可达；无假客服 |

---

## T7 算法质量（有 Key 后单独轮）

| # | 用例 | 通过标准 |
|---|------|----------|
| T7.1 | qwen 真跑 | runtime identity 为 V1.75 / X02 v0.4.1 |
| T7.2 | 无编造 | 人工抽查断言可追证据 |
| T7.3 | Writer 失败 | 不发布坏文案；保留诊断 |

---

## T8 发布前回归（EAS preview，非 Go）

复跑 T0–T6；确认无 Lab；仅邮箱登录策略与内测说明一致。

---

## 测试记录模板（复制到 `docs/TEST_LOG.md`）

```
日期：
设备 / Expo Go 版本：
构建：Expo Go | EAS preview
BFF：fixture | qwen | offline
用例 ID：
结果：✅/❌/⚠
现象：
截图/日志：
责任人：
```
