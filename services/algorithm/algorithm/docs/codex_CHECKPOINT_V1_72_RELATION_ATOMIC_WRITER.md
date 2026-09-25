# Diary One Algorithm V1.72 Implementation Checkpoint

Status: implementation authorized; real-material quality not yet verified.

## Position in the pipeline

V1.72 is an opt-in research successor to V1.71. It changes only the existing
S04 -> S07 -> S09 -> S10 -> S11 research path. It does not change the Web/App
default, Firmware/SDK, the three-to-five Chapter media contract, the daily
Chapter/Aha ceilings, S13 export, GPS, or incremental upload behavior.

## Real defects being repaired

The V1.71 pack-1 run exposed four concrete defects:

1. The selected three Chapters and three Ahas had no complete Chapter/Aha
   relation evidence, while the result was still treated as a complete
   recommendation.
2. Aha/Aha similarity was checked only for exact source duplication, so two
   cards could repeat the same story without a pairwise editorial decision.
3. One selected Aha could carry several facts and several visible events from
   one observation, so it was not an atomic Moment.
4. The Writer returned Aha lines longer than the accepted 24-character
   tolerance; they were labelled for review but still published as valid copy.
   The same run also showed overconfident visible-text and action wording.

## V1.72 contract

### A. Selection-bound relation matrix

The single S07 response must bind the recommended set and its evidence in one
`day_selection` object:

- every selected Chapter/Aha pair has exactly one relation row;
- every unordered selected Aha/Aha pair has exactly one relation row;
- rows cite only facts belonging to the two cards;
- `DISTINCT_STORY` is required for both cards to remain in the published set;
- `SAME_STORY`, `UNRESOLVED`, missing, duplicate, or invalid rows reject only
  the affected later Aha; they do not erase otherwise valid Chapters or Ahas;
- no program-generated relation, proxy score, replacement candidate, retry
  model call, or scene-specific exception is allowed.

This matrix is editorial organization, not new visual evidence. A complete
status is forbidden unless the actually selected set has a closed matrix.

### B. Atomic Aha Moment

- S04 is instructed to record separate visible events/states/discoveries as
  separate facts instead of joining disjoint moments into one fact.
- One S07 Aha proposal must select exactly one supported fact from exactly one
  observation.
- The selected Aha media evidence is narrowed to the frame IDs cited by that
  fact, and the Writer receives only that fact.
- Failure to bind one fact rejects that Aha; the program does not split prose
  heuristically or invent a replacement Moment.

### C. Single-pass 24-character delivery gate

- The Aha `text` field receives a structured-schema `maxLength: 24` contract.
- The local delivery validator independently measures visible characters and
  rejects text above 24.
- A length failure never triggers another model draw. Valid sibling cards may
  still publish; the failed Aha is explicitly blocked.
- The 20-character preference remains a writing target; 21-24 characters are
  accepted.

The current Qwen compatible endpoint provides JSON-object mode rather than a
guarantee of provider-side constrained decoding. Therefore the release gate,
not a provider promise, is the final enforcement boundary.

### D. Uncertain text and action strength

- S04 uses exact visible names/text only when clearly legible; otherwise it
  records a generic fact and an uncertainty limitation.
- S04 describes the weakest action/state supported by the sampled frames and
  must not upgrade stationary to moving, walking to running, or possibility to
  certainty.
- S11 receives the limitations relevant to each card and may not restore a
  precise name or stronger action that S04 did not support.

These are general evidence rules. There are no rules for dogs, ancient towns,
specific OCR strings, colors, or any other example scene.

## Acceptance sequence

1. Contract/unit checks prove exact pair coverage, atomic fact binding,
   isolated rejection, one Writer model call, and the 24-character gate.
2. The complete local regression suite passes without changing V1.71's opt-in
   entry behavior.
3. V1.72 is frozen as a new candidate without rewriting earlier checkpoints.
4. A fresh pack-1 normalization and full S04-S12 run is performed with no
   semantic response reuse.
5. Real output is reviewed card by card. Only that review can establish whether
   the real quality defects improved; local tests alone cannot.

## Explicit exclusions

No Web/App switch, deployment, public test, App R2 change, Firmware/SDK change,
shared-state update, long-term-memory update, S13 export, cost optimization,
GPS integration, semantic keyword blocker, synthetic image-error audit, or
automatic API rewrite is authorized by this checkpoint.
