# 前后端清点（2026-10-02 · 开测版）

对照：你要的功能清单 · Figma 04 · Dev Lite · Expo Go 内测

## 总览（两套口径）

| 口径 | 完成度 | 说明 |
|------|--------|------|
| **Expo Go 全功能试跑**（不含 BLE / 真 Vision / EAS / Docker / 真 qwen） | **~90%** | 代码+PC 冒烟齐；**真机勾选仍 ⬜** |
| **全产品野心（代码）** | **~70–75%** | 见 `FULL_PRODUCT_CODE_PUSH.md`；密钥/引擎/硬件另计 |
| **全产品野心（含外部验收）** | **~55–60%** | 无 Key / 无 Docker 引擎 / 无 Apple 账号时验收不过 |

| 区域 | 完成度 | 说明 |
|------|--------|------|
| App 消费者主链（Figma 04） | ~95% | 问卷+Share 拼贴/插画/Recap；Motion 真资源 ⚠️ |
| Dev Lite 联调后端 | ~95% | health/OTP/Demo/Recap/Collage 冒烟过 |
| 量产 Docker BFF | ~75% | 脚本齐；本机卡 WSL2 |
| 真算法 V1.75 | ~40% | 路径齐，无 Key 无法验质量 |
| Expo Go 内测主链 | ~90% PC | 真机见 `TEST_LOG` |
| 上架 / EAS / BLE | ~10% | 明确暂缓 |

---

## A. 你必须做（开发侧无法替你）

| ID | 项 |
|----|-----|
| U1 | `DASHSCOPE_API_KEY` → 真 qwen |
| U2 | SMTP → 真 OTP、关 `expose_otp` |
| U3 | 手机 Expo Go 真机验收（TEST_PLAN） |
| U4 | Apple Developer + EAS Dev Client（真 Vision） |
| U5 | 硬件 BLE 合同后接线 |
| U6 | **启用 WSL2 并让 Docker Desktop = Running**，再跑 `.\scripts\up-docker-stack.ps1` |

---

## B. 代码侧还可做（本轮起）

| ID | 项 | 优先级 |
|----|-----|--------|
| C1 | `stop-dev-lite.ps1` 停 8787/8790 | ✅ |
| C2 | Account/Privacy 展示云同意状态 | ✅ |
| C3 | Docker healthcheck + README | ✅ |
| C4 | 更新进度板 | ✅ |
| C5 | Dev Lite 简易请求日志 | ✅ |
| C6 | Chapter Motion 真短视频资源（需素材） | P2 后置 |
| C7 | `up-docker-stack.ps1` 一键 compose | ✅ 脚本已写；引擎卡在本机未启用 WSL2 |
| C8 | 量产 BFF access log + 鉴权 401 对齐 | ✅ |
| C9 | 语义端点 Bearer | ✅ |
| C10 | Account 云同意开关 + pipeline 文案 | ✅ |
| C11 | Recap 临时目录清理 + hasAudio 修正 | ✅ |
| C12 | `tests/test_share_recap.py` | ✅ 4 passed |
| C13 | 模拟失败仅 `__DEV__` | ✅ |
| C14 | 云同意 fail-closed（null 也拦） | ✅ |
| C15 | Recap hasAudio 按混音实报 | ✅ |
| C16 | 量产 Session 落盘 + evidence 语义路由 | ✅ |
| C17 | 空 API_TOKEN 不放行垃圾 Bearer | ✅ |
| C18 | fixture 空记忆 mock 回写 + smoke-demo-day | ✅ |
| C19 | Expo Go 路径文档 / .env 写 apps/mobile | ✅ |
| C20 | 云主链：禁假成功 / 默认 production / poll / Recap / Lab Ping mock | ✅ |
| C21 | 问卷后续：Account 重填、pairing→权限链、Avoid 上云格式、共享 formatter | ✅ |
| C22 | Expo Go Share：真拼贴/插画走 BFF Pillow；Recap **仅** PC ffmpeg；素材校验 | ✅ |
| C23 | 全产品代码推进：BLE transport、SMTP 对齐、EAS/Vision、Docker smoke、qwen 无 Key 降级 | ✅ |

---

## C. 已完成（勿重复开工）

- Dev Lite：health / OTP / day-revisions 幂等落盘 / jobs / recap ffmpeg / collage+illustrated / session Bearer  
- App：四 Tab、Share（拼贴/插画/Recap）、问卷、语义路由规则、校验去重抽帧、Lab  
- 量产：OTP shared、day-revision 幂等、share_recap / share_compose 路由、镜像含 ffmpeg  

## D. Expo Go **不能**在本轮闭环（需原生 / 外部）

| 项 | 原因 |
|----|------|
| 真耳机 BLE / 电量 / 真自动采集 | 无 BLE SDK；需硬件合同 + Dev Client |
| 真 Apple Vision 抽帧 | `DiaryOneVision` 仅 Dev Client / EAS |
| iOS 本机合成 Recap | 与「Recap 必须 PC ffmpeg」冲突；Go 禁用原生编码 |
| Docker 量产栈 / 真 SMTP / TestFlight | 本机引擎 / 凭证 / Apple 账号，非 App 代码 |