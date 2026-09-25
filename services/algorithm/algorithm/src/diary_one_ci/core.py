from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


CAPTURE_INTERVAL_MS = 120_000
ASSET_DURATION_MS = 9_000
FRAME_OFFSETS_MS = (1_500, 4_500, 7_500)
E00_LEADERBOARD_ELIGIBLE = False


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> str:
    data = canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha256_bytes(data)


@dataclass(frozen=True)
class SourceProbe:
    source_id: str
    path: str
    sha256: str
    duration_ms: int
    width: int
    height: int
    orientation: str
    aspect_ratio: str
    probe_backend: str


@dataclass(frozen=True)
class LogicalAsset:
    asset_id: str
    source_id: str
    source_start_ms: int
    source_end_ms: int
    duration_ms: int
    materialized_video: bool = False


class SourceIngestor:
    def probe(self, source: Path) -> SourceProbe:
        source = source.resolve()
        if source.suffix == ".json":
            data = json.loads(source.read_text())
            backend = "fixture-manifest-v1"
            duration_ms = int(data["duration_ms"])
            width, height = int(data["width"]), int(data["height"])
        else:
            ffprobe = shutil.which("ffprobe")
            if not ffprobe:
                raise RuntimeError("ffprobe is required for real video input")
            cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration:stream=width,height", "-of", "json", str(source)]
            raw = json.loads(subprocess.check_output(cmd, text=True))
            video = next(s for s in raw["streams"] if "width" in s)
            width, height = int(video["width"]), int(video["height"])
            duration_ms = round(float(raw["format"]["duration"]) * 1000)
            backend = "ffprobe"
        if width * 4 != height * 3 or height <= width:
            raise ValueError(f"source must be portrait 3:4; got {width}x{height}")
        digest = sha256_file(source)
        return SourceProbe(
            source_id=f"src_{digest[:16]}", path=str(source), sha256=digest,
            duration_ms=duration_ms, width=width, height=height,
            orientation="PORTRAIT", aspect_ratio="3:4", probe_backend=backend,
        )


def simulate_logical_captures(source: SourceProbe) -> List[LogicalAsset]:
    assets: List[LogicalAsset] = []
    start = 0
    while start + ASSET_DURATION_MS <= source.duration_ms:
        stable = sha256_bytes(f"{source.sha256}:{start}:{ASSET_DURATION_MS}".encode())[:16]
        assets.append(LogicalAsset(
            asset_id=f"asset_{stable}", source_id=source.source_id,
            source_start_ms=start, source_end_ms=start + ASSET_DURATION_MS,
            duration_ms=ASSET_DURATION_MS,
        ))
        start += CAPTURE_INTERVAL_MS
    return assets


def _ppm(width: int, height: int, seed: bytes) -> bytes:
    # Deterministic source-dependent image; PPM keeps the zero-dependency fixture honest.
    header = f"P6\n{width} {height}\n255\n".encode()
    pixels = bytearray(width * height * 3)
    for y in range(height):
        for x in range(width):
            i = (y * width + x) * 3
            pixels[i:i + 3] = bytes(((seed[0] + x) % 256, (seed[1] + y) % 256, (seed[2] + x + y) % 256))
    return header + pixels


