# 云端大量素材通道（处理 · 筛选 · 输出）

**目标：** 本地已跑通的「大量素材 → V1.75 筛选/出稿」同一合同，经 **订阅云（百炼 DashScope）** 再跑一遍，给 10 月 20 日内测包做质量门。

## 两条通道（不要混）

| 通道 | 入口 | 模型 | 用途 |
|------|------|------|------|
| **本地算法** | eval-web / `POST :8787/x02/v0.4.1/preview` | 本机 X02（可 qwen） | 素材质量、筛选、出稿验收（你已基本通过） |
| **云端商用** | App / PC → BFF `:8790` → Worker → X02 → 百炼 API | 同一 X02 + `DASHSCOPE_API_KEY` | 订阅制扣费路径；内测包真链路 |

本地通过 ≠ 云端通过。云端多一层：上传 multipart、MinIO、Worker、幂等 job、mock 开关。

## 一键打开云端通道

```powershell
cd E:\AI耳机\diary-one\services\bff

# 已保存过 Key：
.\scripts\set-dashscope-key.ps1 -Key 'sk-...'   # 只需一次

# 起 X02(qwen) + Docker BFF/Worker，可选立刻跑一个素材目录
.\scripts\open-cloud-bulk-channel.ps1 -Quality -MediaDir D:\packs\day1 -RequireGrounded
```

仅冒烟（允许空日 mock，**不算质量**）：

```powershell
.\scripts\open-cloud-bulk-channel.ps1 -MediaDir D:\packs\day1
```

已有 Bundle 目录时：

```powershell
.\scripts\smoke-cloud-pack.ps1 -BundleDir D:\packs\day1_bundle -RequireGrounded -ReportDir $env:TEMP\diary-reports
```

## 合同与上限

- Bundle：**V04** letterbox 768×1024（与 App / eval-web 一致）
- X02：最多 **240 assets / day**；感知批：3 assets / 18 frames / 4 MiB
- PC 打包器 `build_pack_bundle.py`：**照片**；视频时长窗请用 App Lab B 或 eval-web 出 Bundle 再 `-BundleDir` 上传
- 质量门：`-RequireGrounded` → 禁止 `dev_lite_fallback`、禁止空 `chapters/ahas`

## 与 Expo Go 关系

手机 Lab **A/B** 走同一 BFF。Demo JPEG 常 `NO_GROUNDED_MEMORY`（正常）。真相册 / PC pack 才验收筛选质量。

## 后续（本地小模型）

本地自训模型与百炼是 **可切换 adapter**，不挡 10/20 内测包。内测包先冻：**云端百炼 + 本通道报告**；本地模型对比体量另轨。
