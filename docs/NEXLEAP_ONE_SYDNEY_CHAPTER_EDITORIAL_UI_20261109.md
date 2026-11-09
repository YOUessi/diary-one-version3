# Nexleap One · Sydney Citywalk Chapter 展示页重设计

日期：2026-11-09。环境：用户 MacBook Air 的 Diary_one_chapter_v2；开发分支 `feature/2026-11-05-direct-vlm-chapter`。参考用户提供的 Nexleap One iPhone 截图，完成既有六组 Chapter 评测页面的**真实交互式前端重设计**，而非单纯生成视觉稿。

## 打开页面

**在 Mac 上直接访问**：

http://127.0.0.1:8810/

也可在 Finder 双击历史工作目录里的 `Open_Chapter_Live.command`，它会检测并启动本地 Live 服务，再打开浏览器。

原始预览 HTML 路径保持不变：

`~/Documents/Nexleap/work_logs/evidence/sydney-six-offset-image-vs-video-20261109/SIX_GROUPS_JPEG_VS_VIDEO_REAL_CHAPTER_COMPARISON.html`

另提供新命名入口 `NEXLEAP_ONE_SIX_GROUPS_INTERACTIVE.html`。新的 CSS 和 JS 为同目录 `nexleap.css` 与 `nexleap.js`。源代码在本仓库 `scripts/sydney_six_offset_nexleap_ui.py` 与 `scripts/review_ui/`。

## 样式与交互

根据参考图保留**暖白背景、杂志式字体与排版、圆角大照片、首图淡入纸白背景、Nexleap One 标记、Live 标签、日期/地点层次与轻量按钮**，但不复制截图中的其他地点、假照片、假时间和其他用户个人内容。

### Day 时间线

桌面宽屏显示**左侧一整天的 Chapter 时间线**，右侧为选中章节。时间线包含封面、标题、故事两行摘要、来源视频相对时间和章节编号。手机窄屏首先显示单栏 Day 卡片，点击进入 Chapter 全屏详情。

顶部支持六组采样偏移（10、20、30、50、60、70 秒）以及三种算法（MobileCLIP＋JPEG V03、直接视频 0.5fps、直接视频 1fps）切换。

**所有时间均明确标记为原片相对时间，而非实际拍摄钟点。** 目前源数据没有可靠的真实拍摄日期，因此展示 `研究实验 · 2026.11.09` 作为实验日期，不能冒充旅行当天时间。

### Chapter 详情

选中章节顶部是大幅真实封面图，左右分别有返回时间线与收藏按钮，封面可点击 `LIVE · 3s`。正文显示模型**原始的完整标题、完整 story**，以及 Citywalk/影像算法/偏移标签。

`My story` 支持添加、编辑用户自己的说明，收藏与 My story 均保存在**浏览器本地 localStorage**，不上传云端、不写入 VLM 数据。关键瞬间区域展示全部模型原始描述及证据来源。图片区域使用与参考图相似的**手机单列大圆角照片**，每张配 Live 标签、原片时间、说明文字；点击照片播放 3 秒实际视频，右上角按钮复制本地图片链接。末尾可切换下一章。

历史 10s/70s 的 JPEG V03 某些标题和 story 为英文，页面保留**模型原文**以便公平评估，不在展示层伪装模型已改为中文。

## 真实数据与视觉素材

- 六组 × 三路线：**129 个 Chapter** 全部保留；
- 共 **701 张真实入选图片或源视频解码代表帧**，全部保留；
- JPEG V03 共 236 张；视频 0.5fps 共 192 张；视频 1fps 共 273 张可映射图片；
- 20s／1fps 原始模型生成五章 79 条选点，四个 200000ms 分块边界未直接映射，仍在 Moments 文字区域保留并标记；其余 75 个原片选帧真实展示；
- 旧 V03 JPEG 数据为 768×1024 的 `ASPECT_FIT_LETTERBOX`，上下带很宽的黑色空白。本次新增 `nexleap_editorial_media/` 做**仅移除人工黑边的展示裁切**；保留原始 `full_chapter_media/`、bundle、JPG 的全部原字节，不对模型原始证据或时间戳做任何更改。
- 不生成图像，不引入假的场景，不依赖第三方图片 CDN 或在线字体。

## Live 动态回忆

使用已有的、仅绑定 `127.0.0.1` 的预览服务器 `scripts/sydney_six_offset_live_server.py`。点击 Live 时，以 `source_asset_id + focus_pts_ms` 定位真正的本地 10 秒 MP4，首次按当前选择的时间中心在 Mac 本地 FFmpeg 渲染 3 秒 H.264 MP4，缓存于 `live_preview_cache/`。之后直接循环播放，用户可暂停和关闭；浏览器不会加载 701 个视频播放器。

**这是一种网页内 Motion / Live 效果，不是 Apple Photos 原生 Live Photo 配对文件**。未在 iPhone 上安装/编译新 App，也没有替换线上 Chapter 生成服务。

## Mac 复现与验收

```bash
cd ~/Documents/Nexleap/Diary_one_chapter_v2
~/miniforge3/bin/python3.13 scripts/sydney_six_offset_nexleap_ui.py
~/miniforge3/bin/python3.13 scripts/sydney_six_offset_live_server.py --port 8810
open http://127.0.0.1:8810/
```

以上仅本地网页生成和 Live 预览，不重新调用 VLM。

Chrome 的桌面、iPhone 390×844 模拟测试已执行，验收项目：

1. 六组、三算法与全部 129 个 Chapter／701 媒体完整加载；
2. 20s／1fps 的五章、79 个原始 Moment 描述、75 个可映射照片保留；
3. 手机默认进入 Day 时间线，点击 Chapter 进入详情，返回时状态正确；
4. 收藏按钮、My story 编辑与本机刷新后的持久化；
5. 手机和桌面无横向溢出，照片、标题和正文展示正常；
6. 点击真实图片可打开原片 3 秒 Live，`video.duration≈3s`、播放状态正确；
7. UI 的源模型 JSON、输入图片、原始视频、API Tokens 和历史费用记录未发生改动，**新增 VLM API 调用为 0，模型费用 ¥0**。

测试日志与截图保存在 Mac 实验目录：
`test_nexleap_editorial_ui.log`、`NEXLEAP_ONE_DESKTOP_DAY.png`、`NEXLEAP_ONE_MOBILE_DAY.png`、`NEXLEAP_ONE_MOBILE_CHAPTER.png`、`NEXLEAP_ONE_MOBILE_PHOTOS.png`、`NEXLEAP_ONE_MOBILE_LIVE.png`。

旧版完整详情 HTML 备份在 `SIX_GROUPS_PRE_NEXLEAP_EDITORIAL_BACKUP.html`。页面需要本地服务才能使用 Live，直接 `file://` 打开仅可以阅读图片和故事；Finder 启动命令仍有效。

## 后续真正产品迁移

当前是在真实研究数据上的独立可交互网页，复用 app/mobile 既有 Motion 语义（3 秒原片动态），但**并未直接修改手机端 React Native 生产页面设计**。下一步如需把同样 UI 落到 iPhone，可将本次的颜色、边距、卡片、时间线与详情布局映射到 `apps/mobile/src/screens/diary/` 和 `src/components/`，再做 iPhone 真机尺寸、Live 视频性能与可访问性验收。
