"""B3: four fixed Plus S07 calls using request-local short references.

Only observation/fact reference values change. No prose rewrites, semantic
rules, fuzzy repair, retries or runtime/Web changes. B2 remains immutable.
"""
import argparse
import copy
import json
import time
import urllib.error
import urllib.request

import codex_structure_model_comparison_20260907 as previous

base = previous.base
ROOT = base.ROOT
AREA = ROOT / "var/codex_structure_short_refs_20260907"
MODEL = previous.MODELS["B"]
PINS = {
    "tools/codex_structure_model_comparison_20260907.py": "8a0a56401b04bdcf0f3f6c2aa03e8b562c654e1059bc24f7f489f3e593f5c0a0",
    "var/codex_structure_model_comparison_20260907/codex_preparation.json": "d08bdc27f15992052c4cb75bfe6cb470aa3220295ac0308bb9b241512da6353f",
    "var/codex_structure_model_comparison_20260907/codex_execution_summary.json": "2cc3e26ba5d78c3cbe28496fbbb72ffc6c8aeca6057e2efc973cf67b53d60f20",
}
# Two repeats, both packs; historical B2 Plus controls, no new long-ID calls.
SLOTS = ((1, 1, 2), (2, 1, 3), (1, 2, 5), (2, 2, 8))
REF_KINDS = {k: "observations" for k in ("observation_id", "observation_ids")}
REF_KINDS.update({k: "facts" for k in ("fact_id", "fact_ids", "event_fact_ids", "chapter_fact_ids", "aha_fact_ids")})


def verify():
    candidate = previous.verify()
    for name, expected in PINS.items():
        base.require(base.sha(ROOT / name) == expected, "B2 baseline drift: " + name)
    old_prep = base.load(previous.AREA / "codex_preparation.json")
    for name, expected in old_prep["files_sha256"].items():
        base.require(base.sha(previous.AREA / name) == expected, "B2 input drift: " + name)
    return candidate


def transform(value, maps, field=None, path=(), unknown=None):
    """Translate only typed reference fields by exact match; leave prose intact."""
    if isinstance(value, dict):
        return {k: transform(v, maps, k, path + (k,), unknown) for k, v in value.items()}
    if isinstance(value, list):
        return [transform(v, maps, field, path + (i,), unknown) for i, v in enumerate(value)]
    if isinstance(value, str) and field in REF_KINDS:
        table = maps[REF_KINDS[field]]
        if value in table:
            return table[value]
        if unknown is not None:
            unknown.append({"path": list(path), "unmapped_reference": value})
    return value


def maps_for(context):
    observations, facts = {}, {}
    for obs in context["observations"]:
        base.require(obs["observation_id"] not in observations, "Duplicate input observation ID")
        observations[obs["observation_id"]] = "O%02d" % (len(observations) + 1)
        for fact in obs["facts"]:
            base.require(fact["fact_id"] not in facts, "Duplicate input fact ID")
            facts[fact["fact_id"]] = "F%02d" % (len(facts) + 1)
    forward = {"observations": observations, "facts": facts}
    reverse = {kind: {short: long for long, short in table.items()} for kind, table in forward.items()}
    base.require(all(len(reverse[k]) == len(v) for k, v in forward.items()), "Non-bijective reference mapping")
    return {"forward": forward, "reverse": reverse}


