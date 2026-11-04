# R5_29: Sydney Citywalk 40s real cloud experiment, API cost and external visual audit

Date: 2026-11-04. Frozen source commit: 6842bdb54ab371c6d8a14c8c0293f7e28d74c3b2
Model: Qwen3.8-Flash (Alibaba Model Studio); real, original V05 bundle with 161 source clips / 228 JPG frames.
Original input SHA256: e5bef3e11cb3dcedb7061445f2b460e9f9d32aaf130134dcc74446843a5928de

## Fair, unassisted cloud input

No user-provided route map, named-places ground truth or manually established 72-second opening boundary was fed to the generating model.
S04 reused 54 originally paid perception calls, each matched by original evidence frame IDs, model and provider.
The 108 later calls were real new API requests. No original MP4 was uploaded.

## API token usage and estimated incremental charge

New call attempts: 108; saved completed paid stages: 108; API failures: 0.
New input tokens: 1,870,709; new output tokens: 120,910.
New estimated native charge: CNY 1.823024; USD 0.253198.
Frozen receipt assumptions: input CNY 0.8 / million tokens; output CNY 2.7 / million tokens; CNY 7.2 / USD 1.
The amounts are calculated from Qwen StageRun token receipts and configured rates, not an official provider invoice. Actual billing may differ due to caching, tiering or exchange rates.

| Pipeline stage | New calls | Input tokens | Output tokens | Est. CNY | Est. USD |
|---|---:|---:|---:|---:|---:|
| S07_THEME_PLAN | 5 | 141,858 | 11,487 | 0.144501 | 0.020070 |
| S08_PLAN_REPAIR | 1 | 53,387 | 7,461 | 0.062854 | 0.008730 |
| S09_IMAGE | 43 | 857,693 | 78,671 | 0.898566 | 0.124801 |
| S11_WRITER | 2 | 47,509 | 2,526 | 0.044827 | 0.006226 |
| S12_FACT_REVIEW | 35 | 166,272 | 5,836 | 0.148775 | 0.020663 |
| S13_COPY_REPAIR | 8 | 67,998 | 2,746 | 0.061813 | 0.008585 |
| S14_COVERAGE | 4 | 515,228 | 10,354 | 0.440138 | 0.061130 |
| S15_FINAL_REVIEW | 1 | 3,596 | 321 | 0.003743 | 0.000520 |
| S16_FINAL | 7 | 14,077 | 1,443 | 0.015158 | 0.002105 |
| S17_FINAL | 2 | 3,091 | 65 | 0.002648 | 0.000368 |

### Previously paid visual-recognition calls (excluded from new spend)

Historical S04: 54 replays, prior estimated CNY 0.370924 / USD 0.051517. These were not billed again in this run.
New run + historically incurred S04 is illustratively USD 0.304715, but this is NOT a new bill or a reproducible cold-start quote.
Run safety controls: 150 new-call maximum, USD 0.45 estimated new-charge stop-loss, 180 combined model-stage attempts.

## Actual published Chapter results

R5_28 baseline: 5 chapters, 20 main gallery images, 0 highlights, delivery READY_WITH_ITEM_BLOCKS.
R5_29 current: 8 chapters, 32 main images, 1 highlight, delivery READY_WITH_ITEM_BLOCKS, coverage INCOMPLETE, production_ready=false.
Publication dispositions: {"INSUFFICIENT": 1, "VISIBLE": 33, "REDUNDANT": 124, "COPY_BLOCKED": 2, "NOT_SELECTED_VALUE": 1}.
The first map/overview asset V001 was independently marked INSUFFICIENT, without external route/intro annotation. This is not proof every opener will be detected.

| C | Published title | Real hero frame ID | Gallery | Highlights |
|---:|---|---|---:|---:|
| 1 | 环形码头与歌剧院水岸 | sydney_04_000089-f0 | 4 | 0 |
| 2 | 黄色石砌仓库与拱桥 | sydney_04_000365-f1 | 4 | 0 |
| 3 | 悉尼歌剧院与拱桥步道 | sydney_04_000413-f0 | 4 | 0 |
| 4 | 巴兰加鲁现代海滨 | sydney_04_000725-f0 | 4 | 0 |
| 5 | 达令港海事景观 | sydney_04_000773-f0 | 4 | 0 |
| 6 | 唐人街与圣玛丽大教堂 | sydney_04_001109-f0 | 4 | 0 |
| 7 | 拱廊内部中庭俯瞰 | sydney_04_001217-f0 | 4 | 0 |
| 8 | 湖边长椅休憩 | sydney_04_001781-f0 | 4 | 1 |

## ChatGPT external editorial quality assessment (not an in-cloud Judge)

The 40-second R5_29 output has improved its Opera House hero: frame 000089-f0 is clearly recognizable and better than the previous 000137-f0 harbor-bridge-focused cover.
The story and image evidence, however, remain over-fragmented into 8 chapters. The Rocks market and historical warehouse could form a stronger common experience; harbor-bridge walking, Barangaroo waterfront and Darling Harbour are overly split relative to their actual memorable topics.
The Darling Harbour chapter still includes frame 000953-f0 of a Chinatown ceremonial gate, a directly visible cross-chapter media error.
The final garden chapter still includes a late Opera House view from frame 001925-f1. Same landmark in a later segment can be merged with the opening harbor Chapter; it does not belong in a garden-focused memory just because it occurs later.
Chinatown/Cathedral and CBD/Strand Arcade chapters are fragmented or locally focused. One chapter is named after benches and a lake rather than narrating the broader Hyde Park and Botanic Gardens visit.
These failures mean an increase from 5 to 8 final chapters does NOT establish a quality gain. R5_29 does not yet match the human editor. A separate single-LLM editorial judgement should not be treated as a statistical accuracy metric.

## Coverage versus production acceptance

The final S14 ledger has no UNREVIEWED items, improving on the old R5_28 141 UNREVIEWED items.
However, at least 2 COPY_BLOCKED and 1 INSUFFICIENT remain; publication_coverage_review_complete is false and final delivery is READY_WITH_ITEM_BLOCKS / INCOMPLETE. Do not merge this experiment to production.
The export contract for production v1 still has a 5-chapter maximum, so this 8-chapter preview is not an accepted production deliverable.

## Local audit sources (kept on Mac, not GitHub)

Run directory: /Users/youtang/Documents/Nexleap/work_logs/evidence/sydney-offset-sweep-r525-20261103/offset_040/runs/r529_unassisted_40_full_20261104
Immutable input_attestation.json, status.json, result.json, attempts/stage_*.json and calls.jsonl.
Calculated costs: r529_api_cost_audit.json and r529_api_stage_costs.csv.
Final media evidence: r529_vs_r528_true_published_diff.json, r529_vs_r528_published_photos_contact.jpg.
Interactive browser view: r529_vs_r528_published_chapters.html.
Do not upload private JPGs, raw source MP4, keys, provider request payloads or unredacted responses to GitHub.
