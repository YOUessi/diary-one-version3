# Windows：MobileCLIP 本地轻处理 → 上云 chapter

目标路径（手机操作，PC 只当后端）：

```text
手机选素材
  → 去重 / 768×1024 压图（App）
  → 探针帧上传 BFF
  → Windows MobileCLIP 出 512-d 向量（+ 可选场景标签）
  → App TypeScript 语义路由选 1/3/5/10 帧
  → Bundle → POST /v1/day-revisions → 云端生成 chapter
```

参考算法包：`E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router`  
BFF 接入：`services/bff/dev_lite/mobileclip_backend.py`

> Apple MobileCLIP 检查点受 **Apple ML Research Model License** 约束，仅非商业科研实验；商店产品不得分发该权重。

---

## 1. 一次性准备（PC）

### 1.1 权重文件（已对接官方下载）

来源：[apple/ml-mobileclip `get_pretrained_models.sh`](https://github.com/apple/ml-mobileclip/blob/main/get_pretrained_models.sh)  
URL：`https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s0.pt`  
期望 SHA256：`809b408eff74f8058843e86a1f92967097d42ba782450e85b8f4867b7f0ca0b7`

一键下载并写入用户环境变量：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\download-mobileclip-s0.ps1
```

落盘路径：

```text
E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router\checkpoints\mobileclip_s0.pt
```

`start-dev-lite.ps1` 会自动探测该路径。

### 1.2 Python 依赖

用 Dev Lite 同一解释器：

```powershell
cd E:\AI耳机\diary-one\services\bff
python -m pip install -e "E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router[mobileclip-experiment]"
# 可选：场景词表标签（prompt router）
python -m pip install --no-deps "git+https://github.com/apple/ml-mobileclip.git@48faa0fea4b08d74188b3841771aca6ff2c92852"
```

还需要系统 **ffmpeg**（探针抽帧在手机侧；Recap 仍要 PC ffmpeg）。

### 1.3 启动

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\start-dev-lite.ps1
```

浏览器打开：`http://127.0.0.1:8790/health`  
应看到类似：

```json
"mobileclip": { "available": true, "model_id": "MOBILECLIP_S0_IMAGE_512_SCENE_PROMPTS_V01", ... }
```

`available: false` 时看 `reason`（缺权重 / 缺 torch 等）。

---

## 2. 手机怎么测

1. Expo Go → Lab：**1 Apply → 2 Ping**（看 health 行里是否带 `mc=yes`）
2. **B · Import from photo library** 选一段**视频**（或 **A2 · Simulation video**）
3. **Active tasks** 等到成功 → Diary 有 chapter
4. **C · Semantic route debug**  
   - 期望：`analyzer=remote_bff`，`modelId` 含 `MOBILECLIP`  
   - 若仍是 `fallback_expo_go`：BFF MobileCLIP 未就绪（回看 /health）

照片路径仍是：去重 + 压图 → 上云（不跑语义选帧）。

---

## 3. 环境变量一览

| 变量 | 含义 |
|------|------|
| `DIARY_ONE_MOBILECLIP_CHECKPOINT` | `mobileclip_s0.pt` 绝对路径 |
| `DIARY_ONE_EVIDENCE_ROUTER_ROOT` | 参考包根目录（脚本可自动设） |
| `DIARY_ONE_MOBILECLIP_DEVICE` | `auto` / `cpu` / `cuda` |
| `DIARY_ONE_MOBILECLIP_PROMPTS` | `1` 开场景标签（需 apple/ml-mobileclip pip）；装不上时自动回落 **仅 512-d 图像向量**（仍可做 1/3/5/10 选帧） |

---

## 4. 接口

| 方法 | 路径 | 作用 |
|------|------|------|
| GET | `/health` | `mobileclip.available` |
| POST | `/v1/evidence/semantic-analyze` | 探针 JPEG → 向量/标签 |
| POST | `/v1/day-revisions` | 上云生成 chapter（不变） |

---

## 5. 与 Apple Vision 的关系

| 环境 | 语义后端 |
|------|----------|
| Windows + 本配置 | **MobileCLIP on BFF** |
| iPhone Dev Client | **DiaryOneVision**（产品默认） |
| Expo Go 且 BFF 无权重 | degraded fallback（仅联调） |
