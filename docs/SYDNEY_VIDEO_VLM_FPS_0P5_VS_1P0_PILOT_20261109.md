# Diary One｜Sydney 视频 Direct VLM：0.5 fps / 1 fps 真实 A/B（2026-11-09）

## 目的与测试范围

研究「将所有真实 10 秒视频输入 VLM」是否能改善场景覆盖、Chapter 划分和动态代表图定位。本次先实施 **16/160 段预实验**，不是完整一天的正式质量验收。

素材来自悉尼 Citywalk 10 秒相位组（offset 10s），已剔除原视频前 72 秒介绍。沿原始约五小时时间线均匀选出 16 个真实 10s 视频片段，按原有顺序形成一份 160 秒分析视频。注意这些源片段相互有采集时间空隙，不得将拼接后 160 秒当成连续行走时长。

早期 FFmpeg / 后期 AVFoundation 的 H.264 编码切片存在不兼容，直接拼接发生解码错误。本轮先把每段独立转码为 **640×360、15 fps、150 帧/10 秒、255 kbps、无音频**，再组合成 160 秒、2400 帧的一份视频。文件 **4,654,960 字节**，Base64 编码约 **6,206,616 字符**（符合百炼 Base64 视频长度限制）。视频 SHA-256：d1f6c85e318ae799be49fb8f011c45e0c593a1afd5aa98150c347676e196eed1。

## 实际请求

模型：qwen3.8-flash；调用方式：OpenAI-compatible chat/completions；消息 content 包含完整统一中文提示词和一项 video_url，video_url.url 为 data:video/mp4;base64 的**相同视频字节**。设 min_pixels=65536、max_pixels=262144、response_format=json_object、enable_thinking=false。两次调用唯一区别是视频项的 fps=0.5 或 fps=1.0。Prompt 告诉模型每个拼接段落相应原始录制时间（见 source_time_map.json），模型仅输出 Chapter 中文文字和 selected_moments.video_time_ms，不输出 JPG/Live 字节。

百炼官方视频请求和上传限制：https://help.aliyun.com/zh/model-studio/vision/

## 真实 API 结果

| 指标 | 0.5 fps | 1 fps |
|---|---:|---:|
| 理论抽帧数量 | 80 | 160 |
| HTTP | 200 | 200 |
| input_tokens | **9,917** | **19,090** |
| output_tokens | **734** | **452** |
| Chapter 数 | **6** | **3** |
| 返回瞬间数 | **14** | **10** |
| 入选的不同原始片段 | **14/16** | **10/16** |
| 模型费用估算 CNY | **0.00991540** | **0.01649240** |
| 格式/位置校验 | 通过 | 通过 |

模型输入 Token 相差 1.925 倍；两次费用总计 **¥0.02640780**。计价依据本地研究环境设置的输入 ¥0.8/百万 Tokens、输出 ¥2.7/百万 Tokens。两次真实模型返回 HTTP 200、finish_reason stop、合法 JSON，均只调用了一次。

0.5 fps 生成的六章：歌剧院与环形码头、海滨步道与自然海湾、达令港与现代天际线、CBD绿地与历史拱廊、街头巷尾与战争纪念碑、皇家植物园巡礼。

1 fps 生成的三章：悉尼歌剧院与环形码头、海湾休闲与植物园漫步、城市街区与花园细节。

实际从视频重新解码截帧检查，1 fps 在这次输出中把帆船和海港其他场景合并，把岩石海湾与战争纪念碑合并；0.5 fps 保留了较多不同区域。**这不是说 0.5 fps 一定更准确**：两种 fps 都只有一次非确定性生成，并且本次只包含 16 个片段，不能推广为完整 160 段的正式最优 fps 结论。

## 从 VLM 时间点恢复封面及 3 秒 Motion

把模型输出的拼接视频时间 t_ms 映射回原始 10 秒视频：

- slot = floor(t_ms / 10000)，从 0 开始；
- source_asset_id = source_time_map[slot] 记录的原始资产；
- focus_pts_ms = t_ms - 10000 × slot；
- 原始长视频相对时间 = 该源片段原始起点 + focus_pts_ms；
- 截取三秒范围 [clamp(focus_pts_ms / 1000 - 1.5, 0, 7), start+3]，从真实原始 10 秒 MP4 解码封面 JPG / 动态 MP4。

已针对每组前两个模型选点，从**原始 10 秒源文件**共还原 4 张 JPG 和 4 段约 3.003 秒的 MP4，来源可追溯，详见本地 LIVE_MOTION_SOURCE_RECONSTRUCTION.json。视频时间是模型建议，发布时仍需要准确 PTS、图文一致性和清晰度校验；此实验不是系统 Apple Photos Live Photo 导出测试。

## 下一步正式 160 段对照

如需严谨比较 B 方案：将同一 10s 偏移组的**全部 160 个 10 秒视频**按原顺序处理（约 1600 秒实际拍摄）。由于 Base64 视频小于 10 MB，建议把分析视频上传至受控私有对象存储，以短期签名 HTTPS URL 提供给模型。保持文件、时间映射、模型、Prompt、max_pixels、输出结构一致，仅改变 fps。确保模型输出的视频时间点能映射至真实原始 10s MP4，并用相同规则多次评估 Chapter 连贯性、关键场景召回、图库/动态片段质量和总费用。

**本次不能与旧的 235 张 JPEG 基线直接做费用或效果排名**：它们不是同一批视觉输入，且此次使用的是压缩后的 640×360 片段集合。音频未参与识别。

## Mac 本地资料

实验根目录：~/Documents/Nexleap/work_logs/evidence/sydney-video-fps-ab-20261109/

主要文件：video_fps_ab.py（可运行双 fps 真实 API 实验）、assess.py（映射位置并抽真实 JPG）、source_time_map.json、chapter_prompt.txt、preflight.json、fps_0p5_status.json、fps_1p0_status.json、两组模型原始 JSON、FINAL_VIDEO_FPS_COMPARISON.json、REAL_VIDEO_FPS_0P5_VS_1P0_REVIEW.html、source_motion_reconstruction/（从原视频恢复的 JPG 和 3s MP4）。

命令：先执行 python video_fps_ab.py prepare，再执行 python video_fps_ab.py run --fps 0.5 与 python video_fps_ab.py run --fps 1.0，最后 python assess.py。已有 status 文件会拒绝重复计费。

所有视频和模型原始故事保留在 Mac。实验还未接入线上 Diary One 视频 API，也没有上传整段约五小时的原始视频。