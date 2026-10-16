"""One fresh pack per command, frozen V1.73; no API without explicit --live."""

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
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import codex_run_full_chain_v1_71 as base


require = base.require
now = base.now
sha = base.sha
load = base.load
save = base.save
emit = base.emit
NORMALIZER = ROOT / "tools/codex_prepare_experience_first_evidence_v1_68.mjs"
NORMALIZER_SHA = "e7795b18537ea94e6e7364fd2fbf9c505fecc7daa5885fea7963e458a55cbe88"
LOADER = ROOT / "tools/codex_v173_normalizer_loader.mjs"
LOADER_SHA = "1f4970803acb82a78437fe8105611131076f46d1b57015edad552199b304685b"
FROZEN = ROOT / "var/codex_v1_73_aha_set_editor"
AREA = ROOT / "var/codex_v1_73_full_chain_execution"
PRIOR = ROOT / "var/codex_v1_72_1_focus_frame_writer_exit"
PRIOR_RUN = ROOT / "var/codex_v1_72_1_full_chain_execution"
CANDIDATE_SHA = "e1ae4fcbfb587562238cd9635f84d9b7599f645924ee38b4b12ae6e91c181ec2"
PRIOR_SHA = "97d5b36efbc0b9e59369fe14b3904f7008f925bf3f5b2cec421137208dd8715c"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


def runtime():
    snapshot = FROZEN / "codex_candidate_runtime"
    sys.path.insert(0, str(snapshot / "src"))
    from diary_one_ci import codex_d4_research as research
    from diary_one_ci import x02
    for name, module in list(sys.modules.items()):
        if name == "diary_one_ci" or name.startswith("diary_one_ci."):
            require(Path(module.__file__).resolve().is_relative_to(snapshot),
                    "Import escaped frozen candidate")
    return research, x02


def verify():
    require(sha(FROZEN / "codex_candidate.json") == CANDIDATE_SHA,
            "V1.73 candidate receipt drift")
    require(sha(PRIOR / "codex_candidate.json") == PRIOR_SHA,
            "V1.72.1 candidate drift")
    candidate = load(FROZEN / "codex_candidate.json")
    for name, digest in candidate["source_sha256"].items():
        require(sha(FROZEN / "codex_candidate_runtime" / name) == digest,
                "Frozen source drift: " + name)
        require(sha(ROOT / name) == digest, "Active source drift: " + name)
    require(sha(NORMALIZER) == NORMALIZER_SHA, "Frozen extraction harness drift")
    require(sha(LOADER) == LOADER_SHA, "V1.73 loader drift")
    research, x02 = runtime()
    require(research.profile() == candidate["research_profile"], "Research profile drift")
    return candidate, x02.x02_runtime_policies()


def prepare():
    candidate, policies = verify()
    require(not AREA.exists(), "Never overwrite a run area")
    origin = load(PRIOR_RUN / "codex_preparation.json")
    require(origin["candidate_sha256"] == PRIOR_SHA, "V1.72.1 pack inventory origin drift")
    packs = copy.deepcopy(origin["packs"])
    for pack in packs:
        pack["session_id"] = str(uuid.uuid5(
            uuid.NAMESPACE_URL, "codex-v173-full-pack-" + str(pack["pack_id"])
        ))
        pack["exported_at"] = now()
    AREA.mkdir()
    shutil.copyfile(FROZEN / "codex_candidate.json", AREA / "codex_candidate.json")
    save(AREA / "codex_preparation.json", {
        "experiment": "CODEX_V1_73_FULL_CHAIN",
        "algorithm_baseline": "V1.72.1",
        "algorithm_candidate": "V1.73",
        "candidate_sha256": CANDIDATE_SHA,
        "created_at": now(),
        "packs": packs,
        "authorized_pack_inventory_origin": str(PRIOR_RUN / "codex_preparation.json"),
        "authorized_pack_inventory_sha256": sha(PRIOR_RUN / "codex_preparation.json"),
        "normalizer_snapshot": origin["normalizer_snapshot"],
        "normalizer_sha256": origin["normalizer_sha256"],
        "normalizer_preparation_sha256": origin["normalizer_preparation_sha256"],
        "normalization_harness_sha256": NORMALIZER_SHA,
        "loader_sha256": LOADER_SHA,
        "runner_sha256": sha(Path(__file__)),
        "research_profile": candidate["research_profile"],
        "runtime_policies": policies,
        "pack_order": [1, 2, 3],
        "rounds_per_pack": 1,
        "fresh_decode_and_extraction": True,
        "cross_run_semantic_cache": False,
        "harness_retries": 0,
        "external_payload": "AUTHORIZED_NORMALIZED_FRAMES_AND_DERIVED_TEXT_NO_ORIGINALS",
        "pipeline_scope": "NORMALIZATION_THEN_S04_S12_NOT_S13",
        "deployment": "NO_WEB_APP_SWITCH",
    })
    emit({"event": "PREPARED_NO_API", "packs": {
        pack["pack_id"]: len(pack["assets"]) for pack in packs
    }})


