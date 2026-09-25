# App Library Bundle V03 — Phone Test Sequence-only Contract

Status: V04.1 research-candidate input contract; not Production and not a wearable capture contract.

## 1. What this bundle is

`DIARY_ONE_APP_LIBRARY_BUNDLE_V03` is the boundary between the local Web research page and the V04.1 algorithm for a manually imported phone-library test day. It carries normalized Evidence plus enough source metadata to audit the test. It does not carry original media bytes.

Every import is treated as one research day. When the source files do not provide verified capture metadata, their array order is represented only by a contiguous zero-based `sequence_index`.

## 2. Time truth

- `sequence_index` means “the tester imported this item in this position.” It may support deterministic display/tie order and provisional sequence partitioning, but it is not a clock time, elapsed duration, or proof of capture adjacency.
- `timeline_offset_ms` is forbidden.
- `logical_asset_duration_ms = 9000` is only the canonical Evidence-normalization contract. It is not the original duration and must never create a day timeline.
- `source_timestamp_ms` is a sampling position inside one photo/video source. For a photo it is `null`; for a video it is a clip-relative millisecond offset. It says nothing about gaps between two assets.
- V04.1 treats current App Library Bundle V01/V02/V03 inputs as `SYNTHETIC_SEQUENCE_ONLY`, returns `timeline_date = null`, and sets every time-reliability flag false. Legacy timestamp/offset fields in V01/V02 do not elevate those inputs to verified chronology. A future `CAPTURE_TIME` mode requires a separate additive contract with timestamp provenance, timezone and ordering validation.

The valid user-facing boundary label is therefore such as `导入顺序第 4–9 项`, never `10:00–10:12` or an invented date.

## 3. Evidence exposure

| Source | Evidence sent to the algorithm | Meaning |
|---|---|---|
| Photo | 1 representative normalized frame | One still observation |
| Video ≤10 s | 1 Window / 3 frames | Early, middle and late evidence |
| Video 10–30 s | 2 Windows / 4 frames | Two Windows, early and late per Window |
| Video 30–90 s | 4 Windows / 8 frames | Four Windows, early and late per Window |
| Video >90 s | 6 Windows / 12 frames | Six Windows, early and late per Window |

All frames are normalized to 768 × 1024 portrait Evidence. The source file remains local; only normalized Evidence declared by the manifest is used for the staged model call.

This phone-test profile does not replace the frozen wearable Auto 9-second / fixed-three-frame contract.

## 4. Validation layers

The checked-in JSON Schema, [`contracts/app_library_bundle_v03.schema.json`](../contracts/app_library_bundle_v03.schema.json), closes the object shapes, field types, fixed identities, media-duration branches and sequence-only fields.

The runtime loader additionally verifies rules that plain JSON Schema does not completely express:

- every `sequence_index` equals its zero-based array position;
- asset and frame IDs are unique;
- Window counts, frame counts, frame roles and canonical offsets form the exact duration profile;
- video sample offsets are unique, ordered and within that source video;
- photo sample offsets are null;
- every Evidence path stays inside the bundle directory;
- every declared Evidence file exists and its SHA-256, geometry and transform match the manifest.

The V04.1 server must reject a bundle when either the structural contract or these cross-field/file gates fail. This input validation is separate from the V04.1 result runtime audit and result JSON Schema; validating a Bundle does not certify a generated result.

## 5. Version boundaries

- V04.1 accepts V01/V02 for controlled historical compatibility and V03 for the active Web test page.
- Historical X02 V03 accepts V01/V02 only and rejects V03.
- Historical E00 rejects V03 because its old adapter would synthesize two-minute offsets from array order.
- V03 is additive. It does not silently change a historical route or result identity.
- [App research export V01](app-research-export-v01.md) remains the historical V01 export reference; it is not the current Web manifest contract.

## 6. Explicit exclusions

This contract does not prove capture-time reliability, GPS, background Sync, cloud storage, privacy governance, S13 HQ export, wearable fidelity, user satisfaction or Production readiness. Those require separate contracts and evidence.
