# Diary One Canonical Checkpoint V1.24 — S13 Selected HQ Materialization & Export

**状态：** FROZEN PRODUCTION-SHAPED CONTRACT
**冻结日期：** 2026-08-29
**覆盖阶段：** S13A Materialization + S13B Export/Publish Adapter
**继承：** V1.21 S10 HQ/route contracts、V1.22 S11、V1.23 S12
**仓库边界：** 只定义云端算法侧接口与本地参考；不决定 App 上传网络/电量/存储 UX，不触碰 Firmware/SDK 或共享状态文件

## 1. 核心结论

S13 只把已经选中的精确 EvidenceAnchor 转换成最终媒体，并导出已经验证的 Diary。

```text
S12A MATERIALIZATION_ALLOWED
→ resolve selected HQ source intervals
→ render exact PHOTO / LIVE_2S / VIDEO_5S routes
→ verify receipt + checksum + provenance
→ activate only predeclared fallback/D1/Hero alternatives when legal
→ return immutable ActivationDelta
→ affected S11 revalidation + S12B
→ build UserDiaryExport + InternalAuditRun
→ atomic artifact commit / published-head CAS adapter
```

S13 不重新理解全天、不重选 Memory、不改变事实、不创造临时漂亮素材，也不把 render 失败解释为事件没有发生。

## 2. 两个执行阶段

### 2.1 S13A｜Selected HQ Materialization

输入：S12A pass、S10 exact HQ request manifest、active route 与 dormant fallback metadata。

输出：

```text
S13MaterializationBundle
  request_receipts[]
  render_receipts[]
  shared_materialization_map[]
  activation_deltas[]
  terminal_failures[]
  retry / latency / bytes / cost provenance
  immutable fingerprint
```

S13A 不能更新用户 published head。

### 2.2 S13B｜Export & Publish Adapter

输入：S12B `ACTIVATE_CURRENT_REVISION`、exact materialization bundle 与 expected head。

输出：

```text
UserDiaryExport
InternalAuditRun
PublicationCommitRecord
```

只有实际 CAS pass 后，Commit Record 才能写 `ATOMIC_PUBLISHED_CURRENT`。本地 reference runner 永远写 `reference_only=true`，不会模拟成真实发布。

## 3. Production-shaped Component Boundary

S13 使用四个可替换接口，不绑定具体云供应商：

| Interface | 职责 | 明确不做 |
|---|---|---|
| `HQSourceResolver` | 根据 exact source ref/interval 返回可读源或 typed failure | 不搜索全天、不扩大时间窗 |
| `MediaMaterializer` | 按 format policy 解码、裁切、编码 PHOTO/LIVE/VIDEO | 不改变 Anchor/semantic scope |
| `ArtifactStore` | checksum、幂等写、临时对象与最终对象原子提升 | 不更新 Memory membership |
| `PublicationStore` | compare-and-swap published head，写 commit record | 不重新验证内容 |

真实云存储、API/Agent destination、App 后台上传时间仍是独立工程/产品专项；S13 只要求 `source_ref` 可由授权 resolver 解析。

## 4. 输入合同

每个 active visible consumer 对应一个 `HQRequest`：

```text
request_id
revision_id / snapshot_id
memory_id / media_id
raw_asset_id / source_family_id
evidence_anchor_ref
semantic_scope_id
source_start_ms / source_end_ms
primary_route
fallback_routes[0..2]
render_policy_ref
source_policy_ref
retry_policy_ref
expected_input_hash?
```

规则：

1. 只接受 current S10 manifest；
2. source interval 不能越过 RawAsset 边界；
3. Fallback 必须在 S10 预声明，最多两条；
4. Fallback 不得改变 Beat/peak、Anchor 或 semantic scope；
5. dormant route 正常不取 HQ、不 render；
6. same source/interval/render fingerprint 可以安全 coalesce；
7. 多 consumer 共享 materialization 不合并其 Memory/Claim identity。

