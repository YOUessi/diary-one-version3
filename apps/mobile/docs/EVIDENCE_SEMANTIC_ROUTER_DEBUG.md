# Evidence semantic router — debug (mobile)

Lightweight visual semantics only: **Feature Print 768-d + VNClassify top-10 + rule fusion (40% feature / 60% labels)**. Picks **1 / 3 / 5 / 10** frames. Not full video understanding.

## Where code lives

| Piece | Path |
| --- | --- |
| TS router | `src/evidence/` |
| Pipeline hook | `src/pipeline/buildAppLibraryBundle.ts` (VIDEO) |
| Sidecar audit | `{bundleDir}/semantic_route_{assetId}.json` |
| iOS Vision module | `modules/diary-one-vision/` (Dev Client / `expo run:ios` only) |

## Run modes

### Expo Go (no native module)

1. Internal Lab → Apply BFF → Ping.
2. Import video (**B · photo library**).
3. Analyzer: `fallback_expo_go` → **`degraded: true`** (brightness/histogram vector). Routing still runs but **must not be treated as Vision quality**.
4. If BFF URL is set and `/v1/evidence/semantic-analyze` returns 501 on Windows, phone stays on fallback — expected.

### iOS Dev Client / EAS development build

1. `npx expo run:ios` or EAS dev client with `diary-one-vision` linked.
2. Import video → analyzer `native_vision` → real Feature Print + classify.
3. Lab button **C · Semantic route debug** shows last audit summary.

### Dev Lite BFF (PC)

- `POST /v1/evidence/semantic-analyze` — multipart `probe_0`, `probe_1`, … (JPEG). **Windows: 501** (use phone native/fallback).
- `POST /v1/evidence/semantic-route` — JSON probes with vectors (stateless audit / parity notes).

## Inspect output

- Asset field `semantic_route_summary` in `bundle.json`.
- Share sidecar JSON from bundle dir after import (path in pipeline task `bundleDir`).
- `getLastSemanticRouteAudit()` via Lab **C**.

## Product constraints

- Photos: still **single frame** + dedupe unchanged.
- Do **not** claim MobileCLIP in Expo Go without weights.
- Failed semantic path falls back to legacy duration windows (logged in `semantic_route_summary`).

See also monorepo `docs/EVIDENCE_SEMANTIC_ROUTER_DEBUG.md`.
