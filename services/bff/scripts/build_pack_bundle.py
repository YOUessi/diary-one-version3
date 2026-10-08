#!/usr/bin/env python3
"""Build App Library Bundle V04 (letterbox 768x1024) from a folder of photos.

Videos are skipped in this PC pack builder (use Expo Lab B / eval-web for video
duration windows). Photos are enough to open the cloud bulk channel:
  media dir → V04 bundle → POST /v1/day-revisions → Worker → X02 (DashScope) → chapters.

Usage:
  python build_pack_bundle.py --media D:\\packs\\day1 --out D:\\packs\\day1_bundle
  python build_pack_bundle.py --media D:\\packs\\day1 --out D:\\packs\\day1_bundle --max-assets 40
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
OUT_W, OUT_H = 768, 1024
FIT = "ASPECT_FIT_LETTERBOX"
BUNDLE_V04 = "DIARY_ONE_APP_LIBRARY_BUNDLE_V04"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def letterbox_jpeg(src: Path, dest: Path) -> tuple[int, int, int]:
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise SystemExit(
            "Pillow required: python -m pip install pillow"
        ) from exc

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        src_w, src_h = im.size
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        elif im.mode == "L":
            im = im.convert("RGB")

        scale = min(OUT_W / src_w, OUT_H / src_h)
        new_w = max(1, int(round(src_w * scale)))
        new_h = max(1, int(round(src_h * scale)))
        resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (OUT_W, OUT_H), (0, 0, 0))
        canvas.paste(resized, ((OUT_W - new_w) // 2, (OUT_H - new_h) // 2))
        dest.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(dest, format="JPEG", quality=90, optimize=True)
        return src_w, src_h, dest.stat().st_size


def collect_photos(media: Path) -> list[Path]:
    files = [
        p
        for p in sorted(media.rglob("*"))
        if p.is_file() and p.suffix.lower() in PHOTO_EXTS
    ]
    return files


def build_bundle(media: Path, out: Path, max_assets: int) -> Path:
    photos = collect_photos(media)
    if not photos:
        raise SystemExit(f"No photos under {media}")
    photos = photos[:max_assets]

    if out.exists():
        shutil.rmtree(out)
    frames_dir = out / "frames"
    frames_dir.mkdir(parents=True)

    assets: list[dict] = []
    for index, src in enumerate(photos):
        asset_id = f"asset-{index}"
        rel = f"frames/{asset_id}_0.jpg"
        dest = out / rel
        try:
            orig_w, orig_h, _ = letterbox_jpeg(src, dest)
        except Exception as exc:  # noqa: BLE001
            print(f"SKIP {src.name}: {exc}")
            continue
        frame_sha = sha256_file(dest)
        orig_sha = sha256_file(src)
        assets.append(
            {
                "asset_id": asset_id,
                "source_display_name": src.name,
                "media_kind": "PHOTO",
                "media_source": "PHONE_LIBRARY_DAY_TEST",
                "original_file_extension": src.suffix.lstrip(".").lower() or "jpg",
                "original_sha256": orig_sha,
                "original_bytes": src.stat().st_size,
                "original_width": orig_w,
                "original_height": orig_h,
                "original_duration_ms": None,
                "original_included": False,
                "sequence_index": len(assets),
                "logical_asset_duration_ms": 9000,
                "materialized_video": False,
                "evidence_sampling_profile": "PHOTO_SINGLE_FRAME",
                "evidence_window_count": 1,
                "frames": [
                    {
                        "frame_id": f"{asset_id}-f0",
                        "window_index": 0,
                        "window_count": 1,
                        "sample_role": "PHOTO_REPRESENTATIVE",
                        "canonical_offset_ms": 4500,
                        "source_timestamp_ms": None,
                        "relative_path": rel,
                        "sha256": frame_sha,
                        "width": OUT_W,
                        "height": OUT_H,
                        "spatial_transform": FIT,
                    }
                ],
            }
        )

    if not assets:
        raise SystemExit("All photos failed to normalize")

    # Re-index after skips
    for i, asset in enumerate(assets):
        asset["sequence_index"] = i

    manifest = {
        "bundle_version": BUNDLE_V04,
        "research_only": True,
        "session": {
            "session_id": str(uuid.uuid4()),
            "exported_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "timezone": "Asia/Shanghai",
        },
        "device": {
            "device_id": "PHOTO_LIBRARY_TEST",
            "hardware_revision": "N/A",
            "firmware_version": "N/A",
            "sdk_version": "diary-one-cloud-pack",
        },
        "normalization": {
            "width": OUT_W,
            "height": OUT_H,
            "orientation": "PORTRAIT",
            "aspect_ratio": "3:4",
            "spatial_transform": FIT,
            "temporal_transform": "PHONE_TEST_DURATION_WINDOWS_V01",
            "canonical_frame_offsets_ms": [1500, 4500, 7500],
            "evidence_profile_version": "PHONE_TEST_DURATION_WINDOWS_V01",
        },
        "assets": assets,
    }
    json_path = out / "bundle.json"
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built V04 bundle: {len(assets)} photos → {json_path}")
    return json_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Diary One Bundle V04 from photos")
    parser.add_argument("--media", required=True, type=Path, help="Folder of photos")
    parser.add_argument("--out", required=True, type=Path, help="Output bundle directory")
    parser.add_argument("--max-assets", type=int, default=240, help="Cap assets (X02 max 240)")
    args = parser.parse_args()
    if not args.media.is_dir():
        raise SystemExit(f"Not a directory: {args.media}")
    build_bundle(args.media.resolve(), args.out.resolve(), max(1, min(240, args.max_assets)))


if __name__ == "__main__":
    main()