def extract_frames(source: SourceProbe, assets: Sequence[LogicalAsset], out_dir: Path) -> List[Dict[str, object]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg") if source.probe_backend == "ffprobe" else None
    frames: List[Dict[str, object]] = []
    for asset in assets:
        for offset in FRAME_OFFSETS_MS:
            timestamp = asset.source_start_ms + offset
            frame_id = f"frame_{sha256_bytes(f'{asset.asset_id}:{offset}'.encode())[:16]}"
            target = out_dir / f"{frame_id}.ppm"
            if ffmpeg:
                cmd = [ffmpeg, "-v", "error", "-ss", f"{timestamp / 1000:.3f}", "-i", source.path, "-frames:v", "1", "-vf", f"scale={source.width}:{source.height}", "-f", "image2", str(target)]
                subprocess.run(cmd, check=True)
            else:
                seed = hashlib.sha256(f"{source.sha256}:{timestamp}".encode()).digest()
                target.write_bytes(_ppm(source.width, source.height, seed))
            frames.append({
                "frame_id": frame_id, "asset_id": asset.asset_id, "source_id": source.source_id,
                "offset_ms": offset, "source_timestamp_ms": timestamp,
                "width": source.width, "height": source.height, "aspect_ratio": "3:4",
                "path": str(target), "sha256": sha256_file(target),
            })
    return frames


class EmbeddingAdapter:
    adapter_id = "abstract"
    dimension = 0

    def embed(self, frame_paths: Sequence[Path]) -> List[List[float]]:
        raise NotImplementedError


class DeterministicHashEmbedding(EmbeddingAdapter):
    """Smoke-only placeholder. It proves the adapter/provenance path, not semantics."""
    adapter_id = "deterministic-hash-placeholder-v1"
    dimension = 16

    def embed(self, frame_paths: Sequence[Path]) -> List[List[float]]:
        output = []
        for path in frame_paths:
            digest = hashlib.sha256(path.read_bytes()).digest()
            raw = [struct.unpack("b", digest[i:i + 1])[0] / 128.0 for i in range(self.dimension)]
            norm = math.sqrt(sum(v * v for v in raw)) or 1.0
            output.append([round(v / norm, 8) for v in raw])
        return output


def build_observations(assets: Sequence[LogicalAsset], frames: Sequence[Dict[str, object]], embeddings: Sequence[Sequence[float]], adapter: EmbeddingAdapter) -> List[Dict[str, object]]:
    by_asset: Dict[str, List[Tuple[Dict[str, object], Sequence[float]]]] = {}
    for frame, embedding in zip(frames, embeddings):
        by_asset.setdefault(str(frame["asset_id"]), []).append((frame, embedding))
    observations = []
    for asset in assets:
        pairs = by_asset[asset.asset_id]
        centroid = [round(sum(e[i] for _, e in pairs) / len(pairs), 8) for i in range(adapter.dimension)]
        observations.append({
            "observation_id": f"obs_{asset.asset_id[6:]}", "asset_id": asset.asset_id,
            "frame_ids": [f["frame_id"] for f, _ in pairs], "embedding_adapter": adapter.adapter_id,
            "embedding": centroid, "source_start_ms": asset.source_start_ms,
        })
    return observations


def smoke_moments(observations: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    # Intentionally non-semantic: deterministic groups of two prove downstream wiring.
    moments = []
    for i in range(0, len(observations), 2):
        group = observations[i:i + 2]
        moments.append({
            "moment_id": f"smoke_moment_{i // 2 + 1:04d}",
            "observation_ids": [o["observation_id"] for o in group],
            "asset_ids": [o["asset_id"] for o in group],
            "start_ms": group[0]["source_start_ms"],
            "engine": "smoke-pairing-v1", "algorithmically_meaningful": False,
        })
    return moments


def boundary_metrics(gold: Sequence[int], predicted: Sequence[int], tolerance_ms: int = 1_000) -> Dict[str, object]:
    unused = set(range(len(predicted)))
    matched = 0
    for g in sorted(gold):
        candidates = [(abs(predicted[i] - g), i) for i in unused if abs(predicted[i] - g) <= tolerance_ms]
        if candidates:
            _, idx = min(candidates)
            unused.remove(idx)
            matched += 1
    precision = matched / len(predicted) if predicted else (1.0 if not gold else 0.0)
    recall = matched / len(gold) if gold else (1.0 if not predicted else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": matched, "fp": len(predicted) - matched, "fn": len(gold) - matched,
            "precision": precision, "recall": recall, "f1": f1, "boundary_miss_rate": 1 - recall}


def run_eval_v01(assets: Sequence[LogicalAsset], moments: Sequence[Dict[str, object]]) -> Dict[str, object]:
    predicted = [int(m["start_ms"]) for m in moments[1:]]
    # Synthetic smoke gold is fixed and explicitly not benchmark gold.
    gold = [assets[i].source_start_ms for i in range(2, len(assets), 2)]
    return {
        "evaluator": "EVAL_V01", "dataset": "E00_SYNTHETIC_SMOKE_GOLD",
        "leaderboard_eligible": False, "tolerance_ms": 1_000,
        "metrics": boundary_metrics(gold, predicted),
        "metric_interpretation": "wiring-only; no algorithm claim",
    }


def transfer_cost_trace(source: SourceProbe, frames: Sequence[Dict[str, object]], adapter: EmbeddingAdapter) -> Dict[str, object]:
    evidence_bytes = sum(Path(str(f["path"])).stat().st_size for f in frames)
    raw_estimate = round(source.duration_ms / 1000 * 6_000_000 / 8)
    return {
        "trace_version": "TRANSFER_COST_V01", "phone_to_cloud": {
            "strategy": "FRAMES_3", "uploaded_bytes": evidence_bytes,
            "full_source_bytes_estimate_at_6mbps": raw_estimate,
            "full_9s_assets_uploaded": 0,
        },
        "ai_cost_usd": 0.0, "model_calls": 0,
        "embedding": {"adapter": adapter.adapter_id, "cost_usd": 0.0, "placeholder": True},
    }


def validate_e00(source: SourceProbe, assets: Sequence[LogicalAsset], frames: Sequence[Dict[str, object]], observations: Sequence[Dict[str, object]], moments: Sequence[Dict[str, object]]) -> Dict[str, object]:
    asset_ids = {a.asset_id for a in assets}
    frame_ids = {str(f["frame_id"]) for f in frames}
    observation_ids = {str(o["observation_id"]) for o in observations}
    checks = {
        "portrait_3x4": source.width * 4 == source.height * 3 and source.height > source.width,
        "logical_assets_not_materialized": all(not a.materialized_video for a in assets),
        "logical_assets_are_9s": all(a.duration_ms == ASSET_DURATION_MS for a in assets),
        "three_frames_per_asset": len(frames) == len(assets) * len(FRAME_OFFSETS_MS),
        "fixed_offsets": all(int(f["offset_ms"]) in FRAME_OFFSETS_MS for f in frames),
        "absolute_timestamps": all(int(f["source_timestamp_ms"]) == next(a.source_start_ms for a in assets if a.asset_id == f["asset_id"]) + int(f["offset_ms"]) for f in frames),
        "frame_to_asset_provenance": all(str(f["asset_id"]) in asset_ids and str(f["source_id"]) == source.source_id for f in frames),
        "observation_to_frame_provenance": all(set(map(str, o["frame_ids"])).issubset(frame_ids) and str(o["asset_id"]) in asset_ids for o in observations),
        "moment_to_observation_provenance": all(set(map(str, m["observation_ids"])).issubset(observation_ids) for m in moments),
        "frame_hashes_valid": all(sha256_file(Path(str(f["path"]))) == f["sha256"] for f in frames),
    }
    return {"validation_version": "E00_VALIDATION_V01", "passed": all(checks.values()), "checks": checks}


def make_report(run: Dict[str, object]) -> str:
    rows = "".join(f"<tr><th>{escape(str(k))}</th><td>{escape(str(v))}</td></tr>" for k, v in run["summary"].items())
    manifest = escape(json.dumps(run, indent=2, ensure_ascii=False))
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Diary One E00</title>
<style>body{{font:15px system-ui;max-width:960px;margin:40px auto;padding:0 20px;color:#18202a}}h1{{margin-bottom:4px}}.badge{{display:inline-block;background:#e7f7ec;color:#146c2e;padding:5px 10px;border-radius:99px}}table{{border-collapse:collapse;width:100%;margin:24px 0}}th,td{{border:1px solid #d9dee5;padding:9px;text-align:left}}th{{width:34%;background:#f6f8fa}}pre{{background:#f6f8fa;padding:16px;overflow:auto}}small{{color:#586069}}</style></head>
<body><h1>E00 Smoke Path</h1><p class='badge'>{escape(str(run['status']))}</p><p><small>Engineering validation only · leaderboard eligible: false</small></p>
<table>{rows}</table><h2>Reproducibility manifest</h2><pre>{manifest}</pre></body></html>"""


def _write_artifact_index(run_dir: Path) -> None:
    write_json(run_dir / "artifact_index.json", {
        "index_version": "ARTIFACT_INDEX_V01",
        "files": {
            str(path.relative_to(run_dir)): sha256_file(path)
            for path in sorted(run_dir.rglob("*"))
            if path.is_file() and path.name != "artifact_index.json"
        },
    })


def create_fixture(root: Path) -> Path:
    fixture = root / "fixtures" / "e00_portrait_3x4.json"
    write_json(fixture, {"fixture_version": "1", "duration_ms": 489_000, "width": 120, "height": 160,
                         "orientation": "PORTRAIT", "aspect_ratio": "3:4", "content": "deterministic synthetic timeline"})
    return fixture


def run_smoke(source_path: Optional[Path], artifact_root: Path, experiment_context: Optional[Dict[str, object]] = None) -> Path:
    artifact_root.mkdir(parents=True, exist_ok=True)
    if source_path is None:
        source_path = create_fixture(artifact_root)
    source = SourceIngestor().probe(source_path)
    assets = simulate_logical_captures(source)
    if not assets:
        raise ValueError("source is too short for one 9s logical asset")
    run_key = sha256_bytes(canonical_bytes({
        "experiment": "E00", "source": source.sha256,
        "config": [CAPTURE_INTERVAL_MS, ASSET_DURATION_MS, FRAME_OFFSETS_MS],
        "input_contract": experiment_context.get("input_contract") if experiment_context else None,
        "bundle_manifest_sha256": experiment_context.get("bundle_manifest_sha256") if experiment_context else None,
    }))[:20]
    final_dir = artifact_root / f"e00_{run_key}"
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{run_key}.", dir=str(artifact_root)))
    try:
        adapter = DeterministicHashEmbedding()
        frames = extract_frames(source, assets, temp_dir / "frames")
        embeddings = adapter.embed([Path(str(f["path"])) for f in frames])
        observations = build_observations(assets, frames, embeddings, adapter)
        moments = smoke_moments(observations)
        evaluation = run_eval_v01(assets, moments)
        trace = transfer_cost_trace(source, frames, adapter)
        validation = validate_e00(source, assets, frames, observations, moments)
        if not validation["passed"]:
            raise RuntimeError("E00 validation failed")
        persisted_frames = [dict(frame, path=f"frames/{Path(str(frame['path'])).name}") for frame in frames]
        payloads = {
            "source_probe.json": asdict(source), "logical_assets.json": [asdict(a) for a in assets],
            "frames.json": persisted_frames, "embeddings.json": {"adapter": adapter.adapter_id, "dimension": adapter.dimension, "vectors": embeddings},
            "observations.json": observations, "moments.json": moments, "evaluation.json": evaluation,
            "transfer_cost_trace.json": trace, "validation.json": validation,
        }
        if experiment_context is not None:
            payloads["experiment_context.json"] = experiment_context
        hashes = {name: write_json(temp_dir / name, value) for name, value in payloads.items()}
        summary = {"logical assets": len(assets), "materialized 9s videos": 0, "fixed frames": len(frames),
                   "frame offsets": "1.5 / 4.5 / 7.5 s", "geometry": f"{source.width}×{source.height} portrait 3:4",
                   "embedding": adapter.adapter_id, "AI cost": "$0.00", "leaderboard": "excluded"}
        manifest = {"experiment": "E00", "status": "SUCCEEDED", "leaderboard_eligible": E00_LEADERBOARD_ELIGIBLE,
                    "run_key": run_key, "created_at": datetime.now(timezone.utc).isoformat(), "config": {
                        "capture_interval_ms": CAPTURE_INTERVAL_MS, "logical_asset_duration_ms": ASSET_DURATION_MS,
                        "frame_offsets_ms": FRAME_OFFSETS_MS, "materialize_logical_assets": False,
                    }, "summary": summary, "artifact_hashes": hashes}
        if experiment_context is not None:
            manifest["input_contract"] = experiment_context["input_contract"]
            manifest["session_id"] = experiment_context["session"]["session_id"]
        manifest_hash = write_json(temp_dir / "manifest.json", manifest)
        manifest["manifest_sha256"] = manifest_hash
        (temp_dir / "report.html").write_text(make_report(manifest), encoding="utf-8")
        _write_artifact_index(temp_dir)
        if final_dir.exists():
            shutil.rmtree(temp_dir)
        else:
            os.replace(temp_dir, final_dir)
        return final_dir
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def run_preextracted_evidence_smoke(
    manifest_path: Path,
    manifest: Dict[str, object],
    bundle_validation: Dict[str, object],
    artifact_root: Path,
) -> Path:
    """Run E00 from App-normalized frames without uploading or materializing raw media."""
    artifact_root.mkdir(parents=True, exist_ok=True)
    bundle_hash = sha256_file(manifest_path)
    run_key = sha256_bytes(canonical_bytes({
        "experiment": "E00_APP_LIBRARY_SMOKE",
        "bundle_manifest_sha256": bundle_hash,
        "contract": manifest["bundle_version"],
    }))[:20]
    final_dir = artifact_root / f"e00_app_library_{run_key}"
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{run_key}.", dir=str(artifact_root)))
    try:
        root = manifest_path.resolve().parent
        logical_assets: List[LogicalAsset] = []
        source_records: List[Dict[str, object]] = []
        input_frames: List[Dict[str, object]] = []
        for index, item in enumerate(manifest["assets"]):
            asset_id = str(item["asset_id"])
            original_hash = str(item["original_sha256"])
            timeline_offset = int(item.get("timeline_offset_ms", index * CAPTURE_INTERVAL_MS))
            logical_assets.append(LogicalAsset(
                asset_id=asset_id,
                source_id=f"src_{original_hash[:16]}",
                source_start_ms=timeline_offset,
                source_end_ms=timeline_offset + ASSET_DURATION_MS,
                duration_ms=ASSET_DURATION_MS,
                materialized_video=False,
            ))
            source_records.append({
                "asset_id": asset_id,
                "media_kind": item["media_kind"],
                "original_sha256": original_hash,
                "original_bytes": int(item["original_bytes"]),
                "original_duration_ms": item.get("original_duration_ms"),
                "original_width": item["original_width"],
                "original_height": item["original_height"],
                "capture_time": item.get("capture_time"),
                "original_included": False,
            })
            for frame in item["frames"]:
                input_frames.append({
                    **frame,
                    "asset_id": asset_id,
                    "source_id": f"src_{original_hash[:16]}",
                    "timeline_offset_ms": timeline_offset,
                })

        frames_dir = temp_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        frames: List[Dict[str, object]] = []
        for frame in input_frames:
            source_path = (root / str(frame["relative_path"])).resolve()
            suffix = source_path.suffix.lower() or ".jpg"
            target = frames_dir / f"{frame['frame_id']}{suffix}"
            shutil.copyfile(source_path, target)
            canonical_offset = int(frame["canonical_offset_ms"])
            frames.append({
                "frame_id": frame["frame_id"],
                "asset_id": frame["asset_id"],
                "source_id": frame["source_id"],
                "offset_ms": canonical_offset,
                "source_timestamp_ms": int(frame["timeline_offset_ms"]) + canonical_offset,
                "original_source_timestamp_ms": frame.get("source_timestamp_ms"),
                "width": int(frame["width"]), "height": int(frame["height"]),
                "aspect_ratio": "3:4", "spatial_transform": frame["spatial_transform"],
                "path": str(target), "sha256": sha256_file(target),
            })

        adapter = DeterministicHashEmbedding()
        embeddings = adapter.embed([Path(str(frame["path"])) for frame in frames])
        observations = build_observations(logical_assets, frames, embeddings, adapter)
        moments = smoke_moments(observations)
        evaluation = run_eval_v01(logical_assets, moments)
        asset_ids = {asset.asset_id for asset in logical_assets}
        frame_ids = {str(frame["frame_id"]) for frame in frames}
        observation_ids = {str(observation["observation_id"]) for observation in observations}
        checks = {
            "bundle_gate_passed": bundle_validation.get("passed") is True,
            "one_logical_asset_per_input": len(logical_assets) == len(manifest["assets"]),
            "logical_assets_are_9s": all(asset.duration_ms == ASSET_DURATION_MS for asset in logical_assets),
            "logical_assets_not_materialized": all(not asset.materialized_video for asset in logical_assets),
            "three_frames_per_asset": len(frames) == len(logical_assets) * 3,
            "fixed_canonical_offsets": all(int(frame["offset_ms"]) in FRAME_OFFSETS_MS for frame in frames),
            "normalized_portrait_3x4": all(int(frame["width"]) * 4 == int(frame["height"]) * 3 for frame in frames),
            "frame_hashes_valid": all(sha256_file(Path(str(frame["path"]))) == frame["sha256"] for frame in frames),
            "frame_to_asset_provenance": all(str(frame["asset_id"]) in asset_ids for frame in frames),
            "observation_to_frame_provenance": all(set(map(str, observation["frame_ids"])).issubset(frame_ids) for observation in observations),
            "moment_to_observation_provenance": all(set(map(str, moment["observation_ids"])).issubset(observation_ids) for moment in moments),
        }
        validation = {"validation_version": "E00_APP_LIBRARY_VALIDATION_V01", "passed": all(checks.values()), "checks": checks}
        if not validation["passed"]:
            raise RuntimeError("App Library E00 validation failed")
        evidence_bytes = sum(Path(str(frame["path"])).stat().st_size for frame in frames)
        original_bytes = sum(int(record["original_bytes"]) for record in source_records)
        trace = {
            "trace_version": "TRANSFER_COST_V01",
            "phone_to_cloud": {
                "strategy": "APP_NORMALIZED_FRAMES_3",
                "uploaded_bytes": evidence_bytes,
                "original_source_bytes": original_bytes,
                "originals_uploaded": 0,
                "full_9s_assets_uploaded": 0,
            },
            "ai_cost_usd": 0.0, "model_calls": 0,
            "embedding": {"adapter": adapter.adapter_id, "cost_usd": 0.0, "placeholder": True},
        }
        context = {
            "input_contract": manifest["bundle_version"],
            "bundle_manifest_sha256": bundle_hash,
            "session": manifest["session"], "device": manifest["device"],
            "normalization": manifest["normalization"],
            "bundle_validation": bundle_validation,
        }
        persisted_frames = [dict(frame, path=f"frames/{Path(str(frame['path'])).name}") for frame in frames]
        payloads = {
            "source_assets.json": source_records,
            "logical_assets.json": [asdict(asset) for asset in logical_assets],
            "frames.json": persisted_frames,
            "embeddings.json": {"adapter": adapter.adapter_id, "dimension": adapter.dimension, "vectors": embeddings},
            "observations.json": observations, "moments.json": moments,
            "evaluation.json": evaluation, "transfer_cost_trace.json": trace,
            "validation.json": validation, "experiment_context.json": context,
        }
        hashes = {name: write_json(temp_dir / name, value) for name, value in payloads.items()}
        kinds = sorted({str(record["media_kind"]) for record in source_records})
        summary = {
            "input mode": "arbitrary App library media",
            "source assets": len(source_records), "media kinds": ", ".join(kinds),
            "logical assets": len(logical_assets), "materialized 9s videos": 0,
            "fixed frames": len(frames), "canonical frame offsets": "1.5 / 4.5 / 7.5 s",
            "normalized geometry": f"{frames[0]['width']}×{frames[0]['height']} portrait 3:4",
            "raw originals uploaded": 0, "AI cost": "$0.00", "leaderboard": "excluded",
        }
        run_manifest = {
            "experiment": "E00_APP_LIBRARY_SMOKE", "status": "SUCCEEDED",
            "leaderboard_eligible": False, "run_key": run_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "input_contract": manifest["bundle_version"],
            "session_id": manifest["session"]["session_id"],
            "config": {"logical_asset_duration_ms": ASSET_DURATION_MS,
                       "frame_offsets_ms": FRAME_OFFSETS_MS,
                       "materialize_logical_assets": False},
            "summary": summary, "artifact_hashes": hashes,
        }
        manifest_hash = write_json(temp_dir / "manifest.json", run_manifest)
        run_manifest["manifest_sha256"] = manifest_hash
        (temp_dir / "report.html").write_text(make_report(run_manifest), encoding="utf-8")
        _write_artifact_index(temp_dir)
        if final_dir.exists():
            shutil.rmtree(temp_dir)
        else:
            os.replace(temp_dir, final_dir)
        return final_dir
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
