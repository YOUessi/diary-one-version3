# Diary One Canonical Checkpoint V1.25 — Production-shaped Pipeline V1.0

**状态：** FULL-FLOW CONTRACT FROZEN / LOCAL REFERENCE RUNNABLE / CLOUD PRODUCTION NOT YET DEPLOYED
**冻结日期：** 2026-08-29
**覆盖范围：** S00–S13 全流程合同、阶段交接、两阶段发布编排、本地可运行 reference
**权威继承：** V1.1–V1.24；冲突时以阶段最新 Canonical Checkpoint 为准
**明确排除：** Firmware/SDK、正式 App、共享状态文件、真实云部署、隐私/伦理/治理专项

## 1. V1.0 产品目标

对高强度参考日：

```text
150 Auto 9s Video
+ 20 Manual Photo
+ 10 Manual 15s Video
+ 3 Manual 60s Video
+ 3 Manual 120s Video
= 186 RawAsset / 34 分钟视频
```

输出目标：

```text
丰富日主要 3–4 Chapter，第 5 个为严格例外
每个 Chapter Standard 3–5 个精选素材
严格 Compact Gate 通过时允许 2 个素材
0–3 Aha；丰富日希望 2–3，但不是配额
证据不足允许更少、HIGHLIGHT_DAY 或 EMPTY_DAY
```

质量优先级始终是：

```text
False Memory / False Merge / Unsupported Claim
>
Missing Memory / 轻微切碎 / 错过一个不确定瞬间
```

## 2. 冻结的全流程

| Stage | 只回答一个问题 | 核心输出 | 最新冻结检查点 |
|---|---|---|---|
| S00 | 处理哪一天、哪一版 | immutable Run/Snapshot/Revision | V1.1 |
| S01 | 输入事实是什么 | RawAsset Ledger | V1.2 |
| S02 | 如何形成最小 Evidence | Windows/Frames + 1-or-3 route | V1.3/V1.4/V1.6/V1.8 |
| S03 | Window 自身与相邻变化信号 | Intrinsic/Edge Signal | V1.5/V1.9 |
| S04 | 当前 Window 看到了什么 | Observation Lite | V1.7/V1.10 |
| S05 | 全天怎样连续分段 | Moment + 双向边界账本 | V1.11–V1.15 |
| S06 | Observation 在 Memory 中扮演什么角色 | KEEP/CONTEXT_ONLY/DROP | V1.16 |
| S07 | 哪些局部假设值得候选 | Chapter/Aha Candidate | V1.17 |
| S08 | 哪个关键未知项值得补证 | ValidatedCandidate | V1.18 |
| S09 | 全日选哪一组 Memory | SelectedMemorySet/Day State | V1.19 |
| S10 | 每个 Memory 用哪些最终媒体 | Beat/Anchor/Media/HQ manifest | V1.20/V1.21 |
| S11 | 如何只依据证据写字和建立索引 | Claim/Narrative/Tags/Entities | V1.22 |
| S12 | 当前 exact Revision 能否进入物化/发布 | S12A/S12B decisions | V1.23 |
| S13 | 如何只处理 selected HQ 并原子导出 | receipts/export/commit | V1.24 |

模型不是总控 Agent。Workflow 由确定性状态机驱动，VLM/Writer 只在明确阶段和有界输入上工作。

## 3. 实际运行顺序

```text
SYNC / INCREMENTAL PREP
  S00 → S01 → S02 → S03
  → persistent background evidence queue

ROLLING PREVIEW OR FINAL
  S04 → S05 → S06 → S07 → S08 → S09
  → S10 A/B/C/D media projection + HQ manifest
  → S11 facts/claims/narrative/index
  → S12A pre-materialization validation
  → S13A selected HQ materialization
  → activation delta?
       yes: affected S11 revalidation
       no: continue
  → S12B activation/export validation
  → S13B export + publisher CAS
```

讨论章节编号不改变这条生产顺序。

## 4. 三类运行时机

### 4.1 每次 Sync

