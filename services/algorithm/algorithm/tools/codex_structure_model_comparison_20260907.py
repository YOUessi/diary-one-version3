"""B2: eight fixed, text-only S07 calls; only the requested model changes.

No runtime edits, semantic repair, hidden retries, images or review answers.
Frozen B1 helpers verify source and reconstruct the original A input.
"""
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request

import codex_structure_hint_ablation_20260907 as base

ROOT = base.ROOT
AREA = ROOT / "var/codex_structure_model_comparison_20260907"
MODELS = {"A": base.MODEL, "B": "qwen3.7-plus-2026-05-26"}
HELPERS = {
    "tools/codex_structure_hint_ablation_20260907.py": "968e6e8978172300cf68cff0ba8f87181f9aa16f3d3be93dd36ae7da974abd00",
    "tools/codex_summarize_hint_ablation_20260907.py": "9eeb1767fb2f6d2f86e43667b7ad0a8bacedf270d697e17b5073489355c6c165",
}
PRICING = {
    "A": "https://help.aliyun.com/zh/model-studio/qwen3-vl-flash",
    "B": "https://help.aliyun.com/zh/model-studio/qwen3-7-plus",
}


def verify():
    candidate = base.verify_source()
    for name, expected in HELPERS.items():
        base.require(base.sha(ROOT / name) == expected, "Diagnostic helper drift: " + name)
    return candidate


def digest(value):
    return hashlib.sha256(base.canonical_bytes(value)).hexdigest()


def prepare():
    candidate = verify()
    base.require(not AREA.exists(), "Refusing to overwrite experiment")
    files, inputs = {}, []
    for pack in (1, 2):
        request, _ = base.requests_for(pack)
        original = base.build_body(request)
        old_provider = base.load(base.OLD / ("pack_%d/round_1/codex_stage_calls/codex_%03d_provider.json" % (pack, base.PINS[pack][0])))
        base.require(digest(original) == old_provider["request_body_sha256"], "Original HTTP input drift")
        files["pack_%d_request.json" % pack] = request
        for condition, model in MODELS.items():
            body = {**original, "model": model}
            base.require({k: v for k, v in body.items() if k != "model"} ==
                         {k: v for k, v in original.items() if k != "model"}, "Non-model input changed")
            files["pack_%d_%s_body.json" % (pack, condition)] = body
            inputs.append({"pack": pack, "condition": condition, "model": model,
                "body_sha256": digest(body), "non_model_sha256": digest({k: v for k, v in body.items() if k != "model"}),
                "observations": len(request["context"]["observations"]),
                "facts": sum(len(o["facts"]) for o in request["context"]["observations"])})
    AREA.mkdir()
    for name, value in files.items():
        base.save(AREA / name, value)
    base.save(AREA / "codex_preparation.json", {
        "experiment": "CODEX_B2_S07_MODEL_ONLY_20260907", "created_at": base.now(),
        "harness_sha256": base.sha(__file__), "helpers_sha256": HELPERS,
        "candidate_sha256": base.CANDIDATE_SHA, "source_sha256": candidate["source_sha256"],
        "files_sha256": {name: base.sha(AREA / name) for name in files}, "inputs": inputs,
        "models": MODELS, "endpoint": base.ENDPOINT,
        "slots": [{"slot": i + 1, "pack": p, "condition": c, "repeat": r} for i, (p, c, r) in enumerate(base.SLOTS)],
        "changed_http_fields": ["model"], "enable_thinking": False,
        "client_sampling_parameters": "UNCHANGED_UNSPECIFIED_DEFAULTS; provider internals not controlled",
        "external_payload": "ORIGINAL_A_ARCHIVED_FACT_TEXT_ONLY_NO_IMAGES_OR_ORIGINALS_OR_REVIEW_ANSWERS",
        "scope": "S07_ONLY_NOT_FULL_PIPELINE_OR_WEB_OR_APP", "max_http_attempts": 8, "retries_per_slot": 0,
        "review_axes": ["real_experience_grouping", "useful_coverage_without_quota_filling", "chapter_aha_relation", "unsupported_sequence", "reference_integrity"],
        "pricing_sources": PRICING, "pricing_verified_date": "2026-09-07",
        "pricing_basis": "BEIJING_PUBLIC_INPUT_OUTPUT_LIST_PRICE_EXCLUDING_DISCOUNTS_CACHE_AND_CREDITS_NOT_ACCOUNT_BILL",
    })
    base.emit({"event": "PREPARED_NO_API_CALL", "inputs": inputs, "only_model_changes": True})


def usage_for(raw, condition):
    old = base.provider_usage(raw)
    if old is None:
        return None
    incoming, outgoing = old["input_tokens"], old["output_tokens"]
    if condition == "A":
        input_rate = 0.15 if incoming <= 32768 else 0.30 if incoming <= 131072 else 0.60
        output_rate = input_rate * 10
    else:
        input_rate, output_rate = (2, 8) if incoming <= 256000 else (6, 24)
    return {"input_tokens": incoming, "output_tokens": outgoing,
            "input_cny_per_million": input_rate, "output_cny_per_million": output_rate,
            "list_price_estimated_cny": (incoming * input_rate + outgoing * output_rate) / 1_000_000,
            "basis": "BEIJING_PUBLIC_LIST_PRICE_NOT_ACCOUNT_BILL"}