**案例：** Chapter 与 Aha 在无损替代不存在时合法引用同一 canonical render。S13 只下载/渲染一次，但导出两个 consumer ref；S12 仍分别验证两个 Memory 的故事职责。

## 5. Request 与 Materialization 幂等性

### 5.1 Fingerprint

Materialization fingerprint 至少覆盖：

```text
source identity + source content hash
exact interval / frame timestamp
EvidenceAnchor / semantic scope
target format
crop / orientation / color / audio / codec policy refs
materializer version
```

相同 fingerprint 的成功对象可复用；任一字段变化都产生新对象，不能覆盖旧对象。

### 5.2 Idempotency

- 同一个 request/fingerprint 重试返回同一成功 receipt；
- 同一 Revision 的并发 worker 只能有一个 final object；
- 临时对象不进入 User Export；
- stale worker 不能覆盖新 policy/version 的对象；
- partial multipart/upload/render 必须可安全清理或隔离。

## 6. Source Resolution

### 6.1 Typed outcome

```text
SOURCE_AVAILABLE
SOURCE_PENDING_RETRYABLE
SOURCE_TERMINAL_UNAVAILABLE
SOURCE_CONTRACT_INVALID
```

`UNKNOWN`、timeout、暂时网络失败和队列等待属于 pending/retryable，不能提前宣判 terminal。

### 6.2 最小范围

- PHOTO 请求 exact timestamp/frame；
- LIVE_2S 请求围绕 exact Anchor 的合法 2 秒窗口；
- VIDEO_5S 请求合法 5 秒窗口；
- 必须按 S10 已给出的边界裁切，不能为了成功擅自扩到整段视频；
- 多个重叠 exact requests 可以 coalesce transport，但分别验证输出。

### 6.3 无二次用户交互

用户已经 Sync 后，S13 不增加“请再上传”的交互。source 暂时不可得时走后台队列/HOLD；所有 route terminal 时按失败合同处理。App 的 Wi‑Fi/蜂窝/电量策略仍由 App 专项决定。

## 7. Decode / Timebase / Render

### 7.1 必须验证

- container/codec 可解析；
- duration 与 source interval 合法；
- rotation/orientation/color metadata 有明确 policy；
- variable-frame-rate/timebase 映射可追溯；
- requested Anchor 落在实际解码范围；
- LIVE/VIDEO 时长、首尾帧与音频策略符合 versioned profile；
- 输出尺寸/码率/压缩/封装符合 target format policy；
- actual bytes 的 checksum、length 与 MIME/container 一致。

### 7.2 数值边界

本检查点冻结“所有数值必须来自 versioned render policy、被 receipt 记录并通过测试”，但不猜测具体分辨率、码率、timebase tolerance 或压缩质量。它们必须通过真实设备素材 benchmark 后以新的 policy version 发布。

**案例：** 73 秒 Manual 的 Anchor 由上游合法 content unit 给出时，S13 可按 exact interval render；S13 不反向决定 73 秒视频应切几个 Window。

## 8. Retry 与 Failure Class

### 8.1 Bounded retry

每个 exact operation 必须引用有限 retry policy：

- transport/source retry；
- decode retry；
- render retry；
- store/commit retry。

retry 次数与 backoff 是可配置工程参数，不能无限；同 fingerprint retry 不创建新的语义 route。reference runner 使用确定性 outcome，不访问网络。

### 8.2 Terminal 证明

只有以下类别可在策略完成后成为 terminal：

- source 明确永久不存在/损坏且不可恢复；
- codec/container 经支持矩阵确认不可解码；
- exact interval 无有效帧且时间事实已确认；
- render policy 对该源确定不可满足；
- checksum/content identity 永久冲突；
-权限/生命周期明确禁止访问（具体治理策略另行定义）。

普通 timeout、服务 5xx、队列等待、网络断开、电量限制或尚未跑完重试不是 terminal。

### 8.3 Contract invalid

ref 缺失、Revision 混用、interval 越界、route 改变 semantic scope、priority 重复、checksum schema 损坏，进入 `CONTRACT_INVALID`；不能借 Fallback 吞掉工程错误。

