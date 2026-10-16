# 算法：App 偏好 → 云端软筛选合同（APP_CLIENT_PROFILE_V01）

**合同状态：FROZEN（V01）** — 产品+算法按此实现；改语义需升 `APP_CLIENT_PROFILE_V02`。

## 状态（2026-10-09）

| 项 | 状态 |
|----|------|
| App 上传 `app_client_profile` | ✅ 结构化 + 兼容旧字符串行 |
| BFF / Worker 转发 | ✅（原有） |
| X02 落盘并读取 | ✅ `x01_server` → `app_client_profile.json` |
| Structure / Writer 软引导 | ✅ prompt 注入 |
| 选章前 + 出稿后软重排 | ✅ boost 靠前 / avoid 靠后；**不删 grounded 章** |
| Topics 自由聚类 + 人/事/地 | ✅ App `rebuildTopics` |
| 硬过滤 / 自训模型 | ❌ 不做（违 V1.75 证据纪律） |

## 合同字段

```json
{
  "schema_version": "APP_CLIENT_PROFILE_V01",
  "memory_preferences": ["title: text", "..."],
  "boost_tags": ["Coffee"],
  "avoid_topics": ["Work stress detail"],
  "writing_style": "Empathetic and warm",
  "preferred_categories": ["Daily life"]
}
```

## 验收

1. 问卷填偏好 → Lab B 真图上云  
2. Preview / job result 含 `client_profile_audit.present=true`  
3. 有 boost/avoid 命中时 `soft_editorial.applied` 可为 true  
4. 无证据时仍可能 `NO_GROUNDED_MEMORY`（偏好不能造记忆）

## 代码

- `services/algorithm/.../app_client_profile.py`
- `x01_server._materialize_bundle` / `x02._run_x02_impl`
- `apps/mobile/src/domain/memoryPreferencesCloud.ts`
- 单测：`algorithm/tests/test_app_client_profile.py`
