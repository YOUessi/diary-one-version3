"""Offline-only audit of the nine specified frozen-baseline review slots.

Reads experiment evidence without mutating it. Only the two derived report paths
below are regenerated. Never calls a model or uses cached semantic outputs.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_64_repeat_review"
JSON_REPORT = AREA / "codex_summary.json"
MD_REPORT = ROOT / "docs/codex_V1_64_RUN_MATRIX.md"
HASH_CACHE: dict[str, str] = {}


def read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        # An active writer can be between file creation and complete JSON output.
        return {}


def sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    key = str(path.resolve())
    if key not in HASH_CACHE:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        HASH_CACHE[key] = digest.hexdigest()
    return HASH_CACHE[key]


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def visible(text) -> int:
    return sum(not char.isspace() for char in str(text or ""))


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def aggregate_calls(calls: list[dict]) -> dict:
    known = [call for call in calls if call["usage_known"]]
    costs = [call["estimated_tiered_cost_cny"] for call in calls
             if call["estimated_tiered_cost_cny"] is not None]
    return {
        "attempted_call_count": len(calls),
        "completed_call_count": sum(c["status"] == "COMPLETED" for c in calls),
        "failed_call_count": sum(c["status"] == "FAILED" for c in calls),
        "in_progress_call_count": sum(c["status"] == "IN_PROGRESS" for c in calls),
        "http_429_count": sum(c["http_status"] == 429 for c in calls),
        "known_duration_seconds": round(sum(c["duration_seconds"] or 0 for c in calls), 3),
        "unknown_duration_count": sum(c["duration_seconds"] is None for c in calls),
        "known_input_tokens": sum(c["input_tokens"] for c in known),
        "known_output_tokens": sum(c["output_tokens"] for c in known),
        "known_total_tokens": sum(c["input_tokens"] + c["output_tokens"] for c in known),
        "usage_known_call_count": len(known),
        "usage_unknown_call_count": len(calls) - len(known),
        "known_estimated_cost_cny": round(sum(costs), 9),
        "cost_unknown_call_count": len(calls) - len(costs),
        "cost_is_complete": len(costs) == len(calls),
        "cost_basis": "RECORDED_BEIJING_TIERED_RATE_SNAPSHOT_NOT_BILLING_INVOICE",
    }


def call_records(directory: Path, report: dict) -> list[dict]:
    recorded = {int(c["index"]): c for c in report.get("stage_calls", []) if isinstance(c, dict) and c.get("index")}
    calls_dir = directory / "codex_stage_calls"
    indices = set(recorded)
    # One directory only. No recursive traversal or initialization-failure archives.
    for path in calls_dir.glob("codex_*_request.json"):
        try:
            indices.add(int(path.name.split("_")[1]))
        except ValueError:
            pass
    result = []
    for index in sorted(indices):
        request = read(calls_dir / f"codex_{index:03d}_request.json")
        response = read(calls_dir / f"codex_{index:03d}_response.json")
        source = response or recorded.get(index, {})
        provider = read(calls_dir / f"codex_{index:03d}_provider.json")
        usage = (provider.get("payload") or {}).get("usage") or {}
        inp, out = number(usage.get("prompt_tokens")), number(usage.get("completion_tokens"))
        known = inp is not None and out is not None
        metric = source.get("metric") or {}
        stage = source.get("stage") or request.get("stage") or "UNKNOWN"
        group = "S04_PERCEPTION" if stage.startswith("S04_") else "S10_MEDIA_SELECTION" if stage.startswith("S10_") else stage
        result.append({
            "index": index, "stage": stage, "stage_group": group,
            "status": source.get("status", "IN_PROGRESS"),
            "duration_seconds": number(source.get("duration_seconds")),
            "http_status": provider.get("http_status"),
            "error_code": source.get("code"),
            "request_id": metric.get("request_id") or (provider.get("payload") or {}).get("id"),
            "usage_known": known, "usage_source": "PROVIDER_BODY" if known else "UNKNOWN",
            "input_tokens": inp if known else None, "output_tokens": out if known else None,
            "reported_metric_input_tokens": metric.get("input_tokens"),
            "reported_metric_output_tokens": metric.get("output_tokens"),
            "estimated_tiered_cost_cny": number(source.get("estimated_tiered_cost_cny")) if known else None,
            "reported_flat_cost_usd": metric.get("estimated_cost_usd"),
            "metric_pricing_basis": metric.get("pricing_basis"),
            "model_frame_count": metric.get("model_frame_count"),
            "request_body_sha256": provider.get("request_body_sha256"),
            "source_prefix": relative(calls_dir / f"codex_{index:03d}"),
        })
    return result


def inspect_input(directory: Path, pack: dict) -> tuple[dict, dict]:
    manifest_path = directory / "codex_manifest.json"
    manifest = read(manifest_path)
    norm = read(directory / "codex_normalization.json")
    assets = manifest.get("assets", [])
    inventory = pack.get("assets", [])
    source_by_hash = {item["sha256"]: item["relative_path"] for item in inventory}
    mapping, originals, frames, mismatches = {}, [], [], []
    for asset in assets:
        original_sha = asset.get("original_sha256")
        name = source_by_hash.get(original_sha, asset.get("source_display_name", asset["asset_id"]))
        mapping[asset["asset_id"]] = name
        mapping[asset["asset_id"].removeprefix("asset_")] = name
        originals.append([name, original_sha])
        for frame in asset.get("frames", []):
            frames.append([name, frame.get("frame_id"), frame.get("sha256")])
            actual = sha(directory / frame["relative_path"])
            if actual != frame.get("sha256"):
                mismatches.append(frame["relative_path"])
    expected_originals = [[item["relative_path"], item["sha256"]] for item in inventory]
    original_mismatches = [item["relative_path"] for item in inventory
                           if sha(Path(pack["source_root"]) / item["relative_path"]) != item["sha256"]]
    info = {
        "manifest_present": bool(manifest), "normalization_status": norm.get("status"),
        "asset_count": len(assets) if manifest else None,
        "photo_count": sum(a.get("media_kind") == "PHOTO" for a in assets) if manifest else None,
        "video_count": sum(a.get("media_kind") == "VIDEO" for a in assets) if manifest else None,
        "frame_count": len(frames) if manifest else None,
        "bundle_version": manifest.get("bundle_version"),
        "spatial_transforms": sorted({f.get("spatial_transform", "UNKNOWN") for a in assets for f in a.get("frames", [])}),
        "manifest_sha256": sha(manifest_path),
        "manifest_matches_normalization_record": sha(manifest_path) == norm.get("manifest_sha256") if manifest and norm else None,
        "original_inventory_matches_preparation": originals == expected_originals if manifest else None,
        "original_file_hash_mismatches": original_mismatches,
        "evidence_file_hash_mismatches": mismatches,
        "ordered_original_hash_fingerprint": fingerprint(originals) if manifest else None,
        "ordered_frame_hash_fingerprint": fingerprint(frames) if manifest else None,
        "source_inventory_sha256": norm.get("sourceInventorySha256"),
        "normalizer_module_hashes": norm.get("moduleHashes"),
        "capture_time_used": norm.get("captureTimeUsed"),
        "fresh_decode_and_extraction": norm.get("freshDecodeAndExtraction"),
        "normalization_seconds": round(norm["totalPreparationMs"] / 1000, 3) if number(norm.get("totalPreparationMs")) is not None else None,
        "frame_extraction_seconds": round(norm["buildEvidenceMs"] / 1000, 3) if number(norm.get("buildEvidenceMs")) is not None else None,
        "evidence_bytes": norm.get("evidenceBytes"),
        "source_manifest": relative(manifest_path),
    }
    return info, mapping


def cards_and_reuse(result: dict, mapping: dict) -> tuple[list[dict], list[dict]]:
    cards = []
    for key, kind in (("chapters", "CHAPTER"), ("ahas", "AHA")):
        for index, card in enumerate(result.get(key) or [], 1):
            selected = card.get("selected_media") or []
            ids = [media.get("source_asset_id") or media.get("asset_id") for media in selected]
            cards.append({
                "kind": kind, "ordinal": index, "id": card.get("id"), "candidate_id": card.get("candidate_id"),
                "title": card.get("title", ""), "story": card.get("story", ""),
                "title_visible_characters": visible(card.get("title")), "story_visible_characters": visible(card.get("story")),
                "tags": card.get("tags", []), "surface_source": card.get("surface_source"),
                "publication_status": card.get("publication_status"),
                "selected_asset_ids": ids, "selected_relative_paths": [mapping.get(a, a) for a in ids],
                "selected_media_kinds": [media.get("media_kind") for media in selected],
                "fact_ids": [claim.get("fact_id") for claim in card.get("claims", []) if claim.get("fact_id")],
                "storyline_identity": card.get("storyline_identity"),
            })
    overlaps = []
    for first, second in combinations(cards, 2):
        assets = sorted(set(first["selected_relative_paths"]) & set(second["selected_relative_paths"]))
        facts = sorted(set(first["fact_ids"]) & set(second["fact_ids"]))
        if assets or facts:
            overlaps.append({"first": {k: first[k] for k in ("kind", "ordinal", "id", "title")},
                             "second": {k: second[k] for k in ("kind", "ordinal", "id", "title")},
                             "shared_relative_paths": assets, "shared_fact_ids": facts,
                             "semantic_error_status": "NOT_AUTOMATICALLY_JUDGED"})
    return cards, overlaps


def completed_diagnostics(directory: Path, result: dict, cards: list[dict], calls: list[dict]) -> dict:
    """Observed counters only: no semantic quality verdict and no new gates."""
    trace = result.get("decision_trace") or {}
    native = [item for item in trace.get("aha_candidates", [])
              if item.get("proposal_source") == "MODEL_STRUCTURE_PROPOSAL"]
    raw_native = []
    structure_outputs_found = 0
    for call in calls:
        if call["stage"] != "S05_S07_STRUCTURE_PROPOSAL":
            continue
        response = read(directory / "codex_stage_calls" / f"codex_{call['index']:03d}_response.json")
        output = response.get("output") or {}
        if isinstance(output.get("aha_proposals"), list):
            raw_native.extend(output["aha_proposals"])
            structure_outputs_found += 1
    rejected = [item for item in native if item.get("validation_status") == "REJECTED"]
    origin_rows = []
    for card in cards:
        if card["kind"] != "AHA":
            continue
        matches = [item for item in trace.get("aha_candidates", [])
                   if item.get("candidate_id") == card["candidate_id"] and item.get("validation_status") == "PASSED"]
        sources = sorted({item.get("proposal_source", "UNKNOWN") for item in matches})
        origin_rows.append({"id": card["id"], "candidate_id": card["candidate_id"], "title": card["title"],
                            "source": "+".join(sources) if sources else "UNRESOLVED",
                            "matched_trace_entries": matches})
    published = {c["candidate_id"]: c for c in cards if c["kind"] == "CHAPTER"
                 and c["publication_status"] == "STAGED_PREVIEW_VALIDATED"}
    s10 = trace.get("s10_chapter_media") or []
    exact_three = [item for item in s10 if item.get("candidate_content_unit_count") == 3
                   and (item.get("display_selection") or {}).get("comparison_attempted") is False]
    return {
        "native_aha_proposal_count": len(raw_native) if structure_outputs_found else None,
        "native_aha_trace_entry_count": len(native),
        "native_proposal_and_trace_counts_match": len(raw_native) == len(native) if structure_outputs_found else None,
        "native_aha_validation_status_counts": dict(Counter(item.get("validation_status", "UNKNOWN") for item in native)),
        "native_aha_rejected_count": len(rejected),
        "native_aha_rejection_reason_counts": dict(Counter(reason for item in rejected for reason in item.get("reason_codes", []))),
        "native_aha_rejection_detail_counts": dict(Counter(item.get("detail") for item in rejected if item.get("detail"))),
        "native_aha_raw_proposals": raw_native,
        "native_aha_trace_entries": native,
        "final_aha_source_counts": dict(Counter(item["source"] for item in origin_rows)),
        "final_aha_origins": origin_rows,
        "s10_chapter_selection_count": len(s10),
        "s10_exact_three_no_comparison_count": len(exact_three),
        "published_chapter_exact_three_no_comparison_count": sum(item.get("candidate_id") in published for item in exact_three),
        "s10_exact_three_no_comparison_cases": [
            {"candidate_id": item.get("candidate_id"), "published_title": published.get(item.get("candidate_id"), {}).get("title"),
             "selection_source": (item.get("display_selection") or {}).get("selection_source")}
            for item in exact_three],
        "final_aha_count": sum(card["kind"] == "AHA" for card in cards),
        "final_chapter_count": sum(card["kind"] == "CHAPTER" for card in cards),
        "aha_story_over_24_count": sum(card["kind"] == "AHA" and card["story_visible_characters"] > 24 for card in cards),
        "chapter_story_over_48_count": sum(card["kind"] == "CHAPTER" and card["story_visible_characters"] > 48 for card in cards),
        "writer_length_by_source": length_by_source(cards),
        "length_scope": "OBSERVATIONAL_COUNTS_NON_WHITESPACE_UNICODE_CHARS_INCLUDING_PUNCTUATION_NOT_NEW_REJECTION_GATES",
    }


def length_by_source(cards: list[dict]) -> dict:
    groups = defaultdict(list)
    for card in cards:
        groups[card.get("surface_source") or "UNKNOWN"].append(card)
    return {source: {
        "aha_count": sum(card["kind"] == "AHA" for card in items),
        "chapter_count": sum(card["kind"] == "CHAPTER" for card in items),
        "aha_story_over_24_count": sum(card["kind"] == "AHA" and card["story_visible_characters"] > 24 for card in items),
        "chapter_story_over_48_count": sum(card["kind"] == "CHAPTER" and card["story_visible_characters"] > 48 for card in items),
        "aha_story_lengths": [card["story_visible_characters"] for card in items if card["kind"] == "AHA"],
        "chapter_story_lengths": [card["story_visible_characters"] for card in items if card["kind"] == "CHAPTER"],
    } for source, items in groups.items()}


def aggregate_completed_diagnostics(runs: list[dict], include_blocked: bool = False) -> dict:
    completed = [run for run in runs if run["returned_result_available"] if include_blocked or run["quality_result_available"]]
    scalar_keys = ("native_aha_trace_entry_count", "native_aha_rejected_count", "s10_chapter_selection_count",
                   "s10_exact_three_no_comparison_count", "published_chapter_exact_three_no_comparison_count",
                   "final_aha_count", "final_chapter_count", "aha_story_over_24_count", "chapter_story_over_48_count")
    histogram_keys = ("native_aha_validation_status_counts", "native_aha_rejection_reason_counts",
                      "native_aha_rejection_detail_counts", "final_aha_source_counts")
    result = {"completed_run_count": len(completed),
              "run_scope": "RETURNED_RESULTS_INCLUDING_BLOCKED_INTERNAL_CANDIDATES" if include_blocked else "DELIVERABLE_RESULTS_COMPLETE_COVERAGE_ONLY",
              "independent_packs_with_completed_runs": len({run["pack_id"] for run in completed}),
              "denominator_note": "REPEATS_ARE_NOT_INDEPENDENT_USERS_AND_COUNTS_ARE_NOT_QUALITY_SCORES",
              "known_native_aha_proposal_count": sum(run["completed_diagnostics"]["native_aha_proposal_count"] or 0 for run in completed),
              "native_proposal_count_unknown_run_count": sum(run["completed_diagnostics"]["native_aha_proposal_count"] is None for run in completed)}
    for key in scalar_keys:
        result[key] = sum(run["completed_diagnostics"][key] for run in completed)
    for key in histogram_keys:
        counter = Counter()
        for run in completed:
            counter.update(run["completed_diagnostics"][key])
        result[key] = dict(counter)
    result["writer_length_by_source"] = length_by_source([card for run in completed for card in run["cards"]])
    return result


def timing_totals(runs: list[dict]) -> dict:
    timed = [run for run in runs if number(run["wall_duration_seconds"]) is not None]
    wall = sum(run["wall_duration_seconds"] for run in timed)
    local = sum(run["inputs"]["normalization_seconds"] or 0 for run in timed)
    groups = defaultdict(list)
    for run in timed:
        for call in run["calls"]:
            groups[call["stage_group"]].append(call)
    all_metrics = aggregate_calls([call for run in timed for call in run["calls"]])
    stages = {}
    for stage, calls in groups.items():
        metrics = aggregate_calls(calls)
        stages[stage] = {
            **metrics,
            "percent_of_algorithm_wall_time": round(100 * metrics["known_duration_seconds"] / wall, 3) if wall else None,
            "percent_of_known_tokens": round(100 * metrics["known_total_tokens"] / all_metrics["known_total_tokens"], 3) if all_metrics["known_total_tokens"] else None,
            "percent_of_known_estimated_cost": round(100 * metrics["known_estimated_cost_cny"] / all_metrics["known_estimated_cost_cny"], 3) if all_metrics["known_estimated_cost_cny"] else None,
        }
    return {
        "timed_run_count": len(timed), "algorithm_wall_seconds_sum": round(wall, 3),
        "local_normalization_seconds_sum": round(local, 3),
        "end_to_end_component_seconds_sum": round(wall + local, 3),
        "definition": "SUM_OF_LOCAL_NORMALIZATION_AND_ALGORITHM_WALL_NOT_EXPERIMENT_MAKESPAN_OR_UI_LATENCY",
        "stage_totals": stages,
    }


def inspect_round(pack: dict, round_number: int) -> dict:
    directory = AREA / f"pack_{pack['pack_id']}" / f"round_{round_number}"
    report_path = directory / "codex_full_run.json"
    report = read(report_path)
    result = report.get("result") or {}
    trace = result.get("decision_trace") or {}
    inputs, mapping = inspect_input(directory, pack)
    calls = call_records(directory, report)
    if report.get("status") == "FAILED":
        status = "FAILED_HTTP_429" if report.get("error_code") == "MODEL_HTTP_429" else "FAILED_OTHER"
    elif report.get("status") == "RETURNED" and result:
        status = "COMPLETED_RESULT"
    elif report.get("status") == "RETURNED":
        status = "RETURNED_EMPTY_RESULT"
    elif calls:
        status = "IN_PROGRESS_NO_FINAL_REPORT"
    elif report_path.exists():
        status = "REPORT_UNREADABLE_OR_INCOMPLETE"
    else:
        status = "PREPARED_NOT_EXECUTED" if inputs["manifest_present"] else "NOT_PREPARED"
    cards, overlaps = cards_and_reuse(result, mapping)
    delivery, coverage = result.get("delivery_state"), result.get("coverage_status")
    failed_calls = [call for call in calls if call["status"] == "FAILED"]
    failed_perception = [call for call in failed_calls if call["stage_group"] == "S04_PERCEPTION"]
    unresolved = result.get("unresolved_asset_ids") or []
    if not result:
        delivery_class = "NO_RESULT"
    elif delivery == "PIPELINE_BLOCKED" or coverage != "COMPLETE":
        delivery_class = "BLOCKED_INTERNAL_CANDIDATES"
    elif delivery == "READY_WITH_GROUNDED_COPY_FALLBACK" or any(c["surface_source"] != "MODEL_WRITER" for c in cards):
        delivery_class = "DEGRADED_DELIVERABLE"
    elif delivery == "READY_PRIMARY_COPY":
        delivery_class = "COMPLETE_DELIVERABLE"
    else:
        delivery_class = "UNCLASSIFIED_RETURNED_RESULT"
    deliverable = delivery_class in {"COMPLETE_DELIVERABLE", "DEGRADED_DELIVERABLE"}
    confounds = []
    if unresolved or coverage == "PARTIAL_UNRESOLVED":
        confounds.append("INCOMPLETE_OBSERVATION_INPUT_DO_NOT_ATTRIBUTE_OUTPUT_DIFFERENCES_TO_RANDOMNESS")
    if failed_perception:
        confounds.append("PERCEPTION_TRANSPORT_OR_PROVIDER_FAILURE")
    if any(call["stage"].startswith("S11_") for call in failed_calls):
        confounds.append("WRITER_REQUEST_FAILED_FALLBACK_IS_NOT_MODEL_WRITING")
    if any(c["surface_source"] != "MODEL_WRITER" for c in cards):
        confounds.append("MIXED_OR_FALLBACK_COPY_COMPARE_MODEL_WRITER_SEPARATELY")
    grouped = defaultdict(list)
    for call in calls:
        grouped[call["stage_group"]].append(call)
    return {
        "pack_id": pack["pack_id"], "round": round_number, "status": status,
        "returned_result_available": status == "COMPLETED_RESULT",
        "status_semantics": "COMPLETED_RESULT_MEANS_JSON_RETURNED_NOT_ALL_STAGES_SUCCEEDED",
        "delivery_class": delivery_class, "quality_result_available": deliverable, "user_rated": False,
        "all_attempted_model_calls_succeeded": not failed_calls if result else None,
        "unresolved_relative_paths": [mapping.get(asset_id, asset_id) for asset_id in unresolved],
        "writer_surface_source_counts": dict(Counter(c["surface_source"] or "UNKNOWN" for c in cards)),
        "stability_comparison_confounds": confounds,
        "published_chapter_count": sum(c["kind"] == "CHAPTER" and c["publication_status"] == "STAGED_PREVIEW_VALIDATED" for c in cards) if result else None,
        "published_aha_count": sum(c["kind"] == "AHA" and c["publication_status"] == "STAGED_PREVIEW_VALIDATED" for c in cards) if result else None,
        "source_run": relative(report_path), "started_at": report.get("started_at"), "completed_at": report.get("completed_at"),
        "wall_duration_seconds": report.get("duration_seconds"),
        "end_to_end_component_minutes": round((report["duration_seconds"] + inputs["normalization_seconds"]) / 60, 3)
        if number(report.get("duration_seconds")) is not None and inputs["normalization_seconds"] is not None else None,
        "algorithm_baseline_recorded": report.get("algorithm_baseline"),
        "actual_runtime_policies": trace.get("runtime_policies"),
        "planned_runtime_policies": report.get("runtime_policies"),
        "runtime_policies_match_plan": trace.get("runtime_policies") == report.get("runtime_policies") if trace.get("runtime_policies") else None,
        "run_mode": result.get("evaluation_run_mode") or report.get("evaluation_run_mode"),
        "cross_run_semantic_cache_used": result.get("cross_run_semantic_cache_used", report.get("cross_run_semantic_cache_used")),
        "delivery_state": result.get("delivery_state"), "coverage_status": result.get("coverage_status"),
        "chapter_count": len(result.get("chapters") or []) if result else None,
        "aha_count": len(result.get("ahas") or []) if result else None,
        "error_code": report.get("error_code"), "error_message": report.get("error_message"),
        "inputs": inputs, "call_metrics": aggregate_calls(calls),
        "stage_metrics": {stage: aggregate_calls(items) for stage, items in grouped.items()},
        "calls": calls, "cards": cards, "cross_card_reuse": overlaps,
        "decision_counts": trace.get("counts"), "stage_statuses": trace.get("stage_statuses"),
        "completed_diagnostics": completed_diagnostics(directory, result, cards, calls) if status == "COMPLETED_RESULT" else None,
    }


def fmt(value, digits=2):
    if value is None:
        return "—"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


DELIVERY_LABELS = {
    "NO_RESULT": "无结果",
    "BLOCKED_INTERNAL_CANDIDATES": "阻断，仅内部候选",
    "DEGRADED_DELIVERABLE": "降级可交付",
    "COMPLETE_DELIVERABLE": "完整可交付",
    "UNCLASSIFIED_RETURNED_RESULT": "已返回，交付状态待核查",
}


def render(summary: dict) -> str:
    lines = ["# Codex V1.64 重复测试：运行矩阵与可追溯性", "", f"离线生成时间：{summary['generated_at']}。算法基线仍为 V1.63；V1.64 是本轮评估记录版本。", "",
             "## 阅读边界", "",
             "- 分母是 **3 套真实素材**，每套计划重复 3 轮，共 9 个运行槽位；不是 9 个独立用户或 9 个独立素材样本。",
             "- 仅汇总 pack_1～3/round_1～3；不纳入工具初始化失误归档。没有最终结果的调用失败不记为 0 Chapter / 0 Aha。",
             "- HTTP 429 属于服务端请求限制/配额故障，不计为内容质量失败；其成功前置调用仍计入已知耗时与费用。",
             "- 缺失 provider usage 的请求按未知处理，不能因为程序填了 0 token 就认定免费。费用为记录内费率快照估算，不是账单。",
             "- 图片/事实复用只是核查线索，不自动判错；Chapter/Aha 数量不是质量分数。此处不作视觉质量或用户满意度结论。",
             "- `RETURNED` / `COMPLETED_RESULT` 仅表示函数返回了结构化结果，不等于全部阶段成功，也不等于可发布；需同时检查 delivery、coverage 与每张卡的 publication_status。",
             "- 上游观察请求失败造成的素材缺失、Writer 请求无响应和逐项 fallback 分开记录，不将这些差异归为纯模型随机性。普通字段降级可与完整素材覆盖并存。",
             "- 正文字数按非空白 Unicode 字符计数，含标点；不是 token 数，也不是英文生产环境长度合同。", "",
             "## 运行矩阵", "",
             "| 素材包/轮次 | 状态/交付分类 | 可交付 Chapter / Aha | 素材/帧 | 本地准备秒 | 算法墙钟秒 | 调用/429 | 已知输入/输出 token | usage 未知调用 | 已知估算人民币 |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for run in summary["runs"]:
        metric, inp = run["call_metrics"], run["inputs"]
        counts = f"{fmt(run['published_chapter_count'])} / {fmt(run['published_aha_count'])}" if run["quality_result_available"] else f"—（内部 {run['chapter_count']}/{run['aha_count']}）" if run["returned_result_available"] else "— / —"
        lines.append(f"| {run['pack_id']} / {run['round']} | {run['status']} / {DELIVERY_LABELS[run['delivery_class']]} | {counts} | {fmt(inp['asset_count'])}/{fmt(inp['frame_count'])} | {fmt(inp['normalization_seconds'])} | {fmt(run['wall_duration_seconds'])} | {metric['attempted_call_count']}/{metric['http_429_count']} | {metric['known_input_tokens']}/{metric['known_output_tokens']} | {metric['usage_unknown_call_count']} | {metric['known_estimated_cost_cny']:.6f} |")
    totals = summary["all_attempted_call_metrics"]
    lines += ["", f"状态分布：`{json.dumps(summary['status_counts'], ensure_ascii=False)}`。",
              f"交付分类分布：`{json.dumps(summary['delivery_class_counts'], ensure_ascii=False)}`。",
              f"全部已尝试请求：{totals['attempted_call_count']} 次；已知 {totals['known_total_tokens']} token；{totals['usage_unknown_call_count']} 次 usage 未知；已知估算 ¥{totals['known_estimated_cost_cny']:.6f}，另有 {totals['cost_unknown_call_count']} 次费用未知。", "",
              "## 可交付运行中的流程观察统计", "",
              "主表只统计完整覆盖且可交付（含文案 fallback 降级）的运行；不纳入阻断内部候选、无结果失败及进行中运行。拒因计数可能一条提议对应多个原因，不能将拒因项数直接当提议数。以下长度只是观察值，不新增阻断规则。", "",
              "| 包/轮 | 原生 Aha 提议/拒绝 | 最终 Aha 来源 | S10 正好三件且未比较/全部 S10 Chapter | Aha 正文>24/全部 Aha | Chapter 正文>48/全部 Chapter |",
              "|---|---:|---|---:|---:|---:|"]
    for run in summary["runs"]:
        d = run.get("completed_diagnostics")
        if not d or not run["quality_result_available"]:
            continue
        sources = ", ".join(f"{key}: {value}" for key, value in d["final_aha_source_counts"].items())
        lines.append(f"| {run['pack_id']}/{run['round']} | {fmt(d['native_aha_proposal_count'])}/{d['native_aha_rejected_count']} | {sources} | {d['s10_exact_three_no_comparison_count']}/{d['s10_chapter_selection_count']} | {d['aha_story_over_24_count']}/{d['final_aha_count']} | {d['chapter_story_over_48_count']}/{d['final_chapter_count']} |")
    d = summary["completed_run_diagnostics"]
    lines += ["", f"可交付结果 {d['completed_run_count']} 轮，来自 {d['independent_packs_with_completed_runs']} 套素材。原生 Aha 提议已知 {d['known_native_aha_proposal_count']} 条，拒绝 {d['native_aha_rejected_count']} 条；未知提议总数的运行 {d['native_proposal_count_unknown_run_count']} 轮。",
              f"最终 Aha 来源：`{json.dumps(d['final_aha_source_counts'], ensure_ascii=False)}`。",
              f"原生 Aha 拒因：`{json.dumps(d['native_aha_rejection_reason_counts'], ensure_ascii=False)}`；详细原因：`{json.dumps(d['native_aha_rejection_detail_counts'], ensure_ascii=False)}`。",
              f"S10 正好三件且未比较 {d['s10_exact_three_no_comparison_count']}/{d['s10_chapter_selection_count']} 次，其中最终发布的 Chapter {d['published_chapter_exact_three_no_comparison_count']} 个。各来源混合计数：Aha 正文 >24 字 {d['aha_story_over_24_count']}/{d['final_aha_count']}；Chapter 正文 >48 字 {d['chapter_story_over_48_count']}/{d['final_chapter_count']}；不能据此单独评价模型 Writer。", "",
              "### Writer 来源分层", "", "只统计可交付卡片。模板/fallback 不混入 MODEL_WRITER 写作长度分母。", "",
              "| 正文来源 | Aha >24/全部 | Chapter >48/全部 |", "|---|---:|---:|"]
    for source, lengths in d["writer_length_by_source"].items():
        lines.append(f"| {source} | {lengths['aha_story_over_24_count']}/{lengths['aha_count']} | {lengths['chapter_story_over_48_count']}/{lengths['chapter_count']} |")
    lines += ["", "### 交付与稳定性比较边界", ""]
    for run in summary["runs"]:
        if not run["returned_result_available"]:
            continue
        lines.append(f"- 包{run['pack_id']}R{run['round']}：{DELIVERY_LABELS[run['delivery_class']]}；delivery=`{run['delivery_state']}`，coverage=`{run['coverage_status']}`；Writer 来源 `{json.dumps(run['writer_surface_source_counts'], ensure_ascii=False)}`；未解决素材 `{', '.join(run['unresolved_relative_paths']) or '无'}`。")
        if run["stability_comparison_confounds"]:
            lines.append(f"  比较混杂：`{'; '.join(run['stability_comparison_confounds'])}`。")
    lines += ["",
              "## 固定输入与版本核查", ""]
    for pack in summary["pack_consistency"]:
        lines.append(f"- 包 {pack['pack_id']}：准备完成 {pack['prepared_rounds']}/3 轮；原始文件/顺序跨轮一致 `{pack['original_order_and_hashes_equal']}`；标准化帧跨轮一致 `{pack['evidence_hashes_equal']}`；文件实测哈希不匹配 {pack['actual_file_hash_mismatch_count']} 个；实际结果策略一致 `{pack['completed_result_policies_equal']}`（有结构化返回记录 {pack['completed_result_count']} 份，不代表均可交付）。")
    lines += ["", "策略以每份结果的 `result.decision_trace.runtime_policies` 为准；失败但未返回结果的运行只保留计划策略，不冒充已验证。", "",
              f"冻结快照纳入 {summary['runtime_integrity']['pinned_file_count']} 个文件；冻结副本不匹配 {len(summary['frozen_runtime_file_hash_mismatches'])} 个，当前仓库对应文件不匹配 {len(summary['runtime_integrity']['current_repo_file_hash_mismatches'])} 个。已返回结果的实际策略记录 {summary['runtime_integrity']['actual_policy_result_count']} 份、相互一致 `{summary['runtime_integrity']['all_actual_result_policies_equal']}`；全部运行计划策略一致 `{summary['runtime_integrity']['all_planned_runtime_policies_equal']}`。", "",
              "## 每包端到端组成耗时", "",
              "每轮分钟数 = 当轮本地标准化耗时 + 当轮算法墙钟耗时。不包括实验排队、人工等待；不是浏览器完整交互性能测试。失败轮是到失败为止的耗时，不能当作更快完成。", "",
              "| 素材包 | R1 分钟 / 分类 | R2 分钟 / 分类 | R3 分钟 / 分类 |", "|---|---|---|---|"]
    for pack_id in ("1", "2", "3"):
        same = [run for run in summary["runs"] if run["pack_id"] == pack_id]
        cells = [f"{fmt(run['end_to_end_component_minutes'])} / {DELIVERY_LABELS[run['delivery_class']]}" for run in same]
        lines.append(f"| {pack_id} | " + " | ".join(cells) + " |")
    lines += ["", "### 阶段份额（可交付的完整覆盖运行）", "",
              "含 Writer 降级轮，失败等待也是真实耗时。耗时份额以这些运行的算法墙钟总和为分母，不含本地标准化；token/费用份额仅对已知 usage/估算费用求占比。", "",
              "| 阶段 | 秒数合计 | 算法耗时份额 | 已知 token 份额 | 已知费用份额 |", "|---|---:|---:|---:|---:|"]
    for stage, metrics in summary["timing_by_scope"]["deliverable_results"]["stage_totals"].items():
        lines.append(f"| {stage} | {metrics['known_duration_seconds']:.2f} | {fmt(metrics['percent_of_algorithm_wall_time'])}% | {fmt(metrics['percent_of_known_tokens'])}% | {fmt(metrics['percent_of_known_estimated_cost'])}% |")
    lines += ["",
              "## 分阶段实测", "", "阶段时长为该阶段调用耗时之和，不与本地抽帧时间混算；整个运行总时间使用独立墙钟记录。", "",
              "| 包/轮 | 阶段 | 调用 | 已知耗时秒 | 已知输入/输出 token | usage 未知 | 已知估算人民币 |", "|---|---|---:|---:|---:|---:|---:|"]
    for run in summary["runs"]:
        for stage, metrics in run["stage_metrics"].items():
            lines.append(f"| {run['pack_id']}/{run['round']} | {stage} | {metrics['attempted_call_count']} | {metrics['known_duration_seconds']:.2f} | {metrics['known_input_tokens']}/{metrics['known_output_tokens']} | {metrics['usage_unknown_call_count']} | {metrics['known_estimated_cost_cny']:.6f} |")
    lines += ["", "## 逐轮成品及复用线索", ""]
    for run in summary["runs"]:
        lines += [f"### 包 {run['pack_id']} · 第 {run['round']} 轮", "", f"状态：`{run['status']}`，{DELIVERY_LABELS[run['delivery_class']]}；delivery=`{run['delivery_state']}` / coverage=`{run['coverage_status']}`；源记录：`{run['source_run']}`。", ""]
        if run["delivery_class"] == "BLOCKED_INTERNAL_CANDIDATES":
            lines += ["以下仅为内部诊断候选，不是发布完成的成品；上游观察缺失混杂，不能按相同输入完整模型结果比较。", ""]
        if not run["cards"]:
            lines += ["当前无可评估成品；不视为产出数量为零。" if not run["quality_result_available"] else "该完成结果没有成品卡片。", ""]
        for card in run["cards"]:
            lines += [f"**{card['kind']} {card['ordinal']}：《{card['title']}》**（标题 {card['title_visible_characters']} 字；正文 {card['story_visible_characters']} 字；来源 `{card['surface_source']}`；`{card['publication_status']}`）", "",
                      card["story"], "", f"素材：{', '.join(card['selected_relative_paths'])}。标签：{', '.join(card['tags']) or '无'}。", ""]
        if run["cross_card_reuse"]:
            lines += ["复用线索（需结合故事判断，不自动判错）：", ""]
            for pair in run["cross_card_reuse"]:
                lines.append(f"- 《{pair['first']['title']}》 / 《{pair['second']['title']}》：共享素材 {', '.join(pair['shared_relative_paths']) or '无'}；共享事实 {len(pair['shared_fact_ids'])} 条。")
            lines.append("")
    lines += ["## 完整机器可读记录", "", f"`{relative(JSON_REPORT)}` 包含实际策略、逐调用 usage/费用、原始记录路径、卡片事实引用和哈希检查结果。未新增任何运行时语义规则。", ""]
    return "\n".join(lines)


def main():
    prep = read(AREA / "codex_preparation.json")
    packs = {str(pack["pack_id"]): pack for pack in prep.get("packs", [])}
    runs = [inspect_round(packs[pack_id], round_number) for pack_id in ("1", "2", "3") if pack_id in packs for round_number in (1, 2, 3)]
    consistency = []
    for pack_id in ("1", "2", "3"):
        same = [r for r in runs if r["pack_id"] == pack_id]
        prepared = [r for r in same if r["inputs"]["manifest_present"]]
        completed = [r for r in same if r["returned_result_available"]]
        consistency.append({
            "pack_id": pack_id, "prepared_rounds": len(prepared), "completed_result_count": len(completed),
            "original_order_and_hashes_equal": len({r["inputs"]["ordered_original_hash_fingerprint"] for r in prepared}) == 1 if len(prepared) > 1 else None,
            "evidence_hashes_equal": len({r["inputs"]["ordered_frame_hash_fingerprint"] for r in prepared}) == 1 if len(prepared) > 1 else None,
            "actual_file_hash_mismatch_count": sum(len(r["inputs"]["original_file_hash_mismatches"]) + len(r["inputs"]["evidence_file_hash_mismatches"]) for r in prepared),
            "completed_result_policies_equal": len({fingerprint(r["actual_runtime_policies"]) for r in completed}) == 1 if len(completed) > 1 else None,
        })
    runtime_mismatches = [relative(AREA / "codex_runtime" / name) for name, expected in prep.get("source_sha256", {}).items()
                          if sha(AREA / "codex_runtime" / name) != expected]
    current_mismatches = [name for name, expected in prep.get("source_sha256", {}).items() if sha(ROOT / name) != expected]
    actual_policies = [run["actual_runtime_policies"] for run in runs if run["actual_runtime_policies"]]
    planned_policies = [run["planned_runtime_policies"] for run in runs if run["planned_runtime_policies"]]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "experiment": "CODEX_V1_64_REPEAT_REVIEW",
        "independent_pack_count": len(packs), "planned_runs": 9, "algorithm_baseline": "V1.63",
        "quality_status": "EXPLORATORY_DEVELOPER_REVIEW_NOT_USER_RATINGS_OR_HELD_OUT_EVAL",
        "status_counts": dict(Counter(r["status"] for r in runs)),
        "delivery_class_counts": dict(Counter(r["delivery_class"] for r in runs)),
        "all_attempted_call_metrics": aggregate_calls([c for r in runs for c in r["calls"]]),
        "completed_run_diagnostics": aggregate_completed_diagnostics(runs),
        "returned_run_diagnostics_including_blocked": aggregate_completed_diagnostics(runs, include_blocked=True),
        "timing_by_scope": {
            "all_attempted_runs_including_failures": timing_totals(runs),
            "deliverable_results": timing_totals([run for run in runs if run["quality_result_available"]]),
            "primary_copy_complete_results": timing_totals([run for run in runs if run["delivery_class"] == "COMPLETE_DELIVERABLE"]),
        },
        "runtime_integrity": {
            "pinned_file_count": len(prep.get("source_sha256", {})),
            "current_repo_file_hash_mismatches": current_mismatches,
            "actual_policy_result_count": len(actual_policies),
            "all_actual_result_policies_equal": len({fingerprint(p) for p in actual_policies}) == 1 if actual_policies else None,
            "planned_policy_run_count": len(planned_policies),
            "all_planned_runtime_policies_equal": len({fingerprint(p) for p in planned_policies}) == 1 if planned_policies else None,
        },
        "pack_consistency": consistency, "frozen_runtime_file_hash_mismatches": runtime_mismatches,
        "runs": runs,
    }
    JSON_REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_REPORT.write_text(render(summary), encoding="utf-8")
    print(json.dumps({"status_counts": summary["status_counts"], "all_calls": summary["all_attempted_call_metrics"],
                      "runtime_hash_mismatches": runtime_mismatches, "outputs": [str(JSON_REPORT), str(MD_REPORT)]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