- 只对新增 RawAsset 做 intake、Evidence plan、便宜信号和上传路由；
- 用户只执行一次 Sync；后续上传必须无感，不新增交互；
- Phone 对 Auto 固定抽三帧，Cloud 只接收保守 1-or-3；
- Cloud 一帧不足时直接把该 Auto 排除候选，不请求另外两帧；
- Manual 素材即使在 Memory 中被相似抑制，仍保留 Manual 窗口与事实账本。

### 4.2 Rolling Preview

- 约 1.5 小时新增有效 coverage 后 eligible；
- 约 2 小时默认尝试；
- strong Manual、semantic delta 或用户主动生成可提前；
- 触发不保证新增 Memory；无足够增量返回 NO_CHANGE；
- 中间结果采用累加体验，但通过 enrich/merge/replace/revision 控制全天质量，不机械累加数量。

### 4.3 Finalization

- 冻结 immutable full-day snapshot；
- 复用 exact-cache 的 Observation/validation，不重复收费理解；
- 从 cached Observation 重新形成全日 Moment 与 final selection；
- late data 创建新 Revision，不修改正在 Finalize 的快照。

## 5. 不可跨越的阶段权限

1. S04 不能借相邻素材给当前 Window 补事实。
2. S05 只能形成连续 Moment；A–B–C 的 resumed mainline 由 S07 表达，不跨 B 聚类成一个 Moment。
3. S06 role 不改变 Observation/Moment。
4. S07 Candidate 不等于最终 Memory。
5. S08 只回答 one-question，不重做全天理解。
6. S09 只选 set，不做媒体美感或写文案。
7. S10 只在 selected Memory 内选媒体，不让漂亮图反向创造 Chapter。
8. S11 只写 approved Claims，不改变 membership/media。
9. S12 只读验证，不静默删除/修理。
10. S13 只 materialize predeclared routes，不改变事实或 selection。

## 6. 核心数据血缘

```text
RawAsset
→ EvidenceWindow / EvidenceFrame
→ WindowIntrinsicSignal / TimelineEdgeSignal
→ ObservationLite
→ Moment + ContinuityEvidenceLedger + BoundaryEvidenceLedger
→ ObservationRole
→ Candidate + CandidateContentUnit
→ ValidationTask / ValidatedCandidate
→ SelectionRecord / SelectedMemorySet
→ ContentBeat / EvidenceAnchor / MediaDecision
→ ChapterFacts / AhaFacts / ClaimLedger
→ GroundedNarrative / CanonicalTagDecision / EntityIndexLink
→ S12A Decision
→ MaterializationReceipt / ActivationDelta
→ S12B Decision
→ UserDiaryExport / InternalAuditRun / PublicationCommitRecord
```

每个箭头必须保存 current immutable refs 和 fingerprint；不得只靠数组位置或自然语言猜 lineage。

## 7. Day State 与数量

```text
CHAPTER_DAY   → 1–5 Chapter + 0–3 Aha
HIGHLIGHT_DAY → 0 Chapter + exactly 1 standalone Aha
EMPTY_DAY     → 0 Chapter + 0 Aha
```

- 3–4 Chapter 是丰富日目标，不是必须凑齐；
- 第 5 Chapter 需要 S09 exceptional increment gate；
- Aha 不因目标 2–3 而降低单峰、独立性或媒体门；
- operational failure、模型故障、HQ 等待或预算不足不能伪装 EMPTY_DAY。

## 8. Chapter 与 Aha 的最终形态

### Chapter

- Title：中文当前测试 2–10，可解释软延伸 11–12；
- Story：默认一句，最多两句；直接呈现经历，不解释“主要画面”；
- Time Label：确定性生成；
- Media：Standard 3–5，strict Compact 2；
- Hero：恰好一个，来自正文集合；
- Canonical Assignment：0–4，每 Facet 至多一项；
- Display Label Candidate：0–2，App 可不展示。

### Aha

