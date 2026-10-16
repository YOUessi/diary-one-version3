"""Isolated real-text comparison: two inputs x two prompts, one call per cell.

Offline by default. No retries, fallback, media upload or runtime policy edits.
Both prompts share the owner's soft length policy; only the focus paragraph differs.
"""
import argparse
import copy
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from diary_one_ci import x02, codex_content_brief as brief
from diary_one_ci.core import canonical_bytes
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key
from codex_run_writer_model_only_v1_51 import prepare as prepare_person1, PINS, digest, expected_body

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "var/codex_writer_checks/codex_v1_53_core_focus"
PERSON2 = ROOT / "var/codex_writer_checks/writer_workbench_v1_40/report.json"
PERSON2_SHA = "357cbb38299c23909d5b60178ae821df98b21105c57db6d93561632c4a7e1278"
MODEL = "qwen3.7-flash-2026-07-15"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
PRICING = "V1_39_BEIJING_SNAPSHOT_2026_09_03_FLASH_UNDER_32K_NOT_CURRENT_BILL"
OLD_FOCUS = (
    "结合主题贴合程度、内容的具体特点和相对其他内容的新增意义，选择最值得说的核心，按需补充细节。"
    "不要逐个列举物体、逐张介绍图片或凑固定数量；素材/封面排序不等于文字重点排序。"
)
NEW_FOCUS = (
    "每条围绕一个由本条事实支持的表达核心，先确定最值得留下的动作、互动或场景特点，再组织句子。"
    "细节只服务这个核心：让它更具体、更有辨识度，或支持画面氛围；去掉后不损失核心的附带属性和背景可以不写。"
    "Chapter 用共同体验概括，不给每张素材平分描述；Aha 留住自己的瞬间，不为覆盖事实而追加无关看点。"
    "不必覆盖全部事实，不设物体或细节数量配额；素材/封面排序不等于文字重点排序。"
)
OLD_LENGTH = "text 是唯一展示文案，一句且最多 20 字；"
SOFT_LENGTH = "text 是唯一展示文案，一句，以 20 字左右为目标，表达完整时允许约 20% 的余量，不为凑字数堆叠细节或截断句子；"


def prompts(context):
    original = x02._writer_prompt(context, retry=False)
    instructions, input_json = original.rsplit("Input:\n", 1)
    assert instructions.count(OLD_LENGTH) == instructions.count(OLD_FOCUS) == 1
    control = instructions.replace(OLD_LENGTH, SOFT_LENGTH)
    candidate = control.replace(OLD_FOCUS, NEW_FOCUS)
    result = {"control": control + "Input:\n" + input_json,
              "candidate": candidate + "Input:\n" + input_json}
    assert result["candidate"].replace(NEW_FOCUS, OLD_FOCUS) == result["control"]
    assert json.loads(input_json) == brief.writer_input(context)
    return result


def prepare():
    person1, _ = prepare_person1()
    assert digest(PERSON2) == PERSON2_SHA
    person2 = copy.deepcopy(json.loads(PERSON2.read_text())["context"])
    assert hashlib.sha256(canonical_bytes(person2)).hexdigest() == "663bb208f78effeeb3bf0b6baf8c069ad98d09278f5d6ea44fa548b973179aa6"
    person2[brief.POLICY_FIELD] = brief.POLICY_VERSION
    contexts = {"person1": person1, "person2": person2}
    plans = []
    for name, context in contexts.items():
        assert len(context["memories"]) == 6
        assert "previous_failures" not in context
        for variant, prompt in prompts(context).items():
            plans.append({"cell": name + "_" + variant, "sample": name,
                          "variant": variant, "context": context, "prompt": prompt,
                          "request_sha256": hashlib.sha256(canonical_bytes(expected_body(
                              prompt, x02.WRITER_SCHEMA, MODEL))).hexdigest()})
    assert len(plans) == 4
    return plans


