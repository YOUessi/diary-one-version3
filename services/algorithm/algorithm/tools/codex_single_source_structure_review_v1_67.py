"""Isolated V1.67 three-pack, one-full-run experiment; no API unless --live."""
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
AREA = ROOT / "var/codex_v1_67_single_source_structure"
PRIOR = ROOT / "var/codex_v1_66_editorial_allocation"
PRIOR_CANDIDATE_SHA = "e833ee755e00d606c625624cb04bdb8d3efc27947e91229dfc7f2c64ee70d096"
NORMALIZER_PRIOR = ROOT / "var/codex_v1_64_repeat_review"
NORMALIZER_PREPARATION_SHA = "ef514491a983d29374b922246306f9e71df2d004cb774876c4653b92edbc5a32"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen3-vl-flash-2026-01-22"
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


def encode(value):
    def explicit_default(item):
        if isinstance(item, Path):
            return str(item)
        raise TypeError("Unsupported audit value type: " + type(item).__name__)
    return json.dumps(value, ensure_ascii=False, indent=2, default=explicit_default) + "\n"


def save(path, value):
    serialized = encode(value)  # Complete serialization before exclusive creation; never leave a type-error fragment.
    with path.open("x", encoding="utf-8") as stream:
        stream.write(serialized)


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


def snapshot(source_root, destination, expected):
    require(not destination.exists(), "Refusing to replace a snapshot")
    require(source_inventory(source_root) == expected, "Source changed before snapshot")
    destination.mkdir(parents=True)
    for relative, digest in expected.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / relative, target)
        require(sha(target) == digest, "Source changed while copying: " + relative)
    require(source_inventory(destination) == expected, "Snapshot inventory mismatch")
    require(source_inventory(source_root) == expected, "Source changed during snapshot")


def prior_inputs():
    candidate_path = PRIOR / "codex_candidate.json"
    require(sha(candidate_path) == PRIOR_CANDIDATE_SHA, "Frozen V1.66 candidate receipt drift")
    candidate = load(candidate_path)
    require(len(candidate["source_sha256"]) == 41, "Expected frozen 41-file V1.66 baseline")
    require(source_inventory(PRIOR / "codex_candidate_runtime") == candidate["source_sha256"], "Frozen V1.66 source drift")
    require(sha(PRIOR / "codex_preparation.json") == candidate["preparation_sha256"], "Prior inventory receipt drift")
    previous = load(PRIOR / "codex_preparation.json")
    require(sha(NORMALIZER_PRIOR / "codex_preparation.json") == NORMALIZER_PREPARATION_SHA, "V1.64 normalizer receipt drift")
    require(previous["normalizer_snapshot"] == str(NORMALIZER_PRIOR / "codex_web_normalizer"), "Unexpected normalizer source")
    expected_normalizer = load(NORMALIZER_PRIOR / "codex_preparation.json")["normalizer_sha256"]
    require(previous["normalizer_sha256"] == expected_normalizer, "Normalizer manifest drift")
    for name, digest in expected_normalizer.items():
        require(Path(name).name == name and sha(NORMALIZER_PRIOR / "codex_web_normalizer" / name) == digest,
                "Archived normalizer drift")
    return candidate, previous


def prepare_baseline():
    require(not AREA.exists(), "Refusing to overwrite an experiment")
    prior_candidate, previous = prior_inputs()
    packs = []
    for original in previous["packs"]:
        pack = dict(original)
        source_root = Path(pack["source_root"]).resolve(strict=True)
        for asset in pack["assets"]:
            relative = Path(asset["relative_path"])
            require(not relative.is_absolute() and ".." not in relative.parts, "Invalid asset path")
            source = (source_root / relative).resolve(strict=True)
            require(source.is_relative_to(source_root), "Source escaped its authorized pack")
            require(sha(source) == asset["sha256"] and source.stat().st_size == asset["bytes"], "Original media drift")
        pack.update(session_id=str(uuid.uuid5(uuid.NAMESPACE_URL, "codex-v167-pack-" + str(pack["pack_id"]))), exported_at=now())
        packs.append(pack)
    require({str(p["pack_id"]) for p in packs} == {"1", "2", "3"}, "Expected exactly three authorized packs")
    AREA.mkdir()
    expected = prior_candidate["source_sha256"]
    snapshot(PRIOR / "codex_candidate_runtime", AREA / "codex_baseline_runtime", expected)
    save(AREA / "codex_preparation.json", {
        "experiment": "CODEX_V1_67_SINGLE_SOURCE_STRUCTURE", "algorithm_baseline": "V1.66",
        "created_at": now(), "planned_rounds": 1, "packs": packs, "source_sha256": expected,
        "baseline_snapshot": "codex_baseline_runtime", "baseline_origin": "FROZEN_V1_66_NOT_ACTIVE_WORKTREE",
        "prior_candidate_sha256": PRIOR_CANDIDATE_SHA,
        "prior_preparation_path": str(PRIOR / "codex_preparation.json"),
        "prior_preparation_sha256": prior_candidate["preparation_sha256"],
        "normalizer_preparation_sha256": NORMALIZER_PREPARATION_SHA,
        "normalizer_snapshot": previous["normalizer_snapshot"], "normalizer_sha256": previous["normalizer_sha256"],
        "model": MODEL, "endpoint": ENDPOINT, "capture_time_used": False, "gps_used": False,
        "source_order": "PRIOR_AUTHORIZED_INVENTORY_RELATIVE_PATH_ORDER_NOT_CAPTURE_TIME",
        "external_payload": "NORMALIZED_JPEG_FRAMES_AND_DERIVED_TEXT_ONLY_NO_ORIGINALS",
        "execution": "THREE_PACKS_ONE_FRESH_FULL_RUN_EACH_SERIAL_NO_CROSS_RUN_SEMANTIC_CACHE",
        "scope": "ONLY_NEW_EXPERIMENT_TOOLS_AND_AREA_NO_WEB_APP_SDK_SHARED_OR_OLD_RECORD_WRITES",
        "quality_status": "EXPLORATORY_DEVELOPER_REVIEW_NOT_USER_ACCEPTANCE",
    })
    emit({"event": "BASELINE_PREPARED_NO_MODEL_CALL", "area": str(AREA), "source_files": len(expected),
          "packs": [{"id": p["pack_id"], "assets": len(p["assets"])} for p in packs]})


