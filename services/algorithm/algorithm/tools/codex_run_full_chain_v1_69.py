"""One fresh pack per command, frozen V1.69; no API without explicit --live.

No algorithm edits, response reuse, fallback models or harness retries. Existing
algorithm call policy remains unchanged. Private raw/provider audits stay local.
"""
import argparse
import copy
import fcntl
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "var/codex_v1_69_s07_plus_short_refs"
AREA = ROOT / "var/codex_v1_69_full_chain_execution"
CANDIDATE_SHA = "a92f528b8ccc50e3d39db380d2e93bc5d187aebb3f9e78e069c331b782d261e8"
NORMALIZER = ROOT / "tools/codex_prepare_experience_first_evidence_v1_68.mjs"
NORMALIZER_SHA = "e7795b18537ea94e6e7364fd2fbf9c505fecc7daa5885fea7963e458a55cbe88"
LOADER = ROOT / "tools/codex_v169_normalizer_loader.mjs"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, value):
    encoded = json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n"
    with Path(path).open("x", encoding="utf-8") as stream:
        stream.write(encoded)


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def verify():
    require(sha(FROZEN / "codex_candidate.json") == CANDIDATE_SHA, "Candidate receipt drift")
    candidate = load(FROZEN / "codex_candidate.json")
    for name, digest in candidate["source_sha256"].items():
        require(sha(FROZEN / "codex_candidate_runtime" / name) == digest, "Frozen source drift: " + name)
        require(sha(ROOT / name) == digest, "Active research source drift: " + name)
    require(sha(NORMALIZER) == NORMALIZER_SHA, "Frozen extraction harness drift")
    require(sha(candidate["authorized_pack_inventory_origin"]) == candidate["authorized_pack_inventory_sha256"], "Original inventory drift")
    for name, digest in candidate["normalizer_sha256"].items():
        require(sha(Path(candidate["normalizer_snapshot"]) / name) == digest, "Frozen extraction module drift")
    return candidate


