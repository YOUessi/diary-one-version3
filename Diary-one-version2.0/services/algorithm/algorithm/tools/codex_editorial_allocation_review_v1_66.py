"""Isolated V1.66 three-pack, one-full-run experiment; no API unless --live."""
import argparse
import fcntl
import hashlib
import json
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_66_editorial_allocation"
PRIOR = ROOT / "var/codex_v1_64_repeat_review"
PRIOR_PREPARATION_SHA = "ef514491a983d29374b922246306f9e71df2d004cb774876c4653b92edbc5a32"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen3-vl-flash-2026-01-22"
BASELINE_PINS = {
    "src/diary_one_ci/x02.py": "ab61205ef49806e6a0504e282d44e696395253e64d789f759e4f722edd476a5e",
    "src/diary_one_ci/codex_content_brief.py": "de3beb060f361eaf377a19f36b6bf71ca1223b5db2b8af6f86f0b9e3e66de433",
    "src/diary_one_ci/codex_chapter_media.py": "7c7fd4bdc45ffe7344c94fefa47653c71ff089b46d4b8043ddddbe54a461167e",
}
sys.dont_write_bytecode = True


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def source_inventory(root):
    inventory = {}
    for branch, suffixes in (("src", {".py", ".json"}), ("contracts", {".json"})):
        for path in sorted((root / branch).rglob("*")):
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            require(not path.is_symlink(), "Source symlink not permitted")
            if not path.is_file():
                continue
            require(path.suffix in suffixes, "Unexpected source file: " + str(path.relative_to(root)))
            inventory[path.relative_to(root).as_posix()] = sha(path)
    return inventory


def snapshot(destination, expected):
    require(not destination.exists(), "Refusing to replace a snapshot")
    require(source_inventory(ROOT) == expected, "Live source changed before snapshot")
    destination.mkdir(parents=True)
    for relative, digest in expected.items():
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        require(sha(target) == digest, "Source changed while copying: " + relative)
    require(source_inventory(destination) == expected, "Snapshot inventory mismatch")
    require(source_inventory(ROOT) == expected, "Live source changed during snapshot")


def prepare_baseline():
    require(not AREA.exists(), "Refusing to overwrite an experiment")
    previous_path = PRIOR / "codex_preparation.json"
    require(sha(previous_path) == PRIOR_PREPARATION_SHA, "Prior preparation drift")
    previous = load(previous_path)
    expected = {**previous["source_sha256"], **BASELINE_PINS}
    require(len(expected) == 40 and source_inventory(ROOT) == expected, "V1.65 baseline drift")
    for name, digest in previous["normalizer_sha256"].items():
        require(Path(name).name == name, "Invalid archived normalizer name")
        require(sha(PRIOR / "codex_web_normalizer" / name) == digest, "Archived normalizer drift")
    packs = []
    for original in previous["packs"]:
        pack = dict(original)
        source_root = Path(pack["source_root"]).resolve(strict=True)
        for asset in pack["assets"]:
            relative = Path(asset["relative_path"])
            require(not relative.is_absolute() and ".." not in relative.parts, "Invalid asset path")
            path = (source_root / relative).resolve(strict=True)
            require(path.is_relative_to(source_root), "Source escaped its authorized pack")
            require(sha(path) == asset["sha256"] and path.stat().st_size == asset["bytes"], "Original media drift")
        pack.update(session_id=str(uuid.uuid5(uuid.NAMESPACE_URL, "codex-v166-pack-" + str(pack["pack_id"]))), exported_at=now())
        packs.append(pack)
    require({str(p["pack_id"]) for p in packs} == {"1", "2", "3"}, "Expected exactly three authorized packs")
    AREA.mkdir()
    snapshot(AREA / "codex_baseline_runtime", expected)
    preparation = {
        "experiment": "CODEX_V1_66_EDITORIAL_ALLOCATION", "algorithm_baseline": "V1.65",
        "created_at": now(), "planned_rounds": 1, "packs": packs,
        "prior_preparation_path": str(previous_path), "prior_preparation_sha256": PRIOR_PREPARATION_SHA,
        "source_sha256": expected, "baseline_snapshot": "codex_baseline_runtime",
        "normalizer_snapshot": str(PRIOR / "codex_web_normalizer"),
        "normalizer_sha256": previous["normalizer_sha256"], "model": MODEL, "endpoint": ENDPOINT,
        "capture_time_used": False, "gps_used": False,
        "source_order": "PRIOR_AUTHORIZED_INVENTORY_RELATIVE_PATH_ORDER_NOT_CAPTURE_TIME",
        "external_payload": "NORMALIZED_JPEG_FRAMES_AND_DERIVED_TEXT_ONLY_NO_ORIGINALS",
        "execution": "THREE_PACKS_ONE_FRESH_FULL_RUN_EACH_SERIAL_NO_CROSS_RUN_SEMANTIC_CACHE",
        "scope": "ONLY_NEW_EXPERIMENT_TOOLS_AND_AREA_NO_WEB_APP_SDK_SHARED_OR_OLD_RECORD_WRITES",
        "quality_status": "EXPLORATORY_DEVELOPER_REVIEW_NOT_USER_ACCEPTANCE",
    }
    save(AREA / "codex_preparation.json", preparation)
    emit({"event": "BASELINE_PREPARED_NO_MODEL_CALL", "area": str(AREA), "source_files": len(expected),
          "packs": [{"id": p["pack_id"], "assets": len(p["assets"])} for p in packs]})