def run_all():
    verify()
    prep = base.load(AREA / "codex_preparation.json")
    base.require(prep["harness_sha256"] == base.sha(__file__), "Prepared harness drift")
    for name, expected in prep["files_sha256"].items():
        base.require(base.sha(AREA / name) == expected, "Prepared input drift")
    base.require(not (AREA / "codex_execution_started.json").exists(), "Execution already attempted; no automatic rerun")
    key, source = base._resolve_qwen_api_key()
    base.require(bool(key), "Existing research credential unavailable; nothing sent")
    base.save(AREA / "codex_execution_started.json", {"started_at": base.now(), "credential_source": source,
        "preparation_sha256": base.sha(AREA / "codex_preparation.json")})
    results = []
    for slot in prep["slots"]:
        directory = AREA / ("slot_%02d" % slot["slot"])
        directory.mkdir()
        request = base.load(AREA / ("pack_%d_request.json" % slot["pack"]))
        expected = base.load(AREA / ("pack_%d_%s_body.json" % (slot["pack"], slot["condition"])))
        transports = []

        def transport(url, headers, body, timeout):
            base.require(url == base.ENDPOINT and json.loads(body) == expected, "Payload/destination drift")
            base.require(not transports, "Retries prohibited")
            transports.append({})
            base.save(directory / "codex_request.json", expected)
            base.save(directory / "codex_attempt.json", {**slot, "started_at": base.now(), "body_sha256": hashlib.sha256(body).hexdigest()})
            base.emit({"event": "CALL_STARTED", **slot, "model": expected["model"]})
            req = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            started = time.monotonic()
            try:
                try:
                    with opener.open(req, timeout=180) as response:
                        status, response_headers, raw = response.status, dict(response.headers.items()), response.read()
                except urllib.error.HTTPError as exc:
                    status, response_headers, raw = exc.code, dict(exc.headers.items()), exc.read()
                clean = raw.decode("utf-8", errors="replace").replace(key, "[REDACTED]")
                try:
                    parsed = json.loads(clean)
                except ValueError:
                    parsed = {"unparsed_response": clean}
                choices = parsed.get("choices", []) if isinstance(parsed, dict) else []
                record = {"http_status": status, "payload": parsed, "usage": usage_for(parsed, slot["condition"]),
                    "provider_model": parsed.get("model") if isinstance(parsed, dict) else None,
                    "finish_reasons": [c.get("finish_reason") for c in choices],
                    "duration_seconds": time.monotonic() - started, "completed_at": base.now()}
                base.save(directory / "codex_provider.json", record)
                transports[-1].update(record)
                return status, response_headers, raw
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                record = {"http_status": None, "usage": None, "error_type": type(exc).__name__,
                    "duration_seconds": time.monotonic() - started, "status": "NO_HTTP_RESPONSE"}
                base.save(directory / "codex_transport_failure.json", record)
                transports[-1].update(record)
                raise

        record = {**slot, "model": expected["model"], "started_at": base.now()}
        started = time.monotonic()
        adapter = base.QwenChatCompletionsAdapter(api_key=key, model=expected["model"], timeout_seconds=180,
            base_url=base.ENDPOINT.rsplit("/chat/completions", 1)[0], transport=transport)
        try:
            result = base.x02.QwenStageGateway(adapter).call(request["stage"], request["prompt"], request["schema"], context=request["context"])
            record.update(status="RETURNED_FOR_REVIEW", output=result.output, request_id=result.request_id)
        except Exception as exc:
            record.update(status="FAILED", error_type=type(exc).__name__, code=getattr(exc, "code", None))
        provider = transports[-1] if transports else {}
        record.update({k: provider.get(k) for k in ("usage", "http_status", "provider_model", "finish_reasons")})
        record.update(duration_seconds=time.monotonic() - started, completed_at=base.now(),
                      transport_attempts=len(transports), quality_status="NOT_AUTOMATICALLY_SCORED")
        base.save(directory / "codex_result.json", record)
        results.append({k: v for k, v in record.items() if k != "output"})
        base.emit({"event": "CALL_FINISHED", **results[-1]})
        if record["http_status"] != 200 or record["provider_model"] != expected["model"]:
            break  # No silent model/contract fallback after unsupported or failed requests.
    known = [r["usage"] for r in results if r["usage"] is not None]
    summary = {"completed_at": base.now(), "results": results, "planned_slots": 8,
        "attempted_slots": len(results), "not_run_slots": prep["slots"][len(results):],
        "http_attempts": sum(r["transport_attempts"] for r in results),
        "known_input_tokens": sum(u["input_tokens"] for u in known),
        "known_output_tokens": sum(u["output_tokens"] for u in known),
        "list_price_estimated_cny_known": sum(u["list_price_estimated_cny"] for u in known),
        "usage_unknown_slots": len(results) - len(known), "full_pipeline_executed": False,
        "source_unchanged_after_execution": bool(verify()), "quality_status": "AWAITING_CONTENT_REVIEW"}
    base.save(AREA / "codex_execution_summary.json", summary)
    base.emit({"event": "EXPERIMENT_FINISHED", **{k: v for k, v in summary.items() if k != "results"}})


def summarize():
    verify()
    import codex_summarize_hint_ablation_20260907 as reviewer
    reviewer.AREA = AREA
    reviewer.main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "summarize"))
    globals()[{"prepare": "prepare", "run": "run_all", "summarize": "summarize"}[parser.parse_args().command]]()
