# Diary One（Nexleap）

商用形态 **iOS App** 开发仓：移动端 + BFF + 算法 + 测试/进度/Bug 迭代。

## 目录

```text
apps/mobile/                 Expo React Native（Figma 04 + PRD）
services/bff/                FastAPI BFF + Dev Lite（无 Docker 联调）
services/algorithm/          nexleap-diary-one（含 algorithm V1.75 / X02）
services/algorithm-handoff-v1_75/   V1.75 工程移交说明文档
docs/
  DEVELOPMENT_ROADMAP.md     目标与开发优先级
  TEST_PLAN.md               商用功能测试点
  PROGRESS.md                进度看板
  BUGS.md                    Bug 跟踪
  TEST_LOG.md                测试记录
```

## 快速联调（Expo Go，无需 Docker）

```powershell
cd services/bff
.\scripts\start-dev-lite.ps1 -Adapter fixture

cd ..\..\apps\mobile
copy .env.example .env   # 改成你的局域网 IP
npx expo start --go --lan --clear
```

手机 Lab：Offline mock → Ping → Demo photo。详见 `docs/TEST_PLAN.md`。

真算法：设置 `DASHSCOPE_API_KEY` 后 `-Adapter qwen`。

## 产品纪律

- Sync ≠ Cloud Processing  
- 未连接不造假电量  
- Tag 不可点；Small Memory 无详情  
- 相册测试源不进 Captured by You  

## 许可与机密

私有仓。勿提交 `.env`、API Key、真实用户素材。
