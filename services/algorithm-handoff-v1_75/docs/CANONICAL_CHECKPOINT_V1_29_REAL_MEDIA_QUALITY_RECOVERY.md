# Canonical Checkpoint V1.29 — Real-media Quality Recovery

Status: PRODUCT AND EVALUATION METHOD FROZEN; GATE 1 IMPLEMENTATION PENDING; NOT PRODUCTION

Date: 2026-09-02

Supersedes: no accepted historical evidence. This checkpoint adds the quality-recovery method for new real-media evaluations after V1.28. V1.28 remains the immutable record of the V02 semantic-contract implementation.

## 1. Outcome and position in the pipeline

The immediate objective is not to tune a final score. It is to make one raw test day travel through every currently implemented stage with enough grounded evidence to diagnose exactly where useful Chapters or Aha Moments were lost.

This work sits between the existing X02 staged-preview implementation and later Production acceptance. It may change Algorithm and Web research-preview contracts. It does not change Firmware/SDK, background App Sync, cloud deployment, shared project-state files, S13 HQ export, or any recorded V01/V02 run.

## 2. Formal evaluation run contract

Every formal real-media acceptance run must be a fresh full run:

```text
raw local media
  -> browser inspection
  -> fresh Evidence generation
  -> fresh bundle materialization
  -> S00-S02 intake
  -> S04 perception
  -> every currently implemented structure, selection, media and Writer stage
  -> S12 validation
  -> explicit S13 NOT_EXECUTED result
```

The result and audit must state:

- `evaluation_run_mode = FRESH_FULL_RUN`;
- `cross_run_semantic_cache_used = false`;
- which stages completed, degraded, failed, or were intentionally not executed;
- exact per-stage time, model calls, frames, Tokens, and configured cost estimate.

Unit tests, fixtures, stage replays, and deterministic debugging runs remain allowed. They are engineering evidence only and cannot be presented as a formal full-run quality result. The Production exact-cache principle remains inherited; this evaluation rule does not delete or redefine it.

## 3. Authorized test packs

The following local folders are authorized as three separate people/test days:

- `OWNER_CONTROLLED_TEST_PACK_1/`;
- `OWNER_CONTROLLED_TEST_PACK_2/`;
- `OWNER_CONTROLLED_TEST_PACK_3/`.

Rules:

- read-only source material;
- never rename, move, rewrite, delete, or add these files to Git;
- never mix top-level people into one test day;
- generated Evidence and run audits remain local and untracked;
- phone-library ordering is synthetic chronology when capture time is ignored.

Person 1 is the first Gate 1 acceptance pack. It is the high-density ancient-town travel day previously observed to lose useful street material, mix incompatible story duties, and return no Aha.

## 4. Chapter hierarchy

Chapter grouping uses three different semantic levels:

1. **Day Episode** — the broad day context, such as one ancient-town trip.
2. **Chapter Storyline** — one coherent thread inside that day, such as strolling through natural lanes, exploring architecture and cultural details, or discovering local vendors and street life.
3. **Content Beat** — one concrete photo/video contribution inside the Storyline.

Sharing one Day Episode is evidence for continuity, not proof that all content belongs in one Chapter. A high-density travel day should normally yield two or three Chapters when the evidence supports distinct Storylines. The implementation must generalize through activity thread, focal subject/theme, setting subzone, time continuity, and interruption/resume evidence; ancient-town labels are examples, never hard-coded output rules.

Story purity and narrative independence outrank raw asset coverage. A Chapter may contain three to five final selected media, while its candidate membership may be larger. The algorithm must not pad every Chapter to five.

## 5. Aha search contract

Every test day must actively search both Aha paths:

1. **Event Aha** — a grounded local action, interaction, reaction, result, ceremony, visible change, playful-animal action, or food interaction.
2. **Discovery Aha** — a concrete, distinctive, independently memorable visual discovery, including a local market detail, architectural motif, rain-lit street, animal detail, food detail, or other small life discovery. It must be more specific than generic attractive scenery.

A Manual Photo may support a Discovery Aha. Manual capture is a prior for human attention, not automatic acceptance. An Aha may lie inside a Chapter timeline only when it performs a different story duty; a Chapter climax cannot be duplicated as a second Aha.

Evaluation targets are one or two Ahas for an ordinary usable day and two or three for a rich day. These are search and quality targets, not fabrication quotas. Zero is valid only when the audit records that both paths were searched and no grounded independent candidate survived, using an explicit reason such as `NO_GROUNDED_AHA_AFTER_SEARCH`. Writer or engineering failure must never be reported as a legitimate zero-Aha day.

## 6. Quality-recovery gates

### Gate 1 — Evidence and S04 reliability

- introduce an additive Web/Algorithm handshake;
- use one Evidence image for a photo;
- use the test-only duration-aware phone-video profile for arbitrary library video lengths;
- preserve grounded facts when a non-critical structured field is invalid;
- record every field degradation, action, rule/path, and candidate hash without retaining free-form rejected content;
- distinguish insufficient visual evidence, structured-field degradation, and provider/engineering failure;
- run Person 1 through the full implemented chain.

The duration-aware phone profile is research-only and does not supersede the frozen Auto 9-second three-frame contract or the future real-App capture-mode contract.

### Gate 2 — Chapter Storyline segmentation

- generate Storyline candidates below Day Episode level;
- prevent theme/setting mixtures that do not share one story duty;
- preserve interruption/resume behavior without forcing the interruption into either surrounding Storyline;
- validate the expected two-to-three-Chapter behavior on Person 1 without hard-coding that pack.

### Gate 3 — dual-path Aha retrieval

- expose event and discovery search ledgers;
- enforce story-duty independence from Chapters;
- require an explicit audited reason for zero;
- validate sparse and rich packs with people 2 and 3.

### Gate 4 — three-person cross-pack evaluation

- run all three packs independently from raw input;
- collect target-specific feedback at Chapter, Aha, media, claim, title/story, and stage level;
- compare coverage, purity, distinctness, grounding, latency, Tokens, and cost;
- discuss accumulated evidence before changing thresholds or weights.

## 7. Claims and exclusions

This checkpoint freezes product intent and the evaluation method only. It does not claim that Gate 1-4 are implemented, that any real-media result is usable, that the three packs represent all users, or that X02/V03 is Production-ready. Each implementation gate requires a later additive integration checkpoint containing source hashes, tests, full-run evidence, known failures, and rollback information.
