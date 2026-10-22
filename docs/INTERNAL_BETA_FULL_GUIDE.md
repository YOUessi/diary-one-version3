# Diary One 内测全手册（Expo Go → 几十人稳定 chapter）

界面以 **App 上的英文**为准。测前请 **Reload**（摇一摇 → Reload）。  
语言请保持 **English**（Account → Language › → App Language → English），否则底栏对不上本手册。

设计对照：[Diary One V1 Figma](https://www.figma.com/design/7NSDFSkyxO38CaELtAtayL/Diary-One-V1-%E2%80%94-Design-System---Prototype--0916%EF%BC%89?node-id=4-5) · 问卷板 [Preference Onboarding](https://www.figma.com/design/7NSDFSkyxO38CaELtAtayL/Diary-One-V1-%E2%80%94-Design-System---Prototype--0916%EF%BC%89?node-id=2145-2)。

| 文档 | 用途 |
|------|------|
| **本文** | 你现在要测什么 + 几十人内测要立什么（主清单） |
| [`EXPO_GO_FULL_TEST_GUIDE.md`](./EXPO_GO_FULL_TEST_GUIDE.md) | 真机逐按钮细节（认路、问卷 8 屏、Share、像素勾选） |
| [`CLOUD_BULK_CHANNEL.md`](./CLOUD_BULK_CHANNEL.md) | PC 大量素材 → 百炼质量门脚本 |
| [`WINDOWS_MOBILECLIP_BFF.md`](./WINDOWS_MOBILECLIP_BFF.md) | 本机 MobileCLIP 权重 + 视频语义选帧 |
| [`TEST_LOG.md`](./TEST_LOG.md) | 把每次结果记这里 |

**明确不做进本轮内测：** 真耳机 BLE、全员本机 Vision、本地自训小模型上云、精细订阅计费。

---

## 0. 你现在到底在哪（读完再动手）

| 能力 | 状态 | 说明 |
|------|------|------|
| Expo Go 四 Tab + 入门/问卷 UI | ✅ 可测 | 细节见 `EXPO_GO_FULL_TEST_GUIDE.md` |
| 相册/Demo → Bundle → BFF → Diary chapter | ✅ 可测 | Expo Go：Lab A/B；**TestFlight 内测包：Device → Import photos（须 OTP）** |
| 本机 Docker 量产栈（Postgres/Redis/MinIO/BFF/Worker） | ✅ 代码齐 | `up-docker-stack.ps1` |
| 本机 Dev Lite（无 Docker 也行） | ✅ | 仅同 Wi‑Fi 几台手机 |
| DashScope / 真 qwen | ⚠️ 看 Key | `set-dashscope-key.ps1`；无 Key 常走 mock |
| MobileCLIP 权重（本机） | ✅ 已可部署 | 权重在参考包 `checkpoints/`；Ping 看 `mc=yes` |
| 公网 HTTPS BFF | ❌ 你还没立 | **几十人卡在这里**（代码/脚本已齐，缺部署） |
| 每用户日配额 | ✅ 已落地 | `DAY_REVISION_DAILY_LIMIT` 默认 8；超限 429 |
| TestFlight / EAS preview | ⏳ `eas.json` 已留公网 URL 占位 | 需填域名 + Apple 账号 + `eas build` |
| 「大量用户各自稳定 chapter」 | ❌ 未成立 | 完成 **阶段 C**（公网 HTTPS）后才算 |

**两句话：**

1. **你自己 / 同 Wi‑Fi 联调** → 走阶段 A（+ 可选 B 质量）。  
2. **马上几十人各自出 chapter** → 必须走阶段 C（公网量产栈 + 关 mock + OTP + 粗配额 + TestFlight/固定入口）。

---

## 商用 / 内测总序（不要跳阶段）

| 阶段 | 名称 | 谁用 | 通过标准 |
|------|------|------|----------|
| **A** | Expo Go 本机全量验收 | 你自己 | `EXPO_GO_FULL_TEST_GUIDE` 商用表 0–30 + 本文 A 勾选 |
| **B** | 真 qwen 质量门 | 你自己 | `ALLOW_MOCK_PREVIEW=false`；真图出 grounded chapter；无 `mock_fallback` |
| **C** | 几十人内测底座 | 内测员 | 公网 Ping 通；每人 OTP；各自 job→chapter；有日配额 |
| **D** | 分发与值守 | 内测员 | TestFlight 或固定 Expo 入口；发简短说明；有人盯失败 job |

每步只记 □ 通过 / ✖ 失败（失败就停，截图 + Lab Ping **整行**）。

---

# 阶段 A · Expo Go 本机全量（你现在就能测）

细节按钮、问卷文案、像素清单：**以 [`EXPO_GO_FULL_TEST_GUIDE.md`](./EXPO_GO_FULL_TEST_GUIDE.md) 为准**。下面是与**当前代码**对齐的总表 + 电脑启动。

## A0 · 电脑每次开测

手机和电脑同一 Wi‑Fi。BFF 必须是 **`192.168.x:8790`**，**不能是** `172.22.x`（WSL，手机连不上）。

### 路线 1 · Docker 量产（推荐，贴近几十人内测）

```powershell
# 1) Docker Desktop → Running
cd E:\AI耳机\diary-one\services\bff
.\scripts\up-docker-stack.ps1

# 2) 千问 X02（compose 里 BFF 连 host.docker.internal:8787）
.\scripts\start-x02.ps1

# 3) 写 App .env 为 WLAN IP
.\scripts\setup-commercial-dev.ps1

# 4) Metro
cd E:\AI耳机\diary-one\apps\mobile
npx expo start --go --lan
```

### 路线 2 · Dev Lite（无 Docker / 快起）

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\setup-commercial-dev.ps1
# UI 冒烟（默认 mock）：
.\scripts\start-dev-lite-background.ps1
# 或真 qwen（要 Key）：
.\scripts\start-dev-lite.ps1 -Adapter qwen
```

**不要**同时开 Dev Lite 和 Docker（抢 `:8790`）。

浏览器：`http://127.0.0.1:8790/health` 应有 JSON。  
防火墙（管理员一次）：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\setup-commercial-dev.ps1 -OpenFirewall
```

### MobileCLIP（视频语义选帧，可选但已接好）

权重路径（已下载脚本）：

```text
E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router\checkpoints\mobileclip_s0.pt
```

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\download-mobileclip-s0.ps1   # 若尚未下载
.\scripts\start-dev-lite.ps1          # 会探测 checkpoint；health.mobileclip.available
```

说明见 `WINDOWS_MOBILECLIP_BFF.md`。  
**注意：** MobileCLIP 在 **跑 BFF 的那台机**上；公网几十人时要么装到公网机，要么视频走退化选帧（照片出 chapter 不依赖它）。

## A1 · 商用一次过完（必须按序）

已经停在四个 Tab：先 **Account → Phone test · cloud loop → Replay sign-in (onboarding) ›**，回到 **Sign in to Diary One**。

| 序 | 你做什么 | 通过标准 |
|----|----------|----------|
| 0 | 电脑 health、Metro、同一 Wi‑Fi、Reload | `127.0.0.1:8790/health` 有 JSON；弹窗 BFF 不是 `172.22` |
| 1 | 登录页认路 | Apple / Google / Email / **Skip to Diary (no device)** / **Continue with Email** |
| 2 | iPhone：**Continue with Apple**（可取消）；Android：提示用 Google/邮箱 | 不崩溃、不假登录 |
| 3 | **Continue with Google** | 未配 ID → **Google Client ID missing** |
| 4–7 | 邮箱 OTP：空邮箱灰钮 → 真邮箱收码 → 错码 → 正确码 | 进 **Pair your Diary One** |
| 8–11 | 配对失败链 + **Continue without a device** + 权限四页 | **SETUP COMPLETE** |
| 12–13 | Device basics 1–7 + 问卷 8 屏（第 8 屏先选 **Agree and continue**） | 进四 Tab；**不要** Skip for now |
| 14 | **Device** | **Not connected** / **Unavailable** / 灰 Sync / 无假电量 |
| 15–16 | Lab：**1 Apply** → **1b consent** → **2 Ping** | `OK` · `x02=up` · `ffmpeg=yes`；看 `mc=` / `mock=` |
| 17 | **0 · Offline mock Diary** | Diary 有 **Offline test memory** |
| 18 | **A · Demo photo → cloud → Diary** | Active tasks 成功（mock 或真章均可先记） |
| 19 | **A2 · Simulation video** | 成功；Motion 可点 |
| 20 | iPhone **B · Import from photo library**（1～3 张真图） | 成功或诚实失败；Android ⚠ 可改 A |
| 21–22 | Diary Share memory / Share day（拼贴、插画、Recap） | Preview / MP4；`ffmpeg=no` 则先修电脑 |
| 23 | Memory 搜 `Fishing`；Captured / Topics | 搜索成功 |
| 24 | Device Lab link → Sync / Automatic Capture / Unpair | 不冒充云端章节 |
| 25–28 | Account 资料 / Privacy 关同意再 Demo 应拦住 / Log out | 同意拦截必过 |
| 29 | Replay → **Skip to Diary** | 内测捷径仍在 |
| 30 | Lab **C · Semantic route debug** | `mc=yes` → `remote_bff`+MOBILECLIP；否则 degraded **可记日志** |

**本轮允许不通过（写日志，不挡其余）：** 真 BLE、Google 真登录、Android 相册 B、原生 Vision。

## A2 · Lab Ping 怎么读（当前代码）

成功行大致：

```text
OK · x02=up · ffmpeg=yes · mc=yes|no · mock=yes|no · http://192.168.x:8790
```

| 字段 | 含义 |
|------|------|
| `x02=up` | 算法预览可达 |
| `ffmpeg=yes` | Daily Recap 能出 MP4 |
| `mc=yes` | MobileCLIP 权重已加载（视频真向量） |
| `mc=no` | 视频会 degraded / 直方图 fallback；**照片 chapter 仍可测** |
| `mock=yes` | 空日可能 mock 章节；**不算质量验收** |
| `mock=no` | 质量门模式 |

## A3 · 本地「轻处理」你在测什么

**照片：** 校验 → SHA 去重 → 768×1024 JPEG → Bundle → 上云。  
**视频：** 探针帧 →（BFF MobileCLIP 512-d 或 fallback）→ 手机规则选 1/3/5/10 帧 → 再压图 → 上云。  
**云端：** Worker → X02（qwen 或 fixture）→ chapters 回 Diary。

照片路径**不跑**语义选帧。

## A4 · 阶段 A 勾选

```
电脑 health / Metro / 非 172.22：□
Skip 或 OTP 进四 Tab：□
配对诚实失败 + 无设备权限链：□ / 未跑
问卷 8 屏（Agree and continue）：□ / 未跑
Lab Apply + Ping（记下 mc= mock=）：□
Offline mock：□
A Demo 云端：□
A2 视频：□
B 真图（iPhone）：□ / ⚠
同意拦截：□
Share 拼贴 / 插画 / Recap：□
Memory / Device Lab link / Account：□
Lab C（MobileCLIP 或 degraded）：□
像素清单 EXPO_GO §10.1：□ / 另测
```

认路、问卷原文、Share 与像素：**打开 `EXPO_GO_FULL_TEST_GUIDE.md` 第 1–10 章跟着点。**

---

# 阶段 B · 真 qwen 质量门（关 mock）

**目标：** 证明「筛选/出稿」是真算法，不是 mock 糊弄。

## B1 · Key

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\set-dashscope-key.ps1 -Key "sk-你的密钥"
```

写入 Windows **用户**环境变量（勿提交 Git）。  
启动脚本会读 User 级 `DASHSCOPE_API_KEY`。仓库 `.env` 可以没有 Key。

## B2 · 关 mock 起栈

**Dev Lite：**

```powershell
.\scripts\stop-dev-lite.ps1
.\scripts\start-dev-lite.ps1 -Adapter qwen
# 不要用 start-dev-lite-background（固定 fixture + mock）
```

**Docker：** 在 `services/bff/.env` 或启动环境设：

```text
ALLOW_MOCK_PREVIEW=false
DASHSCOPE_API_KEY=sk-...
```

然后 `up-docker-stack.ps1` + `start-x02.ps1`。  
一键质量通道（PC pack）：

```powershell
.\scripts\open-cloud-bulk-channel.ps1 -Quality -MediaDir D:\packs\day1 -RequireGrounded
```

## B3 · 手机验收（不要用 Demo JPEG 当质量）

1. Lab Ping：`mock=no`（或至少任务结果无 mock_fallback）  
2. **B · 真相册** 2～5 张今天拍的日常图（或短视频）  
3. Active tasks **succeeded**  
4. Diary 出现 **有内容的 chapter**（不是空日糊弄）  
5. 可选：Lab C 在 `mc=yes` 时确认视频 `remote_bff`+MOBILECLIP  

## B4 · PC 大量素材（与 App 同合同）

见 `CLOUD_BULK_CHANNEL.md`。

- Bundle：**V04** 768×1024  
- `-RequireGrounded`：禁止 `dev_lite_fallback`、禁止空 chapters/ahas  
- 上限：约 240 assets / day  

## B5 · 阶段 B 勾选

```
DASHSCOPE Key 已写入 User env：□
ALLOW_MOCK_PREVIEW=false：□
Ping / 任务无 mock_fallback：□
真图 Lab B → 真 chapter：□
PC -RequireGrounded pack（可选）：□
```

---

# 阶段 C · 几十人各自稳定 chapter（必须做完才算内测底座）

本机 Dev Lite **不能**支撑几十人。要立的是：

> **公网可访问的 Docker 量产 BFF + 真 qwen + 关 mock + OTP + 粗配额 + App 指向公网 URL**

## C1 · 架构（内测最小）

```text
每人手机（Expo Go 或 TestFlight）
  → HTTPS 公网 BFF :443→8790
  → Postgres / Redis / MinIO（同机 Docker）
  → Worker → X02(:8787) → 百炼 DashScope
  → job succeeded → App mapPreviewToDiary → 各自 Diary chapter
```

| 组件 | 已有？ | 你要做的 |
|------|--------|----------|
| `docker-compose.yml` BFF+Worker+PG+Redis+MinIO | ✅ | 部署到云主机或隧道后的机器 |
| X02 + Key | ✅ 脚本 | 同机常驻；Key 进环境 |
| OTP + SMTP | ✅ QQ SMTP 已在 `.env` | 确认任意测试邮箱能收码 |
| `session_token` Bearer | ✅ | 内测员必须 OTP 登录，禁用共用裸 `dev-token` |
| 公网 HTTPS | ❌ | 云主机 443 或 Cloudflare Tunnel / frp |
| App `EXPO_PUBLIC_BFF_BASE_URL` | ✅ 读 .env | 改成 `https://你的域名` |
| 每用户日配额 | ✅ | `DAY_REVISION_DAILY_LIMIT`（默认 8）→ 超限 **429** |
| Worker 并发限制 | ✅ | `WORKER_MAX_CONCURRENT`（默认 1） |
| MobileCLIP 公网 | 可选 | 不装则视频 degraded；照片主路径不受影响 |

## C2 · 云主机部署清单（D1–D2）

任选：**阿里云/腾讯云 2～4 核 8G+**，或办公室 PC + Tunnel。

```text
□ 机器常开，安全组放行 80/443（及 SSH）
□ 安装 Docker + docker compose
□ git clone / 拷贝 services/bff
□ 配置 .env：
    DASHSCOPE_API_KEY=sk-...
    ALLOW_MOCK_PREVIEW=false
    API_TOKEN=<长随机串，勿用 dev-token>
    SMTP_* = 可用发信账号
    EXPOSE_OTP_IN_RESPONSE=false
    DAY_REVISION_DAILY_LIMIT=8
    DAY_REVISION_MAX_INFLIGHT=2
    WORKER_MAX_CONCURRENT=1
□ 质量栈一键：
    cd services/bff
    .\scripts\prepare-multiuser-beta.ps1 -Up
    （或 `docker compose -f docker-compose.yml -f docker-compose.quality.yml --env-file .env up -d --build`）
□ 同机或旁路启动 X02（compose 已用 host.docker.internal:8787）
□ 域名 + HTTPS（Caddy / Nginx / Cloudflare）反代到 8790
□ 浏览器打开 https://你的域名/health → JSON（`allow_mock_preview=false`，可见 `day_revision_daily_limit`）
□ PC：smoke-cloud-pack.ps1 -RequireGrounded → 有 chapters
```

**Tunnel 临时方案（办公室 PC）：** Cloudflare Tunnel / frp 把本机 8790 映到 HTTPS。机器关机 = 全员不可用，只适合短窗口内测。

## C3 · App 指向公网（D2）

`apps/mobile/.env`（示例）：

```text
EXPO_PUBLIC_DEV_BFF_URL=https://bff.your-domain.com
# 可选别名（同义）：EXPO_PUBLIC_BFF_BASE_URL=https://bff.your-domain.com
EXPO_PUBLIC_DEV_BFF_TOKEN=<与服务器 API_TOKEN 一致；内测员优先 OTP，可不依赖此 token>
```

然后：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npx expo start --go --lan
```

内测员 Lab：**1 Apply → 2 Ping**。  
通过标准：Ping **OK**，URL 是 **https 公网**，不是 `192.168`。

TestFlight：改 `eas.json` → `preview.env` 里的 `EXPO_PUBLIC_DEV_BFF_URL` / token 占位，再 `eas build --profile preview`。`EXPO_PUBLIC_INTERNAL_BETA=1` 会强制灌入该 URL（覆盖手机里旧的 LAN 地址）。

## C4 · 粗配额（已落地）

| 规则 | 默认 | 实现 |
|------|------|------|
| 每用户每天 day-revision | 8 | `shared/quota.py` + Dev Lite / Docker BFF；按 OTP email（或 lab API token）计数 |
| 超限 | **429** + `day_revision_quota_exceeded` | App 显示 `Upload limit (429): …` |
| 每用户 inflight | 2 | pending+processing 超限同样 429 |
| Worker 并发 | 1 | `WORKER_MAX_CONCURRENT`（ThreadPool） |
| Job 归属 | OTP email | `CloudJob.owner_email`；jobs GET 校验 |
| 单日 assets | ≤240 | 已有合同 |

验收：

```
同一账号连续上传超过日限 → 被拒且不扣死机器：□
两个邮箱各上传 1 次 → 各有自己的 job/chapter：□
/health 含 day_revision_daily_limit：□
```

## C5 · 账号纪律（几十人）

```
□ 每人用自己的邮箱 OTP（Continue with Email）
□ 禁止把 API_TOKEN 当「全员万能钥匙」写进群公告长期共用
□ EXPOSE_OTP_IN_RESPONSE=false（码只走邮箱）
□ Privacy：测云端必须 Allow cloud evidence upload
□ 日记展示以手机本地为准；云端保证 job 成功回写
```

`CloudJob.owner_email` 已绑 OTP 邮箱；session 用户 GET 他人 job → 404。

## C6 · MobileCLIP 在几十人场景

| 选择 | 何时 |
|------|------|
| **A. 公网机也装权重 + torch** | 要验收视频真语义选帧 |
| **B. 不装** | 视频 degraded fallback；**用照片验收 chapter**（推荐先这样开内测） |
| **C. 只有你本机权重** | 仅你联调；内测员连公网 BFF 时 `mc=no` |

不要让 40 人 VPN 连你笔记本。

## C7 · 阶段 C 勾选

```
公网 https://…/health：□
ALLOW_MOCK_PREVIEW=false + Key：□
API_TOKEN 已换非 dev-token：□
DAY_REVISION_DAILY_LIMIT + Worker 并发已配：□
外网手机 Ping OK：□
邮箱 A OTP → 真图 → chapter：□
邮箱 B OTP → 真图 → chapter（互不覆盖）：□
日配额补丁已上 + 超限可测：□
Worker 未排队死锁 / 能消化积压：□
```

---

# 阶段 D · 分发、说明、值守

## D1 · 分发方式

| 方式 | 适合 | 命令 / 入口 |
|------|------|-------------|
| **Expo Go + Metro/Update** | 技术向、快速改 JS | `npx expo start --go`；或 EAS Update |
| **EAS preview → TestFlight** | 普通人、几十人 | 见下 |

`eas.json` 已有 `preview`（`EXPO_PUBLIC_INTERNAL_BETA=1`，`INCLUDE_VISION=1`）。

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npx eas-cli login
npx eas-cli init          # 若尚未 link
# 在 eas.json preview.env 写入公网 BFF URL
npx eas-cli build --platform ios --profile preview
# Asc App ID 填进 eas.json submit.preview 后：
npx eas-cli submit --platform ios --profile preview
```

Windows 出 iOS 包靠 **EAS 云构建**，不需本机 Xcode。  
**preview ≠ App Store 上架**；上架用 `production` profile。

## D2 · 发给内测员的最短说明（可复制）

```text
1. 安装：TestFlight 链接（推荐）/ 或 Expo Go + 我们发的入口
2. 语言：Account → Language → English（对照手册时）
3. 登录：Continue with Email → 收 6 位码（查垃圾箱）
   ※ 内测包禁止共用 API token；必须每人自己的邮箱 OTP
4. 配对：Continue without a device → 权限 Continue → 问卷最后一屏选 Agree and continue
5. 登录：Account → **Continue with Email** → OTP（不必重跑硬件 onboarding）
6. 隐私：**必须** Account → Privacy & Data → Allow cloud evidence，或跑 Preference / cloud consent survey（选 Agree）
7. 上传（TestFlight）：Device →「Import photos → cloud → Diary」→ 选 2～5 张真实照片（Android 会逐张「Add another」）
   （Expo Go 技术联调才用 Lab A/B；不要让普通内测员进 Lab）
7. 等待：Active tasks 成功 → Diary 看当天 chapter（真 qwen 可能要几分钟）
8. 换人测同一手机：先 Account → Log Out（会清空本机记忆，避免串号）
9. 出问题：截图失败原文 + 邮箱（打码）发回；不要截 Lab（TestFlight 没有 Lab）
```

**部署方务必：** `eas.json` preview 填公网 `EXPO_PUBLIC_DEV_BFF_URL`；`EXPO_PUBLIC_DEV_BFF_TOKEN` 留空；BFF `ALLOW_MOCK_PREVIEW=false` + SMTP + `API_TOKEN≠dev-token`。

**不要测：** 真耳机、假电量、未开放的 Google 登录、共享 Bearer 冒充多人。

## D3 · 你侧值守

```
□ 云主机磁盘 / MinIO 不爆
□ 百炼控制台额度与账单
□ 失败 job 可查（日志 / DB）
□ 机器重启后 compose + X02 自动或有人拉起
□ 内测群：已知问题列表（Android 相册、Expo Go 无 Vision、视频无 mc 等）
```

## D4 · 阶段 D 勾选

```
TestFlight 或固定 Expo 入口发出：□
5 人试跑通过再扩到几十：□
说明文档已发：□
值守人 / 值班窗口明确：□
```

---

# 总时间线（建议 7 天）

| 天 | 事 | 完成标准 |
|----|----|----------|
| **D0** | 阶段 A 你自己 Expo Go 过完 | A4 勾选大半绿 |
| **D1** | 云主机 + compose + Key + mock off | 公网 health；`-RequireGrounded` 出章 |
| **D2** | HTTPS + App 指公网 | 外网手机 Ping OK |
| **D3** | OTP 双账号各出 1 chapter；换 API_TOKEN | 隔离成立 |
| **D4** | 日配额补丁 + Worker 限并发 | 超限有明确错误 |
| **D5** | EAS preview / TestFlight 或 Expo 入口 | 5 人试跑 |
| **D6–7** | 扩到几十人；盯账单与失败 | 可重试；有人值守 |

---

# 总勾选（打印用）

```
【阶段 A · 本机 Expo Go】
A 全量 / Ping / A·A2·B / 同意拦截 / Share：□
Lab C MobileCLIP 或 degraded 已记录：□

【阶段 B · 质量】
Key + mock=no + 真图真章：□
PC bulk -RequireGrounded（可选）：□

【阶段 C · 几十人底座】
公网 HTTPS BFF：□
关 mock + 真 qwen：□
OTP 多用户隔离：□
粗配额 + 限并发：□
App/EAS 指向公网：□

【阶段 D · 分发】
TestFlight 或 Expo 入口：□
内测说明 + 值守：□
```

---

# 先看：哪些找不到 / 本轮不算过

| 旧说法 / 期望 | 现在实际 |
|---------------|----------|
| 底部蓝色 Skip | **暖棕色描边** **Skip to Diary (no device)** |
| 真耳机、真电量 | Expo Go **做不到**；约 3 秒 **No Diary One found** |
| Apple Vision 抽帧 | 仅 Dev Client / EAS（`INCLUDE_VISION=1`）；Go 里 Lab C 会写 `DiaryOneVision=no` |
| Demo JPEG 必有好故事 | 常 `NO_GROUNDED_MEMORY`；**质量用真相册** |
| 本机 Dev Lite = 几十人 | **否**；必须阶段 C 公网栈 |
| MobileCLIP 全员自动有 | 仅 BFF 机器有权重时 `mc=yes` |
| 弹窗立刻出 OTP 码 | 量产 `EXPOSE_OTP_IN_RESPONSE=false` → **去邮箱收** |

**这次不要拿来挡内测：** BLE、未配的 Google 真登录、Android Expo Go 相册、全员真 Vision、本地小模型。

---

# 报问题时带这些

1. 阶段：A / B / C / D  
2. Lab Ping **整行**（含 `mc=` `mock=` URL）  
3. Active tasks 失败原文  
4. 浏览器 `https://…/health` 或 `http://127.0.0.1:8790/health`  
5. 是否公网、是否 OTP 登录、邮箱域名（打码）  
6. iPhone / Android；Expo Go 或 TestFlight  
7. 是否真图还是 Demo  

记入 `docs/TEST_LOG.md`。

---

# 和「算法还要不要补」的关系

| 项 | 几十人内测 |
|----|------------|
| V1.75 筛选/出稿合同 | **不用重写**；与 eval / App Bundle 同合同 |
| 偏好 → 云端软筛选 | **已接通** `APP_CLIENT_PROFILE_V01`（见 `ALGORITHM_CLIENT_PROFILE.md`） |
| Docker BFF + Worker | **部署 + 关 mock**，不是新算法 |
| 粗配额 | **小补丁**（产品纪律），不是新模型 |
| MobileCLIP | **上云前轻处理**；照片主路径可先不依赖 |
| 本地自训模型 | **另轨**，不挡本轮 |

**算法本体不必为了开几十人内测再补一套；缺的是公网量产底座 + 质量开关 + 配额 + 分发。**
