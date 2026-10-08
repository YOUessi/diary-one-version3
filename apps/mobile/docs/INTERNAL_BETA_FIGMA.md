# 内测（TestFlight）· Figma 04 验收标准

**定位：** 这一版走 **内测**，但 **UI/状态机按上架级** 对照 Figma 0916「04 Screens」，不是「能点通就行」的 dev 包。

---

## 1. 用哪条构建线

| Profile | 环境变量 | 用途 |
|---------|----------|------|
| `development` | 默认 | Metro + Dev Client，可出现 Internal Lab |
| **`preview`** | `EXPO_PUBLIC_INTERNAL_BETA=1` · `STORE_RELEASE=0` | **TestFlight 内测主包**：Figma 完整 Sign In（含 Apple/Google 占位）、**无 Lab** |
| `production` | `EXPO_PUBLIC_STORE_RELEASE=1` | App Store 审核向：隐藏未接线 OAuth，仅邮箱 |

```bash
cd diary-one-app
npm run eas:build:ios:preview
# 或
eas build --platform ios --profile preview
```

`showInternalLabTools` 仅在 `__DEV__` 为真时开启；**preview 的 release 包不会带 Lab**（见 `src/config/buildProfile.ts`）。

---

## 2. 内测必过项（对照 `FIGMA_04_COVERAGE.md`）

1. **四 Tab** 与 PRD 纪律：Tag 不可点、Small Memory 无详情、Sync ≠ 云端处理、未连接设备不造假电量。
2. **Onboarding / Sign In（127:1179）**：preview 包为 Apple → Google → or → Email → 底栏 **Continue with Email**（`SignInScreen` + `OnboardingScaffold`）。
3. **Share（R6-S4）**：**Preparing** 顶栏有 **Cancel**；**Preview** 无 Cancel（与 Figma / `FIGMA_04_COVERAGE` 一致）。透明 modal 下章节仍可见。
4. **Diary 日历 / Today 各状态**：含 Calendar Preparing、History load、Empty past day。
5. **Device**：断开态诚实；Automatic Capture 选中态为描边/✓，无画板外的 “Selected” 文案。
6. **Account**：内测包顶区 **Internal beta** 说明（`isInternalBetaBuild`）；About 版本与 `app.json` 一致。

仍标 **⚠️** 的项（Motion 真资源、Share 像素 diff、全稿 token 逐帧）内测也应记录差距，但不阻塞「主流程可验收」。

---

## 3. 与上架清单的关系

内测 UI 按 Figma；**账号/云/硬件** 仍见 `APP_STORE_RELEASE.md` A1–A8。建议在 TestFlight 说明中写清：邮箱 OTP、OAuth、量产云、真 BLE 的边界。

---

## 4. 建议验收流程

1. 安装 **preview** IPA（非 development client）。
2. 按 `page_04.txt` 分组截屏：Diary 状态矩阵 → Memory 搜索/Captured → Share 四条 flow → Device → Account。
3. 与 Figma 并排；⚠️ 项记入 issue，带 frame id。
4. 需要联调云时配置 BFF（见 `BACKEND_INTEGRATION.md`），勿用 Lab 导入冒充用户路径。

---

## 5. 已知内测与 Store 画板差异（刻意）

| 区域 | preview（内测） | production（上架） |
|------|-----------------|------------------|
| Sign In | Figma 含 Apple/Google（stub 弹窗） | 仅邮箱 + 说明文案 |
| Internal Lab | 无 | 无 |
| Account 横幅 | Internal beta 说明 | 无 |
