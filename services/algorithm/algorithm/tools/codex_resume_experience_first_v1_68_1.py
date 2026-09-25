"""Resume V1.68 after a zero-response transport failure; no API unless --live."""

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_AREA = ROOT / "var/codex_v1_68_experience_first_chapter"
AREA = ROOT / "var/codex_v1_68_1_experience_first_chapter_transport"
BASE_HARNESS = ROOT / "tools/codex_experience_first_review_v1_68.py"
BASE_NORMALIZER = ROOT / "tools/codex_prepare_experience_first_evidence_v1_68.mjs"
NORMALIZER_LOADER = ROOT / "tools/codex_v1681_normalizer_loader.mjs"
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
PROBE_URL = "https://dashscope.aliyuncs.com/"
EXECUTION_REVISION = "V1.68.1_TRANSPORT_ONLY"
SOURCE_PREPARATION_SHA = "8d019dd3427ea5f1c539dd38cf7b82296dacdd345f316b94fd1256b1fc5972af"
SOURCE_CANDIDATE_SHA = "bf333f5c8bb8958b4b6fadca060b787584f53c78a4e029b8a8d33faa668f0c7a"
SOURCE_HARNESS_SHA = "67c3edb52a5f4a256c7b26c624c630ff5174b9883c79b009c9a60193f7ed0003"
SOURCE_NORMALIZER_HARNESS_SHA = "e7795b18537ea94e6e7364fd2fbf9c505fecc7daa5885fea7963e458a55cbe88"
SOURCE_FAILED_TREE_SHA = "48c05b7950e1201b104609854529a8b54ebf7c59202d649a1e5023c38e8acf9e"
SOURCE_NORMALIZATION_ANCHORS = {
    "1": {
        "normalization_sha256": "69727e9ad06acc34e94be452e15255a83db116c4508e140e507bd0419dcb3810",
        "manifest_sha256": "af36f7387643c4602fba1b41c15b2030529742e452306e45923fda4a08292934",
        "frame_count": 74,
    },
    "2": {
        "normalization_sha256": "4a117a597526b4197d1137a1dfcea53f0e0edbe2b4ce3da1d12904dec03ff9c6",
        "manifest_sha256": "c725b1fdaf04e26674ab7504acd3fc25bad72d00dc9e7eba43eb17cd533821d5",
        "frame_count": 39,
    },
    "3": {
        "normalization_sha256": "b629123832b538107935a1a6c0937f3d9a3b5d50b59e3d50c19632b59351acf3",
        "manifest_sha256": "6c50346297dd90079c63233c90dbb4f343f856b094b76dccf56e237250274e47",
        "frame_count": 74,
    },
}
sys.dont_write_bytecode = True


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, value):
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with Path(path).open("x", encoding="utf-8") as stream:
        stream.write(encoded)


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def tree_inventory(root):
    root = Path(root)
    inventory = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "Symlink not permitted in archived evidence")
        if path.is_file():
            inventory[path.relative_to(root).as_posix()] = sha(path)
    return inventory


