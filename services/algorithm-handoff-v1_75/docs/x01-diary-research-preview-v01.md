# X01 Diary Research Preview V01

Status: `EXPERIMENTAL`, `leaderboard_eligible=false`.

X01 is an isolated integration spike for showing evidence-grounded Chapter and Aha objects in the RC13 Diary UI. It does not rename or replace canonical E01, does not claim Stage 2 validation, and is not a production backend or agent framework.

## Boundary

Input is a validated `DIARY_ONE_APP_LIBRARY_BUNDLE_V01`:

- arbitrary source photos/videos are normalized locally to portrait 3:4;
- each logical asset has evidence at canonical 1.5/4.5/7.5-second positions;
- original geometry, duration, capture time, byte count, and hash remain provenance;
- the multipart request contains `bundle.json` and declared evidence JPEGs only;
- original photos/videos and materialized 9-second clips are absent.

The response contract is `contracts/x01_diary_preview_v01.schema.json`. It contains observations, local moments, up to four Chapters, up to three Aha memories, evidence-backed claim ledgers, stable IDs, model/request/cost trace, bundle hash, and an explicit day mode. Empty output is valid. `decision_trace` is auditable decision evidence: it lists selected frame IDs, Observation validation outcomes, observed/Materialized counts, every raw Moment candidate's validation/materialization status, and every Chapter/Aha candidate's validation/selection status plus reason codes. Superseded Moment keys cannot be silently rebound to another Moment for the same asset. It explicitly does not contain model chain-of-thought or hidden reasoning. One malformed or unpresented-frame Observation is rejected individually and retained in `observation_candidates`; it cannot fabricate evidence or abort otherwise valid results.

## Precision gates

- Chapter confidence must be at least 0.76.
- Aha confidence must be at least 0.84 and its current hero must be a photo.
- selected Chapters cannot share underlying asset moments.
- Chapter/Aha semantic duplicates are suppressed.
- every selected claim cites known frame IDs belonging to its selected assets;
- unknown references, invalid ledgers, oversized narratives, and low-confidence candidates are rejected;
- an experimental result must report `leaderboard_eligible=false` and `originals_uploaded=0`.

These are research defaults, not benchmark-validated thresholds.

## Model gateway

The default live adapter is Alibaba Cloud Model Studio `qwen3-vl-flash-2026-01-22`, called through its OpenAI-compatible Chat Completions endpoint. The server first reads `DASHSCOPE_API_KEY`; on macOS local research machines it falls back to the login Keychain item named `DiaryOne DashScope API Key`. The credential is kept in process memory, is never printed, and is never exported to the iPhone. `DIARY_ONE_X01_QWEN_BASE_URL` remains an optional process-environment override. Qwen JSON Object mode is treated as untrusted model output: the prompt carries the schema, and the local contract layer still validates all objects, IDs, evidence ownership, claim ledgers, lengths, confidence gates, and daily limits.

`OpenAIResponsesAdapter` remains an explicit cross-vendor frame challenger with strict Structured Outputs; it is not the X01 default. It reads `OPENAI_API_KEY` only when `--adapter openai` is selected. The two providers share the same `EditorialModelAdapter` boundary and normalized result contract.

Trace output is provider-neutral. It records model-call count, tokens, provider/model/request ID, model-frame count, latency, pricing currency and rates, native cost, the configured native-currency/USD conversion, and estimated USD cost. The pricing basis is recorded so reruns do not silently reinterpret historical cost. `stage_metrics` measures `BUNDLE_LOAD`, `EDITORIAL_MODEL_BRIDGE`, and `DETERMINISTIC_VALIDATION_SELECTION`; only the actual model bridge receives model-call, token, and cost attribution. X01 does not invent a per-stage S00-S13 token split from one model request.

Every successful server request is atomically archived, without embedded image bytes, under `var/x01_runs/<session UUID>/runs/<run UUID>.run_audit.json`; `run_audit.json` in the Session directory is an atomic latest-run view. The audit contains the received manifest, returned result, multipart-materialization duration, X01-run duration, and request byte count. Set `DIARY_ONE_X01_RUN_AUDIT_DIR` or `--run-audit-dir` to use another local directory. `var/x01_runs/` is intentionally ignored by Git.

