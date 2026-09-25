"""S11-only, model-only comparison on the three authorized real failure cases.

No network without --live. Exactly four single-use slots; no automatic retries.
Never imported by the active pipeline, never writes over a user's run/review.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "var/codex_writer_checks/ae973dc4-6e3b-4db1-9763-ed431b977e11"
OUTPUT = ROOT / "var/codex_writer_checks/model_comparison_v1_39"
MODELS = {
    "flash": ("qwen3.7-flash-2026-07-15", 0.2, 0.8),
    "plus": ("qwen3.7-plus-2026-05-26", 2.0, 8.0),
}
PRICING_URL = "https://help.aliyun.com/zh/model-studio/model-pricing"


def model_only_request(baseline, model):
    request = copy.deepcopy(baseline)
    request["model"] = model
    # The authorized workload is exclusively existing text, not raw images.
    assert request["enable_thinking"] is False
    assert request["response_format"] == {"type": "json_object"}
    assert request["stream"] is False
    for message in request["messages"]:
        assert all(item["type"] == "text" for item in message["content"])
    return request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=MODELS)
    parser.add_argument("--round", type=int, required=True, choices=(1, 2))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    model, input_rate, output_rate = MODELS[args.model]
    original = json.loads((BASELINE / "request.json").read_text())
    source = json.loads((BASELINE / "report.json").read_text())
    request = model_only_request(original, model)
    context = source["context"]
    if not args.live:
        print(json.dumps({"model": model, "round": args.round, "only_changed_field": "model",
                          "price_cny_per_million": [input_rate, output_rate],
                          "request_sha256": hashlib.sha256(canonical_bytes(request)).hexdigest()}))
        return
    key, _ = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing Qwen credential unavailable; no call made")
    slot = OUTPUT / (args.model + "_" + str(args.round))
    slot.mkdir(parents=True, exist_ok=False)
    body = canonical_bytes(request)
    (slot / "request.json").write_bytes(body)
    without_model = {key: value for key, value in request.items() if key != "model"}
    report = {
        "scope": "S11_ONLY_MODEL_COMPARISON_NOT_FULL_PIPELINE_NOT_USER_QUALITY_ACCEPTANCE",
        "source": source["source"], "slot": slot.name, "model": model,
        "request_sha256": hashlib.sha256(body).hexdigest(),
        "non_model_request_sha256": hashlib.sha256(canonical_bytes(without_model)).hexdigest(),
        "baseline_request_sha256": source["request_sha256"],
        "only_changed_request_field": "model",
        "price_cny_per_million": [input_rate, output_rate], "pricing_url": PRICING_URL,
        "pricing_checked_date": "2026-09-03", "context": context,
        "active_pipeline_sha256": hashlib.sha256(Path(x02.__file__).read_bytes()).hexdigest(),
    }
    adapter = QwenChatCompletionsAdapter(
        api_key=key, model=model, timeout_seconds=60,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    adapter.input_rate_per_million = input_rate
    adapter.output_rate_per_million = output_rate
    adapter.pricing_basis = "alibaba-beijing-public-rate-2026-09-03-input-under-32k"
    transport = adapter.transport

    def fixed_request_transport(url, headers, _generated_body, timeout):
        assert url == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        status, response_headers, response = transport(url, headers, body, timeout)
        # Response content is retained locally, never auth/request headers.
        (slot / "response.json").write_bytes(response)
        report["http_status"] = status
        try:
            payload = json.loads(response)
            report["response_model"] = payload.get("model")
            report["finish_reasons"] = [item.get("finish_reason") for item in payload.get("choices", [])]
        except (ValueError, AttributeError):
            pass
        return status, response_headers, response

    adapter.transport = fixed_request_transport
    try:
        run = x02.QwenStageGateway(adapter).call(
            "S11_WRITER_ATTEMPT_2", "Request replaced by the unchanged archived body.",
            x02.WRITER_SCHEMA, context=context,
        )
        narratives, audit, invalid = x02._validate_writer_output(run.output, context, attempt=2)
        report.update(output=run.output, audit=audit, invalid_ids=invalid,
                      accepted_count=len(narratives), metric=x02._metric_from_run(run),
                      estimated_cost_cny=run.estimated_cost_native)
    except x02.X02StageCallError as exc:
        report.update(error=exc.code, metric=x02._metric_from_run(exc.stage_run))
    finally:
        (slot / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"report_path": str(slot / "report.json"), "model": model,
                      "accepted_count": report.get("accepted_count"), "error": report.get("error"),
                      "metric": report.get("metric"), "estimated_cost_cny": report.get("estimated_cost_cny"),
                      "drafts": [{"text": a.get("draft_text"), "count": a.get("text_visible_characters"),
                                  "status": a["validation_status"]} for a in report.get("audit", [])]},
                     ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