def inventory_sha(inventory):
    encoded = json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_base_harness():
    require(sha(BASE_HARNESS) == SOURCE_HARNESS_SHA, "Frozen V1.68 run harness drift")
    spec = importlib.util.spec_from_file_location("codex_v168_frozen_harness", BASE_HARNESS)
    require(spec is not None and spec.loader is not None, "Could not load frozen V1.68 harness")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_source_area():
    preparation_path = SOURCE_AREA / "codex_preparation.json"
    candidate_path = SOURCE_AREA / "codex_candidate.json"
    require(sha(preparation_path) == SOURCE_PREPARATION_SHA, "V1.68 preparation drift")
    require(sha(candidate_path) == SOURCE_CANDIDATE_SHA, "V1.68 candidate receipt drift")
    candidate = load(candidate_path)
    require(candidate["harness_sha256"] == SOURCE_HARNESS_SHA, "V1.68 harness receipt drift")
    require(candidate["normalization_harness_sha256"] == SOURCE_NORMALIZER_HARNESS_SHA,
            "V1.68 normalizer receipt drift")
    require(candidate["algorithm_candidate"] == "V1.68", "Unexpected algorithm candidate")
    require(tree_inventory(SOURCE_AREA / "codex_candidate_runtime") == candidate["source_sha256"],
            "V1.68 candidate runtime drift")
    failed_report = SOURCE_AREA / "pack_1/round_1/codex_full_run.json"
    report = load(failed_report)
    require(report.get("status") == "FAILED" and report.get("error_code") == "MODEL_TRANSPORT_FAILED",
            "V1.68 superseded record is not the expected transport failure")
    transports = report.get("transport_attempts", [])
    require(len(transports) > 0 and all(item.get("status") == "NO_HTTP_RESPONSE" for item in transports),
            "V1.68 failure included an HTTP response and cannot be treated as transport-only")
    require(report.get("provider_input_tokens_known") == 0
            and report.get("provider_output_tokens_known") == 0,
            "V1.68 failure has known model usage and cannot be treated as zero-response")
    failed_inventory = tree_inventory(failed_report.parent)
    require(inventory_sha(failed_inventory) == SOURCE_FAILED_TREE_SHA,
            "V1.68 failed slot evidence tree drift")
    return candidate, failed_report, report, failed_inventory


def verify_normalization(directory, candidate_sha):
    normalization_path = directory / "codex_normalization.json"
    manifest_path = directory / "codex_manifest.json"
    normalization = load(normalization_path)
    require(normalization.get("status") == "READY"
            and normalization.get("freshDecodeAndExtraction") is True,
            "Only the already-completed fresh V1.68 normalization may be resumed")
    require(normalization.get("candidate_sha256") == candidate_sha,
            "Normalization used a different candidate")
    require(normalization.get("harness_sha256") == SOURCE_NORMALIZER_HARNESS_SHA,
            "Normalization harness drift")
    require(normalization.get("manifest_sha256") == sha(manifest_path), "Manifest drift")
    frames = normalization.get("frames", [])
    require(frames, "Normalization has no frames")
    frame_inventory = {}
    for frame in frames:
        path = directory / frame["relative_path"]
        require(path.is_file() and sha(path) == frame["sha256"], "Normalized evidence drift")
        require(frame["relative_path"] not in frame_inventory, "Duplicate normalized evidence path")
        frame_inventory[frame["relative_path"]] = frame["sha256"]
    allowed = {"codex_normalization.json", "codex_manifest.json", "evidence"}
    require({item.name for item in directory.iterdir()} >= allowed, "Normalization evidence incomplete")
    return {
        "manifest_sha256": sha(manifest_path),
        "normalization_sha256": sha(normalization_path),
        "frame_count": len(frames),
        "frame_inventory_sha256": inventory_sha(frame_inventory),
        "normalization_seconds": normalization["totalPreparationMs"] / 1000,
    }


