# Expo Go 内测操作卡（入口）

**完整手册（阶段 A→D、公网几十人、TestFlight、配额）：**  
→ [`INTERNAL_BETA_FULL_GUIDE.md`](./INTERNAL_BETA_FULL_GUIDE.md)

**真机逐按钮 / 问卷 / 像素：**  
→ [`EXPO_GO_FULL_TEST_GUIDE.md`](./EXPO_GO_FULL_TEST_GUIDE.md)

---

## 电脑（本机联调，阶段 A）

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\setup-commercial-dev.ps1
# 二选一：
.\scripts\up-docker-stack.ps1          # 量产栈
.\scripts\start-x02.ps1
# 或：
.\scripts\start-dev-lite-background.ps1  # 快起 + mock（不算质量）
```

真 qwen / 关 mock / 公网 / 配额：见总册 **阶段 B–C**，不要只用 background mock。

手机：Lab **Apply → Ping**（看 `x02` / `ffmpeg` / `mc` / `mock`）→ A / A2 / B。

结果记入 `docs/TEST_LOG.md`。
