# Diary One（Nexleap）

一句话：用户把照片/视频交给 App，本地先做轻处理，再上云跑算法，最后在 Diary 里看到自己的 **chapter（日记章节）**。

本仓库是 **iOS 内测 / 商用形态** 的开发仓：手机 App、BFF 云接口、算法联调、测试手册都在这里。

---

## 现在做到哪了（2026-10-16）

几十人内测的**云端底座已经在跑**。测试员各自登录、相册导入、出 Chapter，都走公网 `https://bff.diary.luxe`，不再靠本机 Dev Lite 或家里 Wi‑Fi。

### 已经完成

1. **公网 HTTPS BFF**：阿里云 ECS，域名 `https://bff.diary.luxe`（Caddy → BFF）。密钥、千问 Key、SMTP 都在云主机上，不在本仓库。
2. **真千问、已关 mock**：相册图片/视频 → Evidence → BFF → Worker → X02/qwen → Diary Chapter。空日不会用假章节凑数。
3. **账号隔离**：邮箱 OTP（一个发信邮箱，测试员填自己的邮箱收验证码）。登录页同时有 Apple、Google、Email。
4. **配额已在云上生效**：每日修订上限、同时处理上限、Worker 并发。ECS 保持 Running 即可，不依赖打包的人的电脑开机。
5. **App 内测形态**：Bundle ID `com.nexleap.diaryone.dev`，`eas.json` 的 preview 已指向 `https://bff.diary.luxe`。设备页保持未连接，不造假电量。本轮不接耳机 BLE。

### 还没做完（交给同事打包）

安装包还没进 TestFlight。同事按 [`docs/同事_TestFlight打包详细步骤.md`](docs/同事_TestFlight打包详细步骤.md) 做完这三步：

1. Apple Developer 给 `com.nexleap.diaryone.dev` 勾选 **Sign in with Apple**，并把 App Store Connect 的数字 Apple ID 写入 `eas.json` 的 `ascAppId`。
2. 若要 Google 登录可用，填好 Web / iOS Client ID；不填也能先用 Apple 和邮箱 OTP。
3. `eas build --profile preview --platform ios`，再 `eas submit`，把 TestFlight 发给内测员。

### 明确先不做

真耳机 BLE、全员本机 Apple Vision、本地自训小模型上云、精细订阅计费、App Store 正式上架。这些不挡当前软件内测。

---

## 仓库里有什么

```text
apps/mobile/          Expo React Native App（对标 Figma + PRD）
services/bff/         FastAPI：Dev Lite + Docker 量产 BFF/Worker
services/algorithm/   算法 / X02 联调
docs/                 测试手册、路线图、进度与缺口
```

---

## 你应该读哪几本手册

| 手册 | 干什么用 |
|------|----------|
| [`docs/EXPO_GO_FULL_TEST_GUIDE.md`](docs/EXPO_GO_FULL_TEST_GUIDE.md) | **自己用 Expo Go 真机怎么点**：登录、问卷、Lab、Share、像素勾选 |
| [`docs/同事_TestFlight打包详细步骤.md`](docs/同事_TestFlight打包详细步骤.md) | **当前交接**：Apple / 可选 Google / EAS / TestFlight |
| [`docs/INTERNAL_BETA_FULL_GUIDE.md`](docs/INTERNAL_BETA_FULL_GUIDE.md) | 早期内测总册（公网底座已完成，其中「还要部署 HTTPS」的段落以本 README 为准） |

相关补充：

- `docs/WINDOWS_MOBILECLIP_BFF.md` — MobileCLIP 权重怎么下、怎么看 Ping `mc=yes`  
- `docs/CLOUD_BULK_CHANNEL.md` — PC 大量素材走百炼质量门  
- `docs/TEST_LOG.md` — 测试结果往这记  

---

## 自己本机快速联调（仅本地调试，不是当前内测入口）

当前内测不要走这条。测试包应连 `https://bff.diary.luxe`。下面只给还要在自己电脑上改代码的人：

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
