"""Isolated V1.42: one focus-selection + Writer request, no publication or repair."""

import argparse
import copy
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "var/codex_writer_checks/writer_workbench_v1_40/report.json"
DESTINATION = ROOT / "var/codex_writer_checks/writer_focus_v1_42"
MODEL = "qwen3.7-flash-2026-07-15"
CONTEXT_SHA = "663bb208f78effeeb3bf0b6baf8c069ad98d09278f5d6ea44fa548b973179aa6"
PIPELINE_SHA = "4fc7433361959142b8a109be5abfdfaf4b72b27bfa94fcd3eadc7a98334f6d1b"
SERVER_SHA = "e64d552aa3eac15b753b671aaed5850953015d992f5ff12ca7957e41bcbe700b"

FOCUS_INSTRUCTION = """Editorial focus selection for this writing pass:
Use meaningful supported content units (subjects in action, interactions, or a subject in its setting),
not a top-N list of isolated objects. For each supplied memory, rank what is worth expressing by:
central relevance to this memory, distinguishing detail, visible activity/interaction/atmosphere,
and the additional meaning gained by including another unit. Treat scene categories as context,
not fixed mappings to preferred objects or emotional words. No personal preference data is supplied;
do not claim measured user interests, rarity, surprise, or personal feelings.
Start from the central concrete content. Include supporting content only when it adds meaningful,
non-redundant information and fits natural short prose. There is no fixed number to fill.
A Chapter may summarize several selected images without describing each one; an Aha centers on its
single supplied moment. Do not erase materially different content to make a grouping sound coherent,
or invent a temporal/causal connection. Existing fact and narrative constraints still apply.
Atmosphere should emerge from selected concrete content, not replace it with a generic mood phrase.
Keep the wording conversational and natural, rather than a compressed inventory or surveillance report.
Return a short editorial record in focus_reviews for each candidate_id, along with chapters and ahas.
selected contains the chosen content units in decreasing editorial priority, each with focus,
supporting fact_ids and one brief reason. omitted contains only a few notable details left out of
the prose, each with detail, fact_ids and a brief reason; it may be empty. Do not enumerate everything.
These are concise editorial decisions for review, not a detailed reasoning transcript or a proof of
semantic correctness. Leaving a detail out of prose never deletes its fact or media. Do not change
candidate membership or manufacture a different story to justify an existing Aha.
"""


