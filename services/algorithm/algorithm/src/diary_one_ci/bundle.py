from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union

from .core import (
    ASSET_DURATION_MS,
    CAPTURE_INTERVAL_MS,
    FRAME_OFFSETS_MS,
    SourceIngestor,
    run_preextracted_evidence_smoke,
    run_smoke,
    sha256_file,
)


BUNDLE_VERSION = "DIARY_ONE_EXPERIMENT_BUNDLE_V01"
APP_LIBRARY_BUNDLE_VERSION = "DIARY_ONE_APP_LIBRARY_BUNDLE_V01"
APP_LIBRARY_BUNDLE_VERSION_V02 = "DIARY_ONE_APP_LIBRARY_BUNDLE_V02"
APP_LIBRARY_BUNDLE_VERSION_V03 = "DIARY_ONE_APP_LIBRARY_BUNDLE_V03"
APP_LIBRARY_BUNDLE_VERSION_V04 = "DIARY_ONE_APP_LIBRARY_BUNDLE_V04"
PHONE_TEST_EVIDENCE_PROFILE_V01 = "PHONE_TEST_DURATION_WINDOWS_V01"

_APP_LIBRARY_BUNDLE_VERSIONS = (
    APP_LIBRARY_BUNDLE_VERSION,
    APP_LIBRARY_BUNDLE_VERSION_V02,
    APP_LIBRARY_BUNDLE_VERSION_V03,
    APP_LIBRARY_BUNDLE_VERSION_V04,
)
_APP_LIBRARY_BUNDLE_V03_ASSET_FIELDS = frozenset({
    "asset_id",
    "source_display_name",
    "media_kind",
    "media_source",
    "original_file_extension",
    "original_sha256",
    "original_bytes",
    "original_width",
    "original_height",
    "original_duration_ms",
    "original_included",
    "sequence_index",
    "logical_asset_duration_ms",
    "materialized_video",
    "evidence_sampling_profile",
    "evidence_window_count",
    "frames",
})
_APP_LIBRARY_BUNDLE_V03_TOP_FIELDS = frozenset({
    "bundle_version", "research_only", "session", "device", "normalization", "assets",
})
_APP_LIBRARY_BUNDLE_V03_SESSION_FIELDS = frozenset({
    "session_id", "exported_at", "timezone",
})
_APP_LIBRARY_BUNDLE_V03_DEVICE_FIELDS = frozenset({
    "device_id", "hardware_revision", "firmware_version", "sdk_version",
})
_APP_LIBRARY_BUNDLE_V03_NORMALIZATION_FIELDS = frozenset({
    "width", "height", "orientation", "aspect_ratio", "spatial_transform",
    "temporal_transform", "canonical_frame_offsets_ms", "evidence_profile_version",
})
_APP_LIBRARY_BUNDLE_V03_FRAME_FIELDS = frozenset({
    "frame_id", "window_index", "window_count", "sample_role",
    "canonical_offset_ms", "source_timestamp_ms", "relative_path", "sha256",
    "width", "height", "spatial_transform",
})


@dataclass(frozen=True)
class ImportedBundle:
    manifest_path: Path
    source_path: Path
    manifest: Dict[str, object]
    validation: Dict[str, object]


@dataclass(frozen=True)
class ImportedEvidenceBundle:
    manifest_path: Path
    manifest: Dict[str, object]
    validation: Dict[str, object]


