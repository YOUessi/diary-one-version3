"""Local-only preparation or eight fixed S07 calls; no runtime policy changes.

A reuses the historical request. B removes only the organizational hint layer.
Every slot has at most one HTTP attempt. No semantic repair, images or exemplars.
"""
import argparse
import copy
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key

AREA = ROOT / "var/codex_structure_hint_ablation_20260907"
OLD = ROOT / "var/codex_v1_68_2_experience_first_chapter_execution"
CANDIDATE = ROOT / "var/codex_v1_68_experience_first_chapter/codex_candidate.json"
CANDIDATE_SHA = "bf333f5c8bb8958b4b6fadca060b787584f53c78a4e029b8a8d33faa668f0c7a"
MODEL = "qwen3-vl-flash-2026-01-22"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
FIELDS = ("setting_code", "activity_code", "episode_code", "subject_codes", "motifs")
PINS = {
    1: (8, "731aeff78bff7a39803cffede2f9a24c7d358d3aa8d341b18c83a3c2ff8b65f4", "9585ce1dfda480c1a3e341e53f012925259eb54d12c616b73759a051256fe964"),
    2: (10, "cdf2bb502c8b4b4836f06ca1a5a6fea4c4a83745b7537c053d30e54d4ac55cae", "eeff8527f1418d1759dbeffc71cb998f17294e72c178df3bf6dac86f0018e6db"),
}
# Balanced AB/BA order across packs and repetitions; not selected after outcomes.
SLOTS = ((1, "A", 1), (1, "B", 1), (2, "B", 1), (2, "A", 1),
         (1, "B", 2), (1, "A", 2), (2, "A", 2), (2, "B", 2))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def verify_source():
    require(sha(CANDIDATE) == CANDIDATE_SHA, "Historical candidate drift")
    candidate = load(CANDIDATE)
    for relative, expected in candidate["source_sha256"].items():
        require(sha(ROOT / relative) == expected, "Runtime source drift: " + relative)
    return candidate


def requests_for(pack):
    index, request_sha, report_sha = PINS[pack]
    directory = OLD / ("pack_%d/round_1" % pack)
    path = directory / ("codex_stage_calls/codex_%03d_request.json" % index)
    require(sha(path) == request_sha, "Archived structure request drift")
    require(sha(directory / "codex_full_run.json") == report_sha, "Archived full result drift")
    original = load(path)
    require(original["stage"] == "S05_S07_STRUCTURE_PROPOSAL" and original["evidence"] == [], "Not a text-only S07 request")
    prefix, text = original["prompt"].rsplit("Input:\n", 1)
    original_input = json.loads(text)
    audit_context = {k: v for k, v in original["context"].items() if k != "_x02_policy_version"}
    require(original_input == audit_context, "Prompt/context mismatch")
    report = load(directory / "codex_full_run.json")
    require(len(original_input["observations"]) == len(report["result"]["observations"]), "Not all observations present")
    changed = copy.deepcopy(original)
    changed_input = copy.deepcopy(original_input)
    changed_input.pop("moments")
    for before, after in zip(original_input["observations"], changed_input["observations"]):
        for field in FIELDS:
            after.pop(field)
        require(after == {k: v for k, v in before.items() if k not in FIELDS}, "Unexpected observation change")
    changed["prompt"] = prefix + "Input:\n" + json.dumps(changed_input, ensure_ascii=False)
    changed["context"] = {**changed_input, "_x02_policy_version": original["context"]["_x02_policy_version"]}
    require(changed["schema"] == original["schema"], "Response schema changed")
    for field in set(original_input) - {"moments", "observations"}:
        require(changed_input[field] == original_input[field], "Non-hint context changed")
    return original, changed


class Captured(Exception):
    pass


