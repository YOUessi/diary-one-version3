# Expo Go 真机测试手册（对照当前 App）

> **内测总册（阶段 A→D、几十人公网底座、TestFlight）：** [`INTERNAL_BETA_FULL_GUIDE.md`](./INTERNAL_BETA_FULL_GUIDE.md)  
> 本文只管 **Expo Go 真机逐按钮**；MobileCLIP / 关 mock / 公网配额见总册。

界面以 **App 上的英文**为准。本手册只写 **现在 Expo Go 里能点到的按钮**。  
设计对照：[Diary One V1 Figma](https://www.figma.com/design/7NSDFSkyxO38CaELtAtayL/Diary-One-V1-%E2%80%94-Design-System---Prototype--0916%EF%BC%89?node-id=4-5) · 问卷板 [Preference Onboarding](https://www.figma.com/design/7NSDFSkyxO38CaELtAtayL/Diary-One-V1-%E2%80%94-Design-System---Prototype--0916%EF%BC%89?node-id=2145-2)。  
测前请 **Reload**（摇一摇 → Reload），否则可能还是旧界面。

语言请保持 **English**（Account → Language › → App Language → English）。若改成简体中文，底栏会变成「日记 / 记忆 / 设备 / 账户」，本手册对不上。

电脑此时应已就绪：BFF health 有 JSON、`ffmpeg=yes`、X02 `up`（真质量再要求 Key + `mock=no`）。手机 Reload 后再测。

结果记入 `docs/TEST_LOG.md`。

---

## 商用一次过完（必须按序，不要跳）

这是面向商用的 **Expo Go 能测部分的全量验收**。  
**本轮不要先点 Skip。** Skip 只在全部走完后、作为第 22 步补测。

已经停在四个 Tab：先 **Account → Phone test · cloud loop → Replay sign-in (onboarding) ›**，回到 **Sign in to Diary One**，从第 1 步开始。

每步只记 □ 通过 / ✖ 失败（失败就停，截图 + Ping 整行）。细节按钮以后面章节为准。

| 序 | 你做什么 | 通过标准 |
|----|----------|----------|
| 0 | 电脑 health、Metro、同一 Wi‑Fi、Reload | 浏览器 `127.0.0.1:8790/health` 有 JSON；弹窗 BFF 不是 `172.22` |
| 1 | 登录页认路 | 见 Apple / Google / Email / **Skip to Diary (no device)** / 底栏 **Continue with Email** |
| 2 | iPhone：**Continue with Apple**（可取消）；Android：应提示用 Google/邮箱 | 不崩溃、不假登录进主页 |
| 3 | **Continue with Google** | 未配 ID 弹 **Google Client ID missing**，不红屏 |
| 4 | 邮箱点 **Continue with Email**（先故意不填 @） | 黑按钮保持灰 |
| 5 | 填真实邮箱 → **Continue with Email** | 进 **Check your email**；QQ 能收到 6 位码 |
| 6 | 故意错码 → **Continue** | **Invalid code**，仍在 OTP 页 |
| 7 | **Resend code** → 填正确码 → **Continue** | 进入 **Pair your Diary One** |
| 8 | **Find Diary One** → **Allow Bluetooth** → **Continue** | 约 3 秒 **No Diary One found** → OK |
| 9 | 再 **Find Diary One** → **Simulate denied** | **Bluetooth is off for Diary One** → **Back** |
| 10 | **Continue without a device** | 进入 **Pairing needs Bluetooth**，不是问卷 |
| 11 | 权限链四页都点 **Continue**（不要 Simulate denied） | **SETUP COMPLETE** / **Diary One is connected** |
| 12 | **Start device basics**，1–6 点 **Continue**，第 7 点 **Open Diary** | 七页标题与手册 2.4 一致，然后问卷 |
| 13 | 问卷 8 屏：第 1 点 **Get started**；2–6 按手册选满（至少一类/一个 tag/一种文风）；7 **Continue**；8 先点卡片 **Agree and continue** 再 **Finish and personalize** | 进入四 Tab；**不要**点 Skip for now |
| 14 | 底栏 **Device** | **Not connected**、**Unavailable**、灰 **Sync**、无假电量 |
| 15 | **Account → Evidence pipeline lab ›** | 标题 **Internal lab** |
| 16 | **1 · Apply .env BFF defaults** → **1b · Enable cloud consent** → **2 · Ping BFF /health** | Ping：`OK`、`x02=up`、`ffmpeg=yes`；记下 `mc=` / `mock=`；BFF 为 `192.168.x:8790`（几十人公网见总册阶段 C） |
| 17 | **0 · Offline mock Diary** → 切 **Diary** | 出现 **Offline test memory** |
| 18 | Lab **A · Demo photo → cloud → Diary**，等 **Active tasks** 成功 | Diary 有新内容或明确空日，不是无限转、不是假成功 |
| 19 | Lab **A2 · Simulation video → cloud → Diary**，等成功 | 任务成功；章节里 Motion 可点播不崩 |
| 20 | **iPhone** 再跑 **B · Import from photo library**（1～3 张真图）；Android 失败标 ⚠ 即可 | 任务成功或诚实失败 |
| 21 | **Diary**：新装下滚 **Today · Morning Fishing**（勿死磕日历 Aug 16）→ Tag 不可点 → **What you remember** 保存 → 底栏 **Share memory** → **Photo collage** → 再 **Illustrated memory** Style A/B/C **Create** | 拼贴/插画 Preview 出来 |
| 22 | **Today** 首页 **Share day**（有章节时）→ **Daily Recap**（须能播 MP4）→ 再 **Photo collage** | Recap 失败则 ffmpeg/BFF 问题 |
| 23 | **Memory**：搜 `Fishing`；**Captured by You → See all ›**（格子应有图）；有则点 **Your Topics** | 搜索一次成功；格子有海报；Small memory 无详情页 |
| 24 | **Device Settings → Internal lab link** 打开 **Enable** → **Sync** → **Automatic Capture** 切 **Standard / High frequency** → **Unpair lab device** | 连接态无假电量数字；Sync 不冒充云端章节 |
| 25 | **Account**：**Edit** 改昵称 **Save**；**Current Plan**；**Privacy & Data**；**Notifications** 两开关；**Language** 看一眼改回 **English**；**Help & Feedback** 搜/点 Topic；**Licenses**；**Export My Data** | 都能进能返回 |
| 26 | Privacy 点 **Browse on this device only** → Lab 再 **A · Demo** | **必须拦住**，不上传 |
| 27 | 改回 **Allow cloud evidence upload** | consent=yes |
| 28 | **Log Out** → Cancel 一次，再真正 **Log out** | 不崩溃 |
| 29 | **Replay sign-in** → 这次点 **Skip to Diary (no device)** | 能进 Tab（证明内测捷径仍在；商用包以后会藏 Skip） |
| 30 | Lab **C · Semantic route debug** | Ping 含 `mc=yes` 时期望 `remote_bff`+MOBILECLIP；无权重则 degraded，**可记日志**（权重与启动见 `WINDOWS_MOBILECLIP_BFF.md`） |

**本轮允许不通过（写进日志，不挡其余项）：** 真耳机 BLE、Google 真登录（无 Client ID）、Android 相册 B、原生 Vision。  
**几十人公网 / TestFlight / 关 mock 质量门：** 不要停在本文，继续 [`INTERNAL_BETA_FULL_GUIDE.md`](./INTERNAL_BETA_FULL_GUIDE.md) 阶段 B–D。

---

## 先看：哪些东西在 App 里找不到（不是你漏点）

| 文档旧说法 | 现在实际 |
|------------|----------|
| 底部**蓝色** Skip | **没有蓝色字**。Skip 是邮箱框下面、**暖棕色描边**按钮 **Skip to Diary (no device)** |
| 今天 Diary 首页有 **Share day** | **新装 / 清库后**：种子会被移到 **Today**，首页应有 **Morning Fishing** 和 **Share day**。只有**旧本地库**还可能停在 2026-08-16——那时再选日历 Aug 16 或下滚找章节 |
| Google 直接登录 | 没配 Client ID 时只会弹 **Google Client ID missing**，不会进 Google 页 |
| 真耳机、真电量、真搜到设备 | Expo Go **做不到**。搜设备约 3 秒后 **No Diary One found** |
| Apple Vision 抽帧 | Expo Go **做不到**（Lab C 会显示 `DiaryOneVision=no (Expo Go)`） |
| Android 相册导入 | Expo Go Android **经常被系统拦**，用 Lab **A** 或 **A2**，不要死磕 B |
| 弹窗里立刻出现 6 位码 | Docker 量产 BFF 一般 **不在弹窗给码**，去 QQ 邮箱收；Lab「3 · Test OTP API」也可能只有 sent 文案 |

**这次不要测：** 真 BLE、TestFlight、原生 Vision、未配 ID 的 Google 真登录。

---

## 你现在可以测的全部入口（认路）

打开 App 后只有两种画面：

1. **Sign in to Diary One**（没 Skip / 没走完入门）
2. 底栏四 Tab（已经 Skip 过）：从左到右 **Diary · Memory · Device · Account**

已经在四 Tab、想重新看登录页：

**Account** → 向下滚到 **Phone test · cloud loop** → **Replay sign-in (onboarding) ›**

Lab（云端）两条路都能进，是同一页 **Internal lab**：

- **Account** → **Phone test · cloud loop** → **Evidence pipeline lab ›**
- **Device** → **Cloud processing (Expo Go)** → **Open Evidence pipeline lab**

---

## 0. 电脑每次开测（手机测之前）

手机和电脑必须同一 Wi‑Fi。BFF 地址必须是 **192.168.x**（你这台机常见 `192.168.31.74`），**不能是** `172.22.16.1`（WSL，手机连不上）。

PowerShell：

```powershell
# 1) 打开 Docker Desktop，等到 Running
# 2) 量产 BFF
cd E:\AI耳机\diary-one\services\bff
.\scripts\up-docker-stack.ps1

# 3) 千问 X02（Docker 里的 BFF 要连本机 :8787）
.\scripts\start-x02.ps1

# 4) 把 App .env 写成 WLAN IP（不要 172.22）
.\scripts\setup-commercial-dev.ps1

# 5) 另开窗口起 Metro
cd E:\AI耳机\diary-one\apps\mobile
npx expo start --go --lan
```

浏览器打开 `http://127.0.0.1:8790/health` 应有 JSON。手机 Ping 需要 `x02` 为 up、`ffmpeg` 为 yes。

弹窗若仍是 `172.22.16.1:8790`：确认 `apps/mobile/.env` 是 `http://192.168.31.74:8790`，**重启 Metro** 再 Reload。

防火墙拦 8790（管理员跑一次）：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\setup-commercial-dev.ps1 -OpenFirewall
```

Expo Go 扫 Metro 二维码。端口以终端为准（8081 被占时是 8082）。

不要同时再开一份 `start-dev-lite`（会抢 8790）。

---

## 1. 登录页（标题 Sign in to Diary One）

从上到下应看到：

1. 标题 **Sign in to Diary One**
2. **Continue with Apple**
3. **Continue with Google**
4. **or**
5. **Email address** 输入框
6. **Skip to Diary (no device)**（暖棕色描边；副文案 Internal test — skip sign-in and pairing）
7. 条款小字
8. **最底下黑色** **Continue with Email**（没填邮箱时是灰的）

看不到 Skip：中间区域**向上滑**；仍没有就 Reload。  
Skip **不在**黑色 Continue with Email 上。

### 1A · Skip（内测最快，建议先做云端）

1. 点 **Skip to Diary (no device)**。
2. 进入四 Tab。
3. 点 **Device**：标题 **Device**，大字 **Not connected**，下面 **Unavailable**（不要出现假的 72% / 100% 电量）。

### 1B · 邮箱 OTP（Docker 真发信）

1. 在 **Email address** 输入带 `@` 的邮箱（例如你的 QQ 邮箱）。
2. 点黑色 **Continue with Email**（发送中变成 **Sending…**）。
3. **成功：** 弹窗 **Check your email**，然后进入标题 **Check your email** 的下一页。去邮箱拿 **6 位码**。  
   **失败：** **Could not request code** + BFF 地址。若是 `172.22.16.1` 见第 0 章。
4. 在 **6-digit code** 输入码，点 **Continue**（校验中 **Verifying…**）。对了进入 **Pair your Diary One**。
5. 点 **Resend code** 可再发一封。
6. 故意输错 6 位 → 弹窗 **Invalid code**，仍停在 OTP 页。

### 1C · Apple / Google（有限）

- **Continue with Apple**  
  - iPhone：可走系统 Apple 登录；取消不算失败。  
  - Android：弹窗 **Apple sign-in**，说明用 Google 或邮箱。
- **Continue with Google**  
  - 未配 ID：弹窗 **Google Client ID missing**，**不能**进主页。  
  - 已在 `.env` 写 `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID` 并重启 Metro 后，才会打开 Google 页。

---

## 2. 入门（只有登录成功才会到；Skip 会跳过整段）

Skip 过的人要测这里：先 **Replay sign-in (onboarding)**，再走 1B 邮箱（或以后配好的 OAuth），不要 Skip。

### 2.1 配对（标题 Pair your Diary One）

顶栏类似 **SETUP · PAIR DEVICE**。两个按钮：

- 黑色 **Find Diary One**
- 底下暖色 **Continue without a device**

**测云端 / 问卷：点 Continue without a device。**

下一屏标题是 **Pairing needs Bluetooth**（权限链），**不是**问卷。

**测搜设备（一定会失败）：**

1. 点 **Find Diary One**。
2. 标题 **Allow Bluetooth** → 黑按钮 **Continue**。  
   或点 **Simulate denied** → **Bluetooth is off for Diary One** → **Open Settings** / **Back**。
3. 标题 **Looking for Diary One…**，约 3 秒弹窗 **No Diary One found** → **OK** 回到配对页。  
   搜索中可点 **Cancel**。

不要期望连上真耳机。

### 2.2 无设备后的权限链（每页主按钮 Continue）

按顺序点 **Continue**：

1. **Pairing needs Bluetooth**（可 **Simulate denied** → **Bluetooth access is off**）
2. **Allow local network for Sync**
3. **Allow Photos access**
4. **Stay updated when memories are ready** → **SETUP COMPLETE**

拒绝页有 **Open Settings**；部分页还有 **Continue** 往下走。不会反复弹系统权限死循环。

### 2.3 Setup Complete（标题 Diary One is connected）

- **Start device basics** → 下面 2.4（7 页）
- **Skip device basics** → 直接问卷 **Help Diary get to know you**

### 2.4 设备基础 7 步

每页主按钮 **Continue**，第 7 页是 **Open Diary**（实际进入问卷，不是四 Tab）。

| 顶栏 | 标题 |
|------|------|
| DEVICE BASICS · 1 OF 7 | Wear Diary One |
| 2 OF 7 | Power & Volume |
| 3 OF 7 | Choose Your Capture |
| 4 OF 7 | Double Tap to Capture |
| 5 OF 7 | Adjust Your View |
| 6 OF 7 | Automatic Capture |
| 7 OF 7 | From Recordings to Memories → **Open Diary** |

### 2.5 问卷（按你截图的 8 屏点；Reload 后再测）

对照 Figma `node-id=2145-2` 与真机：

| | Figma 设计稿 | 现在 Expo Go（以截图为准） |
|--|--------------|---------------------------|
| 欢迎主按钮 | **Get started** | 已改成 **Get started**（旧包是 **Start**，请 Reload） |
| 欢迎副按钮 | **Skip for now** | **Skip for now** |
| 第 2 屏瓦片 | People who matter / Time with pets / Travel & exploring…（3 步问卷） | **Daily life / Personal growth / …** 共 8 类（命中 tag 库，8 屏） |
| 第 2 屏主按钮 | **Continue** | 未选完是灰的 **Next**；选中后变黑 |

不要在 App 里找 Figma 的 **People who matter**。真机是下面这 8 类。

**每屏共同点：** 左上 **✕**（等同整卷 Skip）、中间进度条、右上 **‹**（第 1 屏没有）。  
底部黑按钮 + 底下暖色 **Skip for now**。Account 里重填时副按钮是 **Cancel**，最后一屏黑按钮是 **Save preferences**。

**第 1 屏 · Help Diary get to know you**

- 小字 **WELCOME TO DIARY**
- 三条：Takes about 1–2 minutes / You can skip this step / You can change these preferences anytime
- 点黑色 **Get started**

**第 2 屏 · Which kind of content do you like Diary to write more?**

点至少一块（出现 ✓），再点 **Next**。八块文案必须是：

1. **Daily life**
2. **Personal growth**
3. **Emotional reflection**
4. **Travel & adventure**
5. **Relationships**
6. **Work & study**
7. **Health & fitness**
8. **Hobbies & creativity**

**第 3 屏 · Anything else you’d like Diary to write for?**

多行输入，可空。占位类似 quiet mornings。点 **Next**。

**第 4 屏 · Select tags that you are interested in**

按类别出现芯片（如 Citywalk、Coffee、Home moments、Family、Workout…）。至少点一个（选中变暖色底）→ **Next**。

**第 5 屏 · What style of content do you like most?**

单选圆点，六项：

- **Empathetic and warm**
- **Logical and clear**
- **Creative and poetic**
- **Direct and objective**
- **Playful and witty**
- **Philosophical and reflective**

选一个 → **Next**。

**第 6 屏 · Select topics Diary will not write for you**

可空。芯片例如 **Repeated commuting**、**Empty landscapes**、**Long indoor meetings**、**Phone / screen-only scenes**、**Work stress detail**、**Conflict / arguments**、**Politics / news**、**Medical / illness detail**。  
选中带 **×**。点 **Next**。

**第 7 屏 · Review your preferences**

核对 Preferred categories / Interest tags / Writing style / Topics to avoid。点 **Continue**（不是 Next）。

**第 8 屏 · Cloud processing consent**

两张单选卡（不是普通按钮）：

- **Agree and continue** — Allow cloud evidence upload for memory generation.
- **Browse on this device only for now** — You can turn cloud processing on later in Privacy & Data.

测云端必须先点选 **Agree and continue**（右侧圆点亮起），再点底部 **Finish and personalize**。  
只点黑按钮、没选卡片时，黑按钮是灰的点不了。

**Skip for now：** 任意一屏点它会跳过整卷进 Diary（云同意未设，第 3 章 Demo 可能被拦，要到 Privacy 打开）。

---

## 3. 云端 Diary（Lab）— 建议 Skip 后立刻做

### 3.1 打开 Internal lab

**Account** → 滚到 **Phone test · cloud loop** → **Evidence pipeline lab ›**  
标题 **Internal lab**。

页顶 **Quick connect** 卡片里能看到 **Target / BFF / Cloud consent**。

**Simulate failures** 默认关：主验收路径 Save / Search / Share 应一次成功。只有要对齐 Figma Failed 板时再打开。

### 3.2 必须按顺序：1 → 1b → 2，再导入

1. 点 **1 · Apply .env BFF defaults**  
   弹窗 **BFF applied**。上面 **BFF:** 必须是 `http://192.168.31.74:8790` 这种 WLAN，**Target: production**。
2. 点 **1b · Enable cloud consent (lab)**  
   **Cloud consent: yes**。  
   或：**Account → Privacy & Data ›** → **Allow cloud evidence upload**（行尾 ✓）。
3. 点 **2 · Ping BFF /health**  
   需要一行以 **OK** 开头，且 **x02=up**、**ffmpeg=yes**。  
   同时记下 **`mc=yes|no`**（MobileCLIP）和 **`mock=yes|no`**（空日是否允许 mock 章）。  
   `x02=down`：电脑再跑 `.\scripts\start-x02.ps1`。  
   `FAIL` / ConnectException：同一 Wi‑Fi、防火墙、URL 不是 172.22。  
   `mc=no`：视频语义为 degraded；照片上云仍可测。要 `mc=yes` 见 `WINDOWS_MOBILECLIP_BFF.md` 并重启 BFF。
4. 可选 **3 · Test OTP API**（证明 BFF 能发 OTP；Docker 下可能没有 `dev_code`）。

**Cloud processing target** 保持选中 **Production BFF**（不要切成 Research (X02)，除非你知道自己在测直连）。

### 3.3 不走云：证明 Diary 能显示

1. Lab 点 **0 · Offline mock Diary (no cloud)**。
2. 底栏 **Diary**。
3. 应出现章节 **Offline test memory**。

这块失败是 App 显示问题，先别怪云。

### 3.4 上云（三选一，优先 A 或 A2）

Ping 已 OK、consent=yes。

| 按钮 | 用途 |
|------|------|
| **A · Demo photo → cloud → Diary** | 不碰相册，内置样图走完整云链路 |
| **A2 · Simulation video → cloud → Diary** | 捆绑 `assets/motion/sim-morning.mp4`（约 8s）→ 云 |
| **B · Import from photo library** | 真相册；**优先 iPhone**；Android Expo Go 失败就标 ⚠，改用 A/A2 |

步骤：

1. 点 A 或 A2。弹窗类似 **Demo pipeline started** → 确定。
2. Lab 看 **Active tasks**，等到成功（真 qwen 可能要几分钟）。
3. 切 **Diary**：今天可能出现新章节或处理横幅。空日、PIPELINE 挡住也可以，任务成功即链路通。
4. **B**：允许相册后选 1～3 张图或短视频。

### 3.5 同意拦截（必测）

1. **Account → Privacy & Data ›**
2. 点 **Browse on this device only**（出现 ✓）。
3. 回 Lab 再点 **A · Demo photo → cloud → Diary**。
4. 应提示需要 cloud consent，**不上传**。
5. 测完改回 **Allow cloud evidence upload**。

### 3.6 Device 页上的捷径（同一套）

**Device** 往下滚 **Cloud processing (Expo Go)**：

- **Open Evidence pipeline lab**
- **Apply .env BFF + cloud consent**
- **A · Demo photo → cloud → Diary**
- **B · Import from photo library**

---

## 4. Diary

底栏最左 **Diary**（Figma 底栏带图标，Expo Go 现为纯文字 **Diary · Memory · Device · Account**）。  
顶栏标题 **Diary**。右上角点 **Search**（Figma 是放大镜图标，真机是文字 **Search**，进同一搜索页）。

### 4.1 今天 vs 种子日期（最容易迷路）

- 打开默认是 **Today**。
- **新装 / `resetLocalAppData` 后**：`Morning Fishing`、`Afternoon Citywalk` 会落在 **Today**；首页应有 **Share day**。往下滚即可，**不要**为了找种子去点日历 Aug 16（那天可能是空日）。
- **旧持久化库**：章节可能仍停在 **Sat, Aug 16**——那时再选日历或下滚找 **Morning Fishing**。
- 点日历月份标题旁的 **▾** 进入大日历，或在格子上选 **16**（August 2026）。空日文案：**No memories for this day.**
- 点 **Today** / **↑** 回到今天。
- 滚到底若有 **Load earlier memories** 就点；失败时点 **Try Again**。

开发时 Diary 页里可能还有 Today 状态调试条；也可到 **Account** 最底部 **Internal · Today state** 点芯片。

### 4.2 Today 七态（Account 最底部）

**Account** 滚过 **Log Out**，到 **Internal · Today state**。  
依次点：`READY` `UNSYNCED` `PREPARING` `READY_NEW_RECORDINGS` `READY_PREPARING` `ZERO_CURATED` `NO_RECORDINGS` `PARTIAL`。  
每点一次切回 **Diary** 看横幅。测完点回 `READY`。

今天空态对应文案：

- `NO_RECORDINGS` → **No recordings today.**
- `ZERO_CURATED` → **No memories were created from today's recordings.**

### 4.3 章节详情

1. 点卡片 **Morning Fishing**。
2. 阅读故事。**Tag 点了不会变成筛选**（刻意不可点）。
3. 有短片/海报可点播放（bundled Motion 或占位）。崩了算失败。
4. **What you remember**：空则点 **+  Add what you remember**；已有则点 **Edit**。  
   半屏标题 **Edit what you remember** → 输入 → **Save**（出现 **Saved**）。  
   改了再关：弹窗 **Discard your changes?**。  
   已有故事可 **Remove**（确认页）。默认保存应一次成功；测 Figma Failed 板时再到 Lab 打开 **Simulate failures**，才会隔次失败 → **Try Again**。
5. 分享：Figma 章节页是**右上角分享图标**；Expo Go 是**最底下黑色条 Share memory**。点底栏 **Share memory** → 第 6 章。

---

## 5. Memory

底栏 **Memory**。

1. 点搜索框 **Search your memories...**（Figma 左侧有放大镜），搜 `Fishing` 应有结果；乱打应空。  
   Diary 顶栏 **Search** 也进同一页。
2. **Captured by You** → 右侧 **See all ›**；或点 **Photos** / **Videos**。点格子进原图；删除走确认（别误删要留的）。  
   Lab 测图不应当作「你拍的」长期纪律（Lab 源有隔离）。
3. **Your Topics** → **See all ›**，或点芯片（种子如 **Fishing**、**Running**、**Model Building**、**Coffee**）。
4. Diary 上的 Small memory **没有下一页详情**。

---

## 6. Share（需要第 3 章 Ping 的 ffmpeg=yes）

**Share 入口和 Figma 不一样，按真机点：**

- Figma Diary 首页：Today 右侧是**分享小图标**；Expo Go 是一条卡片 **Share day**（副文案 **Daily Recap · photo collage**）。
- Figma 章节：右上角图标；Expo Go：底栏 **Share memory**。

**Share day 出现条件：** 当前选中的那一天**已经有章节**。新装时 **Today** 有种子章节就会有；否则滚到 **Morning Fishing** 所在那天（旧库可能是 Aug 16）。

### 6.1 章节 Share memory

1. 打开 **Morning Fishing** → 底栏 **Share memory**。
2. 半屏标题 **Share memory**，两项：
   - **Photo collage**
   - **Illustrated memory**
3. 点 **Photo collage** → **Preparing…**（可顶栏 Cancel）→ Preview 1～4 格 → 系统分享/存相册。
4. 再进 **Illustrated memory** → 选 **Style A / B / C** → **Create** → Preview。三种应能看出差别。

### 6.2 某一天 Share day

1. 选中有章节的那天 → 点 **Share day**。
2. 半屏 **Share day**：
   - **Daily Recap**（9:16 MP4，走电脑 ffmpeg）
   - **Photo collage**（当天静图）
3. `ffmpeg=no` 时 Recap 应失败，先修电脑 ffmpeg 并重启 BFF。

---

## 7. Device

底栏 **Device**。标题 **Device**。此页与 Figma 未连接稿一致。

未开 Lab link 时（应对上 Figma）：

- 左 **Not connected**，右 **Unavailable**
- **On Device**：Storage / New recordings / Ready to sync / Last synced 都是 **Unavailable**
- 中间灰色胶囊 **Sync**，点不了
- **Automatic Capture** 行右侧 Unavailable ›，点不进
- **Device Settings ›**

点 **Device Settings ›**：

- 标题 **Device Settings**
- **Device Name** / **Firmware** = Unavailable
- 可点 **Reset Device**（未连接会说明要先连接）
- 开发开关 **Internal lab link (no BLE)**：打开 → 弹窗 **Lab device link** → **Enable**
- 回到 Device 应变 **Connected**；电量仍可能是 **Battery level unavailable**（不要造假百分比）
- 此时 **Sync** 可点（只改 UI，**不会**变出真耳机录音）
- **Automatic Capture ›** → **Standard** / **High frequency**（选中有 ✓）
- 可 **Unpair lab device** 还原未连接

往下 **Cloud processing (Expo Go)** 见 3.6。

---

## 8. Account

底栏最右 **Account**。标题 **Account**。可能有 **Internal beta** 横幅。

从上到下（要**整页滚完**）：

1. 头像行：昵称（Skip 后常是 **Guest**）+ 右侧 **Edit**（Figma 同样是 Edit，不是大按钮）
2. **WHAT MATTERS TO YOU** / Tell Diary One what matters to you.
   - Figma 这一屏只有 **+ Add what matters to you**
   - Expo Go 空偏好时还有 **Start preference survey**（内测入口，设计稿没有，请用它走问卷）
   - 有芯片后：**+ Add** / **Manage ›** / **Retake preference survey ›**
3. **PLAN** → **Current Plan** 右侧 **Basic ›**
4. **PRIVACY & DATA** → **Privacy & Data ›**
5. **APP SETTINGS** → **Notifications ›** / **Language** 右侧 **English ›**
6. **Phone test · cloud loop** → **Evidence pipeline lab ›** / **Replay sign-in (onboarding) ›**
7. **Support** → **Help & Feedback ›**
8. **About** → **App Version** `1.0.0`（不可点）/ **Licenses ›**
9. **Log Out**
10. **Internal · Today state** 芯片

### 8.1 Edit Profile

点头像行 **Edit**。标题 **Edit Profile**。

- 点头像选系统相册（Android Expo Go 可能失败）
- **Display Name** 改昵称；空名字不能 **Save**
- **Email / Sign-in** 只读
- **Save** 默认一次成功；测 Failed 板时 Lab 开 **Simulate failures** 才会隔次失败 → **Try Again**
- 未保存返回会问是否丢弃

### 8.2 问卷与偏好

- **Start preference survey** / **Retake preference survey**：走第 2.5 节，最后 **Save preferences**
- **+ Add what matters to you** 手写一条
- **Manage ›** 列表里编辑 / 删除确认

### 8.3 Privacy & Data

标题 **Privacy & Data**。

- **Allow cloud evidence upload** / **Browse on this device only**
- **Stored Memories & Captured by You**
- **Memory Profile & Stories**
- **Export My Data**（导出 JSON）
- **Delete Account & Data**
- **Privacy Policy** / **Terms**（配了 URL 才有 Open）

### 8.4 Notifications / Language / Help

- **Notifications**：开关 **Memories Ready**、**Important Device Alerts**
- **Language**：**App Language** → English / 简体中文 / System default（测本手册请留 English）
- **Help & Feedback**：搜索框 **Search Help**；点 **Pairing & Connection**、**Sync**、**Capture & Camera** 等

### 8.5 Log Out

点 **Log Out** → **Cancel** 或 **Log out**。内测主要清本地资料，记忆仍在本机。

---

## 9. 推荐一次测完的顺序

```
电脑 Docker + X02 + setup-commercial-dev + Metro
手机扫码
登录页 → Skip
Device 确认 Not connected
Account → Lab → Apply → 同意 → Ping
Lab 0 Offline mock → Diary 能看到
Lab A 或 A2 → Active tasks 成功 → Diary
Diary Today（或旧库 Aug 16）→ Morning Fishing → Your Story → Share memory
有章节的那天 → Share day → Recap / 日拼贴
Memory 搜索 Fishing
Device Lab link → Sync / Automatic Capture
Account 资料 / Privacy 关同意再 Demo 应拦住
（有空再 Replay 走配对失败 + 问卷）
```

---

## 10. 勾选

```
电脑 health / Metro：□
Skip 进四 Tab：□
邮箱 OTP（QQ 收码）：□ / 未跑
Apple 仅 iPhone / Google 未配 ID 弹窗：□
配对诚实失败：□  无设备权限链：□  问卷：□ / 未跑
Lab Apply + Ping x02=up ffmpeg=yes：□
Offline mock：□
A 或 A2 云端：□
B 相册：□ / ⚠ Android
同意拦截：□
Diary Today（或旧库 Aug 16）章节 / 日历空日 / Your Story：□
Share memory 拼贴 + 插画 ABC：□
Share day Recap + 日拼贴：□
Memory 搜索 / Captured / Topics：□
Device 未连接诚实 + Lab link：□
Account 资料 / Privacy / 通知 / 语言 / Help / 登出：□
```

### 10.1 像素验收清单（对照 Figma，真机一次勾完）

锁定屏（Diary READY / Chapter Detail / Account Home / Memory Home）只看、不大改。其余按画板并排勾选：

```
【Auth / Onboarding】
Sign In 控件高约 52、圆角约 12：□
Permissions 标题约 28、白卡 r16、Continue 52×r12：□
Setup Complete 占位卡 r16×约 220（非 r24）：□
Hardware / Survey 主 CTA 约 52×r12：□

【Share】
Share Preview：‹ + 大标题、白卡 4:5、Try another 灰色：□
Share Selector：半屏 r≈24、选项带缩略图：□
Illustrated Style：未选 Create 灰；选中再 Create：□

【Device】
Device Sync：约 48 高、r≈12（非大胶囊）：□
Device Settings 标题 28、扁平行、Reset 灰字：□

【Memory】
Captured：标题 34、筛选文字非胶囊、日期 13 灰：□
Original Viewer：‹ 白、媒体 cream r12、底栏三动作：□
Delete Original：居中白卡 r16 + 黑底 Delete：□
Your Topics：封面约 2:1、r12、标题 17：□

【Diary 交互（非锁定布局）】
Your Story Sheet：Save 约 44 高黑钮 r≈12：□
Remove note：底区确认卡 + 黑底 Remove：□
Discard（Story）：Keep Editing 文字 + 黑底 Discard：□
日历展开：选中日浅橙底、圆角约 12：□

【Account】
Edit Profile：头像约 88、字段/Save 52×r12：□
Discard（Profile）：同确认卡（非系统 Alert）：□
Preference Add/Edit：底栏白 Sheet 顶 r16、Save 88×44：□
Preference Delete：居中白卡 r16 + 黑底 Delete：□
Notifications / Language 标题 28：□
Help 搜索框约 48×r12：□
```

有意识产品偏差（不算像素失败）：无假电量、Continue without device、CLOUD EVIDENCE、Hardware Skip→survey、系统权限/分享/保存仍可用系统 Alert。

---

## 11. 报问题时带这些

1. Metro 完整 `exp://…`
2. Lab Ping **整行**（不要只说连不上）
3. Active tasks 失败原文
4. 电脑浏览器 `http://127.0.0.1:8790/health`
5. 弹窗里的 BFF URL（是不是 172.22）
6. 手机系统：iPhone 还是 Android Expo Go
