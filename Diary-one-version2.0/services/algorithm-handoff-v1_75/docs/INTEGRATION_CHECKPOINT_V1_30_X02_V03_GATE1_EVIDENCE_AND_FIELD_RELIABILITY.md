# Integration Checkpoint V1.30 — X02 V03 Gate 1 Evidence and Field Reliability

Status: GATE 1 IMPLEMENTED AND VERIFIED ON PERSON 1; REAL OUTPUT QUALITY NOT ACCEPTED; NOT PRODUCTION

Date: 2026-09-02

Supersedes: the `GATE 1 IMPLEMENTATION PENDING` status in V1.29 only. V1.29 remains the frozen product and evaluation-method authority. V1.30 does not declare Gate 2, Gate 3, Gate 4, S13, App integration, or Production complete.

## 1. Baseline and scope

- Algorithm repository: `nexleap-tech/nexleap-diary-one`.
- Algorithm branch: `codex/validation-v01-v02-20260829`.
- Algorithm parent commit: `4e0d581b190bcb44420394465b5f59c739af5bad`.
- Web local repository parent commit: `690eedbe002240c09a5fafb4bf0f2d04608e555b`.
- Evaluation input: read-only Person 1 folder `OWNER_CONTROLLED_TEST_PACK_1/`.
- Algorithm/Web identity: `X02_STAGED_REAL_MEDIA_PREVIEW_V03`.
- Input identity: `DIARY_ONE_APP_LIBRARY_BUNDLE_V02`.
- Run mode: `FRESH_FULL_RUN`; `cross_run_semantic_cache_used = false`.

This checkpoint changes only the Algorithm repository and its local Web research-preview client. It does not change Firmware/SDK, background Sync, cloud deployment, shared project-state files, the source media folders, or S13 HQ export.

## 2. Gate 1 implementation

### 2.1 Additive Web/Algorithm handshake

V03 has dedicated preview and sidecar paths:

- `/x02/v0.3/preview`;
- `/x02/v0.3/run-sidecar`.

The Web refuses an older staged-preview response and verifies the fresh-run/cache flags, duration-aware Evidence capability, field-level degradation capability, bundle version, and audit capability before running.

### 2.2 Test-only duration-aware Evidence profile

`PHONE_TEST_DURATION_WINDOWS_V01` uses actual phone-library video duration:

| Input | Logical Windows | Evidence frames |
|---|---:|---:|
| Photo | 1 | 1 |
| Video `<= 10s` | 1 | 3 |
| Video `> 10s` and `<= 30s` | 2 | 4 |
| Video `> 30s` and `<= 90s` | 4 | 8 |
| Video `> 90s` | 6 | 12 |

Every video frame records its Window index/count, sample role, and actual source timestamp. This research profile does not supersede the frozen Auto 9-second three-frame phone contract or define the future App capture-mode mapping.

### 2.3 Field-level Observation degradation

S04 no longer discards an entire otherwise grounded Observation because one non-critical field is outside its contract.

- Invalid facts are dropped individually; if no valid fact survives, the item becomes `INSUFFICIENT_EVIDENCE`.
- Invalid setting/activity/Episode fields become their audited unknown value; no replacement fact is inferred.
- Invalid subject-list entries are dropped individually while valid entries remain.
- Invalid event fields become `NONE/NONE`.
- Invalid quality becomes the conservative configured value.
- Any surviving degraded Observation becomes `PARTIAL`.
- Missing, duplicate, or provider/engineering responses remain failures and are not relabeled as weak visual evidence.

Each degradation records JSON field path, rule ID, action, and a redacted sentinel. The audit stores a candidate hash rather than the rejected free-form value.

### 2.4 Auditable downstream run

V03 additionally records:

- every currently implemented stage status through S12;
- explicit `S13_HQ_EXPORT = NOT_EXECUTED`;
- event-path and discovery-path Aha candidate counts and search outcome;
- per-stage latency, model calls, frames, Tokens, and configured API cost estimate;
- Web-side Evidence preparation and full user-wait time;
- the degraded Observation ledger separately from failed/insufficient ledgers.

These additions make downstream quality loss diagnosable. They do not by themselves fix Chapter Storyline or Aha ranking.

## 3. Automated verification

