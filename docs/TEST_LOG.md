# Test log

## 2026-10-06 · 商用一次过完（Expo Go 真机）

**PC：** BFF production · smtp=true · ffmpeg=yes · X02 reachable · productionReady=true · `.env` `http://192.168.31.74:8790`

按 `EXPO_GO_FULL_TEST_GUIDE.md` **商用一次过完** 第 0–30 步勾选（手机填）：

```
0 电脑/Reload：□
1 登录页认路：□
2 Apple：□
3 Google 缺 ID 弹窗：□
4 空邮箱按钮灰：□
5 OTP 发到邮箱：□
6 错码：□
7 正确码进配对：□
8 搜设备失败：□
9 Simulate denied：□
10 无设备：□
11 权限四页 Continue：□
12 设备基础 7 步：□
13 问卷 Get started → Agree → Finish：□
14 Device 未连接诚实：□
15 打开 Lab：□
16 Apply + 同意 + Ping x02=up ffmpeg=yes：□
17 Offline mock：□
18 A Demo 云：□
19 A2 仿真视频云：□
20 B 相册：□ / ⚠
21 Diary Today（或旧库 Aug16）/ Your Story / 拼贴 / 插画ABC：□
22 Share day Recap MP4 + 日拼贴：□
23 Memory 搜索/Captured/Topics：□
24 Device Lab link / Sync / Capture：□
25 Account 资料/Plan/Privacy/通知/语言/Help/导出：□
26 关同意拦住 Demo：□
27 开回同意：□
28 Log Out：□
29 Skip 捷径补测：□
30 C Vision=no（记录，非失败）：□
现象：
```

---

## 2026-10-02 · 云端处理缺口补丁（代码）

对照 Expo Go 内测 plan · T2 云主链：

- **假成功已关**：无 BFF URL 时 pipeline **failed**，不再本地 mock succeed
- **默认 Production BFF**（不再默认空 Research）
- **轮询**：刷新 task message；succeeded 无 result → failed；网络错误可展示
- **Ping**：显示并告警 `allow_mock_preview`
- **Recap**：arrayBuffer→base64 写文件（避开 Expo Go FileReader/blob）
- **Device**：入口直达 Lab / Apply / Demo
- **空记忆**：Alert 提示开 mock；成功文案标 `mock fallback`

PC 冒烟仍有效：`smoke-demo-day` / `smoke-recap` · BFF mock=true · Metro :8081

---

## 2026-10-02 · Expo Go 内测就绪（PC）

**环境：** Dev Lite / Docker `http://192.168.31.74:8790` · X02 :8787 · 云端大量素材见 `docs/CLOUD_BULK_CHANNEL.md`（`open-cloud-bulk-channel.ps1`）  
**App .env：** `apps/mobile/.env` → `EXPO_PUBLIC_DEV_BFF_URL=http://192.168.31.74:8790` · token `dev-token`

| 用例 | 结果 | 说明 |
|------|------|------|
| T0.2 Dev Lite health | ✅ | mode=dev_lite · x02=up · ffmpeg=yes · mock=true |
| T0 OTP API | ✅ | `smoke-dev-lite` request/verify + session |
| T0 day-revision 幂等 | ✅ | same job_id |
| T0 job poll | ✅ | succeeded（空包走 mock） |
| T2.1 Demo→云（PC 等价） | ✅ | `smoke-demo-day.ps1` → Mock chapter（X02 EMPTY_DAY 回落） |
| T5.3 Recap MP4 | ✅ | `smoke-recap.ps1` → ~808KB mp4 |
| 防火墙 :8790 | ⚠ | 需**管理员**跑 `setup-commercial-dev.ps1 -OpenFirewall`（本机非管理员拒绝） |
| T0.1 Metro / Expo Go 真机 | ⬜ | 见下方手机清单（无 adb，需你扫码） |
| T0.4 Offline mock 真机 | ⬜ | Lab「0 · Offline mock」 |
| T1–T6 真机走查 | ⬜ | 对照 `TEST_PLAN.md` + `EXPO_GO_INTERNAL_BETA.md` |
| T7 真 qwen | ⏸ | `DASHSCOPE_API_KEY` 未配置 |

**本轮代码/文档修复：**

- fixture 后台默认 `ALLOW_MOCK_PREVIEW=true`；X02 空记忆时 mock 回写章节（Demo 能在 Diary 看到内容）
- `setup-commercial-dev.ps1` 写入 `apps/mobile/.env`（不再指向旧 `diary-one-app`）
- `EXPO_GO_DEV_LITE.md` / Lab Ping 文案 / Production API 说明改到 `diary-one/services/bff`
- 新增 `scripts/smoke-demo-day.ps1`、`docs/EXPO_GO_INTERNAL_BETA.md`
- Expo Go：`app.config.js` 默认不挂 Vision 插件（避免 Metro PluginError）；Dev Client 设 `EXPO_PUBLIC_INCLUDE_VISION=1`
- Metro：`npx expo start --go --lan` 已在 `apps/mobile` 起于 :8081（`.env` 已加载 LAN BFF）

### 手机勾选（请你补结果）

```
日期：2026-10-02
设备 / Expo Go：
BFF：fixture + mock
T0.1 Metro：⬜
T0.3 Lab Ping：⬜
T0.4 Offline mock：⬜
T1.1 Skip：⬜
T1.2 OTP 弹窗码：⬜
T2.1 Demo→Diary：⬜
T2.2 相册：⬜/⚠
T3 Diary 日历/Your Story：⬜
T4 Memory 搜索：⬜
T5 Share Collage/Illustrated/Recap：⬜
T6 Device 未连接 / Account：⬜
现象：
```

## 2026-09-27

- **unit** `pytest tests/`：9 passed（share_recap + api_auth）
- **typecheck** `apps/mobile`：见本轮
- **Docker**：仍卡 WSL2（`wsl` 未安装）

## 2026-09-26

- **unit** `pytest tests/test_share_recap.py`：4 passed（鉴权 401 / 缺 slide_count / 无 ffmpeg 503 / 成功 mp4）
- **typecheck** `apps/mobile`：通过
- **Docker**：Desktop 进程在，但引擎未 Running（日志：`backend is not running`）；`wsl` 未安装发行版 → `docker ps` 挂起。需本机启用 WSL2 后再跑 `up-docker-stack.ps1`

## 2026-09-25

- **PC 冒烟** `smoke-dev-lite.ps1`：health / OTP / day-revisions 幂等 / job poll → succeeded（`ALLOW_MOCK_PREVIEW=true` 无 X02 时 mock 回落）
- 环境：Expo Go Android 57；BFF Dev Lite（本机）
- T0.4 Offline mock：待用户确认
- T2.1 Demo→云：曾失败（本地 Bundle）；已修 Demo JPEG，待复测
- T1.2 OTP：BFF 日志显示手机曾成功 request/verify