## 9. Fallback / D1 / D2 / Hero Activation

### 9.1 Fallback

```text
Primary SUCCESS → use Primary
Primary transient/unknown → retry or HOLD
Primary terminal → try predeclared Fallback 1
Fallback 1 terminal/collision → try predeclared Fallback 2
all exhausted → exact failure routing
```

每次成功的非 Primary activation 创建 immutable delta，不原地修改 S10 MediaDecision。

### 9.2 D2 collision

Fallback 与 healthy Primary 冲突时：

- healthy Primary 锁定；
- 当前 failing position 尝试下一预声明 route；
- 不移动健康媒体，不创建新 Anchor，不搜索漂亮替代；
- 无合法 route 时进入 D1/HOLD/BLOCK。

### 9.3 D1 survivor

Chapter 只有一个 member terminal 且 exact survivor set 已在 S10 预验证时，允许每 Chapter 一次 D1：

- 删除 exact failed member；
- 不从 Candidate 池补新媒体；
- resulting set 仍满足 Compact/Standard、core coverage、chronology、Hero 与 narrative；
- affected S11/S12 全部重验。

第二个 member 又失败时不能连续 D1，进入 HOLD/BLOCK。

### 9.4 Aha

Aha 所有 route runtime exhausted：

- 不使用邻近 support frame；
- 不删除 Aha 后发布其余 current set；
- 不新增 S09 re-selection；
- 使用仍合法 prior 或 HOLD/BLOCK。

### 9.5 Hero Alternate

只能激活 S10 已声明的一个 Passive Alternate；它不增加正文项。激活后重验 cover provenance、format 与 Claim alignment。

## 10. Receipt Contract

成功 receipt 至少包含：

```text
request_id / route_id
memory_id / media_id / consumer_id
source identity + exact interval
input hash / output checksum / byte length
actual format / duration / dimensions
render policy / materializer version
attempt / latency / retry / cost
artifact object ref
shared materialization ref?
completed_at
```

reference runner 没有真实 media bytes，因此使用：

```text
materialization_status = REFERENCE_RECEIPT_SUCCESS
media_bytes_materialized = false
reference_only = true
```

这类 receipt 可验证编排、fingerprint 与 fallback，但不能冒充真实 HQ render receipt。

## 11. Affected-artifact Revalidation

Activation delta 至少触发：

| 变化 | 必须重验 |
|---|---|
| LIVE↔PHOTO/VIDEO format | S11 media-dependent wording + S12 media gate |
| source/route changed but same scope | provenance、quality、duplicate、checksum |
| D1 member removed | Chapter core coverage、Story/Title/Tag、Hero、数量 |
| Hero Alternate | cover-related Claim、format、source |
| cross-memory reuse changed | V1.20/V1.21 pair and reuse decisions |

若 route 改变 Anchor 或 semantic scope，不是普通 revalidation，而是 contract invalid。

## 12. User Diary Export

用户导出只包含产品需要的内容：

```text
user_local_day
revision_id / lifecycle state
day_state
chapters[]
  title / story / time label
  visible media refs + hero
  optional display labels
ahas[]
  moment line / time label
  exactly one visible media ref
  optional display labels
protected user text refs
export fingerprint
```

不向 UI 暴露：内部模型分数、淘汰 Candidate、Token/成本、retry、provider failure、Claim Ledger 或 Evidence IDs。

## 13. Internal Audit Run

内部审计必须能追溯：

```text
RawAsset → Evidence → Observation → Moment
→ Candidate → Selected Memory
→ Beat → Anchor → MediaDecision → HQ request
→ Claim → Narrative/Tag/Entity
→ Materialization → Activation → S12B → Export/Commit
```

并保存：

- input/policy/model/prompt/parameter/taxonomy/materializer versions；
- selected/rejected/omitted reasons；
- token、VBU、美元、latency、retry、cache；
- visible consumer、unique source、materialization 与 shared reuse 分账；
- validator results、human label/evaluator refs（若有）；
- current/prior/expected-head/CAS 结果。

