# Bug 跟踪

| ID | 严重度 | 模块 | 现象 | 状态 | 备注 |
|----|--------|------|------|------|------|
| B001 | P0 | Pipeline | Expo Go Android 相册 / Demo 曾 Pipeline failed | 🔄 | 已加 Offline + 真 JPEG Demo；需复测云 |
| B002 | P1 | Expo Go | Reanimated / MediaLibraryNext 曾红屏 | ✅ | 锁 SDK57 依赖 + legacy media |
| B003 | P2 | 网络 | 手机 Ping 依赖防火墙 8790 | 开放 | setup -OpenFirewall |

新增 Bug：复制一行，状态用 开放/🔄/✅。
