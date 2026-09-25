# Diary One Algorithm V1.72.1 Implementation Checkpoint

Status: implementation authorized; supersedes V1.72 for the next research candidate; real-material quality not yet verified.

## Position in the pipeline

V1.72.1 is a narrow, opt-in research correction inside the existing S04 -> S07 -> S09 -> S10 -> S11 path. It retains V1.72 Chapter grouping and the complete selected-set Chapter/Aha plus Aha/Aha relation matrix. It does not change Web/App defaults, Firmware/SDK, daily quantity ceilings, the Chapter three-to-five-media contract, S13 export, GPS, upload behavior, or Production status.

## Superseding evidence

The fresh V1.72 pack-1 run established three concrete defects:

1. A fact could cite several frames and combine several visible details, so “one fact” did not always become one user-visible Moment.
2. All three Writer Aha lines exceeded 24 characters even though the request schema carried `maxLength: 24`; provider-side constrained decoding is unavailable on the current compatible JSON-object path.
3. The deterministic fallback lost the grounded Writer policy field and republished longer raw facts, bypassing the local hard gate.

The run also showed that a non-repeating Aha can still be too weak when it only supplies contextual labeling rather than an independently revisit-worthy discovery, interaction, or turn.

## V1.72.1 contract

### A. One selected fact, one focus frame, one focal duty

- Every S07 Aha proposal and selected Aha row must identify exactly one supported fact.
- It must also identify exactly one `focus_frame_id` belonging to that fact's evidence frames.
- It must provide one concise `moment_focus` describing the focal subject and its one central action, state, or discovery.
- Proposal and final selection must agree exactly on observation, fact, focus frame, and moment focus. Any mismatch rejects only that Aha.
- The program verifies references but does not create a focus, split prose, or choose a replacement.
- Final Aha media contains only the validated focus frame. The full selected fact remains available to the Writer as grounding evidence, not as a requirement to mention every detail.

### B. General independent-value instruction

S07 must not select an Aha merely because it is a place label, background explanation, taxonomy, or otherwise different from the Chapters. It should be independently worth revisiting as a small discovery, interaction, or turn supported by the recording. This remains a model editorial judgment; there is no keyword gate, object list, scene whitelist, score threshold, or generated semantic counterexample.

### C. One Writer call and one authoritative exit

- S11 makes exactly one model call for the supplied set. There is no API rewrite, retry draw, or post-hoc model repair.
- Aha `text` keeps a 20-character target and a 24-visible-character hard delivery maximum.
- The local validator is the final authority. An invalid Aha is blocked while valid sibling cards survive.
- Grounded-policy Ahas may never be published through deterministic raw-fact fallback. Chapter fallback behavior is unchanged.
- Every derived Writer context used by validation or Chapter fallback must preserve the active grounded-policy field, so validation cannot silently downgrade.
- The current research route uses Qwen3.7 Plus for S07 and S11; S04 and S10 remain on Qwen VL Flash. This changes model routing, not call count.

### D. Focused, grounded expression

- Writer centers an Aha on the supplied `moment_focus`: normally one focal subject plus one action, state, or discovery.
- Secondary background, color, decoration, inventory, camera/process language, and other modifiers are omitted unless essential to understand that Moment.
- The original fact and evidence cautions remain the only factual authority. `moment_focus` is an editorial compression hint, not a new fact source.
- Ordinary target-language wording is preferred; unexplained mixed-language terms are avoided when a natural local equivalent exists.
- Uncertain visible text remains generic, and action intensity cannot exceed the evidence.

These are general content and evidence rules. They contain no runtime exception for any example object, place, animal, activity, or architectural style.

## Acceptance sequence

1. Protocol tests prove focus-frame membership, proposal/selection agreement, single-frame Aha media, one Writer call, policy preservation, and fail-closed handling of overlength Ahas.
2. The complete local regression suite passes, with historical V1.72 evidence unchanged.
3. V1.72.1 is frozen as a new candidate with its own source hashes and profile.
4. Material pack 1 is freshly normalized and run through the complete S04-S12 research chain without semantic reply reuse.
5. Review each Chapter/Aha, including the exact Aha focus frame, expression, pair relations, time, Token, and cost. Only this review can establish real quality.

## Explicit exclusions

No Web/App switch, deployment, public/internal test activation, App R2 change, Firmware/SDK change, shared-state update, long-term-memory update, S13 export, GPS integration, semantic keyword blocker, scene-specific rule, synthetic image-error test, or repeated Writer API draw is authorized by this checkpoint.
