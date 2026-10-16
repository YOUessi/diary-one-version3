# 正式用户 App 验收口径（Expo Go = 打包后）

产品要求：**Expo Go 与打包安装包都必须是正式终端用户 App**，不是实验室演示。

## 默认行为（无 `EXPO_PUBLIC_ENABLE_LAB=1`）

| 必须 | 禁止 |
|------|------|
| Email OTP（真 BFF + 建议 SMTP） | Skip to Diary / 任意 6 位本地登录 |
| Privacy / 问卷显式云同意 | 静默 `cloudEvidenceConsent=true` |
| Production BFF，`mock=false`，真 qwen | fixture / mock 写日记 |
| Device 诚实 Not connected | 假电量 / lab_linked 冒充已连接 |
| Device → Import photos（有 OTP+同意） | Evidence pipeline lab / Demo / Offline mock / Research 入口 |

工程师本地恢复 Lab：

```text
# apps/mobile/.env
EXPO_PUBLIC_ENABLE_LAB=1
# 可选：EXPO_PUBLIC_ALLOW_MOCK_DIARY=1
```

然后重启 Metro。Lab **不得**用于对外宣称「正式可用」。

## PC 质量栈

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\start-quality-loop.ps1
```

- 无 DashScope Key：**拒绝启动**（不再静默 fixture）  
- `allow_mock_preview=false` · `provider≠fixture`

## 手机最短正式路径

1. Expo Go 连 Metro（`.env` 已指向 LAN BFF，**无** shared token）  
2. **Continue with Email → OTP**（查邮箱；正式路径不弹明文码）  
3. **Privacy → Allow cloud evidence**  
4. **Device → Import photos → cloud → Diary**  
5. 认出 Chapter；失败不写假日记  

## 抽检

内容分层见 `ALGORITHM_CONTENT_REVIEW.md`。  
全功能点检见 `PHONE_FULL_TEST.md`（其中 Lab/Skip 步骤仅在 ENABLE_LAB 时存在）。

## 门控代码

- `apps/mobile/src/config/buildProfile.ts` → `isFormalConsumerApp` / `isLabToolsEnabled`  
- Lab 入口随 `showInternalLabTools`（= ENABLE_LAB）  