def focus_schema():
    schema = copy.deepcopy(x02.WRITER_SCHEMA)
    def unit(field):
        return {"type": "object", "additionalProperties": False,
                "required": [field, "fact_ids", "reason"], "properties": {
                    field: {"type": "string"}, "reason": {"type": "string"},
                    "fact_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1}}}
    schema["required"].append("focus_reviews")
    schema["properties"]["focus_reviews"] = {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["candidate_id", "selected", "omitted"], "properties": {
            "candidate_id": {"type": "string"},
            "selected": {"type": "array", "items": unit("focus"), "minItems": 1},
            "omitted": {"type": "array", "items": unit("detail")}}}}
    return schema


def focus_reference_audit(output, context):
    """Diagnostic format/reference checks only; never a runtime publication gate."""
    rows = output.get("focus_reviews", []) if isinstance(output, dict) else []
    rows = rows if isinstance(rows, list) else []
    audit = []
    expected_ids = {m["candidate_id"] for m in context["memories"]}
    for memory in context["memories"]:
        matched = [r for r in rows if isinstance(r, dict) and r.get("candidate_id") == memory["candidate_id"]]
        problems = []
        if len(matched) != 1:
            problems.append("FOCUS_RECORD_MISSING_OR_DUPLICATED")
        else:
            row = matched[0]
            allowed = {f["fact_id"] for f in memory["facts"]}
            for field, text_field in (("selected", "focus"), ("omitted", "detail")):
                units = row.get(field)
                if not isinstance(units, list) or (field == "selected" and not units):
                    problems.append("FOCUS_LIST_INVALID")
                    continue
                for u in units:
                    if not isinstance(u, dict):
                        problems.append("FOCUS_UNIT_INVALID")
                        continue
                    if not all(isinstance(u.get(k), str) and u[k].strip() for k in (text_field, "reason")):
                        problems.append("FOCUS_TEXT_MISSING")
                    refs = u.get("fact_ids")
                    if not isinstance(refs, list) or not refs or any(not isinstance(f, str) or f not in allowed for f in refs):
                        problems.append("FOCUS_REFERENCE_INVALID")
        audit.append({"candidate_id": memory["candidate_id"], "problems": sorted(set(problems)),
                      "scope": "FORMAT_AND_REFERENCES_ONLY_NOT_FOCUS_QUALITY_OR_SEMANTIC_VERIFICATION"})
    unexpected = [r.get("candidate_id") if isinstance(r, dict) else None for r in rows
                  if not isinstance(r, dict) or r.get("candidate_id") not in expected_ids]
    return {"items": audit, "unexpected_candidate_ids": unexpected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    baseline = json.loads(BASELINE.read_text())
    context = baseline["context"]
    assert hashlib.sha256(canonical_bytes(context)).hexdigest() == CONTEXT_SHA
    assert hashlib.sha256(Path(x02.__file__).read_bytes()).hexdigest() == PIPELINE_SHA
    assert hashlib.sha256((ROOT / "src/diary_one_ci/x01_server.py").read_bytes()).hexdigest() == SERVER_SHA
    prompt = FOCUS_INSTRUCTION + "\n" + x02._writer_prompt(context, retry=False)
    schema = focus_schema()
    if not args.live:
        print(json.dumps({"model": MODEL, "maximum_calls": 1, "context_unchanged": True,
                          "memories": len(context["memories"]), "manual_answers_supplied": False,
                          "request_schema_root_fields": schema["required"]}))
        return
    key, _ = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing Qwen credential unavailable; no call made")
    DESTINATION.mkdir(parents=True, exist_ok=False)
    report = {
        "scope": "ISOLATED_S11_FOCUS_AND_PROSE_ONE_CALL_NOT_FULL_PIPELINE_OR_DEPLOYMENT",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "baseline_path": str(BASELINE), "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        "source_run_id": baseline["source_run_id"], "context": context, "input_sha256": CONTEXT_SHA,
        "active_pipeline_sha256": PIPELINE_SHA, "active_server_sha256": SERVER_SHA,
        "model": MODEL, "manual_answers_supplied": False, "retry": "DISABLED_FOR_SINGLE_PASS_EXPERIMENT",
        "quality_status": "AWAITING_REAL_OUTPUT_REVIEW", "captures": [],
        "price_cny_per_million": [0.2, 0.8], "pricing_basis": baseline["pricing_basis"],
    }
    def persist():
        (DESTINATION / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    persist()
    adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=60,
                                       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    adapter.input_rate_per_million, adapter.output_rate_per_million = 0.2, 0.8
    adapter.pricing_basis = report["pricing_basis"]
    original_transport = adapter.transport
    def capture(url, headers, body, timeout):
        assert url == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        assert not report["captures"], "Exactly one model request is authorized for this experiment"
        payload = json.loads(body)
        assert payload["model"] == MODEL
        assert all(p["type"] == "text" for m in payload["messages"] for p in m["content"])
        entry = {"request_sha256": hashlib.sha256(body).hexdigest()}
        report["captures"].append(entry)
        (DESTINATION / "request.json").write_bytes(body)
        persist()
        status, response_headers, response = original_transport(url, headers, body, timeout)
        (DESTINATION / "response.json").write_bytes(response)
        entry["http_status"] = status
        try:
            raw = json.loads(response)
            entry["response_model"] = raw.get("model")
            entry["finish_reasons"] = [c.get("finish_reason") for c in raw.get("choices", [])]
        except (ValueError, AttributeError):
            pass
        persist()
        return status, response_headers, response
    adapter.transport = capture
    started = time.monotonic()
    try:
        run = x02.QwenStageGateway(adapter).call("S11_FOCUS_WRITER_V1_42", prompt, schema,
                                               context={**context, "_x02_policy_version": "V04_1"})
        report["output"] = run.output
        report["metric"] = x02._metric_from_run(run)
        report["estimated_cost_cny"] = run.estimated_cost_native
        persist()
        accepted, audit, invalid = x02._validate_writer_output(run.output, context, attempt=1)
        report.update({"narratives": accepted, "writer_audit": audit, "invalid_ids": invalid,
                       "focus_reference_audit": focus_reference_audit(run.output, context)})
    except x02.X02StageCallError as exc:
        report.update({"error": exc.code, "metric": x02._metric_from_run(exc.stage_run),
                       "estimated_cost_cny": exc.stage_run.estimated_cost_native})
    finally:
        report["workbench_wall_ms"] = round((time.monotonic() - started) * 1000, 3)
        persist()
    print(json.dumps({"report_path": str(DESTINATION / "report.json"), "error": report.get("error"),
                      "metric": report.get("metric"), "estimated_cost_cny": report.get("estimated_cost_cny"),
                      "invalid_ids": report.get("invalid_ids"), "output": report.get("output")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