def prepare():
    candidate = verify()
    require(not AREA.exists(), "Never overwrite a run area")
    previous = load(candidate["authorized_pack_inventory_origin"])
    packs = copy.deepcopy(previous["packs"])
    for pack in packs:
        pack["session_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "codex-v169-full-pack-" + str(pack["pack_id"])))
        pack["exported_at"] = now()
    AREA.mkdir()
    shutil.copyfile(FROZEN / "codex_candidate.json", AREA / "codex_candidate.json")
    save(AREA / "codex_preparation.json", {
        "experiment": "CODEX_V1_69_FULL_CHAIN", "algorithm_baseline": "V1.68", "algorithm_candidate": "V1.69",
        "candidate_sha256": CANDIDATE_SHA, "created_at": now(), "packs": packs,
        "normalizer_snapshot": candidate["normalizer_snapshot"], "normalizer_sha256": candidate["normalizer_sha256"],
        "normalizer_preparation_sha256": previous["normalizer_preparation_sha256"],
        "normalization_harness_sha256": NORMALIZER_SHA, "loader_sha256": sha(LOADER),
        "runner_sha256": sha(__file__), "research_profile": candidate["research_profile"],
        "rounds_per_pack": 1, "pack_order": [1, 2, 3], "feedback_after_each_pack": True,
        "fresh_decode_and_extraction": True, "cross_run_semantic_cache": False,
        "harness_retries": 0, "external_payload": "AUTHORIZED_NORMALIZED_FRAMES_AND_DERIVED_TEXT_NO_ORIGINALS",
        "pipeline_scope": "NORMALIZATION_THEN_EXISTING_S04_S12_NOT_S13_EXPORT",
        "quality_errors": "RECORD_WITHOUT_TUNING_OR_CHERRY_PICKING", "deployment": "NO_WEB_APP_SWITCH",
    })
    emit({"event": "PREPARED_NO_API", "area": str(AREA), "pack_asset_counts": {p["pack_id"]: len(p["assets"]) for p in packs}})


def preparation():
    candidate = verify()
    prep = load(AREA / "codex_preparation.json")
    require(prep["candidate_sha256"] == CANDIDATE_SHA and sha(AREA / "codex_candidate.json") == CANDIDATE_SHA, "Run candidate drift")
    require(prep["runner_sha256"] == sha(__file__) and prep["loader_sha256"] == sha(LOADER), "Execution harness drift")
    require(prep["research_profile"] == candidate["research_profile"], "Model profile drift")
    return prep, candidate


def normalize(pack_id):
    preparation()
    require(not (AREA / ("pack_" + pack_id)).exists(), "Normalization already attempted")
    command = ["node", "--no-warnings", "--experimental-loader", str(LOADER), str(NORMALIZER), pack_id]
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def runtime():
    snapshot = FROZEN / "codex_candidate_runtime"
    sys.path.insert(0, str(snapshot / "src"))
    from diary_one_ci import codex_s07_research as research
    from diary_one_ci import x02
    for name, module in list(sys.modules.items()):
        if name == "diary_one_ci" or name.startswith("diary_one_ci."):
            require(Path(module.__file__).resolve().is_relative_to(snapshot), "Import escaped frozen candidate")
    return research, x02


def validate_input(pack_id):
    prep, candidate = preparation()
    directory = AREA / ("pack_" + pack_id) / "round_1"
    normal = load(directory / "codex_normalization.json")
    manifest_path = directory / "codex_manifest.json"
    require(normal["status"] == "READY" and normal["freshDecodeAndExtraction"] is True, "Fresh normalization missing")
    require(normal["candidate_sha256"] == CANDIDATE_SHA and normal["preparation_sha256"] == sha(AREA / "codex_preparation.json"), "Normalization provenance drift")
    require(normal["harness_sha256"] == NORMALIZER_SHA and normal["manifest_sha256"] == sha(manifest_path), "Evidence manifest drift")
    for frame in normal["frames"]:
        require(sha(directory / frame["relative_path"]) == frame["sha256"], "Evidence frame drift")
    research, x02 = runtime()
    from diary_one_ci.bundle import load_app_library_bundle
    bundle = load_app_library_bundle(manifest_path)
    pack = next(p for p in prep["packs"] if str(p["pack_id"]) == pack_id)
    require([a["original_sha256"] for a in bundle.manifest["assets"]] == [a["sha256"] for a in pack["assets"]], "Input cardinality or identity drift")
    require(bundle.manifest["session"]["session_id"] == pack["session_id"], "Run session drift")
    require(x02.x02_runtime_policies() == candidate["runtime_policies"] and research.profile() == candidate["research_profile"], "Runtime profile drift")
    return prep, candidate, directory, normal, bundle, research, x02


def run(pack_id, live):
    prep, candidate, directory, normal, bundle, research, x02 = validate_input(pack_id)
    if not live:
        emit({"event": "VERIFIED_NO_API", "pack": pack_id, "assets": len(bundle.manifest["assets"]), "frames": len(normal["frames"])})
        return 0
    with (AREA / "codex_serial.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not (directory / "codex_attempt.json").exists(), "This pack was already attempted; no silent rerun")
        for previous in range(1, int(pack_id)):
            require((AREA / ("pack_%d/round_1/codex_full_run.json" % previous)).exists(), "Earlier pack missing")
        from diary_one_ci.x01_server import _resolve_qwen_api_key
        key, credential_source = _resolve_qwen_api_key()
        require(bool(key), "Existing credential unavailable; no request sent")
        save(directory / "codex_attempt.json", {"started_at": now(), "candidate_sha256": CANDIDATE_SHA,
             "preparation_sha256": sha(AREA / "codex_preparation.json"), "credential_source": credential_source})
        return execute(pack_id, directory, normal, candidate, research, x02, key, credential_source)


def execute(pack_id, directory, normal, candidate, research, x02, key, credential_source):
    calls_dir = directory / "codex_stage_calls"
    calls_dir.mkdir()
    calls, transports = [], []
    active = {"index": 0, "stage": None, "halted": False}

    def clean(value):
        return json.loads(json.dumps(value, ensure_ascii=False, default=str).replace(key, "[REDACTED]"))

    def transport(url, headers, body, timeout):
        require(not active["halted"], "External requests stopped after transport/provider failure")
        require(url == ENDPOINT, "Unexpected data destination")
        payload = json.loads(body)
        expected = research.PLUS if active["stage"] == research.S07 else research.FLASH
        require(payload["model"] == expected and payload["enable_thinking"] is False, "Model route drift")
        index = len(transports) + 1
        require(not any(t["stage_call_index"] == active["index"] for t in transports), "Harness retry prohibited")
        record = {"transport_index": index, "stage_call_index": active["index"], "stage": active["stage"],
                  "requested_model": expected, "started_at": now(), "usage": None, "request_body_sha256": hashlib.sha256(body).hexdigest()}
        transports.append(record)
        save(calls_dir / ("codex_%03d_wire_request.json" % index), payload)
        started = time.monotonic()
        raw = None
        try:
            request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            try:
                with opener.open(request, timeout=timeout) as response:
                    status, response_headers, raw_bytes = response.status, dict(response.headers.items()), response.read()
            except urllib.error.HTTPError as exc:
                status, response_headers, raw_bytes = exc.code, dict(exc.headers.items()), exc.read()
            try:
                raw = json.loads(raw_bytes)
            except (ValueError, UnicodeDecodeError):
                raw = {"unparsed": raw_bytes.decode("utf-8", errors="replace")}
            record.update(status="HTTP_RETURNED", http_status=status, provider_model=raw.get("model"),
                          finish_reasons=[c.get("finish_reason") for c in raw.get("choices", [])])
            usage = raw.get("usage") or {}
            incoming, outgoing = usage.get("prompt_tokens", usage.get("input_tokens")), usage.get("completion_tokens", usage.get("output_tokens"))
            if all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in (incoming, outgoing)):
                i_rate, o_rate = research.pricing_rates(expected, incoming)
                record["usage"] = {"input_tokens": incoming, "output_tokens": outgoing,
                    "estimated_cost_cny": (incoming*i_rate + outgoing*o_rate)/1e6,
                    "input_rate_per_million": i_rate, "output_rate_per_million": o_rate, "basis": research.PRICE_BASIS}
            if status != 200:
                active["halted"] = True
            else:
                require(raw.get("model") == expected and record["finish_reasons"] == ["stop"], "Unexpected provider model or incomplete response")
            return status, response_headers, raw_bytes
        except Exception as exc:
            active["halted"] = True
            record.update(status="FAILED", error_type=type(exc).__name__)
            raise
        finally:
            record.update(duration_seconds=time.monotonic()-started, completed_at=now())
            save(calls_dir / ("codex_%03d_provider.json" % index), clean({**record, "payload": raw}))

    def audit_sink(event, record):
        if record["short_references"]:
            save(calls_dir / ("codex_%03d_s07_%s.json" % (record["index"], event.lower())), record)

    base = research.make_gateway(key, transport=transport)

    class TracingGateway(research.ResearchGateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            index = len(calls)+1
            active.update(index=index, stage=stage)
            record = {"index": index, "stage": stage, "started_at": now(), "status": "STARTED"}
            calls.append(record)
            save(calls_dir / ("codex_%03d_request.json" % index), {**record, "prompt": prompt, "schema": schema,
                "context": context, "evidence": [{"asset_id": a["asset_id"], "frame_id": f["frame_id"], "local_path": str(p)} for a,f,p in evidence]})
            emit({"event": "CALL_STARTED", "pack": pack_id, "index": index, "stage": stage})
            started = time.monotonic()
            output = None
            try:
                run = super().call(stage, prompt, schema, evidence=evidence, context=context)
                output = run.output
                record.update(status="COMPLETED", metric=x02._metric_from_run(run))
                return run
            except Exception as exc:
                record.update(status="FAILED", error_type=type(exc).__name__, code=getattr(exc,"code",None))
                raise
            finally:
                record.update(duration_seconds=time.monotonic()-started, completed_at=now())
                save(calls_dir / ("codex_%03d_response.json" % index), clean({**record, "output": output}))
                emit({"event": "CALL_FINISHED", "pack": pack_id, "index": index, "stage": stage,
                      "status": record["status"], "seconds": round(record["duration_seconds"],2)})

    gateway = TracingGateway(base.default_gateway, base.structure_gateway, audit_sink=audit_sink)
    report = {"experiment": "CODEX_V1_69_FULL_CHAIN", "algorithm_candidate": "V1.69", "pack_id": pack_id,
              "round": 1, "started_at": now(), "candidate_sha256": CANDIDATE_SHA, "source_sha256": candidate["source_sha256"],
              "runner_sha256": sha(__file__), "preparation_sha256": sha(AREA / "codex_preparation.json"),
              "manifest_sha256": sha(directory / "codex_manifest.json"), "normalization_sha256": sha(directory / "codex_normalization.json"),
              "research_profile": research.profile(), "credential_source": credential_source,
              "evaluation_run_mode": "FRESH_FULL_RUN", "cross_run_semantic_cache_used": False,
              "pipeline_scope": "NORMALIZATION_AND_S04_S12_NOT_S13_EXPORT", "quality_status": "AWAITING_REAL_CONTENT_REVIEW",
              "normalization_seconds": normal["totalPreparationMs"]/1000}
    started = time.monotonic()
    try:
        result = research.run_research(directory / "codex_manifest.json", gateway)
        report.update(status="RETURNED", **result)
    except Exception as exc:
        report.update(status="FAILED", error_type=type(exc).__name__, error_message=clean(str(exc)), error_code=getattr(exc,"code",None))
    finally:
        known = [t["usage"] for t in transports if t["usage"] is not None]
        report.update(completed_at=now(), duration_seconds=time.monotonic()-started, stage_calls=calls, transport_attempts=transports,
            gateway_audit=copy.deepcopy(gateway.calls), known_input_tokens=sum(u["input_tokens"] for u in known),
            known_output_tokens=sum(u["output_tokens"] for u in known),
            estimated_cost_cny_known=sum(u["estimated_cost_cny"] for u in known) if known else None,
            usage_unknown_calls=len(transports)-len(known), provider_usage_complete=bool(transports) and len(known)==len(transports),
            unknown_usage_is_not_zero=True, source_unchanged_after_execution=bool(verify()))
        report["end_to_end_seconds"] = report["normalization_seconds"] + report["duration_seconds"]
        save(directory / "codex_full_run.json", clean(report))
    result = report.get("result", {})
    emit({"event": "PACK_FINISHED", "pack": pack_id, "status": report["status"],
          "chapters": len(result.get("chapters",[])), "ahas": len(result.get("ahas",[])),
          "calls": len(transports), "seconds": report["end_to_end_seconds"], "cost_cny_known": report["estimated_cost_cny_known"]})
    return 0 if report["status"] == "RETURNED" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "normalize", "run"))
    parser.add_argument("--pack", choices=("1", "2", "3"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        require(args.pack is None and not args.live, "Preparation is local only")
        prepare()
    elif args.command == "normalize":
        require(args.pack is not None and not args.live, "Normalize one explicit pack only")
        sys.exit(normalize(args.pack))
    else:
        require(args.pack is not None, "Run one explicit pack only")
        sys.exit(run(args.pack, args.live))
