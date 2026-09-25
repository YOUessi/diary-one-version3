# Daily Recap · 真视频合成（9:16 MP4）

## 行为

- 按当日 **Chapter** 英雄图生成最多 8 张幻灯片（1080×1920）
- 每张约 **2.5s**，**24fps**，H.264 MP4
- **分享 / 存相册** 使用 `video/mp4`（不再只是静态图）

## 编码路径（自动回退）

| 顺序 | 环境 | 方式 |
|------|------|------|
| 1 | iOS Dev Client / 上架包 | `expo-video-encoder`（本机 AVFoundation） |
| 2 | Expo Go + 已配 BFF | `POST /v1/share/daily-recap/render`（PC **ffmpeg**） |

Expo Go 在 Android / 无原生模块时，**必须**走 Dev Lite BFF + ffmpeg。

## PC 准备（Expo Go 联调）

1. 安装 [ffmpeg](https://ffmpeg.org/download.html) 并加入 `PATH`
2. 验证：`ffmpeg -version`
3. 起 Dev Lite：`services/bff/scripts/start-dev-lite.ps1`
4. `GET http://<LAN>:8790/health` → `ffmpeg_available: true`
5. 手机 Lab：**Production BFF URL** 指向 PC `:8790`

## API

- `POST /v1/share/daily-recap/render`（Bearer：`dev-token` 或 `session_token`）
- Multipart：`slide_count`, `slide_0`…`slide_N`（JPEG），`fps`, `slide_duration_sec`
- 响应：`video/mp4` 二进制

量产 Docker BFF 同样路由（容器内需安装 ffmpeg 或挂载宿主二进制）。

## 依赖

- App：`expo-video-encoder`（仅 iOS 原生编码）
- BFF：`shared/recap_render.py`