- 无 generated Title/Story；
- 一条 ≤20 中文可见字符的 Moment Line；
- 只有一个 peak 与恰好一个可见媒体；
- 可以嵌在 Chapter 时间线，但故事职责必须不同；
- same-story climax 不共选；
- support/context 只帮助理解，不变成第二个可见媒体或第二个事件。

## 9. Cost Architecture

高成本逐级收缩：

```text
186 RawAssets
→ 220 frozen-mode logical Evidence Windows
→ Phone 570 extracted positions, Cloud Auto 1-or-3
→ cached Window-local Observations
→ bounded Moments/Candidates
→ S08 frontier <= 8, necessary tasks <= 16
→ <= 5 Chapter + <= 3 Aha
→ <= 28 visible body/Aha consumers
→ selected HQ only
```

成本控制机制：

- exact fingerprint cache；
- cheap signal 先行、昂贵 perception 后置；
- S08 one-question validation 与 VBU/day budget；
- S09 deterministic bounded solver；
- S10 metadata fallback 不预取 dormant HQ；
- S11 Tag/Time/validator 默认零模型调用；
- Writer 每 Memory 有界 logical attempts；
- S12 两阶段均为 metadata validator；
- S13 request coalescing 与 shared materialization。

真实美元、流量、电量、P50/P95/P99 只能由真实素材 benchmark 得出。

## 10. 本地参考 Pipeline

### 10.1 能证明什么

本地 reference：

- 校验 S00–S10 current Revision handoff；
- 执行 S11 Claim/surface、中文长度、light-affect、closed tag registry 与 typed entity gates；
- 执行 S12A Day State、数量、pair、media、HQ manifest 与 reuse gates；
- 执行 S13 predeclared route success/terminal/transient 模拟；
- Fallback activation 后执行 affected S11/S12 revalidation；
- 生成 S11、S12A、S13A、S12B、User Export、Internal Audit 与 run manifest；
- 对所有文件使用 deterministic fingerprint 和原子 JSON 写入。

### 10.2 明确不证明什么

- 不执行真实 S04 VLM、S05–S10完整算法；S00–S10 是 contract adapter validation；
- 不读取或上传 Raw/HQ bytes；
- 不执行真实 PHOTO/LIVE/VIDEO 解码编码；
- 不调用真实 Writer/provider；
- 不连接 App/Firmware/SDK；
- 不执行真实数据库事务、published-head CAS 或云部署；
- 不证明模型准确率、成本或时延。

run manifest 必须保留：

```text
REFERENCE_VALIDATED_NOT_CLOUD_PRODUCTION
NO_CLOUD_DEPLOYMENT
NO_REAL_MODEL_INFERENCE
NO_HQ_MEDIA_BYTES_RENDERED
NO_APP_OR_FIRMWARE_INTEGRATION
NO_PRODUCTION_CAS_OR_PUBLISHED_HEAD_MUTATION
```

### 10.3 运行方式

从仓库根目录：

```bash
PYTHONPATH=src python3 -m diary_one_ci.cli production-v1 validate \
  fixtures/production_v1/ancient_town_reference_day.json

PYTHONPATH=src python3 -m diary_one_ci.cli production-v1 run \
  fixtures/production_v1/ancient_town_reference_day.json \
  --artifacts artifacts
```

默认使用 `contracts/canonical_concept_registry_v1.json`。

正式 JSON 边界为 `contracts/production_pipeline_v1.schema.json`（输入）与 `contracts/production_pipeline_v1.outputs.schema.json`（S11/S12/S13/User Export/Audit/Run Manifest 输出 union）。

## 11. Reference Artifacts

```text
s11_narrative_bundle.json
s12_pre_materialization_decision.json
s13_materialization_bundle.json
s12_activation_decision.json       # HOLD 时不存在
user_diary_export.json              # HOLD 时不存在
internal_audit_run.json             # HOLD 时不存在
run_manifest.json
```

reference receipt 明确标记 `media_bytes_materialized=false`，不能被下游误当成真实媒体 URL。

## 12. 验证矩阵

当前自动化测试覆盖：