def diagnose(output, context):
    """Length is observational; all non-length runtime checks remain, in this process only."""
    raw_items = []
    if isinstance(output, dict):
        for field in ("chapters", "ahas"):
            if isinstance(output.get(field), list):
                raw_items.extend(r for r in output[field] if isinstance(r, dict))
    # Temporarily remove the old 20-char gate, not substitute a new 24-char gate.
    # This tool never publishes; review >24 separately without accepting its prose quality.
    max_observed = max([20] + [x02._visible_length(r["text"]) for r in raw_items
                              if isinstance(r.get("text"), str)])
    with patch.object(x02, "AHA_MOMENT_LINE_VISIBLE_MAX", max_observed):
        _, audit, invalid = x02._validate_writer_output(output, context, attempt=1)
    assert x02.AHA_MOMENT_LINE_VISIBLE_MAX == 20
    for row in audit:
        row.pop("required_text_visible_max", None)
        count = row.get("text_visible_characters")
        if row["memory_type"] == "AHA" and isinstance(count, int):
            row["length_observation"] = ("WITHIN_20_TARGET" if count <= 20 else
                                         "WITHIN_OWNER_EXAMPLE_TOLERANCE" if count <= 24 else
                                         "OVER_EXAMPLE_TOLERANCE_REVIEW_ONLY")
    return {"items": audit, "invalid_ids_excluding_length": invalid,
            "scope": "EXISTING_FORMAT_REFERENCE_CHECKS_EXCLUDING_AHA_LENGTH_NOT_FULL_SCHEMA_OR_SEMANTIC_ACCEPTANCE"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    plans = prepare()
    if not args.live:
        # Real-output diagnostic replay only: no fabricated semantic examples.
        prior = json.loads((ROOT / "var/codex_writer_checks/codex_v1_51_writer_model_only/report.json").read_text())
        check = diagnose(prior["attempts"][-1]["output"], plans[0]["context"])
        assert not check["invalid_ids_excluding_length"]
        print(json.dumps({"status": "OFFLINE_VERIFIED_NO_CALL", "maximum_calls": 4,
                          "same_facts_schema_length_model_within_pairs": True,
                          "runtime_policy_unchanged": True,
                          "historical_24_char_item_not_length_rejected": True,
                          "plans": [{k: p[k] for k in ("cell", "request_sha256")} for p in plans]}))
        return
    key, _ = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing Qwen credential unavailable; no call made")
    DEST.mkdir(parents=True, exist_ok=False)  # Do not rerun or overwrite this experiment.
    report = {"status": "RUNNING", "started_at": datetime.now(timezone.utc).isoformat(),
              "scope": "S11_ONLY_4_FIRST_DRAFTS_NOT_FULL_PIPELINE_OR_DEPLOYMENT",
              "model": MODEL, "endpoint": ENDPOINT, "maximum_calls": 4,
              "retry": "DISABLED", "fallback": "DISABLED", "images_sent": False,
              "runtime_sha256": PINS, "person2_source_sha256": PERSON2_SHA,
              "harness_sha256": digest(Path(__file__)), "pricing_basis": PRICING,
              "quality_status": "AWAITING_REVIEW", "cells": []}

    def persist():
        (DEST / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    persist()
    adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=55,
                                       base_url=ENDPOINT.rsplit("/chat/completions", 1)[0])
    adapter.input_rate_per_million, adapter.output_rate_per_million = 0.2, 0.8
    adapter.pricing_basis = PRICING
    original_transport = adapter.transport
    started = time.monotonic()
    try:
        for plan in plans:
            cell = {k: v for k, v in plan.items() if k != "prompt"}
            cell.update(status="PREPARED", actual_requests=0)
            report["cells"].append(cell)
            persist()

            def capture(url, headers, body, timeout):
                assert url == ENDPOINT
                assert cell["actual_requests"] == 0, "No retry allowed"
                assert hashlib.sha256(body).hexdigest() == plan["request_sha256"]
                payload = json.loads(body)
                assert all(p["type"] == "text" for m in payload["messages"] for p in m["content"])
                cell.update(actual_requests=1, status="REQUEST_STARTED")
                (DEST / (plan["cell"] + "_request.json")).write_bytes(body)
                persist()
                status, response_headers, response = original_transport(url, headers, body, timeout)
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
                    "S11_CORE_FOCUS_V1_53", plan["prompt"], x02.WRITER_SCHEMA,
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
        costs = []
        for cell in report["cells"]:
            usage = cell.get("usage")
            if isinstance(usage, dict) and all(isinstance(usage.get(k), int) for k in ("prompt_tokens", "completion_tokens")) and usage["prompt_tokens"] <= 32768:
                cell["estimated_cost_cny"] = (usage["prompt_tokens"] * 0.2 + usage["completion_tokens"] * 0.8) / 1_000_000
                costs.append(cell["estimated_cost_cny"])
        report.update(completed_at=datetime.now(timezone.utc).isoformat(),
                      wall_ms=round((time.monotonic() - started) * 1000, 3),
                      actual_requests=sum(c["actual_requests"] for c in report["cells"]),
                      known_estimated_cost_cny=sum(costs),
                      unpriced_call_count=sum(c["actual_requests"] for c in report["cells"]) - len(costs))
        if report["status"] == "RUNNING":
            report["status"] = "INTERRUPTED_NOT_RERUN"
        persist()
    print(json.dumps({"status": report["status"], "report_path": str(DEST / "report.json"),
                      "actual_requests": report["actual_requests"]}), flush=True)


if __name__ == "__main__":
    main()