def prepare():
    candidate = verify()
    base.require(not AREA.exists(), "Refusing to overwrite experiment")
    files, inputs, baseline_files, replay_count = {}, [], {}, 0
    for pack in (1, 2):
        original = base.load(previous.AREA / ("pack_%d_request.json" % pack))
        mapping = maps_for(original["context"])
        prefix, input_text = original["prompt"].rsplit("Input:\n", 1)
        raw_input = json.loads(input_text)
        unknown = []
        short_input = transform(raw_input, mapping["forward"], unknown=unknown)
        base.require(not unknown, "Input contains unknown observation/fact references")
        changed = copy.deepcopy(original)
        changed["context"] = transform(original["context"], mapping["forward"])
        changed["prompt"] = prefix + "Input:\n" + json.dumps(short_input, ensure_ascii=False)
        base.require(transform(short_input, mapping["reverse"]) == raw_input, "Input round-trip changed information")
        base.require(transform(changed["context"], mapping["reverse"]) == original["context"], "Audit context drift")
        base.require([f["text"] for o in short_input["observations"] for f in o["facts"]] ==
                     [f["text"] for o in raw_input["observations"] for f in o["facts"]], "Fact prose changed")
        body = {**base.build_body(changed), "model": MODEL}
        original_body = base.load(previous.AREA / ("pack_%d_B_body.json" % pack))
        rebuilt = copy.deepcopy(changed)
        rebuilt["context"] = transform(changed["context"], mapping["reverse"])
        rebuilt["prompt"] = prefix + "Input:\n" + json.dumps(transform(short_input, mapping["reverse"]), ensure_ascii=False)
        base.require({**base.build_body(rebuilt), "model": MODEL} == original_body, "Non-reference HTTP body drift")
        for slot in base.load(previous.AREA / "codex_execution_summary.json")["results"]:
            if slot["pack"] != pack:
                continue
            path = previous.AREA / ("slot_%02d/codex_result.json" % slot["slot"])
            raw = base.load(path)["output"]
            replay = transform(transform(raw, mapping["forward"]), mapping["reverse"])
            base.require(replay == raw, "Real archived output changed in codec round-trip")
            baseline_files[str(path.relative_to(ROOT))] = base.sha(path)
            replay_count += 1
        files["pack_%d_request.json" % pack] = changed
        files["pack_%d_SHORT_body.json" % pack] = body
        files["pack_%d_reference_map.json" % pack] = mapping
        inputs.append({"pack": pack, "observations": len(mapping["forward"]["observations"]),
            "facts": len(mapping["forward"]["facts"]), "original_body_sha256": previous.digest(original_body),
            "short_body_sha256": previous.digest(body), "original_body_bytes": len(base.canonical_bytes(original_body)),
            "short_body_bytes": len(base.canonical_bytes(body)), "round_trip_exact": True})
    AREA.mkdir()
    for name, value in files.items():
        base.save(AREA / name, value)
    base.save(AREA / "codex_preparation.json", {
        "experiment": "CODEX_B3_S07_SHORT_REFERENCES_20260907", "created_at": base.now(),
        "harness_sha256": base.sha(__file__), "baseline_pins": {**PINS, **baseline_files},
        "candidate_sha256": base.CANDIDATE_SHA, "source_sha256": candidate["source_sha256"],
        "files_sha256": {name: base.sha(AREA / name) for name in files}, "inputs": inputs,
        "slots": [{"slot": i + 1, "pack": p, "condition": "SHORT", "repeat": r, "historical_control_slot": c}
                  for i, (p, r, c) in enumerate(SLOTS)],
        "model": MODEL, "endpoint": base.ENDPOINT, "enable_thinking": False,
        "reference_fields": list(REF_KINDS), "changed": "EXACT_REFERENCE_VALUES_ONLY",
        "short_ids_meaning": "REQUEST_LOCAL_IDENTIFIERS_NOT_CAPTURE_TIME_OR_SCENE_CATEGORIES",
        "external_payload": "ARCHIVED_DERIVED_TEXT_ONLY_NO_IMAGES_OR_ORIGINALS_OR_MAP_TO_LONG_IDS_OR_REVIEW_ANSWERS",
        "scope": "S07_ONLY_NOT_FULL_PIPELINE_OR_WEB_OR_APP", "max_http_attempts": 4, "retries_per_slot": 0,
        "historical_control_limitation": "NOT_SIMULTANEOUS_RANDOMIZED_AB; B2 Plus calls are reused, not newly repeated",
        "offline_checks": {"input_round_trip_exact_packs": 2, "real_output_round_trip_exact": replay_count,
                           "synthetic_semantic_cases": 0, "old_invalid_ids_repaired": 0},
        "pricing_snapshot": {"date": "2026-09-07", "source": previous.PRICING["B"],
                             "input_cny_per_million_under_256k": 2, "output_cny_per_million_under_256k": 8},
    })
    base.emit({"event": "PREPARED_NO_API_CALL", "inputs": inputs, "real_output_round_trips": replay_count})


