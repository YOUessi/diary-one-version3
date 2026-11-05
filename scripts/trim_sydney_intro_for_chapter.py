#!/usr/bin/env python3
"""Remove Sydney source-recording intro before generating any VLM input.

Input: App Library Bundle + authoritative 120s phase timestamps.csv.
Output: separate, JPEG-only, hash-verified sanitized input directory.
The original source video and previous experiments remain unchanged.

Any 10s clip overlapping [0, cutoff) is dropped completely. This is
deliberate: keeping a 70-80s clip would be able to reintroduce 70-72s
when a Chapter later plays its source video.
"""
from __future__ import annotations

import argparse
import copy
import csv
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import uuid

ASSET = re.compile(r"^sydney_\d{2}_(\d{6})$")


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as fp:
        for data in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def create_clean_input(manifest: Path, index_csv: Path, output: Path,
                       cutoff: Decimal = Decimal("72")) -> dict:
    manifest = manifest.resolve()
    index_csv = index_csv.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"Output already exists; refusing to overwrite: {output}")
    bundle = json.loads(manifest.read_text())
    if not isinstance(bundle.get("assets"), list) or not bundle["assets"]:
        raise ValueError("Source has no assets")
    with index_csv.open(encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    by_number = {int(row["original_clip_id"]): row for row in rows}
    if len(by_number) != len(rows):
        raise ValueError("Duplicate original clip in index")
    if len(by_number) != len(bundle["assets"]):
        raise ValueError("Index does not cover entire source bundle")
    kept = []
    excluded = []
    for original_sequence, asset in enumerate(bundle["assets"]):
        match = ASSET.fullmatch(str(asset["asset_id"]))
        if match is None:
            raise ValueError("Unexpected asset ID; refuse to guess source time: " + str(asset["asset_id"]))
        clip_number = int(match.group(1))
        row = by_number.get(clip_number)
        if row is None:
            raise ValueError(f"No authoritative absolute timestamp for {asset['asset_id']}")
        start = Decimal(row["start_seconds"])
        end = Decimal(row["end_seconds"])
        if end <= start:
            raise ValueError("Invalid source clip range")
        if int(asset.get("sequence_index", -1)) != original_sequence:
            raise ValueError("Source sequence index inconsistent")
        # Drop any intersecting intro clip, including 70-80s at 72s cutoff.
        if start < cutoff:
            excluded.append({
                "asset_id": asset["asset_id"], "source_start_seconds": str(start),
                "source_end_seconds": str(end),
                "crosses_cutoff": end > cutoff,
                "frame_ids": [frame["frame_id"] for frame in asset["frames"]],
            })
        else:
            kept.append((asset, start, end))
    if not kept:
        raise ValueError("No clips remain after intro removal")
    sanitized = copy.deepcopy(bundle)
    sanitized["assets"] = [copy.deepcopy(item[0]) for item in kept]
    # Never conflate a trimmed session with previous full-source runs.
    session = sanitized["session"]
    original_sid = uuid.UUID(session["session_id"])
    session["session_id"] = str(uuid.uuid5(original_sid, f"sydney-intro-removed:{cutoff}s"))
    for seq, asset in enumerate(sanitized["assets"]):
        asset["sequence_index"] = seq

    # Atomic directory construction: no partial input can be mistaken as complete.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".intro-cut-", dir=output.parent) as temp:
        tmp = Path(temp) / "input"
        tmp.mkdir()
        kept_frame_ids = set()
        total_bytes = 0
        for asset in sanitized["assets"]:
            for frame in asset["frames"]:
                fid = frame["frame_id"]
                if fid in kept_frame_ids:
                    raise ValueError("Duplicate input Frame ID")
                kept_frame_ids.add(fid)
                rel = PurePosixPath(frame["relative_path"])
                if rel.is_absolute() or ".." in rel.parts:
                    raise ValueError("Unsafe relative image path")
                source = manifest.parent.joinpath(*rel.parts)
                if not source.is_file() or digest(source) != frame["sha256"]:
                    raise ValueError(f"Missing or hash-invalid source JPEG: {fid}")
                target = tmp.joinpath(*rel.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                os.link(source, target)  # No duplicate JPEG bytes, source protected.
                total_bytes += target.stat().st_size
        for optional in ("app_client_profile.json",):
            source = manifest.parent / optional
            if source.exists():
                (tmp / optional).write_bytes(source.read_bytes())
        out_manifest = tmp / "bundle.json"
        out_manifest.write_text(json.dumps(sanitized, ensure_ascii=False, indent=2))
        safe_manifest_sha = digest(out_manifest)
        os.rename(tmp, output)
    remaining_first = min(start for _, start, _ in kept)
    receipt = {
        "rule": "SYDNEY_SOURCE_RECORDING_INTRO_HARD_CUT_V01",
        "source_intro_cutoff_seconds": str(cutoff),
        "intro_deleted_from_vlm_input": True,
        "exclusion_policy": "WHOLE_CLIP_IF_START_BEFORE_CUTOFF",
        "reason": "Prevent opening-route-map or recap media entering the VLM context",
        "source_manifest": str(manifest),
        "source_manifest_sha256": digest(manifest),
        "sanitized_manifest": str(output / "bundle.json"),
        "sanitized_manifest_sha256": safe_manifest_sha,
        "source_session_id": str(original_sid),
        "sanitized_session_id": session["session_id"],
        "source_assets": len(bundle["assets"]),
        "sanitized_assets": len(sanitized["assets"]),
        "removed_assets": len(excluded),
        "source_frames": sum(len(a["frames"]) for a in bundle["assets"]),
        "sanitized_frames": len(kept_frame_ids),
        "removed_frame_ids": [fid for item in excluded for fid in item["frame_ids"]],
        "removed_intervals": excluded,
        "first_remaining_clip_start_seconds": str(remaining_first),
        "retained_images_bytes": total_bytes,
        "model_input_contains_intro": False,
        "model_api_calls": 0,
    }
    (output.parent / "intro_cut_receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cutoff-seconds", type=Decimal, default=Decimal("72"))
    args = parser.parse_args()
    if args.cutoff_seconds <= 0:
        raise ValueError("Cutoff must be positive")
    r = create_clean_input(args.manifest, args.index, args.output, args.cutoff_seconds)
    print(json.dumps({
        k: r[k] for k in (
            "source_assets", "sanitized_assets", "source_frames",
            "sanitized_frames", "removed_frame_ids",
            "first_remaining_clip_start_seconds", "sanitized_manifest",
        )}, ensure_ascii=False))


if __name__ == "__main__":
    main()
