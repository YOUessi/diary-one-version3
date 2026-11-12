"""V02 publication gate: verify actual clip ownership and per-chapter JPEG scope.

Independent from the model. No semantic assertion about place names or stories.
V01 contracts stay frozen and are validated by their original defaults.
"""
from __future__ import annotations

import json
from pathlib import Path

from shared.direct_result_contract import validate_direct_result, require

SCHEMA_VERSION = "DIARY_ONE_PLANNER_GALLERY_CHAPTER_V02"
PIPELINE_VERSION = "X02_PLANNER_GALLERY_CHAPTER_V02"
EDITOR_POLICY = "PLANNER_GALLERY_SCOPED_EDITOR_V02"
MAX_CALLS = 30


def validate_planner_gallery_result(result: dict, manifest_bytes: bytes,
                                    bundle_dir: Path | None) -> None:
    require(result.get("schema_version") == SCHEMA_VERSION, "v02_schema_version")
    require(result.get("editor_policy") == EDITOR_POLICY, "v02_editor_policy")
    require(result.get("experimental") is True
            and result.get("production_ready") is False, "v02_must_remain_experimental")
    validate_direct_result(
        result, manifest_bytes, bundle_dir,
        expected_pipeline=PIPELINE_VERSION,
        id_prefix="planner_gallery_v02:",
        max_gallery=20, max_calls=MAX_CALLS,
    )

    manifest = json.loads(manifest_bytes)
    assets = manifest["assets"]
    clips = len(assets)
    excluded = set(result["excluded_non_lived_frame_ids"])
    chapters = result["chapters"]
    decision = result["decision_trace"]
    trace = result["trace"]

    require(decision.get("clip_ownership") ==
            "EXPLICIT_CONTIGUOUS_ONE_CHAPTER_PER_CLIP", "clip_ownership_protocol")
    require(decision.get("semantic_copy_verified") is False
            and decision.get("visual_fact_reviewed") is False,
            "v02_must_not_claim_semantic_review")
    require(decision.get("no_staged_pipeline") is False, "v02_two_stage_identity")
    require(trace.get("execution_mode") ==
            "GLOBAL_PLANNER_SCOPED_GALLERY_WITH_BOUNDED_RETRY", "v02_execution_mode")
    require(len(chapters) >= 1 and len(chapters) <= 14, "chapter_count")

    intervals = decision.get("chapter_clip_intervals")
    hashes = decision.get("gallery_prompt_sha256")
    observed_counts = decision.get("gallery_model_input_frames")
    require(isinstance(intervals, list) and len(intervals) == len(chapters), "chapter_interval_count")
    require(isinstance(hashes, list) and len(hashes) == len(chapters), "gallery_prompt_count")
    require(isinstance(observed_counts, list) and len(observed_counts) == len(chapters),
            "gallery_frame_count_scope")

    # Every segment of the manifest receives one unique, contiguous owner:
    # start=previous_end+1; final end must equal number of submitted clips.
    previous = 0
    for idx, (ch, interval) in enumerate(zip(chapters, intervals, strict=True), 1):
        require(isinstance(interval, dict)
                and interval.get("candidate_id") == ch.get("candidate_id") == f"C{idx:02d}",
                "candidate_chapter_order")
        start, end = ch.get("source_clip_start"), ch.get("source_clip_end")
        require(type(start) is int and type(end) is int, "chapter_clip_type")
        require(start == previous + 1 and start <= end <= clips,
                "chapter_interval_overlap_or_gap")
        require(interval.get("start_clip") == start and interval.get("end_clip") == end,
                "chapter_interval_mismatch")

        eligible = [(a["asset_id"], f["frame_id"]) for a in assets[start - 1:end]
                    for f in a["frames"] if f["frame_id"] not in excluded]
        expected = [fid for _, fid in eligible]
        require(bool(expected), "chapter_without_lived_jpeg_evidence")
        require(ch["experience_frame_ids"] == expected, "chapter_experience_not_entire_scope")
        require(observed_counts[idx - 1] == len(expected), "chapter_gallery_input_count_mismatch")
        require(ch["source_asset_ids"] == sorted({source for source, _ in eligible}),
                "chapter_source_assets_not_bound")
        allowed = set(expected)
        require(ch["hero_frame_id"] in allowed, "hero_outside_owned_clip")
        require(ch["selected_media"][0]["role"] == "HERO", "hero_not_first_gallery")
        for media in ch["selected_media"]:
            require(media["representative_frame_id"] in allowed, "gallery_outside_owned_clip")
        for moment in ch["key_moments"]:
            require(set(moment["frame_ids"]) <= allowed, "key_moment_outside_owned_clip")
        previous = end
    require(previous == clips, "last_chapter_must_own_tail_clip")

    # All attempts remain billable and traceable. Gallery retries are per
    # chapter; there can be 1..2 plan calls and 1..2 gallery calls per chapter.
    stage_metrics = trace["stage_metrics"]
    count = trace["model_calls"]
    require(len(stage_metrics) == count and len(trace["request_ids"]) == count,
            "v02_model_call_accounting")
    stage_names = [item.get("stage") for item in stage_metrics]
    n_plan = sum(x == "DIRECT_VLM_CHAPTER_PLANNER_V02" for x in stage_names)
    n_gallery = sum(x == "DIRECT_VLM_CHAPTER_GALLERY_V02" for x in stage_names)
    require(1 <= n_plan <= 2 and len(chapters) <= n_gallery <= 2 * len(chapters)
            and n_plan + n_gallery == count, "v02_stage_call_count")
    require(stage_names[:n_plan] == ["DIRECT_VLM_CHAPTER_PLANNER_V02"] * n_plan
            and all(x == "DIRECT_VLM_CHAPTER_GALLERY_V02" for x in stage_names[n_plan:]),
            "v02_stage_call_sequence")
    require(trace["request_ids"] == [item["request_id"] for item in stage_metrics],
            "v02_request_ids_do_not_match_stages")
    require(trace["input_tokens"] == sum(item["input_tokens"] for item in stage_metrics)
            and trace["output_tokens"] == sum(item["output_tokens"] for item in stage_metrics),
            "v02_usage_not_accounted")