def build_body(request):
    bodies = []

    def capture(url, headers, body, timeout):
        require(url == ENDPOINT, "Unexpected destination")
        bodies.append(body)
        raise Captured()

    gateway = x02.QwenStageGateway(QwenChatCompletionsAdapter(
        api_key="offline-placeholder", model=MODEL,
        base_url=ENDPOINT.rsplit("/chat/completions", 1)[0], transport=capture))
    try:
        gateway.call(request["stage"], request["prompt"], request["schema"], context=request["context"])
    except Captured:
        pass
    require(len(bodies) == 1, "Offline capture did not occur exactly once")
    payload = json.loads(bodies[0])
    require(all(c["type"] == "text" for m in payload["messages"] for c in m["content"]), "Unexpected image payload")
    return payload


def prepare():
    candidate = verify_source()
    require(not AREA.exists(), "Refusing to overwrite prepared experiment")
    files, summaries = {}, []
    for pack in (1, 2):
        a, b = requests_for(pack)
        for condition, request in (("A", a), ("B", b)):
            prefix = "pack_%d_%s" % (pack, condition)
            body = build_body(request)
            body_sha = hashlib.sha256(canonical_bytes(body)).hexdigest()
            if condition == "A":
                provider = load(OLD / ("pack_%d/round_1/codex_stage_calls/codex_%03d_provider.json" % (pack, PINS[pack][0])))
                require(provider["request_body_sha256"] == body_sha, "Control does not reproduce historical HTTP body")
            files[prefix + "_request.json"] = request
            files[prefix + "_body.json"] = body
            summaries.append({"pack": pack, "condition": condition, "body_sha256": body_sha,
                              "observations": len(request["context"]["observations"]),
                              "facts": sum(len(o["facts"]) for o in request["context"]["observations"]),
                              "prompt_characters": len(request["prompt"]), "body_bytes": len(canonical_bytes(body))})
    AREA.mkdir()
    for name, value in files.items():
        save(AREA / name, value)
    save(AREA / "codex_preparation.json", {
        "experiment": "CODEX_S07_HINT_LAYER_ABLATION_20260907", "created_at": now(),
        "candidate_sha256": CANDIDATE_SHA, "source_sha256": candidate["source_sha256"],
        "harness_sha256": sha(__file__), "model": MODEL, "endpoint": ENDPOINT,
        "files_sha256": {name: sha(AREA / name) for name in files}, "inputs": summaries,
        "slots": [{"slot": i + 1, "pack": p, "condition": c, "repeat": r} for i, (p, c, r) in enumerate(SLOTS)],
        "removed_observation_fields": FIELDS, "removed_context_fields": ["moments"],
        "unchanged": ["all_facts", "fact_ids", "observation_ids", "roles", "event_fields", "aha_relation_scope", "order", "sequence_semantics", "model", "task_instructions", "response_schema", "sampling_defaults"],
        "external_payload": "ARCHIVED_DERIVED_TEXT_ONLY_NO_IMAGES_OR_ORIGINALS_OR_REVIEW_ANSWERS",
        "validation_scope": "S07_DIAGNOSTIC_REPLAY_NOT_FRESH_FULL_RUN_OR_PRODUCTION",
        "quality_status": "NOT_YET_RUN", "max_http_attempts": 8, "retries_per_slot": 0,
    })
    emit({"event": "PREPARED_NO_API_CALL", "inputs": summaries, "historical_A_body_matches": True})


def provider_usage(raw):
    usage = raw.get("usage") if isinstance(raw, dict) else None
    if not isinstance(usage, dict):
        return None
    incoming, outgoing = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in (incoming, outgoing)):
        return None
    rate = 0.15 if incoming <= 32768 else 0.30 if incoming <= 131072 else 0.60
    return {"input_tokens": incoming, "output_tokens": outgoing,
            "historical_estimated_cny": (incoming * rate + outgoing * rate * 10) / 1_000_000,
            "basis": "HISTORICAL_V1_64_RATE_SNAPSHOT_NOT_CURRENT_PRICE_OR_BILL"}


