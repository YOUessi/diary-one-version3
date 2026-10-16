# 全产品野心 · 代码推进说明（2026-10-02）

完成度被「外部依赖」拖低 ≠ 代码没写。本轮把**仓库内可完成的接线**补齐后的口径：

| 区域 | 代码完成度（估） | 仍需你提供 |
|------|------------------|------------|
| BLE 传输抽象 + 诚实配对 + 自动采集下发 | **~75%** | 厂商 GATT / SDK |
| Vision 模块 + EAS Dev Client 挂载 | **~85%** | `eas build` + Apple 证书 |
| Docker compose + health + 全链路 smoke | **~90%** | 本机启用 WSL2 / Docker 引擎 |
| SMTP（量产对齐 Dev Lite） | **~95%** | 真实 SMTP 账号密码 |
| EAS / TestFlight 配置 | **~80%** | `eas init` projectId + Asc App ID + 上传 |
| Qwen adapter + 无 Key 降级 | **~90%** | `DASHSCOPE_API_KEY` |

**全产品野心综合：约 70–75%（代码）**；挂密钥/引擎/硬件后可达验收。

## 本轮落地

- `device/deviceTransport` + Lab / StubBle；`deviceSyncService` 走 transport
- 配对搜索不再假成功；`hardware_linked` 状态位预留
- 量产 BFF：SMTP 自动关 `expose_otp`；`/health` 暴露 smtp/x02 modelReady
- `start-dev-lite.ps1` 无 Key 自动 fixture+mock（不再 exit 1）
- Vision `app.plugin.js` Info.plist；`eas.json` 显式 `INCLUDE_VISION`
- `app.json` Bluetooth / Local Network 用途说明
- Docker healthcheck + 扩展 `smoke-docker.ps1`
- Privacy/Terms 可点 `EXPO_PUBLIC_*_URL`
