# Nexleap One｜东京 Citywalk 与 Manning Park 标注范例展示

日期：2026-11-09。开发位置：用户 Mac 的 Diary_one_chapter_v2 工作区。

## 真实部署 URL

- 汇总入口：https://youessi.github.io/diary-one-version3/examples/
- 东京 Citywalk：https://youessi.github.io/diary-one-version3/tokyo/
- Manning Park：https://youessi.github.io/diary-one-version3/manning-park/
- 悉尼已有站点：https://youessi.github.io/diary-one-version3/

**部署位置**：GitHub YOUessi/diary-one-version3 的 gh-pages 分支，仅添加 examples/、tokyo/、manning-park/，不改动已有悉尼根目录，也不改变主开发代码。来源仓库 13021068599zyf-glitch/nexleap-chapter-examples 的连接只有 Pull 权限，无 Push 权限，因此原仓库完全只读，未向该仓库提交任何文件。

## 原始数据：不是新的 VLM 推理

直接从来源 GitHub 主分支、固定源码提交 b61d684ab8765c93b5c75ccaabd91bfbcfe8470d 读取四套已经整理的 Chapter 范例：

| 来源 | Chapter | 最终选择 | 所有图片 |
|---|---:|---:|---:|
| 东京 Citywalk 0s | 6 | 47 | 165 |
| Manning Park 0s | 1 | 16 | 162 |
| Manning Park 10s | 1 | 17 | 157 |
| Manning Park 20s | 1 | 16 | 159 |
| 总计 | 9 | 96 | 643 |

每个 Chapter 的原有标题、正文、封面 JPG、人工分类状态、选图顺序、照片备注、场景归类和视频相对时间都来自整理结果.json 和已提交到原仓库的实际图片。643/643 张照片均完成准确映射。终选照片默认显示，候选/未选/排除可独立展开查看；没有额外发明故事，也没有强行将 Manning Park 的一章拆成多个 Chapter。

原始导出照片含大块黑色 aspect-fit letterbox 上下留白。本次仅对供静态网页显示的独立预览图片作裁切，原始 GitHub 图片、来源仓库数据不修改。输出图片总计约 67 MB。

## UI 和使用方式

延续悉尼 Nexleap One 的暖白色编辑型界面：Day 时间线、Chapter 大封面、完整故事、原视频相对时间、标签、My story、本机收藏、逐张照片大图。Manning Park 支持选择 0s、10s、20s 偏移组。东京数据只有 0s 组，展示完整六章。

进入 Chapter 后，首先展示真正「终选」的代表照片；继续展开可查看原始人工标注中的候选、未选、排除及其各自备注。点击照片可以放大。My story 与收藏只保存在观看者的浏览器本地。

## 关于 Live 的准确说明

这个来源仓库只包含人工编辑后的 JSON、真实 JPG 和相关图片说明；没有对应的原始10秒 MP4 文件。用户 Mac 上的常见 Tokyo Zoo 视频与东京 Citywalk 不属于同一来源，不应混用；本地也没有找到这份 Manning Park 的可验证原始 MP4。

因此 **东京与 Manning Park 的网页仅提供真实静态照片展示，不会制造假 3s Live 动画或谎称已验收原生 Live Photo**。要接入和悉尼相同的真实自动 Live，需要未来补充可匹配的 10 秒原始 MP4 和片内 PTS，并重新做来源/时间对齐和视频验收。

已发布的悉尼页面仍有真正的 3s 自动 Live，不受影响。

## 测试结果

- Mac 本地页面：东京 6 章、47 终选、165 总照片；Manning Park 0/10/20s 三组各 1 章，分别 16/17/16 终选、162/157/159 总照片。
- 浏览器真实 E2E：桌面和手机 390×844 视口，无横向溢出；Day 点击进入 Chapter、完整故事、候选图片展开、原 JPG 放大、偏移组切换正常。
- 从公网访问 GitHub Pages：根目录仍为悉尼，examples、tokyo、manning-park 的 HTML、JS、CSS 和实际 JPG 均返回 HTTP 200；东京及 Manning Park 的真实 Chrome 公网测试通过。
- 页面使用 GitHub Pages 静态服务，无 Python API、数据库、模型调用。**本轮新增 VLM API 调用 0 次，费用 ¥0**。

## 离线下载与复现

Mac 下载目录已复制：

~/Downloads/Nexleap_One_Tokyo_ManningPark_Offline_20261109.zip

该 ZIP 约 70 MB，包含完整 HTML、CSS、JS、JPG，可直接解压在其他 Windows/Mac 电脑中打开 tokyo/index.html 或 manning-park/index.html。东京/Manning 页面可完全离线运行；悉尼导航链接会打开公网原有站点，不包含在该 ZIP 中。

复现代码：

- scripts/nexleap_curated_examples_export.py：从四组整理结果.json 和 643 张真实 JPEG 导出静态站点，并验证真实来源与分章状态
- scripts/nexleap_curated_examples_portal.py：生成统一范例入口、GitHub Pages 资源及离线分享 ZIP
- scripts/review_ui/nexleap-example-extensions.js：人工标注相册、候选/未选/排除筛选、真实 JPG 放大等

Mac 工作目录：

~/Documents/Nexleap/work_logs/evidence/nexleap-tokyo-manning-share-20261109/

其中 site/ 是可直接静态托管的网站目录，site/examples、site/tokyo、site/manning-park 为三个入口。源码仓库克隆至独立只读目录 tokyo-manning-chapter-examples-source-20261109，未修改原仓库内容。

## 可见性与素材管理

GitHub Pages 提供**可公开访问**的 URL，不具备基于团队账号的访问白名单。若需要成员登录或禁止其他访问者下载照片，应另用有访问控制的平台。来源仓库本来也是 Public；本展示只发布其真实图片与公开的标注结果，没有额外公开源视频或 API 密钥。