| Surface | Result |
|---|---|
| Algorithm full test suite | 122 passed, 1 skipped |
| Skipped test | local socket integration only; the sandbox disables that socket path |
| Web production build and rendered-contract tests | passed |
| Web lint | passed |
| Diff whitespace check | passed |

The socket behavior was then exercised by the Person 1 browser-to-local-server full run below, so the skipped unit-test environment does not mean the live path was untested.

## 4. Person 1 formal full-run evidence

### 4.1 Run identity

- Session ID: `47ea72c1-065d-45fa-b790-1798365dfcdc`.
- Run ID: `ef740ce9-eb7b-4038-9f06-17fe69bf2d4c`.
- Completed: 2026-09-02 01:03:12 China Standard Time.
- Local run audit: `var/x02_runs/47ea72c1-065d-45fa-b790-1798365dfcdc/run_audit.json`.
- Run-audit SHA-256: `aa911f3d53ceb4af97223624806aacc192346ea23374851f600dd813f5bba20f`.
- Client-trace SHA-256: `f76033bf2f276fd46b8f2d9e1498a55795c9e175ae67ac969303a9245a5710f6`.
- Model: Alibaba Model Studio `qwen3-vl-flash-2026-01-22`.
- Original media uploaded to the model: `0`.
- Image payloads retained in the audit: `false`.

The source folder remains unmodified and untracked. Generated Evidence and audits remain local under ignored `var/` storage and are not included in Git.

### 4.2 Input and Observation result

| Metric | Result |
|---|---:|
| Videos | 20 |
| Original duration | 298.697 seconds |
| Original bytes | 42,238,190 |
| Evidence frames | 74 |
| Evidence bytes sent to the local service/model path | 9,022,849 |
| Usable Observations | 20 |
| Fully observed | 17 |
| Field-degraded but fact-preserved | 3 |
| Insufficient evidence | 0 |
| Failed whole items | 0 |

The three `PARTIAL` items each contained one or two subject codes outside the closed vocabulary. V03 dropped only those invalid list entries and preserved their grounded rain/transit, forest-path, and in-car facts. The V01 failure pattern of losing four whole items did not recur.

This is the Gate 1 acceptance result: every asset reached exactly one usable terminal Observation state, valid facts survived non-critical field errors, and degradation remained explicit.

### 4.3 Stage, time, Token, and cost evidence

| Stage | Time | Model calls | Input Tokens | Output Tokens | Estimated API cost |
|---|---:|---:|---:|---:|---:|
| Web Evidence preparation | 115.203 s | 0 | 0 | 0 | $0 |
| Local multipart materialization | 0.109 s | 0 | 0 | 0 | $0 |
| S00-S02 bundle load | 0.013 s | 0 | 0 | 0 | $0 |
| S04 perception, 4 batches | 117.054 s | 4 | 84,424 | 8,430 | $0.00351509 |
| S04 deterministic validation | 0.006 s | 0 | 0 | 0 | $0 |
| S05-S07 structure proposal | 31.039 s | 1 | 13,071 | 2,563 | $0.00080627 |
| S03-S10 deterministic structure/selection/media | 0.002 s | 0 | 0 | 0 | $0 |
| S11 Writer, 2 attempts | 21.034 s | 2 | 13,419 | 1,798 | $0.00065414 |
| S11-S12 deterministic validation | 0.002 s | 0 | 0 | 0 | $0 |
| **Service-side X02 total** | **169.216 s** | **7** | **110,914** | **12,791** | **$0.00497550** |
| **User-visible end-to-end total** | **284.582 s** | — | — | — | — |

The cost is the configured Alibaba API estimate only. It excludes server, network, storage, observability, and future HQ/Production work.

Compared with the prior Person 1 V01 run:

- frames increased from 60 to 74;
- usable Observations increased from 16 to 20;
- whole-item failures decreased from 4 to 0;
- user-visible time decreased from 318.779 s to 284.582 s;
- API estimate decreased from $0.00541056 to $0.00497550.

The time and price change must not be treated as a stable optimization result: model latency and generated output length varied between two calls. One reliable engineering finding is that browser Evidence generation is still serial and consumed 115.203 seconds, or about 40% of this run's user wait. Production performance is not accepted.

## 5. Visible result and quality diagnosis

