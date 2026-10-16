"""One isolated S11 pass: real selected Chapter/Aha input, initial + one repair.

No perception, grouping, selection or publication. No network without --live.
Uses the active Writer prompt/validation/fallback, not archived prompt experiments.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "var/x02_runs/f12c67c7-e36f-469d-b21b-07bdf4e79d60/runs/670b2417-d3a5-424b-a3c0-a1df6eb031cd.run_audit.json"
DESTINATION = ROOT / "var/codex_writer_checks/writer_workbench_v1_40"
MODEL = "qwen3.7-flash-2026-07-15"


def build_input(source):
    result = source["result"]
    trace = result["decision_trace"]
    observations = {item["id"]: item for item in result["observations"]}
    chapter_media = {item["candidate_id"]: item for item in trace["s10_chapter_media"]}
    aha_media = {item["candidate_id"]: item for item in trace["s10_aha_media"]}
    chapters, ahas, excluded = [], [], []
    for candidate in trace["chapter_candidates"]:
        if candidate.get("selection_status") != "SELECTED":
            continue
        if chapter_media[candidate["candidate_id"]]["final_media_count"] < 3:
            excluded.append({"candidate_id": candidate["candidate_id"],
                             "reason": "HISTORICAL_TWO_MEDIA_EXCEPTION_NOT_CURRENT_PUBLISHABLE_SAMPLE"})
            continue
        chapters.append({
            **candidate,
            "episode_code": x02._dominant_episode_code([observations[value] for value in candidate["observation_ids"]]),
            "fact_ids": sorted({fact for beat in candidate["storyline_identity"]["beat_map"] for fact in beat["fact_ids"]}),
        })
    for candidate in trace["aha_candidates"]:
        if candidate.get("selection_status") != "SELECTED":
            continue
        assert candidate["proposal_source"] == "DETERMINISTIC_EVENT_PEAK", "This recorded-data reconstructor does not infer model proposal scope"
        observation = observations[candidate["observation_id"]]
        facts = x02._supported_aha_fact_ids(observation)
        ahas.append({**candidate, "episode_code": observation["episode_code"],
                     "narrative_duty": observation["event_kind"], "fact_ids": facts,
                     "event_fact_ids": facts})
    context = x02._writer_context(chapters, ahas, chapter_media, aha_media,
                                  result["observations"], storyline_v04=True)
    return context, excluded


def run_writer(context, gateway, persist=lambda report: None):
    report = {"context": context, "attempts": [], "writer_audit": [], "narratives": {},
              "retry_state": "NOT_NEEDED", "fallback_state": "NOT_NEEDED"}
    active = context
    for attempt in (1, 2):
        audit_context = {**active, "_x02_policy_version": "V04_1"}
        try:
            run = gateway.call(
                "S11_WRITER_ATTEMPT_%d" % attempt,
                x02._writer_prompt(active, retry=attempt == 2), x02.WRITER_SCHEMA,
                context=audit_context,
            )
            accepted, audit, invalid = x02._validate_writer_output(run.output, active, attempt=attempt)
            report["attempts"].append({"attempt": attempt, "output": run.output,
                                       "metric": x02._metric_from_run(run),
                                       "estimated_cost_cny": run.estimated_cost_native})
            report["writer_audit"].extend(audit)
            report["narratives"].update(accepted)
        except x02.X02StageCallError as exc:
            invalid = [item["candidate_id"] for item in active["memories"]]
            report["attempts"].append({"attempt": attempt, "error": exc.code,
                                       "metric": x02._metric_from_run(exc.stage_run)})
            report["writer_audit"].extend({
                "candidate_id": item["candidate_id"], "memory_type": item["memory_type"],
                "attempt": attempt, "validation_status": "REJECTED", "reason_codes": [exc.code],
            } for item in active["memories"])
        persist(report)
        if not invalid:
            break
        if attempt == 1:
            report["retry_state"] = "ONLY_FAILED_ITEMS_ONCE"
            active = x02._writer_retry_context(context, invalid, report["writer_audit"])
    missing = [item["candidate_id"] for item in context["memories"] if item["candidate_id"] not in report["narratives"]]
    if missing:
        fallback_context = x02._writer_retry_context(context, missing, report["writer_audit"])
        output, generation_audit = x02._deterministic_writer_fallback(fallback_context)
        accepted, audit, _ = x02._validate_writer_output(
            output, fallback_context, attempt=3, surface_source="DETERMINISTIC_GROUNDED_FALLBACK")
        report["narratives"].update(accepted)
        report["writer_audit"].extend(generation_audit + audit)
        report["fallback_state"] = "EXISTING_COMPLETE_FACT_COPY_ONLY"
    report["missing_ids"] = [item["candidate_id"] for item in context["memories"] if item["candidate_id"] not in report["narratives"]]
    report["format_status"] = "PASSED" if not report["missing_ids"] else "PARTIAL_OR_BLOCKED"
    persist(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    source = json.loads(SOURCE.read_text())
    context, excluded = build_input(source)
    if not args.live:
        print(json.dumps({"model": MODEL, "memory_types": [item["memory_type"] for item in context["memories"]],
                          "fact_counts": [len(item["facts"]) for item in context["memories"]],
                          "excluded": excluded, "maximum_model_calls": 2}, ensure_ascii=False))
        return
    key, _ = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing Qwen credential unavailable; no model call made")
    DESTINATION.mkdir(parents=True, exist_ok=False)
    metadata = {
        "scope": "S11_ONLY_INITIAL_AND_BOUNDED_REPAIR_NOT_FULL_PIPELINE",
        "source_run_id": source["run_id"], "source_path": str(SOURCE),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "active_pipeline_sha256": hashlib.sha256(Path(x02.__file__).read_bytes()).hexdigest(),
        "input_sha256": hashlib.sha256(canonical_bytes(context)).hexdigest(),
        "model": MODEL, "excluded_historical_candidates": excluded,
        "price_cny_per_million": [0.2, 0.8], "pricing_basis": "V1_39_OFFICIAL_BEIJING_SNAPSHOT_2026_09_03_UNDER_32K",
        "copy_quality_status": "AWAITING_USER_REVIEW", "captures": [],
    }
    adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=60,
                                       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    adapter.input_rate_per_million, adapter.output_rate_per_million = 0.2, 0.8
    adapter.pricing_basis = metadata["pricing_basis"]
    transport = adapter.transport

    def capture(url, headers, body, timeout):
        assert url == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        index = len(metadata["captures"]) + 1
        assert index <= 2
        payload = json.loads(body)
        assert payload["model"] == MODEL
        assert all(part["type"] == "text" for message in payload["messages"] for part in message["content"])
        entry = {"attempt": index, "request_sha256": hashlib.sha256(body).hexdigest()}
        metadata["captures"].append(entry)
        (DESTINATION / ("request_%d.json" % index)).write_bytes(body)
        status, response_headers, response = transport(url, headers, body, timeout)
        (DESTINATION / ("response_%d.json" % index)).write_bytes(response)
        entry["http_status"] = status
        try:
            output = json.loads(response)
            entry["response_model"] = output.get("model")
            entry["finish_reasons"] = [item.get("finish_reason") for item in output.get("choices", [])]
        except (ValueError, AttributeError):
            pass
        return status, response_headers, response

    adapter.transport = capture

    def persist(report):
        (DESTINATION / "report.json").write_text(json.dumps({**metadata, **report}, ensure_ascii=False, indent=2) + "\n")

    started = time.monotonic()
    report = run_writer(context, x02.QwenStageGateway(adapter), persist)
    report["workbench_wall_ms"] = round((time.monotonic() - started) * 1000, 3)
    report["totals"] = {
        "model_calls": len(report["attempts"]),
        "input_tokens": sum(a["metric"]["input_tokens"] or 0 for a in report["attempts"]),
        "output_tokens": sum(a["metric"]["output_tokens"] or 0 for a in report["attempts"]),
        "model_duration_ms": sum(a["metric"]["duration_ms"] for a in report["attempts"]),
        "estimated_cost_cny": sum(a.get("estimated_cost_cny", 0) for a in report["attempts"]),
    }
    persist(report)
    print(json.dumps({"report_path": str(DESTINATION / "report.json"), "totals": report["totals"],
                      "format_status": report["format_status"], "retry_state": report["retry_state"],
                      "missing_ids": report["missing_ids"], "narratives": report["narratives"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
