# Diary One · 开发目标与路线图（商用 iOS）

**目标（当前阶段）：** 在 **Expo Go / 后续 TestFlight** 上，按 Figma 04 + PRD V0.1 跑通 **可验收的商用形态主链**：登录 → 选素材/导入 → 云处理 → Diary 回看 → Memory/搜索/分享 → Device 诚实未连接 → Account。  
**暂缓：** App Store 正式上架手续（Apple 账号审核文案等），但不降低功能与纪律标准。

权威依据：

- Figma 0916「04 Screens」→ `diary-one-app/docs/FIGMA_04_COVERAGE.md`
- PRD → `.figma_fetch/prd_text.txt`（产品定义书 V0.1）
- 算法 → `nexleap-diary-one`（V1.75）+ `codex_*_v1_75_*` 交接包
- 后端 → `diary-one-server`（Dev Lite / 量产 Docker）

---

## 1. 仓库模块（本仓 monorepo）

| 路径 | 职责 | 商用角色 |
|------|------|----------|
| `apps/mobile` | Expo RN App（原 `diary-one-app`） | 消费者 UI + 端侧 Bundle + 本地库 |
| `services/bff` | FastAPI BFF + Dev Lite（原 `diary-one-server`） | OTP、day-revision 任务、鉴权 |
| `services/algorithm` | X02 / V1.75（原 `nexleap-diary-one/algorithm` 或整仓） | 记忆生成 |
| `docs/` | 路线图、测试计划、进度、Bug | 迭代真相源 |

---

## 2. 开发优先级（按风险从高到低）

### P0 — 不打通则无法「找产品问题」（本周）

| ID | 交付 | 风险若不做 |
|----|------|------------|
| D0 | **本机 Dev Lite** 稳定：BFF:8790 + X02:8787（无 Docker） | 手机永远 Pipeline failed |
| D1 | **Expo Go 冷启动**：依赖版本锁死 SDK 57；Lab Apply/Ping | 红屏 / 连不上 |
| D2 | **Offline mock Diary** | 分不清是 UI 坏还是云坏 |
| D3 | **Demo photo → BFF → Diary**（不靠相册） | Android Expo Go 相册常挂 |
| D4 | **OTP API + 弹窗码**（无真邮件） | 登录流测不了 |

### P1 — 主链完整（内测验收）

| ID | 交付 |
|----|------|
| D5 | 相册导入（iOS 优先；Android 注明 Expo Go 限制） |
| D6 | Today 七态 + 日历 + Chapter Detail + Your Story |
| D7 | Memory 搜索 / Captured / Topics（纪律：Tag 不可点、Small 无详情） |
| D8 | Share 四条 flow（Cancel 顶栏） |
| D9 | Device 诚实 Not connected；Lab link 仅开发 |
| D10 | Account 资料 / 偏好 / 隐私页 |

### P2 — 算法与质量（有 Key 后）

| ID | 交付 |
|----|------|
| D11 | `DASHSCOPE_API_KEY` + X02 `qwen` 真 V1.75 |
| D12 | 结果校验 fail-closed；PARTIAL ≠ Empty Day |
| D13 | 费用/耗时/失败恢复记入测试记录 |

### P3 — 量产形态（上架前）

| ID | 交付 |
|----|------|
| D14 | Docker：Postgres + Redis + MinIO + Worker |
| D15 | 真 SMTP OTP；关 `expose_otp` |
| D16 | EAS preview / production；去 Lab |
| D17 | 真 BLE（硬件合同后） |

---

## 3. 明确不做 / 暂缓（开发期排雷）

- 不在消费者路径伪造电量、Sync 成功、云 Ready。
- `PHOTO_LIBRARY_TEST` 不进 Captured by You。
- Sync ≠ Cloud Processing。
- Expo Go ≠ 上架包；不在 Go 里承诺相册全权限（Android）。
- fixture / Mock ≠ 算法质量通过。

---

## 4. 进度板（请随迭代改状态）

| 里程碑 | 状态 | 说明 |
|--------|------|------|
| M0 壳层 + Figma 主屏 | ✅ | 见 FIGMA_04_COVERAGE |
| M1 Dev Lite + OTP API | 🔄 | 本机伪云；真邮件未接 |
| M2 Demo/相册 → Diary | 🔄 | Offline ✅；云管线联调中 |
| M3 真 V1.75 | ⏳ | 待 DashScope Key |
| M4 TestFlight 内测包 | ⏳ | EAS preview |
| M5 上架阻断项关闭 | ⏳ | 见 APP_STORE_RELEASE |

更新规则：改代码必改本表一行 + `docs/TEST_PLAN.md` 对应用例结果。
