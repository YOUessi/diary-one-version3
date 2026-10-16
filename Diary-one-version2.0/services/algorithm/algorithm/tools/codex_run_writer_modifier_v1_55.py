"""V1.55 isolated Writer experiment. Offline by default; four first drafts at most."""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key
from codex_prepare_writer_modifier_v1_55 import prepare, ROOT, DRAFT, PRIOR_SHA
from codex_run_writer_core_focus_v1_53 import MODEL, ENDPOINT, PRICING, diagnose
from codex_run_writer_model_only_v1_51 import PINS, digest

DEST = ROOT / "var/codex_writer_checks/codex_v1_55_modifier_selection"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    plans = prepare()
    if not args.live:
        print(json.dumps({"status": "OFFLINE_VERIFIED_NO_CALL", "maximum_calls": len(plans),
                          "plans": [{k: p[k] for k in ("cell", "request_sha256")} for p in plans]}))
        return
    key, _ = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing Qwen credential unavailable; no call made")
    DEST.mkdir(parents=True, exist_ok=False)
    report = {
        "status": "RUNNING", "started_at": datetime.now(timezone.utc).isoformat(),
        "scope": "S11_V1_55_TWO_PACKS_FOUR_FIRST_DRAFTS_NOT_FULL_PIPELINE_OR_DEPLOYMENT",
        "model": MODEL, "endpoint": ENDPOINT, "maximum_calls": 4,
        "retry": "DISABLED", "fallback": "DISABLED", "images_sent": False,
        "runtime_sha256": PINS, "source_report_sha256": PRIOR_SHA,
        "editorial_draft_sha256": digest(DRAFT), "harness_sha256": digest(Path(__file__)),
        "preparer_sha256": digest(ROOT / "tools/codex_prepare_writer_modifier_v1_55.py"),
        "pricing_basis": PRICING, "quality_status": "AWAITING_REVIEW", "cells": [],
    }

    def persist():
        (DEST / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    persist()
    adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=55,
                                       base_url=ENDPOINT.rsplit("/chat/completions", 1)[0])
    adapter.input_rate_per_million, adapter.output_rate_per_million = 0.2, 0.8
    adapter.pricing_basis = PRICING
    transport = adapter.transport
    started = time.monotonic()
    try:
        for plan in plans:
            cell = {k: v for k, v in plan.items() if k not in ("prompt", "body")}
            cell.update(status="PREPARED", actual_requests=0)
            report["cells"].append(cell)
            persist()

            def capture(url, headers, body, timeout):
                assert url == ENDPOINT
                assert cell["actual_requests"] == 0, "No second request for a cell"
                assert sum(c["actual_requests"] for c in report["cells"]) < 4
                assert hashlib.sha256(body).hexdigest() == plan["request_sha256"]
                assert json.loads(body) == plan["body"]
                cell.update(actual_requests=1, status="REQUEST_STARTED")
                (DEST / (plan["cell"] + "_request.json")).write_bytes(body)
                persist()
                status, response_headers, response = transport(url, headers, body, timeout)
                (DEST / (plan["cell"] + "_response.json")).write_bytes(response)
                cell.update(http_status=status, status="HTTP_RETURNED")
                try:
                    raw = json.loads(response)
                    cell.update(response_model=raw.get("model"), usage=raw.get("usage"),
                                finish_reasons=[c.get("finish_reason") for c in raw.get("choices", [])])
                except (ValueError, AttributeError):
                    pass
                persist()
                return status, response_headers, response

            adapter.transport = capture
            print(json.dumps({"event": "START", "cell": plan["cell"]}), flush=True)
            try:
                run = x02.QwenStageGateway(adapter).call(
                    "S11_MODIFIER_SELECTION_V1_55", plan["prompt"], x02.WRITER_SCHEMA,
                    context={**plan["context"], "_x02_policy_version": "V04_1"})
                cell.update(output=run.output, metric=x02._metric_from_run(run),
                            diagnostic=diagnose(run.output, plan["context"]), status="COMPLETED")
            except x02.X02StageCallError as exc:
                cell.update(status="FAILED_NO_RETRY", error=exc.code,
                            metric=x02._metric_from_run(exc.stage_run))
            persist()
            print(json.dumps({"event": "FINISHED", "cell": plan["cell"], "status": cell["status"]}), flush=True)
        report["status"] = "COMPLETED" if all(c["status"] == "COMPLETED" for c in report["cells"]) else "COMPLETED_WITH_FAILURES"
    finally:
        costs, usages = [], []
        for cell in report["cells"]:
            usage = cell.get("usage")
            if isinstance(usage, dict) and all(isinstance(usage.get(k), int) for k in ("prompt_tokens", "completion_tokens")):
                usages.append(usage)
                if usage["prompt_tokens"] <= 32768:
                    cell["estimated_cost_cny"] = (usage["prompt_tokens"] * 0.2 + usage["completion_tokens"] * 0.8) / 1_000_000
                    costs.append(cell["estimated_cost_cny"])
        actual = sum(c["actual_requests"] for c in report["cells"])
        report.update(completed_at=datetime.now(timezone.utc).isoformat(),
                      wall_ms=round((time.monotonic() - started) * 1000, 3),
                      actual_requests=actual, known_estimated_cost_cny=sum(costs),
                      known_input_tokens=sum(u["prompt_tokens"] for u in usages),
                      known_output_tokens=sum(u["completion_tokens"] for u in usages),
                      usage_unknown_call_count=actual - len(usages), unpriced_call_count=actual - len(costs))
        if report["status"] == "RUNNING":
            report["status"] = "INTERRUPTED_NOT_RERUN"
        persist()
    print(json.dumps({"status": report["status"], "report_path": str(DEST / "report.json"),
                      "actual_requests": report["actual_requests"]}), flush=True)


if __name__ == "__main__":
    main()