def preparation():
    prep = load(AREA / "codex_preparation.json")
    require(sha(PRIOR / "codex_preparation.json") == prep["prior_preparation_sha256"] == PRIOR_PREPARATION_SHA,
            "Prior preparation drift")
    require(source_inventory(AREA / "codex_baseline_runtime") == prep["source_sha256"], "Baseline snapshot drift")
    require(prep["normalizer_snapshot"] == str(PRIOR / "codex_web_normalizer"), "Unexpected normalizer source")
    for name, digest in prep["normalizer_sha256"].items():
        require(Path(name).name == name and sha(PRIOR / "codex_web_normalizer" / name) == digest,
                "Archived normalizer drift")
    require(prep["model"] == MODEL and prep["endpoint"] == ENDPOINT, "Experiment destination drift")
    return prep


def import_candidate(source):
    sys.path.insert(0, str(source / "src"))
    from diary_one_ci import x02
    for name, module in list(sys.modules.items()):
        if name == "diary_one_ci" or name.startswith("diary_one_ci."):
            require(Path(module.__file__).resolve().is_relative_to(source.resolve()), "Runtime import escaped snapshot")
    return x02


def freeze_candidate():
    prep = preparation()
    require(not (AREA / "codex_candidate.json").exists(), "Candidate already frozen")
    expected = source_inventory(ROOT)
    require(expected != prep["source_sha256"], "Candidate is unchanged V1.65; wait for V1.66 implementation")
    source = AREA / "codex_candidate_runtime"
    snapshot(source, expected)
    x02 = import_candidate(source)
    names = sorted(set(expected) | set(prep["source_sha256"]))
    candidate = {
        "experiment": prep["experiment"], "algorithm_candidate": "V1.66", "created_at": now(),
        "preparation_sha256": sha(AREA / "codex_preparation.json"), "source_sha256": expected,
        "runtime_policies": x02.x02_runtime_policies(),
        "baseline_differences": [{"path": name, "baseline_sha256": prep["source_sha256"].get(name),
                                  "candidate_sha256": expected.get(name)} for name in names
                                 if prep["source_sha256"].get(name) != expected.get(name)],
        "harness_sha256": sha(Path(__file__)),
        "normalization_harness_sha256": sha(ROOT / "tools/codex_prepare_editorial_evidence_v1_66.mjs"),
        "model": MODEL, "endpoint": ENDPOINT, "quality_status": "NOT_REAL_MODEL_VALIDATED",
    }
    save(AREA / "codex_candidate.json", candidate)
    emit({"event": "CANDIDATE_FROZEN_NO_MODEL_CALL", "source_files": len(expected),
          "changed_files": [r["path"] for r in candidate["baseline_differences"]], "policies": candidate["runtime_policies"]})