The run published two Chapters and one Aha. This is materially more diagnosable than the earlier zero-Aha result, but it is not a usable quality result.

### 5.1 Chapter 1 — local market thread

- Candidate assets: items 1, 6, 7, 12, and 18.
- Final media: all five candidate assets.
- Title: `市场入口与摊位`.
- Story length: 138 visible characters.

The vendor, vegetables, food stall, and fruit material is substantially coherent. Item 1 is a gateway/street entrance that was classified as `MARKET_VISIT`; it is defensible as an entrance beat but should be reviewed rather than assumed correct. The Writer emitted a semicolon-separated fact inventory instead of the frozen natural one-to-two-sentence memory expression. It passed the sentence hard gate and recorded `CHAPTER_STORY_OVER_PREVIEW_WRITING_TARGET`; the previously rejected unapproved 48-character hard deletion gate was not reintroduced.

### 5.2 Chapter 2 — over-broad historic-town thread

- Candidate assets: items 3, 4, 5, 8, 10, 11, 13, 14, 16, and 19.
- Final media: items 3, 8, 11, 13, and 19.
- Title: `古村石巷与水道`.
- Story length: 114 visible characters.

The candidate merges at least two plausible Storyline duties:

1. cultural/architectural discoveries — prayer plaques, historic gates, a temple sign, and the `古越龍山` marker;
2. strolling/scenic experience — stone lanes, canal, bridge, willow, and waterside path.

The deterministic candidate generator had already produced smaller contiguous historic-town groups, but S08-S09 selected the broad ten-item model proposal because the objective rewards asset coverage, Episode diversity, and quality sum; it has no explicit Storyline-purity or subtheme-diversity term. This is the concrete Gate 2 failure. The algorithm should next form Chapter Storylines below the shared `HISTORIC_TOWN_WALK` Episode instead of treating the common Episode code as enough coherence.

The two published Chapters do not share assets, but their displayed ranges overlap (`第1–18项` and `第3–19项`) because the market and historic-town threads interleave. The future product contract must distinguish a thematic Storyline range from a contiguous time range; V1.30 does not decide that UX question.

### 5.3 Missing third plausible thread

Nature-path items 9 and 15 did not form a Chapter because the current Chapter candidate gate requires at least three content units. They might belong to a broader `古镇漫步` Storyline together with selected lane/waterside assets, but that requires Gate 2 Storyline logic rather than lowering the three-item Chapter rule or padding a Chapter.

### 5.4 Aha quality and loss

S07 found ten eligible grounded Aha candidates: three event-path and seven discovery-path candidates. S08-S09 selected the first three eligible items in source order: items 3, 4, and 6. Later item 17 had `PLAYFUL_ANIMAL/HIGH` and item 12 had `FOOD_MOMENT/MEDIUM`, but both were excluded only because preview capacity had already been reached. This is an ordering bias, not an editorial quality comparison.

Only item 3 survived Writer:

- published Aha: `祈福牌架`;
- Moment Line: `视频中首先展示挂满红色祈福牌的木架结构。` (20 visible characters);
- item 4 failed at 21 characters in both attempts;
- item 6 failed at 22 and then 28 characters.

The published prayer-plaque detail is also selected inside Chapter 2 and uses the same source asset. The Web correctly marks this pair `REVIEW`, because reuse is legal only when Chapter and Aha perform different story duties. In this result the Aha reads as an ordinary detail already central to the Chapter rather than a clearly independent small story. It is not accepted as a good Aha.

This exposes three Gate 3 tasks:

1. rank the complete eligible Aha set for surprise, independence, specificity, and quality instead of taking the first three;
2. enforce/audit Chapter-Aha story-duty independence before final selection;
3. make bounded Writer retry actually respond to the measured 20-character failure without semantic truncation.

### 5.5 Tag and expression gaps

- Chapter 1 retained only `CENTRAL_SUBJECT.FOOD_OR_DESSERT`; its market setting/activity coverage is incomplete.
- Both Chapter bodies are grounded but read like model observation summaries, not natural memory copy.
- The one Aha is factually grounded but emotionally flat and not sufficiently distinctive.

These are real-model quality failures. They are not Gate 1 contract failures and must not be hidden by changing the success label.

## 6. Gate status after this checkpoint

