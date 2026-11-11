# Diary One · Planner + Physically Scoped Gallery V02 (opt-in)

**2026-11-11. Research-only integration. Not deployed to production.**
Development branch: experiment/2026-11-11-planner-gallery-router.
Source: committed Direct VLM V03 feature branch; the original Mac worktree's uncommitted V04/Live edits were left untouched.

## 1. Baseline stays available

- Default: unset DIARY_ONE_X02_EDITOR -> direct_vlm -> original run_direct_vlm (unchanged).
- Previous Product Editor: DIARY_ONE_X02_EDITOR=product_v1 -> original Product Editor.
- Research candidate: DIARY_ONE_X02_EDITOR=planner_gallery_v02 -> run_planner_gallery.
- New BFF publication gate (independently default OFF): DIARY_ONE_ALLOW_PLANNER_GALLERY_V02_PUBLISH=1.
- Do not enable both toggles in the production service until integration and visual quality acceptance.

The X02 /health response shows DIARY_ONE_PLANNER_GALLERY_CHAPTER_V02, PLANNER_GALLERY_SCOPED_EDITOR_V02 and a runtimePolicy for physical per-chapter JPEG scope. Existing multipart endpoint remains /x02/v0.4.1/preview. The consumer phone still uses the ordinary /v1/day-revisions asynchronous job path.

## 2. Full algorithm ownership

Phone (unchanged):

    10s MP4 -> MobileCLIP-S0 FP16 endpoint V05 + coverage V07
             -> 1..5 or 10 representative JPEG + actual PTS + Frame IDs + SHA256
             -> Bundle V04/V05 -> BFF upload

Cloud V02 (only when opted in):

    all uploaded JPEG -> Qwen Chapter Planner
       title, story, end_clip, excluded_images
       -> deterministic, strictly increasing clip ranges [prev+1, end]
       -> each range resolves the exact ORIGINAL JPEG records
       -> N separate Qwen Gallery calls, each sees ONLY its chapter JPEG
            selected_images[0] = hero, selected_images[] and key_moments[]
            local IMAGE_INDEX numbering 1..chapter-image-count
            original CLIP_SEQUENCE still preserved in the labels
       -> V02 public media result with source_clip_start/end, original Frame IDs,
          chapter evidence lineage, complete model-call receipts
       -> BFF V02 JSON schema + source-clip interval validation + SHA256 JPG checks
       -> (opt-in publication gate only) phone V02 input-bound result validation
       -> Chapter display, original local JPEG / MP4 mapping
       -> phone-side 3-second Chapter Motion / Live-style presentation for V05
          (NO Apple Photos paired Live Photo is claimed)

The new backend never processes the phone's original MP4. Motion generation remains a **phone-side** algorithm. This experimental branch does not change MobileCLIP, source videos, Live export, or the user's original uncommitted phone code.

## 3. Stage and error policies

- Stage 1: single global visual Planner; at most one fresh retry for malformed planning.
- Stage 2: one JPEG physically isolated Gallery call per Chapter; at most one retry for only that failed Chapter. No successful Chapter is regenerated after a Gallery failure.
- If either stage remains invalid, fail the Day job; never silently fall back to V01 or accept an invented frame ID.
- Model output saved as a private audit record (0600) for each real request when audit_dir is set; images/API keys not embedded.
- App-side and BFF-side checks independently verify input-bound results; BFF requires each Chapter to own [prev.end+1, end] without gaps and requires the last end == number of submitted source assets.
- Every public image, key moment and experience frame must come from the originating Chapter's source span. Selected hero must be first in gallery and must be the unique HERO.
- All model requests, including failed attempts, count toward the token and cost ledger.
- Hard caps: max 250 input JPEG, 35 MiB total raw JPEG, max 14 Chapter, 20 gallery entries per Chapter, 10 key moments per Chapter, 30 model calls per run.
- DIARY_ONE_PLANNER_GALLERY_BUDGET_CNY defaults to 1.20; abort immediately after a completed call exceeds the cumulative cost cap. A provider call that crosses this threshold is still billable.
- No semantic truth certification: title, subject, location and story still require separate visual assessment.

**Source-clip semantics:** one input Bundle asset is one CLIP_SEQUENCE in this contract. A >10s imported video with multiple windows is one source asset and cannot be split into separate Chapters *within that same asset*. The usual Diary One wearable intake supplies individual 10s video assets. This limitation must be tested before accepting long-form imports as a whole-day planner input.

## 4. Versioned result contract

