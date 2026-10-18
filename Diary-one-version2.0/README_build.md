# Diary One 2.0 · 内测构建入口

更新日期：2026-10-18。

请先读 [当前 README](README.md)，再按 [TestFlight 打包详细步骤](docs/TestFlight打包详细步骤.md) 执行。

- 源码目录：`Diary-one-version2.0/apps/mobile`，不要使用仓库根目录的旧 `apps/mobile`。
- 后端已部署到 `https://bff.diary.luxe`，版本 `v2-20261018T145747Z`；X02 模型为 `qwen3.8-flash`，403 已解决。
- Apple Developer 开启对应 Bundle ID 的 Sign in with Apple；App Store Connect 数字 App ID 填入 `submit.preview.ios.ascAppId`。
- Google 可暂缓；如启用，App 与服务器两端均须配置 Client ID。
- 先运行 `npm ci`、类型检查、lint 和核心测试；再使用公司 EAS 账号构建 preview，提交明确 build ID。
- 首次构建需完成项目关联和签名；本轮尚未完成 IPA/原生真机验收。HQ 派生媒体仍缺实现，真实素材质量及 Figma 真机验收仍待完成。

完整当前状态见 [总交接](docs/TEAM_PACK_HANDOFF.md) 和 [补修记录](docs/生成链路补修_2026-10-18.md)。
