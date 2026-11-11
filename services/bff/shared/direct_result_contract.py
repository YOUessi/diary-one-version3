"""Input-bound publisher contract for direct VLM chapters (no forged S04 facts).

Only mechanical guarantees are claimed: exact uploaded JPEG provenance, valid
chapter/media references, no duplicate public covers, and stable session binding.
The VLM's narrative truth remains a separate semantic quality question.
"""
from __future__ import annotations
import hashlib
import json
import uuid
from pathlib import Path

from shared.evidence_input import validate_stored_evidence

SCHEMA_VERSION = "DIARY_ONE_DIRECT_VLM_CHAPTER_V01"
PIPELINE_VERSION = "X02_DIRECT_VLM_CHAPTER_V01"


def require(condition: bool, reason: str):
    if not condition:
        raise ValueError("direct_vlm:" + reason)


def app_asset_id(source: str) -> str:
    value = source[6:] if source.startswith("asset_") else source
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return value


def unique_ids(value, possible, reason: str, *, allow_empty=False) -> list[str]:
    require(isinstance(value, list) and (allow_empty or bool(value)), reason)
    require(all(isinstance(x, str) and x for x in value), reason)
    require(len(value) == len(set(value)) and set(value) <= set(possible), reason)
    return value


def validate_direct_result(
    result: dict, manifest_bytes: bytes, bundle_dir: Path | None,
    *, expected_pipeline: str = PIPELINE_VERSION,
    id_prefix: str = "direct_vlm_v01:", max_gallery: int = 8,
    max_calls: int = 2,
) -> None:
    """Raise ValueError on all structural, lineage, upload, cover, or order mismatches."""
    require(isinstance(manifest_bytes, bytes), "missing_manifest")
    require(bundle_dir is not None and Path(bundle_dir).is_dir(), "missing_original_jpegs")
    validate_stored_evidence(manifest_bytes, Path(bundle_dir))
    manifest = json.loads(manifest_bytes)
    require(result["bundle_manifest_sha256"] == hashlib.sha256(manifest_bytes).hexdigest(), "manifest_sha")
    require(result["session_id"] == manifest["session"]["session_id"], "session")
    require(result["trace"]["pipeline_version"] == expected_pipeline, "pipeline")
    require(not result.get("dev_lite_fallback") and result["delivery_state"] == "READY_PRIMARY_COPY", "not_ready")
    assets, frames, app_ids = {}, {}, set()
    for asset in manifest["assets"]:
        source = asset["asset_id"]
        aid = app_asset_id(source)
        require(source not in assets and aid not in app_ids, "ambiguous_asset_identity")
        assets[source] = asset
        app_ids.add(aid)
        for frame in asset["frames"]:
            fid = frame["frame_id"]
            require(fid not in frames, "duplicate_input_frame")
            frames[fid] = (source, frame)
    require(0 < len(frames) <= 250, "image_count")
    require(result["decision_trace"]["input_coverage"]["frames_submitted"] == len(frames), "missing_submitted_frames")
    require(result["decision_trace"]["input_coverage"]["clips_received"] == len(assets), "missing_submitted_clips")
    actual_bytes = sum((Path(bundle_dir) / f["relative_path"]).stat().st_size for source, f in frames.values())
    require(result["decision_trace"]["input_coverage"]["image_bytes"] == actual_bytes, "image_bytes")
    require(result["coverage_status"] == "INPUT_ALL_FRAMES_SUBMITTED"
            and result["unresolved_asset_ids"] == [], "partial_input")
    require(result["ahas"] == result["observations"] == result["moments"] == [], "staged_results_mixed_in")
    known = set(frames)
    excluded = set(unique_ids(result["excluded_non_lived_frame_ids"], known, "excluded", allow_empty=True))
    gallery_used, chapter_ids, candidate_ids = set(), set(), set()
    for chapter in result["chapters"]:
        cid = chapter["id"]
        require(cid not in chapter_ids, "duplicate_chapter_id")
        chapter_ids.add(cid)
        candidate = chapter.get("candidate_id")
        require(isinstance(candidate, str) and candidate not in candidate_ids, "duplicate_candidate_id")
        candidate_ids.add(candidate)
        require(cid == str(uuid.uuid5(uuid.UUID(result["session_id"]), id_prefix + candidate)),
                "non_deterministic_chapter_id")
        hero = chapter["hero_frame_id"]
        gallery = chapter["selected_media"]
        require(1 <= len(gallery) <= max_gallery, "too_many_gallery_frames")
        hero_media = [item for item in gallery if item["role"] == "HERO"]
        require(len(hero_media) == 1 and hero_media[0]["representative_frame_id"] == hero, "hero_mismatch")
        require(hero_media[0]["asset_id"] == chapter["hero_asset_id"], "hero_asset_mismatch")
        chapter_frames = unique_ids(chapter["experience_frame_ids"], known, "experience_frame_ids")
        moment_frames = []
        for moment in chapter["key_moments"]:
            moment_frames += unique_ids(moment["frame_ids"], known, "moment_frame_ids")
        require(not (set(chapter_frames) | set(moment_frames)) & excluded, "excluded_in_evidence")
        require(chapter["highlights"] == chapter["claims"] == chapter["moment_ids"] == [], "legacy_fake_facts")
        for media in gallery:
            fid = media["representative_frame_id"]
            require(fid in known and fid not in excluded and fid not in gallery_used, "gallery_frame_invalid_or_reused")
            gallery_used.add(fid)
            source, frame = frames[fid]
            require(media["source_asset_id"] == source and media["asset_id"] == app_asset_id(source),
                    "selected_media_asset_binding")
            require(media["media_kind"] == assets[source]["media_kind"], "selected_media_kind")
            require(media["evidence_frame_ids"] == [fid], "selected_media_not_frame_bound")
            require(media["role"] in ("HERO", "SUPPORT"), "selected_media_role")
            kind = assets[source]["media_kind"]
            if kind == "PHOTO":
                require(media["range_basis"] == "STILL_IMAGE"
                        and media["start_ms"] is None and media["end_ms"] is None
                        and media["focus_pts_ms"] is None, "photo_video_range")
            else:
                duration = assets[source].get("original_duration_ms")
                if isinstance(duration, int) and duration > 0:
                    require(media["range_basis"] == "WHOLE_SOURCE_CLIP"
                            and media["start_ms"] == 0 and media["end_ms"] == duration
                            and media["focus_pts_ms"] == frame.get("source_timestamp_ms"),
                            "video_range_not_source_bound")
                else:
                    require(media["range_basis"] == "EVIDENCE_ONLY_NO_VIDEO_RANGE"
                            and media["start_ms"] is None and media["end_ms"] is None
                            and media["focus_pts_ms"] is None, "unknown_duration_invented_range")
        require(hero in gallery_used, "missing_hero_gallery")
    expected = set(chapter_ids)
    actual = set()
    for outcome in result["selected_memory_outcomes"]:
        require(outcome["memory_type"] == "CHAPTER"
                and outcome["visibility_state"] == "VISIBLE_PREVIEW"
                and outcome["memory_id"] in expected
                and outcome["memory_id"] not in actual, "outcome_mismatch")
        actual.add(outcome["memory_id"])
    require(actual == expected and 1 <= result["trace"]["model_calls"] <= max_calls, "missing_outcomes_or_calls")
    require(len(result["trace"]["request_ids"]) == result["trace"]["model_calls"], "request_id_accounting")
