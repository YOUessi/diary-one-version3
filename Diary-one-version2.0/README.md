# Diary One 2.0（Nexleap）

本目录是当前 iOS 内测候选源码，包含 App、BFF/Worker、算法及交接文档。更新日期：2026-10-18。按本轮授权发布当前版本；仍保留已知功能缺口和未完成验收的说明。

## 当前版本状态

| 部分 | 当前事实 |
|---|---|
| App | 最新源码在 `apps/mobile`；登录偏好问卷已按两份飞书文件和参考图修改；结果输入绑定、事务发布、日期/来源、小记忆保留及资料保存已补修 |
| 线上后端 | `https://bff.diary.luxe`，BFF/Worker 发布 `v2-20261018T145747Z`，继续使用现有阿里云 ECS、域名及数据卷 |
| 云端算法 | X02 使用 `qwen3.8-flash`；同一个 Key 的旧模型 403 已通过正确模型配置解决，mock 关闭 |
| 真实调用验证 | 合成图片经过实际 Worker/X02 完成 3 次模型调用，`succeeded` / `READY_PRIMARY_COPY` / `publish_admit=true` / `input_bound=true`，测试数据已清理 |
| 本轮检查 | App 30 项、后端本地及服务器候选镜像 54 项通过；TypeScript、ESLint 和 iOS Hermes 导出通过 |
| 分发状态 | 尚未制作本轮 IPA/TestFlight 包；Hermes 导出不代表 Swift/Vision 原生构建成功或真机验收完成 |

高清派生媒体（S13）仍未实现；真实照片/视频质量、Figma 全页面真机一致性尚未完成验收。其他剩余项见最终核查。此版本可以交给同事构建团队内测包，不代表商用或 App Store 发布放行。

## 同事从这里开始

1. 阅读 [TestFlight 打包详细步骤](docs/TestFlight打包详细步骤.md)。
2. 阅读 [总交接](docs/TEAM_PACK_HANDOFF.md) 和 [生成链路补修](docs/生成链路补修_2026-10-18.md)，了解当前配套版本及回归范围。
3. 阅读 [最终 PRD 与算法核查](docs/最终核查_PRD与算法_2026-10-18.md)，按剩余项记录内测结果。

同事获取代码后，记录本次交接的 commit SHA，并进入 **`Diary-one-version2.0/apps/mobile`**。仓库根目录同级 `apps/mobile` 是另一份历史代码，不要在那里打本轮包。前端必须使用本轮源码重新构建；App 新结果校验依赖已部署的新后端合同标记。

## 构建 TestFlight 内测包

准备公司 Apple Developer / App Store Connect 和 Expo/EAS 权限。Bundle ID 为 `com.nexleap.diaryone.dev`，开启 Sign in with Apple。App Store Connect 建立匹配应用，将该应用的**数字 Apple ID**填入 `apps/mobile/eas.json` 的 `submit.preview.ios.ascAppId`，不是个人 Apple 账号。

使用 Node.js 24.16.x（本轮实测版本），在 `apps/mobile` 运行：

```powershell
npm ci
npm run typecheck
npm run lint -- --no-cache
npm run test:core
npx eas-cli@latest login
npx eas-cli@latest whoami
npx eas-cli@latest build --profile preview --platform ios
```

首次构建按 EAS 提示关联公司项目并完成 iOS 签名。`preview` 已配置 `distribution=store`、真机、Vision 和公网 BFF。保留 `EXPO_PUBLIC_INTERNAL_BETA=1`、`EXPO_PUBLIC_STORE_RELEASE=0`，不要向 App 写入服务器凭证。对本轮成功的明确 build ID 执行：

```powershell
npx eas-cli@latest submit --profile preview --platform ios --id <本轮成功的EAS构建ID>
```

待 Apple 处理完成，在 TestFlight 添加测试员；外部测试可能需要 Beta 审核。Apple/邮箱 OTP 均需真机实测，SMTP 当前仅确认配置存在。Google 可暂不启用；如启用，需同时配置 App 的 Web/iOS Client ID 和服务器 `GOOGLE_CLIENT_IDS`，只改 App 不够。

## 目录和配置

```text
apps/mobile/          Expo React Native iOS App、原生 Vision 模块及前端测试
services/bff/         FastAPI BFF、Worker、完整结果校验及后端测试
services/algorithm/   X02 算法、冻结合同及算法测试
docs/                产品依据、部署证据、打包与验收文档
scripts/             本目录工程辅助脚本
```

现有云服务器已部署，本轮打包不需要重新搭建后端。运维和回滚见 [云端部署记录](docs/云端部署记录_2026-10-18.md)。迁移或重启 X02 时须保留模型配置 `DIARY_ONE_X01_QWEN_MODEL=qwen3.8-flash`；该配置不包含密钥，云端当前通过 systemd drop-in 生效。新模型费用需按百炼实际账单校准。

## 内测边界

- 本轮暂不接耳机 BLE；设备状态如实显示未连接，通过用户主动选择照片/视频测试。
- 原片留本地，只上传证据帧和 manifest；私人补记不作为云生成输入。偏好上传默认关闭，问卷保存不等于偏好已上传生效。
- Captured by You 仅展示可信设备 Manual 来源；相册导入有独立来源，不冒充耳机拍摄。
- 高清原片精选短片/HQ 导出仍缺实现，不能将原片播放、证据帧或幻灯片称为已完成的算法成品。
- 实际照片/视频、无内容、模型失败、重启恢复、账号切换、资料保存、媒体中断和 Figma 真机页面均需记录测试结果。
- `.env`、API Key、SMTP 授权码、证书、真实用户素材、运行数据和服务器私有备份不随源码交付。`.env.example` 仅供配置结构参考。

## 交接文档

| 文档 | 用途 |
|---|---|
| [TestFlight 打包步骤](docs/TestFlight打包详细步骤.md) | 公司账号、签名、构建、提交与测试员配置 |
| [总交接](docs/TEAM_PACK_HANDOFF.md) | 本轮源码、云端版本、配套配置及验收证据 |
| [生成链路补修](docs/生成链路补修_2026-10-18.md) | 结果校验、原子发布、日期来源、小记忆及资料保存 |
| [登录问卷实现与验收](docs/登录偏好问卷_实现与验收_2026-10-18.md) | 两份飞书文件的逻辑、界面及问卷回归 |
| [最终 PRD 与算法核查](docs/最终核查_PRD与算法_2026-10-18.md) | 53 条需求、已补修项及剩余问题 |
| [Figma 页面清单](docs/审查依据_Figma全页面清单_2026-10-18.md) | 全页面和状态验收范围 |
| [部署与回滚记录](docs/云端部署记录_2026-10-18.md) | 最新云端发布、模型修正、真实调用和回滚点 |

私有项目（Nexleap-Tech）。第三方模型和权重按其各自许可使用；MobileCLIP 权重不得因本次源码交付而直接视为已获商用许可。
