# 会议 2026-09-23 · 前端落地说明

依据：`question/Diary-One_量产商业化议题与开会清单_2026-09-23.md`  
（腾讯会议链接 `https://meeting.tencent.com/ctm/KzAL061rfd` 无法拉取录屏文稿，以仓库中同日开会清单为准。）

## 已落地（App）

| 项 | 实现 |
|----|------|
| 轻量入门问卷（可跳过） | `PreferenceSurvey` · 8 步 · Onboarding 壳层样式 |
| 写入 Memory Preferences | 同源 Account → Preferences |
| 第 8 题云端同意 ≠ 登录 | `cloudEvidenceConsent` + version；拒绝后上传失败提示 |
| 通知默认 | 问卷映射 `notificationSettings` |
| Figma 纪律 | 移除 Diary 空态「Import from library」；配对页去掉非画板说明文案 |

## 流程

```
Sign in → OTP → Pair（可跳过）→ Permissions → Setup Complete
  → Hardware basics（可跳过）→ Preference survey（可 Skip for now）→ Diary
```

## 明确不做（会议共识）

- 不用问卷填 Topics / 造假记忆
- 不把问卷做成 Figma 未有的独立营销页风格
- 不在消费者 Diary 主屏加非画板 CTA