- 高强度日 186 RawAsset、220 frozen-mode Window、570 Phone frame positions；
- 16 秒/73 秒任意 Manual 时长不会被实现偷定；
- S00–S10 Revision mismatch；
- Claim 无 Evidence、weak/unsupported surface；
- actual-text span 全覆盖、surface Claim 对齐与窄语气许可；
- Writer provider/model/prompt/token/cache/cost provenance；
- unregistered free Tag、同 Facet 多项、零 Tag 合法；
- exact PlaceEntity 不污染 Canonical concepts；
- light-affect permission 与 unsupported affective wording；
- Day State/数量/Compact/Aha single-media；
- Chapter×Aha independence decision coverage；
- HQ request/route/Anchor/scope；
- Aha PHOTO/LIVE 格式边界与 dormant Fallback 格式；
- cross-Memory reuse 预声明和 activated exact-render 校验；
- Primary terminal→Fallback activation→affected revalidation；
- transient failure→HOLD 且不导出；
- 全日 media_id 唯一性；
- deterministic rerun 与 schema/registry validity；
- User Export 只投影用户可见叙事，不泄露 Claim/span/Evidence 内部字段；
- 原有 bundle/evaluator/E00/X01 测试不回归。

## 13. 贯穿案例

```text
09:00–09:46  古镇入口、石板路、传统建筑、河岸
09:48–09:58  现代茶饮店短插曲，猫碰倒纸杯
10:00–10:30  回到古镇主线
```

合法结果：

- Chapter：古镇漫步；3–4 个不同意义的建筑/河岸媒体；Story 点明街巷与河边，不解释“主要画面”。
- Aha：猫碰倒纸杯；单一 peak/单媒体；“调皮”只有窄许可并绑定真实动作。
- Chapter Tags：CITY_WALK/HISTORIC_DISTRICT/ARCHITECTURE/TRAVEL_OUTING。
- Aha Tags：CAT/CAFE；不继承 Chapter 的旅行 Tag。
- 周庄：PlaceEntity，不作为全球共享 Tag。
- 一个 LIVE route terminal 时激活同 Anchor PHOTO，随后重验 S11/S12，再形成 reference export。

## 14. Production Readiness Gates

要从本地 reference 进入真实云端 Production，至少还需：

1. 真实 S00–S10 stage services/schema adapters；
2. 真实 VLM/Writer provider gateway、structured output 和 cost budget；
3. 真实 HQ source resolver、renderer、object store 与 checksum benchmark；
4. 数据库 immutable ledger、queue、idempotency、CAS 与 recovery；
5. App 无感上传/网络/电量/destination 合同；
6. 真实用户素材标注、质量评分、false-memory/merge/recall eval；
7. 中文 D2e Title failure 用户测试；
8. English/target-locale 独立合同与 release gate；
9. privacy、security、retention、deletion、ethics/governance；
10. load、failure injection、P50/P95/P99 成本/时延/SLO。

这些不是 V1.0 full-flow contract 的缺失，而是从“架构与本地 reference 完成”到“真实 Production 上线”的明确工程/验证门。

## 15. Frozen vs Open

### FROZEN

- S00–S13 阶段职责、顺序、对象演进与权限；
- Rolling Preview/Final 的 Revision 原则；
- Day State/数量/Chapter/Aha 形态；
- S11–S13 两阶段 materialization/revalidation/publish 编排；
- deterministic local reference contract、artifacts 与非声明边界；
- 全链路 cost-accounting categories 与 validation gates。

### OPEN

- 任意时长 Manual Video Window 数量/位置；
- App background upload 与 storage/API/Agent topology；
- 真实模型、阈值、codec、render、数据库、队列和云配置；
- 真实成本、时延、成功率、用户评分；
- D2e、海外 locale、privacy/ethics/governance。

## 16. Freeze Record

Diary One 的 S00–S13 V1.0 全流程逻辑与 S11–S13 control-plane reference 至此形成一个可运行、可验证、可版本化的基线。后续工作从真实数据验证、阈值校准和 Production engineering 开始，不重新发明全局流程；发现反例时通过新的 Canonical Checkpoint 精确修订对应 stage。