def prepare():
    require(not AREA.exists(), "Refusing to overwrite V1.68.1 execution revision")
    candidate, failed_report, failed, failed_inventory = verify_source_area()
    source_records = {}
    for pack_id in ("1", "2", "3"):
        source_records[pack_id] = verify_normalization(
            SOURCE_AREA / ("pack_" + pack_id) / "round_1", SOURCE_CANDIDATE_SHA)
        anchor = SOURCE_NORMALIZATION_ANCHORS[pack_id]
        require(source_records[pack_id]["normalization_sha256"] == anchor["normalization_sha256"],
                "V1.68 source normalization receipt drift")
        require(source_records[pack_id]["manifest_sha256"] == anchor["manifest_sha256"],
                "V1.68 source manifest drift")
        require(source_records[pack_id]["frame_count"] == anchor["frame_count"],
                "V1.68 source frame count drift")

    temporary = Path(tempfile.mkdtemp(prefix=".codex_v1_68_1_prepare_", dir=AREA.parent))
    for name in ("codex_preparation.json", "codex_candidate.json"):
        shutil.copyfile(SOURCE_AREA / name, temporary / name)
    for name in ("codex_baseline_runtime", "codex_candidate_runtime"):
        shutil.copytree(SOURCE_AREA / name, temporary / name)

    require(sha(temporary / "codex_preparation.json") == SOURCE_PREPARATION_SHA,
            "Copied preparation changed")
    require(sha(temporary / "codex_candidate.json") == SOURCE_CANDIDATE_SHA, "Copied candidate changed")
    require(tree_inventory(temporary / "codex_candidate_runtime") == candidate["source_sha256"],
            "Copied candidate runtime changed")

    save(temporary / "codex_execution_revision.json", {
        "execution_revision": EXECUTION_REVISION,
        "created_at": now(),
        "algorithm_candidate": "V1.68",
        "algorithm_or_prompt_changed": False,
        "model_or_endpoint_changed": False,
        "candidate_sha256": SOURCE_CANDIDATE_SHA,
        "preparation_sha256": SOURCE_PREPARATION_SHA,
        "base_harness_sha256": SOURCE_HARNESS_SHA,
        "wrapper_harness_sha256": sha(Path(__file__)),
        "normalizer_harness_sha256": SOURCE_NORMALIZER_HARNESS_SHA,
        "normalizer_loader_sha256": sha(NORMALIZER_LOADER),
        "supersedes_only_execution_of": str(failed_report),
        "superseded_report_sha256": sha(failed_report),
        "superseded_evidence_file_count": len(failed_inventory),
        "superseded_evidence_inventory_sha256": inventory_sha(failed_inventory),
        "superseded_evidence_inventory": failed_inventory,
        "superseded_status": failed["status"],
        "superseded_error_code": failed["error_code"],
        "superseded_http_response_count": 0,
        "superseded_known_input_tokens": 0,
        "superseded_known_output_tokens": 0,
        "transport_change": "DIRECT_TLS_TO_DASHSCOPE_BYPASS_MACOS_SYSTEM_PROXY",
        "transport_destination_allowlist": [ENDPOINT],
        "normalization_contract": "FRESH_REDECODE_THEN_REQUIRE_BYTE_IDENTICAL_MANIFEST_AND_FRAMES",
        "normalization_was_not_redecoded": False,
        "source_normalization_anchors": source_records,
        "scope": "EXECUTION_TRANSPORT_ONLY_NO_ALGORITHM_PROMPT_MODEL_INPUT_WEB_APP_SDK_OR_SHARED_STATE_CHANGE",
        "quality_status": "NO_MODEL_CALL_YET",
    })
    temporary.replace(AREA)
    emit({"event": "V1_68_1_TRANSPORT_REVISION_PREPARED_NO_MODEL_CALL",
          "area": str(AREA), "candidate_sha256": SOURCE_CANDIDATE_SHA,
          "fresh_normalization_required": ["1", "2", "3"]})


def normalize(pack_id):
    revision_path = AREA / "codex_execution_revision.json"
    revision = load(revision_path)
    require(revision["execution_revision"] == EXECUTION_REVISION, "Execution revision drift")
    require(revision["wrapper_harness_sha256"] == sha(Path(__file__)), "Wrapper harness drift")
    require(revision["normalizer_loader_sha256"] == sha(NORMALIZER_LOADER), "Normalizer loader drift")
    require(not (AREA / ("pack_" + pack_id)).exists(), "Refusing to repeat fresh normalization")
    command = ["node", "--no-warnings", "--experimental-loader", str(NORMALIZER_LOADER),
               str(BASE_NORMALIZER), pack_id]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    require(completed.returncode == 0, "Fresh V1.68.1 normalization failed")
    directory = AREA / ("pack_" + pack_id) / "round_1"
    generated = verify_normalization(directory, SOURCE_CANDIDATE_SHA)
    source = revision["source_normalization_anchors"][pack_id]
    require(generated["manifest_sha256"] == source["manifest_sha256"],
            "Fresh normalization manifest differs from V1.68")
    require(generated["frame_count"] == source["frame_count"],
            "Fresh normalization frame count differs from V1.68")
    require(generated["frame_inventory_sha256"] == source["frame_inventory_sha256"],
            "Fresh normalization frame bytes differ from V1.68")
    save(directory / "codex_normalization_revision.json", {
        "execution_revision": EXECUTION_REVISION,
        "completed_at": now(),
        "wrapper_harness_sha256": sha(Path(__file__)),
        "normalizer_loader_sha256": sha(NORMALIZER_LOADER),
        "frozen_normalizer_sha256": SOURCE_NORMALIZER_HARNESS_SHA,
        "execution_revision_receipt_sha256": sha(revision_path),
        "fresh_decode_and_extraction": True,
        "generated": generated,
        "source_v1_68": source,
        "byte_identity_check": "MANIFEST_AND_ALL_FRAME_SHA256_PASS",
    })
    emit({"event": "V1_68_1_FRESH_NORMALIZATION_VERIFIED", "pack": pack_id,
          "frames": generated["frame_count"], "manifest_sha256": generated["manifest_sha256"]})