def run_all():
    verify()
    prep = base.load(AREA / "codex_preparation.json")
    base.require(prep["harness_sha256"] == base.sha(__file__), "Frozen harness drift")
    for name, expected in prep["files_sha256"].items():
        base.require(base.sha(AREA / name) == expected, "Prepared input drift")
    for name, expected in prep["baseline_pins"].items():
        base.require(base.sha(ROOT / name) == expected, "Archived baseline drift")
    base.require(not (AREA / "codex_execution_started.json").exists(), "Already attempted; no automatic rerun")
    key, source = base._resolve_qwen_api_key()
    base.require(bool(key), "Existing research credential unavailable; nothing sent")
    base.save(AREA / "codex_execution_started.json", {"started_at": base.now(), "credential_source": source,
        "preparation_sha256": base.sha(AREA / "codex_preparation.json")})
    results = []
    for slot in prep["slots"]:
        directory = AREA / ("slot_%02d" % slot["slot"])
        directory.mkdir()
        request = base.load(AREA / ("pack_%d_request.json" % slot["pack"]))
        expected = base.load(AREA / ("pack_%d_SHORT_body.json" % slot["pack"]))
        mapping = base.load(AREA / ("pack_%d_reference_map.json" % slot["pack"]))
        transports = []

        def transport(url, headers, body, timeout):
            base.require(url == base.ENDPOINT and json.loads(body) == expected, "Payload/destination drift")
            base.require(not transports, "Retries prohibited")
            transports.append({})
            base.save(directory / "codex_request.json", expected)
            base.save(directory / "codex_attempt.json", {**slot, "started_at": base.now(), "body_sha256": previous.digest(expected)})
            base.emit({"event": "CALL_STARTED", **slot, "model": MODEL})
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
                record = {"http_status": status, "payload": parsed, "usage": previous.usage_for(parsed, "B"),
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

        started = time.monotonic()
        record = {**slot, "model": MODEL, "started_at": base.now()}
        adapter = base.QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=180,
            base_url=base.ENDPOINT.rsplit("/chat/completions", 1)[0], transport=transport)
        try:
            result = base.x02.QwenStageGateway(adapter).call(request["stage"], request["prompt"], request["schema"], context=request["context"])
            base.save(directory / "codex_raw_output.json", result.output)
            unknown = []
            decoded = transform(result.output, mapping["reverse"], unknown=unknown)
            base.save(directory / "codex_reference_decode.json", {"mapping_sha256": base.sha(AREA / ("pack_%d_reference_map.json" % slot["pack"])),
                "unknown_short_references": unknown, "strategy": "EXACT_TYPED_FIELD_LOOKUP_ONLY_NO_FUZZY_REPAIR",
                "semantic_text_changed": False})
            record.update(status="RETURNED_FOR_REVIEW", output=decoded, request_id=result.request_id,
                          unmapped_reference_count=len(unknown))
        except Exception as exc:
            record.update(status="FAILED", error_type=type(exc).__name__, code=getattr(exc, "code", None))
        provider = transports[-1] if transports else {}
        record.update({k: provider.get(k) for k in ("usage", "http_status", "provider_model", "finish_reasons")})
        record.update(duration_seconds=time.monotonic() - started, completed_at=base.now(),
                      transport_attempts=len(transports), quality_status="NOT_AUTOMATICALLY_SCORED")
        base.save(directory / "codex_result.json", record)
        results.append({k: v for k, v in record.items() if k != "output"})
        base.emit({"event": "CALL_FINISHED", **results[-1]})
        if record["http_status"] != 200 or record["provider_model"] != MODEL:
            break
    known = [r["usage"] for r in results if r["usage"] is not None]
    summary = {"completed_at": base.now(), "results": results, "planned_slots": 4, "attempted_slots": len(results),
        "not_run_slots": prep["slots"][len(results):], "http_attempts": sum(r["transport_attempts"] for r in results),
        "known_input_tokens": sum(u["input_tokens"] for u in known), "known_output_tokens": sum(u["output_tokens"] for u in known),
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
    {"prepare": prepare, "run": run_all, "summarize": summarize}[parser.parse_args().command]()
