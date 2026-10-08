# 手机一次试完全部（Expo Go）

电脑已开：**BFF `http://192.168.31.74:8790`** · **Metro `:8081`** · ffmpeg / mock 已就绪。  
（若电脑 IP 变了，在 PC 再跑 `services/bff/scripts/setup-commercial-dev.ps1` 并重启 Metro。）

---

## 0. 连上 App（1 分钟）

1. 手机与电脑 **同一 Wi‑Fi**
2. 打开 **Expo Go（SDK 57）**，扫电脑终端二维码，或输入 `exp://192.168.31.74:8081`
3. 若连不上：电脑用**管理员**跑一次  
   `cd E:\AI耳机\diary-one\services\bff` → `.\scripts\setup-commercial-dev.ps1 -OpenFirewall`

---

## 1. 登录 / Skip（T1）

| 顺序 | 做什么 | 期望 |
|------|--------|------|
| A | **Skip to Diary** | 进四个 Tab；Device = Not connected |
| B | 或 Sign in 填邮箱 → Continue | 弹窗出现 **6 位码** → 输入后继续 |
| C | 故意输错码 | 拒绝，不进主页 |
| D | Apple / Google 按钮 | 只说明未接线，**不**假登录 |

问卷可 Skip；若做过问卷选同意上云更好。

---

## 2. Lab 接通云（T0 / T2）— 必做 · 云端处理主链

**Account → Evidence pipeline lab**（或 Device → Open Evidence pipeline lab）

| 顺序 | 按钮 | 期望 |
|------|------|------|
| 1 | **Apply .env BFF defaults** | URL=`http://192.168.31.74:8790`，Target=production，consent=yes |
| 1b | **Enable cloud consent**（若显示 no） | consent=yes |
| 2 | **Ping BFF /health** | `OK · x02=up · ffmpeg=yes · mock=yes` |
| 3 | **Test OTP API**（可选） | 弹出 dev_code |
| 0 | **Offline mock Diary** | 回 **Diary** 看到 *Offline test memory* |
| A | **Demo photo → cloud → Diary** | Diary 顶栏 **Cloud processing** → Active tasks 成功（可含 *mock fallback*）→ **新章节** |
| B | 相册导入 | iOS 可试；**Android Expo Go 常挂 → 用 A** |

**云端纪律（已修）：**
- 未 Apply BFF URL 时 **不再假成功**，会明确报错
- 默认走 **Production BFF**，不是空的 Research
- Ping 会提示 `mock=no`（无 Key 时 Demo 可能空日记）
- Recap 视频走 BFF ffmpeg（不依赖手机原生编码）

Cloud target 选 **Production BFF**。

---

## 3. Diary（T3）

- 点章节进详情：故事、Tag **点不了**、Motion 占位可接受  
- **Your Story**：写一句 → 保存；再试放弃  
- 日历选别的日期 / 空天文案  
- Account 里 Dev 可切 Today 状态（若有）

---

## 4. Memory（T4）

- 搜索关键词（本地字面）  
- Topics（有数据才显示）→ 进详情  
- Captured by You：**不应**出现相册测试源当作用户素材  
- Small Memory：**没有**独立详情页

---

## 5. Share（T5）

先 **Lab → Apply .env → Ping**（要 `ffmpeg=yes`）。拼贴/插画走 **BFF Pillow**，Recap 走 **电脑 ffmpeg**。

从某天 / 某记忆进 Share：

1. **Photo Collage**：多图网格（1–4 格）→ Preparing（可顶栏 Cancel）→ Preview（无 Cancel）→ 分享  
2. **Illustrated**：Style A 相纸框 / B 暖色晕影 / C 冷暖对切 → Preview  
3. **Daily Recap**：出 **MP4**（电脑 ffmpeg only）；播得了再分享/存相册  

**新装**：种子章节在 **Today**（`shiftSeedDates`），首页可有 **Share day**；旧库可能仍是 `2026-08-16`。种子带网络样图 / 捆绑 Motion，无导入也可测 Share。  
Ping 时 `ffmpeg=no` 则 Recap 会失败——先修电脑再测。

---

## 6. Device / Account（T6）

- Device：**Not connected**，无假电量；Sync 不可当真  
- Automatic Capture：可点选，未连接不要期待真采集  
- Account：改昵称、偏好增删改、Privacy / Language / Help  
- Privacy：可关掉云同意（再 Demo 应被拦住）

---

## 7. 本轮不要硬测

| 功能 | 原因 |
|------|------|
| 真耳机连接 / 电量 | 无硬件 |
| 真 AI 记忆质量 | 需百炼 Key（以后） |
| Vision 语义抽帧 | Expo Go 没有 |
| TestFlight 包 | 后置 |

---

## 出问题怎么说

把 Lab 里 **Ping 那一行全文**，或 **Share details**，发群 / 记到 `docs/TEST_LOG.md`。