def provider_usage(raw):
    usage = raw.get("usage") if isinstance(raw, dict) else None
    if not isinstance(usage, dict):
        return None
    incoming = usage.get("prompt_tokens", usage.get("input_tokens"))
    outgoing = usage.get("completion_tokens", usage.get("output_tokens"))
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in (incoming, outgoing)):
        return None
    rate = 0.15 if incoming <= 32768 else 0.30 if incoming <= 131072 else 0.60
    return {"input_tokens": incoming, "output_tokens": outgoing,
            "estimated_tiered_cost_cny": (incoming * rate + outgoing * rate * 10) / 1_000_000,
            "input_cny_per_million": rate, "output_cny_per_million": rate * 10,
            "cost_basis": "HISTORICAL_V1_64_BEIJING_RATE_SNAPSHOT_NOT_BILLING_OR_CURRENT_PRICE",
            "usage_basis": "PROVIDER_TOTALS_DETAILS_NOT_ADDED_AGAIN"}


def run(pack_id, live):
    prep = preparation()
    candidate_path = AREA / "codex_candidate.json"
    candidate = load(candidate_path)
    require(candidate["preparation_sha256"] == sha(AREA / "codex_preparation.json"), "Preparation changed after freeze")
    require(candidate["harness_sha256"] == sha(Path(__file__)), "Run harness changed after freeze")
    require(candidate["normalization_harness_sha256"] == sha(ROOT / "tools/codex_prepare_editorial_evidence_v1_66.mjs"),
            "Normalization harness changed after freeze")
    source = AREA / "codex_candidate_runtime"
    require(source_inventory(source) == candidate["source_sha256"], "Candidate snapshot drift")
    x02 = import_candidate(source)
    from diary_one_ci.bundle import load_app_library_bundle
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    directory = AREA / ("pack_" + pack_id) / "round_1"
    manifest_path = directory / "codex_manifest.json"
    normalized = load(directory / "codex_normalization.json")
    require(normalized["status"] == "READY" and normalized["freshDecodeAndExtraction"] is True,
            "Fresh complete normalization required")
    require(normalized["candidate_sha256"] == sha(candidate_path), "Normalization did not use this candidate")
    require(normalized["preparation_sha256"] == candidate["preparation_sha256"], "Normalization preparation drift")
    require(normalized["harness_sha256"] == candidate["normalization_harness_sha256"], "Normalizer harness identity mismatch")
    require(normalized["manifest_sha256"] == sha(manifest_path), "Normalized manifest drift")
    bundle = load_app_library_bundle(manifest_path)
    pack = next(p for p in prep["packs"] if str(p["pack_id"]) == pack_id)
    require([a["original_sha256"] for a in bundle.manifest["assets"]] == [a["sha256"] for a in pack["assets"]], "Input inventory drift")
    require(bundle.manifest["bundle_version"] == "DIARY_ONE_APP_LIBRARY_BUNDLE_V04", "Expected Bundle V04")
    require(all(f["spatial_transform"] == "ASPECT_FIT_LETTERBOX" for a in bundle.manifest["assets"] for f in a["frames"]),
            "Expected frozen full-frame profile")
    policies = x02.x02_runtime_policies()
    require(policies == candidate["runtime_policies"], "Candidate policies drift")
    summary = {"pack": pack_id, "round": 1, "assets": len(bundle.manifest["assets"]),
               "frames": sum(len(a["frames"]) for a in bundle.manifest["assets"]), "policies": policies}
    if not live:
        emit({"event": "VERIFIED_NO_MODEL_CALL", **summary})
        return 0
    # Held for the entire run, including key resolution. Never parallelize this experiment's API calls.
    with (AREA / "codex_live_serial.lock").open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another V1.66 live run is active; run packs strictly serially") from None
        require(not any((directory / name).exists() for name in
                        ("codex_attempt.json", "codex_stage_calls", "codex_full_run.json")), "Refusing to repeat an attempted slot")
        from diary_one_ci.x01_server import _resolve_qwen_api_key
        key, credential_source = _resolve_qwen_api_key()
        require(bool(key), "Existing server-side Qwen credential unavailable")
        save(directory / "codex_attempt.json", {"started_at": now(), "pack": pack_id, "round": 1,
             "candidate_sha256": sha(candidate_path), "model": MODEL, "endpoint": ENDPOINT})
        return execute_live(x02, QwenChatCompletionsAdapter, key, credential_source, directory, manifest_path,
                            normalized, prep, candidate, policies, summary)