def _required(mapping: Dict[str, object], keys, location: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ValueError(f"{location} missing required fields: {', '.join(missing)}")


def _reject_unexpected(mapping: Dict[str, object], allowed, location: str) -> None:
    unexpected = sorted(set(mapping) - set(allowed))
    if unexpected:
        raise ValueError(
            f"{location} has unsupported fields for App Library Bundle V03: "
            + ", ".join(unexpected)
        )


def _v03_nonempty_string(value: object, location: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{location} must be a non-empty string")
    return value


def _v03_integer(value: object, location: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"{location} must be an integer >= {minimum}")
    return value


def _v03_sha256(value: object, location: str) -> str:
    text = _v03_nonempty_string(value, location)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{location} must be 64 lowercase hexadecimal characters")
    return text


def _contained_file(root: Path, relative_value: object, location: str) -> Path:
    relative = Path(str(relative_value))
    if relative.is_absolute():
        raise ValueError(f"{location} must be relative to the bundle")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{location} escapes the bundle directory") from exc
    if not resolved.is_file():
        raise ValueError(f"{location} does not exist: {relative}")
    return resolved


def load_bundle(manifest_path: Path) -> ImportedBundle:
    manifest_path = manifest_path.resolve()
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _required(manifest, ("bundle_version", "research_only", "session", "device", "media_profile", "source", "processing"), "bundle")
    if manifest["bundle_version"] != BUNDLE_VERSION:
        raise ValueError(f"unsupported bundle_version: {manifest['bundle_version']}")
    if manifest["research_only"] is not True:
        raise ValueError("Experiment Bundle V01 must be research_only=true")

    session = manifest["session"]
    device = manifest["device"]
    profile = manifest["media_profile"]
    source_meta = manifest["source"]
    processing = manifest["processing"]
    if not all(isinstance(x, dict) for x in (session, device, profile, source_meta, processing)):
        raise ValueError("bundle sections must be JSON objects")
    _required(session, ("session_id", "exported_at", "timezone"), "session")
    _required(device, ("device_id", "hardware_revision", "firmware_version", "sdk_version"), "device")
    _required(profile, ("profile_id", "width", "height", "orientation", "aspect_ratio"), "media_profile")
    _required(source_meta, ("kind", "relative_path", "sha256", "duration_ms"), "source")
    _required(processing, ("capture_interval_ms", "logical_asset_duration_ms", "frame_offsets_ms", "materialize_logical_assets"), "processing")

    source_path = _contained_file(root, source_meta["relative_path"], "source.relative_path")

    checks = {
        "source_hash": sha256_file(source_path) == source_meta["sha256"],
        "portrait_3x4_profile": int(profile["width"]) * 4 == int(profile["height"]) * 3
        and int(profile["height"]) > int(profile["width"])
        and profile["orientation"] == "PORTRAIT"
        and profile["aspect_ratio"] == "3:4",
        "capture_interval_120s": int(processing["capture_interval_ms"]) == CAPTURE_INTERVAL_MS,
        "logical_asset_9s": int(processing["logical_asset_duration_ms"]) == ASSET_DURATION_MS,
        "fixed_frame_offsets": tuple(map(int, processing["frame_offsets_ms"])) == FRAME_OFFSETS_MS,
        "no_video_materialization": processing["materialize_logical_assets"] is False,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"bundle gate failed: {', '.join(failed)}")

    probe = SourceIngestor().probe(source_path)
    probe_checks = {
        "probe_width": probe.width == int(profile["width"]),
        "probe_height": probe.height == int(profile["height"]),
        "probe_duration": probe.duration_ms == int(source_meta["duration_ms"]),
        "probe_sha256": probe.sha256 == source_meta["sha256"],
    }
    failed = [name for name, passed in probe_checks.items() if not passed]
    if failed:
        raise ValueError(f"bundle metadata/probe mismatch: {', '.join(failed)}")
    validation = {
        "validation_version": "EXPERIMENT_BUNDLE_GATE_V01",
        "passed": True,
        "checks": {**checks, **probe_checks},
        "session_id": session["session_id"],
        "source_probe_backend": probe.probe_backend,
    }
    return ImportedBundle(manifest_path, source_path, manifest, validation)


def load_app_library_bundle(manifest_path: Path) -> ImportedEvidenceBundle:
    manifest_path = manifest_path.resolve()
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _required(manifest, ("bundle_version", "research_only", "session", "device", "normalization", "assets"), "bundle")
    bundle_version = manifest["bundle_version"]
    if bundle_version not in _APP_LIBRARY_BUNDLE_VERSIONS:
        raise ValueError(f"unsupported bundle_version: {manifest['bundle_version']}")
    if manifest["research_only"] is not True:
        raise ValueError(f"{bundle_version} must be research_only=true")
    session, device, normalization = manifest["session"], manifest["device"], manifest["normalization"]
    assets = manifest["assets"]
    if not all(isinstance(value, dict) for value in (session, device, normalization)) or not isinstance(assets, list):
        raise ValueError("bundle session/device/normalization must be objects and assets must be an array")
    _required(session, ("session_id", "exported_at", "timezone"), "session")
    _required(device, ("device_id", "hardware_revision", "firmware_version", "sdk_version"), "device")
    _required(normalization, ("width", "height", "orientation", "aspect_ratio", "spatial_transform", "temporal_transform", "canonical_frame_offsets_ms"), "normalization")
    if not assets:
        raise ValueError(f"{bundle_version} needs at least one asset")
    width, height = int(normalization["width"]), int(normalization["height"])
    uses_duration_windows = bundle_version in (
        APP_LIBRARY_BUNDLE_VERSION_V02,
        APP_LIBRARY_BUNDLE_VERSION_V03,
        APP_LIBRARY_BUNDLE_VERSION_V04,
    )
    # V04 retains V03's strict, sequence-only envelope; only geometry changes.
    is_v04 = bundle_version == APP_LIBRARY_BUNDLE_VERSION_V04
    is_v03 = bundle_version in (APP_LIBRARY_BUNDLE_VERSION_V03, APP_LIBRARY_BUNDLE_VERSION_V04)
    spatial_transform = "ASPECT_FIT_LETTERBOX" if is_v04 else "CENTER_CROP_ASPECT_FILL"
    if is_v03:
        _reject_unexpected(manifest, _APP_LIBRARY_BUNDLE_V03_TOP_FIELDS, "bundle")
        _reject_unexpected(session, _APP_LIBRARY_BUNDLE_V03_SESSION_FIELDS, "session")
        _reject_unexpected(device, _APP_LIBRARY_BUNDLE_V03_DEVICE_FIELDS, "device")
        _reject_unexpected(
            normalization,
            _APP_LIBRARY_BUNDLE_V03_NORMALIZATION_FIELDS,
            "normalization",
        )
        _required(
            normalization,
            _APP_LIBRARY_BUNDLE_V03_NORMALIZATION_FIELDS,
            "normalization",
        )
        for key in _APP_LIBRARY_BUNDLE_V03_SESSION_FIELDS:
            _v03_nonempty_string(session[key], f"session.{key}")
        try:
            uuid.UUID(str(session["session_id"]))
        except (AttributeError, ValueError) as exc:
            raise ValueError("session.session_id must be a UUID in App Library Bundle V03") from exc
        for key in _APP_LIBRARY_BUNDLE_V03_DEVICE_FIELDS:
            _v03_nonempty_string(device[key], f"device.{key}")
        expected_normalization = {
            "width": 768,
            "height": 1024,
            "orientation": "PORTRAIT",
            "aspect_ratio": "3:4",
            "spatial_transform": spatial_transform,
            "temporal_transform": PHONE_TEST_EVIDENCE_PROFILE_V01,
            "canonical_frame_offsets_ms": list(FRAME_OFFSETS_MS),
            "evidence_profile_version": PHONE_TEST_EVIDENCE_PROFILE_V01,
        }
        for key, expected in expected_normalization.items():
            if normalization[key] != expected:
                raise ValueError(
                    f"normalization.{key} must equal the {bundle_version} contract"
                )
    global_checks = {
        "normalized_portrait_3x4": width * 4 == height * 3 and height > width
        and normalization["orientation"] == "PORTRAIT" and normalization["aspect_ratio"] == "3:4",
        ("aspect_fit_letterbox_declared" if is_v04 else "center_crop_declared"):
            normalization["spatial_transform"] == spatial_transform,
        "normalized_temporal_sampling_declared": normalization["temporal_transform"] == (
            PHONE_TEST_EVIDENCE_PROFILE_V01
            if uses_duration_windows else "NORMALIZED_FRACTIONS_TO_CANONICAL_9S"
        ),
        "fixed_canonical_offsets": tuple(map(int, normalization["canonical_frame_offsets_ms"])) == FRAME_OFFSETS_MS,
    }
    if uses_duration_windows:
        global_checks["phone_test_evidence_profile_declared"] = (
            normalization.get("evidence_profile_version") == PHONE_TEST_EVIDENCE_PROFILE_V01
        )
    asset_ids = set()
    frame_ids = set()
    frame_count = 0
    kinds = set()
    frame_checks: List[bool] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ValueError(f"assets[{index}] must be an object")
        required_asset_fields = [
            "asset_id", "media_kind", "original_sha256", "original_bytes",
            "original_width", "original_height", "logical_asset_duration_ms",
            "materialized_video", "frames",
        ]
        if uses_duration_windows:
            required_asset_fields.extend(("evidence_sampling_profile", "evidence_window_count"))
        if is_v03:
            required_asset_fields.extend((
                "media_source",
                "original_file_extension",
                "original_duration_ms",
                "original_included",
                "sequence_index",
            ))
        _required(asset, required_asset_fields, f"assets[{index}]")
        if is_v03:
            if "timeline_offset_ms" in asset:
                raise ValueError(
                    f"assets[{index}].timeline_offset_ms is forbidden in App Library Bundle V03"
                )
            unexpected_fields = sorted(
                set(asset) - _APP_LIBRARY_BUNDLE_V03_ASSET_FIELDS
            )
            if unexpected_fields:
                raise ValueError(
                    f"assets[{index}] has unsupported fields for App Library Bundle V03: "
                    + ", ".join(unexpected_fields)
                )
            sequence_index = asset["sequence_index"]
            if (
                not isinstance(sequence_index, int)
                or isinstance(sequence_index, bool)
                or sequence_index != index
            ):
                raise ValueError(
                    f"assets[{index}].sequence_index must equal its zero-based array position {index}"
                )
            if asset["media_source"] != "PHONE_LIBRARY_DAY_TEST":
                raise ValueError(
                    f"assets[{index}].media_source must be PHONE_LIBRARY_DAY_TEST"
                )
            if not isinstance(asset["original_file_extension"], str) or not asset["original_file_extension"]:
                raise ValueError(
                    f"assets[{index}].original_file_extension must be a non-empty string"
                )
            _v03_nonempty_string(asset["asset_id"], f"assets[{index}].asset_id")
            if "source_display_name" in asset and not isinstance(asset["source_display_name"], str):
                raise ValueError(f"assets[{index}].source_display_name must be a string")
            _v03_sha256(asset["original_sha256"], f"assets[{index}].original_sha256")
            _v03_integer(asset["original_bytes"], f"assets[{index}].original_bytes")
            _v03_integer(asset["original_width"], f"assets[{index}].original_width", minimum=1)
            _v03_integer(asset["original_height"], f"assets[{index}].original_height", minimum=1)
            if asset["original_included"] is not False:
                raise ValueError(f"assets[{index}].original_included must be false")
            if asset["logical_asset_duration_ms"] != ASSET_DURATION_MS:
                raise ValueError(f"assets[{index}].logical_asset_duration_ms must be 9000")
            if asset["materialized_video"] is not False:
                raise ValueError(f"assets[{index}].materialized_video must be false")
            _v03_integer(
                asset["evidence_window_count"],
                f"assets[{index}].evidence_window_count",
                minimum=1,
            )
        asset_id = str(asset["asset_id"])
        if asset_id in asset_ids:
            raise ValueError(f"duplicate asset_id: {asset_id}")
        asset_ids.add(asset_id)
        kind = str(asset["media_kind"])
        if kind not in ("PHOTO", "VIDEO"):
            raise ValueError(f"unsupported media_kind: {kind}")
        kinds.add(kind)
        if len(str(asset["original_sha256"])) != 64:
            raise ValueError(f"assets[{index}].original_sha256 must be 64 hex characters")
        if int(asset["original_bytes"]) < 0 or int(asset["original_width"]) <= 0 or int(asset["original_height"]) <= 0:
            raise ValueError(f"assets[{index}] has invalid original metadata")
        if int(asset["logical_asset_duration_ms"]) != ASSET_DURATION_MS or asset["materialized_video"] is not False:
            raise ValueError(f"assets[{index}] violates logical 9s/no-materialization contract")
        frames = asset["frames"]
        if not isinstance(frames, list):
            raise ValueError(f"assets[{index}].frames must be an array")
        duration_ms = asset.get("original_duration_ms")
        if uses_duration_windows:
            window_count = int(asset["evidence_window_count"])
            profile = str(asset["evidence_sampling_profile"])
            if kind == "PHOTO":
                if is_v03 and duration_ms is not None:
                    raise ValueError(f"assets[{index}].original_duration_ms must be null for PHOTO")
                expected_windows, expected_frames = 1, 1
                expected_profile = "PHOTO_SINGLE_FRAME"
            else:
                if is_v03:
                    _v03_integer(
                        duration_ms,
                        f"assets[{index}].original_duration_ms",
                        minimum=1,
                    )
                if duration_ms is None or int(duration_ms) <= 0:
                    raise ValueError(f"assets[{index}] video duration must be positive")
                duration_value = int(duration_ms)
                expected_windows = 1 if duration_value <= 10_000 else 2 if duration_value <= 30_000 else 4 if duration_value <= 90_000 else 6
                expected_frames = 3 if expected_windows == 1 else expected_windows * 2
                expected_profile = (
                    "VIDEO_SINGLE_WINDOW_THREE"
                    if expected_windows == 1 else "VIDEO_MULTI_WINDOW_TWO_PER_WINDOW"
                )
            if window_count != expected_windows or len(frames) != expected_frames or profile != expected_profile:
                raise ValueError(f"assets[{index}] does not match the duration-aware Evidence profile")
        else:
            if len(frames) != 3:
                raise ValueError(f"assets[{index}] must contain exactly three frames")
            if sorted(int(frame["canonical_offset_ms"]) for frame in frames) != list(FRAME_OFFSETS_MS):
                raise ValueError(f"assets[{index}] frame offsets do not match the canonical positions")
        for frame_index, frame in enumerate(frames):
            if not isinstance(frame, dict):
                raise ValueError(f"assets[{index}].frames[{frame_index}] must be an object")
            required_frame_fields = [
                "frame_id", "canonical_offset_ms", "source_timestamp_ms", "relative_path",
                "sha256", "width", "height", "spatial_transform",
            ]
            if uses_duration_windows:
                required_frame_fields.extend(("window_index", "window_count", "sample_role"))
            _required(frame, required_frame_fields, f"assets[{index}].frames[{frame_index}]")
            if is_v03:
                location = f"assets[{index}].frames[{frame_index}]"
                _reject_unexpected(frame, _APP_LIBRARY_BUNDLE_V03_FRAME_FIELDS, location)
                _v03_nonempty_string(frame["frame_id"], f"{location}.frame_id")
                _v03_integer(frame["window_index"], f"{location}.window_index")
                if frame["window_index"] > 5:
                    raise ValueError(f"{location}.window_index must be <= 5")
                _v03_integer(frame["window_count"], f"{location}.window_count", minimum=1)
                if frame["window_count"] not in (1, 2, 4, 6):
                    raise ValueError(f"{location}.window_count is invalid")
                allowed_roles = {
                    "PHOTO_REPRESENTATIVE", "WINDOW_EARLY", "WINDOW_MIDDLE", "WINDOW_LATE",
                }
                if frame["sample_role"] not in allowed_roles:
                    raise ValueError(f"{location}.sample_role is invalid")
                if frame["canonical_offset_ms"] not in FRAME_OFFSETS_MS:
                    raise ValueError(f"{location}.canonical_offset_ms is invalid")
                if frame["source_timestamp_ms"] is not None:
                    _v03_integer(
                        frame["source_timestamp_ms"],
                        f"{location}.source_timestamp_ms",
                    )
                _v03_nonempty_string(frame["relative_path"], f"{location}.relative_path")
                _v03_sha256(frame["sha256"], f"{location}.sha256")
                if frame["width"] != 768 or frame["height"] != 1024:
                    raise ValueError(f"{location} must use 768x1024 Evidence")
                if frame["spatial_transform"] != spatial_transform:
                    raise ValueError(f"{location}.spatial_transform is invalid")
            frame_id = str(frame["frame_id"])
            if frame_id in frame_ids:
                raise ValueError(f"duplicate frame_id: {frame_id}")
            frame_ids.add(frame_id)
            frame_path = _contained_file(root, frame["relative_path"], f"assets[{index}].frames[{frame_index}].relative_path")
            timestamp = frame["source_timestamp_ms"]
            timestamp_valid = timestamp is None if kind == "PHOTO" else (
                timestamp is not None and duration_ms is not None and 0 <= int(timestamp) <= int(duration_ms)
            )
            frame_checks.append(
                sha256_file(frame_path) == frame["sha256"]
                and int(frame["width"]) == width and int(frame["height"]) == height
                and frame["spatial_transform"] == normalization["spatial_transform"]
                and timestamp_valid
            )
            frame_count += 1
        if uses_duration_windows:
            if any(int(frame["window_count"]) != window_count for frame in frames):
                raise ValueError(f"assets[{index}] frame window_count mismatch")
            if sorted(int(frame["window_index"]) for frame in frames) != (
                [0] if kind == "PHOTO" else [0, 0, 0] if window_count == 1 else [value for value in range(window_count) for _ in range(2)]
            ):
                raise ValueError(f"assets[{index}] frame windows are incomplete")
            expected_offsets = (
                [4_500] if kind == "PHOTO" else list(FRAME_OFFSETS_MS) if window_count == 1
                else [value for _ in range(window_count) for value in (1_500, 7_500)]
            )
            if [int(frame["canonical_offset_ms"]) for frame in frames] != expected_offsets:
                raise ValueError(f"assets[{index}] frame offsets do not match their logical Windows")
            if is_v03:
                expected_roles = (
                    ["PHOTO_REPRESENTATIVE"]
                    if kind == "PHOTO"
                    else ["WINDOW_EARLY", "WINDOW_MIDDLE", "WINDOW_LATE"]
                    if window_count == 1
                    else [role for _ in range(window_count) for role in ("WINDOW_EARLY", "WINDOW_LATE")]
                )
                if [frame["sample_role"] for frame in frames] != expected_roles:
                    raise ValueError(f"assets[{index}] frame sample roles do not match their logical Windows")
            if kind == "VIDEO":
                timestamps = [int(frame["source_timestamp_ms"]) for frame in frames]
                if timestamps != sorted(timestamps) or len(set(timestamps)) != len(timestamps):
                    raise ValueError(f"assets[{index}] source timestamps must be unique chronology")
    global_checks.update({
        "asset_ids_unique": len(asset_ids) == len(assets),
        "frame_ids_unique": len(frame_ids) == frame_count,
        "evidence_frame_cardinality": (
            frame_count == sum(len(asset["frames"]) for asset in assets)
            if uses_duration_windows else frame_count == len(assets) * 3
        ),
        "evidence_hash_geometry_and_timestamps": all(frame_checks),
        "arbitrary_photo_video_supported": kinds.issubset({"PHOTO", "VIDEO"}),
        "original_media_not_required_in_bundle": all(asset.get("original_included") is False for asset in assets),
    })
    failed = [name for name, passed in global_checks.items() if not passed]
    if failed:
        raise ValueError(f"App Library bundle gate failed: {', '.join(failed)}")
    validation = {
        "validation_version": (
            "APP_LIBRARY_BUNDLE_GATE_V04" if is_v04 else "APP_LIBRARY_BUNDLE_GATE_V03"
            if is_v03 else "APP_LIBRARY_BUNDLE_GATE_V02"
            if uses_duration_windows else "APP_LIBRARY_BUNDLE_GATE_V01"
        ), "passed": True,
        "checks": global_checks, "session_id": session["session_id"],
        "asset_count": len(assets), "frame_count": frame_count,
        "media_kinds": sorted(kinds),
        "evidence_profile_version": (
            PHONE_TEST_EVIDENCE_PROFILE_V01
            if uses_duration_windows else "FIXED_THREE_FRAME_V01"
        ),
    }
    return ImportedEvidenceBundle(manifest_path, manifest, validation)


def load_any_bundle(manifest_path: Path) -> Union[ImportedBundle, ImportedEvidenceBundle]:
    header = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = header.get("bundle_version")
    if version == BUNDLE_VERSION:
        return load_bundle(manifest_path)
    if version in _APP_LIBRARY_BUNDLE_VERSIONS:
        return load_app_library_bundle(manifest_path)
    raise ValueError(f"unsupported bundle_version: {version}")


def run_bundle_e00(manifest_path: Path, artifact_root: Path) -> Path:
    bundle = load_any_bundle(manifest_path)
    if isinstance(bundle, ImportedEvidenceBundle):
        if bundle.manifest["bundle_version"] in (APP_LIBRARY_BUNDLE_VERSION_V03, APP_LIBRARY_BUNDLE_VERSION_V04):
            raise ValueError(
                "App Library Bundle V03/V04 cannot run the historical E00 smoke because "
                "E00 synthesizes time-shaped 120-second offsets"
            )
        return run_preextracted_evidence_smoke(
            bundle.manifest_path, bundle.manifest, bundle.validation, artifact_root
        )
    context = {
        "input_contract": BUNDLE_VERSION,
        "bundle_manifest_sha256": sha256_file(bundle.manifest_path),
        "session": bundle.manifest["session"],
        "device": bundle.manifest["device"],
        "media_profile": bundle.manifest["media_profile"],
        "bundle_validation": bundle.validation,
    }
    return run_smoke(bundle.source_path, artifact_root, experiment_context=context)
