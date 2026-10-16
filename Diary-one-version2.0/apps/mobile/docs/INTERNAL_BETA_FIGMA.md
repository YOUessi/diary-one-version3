# 内测（TestFlight）· Figma 04 验收标准

**定位：** 走 **EAS `preview` → TestFlight**；UI/状态机按 Figma 0916「04 Screens」对照。  
**本轮成功定义（PRD V0.1）：** 内部相册选图 → 手机 Evidence → 云端算法 → Diary 回写；硬件未接入时 **诚实未连接**。

这不等于「全量 PRD + 真 BLE + 正式上架」。

---

## 1. 用哪条构建线

| Profile | 环境变量 | 用途 |
|---------|----------|------|
| `development` | 默认 | Metro + Dev Client，可出现 Internal Lab |
| **`preview`** | `EXPO_PUBLIC_INTERNAL_BETA=1` · `STORE_RELEASE=0` · Vision | **TestFlight 内测主包**：**仅邮箱 OTP**、无 Lab、无假 BLE |
| `production` | `EXPO_PUBLIC_STORE_RELEASE=1` | App Store 审核向 |

```bash
cd apps/mobile
npx eas-cli build --profile preview --platform ios
```

`showInternalLabTools` 在正式消费者构建中**永久关闭**；**preview release 包不带 Lab**（见 `src/config/buildProfile.ts`）。

---

## 2. 内测边界（写进 TestFlight 说明）

| 能力 | 内测包行为 |
|------|------------|
| 登录 | **Apple / Google / 邮箱 OTP**（Figma 127:1179；云端 `/v1/auth/oauth` + SMTP OTP） |
| 真 BLE | **无** — Pairing Searching 会提示未找到设备；请用 **Continue without a device** |
| Device | 默认 **Disconnected**；不造假电量 % |
| 主路径 | **Device → Upload photos & videos**（或 Diary 空态同按钮）→ 相册选图/视频 → Evidence → 云 → Diary |
| 云模型 | App **不持**模型 Key；BFF 后 X02 用**一把** `DASHSCOPE_API_KEY` 直接调通义 |
| 隐私/条款 | 未配置 `EXPO_PUBLIC_PRIVACY_POLICY_URL` / `EXPO_PUBLIC_TERMS_URL` 时显示友好占位，**不死链** |

---

## 3. 验收最短路径（必过）

1. 安装 **preview** IPA（非 development client）。
2. **登录**：Continue with Apple，或邮箱 OTP（需公网 BFF；OTP 需 SMTP）。
3. **Account → Privacy & Data** → 同意云 Evidence 上传。
4. **Device → Choose from Photos**（或 Diary 空态 **Upload photos & videos**）→ 选图片/视频。
5. **Diary**：Preparing → Ready / Chapter。
6. **Memory** 本地搜索；**Share** 拼贴预览。
7. **Device** 保持 **Disconnected**（勿期望真耳机同步）。

对照全表：[`FIGMA_04_COVERAGE.md`](./FIGMA_04_COVERAGE.md)。

像素：消费者主屏已按节点度量收紧（见 `FIGMA_04_COVERAGE.md`）。  
有意识偏差保留：无假电量、「Continue without a device」、CLOUD EVIDENCE、相册导入入口（非画板）。  
真机侧需再做一次截图对照；真 BLE / 高清 Motion 资源延后。

---

## 4. 与上架 / 运维清单

- 账号 / 云 / 硬件门禁：[`APP_STORE_RELEASE.md`](./APP_STORE_RELEASE.md) A1–A8（后置）。
- 公网 BFF / SMTP / DashScope / EAS：[`INTERNAL_BETA_OPS_CHECKLIST.md`](../../../docs/INTERNAL_BETA_OPS_CHECKLIST.md)  
  与逐步操作单：[`INTERNAL_BETA_USER_RUNBOOK.md`](../../../docs/INTERNAL_BETA_USER_RUNBOOK.md)。

---

## 5. preview vs production（刻意差异）

| 区域 | preview（内测） | production（上架） |
|------|-----------------|------------------|
| Sign In | 仅邮箱 OTP | 仅邮箱 + 审核说明 |
| OAuth | 无（非 Lab） | 无（未接线前） |
| Account 横幅 | Internal beta | 无 |
| BLE | stub / Searching 诚实失败 | 同左直至硬件接入 |
