# 算法：App 偏好 → 云端软筛选合同（APP_CLIENT_PROFILE_V01）

**合同状态：FROZEN（V01）** — 产品+算法按此实现；改语义需升 `APP_CLIENT_PROFILE_V02`。

## 状态（2026-10-18 复核）

云端代码已部署，但真实模型调用被 Key 权限 403 阻塞；下表为实现情况，不是本轮真实模型验收结果。当前 App 不默认上传偏好。商用算法/原生及语言差异见 [最终核查](最终核查_PRD与算法_2026-10-18.md)。

| 项 | 状态 |
|----|------|
| App 上传 `app_client_profile` | 已具备结构化 + 旧字符串行兼容；`EXPO_PUBLIC_UPLOAD_MEMORY_PREFERENCES` 默认关闭，需与同意范围一致后开启 |
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

先确认 App 构建已按用户同意范围启用偏好上传；本轮没有静默开启。

1. 问卷填偏好 → Lab B 真图上云
2. Preview / job result 含 `decision_trace.client_profile_audit.present=true`
3. 有 boost/avoid 命中时 `soft_editorial.applied` 可为 true
4. 无证据时仍可能 `NO_GROUNDED_MEMORY`（偏好不能造记忆）

## 代码

- `services/algorithm/.../app_client_profile.py`
- `x01_server._materialize_bundle` / `x02._run_x02_impl`
- `apps/mobile/src/domain/memoryPreferencesCloud.ts`
- 单测：`algorithm/tests/test_app_client_profile.py`
