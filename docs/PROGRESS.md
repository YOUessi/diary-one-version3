# 进度看板

更新：2026-09-25

| 里程碑 | 状态 | 备注 |
|--------|------|------|
| M0 Figma 主屏 / 四 Tab | ✅ | FIGMA_04_COVERAGE |
| M1 Dev Lite + OTP API | 🔄 | 真邮件未接；弹窗码 |
| M2 Offline Diary | ✅ | Lab 按钮 0 |
| M2 Demo/相册 → 云 → Diary | 🔄 | 用户尚未稳定接本机伪云 |
| M3 真 V1.75 | ⏳ | 待 DASHSCOPE_API_KEY |
| M4 EAS TestFlight | ⏳ | |
| M5 上架阻断项 | ⏳ | APP_STORE_RELEASE |

## 本周焦点

1. 固定 Dev Lite 开机流程，让手机 Ping 稳定为绿  
2. Demo photo 云管线跑通并记入 TEST_LOG  
3. 本仓 GitHub 作为唯一迭代源（代码 + 测试 + Bug）

## GitHub 仓

- 本地 monorepo 已就绪：`E:\AI耳机\diary-one`（初始 commit 已有）
- 目标远程：`https://github.com/Nexleap-Tech/Diary_one`（private）
- 阻塞：本机访问 GitHub 超时 / API 403；需网络可达且组织有建仓权限后执行：

```powershell
gh auth login -h github.com -p https -w -s "repo,read:org,workflow"
cd E:\AI耳机\diary-one
.\scripts\push-to-github.ps1
```
