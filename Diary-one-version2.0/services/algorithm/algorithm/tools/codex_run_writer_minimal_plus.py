"""V1.44: one isolated Plus call, changing only V1.43's model field.

Default invocation is offline. --live uses one exclusive output slot, no retry.
"""

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key

import codex_run_writer_minimal as baseline_tool
from codex_compare_writer_models import model_only_request

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "var/codex_writer_checks/writer_minimal_v1_43"
DESTINATION = ROOT / "var/codex_writer_checks/writer_minimal_plus_v1_44"
MODEL = "qwen3.7-plus-2026-05-26"
BASE_REQUEST_SHA = "b32e32c7d093df23d67b902d656b9544d5fdaf469219da74f19295e515252c7f"


def prepare():
    source = json.loads((BASELINE / "report.json").read_text())
    original_bytes = (BASELINE / "request.json").read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest() == BASE_REQUEST_SHA
    original = json.loads(original_bytes)
    assert original["model"] == baseline_tool.MODEL
    request = model_only_request(original, MODEL)
    assert [k for k in request if request[k] != original[k]] == ["model"]
    full = json.loads(baseline_tool.BASELINE.read_text())["context"]
    assert hashlib.sha256(canonical_bytes(full)).hexdigest() == baseline_tool.BASE_CONTEXT_SHA
    assert source["context"] == baseline_tool.minimal_context(full)
    assert hashlib.sha256(Path(x02.__file__).read_bytes()).hexdigest() == baseline_tool.PIPELINE_SHA
    assert hashlib.sha256((ROOT / "src/diary_one_ci/x01_server.py").read_bytes()).hexdigest() == baseline_tool.SERVER_SHA
    prompt = baseline_tool.minimal_prompt(source["context"])
    suffix = "\nReturn exactly one valid JSON object. Do not include markdown. The object must conform to this schema:\n"
    expected_messages = [{"role": "user", "content": [{"type": "text", "text": prompt + suffix + json.dumps(x02.WRITER_SCHEMA, ensure_ascii=False)}]}]
    assert request["messages"] == expected_messages
    return source, full, request, prompt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    source, validation_context, request, prompt = prepare()
    non_model = {k: v for k, v in request.items() if k != "model"}
    description = {
        "model": MODEL, "memories": len(source["context"]["memories"]), "maximum_calls": 1,
        "only_changed_request_field": "model", "price_cny_per_million": [2.0, 8.0],
        "baseline_request_sha256": BASE_REQUEST_SHA,
        "request_sha256": hashlib.sha256(canonical_bytes(request)).hexdigest(),
        "non_model_request_sha256": hashlib.sha256(canonical_bytes(non_model)).hexdigest(),
    }
    if not args.live:
        print(json.dumps(description))
        return
    key, _ = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing Qwen credential unavailable; no call made")
    DESTINATION.mkdir(parents=True, exist_ok=False)
    report = {
        **description, "recorded_at": datetime.now(timezone.utc).isoformat(),
        "scope": "S11_MODEL_ONLY_SINGLE_CALL_NOT_END_TO_END_OR_DEPLOYMENT",
        "source_run_id": source["source_run_id"], "baseline_path": str(BASELINE / "report.json"),
        "baseline_sha256": hashlib.sha256((BASELINE / "report.json").read_bytes()).hexdigest(),
        "context": source["context"], "input_sha256": source["input_sha256"],
        "validation_context_sha256": baseline_tool.BASE_CONTEXT_SHA,
        "active_pipeline_sha256": baseline_tool.PIPELINE_SHA,
        "active_server_sha256": baseline_tool.SERVER_SHA,
        "captures": [], "retry": "DISABLED_SINGLE_PASS_EXPERIMENT",
        "quality_status": "AWAITING_REVIEW", "manual_answers_supplied": False,
        "pricing_basis": "V1_39_OFFICIAL_BEIJING_SNAPSHOT_2026_09_03_PLUS_UNDER_32K",
    }

    def persist():
        (DESTINATION / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    persist()
    adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=60,
                                       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    adapter.input_rate_per_million, adapter.output_rate_per_million = 2.0, 8.0
    adapter.pricing_basis = report["pricing_basis"]
    transport = adapter.transport

    def capture(url, headers, body, timeout):
        assert url == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        assert not report["captures"], "Only one model request is allowed"
        assert body == canonical_bytes(request), "Actual request changed beyond model"
        entry = {"request_sha256": hashlib.sha256(body).hexdigest()}
        report["captures"].append(entry)
        (DESTINATION / "request.json").write_bytes(body)
        persist()
        status, response_headers, response = transport(url, headers, body, timeout)
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
        run = x02.QwenStageGateway(adapter).call("S11_MINIMAL_PLUS_WRITER_V1_44", prompt,
                                               x02.WRITER_SCHEMA, context={"_x02_policy_version": "V04_1"})
        report.update(output=run.output, metric=x02._metric_from_run(run),
                      estimated_cost_cny=run.estimated_cost_native)
        persist()
        accepted, audit, invalid = x02._validate_writer_output(run.output, validation_context, attempt=1)
        report.update(narratives=accepted, writer_audit=audit, invalid_ids=invalid)
    except x02.X02StageCallError as exc:
        report.update(error=exc.code, metric=x02._metric_from_run(exc.stage_run),
                      estimated_cost_cny=exc.stage_run.estimated_cost_native)
    finally:
        report["workbench_wall_ms"] = round((time.monotonic() - started) * 1000, 3)
        persist()
    print(json.dumps({"report_path": str(DESTINATION / "report.json"), "error": report.get("error"),
                      "metric": report.get("metric"), "estimated_cost_cny": report.get("estimated_cost_cny"),
                      "invalid_ids": report.get("invalid_ids"), "output": report.get("output")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
