> 2026-10-21 干净目录补充：本仓库已展平，唯一构建入口是 `apps/mobile`，文中旧路径 `Diary-one-version2.0/apps/mobile` 在此应替换为 `apps/mobile`。以下保留原日期交接内容；当前代码、测试与限制以 [当前 README](../README.md) 和 [清理记录](CODE_CLEANUP.md) 为准。

# Diary One 交给 iOS 打包同事的最终交接

更新日期：2026-10-18。目标是商用 iOS App；本次交付是用于构建和验收的候选源码，尚未取得商用放行。**后端本轮修改已部署；云端已切换至 Key 允许的 `qwen3.8-flash`，真实供应商调用及合成素材完整生成链路通过，403 阻塞已解除。前端没有全画板真机签字，仍需真实照片/视频与算法质量验收，不能当作只剩打包和提交商店。**

## 从哪里开始

**后续工程补修：** 云端最新发布为 `v2-20261018T145747Z`。B03/B04/B05/B06/B10 已补代码并通过回归，须使用配套最新 App 源码，iPhone 故障注入仍待验收。先读 [生成链路补修](生成链路补修_2026-10-18.md)；高清派生媒体仍未实现，真实照片/视频质量仍待验收。

**登录问卷后续更新：** 本轮已按两份飞书原文件及用户参考图修改问卷，新增互斥/空答/自定义确认、标准词 ID、来源隔离和等待保存。详见 [登录问卷实现与验收](登录偏好问卷_实现与验收_2026-10-18.md)。必须使用本轮新源码重新打包；仍需 iPhone 逐页截图及键盘/返回/重开核验，不能把网页视觉验证写成原生像素验收。

1. 先读 [最终 PRD 与算法核查](最终核查_PRD与算法_2026-10-18.md)：包含全部 53 条需求、算法模块、B01–B12 问题与关闭标准。
2. 再读 [TestFlight 详细步骤](TestFlight打包详细步骤.md)，完成公司账号与 preview 构建。
3. 云端问题按 [部署记录与回滚](云端部署记录_2026-10-18.md) 处理。已有 [重构说明](重构交接与验收_2026-10-18.md) 是实现记录，已知偏差以本次最终核查为准。

## 唯一打包源码

本机：`E:\AI耳机\diary-one\Diary-one-version2.0\apps\mobile`。同事机器：交付快照内 `Diary-one-version2.0/apps/mobile`。不要进入旧的同级 `apps/mobile` 或其它历史项目。

本轮代码按用户授权同步到 GitHub 的 `Diary-one-version2.0`。交接时核对本轮 commit SHA，拉取该提交后再构建，不使用旧缓存或其他目录。交付不包含 node_modules、.env、PEM、真实素材、会话导出或服务器私有备份；依赖由 npm ci 安装。

## 云端已做完的事

| 项 | 当前事实 |
|---|---|
| 原有服务入口 | `https://bff.diary.luxe`，继续使用现有 ECS/HTTPS |
| 本轮 release | `v2-20261018T145747Z`，BFF/Worker 完整结果校验已部署；X02 仍使用已加载算法及 `qwen3.8-flash` |
| 运行状态 | BFF/Worker/Postgres/Redis/MinIO running，X02 与 socat active |
| 配置/数据 | 原 .env、网络地址及数据卷保留，Postgres 容器未重建；已备份 DB、账号文件、源码/配置和旧镜像 |
| 结果真实性 | allow_mock_preview=false，验证码回显关闭；SMTP 仅确认配置存在，本次没有实际发邮件 |
| 新账号删除 | 隔离账号验证通过；跨账号 404、活动任务 409、对象清理及会话撤销正确；测试数据已清理 |
| 真实模型 | `qwen3.8-flash` 同 Key 直接调用 200；合成图片经实际 Worker/X02 完成 3 次调用，succeeded / READY_PRIMARY_COPY / publish_admit=true，无 mock；测试数据已清理 |

不要重建底座、改域名或覆盖服务器配置。保留 X02 的 systemd 模型覆盖配置（见部署记录）；Key 未更换。接下来用授权照片+视频完成真机生成与质量验收。供应商 Key、SMTP、API_TOKEN 只能留服务端。`qwen3.8-flash` 价格尚需按百炼账单校准，现有 trace 估算不能视为实际费用。

## 打包前准备

- Apple Developer / App Store Connect：现行 Bundle ID `com.nexleap.diaryone.dev`，开启 Sign in with Apple，填写真实数字 ascAppId；商用标识是否沿用由公司确定，避免临时随意修改。
- Expo/EAS：确认项目归属公司、签名与构建权限、App Store Connect 对应关系。preview 已是 distribution=store，可提交 TestFlight。
- Google：如在本轮启用，App 配置 Web/iOS Client ID，服务器 .env 另配 GOOGLE_CLIENT_IDS 并按 release overlay 重建 BFF。仅改 App 不会生效。当前服务端缺此配置。
- 公网地址必须是 `https://bff.diary.luxe`，EXPO_PUBLIC_DEV_BFF_TOKEN 为空；不要填写服务器内部 API_TOKEN。
- 保留 EXPO_PUBLIC_INTERNAL_BETA=1、EXPO_PUBLIC_STORE_RELEASE=0、EXPO_PUBLIC_INCLUDE_VISION=1。偏好上传默认关闭，未完成授权合同不要开启。
- 本轮不接 BLE；保留主动图片/视频导入作为已授权测试入口，Device 如实未连接。不要把 PHOTO_LIBRARY_TEST 宣称为 Manual 来源。

## 执行顺序

先构建用于工程和设计验收的候选包；B01 的供应商权限子项已解除，真实照片/视频真机验收仍待完成。B03/B04/B05/B06/B10 已补修并需真机验证，B07–B09 仍待修复。不要拿修复前 build 的结果签字。

```powershell
cd <交付快照>\Diary-one-version2.0\apps\mobile
npm ci
npm run typecheck
npm run lint -- --no-cache
npm run test:core
npx eas-cli@latest login
npx eas-cli@latest whoami
npx eas-cli@latest build --profile preview --platform ios
```

确认需要提交的具体 build ID，使用该 ID 提交，避免 latest 选错旧包：

```powershell
npx eas-cli@latest submit --profile preview --platform ios --id <本轮成功的EAS构建ID>
```

不要用 Expo Go 验收本地 Vision。必须以实际 EAS iOS 原生构建及真 iPhone 调用记录为准。此处没有替公司创建项目、签证书或提交 App Store/TestFlight。

## 验收与交回证据

1. 按最终核查关闭 B01–B12 对应本轮范围；至少对 P0 准入/数据/来源问题复测。
2. Apple/OTP/可用的 Google 真机登录；主动导入照片+视频→真实云任务→结果→重开仍可读；无内容与模型失败分开。
3. 按 PRD T01–T12 留记录，硬件范围明确排除；媒体中断、跨日/未知时间、同日多批、小记忆历史、补记冲突、分享不带私人文字、换账号晚回调重点测试。
4. 依据 [Figma 全页面清单](审查依据_Figma全页面清单_2026-10-18.md) 验证相关节点所有状态，记录机型、iOS、安全区、大字及 VoiceOver；不能只截四个首页。
5. 返回源码 commit 或交付摘要、EAS build ID、App 版本/构建号、云 release、测试结果、未关闭项、截图与回滚点。无逐画板真机记录时不要写“完全对照 Figma”。

本次复查：类型/lint 通过、前端 30 passed、后端 54 passed、算法 311 passed / 25 skipped / 104 subtests passed。真实模型、原生和视觉验收分别留证，不由这些数字替代。