def execute_live(x02, adapter_type, key, credential_source, directory, manifest_path, normalized, prep, candidate, policies, summary):
    calls_dir = directory / "codex_stage_calls"
    calls_dir.mkdir()
    calls, transports = [], []
    active = {"index": 0, "stage": None}

    def safe_error(exc):
        return str(exc).replace(key, "[REDACTED]")

    def trace_transport(url, headers, body, timeout):
        require(url == ENDPOINT, "Unexpected external destination")
        payload = json.loads(body)
        require(payload["model"] == MODEL and payload.get("enable_thinking") is False, "Unexpected model or thinking mode")
        item = {"transport_index": len(transports) + 1, "stage_call_index": active["index"],
                "stage": active["stage"], "started_at": now(), "status": "STARTED", "usage": None,
                "request_body_sha256": hashlib.sha256(body).hexdigest()}
        transports.append(item)
        started = time.monotonic()
        raw = None
        try:
            status, response_headers, response = adapter_type._url_transport(url, headers, body, timeout)
            try:
                raw = json.loads(response)
            except (ValueError, UnicodeDecodeError):
                raw = {"unparsed_utf8": response.decode("utf-8", errors="replace")}
            item.update(status="HTTP_RETURNED", http_status=status, usage=provider_usage(raw))
            return status, response_headers, response
        except Exception as exc:
            item.update(status="NO_HTTP_RESPONSE", error_type=type(exc).__name__, error_message=safe_error(exc))
            raise
        finally:
            item.update(duration_seconds=time.monotonic() - started, completed_at=now())
            # Retain provider payload/usage, never headers or Authorization. Redact accidental credential echoes.
            provider_record = {**item, "payload": raw}
            clean = json.loads(json.dumps(provider_record, ensure_ascii=False).replace(key, "[REDACTED]"))
            save(calls_dir / ("codex_%03d_provider.json" % item["transport_index"]), clean)

    adapter = adapter_type(api_key=key, model=MODEL,
        base_url=ENDPOINT.removesuffix("/chat/completions"), timeout_seconds=180, transport=trace_transport)

    class TracingGateway(x02.QwenStageGateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            index = len(calls) + 1
            active.update(index=index, stage=stage)
            save(calls_dir / ("codex_%03d_request.json" % index), {
                "index": index, "stage": stage, "prompt": prompt, "schema": schema, "context": context,
                "evidence": [{"asset_id": a["asset_id"], "frame_id": f["frame_id"], "sha256": f["sha256"],
                              "local_path": str(path)} for a, f, path in evidence]})
            call_record = {"index": index, "stage": stage, "status": "STARTED", "started_at": now()}
            calls.append(call_record)
            emit({"event": "CALL_STARTED", "pack": summary["pack"], "index": index, "stage": stage})
            started = time.monotonic()
            stage_run, output = None, None
            try:
                stage_run = super().call(stage, prompt, schema, evidence=evidence, context=context)
                output = stage_run.output
                call_record["status"] = "COMPLETED"
                return stage_run
            except Exception as exc:
                stage_run = getattr(exc, "stage_run", None)
                call_record.update(status="FAILED", error_type=type(exc).__name__,
                                   code=getattr(exc, "code", None), error_message=safe_error(exc))
                raise
            finally:
                related = [t for t in transports if t["stage_call_index"] == index]
                known = [t["usage"] for t in related if t["usage"] is not None]
                call_record.update(duration_seconds=time.monotonic() - started, completed_at=now(),
                    metric=x02._metric_from_run(stage_run) if stage_run else None,
                    transport_count=len(related), provider_usage_complete=bool(related) and len(known) == len(related),
                    provider_input_tokens_known=sum(u["input_tokens"] for u in known),
                    provider_output_tokens_known=sum(u["output_tokens"] for u in known),
                    estimated_tiered_cost_cny=sum(u["estimated_tiered_cost_cny"] for u in known) if known else None,
                    unpriced_transport_count=len(related) - len(known),
                    cost_basis="HISTORICAL_V1_64_BEIJING_RATE_SNAPSHOT_NOT_BILLING_OR_CURRENT_PRICE")
                save(calls_dir / ("codex_%03d_response.json" % index), {**call_record, "output": output})
                emit({"event": "CALL_FINISHED", "pack": summary["pack"], "index": index, "stage": stage,
                      "status": call_record["status"], "seconds": round(call_record["duration_seconds"], 2)})

    report = {"experiment": prep["experiment"], "algorithm_baseline": "V1.65", "algorithm_candidate": "V1.66",
        "pack_id": summary["pack"], "round": 1, "started_at": now(), "harness_sha256": sha(Path(__file__)),
        "preparation_sha256": sha(AREA / "codex_preparation.json"), "candidate_sha256": sha(AREA / "codex_candidate.json"),
        "source_sha256": candidate["source_sha256"], "manifest_sha256": sha(manifest_path),
        "credential_source": credential_source, "model": MODEL, "endpoint": ENDPOINT,
        "runtime_policies": policies, "evaluation_run_mode": "FRESH_FULL_RUN",
        "cross_run_semantic_cache_used": False, "quality_status": "NOT_USER_REVIEWED",
        "normalization_seconds": normalized["totalPreparationMs"] / 1000,
        "interface_scope": "FROZEN_V1_64_NORMALIZER_AND_CANDIDATE_FUNCTION_ENTRY_NOT_HTTP_UI_TEST",
        "returned_does_not_mean_success": True}
    started = time.monotonic()
    try:
        result = x02.run_x02_v041(manifest_path, TracingGateway(adapter))
        require(result["decision_trace"]["runtime_policies"] == policies, "Result runtime policies mismatch")
        report.update(status="RETURNED", result=result, delivery_state=result.get("delivery_state"),
                      coverage_status=result.get("coverage_status"))
    except Exception as exc:
        report.update(status="FAILED", error_type=type(exc).__name__, error_code=getattr(exc, "code", None), error_message=safe_error(exc))
    finally:
        known = [t["usage"] for t in transports if t["usage"] is not None]
        seconds = time.monotonic() - started
        report.update(completed_at=now(), duration_seconds=seconds,
            end_to_end_seconds=seconds + report["normalization_seconds"], stage_calls=calls, transport_attempts=transports,
            failed_stages=[{"index": c["index"], "stage": c["stage"], "code": c.get("code")} for c in calls if c["status"] != "COMPLETED"],
            provider_input_tokens_known=sum(u["input_tokens"] for u in known),
            provider_output_tokens_known=sum(u["output_tokens"] for u in known),
            provider_usage_complete=bool(transports) and len(known) == len(transports),
            estimated_tiered_cost_cny=sum(u["estimated_tiered_cost_cny"] for u in known) if known else None,
            unpriced_transport_count=len(transports) - len(known),
            cost_basis="HISTORICAL_V1_64_BEIJING_RATE_SNAPSHOT_NOT_BILLING_OR_CURRENT_PRICE",
            unknown_usage_is_not_zero=True)
        save(directory / "codex_full_run.json", report)
    result = report.get("result", {})
    emit({"event": "RUN_FINISHED", **summary, "status": report["status"], "delivery": result.get("delivery_state"),
          "coverage": result.get("coverage_status"), "chapters": len(result.get("chapters", [])),
          "ahas": len(result.get("ahas", [])), "calls": len(calls), "transport_attempts": len(transports),
          "seconds": report["duration_seconds"], "report": str(directory / "codex_full_run.json")})
    return 0 if report["status"] == "RETURNED" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare-baseline", "freeze-candidate", "run"))
    parser.add_argument("--pack", choices=("1", "2", "3"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare-baseline":
        require(not args.live and args.pack is None, "Preparation is local only")
        prepare_baseline()
    elif args.command == "freeze-candidate":
        require(not args.live and args.pack is None, "Freeze is local only")
        freeze_candidate()
    else:
        require(args.pack is not None, "Run requires --pack")
        sys.exit(run(args.pack, args.live))
