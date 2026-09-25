# Diary One · iOS App 开发总规划（仓库版）

与 Canvas「Diary One · iOS App 开发总规划」同步；**以本文件 + `FIGMA_04_COVERAGE.md` 为执行状态源**。

## 阶段总览

| 阶段 | 名称 | 状态（2026-09-23） |
|------|------|-------------------|
| P0 | 壳层对齐（Tab/导航/Token/六组件/假数据） | ✅ 完成 |
| P1 | Diary 主链 UI（七态/日历/Detail/Story/播放） | ✅ 完成 |
| P2 | Memory + Account（搜索/Captured/Topics/本机资料） | ✅ 完成 |
| **P3** | **端侧素材链路（相册→Bundle→账本→任务机）** | **✅ Dev 可测（Expo Go Lab）** |
| **P4** | **云端算法对接（BFF→Worker→X02→写回 Diary）** | **🔄 Dev Lite 已通；量产 Docker 另轨** |
| P5 | EAS iOS / TestFlight | ⏳ 未开始 |

**仓库布局**：移动端 `diary-one-app/` · 后端 `diary-one-server/`（前后端分文件夹）。

## Sprint 切片

| Sprint | 交付 | 状态 |
|--------|------|------|
| S1–S5 | 壳层 + Diary + Memory + Account + Share UI | ✅ |
| **S6** | 相册选入 + Evidence Bundle + 本地任务 + 账本 | **🔄 本迭代** |
| **S7** | 研究 API 提交 → 校验 → `applyDiaryDayUpdate` | **🔄 已有代码，待 M2 实机联调** |
| S8 | EAS Build + 回归 | ⏳ |

## M2 验收（当前首要）

1. PC：`diary-one-server\scripts\start-dev-lite.ps1`（无 Docker；见 `../diary-one-server/docs/EXPO_GO_DEV_LITE.md`）。  
2. Account → **Internal lab** → Production BFF = `http://<LAN>:8790` · Token `dev-token`。  
3. **Import from photo library** → Bundle V04 → job → Diary 出现 Chapter / Small Memory。  
4. 登录：邮箱 OTP 经 BFF；内测弹窗显示 `dev_code`（无真实邮件前）。  
5. 失败 **Today = PARTIAL**，任务列表可见错误，不伪装 Empty Day。

真 V1.75 算法需本机 `DASHSCOPE_API_KEY` + `-Adapter qwen`；无 Key 时用 fixture + Mock 回写验管线。

## 纪律（不变）

- 来源 `PHOTO_LIBRARY_TEST` 不进消费者 Captured 叙事。  
- Sync（设备→手机）≠ Cloud Processing。  
- 未接硬件：Not connected，不造假电量/同步。
