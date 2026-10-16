# App Research Export Contract V01

This contract is the thin, offline bridge between the Diary One App and Stage 1 experiments. It is research-only and is not a production sync API.

RC13 normally exports `DIARY_ONE_APP_LIBRARY_BUNDLE_V01`, which accepts ordinary Photos-library photos and videos without requiring source 3:4 geometry or a nine-second duration. The older strict continuous-source `DIARY_ONE_EXPERIMENT_BUNDLE_V01` remains available for canonical S001-style captures.

## Bundle layout

```text
session-export/
├── bundle.json
└── media/
    └── source.mp4
```

`bundle.json` must conform to `contracts/experiment_bundle_v01.schema.json`. The importer also applies semantic gates that JSON Schema cannot express:

- the source hash must match;
- probed media must match the declared duration and geometry;
- media must be portrait 3:4;
- the simulation must remain 120s/9s;
- offsets must remain 1.5/4.5/7.5s;
- 9-second videos must not be materialized;
- relative paths may not escape the bundle directory.

## Ordinary Photos-library compatibility path

For `contracts/app_library_bundle_v01.schema.json`, RC13 performs deterministic on-phone normalization:

- any photo geometry is center-cropped with aspect-fill to 768×1024;
- any positive-duration video is sampled at 1/6, 1/2 and 5/6 of its actual duration;
- those samples map to the canonical 1.5/4.5/7.5-second internal coordinates;
- a photo's one factual still is used at each of the three internal coordinates;
- original dimensions, duration, byte size and SHA-256 remain in provenance;
- every derived frame has its own SHA-256 and actual video timestamp;
- full Photos originals are not included or uploaded.

This path verifies App evidence generation and the cloud pipeline with convenient personal media. It remains E00 smoke data and cannot be used as an algorithm leaderboard result.

## App exporter responsibility

The App exporter copies one continuous research source into the bundle and records pseudonymous device, firmware, SDK, media-profile, timezone, and export provenance. It computes SHA-256 after the copy has completed, then writes `bundle.json` last. An incomplete export must never have a final `bundle.json`.

The exporter does not upload the bundle automatically. User-controlled local export is the V01 handoff.

## Import gate

```bash
PYTHONPATH=src python3 -m diary_one_ci.cli bundle validate /path/to/session-export/bundle.json
PYTHONPATH=src python3 -m diary_one_ci.cli bundle run-e00 /path/to/session-export/bundle.json
```

Only a bundle that passes the gate can produce a `SUCCEEDED` E00 artifact. E00 remains excluded from the leaderboard.

## Explicitly out of scope

- account or authentication integration;
- production object storage and signed upload;
- background queue or retry system;
- Chapter or Aha UI;
- automatic full-raw phone-to-cloud upload;
- SDK diagnostic logic inside the formal App.