def direct_request(url, headers, body, timeout):
    require(url == ENDPOINT, "Direct transport destination is not allowlisted")
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read()
    except urllib.error.URLError as exc:
        from diary_one_ci.x01 import X01Error
        raise X01Error("Could not reach Qwen directly: %s" % exc.reason) from exc


def probe():
    require(AREA.exists(), "Prepare V1.68.1 before probing")
    revision_path = AREA / "codex_execution_revision.json"
    revision = load(revision_path)
    require(revision["execution_revision"] == EXECUTION_REVISION, "Execution revision drift")
    require(revision["wrapper_harness_sha256"] == sha(Path(__file__)), "Wrapper harness drift")
    path = AREA / "codex_transport_probe.json"
    require(not path.exists(), "Refusing to repeat the transport probe")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(PROBE_URL, method="HEAD")
    started_at = now()
    try:
        with opener.open(request, timeout=10) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except urllib.error.URLError as exc:
        save(path, {"execution_revision": EXECUTION_REVISION, "started_at": started_at,
                    "completed_at": now(), "status": "FAILED", "error_type": type(exc.reason).__name__,
                    "request": "DIRECT_UNAUTHENTICATED_HEAD_NO_MEDIA_NO_MODEL_CALL",
                    "wrapper_harness_sha256": sha(Path(__file__)),
                    "execution_revision_receipt_sha256": sha(revision_path)})
        raise RuntimeError("Direct DashScope connectivity probe failed") from exc
    require(100 <= status <= 599, "Invalid HTTP status from connectivity probe")
    save(path, {"execution_revision": EXECUTION_REVISION, "started_at": started_at,
                "completed_at": now(), "status": "HTTP_RETURNED", "http_status": status,
                "request": "DIRECT_UNAUTHENTICATED_HEAD_NO_MEDIA_NO_MODEL_CALL",
                "api_key_sent": False, "model_call": False, "system_proxy_used": False,
                "wrapper_harness_sha256": sha(Path(__file__)),
                "execution_revision_receipt_sha256": sha(revision_path)})
    emit({"event": "DIRECT_TRANSPORT_PROBE_HTTP_RETURNED_NO_MODEL_CALL", "http_status": status})


