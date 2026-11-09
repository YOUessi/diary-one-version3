Nexleap One｜Sydney Citywalk · 六组算法对照离线版

一、如何给同事观看
1. 把整个 ZIP 文件发给对方。
2. 对方在 Windows / macOS 上解压，保留内部 Nexleap_One_Sydney 文件夹完整。
3. 双击这个文件夹里的 index.html，推荐用 Chrome / Edge 打开。
4. 顶部切换「抽帧＋VLM」「视频 0.5 fps」「视频 1 fps」，再选六个偏移组。
5. Day 时间线里的封面、Chapter 详情的大幅封面和下面的照片，都会在进入可见区域时静音自动播放 3 秒 Live；滑到下一张会自动切换，离开屏幕会暂停。
6. 可展开 Chapter 看到完整 Story、全部关键瞬间和真实入选照片；My story、收藏仅存在对方自己的浏览器中。

二、内容数量
- 6 个偏移组（10s / 20s / 30s / 50s / 60s / 70s）。
- 每组对比三条路线：原有 JPEG＋VLM，纯视频 VLM 0.5 fps、1 fps。
- 共 129 个 Chapter、701 张实际入选静态照片、694 个不同的真实 3 秒 Live 视频。
- 页面包含原有的英文与中文模型故事，保留实验结果，不修改原始模型输出。

三、常见问题
- 看不到动图：确认解压后的 media/live3s 子文件夹仍在，推荐用 Chrome 或 Edge 而不是微信内置浏览器。
- 如果本地文件播放被浏览器安全策略拦截，可以在 Nexleap_One_Sydney 文件夹打开终端执行：
  python3 -m http.server 8080
  再浏览器打开 http://127.0.0.1:8080/
- 无须联网，无须运行百炼 API，不需要对方连接我的 Mac。
- Live 是网页循环播放的 3 秒无声 MP4，不是 iPhone Photos 原生的 HEIC/MOV Live Photo。
- 分享包不含原本 5 小时原视频、原始 10 秒片段、密钥或私人访问令牌。

四、素材授权
悉尼 Citywalk 原始视频来源：Prowalk Tours（第三方版权所有）。
本包仅供拥有适当权限的内部研究与评审使用。公开发链接、把视频剪辑和截图上传公开网站等行为，
应先确认取得版权所有者授权或适用合法例外。
Prowalk Tours 官方授权页面：https://www.prowalktours.com/licensing

五、上线网页
这是完整的 HTML / CSS / JS + MP4 静态网站，可部署 GitHub Pages、Cloudflare Pages、Railway、
任意静态服务器。但当前没有在外部公网发布第三方视频素材。
如已取得授权，可以将本目录原封不动部署至支持静态资源的网站，无须数据库或模型 API。
