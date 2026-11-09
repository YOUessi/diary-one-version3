# Sydney Citywalk 六组：离线分发包与在线托管说明

日期：2026-11-09。完整共享 ZIP 已复制到用户 Mac 的 Downloads：

`~/Downloads/Nexleap_One_Sydney_6Groups_Offline_Live_20261109.zip`

## 包含的内容

- Nexleap One 的 Day 时间线、Chapter 详情、完整故事、关键瞬间、Live 自动播放网页版。
- 六个相位组（10/20/30/50/60/70 秒），三种模型方案（JPEG VLM V03、视频 0.5fps、视频 1fps）。
- **129 个 Chapter、701 张真实入选 JPG、694 个按源视频与 PTS 精确恢复的 3 秒 Live MP4**。
- HTML、CSS、JS、JPG、MP4 都在压缩包内，不需要联系原始 Mac、不需要本地 8810 服务，也不需要联网或者大模型 API。
- 收藏和 My story 仅保存在观看者自己的浏览器本地，不同步其他人。

源原始 3 秒 MP4 总大小约 597 MB，分享文件转码为 640×360、24fps、约 525 kbps。694 个 MP4 压缩至约 127.28 MB。最终 ZIP **172,452,193 bytes（约 164.46 MiB）**，SHA-256：

`b227a67a80fb193b6d4edfa04cb07e54c4cb79d06e9b6391dfdd54c9042a4cf0`

## 使用方法

1. 将完整 ZIP 通过获准的文件分享方式发送给评审人员。
2. 对方在 Windows/Mac 上解压，保留 Nexleap_One_Sydney 目录结构。
3. 使用 Chrome / Edge 打开解压后的 `Nexleap_One_Sydney/index.html`。
4. 在 Day 时间线和 Chapter 详情页浏览真实图片，视频进入视野会自动静音播放 3 秒并循环，离开视野暂停。
5. 如果本地浏览器限制 file:// 的视频播放，可以从解压目录运行 `python3 -m http.server 8080`，访问 `http://127.0.0.1:8080/`。

ZIP 不包含完整 5 小时源影片、原始 10 秒切片、模型 API Key、密钥及其他私有开发配置。视频是 H264 MP4 动态预览，而不是 Apple Photos 原生 Live Photo。

## 完整性验证

- 打包成功并完成 ZIP CRC 全项验收：共 **1402 个文件，701 JPG + 694 MP4**。
- ZIP 解压到独立 QA_EXTRACTED 文件夹，Chrome 打开 file:// 下的 index.html，在浏览器拦截一切 HTTP(S) 请求的前提下，**Day 时间线和 Chapter Live 仍正常自动播放**。
- 验证日志 `test_fresh_unzip_offline.log` 中包含 `OFFLINE_PORTABLE_E2E_PASS_NO_NETWORK_REQUIRED`。
- 复制到 Downloads 后重新核对 SHA-256，验证完全一致。
- 本轮没有重新调用 VLM，不产生新增模型推理费用。

完整 Mac 研究目录：

`~/Documents/Nexleap/work_logs/evidence/Nexleap_One_Sydney_Portable_Share_20261109/`

## 复现

需要用户原始影片和本地真实结果。先运行：

```bash
cd ~/Documents/Nexleap/Diary_one_chapter_v2
~/miniforge3/bin/python3.13 scripts/sydney_six_offset_portable_export.py prepare
~/miniforge3/bin/python3.13 scripts/sydney_six_offset_portable_export.py render --workers 4
~/miniforge3/bin/python3.13 scripts/sydney_six_offset_portable_compress.py optimize --workers 4
~/miniforge3/bin/python3.13 scripts/sydney_six_offset_portable_compress.py finalize
```

这些操作不修改原始视频、模型 JSON 或 API usage。重新导出仍需要执行最终质量、文件大小和版权检查。

## 需要公开网页链接时

静态网站可以部署至 GitHub Pages / Railway / Cloudflare Pages。所有相对路径都是静态的，无需 Python API 或原 Mac。

**但悉尼实验视频来自第三方 Prowalk Tours。** 其版权条款没有自动授予重新剪辑、分发或公开展示的权利。公开部署整个展示站点前，需要取得权利人许可，或确认适用的法定例外。授权联系：

- https://www.prowalktours.com/terms-of-use
- https://www.prowalktours.com/licensing

目前没有未经授权把真实视频截图和剪辑上传公共服务器，也没有虚构任何可公开访问的链接。离线包可交给有权参与此评审的团队成员。