def run(pack_id, live):
    revision_path = AREA / "codex_execution_revision.json"
    probe_path = AREA / "codex_transport_probe.json"
    revision = load(revision_path)
    probe_record = load(probe_path)
    _, _, _, failed_inventory = verify_source_area()
    require(revision["execution_revision"] == EXECUTION_REVISION, "Execution revision drift")
    require(revision["wrapper_harness_sha256"] == sha(Path(__file__)), "Wrapper harness drift")
    require(revision["normalizer_loader_sha256"] == sha(NORMALIZER_LOADER), "Normalizer loader drift")
    require(revision["superseded_evidence_inventory_sha256"] == inventory_sha(failed_inventory),
            "Superseded V1.68 evidence drift")
    require(probe_record.get("status") == "HTTP_RETURNED" and probe_record.get("model_call") is False,
            "Successful no-model connectivity probe required")
    require(probe_record.get("wrapper_harness_sha256") == sha(Path(__file__))
            and probe_record.get("execution_revision_receipt_sha256") == sha(revision_path),
            "Transport probe identity drift")
    for normalized_pack in ("1", "2", "3"):
        directory = AREA / ("pack_" + normalized_pack) / "round_1"
        normalization_revision_path = directory / "codex_normalization_revision.json"
        require(normalization_revision_path.exists(), "All three packs require fresh normalization before API use")
        normalization_revision = load(normalization_revision_path)
        actual = verify_normalization(directory, SOURCE_CANDIDATE_SHA)
        require(normalization_revision.get("execution_revision") == EXECUTION_REVISION
                and normalization_revision.get("execution_revision_receipt_sha256") == sha(revision_path)
                and normalization_revision.get("generated") == actual,
                "Fresh normalization revision identity drift")
    if live:
        for previous_pack in range(1, int(pack_id)):
            previous_report_path = AREA / ("pack_" + str(previous_pack)) / "round_1/codex_full_run.json"
            previous_result_path = AREA / ("codex_execution_result_pack_" + str(previous_pack) + ".json")
            require(previous_report_path.exists() and previous_result_path.exists(),
                    "Previous V1.68.1 pack has not completed")
            require(load(previous_report_path).get("status") == "RETURNED",
                    "Previous V1.68.1 pack did not return a model result; stop the sequence")
            previous_result = load(previous_result_path)
            require(previous_result.get("execution_revision") == EXECUTION_REVISION
                    and previous_result.get("execution_revision_receipt_sha256") == sha(revision_path)
                    and previous_result.get("report_sha256") == sha(previous_report_path),
                    "Previous V1.68.1 execution result identity drift")
    base = load_base_harness()
    base.AREA = AREA
    x02 = base.import_candidate(AREA / "codex_candidate_runtime")
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    QwenChatCompletionsAdapter._url_transport = staticmethod(direct_request)
    original_save = base.save
    normalization_revision_path = AREA / ("pack_" + pack_id) / "round_1/codex_normalization_revision.json"
    execution_identity = {
        "execution_revision": EXECUTION_REVISION,
        "execution_revision_receipt_sha256": sha(revision_path),
        "wrapper_harness_sha256": sha(Path(__file__)),
        "normalizer_loader_sha256": sha(NORMALIZER_LOADER),
        "normalization_revision_sha256": sha(normalization_revision_path),
        "transport_probe_sha256": sha(probe_path),
        "network_execution_mode": "DIRECT_TLS_TO_DASHSCOPE_BYPASS_MACOS_SYSTEM_PROXY",
        "superseded_evidence_inventory_sha256": revision["superseded_evidence_inventory_sha256"],
    }

    def save_with_execution_identity(path, value):
        if Path(path).name in {"codex_attempt.json", "codex_full_run.json"}:
            enriched = dict(value)
            enriched.update(execution_identity)
            value = enriched
        original_save(path, value)

    base.save = save_with_execution_identity
    result = base.run(pack_id, live)
    if live:
        report_path = AREA / ("pack_" + pack_id) / "round_1/codex_full_run.json"
        if report_path.exists():
            result_path = AREA / ("codex_execution_result_pack_" + pack_id + ".json")
            save(result_path, {
                "execution_revision": EXECUTION_REVISION,
                "pack_id": pack_id,
                "completed_at": now(),
                "wrapper_harness_sha256": sha(Path(__file__)),
                "execution_revision_receipt_sha256": sha(revision_path),
                "transport_probe_sha256": sha(probe_path),
                "transport": "DIRECT_TLS_TO_DASHSCOPE_BYPASS_MACOS_SYSTEM_PROXY",
                "report_path": str(report_path),
                "report_sha256": sha(report_path),
                "base_run_exit_code": result,
            })
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "normalize", "probe", "run"))
    parser.add_argument("--pack", choices=("1", "2", "3"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        require(args.pack is None and not args.live, "Prepare is local only")
        prepare()
    elif args.command == "normalize":
        require(args.pack is not None and not args.live, "Normalize requires --pack and is local only")
        normalize(args.pack)
    elif args.command == "probe":
        require(args.pack is None and not args.live, "Probe is an unauthenticated HEAD only")
        probe()
    else:
        require(args.pack is not None, "Run requires --pack")
        sys.exit(run(args.pack, args.live))
