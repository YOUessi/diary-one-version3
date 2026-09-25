"""V1.43 isolated minimal Writer package; one paid call only with --live."""

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

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "var/codex_writer_checks/writer_workbench_v1_40/report.json"
DESTINATION = ROOT / "var/codex_writer_checks/writer_minimal_v1_43"
MODEL = "qwen3.7-flash-2026-07-15"
BASE_CONTEXT_SHA = "663bb208f78effeeb3bf0b6baf8c069ad98d09278f5d6ea44fa548b973179aa6"
PIPELINE_SHA = "4fc7433361959142b8a109be5abfdfaf4b72b27bfa94fcd3eadc7a98334f6d1b"
SERVER_SHA = "e64d552aa3eac15b753b671aaed5850953015d992f5ff12ca7957e41bcbe700b"


def minimal_context(context):
    memories = []
    for source in context["memories"]:
        memory = {"candidate_id": source["candidate_id"], "memory_type": source["memory_type"],
                  "facts": [{"fact_id": f["fact_id"], "text": f["text"]} for f in source["facts"]]}
        if source["memory_type"] == "AHA":
            memory["event_fact_ids"] = list(source["event_fact_ids"])
        memories.append(memory)
    return {"locale": "zh-Hans", "time_evidence": "无可靠拍摄时间；素材排列不是事件先后证据。",
            "memories": memories}


def minimal_prompt(context):
    return f"""你为 Diary One 的记忆卡片写中文短文案。只返回指定 JSON，不输出分析、评分或取舍记录。
每个输入记忆都要返回，放入相应的 chapters 或 ahas，不新增、删除或改变分组。
先选择这段内容最值得记住的具体画面或互动，只有能增加意义时才补充少量细节，不凑数量、不逐物罗列。
像翻相册时自然说的一句话：具体、简洁，可以有画面支持的适度氛围，不写空泛口号。
只依据当前记忆的 facts。不可新增地点、身份、关系、味觉、意图、因果、对话或事件，也不可代替用户宣称感受和偏好。
没有可靠拍摄时间，不把素材排列或事实中的过程性措辞当作已证实的先后行程。不同环境可以并列概括，不编写连接经历。
Chapter 与 Aha 的文字职责应区分，但不能为制造区别而编造新事件。
Chapter：title 通常 {x02.CHAPTER_TITLE_VISIBLE_MIN}–{x02.CHAPTER_TITLE_VISIBLE_TARGET_MAX} 字，必要时最多 {x02.CHAPTER_TITLE_VISIBLE_HARD_MAX} 字；text 默认一句，最多两句；自然表达下尽量不超过 {x02.CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX} 字，不机械截断。
Aha：title 只是内部短标签；text 是唯一展示文案，聚焦一个瞬间，一句且最多 {x02.AHA_MOMENT_LINE_VISIBLE_MAX} 字。只引用 event_fact_ids 指定的事实。
汉字、字母、数字、标点各计一字，空白不计。输出前检查 Aha 长度，必要时自然改写。
chapters 和 ahas 中的每一条都必须含 candidate_id、title、text、claim_ids；claim_ids 是实际支持该文案的本条 fact_id 数组，不得遗漏。
输入：
""" + json.dumps(context, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    baseline = json.loads(BASELINE.read_text())
    original = baseline["context"]
    assert hashlib.sha256(canonical_bytes(original)).hexdigest() == BASE_CONTEXT_SHA
    assert hashlib.sha256(Path(x02.__file__).read_bytes()).hexdigest() == PIPELINE_SHA
    assert hashlib.sha256((ROOT / "src/diary_one_ci/x01_server.py").read_bytes()).hexdigest() == SERVER_SHA
    context = minimal_context(original)
    unchanged_facts = all(new["facts"] == [{"fact_id": f["fact_id"], "text": f["text"]} for f in old["facts"]]
                          for old, new in zip(original["memories"], context["memories"]))
    assert unchanged_facts
    description = {"model": MODEL, "memories": len(context["memories"]), "maximum_calls": 1,
                   "fact_counts": [len(m["facts"]) for m in context["memories"]],
                   "fact_ids_and_text_unchanged": unchanged_facts,
                   "original_context_bytes": len(canonical_bytes(original)),
                   "minimal_context_bytes": len(canonical_bytes(context)), "manual_answers_supplied": False}
    if not args.live:
        print(json.dumps(description))
        return
    key, _ = _resolve_qwen_api_key()
    if not key:
        raise SystemExit("Existing Qwen credential unavailable; no call made")
    DESTINATION.mkdir(parents=True, exist_ok=False)
    report = {**description, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "scope": "S11_MINIMAL_PACKAGE_SINGLE_CALL_NOT_END_TO_END_OR_DEPLOYMENT",
              "baseline_path": str(BASELINE), "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
              "source_run_id": baseline["source_run_id"], "context": context,
              "input_sha256": hashlib.sha256(canonical_bytes(context)).hexdigest(),
              "validation_context_sha256": BASE_CONTEXT_SHA, "active_pipeline_sha256": PIPELINE_SHA,
              "active_server_sha256": SERVER_SHA, "captures": [], "retry": "DISABLED_SINGLE_PASS_EXPERIMENT",
              "quality_status": "AWAITING_REVIEW", "price_cny_per_million": [0.2, 0.8],
              "pricing_basis": baseline["pricing_basis"]}
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
        assert not report["captures"], "Only one model request is allowed"
        payload = json.loads(body)
        assert payload["model"] == MODEL
        assert all(part["type"] == "text" for message in payload["messages"] for part in message["content"])
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
        run = x02.QwenStageGateway(adapter).call("S11_MINIMAL_WRITER_V1_43", minimal_prompt(context),
                                               x02.WRITER_SCHEMA, context={"_x02_policy_version": "V04_1"})
        report.update({"output": run.output, "metric": x02._metric_from_run(run),
                       "estimated_cost_cny": run.estimated_cost_native})
        persist()
        accepted, audit, invalid = x02._validate_writer_output(run.output, original, attempt=1)
        report.update({"narratives": accepted, "writer_audit": audit, "invalid_ids": invalid})
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