| Gate | Status | Evidence |
|---|---|---|
| Gate 1 — Evidence and S04 reliability | **IMPLEMENTED / PERSON 1 TECHNICAL ACCEPTANCE PASSED** | 20 usable terminal Observations, 3 explicit field degradations, 0 whole-item failures |
| Gate 2 — Chapter Storyline segmentation | **OPEN / REAL FAILURE CONFIRMED** | broad historic-town candidate merges culture and stroll/scenery; coverage-biased selection |
| Gate 3 — dual-path Aha retrieval and independence | **PARTIAL INSTRUMENTATION / REAL FAILURE CONFIRMED** | both paths searched, but ordering bias, Writer loss, and embedded non-distinct Aha remain |
| Gate 4 — three-person evaluation | **NOT STARTED** | people 2 and 3 have not been run under V03 |
| S13 HQ export | **NOT EXECUTED** | outside staged Web Preview |
| Production readiness | **FALSE** | no Production service, App Sync, HQ path, three-person acceptance, or performance acceptance |

## 7. Versioned implementation hashes

### Algorithm

| Artifact | SHA-256 |
|---|---|
| `docs/CANONICAL_CHECKPOINT_V1_29_REAL_MEDIA_QUALITY_RECOVERY.md` | `4ed629288d7b23a6038be3166b9463119e9994b9d4c049a6c1011cbafe447e36` |
| `contracts/app_library_bundle_v02.schema.json` | `2bf249bec61ad054bc1b830ec0f2168a391bbf5336c8aed22afe174cce5ee6b1` |
| `contracts/x02_staged_preview_v03.schema.json` | `1fa81a3047b88431222b1bbb7503d46226b271b03b0805532be9158d24df3703` |
| `src/diary_one_ci/contracts/x02_field_degradation_v01.json` | `29d8aca5e9a2dfaf70bbaae6e6d96a2e6ceb27a20416f0a1de91b2035fa6e6fa` |
| `src/diary_one_ci/bundle.py` | `15155fb287948682551095d6b387256a068c103517fda7619f4c50641ed75572` |
| `src/diary_one_ci/x02.py` | `f2cdd564152ea6d48ab0daa88056d4426effa9fe0fa1462eb33e45078afefaa1` |
| `src/diary_one_ci/x01_server.py` | `6fb3d48cc7ef395f49b54b78087f5bcae6eb34afc1ad0b170d3154d56e1ba47a` |
| `tests/test_x02.py` | `7ff122de9c2068e1132c64213358b8af611490d59ed02c1f577fe7f551d62778` |
| `tests/test_x01.py` | `a23e5ab94be813aaf1dd15d8b2c538b6bc00f6fdf60530b0bfb491992864956e` |

### Web research client

| Artifact | SHA-256 |
|---|---|
| `README.md` | `f99cd4968c3ff178bef3019271a2c8b3f97f12ee537982244776139ad97bbec0` |
| `app/lib/contracts.ts` | `7899487beab3c34137d25bccc4dfa642e3ee89ae8c5b9ec9922c1d63e149de88` |
| `app/lib/media-evidence.ts` | `51e9f6538a742b72326ca93fcf480d9fe6d7bed249a8513eb4cd8d8c4315eee6` |
| `app/page.tsx` | `676688c81b106959d5b9fb483818a60ae74a7de9168aeb49539d1d9390cce803` |
| `tests/rendered-html.test.mjs` | `c6fedbc707da06a3d635d7756f845188b7c0b481a68c4e669707e90647681696` |

The Web repository has no configured Git remote at this checkpoint. Its commit can be recorded locally, but no remote destination is inferred.

## 8. Rollback and next work

Algorithm rollback is the parent commit `4e0d581b190bcb44420394465b5f59c739af5bad`. Web rollback is `690eedbe002240c09a5fafb4bf0f2d04608e555b`. Historical local run audits are append-only evidence and are not rewritten by rollback.

The next implementation unit is Gate 2, not a model swap or a numeric Chapter quota. It should introduce Chapter Storyline identity and purity below Day Episode, rerun Person 1 from raw media through the full chain, and then reassess Aha ranking/independence under Gate 3. No threshold learned from Person 1 alone may be declared universal before the three independent packs are evaluated.
