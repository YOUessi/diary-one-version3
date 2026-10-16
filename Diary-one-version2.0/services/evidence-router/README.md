# Evidence router (Dev Lite / parity)

Full Python engine lives in `E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router`.

## Windows MobileCLIP (wired)

Dev Lite now loads MobileCLIP for `POST /v1/evidence/semantic-analyze` when:

```powershell
$env:DIARY_ONE_MOBILECLIP_CHECKPOINT = "…\mobileclip_s0.pt"
```

See **`docs/WINDOWS_MOBILECLIP_BFF.md`**.

`start-dev-lite.ps1` adds the reference package `src` to `PYTHONPATH` automatically.

## Profiles

- Phone TypeScript routing switches to `MOBILECLIP_*` profiles when `modelId` contains `MOBILECLIP`.
- iOS Dev Client still uses Apple Vision (`DiaryOneVision`) when the native module is present.

Apple Vision helper (Mac only): `scripts/vision_feature_print.m` from the reference package.