def run_all():
    verify_source()
    prep = load(AREA / "codex_preparation.json")
    require(prep["harness_sha256"] == sha(__file__), "Prepared harness drift")
    for name, expected in prep["files_sha256"].items():
        require(sha(AREA / name) == expected, "Prepared input drift")
    require(not (AREA / "codex_execution_started.json").exists(), "Execution already attempted; no automatic rerun")
    key, source = _resolve_qwen_api_key()
    require(bool(key), "Existing research credential unavailable; no request sent")
    save(AREA / "codex_execution_started.json", {"started_at": now(), "credential_source": source,
          "preparation_sha256": sha(AREA / "codex_preparation.json"), "slots": prep["slots"]})
    results = []
    for slot in prep["slots"]:
        directory = AREA / ("slot_%02d" % slot["slot"])
        directory.mkdir()
        request = load(AREA / ("pack_%d_%s_request.json" % (slot["pack"], slot["condition"])))
        expected = load(AREA / ("pack_%d_%s_body.json" % (slot["pack"], slot["condition"])))
        transports = []

        def transport(url, headers, body, timeout):
            require(url == ENDPOINT and json.loads(body) == expected, "Payload/destination drift")
            require(not transports, "No automatic retry is allowed")
            transports.append({"started_at": now()})
            save(directory / "codex_request.json", expected)
            save(directory / "codex_attempt.json", {**slot, "started_at": now(), "body_sha256": hashlib.sha256(body).hexdigest()})
            emit({"event": "CALL_STARTED", **slot})
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
                record = {"http_status": status, "payload": parsed, "usage": provider_usage(parsed),
                          "duration_seconds": time.monotonic() - started, "completed_at": now()}
                save(directory / "codex_provider.json", record)
                transports[-1].update(record)
                return status, response_headers, raw
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                record = {"http_status": None, "usage": None, "status": "NO_HTTP_RESPONSE",
                          "error_type": type(exc).__name__, "duration_seconds": time.monotonic() - started}
                save(directory / "codex_transport_failure.json", record)
                transports[-1].update(record)
                raise

        adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL, timeout_seconds=180,
                 base_url=ENDPOINT.rsplit("/chat/completions", 1)[0], transport=transport)
        record = {**slot, "started_at": now()}
        started = time.monotonic()
        try:
            result = x02.QwenStageGateway(adapter).call(request["stage"], request["prompt"], request["schema"], context=request["context"])
            record.update(status="RETURNED_FOR_REVIEW", output=result.output, request_id=result.request_id)
        except Exception as exc:
            record.update(status="FAILED", error_type=type(exc).__name__, code=getattr(exc, "code", None))
        record.update(duration_seconds=time.monotonic() - started, completed_at=now(),
                      transport_attempts=len(transports), usage=transports[-1].get("usage") if transports else None,
                      http_status=transports[-1].get("http_status") if transports else None,
                      quality_status="NOT_AUTOMATICALLY_SCORED")
        save(directory / "codex_result.json", record)
        results.append({k: v for k, v in record.items() if k != "output"})
        emit({"event": "CALL_FINISHED", **results[-1]})
        if not transports or record["http_status"] in (None, 401, 403):
            break  # Infrastructure/credential problem, not a semantic retry opportunity.
    known = [r["usage"] for r in results if r["usage"] is not None]
    summary = {"completed_at": now(), "results": results, "planned_slots": 8,
               "attempted_slots": len(results), "not_run_slots": prep["slots"][len(results):],
               "http_attempts": sum(r["transport_attempts"] for r in results),
               "known_input_tokens": sum(u["input_tokens"] for u in known),
               "known_output_tokens": sum(u["output_tokens"] for u in known),
               "historical_estimated_cny_known": sum(u["historical_estimated_cny"] for u in known),
               "usage_unknown_slots": len(results) - len(known), "full_pipeline_executed": False,
               "quality_status": "AWAITING_REAL_CONTENT_REVIEW"}
    save(AREA / "codex_execution_summary.json", summary)
    emit({"event": "EXPERIMENT_FINISHED", **summary})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    args = parser.parse_args()
    prepare() if args.command == "prepare" else run_all()
