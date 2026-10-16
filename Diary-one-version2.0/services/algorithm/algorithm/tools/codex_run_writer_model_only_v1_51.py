"""V1.51: fixed V1.48 Writer input, only model changes, at most two calls.

Default is offline verification. Reuses the existing Writer workbench and runtime
validation/repair/fallback; never imported by the Web or production pipeline.
"""
import argparse
import copy
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from diary_one_ci import x02, codex_content_brief as brief
from diary_one_ci.core import canonical_bytes
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key
from codex_run_full_pipeline_pair import audit_context_bytes
from codex_run_writer_workbench import build_input, run_writer

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "var/codex_content_handoff_ab_v1_47/codex_v1_48_person1/candidate/codex_attempt_02"
DESTINATION = ROOT / "var/codex_writer_checks/codex_v1_51_writer_model_only"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen3.7-flash-2026-07-15"
PINS = {
    "src/diary_one_ci/x02.py": "b72fe93c3c7cb493f3ef3a5c7e8c60d6f647f1771266effe270c78fdf800f07b",
    "src/diary_one_ci/codex_content_brief.py": "462eb31ba3d33053c925f203755a51356c4c9301d4ca118c6dcfd822d9bfc185",
    "src/diary_one_ci/x01_server.py": "e64d552aa3eac15b753b671aaed5850953015d992f5ff12ca7957e41bcbe700b",
}
SOURCE_SHA = "63bd0cc9082b79d453e5ecced20923a8c85c0a90e9faa1c3fc8cd5158dbc2f8e"
REQUEST_SHAS = (
    "c7deb22190d8284f544b1335176af52f71ccb9ef5ce4149fb1189c06b1007f5f",
    "eed2b44cac102acb5fa5f72d114e4d4d8708b7fd01347efb138963e4fd3eb508",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_body(prompt, schema, model):
    # Exact QwenStageGateway body construction, checked against the live capture.
    suffix = "\nReturn exactly one valid JSON object. Do not include markdown. The object must conform to this schema:\n"
    return {"model": model, "messages": [{"role": "user", "content": [
        {"type": "text", "text": prompt + suffix + json.dumps(schema, ensure_ascii=False)}
    ]}], "response_format": {"type": "json_object"}, "enable_thinking": False, "stream": False}


def prepare():
    for relative, sha in PINS.items():
        assert digest(ROOT / relative) == sha, "Runtime baseline drift: " + relative
    assert digest(SOURCE / "codex_full_run.json") == SOURCE_SHA
    source = json.loads((SOURCE / "codex_full_run.json").read_text())
    records, responses = [], []
    for index, sha in zip((11, 12), REQUEST_SHAS):
        path = SOURCE / ("codex_stage_calls/codex_%03d_request.json" % index)
        assert digest(path) == sha
        records.append(json.loads(path.read_text()))
        responses.append(json.loads(path.with_name("codex_%03d_response.json" % index).read_text()))
    archived_input = json.loads(records[0]["prompt"].rsplit("Input:\n", 1)[1])
    context, excluded = build_input(source)
    assert not excluded
    by_id = {m["candidate_id"]: m for m in context["memories"]}
    assert set(by_id) == {m["candidate_id"] for m in archived_input["memories"]}
    context["memories"] = [by_id[m["candidate_id"]] for m in archived_input["memories"]]
    for archived, rebuilt in zip(archived_input["memories"], context["memories"]):
        if rebuilt["memory_type"] == "AHA":
            assert set(archived["event_fact_ids"]) == set(rebuilt["event_fact_ids"])
            rebuilt["event_fact_ids"] = copy.deepcopy(archived["event_fact_ids"])
    context[brief.POLICY_FIELD] = brief.POLICY_VERSION
    assert brief.writer_input(context) == archived_input
    active = context
    for attempt, record, response in zip((1, 2), records, responses):
        assert not record["evidence"]
        assert record["schema"] == x02.WRITER_SCHEMA
        assert x02._writer_prompt(active, retry=attempt == 2) == record["prompt"]
        hashed = hashlib.sha256(audit_context_bytes({**active, "_x02_policy_version": "V04_1"})).hexdigest()
        assert hashed == record["context_sha256"], "Reconstructed validation context differs"
        _, audit, invalid = x02._validate_writer_output(response["output"], active, attempt=attempt)
        original_audit = [a for a in source["result"]["decision_trace"]["writer_items"]
                          if a["attempt"] == attempt]
        assert audit == original_audit, "Archived validation no longer reproduces"
        if attempt == 1:
            active = x02._writer_retry_context(context, invalid, audit)
    assert [m["memory_type"] for m in context["memories"]] == ["CHAPTER"] * 3 + ["AHA"] * 3
    baseline_body = expected_body(records[0]["prompt"], records[0]["schema"], source["model"])
    return context, baseline_body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    context, baseline_body = prepare()
    description = {
        "scope": "S11_ONLY_MODEL_VARIABLE_NOT_FULL_PIPELINE_OR_DEPLOYMENT",
        "model": MODEL, "maximum_model_calls": 2, "memories": 6,
        "baseline_source_sha256": SOURCE_SHA, "archived_requests_sha256": REQUEST_SHAS,
        "initial_prompt_and_schema_exact_match": True,
        "full_validation_and_retry_context_hashes_match": True,
        "baseline_body_provenance": "RECONSTRUCTED_FROM_ARCHIVED_GATEWAY_INPUT_AND_PINNED_CODE_NOT_ARCHIVED_HTTP",
        "first_request_non_model_sha256": hashlib.sha256(canonical_bytes(
            {k: v for k, v in baseline_body.items() if k != "model"})).hexdigest(),
        "originals_or_images_sent": False, "manual_answers_supplied": False,
    }
    if not args.live:
        print(json.dumps({**description, "status": "OFFLINE_VERIFIED_NO_MODEL_CALL"}), flush=True)
        return
    key, credential_source = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing credential unavailable; no model call made")
    DESTINATION.mkdir(parents=True, exist_ok=False)
    metadata = {
        **description, "recorded_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": ENDPOINT, "credential_source": credential_source,
        "runtime_sha256": PINS, "harness_sha256": digest(Path(__file__)),
        "workbench_sha256": digest(ROOT / "tools/codex_run_writer_workbench.py"),
        "price_cny_per_million": [0.2, 0.8],
        "pricing_basis": "V1_39_OFFICIAL_BEIJING_SNAPSHOT_2026_09_03_FLASH_UNDER_32K_NOT_CURRENT_BILL",
        "copy_quality_status": "AWAITING_REVIEW", "captures": [],
    }
    latest = {}

    def persist(report):
        latest.update(report)
        (DESTINATION / "report.json").write_text(
            json.dumps({**metadata, **latest}, ensure_ascii=False, indent=2) + "\n")

    persist({"status": "PREPARED"})
    adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=60,
                                       base_url=ENDPOINT.rsplit("/chat/completions", 1)[0])
    adapter.input_rate_per_million, adapter.output_rate_per_million = 0.2, 0.8
    adapter.pricing_basis = metadata["pricing_basis"]
    transport = adapter.transport

    def capture(url, headers, body, timeout):
        assert url == ENDPOINT
        index = len(metadata["captures"]) + 1
        assert index <= 2, "Only initial and one bounded repair are authorized"
        payload = json.loads(body)
        assert payload["model"] == MODEL
        assert all(part["type"] == "text" for m in payload["messages"] for part in m["content"])
        if index == 1:
            expected = copy.deepcopy(baseline_body)
            expected["model"] = MODEL
            assert payload == expected, "Initial request changed beyond model"
        entry = {"attempt": index, "request_sha256": hashlib.sha256(body).hexdigest(),
                 "status": "REQUEST_STARTED"}
        metadata["captures"].append(entry)
        (DESTINATION / ("request_%d.json" % index)).write_bytes(body)
        persist({})
        print(json.dumps({"event": "WRITER_CALL_STARTED", "attempt": index}), flush=True)
        status, response_headers, response = transport(url, headers, body, timeout)
        (DESTINATION / ("response_%d.json" % index)).write_bytes(response)
        entry.update(http_status=status, status="HTTP_RETURNED")
        try:
            raw = json.loads(response)
            entry.update(response_model=raw.get("model"), usage=raw.get("usage"),
                         finish_reasons=[c.get("finish_reason") for c in raw.get("choices", [])])
        except (ValueError, AttributeError):
            pass
        persist({})
        print(json.dumps({"event": "WRITER_CALL_RETURNED", "attempt": index, "http_status": status}), flush=True)
        return status, response_headers, response

    adapter.transport = capture
    started = time.monotonic()
    try:
        result = run_writer(context, x02.QwenStageGateway(adapter), persist)
        persist({**result, "status": "COMPLETED"})
    finally:
        captures = metadata["captures"]
        usages = [c.get("usage") for c in captures]
        known = [u for u in usages if isinstance(u, dict)
                 and isinstance(u.get("prompt_tokens"), int) and isinstance(u.get("completion_tokens"), int)]
        known_costs = [(u["prompt_tokens"] * 0.2 + u["completion_tokens"] * 0.8) / 1_000_000
                       for u in known if u["prompt_tokens"] <= 32768]
        persist({"completed_at": datetime.now(timezone.utc).isoformat(),
                 "workbench_wall_ms": round((time.monotonic() - started) * 1000, 3),
                 "totals": {"actual_request_count": len(captures),
                            "known_input_tokens": sum(u["prompt_tokens"] for u in known),
                            "known_output_tokens": sum(u["completion_tokens"] for u in known),
                            "unpriced_call_count": len(captures) - len(known_costs),
                            "known_estimated_cost_cny": sum(known_costs)}})
    print(json.dumps({"report_path": str(DESTINATION / "report.json"),
                      "format_status": latest.get("format_status"), "retry_state": latest.get("retry_state"),
                      "totals": latest["totals"], "narratives": latest.get("narratives")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
