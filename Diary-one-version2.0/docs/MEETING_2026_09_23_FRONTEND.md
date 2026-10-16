# 会议 2026-09-23 · 前端落地说明

依据：`question/Diary-One_量产商业化议题与开会清单_2026-09-23.md`  
问卷 UI 已对齐 Figma `node-id=2145-2`（2026-10-02 长图）+ 封闭 tag 库 / 负向提示。

## 已落地（App）

| 项 | 实现 |
|----|------|
| 入门问卷（可跳过） | `PreferenceSurvey` · Intro→类别→开放文本→Interest tags→文风→Avoid→Review→Consent |
| Tag 库命中 | `onboarding/tagLibrary.ts` 封闭词表；选项 id 必须命中库 |
| 负向提示词 | Avoid topics → Memory Preference 标题 `Avoid: {label}` + negativePrompt 正文 |
| 写入 Memory Preferences | 同源 Account → Preferences；`memoryPreferencesForUpload` 上云 |
| Account 重填问卷 | Account → Start / Retake preference survey（`mode: account`） |
| 云端同意 ≠ 登录 | `cloudEvidenceConsent` + version |
| Figma 壳 | 顶栏 ✕ / 进度条 / Next·Start·Finish；2 列类别瓦片；chip；文风列表；Review |

## 流程

```
Sign in → OTP → Pair（可跳过 → 权限链）→ Permissions → Setup Complete
  → Hardware basics（可跳过）→ Preference survey（可 Skip）→ Diary
```

Skip 问卷后可在 **Account → Start preference survey** 补填；已有偏好可 **Retake**。

## 明确不做

- 不用问卷填 Topics / 造假记忆
- Tag 不可点成筛选（消费者 Diary 纪律不变）
- 不声称「已学会」——仅声明偏好
