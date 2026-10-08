# App Store 上架级清单（Diary One · iOS）

**当前结论：** Figma 04 **用户屏功能与状态**已齐；**上架级**还需完成本清单中「阻断项」，并完成 **EAS production** 构建验证。

构建开关：`EXPO_PUBLIC_STORE_RELEASE=1`（见 `eas.json` → `production`）  
实现：`src/config/buildProfile.ts` · `app.config.js`（显示名 / Bundle ID）

---

## A. 阻断项（未完成不能当正式上架）

| # | 项 | 状态 | 说明 |
|---|-----|------|------|
| A1 | **Apple 开发者账号 + Bundle ID** | 你方 | production 使用 `com.nexleap.diaryone` |
| A2 | **Sign in with Apple** | 待做 | 若上架版展示 Google/第三方登录，必须同时接 Apple；当前 Store 版 **仅邮箱**（见 SignIn） |
| A3 | **真实账号服务** | 🔄 联调中 | Dev Lite 已接 OTP API；内测弹窗 `dev_code`。上架需真实 SMTP + 关 expose |
| A4 | **隐私政策 / 条款 URL** | 待填 | Account 内链到可访问 HTTPS 页面 |
| A5 | **App Privacy（营养标签）** | 待填 | App Store Connect 与 PRD 数据流一致 |
| A6 | **蓝牙 / 本地网络** | 待硬件 | 真配对需用途字符串与实测；当前诚实 Not connected |
| A7 | **云记忆生产链路** | 🔄 联调中 | Dev Lite（无 Docker）已对齐 `/v1/day-revisions`；真 V1.75 需 `DASHSCOPE_API_KEY`；量产 Docker 另轨 |
| A8 | **截图与审核文案** | 待做 | 不得使用假电量/假同步；与 Figma 269 断开态一致 |

---

## B. 工程已做（Store production 构建）

| 项 | 说明 |
|----|------|
| 隐藏研发入口 | Internal Lab、Evidence 导入、Today 状态切换、Device Services 卡、Settings 内 Lab 开关 |
| 权限文案 | 相册/导出改为用户向说明（非 evidence test） |
| `app.config.js` | Store 构建显示名 **Diary One**，Bundle `com.nexleap.diaryone` |
| EAS `production` | `EXPO_PUBLIC_STORE_RELEASE=1` |

---

## C. Figma 上架级 UI（仍 ⚠️ 非像素终验）

| 区域 | 差距 |
|------|------|
| Sign In（Store） | 无 Apple/Google 按钮（审核策略）；与画板 127:1179 略有不同 |
| Motion / Short clip | 播放态 UI 有，非真实 motion 资源 |
| Share / Device / Auth / Account 子页 | 已按本地 Figma 节点收紧字号/圆角/CTA（见 `FIGMA_04_COVERAGE` 像素结论） |
| 全局 Design Token | Token 已锁 `#FAF9F6`/`#C98245`；全稿逐帧截图 diff 仍待 |

验收方式：对 `FIGMA_04_COVERAGE.md` 中 ⚠️ 项做 **Store 构建** 截图对比。

---

## D. 构建命令

```bash
cd apps/mobile
npx eas-cli login
npx eas-cli init
npx eas-cli build --platform ios --profile preview
npx eas-cli submit --platform ios --profile preview
```

Windows 上同样可在 `E:\AI耳机\diary-one\apps\mobile` 跑上述命令。preview 包 **包含 Apple Vision**。

**内测（Figma 完整 UI，无 Lab）：** `eas build --profile preview`（`EXPO_PUBLIC_INTERNAL_BETA=1`）— 见 `INTERNAL_BETA_FIGMA.md`

---

## E. 建议发布路径

1. **TestFlight（preview）** — 内测验收：对照 Figma 04，Sign In 含社交按钮占位，**无 Lab**  
2. **TestFlight（production 配置）** — 审核预演：仅邮箱登录，无 Lab  
3. **App Store** — A 表全部关闭 + 真账号 + 真设备或明确产品边界  

---

## F. 与后端关系

上架用户路径 **不依赖** `__DEV__` 研发导入。记忆生成需 **diary-one-server** 量产环境 + 合规，见 `diary-one-server/docs/DEPLOY.md`。