def preparation():
    candidate, policies = verify()
    prep = load(AREA / "codex_preparation.json")
    require(prep["candidate_sha256"] == CANDIDATE_SHA
            and sha(AREA / "codex_candidate.json") == CANDIDATE_SHA,
            "Preparation candidate drift")
    require(prep["runner_sha256"] == sha(Path(__file__))
            and prep["loader_sha256"] == sha(LOADER), "Execution harness drift")
    require(prep["research_profile"] == candidate["research_profile"]
            and prep["runtime_policies"] == policies, "Runtime profile drift")
    return prep, candidate


def normalize(pack_id):
    preparation()
    require(not (AREA / ("pack_" + pack_id)).exists(), "Normalization already attempted")
    return subprocess.run([
        "node", "--no-warnings", "--experimental-loader", str(LOADER),
        str(NORMALIZER), pack_id,
    ], cwd=ROOT, check=False).returncode


def validate_input(pack_id):
    prep, candidate = preparation()
    directory = AREA / ("pack_" + pack_id) / "round_1"
    normal = load(directory / "codex_normalization.json")
    manifest = directory / "codex_manifest.json"
    require(normal["status"] == "READY" and normal["freshDecodeAndExtraction"] is True,
            "Fresh normalization missing")
    require(normal["candidate_sha256"] == CANDIDATE_SHA
            and normal["manifest_sha256"] == sha(manifest), "Normalization provenance drift")
    for frame in normal["frames"]:
        require(sha(directory / frame["relative_path"]) == frame["sha256"],
                "Evidence frame drift")
    research, x02 = runtime()
    from diary_one_ci.bundle import load_app_library_bundle
    bundle = load_app_library_bundle(manifest)
    pack = next(item for item in prep["packs"] if str(item["pack_id"]) == pack_id)
    require([asset["original_sha256"] for asset in bundle.manifest["assets"]]
            == [asset["sha256"] for asset in pack["assets"]], "Input identity drift")
    require(bundle.manifest["session"]["session_id"] == pack["session_id"], "Session drift")
    return prep, candidate, directory, normal, bundle, research, x02


def run(pack_id, live):
    _, candidate, directory, normal, bundle, research, x02 = validate_input(pack_id)
    if not live:
        emit({"event": "VERIFIED_NO_API", "pack": pack_id,
              "assets": len(bundle.manifest["assets"]), "frames": len(normal["frames"])})
        return 0
    with (AREA / "codex_serial.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not (directory / "codex_attempt.json").exists(),
                "This pack was already attempted")
        for previous in range(1, int(pack_id)):
            require((AREA / ("pack_%d/round_1/codex_full_run.json" % previous)).exists(),
                    "Earlier pack missing")
        from diary_one_ci.x01_server import _resolve_qwen_api_key
        key, credential_source = _resolve_qwen_api_key()
        require(bool(key), "Existing credential unavailable; no request sent")
        save(directory / "codex_attempt.json", {
            "started_at": now(), "candidate_sha256": CANDIDATE_SHA,
            "preparation_sha256": sha(AREA / "codex_preparation.json"),
            "credential_source": credential_source,
        })
        return execute(pack_id, directory, normal, candidate, research, x02,
                       key, credential_source)


