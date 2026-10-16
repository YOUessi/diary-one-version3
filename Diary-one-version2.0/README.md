# Diary One（Nexleap）

一句话：用户把照片/视频交给 App，本地先做轻处理，再上云跑算法，最后在 Diary 里看到自己的 **chapter（日记章节）**。

本仓库是 **iOS 内测 / 商用形态** 的开发仓：手机 App、BFF 云接口、算法联调、测试手册都在这里。

---

## 现在做到哪了（汇报口径）

### 已经能演示的

1. **Expo Go 真机**：登录 / Skip、配对失败诚实提示、问卷、四个 Tab（Diary / Memory / Device / Account），UI 按 Figma 对齐可测。  
2. **云端出 chapter**：相册或 Lab Demo → 去重压缩（视频可语义选帧）→ 上传 BFF → Worker → X02/千问 → Diary 出章节。  
3. **本机联调两套后端**：  
   - Dev Lite（不起 Docker，适合自己同 Wi‑Fi 调试）  
   - Docker 量产栈（Postgres + Redis + MinIO + BFF + Worker，更接近以后给别人用）  
4. **视频语义轻处理（可选）**：Windows BFF 接 MobileCLIP 权重后，可出 512 维向量；手机规则再选 1/3/5/10 帧。没权重时会降级，链路仍能走通。  
5. **分享**：拼贴、插画、Daily Recap（电脑要有 ffmpeg）。

### 还没到「几十人各自稳定出 chapter」

本机 Dev Lite / 家里 Wi‑Fi **只能给几台手机用**。  
要马上内测几十人，还需要：

- 一台 **公网 HTTPS** 的量产 BFF（云主机或隧道）  
- **真千问 Key + 关掉 mock**（否则空日可能是假章节）  
- 每人 **邮箱 OTP** 登录（账号隔离）  
- **粗配额**（`DAY_REVISION_DAILY_LIMIT` / Worker 并发）——已落地；公网 HTTPS 仍需你部署  
- **TestFlight / 固定 Expo 入口** 发给内测员  

细节步骤与勾选表见下面「怎么测 / 怎么内测」。

### 明确先不做

真耳机 BLE、全员本机 Apple Vision、本地自训小模型上云、精细订阅计费。这些不挡当前软件内测。

---

## 仓库里有什么

```text
apps/mobile/          Expo React Native App（对标 Figma + PRD）
services/bff/         FastAPI：Dev Lite + Docker 量产 BFF/Worker
services/algorithm/   算法 / X02 联调
docs/                 测试手册、路线图、进度与缺口
```

---

## 你应该读哪两本手册

| 手册 | 干什么用 |
|------|----------|
| [`docs/EXPO_GO_FULL_TEST_GUIDE.md`](docs/EXPO_GO_FULL_TEST_GUIDE.md) | **自己用 Expo Go 真机怎么点**：登录、问卷、Lab、Share、像素勾选 |
| [`docs/INTERNAL_BETA_FULL_GUIDE.md`](docs/INTERNAL_BETA_FULL_GUIDE.md) | **内测总册**：本机验收 → 关 mock 质量门 → 公网几十人底座 → TestFlight/值守 |

相关补充：

- `docs/WINDOWS_MOBILECLIP_BFF.md` — MobileCLIP 权重怎么下、怎么看 Ping `mc=yes`  
- `docs/CLOUD_BULK_CHANNEL.md` — PC 大量素材走百炼质量门  
- `docs/TEST_LOG.md` — 测试结果往这记  

---

## 自己本机快速联调（阶段 A）

```powershell
cd services/bff
.\scripts\setup-commercial-dev.ps1
.\scripts\up-docker-stack.ps1      # 或 start-dev-lite-background.ps1
.\scripts\start-x02.ps1            # Docker 路线需要

cd ..\..\apps\mobile
npx expo start --go --lan
```

手机：同一 Wi‑Fi → Lab **Apply → Ping**（看 `x02` / `ffmpeg` / `mc` / `mock`）→ **A Demo** 或 **B 相册真图**。  
BFF 地址必须是 `192.168.x`，不能是 `172.22`（WSL，手机连不上）。

真算法质量：先 `.\scripts\set-dashscope-key.ps1 -Key "sk-..."`，再用 qwen 起栈并 **关 mock**（见内测总册阶段 B）。

---

## 产品纪律（别踩坑）

- Sync ≠ 云端出章节；未连接设备不造假电量  
- Tag 点了不会变筛选；Small Memory 没有详情页  
- Lab/测试导入的图不要当成用户长期「Captured by You」纪律  
- Demo 小图经常空日——**验收记忆质量请用真实照片**  
- 勿提交 `.env`、API Key、真实用户素材、MobileCLIP 权重大文件  

---

## 许可

私有仓（Nexleap-Tech）。Apple MobileCLIP 权重另受 Apple ML Research 许可约束，仅科研/非商业实验用途，勿随仓库分发。
