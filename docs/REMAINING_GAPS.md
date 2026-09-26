# 前后端剩余缺口（2026-09-26）

对照：`DEVELOPMENT_ROADMAP` · `BACKEND_ROADMAP` · `YOUR_TURN` · Figma 覆盖表

## 总览

| 区域 | 完成度（估） | 说明 |
|------|-------------|------|
| App 消费者主链（Figma 04） | ~95% | 问卷已加；Motion 像素/真资源 ⚠️ |
| Dev Lite 联调后端 | ~90% | 缺你侧 Key/SMTP 真测 |
| 量产 Docker BFF | ~70% | compose 有；本机一键验 worker 未强制跑通 |
| 真算法 V1.75 | ~40% | 代码路径齐，**无 Key 无法验收质量** |
| 上架 / EAS / BLE | ~10% | 明确暂缓或依赖外部 |

---

## A. 你必须做（开发侧无法替你）

| ID | 项 |
|----|-----|
| U1 | `DASHSCOPE_API_KEY` → 真 qwen |
| U2 | SMTP → 真 OTP、关 `expose_otp` |
| U3 | 手机 Expo Go 真机验收（TEST_PLAN） |
| U4 | Apple Developer + EAS Dev Client（真 Vision） |
| U5 | 硬件 BLE 合同后接线 |

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

---

## C. 已完成（勿重复开工）

- Dev Lite：health / OTP / day-revisions 幂等落盘 / jobs / recap ffmpeg / session Bearer  
- App：四 Tab、Share、问卷、语义路由规则、去重抽帧、Lab  
- 量产：OTP shared、day-revision 幂等、share_recap 路由、镜像含 ffmpeg  