def execute(pack_id, directory, normal, candidate, research, x02, key, credential_source):
    calls_dir = directory / "codex_stage_calls"
    calls_dir.mkdir()
    calls, transports = [], []
    active = {"index": 0, "stage": None, "halted": False}

    def clean(value):
        return json.loads(json.dumps(
            value, ensure_ascii=False, default=str
        ).replace(key, "[REDACTED]"))

    def transport(url, headers, body, timeout):
        require(not active["halted"], "Requests stopped after failure")
        require(url == ENDPOINT, "Unexpected data destination")
        payload = json.loads(body)
        plus_stage = (
            active["stage"] in (research.routing.S07, research.editor.EDITOR_STAGE)
            or str(active["stage"]).startswith("S11_")
        )
        expected = research.routing.PLUS if plus_stage else research.routing.FLASH
        require(payload["model"] == expected and payload["enable_thinking"] is False,
                "Model route drift")
        index = len(transports) + 1
        record = {
            "transport_index": index, "stage_call_index": active["index"],
            "stage": active["stage"], "requested_model": expected,
            "started_at": now(), "usage": None,
            "request_body_sha256": hashlib.sha256(body).hexdigest(),
        }
        transports.append(record)
        save(calls_dir / ("codex_%03d_wire_request.json" % index), payload)
        started = time.monotonic()
        raw = None
        try:
            request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            try:
                with opener.open(request, timeout=timeout) as response:
                    status, response_headers, raw_bytes = (
                        response.status, dict(response.headers.items()), response.read()
                    )
            except urllib.error.HTTPError as exc:
                status, response_headers, raw_bytes = exc.code, dict(exc.headers.items()), exc.read()
            try:
                raw = json.loads(raw_bytes)
            except (ValueError, UnicodeDecodeError):
                raw = {"unparsed": raw_bytes.decode("utf-8", errors="replace")}
            record.update(
                status="HTTP_RETURNED", http_status=status, provider_model=raw.get("model"),
                finish_reasons=[choice.get("finish_reason") for choice in raw.get("choices", [])],
            )
            usage = raw.get("usage") or {}
            incoming = usage.get("prompt_tokens", usage.get("input_tokens"))
            outgoing = usage.get("completion_tokens", usage.get("output_tokens"))
            if all(isinstance(value, int) and not isinstance(value, bool) and value >= 0
                   for value in (incoming, outgoing)):
                input_rate, output_rate = research.routing.pricing_rates(expected, incoming)
                record["usage"] = {
                    "input_tokens": incoming, "output_tokens": outgoing,
                    "estimated_cost_cny": (
                        incoming * input_rate + outgoing * output_rate
                    ) / 1_000_000,
                    "input_rate_per_million": input_rate,
                    "output_rate_per_million": output_rate,
                    "basis": research.routing.PRICE_BASIS,
                }
            if 400 <= status < 500:
                active["halted"] = True
            else:
                require(raw.get("model") == expected
                        and record["finish_reasons"] == ["stop"],
                        "Unexpected provider response")
            return status, response_headers, raw_bytes
        except Exception as exc:
            transient_timeout = (
                isinstance(exc, TimeoutError)
                or "timed out" in str(exc).casefold()
                or type(exc).__name__.casefold() == "timeout"
            )
            if not transient_timeout:
                active["halted"] = True
            record.update(status="FAILED", error_type=type(exc).__name__)
            raise
        finally:
            record.update(duration_seconds=time.monotonic() - started, completed_at=now())
            save(calls_dir / ("codex_%03d_provider.json" % index),
                 clean({**record, "payload": raw}))

    def audit_sink(event, record):
        if record["short_references"]:
            save(calls_dir / ("codex_%03d_short_refs_%s.json" %
                              (record["index"], event.lower())), record)

    base_gateway = research.make_gateway(key, transport=transport)

    class TracingGateway(research.ResearchGateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            index = len(calls) + 1
            active.update(index=index, stage=stage)
            record = {"index": index, "stage": stage, "started_at": now(), "status": "STARTED"}
            calls.append(record)
            save(calls_dir / ("codex_%03d_request.json" % index), {
                **record, "prompt": prompt, "schema": schema, "context": context,
                "evidence": [{
                    "asset_id": asset["asset_id"], "frame_id": frame["frame_id"],
                    "local_path": str(path),
                } for asset, frame, path in evidence],
            })
            emit({"event": "CALL_STARTED", "pack": pack_id, "index": index, "stage": stage})
            started = time.monotonic()
            output = None
            try:
                result = super().call(stage, prompt, schema, evidence=evidence, context=context)
                output = result.output
                record.update(status="COMPLETED", metric=x02._metric_from_run(result))
                return result
            except Exception as exc:
                record.update(status="FAILED", error_type=type(exc).__name__,
                              code=getattr(exc, "code", None))
                raise
            finally:
                record.update(duration_seconds=time.monotonic() - started, completed_at=now())
                save(calls_dir / ("codex_%03d_response.json" % index),
                     clean({**record, "output": output}))
                emit({"event": "CALL_FINISHED", "pack": pack_id, "index": index,
                      "stage": stage, "status": record["status"],
                      "seconds": round(record["duration_seconds"], 2)})

    gateway = TracingGateway(
        base_gateway.default_gateway, base_gateway.structure_gateway,
        audit_sink=audit_sink,
    )
    report = {
        "experiment": "CODEX_V1_73_FULL_CHAIN", "algorithm_candidate": "V1.73",
        "pack_id": pack_id, "round": 1, "started_at": now(),
        "candidate_sha256": CANDIDATE_SHA, "source_sha256": candidate["source_sha256"],
        "runner_sha256": sha(Path(__file__)),
        "preparation_sha256": sha(AREA / "codex_preparation.json"),
        "manifest_sha256": sha(directory / "codex_manifest.json"),
        "normalization_sha256": sha(directory / "codex_normalization.json"),
        "research_profile": research.profile(), "credential_source": credential_source,
        "evaluation_run_mode": "FRESH_FULL_RUN", "cross_run_semantic_cache_used": False,
        "pipeline_scope": "NORMALIZATION_AND_S04_S12_NOT_S13",
        "quality_status": "AWAITING_REAL_CONTENT_REVIEW",
        "normalization_seconds": normal["totalPreparationMs"] / 1000,
    }
    started = time.monotonic()
    try:
        result = research.run_research(directory / "codex_manifest.json", gateway)
        report.update(status="RETURNED", **result)
    except Exception as exc:
        report.update(status="FAILED", error_type=type(exc).__name__,
                      error_message=clean(str(exc)), error_code=getattr(exc, "code", None))
    finally:
        known = [item["usage"] for item in transports if item["usage"] is not None]
        report.update(
            completed_at=now(), duration_seconds=time.monotonic() - started,
            stage_calls=calls, transport_attempts=transports,
            gateway_audit=copy.deepcopy(gateway.calls),
            known_input_tokens=sum(item["input_tokens"] for item in known),
            known_output_tokens=sum(item["output_tokens"] for item in known),
            estimated_cost_cny_known=(
                sum(item["estimated_cost_cny"] for item in known) if known else None
            ),
            usage_unknown_calls=len(transports) - len(known),
            provider_usage_complete=bool(transports) and len(known) == len(transports),
            unknown_usage_is_not_zero=True,
            source_unchanged_after_execution=bool(verify()),
        )
        report["end_to_end_seconds"] = report["normalization_seconds"] + report["duration_seconds"]
        save(directory / "codex_full_run.json", clean(report))
    result = report.get("result", {})
    emit({"event": "PACK_FINISHED", "pack": pack_id, "status": report["status"],
          "chapters": len(result.get("chapters", [])), "ahas": len(result.get("ahas", [])),
          "calls": len(transports), "seconds": report["end_to_end_seconds"],
          "cost_cny_known": report["estimated_cost_cny_known"]})
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

