# 质量门 + 剩余算法（2026-10-09 已落地）

面向你本地/真机测试。代码已齐；**真 qwen 需要你本机 Key + 真实照片包**。

## 1. 真 qwen + 关 mock

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\set-dashscope-key.ps1 -Key 'sk-...'   # 若尚未写入
.\scripts\start-quality-stack.ps1               # qwen + ALLOW_MOCK_PREVIEW=false
```

Lab Ping：`mock=no`，且 x02 非 fixture。

## 2. 真实日 pack 质量门

```powershell
.\scripts\run-quality-gate.ps1 -MediaDir D:\packs\day1
# 或
.\scripts\smoke-cloud-pack.ps1 -MediaDir D:\packs\day1 -RequireGrounded -ReportDir $env:TEMP\diary-q
```

`-RequireGrounded` 现在会 **硬失败**：mock=on、fixture、空章、mock_fallback、无标题。

## 3. 偏好 → V1.75 筛选（合同已冻）

`APP_CLIENT_PROFILE_V01` 冻结说明：`ALGORITHM_CLIENT_PROFILE.md`  
行为：Structure/Writer 软引导 + 选章前后软重排；**不造记忆、不硬删 grounded**。

## 4. Topics 自由聚类

App `rebuildTopicsFromChapters`：Jaccard 聚类（≥0.34）+ 残留同 tag Topics；带 person/event/place facet。

## 5. Search Agent

Memory 搜索结果上方 **Search summary**（抽取式本地摘要，非对话 Agent）。一级结果仍是 Chapters。

## 6. Live / 轮播头图

Chapter Detail：`HeroLiveCarousel` — 多海报轮播；有 mp4 时可切 LIVE/STILL。

---

## 你怎么测（建议顺序）

1. `start-quality-stack.ps1` → Ping `mock=no`  
2. 问卷填偏好 → Lab B **真日常图** → Diary 有 chapter；可选抓 result 看 `client_profile_audit`  
3. Memory 搜关键词 → 看 Search summary  
4. 打开章节 → 头图轮播 / LIVE  
5. Memory → Your Topics → 看聚类与 People/Events/Places  
6. PC：`run-quality-gate.ps1 -MediaDir <真照片目录>`  
