# Evidence 语义路由调试手册（App + 前后端）

> **能力边界（写死）：** 这是「轻量级视觉语义理解」，**不是**多模态大模型读懂整段视频。  
> App 获得的是：Feature Print 相似度 + 粗粒度分类标签 → 规则选 **1 / 3 / 5 / 10** 帧。  
> **不能**稳定认地点名、行为因果、店招 OCR、日记主观「最有意义」。

参考工程（算法真相源）：

`E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router`  
（`semantic.py` · `SemanticRoutingProfile` · `semantic_router_v01_profile` · `vision_feature_print.m`）

App 落地：`apps/mobile/src/evidence/` · 原生：`modules/diary-one-vision/`  
仍保留：去重 `dedupeMedia` · 压缩 `evidenceNormalize` · Bundle V04。

---

## 1. 三件套在 App 里怎么串

```text
选视频
  → 去重（original_sha256）
  → 探针：约每 1s + 最后一帧（VideoThumbnails）
  → 分析器：
       native_vision（iOS Dev Client）
    或 fallback_expo_go（仅调试，degraded）
  → 规则路由 40% Feature + 60% Classify
  → 选 1/3/5/10 代表帧时间戳
  → 抽帧 → 压缩 768×1024 JPEG → bundle.json
  → sidecar：semantic_route_{assetId}.json
  → （可选）上传 Dev Lite / 百炼云处理
```

照片仍是：**单帧 + 去重 + 压缩**，不跑语义路由。

---

## 2. Apple Vision（真模型）vs Expo Go

| 环境 | Feature Print / Classify | 怎么开 |
|------|-------------------------|--------|
| **Expo Go** | ❌ 无原生 Vision | 用 fallback，**不可当质量验收** |
| **`npx expo run:ios` / EAS Dev Client** | ✅ `DiaryOneVision` | 真 768-d + Top10 标签 |
| Windows PC Dev Lite | `semantic-analyze` → 501 | 路由在手机 TS；Mac 才可接参考 Python helper |

真 Vision 调试必须出 **开发包**（不是商店里的 Expo Go）：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
# 需 Mac + Xcode 或 EAS iOS 构建机
npx expo run:ios
# 或: eas build --profile development --platform ios
```

模块：`VNGenerateImageFeaturePrintRequest` Revision 2 + `VNClassifyImageRequest` Top 10  
（对齐 `scripts/vision_feature_print.m`）

---

## 3. Expo Go 联调流程（规则 + 去重/压缩先通）

1. PC：`start-dev-lite.ps1`（有 Key 用 qwen）  
2. 手机 Expo Go → Lab：**1 Apply → 2 Ping**  
3. **B · Import** 选一段视频（或 Demo 先验证云管线）  
4. Active tasks：`bundle_ready` 文案含 `frames=` / `analyzer=`  
5. **C · Semantic route debug** 看上次路由摘要  
6. 查设备 bundle 目录：`semantic_route_asset-0.json`  
7. 若 `degraded: true` / `analyzer=fallback_expo_go` → **只证明规则链路通**，不是 Vision 质量

---

## 4. Dev Client（真 Vision）调试流程

1. 安装带 `diary-one-vision` 的 Dev Client  
2. Lab 同上导入视频  
3. 确认 audit：`modelId` 含 `APPLE_VISION_FEATURE_PRINT_REVISION_2`  
4. `analyzer=native_vision`，`degraded` 应为 false  
5. 对照参考包现象自检：  
   - 街区→店铺/拱廊：倾向升到 3 帧  
   - 店铺→广场：倾向 3 帧  
   - 同街持续变化：可降到 1 帧（语义中心而非固定第 5 秒）  
6. 再跑 Demo / 云管线，确认选帧后的 Bundle 仍能过 BFF→Diary

---

## 5. 前后端接口（Dev Lite）

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/v1/evidence/semantic-analyze` | 上传探针 JPEG；Windows 预期 501 |
| POST | `/v1/evidence/semantic-route` | 已有向量/标签时做服务端审计（可选） |
| POST | `/v1/day-revisions` | 既有云处理主链（不变） |

Health：`GET /health` 仍看 BFF + X02。

---

## 6. 验收清单

- [ ] 照片：去重跳过重复；压缩 768×1024；不进 Captured 测试源纪律  
- [ ] 视频 Expo Go：能出 `semantic_route_*.json`（允许 degraded）  
- [ ] 视频 Dev Client：`native_vision` + 1/3/5/10 与 reason 可读  
- [ ] 黑帧/无效探针被排除  
- [ ] 语义失败时回退旧 duration 窗口，任务不静默假成功  
- [ ] 云链路（fixture/qwen）在选帧后仍 Succeeded  

---

## 7. 与参考包 Profile 对齐

App 默认对齐 **`M4_SEMANTIC_ROUTER_V01` / Apple Vision gate**：

- `feature_weight = 0.40`  
- `classification_weight = 0.60`  
- `probe_step_ms = 1000` + 最后一帧  
- 档位：`FRAME_1 | FRAME_3 | FRAME_5 | FIXED_SEQUENCE_10`  

MobileCLIP 研究分支（`M4_MOBILECLIP_*`）**未**打进 Expo Go；需权重与独立实验脚本，见参考包 README。