## 14. Atomic Write & Publish

1. 每个 artifact 先写不可见临时对象；
2. checksum/length/metadata 全通过后原子提升；
3. User Export 与 Audit 都成功后形成 exact export fingerprint；
4. S12B 授权且 expected head 未变化时执行 CAS；
5. CAS pass 后写 immutable Commit Record；
6. CAS stale 不覆盖新 head；
7. partial artifact 永不进入 published export；
8. 已发布后 source/存储事故走恢复/新 Revision，不回写历史 receipt。

## 15. 成本上界与分账

继承 V1.21：

```text
Chapter body media <= 25
Aha visible media <= 3
body + Aha visible consumers <= 28
Chapter Hero derivative consumers <= 5
active render consumers <= 33
unique active HQ source requests <= 28 before coalescing
dormant fallback refs <= 56 (metadata only)
```

S13 成本审计分别记录：

1. HQ bytes resolved；
2. unique source downloads；
3. materialization count；
4. shared-materialization reuse count；
5. derivative Hero count；
6. output bytes；
7. retries/terminal failures；
8. compute/storage/egress cost。

在真实 codec、设备源、网络和云价格 benchmark 前，不承诺每用户固定 MB、美元或时延。

## 16. Canonical Failure Cases

1. **Primary terminal，Fallback success：** activation delta→S11/S12B revalidation→publish eligible。
2. **Primary timeout：** retry/HOLD；不激活 Fallback。
3. **Fallback 改 Anchor：** contract invalid；不能用“画面差不多”通过。
4. **Fallback 与健康项相撞：** 健康项锁定，尝试下一 fallback。
5. **Chapter 一项 exhausted：** exact D1 survivor pass 才允许一次删除。
6. **Chapter 两项 exhausted：** HOLD/BLOCK；不连续 D1。
7. **Aha all routes exhausted：** HOLD/BLOCK；不使用 support frame。
8. **同源 Chapter/Aha necessary reuse：** 一个 materialization、两个 consumer，Claim 分离。
9. **checksum mismatch：** object 不可见，按 typed failure 处理。
10. **CAS stale：** artifacts 保留审计，published head 不变。

## 17. Frozen Invariants

1. selected HQ only；
2. 不上传/搜索全天 Raw；
3. exact interval 不擅自扩大；
4. Primary/Fallback 路径预声明且有界；
5. transient 不等于 terminal；
6. contract invalid 不被 fallback 掩盖；
7. route 不改变 Anchor/semantic scope；
8. D1 每 Chapter 最多一次；
9. Aha 失败不删除后继续发布；
10. healthy Primary 锁定；
11. exact reuse 可共享 materialization、不共享 Memory identity；
12. activation delta immutable；
13. affected artifacts 必须重验；
14. checksum/bytes/format/timebase 可审计；
15. idempotent fingerprint 与 atomic write；
16. S12B 后才允许 publish adapter；
17. CAS pass 后才更新 head；
18. User Export 与 Internal Audit 分离；
19. reference receipt 不冒充真实 render；
20. 失败不改写事实。

## 18. OPEN / Deployment Boundary

- App 无感上传的实际 Wi‑Fi/蜂窝/电量/后台时机；
- source 实际落在云存储、设备代理、API 或其他服务的拓扑；
- PHOTO/LIVE/VIDEO 的分辨率、码率、压缩、音频与 timebase 数值；
- provider/cloud/queue/database/object-store 技术选型；
- retry/backoff/SLO/告警的真实数值；
- source/object retention、privacy、encryption、deletion 与治理；
- 真实硬件/编码素材下 P50/P95/P99 成本、时延与成功率。

这些 OPEN 项阻止“已完成云端 Production 部署”的声明，但不阻止 S13 control-plane 合同与本地 reference pipeline 冻结。

## 19. Freeze Record

S13 的选择后 HQ materialization、失败分类、预声明 activation、两阶段重验、导出与原子发布接口至此冻结。任何实现都必须保留 selected-only、immutable、bounded、revalidated 和 CAS 五个核心边界。
