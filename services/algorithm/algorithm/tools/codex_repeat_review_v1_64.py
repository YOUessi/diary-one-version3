"""Frozen V1.63, three real packs x three full runs; experiment only, no policy edits."""
import argparse
import hashlib
import json
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_64_repeat_review"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen3-vl-flash-2026-01-22"
PINS = {
    "x02.py": "a609c1c6a6506657674351ef5d3682bc62937296d3560919517c16041fa7aed3",
    "bundle.py": "67a0bd1da43bd8e49bfb22d6f47761a1e702581f4d0c71d8fd8d2a2f67ab4074",
    "x01_server.py": "00433af5202f17d2ce329f7c5c5fcd51cb4ace8400e4f9576d2dfb64db9f1399",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, default=lambda x: str(x) if isinstance(x, Path) else None)
        stream.write("\n")


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def prepare():
    for name, expected in PINS.items():
        assert sha(ROOT / "src/diary_one_ci" / name) == expected, "V1.63 source drift: " + name
    assert not AREA.exists(), "Refusing to overwrite an experiment"
    original = ROOT / "var/codex_content_handoff_ab_v1_47/codex_preparation_manifest.json"
    old = json.loads(original.read_text())
    packs = []
    for pack in old["packs"]:
        for item in pack["assets"]:
            assert sha(Path(pack["source_root"]) / item["relative_path"]) == item["sha256"], "Original drift"
        packs.append({**pack, "session_id": str(uuid.uuid5(uuid.NAMESPACE_URL, "codex-v164-pack-" + pack["pack_id"])),
                      "exported_at": now()})
    AREA.mkdir()
    shutil.copytree(ROOT / "src", AREA / "codex_runtime/src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(ROOT / "contracts", AREA / "codex_runtime/contracts")
    web_dir = AREA / "codex_web_normalizer"
    web_dir.mkdir()
    for path in (ROOT.parent / "apps/eval-web/app/lib").glob("*.ts"):
        shutil.copy2(path, web_dir / path.name)
    source_hashes = {str(p.relative_to(AREA / "codex_runtime")): sha(p)
                     for p in (AREA / "codex_runtime").rglob("*") if p.is_file()}
    normalizer_hashes = {p.name: sha(p) for p in web_dir.glob("*.ts")}
    preparation = {"experiment": "CODEX_V1_64_REPEAT_REVIEW", "algorithm_baseline": "V1.63",
                   "created_at": now(), "planned_rounds": 3, "packs": packs,
                   "source_inventory_path": str(original), "source_inventory_sha256": sha(original),
                   "source_sha256": source_hashes, "normalizer_sha256": normalizer_hashes,
                   "model": MODEL, "endpoint": ENDPOINT,
                   "source_order": "PRIOR_AUTHORIZED_INVENTORY_RELATIVE_PATH_ORDER_NOT_CAPTURE_TIME",
                   "capture_time_used": False, "gps_used": False,
                   "external_payload": "NORMALIZED_JPEG_FRAMES_AND_DERIVED_TEXT_ONLY_NO_ORIGINALS",
                   "execution": "REDECODE_EACH_ROUND_FRESH_FULL_SEMANTIC_PIPELINE_NO_CROSS_RUN_CACHE",
                   "quality_status": "EXPLORATORY_DEVELOPER_REVIEW_NOT_USER_RATINGS_OR_HELD_OUT_EVAL",
                   "scope": "NO_ALGORITHM_WEB_APP_FIRMWARE_OR_SHARED_STATUS_EDITS"}
    save(AREA / "codex_preparation.json", preparation)
    emit({"event": "PREPARED", "area": str(AREA), "packs": [{"id": p["pack_id"], "assets": len(p["assets"])} for p in packs]})


def run(pack_id, round_number, live):
    prep = json.loads((AREA / "codex_preparation.json").read_text())
    source = AREA / "codex_runtime"
    for relative, expected in prep["source_sha256"].items():
        assert sha(source / relative) == expected, "Pinned runtime drift: " + relative
    sys.path.insert(0, str(source / "src"))
    from diary_one_ci import x02
    from diary_one_ci.bundle import load_app_library_bundle
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    from diary_one_ci.x01_server import _resolve_qwen_api_key
    assert Path(x02.__file__).resolve().is_relative_to(source.resolve())
    directory = AREA / ("pack_" + pack_id) / ("round_" + str(round_number))
    manifest_path = directory / "codex_manifest.json"
    bundle = load_app_library_bundle(manifest_path)
    pack = next(p for p in prep["packs"] if p["pack_id"] == pack_id)
    assert [a["original_sha256"] for a in bundle.manifest["assets"]] == [a["sha256"] for a in pack["assets"]]
    assert bundle.manifest["bundle_version"] == "DIARY_ONE_APP_LIBRARY_BUNDLE_V04"
    assert all(f["spatial_transform"] == "ASPECT_FIT_LETTERBOX" for a in bundle.manifest["assets"] for f in a["frames"])
    policies = x02.x02_runtime_policies()
    assert policies["subject_granularity"] == "DIARY_ONE_X02_SUBJECT_GRANULARITY_V02"
    summary = {"pack": pack_id, "round": round_number, "assets": len(bundle.manifest["assets"]),
               "frames": sum(len(a["frames"]) for a in bundle.manifest["assets"]), "policies": policies}
    if not live:
        emit({"event": "VERIFIED_NO_MODEL_CALL", **summary})
        return 0
    assert not (directory / "codex_full_run.json").exists()
    calls_dir = directory / "codex_stage_calls"
    assert not calls_dir.exists(), "Refusing to repeat an attempted run"
    key, credential_source = _resolve_qwen_api_key()
    assert key, "Existing Qwen research credential unavailable"
    calls_dir.mkdir()
    calls = []
    active = {"index": 0}
    base_transport = QwenChatCompletionsAdapter._url_transport

    def trace_transport(url, headers, body, timeout):
        assert url == ENDPOINT, "Unexpected external destination"
        payload = json.loads(body)
        assert payload["model"] == MODEL
        # Raw provider body is retained locally for forensic review; never log auth headers.
        status, response_headers, response = base_transport(url, headers, body, timeout)
        try:
            raw = json.loads(response)
        except (ValueError, UnicodeDecodeError):
            raw = {"unparsed_utf8": response.decode("utf-8", errors="replace")}
        save(calls_dir / ("codex_%03d_provider.json" % active["index"]),
             {"http_status": status, "request_body_sha256": hashlib.sha256(body).hexdigest(), "payload": raw})
        return status, response_headers, response

    adapter = QwenChatCompletionsAdapter(api_key=key, model=MODEL,
        base_url=ENDPOINT.removesuffix("/chat/completions"), timeout_seconds=180, transport=trace_transport)

    class TracingGateway(x02.QwenStageGateway):
        def call(self, stage, prompt, schema, evidence=(), context=None):
            index = len(calls) + 1
            active["index"] = index
            save(calls_dir / ("codex_%03d_request.json" % index),
                 {"index": index, "stage": stage, "prompt": prompt, "schema": schema, "context": context,
                  "evidence": [{"asset_id": a["asset_id"], "frame_id": f["frame_id"], "sha256": f["sha256"],
                                "local_path": str(p)} for a, f, p in evidence]})
            calls.append({"index": index, "stage": stage, "status": "STARTED"})
            emit({"event": "CALL_STARTED", "pack": pack_id, "round": round_number, "index": index, "stage": stage})
            started = time.monotonic()
            stage_run = None
            record = {}
            try:
                stage_run = super().call(stage, prompt, schema, evidence=evidence, context=context)
                record = {"status": "COMPLETED", "output": stage_run.output}
                return stage_run
            except Exception as exc:
                stage_run = getattr(exc, "stage_run", None)
                record = {"status": "FAILED", "error_type": type(exc).__name__, "code": getattr(exc, "code", None)}
                raise
            finally:
                record.update(stage=stage, duration_seconds=time.monotonic() - started,
                              metric=x02._metric_from_run(stage_run) if stage_run else None)
                if stage_run and (stage_run.input_tokens or stage_run.output_tokens):
                    rate = 0.15 if stage_run.input_tokens <= 32768 else 0.30 if stage_run.input_tokens <= 131072 else 0.60
                    record["estimated_tiered_cost_cny"] = (stage_run.input_tokens * rate + stage_run.output_tokens * rate * 10) / 1_000_000
                    record["cost_basis"] = "EXISTING_EXPERIMENT_BEIJING_RATE_SNAPSHOT_NOT_BILLING_INVOICE"
                else:
                    record["estimated_tiered_cost_cny"] = None
                calls[-1].update({k: v for k, v in record.items() if k != "output"})
                save(calls_dir / ("codex_%03d_response.json" % index), record)
                emit({"event": "CALL_FINISHED", "pack": pack_id, "round": round_number,
                      "index": index, "stage": stage, "status": record["status"], "seconds": round(record["duration_seconds"], 2)})

    report = {"experiment": prep["experiment"], "algorithm_baseline": "V1.63", "pack_id": pack_id,
              "round": round_number, "started_at": now(), "harness_sha256": sha(Path(__file__)),
              "preparation_sha256": sha(AREA / "codex_preparation.json"), "manifest_sha256": sha(manifest_path),
              "credential_source": credential_source, "model": MODEL, "endpoint": ENDPOINT,
              "runtime_policies": policies, "evaluation_run_mode": "FRESH_FULL_RUN", "cross_run_semantic_cache_used": False,
              "quality_status": "NOT_USER_REVIEWED", "interface_scope": "SAME_WEB_NORMALIZER_AND_ALGORITHM_ENTRY_NO_HTTP_UI_TEST"}
    started = time.monotonic()
    try:
        result = x02.run_x02_v041(manifest_path, TracingGateway(adapter))
        report.update(status="RETURNED", result=result)
        assert result.get("runtime_policies", policies) == policies
    except Exception as exc:
        report.update(status="FAILED", error_type=type(exc).__name__, error_code=getattr(exc, "code", None), error_message=str(exc))
    finally:
        report.update(completed_at=now(), duration_seconds=time.monotonic() - started, stage_calls=calls,
                      estimated_tiered_cost_cny=sum(c.get("estimated_tiered_cost_cny") or 0 for c in calls),
                      unpriced_call_count=sum(c.get("estimated_tiered_cost_cny") is None for c in calls))
        save(directory / "codex_full_run.json", report)
    result = report.get("result", {})
    emit({"event": "RUN_FINISHED", **summary, "status": report["status"], "delivery": result.get("delivery_state"),
          "chapters": len(result.get("chapters", [])), "ahas": len(result.get("ahas", [])), "calls": len(calls),
          "seconds": report["duration_seconds"], "report": str(directory / "codex_full_run.json")})
    return 0 if report["status"] == "RETURNED" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    parser.add_argument("--pack", choices=("1", "2", "3"))
    parser.add_argument("--round", type=int, choices=(1, 2, 3))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    else:
        assert args.pack and args.round
        sys.exit(run(args.pack, args.round, args.live))
