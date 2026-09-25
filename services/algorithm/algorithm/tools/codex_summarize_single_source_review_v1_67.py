"""One-shot local summary of all three V1.67 round_1 records; no semantic scoring."""
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_67_single_source_structure"
DESTINATION = AREA / "codex_summary.json"
sys.dont_write_bytecode = True
HELPER_PATH = ROOT / "tools/codex_summarize_repeat_review_v1_64.py"
spec = importlib.util.spec_from_file_location("v164_readonly_card_helpers", HELPER_PATH)
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)  # Import pure helpers only; never call its main/write functions.


def read(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected complete JSON object: " + str(path))
    return value


def reasons(rows):
    return dict(Counter(code for row in rows for code in row.get("reason_codes", [])))


def relation_summary(rows):
    return {"count": len(rows), "relation_counts": dict(Counter(r.get("relation", "INVALID")
            if isinstance(r, dict) else "INVALID_ROW" for r in rows)), "rows": rows}


def ledger_summary(rows):
    return {"entries": len(rows), "validation_status_counts": dict(Counter(r.get("validation_status", "UNKNOWN") for r in rows)),
            "selection_status_counts": dict(Counter(r.get("selection_status", "UNKNOWN") for r in rows)),
            "rejection_reasons": reasons([r for r in rows if r.get("validation_status") == "REJECTED"]),
            "not_selected_reasons": reasons([r for r in rows if r.get("selection_status") == "NOT_SELECTED"]),
            "rows": rows}


def metrics(calls, transports):
    known = [r["usage"] for r in transports if isinstance(r.get("usage"), dict)]
    return {
        "stage_call_count": len(calls), "failed_stage_call_count": sum(c.get("status") == "FAILED" for c in calls),
        "stage_call_seconds": sum(c.get("duration_seconds") or 0 for c in calls),
        "transport_attempt_count": len(transports),
        "http_429_count": sum(t.get("http_status") == 429 for t in transports),
        "no_http_response_count": sum(t.get("status") == "NO_HTTP_RESPONSE" for t in transports),
        "provider_input_tokens_known": sum(u["input_tokens"] for u in known),
        "provider_output_tokens_known": sum(u["output_tokens"] for u in known),
        "provider_usage_unknown_count": len(transports) - len(known),
        "provider_usage_complete": bool(transports) and len(known) == len(transports),
        "historical_estimated_cny_known": sum(u["estimated_tiered_cost_cny"] for u in known) if known else None,
        "cost_basis": "HISTORICAL_V1_64_BEIJING_RATE_SNAPSHOT_NOT_BILLING_OR_CURRENT_PRICE",
        "usage_rule": "PROVIDER_TOTALS_ONLY_DETAILS_NOT_ADDED_AGAIN_MISSING_IS_UNKNOWN",
    }


def allocation_flow(directory, result, calls):
    trace = result.get("decision_trace") or {}
    allocation = trace.get("editorial_allocation") or {}
    plan, projection = allocation.get("plan"), allocation.get("writer_projection")
    selected_chapters = set((trace.get("chapter_set_selection") or {}).get("selected_candidate_ids", []))
    selected_ahas = set((trace.get("aha_set_selection") or {}).get("selected_candidate_ids", []))
    raw, s10, writers = [], [], []
    raw_present, structure_response_available, raw_proposals = False, False, {"chapter": [], "aha": []}
    raw_relation_missing_chapters = []
    for call in calls:
        prefix = directory / "codex_stage_calls" / ("codex_%03d" % call["index"])
        request = read(Path(str(prefix) + "_request.json"))
        response = read(Path(str(prefix) + "_response.json"))
        context, output = request.get("context") or {}, response.get("output") or {}
        if call["stage"] == "S05_S07_STRUCTURE_PROPOSAL":
            structure_response_available = structure_response_available or bool(output)
            chapters = output.get("storyline_proposals")
            supplied = isinstance(chapters, list)
            raw_present = raw_present or supplied
            for chapter_index, chapter in enumerate(chapters if isinstance(chapters, list) else []):
                if not isinstance(chapter, dict) or not isinstance(chapter.get("aha_relations"), list):
                    raw_relation_missing_chapters.append({"call_index": call["index"], "source_chapter_index": chapter_index})
                    continue
                for relation_index, row in enumerate(chapter["aha_relations"]):
                    raw.append({**row, "_source_chapter_key": chapter.get("key"),
                                "_source_chapter_index": chapter_index, "_source_relation_index": relation_index}
                               if isinstance(row, dict) else row)
            raw_proposals["chapter"].extend(output.get("storyline_proposals") or [])
            raw_proposals["aha"].extend(output.get("aha_proposals") or [])
        elif call["stage"].startswith("S10_"):
            s10.append({"call_index": call["index"], "candidate_id": context.get("candidate_id"),
                        "status": call.get("status"), **relation_summary(context.get("chapter_aha_relations") or [])})
        elif call["stage"].startswith("S11_"):
            # Inspect what the archived prompt actually sent, not a newly recomputed projection.
            try:
                wire = json.loads(request["prompt"].rsplit("Input:\n", 1)[1])
                wire_relations = wire.get("chapter_aha_relations")
                parsed = isinstance(wire_relations, list)
            except (KeyError, IndexError, ValueError, AttributeError):
                wire, wire_relations, parsed = {}, [], False
            writers.append({"call_index": call["index"], "status": call.get("status"), "prompt_input_parsed": parsed,
                            "candidate_ids": [m.get("candidate_id") for m in wire.get("memories", [])],
                            "count": len(wire_relations) if parsed else None,
                            "rows": wire_relations if parsed else None})
    compiled = plan.get("relations", []) if isinstance(plan, dict) else None
    retained = [r for r in compiled if r.get("chapter_candidate_id") in selected_chapters
                and r.get("aha_candidate_id") in selected_ahas] if compiled is not None else None
    # A useful denominator: passed Chapter members that are also actual eligible
    # Aha observations. This is not the unrelated full Cartesian pair matrix.
    valid_chapters = {r["candidate_id"]: set(r.get("observation_ids", []))
                      for r in trace.get("chapter_candidates", []) if r.get("validation_status") == "PASSED"}
    eligible_ahas = {r["candidate_id"]: r.get("observation_id")
                    for r in trace.get("aha_candidates", []) if r.get("validation_status") == "PASSED"}
    relevant_keys = {(chapter_id, aha_id) for chapter_id, members in valid_chapters.items()
                     for aha_id, observation_id in eligible_ahas.items() if observation_id in members}
    relevant_rows = [r for r in compiled or []
                     if (r.get("chapter_candidate_id"), r.get("aha_candidate_id")) in relevant_keys]
    compiled_keys = {(r.get("chapter_candidate_id"), r.get("aha_candidate_id")) for r in compiled or []}
    diagnostics = plan.get("diagnostics", []) if isinstance(plan, dict) else []
    projection_diagnostics = projection.get("diagnostics", []) if isinstance(projection, dict) else []
    return {
        "available": bool(allocation), "raw_relation_field_present": raw_present,
        "raw_relation_source": "NESTED_PER_CHAPTER_AHA_RELATIONS_NOT_LEGACY_TOP_LEVEL",
        "raw_relation_missing_or_invalid_chapters": raw_relation_missing_chapters,
        "structure_wire_receipt": trace.get("structure_wire"),
        "structure_wire_diagnostic_codes": dict(Counter(
            row.get("code", "UNKNOWN") for row in (trace.get("structure_wire") or {}).get("diagnostics", []))),
        "raw": relation_summary(raw) if raw_present else None,
        "compiled": relation_summary(compiled) if compiled is not None else None,
        "member_overlap_relevant_pairs": {
            "denominator": "PASSED_CHAPTER_MEMBERS_INTERSECT_FINAL_ELIGIBLE_AHA_OBSERVATIONS_BEFORE_SET_SELECTION",
            "expected_pair_count": len(relevant_keys) if compiled is not None else None,
            **relation_summary(relevant_rows),
            "missing_compiled_pairs": [list(pair) for pair in sorted(relevant_keys - compiled_keys)],
        },
        "selected_pairs": relation_summary(retained) if retained is not None else None,
        "writer_projection": relation_summary(projection.get("relations", [])) if isinstance(projection, dict) else None,
        "compiled_diagnostic_codes": dict(Counter(d.get("code", "UNKNOWN") for d in diagnostics)),
        "compiled_unresolved_reason_codes": reasons([r for r in compiled or [] if r.get("relation") == "UNRESOLVED"]),
        "compiled_diagnostics": diagnostics,
        "writer_projection_diagnostic_codes": dict(Counter(d.get("code", "UNKNOWN") for d in projection_diagnostics)),
        "writer_projection_diagnostics": projection_diagnostics,
        "selection_examined_relations": (trace.get("aha_set_selection") or {}).get("chapter_relations", []),
        "selection_rejections": (trace.get("aha_set_selection") or {}).get("rejections", {}),
        "s10_calls": s10, "actual_writer_calls": writers,
        "actual_writer_relation_occurrences_known": sum(w["count"] or 0 for w in writers),
        "writer_projection_unknown_call_count": sum(not w["prompt_input_parsed"] for w in writers),
        "raw_proposals": raw_proposals,
        "raw_proposal_counts": {kind: len(rows) if structure_response_available else None for kind, rows in raw_proposals.items()},
        "chapter_candidate_ledger": ledger_summary(trace.get("chapter_candidates") or []),
        "aha_candidate_ledger": ledger_summary(trace.get("aha_candidates") or []),
        "selected_chapter_candidate_ids": sorted(selected_chapters), "selected_aha_candidate_ids": sorted(selected_ahas),
        "writer_items": trace.get("writer_items", []), "blocked_memories": trace.get("blocked_memories", []),
        "count_semantics": "RAW_ROWS_COMPILED_PAIR_MATRIX_SELECTED_PAIRS_AND_PER_CALL_OCCURRENCES_HAVE_DIFFERENT_DENOMINATORS_NOT_A_FUNNEL_CONVERSION_RATE",
        "diagnostic_semantics": "PROJECTION_DIAGNOSTICS_INCLUDE_INHERITED_PLAN_DIAGNOSTICS_NOT_DISJOINT_NEW_FAILURES",
    }


def summarize_pack(pack, report, candidate):
    round_directory = AREA / ("pack_" + str(pack["pack_id"])) / "round_1"
    directory = round_directory
    manifest = read(round_directory / "codex_manifest.json")
    norm = read(round_directory / "codex_normalization.json")
    result, calls, transports = report.get("result") or {}, report.get("stage_calls") or [], report.get("transport_attempts") or []
    mapping, mismatches = {}, []
    for index, asset in enumerate(manifest["assets"]):
        original = pack["assets"][index] if index < len(pack["assets"]) else {}
        if asset.get("original_sha256") != original.get("sha256"):
            mismatches.append(index)
        name = original.get("relative_path", asset["asset_id"])
        mapping[asset["asset_id"]] = name
        mapping[asset["asset_id"].removeprefix("asset_")] = name
    cards, overlaps = legacy.cards_and_reuse(result, mapping)
    for card in cards:
        originals = result["chapters" if card["kind"] == "CHAPTER" else "ahas"]
        card["selected_media"] = [{**m, "original_relative_path": mapping.get(m.get("source_asset_id") or m.get("asset_id"))}
                                  for m in originals[card["ordinal"] - 1].get("selected_media", [])]
    delivery, coverage = result.get("delivery_state"), result.get("coverage_status")
    if not result:
        classification = "NO_RESULT"
    elif delivery == "PIPELINE_BLOCKED" or coverage != "COMPLETE":
        classification = "BLOCKED_INTERNAL_CANDIDATES"
    elif delivery == "NO_GROUNDED_MEMORY":
        classification = "COMPLETE_EMPTY_RESULT"
    elif delivery != "READY_PRIMARY_COPY" or any(c["surface_source"] != "MODEL_WRITER" for c in cards):
        classification = "DEGRADED_DELIVERABLE"
    else:
        classification = "COMPLETE_DELIVERABLE"
    stages = sorted({c["stage"] for c in calls} | {t["stage"] for t in transports})
    trace = result.get("decision_trace") or {}
    return {
        "pack_id": str(pack["pack_id"]), "round": 1, "status": report["status"], "delivery_class": classification,
        "delivery_state": delivery, "coverage_status": coverage, "error_code": report.get("error_code"),
        "error_message": report.get("error_message"), "failed_stages": report.get("failed_stages", []),
        "all_attempted_stage_calls_completed": bool(calls) and all(c["status"] == "COMPLETED" for c in calls),
        "expected_input_assets": len(pack["assets"]), "manifest_assets": len(manifest["assets"]),
        "manifest_frames": sum(len(a.get("frames", [])) for a in manifest["assets"]),
        "inventory_hash_mismatch_indices": mismatches,
        "normalization_status": norm.get("status"), "fresh_decode": norm.get("freshDecodeAndExtraction"),
        "unresolved_original_paths": [mapping.get(a, a) for a in result.get("unresolved_asset_ids", [])],
        "decision_counts": trace.get("counts"), "stage_statuses": trace.get("stage_statuses"),
        "chapter_count": len(result.get("chapters", [])) if result else None,
        "aha_count": len(result.get("ahas", [])) if result else None,
        "cards": cards, "cross_card_reuse_not_automatically_error": overlaps,
        "writer_length_by_source": legacy.length_by_source(cards),
        "allocation": allocation_flow(directory, result, calls),
        "normalization_seconds": report.get("normalization_seconds"), "algorithm_seconds": report.get("duration_seconds"),
        "end_to_end_seconds": report.get("end_to_end_seconds"), "metrics": metrics(calls, transports),
        "per_stage": {stage: metrics([c for c in calls if c["stage"] == stage], [t for t in transports if t["stage"] == stage]) for stage in stages},
        "algorithm_stage_metrics_original_units": (result.get("trace") or {}).get("stage_metrics"),
        "runtime_policies": trace.get("runtime_policies"),
        "runtime_policies_match_candidate": trace.get("runtime_policies") == candidate["runtime_policies"] if result else None,
        "source_report": str(directory / "codex_full_run.json"), "source_report_sha256": legacy.sha(directory / "codex_full_run.json"),
        "manifest_sha256": legacy.sha(round_directory / "codex_manifest.json"),
        "manifest_matches_normalization": legacy.sha(round_directory / "codex_manifest.json") == norm.get("manifest_sha256"),
        "candidate_matches_run": report.get("candidate_sha256") == legacy.sha(AREA / "codex_candidate.json"),
    }


def main():
    if DESTINATION.exists():
        raise RuntimeError("Refusing to overwrite the one-shot summary")
    paths = [AREA / ("pack_" + str(n)) / "round_1/codex_full_run.json" for n in (1, 2, 3)]
    if not all(p.is_file() for p in paths):
        raise RuntimeError("Wait until all three round_1 final reports exist; no summary written")
    reports = [read(p) for p in paths]
    if any(r.get("status") not in {"RETURNED", "FAILED"} or not r.get("completed_at") for r in reports):
        raise RuntimeError("All three reports must be complete terminal records; no summary written")
    prep, candidate = read(AREA / "codex_preparation.json"), read(AREA / "codex_candidate.json")
    packs = {str(p["pack_id"]): p for p in prep["packs"]}
    runs = [summarize_pack(packs[str(n)], report, candidate) for n, report in zip((1, 2, 3), reports)]
    summary = {
        "experiment": prep["experiment"], "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "THREE_PACKS_ONE_ROUND_EACH_NOT_INDEPENDENT_NEW_USERS_OR_SEMANTIC_SCORES",
        "runtime_candidate": "V1.67", "all_three_terminal_reports_present": True,
        "returned_does_not_mean_success": True, "user_quality_accepted": False,
        "delivery_class_counts": dict(Counter(r["delivery_class"] for r in runs)),
        "all_three_complete_primary_delivery": all(r["delivery_class"] == "COMPLETE_DELIVERABLE" for r in runs),
        "all_three_stage_calls_completed": all(r["all_attempted_stage_calls_completed"] for r in runs),
        "totals_including_failures": metrics([c for r in reports for c in r.get("stage_calls", [])],
                                             [t for r in reports for t in r.get("transport_attempts", [])]),
        "sum_end_to_end_seconds_known": sum(r["end_to_end_seconds"] or 0 for r in runs),
        "runs": runs, "helper_path": str(HELPER_PATH), "helper_sha256": legacy.sha(HELPER_PATH),
        "summarizer_sha256": legacy.sha(Path(__file__)), "candidate_sha256": legacy.sha(AREA / "codex_candidate.json"),
        "summary_is_derived_not_a_source_record": True,
    }
    with DESTINATION.open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"summary": str(DESTINATION), "delivery_class_counts": summary["delivery_class_counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
