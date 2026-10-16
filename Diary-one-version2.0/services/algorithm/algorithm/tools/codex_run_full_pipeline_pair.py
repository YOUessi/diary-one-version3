"""One fresh real-media run from an isolated pinned source version.

No new algorithm, semantic rule, money gate, automatic experiment repeat or Web mutation.
No model call unless --live; originals never enter the model transport.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_content_handoff_ab_v1_47"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def audit_context_bytes(context):
    # S04 includes local Path objects. Convert only the audit copy, never model input.
    def encode(value):
        if isinstance(value, Path):
            return str(value)
        raise TypeError("Unsupported audit value: " + type(value).__name__)
    return json.dumps(context or {}, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=encode).encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("baseline", "candidate"))
    parser.add_argument("--pack", choices=("1", "2", "3"), default="1")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--attempt", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    preparation = json.loads((AREA / "codex_preparation_manifest.json").read_text())
    version = "baseline_v1_45" if args.variant == "baseline" else "candidate_v1_46"
    pin = preparation["versions"][version]
    source = AREA / ("codex_" + version)
    for relative, expected in pin["file_sha256"].items():
        if digest(source / relative) != expected:
            raise RuntimeError("Pinned source mismatch: " + relative)
    sys.path.insert(0, str(source / "src"))
    from diary_one_ci import x02
    from diary_one_ci.bundle import load_app_library_bundle
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    from diary_one_ci.x01_server import _resolve_qwen_api_key

    if not Path(x02.__file__).resolve().is_relative_to(source.resolve()):
        raise RuntimeError("Wrong runtime import path")
    directory = AREA / ("codex_v1_48_person" + args.pack) / args.variant
    manifest_path = directory / "codex_manifest.json"
    bundle = load_app_library_bundle(manifest_path)
    pack = next(p for p in preparation["packs"] if p["pack_id"] == args.pack)
    if [a["original_sha256"] for a in bundle.manifest["assets"]] != [a["sha256"] for a in pack["assets"]]:
        raise RuntimeError("Input pack or order mismatch")
    # Exercise logging with the actual evidence objects before any paid request.
    evidence = x02._perception_evidence(bundle, bundle.manifest["assets"])
    audit_context_bytes({"assets": bundle.manifest["assets"], "evidence": evidence})
    if not args.live:
        print(json.dumps({"status": "INPUT_AND_RUNTIME_VERIFIED_NO_MODEL_CALL", "variant": args.variant,
                          "assets": len(bundle.manifest["assets"]), "source": str(source)}), flush=True)
        return 0
    if args.attempt > 1:
        directory = directory / ("codex_attempt_%02d" % args.attempt)
    report_path = directory / "codex_full_run.json"
    calls_dir = directory / "codex_stage_calls"
    if report_path.exists() or calls_dir.exists():
        raise RuntimeError("Refusing to rerun or overwrite an existing experiment")
    directory.mkdir(exist_ok=True)
    key, credential_source = _resolve_qwen_api_key()
    if not key:
        raise RuntimeError("Existing research credential unavailable; no model call made")
    adapter = QwenChatCompletionsAdapter(
        api_key=key, model=preparation["proposed_model"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", timeout_seconds=180,
    )
    calls_dir.mkdir()
    calls = []

    class TracingGateway(x02.QwenStageGateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            index = len(calls) + 1
            record = {"index": index, "stage": stage, "prompt": prompt, "schema": schema,
                      "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                      "context_sha256": hashlib.sha256(audit_context_bytes(context)).hexdigest(),
                      "evidence": [{"asset_id": a["asset_id"], "frame_id": f["frame_id"],
                                    "sha256": f["sha256"]} for a, f, p in evidence]}
            save(calls_dir / ("codex_%03d_request.json" % index), record)
            calls.append({"index": index, "stage": stage, "status": "STARTED"})
            print(json.dumps({"event": "CALL_STARTED", "index": index, "stage": stage,
                              "frames": len(evidence)}), flush=True)
            started = time.monotonic()
            run = None
            try:
                run = super().call(stage, prompt, schema, evidence=evidence, context=context)
                record = {"status": "COMPLETED", "output": run.output}
                return run
            except Exception as exc:
                run = getattr(exc, "stage_run", None)
                record = {"status": "FAILED", "error_type": type(exc).__name__,
                          "error_code": getattr(exc, "code", None)}
                raise
            finally:
                record["stage"] = stage
                record["duration_seconds"] = time.monotonic() - started
                record["metric"] = x02._metric_from_run(run) if run else None
                if run and (run.input_tokens or run.output_tokens):
                    rate = 0.15 if run.input_tokens <= 32768 else 0.30 if run.input_tokens <= 131072 else 0.60
                    record["recomputed_cost_cny"] = (run.input_tokens * rate + run.output_tokens * rate * 10) / 1_000_000
                    record["cost_status"] = "ESTIMATED_FROM_REPORTED_USAGE_2026_09_04_BEIJING_TIERS"
                else:
                    record["recomputed_cost_cny"] = None
                    record["cost_status"] = "USAGE_UNAVAILABLE_NOT_ZERO_COST"
                calls[-1].update({k: v for k, v in record.items() if k != "output"})
                save(calls_dir / ("codex_%03d_response.json" % index), record)
                print(json.dumps({k: v for k, v in calls[-1].items() if k != "metric"}), flush=True)

    report = {"experiment": "CODEX_V1_48_PERSON_FULL_PAIR", "variant": args.variant, "pack_id": args.pack,
              "attempt": args.attempt, "harness_sha256": digest(Path(__file__)),
              "source_version": version, "source_archive_sha256": pin["archive_sha256"],
              "manifest_sha256": digest(manifest_path), "credential_source": credential_source,
              "model": adapter.model, "evaluation_run_mode": "FRESH_FULL_RUN",
              "cross_run_semantic_cache_used": False, "quality_status": "NOT_USER_REVIEWED"}
    started = time.monotonic()
    try:
        result = x02.run_x02(manifest_path, TracingGateway(adapter))
        has_brief = "content_handoff" in result.get("decision_trace", {})
        if has_brief != (args.variant == "candidate"):
            raise RuntimeError("Result handoff policy does not match selected version")
        report.update(status="PIPELINE_BLOCKED" if result.get("delivery_state") == "PIPELINE_BLOCKED"
                      else "COMPLETED", execution_status="RETURNED", result=result)
    except Exception as exc:
        report.update(status="FAILED", error_type=type(exc).__name__,
                      error_code=getattr(exc, "code", None), error_message=str(exc))
    finally:
        report["duration_seconds"] = time.monotonic() - started
        report["stage_calls"] = calls
        report["known_recomputed_cost_cny"] = sum(c.get("recomputed_cost_cny") or 0 for c in calls)
        report["unpriced_call_count"] = sum(c.get("recomputed_cost_cny") is None for c in calls)
        save(report_path, report)
    result = report.get("result", {})
    print(json.dumps({"event": "RUN_FINISHED", "status": report["status"], "variant": args.variant,
                      "chapters": len(result.get("chapters", [])), "ahas": len(result.get("ahas", [])),
                      "calls": len(calls), "seconds": report["duration_seconds"],
                      "known_cost_cny": report["known_recomputed_cost_cny"],
                      "unpriced_calls": report["unpriced_call_count"], "report": str(report_path)}), flush=True)
    return 0 if report["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