- New public result: DIARY_ONE_PLANNER_GALLERY_CHAPTER_V02.
- New stage trace pipeline: X02_PLANNER_GALLERY_CHAPTER_V02.
- Editor policy: PLANNER_GALLERY_SCOPED_EDITOR_V02.
- Stable input-bound UUID5: planner_gallery_v02:C01 etc (separate namespace from V01).
- Public Chapter fields add source_clip_start and source_clip_end, both 1-based.
- decision_trace.chapter_clip_intervals lists every continuous interval.
- decision_trace.gallery_model_input_frames counts physically scoped JPEGs.
- trace.stage_metrics contains *all* Planner/Gallery call receipts.
- Separate BFF schema file and SHA256 allowlist; no overwrite of the frozen V01 schema.
- Experimental=true and production_ready=false intentionally preserved.

## 5. Verification

Use the Mac's existing environment, never the Tang machine to develop:

    cd ~/Documents/Nexleap/Diary_one_planner_gallery_exp_20261111
    export PYTHONPATH="$PWD/services/algorithm/algorithm/src:$PWD/services/bff"
    /Users/youtang/Documents/Nexleap/Diary_one_version3_clean/.venv/bin/python -m pytest -q \
      services/algorithm/algorithm/tests/test_planner_gallery_v02.py \
      services/algorithm/algorithm/tests/test_direct_vlm_compact.py \
      services/bff/tests/test_direct_vlm_contract.py

    cd apps/mobile
    ./node_modules/.bin/tsc --noEmit
    node --test tests/planner-gallery-v02-contract.test.cjs

Tests validate: default-off routing; real JPEG bundle; fake provider input counts and request order; entire clip ownership; explicit UUID/Trace/BFF schema; BFF dual-gate; tampered frame ID, time range, moment, cost/trace rejection; exact-frame-only retry; private raw receipts; phone-side V02 rejection of forged references.

## 6. Why this is only a candidate

Previous real Qwen experiments showed:
- one-call end_clip: strict-valid 1/12;
- single-call nested plan/gallery: strict-valid 0/12;
- two global stages with all photos visible: 0/2 whole Days strict-valid;
- per-chapter JPEG physical selection: 1/2 whole Days on first attempt, 2/2 after one bounded retry, but the independent semantic judge still flagged unsupported object/place claims and gallery/cover mismatch risks.

Therefore passing this new V02 structure **is not a product quality decision**. Before a live rollout, run at least three independent repeats across city/nature/museum/other user profiles, ground named works/landmarks, measure distinct scene recall, verify each cover, detect semantic duplicate photos, profile sequential model latency/cost, and complete a production-like BFF job test.

## 7. Rollback

Leave DIARY_ONE_X02_EDITOR unset (defaults to direct_vlm) and remove DIARY_ONE_ALLOW_PLANNER_GALLERY_V02_PUBLISH from BFF. No phone extraction logic, original video files or Live algorithm needs modification.


## 8. Mac real-provider and HTTP acceptance receipts (2026-11-11)

Completed on the Mac using the configured Qwen3.8-Flash API, without modifying the running production deployment.

**Direct gateway smoke (13 museum JPEGs):**
- Provider calls: 2 (1 Chapter Planner, 1 scoped Chapter Gallery).
- Output: 1 Chapter / 9 Gallery images.
- Estimated cost: ¥0.0188807 from actual request usage.
- V02 JSON Schema, exact source frame references and BFF input-bound result contract passed.

**Local X02 HTTP multipart smoke (39 Sydney Citywalk JPEGs):**
- Only bound to 127.0.0.1, port 18889, and stopped after verification.
- GET /health reported V02 schema, editor revision, model ready and max 30 calls.
- POST /x02/v0.4.1/preview returned HTTP 200.
- Five Chapter source-clip intervals: [1,8], [9,13], [14,20], [21,28], [29,39].
- Final Gallery: 26 JPEGs from the originally submitted 39.
- Six real model requests: one Planner plus five Gallery calls. Every request ID is retained privately.
- Actual token-based estimated provider cost: ¥0.0565589.
- BFF V02 strict input binding passed; the isolated opt-in publication envelope passed; actual phone V02 validator accepted the unchanged real model output.
- Private model outputs/real JPGs are stored outside Git, under:
  ~/Documents/Nexleap/work_logs/evidence/planner-gallery-v02-smoke-20261111/
- Stage-attempt private audit directories are mode 0700; JSON model responses are mode 0600.
- No API keys or test user media are committed to Git.

For this integration smoke the 13/39 genuine historical JPEGs were packaged as individual PHOTO assets with preserved ordering; this verifies API, schema, time ownership and image provenance, **not** live-phone video capture, long-form segmentation or an unbiased Chapter semantic quality benchmark. The new path still requires actual phone video import and Live/Motion device tests before release.

**Regression tests in the isolated worktree:**
- Python algorithm + entire BFF regression set: 245 passed, 7 skipped.
- App Node contract tests: 30 passed.
- App TypeScript compile with --noEmit: passed.
- Both prior V01 results and newer V02 output retain separate immutable schema hashes.
- Test UI/production endpoint was not deployed or changed.