When a billable model response is received but later deterministic validation still fails, the gateway also writes `failures/<failure UUID>.failed_run_audit.json` plus the atomic `failure_audit.json` latest view. The image-free failure record keeps the model request ID, selected Evidence allowlist, raw structured model output, stage durations, input/output tokens, pricing basis, and estimated native/USD cost. This prevents failed calls from disappearing from cost and quality analysis.

`POST /x01/v0.1/run-sidecar` accepts at most 2 MiB of image-free JSON and attaches client timing plus a structured human evaluation to an already-recorded Session. The envelope is `DIARY_ONE_X01_RUN_SIDECAR_V01`; `human_review` uses `DIARY_ONE_HUMAN_EVALUATION_V02`, repeats the same Session UUID, and requires `evaluation_id`, a non-negative integer `revision`, `run_id`, `bundle_manifest_sha256`, `pipeline_version`, and `request_id`. All four Run-binding fields must be non-empty and match that exact archived Run. `run_id` resolves `runs/<run UUID>.run_audit.json`; Human Evaluation never falls back to the latest-run alias. Review revisions are atomically archived under `reviews/<evaluation UUID>/<revision>.human_review.json`; stale revisions and conflicting content at the same revision are rejected, while an exact retry is idempotent. `human_review.json` remains the latest accepted review view. The V02 evaluation body otherwise remains extensible so granular Day, Chapter, Aha, asset, frame, copy-field, and boundary feedback can evolve without changing this storage endpoint. Client Trace may omit Run binding for compatibility, but a supplied Client Trace `run_id` is still verified and archived against that Run.

Every Observation, Moment, Chapter, Aha, and Claim frame reference is checked against the exact `selected_evidence` allowlist reported by the adapter. A frame that exists in the uploaded bundle but was not presented to the model cannot support model output. The model prompt treats frame IDs as opaque allowlist tokens and explicitly forbids constructing or predicting them from asset IDs or canonical offsets.

Qwen research configuration:

- `DASHSCOPE_API_KEY`: model credential; on macOS, the login Keychain item `DiaryOne DashScope API Key` is used when this variable is absent;
- `DIARY_ONE_X01_QWEN_BASE_URL`: workspace-specific HTTPS base URL ending in `/compatible-mode/v1`;
- `DIARY_ONE_X01_QWEN_MODEL`: defaults to `qwen3-vl-flash-2026-01-22`;
- `DIARY_ONE_X01_QWEN_INPUT_CNY_PER_MTOK` / `DIARY_ONE_X01_QWEN_OUTPUT_CNY_PER_MTOK`: reproducible native pricing overrides;
- `DIARY_ONE_X01_CNY_PER_USD`: explicit cost-conversion input, recorded in every result;
- `DIARY_ONE_X01_QWEN_PRICING_BASIS`: optional label for the price sheet or contract used.

OpenAI challenger configuration uses `OPENAI_API_KEY`, `DIARY_ONE_X01_OPENAI_MODEL`, `DIARY_ONE_X01_OPENAI_INPUT_USD_PER_MTOK`, and `DIARY_ONE_X01_OPENAI_OUTPUT_USD_PER_MTOK`.

Phone-to-Mac research traffic uses TLS with certificate pinning plus a separate bearer token. The server refuses non-loopback startup unless a TLS certificate, private key, and bearer token are present. This test transport credential is not the model API key.

`FixtureEditorialAdapter` exists solely for deterministic contract and transport tests. It must be selected explicitly with `--adapter fixture`, labels its provider/model as a fixture, records zero model calls, and is never a live fallback.

## RC13 flow

1. Open Developer Tools.
2. Under Cloud E00 Smoke Test, choose ordinary Photos-library photos/videos; 4–12 related items are recommended for a first X01 run.
3. The app prepares the normalized evidence bundle.
4. Check the X01 server. Generation remains disabled unless `/health` reports the model ready.
5. Tap Generate on Diary Home.
6. The result is contract-validated, appended as a new archived run, and shown on Diary with an X01 experimental badge.