def preparation():
    prior_candidate, previous = prior_inputs()
    prep = load(AREA / "codex_preparation.json")
    require(prep["prior_candidate_sha256"] == PRIOR_CANDIDATE_SHA, "Baseline identity changed")
    require(prep["source_sha256"] == prior_candidate["source_sha256"], "Baseline manifest drift")
    require(source_inventory(AREA / "codex_baseline_runtime") == prep["source_sha256"], "Baseline snapshot drift")
    require(prep["normalizer_sha256"] == previous["normalizer_sha256"], "Normalizer manifest drift")
    require(prep["normalizer_snapshot"] == previous["normalizer_snapshot"], "Normalizer path drift")
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
    require(expected != prep["source_sha256"], "Candidate is unchanged V1.66; wait for V1.67 implementation")
    source = AREA / "codex_candidate_runtime"
    snapshot(ROOT, source, expected)
    x02 = import_candidate(source)
    require("structure_wire" in x02.x02_runtime_policies(), "V1.67 structure_wire policy missing")
    names = sorted(set(expected) | set(prep["source_sha256"]))
    candidate = {
        "experiment": prep["experiment"], "algorithm_candidate": "V1.67", "created_at": now(),
        "preparation_sha256": sha(AREA / "codex_preparation.json"), "source_sha256": expected,
        "runtime_policies": x02.x02_runtime_policies(),
        "baseline_differences": [{"path": name, "baseline_sha256": prep["source_sha256"].get(name),
                                  "candidate_sha256": expected.get(name)} for name in names
                                 if prep["source_sha256"].get(name) != expected.get(name)],
        "harness_sha256": sha(Path(__file__)),
        "normalization_harness_sha256": sha(ROOT / "tools/codex_prepare_single_source_evidence_v1_67.mjs"),
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
    require(candidate["normalization_harness_sha256"] == sha(ROOT / "tools/codex_prepare_single_source_evidence_v1_67.mjs"),
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
            raise RuntimeError("Another V1.67 live run is active; run packs strictly serially") from None
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

    report = {"experiment": prep["experiment"], "algorithm_baseline": "V1.66", "algorithm_candidate": "V1.67",
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


def preflight():
    candidate, previous = prior_inputs()
    # Use an already archived real tuple only to check audit serialization.
    # It is never installed as this experiment's inputs or semantic output.
    x02 = import_candidate(PRIOR / "codex_candidate_runtime")
    from diary_one_ci.bundle import load_app_library_bundle
    bundle = load_app_library_bundle(PRIOR / "pack_1/round_1/codex_manifest.json")
    evidence = x02._perception_evidence(bundle, bundle.manifest["assets"][:3])
    encoded = encode({"_perception_evidence": evidence})
    require(json.loads(encoded)["_perception_evidence"][0][2] == str(evidence[0][2]), "Path audit serialization failed")
    try:
        save(None, {"unsupported": object()})
    except TypeError as exc:
        require(str(exc).startswith("Unsupported audit value type:"), "Unexpected serialization failure")
    else:
        raise RuntimeError("Unknown type should fail before attempting file creation")
    emit({"event": "PREFLIGHT_PASS_NO_WRITES_NO_MODEL_CALL", "frozen_baseline_files": len(candidate["source_sha256"]),
          "normalizer_modules": len(previous["normalizer_sha256"]), "actual_Path_serialization": "PASS",
          "unknown_type_fails_before_open": "PASS", "baseline_from_active_tree": False})



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "prepare-baseline", "freeze-candidate", "run"))
    parser.add_argument("--pack", choices=("1", "2", "3"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "preflight":
        require(not args.live and args.pack is None, "Preflight is local only")
        preflight()
    elif args.command == "prepare-baseline":
        require(not args.live and args.pack is None, "Preparation is local only")
        prepare_baseline()
    elif args.command == "freeze-candidate":
        require(not args.live and args.pack is None, "Freeze is local only")
        freeze_candidate()
    else:
        require(args.pack is not None, "Run requires --pack")
        sys.exit(run(args.pack, args.live))
